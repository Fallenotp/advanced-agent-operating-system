# Merging

## The rule

Nothing merges into `main` without a pull request, a green `checks` run, and the owner's review where it counts. Until the branch ruleset in [setup-checklist.md](setup-checklist.md) exists, none of this is enforced — a red check is advice and a direct push goes through. Treat the ruleset as unfinished work, not as done.

## The flow

1. Open a pull request from a branch. One underlying problem per pull request — not three fixes in one, not a fix plus a rewrite. See [CONTRIBUTING.md](../../CONTRIBUTING.md).
2. CI runs the `checks` job (`.github/workflows/checks.yml`). It compiles every Python file, syntax-checks the shell files, parses every YAML file, runs each checker against its fixtures, runs the negative corpus, runs the gate self-test, and runs the gate on the repo itself.
3. If a check fails and the work is right, record an override in `checks/overrides.yaml` — check, file, reason in plain English, reviewed-by (a named human, never the agent), date, expires in 7 days. An override used twice for the same check is a pattern: rewrite the check instead.
4. A pull request that touches `checks/`, `approvals.yaml`, or `.github/workflows/` needs the owner's review. `CODEOWNERS` names `@Fallenotp` for those paths, and the ruleset must require code-owner review for it to bite. An agent cannot quietly rewrite its own judge.
5. Merge with a merge commit. No rebase, no squash — the history should show what was reviewed, as it was reviewed.

## What blocks a merge

- Any BLOCK-tier check failing (see [gate-checkers.md](../internals/gate-checkers.md) for the tier table).
- A missing or failing `checks` status check, once the ruleset requires it.
- A change to the gate itself without the owner's review.
- A fresh review missing for public, money, or data work — the gate proves the paperwork exists, a different agent proves the work is real.

## What does not block a merge

- WARN-tier failures. They print in the log and the run still passes. A check that blocks good work twice is a pattern — rewrite the check, do not teach people to work around it.
- A failing check with a valid, unexpired override. The gate prints `OVERRIDDEN` so the exception is visible.
