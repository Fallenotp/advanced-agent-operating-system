#!/usr/bin/env python3
"""Check a job description for high-risk tools listed as allowed (WARN tripwire).

Usage: python3 check_tools.py <job-description-file>
Prints any high-risk action (send, post, publish, deploy, delete, pay)
mentioned as something the agent MAY do, so a human can confirm it is
meant to be allowed and at which level (green / amber / red).

This is a WARN-tier tripwire, never a BLOCK. It reads prose, and prose
cannot be checked reliably: synonyms ("email", "push", "remove") bypass
it, and ordinary English trips it. The BLOCK-tier Step 2 check is
checks/check_tool_allowlist.py, which reads the structured Section 8 tool
list ("Can change:" / "Can never touch:") instead of prose.

Rules, from the failures found when this checker was tested against
adversarial input:
- Exact words only: "post" must not match "postpone", "send" must not
  match "sender", "deploy" must not match "deployment", and past-tense
  reports ("was deleted", "was published") must not match. Only the base
  word and its present-tense "-s" form are matched.
- Negation is per sentence, and the negator must sit right before the
  verb (within 3 words): "must never send" is a ban; "Never forget: the
  agent must send the weekly report" is an allowance, because "never"
  belongs to "forget", not to "send".
- No catch-all regexes. The old "not ... that" / "no ... that" patterns
  exempted any line containing those words, so one stray "not" hid a real
  allowance. Only the explicit ban phrases below count.

Exit 0 always on a completed scan (a WARN is not a failure); exit 1 only
on usage or file errors. Deterministic: reads only the file given,
changes nothing.
"""
import re
import sys

# Base word -> forms matched (base + present-tense "-s" form only).
HIGH_RISK = {
    "send": ["send", "sends"],
    "post": ["post", "posts"],
    "publish": ["publish", "publishes"],
    "deploy": ["deploy", "deploys"],
    "delete": ["delete", "deletes"],
    "pay": ["pay", "pays"],
}

# Words that, within 3 words before the verb, make it a ban, not an
# allowance. Each must sit next to the verb — "never" five words away
# ("Never forget: the agent must send ...") does not count.
NEGATORS = {
    "never", "not", "n't", "no", "cannot", "can't", "mustn't", "shouldn't",
    "wouldn't", "couldn't", "won't", "don't", "forbidden", "barred",
    "prohibited", "disallowed",
}

SENTENCE_SPLIT = re.compile(r"[.!?;]\s+|\n")


def _sentences(text):
    """Split text into sentences. One line can hold several sentences, and
    a ban in one must not exempt an allowance in another."""
    out = []
    for chunk in SENTENCE_SPLIT.split(text):
        chunk = chunk.strip()
        if chunk:
            out.append(chunk)
    return out


def _words(sentence):
    """Words in a sentence, lowercased, keeping n't as its own token."""
    sentence = sentence.lower().replace("n't", " n't")
    return re.findall(r"[a-z]+", sentence)


def _flagged(sentence):
    """Return the list of high-risk base words used as allowances in this
    sentence. A verb counts as an allowance unless a negator sits within
    the 3 words right before it."""
    words = _words(sentence)
    found = []
    for base, forms in HIGH_RISK.items():
        for i, word in enumerate(words):
            if word not in forms:
                continue
            before = words[max(0, i - 3):i]
            if any(w in NEGATORS for w in before):
                continue
            found.append(base)
    return found


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 check_tools.py <job-description-file>")
        return 2
    try:
        text = open(sys.argv[1], encoding="utf-8").read()
    except OSError as exc:
        print(f"FAIL: cannot read file: {exc}")
        return 1
    lines = text.splitlines()
    found = []
    for sentence in _sentences(text):
        for word in _flagged(sentence):
            # Line number of the sentence, for the report.
            pos = text.find(sentence[:40])
            line_no = text[:pos].count("\n") + 1 if pos >= 0 else 0
            found.append((word, line_no))
    print("TIER: warn — this prose scan is a tripwire, never a block")
    if not found:
        print("PASS: no high-risk tools listed as allowed")
        return 0
    print("WARN: high-risk actions mentioned as allowed — a human confirms each is intended, and at which level:")
    for word, line in sorted(set(found)):
        print(f"  - {word} (line {line})")
    print("NOTE: synonyms (email, push, remove, charge, share, upload) bypass this scan. The structured allowlist check (checks/check_tool_allowlist.py) is the one that blocks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
