---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/ktl-command
title: The ktl command
description: How the ktl package from PyPI installs the six skills for an agent (ktl skills install, status, path) and sets the GitHub variables, secrets, Environments and rulesets their workflows need (ktl gh plan, apply, secrets, enable, prune, check), from each skill's repository-settings.json catalogue.
genre: how-to
resource: src/ktl/README.md
sources:
  - resource: src/ktl/README.md
    id: ktl-readme.md
    excerpt: The package has no dependencies and needs Python 3.9 or later.
  - resource: skills/ktl-sidecar/references/repository-settings.md
    id: repository-settings.md
    excerpt: It never loosens.
  - resource: docs/releasing.md
    id: docs-releasing.md
    excerpt: Required reviewers on it wait until releases have downstream users
  - resource: src/ktl
  - resource: skills/ktl-sidecar/references/repository-settings.json
  - resource: skills/ktl-website/references/repository-settings.json
  - resource: .github/repository-settings.json
  - resource: pyproject.toml
  - resource: alias
  - resource: tests/test_gh.py
  - resource: CHANGELOG.md
relatedTo:
  - https://w3id.org/ktl/knowledge/playbooks/ktl-sidecar-skill
  - https://w3id.org/ktl/knowledge/playbooks/releasing
  - https://w3id.org/ktl/knowledge/references/gh-skill-cli
generated:
  by: process:ktl-librarian
  at: "2026-11-14T19:45:34Z"
status: draft
---

# Overview

`ktl` is the PyPI package that carries the six KTL skills and a command of the same name. The package has no dependencies and needs Python 3.9 or later.[^ktl-readme.md] A second package, `knowledge-trust-ladder`, holds no code and installs `ktl` at the same version under the repository's name. The command's code is in `src/ktl/`, and it uses the standard library alone.

# Install the skills: `ktl skills`

- `ktl skills install` copies the six skills into the folder an agent reads. Without `--agent` it installs for GitHub Copilot, as `gh skill install` does. `--agent claude-code` or `--agent codex` installs for those agents, and `--dest` names any other agent's folder. `--scope` takes `user` or `project`, and `--skill` installs one skill.
- `ktl skills status` checks each folder an agent reads, and says whether each KTL skill there is the same as the package's. It exits 1 when a copy differs. A copy that `gh skill install` made counts as the same when only gh's own rewrite of its `SKILL.md` differs.
- `ktl skills path` prints the folder that holds the skills, for `gh skill install --from-local`, `npx skills add` or a Claude Code plugin marketplace.

`ktl skills` opens no network connection and runs nothing it copies.

# Set the GitHub settings: `ktl gh`

The workflows the skills install read repository variables, secrets kept in Environments, and a few repository settings. `ktl gh` compares what each catalogue asks for with a repository's settings, and sets what is missing. It calls the GitHub CLI with the user's own login, so it needs `gh auth login` and admin rights on the repository. On another forge, a person sets the same intent by hand.

- `plan` lists each missing or different item with the verb that deals with it and the reason. It changes nothing.
- `apply` creates each Environment the workflows name, limited to the refs the catalogue gives. It adds a missing branch rule, required reviewer, ruleset rule or setting. It never loosens a setting and never turns a switch on.[^repository-settings.md] `--recommended` also makes the hardening changes.
- `secrets` asks for each missing secret without an echo. It hands each value to `gh secret set` on standard input, never in an argument.
- `enable <switch>` turns one switch on once everything it needs is in place, and `--run` starts the workflow's first run.
- `prune` removes a variable or secret a release retired, such as `KNOWLEDGE_LIBRARIAN_CMD`. It also removes a switch set on an Environment, and a repository copy of a secret its Environment now holds.
- `check` lists only the gaps, and exits 1 while a required one remains. `--strict` counts the recommended items too.

Each verb that changes something prints the changes and asks first, unless `--yes` is given.

# The catalogues

A catalogue is a JSON file. It lists each variable, secret, Environment, setting and ruleset a set of workflows needs, with the reason. ktl-sidecar and ktl-website each carry one as `references/repository-settings.json`, and this repository describes its own workflows in `.github/repository-settings.json`. Each entry is `required`, `recommended` or `optional`.

The sidecar's catalogue marks the hardening `recommended`: rulesets on the default branch and on `v*` tags, a read-only default workflow token, secret scanning and push protection, and a required reviewer on a `release` Environment. In this repository, required reviewers on `release` wait until releases have downstream users.[^docs-releasing.md] `tests/test_gh.py` holds the catalogues to the templates, to the table of switches and secrets in `automation.md`, and to the retired names the changelog gives.

[^ktl-readme.md]: src/ktl/README.md, the paragraph after the title
[^repository-settings.md]: skills/ktl-sidecar/references/repository-settings.md, What each verb does, `apply`
[^docs-releasing.md]: docs/releasing.md, the paragraph after the table of repositories
