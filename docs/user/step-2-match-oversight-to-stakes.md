# Step 2 — Match the oversight to the stakes

Step 1 is hiring and training — writing the job. Step 2 is deciding how tightly you supervise it once it is working: what it can do alone, and what needs your okay.

## One agent, one job, only the tools it needs

- One agent, one job, and only the tools it needs for that job — nothing else.
- Do not rely on a prompt saying "don't send". Take the tool away instead: remove send, leave drafts. A rule in a prompt is only a suggestion; a rule in the tools is an actual restriction.
- Scale the checkpoint to the reach: the more people an action can touch, the more important the human check. If the worst case is just a bad draft, no checkpoint is needed.
- Green acts alone (low-risk, internal, reversible). Amber asks first (public or customer-facing, or anything that costs money). Red hands to the owner (pricing, legal, complaints, irreversible actions).
- Start strict — almost everything amber in the first 1–2 weeks — and loosen one action at a time as proof builds. Trust is per task, not general. Never go entirely hands-off.

A real example from the video walkthrough this manual is based on: an agent saw an unassigned task, decided to be proactive, and sent an email that was only meant to be drafted for human review — to almost 200,000 people. A separate interview describes a similar incident — an agent sending an unintended discount code to 150,000 people — treat the exact number as uncertain, and the two tellings may not be the same incident; the point is the access mistake, not the count. Two access mistakes in one: it could see tasks not assigned to it, and it had a send button it should never have had. Neither was a prompt problem. Both were access problems.

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

## Take the tool away instead of writing a rule

- Do not rely on "don't send". Remove send, leave drafts.
- Do not rely on "don't deploy". Remove the deploy tool. The agent can suggest the change; the owner checks it, then the owner merges or deploys.
- Use code, not the agent, for anything deterministic — for example, "is this number greater than 10?" or "is this due in under 3 days?" Save the agent for work that needs judgement.
- Build with the least amount of agent possible. Most processes end up as a normal workflow with one small agent step in the middle.

## Done check

- The job description lists exactly which tools the agent has, and which it does not have.
- Every green / amber / red decision is written down, not assumed.
- Run `../../skills/step-2-match-oversight-to-stakes/scripts/check_tools.py <job-description-file>` — it flags high-risk actions (send, post, publish, deploy, delete, pay) listed as allowed.
- Then apply Step 3 ([step-3-never-take-first-look.md](step-3-never-take-first-look.md)) before handing anything over.

## The skill

[`skills/step-2-match-oversight-to-stakes/`](../../skills/step-2-match-oversight-to-stakes/) — `SKILL.md`, `scripts/check_tools.py`.
