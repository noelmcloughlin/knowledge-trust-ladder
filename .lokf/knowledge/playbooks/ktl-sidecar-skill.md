---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-sidecar-skill
title: ktl-sidecar skill
description: Procedure that creates a .lokf/ sidecar - tooling, docs, a dummy skeleton, and the knowledge_bundle doorway link beside it - from bundled templates, or repairs a single missing sidecar file, then hands off to ktl-librarian.
genre: how-to
resource: skills/ktl-sidecar/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-09-17T17:30:00Z"
status: draft
about:
  - https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
definedBy:
- https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
references:
  - https://knowledge-trust-ladder.example/knowledge/references/lokf-toolkit
verified:
- by: process:ktl-librarian
  at: "2026-09-17T17:30:00Z"
---

# Overview

Runs **once** per repository, or to repair a single missing sidecar file;
it never authors concepts. Six steps: run the preflight and gather the host project's facts (Step 0;
the preflight says what the machine can do, and the layout is the same on
every host - `.lokf/knowledge` is the real folder, see
[Hosts and doorways](../explanation/hosts-and-doorways.md)), copy each file
from `templates/` and substitute placeholders (Step 1, since 2026-09-17
including `.lokf/.gitattributes`, which keeps the bundle on LF), add three
root-level pointers - `llms.txt`, a README aside, and a `knowledge_bundle`
symlink onto `.lokf/knowledge` for people, folder pickers and Obsidian
(Step 2, see [Open the knowledge bundle in Obsidian](open-bundle-in-obsidian.md)) - verify
no placeholder survives (Step 3), validate (Step 4), optionally lay down the
CI automation (Step 5: two workflows and six scripts - the conventions
script's Python half among them, since the `.sh` fails without it - of
which the preflight, the forge-free provenance gate and, since 2026-09-23,
the feedback recorder need neither git nor GitHub to be laid down), and hand off (Step 6). Its frontmatter declares what it
needs in the Agent Skills `compatibility` field, as every skill here does.

Its detail lives in three reference files - `references/portability.md` (a
matrix, host by host: git or none, GitHub, GitLab or Forgejo, Linux, macOS,
Windows and PowerShell, synced folders, an Obsidian vault, and the
forge-free gate, which verifies GPG keys with their subkeys and SSH keys
alike against `.lokf/curators/<id>.asc` or `.pub`), `references/automation.md`
(what the Step 5 files do) and, since 2026-09-17, `references/prerequisites.md`
(each preflight line in plain words: what it means, what it stops, who fixes
it and what to send them, for a person who cannot act on it themselves; the
contract holds it to every line the preflight can print) - so the router
itself stays small. Every file it writes
is copied from `templates/`, never retyped, which is what keeps a freshly
laid-down bundle byte-identical to the reviewed template.

`automation.md` also carries what Step 5 points a host at: the signing
setup for a curator who opens their own pull request (the SSH key already
used to push, registered on GitHub a second time as a *signing* key,
because GitHub blocks approving one's own pull request and the
`provenance` gate then needs a signature),
the advice to mark `validate` and `provenance` as required checks, and the
wrinkle that the librarian's own review pull request never fires that gate:
GitHub does not start `pull_request` workflows for a pull request opened
with the default `GITHUB_TOKEN`, so `publish` runs its own two checks first
and a required check sits at "Expected" there until a person fires a fresh
event.
