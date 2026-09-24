---
type: Reference
id: https://knowledge-trust-ladder.example/knowledge/references/gh-skill-cli
title: gh skill (GitHub CLI)
description: The GitHub CLI command group that installs, pins, and publishes agent skills from GitHub repositories; the publish path this repository uses for releases.
genre: reference
resource: https://cli.github.com/manual/gh_skill_install
generated:
  by: process:ktl-librarian
  at: "2026-09-24T00:55:04Z"
status: draft
definedBy:
- https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
---

# Overview

Added in GitHub CLI v2.90.0. `gh skill install <repo> <skill[@version]>`
installs one named skill, or every skill a repository offers with `--all`, into a host-specific directory, at project or
user scope, with `--pin` for a tag or commit SHA; there is no cross-skill
dependency mechanism, which is why this repository documents installing each
of the four explicitly.

`gh skill publish` validates the repository's skills against the Agent Skills
specification and creates the tag and GitHub release. `--dry-run` is the
validation-only mode CI runs on every pull request; `--tag vX.Y.Z` is the
non-interactive publish the release workflow calls.
