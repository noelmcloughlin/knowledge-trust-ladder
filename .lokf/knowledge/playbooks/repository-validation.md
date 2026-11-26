---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/repository-validation
title: Repository validation
description: "What CI checks on every pull request and weekly: the repository contract, the Agent Skills spec, shell and workflow linting, the install and website smoke tests, and Markdown, link and spelling checks."
genre: how-to
resource: .github/workflows/validate.yml
generated:
  by: process:ktl-librarian
  at: "2026-11-18T11:03:45Z"
status: draft
references:
  - https://w3id.org/ktl/knowledge/references/agent-skills-specification
  - https://w3id.org/ktl/knowledge/references/open-skills-cli
  - https://w3id.org/ktl/knowledge/playbooks/contributing
sources:
  - resource: .github/workflows/validate.yml
  - resource: scripts/validate-repository.sh
  - resource: CHANGELOG.md
    id: changelog-docent-holdout
    excerpt: "`tests/docent-holdout.yaml` pairs the eight captured questions with the concept each answer should rest on"
  - resource: tests/test_website_preflight.py
  - resource: tests/test_website_template.py
    id: test_website_template.py
    excerpt: "def test_the_home_page_has_five_buttons_and_greys_the_one_it_cannot_find():"
  - resource: scripts/smoke-test-website.sh
    id: smoke-test-website-buttons
    excerpt: assert "the home page keeps its five buttons, with the schema's and the bundle's links and the architecture page's and the quick start's greyed, and does not lead with LOKF core"
  - resource: tests/test_federation.py
    id: test_federation.py
    excerpt: def test_through_a_proxy_a_member_name_is_checked_once_and_the_proxy_resolves_it
  - resource: tests/test_ingest.py
    id: test_ingest.py
    excerpt: def test_a_git_older_than_2_31_is_refused_for_every_git_entry
  - resource: tests/test_sync.py
  - resource: tests/test_repository.py
  - resource: tests/test_changelog_release.py
  - resource: tests/test_m365.py
  - resource: tests/requirements.in
  - resource: tests/requirements.txt
  - resource: .github/workflows/publish.yml
  - resource: scripts/smoke-test-install.sh
  - resource: skills/ktl-sidecar/templates/knowledge-sync.manifest
  - resource: tests/test_docent_holdout.py
    id: test_docent_holdout.py
    excerpt: outside .lokf/ and the docent's search path, so the docent cannot read a question beside its answer.
  - resource: lychee.toml
    id: lychee.toml
    excerpt: retried here; validate.yml checks the links a second time instead.
  - resource: tests/test_conformance.py
verified:
  - by: process:ktl-librarian
    at: "2026-11-26T02:26:42Z"
---

# Overview

`validate.yml` runs separate jobs for the repository contract, the behavioural tests of the sidecar scripts, script linting, workflow linting, the install path, the website template's build, and Markdown and link checks. Separate jobs make a failure easy to diagnose. It runs on every pull request, every push to `main`, weekly (Mondays at 06:00 UTC), and on demand.

# The repository contract

The `validate-skills` job sets up `uv` and Node.js 22, runs `scripts/validate-repository.sh`, confirms that `gh skill` is available, and then runs `gh skill publish --dry-run`. The contract script checks facts about this repository's own files. The behavioural tests of the sidecar scripts and the prose checker are under `tests/` instead. Each moved check keeps its number in the script, with a line saying where it went, so a changelog entry or a concept that names one still points somewhere.

- Check 1: exactly the intended skill directories exist (`ktl-curator`, `ktl-docent`, `ktl-librarian`, `ktl-prose`, `ktl-sidecar` and `ktl-website`). The script's list is the one place their number is written.
- Check 2: each of them holds a `SKILL.md` with that exact case.
- Check 3: each frontmatter `name` matches its directory.
- Check 3b: each skill declares a `compatibility` field of 1 to 500 characters naming what it needs.
- Check 3c: each `description` ends in a `Keywords:` list within the spec's 1024 characters, and `plugin.json` and `marketplace.json` carry the same keywords. Catalogs have no tag field, so that list is what they search.
- Check 4: no duplicate `SKILL.md` under `skills/`.
- Check 5: every relative Markdown link under `skills/` resolves from the linking file's own directory, as an installer copies one skill at a time. Fenced examples are ignored.
- Check 6: every `.sh` script under `skills/` and `scripts/` is ShellCheck-clean. Locally, the check skips when ShellCheck is not installed. Under CI it fails instead, as every check does whose tool is missing, since a skipped check there is one nobody ran.
- Check 7: Rule 3 in `ktl-librarian/SKILL.md` is the canonical list of LOKF classes. Check 7a holds `ktl-curator/references/trust-fields.md`'s enumeration to it, and check 7b holds every stated class count to it.
- Check 7c: Rule 3's list equals the classes `lokf vocab --all --json` declares as types, at the lokf floor the templates pin, with the toolkit run through `uvx`. Without uv the check fails.
- Check 7d: the relation fields `knowledge-report.sh` counts reliance from equal the slots the schema ranges over `Concept`, apart from the structural `concepts` and `target`.
- Check 8: the layout tests are in `tests/test_layouts.py`.
- Check 9: the paths the sibling repositories deep-link into still exist, and so does each heading such a link names. A link counts whether it names a file on GitHub or the site's persistent address: `w3id.org/ktl/docs/<page>/` names `docs/<page>.md`, and `w3id.org/ktl/knowledge/<id>` names `.lokf/knowledge/<id>.md`. The siblings are the two Obsidian plugins, ktl-federation, ai-linkmo and gist. Check 9a runs only when they are cloned beside this repository, and confirms that the recorded list of those paths and headings is complete. It skips what git ignores in a sibling: the copies its website build writes under its site's folder, `website/` or `ktl-website/`, and a domain host's `snapshot/`, which holds a copy of this bundle.
- Check 10: `CONTRIBUTING.md` stays within 1000 words and `SECURITY.md` within 900.
- Check 10a: each `SKILL.md` stays within its own word budget: 2700 words for ktl-curator, 2200 for ktl-docent, 4000 for ktl-librarian, 2350 for ktl-prose, 3600 for ktl-sidecar and 2000 for ktl-website. A skill with no budget fails. A table's pipes and its separator row are not counted as words.
- Check 11: the sidecar's `knowledge-sync.manifest`, which lists the copies, is checked first. Every template it names must exist, and every `always` and `needs` line must name a template it lists. Every file under the templates' `github/`, `scripts/` and `m365/` folders must be in it, so a new workflow or script cannot be released without a sync for it. Then each copy the manifest names must be byte-identical to its template, and `.lokf/justfile` to its template below the first line, which names the host.

  `knowledge-apply.py` and `knowledge-conventions.py` must pin the same PyYAML release. Without `uv` the check fails up front and names the cause. Then `knowledge-conventions.sh --strict` must pass on this repository's bundle. `tests/test_conventions.py` tests what it reports on a bundle that breaks each rule.

  The federation, sync and ingest copies are held to their templates only where this repository has a copy, and it has none. Its bundle is not a domain, it has nothing to sync itself to, and it has no sources outside the repository. Every other copy must be here. `tests/test_federation.py`, `tests/test_sync.py` and `tests/test_ingest.py` run those scripts from their templates.

- Check 11a: ktl-docent's copies of `knowledge-report.sh` and `knowledge-feedback.sh` match their templates, and no ktl-docent page runs a script under `.lokf/scripts/`. Each copy, run from outside the repository as an installer leaves it, labels a concept and records a gap in the repository it is run in.
- Check 11b: every page that gives the no-Python schema URL names the same commit, and names the tag of the `lokf` floor that the sidecar's `pyproject.toml` template sets.
- Check 11c: `tests/test_conventions.py` tests conventions rule 14, which reads the commits after a pull request's base.
- Check 11w: the website skill's templates are this repository's own `website/` and `.github/workflows/knowledge-website.yaml`, held byte-identical, apart from the three files each host owns once written: `site.toml`, `README.md` and `assets/css/custom.css`. The README template, with this repository's values filled in, must equal `website/README.md`. Every tracked file under `website/` must have a template or be one of the three. The template's two logos, `knowledge-trust-ladder-logo.svg` and `knowledge-trust-ladder-logo-dark.svg`, must equal this repository's copies in `.assets/`.
- Check 12: every line `knowledge-preflight.sh` can print as missing or a warning has a row on `ktl-sidecar/references/prerequisites.md`. `tests/test_preflight.py` tests how the preflight behaves.
- Check 12w: every line `website-preflight.sh` can print as missing or a warning has a row on `ktl-website/references/prerequisites.md`.
- Check 12a: `tests/test_feedback.py` tests `knowledge-feedback.sh`.
- Checks 13 and 13a: `tests/test_provenance.py` tests the forge-free provenance gate, with throwaway GPG and SSH keys, and its `--unattended` form.
- Check 14: `CHANGELOG.md` never carries two headings for one released version. Where node is installed, a throwaway repository also proves three things. `changelog-release.mjs promote` folds a second qualifying push into the section that still waits for `publish.yml`, listing each entry once. A version already tagged is left alone. A push with nothing new passes `check` for the version already promoted, and fails for any other. `tests/test_changelog_release.py` tests each of the script's commands.
- Check 15: the sidecar's `templates/pyproject.toml` pins `ktl` at one of the two newest released versions in `CHANGELOG.md`. Two are allowed because the newest heading exists before its tag: `semantic-release.yml` promotes it on merge to `main`, and `publish.yml` creates the tag later. Where the pinned tag is on the clone, it must carry `skills/ktl-librarian/SKILL.md` and the sync manifest, which a host reads from the package. `semantic-release.yml` must move the template's `ktl` pin, and the librarian template must install `ktl-librarian` from the locked `ktl` package.
- Check 16: the repository's former name stays out of every file but `CHANGELOG.md`, the bundle's `log.md`, `rename-plan.md`, the contract script and one "formerly" line in `docs/install.md`.
- Check 16a: the skills' and plugins' old `lokf-` names stay out of every file but `CHANGELOG.md` and the contract script. Their names now start with `ktl-`.
- Check 16b: no file calls a role, skill or repository of KTL a LOKF one, apart from `CHANGELOG.md`, the bundle's `log.md`, the source map (`playbooks/knowledge-sources.md`) and the contract script.
- Check 17: the Microsoft 365 Copilot skills. No `SKILL.md` sits under any skill's `templates/`. Every instructions file under `templates/m365/` carries ktl-docent's trust-label table word for word. `knowledge-m365.sh` builds `ktl-docent-m365` from this repository's bundle. Without `zip` the folder is still checked and the zip check is skipped. Where `zip` is installed, the build must write the zip, and gives the same zip bytes under another time zone and umask, as a release asset must. `tests/test_m365.py` tests the build, its refusals and each limit on a small bundle.
- Check 17a: every `SKILL.md` git tracks is at `skills/ktl-*/SKILL.md`, so `gh skill install --all` and `npx skills add` install the ktl- skills only. Both installers find a `SKILL.md` anywhere in the tree, so the check walks the whole index.
- Check 18: `prose-check.py` gives this repository's bundle its verdicts, and ktl-prose's own pages pass the style rules they state. `tests/test_prose_check.py` tests what the script reports and refuses.
- Check 19: `knowledge-apply.sh --format` prints the block `ktl-librarian/references/patch.md` shows. `tests/test_apply.py` tests what the pen writes and refuses.
- Check 20: `tests/test_report.py` tests `knowledge-report.sh`, and check 20a its curator's queue.
- Check 21: no tracked file holds a character a reader cannot see. That is a control character other than a tab or a line's closing carriage return, a format character, a line or paragraph separator, or another character the pen treats as invisible, such as a Hangul filler or a variation selector. Format characters include a zero-width space, a byte order mark and the right-to-left override that the "Trojan Source" attack hides code behind. The check also proves that it finds a right-to-left override planted in a script.
- Check 22: `tests/test_provenance.py` tests parser parity, which holds the gate's event reader to a YAML parser.
- Check 23: the GitHub settings catalogues, `references/repository-settings.json` in ktl-sidecar and ktl-website and `.github/repository-settings.json`, are held to the templates, to `automation.md`'s table of switches and secrets, to the pages they link to, and to the changelog's retired names in `tests/test_gh.py`.
- Check 24: `SPEC.md` is the source for the rules more than one program applies, and four copies say the same words. They are the conventions in the header of `knowledge-conventions.sh`, the pen's operations and the refusals that keep a person's record in `ktl-librarian/references/patch.md`, and the label table and the queue's order in `ktl-curator/references/trust-fields.md`.

# The behavioural tests

The `test-scripts` job runs on two runners side by side, one per part of a matrix: `tests/test_federation.py` alone, and the rest of `tests/`. The federation builds are CPU-bound, so the second runner adds CPUs of its own. Each part sets up `uv` and Node.js 22. It installs the `just` that `.lokf/uv.lock` pins through `uv sync --locked --project .lokf`, with that command alone linked onto PATH. It installs the test packages into an environment of their own with `uv pip install --require-hashes -r tests/requirements.txt`. Each file is checked against its hash there, which `uv run --with-requirements` does not do. It then runs `pytest -n auto` on its own paths, with one worker per CPU.

`tests/requirements.in` pins `pytest==9.2.0`, `pytest-xdist==3.8.0`, `pyyaml==6.0.3` and `pypdf==7.1.0`, and `uv pip compile --generate-hashes` writes `tests/requirements.txt` from it. `pytest.ini` points pytest at `tests/`. `publish.yml` makes the same install and runs `pytest -n auto` over all of `tests/` before a release, with one worker per CPU, in its read-only `verify` job (`CHANGELOG.md`).

The tests run the scripts under `skills/ktl-sidecar/templates/`, `skills/ktl-prose/scripts/` and `skills/ktl-website/` on throwaway bundles and repositories. Each module says which contract check it carries:

- `test_apply.py`: the pen, `knowledge-apply.sh` (check 19).
- `test_changelog_release.py`: `changelog-release.mjs`, each of its commands in a throwaway repository, skipped without node (check 14).
- `test_conformance.py`: `knowledge-report.sh` on the bundle in `tests/conformance/reader/`, which has one concept for each trust label a program can compute from the files alone. The test copies the bundle out of the repository, so git holds no history of it, and checks that the report gives what `expected.json` holds. Those values were worked out by hand from section 8 of `SPEC.md`.
- `test_conventions.py`: `knowledge-conventions.sh` on a bundle that breaks each rule, and on a bundle that keeps every rule with CRLF line endings, through a link and without uv (check 11's synthetic bundle, and check 11c).
- `test_docent_holdout.py`: the docent holdout in `tests/docent-holdout.yaml`, with no model call.[^changelog-docent-holdout] It checks that each concept the holdout expects is still a file in the bundle, and that `evals/` has one case per question, each asking the same question. The holdout sits outside `.lokf/`, so the docent never reads a question beside its answer.[^test_docent_holdout.py]
- `test_federation.py`: `knowledge-federate.py` on two fixture bundles and a domain that names them. It checks the lock, one named graph per bundle, and the same bytes from two builds. It also covers the checks that stop a build and keep the previous snapshot, and the gate on a target no member owns. It covers a member that is itself a domain, the diamond rule, the depth a build follows, a schema released beside a member's zip, the `mcp` server, `--verify-only` and `members`.

  It also covers which members join: a member is built as a person last confirmed it, a member no person confirmed waits outside the workspace, and a retired member or `Domain` concept is left out. The build runs lokf in its own process, and a test checks that a failing lokf command fails there as a separate process would and that the build's working directory is put back.

  It also checks that a build reaches a member at a local path only with `--allow-local`, and at a private address only as a person confirmed on the Domain concept. A zip holding a `.git` folder or any file but Markdown and images stops the build. So does a distribution name that is not one plain file name or does not end as its file does, and so does a member's schema that imports anything but `lokf` and `linkml:` names. The report on a member reads no git configuration from it.

  It checks that a name which turns private after the check is refused at the connection. It also checks that a member's move to another namespace waits under the namespace it is built at, and that a move the build would refuse leaves the member as it is.

  It checks that every address that is not global counts as private, the shared address space included. It checks that through a proxy a member's name is checked once and the proxy resolves it.[^test_federation.py] It checks that the export labels blank nodes by RDFC-1.0 while the toolkit uses rdflib. It checks that a member's own words cut no quad and add no line to the workspace index, and that `labels.rq` reads review dates, status and the latest confirmation.

  The module makes the sidecar's environment once, under a lock all parallel workers share, before any test runs uv in it. Without uv every test in it skips.

- `test_feedback.py`: `knowledge-feedback.sh` (check 12a).
- `test_ingest.py`: `knowledge-ingest.py` on throwaway repositories against servers of its own. It covers each kind of source, the manifest's refusals, `--patch`, `--status` and the shell half's refusal to run under `sh`, and a name that turns private after the check and is refused at the connection. It also covers a `git` entry held to the addresses its check found, with no redirect followed, and the refusal of a git older than 2.31. It covers a confidential entry's records kept out of the committed lock, the run's time limit, and the pypdf the script's header pins.[^test_ingest.py] It covers a download cut short, which is tried again and never mirrored. It covers a mirror file edited by hand, which is written again, a redirected page, and a changed header setting that reaches every page.

  It also covers the privileged job's refusal of a rename, a link or a file marked to run, and its push leased to the commit it read.
- `test_layouts.py`: the librarian wrapper, the librarian, registrar and release workflows, and the `just lokf-link` recipe, with and without the doorway link (formerly `scripts/test-sidecar-layouts.sh`).
- `test_m365.py`: `knowledge-m365.sh`, the Microsoft 365 Copilot skills' builder, on a small bundle of its own (check 17).
- `test_preflight.py`: `knowledge-preflight.sh`, and each sidecar script's refusal to run under `sh` (check 12).
- `test_prose_check.py`: `prose-check.py` (check 18).
- `test_provenance.py`: `knowledge-provenance.sh` with throwaway keys, its `--unattended` form and parser parity (checks 13, 13a and 22).
- `test_report.py`: `knowledge-report.sh` and the curator's queue (checks 20 and 20a).
- `test_repository.py`: this repository's own scripts and workflows, the ones no skill installs. It checks that `scripts/smoke-test-install.sh` fails when the install leaves installer metadata in this source repository, and passes when the metadata was there before it ran. It also checks that `publish.yml` runs the contract and the tests in a job that holds a read-only token, and that the job that holds the write token needs it and runs neither.
- `test_sync.py`: `knowledge-sync.sh` on a host whose `.lokf/pyproject.toml` pins the first of two `ktl` wheels, built from the real templates on a local `file://` index. It also checks that the report calls a copy a pin bump only when its `uses:` lines are all that differ. It also tests `--apply`, which holds every workflow change, takes the pin's line at the run's tag, and takes the patch's lock only when uv writes the same lock from the index. `--apply` refuses a deletion, a link, a path a sync may not touch, a copy inside a `.git` folder and a dirty checkout.

  A host with a site gets the site templates in whichever folder holds it, `website/` or `ktl-website/`, and the sync leaves another site's `website/` alone. It checks that a local edit the sync overwrites is not blamed on the release, and that a host file no manifest line names is reported and left alone.
- `test_website_preflight.py`: `website-preflight.sh` on this repository and on a bare directory, and its refusal to run under `sh`; check 12w keeps the rows its lines need. It checks that the preflight prints no credential a remote's address carries. It also checks which folder the site goes in: `website/` when it is this skill's, `ktl-website/` beside another site's `website/`, the earlier Astro site named as one to move, and two foreign folders as a stop. It checks that a schema is found at the root first and then under `.linkml/`, that a domain host is named by its federation workflow, and what the docs folder gives the home page.
- `test_website_template.py`: the ktl-website templates installed on a temporary host, with no placeholder left, and the three files a host owns named alike in the skill's page, its preflight, the contract and the sidecar's `knowledge-sync.sh`. It checks that `site.toml` is valid TOML once filled and that the build refuses a placeholder left behind.

  It checks that the site finds each input through a mount and takes no setting for it, and that a retelling is found by its file name. It checks that no file's frontmatter reaches Hugo, and that the home page has five buttons and greys the one it cannot find.[^test_website_template.py] It also checks `site.toml`'s `source` setting. The setting moves the five root mounts, the README, `SPEC.md`, the docs, the changelog and the figures, and the build reads it last.

  It also checks that the workflows and the sync look in either folder, the link check, and the raw-HTML cleaner, which keeps what GitHub allows and shows the rest as text. It checks that Step 1 writes each value as a TOML string and refuses a line break. It checks that the build installs its tools from the index uv reads and leaves the lock alone, and that a site's own copy of a library is taken before the CDN and checked alike. It checks that each SVG is read as XML, and that the cleaner keeps a class or a `data-` attribute only where the site wrote it.

  It checks that the specification's button follows Architecture and is never greyed. It checks that a root `SPEC.md` becomes a page of the guide, and that nothing names the page where the file is missing.

Every subprocess runs under an isolated git config, so a global `commit.gpgsign=true` signs no fixture commit, and under a temporary directory of pytest's own. A layout test that needs `just`, `jq`, `node`, `zip` or `unzip` skips and says so when the tool is missing. The conventions tests fail, rather than skip, when uv is missing.

# The other jobs

- `lint-scripts` runs ShellCheck on the whole tree.
- `lint-workflows` runs `actionlint`, pointed by path at this repository's workflows and at the workflow templates that get copied into other repositories: the sidecar's `knowledge-librarian.yaml`, `knowledge-registrar.yaml`, `knowledge-release.yaml`, `knowledge-federation.yaml`, `knowledge-sync.yaml` and `knowledge-ingest.yaml`, and ktl-website's `knowledge-website.yaml`. It would otherwise look only under `.github/workflows/`. It ignores the `copilot-requests` permission, which actionlint 1.7.12 predates. The job also checks that every `uses:` in this repository's workflows and those templates names a commit SHA or image digest rather than a floating tag or branch.
- `smoke-test` installs the skills from the checkout into a throwaway consumer repository through `scripts/smoke-test-install.sh`. It checks that ktl-docent's two scripts come with the install. It also checks that, run from where the installer put them, they label a concept and record a gap in a reader's repository.
- `smoke-test-website` builds the ktl-website template on a host made from the sidecar's dummy skeleton through `scripts/smoke-test-website.sh`, three times. One build has a README, docs pages, a changelog, a root `SPEC.md`, figures, a LinkML schema, retellings, the federation workflow, a mirrored source and data. Another has none of them, since the site finds each with no setting, and the third has a domain vocabulary alone. The fuller build's home page lights four of its five buttons, and the empty build's keeps all five, with the schema's and the bundle's links.[^smoke-test-website-buttons] This repository's own site, which `knowledge-website.yaml` builds, proves a fuller `site.toml`.
- `validate-markdown` runs markdownlint, lychee, and codespell. A failed lychee pass waits a minute and checks every link again, and only the second pass fails the job. Lychee itself retries a timeout or a 429 but never a failed connection.[^lychee.toml] Codespell skips `knowledge_bundle`, the link to `.lokf/knowledge`, which it already checks at its real path.

The schedule runs weekly because otherwise link rot, an upstream `gh skill` change or drift in the install path would show up only on the next pull request that happens to run.

[^changelog-docent-holdout]: CHANGELOG.md, the entry for ktl-docent's holdout
[^test_docent_holdout.py]: tests/test_docent_holdout.py, the module's docstring
[^lychee.toml]: lychee.toml, the comment above max_retries, and .github/workflows/validate.yml's Check links step
[^test_federation.py]: tests/test_federation.py, the private-address and proxy tests
[^test_ingest.py]: tests/test_ingest.py, the tests of a git entry and of a confidential entry
[^test_website_template.py]: tests/test_website_template.py, the test of the home page's five buttons
[^smoke-test-website-buttons]: scripts/smoke-test-website.sh, the home page's assertions
