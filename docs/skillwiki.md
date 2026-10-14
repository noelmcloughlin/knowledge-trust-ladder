# What KTL took from SkillWiki

> [!NOTE]
> What Knowledge Trust Ladder (KTL) took from one paper and its code, and where the two designs part. SkillWiki is not WikiSkill, the Google Research paper that [docs/wikiskill.md](wikiskill.md) covers. The code is cited at commit `050d540`.

*SkillWiki: A Living Knowledge Infrastructure for Agent Skills* (Huang et al., Harbin Institute of Technology, Tencent and Nanyang Technological University, June 2026) turns trajectories, documents, API specifications, scripts and earlier skills into skills. It governs them through a lifecycle of eight stored states, a provenance graph and feedback from their runs. A SkillWiki skill is executable: an interface, an implementation, tests, an evaluation contract and runtime metrics. A KTL concept is a claim about a repository, with the sources it rests on. So SkillWiki asks whether a skill still works, and KTL asks who stands behind a claim. Below, *the bundle* is the corpus KTL keeps in `.lokf/knowledge/`.

## What KTL took from it

Reading the paper beside this repository in October 2026 changed the skills in four places, and the [changelog](../CHANGELOG.md) lists them.

- **A program counts reliance.** SkillWiki computes from its typed edges which skills a change reaches. `knowledge-report.sh` reads every typed relation in the bundle and prints how many other concepts rely on each one, the review dates due within 30 days, and each confirmed concept derived from one edited after that confirmation. It ranks *Worth ten minutes today*, the curator's queue, and `ktl-curator` quotes that queue, so no model counts or sorts it.
- **A retired concept names what replaced it.** A deprecated SkillWiki skill carries a `replacement_skill_id`. When a person retires a concept, `ktl-curator` asks what replaced it and links the successor in the concept's `**Deprecation**` line in `log.md`. The report's label then reads *retired, replaced by* that path, and the docent opens the successor before it falls back to the repository. The log holds the link until LOKF has a relation type for a successor, which [nicholsn/lokf#112](https://github.com/nicholsn/lokf/issues/112) asks for.
- **A reader's dispute shows on the concept.** SkillWiki defines a *Degraded* state for a released skill that keeps failing while it stays usable. A docent's Disagreement can name the concept it disputes, and until the librarian handles the entry the concept's label adds *a reader disputed this* and the day. The report reads the path from the entry and never its text.
- **A confirming commit records the verdict.** SkillWiki's structured diff sorts a change by what it touches before review. KTL's conventions rule 14 reads each commit of a pull request. A commit that records a person's confirmation may change what the concept says only when that person is also recorded as its author, as *Correct now* records them.

One more waits for LOKF 0.9.0. SkillWiki's verifier specs check an output by program. LOKF 0.9.0 adds `sources[].excerpt`, the exact passage a concept relies on, and a program can then check that passage against its source. Today the work list knows that a source file moved, and only reading it says whether the passage did.

## Where the designs part

- **Who stands behind a decision.** SkillWiki records each transition with `author="repository"`, and the paper says its governance workflow "can operate fully autonomously". KTL records a verdict only for a person the forge can name. `ktl-curator` stops in a session it cannot tell is live, and the registrar's `provenance` job asks for that person's approval or signature on the pull request.
- **What a state names.** A SkillWiki skill stores its state. KTL stores no label. `knowledge-report.sh` computes each one from the events, and the words say what checked a concept: *checked by automation only*, or *confirmed by a person*.
- **Scores and signals.** SkillWiki attaches a `confidence` number to its edges, its candidates and its proposals. LOKF's schema says that "OKF stores signals, never a score", and KTL records a named person's verdict where SkillWiki has a number.
- **A declined proposal.** SkillWiki compares a new maintenance proposal with the pending ones, so a rejected proposal can be raised again. The librarian proposes nothing again from a pull request a person closed without merging, until the source moves or a reader asks again.

## Sources

- Huang, D., Ding, Y., Liu, B., Liu, Q., Chen, X., Bian, J., Sun, H., Tu, Z., Chu, D., Yu, X. and Sui, D. (2026). SkillWiki: A Living Knowledge Infrastructure for Agent Skills. arXiv:2606.16523. <https://arxiv.org/abs/2606.16523>
- SkillWiki's source code at commit `050d540`. <https://github.com/Huangdingcheng/SkillWiki/tree/050d540215374f73cf295c410a8beb4415f7c128>
