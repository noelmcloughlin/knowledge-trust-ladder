# Install

This page gives every way to install the six skills, what each needs on the machine, and how to pin them to one release. [Quick start](#quick-start) says which skills to start with. Already have a healthy `.lokf/`? Skip the **sidecar**.

## Quick start

**Start with the sidecar and the librarian.** The curator matters once there is a bundle worth trusting, and the website skill once there is one worth showing.

> **Only want to ask?** Install the docent skill into any agent you already use and ask it about this project. It answers from this repository's own bundle and says how far each answer has been checked. See [eight captured answers](examples/docent.md).

### GitHub CLI

Use [`gh skill`](https://cli.github.com/manual/gh_skill_install) version 2.90.0 or later. It defaults to GitHub Copilot, so pass `--agent` to name your agent (`claude-code`, `github-copilot`, `cursor`, `codex`, `gemini-cli`, or another from `gh skill install --help`):

```bash
gh skill install noelmcloughlin/knowledge-trust-ladder --all --scope user
```

To install only one, name it:

```bash
gh skill install noelmcloughlin/knowledge-trust-ladder ktl-docent --scope user
```

### Open Skills CLI

Install all six skills with the Open Skills CLI, [`npx skills`](https://github.com/vercel-labs/skills). Behind a company proxy or an internal npm registry, the command could fail.

```bash
npx skills add noelmcloughlin/knowledge-trust-ladder --global --yes \
  --skill ktl-sidecar --skill ktl-librarian --skill ktl-curator \
  --skill ktl-docent --skill ktl-prose --skill ktl-website
```

In PowerShell or cmd, type the command on one line without the `\` continuations.

### Claude Code plugin

```text
/plugin marketplace add noelmcloughlin/knowledge-trust-ladder
/plugin install knowledge-trust-ladder@knowledge-trust-ladder
```

## Install for your user, not into the repository

A user install keeps the instructions an agent follows under your control ([threat-model.md](threat-model.md)). The scheduled librarian run installs `ktl-librarian` at the pinned tag before it starts. Install into the repository only when a team wants every member on one version: leave out `--global`, or pass `--scope project`, and commit the `skills-lock.json` that `npx skills` writes.

## Turn on the workflows

Each workflow the skills install does nothing until a repository variable turns it on. Set these under Repository variables (Settings, Secrets and variables, Actions, Variables), never on an Environment, which a job's `if:` cannot read. Put each secret in the Environment of the workflow that reads it, limited to the default branch, never as a repository secret that any branch's workflow can read. [The sidecar's automation page](../skills/ktl-sidecar/references/automation.md#switches-and-where-they-go) lists every switch and secret, and where each goes.

The workflows are GitHub Actions. On GitLab, Codeberg, Forgejo or Gitea, [the sidecar's portability page](../skills/ktl-sidecar/references/portability.md#not-github-gitlab-codeberg-forgejo-gitea-another-forge-or-none) says what their CI runs instead, and what the forge-free gate replaces.

## Pin to one tag

All six skills are released together under one tag, so pin them to the same one. Append it to the skill name (`ktl-docent@v0.16.0`) or pass `--pin v0.16.0`. [releasing.md](releasing.md) says what each version level means.

## Microsoft 365 Copilot

Copilot runs custom skills in a sandbox with no repository, so only the **docent** runs there, and it carries a snapshot of the bundle. [m365.md](m365.md) says where to get it and how to add it to a declarative agent.

## What each skill needs

Every skill runs from a POSIX shell (on Windows, the bash of Git for Windows, as [portability.md](../skills/ktl-sidecar/references/portability.md#not-linux-windows-and-powershell) says) and starts with a preflight that prints what this machine can do and which steps that disables.

| Skill | Needs |
| --- | --- |
| `ktl-sidecar`, `ktl-librarian` | [`uv`](https://docs.astral.sh/uv/), for the `lokf` toolkit |
| `ktl-curator` | this machine signed in to the forge (`gh` or `glab`) to record a confirmation in your name, and signed commits when you open your own curation pull requests ([signing-commits.md](signing-commits.md)) |
| `ktl-docent` | nothing |
| `ktl-prose` | `python3` 3.9 or newer, or `uv`, for its check script, and git to compare a file with its earlier version |
| `ktl-website` | a sidecar from 0.30.0 or later, `uv`, and Node.js 22.12 or newer with npm to build the site on this machine; GitHub Actions and Pages to publish it, or the same build in another forge's CI ([deploy.md](../skills/ktl-website/references/deploy.md#another-forge)) |

Someone who cannot act on a line the preflight prints, such as a **curator** who knows the subject but not the repository, gets a request note for whoever set the repository up. The note comes from the **sidecar**'s [prerequisites page](../skills/ktl-sidecar/references/prerequisites.md).
