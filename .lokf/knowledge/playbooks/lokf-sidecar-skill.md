---
type: Playbook
id: https://lokf-agent-skills.example/knowledge/playbooks/lokf-sidecar-skill
title: lokf-sidecar skill
description: One-shot procedure that creates a .lokf/ sidecar - tooling, docs, a dummy skeleton, and the knowledge_bundle doorway link beside it - from bundled templates, then hands off to lokf-librarian. Formerly named lokf-scaffolding.
genre: how-to
resource: skills/lokf-sidecar/SKILL.md
generated:
  by: process:lokf-librarian
  at: "2026-09-13T12:00:00Z"
status: draft
about:
  - https://lokf-agent-skills.example/knowledge/glossary/knowledge-bundle
definedBy:
- https://lokf-agent-skills.example/knowledge/references/agent-skills-specification
references:
  - https://lokf-agent-skills.example/knowledge/references/lokf-toolkit
verified:
- by: process:lokf-librarian
  at: "2026-09-13T15:00:00Z"
---

# Overview

Runs **once** per repository, or to repair a single missing sidecar file;
it never authors concepts. Six steps: gather the host project's facts (Step 0;
the layout is the same on every host - `.lokf/knowledge` is the real folder, see
[Hosts and doorways](../explanation/hosts-and-doorways.md)),
copy each file from `templates/` and substitute placeholders (Step 1), add
three root-level pointers - `llms.txt`, a README aside, and a `knowledge_bundle`
symlink onto `.lokf/knowledge` for people, folder pickers and Obsidian (Step 2, see
[Open the knowledge bundle in Obsidian](open-bundle-in-obsidian.md)) - verify no
placeholder survives (Step 3), validate (Step 4), optionally lay down the CI
automation (Step 5), and hand off (Step 6).

Its detail lives in two reference files - `references/portability.md` (non-git,
non-GitHub, non-POSIX hosts) and `references/automation.md` (what the Step 5
files do) - so the router itself stays small. Every file it writes is copied
from `templates/`, never retyped, which is what keeps a freshly laid-down bundle
byte-identical to the reviewed template.
