---
type: Explanation
id: https://w3id.org/ktl/knowledge/explanation/why-a-registrar-role
title: Why a registrar role, and why it is not a skill
description: "What the registrar does, keeping every bundle record in order and every confirmation tied to a person, and why no person has to do it: the `lokf` toolkit, CI's `knowledge-registrar.yaml`, the `knowledge-apply.sh` pen at the librarian's desk, and two optional Obsidian plugins for a desk with no CI."
genre: explanation
resource: README.md
sources:
  - resource: README.md
  - resource: docs/obsidian.md
  - resource: skills/ktl-librarian/SKILL.md
  - resource: skills/ktl-sidecar/SKILL.md
generated:
  by: process:ktl-curator
  at: "2026-10-13T00:25:28Z"
relatedTo:
  - https://w3id.org/ktl/knowledge/explanation/why-four-roles
  - https://w3id.org/ktl/knowledge/explanation/three-lines-of-defence
about:
  - https://w3id.org/ktl/knowledge/glossary/registrar
verified:
  - by: human:noelmcloughlin
    at: "2026-09-10T00:00:00Z"
  - by: human:noelmcloughlin
    at: "2026-10-03T09:42:48Z"
  - by: process:ktl-librarian
    at: "2026-10-19T20:01:11Z"
  - by: human:noelmcloughlin
    at: "2026-10-13T00:25:28Z"
stale_after: 2027-09-10
status: draft
---
# Overview

A museum registrar keeps the records themselves in order: each accession documented, its provenance filed, nothing entered in a form the catalogue can't read. The README calls it the fifth role, which is not a skill, beside the four that are ([why four skill roles](why-four-roles.md)). No person has to do it. The `lokf` toolkit does it on every change, and CI's `knowledge-registrar.yaml` does it again on every pull request that touches the bundle. There it also ties each confirmation that is added or removed to that person's approval or their signed commit.

At the librarian's desk the registrar is `knowledge-apply.sh`, the only pen. The librarian describes each change as an operation in `.lokf/patch.yaml`, and the script, not the agent, writes the record: it stamps `generated`, keeps the index bullets equal to the description, files the log line under the day's heading, and refuses an operation that would name a person as its actor, rewrite text a person wrote, or delete a concept a person confirmed or left a note on. In the scheduled run the wrapper applies the file after the agent has finished, so the agent never writes the bundle at all. At the reader's desk and the curator's the registrar is `knowledge-report.sh`, which computes each trust label and the bundle's health line, so that neither is a model's arithmetic. The README calls these the deterministic tools: a check gives the same answer every time, which neither the librarian nor the curator can promise.

In [Obsidian](https://obsidian.md/) there is no CI, so two optional plugins do the registrar's work at the desk. [KTL Registrar](https://github.com/noelmcloughlin/obsidian-ktl-registrar) checks each record as it is typed, and [KTL Curator](https://github.com/noelmcloughlin/obsidian-ktl-curator) runs this repository's `ktl-curator` review session with no agent in the loop.

In the three lines of defence that regulated industries use, the librarian and the curator are the first line, the registrar the second, and the bundle ships the evidence a third line would need ([three lines of defence](three-lines-of-defence.md)).

The curator is always a person; the skill and the plugin that carry the name are that person's assistants, and neither reaches a verdict of its own. Obsidian is optional in both directions: the plugins work on any LOKF bundle however it was made, and a vault with no bundle in it is left alone (`docs/obsidian.md`).

## Open questions

- 2026-10-13, process:ktl-librarian: Since 2026-10-13 the fifth-role section is on `docs/architecture.md`, not in `README.md`, so `resource`, `sources` and "The README calls it the fifth role" should name that page. That page and `docs/obsidian.md` now say KTL Registrar does the registrar's work and KTL Curator assists the curator, while this concept and its description say both plugins do the registrar's work.
- 2026-10-19, human:noelmcloughlin: refresh against sources.
