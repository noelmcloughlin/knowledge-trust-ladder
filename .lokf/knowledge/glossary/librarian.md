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
  at: "2026-10-13T15:08:54Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-28T00:35:16Z"
---

# Overview

The architecture page names a role after the library profession: the **librarian** *binds it into order*. It scrapes the repository, derives concepts with their sources, classifies them, links them with typed relationships, audits, and hands off for review. Like a real librarian it catalogues without vouching: facts about the repository, never verdicts about truth. It runs often, including on a schedule, and starts each run from its [work list](work-list.md).

The `ktl-librarian` skill plays the role ([ktl-librarian skill](../playbooks/ktl-librarian-skill.md)). It writes the bundle only through [the pen](the-pen.md), which marks each concept it creates `status: draft` until a person confirms it through the curator.

The data-management sense of the word *curator* is the librarian's job. The [curator](curator.md) is the museum sense.
