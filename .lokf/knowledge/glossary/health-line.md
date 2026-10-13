---
type: GlossaryTerm
id: https://knowledge-trust-ladder.example/knowledge/glossary/health-line
title: Health line
description: "The one line `knowledge-report.sh` prints for the whole bundle, counting its concepts under seven trust labels, such as \"Confirmed by a person: 3 of 40\". It is derived on every read and never stored, and it is the number to watch over time."
definition: The line `knowledge-report.sh` computes for the whole bundle, counting its concepts under seven trust labels. "Confirmed by a person, a of N" rising is the bundle earning trust.
genre: reference
resource: skills/ktl-curator/references/trust-fields.md
sources:
- resource: skills/ktl-curator/references/trust-fields.md
- resource: skills/ktl-curator/SKILL.md
- resource: skills/ktl-sidecar/templates/scripts/knowledge-report.sh
- resource: docs/architecture.md
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/glossary/trust-label
- https://knowledge-trust-ladder.example/knowledge/glossary/trust-ladder
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-curator-skill
generated:
  by: process:ktl-librarian
  at: "2026-10-13T15:08:54Z"
status: draft
---

# Overview

The **health line** is one line for the whole bundle, which `knowledge-report.sh` computes so that it is not a model's arithmetic. It counts the concepts under seven [trust labels](trust-label.md): confirmed by a person, checked by automation only, nobody has checked, drafts, past review date, edited since confirmed, and retired. A retired concept is counted once, there.

The curator's report opens with the line, and adds one field the script does not compute, *Not tied to a signed commit*, for example:

`Confirmed by a person: 3 of 40 · Checked by automation only: 12 · Nobody has checked: 23 · Drafts: 4 · Past review date: 2 · Edited since confirmed: 1 · Retired: 2 · Not tied to a signed commit: 1`

It is the one number to watch over time: "confirmed by a person: *a* of *N*" rising is the bundle earning trust. It is derived every time and never stored, since the specification keeps scores out of frontmatter. The architecture page says the number is meant to rise slowly, a handful of concepts in a sitting.
