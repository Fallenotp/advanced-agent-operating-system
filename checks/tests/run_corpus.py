#!/usr/bin/env python3
"""Run the negative test corpus for the gate's checkers.

Usage: python3 checks/tests/run_corpus.py [--root DIR]
Reads checks/tests/corpus.json. For each case it writes the case's
input files into checks/tests/.tmp/<id>/ (fresh each run), runs the
command, and compares the outcome to the case's expectation:

  pass           exit 0
  fail           exit non-zero
  warn           exit 0 and "WARN" in the output
  contains       exit 0 and case["text"] in the output
  contains_all   exit 0 and every string in case["texts"] in the output
  fail-contains  exit non-zero and case["text"] in the output

The corpus holds BOTH directions for every checker: legitimate inputs
it must pass (a filled brief with "[ ]" in an example, "Used 2 tries",
a good handoff) and cheating inputs it must fail (a nonsense brief,
"Never forget: send the report", fluff evidence, a test script that is
just "true"). If a checker cannot pass its own negative corpus, it
ships as WARN, not BLOCK.

Placeholders in a case's run/shell: {root} is the repo root, {dir} is
the case's temp dir. setup_mtimes lists files whose mtime is set with
touch -d (git does not preserve mtimes, so the corpus sets them).

Exit 0 only if every case passes. Deterministic: writes only under
checks/tests/.tmp/, changes nothing else.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.dirname(os.path.dirname(HERE))


def _write_files(base, files):
    for relpath, content in files.items():
        path = os.path.join(base, relpath)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)


def _run_case(case, root, tmp):
    case_dir = os.path.join(tmp, case["id"])
    os.makedirs(case_dir, exist_ok=True)
    _write_files(case_dir, case.get("files", {}))
    for relpath, date in case.get("mtimes", {}).items():
        path = os.path.join(case_dir, relpath)
        subprocess.run(["touch", "-d", date, path], check=True)
    fmt = {"root": root, "dir": case_dir}
    if "shell" in case:
        cmd = ["bash", "-c", case["shell"].format(**fmt)]
    else:
        cmd = [part.format(**fmt) for part in case["run"]]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=root)
    out = proc.stdout + proc.stderr
    expect = case["expect"]
    ok = False
    detail = ""
    if expect == "pass":
        ok = proc.returncode == 0
        detail = f"exit {proc.returncode}"
    elif expect == "fail":
        ok = proc.returncode != 0
        detail = f"exit {proc.returncode}"
    elif expect == "warn":
        ok = proc.returncode == 0 and "WARN" in out
        detail = f"exit {proc.returncode}, WARN in output: {'WARN' in out}"
    elif expect == "contains":
        ok = proc.returncode == 0 and case["text"] in out
        detail = f"exit {proc.returncode}, {case['text']!r} in output: {case['text'] in out}"
    elif expect == "contains_all":
        missing = [t for t in case["texts"] if t not in out]
        ok = proc.returncode == 0 and not missing
        detail = f"exit {proc.returncode}, missing: {missing}"
    elif expect == "fail-contains":
        ok = proc.returncode != 0 and case["text"] in out
        detail = f"exit {proc.returncode}, {case['text']!r} in output: {case['text'] in out}"
    else:
        detail = f"unknown expectation: {expect!r}"
    return ok, detail, out


def main() -> int:
    root = DEFAULT_ROOT
    for arg in sys.argv[1:]:
        if arg.startswith("--root="):
            root = arg.split("=", 1)[1]
    corpus_path = os.path.join(HERE, "corpus.json")
    with open(corpus_path, encoding="utf-8") as handle:
        corpus = json.load(handle)
    tmp = os.path.join(HERE, ".tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp, exist_ok=True)
    passed = failed = 0
    for case in corpus["cases"]:
        ok, detail, out = _run_case(case, root, tmp)
        if ok:
            passed += 1
            print(f"PASS {case['id']}: {case['desc']}")
        else:
            failed += 1
            print(f"FAIL {case['id']}: {case['desc']} — expected {case['expect']}, got {detail}")
            for line in out.splitlines()[:8]:
                print(f"    {line}")
    print(f"CORPUS: {passed} passed, {failed} failed, {passed + failed} total")
    if failed == 0:
        # A passing run leaves nothing behind. A failing run keeps the
        # case inputs under checks/tests/.tmp/ so the failure can be
        # inspected and re-run by hand.
        shutil.rmtree(tmp, ignore_errors=True)
    else:
        print(f"Case inputs kept in {tmp} for inspection.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
