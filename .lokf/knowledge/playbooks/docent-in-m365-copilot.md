---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/docent-in-m365-copilot
title: The docent in Microsoft 365 Copilot
description: How a person gets ktl-docent-m365, the docent packed with a snapshot of the bundle as a Microsoft 365 Copilot custom skill, from a release or by building it with `.lokf/m365/knowledge-m365.sh`, adds it to a declarative agent, and keeps it current; why only the read-only roles go there.
genre: how-to
resource: docs/m365.md
sources:
- resource: docs/m365.md
- resource: skills/ktl-sidecar/references/m365.md
- resource: skills/ktl-sidecar/templates/m365/ktl-docent-m365.md
- resource: skills/ktl-sidecar/templates/m365/knowledge-m365.sh
generated:
  by: process:ktl-librarian
  at: "2026-09-24T22:22:58Z"
status: draft
isPartOf:
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-sidecar-skill
references:
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-docent-skill
- https://knowledge-trust-ladder.example/knowledge/playbooks/releasing
- https://knowledge-trust-ladder.example/knowledge/glossary/trust-label
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/explanation/three-lines-of-defence
- https://knowledge-trust-ladder.example/knowledge/explanation/domain-schemas
---

# Overview

**ktl-docent-m365** is the docent as a custom skill for a Microsoft 365 Copilot declarative agent. It is not a fifth skill: it puts [ktl-docent](ktl-docent-skill.md) into Copilot. Copilot runs a skill with no repository, shell or network, so the skill carries a **snapshot** of the bundle and answers from it. Every answer names the snapshot (repository, revision, build date) and the trust label of each concept it used, in the same words ktl-docent uses. It cannot check a value at its source or write `.lokf/feedback.md`, so it says so and hands the reader a ready-to-paste Miss or Disagreement line to file in the repository instead.

# Get the skill

**From a release.** Each release whose bundle changed carries `ktl-docent-m365-<tag>-<repository>.zip` among its assets, beside the bundle zip. `knowledge-release.yaml` builds it at the bundle's commit time, so the zip is reproducible, and a repository that has not laid down `.lokf/m365/` attaches the bundle zip alone.

**Or build it.** A repository on another forge, or on none, runs the builder the release workflow runs, on its bundle folder:

```bash
.lokf/m365/knowledge-m365.sh --repo-url https://github.com/me/my-repo --ref v1.2.0 .lokf/knowledge ./dist
```

It writes `dist/ktl-docent-m365/` (with `SKILL.md`, `SNAPSHOT.md` and `knowledge/`) and `dist/ktl-docent-m365.zip`. In a git clone only tracked files are copied, and hidden files such as `.obsidian/` are left out. With `SOURCE_DATE_EPOCH` set, one input gives one zip. The build writes nothing and exits 1 if a skill breaks one of Copilot's limits: `SKILL.md` over 20,000 characters, folders more than 3 deep, file types Copilot does not accept, more than 350 files, more than 10 MB, or symbolic links.

# Add it to an agent

With **Agent Builder**, nothing is installed: create or open an agent in Microsoft 365 Copilot and add the zip as a skill. With the **Agents Toolkit CLI** (`atk`, for developers, on Node.js), log in, scaffold or reuse a declarative agent, and run `ATK_FRONTIER=true atk add skill --from <zip> -i false` (the command is hidden without that variable), then `atk validate`, `atk provision` and `atk preview`. Custom skills are in preview: the tenant must be in the Frontier program, and an agent cannot yet have both skills and embedded files.

# Keep it current

The snapshot does not update itself. After each release that changes the bundle, take the new zip and add it again. The workflow packs the skill only when the bundle changed, so a release with new instructions and the same bundle carries no new zip. For that tag, run the workflow by hand with `force`.

# Which roles go to Copilot

`.lokf/m365/` holds one instructions file per read-only role, named after the skill it becomes (`ktl-docent-m365.md`, deliberately not `SKILL.md`, so no installer lists it), and the builder packs each file into its own zip. The auditor, the third line, is planned as `ktl-auditor-m365.md` beside it, with no change to the builder, workflow or checks. The sidecar and librarian need a repository and a shell, so they have no Copilot form. The curator has none yet: it needs a write action the agent can call and an identity that is not a forge login, and the shape of that identity record is held in reserve (see [domain-schemas](../explanation/domain-schemas.md)).

A host's copy under `.lokf/m365/` is what its releases pack, so a host that edits it changes what its readers' Copilot follows. Repository check 17 holds every instructions file's trust-label table word for word to ktl-docent's.
