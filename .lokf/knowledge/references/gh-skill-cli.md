---
type: Reference
id: https://knowledge-trust-ladder.example/knowledge/references/gh-skill-cli
title: gh skill (GitHub CLI)
description: The GitHub CLI command group that installs, pins, and publishes agent skills from GitHub repositories; the publish path this repository uses for releases.
genre: reference
resource: https://cli.github.com/manual/gh_skill_install
generated:
  by: process:lokf-librarian
  at: "2026-09-09T10:00:00Z"
status: draft
definedBy:
- https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
verified:
- by: process:lokf-librarian
  at: "2026-09-09T17:00:00Z"
---

# Overview

Added in GitHub CLI v2.90.0. `gh skill install <repo> <skill[@version]>`
installs one skill at a time into a host-specific directory, at project or
user scope, with `--pin` for a tag or commit SHA; there is no cross-skill
dependency mechanism, which is why this repository documents installing each
of the four explicitly.

`gh skill publish` validates the repository's skills against the Agent Skills
specification and creates the tag and GitHub release. `--dry-run` is the
validation-only mode CI runs on every pull request; `--tag vX.Y.Z` is the
non-interactive publish the release workflow calls.
