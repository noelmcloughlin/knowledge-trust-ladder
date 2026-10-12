---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/skillwiki
title: What KTL took from SkillWiki
description: "What Knowledge Trust Ladder (KTL) took from the SkillWiki paper (Huang et al., 2026) and its code, as `docs/skillwiki.md` says: the four changes the reading made to the skills, the excerpt check that waits for LOKF 0.9.0, and where the two designs part, such as who stands behind a decision."
genre: explanation
resource: docs/skillwiki.md
sources:
- resource: docs/skillwiki.md
about:
- https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/explanation/wikiskill
- https://knowledge-trust-ladder.example/knowledge/explanation/skills-repositories
- https://knowledge-trust-ladder.example/knowledge/glossary/trust-label
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-curator-skill
generated:
  by: process:ktl-librarian
  at: "2026-10-12T16:43:57Z"
status: draft
---

# Overview

`docs/skillwiki.md` says what Knowledge Trust Ladder (KTL) took from one paper and its code, and where the two designs part. The paper is *SkillWiki: A Living Knowledge Infrastructure for Agent Skills* (Huang et al., Harbin Institute of Technology, Tencent and Nanyang Technological University, June 2026). The page cites the code at commit `050d540`. SkillWiki is not WikiSkill, the Google Research paper that [WikiSkill](wikiskill.md) covers.

SkillWiki turns trajectories, documents, API specifications, scripts and earlier skills into skills. It governs them through a lifecycle of eight stored states, a provenance graph and feedback from their runs. A SkillWiki skill is executable, and a KTL concept is a claim about a repository with the sources it rests on. So SkillWiki asks whether a skill still works, and KTL asks who stands behind a claim.

# What KTL took from it

Reading the paper in October 2026 changed the skills in four places, which `CHANGELOG.md` lists:

- **A program counts reliance.** `knowledge-report.sh` prints how many other concepts rely on each one through a typed relation, and ranks *Worth ten minutes today*, the curator's queue, which `ktl-curator` quotes.
- **A retired concept names what replaced it.** `ktl-curator` links the successor in the concept's `**Deprecation**` line in `log.md`, and the report's label reads *retired, replaced by* that path. The log holds the link until LOKF has a relation type for a successor, which nicholsn/lokf#112 asks for.
- **A reader's dispute shows on the concept.** Until the librarian handles a docent's Disagreement, the concept's label adds *a reader disputed this* and the day.
- **A confirming commit records the verdict.** Conventions rule 14 reads each commit of a pull request. A commit that records a person's confirmation may change what the concept says only when that person is also recorded as its author.

One more waits for LOKF 0.9.0, whose `sources[].excerpt` lets a program check the exact passage a concept relies on against its source.

# Where the designs part

- **Who stands behind a decision.** SkillWiki records each transition with `author="repository"`, and the paper says its governance workflow "can operate fully autonomously". KTL records a verdict only for a person the forge can name.
- **What a state names.** SkillWiki stores a skill's state. KTL stores no label: `knowledge-report.sh` computes each one from the events.
- **Scores and signals.** SkillWiki attaches a `confidence` number. KTL records a named person's verdict where SkillWiki has a number.
- **A declined proposal.** SkillWiki can raise a rejected proposal again. The librarian proposes nothing again from a pull request a person closed without merging, until the source moves or a reader asks again.
