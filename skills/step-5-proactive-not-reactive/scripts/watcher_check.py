#!/usr/bin/env python3
"""Deterministic watcher check (Step 5 written rule, no agent judgement).

Usage: python3 watcher_check.py <tasks.json> [--today=YYYY-MM-DD]
tasks.json is a list of tasks, each with "title", "due" (a date), and
"owner" (a name, or "" / null when there is no owner).
Prints: overdue tasks, tasks due in the next 3 days with no owner,
and "No deadlines need you" when there is nothing to flag.
Makes no external calls and changes nothing.

This is a WARN-tier report, never a gate. One bad row must never silence
the watcher: bad rows are collected, the good rows are still reported,
and the bad rows are listed in a separate WARN section. Exit 0 on a
completed run (a WARN is not a failure); exit 1 only on usage errors or
an unreadable tasks file.

Dates are parsed leniently: YYYY-MM-DD, YYYY-M-D ("2026-2-3"), and
day-first DD/MM/YYYY ("23/11/2026") or DD-MM-YYYY. Only a genuinely
unparseable date is a bad row.

Owners: "TBD", "todo", "?", "unassigned", "someone", "none", and empty
all count as NO owner. A placeholder name is not a person.
"""
import datetime
import json
import re
import sys

PLACEHOLDER_OWNERS = {"", "tbd", "todo", "?", "unassigned", "someone", "none", "n/a"}


def _parse_date(value):
    """Parse a date leniently. Returns a date, or None if unparseable."""
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value:
        return None
    # ISO: 2026-11-23 or 2026-2-3.
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", value)
    if m:
        try:
            return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    # ISO with slashes: 2026/11/23.
    m = re.match(r"^(\d{4})/(\d{1,2})/(\d{1,2})$", value)
    if m:
        try:
            return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    # Day-first: 23/11/2026 or 23-11-2026.
    m = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{4})$", value)
    if m:
        try:
            return datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
    return None


def _has_owner(task):
    owner = task.get("owner")
    if owner is None:
        return False
    return str(owner).strip().lower() not in PLACEHOLDER_OWNERS


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 watcher_check.py <tasks.json> [--today=YYYY-MM-DD]")
        return 2
    today = datetime.date.today()
    # --today takes its date in = form (--today=2026-11-23); the space
    # form (--today 2026-11-23) is also accepted for existing callers.
    today_arg = None
    for i, arg in enumerate(sys.argv[2:], 2):
        if arg.startswith("--today="):
            today_arg = arg.split("=", 1)[1]
            break
        if arg == "--today" and i + 1 < len(sys.argv):
            today_arg = sys.argv[i + 1]
            break
    if today_arg is not None:
        parsed = _parse_date(today_arg)
        if parsed is None:
            print(f"FAIL: --today is not a readable date: {today_arg!r}")
            return 2
        today = parsed
    try:
        tasks = json.load(open(sys.argv[1], encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"FAIL: cannot read tasks file: {exc}")
        return 1
    if not isinstance(tasks, list):
        print("FAIL: tasks file must hold a JSON list of tasks")
        return 1
    overdue = []
    due_soon_no_owner = []
    bad_rows = []
    for i, task in enumerate(tasks):
        title = task.get("title") if isinstance(task, dict) else None
        title = title or f"task {i}"
        if not isinstance(task, dict) or "due" not in task:
            bad_rows.append(f"task '{title}' is missing 'due' — every task needs a due date")
            continue
        due = _parse_date(task.get("due"))
        if due is None:
            bad_rows.append(f"task '{title}' has an unreadable 'due' date: {task.get('due')!r}")
            continue
        if due < today:
            overdue.append(task)
        elif (due - today).days <= 3 and not _has_owner(task):
            due_soon_no_owner.append(task)
    print("TIER: warn — this watcher reports, it never blocks a merge")
    if overdue:
        print("OVERDUE:")
        for task in overdue:
            print(f"  - {task.get('title') or 'untitled'} (due {task['due']}, owner: {task.get('owner') or 'none'})")
    if due_soon_no_owner:
        print("DUE IN THE NEXT 3 DAYS WITH NO OWNER:")
        for task in due_soon_no_owner:
            print(f"  - {task['title']} (due {task['due']})")
    if not overdue and not due_soon_no_owner:
        print("No deadlines need you")
    if bad_rows:
        print("WARN: some rows could not be read — the good rows above were still checked:")
        for row in bad_rows:
            print(f"  - {row}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
