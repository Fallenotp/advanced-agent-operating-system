# Templates

Two fill-in templates live in [`templates/`](../../templates/). Copy one, fill it in, save it under your own name. Do not edit the template in place.

## The job-description template

[`templates/job-description-template.md`](../../templates/job-description-template.md) — one page, plain English, eleven fields plus a shortcut at the top.

- **Section 00 — Found how-to (the shortcut).** Paste a step-by-step video or written guide someone else already made for this task, instead of writing the steps from scratch. Check the step list beside the original before saving it.
- **1. Role.** One line: what it is.
- **2. Mission.** One sentence: what success looks like.
- **3. Owner.** One named person. That person checks it and owns the outcome.
- **4. Responsibilities.** 3 max, each with a frequency.
- **5. Steps.** The step-by-step, in order, with the why for any step that is not obvious.
- **6. Deliverable + definition of done.** Exact format, and how the owner will know it is right. Include 1–2 examples of good output and 1 of bad, plus test examples the agent must pass before it touches real work.
- **7. Sources of truth.** Where facts come from. If it is not there, flag it — do not guess.
- **8. Tools & access.** What it can read, what it can change, what it can never touch.
- **9. Green / amber / red.** Acts alone / asks first / hands to the owner.
- **10. Schedule + report.** When it runs, and when/how it reports back for review.
- **11. Correction log.** Where fixes go, so the same mistake is never fixed twice. See [step-4-every-correction-becomes-the-system.md](step-4-every-correction-becomes-the-system.md).

A good first job is recurring, written output, checkable in under 5 minutes. Examples: drafting replies to new reviews (draft-only, owner approves), or a weekly research brief. Not anything that sends, pays, or publishes on its own.

Run [`skills/step-1-onboard-like-a-new-hire/scripts/check_job_description.py`](../../skills/step-1-onboard-like-a-new-hire/scripts/check_job_description.py) on the filled-in file — it lists any missing fields.

## The skill template

[`templates/skill-template.md`](../../templates/skill-template.md) — a blank `SKILL.md` to copy, plus five filled-in "Use when…" descriptions, one per step, in the real published pattern.

A skill is a folder with a `SKILL.md` file, plus optional `scripts/`, `references/`, and `assets/`. This is the vendor-neutral Agent Skills format: the same folder works across agents. Keep the shared frontmatter to the standard fields only.

Rules for the description: the description is the trigger. The agent only sees names + descriptions until a task matches, then it loads the body. Write it as: what it does, then "Use when..." with trigger words first. Keep it short — a few sentences — so it stays cheap to load at startup. Keep the body under 500 lines. Move detail to `references/`. Put deterministic steps in `scripts/` — script code never enters the conversation, only its output does.

Where a skill lives: master copy in `.agents/skills/<name>/SKILL.md`, linked or copied to each agent's folder as needed (for example `.claude/skills/<name>/`, `.gemini/skills/<name>/`, `.github/skills/<name>/`). Edit only the master copy.
