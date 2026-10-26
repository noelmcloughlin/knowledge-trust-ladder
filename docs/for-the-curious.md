# For the curious

This page is for anyone who wants the mechanics behind [the architecture](architecture.md), which helps decide whether to install these skills. It says who writes the bundle and what checks each write, exactly what "confirmed by a person" rests on, how readers and verdicts steer the next run, and what to do when a bundle outgrows the built-in vocabulary.

## Who writes the bundle, and what checks it

The librarian and the curator write to the bundle, each in one way only, and programs check every write. The docent writes nothing there.

- **The librarian**, an agent, writes one file: `.lokf/patch.yaml`, a list of operations. `knowledge-apply.sh` applies it, and is called *the pen* because the librarian writes the bundle only through it. The pen writes each concept, stamps `generated` from the clock, keeps the two index bullets equal to the concept's `description`, and files the line in `log.md`. It refuses an operation that would fake or change a person's record ([threat model](threat-model.md#repository-hardening)). On the scheduled run, the wrapper refuses a run in which the agent wrote any other file.
- **The curator**, a named person, writes the verdicts through `ktl-curator` or the KTL Curator plugin. A verdict is a `verified` event in that person's name, or a change of `status` or review date, with one line in `log.md`.
- **The docent**, an agent, writes nothing in the bundle. `knowledge-feedback.sh` records what a reader missed in `.lokf/feedback.md`, and the pen moves each entry the librarian handles into `.lokf/questions.md`.

On GitHub, every change is merged into the default branch through a pull request. On that pull request the registrar's gate, `knowledge-registrar.yaml`, runs `lokf validate`, the conventions script and the `provenance` job. That job accepts a `human:` event that a change adds or removes only with that person's approval of the pull request or their signature on the commit. On another forge, or with none, `knowledge-provenance.sh` checks each confirmation's signature against the keys under `.lokf/curators/` instead.

No trust label is stored: `knowledge-report.sh` computes each one from the frontmatter on every read, for the docent's answers, the curator's report and the librarian's work list. [The architecture](architecture.md#the-fifth-role-which-is-not-a-skill) draws the same writers and checks in one figure.

## Four levels of checking

Each proves less than its name suggests. Only the third yields a claim someone has agreed to vouch for.

| Check | Who, when | What it proves | What it can't |
| --- | --- | --- | --- |
| Schema-valid | the `lokf` toolkit on every change (`just lokf-validate`, and `just lokf-check-refs` for relation targets); `lokf validate` again as the CI gate on every pull request that touches the bundle | the frontmatter is well-formed, the types and relations are ones the schema knows, and every typed relation points at a concept that exists | that anything in it is true |
| Source-consistent | `ktl-librarian` on every scheduled refresh, starting from the sources `knowledge-report.sh` finds have moved; shown as *checked by automation only* | the concept still matches what its source says today | that the source is right, or that the concept says what the team means |
| Human-confirmed | a named person, through `ktl-curator` or the KTL Curator plugin, shown as *confirmed by a person* | someone accountable read the source and agreed | that it stays true, which is what review dates are for |
| Proven in use | readers, through `ktl-docent`, which records misses and disagreements in `.lokf/feedback.md`; and, where the retrieval score is switched on, `knowledge-report.sh` on each scheduled refresh | the bundle answered a real question, or didn't, and the gap became the librarian's next task; the score says whether the index still leads to the concept behind each question readers asked | nothing further: this is the feedback loop that feeds the other three |

The first and third rows also run live, outside these skills and the CLI, for anyone maintaining a bundle in Obsidian rather than through an agent. The KTL Registrar plugin runs the first, and the KTL Curator plugin the third: see [the fifth role](architecture.md#the-fifth-role-which-is-not-a-skill).

## How readers and verdicts steer the next run

Programs decide what each role looks at next, and each verdict changes what the next run does.

- **The curator's queue is computed.** `knowledge-report.sh` reads every typed relation in the bundle and counts how many concepts rely on each one. *Worth ten minutes today* puts first what waits on a person, such as a passed review date or an edit since a confirmation, and within that the concepts most relied on. `ktl-curator` quotes the queue, so no model counts or sorts it.
- **A retired concept names its successor.** When a person retires a concept, `ktl-curator` asks what replaced it and links the successor in the concept's `**Deprecation**` line in `log.md`. The label then reads *retired, replaced by* that path, and the docent opens the successor before it falls back to the repository. The log holds the link until LOKF has a relation for a successor, which [nicholsn/lokf#112](https://github.com/nicholsn/lokf/issues/112) asks for.
- **A reader's dispute shows at once.** A docent's Disagreement can name the concept it disputes. Until the librarian handles the entry, that concept's label adds *a reader disputed this* and the day.
- **The librarian reads the verdicts first.** Before it derives anything, it reads the `**Curation**` lines in `log.md` and every open question a person left. It re-derives a concept a person sent back from the source the note names, never the same way again. It names a send-back that comes twice in its hand-off to the reviewer, as a sign that its own instructions need fixing.
- **A closed pull request is a person's no.** The scheduled workflow records each of its pull requests that a person closed without merging. The librarian proposes none of those changes again until the source moves, a person leaves a new note or a reader asks again. While one of its pull requests is still open, a scheduled run opens no second one.
- **The index is how a reader finds a concept.** The docent picks one to three concepts from the `index.md` bullets before it opens anything, and each bullet copies its concept's `description`. A miss on a question that an existing concept answers is a defect in that description, so the librarian fixes it and adds no second concept.
- **A run is bounded.** The librarian starts from the work list `knowledge-report.sh` computes: the concepts whose sources moved since their last stamp, ordered by history and never by a clock. It handles at most ten feedback entries a run, oldest first. In a scheduled week in which nothing waits, no agent runs, except in a month's first seven days, when the run goes ahead for the sources no program compares.
- **The score reports and gates nothing.** Where the retrieval score is switched on, the pull request shows `n of m`, and a person merges as before, whatever the score.
- **What a person confirmed is retired, not deleted.** The pen refuses to delete a concept a person confirmed or left a note on, so the curator retires it, and it stays for links and history. `knowledge-report.sh coverage` counts the tracked files no concept names, which is how the librarian finds what the bundle missed.

## When the vocabulary stops fitting

LOKF's vocabulary is a short list of classes and typed relations, kept small so that bundles stay portable. When concepts stop fitting those classes, typically in a deep or safety-critical domain such as medicine, law, finance or safety engineering, the answer is a domain schema written in [LinkML](https://linkml.io) that extends LOKF's. The **curator** flags concepts that no longer fit, the team decides, and the **librarian** applies it.

[`ktl-curator/references/domain-schemas.md`](../skills/ktl-curator/references/domain-schemas.md) says what it costs (no new tooling) and how to write one. It also says what to do when the domain already has a LinkML vocabulary of its own, and how to validate values it binds to an external domain ontology. [`ktl-librarian/references/domain-schema.md`](../skills/ktl-librarian/references/domain-schema.md) gives the recipe that writes one and validates against it with the toolkit you already have.

When bundles are federated into one context layer, each domain schema is released with its bundle and a domain admits a bundle when its vocabulary fits ([A federation of bundles](federation.md)).
