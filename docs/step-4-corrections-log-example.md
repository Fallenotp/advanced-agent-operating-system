# Corrections Log — Format and Worked Examples

Every failure, failed check, or owner correction goes here, with context. Never fix the same problem more than twice — twice is a pattern, and a pattern means rewriting the skill, checklist, or job description (Step 4).

## How to log

Each entry records: date, a problem-id slug (e.g. `video-timing-mismatch`), which system/agent, what task, expected vs actual, inputs/files/screenshot, and how bad it was.

The problem-id is the key the pattern count uses — never free text. Counting by substring overcounts: "video timing" and "video captions" are two different problems, but a substring count on "video" calls them one pattern. Two rows with the same problem-id are the same problem; the same failure worded differently is two rows until a human confirms the match and reuses the same problem-id.

For a row marked as a pattern, the Owner approved? cell must read `Yes — <name>, <date>` (for example `Yes — Ian, 2026-11-23`), and the Fix proposed cell must name the file that changed. A row that says "fix applied" with no actual change fails the check; a real fix recorded only in prose ("updated the skill") fails it too — write the file down.

A fix is proposed by thinking, then grounded by research, documentation, a working example, or a test. The owner approves it before it becomes permanent. Then test it on the next run, plus old cases that used to pass.

A helper script is in `../skills/step-4-every-correction-becomes-the-system/scripts/log_correction.py` — it appends a row and prints `PATTERN` when the same problem-id has appeared twice. `../checks/check_corrections.py` verifies a pattern row proves its fix: the named file exists and changed after the log date, and the approval is dated and not in the future.

## Format

| Date | Problem ID | System | Task | Expected vs actual | Severity | Pattern? | Fix proposed | Owner approved? | Tested? |
|---|---|---|---|---|---|---|---|---|---|
| YYYY-MM-DD | problem-slug |  |  | Expected: ... Actual: ... | low / medium / high | No / Yes |  | Yes — Name, YYYY-MM-DD / No | Yes / No / Partly |

## Worked examples (2026-11-23)

These are two real corrections from the first run of this system. Names and project details have been removed — the shape is what matters.

| Date | Problem ID | System | Task | Expected vs actual | Severity | Pattern? | Fix proposed | Owner approved? | Tested? |
|---|---|---|---|---|---|---|---|---|---|
| 2026-11-23 | step-four-page-unreadable | Step Four web page | Read the page top to bottom | Expected: full page readable, all content as real text. Actual: sticky table-of-contents overlay, text clipped mid-line under the overlay, only about a third of the screen readable at a time. | high | No — first occurrence logged here | Remove the sticky table of contents entirely, no fixed or floating elements, put all six stages, all three levels, and all four work-type tables in the page as real text, fix the 210-word example so it is 210 everywhere | Yes — Ian, 2026-11-23 | Yes — builder audit passed, the owner confirmed on 2026-11-23 that he could read it |
| 2026-11-23 | step-3-not-applied-to-own-work | The agent's own work (Step Four page build) | Apply Step 3 to the agent's own work before handoff | Expected: agent checks its own work before the owner sees it. Actual: the page was handed over as reviewed without the Step 3 self-check being applied; the owner flagged it and asked the agent to apply the concept to its own work. | medium | Yes — the same gap happened in earlier work, where subagents handed work straight to the owner so he was the first look, except one video-verification workflow where a separate check caught timing mismatches and gaps | Add the Step 3 blanket rule and the four checkers as a skill (`step-3-never-take-first-look`), and require a rendered read-through before handoff | Yes — Ian, 2026-11-23 | Partly — applied and verified on the Step Four fix (audit passed, owner confirmed readable); the skill itself is new and has not yet been tested on a fresh job |
