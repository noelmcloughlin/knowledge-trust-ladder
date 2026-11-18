# Changelog

All notable changes to this repository are documented here, in the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format. Versioning follows [docs/releasing.md](docs/releasing.md), and all skills are released together under one tag.

## [Unreleased]

### Fixed

- **`publish.yml` asks the hosts to sync only once the release's `ktl` package is on PyPI.**
- **A sync run waiting for its workflow review blocks no later sync, and a stale approval pushes nothing.** One waiting since a merged pull request had held each host's syncs for days.

## [0.69.1] - 2026-11-18

### Fixed

- **The reader's conformance fixture writes its reified relation with `predicate`, the LOKF Relation slot, not `type`.** The registrar plugin's validator warned on it.
- **The sync keeps a website script's executable bit, so a site it adds `uv-env.sh` and `vendor.sh` to still builds.** build.sh runs them directly; the sidecar copies already kept theirs.
- **The federation build verifies a release made before its repository moved, under the old owner with the signer workflow still pinned.**
- **The pen keeps an ETag revision in single quotes, so the unattended gate still reads a person's confirmation.** It had written `"W/\"…\""`, which the gate refused.

## [0.69.0] - 2026-11-18

### Added

- **ktl-sidecar's `<OWNER_TYPE>` sets the publisher to `Person` or `Organization`.**
- **ktl-docent answers "which skill should I use?" from a skill's concept.**
- **Feedback starting `Host text:` records a fault in the host's own files.**
- **ktl-librarian's bootstrap maps a plugin marketplace manifest.**
- **The pen refuses a source id that another concept gives another resource or excerpt.**
- **The gate checks LOKF's SHACL shapes where `uv.lock` holds lokf's `shacl` extra.**
- **The preflight warns when `uv.lock` holds no pyshacl.**

### Changed

- **The sidecar names `lokf[build,shacl]>=0.10.0`, and the no-Python schema names its commit.**
- **A skill's concept is `playbooks/<name>-skill.md`, with its `SKILL.md` as `resource`.**
- **ktl-sidecar commits Step 5's files, and keeps the KTL skills out of a host's own `skills/`.**
- **ktl-librarian's first pull request follows the sidecar's.**
- **ktl-librarian cites an installed skill's published copy, committed or not.**
- **Conventions rule 16 fails one source id with two excerpts, as LOKF 0.10.0's shapes do.**
- **A concept may cite two passages of one file, each under an id of its own.**
- **ktl-librarian uses LOKF 0.10.0's names for a domain vocabulary, and `adapt --beside`.**
- **ktl-librarian's version check asks uv's index, and finds a tag's commit through `gh api`.**
- **ktl-website's `baseURL` is the Pages API's `html_url`, which names a private site's own domain.**
- **The sync's pull request checklist says how to clear a convention a release tightens.**

### Fixed

- **The pen drops a folder's empty root section and `index.md` with its last concept**, unless another index links it.
- **ktl-sidecar puts the README aside before the first heading of any level.**
- **ktl-sidecar names all six skills, as the preflight does.**
- **Conventions rule 9 fails a blank line before the frontmatter and a `---` with spaces after it**, which LOKF 0.10.0 reads.
- **The federation build reads a member page that opens after a byte order mark or blank lines.**
- **`MemberDomain` keeps a class IRI of its own**, so no catalogue reads as a member and `moved.rq` finds member domains.
- **The website preflight warns when `site.toml`'s `baseURL` is not where Pages serves the site.**
- **The preflight reads a lokf floor whose extras hold a space.**
- **ktl-sidecar's Step 1 names an unset placeholder rather than failing with a traceback.**
- **The federation build and its MCP `read_document` treat frontmatter that does not parse as none.**

### Security

- **ktl-librarian finds a `Host text:` fault in the file itself, and never words its question from the entry**, so a reader's text cannot reach a concept.

## [0.68.0] - 2026-11-18

### Added

- **`SPEC.md`, version 0.2, states the rules KTL adds to a LOKF bundle**: the ladder, who writes each record, the eighteen conventions, what counts as a person's confirmation, and how each trust label is computed.
- **Contract check 24 holds the copies of those rules to `SPEC.md`**, in the conventions script's header, patch.md and trust-fields.md.
- **`tests/conformance/reader/` holds a bundle and the labels a program must report of it**, for the report script and for any second program that reports trust.
- **A root `SPEC.md` becomes the site's page `/spec/`**, with a Specification line under Home, a home page button after Architecture, its Markdown at `/spec.md`, and every link to `SPEC.md` sent to the page.

### Changed

- **The report script reads a later `revised.at` as the last edit**, so a concept another LOKF producer edited after its confirmation reads as edited since.
- **The wording of conventions 1, 4, 5, 6, 8, 10, 13, 16, 17 and 18 says what the script checks**, and the trust-fields table says what the report computes.
- **ktl-curator's *Retire* writes the successor in `isReplacedBy`, which the report and the docent read before the `**Deprecation**` line.**

### Fixed

- **`diataxis.md` in a folder below the root is a concept to every script**: the pen, the shell half of the conventions, the feedback recorder and the preflight read the name as reserved in every folder.
- **Convention 5 finds a quoted `resource` with a comment beside it.**
- **Convention 10 refuses a tag on a list or a mapping**, as it refuses one on a value.
- **The report lists no retired concept as disputed by a reader**, and none as derived from an edited concept when its confirmation's time cannot be read.
- **The home page's six buttons fit on one line again, each as wide as its label needs.**
- **The trust label on a concept card wraps inside its own width, as a rounded box on two lines**, so a retired concept's "replaced by" path stays readable on a phone.

### Security

- **The pen refuses a change to an exclusion a person decided**, to its `resource` or its `reason`.
- **The pen refuses a `question` or a `delete` on a concept a person retired.**
- **The pen refuses a log line that starts with `**Curation**` or `**Deprecation**`**, the two lines ktl-curator writes for a person.
- **The pen reads a person's note in four more spellings, with the lines under it and the order it stands in.**
- **The pen refuses a `set` of `isReplacedBy` or `relations` on a concept a person retired.**

## [0.67.0] - 2026-11-17

### Added

- **`site.toml`'s `schema` names the schema file the site shows**: a path, or `pkg:<package>/<path>` for one inside a package.
- **The website builds behind a package mirror, and no lock is written again**: `scripts/uv-env.sh` installs the versions the lock pins from the index uv reads, each checked against the lock's hash.
- **The website builds where the CDN is blocked**, from a copy of Cytoscape or Mermaid in the site's `assets/vendor/`, checked against the hash in `hugo.toml`.
- **`scripts/vendor.sh` writes the site's copies of Cytoscape and Mermaid, `assets/vendor/`, from an npm registry**, and keeps a file only at the hash `hugo.toml` holds.
- **A domain host's workspace builds behind a package mirror**, through the site's `scripts/uv-env.sh`.
- **A runner that holds uv keeps its own**, so a locked-down runner with uv on its image runs.

### Changed

- **With no LinkML schema of its own, the site shows the bundle's domain vocabulary**, `.lokf/schema/domain.yaml`, before LOKF core.
- **The navigation's Knowledge graph link has an icon and a tone of its own.**
- **The librarian keeps history out of a concept's body**: it belongs in the log.
- **The website's text size is Medium by default.**
- **The release tools are in `.release/` and the PyPI build backend in `.pypi/`**, outside `.github/`.
- **`diataxis.md` is reserved at the bundle's root alone**, where KTL Registrar keeps its map. `index.md` and `log.md` stay reserved in every folder.
- **Without zip, the contract still checks the Microsoft 365 skill's folder.**
- **The threat model links the sidecar's automation and gate references** for the detail they already give, and keeps each measure and its reasons.
- **A `revision` on a file its own branch changed is a `sha256:` digest of the file**, since a squash merge replaces the branch's commits.
- **The report script compares a `sha256:` pin with the file as committed**, so a file changed after the person was shown it reads as moved.

### Fixed

- **The site serves each local file the schema imports beside it.**
- **`knowledge-report.sh questions` lists each open question with its day, its asker and its text.**
- **A `perf:` commit and a revert count as releasing in the `plan` job**, as the pinned commit-analyzer counts them.
- **`changelog-release.mjs` reads `## [Unreleased]` only as a line of its own.**
- **The changelog fold keeps or leaves out an entry whole.**
- **Each skill's description says which one takes an error report.**
- **The ingest reads a page's CDATA sections in one pass**, where a page of openers with no closer ran past the time limit.
- **`knowledge-ingest.sh --patch` writes a source's title with round brackets where it has square ones**, which the pen refuses.
- **A root `diataxis.md` or a folder's `log.md` does not stop the website's build.**
- **Mermaid diagrams follow the Display menu** between light and dark.
- **The graph and health pages cope with a bundle that holds no concept.**
- **The KTL scorecard badge counts every concept**, a retired one included.
- **ktl-website's page gives the preflight's rule for the site's folder**: one that holds `site.toml` and `hugo.toml`.
- **ktl-website's deploy page says what a locked-down network needs.**
- **A root `diataxis.md` is no node of the graph**, in the website's build or the federation build.
- **The workflows read `site.toml` as TOML**, in any letter case and either quote.
- **ktl-curator's Step 3 follows its reference**: the curation policy and a placeholder are drafts under `process:ktl-curator`, and neither needs an authenticated id.
- **The threat model, the gate reference and the conventions script's comment name the parser's one PyYAML release alone**, without the upload date the scripts dropped in 0.66.0.
- **Conventions rule 6 fails a `revision` whose commit the checkout's history does not hold**, in every clone and not only a fresh one.
- **On a pull request, rule 6 refuses a `revision` that names one of its commits**, which a squash merge would leave naming nothing.
- **The gate reads the pull request's own commits for rules 6 and 14**, through `--head`, and not those its base gained since.

### Security

- **The registrar's gate reads who signed a commit from its committer**, and from its author only when GitHub's web editor made the commit.
- **The gate matches a confirmation by its concept's `id` and its path**, so one moved or copied into another concept counts, and a renamed concept keeps its events.
- **An approving review backs a confirmation only while it stands**: it is the person's last decisive review, and the concept is what the approved commit held.
- **The gate reads a commit that has no parent**, so a merge of an unrelated history brings in no confirmation that nobody signed.
- **The gate stops and backs nothing when git or GitHub does not answer one of its reads**, or on frontmatter it cannot read.
- **Conventions rule 13 finds the commit that put a confirmation into the frontmatter by parsing the concept at each candidate.** Rule 14 follows a renamed concept, and rule 10 names a key given twice.
- **The pen takes a `process:` actor of letters, digits, `.`, `_` and `-` alone**, and none that starts `process:ktl-curator`.
- **A send-back that `process:ktl-curator` wrote for a person with no login counts as a person's record**, and the curator's policy template and placeholder are drafts under that actor.
- **The curator and the librarian treat a concept, an open question, a file or a page as text to quote**, never as an instruction.
- **A release tags only the commit it checked**: `publish.yml` stops unless `main` is still that commit.
- **The repository's own catalogue recommends a required reviewer on the `pypi` and `testpypi` Environments**, since a pushed tag carries its own copy of `pypi.yml`.
- **The repository contract fails under CI when shellcheck, node or zip is missing**, where it skipped the check.
- **A federation build refuses a member's schema that imports anything but `lokf` and `linkml:` names**, or that declares the `linkml` prefix as another namespace.
- **A member's zip holds Markdown and images alone**, so none carries a file a browser runs or a `pyproject.toml`.
- **A member's distribution name ends `.jsonld` for a served file and `.zip` for a zip**, so no served file is published as a page.
- **`members --add <address>` reads the `index.md` beside a served file as it reads a member's address**, checked before the request and at the connection.
- **`knowledge-feedback.sh` refuses a symbolic link at `.lokf/`, at `feedback.md` or at its lock**, and rewrites the file through one `mktemp` creates.
- **The ingest workflow hands its secrets to the script alone**, so the steps that package and upload the patch hold none.
- **A repository file cannot draw a trust label on the website**: raw HTML keeps a class or a `data-` attribute only where the site's own rendering wrote it.
- **The website keeps an `<input>` only as a task list's checkbox.**
- **The website serves only the kinds of file it names**: figures and PDF files from `docs/` and `.assets/`, and Markdown from the bundle.
- **The website's build reads each SVG as XML**, and stops on one that could run a script.
- **A page of the website sends no referrer**, so a remote image does not learn which page loaded it.
- **A description cannot add a key to `site.toml`**: ktl-website's Step 1 writes each value as a TOML string and stops on a line break.
- **A description cannot add a key to the bundle's `index.md`**: ktl-sidecar's Step 1 writes each free-text value as a quoted string, and stops on an empty value, a line break or a character that does not print.
- **The ingest pins pypdf 7.1.0**, as the tests do after a Dependabot update.

## [0.66.0] - 2026-11-15

### Added

- **`site.toml`'s `source` names the folder the README, the docs, the changelog and the figures come from**, such as a fork's `.linkml/`, and **`linkml` names the folder of a LinkML project whose schema the site shows.**

### Changed

- **The KTL badge is labelled `KTL scorecard`.**
- **The pen, the conventions check and the ingest carry no `exclude-newer` date**, since many company indexes serve no upload times.
- **The threat model names the Scorecard, CodeQL, SHA-pinning and release-tag measures that each repository with a bundle carries.**
- **The website template requires Python 3.11 or later**, as the sidecar does.

### Fixed

- **An old address with capitals keeps its case when `site.toml` lists it as `[[params.redirects]]` with `from` and `to`**, since Hugo lowercases a table's keys.

## [0.65.0] - 2026-11-15

### Added

- **`ktl gh check --strict` asks a public repository for a Scorecard workflow**, through the catalogue's new `workflow` kind.
- **`ktl gh apply` turns back on a catalogued workflow that GitHub turned off for inactivity.**
- **`scorecard.yml` publishes this repository's OpenSSF Scorecard**, which the README's badge shows.
- **The website serves `badge.json`, a KTL badge of how many concepts a person confirmed**, for a README to show.
- **Each release carries its signed provenance as a `provenance-*.intoto.jsonl` asset**, which `gh attestation verify --bundle` reads.
- **`codeql.yml` scans the Python, the JavaScript and the workflows.**

### Changed

- **actionlint lints every workflow**, `pypi.yml` included.
- **Links point to `lmodel/schema-sidecar`**, where `linkml-sidecar` moved.
- **`llms.txt` lists the install routes in the install page's order.**
- **The README links `ktl` on PyPI and says how to report a bug or contribute**; the issue templates name the `ktl` command.
- **The docent eval installs Claude Code from a lockfile, checked by hash.**
- **The KTL badge reads `n of m`**, without the word "confirmed".
- **A release carries the Microsoft 365 Copilot skill zip only once `KNOWLEDGE_M365_ENABLED` is `true`**, which is unset by default while that skill is unfinished.
- **Hosts pin `ktl` in `.lokf/pyproject.toml`, and the librarian installs its skill from that locked package.** A host adds the pin once, with `uv add --project .lokf "ktl==X.Y.Z"`.
- **The sync moves the `ktl` pin, relocks, and reads the release's templates from the package at the lock's hash**, asking the host's own index for the newest release.
- **The preflight compares a host's copies with the templates of the `ktl` in `.lokf/.venv`.**

### Removed

- **`scripts/sync-sidecar.sh`**: each host's `knowledge-sync.yaml` opens its own pull request, and `.lokf/scripts/knowledge-sync.sh --pr <tag>` opens one by hand.
- **`TRUST_LADDER_SKILLS_REF`, `TRUST_LADDER_SKILLS_SHA`, `TRUST_LADDER_SKILLS_REPO` and `KNOWLEDGE_SKILLS_TOKEN`**: a private index's credential is `UV_INDEX_KNOWLEDGE_USERNAME` and `UV_INDEX_KNOWLEDGE_PASSWORD`.

### Fixed

- **`knowledge-federate.py members` names a release's schema only when it is `schema-<tag>-<name>.yaml`, with the zip's `<tag>-<name>`.** A schema file another workflow attaches, such as gist's copy for other projects to import, no longer fails a member's move on its attestation.

## [0.64.0] - 2026-11-14

### Added

- **Each role has its own docs page under `docs/cast/`, and `docs/first-bundle.md` shows a first run step by step.** The README gains a get-started section.
- **`docs/for-the-curious.md` is now `docs/how-it-works.md`, and its old address redirects.** The ingest page splits into `docs/ingest.md` and `docs/ingest-reference.md`.
- **`docs/young-readers.md` says how a bundle retells adult knowledge for readers aged 8 to 18.**
- **`docs/examples/first-bundle.md` holds a captured first run of the four roles on a small repository.**
- **`knowledge-report.sh sample` draws the curator's samples, and the whole report prints them.** An auditor passes `--seed` for a sample nobody could foresee.
- **`knowledge-report.sh evidence` prints every `generated` record and `verified` event as a table, and marks a second person's re-check.** `knowledge-release.yaml` attaches it to each release as `evidence-<tag>-<name>.tsv`.
- **`docs/examples/curator.md` holds a captured `ktl-curator` session**, and the docent answers asked after it move to `docs/examples/docent-after-curation.md`.
- **`docs/uses.md` says what KTL is for and what it is not**, and answers whether it fits DevSecOps and technology governance.
- **The skills use `sources[].excerpt`**: the librarian copies the passage that a footnoted claim rests on, the curator shows it, and the docent quotes it. The librarian's `references/excerpts.md` says when to write one.
- **The pen refuses an excerpt that its file does not hold**, or one that is empty or longer than 500 characters.
- **A concept's page on the website shows the passage it quotes under each source.**
- **The work list tells a moved file from a moved passage**, lists first each excerpt that its file no longer holds, and counts the footnoted sources with no excerpt.
- **`knowledge-apply.sh --dry-run --diff` shows each change as a unified diff.**
- **The whole report prints vocabulary fit and the confirmations not tied to a signed commit.**
- **`knowledge-conventions.sh --strict` fails when it could not check a rule**, and every workflow uses it.
- **The ingest lock records each mirror file's digest, and a run writes a hand-edited file again.** `--status` counts edited files, and the first run after the upgrade rewrites the mirror once.
- **A mirrored source shows its origin, version and fetch day on the concept page.**
- **A ktl-website Mermaid diagram opens over the page with a click**, as a figure does, where the wheel or buttons zoom it and a drag moves it.
- **The bundle page and the health page show their figures on a card**: a bar of the ladder's states and a tile per health figure, each linking to its list.
- **A concept card names a Creative Commons licence by its short name**, shows each check's person or automation dot, offers its files as chips, rules its record's rows, and shows a genre that repeats the type only once.
- **Each release is also the `ktl` package on PyPI**, for a machine that reaches a package index and no git host. `uvx ktl skills install --scope user` installs the six skills for GitHub Copilot, or with `--agent` for Claude Code or Codex, and `ktl skills status` says whether the copies an agent reads are the release's. `knowledge-trust-ladder` installs the same package under the repository's name. `pypi.yml` uploads both once `PYPI_RELEASE_ENABLED` is set, from a build anyone can repeat byte for byte, and attaches each file's checksum to the release.
- **`ktl gh` sets the GitHub settings a repository's workflows need**, from the catalogue each skill carries in `references/repository-settings.json`. `plan` and `check` say what is missing and why, `apply` creates the Environments, branch rules and values without loosening anything, `secrets` asks for each secret without an echo, `enable` turns a switch on once what it needs holds, and `prune` removes retired names such as `KNOWLEDGE_LIBRARIAN_CMD`.

### Changed

- **The file a bundle's `schema :=` line names is now called its *domain vocabulary*, and a *domain schema* is a LinkML project's schema, which never imports `lokf`.** The librarian's and the curator's pages are now `references/domain-vocabulary.md` and `references/domain-vocabularies.md`. The `schema` variable and `--schema` are unchanged.
- **`docs/three-lines.md` lists only the work that remains**, an auditor skill for a host with a third line.
- **Rule 10 keeps `sources`, `exclusions` and `resource` in block form, and rules 6 and 11 read flow-form events.** A bundle that writes `sources` in flow form now fails the gate.
- **The report and the conventions check are faster on a large bundle**: at 2,000 concepts the work list takes 0.9 s instead of 234 s.
- **A concept page carries only its own folder's sidebar**, since the site grew with the square of the bundle.
- **A scheduled run applies and checks the patch with the pen and the gate copied from HEAD before the agent ran**, and is refused if the agent moved HEAD or changed them. The threat model names the two routes this cannot close.
- **The skills release runs the contract and the tests in a read-only `verify` job**, which installs the test packages by hash from `tests/requirements.txt`, as `validate.yml` does.
- **A switched-off librarian skips every job**, with no checkout or install each week.
- **A sync names a local edit it overwrote, and a host script no manifest line lists.**
- **A federation build exports a large member in seconds, not minutes**, by labelling blank nodes with pyoxigraph's RDFC-1.0, as lokf pull request 187 proposes. Each `export/<slug>/graph.nt` changes its blank-node labels once.
- **The skills' scripts need Python 3.11 or later**, so on RHEL 9 or Ubuntu 22.04 they run only through `uv run` or `.lokf/.venv`. The ingest no longer pins typing-extensions.
- **`ktl-prose` reports "stops without" under rule 11**, since "The build stops without `gh`" means that the build needs `gh`.
- **A domain vocabulary takes a published release of a LinkML project's schema, not its working copy**, such as the file a sidecar's `just merged` writes.
- **`ktl-website` builds a Hugo site in place of the Astro one, and needs uv and no Node.js.** Hugo and Pagefind come from PyPI at hashed versions. The site finds what it shows with no setting, such as the README, the changelog, a LinkML schema's `gen-doc` pages or a domain host's workspace. Its home page has five buttons on every site, and greys the one whose page is missing. `site.toml` holds the four values a site needs, and [customising.md](skills/ktl-website/references/customising.md#from-the-earlier-astro-site) says how to move an Astro site.
- **A website's schema elements answer at `/elements/<Name>/` with no setting**, the address mkdocs gave each and the one a schema's w3id rules point at.
- **`ktl-website` installs into `ktl-website/` when `website/` is another site's, and finds the site there on a rerun.** The website and federation workflows and the sidecar's sync look in both folders.
- **`ktl-prose` rewords a changelog's released sections only when a person asks**, and keeps each heading, date, link and excerpt.
- **A ktl-website site with no LinkML schema of its own shows LOKF core in its Schema part**, from `.lokf/schema/lokf.yaml` or the `lokf` package, so the home page's schema button is never greyed. The home page still leads only with a repository's own schema.
- **The website's home page fills the Quick start button**, so a new reader sees where to begin. A site with no quick start fills the first button found, as before.
- **The preflight reads a skill that `gh skill install` rewrote as the release it came from**, so a gh copy beside a verbatim copy of one release is no longer reported as stale.
- **`llms.txt` names the PyPI route first**, for an agent at a site that reaches no git host.

### Removed

- **The website takes no `PAGES` entries.** A retelling is found by its file name, `<page>.<language>-simple.md`, instead.

### Fixed

- **A concept with an `exclusions` entry is no longer labelled *a reader disputed this*.**
- **The pen holds a person's record against nine more spellings**, such as a `human:` actor under any key.
- **The pen keeps a file's mode, and writes back an unchanged frontmatter block as it found it.**
- **A federation build keeps each quad whole, stops a member's index title from adding lines to the MCP server's instructions, and refuses the rest of the XML family as files a browser runs.**
- **The ingest tries a download again when it is cut short, and its privileged job refuses a rename, a link and a file marked to run.** A body that UTF-8 cannot write fails only itself, and an exclude pattern with no slash applies in every folder.
- **The librarian's wrapper runs in a linked work tree and in a clone with no hooks folder, and a sync no longer fetches into a `--source` clone.**
- **The website preflight prints no credential that the remote's address carries.**
- **The provenance gate and `knowledge-registrar.yaml` read five confirmations they once passed unseen**, such as one in a commit with no parent or in a sidecar kept in a subfolder. The gate stops on a shallow clone or a missing tool, and allows the merge of a branch where a key was added in a change of its own.
- **`knowledge-report.sh` reads a compact offset such as `-0500`, a comment beside a quoted value and a `urn:` or `doi:` source as a parser does.** A source map that names `.` no longer moves with the bundle's commits, and the work list names each concept with no stamp. Conventions rule 10 refuses a comment line among the events, rule 5 takes a `urn:` for no file, and rule 16 reads `./docs/a.md` as `docs/a.md`.
- **The preflight counts CRLF files with any `grep`, and finds an SSH signing key given as `key::` or under `~`.**
- **The librarian's wrapper runs the agent with the skill that the workflow installed, not a copy under `.claude/skills/`, and refuses an agent that tells git to stop checking a file for changes, as `skip-worktree` does.** The federation's `labels.rq` and `moved.rq` compare two times as times.
- **The website refuses a raw-HTML address that holds a control character**, such as the tab a browser drops from `java<tab>script:`.
- **A line of a block scalar under `sources` no longer reads as a source.**
- **The ingest keeps a table cell's code block, list, panel or nested table in the cell**, and keeps spans and a table or `<pre>` left open.
- **A changed `authors`, `license` or `convert` setting, or a new converter version, reaches every mirrored page**, and a page that left the selection gets a new header.
- **A redirected page's links are resolved against the address that served it**, which the header records as `redirected_to`. A redirect from https to http is refused.
- **`--patch` keeps each item on the Reference concept that names its copy**, whose `resource` follows a git item to its newer commit.
- **The ingest workflow's push is leased to the commit it read**, so a branch a person committed to is left alone.
- **`labels.rq` shows a passed review date, a retired concept and a draft, one row per concept**, and counts a person's latest confirmation.
- **Two federation builds sharing a cache write a download file each, a build reads each bundle once, and an unreadable zip is a finding, not a traceback.** The docs say the snapshot swap is two renames.
- **A concept page's address is its id when the id holds a capital, a dot or a leading underscore, and a single `verified` event shows on its card.**
- **A source is compared with the commit its event names as `revision`**, so a source changed while the pull request waited reads as moved.
- **The work list names sources git holds no history of**, such as an ignored file.
- **The feedback script refuses entry text that reads as an attribution, and `diataxis.md` as a concept.**
- **The pen writes a shared log line once, and two of its refusals say what is wrong**: a target quoted in an open question, and one feedback entry named twice.
- **The librarian and sync workflows work on GitHub Enterprise Server.**
- **Check 21 refuses every character the pen treats as invisible.**
- **The install smoke test's check for leaked installer metadata can fail.**
- **The gate and the report skip a folder whose name ends in `.md`.**
- **The sync's check no longer reports a pass for conventions it could not run**, as when `uv` is missing.
- **The librarian wrapper compares files by git object id, not by a `cksum` checksum**, which a rewritten file of the same length can match.
- **A confirmation's `revision` is compared only with its concept's `resource`**, and each other source with the commit that recorded the confirmation.
- **The pen writes a `revision` in double quotes**, since YAML 1.2 reads a short hash such as `1234e56` as a number. An unquoted value that YAML reads as a number is kept as it was.
- **`knowledge-provenance.sh` counts each concept a range confirms**, not each curator once per commit.
- **The schema on exhibit takes the site's walnut colour for its title**, so it no longer reads as the heading of the page below it.
- **A concept's page no longer lists a retired concept among those that point at it.** The report counts a retired concept for none, and a successor with the same title was listed twice.
- **Conventions rule 10 says that a tag, an anchor, an alias or a merge key is refused on any frontmatter field**, as the check always did, not only on the fields the gates read.
- **`website-preflight.sh` names the file a foreign site folder lacks**, `hugo.toml` as well as `site.toml`.
- **`knowledge-sync.sh` and the automation page say that `--source` looks for the tag in that clone alone**, not on the remote.
- **A concept page no longer scrolls sideways on a phone**: a long path or address in its record wraps.
- **The docs agree with what the workflows need from GitHub.** automation.md's table names `KNOWLEDGE_CURATION_ENVIRONMENT`, the two secrets that stay on the repository are named, a domain host's `github-pages` Environment admits release tags, the librarian's first run by hand follows its switch, and gate.md says a release job's push rules out required checks.

### Security

- **The scheduled librarian writes the bundle on a runner the agent never shared.** A new `apply` job in `knowledge-librarian.yaml` runs the default branch's pen on the agent's patch file, since the agent could change its checkout and `.venv`.
- **The ingest pins pypdf 7.0.1**, as the tests do after a Dependabot update.

## [0.63.0] - 2026-11-12

### Added

- **A domain host builds members from private and internal GitHub repositories**, and `gh` fetches their files with the secret `KNOWLEDGE_FEDERATE_TOKEN`, or after `gh auth login` by hand. A public member is fetched without the credential.
- **`KNOWLEDGE_RUNNER` names the runner every job runs on**, `ubuntu-latest` unless set, so a host with self-hosted runners needs no edit that a sync would undo. automation.md's Customising section lists what a locked-down organisation sets.
- **A host can install the skills from its organisation's private copy**, named by `TRUST_LADDER_SKILLS_REPO`, which a sync keeps, and read with the secret `KNOWLEDGE_SKILLS_TOKEN`.
- **The website and federation workflows warn when a private repository's Pages site is public.**
- **`KNOWLEDGE_ATTEST_PRIVATE` attests a private repository's release**, which a domain build needs from every member. It needs GitHub Enterprise Cloud.
- **ktl-prose lists every sentence it would cut, and the person answers once.** Its check accepts a cut sentence whose links, numbers and quotations the page still holds, and notes the words a page lost or gained.
- **ktl-prose reads a concept's `genre`, and names for ktl-librarian a page that has left its genre.** `references/rules.md` gives the order to read a sentence in, and three more faults, such as the dropped "that".

### Changed

- **ktl-prose's check stops more changes that reverse a claim**, such as `confirmed` to `unconfirmed`, and reads each list item and table row as a sentence. `references/limits.md` lists every finding.
- **A pass over a script's comments may change no other line**, and `--against` and `--before` report one that does as `not-prose`.
- **ktl-prose's notes give the line of a word of strength that came or went**, and one note lists the new code spans.
- **The sources of ktl-prose's rules move to `references/sources.md`**, with what they say about line breaks.

### Fixed

- **ktl-prose's check finds a reversed sentence even when an earlier sentence shares as many of its words.**
- **ktl-prose's check prints a control character as its code point**, so no file can write to a terminal or a CI log through a finding.
- **A sign-in or proxy page in a zip's place is no longer reported as a wrong checksum**, and the finding names the media type and the address that answered.
- **`members --add` reads a private repository's release list.**
- **The release, sync, ingest and federation workflows say what `gh` or git said when they cannot read GitHub.**
- **The federation build deploys no site without its workspace when the release list cannot be read**, installs `just` for a site that builds with it, and turns Astro's telemetry off.
- **semantic-release installs from `.github/release/package-lock.json`**, so a company registry can be given the exact list.
- **The ingest installs the packages that `uv.lock` pins, checked by hash, in the job that holds its secrets.** The registrar says when `gh` is missing, and the release when python3 is older than 3.9.
- **The website colours code blocks again after the satteri 0.11 update.**

## [0.62.0] - 2026-11-06

### Changed

- **Schema files go in `.lokf/schema/`**, named as `schema := "schema/<slug>.yaml"`. The release and the preflight read either layout, and the preflight lists schema files left at the root of `.lokf/`.
- **A domain host moves `domain.yaml` and `lokf.yaml` into `.lokf/schema/` before its next sync**, which its installed sync script refuses until then. ktl-librarian's `references/domain-schema.md` gives the move.

### Fixed

- **An ingest `command` runs where git ignores both it and the manifest**, and its record says it ran unchecked.
- **The scheduled librarian runs in a fork whose upstream owns the root `.gitignore`**, since the install step lists its files in `.git/info/exclude`. It checks every installed file.

### Security

- **The librarian's agent job saves no cache that the release restores**, since uv trusts the wheels it unpacked there. The agent's job, the release's `pack`, the gate, `docent-eval.yml` and `publish.yml` take no uv cache, and the agent's job no npm cache.
- **The librarian's `publish` job refuses a rename, a copy, a link or a mode change**, since moving the gate script into the bundle skipped the gate. A missing gate fails the run.
- **The librarian's `publish` job keeps its token off disk**, in its push step's address only.
- **Every job of the registrar and sync workflows runs harden-runner.**
- **The librarian wrapper restores `.git/info/` after the agent runs**, so an exclude rule the agent adds cannot hide its writes from the write-scope check.
- **ktl-website strips a page title's tags until none is left**, since one pass over `<<b>script>` left `<script>`.

## [0.61.0] - 2026-11-02

### Added

- **The gate page and ktl-prose list what their checks cannot see**, in `references/gate.md` and `references/limits.md`.
- **The work list counts a body that changed after its stamp as a moved source**, for `quiet` and a person's confirmation too, since a rewording could reverse a claim. A host's first run after this release checks each body reworded so far.
- **`knowledge-report.sh isolated` names the concepts that no relation joins to the rest of the bundle**, and the work list shows ten at a time, in turn by month. They fail no check.

### Changed

- **The librarian writes each relation a source states, and none added only to join two concepts.** The refresh's file sweep no longer calls unnamed files orphans.

### Fixed

- **Every job of the librarian, registrar, release and website workflows has a time limit**: 60 minutes for the agent's job, and 10 to 30 for the others.
- **The knowledge website rebuilds when a linkml-project-copier project's schema changes.**
- **Both gates and rule 9 refuse a symbolic link, apart from the bundle's two names**, since the toolkit follows a link and git does not.
- **The gates refuse frontmatter they cannot read**, such as a `human:` event under a quoted key, which now reads as `(unreadable)`, and rule 10 names the spelling.
- **An edit inside frontmatter the gates cannot read is refused**, since a forged event could pass there.
- **A range that deletes `.lokf/curators/` is read, not skipped.**
- **Rule 9 reports a `---` inside a frontmatter value**, where the toolkit ends the block.
- **The report and the gates read an event whose list dash stands alone**, rather than merging it with the next event, which could lose a person's confirmation.
- **The prose check reads a concept whose `exclusions` entries name who decided.**
- **The prose check no longer rewords a confirmation it cannot see.** A person's `revised` or any `refuted` event leaves a concept alone, and a quoted `status: deprecated` reads as retired.
- **The prose check holds more of what a rewording must keep**, such as the unit on a number, and a retelling adds nothing in its title or description.
- **The prose check stops a sentence whose meaning was reversed**, such as `enabled` to `disabled`.
- **The prose check and its skill no longer claim what they cannot know**, such as "only the wording differs".
- **The prose check no longer refuses or crashes on ordinary input**, such as a year that opens a wrapped line.
- **The pen refuses a relation to nothing**, whether a patch adds it or a `delete` leaves it.
- **The curator's queue counts what a domain schema's own slots point at**, not only LOKF's fourteen relation fields.

### Security

- **The ingest pins pypdf 6.21.4**, as the tests do after a Dependabot update.

## [0.60.0] - 2026-10-30

### Added

- **`just lokf-check-refs` runs lokf's `--check-excerpts`**, so the gate fails an excerpt that its file no longer holds. A host raises its lokf floor to 0.9.0 before it takes this release.
- **ktl-website's `SCHEMA: "auto"` falls back to the sidecar's domain schema**, built into the ignored `.lokf/docs/elements/`. The preflight warns when git does not ignore that folder.

### Changed

- **`lokf-convert`, `lokf-serve` and the website's `lokf export` pass the domain schema too**, so the graph names its classes and slots under their own IRIs.
- **The preflight warns on a `lokf` floor below 0.9.0**, and when `[tool.lokf] schema` and the justfile's `schema :=` line name different files.
- **A member's distribution names its checksum as LOKF core's `Checksum`, with `algorithm: sha256` and a `checksum_value`.** A domain host rewrites its member concepts when it takes this release.
- **The federation docs say the workspace exports every bundle under LOKF core**, and the workspace index says each bundle's fit is checked against its released schema.

### Fixed

- **`automation.md` gives the right reason that the librarian's variables are repository variables.**
- **The librarian's Snyk W012 note names the lokf 0.9.0 wheel.**
- **The preflight warns when `.lokf/lokf.yaml` is from another lokf release than the one `uv.lock` pins.**
- **The federation check runs on a pull request that changes `.lokf/lokf.yaml` or `.lokf/justfile`.**
- **This repository's domain-bundle playbook names a commit that `main` holds.**
- **A `command` entry run outside a git work tree says so in its lock record (`command_unchecked`), its mirror's header and the summary**, and one in a repository git will not read is refused.
- **The preflight installs the packages of the pen and the conventions script, and reports `missing` when uv cannot.**

## [0.59.0] - 2026-10-28

### Added

- **A host's composite domain schema is released as one file**, with each `lokf adapt` copy it imports merged in. A name two files define differently stops the release.
- **The sidecar reads lokf 0.9.0's `exclusions`.** Coverage and `--why` count an excluded file apart and never as a source, and conventions rule 18 fails a blank reason or a material listed both ways.

### Changed

- **The sidecar requires lokf 0.9.0.** A host raises the floor in `.lokf/pyproject.toml` by hand, refreshes any `.lokf/lokf.yaml`, runs `uv lock` and renames each `supporting_text` key to `excerpt`.
- **The skills describe `revision`, `excerpt` and `lokf adapt` as released**, and the audit fallback links `lokf.yaml` at the v0.9.0 commit.
- **The librarian's domain-schema page says how to import a published vocabulary through its `lokf adapt` copy.**
- **A domain build still indexes a member's explicit ids outside its namespace**, which lokf 0.9.0 refuses unless the registrant allows them, but never one in another member's namespace.
- **The reliance count and the docent follow `isReplacedBy`**, the relation slot lokf 0.9.0 adds.

### Fixed

- **A release that changes only the domain schema attaches it.**

## [0.58.0] - 2026-10-28

### Added

- **The gate checks three more conventions, rules 15 to 17.** Every concept names where it came from, as `resource` or a `sources` entry. A footnote cites a `sources` entry by its `id`, one id names one resource, and each **Added** and **Deprecation** log bullet names a concept the bundle holds.
- **The librarian cites a source by its `id` in a footnote wherever a claim rests on a number, a name or a qualifier**, as `references/golden-rules.md` says.
- **ktl-docent has a holdout, and an eval that runs it.** `tests/docent-holdout.yaml` pairs the eight captured questions with the concept each answer should rest on, and a test fails when one of those concepts moves. `just docent-eval` runs the eval, and `docent-eval.yml` runs it weekly under a cost ceiling, never on a pull request ([the docent eval](docs/threat-model.md#the-docent-eval)).
- **The curator's report lists each retired concept whose successor no person has confirmed.**
- **A curation policy may carry `Automation re-check: <n>`**, and the curator's report then lists n concepts checked by automation only, for a person to check.

### Changed

- **ktl-sidecar installs the ingest's example manifest as `.lokf/ingest.yaml.sample`**, for a host to copy to `.lokf/ingest.yaml`.

### Fixed

- **The sidecar's two example concepts carry a `resource`**, so the skeleton passes rule 15.
- **`knowledge-report.sh` reads a review date by its day**, so a `stale_after` datetime is due on that day.
- **The pen, the conventions check and the ingest run behind a package mirror with no upload times**, and the ingest pins typing-extensions.
- **A uv that cannot install a script's packages no longer reads as findings.** The conventions check exits 2, the pen falls back to python3 or exits 2, and the ingest falls back to a `.venv` without pypdf.

## [0.57.0] - 2026-10-27

### Added

- **A ktl-website home page offers a Schema button when the site shows a LinkML schema's pages.**

### Fixed

- **A `!` after the type releases a major version.** `.releaserc.json` names the Conventional Commits preset, so a `feat!:` commit no longer releases nothing.
- **The preflight warns when git is too old for an ingest `git` entry**, and names each entry a run would refuse.
- **The ingest fetches a source whose name resolves only at a proxy with no outside DNS**, as the federation build does.
- **A `git` entry fetched through a proxy that resolves names needs no git 2.37**, and git uses the proxy that the ingest chose, or none, whatever git's configuration or `no_proxy` says.
- **The ingest passes `all_proxy` to git and to a `command` entry**, as it passes `https_proxy`.
- **The ingest converts a page that leaves out `</head>`, as HTML allows**, and reads a line break in a page's text as a space.
- **The ingest refuses a manifest value of the wrong type, by name**, such as a quoted `"false"`, which counted as true.
- **One page or file fails only itself**, and a charset that decodes to a lone surrogate no longer stops the run.
- **A `git` file whose mirror name is taken is skipped, and one whose name the workflow does not publish gets a name of plain characters and a digest.**
- **A file restored with unchanged bytes keeps its record and changes no line of the lock**, and an entry that leaves the manifest frees its bytes.
- **A `git` entry's relative local path is read against the repository root**, and a `command` with changes not yet committed is refused.
- **The ingest starts no work after 25 minutes, inside the job's 30, and writes what it fetched.** The rest waits for the next run, and `--time-limit` sets the minutes.
- **A `git` entry downloads only the files that changed.**
- **A new ETag for unchanged bytes is recorded by the next run that changes the lock**, so later runs get 304.
- **A `command` entry's timeout stops every process the command started**, and a malformed lock stops the run with a message, not a traceback.
- **The ingest and the pen run on Python 3.9, as their shell halves say**, and before Python 3.11 the ingest keeps a time with fractional seconds in UTC.

### Security

- **The ingest pins a `git` entry's host name to the addresses its check found, and follows no redirect for it**, so DNS rebinding cannot reach a private address through git unless a proxy resolves the name. Without `allow_private_addresses` such an entry needs git 2.37 or later, and a host name outside ASCII is refused, so write its `xn--` form.
- **The ingest and the federation build count every address that is not global as private**, such as the shared address space 100.64.0.0/10.
- **The ingest refuses a `git` entry whose address git's configuration rewrites with `url.<base>.insteadOf`.**
- **The ingest refuses a `git` entry when git is older than 2.31**, since an older git ignores the protocol limits and the credential that the script sets. The preflight warns before a run.
- **The ingest's git reads no `~/.netrc`, `~/.gitconfig` or `/etc/gitconfig`**, so a `.netrc` default credential reaches no other host. A file that `GIT_CONFIG_GLOBAL` names is still read.
- **The ingest sends a credential only to its own origin, and git follows no redirect with one.**
- **No credential reaches the lock or the summary**: a line break that ends a secret is trimmed, and a secret with one inside is refused.
- **The ingest removes and writes files only inside the mirror.**
- **An entry made `confidential` leaves the committed mirror on its next run.**
- **The committed lock records no title, address or author of a confidential page**, unless the entry sets `lock_details: true`. Those records move to the ignored `.lokf/.cache/ingest.lock.yaml`, and the summary names none of the entry's items.
- **The ingest pins pypdf 6.21.2**, since 6.1.1 has published advisories for infinite loops and memory exhaustion on a crafted PDF.
- **One source can no longer stall the run or fill the disk**: a body has a deadline of ten timeouts, lists and quotes nest at most eight deep, and the caps count the Markdown written.
- **The mirror keeps no `javascript:` or `data:` link in any letter case, and no invisible character**, and each title and summary line is one line.
- **An `http` entry needs `allow_private_addresses: true` for a plain `http://` address.**
- **The pen and the librarian's pull request remove the characters that the mirror removes**, and the ingest refuses a file name that holds one.

## [0.56.2] - 2026-10-27

### Fixed

- **The curator's report ends by saying when the review session will not run, and why.** A harness line saying the person cannot answer no longer stops the session, and the curator goes on only when the person replies.
- **The federation's members script moves the day of a pruned release with its tag**, and changes no other day.
- **The federation's members script follows a member's moved namespace**, unless the build would refuse it.
- **The federation's members script shortens a hand-off line that the pen would refuse as longer than 300 characters.**
- **A federation build finds a waiting member by the namespace it builds**, not the one a move proposes.
- **The federation build and members script remove the files they download**, unless `--cache` names a folder to keep them in.

## [0.56.1] - 2026-10-26

### Changed

- **`docs/three-lines-critics.md` is merged into `docs/three-lines.md`**, and the docs pages' titles are shorter.
- **The workflows run the `just` that `.lokf/uv.lock` pins, checked by hash, as `rust-just==1.47.0` in the sidecar's `pyproject.toml`.** A host whose `pyproject.toml` lacks it still gets that version by name, and the preflight says to run `uv add rust-just==1.47.0` in `.lokf/`.

### Fixed

- **ktl-website builds for an owner spelt with capitals.**
- **ktl-website's cards show a concept's genre as a plain tag beside its type, unless it repeats the type, and search gains a Genre filter.**
- **ktl-website words a type as the bundle's prose spells it**, so `SlsaSourceControlSystem` reads "SLSA source control system".
- **ktl-website reloads once a page whose stylesheet a deploy removed**, so it no longer shows unstyled.
- **The federation build and the ingest check the address each connection opens**, so DNS rebinding reaches no private address unless private addresses are allowed.
- **CI lints the ingest workflow template, `knowledge-ingest.yaml`, with actionlint.**

## [0.56.0] - 2026-10-24

### Added

- **ktl-website redirects an old address with `REDIRECTS`, and leaves a path off the site with `DOCS.exclude`.**

### Fixed

- **A link to a docs folder's `index.md` reaches its page**, which comes first in the Guide as its Overview.

## [0.55.2] - 2026-10-22

### Fixed

- **The preflight asks the package index uv reads, a company mirror included, and prints only its host name.** It warns when `.lokf/uv.lock` was made against another index, since `uv sync --locked` then fails.
- **The sidecar's portability page says what a mirror does to the lock**, and how to make uv trust a proxy that inspects TLS.

## [0.55.1] - 2026-10-22

### Fixed

- **A sync completes again on a host with a website**, since its website step allows square brackets in a path.
- **ktl-prose reads every file in scope, the ones its script cleared too**, and its rules name three more faults, such as the dead sentence.
- **ktl-curator commits a verdict apart from the change it confirms**, as conventions rule 14 checks.
- **ktl-librarian's domain-schema page says how to import a published vocabulary with `lokf adapt`.**
- **The website template takes Astro 7.4.0** and its plugins' patch releases.

## [0.55.0] - 2026-10-20

### Added

- **The pen runs `lokf validate` on every concept a patch would write**, when `.lokf/.venv` holds the toolkit.
- **The preflight warns about a python3 older than 3.9**, about being run from ktl-sidecar's own folder, and names KTL skills installed for one user.
- **ktl-prose's check reads a script's comments and docstrings as paragraphs.**

### Changed

- **ktl-prose's check reports a paragraph of more than eight sentences**, and lists "outright" and "at all" among the words to cut. The rules page gains four points, such as a method for a paragraph with two topics.

### Fixed

- **The sidecar's scripts run behind a package mirror that serves no upload times**, by trying `.lokf/.venv` before `uv run`, and none picks a Python older than 3.9.
- **When its runner cannot start, the conventions check says so and exits 2**, instead of reporting findings.
- **A freshly installed skeleton passes its conventions.**
- **ktl-prose runs its check through `uv run`**, so an old `python3` never runs it.
- **ktl-sidecar's Step 0 runs the preflight from the host repository's root.**
- **The librarian's audit lints the files it touched**, not `.lokf/.venv/`.
- **A release attaches a linkml-sidecar host's schema**, wherever the `schema :=` line names it, and the copy imports LOKF core as `lokf`.
- **ktl-prose's check reads a comment's layout**, so a table of options or a usage line is not one long sentence, and `--against` compares a script by its comments.
- **ktl-prose's check reports fewer false findings**, and lets a sentence start with a lowercase name such as `ktl-docent`.

## [0.54.0] - 2026-10-20

### Changed

- **The graph page keeps the graph at full height in full screen**, with search and filters in a side panel, and stays in full screen when the view switches between *This bundle* and *The workspace*.
- **The graph's filters read as controls**, with counts, *All* and *None*, and an "N of M concepts shown" line.

## [0.53.0] - 2026-10-19

### Added

- **The workspace counts the links between its members by slot**, in the lock, the workspace index and `queries/links.rq`.
- **The workspace carries `graph.json`**, every bundle's concepts and typed relations as cytoscape.js elements.
- **The MCP server loads a member's graph when a walk first reaches it, and a SPARQL query loads them all**, as LOKF section 11.4 has it. The lock's `graphs` (format 4) gives each graph's place in `graph.nq`.
- **The federation build has the `sensitivity` gate of LOKF section 11.5.** An `internal` member joins only a private or internal repository's workspace, once a person confirms `sensitivity: internal` on the Domain concept, and the workflow keeps that workspace off the site. A `confidential` member never joins.
- **A bundle that releases no zip joins by the `concepts.jsonld` its site serves**, pinned by that file's checksum, and `members --add <address>` drafts such a member.
- **A member whose file cannot be fetched is held at its last good state**, from the workspace that `--previous` names, as LOKF section 11.5 has it.
- **The readers read a workspace in place**, from a folder, a `workspace-<tag>.zip` or the site that serves it. `read_document` tries the workspace's copy of a release, then its `concepts.jsonld`, then its source.
- **`--member <slug>` on `mcp`, `serve` and `query` loads only those members' graphs**, and refuses the stored queries that read the lock graph.
- **A domain host's release notes say which members joined, moved or left its workspace**, from `knowledge-federate.py diff`.
- **A domain host's graph page draws the workspace** from the `graph.json` that the federation workflow serves, and `WORKSPACE` in `site.config.mjs` turns the view on or off.

### Changed

- **`docs/federation.md` holds the whole federation design, and states each rule once**, with the parts that `docs/context-layer.md` held.
- **The docs describe the pen, its figure and the ingest's guards once**, with the figure on `docs/architecture.md`.
- **`docs/context-layer-technology.md` keeps to what KTL needs from a product**, without the vendor tables.
- **`docs/for-the-curious.md` holds what KTL took from the WikiSkill and SkillWiki papers**, in place of `docs/wikiskill.md` and `docs/skillwiki.md`, and says how readers and verdicts direct the next run.
- **The federation build runs lokf in its own process**, rather than starting one for each bundle, so ktl-federation's five members build in 4.5 seconds instead of 12.
- **`SECURITY.md` and `docs/threat-model.md` say what holds after these fixes**, with a section on the website, and no longer claim that a hostile release could at most propose a change before review.

### Fixed

- **The sync script no longer fails when a sync replaces it with a longer copy**, which Bash went on reading. It now exits on the line that calls `main`, and `scripts/sync-sidecar.sh` runs each sibling's script from a copy.
- **A confidential ingest entry is refused where git could commit its copy.**
- **The sync keeps a host's `.lokf/.gitignore` current.**
- **The scheduled librarian stops before any agent runs when git does not ignore `.agents/`.**
- **The federation gate refuses a link into a member's namespace that names no concept of that member**, as `--check-refs` does inside a bundle, under the same `unowned_targets` policy. It reads a reified `relations` entry as the slot it names, and `links.rq` and `unowned.rq` count such entries.
- **The members script moves the other members when it cannot check one**, and asks again with the job's token when the GitHub API refuses a release list as rate limited.
- **The MCP server's `federated_sparql` stops reading at its limit, and says when it cut an answer.**
- **The workspace's stored queries take their predicates from the toolkit.**
- **The graph page's details panel sets each label beside its value.**
- **A member whose index gives its licence as text, such as `MIT`, no longer stops the domain build.**
- **The MCP server reads a concept whose `id` is outside its bundle's namespace.**
- **A member whose namespace nests with another's stops the build before anything is fetched**, with a finding that names both.
- **A checksum must be `sha256:` and 64 hex digits**, so no path in it can make the build delete a file outside the download cache.
- **Every download stops at `--max-bytes`**, a member's schema and workspace as well as its zip.
- **A download is tried again after a server error or a dropped connection, and follows a redirect only within http and https**, never from https to http or from a public address to a private one.
- **A zip of more than 100,000 entries, or one that cannot be read, stops the build with a finding.**
- **A reader keeps no partial answer to a range request as the whole file**, and `--previous` refuses a site address.
- **The federation workflow's weekly schedule no longer replaces a release build that waits its turn**, and each job has a time limit.
- **A domain host's site serves each member's release inside the workspace**, hidden `.lokf/` folders included.
- **The contract records every sibling host's links into this repository**, and its cross-check reads all five hosts.
- **The librarian keeps run accounts out of the source map.**
- **An agent that applies its own patch no longer loses a scheduled run's work**, since the pen only checks the patch under `KNOWLEDGE_PEN_DRY_RUN_ONLY` and the wrapper applies it.

### Security

- **A release can no longer write a host's git configuration through the sync**, which refuses a copy path inside a `.git` folder and clones the release without a checkout.
- **The branch the sync pushes carries no workflow a release wrote**, since a workflow on a pushed branch runs with the repository's secrets. `publish` holds the release's workflow changes for a person, or for a reviewer of the Environment that `KNOWLEDGE_SYNC_REVIEW_ENVIRONMENT` names.
- **The sync's `publish` refuses a deletion, a link or an unusual mode, and leases its push to the commit it read.**
- **Each workflow reads its secrets from an Environment limited to the default branch:** `knowledge-librarian`, `knowledge-sync` and `knowledge-ingest`. Move every repository secret there on every host, as the sidecar's `references/automation.md` says.
- **A federation build refuses a member zip holding a hidden file or a file a browser runs, and a distribution name that is not one plain file name.** A `.git` folder in a zip could run code in the build.
- **A federation build fetches members over http or https from public addresses only.** `--allow-local` allows local paths and private addresses, and a person's `private_addresses: allow` on the Domain concept allows a forge on the host's network.
- **A member's attestation must come from its own release workflow**, and a build needs `gh` unless given `--no-attestation`.
- **The federation workflow passes its token only to `gh`, and the website and federation builds run no npm install script.**
- **The website copies only files inside the repository, and treats raw HTML as GitHub does in a README**: an SVG holding a script is left out, and other markup is shown as text. Astro's telemetry is off.

## [0.52.0] - 2026-10-18

### Added

- **A member that waits in a member domain joins at the release that domain built.** The `MemberDomain` concept names that release's `workspace-<tag>.zip` and its checksum, and the lock, from format 3, names each member concept. The build refuses a schema or workspace from another release.
- **`knowledge-report.sh coverage --why <path>` names the concept that claims a file**, directly or through a folder above it.
- **`coverage --strict` exits 1 when no concept names a tracked file**, when a folder holds no tracked file, or when it cannot count.

### Changed

- **`coverage` counts separately the untracked files git would add, and no longer counts a tracked file deleted from the working tree.**

### Fixed

- **The federation check, `build --verify-only`, runs the gate as the next release build would**, so a link into an unowned namespace or an unconfirmed member fails the pull request, not the release build. It names the members the next release would leave out, and runs on any change to the domain bundle.
- **`coverage .` lists every file no concept names, and a mistyped folder says git tracks nothing there.** `coverage` refuses a flag it does not know.

## [0.51.0] - 2026-10-18

### Added

- **A person who sends back text they wrote can release it to the librarian**, whose next run rewrites it from its sources. ktl-curator records this as `process:ktl-curator` in `generated`, in a commit that person signs.

### Fixed

- **`docs/three-lines.md` no longer lists the `lokf-registry` MCP server as a design**, since `knowledge-federate.py mcp` serves it.
- **Conventions rule 2 holds every `at:` to one shape: UTC to the second, as `date -u +%Y-%m-%dT%H:%M:%SZ` writes it.** A person's event that no script could read had counted as confirming every later edit.

## [0.50.1] - 2026-10-18

### Fixed

- **The federation build leaves out a concept a curator retired**, so a retired `Domain` concept no longer counts as a second top, and a retired member is neither built into the workspace nor moved by `members`. The curator's domain-bundle.md says how a member leaves.
- **The federation build takes each member, and the Domain concept's gate policy and depth, as a person last confirmed them**, with the defaults until a first confirmation. A member no person confirmed is left out, and the lock, the workspace index and the gate's errors name it as waiting.
- **`members --add` quotes the description from the new member's own index**, so a description with no full stop no longer runs on.
- **The sync calls a copy a pin bump only when its `uses:` lines are all that differ.**

## [0.50.0] - 2026-10-18

### Added

- **The ingest restores a lost mirror file and prunes on a schedule.** A scheduled run removes a gone or unlisted file no concept cites once an earlier run recorded it, and the preflight counts missing, stray and prunable files.
- **`docs/ingest.md` has a figure**, `.assets/ktl-ingest.svg`, with its dark variant.

### Removed

- **The figures no page shows**: every `-dimmed` figure, and both files of the lifecycle loop.

## [0.49.0] - 2026-10-18

### Added

- **The ingest mirrors knowledge from outside the repository.** `knowledge-ingest.py`, a new ktl-sidecar template, fetches the sources `.lokf/ingest.yaml` names, such as a Confluence selection, into `.lokf/mirror/` as Markdown, and records each in `.lokf/ingest.lock.yaml`. The librarian derives concepts from a mirror file as from any tracked file.
- **`knowledge-ingest.yaml` opens one pull request with what changed, and a checklist for the reviewer**, from the branch `knowledge-ingest`, once `KNOWLEDGE_INGEST_ENABLED` turns it on. It runs the host's script in a read-only job with the secrets whose names start `KNOWLEDGE_INGEST_`, and commits in a separate one.
- **`docs/ingest.md` is the guide.** The preflight prints an `ingest` line, and `knowledge-report.sh coverage` counts the mirror's files.

### Changed

- **A domain concept is named for the domain, never for its position**, as the curator's domain-bundle.md says.

## [0.48.0] - 2026-10-17

### Added

- **A domain may name domains, tier by tier**: `knowledge-federate.py build` follows them as deep as the top `Domain` concept's `max_depth`, 3 unless set. `domain.yaml` adds `max_depth` and a `MemberDomain` class, and the lock records each member's tier and the domains that named it.
- **The diamond rule.** A bundle that two domains name joins the workspace once when the releases match, and the build stops when they differ. `members --add` drafts a `MemberDomain` for a release that is a domain.
- **`docs/federation.md` takes the federation's mechanics out of `docs/context-layer.md`**, with the tiers of domains, the figure `ktl-federation-tiers.svg` and two new decisions.
- **`knowledge-report.sh coverage` counts, for each top-level folder, the tracked files no concept names in its `resource` or `sources`**, and lists them for a folder you name. A folder the source map names is accounted for.

### Changed

- **The website's figures stay in the text column on a wide screen, and a click opens one at full size.** A host gets the change at its next website repair.
- **The sidecar's pages name Codeberg beside GitLab, Forgejo and Gitea**, and point at the portability recipe for another forge. The registrar template links the three-lines page through w3id.

### Fixed

- **Two tiers may each name a `members/<slug>.md`**, since each bundle keeps a folder of its own under `bundles/` and `export/`.

## [0.47.0] - 2026-10-17

### Added

- **A host keeps its sidecar current by itself.** `knowledge-sync.yaml`, a new template, runs the host's own `knowledge-sync.sh` in a read-only job each week the skills pin is behind. Another job opens one pull request with the `KNOWLEDGE_SYNC_TOKEN` secret, or attaches the change to the run without it.
- **`publish.yml` asks the hosts named in `KNOWLEDGE_SYNC_HOSTS` to sync as soon as a release is tagged.**
- **`knowledge-sync.sh` is the sync, as a sidecar script**: it copies a release's templates over the host's copies, moves the pin, writes the changelog entry and runs the checks, and `--commit`, `--push` and `--pr` take it to a pull request.
- **`templates/knowledge-sync.manifest` lists each template a sync keeps current, and the rule for it**, so no code from a release runs in a host's sync. The sync script, the preflight and contract check 11 read it.

### Changed

- **`scripts/sync-sidecar.sh` runs each sibling's own `knowledge-sync.sh`, or the tag's in a sibling that has none.** `--finish <tag>` returns each sibling to its default branch and removes a merged sync branch, and the entry links the comparison between the two pins.

### Fixed

- **`knowledge-federate.py members` verifies attestations under the librarian wrapper, which strips every token.** It takes the job's read-only token as `KNOWLEDGE_FEDERATE_TOKEN` and gives it only to `gh`, once a host sets `AGENT_USE_JOB_TOKEN` to `true` and `AGENT_API_KEY_ENV` to that name.
- **The sync writes the changelog entry itself, rather than printing a hint for a person to follow.**

## [0.46.0] - 2026-10-17

### Added

- **`knowledge-federate.py mcp` serves a workspace to agents** as the `lokf-registry` server that section 11.4 of the LOKF specification describes, with five bounded tools such as `resolve_iri`. `serve`, `query` and `mcp` take an absolute `--snapshot`, so they read an unpacked `workspace-<tag>.zip` wherever a sidecar environment exists.
- **`knowledge-release.yaml` attaches the domain schema the justfile names**, as `schema-<tag>-<name>.yaml` with its checksum and attestation, so a federation validates the bundle against it, not against LOKF core only.
- **`knowledge-federate.py members --add <owner>/<repo>` drafts a new member** from the repository's newest verified bundle release, and refuses a namespace that nests with a member's.

### Changed

- **The sidecar's `llms.txt` and README aside no longer assume `npx skills` works.** `llms.txt` offers the GitHub CLI route, and the README aside points at the install page.

### Fixed

- **The workspace registry no longer names the runner's folder as the domain's `source_base`**, and the index names the address that is served (`.../workspace/index.md`), not a folder that answers 404.
- **`postcss-selector-parser` 7.1.6 in the website template's lockfile and in this repository's site** (GHSA-rj75-hqrm-r3gf, quadratic selector parsing).

## [0.45.1] - 2026-10-17

### Changed

- **`knowledge-apply.sh` indents a list under its key**, as yamllint's default rules ask.

### Fixed

- **`knowledge-apply.sh` lists a concept with no description by its link only.**
- **`knowledge-apply.sh` applies a `set` on a `rewrite` as it does on a `patch`**, and every operation refuses, by name, a key it does not take.
- **`knowledge-federate.py members` moves a member's text with its version**, and calls a member "confirmed" only when a person confirmed it as it stands. `--dry-run` prints the patch even while a librarian pull request is open.
- **`knowledge-apply.sh` writes a log line once, however many operations give it**, and a patch can carry one `log` line for every operation that gives none.
- **`knowledge-apply.sh` writes a bare web address in a log line or an open question as an autolink**, which markdownlint accepts.
- **The sidecar's `.lokf/.gitignore` ignores `.cache/`**, where a domain host's federation build keeps the members' release zips.

## [0.45.0] - 2026-10-16

### Changed

- **A skill page's word budget no longer counts table pipes or separator rows.** The budgets are unchanged.
- **A confirmed concept that a question put back to draft reads "reopened", not "still a draft".** `knowledge-report.sh` keeps the confirmed rung and adds a flag naming the day, the asker and how many questions wait, and the label tables and the website's card say the same.

### Fixed

- **`scripts/sync-sidecar.sh` writes the sibling's changelog entry in full**, naming the copies the sync changed, and ends it with "No plugin change" only for an Obsidian plugin.
- **The repository contract skips a sibling's website build output**, whose folded YAML strings it read as links ending in a backslash.
- **`scripts/sync-sidecar.sh` keeps a host's own `schema :=` line in its justfile**, so a domain host's members are validated against its schema, not LOKF core.
- **`scripts/sync-sidecar.sh` reports a sibling whose bundle fails `lokf-check-refs`.**

## [0.44.0] - 2026-10-16

### Added

- **ktl-sidecar gains federation templates for a domain host**: `knowledge-federate.py`, `knowledge-federation.yaml` and `domain.yaml` build one workspace from the released bundles a domain names, one named graph each, and gate links no member owns. `docs/context-layer.md` holds the design.

### Changed

- **`docs/install.md` gives one `gh skill install --all` line, with `--agent`, and the GitHub CLI 2.90.0 floor.** The contract keeps every tracked `SKILL.md` under `skills/ktl-*/`, so `--all` installs only the ktl- skills.

### Fixed

- **ktl-website's link check reads an address in a code span without its closing backtick.**

## [0.43.1] - 2026-10-15

### Changed

- **The README links the website's pages on `w3id.org/ktl`**, rather than Markdown files on GitHub.

### Fixed

- **`scripts/sync-sidecar.sh` copies `.lokf/justfile` but keeps the sibling's first line, which names the host.** Check 11 holds this repository's copy to the template the same way.

## [0.43.0] - 2026-10-15

### Added

- **A ktl-website site serves the whole bundle as `llms-full.txt`**, each concept's text after its trust label, and its link check reads the text files too.
- **A ktl-website site offers the bundle log as an Atom feed, `knowledge/log.xml`**, with an entry for each day.
- **A ktl-website concept page links the concept's history and names its licence**, and the overview page, the feed and the two text files name the bundle's.
- **A ktl-website concept page opens the knowledge graph on the concept** at `/graph/?concept=<id>`, and the address follows the selected node.
- **A ktl-website page previews a concept link** with its title, type, trust label and definition, on hover or keyboard focus.
- **A ktl-website site serves each docs page as Markdown at its path with `.md` added**, and `llms.txt` links those files rather than the HTML.
- **A ktl-website release page links the release, and the repository, the docs and the bundle at its tag**, which the new `RELEASE_TAG` option names.
- **A ktl-website page and its retelling offer each other as reading levels.** A `PAGES` entry's `retells` names the page it retells, and a concept with an `audience` field or an `audience-` tag retells the concept its `derivedFrom` names.

### Changed

- **GitHub's dark theme shows the `-dark` figures, as the site does**, and the sync no longer swaps a `-dimmed` source for a `-dark` one.

### Fixed

- **The ktl-website graph explorer fits the graph to its stage once the layout settles.**

## [0.42.0] - 2026-10-14

### Changed

- **The README, the architecture page and the plugin's homepage link to the site at `https://w3id.org/ktl/`.**
- **The README lists Exhibitions, the sites that show a repository's collection**: this repository's bundle and AI-LinkMO's.
- **The bundle's `base_iri` is `https://w3id.org/ktl/knowledge/`**, in place of `knowledge-trust-ladder.example`, so every concept's IRI resolves.
- **A ktl-website data page opens Datasette Lite in a new tab.**

### Fixed

- **`sync-sidecar.sh` sets its next steps apart with blank lines.**
- **A move of the bundle's `base_iri`, as ktl-librarian's Rule 2 describes, no longer reads as an edit of every confirmed concept**, since conventions rule 13 compares each id and relation target by its path under each commit's base.
- **A release's changelog lists each entry once**, even when a stacked pull request still carries another's entries.

## [0.41.0] - 2026-10-14

### Added

- **A ktl-website site shows the pages `gen-doc` writes for a LinkML schema under a Schema topic**, through `SCHEMA`, and draws a mermaid diagram on any page.
- **A ktl-website site can serve the data as SQLite databases to open in Datasette Lite.** They stay off until `BROWSE` is set, and their Datasette metadata is published without its `plugins` settings.

### Changed

- **The knowledge website workflow also runs weekly, and on a change to a justfile, a `pyproject.toml` or a `uv.lock`.**

## [0.40.0] - 2026-10-14

### Added

- **A ktl-website home page offers an Architecture button when `docs/architecture.md` is on the site.**
- **The scheduled librarian takes an agent that wants its prompt somewhere other than after `-p`**, through the repository variable `AGENT_PROMPT_FLAG`, which names the flag, or `arg` for the last argument. The sidecar's automation page states the five conditions any agent must meet.

### Changed

- **A ktl-website site shows the Knowledge Trust Ladder logo unless its configuration names another.** `LOGO` defaults to `"auto"`, which takes the repository's logo or the template's copies, and `null` shows the title as text.
- **The README and docs pages lose their dead sentences.** No skill changed.

### Fixed

- **`sync-sidecar.sh` writes each sibling's sync on a branch of its own, `sync-<tag>`, from origin's default branch**, and skips a sibling with uncommitted changes.
- **The scheduled librarian writes its patch with the agent's file tool**, as the wrapper's prompt now says, since a shell write is denied. The documented Claude Code command drops `Write(.lokf/patch.yaml)`, which `Edit(.lokf/patch.yaml)` covers.

## [0.39.0] - 2026-10-13

### Added

- **ktl-website installs a website for any repository's knowledge bundle**, with a page per concept and its trust label. Its workflow, `knowledge-website.yaml`, builds the site on every pull request and publishes it to GitHub Pages once `KNOWLEDGE_WEBSITE_ENABLED` is `true`. The contract holds this repository's site to the template, and a smoke test builds it.

### Changed

- **The website reads the repository's values and options from `website/site.config.mjs`**, so the same site builds for any repository with a knowledge bundle.
- **This repository's website workflow, `website.yml`, is a copy of the skill's template**, and deploys only once the repository variable `KNOWLEDGE_WEBSITE_ENABLED` is `true`.

### Fixed

- **A concept's source link keeps its leading dot**, as in `.github/workflows/validate.yml`.

## [0.38.2] - 2026-10-13

### Changed

- **The README is cut to the poem, the opening paragraph and its links**, and names LOKF and LinkML as inspirations. Its library, museum and roles story moved to `docs/architecture.md`, and its quick start to `docs/install.md`.
- **The retelling for readers aged 13 to 18 is now `docs/architecture.en-simple.md`, beside the page it retells**, and the website still serves it at `/simple/`.
- **The website's home page keeps four buttons**: Browse the bundle, Architecture, Glossary and Quick start. The Architecture group opens with the architecture page.

### Fixed

- **The pen adds its edited-since note to a log line once**, whatever the case of an existing note.

## [0.38.1] - 2026-10-13

### Added

- **A website in `website/`, built with Astro Starlight from the README, `docs/` and the bundle**, which `website.yml` publishes to GitHub Pages with the four files `lokf export` writes. Each concept page shows its trust label, sources and typed relations.
- **`docs/context-layer.md` places Knowledge Trust Ladder in the context-layer discourse** and designs a federation of bundles, and `docs/context-layer-technology.md` surveys the systems it would connect to.

### Changed

- **The research pages are trimmed to what KTL took and what remains.**
- **The READMEs and ktl-librarian's Golden Rule 1 link OKF's specification at `GoogleCloudPlatform/open-knowledge-format`**, where Google moved it from `knowledge-catalog/okf/`.
- **The website's home page makes Browse the bundle its primary button**, and Quick start a secondary one.

## [0.38.0] - 2026-10-11

### Added

- **ktl-prose writes for younger readers.** `references/young-readers.md` sets the limits for readers aged 8 to 12 and 13 to 18, who get a retelling in a new file, and for dyslexic readers, who get a rewording.
- **prose-check.py holds a page to a band of readers** with `--audience 8-12`, `13-18` or `dyslexia`, and reports Latin abbreviations such as `i.e.`. It notes the Automated Readability Index, and each word outside the VOA Learning English word book, which is in the public domain and in `assets/`. A page that opens "This page is for readers aged 13 to 18." is held to that band with no flag.
- **prose-check.py checks that a retelling adds nothing**: `--derived-from ADULT YOUNG` reports a number, link or code span the original does not hold. The retelling's first paragraph must link the original, and in a bundle `derivedFrom` must name the adult concept.
- **`README.en-simple.md` retells the README for readers aged 13 to 18**, and `docs/examples/prose.md` captures the retelling.
- **A bundle can declare its younger readers** in the curation policy's optional `Younger readers:` line, which `prose-check.py --bundle` reports.
- **The librarian retells, and the docent answers, for younger readers.** ktl-librarian's `references/retellings.md` says how, a scheduled run retells only a confirmed concept, for a band the curation policy declares, and ktl-docent and its Copilot copy keep every label.

### Changed

- **The install commands install all five skills for your user**, and both READMEs open with a Quick start that holds every install command. `docs/install.md` says when a team installs into the repository instead.
- **A domain schema is one variable in the sidecar's justfile, `schema := ""`.** The `lokf-validate` and `lokf-check-refs` recipes, which the registrar, librarian and release workflows run, pass it as `--schema`, and a host sets it by hand or through the linkml-sidecar skill.

### Fixed

- **A docs-only merge after a promotion no longer fails the release job**, and a failing check writes its reason as a GitHub annotation.

## [0.37.1] - 2026-10-07

### Added

- **The schema is the source of the class list and of the relation fields.** Contract checks 7c and 7d hold Rule 3's class list and `knowledge-report.sh`'s relation fields to the schema at the lokf floor the templates pin.
- **ktl-sidecar's portability page says what is tested before a release, and what stays with the host**: an edited copy, a port to another forge or shell, and another operating system.

### Changed

- **ktl-docent follows all thirteen typed relations when it widens along the graph**, adding `sameAs`, `measures`, `memberOf` and `holder`.
- **The behavioural tests of the sidecar scripts moved out of the repository contract into `tests/`, run with pytest by `validate.yml` and before each release.** Each check's number stays in the contract with a line saying where it went, and `scripts/test-sidecar-layouts.sh` moved there too.

### Fixed

- **The report script counts reliance through `measures`, `memberOf` and `holder`**, so through all thirteen relation fields, as ktl-curator's trust-fields.md now says.

## [0.37.0] - 2026-10-07

### Added

- **ktl-librarian has a page for a host whose content is Agent Skills**, `references/agent-skills.md`, which says which skills are the host's own and what a skill's concept holds. The first run's sweep table names Agent Skills folders.
- **`docs/skills-repositories.md` says whether KTL helps a repository whose content is Agent Skills**, from a run on `anthropics/skills` at commit `683bc88`.

### Changed

- **`docs/threat-model.md` names a skills repository, where every source the librarian reads is instructions for an agent**, and says that only the pull request's reviewer catches an instruction that shapes a concept.

## [0.36.1] - 2026-10-07

### Security

- **The provenance gate reads a `verified` or `generated` event that spans lines, so a forged confirmation cannot hide in a multi-line flow layout.** Checks 13a and 22 cover it.
- **The provenance gate reads a concept behind a byte order mark or in CRLF line endings, so a forged confirmation cannot hide behind one either.** Check 22 covers both.
- **The unattended provenance check follows a renamed concept, so a person's text cannot be rewritten under a new name.**
- **The pen refuses a provenance or event key in any case, and a top-level event field**, so a patch cannot write a `Verified:` or a top-level `by: human:`. Check 19 covers it.
- **The pen keeps a curator's send-back, a `process:ktl-curator` note, and never joins a protected heading, such as `## Open questions`, to the line before it.** Check 19 covers each.

### Added

- **Check 22 holds the gate's event reader to a real YAML parser**, in every layout a person might write a human event in.

### Fixed

- **The report script reads every timestamp and event layout a YAML parser does**, such as a `+00:00` offset or a multi-line `verified` list, so it gives each concept the right label. Check 20 covers each.
- **The report script counts an edited-since concept once, and reads a CRLF `index.md`, a successor-less retirement and a subfolder sidecar.** Checks 20 and 20a cover each.
- **The pen keeps a null value as written, writes atomically, scrubs a log line and a question by Unicode category, and clears a `./`-led or `#fragment` index link on delete.** Check 19 covers each.
- **`prose-check.py` skips an indented code block and reads a prose line that opens with an inline HTML tag.** Its comparison reports a changed inline tag or a dropped hard line break, reads a list marker only at the start of a block, and notes a change of a fifth. Check 18 covers each.
- **The registrar scopes rule 14 to the pull request's merge-base, the feedback script rejects a `.` path segment, and both read login characters the same in every locale.** Check 12a covers each.
- **Contract check 15 reads the pinned skill path from the commit the pin records, not only from the tag ref**, so it no longer skips on a checkout with no tags.
- **The layout tests no longer fail now and then on a SIGPIPE race, isolate their git config, and leave no temporary files behind.**

## [0.36.0] - 2026-10-06

### Added

- **Each skill's page has a word budget, which contract check 10a holds every `SKILL.md` to.** An edit that adds words to a page moves as many into that skill's `references/`.
- **The curator's queue comes from the script**: `knowledge-report.sh` prints it, from reliance counts to *Worth ten minutes today*, ranked as `references/trust-fields.md` says, and ktl-curator quotes it. Check 20a covers it.
- **A retired concept names what replaced it.** ktl-curator's *Retire* links the successor after "replaced by" in its `**Deprecation**` line in `log.md`, which `knowledge-report.sh labels` and ktl-docent read. LOKF has no typed relation for a successor yet: [nicholsn/lokf#112](https://github.com/nicholsn/lokf/issues/112) asks for one.
- **A reader's disagreement shows on the concept.** `knowledge-feedback.sh --concept <path>`, which ktl-docent passes, names the disputed concept, and `knowledge-report.sh labels` marks it *a reader disputed this on* that day. The report reads the path, never the entry's text.
- **Conventions rule 14: a commit that records a person's confirmation changes the verdict, not what the concept says**, unless `generated.by` names that person, as *Correct now* does. `knowledge-conventions.sh --since <commit>` checks it, and check 11c covers it.
- **`docs/skillwiki.md` reads the SkillWiki paper (Huang et al., 2026) against this design**, the README credits it, and `docs/wikiskill.md` tells the two papers apart.

### Fixed

- **ktl-curator's two pages rank its queue in the order the script applies**, and the SPARQL query for the most relied-upon concepts counts each citing concept once, and never a concept for itself.

## [0.35.0] - 2026-10-06

### Changed

- **ktl-prose lays out what it rewords the way the file's project does**: one line for each paragraph in a bundle, and the host's layout outside it, as `references/rules.md` sets out.

## [0.34.2] - 2026-10-05

### Changed

- **The preflight reads the CI variables by indirect expansion, not `eval`**, so a scanner that searches for `eval` finds none. It still runs in bash 3.2.
- **The preflight names who needs a missing `knowledge-feedback.sh` or `knowledge-report.sh`:** ktl-curator, and an older ktl-docent.

### Security

- **ktl-docent runs its own copies of `knowledge-report.sh` and `knowledge-feedback.sh`, never the repository's**, since anyone who can commit to a repository can change its `.lokf/scripts/`. Check 11a holds the copies byte-identical to the templates, the docent reads a login from `gh` or `glab` instead of running the preflight, and without its scripts it never writes `.lokf/feedback.md`.
- **ktl-docent puts the asker's login in an entry only when the asker agrees**, since the entry can reach a public pull request and git history.
- **ktl-docent and ktl-curator keep only the `username` from `glab api user`**, not the whole profile with its email.
- **ktl-librarian and ktl-sidecar read the no-Python schema from a commit, not a tag**, since a tag can be moved (Snyk W012), and read it as data, never instructions. Check 11b fails a tag or a branch in its URL.

## [0.34.1] - 2026-10-05

### Changed

- **The Copilot docent's gap report gives the librarian what ktl-docent's does**, and the skill gives source links and finds endpoints as ktl-docent does, under the heading `ktl-docent-m365`.

### Fixed

- **The Copilot docent, and ktl-docent's rules for a sidecar with no script, label a concept as `knowledge-report.sh labels` does**, so a retired concept carries no other label.
- **Every label table reads an empty `verified` list as *nobody has checked this yet*, as the report script does.**

## [0.34.0] - 2026-10-05

### Added

- **The librarian's pull request says how the conventions script ended**, since the registrar's gate does not run on a pull request the workflow opens.
- **`knowledge-report.sh changes` says what a change does to each confirmed concept**, such as *its confirmation is gone*.
- **ktl-prose rule 10 cuts "own", "itself" and "at all" where they draw no contrast.**
- **`prose-check.py` counts the words before and after a rewording**, and notes a changed day or month and a cut of more than a fifth.
- **A scheduled librarian run opens no second pull request beside an open one**, and a run a person starts names the open one. A new job in `knowledge-librarian.yaml`, `earlier`, lists the workflow's pull requests with a token that reads only pull requests.
- **What a person declined is not proposed again until it changes.** A scheduled run reads a record of each pull request a person closed without merging, and the work list names it under *Declined*.
- **The preflight warns when git holds no `.lokf/uv.lock`** on a host that carries the registrar workflow.

### Changed

- **The pen refuses a patch that handles more than ten reader entries**, the limit ktl-librarian states for a run.
- **The registrar's gate and the release workflow install the toolkit with `uv sync --locked`.** A host whose `.lokf/uv.lock` is missing from git, or behind `.lokf/pyproject.toml`, now fails at the install step: run `uv lock` in `.lokf/` and commit the file.

### Fixed

- **The pen writes a value back as the file held it**, so `1.10` stays `1.10` and a person's event no longer reads as changed. It also takes an all-digit commit hash as `revision`.
- **The retrieval score leaves out a question whose concept has left the bundle**, and says how many it left out.
- **Conventions rule 10 reports a comment beside `id`, `by`, `at` or `revision`**, which a line reader takes for part of the value.
- **`docs/wikiskill.md` says the paper's raw layer keeps every trace, not its wiki.**
- **A week is quiet again once the librarian has asked about a source it cannot act on**, such as a confirmed concept's deleted source, until that source changes.

### Security

- **A person's record is the same after the pen writes as before**: the pen refuses a patch that would change a `human:` event or a person's note. Check 19 exercises three such patches.
- **A reader's question and the hand-off hold no character a reader cannot see**, such as a tag character that hides text from a reader and not from a model. The pen and `publish` go by Unicode category, as check 21 does.
- **The hand-off a reviewer reads is the pen's, after the retrieval call too**: the wrapper writes it again once that call, which carries readers' words, returns.
- **A reply cannot add to what it is scored against**: the retrieval scorer reads the expected concepts apart from the reply.
- **The skill a scheduled run installs is pinned to a commit**, since a moved tag could give an unattended agent other instructions. `TRUST_LADDER_SKILLS_SHA` holds the commit, the install step stops unless the tag still names it, and check 15 holds the template's commit to its tag.
- **The conventions script and the pen pin PyYAML**, and `exclude-newer` takes no file uploaded after a set date.

## [0.33.0] - 2026-10-04

### Added

- **The README shows who writes the bundle and what checks it**, with `.assets/ktl-architecture.svg` in place of its lifecycle diagram.
- **The README defines a docent, a registrar, an accession and the sidecar where it first names each, and links the bundle's glossary**, which defines all four and *desk*. The README pointer that ktl-sidecar installs says what a docent is too.
- **ktl-prose keeps one topic to a paragraph, and says what happens in plain words.** Rule 3 asks that a paragraph past 150 words be split, and rule 9 asks for the literal verb, as ktl-librarian's rules now do. `prose-check.py` reports a long paragraph as `paragraph`, and seven figures under `words`.
- **`prose-check.py` reports a character no reader sees, as `unseen`**, such as a zero-width space, in code and frontmatter too, and refuses a rewording that adds one. Check 18 exercises both.

### Changed

- **In a live session, ktl-librarian and ktl-curator open a pull request only when the person says so**, since that person is the change's author, as the AI covenant says.
- **The docs, the skill pages and the script comments read plainer**: a third pass replaced figures of speech with what happens, and split every paragraph and comment block past 150 words. No fact changed.

### Security

- **The contract fails on a character a reader cannot see in any tracked file**, such as a zero-width space, which no diff shows. Check 21 holds the rule, and code that needs one spells it as an escape.

## [0.32.0] - 2026-10-04

### Added

- **A scheduled week with nothing waiting for the librarian runs no agent**, when `KNOWLEDGE_SKIP_QUIET` allows and `knowledge-report.sh quiet` agrees. A run in a month's first seven days still goes ahead, since the work list never fetches a source given as a URL (check 20).
- **The librarian's hand-off reaches its pull request**: the patch file's `handoff`, up to ten printable lines, shows in a code block and never in the bundle.
- **Conventions rule 13: a confirmed concept still says what its person confirmed.** A hand edit to its body or claims must move `generated.at` past the confirmation, so it reads *edited since*. The open questions, KTL Registrar's block and the trust fields are exempt (check 11).

### Changed

- **ktl-librarian's page is half as long**, with detail moved to `references/golden-rules.md`, `references/bootstrap.md` and `references/audit.md`, and a host without the pen runs ktl-sidecar's repair in place of the by-hand fallbacks. The librarian now stamps a concept when it reads a person's note.

### Security

- **The wrapper removes the retrieval score and hand-off files once the agent returns**, so the agent cannot plant its own score, or a link that sends the next write into the checkout.

## [0.31.0] - 2026-10-04

### Added

- **`docs/for-the-curious.md` shows who writes the bundle and what checks it**, in a new diagram, `.assets/ktl-architecture.svg`. The README and the bundle's glossary say why `knowledge-apply.sh` is called *the pen*.
- **Check 16b keeps KTL's roles, skills and repositories from being named after LOKF**, except in the changelog, the bundle's log and the source map's dated notes.

### Changed

- **The pages name Knowledge Trust Ladder (KTL), the bundle and LOKF apart**: KTL is the design, the bundle is its corpus in `.lokf/knowledge/`, and LOKF is the format and its toolkit. `references/trust-fields.md` drops *whoever held the pen*.
- **Each skill's heading is its name, such as `# ktl-curator` in place of `# KTL Curator`**, and the pages call the Obsidian plugin *the KTL Curator plugin*.

### Fixed

- **The trust ladder's middle rung credits the librarian's refresh, not the schema check**, since the refresh writes the `process:` event that *Checked by automation only* means.
- **The three-lines diagram names every part of the registrar, and its title says *KTL role*.** The two-vaults diagram shows `services/`, not `concepts/`.
- **The preflight reports `ktl-prose` and a stale copy of it**, and its note for a host without `uv` counts seven of the twelve conventions.
- **`docs/signing-commits.md` says a signature is required to remove a confirmation, as to add one.**
- **`scripts/sync-sidecar.sh` copies each template that a synced copy cannot run without**, such as the apply script beside the wrapper, and each that ktl-sidecar puts on every host.
- **The pen keeps an index in the shape a person gave it**: it rewrites only a line that holds nothing but the concept's link, and finds a folder's section at any heading level below the title. It refuses to delete a concept that a sentence links, and conventions rule 12 reads a line of two links as neither one's bullet (check 19).

## [0.30.0] - 2026-10-03

### Added

- **`knowledge-report.sh` computes what the skills used to work out**: the trust labels, the health line, the work list and a change's effect on the record. It judges that a source moved by git history, not a clock (check 20).
- **The scheduled pull request can carry a retrieval score**, off unless `KNOWLEDGE_RETRIEVAL` is `true`, for the concepts that the agent picks from `index.md` for readers' questions. It gates nothing.
- **`.lokf/questions.md` is a ledger of the questions that readers asked, and only grows**: `knowledge-apply.sh` moves each handled feedback entry there.
- **The pen gains `resolve`, which withdraws an open question that the librarian asked but never a person's note, and `--format`, which prints the patch file's shape** (check 19).
- **Conventions rule 12: an index bullet carries its concept's title and description**, and the pen's `reindex` operation repairs one that a hand edit left behind.

### Changed

- **ktl-librarian starts a refresh from the work list**, reading a local source again only when it moved, and searches the bundle for the old value of a changed count or name. It withdraws its answered questions, leaves a person's answered note to the curator, and keeps a reader's words out of the bundle.
- **The health line counts a concept edited since its confirmation once**, under *Edited since confirmed* and no longer under *Confirmed by a person*.
- **ktl-curator clears answered open questions on *Correct now* too**, and its report lists apart the questions that a later confirmation answered and the confirmed concepts whose source moved since.
- **The scheduled pull request is filled by `publish`, the job that opens it**, which takes only the retrieval score's two integers from the job that ran the agent.

### Fixed

- **A sidecar installed from 0.29.0 paired the new wrapper with a skill that predates the pen.** The wrapper now takes the patch format from `knowledge-apply.sh --format` and warns of an older pinned skill. Such a host moves `TRUST_LADDER_SKILLS_REF` to `v0.29.0` or syncs to this release.
- **`docs/wikiskill.md` says the paper's ablation ran on four benchmarks, not five.**
- **A `from_feedback` line that `feedback.md` does not hold is a finding, not a traceback.**

### Security

- **A person's record is never removed without that person**: the provenance gates ask for them when a change removes their `verified` event, even by deleting its concept, and only another person's `generated` record replaces theirs.
- **`publish` checks a person's events on the patched tree, not by a line pattern.** `knowledge-provenance.sh --unattended` refuses any change to a person's events, notes or text, in any YAML layout, and the wrapper runs it after the pen too.
- **The pen refuses to delete a concept that a person left a note on**, as it refuses one that a person confirmed.
- **A reader's words no longer reach `log.md`**, which ktl-curator opens, and stay in the ledger.

## [0.29.0] - 2026-10-03

### Added

- **A fifth skill, `ktl-prose`, rewords a bundle's agent-written, unconfirmed concepts in plain English**, changing no fact and no frontmatter byte. Its `prose-check.py` proves that only wording changed (check 18).
- **`docs/wikiskill.md` reads the WikiSkill paper (Tang et al., Google Research, 2026) against this design**, and the docent examples link the concept behind each question, so renaming or deleting it fails the link check.
- **ktl-librarian writes the bundle only through `knowledge-apply.sh`, the pen**, from seven operations in `.lokf/patch.yaml` (`references/patch.md`). The pen refuses a `human:` actor, a rewrite of a person's text or the deletion of a confirmed concept, and writes nothing unless every operation passes (check 19).

### Changed

- **ktl-librarian writes in plain English, and offers a `ktl-prose` pass in a live session** before it opens its pull request.
- **ktl-librarian reads the curator's verdicts before it derives**, and re-derives a sent-back concept from the note's source. It fixes a reader's miss in the answering concept's `description` and index bullets, never with a twin, at most ten a run. Rule 3 reaches a `Person` or `Organization` through `author` or `publisher`, not `source`.

### Fixed

- **ktl-docent and the Copilot docent treat a concept edited after a person confirmed it as unconfirmed**, and label it *edited since a person last confirmed it*.
- **ktl-curator compares the two times of "edited since" whole**, so a concept rewritten on the day it was confirmed counts as edited.
- **The skills no longer claim a SHACL check that nothing runs**, and name `lokf validate` (JSON Schema) and `--check-refs`.

### Security

- **The scheduled librarian's agent writes only `.lokf/patch.yaml`.** The wrapper applies it with the pen and refuses a run that touched any other file, so the pen's refusals hold unattended.

## [0.28.0] - 2026-09-29

### Added

- **Release assets can carry a host's published name**, from the `KNOWLEDGE_RELEASE_NAME` repository variable, or else the repository's.

## [0.27.2] - 2026-09-25

### Security

- **The Snyk W011 findings on ktl-librarian and ktl-docent are acknowledged** in each skill and [the threat model](docs/threat-model.md#prompt-injection-guards). The librarian resolves only what a feedback entry names, and the docent writes only a scripted feedback entry.

## [0.27.1] - 2026-09-25

### Fixed

- **`atk add skill` works with the released Agents Toolkit**: `docs/m365.md`, the sidecar's `references/m365.md` and the Copilot playbook set `TEAMSFX_AGENT_SKILLS`, which the 1.1.17 release reads, besides `ATK_FRONTIER`, which only the 1.1.18 betas read.
- **The toolkit route in `docs/m365.md` runs in the agent's project**, passes `--env dev`, skips `atk validate`, which rejects `agent_skills`, and keeps both variables exported for `provision`.
- **`docs/m365.md` says what a tenant without the Frontier preview sees**: `atk provision` fails with `Unrecognized member 'agent_skills'`, and Agent Builder sends the skill to Copilot Studio, which needs its own licence.

## [0.27.0] - 2026-09-24

### Added

- **Releases carry the docent as a Microsoft 365 Copilot skill**, `ktl-docent-m365-<tag>-<repository>.zip`, for upload to Agent Builder. `knowledge-m365.sh` in the new `.lokf/m365/` folder packs it within Copilot's limits (check 17).
- **`scripts/sync-sidecar.sh` syncs a sibling repository to one release**: it copies the tag's templates, moves the skills pin to the tag, runs the sidecar's checks and leaves the diff for review. `docs/releasing.md` drops the hand bump of the template's pin.

## [0.26.0] - 2026-09-24

### Added

- **Conventions rule 11 rejects an `at:` later than the commit that recorded it**, and ktl-librarian and ktl-curator take every `at` from `date -u`.

## [0.25.0] - 2026-09-24

### Changed

- **The release workflow attaches the bundle as a reproducible zip**, `knowledge-<tag>-<repository>.zip` with its `.sha256`, in place of the tarball.

## [0.24.0] - 2026-09-24

### Added

- **A third sidecar workflow, `knowledge-release.yaml`, attaches the bundle to a GitHub release** once the registrar's checks pass, with a checksum and, on a public repository, an attestation. It runs by hand, or on each release with `KNOWLEDGE_RELEASE_ENABLED`, and skips an unchanged bundle unless `force` is set. This repository's `publish.yml` dispatches it.
- **The librarian template takes the agent's credential**, the `AGENT_API_KEY` secret or, with `AGENT_USE_JOB_TOKEN`, the job's token. The wrapper exports it only under the name that `AGENT_API_KEY_ENV` gives, and refuses a name that `gh`, git or the runner also read.

### Fixed

- **The librarian runs `lokf validate --check-refs` before it opens a pull request**, since the registrar gate never runs on that pull request.
- **The sidecar README's layout tree names everything that Step 5 creates.**

## [0.23.1] - 2026-09-24

### Fixed

- **The librarian template no longer installs the pinned skill in `noelmcloughlin/knowledge-trust-ladder`**, whose scheduled runs used that old copy in place of the source. This repository's workflow matches the template apart from its skills pin (check 11).
- **The release commit moves the skills pin in the template only**, since `GITHUB_TOKEN` may not push a change under `.github/workflows/`.
- **The preflight no longer reports a host's own skills pin as drift.**

## [0.23.0] - 2026-09-23

### Added

- **A sixth sidecar script, `knowledge-feedback.sh`, files a reader's Miss or Disagreement** in `.lokf/feedback.md` and prints only a kind, a date and a count. The preflight names a sidecar without it (check 12a).

### Changed

- **ktl-docent records a gap by running that script**, and never reads `feedback.md`. A host on an older sidecar runs the ktl-sidecar repair.
- **The README, docs pages, skill introductions and workflow comments are restyled for the reader.** The critics page is arranged by criticism, and the host-by-host layouts move to `docs/obsidian.md`.

### Fixed

- **Scheduled runs on a scaffolded host no longer fail at the install step**: the template pins `v0.22.0` in place of `v0.21.0`, which predates the `ktl-` names, and check 15 reads the pinned tag for `skills/ktl-librarian`.

### Security

- **Reader feedback no longer reaches the docent's context** (Snyk W011), since the script inserts each entry. ktl-librarian is the only skill that still reads one.

## [0.22.0] - 2026-09-22

### Added

- **Each of the seven diagrams gains a dark counterpart, `*-dark.svg`, and a dimmed one on warm grey, `*-dimmed.svg`, which the Markdown picks by theme.** The light original stays the fallback at its path.

### Changed

- **The skills take the `ktl-` prefix**: `ktl-curator`, `ktl-docent`, `ktl-librarian` and `ktl-sidecar`, formerly `lokf-curator`, `lokf-docent`, `lokf-librarian` and `lokf-sidecar`. The Obsidian plugins are KTL Registrar and KTL Curator (`obsidian-ktl-registrar`, `obsidian-ktl-curator`). A host upgrading from 0.21.0 reinstalls the skills, removes the `lokf-*` copies, renames its bundle's `process:lokf-librarian` and `process:lokf-curator` actors, and moves `TRUST_LADDER_SKILLS_REF` to a release that carries the new names.
- **The dark-mode source is the dimmed set**, and nothing references the `*-dark.svg` files left in `.assets/`.

### Fixed

- **A recoloured copy carries no C2PA content credential**, since the original's would no longer verify.
- **The dimmed ink darkens with the dimmed paper**, so faint labels keep 4.5:1, and two labels that never met 4.5:1 now do.

## [0.21.0] - 2026-09-19

### Added

- **Skill descriptions end in a `Keywords:` list**, so catalogs without a tag field find these skills under OKF or trust ladder. Check 3c holds the list, and the spec's 1024 characters.
- **A Claude Code plugin manifest, `.claude-plugin/`, offers the four skills as one plugin, `knowledge-trust-ladder`**, with keywords for plugin catalogs.

### Fixed

- **The librarian's publish job accepts a concept named outside ASCII**, listing paths with `core.quotePath` off, as the provenance gates do.
- **The skills pin moves with each release**: `semantic-release.yml` sets `TRUST_LADDER_SKILLS_REF` to the newest tag, so check 15 no longer fails `main`.
- **The docent treats entries already in `.lokf/feedback.md` as untrusted**, as the librarian and the curator do.

## [0.20.0] - 2026-09-19

### Changed

- **The relation audit and the registrar gate run `lokf validate --check-refs`, not a hand-written SPARQL query**, so the gate validates once. The audit covers reified `relations` and a domain schema's slots, and no longer reports an external `source` or `definedBy` as missing.
- **The librarian's recipe passes a domain schema's `--schema` to `lokf-check-refs` too.**

### Fixed

- **The librarian template pins `v0.19.7`**, so a new host installs the current librarian.

## [0.19.7] - 2026-09-19

### Fixed

- **The librarian template pins `v0.19.6`**, so a new host installs the current librarian.

## [0.19.6] - 2026-09-19

### Added

- **A logo mark, `.assets/knowledge-trust-ladder-logo.svg`, shows a ladder rising out of an open book**, and both plugin repositories share it. It is the repository avatar, and every diagram carries it with the wordmark, which titles the social-preview card.
- **`docs/install.md` takes the install commands, prerequisites and pinning rule out of the README.**
- **The README states the project's claims**: a runtime for OKF's trust frontmatter, built specification, schema and interoperability first. It answers the context layer's question of who is responsible for the quality of the context, and takes in the domain schemas that OKF puts out of scope.

### Changed

- **The README introduces the project and leaves the manual to `docs/`.** Its opening says "collection", not "library", which this audience reads as a code library, names the whole system with the Obsidian plugins as optional, and calls `knowledge_bundle` the visible doorway to `.lokf/`.
- **This repository is now `knowledge-trust-ladder`, formerly `lokf-agent-skills`**, since a name after the format read as upstream LOKF's official home. The four skill names stay, and GitHub redirects the old clone and `npx skills add` paths.
- **`LOKF_SKILLS_REPO` and `LOKF_SKILLS_REF` are now `TRUST_LADDER_SKILLS_REPO` and `TRUST_LADDER_SKILLS_REF`.** An older copy of the template works through the redirect, and each sibling renames both before it next syncs.
- **The bundle's `base_iri` is `https://knowledge-trust-ladder.example/knowledge/`**, which changes every concept's id and relation target.
- **`lokf-trust-ladder.svg` is now `trust-ladder.svg`**, the diagram's name rather than the project's.
- **The repository contract refuses the old name (check 16)**, except in `CHANGELOG.md`, one "formerly" line in `docs/install.md` and the bundle's `log.md`, which keeps each day's name.
- **The three-lines diagram follows the legend it shares**, with neutral bands and each card in the colour of whoever acts.
- **The diagrams no longer glare, and their labels are legible**: a warm `#E4E1D7` canvas replaces pure white, the faint ink moves from `#888780` to `#6E6D66` to clear 4.5:1, and six labels no longer overflow or crowd their boxes.

### Fixed

- **The librarian template pins `v0.19.5`, the newest release a host can clone**, since the top changelog heading is promoted before its tag exists.

## [0.19.5] - 2026-09-19

### Security

- **The curator counts reader feedback with `grep -c`, and never opens, quotes or acts on an entry.** The skill and [the threat model](docs/threat-model.md#prompt-injection-guards) acknowledge the Snyk W011 finding on lokf-curator: every curator write is a live person's verdict.

## [0.19.4] - 2026-09-19

### Fixed

- **An unauthenticated send-back is attributed to the session, as `process:lokf-curator`**, so conventions rule 4 no longer rejects it at the gate.
- **The librarian template pins the current release**: `LOKF_SKILLS_REF` moves from `v0.19.2` to `v0.19.4`.

### Security

- **The provenance gates read a concept whatever its name**: they list paths with `core.quotePath` off, so a non-ASCII name no longer hides a `human:` confirmation, and refuse a path that git still quotes (check 13).
- **The registrar's step summary strips backticks from an id that failed the login pattern**, so the id cannot render as Markdown.
- **The Snyk W011 finding on lokf-sidecar is answered** in the `provenance` job's comments and [the threat model](docs/threat-model.md#prompt-injection-guards): no agent runs in that job.

## [0.19.3] - 2026-09-18

### Fixed

- **Retitling a pull request re-runs the title check**, whose trigger now names `edited`.
- **The librarian points a local `resource` only at a path that git tracks**, never at an installed skill under `.agents/`, which fails conventions rule 5 elsewhere. It names the published copy of such a skill.
- **The librarian template installs the current skill**, where it pinned `v0.9.0`. Check 15 holds the pin to one of the two newest releases, since the newest one's tag comes after its changelog heading.

### Security

- **The registrar gate sets a top-level `permissions: {}`, and its read-only jobs keep no checkout credential on disk.**

## [0.19.2] - 2026-09-17

### Security

- **The librarian wrapper restores `.git/config` and `.git/hooks/` on every exit**, a failed or cancelled run included, so a poisoned `core.hooksPath` cannot reach the workflow's next steps.

## [0.19.1] - 2026-09-17

### Fixed

- **A pull request that would release must be titled to release**, since a squash merge takes the title as its subject, and the `plan` job says how to retitle.

- **The no-Python schema fallback names the `v0.8.0` tag of `lokf.yaml`**, not upstream `main`, and moves with the toolkit's floor.

- **A pull request that releases nothing needs no release notes**, so a `chore:` or `docs:` one, such as a Dependabot bump, passes.
- **Check 11's failure after a Dependabot action bump names both directions**, not only "copy the template over it". The bump still fails the contract until the template copy is synced, since the bot cannot see it.

## [0.19.0] - 2026-09-17

### Added

- **The registrar gate resolves a `revision`**: a commit-shaped one must name a commit that holds the concept's local `resource`, and a shallow clone is reported, not passed (check 11).
- **The curator and the librarian gain portability pages, and the sidecar's becomes a host matrix** across nine kinds of host, from GitHub to an Obsidian vault.
- **Every skill declares what it needs in its `compatibility` field**, which check 3b holds to the spec's 500 characters.
- **A forge-free provenance gate, `knowledge-provenance.sh`, checks each confirmation's commit signature** against the curator's GPG or SSH key under `.lokf/curators/`, with plain git (check 13).
- **Every skill runs `knowledge-preflight.sh` first**, which prints what the machine can do and which steps a gap disables, and a prerequisites page says who fixes each line (check 12).
- **The sidecar creates `.lokf/.gitattributes`**, keeping the bundle on LF so a Windows checkout gives CI's verdict.
- **The gate checks three more conventions**: one file per `id`, lowercase paths, and a closed frontmatter block with no byte order mark (check 11).

### Changed

- **The skills write and quote `revision`, from lokf 0.9.0**, and the librarian's tables name a source's `excerpt`.
- **The sidecar's toolkit floor is lokf 0.8.0**, and the librarian's field tables state its constraints, such as a bare date meaning midnight UTC.
- **The curator says what it can record before it offers a session**, from three identity routes, and the docent names the same routes. The librarian names files in lowercase and hands off on a host without git.
- **Six of the conventions script's ten checks parse YAML in `knowledge-conventions.py`**, where grep and awk missed flow-style events. Without `uv` the script names the rules it skipped, and the preflight reports a host with one half only (check 11).

### Fixed

- **The librarian's version check names a command that exists**: `uvx --from pip pip index versions lokf`.
- **The conventions script reads a Windows checkout**, stripping CRLF and a byte order mark (check 11).
- **The conventions script and the preflight read a bundle reached through a link** (checks 11 and 12).
- **The preflight reads `commit.gpgsign` as git does**, and all three scripts stop with one line under `sh`.
- **The gate refuses a `human:` id that it cannot look up**, such as `human:-x`, which both gates had skipped, so an unsigned confirmation under one passed.
- **The gate compares a confirmation whole, not its `by:` line**, so a re-dated or restyled event no longer passes. It keys events by the concept's `id`, so a renamed concept keeps its confirmations and a copy does not (check 13).
- **The conventions script no longer aborts on a runner that ignores SIGPIPE**, as GitHub Actions does, and the contract's job installs `uv` for the parser's half.
- **The `validate` check fails a confirmation spelt with a YAML tag, anchor, alias or quoted key**, which both gates missed, under conventions rule 10 (check 11).
- **Both gates read merges, `generated`, and only the frontmatter**, so a merge cannot add a confirmation unseen, and an example in a code fence no longer counts (check 13).
- **A push to `main` between releases no longer promotes `## [Unreleased]` a second time**, and the `plan` job runs `check` directly, which semantic-release skips on a pull request (check 14).
- **`publish.yml` installs `uv`, so a release can pass the contract it runs**, and the contract names a missing `uv` first.

## [0.18.0] - 2026-09-16

### Added

- **The registrar gate fails on a vanished source**: a local `resource:` must name a file or directory that exists, and a URL is never fetched (check 11).
- **The curation policy gains two switches, both off by default.** `Independent re-check: <n>` lists n confirmed concepts, picked by a rule the curator cannot steer, for a second person, and `Evidence first: yes` makes the docent quote the source behind an unconfirmed concept.

### Changed

- **`docs/three-lines.md` is written for a governance reader** and cites the IIA's 2026 Statement of Position. The model's critics have a page of their own, `docs/three-lines-critics.md`.
- **Adopter-facing text no longer addresses "solo maintainers"**: it describes the case where the confirming person opens the pull request, so the gate's evidence is their signature.
- **`EXAMPLES.md` is now `docs/examples/docent.md`**, one page for each skill's captured sessions, and `docs/examples/curator.md` lists what is still to capture.

## [0.17.1] - 2026-09-14

### Changed

- **`SECURITY.md` is a policy, not a threat model**, with a surface table that check 10 holds to a word budget. The shared design moves to `docs/threat-model.md`, which the sibling repositories link (check 9).
- **The README is shorter, and its repository tree is now `docs/repository-layout.md`.** Only the two enumerations that check 7 compares count LOKF's classes and relations.
- **The shared pages and this bundle count three LOKF repositories, not four**: a host that installs the skills is not one.

## [0.17.0] - 2026-09-14

### Added

- **Check 9 of `validate-repository.sh` holds the paths that LOKF Curator and LOKF Registrar link into**, since their link checks follow those URLs.
- **`docs/releasing.md` and `docs/signing-commits.md` hold the release pipeline and the signing walkthrough for all four repositories**, and each `CONTRIBUTING.md` links them. Check 10 holds this repository's `CONTRIBUTING.md` to a word budget, and CI fails an action that is not pinned to a commit.
- **`docs/three-lines.md` maps the cast onto the three lines of defence**, and says what an auditor can check and what the evidence does not show.
- **The registrar gate runs `templates/scripts/knowledge-conventions.sh` on every `.lokf/**` pull request**, for four conventions that `lokf validate` cannot check (check 11).

### Fixed

- **The librarian lints the Markdown it writes** with the host's markdownlint configuration, since `lokf validate` cannot see a fault such as `MD032` in a body.
- **The librarian and the curator reuse the day's `log.md` heading**, the bare date that OKF §9 requires.
- **The librarian's open questions take the curator's shape**, `- YYYY-MM-DD, process:lokf-librarian: ...`.
- **The docent no longer takes a reader's identity from `git config user.name`**, only from `gh api user`, as the curator does.

## [0.16.1] - 2026-09-14

### Added

- **`lokf-librarian/references/domain-schema.md` says how to extend the vocabulary into a domain**, where the curator's `domain-schemas.md` says when. Rule 3 counts the `Concept` descendants of a host's `--schema` as vocabulary.

### Fixed

- **Rule 3 in `lokf-librarian/SKILL.md` lists fifteen classes, adding `Role`.**

### Changed

- **The curator's vocabulary-fit line counts a host's domain schema as known vocabulary**, as Rule 3 does, and reads "doesn't fit the known vocabulary", as the LOKF Curator plugin does.
- **`lokf-curator/references/review-session.md` says how the curation-policy table is read**: class names match ignoring spaces and plural form, and an unknown class binds nothing.
- **`README.md` says each role and label once**, maps its plugin table onto the four levels of checking, and moves its Obsidian section to `docs/obsidian.md`.

## [0.16.0] - 2026-09-13

### Changed

- **Every host has one layout**: `.lokf/knowledge/` is the real folder, and Step 2 creates the `knowledge_bundle` doorway link by default again. Step 0 no longer asks what kind of host it is in, and Step 6 reports whether the doorway was made. `just lokf-link` recreates it, refuses a name already taken, and loses its `visible` variable.
- **`lokf-docent` gains `references/obsidian.md`**: the two-vault answer, and `lokf-sidecar` as the way to make a missing link, which is never a feedback entry.
- **Shared-folder guidance moves to `lokf-sidecar/references/portability.md`**: sync services drop links, so the doorway is per machine.
- **`README.md` splits its bundle section in two, and "For the curious" moves to `docs/for-the-curious.md`.**

### Removed

- **The visible layout**, a real `knowledge_bundle/` folder inside a vault, which Obsidian indexed into the vault's link suggestions, graph and search. Step 0's host decision, the `visible` variable and two layout tests go with it.
- **References to the maintainer's private vault.**

## [0.15.0] - 2026-09-12

### Changed

- **`lokf-curator/references/domain-schemas.md` says a domain schema imports a domain's existing LinkML vocabulary** beside LOKF's, rather than describing it again.
- **`lokf-scaffolding` is renamed `lokf-sidecar`**, and a bundle it already created needs nothing.
- **The Obsidian guidance opens the `knowledge_bundle` link as a vault, never the repository root**, and documents linking `.lokf/knowledge` into a personal vault.
- **`README.md` gains "Where the skills meet an Obsidian vault"**, and its "fifth role" calls LOKF Curator the curator's assistant, not a registrar, since the curator is always a person.
- **LOKF Enforcer is now LOKF Registrar** (repository `obsidian-lokf-registrar`), named for its role.

### Added

- **`lokf-sidecar` creates the bundle by host**: a code repository keeps `.lokf/knowledge` real with `knowledge_bundle` as the doorway link, and a notes vault or shared folder does the reverse, which both plugins detect. `just lokf-link` recreates a link that a sync service drops, follows a `visible` variable for a nested vault, and refuses a dangling link.
- **`scripts/test-sidecar-layouts.sh` tests the sidecar in throwaway hosts of both layouts**, under the repository-contract check.
- **`lokf-librarian` leaves alone the `<!-- lokf:related -->` block and the `diataxis.md` map that LOKF Registrar writes**, and scopes a diff by both bundle paths.
- **Semantic release computes the version from Conventional Commits and promotes `## [Unreleased]` to a dated heading**, but never tags, and `publish.yml` refuses a typed version that disagrees. See [docs/releasing.md](docs/releasing.md).

### Fixed

- **The librarian wrapper and both workflow templates name the bundle by both paths**, since a git pathspec never follows a symlink, and `git add` is guarded against a pathspec that matches nothing.
- **Windows guidance prefers a junction, `mklink /J`**, which needs no elevated rights, to `mklink /D`.

## [0.14.0] - 2026-09-12

### Security

Anything that could steer `lokf-curator` or edit the bundle could forge "confirmed by a person", since `lokf validate` passes a well-formed `human:<id>`.

- **`knowledge-registrar.yaml` gains a `provenance` job**: each `human:` actor that a pull request adds needs an approving review from that account, or their signature on the commit when they opened the pull request.
- **A solo maintainer signs commits**, as `references/automation.md` shows. A repository that cannot sign can add an optional `attestation` job, gated on a GitHub Environment's required reviewers. It never turns the check off, since such a reviewer may have opened the pull request.
- **`lokf-curator` takes identity from `gh api user` only**, never `git config user.name`. Its Step 2 refuses to run unattended, and Step 1 stays read-only.
- **`lokf-sidecar` and `lokf-curator` report whether commit signing is on**, and `lokf-curator` counts existing `human:` events *Not tied to a signed commit*, without touching `git config`.

### Fixed

- **`lokf-curator` and `README.md` say LOKF has 15 built-in classes, not 14**, adding `Role`.

### Added

- **`lokf-sidecar` Step 2 also creates a `knowledge_bundle` symlink to `.lokf/knowledge`** for folder pickers that hide dot-folders, such as Obsidian's. `templates/gitignore` excludes `.obsidian/`, and the lint and link checks skip the linked files.

## [0.13.0] - 2026-09-10

- **The librarian's SKILL.md and `.lokf/README.md` forbid a spaced dash that wrapping moves to the start of a line**, where Markdown reads a list item (`MD032`).
- **`.markdownlint-cli2.jsonc` turns off `MD060`**, which flags this repository's table style whatever its `style` setting.

## [0.12.0] - 2026-09-10

### Changed

- **The `knowledge-validate.yaml` CI gate and its template are renamed `knowledge-registrar.yaml`**, after the registrar role: it keeps bundle records well-formed and never judges whether their content is true. A repository with the old filename keeps working until it scaffolds again or renames the file.

### Fixed

- **Each `SKILL.md` declares `license: Apache-2.0`**, so `gh skill publish` no longer warns that the field is missing.

## [0.11.0] - 2026-09-10

### Security

- **The `knowledge-librarian` workflow runs `bash .lokf/scripts/knowledge-librarian.sh`, not a command from a repository variable**, so a change to what runs goes through code review.
- **The `knowledge-librarian` workflow splits into two jobs**, so a compromised agent cannot reach a write-scoped credential. The agent runs in a `contents: read` job and passes a patch artifact to a job that runs no agent code, the only one with `contents: write` and `pull-requests: write`. Top-level workflow permissions default to none.
- **The `knowledge-librarian.sh` wrapper quotes `AGENT_CLI` as an argument array**, and fails if the agent changed a path outside `.lokf/knowledge/` other than `.lokf/feedback.md`.

### Changed

- **A host turns on the scheduled librarian run with the `KNOWLEDGE_LIBRARIAN_ENABLED` repository variable set to `true`**, in place of `KNOWLEDGE_LIBRARIAN_CMD`, and `AGENT_CLI` is unchanged.

## [0.9.0] - 2026-09-09

Initial release: four [Agent Skills](https://agentskills.io/home) that turn a repository's scattered knowledge into a [LOKF](https://lokf.nolan-nichols.com/) knowledge bundle that is kept current and reviewed by a person.

- **`lokf-sidecar` installs a `.lokf/` sidecar from bundled templates** in a repository that has none.
- **`lokf-librarian` derives concepts, their sources and typed relationships from the repository**, audits the bundle against the LOKF schema and hands it off for review, on a schedule too. It deals in facts, never in verdicts about truth.
- **`lokf-curator` assists a human curator** with a trust and freshness report, and a review session that records a person's verdict in the bundle's frontmatter: confirm, correct, retire or send back.
- **`lokf-docent` answers a reader from the bundle first**, with each concept's trust label, checks exact values at the source, and records a gap in `.lokf/feedback.md` for the librarian. [`docs/examples/docent.md`](docs/examples/docent.md) has real transcripts.

This repository uses its own skills: its `.lokf/` bundle describes the four skills, its governance and its CI.
