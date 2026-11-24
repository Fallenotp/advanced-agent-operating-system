#!/bin/bash
# checks/gate.sh — the runner for the five-step agent gate.
#
# One runner, three gates: the agent runs it as a self-check before
# handoff, pre-commit runs it for fast feedback, and CI runs it as a
# required status check. Pre-commit is feedback only (it is bypassable
# with --no-verify); the CI required check is the real gate. A workflow
# without the branch ruleset is advisory — see docs/setup-checklist.md.
#
# Usage:
#   bash checks/gate.sh --self-test
#       Prove the checkers work: run the negative test corpus, then the
#       gate's own scenarios (valid/expired/unknown overrides, the
#       >2-overrides tripwire, --warn-only, zero checks).
#   bash checks/gate.sh [--target DIR] [--job FILE] [--handoff FILE]
#       [--review FILE --author-session ID --reviewer-session ID]
#       [--tasks FILE] [--log FILE] [--action FILE]
#       [--warn-only] [--record-history]
#       Run the checks that have inputs. With no inputs at all, the gate
#       fails with "no checks ran" — a gate that checked nothing must
#       never report success.
#
# Exit codes: 0 = every BLOCK-tier check passed (WARNs allowed);
# 1 = a BLOCK-tier check failed, or no checks ran, or an override was
# bad; 2 = usage error.
#
# Paths resolve from the repo root (the parent of checks/), never from
# the working directory. --root DIR overrides the root (used by the
# self-test to run scenarios in a temp copy). --overrides FILE and
# --history FILE override the default paths (also for the self-test).
#
# Overrides: checks/overrides.yaml is read automatically. A failing
# check with a valid override prints OVERRIDDEN and passes. An expired
# override, or one naming a check or file not in this run, FAILS the
# run. More than 2 overrides in one run FAILS with "the check is
# wrong, fix the check". Overrides are listed in the output so the
# owner sees them.
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OVERRIDES_FILE="$ROOT/checks/overrides.yaml"
HISTORY_FILE="$ROOT/checks/overrides-history.log"
WARN_ONLY=0
RECORD_HISTORY=0
SELF_TEST=0
TARGET=""
JOB=""
HANDOFF=""
HANDOFF_TIER="block"
REVIEW=""
AUTHOR_SESSION=""
REVIEWER_SESSION=""
TASKS=""
LOGFILE=""
ACTION=""

usage() {
  echo "Usage: bash checks/gate.sh --self-test | [--target DIR] [--job FILE] [--handoff FILE] [--review FILE --author-session ID --reviewer-session ID] [--tasks FILE] [--log FILE] [--action FILE] [--warn-only] [--record-history]"
  echo "Run with no inputs and the gate fails: a gate that checked nothing must never report success."
}

while [ $# -gt 0 ]; do
  case "$1" in
    --self-test) SELF_TEST=1; shift ;;
    --warn-only) WARN_ONLY=1; shift ;;
    --record-history) RECORD_HISTORY=1; shift ;;
    --root) ROOT="$2"; OVERRIDES_FILE="$ROOT/checks/overrides.yaml"; HISTORY_FILE="$ROOT/checks/overrides-history.log"; shift 2 ;;
    --overrides) OVERRIDES_FILE="$2"; shift 2 ;;
    --history) HISTORY_FILE="$2"; shift 2 ;;
    --target) TARGET="$2"; shift 2 ;;
    --job) JOB="$2"; shift 2 ;;
    --handoff) HANDOFF="$2"; shift 2 ;;
    --handoff-tier) HANDOFF_TIER="$2"; shift 2 ;;
    --review) REVIEW="$2"; shift 2 ;;
    --author-session) AUTHOR_SESSION="$2"; shift 2 ;;
    --reviewer-session) REVIEWER_SESSION="$2"; shift 2 ;;
    --tasks) TASKS="$2"; shift 2 ;;
    --log) LOGFILE="$2"; shift 2 ;;
    --action) ACTION="$2"; shift 2 ;;
    --help) usage; exit 0 ;;
    *) echo "FAIL: unknown argument: $1"; usage; exit 2 ;;
  esac
done

TODAY="$(date +%F)"
CHECKS_RUN=0
BLOCK_FAILS=0
WARNS=0
OVERRIDES_USED=0
KNOWN_CHECKS=""
KNOWN_FILES=""

# --- overrides -------------------------------------------------------------
# Load the override entries once. Each line: check, file, reason,
# reviewed-by, date, expires (tab-separated).
OVERRIDE_LINES=""
if [ -f "$OVERRIDES_FILE" ]; then
  if ! OVERRIDE_LINES="$(python3 "$SCRIPT_DIR/_override_check.py" --overrides "$OVERRIDES_FILE" list)"; then
    echo "FAIL: overrides file cannot be parsed: $OVERRIDES_FILE"
    exit 1
  fi
fi

override_for() {
  # override_for <check> <file> — prints "reason|reviewed-by|expires" for
  # a valid (not expired) override, or nothing. Expired overrides are
  # caught separately by validate_overrides.
  local check="$1" file="$2"
  echo "$OVERRIDE_LINES" | awk -F'\t' -v c="$check" -v f="$file" -v today="$TODAY" '
    $1 == c && $2 == f && $6 != "" && $6 >= today { print $3 "|" $4 "|" $6; exit }
  '
}

validate_overrides() {
  # An expired override, or one naming a check or file not in this run,
  # is itself a FAIL.
  local bad=0
  while IFS="$(printf '\t')" read -r check file reason reviewed_by date expires; do
    [ -z "$check" ] && continue
    if [ -n "$expires" ] && [ "$expires" \< "$TODAY" ]; then
      echo "FAIL: override for '$check' on '$file' expired on $expires — the check is wrong, fix the check"
      bad=1
    fi
    case " $KNOWN_CHECKS " in *" $check "*) ;; *) echo "FAIL: override names unknown check '$check'"; bad=1 ;; esac
    case " $KNOWN_FILES " in *" $file "*) ;; *) echo "FAIL: override names file not in this run: '$file'"; bad=1 ;; esac
  done <<EOF
$OVERRIDE_LINES
EOF
  return "$bad"
}

# --- check runner ----------------------------------------------------------
# run_check <name> <tier> <file> <command...>
# tier: block or warn. A block failure fails the run (unless --warn-only
# or a valid override applies). A warn failure prints WARN and the run
# still passes.
run_check() {
  local name="$1" tier="$2" file="$3"; shift 3
  CHECKS_RUN=$((CHECKS_RUN + 1))
  KNOWN_CHECKS="$KNOWN_CHECKS $name"
  KNOWN_FILES="$KNOWN_FILES $file"
  echo "CHECK: $name (tier: $tier) — $file"
  local out rc
  if ! command -v "$1" >/dev/null 2>&1 && [ "$1" != "bash" ] && [ "$1" != "python3" ]; then
    echo "INFRA: checker not found: $1 — the gate itself is broken"
    BLOCK_FAILS=$((BLOCK_FAILS + 1))
    return
  fi
  out="$("$@" 2>&1)"
  rc=$?
  echo "$out" | sed 's/^/  /'
  if [ "$rc" -eq 0 ]; then
    echo "PASS: $name"
    return
  fi
  # It failed. A valid override turns it into a pass, loudly.
  local override
  override="$(override_for "$name" "$file")"
  if [ -n "$override" ]; then
    local reason="${override%%|*}"; local rest="${override#*|}"
    local by="${rest%%|*}"; local expires="${rest##*|}"
    echo "OVERRIDDEN: $name on $file — $reason (by $by, expires $expires)"
    OVERRIDES_USED=$((OVERRIDES_USED + 1))
    return
  fi
  if [ "$tier" = "warn" ] || [ "$WARN_ONLY" -eq 1 ]; then
    echo "WARN: $name failed, but its tier is warn (or --warn-only) — the run still passes"
    WARNS=$((WARNS + 1))
    return
  fi
  echo "FAIL: $name"
  BLOCK_FAILS=$((BLOCK_FAILS + 1))
}

tier_of() {
  # tier_of <key> — read the tier from checks/manifest.yaml, default block.
  local key="$1" tier
  tier="$(sed -n "/^tiers:/,/^[^ ]/p" "$ROOT/checks/manifest.yaml" 2>/dev/null | grep -E "^  $key:" | sed 's/.*: *//' | tr -d ' ')"
  echo "${tier:-block}"
}

finish() {
  # The aggregation. Called once, at the end of every run.
  if [ "$CHECKS_RUN" -eq 0 ]; then
    echo "RESULT: no checks ran — nothing was verified"
    echo "A gate that checked nothing must never report success. Pass --self-test, --target, --job, --handoff, --review, --tasks, --log, or --action."
    return 1
  fi
  if ! validate_overrides; then
    BLOCK_FAILS=$((BLOCK_FAILS + 1))
  fi
  if [ "$OVERRIDES_USED" -gt 2 ]; then
    echo "FAIL: $OVERRIDES_USED overrides used in one run — the check is wrong, fix the check (Step 4)"
    BLOCK_FAILS=$((BLOCK_FAILS + 1))
  fi
  if [ "$RECORD_HISTORY" -eq 1 ]; then
    echo "$TODAY run-$$ $OVERRIDES_USED $CHECKS_RUN" >> "$HISTORY_FILE"
  fi
  if [ -f "$HISTORY_FILE" ]; then
    local week_ago total with_override
    week_ago="$(date -d "7 days ago" +%F 2>/dev/null || echo "0000-00-00")"
    total="$(awk -v w="$week_ago" '$1 >= w' "$HISTORY_FILE" | wc -l)"
    with_override="$(awk -v w="$week_ago" '$1 >= w && $3 > 0' "$HISTORY_FILE" | wc -l)"
    if [ "$total" -ge 5 ] && [ "$with_override" -gt 0 ] && [ $((with_override * 100 / total)) -gt 20 ]; then
      echo "FAIL: overrides were used in $with_override of the last $total runs (over 20%) — the checks are wrong, fix the checks (Step 4)"
      BLOCK_FAILS=$((BLOCK_FAILS + 1))
    fi
  fi
  echo "RESULT: $CHECKS_RUN check(s) ran, $BLOCK_FAILS block failure(s), $WARNS warning(s), $OVERRIDES_USED override(s)"
  if [ "$BLOCK_FAILS" -ne 0 ]; then
    echo "RESULT: FAIL"
    return 1
  fi
  echo "RESULT: PASS"
  return 0
}

# --- self-test -------------------------------------------------------------
self_test() {
  local tmp fail=0
  tmp="$(mktemp -d)"
  echo "Self-test: proving the checkers work (negative corpus + gate scenarios)"
  if ! python3 "$SCRIPT_DIR/tests/run_corpus.py" --root "$ROOT"; then
    echo "SELF-TEST FAIL: corpus"
    fail=1
  fi
  # Scenario 1: a failing job with a valid override passes, loudly.
  cat > "$tmp/job-bad.md" <<'EOF'
# Agent Job Description — Bad

## 1. Role
Review responder.

## 2. Mission
Draft replies.

## 3. Owner
The owner.

## 4. Responsibilities
Draft replies.

## 5. Steps
Read, draft, hand over.

## 6. Deliverable
A draft reply.

## 7. Sources of truth
The review itself.

## 8. Tools
Can read: reviews.
Can change: send emails to clients.
Can never touch: the live site.

## 9. Green / amber / red
Green: drafting. Amber: public. Red: publishing.

## 10. Schedule
Runs weekly.

## 11. Correction log
Log location: docs/step-4-corrections-log-example.md
EOF
  cat > "$tmp/overrides-good.yaml" <<EOF
overrides:
  - check: step2_allowlist
    file: $tmp/job-bad.md
    reason: Owner reviewed the send allowance in person and confirmed it is amber, owner approves each send.
    reviewed-by: Ian
    date: $TODAY
    expires: 2099-01-01
EOF
  if bash "$SCRIPT_DIR/gate.sh" --root "$ROOT" --overrides "$tmp/overrides-good.yaml" --job "$tmp/job-bad.md" | grep -q "OVERRIDDEN: step2_allowlist"; then
    echo "SELF-TEST PASS: valid override prints OVERRIDDEN and passes"
  else
    echo "SELF-TEST FAIL: valid override did not print OVERRIDDEN"; fail=1
  fi
  # Scenario 2: an expired override fails the run.
  cat > "$tmp/overrides-expired.yaml" <<EOF
overrides:
  - check: step2_allowlist
    file: $tmp/job-bad.md
    reason: Old override, no longer valid.
    reviewed-by: Ian
    date: 2026-01-01
    expires: 2026-01-08
EOF
  if bash "$SCRIPT_DIR/gate.sh" --root "$ROOT" --overrides "$tmp/overrides-expired.yaml" --job "$tmp/job-bad.md" >/dev/null 2>&1; then
    echo "SELF-TEST FAIL: expired override passed"; fail=1
  else
    echo "SELF-TEST PASS: expired override fails the run"
  fi
  # Scenario 3: an override naming an unknown check fails the run.
  cat > "$tmp/overrides-unknown.yaml" <<EOF
overrides:
  - check: step99_nonexistent
    file: $tmp/job-bad.md
    reason: Made-up check.
    reviewed-by: Ian
    date: $TODAY
    expires: 2099-01-01
EOF
  if bash "$SCRIPT_DIR/gate.sh" --root "$ROOT" --overrides "$tmp/overrides-unknown.yaml" --job "$tmp/job-bad.md" >/dev/null 2>&1; then
    echo "SELF-TEST FAIL: unknown-check override passed"; fail=1
  else
    echo "SELF-TEST PASS: unknown-check override fails the run"
  fi
  # Scenario 4: more than 2 overrides in one run fails (tripwire).
  # Needs THREE genuinely failing checks, one override each.
  cat > "$tmp/job-bad2.md" <<'EOF'
# Agent Job Description — Bad

## 1. Role
[ ]

## 2. Mission
[ ]

## 3. Owner
[ ]

## 4. Responsibilities
[ ]

## 5. Steps
[ ]

## 6. Deliverable
[ ]

## 7. Sources of truth
[ ]

## 8. Tools
Can read: reviews.
Can change: send emails to clients.
Can never touch: the live site.

## 9. Green / amber / red
[ ]

## 10. Schedule
[ ]

## 11. Correction log
[ ]
EOF
  printf '%s\n' "all done" > "$tmp/handoff-bad.md"
  cat > "$tmp/overrides-three.yaml" <<EOF
overrides:
  - check: step1_job_description
    file: $tmp/job-bad2.md
    reason: One.
    reviewed-by: Ian
    date: $TODAY
    expires: 2099-01-01
  - check: step2_allowlist
    file: $tmp/job-bad2.md
    reason: Two.
    reviewed-by: Ian
    date: $TODAY
    expires: 2099-01-01
  - check: step3_verify_handoff
    file: $tmp/handoff-bad.md
    reason: Three.
    reviewed-by: Ian
    date: $TODAY
    expires: 2099-01-01
EOF
  if bash "$SCRIPT_DIR/gate.sh" --root "$ROOT" --overrides "$tmp/overrides-three.yaml" --job "$tmp/job-bad2.md" --handoff "$tmp/handoff-bad.md" >/dev/null 2>&1; then
    echo "SELF-TEST FAIL: three overrides passed"; fail=1
  else
    echo "SELF-TEST PASS: three overrides trip the 'fix the check' failure"
  fi
  # Scenario 5: --warn-only turns a block failure into a pass.
  if bash "$SCRIPT_DIR/gate.sh" --root "$ROOT" --warn-only --job "$tmp/job-bad.md" >/dev/null 2>&1; then
    echo "SELF-TEST PASS: --warn-only lets a block failure through as a warning"
  else
    echo "SELF-TEST FAIL: --warn-only did not pass"; fail=1
  fi
  # Scenario 6: no inputs at all fails with "no checks ran".
  if bash "$SCRIPT_DIR/gate.sh" --root "$ROOT" 2>&1 | grep -q "no checks ran"; then
    echo "SELF-TEST PASS: zero checks fails with 'no checks ran'"
  else
    echo "SELF-TEST FAIL: zero checks did not fail"; fail=1
  fi
  rm -rf "$tmp"
  if [ "$fail" -ne 0 ]; then
    echo "SELF-TEST RESULT: FAIL"
    exit 1
  fi
  echo "SELF-TEST RESULT: PASS"
  exit 0
}

# --- main ------------------------------------------------------------------
if [ "$SELF_TEST" -eq 1 ]; then
  self_test
fi

MANIFEST="$ROOT/checks/manifest.yaml"
export GATE_MANIFEST="$MANIFEST"

if [ -n "$TARGET" ]; then
  if [ ! -d "$TARGET" ]; then
    echo "FAIL: --target is not a directory: $TARGET"; exit 2
  fi
  run_check "step3_run_checks" "$(tier_of step3_run_checks)" "$TARGET" \
    bash "$ROOT/skills/step-3-never-take-first-look/scripts/run_checks.sh" "$TARGET"
fi

if [ -n "$JOB" ]; then
  if [ ! -f "$JOB" ]; then echo "FAIL: --job is not a file: $JOB"; exit 2; fi
  run_check "step1_job_description" "$(tier_of step1_job_description)" "$JOB" \
    python3 "$ROOT/skills/step-1-onboard-like-a-new-hire/scripts/check_job_description.py" "$JOB" --tier="$(tier_of step1_job_description)"
  run_check "step2_prose_scan" "$(tier_of step2_prose_scan)" "$JOB" \
    python3 "$ROOT/skills/step-2-match-oversight-to-stakes/scripts/check_tools.py" "$JOB"
  run_check "step2_allowlist" "$(tier_of step2_allowlist)" "$JOB" \
    python3 "$ROOT/checks/check_tool_allowlist.py" "$JOB" --approvals="$ROOT/approvals.yaml" --tier="$(tier_of step2_allowlist)"
fi

if [ -n "$HANDOFF" ]; then
  if [ ! -f "$HANDOFF" ]; then echo "FAIL: --handoff is not a file: $HANDOFF"; exit 2; fi
  run_check "step3_verify_handoff" "$HANDOFF_TIER" "$HANDOFF" \
    python3 "$ROOT/skills/step-3-never-take-first-look/scripts/verify_handoff.py" "$HANDOFF" --tier="$HANDOFF_TIER"
fi

if [ -n "$REVIEW" ]; then
  if [ ! -f "$REVIEW" ]; then echo "FAIL: --review is not a file: $REVIEW"; exit 2; fi
  if [ -z "$AUTHOR_SESSION" ] || [ -z "$REVIEWER_SESSION" ]; then
    echo "FAIL: --review needs --author-session and --reviewer-session"; exit 2
  fi
  run_check "step3_review" "$(tier_of step3_review)" "$REVIEW" \
    python3 "$ROOT/checks/check_review.py" "$REVIEW" --author-session="$AUTHOR_SESSION" --reviewer-session="$REVIEWER_SESSION" --tier="$(tier_of step3_review)"
fi

if [ -n "$TASKS" ]; then
  if [ ! -f "$TASKS" ]; then echo "FAIL: --tasks is not a file: $TASKS"; exit 2; fi
  run_check "step5_watcher" "$(tier_of step5_watcher)" "$TASKS" \
    python3 "$ROOT/skills/step-5-proactive-not-reactive/scripts/watcher_check.py" "$TASKS"
fi

if [ -n "$LOGFILE" ]; then
  if [ ! -f "$LOGFILE" ]; then echo "FAIL: --log is not a file: $LOGFILE"; exit 2; fi
  run_check "step4_corrections" "$(tier_of step4_corrections)" "$LOGFILE" \
    python3 "$ROOT/checks/check_corrections.py" "$LOGFILE" --root="$ROOT" --tier="$(tier_of step4_corrections)"
fi

if [ -n "$ACTION" ]; then
  if [ ! -f "$ACTION" ]; then echo "FAIL: --action is not a file: $ACTION"; exit 2; fi
  run_check "step5_level5" "$(tier_of step5_level5)" "$ACTION" \
    python3 "$ROOT/checks/check_level5.py" "$ACTION" --approvals="$ROOT/approvals.yaml"
fi

finish
exit $?
