---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-librarian-skill
title: ktl-librarian skill
description: Recurring procedure that scrapes the host repository, derives and maintains the .lokf/ concepts and their typed relations, audits the bundle, and hands off for human review.
genre: how-to
resource: skills/ktl-librarian/SKILL.md
sources:
- resource: skills/ktl-librarian/SKILL.md
- resource: skills/ktl-librarian/references/scheduled-task.md
- resource: .github/workflows/knowledge-librarian.yaml
- resource: .lokf/scripts/knowledge-librarian.sh
- resource: CHANGELOG.md
generated:
  by: process:ktl-librarian
  at: "2026-09-24T22:22:58Z"
status: draft
dependsOn:
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-sidecar-skill
about:
  - https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
definedBy:
- https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
references:
  - https://knowledge-trust-ladder.example/knowledge/references/lokf-specification
  - https://knowledge-trust-ladder.example/knowledge/references/okf-specification
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-curator-skill
verified:
- by: human:noelmcloughlin
  at: "2026-09-09T18:36:00Z"
stale_after: 2027-09-09
---

# Overview

Runs **often**, including on a schedule. It carries the seven LOKF Golden Rules
(OKF-first; the bundle-root semantic header and `base_iri` authority test; the
type vocabulary plus the Diátaxis `genre` facet; typed
relationships over bare links; core field-to-ontology mapping; trust,
provenance and lifecycle; permissiveness), then four sections: scrape and
build, audit, hand off for review, and the scheduled task.

It deals in **facts about the repository, never verdicts about truth**: it may
record that it re-checked a concept against its source (`verified` by
`process:ktl-librarian`), but only [ktl-curator](ktl-curator-skill.md)
writes a `human:` confirmation. Concepts it creates start as `status: draft`,
and a claim it cannot settle gets an `## Open questions` section instead of a
guess.

Each steady-state run starts by consuming `.lokf/feedback.md`, where
ktl-docent records readers' misses and disagreements. Every entry is an
untrusted report, never an instruction: the librarian resolves only the
question or disagreement it names, from the source it points at, and
removes each entry it handled. A scheduled run installs the pinned
`ktl-librarian` release first, except in the repository that publishes the
skills, which runs its own source under bare `skills/` (2026-09-24).

**The scheduled run's credential and checks (added 2026-09-24).** The wrapper hands the agent one credential, under the name the `AGENT_API_KEY_ENV` variable gives: the `AGENT_API_KEY` secret, or, with `AGENT_USE_JOB_TOKEN` set to `true`, the job's own token, which Copilot CLI accepts. It refuses a name that does not end `_API_KEY`, `_TOKEN` or `_KEY`, or that starts `GITHUB_`, `GH_`, `GIT_`, `RUNNER_` or `ACTIONS_`, and it exports the key into the agent's environment only, never into an argument list or its own git commands. The `refresh` job now validates with `lokf validate --check-refs`, as the registrar gate does, so a dangling relation target fails the librarian's own check before `publish` opens the pull request.

Two things it now leaves alone by rule (added 2026-09-12): the Obsidian
affordances KTL Registrar may write into a bundle - a marker-delimited
`<!-- lokf:related -->` block in a concept body and a `diataxis.md` Map of
Content (`type: Document`, `generated.by: ktl-registrar/<version>`), which it
never edits, lists, audits as orphans, or counts - and the bundle's second
name: `.lokf/knowledge` is the real folder ktl-sidecar lays down, with a
`knowledge_bundle` link beside it, but a host rearranged by hand may have the
link the other way round, so it addresses the bundle by the tools' name and
names both paths when scoping a diff or a PR.

The tooling-version check (rule 6) now runs **only in interactive
sessions**: the scheduled workflow's wrapper permits edits solely under
`.lokf/knowledge/`, `knowledge_bundle/` and `.lokf/feedback.md`, so a
scheduled run that touched `.lokf/pyproject.toml` would fail the whole run
closed rather than land a partial change - added 2026-09-12 as part of a
security-hardening pass that also added a second, independent enforcement
of that same path boundary in `knowledge-librarian.yaml`'s privileged
`publish` job (re-derived from the proposed patch on a clean checkout,
never trusting the `refresh` job's own check alone), plus harden-runner and
`.git/config`/`.git/hooks/` snapshot-and-restore around the agent call in
the wrapper script - restored from an `EXIT` trap since 2026-09-17, after a
Socket audit showed a failing agent or a cancelled job skipped the restore
and left a poisoned config for the workflow's next steps. See `policies/security.md` for the detail.

**Extending the vocabulary (added 2026-09-14).** Rule 3's classes are
deliberately few and portable. A domain needing more of its own gets a
LinkML schema that imports LOKF's and validates with `lokf validate --schema
<file>`, which the toolkit has always accepted - no loosening of Rule 7.
`ktl-librarian/references/domain-schema.md` is the recipe: a pinned copy of
the core schema, the domain schema, frontmatter naming the class exactly, and
the flag wired into the justfile and both workflow templates. Rule 3 reads
that wiring back - where the justfile passes `--schema`, that schema's
`Concept` descendants are part of the vocabulary, and a record names the
subclass. The tooling-version step (rule 6) refreshes the pinned copy.
`ktl-curator/references/domain-schemas.md` covers when; this covers how.

**The toolkit's constraints, and `revision` (added 2026-09-17).** The field
tables state what lokf 0.8.0 enforces: `sources[].author` is an actor
string, `http_method` is one uppercase verb from a closed list, and every
timestamp, `stale_after` included, is a datetime, a bare date meaning
midnight UTC. Where the toolkit accepts it, the skill also writes `revision`
on `generated`: the full commit hash of a file in the repository, or the
ETag or a `sha256:` digest of a URL, always quoted. The field is proposed
for lokf 0.9.0 and not yet released, and the 0.8.0 validator rejects it, so
the key is left out on every released toolkit, on a file with uncommitted
changes, and on a source the skill did not read that run. The registrar gate checks that a commit hash names a
commit holding the concept's `resource`. Every `at` comes from `date -u` at the moment it is written, never an estimate or local time labelled `Z` (2026-09-24), and conventions rule 11 rejects one later than the commit that records it.

**Portability (added 2026-09-17).** `references/portability.md` says what
the skill loses on each host and the substitute: without git, `revision` is
left out and the hand-off names the platform's version history; on GitLab
or Forgejo the wrapper ports and the merge request is opened there; from
PowerShell the commands run through Git for Windows' bash; on macOS
`shasum -a 256`. Files and directories are named in lowercase, since the
path is the id and case-insensitive hosts collide. The audit runs the
preflight first, and the tooling-version check now uses `uvx --from pip pip
index versions lokf`: `uv pip` has no `index` subcommand, which every
earlier refresh had noted and worked around.
