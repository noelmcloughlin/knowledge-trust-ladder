---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/trust-ladder
title: Trust ladder
description: "Knowledge Trust Ladder's answer to who is responsible for the quality of the context: written into each concept, where it came from and how far it has been checked, as rungs a claim climbs from still a draft to confirmed by a person."
definition: The answer, written into each entry of the bundle, to who is responsible for the quality of the context. It says where the entry came from and how far it has been checked, in plain words.
genre: reference
resource: docs/architecture.md
sources:
  - resource: docs/architecture.md
relatedTo:
  - https://w3id.org/ktl/knowledge/glossary/trust-label
  - https://w3id.org/ktl/knowledge/glossary/health-line
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
generated:
  by: process:ktl-librarian
  at: "2026-10-26T20:05:58Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-29T00:48:33Z"
---

# Overview

The architecture page says a catalogue is useful only when a reader can tell which entries are sound, and that this depends on one question: *who is responsible for the quality of this context?* The **trust ladder** is the answer, written into each entry: where the entry came from and how far it has been checked, in plain words.

Its rungs are frontmatter fields. The page calls Knowledge Trust Ladder (KTL) an OKF runtime. OKF sets out to "standardize the small set of frontmatter fields that make an agent-maintained corpus **trustable**, without prescribing any runtime". In KTL those fields are the rungs a claim climbs, with a gate that refuses a `human:` confirmation no person can be tied to. The page's figure of the ladder runs from still a draft, through checked by automation, to confirmed by a person, and shows what drops a concept a rung and what only flags it. A question asked after a confirmation reopens the concept and flags what waits, but never drops the rung. Only an edit after the confirmation does that.

The curator reports each concept's place on the ladder in plain words, as a [trust label](trust-label.md) computed from the frontmatter on every read and never stored. The architecture page says each label is a signal for the reader to weigh, never a score.
