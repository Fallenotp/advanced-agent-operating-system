# Lint checks that hold

This page is the lessons-learned record for the checks in this repo: what they are, what went wrong building them, and how to think through a new one. It is written in plain words, clear enough for a 12-year-old to follow. Two numbers were updated when this page moved into the repo: the test set is 67 cases, not 61, and a pattern row's fix counts when the file changed on or after the row's date, not only after it. Everything else is word for word from the draft.

A lint check is a small script that looks at a file and answers one question. It exits 0 for pass, 1 for fail, 2 for you ran it wrong. That is all it does.

The script itself has no power. Nobody has to obey it. The power sits in where it runs.

It runs in three places. The agent runs it on its own work before handing anything over. A pre-commit hook runs it before a commit lands. A commit is a saved batch of changes, and a pre-commit hook is a small script that runs just before one is saved. CI runs it on every pull request as a required check, and a failed check blocks the merge. CI is a service that runs checks on every proposed change. A pull request is a proposal to merge a batch of changes into the main copy, and a merge is when that proposal is accepted. A local hook can be skipped. A person can pass a flag and commit anyway. CI cannot be skipped that way. That is why CI is the real gate, and the other two are backup.

Hooks are the wrong tool for this. A hook belongs to one harness. Claude Code, Codex, Gemini CLI, and OpenCode each have their own hook config, their own events, and their own rules about what can block. A hook written for one does not carry to the next. A lint check is a plain script. It runs anywhere a shell runs.

Instruction files have the opposite problem. AGENTS.md, CLAUDE.md, and GEMINI.md are read as guidance. Nothing enforces them. Gemini CLI reads only GEMINI.md. A rule written in prose is a request. A check that runs in CI is a gate. The skill carries the knowledge, the always-on file carries the instruction to run it, and CI carries the enforcement.

### Setting it up for any job

The shape is the same whatever the job is. Only the checks change.

Write the rule in the skill first, in plain words, and name the exact check. If you cannot name the check, you do not have a check yet. You have a wish.

One runner. A script called checks/gate.sh that runs every checker and prints one PASS or FAIL line per check. If zero checks ran, the runner fails. A run where nothing was checked must never report success. Our own runner learned this the hard way. An early version printed success when no checks ran at all.

One checker per question. Each checker answers one narrow question. A checker that tries to judge everything judges nothing.

Run it in three places. The agent runs it before handoff. Pre-commit runs it before a commit. CI runs it on every pull request as a required check.

Guard the checks themselves. The checks folder gets a CODEOWNERS entry naming the owner. CODEOWNERS is a file that names who must review changes to certain folders. A branch rule is a setting that says changes there need that owner's review before they can merge. An agent that can rewrite its own judge can pass itself.

Keep the exit codes honest. 0 means pass. 1 means fail. 2 means you ran it wrong.

### The checks we actually built

Step 1, check_job_description.py. It reads the job description by its headings, not by hunting for words. Each of the eleven fields must sit under its own heading, or on a Field line, with real content under it, at least ten characters once blank slots are removed. A line that ends in [ ] is an unfilled slot, so the blank template fails even though it has guidance prose under each heading. A [ ] in the middle of a real sentence is fine. A field that says N/A with a reason counts as filled.

Step 2 has two checks. The first, check_tools.py, reads the prose and warns about risky words like send, post, publish, deploy, delete, and pay. It matches exact words only, so postpone and sender do not trip it, and it only counts a ban when the ban word sits within three words of the verb. It never blocks anything. It only warns, and it always exits 0 on a finished scan. The second, check_tool_allowlist.py, is the one that blocks. It reads the structured tool list in section 8 of the brief, the lines that say Can read, Can change, and Can never touch. A risky word in Can change fails unless an approval record in approvals.yaml covers it. A risky word in Can never touch is a ban, never a failure. An approval that lives only in chat does not count.

Step 3 has three checks. verify_handoff.py reads the handoff and wants real evidence, a real not checked section, and a tries count of 3 or fewer. Evidence must be machine-checkable: a command with an exit code, a file path that exists, or a number with a unit, like 42 passed. A sentence that says the tests passed is not evidence. It accepts Used 2 tries and Tries - 1, and the last tries count in the file wins. Empty phrases like Not checked: nothing fail. A second check, check_review.py, makes sure the reviewer is not the author. It compares session ids, and it wants the review to quote the work. A review that quotes nothing only warns. The third, run_checks.sh, runs the project's own build, lint, typecheck, and test commands when they exist. A docs-only project, with no package.json or pyproject.toml, passes with a note. A test command that passes but prints no test count only warns. It runs project code, so it runs in CI or a sandbox, never on an untrusted pull request.

Step 4 has two parts. log_correction.py appends a row to the corrections log and counts earlier rows with the same problem id. Two of the same problem id prints PATTERN. A missing log file is treated as an empty log. The second, check_corrections.py, checks the log itself. A row marked as a pattern must name a file that changed on or after the row's date, and carry an approval in the form Yes, a name, and a date. A fix described only in prose fails. It starts as a warning and is promoted to a block only after clean runs.

Step 5 has two checks. watcher_check.py reads the task list and reports overdue tasks and tasks due in the next three days with no owner. One bad row no longer hides the rest. It reads lenient dates, like 23/11/2026 and 2026-2-3, and treats TBD as no owner. It only warns, never blocks a merge. The second, check_level5.py, checks that every Level 5 action has an approval record in approvals.yaml. The action file is JSON, and the action class must be one of six fixed kinds: report-only, update-wiki, update-docs, send-summary, file-issue, update-schedule. The approver must be a named human, not the agent that did the action, and the approval must not be expired. An approval in chat alone does not count.

One runner ties them together. checks/gate.sh runs every checker that has an input and prints one PASS or FAIL line per check. It reads which checks block and which only warn from checks/manifest.yaml. If zero checks ran, it fails. It reads overrides from checks/overrides.yaml and prints them, so an exception is visible in the log. The runner has its own self-test, bash checks/gate.sh --self-test, which runs the whole test set plus six scenarios. The test set lives in checks/tests/, 67 cases of good work the checks must pass and cheating work they must fail. It ran 67 passed, 0 failed, on 2026-11-25.

### Why bother

Self-critique alone catches 11% of errors, and 4% of claimed-but-not-done work. Add an independent critic and it catches 73%. Add ground truth, tests or a compiler, and it catches 90%, and 99% of claimed-but-not-done work. Those numbers come from a simulator table, not a controlled study. The source is "Reflection and Verification" at https://agent.xinbetween.com/c11/, read live on 2026-11-24.

Park and Choi ran a frontier agent through 54 cycles. It claimed improvement every time. In 56% of the cycles the measured change was zero or worse. Self-report told them nothing. The paper is at https://arxiv.org/abs/2607.25152, read live on 2026-11-24.

And there is a ceiling on what can be checked at all. The obey-cli team turns AGENTS.md rules into deterministic checkers and scores what the agent did, not what it said. In their runs only about 23% of real-world rules could be checked by a script at all. Their own checkers had 136 errors. The 23% figure comes from the lint research report. It was not re-measured here. The 136 errors are in their own write-up at https://pypi.org/project/obey-cli/, opened 2026-11-24.

The Agent Skills spec ships a format validator, and pre-commit plus CI is the established pattern. See https://agentskills.io, opened 2026-11-24.

### What round 3 found, and what changed

Round 3 tried to fool the first version of these checks, and it worked. Every failure below was found by running the actual scripts on 2026-11-24. The builder then rewrote the checks, and each example was re-run on the new scripts the same day. What follows is the history, and what each check does now.

A filled-in brief failed because one "[ ]" sat in an example sentence. The check looked for the characters anywhere in the file. Now the check reads headings and only treats a line ending in [ ] as an unfilled slot. A filled brief with [ ] in an example sentence passes. The blank template still fails, all eleven fields missing.

"Pay attention to tone" got flagged for the word "pay". Now the prose scan matches exact words only, and it only counts a ban when the ban word sits within three words of the verb. It still warns on "Pay attention to tone", and on "Never forget: the agent must send the weekly report". It warns because it reads prose, and prose cannot be checked reliably. That is why it never blocks. The check that blocks reads the structured tool list instead.

"Used 2 tries" failed because the checker only accepted three exact wordings. Now it accepts "Used 2 tries", "attempts: 2", and "Tries - 1", and the last count in the file wins.

A file with nothing but the eleven field words passed. Now the check reads headings and wants real content under each one. A file with only the field words fails.

Any evidence line of 15 characters or more passed. "Ran the tests, all passed." passed. Now evidence must be machine-checkable. A command with an exit code, a file path that exists, or a number with a unit. "Ran the tests, all passed." fails.

run_checks.sh trusted the project's own test command. A stub that always passed made the check pass. Now a test command that passes but prints no test count only warns, and a docs-only project passes with a note instead of failing for having no tests.

watcher_check.py stopped at the first task with a bad date and returned 1. One bad row hid every overdue task after it. Now it reports every task, good and bad, and reads lenient dates like 23/11/2026 and 2026-2-3.

log_correction.py counted repeats by matching the system and task words. Two different failures under the same job name counted as one pattern. Now it counts by problem id, an exact slug like video-timing-mismatch. Two rows with the same problem id print PATTERN. Three different problem ids do not.

One gap is still open, and it is open on purpose. Made-up test numbers still pass the handoff check. A typed "214 passed, 0 failed, exit 0" looks exactly like a real run to a script. The script says so in its own output. Genuineness is reviewer-checked, by a different agent re-running the check. That is the limit of what a script can settle, and it is written down, not hidden.

One more small thing. The template's own ban line, "Not anything that sends, pays, or publishes", still trips the prose scan as a warning. The ban word sits four words before the verbs, past the three-word window. Widening the window would break the "Never forget" case. It is a warning, it blocks nothing, and it is pinned as a test case so the next change to the scan has to face it.

The pattern in all of these was the same. The first checks matched text. Text is the wrong thing to match. A check should look at structure. Fields in a file, not words in a paragraph. A date read as a date, not a string that looks like one. A test result read from the test runner, not from a sentence that says the tests passed.

### Writing a check that does not block good work

Check structure, not prose. If the input is a job description, read its headings. If it is a task list, read the data file. Free text is where false alarms live.

Decide which way each check fails. A check that blocks a merge should only fail on facts a script can settle without guessing. A missing field is a fact. A word that looks risky is not. When in doubt, the check warns and a human decides.

Two severities. BLOCK and WARN. BLOCK is for things a script can settle without guessing, and where the stakes are high. A missing required field. A test that failed. WARN is for everything else. A warning never stops a merge on its own.

An override, on purpose. A file called overrides.yaml. An override names the check, the reason, who approved it, and an expiry date. Only the owner can add one. Overrides expire. And the override rate is itself watched. If overrides climb, the check is wrong, not the work.

Dry run first. A new check runs as WARN for two weeks. If it flags good work in that time, fix the check before it ever blocks anything.

A test set for the checker itself. Keep two lists. Legitimate inputs the checker must pass. Cheating inputs it must fail. Run both lists in CI with the checker. A checker with no tests is a guess.

One assertion per check. A checker that checks five things fails for five reasons, and the person reading the failure cannot tell which one mattered.

Never block on judgement. Taste, strategy, whether evidence is genuine, whether a fix is the right fix. Those are human calls. A script that tries to make them will block good work and pass bad work, both at once. That is what our checks did.

### How this page is written

This page is written to sound like one person explaining something to another person across a table. Short sentences mixed with long ones. Specifics instead of abstractions. No em dashes and no banned vocabulary.

Three repos shaped that voice, all opened 2026-11-24. kill-ai-slop at https://github.com/yetone/kill-ai-slop catalogues 33 tells of machine-made copy and design, each with a before and after rebuild, plus a skill that scans a project and strips them. humanize at https://github.com/leeshiming/humanize is two skills built from the detection literature. It works through nine levers, nine kinds of small change, like mixing short and long sentences, adding a concrete detail, and cutting hedges. It is grounded in 50 or more peer-reviewed sources, and honest about its ceiling. Static rewriting beats perplexity detectors. A perplexity detector guesses whether text is machine-made by how predictable the words are. It does not beat learned classifiers like GPTZero. A learned classifier is a program trained on examples of human and machine text, and GPTZero is one of them. write-like-a-human at https://github.com/thebpandey/write-like-a-human runs three edit passes in order, vocabulary, then structure, then texture, with a tiered banned-word list and a hard em dash ban. It never invents facts. Where a draft lacks a specific, it leaves a [bracketed placeholder] for the reader to fill in. This page follows the same rule.

### Sources for this section

The lint research report, 2026-11-23. What a lint check is, where the blocking power lives, why hooks do not carry across harnesses, why instruction files are advisory, and the gate design.

obey-cli, https://pypi.org/project/obey-cli/, opened 2026-11-24. Turns AGENTS.md rules into deterministic checkers, scores what the agent did. 2,663 sandboxed runs. 136 errors in their own checkers.

Agent Skills, https://agentskills.io, opened 2026-11-24. Progressive disclosure, format validator.

"Reflection and Verification", https://agent.xinbetween.com/c11/, opened 2026-11-24. Simulator table with the 11, 73, 90, and 99 figures. Labelled illustrative, not a controlled study.

Park and Choi, https://arxiv.org/abs/2607.25152, opened 2026-11-24. 54 cycles, 56% with a measured change of zero or below.

The video, https://www.youtube.com/watch?v=42Y6z9KKRKc. Transcript read live 2026-11-23.

The examples in this section were run against the actual scripts in this repo on 2026-11-24, after the checks were rewritten. The test set that proves them lives in checks/tests/, 67 cases, all passing.

## What we got wrong, and what we changed

This section is the story of the checks in section 12. They did not arrive working. Three rounds of review found three different kinds of failure. A different person reviewed each round. One reviewer would have missed most of it.

### Round 1: the first review found 5 problems

The first review happened before anything was uploaded. It found 5 problems.

Wrong file paths. The checks pointed at files that were not where the paths said. We fixed the paths. A check that cannot find its own files checks nothing.

A checker failed its own blank template. It was built to check filled-in briefs, but it ran on the blank one and failed it. We fixed it to run on the right file. A check must run on the thing it was built for.

Two claims had no source. We found the source for one and dropped the other. A number with no source behind it is a guess.

No sources section at all. We added one, with links. If a reader cannot open the source, the claim does not count.

The 200,000-email story was told on its own. An agent sent a draft email to almost 200,000 people because it had a send button it should never have had. A separate interview tells a similar story, an agent sending a discount code to 150,000 people. The page told only the first story, so the number looked certain. We fixed it by telling both stories side by side and saying the exact count is uncertain, and the two tellings may not be the same incident. The point was never the count. The point was the access mistake.

### Round 2: a fresh review found the missing source

A different agent reviewed the fixed files. It found the one problem that stopped the upload. The 11, 73, 90, and 99 numbers had no source anyone could open. It also found 11 more fixes.

No LICENSE file. We added one.

The page claimed the checks were enforced automatically, but there was no CI file. CI is a service that runs checks on every proposed change. We added a real CI file.

The Step 5 example in the template did not match the real skill. We replaced it with the real words.

The Step 2 checker flagged 7 out of 10 test lines that only talked about banning the actions. We taught it to tell a ban from an allowance.

The Step 1 checker passed a blank template. We made it fail a blank one.

The text said the two email stories were the same incident. That was not proven. We changed it to "a similar incident."

Two references pointed at files that did not exist in the project. We reworded them.

The Step 5 checker crashed on a task with no due date. We made it print FAIL instead of crashing.

The script that runs the tests said success when nothing ran. We made it fail when zero checks ran. Success with zero checks run is the most dangerous result a check can print, because it looks like a pass.

The handoff checker accepted empty phrases, and it missed the words "Tries used: 1". We tightened it.

The counts of how much text the model reads were stated as fact. They were estimates. We marked them as estimates.

Each change had a reason behind it. A check that passes its own blank template is not a check. A claim of enforcement with no enforcement file is a story. A crash hides the real problem. A number stated as fact when it is an estimate will be quoted as fact by the next reader.

### Round 3: someone tried to fool the checks

A third reviewer ran an adversarial review. Adversarial means the reviewer tries to break the thing on purpose. The reviewer fed the checks good work they should pass and bad work they should fail. The checks did both wrong.

A filled-in brief failed because one "[ ]" sat in an example sentence. "Pay attention to tone" got flagged for the word "pay". "Used 2 tries" failed because the checker only accepted three exact wordings. A file with nothing but the eleven field words passed. A line that said "Never forget: send the report" passed, because the checker saw the word "never" and assumed the line was a ban. Made-up test numbers passed as evidence.

The cause was the same in every case. The checks matched text. Text is the wrong thing to match. That finding is what section 12 is built on.

### One fix took two tries

The handoff checker deserved its own story, because it took two tries to fix. The first fix only partly worked. Two empty phrases still passed. The second fix did two things. It stripped the label off a line before judging it, so "Not checked: nothing" was judged on the word "nothing" alone. And it stopped reading a section when the next section started, so one section could not borrow another section's lines to look full.

Then a different agent verified it with test inputs of its own. The fix was only trusted after someone who did not write it tried to break it.

### What the three rounds add up to

Each round found a different kind of failure. Round 1 found mistakes in the files, and round 2 found claims with no proof, but round 3 found the checks themselves were wrong. No single review catches all three. That is why the reviewer changes each time, and why the person who wrote the check never gets the last word on it.

## How to think through a new check

Nothing here depends on our project folder, our file names, or one tool. The steps work for any agent system, any harness, any component. A harness is the program that runs the agent. Claude Code, Codex, Gemini, and OpenCode are four harnesses. The next one has not been built yet, and the steps still work for it. Our checks are the examples. Swap in your own file names.

Each step below has the rule, then one example from our work, then one example from a different kind of work.

Say what the check must catch, in one sentence, before writing any code. From our work, the sentence was this. "A job description is finished only when every field has real content in it." Somewhere else, a document check would say this. "A client letter is ready only when every claim in it comes from the notes." And a release step would say this. "A release is safe only when the tests passed on this exact build." If you cannot write that sentence, you do not have a check yet.

Ask what the check will actually look at. If the answer is words in a paragraph, stop. Find the structure. Look for headings, fields, a data file, an exit code, or a list of files. An exit code is the number a script returns when it finishes. Zero means pass. In our work, the Step 1 check looked for field words in the text. A file with only the field words passed. The fix is to read the headings and check that each one has content under it. Somewhere else, a document check might count words instead of checking each claim against the notes. A release check might read the words "release successful" from a log line instead of reading the exit code the release tool returned. Words can be typed. Structure has to be built.

Write the good inputs first. List five real pieces of good work the check must pass. From our work, take a filled brief with "[ ]" in an example sentence, a brief that says "Pay attention to tone," and a handoff that says "Used 2 tries." From somewhere else, take a client letter that quotes the notes word for word, and a release where a test step was skipped on purpose and the reason was written down. If you cannot list five, you do not understand the job yet.

Write the cheating inputs. A blank template is one. A file with only the field names is another, and so is a line that claims the tests passed. From our work, the nonsense brief that passed, and the made-up test numbers that passed. From somewhere else, a letter that copies the claim but drops the source, and a release log pasted from yesterday. A check that has never met a cheating input will meet one on its first real day.

Pick which way the check fails. A check can fail two ways. It can block good work. That is called a false positive. Or it can pass bad work. That is called a false negative. A blocking check should only fail on facts a script can settle without guessing. A missing field counts, and so does a test that failed. Everything else should only warn. A warning never stops a merge on its own. In our work, a missing field blocks, and a risky word only warns. Somewhere else, a missing signature blocks a client letter while an unusual phrase only warns, and a failed test blocks a release while a slow test only warns.

Build the escape hatch. An override is a written, approved exception. It lives in a file called overrides.yaml. It names the check, the reason, who approved it, and the date it expires. Only the owner can add one. Overrides expire. And the override rate is watched. If overrides climb, the check is wrong, not the work. In our work, that is the design in section 12. Somewhere else, a letter override would be signed by the owner with a date on it, and a release override would last for one release and then die.

Dry run before enforcing. A dry run means the check runs and reports, but it blocks nothing. A new check runs as a warning for two weeks. Count how often it flags good work. If it flags good work, fix the check before it ever blocks anything. In our work, that is how the new checks should have started. Somewhere else, run the document check on old letters first, and run the release check on past releases first. Two weeks of warnings is cheap. One blocked release is not.

Keep the checker tested. Two lists, kept in CI. One list holds good inputs the checker must pass. The other holds cheating inputs it must fail. Both lists run with the checker. A checker with no tests is a guess. In our work, that means test lists for check_job_description.py and the rest. Somewhere else, it means the same two lists for the letter check and the release check.

Know when to stop. If the check needs judgement, it is not a check. It is a job for a person. Taste, strategy, whether evidence is genuine, whether a fix is the right fix. A script that tries to make those calls will block good work and pass bad work, both at once. That is what our checks did. Hand those calls to a human and keep the script to facts it can measure.

---
