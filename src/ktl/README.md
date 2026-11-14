# ktl

The six Knowledge Trust Ladder (KTL) agent skills, and a command that installs them for GitHub Copilot, Claude Code, Codex or any other agent that reads skill folders, and sets the GitHub settings their workflows need. The skills keep a LOKF knowledge bundle beside a repository true, and record who checked each claim. [The KTL site](https://w3id.org/ktl/) says what each skill does.

The package has no dependencies and needs Python 3.9 or later.

## Install the skills

Install all six for your user:

```bash
uvx ktl skills install --scope user
```

That installs for GitHub Copilot, as `gh skill install` does. For Claude Code or Codex, add `--agent claude-code` or `--agent codex`. `--scope` takes `user` or `project`, and `project` means the top folder of the repository you are in. For any other agent, give the folder it reads with `--dest`. To install one skill, add `--skill ktl-docent`. To pin a version, write `ktl@X.Y.Z` in place of `ktl`, or `ktl==X.Y.Z` to pip. The six skills are released together, so one version pins them all. To update, run the command again as `uvx ktl@latest`, or `uv tool upgrade ktl` where `uv tool install` put the package.

Without uv, pipx does the same:

```bash
pipx run ktl skills install --scope user
```

`python3 -m pip install --user ktl`, then `python3 -m ktl skills install --scope user`, works where the system lets pip install for a user. Debian, Ubuntu and Homebrew refuse it.

## Check what is installed

`ktl skills status` says, for each folder an agent reads at project and user scope, whether each KTL skill there is the same as this package's, and names each file that differs. A copy `gh skill install` made counts as the same when only gh's own rewrite of its `SKILL.md` differs. It exits 1 when a copy differs, so a script can act on it. `--dest` checks one folder.

## Set the GitHub settings

The workflows the skills install read repository variables, secrets kept in Environments, and a few repository settings. `ktl gh` compares what each skill's catalogue asks for with a repository's settings, through the GitHub CLI and your own login, and sets what is missing:

```bash
uvx ktl gh plan              # what is missing, and why; changes nothing
uvx ktl gh apply             # the Environments, their branch rules, and the values a catalogue gives
uvx ktl gh secrets           # each secret, asked for without an echo
uvx ktl gh enable librarian  # one switch, once what it needs is in place
uvx ktl gh prune             # the variables a release retired
```

Run it in a clone, or name a repository with `--repo owner/name`. It needs `gh auth login` and admin rights on the repository. `apply` never loosens a setting and never turns a switch on, and each verb that changes something prints the change and asks first. [Turn on the workflows](https://w3id.org/ktl/docs/install/#turn-on-the-workflows) says what each workflow needs, and links the page on each verb.

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

`ktl skills` names the six skills. The package also goes by the repository's name: `knowledge-trust-ladder` installs `ktl` at the same version. Each release's files can be rebuilt from its tag and compared byte for byte, as [the release page](https://w3id.org/ktl/docs/releasing/#the-ktl-package-on-pypi) says. [The install page](https://w3id.org/ktl/docs/install/) gives every other route, and what each skill needs on the machine.
