---
type: Explanation
id: https://w3id.org/ktl/knowledge/explanation/young-readers
title: Young readers
description: "How KTL retells knowledge that adults wrote for readers aged 8 to 18, for a teacher or a youth leader: what a retelling is, the two age bands and their limits, what each role does, how to ask for one, what KTL never does with a young reader, and what exists today."
genre: explanation
resource: docs/young-readers.md
sources:
  - resource: docs/young-readers.md
    id: docs-young-readers.md
    excerpt: This page is for a teacher, a youth leader, or anyone who wants knowledge that adults wrote retold for readers aged 8 to 18.
relatedTo:
  - https://w3id.org/ktl/knowledge/explanation/three-lines-of-defence
  - https://w3id.org/ktl/knowledge/explanation/intended-uses
references:
  - https://w3id.org/ktl/knowledge/playbooks/ktl-prose-skill
  - https://w3id.org/ktl/knowledge/policies/knowledge-curation
  - https://w3id.org/ktl/knowledge/young-readers/the-pen
  - https://w3id.org/ktl/knowledge/glossary/trust-label
  - https://w3id.org/ktl/knowledge/glossary/librarian
  - https://w3id.org/ktl/knowledge/glossary/curator
  - https://w3id.org/ktl/knowledge/glossary/docent
  - https://w3id.org/ktl/knowledge/glossary/registrar
generated:
  by: process:ktl-librarian
  at: "2026-11-14T20:13:07Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-11-26T02:26:42Z"
---

# Overview

`docs/young-readers.md` is for a teacher, a youth leader, or anyone who wants knowledge that adults wrote retold for readers aged 8 to 18.[^docs-young-readers.md] Adults write most knowledge for other adults, and a school book is that knowledge written again for a younger reader. KTL keeps both in one bundle. The adult concept stays as its authors wrote it. A *retelling* says the same thing in shorter words for readers in a band of ages, links back to the adult concept, and carries a [trust label](../glossary/trust-label.md) of its own.

# What a retelling is

A retelling is a new concept, never an edit of the adult one. It leaves detail out, explains each term, and may reorder what it keeps. It never says what the adult concept does not say.

The page names two bands by age, because readers come from many school systems.[^docs-young-readers.md]

| Band | The reader | A sentence is split over | A paragraph is split over |
| --- | --- | --- | --- |
| `8-12` | aged 8 to 12 | 15 words | 50 words |
| `13-18` | aged 13 to 18 | 20 words | 75 words |

ktl-prose's young readers page maps a school year or a grade to a band. It also gives a pass for dyslexic readers, which keeps every fact and changes the page in place.

A retelling names the adult concept as its source. So when the adult concept changes, the retelling goes on the librarian's work list, and the two cannot drift apart unseen.

# Who does what

- The **librarian** writes a retelling from the adult concept alone, as a new concept under `young-readers/`, when a person asks. On a schedule, it writes one only for a band the [curation policy](../policies/knowledge-curation.md) names, and only from a concept a person has confirmed.
- **ktl-prose** holds a retelling to its band's limits, and shows by script that the retelling adds nothing the adult concept does not hold.
- The **curator** is an adult who confirms the retelling against the adult concept, and asks whether that concept supports every sentence.
- The **docent** answers in the band the asker names, when the asker says the answer is for a younger reader.
- The **registrar** checks a retelling as it checks any concept.

# How to ask

- For a page outside the bundle, a person asks for a version for a band. ktl-prose writes a new file beside the page, such as `README.en-simple.md`, and leaves the page as it is.
- For a concept in the bundle, a person asks the librarian to retell it for a band, and the librarian writes it through the pen.
- For every confirmed concept, on a schedule, a person sets `Younger readers: 8-12` in the curation policy with ktl-curator.[^docs-young-readers.md]
- For one answer, the asker tells the docent who the answer is for.

The request names the band. When it names no age, grade or school year, the skill asks which band is meant.

# What KTL never does

- **It never guesses an age.** The skills never infer a reader's age from how they write, and never ask a reader's own age. The person who asks names the band.
- **It never records a reader.** No file holds a reader's name, age or words. A host that reads a retelling with young readers records only a count in a band.
- **It never asks for consent on a host's behalf.** Consent from the readers, and from their parents or carers, stays with the host.

# What exists today

This repository has tried retellings on its own pages only: the architecture page for readers aged 13 to 18, and one retold concept in the bundle, [the pen](../young-readers/the-pen.md). Captured runs show both being written and checked. The project knows of no school or youth group that has built a bundle this way.[^docs-young-readers.md]

# The other end of the range

A retelling for a ten-year-old and a policy for a bank's auditor sit on the same ladder. Each says where it came from, what checked it, and who vouched for it. The page names [three lines of defence](three-lines-of-defence.md) as its counterpart for regulated industries, and [what KTL is for](intended-uses.md) for the other uses.

[^docs-young-readers.md]: docs/young-readers.md, the note at the top, the table of bands, *How to ask* and *What exists today*
