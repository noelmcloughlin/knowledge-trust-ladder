---
type: Policy
id: https://knowledge-trust-ladder.example/knowledge/policies/versioning
title: "Versioning policy"
description: "One repository-level semantic version covers all five skills, released together under a single tag, with patch, minor and major computed from Conventional Commits rather than hand-picked."
genre: reference
resource: docs/releasing.md
sources:
- resource: docs/releasing.md
- resource: README.md
- resource: CONTRIBUTING.md
- resource: CHANGELOG.md
- resource: docs/install.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
about:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/releasing
---

# Overview

The version is `vMAJOR.MINOR.PATCH`, and nobody picks it. `docs/releasing.md` gives the rule: commits typed with Conventional Commits decide the bump. `feat:` is minor. `fix:` and `security:` are patch. A `BREAKING CHANGE:` footer, or `!` after the type, is major. `docs:`, `chore:`, `refactor:`, `style:`, `test:` and `ci:` release nothing: the change merges, and its changelog entries ship with the next release that does.

# One tag for every skill

All five skills ship together under one tag rather than versioning independently, so a set pinned to one tag agrees with itself. `docs/install.md` says to pin them to the same tag, as `ktl-docent@v0.16.0` or `--pin v0.16.0`. Tags carry the `v`; changelog headings never do. `CHANGELOG.md` is the one release note, in Keep a Changelog form, and its top released heading is the current version.

# What counts as a release

Type the commit for what the change is. A behaviour change is a `feat:` even when most of the diff is prose. When a pull request should release, its title carries the releasing type too, because a squash merge takes its subject from the title. A change that alters what a skill does gets a line under `## [Unreleased]`; the `plan` job refuses a releasing pull request with an empty section.

# Supported versions

`SECURITY.md` says that only the latest published tag receives fixes, and that a security fix ships as a patch release noted in the changelog.
