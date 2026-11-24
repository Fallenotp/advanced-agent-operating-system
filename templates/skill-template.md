# SKILL.md Template

A skill is a folder with a `SKILL.md` file, plus optional `scripts/`, `references/`, and `assets/`. This is the vendor-neutral Agent Skills format: the same folder works across agents. Keep the shared frontmatter to the standard fields only.

Copy the blank template below, fill it in, and save it as `SKILL.md` in a folder named the same as the skill.

## Blank template — copy this

```markdown
---
name: <skill-name-lowercase-with-dashes>
description: <what it does. Use when <trigger words first — what the user says, or the situation>.>
# Optional, commented out in the shared file:
# license: <license>
# compatibility: <which agents/tools it works with>
# metadata: <extra notes>
---

# <Skill title>

<One or two sentences: what this skill is for.>

## When to use

- <situation or trigger>
- <situation or trigger>

## When not to use

- <situation where this skill does not apply>

## Steps

1. <step, in order>
2. <step, in order>
3. <step, in order>

## Verification

<How to check the work before handing it over. Name the exact check.>
<Max 3 tries. Say what was NOT checked. Never change the check to make it pass.>

## Gotchas / corrections log

- <trap, and what to do instead — added after a mistake, with the owner's approval>
- <trap, and what to do instead>
```

## Rules for the description

- The description is the trigger. The agent only sees names + descriptions until a task matches, then it loads the body.
- Write it as: what it does, then "Use when..." with trigger words first.
- Keep it short — a few sentences, what it does plus 'Use when…' — so it stays cheap to load at startup.
- Keep the body under 500 lines. Move detail to `references/`. Put deterministic steps in `scripts/` — script code never enters the conversation, only its output does.
- Sources for the figures in this repo: see `../README.md`, Sources.

## Five filled-in description examples

One per step, in the real published pattern — what it does, then "Use when..." with trigger words first.

### Step 1 — Onboarding

> Write a job description for an agent before building anything. Use when starting a new agent, handing a task to a subagent, onboarding an agent like a new hire, or when a job has no written role, quick win, or measure of success. Do the job yourself first, pick a small quick win, quantify success, and feed a found how-to video or written guide as source material.

### Step 2 — Oversight / routing

> Decide how tightly to supervise an agent once it is working. Use when an agent is about to send, post, publish, deploy, delete, pay, or touch clients, money, or live systems, or when choosing what tools an agent gets. One agent, one job, only the tools it needs. Take the tool away instead of writing a rule, and scale the checkpoint to the reach.

### Step 3 — Verify before done

> Check work before handing it over, never say done without evidence. Use when an agent finishes visual work, code, data or a spreadsheet, or writing, before the owner sees it, before a commit, merge, or anything public. Run the checker for that type of work, show real evidence, max 3 tries, say what was NOT checked, and use a fresh reviewer for public, money, or data work.

A second Step 3 description, for a verify-only skill:

> Use when someone is about to declare work done, fixed, ready or mergeable, and before a merge, pull request or handoff report.

### Step 4 — Correction becomes the system

> Turn every correction into the system so the same mistake is never fixed twice. Use when a mistake happens twice, a check fails, the owner corrects something, or a fix is proposed. Log it with context, find the pattern, rewrite the skill, checklist, or job description, ground the fix in research or a test, get the owner's approval before it becomes permanent, and test it on the next run.

Self-learning protocol for the body: the agent may update the skill itself only after a fix is validated on repeat runs, append lessons learned, update the anti-patterns, and prune stale content.

### Step 5 — Proactive

> Make an agent proactive only for boring, recurring problems. Use when considering a scheduled check, a watcher, or an event-driven agent, or when an agent proposes a fix on its own. Level 4 proposes problem, cause, and solution; Level 5 fixes it and tells you after. Only boring recurring problems, written rule against a live source, irreversible or public or production work stays gated.

## Where it lives

- Master copy: `.agents/skills/<name>/SKILL.md`
- Linked or copied to each agent's folder as needed, for example `.claude/skills/<name>/`, `.gemini/skills/<name>/`, `.github/skills/<name>/`
- Edit only the master copy.
- Enforcement is by lint checks / CI-style checks, never by hooks: the skill names the exact check, the always-on file says run it after every change, and CI runs the same check and blocks the merge if it fails.
