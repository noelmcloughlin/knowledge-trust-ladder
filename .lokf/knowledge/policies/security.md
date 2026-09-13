---
type: Policy
id: https://lokf-agent-skills.example/knowledge/policies/security
title: Security policy
description: The actual attack surface (copied-into-other-repositories templates, this repo's own CI, the four skills' own prose read by an LLM agent), that a skill's `Scope:` line is advisory except on the scheduled workflow, how to report privately, this repository's hardening, the `human:` attribution gate, and its prompt-injection guards.
genre: reference
resource: SECURITY.md
generated:
  by: process:lokf-librarian
  at: "2026-09-13T23:00:00Z"
references:
  - https://lokf-agent-skills.example/knowledge/playbooks/repository-validation
verified:
- by: process:lokf-librarian
  at: "2026-09-13T23:00:00Z"
- by: human:noelmcloughlin
  at: "2026-09-10T00:00:00Z"
stale_after: 2027-03-10
---

# Overview

Three things execute: the wrapper script and workflow templates that get
copied into *other* repositories and run there, this repository's own
workflows, and the four skills' `SKILL.md`/`references/` prose - executed by
whichever LLM agent runs it. Vulnerabilities go through GitHub private
vulnerability reporting, not public issues.

A skill's `Scope:` line is prose, not an enforced boundary - the Agent
Skills format has no permission manifest, so an installed skill runs with
whatever tool access the calling agent session has (the same warning
`npx skills` prints after every install). Only the scheduled workflow
technically checks its scope (below); interactive sessions rely on a person
reviewing what the agent changed before committing or merging.

Hardening: third-party Actions pinned to reviewed commit SHAs everywhere
including the templates, `persist-credentials: false`, least-privilege
`permissions`, and harden-runner in audit mode on every workflow that
installs packages or runs third-party/agent code -
`validate.yml`, `publish.yml`, both jobs of `knowledge-librarian.yaml`
(`refresh` and `publish`), and `knowledge-registrar.yaml`'s job. A
maintainer-approved `release` environment gates `publish.yml`'s and
`semantic-release.yml`'s write-scoped jobs; `semantic-release.yml` installs
its pinned npm packages with `--ignore-scripts`, and `publish.yml` reads its
`workflow_dispatch` version input only through an `env:` var, never
interpolated directly into a shell command. `knowledge-librarian.yaml`'s
agent step always runs the pinned, reviewed wrapper script directly - the
`AGENT_CLI` repository variable (or, now, `secrets.AGENT_CLI` when the
command itself must stay out of the (public) Variables tab) can only choose
which agent runs, never what command runs. That workflow is split into two
jobs by least privilege: `refresh` runs the agent - third-party code - with
`contents: read` and no persisted git credentials (`uv sync --locked` pins
what gets installed), and hands its proposed bundle change to `publish` as a
patch artifact; only `publish`, which runs no agent code, holds
`contents: write` / `pull-requests: write`, so a compromised agent cannot
reach a write-scoped credential. Top-level workflow permissions default to
none. The template's agent step is gated on the consumer's
`KNOWLEDGE_LIBRARIAN_ENABLED` repository variable, so a freshly installed
copy stays inert until a maintainer arms it, and the workflow triggers only
on `schedule` and `workflow_dispatch`, never on an event an outside
contributor can fire. Dependabot covers this repository's own workflows
but cannot reach the templates - a documented upstream limitation, so those
pins are bumped by hand. Dependency review and CodeQL are deliberately
absent: there is no dependency manifest or compiled code here to scan.

`main` is protected, but not by a merge gate (recorded 2026-09-13):
deletions and force-pushes are blocked and linear history is required, but
a rule requiring pull requests, or requiring status checks to pass, is
deliberately *not* enabled - rulesets apply to direct pushes as well as to
merges, and the release workflow's own commit to `main` cannot be exempted
from them (a bypass list accepts roles, teams, GitHub Apps and Dependabot,
and `github-actions[bot]` is none of those). What gates a change is access
control - only the maintainer can write - plus CI run on every pull request
and read before merging. Secret scanning and push protection are on. All
of these are GitHub settings, not files in the tree, so nothing in CI can
assert they still hold.

One consequence the sidecar's `references/automation.md` states and this
policy leaves implicit: the template's `publish` job opens the librarian's
review pull request with the default `GITHUB_TOKEN`, and GitHub does not
start `pull_request`-triggered workflows for a pull request opened that way,
so `knowledge-registrar.yaml`'s `validate`/`provenance` jobs never run on
it; `publish`'s own checks (below) are that pull request's backstop, and a
consumer that has marked those checks required sees them sit at "Expected"
until a person fires a fresh `pull_request` event (close/reopen, or an empty
commit).

## `human:` attribution is a claim, not a credential

A `verified` event whose actor starts with `human:` is the bundle's central
trust signal, and just a string in a Markdown file - any writer that can
edit the bundle can type one, and it validates whether or not a person ever
looked. The realistic threat isn't an outside attacker but the ordinary
shape of agent work: another agent driving lokf-curator recording a
confirmation nobody gave. Four measures, most to least authoritative:
`knowledge-registrar.yaml`'s `provenance` job requires GitHub-held evidence
(an APPROVED review from the named account, or their signature on the
introducing commit) for every `human:` actor newly added on a pull request -
the one measure that runs outside the agent and so can't simply be
declined; lokf-curator writes `human:` only for an identity `gh api user`
authenticates, with no config-file or "just ask" fallback; lokf-curator
refuses to run a review session unattended (CI, headless, subagent,
scheduled, or non-live answers); and its report flags any `human:` event
whose introducing commit carries no signature, so an event that slipped in
some other way stays visible rather than silently trusted. A signature
proves a key holder committed and an approval proves an account clicked a
button - neither proves anyone read the source; the gate raises the cost of
forgery, it does not make a confirmation true. Where `.lokf/` is gitignored,
no pull request ever carries the bundle, so this whole CI half never runs -
the curator's in-session rules are then the only guard. An optional
`attestation` job (armed only when `KNOWLEDGE_CURATION_ENVIRONMENT` names an
environment) substitutes a fresh, logged environment-reviewer approval for
repositories that cannot sign; leaving that environment's required
reviewers empty makes it self-approve, turning the gate into a false
assurance, so the reviewers must be configured first. This whole section is
new to the policy since the security-hardening pass; the four-skill split
below was already current.

Prompt-injection guards, one per input path an agent reads but didn't author:
lokf-librarian resolves a `.lokf/feedback.md` entry only from the source it
names, never from the entry's own wording; lokf-curator quotes a fetched
`resource`/`sources` to the human rather than ever acting on it itself;
lokf-docent treats fetched source or repository content as text to quote,
never as instructions, is read-only on the bundle besides, and now also
never carries a secret, credential, token, or connection string into an
answer or a feedback entry - it names the file and line and the kind of
value, never the value itself, since the scheduled workflow commits
`feedback.md` into a public pull request. If any guard fails, the one
unattended write path (`knowledge-librarian.yaml`) contains the damage, and
enforcement of its path boundary now lives in the privileged `publish` job,
not the agent's own `refresh` job: before applying `refresh`'s patch,
`publish` re-derives the allowed-paths check itself from the patch's own
`git apply --numstat` output (on a clean checkout the agent never shared)
and refuses anything outside `.lokf/knowledge`, `knowledge_bundle`, and
`.lokf/feedback.md`, and separately refuses a patch that adds a `by:
human:` claim, since this skill never writes one. The wrapper script's own
version of the same check, run inside `refresh` right after the agent call,
is a fail-fast convenience rather than the backstop - a sufficiently
capable `AGENT_CLI` sharing that job's workspace could in principle blind
it by setting `core.fsmonitor`/`core.hooksPath` before the check re-reads
`git status`, so the wrapper now snapshots both `.git/config` and
`.git/hooks/` before the agent call and restores them unconditionally
afterward, and its checks live inside a `main()` invoked only from the
script's last line so an agent that truncates the running script mid-way
cannot skip them by ending the file early. `publish`'s own checks cannot be
reached either way. Commits, when they happen, still touch only those same
paths (`git add -A --` scoped to the three pathspecs, never unscoped), never
push to the default branch, and always end at a human-reviewed PR. Ordinary
repository content the librarian scrapes has no equivalent per-entry guard -
it relies on the same review-before-merge every other change to `main` goes
through, a materially higher trust level than unreviewed reader feedback.
