---
name: step-4-every-correction-becomes-the-system
description: Turn every correction into the system so the same mistake is never fixed twice. Use when a mistake happens twice, a check fails, the owner corrects something, or a fix is proposed. Log it with context, find the pattern, rewrite the skill, checklist, or job description, ground the fix in research or a test, get the owner's approval before it becomes permanent, and test it on the next run.
---

# Step 4 — Every correction becomes the system

Never fix the same problem more than twice. Once can be a one-off. The second time, funnel it into a skill.

## When to use

- A mistake happens a second time.
- A check fails, or the owner corrects something the check missed.
- A fix is proposed for a recurring problem.
- After every run that went wrong, before the next run starts.

## When not to use

- A genuine one-off with no pattern behind it. Log it, watch for a repeat, do not rewrite the system for it yet.
- Anything the owner has not approved yet. A proposed fix is a draft until the owner approves it.

## The loop

1. **Log it.** Triggered by an error, a failed check, or the owner spotting a mistake. Each entry records: date, a problem-id slug, which system/agent, what task, expected vs actual, inputs/files/screenshot, and how bad it was. Log location: `../../docs/step-4-corrections-log-example.md`. Run `scripts/log_correction.py` to append an entry and count repeats by problem-id.
2. **Find the pattern.** Twice is a pattern. Compare expected vs actual and trace back to the missing or unclear instruction. One failure is a data point; the same failure twice is a system gap.
3. **Rewrite the system, not the model.** What gets rewritten is the skill file, the job description, the checklist, or an example — usually a short "gotcha" (the trap, and what to do instead). The agent does not retrain itself. It "learns" by updating its written instructions.
4. **Ground the fix.** A fix should be proposed by thinking, then grounded by research, documentation, a working example, or a test. Thinking alone can invent a plausible-but-wrong fix.
5. **Owner approves.** The owner approves the lesson before it becomes permanent, at least for anything important. An agent can learn the wrong lesson from one failure, or overcorrect. Human approval stops that. Never fully automatic.
6. **Test it on the next run.** Re-run the task, or a test case, clean two or three times. Test on the failing case plus old cases that used to pass, so the fix does not break what worked. If it is fixed, that automation is one step closer to reliable. If not, a human steps in.

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

- One sheet as the run log (`../../docs/step-4-corrections-log-example.md`) plus the owner list.
- One skill per recurring job, with a Gotchas section.
- After every fix: "Fix it, then add this to the skill so it never happens again."
- A short weekly review — about 20 minutes — of the log: what repeated, what got fixed, what still needs the owner.

## Scripts

- `scripts/log_correction.py` — appends a correction entry to the log and counts repeats by the structured problem-id (exact match, never substring). It prints `PATTERN` when the count reaches 2. Script code never enters context; only its output does.

## Done check

- The failure is logged with context.
- The pattern (if any) is named, or the entry is marked as a watched one-off.
- The fix is grounded, proposed as one change, approved by the owner, and tested on the next run plus old cases.
- The skill, checklist, or job description was actually updated — not just the one output.

## References

- `../../docs/step-4-corrections-log-example.md` — the run log.
- Keep an owner and last-checked list — one line per automation: what it is, who owns it, and when it was last checked.
