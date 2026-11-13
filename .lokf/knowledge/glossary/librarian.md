---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/librarian
title: Librarian
description: "The role that binds a repository's knowledge into order, played by the ktl-librarian skill: it derives concepts with their sources, classifies and links them, audits, and hands off for review. It catalogues without vouching, and writes the bundle only through the pen."
definition: The role that derives the bundle's concepts from the repository with their sources, classifies them, links them with typed relationships, audits, and hands off for review. It records facts about the repository, never verdicts about truth.
genre: reference
resource: docs/architecture.md
sources:
  - resource: docs/architecture.md
  - resource: docs/cast/librarian.md
    id: cast-librarian.md
    excerpt: It derives each concept from a source it names, gives it a LOKF class, and links it to other concepts with typed relations.
  - resource: skills/ktl-librarian/SKILL.md
about:
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
relatedTo:
  - https://w3id.org/ktl/knowledge/playbooks/ktl-librarian-skill
  - https://w3id.org/ktl/knowledge/glossary/the-pen
  - https://w3id.org/ktl/knowledge/glossary/curator
  - https://w3id.org/ktl/knowledge/glossary/work-list
generated:
  by: process:ktl-librarian
  at: "2026-11-13T14:41:35Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-29T00:48:33Z"
---

# Overview

The architecture page names a role after the library profession: the **librarian** *binds it into order*. It runs often, including on a schedule, and records facts about the repository, never verdicts about truth. Its own page says it derives each concept from a source it names, gives it a LOKF class, and links it to other concepts with typed relations.[^cast-librarian.md] Like a real librarian it catalogues without vouching. The `ktl-librarian` skill also audits the bundle and prepares a change for a maintainer to review. It starts each later run from its [work list](work-list.md).

The `ktl-librarian` skill plays the role ([ktl-librarian skill](../playbooks/ktl-librarian-skill.md)). It writes the bundle only through [the pen](the-pen.md), which marks each concept it creates `status: draft` until a person confirms it through the curator.

The data-management sense of the word *curator* is the librarian's job. The [curator](curator.md) is the museum sense.

[^cast-librarian.md]: docs/cast/librarian.md, *What it does*
