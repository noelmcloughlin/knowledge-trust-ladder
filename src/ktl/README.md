# ktl

The six Knowledge Trust Ladder (KTL) agent skills, and a command that installs them for GitHub Copilot, Claude Code, Codex or any other agent that reads skill folders. The skills keep a LOKF knowledge bundle beside a repository true, and record who checked each claim. [The KTL site](https://w3id.org/ktl/) says what each skill does.

The package has no dependencies, needs Python 3.9 or later, and installs from PyPI or any mirror of it, so it serves a machine that cannot reach github.com.

## Install the skills

Install all six for your user:

```bash
uvx ktl skills install --scope user
```

That installs for GitHub Copilot, as `gh skill install` does. For Claude Code or Codex, add `--agent claude-code` or `--agent codex`. `--scope` takes `user` or `project`. For any other agent, give the folder it reads with `--dest`. To install one skill, add `--skill ktl-docent`. To pin a version, write `ktl@0.64.0` in place of `ktl`. The six skills are released together, so one version pins them all, and installing the next version updates them.

Without uv, install the package with pip, then run the same command:

```bash
python3 -m pip install --user ktl
ktl skills install --scope user
```

## Other installers

`ktl skills path` prints the folder that holds the skills. It is the argument for the installers that take a local folder:

```bash
gh skill install "$(ktl skills path)" --from-local --all --scope user --agent github-copilot
npx skills add "$(ktl skills path)" --global --yes
```

The package folder is also a Claude Code plugin marketplace. Install the package with `uv tool install ktl` first, so that the folder stays in place, then:

```bash
claude plugin marketplace add "$(ktl skills path --marketplace)"
claude plugin install knowledge-trust-ladder@knowledge-trust-ladder
```

`ktl skills list` names the six skills. [The install page](https://w3id.org/ktl/docs/install/) gives every other route, and what each skill needs on the machine.
