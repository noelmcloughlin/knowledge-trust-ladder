---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/repository-validation
title: Repository validation
description: "What CI checks on every pull request and weekly: the repository contract, the Agent Skills spec, shell and workflow linting, the install and website smoke tests, and Markdown, link and spelling checks."
genre: how-to
resource: .github/workflows/validate.yml
generated:
  by: process:ktl-librarian
  at: "2026-10-28T00:35:16Z"
status: draft
references:
  - https://w3id.org/ktl/knowledge/references/agent-skills-specification
  - https://w3id.org/ktl/knowledge/references/open-skills-cli
  - https://w3id.org/ktl/knowledge/playbooks/contributing
sources:
  - resource: .github/workflows/validate.yml
  - resource: scripts/validate-repository.sh
  - resource: CHANGELOG.md
    id: changelog.md
  - resource: tests/test_website_preflight.py
  - resource: tests/test_website_template.py
    id: test_website_template.py
  - resource: scripts/smoke-test-website.sh
    id: smoke-test-website.sh
  - resource: tests/test_federation.py
    id: test_federation.py
  - resource: tests/test_ingest.py
    id: test_ingest.py
  - resource: tests/test_sync.py
  - resource: tests/requirements.txt
  - resource: scripts/smoke-test-install.sh
  - resource: skills/ktl-sidecar/templates/knowledge-sync.manifest
  - resource: tests/test_docent_holdout.py
    id: test_docent_holdout.py
verified:
  - by: process:ktl-librarian
    at: "2026-10-29T00:48:33Z"
---

# Overview

`validate.yml` runs separate jobs for the repository contract, the behavioural tests of the sidecar scripts, script linting, workflow linting, the install path, the website template's build, and Markdown and link checks. Separate jobs make a failure easy to diagnose. It runs on every pull request, every push to `main`, weekly (Mondays at 06:00 UTC), and on demand.

# The repository contract

The `validate-skills` job sets up `uv`, runs `scripts/validate-repository.sh`, confirms that `gh skill` is available, and then runs `gh skill publish --dry-run`. The contract script checks facts about this repository's own files. Since 2026-10-07 the behavioural tests of the sidecar scripts and the prose checker are under `tests/` instead. Each moved check keeps its number in the script, with a line saying where it went, so a changelog entry or a concept that names one still points somewhere.

- Check 1: exactly the intended skill directories exist (`ktl-curator`, `ktl-docent`, `ktl-librarian`, `ktl-prose`, `ktl-sidecar` and `ktl-website`). The script's list is the one place their number is written.
- Check 2: each of them holds a `SKILL.md` with that exact case.
- Check 3: each frontmatter `name` matches its directory.
- Check 3b: each skill declares a `compatibility` field of 1 to 500 characters naming what it needs.
- Check 3c: each `description` ends in a `Keywords:` list within the spec's 1024 characters, and `plugin.json` and `marketplace.json` carry the same keywords. Catalogs have no tag field, so that list is what they search.
- Check 4: no duplicate `SKILL.md` under `skills/`.
- Check 5: every relative Markdown link under `skills/` resolves from the linking file's own directory, as an installer copies one skill at a time. Fenced examples are ignored.
- Check 6: every `.sh` script under `skills/` and `scripts/` is ShellCheck-clean. Locally, the check skips when ShellCheck is not installed, because CI runs it.
- Check 7: Rule 3 in `ktl-librarian/SKILL.md` is the canonical list of LOKF classes. Check 7a holds `ktl-curator/references/trust-fields.md`'s enumeration to it, and check 7b holds every stated class count to it.
- Check 7c: Rule 3's list equals the classes `lokf vocab --all --json` declares as types, at the lokf floor the templates pin, with the toolkit run through `uvx`. Without uv the check fails.
- Check 7d: the relation fields `knowledge-report.sh` counts reliance from equal the slots the schema ranges over `Concept`, apart from the structural `concepts` and `target`.
- Check 8: the layout tests are in `tests/test_layouts.py`.
- Check 9: the paths the sibling repositories deep-link into still exist, and so does each heading such a link names. A link counts whether it names a file on GitHub or the site's persistent address: `w3id.org/ktl/docs/<page>/` names `docs/<page>.md`, and `w3id.org/ktl/knowledge/<id>` names `.lokf/knowledge/<id>.md`. The siblings are the two Obsidian plugins, ktl-federation, ai-linkmo and gist. Check 9a runs only when they are cloned beside this repository, and confirms that the recorded list of those paths and headings is complete. It skips what git ignores in a sibling: since 0.45.0 the copies its website build writes under `website/`, and since 0.53.0 a domain host's `snapshot/`, which holds a copy of this bundle.
- Check 10: `CONTRIBUTING.md` stays within 1000 words and `SECURITY.md` within 900.
- Check 10a: each `SKILL.md` stays within its own word budget: 2700 words for ktl-curator, 2200 for ktl-docent, 4000 for ktl-librarian, 2350 for ktl-prose, 3600 for ktl-sidecar and 2000 for ktl-website. A skill with no budget fails. Since 0.45.0 a table's pipes and its separator row are not counted as words.
- Check 11: the sidecar's `knowledge-sync.manifest`, which since 0.47.0 lists the copies, is checked first. Every template it names must exist, and every `always` and `needs` line must name a template it lists. Every file under the templates' `github/`, `scripts/` and `m365/` folders must be in it, so a new workflow or script cannot be released without a sync for it. Then each copy the manifest names must be byte-identical to its template, and `.lokf/justfile` to its template below the first line, which names the host.

  The comparison leaves out the librarian workflow's skills pin, `TRUST_LADDER_SKILLS_REF` and `TRUST_LADDER_SKILLS_SHA`, which the release commit moves in the template only. `knowledge-apply.py` and `knowledge-conventions.py` must pin the same PyYAML release and the same cut-off date. Without `uv` the check fails up front and names the cause. Then `knowledge-conventions.sh` must pass on this repository's bundle. `tests/test_conventions.py` tests what it reports on a bundle that breaks each rule.

  The federation, sync and ingest copies are held to their templates only where this repository has a copy, and it has none. Its bundle is not a domain, it has nothing to sync itself to, and it has no sources outside the repository. Every other copy must be here. `tests/test_federation.py`, `tests/test_sync.py` and `tests/test_ingest.py` run those scripts from their templates.

- Check 11a: ktl-docent's copies of `knowledge-report.sh` and `knowledge-feedback.sh` match their templates, and no ktl-docent page runs a script under `.lokf/scripts/`. Each copy, run from outside the repository as an installer leaves it, labels a concept and records a gap in the repository it is run in.
- Check 11b: every page that gives the no-Python schema URL names the same commit, and names the tag of the `lokf` floor that the sidecar's `pyproject.toml` template sets.
- Check 11c: `tests/test_conventions.py` tests conventions rule 14, which reads the commits after a pull request's base.
- Check 11w: the website skill's templates are this repository's own `website/` and `.github/workflows/knowledge-website.yaml`, held byte-identical, apart from the three files each host owns once written: `site.config.mjs`, `README.md` and `src/styles/custom.css`. The README template, with this repository's values filled in, must equal `website/README.md`. Every tracked file under `website/` must have a template or be one of the three. The template's two logos, `knowledge-trust-ladder-logo.svg` and `knowledge-trust-ladder-logo-dark.svg`, must equal this repository's copies in `.assets/`.
- Check 12: every line `knowledge-preflight.sh` can print as missing or a warning has a row on `ktl-sidecar/references/prerequisites.md`. `tests/test_preflight.py` tests how the preflight behaves.
- Check 12w: every line `website-preflight.sh` can print as missing or a warning has a row on `ktl-website/references/prerequisites.md`.
- Check 12a: `tests/test_feedback.py` tests `knowledge-feedback.sh`.
- Checks 13 and 13a: `tests/test_provenance.py` tests the forge-free provenance gate, with throwaway GPG and SSH keys, and its `--unattended` form.
- Check 14: `CHANGELOG.md` never carries two headings for one released version. Where node is installed, a throwaway repository also proves three things. `changelog-release.mjs promote` folds a second qualifying push into the section that still waits for `publish.yml`, listing each entry once. A version already tagged is left alone. A push with nothing new passes `check` for the version already promoted, and fails for any other.
- Check 15: the librarian template's `TRUST_LADDER_SKILLS_REF` names one of the two newest released versions in `CHANGELOG.md`. Two are allowed because the newest heading exists before its tag: `semantic-release.yml` promotes it on merge to `main`, and `publish.yml` creates the tag later. The commit the pin records must carry `skills/ktl-librarian`, the path the install step copies out of it. The check reads it from that commit when the tag ref is absent. Where the tag is on the clone, `TRUST_LADDER_SKILLS_SHA` must be the commit the tag names. The install step must compare the commit it cloned with that one, and `semantic-release.yml` and the sidecar's `knowledge-sync.sh` template must each move the commit with the tag.
- Check 16: the name the repository had before it was renamed on 2026-09-19 stays out of every file but `CHANGELOG.md`, the bundle's `log.md`, `rename-plan.md`, the contract script and one "formerly" line in `docs/install.md`.
- Check 16a: the skills' and plugins' old `lokf-` names stay out of every file but `CHANGELOG.md` and the contract script. They took the `ktl-` prefix on 2026-09-22.
- Check 16b: no file calls a role, skill or repository of KTL a LOKF one, apart from `CHANGELOG.md`, the bundle's `log.md`, the source map (`playbooks/knowledge-sources.md`) and the contract script.
- Check 17: the Microsoft 365 Copilot skills. No `SKILL.md` sits under any skill's `templates/`. Every instructions file under `templates/m365/` carries ktl-docent's trust-label table word for word. `knowledge-m365.sh` builds `ktl-docent-m365` from this repository's bundle. Where `zip` is installed, the build gives the same zip bytes under another time zone and umask, as a release asset must.
- Check 17a: every `SKILL.md` git tracks is at `skills/ktl-*/SKILL.md`, so `gh skill install --all` and `npx skills add` install the ktl- skills only (0.44.0). Both installers find a `SKILL.md` anywhere in the tree, so the check walks the whole index.
- Check 18: `prose-check.py` gives this repository's bundle its verdicts, and ktl-prose's own pages pass the style rules they state. `tests/test_prose_check.py` tests what the script reports and refuses.
- Check 19: `knowledge-apply.sh --format` prints the block `ktl-librarian/references/patch.md` shows. `tests/test_apply.py` tests what the pen writes and refuses.
- Check 20: `tests/test_report.py` tests `knowledge-report.sh`, and check 20a its curator's queue.
- Check 21: no tracked file holds a character a reader cannot see. That is a control character other than a tab or a line's closing carriage return, or a format character. Format characters include a zero-width space, a byte order mark and the right-to-left override that the "Trojan Source" attack hides code behind. The check also proves that it finds a right-to-left override planted in a script.
- Check 22: `tests/test_provenance.py` tests parser parity, which holds the gate's event reader to a YAML parser.

# The behavioural tests

The `test-scripts` job runs on two runners side by side, one per part of a matrix: `tests/test_federation.py` alone, and the rest of `tests/`. The federation builds are CPU-bound, so the second runner adds CPUs of its own. Each part sets up `uv`, installs the `just` that `.lokf/uv.lock` pins through `uv sync --locked --project .lokf`, with that command alone linked onto PATH (0.56.1), and Node.js 22, and runs `uv run --no-project --with-requirements tests/requirements.txt pytest -n auto` on its own paths, with one worker per CPU. `tests/requirements.txt` pins `pytest==9.1.1`, `pytest-xdist==3.8.0`, `pyyaml==6.0.3` and `pypdf==6.21.2`, and `pytest.ini` points pytest at `tests/`. `publish.yml` runs `uv run --no-project --with-requirements tests/requirements.txt pytest` before a release, in one process over all of `tests/`.

The tests run the scripts under `skills/ktl-sidecar/templates/`, `skills/ktl-prose/scripts/` and `skills/ktl-website/` on throwaway bundles and repositories. Each module says which contract check it carries:

- `test_apply.py`: the pen, `knowledge-apply.sh` (check 19).
- `test_conventions.py`: `knowledge-conventions.sh` on a bundle that breaks each rule, and on a bundle that keeps every rule with CRLF line endings, through a link and without uv (check 11's synthetic bundle, and check 11c).
- `test_docent_holdout.py`: since 0.58.0, the docent holdout in `tests/docent-holdout.yaml`, with no model call.[^changelog.md] It checks that each concept the holdout expects is still a file in the bundle, and that `evals/` has one case per question, each asking the same question. The holdout sits outside `.lokf/`, so the docent never reads a question beside its answer.[^test_docent_holdout.py]
- `test_federation.py`: `knowledge-federate.py` on two fixture bundles and a domain that names them (0.44.0). It checks the lock, one named graph per bundle, and the same bytes from two builds. It also covers the checks that stop a build and keep the previous snapshot, and the gate on a target no member owns. It covers a member that is itself a domain, the diamond rule, the depth a build follows, a schema released beside a member's zip, the `mcp` server, `--verify-only` and `members`.

  Since 0.50.1 it also covers which members join: a member is built as a person last confirmed it, a member no person confirmed waits outside the workspace, and a retired member or `Domain` concept is left out. Since 0.53.0 the build runs lokf in its own process, and a test checks that a failing lokf command fails there as a separate process would and that the build's working directory is put back. Also since 0.53.0 it checks that a build reaches a member at a local path only with `--allow-local`, and at a private address only as a person confirmed on the Domain concept. A zip holding a `.git` folder or a file a browser runs, and a distribution name that is not one plain file name, stop the build, and the report on a member reads no git configuration from it.

  Since 0.56.1 it checks that a name which turns private after the check is refused at the connection. It also checks that a member's move to another namespace waits under the namespace it is built at, and that a move the build would refuse leaves the member as it is.

  Since 0.57.0 it checks that every address that is not global counts as private, the shared address space included, and that through a proxy a member's name is checked once and the proxy resolves it.[^test_federation.py]

  The module makes the sidecar's environment once, under a lock all parallel workers share, before any test runs uv in it. Without uv every test in it skips.

- `test_feedback.py`: `knowledge-feedback.sh` (check 12a).
- `test_ingest.py`: `knowledge-ingest.py` on throwaway repositories against servers of its own. It covers each kind of source, the manifest's refusals, `--patch`, `--status` and the shell half's refusal to run under `sh`, and since 0.56.1 a name that turns private after the check and is refused at the connection. Since 0.57.0 it also covers a `git` entry held to the addresses its check found, with no redirect followed, and the refusal of a git older than 2.31. The same release added tests for a confidential entry's records kept out of the committed lock, the run's time limit, and the pypdf the script's header pins.[^test_ingest.py]
- `test_layouts.py`: the librarian wrapper, the librarian, registrar and release workflows, and the `just lokf-link` recipe, with and without the doorway link (formerly `scripts/test-sidecar-layouts.sh`).
- `test_preflight.py`: `knowledge-preflight.sh`, and each sidecar script's refusal to run under `sh` (check 12).
- `test_prose_check.py`: `prose-check.py` (check 18).
- `test_provenance.py`: `knowledge-provenance.sh` with throwaway keys, its `--unattended` form and parser parity (checks 13, 13a and 22).
- `test_report.py`: `knowledge-report.sh` and the curator's queue (checks 20 and 20a).
- `test_sync.py`: `knowledge-sync.sh` on a stand-in for the skills repository at two tags and a host at the first, and `scripts/sync-sidecar.sh`, which runs each sibling's own copy, and its `--finish`. It also checks that the report calls a copy a pin bump only when its `uses:` lines are all that differ (0.50.1). Since 0.53.0 it also tests `--apply`, which holds every workflow change but the pin and takes the pin from the caller, not from the patch. `--apply` refuses a deletion, a link, a path a sync may not touch, a copy inside a `.git` folder and a dirty checkout. Since 0.55.1 a host with a site gets the site templates, a route named with brackets included.
- `test_website_preflight.py`: `website-preflight.sh` on this repository and on a bare directory, and its refusal to run under `sh`; check 12w keeps the rows its lines need.
- `test_website_template.py`: the ktl-website templates installed on a temporary host, with no placeholder left, and the three files a host owns named alike in the skill's page, its preflight, the contract and the sidecar's `knowledge-sync.sh`. Since 0.53.0 it also checks that raw HTML passes only as GitHub renders it, and that the Markdown plugin checks raw HTML on every page. Since 0.56.0 it checks `DOCS.exclude`, a docs page's address as Starlight gives it, the redirects `REDIRECTS` writes, and that the site's host is lowercased for an owner spelt with capitals. Since 0.57.0 it checks that the home page offers a Schema button when the site shows the schema's pages.[^test_website_template.py]

Every subprocess runs under an isolated git config, so a global `commit.gpgsign=true` signs no fixture commit, and under a temporary directory of pytest's own. A layout test that needs `just`, `jq`, `node`, `zip` or `unzip` skips and says so when the tool is missing. The conventions tests fail, rather than skip, when uv is missing.

# The other jobs

- `lint-scripts` runs ShellCheck on the whole tree.
- `lint-workflows` runs `actionlint`, pointed by path at this repository's workflows and at the workflow templates that get copied into other repositories: the sidecar's `knowledge-librarian.yaml`, `knowledge-registrar.yaml`, `knowledge-release.yaml`, `knowledge-federation.yaml` (since 0.44.0), `knowledge-sync.yaml` and, since 0.56.1, `knowledge-ingest.yaml`, and ktl-website's `knowledge-website.yaml`. It would otherwise look only under `.github/workflows/`. It ignores the `copilot-requests` permission, which actionlint 1.7.12 predates. The job also checks that every `uses:` in this repository's workflows and those templates names a commit SHA or image digest rather than a floating tag or branch.
- `smoke-test` installs the skills from the checkout into a throwaway consumer repository through `scripts/smoke-test-install.sh`. It checks that ktl-docent's two scripts come with the install. It also checks that, run from where the installer put them, they label a concept and record a gap in a reader's repository.
- `smoke-test-website` builds the ktl-website template on a host made from the sidecar's dummy skeleton through `scripts/smoke-test-website.sh`, twice. One build has a README, a docs page, a changelog, the schema's pages and the data, and since 0.56.0 the redirects a retired mkdocs site needs and a folder `DOCS.exclude` keeps off the site. The other has none of them. Since 0.57.0 the fuller build's home page offers the schema's pages as a button, and the other's offers none.[^smoke-test-website.sh] This repository's own site, which `knowledge-website.yaml` builds, proves the fuller configuration.
- `validate-markdown` runs markdownlint, lychee, and codespell. Codespell skips `knowledge_bundle`, the link to `.lokf/knowledge`, which it already checks at its real path.

The schedule runs weekly because otherwise link rot, an upstream `gh skill` change or drift in the install path would show up only on the next pull request that happens to run.

[^changelog.md]: CHANGELOG.md, 0.57.0 and 0.58.0
[^test_docent_holdout.py]: tests/test_docent_holdout.py, the module's docstring
[^test_federation.py]: tests/test_federation.py, the private-address and proxy tests
[^test_ingest.py]: tests/test_ingest.py, the tests added in 0.57.0
[^test_website_template.py]: tests/test_website_template.py, the home page's buttons
[^smoke-test-website.sh]: scripts/smoke-test-website.sh, the home page's assertions
