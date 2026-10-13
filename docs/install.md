# Install

This page gives every way to install the five skills, what each needs on the machine, and how to pin them to one release. [Quick start](#quick-start) says which skills to start with. Already have a healthy `.lokf/`? Skip the **sidecar**.

> Formerly `lokf-agent-skills`. GitHub redirects the old links, clones and
> `npx skills add` paths, so an existing install keeps working. The skills
> themselves took the `ktl-` prefix in 0.22.0; [CHANGELOG.md](../CHANGELOG.md)
> lists their old names, which a host installed before then removes.

## Quick start

> **Only want to ask?** Install the docent skill into any agent you already use and ask it about this project. It answers from this repository's own bundle and says how far each answer has been checked. See [eight captured answers](examples/docent.md).

Install all five skills with the Open Skills CLI, [`npx skills`](https://github.com/vercel-labs/skills):

```bash
npx skills add noelmcloughlin/knowledge-trust-ladder --global --yes \
  --skill ktl-sidecar --skill ktl-librarian --skill ktl-curator \
  --skill ktl-docent --skill ktl-prose
```

**Start with the sidecar and the librarian**; the curator matters once there is a bundle worth trusting.

```text
# Claude Code plugin
/plugin marketplace add noelmcloughlin/knowledge-trust-ladder
/plugin install knowledge-trust-ladder@knowledge-trust-ladder
```

## Install with the GitHub CLI

[`gh skill`](https://cli.github.com/manual/gh_skill_install), GitHub CLI v2.90.0+:

```bash
gh skill install noelmcloughlin/knowledge-trust-ladder ktl-sidecar --scope user
gh skill install noelmcloughlin/knowledge-trust-ladder ktl-librarian --scope user
gh skill install noelmcloughlin/knowledge-trust-ladder ktl-curator --scope user
gh skill install noelmcloughlin/knowledge-trust-ladder ktl-docent --scope user
gh skill install noelmcloughlin/knowledge-trust-ladder ktl-prose --scope user
```

## Install for your user, not into the repository

The commands above install for your user, so one install serves every repository. A repository needs no copy of its own: the scheduled librarian run installs `ktl-librarian` at the pinned tag before it starts. A user install also keeps the instructions an agent follows under your control, since a copy inside a repository comes from whoever controls that repository ([threat-model.md](threat-model.md)). Install into the repository only when a team wants every member on one version. Leave out `--global`, or pass `--scope project`, and commit the `skills-lock.json` that `npx skills` writes.

## Pin to one tag

All five skills release together under one tag, so pin them to the same one. Append it to the skill name (`ktl-docent@v0.16.0`) or pass `--pin v0.16.0`. [releasing.md](releasing.md) says what each version level means.

## Microsoft 365 Copilot

Copilot runs custom skills in a sandbox with no repository, so only the **docent** goes there, and it takes a snapshot of the bundle with it. [m365.md](m365.md) says where to get it and how to add it to a declarative agent.

## What each skill needs

Every skill runs from a POSIX shell and starts with a preflight that prints what this machine can do and which steps that disables.

| Skill | Needs |
| --- | --- |
| `ktl-sidecar`, `ktl-librarian` | [`uv`](https://docs.astral.sh/uv/), for the `lokf` toolkit |
| `ktl-curator` | this machine signed in to the forge (`gh` or `glab`) to record a confirmation in your name, and signed commits when you open your own curation pull requests ([signing-commits.md](signing-commits.md)) |
| `ktl-docent` | nothing |
| `ktl-prose` | `python3` 3.9 or newer, or `uv`, for its check script, and git to compare a file with its earlier version |

Someone who cannot act on a line the preflight prints, such as a **curator** who knows the subject but not the repository, gets a request note for whoever set the repository up. The note comes from the **sidecar**'s [prerequisites page](../skills/ktl-sidecar/references/prerequisites.md).
