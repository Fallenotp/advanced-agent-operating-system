#!/usr/bin/env python3
"""Helper for the gate: list the overrides in checks/overrides.yaml.

Usage: python3 _override_check.py --overrides=FILE list
Prints one tab-separated line per override entry:
  check<TAB>file<TAB>reason<TAB>reviewed-by<TAB>date<TAB>expires
A missing overrides file means "no overrides" (exit 0, no output).
A file the YAML-subset reader cannot parse is an error (exit 1) — a
config the gate cannot read exactly is a config it must not trust.
Internal helper for checks/gate.sh; not a checker on its own.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gate_yaml import load_file, YamlError  # noqa: E402


def main() -> int:
    # --overrides takes its file in = form (--overrides=FILE); the space
    # form (--overrides FILE) is also accepted — checks/gate.sh uses it.
    path = None
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg.startswith("--overrides="):
            path = arg.split("=", 1)[1]
            break
        if arg == "--overrides" and i + 1 < len(sys.argv):
            path = sys.argv[i + 1]
            break
    if path is None or path == "" or "list" not in sys.argv[1:]:
        print("Usage: python3 _override_check.py --overrides=FILE list", file=sys.stderr)
        return 2
    if not os.path.isfile(path):
        return 0
    try:
        data = load_file(path)
    except YamlError as exc:
        print(f"FAIL: cannot parse overrides file: {exc}", file=sys.stderr)
        return 1
    entries = data.get("overrides", []) if isinstance(data, dict) else []
    for entry in entries:
        if not isinstance(entry, dict):
            print(f"FAIL: override entry is not a mapping: {entry!r}", file=sys.stderr)
            return 1
        fields = [
            str(entry.get("check", "")),
            str(entry.get("file", "")),
            str(entry.get("reason", "")),
            str(entry.get("reviewed-by", "")),
            str(entry.get("date", "")),
            str(entry.get("expires", "")),
        ]
        print("\t".join(fields))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
