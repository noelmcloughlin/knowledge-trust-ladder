---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-sidecar-skill
title: ktl-sidecar skill
description: Procedure that creates a .lokf/ sidecar - tooling, docs, a dummy skeleton, and the knowledge_bundle doorway link beside it - from bundled templates, or repairs a single missing sidecar file, then hands off to ktl-librarian.
genre: how-to
resource: skills/ktl-sidecar/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-09-24T16:46:12Z"
hasPart:
- https://knowledge-trust-ladder.example/knowledge/playbooks/open-bundle-in-obsidian
status: draft
about:
  - https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
definedBy:
- https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
references:
  - https://knowledge-trust-ladder.example/knowledge/references/lokf-toolkit
  - https://knowledge-trust-ladder.example/knowledge/explanation/hosts-and-doorways
---

# Overview

Runs **once** per repository, or to repair a single missing sidecar file;
it never authors concepts. Seven steps, 0 to 6: run the preflight and gather the host project's facts (Step 0;
the preflight says what the machine can do, and the layout is the same on
every host - `.lokf/knowledge` is the real folder, see
[Hosts and doorways](../explanation/hosts-and-doorways.md)), copy each file
from `templates/` and substitute placeholders (Step 1, since 2026-09-17
including `.lokf/.gitattributes`, which keeps the bundle on LF), add three
root-level pointers - `llms.txt`, a README aside, and a `knowledge_bundle`
symlink onto `.lokf/knowledge` for people, folder pickers and Obsidian
(Step 2, see [Open the knowledge bundle in Obsidian](open-bundle-in-obsidian.md)) - verify
no placeholder survives (Step 3), validate (Step 4), optionally lay down the
CI automation (Step 5: three workflows and six scripts, the conventions
script's Python half among them, since the `.sh` fails without it; two
of the scripts land even when the rest of Step 5 is skipped, since they need
neither git nor GitHub: the preflight and, since 2026-09-23, the feedback
recorder; the forge-free provenance gate needs git and gpg or ssh-keygen),
and hand off (Step 6). Its frontmatter declares what it
needs in the Agent Skills `compatibility` field, as every skill here does.

Its detail lives in four reference files, so the router itself stays small. `references/portability.md` is a matrix, host by host: git or none, GitHub, GitLab or Forgejo, Linux, macOS, Windows and PowerShell, synced folders, and an Obsidian vault. `references/automation.md` says what the librarian, wrapper, release and feedback files do and how to wire them. `references/gate.md`, split out of `automation.md` on 2026-09-24, covers the registrar workflow and the forge-free gate, which verifies GPG keys with their subkeys and SSH keys alike against `.lokf/curators/<id>.asc` or `.pub`. `references/prerequisites.md`, since 2026-09-17, gives each preflight line in plain words: what it means, what it stops, who fixes it and what to send them, for a person who cannot act on it themselves; the contract holds it to every line the preflight can print as missing or a warning. Every file the skill writes is copied from `templates/`, never retyped, which is what keeps a freshly laid-down bundle byte-identical to the reviewed template.

`gate.md` also carries what Step 5 points a curator at: the signing setup for one who opens their own pull request (the SSH key already used to push, registered on GitHub a second time as a *signing* key, because GitHub blocks approving one's own pull request and the `provenance` gate then needs a signature), the advice to mark `validate` and `provenance` as required checks, and the wrinkle that the librarian's own review pull request never fires that gate. GitHub does not start `pull_request` workflows for a pull request opened with the default `GITHUB_TOKEN`, so `publish` runs its own two checks first, and a required check sits at "Expected" there until a person fires a fresh event.

`automation.md` says how to arm the scheduled librarian. Its agent's credential goes in the `AGENT_API_KEY` secret, or, for Copilot CLI, the job's own token with `AGENT_USE_JOB_TOKEN`, and `AGENT_API_KEY_ENV` names the variable the agent reads it from; the page gives pinned `AGENT_CLI` commands for Copilot CLI and Claude Code, both run through `npx` on the Node 22 the workflow sets up. The third workflow, `knowledge-release.yaml` (since 2026-09-24), needs no agent: it attaches the bundle to a GitHub release as `knowledge-<tag>-<repository>.zip` with a checksum, skips a release whose bundle matches the last one released, and runs when dispatched by hand or, once `KNOWLEDGE_RELEASE_ENABLED` is `true`, on each published release.

The librarian workflow template installs a pinned `ktl-librarian` into
`.agents/skills/` on every scheduled run, since installed skills are
gitignored runtime state a checkout does not carry. The step is skipped in
the repository that publishes the skills (an `if` on the repository name,
since 2026-09-24), where an install would shadow the source under bare
`skills/` because the wrapper searches `.agents/skills/` first. The
preflight's `copies` line compares that workflow with its template apart
from `TRUST_LADDER_SKILLS_REF`, a pin each host moves on its own schedule.
