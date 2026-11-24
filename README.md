# Advanced Agent Operating System

A plain-English instruction manual for managing AI agents — like a manager manages employees. Not prompting. Managing.

The most valuable skill is not writing a clever prompt. It is giving an agent a clear job, limiting what it can do, checking its work before you see it, learning from every correction, and only then letting it act on its own.

Use the five steps in order. Skipping ahead is what breaks things.

## The five steps

### 1. Onboard it like a new hire

Write the job description first. Do the job yourself first, so you know what good looks like, what bad looks like, and what to avoid.

- Pick a small quick win to start, then stack bigger tasks.
- Decide upfront how success is measured — one number, in advance. For example, hours saved per week.
- Shortcut: find a step-by-step video or a written guide with images by someone who already did the task, and feed that to the agent as the source material for the job description, instead of writing it all from scratch. Check the step list beside the original before saving it.

Skill: `skills/step-1-onboard-like-a-new-hire/`
Template: `templates/job-description-template.md`

### 2. Match the oversight to the stakes

Step 1 is hiring and training — writing the job. Step 2 is deciding how tightly you supervise it once it is working: what it can do alone, and what needs your okay.

- One agent, one job, and only the tools it needs for that job — nothing else.
- Do not rely on a prompt saying "don't send". Take the tool away instead: remove send, leave drafts. A rule in a prompt is only a suggestion; a rule in the tools is an actual restriction.
- Scale the checkpoint to the reach: the more people an action can touch, the more important the human check. If the worst case is just a bad draft, no checkpoint is needed.
- Green acts alone (low-risk, internal, reversible). Amber asks first (public or customer-facing, or anything that costs money). Red hands to the owner (pricing, legal, complaints, irreversible actions).
- Start strict — almost everything amber in the first 1–2 weeks — and loosen one action at a time as proof builds. Trust is per task, not general. Never go entirely hands-off.

A real example from the video: an agent saw an unassigned task, decided to be proactive, and sent an email that was only meant to be drafted for human review — to almost 200,000 people. A separate interview describes a similar incident — an agent sending an unintended discount code to 150,000 people — treat the exact number as uncertain, and the two tellings may not be the same incident; the point is the access mistake, not the count. Two access mistakes in one: it could see tasks not assigned to it, and it had a send button it should never have had. Neither was a prompt problem. Both were access problems.

Skill: `skills/step-2-match-oversight-to-stakes/`

### 3. Never take the first look

The agent must check its own work before you see it. First drafts land roughly 70% there; with checks they get to 95–99%. Your first look should never be the agent's first output.

**The blanket rule — never say done without evidence. Before anything is handed over:**

1. Run the check for this type of work and show what it said — the real output, screenshot, total, or source, not a summary.
2. Fix what failed, biggest first, and run the check again. At most 3 tries. If it still fails, stop and tell the owner what is left, with the evidence.
3. Say what you did NOT check, and why.
4. Never change the check to make it pass. If you think the check is wrong, say so and let the owner change it.
5. For anything a customer, client, or the public will see, or anything that moves money or data: a different agent — a fresh session that did not make the work — checks it first, and it may say "no issues".

Why the same agent cannot review its own work: it sees what it meant to make, not what is actually there — like grading its own homework. A check only works if the checker knows something the author did not: a test result, a screenshot, a recalculated total, a source document, or a fresh reviewer.

**The four checkers** — pick the one by output type. Full detail in `docs/step-3-checkers.md`:

- **Visual** (website, deck, card, PDF): screenshot every page/slide, read every word, spelling, contrast, positioning, cut-off/overlap. Click every button and link. Phone size as well as computer size. Max 3 passes.
- **Code** (app, script, website code): build + lint + typecheck + tests, paste the real output. Then run the real app end to end and drive the changed feature like a user would.
- **Data / spreadsheets**: totals must be formulas, never a number typed in by hand. Recalculate, spot-check 2–3 rows by hand against numbers you already know, reconcile the total against a trusted number, read back the computed value after recalculation.
- **Writing / docs**: pull out every number, date, name, quote, and link. Open each source and confirm it says that. Delete anything that cannot be confirmed. Read the whole thing top to bottom. Click every link.

Skill: `skills/step-3-never-take-first-look/`
Checkers: `docs/step-3-checkers.md`

### 4. Every correction becomes the system

Never fix the same problem more than twice. Once can be a one-off. The second time, funnel it into a skill.

1. **Log it.** Triggered by an error, a failed check, or the owner spotting a mistake. Each entry records: date, a problem-id slug, which system/agent, what task, expected vs actual, inputs/files/screenshot, and how bad it was.
2. **Find the pattern.** Twice is a pattern. Compare expected vs actual and trace back to the missing or unclear instruction.
3. **Rewrite the system, not the model.** What gets rewritten is the skill file, the job description, the checklist, or an example — usually a short "gotcha" (the trap, and what to do instead). The agent does not retrain itself. It "learns" by updating its written instructions.
4. **Ground the fix.** A fix should be proposed by thinking, then grounded by research, documentation, a working example, or a test. Thinking alone can invent a plausible-but-wrong fix.
5. **The owner approves.** The owner approves the lesson before it becomes permanent, at least for anything important. An agent can learn the wrong lesson from one failure, or overcorrect. Human approval stops that. Never fully automatic.
6. **Test it on the next run.** Re-run the task, or a test case, clean two or three times. Test on the failing case plus old cases that used to pass.

Separate the jobs: the thing that does the work, the thing that grades the work, and the thing that proposes the fix must be separate — generator, verifier, and coach. One change at a time.

New automations are glass balls — drop one and it shatters. They become rubber balls when three things exist: corrections stored in a skill, traces (a clear history of what the agent actually output), and notifications (the owner finds out when something errors). Underneath all of it: a named human owner for every automation.

Skill: `skills/step-4-every-correction-becomes-the-system/`
Log format and worked examples: `docs/step-4-corrections-log-example.md`

### 5. Make your AI employees proactive, not reactive

Only after Steps 1–4. Steps 1–4 get an agent to Level 4. This step is the jump to Level 5.

- **Level 4 — proposes:** "Here is the problem, here is what I think caused it, and here is the solution I think we should pick." The owner decides.
- **Level 5 — implements and informs:** "I found a problem, figured out what caused it, researched how to fix it, and I fixed it. Just wanted to keep you in the loop." The owner hears about it after.

What actually works: boring, recurring problems humans are inconsistent at — stale data (meeting notes that never made it into the wiki), a wiki with clashing information, tasks about to miss deadlines. Proactive "co-founder" agents for business vision and strategy have not worked — a human expert is still better at that.

- Three triggers: scheduled (an exact time, good for deliverables); a watcher (wakes up on a schedule, checks, and stays silent if there is nothing to say); event-driven (something happens, it reacts).
- How it decides something is a problem: a written rule against a live source, not a feeling. For example, a task due within 3 days with no owner. Check the live system, not a document about it. Use code, not the agent, for deterministic steps.
- Guardrails: anything irreversible, anything the outside world sees, or anything that touches production stays gated — a human approves it. Separate finding a problem from changing something.
- Trust climbs a ladder, per task, not in general: shadow it first (read-only, draft in chat), then propose-only (Level 4, the owner approves every proposal), then — after 2–4 clean weeks on that exact task — one narrow, reversible Level 5 action. Trust resets down if it fails, or the model/tools change, or the task is new. Always a kill switch and a named owner. Never go entirely hands-off.

**Propose-only until the owner chooses what it watches.** The recommended first agent is a Deadline and Stale-Info Watcher, Level 4, report-only, Monday and Thursday at 8am. It watches one list the owner already uses, flags anything due in the next 3 days with no owner, anything already overdue, and any meeting note from the last 7 days not in the wiki. One short message listing only what needs the owner, or nothing / "No deadlines need you" if nothing does. It never changes a date, marks anything done, or messages anyone. Do not set it up until the owner chooses which list or wiki it watches.

Skill: `skills/step-5-proactive-not-reactive/`

## How to use this repo

1. Pick ONE agent to onboard properly. Write its job description first (`templates/job-description-template.md`).
2. Give it only the tools it needs. Write down green / amber / red.
3. Give it the Step 3 check for its type of work. It does not hand anything over without evidence.
4. When a correction happens, log it (`docs/step-4-corrections-log-example.md`). Twice is a pattern — rewrite the skill, with the owner's approval.
5. Only then think about Step 5, and only for boring, recurring problems.

## Token cost — why five small skills, not one big file

- Each skill costs about 100 tokens of metadata at startup (estimate) — just its name and description. Five skills is about 500 tokens (estimate).
- A skill's body loads only when a task triggers it (under 5,000 tokens, estimate). Detail lives in `references/` and loads only when read.
- Scripts never enter the conversation — only their output does. A script's code costs no tokens, no matter how long it is.
- Keep the always-on file tiny, as a pointer. Do not dump all five steps into a file that loads before every request — that would cost the full text on every turn, forever.

## Enforcement — lint checks, not hooks

Enforcement is by checks, never by agent-side hooks. A check is a small script that looks at a file and says pass or fail. The blocking power comes from where it runs, not from the script — so the same checks run in three places: the agent runs them before it hands anything over, they run in CI on every pull request, and CI is a required status check, so a red check stops the merge.

- The skill names the exact check.
- The always-on file says: run the check after every change.
- The same check runs in CI on every change, and blocks the merge if it fails.
- A check the work can modify is a broken check. The checklist lives where the agent reads it but cannot edit it. Never let a change edit its own judge.

**The gate — `checks/gate.sh`.** One runner calls every checker and prints PASS or FAIL per check, with the file and line. Exit 0 means every BLOCK-tier check passed; exit 1 means a BLOCK check failed; exit 2 is a usage error; zero checks run is a FAIL. Run it before a handoff, or let CI run it: `bash checks/gate.sh --target .` for a whole directory, or `--job`, `--handoff`, `--review`, `--tasks`, `--log`, `--action` for one piece of work. `--self-test` runs the full negative corpus plus the override and tripwire scenarios. `--warn-only` runs new or changed checks as warnings first — use it for two weeks before promoting a check to BLOCK, and measure the false-positive rate.

**Tiers — what blocks and what warns.** Every checker prints its tier. BLOCK stops the merge; WARN shows up in the output and the run still passes.

| Check | Tier |
|---|---|
| Step 1 job description | BLOCK for new delegations, WARN otherwise |
| Step 2 prose scan | WARN, never BLOCK — it reads free text, so it trips on ordinary English |
| Step 2 tool allowlist | BLOCK |
| Step 3 handoff evidence | BLOCK for public, money, or data work; WARN for internal drafts |
| Step 3 run-checks | BLOCK where code checks apply |
| Step 4 corrections log | WARN first; BLOCK only after two weeks of clean runs |
| Step 5 watcher | WARN, never BLOCK a merge |
| Step 5 level-5 approvals | BLOCK |
| Fresh review | BLOCK for public, money, or data work; WARN otherwise |
| Changes to `checks/` or `approvals.yaml` | BLOCK, code-owner review required, never overridable |

**Why the checks read structure, not prose.** The first version of these checkers matched words in free text, and it failed both ways: it blocked good work (a filled brief failed for one `[ ]` in an example; "pay attention" and "post a summary" got flagged as high-risk actions; "Used 2 tries" failed) and it passed bad work (a nonsense brief passed; "Never forget: the agent must send the weekly report" passed; a made-up test result passed). The fix was to check structure instead — sections and fields in a job description, the tool list in Section 8, a problem-id in a log row, an approval record with a task-id and a date. A check that cannot tell good input from bad input is not a check: every checker ships with a negative corpus in `checks/tests/corpus.json` — legitimate inputs it must pass and cheating inputs it must fail — and CI runs it (`python3 checks/tests/run_corpus.py`). If a checker cannot pass its own corpus, it ships as WARN, not BLOCK.

**Overrides — the escape hatch.** When a check is wrong and the work is right, record it in `checks/overrides.yaml`: the check, the file, the reason in plain English, who reviewed it (a named human, never the agent), the date, and when it expires (7 days by default). The gate prints `OVERRIDDEN: <check> on <file> — <reason> (by <name>, expires <date>)`. An expired override, or one naming a check or file not in the run, fails the run. More than 2 overrides in one run, or more than 20% of runs in a week using an override, fails the run with "the check is wrong, fix the check" — that is the tripwire: an override used twice for the same check is a pattern, so rewrite the check. Emergency path: if CI is down, the owner merges with a recorded override ("CI unavailable, checks run locally, output attached") and attaches the local output to the pull request.

**What the gate cannot check.** No script can tell whether evidence is genuine, whether a fix is correct, or whether a brief makes sense. That is the fresh reviewer's job (Step 3). The gate proves the paperwork exists; the reviewer proves the work is real.

**Setup — the human half.** The scripts cannot protect the repo on their own. Work through `docs/setup-checklist.md` once, by hand: enable the branch ruleset on `main` (require a pull request, require the gate status check, block force pushes), turn on code-owner review so `CODEOWNERS` takes effect for `checks/`, `approvals.yaml`, and `.github/workflows/`, and confirm the workflow actually ran. Until the ruleset exists, every check here is advisory.

## What's in this repo

```
README.md                          — this manual
LICENSE                            — Creative Commons Attribution 4.0 International (CC BY 4.0)
CODEOWNERS                         — checks/, approvals.yaml, and .github/workflows/ are owned by @Fallenotp
.gitignore                         — test residue (checks/tests/.tmp/) and Python caches are never committed
approvals.yaml                     — structured Level 5 approval records (task-id, action-class, scope, approver, date, expires)
.github/workflows/checks.yml       — CI: runs the checkers on every push and pull request
checks/
  gate.sh                          — the runner: calls every checker, prints PASS/FAIL, exit 0/1/2
  gate_yaml.py                     — minimal YAML reader (no dependency) used by the checkers
  _override_check.py               — reads checks/overrides.yaml for the gate
  check_tool_allowlist.py          — Step 2 BLOCK: structured tool list + approval record
  check_review.py                  — Step 3: reviewer session differs from author, review quotes the work
  check_corrections.py             — Step 4: pattern rows prove their fix and approval
  check_level5.py                  — Step 5 BLOCK: structured Level 5 approvals
  manifest.yaml                    — which checks apply to this repo, and the tier table
  overrides.yaml                   — recorded overrides (check, file, reason, reviewed-by, date, expires)
  tests/
    corpus.json                    — negative corpus: good inputs that must pass, cheating inputs that must fail
    run_corpus.py                  — runs the corpus and reports PASS/FAIL per case
skills/
  step-1-onboard-like-a-new-hire/  — SKILL.md, references/, scripts/
  step-2-match-oversight-to-stakes/ — SKILL.md, scripts/
  step-3-never-take-first-look/    — SKILL.md, references/, scripts/
  step-4-every-correction-becomes-the-system/ — SKILL.md, scripts/
  step-5-proactive-not-reactive/   — SKILL.md, scripts/
templates/
  job-description-template.md      — fill-in agent job description
  skill-template.md                — blank SKILL.md template + five filled-in descriptions
docs/
  step-3-checkers.md               — the four checkers, in full
  step-4-corrections-log-example.md — corrections log format + two worked examples
  setup-checklist.md               — the human half: branch ruleset, code owners, tiers, overrides
```

## Sources

- **Video** — the walkthrough this manual is based on: https://www.youtube.com/watch?v=42Y6z9KKRKc
- **70% first drafts, 95–99% with checks** — the video's own figures for first drafts with and without a taught check.
- **Self-critique ~11% of errors, ~4% of claimed-but-not-done work; ground truth ~90% / ~99%; fresh independent critic ~73%** — illustrative figures from the "Reflection & Verification" chapter's simulator: https://agent.xinbetween.com/c11/ — not results from a controlled study. The direction is the point (self-critique catches little; ground truth and a fresh critic catch far more), not the decimals.
- **Over half of claimed improvements flat or worse** — Park & Choi, "When Do Agent Loops Mistake Stagnation for Progress?", arXiv:2607.25152: across 54 cycles an agent claimed improvement every time, yet 56% had a measured delta of zero or below. https://arxiv.org/abs/2607.25152
- **About 100 tokens of metadata per skill at startup, body under 5,000 tokens when triggered, scripts only output tokens** — estimates from the token-cost research done during the walkthrough. There is no source file for these figures, so treat them as estimates, not as a cited measurement.
- **The "almost 200,000 people" email story** — from the video. A separate interview describes a similar incident — an agent sending an unintended discount code to 150,000 people — treat the exact number as uncertain, and the two tellings may not be the same incident; the point is the access mistake, not the count.
- **Agent Skills as a vendor-neutral open standard** — Anthropic donated the standard to the Agentic AI Foundation (a Linux Foundation project) on October 22, 2026. Specification: https://agentskills.io — announcement: https://www.anthropic.com/news/donating-agent-skills-to-the-agentic-ai-foundation

## License

This manual is licensed under Creative Commons Attribution 4.0 International (CC BY 4.0) — see `LICENSE`. You may copy, share, and adapt it, with attribution. CC BY 4.0 was chosen because this is a written manual, not code; the owner can swap it for another license.

## What this is not

- Not a co-founder agent. Strategic decisions stay with a human expert.
- Not fully automatic learning. The owner approves every correction before it becomes permanent.
- Not a prompt pack. A prompt is not a permission layer — access and checks are.
