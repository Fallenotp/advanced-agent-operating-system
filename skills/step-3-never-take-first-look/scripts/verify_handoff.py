#!/usr/bin/env python3
"""Check a handoff file for Step 3 evidence.

Usage: python3 verify_handoff.py <handoff-file> [--tier block|warn]
Checks the file contains: (1) real evidence under an "Evidence" heading
(or an "Evidence:" line), (2) a "Not checked" section with substantive
content, and (3) a tries count of 3 or fewer.

Evidence must be machine-checkable: a command with an exit code
("exit 0"), a file path that exists, or a number with a unit
("42 passed", "3 files", "95%"). Fluent fluff without one of those
("I checked everything carefully and it all looks good") FAILS — length
is not substance.

What this script does NOT cover: whether a number in the evidence is
real. A typed "214 passed, 0 failed" passes this script exactly like a
real run does. Genuineness is reviewer-checked — a different agent
re-running the check. The script says so in its output; a PASS here
means "these specific assertions held", not "the work is verified".

Tries: accepts "Tries: 1", "Tries used: 1", "Tries = 1", "Used 2 tries",
"attempts: 2", "Tries — 1" (em/en dash). The LAST tries mention in the
file wins, not the first — "Tries: 5 last time, but this time tries: 1"
is 1 try.

Vacuous phrases such as "The evidence is that it worked" or a bare
"Not checked: nothing" do not pass. Prints PASS or FAIL per item.
Exit 0 only if all pass. Deterministic: reads only the file given,
changes nothing.
"""
import os
import re
import sys

# Content too short or too vague to count as evidence.
VACUOUS = [
    r"^the evidence is that it worked\.?$",
    r"^it worked\.?$",
    r"^yes\.?$",
    r"^done\.?$",
    r"^ok\.?$",
    r"^see above\.?$",
    r"^nothing\.?$",
    r"^none\.?$",
    r"^n/a\.?$",
]

# Units that make a number machine-checkable evidence. A bare number with
# no unit ("214") is not evidence; "214 passed" is.
UNITS = (
    "passed", "failed", "tests", "cases", "files", "lines", "sections",
    "pages", "slides", "errors", "warnings", "checks", "rows", "items",
    "examples", "tries", "attempts", "runs", "clicks", "links", "buttons",
    "%", "ms", "seconds", "second", "minutes", "minute", "hours", "mb", "gb",
)
NUMBER_WITH_UNIT = re.compile(
    r"\d+(?:\.\d+)?\s*(?:" + "|".join(UNITS) + r")\b", re.IGNORECASE
)
EXIT_CODE = re.compile(r"\bexit(?:\s+code)?\s*[:=]?\s*0\b", re.IGNORECASE)
# A path-like token: contains a "/" or ends in a known file extension.
PATH_TOKEN = re.compile(r"(?:[\w.\-]+/[\w./\-]+|[\w.\-]+\.(?:py|md|sh|yml|yaml|json|txt|html|csv|pdf|png|jpg))")


# Lines starting with one of these labels belong to a different section,
# not to the section being collected.
KNOWN_LABELS = (
    r"evidence",
    r"not[ -]checked",
    r"tries(?:\s+used)?",
)
LABEL_PREFIX = re.compile(
    r"^(?:" + "|".join(KNOWN_LABELS) + r")\s*[:\-]\s*", re.IGNORECASE
)


def _section_content(lines, name):
    """Return the content lines for a section named e.g. "evidence" or
    "not checked": either a Markdown heading ("## Evidence") with content
    under it, or an inline line ("Evidence: <content>"). Returns None if
    no such heading/line is found. Collection stops at the next heading
    or the next known section label ("Evidence:", "Not checked:",
    "Tries:"), so one section's content can never borrow another
    section's lines to look substantive."""
    pattern = re.compile(r"^(#{1,6}\s+)?" + name + r"\s*[:\-]?\s*(.*)$", re.IGNORECASE)
    for i, line in enumerate(lines):
        m = pattern.match(line.strip())
        if not m:
            continue
        content = [m.group(2).strip()] if m.group(2) and m.group(2).strip() else []
        for following in lines[i + 1:]:
            if re.match(r"^#{1,6}\s", following):
                break
            if LABEL_PREFIX.match(following.strip()):
                break
            if following.strip():
                content.append(following.strip())
        return content
    return None


def _substantive(content):
    """True if the section has at least one line of real content:
    15+ characters and not a vacuous phrase. A leading section label
    ("Not checked:", "Evidence:") is stripped first, so a line like
    "Not checked: nothing" is judged on "nothing" alone, not on the
    label padding it past the length check."""
    if not content:
        return False
    for line in content:
        text = LABEL_PREFIX.sub("", line.strip())
        if len(text) >= 15 and not any(re.match(p, text, re.IGNORECASE) for p in VACUOUS):
            return True
    return False


def _machine_checkable(content, base_dir):
    """True if at least one evidence line is machine-checkable: a command
    with an exit code, a file path that exists, or a number with a unit.
    Fluff ("I checked everything carefully") has none of these and fails.
    A path counts only if the file exists (checked beside the handoff
    file, then in the working directory)."""
    if not content:
        return False
    for line in content:
        text = LABEL_PREFIX.sub("", line.strip())
        if not text or any(re.match(p, text, re.IGNORECASE) for p in VACUOUS):
            continue
        if EXIT_CODE.search(text):
            return True
        if NUMBER_WITH_UNIT.search(text):
            return True
        for token in PATH_TOKEN.findall(text):
            for folder in (base_dir, os.getcwd()):
                if os.path.isfile(os.path.join(folder, token)):
                    return True
    return False


TRIES_PATTERNS = [
    re.compile(r"tries(?:\s+used)?\s*[:=\-–—]\s*(\d+)", re.IGNORECASE),
    re.compile(r"used\s+(\d+)\s+tries\b", re.IGNORECASE),
    re.compile(r"attempts\s*[:=]\s*(\d+)", re.IGNORECASE),
    re.compile(r"(\d+)\s+attempts\b", re.IGNORECASE),
]


def _tries_count(text):
    """The LAST tries mention in the file wins. Returns the count, or None
    if no tries phrasing is found."""
    found = []
    for pattern in TRIES_PATTERNS:
        for m in pattern.finditer(text):
            found.append((m.start(), int(m.group(1))))
    if not found:
        return None
    found.sort()
    return found[-1][1]


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    tier = "block"
    for a in sys.argv[1:]:
        if a.startswith("--tier="):
            tier = a.split("=", 1)[1]
    if tier not in ("block", "warn"):
        print("Usage: python3 verify_handoff.py <handoff-file> [--tier block|warn]")
        return 2
    if len(args) != 1:
        print("Usage: python3 verify_handoff.py <handoff-file> [--tier block|warn]")
        return 2
    try:
        text = open(args[0], encoding="utf-8").read()
    except OSError as exc:
        print(f"FAIL: cannot read file: {exc}")
        return 1
    lines = text.splitlines()
    base_dir = os.path.dirname(os.path.abspath(args[0]))
    ok = True
    print(f"TIER: {tier}")
    evidence = _section_content(lines, r"evidence")
    if _machine_checkable(evidence, base_dir):
        print("PASS: evidence section present with machine-checkable content (command + exit code, existing file path, or number with a unit)")
    else:
        print("FAIL: no machine-checkable evidence — show the actual command output, exit code, file, or counted result, not a summary")
        ok = False
    not_checked = _section_content(lines, r"not[ -]checked")
    if _substantive(not_checked):
        print("PASS: 'not checked' section present with real content")
    else:
        print("FAIL: no 'not checked' section with real content — say what was NOT checked, and why")
        ok = False
    tries = _tries_count(text)
    if tries is not None and tries <= 3:
        print(f"PASS: tries = {tries} (max 3)")
    elif tries is not None:
        print(f"FAIL: tries = {tries} — over the max of 3, stop and report what is left")
        ok = False
    else:
        print("FAIL: no tries count found — state how many tries were used (max 3)")
        ok = False
    print("NOTE: numbers in evidence are not verified as real by this script — genuineness is reviewer-checked (a different agent re-runs the check).")
    print("RESULT: PASS" if ok else "RESULT: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
