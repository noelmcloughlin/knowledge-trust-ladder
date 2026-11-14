# The GitHub settings: `ktl gh`

The Step 5 workflows read repository variables, secrets kept in Environments, and a few repository settings, as [automation.md](automation.md#switches-and-where-they-go) lists them. `ktl gh`, a command of the `ktl` package, sets them from [repository-settings.json](repository-settings.json) beside this page, and from ktl-website's own. It calls the GitHub CLI with your own login, so it needs `gh auth login` and admin rights on the repository. On another forge, set the same intent by hand, as [portability.md](portability.md#not-github-gitlab-codeberg-forgejo-gitea-another-forge-or-none) says.

Run it in a clone of the repository, or name one with `--repo owner/name`:

```sh
uvx ktl gh plan              # what is missing or different, and why; changes nothing
uvx ktl gh apply             # the Environments, their branch rules, and the values a catalogue gives
uvx ktl gh secrets           # each secret the workflows read, asked for without an echo
uvx ktl gh enable librarian  # one switch, once what it needs is in place
uvx ktl gh prune             # retired names, and copies no workflow can read
uvx ktl gh check             # the gaps alone, exiting 1 while one remains
```

## What each verb does

- **`plan`** reads the workflows under `.github/workflows/`, the catalogues and the repository's settings. It prints each item with the verb that deals with it and the reason. `--role bundle`, `domain`, `ingest` or `website` counts that role's workflows as present before they are installed. `--json` prints the plan for a script.
- **`apply`** creates each Environment the workflows name, limited to the refs the catalogue gives, and adds what is missing: a branch rule, a required reviewer (you, or whom `--reviewer` names), a rule of a ruleset, a setting. It never loosens. A wider branch rule, a reviewer the catalogue does not ask for, or a variable with another value is reported for you to decide. It never turns a switch on. It turns on again a workflow a catalogue describes that GitHub turned off, which GitHub does to a scheduled workflow in a public repository after 60 days with no activity there. `--recommended` makes the [hardening](#hardening) changes too. `--agent copilot`, `claude-code` or `members` sets the librarian's agent variables to the commands [automation.md](automation.md#setting-it-up) gives.
- **`secrets`** asks for each missing secret, saying what it is for. An empty answer skips one. Without a terminal it reads `NAME=value` lines from standard input, or from the file `--from` names. Each value reaches `gh secret set` on standard input, never in an argument. It sets no secret before its Environment exists.
- **`enable <switch>`** turns one switch on once what it needs holds: `librarian`, `release`, `website`, `ingest`, `federation`, `sync-review`, `curation`, or another a catalogue names. It makes the settings it can, such as letting Actions open pull requests or taking Pages from Actions, and stops on the rest. `--run` starts the workflow's first run by hand. `ktl gh enable` alone lists the switches.
- **`prune`** removes a variable or secret a release retired, a switch set on an Environment, where no job's condition reads it, and a repository copy of a secret its Environment now holds. It keeps a name a workflow in the repository still reads.
- **`check`** lists what `plan` leaves to `apply`, `secrets`, `prune` or a person, and exits 1 while anything required remains. `--strict` counts the recommended items too.

Each verb that changes something prints the changes and asks first, unless `--yes` is given.

## Hardening

These are recommended for every repository: `apply --recommended` makes them, and `check --strict` counts them.

- A ruleset on the default branch that blocks deletion and force pushes. A rule requiring a pull request or a passing check would refuse a release job's own push, so the catalogue asks for neither.
- A ruleset on tags matching `v*` that blocks moving and deleting them. Creating a tag stays open to the release job.
- Actions pinned to a commit. The plan holds this back while any workflow still uses a tag.
- A read-only default workflow token.
- Secret scanning, push protection and private vulnerability reporting, on a public repository.
- Dependabot alerts and security updates.
- A required reviewer on an Environment named `release`, where one exists.
- A workflow that publishes an OpenSSF Scorecard result, on a public repository. `ktl gh` writes no workflow, so `plan` leaves it to you: [scorecard.yml](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/.github/workflows/scorecard.yml) in KTL's own repository is one to copy, with its badge in the README.

## The catalogue

A catalogue is a JSON file. Each skill that installs workflows carries one in its `references/`. A repository describes its own workflows in `.github/repository-settings.json`, and a template that writes workflows of its own carries its file under `.github/repository-settings/`. `ktl gh` reads every one it finds, and `--catalogue <file>` adds another.

| Field | Holds |
| --- | --- |
| `format` | `1` |
| `source` | the catalogue's name |
| `docs` | the address each entry's `docs` is relative to |
| `roles` | for each role, its `title`, its `workflows`, and `with`, the roles it includes; `--role` reads these |
| `presets` | for each preset, its `title`, `docs`, and `variables`, each a value or `null` for unset; `default_for` names a workflow whose presence proposes the preset while `AGENT_CLI` is unset |
| `settings` | the entries |
| `retired` | for each retired name, its `kind`, `name`, `replaced_by`, `why`, and `changelog`, the release whose entry says why it went |

Every entry has a `kind`, a `name` and a `why`, and may have `docs`. `workflows` names the files that read it; with none, it applies to every repository. Its `level` is `required` unless it says `recommended`, or `optional`: checked where it is set or exists, and never created.

| Kind | Fields |
| --- | --- |
| `variable` | `job_level` when a job's `if:`, `runs-on:` or `environment:` reads it; `pattern`, which the whole value must match; `check: repositories` for a list of `owner/name` that must be current; `switch` |
| `switch`, in a variable | `name`, for `enable`; `values`, `["true"]` unless given; `environment`, when the switch names an Environment, which then needs a reviewer first; `run`, the workflow `--run` starts; `requires` |
| `secret` | `environment`, or none for a repository secret; `repository_copy: true` where a repository copy may stay beside it; `unless`, a requirement under which it is not needed; `names_from: ingest`, for one secret per name `.lokf/ingest.yaml` gives |
| `environment` | `branches`, where `{default}` is the default branch; `tags`; `reviewers`, the least number, where `0` asks for none since each run would wait; `named_by`, the variable that holds its name |
| `setting` | `value`; `visibility`, the visibilities it applies to; `report_only` |
| `ruleset` | `target`, `branch` or `tag`; `include`, refs as GitHub writes them, `~DEFAULT_BRANCH` among them; `rules`, the rule types |
| `workflow` | `uses`, the action as `owner/name`, which a workflow under `.github/workflows/` must use; `inputs`, each input that workflow must give and its value; `visibility`. It names no `workflows`, since it asks for whichever file does the work |

A requirement in `requires` or `unless` is one of `variable`, which may say what it `equals`; `unset`; `secret`, with its `environment`; `any`, a list; `setting`, with its `value`; `pages`; `without`, a workflow that must be absent; `without_publishers`; `file`; `secrets_from`; `visibility`; or `confirm`, a fact a person confirms because GitHub cannot see it. Its `text` says it in words.

Two entries of one kind and name, and for a secret one Environment, merge: their workflows join, their branch rules and rules add up, and the stricter level wins. The tests hold KTL's catalogues to the templates, and to the table in [automation.md](automation.md#switches-and-where-they-go).
