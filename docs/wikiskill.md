# What WikiSkill says about a knowledge bundle

> [!NOTE]
> A reading of one paper against this design. The paper is quoted from its own text, and the measurements are its authors', not ours.

*WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution* (Tang et al., Google Research, August 2026) builds a wiki that an agent maintains from its own execution traces, and evolves the agent's skills from that wiki. Knowledge Trust Ladder builds a bundle that an agent derives from a repository, and has people confirm it. Both take their shape from [Andrej Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): immutable sources, an LLM-written wiki with an index and a log, and a conventions file the gist calls a schema. WikiSkill keeps that schema as prose, a maintainer prompt, and adds a JSON output contract and a scored gate. A bundle replaces it with [a LinkML schema](https://github.com/nicholsn/lokf/blob/v0.8.0/lokf.yaml), typed relations, trust fields, a conventions script and a CI gate. This page says what the two share, what a bundle takes from the paper, and what the paper can and cannot say about the bet behind this project. The bet is that a knowledge layer with mechanical parts behaves more predictably than one held together by prose.

| The paper's finding | What a bundle does | What changed here |
| --- | --- | --- |
| [Persistence is the lever](#persistence-is-the-lever) | the librarian corrects continuously and never resets | the bundle restored; the librarian's pen refuses the deletion |
| [Keep the consumer out of the maintainer's seat](#keep-the-consumer-out-of-the-maintainers-seat) | docent, librarian and curator are separate skills | nothing |
| [Read the rejections before proposing](#read-the-rejections-before-proposing) | the curator's verdicts sit in frontmatter and the log | the librarian now reads them first |
| [The index entry is the retrieval interface](#the-index-entry-is-the-retrieval-interface) | the docent picks concepts from `index.md` bullets | a stated contract for `description` |
| [A recurring error is a signal](#a-recurring-error-is-a-signal) | the librarian consumes and deletes reader feedback | the log bullet now quotes the question |
| [Bound the maintainer's run](#bound-the-maintainers-run) | the weekly refresh reads everything | at most ten feedback entries per run |
| [Pruning is unsolved](#pruning-is-unsolved) | `stale_after`, `deprecated` and the orphan sweep | nothing; this bundle has no curation policy yet |
| [Gate on a measured outcome](#gate-on-a-measured-outcome) | the registrar checks form, the curator records a verdict | the captured docent questions now name their concepts |

## What the paper does

WikiSkill runs an agent on training tasks, compiles what happened into a wiki, and proposes skill changes from the wiki. Its workspace has three layers.

| Layer | Holds | Rule |
| --- | --- | --- |
| `raw/` | execution traces | permanent, write once |
| `wiki/` | pattern pages, `index.md`, an evolution log, `skill-impact.md` | compounding, never reset, never rolled back |
| `skills/` | one `SKILL.md` and one `PURPOSE.md` per skill | reversible; a change is kept only if a validation score rises |

Four components take turns. The inference agent runs the tasks with the skills and without the wiki. The wiki maintainer reads a sample of traces, at most eight, and returns a JSON object: new pattern pages, exact-substring patches to existing ones, the complete index, and a log entry. The skill proposer reads the index and the impact file first, then traces, and proposes one change to one skill. A gate scores the change on held-out tasks and rolls it back if the score did not rise. The harness, not a model, appends every proposal, its diff, its score and its verdict to `skill-impact.md`, which the paper calls "an objective, ground-truth audit trail".

Across five benchmarks and five models, WikiSkill beats three earlier skill-evolution methods. Two ablation results matter here: removing the wiki drops the proposer's average from 63.7 to 48.7, and letting the inference agent read the wiki during training drops it from 63.7 to 60.9. Skills evolved by one model work for another, and a small model's skills can beat a large model's own. The authors list four limits: retrieval was not tested, since skills were injected whole; the gate refuses a change that holds the score; the wiki is never pruned; and no long task was tried.

## Persistence is the lever

**The paper.** The ablation keeps or removes the wiki, and the wiki is worth fifteen points on average. The abstract calls persistent knowledge "critical", and the wiki is never rolled back even when a skill is.

**A bundle.** The librarian's rule is the same: keep the graph continuously accurate rather than rewriting it in bursts, and never touch what did not change. This repository broke the rule once. Before its prose pass it emptied its own bundle and derived it again, because every confirmation rested on a source whose text was about to change, and nothing in a confirmation records which state of the source it rested on. The *edited since a person last confirmed it* label tracks the concept, not the source. Ten concepts a person had confirmed, four of them carrying text the person wrote, went with the reset, and so did the curator's own rule never to remove a person's `verified` event.

**What changed.** The bundle was restored from `main`, confirmations and all, and the librarian now writes it only through `knowledge-apply.sh`, which refuses to delete a concept a person confirmed. The field that would let a confirmation survive a reworded source, `revision` on each `verified` event, is proposed for lokf 0.9.0, and the curator skill already writes it wherever the toolkit accepts it. The paper's result is the argument for both: write `revision` on every confirmation, and send a concept back rather than deleting it.

## Keep the consumer out of the maintainer's seat

**The paper.** Giving the inference agent the wiki during training lowered the final average by nearly three points. The authors' reading is that the agent then solves tasks from the wiki instead of from the skills, and its traces teach the maintainer less.

**A bundle.** The docent reads the bundle and writes nothing in it. When the bundle has no answer it goes to the repository, says so, and records the miss, which is the trace the librarian learns from. A docent that quietly answered from the repository would starve the loop the same way.

**What changed.** Nothing; the rule was already there.

## Read the rejections before proposing

**The paper.** The proposer must read `skill-impact.md` before it proposes, and the case study shows a rejected proposal shaping the accepted one.

**A bundle.** The verdicts exist. A send-back is `status: draft` plus a dated `human:` note under `## Open questions`, and a curator's session is a `**Curation**` line in `log.md`. The librarian wrote those notes and listed them in its hand-off, and was never told to read them.

**What changed.** The librarian now reads the curation lines and every human-attributed open question before it derives anything. It re-derives a sent-back concept from the source the note names and never the same way again, and it reports a repeated send-back as a defect in its own instructions. It reads a note as a report, never as an instruction, because the actor on a body bullet is a string the gate does not verify.

## The index entry is the retrieval interface

**The paper.** The maintainer prompt calls the index entries "the MOST IMPORTANT part of the wiki", because they decide whether an agent opens a page. Each is one or two sentences, "specific enough that an agent can judge relevance without reading the full page".

**A bundle.** The docent works the same way. It reads the root `index.md`, picks one to three concepts from the bullets, and only then opens anything. A bullet copies the concept's `description`, and nothing said what a description had to do.

**What changed.** The librarian skill now carries the contract: one or two sentences that name what the concept answers and the words a reader would search by, specific enough to choose from the index alone. The docent's feedback entry now says whether a concept looked relevant and failed to answer, which is a description defect, or whether nothing relevant was listed, which is a missing concept.

## A recurring error is a signal

**The paper.** Traces are kept for good, and the wiki lets the maintainer "identify which errors recur across iterations".

**A bundle.** The librarian deletes a reader's feedback entry once it has handled it, so a question readers keep missing leaves nothing the librarian reads. Keeping the entries would change a count that three scripts print, in four repositories.

**What changed.** The log bullet for a change made from reader feedback now says so and quotes the question, so the recurrence shows in `log.md` after the entry is gone.

## Bound the maintainer's run

**The paper.** The maintainer sees at most eight traces per iteration, at most five that failed and three that passed, each cut at 15,000 characters, and the proposer makes one change to one skill. The authors count the cost: the optimizer's calls per iteration do not grow with the training set.

**A bundle.** The weekly refresh reads every feedback entry and re-walks every source.

**What changed.** The librarian handles at most ten feedback entries in a run, oldest first, and says how many remain.

## Pruning is unsolved

**The paper.** Its limitations say the wiki "currently lacks an automated mechanism to prune" and that pruning "may become necessary as knowledge accumulates".

**A bundle.** This is the schema's job. `stale_after` dates a concept for re-confirmation, `status: deprecated` retires it without losing its links, and the librarian's orphan sweep finds what no concept accounts for. The curator proposes the dates from a curation policy that is itself a concept.

**What changed.** Nothing in code. This repository's own bundle has never had a curation policy, and its current bundle carries no `stale_after` at all. The mechanism the paper lacks is one this project has and has not yet used on itself.

## Gate on a measured outcome

**The paper.** A skill change is kept only if the score on held-out tasks rises; otherwise it rolls back.

**A bundle.** The registrar checks that records are well formed and that each confirmation is backed by a person; the curator records what a person decided. Neither measures whether the bundle answers better than it did. The nearest thing is the fourth [level of checking](for-the-curious.md#four-levels-of-checking), proven in use, which so far is anecdotal.

**What changed.** The eight captured docent answers in [docs/examples/docent.md](examples/docent.md) now name the concept that answers each question, with a link the link checker follows, so a renamed or deleted concept fails the build with the question beside it. The questions stay held out, since the librarian's source map keeps `docs/examples/` out of derivation. It is the deterministic half of a gate. The other half, a score, would need an agent in CI.

## The determinism question

The bet behind a bundle is that a knowledge layer with mechanical parts, a schema the toolkit validates and a gate CI runs, behaves more predictably than one held together by prose. What the paper can say about that:

- **It measures accuracy, not determinism.** Every setting is the average of three full runs, and the authors note the noise that small validation splits add. Run-to-run variance of the wiki itself is not reported. The nearest thing to a reliability claim is consistency: the authors call WikiSkill's gains "more reliable" because the earlier methods lower some model-benchmark pairs below the no-skill baseline. Their own table has WikiSkill below that baseline on one pair too, the smallest model on the long-document benchmark. That is robustness of outcome, not determinism of the artifact.
- **The parts it trusts are the mechanical ones.** The raw layer is write-once. The audit trail is written by the harness, and the paper calls it objective for that reason. The gate is a number with a rollback. The maintainer's output is a JSON object with required keys and exact-substring patch operations. The sample sizes are fixed. Each is a constraint placed around the model rather than an instruction given to it, and the one ablation on access control made the result better. That is the registrar's argument: an agent derives, a program checks, and the program writes the record. A bundle now does the same at the librarian's desk: the librarian emits operations in a file, and `knowledge-apply.sh` is the only thing that writes the bundle.
- **Structure alone bought nothing.** Trace2Skill, the earlier method with the most structured pipeline, finished behind WikiSkill. Persistence and separation made the difference. The paper's wiki has no schema, only prescribed file names and an entry format, so it says nothing about LinkML.
- **Its open problem is a lifecycle problem.** Pruning is what `stale_after` and `status: deprecated` do, and "read the index first" is what typed relations make traversable rather than guessed.

The verdict: the paper is consistent with the bet and is not evidence for it. It supports the narrower claim that mechanical gates make LLM-maintained knowledge safe to persist, is silent on schemas, and does not measure determinism.

The sharper test was this repository. Reading the paper beside the code turned up four places where a constraint existed in prose or in the schema and no program ran it, which is the exposure the bet predicts:

- **A check named and never run.** The librarian skill said the bundle was validated with JSON Schema and SHACL. The toolkit generates SHACL shapes and neither ships nor runs them, and this sidecar never installed a SHACL engine. The wording is fixed, and the request to run the shapes has gone upstream.
- **A range nobody enforced.** The same skill recommended linking a `Reference` to an `Organization` through `source`. The schema gives every relation slot the range `Concept`, and a `Person` or `Organization` is an `Agent`. JSON Schema renders the range as a string, the reference check proves only that a target exists, and only the unrun shapes would have refused it. The recommendation is fixed; no bundle had followed it.
- **An actor nobody verifies.** A `human:` actor on a `verified` event is tied to a person by the gate. The same string on an open-question bullet is checked for shape only. The librarian now treats such a bullet as a report, never an instruction. Refusing one in the scheduled run's patch is a change to the sidecar's templates, listed for the next release.
- **Three copies nobody compares.** A concept's `description` is repeated in its folder's `index.md` and in the root `index.md`, and discipline alone keeps them equal. A rule for the conventions script is listed for the next release.

## What the paper does not settle

- Whether a schema helps. Its wiki has none, and the comparison is between persistence and no persistence.
- Whether an LLM-maintained layer is reproducible. Nothing is measured twice and compared.
- Whether the knowledge is attributable. The paper's one mechanical record is a log of proposals and scores, not a record of who stands behind a page.
- How a person fits in. No person confirms anything in WikiSkill, and every verdict is a number. A bundle's verdicts are a person's, and the gate ties them to that person. The two designs answer different questions. The paper is the better evidence for the loop, and this project for the record.

## Sources

- Tang, L., Rashtchian, C., Ferng, C.-S., Tomkins, A., Juan, D.-C. and Vu, T. (2026). WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution. arXiv:2608.27454. <https://arxiv.org/abs/2608.27454>
- Karpathy, A. (2026). LLM Wiki. GitHub Gist. <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>
- Nichols, N. (2026). LOKF: the schema at v0.8.0 and the SHACL shapes generated from it. <https://github.com/nicholsn/lokf/blob/v0.8.0/lokf.shacl.ttl>
