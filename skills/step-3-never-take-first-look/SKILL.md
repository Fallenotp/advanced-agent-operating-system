---
name: step-3-never-take-first-look
description: Check work before handing it over, never say done without evidence. Use when an agent finishes visual work, code, data or a spreadsheet, or writing, before the owner sees it, before a commit, merge, or anything public. Run the checker for that type of work, show real evidence, max 3 tries, say what was NOT checked, and use a fresh reviewer for public, money, or data work.
---

# Step 3 — Never take the first look

The owner's first look should never be the agent's first output. First drafts land roughly 70% there; with checks they get to 95–99%. An agent saying a task is done is not the same as it actually being done.

## When to use

- Before handing any work to the owner.
- Before a commit, merge, or anything a client or the public will see.
- Before anything that moves money or data.
- Every time, for every type of work — the checker changes, the rule does not.

## When not to use

- There is no "not to use". For low-stakes internal drafts, the agent's own check plus the owner's read is enough. The fresh reviewer (below) is only for high stakes.

## The blanket rule

**Never say done without evidence. Before you hand anything over:**

1. Run the check for this type of work (below) and show what it said — the real output, screenshot, total, or source, not a summary.
2. Fix what failed, biggest first, and run the check again. At most 3 tries. If it still fails, stop and tell the owner what is left, with the evidence.
3. Say what you did NOT check, and why.
4. Never change the check to make it pass. If you think the check is wrong, say so and let the owner change it.
5. For anything a customer, client, or the public will see, or anything that moves money or data: a different agent — a fresh session that did not make the work — checks it first, and it may say "no issues".

## Why the same agent cannot review its own work

It sees what it meant to make, not what is actually there — like grading its own homework. It misses typos and mistakes it already made. A check only works if the checker knows something the author did not: a test result, a screenshot, a recalculated total, a source document, or a fresh reviewer who never saw the reasoning.

Measured catch rates in the "Reflection & Verification" chapter's simulator (https://agent.xinbetween.com/c11/): self-critique in the same conversation catches about 11% of errors, and about 4% of claimed-but-not-done work. Ground truth (tests, a screenshot, a recalculated total) lifts that to about 90%, and claimed-but-not-done to about 99%. A fresh, independent critic catches about 73%. These are illustrative figures from that chapter's simulator, not results from a controlled study — the direction, not the decimals, is the point. (Sources: see `../../README.md`, Sources.)

## The four checkers

Pick the checker by output type. Full detail is in `references/checkers.md`.

### Visual — website, deck, card, PDF

Screenshot every page/slide, read every word, spelling, contrast, positioning, cut-off/overlap. Click every button and link. Phone size as well as computer size. Max 3 passes. Hand over with a checked list. A screenshot you did not read is not a verified screen.

### Code — app, script, website code

Build + lint + typecheck + tests, paste the real output. Then run the real app end to end and drive the changed feature like a user would. A passing unit suite with an app that will not start is a failed verification. Fresh reviewer for anything important. Never let the change edit its own judge — tests, lint config, and the checklist live where the change cannot touch them.

### Data / spreadsheets

Totals must be formulas, never a number typed in by hand. Recalculate (for spreadsheets, bake with a real recalculator, not just the file writer). Spot-check 2–3 rows by hand against numbers you already know. Reconcile the total against a trusted number. Read back the computed value after recalculation. If the total does not move the way the change intended, the write is wrong even though it succeeded.

### Writing / docs

Pull out every number, date, name, quote, and link. Open each source and confirm it says that. Delete anything that cannot be confirmed after a genuine search — do not soften the wording. Read the whole thing top to bottom for spelling and consistency. Click every link.

## Fresh reviewer

- Use a different agent or a fresh session that never saw how the work was made.
- Give it only the finished work, the acceptance criteria, and a rubric. Do not show it the reasoning that produced the work.
- It may say "no issues". A reviewer told only to find problems will invent them.
- For subjective work (an email, a script): tune the judge against the owner marking pass/fail on real examples until it agrees with the owner.

## Evidence, not a feeling

- Show the command and its output, or the screenshot, or the total, or the source.
- "All tests pass" on its own tells the owner very little. Reading the output is faster than rerunning the check.
- Stamp the handoff with what was verified, including `none` where nothing was verified — an honest `none` can be found later.
- Keep the checklist where the agent reads it but cannot edit it. A check the work can modify is a broken check.

## Scripts

- `scripts/run_checks.sh` — runs the project's build, lint, typecheck, and test commands if they exist, and prints which ones were not run and why. Exit code is non-zero if any check fails. Script code never enters context; only its output does.
- `scripts/verify_handoff.py <handoff-file>` — deterministic check that a handoff file contains real evidence, a "not checked" section, and a tries count of 3 or fewer.

## Done check

- The right checker ran, evidence is shown, tries are 3 or fewer, and what was NOT checked is stated.
- High-stakes work went to a fresh reviewer first.
- If a miss slips through anyway, log it — that is Step 4 (`step-4-every-correction-becomes-the-system`). Twice is a pattern.

## References

- `references/checkers.md` — the full Visual, Code, Data, and Writing checkers.
