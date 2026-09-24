---
type: Reference
id: https://knowledge-trust-ladder.example/knowledge/references/open-skills-cli
title: Open Skills CLI (npx skills)
description: The vendor-neutral installer for agent skills, supporting GitHub, git, and local sources with repeatable --skill and --agent selection.
genre: reference
resource: https://github.com/vercel-labs/skills
generated:
  by: process:ktl-librarian
  at: "2026-09-09T10:00:00Z"
status: draft
definedBy:
- https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
verified:
- by: process:ktl-librarian
  at: "2026-09-24T01:25:00Z"
---

# Overview

`npx skills add <source> --skill <name> ...` installs selected skills into
whichever agent directories a repository uses, and accepts a **local path** as
the source - which is what makes it usable as a pre-publication check.

That local-source support is why `scripts/smoke-test-install.sh` can exercise
the real install path in CI against the checked-out branch, in a throwaway
consumer repository, before any change reaches a published release.
