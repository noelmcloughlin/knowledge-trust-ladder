# Change Log

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
  Knowledge bundle, lokf-librarian skill, Why a registrar role, Security
  policy, Versioning policy. Four of the five shared one root cause - the
  concept cited a single `resource` but the disputed detail actually came
  from a different file the librarian had read (a workflow wrapper,
  `scripts/validate-repository.sh`, or a sibling doc) - worth lokf-librarian
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
  failing and cancelled cases. `playbooks/lokf-librarian-skill.md` follows.
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

* **`playbooks/lokf-curator-skill.md`, `playbooks/lokf-docent-skill.md` and
  `playbooks/repository-validation.md` follow their skills**: the
  conventions script's fifth rule (a local `resource` must exist), the
  curation policy's `Independent re-check:` and `Evidence first:` switches,
  and that the docent reads the second from the policy alone.

* **`playbooks/lokf-sidecar-skill.md` no longer says "the solo maintainer's
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
  `playbooks/lokf-sidecar-skill.md`, `playbooks/lokf-docent-skill.md`,
  `playbooks/lokf-librarian-skill.md`. **Orphan fixed**:
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
  session - `skills/lokf-librarian/references/domain-schema.md` now states
  the recipe (pin the core schema, write a domain schema, name the class
  exactly, wire `--schema` in) without the validator-internals digression or
  the two citations of a named consumer project the first draft carried.
  `playbooks/lokf-librarian-skill.md` gained a paragraph on it; re-verified,
  no change: `playbooks/lokf-curator-skill.md`. **Correctness bug fixed:**
  Rule 3 in `skills/lokf-librarian/SKILL.md` listed fourteen classes,
  omitting `Role`, against `README.md`/`docs/for-the-curious.md`'s fifteen -
  the open question this concept carried since 2026-09-13. Confirmed against
  the raw schema (fifteen concept classes, `Role` among them), fixed Rule 3,
  closed the question. `playbooks/knowledge-sources.md`: run note added.
* **Curation-policy table: how a row binds to a class is now stated.**
  `lokf-curator/references/review-session.md` defined the template but not
  the match. The LOKF Curator plugin, which implements this document, read
  it literally, so the template's own prose rows ("Glossary terms",
  "people") bound nothing. The skill now states the tolerant match - spaces
  and plural form ignored - and `playbooks/lokf-curator-skill.md` records it.
* **The curator skill now reads a host's domain schema too**, closing the
  asymmetry the `lokf-curator` plugin's bundle raised as an open question:
  the librarian's Rule 3 widened its class list from `.lokf/justfile`'s
  `--schema`, while the curator still counted vocabulary fit against the
  fifteen built-ins, so a host with a domain schema saw every domain class
  reported as a misfit for good. `references/trust-fields.md` states the
  widening (read the file; no toolkit, as everywhere else in Step 1), the
  label becomes "doesn't fit the known vocabulary" as the plugin already
  words it, and `SKILL.md`, `references/domain-schemas.md` and the
  librarian's `references/domain-schema.md` (step 5: the skills need no
  telling, the plugins do) follow. `playbooks/lokf-curator-skill.md` records
  it.

## 2026-09-13

* **Steady-state refresh** (librarian pass, no feedback pending), after a
  `lokf-sidecar` health check that found nothing to repair here. Withdrawn:
  the third pass's additions that described commit `312190e`, namely the
  sidecar's *refresh* mode and `automation.md`'s GPG-or-SSH and
  required-checks-off text (`playbooks/lokf-sidecar-skill.md`, and the
  `index.md` bullet), the **Drift** audit heading and `Role` in Rule 3
  (`playbooks/lokf-librarian-skill.md`), and `SECURITY.md`'s "documented
  once, here" paragraph (`policies/security.md`, which now cites the
  librarian-PR wrinkle to `automation.md`, where this tree states it). That
  commit is on the unmerged branch `update`, not in the checked-out
  `skills/`. `playbooks/lokf-librarian-skill.md` is `status: draft` again
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
  `playbooks/lokf-librarian-skill.md` (the new **Drift** audit heading, and
  `Role` restoring the fifteenth class), `playbooks/lokf-sidecar-skill.md`
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
  "Install the pinned lokf-librarian skill" step, since it publishes the
  skills it uses - and a run note added. **Drift audit:** that omission plus
  a two-line comment is the only difference; `knowledge-registrar.yaml`,
  the wrapper and the justfile match their templates. `lokf` on PyPI is
  still `0.7.0`, matching the floor.

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

## 2026-09-12

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
