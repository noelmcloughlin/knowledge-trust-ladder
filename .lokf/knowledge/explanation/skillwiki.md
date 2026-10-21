---
type: Explanation
id: https://w3id.org/ktl/knowledge/explanation/skillwiki
title: What KTL took from SkillWiki
description: "What Knowledge Trust Ladder (KTL) took from the SkillWiki paper (Huang et al., 2026) and its code: the four changes the reading made to the skills, the excerpt check that waits for LOKF 0.9.0, and where the two designs part, such as who stands behind a decision."
genre: explanation
resource: https://arxiv.org/abs/2606.16523
sources:
  - resource: https://arxiv.org/abs/2606.16523
  - resource: https://github.com/Huangdingcheng/SkillWiki/tree/050d540215374f73cf295c410a8beb4415f7c128
  - resource: CHANGELOG.md
  - resource: docs/for-the-curious.md
about:
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
relatedTo:
  - https://w3id.org/ktl/knowledge/explanation/wikiskill
  - https://w3id.org/ktl/knowledge/explanation/skills-repositories
  - https://w3id.org/ktl/knowledge/glossary/trust-label
  - https://w3id.org/ktl/knowledge/playbooks/ktl-curator-skill
generated:
  by: process:ktl-librarian
  at: "2026-10-19T23:21:13Z"
verified:
  - by: human:noelmcloughlin
    at: "2026-10-13T00:59:27Z"
  - by: process:ktl-librarian
    at: "2026-10-20T23:23:33Z"
  - by: human:noelmcloughlin
    at: "2026-10-19T12:28:10Z"
stale_after: 2027-04-19
status: draft
---

# Overview

*SkillWiki: A Living Knowledge Infrastructure for Agent Skills* (Huang et al., Harbin Institute of Technology, Tencent and Nanyang Technological University, June 2026, arXiv:2606.16523) is a paper with code, cited here at commit `050d540`. This concept records what Knowledge Trust Ladder (KTL) took from both, and where the two designs part. SkillWiki is not WikiSkill, the Google Research paper that [WikiSkill](wikiskill.md) covers.

SkillWiki turns trajectories, documents, API specifications, scripts, earlier skills and agent execution experience into skills. It governs them through a lifecycle of eight stored states, a provenance graph and feedback from their runs. A SkillWiki skill is executable, and a KTL concept is a claim about a repository with the sources it rests on. So SkillWiki asks whether a skill still works, and KTL asks who stands behind a claim.

# What KTL took from it

Reading the paper in October 2026 changed the skills in four places, which `CHANGELOG.md` lists:

- **A program counts reliance.** `knowledge-report.sh` prints how many other concepts rely on each one through a typed relation. It ranks the curator's queue, *Worth ten minutes today*, and `ktl-curator` quotes that queue.
- **A retired concept names what replaced it.** A deprecated SkillWiki skill carries a `replacement_skill_id`. `ktl-curator` links the successor in the concept's `**Deprecation**` line in `log.md`, and the report's label reads *retired, replaced by* that path, and the docent opens the successor before it falls back to the repository. The log holds the link until LOKF has a relation type for a successor, which nicholsn/lokf#112 asks for.
- **A reader's dispute shows on the concept.** SkillWiki defines a *Degraded* state for a released skill that keeps failing while it stays usable. Until the librarian handles a docent's Disagreement, the concept's label adds *a reader disputed this* and the day.
- **A confirming commit records the verdict.** SkillWiki's structured diff sorts a change by what it touches before review. Conventions rule 14 reads each commit of a pull request. A commit that records a person's confirmation may change what the concept says only when `generated.by` names that person.

One more change waits for LOKF 0.9.0. SkillWiki's verifier specs check an output by program, and LOKF 0.9.0's `sources[].excerpt` lets a program check the exact passage a concept relies on against its source.

Since 0.53.0, `docs/for-the-curious.md` holds what KTL took from the paper, under *How readers and verdicts steer the next run*, and `docs/skillwiki.md` is gone. `CHANGELOG.md` says this concept stays the record of the paper.

# Where the designs part

- **Who stands behind a decision.** SkillWiki records each transition with `author="repository"`, and the paper says that by default its governance workflow "can operate fully autonomously", though user decisions always take precedence. KTL records a verdict only for a person the forge can name.
- **What a state names.** SkillWiki stores a skill's state. KTL stores no label: `knowledge-report.sh` computes each one from the events.
- **Scores and signals.** SkillWiki attaches a `confidence` number. LOKF's schema says that "OKF stores signals, never a score", and KTL records a named person's verdict where SkillWiki has a number.
- **A declined proposal.** SkillWiki can raise a rejected proposal again. The librarian proposes nothing again from a pull request a person closed without merging, until the source moves, a person leaves a new note or a reader asks again.

## Open questions

- 2026-10-19, human:noelmcloughlin: refresh against sources.
