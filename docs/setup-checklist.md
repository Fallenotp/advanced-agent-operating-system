# Setup checklist

The gate scripts are the easy half. The hard half is the settings on the repo, and a script cannot do those for you. Work through this list once, by hand, after the repo is created.

## 1. Protect `main` with a branch ruleset

A workflow file on its own is advice. A ruleset is the gate. On GitHub: repo → Settings → Rules → Rulesets → New ruleset → Branch ruleset.

- Name it `gate`.
- Target: the `main` branch.
- Turn on **Require a pull request before merging** (at least 1 approval).
- Turn on **Require status checks to pass** and select the `gate` job from `.github/workflows/checks.yml`. Without this, a red check is a suggestion and the merge goes through anyway.
- Turn on **Block force pushes** and **Block deletions**.
- Leave "Require approval from someone other than the last pusher" on if it is offered.

Until this ruleset exists, every check in this repo is advisory. The CI run still shows red or green, but nothing stops a bad merge.

## 2. Make CODEOWNERS take effect

`CODEOWNERS` lists `@Fallenotp` as the owner of `checks/`, `approvals.yaml`, and `.github/workflows/`. That file only bites when the branch ruleset above requires review from code owners. In the same ruleset, turn on **Require review from Code Owners**. From then on, a pull request that touches a checker, an approval, or the workflow cannot merge without the owner's review — an agent cannot quietly rewrite its own judge.

## 3. Check the workflow ran

Open the Actions tab after the first push. The `gate` job must show green. Click into it and confirm these steps ran:

- Step 1 job-description checker — blank template fails, filled fixture passes.
- Step 2 tools checker — blank template passes, risky brief fails.
- Step 3 handoff checker — vacuous handoff fails, good handoff passes; the negative corpus runs (`python3 checks/tests/run_corpus.py`).
- Step 3 run-checks — docs-only directory passes with a note; package fixture passes; empty-scripts fixture fails; the `true` test script warns.
- Step 4 log — a fresh log file works; a repeated problem-id prints `PATTERN`.
- Step 5 watcher — a bad date does not silence the run; owner `TBD` is flagged.
- Gate self-test (`bash checks/gate.sh --self-test`) — all six scenarios pass.

If any step is missing from the run, the workflow file drifted from the scripts — fix the workflow, not the scripts.

## 4. Decide the tier for your own work

The gate ships with these tiers (`checks/manifest.yaml`):

- Step 1 — BLOCK for new delegations, WARN otherwise.
- Step 2 prose scan — WARN, never BLOCK. Step 2 allowlist — BLOCK.
- Step 3 handoff — BLOCK for public, money, or data work; WARN for internal drafts. `run_checks.sh` — BLOCK where code checks apply.
- Step 4 — WARN first; promote to BLOCK only after two weeks of clean runs.
- Step 5 watcher — WARN, never BLOCK a merge. Step 5 level-5 approvals — BLOCK.
- Review — BLOCK for public, money, or data work; WARN otherwise.
- Changes to `checks/` or `approvals.yaml` — BLOCK, code-owner review required, never overridable.

For the first two weeks, run the gate with `--warn-only` and watch the false-positive rate. A check that blocks good work twice is a pattern — rewrite the check (Step 4), do not teach people to work around it.

## 5. Overrides — the escape hatch

When a check is wrong and the work is right, record an override in `checks/overrides.yaml`: the check, the file, the reason in plain English, who reviewed it (a named human, never the agent), the date, and when it expires (7 days by default). The gate prints `OVERRIDDEN: <check> on <file> — <reason> (by <name>, expires <date>)`.

- An expired override, or one naming a check or file not in the run, fails the run.
- More than 2 overrides in one run fails the run with "the check is wrong, fix the check".
- More than 20% of runs in a week using an override fails the run the same way.
- An override used twice for the same check is a pattern — rewrite the check.

Emergency path: if CI is down, the owner merges with a recorded override — reason "CI unavailable, checks run locally, output attached" — and the local output is attached to the pull request.

## 6. What the gate cannot check

No script can tell whether evidence is genuine, whether a fix is correct, or whether a brief makes sense. That is the fresh reviewer's job (Step 3): a different agent or fresh session, given only the finished work and the acceptance criteria. The gate proves the paperwork exists; the reviewer proves the work is real.
