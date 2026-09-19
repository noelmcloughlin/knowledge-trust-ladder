# Changelog

All notable changes to this repository are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows the rules in [README.md](README.md#versioning). All skills release together under one tag.

## [Unreleased]

### Changed

- **The relation audit uses the toolkit's own flag.** `just lokf-check-refs` ran a hand-written SPARQL query; both justfiles and both registrar workflows now call `lokf validate --check-refs`.
- **An external `source` or `definedBy` is no longer a dangling target.** Both slots are documented as taking an off-site URL; the query reported them as missing concepts.
- **The predicate list cannot go stale again.** `--check-refs` reads the relation slots from the schema, so reified `relations` and a domain schema's own slots are covered too.
- **The registrar gate validates once.** `--check-refs` rides on the existing validate step, replacing a second `lokf validate` run through `uvx --from rust-just just`.
- **A domain schema passes `--schema` to `lokf-check-refs` too.** The librarian's recipe said that audit was unaffected by one, which stopped being true when it moved onto `lokf validate`.

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

- **The librarian wrapper restores `.git/config` and `.git/hooks/` on every exit.** The restore ran only after a clean return, so an agent that poisoned `core.hooksPath` or `core.fsmonitor` and then exited non-zero, or a cancelled job, left them in the checkout for the workflow's next steps to read. An `EXIT` trap now restores on failure and on the runner's signals; the layout tests prove both. Reported by a Socket audit on skills.sh.

## [0.19.1] - 2026-09-17

### Fixed

- **A pull request that would release must be titled to release.** A squash merge takes its subject from the pull request title, and GitHub's default title carries no type, so a typed `fix:` reached `main` untyped and released nothing. The `plan` job now refuses that combination and says how to retitle.

- **The no-Python schema fallback is pinned to the toolkit's version.** Both skills, the sidecar README and the toolkit concept pointed at `lokf.yaml` on upstream `main`, which has already moved past the 0.8.0 floor, so a manual cross-check read a schema the installed validator does not enforce. The URL now names the `v0.8.0` tag and the librarian's tooling-version step moves it with the floor; this also answers a skills.sh audit finding about an unpinned runtime URL.

- **A pull request that releases nothing is no longer failed for writing no release notes.** The `plan` job's new changelog check ran on every pull request, so a `chore:` or `docs:` one - a Dependabot action bump among them - failed against the empty `## [Unreleased]` a release had just emptied. It now reads the pull request's own commits and asks for notes only when one of them would release.
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

- **The skills use lokf 0.9.0+'s `revision`.** The curator writes it on a confirmation and the librarian on `generated` (the full commit hash of a file, an ETag or digest for a URL), the docent quotes it beside the date, and `docs/three-lines.md` moves "which state of the source was the check made against" from an OKF gap to a recorded answer. On an older toolkit the key is left out. The librarian's field tables also name `excerpt` on a source, and the domain-schema page says an undeclared type now projects as `lokf:Concept`.
- **The sidecar's toolkit floor is lokf 0.8.0**, here and in the `lokf-sidecar` template. The librarian's field tables now state its constraints: `sources[].author` is an actor string, `http_method` is one of seven uppercase verbs, and every timestamp including `stale_after` is a datetime, a bare date meaning midnight UTC.
- **The curator says what it can record before offering a session**, from a *Ready to record* line with three identity routes - `gh`, `glab`, the signing key the forge lists - and a rule for a host with no forge. The librarian names files in lowercase and hands off on a host without git; the docent's feedback attribution names the same routes.
- **Six of the conventions script's ten checks now parse YAML for real.** `knowledge-conventions.py`, run through `uv run`, takes over the quoted-`at`, `verified`-shape, open-question, duplicate-`id`, closed-frontmatter and plain-spelling rules from grep and awk, which missed a flow-style `verified` and a multi-line flow item; the other four stay shell, needing nothing but bash and git, and without `uv` the OK line says which rules were skipped. The sidecar lays it down beside the `.sh` (Step 5's seventh file), and the preflight reports a host holding one without the other. Check 11 proves each rule on the layouts that used to slip.

### Fixed

- **The librarian's version check names a command that exists**: `uvx --from pip pip index versions lokf`, since `uv pip index` is not a subcommand.
- **A Windows checkout no longer blinds the conventions script.** It reads files with CRLF and a byte order mark stripped, and check 11 holds a CRLF bundle to the same verdict as LF.
- **A bundle reached through a link is read, not passed unread.** `find` never entered a linked `.lokf/knowledge`, so the conventions script and the preflight saw zero files; checks 11 and 12 plant one.
- **The preflight reads `commit.gpgsign` as git does**, taking `yes` and `1` as on and no `user.signingkey` as git's default key; all three scripts stop on one line under `sh`.
- **The gate refuses a `human:` id it cannot look up.** The schema accepts `human:-x`, and both the GitHub job and the forge-free script skipped such ids as unparseable, so an unsigned confirmation under one passed unseen.
- **The gate reads a confirmation whole, not its `by:` line.** Re-dating an existing event, moving its `revision`, or writing it in flow style left no added `by: human:` line and passed both gates; events are now compared whole between base and head, keyed by the concept's `id`, so a renamed concept keeps its confirmations and a copied one does not. Check 13 proves each.
- **The conventions script no longer aborts on a runner that ignores SIGPIPE.** GitHub Actions starts every step that way, so an awk that closed the frontmatter pipe early turned into a `tr: write error` that `pipefail` made fatal on the first long concept; the script now reads each file whole, and the contract's own job installs `uv` so the parser's half runs there too.
- **A confirmation spelt with a YAML tag, anchor, alias or quoted key was invisible to both gates** while `lokf validate` accepted it. Conventions rule 10 now holds `id`, `by`, `at` and `revision` to spellings a line reader and a parser agree on, so the `validate` check fails such a concept before the `provenance` check could miss it; check 11 proves it.
- **Both gates read merges, `generated`, and only the frontmatter.** A merge commit listed no changed paths, so an event added in one passed the forge-free gate unseen; a human `generated` record - the curator's Correct writes one - was a claim only when written as a `by:` line; and a `by: human:` in a body code fence counted as one. Events are now read against every parent of a commit, from `verified` and `generated`, and from nowhere else. Check 13 proves each.
- **A push to `main` between releases no longer promotes `## [Unreleased]` a second time.** `semantic-release.yml` computes the version from the last *tag*, and only `publish.yml` tags, so two qualifying merges without a publish between them promoted the same version twice, leaving two `## [0.19.0]` headings and orphaning the second push's entries above an empty `[Unreleased]`. `changelog-release.mjs promote` now folds into the top released section instead of inserting a new one when that section's version carries no tag yet, merging by subsection in Keep a Changelog order. Check 14 proves it, and repairs the two headings this bug had already written. The `plan` job also runs `changelog-release.mjs check` directly, since semantic-release skips its own plugin hooks - including this one - on a pull request and would otherwise let an empty `[Unreleased]` merge, contrary to `docs/releasing.md`'s claim.
- **`publish.yml` installs `uv`, so a release can pass the contract it runs.** Six of the conventions script's ten rules run through `uv run`, and the publish job never installed it, so every expectation for those rules failed and no release could reach the tag - `validate.yml` had the same gap and was fixed, the release path was missed. The contract now also names that cause in one line up front, instead of leaving fifteen expectations reporting only that they "failed to report" something.

## [0.18.0] - 2026-09-16

### Added

- **The registrar gate fails on a vanished source.** `knowledge-conventions.sh` gains a fifth rule: a `resource:` that is not a URL must name a file or directory that still exists under the repository root. Check 11 proves it on a bundle that breaks it; URLs are never fetched.
- **Two switches in the curation policy, both off by default.** `Independent re-check: <n>` makes every curator report list n confirmed concepts, picked by a rule the curator cannot steer, with their sources for a second person; `Evidence first: yes` makes the docent quote the source before any answer that rests on a concept not yet confirmed by a person, and the docent reads that line from the policy alone. The sidecar's automation reference recommends a pull request template line asking a curation PR's approver to open the sources; this repository's template carries it.

### Changed

- **`docs/three-lines.md` is written for a governance reader.** It names The Institute of Internal Auditors in full, cites the 2026 Statement of Position, places each role in a new diagram (`.assets/lokf-three-lines.svg`), and ends with what remains open and whose it is. The model's critics, quoted from their own texts and marked as preliminary research, and a bundle's answer to each with every remaining gap labelled by kind, are on a page of their own, `docs/three-lines-critics.md`.
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
- **`templates/scripts/knowledge-conventions.sh`, and the registrar gate runs it.** `lokf validate` reads a body as an opaque string and never opens `log.md`, so the four conventions the skills and plugins rely on - one ISO-date log heading per day, quoted timestamps, `verified` as a list with one librarian event, open questions in the curator's shape - are now a script the sidecar lays down and `knowledge-registrar.yaml` runs on every `.lokf/**` pull request, alongside the justfile's `lokf-check-refs`. Check 11 of the repository contract holds this repository's copies identical to the templates and proves the script fails on a bundle that breaks each rule; actionlint is pointed at the templates by path.

### Fixed

- **The librarian now lints the Markdown it writes.** Its rule against letting a wrapped punctuation dash start a line was advice only, and a pass tripped `MD032` in a host's lint gate anyway; the audit step now runs the host's markdownlint config over the bundle, since `lokf validate` reads a concept body as an opaque string and cannot see this class of fault at all.
- **One `log.md` heading per day, the bare date.** The librarian had been opening a fresh `## 2026-09-14 (2)` heading for each run in a day; that is not the ISO-date heading OKF §9 requires, passes the registrar's date check unseen, and the curator plugin cannot find the day through it. The librarian and the curator's review session now both reuse the day's heading, and the librarian's log bullets are held to a few sentences.
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
- **`README.md` polished, not restructured.** Role names carry the emphasis; the docent's job and the trust labels are each said once; the plugin table maps onto the four levels of checking; *Where the bundle lives* is a section of its own; the layout lists every workflow and the measured size of each `SKILL.md`. The Obsidian section moves to `docs/obsidian.md`, with the two-vaults picture the plugin READMEs use, and the README keeps one paragraph and a link.

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

- **`lokf-curator/references/domain-schemas.md`** gains "When the domain already has a schema": a regulated domain may already have a LinkML vocabulary of its own and a domain schema then imports it beside LOKF's rather than re-describing it. What such a vocabulary lacks - who encoded a record, who confirmed it, when to look again - OKF v0.2 defines for documents only; whether it belongs on domain records is left to the domain's owners and the OKF specification. The README's summary line points at the new section.
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

- `lokf-sidecar` Step 2 now also creates a `knowledge_bundle` symlink to `.lokf/knowledge` at the repo root (POSIX hosts) - a visible entry point for humans and their tools, chiefly Obsidian's "Open folder as vault," which like most OS folder pickers hides dot-directories by default. Mirrors the Step 0 tracked/gitignored decision; `templates/gitignore` now excludes the `.obsidian/` folder Obsidian writes through the link into `.lokf/knowledge/` when used as a vault. This repository's own `.lokf/` now carries the symlink too, with matching excludes added to `.markdownlint-cli2.jsonc`, `lychee.toml`, and the `codespell` step so the aliased files aren't linted/checked twice.

## [0.13.0] - 2026-09-10

- The librarian SKILL now says: A spaced dash ("X - Y") used as punctuation must not be allowed to land at the start of a line after wrapping - Markdown reads a line beginning `-` followed by a space as a list item, so a paragraph never meant to be a list trips `MD032/blanks-around-lists` wherever the consuming repo lints `.lokf/**` (most do, via a `lint-and-docs`-style gate). Reword or rewrap so the dash stays mid-line; when unsure, prefer an unwrapped single line over one that risks the break landing there.
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
- `lokf-docent` - the reader's entry point. Answers questions from the bundle first, states each concept's trust label in plain words, verifies exact values at the source, and - when the bundle has no answer - explores the repository directly and records the gap in `.lokf/feedback.md` for the librarian to pick up. See [`docs/examples/docent.md`](docs/examples/docent.md) for real question-and-answer transcripts.

This repository dogfoods its own skills: `.lokf/` here is a real bundle built by `lokf-sidecar` and `lokf-librarian`, self-describing all four skills, this repository's own governance, and its CI.
