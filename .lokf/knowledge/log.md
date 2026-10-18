# Change Log

## 2026-10-18

* **Changed**: Curating a domain bundle says the diamond rule's stop lasts until both owners pin one release, as the curator's domain-bundle.md now does.
* **Changed**: the source map names the site's `src/components` and `src/styles` folders instead of all of `src/`, in `website/` and in ktl-website's template, since its rows exclude only the components, styles and scripts. Edited since a person confirmed it; the label says so until the curator looks again.
* **Open question**: Knowledge sources: The website rows exclude the site's components, styles and scripts. Is the rest of `src/`, in `website/` and in ktl-website's template, excluded too: its pages, `assets/`, `content.config.ts`, `routeData.ts`, `socialCards.ts` and `trust.ts`? If not, `playbooks/website.md` and `playbooks/ktl-website-skill.md` should cite them.
* **Changed**: the source map now lists in `sources` every path its rows consciously exclude, so `knowledge-report.sh coverage` counts those files as looked at. Each row still gives the reason, and the site's components, styles and scripts are taken as its `src/` and `scripts/` folders. Edited since a person confirmed it; the label says so until the curator looks again.
* **Curation**: human:noelmcloughlin released 3 concepts they wrote, so the librarian may rewrite them from their sources: Trust label, ktl-curator skill and Three lines of defence, each sent back earlier today. Each keeps its confirmation and note, and stays a draft until a person confirms the new text.
* **Curation**: human:noelmcloughlin corrected 1 now and sent 4 back. Knowledge bundle now lists `docs/architecture.md` as a source and says the bundle opens as a vault of its own, beside a person's vault and never inside it. The ktl-librarian skill, Trust label, ktl-curator skill and Three lines of defence went back for not following their sources' recent changes. The same send-back came up three times: Trust label, ktl-curator skill and Three lines of defence carry text a person wrote, which the pen does not let the librarian update when its sources change.
* **Changed**: The curated context layer: the workspace build takes each member and the domain's settings as a person last confirmed them, as `docs/federation.md` says since 0.50.1.
* **Changed**: ktl-sidecar skill: the federation build takes each member as a person last confirmed it and leaves retired concepts out, as `references/automation.md` says since 0.50.1.
* **Changed**: Repository validation: the federation and sync tests cover what 0.50.1 fixed.
* **Changed**: Knowledge sources: the thirty-fourth pass, after 0.50.1. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: the domain bundle playbook says which release a member joins at while a move waits, what a send-back and a removed confirmation do, and that the Domain concept's settings count as a person confirmed them, as domain-bundle.md now says.
* **Changed**: Curating a domain bundle: the diamond rule gives its reason apart from what the two owners then do, as `docs/federation.md` puts it, and a member leaves when the curator retires its concept, as the curator's `domain-bundle.md` says.
* **Prose**: reworded 4 concept bodies in plain English. No fact, link, number or frontmatter changed.
* **Added**: Knowledge outside the repository, from `docs/ingest.md` and the librarian's `references/ingest.md`, which 0.49.0 and 0.50.0 brought; the coverage sweep found the guide under no concept.
* **Rewrite**: The curated context layer: since 0.48.0 `docs/federation.md` holds the tiers of domains, the workspace, what exists and the decisions, which `docs/context-layer.md` no longer carries. The concept now follows both pages, and lists one named graph per bundle, the `lokf-registry` MCP server and the SPARQL endpoint as existing, with lazy loading still a design.
* **Resolved**: The curated context layer: the table in `docs/federation.md` lists one named graph per bundle under `knowledge-federate.py build` as existing, and lazy loading as a design; the MCP server now exists as `knowledge-federate.py mcp`.
* **Open question**: Hosts and doorways: `skills/ktl-sidecar/SKILL.md` now counts six workflow files and `CHANGELOG.md` adds Codeberg to the forges, while the concept, which a person wrote, still says three workflows and three forges.
* **Open question**: Three lines of defence: `docs/three-lines.md` now lists lazy loading, a `lokf-registry` MCP server and remote harvesting as what remains of the context layer, where the concept says the domain tiers and the workspace; `docs/federation.md` lists the MCP server as built.
* **Changed**: Context layer: `docs/context-layer.md` now says why KTL federates bundles through domains, and `docs/federation.md` holds how a federation runs and what remains a design. The concept no longer cites a release date or a table that the context-layer page has dropped.
* **Changed**: Health line: the definition said seven trust labels, while `knowledge-report.sh health` prints eight, as the description and body already say.
* **Changed**: LOKF: `skills/ktl-librarian/SKILL.md` no longer contrasts standard tooling with scripts that only work in the repository that grew them, and no other source says so, so the concept drops that contrast.
* **Changed**: Registrar: `docs/for-the-curious.md` now says that on another forge, or with none, `knowledge-provenance.sh` checks each confirmation's signature against the keys under `.lokf/curators/`, and the concept says so too.
* **Changed**: Work list: `skills/ktl-librarian/SKILL.md` now says only that history orders a source's last commit and the stamp, and no longer adds that no clock does.
* **Open question**: ktl-curator skill: since 0.49.0 `references/review-session.md` says how the curator quotes a source mirrored under `.lokf/mirror/`, and the concept, whose text a person wrote, does not say it.
* **Open question**: ktl-docent skill: since 0.49.0 `references/answering.md` says how the docent cites a source mirrored under `.lokf/mirror/`, and the concept, whose text a person wrote, does not say it.
* **Changed**: ktl-librarian skill: the concept now carries the mirror of sources outside the repository (`references/ingest.md`, new in 0.49.0), the orphan sweep with `knowledge-report.sh coverage` (`SKILL.md`), one `log` line for a whole patch (`references/patch.md`), and the members script's use of the job token (`references/scheduled-task.md`). Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: ktl-sidecar skill: `skills/ktl-sidecar/SKILL.md` and `references/automation.md` now install the sync templates (0.47.0) and the ingest templates (0.49.0), the report script counts tracked files no concept names (0.48.0), and a domain follows member domains tier by tier (0.48.0). The concept now says so, and the points the note of 2026-10-13 names are carried as `SKILL.md` states them.
* **Changed**: ktl-website skill: `CHANGELOG.md` says since 0.48.0 the site's figures stay in the text column and open at full size on a click, which a host gets with its next website repair.
* **Changed**: Contributing: `CONTRIBUTING.md` now says each sibling's `knowledge-sync.yaml` opens the sync pull request within a week, and `scripts/sync-sidecar.sh --pr` and `--finish` open and finish it by hand.
* **Changed**: Releasing: `knowledge-release.yaml` attaches the domain schema the justfile names since 0.46.0, `publish.yml` asks the hosts in `KNOWLEDGE_SYNC_HOSTS` to sync, and `docs/releasing.md` and `scripts/sync-sidecar.sh` say each sibling now syncs itself through `knowledge-sync.yaml`, with `--pr` and `--finish` for the day of a release.
* **Changed**: Repository validation: `scripts/validate-repository.sh` check 9 now reads the site's w3id addresses, check 11 reads `knowledge-sync.manifest` first, and check 15 names the sidecar's `knowledge-sync.sh`; `validate.yml` lints `knowledge-sync.yaml`, and `tests/test_ingest.py`, `tests/test_sync.py` and the `pypdf` pin are new.
* **Changed**: Knowledge sources: a row each for the sync (0.47.0) and the ingest (0.49.0, 0.50.0), the templates row names the federation, sync and ingest templates, the README row KTL Federation's site, and the context-layer row `docs/federation.md`. The map now lists under `sources` the files its rows account for, so the coverage sweep counts them. Edited since a person confirmed it; the label says so until the curator looks again.
* **Resolved**: Knowledge sources: the templates row now names `domain.yaml`, `knowledge-federate.py` and `knowledge-federation.yaml` from `skills/ktl-sidecar/templates/`, the README row names KTL Federation's site, and the context-layer row names `docs/federation.md`.
* **Open question**: Security policy: `SECURITY.md` now counts nine scripts and five workflows in the sidecar's templates and covers the federation build and the sync, which the concept, written by a person, does not carry.
* **Open question**: Threat model: `docs/threat-model.md` now covers the sync workflow, the federation build, the ingest workflow and the mirror, which the concept, written by a person, does not carry.
* **Added**: Curating a domain bundle, from `skills/ktl-curator/references/domain-bundle.md` as `docs/domain-name` leaves it, so a domain host can link the curator's page by its w3id IRI.
* **Changed**: the context layer explanation and the exhibition term no longer name a domain by its position. As `docs/context-layer.md` and `README.md` now say, the domain a build starts from bounds the workspace, and KTL Federation is the domain that federates member bundles.

## 2026-10-16

* **Prose**: reworded 8 concept bodies in plain English. No fact, link, number or frontmatter changed.
* **Changed**: The curated context layer follows `docs/context-layer.md`, which says the domain tiers and the workspace were released on 2026-10-16 as the sidecar's federation templates, with ktl-federation as the first host. The concept no longer says the diagrams draw them dashed, and now carries the page's table of what exists and what remains a design.
* **Open question**: The curated context layer: one bundle, and a federation of bundles: `docs/context-layer.md`'s table under What exists today lists one named graph per bundle as design, beside lazy loading and a `lokf-registry` MCP server. Since 0.44.0 `knowledge-federate.py build` loads each member's `graph.nt` into a named graph named by its `base_iri` and writes them all to `graph.nq`, as `CHANGELOG.md` and the description in `.assets/ktl-context-workspace.svg` say. Is one named graph per bundle now built, with lazy loading and the MCP server still a design?
* **Changed**: Context layer: `docs/context-layer.md` says the federation's domain tiers and workspace were released on 2026-10-16 as the sidecar's templates, so the term no longer calls them a design drawn dashed.
* **Changed**: Health line: since 0.45.0 the line counts eight labels, with *Reopened* for a confirmed concept a question put back to draft, as `knowledge-report.sh` and the curator's `trust-fields.md` now say.
* **Changed**: Trust ladder: `docs/architecture.md` and its ladder figure now say that a question after a confirmation reopens a concept without dropping its rung, and only an edit drops it.
* **Changed**: Domain schema: the curator's `domain-schemas.md` says since 0.44.0 that the sidecar ships one domain schema, `domain.yaml`, for a bundle that federates other bundles.
* **Changed**: Exhibition: the README's Exhibitions section lists KTL Federation since 0.44.0, so the term names five.
* **Changed**: Why the skills live in their own repository: `docs/install.md` now installs all six with one `gh skill install --all --agent` line, says `npx skills` can fail behind a proxy, and no longer records the old repository name, so the concept cites `CHANGELOG.md` for the rename.
* **Changed**: gh skill: the manual's `--agent`, `--scope` and `--dir` options and their defaults, which `docs/install.md` now relies on.
* **Changed**: ktl-sidecar skill: the three files a domain host gets since 0.44.0, `domain.yaml`, `knowledge-federate.py` and `knowledge-federation.yaml`, and what each does, as `SKILL.md` and `references/automation.md` now say.
* **Changed**: ktl-website skill: since 0.45.0 a concept's card shows its open questions beside the label, which reads *reopened* for a confirmed concept a question put back to draft.
* **Changed**: Releasing: since 0.45.0 `sync-sidecar.sh` keeps a sibling's own `schema :=` line, reports a failure of any check it runs, and writes the sibling's changelog entry in full.
* **Changed**: Repository validation: check 9a skips a sibling's website build output, check 10a counts no table pipes, check 11 covers a domain host's three files, check 17a keeps every tracked `SKILL.md` under `skills/ktl-*/`, `actionlint` reads five templates, and `test_federation.py` joins the tests, as 0.44.0 and 0.45.0 brought them.
* **Open question**: When the built-in vocabulary stops fitting - domain schemas: Since 0.44.0 `skills/ktl-curator/references/domain-schemas.md` says one domain schema ships with the sidecar, `domain.yaml`, for a bundle that federates other bundles, and ktl-librarian's `references/domain-schema.md` points a domain bundle at that template and at the curator's `domain-bundle.md`. This concept does not say so.
* **Open question**: Trust label: Since 0.45.0 `skills/ktl-curator/references/trust-fields.md` has a label *Reopened*: `status: draft` on a concept with a `human:` `verified` event, naming the earliest question asked on or after the confirmation's day, its asker and how many wait. A reopened concept still counts as confirmed, and *Still a draft* now needs no `human:` event. This concept does not name the label.
* **Open question**: ktl-curator skill: Since 0.45.0 the curator's label table reads *Still a draft / Reopened*, and the health line counts *Reopened*, a confirmed concept a question put back to draft, apart from *Drafts* (`SKILL.md`, `references/trust-fields.md`). Since 0.44.0 `references/domain-bundle.md` says how a person confirms a member of a domain bundle. This concept carries neither.
* **Open question**: ktl-docent skill: Since 0.45.0 the docent's label table reads *Still a draft / Reopened*: for a confirmed concept a question put back to draft, the docent says the confirmation first, then when it was reopened, by whom and how many questions wait (`SKILL.md`, `references/answering.md`). Since 0.44.0 `references/answering.md` also says how to answer on a domain host from the workspace under `snapshot/`, labelling each concept with its bundle. This concept carries neither.
* **Open question**: Knowledge sources: Since 0.44.0 ktl-sidecar's templates also hold a domain host's `domain.yaml`, `scripts/knowledge-federate.py` and `github/knowledge-federation.yaml`, which `sync-sidecar.sh` carries and check 11 holds to their templates where a copy exists. The templates row counts nine scripts and three workflows and names none of them. The README's Exhibitions list KTL Federation since 2026-10-16, and `docs/context-layer.md` says the federation design was released that day. The README row and the context-layer row say neither.
* **Prose**: reworded 4 concept bodies in plain English. No fact, link, number or frontmatter changed.
* **Changed**: Exhibition names the four sites the README's Exhibitions section lists since 2026-10-16, the two Obsidian plugins' sites among them.
* **Changed**: Knowledge sources says the README links the site's pages since 0.43.1 and lists the two Obsidian plugins' exhibitions since 2026-10-16, and records the thirty-second pass. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: Releasing says `sync-sidecar.sh` carries `.lokf/justfile` since 0.43.1 and keeps the sibling's first line, which names the host, as `docs/releasing.md` now says.
* **Changed**: Repository validation says check 11 holds `.lokf/justfile` to its template below the first line since 0.43.1.
* **Open question**: Three lines of defence - where each role sits, and what an auditor can check: Since 0.43.0 `docs/three-lines.md` shows `.assets/ktl-three-lines-dark.svg` in GitHub's dark theme, and `CHANGELOG.md` says the `-dimmed` set stays in `.assets/` unreferenced. This concept says the diagram has a dimmed counterpart for dark mode.

## 2026-10-15

* **Changed**: Why the skills live in their own repository: `docs/install.md` no longer says one install serves every repository or that a repository needs no copy; it says a user install keeps the agent's instructions under the user's control.
* **Changed**: Why four skill roles: ktl-website now builds the schema's pages and the data too, as `docs/architecture.md` says since 0.41.0, and the concept no longer says the roles lose nothing without it, which the page says only of ktl-prose.
* **Changed**: ktl-website skill: what 0.43.0 added to the site (the full-text and Markdown files, the log feed, concept history and licence, hover previews, release links and reading levels), and the site's address; the architecture page does not say the roles lose nothing without it.
* **Changed**: ktl-sidecar skill: the scheduled librarian's `AGENT_PROMPT_FLAG`, the five conditions for any other agent, the patch file written with the agent's own file tool, the pull-request setting the `publish` job needs, and rule 13's `base_iri` exception, as `references/automation.md` and `references/gate.md` now say.
* **Changed**: ktl-librarian skill: the scheduled run's prompt flag, the rule that the agent writes its patch with its own file tool, and the pull-request setting, as `knowledge-librarian.sh` and `references/scheduled-task.md` now say. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: Releasing: `sync-sidecar.sh` works on a `sync-<tag>` branch in each sibling and sets its next steps apart, and the changelog fold lists each entry once, as 0.40.0 and 0.42.0 brought them.
* **Changed**: Repository validation: check 11w also holds the website template's logos equal to `.assets/`, check 14 proves the fold lists each entry once, and the website smoke test builds the schema's pages and the data, as `validate-repository.sh` and `smoke-test-website.sh` now do.
* **Changed**: The docent in Microsoft 365 Copilot: `docs/m365.md` now says an auditor would be `ktl-auditor-m365.md`, not that it is planned, and no longer says the identity record is held in reserve.
* **Changed**: Accession: the quotation follows `docs/architecture.md`, which now says the registrar "keeps the records in order".
* **Changed**: Registrar: the quotation follows `docs/architecture.md`, which now says the registrar "keeps the records in order".
* **Changed**: Domain schema: `docs/architecture.md` and `docs/for-the-curious.md` no longer say "not a looser bundle", so the term no longer does.
* **Changed**: Doorway: `docs/obsidian.md` no longer says to open the link itself and never the host root, so the term cites ktl-docent's `references/obsidian.md`, which still does.
* **Changed**: Workshop: `docs/obsidian.md` no longer says what keeps the workshop clean, so the term cites ktl-docent's `references/obsidian.md`, which still does.
* **Changed**: Exhibition: the README's Exhibitions section, added in 0.42.0, lists the sites that show a repository's collection.
* **Changed**: The source map: the README's row names the Exhibitions and the site's address, and the thirty-first pass is recorded. Edited since a person confirmed it; the label says so until the curator looks again.
* **Open question**: Security policy: Since 0.41.0 the ktl-website row of `SECURITY.md` says the build job also runs `just` when the site builds a folder through a recipe, and that the sync runs the commands `site.config.mjs` names to build the schema's pages and the data. Since 2026-10-14 `SECURITY.md` also counts five surfaces, matching its table. This concept carries neither.
* **Open question**: Threat model: Since 0.41.0 `docs/threat-model.md` says that ktl-website's build also runs the commands its `site.config.mjs` names, or a `gen-doc` recipe it finds, to build the schema's pages and the data, and that they are the repository's code too. This concept does not say so.
* **Open question**: Knowledge Trust Ladder in a skills repository: Since 2026-10-14 `docs/skills-repositories.md` says each of this repository's six skills has a `Playbook` concept. This concept still says five.
* **Open question**: Knowledge bundle: Since 2026-10-14 `docs/obsidian.md` sends readers to each plugin's usage page, not its README, and says the plugins' architecture pages name the cost of putting exhibits in a vault's index. This concept says the plugin READMEs name the cost of a folder inside a vault. Which page names that cost now?
* **Open question**: Build, preview and edit the website: Since 0.43.0 `website/README.md` says the site also serves the bundle log as an Atom feed, `knowledge/log.xml`, and the home, docs and extra pages as Markdown beside them, and that each release page links the repository, the docs and the bundle at the release's tag. It names `src/components/ReadingLevels.astro` and `src/components/ConceptPreviews.astro` for the reading levels and the hover preview. This concept names none of them.

## 2026-10-14

* **Changed**: ktl-website skill: the Schema topic, the data pages in Datasette Lite, the preflight's recipe and `just` lines, the weekly run and its new triggers, and the smoke test's schema and data, as 0.41.0 and 0.42.0 brought them.
* **Open question**: Build, preview and edit the website: Since 0.41.0 (2026-10-14) `knowledge-website.yaml` also runs every Monday at 05:23 UTC from the default branch, and on a change to `.linkml/`, a justfile, a `pyproject.toml` or a `uv.lock`; the scheduled run deploys too. This concept lists the push and pull-request paths up to the workflow itself, and no weekly run.
* **Open question**: Build, preview and edit the website: `website/README.md` now says a promoted release's changelog page appears with the next build, the workflow's weekly run at the latest, or a run by hand. This concept says the next build, or a run by hand.
* **Open question**: Build, preview and edit the website: `website/README.md` now names `site.config.mjs` for the site's values and options, `src/styles/custom.css`, this repository's own, for its look, and `src/components/Mermaid.astro` for how a diagram is drawn, and says `node scripts/config.mjs` prints what the sync reads. This concept's What to edit section names none of them.
* **Open question**: Build, preview and edit the website: Since 0.42.0 (`CHANGELOG.md`) the README and the architecture page link the site at its persistent address, `https://w3id.org/ktl/`, which redirects to the GitHub Pages address this concept names.
* **Changed**: `base_iri` moved from the `knowledge-trust-ladder.example` placeholder to `https://w3id.org/ktl/knowledge/`, now that the w3id rule resolves it. Every concept id, the publisher id and every typed-relation target moved with it; no `verified` event changed.
* **Changed**: Knowledge sources: `base_iri` is now `https://w3id.org/ktl/knowledge/`, no longer the `knowledge-trust-ladder.example` placeholder. Edited since a person confirmed it; the label says so until the curator looks again.
* **Added**: ktl-website skill, from `skills/ktl-website/SKILL.md` and its references, the sixth skill that 0.39.0 added.
* **Changed**: Versioning policy: six skills under one tag, as `docs/architecture.md` and `CONTRIBUTING.md` now count since ktl-website. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: Why the skills live in their own repository: six skills, as `docs/install.md`, `plugin.json` and `marketplace.json` now count since ktl-website.
* **Changed**: Contributing: only `website/` builds, two helpers (`ktl-prose` and `ktl-website`) and six skills under one tag, check 11w among the template pairs, and the website's role boundary, as `CONTRIBUTING.md` now says.
* **Changed**: Repository validation: six skill directories, ktl-website's word budget, checks 11w and 12w, check 17 over every skill's templates, the two website test modules, four workflow templates for actionlint and the `smoke-test-website` job, as `validate-repository.sh` and `validate.yml` now say.
* **Changed**: Releasing: six skills under one tag since 0.39.0 (`CHANGELOG.md`), and `sync-sidecar.sh` also carries ktl-website's templates to a sibling that has a site.
* **Changed**: ktl-sidecar skill: Step 6 names ktl-website as the skill that can publish the bundle, and the scheduled librarian's and the release's variables go under Repository variables, never on an environment, as `SKILL.md` and `references/automation.md` now say.
* **Changed**: Why four skill roles: the architecture page now names a sixth skill, `ktl-website`, which publishes the bundle and is optional like `ktl-prose`.
* **Changed**: The source map: six skill playbooks, a row for ktl-website's templates and preflight, the website workflow's new name, the website smoke test, and the thirtieth pass's notes. Edited since a person confirmed it; the label says so until the curator looks again.
* **Open question**: Security policy: Since 2026-10-14 `SECURITY.md` lists ktl-website's templates and its preflight as a surface of their own. It names `knowledge-website.yaml` among this repository's copies of the templates, counts the six skills' prose, and names five skills that run `.lokf/scripts/`, ktl-website among them. This concept carries the earlier table and four skills. `SECURITY.md` itself still says four surfaces above a table of five rows.
* **Open question**: Threat model: Since 2026-10-14 `docs/threat-model.md` names ktl-website among the skills that run the repository's scripts from `.lokf/scripts/`, counts four workflow templates under the two skills' `templates/github/` as pinned, and says six skills read content they did not author. This concept still names four skills that run those scripts.
* **Open question**: Hosts and doorways - where the bundle's real folder lives: Since 2026-10-14 the portability matrix in `skills/ktl-sidecar/references/portability.md` says that on GitLab, Forgejo and Gitea the GitHub Actions workflows are lost, ktl-website's deploy included. This concept says the three GitHub Actions workflows are the only loss there.

## 2026-10-13

* **Curation**: human:noelmcloughlin corrected 1: Build, preview and edit the website, now naming `knowledge-website.yaml`, the default branch, the variable gate, `docs/architecture.en-simple.md` and `DOCS.groups`.
* **Curation**: human:noelmcloughlin sent 1 back: Build, preview and edit the website, for the `website.yml` changes the ktl-website skill brings.
* **Changed**: The context layer now says the architecture page uses the term and links the page, since "Why libraries have catalogues" and "Prose, Structure, Meaning, Context" moved there from the README on 2026-10-13. It is about the glossary term of the same name.
* **Changed**: Intended uses takes the context layer and the question of who is responsible from `docs/architecture.md`, where the README's sections moved on 2026-10-13, and keeps the README for what the project is.
* **Changed**: Why a distribution repository now cites `docs/install.md`, which holds the quick start, the plugin commands and the docent-only route the README carried until 2026-10-13, and `docs/architecture.md` for the one-tag rule.
* **Rewrite**: Why four roles follows `docs/architecture.md`, where the README's roles moved on 2026-10-13, and answers the note sent back that day. Only KTL Registrar does the registrar's work in Obsidian, and the concept now carries the Runs column, the curator always being a person, what ktl-prose never changes and the three lines of defence.
* **Changed**: Why four roles cites `docs/architecture.md` and `docs/obsidian.md`, and relates to the three lines of defence its body links.
* **Changed**: WikiSkill cites `docs/architecture.md` for the paper's credit, which moved there from the README on 2026-10-13.
* **Changed**: Accession cites `docs/architecture.md`, where the README's fifth-role section moved on 2026-10-13, and relates to the collection an accession joins.
* **Changed**: Desk cites `docs/architecture.md`, where the README's fifth-role section moved on 2026-10-13, and gives the registrar's work in Obsidian to KTL Registrar alone, as that page says.
* **Changed**: Docent cites `docs/architecture.md`, where the README's table of roles moved on 2026-10-13, and the retelling beside it.
* **Changed**: LOKF cites `docs/architecture.md`, where the README's format section and credits moved on 2026-10-13, and relates to LinkML, the language its schema is written in.
* **Changed**: OKF cites `docs/architecture.md`, whose credits name Google Cloud as the specification's creator since they moved from the README on 2026-10-13.
* **Changed**: Registrar cites `docs/architecture.md`, where the README's fifth-role section moved on 2026-10-13.
* **Changed**: Sidecar cites `docs/architecture.md`, where the README's table of roles moved on 2026-10-13.
* **Changed**: The pen cites `docs/architecture.md`, where the README's fifth-role section moved on 2026-10-13; the README no longer names the pen.
* **Changed**: The pen for younger readers follows the pen, which now names the architecture page instead of the README.
* **Changed**: ktl-prose skill cites `docs/architecture.md` for the fifth skill, which moved there from the README on 2026-10-13.
* **Rewrite**: Versioning answers the note of 2026-10-13: it says what `.releaserc.json` does with `!` beside what `docs/releasing.md` says, from commit-analyzer's default preset and rules at the version the workflow pins. The one-tag rule cites `docs/architecture.md`, where the README's reading list moved. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: Versioning cites `.releaserc.json`, the release workflow and commit-analyzer's README, default rules and Angular parser. Edited since a person confirmed it; the label says so until the curator looks again.
* **Open question**: Versioning policy: `docs/releasing.md` and the `plan` job in `.github/workflows/semantic-release.yml` treat `!` after the type as breaking. `.releaserc.json` names no preset, and the default Angular preset of commit-analyzer, which the workflow pins at 13.0.1, has no place for `!` in its header pattern, so a `feat!:` commit releases nothing. Which should change: the preset, or the page and the plan job?
* **Changed**: Releasing now says which rules are `.releaserc.json`'s and which are commit-analyzer's defaults, and that the Angular preset it reads commits with has no place for `!`.
* **Changed**: The lokf toolkit answers the note of 2026-10-13. It no longer says the SHACL shapes catch violations, which `CHANGELOG.md` withdrew, calls the template's `lokf[build]>=0.8.0` a floor, and carries the librarian's version check and the byte-identical schema. Its commands come from the toolkit's `cli.py` at v0.8.0, and its extras and their uses from the pages that name them.
* **Changed**: ktl-sidecar skill answers the note of 2026-10-13. The wrapper looks under `.claude/skills/`, `.github/skills/` and `.agents/skills/` before bare `skills/`, `references/m365.md` dates from 2026-09-24, and the concept now carries the repair rule, the base IRI rule, the four things gitignoring changes and why placeholders are substituted with Python.
* **Changed**: Repository validation says check 9 now also checks each heading a sibling repository links to, as `scripts/validate-repository.sh` does since 2026-10-13.
* **Open question**: When the built-in vocabulary stops fitting - domain schemas: Since 2026-10-13 the section "Prose, Structure, Meaning, Context" is on `docs/architecture.md`, not in `README.md`. This concept says "The README says" for its quotation and lists `README.md` in `sources`; both should name `docs/architecture.md`.
* **Open question**: Why a registrar role, and why it is not a skill: Since 2026-10-13 the fifth-role section is on `docs/architecture.md`, not in `README.md`, so `resource`, `sources` and "The README calls it the fifth role" should name that page. That page and `docs/obsidian.md` now say KTL Registrar does the registrar's work and KTL Curator assists the curator, while this concept and its description say both plugins do the registrar's work.
* **Open question**: Three lines of defence - where each role sits, and what an auditor can check: Since 2026-10-13 the fifth-role section that points at `docs/three-lines.md` is on `docs/architecture.md`, not in `README.md`. The sentence "The README's section on the fifth role" and the `README.md` source should name `docs/architecture.md`.
* **Open question**: Knowledge bundle: Since 2026-10-13 `README.md` keeps the poem, but "Why libraries have catalogues", which says a bundle is the catalogue, is on `docs/architecture.md`. `sources` should list `docs/architecture.md` beside `README.md`.
* **Open question**: ktl-curator skill: Since 2026-10-13 the Runs column ("a little, regularly") is in the table of roles on `docs/architecture.md`, not in `README.md`. `sources` should list `docs/architecture.md` instead of `README.md`.
* **Open question**: ktl-docent skill: Since 2026-10-13 the Runs column ("whenever anyone asks") is in the table of roles on `docs/architecture.md`, not in `README.md`. `sources` should list `docs/architecture.md` instead of `README.md`.
* **Open question**: Build, preview and edit the website: Since 2026-10-13 `website/README.md` says `docs/architecture.en-simple.md` becomes the page for readers aged 13 to 18, and that the home page's tagline is the first line of `docs/architecture.md` that is bold throughout; `.github/workflows/website.yml` no longer lists `README.en-simple.md`. This concept still names `README.en-simple.md`. `CHANGELOG.md` changed too, only in its unreleased notes, and still records the site under the 0.38.1 release.
* **Changed**: The LinkML reference is titled LinkML (linkml.io), as its siblings name their sites, so the index tells it from the glossary term.
* **Added**: Librarian, a role the glossary lacked, from the table of roles on `docs/architecture.md` and ktl-librarian's `SKILL.md`.
* **Added**: Curator, a role the glossary lacked, from the table of roles on `docs/architecture.md`, the verdicts in `docs/for-the-curious.md` and the plugin table in `docs/obsidian.md`.
* **Added**: Collection, the word the README's opening paragraph sets in bold, from the README and `docs/architecture.md`.
* **Added**: Context layer, the term `docs/architecture.md` sets in bold, beside the explanation of the same name, with `docs/context-layer.md`'s definition.
* **Added**: Trust ladder, the project's own name for how far each claim has been checked, from `docs/architecture.md`.
* **Added**: Workshop, one of the two vaults `docs/obsidian.md` sets in bold.
* **Added**: Exhibition, one of the two vaults `docs/obsidian.md` sets in bold.
* **Added**: Doorway, the name `docs/obsidian.md` gives the `knowledge_bundle` link, with ktl-sidecar's rule for a gitignored `.lokf/`.
* **Added**: Health line, from the curator's `trust-fields.md` and `SKILL.md`, the report script and the architecture page.
* **Added**: Work list, from ktl-librarian's `SKILL.md` and `docs/for-the-curious.md`.
* **Added**: LinkML, the schema language LOKF is written in, from `docs/architecture.md`, `docs/for-the-curious.md`, ktl-librarian's `SKILL.md` and the curator's `domain-schemas.md`. The LinkML reference defines it.
* **Added**: Domain schema, the term `docs/for-the-curious.md` defines, with what the architecture page says it gives a domain.
* **Added**: Three lines of defence, the model `docs/architecture.md` sets in bold, from `docs/three-lines.md`.
* **Changed**: The source map follows the README's move: `docs/architecture.md` joins the README's row, the retelling has its new path, the install count, the card and the release rows follow their pages, and the twenty-ninth pass is recorded. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: Docent cites the retelling for readers aged 13 to 18 at its new path, `docs/architecture.en-simple.md`.
* **Curation**: human:noelmcloughlin confirmed 2 concepts, corrected 16, sent 5 back and marked 1 for later. Two corrections added files the concept drew on to `sources`, two moved a `resource` to the page that holds the facts, ten restored facts a summary had dropped from its source, and two send-backs name claims from files the concept does not list, so the librarian may be citing too few sources and shortening too far.

## 2026-10-12

* **Prose**: reworded 2 concept bodies in plain English: the context layer, whose pin-or-float detail now follows the list of decisions, and the website playbook. No fact, link, number or frontmatter changed.
* **Changed**: The context layer follows `docs/context-layer.md` again: its new title and federation heading, and the pin-or-float decision, which the page now settles by pinning and which absorbs the staleness bullet. Trust at read time moved from the decisions into the workspace section, as on the page.
* **Changed**: Domain schemas quotes the README as it now reads, which says a domain "extends the schema" without naming LinkML.
* **Added**: Build, preview and edit the website, from `website/README.md` and `.github/workflows/website.yml`, which the 0.38.1 release added.
* **Changed**: The source map gains a row for `website/` and `website.yml`, which feed the new website playbook. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: `docs/context-layer.md` and `docs/context-layer-technology.md` now write catalogue, as the README and the rest of the bundle do. The concept and its description follow them; product names such as Unity Catalog keep their own spelling.
* **Changed**: Knowledge sources records the twenty-seventh pass. Edited since a person confirmed it; the label says so until the curator looks again.
* **Prose**: reworded 2 concept bodies in plain English: WikiSkill and SkillWiki, after the librarian rewrote both. No fact, link, number or frontmatter changed.
* **Changed**: WikiSkill takes the page's new title, and its description names what the page now holds.
* **Changed**: SkillWiki takes the page's new title, and its description names what the page now holds.
* **Rewrite**: `docs/wikiskill.md` was trimmed to what KTL took from the paper and what the paper leaves open, without the part-by-part table or the programs, models and people table. The concept follows it, under the page's new title.
* **Rewrite**: `docs/skillwiki.md` was trimmed to the four changes, the excerpt check and where the designs part, without the side-by-side table, the programs, models and people table or the paper's open points. The concept follows it, under the page's new title.
* **Changed**: `docs/skills-repositories.md` no longer reads the two papers against KTL's design, and now gives the handling before the two runs. The overview says so.
* **Changed**: `docs/context-layer.md` no longer quotes Tellius, Andreessen Horowitz, Forrester, Gartner and the other vendors, nor the analogies in its workspace steps. The concept drops the two quotations it carried.
* **Changed**: `docs/three-lines-critics.md` is no longer marked as preliminary research, and the concept no longer says it is.
* **Changed**: Knowledge sources: the `docs/wikiskill.md`, `docs/skillwiki.md` and `docs/skills-repositories.md` rows follow the trimmed pages, and the twenty-sixth pass is recorded. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: Domain schemas now relates to the curator skill instead of naming it as its subject.
* **Changed**: Three lines of defence now relates to the two role explanations instead of naming them as its subject.
* **Changed**: Versioning now relates to the releasing playbook instead of naming it as its subject. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: ktl-sidecar skill now cites commit 61b9355, which split `gate.md` out of `automation.md` on 2026-09-24.
* **Changed**: The source map's templates row now names every file the sidecar writes, and re-checks the `justfile`, which carries the domain-schema variable since 0.38.0. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: Trust label keeps `definedBy` as an empty list, as every relation field is a list.
* **Changed**: Context layer now names all three gaps `docs/context-layer.md` says OKF leaves open, and the page's recommendation on cross-bundle links.
* **Changed**: Hosts and doorways now gives both halves of what Obsidian's *Excluded files* does, as `skills/ktl-sidecar/references/portability.md` states them.
* **Changed**: Intended uses now says, as the README does, that the context layer is what is missing and the bundle is its catalogue.
* **Changed**: Three lines of defence now matches `docs/three-lines-critics.md` on how its sources are cited and on who produces evidence that oversight works, and relates to the context layer it links.
* **Changed**: Why a distribution repository's description now names the Microsoft 365 route and the rename its body covers, and its sources list `.claude-plugin/plugin.json`.
* **Changed**: Why four roles no longer calls every handoff a frontmatter fact, since one is a feedback entry, and says the pen marks new concepts as drafts.
* **Changed**: WikiSkill now quotes `docs/wikiskill.md` on the concepts readers keep arriving at, and relates to SkillWiki, which it sets itself apart from.
* **Changed**: OKF now lists `README.md`, the source that names Google Cloud as the specification's creator.
* **Changed**: Trust label now references the OKF specification rather than naming it as the definition, since the labels are defined in `trust-fields.md` and the specification defines only the fields.
* **Changed**: The pen for younger readers now relates to the registrar its body links.
* **Changed**: ktl-librarian skill now covers its plain-English rules and the offer of a prose pass before hand-off, and carries typed relations to the security policy and ktl-prose that its body names. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: ktl-prose skill now numbers its steps 0 to 5 as `SKILL.md` does, says step 0 runs the conventions script too, and drops an override claim no source makes.
* **Changed**: ktl-sidecar skill now says the `validate` job passes the merge-base, as `knowledge-registrar.yaml` has done since 0.36.1.
* **Changed**: Open the bundle in Obsidian now lists Obsidian's symlinks help page, the source of the sentence it quotes.
* **Changed**: Releasing now points at the paragraph that describes `check`; the page has no next section.
* **Changed**: Threat model now lists `knowledge-conventions.sh`, the source of its claim about conventions rule 10.
* **Changed**: Code of conduct's description no longer promises the behavioural standards, which the body does not list.
* **Changed**: Open Skills CLI's description now says what the body covers: the installer and its local-path use as a pre-publication check.
* **Changed**: The source map no longer says all three release files sit behind the `release` Environment; only the `release` job does. Edited since a person confirmed it; the label says so until the curator looks again.
* **Open question**: Knowledge bundle: the body's library and museum terms, the workshop and the log and index details come from `README.md`, `docs/obsidian.md` and `skills/ktl-librarian/SKILL.md`, but `sources` names only `skills/ktl-sidecar/templates/README.md`. Should those three be added as sources?
* **Open question**: Why a registrar role, and why it is not a skill: the body's account of the pen (stamps `generated`, keeps index bullets equal, files the log line, refuses some writes) and of the wrapper comes from `skills/ktl-librarian/SKILL.md` and `skills/ktl-sidecar/SKILL.md`, which are not in `sources`. The pen also refuses deleting a concept a person left a note on, not only one a person confirmed. And `about` names the knowledge bundle while `glossary/registrar` describes this role. Should these change?
* **Open question**: Agent Skills specification: the body says the `description` is kept near ~100 tokens, but the specification's ~100 tokens is a startup budget for `name` and `description` together, and this repository enforces only the 1024-character limit (check 3c); its descriptions run to about 150 to 230 tokens. The `resource` is `agentskills.io/home` while the facts come from `agentskills.io/specification`. Should both change?
* **Prose**: reworded 22 concept bodies in plain English. No fact, link, number or frontmatter changed.
* **Changed**: the README's *context layer* now links `docs/context-layer.md`, which the concept now cites. That page, like the README, names no intended use or non-goal, so the open question stays.
* **Changed**: `docs/three-lines.md` now lists the context layer's domain tiers and workspace among what remains for this project, and the concept follows it.
* **Changed**: `README.md` no longer calls a docent a museum's name for a guide. `README.en-simple.md` does, and the concept now cites it.
* **Changed**: `README.md` no longer says each skill stands alone, and no other source does, so the concept no longer says it.
* **Changed**: `scripts/sync-sidecar.sh` no longer counts ai-linkmo among the siblings it brings up to a release, and the concept no longer does either.
* **Changed**: the source map names `docs/context-layer.md` and `docs/context-layer-technology.md`, which the new context-layer concept follows. Edited since a person confirmed it; the label says so until the curator looks again.
* **Open question**: OKF specification (v0.2): the `resource` is the copy under `knowledge-catalog/okf/`, whose folder's README now says OKF lives in its own repository and asks readers to stop using that copy. The README, the sidecar's README template and `CHANGELOG.md` now link `https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md`. A person wrote this concept, so moving its `resource` is the curator's to record.
* **Added**: The context layer, from `docs/context-layer.md` and `docs/context-layer-technology.md`, which the README now links.
* **Changed**: check 16 is described without the repository's old name, which the check itself refuses outside the files that record history.
* **Changed**: ktl-librarian now names the domain schema by one `schema` line in the justfile, has pages for a host of Agent Skills and for retellings, and the scheduled run validates through `just lokf-check-refs`. `references/domain-schema.md`, `references/agent-skills.md`, `references/retellings.md` and `knowledge-librarian.yaml` say so. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: ktl-sidecar's page now names the fourteenth convention, the curator's queue in the report script, and what is tested before a release. `references/gate.md`, `references/portability.md` and the CHANGELOG entries for 0.36.0 and 0.37.1 say so.
* **Changed**: ktl-curator's page now says the script ranks the queue and counts reliance through thirteen relation fields, reads the justfile's `schema` line, offers a `Younger readers:` switch, and asks what replaced a retired concept. `SKILL.md`, `references/trust-fields.md` and `references/review-session.md` say so.
* **Changed**: ktl-docent's page now follows all thirteen typed relations, names a retired concept's successor and the label for a reader's dispute, passes `--concept` with a Disagreement, and answers a younger reader. `SKILL.md`, `references/answering.md` and `references/feedback.md` say so.
* **Changed**: ktl-prose's page now covers retellings for younger readers and the pass for dyslexic readers, with `prose-check.py --audience`, `--derived-from` and the VOA word book. `references/young-readers.md`, `prose-check.py` and the 0.38.0 CHANGELOG entry say so.
* **Changed**: `changelog-release.mjs check` now passes an empty `[Unreleased]` for a version already promoted, as `.releaserc.json` and the script say since #114, and `publish.yml` runs the pytest suite under `tests/` before it publishes.
* **Rewrite**: the behavioural checks moved out of `scripts/validate-repository.sh` into pytest modules under `tests/`, which `validate.yml` runs in a job of its own (0.37.1). The page now lists the contract's checks as the script numbers them, says which module carries each moved check, and adds checks 7c, 7d, 10a and 22.
* **Changed**: `CONTRIBUTING.md` now asks for `pytest` beside the contract script before a pull request, lists `tests/` in its layout, and says the skills are written partly in Python, not in one Python script.
* **Changed**: the limits list now names `skills/ktl-sidecar/references/m365.md` as the source of Agent Builder's 50 MB zip limit, beside the toolkit's 10 MB app package the builder enforces.
* **Changed**: A domain schema is now one `schema` variable in the sidecar's justfile, which the validate and check-refs recipes and the three workflows use, as `skills/ktl-librarian/references/domain-schema.md` and the justfile template say since #116.
* **Changed**: `docs/skills-repositories.md` now says what KTL does and leaves alone in a repository of Agent Skills; no source yet states intended uses or non-goals in general, so the question stays open.
* **Changed**: The install commands now install for the user (`--global`, `--scope user`), and `docs/install.md` gained a section on when a team installs into the repository instead (#115).
* **Changed**: `docs/wikiskill.md` now names WikiSkill apart from SkillWiki, the 2026 paper `docs/skillwiki.md` reads, and the concept says so.
* **Changed**: the trust labels now include *a reader disputed this*, read from `.lokf/feedback.md`, and *derived from a concept edited since its confirmation*, and a retired concept names its successor from `log.md`; `skills/ktl-curator/references/trust-fields.md` says so.
* **Changed**: `SECURITY.md` now counts four skills that run the repository's `.lokf/scripts/`, ktl-prose among them, and says `prose-check.py` also reads the skill's own word list. Every other claim was checked against `SECURITY.md` and `scripts/validate-repository.sh` check 10 and still holds. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: `docs/threat-model.md` now names ktl-prose among the skills that run `.lokf/scripts/`, adds conventions rule 14, says what a Disagreement's concept path is used for, and covers a skills repository. The concept follows all four.
* **Changed**: the source map names the files tracked since the 2026-10-06 refresh (`tests/`, `pytest.ini`, `README.en-simple.md`, `docs/skillwiki.md`, `docs/skills-repositories.md`, `docs/examples/prose.md`, ktl-prose's word list and three new references) and follows the README's renamed agents callout. Edited since a person confirmed it; the label says so until the curator looks again.
* **Added**: SkillWiki's skill governance and KTL, from `docs/skillwiki.md`, which no concept covered.
* **Added**: KTL in a skills repository, from `docs/skills-repositories.md`, which no concept covered.
* **Prose**: after the librarian's refresh, reworded 3 concept bodies in plain English: repository validation now says which test module tests each moved check, and two long sentences in the SkillWiki and skills-repository concepts became lists. No fact, link, number or frontmatter changed.

## 2026-10-11

* **Added**: The pen, retold for readers aged 13 to 18 from `glossary/the-pen.md`, the first retelling for younger readers in this bundle.

## 2026-10-06

* **Prose**: after the librarian's refresh, reworded 2 more concept bodies: a long sentence in the ktl-prose skill split in two, and the lokf toolkit's last paragraph split where it turns to the no-Python fallback. No fact, link, number or frontmatter changed.
* **Changed**: ktl-prose now lays out what it rewords the way the file's project does, one line for each paragraph and list item in the bundle, as `skills/ktl-prose/SKILL.md` and `references/rules.md` now say. The concept says so in its rules, its steps and its note on files outside the bundle.
* **Changed**: since 2026-10-05 the no-Python fallback reads LOKF's schema from the commit tagged `v0.8.0`, never from the tag, as `skills/ktl-librarian/SKILL.md` and `CHANGELOG.md` say; both are now among the concept's sources. The description now has no dash.
* **Changed**: check 11's synthetic bundle also breaks rule 12 with an index bullet left behind by an edited description, as `scripts/validate-repository.sh` shows, and the list of breaks now includes it. The description now has no dash.
* **Changed**: the body cites check 9 of `scripts/validate-repository.sh`, which lists `docs/threat-model.md` among the paths a sibling depends on, so that script is now among the concept's sources. The description now has no dash.
* **Changed**: the install manual does not say the command group may change without notice; the v2.90.0 release notes do, and the concept now credits them. The publish manual and the two workflows that call `gh skill publish` are now among its sources.
* **Changed**: the contributing playbook's description, which both index bullets copy, now reads in plain English, with no dash.
* **Changed**: the ktl-curator skill's description, which both index bullets copy, now reads in plain English, with no dash.
* **Changed**: the ktl-docent skill's description, which both index bullets copy, now reads in plain English, with no dash.
* **Changed**: the code of conduct's description, which both index bullets copy, now reads in plain English, with no dash.
* **Changed**: The docent records a miss through its own copy of `knowledge-feedback.sh`, as `skills/ktl-docent/SKILL.md` now says. The concept's quotation that a docent explains the exhibition without moving anything on the shelves now comes from the README's table of roles.
* **Changed**: `docs/install.md` no longer counts four skills or calls `ktl-prose` a helper, and points to the README's install section instead. The concept now says what `README.md` says: each skill stands alone, and `ktl-prose` is optional and installs the same way.
* **Changed**: `README.md` no longer says that a person confirms drafts a few at a time, so the run order drops the phrase. Its docent row now says that, like a real docent, the docent explains the exhibition without moving anything on the shelves, and the docent bullet says so too. The sidecar bullet says the skill installs `.lokf/`, the README's own verb.
* **Changed**: `skills/ktl-curator/references/trust-fields.md` now reads a `verified` key with no events as *nobody has checked this yet*, as `knowledge-report.sh` does, and the concept says so.
* **Changed**: `README.md` now makes the taxonomy point in one sentence: LOKF supplies the fixed taxonomy that OKF leaves to the producer, and a domain that outgrows it extends the schema. The concept follows it, and no longer says that any domain can bring its own, which no source now states.
* **Changed**: The concept now lists `docs/three-lines-critics.md`, which it summarises, and `CHANGELOG.md`, which dates the critics page's arrangement, as its sources. It drops a date that no source gives, and says *holds*, *installs* and *released* where the pages do.
* **Changed**: `docs/wikiskill.md` now leaves the pen's refusals, conventions rule 13 and `revision` to the threat model and the three-lines page, and says once what it said twice. The concept follows it, takes the page's labels for two findings, and says *merges* where it said *lands*.
* **Changed**: `skills/ktl-sidecar/SKILL.md` says that every skill addresses `.lokf/knowledge`, where the table counted four skills, and that Step 2 adds the doorway.
* **Changed**: `CONTRIBUTING.md` now has a template change copied over each of this repository's copies, ktl-docent's included, under checks 11 and 11a, and names the two plugin repositories in the sync command.
* **Changed**: `SECURITY.md` now counts ktl-docent's two scripts among the scripts a skill runs in place, and says which skills run the repository's `.lokf/scripts/` and that ktl-docent runs only its own. Checked against `SECURITY.md` again, as the note of 2026-10-03 asks. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: `scripts/validate-repository.sh` adds check 11a, which holds ktl-docent's own copies of two sidecar scripts to their templates and runs them as an installer leaves them, and check 11b, which holds the no-Python schema URL to one commit. The smoke test now checks that the docent's scripts come with the install and work in a reader's repository.
* **Changed**: `docs/threat-model.md` now says which skills run the repository's `.lokf/scripts/`, that ktl-docent runs only its own copies of two of them, and that the no-Python schema is read by commit. The concept follows it, and says that the `release` Environment, not the gate, exists in name only without reviewers.
* **Changed**: `skills/ktl-curator/SKILL.md` now keeps only the `username` from `glab api user`, because the whole profile includes the person's email, and the concept says so.
* **Changed**: `skills/ktl-librarian/SKILL.md` now reads the no-Python schema from a commit, not a tag, and answers Snyk's W012 finding, so the concept adds that note. Its W011 paragraph now says, as the skill does, that an entry can neither add a confirmation nor remove one. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: `skills/ktl-sidecar/SKILL.md` now says that ktl-docent runs its own copies of the feedback recorder and the report script, so the copies Step 5 installs serve a person, an earlier ktl-docent, ktl-curator and ktl-librarian.
* **Changed**: Since 0.34.1 the Copilot docent's gap line starts a Miss with the reader's question and says which of two cases it is, and a Disagreement says which version the answer gave, as `ktl-docent-m365.md` states. Where a release has no zip, the concept now says the repository's sidecar has no `.lokf/m365/`, as `docs/m365.md` does.
* **Changed**: The source map now names `skills/ktl-docent/scripts/`, the docent's own copies of two sidecar scripts added in 0.34.2, which no row accounted for. Edited since a person confirmed it; the label says so until the curator looks again.
* **Rewrite**: ktl-docent now runs its own copies of `knowledge-report.sh` and `knowledge-feedback.sh`, never the repository's, names the asker in an entry only when the asker agrees, and labels a retired or edited concept as the report script does. The concept is rewritten from `skills/ktl-docent/SKILL.md` and its references as they now stand, with the skill's new scanner note.
* **Prose**: reworded 4 concept bodies in plain English: the ktl-docent skill, three lines of defence, WikiSkill's loop and the threat model. No fact, link, number or frontmatter changed.
* **Prose**: reworded 21 more concept bodies in plain English, among them repository validation, releasing and the three skill playbooks, with long runs of checks, steps and conditions turned into lists. No fact, link, number or frontmatter changed.
* **Prose**: a full pass over the 25 concept bodies reworded today puts each paragraph and list item on one line, as ktl-librarian writes them, and makes 30 sentences plainer. No fact, link, number or frontmatter changed.

## 2026-10-05

* **Changed**: the skills pin is two values now, `TRUST_LADDER_SKILLS_REF` and `TRUST_LADDER_SKILLS_SHA`, and the release step in `semantic-release.yml` and `scripts/sync-sidecar.sh` each move both, as `docs/releasing.md` says. The page no longer says that check 11 ignores one value.
* **Changed**: `scripts/validate-repository.sh` has twenty-one numbered checks, and checks 11, 12, 15, 18, 19 and 20 now test more, such as the commit pinned beside the skills tag and the `.lokf/uv.lock` the gate installs from. The page now also describes check 16b, and check 12 counts five other scripts under `sh`.
* **Changed**: the row for this repository's own sidecar copies names both values of the skills pin, since check 11 and the preflight now ignore `TRUST_LADDER_SKILLS_SHA` too. Three rows follow `README.md`: `docs/for-the-curious.md` also says who writes the bundle, the README no longer shows the lifecycle diagram, and its pointer for agents is in the Prefer to ask? callout. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: `skills/ktl-curator/references/portability.md` says the key that signs is often a subkey, and names `subkeys` only in GitHub's key listing. The concept said usually, and gave the field to every forge.
* **Changed**: `skills/ktl-docent/SKILL.md` says the scheduled workflow commits `feedback.md` often into a public pull request. The concept said only that the pull request can be public.
* **Changed**: the hand-off now gives the words before and after from the `OK` line of `prose-check.py`, as step 5 of `skills/ktl-prose/SKILL.md` asks.
* **Changed**: the page now names two more refusals of the pen, the commit the skill pin checks, and the conventions run in `refresh`, as `skills/ktl-librarian/references/patch.md` and `.github/workflows/knowledge-librarian.yaml` state. It also says that a scheduled run stops while a pull request the workflow opened is still open, and what the quiet check no longer counts, as `.lokf/scripts/knowledge-report.sh` states. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: the page now says that a scheduled run stops while a pull request the workflow opened is still open, and proposes nothing again that a person declined, as `skills/ktl-sidecar/references/automation.md` states. It also says that the skill pin names a commit beside its tag, which the install step checks and the preflight's `copies` line leaves out of its comparison, as `.github/workflows/knowledge-librarian.yaml` and `.lokf/scripts/knowledge-preflight.sh` state.
* **Changed**: the pen now refuses a patch that would change a person's record in any concept it writes, and a patch that handles more than ten feedback entries. `skills/ktl-librarian/references/patch.md` and the header of `knowledge-apply.py` say so.
* **Changed**: the concept now names the inputs of the label *a source moved since the confirmation*, which `skills/ktl-curator/references/trust-fields.md` lists as `resource`, `sources[].resource` and git history.
* **Changed**: the surface table now says separate jobs, not two jobs, mean the agent never meets a write token, as `SECURITY.md` says. Every other claim still matches `SECURITY.md`, check 10 of `scripts/validate-repository.sh` and `CHANGELOG.md`. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: the concept now names four measures `docs/threat-model.md` added: the skills pin named by commit, the toolkit and parser installed as reviewed, the librarian's three jobs, and the guards on the `earlier` job's reading of pull requests. It also names the pen's check of a person's record and the hand-off written again after the retrieval call. The pen's date now follows `CHANGELOG.md` 0.29.0, and the pen is named as the librarian's only way to write the bundle rather than the bundle's only writer.
* **Changed**: `scripts/sync-sidecar.sh` now also moves `TRUST_LADDER_SKILLS_SHA` to the commit the tag names, as `CONTRIBUTING.md` says.
* **Changed**: three phrases now match `skills/ktl-curator/references/domain-schemas.md`. That page says LOKF has a small vocabulary and never says it is small on purpose, and its signs are many producer-defined keys and a wrong or ambiguous field.
* **Changed**: three claims that no source states are removed: that most readers of a code repository never open Obsidian, that the vault lacks the bundle on mobile, and that the problem showed in the maintainer's own vault. The notes-vault bullet now ends with the reason `docs/obsidian.md` gives, that this keeps the workshop clean.
* **Changed**: the context layer is defined as `README.md` defines it, a governed layer that persists from one task to the next. The open question stays, because neither `README.md` nor any page under `docs/` states which uses KTL is meant for and which it is not.
* **Changed**: the loop now ends as `README.md` says, with the curator reviewing what is new or changed. The README no longer shows `.assets/ktl-lifecycle-loop.svg`, so the concept no longer points at it.
* **Changed**: `docs/wikiskill.md` no longer says the paper's wiki keeps every trace: the paper keeps them, and its wiki's log names the errors that came back. The concept now says the same, and adds what the page now says about the pen's check of a person's record, declined pull requests, the pen's limit of ten feedback entries and the questions the retrieval score leaves out.
* **Changed**: step 2 of the two-vault setup now says what `docs/obsidian.md` says: there is nothing to configure, because the root `index.md` carries the bundle's header. No repository source holds the phrase the concept quoted as the plugins' default.

## 2026-10-04

* **Added**: Accession, a museum's word for an item added to its collection, from `README.md`, which now says so where it describes the registrar.
* **Changed**: Registrar: its quotation of the README carries the README's new gloss on *accession*.
* **Added**: Registrar, the person in a museum who keeps the collection's records, from `README.md`, which now says so where it first names the role.
* **Added**: Sidecar, the `.lokf/` folder beside the code and the role that installs it, from `README.md`, which now says so where it first names it.
* **Added**: Docent, a museum's name for a guide, from `README.md`, which now says so where it first names the docent.
* **Added**: Desk, the README's word for the place where a role does its work, from its section on the registrar.
* **Changed**: ktl-prose skill: rule 3 covers a paragraph past 150 words, rule 9 asks for the literal verb, and the check reports both and a character no reader sees.
* **Changed**: repository validation: check 18 exercises the paragraph, figure-of-speech and unseen-character findings, and check 21 searches every tracked file for a character a reader cannot see.
* **Changed**: threat model: this repository's contract fails on a character a reader cannot see, and ktl-prose's check refuses a rewording that adds one.
* **Changed**: security policy: `SECURITY.md` now says what guards each surface, and that a security fix is published as a patch release. Checked against it again, as the note of 2026-10-03 asks. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: the pen: the README now names it as the registrar for the librarian.
* **Changed**: contributing: `CONTRIBUTING.md` now says to merge this side first, and that a curator's key is added first in a pull request of its own.
* **Changed**: the skill page gives the Golden Rules in brief and keeps their tables, the first run's sweep and the audit's detail in three new references; a run's hand-off reaches its pull request, a quiet week runs no agent, and a note the run reads leaves its stamp. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: the pen also takes the librarian's hand-off, which it cleans and writes nowhere in the bundle, as `references/patch.md` now says.
* **Changed**: check 11 now proves conventions rule 13, check 19 the pen's hand-off and check 20 the quiet check, and the layout tests the wrapper's quiet skip and hand-off; the playbook counts thirteen conventions, eight of them in the Python half.
* **Changed**: the sidecar's references now describe the quiet week, the hand-off's path to the pull request, and the gate's thirteenth convention.
* **Changed**: the threat model adds the librarian's hand-off as a guarded path to the pull request, and conventions rule 13 under human attribution.
* **Changed**: `docs/wikiskill.md` now names conventions rule 13, the hand-off that carries a repeated send-back to the pull request, and the quiet week that bounds a run further.
* **Changed**: an auditor's questions now include whether a confirmed text is the one its person saw, which conventions rule 13 answers.
* **Prose**: Releasing; the sentence on the sync script is split into six; no fact changed.
* **Changed**: WikiSkill's loop and Knowledge Trust Ladder; `docs/wikiskill.md` now names the design KTL and keeps *the bundle* for its corpus and *the wiki* for the paper's, and the concept follows it.
* **Changed**: Three lines of defence; the roles are KTL's and the pages now say so, where they named them after LOKF, the format.
* **Changed**: Threat model; the three repositories that share it are KTL's, not LOKF's.
* **Changed**: Contributing; the sibling repositories are KTL's, as `CONTRIBUTING.md` now says.
* **Changed**: Releasing; the three repositories are KTL's, and the sync script's every-host templates now include one from ktl-sidecar's Step 1.
* **Added**: The pen, the name the README and `docs/for-the-curious.md` give `knowledge-apply.sh`, the librarian's only way to write the bundle.
* **Changed**: Releasing; the sync script now lays down a template a sibling lacks when Step 5 puts it on every host or a copy there needs it, as `scripts/sync-sidecar.sh` and `docs/releasing.md` say.
* **Changed**: Repository validation; check 19 now also holds the pen to a root index shaped by hand, which keeps its `##` sections and its lines that list several concepts.

## 2026-10-03

* **Prose**: Threat model: one sentence split; no fact changed.
* **Prose**: ktl-sidecar skill: one sentence split; no fact changed.
* **Prose**: ktl-docent skill: one sentence split; no fact changed.
* **Changed**: ktl-librarian skill: a refresh starts from the work list, a handled entry moves to the ledger with its question, the pen has eight operations and prints its own format, and `publish` refuses a change to a person's record, as `skills/ktl-librarian/SKILL.md`, `references/patch.md` and `references/scheduled-task.md` now say. Edited since a person confirmed it; the label says so until the curator looks again.
* **From reader feedback**: ktl-librarian skill: step 6 of `skills/ktl-librarian/SKILL.md` names `.lokf/patch.yaml` as the one file the scheduled agent writes, so the skill page no longer lags the wrapper and the question is withdrawn.
* **Changed**: ktl-sidecar skill: Step 5 lays down nine scripts and fourteen files, `knowledge-report.sh` among them and among the three that land regardless; the gate reference covers a removed confirmation and the unattended check, and the automation reference the retrieval score.
* **Changed**: ktl-curator skill: Step 1 quotes `knowledge-report.sh`, lists apart the questions a later confirmation answered and names the confirmed concepts whose source moved, as `skills/ktl-curator/SKILL.md` and `references/trust-fields.md` now say.
* **Changed**: ktl-docent skill: a label comes from `knowledge-report.sh labels`, and a handled entry moves to the ledger, as `skills/ktl-docent/SKILL.md` and `references/feedback.md` now say.
* **Changed**: Threat model: a removed confirmation needs its person, `publish` reads a person's record off the patched tree, the pen refuses to delete a concept a person left a note on, and a handled entry moves to a ledger only programs read, as `docs/threat-model.md` now says.
* **Changed**: Repository validation: twenty checks and nine sidecar scripts, as `scripts/validate-repository.sh` now counts; checks 13, 13a, 19 and 20, the twelfth conventions rule and the layout tests' new cases are described.
* **Changed**: Knowledge sources: the sidecar lays down nine scripts, `knowledge-report.sh` among the fifteen dogfooded copies, and the `docs/wikiskill.md` row follows the page's present sections. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: Three lines of defence: the second line names `knowledge-report.sh`, the gate asks the person behind a confirmation that is removed, and the report lists a confirmed concept whose source moved, as `docs/three-lines.md` now says.
* **Changed**: WikiSkill's loop and the bundle's ladder: the ablation ran on four benchmarks, and the rows and findings name the ledger, the work list, the report script, the removal rule and the retrieval score, as `docs/wikiskill.md` now does.
* **Changed**: Why four skill roles: the registrar's parts include `knowledge-report.sh` at the reader's desk and the curator's, as `README.md` now says.
* **Changed**: Trust label: `knowledge-report.sh` computes the labels, and a concept edited since its confirmation is counted once, as `skills/ktl-curator/references/trust-fields.md` now says.
* **Open question**: Why a registrar role, and why it is not a skill: `README.md` now says the gate ties each confirmation that is added or removed to its person, and names `knowledge-report.sh` as the registrar at the reader's desk and the curator's; this text, which a person wrote, says each new confirmation and names neither.
* **Changed**: Security policy, re-checked against `SECURITY.md` as the curator's send-back of 2026-10-03 asked: the body follows the file section by section and carries qualifiers it had dropped (a *first* reply, harden-runner *in audit mode*, actions pinned *to commit SHAs*, the `release` Environment, *with scope and reproduction*, the gate proving who vouched, not what they read); the word counts are the ones check 10's comment gives. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: Knowledge sources: the issue-template row says both templates name five skills, as the curator's send-back of 2026-10-03 asked, and the plugin row counts five skills, as `README.md` does; the other "four skills" in the bundle follow sources that still say four, with `ktl-prose` as a helper. Edited since a person confirmed it; the label says so until the curator looks again.
* **Curation**: human:noelmcloughlin confirmed 2 concepts (ktl-librarian skill, versioning policy), corrected 1 (Why a registrar role: the title now ends "why it is not a skill", since the README's fifth skill is ktl-prose) and sent 2 back (Knowledge sources: the issue-template row still says "all four skills"; Security policy: check it against `SECURITY.md` again). Two of the three verdicts were the same kind, a skill count the move to five skills left behind, which is worth a line in ktl-librarian's instructions.
* **Changed**: The docent in Microsoft 365 Copilot: the release asset's `<repository>` may be the name `KNOWLEDGE_RELEASE_NAME` sets, as `docs/m365.md` says since #86, and the `atk validate` line quotes the error the page quotes.
* **Open question**: The docent in Microsoft 365 Copilot: Microsoft's page on custom skills (updated 2026-09-04) says the Agents Toolkit takes a skill directory and that `.zip` isn't supported. `skills/ktl-sidecar/references/m365.md` says `atk add skill --from` takes a zip from any path, as checked against the toolkit's source, and this concept follows it. Which holds for the toolkit a reader installs?
* **Changed**: Why the skills live in their own repository: the old repository name is left to `docs/install.md`, which records it; the contract keeps it out of every other file.
* **Changed**: ktl-librarian skill: seven pen operations, with `reindex`, as `references/patch.md` now gives. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: When the built-in vocabulary stops fitting: the description is the catalogue entry, cut to one sentence.
* **Changed**: Hosts and doorways: the description is the catalogue entry, cut to one sentence.
* **Changed**: What Knowledge Trust Ladder is for: the description is the catalogue entry, cut to two sentences.
* **Changed**: Three lines of defence: the description is the catalogue entry, cut to one sentence.
* **Changed**: The docent in Microsoft 365 Copilot: the description is the catalogue entry, cut to one sentence.
* **Changed**: Open the knowledge bundle in Obsidian: the description is the catalogue entry, cut to one sentence.
* **Changed**: Releasing: the description is the catalogue entry, cut to one sentence.
* **Changed**: Why a registrar role: the description no longer says "rather than by an agent", which `README.md` does not say (the curator's send-back of 2026-09-26); the body follows the README's registrar section as of `f1f0d51`, which dropped the two plugins' "levels of checking" and folded the three-lines paragraph under it, and the undated pen is no longer dated. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: The docent in Microsoft 365 Copilot: the limits sentence now gives both sizes the sidecar's `references/m365.md` states, the toolkit's 10 MB app package and Agent Builder's 50 MB zip (the curator's send-back of 2026-09-26); four qualifiers `docs/m365.md` does not state are dropped ("fifth skill", "at the bundle's commit time", "the toolkit's preview", "check 17 word for word").
* **Changed**: Knowledge sources: the rows name `bug_report.md`, `feature_request.md`, `docent.md` and `curator.md` instead of their globs, and `.gitignore` joins the `LICENSE` row (the curator's send-back of 2026-09-26); the skills row counts five playbooks and the references row admits `prose-check.py`; a row for `.markdownlint-cli2.jsonc` and `lychee.toml`, which had none; a note for this pass. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: WikiSkill's loop and the bundle's ladder (was "What WikiSkill says about a knowledge bundle"): `docs/wikiskill.md` was restructured in `f1f0d51` around a part-by-part table, eight findings, and where each design puts programs, models and people; the determinism section and the four gaps it named are gone from the page, so they are gone here.
* **Changed**: Three lines of defence: the second line names `knowledge-apply.sh` as the librarian's only pen and its refusal of a `human:` actor, as `docs/three-lines.md` does since `f1f0d51`, and the README pointer names the section that now holds it.
* **Changed**: gh skill (GitHub CLI): the manual's `--from-local` and its preview notice are carried, the v2.90.0 claim now cites the release notes that state it, and a dependency claim no page supports is dropped.
* **Changed**: LinkML: the class count is dropped; the specification site lists fourteen types and the 0.8.0 schema's `Concept` descendants plus `Person` and `Organization` make fifteen, so the page states neither.
* **Changed**: LOKF toolkit: the 0.8.0 command line's other subcommands and the `[tables]` extra are named, and an unverified claim about upstream `main` is dropped.
* **Changed**: Why four skill roles: the README now names `ktl-prose` as the fifth skill that is not a role and the registrar as toolkit, gate, pen and plugins, and its "in short" summary line is gone since `f1f0d51`.
* **Changed**: Why the skills live in their own repository: five skills, as `README.md`, `docs/install.md` and `plugin.json` now count; two dates and two check numbers no named source states are dropped.
* **Changed**: When the built-in vocabulary stops fitting: the OKF sentence follows the README's wording since `f1f0d51`, and the graph note carries how 0.8.0 and 0.9.0 project an undeclared type, as the librarian's `domain-schema.md` states.
* **Changed**: ktl-prose skill: "the roles lose nothing without it", as the README says, not "the four roles".
* **Changed**: Contributing: one Python script and five skills, as `CONTRIBUTING.md` says; the pull request's *why*, the `ktl-prose` boundary, the sync script's own checks and the "land this side first" condition are carried; two dates and a word count no named source states are dropped.
* **Changed**: Releasing: five skills, as `docs/releasing.md` counts; the title check is its own workflow step; the release asset's name follows `KNOWLEDGE_RELEASE_NAME`; the sync script reports a template a sibling never laid down; the pin is never bumped by hand, the sibling pull request waits for the tag, and the Environment and branch settings are stated, all from `docs/releasing.md`; the Copilot skill is no longer "not yet released", and two dates no source carries are dropped.
* **Changed**: Repository validation: nineteen checks, five skill directories, eight sidecar scripts and four sibling scripts, as `scripts/validate-repository.sh` now counts; checks 18 (`prose-check.py`) and 19 (`knowledge-apply.sh`) are described; the files exempt from checks 16 and 16a are all named; the job's step order follows `validate.yml`.
* **Changed**: Versioning policy: five skills under one tag, as `README.md`, `CONTRIBUTING.md` and `docs/releasing.md` now say, and `publish.yml` is listed as the source for the `v` refusal it carries. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: Security policy: the surface table's fourth row, `prose-check.py`, and "five skills' prose" as `SECURITY.md` now reads, and a report says why a file is exploitable. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: Threat model: `docs/threat-model.md`'s statements on how the agent is chosen and armed, Dependabot and the templates' pins, the Environment's reviewers and `--ignore-scripts`, the curator's refused verbs, the `attestation` job, a gitignored bundle, and the `ktl-prose` guard are carried; the gate description names the one job that reads events whole; a claim about stable section headings and a word count no source states are dropped.
* **Changed**: Code of conduct: "officially represents", as `CODE_OF_CONDUCT.md` says.
* **Changed**: ktl-curator skill: two claims about the KTL Curator plugin that no source carries are replaced by what `trust-fields.md` says; `revision` is left out with no version control too, and records the source's state, as `review-session.md` says; `README.md` and `CHANGELOG.md` are listed for the cadence and the dates.
* **Changed**: ktl-docent skill: evidence-first also covers a concept edited since its confirmation, as `SKILL.md` says; `README.md` and `CHANGELOG.md` are listed for the cadence and the dates.
* **Changed**: ktl-sidecar skill: "missing or broken", as Step 0 says; the sources now list the librarian workflow, `scheduled-task.md` and the preflight, which carry the install step and the `copies` exception, and `CHANGELOG.md` for the dates; the pen's undated arrival is no longer dated.
* **Changed**: ktl-librarian skill: the `refresh` job's `--check-refs` step continues on error and reports in the pull request body, as `knowledge-librarian.yaml` has it; `revision` is left out with no version control too; three undated changes are no longer dated, and two qualifiers no source states are dropped. Edited since a person confirmed it; the label says so until the curator looks again.
* **Open question**: ktl-librarian skill: the scheduled wrapper `knowledge-librarian.sh` lets the agent write only `.lokf/patch.yaml`, and this concept says so, but `skills/ktl-librarian/SKILL.md` step 6 still says the wrapper permits edits under `.lokf/knowledge/`, `knowledge_bundle/` and `.lokf/feedback.md`; the skill page lags the script and is outside the bundle.
* **Changed**: Open the knowledge bundle in Obsidian: the sidecar's `portability.md`, which carries the reconciler, the Windows junction detail and the version, and `CHANGELOG.md`, which dates the retired layout, are listed as sources; a reading date no source records is dropped.
* **Changed**: Hosts and doorways: three workflows and three calls to rewrite on another forge, as the sidecar's `portability.md` counts; a paragraph on an alternative no source records, a "never inside the host's build" claim and a markers detail are dropped; `portability.md` and `CHANGELOG.md`, which carry the matrix and the retired layout's dates, are listed as sources.
* **Changed**: Trust label: the section reference and the reason nothing is scored follow `trust-fields.md`'s wording.
* **Changed**: LOKF: the tools sentence follows the README's wording since `f1f0d51`.

## 2026-10-02

* **Prose**: What WikiSkill says about a knowledge bundle: two sentences split; no fact changed.
* **Added**: ktl-prose skill, the fifth skill, from `skills/ktl-prose/SKILL.md`; re-created after the bundle was restored from main.
* **Added**: What WikiSkill says about a knowledge bundle, from `docs/wikiskill.md`, the new page that reads the paper against this design.
* **Changed**: ktl-librarian skill: the run now reads the curator's verdicts first, caps feedback at ten entries, treats a miss on a covered question as a description defect, and writes the bundle only through `knowledge-apply.sh`; `skills/ktl-librarian/SKILL.md` and `references/patch.md` say so. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: Knowledge sources: the sidecar lays down eight scripts, the apply script and its Python half among the fourteen dogfooded copies, and `docs/wikiskill.md` feeds a new Explanation concept. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: Why a registrar role: `knowledge-apply.sh` is the registrar at the librarian's desk, as the README's fifth-role section now says. Edited since a person confirmed it; the label says so until the curator looks again.
* **Changed**: Threat model: the hardening list gains the librarian's pen, `knowledge-apply.sh`, as `docs/threat-model.md` does.
* **Changed**: Three lines of defence: the independent checker is the generated JSON Schema; the SHACL shapes exist upstream and nothing here runs them, as `docs/three-lines.md` now says.
* **Changed**: ktl-sidecar skill: Step 5 lays down eight scripts and thirteen files, the apply script and its Python half among them.

## 2026-09-26

* **Curation**: human:noelmcloughlin confirmed 5 concepts (ktl-librarian skill, LOKF specification, versioning policy, security policy, knowledge bundle), corrected 3 (Agent Skills specification, OKF specification, AI covenant) and sent 3 back (Why a registrar role: its description says "rather than by an agent", which the README does not; Knowledge sources: name the files covered only by glob and add `.gitignore`; The docent in Microsoft 365 Copilot: Agent Builder's 50 MB zip limit). All three corrections were the same kind: a paraphrase that drifted from its source's wording, adding a qualifier the source lacks ("case-exact", "100 words", `generated` as provenance) or dropping one it has ("in that session", "batched"), which is worth a line in ktl-librarian's instructions.
* **The skill playbooks carry the Snyk W011 acknowledgements.** #83 added a note to the librarian's and docent's `SKILL.md` saying what contains each finding: the scheduled workflow's `publish` job for the librarian reading feedback, and the read-only bundle and scripted feedback entry for the docent's repository fallback. `ktl-librarian-skill` and `ktl-docent-skill` now say so, and the docent playbook gains a typed reference to the threat model it cites.

## 2026-09-25

* **The Copilot playbook says what a tenant without custom skills sees.** `docs/m365.md` and the sidecar's `references/m365.md` record a test in such a tenant: `atk provision` refused `agent_skills` at Microsoft's service, and Agent Builder sent the skill to Copilot Studio, which needs its own licence. `docent-in-m365-copilot` now checks for the preview before the routes, adds the Copilot Studio step, and has two troubleshooting lines for those errors in place of the fallback to Agent Builder.

## 2026-09-24

* **The Copilot playbook names both toolkit flags.** `docs/m365.md` and the sidecar's `references/m365.md` now say `atk add skill` is hidden behind `TEAMSFX_AGENT_SKILLS` in the 1.1.17 release and `ATK_FRONTIER` from the 1.1.18 betas on, and set both. `docent-in-m365-copilot` follows, in its toolkit route and its troubleshooting list. The toolkit route also changes into the project folder, passes `--env dev`, and skips `atk validate`, which rejects `agent_skills` against the v1.8 schema; two troubleshooting lines cover `InvalidProjectError` and that rejection. Both variables are exported for the session, since `provision` packs the skill's files only while one is set.
* **The Copilot playbook follows the reworked `docs/m365.md`.** `docent-in-m365-copilot` now gives the three steps in order, says what a release with no docent zip means, adds the first-answer check and where its gap line goes, and carries the page's troubleshooting list. The build's need for bash and `zip` is new, taken from the builder.
* **Three open questions closed.** `docs/install.md` now says the skills took the `ktl-` prefix in 0.22.0, so the distribution concept states it again. `references/scheduled-task.md` lists the refresh job's install, Node and write-scope steps, closing the librarian playbook's question. Obsidian's settings help confirms that *Excluded files* hides a folder from search, graph view and unlinked mentions, so the Obsidian playbook cites it, and the sidecar's `portability.md` and the docent's `obsidian.md` no longer understate it.
* **Threat model follows its source.** `docs/threat-model.md` and the concept now say the release workflow's `attach` job checks each zip, not one.
* **The bundle follows the Microsoft 365 Copilot docent.** A new playbook, `docent-in-m365-copilot`, derives from `docs/m365.md` and the sidecar's `references/m365.md`: how to get or build the docent's Copilot skill, add it to a declarative agent and keep it current, and why only read-only roles go there. The sidecar, releasing and repository-validation playbooks now describe the `.lokf/m365/` folder, the release workflow's second zip and check 17. The three-lines, domain-schemas, hosts and distribution explanations carry the auditor's planned Copilot form, the reserved Microsoft 365 identity shape, the new portability row and the fourth install route.
* **Sibling sync described.** `scripts/sync-sidecar.sh` brings a sibling repository's template copies and skills pin up to one release and leaves the diff for review; the releasing and contributing playbooks and the source map now say so. `CONTRIBUTING.md` no longer asks for a hand bump of the template's pin or calls the librarian workflow an exception to check 11, so the contributing playbook's open question closes and the concept follows its source again.
* **Curation**: at human:noelmcloughlin's instruction, his four confirmations of 2026-09-09 (knowledge bundle, Agent Skills, OKF and LOKF specifications) are re-dated from 18:30-18:38Z to 16:35:55Z, the commit that recorded them, so they satisfy conventions rule 11. What was confirmed is unchanged.
* **Glossary terms described.** The four glossary terms gain a `description` and their index bullets a summary. The knowledge bundle's is the first sentence of its human-authored definition, word for word, so its `generated` record stays true.
* **Conventions rule 11 reflected.** The repository-validation playbook counts eleven rules and the new time check among check 12's cases, and the librarian playbook says every `at` now comes from `date -u`.
* **Audit: impossible timestamps corrected.** Sixteen `generated.at` values and eight `process:ktl-librarian` verification times were later than the commit that recorded them (local time written as UTC on 2026-09-24, round placeholder times on 2026-09-09 and 2026-09-14). Each now carries that commit's time, the latest moment git attests. No `human:` event was touched.
* **Audit: three body links typed.** `lokf-specification` now `references` the toolkit, the librarian playbook `references` the curator playbook, and the sidecar playbook `hasPart` the Obsidian playbook, the inverse of that playbook's existing `isPartOf`.
* **The bundle follows 0.24.0 and 0.25.0.** The sidecar, librarian, releasing and repository-validation playbooks and the threat model now describe the third sidecar workflow, `knowledge-release.yaml`, which `publish.yml` dispatches to attach the bundle zip, the scheduled librarian's credential slot and `--check-refs` validation, and the gate detail's move into the sidecar's new `gate.md`. The source map lists the release workflow among the dogfooded copies; the rest of the diff was rewording that changed no concept.
* **Two concepts cut back to their sources.** `why-a-registrar-role` drops the four-skill contrast and "or agent", neither of which the README says, closing the curator's open question. `policies/versioning.md` drops an uncited history of the old rule and the reasoning behind one shared tag, keeping the README's conclusion, and dates semantic release to 0.15.0 (2026-09-12) from the changelog instead of 2026-09-14.
* **Reader feedback consumed.** Two docent misses from 2026-09-24. The governance question becomes `explanation/domain-schemas.md`, derived from the curator's and librarian's domain-schema references, including the AI Risk Ontology pointer no concept carried. The DevSecOps question becomes `explanation/intended-uses.md`, a draft placeholder, because no source names KTL's intended uses or non-goals.
* **Curation**: human:noelmcloughlin confirmed 2 concepts (LOKF specification, AI covenant), corrected 1
  (Knowledge bundle's definition), and sent 2 back (ktl-librarian skill, Why a registrar role).
* **Audit**: `playbooks/index.md` had no bullet for the Obsidian playbook, and
  the sidecar playbook linked `hosts-and-doorways` in its body with no typed
  relation; both fixed. Every other check passed - schema, relation targets,
  conventions, the projected graph, and the manual lint pass.
* **README-sourced explanations re-derived.** `why-four-roles`,
  `why-a-registrar-role`, `why-a-distribution-repository` and `glossary/lokf`
  had kept prose no current source carries (an origin story, an adversarial
  review analogy, a single-plugin framing), and missed the run order, the
  plugins' levels of checking and the Claude Code plugin route. Each now cites
  every file it rests on; the registrar concept's open question closes by
  dropping the uncited rename detail.
* **The contract and release playbooks follow #69 and #70.** Check 11 now
  covers the librarian workflow apart from its skills pin, which the release
  commit moves in the template only; checks 3c, 16 and 16a were missing, and
  the count is sixteen, not fifteen.
* **Skill and policy playbooks follow their sources.** The sidecar has seven
  steps and two scripts that land regardless; the curator's report counts
  unsigned confirmations from git history; the librarian consumes feedback
  first; the threat model gains the registrar's pull-request-metadata guard
  and the publish job's exact pathspecs; contributing, security and the
  covenant gain the #60 rules. Two curator open questions close by citing the
  files the claims came from.
* **Source map**: rows for `.claude-plugin/` and `.lokf/curators/`, and the
  dogfooded-workflows row no longer says the librarian workflow omits its
  install step.

## 2026-09-23

* **The docent records a reader's gap without reading the file it goes in.**
  `.lokf/feedback.md` is kept newest first, so adding an entry meant reading
  it, editing it and writing it back, which put other readers' free text
  into the docent's session, held off by prose alone (Snyk W011).
  `knowledge-feedback.sh`, a new sidecar script, does the insertion instead:
  ktl-docent passes its own entry as an argument and never opens the file.
  The guard is the call rather than a rule an agent has to keep, the same
  reason the conventions the librarian kept breaking became a script. The
  preflight reports a sidecar that predates it; check 12a exercises it.
  Nothing changed for ktl-librarian, which still reads them.

* **A scaffolded host installed a librarian that was not in the tag.** The
  librarian template's `TRUST_LADDER_SKILLS_REF` read `v0.21.0`, where the
  skills are named `lokf-*`; its install step clones that tag and copies
  `skills/ktl-librarian`, a path that arrived with the rename in `v0.22.0`.
  Every scheduled run failed there, armed or not. The pin moves to `v0.22.0`,
  and check 15 now reads the pinned tag for the path the step copies - a
  version check alone reported both halves as current.

## 2026-09-19

* **The relation audit moved onto the toolkit's own flag.** `just lokf-check-refs`
  ran a hand-written SPARQL query naming ten predicates, which had drifted
  against the schema and reported an external `source:` or `definedBy:` URL -
  correct usage for both slots - as a dangling target. Both justfiles and both
  registrar workflows now call `lokf validate --check-refs`, so the slot list
  comes from the schema and the gate validates once instead of twice. The two
  plugin repositories had already made this change in their own copies; the
  template was the last holdout, which is what their preflight `copies` line
  was reporting. `references/lokf-toolkit.md` no longer says the recipe runs
  a SPARQL query.

* **Repository renamed to `knowledge-trust-ladder`**, from `lokf-agent-skills`,
  because upstream LOKF now ships its own bundled skills and a third-party
  repository named after the format read as their official home. The bundle's
  `base_iri` moves with it, re-iding all 30 concepts and every typed-relation
  target in one mechanical pass; no `verified` event changed, so nothing a
  person confirmed was touched. Concepts naming the repository in prose, its
  GitHub URL, or the card asset were rewritten by the same pass. The four
  skill names stay as they are: they are installed paths in every host.
  Entries below this day keep the name the project had when they were
  written, as `CHANGELOG.md` does: a log that renames its own past is no
  longer a record of what happened.

* **The README states the architectural claim, and a logo joins the assets.**
  A short section near the top quotes OKF's fourth goal - fields that make a
  corpus trustable "without prescribing any runtime" - and says this is such
  a runtime, then says the domain schemas OKF puts out of scope are in scope
  here by construction, pointing at the curator's domain-schemas page for the
  flag and the recipe. New
  `.assets/knowledge-trust-ladder-logo.svg`, three rungs in the trust
  ladder's own grey, amber and blue, shared byte-for-byte with both plugin
  repositories; `lokf-trust-ladder.svg` renamed
  `trust-ladder.svg`, since the old name now reads as the project's rather
  than the diagram's. The source-map row for `.assets/*.svg` covers both.

* **The README became a front door.** Much the same length - 1,792 words to
  1,864 - and a different shape: the opening
  sentence carried four link-bearing clauses before saying what the project
  does, and the install commands - two code blocks, a prerequisites paragraph
  and the pinning rule - sat in the middle of the narrative. Commands moved to
  a new `docs/install.md`, leaving one `npx skills add` line; the closing
  sections collapsed into one `Read on` table. What the space bought: the
  runtime claim, the context layer the bundle is, and the schema-first order
  of work. The source-map row now names the new page.

* **The logo carries knowledge and trust, not just a ladder.** The first mark
  was three rungs alone: it drew *ladder* and left the other two words to the
  filename. The ladder now rises out of an open book (knowledge, in the
  agent-green of the diagrams' key) and its top rung *is* the check mark in
  the curator's blue - so the mark reads draft, checked, vouched-for from
  bottom to top. Rails lightened to `#A8A69D` so the grey draft rung is not
  read as structure. Every diagram now carries the mark and the wordmark in
  its top-left corner, from one shared definition.

* **The three-lines diagram was keyed against its own legend.** Its bands
  coloured the first line green and the second blue, while the legend the
  other diagrams share reads green for agent work, amber for deterministic
  checks, blue for a named person - so the registrar, a program, sat in the
  person's colour and the curator, a person, sat in the agent's. The bands are
  now neutral panels and each card takes the colour of who acts. It also
  gained the title and legend the rest of the family has.

* **Text that collided with its own box.** A headless-Chrome pass measured
  every `<text>` against the smallest rect containing it: six labels across
  four diagrams overflowed or came within 2px, including one in the siblings'
  two-vaults copy that was hidden behind a card it was painted before. Fixed
  by shortening the labels, widening one card, and correcting the paint order.

* **Assets restacked.** Every diagram's canvas was pure white while its cards
  were tinted, so the largest area was the brightest and the cards read as
  sunken rather than raised. The canvas is now `#E4E1D7` across all seven
  assets, and the faint ink `#888780` is now `#6E6D66`, which also lifts the
  10px grey labels past 4.5:1 - a contrast failure that predated the change.
  The same restack was applied to both plugin repositories' assets.

## 2026-09-18

* **Curation**: unauthenticated session (no `gh` login, so only
  send-back/retire/later were available - no `human:` events written) sent
  back 5 concepts flagged as edited since a prior human confirmation:
  Knowledge bundle, ktl-librarian skill, Why a registrar role, Security
  policy, Versioning policy. Four of the five shared one root cause - the
  concept cited a single `resource` but the disputed detail actually came
  from a different file the librarian had read (a workflow wrapper,
  `scripts/validate-repository.sh`, or a sibling doc) - worth ktl-librarian
  tightening `resource`/`sources` citation discipline rather than
  re-deriving each concept the same way again.

* **Pin check given the publish window**: check 15 required the pin to equal
  the newest released heading, which no publish can satisfy - the heading is
  promoted on merge and the tag created later, so the pin can only name the
  release below it. It now accepts either of the two newest, failing the
  0.19.3 publish is what showed this.

* **Retitle now re-runs the check**: the squash-title check asks the author
  to retitle, but `semantic-release.yml` listened only for the default
  pull-request types, so a title edit fired no run and the check could not
  be cleared. The trigger names `edited`. `playbooks/releasing.md` follows.

* **Tracked resources only**: Rule 5's field notes now say a local
  `resource` must be a path git tracks. A gitignored install path under
  `.agents/` resolves only on the machine holding it, and failed the
  conventions gate in a clean CI checkout.

* **Registrar template least-privilege**: the workflow had no top-level
  `permissions: {}` and left the checkout credential on disk in both
  read-only jobs, while `knowledge-librarian.yaml` and two host copies
  already set the first. Both added to the template and this repository's
  copy, so the gate's jobs opt into scope rather than inherit it.
* **Skills pin held to the release**: the librarian template's
  `LOKF_SKILLS_REF` sat at `v0.9.0` while this repository released `v0.19.2`,
  so every host scaffolded from it installed a librarian ten minor versions
  old. Bumped, and check 15 now holds the pin to `CHANGELOG.md`'s top
  released heading so it cannot fall behind unnoticed.
  `playbooks/repository-validation.md` follows.

## 2026-09-17

* **Wrapper restore made unconditional**: `knowledge-librarian.sh` restored
  `.git/config` and `.git/hooks/` only after a clean agent return, so a
  failing agent or a cancelled job left a poisoned config in the checkout.
  An `EXIT` trap now restores on every way out; the layout tests prove the
  failing and cancelled cases. `playbooks/ktl-librarian-skill.md` follows.
* **Schema fallback pinned**: the no-Python fallback URL in both skills'
  Sources notes, the sidecar README and `references/lokf-toolkit.md` now
  points at the `v0.8.0` tag matching the `lokf` floor, not `main`, which
  has already diverged from it. The librarian's tooling-version step moves
  the pin with the floor.
* **Duplicate-release fix (seventeenth pass)**: two merges to `main` between
  publishes computed the same next version twice, promoting `## [Unreleased]`
  onto a second `## [0.19.0]` heading above the first and orphaning the
  second push's entries. `changelog-release.mjs promote` now folds into the
  top released section, by subsection, when its version carries no tag yet;
  the `plan` job also runs `changelog-release.mjs check` directly, since
  semantic-release skips its own plugins' hooks on a pull request and the
  contract's claim that an empty `[Unreleased]` fails a pull request was not
  true. Check 14 proves both, and repairs the changelog this bug had already
  written twice. `playbooks/releasing.md` follows.
* **Third audit (sixteenth pass)**: the sidecar and contract playbooks and
  the threat model follow the audit's fixes - the sidecar lays down the
  conventions script's Python half, both gates read merges against every
  parent, human `generated` records and only the frontmatter, and rule 10
  keeps the fields the gates read to plain spellings.
* **Conventions script split (fifteenth pass)**: `knowledge-conventions.py`,
  run through `uv run`, takes over the five frontmatter-shape rules (quoted
  `at`, `verified` shape, open questions, duplicate `id`, closed frontmatter)
  with a real YAML parse; the contract and sources playbooks follow.
* **Second audit (fourteenth pass)**: the three lines explanation follows
  its pruned page and the shortened critics page; the trust label and the
  curator and librarian playbooks now say `revision` is proposed for lokf
  0.9.0 and unreleased; the contract playbook adds the id the gate used to
  skip, and the gate's reading of a confirmation whole - a re-dated event or
  a flow-style one counts, a renamed concept does not.
* **Audit follow-up (thirteenth pass)**: the sidecar, curator and docent
  playbooks, the contract and the threat model follow the forge-free gate's
  SSH and subkey support, the linked-bundle and `commit.gpgsign` fixes, and
  the new `prerequisites.md` that puts each preflight line in plain words
  for a person who cannot act on it.
* **Portability work (twelfth pass)**: the contract, the four skill
  playbooks, the threat model, the three lines page and the hosts
  explanation follow their sources - a preflight every skill runs first, a
  forge-free provenance gate, `.lokf/.gitattributes`, three new conventions
  (one file per `id`, lowercase paths, a readable frontmatter block), each
  skill's `compatibility` field, and three identity routes for the curator.
* **Steady-state refresh (eleventh pass)**: twenty concepts re-checked
  against their sources. The librarian, curator and docent skills and the
  trust label now describe `revision`, and the librarian skill no longer
  counts its classes.
* **Releasing** corrected: semantic-release runs with `--dry-run` and
  `@semantic-release/exec` calls the changelog script's `check` and `notes`;
  `publish.yml` compares against the top released heading, not Unreleased.
* **Provenance fixed**: `repository-validation` and `three-lines-of-defence`
  carried a `generated.at` later than the change that wrote them, and now
  carry the time that change merged.
* **Repository validation** follows check 11: the conventions script's
  sixth rule (a commit-shaped `revision` must name a commit holding the
  resource) is proved in a throwaway repository, failing and passing.
* **Three lines of defence** follows the page: the state a confirmation was
  checked against is recorded in `revision` (lokf 0.9.0+), the gate resolves
  a commit hash against the tree, and OKF's adoption of the field
  (knowledge-catalog#437) is the remaining upstream item.

## 2026-09-16

* **Steady-state refresh (tenth pass)**, against the uncommitted working
  tree: fifteen concepts re-checked against their sources and found to
  match (`verified` refreshed), the four re-generated today carry today's
  `generated.at`, and the source map's excluded-files and images rows
  follow `docs/examples/` and the new diagram. `explanation/three-lines-of-defence.md`
  follows the page's renamed closing heading, "What remains to do, and who
  does it". `explanation/index.md`'s hosts-and-doorways bullet
  no longer calls the layout an open question. `.lokf/feedback.md` has no
  entries; `lokf` on PyPI is still `0.7.0`.

* **`explanation/three-lines-of-defence.md` refreshed against a rewritten
  `docs/three-lines.md` and its new `docs/three-lines-critics.md`**: the
  page names The Institute of Internal Auditors in full, cites the 2026
  Statement of Position, places each role in a diagram and ends with what
  remains open and whose it is; the critics page quotes the model's critics
  and the research behind two partial critiques, marked preliminary, with a
  bundle's answer to each and every remaining gap labelled by kind.
  `index.md`, `playbooks/knowledge-sources.md` and `docs/repository-layout.md`
  follow, and the source map's excluded-files row follows `EXAMPLES.md` to
  `docs/examples/docent.md`.

* **`playbooks/ktl-curator-skill.md`, `playbooks/ktl-docent-skill.md` and
  `playbooks/repository-validation.md` follow their skills**: the
  conventions script's fifth rule (a local `resource` must exist), the
  curation policy's `Independent re-check:` and `Evidence first:` switches,
  and that the docent reads the second from the policy alone.

* **`playbooks/ktl-sidecar-skill.md` no longer says "the solo maintainer's
  signing setup"**, matching `references/automation.md` and the registrar
  workflow's comments, which describe the case - the confirming person opens
  the pull request - rather than the person.

## 2026-09-14

* **Maintainer polish after the ninth pass**: the README's tree moved to
  `docs/repository-layout.md` and says *three* repositories, the count the
  ninth pass flagged, and `index.md`, `policies/index.md`,
  `policies/threat-model.md`, `playbooks/releasing.md` and
  `playbooks/knowledge-sources.md` now count the same three.
  `explanation/three-lines-of-defence.md` names the README's renamed section;
  prose counts of LOKF's classes and relations left the README, `docs/` and
  the skills' references, with Rule 3 and `trust-fields.md` still enumerating
  them under check 7.

* **Steady-state refresh (ninth pass)**, against commit `b94a299`.
  `policies/security.md` rewritten to match the slimmed `SECURITY.md`
  (reporting, supported versions, a surface table), and a new concept,
  `policies/threat-model.md`, added for the shared design page
  `docs/threat-model.md` moved it to - hardening, the `human:` attribution
  gate, prompt-injection guards - keeping that page's section headings
  stable since the other three repositories deep-link them.
  `playbooks/knowledge-sources.md` and `playbooks/repository-validation.md`
  updated to match; `index.md` and `policies/index.md` gained the new
  concept's bullet. Flagged, not fixed (outside this skill's `.lokf/`-only
  scope): `README.md`'s docs-layout listing still says "four repositories
  release" where the same commit corrected `docs/releasing.md` itself to
  "three". See `playbooks/knowledge-sources.md`'s note for detail.

* **Steady-state refresh (eighth pass)**, against the two commits landed since
  the seventh pass. Twelve concepts re-checked against their current sources
  and found unchanged (content matches; `verified` refreshed only):
  `explanation/why-four-roles.md`, `why-a-registrar-role.md`,
  `why-a-distribution-repository.md`, `glossary/lokf.md`, `glossary/okf.md`,
  `glossary/trust-label.md`, `glossary/knowledge-bundle.md`,
  `explanation/hosts-and-doorways.md`, `playbooks/open-bundle-in-obsidian.md`,
  `playbooks/ktl-sidecar-skill.md`, `playbooks/ktl-docent-skill.md`,
  `playbooks/ktl-librarian-skill.md`. **Orphan fixed**:
  `playbooks/knowledge-sources.md`'s dogfooded-workflows row had no entry for
  `.lokf/scripts/knowledge-conventions.sh` (added earlier today), now listed
  alongside `knowledge-librarian.sh` as byte-identical to its template.
  `.lokf/feedback.md` had no entries.

* **`playbooks/repository-validation.md`**: check 11 added (template copies
  identical, `knowledge-conventions.sh` exercised), the sibling count corrected
  to the two plugin repositories, and actionlint's explicit paths noted.
* **Steady-state refresh against this session's uncommitted repository
  changes**: `CONTRIBUTING.md` was trimmed to a checklist, its release
  process and commit-signing walkthrough moved to two new pages,
  `docs/releasing.md` and `docs/signing-commits.md`; a third new page,
  `docs/three-lines.md`, maps the four-skill-plus-registrar cast onto the
  Three Lines Model; `validate.yml` gained an action-pinning check;
  `scripts/validate-repository.sh` gained checks 9/9a (the paths sibling
  repositories deep-link into, and completeness when they're cloned
  alongside) and 10 (a 1000-word budget on `CONTRIBUTING.md`); `README.md`
  gained a section pointing at `docs/three-lines.md`.
  `playbooks/contributing.md` rewritten to match the trimmed file, its
  Code-of-conduct/AI/Releasing sections, and the new `docs/` links.
  `policies/versioning.md` re-sourced from `CONTRIBUTING.md` to
  `docs/releasing.md` and rewritten: its qualitative patch/minor/major
  definition ("does not materially change expected behaviour") no longer
  exists anywhere in the repository, superseded by the Conventional-Commits
  table `docs/releasing.md`/`playbooks/releasing.md` already state - the
  2026-09-10 human confirmation left standing, per rule, since the concept
  was not human-*authored*. `playbooks/releasing.md`'s stale
  `CONTRIBUTING.md` citation repointed to `docs/releasing.md`.
  `playbooks/repository-validation.md` gained the new action-pinning check
  and, closing a pre-existing gap this pass found (checks 6-8 were never
  described either), the full ten-check enumeration. **Added**
  `explanation/three-lines-of-defence.md` for the new page, linked from
  `why-four-roles.md` and `why-a-registrar-role.md` via `about`.
  **Orphan sweep**, also fixing two pre-existing gaps unrelated to this
  diff: `explanation/index.md` was missing a bullet for
  `why-a-registrar-role.md` (present in the root `index.md` and in `log.md`
  since 2026-09-10, never added here), and its first bullet's title had
  drifted from the concept's own ("Why four roles" vs "Why four skill
  roles"); both fixed. `index.md` gained the new explanation's bullet.
  `playbooks/knowledge-sources.md`: the `CONTRIBUTING.md` row updated, two
  new rows added for the `docs/` pages, and a run note added. `lokf` on
  PyPI is still `0.7.0` (checked via PyPI's JSON API; `uv pip index` is
  still not a subcommand here), matching the sidecar's floor - no bump.
  `.lokf/feedback.md` has no entries. Not re-checked this pass: concepts
  whose resource is untouched by this diff.

* **Two reference concepts corrected** on a librarian pass over the whole
  repository. `references/linkml.md` still said the vocabulary it describes
  has fourteen classes - the same stale count fixed in Rule 3 earlier today -
  and named no way to validate an extension; it now says fifteen and points
  at `lokf validate --schema` and the recipe. `references/lokf-toolkit.md`
  described `lokf validate` without the `--schema` flag the recipe rests on.
  `lokf` on PyPI is `0.7.0`, matching the floor; `.lokf/feedback.md` is empty.

* **Steady-state refresh**, against branch `docs/domain-schema-extension`
  (uncommitted): reframed the domain-schema-extension material added this
  session - `skills/ktl-librarian/references/domain-schema.md` now states
  the recipe (pin the core schema, write a domain schema, name the class
  exactly, wire `--schema` in) without the validator-internals digression or
  the two citations of a named consumer project the first draft carried.
  `playbooks/ktl-librarian-skill.md` gained a paragraph on it; re-verified,
  no change: `playbooks/ktl-curator-skill.md`. **Correctness bug fixed:**
  Rule 3 in `skills/ktl-librarian/SKILL.md` listed fourteen classes,
  omitting `Role`, against `README.md`/`docs/for-the-curious.md`'s fifteen -
  the open question this concept carried since 2026-09-13. Confirmed against
  the raw schema (fifteen concept classes, `Role` among them), fixed Rule 3,
  closed the question. `playbooks/knowledge-sources.md`: run note added.
* **Curation-policy table: how a row binds to a class is now stated.**
  `ktl-curator/references/review-session.md` defined the template but not
  the match. The KTL Curator plugin, which implements this document, read
  it literally, so the template's own prose rows ("Glossary terms",
  "people") bound nothing. The skill now states the tolerant match - spaces
  and plural form ignored - and `playbooks/ktl-curator-skill.md` records it.
* **The curator skill now reads a host's domain schema too**, closing the
  asymmetry the `ktl-curator` plugin's bundle raised as an open question:
  the librarian's Rule 3 widened its class list from `.lokf/justfile`'s
  `--schema`, while the curator still counted vocabulary fit against the
  fifteen built-ins, so a host with a domain schema saw every domain class
  reported as a misfit for good. `references/trust-fields.md` states the
  widening (read the file; no toolkit, as everywhere else in Step 1), the
  label becomes "doesn't fit the known vocabulary" as the plugin already
  words it, and `SKILL.md`, `references/domain-schemas.md` and the
  librarian's `references/domain-schema.md` (step 5: the skills need no
  telling, the plugins do) follow. `playbooks/ktl-curator-skill.md` records
  it.

## 2026-09-13

* **Steady-state refresh** (librarian pass, no feedback pending), after a
  `ktl-sidecar` health check that found nothing to repair here. Withdrawn:
  the third pass's additions that described commit `312190e`, namely the
  sidecar's *refresh* mode and `automation.md`'s GPG-or-SSH and
  required-checks-off text (`playbooks/ktl-sidecar-skill.md`, and the
  `index.md` bullet), the **Drift** audit heading and `Role` in Rule 3
  (`playbooks/ktl-librarian-skill.md`), and `SECURITY.md`'s "documented
  once, here" paragraph (`policies/security.md`, which now cites the
  librarian-PR wrinkle to `automation.md`, where this tree states it). That
  commit is on the unmerged branch `update`, not in the checked-out
  `skills/`. `playbooks/ktl-librarian-skill.md` is `status: draft` again
  with an open question: `README.md` counts fifteen LOKF classes, Rule 3
  lists fourteen. Re-verified, no change: `explanation/why-four-roles.md`,
  `explanation/why-a-distribution-repository.md`, `glossary/lokf.md`.
  `playbooks/knowledge-sources.md`: run note added.

* `playbooks/knowledge-sources.md`: the `docs/` row now covers the new
  `docs/obsidian.md` - the README's Obsidian section, moved out as a page of
  its own with the two-vaults picture - and names the two files it must agree
  with. `explanation/why-a-registrar-role.md`: the "extensions of the skills'
  output" sentence is now cited to `docs/obsidian.md`, where it lives. No
  other concept changed: the README polish moved emphasis and order, not
  facts.

* **Steady-state refresh** (librarian pass, no feedback pending), against the
  commits since `3399203` and this session's uncommitted `README.md` (three
  more `.assets/` images, one sentence on the plugin READMEs). Content
  corrected or extended: `policies/security.md` (`main` is protected but not
  by a merge gate - required status checks deliberately off; the template's
  `validate`/`provenance` jobs never run on the librarian's own PR; a
  consumer's `SECURITY.md` links here rather than restating; the closing
  "branch protection" claim replaced by review-before-merge, as `SECURITY.md`
  now says), `policies/versioning.md` (tags carry the `v`, changelog
  headings never do), `playbooks/contributing.md` (required checks off; sign
  your commits), `playbooks/releasing.md` (the `v` the cross-check strips),
  `playbooks/ktl-librarian-skill.md` (the new **Drift** audit heading, and
  `Role` restoring the fifteenth class), `playbooks/ktl-sidecar-skill.md`
  (the new *refresh* mode; `automation.md`'s GPG-or-SSH signing, its advice
  against required status checks, and its "Keeping a host's copies in step"
  section; the Step 6 handoff line on a host's `SECURITY.md`) and
  `explanation/why-a-registrar-role.md` (the plugins are extensions of the
  skills' output, not plugins for a vault in general). Re-verified, no
  change: `explanation/why-four-roles.md`,
  `explanation/why-a-distribution-repository.md`, `glossary/lokf.md`,
  `playbooks/open-bundle-in-obsidian.md`. `playbooks/knowledge-sources.md`:
  the dogfooded-workflows row no longer claims byte-identity - this
  repository's `knowledge-librarian.yaml` deliberately omits the template's
  "Install the pinned ktl-librarian skill" step, since it publishes the
  skills it uses - and a run note added. **Drift audit:** that omission plus
  a two-line comment is the only difference; `knowledge-registrar.yaml`,
  the wrapper and the justfile match their templates. `lokf` on PyPI is
  still `0.7.0`, matching the floor.

* **Steady-state refresh** (librarian pass, no feedback pending): re-verified
  `playbooks/ktl-sidecar-skill.md`, `explanation/hosts-and-doorways.md`,
  `playbooks/open-bundle-in-obsidian.md`, `explanation/why-four-roles.md` and
  `explanation/why-a-registrar-role.md` against `skills/ktl-sidecar/SKILL.md`
  and the compacted `README.md` from this session's "For the curious" move
  and prose-compaction pass. All five already matched - no content changed,
  only each concept's own `process:ktl-librarian` `verified` event, the two
  hosts-and-doorways/open-bundle-in-obsidian concepts gaining their first
  one. `playbooks/knowledge-sources.md` gained its own `docs/for-the-curious.md`
  row (added this session) and its `generated`/`verified` refreshed to match.
  `glossary/knowledge-bundle.md` was not re-checked - `templates/README.md`'s
  wording tweak this session didn't touch what the term means.

* **The visible layout is retired; one layout, the doorway by default.**
  Hand-edited in session alongside the `ktl-sidecar` change, not a librarian
  run - the librarian's next pass re-verifies. `playbooks/open-bundle-in-obsidian.md`
  and `explanation/hosts-and-doorways.md` rewritten (`generated` refreshed,
  their process `verified` events dropped, since the text they checked is
  gone): the bundle is `.lokf/knowledge` on every host, `knowledge_bundle` a
  link beside it; an Obsidian user keeps two vaults - the workshop they have,
  and the bundle opened as its own vault through the link - and the bundle is
  never laid down as a real folder inside a vault, because a day of use in the
  maintainer's own vault showed the exhibition leaking into the workshop's
  link suggestions, quick switcher, graph and search (Obsidian's *Excluded
  files* only makes that less noticeable). The playbook keeps the 1.13.7
  reconciler findings and now names the cost of linking a repository's bundle
  *into* a vault; the explanation records the 2026-09-12 attempt, its cost,
  and what the reversal keeps (dual pathspecs, plugin auto-detection, junction
  guidance). `glossary/knowledge-bundle.md` (`generated` refreshed; its human
  confirmation of 2026-09-09 stands, so the curator will show it as edited
  since) no longer claims "three pictures": a bundle is a folder of notes
  opened as its own vault, or, at a cost, a folder inside a vault or a whole
  vault. `playbooks/ktl-sidecar-skill.md` (`generated` refreshed) drops the
  Step 0 layout decision; `playbooks/ktl-librarian-skill.md` (`generated`
  refreshed) restates the second-name rule without the visible layout.
  `index.md`'s two TOC lines follow.
* **Later the same day.** The names of the maintainer's private projects were
  removed from this bundle's notes and from this log: the family this bundle
  describes is the four skills and the two Obsidian plugins, and no host
  outside it is a reference. `README.md`'s Obsidian section was cut back to the
  value of the pairing - Obsidian optional, the exhibition as the workshop's
  output - and the mechanics it carried (what the file reconciler does with a
  link, the second vault, the linked-in arrangement and its cost) moved to
  `ktl-sidecar/references/portability.md`, so that
  `playbooks/open-bundle-in-obsidian.md` derives from a source that states them.
  Every passing mention of Obsidian in the skills and templates now says it is
  optional. `README.md`'s "For the curious" moved to `docs/for-the-curious.md`,
  mirroring the plugin READMEs (`playbooks/knowledge-sources.md` lists it), and
  duplicated prose was compacted in the README, the sidecar skill's Steps 2 and
  6, `portability.md` and this bundle's `open-bundle-in-obsidian.md`, whose
  history section now defers to `explanation/hosts-and-doorways.md`.

## 2026-09-12

* **Steady-state refresh against the security-hardening pass** (uncommitted
  at the time of this run: 19 files touched, none of them `.lokf/`).
  `policies/security.md` rewritten from the current `SECURITY.md`
  (`generated`/`verified` refreshed): harden-runner now runs on every
  workflow that installs packages or runs third-party/agent code, not only
  `validate.yml`/`publish.yml`; a new `## human: attribution is a claim, not
  a credential` section records `knowledge-registrar.yaml`'s `provenance`
  gate, ktl-curator's `gh api user`-only identity rule, its refusal to run
  unattended, and the optional `attestation` job; the blast-radius paragraph
  now correctly attributes boundary enforcement to the privileged `publish`
  job (re-deriving the allow-list from the patch itself on a clean
  checkout) rather than the wrapper script, and records the wrapper's new
  `.git/config`/`.git/hooks/` snapshot-and-restore and its checks moving
  into a `main()` called last. `playbooks/ktl-docent-skill.md` and
  `playbooks/ktl-librarian-skill.md` (`generated`/`verified` refreshed on
  both) gained the docent's new never-repeat-a-secret guard and the
  librarian's own scheduled-run-only caveat on the tooling-version check,
  respectively. `playbooks/releasing.md` (`generated`/`verified` refreshed)
  gained the `env:`-var injection-hardening note on `publish.yml`'s two
  version checks, and a fact from a previously unlisted source,
  `.releaserc.json`: the release-rule mapping is the Angular preset's
  defaults plus one addition, `security:` -> patch. `knowledge-sources.md`'s
  source map gained a row for `semantic-release.yml` /
  `changelog-release.mjs` / `.releaserc.json`, none of which had one.
  Re-verified without body changes (`verified` refreshed only, confirmed
  still matching their current, unchanged-by-this-pass resources):
  `playbooks/ktl-sidecar-skill.md`, `playbooks/open-bundle-in-obsidian.md`,
  `playbooks/contributing.md`, `policies/versioning.md`,
  `explanation/hosts-and-doorways.md` (its first `verified` event),
  `explanation/why-a-distribution-repository.md`,
  `explanation/why-a-registrar-role.md`, `explanation/why-four-roles.md`,
  `glossary/lokf.md`, `glossary/okf.md`, `glossary/knowledge-bundle.md`.
  `.lokf/feedback.md` held no real entries (its unfilled template only), so
  nothing was consumed. `lokf` on PyPI is still `0.7.0`, matching this
  sidecar's floor - no bump needed. Not re-checked this run: the policy
  concepts whose resources this pass never touched
  (`policies/ai-covenant.md`, `policies/code-of-conduct.md`), the two
  concepts sourced from `skills/ktl-curator/` (`playbooks/ktl-curator-skill.md`,
  `glossary/trust-label.md`), `playbooks/repository-validation.md`, and the
  seven external `Reference` concepts - none of their resources appear
  among this pass's changed files, so they were left as last verified.

* **Semantic-release, hardened - version and changelog only** (maintainer
  decision): `playbooks/releasing.md` rewritten (`generated`/`verified`
  refreshed). `semantic-release.yml`'s `release` job, behind the `release`
  GitHub Environment, computes the next version from Conventional Commits on
  every push to `main`, but only ever runs semantic-release `--dry-run` -
  `gh skill publish` stays this repository's one tag creator, so nothing here
  writes, commits, tags, or publishes on the tool's own initiative. A plain
  shell step reads the dry run's computed version, promotes `CHANGELOG.md`'s
  `## [Unreleased]` section itself, and commits directly. `publish.yml` gains
  a cross-check: the maintainer's typed version must match what got
  promoted, or the run fails before touching the registry.

* **KTL Registrar named** (maintainer decision): `explanation/why-a-registrar-role.md` (`generated` refreshed),
  `playbooks/ktl-librarian-skill.md`, `playbooks/open-bundle-in-obsidian.md`,
  and `playbooks/knowledge-sources.md` name the plugin and its
  repository `obsidian-ktl-registrar`. The `diataxis.md` actor the librarian
  leaves alone reads `ktl-registrar/<version>`.
  `glossary/knowledge-bundle.md` (`generated` refreshed) now records the
  README's three pictures for the bundle - the librarian's *catalogue*, the
  museum's *exhibition* as the hall visitors are shown into, and the
  *workshop* of sources both stand against - after the README's opening
  section was made to say that its catalogue and its exhibition are the same
  folder.
* **Corrected `playbooks/open-bundle-in-obsidian.md`** (rewritten, `generated`
  refreshed): it now states the one supported route - open `knowledge_bundle`
  *itself* as a vault - and records why the repository-root route cannot
  work, citing Obsidian's help on symbolic links ("ignores a symlink ... from
  one folder in the vault to another folder in the same vault") and its
  dot-folder rule. The two companion plugin READMEs had claimed otherwise;
  both were corrected the same day. Added the supported reverse direction
  (linking a repository's bundle *into* a personal vault). Source:
  `skills/ktl-sidecar/SKILL.md` Step 2, whose symlink paragraph was
  rewritten to match.
* **Re-verified** `playbooks/ktl-sidecar-skill.md` against the updated
  router (Step 5 heading and Step 6 wording changed, step list unchanged) -
  `verified` timestamp refreshed only. Not a full steady-state sweep.
* **Second pass, same day**: `playbooks/open-bundle-in-obsidian.md` rewritten
  again after the maintainer asked for the architecture, not the Obsidian
  community's habits, to lead. The symlink rule is now stated from Obsidian
  1.13.7's own file reconciler (`reconcileSymbolicLinkCreation`, read from the
  installed application bundle): a link is skipped when its resolved path
  equals, contains, or lies inside a folder already being watched, the vault
  root included - so the doorway opened *as* a vault works exactly as Step 2
  intends (the maintainer's own vault does this daily), and a host-root
  vault merely does not list it, which for a notes-vault host is the property
  that keeps the sidecar safe inside the vault. Added the Windows junction
  (`mklink /J`, no elevated rights) and the OneDrive note (syncs neither
  symlinks nor junctions; no rule against dot-folders) to the playbook,
  `skills/ktl-sidecar/SKILL.md` Step 2, and `references/portability.md`.
  Added `explanation/hosts-and-doorways.md` (`status: draft`, with open
  questions for the maintainer): the two-name rule (`.lokf/knowledge` for
  tools, `knowledge_bundle` for people, one of them a link) and the proposal
  to let a vault or shared-drive host make the visible name the real folder.
* **Third pass, same day - the proposal adopted**: the maintainer asked for
  the recommended fixes to be implemented. `skills/ktl-sidecar/SKILL.md`
  Step 0 now decides the layout by host (code repository: hidden real folder,
  visible doorway link; notes vault or shared folder: visible real
  `knowledge_bundle/`, `.lokf/knowledge` as the tools' link), with Steps 1, 2,
  3, 5 and 6 marked where the visible layout differs; the wrapper script and
  both workflow templates name the bundle under both names (a git pathspec
  never traverses a symlink; `git add` refuses an empty pathspec, hence a
  guard), the registrar triggers on `knowledge_bundle/**`, and the justfile
  gained `just lokf-link`. `skills/ktl-librarian/SKILL.md` gained the
  layout note and a rule to leave KTL Registrar's Obsidian affordances
  (`<!-- lokf:related -->` blocks, `diataxis.md`) alone. Updated
  `explanation/hosts-and-doorways.md` (proposal → adopted, open questions
  resolved), `playbooks/open-bundle-in-obsidian.md` (visible-layout section),
  `playbooks/ktl-sidecar-skill.md` (Step 0 decision) and
  `playbooks/ktl-librarian-skill.md` (also corrected "14-class" to the
  schema's 15, matching `README.md`'s earlier fix). `templates/README.md`
  and this sidecar's `README.md` explain the layout in one sentence.
* **Fourth pass - the vault-in-a-subfolder host, and layout tests.** `ktl-sidecar` Step 0
  gained the case of a vault one level below the repository root (the maintainer's
  own notes vault, `vault/` here): the real folder goes inside the vault,
  `vault/knowledge_bundle/`, the link is `.lokf/knowledge -> ../vault/knowledge_bundle`, the
  justfile's new `visible` variable names that path for `just lokf-link`, and Step 5's three files
  name it in place of `knowledge_bundle`. `explanation/hosts-and-doorways.md` gained the table row
  and the note that `scripts/test-sidecar-layouts.sh` now pins both layouts - the wrapper's
  boundary check, both workflows' pathspecs, and the recipe - from the repository-contract check;
  `playbooks/open-bundle-in-obsidian.md` and `playbooks/ktl-sidecar-skill.md` say the same in a
  clause. The README's Obsidian section now states the two-name rule outright and names the vault
  the workshop and the bundle the exhibition. `explanation/why-a-registrar-role.md` no longer files
  KTL Curator under the registrar or calls the plugin a curator: KTL Registrar is the registrar in the
  editor, KTL Curator is the person's assistant, and the curator is always a person.
* **Vocabulary**: `glossary/knowledge-bundle.md` now records the museum synonyms the READMEs
  use - the bundle is the *exhibition*, a concept an *exhibit*, the sources or notes the
  *workshop* - so the three words are defined once, at the term of record.

## 2026-09-11

* **`knowledge_bundle` symlink added to `ktl-sidecar` Step 2**: a third
  root-level pointer, alongside `llms.txt` and the README aside - `ln -s
  .lokf/knowledge knowledge_bundle`, a visible entry point for humans and
  their tools, chiefly Obsidian's "Open folder as vault," which like most OS
  folder pickers hides dot-directories by default. `templates/gitignore` now
  excludes `.obsidian/`, which Obsidian writes through the link into the real
  `.lokf/knowledge/.obsidian/` when used as a vault. Added
  `playbooks/open-bundle-in-obsidian.md` and refreshed
  `playbooks/ktl-sidecar-skill.md`'s Overview (Step 2 now three
  additions, not two). Re-verified `glossary/knowledge-bundle.md` and
  `playbooks/repository-validation.md` against their now-touched resources -
  no body drift, `verified` timestamps only. This repository's own bundle
  gained the symlink too, plus matching excludes in
  `.markdownlint-cli2.jsonc`, `lychee.toml`, and the `codespell` step so the
  aliased files aren't linted/checked twice - those two config files stay
  outside the bundle, per the existing convention noted in
  `playbooks/knowledge-sources.md`. Targeted pass, not a full steady-state
  sweep - concepts untouched by this change were not re-checked this run.

## 2026-09-10

* **`knowledge-validate.yaml` renamed to `knowledge-registrar.yaml`**: at a
  maintainer's request, so the CI gate that keeps bundle records well-formed
  (never judging their truth) is named for the registrar role it actually
  performs, matching `explanation/why-a-registrar-role.md`. Renamed the
  dogfooded workflow and its byte-identical template counterpart under
  `skills/ktl-sidecar/templates/github/`, and updated every
  cross-reference across the four skills' `SKILL.md`/`references/` files,
  `.github/dependabot.yml`, `explanation/why-a-registrar-role.md`, and this
  file's own source-map row. Historical `log.md`/source-map entries that
  named the old workflow stay as they were, describing what it was called
  at the time.

* **Feedback consumed - Disagreement fixed**: ktl-docent flagged that
  `explanation/why-four-roles.md`'s title/description read as the total
  count of roles, while `README.md`'s own headers ("Four roles, three lines
  of the poem" / "The fifth role, which is not a skill") name five roles in
  total, four of which are skills. Retitled the concept "Why four **skill**
  roles rather than one skill", reworded its description, and added a short
  paragraph naming both the source headers and `explanation/why-a-registrar-role.md`
  explicitly. Updated `knowledge/index.md`'s matching bullet.

* **Curation**: `human:noelmcloughlin` confirmed 5 concepts this session -
  `policies/security.md`, `explanation/why-a-registrar-role.md`,
  `playbooks/knowledge-sources.md`, `policies/ai-covenant.md`,
  `policies/versioning.md` - each cleared `status: draft`, gained a `verified`
  event, and a proposed `stale_after` review date (2027-03-10 for
  `policies/security.md`, given how fast its CI-security content is moving;
  2027-09-10 for the rest). `policies/security.md`'s `## Open questions`
  entry (about `SECURITY.md`'s own prose lagging the actual two-job workflow
  split) was cleared - the person confirmed the gap is real and the
  concept's claim, not `SECURITY.md`'s prose, reflects current behaviour;
  fixing `SECURITY.md` itself remains outside this skill's scope.

* **`policies/security.md` refreshed** to describe `knowledge-librarian.yaml`'s
  new two-job, least-privilege split (commit `17d8f3a`): the agent runs
  `contents: read` with no persisted credentials, and only a separate
  agent-free `publish` job holds the write scope; enforcement of the bundle
  write-boundary moved into `.lokf/scripts/knowledge-librarian.sh` itself
  (non-zero exit on a stray path), rather than a dedicated workflow step.
  `SECURITY.md`'s own prose still asserts the prior single-job design in one
  place - recorded under this concept's `## Open questions` since fixing that
  file is outside this skill's `.lokf/`-only scope.
* **Added `explanation/why-a-registrar-role.md`**: `README.md` gained a
  substantive new section describing a "registrar" role - keeping bundle
  records well-formed and provenanced - filled by tooling (the `lokf`
  toolkit, CI) or, for hand-edited bundles, two companion Obsidian plugins
  (KTL Registrar, KTL Curator), rather than by a fifth skill. No prior
  concept captured this; `explanation/why-four-roles.md` gained a `relatedTo`
  link to it.
* **Steady-state refresh**: re-verified `playbooks/releasing.md`,
  `playbooks/ktl-librarian-skill.md`, `playbooks/ktl-docent-skill.md`,
  `playbooks/repository-validation.md`, and `policies/versioning.md` against
  their current sources - no drift found - and refreshed each concept's own
  `process:ktl-librarian` `verified` event (human `verified` events left
  untouched). `lokf` on PyPI is still `0.7.0`; the sidecar's `>=0.7.0` floor
  needs no bump.

## 2026-09-09

* **`SECURITY.md` gained an "Interactive use: scope is advisory, not
  enforced" section**: prompted by a user question about `npx skills add`'s
  generic "runs with full agent permissions" warning. Boilerplate - the
  Agent Skills format has no permission manifest - but it surfaced a real
  gap: a skill's `Scope:` line is prose, checked only by the scheduled
  workflow's write-scope enforcement; interactive sessions rely on a person
  reviewing what the agent changed. Updated `policies/security.md` to match.
* **Security hardening on `knowledge-librarian.yaml`**: prompted by an
  external security scan of the scaffolding templates. Two findings: (1,
  MEDIUM) the agent step let a repository variable's *content* become the
  executed shell command (`bash -c "${KNOWLEDGE_LIBRARIAN_CMD}"`), wider than
  needed under that job's `contents: write` scope - fixed by removing that
  variable entirely; the workflow now always invokes the pinned, reviewed
  `.lokf/scripts/knowledge-librarian.sh` directly, and `AGENT_CLI` only
  selects which agent runs, never what command runs. (2, LOW) the wrapper
  script's contract - only touch `.lokf/knowledge/`, never run git - was
  advisory, unenforced - fixed by a new "Enforce the agent's write scope"
  step that fails the job before any commit if anything else changed
  (excluding `.lokf/uv.lock`, a known `uv sync` side effect). Applied to the
  scaffolding template and this repository's dogfooded copy in lockstep (both
  `.yaml` and `.sh`), plus `SECURITY.md`, `scheduled-task.md`, and
  `automation.md`. Updated `policies/security.md` to match.
* **Curation**: human:noelmcloughlin confirmed 5 concepts (the ones most
  relied-upon and least-checked per the Step 1 report): `references/agent-skills-specification`,
  `references/okf-specification`, `glossary/knowledge-bundle`,
  `playbooks/ktl-librarian-skill`, `references/lokf-specification`. Sent 0
  back, corrected 0, retired 0. One evidence-citation error caught mid-session
  (a quote presented as coming from a single "Section 1" of
  `ktl-librarian/SKILL.md` was actually a synthesis drawn from three separate
  places in the file) - re-quoted properly and the underlying claim held; a
  one-off slip in how evidence was presented, not a defect in the concept or
  a pattern worth changing ktl-librarian's instructions over.
* **AI_COVENANT.md gained a "Repository-Owned Agent Automation" section**:
  raised by the maintainer after noticing this same run's own commit carried
  an AI co-authorship trailer the covenant already discourages (fixed by
  amending that commit). The deeper gap: the covenant's model is a person
  drafting with AI help then submitting, but `ktl-librarian` (scheduled or
  interactive) and `ktl-curator` both have an *agent* executing the actual
  commit/PR. The scheduled workflow already gets this right by convention
  (bot identity, no trailer, mandatory review) but the convention was never
  written down. New section makes it explicit: bot-or-maintainer identity
  with no trailer either way, every change lands as a human-reviewed PR
  (never an agent's own approval), and a curator-recorded human verdict must
  trace to that person's real-time answer to that specific item. Updated
  `policies/ai-covenant.md` to match.
* **Steady-state refresh, second pass**: re-verified all 18 internal-resource
  concepts (no drift - the two upstream commits since the prior pass,
  `e6d5633` and `b743c84`, were prose tidying with no facts this bundle
  asserts) and, for the first time since bootstrap, fetched and checked all
  seven external Reference concepts against their live sources - all still
  accurate. Details and the one loose end (an unconfirmed GitHub CLI version
  number) are in `playbooks/knowledge-sources.md`.
* **Correctness bug found and fixed**: a same-day commit (`e6d5633`) had
  flipped the `sameAs` typed-relation's RDF predicate from the correct
  `schema:sameAs` to `owl:sameAs` in `ktl-librarian/SKILL.md`'s Golden Rule
  4 - confirmed wrong against both the LOKF specification site and the raw
  `lokf.yaml` schema. Not just documentation: `just lokf-check-refs`'s SPARQL
  query filtered on the same wrong predicate in both `.lokf/justfile` and the
  `ktl-sidecar` template it's copied from, so a `sameAs` relation's
  target would have silently never been checked for existing. Fixed all
  three; `lokf validate` and `lokf-check-refs` still pass.
* **Tooling floor bumped**: `lokf` reached 0.7.0 on PyPI (floor was
  `>=0.5.0`, already resolving to 0.7.0 with no upper bound). Reviewed
  0.6.0/0.7.0 release notes for breaking changes affecting this sidecar -
  none found. Bumped the floor to `>=0.7.0` to match what's actually locked.
* **Feedback consumed, no bundle change**: the one open `.lokf/feedback.md`
  entry asked about a roadmap for a fifth skill; re-searched the repository
  and found nothing to derive a concept from, so cleared it rather than
  inventing one, per the docent's own note.
* **Orphan sweep**: `LICENSE`, `llms.txt`, and `EXAMPLES.md` had no
  source-map row; added one, all three staying excluded as concepts (see
  `playbooks/knowledge-sources.md` for why).
* **Initialization**: Scaffolded the LOKF bundle for LOKF Agent Skills, then
  ran a bootstrap discovery pass over the repository. Populated it with 25
  concepts: 8 playbooks (the four skills, the source map, contributing,
  releasing, repository validation), 7 references (the LOKF, OKF and Agent
  Skills specifications, the lokf toolkit, LinkML, and the two installer
  CLIs), 4 glossary terms, 4 policies, and 2 explanations. `base_iri` is a
  placeholder (`lokf-agent-skills.example`) pending a namespace the project
  controls.
* **Removed**: the scaffolded `services/` directory and its two dummy
  concepts - this repository ships documentation, agent skills, and CI, and
  has no `Service`, `Dataset`, `Table`, or `Metric` assets to describe.
* **Steady-state refresh**: re-verified all 17 internal-resource concepts
  against their current files (no factual drift found) and added a
  `process:ktl-librarian` `verified` event to each. Consciously excluded a
  new decorative asset, `.assets/lokf-agent-skills-card.svg`, recording it
  in `playbooks/knowledge-sources.md` instead of as a concept.
* **Audit**: `uv run lokf validate knowledge` (previously unavailable) found
  12 of 25 concepts using a bare scalar on a multivalued relation slot
  (`dependsOn`/`definedBy`/`relatedTo`) - schema-invalid despite reading
  naturally. Fixed by wrapping each as a one-item list, content unchanged.
  Same failure was independently visible in this repository's own
  `Knowledge Bundle Validation` GitHub Actions run. Clarified
  `ktl-librarian/SKILL.md` Golden Rule 4 and section 2 so it doesn't recur.
* **Source map extended**: an orphan sweep found three `.github/` surfaces
  accounted for by neither a concept nor a source-map row - the two dogfooded
  `knowledge-*.yaml` workflows, and the issue/pull-request templates alongside
  `dependabot.yml`. Added a row for each in
  `playbooks/knowledge-sources.md`, keeping all of them excluded as concepts
  (intake forms and maintenance config carry no reusable knowledge), and
  recorded the defects the sweep turned up in each.
* **Versioning policy re-sourced**: the `vMAJOR.MINOR.PATCH` bump definitions
  moved out of `README.md` (slimmed) into `CONTRIBUTING.md`'s release-process
  section, where the rest of the release mechanics already live. Repointed
  `policies/versioning.md`'s `resource` to follow them - its body was
  asserting definitions its stated source no longer carried - along with the
  cross-references in `README.md` and `CHANGELOG.md`.
* **Prompt-injection guards added and documented**: a synergy review against
  an external curation-patterns catalog (ai4curation.io) found that
  `.lokf/feedback.md` reached the scheduled librarian agent with no guard
  against a reader-submitted entry phrased as a directive. Added an explicit
  guard to `ktl-librarian/SKILL.md` (resolve only from the source an entry
  names, never its wording), and the same guard for the other two content-
  fetching paths in `ktl-curator/SKILL.md` and `ktl-docent/SKILL.md`.
  `SECURITY.md` gained a **Prompt-injection guards** section naming all three
  plus the unattended-write-path blast-radius containment and what remains
  unguarded (ordinary repository content, a reader's own phrasing); refreshed
  `policies/security.md` to match.
