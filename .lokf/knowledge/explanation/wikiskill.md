---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/wikiskill
title: What KTL took from WikiSkill
description: "What Knowledge Trust Ladder (KTL) took from the WikiSkill paper (Tang et al., 2026), as `docs/wikiskill.md` says: the same loop of maintainer, pen, consumer and gate; the seven changes the reading made to the skills, such as a consumer that writes nothing, a bounded run and a retrieval score; and what the paper leaves open."
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
- https://knowledge-trust-ladder.example/knowledge/explanation/skillwiki
generated:
  by: process:ktl-librarian
  at: "2026-10-12T16:43:57Z"
status: draft
verified:
- by: process:ktl-librarian
  at: "2026-10-12T23:54:05Z"
---

# Overview

`docs/wikiskill.md` says what Knowledge Trust Ladder (KTL) took from one paper, and what the paper leaves open. The paper is *WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution* (Tang et al., Google Research, August 2026). It has an agent compile its own execution traces into a wiki, and evolves the agent's skills from it. KTL has an agent derive a bundle from a repository and has a person confirm it. Both take their shape from Andrej Karpathy's LLM Wiki: immutable sources, a corpus a model writes, an index a reader opens first, a log, and a conventions file. WikiSkill is not SkillWiki, a 2026 paper on governing agent skills that [SkillWiki](skillwiki.md) covers.

The two run the same loop:

- a model maintains the corpus;
- a program applies its changes and keeps the record;
- a separate agent consumes the corpus without writing it;
- a gate decides what stays.

WikiSkill's gate is a validation score, with no person in the loop. KTL's gate is the registrar, and the verdict is a named person's.

# What KTL took from it

Reading the paper in October 2026 changed the skills in these places, and `CHANGELOG.md` lists each change:

- **The consumer does not maintain the corpus.** The docent reads the bundle and writes nothing in it. When it has to go to the repository it says so and records the miss in `feedback.md`.
- **The maintainer reads the rejections first.** The librarian reads the curator's verdicts before it derives anything: the `**Curation**` lines in `log.md` and every open question a person left. It re-derives a sent-back concept from the source the note names, and reports a repeated send-back as a defect in its own instructions.
- **A declined proposal is not proposed again.** The scheduled workflow reads the pull requests a person closed without merging. The librarian proposes none of their changes again until the source moves or a reader asks again. While a pull request is open, a scheduled run opens no second one.
- **The index entry is the retrieval interface.** The docent picks one to three concepts from the `index.md` bullets before it opens anything. A bullet copies the concept's `description`, and the pen keeps the copies equal. A miss on a question an existing concept answers is a defect in that description, not a reason to add a second concept.
- **A recurring question is a signal.** The pen moves each handled feedback entry into `questions.md`, a ledger that only grows, and `knowledge-report.sh` names the concepts readers keep arriving at.
- **The maintainer's run is bounded.** The librarian starts from a work list `knowledge-report.sh` computes from history, never from a clock. A run handles at most ten feedback entries, oldest first. A scheduled week in which nothing waits runs no agent, and the first run of each month goes ahead regardless.
- **A measured outcome beside the gate.** A scheduled refresh can carry a retrieval score: the agent chooses concepts from `index.md` alone for each question in the ledger, and a program scores the reply. The pull request shows `n of m`, and a person decides, so a neutral change still merges.

The paper's results also support two things KTL already did. Its ablation finds the persistent wiki worth fifteen points on average. In KTL, the pen refuses to delete a concept a person confirmed. The paper lists pruning as unsolved. KTL has `stale_after`, `status: deprecated` and the librarian's orphan sweep.

# What the paper leaves open

The paper is evidence for the loop, not for the parts KTL adds. It runs no schema, derives nothing twice to test reproducibility, records no one behind a page, and has no person in the loop.
