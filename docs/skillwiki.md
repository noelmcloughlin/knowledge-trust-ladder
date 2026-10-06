# SkillWiki's skill governance and Knowledge Trust Ladder

> [!NOTE]
> A reading of one paper and its code against this design, for anyone deciding what Knowledge Trust Ladder (KTL) shares with SkillWiki and what it does with it. SkillWiki is not WikiSkill, the Google Research paper that [docs/wikiskill.md](wikiskill.md) reads. The paper is quoted from its own text, and the code is cited at commit `050d540`.

*SkillWiki: A Living Knowledge Infrastructure for Agent Skills* (Huang et al., Harbin Institute of Technology, Tencent and Nanyang Technological University, June 2026) turns trajectories, documents, API specifications, scripts and earlier skills into skills. It governs them through a lifecycle, a provenance graph and feedback from their runs. KTL keeps a repository's knowledge as a bundle of concepts that an agent derives and a person confirms. Both keep what they hold as assets with a source and a history. Below, *KTL* is this design, *the bundle* is the corpus it keeps in `.lokf/knowledge/`, and *the skill repository* is SkillWiki's corpus.

The two keep different things. A SkillWiki skill is executable: an interface, an implementation, test cases, an evaluation contract and runtime metrics. A KTL concept is a claim about a repository, with the sources it rests on. So SkillWiki asks whether a skill still works, and KTL asks who stands behind a claim.

## The same parts, side by side

| Part | SkillWiki | KTL |
| --- | --- | --- |
| The sources | trajectories, documents, API specifications, scripts and earlier skills, which the paper keeps "as evidence sources" linked to each skill | the repository, which the bundle cites and never edits, and `questions.md`, the questions readers asked |
| The corpus | the skill repository: one record per skill version, with its interface, implementation, tests, evaluation contract, metrics and provenance | the bundle: one Markdown concept per file, with its sources, typed relations and trust events |
| Its conventions | Pydantic models, and a transition table over eight stored states, S0 to S7 | a LinkML schema, a JSON-LD context and a conventions script |
| The writer | an ingest pipeline and self-management agents, among them a builder, an auditor, a maintainer and a librarian, behind an HTTP API | the librarian, which writes the bundle only through `knowledge-apply.sh`, called *the pen* |
| The gate | an audit, a harness run of deterministic verifier specs, and an LLM reviewer that approves on its own at a score of 8.0 or more | the registrar's automation: `lokf validate --check-refs`, the conventions script and the `provenance` job |
| The record | an event log, a version list per skill, and git branches, tags and snapshots | `generated` and `verified` events, `log.md` and git. `knowledge-report.sh` computes every trust label on each read |
| The verdict | `skillwiki promote` and `skillwiki proposal accept` or `reject` | the curator's, a named person: confirm, correct, send back or retire, tied to that person's forge account |
| The consumer | runtime agents, which retrieve released skills | the docent, a museum's name for a guide, which answers from the bundle and writes nothing there |
| Evolution | success counts, reflection memory and failure signatures, which become maintenance proposals | readers' misses and disagreements in `feedback.md`, the `questions.md` ledger, and the librarian's scheduled refresh |
| Retirement | S6 *Deprecated*, with a reason and a replacement, then S7 *Archived* | `status: deprecated`, with the successor linked in `log.md` |
| The graph | typed edges between skills, and a graph of sources, skills, executions, validations and versions | typed relations in frontmatter, which the JSON-LD context projects to RDF |

## What KTL does with it

Reading the paper beside this repository in October 2026 changed the skills in four places, and the [changelog](../CHANGELOG.md) lists them.

**A program counts reliance.** SkillWiki computes from its typed edges which skills a change reaches. `knowledge-report.sh` reads every typed relation in the bundle and prints how many other concepts rely on each one, counting each citing concept once. It also prints the review dates due within 30 days, and each confirmed concept derived from one edited after that confirmation. It ranks *Worth ten minutes today*, the curator's queue, and `ktl-curator` quotes that queue, so no model counts or sorts it.

**A retired concept names what replaced it.** A deprecated SkillWiki skill carries a `replacement_skill_id`. When a person retires a concept, `ktl-curator` asks what replaced it and links the successor in the concept's `**Deprecation**` line in `log.md`. The report's label then reads *retired, replaced by* that path, and the docent opens the successor before it falls back to the repository. Until LOKF has a relation type for a successor, which [nicholsn/lokf#112](https://github.com/nicholsn/lokf/issues/112) asks for, the log holds the link.

**A reader's dispute shows on the concept.** SkillWiki's S5 *Degraded* marks a released skill that keeps failing, and the skill stays usable. A docent's Disagreement can name the concept it disputes. Until the librarian handles the entry, the concept's label adds *a reader disputed this* and the day. The report reads the path from the entry and never its text.

**A confirming commit records the verdict.** SkillWiki's structured diff sorts a change by what it touches before review: schema, postconditions, dependencies, implementation, provenance or metadata. KTL's conventions rule 14 reads each commit of a pull request. A commit that records a person's confirmation may change what the concept says only when that person is also recorded as its author, as *Correct now* records them.

One more waits for LOKF 0.9.0. SkillWiki's verifier specs check an output by program. LOKF 0.9.0 adds `sources[].excerpt`, the exact passage a concept relies on, and a program can then check that passage against its source. Today the work list knows that a source file moved, and only reading it says whether the passage did.

## Where the designs differ

**Who stands behind a decision.** `skillwiki promote` sends only the target state, and the skill repository records each transition with `author="repository"` (`layers/skill_repository/repository.py`). The route that accepts a maintenance proposal is documented as "accepted by a human reviewer", and it takes only the proposal's id. SkillWiki's own `skillwiki-manage` skill shows an agent how to run both. The paper says the governance workflow "can operate fully autonomously", and that "User decisions always take precedence over autonomous governance actions." KTL records a verdict only for a person the forge can name. `ktl-curator` stops in a session it cannot tell is live, and the registrar's `provenance` job asks for that person's approval or signature on the pull request.

**What a state names.** A SkillWiki skill stores its state, and `skillwiki verify` promotes a draft to S3 *Verified* when the harness passes. KTL stores no label. `knowledge-report.sh` computes each one from the events, and the words say what checked a concept: *checked by automation only*, or *confirmed by a person*.

**Where a check's input comes from.** SkillWiki's harness runs test cases from the caller in place of a skill's own, and its deterministic repair fills a missing output field from the test input (`layers/skill_runtime/harness/verifier_loop.py`). KTL's retrieval score reads what it expects from the ledger, in a file of its own, and reads the agent's reply only for answers.

**A declined proposal.** SkillWiki compares a new maintenance proposal with the pending ones, so a rejected proposal can be raised again. KTL's scheduled workflow reads the pull requests a person closed without merging, and the librarian proposes none of their changes again until the source moves or a reader asks again.

**Scores and signals.** SkillWiki attaches a `confidence` number to its edges, its candidates and its proposals. LOKF's schema describes a source's credibility fields as signals, and says that "OKF stores signals, never a score". KTL records a named person's verdict where SkillWiki has a number.

## Where each design puts the program, the model and the person

| | SkillWiki | KTL |
| --- | --- | --- |
| Programs | the transition table, the deterministic verifiers, the structured diff, the health thresholds and the git store | the schema and the JSON-LD context, the conventions script, the pen, the registrar's gate and its `provenance` job, and the report script |
| Models | the ingest extractors, the builder, the reviewer, the repair step, and the coding agent the harness runs | the librarian, the docent and the optional prose pass |
| People | whoever runs `promote` or accepts a proposal; the record names the repository | the curator, whose verdict the gate ties to them |

## What the paper does not settle

- How the governance scales. The authors write that its behaviour "in substantially larger repositories containing tens of thousands of skills has not yet been systematically evaluated".
- Whether governed skills help an agent. Their evaluation "primarily measures the effectiveness of the proposed infrastructure and governance workflow, rather than the downstream impact".
- What *governed* counts. Table 1 reports 99 candidates and 99 governed skills from 125 artifacts, and the text calls them "governed skill candidates".
- Who stands behind a release. The record names the repository, not a person.

## Sources

- Huang, D., Ding, Y., Liu, B., Liu, Q., Chen, X., Bian, J., Sun, H., Tu, Z., Chu, D., Yu, X. and Sui, D. (2026). SkillWiki: A Living Knowledge Infrastructure for Agent Skills. arXiv:2606.16523. <https://arxiv.org/abs/2606.16523>
- SkillWiki's source code at commit `050d540`. <https://github.com/Huangdingcheng/SkillWiki/tree/050d540215374f73cf295c410a8beb4415f7c128>
