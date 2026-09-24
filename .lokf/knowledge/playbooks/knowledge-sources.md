---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/knowledge-sources
title: Knowledge sources
description: Map of the repository locations this bundle was derived from, and how to re-check each on a future refresh.
genre: how-to
resource: .
generated:
  by: process:ktl-librarian
  at: "2026-09-24T16:40:00Z"
verified:
- by: human:noelmcloughlin
  at: "2026-09-10T00:00:00Z"
stale_after: 2027-09-10
---

# Sources swept for this bootstrap discovery pass

| Source | Yields | Re-check by |
| --- | --- | --- |
| `skills/*/SKILL.md` | the four skill Playbooks | re-read each router; a changed step list, guardrail, or frontmatter `description` is a drift signal |
| `skills/*/references/*.md` | detail behind each skill Playbook | diff against the claims in the corresponding concept body |
| `skills/ktl-sidecar/templates/` | what the sidecar skill actually writes: the toolkit dependency and its `[build]` extra, `.gitattributes`, the six scripts (preflight, conventions and its Python half, librarian wrapper, provenance gate, feedback recorder), and the three workflows (registrar, librarian and, since 2026-09-24, release) | diff `pyproject.toml` (the `lokf` floor) and the template lists in the skill's Step 1 and Step 5 tables |
| `README.md`, `docs/install.md`, `docs/repository-layout.md` | project identity and the four-role narrative; the install commands, prerequisites table and pinning rule, on their own page since 2026-09-19 when the README became a front door; the repository tree, likewise on its own page | diff the roles table and the `Read on` table; diff `docs/install.md` against `references/gh-skill-cli.md` and `references/open-skills-cli.md`; diff the tree against the working copy |
| `docs/for-the-curious.md`, `docs/obsidian.md` | the mechanics the README delegates: the four levels of checking and the domain-schema escape hatch; and, since 2026-09-13, the human guide to opening the bundle as a vault of its own with the two plugins | diff the four-levels table against `glossary/trust-label.md` and `ktl-curator/references/domain-schemas.md`; diff `obsidian.md`'s two-vault steps against `playbooks/open-bundle-in-obsidian.md` and `ktl-docent/references/obsidian.md`, which must agree with it |
| `.claude-plugin/plugin.json`, `marketplace.json` | the Claude Code plugin route to the four skills (2026-09-19), carried by `explanation/why-a-distribution-repository.md` | diff the install commands in `README.md` against that concept; check 3c holds the two keyword lists identical |
| `CONTRIBUTING.md` | the contributing playbook | diff the layout table and the pre-PR checklist; since 2026-09-14 the release-process and signing detail live in `docs/releasing.md`/`docs/signing-commits.md` instead, and a word-budget check (`validate-repository.sh` check 10) holds this file to 1000 words |
| `docs/releasing.md`, `docs/signing-commits.md` | the release-process detail (`CONTRIBUTING.md` used to carry it) that `playbooks/releasing.md` and `policies/versioning.md`'s bump rule now derive from; `docs/signing-commits.md` backs the one-sentence summary in `playbooks/contributing.md`, no concept of its own | diff `playbooks/releasing.md` and `policies/versioning.md`'s Conventional-Commits table against `docs/releasing.md`'s |
| `docs/three-lines.md`, `docs/three-lines-critics.md` | the roles placed in the three lines of defence, what an auditor can check and what remains to do and who does it; the critics, quoted, and what a bundle answers and leaves open, on the second page | diff `explanation/three-lines-of-defence.md`; confirm every external link on both pages still resolves and still says what is quoted, and that the cross-links between the two pages still meet their headings |
| `SECURITY.md` | the slim security policy (reporting, supported versions, a surface table) | diff the surface table and the reporting/supported-versions text |
| `docs/threat-model.md` | the shared threat model (2026-09-14 on, replacing `SECURITY.md`'s own design section) - repository hardening, the `human:` attribution gate, prompt-injection guards | diff `policies/threat-model.md`; its section headings are deep-linked by the other two repositories' `SECURITY.md`, so a heading rename here is a breaking change there |
| `AI_COVENANT.md`, `CODE_OF_CONDUCT.md` | governance policies | diff each; both are adapted from upstream documents that may themselves change |
| `.github/workflows/validate.yml`, `publish.yml` | the validation and releasing playbooks | diff job names, triggers, and the pinned action SHAs |
| `.github/workflows/semantic-release.yml`, `.github/scripts/changelog-release.mjs`, `.releaserc.json` | the version-and-changelog automation `playbooks/releasing.md` describes | diff the `release` job's steps, the script's `verifyRelease`/`generateNotes` behaviour, and `.releaserc.json`'s `releaseRules` (which commit types map to which bump) against the concept's Overview; all three sit behind the `release` Environment along with `publish.yml` |
| `.github/workflows/knowledge-registrar.yaml`, `knowledge-librarian.yaml`, `knowledge-release.yaml`, `.lokf/scripts/knowledge-librarian.sh`, `knowledge-conventions.sh`, `knowledge-conventions.py`, `knowledge-preflight.sh`, `knowledge-provenance.sh`, `knowledge-feedback.sh`, `.lokf/.gitattributes` | this repository's dogfooded copies of the workflow templates, scripts and attributes the sidecar skill ships | diff each against its counterpart under `skills/ktl-sidecar/templates/`; all ten are kept byte-identical (check 11 and the preflight report any drift) apart from one value, `knowledge-librarian.yaml`'s `TRUST_LADDER_SKILLS_REF`: since 2026-09-24 the release commit moves that pin in the template only, because `GITHUB_TOKEN` may not push under `.github/workflows/`, and the install step that reads it is skipped here by an `if` on the repository name, since this repository publishes the skills it uses and the wrapper finds them under bare `skills/`. Any other difference is a template bump not yet copied across |
| `.lokf/curators/*.asc`, `*.pub` | the curator public keys `knowledge-provenance.sh` verifies `human:` confirmations against (the first, `noelmcloughlin.asc`, registered 2026-09-24) | consciously excluded as concepts: key material, not knowledge; re-check that `playbooks/ktl-curator-skill.md` and `policies/threat-model.md` still describe the directory as the gate reads it |
| `.github/ISSUE_TEMPLATE/*.md`, `.github/pull_request_template.md`, `.github/dependabot.yml` | contributor intake forms and pin maintenance | consciously excluded as concepts - see note below; re-check only that each template still names all four skills and that its `AI_COVENANT.md` link is absolute |
| `scripts/*.sh` | what the validation playbook claims CI enforces | re-read the assertions; a new check is a gap in the playbook |
| `CHANGELOG.md` | what changed between releases | read the `[Unreleased]` section for behaviour changes not yet reflected in concepts |
| external URLs cited across the repo | the seven Reference concepts | confirm each still resolves and still says what the concept claims |
| `.assets/*.svg` | the README social-preview card, the project's logo mark, and the diagrams the README and `docs/` pages embed | consciously excluded - see note below; re-check only that each diagram still matches the page that embeds it |
| `LICENSE`, `llms.txt`, `docs/examples/` | licensing boilerplate, the agent-facing pointer file, and captured skill transcripts (the docent's; the curator's page is a placeholder) | consciously excluded as concepts - see note below; re-check that `llms.txt` still matches the "For AI agents" callout in `README.md`, and that `docs/examples/docent.md`'s trust-label claims still match `glossary/trust-label.md` |

# Notes for the next run

- **Steady-state refresh (2026-09-24, nineteenth pass)**, on `main` at
  0.25.0, after #75, #76 and #77. Five concepts follow their sources: the
  sidecar playbook names three workflows and the new `gate.md`, the
  librarian playbook the agent credential slot and `--check-refs`, and the
  releasing and validation playbooks and the threat model the release
  workflow; the template and dogfooded-copies rows above name it too. Most
  of the diff was a plain-prose pass over the skills and docs that changed
  no fact, so `security.md`, the curator and docent playbooks and the
  explanations stand as they were.
  `docs/releasing.md`'s follow-up section and `scheduled-task.md`'s step list
  still lag the workflow, as the eighteenth pass and the librarian
  playbook's open question say. `lokf` on PyPI is still `0.8.0`, the floor;
  `.lokf/feedback.md` has no entries; all seven Reference URLs resolve.
- **Steady-state refresh (2026-09-24, eighteenth pass)**, on `main` at
  0.23.1. Most concepts had not been re-checked since #54, #59, #61 and #65
  rewrote `README.md` and `docs/`, and #64 renamed their contents
  mechanically: twenty concepts follow their sources again, nine re-checked
  unchanged. The README-sourced explanations had kept prose no current source
  carries; a pass after any README rewrite should re-read all four. Several
  sources lag #69/#70 themselves (`CONTRIBUTING.md`'s "one exception" and
  pin follow-up, `docs/releasing.md`'s follow-up section, `docs/install.md`'s
  "skill names are unchanged", the sidecar's `automation.md`,
  `portability.md` and `prerequisites.md` on byte-identical copies): flagged,
  not fixed here. `lokf` on PyPI is still `0.8.0`, the floor; upstream `main`
  carries unreleased `--check-ids` work. `.lokf/feedback.md` has no entries.
- **Refresh after the portability work (2026-09-17, twelfth pass)**, on the
  working tree before it merged. The contract, sidecar, curator, librarian,
  docent, threat-model and three-lines concepts and the hosts explanation
  follow their sources: the preflight and the forge-free gate, the
  `.gitattributes` template, three new conventions, the `compatibility`
  fields, the identity routes, and checks 3b, 12 and 13. The rows above
  name the four scripts and the attributes file. `lokf` on PyPI is still
  `0.8.0`; `.lokf/feedback.md` has no entries.
- **Steady-state refresh (2026-09-17, eleventh pass)**, on `main` at the
  0.19.0 release, after #41 and #42 landed. Twenty concepts re-checked; six
  follow their sources: the librarian, curator and docent skills and the
  trust label now describe `revision`, the librarian skill no longer counts
  its classes, and the releasing playbook says what `@semantic-release/exec`
  calls and which changelog heading `publish.yml` compares. Two concepts'
  `generated.at` were set to a time after the change that wrote them and now
  carry #42's merge time. Rows above still hold. `lokf` on PyPI is `0.8.0`,
  matching the floor; `.lokf/feedback.md` has no entries; all seven
  Reference URLs resolve.
- **Steady-state refresh (2026-09-16, tenth pass)**, against the working
  tree's uncommitted changes (nothing has landed since `e52267d`, the
  0.17.1 release). Fifteen concepts re-checked against their current
  sources and found to match, `verified` refreshed; the four re-generated
  today to follow their sources carry today's `generated.at`. Rows above
  follow `EXAMPLES.md` to `docs/examples/docent.md` and admit the new
  `.assets/ktl-three-lines.svg` diagram; the mirror follows the page's
  renamed closing heading, "What remains to do, and who does it". `lokf` on PyPI
  is still `0.7.0`, matching the floor; `.lokf/feedback.md` has no entries;
  all seven Reference URLs resolve.
- **Maintainer edits (2026-09-14, after the ninth pass)**, not a refresh: the
  README count the ninth pass flagged is fixed - the tree moved to
  `docs/repository-layout.md` and says three - and every page and record
  that counted four LOKF repositories now counts three (`knowledge-trust-ladder`,
  KTL Registrar, KTL Curator; a host that installs the skills is not one).
  Prose counts of LOKF's classes and relations left `README.md`, `docs/` and
  the skills' references, so the sixth pass's "grep for the number" lesson
  has only Rule 3 and `trust-fields.md` left to find.
- **Steady-state refresh (2026-09-14, ninth pass)**, against commit `b94a299`
  ("docs(security): improved layout"), landed since the eighth pass.
  `SECURITY.md` shrank from ~1,900 to 471 words: reporting, supported
  versions, and a `Surface | What holds it` table, with the design it used to
  carry moved to a new page, `docs/threat-model.md`. `policies/security.md`
  rewritten to match, and a new concept, `policies/threat-model.md`, added
  for the design page - its four section headings kept as the concept's own
  structure, since the sibling repositories' `SECURITY.md` files deep-link
  them. `playbooks/repository-validation.md`'s check-10 description extended
  (the word budget now covers `SECURITY.md` too, at 900 words) and the
  source-map row above split in two. **Correctness bug found, not fixed
  here**: `README.md`'s own docs-layout listing (`docs/releasing.md`'s row)
  still says "how the **four** repositories release", while the same commit
  fixed `docs/releasing.md`'s own heading and body to say **three** -
  a one-word README fix outside this skill's `.lokf/`-only scope; flagging
  for the maintainer. `lokf` on PyPI is still `0.7.0`, matching the floor;
  `.lokf/feedback.md` has no entries; no other concept referenced the old
  `policies/security.md` structure.
- **Steady-state refresh (2026-09-14, eighth pass)**, against the two commits
  landed since the seventh pass (`423a982`, the log-heading/Open-questions-shape/attribution
  wording fixes now already reflected in `skills/ktl-librarian/SKILL.md`, and `12e5570`, which
  added `.lokf/scripts/knowledge-conventions.sh`). Content re-checked against current sources and
  found unchanged, `verified` refreshed only: `explanation/why-four-roles.md`,
  `explanation/why-a-registrar-role.md`, `explanation/why-a-distribution-repository.md`,
  `glossary/lokf.md`, `glossary/okf.md`, `glossary/trust-label.md`, `glossary/knowledge-bundle.md`,
  `explanation/hosts-and-doorways.md`, `playbooks/open-bundle-in-obsidian.md`,
  `playbooks/ktl-sidecar-skill.md`, `playbooks/ktl-docent-skill.md`,
  `playbooks/ktl-librarian-skill.md`. **Orphan found and fixed**: the dogfooded-workflows row above
  had no entry for the new `.lokf/scripts/knowledge-conventions.sh`, added this pass, byte-identical
  to its template. `.lokf/feedback.md` has no entries. `lokf` on PyPI is still `0.7.0`, matching the
  floor - no bump.
- **Steady-state refresh (2026-09-14, seventh pass)**, against this session's
  uncommitted repository changes (`CONTRIBUTING.md` trimmed to a checklist;
  new `docs/releasing.md`, `docs/signing-commits.md`, `docs/three-lines.md`;
  `validate.yml` gained an action-pinning check; `scripts/validate-repository.sh`
  gained checks 9/9a (sibling deep-link paths) and 10 (word budget); `README.md`
  gained the three-lines-of-defence section). `playbooks/contributing.md`
  rewritten to match the trimmed file and its two new `docs/` links.
  `policies/versioning.md` re-pointed from `CONTRIBUTING.md` to
  `docs/releasing.md` and rewritten: the qualitative patch/minor/major
  definition it carried no longer exists anywhere in the repository, replaced
  by the Conventional-Commits table `docs/releasing.md` and
  `playbooks/releasing.md` already state - human confirmation of 2026-09-10
  left standing per rule. `playbooks/releasing.md`'s stale `CONTRIBUTING.md`
  citation repointed. `playbooks/repository-validation.md` gained the
  action-pinning check and the full ten-check enumeration it had never
  carried (a pre-existing gap, not new drift). Added
  `explanation/three-lines-of-defence.md` for the new page. Orphan sweep also
  fixed two pre-existing `explanation/index.md` gaps unrelated to this diff:
  a missing `why-a-registrar-role.md` bullet, and a title that had drifted
  from the concept's own ("Why four roles" vs "Why four skill roles"). `lokf`
  on PyPI is still `0.7.0` (PyPI's JSON API; `uv pip index` is still not a
  subcommand here), matching the floor - no bump. `.lokf/feedback.md` has no
  entries.
- **Steady-state refresh (2026-09-14, sixth pass)**, whole-repository sweep
  on the same branch. Two `references/` concepts had drifted from the sources
  they describe and were corrected: `linkml.md` (a stale fourteen-class count,
  and no mention of `--schema`) and `lokf-toolkit.md` (same missing flag). The
  lesson for the next run: a class count or a toolkit flag repeated in a
  second concept is drift waiting to happen, so grep the bundle for the number
  and the command whenever either changes upstream. Re-checked and unchanged:
  `lokf-specification.md`, `okf-specification.md`, `glossary/lokf.md`. `lokf`
  on PyPI is `0.7.0`, matching the floor; `.lokf/feedback.md` has no entries.
- **Steady-state refresh (2026-09-14, fifth pass)**, on branch
  `docs/domain-schema-extension`, uncommitted. Swept: a new reference file,
  `skills/ktl-librarian/references/domain-schema.md` (the extending-the-vocabulary
  recipe: a pinned core-schema copy, a LinkML domain schema, frontmatter
  naming the class exactly, the flag wired into the justfile and both
  workflows), and edits to `skills/ktl-librarian/SKILL.md` (Rule 7, the
  audit section, the tooling-version step), `skills/ktl-curator/references/domain-schemas.md`,
  `docs/for-the-curious.md`, `skills/ktl-sidecar/templates/justfile` and
  `CHANGELOG.md` reframing an earlier, more defensive draft of the same
  material - dropped the validator-internals digression and the two
  citations of a named consumer project, in favour of one recipe stated on
  its own terms. `playbooks/ktl-librarian-skill.md` gained a paragraph
  describing this; `playbooks/ktl-curator-skill.md` re-verified, no body
  change (its "domain-schema guidance" line already covers it). **Correctness
  bug found and fixed (this run):** Rule 3's class list named fourteen
  classes, omitting `Role`, while `README.md` and `docs/for-the-curious.md`
  both said fifteen - the standing open question on
  `playbooks/ktl-librarian-skill.md`. Fetched the raw schema
  (`raw.githubusercontent.com/nicholsn/lokf/main/lokf.yaml`) and counted the
  fifteen concept-designating classes directly: `Role` is one of them. Fixed
  Rule 3 in `skills/ktl-librarian/SKILL.md` and closed the open question;
  no other concept named a class count. `lokf` on PyPI is still `0.7.0`;
  `.lokf/feedback.md` has no entries. **Later the same day**, two further
  passes over `skills/ktl-curator/`: `references/review-session.md` states
  how the curation-policy table binds a row to a class, and
  `references/trust-fields.md` (with `SKILL.md`, `references/domain-schemas.md`
  and the librarian's `references/domain-schema.md`) has the vocabulary-fit
  line respect a host's domain schema. Both came from the Obsidian plugins:
  the first from a defect their tests found in this document's own template,
  the second from an open question the curator plugin's bundle raised. So the
  plugin repositories are a live source for this bundle, not only consumers -
  re-read their `CHANGELOG.md` and bundle logs on a pass that touches
  `skills/ktl-curator/`. `playbooks/ktl-curator-skill.md` carries both.
- **Steady-state refresh (2026-09-13, fourth pass)**, preceded by a
  `ktl-sidecar` health check: every Step 1/2/5 file is present, the doorway
  resolves, no placeholder survives, signing is on, and the only template
  difference beyond placeholders is `knowledge-librarian.yaml`'s deliberate
  omission of the install step. The template `pyproject.toml` itself still
  floors `lokf` at `>=0.5.0` while every host laid down from it has moved to
  `>=0.7.0`: a template bump for the maintainer, not a sidecar repair.
  Withdrawn this pass: the claims the third pass derived from commit
  `312190e` (the sidecar *refresh* mode, GPG-or-SSH signing and
  required-checks-off advice in `automation.md`, the librarian's **Drift**
  audit heading, `Role` in Rule 3). That commit sits on the unmerged branch
  `update`, and the checked-out `skills/` does not carry it; restore them
  when it lands. `playbooks/ktl-librarian-skill.md` is a draft again with an
  open question, since `README.md`'s fifteen classes and Rule 3's fourteen
  disagree on this tree. Re-verified against the polished `README.md` and
  the new `docs/obsidian.md`: `explanation/why-four-roles.md`,
  `explanation/why-a-distribution-repository.md`,
  `explanation/why-a-registrar-role.md`, `glossary/lokf.md`. `lokf` on PyPI
  is still `0.7.0`; `.lokf/feedback.md` has no entries.
- **Steady-state refresh (2026-09-13, third pass)**: swept the commits since
  the prior pass plus the uncommitted `README.md` (three more decorative
  `.assets/*.svg`, covered by the existing row, and one sentence on what the
  plugin READMEs now do). Corrected drift in `policies/security.md`,
  `policies/versioning.md`, `playbooks/contributing.md`,
  `playbooks/releasing.md`, `playbooks/ktl-librarian-skill.md`,
  `playbooks/ktl-sidecar-skill.md` and `explanation/why-a-registrar-role.md`
  (see `log.md`). The dogfooded-workflows row above stopped claiming
  byte-identity for `knowledge-librarian.yaml` - the omission of the
  install step is deliberate here, not drift. `lokf` on PyPI is still
  `0.7.0` (PyPI's JSON API; `uv pip index` is still not a subcommand of
  this environment's `uv`), matching the floor; no bump. `.lokf/feedback.md`
  had no entries.
- **Correction (2026-09-12)**: `open-bundle-in-obsidian.md` was rewritten to
  withdraw the "open the repository root as a vault" route (Obsidian ignores
  a symlink whose target is inside the same vault, per its own help) - the
  next run should confirm `skills/ktl-sidecar/SKILL.md` Step 2 still says
  the same, and that the two plugin repositories' READMEs still agree.
  Later the same day the two-name layout rule landed in Step 0 (see
  `explanation/hosts-and-doorways.md`): the next run should check that the
  wrapper script, both workflow templates, and the three dogfooded copies
  still name both `.lokf/knowledge` and `knowledge_bundle` in every pathspec.
- **Targeted addition, not committed (2026-09-11)**: `ktl-sidecar` Step 2
  gained a third root-level pointer - a `knowledge_bundle` symlink to
  `.lokf/knowledge`, so Obsidian's "Open folder as vault" (and any OS folder
  picker that hides dot-directories) has a visible entry point. Added
  `playbooks/open-bundle-in-obsidian.md`; refreshed
  `playbooks/ktl-sidecar-skill.md`'s Overview (Step 2 now reads three
  additions, not two) and re-verified `glossary/knowledge-bundle.md` and
  `playbooks/repository-validation.md` against their now-touched resources
  (`skills/ktl-sidecar/templates/README.md`; `.github/workflows/validate.yml`
  plus new `knowledge_bundle`-excluding args in `.markdownlint-cli2.jsonc` and
  `lychee.toml`, both still consciously excluded as concepts per the note
  below) - no body drift in either, `verified` timestamps refreshed only.
  Scoped to this one addition at the requesting user's direction, not a full
  steady-state sweep - other concepts were not re-checked this run. This
  repository's own `.lokf/` gained the symlink too (git-tracked, matching
  `.lokf/` itself). As of this note, none of it is committed yet - it sits in
  the working tree pending the maintainer's review, so the next run (bootstrap
  or steady-state) should confirm it actually landed before trusting this
  entry.
- **`knowledge-validate.yaml` renamed to `knowledge-registrar.yaml` (2026-09-10,
  third pass)**: prompted by a maintainer decision that the workflow's job -
  keeping bundle records well-formed, never judging their truth - is exactly
  the registrar's role named in `README.md` and
  `explanation/why-a-registrar-role.md`, so its filename should say so.
  Renamed `.github/workflows/knowledge-validate.yaml` and its byte-identical
  template counterpart under `skills/ktl-sidecar/templates/github/` to
  `knowledge-registrar.yaml` (workflow `name:`, self-referencing `paths:`
  filter, and `concurrency.group` updated to match; the `validate` job id/name
  left as-is - still an accurate description of what that job does). Updated
  every cross-reference: this file's source-map row, `explanation/why-a-registrar-role.md`,
  `.github/dependabot.yml`'s manual-bump comment, and the mentions in
  `ktl-librarian/SKILL.md`, `ktl-librarian/references/scheduled-task.md`,
  `ktl-sidecar/SKILL.md`, `ktl-sidecar/references/automation.md`,
  and `ktl-curator/references/review-session.md`. Left historical `log.md`
  and source-map entries referring to the old name alone - they describe past
  events under the name the workflow had at the time. `.github/workflows/validate.yml`
  (the unrelated *repository* CI gate covered by `playbooks/repository-validation.md`)
  merely shares the word "validate" and was left untouched - out of scope for
  this rename.
- **Feedback consumed (2026-09-10, second pass)**: ktl-docent recorded a
  Disagreement - `explanation/why-four-roles.md`'s title/description read as
  the total count of roles, but `README.md`'s own "Four roles, three lines of
  the poem" / "The fifth role, which is not a skill" headers make clear there
  are five roles named (four skill roles + the registrar, explicitly not a
  skill). Not a factual contradiction between concept and source - just an
  ambiguous title left over from before `explanation/why-a-registrar-role.md`
  existed - so fixed directly: retitled to "Why four **skill** roles rather
  than one skill", reworded the description, and added a short clarifying
  paragraph to the body naming both the source's section headers and the
  registrar concept. Updated `knowledge/index.md`'s bullet to match. No
  repository changes outside `.lokf/` since the prior librarian pass
  (`34f01ca`); `lokf` on PyPI is still `0.7.0`, no floor bump needed.
- **Steady-state refresh (2026-09-10)**: re-verified concepts touched since the
  prior pass against their now-current sources. `.github/workflows/knowledge-librarian.yaml`
  and `.lokf/scripts/knowledge-librarian.sh` were split into two least-privilege
  jobs (commit `17d8f3a`) - the agent now runs `contents: read` with no
  persisted credentials, and only a separate, agent-free `publish` job holds
  `contents: write`/`pull-requests: write`. `policies/security.md` was rewritten
  to match, sourced from the workflow/script/`CHANGELOG.md` rather than
  `SECURITY.md` prose, which still describes the prior single-job design in one
  place - flagged under that concept's `## Open questions` since fixing
  `SECURITY.md` itself is outside this skill's `.lokf/`-only scope. `README.md`
  gained a substantive new section, "The fifth role, which is not a skill" (the
  registrar, plus two companion Obsidian plugins, KTL Registrar and LOKF
  Curator) - a real gap, not yet a concept, so added
  `explanation/why-a-registrar-role.md`. Confirmed `skills/ktl-librarian/SKILL.md`'s
  layout diagram and bundle-root `publisher` example already use `person/`/`Person`
  (an earlier fix, commit `dd74943`), consistent with this bundle's own
  `knowledge/index.md`. Version bump to v0.10.0 in `README.md`/`CHANGELOG.md`
  touches no concept - no literal version pin is asserted anywhere in the
  bundle. `lokf` on PyPI is still `0.7.0`, matching the sidecar's floor - no
  bump needed. Noticed but did not act on (out of scope - a prose consistency
  issue between two non-`.lokf/` files, not a bundle fact): `skills/ktl-librarian/SKILL.md`
  still says "For the CURATOR" (uppercase) while the actual
  `knowledge-librarian.yaml` PR body says "For the curator" (lowercase).
- **Steady-state refresh (2026-09-09, second pass)**: re-verified all 18
  internal-resource concepts against their current files (18, not 17 -
  this file itself is one) - no body drift found; two upstream commits since
  the prior pass (`e6d5633`, `b743c84`) turned out to be prose tidying with
  no factual changes this bundle asserts. Also fetched and checked all seven
  external Reference concepts against their live sources for the first time
  (previously unverified since bootstrap) - all still accurate; `gh-skill-cli.md`'s
  "Added in GitHub CLI v2.90.0" claim could not be independently confirmed
  from `cli.github.com` itself (the manual page carries no version-introduced
  note) but was not contradicted either - GitHub's own CLI changelog shows
  `gh skill install` already existed by v2.91.0, consistent with v2.90.0
  without pinning it exactly; leaving as-is, flag if a future run finds the
  exact version.
- **Correctness bug found and fixed (this run)**: `skills/ktl-librarian/SKILL.md`
  Golden Rule 4 mapped `sameAs` to `owl:sameAs`, changed from the correct
  `schema:sameAs` by commit `e6d5633` (self-described as "chore: minor updates
  and improvements", not a deliberate spec change). Cross-checked against both
  the LOKF specification site and the raw `lokf.yaml` schema on GitHub, which
  agree: `sameAs` maps to `schema:sameAs`. This wasn't just a documentation
  slip - `just lokf-check-refs`'s SPARQL query (in both `.lokf/justfile` and
  the `skills/ktl-sidecar/templates/justfile` it was copied from) filters
  on the same predicate list, so any `sameAs` relation would have silently
  never been checked for a dangling target. Fixed in all three places, no
  `sameAs` relations exist in this bundle yet so nothing else changed;
  `just lokf-validate` and `just lokf-check-refs` still pass.
- **Tooling floor bumped (this run)**: `lokf` on PyPI reached 0.7.0 (this
  sidecar's floor was `>=0.5.0`, already resolving to 0.7.0 in practice since
  there was no upper bound). Reviewed the 0.6.0/0.7.0 release notes for
  breaking changes - 0.6.0 requires `mcp>=2.0` (irrelevant here; this sidecar
  never touches the MCP server feature) and 0.7.0 is toolkit-code-unchanged
  from 0.6.0. Bumped the floor to `>=0.7.0` to match what's actually locked;
  `uv sync`, `just lokf-validate`, and `just lokf-check-refs` all still pass.
- **Feedback consumed (this run)**: the one `.lokf/feedback.md` entry (a
  reader's "roadmap for a fifth skill?" Miss) was cleared with no bundle
  change - re-searched the whole repository for "fifth"/"roadmap" and found
  nothing, so recording a placeholder concept would have been inventing a
  fact rather than deriving one, per the docent's own note on the entry.
- **Orphan sweep (this run)**: `LICENSE`, `llms.txt`, and `EXAMPLES.md` had no
  source-map row. Added one (above); all three stay excluded as concepts -
  `LICENSE` restates the Apache-2.0 fact `playbooks/contributing.md` already
  carries, `llms.txt` restates the agent-facing pointer already in `README.md`
  and covered by no concept of its own, and `EXAMPLES.md` is captured docent
  output rather than a repository fact to derive from.
- **Steady-state refresh (2026-09-09, first pass)**: re-verified all 17
  internal-resource concepts against their current files - all still
  accurate; no body changes needed. Consciously skipped
  `.assets/knowledge-trust-ladder-card.svg`, a new decorative image added to
  `README.md` since the bootstrap pass: it carries no reusable knowledge, so
  it gets a source-map row (above) instead of a concept, the same treatment
  as `.markdownlint-cli2.jsonc`/`lychee.toml`.
- **Audit finding, fixed this run**: 12 of 25 concepts had a bare-scalar
  value on a multivalued relation slot (`dependsOn`/`definedBy`/`relatedTo`),
  which is schema-invalid even though it reads naturally - `uv run lokf
  validate knowledge` failed with exactly this error before the fix, and the
  same failure was independently visible in this repository's own
  `Knowledge Bundle Validation` GitHub Actions run. Fixed by wrapping each as
  a one-item list (content unchanged); `ktl-librarian/SKILL.md` Golden Rule
  4 and section 2 now say so explicitly, so it should not recur.
- **Orphan sweep (this run)**: three `.github/` surfaces had no source-map row
  and no concept - the two dogfooded `knowledge-*.yaml` workflows, the issue
  and pull-request templates, and `dependabot.yml`. They now have rows (above)
  and stay excluded as concepts: they are intake forms and maintenance config,
  not reusable knowledge. The sweep found real defects in them, fixed the
  same run (not separately itemized in `CHANGELOG.md`, which for this
  first release describes the shipped feature rather than its pre-release
  fix history): both issue templates offered only
  `ktl-librarian` and `ktl-sidecar` under "Which skill?", all three
  templates linked `AI_COVENANT.md` relatively (which 404s in GitHub's
  rendered forms), and the two shipped workflow templates lagged the pins
  Dependabot had already applied to the dogfooded copies.
- **No `Service`, `Dataset`, `Table`, `Metric`, or `AttestedComputation`
  concepts exist**, and that is correct: this repository ships documentation,
  agent skills, and CI - it runs no API, stores no data, and defines no
  measured quantity. The scaffolded `services/` directory and its two dummy
  concepts were removed rather than filled. If a hosted docs site or a
  published package ever appears, that changes.
- **No `Person`/`Organization` concept.** The maintainer is recorded once as
  the bundle's `publisher` in `index.md`; nothing else links to a person, and
  the skill says to add such concepts only when something does.
- **`base_iri` is a placeholder** (`knowledge-trust-ladder.example`, an RFC 2606
  reserved domain) pending a namespace the project actually controls. It mints
  every concept `@id` here, so migrating it later rewrites all of them - cheap
  now, expensive once anything external links in.
