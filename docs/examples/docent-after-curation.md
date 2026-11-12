# Examples: what a curation changes for a reader

On 2026-11-12 a person ran `ktl-curator` on this repository's own `.lokf/knowledge/` bundle, in [the session captured here](curator.md). They confirmed four concepts, sent two back with a question and retired one ([`log.md`](../../.lokf/knowledge/log.md)), and confirmed a curation policy that sets `Evidence first: yes`. That same evening a person asked `ktl-docent` the nine questions below, one at a time, at commit `c56f4ae`. The docent followed `skills/ktl-docent/SKILL.md`.

The answers are captured output, with the closing "What's next?" left off each. Every label comes from the docent's own `scripts/knowledge-report.sh labels`. Two things the curation set show up throughout:

- **Evidence first.** An answer resting on a concept no person has confirmed, or one edited since a person confirmed it, quotes its source before the answer. An answer resting only on a confirmed concept keeps the usual order, as answer 9's table does.
- **Labels.** Most of the bundle is still drafts, and the labels say so in every footer.

## 1. "What is KTL about?"

> From `docs/architecture.md`, line 28: "A **knowledge bundle** is the
> catalogue: a plain folder of Markdown concept files that keeps the work
> instead of discarding it. It is useful only when a reader can tell which
> entries are sound, and that depends on one question: *who is responsible
> for the quality of this context?* The trust ladder is the answer, written
> into each entry: where the entry came from and how far it has been
> checked"
>
> From line 34: "**KTL is an OKF runtime.** OKF sets out to "standardize
> the small set of frontmatter fields that make an agent-maintained corpus
> **trustable**, without prescribing any runtime". In KTL those fields are
> the rungs a claim climbs and the gate that refuses a `human:`
> confirmation no person can be tied to."
>
> From lines 42-45, the table of roles: Sidecar *lays the network* (once),
> Librarian *binds it into order* (often), Curator *holds the scales* (a
> little, regularly), Docent *guides the visitors* (whenever anyone asks).
>
> So Knowledge Trust Ladder (KTL) turns a repository's scattered knowledge
> into a knowledge bundle, `.lokf/knowledge/`, with one Markdown file per
> concept. Each concept records where it came from and how far it has been
> checked. The trust ladder runs from still a draft, through checked by
> automation, to confirmed by a person. A gate refuses any `human:`
> confirmation that can't be tied to a real person.
>
> Four skills do the work, named after library and museum roles:
>
> - **ktl-sidecar** installs `.lokf/`.
> - **ktl-librarian** derives concepts from the repository and never
>   vouches for them.
> - **ktl-curator** helps a person record their verdicts. The curator is
>   always a person.
> - **ktl-docent** answers readers' questions from the bundle and writes
>   nothing in it.
>
> A fifth role, the registrar, is a set of programs rather than a skill:
> the `lokf` toolkit, the CI gate, the pen and the report script. Two
> optional skills sit beside the roles: ktl-prose rewords bodies an agent
> wrote, and ktl-website publishes the bundle.
>
> On a new repository they run in that order. After that they run as a
> loop: the librarian refreshes, readers report gaps, and the curator
> reviews what changed. No person has confirmed any of this as it now
> reads (see the labels below).
>
> The bundle has no settled answer on what KTL is *for* in practice, such
> as DevSecOps or governance, or what it isn't for.
> `explanation/intended-uses.md` is a draft placeholder for that question,
> and it says no source in the repository settles it yet.

```text
From the bundle:
- Trust ladder (glossary/trust-ladder.md) - checked by automation only, still a draft
- Why four skill roles rather than one skill (explanation/why-four-roles.md) - edited since a person last confirmed it (confirmed 2026-10-19, edited 2026-10-25)
- What Knowledge Trust Ladder is for, and what it is not (explanation/intended-uses.md) - checked by automation only, still a draft
Checked at source: docs/architecture.md, lines 28, 34, 42-45 - matches both concepts
Gap recorded: none
```

*Each concept is at most checked by automation, or was edited since a person confirmed it, so the source comes first.*

## 2. "What is LOKF?"

> From `docs/architecture.md`, line 32: "It is written in **LOKF** (Linked
> Open Knowledge Format), a semantic profile of OKF whose specification is
> a single LinkML schema. People, agents and any tool that speaks OKF, JSON
> Schema, JSON-LD, SHACL or another supported format can read it."
>
> So LOKF, the Linked Open Knowledge Format, is the format this bundle is
> written in. It is a semantic profile of OKF, the Open Knowledge Format
> from Google Cloud. A bundle in OKF is a folder of Markdown files with
> YAML frontmatter, which gives knowledge prose and structure. LOKF adds
> meaning: it binds every field, type and relationship to a public
> vocabulary (schema.org, DCAT and PROV-O). That way the same Markdown can
> be read as JSON-LD and RDF, validated with SHACL and queried with SPARQL.
>
> Nolan Nichols created LOKF. Its specification is one LinkML schema,
> `lokf.yaml`. The JSON Schema, JSON-LD context, SHACL shapes and OWL
> ontology are all generated from that schema and never edited by hand.
> The `lokf` Python toolkit is separate from the specification: the
> specification defines what LOKF means, and the toolkit validates and
> converts bundles.
>
> The parts above that come from the specification concept are confirmed
> by a person. The glossary entry is a draft that no person has checked.
> Its definition says the Markdown expands to JSON-LD and RDF "losslessly",
> but the architecture page doesn't use that word, so treat it as the
> glossary's claim.

```text
From the bundle:
- LOKF (glossary/lokf.md) - checked by automation only, still a draft
- LOKF specification (references/lokf-specification.md) - confirmed by a person, 2026-09-26
Checked at source: docs/architecture.md, line 32 - matches the glossary concept, except "losslessly"
Gap recorded: none
```

*The glossary term half answered, so the docent followed its `definedBy` relation to the specification concept, which a person confirmed. The word "losslessly" is in the draft's definition but not in its source, so the answer marks it as the glossary's claim instead of stating it as fact.*

## 3. "Can schools use KTL?"

> The bundle only half covers this, so I went to the repository.
>
> From `README.md`, line 54: "The same ladder serves both ends of a range:
> a school or a youth group that retells adult knowledge for younger
> readers, and a regulated team that must show who vouched for each
> claim."
>
> From `docs/young-readers.md`, line 4: "This page is for a teacher, a
> youth leader, or anyone who wants knowledge that adults wrote retold for
> readers aged 8 to 18." From line 48 of the same page: "This repository
> has tried retellings on its own pages only. … We know of no school or
> youth group that has built a bundle this way."
>
> So yes, schools are one of the two uses the README names. A school keeps
> its adult knowledge as concepts in a bundle, such as a safety policy, a
> syllabus or the rules of a sport. It then adds *retellings* of those
> concepts for readers aged 8 to 12 or 13 to 18:
>
> - The librarian writes each retelling as a new concept, and the original
>   stays as it is.
> - ktl-prose holds the retelling to its age band's limits. Its script
>   shows the retelling adds nothing the original doesn't say.
> - An adult, as curator, confirms it against the original.
> - The docent can answer in a band when the asker names it, as in "for my
>   class of ten-year-olds".
> - A school can have retellings written on a schedule by setting
>   `Younger readers: 8-12` in its curation policy.
>
> KTL never guesses or asks a reader's age, never records a reader, and
> leaves consent from pupils and parents to the school.
>
> It is untried in a real school. The repository has retold only its own
> pages, and knows of no school or youth group that has built a bundle
> this way.

```text
From the bundle:
- ktl-prose skill (playbooks/ktl-prose-skill.md) - checked by automation only, still a draft
- What Knowledge Trust Ladder is for, and what it is not (explanation/intended-uses.md) - checked by automation only, still a draft
Checked at source: README.md, line 54; docs/young-readers.md, lines 4-48
Gap recorded: Miss - "Can schools use KTL?": answered from README.md and docs/young-readers.md;
  intended-uses.md says no source states intended uses, and no concept draws on docs/young-readers.md
```

*The first gap of the session, so the docent asked once: "Record bundle gaps in `.lokf/feedback.md` for the librarian, under your login `noelmcloughlin`?" The asker said yes. `knowledge-feedback.sh` wrote the entry without opening the file, and printed only that three entries were waiting.*

## 4. "I have a repository, how do I get started?"

> From `docs/install.md`, line 7: "**Start with the sidecar and the
> librarian.** The curator matters once there is a bundle worth trusting,
> and the website skill once there is one worth showing."
>
> From lines 13-16: "Use `gh skill` version 2.90.0 or later. It defaults
> to GitHub Copilot, so pass `--agent` to name your agent … `gh skill
> install noelmcloughlin/knowledge-trust-ladder --all --scope user`"
>
> From `skills/ktl-sidecar/SKILL.md`, line 10: "Create a fresh **`.lokf/`
> sidecar** inside the repository this skill is invoked from … Then hand
> off to **ktl-librarian** to fill it with real knowledge."
>
> Here is how to get started:
>
> 1. **Install the skills** for your user, not into the repository. With
>    the GitHub CLI 2.90.0 or later, run `gh skill install
>    noelmcloughlin/knowledge-trust-ladder --all --agent claude-code
>    --scope user`, and swap `claude-code` for your agent. The Open Skills
>    CLI (`npx skills add … --global`) and a Claude Code plugin also work.
>    You also need `uv`.
> 2. **Run ktl-sidecar once**, from your repository: ask your agent to "add
>    a LOKF sidecar". It runs a preflight, copies `.lokf/` from its
>    templates, and adds `llms.txt`, a README note and the
>    `knowledge_bundle` link. Then it validates. It can also install the
>    CI workflows, and it hands off to ktl-librarian. You decide whether
>    `.lokf/` is committed, which is the default, or gitignored, for a
>    personal bundle.
> 3. **Run ktl-librarian.** It reads your repository and writes concepts,
>    each a draft with its sources.
> 4. **Run ktl-curator** once the bundle is worth trusting. A person
>    confirms, corrects, sends back or retires each concept.
> 5. **Ask ktl-docent** questions, as you're doing now. Later, ktl-website
>    can publish the bundle as a site.
>
> [Your first bundle](../first-bundle.md) walks one repository from no
> bundle to its first confirmed concept and first answer.
> [A captured run](first-bundle.md) shows what each step printed.

```text
From the bundle:
- ktl-sidecar skill (playbooks/ktl-sidecar-skill.md) - checked by automation only, still a draft
- Why the skills live in their own repository (explanation/why-a-distribution-repository.md) - checked by automation only, still a draft
Checked at source: docs/install.md, lines 7-16 (order and install command);
  skills/ktl-sidecar/SKILL.md, line 10 (the hand-off)
Gap recorded: none
```

*The install command is something the reader will act on, so the docent checked it at the source. That holds whatever the label.*

## 5. "What is the difference between the registrar and the skills?"

> From `docs/architecture.md`, line 55: "The **registrar** keeps the
> records in order … No human has to do this: the `lokf` toolkit checks
> every change, and CI's `knowledge-registrar.yaml` checks every pull
> request that touches the bundle. It also ties each confirmation that is
> added or removed to the confirming person's approval or signed commit."
>
> From line 57: "These are the deterministic tools of the summary at the
> top of this page: a check gives the same answer every time, which
> neither the librarian nor the curator can promise."
>
> So the difference is **judgment against a fixed rule**:
>
> - **The skills** (ktl-sidecar, ktl-librarian, ktl-curator, ktl-docent)
>   are instructions an agent follows. An agent can read, decide and
>   phrase things, so two runs can differ. The librarian derives concepts
>   but never vouches for them. The curator skill records only what a
>   person decides. The docent answers questions.
> - **The registrar** is a set of programs, not a skill, and no agent and
>   no person plays it. A check gives the same answer every time. It has
>   three parts:
>   - **The pen**, `knowledge-apply.sh`, at the librarian's desk. It is
>     the librarian's only way to write the bundle. It applies
>     `.lokf/patch.yaml`, stamps `generated`, keeps the index in step, and
>     refuses a `human:` actor or a rewrite of text a person wrote.
>   - **The report**, `knowledge-report.sh`, at the reader's and curator's
>     desks. It computes every trust label and the health line, so that no
>     label depends on a model's arithmetic. Every label in this session
>     came from it.
>   - **The gate**: `lokf validate` on every change, and
>     `knowledge-registrar.yaml` in CI on each pull request. The gate ties
>     every `human:` confirmation added or removed to that person's
>     approval or signed commit. In Obsidian, where there is no CI, the
>     KTL Registrar plugin does this work.
>
> In the three lines of defence, the librarian and curator are the first
> line, which owns the content. The registrar is the second, which keeps
> the records well-formed. The registrar never judges whether a claim is
> true.

```text
From the bundle:
- Why a registrar role, and why it is not a skill (explanation/why-a-registrar-role.md) - edited since a person last confirmed it (confirmed 2026-10-13, edited 2026-10-19), reopened
- Registrar (glossary/registrar.md) - checked by automation only, still a draft
Checked at source: docs/architecture.md, lines 55-57 - matches the concept
Gap recorded: none
```

## 6. "For 12-18 year olds, explain what a trust ladder is."

> The bundle has no retelling of the trust ladder for young readers; its
> only one is for the pen. So I answered from the adult concept in shorter
> words, keeping every fact. "12 to 18" covers two age bands, 8 to 12 and
> 13 to 18. The ktl-prose rule for a range like that is to use the younger
> band, so this is written for ages 8 to 12, which a 12-year-old can read
> comfortably.
>
> The source first, as written for adults, from `docs/architecture.md`,
> line 28: "It is useful only when a reader can tell which entries are
> sound, and that depends on one question: *who is responsible for the
> quality of this context?* The trust ladder is the answer, written into
> each entry: where the entry came from and how far it has been checked"
>
> **What is a trust ladder?**
>
> A project can keep its knowledge in a bundle. A bundle is a folder of
> notes. Each note is about one thing. Some notes may be wrong. Some may be
> out of date. So how can you tell which notes to believe?
>
> The trust ladder helps you decide. Each note says where it came from.
> Each note also says how far it has been checked. Think of a ladder with
> three steps, called rungs.
>
> - **Bottom rung: "still a draft."** Nobody has confirmed this note yet.
> - **Middle rung: "checked by automation."** A computer program has
>   checked it. No person has checked it.
> - **Top rung: "confirmed by a person."** A named person opened the
>   note's source and agreed with it.
>
> A note can slip down a rung. This happens when someone edits it after a
> person checked it. That person checked the old words, not the new ones.
>
> A question about a note is different. It does not move the note down. It
> only puts a flag on it.
>
> A gate guards the top rung. It turns away any "confirmed" mark that no
> real person can be linked to.
>
> The words for each rung are called **trust labels**. A program works
> them out each time you read a note. They are never saved in the note. A
> label is a hint for you to think about. It is not a score.
>
> **Can you trust this answer?** The note behind it is "still a draft", so
> no person has confirmed it yet. That's why the source comes first above.

```text
From the bundle:
- Trust ladder (glossary/trust-ladder.md) - checked by automation only, still a draft
- Trust label (glossary/trust-label.md) - confirmed by a person, 2026-11-12, against 7339a70
Checked at source: docs/architecture.md, line 28 - matches the concept
Gap recorded: none
```

*Shorter words for this reader, but the footer and labels stay word for word, and the answer says in plain words what its label means. The source quote stays as the adults wrote it. The docent wrote nothing to the bundle: the retelling is for this reader only. The curation policy's `Younger readers: 13-18` lets the librarian write a retelling of a confirmed concept on its scheduled runs, but the trust ladder concept is not confirmed yet.*

## 7. "What is Obsidian?"

> Neither the bundle nor the repository says what Obsidian itself is. Both
> assume the reader knows. So the first paragraph below is general
> knowledge, not taken from the bundle.
>
> **What Obsidian is:** a note-taking app. It works on a folder of plain
> Markdown files on your own computer, which it calls a *vault*. It adds
> links between notes, a graph view and search, and you can extend it with
> community plugins. Because the notes are just files, any other tool can
> read them too.
>
> From `docs/obsidian.md`, lines 7 and 17-18: "The Obsidian vault you
> already have is the **workshop**, and nothing in it is moved or
> migrated. The bundle is the **exhibition**: the checked part of what the
> workshop knows, and the part that teammates, CI and agents read. It
> opens as a small vault of its own, and the two never index the same
> file." … "**Open the bundle as a vault.** Choose **File → Open folder as
> vault**, and pick `knowledge_bundle` … **Install the plugins in that
> vault.** Obsidian installs plugins per vault."
>
> **How KTL uses it:** a knowledge bundle is already a folder of Markdown
> files, so Obsidian can open it directly. KTL keeps two vaults apart:
>
> - The **workshop** is the vault you already keep. It stays as it is.
> - The **exhibition** is the bundle. You open it as a small vault of its
>   own through the `knowledge_bundle` link that ktl-sidecar creates. You
>   need the link because Obsidian's folder picker hides `.lokf/`.
>
> The two vaults never index the same file. In the exhibition vault you
> can install two optional plugins:
>
> - **KTL Registrar** checks each record as you type, since Obsidian has
>   no CI.
> - **KTL Curator** runs the curator's review session with no agent.
>
> Obsidian is optional in both directions. The skills rely on `lokf
> validate`, not on a plugin.

```text
From the bundle:
- Open the knowledge bundle in Obsidian (playbooks/open-bundle-in-obsidian.md) - checked by automation only, still a draft
Checked at source: docs/obsidian.md, lines 7-18 - matches the concept
Not from the bundle or the repository: what Obsidian itself is (general knowledge)
Gap recorded: Miss - "What is Obsidian?": no glossary term for Obsidian itself;
  the bundle and docs/obsidian.md assume the reader knows
```

*The answer marks the part that rests on neither the bundle nor the repository. The asker had already agreed to recording, so the docent did not ask again. The script reported four entries waiting.*

## 8. "Why should a project use KTL? Is there any value?"

> The bundle has no concept that answers "why" directly.
> `explanation/intended-uses.md` is a draft placeholder for this question.
> It says no source states, in general, which uses KTL fits and which it
> doesn't, and its open question has waited for a maintainer since
> 2026-09-24. So the answer below is built from what the sources do claim.
>
> From `README.md`, line 13: "Knowledge Trust Ladder (KTL) keeps any
> repository's scattered knowledge as a **collection**: catalogued,
> authenticated and explained, with the trust in every claim left
> visible. An agent derives each claim, deterministic tools check it, and
> a named person vouches for it."
>
> From `docs/architecture.md`, line 28: "It is useful only when a reader
> can tell which entries are sound, and that depends on one question: *who
> is responsible for the quality of this context?*"
>
> **The value the sources claim:**
>
> 1. **Knowledge kept instead of re-derived.** A project's knowledge is
>    scattered across code, docs, policies and people's heads. Each time an
>    agent or a newcomer asks, it gets pieced together again and then
>    thrown away. The bundle keeps it as one Markdown file per concept,
>    each naming its source, so the next task starts from it.
> 2. **Trust you can see.** Most documentation looks equally sure whether
>    or not it's right. Every KTL concept carries where it came from and
>    how far it has been checked. That runs from still a draft, through
>    checked by automation, to confirmed by a person, and an edit after a
>    confirmation shows up. This session's answers carried those labels.
> 3. **A named person stands behind each confirmation.** An agent can't
>    vouch for anything, and the CI gate refuses any `human:` confirmation
>    it can't tie to that person's approval or signed commit. That is what
>    `docs/three-lines.md` offers a regulated team: evidence of who
>    vouched for each claim.
> 4. **One source for people and machines.** The same files are
>    documentation a person reads and a graph that JSON-LD, SHACL and
>    SPARQL can query. A bundle can also join others into a federated
>    context layer across repositories.
> 5. **Readers steer the work.** A question the bundle can't answer
>    becomes a note for the librarian, as two did in this session.
>
> **What isn't established:**
>
> - No source measures the value. The repository shows KTL working on its
>   own bundle and on the sites its README lists. It knows of no school
>   that has used it.
> - The cost is real. A person has to curate regularly, or most of the
>   bundle stays as drafts and automation checks, as most of this one
>   does: 4 concepts were confirmed in the latest curation, against dozens
>   of drafts.
> - KTL keeps knowledge *about* a project. In a repository of Agent
>   Skills, `docs/skills-repositories.md` leaves whether a skill actually
>   works to evaluations, since KTL's checks cover the form and provenance
>   of what the bundle says.
> - No source says what KTL is *not* for.
>
> **In short:** KTL is worth it when it matters who vouched for a claim, as
> for a regulated team or for agents that need trustworthy context, and
> when someone will curate. If all you need is quick docs, it's more than
> you need.

```text
From the bundle:
- What Knowledge Trust Ladder is for, and what it is not (explanation/intended-uses.md) - checked by automation only, still a draft
- The curated context layer: one bundle, and a federation of bundles (explanation/context-layer.md) - checked by automation only, still a draft
- Trust ladder (glossary/trust-ladder.md) - checked by automation only, still a draft
Checked at source: README.md, lines 13 and 54; docs/architecture.md, line 28
Gap recorded: none - intended-uses.md already holds this as an open question for a maintainer
```

*This is not a new Miss. The bundle already holds the question as a draft with an open question, so a second entry would only repeat it.*

## 9. "How far can you trust an entry in the bundle?"

> It depends on the entry's trust label. The label says how far that one
> entry has been checked, and `knowledge-report.sh` works it out from the
> frontmatter each time it's read. How far to trust each label:
>
> | Label | How far to trust it |
> | --- | --- |
> | **Confirmed by a person** | The most trust the bundle offers. In this bundle it means a named person opened the concept's source and agreed the concept still says what the source says. It is a person's word, not proof. |
> | **Edited since a person last confirmed it** | Treat it as unconfirmed. The person confirmed an earlier text, not this one. |
> | **Checked by automation only** | A program re-checked it, for instance that its source still exists. No person has judged whether it's right. |
> | **Nobody has checked this yet** | Only the librarian's word. Check the source before relying on it. |
> | **Still a draft / Reopened** | A draft has never been confirmed by a person. A reopened concept was confirmed, but someone has since asked a question about it that is still waiting. |
> | **Past its review date** | It may be out of date, even if it was confirmed. |
> | **Retired** | History, not fact. Follow its successor. |
>
> A label is a signal for you to weigh, never a score. Whatever the label,
> check versions, paths, numbers and anything you're about to act on
> against the concept's source. The bundle summarises, and the source is
> the authority. That's why this session quoted sources.
>
> **This bundle today**, from the labels of its 65 concepts:
>
> - 8 are confirmed by a person.
> - 14 were edited since a person last confirmed them. 13 of those were
>   reopened with a question.
> - 42 are checked by automation only, all still drafts.
> - 1 is retired.
> - None is past its review date.
>
> So most of it is useful drafts, not confirmed knowledge.
>
> **What even "confirmed" doesn't prove.** From `docs/three-lines.md`,
> lines 52-57:
>
> > - A confirmation records who and when. It records which state of the
> >   source only when the event carries `revision`, and even then the
> >   state the skill fetched, not what the person read.
> > - The gate checks identity, not entitlement: that `human:ada` is ada,
> >   not that ada was the right person. …
> > - An Environment attestation records only that a listed reviewer
> >   clicked Approve, not that they opened the source.
> > - The `provenance` job runs on GitHub. Elsewhere
> >   `knowledge-provenance.sh` checks signatures against the keys on file
> >   and nothing checks approvals. …
>
> So a confirmation tells you **who** vouched and **when**, tied to their
> login or signature. It doesn't tell you that they were the right person
> to judge, or that they read carefully. You also need to trust the
> curator.

```text
From the bundle:
- Trust label (glossary/trust-label.md) - confirmed by a person, 2026-11-12, against 7339a70
- Knowledge curation policy (policies/knowledge-curation.md) - confirmed by a person, 2026-11-12, against 12d91ca
- Three lines of defence - where each role sits, and what an auditor can check (explanation/three-lines-of-defence.md) - edited since a person last confirmed it (confirmed 2026-10-19, edited 2026-11-12), reopened 2026-11-12 by noelmcloughlin: 1 question waits
Checked at source: docs/three-lines.md, lines 52-57 - matches the concept, which shortens the second and third limits
Gap recorded: none
```

*The table rests on two concepts a person confirmed that day, so it comes first and needs no quoted source. The limits rest on a concept edited since a person confirmed it, so its source is quoted before the answer draws on it. The counts come from running `knowledge-report.sh labels` over every concept, not from a model's tally.*

## Which concept answers each question

| Question | Concept that answers it today |
| --- | --- |
| 1. What is KTL about? | [glossary/trust-ladder.md](../../.lokf/knowledge/glossary/trust-ladder.md), [explanation/why-four-roles.md](../../.lokf/knowledge/explanation/why-four-roles.md) |
| 2. What is LOKF? | [glossary/lokf.md](../../.lokf/knowledge/glossary/lokf.md), [references/lokf-specification.md](../../.lokf/knowledge/references/lokf-specification.md) |
| 3. Can schools use KTL? | none; a miss recorded for [explanation/intended-uses.md](../../.lokf/knowledge/explanation/intended-uses.md) and [playbooks/ktl-prose-skill.md](../../.lokf/knowledge/playbooks/ktl-prose-skill.md) |
| 4. How do I get started? | [playbooks/ktl-sidecar-skill.md](../../.lokf/knowledge/playbooks/ktl-sidecar-skill.md), [explanation/why-a-distribution-repository.md](../../.lokf/knowledge/explanation/why-a-distribution-repository.md) |
| 5. Registrar or skills? | [explanation/why-a-registrar-role.md](../../.lokf/knowledge/explanation/why-a-registrar-role.md), [glossary/registrar.md](../../.lokf/knowledge/glossary/registrar.md) |
| 6. A trust ladder, for ages 12 to 18 | [glossary/trust-ladder.md](../../.lokf/knowledge/glossary/trust-ladder.md), [glossary/trust-label.md](../../.lokf/knowledge/glossary/trust-label.md) |
| 7. What is Obsidian? | [playbooks/open-bundle-in-obsidian.md](../../.lokf/knowledge/playbooks/open-bundle-in-obsidian.md); a miss recorded for Obsidian itself |
| 8. Why use KTL? | [explanation/intended-uses.md](../../.lokf/knowledge/explanation/intended-uses.md), [explanation/context-layer.md](../../.lokf/knowledge/explanation/context-layer.md) |
| 9. How far can you trust an entry? | [glossary/trust-label.md](../../.lokf/knowledge/glossary/trust-label.md), [explanation/three-lines-of-defence.md](../../.lokf/knowledge/explanation/three-lines-of-defence.md) |

## Notes

- [`ktl-curator` in a review session](curator.md) captures the curation these answers follow.
- Answers under `Evidence first: no` are not captured yet.
- The two misses this session recorded wait in `.lokf/feedback.md` for the librarian's next run.
