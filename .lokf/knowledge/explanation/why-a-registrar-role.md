---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/why-a-registrar-role
title: Why a registrar role, and why it is not a fifth skill
description: The job none of the four skills does - keeping bundle records well-formed and every confirmation tied to a person - and why it is done by tooling (the `lokf` toolkit, CI, and two optional Obsidian plugins) rather than by an agent.
genre: explanation
resource: README.md
sources:
- resource: README.md
- resource: docs/obsidian.md
generated:
  by: process:ktl-librarian
  at: "2026-09-24T11:05:00Z"
status: draft
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/explanation/why-four-roles
about:
- https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
verified:
- by: human:noelmcloughlin
  at: "2026-09-10T00:00:00Z"
stale_after: 2027-09-10
---

# Overview

A museum registrar keeps the records themselves in order: each accession documented, its provenance filed, nothing entered in a form the catalogue can't read. The README calls it the fifth role, which is not a skill, beside the four that are ([why four skill roles](why-four-roles.md)). No person has to do it. The `lokf` toolkit does it on every change, and CI's `knowledge-registrar.yaml` does it again on every pull request that touches the bundle. There it also checks that each new confirmation is backed by that person's approval of the pull request or their signature on the commit.

In [Obsidian](https://obsidian.md/) there is no CI, so two optional plugins do the registrar's work at the desk:

- [KTL Registrar](https://github.com/noelmcloughlin/obsidian-ktl-registrar) checks each record is well-formed as it is typed, live in the editor - the first of the four levels of checking.
- [KTL Curator](https://github.com/noelmcloughlin/obsidian-ktl-curator) runs this repository's `ktl-curator` review session - the third level: source beside claim, the person's decision written down, and no agent in the loop.

The curator is always a person; the skill and the plugin that carry the name are that person's assistants, and neither reaches a verdict of its own. Obsidian is optional in both directions: the plugins work on any LOKF bundle however it was made, and a vault with no bundle in it is left alone (`docs/obsidian.md`).
