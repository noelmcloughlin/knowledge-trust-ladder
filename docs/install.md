# Install

Four skills, each one standing alone. The **sidecar** plus the **librarian** is
enough to see the idea: the bundle gets built, everything in it marked a draft.
Add the **curator** once there is a bundle worth trusting. Already have a
healthy `.lokf/`? Skip the **sidecar**. The **docent** goes anywhere an agent
only *reads* a bundle, this repository included.

> Formerly `lokf-agent-skills`. GitHub redirects the old links, clones and
> `npx skills add` paths, so an existing install keeps working. The skills
> themselves took the `ktl-` prefix in 0.22.0; [CHANGELOG.md](../CHANGELOG.md)
> lists their old names, which a host installed before then removes.

## Install with the GitHub CLI

[`gh skill`](https://cli.github.com/manual/gh_skill_install), GitHub CLI v2.90.0+:

```bash
gh skill install noelmcloughlin/knowledge-trust-ladder ktl-sidecar
gh skill install noelmcloughlin/knowledge-trust-ladder ktl-librarian
gh skill install noelmcloughlin/knowledge-trust-ladder ktl-curator
gh skill install noelmcloughlin/knowledge-trust-ladder ktl-docent
```

## Install with the Open Skills CLI

[`npx skills`](https://github.com/vercel-labs/skills):

```bash
npx skills add noelmcloughlin/knowledge-trust-ladder \
  --skill ktl-sidecar \
  --skill ktl-librarian \
  --skill ktl-curator \
  --skill ktl-docent --yes
```

## Pin to one tag

All four skills release together under one tag, so pin them to the same one.
Append it to the skill name (`ktl-docent@v0.16.0`) or pass `--pin v0.16.0`.
What each version level means: [releasing.md](releasing.md).

## Microsoft 365 Copilot

Copilot runs custom skills in a sandbox with no repository, so only the
**docent** goes there, and it takes a snapshot of the bundle with it.
[m365.md](m365.md) says where to get it and
how to add it to a declarative agent.

## What each skill needs

Every skill runs from a POSIX shell and starts with a preflight that prints
what this machine can do and which steps that disables.

| Skill | Needs |
| --- | --- |
| `ktl-sidecar`, `ktl-librarian` | [`uv`](https://docs.astral.sh/uv/), for the `lokf` toolkit |
| `ktl-curator` | this machine signed in to the forge (`gh` or `glab`) to record a confirmation in your name, and signed commits when you open your own curation pull requests ([signing-commits.md](signing-commits.md)) |
| `ktl-docent` | nothing |

Someone who cannot act on a line the preflight prints, such as a **curator**
who knows the subject but not the repository, gets a request note for whoever
set the repository up. The note comes from the **sidecar**'s
[prerequisites page](../skills/ktl-sidecar/references/prerequisites.md).
