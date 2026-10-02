---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/docent-in-m365-copilot
title: "The docent in Microsoft 365 Copilot"
description: "How a person gets ktl-docent-m365, the docent packed with a snapshot of the bundle as a Microsoft 365 Copilot custom skill, from a release or by building it, adds it to a declarative agent, and keeps it current."
genre: how-to
resource: docs/m365.md
sources:
- resource: docs/m365.md
- resource: skills/ktl-sidecar/references/m365.md
- resource: skills/ktl-sidecar/templates/m365/ktl-docent-m365.md
- resource: skills/ktl-sidecar/templates/m365/knowledge-m365.sh
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
isPartOf:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-docent-skill
references:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/releasing
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-sidecar-skill
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/explanation/hosts-and-doorways
---

# Overview

`ktl-docent-m365` is the docent as a custom skill for a Microsoft 365 Copilot declarative agent. It is not a skill of its own; it puts `ktl-docent` into Copilot. Copilot runs skills with no repository, shell or network, so the skill carries a snapshot of the bundle, and the docent answers from it. Each answer names the snapshot and how far each concept has been trusted. The docent there cannot check a source or write `.lokf/feedback.md`, so it says so and gives the reader a gap report to file.

# Steps

1. **Get the zip.** Download `ktl-docent-m365-<tag>-<repository>.zip` from a release's assets. The release workflow attaches it beside the bundle zip on every release whose bundle changed. A release with no such asset means the bundle did not change since the last release that carries one, or the repository has not laid down `.lokf/m365/`. Or build it yourself: `.lokf/m365/knowledge-m365.sh --repo-url <url> --ref <tag> .lokf/knowledge ./dist` needs bash and `zip`, writes `dist/ktl-docent-m365/` with `SKILL.md`, `SNAPSHOT.md` and `knowledge/`, and exits 1 if the skill breaks one of Copilot's limits.
2. **Add it to an agent.** First check that the tenant has custom skills: they are in preview, for organizations in Microsoft's Frontier program, and not in tenants that use Information Barriers. With Agent Builder, nothing is installed: create or open an agent and add the zip as a skill. With the Agents Toolkit, install the CLI, create an agent, change into its folder, export both `TEAMSFX_AGENT_SKILLS=true` and `ATK_FRONTIER=true`, run `atk add skill --from <zip> -i false`, then `atk provision --env dev` and `atk preview --env dev` in the same shell. Skip `atk validate`, which rejects the `agent_skills` entry the toolkit itself wrote.
3. **Ask it something.** The answer names the snapshot, its version and build date, and each concept it rests on with a trust label. An answer with no snapshot in it did not come from the skill.

# Keep it current

The snapshot does not update itself. After each release that changes the bundle, take the new zip and add it again. A release that brings new instructions and the same bundle carries no new zip; run the workflow by hand with `force` for that tag.

# How it is put together

`.lokf/m365/` holds one instructions file per read-only role, named after the skill it becomes, and the builder packs each into its own zip. The docent's file is `ktl-docent-m365.md`, and its trust labels must match `ktl-docent`'s word for word, which the repository checks enforce. The curator cannot follow yet: it needs an action that lets the agent write, and a way to record who confirmed what without a forge login.
