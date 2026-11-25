#!/usr/bin/env python3
"""Append a correction entry to the corrections log and count repeats.

Usage:
  python3 log_correction.py --system=SYSTEM --task=TASK \
      --problem-id=PROBLEM-ID --expected=EXPECTED --actual=ACTUAL \
      --severity=low|medium|high --log=PATH

Appends one markdown table row to the log file at PATH. Counts prior
rows with the SAME problem-id (exact match on the Problem ID column),
and prints PATTERN when the count reaches 2 (twice is a pattern).

--problem-id is a slug, e.g. "video-timing-mismatch". It is the key the
pattern count uses — never free text. Counting by substring overcounts:
"video timing" and "video captions" are two different problems, but a
substring count on "video" calls them one pattern. Counting by
problem-id also fails in the other direction if the same failure is
worded differently each time — when that happens, a human confirms the
match and reuses the same problem-id.

Concurrent appends: two agents logging at once can interleave rows.
The append below holds an exclusive lock (fcntl.flock) on the log file
while writing, so rows cannot interleave. If the platform has no flock,
the append still works, but the lock is skipped.
Deterministic: only appends to the log.
"""
import argparse
import datetime
import re
import sys

PROBLEM_ID = re.compile(r"^[a-z0-9][a-z0-9\-]*$")


def _problem_id_count(existing, problem_id):
    """Count rows whose Problem ID column is exactly this problem-id.
    The log is a markdown table; the Problem ID is the second column.
    Exact match only — substring matching overcounts generic words."""
    count = 0
    for line in existing.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 2 and cells[1] == problem_id:
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--system", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--problem-id", required=True,
                        help="slug for the problem, e.g. video-timing-mismatch")
    parser.add_argument("--expected", required=True)
    parser.add_argument("--actual", required=True)
    parser.add_argument("--severity", choices=["low", "medium", "high"], default="medium")
    parser.add_argument("--log", required=True)
    args = parser.parse_args()

    if not PROBLEM_ID.match(args.problem_id):
        print(f"FAIL: --problem-id must be a slug (lowercase letters, digits, hyphens): {args.problem_id!r}")
        return 2

    try:
        existing = open(args.log, encoding="utf-8").read()
    except FileNotFoundError:
        # First entry: a missing log is an empty log, not an error.
        existing = ""
    except OSError as exc:
        print(f"FAIL: cannot read log: {exc}")
        return 1
    count = _problem_id_count(existing, args.problem_id)
    today = datetime.date.today().isoformat()
    row = (
        f"| {today} | {args.problem_id} | {args.system} | {args.task} | "
        f"{args.expected} vs {args.actual} | {args.severity} | "
        f"{'Yes' if count + 1 >= 2 else 'No'} |  |  |  |\n"
    )
    header = ("| Date | Problem ID | System | Task | Expected vs actual | Severity | "
              "Pattern? | Fix proposed | Owner approved? | Tested? |\n"
              "|---|---|---|---|---|---|---|---|---|---|\n")
    with open(args.log, "a", encoding="utf-8") as handle:
        locked = False
        try:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX)
            locked = True
        except (ImportError, OSError):
            pass  # locking is best-effort; the write still happens
        if not existing:
            handle.write(header)
        handle.write(row)
        if locked:
            fcntl.flock(handle, fcntl.LOCK_UN)
    print(f"Logged: {args.system} / {args.task} (problem-id: {args.problem_id}, prior matching entries: {count})")
    if count + 1 >= 2:
        print("PATTERN: this has happened twice — rewrite the skill, checklist, or job description, and get the owner's approval before it becomes permanent.")
    else:
        print("No pattern yet — watch for a repeat before rewriting the system.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
