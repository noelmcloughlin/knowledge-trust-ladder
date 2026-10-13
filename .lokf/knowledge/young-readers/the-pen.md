---
type: GlossaryTerm
id: https://knowledge-trust-ladder.example/knowledge/young-readers/the-pen
title: The pen, for readers aged 13 to 18
description: The pen retold for readers aged 13 to 18, the script that is ktl-librarian's only way to write the bundle, and what it refuses.
definition: The name the docs give `knowledge-apply.sh`, the script through which ktl-librarian writes every change to the bundle.
genre: reference
resource: skills/ktl-sidecar/templates/scripts/knowledge-apply.sh
derivedFrom:
- https://knowledge-trust-ladder.example/knowledge/glossary/the-pen
sources:
- resource: .lokf/knowledge/glossary/the-pen.md
about:
- https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
tags:
- audience-13-18
generated:
  by: process:ktl-librarian
  at: "2026-10-13T15:08:54Z"
status: draft
verified:
- by: process:ktl-librarian
  at: "2026-10-12T23:54:28Z"
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/glossary/registrar
---

This page is for readers aged 13 to 18. It retells [[the-pen]] in shorter words. The full page has every detail.

# What is the pen?

**The pen** is the name the docs give `knowledge-apply.sh`. It is the script through which ktl-librarian writes every change to the bundle ([[knowledge-bundle]]).

# How does the librarian use it?

ktl-librarian never edits a file under `.lokf/knowledge/` by hand. It describes each change as an operation in `.lokf/patch.yaml`. The pen checks every operation. Then it writes the files, or it refuses the whole file and writes nothing.

# What does the pen do with a change?

- It stamps `generated` from the clock.
- It keeps a concept's `description` equal to its two index bullets.
- It files each line in `log.md`.

# What does the pen refuse?

The pen refuses:

- a `human:` actor, which marks a person's record;
- a rewrite of text a person wrote;
- the deletion of a concept a person confirmed or left a note on.

It also refuses a patch that would add, change or remove a person's record. That record is a `human:` event or a person's note.

# Who else writes the bundle?

The pen is the librarian's only way to write the bundle. A person writes the curator's verdicts another way, through ktl-curator or the KTL Curator plugin. The architecture page names the pen as the [[registrar]] for the librarian.
