# Step 4 — Every correction becomes the system

Never fix the same problem more than twice. Once can be a one-off. The second time, funnel it into a skill.

## The loop

1. **Log it.** Triggered by an error, a failed check, or the owner spotting a mistake. Each entry records: date, a problem-id slug, which system/agent, what task, expected vs actual, inputs/files/screenshot, and how bad it was. Run [`skills/step-4-every-correction-becomes-the-system/scripts/log_correction.py`](../../skills/step-4-every-correction-becomes-the-system/scripts/log_correction.py) to append an entry and count repeats by problem-id.
2. **Find the pattern.** Twice is a pattern. Compare expected vs actual and trace back to the missing or unclear instruction.
3. **Rewrite the system, not the model.** What gets rewritten is the skill file, the job description, the checklist, or an example — usually a short "gotcha" (the trap, and what to do instead). The agent does not retrain itself. It "learns" by updating its written instructions.
4. **Ground the fix.** A fix should be proposed by thinking, then grounded by research, documentation, a working example, or a test. Thinking alone can invent a plausible-but-wrong fix.
5. **The owner approves.** The owner approves the lesson before it becomes permanent, at least for anything important. An agent can learn the wrong lesson from one failure, or overcorrect. Human approval stops that. Never fully automatic.
6. **Test it on the next run.** Re-run the task, or a test case, clean two or three times. Test on the failing case plus old cases that used to pass.

Separate the jobs: the thing that does the work, the thing that grades the work, and the thing that proposes the fix must be separate — generator, verifier, and coach. One change at a time.

New automations are glass balls — drop one and it shatters. They become rubber balls when three things exist: corrections stored in a skill, traces (a clear history of what the agent actually output), and notifications (the owner finds out when something errors). Underneath all of it: a named human owner for every automation.

## How to log

Each entry records: date, a problem-id slug (e.g. `video-timing-mismatch`), which system/agent, what task, expected vs actual, inputs/files/screenshot, and how bad it was.

The problem-id is the key the pattern count uses — never free text. Counting by substring overcounts: "video timing" and "video captions" are two different problems, but a substring count on "video" calls them one pattern. Two rows with the same problem-id are the same problem; the same failure worded differently is two rows until a human confirms the match and reuses the same problem-id.

For a row marked as a pattern, the Owner approved? cell must read `Yes — <name>, <date>` (for example `Yes — Ian, 2026-11-23`), and the Fix proposed cell must name the file that changed. A row that says "fix applied" with no actual change fails the check; a real fix recorded only in prose ("updated the skill") fails it too — write the file down.

A fix is proposed by thinking, then grounded by research, documentation, a working example, or a test. The owner approves it before it becomes permanent. Then test it on the next run, plus old cases that used to pass.

A helper script is in [`skills/step-4-every-correction-becomes-the-system/scripts/log_correction.py`](../../skills/step-4-every-correction-becomes-the-system/scripts/log_correction.py) — it appends a row and prints `PATTERN` when the same problem-id has appeared twice. [`checks/check_corrections.py`](../../checks/check_corrections.py) verifies a pattern row proves its fix: the named file exists and changed on or after the log date, and the approval is dated and not in the future.

## Format

| Date | Problem ID | System | Task | Expected vs actual | Severity | Pattern? | Fix proposed | Owner approved? | Tested? |
|---|---|---|---|---|---|---|---|---|---|

Filled rows are in Worked examples below. Do not put a placeholder row here — `check_corrections.py` reads every row in this file, and a row with `YYYY-MM-DD` as its date fails the check.

## Worked examples (2026-11-23)

These are two real corrections from the first run of this system. Names and project details have been removed — the shape is what matters.

| Date | Problem ID | System | Task | Expected vs actual | Severity | Pattern? | Fix proposed | Owner approved? | Tested? |
|---|---|---|---|---|---|---|---|---|---|
| 2026-11-23 | step-four-page-unreadable | Step Four web page | Read the page top to bottom | Expected: full page readable, all content as real text. Actual: sticky table-of-contents overlay, text clipped mid-line under the overlay, only about a third of the screen readable at a time. | high | No — first occurrence logged here | Remove the sticky table of contents entirely, no fixed or floating elements, put all six stages, all three levels, and all four work-type tables in the page as real text, fix the 210-word example so it is 210 everywhere | Yes — Ian, 2026-11-23 | Yes — builder audit passed, the owner confirmed on 2026-11-23 that he could read it |
| 2026-11-23 | step-3-not-applied-to-own-work | The agent's own work (Step Four page build) | Apply Step 3 to the agent's own work before handoff | Expected: agent checks its own work before the owner sees it. Actual: the page was handed over as reviewed without the Step 3 self-check being applied; the owner flagged it and asked the agent to apply the concept to its own work. | medium | Yes — the same gap happened in earlier work, where subagents handed work straight to the owner so he was the first look, except one video-verification workflow where a separate check caught timing mismatches and gaps | Add the Step 3 blanket rule and the four checkers as a skill — see `skills/step-3-never-take-first-look/SKILL.md` — and require a rendered read-through before handoff | Yes — Ian, 2026-11-23 | Partly — applied and verified on the Step Four fix (audit passed, owner confirmed readable); the skill itself is new and has not yet been tested on a fresh job |

## Separate the jobs

The thing that does the work, the thing that grades the work, and the thing that proposes the fix must be separate.

- **Generator** — does the job.
- **Verifier** — grades the work. It never fixes its own work.
- **Coach** — proposes one change at a time, based on the verifier's findings and the log.

One change at a time. A change that is claimed to help must be tested — in the research, over half of claimed improvements were flat or worse when actually tested. Do not stack several fixes at once and guess which one worked.

## Glass balls and rubber balls

New automations are glass balls — drop one and it shatters. They become rubber balls when three things exist:

1. Evaluations and corrections stored in a skill (or a simple sheet with run history and feedback).
2. Traces — a clear history of what the agent actually output, so you can troubleshoot.
3. Notifications — the owner finds out when something errors.

Underneath all of it: a named human owner for every automation. List every automation, who owns it, and when it was last checked — like an inspection tag. Keep that list in one place: one line per automation — what it is, who owns it, and when it was last checked.

## Pitfalls

- Feedback never written down.
- Corrections that contradict each other.
- Skills growing bloated — keep the gotcha short, move detail to references.
- An agent learning the wrong lesson from one failure — owner approval stops this.
- No owner, no review, no notification.
- The grader fixing its own work, or the change editing its own judge.

## Practical setup for a solo user

- One sheet as the run log (this page) plus the owner list.
- One skill per recurring job, with a Gotchas section.
- After every fix: "Fix it, then add this to the skill so it never happens again."
- A short weekly review — about 20 minutes — of the log: what repeated, what got fixed, what still needs the owner.

## Done check

- The failure is logged with context.
- The pattern (if any) is named, or the entry is marked as a watched one-off.
- The fix is grounded, proposed as one change, approved by the owner, and tested on the next run plus old cases.
- The skill, checklist, or job description was actually updated — not just the one output.

## The skill

[`skills/step-4-every-correction-becomes-the-system/`](../../skills/step-4-every-correction-becomes-the-system/) — `SKILL.md`, `scripts/log_correction.py`.
