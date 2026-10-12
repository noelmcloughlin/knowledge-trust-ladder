---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/skillwiki
title: SkillWiki's skill governance and Knowledge Trust Ladder
description: "The SkillWiki paper (Huang et al., 2026) and its code set beside Knowledge Trust Ladder (KTL), as `docs/skillwiki.md` does: the same parts side by side, the four changes the reading made to the skills, where the two designs differ on who stands behind a decision, and what the paper does not settle. SkillWiki is not WikiSkill."
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
  at: "2026-10-12T00:29:45Z"
status: draft
---

# Overview

`docs/skillwiki.md` reads one paper and its code against KTL's design. The paper is *SkillWiki: A Living Knowledge Infrastructure for Agent Skills* (Huang et al., Harbin Institute of Technology, Tencent and Nanyang Technological University, June 2026). The page quotes the paper from its own text and cites the code at commit `050d540`. SkillWiki is not WikiSkill, the Google Research paper that [WikiSkill's loop](wikiskill.md) covers.

SkillWiki turns trajectories, documents, API specifications, scripts and earlier skills into skills. It governs them through a lifecycle, a provenance graph and feedback from their runs. The two designs keep different things. A SkillWiki skill is executable, and a KTL concept is a claim about a repository with the sources it rests on. So SkillWiki asks whether a skill still works, and KTL asks who stands behind a claim.

# The same parts

The page sets the two designs side by side part by part: the sources, the corpus, its conventions, the writer, the gate, the record, the verdict, the consumer, evolution, retirement and the graph. In SkillWiki a large language model (LLM) reviewer approves on its own at a score of 8.0 or more. In KTL the verdict is the curator's, a named person tied to that person's forge account.

# What KTL does with it

Reading the paper in October 2026 changed the skills in four places, which `CHANGELOG.md` lists:

- **A program counts reliance.** `knowledge-report.sh` prints how many other concepts rely on each one through a typed relation, and ranks *Worth ten minutes today*, the curator's queue, which `ktl-curator` quotes.
- **A retired concept names what replaced it.** `ktl-curator` links the successor in the concept's `**Deprecation**` line in `log.md`, and the report's label reads *retired, replaced by* that path. The log holds the link until LOKF has a relation type for a successor, which nicholsn/lokf#112 asks for.
- **A reader's dispute shows on the concept.** Until the librarian handles a docent's Disagreement, the concept's label adds *a reader disputed this* and the day.
- **A confirming commit records the verdict.** Conventions rule 14 reads each commit of a pull request. A commit that records a person's confirmation may change what the concept says only when that person is also recorded as its author.

One more waits for LOKF 0.9.0, whose `sources[].excerpt` lets a program check the exact passage a concept relies on against its source.

# Where the designs differ

- **Who stands behind a decision.** SkillWiki records each transition with `author="repository"`, and the paper says its governance workflow "can operate fully autonomously". KTL records a verdict only for a person the forge can name.
- **What a state names.** SkillWiki stores a skill's state. KTL stores no label: `knowledge-report.sh` computes each one from the events.
- **Where a check's input comes from.** SkillWiki's harness runs test cases from the caller. KTL's retrieval score reads what it expects from the ledger, in a file of its own.
- **A declined proposal.** SkillWiki can raise a rejected proposal again. The librarian proposes nothing again from a pull request a person closed without merging, until the source moves or a reader asks again.
- **Scores and signals.** SkillWiki attaches a `confidence` number. KTL records a named person's verdict where SkillWiki has a number.

# What the paper does not settle

The page names four open points:

- how the governance scales to tens of thousands of skills;
- whether governed skills help an agent downstream;
- what *governed* counts in the paper's Table 1;
- who stands behind a release, since the record names the repository and not a person.
