---
type: Explanation
id: https://lokf-agent-skills.example/knowledge/explanation/why-a-registrar-role
title: Why a registrar role, and why it is not a fifth skill
description: The job none of the four skills does - keeping bundle records themselves well-formed and provenanced - and why it is enforced by tooling (the `lokf` toolkit, CI, and two companion Obsidian plugins) rather than by an agent.
genre: explanation
resource: README.md
generated:
  by: process:lokf-librarian
  at: "2026-09-12T17:00:00Z"
relatedTo:
- https://lokf-agent-skills.example/knowledge/explanation/why-four-roles
about:
- https://lokf-agent-skills.example/knowledge/glossary/knowledge-bundle
verified:
- by: process:lokf-librarian
  at: "2026-09-13T15:00:00Z"
- by: human:noelmcloughlin
  at: "2026-09-10T00:00:00Z"
stale_after: 2027-09-10
---

# Overview

A museum registrar keeps accession records themselves in order - each entry
properly documented, provenance paperwork filed, nothing entered in a form
the catalogue cannot read - without ever judging whether an object is
authentic. That is a distinct job from the four this repository already
splits out ([why four roles](why-four-roles.md)): it does not derive facts
(librarian), does not decide what is trusted (curator), and does not answer
questions (docent). It is not a fifth skill here because, in a repository,
tooling already does it on every change: the `lokf` toolkit (`just
lokf-validate`, `just lokf-check-refs`) and CI's `Knowledge Registrar`
gate (`.github/workflows/knowledge-registrar.yaml` - renamed from
`knowledge-validate.yaml` to match this role by name).

Where a bundle is edited by hand instead - in [Obsidian](https://obsidian.md/),
with no CI to catch a malformed record - one plugin does the same job at the
desk rather than after a commit, and a second brings the curator's session
to that desk:

- [LOKF Registrar](https://github.com/noelmcloughlin/obsidian-lokf-registrar) -
  the registrar in the editor: checks a record is well-formed as it is
  written.
- [LOKF Curator](https://github.com/noelmcloughlin/obsidian-lokf-curator) -
  the curator's assistant, not the curator: puts a source beside a claim and
  records what a person decided, running this repository's `lokf-curator`
  review session without an agent in the loop.

Neither plugin reaches a verdict of its own - the registrar keeps the
provenance honest, the assistant keeps the record of the decisions, and the
judging stays with the curator, who is always a person; the skill and the
plugin that carry that name are that person's assistants. Both directions are optional companions rather than
a dependency: the plugins work on any LOKF bundle however it was produced,
and these four skills need no plugin, since `lokf validate` remains the gate
they rely on. The only thing every path shares is the LOKF specification
itself.
