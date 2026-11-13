---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/health-line
title: Health line
description: "The one line `knowledge-report.sh` prints for the whole bundle, counting its concepts under eight trust labels, such as \"Confirmed by a person: 3 of 40\" and \"Reopened\". It is derived on every read and never stored, and it is the number to watch over time."
definition: The line `knowledge-report.sh` computes for the whole bundle, counting its concepts under eight trust labels. "Confirmed by a person, a of N" rising is the bundle earning trust.
genre: reference
resource: skills/ktl-curator/references/trust-fields.md
sources:
  - resource: skills/ktl-curator/references/trust-fields.md
    id: trust-fields.md
    excerpt: The whole report runs the local half of that check and prints the *Not tied to a signed commit* count and the concepts behind it.
  - resource: skills/ktl-curator/SKILL.md
  - resource: skills/ktl-sidecar/templates/scripts/knowledge-report.sh
  - resource: docs/architecture.md
  - resource: CHANGELOG.md
relatedTo:
  - https://w3id.org/ktl/knowledge/glossary/trust-label
  - https://w3id.org/ktl/knowledge/glossary/trust-ladder
  - https://w3id.org/ktl/knowledge/playbooks/ktl-curator-skill
generated:
  by: process:ktl-librarian
  at: "2026-11-13T14:41:35Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-11-02T13:29:19Z"
---

# Overview

The **health line** is one line for the whole bundle, which `knowledge-report.sh` computes so that it is not a model's arithmetic. It counts the concepts under eight [trust labels](trust-label.md): confirmed by a person, checked by automation only, nobody has checked, drafts, reopened, past review date, edited since confirmed, and retired. A retired concept is counted once, there. Since 0.45.0 *Drafts* counts the concepts no person has confirmed, and *Reopened* those a person confirmed and a question since put back to `status: draft`. A reopened concept still counts as confirmed, because a question flags a concept and never drops it a rung.

The curator's report opens with the line as the script prints it, for example:

`Confirmed by a person: 3 of 40 · Checked by automation only: 12 · Nobody has checked: 23 · Drafts: 4 · Reopened: 2 · Past review date: 2 · Edited since confirmed: 1 · Retired: 2 · Not tied to a signed commit: 1`

The last field, *Not tied to a signed commit*, counts the confirmations behind which git holds no signature. The whole report computes it, and drops the field when `.lokf/` is not git-tracked.[^trust-fields.md]

It is the one number to watch over time: "confirmed by a person: *a* of *N*" rising is the bundle earning trust. It is derived every time and never stored, since the specification keeps scores out of frontmatter. The architecture page says the number is meant to rise slowly, a handful of concepts in a sitting.

[^trust-fields.md]: skills/ktl-curator/references/trust-fields.md, *Checking a confirmation against git*, and the report template
