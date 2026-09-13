---
type: Playbook
id: https://lokf-agent-skills.example/knowledge/playbooks/knowledge-sources
title: Knowledge sources
description: Map of the repository locations this bundle was derived from, and how to re-check each on a future refresh.
genre: how-to
resource: .
generated:
  by: process:lokf-librarian
  at: "2026-09-13T15:00:00Z"
verified:
- by: process:lokf-librarian
  at: "2026-09-13T15:00:00Z"
- by: human:noelmcloughlin
  at: "2026-09-10T00:00:00Z"
stale_after: 2027-09-10
---

# Sources swept for this bootstrap discovery pass

| Source | Yields | Re-check by |
| --- | --- | --- |
| `skills/*/SKILL.md` | the four skill Playbooks | re-read each router; a changed step list, guardrail, or frontmatter `description` is a drift signal |
| `skills/*/references/*.md` | detail behind each skill Playbook | diff against the claims in the corresponding concept body |
| `skills/lokf-sidecar/templates/` | what the sidecar skill actually writes; the toolkit dependency and its `[build]` extra | diff `pyproject.toml` (the `lokf` floor) and the template list in the skill's Step 1 table |
| `README.md` | project identity, the four-role narrative, versioning policy, install commands | diff the roles table and the Versioning section |
| `docs/for-the-curious.md` | the mechanics the README delegates: the four levels of checking and the domain-schema escape hatch | diff the four-levels table against `glossary/trust-label.md` and `lokf-curator/references/domain-schemas.md` |
| `CONTRIBUTING.md` | the contributing playbook | diff the layout table and the pre-PR checklist |
| `SECURITY.md` | the security policy | diff the hardening bullets |
| `AI_COVENANT.md`, `CODE_OF_CONDUCT.md` | governance policies | diff each; both are adapted from upstream documents that may themselves change |
| `.github/workflows/validate.yml`, `publish.yml` | the validation and releasing playbooks | diff job names, triggers, and the pinned action SHAs |
| `.github/workflows/semantic-release.yml`, `.github/scripts/changelog-release.mjs`, `.releaserc.json` | the version-and-changelog automation `playbooks/releasing.md` describes | diff the `release` job's steps, the script's `verifyRelease`/`generateNotes` behaviour, and `.releaserc.json`'s `releaseRules` (which commit types map to which bump) against the concept's Overview; all three sit behind the `release` Environment along with `publish.yml` |
| `.github/workflows/knowledge-registrar.yaml`, `knowledge-librarian.yaml` | this repository's dogfooded copies of the two workflow templates the sidecar skill ships | diff each against its counterpart under `skills/lokf-sidecar/templates/github/`; they are deliberately kept byte-identical, so any difference is either a template bump not yet copied across or a divergence `.github/dependabot.yml` should explain |
| `.github/ISSUE_TEMPLATE/*.md`, `.github/pull_request_template.md`, `.github/dependabot.yml` | contributor intake forms and pin maintenance | consciously excluded as concepts - see note below; re-check only that each template still names all four skills and that its `AI_COVENANT.md` link is absolute |
| `scripts/*.sh` | what the validation playbook claims CI enforces | re-read the assertions; a new check is a gap in the playbook |
| `CHANGELOG.md` | what changed between releases | read the `[Unreleased]` section for behaviour changes not yet reflected in concepts |
| external URLs cited across the repo | the seven Reference concepts | confirm each still resolves and still says what the concept claims |
| `.assets/*.svg` | decorative images (e.g. the README social-preview card) | consciously excluded - see note below; re-check only that the row still applies if the asset's purpose changes |
| `LICENSE`, `llms.txt`, `EXAMPLES.md` | licensing boilerplate, the agent-facing pointer file, and captured docent transcripts | consciously excluded as concepts - see note below; re-check that `llms.txt` still matches the "For AI agents" callout in `README.md`, and that `EXAMPLES.md`'s trust-label claims still match `glossary/trust-label.md` |

# Notes for the next run

- **Rename and correction (2026-09-12)**: `skills/lokf-scaffolding/` is now
  `skills/lokf-sidecar/` (frontmatter `name: lokf-sidecar`); every row above
  already uses the new path. `open-bundle-in-obsidian.md` was rewritten to
  withdraw the "open the repository root as a vault" route (Obsidian ignores
  a symlink whose target is inside the same vault, per its own help) - the
  next run should confirm `skills/lokf-sidecar/SKILL.md` Step 2 still says
  the same, and that the two plugin repositories' READMEs still agree.
  Later the same day the two-name layout rule landed in Step 0 (see
  `explanation/hosts-and-doorways.md`): the next run should check that the
  wrapper script, both workflow templates, and the three dogfooded copies
  still name both `.lokf/knowledge` and `knowledge_bundle` in every pathspec.
- **Targeted addition, not committed (2026-09-11)**: `lokf-sidecar` Step 2
  gained a third root-level pointer - a `knowledge_bundle` symlink to
  `.lokf/knowledge`, so Obsidian's "Open folder as vault" (and any OS folder
  picker that hides dot-directories) has a visible entry point. Added
  `playbooks/open-bundle-in-obsidian.md`; refreshed
  `playbooks/lokf-sidecar-skill.md`'s Overview (Step 2 now reads three
  additions, not two) and re-verified `glossary/knowledge-bundle.md` and
  `playbooks/repository-validation.md` against their now-touched resources
  (`skills/lokf-sidecar/templates/README.md`; `.github/workflows/validate.yml`
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
  template counterpart under `skills/lokf-sidecar/templates/github/` to
  `knowledge-registrar.yaml` (workflow `name:`, self-referencing `paths:`
  filter, and `concurrency.group` updated to match; the `validate` job id/name
  left as-is - still an accurate description of what that job does). Updated
  every cross-reference: this file's source-map row, `explanation/why-a-registrar-role.md`,
  `.github/dependabot.yml`'s manual-bump comment, and the mentions in
  `lokf-librarian/SKILL.md`, `lokf-librarian/references/scheduled-task.md`,
  `lokf-sidecar/SKILL.md`, `lokf-sidecar/references/automation.md`,
  and `lokf-curator/references/review-session.md`. Left historical `log.md`
  and source-map entries referring to the old name alone - they describe past
  events under the name the workflow had at the time. `.github/workflows/validate.yml`
  (the unrelated *repository* CI gate covered by `playbooks/repository-validation.md`)
  merely shares the word "validate" and was left untouched - out of scope for
  this rename.
- **Feedback consumed (2026-09-10, second pass)**: lokf-docent recorded a
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
  registrar, plus two companion Obsidian plugins, LOKF Registrar and LOKF
  Curator) - a real gap, not yet a concept, so added
  `explanation/why-a-registrar-role.md`. Confirmed `skills/lokf-librarian/SKILL.md`'s
  layout diagram and bundle-root `publisher` example already use `person/`/`Person`
  (an earlier fix, commit `dd74943`), consistent with this bundle's own
  `knowledge/index.md`. Version bump to v0.10.0 in `README.md`/`CHANGELOG.md`
  touches no concept - no literal version pin is asserted anywhere in the
  bundle. `lokf` on PyPI is still `0.7.0`, matching the sidecar's floor - no
  bump needed. Noticed but did not act on (out of scope - a prose consistency
  issue between two non-`.lokf/` files, not a bundle fact): `skills/lokf-librarian/SKILL.md`
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
- **Correctness bug found and fixed (this run)**: `skills/lokf-librarian/SKILL.md`
  Golden Rule 4 mapped `sameAs` to `owl:sameAs`, changed from the correct
  `schema:sameAs` by commit `e6d5633` (self-described as "chore: minor updates
  and improvements", not a deliberate spec change). Cross-checked against both
  the LOKF specification site and the raw `lokf.yaml` schema on GitHub, which
  agree: `sameAs` maps to `schema:sameAs`. This wasn't just a documentation
  slip - `just lokf-check-refs`'s SPARQL query (in both `.lokf/justfile` and
  the `skills/lokf-sidecar/templates/justfile` it was copied from) filters
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
  `.assets/lokf-agent-skills-card.svg`, a new decorative image added to
  `README.md` since the bootstrap pass: it carries no reusable knowledge, so
  it gets a source-map row (above) instead of a concept, the same treatment
  as `.markdownlint-cli2.jsonc`/`lychee.toml`.
- **Audit finding, fixed this run**: 12 of 25 concepts had a bare-scalar
  value on a multivalued relation slot (`dependsOn`/`definedBy`/`relatedTo`),
  which is schema-invalid even though it reads naturally - `uv run lokf
  validate knowledge` failed with exactly this error before the fix, and the
  same failure was independently visible in this repository's own
  `Knowledge Bundle Validation` GitHub Actions run. Fixed by wrapping each as
  a one-item list (content unchanged); `lokf-librarian/SKILL.md` Golden Rule
  4 and section 2 now say so explicitly, so it should not recur.
- **Orphan sweep (this run)**: three `.github/` surfaces had no source-map row
  and no concept - the two dogfooded `knowledge-*.yaml` workflows, the issue
  and pull-request templates, and `dependabot.yml`. They now have rows (above)
  and stay excluded as concepts: they are intake forms and maintenance config,
  not reusable knowledge. The sweep found real defects in them, fixed the
  same run (not separately itemized in `CHANGELOG.md`, which for this
  first release describes the shipped feature rather than its pre-release
  fix history): both issue templates offered only
  `lokf-librarian` and `lokf-sidecar` under "Which skill?", all three
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
- **`base_iri` is a placeholder** (`lokf-agent-skills.example`, an RFC 2606
  reserved domain) pending a namespace the project actually controls. It mints
  every concept `@id` here, so migrating it later rewrites all of them - cheap
  now, expensive once anything external links in.
