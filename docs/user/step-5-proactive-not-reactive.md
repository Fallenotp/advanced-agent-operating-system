# Step 5 — Make your AI employees proactive, not reactive

Only after Steps 1–4. Steps 1–4 get an agent to Level 4. This step is the jump to Level 5.

## Levels

- **Level 4 — proposes:** "Here is the problem, here is what I think caused it, and here is the solution I think we should pick." The owner decides.
- **Level 5 — implements and informs:** "I found a problem, figured out what caused it, researched how to fix it, and I fixed it. Just wanted to keep you in the loop." The owner hears about it after.

## What actually works

Boring, recurring problems humans are inconsistent at:

- Stale data — meeting notes that never made it into the wiki.
- A wiki with clashing information — two passages that contradict each other.
- Tasks about to miss deadlines.

Proactive "co-founder" agents for business vision and strategy have not worked — a human expert is still better at that.

## Three triggers

1. **Scheduled** — an exact time, good for deliverables.
2. **Watcher** — wakes up on a schedule, checks, and stays silent if there is nothing to say.
3. **Event-driven** — something happens, it reacts.

## How it decides something is a problem

A written rule against a live source, not a feeling. For example: a task due within 3 days with no owner, or two wiki passages that contradict each other. Check the live system, not a document about it. Use code, not the agent, for deterministic steps ("is this due in under 3 days?").

Separate finding a problem from changing something. Reporting a wiki conflict is one decision; rewriting the wiki is a second one.

## Guardrails

- Irreversible, externally visible, or production work stays gated — a human approves it.
- Positive evidence of a problem is required. Never act on the absence of a success signal alone.
- Re-check the live source on every run. Do not act on stale information.
- Stay silent when there is nothing to say. Too many false alarms and the owner stops reading — that is crying wolf.

## Trust ladder — per task, not in general

1. **Shadow** — read-only, draft in chat, owner watches.
2. **Propose-only (Level 4)** — owner approves every proposal.
3. **One narrow, reversible Level 5 action** — only after 2–4 clean weeks on that exact task.

Trust resets down if it fails, or the model or tools change, or the task is new. Always a kill switch and a named owner. Never go entirely hands-off.

## Where a workflow lives

A workflow is handed over in four places, not in a chat prompt:

1. The job description (the brief).
2. The always-on file — short facts, not procedures (for example, an AGENTS.md file in your own project).
3. The skill file (SKILL.md — the repeatable playbook, where Step 4 corrections live).
4. The scheduled-task prompt (the trigger plus pass conditions for one recurring job).

## Which agent or model

- Single-purpose beats generalist for a first proactive job — one job, narrow tools.
- A manager with subagents only helps when the work genuinely splits into parallel pieces.
- Think in tiers, not names: cheap and fast for routine watching and triage, strong reasoning for the judgement call. The workflow, tools, and checks matter more than which model is picked.

## Recommended first agent — NOT set up yet

A weekly Deadline and Stale-Info Watcher, Level 4, report-only:

- Runs Monday and Thursday at 8am.
- Watches one list the owner already uses. Flags anything due in the next 3 days with no owner, anything already overdue, and any meeting note from the last 7 days not in the wiki.
- One short message listing only what needs the owner — or nothing, or "No deadlines need you", if nothing does.
- It never changes a date, marks anything done, or messages anyone.

**Do not set this up yet.** It needs the owner to choose which list or wiki it watches. That choice has not been made.

Test plan once it is chosen: run it by hand for a week, review every report for two weeks, keep it report-only for 2–4 clean weeks before even thinking about one reversible Level 5 action. Judge it on: zero missed deadlines in 4 weeks, no more than one false alarm per week. Owner: the owner.

## Done check

- The problem is boring, recurring, and written as a rule against a live source.
- The trigger, the guardrails, the trust level, the kill switch, and the owner are all written down.
- The agent is at the trust level it has actually earned on that exact task — not higher.
- If the owner has not chosen what it watches, nothing is set up. That is the correct state.

## The skill

[`skills/step-5-proactive-not-reactive/`](../../skills/step-5-proactive-not-reactive/) — `SKILL.md`, `scripts/watcher_check.py`.
