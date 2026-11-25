# Security policy

## Supported versions

| Version | Supported |
|---|---|
| `main` (current) | Yes |
| Any older snapshot or tag | No |

This repo is a written manual plus small check scripts. There are no releases yet; when one is cut, the current release gets fixes and older ones do not.

## Reporting a vulnerability

Do not open a public issue. Report it privately through GitHub's private vulnerability reporting on this repo, so the fix can land before the details are public. A fix merges to `main` and ships in the next release.

## What counts

A real problem here is a check that can be bypassed, a script that runs code it should not, or a doc that tells the reader to do something unsafe (for example, to run an untrusted script as a local gate). A wording preference is not a vulnerability — open a discussion for that.
