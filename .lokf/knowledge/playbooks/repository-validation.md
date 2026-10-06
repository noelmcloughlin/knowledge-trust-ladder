---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/repository-validation
title: Repository validation
description: "What CI checks on every pull request and weekly: the repository contract, the Agent Skills spec, shell and workflow linting, the install smoke test, and Markdown, link and spelling checks."
genre: how-to
resource: .github/workflows/validate.yml
generated:
  by: process:ktl-librarian
  at: "2026-10-06T11:10:52Z"
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
  at: "2026-10-06T11:10:52Z"
---

# Overview

`validate.yml` runs five jobs on every pull request, every push to `main`, weekly, and on demand. `validate-skills` runs `scripts/validate-repository.sh`, twenty-one numbered checks, several with lettered sub-checks:

- Exactly five skill directories with a case-correct `SKILL.md` in each.
- Frontmatter `name` matching its directory.
- Check 3b, added 2026-09-17: a `compatibility` field of at most 500 characters naming what the skill needs.
- Check 3c, added 2026-09-19: each skill's `description` ending in a `Keywords:` list within the spec's 1024 characters, with `.claude-plugin/plugin.json` and `marketplace.json` carrying one identical keyword list. Catalogs have no tag field, so that list is the only tag they read.
- No duplicate `SKILL.md`.
- Every relative Markdown link under `skills/` resolving (fenced examples excluded).
- ShellCheck-clean scripts.
- Every stated LOKF class count agreeing with `ktl-librarian/SKILL.md` Rule 3 (and with `ktl-curator/references/trust-fields.md`'s own enumeration).
- The sidecar layout tests. They also run the registrar's `provenance` step as the template has it, with `gh` stubbed, and the wrapper's unattended check, retrieval call, quiet skip and hand-off, after whatever the agent left at the output paths is gone.
- The paths the two sibling plugin repositories deep-link into by URL still existing and, when those siblings are cloned beside this repo, that the list of them is complete.
- Check 10, extended 2026-09-14 when `SECURITY.md`'s design moved to `docs/threat-model.md`: `CONTRIBUTING.md` and `SECURITY.md` each staying under their own word budget (1000 and 900).
- Check 11, added 2026-09-14: this repository's copies of the three knowledge workflows (the release workflow since 2026-09-24), the nine sidecar scripts, the two `.lokf/m365/` files (since 2026-09-24) and `.lokf/.gitattributes` staying byte-identical to their templates.

  Since 2026-09-24 the comparison leaves out the librarian workflow's skills pin, which the release commit moves in the template only. The pin is two values, `TRUST_LADDER_SKILLS_REF` and `TRUST_LADDER_SKILLS_SHA`. Check 11 also requires the two Python halves, `knowledge-apply.py` and `knowledge-conventions.py`, to pin the same PyYAML release and the same cut-off date. It fails up front, naming the cause, when `uv` is missing. It shows `knowledge-conventions.sh`:

  - passing on this bundle;
  - failing on a synthetic bundle breaking each of its thirteen rules;
  - reading a CRLF bundle as it reads LF;
  - reading a bundle reached through a link;
  - without `uv`, running its own rules and saying which it skipped.

  The breaks are:

  - a vanished `resource`;
  - a `revision` naming no commit;
  - a duplicate `id`;
  - an upper-case path;
  - a byte order mark;
  - a missing frontmatter block;
  - an event spelt with a quoted key, a tag or a comment beside a field (a comment on its own line, or a `#` in a quoted value, shown to pass);
  - a time later than the commit that recorded it or, uncommitted, in the future (rule 11, since 2026-09-24, with a time before its commit shown to pass);
  - an index bullet left behind by an edited description, in the folder's index and in the root's (rule 12, with a bullet that still agrees, a concept no index lists and a line that lists two concepts shown to pass);
  - a confirmed concept edited after its confirmation with `generated` left behind (rule 13, since 2026-10-04, with a person's note, KTL Registrar's block, a requoted title, a restamp and a second confirmation shown to pass);
  - breaks of the first four rules.

  The twelfth conventions rule holds an index bullet to its concept's title and description, and the thirteenth holds a confirmed concept to the text its person confirmed. The script delegates eight of the rules (2, 3, 4, 7, 9, 10, 12 and 13), the first six since 2026-09-17, to `knowledge-conventions.py` through `uv run`: a real YAML parse in place of grep and awk. That is proven on the layouts the script used to miss:

  - a multi-line flow item with an unquoted `at`;
  - a number for an `at`;
  - a block that does not parse, reported on one line;
  - a list where a mapping should be.

  A second librarian event in a body code fence is not counted.
- Check 11a, added 2026-10-05: ktl-docent's copies of `knowledge-report.sh` and `knowledge-feedback.sh` matching their templates, and no ktl-docent page running a script under `.lokf/scripts/`. Each copy, run from outside the repository as an installer leaves it, labels a concept and records a gap in the repository it is run in.
- Check 11b, same day: every page that gives the no-Python schema URL pinning one commit, never a tag or a branch, and naming the tag of the `lokf` floor that the sidecar's `pyproject.toml` template sets.
- Check 12, added 2026-09-17: `knowledge-preflight.sh`:

  - ending on its summary line here, on a bare directory, and warning on a CRLF bundle;
  - counting a linked bundle;
  - reading `commit.gpgsign = yes` as signing on;
  - warning when the conventions script's Python half is missing beside it;
  - warning when `knowledge-feedback.sh` is missing from a sidecar's `scripts/`, and falling silent once it is there;
  - warning when the registrar workflow is installed but git holds no `.lokf/uv.lock`, and falling silent once it does;
  - stopping on one line under `sh` (as the other five scripts do);
  - every line it can print as missing or a warning having a row on `ktl-sidecar/references/prerequisites.md`.
- Check 12a, added 2026-09-23: `knowledge-feedback.sh`:

  - refusing to write where `.lokf/` has no `knowledge/`;
  - creating `feedback.md` on the first entry under today's UTC date;
  - putting a newer entry above an older one within a day, and a newer day above an older one;
  - leaving a day ahead of today, from a clock ahead of this one, where it is, and filing today once beneath it;
  - reading a day heading past a trailing space;
  - accepting a lower-case kind and a dotted login as the gates read them;
  - repeating no entry's text on its own output;
  - collapsing a multi-line entry to one line, so a newline cannot forge a second entry;
  - refusing a third kind, an attribution that is not a login, an empty entry, a call with no text and a root that does not exist, while leaving the file untouched;
  - exiting 1 rather than 2 on a lock another run holds and on a read-only bundle (skipped as root, whom no chmod keeps out);
  - leaving no temporary file or lock behind.
- Check 13, same day: `knowledge-provenance.sh` passing a confirmation signed by the curator on file, with a GPG key, a GPG signing subkey, or an SSH key.

  The script fails:

  - an unsigned confirmation;
  - a concept path git has to quote (refused rather than passed unread; a name with a byte above 0x7f is read);
  - an unknown id;
  - an id the gate cannot look up (which it used to skip);
  - a wrong key of either kind;
  - an id's own key registered in the same range as their confirmation.

  Another curator's key added alongside passes.

  Events are read whole from the frontmatter, against every parent of a commit, and keyed by the concept's `id` rather than found as added `by:` lines. So the script fails a re-dated confirmation nobody signed, an unsigned flow-style event, a flow-style human `generated` record and an event a merge adds that neither side held. It passes the same re-date signed by its curator, a confirmed concept that merely moved, an example event in a body code fence and a merge that brings in a signed confirmation.

  All of this runs with throwaway keys, and where there is no `.lokf/curators/` the script says so and passes. A removed confirmation needs its curator's signature as an added one does, whether the event is struck out or its concept deleted, and a person's `generated` record may give way only to another person's.
- Check 13a: the same script's `--unattended` form refusing, with no key at all, a change that adds, changes or removes a person's event or note, or rewrites text a person wrote.
- Check 14, added 2026-09-17: `CHANGELOG.md` never carrying two headings for one released version. It also covers `changelog-release.mjs promote` folding a second qualifying push into the top released section by subsection, rather than adding a second heading for it, when that version carries no tag yet. The fold is proven in a throwaway repository, and a version is left alone once it is tagged.
- Check 15, added 2026-09-18: the librarian template's `TRUST_LADDER_SKILLS_REF` naming one of this repository's two newest released versions, since a host installs the skill from that pin, and without the check the pin goes out of date unnoticed. It sat at `v0.9.0` through `v0.19.2`.

  The check allows two headings of slack, not one, because the newest heading exists before its tag does. `semantic-release.yml` promotes it on merge and `publish.yml` creates the tag later, so during the publish that runs this contract the only pin a host could clone is the heading below the top.

  Since 2026-09-23 the check also reads the pinned tag itself for the path the install step copies out of it (`skills/ktl-librarian`), and skips that half where the tag is not on the clone. A rename leaves a real version and a real path that are not in the same tag, which is how the pin sat at `v0.21.0` after the `lokf-*` skills became `ktl-*`.

  Check 15 also requires the template's `TRUST_LADDER_SKILLS_SHA` to be the commit the pinned tag names, and skips that where the tag is not on the clone. It also checks that the install step compares the commit it cloned with that one, and that `semantic-release.yml` and `scripts/sync-sidecar.sh` each move the commit with the tag.
- Check 16, added 2026-09-19: the repository's old name staying out of every file but the ones that record history: `CHANGELOG.md`, the bundle's `log.md`, `rename-plan.md`, the contract script itself, and one "formerly" line in `docs/install.md`.
- Check 16a, added 2026-09-23: the skills' and plugins' old `lokf-` names staying out of every file but `CHANGELOG.md` and the contract script.
- Check 16b: no file calling a role, skill or repository of KTL a LOKF one, apart from `CHANGELOG.md`, the bundle's `log.md`, the source map (`playbooks/knowledge-sources.md`) and the contract script.
- Check 17, added 2026-09-24: the Microsoft 365 Copilot skills:

  - no `SKILL.md` anywhere under the sidecar's `templates/`, so no installer lists an instructions file as a skill;
  - every instructions file under `templates/m365/` carrying ktl-docent's trust-label table word for word;
  - `knowledge-m365.sh` building `ktl-docent-m365` from this repository's own bundle within Copilot's limits;
  - where `zip` is installed, the same zip bytes under another time zone and umask, as a release asset must.
- Check 18: `ktl-prose`'s `prose-check.py` exercised as the conventions script is at check 11:

  - reporting a dash, a long sentence, a long paragraph, a figure of speech, a stock phrase and a character no reader sees, with the line each is on;
  - staying quiet on what the hand passes kept;
  - refusing, with `--before` or `--against HEAD`, a rewording that touches anything but wording, a frontmatter byte, a character no reader sees, or a concept a person wrote or confirmed.

  Check 18 also requires a comparison that passes to give each version's word count. It also requires a changed day or month written out, and a text cut by more than a fifth, to be notes for the reader and never refusals.
- Check 19: `knowledge-apply.sh`, the librarian's only pen, exercised on a throwaway bundle:

  - each operation applied;
  - each refusal refused;
  - a dry run writing nothing;
  - a handled feedback entry added to the ledger with its question in a code span;
  - `resolve` withdrawing the librarian's own question and never a person's note;
  - a root index shaped by hand keeping its shape;
  - the hand-off reaching the file `--handoff` names as plain single lines, and never the bundle;
  - `--format` printing the block `references/patch.md` shows.

  Check 19 also requires the pen to refuse a patch that would change a person's record, whatever its operations, or that handles more than ten reader entries. The pen must write back a frontmatter value no operation named as the file held it, and keep every character a reader cannot see out of a reader's question and a hand-off line.
- Check 20: `knowledge-report.sh` on a throwaway repository:

  - printing the health line, each label, the work list, the changes against `HEAD` and the retrieval score;
  - counting a source as moved by commit order, never by clock;
  - telling, with `quiet`, a week with nothing waiting from one with work, where a note no longer counts once the librarian has stamped its concept after it.

  Check 20 also requires `changes` to say what a change does to each confirmed concept's label. The report script must score a retrieval reply against what the ledger expects, never against a line of the reply, and without a question whose concept has left the bundle. `quiet` and the work list must set aside a moved source that a question of the librarian's names, and what a person declined by closing the workflow's pull request, until it changes again.
- Check 21: no tracked file holding a character a reader cannot see, such as the right-to-left override, which the "Trojan Source" attack uses to make code read differently from how it runs.

The job sets up `uv`, runs the contract, then confirms `gh skill` is available, and then runs `gh skill publish --dry-run`.

The other jobs:

- `lint-scripts` runs ShellCheck on every script.
- `lint-workflows` runs `actionlint`, pointed by path at this repository's workflows and at the three workflow templates that get copied into other repositories. It would otherwise look only under `.github/workflows/`. Since 2026-09-24 it ignores the `copilot-requests` permission, which actionlint 1.7.12 predates. Since 2026-09-14 the job also runs a check that every `uses:` in this repository's workflows and those templates names a commit SHA or image digest rather than a floating tag or branch.
- `smoke-test` installs the skills from the checkout into a throwaway consumer repo via `scripts/smoke-test-install.sh`. It checks that ktl-docent's two scripts come with the install and, run from where the installer put them, label a concept and record a gap in a repository that holds only a bundle.
- `validate-markdown` runs markdownlint, lychee, and codespell.

The weekly schedule exists because link rot, an upstream `gh skill` change, or install-path drift would otherwise be found only on the next incidental pull request.
