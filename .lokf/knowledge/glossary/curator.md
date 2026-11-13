---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/curator
title: Curator
description: "The role that holds the scales, always a person: in the museum sense, the one who authenticates, weighs provenance and decides what goes on exhibit. The ktl-curator skill and the KTL Curator plugin are that person's assistants, and reach no verdict of their own."
definition: "The role, always played by a person, that records a verdict on a concept against its source: confirm, correct, retire or send back. Curator is the museum sense, the one who authenticates, weighs provenance and decides what goes on exhibit, not the data-management sense, which is the librarian's job."
genre: reference
resource: docs/architecture.md
sources:
  - resource: docs/architecture.md
  - resource: docs/cast/curator.md
    id: cast-curator.md
    excerpt: "The skill prints a one-screen report first: the health line, what is worth ten minutes today, and the questions that wait. A review session follows only when you say yes. It takes one concept at a time, shows the source before the claim, and records one verb."
  - resource: docs/how-it-works.md
  - resource: docs/obsidian.md
  - resource: skills/ktl-curator/SKILL.md
about:
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
relatedTo:
  - https://w3id.org/ktl/knowledge/playbooks/ktl-curator-skill
  - https://w3id.org/ktl/knowledge/glossary/librarian
  - https://w3id.org/ktl/knowledge/glossary/trust-label
  - https://w3id.org/ktl/knowledge/glossary/health-line
generated:
  by: process:ktl-librarian
  at: "2026-11-13T14:41:35Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-29T00:48:33Z"
---

# Overview

The architecture page names a role after the museum profession: the **curator** *holds the scales*. Curator is the museum sense, the one who authenticates, weighs provenance and decides what goes on exhibit. It is not the data-management sense, which is the [librarian](librarian.md)'s job.

The curator is always a person. The `ktl-curator` skill is that person's assistant. It prints a one-screen report first, and a review session follows only when the person says yes. The session takes one concept at a time, shows the source before the claim, and records one verb: confirm, send back, correct now, retire or later.[^cast-curator.md] It records judgements a person made, never facts it derived, and it runs a little, regularly ([ktl-curator skill](../playbooks/ktl-curator-skill.md)). In Obsidian, the KTL Curator plugin is the same assistant. The skill and the plugin that carry the name reach no verdict of their own.

A verdict is a `verified` event in that person's name, or a change of `status` or review date, with one line in `log.md`. On a send-back of text that person wrote, `ktl-curator` asks whether to release it to the librarian. On a yes it sets `generated.by` to `process:ktl-curator`, which needs an authenticated id. A concept a person checked against its source reads *confirmed by a person*, the top [trust label](trust-label.md), and the [health line](health-line.md) counts how many do.

[^cast-curator.md]: docs/cast/curator.md, *What a session looks like*
