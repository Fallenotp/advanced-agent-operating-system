#!/usr/bin/env python3
"""Step 5 Level 5 check (BLOCK): a Level 5 action needs a structured approval.

Usage: python3 check_level5.py <action.json> [--approvals approvals.yaml]

The action file is JSON (machine-written, so the format is exact):
  {"task-id": "weekly-watcher", "action-class": "update-wiki",
   "actor": "agent-1", "date": "2026-11-23", "scope": "update the wiki page"}

An approval covers the action when ALL of these hold:
- The approvals file has an entry with the same task-id and action-class.
- action-class is in the fixed list: report-only, update-wiki,
  update-docs, send-summary, file-issue, update-schedule. Free-text
  action classes are not checkable, so they are not allowed.
- The approval's scope appears in the action's scope (or is "*").
- approved-by is a named human and is NOT the actor. An agent that can
  write to approvals.yaml can approve itself — that is why approvals.yaml
  is protected by CODEOWNERS and a branch ruleset, not by this script.
- The approval date is not in the future, and expires is on or after
  the action date.
- An approval that lives only in chat is not an approval the gate can
  see. If it is not in approvals.yaml, it does not exist for this check.

Exit 0 on PASS, 1 on FAIL, 2 on usage error. Deterministic: reads only
the files given, changes nothing.
"""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gate_yaml import load_file, YamlError  # noqa: E402

ACTION_CLASSES = {
    "report-only", "update-wiki", "update-docs",
    "send-summary", "file-issue", "update-schedule",
}


def _date(value):
    try:
        return datetime.date.fromisoformat(str(value).strip())
    except (ValueError, TypeError):
        return None


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    approvals_path = "approvals.yaml"
    for a in sys.argv[1:]:
        if a.startswith("--approvals="):
            approvals_path = a.split("=", 1)[1]
    if len(args) != 1:
        print("Usage: python3 check_level5.py <action.json> [--approvals approvals.yaml]")
        return 2
    try:
        action = json.load(open(args[0], encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"FAIL: cannot read action file: {exc}")
        return 1
    print("TIER: block")
    task_id = str(action.get("task-id", "")).strip()
    action_class = str(action.get("action-class", "")).strip()
    actor = str(action.get("actor", "")).strip()
    action_date = _date(action.get("date"))
    scope = str(action.get("scope", "")).strip()
    problems = []
    if not task_id:
        problems.append("action has no task-id")
    if action_class not in ACTION_CLASSES:
        problems.append(f"action-class {action_class!r} is not in the fixed list: {sorted(ACTION_CLASSES)}")
    if action_date is None:
        problems.append("action date is missing or not YYYY-MM-DD")
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        return 1
    try:
        data = load_file(approvals_path)
        approvals = data.get("approvals", []) if isinstance(data, dict) else []
    except (OSError, YamlError) as exc:
        print(f"FAIL: cannot read approvals file: {exc}")
        return 1
    today = datetime.date.today()
    matched = None
    for entry in approvals:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("task-id", "")).strip() != task_id:
            continue
        if str(entry.get("action-class", "")).strip() != action_class:
            continue
        matched = entry
        break
    if matched is None:
        print(f"FAIL: no approval record for task {task_id!r} / action-class {action_class!r} — an approval in chat alone does not count")
        return 1
    entry_scope = str(matched.get("scope", "")).strip()
    if entry_scope != "*" and entry_scope and entry_scope.lower() not in scope.lower():
        print(f"FAIL: approval scope {entry_scope!r} does not cover this action's scope {scope!r}")
        return 1
    approver = str(matched.get("approved-by", "")).strip()
    if not approver:
        print("FAIL: approval has no approver name")
        return 1
    if approver == actor:
        print(f"FAIL: approver {approver!r} is the actor — an agent cannot approve its own action")
        return 1
    approved = _date(matched.get("date"))
    expires = _date(matched.get("expires"))
    if approved is None or approved > today:
        print("FAIL: approval date is missing or in the future")
        return 1
    if expires is None or expires < action_date:
        print(f"FAIL: approval expired on {expires} — the action is dated {action_date}")
        return 1
    print(f"PASS: Level 5 action approved — task {task_id!r}, {action_class!r}, approved by {approver} until {expires}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
