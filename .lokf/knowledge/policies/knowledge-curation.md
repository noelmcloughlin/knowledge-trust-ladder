---
type: Policy
id: https://w3id.org/ktl/knowledge/policies/knowledge-curation
title: Knowledge curation policy
description: How often each kind of concept in this bundle is re-confirmed by a person, and who does it.
genre: reference
sources:
  - resource: skills/ktl-curator/references/review-session.md
    title: the curation policy template whose sections and switches this policy fills in
generated:
  by: human:noelmcloughlin
  at: "2026-11-12T18:17:09Z"
---

# Who curates

Noel McLoughlin (`human:noelmcloughlin`), alone for now.

# How often a person re-confirms

| Kind of concept | Re-confirm every |
| --- | --- |
| Policies, playbooks, references | 12 months |
| Glossary terms, explanations | 24 months |

The ktl-curator skill proposes `stale_after` from this table when a person confirms a concept. Change the table, not the skill.

# What "confirmed" means here

A named person opened the concept's source and agreed the concept still says what the source says. Automation re-checking that a file still exists is recorded separately and is not confirmation.

# Independent re-check

Independent re-check: 0

There is no second person to hand a sample to yet. Set above zero and every ktl-curator report lists that many concepts confirmed by a person, picked by a rule the curator cannot steer, for someone other than the person who confirmed them.

# Automation re-check

Automation re-check: 3

Every ktl-curator report lists three concepts checked by automation only, picked by the same rule, for a person to check against their sources. The verdict goes through the ordinary verbs.

# How the docent answers

Evidence first: yes

ktl-docent quotes the source before any answer that rests on a concept not yet confirmed by a person.

# Younger readers

Younger readers: 13-18

ktl-librarian may write retellings of confirmed concepts for readers aged 13 to 18 on its scheduled runs. Each one is a new concept, which a person confirms against the concept it retells.
