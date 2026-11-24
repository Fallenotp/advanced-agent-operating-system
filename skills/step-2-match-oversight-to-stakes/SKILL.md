---
name: step-2-match-oversight-to-stakes
description: Decide how tightly to supervise an agent once it is working. Use when an agent is about to send, post, publish, deploy, delete, pay, or touch clients, money, or live systems, or when choosing what tools an agent gets. One agent, one job, only the tools it needs. Take the tool away instead of writing a rule, and scale the checkpoint to the reach.
---

# Step 2 — Match the oversight to the stakes

Step 1 is hiring and training — writing the job. Step 2 is supervision once it is working: what it can do alone, and what needs the owner's okay.

## When to use

- An agent is about to act where a mistake would be costly: sending, posting, publishing, deploying, deleting, paying, or touching clients, money, or live systems.
- Choosing which tools an agent gets.
- An agent keeps being given a rule in words and breaking it.
- Deciding whether a human checkpoint is needed at all.

## When not to use

- Low-stakes, internal, reversible drafts where the worst case is a bad draft. No checkpoint is needed there — checking everything doubles cost and time.

## Focused agent

One agent, one job, only the tools it needs for that job — nothing else.

- Example: an agent drafting replies to reviews for your business can read the reviews and write drafts. It cannot send anything, cannot delete anything, cannot open email or social media, cannot touch the website. If it goes wrong, the worst it can do is write a bad draft.
- Contrast: a generalist agent with access to everything. If it misunderstands one instruction, it can send, post, delete, or publish in the wrong place. More tools means more ways to go wrong, harder to check, and harder to know what happened.
- Tools are decided by the owner, not the agent. Start narrow. Add one tool at a time, only after the agent proves itself on the current tools. That is how it earns a promotion.
- Trust is per task, not general. Proof on one task does not transfer to a different task.

## Take the tool away instead of writing a rule

A rule in a prompt is only a suggestion. A rule in the tools is an actual restriction.

- Do not rely on "don't send". Remove send, leave drafts.
- Do not rely on "don't deploy". Remove the deploy tool. The agent can suggest the change; the owner checks it, then the owner merges or deploys.
- Use code, not the agent, for anything deterministic — for example, "is this number greater than 10?" or "is this due in under 3 days?" Save the agent for work that needs judgement.
- Build with the least amount of agent possible. Most processes end up as a normal workflow with one small agent step in the middle.

## Green / amber / red

- **Green — acts alone:** low-risk, internal, reversible. A draft, a summary for the owner to read, a research note.
- **Amber — asks first:** public or customer-facing, or anything that costs money. Draft it, owner approves, then it goes out.
- **Red — hands to the owner:** pricing, legal, complaints, irreversible actions, anything that cannot be undone. The agent does not do it at all.
- Start strict: almost everything amber in the first 1–2 weeks. Loosen one action at a time as proof builds. Never go entirely hands-off.

## Scale the checkpoint to the reach

The more people an action can touch, the more important the human check.

- Worst case is a bad draft for one person: no checkpoint needed.
- Worst case touches many people, clients, or the public: a human checks first.
- A circuit-breaker rule works well: automate the routine cases, and send anything above a reach threshold to a human — for example, a change affecting more than a small share of users gets human review.

## Examples — your business

- Low stakes: agent drafts a follow-up summary after a session for the owner to review. No send tool. No checkpoint beyond the owner's read.
- High stakes: agent posts on social media or emails clients directly. That stays a draft until the owner approves. That is a hot zone.

## Examples — code

- Low stakes: agent writes code and opens a pull request as a draft for the owner to review.
- High stakes: agent deploys straight to the live site or pushes to the main branch without the owner. Remove the deploy tool. The agent can suggest the change; the owner checks it, then the owner clicks merge.

## Done check

- The job description lists exactly which tools the agent has, and which it does not have.
- Every green / amber / red decision is written down, not assumed.
- Run `scripts/check_tools.py <job-description-file>` — it flags high-risk actions (send, post, publish, deploy, delete, pay) listed as allowed.
- Then apply Step 3 (`step-3-never-take-first-look`) before handing anything over.

## References

- `scripts/check_tools.py` — deterministic check for high-risk tools in a job description. Script code never enters context; only its output does.
