---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/repository-validation
title: Repository validation
description: "What CI checks on every pull request and weekly: the repository contract, the Agent Skills spec, shell and workflow linting, the install smoke test, and Markdown, link and spelling checks."
genre: how-to
resource: .github/workflows/validate.yml
generated:
  by: process:ktl-librarian
  at: "2026-10-12T00:39:30Z"
status: draft
references:
- https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
- https://knowledge-trust-ladder.example/knowledge/references/open-skills-cli
- https://knowledge-trust-ladder.example/knowledge/playbooks/contributing
sources:
- resource: .github/workflows/validate.yml
- resource: scripts/validate-repository.sh
- resource: CHANGELOG.md
verified:
- by: process:ktl-librarian
  at: "2026-10-12T03:11:32Z"
---

# Overview

`validate.yml` runs separate jobs for the repository contract, the behavioural tests of the sidecar scripts, script linting, workflow linting, the install path, and Markdown and link checks, so a failure is easy to diagnose. It runs on every pull request, every push to `main`, weekly (Mondays at 06:00 UTC), and on demand.

# The repository contract

The `validate-skills` job sets up `uv`, runs `scripts/validate-repository.sh`, confirms that `gh skill` is available, and then runs `gh skill publish --dry-run`. The contract script checks facts about this repository's own files. Since 2026-10-07 the behavioural tests of the sidecar scripts and the prose checker are under `tests/` instead. Each moved check keeps its number in the script, with a line saying where it went, so a changelog entry or a concept that names one still points somewhere.

- Check 1: exactly the intended skill directories exist (`ktl-curator`, `ktl-docent`, `ktl-librarian`, `ktl-prose` and `ktl-sidecar`). The script's list is the one place their number is written.
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
- Check 9: the paths the sibling repositories deep-link into by URL still exist. Check 9a runs only when the siblings are cloned beside this repository, and confirms that the recorded list of those paths is complete.
- Check 10: `CONTRIBUTING.md` stays within 1000 words and `SECURITY.md` within 900.
- Check 10a: each `SKILL.md` stays within its own word budget: 2700 words for ktl-curator, 2200 for ktl-docent, 4000 for ktl-librarian, 2350 for ktl-prose and 3600 for ktl-sidecar. A skill with no budget fails.
- Check 11: this repository's copies of the three knowledge workflows, the sidecar scripts, the two `.lokf/m365/` files and `.lokf/.gitattributes` stay byte-identical to their templates. The comparison leaves out the librarian workflow's skills pin, `TRUST_LADDER_SKILLS_REF` and `TRUST_LADDER_SKILLS_SHA`, which the release commit moves in the template only. `knowledge-apply.py` and `knowledge-conventions.py` must pin the same PyYAML release and the same cut-off date. Without `uv` the check fails up front and names the cause. Then `knowledge-conventions.sh` must pass on this repository's bundle. `tests/test_conventions.py` tests what it reports on a bundle that breaks each rule.
- Check 11a: ktl-docent's copies of `knowledge-report.sh` and `knowledge-feedback.sh` match their templates, and no ktl-docent page runs a script under `.lokf/scripts/`. Each copy, run from outside the repository as an installer leaves it, labels a concept and records a gap in the repository it is run in.
- Check 11b: every page that gives the no-Python schema URL names the same commit, and names the tag of the `lokf` floor that the sidecar's `pyproject.toml` template sets.
- Check 11c: `tests/test_conventions.py` tests conventions rule 14, which reads the commits after a pull request's base.
- Check 12: every line `knowledge-preflight.sh` can print as missing or a warning has a row on `ktl-sidecar/references/prerequisites.md`. `tests/test_preflight.py` tests how the preflight behaves.
- Check 12a: `tests/test_feedback.py` tests `knowledge-feedback.sh`.
- Checks 13 and 13a: `tests/test_provenance.py` tests the forge-free provenance gate, with throwaway GPG and SSH keys, and its `--unattended` form.
- Check 14: `CHANGELOG.md` never carries two headings for one released version. Where node is installed, a throwaway repository also proves three things. `changelog-release.mjs promote` folds a second qualifying push into the section that still waits for `publish.yml`. A version already tagged is left alone. A push with nothing new passes `check` for the version already promoted, and fails for any other.
- Check 15: the librarian template's `TRUST_LADDER_SKILLS_REF` names one of the two newest released versions in `CHANGELOG.md`. It allows two headings of slack because the newest heading exists before its tag: `semantic-release.yml` promotes it on merge to `main`, and `publish.yml` creates the tag later. The commit the pin records must carry `skills/ktl-librarian`, the path the install step copies out of it, and the check reads it from that commit when the tag ref is absent. Where the tag is on the clone, `TRUST_LADDER_SKILLS_SHA` must be the commit the tag names. The install step must compare the commit it cloned with that one, and `semantic-release.yml` and `scripts/sync-sidecar.sh` must each move the commit with the tag.
- Check 16: the name the repository had before it was renamed on 2026-09-19 stays out of every file but `CHANGELOG.md`, the bundle's `log.md`, `rename-plan.md`, the contract script and one "formerly" line in `docs/install.md`.
- Check 16a: the skills' and plugins' old `lokf-` names stay out of every file but `CHANGELOG.md` and the contract script. They took the `ktl-` prefix on 2026-09-22.
- Check 16b: no file calls a role, skill or repository of KTL a LOKF one, apart from `CHANGELOG.md`, the bundle's `log.md`, the source map (`playbooks/knowledge-sources.md`) and the contract script.
- Check 17: the Microsoft 365 Copilot skills. No `SKILL.md` sits under the sidecar's `templates/`. Every instructions file under `templates/m365/` carries ktl-docent's trust-label table word for word. `knowledge-m365.sh` builds `ktl-docent-m365` from this repository's bundle. Where `zip` is installed, the build gives the same zip bytes under another time zone and umask, as a release asset must.
- Check 18: `prose-check.py` gives this repository's bundle its verdicts, and ktl-prose's own pages pass the style rules they state. `tests/test_prose_check.py` tests what the script reports and refuses.
- Check 19: `knowledge-apply.sh --format` prints the block `ktl-librarian/references/patch.md` shows. `tests/test_apply.py` tests what the pen writes and refuses.
- Check 20: `tests/test_report.py` tests `knowledge-report.sh`, and check 20a its curator's queue.
- Check 21: no tracked file holds a character a reader cannot see. That is a control character other than a tab or a line's closing carriage return, or a format character, such as a zero-width space, a byte order mark or the right-to-left override that the "Trojan Source" attack hides code behind. The check also proves that it finds a right-to-left override planted in a script.
- Check 22: `tests/test_provenance.py` tests parser parity, which holds the gate's event reader to a YAML parser.

# The behavioural tests

The `test-scripts` job sets up `uv`, installs `just` (`rust-just==1.47.0`) and Node.js 22, and runs `uv run --no-project --with-requirements tests/requirements.txt pytest`. `tests/requirements.txt` pins `pytest==9.1.1` and `pyyaml==6.0.3`, and `pytest.ini` points pytest at `tests/`. `publish.yml` runs the same command before a release.

The tests run the scripts under `skills/ktl-sidecar/templates/` and `skills/ktl-prose/scripts/` on throwaway bundles and repositories. Each module says which contract check it carries:

- `test_apply.py`: the pen, `knowledge-apply.sh` (check 19).
- `test_conventions.py`: `knowledge-conventions.sh` on a bundle that breaks each rule, and on a bundle that keeps every rule with CRLF line endings, through a link and without uv (check 11's synthetic bundle, and check 11c).
- `test_feedback.py`: `knowledge-feedback.sh` (check 12a).
- `test_layouts.py`: the librarian wrapper, the librarian, registrar and release workflows, and the `just lokf-link` recipe, with and without the doorway link (formerly `scripts/test-sidecar-layouts.sh`).
- `test_preflight.py`: `knowledge-preflight.sh`, and each sidecar script's refusal to run under `sh` (check 12).
- `test_prose_check.py`: `prose-check.py` (check 18).
- `test_provenance.py`: `knowledge-provenance.sh` with throwaway keys, its `--unattended` form and parser parity (checks 13, 13a and 22).
- `test_report.py`: `knowledge-report.sh` and the curator's queue (checks 20 and 20a).

Every subprocess runs under an isolated git config, so a global `commit.gpgsign=true` signs no fixture commit, and under a temporary directory of pytest's own. A layout test that needs `just`, `jq`, `node`, `zip` or `unzip` skips and says so when the tool is missing. The conventions tests fail, rather than skip, when uv is missing.

# The other jobs

- `lint-scripts` runs ShellCheck on the whole tree.
- `lint-workflows` runs `actionlint`, pointed by path at this repository's workflows and at the three workflow templates that get copied into other repositories. It would otherwise look only under `.github/workflows/`. It ignores the `copilot-requests` permission, which actionlint 1.7.12 predates. The job also checks that every `uses:` in this repository's workflows and those templates names a commit SHA or image digest rather than a floating tag or branch.
- `smoke-test` installs the skills from the checkout into a throwaway consumer repository through `scripts/smoke-test-install.sh`. It checks that ktl-docent's two scripts come with the install and, run from where the installer put them, label a concept and record a gap in a reader's repository.
- `validate-markdown` runs markdownlint, lychee, and codespell. Codespell skips `knowledge_bundle`, the link to `.lokf/knowledge`, which it already checks at its real path.

The schedule runs weekly because otherwise link rot, an upstream `gh skill` change or drift in the install path would show up only on the next pull request that happens to run.
