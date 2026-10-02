---
type: GlossaryTerm
id: https://knowledge-trust-ladder.example/knowledge/glossary/trust-label
title: "Trust label"
description: "The plain words the skills use for how far a concept has been checked. Each label is computed from the concept's frontmatter on every read and never stored."
definition: "A plain-words statement of how far a concept has been checked, such as \"confirmed by a person\", computed from the concept's `verified`, `generated`, `status` and `stale_after` fields on every read and never stored."
genre: reference
resource: skills/ktl-curator/references/trust-fields.md
sources:
- resource: skills/ktl-curator/references/trust-fields.md
- resource: skills/ktl-curator/SKILL.md
- resource: skills/ktl-docent/SKILL.md
- resource: README.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
about:
  - https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
definedBy:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-curator-skill
---

# Overview

The README says that every concept carries its own trust record, and that the curator reports it in plain words rather than ontology terms. The labels are computed from the frontmatter on every read and never stored, so they cannot drift from what they describe.

# The labels

The curator's `references/trust-fields.md` defines each one by the fields behind it:

- **Confirmed by a person**: any `verified[].by` starts with `human:`.
- **Checked by automation only**: `verified` is present, with no `human:` actor.
- **Nobody has checked this yet**: there is no `verified` key.
- **Still a draft**: `status: draft`.
- **Retired**: `status: deprecated`.
- **Edited since a person last confirmed it**: `generated.at` is later than the latest `human:` `verified[].at`. The two times are compared whole, never cut to the day.
- **Past its review date**: `stale_after` is on or before today. **Due soon**: within the next thirty days.
- **N other concepts rely on this**: how many concepts' typed relations target this concept's `id`.
- **Doesn't fit the known vocabulary**: the `type` is neither a core LOKF class nor a class of the host's domain schema.
- **Not tied to a signed commit**: a `human:` confirmation whose introducing commit carries no good signature.

The docent uses the same words, with the first seven, and never says RDF, IRI, SPARQL or tier to a reader. The Obsidian plugins show the same labels at the desk.

# What the number to watch means

The README names one number to watch: confirmed by a person, n of N. It is meant to rise slowly, a handful of concepts in a sitting. A small, young bundle can reach fully confirmed quickly. A large or fast-growing one never quite does, and the report says so.
