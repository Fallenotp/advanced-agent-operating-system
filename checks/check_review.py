#!/usr/bin/env python3
"""Step 3 review check: the reviewer must not be the author, and the
review must quote the work.

Usage: python3 check_review.py <review-file> --author-session=ID
       --reviewer-session=ID [--tier=block|warn]

Two checks:
1. Reviewer session id differs from author session id. Comparing names
   is not enough — the same person with two names passes, and an agent
   "reviewing itself" in a fresh session of the same model passes
   mechanically. The session id is what proves a different session did
   the review. Equal sessions FAIL (BLOCK tier) or WARN (WARN tier).
2. The review must quote specific parts of the output: a markdown
   blockquote line ("> ...") or a quoted passage of 10+ characters.
   A review with no quotes is WARN — it may be a rubber stamp, and the
   gate cannot tell. This is necessary but not sufficient: a quote
   proves the reviewer looked at the words, not that the review is
   independent. That limit is stated in the output, not hidden.

Exit 0 when nothing BLOCK-tier fails, 1 on a BLOCK failure, 2 on usage
error. Deterministic: reads only the file given, changes nothing.
"""
import re
import sys

QUOTE_LINE = re.compile(r"^\s*>\s*(.{10,})\s*$")
QUOTED_TEXT = re.compile(r'"([^"]{10,})"')


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    author = reviewer = None
    tier = "block"
    for a in sys.argv[1:]:
        if a.startswith("--author-session="):
            author = a.split("=", 1)[1]
        elif a.startswith("--reviewer-session="):
            reviewer = a.split("=", 1)[1]
        elif a.startswith("--tier="):
            tier = a.split("=", 1)[1]
    if tier not in ("block", "warn") or len(args) != 1 or not author or not reviewer:
        print("Usage: python3 check_review.py <review-file> --author-session=ID --reviewer-session=ID [--tier=block|warn]")
        return 2
    try:
        text = open(args[0], encoding="utf-8").read()
    except OSError as exc:
        print(f"FAIL: cannot read file: {exc}")
        return 1
    print(f"TIER: {tier}")
    ok = True
    if author == reviewer:
        message = "reviewer session is the same as the author session — a different session must review the work"
        if tier == "block":
            print(f"FAIL: {message}")
            ok = False
        else:
            print(f"WARN: {message}")
    else:
        print("PASS: reviewer session differs from author session")
    quotes = []
    for line in text.splitlines():
        m = QUOTE_LINE.match(line)
        if m:
            quotes.append(m.group(1))
    quotes += QUOTED_TEXT.findall(text)
    if quotes:
        print(f"PASS: review quotes the work ({len(quotes)} quoted passage(s))")
    else:
        print("WARN: review quotes nothing from the work — a review with no quotes may be a rubber stamp")
    print("NOTE: a quote proves the reviewer looked at the words. It does not prove independence — a fresh session of the same model is still the same reasoning in a new context. That limit stays with the human.")
    if not text.strip():
        print("FAIL: review file is empty")
        ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
