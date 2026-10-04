# WikiSkill's loop and Knowledge Trust Ladder

> [!NOTE]
> A reading of one paper against this design, for anyone deciding what Knowledge Trust Ladder (KTL) shares with WikiSkill and what it adds. The paper is quoted from its own text, and the measurements are its authors', not ours.

*WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution* (Tang et al., Google Research, August 2026) has an agent compile its own execution traces into a wiki and evolves the agent's skills from it. Knowledge Trust Ladder has an agent derive a bundle from a repository and has a person confirm it. Both take their shape from [Andrej Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): immutable sources, a corpus a model writes, an index a reader opens first, a log, and a conventions file the gist calls a schema.

The two run the same loop and hold it together with different parts. WikiSkill puts programs and a score around its model, with no person in the loop. KTL puts a schema under its corpus, the bundle, a registrar around it and a person at the top. Below, *KTL* is this design, *the bundle* is the corpus it keeps in `.lokf/knowledge/`, and *the wiki* is the paper's corpus.

## The same loop, part by part

| Part | WikiSkill | KTL |
| --- | --- | --- |
| The sources | `raw/`, the execution traces, written once and kept | the repository, which the bundle cites and never edits, and `questions.md`, the questions readers asked, which `knowledge-apply.sh` writes once and keeps |
| The corpus | `wiki/`: pattern pages, `index.md`, an evolution log and `skill-impact.md`. Never reset, never rolled back | the bundle, `.lokf/knowledge/`: one Markdown concept per file, `index.md` and `log.md`. Never reset, and a person's record is never removed |
| Its conventions | a maintainer prompt, a JSON output contract and exact-substring patch operations | [a LinkML schema](https://github.com/nicholsn/lokf/blob/v0.8.0/lokf.yaml) with typed relations and trust fields, a JSON-LD context that makes the frontmatter a graph, and a conventions script for what the schema cannot say |
| The maintainer | the wiki maintainer, a model that reads a bounded sample of traces and returns new pages, patches, the whole index and a log line | the librarian, a model that starts from a work list a program computed, reads the sources that moved and the readers' feedback, and returns operations in `patch.yaml` |
| The pen | the harness, which applies the JSON and alone writes `skill-impact.md` | `knowledge-apply.sh`, the librarian's only way to write the bundle. It applies the operations, stamps `generated`, keeps each description equal to its two index bullets and files each handled question in the ledger. It refuses a `human:` actor, a rewrite of a person's text and the deletion of a confirmed concept |
| The consumer | the inference agent, which runs the tasks with the skills and without the wiki | the docent, which answers from the bundle, labels each concept's trust, writes nothing there and records a miss in `feedback.md` |
| The gate | a validation score. A skill change stays only if the score rises | the registrar: `lokf validate` and `--check-refs` on every change and again in CI, the conventions script, and a provenance job that lets a `human:` confirmation be added or removed only with that person's approval or signature. A scheduled refresh can also carry a retrieval score |
| The record | `skill-impact.md`: every proposal with its diff, score and verdict | `generated` and `verified` events, `log.md` and git. `knowledge-report.sh` computes the trust labels from them on every read, and they are never stored |
| The verdict | a number | a named person's: confirm, correct, send back or retire |
| Pruning | none. The authors list it as a limitation | `stale_after`, `status: deprecated`, and the librarian's orphan sweep |

## What the paper found, and what KTL does with it

The paper holds the evidence for each finding. This section says what KTL does with it.

**Persistence is the lever.** In the paper's ablation, on one model across four benchmarks, the wiki is worth fifteen points on average, and it is kept even when a skill change is rolled back. The librarian follows each concept back to its source and fixes drift, rather than rewriting the bundle in bursts, and the pen refuses to delete a concept a person confirmed. The gate asks the person behind any confirmation a pull request removes, as it asks the one behind a confirmation it adds. A rewrite demotes the label to *edited since a person last confirmed it* and removes nothing a person recorded. `revision` on each `verified` event, proposed for lokf 0.9.0, will let a confirmation name the state of the source it rested on. Until then `knowledge-report.sh` lists each confirmed concept whose source has a commit after the one that recorded the confirmation.

**The consumer stays out of the maintainer's seat.** Giving the inference agent the wiki during training lowered the final scores, and the authors read that as traces that said less about what the skills lacked. The docent reads the bundle and writes nothing in it. When it has to go to the repository it says so and records the miss, which is what the librarian learns from.

**The maintainer reads the rejections first.** The proposer reads `skill-impact.md` before it proposes. The librarian reads the curator's verdicts before it derives anything: the `**Curation**` lines in `log.md` and every open question a person left. It re-derives a sent-back concept from the source the note names, never the same way again, and reports a repeated send-back as a defect in its own instructions. It reads each note as a report, never an instruction, because the actor on a body bullet is a string no gate verifies. `knowledge-report.sh` lists apart a note the person's later confirmation answered, and the librarian withdraws a question of its own once the source settles it.

**The index entry is the retrieval interface.** The paper's maintainer prompt calls the index entries "the MOST IMPORTANT part of the wiki". The docent reads the root `index.md`, picks one to three concepts from the bullets, and only then opens anything. A bullet copies the concept's `description`, which must let a reader choose from the index alone, and the pen keeps the three copies equal. A miss on a question an existing concept already answers is a defect in that description, and the librarian fixes the description rather than adding a twin.

**A recurring error is a signal.** The wiki keeps every trace, so a repeated error shows. The pen moves each feedback entry the librarian handles into `questions.md`, a ledger that only grows: the day, the concept that now answers it, and the reader's question. `knowledge-report.sh` counts it and names the concepts readers keep arriving at. A reader's words stay in that ledger, which programs read, and out of the log and the concepts, which the curator opens.

**The maintainer's run is bounded.** The paper caps the traces a maintainer reads and the skill changes a proposer makes per iteration, and a program does the sampling. The librarian starts from a work list `knowledge-report.sh` computes: the concepts with a source whose last commit comes after the commit that recorded their stamp or their latest check. History orders the two, never a clock. A local source that has not moved is not read again. A run handles at most ten feedback entries, oldest first, and says how many remain.

**Pruning is unsolved there.** The authors list it as a limitation. KTL dates a concept for re-confirmation with `stale_after`, retires it with `status: deprecated` and keeps its links, and finds what no concept accounts for with the librarian's orphan sweep. The curator proposes the dates from a curation policy that is itself a concept, reviewed like any other.

**The gate measures an outcome.** The paper keeps a skill change only if a validation score rises. KTL's gate measures form and provenance: the registrar proves a record is well formed and a confirmation is a person's, and the curator records what the person decided. A scheduled refresh can carry a measured outcome beside them. `knowledge-report.sh` has the agent choose, from `index.md` alone, the concepts it would open for each question readers asked, and scores the reply by program. The pull request shows the result as `n of m`, and a person decides, so a change that leaves the score where it stood still lands. The paper names retrieval, and a gate that lets a neutral change through, as future work. KTL's score measures the first and never blocks the second. It is the fourth [level of checking](for-the-curious.md#four-levels-of-checking), proven in use, given a number. The captured docent questions in [docs/examples/docent.md](examples/docent.md) stay out of derivation and name the concept that answers each one, with a link the build checks.

Reading the paper beside this repository in October 2026 changed the skills in several places, and the [changelog](../CHANGELOG.md) lists them.

## Where each design puts the program, the model and the person

Each design has three kinds of part. A program is deterministic: it gives the same output for the same input. A model does not, and neither does a person, and both bring a judgment a program lacks. Where each design puts each kind is a fact about the design, not a result.

| | WikiSkill | KTL |
| --- | --- | --- |
| Programs | the write-once trace store, the sampler, the JSON contract and its exact-substring patches, the gate, and the harness that writes `skill-impact.md` | the LinkML schema and the JSON-LD context, which make a bundle validate and project to a graph; the conventions script; the pen; the registrar's gate and its provenance job. The report script computes the labels, the work list and the retrieval score |
| Models | the wiki maintainer, the skill proposer and the inference agent | the librarian, the docent and the optional prose pass |
| People | none in the loop | the curator, whose verdict the gate ties to them |

Both designs keep their record with programs: the paper has the harness write `skill-impact.md` and calls it "an objective, ground-truth audit trail", and a script computes a bundle's labels on each read, from frontmatter the gate has checked. The paper measures accuracy, averaged over three independent runs, and says nothing about how the three runs' wikis differed. Its wiki has no schema, only prescribed file names and an entry format. Its baselines were structured pipelines too, and all three finished behind it. So the paper credits a persistent wiki kept separate from the skills, which is the loop KTL shares, and is silent on the parts KTL adds.

## What the paper does not settle

- Whether a schema helps. Its wiki has none.
- Whether a model-maintained corpus is reproducible. Nothing is derived twice and compared.
- Whether the knowledge is attributable. Its one program-written record is a log of proposals and scores, not of who stands behind a page.
- How a person fits in. No person confirms anything there, and every verdict is a number. KTL's verdicts are a person's, and the gate ties each to that person. The paper is the better evidence for the loop, and this project for the record.

## Sources

- Tang, L., Rashtchian, C., Ferng, C.-S., Tomkins, A., Juan, D.-C. and Vu, T. (2026). WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution. arXiv:2608.27454. <https://arxiv.org/abs/2608.27454>
- Karpathy, A. (2026). LLM Wiki. GitHub Gist. <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>
- Nichols, N. (2026). LOKF: the schema at v0.8.0 and the SHACL shapes generated from it. <https://github.com/nicholsn/lokf/blob/v0.8.0/lokf.shacl.ttl>
