# Install

This page is for anyone installing the six skills. Already have a healthy `.lokf/`? Skip the **sidecar**.

## Quick start

**Start with the sidecar and the librarian.** The curator matters once there is a bundle worth trusting, and the website skill once there is one worth showing. [Your first bundle](first-bundle.md) walks through a first run.

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

Install all six skills with the Open Skills CLI, [`npx skills`](https://github.com/vercel-labs/skills).

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

### PyPI

Each release is also the [`ktl`](https://pypi.org/project/ktl/) package on PyPI, which carries the six skills and a command that installs them. It has no dependencies and needs Python 3.9 or later. It installs for GitHub Copilot unless you add `--agent claude-code` or `--agent codex`, or give the folder your agent reads with `--dest`:

```bash
uvx ktl skills install --scope user
```

Without uv, `pipx run ktl skills install --scope user` does the same. `python3 -m pip install --user ktl` works where the system lets pip install for a user; Debian, Ubuntu and Homebrew refuse it. To update, add `@latest`: `uvx ktl@latest skills install --scope user`. `ktl skills status` says whether the skills in each folder an agent reads are the package's. `ktl skills path` prints the folder that holds the skills, which `gh skill install --from-local` and `npx skills add` take in place of `noelmcloughlin/knowledge-trust-ladder`. The [package's page](https://pypi.org/project/ktl/) gives the Claude Code plugin route from the installed package.

## Install for your user, not into the repository

A user install keeps the instructions that an agent follows under your control ([threat-model.md](threat-model.md)). The scheduled librarian run installs `ktl-librarian` from the `ktl` package that `.lokf/pyproject.toml` pins before it starts. Install into the repository only when a team wants every member on one version: leave out `--global`, or pass `--scope project`, and commit the `skills-lock.json` that `npx skills` writes.

## Turn on the workflows

The librarian, the ingest and the site's deploy wait for a repository variable to turn them on, and so do the release and the federation, except when run by hand; the registrar's checks, the weekly sync and the site's pull-request build need none. Set these under Repository variables (Settings, Secrets and variables, Actions, Variables), never on an Environment, which a job's `if:` cannot read. Put each secret in the Environment of the workflow that reads it, limited to the default branch, never as a repository secret that any branch's workflow can read. [The sidecar's automation page](../skills/ktl-sidecar/references/automation.md#switches-and-where-they-go) lists every switch and secret, and where each goes. On GitHub, `uvx ktl gh plan` lists what a repository still needs, and `ktl gh apply`, `secrets` and `enable` set it, as [the settings page](../skills/ktl-sidecar/references/repository-settings.md) says.

The workflows are GitHub Actions. On GitLab, Codeberg, Forgejo or Gitea, [the sidecar's portability page](../skills/ktl-sidecar/references/portability.md#not-github-gitlab-codeberg-forgejo-gitea-another-forge-or-none) says what their CI runs instead, and what the forge-free gate replaces.

## Pin to one tag

All six skills are released together under one tag, so pin them to the same one. Append it to the skill name (`ktl-docent@v0.16.0`) or pass `--pin v0.16.0`. From PyPI, the package version is the tag without its `v`: `uvx ktl@X.Y.Z skills install ...` for `vX.Y.Z`. A repository with a sidecar pins it once in `.lokf/pyproject.toml`, with `uv add --project .lokf "ktl==X.Y.Z"`, and its weekly sync moves the pin. [releasing.md](releasing.md) says what each version level means.

## Microsoft 365 Copilot

Copilot runs custom skills in a sandbox with no repository, so only the **docent** runs there, and it carries a snapshot of the bundle. [m365.md](m365.md) says where to get it and how to add it to a declarative agent.

## What each skill needs

Every skill runs from a POSIX shell (on Windows, the bash of Git for Windows, as [portability.md](../skills/ktl-sidecar/references/portability.md#not-linux-windows-and-powershell) says) and starts with a preflight that prints what this machine can do and which steps that disables.

| Skill | Needs |
| --- | --- |
| `ktl-sidecar`, `ktl-librarian` | [`uv`](https://docs.astral.sh/uv/), for the `lokf` toolkit |
| `ktl-curator` | this machine signed in to the forge (`gh` or `glab`) to record a confirmation in your name, and signed commits when you open your own curation pull requests ([signing-commits.md](signing-commits.md)) |
| `ktl-docent` | nothing |
| `ktl-prose` | `python3` 3.11 or newer, or `uv`, for its check script, and git to compare a file with its earlier version |
| `ktl-website` | a sidecar from 0.30.0 or later, and `uv` to build the site on this machine, with no Node.js; GitHub Actions and Pages to publish it, or the same build in another forge's CI ([deploy.md](../skills/ktl-website/references/deploy.md#another-forge)) |

Someone who cannot act on a line that the preflight prints, such as a **curator** who knows the subject but not the repository, gets a request note for whoever set the repository up. The note comes from the **sidecar**'s [prerequisites page](../skills/ktl-sidecar/references/prerequisites.md).
