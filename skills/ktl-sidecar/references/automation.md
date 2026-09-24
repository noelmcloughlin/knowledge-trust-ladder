# Step 5 automation: what the files do and how to wire them

You lay these files down once. This page covers the librarian loop, the release asset and the feedback script, and how to wire each. [gate.md](gate.md) covers the registrar workflow and the two scripts it runs, and ktl-librarian's [scheduled-task.md](../../ktl-librarian/references/scheduled-task.md) says how the librarian loop behaves at run time. The workflows apply only to a **git-tracked** `.lokf/` on **GitHub**; SKILL.md Step 5 says why a gitignored bundle makes them a permanent no-op.

Each file has a section on one of the two pages. Read the one you are wiring.

| File | What it does | What you set up | Where |
| --- | --- | --- | --- |
| `knowledge-registrar.yaml` | Validates the bundle, and checks that each new human confirmation is backed by its person | Nothing to wire. Curators sign their commits; the attestation environment is optional | [gate.md](gate.md) |
| `knowledge-conventions.sh` and `.py` | The checks the gate runs that `lokf validate` cannot | Nothing | [gate.md](gate.md) |
| `knowledge-provenance.sh` | The signature check, with no forge needed | A public key per curator under `.lokf/curators/` | [gate.md](gate.md) |
| `knowledge-librarian.yaml` | Runs the librarian agent weekly and opens a review pull request | Repository variables, and a secret for the agent's key | below |
| `knowledge-librarian.sh` | The wrapper the librarian workflow runs | Nothing, unless the skills live in an unusual directory | below |
| `knowledge-release.yaml` | Attaches the bundle to a GitHub release as a tarball | One variable to arm it, or run it by hand | below |
| `knowledge-feedback.sh` | Records a reader's gap without reading the file | Nothing. It never runs in CI | below |

## `knowledge-librarian.yaml`: the scheduled refresh loop

It runs weekly (Mondays 05:00 UTC) and on demand, in two jobs:

- **`refresh`** is read-only. It checks out the full history, sets up `uv`, installs the sidecar, runs the reviewed agent wrapper, validates, and diffs `.lokf/knowledge/` only, so tool artifacts such as a fresh `uv.lock` never trigger a pull request. If anything changed it packages the change as a patch artifact, together with `.lokf/feedback.md`, the reader-feedback file ktl-docent writes and the librarian consumes.
- **`publish`** is the privileged job and runs no agent code. It applies that patch on a clean checkout, commits it to a fresh `knowledge-librarian/<date>-<run_id>` branch, and opens a review pull request via `github-script`.

The guardrails:

- Only `publish` holds `contents: write` and `pull-requests: write`. The agent runs in a `contents: read` job with no persisted credentials.
- It never pushes to the default branch and never auto-merges.
- It opens no pull request when nothing changed.
- What runs is the reviewed `.lokf/scripts/knowledge-librarian.sh`, at a fixed path, not an arbitrary command string.

### Wiring it up

The workflow is **inert until wired**. With `KNOWLEDGE_LIBRARIAN_ENABLED` unset (or not `true`) the agent step is skipped, so the workflow is harmless until you set these:

| Repository variable | Value |
| --- | --- |
| `KNOWLEDGE_LIBRARIAN_ENABLED` | `true` - arms the scheduled run; anything else (or unset) leaves the agent step skipped |
| `AGENT_CLI` | your non-interactive agent command; the wrapper appends `-p "<prompt>"`. The two commands below are the ones this file vouches for. Keep the credential out of it; if it must embed one, make it a *secret* named `AGENT_CLI` instead, which the workflow also reads |
| `AGENT_API_KEY_ENV` | the environment variable the agent reads its credential from: `COPILOT_GITHUB_TOKEN` for Copilot CLI, `ANTHROPIC_API_KEY` for Claude Code |
| `AGENT_USE_JOB_TOKEN` | `true` - the job's own `GITHUB_TOKEN` is the credential, passed under that name. Copilot CLI accepts it; leave it unset for any other agent |

| Repository secret | Value |
| --- | --- |
| `AGENT_API_KEY` | the agent's API key or token, when `AGENT_USE_JOB_TOKEN` is not set. The wrapper hands it to the agent under the `AGENT_API_KEY_ENV` name and to nothing else |

### What the wrapper refuses

The wrapper splits `AGENT_CLI` on whitespace and honours no quotes, so no flag value may contain a space; both commands below are written that way. It refuses to start when:

- only one of the credential and `AGENT_API_KEY_ENV` is set;
- the name does not end `_API_KEY`, `_TOKEN` or `_KEY`, so a slip cannot overwrite `PATH` or `LD_PRELOAD`;
- the name starts `GITHUB_`, `GH_`, `GIT_`, `RUNNER_` or `ACTIONS_`, because `gh`, git and the runner read those too.

The key reaches the agent's environment only, never an argument list or the wrapper's own git commands. The workflow sets up Node 22 before the agent step, since both commands below run through `npx`.

### Copilot CLI

Copilot CLI needs three settings and no key to keep:

| Setting | Value |
| --- | --- |
| `AGENT_CLI` | `npx -y @github/copilot@1.0.88 --no-ask-user --allow-tool=read --allow-tool=write --allow-tool=shell(git:*) --allow-tool=shell(uv:*) --allow-tool=shell(uvx:*) --allow-tool=shell(just:*) --allow-tool=shell(bash:*)` |
| `AGENT_API_KEY_ENV` | `COPILOT_GITHUB_TOKEN` |
| `AGENT_USE_JOB_TOKEN` | `true` |

The `refresh` job requests `copilot-requests: write`, which lets the job token pay for the requests. On a personally owned repository they are billed to the owner's Copilot seat. In an organisation the policy *Allow use of Copilot CLI billed to the organization* must be on; it is on by default wherever Copilot CLI is enabled. The token holds `contents: read` besides, and expires with the job.

The flags pre-approve what the skill runs: reading and writing files, and the git, uv, uvx, just and bash commands. A `-p` run can prompt no one, so any other tool call is denied and shown in the log; widen the list when a log shows a denied call the skill needed. `--no-ask-user` stops the CLI asking a question instead. The `write` approval is not scoped to the bundle: the wrapper refuses a run that wrote outside it, and the `publish` job checks the patch again.

A personal access token can stand in for the job token. Use a fine-grained token owned by the person, not by an organisation, with the account permission *Copilot Requests*; a classic `ghp_` token is ignored. Put it in the `AGENT_API_KEY` secret and leave `AGENT_USE_JOB_TOKEN` unset. The requests are then billed to that person's seat, and that person's plan decides which models are available.

### Claude Code

| Setting | Value |
| --- | --- |
| `AGENT_CLI` | `npx -y @anthropic-ai/claude-code@2.1.281 --permission-mode dontAsk --allowedTools Read,Edit(.lokf/knowledge/**),Bash(git:*),Bash(uv:*),Bash(uvx:*),Bash(just:*),Bash(bash:*)` |
| `AGENT_API_KEY_ENV` | `ANTHROPIC_API_KEY` with a Console key, or `CLAUDE_CODE_OAUTH_TOKEN` with a subscription token |
| `AGENT_API_KEY` (secret) | an API key from the Claude Console, or the token `claude setup-token` prints |
| `AGENT_USE_JOB_TOKEN` | unset. Claude Code cannot use the job's GitHub token |

Pay for the runs in one of two ways. A Console API key is billed per use, apart from any subscription, and the Console can cap its spending. A Pro or Max subscription needs no API billing: run `claude setup-token` on your own machine, and it prints a long-lived token for your account. The runs then count against that subscription's usage limits, which your own sessions share.

`dontAsk` denies any call that would otherwise prompt, so a run never waits for a person, and `--allowedTools` names what the skill needs. `Edit(.lokf/knowledge/**)` confines every file edit to the bundle; Edit rules cover new files too. `Bash(git:*)` is the prefix form, and it is why no pattern has a space: a rule such as `Bash(git log:*)` cannot be passed, since the wrapper splits on spaces.

### Before arming the schedule

Type every value in the Settings form without quotes. GitHub stores exactly what you type, so a quote becomes part of the value: `AGENT_API_KEY_ENV` is then refused, and `AGENT_CLI` passes the quote to the agent.

Both commands pin the CLI's version, as every action in the workflow is pinned, so a run executes the code you tried. A new CLI release reaches the librarian when you move the pin, not before. Move it on purpose, from the CLI's release notes; nothing bumps a repository variable for you.

Whichever agent, run the workflow once by hand from the Actions tab before arming the schedule, and read the agent's log for denied tool calls.

## `knowledge-librarian.sh`: the agent wrapper

It is generic, with no placeholders. It resolves the repository root from its own location and finds `ktl-librarian/SKILL.md` under `.claude/skills/`, `.github/skills/`, `.agents/skills/` or `skills/`. If your repository uses another directory, extend the `candidate` list and run the script once to confirm. It then builds a prompt telling the agent to follow that skill, and calls `$AGENT_CLI -p`.

The workflow relies on this contract:

- it only reads the repository and writes under `.lokf/knowledge/`;
- it never commits, pushes or opens pull requests;
- it exits 0 whether or not anything changed. The workflow diffs the tree to decide about a pull request.

## `knowledge-release.yaml`: the bundle as a release asset

It attaches `.lokf/knowledge` to a GitHub release as `knowledge-<tag>.tar.gz`, with a `.sha256` file beside it, so a reader can take the bundle as it stood at that release without cloning the repository. It runs no agent and needs no LLM. It never commits or pushes.

It starts in two ways:

- **By hand, always.** Run it from the Actions tab, or `gh workflow run knowledge-release.yaml -f tag=<tag>`, naming an existing release's tag.
- **On each published release, once armed.** Set the `KNOWLEDGE_RELEASE_ENABLED` repository variable to `true`. Unset, each release shows the run as skipped.

GitHub starts no workflow for a release made with the default `GITHUB_TOKEN`, so the release trigger never fires when your release job makes releases that way. Have that job dispatch this workflow after it creates the release, with `actions: write` on the job: `gh workflow run knowledge-release.yaml --ref "$TAG" -f tag="$TAG"`. The skills repository's own `publish.yml` does this.

### An unchanged bundle gets no tarball

The `pack` job compares the bundle's git tree at the tag with its tree at the newest other published release that carries a knowledge tarball. When the two match, the run ends green with a notice naming that release, and nothing is uploaded. A reader who wants the bundle for such a release takes it from the release the notice names. The tree changes only when a tracked file in the bundle does, so a release that touched only code or docs compares as unchanged. To attach a tarball anyway, for example to repair a release's assets, start the workflow by hand with `force` ticked.

### What the tarball holds

When the bundle changed, `pack` runs the registrar's two checks, so a release never carries a bundle its own gate would fail. It then packs the bundle under a read-only token:

- The tarball holds the tracked files under a `knowledge/` root.
- It is reproducible. Every file carries the time of the last commit that touched the bundle, so a reader can rebuild it from the tag and compare checksums, and an unchanged bundle gives the same checksum at every release.
- Links inside the bundle are stored as links, never followed.

The `attach` job holds `contents: write`, runs no third-party packages, checks the tarball against its checksum and uploads both files, replacing an earlier upload of the same name. On a public repository it also records a build-provenance attestation; check one with `gh attestation verify <file> -R <owner>/<repo>`. A private repository needs GitHub Enterprise Cloud for attestations, so the step skips itself there.

## `knowledge-feedback.sh`: how a reader's gap gets recorded without being read back

It has no placeholders, and it is the one script here that has nothing to do with CI. ktl-docent runs it in an ordinary session to add a Miss or a Disagreement to `.lokf/feedback.md`:

```sh
bash .lokf/scripts/knowledge-feedback.sh [--root <dir>] [--for <login>] <Miss|Disagreement> <text>
```

It inserts the entry above every older one under today's UTC date, creating the file on the first entry anyone records, and prints one line: the kind, the date, and how many entries are now waiting. It prints no entry's text, the new one included.

That is the point of it. `feedback.md` holds free text from readers who may have no access to the repository, and the script exists so the docent never opens the file and no earlier reader's report reaches its session. ktl-docent's [feedback.md](../../ktl-docent/references/feedback.md) says why in full. The librarian still reads the entries, under its own skill's guards and behind the scheduled workflow's `publish` job; ktl-curator only ever counts them.

Refusals are part of the contract:

- A kind other than `Miss` or `Disagreement` is rejected, since the librarian has no rule for a third.
- `--for` takes a forge login's characters and nothing else, so an attribution can only ever be a login. That is the one field a later reader might take as evidence that a named person asked.
- The text is collapsed to a single line, so a caller that passes a paragraph cannot forge a second entry.

It takes a directory lock for the rewrite, so two runs in one checkout cannot drop each other's entry. Exit `2` means nothing was written. Exit `1` means it could not be written: a read-only `.lokf/`, where the docent says the gap out loud instead, or a lock another run holds.

## Customising

The runner, `ubuntu-latest`, is the only project-specific choice; swap in a self-hosted runner group and internal-CA env if your organisation needs them. Actions are pinned to commit SHAs with a version comment. Bump them with your usual update tooling; Dependabot and Renovate handle SHA pins.
