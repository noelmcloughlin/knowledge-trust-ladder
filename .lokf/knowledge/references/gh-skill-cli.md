---
type: Reference
id: https://knowledge-trust-ladder.example/knowledge/references/gh-skill-cli
title: gh skill (GitHub CLI)
description: The GitHub CLI command group that installs, pins, and publishes agent skills from GitHub repositories; the publish path this repository uses for releases.
genre: reference
resource: https://cli.github.com/manual/gh_skill_install
generated:
  by: process:ktl-librarian
  at: "2026-10-03T01:25:58Z"
status: draft
definedBy:
- https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
sources:
- resource: https://cli.github.com/manual/gh_skill_install
- resource: https://cli.github.com/manual/gh_skill
- resource: https://github.com/cli/cli/releases/tag/v2.90.0
---

# Overview

`gh skill install <repo> <skill[@version]>` installs one named skill from a GitHub repository or, with `--from-local`, from a local directory, or every skill a repository offers with `--all`, into a host-specific directory at project or user scope, with `--pin` for a tag or commit SHA. The command group arrived in GitHub CLI v2.90.0, whose release notes call it a public preview, and the manual says it is subject to change without notice.

`gh skill publish` validates the repository's skills against the Agent Skills
specification and creates the tag and GitHub release. `--dry-run` is the
validation-only mode CI runs on every pull request; `--tag vX.Y.Z` is the
non-interactive publish the release workflow calls.
