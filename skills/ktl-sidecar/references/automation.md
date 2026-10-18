# Step 5 automation: what the files do and how to set them up

You install these files once. This page covers the librarian loop, the release asset and the feedback script, and how to set each up. [gate.md](gate.md) covers the registrar workflow and the two scripts it runs, and ktl-librarian's [scheduled-task.md](../../ktl-librarian/references/scheduled-task.md) says how the librarian loop behaves at run time. The workflows apply only to a **git-tracked** `.lokf/` on **GitHub**; SKILL.md Step 5 says why a gitignored bundle makes them a permanent no-op. [portability.md](portability.md#not-github-gitlab-codeberg-forgejo-gitea-another-forge-or-none) says what GitLab, Codeberg, Forgejo or Gitea keep of them, and what a port rewrites.

Each file has a section on one of the two pages. Read the one you are setting up.

| File | What it does | What you set up | Where |
| --- | --- | --- | --- |
| `knowledge-registrar.yaml` | Validates the bundle, and checks that each new human confirmation is backed by its person | Nothing to set up. Curators sign their commits; the attestation environment is optional | [gate.md](gate.md) |
| `knowledge-conventions.sh` and `.py` | The checks the gate runs that `lokf validate` cannot | Nothing | [gate.md](gate.md) |
| `knowledge-provenance.sh` | The signature check, with no forge needed, and the check that an unattended change touches no person's record | A public key per curator under `.lokf/curators/`; nothing for the unattended form | [gate.md](gate.md) |
| `knowledge-librarian.yaml` | Runs the librarian agent weekly when work waits for it, and opens a review pull request | Repository variables, and a secret for the agent's key | below |
| `knowledge-librarian.sh` | The wrapper the librarian workflow runs | Nothing, unless the skills live in an unusual directory | below |
| `knowledge-apply.sh`, `knowledge-apply.py` | The librarian's only pen: applies `.lokf/patch.yaml` to the bundle; the wrapper runs it after the agent | Nothing | ktl-librarian's `references/patch.md`, or `--format` |
| `knowledge-report.sh` | What a program can say about the bundle: each trust label, the health line, the librarian's work list, whether any work waits, what a change does to the record, the retrieval score, and the tracked files no concept names | Nothing, or one variable for the retrieval score | below |
| `knowledge-release.yaml` | Attaches the bundle to a GitHub release as a zip file | One variable to turn it on, or run it by hand | below |
| `knowledge-feedback.sh` | Records a reader's gap without reading the file | Nothing. It never runs in CI | below |
| `knowledge-federation.yaml` and `knowledge-federate.py` *(a domain host only)* | Build the workspace of a domain host from the released bundles its member concepts name, publish it, and keep the members current | One variable to turn it on, Pages taken from Actions, and `AGENT_CLI` set to the script | below |
| `knowledge-sync.yaml`, `knowledge-sync.sh` and `PULL_REQUEST_TEMPLATE/knowledge-sync.md` | Keep the sidecar copies and the skills pin at the newest release of the skills repository, and open the pull request that moves them | One secret, so the workflow can open the pull request; without it the run attaches the change | below |
| `knowledge-ingest.yaml`, `knowledge-ingest.sh` and `PULL_REQUEST_TEMPLATE/knowledge-ingest.md` *(a host with `.lokf/ingest.yaml`)* | Mirror the sources outside the repository that the manifest names into `.lokf/mirror/`, and open one pull request with what changed | One variable to turn it on, and the secrets the manifest names | [below](#knowledge-ingestyaml-knowledge-outside-the-repository) |

## Switches and where they go

Every switch below is a **repository variable** or a **repository secret**: Settings, Secrets and variables, Actions, then Variables or Secrets, under the Repository heading. Never set one on an environment such as `release`, or under the Agents tab, which is the Copilot cloud agent's store. A job's `if:` reads only repository and organization variables, so a switch set anywhere else stays off without a word.

| Name | Kind | Workflow | What it does |
| --- | --- | --- | --- |
| `KNOWLEDGE_LIBRARIAN_ENABLED` | variable | `knowledge-librarian.yaml` | `true` runs the agent; anything else skips it |
| `AGENT_CLI` | variable, or a secret when it must embed a credential | `knowledge-librarian.yaml` | the agent command ([below](#setting-it-up)) |
| `AGENT_PROMPT_FLAG` | variable | `knowledge-librarian.yaml` | optional: where the prompt goes, `-p` by default ([below](#any-other-agent)) |
| `AGENT_API_KEY_ENV` | variable | `knowledge-librarian.yaml` | the name the agent reads its credential from |
| `AGENT_API_KEY` | secret | `knowledge-librarian.yaml` | the agent's key or token; never a variable, which anyone with access can read |
| `AGENT_USE_JOB_TOKEN` | variable | `knowledge-librarian.yaml` | `true` for Copilot CLI, which pays with the job's token, and for a domain host's members script, which verifies attestations with it |
| `KNOWLEDGE_RETRIEVAL` | variable | `knowledge-librarian.yaml` | optional: `true` scores retrieval on each run that changes the bundle |
| `KNOWLEDGE_RELEASE_ENABLED` | variable | `knowledge-release.yaml` | `true` attaches the bundle to each published release |
| `KNOWLEDGE_RELEASE_NAME` | variable | `knowledge-release.yaml` | optional: the name in the zip file when the repository's own name is not the one it publishes under |
| `KNOWLEDGE_WEBSITE_ENABLED` | variable | `knowledge-website.yaml` | `true` publishes the site to GitHub Pages, as ktl-website's [deploy.md](../../ktl-website/references/deploy.md) says |
| `KNOWLEDGE_FEDERATION_ENABLED` | variable | `knowledge-federation.yaml` | `true` builds the workspace on each release and deploys the site with it; a domain host leaves `KNOWLEDGE_WEBSITE_ENABLED` unset, since this workflow is its one Pages deployer |
| `KNOWLEDGE_SYNC_TOKEN` | secret | `knowledge-sync.yaml` | a fine-grained personal access token for this repository, with Contents, Pull requests and Workflows set to read and write ([below](#knowledge-syncyaml-keeping-the-sidecar-current)). The workflow pushes under `.github/workflows/` and opens the pull request with it. Unset, each run attaches its change and opens nothing |
| `KNOWLEDGE_INGEST_ENABLED` | variable | `knowledge-ingest.yaml` | `true` turns the ingest on; unset or anything else, the workflow does nothing ([below](#knowledge-ingestyaml-knowledge-outside-the-repository)) |
| `KNOWLEDGE_INGEST_*` | secrets | `knowledge-ingest.yaml` | the credentials `.lokf/ingest.yaml` names, one secret per name; the workflow hands these names over and no other secret |

The librarian also needs one repository setting: Settings, Actions, General, Workflow permissions, *Allow GitHub Actions to create and approve pull requests* ([below](#before-turning-on-the-schedule)).

## `knowledge-librarian.yaml`: the scheduled refresh loop

It runs weekly (Mondays 05:00 UTC) and on demand, in three jobs:

- **`earlier`** reads what became of the pull requests this workflow opened before. Its token can read pull requests and nothing else. It checks nothing out and runs no agent.
- **`refresh`** is read-only. It checks out the full history, sets up `uv`, installs the sidecar, runs the reviewed agent wrapper, validates, runs the conventions script, and diffs `.lokf/knowledge/` only, so tool artifacts such as a fresh `uv.lock` never trigger a pull request. If anything changed it packages the change as a patch artifact, together with `.lokf/feedback.md`, the reader-feedback file ktl-docent writes and the librarian consumes, and `.lokf/questions.md`, the ledger a handled entry moves into. The librarian's hand-off is uploaded beside the patch.
- **`publish`** is the privileged job and runs no agent code. It applies that patch on a clean checkout and checks the result before it commits. Then it commits to a fresh `knowledge-librarian/<date>-<run_id>` branch and opens a review pull request via `github-script`. It fills that pull request itself, with `knowledge-report.sh` on its own checkout: the bundle's health line, and what the change does to the record. The pull request also says how `lokf validate` and the conventions script ended in `refresh`, since the registrar's gate does not run on a pull request this workflow opens. The hand-off goes under *From the librarian*, as the agent's own words.

**A quiet week runs no agent.** A scheduled run asks `knowledge-report.sh quiet` first, and skips the agent when nothing waits for it. Work waits when a source moved after its concept's stamp, or a person left a note after the librarian last wrote or checked that concept. It waits too when reader feedback is on file, or a concept carries no stamp at all, as the skeleton's do. A scheduled run in a month's first seven days goes ahead regardless. The work list never fetches a source given as a URL and names no file the source map leaves out, so the librarian reads both at least monthly. A run you start from the Actions tab always runs the agent. Change the cadence in the agent step's `run` line.

A moved source stops making work once the librarian's own question covers it: an open question of its own that names the source's path, committed no earlier than the source's last change. The usual case is a concept a person confirmed whose source is then deleted. Only the curator retires that concept, so the librarian asks once and the week is quiet again. The source makes work again when it changes after the question.

**A scheduled run waits its turn.** `earlier` finds the pull requests this workflow opened by their branch, `knowledge-librarian/...` in this repository, and reads two things off them:

- **One is still open.** The default branch is where it was, so the agent would propose the same change again. A scheduled run stops before `refresh`, and the run's log names the pull request.
- **A person closed one without merging.** That person declined what it changed. `earlier` hands the next scheduled runs a record of it: its number, its base commit, the concepts it touched or added, and a hash of each feedback entry it handled. `knowledge-report.sh` counts none of that as work, and the work list names it, so the librarian proposes none of it again.

Each declined item makes work again once it changes after that pull request: its source moves, a person leaves a new note, or a reader asks again. A run you start from the Actions tab reads no record and waits for no open pull request, so starting one is how you ask the librarian to try again. The pull request it opens then names the earlier one. `earlier` reads the three hundred newest pull requests, and keeps the ten newest of this workflow's that were closed without merging.

**The hand-off is the agent's words, and the pull request says so.** The patch file may carry `handoff`, up to ten lines for the reviewer, such as a send-back that came up twice or a source that did not answer. The pen accepts each only as one line of printable text with no backtick, and writes them nowhere in the bundle. `publish` cleans them again and shows them in a code block, where no link, image, mention or HTML renders. Both take out every character a reader cannot see, by its Unicode category: a control, a zero-width space, a bidirectional mark or a tag character.

The guardrails:

- Only `publish` holds `contents: write` and `pull-requests: write`. The agent runs in a `contents: read` job with no persisted credentials.
- It never pushes to the default branch and never auto-merges.
- It opens no pull request when nothing changed, and runs no agent in a scheduled week when nothing waits or while a pull request of its own is still open.
- `earlier` holds `pull-requests: read` alone. It passes on numbers, dates, commits, concept paths and hashes, each matched against a pattern, and reads no title, body or comment.
- What runs is the reviewed `.lokf/scripts/knowledge-librarian.sh`, at a fixed path, not an arbitrary command string.
- `publish` refuses a patch that touches a path outside the bundle, the feedback file and the ledger, and one that touches a person's record. It reads that off the patched tree with `knowledge-provenance.sh --unattended`, so a `human:` event in any YAML layout, a person's note and text a person wrote are all covered.

### Setting it up

The workflow is **inert until set up**. With `KNOWLEDGE_LIBRARIAN_ENABLED` unset (or not `true`) the agent step is skipped, so the workflow does nothing until you set these:

| Repository variable | Value |
| --- | --- |
| `KNOWLEDGE_LIBRARIAN_ENABLED` | `true`: turns on the scheduled run; anything else (or unset) leaves the agent step skipped |
| `AGENT_CLI` | your non-interactive agent command; the wrapper appends `-p "<prompt>"`. The two commands below are the ones this file vouches for, and [any other agent](#any-other-agent) says what a third must do. Keep the credential out of it; if it must embed one, make it a *secret* named `AGENT_CLI` instead, which the workflow also reads |
| `AGENT_PROMPT_FLAG` | optional. The flag the prompt follows, `-p` unless set, or `arg` for an agent that takes the prompt as its bare last argument. Leave it unset for the two commands below |
| `AGENT_API_KEY_ENV` | the environment variable the agent reads its credential from: `COPILOT_GITHUB_TOKEN` for Copilot CLI, `ANTHROPIC_API_KEY` for Claude Code |
| `AGENT_USE_JOB_TOKEN` | `true`: the job's own `GITHUB_TOKEN` is the credential, passed under that name. Copilot CLI accepts it, and so does a [domain host's](#knowledge-federationyaml-the-workspace-of-a-domain-host) members script; leave it unset for any other agent |
| `KNOWLEDGE_RETRIEVAL` | optional. `true`: each run that changes the bundle makes one more agent call and the pull request carries a retrieval score ([below](#knowledge-reportsh-what-a-program-can-say-about-the-bundle)). Unset, nothing is scored |

Set each one under **Repository variables** (Settings, Secrets and variables, Actions, Variables), or with `gh variable set <name> --body <value>`. A variable set on an environment, such as `release`, is never seen: no job in the sidecar's workflows names an environment, and a job's `if:` reads only repository and organization variables.

| Repository secret | Value |
| --- | --- |
| `AGENT_API_KEY` | the agent's API key or token, when `AGENT_USE_JOB_TOKEN` is not set. The wrapper hands it to the agent under the `AGENT_API_KEY_ENV` name and to nothing else |

### What the wrapper refuses

The wrapper splits `AGENT_CLI` on whitespace and honours no quotes, so no flag value may contain a space; both commands below are written that way. It refuses to start when:

- `knowledge-apply.sh` or its Python half is not beside it, since the bundle is written through them alone;
- only one of the credential and `AGENT_API_KEY_ENV` is set;
- the name does not end `_API_KEY`, `_TOKEN` or `_KEY`, so a slip cannot overwrite `PATH` or `LD_PRELOAD`;
- the name starts `GITHUB_`, `GH_`, `GIT_`, `RUNNER_` or `ACTIONS_`, because `gh`, git and the runner read those too;
- `AGENT_PROMPT_FLAG` is anything but a short flag, a long flag or the word `arg`, so the variable can move the prompt and add nothing else.

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
| `AGENT_CLI` | `npx -y @anthropic-ai/claude-code@2.1.281 --permission-mode dontAsk --allowedTools Read,Edit(.lokf/patch.yaml),Bash(git:*),Bash(uv:*),Bash(uvx:*),Bash(just:*),Bash(bash:*)` |
| `AGENT_API_KEY_ENV` | `ANTHROPIC_API_KEY` with a Console key, or `CLAUDE_CODE_OAUTH_TOKEN` with a subscription token |
| `AGENT_API_KEY` (secret) | an API key from the Claude Console, or the token `claude setup-token` prints |
| `AGENT_USE_JOB_TOKEN` | unset. Claude Code cannot use the job's GitHub token |

Pay for the runs in one of two ways. A Console API key is billed per use, apart from any subscription, and the Console can cap its spending. A Pro or Max subscription needs no API billing: run `claude setup-token` on your own machine, and it prints a long-lived token for your account. The runs then count against that subscription's usage limits, which your own sessions share.

`dontAsk` denies any call that would otherwise prompt, so a run never waits for a person, and `--allowedTools` names what the skill needs. `Edit(.lokf/patch.yaml)` confines every file write to the patch file, which the wrapper applies with `knowledge-apply.sh` after the run; the bundle itself is on no list. An `Edit` rule covers every file-writing tool, the Write tool included; Claude Code ignores a `Write(<path>)` rule and says so in the log. `dontAsk` denies a shell write through a command not on the list, such as `echo` or `cat`, so the wrapper's prompt tells the agent to write the patch file with its own file tool. `Bash(git:*)` is the prefix form, and it is why no pattern has a space: a rule such as `Bash(git log:*)` cannot be passed, since the wrapper splits on spaces.

### Any other agent

The wrapper is written for no one vendor. It runs the command `AGENT_CLI` names, puts the prompt where `AGENT_PROMPT_FLAG` says, hands the credential over under the name `AGENT_API_KEY_ENV` gives, and checks the result the same way whoever ran. So a third agent works when it meets five conditions:

1. It runs one prompt without a terminal and exits when the prompt is done, as `-p` does for the two above.
2. It takes that prompt after a flag or as its last argument, with no quoting in between. Set `AGENT_PROMPT_FLAG` to the flag, or to `arg`.
3. It asks no question in that run, and denies rather than waits where it would ask. A denied call shows in the log; a call that waits for an answer runs until the job's timeout.
4. It can write `.lokf/patch.yaml` with its own file tool, and run `git`, `uv`, `uvx`, `just` and `bash` in the checkout. Pre-approve those in the command. Where the agent lets you scope the file approval to a path, scope it to the patch file; where it does not, the wrapper's post-run check still refuses a run that wrote anywhere else.
5. It reads its credential from one environment variable whose name ends `_API_KEY`, `_TOKEN` or `_KEY`. Name it in `AGENT_API_KEY_ENV` and put the value in the `AGENT_API_KEY` secret.

Two agents known to fit, neither of which this file has run unattended:

| Agent | What differs |
| --- | --- |
| Gemini CLI | `-p`, as the two above, and `GEMINI_API_KEY`. Approval is `--approval-mode yolo`, which pre-approves every tool, so the wrapper's post-run check is the one boundary |
| Codex CLI | `codex exec` takes the prompt as its last argument, and `-p` names a profile. Set `AGENT_PROMPT_FLAG` to `arg`. The credential is `CODEX_API_KEY`, and the sandbox must be `--sandbox workspace-write` for the patch file to be written |

The job sets up Node 22 and uv before the agent step, so a command that runs through `npx` or `uvx` needs no install step. An agent installed another way needs a step of its own in the workflow, before the wrapper runs, in a copy you maintain.

Whichever agent, the wrapper's prompt names no vendor. It tells the agent to write the patch file with its own file-writing tool, since an unattended run may deny a shell write, and the skill it follows says the same.

### Before turning on the schedule

Type every value in the Settings form without quotes. GitHub stores exactly what you type, so a quote becomes part of the value: `AGENT_API_KEY_ENV` is then refused, and `AGENT_CLI` passes the quote to the agent.

Both commands pin the CLI's version, as every action in the workflow is pinned, so a run executes the code you tried. A new CLI release reaches the librarian when you move the pin, not before. Move it on purpose, from the CLI's release notes; nothing bumps a repository variable for you.

Let the workflow open its pull request. `publish` opens it with the job's own `GITHUB_TOKEN`, and GitHub refuses that with a 403 while the repository setting *Allow GitHub Actions to create and approve pull requests* is off, as it is by default. Turn it on under Settings, Actions, General, Workflow permissions, and keep the default token read-only, or run:

```sh
gh api -X PUT repos/<owner>/<repo>/actions/permissions/workflow -f default_workflow_permissions=read -F can_approve_pull_request_reviews=true
```

The same setting lets a workflow approve a pull request. No workflow the sidecar installs does, and the registrar's gate counts an approval only from the person a confirmation names, so a workflow's approval never stands in for one.

Whichever agent, run the workflow once by hand from the Actions tab before turning on the schedule, and read the agent's log for denied tool calls. A run that ends with *the agent wrote no `.lokf/patch.yaml`* on a bundle with work waiting usually means a denied write: look for the agent's file tool in the log, and widen the approval to the patch file.

## `knowledge-librarian.sh`: the agent wrapper

It is generic, with no placeholders. It resolves the repository root from its own location and finds `ktl-librarian/SKILL.md` under `.claude/skills/`, `.github/skills/`, `.agents/skills/` or `skills/`. If your repository uses another directory, extend the `candidate` list and run the script once to confirm. It then builds a prompt telling the agent to follow that skill, and calls `$AGENT_CLI -p`.

The workflow relies on this contract:

- the agent writes one file, `.lokf/patch.yaml`, and the wrapper applies it with `knowledge-apply.sh`, so the bundle, a handled feedback entry and its ledger line change only through that script;
- the patch file's hand-off reaches the file `KNOWLEDGE_HANDOFF_OUT` names through the same script, and the wrapper removes that file and the retrieval score's once the agent returns. So the workflow reads only what was written after the agent, and no link the agent left there can send a write into the checkout. The retrieval test calls the agent a second time, so the wrapper writes the pen's hand-off there again after that call;
- a run in which the agent changed any other path, or whose result touches a person's record, is refused;
- it never commits, pushes or opens pull requests;
- it exits 0 whether or not anything changed. The workflow diffs the tree to decide about a pull request. With `KNOWLEDGE_SKIP_QUIET` set to `true`, as the workflow sets it on a scheduled run, a bundle `knowledge-report.sh quiet` finds quiet ends the run before the agent is called;
- `KNOWLEDGE_DECLINED`, which the workflow sets on a scheduled run, names the record of what a person declined. The wrapper passes it on untouched, and `knowledge-report.sh` reads it for the quiet check and for the agent's work list.

## `knowledge-release.yaml`: the bundle as a release asset

It attaches `.lokf/knowledge` to a GitHub release as `knowledge-<tag>-<repository>.zip`, with a `.sha256` file beside it, so a reader can take the bundle as it stood at that release without cloning the repository. Every operating system opens a zip file with its own tools. It runs no agent and needs no LLM. It never commits or pushes.

It starts in two ways:

- **By hand, always.** Run it from the Actions tab, or `gh workflow run knowledge-release.yaml -f tag=<tag>`, naming an existing release's tag.
- **On each published release, once turned on.** Set the `KNOWLEDGE_RELEASE_ENABLED` repository variable to `true`, under Repository variables and not on an environment. Unset, each release shows the run as skipped.

`<repository>` is the repository's name. A host that publishes under another name, such as a package renamed for PyPI, sets it in the `KNOWLEDGE_RELEASE_NAME` repository variable: letters, digits, `.`, `_` and `-`. The Copilot skill zips take the same name.

GitHub starts no workflow for a release made with the default `GITHUB_TOKEN`, so the release trigger never fires when your release job makes releases that way. Have that job dispatch this workflow after it creates the release, with `actions: write` on the job: `gh workflow run knowledge-release.yaml --ref "$TAG" -f tag="$TAG"`. The skills repository's own `publish.yml` does this.

### An unchanged bundle gets no zip

The `pack` job compares the bundle's git tree at the tag with its tree at the newest other published release that carries a knowledge bundle, as a zip or as the tarball earlier releases attached. When the two match, the run ends green with a notice naming that release, and nothing is uploaded. A reader who wants the bundle for such a release takes it from the release the notice names. The tree changes only when a tracked file in the bundle does, so a release that touched only code or docs compares as unchanged. To attach a zip anyway, for example to repair a release's assets, start the workflow by hand with `force` ticked.

### The domain schema beside it

When the host's `.lokf/justfile` names a schema on its `schema :=` line, the release carries that file too, as `schema-<tag>-<name>.yaml` with its own `.sha256` and attestation. A domain that admits the bundle names it as a second distribution of the member concept and validates the bundle against it, rather than against LOKF core alone. The line is read as text and must name a file in `.lokf/`, never a path.

### What the zip holds

When the bundle changed, `pack` runs the registrar's two checks, so a release never carries a bundle its own gate would fail. It then packs the bundle under a read-only token:

- The zip holds the tracked files under a `knowledge/` root.
- It is reproducible. Every file carries the time of the last commit that touched the bundle, so a reader can rebuild it from the tag and compare checksums, and an unchanged bundle gives the same checksum at every release.
- A link inside the bundle is stored as a link and never followed, so the zip can hold nothing from outside the bundle. A bundle normally carries none; the `knowledge_bundle` doorway sits at the repository root, outside it.
- It is built with `zip` and checked with `unzip`, which GitHub's hosted Ubuntu runners carry. A self-hosted runner needs both installed.

The `attach` job holds `contents: write`, runs no third-party packages, checks the zip against its checksum and uploads both files, replacing an earlier upload of the same name. On a public repository it also records a build-provenance attestation; check one with `gh attestation verify <file> -R <owner>/<repo>`. A private repository needs GitHub Enterprise Cloud for attestations, so the step skips itself there.

## `knowledge-federation.yaml`: the workspace of a domain host

A domain host is one whose bundle names other bundles: each `MemberBundle` concept (or `MemberDomain`, when that bundle is a domain in turn) names one released zip and its checksum, a person confirms that it belongs, and the workspace is the graph built from those releases, one named graph per bundle. The design is the skills repository's `docs/context-layer.md`, and `docs/federation.md` says how the workspace is built; `templates/domain.yaml` is the schema. Three files make it run, and nothing in them runs a model.

- **The build.** `uv run --project .lokf .lokf/scripts/knowledge-federate.py build --tag <tag>` resolves the members into `snapshot/workspace.lock.yaml`, fetches each zip into `.lokf/.cache/federation/` by digest, checks it against the checksum the member concept names, refuses a zip holding a symbolic link or a path outside its root, verifies its attestation with `gh attestation verify` when `gh` is present, checks that the zip's `index.md` names the `base_iri` the concept declares, registers and exports each bundle with the toolkit, loads one named graph per bundle (blank nodes relabelled so the same releases give the same bytes), writes the lock as a graph of its own, gates every typed relation whose target lies in no member's namespace as the domain's `unowned_targets` says, and renames `snapshot.new/` to `snapshot/` in one step. A member whose zip is itself a domain is followed, tier by tier, as deep as the top `Domain` concept's `max_depth` allows (3 unless set), and a bundle two domains name at one release joins once, named by both in the lock; named at two releases it stops the build. `--verify-only` stops after the zips are checked.
- **The workflow.** On a release of the host (the host's release job dispatches it, since a release made with `GITHUB_TOKEN` starts no workflow), `build` runs the build from the tag and the website build when there is one, and `publish` attaches `workspace-<tag>.zip` with its checksum and attestation to the release and deploys the Pages artifact with the workspace under `/workspace/`. On a push to the default branch it rebuilds the site and reuses the newest released workspace. On a pull request that changes a member it runs `build --verify-only`. GitHub starts no workflow for a pull request the librarian's job token opened, so on the librarian's pull request that job first runs when a person pushes to it, as the curator's confirmation commit does. Weekly it dispatches the librarian workflow, because a bundle whose sources are release URLs is always quiet to the schedule.
- **The members script.** `knowledge-federate.py members` lists each member's releases through the public GitHub API, picks the newest release that carries a `knowledge-*.zip`, verifies it, and writes the change as `patch` and `question` operations in `.lokf/patch.yaml` for the pen, with what it verified in the hand-off lines. The patch moves the old tag, zip name and release day in the description and the body as well as in the frontmatter, and names the `schema-<tag>-<name>.yaml` released beside the zip as a second distribution when there is one. A body line it cannot change safely stays as it is, and the question says how many stay. A member a person wrote gets the question alone. Set `AGENT_CLI` to `uv run --project .lokf .lokf/scripts/knowledge-federate.py members`; the wrapper's `-p` prompt is ignored. Set `AGENT_USE_JOB_TOKEN` to `true` and `AGENT_API_KEY_ENV` to `KNOWLEDGE_FEDERATE_TOKEN` too: the script hands the job's read-only token to `gh attestation verify` alone, and stops before writing anything when it has no credential. So the change is verified when it is written, before the `check` job can run on it. The pen restamps `generated`, so a moved member a person confirmed reads "edited since a person confirmed it" until the curator confirms the new release. By hand, `members --add <owner>/<repo>` drafts a new member concept from that repository's newest bundle release the same way, as a `create` with a question, and as a `MemberDomain` when that release is a domain.
- **The readers.** `knowledge-federate.py mcp` is the `lokf-registry` MCP server over the snapshot (`resolve_iri`, `neighbors`, `subgraph`, `federated_sparql`, `read_document`, each bounded, the workspace index as its instructions), `serve` the toolkit's SPARQL endpoint and graph page, and `query` a one-off query; each takes `--snapshot <path>` to read an unpacked `workspace-<tag>.zip` anywhere. The curator's [domain-bundle.md](../../ktl-curator/references/domain-bundle.md#reading-the-workspace) says how to use each, and how to serve `graph.nq` read-only from a container.

To set it up: tell Pages once to take its site from Actions (`gh api -X POST repos/{owner}/{repo}/pages -f build_type=workflow`), set `KNOWLEDGE_FEDERATION_ENABLED` to `true`, leave `KNOWLEDGE_WEBSITE_ENABLED` unset, set `AGENT_CLI`, `AGENT_USE_JOB_TOKEN` and `AGENT_API_KEY_ENV` as above with `KNOWLEDGE_LIBRARIAN_ENABLED` `true`, let the workflow open its pull request as [Before turning on the schedule](#before-turning-on-the-schedule) says, and add `gh workflow run knowledge-federation.yaml --ref "$tag" -f tag="$tag"` to the host's release job beside its dispatch of `knowledge-release.yaml`.

## `knowledge-sync.yaml`: keeping the sidecar current

A release of the skills repository changes the templates, and a host carries copies of them. The copies and the skills pin in `knowledge-librarian.yaml` move together from one release, because the skill a release installs is written against the wrapper, gate and preflight that release includes. The pin also decides which instructions the scheduled librarian follows unattended. This workflow moves them.

It runs weekly (Mondays 04:10 UTC) and on demand, in three jobs:

- **`earlier`** reads the pin and the address of the skills repository out of `knowledge-librarian.yaml`, asks that repository for its newest release, and reads what became of this workflow's last pull request. Its token can read the repository and its pull requests, and nothing else, and it reads no pull request's title, body or comment. When the pin is at the newest release, the run stops after one read. The skills repository must be public, or at least readable with the job's token.
- **`sync`** is read-only, and runs no code from the release. It runs the host's own `.lokf/scripts/knowledge-sync.sh`, which clones the release and reads its `knowledge-sync.manifest`: each template a host may carry, its copy, and the rule for it. The script writes the release's templates over the host's copies, adds a template a file here needs, moves the pin to the tag and the commit it names, and writes the changelog entry under `## [Unreleased]` and `### Security`. The change goes to `publish` as a patch, and to the run as an artifact.
- **`publish`** refuses a patch that touches anything but the sidecar's copies, the site's copies, the pin and `CHANGELOG.md`, and checks that the tag names the pinned commit at the skills repository. Then it applies the patch on a clean checkout, commits it as `knowledge-sync[bot]`, pushes the branch `knowledge-sync` and opens the pull request, or refreshes the open one. It writes the body from the patch it applied, not from anything `sync` wrote: the files and the pin. Then comes `.github/PULL_REQUEST_TEMPLATE/knowledge-sync.md`, whose checklist is the reviewer's. The pull request's own checks run the synced copies, as they run on any change.

**One pull request at a time, refreshed until it is merged.** While this workflow's pull request is open, a later run that finds a newer release replaces the branch's one commit with a sync to that release, and sets the title and body to say so. The week's releases fold into one pull request, and a reviewer reads the diff as it is when they merge. A pull request a person added a commit to is left alone: merge or close it first.

**What a person decided holds.** A tag whose pull request a person closed without merging is not proposed again by the schedule. A run you start from the Actions tab may name a tag, and goes ahead in every case but one. A pull request that proposes that tag and is still open stops it, whether this workflow opened it or you did from a `sync-<tag>` branch. A pull request opened by hand for an older release is not seen, so merge or close it yourself.

### Setting it up

The pull request changes files under `.github/workflows/`, which the job's own `GITHUB_TOKEN` may not push. So `publish` pushes and opens the pull request with one repository secret:

| Repository secret | Value |
| --- | --- |
| `KNOWLEDGE_SYNC_TOKEN` | a fine-grained personal access token (Settings, Developer settings, Personal access tokens, Fine-grained tokens) for this repository alone, with the repository permissions Contents, Pull requests and Workflows set to read and write, and an expiry you will renew. A GitHub App's installation token, made in a step of your own before `publish` pushes, serves the same |

Without the secret the workflow still runs: `sync` attaches the change to the run as `sync.patch` and writes the summary, and `publish` says so and opens nothing. A pull request opened with the token is opened under the token's owner and starts this repository's checks, as one opened with `GITHUB_TOKEN` would not.

The skills repository can ask for the sync as soon as a release is tagged. Its `publish.yml` dispatches this workflow in each host named in its `KNOWLEDGE_SYNC_HOSTS` variable, with a token that holds Actions write there. The variable is a list of `owner/repo` names, and `false` asks nobody, as unset does. A host it does not name, or cannot reach, syncs on its own schedule.

### By hand

The script the workflow runs is yours too. From the host, once the tag exists:

```sh
.lokf/scripts/knowledge-sync.sh --pr v0.47.0       # branch, commit, push and open the pull request
.lokf/scripts/knowledge-sync.sh --branch v0.47.0   # the sync alone, on sync-v0.47.0, with the commit command printed
```

Without `--source` it clones the tag from the address `knowledge-librarian.yaml` names; `--source <dir>` reads it from a clone you have. It refuses a tree with uncommitted changes, a branch that exists, and a tag that is not a published release. `--no-checks` skips the sidecar's checks, which the pull request's checks run again. The script reads the release's `knowledge-sync.manifest` and copies what it lists. A rule in it that your copy of the script does not know is reported and left for the next sync, once the copy the release brings is merged.

**Reviewing the pull request.** Read the diff as you would any change to a workflow or a script: the copies are what the host runs. The report at the top names the release, the files that moved and the pin, and says when the run refreshed an earlier diff. The release's own changelog, linked from the entry, says why each file changed. A sync that moves only the pin releases nothing new in the host apart from the pin, and still deserves the read: it decides what the librarian runs next. The `sync` job's summary holds the script's own lines, among them a copy that differed only on its action pins, which Dependabot bumped in the host first; the template's pins are back until the skills repository bumps them.

A private host should turn harden-runner's egress policy from `audit` to `block` in the `sync` job, with the skills repository and GitHub allowed: that job clones the release with the host's checkout readable.

## `knowledge-ingest.yaml`: knowledge outside the repository

A bundle cites what the librarian can read, and the librarian reads the repository. A wiki page, a document on an intranet address, a file in another repository or the output of a command is outside it. The ingest brings a copy in. `.lokf/ingest.yaml` names each source, `knowledge-ingest.sh` fetches it and writes it as Markdown under `.lokf/mirror/<entry id>/`, and `.lokf/ingest.lock.yaml` records what was fetched. A mirror file is repository content: the librarian derives concepts from it as from any tracked file, and names it as the concept's `resource` with the origin as a `sources` entry. [ingest.md](https://w3id.org/ktl/docs/ingest/) in this skill's home repository is the guide to the manifest; this section is the workflow.

It runs weekly (Sundays 04:10 UTC) and on demand, in two jobs:

- **`ingest`** is read-only. It hands the script the repository secrets whose names start `KNOWLEDGE_INGEST_` and no other, reads the repository's visibility, and runs the host's own `.lokf/scripts/knowledge-ingest.sh`. The script lists each entry, fetches what moved, converts it, writes the mirror and the lock, and refuses what the manifest's caps and the repository's visibility do not allow. The change goes to `publish` as a patch, and the run's summary to the job's page.
- **`publish`** holds the write token and no secret. It refuses a patch that touches anything but `.lokf/mirror/` and the lock, applies it on a clean checkout, commits it as `knowledge-ingest[bot]`, pushes the branch `knowledge-ingest` and opens the pull request, or refreshes the open one. The body is the run's summary and then `.github/PULL_REQUEST_TEMPLATE/knowledge-ingest.md`, whose checklist is the reviewer's.

**One pull request at a time, refreshed until it is merged.** A later run replaces the branch's one commit with today's mirror and writes the body again. A pull request a person added a commit to is left alone. One a person closed without merging is a no: a scheduled run proposes the mirror again only once `.lokf/ingest.yaml` has changed, and a run started by hand proposes it now. The librarian's Monday run then finds each concept whose mirror file moved in its work list, as it finds any moved source, and reads only those.

### Setting it up

1. Copy `templates/ingest.yaml` to `.lokf/ingest.yaml` and replace its examples with your sources. Each `auth` block names environment variables, never a value.
2. Store each credential as a repository secret of the name the manifest gives, such as `KNOWLEDGE_INGEST_ATLASSIAN_TOKEN`. For Confluence Cloud that is an API token with read scopes and an expiry, used as HTTP Basic with the account's email in `KNOWLEDGE_INGEST_ATLASSIAN_USER`; for a repository, a fine-grained token with Contents read.
3. Set the repository variable `KNOWLEDGE_INGEST_ENABLED` to `true`, and turn on *Allow GitHub Actions to create and approve pull requests* under Settings, Actions, General, which the `publish` job needs to open the pull request with the job's own token.
4. Start one run from the Actions tab and read its summary. An entry that says *failed* with a credential's name is a secret not yet set; the run shows each such line as a warning too.

The pull request starts no checks, since the job's own token opened it; the mirror is text, and the registrar's conventions run on the bundle alone. Merge it, and the librarian's next run reads the mirror.

### By hand

The script the workflow runs is yours too, with the credentials in the environment:

```sh
KNOWLEDGE_INGEST_ATLASSIAN_USER=me@example.com KNOWLEDGE_INGEST_ATLASSIAN_TOKEN=... \
  bash .lokf/scripts/knowledge-ingest.sh --visibility private     # every entry
bash .lokf/scripts/knowledge-ingest.sh --dry-run --only platform-runbooks   # one entry, nothing written
bash .lokf/scripts/knowledge-ingest.sh --prune                   # remove gone and unlisted files no concept cites
bash .lokf/scripts/knowledge-ingest.sh --patch                   # Reference concepts for the entries that ask, for the pen
```

`--visibility` says whether the repository is public or private, which decides whether an `internal` entry may be committed. By hand the script asks `gh` when it is signed in, and otherwise counts the repository as public and refuses internal entries until told. Commit the mirror and the lock with the bundle change, as the person who ran it. A private host should set harden-runner's egress policy to `block` in the `ingest` job, with the sources' hosts allowed, since the host's checkout and its secrets are readable there.

## `knowledge-feedback.sh`: how a reader's gap gets recorded without being read back

It has no placeholders, and it is the one script here that has nothing to do with CI. It adds a Miss or a Disagreement to `.lokf/feedback.md` in an ordinary session. ktl-docent runs a byte-identical copy from its own `scripts/` folder, never this one, so a question runs no code the repository supplies. This copy serves a person, and an earlier ktl-docent that ran it:

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

Three more pins decide what a run installs, and no update tool moves them:

- **The skill.** `TRUST_LADDER_SKILLS_REF` names a release tag of the skills repository, and `TRUST_LADDER_SKILLS_SHA` the commit that tag named when the pin was set. A tag can be moved, and what it names is the instructions an agent follows unattended. So the install step installs nothing unless the tag still names that commit. Move the two together.
- **The toolkit.** All three workflows install it with `uv sync --locked`: what `.lokf/uv.lock` names, each file checked against the hash recorded there. A lock that is missing or behind `.lokf/pyproject.toml` fails the step, so commit `uv.lock`, and run `uv lock` in the change that moves the `lokf` floor.
- **The parser.** The Python halves of the conventions script and the pen install PyYAML through `uv run`, from the dependency block each file carries. That block names one release, and `exclude-newer` takes no file uploaded after its date. A copy from a newer release of the sidecar moves both.

## `knowledge-report.sh`: what a program can say about the bundle

It has no placeholders and writes nothing. A trust label, the health line and the librarian's work list are arithmetic over frontmatter and git history, and this script does that arithmetic so that no model has to:

```sh
bash .lokf/scripts/knowledge-report.sh [--root <dir>] [health | labels [<path>...] | worklist | quiet | changes | retrieval --prompt | retrieval <reply-file> | coverage [<dir>...]]
```

- With no command it prints the whole report ktl-curator's Step 1 starts from: the health line, every concept's label, the open questions, and the confirmed concepts whose source moved after the confirmation.
- `labels` prints one line per concept, in the shape of ktl-docent's footer.
- `worklist` is where ktl-librarian starts a refresh: the sources that moved since each concept was derived or last checked, the notes a person left, and how much reader feedback waits. It holds paths and dates, and nobody's words. It names two kinds of item apart, since the librarian acts on neither: a moved source its own question already covers, and what a person declined by closing the workflow's pull request.
- `quiet` exits 0 when nothing waits for the librarian and 1 when work does, with one line of counts. A note counts while its commit comes after the one that recorded the concept's latest stamp, so a note the librarian has read waits for the curator alone. The two kinds the work list names apart do not count, and the line says how many it set aside. A bundle git holds no full history of is never quiet. The wrapper asks it before a scheduled run.
- `changes` says what the working tree does to the record against `HEAD`. It names each confirmed concept the change touches, and says how that concept reads afterwards: still confirmed, edited since that confirmation, or removed. The librarian workflow's `publish` job fills its pull request from it.
- `retrieval` measures what the index promises, and the next section covers it.
- `coverage` counts, per top-level folder, the tracked files under no path a concept names in its `resource` or `sources`, and lists them under a folder you name. It is ktl-librarian's sweep for orphans, and it makes no scheduled run busy.

A source has moved when its last commit comes after the commit that recorded the event it is compared with, or when it carries an edit not yet committed and the concept does not. History orders the two, never a clock, so a source changed in that same commit has not moved. That is the file's history and not its meaning: only reading the source says whether a fact changed. Without git, or with a shallow clone or a gitignored `.lokf/`, the script says the sources were not compared.

It needs bash and awk, and uses git where there is one. It runs wherever the other scripts here run, and in a workflow job that installs nothing, which is why `publish` can run it.

### The retrieval score

ktl-docent chooses what to open from `index.md` alone, and a concept's `description` is written so that it can. The score measures that. Set the `KNOWLEDGE_RETRIEVAL` repository variable to `true`, and each scheduled run that changes the bundle makes one more agent call:

1. `retrieval --prompt` builds one prompt: the root index's entries, and the questions readers asked, from the ledger in `.lokf/questions.md`.
2. The wrapper has the agent answer it from an empty directory, so the index is all it has. A call that changes anything in the checkout refuses the run.
3. `retrieval <reply-file>` scores the reply by program. A question counts when a concept the ledger names for it is among the first three paths the reply gives. A question whose every concept has left the bundle is not asked, and the score says how many were left out. What a reply is scored against comes from the ledger alone, never from a line of the reply.

The pull request carries the one line, as `n of m`. With no question on file there is no call and no line. The score reports and gates nothing: a person merges, as before.
