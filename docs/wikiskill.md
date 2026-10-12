# What KTL took from WikiSkill

> [!NOTE]
> What Knowledge Trust Ladder (KTL) took from one paper, and what the paper leaves open. WikiSkill is not SkillWiki, a 2026 paper on governing agent skills that [docs/skillwiki.md](skillwiki.md) covers.

*WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution* (Tang et al., Google Research, August 2026) has an agent compile its own execution traces into a wiki and evolves the agent's skills from it. KTL has an agent derive a bundle from a repository and has a person confirm it. Both take their shape from [Andrej Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): immutable sources, a corpus a model writes, an index a reader opens first, a log, and a conventions file.

The two run the same loop. A model maintains the corpus, a program applies its changes and keeps the record, a separate agent consumes the corpus without writing it, and a gate decides what stays. WikiSkill's gate is a validation score, with no person in the loop. KTL's gate is the registrar, and the verdict is a named person's. Below, *the bundle* is the corpus KTL keeps in `.lokf/knowledge/`.

## What KTL took from it

Reading the paper beside this repository in October 2026 changed the skills in these places, and the [changelog](../CHANGELOG.md) lists each change.

- **The consumer does not maintain the corpus.** Giving the inference agent the wiki during training lowered the paper's scores. The docent reads the bundle and writes nothing in it. When it has to go to the repository it says so and records the miss in `feedback.md`, which is what the librarian learns from.
- **The maintainer reads the rejections first.** The paper's proposer reads its record of rejected proposals before it proposes. The librarian reads the curator's verdicts before it derives anything: the `**Curation**` lines in `log.md` and every open question a person left. It re-derives a sent-back concept from the source the note names, never the same way again, and reports a repeated send-back as a defect in its own instructions.
- **A declined proposal is not proposed again.** A person declines the scheduled librarian's proposal by closing its pull request without merging. The workflow reads those pull requests before each scheduled run, so the librarian proposes none of their changes again until the source moves or a reader asks again. While a pull request is open, a scheduled run opens no second one beside it.
- **The index entry is the retrieval interface.** The paper's maintainer prompt calls the index entries "the MOST IMPORTANT part of the wiki". The docent reads `index.md`, picks one to three concepts from the bullets, and only then opens anything. A bullet copies the concept's `description`, the pen keeps the copies equal, and a miss on a question an existing concept already answers is a defect in that description, not a reason for a twin.
- **A recurring question is a signal.** The pen moves each feedback entry the librarian handles into `questions.md`, a ledger that only grows: the day, the concept that now answers it, and the reader's question. `knowledge-report.sh` counts it and names the concepts readers keep arriving at.
- **The maintainer's run is bounded.** The paper caps what a maintainer reads per iteration, and a program does the sampling. The librarian starts from a work list `knowledge-report.sh` computes: the concepts whose source has moved since their `generated` stamp or latest check, ordered by history and never by a clock. A run handles at most ten feedback entries, oldest first, and says how many remain. A scheduled week in which nothing waits runs no agent, and the first run of each month goes ahead regardless, for the sources no program compares.
- **A measured outcome beside the gate.** The paper keeps a skill change only if a validation score rises. KTL's gate measures form and provenance, and a scheduled refresh can carry a retrieval score beside it. `knowledge-report.sh` has the agent choose, from `index.md` alone, the concepts it would open for each question in the ledger, and scores the reply by program. The pull request shows `n of m`, and a person decides, so a neutral change still merges.

Two things KTL already did, the paper's results support. Its ablation finds the persistent wiki worth fifteen points on average, kept even when a skill change is rolled back. The pen refuses to delete a concept a person confirmed, and a rewrite demotes the label to *edited since a person last confirmed it* without removing the record. The paper also lists pruning as unsolved. KTL dates a concept for re-confirmation with `stale_after`, retires it with `status: deprecated`, and finds what no concept accounts for with the librarian's orphan sweep.

## What the paper leaves open

The paper is evidence for the loop, not for the parts KTL adds. It runs no schema, derives nothing twice to test reproducibility, records no one behind a page, and has no person in the loop. Those are the questions this project exists to answer, and the bundle's own record is the evidence for them.

## Sources

- Tang, L., Rashtchian, C., Ferng, C.-S., Tomkins, A., Juan, D.-C. and Vu, T. (2026). WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution. arXiv:2608.27454. <https://arxiv.org/abs/2608.27454>
- Karpathy, A. (2026). LLM Wiki. GitHub Gist. <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>
