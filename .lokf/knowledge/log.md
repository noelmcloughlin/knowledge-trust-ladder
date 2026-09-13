# Change Log

## 2026-09-13 (2)

* **Steady-state refresh** (librarian pass, no feedback pending): re-verified
  `playbooks/lokf-sidecar-skill.md`, `explanation/hosts-and-doorways.md`,
  `playbooks/open-bundle-in-obsidian.md`, `explanation/why-four-roles.md` and
  `explanation/why-a-registrar-role.md` against `skills/lokf-sidecar/SKILL.md`
  and the compacted `README.md` from this session's "For the curious" move
  and prose-compaction pass. All five already matched - no content changed,
  only each concept's own `process:lokf-librarian` `verified` event, the two
  hosts-and-doorways/open-bundle-in-obsidian concepts gaining their first
  one. `playbooks/knowledge-sources.md` gained its own `docs/for-the-curious.md`
  row (added this session) and its `generated`/`verified` refreshed to match.
  `glossary/knowledge-bundle.md` was not re-checked - `templates/README.md`'s
  wording tweak this session didn't touch what the term means.

## 2026-09-13

* **The visible layout is retired; one layout, the doorway by default.**
  Hand-edited in session alongside the `lokf-sidecar` change, not a librarian
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
  vault. `playbooks/lokf-sidecar-skill.md` (`generated` refreshed) drops the
  Step 0 layout decision; `playbooks/lokf-librarian-skill.md` (`generated`
  refreshed) restates the second-name rule without the visible layout.
  `index.md`'s two TOC lines follow.
* **Later the same day.** The names of the maintainer's private projects were
  removed from this bundle's notes and from this log: the family this bundle
  describes is the four skills and the two Obsidian plugins, and no host
  outside it is a reference. `README.md`'s Obsidian section was cut back to the
  value of the pairing - Obsidian optional, the exhibition as the workshop's
  output - and the mechanics it carried (what the file reconciler does with a
  link, the second vault, the linked-in arrangement and its cost) moved to
  `lokf-sidecar/references/portability.md`, so that
  `playbooks/open-bundle-in-obsidian.md` derives from a source that states them.
  Every passing mention of Obsidian in the skills and templates now says it is
  optional. `README.md`'s "For the curious" moved to `docs/for-the-curious.md`,
  mirroring the plugin READMEs (`playbooks/knowledge-sources.md` lists it), and
  duplicated prose was compacted in the README, the sidecar skill's Steps 2 and
  6, `portability.md` and this bundle's `open-bundle-in-obsidian.md`, whose
  history section now defers to `explanation/hosts-and-doorways.md`.

## 2026-09-12 (3)

* **Steady-state refresh against the security-hardening pass** (uncommitted
  at the time of this run: 19 files touched, none of them `.lokf/`).
  `policies/security.md` rewritten from the current `SECURITY.md`
  (`generated`/`verified` refreshed): harden-runner now runs on every
  workflow that installs packages or runs third-party/agent code, not only
  `validate.yml`/`publish.yml`; a new `## human: attribution is a claim, not
  a credential` section records `knowledge-registrar.yaml`'s `provenance`
  gate, lokf-curator's `gh api user`-only identity rule, its refusal to run
  unattended, and the optional `attestation` job; the blast-radius paragraph
  now correctly attributes boundary enforcement to the privileged `publish`
  job (re-deriving the allow-list from the patch itself on a clean
  checkout) rather than the wrapper script, and records the wrapper's new
  `.git/config`/`.git/hooks/` snapshot-and-restore and its checks moving
  into a `main()` called last. `playbooks/lokf-docent-skill.md` and
  `playbooks/lokf-librarian-skill.md` (`generated`/`verified` refreshed on
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
  `playbooks/lokf-sidecar-skill.md`, `playbooks/open-bundle-in-obsidian.md`,
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
  concepts sourced from `skills/lokf-curator/` (`playbooks/lokf-curator-skill.md`,
  `glossary/trust-label.md`), `playbooks/repository-validation.md`, and the
  seven external `Reference` concepts - none of their resources appear
  among this pass's changed files, so they were left as last verified.

## 2026-09-12 (2)

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

## 2026-09-12

* **LOKF Enforcer is now LOKF Registrar** (maintainer decision; the plugin
  was renamed for its role before its first release):
  `explanation/why-a-registrar-role.md` (`generated` refreshed),
  `playbooks/lokf-librarian-skill.md`, `playbooks/open-bundle-in-obsidian.md`,
  and `playbooks/knowledge-sources.md` name it so, repository link
  `obsidian-lokf-registrar`. The `diataxis.md` actor the librarian leaves
  alone reads `lokf-registrar/<version>`; a map from a build before the
  rename carries `lokf-enforcer/<version>` and is left alone the same.
  `glossary/knowledge-bundle.md` (`generated` refreshed) now records the
  README's three pictures for the bundle - the librarian's *catalogue*, the
  museum's *exhibition* as the hall visitors are shown into, and the
  *workshop* of sources both stand against - after the README's opening
  section was made to say that its catalogue and its exhibition are the same
  folder. Earlier entries keep the old plugin name.
* **`lokf-scaffolding` renamed to `lokf-sidecar`** (maintainer decision):
  `playbooks/lokf-scaffolding-skill.md` moved to
  `playbooks/lokf-sidecar-skill.md` with its `id`, `title`, `resource`, and
  description updated (the description now records the former name); every
  relation that targeted the old `id` - `why-four-roles.md`'s `about`,
  `lokf-librarian-skill.md`'s `dependsOn`, `open-bundle-in-obsidian.md`'s
  `isPartOf` - re-pointed; `index.md` and `playbooks/index.md` bullets,
  `knowledge-sources.md`'s source-map rows, and `glossary/knowledge-bundle.md`'s
  `resource` path updated. Historical entries below keep the wording they
  had, except where the maintainer's own find-and-replace already touched
  them.
* **Corrected `playbooks/open-bundle-in-obsidian.md`** (rewritten, `generated`
  refreshed): it now states the one supported route - open `knowledge_bundle`
  *itself* as a vault - and records why the repository-root route cannot
  work, citing Obsidian's help on symbolic links ("ignores a symlink ... from
  one folder in the vault to another folder in the same vault") and its
  dot-folder rule. The two companion plugin READMEs had claimed otherwise;
  both were corrected the same day. Added the supported reverse direction
  (linking a repository's bundle *into* a personal vault). Source:
  `skills/lokf-sidecar/SKILL.md` Step 2, whose symlink paragraph was
  rewritten to match.
* **Re-verified** `playbooks/lokf-sidecar-skill.md` against the renamed
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
  `skills/lokf-sidecar/SKILL.md` Step 2, and `references/portability.md`.
  Added `explanation/hosts-and-doorways.md` (`status: draft`, with open
  questions for the maintainer): the two-name rule (`.lokf/knowledge` for
  tools, `knowledge_bundle` for people, one of them a link) and the proposal
  to let a vault or shared-drive host make the visible name the real folder.
* **Third pass, same day - the proposal adopted**: the maintainer asked for
  the recommended fixes to be implemented. `skills/lokf-sidecar/SKILL.md`
  Step 0 now decides the layout by host (code repository: hidden real folder,
  visible doorway link; notes vault or shared folder: visible real
  `knowledge_bundle/`, `.lokf/knowledge` as the tools' link), with Steps 1, 2,
  3, 5 and 6 marked where the visible layout differs; the wrapper script and
  both workflow templates name the bundle under both names (a git pathspec
  never traverses a symlink; `git add` refuses an empty pathspec, hence a
  guard), the registrar triggers on `knowledge_bundle/**`, and the justfile
  gained `just lokf-link`. `skills/lokf-librarian/SKILL.md` gained the
  layout note and a rule to leave LOKF Enforcer's Obsidian affordances
  (`<!-- lokf:related -->` blocks, `diataxis.md`) alone. Updated
  `explanation/hosts-and-doorways.md` (proposal → adopted, open questions
  resolved), `playbooks/open-bundle-in-obsidian.md` (visible-layout section),
  `playbooks/lokf-sidecar-skill.md` (Step 0 decision) and
  `playbooks/lokf-librarian-skill.md` (also corrected "14-class" to the
  schema's 15, matching `README.md`'s earlier fix). `templates/README.md`
  and this sidecar's `README.md` explain the layout in one sentence.
* **Fourth pass - the vault-in-a-subfolder host, and layout tests.** `lokf-sidecar` Step 0
  gained the case of a vault one level below the repository root (the maintainer's
  own notes vault, `vault/` here): the real folder goes inside the vault,
  `vault/knowledge_bundle/`, the link is `.lokf/knowledge -> ../vault/knowledge_bundle`, the
  justfile's new `visible` variable names that path for `just lokf-link`, and Step 5's three files
  name it in place of `knowledge_bundle`. `explanation/hosts-and-doorways.md` gained the table row
  and the note that `scripts/test-sidecar-layouts.sh` now pins both layouts - the wrapper's
  boundary check, both workflows' pathspecs, and the recipe - from the repository-contract check;
  `playbooks/open-bundle-in-obsidian.md` and `playbooks/lokf-sidecar-skill.md` say the same in a
  clause. The README's Obsidian section now states the two-name rule outright and names the vault
  the workshop and the bundle the exhibition. `explanation/why-a-registrar-role.md` no longer files
  LOKF Curator under the registrar or calls the plugin a curator: the Enforcer is the registrar in the
  editor, the Curator plugin is the person's assistant, and the curator is always a person.
* **Vocabulary**: `glossary/knowledge-bundle.md` now records the museum synonyms the READMEs
  use - the bundle is the *exhibition*, a concept an *exhibit*, the sources or notes the
  *workshop* - so the three words are defined once, at the term of record.

## 2026-09-11

* **`knowledge_bundle` symlink added to `lokf-sidecar` Step 2**: a third
  root-level pointer, alongside `llms.txt` and the README aside - `ln -s
  .lokf/knowledge knowledge_bundle`, a visible entry point for humans and
  their tools, chiefly Obsidian's "Open folder as vault," which like most OS
  folder pickers hides dot-directories by default. `templates/gitignore` now
  excludes `.obsidian/`, which Obsidian writes through the link into the real
  `.lokf/knowledge/.obsidian/` when used as a vault. Added
  `playbooks/open-bundle-in-obsidian.md` and refreshed
  `playbooks/lokf-sidecar-skill.md`'s Overview (Step 2 now three
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
  `skills/lokf-sidecar/templates/github/`, and updated every
  cross-reference across the four skills' `SKILL.md`/`references/` files,
  `.github/dependabot.yml`, `explanation/why-a-registrar-role.md`, and this
  file's own source-map row. Historical `log.md`/source-map entries that
  named the old workflow stay as they were, describing what it was called
  at the time.

* **Feedback consumed - Disagreement fixed**: lokf-docent flagged that
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
  (LOKF Enforcer, LOKF Curator), rather than by a fifth skill. No prior
  concept captured this; `explanation/why-four-roles.md` gained a `relatedTo`
  link to it.
* **Steady-state refresh**: re-verified `playbooks/releasing.md`,
  `playbooks/lokf-librarian-skill.md`, `playbooks/lokf-docent-skill.md`,
  `playbooks/repository-validation.md`, and `policies/versioning.md` against
  their current sources - no drift found - and refreshed each concept's own
  `process:lokf-librarian` `verified` event (human `verified` events left
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
  `playbooks/lokf-librarian-skill`, `references/lokf-specification`. Sent 0
  back, corrected 0, retired 0. One evidence-citation error caught mid-session
  (a quote presented as coming from a single "Section 1" of
  `lokf-librarian/SKILL.md` was actually a synthesis drawn from three separate
  places in the file) - re-quoted properly and the underlying claim held; a
  one-off slip in how evidence was presented, not a defect in the concept or
  a pattern worth changing lokf-librarian's instructions over.
* **AI_COVENANT.md gained a "Repository-Owned Agent Automation" section**:
  raised by the maintainer after noticing this same run's own commit carried
  an AI co-authorship trailer the covenant already discourages (fixed by
  amending that commit). The deeper gap: the covenant's model is a person
  drafting with AI help then submitting, but `lokf-librarian` (scheduled or
  interactive) and `lokf-curator` both have an *agent* executing the actual
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
  `schema:sameAs` to `owl:sameAs` in `lokf-librarian/SKILL.md`'s Golden Rule
  4 - confirmed wrong against both the LOKF specification site and the raw
  `lokf.yaml` schema. Not just documentation: `just lokf-check-refs`'s SPARQL
  query filtered on the same wrong predicate in both `.lokf/justfile` and the
  `lokf-sidecar` template it's copied from, so a `sameAs` relation's
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
  `process:lokf-librarian` `verified` event to each. Consciously excluded a
  new decorative asset, `.assets/lokf-agent-skills-card.svg`, recording it
  in `playbooks/knowledge-sources.md` instead of as a concept.
* **Audit**: `uv run lokf validate knowledge` (previously unavailable) found
  12 of 25 concepts using a bare scalar on a multivalued relation slot
  (`dependsOn`/`definedBy`/`relatedTo`) - schema-invalid despite reading
  naturally. Fixed by wrapping each as a one-item list, content unchanged.
  Same failure was independently visible in this repository's own
  `Knowledge Bundle Validation` GitHub Actions run. Clarified
  `lokf-librarian/SKILL.md` Golden Rule 4 and section 2 so it doesn't recur.
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
  guard to `lokf-librarian/SKILL.md` (resolve only from the source an entry
  names, never its wording), and the same guard for the other two content-
  fetching paths in `lokf-curator/SKILL.md` and `lokf-docent/SKILL.md`.
  `SECURITY.md` gained a **Prompt-injection guards** section naming all three
  plus the unattended-write-path blast-radius containment and what remains
  unguarded (ordinary repository content, a reader's own phrasing); refreshed
  `policies/security.md` to match.
