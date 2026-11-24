#!/bin/bash
# Step 3 code checker: run the project's build, lint, typecheck, and
# test commands if they exist, and print which ones were not run and why.
#
# Usage: bash run_checks.sh [target-dir]
#   target-dir defaults to the current directory. The directory it ran in
#   is printed, so a run from the wrong directory is obvious.
#
# Which checks apply is decided by checks/manifest.yaml (code checks apply
# only if package.json or pyproject.toml exists in the target directory).
# A docs-only repo — no package.json, no pyproject.toml — is NOT a
# failure: it prints "no code checks apply" and passes with a note.
# "Nothing applicable" and "nothing verified" are different states.
# A project that HAS code checks but ran none of them FAILS.
#
# Minimum signal: a passing test command must print a test count
# (e.g. "3 passed", "12 tests"). A test script that always passes
# ("test": "true") prints no count — that is a WARN, not a PASS.
# A stub suite is indistinguishable from a real one otherwise.
#
# WARNING: this runner EXECUTES project code (npm run, pytest). It must
# only run in CI or a sandbox, never as a local gate on untrusted pull
# requests. Prefer running the linter/test binary directly where possible.
set -u

TARGET="${1:-.}"
if [ ! -d "$TARGET" ]; then
  echo "FAIL: target directory does not exist: $TARGET"
  exit 2
fi
cd "$TARGET" || exit 2
echo "Running in: $(pwd)"

# Applicability: from checks/manifest.yaml when the gate passes it, else
# the built-in rule (package.json or pyproject.toml present).
MANIFEST="${GATE_MANIFEST:-}"
APPLIES=0
if [ -n "$MANIFEST" ] && [ -f "$MANIFEST" ]; then
  # Manifest lists the files under applies_when_any_file. One per line.
  while IFS= read -r marker; do
    marker="$(echo "$marker" | tr -d ' -')"
    if [ -n "$marker" ] && [ -f "$marker" ]; then APPLIES=1; fi
  done < <(sed -n '/applies_when_any_file:/,/^[^ -]/p' "$MANIFEST" | grep -E '^\s*-\s+' | sed 's/^\s*-\s*//')
else
  if [ -f package.json ] || [ -f pyproject.toml ]; then APPLIES=1; fi
fi

if [ "$APPLIES" -eq 0 ]; then
  echo "NOTE: no code checks apply — no package.json or pyproject.toml in $(pwd)"
  echo "RESULT: PASS (no code checks apply)"
  exit 0
fi

fail=0
warn=0
ran=0
run() {
  local name="$1"; shift
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "NOT RUN: $name — command not found: $*"
    return 0
  fi
  ran=$((ran + 1))
  echo "--- $name: $*"
  if "$@"; then
    echo "PASS: $name"
  else
    echo "FAIL: $name"
    fail=1
  fi
}

run_test() {
  # Like run(), but the output must show a test count (e.g. "3 passed").
  # A passing command with no count is a stub until proven otherwise: WARN.
  local name="$1"; shift
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "NOT RUN: $name — command not found: $*"
    return 0
  fi
  ran=$((ran + 1))
  echo "--- $name: $*"
  local out
  if out="$("$@" 2>&1)"; then
    echo "$out"
    if echo "$out" | grep -qiE '[0-9]+ (passed|failed|tests?|cases?|test\(s\)|passed,)'; then
      echo "PASS: $name"
    else
      echo "WARN: $name — passed but printed no test count (stub suite?). A count like '3 passed' is required for a real PASS."
      warn=1
    fi
  else
    echo "$out"
    echo "FAIL: $name"
    fail=1
  fi
}

if [ -f package.json ]; then
  if grep -q '"build"' package.json; then run "build" npm run build; else echo "NOT RUN: build — no build script in package.json"; fi
  if grep -q '"lint"' package.json; then run "lint" npm run lint; else echo "NOT RUN: lint — no lint script in package.json"; fi
  if grep -q '"typecheck"' package.json; then run "typecheck" npm run typecheck; else echo "NOT RUN: typecheck — no typecheck script in package.json"; fi
  if grep -q '"test"' package.json; then run_test "test" npm test; else echo "NOT RUN: test — no test script in package.json"; fi
elif [ -f pyproject.toml ]; then
  if command -v pytest >/dev/null 2>&1; then run_test "test" python3 -m pytest -q; else echo "NOT RUN: test — pytest not installed"; fi
fi

if [ "$fail" -ne 0 ]; then
  echo "RESULT: at least one check failed — fix the biggest failure first, then re-run"
  exit 1
elif [ "$ran" -eq 0 ]; then
  echo "RESULT: no checks ran although code checks apply — nothing was verified"
  exit 1
else
  if [ "$warn" -ne 0 ]; then
    echo "RESULT: all checks that ran passed, with warnings (see WARN lines above)"
  else
    echo "RESULT: all checks that ran passed"
  fi
  exit 0
fi
