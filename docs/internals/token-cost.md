# Token cost — why five small skills, not one big file

Each skill costs about 100 tokens of metadata at startup (estimate) — just its name and description. Five skills is about 500 tokens (estimate).

- A skill's body loads only when a task triggers it (under 5,000 tokens, estimate). Detail lives in `references/` and loads only when read.
- Scripts never enter the conversation — only their output does. A script's code costs no tokens, no matter how long it is.
- Keep the always-on file tiny, as a pointer. Do not dump all five steps into a file that loads before every request — that would cost the full text on every turn, forever.

The figures above are estimates from the token-cost research done during the walkthrough this manual is based on. There is no source file for them, so treat them as estimates, not as a cited measurement.

The same thinking applies to enforcement: lint checks run in CI and pre-commit cost zero tokens in the conversation, because scripts run outside it and only their output enters it.
