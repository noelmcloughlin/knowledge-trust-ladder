# Changelog

All notable changes to this repository are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows the rules in [docs/releasing.md](docs/releasing.md). All skills release together under one tag.

## [Unreleased]

## [0.31.0] - 2026-10-04

### Added

- **`docs/for-the-curious.md` shows who writes the bundle and what checks it.** A new section and diagram, `.assets/ktl-architecture.svg`, give each writer's one door. The librarian's patch file goes through the pen, the curator's verdicts through `ktl-curator` or the KTL Curator plugin, and a reader's miss through the docent's feedback recorder. Below them sit the registrar's gate and the report script. The README now says why `knowledge-apply.sh` is called *the pen* where it first names it, and the bundle's glossary defines the term.
- **Check 16b keeps KTL's roles, skills and repositories from being named after LOKF.** LOKF is the format, its schema and its toolkit. The changelog, the bundle's log and the source map's dated notes keep what was written at the time.

### Changed

- **The pages name Knowledge Trust Ladder (KTL), the bundle and LOKF apart.** KTL is this design, with its roles, skills, scripts and gate. The bundle is the corpus it keeps in `.lokf/knowledge/`, and LOKF is the format and its toolkit. `docs/wikiskill.md`, `docs/three-lines.md` and `docs/three-lines-critics.md` used *a bundle* or *LOKF* where they meant the design, so a reader could not tell the design from its corpus, or from the paper's wiki. The contributing guide, the signing page, two sidecar references, the issue templates and five bundle concepts follow, and `references/trust-fields.md` no longer says *whoever held the pen*, now that the pen names a script.
- **Each skill's heading is its name, such as `# ktl-curator`.** `# KTL Curator` was also the Obsidian plugin's name. Where Obsidian is the scope, the pages now say *the KTL Curator plugin*.

### Fixed

- **The trust ladder's middle rung credits the librarian's refresh, not the schema check.** *Checked by automation only* means a `verified` event with a `process:` actor, which a scheduled refresh writes after it reads the source again. The diagram credited `lokf validate`, CI and the KTL Registrar plugin, none of which writes one.
- **The three-lines diagram names every part of the registrar.** Its second line gains the pen and the report script, which `docs/three-lines.md` already listed, and its title says *KTL role*. The two-vaults diagram shows `services/`, a folder the sidecar lays down, where it showed `concepts/`.
- **The preflight reports `ktl-prose`.** Its two skill checks listed four skills, so it never reported the fifth or a stale copy of it. Its note for a host without `uv` now counts seven of the twelve conventions, where it said six of eleven.
- **`docs/signing-commits.md` says a signature is required to remove a confirmation, as to add one.** The gate has held removals to the same evidence since 0.30.0.
- **`scripts/sync-sidecar.sh` lays down what a synced copy cannot run without.** It only reported a template the sibling had never laid down. So a sync to 0.30.0 carried the new wrapper, which refuses to start without the apply script, and left the apply script and the report script out. It now lays down a template that ktl-sidecar puts on every host, and one that a copy already in the sibling cannot run without. That is a script a workflow runs, the apply script beside the wrapper, or a Python half beside its shell half. It reports any other, as before.
- **The pen keeps an index in the shape a person gave it.** `knowledge-apply.sh` took any bullet that held a concept's link for that concept's own bullet, so a `reindex`, `set` or `delete` of one concept rewrote or removed a line that listed several. It looked for a folder's section under a `#` heading only, so a root index with `##` sections gained a second section at its end. It now rewrites every line that holds the concept's link alone, and leaves a line that lists it among other links or names it in a sentence. It takes a deleted concept's link out of a list of links, and refuses the delete while a sentence links it. It finds the folder's section at any heading level, or by the section's link to the folder's `index.md`, and never under the title. Conventions rule 12 reads a line that lists two concepts the same way, as neither one's bullet. Check 19 exercises each case. ai-linkmo's sync to 0.30.0 found the defect, since its root index lists concepts this way.

## [0.30.0] - 2026-10-03

### Added

- **`knowledge-report.sh` computes what the skills used to work out.** It prints each concept's trust label, the bundle's health line, ktl-librarian's work list and what a change does to the record, from frontmatter and git history, in bash and awk. ktl-curator's Step 1 and ktl-docent's footer quote it. The librarian workflow's `publish` job fills its pull request from it, on its own checkout. A source has moved when history, not a clock, puts its last commit after the one that recorded the event. Check 20 exercises it.
- **A retrieval score, off unless `KNOWLEDGE_RETRIEVAL` is `true`.** On a scheduled run that changes the bundle, the agent picks from `index.md` alone the concepts it would open for each question readers asked, and `knowledge-report.sh` scores the reply by program. The pull request carries the result as `n of m`. It reports and gates nothing.
- **A ledger of the questions readers asked, `.lokf/questions.md`.** `knowledge-apply.sh` moves each handled feedback entry there: the day, the kind, the concept that now answers it, and the reader's question from the operation's `asked` key. It only grows, and programs read it.
- **The pen gains `resolve` and `--format`.** `resolve` withdraws an open question the librarian itself asked, and never a person's note. `--format` prints the patch file's shape, which check 19 holds equal to `references/patch.md`.
- **Conventions rule 12: an index bullet carries its concept's title and description.** The pen keeps the three copies equal for a concept it writes; the gate now fails when another hand leaves one behind, and a `reindex` operation repairs it.

### Changed

- **ktl-librarian starts a refresh from the work list,** and reads a local source again only when it moved. It leaves a note that a later confirmation answered to the curator, withdraws its own answered questions, and keeps a reader's words out of `log.md` and out of every concept. When a count or a name changes in one source, it searches the bundle for the old value, which the curation of 2026-10-03 asked for.
- **The health line counts a concept edited since its confirmation once, under *Edited since confirmed*,** and no longer under *Confirmed by a person* as well. The person confirmed an earlier text.
- **ktl-curator clears answered open questions on *Correct now* too.** Its report lists apart the questions a person's later confirmation answered, and the confirmed concepts whose source moved after the confirmation.
- **The scheduled pull request is filled by the job that opens it.** The health line and what the change does to the record come from `knowledge-report.sh` in `publish`, and nothing but the retrieval score's two integers comes from the job that ran the agent.

### Fixed

- **A sidecar laid down from 0.29.0 paired the new wrapper with a skill that predates the pen.** The template pins the skills one release behind, and the wrapper's prompt named `references/patch.md`, which that release lacks. The prompt now takes the format from `knowledge-apply.sh --format`, and the wrapper says so when the pinned skill is older. A host already laid down from 0.29.0 moves `TRUST_LADDER_SKILLS_REF` to `v0.29.0` or syncs to this release.
- **`docs/wikiskill.md` said the paper's ablation ran on five benchmarks.** Its Table 3 has four.
- **A `from_feedback` line that `feedback.md` does not hold is a finding, not a traceback.**

### Security

- **A person's record is never removed without that person.** The `provenance` job and `knowledge-provenance.sh` ask the person behind a `verified` event that a change removes, struck out or gone with its concept, as they ask the one behind an event it adds. A person's `generated` record may give way only to another person's. Before this a pull request that deleted a confirmed concept passed the gate.
- **`publish` reads a person's events off the patched tree.** `knowledge-provenance.sh --unattended` refuses a person's event added, changed or removed in any YAML layout, a person's note added or removed, and a change to text a person wrote. The line pattern it replaces as the backstop saw a block-style `by: human:` line only. The wrapper runs the same check after the pen.
- **The pen refuses to delete a concept a person left a note on,** as it refuses one a person confirmed.
- **A reader's words no longer reach `log.md`.** The librarian quoted a reader's question there since 0.29.0, and ktl-curator opens that file to add its line. The question now stays in the ledger.

## [0.29.0] - 2026-10-03

### Added

- **A fifth skill, `ktl-prose`, rewords a bundle's agent-written concepts in plain English.** It rewords only a body an agent wrote and no person confirmed, and changes no fact and no frontmatter byte, so `generated` keeps naming the librarian. Its `prose-check.py` reports dashes, long sentences and stock phrases, and proves a rewording changed only wording. Check 18 exercises it.
- **`docs/wikiskill.md` reads the WikiSkill paper (Tang et al., Google Research, 2026) against this design,** part by part. The captured docent answers in `docs/examples/docent.md` now link the concept behind each question, so the link checker fails the build when that concept is renamed or deleted.
- **`knowledge-apply.sh`, the librarian's only pen.** ktl-librarian describes each change as one of seven operations in `.lokf/patch.yaml` (`references/patch.md`), and the script writes the files. It stamps `generated`, keeps each description equal to its two index bullets, files the log line, and refuses a `human:` actor, a rewrite of a person's text, or the deletion of a confirmed concept. Nothing is written unless every operation passes. Check 19 exercises it.

### Changed

- **ktl-librarian writes in plain English, and offers a plain-prose pass in a live session.** A paragraph in its section 1 gives the rules for every body, `description` and index bullet, so a new concept needs no rewording. Before it opens its pull request in a live session it offers the `ktl-prose` pass, whose time is before a person confirms. An unattended run skips the offer.
- **ktl-librarian reads the curator's verdicts before it derives, and closes the loop on a reader's miss.** It re-derives a sent-back concept from the source the note names. A miss that an existing concept answers is a description defect, fixed in the `description` and both index bullets, never with a twin. A run handles at most ten feedback entries. Rule 3 reaches a `Person` or `Organization` through `author` or `publisher`, not `source`.

### Fixed

- **A concept edited after a person confirmed it is no longer read as confirmed.** ktl-docent and the Copilot docent gain the label *edited since a person last confirmed it*, which the curator and the Obsidian plugins already show. The docent says the edit first, gives both dates, and treats the concept as unconfirmed.
- **ktl-curator compares the two times of "edited since" whole.** `references/trust-fields.md` told it to cut both to the day first, so a concept confirmed in the morning and rewritten that afternoon did not count as edited. The Obsidian plugins and the SPARQL query already compared whole times.
- **The skills no longer claim a SHACL check that nothing runs.** ktl-librarian, ktl-sidecar and `docs/three-lines.md` said the bundle was validated with JSON Schema and SHACL. The toolkit generates the shapes and neither ships nor runs them, so the wording now names what runs: `lokf validate` (JSON Schema) and `--check-refs`.

### Security

- **The scheduled librarian never writes the bundle itself.** The agent's one output is `.lokf/patch.yaml`; `knowledge-librarian.sh` applies it with `knowledge-apply.sh` and refuses a run that touched any other file, so the refusals above hold in the unattended run and not only in prose. The threat model's hardening list names it.

## [0.28.0] - 2026-09-29

### Added

- **Release assets can carry a host's published name.** `knowledge-release.yaml` names its zips after the `KNOWLEDGE_RELEASE_NAME` repository variable when it is set, and after the repository otherwise, so a host whose package is published under another name, such as gist as `gist-linkml`, ships assets under that name.

## [0.27.2] - 2026-09-25

### Security

- **The Snyk W011 findings on ktl-librarian and ktl-docent are acknowledged** in each skill and [the threat model](docs/threat-model.md#prompt-injection-guards). The librarian resolves only what a feedback entry names, and the scheduled `publish` job refuses any other path and any `by: human:` claim. The docent quotes repository text it did not author and writes only a scripted feedback entry.

## [0.27.1] - 2026-09-25

### Fixed

- **`atk add skill` works with the released Agents Toolkit.** The 1.1.17 release hides the command behind `TEAMSFX_AGENT_SKILLS`, not `ATK_FRONTIER`, which only the 1.1.18 betas read, so the documented line failed with `UnknownCommandError`. `docs/m365.md`, the sidecar's `references/m365.md` and the Copilot playbook now set both.
- **The toolkit route in `docs/m365.md` runs in the agent's project.** The steps change into the folder `atk new` creates, pass `--env dev` to `provision` and `preview`, and skip `atk validate`, which rejects `agent_skills` against the v1.8 schema. Both variables are exported for the session, since `provision` packs the skill's files only while one is set.
- **`docs/m365.md` says what a tenant without custom skills sees.** The reader checks for the Frontier preview first. Without it, `atk provision` fails with `Unrecognized member 'agent_skills'` and Agent Builder sends the skill to Copilot Studio, which needs its own licence. The troubleshooting list quotes both.

## [0.27.0] - 2026-09-24

### Added

- **Releases carry the docent as a Microsoft 365 Copilot skill.** `knowledge-release.yaml` attaches `ktl-docent-m365-<tag>-<repository>.zip` beside the bundle zip, for upload to Agent Builder. The new `.lokf/m365/` folder holds its instructions and `knowledge-m365.sh`, which packs a reproducible zip within Copilot's limits. Check 17 builds it.
- **`scripts/sync-sidecar.sh` syncs a sibling repository to one release.** It copies a published tag's templates over the sibling's copies, moves its skills pin to that tag, runs the sidecar's checks, and leaves the diff for review. `docs/releasing.md` drops the hand bump of the template's own pin, which the release commit has made since 0.23.1.

## [0.26.0] - 2026-09-24

### Added

- **Conventions rule 11 rejects an `at:` later than the commit that recorded it.** Local time labelled `Z` and round placeholders had put 28 times in this bundle ahead of their commits, so concepts read as edited after a person confirmed them. ktl-librarian and ktl-curator now take every `at` from `date -u`.

## [0.25.0] - 2026-09-24

### Changed

- **The release workflow attaches the bundle as a zip file.** `knowledge-<tag>-<repository>.zip` with its `.sha256` replaces the tarball, since every operating system opens a zip. It stays reproducible across time zones and umasks, and stores links as links. Layout test 5 runs the pack.

## [0.24.0] - 2026-09-24

### Added

- **`knowledge-release.yaml`, a third sidecar workflow.** It attaches `.lokf/knowledge` to a GitHub release as a reproducible archive with a checksum, after the registrar's checks pass, and attests it on a public repository. It skips an unchanged bundle unless `force` is set, and runs by hand or, with `KNOWLEDGE_RELEASE_ENABLED`, on each release. `publish.yml` dispatches it here.
- **The librarian template has a slot for the agent's credential.** `AGENT_API_KEY_ENV` names the variable the agent reads. The credential is the `AGENT_API_KEY` secret or, with `AGENT_USE_JOB_TOKEN`, the job's own token for Copilot CLI. The wrapper exports it under that name only and refuses a name that `gh`, git or the runner also read. Layout test 1c exercises it.

### Fixed

- **The librarian validates relation targets before it opens a pull request.** Its validate step now runs `lokf validate --check-refs`, as the registrar gate does, because the gate never fires on the librarian's own pull request.
- **The sidecar README's layout tree names everything Step 5 lays down.** It stopped at `justfile` and `feedback.md`; `scripts/`, `queries.http` and `curators/` were missing.

## [0.23.1] - 2026-09-24

### Fixed

- **The librarian template no longer installs the pinned skill in `noelmcloughlin/knowledge-trust-ladder`.** The install step put a copy in `.agents/skills/`, which the wrapper searches before `skills/`, so scheduled runs used that old release instead of the source. The step checks the repository name, not a file a host could commit. This repository's workflow now matches the template apart from its skills pin, and check 11 enforces it.
- **The release commit moves the skills pin in the template only.** `GITHUB_TOKEN` may not push a change under `.github/workflows/`, so moving it in this repository's workflow as well made the 0.23.1 release fail.
- **The preflight no longer reports a different skills pin as drift.** A host moves `TRUST_LADDER_SKILLS_REF` on its own schedule, so its librarian workflow is compared with the template's apart from that one value.

## [0.23.0] - 2026-09-23

### Added

- **`knowledge-feedback.sh`, a sixth sidecar script.** It files a reader's Miss or Disagreement in `.lokf/feedback.md` under today's UTC date, newest first, and prints only a kind, a date and a count. The preflight names a sidecar that predates it; check 12a exercises it.

### Changed

- **ktl-docent records a gap by running that script** and never reads `feedback.md`. A host on an older sidecar runs the ktl-sidecar repair; until then the preflight says so and the hand-written format stands.
- **The README, docs pages, skill introductions and workflow comments are restyled for the reader**: shorter sentences, steps before rationale, plain statements. The critics page is arranged by criticism with a verdict table and sources by DOI, and the host-by-host layouts live once in `docs/obsidian.md`.

### Fixed

- **The librarian template pins a tag that carries the skill.** `TRUST_LADDER_SKILLS_REF` read `v0.21.0`, where the skills are still `lokf-*`, so the install step's `skills/ktl-librarian` was not there and every scheduled run on a scaffolded host failed at it. The pin moves to `v0.22.0`, and check 15 now reads the pinned tag for that path.

### Security

- **Reader feedback no longer reaches the docent's context.** Keeping `feedback.md` newest first made an entry a read, an edit and a write back, so outsider-written text entered the session, guarded by prose alone (Snyk W011). The script does the insertion instead; ktl-librarian is the only skill that still reads an entry.

## [0.22.0] - 2026-09-22

### Added

- **A dark counterpart for all seven diagrams**, `*-dark.svg` beside each original. Same geometry and wording; only the palette differs, re-toned role for role from the light one.
- **A dimmed counterpart too**, `*-dimmed.svg`: the same geometry on warm grey paper rather than a dark one.
- **The markdown picks by theme.** Every diagram is a `<picture>` with a `prefers-color-scheme: dark` source over the existing file, so the light original stays the fallback and its path is unchanged.

### Changed

- **The skills take the `ktl-` prefix**: `ktl-curator`, `ktl-docent`, `ktl-librarian` and `ktl-sidecar`, formerly `lokf-curator`, `lokf-docent`, `lokf-librarian` and `lokf-sidecar`. The Obsidian plugins are KTL Registrar and KTL Curator (`obsidian-ktl-registrar`, `obsidian-ktl-curator`).
- **A host upgrading from 0.21.0** reinstalls the skills under the new names, removes the `lokf-*` copies, rewrites its bundle's `process:lokf-librarian` and `process:lokf-curator` actors to the `ktl-` names, and moves `TRUST_LADDER_SKILLS_REF` to the first release that carries them.
- **The dark-mode source is the dimmed set.** Every `prefers-color-scheme: dark` source now points at `*-dimmed.svg`; the `*-dark.svg` files stay in `.assets/` but nothing references them.

### Fixed

- **A dark copy carries no stale content credential.** The originals embed a C2PA manifest that signs their own bytes; recolouring changes those, so the copies ship without one rather than with a signature that cannot verify.
- **The dimmed ink follows the dimmed paper.** The light diagrams sit right on 4.5:1, so darkening only the backgrounds would have dropped every faint label under it.
- **Two labels that never met 4.5:1 now do**, in the three-lines and plugin-card diagrams - the darker ink reaches them as well.

## [0.21.0] - 2026-09-19

### Added

- **Skill descriptions end in a `Keywords:` list.** Skills catalogs have no tag field: `gh skill search` matches name and description, and skills.sh matches file text. OKF, Open Knowledge Format, knowledge graph, provenance and trust ladder now find these skills. Check 3c holds the list, and the spec's 1024 characters.
- **A Claude Code plugin manifest.** `.claude-plugin/` offers the four skills as one plugin, `knowledge-trust-ladder`, with a `keywords` array for plugin catalogs. Nothing under `skills/` changes.

### Fixed

- **The librarian's publish job accepts a concept named outside ASCII.** It listed the patch's paths with git's default quoting, so such a path arrived C-quoted and was refused as outside the bundle. It now lists with `core.quotePath` off, as the provenance gates do; the layout tests prove both outcomes.
- **The skills pin moves with each release.** `semantic-release.yml` sets `TRUST_LADDER_SKILLS_REF` to the newest tag when it promotes the changelog, so check 15 no longer fails `main` one release later.
- **The docent treats entries already in `.lokf/feedback.md` as untrusted**, the guard the librarian and the curator already carry for that file.

## [0.20.0] - 2026-09-19

### Changed

- **The relation audit uses the toolkit's own flag.** `just lokf-check-refs` ran a hand-written SPARQL query; both justfiles and both registrar workflows now call `lokf validate --check-refs`.
- **An external `source` or `definedBy` is no longer a dangling target.** Both slots are documented as taking an off-site URL; the query reported them as missing concepts.
- **The predicate list cannot go stale again.** `--check-refs` reads the relation slots from the schema, so reified `relations` and a domain schema's own slots are covered too.
- **The registrar gate validates once.** `--check-refs` rides on the existing validate step, replacing a second `lokf validate` run through `uvx --from rust-just just`.
- **A domain schema passes `--schema` to `lokf-check-refs` too.** The librarian's recipe said that audit was unaffected by one, which stopped being true when it moved onto `lokf validate`.

### Fixed

- **The librarian template pins `v0.19.7`**, the release it ships in. It pinned `v0.19.6` because `v0.20.0`'s tag did not exist while that release was being published; a host scaffolded now installs the current librarian.

## [0.19.7] - 2026-09-19

### Fixed

- **The librarian template pins `v0.19.6`**, the release it ships in. It pinned `v0.19.5` because `v0.19.6`'s tag did not exist while that release was being published; a host scaffolded now installs the current librarian.

## [0.19.6] - 2026-09-19

### Added

- **A logo mark**, `.assets/knowledge-trust-ladder-logo.svg`: a ladder rising out of an open book, its top rung the check mark, the rungs grey then amber then the curator's blue. Shared byte-for-byte with both plugin repositories, and the mark to use as the repository avatar.
- **Every diagram carries the mark and the wordmark**, from one shared definition. The social-preview card's title is the wordmark and a tagline, not the repository slug.
- **`docs/install.md`**: the `gh skill` commands, the per-skill prerequisites and the pinning rule, moved out of the README.
- **The README states the runtime claim.** OKF's fourth goal asks for frontmatter that makes a corpus trustable "without prescribing any runtime"; this is such a runtime.
- **The README names its order of work**: specification first, schema first, interoperability first - nothing here invents a field, a format or a validator.
- **The README names the context layer**, and the question that layer comes back to - who is responsible for the quality of this context - as the one the trust ladder answers.
- **The README claims the domain schemas OKF puts out of scope**, in scope here by construction, and points at the curator's `domain-schemas.md` for the flag and the recipe.

### Changed

- **The README is a front door, not the manual.** 1,792 words to 1,864: much the same length, a different shape. Install commands out to `docs/install.md`; the closing sections collapsed into one `Read on` table.
- **The opening says "collection", not "library"**, which this audience reads as a code library. A collection is what a librarian, a registrar, a curator and a docent all serve.
- **The opening names the whole system** - four skills, the registrar automation, the `lokf` toolkit underneath - and the two Obsidian plugins as optional.
- **The sidecar bootstraps a fresh `knowledge_bundle`** in the README's words, the visible doorway, with `.lokf/` named as what lies behind it.
- **This repository is now `knowledge-trust-ladder`**, formerly `lokf-agent-skills`. Upstream LOKF ships its own bundled skills, and a third-party repository named after the format read as their official home.
- **The four skill names are unchanged** - they are installed paths in every host. GitHub redirects the old clone and `npx skills add` paths.
- **`TRUST_LADDER_SKILLS_REPO` moves with the repository** (renamed from `LOKF_SKILLS_REPO`, to match the repository's own name). A host that copied the template earlier keeps working through the redirect until it copies again.
- **The bundle's `base_iri` is `https://knowledge-trust-ladder.example/knowledge/`**, which re-ids all 30 concepts and every typed-relation target.
- **`lokf-trust-ladder.svg` is now `trust-ladder.svg`**: under the new repository name the old filename read as the project's mark rather than the diagram's.
- **The bundle's log keeps the name the project had on each day.** The rename pass had rewritten entries written weeks earlier, including the one recording the old `base_iri`; `CHANGELOG.md` was left alone, and the log is the bundle's own record.
- **The repository contract refuses the old name** (check 16). `CHANGELOG.md`, the bundle's `log.md` and one "formerly" line in `docs/install.md` are the exceptions, because they record history.
- **The three-lines diagram is keyed to the legend it shares.** Its bands made the first line green and the second blue, where green means agent work and blue a named person - so the registrar sat in the person's colour and the curator in the agent's. Neutral bands now, and each card takes the colour of whoever acts.
- **Labels no longer collide with their own boxes**: six across four diagrams overflowed or came within 2px, one of them hidden behind a card painted over it.
- **The diagrams no longer glare.** A pure-white canvas was the brightest thing on the page, with the tinted cards below it; all seven assets now use the warm `#E4E1D7`, an even three-step ramp from canvas to panel to card. Green and blue were rejected for it - in these diagrams they mean agent work and a named person.
- **Small grey labels are legible again**: the faint ink moved from `#888780` to `#6E6D66`, clearing 4.5:1 where it had been 3.6:1.
- **`LOKF_SKILLS_REPO`/`LOKF_SKILLS_REF` are now `TRUST_LADDER_SKILLS_REPO`/`TRUST_LADDER_SKILLS_REF`.** The old names said "LOKF" for the repository itself, which is now `knowledge-trust-ladder`; the skills stay `lokf-*`, only the repository pointer is renamed. Each sibling's own copy of the workflow needs the same rename before it next syncs from the template.

### Fixed

- **The librarian template pins a release that exists.** `publish.yml` promotes the top `CHANGELOG.md` heading before its tag exists, so pinning to that heading fails check 15's own clone test until the tag lands; the template now pins `v0.19.5`, the newest release a host can actually clone.

## [0.19.5] - 2026-09-19

### Security

- **The curator counts reader feedback without reading it.** Its report says how many entries wait in `.lokf/feedback.md` but gave no way to count them, so an agent read outsider-written free text into its session to get a number. It now counts with `grep -c` and never opens, quotes or acts on an entry.
- **The Snyk W011 finding on lokf-curator is acknowledged** in the skill and [the threat model](docs/threat-model.md#prompt-injection-guards): a real surface, now count-only, and every curator write is a live person's verdict.

## [0.19.4] - 2026-09-19

### Fixed

- **An unauthenticated send-back is attributed to the session.** The curator's send-back note showed only the `human:<id>` shape, so a session with no `gh` login improvised a description of itself in the actor's place, and conventions rule 4 rejected every such note at the gate. The skill now says to write `process:lokf-curator` there.
- **The librarian template pins the current release.** `LOKF_SKILLS_REF` moves from `v0.19.2` to `v0.19.4`, the release this template ships in; check 15 failed on `main` once 0.19.4 was promoted.

### Security

- **The provenance gates read a concept whatever its name.** Git's default quoting C-quotes a path holding a byte above 0x7f, so the `.md` filter in both gates dropped that concept and a `human:` confirmation inside it passed as "no new confirmations". `knowledge-registrar.yaml`'s `provenance` job and `knowledge-provenance.sh` now list paths with `core.quotePath` off.
- **A path git still has to quote is refused, not skipped.** A double quote, a backslash or a control character in a name is a finding with the path named; check 13 proves both outcomes.
- **The registrar's step summary strips backticks** from an id that failed the login pattern, so it cannot close the code span and render as Markdown.
- **The Snyk W011 finding on lokf-sidecar is answered** in the `provenance` job's comments and [the threat model](docs/threat-model.md#prompt-injection-guards): the job reads pull-request metadata, and no agent runs in it.

## [0.19.3] - 2026-09-18

### Fixed

- **Retitling a pull request re-runs the title check.** The check that refuses a releasing pull request with a non-releasing title told the author to retitle, but the workflow listened only for the default pull-request types, so a title change fired nothing and the check stayed red whatever the author did. The trigger now names `edited`.
- **The librarian no longer points a `resource` at gitignored runtime state.** A concept whose `resource` named an installed skill under `.agents/` resolved on a machine that had it and failed conventions rule 5 everywhere else, which is how it reached CI in the curator plugin. A local `resource` must be a path git tracks; the published copy, pinned to the version the host installs, is what to name instead.
- **The librarian template installs the current skill, not a ten-version-old one.** `LOKF_SKILLS_REF` pinned `v0.9.0` while this repository released `v0.19.2`, so every host scaffolded from the template ran a librarian that far behind. Check 15 now holds the pin to the top released heading in the changelog, so it cannot fall behind in silence again.
- **The skills-pin check no longer fails every publish.** Check 15 held `LOKF_SKILLS_REF` to the newest released heading, but that heading is promoted on merge while its tag is created later by `publish.yml`, so during the publish the only pin a host could clone is the one below it. The check now accepts either of the two newest releases.

### Security

- **The registrar gate opts into token scope instead of inheriting it.** `knowledge-registrar.yaml` had no top-level `permissions: {}`, unlike the librarian workflow beside it, and both of its read-only jobs kept the checkout credential on disk although neither pushes. Both are now set in the template and this repository's copy.

## [0.19.2] - 2026-09-17

### Security

- **The librarian wrapper restores `.git/config` and `.git/hooks/` on every exit.** An `EXIT` trap now restores them after a failing agent or a cancelled job too, so a poisoned `core.hooksPath` cannot reach the workflow's next steps. A Socket audit reported it, and the layout tests prove the fix.

## [0.19.1] - 2026-09-17

### Fixed

- **A pull request that would release must be titled to release.** A squash merge takes its subject from the pull request title, and GitHub's default title carries no type, so a typed `fix:` reached `main` untyped and released nothing. The `plan` job now refuses that combination and says how to retitle.

- **The no-Python schema fallback is pinned to the toolkit's version.** It pointed at `lokf.yaml` on upstream `main`, which the 0.8.0 validator does not enforce. The URL now names the `v0.8.0` tag and moves with the floor, which also answers a skills.sh audit finding.

- **A pull request that releases nothing is no longer failed for writing no release notes.** The `plan` job asks for notes only when one of the pull request's own commits would release, so a `chore:` or `docs:` one, a Dependabot bump among them, passes.
- **A Dependabot action bump no longer breaks the contract on its own.** The bot edits `.github/workflows/` and cannot see the copies under `skills/lokf-sidecar/templates/github/`, which check 11 holds byte-identical, so every bump failed until the template was synced by hand. The failure now names both directions instead of only "copy the template over it", which is the wrong one in that case.

## [0.19.0] - 2026-09-17

### Added

- **The registrar gate resolves a `revision`.** A sixth rule: a commit-shaped `revision` on an event must name a commit that holds the concept's local `resource`, so the skills pin with the full hash; the validate job checks out the full history, and a shallow clone is reported rather than passed. Check 11 proves both outcomes in a throwaway repository.
- **Portability pages for the curator and the librarian, and the sidecar's rewritten as a host matrix.** What works, what is lost and the substitute on GitHub, GitLab, Forgejo, no forge, no git, Windows and PowerShell, macOS, synced folders and an Obsidian vault.
- **Every skill declares what it needs** in the Agent Skills `compatibility` field; check 3b holds it to the spec's 500 characters.
- **A forge-free provenance gate.** `knowledge-provenance.sh` verifies each confirmation's commit signature against the curator's public key on file under `.lokf/curators/`, GPG with its subkeys or SSH, with plain git and gpg or ssh-keygen; check 13 proves each outcome with throwaway keys.
- **A prerequisites page** gives each preflight line its plain meaning, who fixes it and what to send them, for a person who cannot act on it themselves; check 12 holds it to every line the preflight can print.
- **A preflight every skill runs first.** `knowledge-preflight.sh` prints what this machine can do, from shell and git to identity, signing, keys on file and toolkit, and ends by naming what is missing and which steps that disables; check 12 exercises it.
- **The sidecar lays down `.lokf/.gitattributes`**, keeping the bundle on LF so a Windows checkout gives CI's verdict.
- **Three more conventions the gate checks**: one file per `id`, lowercase paths, and a closed frontmatter block with no byte order mark; check 11 proves each.

### Changed

- **The skills use lokf 0.9.0+'s `revision`.** The curator writes it on a confirmation, the librarian on `generated`, and the docent quotes it beside the date. An older toolkit leaves it out. The librarian's tables also name a source's `excerpt`.
- **The sidecar's toolkit floor is lokf 0.8.0**, here and in the `lokf-sidecar` template. The librarian's field tables now state its constraints: `sources[].author` is an actor string, `http_method` is one of seven uppercase verbs, and every timestamp including `stale_after` is a datetime, a bare date meaning midnight UTC.
- **The curator says what it can record before offering a session**, from a *Ready to record* line with three identity routes - `gh`, `glab`, the signing key the forge lists - and a rule for a host with no forge. The librarian names files in lowercase and hands off on a host without git; the docent's feedback attribution names the same routes.
- **Six of the conventions script's ten checks now parse YAML for real.** `knowledge-conventions.py`, run through `uv run`, replaces grep and awk where they missed flow-style events. The other four stay shell, and without `uv` the script says which rules it skipped. The preflight reports a host holding one half without the other, and check 11 proves each rule.

### Fixed

- **The librarian's version check names a command that exists**: `uvx --from pip pip index versions lokf`, since `uv pip index` is not a subcommand.
- **A Windows checkout no longer blinds the conventions script.** It reads files with CRLF and a byte order mark stripped, and check 11 holds a CRLF bundle to the same verdict as LF.
- **A bundle reached through a link is read, not passed unread.** `find` never entered a linked `.lokf/knowledge`, so the conventions script and the preflight saw zero files; checks 11 and 12 plant one.
- **The preflight reads `commit.gpgsign` as git does**, taking `yes` and `1` as on and no `user.signingkey` as git's default key; all three scripts stop on one line under `sh`.
- **The gate refuses a `human:` id it cannot look up.** The schema accepts `human:-x`, and both the GitHub job and the forge-free script skipped such ids as unparseable, so an unsigned confirmation under one passed unseen.
- **The gate reads a confirmation whole, not its `by:` line.** Re-dating an existing event, moving its `revision`, or writing it in flow style left no added `by: human:` line and passed both gates; events are now compared whole between base and head, keyed by the concept's `id`, so a renamed concept keeps its confirmations and a copied one does not. Check 13 proves each.
- **The conventions script no longer aborts on a runner that ignores SIGPIPE.** GitHub Actions starts every step that way, so an awk that closed the frontmatter pipe early turned into a `tr: write error` that `pipefail` made fatal on the first long concept; the script now reads each file whole, and the contract's own job installs `uv` so the parser's half runs there too.
- **A confirmation spelt with a YAML tag, anchor, alias or quoted key was invisible to both gates** while `lokf validate` accepted it. Conventions rule 10 now holds `id`, `by`, `at` and `revision` to spellings a line reader and a parser agree on, so the `validate` check fails such a concept before the `provenance` check could miss it; check 11 proves it.
- **Both gates read merges, `generated`, and only the frontmatter.** Events are now read against every parent of a commit, from `verified` and `generated` and nowhere else, so a merge can no longer slip one in and an example in a body code fence no longer counts. Check 13 proves each.
- **A push to `main` between releases no longer promotes `## [Unreleased]` a second time.** When the top released version has no tag yet, `changelog-release.mjs promote` folds new entries into it by subsection instead of writing a second heading. The `plan` job also runs `check` directly, because semantic-release skips its plugin hooks on a pull request. Check 14 proves it.
- **`publish.yml` installs `uv`, so a release can pass the contract it runs.** Six conventions rules run through `uv run`, and without it no release could reach the tag. The contract now names that cause in one line up front.

## [0.18.0] - 2026-09-16

### Added

- **The registrar gate fails on a vanished source.** `knowledge-conventions.sh` gains a fifth rule: a `resource:` that is not a URL must name a file or directory that still exists under the repository root. Check 11 proves it on a bundle that breaks it; URLs are never fetched.
- **Two switches in the curation policy, both off by default.** `Independent re-check: <n>` lists n confirmed concepts, picked by a rule the curator cannot steer, for a second person to re-check. `Evidence first: yes` makes the docent quote the source before an answer resting on an unconfirmed concept.

### Changed

- **`docs/three-lines.md` is written for a governance reader.** It names the IIA in full, cites its 2026 Statement of Position, places each role in a diagram, and ends with what remains open and whose it is. The model's critics have a page of their own, `docs/three-lines-critics.md`.
- **Adopter-facing text no longer addresses "solo maintainers".** The sidecar's automation reference and the registrar workflow's comments describe the case - the confirming person also opens the pull request, so the gate's evidence is their signature - and the attestation environment's reviewers are "the people allowed to attest".
- **`EXAMPLES.md` is now `docs/examples/docent.md`**, one page per skill's captured sessions; `docs/examples/curator.md` is a placeholder that lists what is still to capture, including a docent answer under each value of `Evidence first:`.

## [0.17.1] - 2026-09-14

### Changed

- **`SECURITY.md` is a policy, not a threat model**: what executes here and what holds it, in a surface table that check 10 holds to a word budget. The shared design - hardening, the `human:` attribution gate, the prompt-injection guards - moves to `docs/threat-model.md`, which the sibling repositories link instead of restating; check 9 records the path.
- **The README is shorter, and its repository tree is now `docs/repository-layout.md`.** The README, `docs/` and the skills' prose no longer quote how many classes and relations LOKF has; the two enumerations check 7 compares stay the only places it is counted.
- **Three LOKF repositories, not four.** The shared pages and this bundle count `lokf-agent-skills`, LOKF Registrar and LOKF Curator; a host that installs the skills is not one of them.

## [0.17.0] - 2026-09-14

### Added

- **`validate-repository.sh` check 9: the paths sibling repositories link into.** LOKF Curator and LOKF Registrar deep-link files here and their link checks follow those URLs for real, so moving one passed every check here and broke their builds; the check now fails instead, and confirms its list is complete when the siblings are cloned alongside.
- **`docs/releasing.md` and `docs/signing-commits.md`** carry the release pipeline, the repository settings it depends on, and the signing walkthrough once for all four repositories; every `CONTRIBUTING.md` links there instead of repeating them. Check 10 holds this repository's `CONTRIBUTING.md` to a word budget, and CI fails an action not pinned to a commit.
- **`docs/three-lines.md`** maps the cast onto the three lines of defence for readers who work under that model, and says what an auditor can check and what the evidence does not show; the README and both plugins link to it.
- **`templates/scripts/knowledge-conventions.sh`, and the registrar gate runs it.** It checks what `lokf validate` cannot: one ISO-date log heading per day, quoted timestamps, `verified` as a list, and open questions in the curator's shape. `knowledge-registrar.yaml` runs it on every `.lokf/**` pull request, and check 11 proves it fails on each broken rule.

### Fixed

- **The librarian now lints the Markdown it writes.** Its rule against letting a wrapped punctuation dash start a line was advice only, and a pass tripped `MD032` in a host's lint gate anyway; the audit step now runs the host's markdownlint config over the bundle, since `lokf validate` reads a concept body as an opaque string and cannot see this class of fault at all.
- **One `log.md` heading per day, the bare date.** A suffixed heading such as `## 2026-09-14 (2)` is not the ISO-date heading OKF §9 requires, and the curator plugin cannot find the day through it. The librarian and the curator now reuse the day's heading.
- **The librarian's open questions take the curator's shape**, `- YYYY-MM-DD, process:lokf-librarian: ...`, so the date and actor lead and the first bullet the curator reads is the question.
- **The docent no longer takes a reader's identity from `git config user.name`** for a feedback entry - `gh api user` or nothing, the same rule the curator holds to.

## [0.16.1] - 2026-09-14

### Added

- **`lokf-librarian/references/domain-schema.md`**: how to extend the vocabulary into a domain - a LinkML schema importing a pinned `lokf.yaml`, `--schema` wired into the justfile and both workflows, both plugins' *Known LOKF types* settings told, and what it leaves undone for the graph. The curator's `domain-schemas.md` says when; this says how. Rule 3 now reads the host's justfile for a `--schema` and counts that schema's `Concept` descendants as vocabulary.

### Fixed

- **Rule 3 in `lokf-librarian/SKILL.md` listed fourteen classes, omitting `Role`**, while `README.md` and `docs/for-the-curious.md` said fifteen. Confirmed against the raw schema and corrected; the skills now teach one number.

### Changed

- **The curator's vocabulary-fit line respects a host's domain schema.** Where `.lokf/justfile` validates with `--schema <slug>.yaml`, `trust-fields.md` now has the skill read that file and count its `Concept` descendants as known - the same widening as Rule 3, so the line goes quiet once a team adopts a schema instead of naming every domain class a misfit. The label reads "doesn't fit the known vocabulary", matching the LOKF Curator plugin.
- **`lokf-curator/references/review-session.md` states how the curation-policy table is read**: class names match ignoring spaces and plural form ("Glossary terms" is `GlossaryTerm`), and an unknown class binds nothing. Written down because the LOKF Curator plugin matched literally and so ignored four rows of this file's own template.
- **`README.md` polished, not restructured.** Each role and label is said once, the plugin table maps onto the four levels of checking, and the Obsidian section moves to `docs/obsidian.md`.

## [0.16.0] - 2026-09-13

### Changed

- **One layout on every host.** `.lokf/knowledge/` is always the real folder, and the `knowledge_bundle` doorway link beside it is created by default again (Step 2). Step 0 no longer asks what kind of host it is in; Step 6 reports whether the doorway was made and the one command if not.
- **`just lokf-link`** creates or recreates that doorway, idempotently, refusing a name already taken. Its `visible` variable is gone.
- **`lokf-docent` gains `references/obsidian.md`**: the two-vault answer, plus `lokf-sidecar` named as the way to make a missing link. A missing link is never a feedback entry.
- **Shared-folder guidance consolidated** into `lokf-sidecar/references/portability.md`, Obsidian included: sync services carry `.lokf/` but drop links, so the doorway is per machine.
- **`README.md` restructured.** "Where the bundle lives" (host-agnostic) and "…and where it meets an Obsidian vault" (optional, two vaults) replace the combined section; "For the curious" moves to `docs/for-the-curious.md`.

### Removed

- **The visible layout** (0.15.0) - a real `knowledge_bundle/` folder inside a vault. Obsidian indexes it like any other folder, so the exhibition leaked into the workshop's link suggestions, graph and search. Step 0's host decision, the `visible` variable and two layout-test cases go with it.
- References to the maintainer's private vault: the family this repository describes is the four skills and the two plugins.

## [0.15.0] - 2026-09-12

### Changed

- **`lokf-curator/references/domain-schemas.md`** gains "When the domain already has a schema": a domain schema imports a domain's existing LinkML vocabulary beside LOKF's rather than re-describing it. Whether provenance fields belong on domain records is left to the domain's owners and OKF.
- **`lokf-scaffolding` renamed `lokf-sidecar`**, matching what it produces: directory, frontmatter, install commands, this repository's own bundle, and every cross-reference. A bundle already laid down needs nothing - the files it wrote are identical.
- **Corrected Obsidian guidance for `knowledge_bundle`**: the link is opened *itself* as a vault, never the repository root (Obsidian skips a symlink resolving inside the vault it's indexing, and never indexes a dot-folder). Linking a repository's `.lokf/knowledge` *into* a personal vault - the reverse direction - is supported and now documented.
- **`README.md`** gains "Where the skills meet an Obsidian vault": the bundle's two names and which is real per host, a plugin-for-skill table, and the vault-as-**workshop**/bundle-as-**exhibition** framing. "The fifth role" no longer calls LOKF Curator a registrar: it is the curator's assistant, and the curator is always a person.
- **LOKF Enforcer is now LOKF Registrar** (repository `obsidian-lokf-registrar`), renamed for its role before its first release, wherever the README, the skills and this repository's bundle name it.

### Added

- **`lokf-sidecar` lays the bundle down by host.** Two names, one real folder: `.lokf/knowledge` (what the tools address) and `knowledge_bundle` (what people and Obsidian open). A code repository keeps the hidden folder real with `knowledge_bundle` as the doorway link; a notes vault or shared folder (Step 0 asks) makes `knowledge_bundle/` real and `.lokf/knowledge` the link - detected by both plugins with nothing to configure.
- **`just lokf-link`** recreates the visible layout's link where a sync service drops it, follows a new `visible` variable for a vault nested inside its repository (e.g. `../vault/knowledge_bundle`), and refuses a dangling link instead of failing on `ln`.
- **`scripts/test-sidecar-layouts.sh`**, run by the repository-contract check: builds throwaway hosts in both layouts and pins the wrapper's boundary check, the librarian workflow's change detection and packaging, the registrar's triggers, and `lokf-link`, all against both bundle names.
- **`lokf-librarian`** now leaves LOKF Registrar's Obsidian affordances alone by rule - the `<!-- lokf:related -->` block and the `diataxis.md` map - and addresses the bundle by both paths when scoping a diff or PR.
- **Semantic release**, version and changelog only: the version is computed from Conventional Commits on `main`, and `CHANGELOG.md`'s `## [Unreleased]` section is promoted into a dated heading. It never tags - `gh skill publish` remains the one tag creator - and `publish.yml` now refuses a typed version that disagrees with what was promoted. See [docs/releasing.md](docs/releasing.md).

### Fixed

- The librarian wrapper and both workflow templates name the bundle under **both** `.lokf/knowledge` and `knowledge_bundle`: a git pathspec never traverses a symlink, so the visible layout previously went undetected. `git add` is guarded against a pathspec matching nothing.
- Windows guidance now prefers a junction (`mklink /J`, no elevated rights, followed by Obsidian like a symlink) over the Developer-Mode `mklink /D` note.

## [0.14.0] - 2026-09-12

### Security

A `human:<id>` verification is a claim any writer can type, not a credential, and `lokf validate` passes a forged one since it is well-formed - so "confirmed by a person" was forgeable by anything able to steer `lokf-curator` or edit the bundle directly.

- `knowledge-registrar.yaml` gains a `provenance` job: every `human:` actor a PR newly adds under `.lokf/knowledge/` needs forge-held evidence - an APPROVED review from that account, or, when they authored the PR, a signature of theirs on the introducing commit, checked via GitHub's API (a runner has no keyring, so `git log %G?` can't do this locally). The load-bearing change; the rest is defence in depth.
- Solo maintainers take the signature branch (three `git config` lines, documented in `references/automation.md`); an optional `attestation` job gates on a GitHub Environment's required reviewers instead for a repository that can't sign - deliberately not a switch that disables the check, since an environment reviewer may be the PR's own author.
- `lokf-curator` resolves identity from `gh api user` only - the spoofable `git config user.name` fallback is gone - and Step 2 now refuses to run unattended (CI, a headless session, a subagent, a scheduled task); Step 1 stays read-only and safe anywhere.
- `lokf-sidecar` and `lokf-curator` now report whether commit signing is on before a solo maintainer spends twenty minutes on confirmations the gate will reject, and `lokf-curator` Step 1 reports a *Not tied to a signed commit* count on existing `human:` events - both report only, never touch `git config`.

### Fixed

- `lokf-curator` and `README.md` said LOKF has 14 built-in classes; the installed schema has 15 - `Role` was missing from every count and enumeration. Corrected in the class list, the vocabulary-fit label, and the "vocabulary stops fitting" paragraph.

### Added

- `lokf-sidecar` Step 2 now also creates a `knowledge_bundle` symlink to `.lokf/knowledge` at the repo root, a visible entry point for folder pickers that hide dot-directories, Obsidian's "Open folder as vault" among them. `templates/gitignore` excludes the `.obsidian/` folder Obsidian writes through it, and the lint and link checks skip the aliased files.

## [0.13.0] - 2026-09-10

- The librarian SKILL now says a spaced dash ("X - Y") must not land at the start of a line after wrapping, where Markdown reads it as a list item and trips `MD032/blanks-around-lists`. Reword or rewrap so the dash stays mid-line.
- `.markdownlint-cli2.jsonc` disables `MD060` (table column style): it flags the padded-header/bare-separator table style used everywhere in this repo (and on GitHub generally) as inconsistent, and no `style` setting reconciles the two without just relocating which row gets flagged. `.lokf/README.md`'s concept checklist gained a reminder not to let a spaced dash wrap onto its own line, since Markdown reads that as a list item (`MD032`).

## [0.12.0] - 2026-09-10

### Changed

- Renamed the `knowledge-validate.yaml` CI gate (and its scaffolding template counterpart) to `knowledge-registrar.yaml`, to name it for the registrar role it actually performs - keeping bundle records well-formed, never judging whether their content is true. Updated every cross-reference, including `README.md`'s own "fifth role" paragraph, which now names the gate directly. A repo that already scaffolded the old filename keeps working; re-scaffolding (or a manual rename) picks up the new name.

### Fixed

- Each `SKILL.md` (`lokf-curator`, `lokf-docent`, `lokf-librarian`, `lokf-sidecar`) now declares `license: Apache-2.0` in its frontmatter, matching this repository's `LICENSE`. Fixes the `recommended field missing: license` warning `gh skill publish` raised on all four skills during the `v0.11.0` release.

## [0.11.0] - 2026-09-10

### Security

- `knowledge-librarian` workflow now runs a fixed, reviewed in-repo script (`bash .lokf/scripts/knowledge-librarian.sh`) instead of an arbitrary command string from a repository variable, so changing *what executes* goes through code review rather than an unreviewed Settings edit.
- `knowledge-librarian` workflow split into two jobs: the agent (third-party code) runs in a `contents: read` job with no persisted git credentials and hands its proposed change to a separate privileged job - which runs no agent code - as a patch artifact. Only that job holds `contents: write` / `pull-requests: write`, so a compromised agent cannot reach a write-scoped credential. Top-level workflow permissions now default to none.
- `knowledge-librarian.sh` wrapper now parses `AGENT_CLI` into a quoted argv array (removing the unquoted expansion that word-split the value at the command position) and enforces the bundle boundary after the agent runs: it fails if the agent modified any path outside `.lokf/knowledge/` (`.lokf/feedback.md` allowed), so the "edit only the bundle" contract is enforced, not merely requested.

### Changed

- Arm the scheduled librarian run with the `KNOWLEDGE_LIBRARIAN_ENABLED` repository variable set to `true` (replaces `KNOWLEDGE_LIBRARIAN_CMD`); `AGENT_CLI` is unchanged. Updated the `lokf-sidecar` templates, the dogfooded workflow, the wrapper-script header, and the `lokf-sidecar`/`lokf-librarian` automation docs to match.

## [0.9.0] - 2026-09-09

Initial release: four [Agent Skills](https://agentskills.io/home) that turn a repository's scattered knowledge into a maintained, trusted [LOKF](https://lokf.nolan-nichols.com/) knowledge bundle - built once, kept current, and reviewed by a person, rather than rediscovered every session.

- `lokf-sidecar` - bootstraps a fresh `.lokf/` sidecar into a repository that has none: tooling, docs, and a dummy skeleton from bundled templates.
- `lokf-librarian` - scrapes the repository, derives concepts with their sources, wires typed relationships, audits the bundle against the LOKF schema, and hands off for review. Runs often, including on a schedule; deals in facts about the repository, never in verdicts about truth.
- `lokf-curator` - a human curator's assistant: a one-screen trust and freshness report, and an opt-in review session that records a person's confirm/correct/retire/send-back verdict directly in the bundle's frontmatter.
- `lokf-docent`, the reader's entry point. It answers from the bundle first with each concept's trust label, verifies exact values at the source, and records a gap in `.lokf/feedback.md` for the librarian when the bundle has no answer. [`docs/examples/docent.md`](docs/examples/docent.md) has real transcripts.

This repository dogfoods its own skills: `.lokf/` here is a real bundle built by `lokf-sidecar` and `lokf-librarian`, self-describing all four skills, this repository's own governance, and its CI.
