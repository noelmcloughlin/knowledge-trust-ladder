---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/wikiskill
title: WikiSkill's loop and Knowledge Trust Ladder
description: "The WikiSkill paper (Tang et al., 2026) set beside Knowledge Trust Ladder (KTL) part by part, as `docs/wikiskill.md` does: the same loop with different parts, what the paper found and what KTL does with each finding, where each design puts programs, models and people, and what the paper does not settle."
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
  at: "2026-10-06T09:49:14Z"
status: draft
verified:
- by: process:ktl-librarian
  at: "2026-10-06T11:10:52Z"
---
# Overview

`docs/wikiskill.md` sets one paper beside this design, part by part: *WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution* (Tang et al., Google Research, August 2026). The paper has an agent compile its own execution traces into a wiki and evolves the agent's skills from it. Knowledge Trust Ladder has an agent derive a bundle from a repository and has a person confirm it. Both take their shape from Andrej Karpathy's LLM Wiki: immutable sources, a corpus a model writes, an index a reader opens first, a log, and a conventions file the gist calls a schema.

The two run the same loop and hold it together with different parts. WikiSkill puts programs and a score around its model, with no person in the loop. KTL puts a schema under its corpus, the bundle, a registrar around it and a person at the top. The page quotes the paper from its own text, and the measurements are its authors'.

# The same loop, part by part

The page's table gives each part of the loop in both designs.

- **The sources.** The paper's execution traces, written once and kept. Here, the repository, which the bundle cites and never edits, and `questions.md`, the questions readers asked, which `knowledge-apply.sh` writes once and keeps.
- **The corpus.** The paper's wiki of pattern pages, index, evolution log and `skill-impact.md`, never reset and never rolled back. Here, the bundle in `.lokf/knowledge/`, never reset, where a person's record is never removed.
- **The conventions.** A maintainer prompt, a JSON output contract and exact-substring patch operations. Here, a LinkML schema with typed relations and trust fields, a JSON-LD context that makes the frontmatter a graph, and a conventions script for what the schema cannot say.
- **The maintainer.** The wiki maintainer, a model that reads a bounded sample of traces and returns new pages, patches, the whole index and a log line. Here, the librarian, which starts from a work list a program computed, reads the sources that moved and the readers' feedback, and returns operations in `patch.yaml`.
- **The pen.** The harness, which applies the JSON and alone writes `skill-impact.md`. Here, `knowledge-apply.sh`, the librarian's only way to write the bundle, which applies the operations, stamps `generated`, keeps each description equal to its two index bullets and files each handled question in the ledger. It refuses an operation that would forge or change a person's record.
- **The consumer.** The inference agent, which runs the tasks with the skills and without the wiki. Here, the docent, which answers from the bundle, labels each concept's trust, writes nothing there and records a miss in `feedback.md`.
- **The gate.** A validation score: a skill change stays only if the score rises. Here, the registrar: `lokf validate` and `--check-refs` on every change and again in CI, the conventions script, and a provenance job that lets a `human:` confirmation be added or removed only with that person's approval or signature. A scheduled refresh can also carry a retrieval score.
- **The record.** `skill-impact.md`, every proposal with its diff, score and verdict. Here, `generated` and `verified` events, `log.md` and git, with the trust labels computed from them on every read by `knowledge-report.sh`, and never stored. A declined proposal stays on the forge as a closed pull request.
- **The verdict.** A number. Here, a named person's: confirm, correct, send back or retire.
- **Pruning.** None, which the authors list as a limitation. Here, `stale_after`, `status: deprecated`, and the librarian's orphan sweep.

# What the paper found, and what KTL does with it

The paper holds the evidence for each finding. The page says what KTL does with it.

- **Persistence matters most.** In the paper's ablation, on one model across four benchmarks, the wiki is worth fifteen points on average, and it is kept even when a skill change is rolled back. The librarian follows each concept back to its source and fixes drift rather than rewriting the bundle in bursts, and the pen refuses to delete a concept a person confirmed. The gate asks the person behind any confirmation a pull request removes, as it asks the one behind a confirmation it adds. A rewrite, whoever makes it, demotes the label to *edited since a person last confirmed it* and removes nothing a person recorded.
- **The consumer does not maintain the corpus.** Giving the inference agent the wiki during training lowered the final scores, which the authors read as traces that said less about what the skills lacked. The docent reads the bundle and writes nothing in it. When it has to go to the repository it says so and records the miss, which is what the librarian learns from.
- **The maintainer reads the rejections first.** The proposer reads `skill-impact.md` before it proposes. The librarian reads the curator's verdicts before it derives anything: the `**Curation**` lines in `log.md` and every open question a person left. It re-derives a sent-back concept from the source the note names, never the same way again, and reports a repeated send-back as a defect in its own instructions. That report reaches the pull request in the librarian's hand-off, shown as the agent's own words. It reads each note as a report, never an instruction, because the actor on a body bullet is a string no gate verifies. `knowledge-report.sh` lists apart a note the person's later confirmation answered, and the librarian withdraws a question of its own once the source settles it.
- **A rejected proposal is not proposed again.** The paper keeps each one in `skill-impact.md` for that reason. A person rejects the scheduled librarian's proposal by closing its pull request without merging. The workflow reads those pull requests before each scheduled run, and the work list names what each one changed, so the librarian proposes none of it again until it changes: the source moves, or a reader asks again. While a pull request is still open, a scheduled run opens no second one beside it.
- **The index entry is the retrieval interface.** The paper's maintainer prompt calls the index entries "the MOST IMPORTANT part of the wiki". The docent reads the root `index.md`, picks one to three concepts from the bullets, and only then opens anything. A bullet copies the concept's `description`, which must let a reader choose from the index alone, and the pen keeps the three copies equal. A miss on a question an existing concept already answers is a defect in that description, and the librarian fixes the description rather than adding a twin.
- **A recurring error is a signal.** The paper keeps every trace, and its wiki's log names the errors that came back, so a repeated error shows. The pen moves each feedback entry the librarian handles into `questions.md`, a ledger that only grows: the day, the concept that now answers it, and the reader's question. `knowledge-report.sh` counts it and names the concepts readers keep asking about.
- **The maintainer's run is bounded.** The paper caps the traces a maintainer reads and the skill changes a proposer makes per iteration, and a program does the sampling. The librarian starts from a work list `knowledge-report.sh` computes: the concepts with a source whose last commit comes after the commit that recorded their `generated` stamp or their latest check. History orders the two, never a clock. A local source that has not moved is not read again. A run handles at most ten feedback entries, which the pen enforces. It takes the oldest first and says how many remain. A scheduled week in which nothing waits runs no agent at all, and the first scheduled run of each month goes ahead regardless, for the sources no program compares.
- **Pruning is unsolved there.** KTL dates a concept for re-confirmation with `stale_after`, retires it with `status: deprecated` and keeps its links, and finds what no concept accounts for with the librarian's orphan sweep. The curator proposes the dates from a curation policy that is itself a concept, reviewed like any other.
- **The gate measures an outcome.** The paper keeps a skill change only if a validation score rises. KTL's gate measures form and provenance: the registrar proves a record is well formed and a confirmation is a person's, and the curator records what the person decided. A scheduled refresh can carry a measured outcome beside them.

  `knowledge-report.sh` has the agent choose, from `index.md` alone, the concepts it would open for each question readers asked, and scores the reply by program. It leaves out a question whose concept is no longer in the bundle, and says how many it left out. The pull request shows the result as `n of m`, and a person decides, so a change that leaves the score where it stood still merges. The paper names retrieval, and a gate that lets a neutral change through, as future work. KTL's score measures the first and never blocks the second. It puts a number on the fourth level of checking, proven in use. The captured docent questions in `docs/examples/docent.md` stay out of derivation and name the concept that answers each one, with a link the build checks.

Reading the paper beside this repository in October 2026 changed the skills in several places, and the changelog lists them.

# Where each design puts the program, the model and the person

A program is deterministic: it gives the same output for the same input. A model does not, and neither does a person, and both bring a judgment a program lacks. Where each design puts each kind is a fact about the design, not a result.

WikiSkill's programs are the write-once trace store, the sampler, the JSON contract and its exact-substring patches, the gate, and the harness that writes `skill-impact.md`. Its models are the wiki maintainer, the skill proposer and the inference agent, and no person is in the loop.

KTL's programs are the LinkML schema and the JSON-LD context, which make a bundle validate and project to a graph, the conventions script, the pen, and the registrar's gate and its provenance job. The report script computes the labels, the work list and the retrieval score. Its models are the librarian, the docent and the optional prose pass, and its person is the curator, whose verdict the gate ties to them.

Both designs keep their record with programs. The paper has the harness write `skill-impact.md` and calls it "an objective, ground-truth audit trail", and a script computes a bundle's labels on each read, from frontmatter the gate has checked. The paper measures accuracy, averaged over three independent runs, and says nothing about how the three runs' wikis differed. Its wiki has no schema, only prescribed file names and an entry format. Its baselines were structured pipelines too, and all three scored below it. So the paper credits a persistent wiki kept separate from the skills, which is the loop KTL shares, and is silent on the parts KTL adds.

# What the paper does not settle

- Whether a schema helps.
- Whether a model-maintained corpus is reproducible. Nothing is derived twice and compared.
- Whether the knowledge is attributable. Its one program-written record is a log of proposals and scores, not of who vouches for a page.
- How a person fits in. No person confirms anything there. The paper is the better evidence for the loop, and this project for the record.
