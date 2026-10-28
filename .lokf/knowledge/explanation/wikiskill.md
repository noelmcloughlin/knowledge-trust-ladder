---
type: Explanation
id: https://w3id.org/ktl/knowledge/explanation/wikiskill
title: What KTL took from WikiSkill
description: What Knowledge Trust Ladder (KTL) took from the WikiSkill paper (Tang et al., 2026), and what the paper leaves open. Both run one loop of maintainer, pen, consumer and gate, and the reading made seven changes to the skills, such as a consumer that writes nothing, a bounded run and a retrieval score.
genre: explanation
resource: https://arxiv.org/abs/2608.27454
sources:
  - resource: https://arxiv.org/abs/2608.27454
  - resource: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
  - resource: CHANGELOG.md
  - resource: docs/architecture.md
  - resource: docs/for-the-curious.md
  - resource: skills/ktl-docent/SKILL.md
  - resource: skills/ktl-librarian/SKILL.md
  - resource: skills/ktl-librarian/references/patch.md
  - resource: skills/ktl-sidecar/references/automation.md
  - resource: skills/ktl-sidecar/templates/github/knowledge-librarian.yaml
about:
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
relatedTo:
  - https://w3id.org/ktl/knowledge/explanation/three-lines-of-defence
  - https://w3id.org/ktl/knowledge/playbooks/ktl-librarian-skill
  - https://w3id.org/ktl/knowledge/playbooks/ktl-docent-skill
  - https://w3id.org/ktl/knowledge/playbooks/knowledge-sources
  - https://w3id.org/ktl/knowledge/explanation/skillwiki
generated:
  by: process:ktl-librarian
  at: "2026-10-26T20:05:58Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-28T00:35:16Z"
---

# Overview

*WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution* (Tang et al., Google Research, August 2026, arXiv:2608.27454) has an agent compile its own execution traces into a wiki, and evolves the agent's skills from it. In Knowledge Trust Ladder (KTL), an agent derives a bundle from a repository and a person confirms it. Both take their shape from Andrej Karpathy's LLM Wiki: immutable sources, a corpus a model writes, an index a reader opens first, a log, and a conventions file. WikiSkill is not SkillWiki, a 2026 paper on governing agent skills that [SkillWiki](skillwiki.md) covers.

The two run the same loop:

- a model maintains the corpus;
- a program applies its changes and keeps the record;
- a separate agent consumes the corpus without writing it;
- a gate decides what stays.

WikiSkill's gate is a validation score, with no person in the loop. KTL's gate is the registrar, and the verdict is a named person's.

# What KTL took from it

Reading the paper in October 2026 changed the skills in seven places, and `CHANGELOG.md` lists each change:

- **The consumer does not maintain the corpus.** Giving the paper's inference agent the wiki during training lowered its scores. The docent reads the bundle and writes nothing in it. When it has to go to the repository, it says so and records the miss in `feedback.md`, which the librarian learns from.
- **The maintainer reads the rejections first.** The paper's proposer reads its record of rejected proposals before it proposes. The librarian reads the curator's verdicts before it derives anything: the `**Curation**` lines in `log.md` and every open question a person left. It re-derives a sent-back concept from the source the note names, never the same way again, and names a send-back that comes twice in its hand-off to the reviewer.
- **A declined proposal is not proposed again.** The scheduled workflow reads the pull requests a person closed without merging, and the librarian proposes none of their changes again until the source moves, a person leaves a new note or a reader asks again. While its pull request is open, a scheduled run opens no second one.
- **The index entry is the retrieval interface.** The paper's maintainer prompt calls the index entries "the MOST IMPORTANT part of the wiki". The docent picks one to three concepts from the `index.md` bullets before it opens anything. A bullet copies the concept's `description`, and the pen keeps the copies equal. A miss on a question an existing concept answers is a defect in that description, not a reason for a twin.
- **A recurring question is a signal.** The pen moves each feedback entry the librarian handles into `questions.md`, a ledger that only grows, and `knowledge-report.sh` names the concepts readers keep arriving at.
- **The maintainer's run is bounded.** The paper caps what its maintainer reads in each iteration. The librarian starts from a work list `knowledge-report.sh` computes from history, never from a clock, and handles at most ten feedback entries a run, oldest first. In a scheduled week in which nothing waits, no agent runs, except in a month's first seven days, when the run goes ahead for the sources no program compares.
- **A measured outcome beside the gate.** The paper keeps a skill change only if a validation score rises. A scheduled refresh can carry a retrieval score beside KTL's gate: the agent chooses concepts from `index.md` alone for each question in the ledger, and a program scores the reply. The pull request shows `n of m`, and a person merges as before, whatever the score.

The paper's results also support two things KTL already did. Its ablation finds the persistent wiki worth fifteen points on average, and the pen refuses to delete a concept a person confirmed. The paper lists pruning as unsolved, and KTL has `stale_after`, `status: deprecated` and the librarian's orphan sweep.

# What the paper leaves open

The paper is evidence for the loop, not for the parts KTL adds. It runs no schema, derives nothing twice to test reproducibility, records no one behind a page, and has no person in the loop.
