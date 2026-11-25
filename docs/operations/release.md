# Release

No release has been cut from this repo yet. This page describes how to cut one when the time comes, so the first release is not invented on the spot.

## What a release is here

This repo is a written manual plus small check scripts, not an app. A release is a tagged snapshot of the manual that a reader can trust as a stable copy: the README, the five skills, the gate, and the docs, all at one commit, with the checks green on that commit.

## How to cut one

1. Make sure `main` is green: the `checks` job passed on the head commit, and the gate self-test passes locally (`bash checks/gate.sh --self-test`).
2. Pick the version. Use a date tag — `2026-11-25` — not a semantic version. The manual is a document; its versions are dates.
3. Tag the commit and push the tag:
   ```sh
   git tag 2026-11-25
   git push origin 2026-11-25
   ```
4. Open a GitHub release from the tag. The release notes list what changed since the last release, in plain words, one line per change. Say what was checked: the corpus result and the self-test result, with the numbers.
5. Do not rewrite history after a release. A fix goes in the next release, not into the tag.

## What a release never does

- It never changes the license. The manual is CC BY 4.0, in `LICENSE`.
- It never ships a check that fails its own corpus. If a checker cannot pass its own corpus, it ships as WARN, not BLOCK — and a release does not promote it.
