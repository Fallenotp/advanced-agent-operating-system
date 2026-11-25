# Contributing

This guide is owned by the maintainer, and the maintainer decides on pull requests. Opening a PR does not create an obligation to review or merge it.

## The rules

**Solve one underlying problem per PR.** One fix, one change, one reason. A PR that fixes three things, or a fix plus a rewrite, will be asked to split. If you cannot state the problem in one sentence, you do not have a PR yet.

**Provide evidence for the changed behaviour.** A checkbox or "tests pass" alone does not show that the change works. Show the real output: the gate run, the corpus result, the before and after. For a doc change, quote the source you opened. For a checker change, show the corpus case that proves it — a good input it now passes, or a cheating input it now fails.

**Run the gate before opening a PR.** `bash checks/gate.sh --target=.` and `bash checks/gate.sh --self-test`. Paste the real output in the PR. A PR with a red gate and no override will not be reviewed.

**Do not edit the gate to make your change pass.** If a check blocks good work, fix the check — and prove the fix with the corpus. A change that edits its own judge is a broken check. Changes to `checks/`, `approvals.yaml`, and `.github/workflows/` need the owner's review.

**Write in the voice of the repo.** Plain words, short sentences, second person. Every claim a reader could act on must be confirmed against the repo itself. Delete anything that cannot be confirmed — do not soften it.

**Keep the manual true.** Every number, date, name, quote, and link must come from a source that was opened. Sources live in `docs/README.md`.

## What a good PR looks like

- Problem: one sentence, what is wrong and where.
- Change: what you changed, file by file.
- Scope and approval: what this does and does not touch, and whose approval it needs.
- Verification: the gate output, the corpus result, and what you did not check.

## What will be closed

- A PR with no problem statement, or one that bundles several problems.
- A PR that changes the license. The manual is CC BY 4.0.
- A PR that adds a check with no corpus cases for it. A checker with no tests is a guess.
- A PR that puts real user data in an example, a screenshot, or a fixture.
