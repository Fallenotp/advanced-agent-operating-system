#!/usr/bin/env python3
"""Step 2 allowlist check (BLOCK): high-risk tools in the structured tool list.

Usage: python3 check_tool_allowlist.py <job-description-file>
       [--approvals=approvals.yaml] [--tier=block|warn]

Reads the job description's Section 8 ("Tools & access") — the
structured lines "Can read:", "Can change:", "Can never touch:" — not
prose. A high-risk tool in "Can change:" fails unless an approval record
in approvals.yaml covers it. A high-risk tool in "Can never touch:" is
a ban, never a failure. "Can read:" is not acting, so it is not checked.

High-risk words (exact words, including the synonyms the prose scan
cannot see): send, post, publish, deploy, delete, pay, email, message,
push, merge, remove, charge, share, upload.

An approval covers a tool when: the approvals file has an entry with
the same task (the job file's name without ".md", or the "task-id" the
job names), the tool word appears in the approval's scope, the approval
is not expired, the approver is a named human, and the approval date is
not in the future. An approval that lives only in chat is not an
approval the gate can see.

Exit 0 on PASS, 1 on FAIL, 2 on usage error. Deterministic: reads only
the files given, changes nothing.
"""
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gate_yaml import load_file, YamlError  # noqa: E402

HIGH_RISK = {
    "send", "post", "publish", "deploy", "delete", "pay",
    "email", "message", "push", "merge", "remove", "charge", "share", "upload",
}

HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


def _normalise(text):
    text = text.strip().lower()
    text = re.sub(r"^\d+[\.\)]\s*", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" :")


def _tools_section(lines):
    """Return {kind: [(line_no, text)]} for the three Section 8 lines.
    kind is "read", "change", or "never". Lines after a "Can ...:" line
    belong to it until the next "Can ...:" line or the next heading."""
    section = {}
    in_tools = False
    current = None
    for i, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line:
            continue
        m = HEADING.match(line)
        if m:
            heading = _normalise(m.group(2))
            in_tools = heading.startswith("tools")
            current = None
            continue
        if not in_tools:
            continue
        m = re.match(r"^Can (read|change|never touch)\s*:\s*(.*)$", line, re.IGNORECASE)
        if m:
            current = {"read": "read", "change": "change", "never touch": "never"}[m.group(1).lower()]
            section.setdefault(current, []).append((i, m.group(2).strip()))
            continue
        if current is not None and line.startswith(("-", "*")):
            section[current].append((i, line.lstrip("-* ").strip()))
    return section


def _words(text):
    return set(re.findall(r"[a-z]+", text.lower()))


def _date(value):
    try:
        return datetime.date.fromisoformat(str(value).strip())
    except (ValueError, TypeError):
        return None


def _approval_covers(approvals, task_id, tool, today):
    """True if an approval covers this tool for this task. Returns
    (covered, reason)."""
    for entry in approvals:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("task-id", "")).strip() != task_id:
            continue
        scope_words = _words(str(entry.get("scope", "")))
        if tool not in scope_words and str(entry.get("scope", "")).strip() != "*":
            continue
        approver = str(entry.get("approved-by", "")).strip()
        if not approver:
            return False, "approval has no approver name"
        approved = _date(entry.get("date"))
        expires = _date(entry.get("expires"))
        if approved is None or approved > today:
            return False, "approval date is missing or in the future"
        if expires is None or expires < today:
            return False, "approval is expired or has no expiry"
        return True, f"approved by {approver} until {expires}"
    return False, "no approval record covers it"


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    approvals_path = None
    tier = "block"
    for a in sys.argv[1:]:
        if a.startswith("--approvals="):
            approvals_path = a.split("=", 1)[1]
        elif a.startswith("--tier="):
            tier = a.split("=", 1)[1]
    if tier not in ("block", "warn") or len(args) != 1:
        print("Usage: python3 check_tool_allowlist.py <job-description-file> [--approvals=approvals.yaml] [--tier=block|warn]")
        return 2
    try:
        text = open(args[0], encoding="utf-8").read()
    except OSError as exc:
        print(f"FAIL: cannot read file: {exc}")
        return 1
    task_id = os.path.splitext(os.path.basename(args[0]))[0]
    section = _tools_section(text.splitlines())
    change_lines = section.get("change", [])
    print(f"TIER: {tier}")
    if not change_lines:
        print("PASS: no 'Can change:' line found — nothing is allowed, so nothing high-risk is allowed")
        return 0
    change_text = " ".join(t for _, t in change_lines)
    if not change_text or change_text.strip("[] ") == "":
        print("PASS: 'Can change:' is blank — nothing is allowed")
        return 0
    found = sorted(HIGH_RISK & _words(change_text))
    if not found:
        print("PASS: 'Can change:' lists no high-risk tools")
        return 0
    approvals = []
    if approvals_path:
        try:
            data = load_file(approvals_path)
            approvals = data.get("approvals", []) if isinstance(data, dict) else []
        except (OSError, YamlError) as exc:
            print(f"FAIL: cannot read approvals file: {exc}")
            return 1
    today = datetime.date.today()
    failures = []
    for tool in found:
        line_no = next((n for n, t in change_lines if tool in _words(t)), change_lines[0][0])
        covered, reason = _approval_covers(approvals, task_id, tool, today)
        if covered:
            print(f"PASS: '{tool}' (line {line_no}) — {reason}")
        else:
            failures.append((tool, line_no, reason))
    if failures:
        print("FAIL: high-risk tools in 'Can change:' with no approval record:")
        for tool, line_no, reason in failures:
            print(f"  - {tool} (line {line_no}): {reason}")
        print("Fix: move the tool to 'Can never touch:', or get the owner's approval recorded in approvals.yaml. An approval in chat alone does not count.")
        return 1
    print("PASS: every high-risk tool in 'Can change:' has an approval record")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
