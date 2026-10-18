---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/repository-validation
title: Repository validation
description: "What CI checks on every pull request and weekly: the repository contract, the Agent Skills spec, shell and workflow linting, the install and website smoke tests, and Markdown, link and spelling checks."
genre: how-to
resource: .github/workflows/validate.yml
generated:
  by: process:ktl-librarian
  at: "2026-10-18T10:22:18Z"
status: draft
references:
  - https://w3id.org/ktl/knowledge/references/agent-skills-specification
  - https://w3id.org/ktl/knowledge/references/open-skills-cli
  - https://w3id.org/ktl/knowledge/playbooks/contributing
sources:
  - resource: .github/workflows/validate.yml
  - resource: scripts/validate-repository.sh
  - resource: CHANGELOG.md
  - resource: tests/test_website_preflight.py
  - resource: tests/test_website_template.py
  - resource: scripts/smoke-test-website.sh
  - resource: tests/test_federation.py
  - resource: tests/test_ingest.py
  - resource: tests/test_sync.py
  - resource: tests/requirements.txt
  - resource: scripts/smoke-test-install.sh
  - resource: skills/ktl-sidecar/templates/knowledge-sync.manifest
verified:
  - by: process:ktl-librarian
    at: "2026-10-12T23:54:05Z"
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
- Check 9: the paths the sibling repositories deep-link into still exist, and so does each heading such a link names. A link counts whether it names a file on GitHub or the site's persistent address: `w3id.org/ktl/docs/<page>/` names `docs/<page>.md`, and `w3id.org/ktl/knowledge/<id>` names `.lokf/knowledge/<id>.md`. Check 9a runs only when the siblings are cloned beside this repository, and confirms that the recorded list of those paths and headings is complete. Since 0.45.0 it skips the copies a sibling's website build writes under `website/`, which git ignores there.
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

The `test-scripts` job sets up `uv`, installs `just` (`rust-just==1.47.0`) and Node.js 22, and runs `uv run --no-project --with-requirements tests/requirements.txt pytest`. `tests/requirements.txt` pins `pytest==9.1.1`, `pyyaml==6.0.3` and `pypdf==6.19.0`, and `pytest.ini` points pytest at `tests/`. `publish.yml` runs the same command before a release.

The tests run the scripts under `skills/ktl-sidecar/templates/`, `skills/ktl-prose/scripts/` and `skills/ktl-website/` on throwaway bundles and repositories. Each module says which contract check it carries:

- `test_apply.py`: the pen, `knowledge-apply.sh` (check 19).
- `test_conventions.py`: `knowledge-conventions.sh` on a bundle that breaks each rule, and on a bundle that keeps every rule with CRLF line endings, through a link and without uv (check 11's synthetic bundle, and check 11c).
- `test_federation.py`: `knowledge-federate.py` on two fixture bundles and a domain that names them (0.44.0). It checks the lock, one named graph per bundle, and the same bytes from two builds. It also covers the checks that stop a build and keep the previous snapshot, and the gate on a target no member owns. It covers a member that is itself a domain, the diamond rule, the depth a build follows, a schema released beside a member's zip, the `mcp` server, `--verify-only` and `members`. Without uv every test in it skips.
- `test_feedback.py`: `knowledge-feedback.sh` (check 12a).
- `test_ingest.py`: `knowledge-ingest.py` on throwaway repositories against servers of its own: each kind of source, the manifest's refusals, `--patch`, `--status`, and the shell half's refusal to run under `sh`.
- `test_layouts.py`: the librarian wrapper, the librarian, registrar and release workflows, and the `just lokf-link` recipe, with and without the doorway link (formerly `scripts/test-sidecar-layouts.sh`).
- `test_preflight.py`: `knowledge-preflight.sh`, and each sidecar script's refusal to run under `sh` (check 12).
- `test_prose_check.py`: `prose-check.py` (check 18).
- `test_provenance.py`: `knowledge-provenance.sh` with throwaway keys, its `--unattended` form and parser parity (checks 13, 13a and 22).
- `test_report.py`: `knowledge-report.sh` and the curator's queue (checks 20 and 20a).
- `test_sync.py`: `knowledge-sync.sh` on a stand-in for the skills repository at two tags and a host at the first, and `scripts/sync-sidecar.sh`, which runs each sibling's own copy, and its `--finish`.
- `test_website_preflight.py`: `website-preflight.sh` on this repository and on a bare directory, and its refusal to run under `sh`; check 12w keeps the rows its lines need.
- `test_website_template.py`: the ktl-website templates laid down on a temporary host, with no placeholder left, and the three files a host owns named alike in the skill's page, its preflight, the contract and the sidecar's `knowledge-sync.sh`.

Every subprocess runs under an isolated git config, so a global `commit.gpgsign=true` signs no fixture commit, and under a temporary directory of pytest's own. A layout test that needs `just`, `jq`, `node`, `zip` or `unzip` skips and says so when the tool is missing. The conventions tests fail, rather than skip, when uv is missing.

# The other jobs

- `lint-scripts` runs ShellCheck on the whole tree.
- `lint-workflows` runs `actionlint`, pointed by path at this repository's workflows and at the workflow templates that get copied into other repositories: the sidecar's `knowledge-librarian.yaml`, `knowledge-registrar.yaml`, `knowledge-release.yaml`, `knowledge-federation.yaml` (since 0.44.0) and `knowledge-sync.yaml`, and ktl-website's `knowledge-website.yaml`. It would otherwise look only under `.github/workflows/`. It ignores the `copilot-requests` permission, which actionlint 1.7.12 predates. The job also checks that every `uses:` in this repository's workflows and those templates names a commit SHA or image digest rather than a floating tag or branch.
- `smoke-test` installs the skills from the checkout into a throwaway consumer repository through `scripts/smoke-test-install.sh`. It checks that ktl-docent's two scripts come with the install. It also checks that, run from where the installer put them, they label a concept and record a gap in a reader's repository.
- `smoke-test-website` builds the ktl-website template on a host made from the sidecar's dummy skeleton through `scripts/smoke-test-website.sh`, twice: once with a README, a docs page, a changelog, the schema's pages and the data, and once with none of them. This repository's own site, which `knowledge-website.yaml` builds, proves the fuller configuration.
- `validate-markdown` runs markdownlint, lychee, and codespell. Codespell skips `knowledge_bundle`, the link to `.lokf/knowledge`, which it already checks at its real path.

The schedule runs weekly because otherwise link rot, an upstream `gh skill` change or drift in the install path would show up only on the next pull request that happens to run.
