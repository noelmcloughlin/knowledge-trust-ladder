---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/why-a-distribution-repository
title: "Why the skills live in their own repository"
description: "Why the five skills are published from one installable repository with three install routes, one tag for all of them and one changelog, and why this repository also keeps a bundle of its own."
genre: explanation
resource: README.md
sources:
- resource: README.md
- resource: docs/install.md
- resource: .claude-plugin/marketplace.json
- resource: docs/m365.md
- resource: docs/releasing.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
references:
  - https://knowledge-trust-ladder.example/knowledge/references/gh-skill-cli
  - https://knowledge-trust-ladder.example/knowledge/references/open-skills-cli
  - https://knowledge-trust-ladder.example/knowledge/policies/versioning
  - https://knowledge-trust-ladder.example/knowledge/playbooks/docent-in-m365-copilot
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/releasing
---

# Overview

`knowledge-trust-ladder` packages and distributes the skills. The sidecar's `references/portability.md` calls it the sole, canonical source of the skills, and says to install from it with `gh skill install` or `npx skills add` rather than by copying files.

# Three ways in, one tag

`docs/install.md` gives three install routes: the GitHub CLI's `gh skill install`, the Open Skills CLI's `npx skills add`, and a Claude Code plugin through `/plugin marketplace add`. All five skills release together under one tag, so a set pinned to one tag agrees with itself, and `CHANGELOG.md` is the one release note. Microsoft 365 Copilot gets the docent as a zip each release carries.

Each skill stands alone, and the README says the sidecar plus the librarian is enough to see the idea. The curator is added once there is a bundle worth trusting, the docent goes anywhere an agent only reads one, and `ktl-prose` is optional.

# Why the repository is a consumer too

The repository runs its own skills on itself. Its `.lokf/` sidecar is laid down from the same templates it ships, the check named check 11 holds each host copy byte-identical to its template, and this bundle is derived from the repository's own README, docs and skill pages. The scheduled librarian workflow and the registrar gate run here as in any consumer. So a change to a template is exercised here before it reaches the sibling repositories through `scripts/sync-sidecar.sh`.

# Why not spread the skills across the siblings

The README names two Obsidian plugins, KTL Registrar and KTL Curator, as optional companions for a desk with no continuous integration. They are separate repositories because they are TypeScript plugins with their own release convention, bare `X.Y.Z` tags and draft releases. They carry copies of the sidecar's templates and a pin to one release of the skills, and `docs/releasing.md` says the copies and the pin must move together, from one tag. Keeping the skills in one repository is what makes that pin meaningful.
