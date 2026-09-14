# Changelog

All notable changes to this repository are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows the rules in [README.md](README.md#versioning). All skills release together under one tag.

## [Unreleased]

### Added

- **`lokf-librarian/references/domain-schema.md`**: how to extend the vocabulary into a domain - a LinkML schema importing a pinned `lokf.yaml`, `--schema` wired into the justfile and both workflows, both plugins' *Known LOKF types* settings told, and what it leaves undone for the graph. The curator's `domain-schemas.md` says when; this says how. Rule 3 now reads the host's justfile for a `--schema` and counts that schema's `Concept` descendants as vocabulary.

### Fixed

- **Rule 3 in `lokf-librarian/SKILL.md` listed fourteen classes, omitting `Role`**, while `README.md` and `docs/for-the-curious.md` said fifteen. Confirmed against the raw schema and corrected; the skills now teach one number.

### Changed

- **`README.md` polished, not restructured.** Role names carry the emphasis; the docent's job and the trust labels are each said once; the plugin table maps onto the four levels of checking; *Where the bundle lives* is a section of its own; the layout lists every workflow and the measured size of each `SKILL.md`. The Obsidian section moves to `docs/obsidian.md`, with the two-vaults picture the plugin READMEs use, and the README keeps one paragraph and a link.

## [0.16.0] - 2026-09-13

### Changed

- **One layout on every host.** `.lokf/knowledge/` is always the real folder, and the `knowledge_bundle` doorway link beside it is created by default again (Step 2). Step 0 no longer asks what kind of host it is in; Step 6 reports whether the doorway was made and the one command if not.
- **`just lokf-link`** creates or recreates that doorway, idempotently, refusing a name already taken. Its `visible` variable is gone.
- **`lokf-docent` gains `references/obsidian.md`**: the two-vault answer, plus `lokf-sidecar` named as the way to make a missing link. A missing link is never a feedback entry.
- **Shared-folder guidance consolidated** into `lokf-sidecar/references/portability.md`, Obsidian included: sync services carry `.lokf/` but drop links, so the doorway is per machine.
- **`README.md` restructured.** "Where the bundle lives" (host-agnostic) and "…and where it meets an Obsidian vault" (optional, two vaults) replace the combined section; "For the curious" moves to `docs/for-the-curious.md`.

### Removed

- **The visible layout** (0.15.0) - a real `knowledge_bundle/` folder inside a vault. Obsidian indexes it like any other folder, so the exhibition leaked into the workshop's link suggestions, graph and search. Step 0's host decision, the `visible` variable and two layout-test cases go with it.
- References to the maintainer's private vault: the family this repository describes is the four skills and the two plugins.

## [0.15.0] - 2026-09-12

### Changed

- **`lokf-curator/references/domain-schemas.md`** gains "When the domain already has a schema": a regulated domain may already have a LinkML vocabulary of its own and a domain schema then imports it beside LOKF's rather than re-describing it. What such a vocabulary lacks - who encoded a record, who confirmed it, when to look again - OKF v0.2 defines for documents only; whether it belongs on domain records is left to the domain's owners and the OKF specification. The README's summary line points at the new section.
- **`lokf-scaffolding` renamed `lokf-sidecar`**, matching what it produces: directory, frontmatter, install commands, this repository's own bundle, and every cross-reference. A bundle already laid down needs nothing - the files it wrote are identical.
- **Corrected Obsidian guidance for `knowledge_bundle`**: the link is opened *itself* as a vault, never the repository root (Obsidian skips a symlink resolving inside the vault it's indexing, and never indexes a dot-folder). Linking a repository's `.lokf/knowledge` *into* a personal vault - the reverse direction - is supported and now documented.
- **`README.md`** gains "Where the skills meet an Obsidian vault": the bundle's two names and which is real per host, a plugin-for-skill table, and the vault-as-**workshop**/bundle-as-**exhibition** framing. "The fifth role" no longer calls LOKF Curator a registrar: it is the curator's assistant, and the curator is always a person.
- **LOKF Enforcer is now LOKF Registrar** (repository `obsidian-lokf-registrar`), renamed for its role before its first release, wherever the README, the skills and this repository's bundle name it.

### Added

- **`lokf-sidecar` lays the bundle down by host.** Two names, one real folder: `.lokf/knowledge` (what the tools address) and `knowledge_bundle` (what people and Obsidian open). A code repository keeps the hidden folder real with `knowledge_bundle` as the doorway link; a notes vault or shared folder (Step 0 asks) makes `knowledge_bundle/` real and `.lokf/knowledge` the link - detected by both plugins with nothing to configure.
- **`just lokf-link`** recreates the visible layout's link where a sync service drops it, follows a new `visible` variable for a vault nested inside its repository (e.g. `../vault/knowledge_bundle`), and refuses a dangling link instead of failing on `ln`.
- **`scripts/test-sidecar-layouts.sh`**, run by the repository-contract check: builds throwaway hosts in both layouts and pins the wrapper's boundary check, the librarian workflow's change detection and packaging, the registrar's triggers, and `lokf-link`, all against both bundle names.
- **`lokf-librarian`** now leaves LOKF Registrar's Obsidian affordances alone by rule - the `<!-- lokf:related -->` block and the `diataxis.md` map - and addresses the bundle by both paths when scoping a diff or PR.
- **Semantic release**, version and changelog only: the version is computed from Conventional Commits on `main`, and `CHANGELOG.md`'s `## [Unreleased]` section is promoted into a dated heading. It never tags - `gh skill publish` remains the one tag creator - and `publish.yml` now refuses a typed version that disagrees with what was promoted. See [CONTRIBUTING.md](CONTRIBUTING.md#release-process).

### Fixed

- The librarian wrapper and both workflow templates name the bundle under **both** `.lokf/knowledge` and `knowledge_bundle`: a git pathspec never traverses a symlink, so the visible layout previously went undetected. `git add` is guarded against a pathspec matching nothing.
- Windows guidance now prefers a junction (`mklink /J`, no elevated rights, followed by Obsidian like a symlink) over the Developer-Mode `mklink /D` note.

## [0.14.0] - 2026-09-12

### Security

A `human:<id>` verification is a claim any writer can type, not a credential, and `lokf validate` passes a forged one since it is well-formed - so "confirmed by a person" was forgeable by anything able to steer `lokf-curator` or edit the bundle directly.

- `knowledge-registrar.yaml` gains a `provenance` job: every `human:` actor a PR newly adds under `.lokf/knowledge/` needs forge-held evidence - an APPROVED review from that account, or, when they authored the PR, a signature of theirs on the introducing commit, checked via GitHub's API (a runner has no keyring, so `git log %G?` can't do this locally). The load-bearing change; the rest is defence in depth.
- Solo maintainers take the signature branch (three `git config` lines, documented in `references/automation.md`); an optional `attestation` job gates on a GitHub Environment's required reviewers instead for a repository that can't sign - deliberately not a switch that disables the check, since an environment reviewer may be the PR's own author.
- `lokf-curator` resolves identity from `gh api user` only - the spoofable `git config user.name` fallback is gone - and Step 2 now refuses to run unattended (CI, a headless session, a subagent, a scheduled task); Step 1 stays read-only and safe anywhere.
- `lokf-sidecar` and `lokf-curator` now report whether commit signing is on before a solo maintainer spends twenty minutes on confirmations the gate will reject, and `lokf-curator` Step 1 reports a *Not tied to a signed commit* count on existing `human:` events - both report only, never touch `git config`.

### Fixed

- `lokf-curator` and `README.md` said LOKF has 14 built-in classes; the installed schema has 15 - `Role` was missing from every count and enumeration. Corrected in the class list, the vocabulary-fit label, and the "vocabulary stops fitting" paragraph.

### Added

- `lokf-sidecar` Step 2 now also creates a `knowledge_bundle` symlink to `.lokf/knowledge` at the repo root (POSIX hosts) - a visible entry point for humans and their tools, chiefly Obsidian's "Open folder as vault," which like most OS folder pickers hides dot-directories by default. Mirrors the Step 0 tracked/gitignored decision; `templates/gitignore` now excludes the `.obsidian/` folder Obsidian writes through the link into `.lokf/knowledge/` when used as a vault. This repository's own `.lokf/` now carries the symlink too, with matching excludes added to `.markdownlint-cli2.jsonc`, `lychee.toml`, and the `codespell` step so the aliased files aren't linted/checked twice.

## [0.13.0] - 2026-09-10

- The librarian SKILL now says: A spaced dash ("X - Y") used as punctuation must not be allowed to land at the start of a line after wrapping - Markdown reads a line beginning `-` followed by a space as a list item, so a paragraph never meant to be a list trips `MD032/blanks-around-lists` wherever the consuming repo lints `.lokf/**` (most do, via a `lint-and-docs`-style gate). Reword or rewrap so the dash stays mid-line; when unsure, prefer an unwrapped single line over one that risks the break landing there.
- `.markdownlint-cli2.jsonc` disables `MD060` (table column style): it flags the padded-header/bare-separator table style used everywhere in this repo (and on GitHub generally) as inconsistent, and no `style` setting reconciles the two without just relocating which row gets flagged. `.lokf/README.md`'s concept checklist gained a reminder not to let a spaced dash wrap onto its own line, since Markdown reads that as a list item (`MD032`).

## [0.12.0] - 2026-09-10

### Changed

- Renamed the `knowledge-validate.yaml` CI gate (and its scaffolding template counterpart) to `knowledge-registrar.yaml`, to name it for the registrar role it actually performs - keeping bundle records well-formed, never judging whether their content is true. Updated every cross-reference, including `README.md`'s own "fifth role" paragraph, which now names the gate directly. A repo that already scaffolded the old filename keeps working; re-scaffolding (or a manual rename) picks up the new name.

### Fixed

- Each `SKILL.md` (`lokf-curator`, `lokf-docent`, `lokf-librarian`, `lokf-sidecar`) now declares `license: Apache-2.0` in its frontmatter, matching this repository's `LICENSE`. Fixes the `recommended field missing: license` warning `gh skill publish` raised on all four skills during the `v0.11.0` release.

## [0.11.0] - 2026-09-10

### Security

- `knowledge-librarian` workflow now runs a fixed, reviewed in-repo script (`bash .lokf/scripts/knowledge-librarian.sh`) instead of an arbitrary command string from a repository variable, so changing *what executes* goes through code review rather than an unreviewed Settings edit.
- `knowledge-librarian` workflow split into two jobs: the agent (third-party code) runs in a `contents: read` job with no persisted git credentials and hands its proposed change to a separate privileged job - which runs no agent code - as a patch artifact. Only that job holds `contents: write` / `pull-requests: write`, so a compromised agent cannot reach a write-scoped credential. Top-level workflow permissions now default to none.
- `knowledge-librarian.sh` wrapper now parses `AGENT_CLI` into a quoted argv array (removing the unquoted expansion that word-split the value at the command position) and enforces the bundle boundary after the agent runs: it fails if the agent modified any path outside `.lokf/knowledge/` (`.lokf/feedback.md` allowed), so the "edit only the bundle" contract is enforced, not merely requested.

### Changed

- Arm the scheduled librarian run with the `KNOWLEDGE_LIBRARIAN_ENABLED` repository variable set to `true` (replaces `KNOWLEDGE_LIBRARIAN_CMD`); `AGENT_CLI` is unchanged. Updated the `lokf-sidecar` templates, the dogfooded workflow, the wrapper-script header, and the `lokf-sidecar`/`lokf-librarian` automation docs to match.

## [0.9.0] - 2026-09-09

Initial release: four [Agent Skills](https://agentskills.io/home) that turn a repository's scattered knowledge into a maintained, trusted [LOKF](https://lokf.nolan-nichols.com/) knowledge bundle - built once, kept current, and reviewed by a person, rather than rediscovered every session.

- `lokf-sidecar` - bootstraps a fresh `.lokf/` sidecar into a repository that has none: tooling, docs, and a dummy skeleton from bundled templates.
- `lokf-librarian` - scrapes the repository, derives concepts with their sources, wires typed relationships, audits the bundle against the LOKF schema, and hands off for review. Runs often, including on a schedule; deals in facts about the repository, never in verdicts about truth.
- `lokf-curator` - a human curator's assistant: a one-screen trust and freshness report, and an opt-in review session that records a person's confirm/correct/retire/send-back verdict directly in the bundle's frontmatter.
- `lokf-docent` - the reader's entry point. Answers questions from the bundle first, states each concept's trust label in plain words, verifies exact values at the source, and - when the bundle has no answer - explores the repository directly and records the gap in `.lokf/feedback.md` for the librarian to pick up. See [`EXAMPLES.md`](EXAMPLES.md) for real question-and-answer transcripts.

This repository dogfoods its own skills: `.lokf/` here is a real bundle built by `lokf-sidecar` and `lokf-librarian`, self-describing all four skills, this repository's own governance, and its CI.
