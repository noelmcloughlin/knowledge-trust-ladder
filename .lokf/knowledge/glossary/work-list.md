---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/glossary/work-list
title: Work list
description: "What `knowledge-report.sh worklist` prints for ktl-librarian before each refresh, from frontmatter and git, in paths and dates and nobody's words: the concepts whose sources moved since they were derived or last checked, the notes a person left and the librarian's own open questions. It also counts the reader feedback that waits."
definition: The list `knowledge-report.sh worklist` computes from frontmatter and git, which ktl-librarian starts every refresh from.
genre: reference
resource: skills/ktl-librarian/SKILL.md
sources:
- resource: skills/ktl-librarian/SKILL.md
- resource: docs/for-the-curious.md
relatedTo:
- https://w3id.org/ktl/knowledge/playbooks/ktl-librarian-skill
- https://w3id.org/ktl/knowledge/glossary/librarian
generated:
  by: process:ktl-librarian
  at: "2026-10-13T15:08:54Z"
status: draft
verified:
- by: process:ktl-librarian
  at: "2026-10-16T23:58:13Z"
---

# Overview

ktl-librarian starts every refresh from the **work list**, which `bash .lokf/scripts/knowledge-report.sh worklist` prints. A program has already found which concepts' sources moved since they were derived or last checked, which notes a person left, and which of those a later confirmation answered. It counts the reader entries that wait and names the concepts readers keep asking about, in paths and dates and nobody's words.

A source moved when its last commit comes after the commit that recorded the [librarian](librarian.md)'s stamp or the latest check, so history orders the two and no clock does. The same script computes each trust label from the frontmatter on every read, for the docent's answers, the curator's report and the librarian's work list (`docs/for-the-curious.md`).
