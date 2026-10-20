---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/ktl-sidecar-skill
title: ktl-sidecar skill
description: Procedure that creates a .lokf/ sidecar, tooling, docs, a dummy skeleton, and the knowledge_bundle doorway link beside it, from bundled templates, or repairs a missing or broken sidecar file, then hands off to ktl-librarian.
genre: how-to
resource: skills/ktl-sidecar/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-20T23:23:33Z"
hasPart:
  - https://w3id.org/ktl/knowledge/playbooks/open-bundle-in-obsidian
  - https://w3id.org/ktl/knowledge/playbooks/docent-in-m365-copilot
status: draft
about:
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
definedBy:
  - https://w3id.org/ktl/knowledge/references/agent-skills-specification
references:
  - https://w3id.org/ktl/knowledge/references/lokf-toolkit
  - https://w3id.org/ktl/knowledge/explanation/hosts-and-doorways
sources:
  - resource: skills/ktl-sidecar/SKILL.md
  - resource: skills/ktl-sidecar/references/automation.md
  - resource: skills/ktl-sidecar/references/gate.md
  - resource: skills/ktl-sidecar/references/portability.md
  - resource: skills/ktl-sidecar/references/prerequisites.md
  - resource: skills/ktl-sidecar/references/m365.md
  - resource: .github/workflows/knowledge-librarian.yaml
  - resource: skills/ktl-librarian/references/scheduled-task.md
  - resource: .lokf/scripts/knowledge-preflight.sh
  - resource: CHANGELOG.md
  - resource: https://github.com/noelmcloughlin/knowledge-trust-ladder/commit/61b9355f0dfa037ff8e165affa285344e451c209
  - resource: https://github.com/noelmcloughlin/knowledge-trust-ladder/commit/8fcdd867e45528a21f20f177fb63306afe8d278d
  - resource: skills/ktl-sidecar/templates
verified:
  - by: process:ktl-librarian
    at: "2026-10-19T18:47:10Z"
---
# Overview

ktl-sidecar runs **once** per repository, or to repair a missing or broken sidecar file. A repair rewrites only the missing or broken file, and never overwrites concept files. It never authors concepts. It has seven steps, 0 to 6:

- **Step 0.** Run the preflight from the host repository's root and gather the host project's facts. The preflight says what the machine can do, and the layout is the same on every host: `.lokf/knowledge` is the real folder (see [Hosts and doorways](../explanation/hosts-and-doorways.md)).
- **Step 1.** Copy each file from `templates/` and substitute placeholders as literal text with Python, not sed, since a value holding sed's delimiter or GNU sed's `e` command would change what the command does. Since 2026-09-17 the files include `.lokf/.gitattributes`, which keeps the bundle on LF.
- **Step 2.** Add three root-level pointers: `llms.txt`, a README aside, and a `knowledge_bundle` symlink onto `.lokf/knowledge` for people, folder pickers and Obsidian (see [Open the knowledge bundle in Obsidian](open-bundle-in-obsidian.md)).
- **Step 3.** Verify no placeholder survives.
- **Step 4.** Validate.
- **Step 5.** Optionally install the CI automation: the workflows, the scripts and, since 2026-09-24, the `m365/` folder. The step's lint advice names nine `scripts/*.sh` and six `.github/workflows/*.yaml`. Since 0.44.0 a domain host, whose bundle names other bundles, also gets `.lokf/domain.yaml`, `.lokf/scripts/knowledge-federate.py` and `.github/workflows/knowledge-federation.yaml`. Since 0.47.0, wherever the librarian workflow is, the step also installs `knowledge-sync.yaml`, `.lokf/scripts/knowledge-sync.sh` and a pull request template, which keep the copies and the skills pin at the newest release of the skills repository. Since 0.49.0 a host with knowledge outside its repository also gets `.lokf/ingest.yaml`, `.lokf/scripts/knowledge-ingest.sh` with its Python half, `knowledge-ingest.yaml` and a pull request template.
- **Step 6.** Hand off to ktl-librarian. All four skills should be installed, and ktl-website can publish the bundle as a site once it is worth showing.

Step 0 also settles two things. The bundle's base IRI, which every concept's id starts with, is never the code-host repository URL: that path space is not the project's, so the ids could never resolve. And Step 0 decides whether `.lokf/` is committed or gitignored. Committing it is the default the four skills assume. Gitignoring it is equally valid, for a personal bundle or under a policy against committing agent-authored content, and changes four things:

- every file is still created, since the bundle is filesystem-based either way;
- the commit in Step 4 is skipped, and so is Step 5 apart from the scripts and the `m365/` folder its table installs anyway;
- the `knowledge_bundle` symlink from Step 2 goes into the root `.gitignore` instead of being committed;
- the Step 6 hand-off says so.

The conventions script's Python half is among those scripts, since the `.sh` fails without it, and so is the apply script's `knowledge-apply.py`, the librarian's only pen. Three of the scripts and the `m365/` folder are installed even when the rest of Step 5 is skipped, since they need neither git nor GitHub:

- the preflight;
- since 2026-09-23, the feedback recorder;
- the report script `knowledge-report.sh`, which computes each trust label, the health line, the librarian's work list and whether any work waits. Since 2026-10-06 it also computes the curator's queue, with how many other concepts rely on each concept, and since 0.48.0 it counts the tracked files no concept names;
- the Microsoft 365 Copilot skills' builder with its instructions.

The forge-free provenance gate needs git and gpg or ssh-keygen. The skill's frontmatter declares what it needs in the Agent Skills `compatibility` field, as every skill here does.

ktl-docent runs its own copies of the feedback recorder and the report script, never the ones Step 5 installs (2026-10-05). The installed feedback recorder serves a person and an earlier ktl-docent, and ktl-curator and ktl-librarian quote the installed report script.

The skill keeps its detail in five reference files, so the router stays small:

- `references/portability.md` is a matrix, host by host: git or none, GitHub, GitLab, Codeberg, Forgejo or Gitea, Linux, macOS, Windows and PowerShell, synced folders, an Obsidian vault and, since 2026-09-24, a Microsoft 365 Copilot declarative agent. Since 2026-10-07 it also says what the skills repository tests before a release. A host whose copies are as the sidecar installed them need not test the templates again. A copy the host edited, a port to another forge or shell, and another operating system stay the host's.
- `references/m365.md`, added on 2026-09-24, says what Copilot allows a custom skill, what the Agents Toolkit checks, and which roles can run there. The docent and a future auditor run there as snapshot skills. The sidecar and librarian do not run there at all. The curator does not run there until it has a write action and an identity other than a forge login ([The docent in Microsoft 365 Copilot](docent-in-m365-copilot.md)).
- `references/automation.md` says what the librarian, wrapper, release and feedback files do and how to set them up, and since 0.44.0 the federation workflow and script of a domain host.
- `references/gate.md`, split out of `automation.md` on 2026-09-24, covers the registrar workflow and the forge-free gate.
- `references/prerequisites.md`, since 2026-09-17, gives each preflight line in plain words: what it means, what it stops, who fixes it and what to send them, for a person who cannot act on it themselves. The contract holds it to every line the preflight can print as missing or a warning. Since 0.49.0 it explains the `ingest` line too.

Every file the skill writes is copied from `templates/`, never retyped, which keeps a freshly installed bundle byte-identical to the reviewed template.

The forge-free gate verifies GPG keys with their subkeys and SSH keys alike against `.lokf/curators/<id>.asc` or `.pub`. It asks the person behind a confirmation that a change removes, as it asks the one behind a confirmation it adds. Its `--unattended` form refuses any change to a person's record in an unattended run.

The conventions script's thirteenth convention fails an edit to a confirmed concept that leaves `generated` older than the confirmation (2026-10-04). A move of the bundle's `base_iri` is no edit, since an id or relation target that moved with it still says the same (0.42.0). Its fourteenth, given a base commit with `--since`, fails a commit that records a person's confirmation and also changes the concept's claims, unless `generated.by` names that same person. The `validate` job passes the merge-base of the pull request's base and head, the commit the `provenance` job also uses (2026-10-07).

`gate.md` also carries what Step 5 points a curator at:

- the signing setup for one who opens their own pull request. That is the SSH key already used to push, registered on GitHub a second time as a *signing* key. GitHub blocks approving one's own pull request, and the `provenance` gate then needs a signature;
- the advice to mark `validate` and `provenance` as required checks;
- the caveat that the librarian's review pull request never triggers that gate.

GitHub does not start `pull_request` workflows for a pull request opened with the default `GITHUB_TOKEN`. So `publish` runs its own checks first, the unattended form of the forge-free gate among them. A required check stays at "Expected" there until a person triggers a new event.

`automation.md` says how to turn on the scheduled librarian. Its agent's credential goes in the `AGENT_API_KEY` secret or, for Copilot CLI, the job's own token with `AGENT_USE_JOB_TOKEN`. `AGENT_API_KEY_ENV` names the variable the agent reads it from. The page gives pinned `AGENT_CLI` commands for Copilot CLI and Claude Code, both run through `npx` on the Node 22 the workflow sets up. Each of these variables goes under Repository variables, never on an Environment, since a job's `if:` reads only repository and organization variables. The secrets go in the `knowledge-librarian` Environment, limited to the default branch. A table on that page lists every switch and secret.

The prompt follows `-p` unless the optional `AGENT_PROMPT_FLAG` names another flag, or `arg` for an agent that takes the prompt as its last argument, such as Codex CLI. The page states the five conditions any other agent must meet (0.40.0). The wrapper's prompt tells the agent to write `.lokf/patch.yaml` with its own file-writing tool, never with a shell redirect, a heredoc or a script, since an unattended run may deny a shell write. The Claude Code command confines the agent's file tool with `Edit(.lokf/patch.yaml)`. An `Edit` rule covers every file-writing tool, the Write tool included, and Claude Code ignores a `Write(<path>)` rule. The list does not confine the shell, so the wrapper sets `KNOWLEDGE_PEN_DRY_RUN_ONLY` for the agent, and the pen then only checks the patch file and leaves it for the wrapper to apply (0.53.0). `publish` opens its pull request with the job's own `GITHUB_TOKEN`, which GitHub refuses while the repository setting *Allow GitHub Actions to create and approve pull requests* is off. The page says to turn it on and keep the default token read-only, and gives the `gh api` command that does both.

With an optional variable, `KNOWLEDGE_RETRIEVAL`, each run that changes the bundle scores whether the index leads to the concept that answers each question readers asked. The pull request carries the score. A scheduled week with nothing waiting for the librarian runs no agent, since `knowledge-report.sh quiet` decides first. A scheduled run in a month's first seven days and a run a person starts always go ahead.

**Each secret in its Environment (0.53.0).** `automation.md` tells every host to keep each secret in the Environment of the workflow that reads it, limited to the default branch. `AGENT_API_KEY`, and `AGENT_CLI` when it is a secret, go in `knowledge-librarian`. `KNOWLEDGE_SYNC_TOKEN` goes in `knowledge-sync`, and every `KNOWLEDGE_INGEST_` secret in `knowledge-ingest`. A repository secret can be read by a workflow on any branch, and a workflow file runs on a push to the branch that carries it. The workflows still read a repository secret of the same name, so a host keeps working while it moves them, and the page says to delete the repository secret once it is moved. A private repository on GitHub Free has no Environments, so its secrets stay repository secrets there.

A first job, `earlier`, reads what became of the pull requests the workflow opened before. While one is still open, every scheduled run stops before the agent, in the first seven days too. On a scheduled run, the quiet check counts none of what a person declined by closing one without merging, and the librarian proposes none of it again until it changes. The librarian's hand-off, its own words for the reviewer, goes with the patch, and `publish` shows it under *From the librarian*, in a code block (2026-10-04).

The third workflow, `knowledge-release.yaml` (since 2026-09-24), needs no agent. It attaches the bundle to a GitHub release as `knowledge-<tag>-<repository>.zip` with a checksum. Since the `m365/` folder was added, it also attaches one Copilot skill zip per instructions file under `.lokf/m365/` beside it, built by `.lokf/m365/knowledge-m365.sh`. It skips a release whose bundle matches the last one released. When `.lokf/justfile` names a schema on its `schema :=` line, the release attaches that file too, as `schema-<tag>-<name>.yaml`. Since 0.55.0 the line may name any file in the repository, such as a linkml-sidecar schema, but never one outside it, and the released copy imports LOKF core as `lokf`. It runs when dispatched by hand or, once the `KNOWLEDGE_RELEASE_ENABLED` repository variable is `true`, on each published release.

**A domain host (0.44.0).** `references/automation.md` describes a domain host as one whose bundle names other bundles. Each `MemberBundle` concept names one released zip and its checksum, and a `MemberDomain` concept does the same when that bundle is a domain in turn. A person confirms that it belongs, and the workspace is the graph built from those releases, one named graph per bundle. Nothing in the host's three files runs a model:

- `knowledge-federate.py build --tag <tag>` resolves the members into a lock, fetches each zip over http or https from a public address, and checks it against the checksum its concept names. A local path needs `--allow-local`, and a private address needs a person's `private_addresses: allow` on the top `Domain` concept. For a GitHub release the build verifies the attestation, pinned to the member's `knowledge-release.yaml`, or to its `knowledge-federation.yaml` for a workspace, and without `gh` it stops unless run with `--no-attestation`. It refuses a zip holding a symbolic link, a path outside its root, a hidden file such as a `.git` folder or a file a browser runs, and a distribution name that is not one plain file name (0.53.0). A member that releases no zip names the `concepts.jsonld` its site serves instead, and the build checks that file against its checksum (0.53.0). It registers and exports each bundle with the toolkit, and loads one named graph per bundle. It gates every typed relation whose target lies in no member's namespace, or names no concept of the member whose namespace holds it, as the domain's `unowned_targets` says, and renames `snapshot.new/` to `snapshot/` in one step. A member whose `sensitivity` is above what the top `Domain` concept clears stops the build. So does a confidential member always, and an internal one when the repository is neither private nor internal (0.53.0). A member whose zip is itself a domain is followed, tier by tier, as deep as the top `Domain` concept's `max_depth` allows (3 unless set). A bundle two domains name at one release joins once, and named at two releases it stops the build (0.48.0). Since 0.50.1 the build takes each member as a person last confirmed it. A moved member no person has confirmed is built at the newest release the default branch held confirmed, while that confirmation stands, and a member no person confirmed is left out. The lock and the workspace index list both as waiting. A retired member or `Domain` concept is left out too, and the top `Domain` concept's `unowned_targets`, `max_depth` and `sensitivity` count only as a person confirmed them. `--verify-only` runs every step up to the gate in a temporary folder and writes nothing, and its gate judges the workspace the next release build would make.
- `knowledge-federation.yaml` runs the build on each release of the host and deploys the workspace under `/workspace/` of the host's site, once the `KNOWLEDGE_FEDERATION_ENABLED` repository variable is `true`. A domain host leaves `KNOWLEDGE_WEBSITE_ENABLED` unset, since this workflow is its one Pages deployer.
- `knowledge-federate.py members` is the domain's librarian, a script the librarian workflow runs as `AGENT_CLI`. It picks each member's newest release that carries a bundle zip, verifies it, and writes the change as operations for the pen. It verifies attestations with the job's read-only token, under `AGENT_USE_JOB_TOKEN` set to `true` and `AGENT_API_KEY_ENV` set to `KNOWLEDGE_FEDERATE_TOKEN`.
- `knowledge-federate.py mcp` is the `lokf-registry` MCP server over the snapshot, `serve` the toolkit's SPARQL endpoint and graph page, and `query` a one-off query (0.46.0). `diff <old> <new>` says what changed between two workspaces.

The librarian workflow template installs a pinned `ktl-librarian` into `.agents/skills/` on every run, since installed skills are gitignored runtime state a checkout does not carry. The step is skipped in the repository that publishes the skills (an `if` on the repository name, since 2026-09-24). There an install would shadow the source under bare `skills/`, because the wrapper looks under `.claude/skills/`, `.github/skills/` and `.agents/skills/` before bare `skills/`. The preflight's `copies` line compares that workflow with its template apart from `TRUST_LADDER_SKILLS_REF` and the commit beside it in `TRUST_LADDER_SKILLS_SHA`, a pin each host moves on its own schedule. The install step installs nothing unless the tag still names that commit. Since 0.47.0 the preflight compares the copies `templates/knowledge-sync.manifest` lists, and warns when the installed sidecar has no manifest.

**Keeping the sidecar current (0.47.0).** `knowledge-sync.yaml` runs weekly and on demand. When the skills pin is behind the newest release, its read-only `sync` job runs the host's own `knowledge-sync.sh`, which reads the release's `knowledge-sync.manifest` and writes the release's templates over the host's copies, moves the pin and writes the changelog entry. Its `publish` job runs the default branch's copy of the script with `--apply`. That refuses a patch that touches anything but the sidecar's copies, the site's copies, the pin and `CHANGELOG.md`, or that deletes, renames or links a file. It keeps every workflow as the default branch has it but for the pin, and holds the workflow changes the release brought for a person to read and apply. It then pushes the branch `knowledge-sync`, leased to the commit the `earlier` job read, and opens one pull request there, refreshed until it is merged, with the `KNOWLEDGE_SYNC_TOKEN` secret from the `knowledge-sync` Environment. Without the secret the run attaches its change and opens nothing. When the optional `KNOWLEDGE_SYNC_REVIEW_ENVIRONMENT` variable names an Environment with required reviewers, the `review` and `push-workflows` jobs push the held workflow changes once a reviewer approves (0.53.0).

**Knowledge outside the repository (0.49.0).** `.lokf/ingest.yaml` names each source outside the repository, `knowledge-ingest.sh` fetches it and writes it as Markdown under `.lokf/mirror/<entry id>/`, and `.lokf/ingest.lock.yaml` records what was fetched. `knowledge-ingest.yaml` runs weekly and on demand once `KNOWLEDGE_INGEST_ENABLED` is `true`. Its read-only `ingest` job hands the script only the secrets whose names start `KNOWLEDGE_INGEST_`, from the `knowledge-ingest` Environment, and its `publish` job opens one pull request on the branch `knowledge-ingest`, refreshed until it is merged. A scheduled run also prunes a mirror file whose source is gone or has left the selection, that no concept cites, and that an earlier run recorded so.

**Behind a package mirror, or with an old python3 (0.55.0).** A company package index, such as Nexus or Artifactory, often serves no upload times, and then `uv run` cannot resolve a script whose header names `exclude-newer`. So the pen, the conventions check and the ingest run with `.lokf/.venv` first, which `uv sync` installs from `uv.lock`, and through `uv run` after it (`references/portability.md`). No script picks a Python older than 3.9. When its runner cannot start, the conventions check says so and exits 2, rather than reporting findings against the bundle.

The preflight warns on its `python` line when python3 is older than 3.9, and on its `root` line when it screened the skill's own folder rather than the repository. It also lists KTL skills installed for one user, under `~/.copilot/skills/`, `~/.claude/skills/` or `~/.agents/skills/`. Those serve that user's live sessions, but the scheduled librarian runs on a fresh runner and needs a copy in the repository (`references/prerequisites.md`).

## Open questions

- 2026-10-13, human:noelmcloughlin: the wrapper does not search `.agents/skills/` first; `skills/ktl-sidecar/SKILL.md` gives the order `.claude/skills/`, `.github/skills/`, `.agents/skills/`, then bare `skills/`. "Added the same day" for `references/m365.md` reads as 2026-10-07, but git adds it on 2026-09-24. Also carry "Never overwrite concept files", that `<BASE_IRI>` is never the code-host repository URL, that tracked or gitignored changes four things, and that placeholders are substituted via Python, not sed.
- 2026-10-19, human:noelmcloughlin: refresh against sources.
