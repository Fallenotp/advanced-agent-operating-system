# How the gate checkers work

Enforcement is by checks, never by agent-side hooks. A check is a small script that looks at a file and says pass or fail. The blocking power comes from where it runs, not from the script — so the same checks run in three places: the agent runs them before it hands anything over, they run in CI on every pull request, and CI is a required status check, so a red check stops the merge.

- The skill names the exact check.
- The always-on file says: run the check after every change.
- The same check runs in CI on every change, and blocks the merge if it fails.
- A check the work can modify is a broken check. The checklist lives where the agent reads it but cannot edit it. Never let a change edit its own judge.

## The gate — `checks/gate.sh`

One runner calls every checker and prints PASS or FAIL per check, with the file and line. Exit 0 means every BLOCK-tier check passed; exit 1 means a BLOCK check failed; exit 2 is a usage error; zero checks run is a FAIL. Run it before a handoff, or let CI run it: `bash checks/gate.sh --target=.` for a whole directory, or `--job=`, `--handoff=`, `--review=`, `--tasks=`, `--log=`, `--action=` for one piece of work. `--self-test` runs the full negative corpus plus the override and tripwire scenarios. `--warn-only` runs new or changed checks as warnings first — use it for two weeks before promoting a check to BLOCK, and measure the false-positive rate.

Every option also accepts the space form (`--target .`). The `=` form is the documented one.

## Tiers — what blocks and what warns

Every checker prints its tier. BLOCK stops the merge; WARN shows up in the output and the run still passes. Tiers live in [`checks/manifest.yaml`](../../checks/manifest.yaml).

| Check | Tier |
|---|---|
| Step 1 job description | BLOCK |
| Step 2 prose scan | WARN, never BLOCK — it reads free text, so it trips on ordinary English |
| Step 2 tool allowlist | BLOCK |
| Step 3 handoff evidence | BLOCK for public, money, or data work; WARN for internal drafts |
| Step 3 run-checks | BLOCK where code checks apply |
| Step 4 corrections log | WARN first; BLOCK only after two weeks of clean runs |
| Step 5 watcher | WARN, never BLOCK a merge |
| Step 5 level-5 approvals | BLOCK |
| Fresh review | BLOCK for public, money, or data work; WARN otherwise |
| Changes to `checks/` or `approvals.yaml` | BLOCK, code-owner review required, never overridable |

## Why the checks read structure, not prose

The first version of these checkers matched words in free text, and it failed both ways: it blocked good work (a filled brief failed for one `[ ]` in an example; "pay attention" and "post a summary" got flagged as high-risk actions; "Used 2 tries" failed) and it passed bad work (a nonsense brief passed; "Never forget: the agent must send the weekly report" passed; a made-up test result passed). The fix was to check structure instead — sections and fields in a job description, the tool list in Section 8, a problem-id in a log row, an approval record with a task-id and a date. A check that cannot tell good input from bad input is not a check: every checker ships with a negative corpus in [`checks/tests/corpus.json`](../../checks/tests/corpus.json) — legitimate inputs it must pass and cheating inputs it must fail — and CI runs it (`python3 checks/tests/run_corpus.py`). If a checker cannot pass its own corpus, it ships as WARN, not BLOCK.

The full story of what went wrong building these checks, round by round, is in [lint-checks-that-hold.md](lint-checks-that-hold.md).

## Overrides — the escape hatch

When a check is wrong and the work is right, record it in [`checks/overrides.yaml`](../../checks/overrides.yaml): the check, the file, the reason in plain English, who reviewed it (a named human, never the agent), the date, and when it expires (7 days by default). The gate prints `OVERRIDDEN: <check> on <file> — <reason> (by <name>, expires <date>)`. An expired override, or one naming a check or file not in the run, fails the run. More than 2 overrides in one run, or more than 20% of runs in a week using an override, fails the run with "the check is wrong, fix the check" — that is the tripwire: an override used twice for the same check is a pattern, so rewrite the check. Emergency path: if CI is down, the owner merges with a recorded override ("CI unavailable, checks run locally, output attached") and attaches the local output to the pull request.

## What the gate cannot check

No script can tell whether evidence is genuine, whether a fix is correct, or whether a brief makes sense. That is the fresh reviewer's job (Step 3). The gate proves the paperwork exists; the reviewer proves the work is real.

## The checkers, one by one

| Checker | Question it answers | Tier |
|---|---|---|
| `skills/step-1-onboard-like-a-new-hire/scripts/check_job_description.py` | Does the job description have all eleven fields, with real content? | BLOCK |
| `skills/step-2-match-oversight-to-stakes/scripts/check_tools.py` | Does the prose mention risky actions (send, post, publish, deploy, delete, pay)? | WARN, never BLOCK |
| `checks/check_tool_allowlist.py` | Does the structured tool list allow a risky action without an approval? | BLOCK |
| `skills/step-3-never-take-first-look/scripts/verify_handoff.py` | Does the handoff show real evidence, a not-checked section, and 3 or fewer tries? | BLOCK / WARN |
| `skills/step-3-never-take-first-look/scripts/run_checks.sh` | Do the project's own build, lint, typecheck, and test commands pass? | BLOCK where code checks apply |
| `checks/check_review.py` | Is the reviewer a different session from the author, and does the review quote the work? | BLOCK / WARN |
| `skills/step-4-every-correction-becomes-the-system/scripts/log_correction.py` | Appends a log row and counts repeats by problem-id. | — |
| `checks/check_corrections.py` | Does a pattern row prove its fix (file changed on or after the row date, owner approved)? | WARN first, then BLOCK |
| `skills/step-5-proactive-not-reactive/scripts/watcher_check.py` | What is overdue, and what is due in 3 days with no owner? | WARN, never BLOCK |
| `checks/check_level5.py` | Does a Level 5 action have an approval that covers it? | BLOCK |
