# Docs

Start here, in order. The five steps depend on each other — skipping ahead is what breaks things.

1. Pick ONE agent to onboard properly. Write its job description first ([templates/job-description-template.md](../templates/job-description-template.md)).
2. Give it only the tools it needs. Write down green / amber / red.
3. Give it the Step 3 check for its type of work. It does not hand anything over without evidence.
4. When a correction happens, log it ([step-4-every-correction-becomes-the-system.md](user/step-4-every-correction-becomes-the-system.md)). Twice is a pattern — rewrite the skill, with the owner's approval.
5. Only then think about Step 5, and only for boring, recurring problems.

## Using this manual

- [step-1-onboard-like-a-new-hire.md](user/step-1-onboard-like-a-new-hire.md) — write the job first
- [step-2-match-oversight-to-stakes.md](user/step-2-match-oversight-to-stakes.md) — decide what it may touch
- [step-3-never-take-first-look.md](user/step-3-never-take-first-look.md) — check its work before you see it
- [step-4-every-correction-becomes-the-system.md](user/step-4-every-correction-becomes-the-system.md) — log a correction, rewrite the skill
- [step-5-proactive-not-reactive.md](user/step-5-proactive-not-reactive.md) — let it act on its own, last
- [templates.md](user/templates.md) — the two fill-in templates

## How it is built

- [gate-checkers.md](internals/gate-checkers.md) — how the gate checkers work, tiers, overrides, what the gate cannot check
- [lint-checks-that-hold.md](internals/lint-checks-that-hold.md) — the lint checks, and what we got wrong building them
- [token-cost.md](internals/token-cost.md) — why five small skills, not one big file

## Running it

- [setup-checklist.md](operations/setup-checklist.md) — the human half: branch ruleset, code owners, tiers, overrides
- [merging.md](operations/merging.md) — how changes land on `main`
- [release.md](operations/release.md) — how to cut a release (none cut yet)

## What this is not

- Not a co-founder agent. Strategic decisions stay with a human expert.
- Not fully automatic learning. The owner approves every correction before it becomes permanent.
- Not a prompt pack. A prompt is not a permission layer — access and checks are.

## Sources

- **Video** — the walkthrough this manual is based on: https://www.youtube.com/watch?v=42Y6z9KKRKc
- **70% first drafts, 95–99% with checks** — the video's own figures for first drafts with and without a taught check.
- **Self-critique ~11% of errors, ~4% of claimed-but-not-done work; ground truth ~90% / ~99%; fresh independent critic ~73%** — illustrative figures from the "Reflection & Verification" chapter's simulator: https://agent.xinbetween.com/c11/ — not results from a controlled study. The direction is the point (self-critique catches little; ground truth and a fresh critic catch far more), not the decimals.
- **Over half of claimed improvements flat or worse** — Park & Choi, "When Do Agent Loops Mistake Stagnation for Progress?", arXiv:2607.25152: across 54 cycles an agent claimed improvement every time, yet 56% had a measured delta of zero or below. https://arxiv.org/abs/2607.25152
- **About 100 tokens of metadata per skill at startup, body under 5,000 tokens when triggered, scripts only output tokens** — estimates from the token-cost research done during the walkthrough. There is no source file for these figures, so treat them as estimates, not as a cited measurement.
- **The "almost 200,000 people" email story** — from the video. A separate interview describes a similar incident — an agent sending an unintended discount code to 150,000 people — treat the exact number as uncertain, and the two tellings may not be the same incident; the point is the access mistake, not the count.
- **Agent Skills as a vendor-neutral open standard** — Anthropic donated the standard to the Agentic AI Foundation (a Linux Foundation project) on October 22, 2026. Specification: https://agentskills.io — announcement: https://www.anthropic.com/news/donating-agent-skills-to-the-agentic-ai-foundation
