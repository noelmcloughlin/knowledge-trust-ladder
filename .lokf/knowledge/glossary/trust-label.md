---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/trust-label
title: Trust label
description: The plain words the skills use for how far a concept has been checked, derived from its frontmatter on every read and never stored.
definition: The plain-language phrase a skill uses for how far a concept has been checked - "confirmed by a person", "checked by automation only", "nobody has checked this yet" - derived from frontmatter, never stored.
genre: reference
resource: skills/ktl-curator/references/trust-fields.md
generated:
  by: human:noelmcloughlin
  at: "2026-10-13T01:06:43Z"
definedBy: []
about:
- https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
verified:
- by: process:ktl-librarian
  at: "2026-10-06T11:10:52Z"
- by: human:noelmcloughlin
  at: "2026-10-13T01:06:43Z"
references:
- https://w3id.org/ktl/knowledge/references/okf-specification
status: draft
---

# Overview

The labels restate OKF v0.2 section 5's trust fields in words a non-specialist can act on. `knowledge-report.sh` computes them each time from `verified`, `status`, `generated.at` and `stale_after`. It also uses the relation fields for reliance. It computes each label except two, which are both worked out by hand: *doesn't fit the known vocabulary* and *not tied to a signed commit*.

- Any `verified` actor prefixed `human:` means confirmed by a person.
- Events by non-human actors alone mean checked by automation.
- No `verified` key, or one with no events, means nobody has checked it.

`knowledge-report.sh` reads `resource`, `sources[].resource` and git history for the label *a source moved since the confirmation*.

It reads `.lokf/feedback.md` for the label *a reader disputed this*: a waiting `**Disagreement**` that names the concept, never on a retired concept. It reads the newest `**Deprecation**` line in `log.md` for the successor a retired concept names. It reads `derivedFrom` for the label *derived from a concept edited since its confirmation*.

A `revision` on an event (proposed for lokf 0.9.0, not yet released) is shown beside that event's date but changes no label: its absence means unrecorded, never unchanged.

The labels overlap. A concept can be confirmed *and* past its review date, so the counts in a curator report are not a partition. One pair never overlaps: a concept edited since its confirmation is counted under *edited since confirmed* and not as confirmed, because the person confirmed an earlier text. Nothing is scored and nothing is stored: the spec keeps scores out of frontmatter.

## Open questions

- 2026-10-16, process:ktl-librarian: Since 0.45.0 `skills/ktl-curator/references/trust-fields.md` has a label *Reopened*: `status: draft` on a concept with a `human:` `verified` event, naming the earliest question asked on or after the confirmation's day, its asker and how many wait. A reopened concept still counts as confirmed, and *Still a draft* now needs no `human:` event. This concept does not name the label.
