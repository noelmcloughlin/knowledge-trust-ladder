---
type: GlossaryTerm
id: https://knowledge-trust-ladder.example/knowledge/glossary/sidecar
title: Sidecar
description: "`.lokf/`, the folder beside a project's code that holds the bundle and the tooling that checks it, kept out of the project's build; also the role, and the ktl-sidecar skill, that installs it."
definition: The `.lokf/` folder beside a project's code, like `.git/`, which holds the bundle and the tooling that validates it and is kept out of the project's build. The ktl-sidecar skill, the first role to run, installs it from bundled templates.
genre: reference
resource: README.md
sources:
- resource: README.md
- resource: skills/ktl-sidecar/SKILL.md
- resource: skills/ktl-sidecar/templates/README.md
about:
- https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-sidecar-skill
- https://knowledge-trust-ladder.example/knowledge/explanation/hosts-and-doorways
generated:
  by: process:ktl-librarian
  at: "2026-10-04T17:59:39Z"
status: draft
verified:
- by: process:ktl-librarian
  at: "2026-10-06T09:49:14Z"
---

# Overview

The *sidecar* is `.lokf/`, a dot-folder beside a project's code, like `.git/`, and kept out of the project's build. The README it carries says it "does not touch the app build; it is independent tooling you can run on its own". It holds the bundle at `.lokf/knowledge/`, the scripts that check and write the bundle, and their docs. A `knowledge_bundle` link beside it names the bundle for folder pickers that hide dot-folders.

The same word names the first role in the README's table, which *lays the network*, and the `ktl-sidecar` skill that plays it. The skill installs `.lokf/` from bundled templates once, and later repairs a broken sidecar file.
