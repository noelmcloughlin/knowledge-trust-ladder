---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/wikiskill
title: What WikiSkill says about a knowledge bundle
description: 'The WikiSkill paper (Tang et al., 2026) read against this design: what the two share, what the skills took from it, and what the paper can and cannot say about determinism.'
genre: explanation
resource: docs/wikiskill.md
sources:
- resource: docs/wikiskill.md
- resource: README.md
about:
- https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/explanation/three-lines-of-defence
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-librarian-skill
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-docent-skill
- https://knowledge-trust-ladder.example/knowledge/playbooks/knowledge-sources
generated:
  by: process:ktl-librarian
  at: '2026-10-02T23:56:29Z'
status: draft
---
# Overview

`docs/wikiskill.md` reads one paper against this design: *WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution* (Tang et al., Google Research, August 2026). The paper builds a wiki that an agent maintains from its own execution traces, and evolves the agent's skills from that wiki. Both designs descend from Andrej Karpathy's LLM Wiki: immutable sources, an LLM-written wiki with an index and a log, and a conventions file. WikiSkill keeps that schema as prose and adds a JSON output contract and a scored gate. A bundle replaces it with a LinkML schema, typed relations, trust fields, a conventions script and a CI gate.

# What the two share

The paper's three layers map onto the repository, the bundle and the skills. Its wiki maintainer is the librarian, its inference agent the docent, and its gate the registrar and the curator. Its largest result, that persistence is the lever, is the librarian's rule to correct continuously and never reset. Its second result, that the consumer must stay out of the maintainer's seat, is the docent's rule to record a miss rather than answer from the repository.

# What the skills took from it

- The librarian reads the curator's verdicts before it derives anything, and re-derives a sent-back concept from the source the note names.
- A miss on a question an existing concept already answers is a description defect, and the index bullet has a stated contract: one or two sentences a reader can choose from in `index.md` alone.
- The log bullet for a change made from reader feedback quotes the question, so a recurring miss stays visible.
- A run handles at most ten feedback entries.
- The librarian writes the bundle only through `knowledge-apply.sh`, the way the paper's maintainer emits patch operations that a harness applies.
- The captured docent answers name the concept behind each question, with links the link checker follows.

# The determinism question

The paper measures accuracy, not determinism, and its wiki has no schema, so it is consistent with the bet that mechanical parts make a knowledge layer more predictable, and is not evidence for it. The parts it trusts are the mechanical ones: a write-once raw layer, an audit trail the harness writes, a scored gate, a JSON contract. Reading it beside the code found four places where a constraint existed in prose or in the schema and no program ran it. They are a SHACL check named and never run, a relation range nobody enforced, an actor on an open-question bullet nobody verifies, and three copies of every description nobody compares. The page says which are fixed and which wait for the sidecar's next release.
