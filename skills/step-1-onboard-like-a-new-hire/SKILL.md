---
name: step-1-onboard-like-a-new-hire
description: Write a job description for an agent before building anything. Use when starting a new agent, handing a task to a subagent, onboarding an agent like a new hire, or when a job has no written role, quick win, or measure of success. Do the job yourself first, pick a small quick win, quantify success, and feed a found how-to video or written guide as source material.
---

# Step 1 — Onboard it like a new hire

The problem is usually not lack of context. Nobody told the agent what the job is. Write the job first, then build.

## When to use

- Starting a new agent or a new recurring job.
- Handing work to a subagent.
- A task keeps coming back wrong, or nobody can say what "good" looks like.
- You are about to build before defining the role.

## When not to use

- A one-off question with no repeatable job behind it.
- Work where the outcome cannot be described in advance — describe the decision rule instead, not a fake procedure.

## Steps

1. **Do the job yourself first.** Do one real example by hand so you know what good looks like, what bad looks like, and what to avoid. If you cannot write the bullet points, you cannot hand it off.
2. **Write the job description.** Use the fields in `references/job-description-fields.md`. Keep it to one page. Role, mission, owner, responsibilities (3 max), steps, deliverable and definition of done, sources of truth, tools and access, green / amber / red, schedule and report, correction log.
3. **Pick a quick win.** The first task should be small, recurring, written, and checkable in under 5 minutes. Stack bigger tasks only after the quick win passes.
4. **Quantify success.** One number, in advance — for example, hours saved per week, or leads per month. "You can't manage what you haven't defined."
5. **Feed a found how-to as source material.** Do not write the steps from scratch if someone already did the task well. Find a step-by-step video or a written guide with images, feed it in, and ask for the job-description fields — not a summary. See "Source-material shortcut" below.
6. **Check it with the script.** Run `scripts/check_job_description.py <job-description-file>` — it lists any missing fields. Fix the missing fields before the agent starts.

## Source-material shortcut

1. Prefer a written guide with screenshots. It is the most reliable input.
2. Otherwise use a short how-to video (under 10 minutes, or one slice of a longer one) as transcript plus screenshots/frames. Transcript alone misses what was shown but never said. A bare link alone is unreliable — some tools cannot watch a link at all.
3. Ask for the template fields: role, mission, steps in order with timestamps, deliverable and definition of done, sources of truth, what it must never do, and what to flag to the owner.
4. Read the step list beside the source before saving it as a skill. Correct it now — the skill will copy whatever the list says. Run it once while watching before trusting it with real work.
5. Add the two things no outside source can supply: the owner's boundaries (what it must never send, publish, pay, or delete without the owner) and 1–2 examples of the owner's own good output.

## What good looks like

- One agent, one written job. The job description lives in its own file, apart from any one tool, so the role travels when tools change.
- The agent can read the job description and say, without guessing: what to do, in what order, what the output looks like, where facts come from, what it must never do, and when to ask.
- A new agent can pass the test examples in the job description before it touches real work.

## Done check

- Job description exists, all fields present (script passes).
- Quick win defined and measured.
- Source material, if used, was checked beside the original.
- Then apply Step 3 (`step-3-never-take-first-look`) before handing anything over.

## References

- `references/job-description-fields.md` — the 11 fields, with what goes in each.
- `scripts/check_job_description.py` — deterministic field check. Script code never enters context; only its output does.
