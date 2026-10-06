---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-sidecar-skill
title: ktl-sidecar skill
description: Procedure that creates a .lokf/ sidecar, tooling, docs, a dummy skeleton, and the knowledge_bundle doorway link beside it, from bundled templates, or repairs a missing or broken sidecar file, then hands off to ktl-librarian.
genre: how-to
resource: skills/ktl-sidecar/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-06T09:49:14Z"
hasPart:
- https://knowledge-trust-ladder.example/knowledge/playbooks/open-bundle-in-obsidian
- https://knowledge-trust-ladder.example/knowledge/playbooks/docent-in-m365-copilot
status: draft
about:
- https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
definedBy:
- https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
references:
- https://knowledge-trust-ladder.example/knowledge/references/lokf-toolkit
- https://knowledge-trust-ladder.example/knowledge/explanation/hosts-and-doorways
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
verified:
- by: process:ktl-librarian
  at: "2026-10-06T11:10:52Z"
---
# Overview

ktl-sidecar runs **once** per repository, or to repair a missing or broken sidecar file. It never authors concepts. It has seven steps, 0 to 6:

- **Step 0.** Run the preflight and gather the host project's facts. The preflight says what the machine can do, and the layout is the same on every host: `.lokf/knowledge` is the real folder (see [Hosts and doorways](../explanation/hosts-and-doorways.md)).
- **Step 1.** Copy each file from `templates/` and substitute placeholders. Since 2026-09-17 that includes `.lokf/.gitattributes`, which keeps the bundle on LF.
- **Step 2.** Add three root-level pointers: `llms.txt`, a README aside, and a `knowledge_bundle` symlink onto `.lokf/knowledge` for people, folder pickers and Obsidian (see [Open the knowledge bundle in Obsidian](open-bundle-in-obsidian.md)).
- **Step 3.** Verify no placeholder survives.
- **Step 4.** Validate.
- **Step 5.** Optionally install the CI automation: three workflows, nine scripts and, since 2026-09-24, the `m365/` folder, fourteen files in all.
- **Step 6.** Hand off.

The conventions script's Python half is among those scripts, since the `.sh` fails without it, and so is the apply script's `knowledge-apply.py`, the librarian's only pen. Three of the scripts and the `m365/` folder are installed even when the rest of Step 5 is skipped, since they need neither git nor GitHub:

- the preflight;
- since 2026-09-23, the feedback recorder;
- the report script `knowledge-report.sh`, which computes each trust label, the health line, the librarian's work list and whether any work waits;
- the Microsoft 365 Copilot skills' builder with its instructions.

The forge-free provenance gate needs git and gpg or ssh-keygen. The skill's frontmatter declares what it needs in the Agent Skills `compatibility` field, as every skill here does. ktl-docent runs its own copies of the feedback recorder and the report script, never the ones Step 5 installs (2026-10-05). The installed feedback recorder serves a person and an earlier ktl-docent, and ktl-curator and ktl-librarian quote the installed report script.

The skill keeps its detail in five reference files, so the router itself stays small:

- `references/portability.md` is a matrix, host by host: git or none, GitHub, GitLab or Forgejo, Linux, macOS, Windows and PowerShell, synced folders, an Obsidian vault and, since 2026-09-24, a Microsoft 365 Copilot declarative agent.
- `references/m365.md`, added the same day, says what Copilot allows a custom skill, what the Agents Toolkit checks, and which roles can run there. The docent and a future auditor run there as snapshot skills. The sidecar and librarian do not run there at all, and the curator not until it has a write action and an identity other than a forge login ([The docent in Microsoft 365 Copilot](docent-in-m365-copilot.md)).
- `references/automation.md` says what the librarian, wrapper, release and feedback files do and how to set them up.
- `references/gate.md`, split out of `automation.md` on 2026-09-24, covers the registrar workflow and the forge-free gate. That gate verifies GPG keys with their subkeys and SSH keys alike against `.lokf/curators/<id>.asc` or `.pub`. The gate asks the person behind a confirmation that a change removes, as it asks the one behind a confirmation it adds, and its `--unattended` form refuses any change to a person's record in an unattended run. Its thirteenth convention fails an edit to a confirmed concept that leaves `generated` older than the confirmation (2026-10-04).
- `references/prerequisites.md`, since 2026-09-17, gives each preflight line in plain words: what it means, what it stops, who fixes it and what to send them, for a person who cannot act on it themselves. The contract holds it to every line the preflight can print as missing or a warning.

Every file the skill writes is copied from `templates/`, never retyped, which is what keeps a freshly installed bundle byte-identical to the reviewed template.

`gate.md` also carries what Step 5 points a curator at:

- the signing setup for one who opens their own pull request. That is the SSH key already used to push, registered on GitHub a second time as a *signing* key, because GitHub blocks approving one's own pull request and the `provenance` gate then needs a signature;
- the advice to mark `validate` and `provenance` as required checks;
- the caveat that the librarian's review pull request never fires that gate.

GitHub does not start `pull_request` workflows for a pull request opened with the default `GITHUB_TOKEN`, so `publish` runs its own checks first, the unattended form of the forge-free gate among them. A required check stays at "Expected" there until a person fires a fresh event.

`automation.md` says how to turn on the scheduled librarian. Its agent's credential goes in the `AGENT_API_KEY` secret or, for Copilot CLI, the job's own token with `AGENT_USE_JOB_TOKEN`. `AGENT_API_KEY_ENV` names the variable the agent reads it from. The page gives pinned `AGENT_CLI` commands for Copilot CLI and Claude Code, both run through `npx` on the Node 22 the workflow sets up.

With an optional variable, `KNOWLEDGE_RETRIEVAL`, each run that changes the bundle scores whether the index leads to the concept that answers each question readers asked, and the pull request carries the score. A scheduled week with nothing waiting for the librarian runs no agent, since `knowledge-report.sh quiet` decides first. A scheduled run in a month's first seven days and a run a person starts always go ahead.

A first job, `earlier`, reads what became of the pull requests the workflow opened before. While one is still open, every scheduled run stops before the agent, in the first seven days too. On a scheduled run, the quiet check counts none of what a person declined by closing one without merging, and the librarian proposes none of it again until it changes. The librarian's hand-off, its own words for the reviewer, goes with the patch, and `publish` shows it under *From the librarian*, in a code block (2026-10-04).

The third workflow, `knowledge-release.yaml` (since 2026-09-24), needs no agent. It attaches the bundle to a GitHub release as `knowledge-<tag>-<repository>.zip` with a checksum. Since the `m365/` folder was added, it also attaches one Copilot skill zip per instructions file under `.lokf/m365/` beside it, built by `.lokf/m365/knowledge-m365.sh`. It skips a release whose bundle matches the last one released. It runs when dispatched by hand or, once `KNOWLEDGE_RELEASE_ENABLED` is `true`, on each published release.

The librarian workflow template installs a pinned `ktl-librarian` into `.agents/skills/` on every scheduled run, since installed skills are gitignored runtime state a checkout does not carry. The step is skipped in the repository that publishes the skills (an `if` on the repository name, since 2026-09-24), where an install would shadow the source under bare `skills/` because the wrapper searches `.agents/skills/` first. The preflight's `copies` line compares that workflow with its template apart from `TRUST_LADDER_SKILLS_REF` and the commit beside it in `TRUST_LADDER_SKILLS_SHA`, a pin each host moves on its own schedule. The install step installs nothing unless the tag still names that commit.
