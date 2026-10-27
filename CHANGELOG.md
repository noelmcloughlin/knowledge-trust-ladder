# Changelog

All notable changes to this repository are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows the rules in [docs/releasing.md](docs/releasing.md). All skills release together under one tag.

## [Unreleased]

### Added

- **A ktl-website home page offers a Schema button when the site shows a LinkML schema's pages.**

## [0.56.3] - 2026-10-27

### Fixed

- **A `!` after the type releases a major version.** `.releaserc.json` names the Conventional Commits preset, so a `feat!:` commit no longer releases nothing, as `docs/releasing.md` already said.
- **The preflight warns when git is too old for an ingest `git` entry**, and names each entry a run would refuse.

### Security

- **The ingest holds a `git` entry that names a host to the addresses its check found, and follows no redirect for it**, so DNS rebinding cannot reach a private address through git unless a proxy resolves the name. Without `allow_private_addresses` such an entry needs git 2.37 or later, and a host name outside ASCII is refused: write its `xn--` form.
- **The ingest and the federation build count every address that is not global as private.** Python's `is_private` leaves out the shared address space, 100.64.0.0/10, which holds Alibaba Cloud's metadata service and Tailscale's networks.
- **The ingest refuses a `git` entry whose address git's own configuration rewrites** with `url.<base>.insteadOf`, since the address check and the credential cover only the address the manifest names.

## [0.56.2] - 2026-10-27

### Fixed

- **The curator's report ends with its stop.** When the review session will not run, the report's last line says so, gives the reason, and names what changes it. A harness line saying the person cannot answer no longer stops the session on its own: the curator says it and goes on only when the person replies, one item per turn.
- **The federation's members script moves the day of a pruned release.** When the release list no longer holds a member's old release, the day the text writes right after the old tag moves with the tag, and only there.
- **The federation's members script follows a member's moved namespace.** When a new release's `index.md`, or a served file's `@base`, names another `base_iri`, the patch sets it and the question says so. The build refused such a member before. A namespace the build would refuse leaves the member as it is.
- **The federation's members script cuts a long hand-off line.** The pen refuses a patch with a hand-off line over 300 characters, and the line for a failed attestation or a moved namespace could be that long.
- **A federation build finds a waiting member by the namespace it builds.** The lock's waiting entry named the namespace a move proposes, so the entry of a member held or left out at its old namespace was not updated.
- **The federation build and members script remove the files they download.** Each zip, schema or served file fetched to check its digest and attestation is downloaded to a temporary folder, which is removed when the run ends, unless `--cache` names a folder to keep the files in.

## [0.56.1] - 2026-10-26

### Changed

- **`docs/three-lines.md` holds the model's critics.** `docs/three-lines-critics.md` is folded into it, and the docs pages' titles are shorter.
- **The workflows run the `just` that `.lokf/uv.lock` pins, checked by hash.** The sidecar's `pyproject.toml` names `rust-just==1.47.0`. A host without it still gets that version by name, and the preflight says to run `uv add rust-just==1.47.0` in `.lokf/`.

### Fixed

- **ktl-website builds for an owner spelt with capitals.** `SITE`'s host is lowercased, as Astro writes it, so the link check no longer reports every social card broken.
- **ktl-website's cards show a concept's genre.** The concept card and the link preview give the genre beside the type, the social card gives both, and search gains a Genre filter.
- **ktl-website words a type as the bundle spells it.** A word the bundle's prose writes with capitals keeps them, so `SlsaSourceControlSystem` reads "SLSA source control system" on every card and in relation names.
- **ktl-website's card head names a field once.** The genre stands after a lower-case "genre" key, and a genre that repeats the type is left off the card, the link preview and the social card.
- **ktl-website's card head reads the same on every concept.** The genre stands beside the type as a plain tag, without the lower-case "genre" key, as the link preview and the social card give it.
- **ktl-website reloads a page kept from before a deploy.** A page whose stylesheet the deploy removed reloads once and shows styled, instead of unstyled for up to ten minutes.
- **The federation build and the ingest check the address each connection opens.** A name that answers a public address to the check and a private one to the connection (DNS rebinding) now reaches nothing, unless private addresses are allowed.
- **CI lints the ingest workflow template.** actionlint now names `knowledge-ingest.yaml` with the other templates.

## [0.56.0] - 2026-10-24

### Added

- **ktl-website keeps old addresses and leaves a folder out.** `REDIRECTS` redirects an old address, such as a retired mkdocs site's `/elements/<Term>/`, to its page, and `DOCS.exclude` keeps a path such as `templates-linkml/` off the site.

### Fixed

- **A link to a docs folder's `index.md` reaches its page**, which Starlight serves at the folder's address, and that page comes first in the Guide, as its Overview.

## [0.55.2] - 2026-10-22

### Fixed

- **The preflight asks the package index uv reads**, a company mirror included, and prints only its host name. It warns when `.lokf/uv.lock` was made against another index, since `uv sync --locked` then fails and `uv sync` rewrites the lock.
- **The sidecar's portability page says what a mirror does to the lock**, and how a proxy that inspects TLS gets its certificate trusted by uv.

## [0.55.1] - 2026-10-22

### Fixed

- **A sync reaches a host with a website again.** Since 0.53.0 it stopped at `src/pages/og/[...route].ts`, because its website step refused square brackets in a path; it now allows the same characters as `--apply`.
- **ktl-prose reads every file in scope, the ones its script cleared too.** Its rules now name the dead sentence, a quantity no source gives, and "either way" with no alternatives named.
- **ktl-curator commits a verdict apart from the change it confirms**, as conventions rule 14 checks.
- **ktl-librarian's domain-schema page brings a published vocabulary in with `lokf adapt`.**
- **The website template takes Astro 7.4.0** and the patch releases of its plugins.

## [0.55.0] - 2026-10-20

### Added

- **The pen checks the schema before it writes.** `knowledge-apply.sh` runs `lokf validate` on every concept a patch would write, with `--dry-run` too, when `.lokf/.venv` holds the toolkit.
- **The preflight warns about a python3 older than 3.9**, about being run from ktl-sidecar's own folder, and names KTL skills installed for one user.
- **ktl-prose's check reads a script's comments.** Given a shell, Python, YAML or TOML file or a justfile, `prose-check.py` holds each `#` comment block, and each Python docstring, to the rules a paragraph keeps.

### Changed

- **The check reports a paragraph of more than eight sentences**, and lists "outright" and "at all" among the words to cut. The rules page gains a method for a paragraph with two topics, the rule before its exception, pointing words as names, and the quiet figures of motion.

### Fixed

- **The sidecar's scripts run behind a package mirror.** The pen, the conventions check and the ingest try `.lokf/.venv` first and `uv run` after it, because `uv run` fails behind a mirror that serves no upload times. No script picks a Python older than 3.9.
- **When its runner cannot start, the conventions check says so and exits 2**, instead of reporting findings against the bundle.
- **A freshly installed skeleton passes its own conventions:** the dummy services' descriptions match their index bullets.
- **ktl-prose runs its check through `uv run`**, so an old `python3` never runs it.
- **ktl-sidecar's Step 0 runs the preflight from the host repository's root.**
- **The librarian's audit lints the files it touched**, not `.lokf/.venv/`.
- **A release attaches a linkml-sidecar host's schema.** The `schema :=` line may name any file in the repository, and the released copy imports LOKF core as `lokf`, so a domain can resolve that import.
- **ktl-prose's check reads a comment's layout.** A table of options is read row by row, and a usage line or a command under a colon is not read, so neither is reported as one long sentence. `--against` compares a script as its comments.
- **The check reports fewer false findings.** A sentence may start with a lowercase name such as `ktl-docent` or `.lokf/`, and a minus, a `-- <args>` marker, "at all of" and "at all times" are no longer reported.

## [0.54.0] - 2026-10-20

### Changed

- **The graph page keeps the graph at full height in full screen.** Search and filters move into a side panel that scrolls, and switching between *This bundle* and *The workspace* draws the other graph in place, so full screen stays on.
- **The graph's filters read as controls.** Larger rows, a count on each entry, *All* and *None* on each group, and an "N of M concepts shown" line whenever a filter is off; every filter still starts on.

## [0.53.0] - 2026-10-19

### Added

- **The workspace counts the links between its members.** The lock, the workspace index and `queries/links.rq` count the typed relations in one bundle whose target is a concept of another, by slot.
- **The workspace carries `graph.json`**, every bundle's concepts and typed relations as cytoscape.js elements. Each node names its bundle, and the links between bundles are marked.
- **The MCP server loads a member's graph when a walk first reaches it**, as section 11.4 of the LOKF specification has members load, and a SPARQL query loads them all. The lock's `graphs` (format 4) says where each graph lies in `graph.nq`, with its digest, the namespaces it names and the IRIs it shares with another graph.
- **The federation build has the `sensitivity` gate of LOKF section 11.5.** A member concept says `public`, `internal` or `confidential`: an internal member joins once a person confirms `sensitivity: internal` on the Domain concept, and only in a private or internal repository, a confidential one never, and the workflow keeps an internal workspace off the site.
- **A bundle that releases no zip joins by the `concepts.jsonld` its site serves**, pinned by that file's checksum; the build writes the file out as the bundle. The members script asks for it with a conditional request and proposes a changed file, and `members --add <address>` drafts such a member.
- **A member whose file cannot be fetched is held at its last good state**, as section 11.5 of the LOKF specification has it, from the previous release's workspace that `--previous` names. A release zip with other bytes is held only at the release a build fetched before, a member never built is left out until it can be fetched, and a check holds nothing its pull request proposes.
- **The readers read a workspace where it lies:** a folder, a `workspace-<tag>.zip` in place, or the site that serves it, a graph at a time by range request. `read_document` reads the workspace's copy of a release, else its `concepts.jsonld`, else its source, as section 11.4 chains them.
- **A reader can be given some members alone.** `--member <slug>` on `mcp`, `serve` and `query` loads those bundles' graphs and no other, and refuses the stored queries that read the lock graph.
- **A domain host's release notes say what changed in its workspace.** `knowledge-federate.py diff` compares two workspaces, and the federation workflow adds the members that joined, moved or left, and the links between them, to each release's notes.
- **A domain host's graph page draws the workspace.** Its *The workspace* view draws every bundle the domain names, each in a colour and shape of its own, with the links between bundles dashed, from the `graph.json` the federation workflow serves. `WORKSPACE` in `site.config.mjs` turns the view on or off, and it is on when the repository has the workflow.

### Changed

- **`docs/federation.md` holds the whole federation design, and states each rule once.** Domains as manifests, LOKF section 11 and the release moved there from `docs/context-layer.md`, which keeps what a context layer is, the one-bundle table and what OKF leaves open.
- **The docs say the pen, its figure and the ingest's guards once.** The figure of who writes the bundle stays on `docs/architecture.md`, and `docs/for-the-curious.md`, `docs/ingest.md` and `docs/three-lines.md` link to the page that holds each detail instead of repeating it.
- **`docs/context-layer-technology.md` keeps to what KTL needs from a product.** The vendor tables of limits, plans and quotes are gone, and the page names the sidecar's own workspace server and MCP server beside the stores'.
- **`docs/for-the-curious.md` says how readers and verdicts steer the next run.** It now holds what KTL took from the WikiSkill and SkillWiki papers, so `docs/wikiskill.md` and `docs/skillwiki.md` are gone. The bundle's two concepts stay the record of each paper.
- **The federation build runs lokf in its own process.** It exported and validated each bundle through a new lokf process, which imported lokf and LinkML again every time. A build of ktl-federation's five members takes 4.5 seconds instead of 12, with the same output, and the federation tests run in half the time.
- **`SECURITY.md` and `docs/threat-model.md` say what holds after these fixes**, with a section on the website, and no longer claim the most a hostile release could do before review was propose a change.

### Fixed

- **The sync script no longer fails after a complete sync that replaces it with a longer copy.** Bash read on into the new copy and ran a line from its middle, so the run exited with an error and the sync workflow opened no pull request. The script now exits on the line that calls `main`, a v0.52.0 copy also stops when it syncs to this release, and `scripts/sync-sidecar.sh` runs each sibling's script from a copy.
- **A confidential ingest entry is refused where git could commit its copy.** The script checks that git ignores `.lokf/.cache/mirror/` and tracks nothing there before it fetches the entry.
- **The sync keeps a host's `.lokf/.gitignore` current.** A host kept the copy ktl-sidecar Step 1 first wrote, so it could lack the template's later lines, such as `.cache/`, where a confidential copy goes.
- **The scheduled librarian stops before any agent runs when git does not ignore `.agents/`.** It stopped only after the agent had run, at the write-scope check, with `?? .agents/`.
- **The federation gate refuses a link into a member's namespace that names no concept of that member**, as `--check-refs` refuses one inside a bundle, under the same `unowned_targets` policy. It checked only that some member owned the namespace.
- **The federation gate reads a reified `relations` entry as it reads the slot that entry names**, so a target no member owns there stops the build too. `links.rq` and `unowned.rq` count such entries as well.
- **The members script moves the other members when it cannot check one**, which the hand-off names. When the GitHub API refuses a release list as rate limited, gh asks again with the job's token.
- **The MCP server's `federated_sparql` stops reading at its limit**, 1000 rows or 2000 triples, and says when it cut an answer. It read a SELECT whole before cutting it, and returned a CONSTRUCT whole.
- **The workspace's stored queries take their predicates from the toolkit.** `unowned.rq` named `owl:sameAs` where lokf writes `schema:sameAs`, and left out `memberOf` and `holder`.
- **The graph page's details panel sets each label beside its value.** Starlight's spacing for page content put every label a line below it.
- **A member whose index gives its licence as text, such as `MIT`, no longer stops the domain build.** The lock graph keeps such a value as a literal, and the index writes it as text.
- **The MCP server reads a concept whose `id` lies outside its bundle's namespace**, which the registry routes through its `id_index`. It cut the IRI by the wrong prefix.
- **A member whose namespace nests with another's stops the build with a finding that names both**, before anything is fetched. The registry refused it only after every download, with a Python traceback.
- **A checksum must be `sha256:` and 64 hex digits.** Only its length was checked, so a path in it could reach outside the download cache and have the build delete a file there.
- **Every download stops at `--max-bytes`**, a member's schema and workspace as well as its zip, where each was read whole before its checksum was compared.
- **A download is tried again after a server error or a dropped connection, and follows a redirect only within http and https**, never from https to http and never from a public address to a private one.
- **A zip of more than 100,000 entries, or one that matches its checksum but cannot be read, stops the build with a finding**, where it filled the disk or ended in a traceback.
- **A reader keeps no partial answer to a range request as the whole file**, and `--previous` refuses a site address, from which no zip member could be held.
- **The federation workflow's weekly schedule no longer takes the place of a release build that waits for its turn**, and each job has a time limit.
- **A domain host's site serves each member's release inside the workspace.** The Pages upload left out the hidden `bundles/<slug>/.lokf/` folders, so every member link in the served workspace index answered 404.
- **The contract records every sibling host's links into this repository**, among them ktl-federation's into the federation page and the domain-bundle playbook. Its local cross-check reads all five hosts, and skips a domain host's ignored `snapshot/`, which holds a copy of this bundle.
- **The librarian keeps run accounts out of the source map.** No rule asked for one, yet each refresh had added its account to `playbooks/knowledge-sources.md`, 41 of them by 2026-10-19. The skill now says the map holds none.
- **An agent that applies its own patch no longer loses a scheduled run's work.** The wrapper sets `KNOWLEDGE_PEN_DRY_RUN_ONLY` for the agent, so the pen only checks the patch file there and leaves it for the wrapper to apply. The skill and the pen's dry-run line no longer tell a scheduled agent to apply and validate.

### Security

- **A release can no longer write a host's git configuration through the sync.** `knowledge-sync.sh` refuses a copy path inside a `.git` folder and clones the release without a checkout.
- **The branch the sync pushes carries no workflow a release wrote.** A workflow on a pushed branch runs with the repository's secrets, so `publish` applies the patch with `knowledge-sync.sh --apply`, keeps every workflow but for the pin, and holds the release's workflow changes for a person, or for a reviewer of the Environment `KNOWLEDGE_SYNC_REVIEW_ENVIRONMENT` names.
- **The sync's `publish` refuses a deletion, a link or an unusual mode, and leases its push** to the commit it read. A branch holding a person's commit is left alone with or without a pull request, and the report names a manifest rule the script does not know.
- **Each workflow reads its secrets from an Environment limited to the default branch:** `knowledge-librarian`, `knowledge-sync` and `knowledge-ingest`. Move every repository secret there on every host, as the sidecar's `references/automation.md` says.
- **A federation build refuses a member zip holding a hidden file or a file a browser runs, and a distribution name that is not one plain file name.** A `.git` folder in a zip, or a name that climbs out of the workspace, could run code in the build; the health line now runs git on no member's folder.
- **A federation build fetches members over http or https from public addresses only.** `--allow-local` allows local paths and private addresses, and a person's `private_addresses: allow` on the Domain concept allows a forge on the host's own network.
- **A member's attestation must come from its own release workflow**, or its federation workflow for a workspace, and a build without `gh` stops unless given `--no-attestation`.
- **The federation workflow hands its token to `gh` alone, and the website and federation builds run no npm install script.**
- **The website copies only files inside the repository, and passes raw HTML as GitHub renders a README.** A link out of the repository and an SVG holding a script are left out, other markup is shown as text, and Astro's telemetry is off.

## [0.52.0] - 2026-10-18

### Added

- **A member that waits in a member domain joins at the release that domain built.** The members script now names a member domain's released `workspace-<tag>.zip` and its checksum in the `MemberDomain` concept. The build then takes such a member at the release the lock inside that zip records, and the lock names each member concept (format 3). A member names the files of one release, and the build refuses a schema or workspace from another.
- **`knowledge-report.sh coverage --why <path>` names the concept that claims a file**, directly or through a folder above it, so a reviewer can find the row of the source map that excludes it. It reads frontmatter only.
- **`coverage --strict` exits 1 when a tracked file is named by nobody.** It also fails on a folder that holds no tracked file, such as a mistyped one, and when it cannot count, so a check built on it never passes by default.

### Changed

- **`coverage` counts apart the files git would add.** A concept names only a path git tracks, so a new file shows with the advice to commit it, or to ignore it if it is runtime state. A tracked file deleted from the working tree no longer counts.

### Fixed

- **The federation check runs the gate as the next release build would.** `build --verify-only` stopped after the zips, so a pull request with a link into a namespace no member owns, or into a member no person had confirmed, passed and the release build after the merge failed. The check now exports, loads and gates the bundles without writing anything, names the members the next release would leave out, and runs on any change to the domain bundle.
- **`coverage .` lists every file nobody named, and a mistyped folder says git tracks nothing there.** Both printed "none", which read as fully covered. A flag `coverage` does not know is refused instead of being read as a folder.

## [0.51.0] - 2026-10-18

### Added

- **A person who sends back text they wrote can release it to the librarian.** ktl-curator then writes `process:ktl-curator` in `generated`, in a commit that person signs, so the librarian's next run rewrites the text from its sources instead of only adding a question.

### Fixed

- **`docs/three-lines.md` no longer lists the `lokf-registry` MCP server as a design.** `knowledge-federate.py mcp` serves it, as `docs/federation.md` says.
- **Conventions rule 2 holds every `at:` to one shape: UTC to the second, as `date -u +%Y-%m-%dT%H:%M:%SZ` writes it.** A time with a lower-case `t` or `z`, an offset or a fraction passed the gate. The report script, the federation build and the workspace's stored queries did not all read such a time the same way. A person's event that no script could read counted as confirming every later edit.

## [0.50.1] - 2026-10-18

### Fixed

- **The federation build leaves out a concept a curator retired.** A retired `Domain` concept no longer counts as a second top, and a retired member is neither built into the workspace nor moved by `members`. The curator's domain-bundle.md says how a member leaves.
- **The federation build takes each member as a person last confirmed it.** It built every member concept on the tag, so a merged move or a new member joined the workspace before anyone confirmed it, against the federation design. A moved member is now built at the newest release the default branch held confirmed, while that confirmation stands, and a member no person confirmed is left out. The lock and the workspace index list both as waiting.
- **The Domain concept's gate policy and depth count only as a person confirmed them.** An edit no person confirmed waits, and the defaults stand in until a first confirmation.
- **The gate names a member that waits.** A link into the namespace of a member left out for want of a confirmation is reported with that member, and an error about a release a person confirmed earlier says which newer one waits.
- **`members --add` quotes the description in the new member's own index.** It pasted the description after a colon, with no full stop when the description had none, so the next sentence ran on.
- **The sync calls a copy a pin bump only when its `uses:` lines are all that differ.** It reported every copy the release changed as "differed only on its action pins", because under `pipefail` its test took `diff`'s exit status.

## [0.50.0] - 2026-10-18

### Added

- **The ingest restores a lost mirror file and prunes on a schedule.** A file the lock names and the disk has lost is fetched again and reported as restored. A scheduled run removes a gone or unlisted file no concept cites, once an earlier run recorded it so, and the preflight counts missing, stray and prunable files.
- **`docs/ingest.md` has a figure**, `.assets/ktl-ingest.svg` with its dark variant: the sources, the ingest, the review and the concept that cites the mirror.

### Removed

- **The figures nobody shows.** Every `-dimmed` figure, unreferenced since the dark theme moved to the `-dark` set, and both files of the lifecycle loop, which no page has shown since the README dropped it.

## [0.49.0] - 2026-10-18

### Added

- **The ingest mirrors knowledge from outside the repository.** `knowledge-ingest.py`, a new ktl-sidecar template with a shell half, reads `.lokf/ingest.yaml`, fetches the sources it names, converts each to Markdown and writes it under `.lokf/mirror/`, with `.lokf/ingest.lock.yaml` recording the version, the digest and the status of each. Four kinds: a Confluence selection, a list of addresses, a path in another repository at a ref, and a command the host committed. The librarian derives concepts from a mirror file as from any tracked file, so nothing in the trust ladder changes.
- **`knowledge-ingest.yaml` opens one pull request with what changed.** It runs the host's own script with the repository secrets whose names start `KNOWLEDGE_INGEST_` in a read-only job, and a separate job commits the mirror and the lock to the branch `knowledge-ingest`, refreshed until merged; `.github/PULL_REQUEST_TEMPLATE/knowledge-ingest.md` is the reviewer's checklist. `KNOWLEDGE_INGEST_ENABLED` turns it on.
- **`docs/ingest.md`** is the guide: the manifest, the mirror, the lock, the secrets, what the pull request shows and what the librarian does next. The preflight prints an `ingest` line, and `knowledge-report.sh coverage` counts the mirror's files.

### Changed

- **A domain concept is named for the domain, never for its position.** The curator's domain-bundle.md says so, its worked example names ktl-federation's `domains/ktl-federation`, and it says a confirmation stays with the concept's `id`.

## [0.48.0] - 2026-10-17

### Added

- **A domain may name domains, tier by tier.** `knowledge-federate.py build` follows a member whose released bundle is itself a domain as deep as the top `Domain` concept's `max_depth` allows, 3 unless set, and `domain.yaml` adds `max_depth` and a `MemberDomain` class so a manifest says which members are domains. The lock records each member's tier and every domain that named it, and the workspace index says who named each.
- **The diamond rule.** A bundle two domains name at the same release joins the workspace once, and the lock records both; at different releases the build stops, because one named graph holds one release. `members --add` drafts a `MemberDomain` when the release it admits is a domain.
- **`docs/federation.md` takes the federation's mechanics out of the context-layer page.** It holds the tiers of domains with the figure `ktl-federation-tiers.svg`, how the workspace stays current, what exists today and the decisions, two of them new: namespaces that mirror the tree, and what a member adds. `docs/context-layer.md` keeps the discourse, the one-bundle table and the design.
- **`knowledge-report.sh coverage` counts the tracked files no concept names.** Per top-level folder, the files under no path a concept names in its `resource` or `sources`, and the list under a folder you name: ktl-librarian's sweep for orphans as arithmetic, where a folder the source map names is accounted for and the map's row says why it is left out.

### Changed

- **The website's figures stay in the text column.** On a wide screen a diagram no longer grows into the main pane's spare width; a click opens it at full size. The change is in the template's `theme.css` and `Mermaid.astro`, so a host gets it with its next website repair.
- **The sidecar's pages name Codeberg beside GitLab, Forgejo and Gitea.** The install, signing, automation and scheduled-task pages point at the portability recipe for another forge, and the registrar template's header links the three-lines page through w3id.

### Fixed

- **Two tiers may each name a `members/<slug>.md`.** Each bundle keeps a folder of its own under `bundles/` and `export/`, and none can take the domain's own `domain` folder.

## [0.47.0] - 2026-10-17

### Added

- **A host keeps its sidecar current by itself.** `knowledge-sync.yaml`, a new ktl-sidecar template, reads the skills pin and the newest release each week. When the pin is behind, it runs the host's own `knowledge-sync.sh` in a read-only job and, in a separate job, opens one pull request from `.github/PULL_REQUEST_TEMPLATE/knowledge-sync.md` with the `KNOWLEDGE_SYNC_TOKEN` secret, or attaches the change to the run without it. The pull request stays one, refreshed to the newest release each week until it is merged. `publish.yml` asks the hosts named in `KNOWLEDGE_SYNC_HOSTS` to sync as soon as a release is tagged.
- **`knowledge-sync.sh` is the sync, as a sidecar script.** It copies a release's templates over a host's copies, moves the pin, writes the changelog entry under `## [Unreleased]` and `### Security`, runs the sidecar's checks, and takes the sync to a pull request with `--commit`, `--push` and `--pr`. Without `--source` it clones the tag.
- **`templates/knowledge-sync.manifest` lists what a sync keeps current.** Each template, its copy and the rule for it, in one list that the sync script, the preflight and contract check 11 read. So a release is data to a host's sync, and no code from it runs there.

### Changed

- **`scripts/sync-sidecar.sh` runs each sibling's own `knowledge-sync.sh`, or the tag's in a sibling that has none.** It takes `--commit`, `--push` and `--pr`, and `--finish <tag>` puts each sibling back on its default branch and removes a merged sync branch. The entry links the comparison between the two pins, so a sync that skipped releases points at all of them.

### Fixed

- **`knowledge-federate.py members` verifies attestations under the librarian wrapper.** The wrapper strips every token, so `gh attestation verify` failed; the script now takes the job's read-only token as `KNOWLEDGE_FEDERATE_TOKEN` (`AGENT_USE_JOB_TOKEN` `true`, `AGENT_API_KEY_ENV` set to that name), hands it to `gh` alone, and says which variables to set when it has no credential.
- **The sync writes the changelog entry instead of printing it with a hint.** The hint named `### Security` with a sentence's colon after it, and a heading typed that way once failed the lint.

## [0.46.0] - 2026-10-17

### Added

- **`knowledge-federate.py mcp` serves a workspace to agents.** It is the `lokf-registry` server the LOKF specification's section 11.4 describes, over the snapshot: `resolve_iri`, `neighbors`, `subgraph`, `federated_sparql` and `read_document`, each bounded in depth and size, with the workspace index as the server's instructions so an agent reads it first. `serve`, `query` and `mcp` take an absolute `--snapshot`, so an unpacked `workspace-<tag>.zip` is read anywhere a sidecar environment exists.
- **`knowledge-release.yaml` attaches the domain schema the justfile names.** `schema-<tag>-<name>.yaml` goes beside the bundle zip with its own `.sha256` and attestation, so a federation can validate the bundle on its own terms. `knowledge-federate.py` names it as a second distribution when a member moves, and the build validates that member against it instead of LOKF core alone.
- **`knowledge-federate.py members --add <owner>/<repo>` drafts a new member.** It verifies the repository's newest bundle release, reads the bundle's namespace and title from the zip, refuses a namespace that nests with a member's, and writes a `create` with a question for the pen.

### Changed

- **The sidecar's `llms.txt` and README aside no longer assume `npx skills` works.** The agent context offers the GitHub CLI route beside it and says when a company proxy blocks the other; the README aside points at the install page.

### Fixed

- **The workspace registry no longer names the runner's own folder as the domain's `source_base`.** The domain's entry now points at the host's repository at the tag, or at the served copy of the unpacked bundle, and the index names the address that is served (`.../workspace/index.md`) rather than a folder that answers 404.
- **`postcss-selector-parser` 7.1.6 in the website template's lockfile** (GHSA-rj75-hqrm-r3gf, quadratic selector parsing), and in this repository's own site.

## [0.45.1] - 2026-10-17

### Changed

- **`knowledge-apply.sh` indents a list under its key.** PyYAML put the dashes at the key's own column, which yamllint's default rules reject, so each concept the pen writes now takes the indented form.

### Fixed

- **`knowledge-apply.sh` lists a concept with no description by its link alone.** Its index bullets ended in a bare " - ", the separator for a description that was not there.
- **`knowledge-apply.sh` applies a `set` on a `rewrite` as it does on a `patch`.** It used to drop the key without a word while the dry run passed, and now every operation refuses a key it does not take, naming it.
- **`knowledge-federate.py members` moves a member's text with its version.** The patch now moves the old tag, zip name and release day in the description and body too, calls a member "confirmed" only when a person confirmed it as it stands, and `--dry-run` prints the patch even while a librarian pull request is open.
- **`knowledge-apply.sh` writes a log line once, however many operations give it.** A patch can also carry one `log` line for every operation that gives none, so a change made to many concepts no longer leaves one identical bullet for each.
- **`knowledge-apply.sh` writes a bare web address in a log line or an open question as an autolink.** ai-linkmo's markdownlint refused the bare addresses a question carried into the concept and `log.md`.
- **The sidecar's `.lokf/.gitignore` leaves out `.cache/`.** A domain host's federation build keeps the members' release zips there, and the first domain host committed four of them.

## [0.45.0] - 2026-10-16

### Changed

- **A skill page's word budget no longer counts table pipes or separator rows.** A table is the densest way to state a vocabulary, and a plain word count taxed it hardest. The budgets are unchanged.
- **A confirmed concept that a question put back to draft reads "reopened", not "still a draft".** `knowledge-report.sh` keeps the rung a person's confirmation earned and adds a flag naming the day, the asker and how many questions wait; the health line counts those under *Reopened*. The curator's and docent's tables, the SPARQL page, the ladder figure and the website's card say the same, and the card now shows the open questions beside the label.

### Fixed

- **`scripts/sync-sidecar.sh` writes the sibling's changelog entry in full.** It names the copies the sync changed, or says the pin moved alone. It used to print a placeholder, which two plugins released unfilled.

- **The repository contract skips a sibling's website build output.** Its copies of the curator's pages quote two links inside folded YAML strings, which the check read as links ending in a backslash and failed on.
- **`scripts/sync-sidecar.sh` ends the entry with "No plugin change" only for an Obsidian plugin.** ai-linkmo and gist are not plugins, so their entries end with what changed.
- **`scripts/sync-sidecar.sh` keeps a host's own `schema :=` line in its justfile.** It copied the template's empty one, so a domain host's members were validated on LOKF core and failed.
- **`scripts/sync-sidecar.sh` reports a sibling whose bundle fails `lokf-check-refs`.** It printed lokf's verdict and still passed, because only the last check's status counted.

## [0.44.0] - 2026-10-16

### Added

- **Federation templates for a domain host.** ktl-sidecar gains `knowledge-federate.py`, `knowledge-federation.yaml` and `domain.yaml`, which build one workspace from the released bundles a domain names, with one named graph per bundle and a gate on links no member owns. The design is `docs/context-layer.md`, and the first host is `noelmcloughlin/ktl-federation`.

### Changed

- `docs/install.md`: one `gh skill install --all` line with `--agent`, the GitHub CLI 2.90.0 floor, and when `npx skills` fails behind a proxy. The contract keeps every tracked `SKILL.md` under `skills/ktl-*/`, so `--all` installs the ktl- skills only.

### Fixed

- **ktl-website's link check reads an address in a code span without its closing backtick.** A concept that named the site's address in backticks failed the build with a broken link in `llms.txt`.

## [0.43.1] - 2026-10-15

### Changed

- **The README links the website's pages.** The quick start, the architecture page and the shorter version open on `w3id.org/ktl` rather than as Markdown files on GitHub.

### Fixed

- **`scripts/sync-sidecar.sh` carries `.lokf/justfile`.** It keeps the sibling's first line, which names the host, so a recipe change such as the v0.38.0 `schema` variable reaches every sibling; check 11 holds this repository's copy to the template the same way.

## [0.43.0] - 2026-10-15

### Added

- **A ktl-website site serves the whole bundle as `llms-full.txt`.** Each concept's text follows its trust label, its type, its addresses and its sources, so a model that reads the file at once can tell a draft from a confirmed concept. The site's link check reads the text files too.
- **A ktl-website site offers the bundle log as an Atom feed, `knowledge/log.xml`.** Each day of the log is an entry, titled and categorised by the kinds of change it holds and dated from git, so a reader can follow the bundle without watching the repository.
- **A ktl-website concept page links the concept's history and names its licence.** The record links every commit to the concept's file up to the built one, and gives the bundle's licence, or the concept's own, which the page head names too. The overview page, the feed and the two text files name the bundle's licence by its short name.
- **A ktl-website concept page opens the knowledge graph on the concept.** The record and the neighbourhood map link `/graph/?concept=<id>`, which selects the concept and frames its neighbours, and the address follows the selected node, so a view can be shared.
- **A ktl-website page previews a concept link.** A link to a concept shows the concept's title, type, trust label and definition while the pointer or the keyboard focus rests on it, from `knowledge/previews.json`, which the sync writes; Escape dismisses it.
- **A ktl-website site serves each docs page as Markdown beside it.** The home page and the extra pages too, at the page's path with `.md` added and every link a full address, so `llms.txt` sends a model to the words rather than the HTML.
- **A ktl-website release page links the repository, the docs and the bundle as they stood at the release.** The links go to the release's tag on GitHub, named by the new `RELEASE_TAG` option, and to the release itself.
- **A ktl-website page and its retelling offer each other as reading levels.** A `PAGES` entry's `retells` names the page it retells, and in the bundle a concept with an `audience` field or an `audience-` tag retells the concept its `derivedFrom` names; both pages open with a Reading level line.

### Changed

- **GitHub's dark theme shows the `-dark` figures.** Every `<picture>` dark source in the README and the docs pages names the `-dark` set, which the site already showed, so a figure is the same on GitHub and on the site. The sync no longer swaps a `-dimmed` source for its `-dark` neighbour; the `-dimmed` set stays in `.assets/`, unreferenced.

### Fixed

- **The ktl-website graph explorer fits the graph to its stage once the layout settles.** The re-fit waited for an event that had already fired, so it never ran.

## [0.42.0] - 2026-10-14

### Changed

- **The README, the architecture page and the plugin's homepage link to the site at `https://w3id.org/ktl/`.** The persistent address redirects to the GitHub Pages site.
- **The README lists Exhibitions, the sites that show a repository's collection.** It names this repository's own bundle and AI-LinkMO's.
- **The bundle's `base_iri` is `https://w3id.org/ktl/knowledge/`.** It replaces the `knowledge-trust-ladder.example` placeholder, so every concept's IRI resolves to its page, its JSON-LD or its Markdown file.
- **A ktl-website data page opens Datasette Lite in a new tab.** The site stays open while Datasette Lite downloads Datasette and the database.

### Fixed

- **`sync-sidecar.sh` sets its next steps apart.** A blank line now comes before the changelog entry to add and before the commit commands, so each step reads on its own.
- **A move of the bundle's `base_iri` no longer reads as an edit of every confirmed concept.** Conventions rule 13 compares each id and relation target by its path under the base each commit held, so the migration ktl-librarian's Rule 2 describes keeps every confirmation.
- **A release's changelog lists each entry once.** A pull request stacked on another still carries the other's entries under Unreleased, and the promotion no longer folds them into the pending section a second time.

## [0.41.0] - 2026-10-14

### Added

- **A ktl-website site shows a LinkML schema's pages under a Schema topic.** `SCHEMA` renders the pages `gen-doc` writes, found through a `gen-doc` recipe by default and built by the sync when missing. A mermaid diagram on any page is drawn in the browser.
- **A ktl-website site can serve the data as SQLite databases to open in Datasette Lite.** `BROWSE` names their folder and the command that builds it, and stays off until set, since the databases go on the public site. Their Datasette metadata is published without its `plugins` settings.

### Changed

- **The knowledge website workflow also runs weekly, and on a change to a justfile, a `pyproject.toml` or a `uv.lock`.** A schema or data change it cannot see, and a promoted changelog, reach the site within a week.

## [0.40.0] - 2026-10-14

### Added

- **A ktl-website home page offers an Architecture button when the docs have an architecture page.** The default buttons are now Browse the bundle, Architecture when `docs/architecture.md` is on the site, Bundle health and Knowledge graph.
- **The scheduled librarian takes an agent that wants its prompt somewhere other than after `-p`.** The repository variable `AGENT_PROMPT_FLAG` names the flag, or `arg` for an agent such as Codex CLI that takes the prompt as its last argument. The sidecar's automation page now states the five conditions any agent must meet, beside the Copilot CLI and Claude Code commands it vouches for.

### Changed

- **A ktl-website site shows the Knowledge Trust Ladder logo unless its configuration names another.** `LOGO` now defaults to `"auto"`, which takes a `knowledge-trust-ladder-logo.svg` the repository already has, or else the light and dark copies the template now carries. `null` still shows the title as text.
- **The README and docs pages lose their dead sentences.** The install, Obsidian, Copilot and releasing pages say the step and stop, and the Obsidian page names the `knowledge_bundle` doorway once instead of narrating the link. No skill change.

### Fixed

- **`sync-sidecar.sh` writes each sibling's sync on a branch of its own.** It starts `sync-<tag>` from the sibling's default branch as origin has it, skips a sibling with uncommitted changes, and names the files to stage, so the diff is never left on `main` or inside a feature branch.
- **The scheduled librarian writes its patch with the agent's own file tool.** The wrapper's prompt now says so. An agent that tried a shell write first was denied and gave up without writing the patch. The documented Claude Code command drops `Write(.lokf/patch.yaml)`, which Claude Code ignores; `Edit(.lokf/patch.yaml)` already covers the Write tool.

## [0.39.0] - 2026-10-13

### Added

- **ktl-website lays a website down for any repository's knowledge bundle.** The skill copies the site from its templates into `website/`: a page per concept with its trust label, a health page, the knowledge graph, search by trust and type, and the four `lokf export` files served beside the pages, with the README, the docs and the changelog when the repository has them. Its workflow, `knowledge-website.yaml`, builds the site on every pull request and publishes to GitHub Pages once `KNOWLEDGE_WEBSITE_ENABLED` is `true`. This repository's own site is the template's first copy, which the contract holds byte-identical, and a smoke test builds the template on the sidecar's dummy bundle.

### Changed

- **The website reads the repository's values and options from `website/site.config.mjs`.** The README, the docs pages, the changelog, the figures and the logo are each optional there, so the same site builds for any repository with a knowledge bundle, and this repository's site is unchanged.
- **This repository's website workflow, `website.yml`, is a copy of the skill's template.** Its deploy now waits for the repository variable `KNOWLEDGE_WEBSITE_ENABLED` to be `true`.

### Fixed

- **A concept's source link keeps its leading dot.** A source such as `.github/workflows/validate.yml` linked `github/...` on GitHub, which is no file there; `.` and `./` still read as the whole repository.

## [0.38.2] - 2026-10-13

### Changed

- **The README is a doorway, in the style of LinkML's.** It keeps the poem and the opening paragraph, names LOKF and LinkML as inspirations beside the poem, and links the website, the quick start and the retelling for readers aged 13 to 18. The library, museum and roles story moved to `docs/architecture.md`, which leads the website's Architecture group, and the quick start moved to `docs/install.md`.
- **The retelling for readers aged 13 to 18 sits beside the page it retells.** `docs/architecture.en-simple.md` retells `docs/architecture.md`, which links it, and the website still serves it at `/simple/`.
- **The website's home page keeps four buttons**: Browse the bundle, Architecture, Glossary and Quick start. The site's header already links GitHub, and the context layer is in the Architecture group, which opens with the architecture page as its overview.

### Fixed

- **The pen adds its edited-since note to a log line once.** It now looks for the note whatever its case, so a log line that already carries it gets no second copy.

## [0.38.1] - 2026-10-13

### Added

- **A website in `website/`, built with Astro Starlight from the README, `docs/` and the bundle.** Each concept page shows its trust label, sources and typed relations beside its own Markdown and JSON-LD, and `website.yml` publishes `main` to GitHub Pages with the four files `lokf export` writes.

- **`docs/context-layer.md` places Knowledge Trust Ladder in the context-layer discourse.** It quotes the people building context layers, shows one bundle as one repository's layer, and sets out a design for federating bundles through domain manifests and a rebuilt workspace, drawn in two diagrams with the unshipped parts dashed. `docs/context-layer-technology.md` surveys the stores, catalogs, agent surfaces and artifact repositories it would plug into.

### Changed

- **The research pages are trimmed to what KTL took and what remains.** `docs/wikiskill.md` and `docs/skillwiki.md` keep the changes each paper led to and drop the part-by-part comparisons; `docs/skills-repositories.md`, `docs/context-layer.md` and `docs/context-layer-technology.md` lose the quotation surveys and keep the runs, the design, the status table and the decisions.

- **The README, the sidecar's README and ktl-librarian's Golden Rule 1 link OKF's specification in its own repository.** Google moved the Open Knowledge Format to `GoogleCloudPlatform/open-knowledge-format` and froze the copy under `knowledge-catalog/okf/`.
- **The website's home page highlights Browse the bundle.** It is now the first and primary button, and Quick start follows it as a secondary one.

## [0.38.0] - 2026-10-11

### Added

- **ktl-prose writes for younger readers.** `references/young-readers.md` gives two bands of age, 8 to 12 and 13 to 18, and a pass for dyslexic readers, with the limits of each. A text for a younger reader is a retelling in a new file, which ktl-librarian writes in the bundle and ktl-prose writes beside a file a person names; a pass for dyslexic readers is a rewording at tighter limits.
- **prose-check.py holds a page to a band of readers.** `--audience 8-12`, `13-18` or `dyslexia` sets the band's limits, counts the sentences in each paragraph, and notes the page's Automated Readability Index. A page that opens "This page is for readers aged 13 to 18." is held to that band with no flag.
- **A band of readers is spared Latin abbreviations, and told which words may be hard.** Under a band, prose-check.py reports `i.e.`, `vs`, `cf.`, `etc.` and `via`, and notes the words a page uses that the VOA Learning English word book does not hold. The word book is in the public domain and sits in the skill's `assets/` folder with its credit.
- **prose-check.py proves that a retelling adds nothing.** `--derived-from ADULT YOUNG` reports a number, link, code span, quotation, HTML tag or fenced block that the retelling holds and the text it retells does not, and notes what it left out. The retelling's first paragraph must link the original, and in a bundle `derivedFrom` must name the adult concept.
- **A README for readers aged 13 to 18.** `README.en-simple.md` retells the README in shorter sentences, `prose-check.py --derived-from` shows it adds nothing, and the README points to it.
- **A bundle can declare its younger readers.** The curation policy's optional `Younger readers:` line names a band of age, and `prose-check.py --bundle` reports it as `audience: 8-12`, or `audience: none declared`.
- **The librarian retells, and the docent answers, for younger readers.** ktl-librarian's `references/retellings.md` says how it writes and refreshes a retelling, and that a scheduled run retells only a confirmed concept, for a band the curation policy declares. ktl-docent and its Copilot copy prefer a retelling for a younger reader, or answer from the adult concept in shorter words, with every label kept. `docs/examples/prose.md` captures the README's retelling.

### Changed

- **The install commands install all five skills for your user.** Both READMEs open with a Quick start that holds every install command, the docent alone included; it installs the whole set with `--global`, `docs/install.md` passes `--global` and `--scope user`, and a new section there says when a team installs into the repository instead.
- **A domain schema is one variable in the sidecar's justfile.** The `lokf-validate` and `lokf-check-refs` recipes pass `schema := ""` as `--schema`, and the registrar, librarian and release workflows run those recipes, so a host wires a domain schema by setting that one line, by hand or through the linkml-sidecar skill.

### Fixed

- **A docs-only merge after a promotion no longer fails the release job.** The version semantic-release computes is already promoted and waits for `publish.yml`, so an empty Unreleased section passes and nothing is promoted twice. A failing check also writes its reason as a GitHub annotation.

## [0.37.1] - 2026-10-07

### Added

- **The schema is the source of the class list and of the relation fields.** Contract check 7c holds Rule 3's class list to the classes `lokf vocab --all --json` declares as types, at the lokf floor the templates pin, where check 7 compared two prose lists with each other. Check 7d holds the relation fields `knowledge-report.sh` counts reliance from to the slots the schema ranges over `Concept`. Both run the toolkit through `uvx` at the floor, so the comparison is against the schema a host installs.
- **ktl-sidecar's portability page says what is tested before a release, and what stays with the host.** The skills repository tests every template before a release, so a host whose copies are as the sidecar laid them down need not test them again. A copy the host edited, a port to another forge or shell, and another operating system stay the host's.

### Changed

- **ktl-docent follows all thirteen typed relations when it widens along the graph.** `sameAs`, `measures`, `memberOf` and `holder` join the list in its SKILL.md and in the Copilot instructions. A Metric now leads to what it measures, a Role to its organization and its holder, and a concept to one that says it is the same thing.

- **The behavioural tests of the sidecar scripts moved out of the repository contract into `tests/`, run with pytest.** `scripts/validate-repository.sh` held about 2,000 lines of them beside the checks on this repository's own files, each building a throwaway bundle or repository. Checks 8, 11 (its synthetic bundle), 11c, 12 (most of it), 12a, 13, 13a, 18 and 19 (most of each), 20, 20a and 22, and `scripts/test-sidecar-layouts.sh`, are now one module per script under `tests/`. The fixtures and the expected lines are the same. Each check's number stays in the contract with a line saying where it went, so a changelog entry or a bundle concept that names one still points somewhere. `validate.yml` runs the tests in a job of their own, with `just` installed for the lokf-link recipe's tests, and `publish.yml` runs them before a release. A test can be run alone, and the contract runs in seconds.

### Fixed

- **The report script counts reliance through `measures`, `memberOf` and `holder`.** The schema ranges the three over `Concept`, so a Metric relies on what it measures and a Role on its organization and its holder, but the count read ten fields and left them out. The three are in the list, in the template and in both copies, and ktl-curator's trust-fields.md names thirteen. The template changed, so the siblings take it at the next sync.

## [0.37.0] - 2026-10-07

### Added

- **ktl-librarian has a page for a host whose content is Agent Skills.** `references/agent-skills.md` says which skills are the host's own, and leaves out installed and vendored ones. It asks a person about a skill under `.claude/skills/` that shows no sign of another home, and gives a skill template no concept of its own. It says what a skill's concept holds, while the procedure stays in `SKILL.md`. A skill the repository deprecates stays a fact in the concept, apart from the curator's `status: deprecated`. A miss that a skill's own description should have prevented goes to the reviewer in a hand-off line, since only a person changes that description. The first run's sweep table names Agent Skills folders.
- **`docs/skills-repositories.md` says whether KTL helps a repository whose content is Agent Skills,** read through WikiSkill and SkillWiki. It reports this repository's own evidence, and a run of the sidecar, the librarian and the docent on `anthropics/skills` at commit `683bc88`. It ends with the designs that remain, among them a record of skill runs and a trigger test.

### Changed

- **The threat model names a skills repository.** There every source the librarian reads is a set of instructions for an agent. `docs/threat-model.md` says which guards still hold, and that only the person reviewing a pull request catches an instruction that shapes what a concept says.

## [0.36.1] - 2026-10-07

### Security

- **The provenance gate reads a `verified` or `generated` event that spans lines, so a forged confirmation cannot hide in a multi-line flow layout.** The hand-written readers in `knowledge-provenance.sh` and `knowledge-registrar.yaml`'s `provenance` job parsed a flow event only on one line. A `verified: [` or a `generated: {` continued on the next line is valid YAML every parser reads as a confirmation, but the gate saw no event and let an unsigned `human:` actor through, where `knowledge-report.sh` and the Obsidian plugins trusted it. Both readers now accumulate a flow event to its closing bracket. Checks 13a and 22 cover it.
- **The provenance gate reads a concept behind a byte order mark or in CRLF line endings, so a forged confirmation cannot hide behind one either.** The same two readers keyed on a bare `---` first line: a leading BOM (`\357\273\277`) or a `---\r` opener matched nothing, so the reader saw no frontmatter, read no events, and passed an unsigned `human:` event that every YAML parser strips the mark or the carriage return and reads. The readers now strip both before the opener, under `LC_ALL=C` so a gawk in a UTF-8 locale reads the three BOM bytes as bytes, not as one character the strip would miss. Conventions already strips a BOM in the shell, and silently strips CRLF, so the gate was the only guard against the CRLF form. Check 22 covers a BOM-prefixed and a CRLF forgery.
- **The unattended provenance check follows a renamed concept, so a person's text cannot be rewritten under a new name.** `knowledge-provenance.sh --unattended` read a rename as a delete and an add and compared each path with its copy at `HEAD`, so a concept a person authored, renamed and rewritten in one change had no `HEAD` copy at its new path and passed. The check now pairs a rename by git's own detection and compares the bodies. Verified against a rename-plus-rewrite and a rename-only control.
- **The pen refuses a provenance or event key in any case, and a top-level event field.** `create` and `set` denied `verified`, `status` and the rest only in lower case at the top level, so a `set` carrying `Verified:` or a top-level `by: human:` was written in, where the scheduled run's own backstop grep then refused the whole run. The pen now matches those keys case-insensitively and refuses a top-level `by`, `at` and `revision`. Check 19 covers it.
- **The pen protects a curator's send-back and will not glue a protected heading onto the line before it.** A `resolve` or `delete` could remove a `process:ktl-curator` note, the form a send-back takes when the curator could not sign in, and an edit ending exactly at `## Open questions` or the `lokf:related` marker merged that heading into the text. The pen now keeps such a note, and checks after each edit that a protected section is still there. Check 19 covers each.

### Added

- **Check 22 holds the gate's event reader to a real YAML parser.** It builds a human event in every layout a person might write (block, single-line and multi-line flow, a sequence, a mapping, an offset timestamp, an empty list, behind a byte order mark, and in CRLF line endings) and asserts the gate flags an unsigned one exactly when a parser sees one. So a layout one reader skips and the other reads cannot return as a way past the gate.

### Fixed

- **The report script reads every timestamp and event layout a YAML parser does.** `knowledge-report.sh` dropped a `+00:00` offset, so an edited concept read *confirmed by a person* and a confirmed one read *edited since*; dropped a multi-line `verified` list, so a confirmation read *nobody has checked*; counted an empty `verified: [ ]` as automation; and missed a concept behind a byte order mark. `norm()` now converts any offset across the day, month, year and leap years, and the reader accumulates a flow list or mapping and strips a BOM — byte-for-byte under `LC_ALL=C`, so a gawk in a UTF-8 locale reads the mark as bytes, not as a two-byte character it would leave in place. Check 20 covers each.
- **The report script counts an edited-since concept once, and reads a CRLF `index.md`, a successor-less retirement and a subfolder sidecar.** A concept edited after its confirmation whose source then moved was listed both on the work list and under *a source moved after that confirmation*; it now sits once on the work list, since the edit already overtook the confirmation. `base_iri` is read through a carriage return and a byte order mark, a retirement whose newest deprecation line names no successor reads as plain retired, and `changes` reads a subfolder sidecar from the work-tree top. Checks 20 and 20a cover each.
- **The pen keeps a null value, writes atomically, scrubs a log line and a question, and clears a `./`-led or `#fragment` index link on delete.** A `~`, `NULL` or empty value no longer flips to `null`. A write that fails partway leaves the bundle unchanged, each file staged beside its target and put in place only once all are written. A `log` line and a `question` are scrubbed by Unicode category, as the hand-off is. And `delete` now takes a link written with a `./` lead or a `#fragment` out of a list of links, or refuses a sentence that holds it, rather than leaving it to dangle. Check 19 covers each.
- **ktl-prose skips an indented code block, reads a prose line that opens with an inline HTML tag, keeps an inline tag and a hard line break, reads a marker only where it opens a block, and notes a change of a fifth either way.** An indented code block is code, so no style rule reads it. A prose line that opens with an inline tag is read with the tag masked, not skipped whole. A changed inline tag or a dropped hard line break is now reported, and a number that begins a wrapped line is checked as a fact, not a list number. The growth and shrink notes fire at a fifth, up or down, with no word floor. Check 18 covers each. (A rewording that swaps two facts from the same set is still passed by the token comparison and left to the reviewer, since the same comparison must pass a legitimate reordering of clauses.)
- **The registrar scopes rule 14 to the pull request's merge-base, the feedback script rejects a `.` path segment, and both read login characters the same in every locale.** The `validate` job passed `base.sha`, where `provenance` uses the merge-base, so a commit the base branch gained after the pull request opened could read as the pull request's; both now use the merge-base. `knowledge-feedback.sh --concept` rejected `..` but not `playbooks/./draft.md`, which the report then never matched. Both scripts' login checks now set `globasciiranges`, a no-op where the shell lacks it. Check 12a covers each.
- **Contract check 15 reads the pinned skill path from the commit the pin records, not only from the tag ref.** It used to skip when the tag was not on the clone, which on the scheduled, tag-less checkout was always; it now resolves the recorded commit and reads the path from it, and the tag-agreement half says whether that commit is a real object when the tag is absent. A fixture stages an untagged commit and reads the path from it.
- **The layout tests no longer flake on a SIGPIPE race, isolate their git config, and leave no temporary files behind.** A large `sed` piped into `grep -q`, which exits on its first match, could take SIGPIPE and fail the check under `pipefail`; the sections are captured first. The fixtures run under an isolated git config, so a global `commit.gpgsign=true` no longer signs them, and the extracted workflow steps write under the test's own working directory.

## [0.36.0] - 2026-10-06

### Added

- **Each skill's page has a word budget.** Contract check 10a holds every `SKILL.md` to one, set just above the page's size. An agent loads the whole page when the skill starts, and the Agent Skills specification recommends under 5,000 tokens for it. ktl-librarian's page, halved in 0.32.0, had taken back 328 words within two days. An edit that adds words to a page now moves as many into that skill's `references/`, and `docs/repository-layout.md` names the check where it gave token estimates.
- **The curator's queue comes from the script.** `knowledge-report.sh` reads every typed relation, in each spelling the format allows, and resolves its target as the KTL Curator plugin does. Its whole report prints how many other concepts rely on each concept, counting each citing concept once. It also prints the review dates due within 30 days, each confirmed concept derived from one edited after that confirmation, and *Worth ten minutes today*, ranked as `references/trust-fields.md` says. ktl-curator quotes that queue, where it used to count relations and sort them itself. Check 20a covers each spelling, a self-reference, a retired concept and a concept with no `id`.
- **A retired concept names what replaced it.** ktl-curator's *Retire* asks what replaced the concept, and its `**Deprecation**` line in `log.md` links the successor after "replaced by". `knowledge-report.sh labels` then reads *retired, replaced by* that path, from the newest such line, and only for a concept the bundle holds. ktl-docent, and its Microsoft 365 form, open the successor before falling back to the repository. LOKF has no typed relation for a successor yet, so the log holds the link, and [nicholsn/lokf#112](https://github.com/nicholsn/lokf/issues/112) asks for one.
- **A reader's disagreement shows on the concept.** `knowledge-feedback.sh --concept <path>` names the concept a Disagreement disputes, right after the kind. It accepts the path only with a Disagreement, only in the bundle's lowercase spelling, and only for a concept file that exists. Until the librarian handles the entry, `knowledge-report.sh labels` adds *a reader disputed this on* that day, and the whole report lists the concept. The report reads the path and never the entry's text. ktl-docent passes the path whenever a Disagreement is about one concept.
- **Conventions rule 14: a commit that records a person's confirmation changes the verdict, not what the concept says.** Rule 13 compares a confirmed concept with the commit that recorded the confirmation, so an edit made in that same commit read as confirmed, and only the person reviewing the pull request could catch it. With `--since <commit>`, `knowledge-conventions.sh` reads each commit after it against every parent, as the `provenance` job does. A commit that adds a person's event no parent holds may change the concept's claims only when `generated.by` names that person, the shape of *Correct now*. The registrar's `validate` job passes the pull request's base, and a scheduled run passes none, since a squash merge folds an edit and a later confirmation into one commit. Check 11c covers each case, a merge among them.
- **`docs/skillwiki.md` reads the SkillWiki paper (Huang et al., 2026) and its code against this design,** part by part: what KTL does with it, where the two designs differ, and what the paper does not settle. `docs/wikiskill.md` names the two papers apart, and the README credits SkillWiki.

### Fixed

- **ktl-curator's two pages ranked its queue differently.** `SKILL.md` put a confirmed concept whose source moved in the first group, and `references/trust-fields.md` left that case out. Both now give the order the script applies. The SPARQL query for the most relied-upon concepts counts each citing concept once, and never a concept for itself.

## [0.35.0] - 2026-10-06

### Changed

- **ktl-prose lays out what it rewords the way the file's project does.** In a bundle that is one line for each paragraph, as ktl-librarian writes it, where the skill used to keep a concept's old wrapping. Outside the bundle it keeps the host's layout, and `references/rules.md` sets out the three layouts in use, with the benefit and the cost of each.

## [0.34.2] - 2026-10-05

### Changed

- **The preflight reads the CI variables by indirect expansion, not `eval`**, so a scanner that searches for `eval` finds none. Its output is unchanged, in bash 3.2 too.
- **The preflight names who needs a missing `knowledge-feedback.sh` or `knowledge-report.sh`:** ktl-curator and an earlier ktl-docent, since the docent runs its own copies.

### Security

- **ktl-docent runs its own copies of `knowledge-report.sh` and `knowledge-feedback.sh`, never the repository's.** Anyone who can commit to a repository can change its `.lokf/scripts/`, so asking about a repository you had not reviewed ran its code. Check 11a holds the copies in `skills/ktl-docent/scripts/` byte-identical to the templates. The docent no longer runs the preflight: it reads a login from `gh` or `glab`. Without its scripts, it works out labels by hand, gives the reader the feedback line to file, and never writes `.lokf/feedback.md`. Its scanner note answers the Gen Agent Trust Hub audit of 2026-10-04.
- **ktl-docent puts the asker's login in an entry only when the asker agrees.** The scheduled workflow commits `.lokf/feedback.md`, often into a public pull request, and git history keeps the line after the librarian clears it.
- **ktl-docent and ktl-curator keep only the `username` from `glab api user`**, as the preflight did. Both gave the bare call as a login's source, and it prints the whole profile, email and linked accounts included.
- **ktl-librarian and ktl-sidecar read the no-Python schema from a commit, not a tag**, since a tag can be moved (Snyk W012). The URL names commit `66073c3`, tagged `v0.8.0`, whose `lokf.yaml` is byte-identical to the schema in the `lokf` 0.8.0 wheel that `.lokf/uv.lock` pins. Both skills say to read it as data, never instructions. Check 11b fails a tag or a branch in the URL, pages that pin different commits, and a page that does not name the floor's tag.

## [0.34.1] - 2026-10-05

### Changed

- **The Copilot docent's gap report gives the librarian what ktl-docent's does.** A Miss starts with the reader's question in quotes and says whether a concept looked relevant from `index.md` and did not answer, or nothing relevant was listed. A Disagreement says which version the answer gave. The skill also gives the source link when a question about the present rests only on an unchecked or edited concept, finds endpoints, versions and schemas as ktl-docent does, and takes `ktl-docent-m365` as its heading.

### Fixed

- **The Copilot docent labels a concept as `knowledge-report.sh labels` does.** Its rules reported every label that applied, most cautionary first, so a retired concept could also read as confirmed, and a concept edited after its confirmation could read as both. A retired concept now carries no other label, and *edited since a person last confirmed it* takes the place of *confirmed by a person*. *Still a draft* and then *past its review date* follow the first label, and a confirmation names the revision it was checked against. ktl-docent's `references/answering.md` gave the same rules for a sidecar with no script, and now matches the script too.
- **Every label table reads an empty `verified` list as *nobody has checked this yet*, as the report script does.** The tables in ktl-docent, the Copilot docent and ktl-curator's `references/trust-fields.md` called it *checked by automation only*.

## [0.34.0] - 2026-10-05

### Added

- **The librarian's pull request says how the conventions script ended.** The registrar's gate does not run on a pull request the workflow opens, so `refresh` runs `knowledge-conventions.sh` and the pull request reports the outcome beside the validation's. The pen keeps most conventions by itself. A `resource` that names no file and a `revision` that names no commit are the two only this script finds.
- **`knowledge-report.sh changes` says what a change does to each confirmed concept.** Each one it names is followed by *still reads as confirmed*, *reads as edited since that confirmation*, *removed* or *its confirmation is gone*. A check or a question on a confirmed concept was listed like an edit, so a reviewer could not tell which concepts lost their label.
- **ktl-prose rule 10 says where a text says a thing twice.** "own" after a possessive, "itself" after a noun and "at all" after a negative are cut where they draw no contrast. A fourth pass, over the bundles of the three sibling repositories, cut 58 of 84 and 33 of 43. It cleared 305 of the script's 312 findings, and the text grew by one word in a hundred.
- **`prose-check.py` counts the words before and after a rewording.** The `OK` line of a comparison gives both counts, so the hand-off quotes them. A day or a month written out that changed, and a text cut by more than a fifth, are notes for the reader.
- **A scheduled librarian run opens no second pull request beside an open one.** `knowledge-librarian.yaml` has a third job, `earlier`, which lists the pull requests the workflow opened, under a token that reads pull requests and nothing else. While one is open, a scheduled run stops before the agent. A week's pull request left unreviewed was joined by another each Monday, each from the same default branch. A run a person starts goes ahead, and its pull request names the open one.
- **What a person declined is not proposed again.** A pull request of the workflow's that a person closed without merging left nothing the next run could read, so the same change came back. `earlier` now hands a scheduled run a record of each: its base commit, the concepts it touched or added, and a hash of each feedback entry it handled. `knowledge-report.sh quiet` counts none of that as work, and the work list names it under *Declined*. Each item makes work again once it changes after that pull request. A run a person starts reads no record, so starting one asks the librarian to try again.
- **The preflight warns when git holds no `.lokf/uv.lock`** on a host that carries the registrar workflow, since the gate now installs from that lock.

### Changed

- **The pen refuses a patch that handles more than ten reader entries.** ktl-librarian stated that limit for a run, and nothing held a run to it.
- **The registrar's gate and the release workflow install the toolkit with `uv sync --locked`**, as the librarian workflow did. A host whose `.lokf/uv.lock` is missing from git, or behind `.lokf/pyproject.toml`, now fails at the install step: run `uv lock` in `.lokf/` and commit the file.

### Fixed

- **The pen writes a value back as the file held it.** It read each concept's frontmatter into YAML's types and wrote the whole block back, so `1.10` became `1.1`, `12:30:00` became `45000` and `yes` became `true` in any concept it touched. On a person's event an unquoted `at` came back in another shape and an all-digit `revision` as another number. The gate read that event as changed, and the report script lost the confirmation's date. The pen also refused an all-digit commit hash given as `revision`.
- **The retrieval score leaves out a question whose concept has left the bundle.** No index could lead to such a concept, so the question counted as a miss on every run. It is not asked now, and the score says how many were left out.
- **Conventions rule 10 reports a comment beside `id`, `by`, `at` or `revision`.** A parser drops the comment and a line reader takes it for part of the value. The gate then read an actor nobody is, and the report script could not read the time, so the concept never read as edited since.
- **`docs/wikiskill.md` said the paper's wiki keeps every trace.** Its raw layer keeps them, and the wiki's log names the errors that came back.
- **A week is quiet again once the librarian has asked about a source it cannot act on.** A confirmed concept whose source is deleted is the curator's to retire, so the librarian can only add a question, and a question moves no stamp. `knowledge-report.sh quiet` kept counting that source, and an agent ran every week until the curator acted. A moved source no longer counts once an open question of the librarian's that names it was committed no earlier than the source's last change, and the work list names it apart. It counts again when the source changes after the question.

### Security

- **A person's record is the same after the pen writes as before.** The pen compares each concept it is about to write with the file it read, and refuses the patch when a `human:` event or a person's note would differ. Three patches passed its per-operation checks before: a `rewrite` whose body brought its own `## Open questions` section, a note in a person's name spelt with an escaped line break, and a `delete` behind a second heading placed above the real one. `knowledge-provenance.sh --unattended` refused each in a scheduled run, and nothing did in a live session. Check 19 exercises them.
- **A reader's question and the hand-off hold no character a reader cannot see, whichever block it sits in.** The pen and `publish` listed ranges, which left out the Arabic letter mark, the soft hyphen and the tag characters, which hide text from a reader and not from a model. The pen cleaned a reader's question of control characters only. Both now go by Unicode category, as check 21 and `prose-check.py` do.
- **The hand-off a reviewer reads is the pen's, after the retrieval call too.** That call carries readers' words in its prompt and runs after the pen has written the hand-off, whose path it could write. The wrapper writes the pen's lines there again once the call returns.
- **A reply cannot add to what it is scored against.** The retrieval scorer read the expected concepts and the reply from one stream. A reply that held lines in the scorer's own shape raised both counts.
- **The skill a scheduled run installs is pinned to a commit.** The librarian workflow named a release tag, and a tag can be moved to other instructions, which an agent would then follow unattended. `TRUST_LADDER_SKILLS_SHA` now holds the commit that tag named when the pin was set, and the install step installs nothing unless the tag still names it. The release step and `scripts/sync-sidecar.sh` move the two together, and check 15 holds the template's commit to its tag.
- **The conventions script and the pen pin PyYAML.** Each ran through `uv run` with a bare `pyyaml` in its dependency block, so the gate and the scheduled run installed whichever release was newest that day. The block now names one release, and `exclude-newer` takes no file uploaded after a set date.

## [0.33.0] - 2026-10-04

### Added

- **The README shows who writes the bundle and what checks it.** The diagram that `docs/for-the-curious.md` added in 0.31.0, `.assets/ktl-architecture.svg`, replaces the README's lifecycle diagram, since the opening card already shows the order the roles first run in and the loop back to the librarian. Its headings now say what happens: *each in one way only* and *what is written*, where they said *each through one door* and *what lands*.
- **The README says what a docent, a registrar, an accession and the sidecar are where it first names each, and links the bundle's glossary.** A docent is a museum's name for a guide, and the README pointer that ktl-sidecar installs says so too. A registrar is the person in a museum who keeps the collection's records, and an accession is an item added to the collection. The sidecar is `.lokf/`, a folder beside the code and kept out of the project's build. The glossary now defines all four, and *desk*, the README's word for the place where a role does its work.
- **ktl-prose keeps one topic to a paragraph, and says what happens in plain words.** Rule 3 now covers the paragraph: split one that runs past 150 words where its topic turns, the limit the Federal Plain Language Guidelines give. `prose-check.py` reports it as `paragraph`, and never counts a table cell. Rule 9 now asks for the literal verb: a key is "added", not "landed", and an IRI is "built", not "minted". The script reports seven such figures under `words`, and the rules page lists the rest with their plain words. A word of the analogy a project names its roles by, such as the librarian's *desk*, stands once the project's glossary defines it. ktl-librarian's rules for a concept body say the same.
- **`prose-check.py` reports a character no reader sees, as `unseen`.** That is a control character other than a tab, or a format character such as a zero-width space, a byte order mark or the right-to-left override the "Trojan Source" attack hides code behind. An agent that types such a character's escape into a tool call can write the character itself. The script reports each line that holds one, code and frontmatter included, and its comparison refuses a rewording that adds one. Check 18 exercises both.

### Changed

- **In a live session, ktl-librarian opens its pull request only when the person says so.** The person who started it is the change's author and submits it, as the AI covenant says. A scheduled run's workflow still opens its own. ktl-curator's review session ends the same way.
- **The docs, the skill pages and the script comments read plainer.** A third pass replaced figures of speech, such as "lands", "mints", "ships", "arms", "wires" and "lays down", with what happens. It split every paragraph and comment block past 150 words, and took the dashes and long sentences out of the script comments, which no pass had read before. No fact changed. The captured docent answers, the released changelog entries and the messages the scripts print stay as they were.

### Security

- **The contract fails on a character a reader cannot see in any tracked file.** Check 21 searches every tracked text file for a control character other than a tab, and for a format character such as a zero-width space, a byte order mark or a right-to-left override. A diff shows none of them, and GitHub warns of only some. Typed escapes once put three of them into a sanitizer here, as the characters themselves, and only a search by hand found them. Code that needs one spells it as an escape.

## [0.32.0] - 2026-10-04

### Added

- **A scheduled week with nothing waiting for the librarian runs no agent.** `knowledge-report.sh quiet` exits 0 when no source moved since its concept's stamp, no person left a note since the librarian last stamped that concept, every concept carries a stamp, and no reader feedback waits. The wrapper asks it before a scheduled run, which `KNOWLEDGE_SKIP_QUIET` allows, and calls no agent when the answer is quiet. A scheduled run in a month's first seven days goes ahead regardless, since the work list never fetches a source given as a URL. So does a run a person starts. Check 20 and the layout tests exercise it.
- **The librarian's hand-off reaches its pull request.** The patch file may carry `handoff`, up to ten lines for the reviewer in the agent's own words, such as a send-back that came up twice or a source that did not answer. The pen holds each to one line of printable text with no backtick, and writes none of it to the bundle. `publish` cleans the lines again and shows them under *From the librarian*, in a code block, where nothing renders. A scheduled run's hand-off stayed in the job log until now.
- **Conventions rule 13: a confirmed concept still says what its person confirmed.** After the commit that recorded the latest confirmation, a change to the concept's body or claims must move `generated.at` past it, so the concept reads *edited since*. The pen always restamped, and the gate now fails a hand edit that does not. The rule compares parsed values, so a requoted value is no change, and it leaves out the open questions, KTL Registrar's block and the trust fields. It can miss an edit, and never flags a concept its person saw. Check 11 exercises it.

### Changed

- **ktl-librarian's page is half as long, about 3,700 words where it had 7,458.** The Golden Rules' tables, the first run's sweep and the audit's detail moved to `references/golden-rules.md`, `references/bootstrap.md` and `references/audit.md`, which an agent opens when a step needs them. The by-hand fallbacks for a host without the pen are gone, and such a host runs ktl-sidecar's repair first. A note from a person that the librarian reads now leaves its stamp on the concept, so the quiet check knows the note was read.

### Security

- **The workflow reads the retrieval score and the hand-off only as the wrapper's programs wrote them.** The wrapper wrote the score file only when it scored, so an agent could leave its own `n of m` there for the pull request, or a link that sent the next write into the checkout. The wrapper now removes both files once the agent returns.

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
- **The gate refuses a `human:` id it cannot look up.** The schema accepts `human:-x`, and both the GitHub job and the forge-free script skipped such ids as unparsable, so an unsigned confirmation under one passed unseen.
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
