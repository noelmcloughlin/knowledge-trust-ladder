---
type: Explanation
id: https://w3id.org/ktl/knowledge/explanation/intended-uses
title: What Knowledge Trust Ladder is for, and what it is not
description: "Which uses Knowledge Trust Ladder (KTL) fits and which it does not, as `docs/uses.md` says: the nine uses the skills were built for, among them knowledge retold for a younger reader, DevSecOps and technology governance, what KTL is not (a scanner, a judge of truth, a vector store, a live system), and three questions for judging any other use."
genre: explanation
resource: docs/uses.md
sources:
  - resource: docs/uses.md
    id: uses.md
    excerpt: KTL keeps knowledge about systems. It does not scan, enforce or run them.
  - resource: README.md
  - resource: docs/architecture.md
  - resource: docs/skills-repositories.md
  - resource: docs/context-layer.md
generated:
  by: process:ktl-librarian
  at: "2026-11-17T19:01:39Z"
status: draft
relatedTo:
  - https://w3id.org/ktl/knowledge/explanation/three-lines-of-defence
  - https://w3id.org/ktl/knowledge/policies/threat-model
  - https://w3id.org/ktl/knowledge/explanation/domain-vocabularies
  - https://w3id.org/ktl/knowledge/explanation/context-layer
verified:
  - by: process:ktl-librarian
    at: "2026-11-17T22:28:06Z"
references:
  - https://w3id.org/ktl/knowledge/explanation/young-readers
---

# Overview

`docs/uses.md` says which uses Knowledge Trust Ladder (KTL) fits and which it does not. KTL keeps what is known about a repository as a catalogue of claims. Each claim names its source and carries a label that says how far it has been checked: by nobody, by automation, or by a named person. KTL keeps knowledge about systems, and does not scan, enforce or run them.[^uses.md]

In every use it does four things. The librarian derives claims and names their sources. The registrar checks what a program can check. The curator records a person's verdict. The next run starts from the concepts whose sources moved.

## The uses it was built for

The page lists nine, each with what carries it:

- answers about a repository that say how far each was checked, from the docent in any agent and in Microsoft 365 Copilot;
- context for a coding agent that outlasts one session, from the bundle's `index.md`;
- documentation that knows when it went stale, from the librarian's work list and the curation policy;
- a record of who vouched for what, from the curator, the evidence table on each release and [three lines of defence](three-lines-of-defence.md);
- a typed catalogue of a domain, from LOKF's classes and a [domain vocabulary](domain-vocabularies.md);
- knowledge kept outside the repository, through the ingest;
- one layer of context over many repositories, through [federation](context-layer.md);
- a site and a release that anyone can read, from the website skill and the release workflow;
- the same knowledge retold for a younger reader.

[Young readers](young-readers.md) covers that last use.

## The two uses readers asked about

- **DevSecOps.** KTL fits as the knowledge side. A bundle can hold what a team's pipelines are, which checks a branch requires, which policy asks for them, and who confirmed each claim. A domain vocabulary adds the types a security standard defines, such as those of SLSA or CWE. KTL is not the tooling side: it runs no scanner, stores no secret, writes no bill of materials and decides no deployment, and its gate checks the bundle and never the code.
- **Technology governance.** KTL fits where governance needs to know who is accountable for a statement. [Three lines of defence](three-lines-of-defence.md) places each role in the model that regulated industries use, and says what an auditor can check and where that evidence stops. KTL is not a governance, risk and compliance system: it keeps no risk register, tests no control and tracks no exception.

## What it is not

The page names six things: the source of truth, a judge of truth, a vector store, a live system, a place for secrets or personal data, and a test of whether something works.

## Judging another use

Three questions settle most uses the page does not list. Is there a source to point at? Does it matter who vouched for it? Does it change slowly enough for a person to confirm? A use that passes all three still needs someone to play the curator, a little and regularly.

[^uses.md]: docs/uses.md, the second paragraph
