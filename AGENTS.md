# AGENTS.md

This repo is a plain-English instruction manual for managing AI agents like employees: five skills, two templates, and lint checks that enforce them. The manual is the product. The scripts are the enforcement.

## What this repo protects

1. **The manual stays true.** Every number, date, name, quote, and link in a doc must come from a source that was opened. A claim that cannot be confirmed is deleted, not softened.
2. **The gate stays honest.** The checks in `checks/` are the judge. A change must never edit its own judge, and a checker that cannot pass its own corpus ships as WARN, not BLOCK.
3. **The skills stay small.** One skill is one job. Detail lives in `references/`, deterministic steps live in `scripts/`. The always-on files stay short pointers.
4. **The owner stays in charge.** Corrections become permanent only with the owner's approval. Level 5 actions need a written approval in `approvals.yaml`. Nothing here is fully automatic.

## The five steps, and the enforcement

The manual has five steps, in order. Step 1 writes the job. Step 2 limits the tools. Step 3 checks the work before the owner sees it. Step 4 turns every correction into the system. Step 5 lets the agent act alone — last, and only for boring, recurring problems.

Enforcement is by lint checks, never by agent-side hooks. The skill names the exact check, this file says to run it after every change, and CI runs the same check and blocks the merge if it fails. The gate is `checks/gate.sh` — one runner that calls every checker and prints PASS or FAIL per check. Run it before any handoff:

```sh
bash checks/gate.sh --target=.
bash checks/gate.sh --self-test   # corpus + override and tripwire scenarios
python3 checks/tests/run_corpus.py
```

The tiers live in `checks/manifest.yaml`. BLOCK stops the merge; WARN prints and the run still passes. `checks/`, `approvals.yaml`, and `.github/workflows/` are owned by `@Fallenotp` (`CODEOWNERS`) — a change there needs the owner's review, and the branch ruleset must require it (see `docs/operations/setup-checklist.md`).

## The always-on gate — never say done without evidence

Before anything is handed over:

1. Run the check for this type of work and show what it said — the real output, screenshot, total, or source, not a summary. For visual work, the evidence is the rendered image itself, looked at as a picture: reading an SVG or XML source is not a visual check.
2. Fix what failed, biggest first, and run the check again. At most 3 tries. If it still fails, mark the affected job BLOCKED and report the remaining faults and evidence to the orchestrator.
3. Say what you did NOT check, and why.
4. Never change the check to make it pass. If you think the check is wrong, say so and let the owner change it.
5. For anything a customer, client, or the public will see, or anything that moves money or data: a different agent — a fresh session that did not make the work — checks it first, and it may say "no issues".

Pick the checker by output type — the four checkers are in `docs/user/step-3-never-take-first-look.md`.

## Glossary

- **you** — the agent working in this repo. **we** — the maintainers. **user** — the person reading the manual. **owner** — the person who owns the outcome and approves corrections (`@Fallenotp` here).
- **agent** — the AI doing the work. **harness** — the program that runs the agent (Claude Code, Codex, Gemini, OpenCode, and the ones not built yet). This repo is harness-agnostic: skills and scripts are plain files.
- **skill** — a folder with a `SKILL.md` plus optional `scripts/` and `references/`, in the vendor-neutral Agent Skills format.
- **check** — a small script that answers one question about a file, exit 0 for pass, 1 for fail, 2 for usage error.
- **gate** — `checks/gate.sh`, the runner that calls every checker.
- **tier** — BLOCK or WARN, read from `checks/manifest.yaml`.
- **override** — a written, owner-approved exception in `checks/overrides.yaml`, with an expiry date.
- **corpus** — `checks/tests/corpus.json`: good inputs a checker must pass and cheating inputs it must fail.

## Design stance

We like plain words, short sentences, and checks that look at structure — headings, fields, dates, exit codes — not at prose. A check that matches words will block good work and pass bad work, both at once. That is what the first version of these checks did; the story is in `docs/internals/lint-checks-that-hold.md`.

## Development discipline

- One underlying problem per pull request. Provide evidence for the changed behaviour — a checkbox or "tests pass" alone does not show that the change works.
- Run the gate before opening a pull request. Paste the real output.
- Do not document every feature, enumerate fields, or narrate control flow. Write the task guide a reader needs, nothing more.
- Update the docs when a file moves. Every link in the README must open a file that exists.
- Never edit `checks/` to make a failing check pass. If the check is wrong, fix the check — and prove it with the corpus.
- Corrections go in the log (`docs/user/step-4-every-correction-becomes-the-system.md`). Twice is a pattern: rewrite the skill, with the owner's approval.
- Never put real user data in a screenshot, an example, or a fixture. The one app-style visual in the README is a diagram, not a screenshot of real work.
