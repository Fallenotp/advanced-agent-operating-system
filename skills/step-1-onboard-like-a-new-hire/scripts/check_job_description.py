#!/usr/bin/env python3
"""Check a job description file for the required Step 1 fields.

Usage: python3 check_job_description.py <job-description-file> [--tier block|warn]
Parses sections, not prose: each required field must appear as a heading
("## 1. Role", "## Role") or a "Field:" line, WITH real content under it
(10+ characters of text once placeholders are removed). A heading with
nothing under it is a missing field. A file that only mentions the field
words in prose fails.

A "[ ]" in the middle of otherwise real text (for example an
instruction that says "mark done items [ ] in the tracker") is fine.
A line ENDING in "[ ]" is an unfilled slot ("Role: [ ]"), so the section
is not filled even if guidance prose sits above it — that is how a
blank template fails while a filled brief passes. An explicit
"N/A: <reason>" counts as filled.

Exit 0 on PASS, 1 on FAIL, 2 on usage error. --tier only changes the
label printed ("TIER: block|warn"); the gate decides what a failure means.
Deterministic: reads only the file given, changes nothing.
"""
import re
import sys

REQUIRED = [
    "role",
    "mission",
    "owner",
    "responsibilities",
    "steps",
    "deliverable",
    "sources of truth",
    "tools",
    "green",
    "schedule",
    "correction log",
]

PLACEHOLDER = re.compile(r"\[\s*\]")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


def _normalise(text):
    """Lowercase, drop a leading number ("1. ", "10) "), collapse spaces."""
    text = text.strip().lower()
    text = re.sub(r"^\d+[\.\)]\s*", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" :")


def _heading_matches(heading, field):
    """True if the heading is the field, or starts with it plus a
    separator ("green / amber / red" is the green field; "schedule +
    report" is the schedule field; "tools & access" is the tools field).
    A heading like "role of the payroll team" does NOT match "role" —
    the word after the field must be a separator, not more words."""
    if heading == field:
        return True
    for sep in (" /", " +", " -", " &", ":"):
        if heading.startswith(field + sep):
            return True
    return False


def _parse_sections(lines):
    """Return {field: [content lines]} for every required field found as a
    heading or a "Field:" line. Lines under a heading belong to that field
    until the next heading."""
    sections = {}
    current = None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        m = HEADING.match(line)
        if m:
            heading = _normalise(m.group(2))
            current = None
            for field in REQUIRED:
                if _heading_matches(heading, field):
                    current = field
                    sections.setdefault(field, [])
                    break
            continue
        m = re.match(r"^([A-Za-z /+&-]+?)\s*:\s*(.+)$", line)
        if m and current is None:
            name = _normalise(m.group(1))
            for field in REQUIRED:
                if _heading_matches(name, field):
                    sections.setdefault(field, []).append(m.group(2).strip())
                    current = field
                    break
            continue
        if current is not None:
            sections[current].append(line)
    return sections


def _filled(content_lines):
    """True if the section has real content: 10+ characters of text once
    "[ ]" placeholders are removed, AND no line ends with a "[ ]"
    placeholder. A line ending in "[ ]" is an unfilled slot ("Role: [ ]",
    "1. [ ] — frequency: [ ]"), so the section is not filled even if
    guidance prose sits above it — that is how a blank template fails
    while a filled brief passes. A "[ ]" in the middle of a real
    sentence ("mark done items [ ] in the tracker") is fine. "N/A:
    <reason>" counts, because the reason is real text."""
    if not content_lines:
        return False
    for line in content_lines:
        if re.search(r"\[\s*\]\s*$", line.strip()):
            return False
    text = " ".join(content_lines)
    text = PLACEHOLDER.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text) >= 10


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    tier = "block"
    for a in sys.argv[1:]:
        if a.startswith("--tier="):
            tier = a.split("=", 1)[1]
    if tier not in ("block", "warn"):
        print("Usage: python3 check_job_description.py <job-description-file> [--tier block|warn]")
        return 2
    if len(args) != 1:
        print("Usage: python3 check_job_description.py <job-description-file> [--tier block|warn]")
        return 2
    try:
        text = open(args[0], encoding="utf-8").read()
    except OSError as exc:
        print(f"FAIL: cannot read file: {exc}")
        return 1
    sections = _parse_sections(text.splitlines())
    missing = [f for f in REQUIRED if not _filled(sections.get(f, []))]
    print(f"TIER: {tier}")
    if missing:
        print("FAIL: missing or unfilled fields (a heading with no real content under it is missing):")
        for field in missing:
            print(f"  - {field}")
        return 1
    print("PASS: all required job description fields present, each with real content")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
