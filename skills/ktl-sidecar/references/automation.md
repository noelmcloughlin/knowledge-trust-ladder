# Step 5 automation: what the files do and how to wire them

You lay these files down once. ktl-librarian's operating manual, [`../../ktl-librarian/references/scheduled-task.md`](../../ktl-librarian/references/scheduled-task.md), says how they behave at run time. They apply only to a **git-tracked** `.lokf/` on **GitHub**; SKILL.md Step 5 says why a gitignored bundle makes the workflows a permanent no-op.

Each file has a section below. Read the one you are wiring, or the whole page once.

| File | What it does | What you set up |
| --- | --- | --- |
| `knowledge-registrar.yaml` | Validates the bundle, and checks that each new human confirmation is backed by its person | Nothing to wire. Curators sign their commits; the attestation environment is optional |
| `knowledge-librarian.yaml` | Runs the librarian agent weekly and opens a review pull request | Repository variables, and a secret for the agent's key |
| `knowledge-release.yaml` | Attaches the bundle to a GitHub release as a tarball | One variable to arm it, or run it by hand |
| `knowledge-librarian.sh` | The wrapper the librarian workflow runs | Nothing, unless the skills live in an unusual directory |
| `knowledge-conventions.sh` and `.py` | The checks the gate runs that `lokf validate` cannot | Nothing |
| `knowledge-provenance.sh` | The signature check, with no forge needed | A public key per curator under `.lokf/curators/` |
| `knowledge-feedback.sh` | Records a reader's gap without reading the file | Nothing. It never runs in CI |

## `knowledge-registrar.yaml`: the validation and provenance gate

The registrar keeps the bundle's records well-formed and provenanced. It never judges whether their content is true; that is the curator's job. The workflow runs no agent code at all, and none of its jobs can write to the repository.

### The `validate` job

It runs on every pull request touching `.lokf/**` (or the workflow itself), weekly on Mondays at 06:00 UTC, and on demand. It holds `contents: read` only, and a newer run on the same ref cancels the older one. Keep it green: the bar is that the projected graph describes the repository as it is today.

It runs two checks:

1. `uv run lokf validate --check-refs knowledge`: the schema check, and every typed relation must point at a concept in the bundle.
2. `bash scripts/knowledge-conventions.sh knowledge`: the conventions the toolkit cannot see, listed under `knowledge-conventions.sh` below.

It checks out the full history, because the conventions script resolves each commit-shaped `revision` against a commit.

### The `provenance` job

It runs on pull requests only, and enforces the other half of the registrar's remit: that the paperwork is *provenanced*, not merely well-formed.

A `human:<id>` verification claims that a named person checked a concept against its source. Nothing in the format proves one. Any writer that can edit the file can type the string, and `lokf validate` sees a perfectly valid event.

So the job collects the actor of every `human:` event the pull request adds or changes under `.lokf/knowledge/`. An event is a `verified` entry, or the `generated` record the curator's Correct writes. The job reads each one whole from the frontmatter and keys it by the concept's `id`, so:

- a re-dated event counts;
- a renamed concept does not;
- an id quoted in an `## Open questions` note or a body code fence is not an event at all.

For each actor it then requires evidence from the forge, one of:

- an **APPROVED** review from that account; or
- a signature of *theirs* on the commit that introduced the event, when that person opened the pull request. GitHub will not let authors approve their own pull request, so the signature is the route for them.

Signature status comes from GitHub's API rather than `git log %G?`. A runner has neither a GPG keyring nor an allowed-signers file, so locally every signature reads as unverifiable however good it is. The API also names the account each commit is attributed to, which is what ties a signature to a person rather than merely proving one exists.

The job needs `pull-requests: read` and `contents: read`, and `fetch-depth: 0` because it diffs against the merge base. Where the repository carries curator keys under `.lokf/curators/`, it also runs `knowledge-provenance.sh` (below) as a second opinion.

This is what makes ktl-curator's confirmations mean anything to a later reader. Without it, "confirmed by a person" is only as good as whatever wrote the file. The cost is intended: a curation pull request now needs its curator's approval or signature before it can merge.

### When the confirming person opens the pull request: sign the commits

Set up signing once, reusing the SSH key you already push with:

```sh
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
```

Then add that same key again at `github.com/settings/keys`, this time as a **signing** key. This step is not optional. GitHub keeps authentication and signing keys in separate lists, and the gate reads GitHub's own verdict, so a key registered only for auth leaves every commit Unverified however correct the local setup is. Skipping it is the usual reason the gate still fails after someone has started signing. The commit's email must also be a verified email on that account. Commits made through GitHub's web editor are signed by GitHub automatically and pass without any of this. The skills' home repository covers GPG as the alternative, key renewal and what to do when signing fails: [signing your commits](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/docs/signing-commits.md).

A signature is the better route anyway. It is cryptographic and still checkable years later, where a review approval is a mutable record that a force-push can dismiss.

**Why the skills tell you to run these rather than running them for you.** `--global` changes how you commit in every unrelated repository on the machine, and a wrong `user.signingkey` makes `git commit` fail everywhere until you find it. That is too large a side effect for a knowledge sidecar to cause on its own. More to the point, a skill can only do the half that does not help: registering the key with GitHub is the step the gate reads, and doing the local half alone produces Unverified commits while leaving you believing it is set up.

**A committed `.gitconfig` cannot do it either**, if that occurs to you as a shortcut. Git reads `/etc/gitconfig`, `~/.gitconfig` and `.git/config`, never a file in the working tree. It refuses this deliberately: a config file arriving with a clone could otherwise set `core.sshCommand` or an alias and run commands on checkout. A tracked `.gitconfig` is inert, and relying on one is a silent no-op.

### If you cannot sign: the `attestation` job

The third job is an opt-in escape hatch. Enabling it takes two steps, and the first is the one that does the work:

1. **Settings -> Environments -> New environment.** Name it (`knowledge-curation`, say), tick **Required reviewers**, add the people allowed to attest, and save. The name is a GitHub setting, not a file; it has nothing to do with the curation policy concept of the same name that ktl-curator writes.
2. **Settings -> Secrets and variables -> Actions -> Variables**: set `KNOWLEDGE_CURATION_ENVIRONMENT` to that environment's name.

Do not do the second without the first. An environment with no required reviewers approves itself the instant it is reached, so setting the variable while skipping the reviewers silently disables the gate entirely, the failure mode this design exists to avoid. With the variable unset (the default), the `attestation` job never runs and `provenance` simply fails on an unbacked confirmation.

Its shape is deliberate. It is **not** a setting that turns the check off. A permanent "provenance: off" switch gets flipped for one urgent afternoon and never flipped back. From then on the bundle asserts confirmations nothing supports, while the health line and these docs still promise otherwise; that is worse than never having built the gate. So instead of disabling anything, the job asks for a fresh human action on each pull request that needs one: the run pauses, GitHub emails the environment's reviewers, and a person clicks Approve in a browser. An environment reviewer **may** be the person who opened the pull request, since environments do not carry the self-approval ban that pull-request reviews do. That is what makes it usable when one person opens the pull request and attests. Each click is recorded in the deployment log, so it stays auditable afterwards.

Say plainly to whoever clicks what the attestation means. It records that a person with repository access vouched for the confirmation out of band. It is not evidence that anyone opened the concept's source. That distinction is why signing is the recommended path and this is the fallback.

### Marking the required checks

Mark `validate` and `provenance` as required in branch protection, and `attestation` too if you enable it. When a confirmation is backed, `attestation` is skipped rather than run. If your branch-protection configuration treats a skipped required check as blocking, that errs toward a stuck pull request rather than a silent bypass: annoying, but the safe direction.

Add one line to the repository's pull request template for whoever approves a curation pull request: *I opened the sources named by every confirmation I am approving.* An approval then records a task done, not only a click. The gate can prove who approved, never what they read.

One wrinkle follows if you do. The librarian's own pull request (below) never fires this workflow's `pull_request` trigger in the first place: GitHub does not start `pull_request` workflows for a pull request opened with the default `GITHUB_TOKEN`, which is how `knowledge-librarian.yaml`'s `publish` job opens it. Nothing unsafe merges, because `publish` runs its own version of both checks before it opens that pull request (a path allow-list, and no `by: human:` claim). But a required `validate` or `provenance` sits at "Expected" on that pull request until a human fires a fresh event for it: close and reopen it, or push an empty commit. ktl-librarian's scheduled-task.md has the detail.

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

## `knowledge-librarian.sh`: the agent wrapper

It is generic, with no placeholders. It resolves the repository root from its own location and finds `ktl-librarian/SKILL.md` under `.claude/skills/`, `.github/skills/`, `.agents/skills/` or `skills/`. If your repository uses another directory, extend the `candidate` list and run the script once to confirm. It then builds a prompt telling the agent to follow that skill, and calls `$AGENT_CLI -p`.

The workflow relies on this contract:

- it only reads the repository and writes under `.lokf/knowledge/`;
- it never commits, pushes or opens pull requests;
- it exits 0 whether or not anything changed. The workflow diffs the tree to decide about a pull request.

## `knowledge-conventions.sh`: what the gate checks that `lokf validate` cannot

It has no placeholders. The `validate` job runs it after `lokf validate`, and ktl-librarian's audit runs it before handing off. The toolkit reads a concept body as an opaque string and never opens `log.md`, so it never sees these ten conventions. The script holds the bundle to them:

1. `log.md` has one bare `## YYYY-MM-DD` heading per day, newest first (OKF §9, and how the KTL Curator plugin finds today).
2. Every `at:` is quoted.
3. `verified` is a list, carrying at most one `process:ktl-librarian` event.
4. Each `## Open questions` bullet has the `- YYYY-MM-DD, <actor>: ...` shape the curator quotes.
5. Every `resource:` that is not a URL names a file or directory that still exists relative to the repository root, so a vanished source fails the gate rather than waiting for the librarian's next refresh. URLs are never fetched.
6. Every commit-shaped `revision` on an event (lokf 0.9.0+) names a commit that holds the concept's local `resource`. The `validate` job checks out the full history for this; a shallow clone is reported, not passed.
7. One file per `id`. A sync client's conflict copy carries its original's `id`, validates, and silently merges into it in the graph.
8. Every path is lowercase. Two paths differing only by case collide on Windows, macOS and SharePoint, and a space, a parenthesis or an upper-case host name is how sync clients name a conflict copy.
9. Every concept has a closed frontmatter block, with no byte order mark in front of it.
10. The fields the provenance gates read line by line (`id`, and `by`, `at` and `revision` on an event) are spelt with no tag, anchor, alias, quoted key, block scalar or value spanning lines. Each of those is valid YAML that `lokf validate` accepts and neither gate can see.

Each of the first five has been broken by an agent that had it in prose, which is why it is a script. The rest are there so that a pin, a duplicate, a file the script could not read or an event the gate could not fails loudly instead of passing unread.

Four of them (2, 3, 8 and 10) are house rules stricter than OKF, which permits an unquoted datetime, a bare `verified` mapping, any file name and any YAML. The gate asks more so that an event is always appended to a list, a datetime reaches every consumer as one string, a name never collides on a case-insensitive host, and an event reads the same to the gates' line readers as to a parser. Every reader here (the toolkit, both plugins, the gates) does accept a bare mapping, as OKF requires, so that half of rule 3 is style, not safety; the script's header says so.

The check is split across two files, because the conventions split into two kinds of question. Five of the rules ask about a document's YAML: whether an `at:` is quoted, `verified` is a list, an `id` is unique, a frontmatter block closes, and an event is spelt the one way every reader agrees on. A real parser answers those outright, where grep and awk could only approximate, and missed a flow-style `verified: { by: ... }` and a multi-line flow item entirely. So `knowledge-conventions.sh` hands rules 2, 3, 7, 9 and 10, and the open-question bullet rule (4) with them, to `knowledge-conventions.py` next to it, through `uv run`. Nothing needs preinstalling: `uv` reads the script's own dependency header, and CI installs `uv` before this runs. The other four (1, 5, 6 and 8) are git and filesystem facts, so they stay in the shell script, which keeps running (bash, grep and awk, no toolchain) wherever git does. Without `uv` it still runs and says which rules it skipped.

It reads every file with carriage returns and a leading byte order mark stripped, so a Windows checkout gives the same verdict as CI.

## `knowledge-provenance.sh`: the signature half of the gate, on any host

The `provenance` job above needs GitHub. This script does the signature half anywhere git runs, and serves as a second opinion where the job does run. It needs plain git, and gpg or ssh-keygen.

It checks every commit in a range that adds or changes a `human:<id>` event under the bundle, and requires a signature by a key the repository carries for that id. An event is a `verified` entry or the `generated` record, read whole against every parent of the commit and keyed by the concept's `id`, exactly as the GitHub job reads them, so a merge that brings in another curator's confirmation claims nothing. The key on file is `.lokf/curators/<id>.asc` (the `gpg --armor --export` of a GPG key) or `<id>.pub` (an OpenSSH public key file). A GPG key counts with all its subkeys; an SSH signature is checked with `ssh-keygen -Y verify` over the commit's payload.

It fails on:

- an unsigned commit, or one signed by another key, or by an expired or revoked one;
- an id with no key on file;
- a range that adds or changes an id's own key file and a confirmation by that id together. A key lands in its own reviewed change before its holder vouches with it.

With no `.lokf/curators/` it says so and passes: a host that has not opted in loses nothing. The GitHub job runs it as an extra step when a key file exists. On another forge or a plain CI, run it with `<base> <head>` from the pull or merge request. It proves who held the key, never that anyone read the source.

## `knowledge-feedback.sh`: how a reader's gap gets recorded without being read back

It has no placeholders, and it is the one script here that has nothing to do with CI. ktl-docent runs it in an ordinary session to add a Miss or a Disagreement to `.lokf/feedback.md`:

```sh
bash .lokf/scripts/knowledge-feedback.sh [--root <dir>] [--for <login>] <Miss|Disagreement> <text>
```

It inserts the entry above every older one under today's date, creating the file on the first entry anyone records, and prints one line: the kind, the date, and how many entries are now waiting. It prints no entry's text, the new one included.

That is the point of it rather than a convenience. `feedback.md` holds free text from readers who may have no access to the repository, and it is kept newest first, so an insertion used to be a read, an edit and a write back. Every earlier reader's report then entered the docent's context, in a session that had just been fetching URLs and reading repository files, and the only guard was a line of prose telling the agent not to act on them. With the script the docent hands over its own entry and never opens the file, so there is nothing to ignore. The librarian still reads the entries, because consuming them is its job; it does that under the guards in its own skill and behind the scheduled workflow's `publish` job. ktl-curator only ever counts them.

Refusals are part of the contract:

- A kind other than `Miss` or `Disagreement` is rejected, since the librarian has no rule for a third.
- `--for` takes a forge login's characters and nothing else, so an attribution can only ever be a login. That is the one field a later reader might take as evidence that a named person asked.
- The text is collapsed to a single line, so a caller that passes a paragraph cannot forge a second entry.

It files under today's UTC date, as the bundle's timestamps are, and takes a directory lock for the rewrite, so two runs in one checkout cannot drop each other's entry. Exit `2` means nothing was written. Exit `1` means it could not be written: a read-only `.lokf/`, where the docent says the gap out loud instead, or a lock another run holds.

## Customising

The runner, `ubuntu-latest`, is the only project-specific choice; swap in a self-hosted runner group and internal-CA env if your organisation needs them. Actions are pinned to commit SHAs with a version comment. Bump them with your usual update tooling; Dependabot and Renovate handle SHA pins.
