---
type: Explanation
id: https://w3id.org/ktl/knowledge/explanation/why-a-registrar-role
title: Why a registrar role, and why it is not a skill
description: "What the registrar, the fifth role and not a skill, does: it keeps every bundle record in order and ties every confirmation to a person, through the `lokf` toolkit, CI's `knowledge-registrar.yaml`, the pen `knowledge-apply.sh` and `knowledge-report.sh`, while the KTL Registrar plugin does that work in Obsidian, where there is no CI."
genre: explanation
resource: docs/architecture.md
sources:
  - resource: docs/architecture.md
  - resource: README.md
  - resource: docs/obsidian.md
  - resource: skills/ktl-librarian/SKILL.md
  - resource: skills/ktl-sidecar/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-19T21:26:04Z"
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
    at: "2026-10-29T00:48:33Z"
  - by: human:noelmcloughlin
    at: "2026-10-13T00:25:28Z"
stale_after: 2027-09-10
status: draft
---

# Overview

A museum registrar keeps a collection's records in order: each accession (an item added to the collection) documented, its provenance filed, nothing entered in a form the catalogue can't read. `docs/architecture.md` calls the registrar the fifth role, which is not a skill, beside the four skills ([why four skill roles](why-four-roles.md)). No person has to do it. The `lokf` toolkit checks every change, and CI's `knowledge-registrar.yaml` checks every pull request that touches the bundle. There it also ties each confirmation that is added or removed to that person's approval or their signed commit.

At the librarian's [desk](../glossary/desk.md) the registrar is `knowledge-apply.sh`, *the pen*, the only way the librarian writes the bundle. The librarian describes each change as an operation in `.lokf/patch.yaml`, and the script writes it. The script stamps `generated` from the clock, keeps a concept's `description` equal to its two index bullets, and files the log line under the day's heading. It refuses a `human:` actor, a rewrite of text a person wrote, and the deletion of a concept a person confirmed or left a note on. In a scheduled run the wrapper applies the patch after the agent has finished.

At the reader's desk and the curator's the registrar is `knowledge-report.sh`, which computes each trust label and the bundle's health line, so that neither is a model's arithmetic. These are the deterministic tools: a check gives the same answer every time, which neither the librarian nor the curator can promise.

In [Obsidian](https://obsidian.md/) there is no CI, so two optional plugins work inside the editor. [KTL Registrar](https://w3id.org/ktl/registrar/) does the registrar's work, checking each record as it is typed. [KTL Curator](https://w3id.org/ktl/curator/) is the curator's assistant, and runs this repository's `ktl-curator` review session with no agent in the loop. Obsidian is optional in both directions: the skills rely on `lokf validate`, not on a plugin, and the plugins work on any LOKF bundle however it was made (`docs/obsidian.md`).

In the three lines of defence that regulated industries use, the librarian and the curator are the first line, the registrar the second, and the bundle holds the evidence a third line would need ([three lines of defence](three-lines-of-defence.md)).

The curator is always a person. The skill and the plugin that carry the name reach no verdict of their own.
