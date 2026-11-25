#!/usr/bin/env python3
"""Step 4 corrections check: a pattern row must prove its fix happened.

Usage: python3 check_corrections.py <log-file> [--root=DIR] [--tier=block|warn]

The log is the markdown table in docs/user/step-4-every-correction-becomes-the-system.md:
  Date | Problem ID | System | Task | Expected vs actual | Severity |
  Pattern? | Fix proposed | Owner approved? | Tested?

Rules:
- Every row needs a problem-id slug (e.g. "video-timing-mismatch").
  Rows are grouped by exact problem-id match, never by substring.
- A row whose Pattern? cell starts with "Yes" (case-insensitive,
  leading whitespace stripped) is a pattern row and must carry: a Fix
  proposed that names a file (a path that exists under --root) AND that
  file must have changed on or after the row's date (checked with git
  log when the root is a git repo, else file mtime — mtime is weaker
  and the script says so); and an Owner approved? cell reading
  "Yes — <name>, <date>" with a date that is not in the future.
  A cell starting with "No" is not a pattern row and is skipped.
  Any other non-empty Pattern? value is not silently skipped: it
  produces a WARNING naming the unrecognized value.
- A row that says "fix applied" with no actual change fails the
  file-exists/file-changed check. A real fix recorded only in prose
  ("updated the skill") fails the file-name check — write the file down.
- Malformed rows (wrong columns, bad date, bad problem-id) FAIL in both
  tiers: a broken record is not a judgement call.
- Unverified pattern rows are WARN when --tier=warn (the default: the
  log format is new and the matching will be wrong at first — run it as
  WARN, measure, then promote) and FAIL when --tier=block.

Exit 0 when nothing fails at the chosen tier, 1 on failure, 2 on usage
error. Deterministic: reads only the files given, changes nothing.
"""
import datetime
import os
import re
import subprocess
import sys

PROBLEM_ID = re.compile(r"^[a-z0-9][a-z0-9\-]*$")
APPROVAL = re.compile(r"^Yes\s*[—\-]\s*(.+?),\s*(\d{4}-\d{2}-\d{2})\s*$")
PATH_TOKEN = re.compile(r"(?:[\w.\-]+/[\w./\-]+|[\w.\-]+\.(?:py|md|sh|yml|yaml|json|txt|html|csv))")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _date(value):
    try:
        return datetime.date.fromisoformat(str(value).strip())
    except (ValueError, TypeError):
        return None


def _rows(text):
    """Parse the markdown table into row dicts. Returns (rows, errors)."""
    rows = []
    errors = []
    header = None
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells if c):
            continue  # separator row
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if [c.lower() for c in cells] == header:
            continue  # a repeated header row (second table in the file) is not a data row
        if len(cells) != len(header):
            errors.append(f"line {line_no}: {len(cells)} columns, expected {len(header)}")
            continue
        rows.append(dict(zip(header, cells)))
    if header is None:
        errors.append("no table header found")
    return rows, errors


def _file_changed_after(root, path, after_date):
    """True if the file changed on or after after_date. Prefers git log; falls
    back to file mtime and says so (mtime is weaker — a fresh checkout
    makes every file look new). Returns (changed, method)."""
    full = os.path.join(root, path)
    if not os.path.isfile(full):
        return False, "missing"
    try:
        out = subprocess.run(
            ["git", "-C", root, "log", "-1", "--format=%ci", "--", path],
            capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0 and out.stdout.strip():
            changed = datetime.datetime.fromisoformat(out.stdout.strip()).date()
            return changed >= after_date, "git"
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    mtime = datetime.date.fromtimestamp(os.path.getmtime(full))
    return mtime >= after_date, "mtime"


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = "."
    tier = "warn"
    for a in sys.argv[1:]:
        if a.startswith("--root="):
            root = a.split("=", 1)[1]
        elif a.startswith("--tier="):
            tier = a.split("=", 1)[1]
    if tier not in ("block", "warn") or len(args) != 1:
        print("Usage: python3 check_corrections.py <log-file> [--root=DIR] [--tier=block|warn]")
        return 2
    try:
        text = open(args[0], encoding="utf-8").read()
    except OSError as exc:
        print(f"FAIL: cannot read file: {exc}")
        return 1
    print(f"TIER: {tier}")
    rows, errors = _rows(text)
    failures = []
    warnings = []
    for error in errors:
        failures.append(error)
    today = datetime.date.today()
    for row in rows:
        problem_id = row.get("problem id", "")
        row_date = _date(row.get("date", ""))
        label = f"problem-id {problem_id!r} ({row.get('date', '?')})"
        if not PROBLEM_ID.match(problem_id):
            failures.append(f"{label}: problem-id is not a slug — use lowercase letters, digits, hyphens")
            continue
        if row_date is None:
            failures.append(f"{label}: date is not YYYY-MM-DD")
            continue
        # Pattern? classification: "Yes" starts a pattern row, "No" is a
        # one-off. Anything else non-empty is not silently skipped — it
        # warns, naming the value, so a prose cell can never again make
        # a pattern row look verified when it was never checked.
        pattern_cell = row.get("pattern?", "").strip()
        pattern_lower = pattern_cell.lower()
        if pattern_lower.startswith("yes"):
            pass  # pattern row: verify it below
        elif pattern_lower.startswith("no") or pattern_cell == "":
            continue
        else:
            warnings.append(
                f"{label}: Pattern? value {pattern_cell!r} is not recognized "
                "— expected a value starting with 'Yes' or 'No'; row was not verified"
            )
            continue
        fix = row.get("fix proposed", "")
        paths = PATH_TOKEN.findall(fix)
        if not fix.strip():
            problems = [f"{label}: marked as a pattern but no fix is proposed"]
        elif not paths:
            problems = [f"{label}: fix names no file — write the file that changed, not prose"]
        else:
            problems = []
            for path in paths:
                changed, method = _file_changed_after(root, path, row_date)
                if method == "missing":
                    problems.append(f"{label}: fix names {path!r}, which does not exist under {root}")
                elif not changed:
                    problems.append(f"{label}: {path!r} did not change on or after {row_date} (checked by {method})")
                elif method == "mtime":
                    warnings.append(f"{label}: {path!r} verified by mtime only — git was unavailable, so a fresh checkout could fake this")
        approval = row.get("owner approved?", "")
        m = APPROVAL.match(approval)
        if not m:
            problems.append(f"{label}: Owner approved? must read 'Yes — <name>, <date>' for a pattern row, got {approval!r}")
        else:
            approved_date = _date(m.group(2))
            if approved_date is None or approved_date > today:
                problems.append(f"{label}: approval date is missing or in the future")
        if tier == "block":
            failures.extend(problems)
        else:
            warnings.extend(problems)
    if not rows and not errors:
        print("NOTE: log has no rows — nothing to check")
    for warning in warnings:
        print(f"WARN: {warning}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    if warnings:
        print(f"PASS (with {len(warnings)} warning(s)): all pattern rows are recorded; see WARN lines")
    else:
        print("PASS: corrections log is well-formed and every pattern row proves its fix")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
