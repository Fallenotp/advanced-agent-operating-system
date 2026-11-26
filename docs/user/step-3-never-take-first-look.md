# Step 3 — Never take the first look

The agent must check its own work before you see it. First drafts land roughly 70% there; with checks they get to 95–99%. Your first look should never be the agent's first output.

## The blanket rule — never say done without evidence

Before anything is handed over:

1. Run the check for this type of work and show what it said — the real output, screenshot, total, or source, not a summary.
2. Fix what failed, biggest first, and run the check again. At most 3 tries. If it still fails, mark the affected job BLOCKED and report the remaining faults and evidence to the orchestrator.
3. Say what you did NOT check, and why.
4. Never change the check to make it pass. If you think the check is wrong, say so and let the owner change it.
5. For anything a customer, client, or the public will see, or anything that moves money or data: a different agent — a fresh session that did not make the work — checks it first, and it may say "no issues".

Why the same agent cannot review its own work: it sees what it meant to make, not what is actually there — like grading its own homework. A check only works if the checker knows something the author did not: a test result, a screenshot, a recalculated total, a source document, or a fresh reviewer.

Measured catch rates in the "Reflection & Verification" chapter's simulator (https://agent.xinbetween.com/c11/): self-critique in the same conversation catches about 11% of errors, and about 4% of claimed-but-not-done work. Ground truth (tests, a screenshot, a recalculated total) lifts that to about 90%, and claimed-but-not-done to about 99%. A fresh, independent critic catches about 73%. These are illustrative figures from that chapter's simulator, not results from a controlled study — the direction, not the decimals, is the point.

## The four checkers

Pick the checker by output type. The blanket rule in [`skills/step-3-never-take-first-look/SKILL.md`](../../skills/step-3-never-take-first-look/SKILL.md) is the gate; the checker is the evidence.

- **Visual** (website, deck, card, PDF): screenshot every page/slide, read every word, spelling, contrast, positioning, cut-off/overlap. Click every button and link. Phone size as well as computer size. Max 3 passes.
- **Code** (app, script, website code): build + lint + typecheck + tests, paste the real output. Then run the real app end to end and drive the changed feature like a user would.
- **Data / spreadsheets**: totals must be formulas, never a number typed in by hand. Recalculate, spot-check 2–3 rows by hand against numbers you already know, reconcile the total against a trusted number, read back the computed value after recalculation.
- **Writing / docs**: pull out every number, date, name, quote, and link. Open each source and confirm it says that. Delete anything that cannot be confirmed. Read the whole thing top to bottom. Click every link.

The full checkers are below.

### Visual — website, deck, card, PDF

1. Look at the finished thing, not the code. Screenshot every page, every slide, every card — front and back if there are two sides.
2. Read every word on every screenshot. Check spelling against the source copy. Check nothing is cut off at the edge, nothing overlaps anything else, and text is big enough to read.
3. Check contrast: dark text on a light background, or light text on a dark background — never light grey on white, never dark on dark.
4. Check positioning: headings line up, spacing is even, nothing is pushed off the screen, nothing scrolls sideways.
5. Click every button and every link. Fill in every form the way a real person would. Screenshot what happens after each click. If a button does nothing, or goes to the wrong place, that is a fail.
6. Check on a phone-sized screen as well as a computer screen.
7. Fix what you found — biggest problem first — then look again from step 1. At most 3 times.
8. If it still is not right after 3 tries, mark the affected job BLOCKED and send the remaining faults and screenshots to the orchestrator. Do not keep fixing in circles.
9. When you hand it over, say what you checked, in one short list: pages/slides checked, buttons clicked, problems found and fixed, and anything you could not check. A screenshot you did not read is not a check.

For a deck, check every slide for five things: cut-off text or faces, low contrast, overlapping elements, empty areas that look unfinished, and text too small to read.

### Code — app, script, website code

1. Build it. Paste the real build output.
2. Run lint. Paste the real lint output.
3. Run typecheck. Paste the real typecheck output.
4. Run tests. Paste the real test output.
5. Run the real app end to end and drive the changed feature like a user would. A passing unit suite with an app that will not start is a failed verification.
6. Fresh reviewer for anything important: a different agent or fresh session that never saw how the work was made, given only the finished work and the acceptance criteria.
7. Never let the change edit its own judge. Tests, lint config, and the checklist live where the change cannot touch them.

Use [`skills/step-3-never-take-first-look/scripts/run_checks.sh`](../../skills/step-3-never-take-first-look/scripts/run_checks.sh) for steps 1–4 where the project has those commands. It prints which checks were not run and why. It reads [`checks/manifest.yaml`](../../checks/manifest.yaml) first: code checks apply only to a project with a `package.json` or a `pyproject.toml`. A directory with no code files passes with a note ("no code checks apply") instead of failing. A project with code files but no test script fails — zero checks ran when checks were applicable. A test script that prints no test count (for example a script that just runs `true`) warns instead of passing. The runner only executes project scripts in CI or a sandbox — never as a local gate on an untrusted pull request, because a test script is arbitrary code.

### Data / spreadsheets

1. Totals must be formulas (for example `=SUM(...)`), never a number typed in by hand. When source data changes, the workbook must recompute itself.
2. Recalculate with a real recalculator — a file writer alone does not evaluate formulas. Flag any `#REF!` or `#DIV/0!`.
3. Spot-check 2–3 rows by hand against numbers you already know, spread across start, middle, and end. An error-free sheet can still point at the wrong row.
4. Reconcile the total against an independent number you already trust, and explain any difference.
5. Read back the computed value in the cells you touched after recalculation — not your own success message. If the total does not move the way the change intended, the write is wrong even though it succeeded.
6. Test with a case whose answer you already know, including an edge case such as a value that is not there.

### Writing / docs

1. Pull out every number, date, name, quote, and link before trusting a sentence.
2. Open each source and confirm it says that. Check the date, and check who is talking — the organisation that owns the fact beats a summary.
3. Cross-check the 1–3 claims that would hurt if wrong against one independent source.
4. When a claim cannot be confirmed after a genuine search, delete it instead of softening the wording.
5. Read the finished document top to bottom for spelling and consistency. Click every link.
6. Quotes and statistics need a primary source you opened yourself, not a secondhand mention.

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

- [`scripts/run_checks.sh`](../../skills/step-3-never-take-first-look/scripts/run_checks.sh) — runs the project's build, lint, typecheck, and test commands if they exist, and prints which ones were not run and why. Exit code is non-zero if any check fails. Script code never enters context; only its output does.
- [`scripts/verify_handoff.py`](../../skills/step-3-never-take-first-look/scripts/verify_handoff.py) — deterministic check that a handoff file contains real evidence, a "not checked" section, and a tries count of 3 or fewer.

## Done check

- The right checker ran, evidence is shown, tries are 3 or fewer, and what was NOT checked is stated.
- High-stakes work went to a fresh reviewer first.
- If a miss slips through anyway, log it — that is Step 4 ([step-4-every-correction-becomes-the-system.md](step-4-every-correction-becomes-the-system.md)). Twice is a pattern.

## The skill

[`skills/step-3-never-take-first-look/`](../../skills/step-3-never-take-first-look/) — `SKILL.md`, `references/checkers.md`, `scripts/run_checks.sh`, `scripts/verify_handoff.py`.
