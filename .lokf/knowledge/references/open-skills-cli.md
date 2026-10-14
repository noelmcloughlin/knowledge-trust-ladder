---
type: Reference
id: https://w3id.org/ktl/knowledge/references/open-skills-cli
title: Open Skills CLI (npx skills)
description: The vendor-neutral installer for agent skills, `npx skills add`, which takes a local path as its source, so this repository uses it as a pre-publication install check.
genre: reference
resource: https://github.com/vercel-labs/skills
generated:
  by: process:ktl-librarian
  at: "2026-10-12T16:08:20Z"
status: draft
definedBy:
- https://w3id.org/ktl/knowledge/references/agent-skills-specification
verified:
- by: process:ktl-librarian
  at: "2026-10-12T03:11:32Z"
---

# Overview

`npx skills add <source> --skill <name> ...` installs selected skills into whichever agent directories a repository uses, and accepts a **local path** as the source. That makes it usable as a pre-publication check.

That local-source support is why `scripts/smoke-test-install.sh` can exercise the real install path in CI against the checked-out branch, in a throwaway consumer repository, before any change reaches a published release.
