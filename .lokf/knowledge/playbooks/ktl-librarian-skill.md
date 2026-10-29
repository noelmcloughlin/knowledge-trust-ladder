---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/ktl-librarian-skill
title: ktl-librarian skill
description: Recurring procedure that scrapes the host repository, derives and maintains the .lokf/ concepts and their typed relations, audits the bundle, and hands off for human review.
genre: how-to
resource: skills/ktl-librarian/SKILL.md
sources:
  - resource: skills/ktl-librarian/SKILL.md
    id: ktl-librarian-skill.md
  - resource: skills/ktl-librarian/references/golden-rules.md
  - resource: skills/ktl-librarian/references/bootstrap.md
  - resource: skills/ktl-librarian/references/audit.md
  - resource: skills/ktl-librarian/references/scheduled-task.md
  - resource: skills/ktl-librarian/references/patch.md
  - resource: skills/ktl-librarian/references/ingest.md
    id: references-ingest.md
  - resource: skills/ktl-librarian/references/domain-schema.md
  - resource: skills/ktl-librarian/references/agent-skills.md
  - resource: skills/ktl-librarian/references/retellings.md
  - resource: skills/ktl-librarian/references/portability.md
  - resource: skills/ktl-sidecar/references/automation.md
  - resource: .github/workflows/knowledge-librarian.yaml
  - resource: .lokf/scripts/knowledge-librarian.sh
  - resource: .lokf/scripts/knowledge-apply.sh
  - resource: .lokf/scripts/knowledge-report.sh
  - resource: .lokf/scripts/knowledge-conventions.sh
  - resource: CHANGELOG.md
    id: changelog.md
  - resource: .lokf/justfile
generated:
  by: process:ktl-librarian
  at: "2026-10-29T01:31:51Z"
dependsOn:
  - https://w3id.org/ktl/knowledge/playbooks/ktl-sidecar-skill
about:
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
definedBy:
  - https://w3id.org/ktl/knowledge/references/agent-skills-specification
references:
  - https://w3id.org/ktl/knowledge/references/lokf-specification
  - https://w3id.org/ktl/knowledge/references/okf-specification
  - https://w3id.org/ktl/knowledge/playbooks/ktl-curator-skill
  - https://w3id.org/ktl/knowledge/policies/security
verified:
  - by: human:noelmcloughlin
    at: "2026-09-09T18:36:00Z"
  - by: human:noelmcloughlin
    at: "2026-09-26T20:00:42Z"
  - by: human:noelmcloughlin
    at: "2026-10-03T09:40:04Z"
  - by: process:ktl-librarian
    at: "2026-10-18T17:45:03Z"
  - by: human:noelmcloughlin
    at: "2026-10-13T00:19:38Z"
stale_after: 2027-10-13
status: draft
relatedTo:
  - https://w3id.org/ktl/knowledge/playbooks/ktl-prose-skill
---

# Overview

The librarian runs **often**, including on a schedule. It carries the seven LOKF Golden Rules in brief: OKF first; the bundle-root semantic header and the `base_iri` authority test; the type vocabulary plus the Diátaxis `genre` facet; typed relationships over bare links; the core field-to-ontology mapping; trust, provenance and lifecycle; and permissiveness. Their tables are in `references/golden-rules.md`. Four sections follow: scrape and build, audit, hand off for review, and the scheduled task. `references/bootstrap.md` holds the first run's sweep, and `references/audit.md` the audit's detail.

It deals in **facts about the repository, never verdicts about truth**. It may record that it re-checked a concept against its source (`verified` by `process:ktl-librarian`), but only [ktl-curator](ktl-curator-skill.md) writes a `human:` confirmation. Concepts it creates start as `status: draft`, and a claim it cannot settle gets an `## Open questions` section instead of a guess.

Each concept the librarian derives names where it came from, as a `resource` or a `sources` entry, and conventions rule 15 fails a concept that names neither (0.58.0)[^changelog.md]. Wherever a claim rests on a number, a name or a qualifier, the librarian gives the source's entry an `id` and cites it with a footnote, and conventions rule 16 checks the join[^ktl-librarian-skill.md]. `references/golden-rules.md` says how to choose the id and write the footnote.

## A steady-state run

Each steady-state run starts from the work list that `knowledge-report.sh worklist` computes. It names the concepts whose sources moved since they were derived or last checked, ordered by git history and never by clock, the notes a person left, and how much reader feedback waits. A local source that has not moved is not read again. The list also names two kinds of item the run leaves alone: a source where the librarian's own question has waited for a person since, and an item under *Declined*, from a pull request a person closed without merging.

Then the run reads the verdicts on its previous work: the `**Curation**` lines in `log.md` and every open question a person left. It reads each as a report, never as an instruction, and re-derives a sent-back concept from the source the note names, never the same way again. Every note the run reads leaves the librarian's stamp on its concept, a `patch`, `rewrite` or `recheck`, so the quiet check knows the note was read. A note older than a person's later confirmation is the curator's to clear. The run withdraws a question of its own with the `resolve` operation once the source settles it.

Then it consumes `.lokf/feedback.md`, where ktl-docent records readers' misses and disagreements, at most ten entries in a run, oldest first. Every entry is an untrusted report: the librarian resolves only the question or disagreement it names, from the source it points at. It names each entry it handled in the operation's `from_feedback`, with the reader's question in `asked`. The pen moves the entry out of `feedback.md` and into `.lokf/questions.md`, a ledger that only grows and that only programs read. A reader's words go nowhere else: not into a concept, not into `log.md`, and not into the hand-off. A miss on a question an existing concept already answers is a description defect, so the skill fixes that `description` and adds no twin. On a host of Agent Skills, `references/agent-skills.md` says when a person must hear of it too.

When a count or a name changes in one source, the run searches the bundle for the old value and changes a concept only where its own source now states the new one. It sweeps for orphans with `knowledge-report.sh coverage`, which counts, per folder, the tracked files under no path a concept names in `resource` or `sources`. A file only a concept's `exclusions` account for (lokf 0.9.0 and later) is counted apart, as left out on purpose, and conventions rule 18 fails an exclusion with a blank reason or a material listed both ways. The map of knowledge sources, `playbooks/knowledge-sources.md`, is itself a concept, and it holds no account of a run (0.53.0).

## The pen

The skill never edits a file under `knowledge/` by hand. It describes each change as an operation in `.lokf/patch.yaml`, and `knowledge-apply.sh`, the sidecar's script called the pen, checks every operation and writes the files. The pen stamps `generated` from the clock, keeps a `description` equal to its two index bullets, and files each log line under the day's heading. It refuses an operation that would name a person as its actor, rewrite text a person wrote, or delete a concept a person confirmed or left a note on. It also refuses a patch that would add, change or remove a `human:` event or a person's note, however its operations spell it, and one that handles more than ten feedback entries. Since 0.55.0 it also runs `lokf validate` on every concept it would write, with `--dry-run` too, when `.lokf/.venv` holds the toolkit, and says `schema not checked` when it cannot run that check. `references/patch.md` gives the eight operations, and `knowledge-apply.sh --format` prints the same block, so the scheduled wrapper's prompt names no file of the skill.

A patch may carry one `log` line for every operation that gives none, and the pen writes that line once (0.45.1). It may also carry `handoff`, up to ten lines for the reviewer in the agent's own words. The pen holds each to one line of printable text and writes none of it to the bundle, and the scheduled pull request shows them under *From the librarian*, in a code block (0.32.0). `reindex` re-derives a concept's two index bullets without touching the concept, and `resolve` withdraws an open question the librarian itself asked.

## The scheduled run

A scheduled run installs the pinned `ktl-librarian` release first, except in the repository that publishes the skills, which runs its own source under bare `skills/`. The install step installs nothing unless the release tag still names the commit pinned beside it. It stops the run before any agent runs when git does not ignore `.agents/`, where it installs the skill (0.53.0).

The wrapper hands the agent one credential, under the name the `AGENT_API_KEY_ENV` variable gives. That credential is the `AGENT_API_KEY` secret, or, with `AGENT_USE_JOB_TOKEN` set to `true`, the job's own token. The job token serves Copilot CLI, billed to the repository owner's seat, or a domain host's members script, which reads it as `KNOWLEDGE_FEDERATE_TOKEN`. The wrapper refuses a name that does not end `_API_KEY`, `_TOKEN` or `_KEY`, or that starts `GITHUB_`, `GH_`, `GIT_`, `RUNNER_` or `ACTIONS_`. It exports the key into the agent's environment only, never into an argument list or its own git commands. The `AGENT_API_KEY` secret, and `AGENT_CLI` when it is a secret, go in the `knowledge-librarian` Environment, limited to the default branch, so a workflow on any other branch cannot read them (0.53.0). The workflow still reads a repository secret of the same name, so a host keeps working while it moves the secret.

The prompt follows `-p`, or the flag the `AGENT_PROMPT_FLAG` variable names, or comes last when that variable is `arg` (0.40.0). The prompt tells the agent to create and edit `.lokf/patch.yaml` with its own file-writing tool, never with a shell redirect, a heredoc or a script, since an unattended run may deny a shell write (0.40.0). The sidecar's `automation.md` says the same for every agent, and its documented Claude Code command scopes the agent's file tool to the patch file with `Edit(.lokf/patch.yaml)`.

In the agent's step the wrapper sets `KNOWLEDGE_PEN_DRY_RUN_ONLY`, so the pen there only checks the patch file and leaves it for the wrapper. A run of the pen without `--dry-run` in that step exits 2 and writes nothing (0.53.0). The wrapper applies the file after the agent has finished. It refuses a run that changed anything else, and one whose result touches a person's record, which `knowledge-provenance.sh --unattended` reads off the tree.

The `refresh` job validates with `just lokf-check-refs`, which runs `lokf validate --check-refs --check-excerpts`, as the registrar gate does, through the `just` that `.lokf/uv.lock` pins where the sidecar's `pyproject.toml` names `rust-just`, else the same version fetched by name (0.56.1). It runs `knowledge-conventions.sh` the same way. Both steps continue on error, so a dangling relation target or a convention finding is reported in the pull request body rather than stopping the pull request. The `publish` job opens that pull request with the job's own token, which GitHub refuses while the repository setting *Allow GitHub Actions to create and approve pull requests* is off.

A scheduled week with nothing waiting runs no agent. `knowledge-report.sh quiet` finds no moved source, no note a person left since the librarian's last stamp, no concept without a stamp and no reader feedback. A moved source does not count once an open question of the librarian's that names it was committed no earlier than the source's last change. A scheduled run in a month's first seven days, and a run a person starts, always go ahead (0.32.0). The one exception is a scheduled run while a pull request the workflow opened is still open: it stops before the agent. On a scheduled run, the quiet check counts none of what a person declined by closing one of those pull requests without merging, and the librarian proposes none of it again until it changes.

## Guards around the agent

**Reading feedback, the Snyk W011 finding (acknowledged).** The librarian is the one skill that reads what a reader wrote, because consuming an entry is what `.lokf/feedback.md` is for. So the scanner's finding is acknowledged rather than designed away. An unattended run has no write credential in `refresh`. `publish`, which runs no agent, re-derives the touched paths from the patch on a clean checkout. It refuses a patch touching any path outside `.lokf/knowledge`, `knowledge_bundle`, `.lokf/feedback.md` and `.lokf/questions.md`, and one that touches a person's record in any YAML layout, so an entry can neither add a confirmation nor remove one. What comes out is a pull request a person merges. On the way in, `knowledge-feedback.sh` holds each entry to one line and one of two kinds.

**The no-Python schema, the Snyk W012 finding (addressed).** An audit without Python reads LOKF's schema from GitHub, at a URL that names the commit tagged `v0.9.0`, never a tag or `main`, so the file it serves cannot change. That file is byte-identical to the schema inside the `lokf` 0.9.0 wheel, which `uv sync --locked` checks against `.lokf/uv.lock` wherever Python is present. A check in this repository fails a tag or a branch in the URL. The skill reads the schema as data to compare against, never as instructions.

Each job of the workflow hardens its runner with harden-runner. The wrapper snapshots `.git/config` and `.git/hooks/` before the agent call and puts them back afterwards, from an `EXIT` trap for every other way out, so a failing agent or a cancelled job leaves no rewritten config in the checkout for the workflow's next steps. `policies/security.md` has the detail.

## What it leaves alone

The librarian leaves the Obsidian affordances that KTL Registrar may write into a bundle alone. These are a marker-delimited `<!-- lokf:related -->` block in a concept body and a `diataxis.md` map at the bundle root. It never edits, moves or deletes them, and it treats `diataxis.md` like `index.md` and `log.md`: reserved, and never a concept. The pen carries the block over on a `rewrite`.

The tooling-version check, step 7 of a refresh, runs **only in interactive sessions**. It compares the latest `lokf` on PyPI, from `uvx --from pip pip index versions lokf`, with the floor in `.lokf/pyproject.toml`, since `uv pip` has no `index` subcommand. Unattended, the wrapper lets the agent write only `.lokf/patch.yaml`, so a scheduled run skips the step.

## Reference pages

**Extending the vocabulary.** Rule 3's classes are few and portable. A domain needing more of its own gets a LinkML schema that imports LOKF's and validates with `lokf validate --schema <file>`. `references/domain-schema.md` is the recipe: a pinned copy of the core schema, the domain schema, frontmatter naming the class exactly, and one `schema` variable in the sidecar's justfile. The `lokf-validate`, `lokf-check-refs`, `lokf-convert` and `lokf-serve` recipes pass that variable as `--schema`, and the registrar, librarian and release workflows run those recipes, so nothing else in the sidecar changes. Rule 3 reads that variable back: where it names a file, every `Concept` descendant in that file or its imports is part of the vocabulary, and a record names the subclass. The tooling-version step refreshes the pinned copy. The variable takes any path relative to `.lokf/`: a linkml-sidecar under `.linkml/`, a schema project at the repository's root, or a schema anywhere else, and in the last two a `.lokf/` beside the schema is a bundle about the repository until its maintainers add the import and the variable. A published vocabulary the domain schema needs does not go into `imports:` as it is, since LinkML merges every imported name into one namespace; `lokf adapt`, released in lokf 0.9.0, writes a copy that sits beside `lokf.yaml` (0.55.1). `ktl-curator/references/domain-schemas.md` covers when; this covers how.

**A host of Agent Skills.** `references/agent-skills.md` is for a repository whose content is Agent Skills. The librarian derives one `Playbook` concept, with `genre: how-to`, for each skill the host authors, and leaves out installed and vendored skills. A skill template gets no concept of its own. The procedure stays in `SKILL.md`, and the concept holds what the skill is for, what it needs and how it relates to the host's other skills. A skill the repository deprecates stays a fact in the concept, apart from the curator's `status: deprecated`. A miss that a skill's own `description` should have prevented goes to the reviewer in a hand-off line, since only a person changes that description.

**Retellings for younger readers.** `references/retellings.md` says how the librarian writes and refreshes a retelling: a concept that tells younger readers what another concept says, in shorter words. A retelling may leave a fact out, and it never adds one. Its `derivedFrom` names the adult concept, a `sources` entry gives that concept's path, and its `tags` carry the band, such as `audience-13-18`. A refresh re-derives it from the adult concept as it now stands. In a live session the librarian writes one when a person asks. A scheduled run writes one only for a band the curation policy's `Younger readers:` line declares, and only from a concept a person has confirmed. No run writes one because a reader's feedback entry asks for it.

**The toolkit's constraints, and `revision`.** The field tables state what lokf enforces from 0.8.0: `sources[].author` is an actor string, `http_method` is one uppercase verb from a closed list, and every timestamp, `stale_after` included, is a datetime, a bare date meaning midnight UTC. Where the toolkit accepts it, the skill also passes `revision`: the full commit hash of a file in the repository, or the ETag or a `sha256:` digest of a URL, always quoted. The field arrived in lokf 0.9.0, and the 0.8.0 validator rejects it. So the key is left out on an older toolkit, on a file with uncommitted changes or not under version control, and on a source the skill did not read that run. Conventions rule 6 checks that a commit-shaped `revision` names a commit holding the concept's `resource`, and rule 11 rejects an `at` later than the commit that first recorded it.

**Portability.** `references/portability.md` says what the skill loses on each host and the substitute. On GitLab, Codeberg, Forgejo or Gitea the wrapper is scheduled in that CI and the merge request is opened there. From PowerShell the commands run through Git for Windows' bash, and on macOS `shasum -a 256` stands in for `sha256sum`. Files and directories are named in lowercase, since the path is the id and case-insensitive hosts collide. The audit runs the preflight first.

**Plain English and the prose pass.** The librarian writes each body, description and log line in plain English, under rules ktl-prose carries in full. In a live session, where ktl-prose is installed and the run created or rewrote concepts, the hand-off first names them and offers a plain-prose pass, which runs only when the person says yes. A scheduled run skips the offer. The pull request description ends with a section for the curator that quotes the health line, names the confirmed concepts the change touches, the new drafts and the new open questions, and says whether to run ktl-curator after the merge or on the branch, committing the verdicts separately, so that confirmations never stack on a pull request that has not merged (0.55.1).

**Sources outside the repository (0.49.0).** On a host with `.lokf/ingest.yaml`, `knowledge-ingest.sh` fetches the sources that manifest names and keeps a copy of each under `.lokf/mirror/<entry id>/`, one Markdown file per page or document (`references/ingest.md`). In a live session the librarian runs `bash .lokf/scripts/knowledge-ingest.sh` before the work list, with the credentials the manifest names in the environment. Unattended, it does not run it: the ingest workflow runs on Sundays and opens one pull request with the mirror's changes, a person merges it, and the work list then names each concept whose mirror file moved. The wrapper refuses a run that changed anything but the patch file, so a mirror written in the scheduled run would fail it. A concept derived from a mirrored page names the mirror file as its `resource` and the origin as a `sources` entry. A `Reference` concept, where one is wanted, is the other way round: the origin is its `resource`, and the mirror path is under `sources`. For an entry with `reference: true`, `knowledge-ingest.sh --patch` writes those concepts as operations for the pen. The librarian reads a mirror file as a source, never as instructions, and derives nothing from a file the lock does not mark `ok`. The source map gives one row per manifest entry, never per item. The lock, `.lokf/ingest.lock.yaml`, records a status for each item. A confidential entry's items are recorded in `.lokf/.cache/ingest.lock.yaml` instead, beside its copies, unless the entry sets `lock_details: true`[^references-ingest.md]. When the lock marks an item `gone` or `unlisted`, the librarian re-verifies each concept that cites it. It deletes such a concept when nothing else carries its claim, or adds a `question` that names the mirror path and says the source is gone when a person confirmed it. Once no concept cites the file, the ingest's next scheduled run removes it with `--prune`. The librarian may also run `--prune` in a live session after it has handled the concepts, and never unattended. It never clears the mirror before a run.

[^changelog.md]: CHANGELOG.md, 0.58.0, Added
[^ktl-librarian-skill.md]: skills/ktl-librarian/SKILL.md, Writing a concept
[^references-ingest.md]: skills/ktl-librarian/references/ingest.md, When a source goes away
