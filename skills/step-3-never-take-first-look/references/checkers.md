# The four checkers — Step 3

Pick the checker by output type. The blanket rule in `../SKILL.md` is the gate; the checker is the evidence.

## Visual — website, deck, card, PDF

1. Look at the finished thing, not the code. Screenshot every page, every slide, every card — front and back if there are two sides. Render every image to pixels and look at it as a picture. Reading an image file's source code — SVG or XML — is not a visual check; a picture you only read as code is not a verified picture.
2. Read every word on every screenshot. Check spelling against the source copy. Check nothing is cut off at the edge, nothing overlaps anything else, and text is big enough to read.
3. Check contrast: dark text on a light background, or light text on a dark background — never light grey on white, never dark on dark.
4. Check positioning: headings line up, spacing is even, nothing is pushed off the screen, nothing scrolls sideways.
5. Click every button and every link. Fill in every form the way a real person would. Screenshot what happens after each click. If a button does nothing, or goes to the wrong place, that is a fail.
6. Check on a phone-sized screen as well as a computer screen.
7. Fix what you found — biggest problem first — then look again from step 1. At most 3 times.
8. If it still is not right after 3 tries, mark the affected job BLOCKED and send the remaining faults and screenshots to the orchestrator. Do not keep fixing in circles.
9. When you hand it over, say what you checked, in one short list: pages/slides checked, buttons clicked, problems found and fixed, and anything you could not check. A screenshot you did not read is not a check.

For a deck, check every slide for five things: cut-off text or faces, low contrast, overlapping elements, empty areas that look unfinished, and text too small to read.

## Code — app, script, website code

1. Build it. Paste the real build output.
2. Run lint. Paste the real lint output.
3. Run typecheck. Paste the real typecheck output.
4. Run tests. Paste the real test output.
5. Run the real app end to end and drive the changed feature like a user would. A passing unit suite with an app that will not start is a failed verification.
6. Fresh reviewer for anything important: a different agent or fresh session that never saw how the work was made, given only the finished work and the acceptance criteria.
7. Never let the change edit its own judge. Tests, lint config, and the checklist live where the change cannot touch them.

Use `../scripts/run_checks.sh` for steps 1–4 where the project has those commands. It prints which checks were not run and why.

## Data / spreadsheets

1. Totals must be formulas (for example `=SUM(...)`), never a number typed in by hand. When source data changes, the workbook must recompute itself.
2. Recalculate with a real recalculator — a file writer alone does not evaluate formulas. Flag any `#REF!` or `#DIV/0!`.
3. Spot-check 2–3 rows by hand against numbers you already know, spread across start, middle, and end. An error-free sheet can still point at the wrong row.
4. Reconcile the total against an independent number you already trust, and explain any difference.
5. Read back the computed value in the cells you touched after recalculation — not your own success message. If the total does not move the way the change intended, the write is wrong even though it succeeded.
6. Test with a case whose answer you already know, including an edge case such as a value that is not there.

## Writing / docs

1. Pull out every number, date, name, quote, and link before trusting a sentence.
2. Open each source and confirm it says that. Check the date, and check who is talking — the organisation that owns the fact beats a summary.
3. Cross-check the 1–3 claims that would hurt if wrong against one independent source.
4. When a claim cannot be confirmed after a genuine search, delete it instead of softening the wording.
5. Read the finished document top to bottom for spelling and consistency. Click every link.
6. Quotes and statistics need a primary source you opened yourself, not a secondhand mention.
