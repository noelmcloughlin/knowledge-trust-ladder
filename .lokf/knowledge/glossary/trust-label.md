---
type: GlossaryTerm
id: https://knowledge-trust-ladder.example/knowledge/glossary/trust-label
title: Trust label
definition: The plain-language phrase a skill uses for how far a concept has been checked - "confirmed by a person", "checked by automation only", "nobody has checked this yet" - derived from frontmatter, never stored.
genre: reference
resource: skills/ktl-curator/references/trust-fields.md
generated:
  by: process:ktl-librarian
  at: "2026-09-17T15:49:14Z"
status: draft
definedBy:
- https://knowledge-trust-ladder.example/knowledge/references/okf-specification
about:
  - https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
verified:
- by: process:ktl-librarian
  at: "2026-09-17T15:49:14Z"
---

# Overview

The labels restate OKF section 5.3's trust tiers in words a non-specialist can
act on. They are computed each time from `verified`, `status`, `generated.at`,
and `stale_after`: any `verified` actor prefixed `human:` means confirmed by a
person; events by non-human actors only mean checked by automation; no
`verified` key at all means nobody has checked it.

A `revision` on an event (proposed for lokf 0.9.0, not yet released) is
shown beside that event's date but changes no label: its absence means
unrecorded, never unchanged.

They deliberately overlap - a concept can be confirmed *and* past its review
date - so the counts in a curator report are not a partition. Nothing is
scored and nothing is stored: a score would be subjective, unportable, and
would go stale.
