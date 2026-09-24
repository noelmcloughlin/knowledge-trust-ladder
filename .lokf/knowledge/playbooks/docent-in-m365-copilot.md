---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/docent-in-m365-copilot
title: The docent in Microsoft 365 Copilot
description: How a person gets ktl-docent-m365, the docent packed with a snapshot of the bundle as a Microsoft 365 Copilot custom skill, from a release or by building it with `.lokf/m365/knowledge-m365.sh`, adds it to a declarative agent, checks the first answer, and keeps it current; what to do when a step fails, and why only the read-only roles go there.
genre: how-to
resource: docs/m365.md
sources:
- resource: docs/m365.md
- resource: skills/ktl-sidecar/references/m365.md
- resource: skills/ktl-sidecar/templates/m365/ktl-docent-m365.md
- resource: skills/ktl-sidecar/templates/m365/knowledge-m365.sh
generated:
  by: process:ktl-librarian
  at: "2026-09-24T22:42:01Z"
status: draft
isPartOf:
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-sidecar-skill
references:
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-docent-skill
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-librarian-skill
- https://knowledge-trust-ladder.example/knowledge/playbooks/releasing
- https://knowledge-trust-ladder.example/knowledge/glossary/trust-label
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/explanation/three-lines-of-defence
- https://knowledge-trust-ladder.example/knowledge/explanation/domain-schemas
---

# Overview

**ktl-docent-m365** is the docent as a custom skill for a Microsoft 365 Copilot declarative agent. It is not a fifth skill: it puts [ktl-docent](ktl-docent-skill.md) into Copilot. Copilot runs a skill with no repository, shell or network, so the skill carries a **snapshot** of the bundle and answers from it. Every answer names the snapshot (repository, revision, build date) and the trust label of each concept it used, in the same words ktl-docent uses. It cannot check a value at its source or write `.lokf/feedback.md`, so it says so and hands the reader a ready-to-paste Miss or Disagreement line to file in the repository instead.

Getting it running takes three steps, in this order: get the zip, add it to an agent, and ask it something to check the answer names the snapshot. The short route installs nothing.

# 1. Get the zip

**From a release.** Each release whose bundle changed carries `ktl-docent-m365-<tag>-<repository>.zip` among its assets, beside the bundle zip. `knowledge-release.yaml` builds it at the bundle's commit time, so the zip is reproducible. A release with no such asset means one of two things. Either the bundle did not change since the last release that carries one, and the reader takes the zip from that earlier release, or the repository has not laid down `.lokf/m365/`, and its releases carry the bundle zip alone.

**Or build it.** A repository on another forge, or on none, runs the builder the release workflow runs, on its bundle folder. It needs bash and `zip`:

```bash
.lokf/m365/knowledge-m365.sh --repo-url https://github.com/me/my-repo --ref v1.2.0 .lokf/knowledge ./dist
```

It writes `dist/ktl-docent-m365/` (with `SKILL.md`, `SNAPSHOT.md` and `knowledge/`) and `dist/ktl-docent-m365.zip`. In a git clone only tracked files are copied, and hidden files such as `.obsidian/` are left out. With `SOURCE_DATE_EPOCH` set, one input gives one zip. The build writes nothing and exits 1 if a skill breaks one of Copilot's limits: `SKILL.md` over 20,000 characters, folders more than 3 deep, file types Copilot does not accept, more than 350 files, more than 10 MB, or symbolic links.

# 2. Add it to an agent

Two routes take the same zip, and the page recommends **Agent Builder** unless the reader already develops agents with the toolkit. With Agent Builder, nothing is installed: create or open an agent in Microsoft 365 Copilot and add the zip as a skill. With the **Agents Toolkit CLI** (`atk`, for developers, on Node.js), log in, scaffold or reuse a declarative agent, and run `ATK_FRONTIER=true atk add skill --from <zip> -i false` (the command is hidden without that variable), then `atk validate`, `atk provision` and `atk preview`. Either way, custom skills are in preview: the tenant must be in the Frontier program, and an agent cannot yet have both skills and embedded files.

# 3. Ask it something

Ask the agent a question the bundle answers, such as what a service does or who owns it. The answer names the snapshot, its version and build date, and each concept it rests on with a [trust label](../glossary/trust-label.md). An answer with no snapshot in it did not come from the skill. When the docent cannot answer, or two concepts disagree, it ends with one line to paste into the repository's `.lokf/feedback.md`, and `SNAPSHOT.md` says where to send it; the docent never records the gap itself. Filed in the repository, the line reaches [ktl-librarian](ktl-librarian-skill.md), which turns it into a concept or a question for the curator.

# Keep it current

The snapshot does not update itself. After each release that changes the bundle, take the new zip and add it again. The workflow packs the skill only when the bundle changed, so a release with new instructions and the same bundle carries no new zip. For that tag, run the workflow by hand with `force`.

# If something goes wrong

- **The release has no `ktl-docent-m365-…` asset.** The bundle did not change since the last release that carries one, or the repository has not laid down `.lokf/m365/`.
- **The build exits 1.** The skill breaks one of Copilot's limits, the output names which, and nothing is written.
- **The build says `zip not found`.** The folder is built but not zipped: install `zip`, or zip the folder by hand before adding it.
- **`atk add skill` is not a command.** Set `ATK_FRONTIER=true`. The command also works only inside a project the toolkit scaffolded.
- **Agent Builder or the toolkit refuses the skill.** The tenant is not in the Frontier program, or the agent already has embedded files. Both are preview limits, not faults in the zip.

# Which roles go to Copilot

`.lokf/m365/` holds one instructions file per read-only role, named after the skill it becomes (`ktl-docent-m365.md`, deliberately not `SKILL.md`, so no installer lists it), and the builder packs each file into its own zip. The auditor, the third line, is planned as `ktl-auditor-m365.md` beside it, with no change to the builder, workflow or checks. The sidecar and librarian need a repository and a shell, so they have no Copilot form. The curator has none yet: it needs a write action the agent can call and an identity that is not a forge login, and the shape of that identity record is held in reserve (see [domain-schemas](../explanation/domain-schemas.md)).

A host's copy under `.lokf/m365/` is what its releases pack, so a host that edits it changes what its readers' Copilot follows. Repository check 17 holds every instructions file's trust-label table word for word to ktl-docent's.
