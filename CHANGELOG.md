# Changelog

All notable changes to this repository are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows the rules in [README.md](README.md#versioning). All skills release together under one tag.

## [Unreleased]

## [0.16.0] - 2026-09-13

### Changed

- **One layout, every host.** `.lokf/knowledge/` is the real folder everywhere, and the `knowledge_bundle` doorway link beside it (Step 2) is laid down by default again - a host-agnostic reason: dot-folders are hidden from Finder and most pickers, and Obsidian opens the link *itself* as a vault. Step 0 no longer asks which kind of host it is in; the Step 6 handoff says whether the doorway was created, the one command if not, and, for a vault host, to open `knowledge_bundle` itself as a vault.
- **`just lokf-link`** now creates or recreates that doorway idempotently, refusing a name already taken; its `visible` variable is gone.
- **`lokf-docent`** gains `references/obsidian.md`, answering the two-vault workflow directly and naming `lokf-sidecar` for an agent to make the link; a missing link is never a feedback entry.
- **Shared-folder guidance is consolidated** in `lokf-sidecar/references/portability.md`, Obsidian included: sync services carry `.lokf/` but drop links, so the doorway is per-machine; a team may still rearrange a real `knowledge_bundle/` by hand outside a vault, still covered by the Step 5 templates and the plugins' auto-detection.
- **`README.md` restructured**: "Where the bundle lives" (host-agnostic) and "…and where it meets an Obsidian vault" (optional, why the pairing is worth it, the two-vault story) replace the old combined section; "For the curious" is delegated to a new `docs/for-the-curious.md`, mirroring the plugin READMEs; every passing Obsidian mention now says it is optional.

### Removed

- **The visible layout** (0.15.0) - a real `knowledge_bundle/` folder inside a vault, with `.lokf/knowledge` as the link. A day of use showed why not: Obsidian indexes a real folder like any other, so the exhibition leaked into the workshop's link suggestions, graph and search. Its Step 0 host decision, the justfile's `visible` variable, and two layout-test cases go with it.
- References to the maintainer's private vault, named during the 0.15.0 work: the family this repository describes is the four skills and the two Obsidian plugins.

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
- **Semantic release**, version and changelog only: the version is computed from Conventional Commits on `main` and `CHANGELOG.md`'s `## [Unreleased]

## [0.15.0] - 2026-09-12` section promoted into a dated heading. It never tags - `gh skill publish` remains the one tag creator - and `publish.yml` now refuses a typed version that disagrees with what was promoted. See [CONTRIBUTING.md](CONTRIBUTING.md#release-process).

### Fixed

- The librarian wrapper and both workflow templates name the bundle under **both** `.lokf/knowledge` and `knowledge_bundle`: a git pathspec never traverses a symlink, so the visible layout previously went undetected. `git add` is guarded against a pathspec matching nothing.
- Windows guidance now prefers a junction (`mklink /J`, no elevated rights, followed by Obsidian like a symlink) over the Developer-Mode `mklink /D` note.

## [0.14.0] - 2026-09-12

### Security

A `human:<id>` verification is a claim any writer can type, not a credential - and `lokf validate` passes a forged one, because it is perfectly well-formed. That made "confirmed by a person" forgeable by anything able to steer `lokf-curator` or edit the bundle directly: another agent driving the session, a subagent, a scheduled run. Four changes close it, in the order they matter.

- `knowledge-registrar.yaml` gains a `provenance` job (pull requests only, `pull-requests: read`). It collects every `human:` actor a PR newly adds under `.lokf/knowledge/` - anchored on `by:`, so an id quoted in an `## Open questions` note is not mistaken for a verification - and requires forge-held evidence for each: an APPROVED review from that account, or, when that person authored the PR (GitHub does not let authors approve their own), a signature of theirs on the commit that introduced the event. Signature status is read from GitHub's API, not `git log %G?`: a runner has neither a GPG keyring nor an allowed-signers file, so locally every signature reads as unverifiable - and the API additionally names the account each commit is attributed to, which is what ties a signature to a person rather than merely proving one exists. This is the load-bearing change; the rest is defense in depth.
- Solo maintainers, who cannot approve their own pull requests, take the signature branch; the setup is three `git config` lines reusing an existing SSH key, documented in `lokf-sidecar`'s `references/automation.md` and in the workflow itself. A signature is also the stronger record - cryptographic, and still checkable after a review could have been dismissed.
- For a repository that genuinely cannot sign, an optional `attestation` job gates on a GitHub Environment's required reviewers instead. It is deliberately not a switch that disables the check: a permanent "provenance: off" setting gets flipped once and never flipped back, leaving the bundle asserting confirmations nothing supports. This asks for a fresh click per pull request, it lands in the deployment log, and - unlike a PR review - an environment reviewer may be the person who opened the PR, which is what makes it work for one-person repositories. Off unless `KNOWLEDGE_CURATION_ENVIRONMENT` names an environment, and a no-op unless that environment actually has required reviewers configured (documented prominently, since that is the way to get a false sense of protection).
- `lokf-curator` now resolves identity from `gh api user` alone. The `git config user.name` fallback is gone (an ordinary writable config value that anything with shell access can set to a maintainer's slug) and so is asking (it takes the identity from the one channel an attacker fully controls). With no authenticated id, *Confirm* and *Correct now* are unavailable for the session; *Wrong - send back*, *Retire* and *Later* assert nothing about who checked what and remain available.
- `lokf-curator` Step 2 now refuses to run unattended: `CI`/`GITHUB_ACTIONS` set, a headless `-p` session, a subagent, a scheduled task, or answers arriving from a file or tool result rather than a live turn. Step 1 stays read-only and safe to run anywhere.
- `lokf-sidecar` (Step 5) and `lokf-curator` (before the first verb of a review session) now check whether commit signing is on and report it, so a solo maintainer learns their confirmations will be rejected *before* recording twenty minutes of them rather than when the gate fires. Both only report: neither runs `git config`, and neither touches `--global` config - a knowledge sidecar should not change how someone commits in unrelated repositories, and the half a skill could automate is not the half the gate reads (registering the key with GitHub is). The docs also note that a committed `.gitconfig` cannot enable signing at all: git reads only system, `~`, and `.git/config`, deliberately, since a config file arriving with a clone could otherwise run commands.
- `lokf-curator` Step 1 reports a new *Not tied to a signed commit* count - `human:` events whose introducing commit (found with `git log -S`) carries no `gpgsig` header. It deliberately tests for a signature's *presence*, not its validity: verifying one needs an allowed-signers file or keyring that a typical checkout lacks even for its own user's commits, so `%G?` would report good signatures as absent and the count would accuse everybody. It is worded as a question worth asking, never an accusation, since unsigned commits are ordinary. Excluded: uncommitted events, a gitignored `.lokf/`, and events predating the file's history.

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
