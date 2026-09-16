# Step 5 automation - what the four files do and how to wire them

Laying these down is one-time setup; how they behave at run time is lokf-librarian's operating manual ([`../../lokf-librarian/references/scheduled-task.md`](../../lokf-librarian/references/scheduled-task.md)). Applies only to a **git-tracked** `.lokf/` on **GitHub** - see SKILL.md Step 5 for why a gitignored bundle makes both workflows a permanent no-op.

## `knowledge-registrar.yaml` - the validation and provenance gate

Named for the registrar's job: keeping the bundle's records well-formed and provenanced, never judging whether their content is true (that's the curator's job, and this workflow runs no agent code at all). Runs `uv run lokf validate knowledge` on every pull request touching `.lokf/**` (or the workflow itself), weekly (Mondays 06:00 UTC), and on demand. Read-only (`contents: read`); superseded runs on the same ref are cancelled. Keep it green: the bar is that the projected graph describes the repository as it is today.

Its second job, `provenance`, runs on pull requests only and enforces the other half of the registrar's remit - that the paperwork is *provenanced*, not merely well-formed. A `human:<id>` verification claims a named person checked a concept against its source, but nothing in the format proves one: any writer that can edit the file can type the string, and `lokf validate` sees a perfectly valid event. So the job collects every `human:` actor the PR newly adds under `.lokf/knowledge/` (anchored on `by:`, so an id quoted in an `## Open questions` note doesn't count) and requires evidence from the forge for each: an **APPROVED** review from that account, or - when that person opened the PR, since GitHub won't let authors approve their own - a signature of *theirs* on the commit that introduced the event. Signature status is read from GitHub's API rather than `git log %G?`: a runner has neither a GPG keyring nor an allowed-signers file, so locally every signature reads as unverifiable no matter how good it is. The API also names the account each commit is attributed to, which is what ties a signature to a person rather than merely proving one exists. Needs `pull-requests: read` and `contents: read`; `fetch-depth: 0` because it diffs against the merge base.

This is what makes lokf-curator's confirmations mean anything to a later reader: without it, "confirmed by a person" is only as good as whatever wrote the file. The cost is intended: a curation PR now needs its curator's approval or signature before it can merge.

### When the confirming person opens the pull request: sign the commits

GitHub will not let anyone approve their own pull request, so when the person whose confirmations a pull request carries is also the person opening it, the signature is the route - and it is the better one anyway. A signature is cryptographic and still checkable years later; a review approval is a mutable record that a force-push can dismiss. One-time setup, reusing the SSH key already used to push:

```sh
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
```

Then add that same key again at `github.com/settings/keys`, this time as a **signing** key. That step is not optional, and skipping it is the usual reason the gate still fails after someone has started signing: GitHub keeps authentication and signing keys in separate lists, and this check reads GitHub's own verdict, so a key registered only for auth leaves every commit Unverified however correct the local setup is. The commit's email must also be a verified email on that account. Commits made through GitHub's web editor are signed by GitHub automatically and pass without any of this.

**Why the skills tell you to run these rather than running them for you.** `--global` would change how you commit in every unrelated repository on the machine, and a wrong `user.signingkey` makes `git commit` fail everywhere until you find it - too large a side effect for a knowledge sidecar to cause on its own. More to the point, a skill can only do the half that doesn't help: registering the key with GitHub is the step the gate actually reads, and doing the local half alone produces Unverified commits while leaving you believing it is set up.

**A committed `.gitconfig` cannot do it either**, if that occurs to you as a shortcut. Git reads `/etc/gitconfig`, `~/.gitconfig`, and `.git/config` - never a file in the working tree. It refuses this deliberately: a config file arriving with a clone could otherwise set `core.sshCommand` or an alias and run commands on checkout. A tracked `.gitconfig` is inert. Committing one and relying on it is a silent no-op.

### If you genuinely cannot sign: the `attestation` job

The third job is an opt-in escape hatch, and its shape is deliberate. It is **not** a setting that turns the check off. A permanent "provenance: off" switch gets flipped for one urgent afternoon and never flipped back, and from then on the bundle asserts confirmations nothing supports while the health line and these docs still promise otherwise - worse than never having built the gate. So instead of disabling anything, it asks for a fresh human action on each pull request that needs one: the run pauses, GitHub emails the environment's reviewers, and a person clicks Approve in a browser. Crucially, an environment reviewer **may** be the person who opened the pull request - environments do not carry the self-approval ban that pull-request reviews do - which is what makes this usable when the same person opens the pull request and attests. Each click is recorded in the deployment log, so it stays auditable afterwards.

Enabling it takes two steps, and the first is the one that does the work:

1. **Settings -> Environments -> New environment** (say `knowledge-curation`), tick **Required reviewers**, add the people allowed to attest, save.
2. **Settings -> Secrets and variables -> Actions -> Variables**: set `KNOWLEDGE_CURATION_ENVIRONMENT` to that environment's name.

Do not do the second without the first. An environment with no required reviewers approves itself the instant it is reached, so setting the variable while skipping the reviewers silently disables the gate entirely - the failure mode this design exists to avoid. With the variable unset (the default), the `attestation` job never runs and `provenance` simply fails on an unbacked confirmation.

What the attestation does and does not mean is worth saying plainly to whoever clicks: it records that a person with repository access vouched for the confirmation out of band. It is not evidence that anyone opened the concept's source. That distinction is why signing is the recommended path and this is the fallback.

### Marking the required checks

Mark `validate` and `provenance` as required in branch protection, and `attestation` too if you enable it. When a confirmation is backed, `attestation` is skipped rather than run; if your branch-protection configuration treats a skipped required check as blocking, that errs toward a stuck pull request rather than a silent bypass - annoying, but the safe direction.

Add one line to the repository's pull request template for whoever approves a curation pull request: *I opened the sources named by every confirmation I am approving.* An approval then records a task done, not only a click; the gate can prove who approved, never what they read.

One wrinkle if you do: the librarian's own PR (below) never fires this workflow's `pull_request` trigger in the first place - GitHub does not start `pull_request` workflows for a PR opened with the default `GITHUB_TOKEN`, which is how `knowledge-librarian.yaml`'s `publish` job opens it. `publish` carries its own version of both checks before it ever opens that PR (path allow-list, no `by: human:` claim), so nothing unsafe merges - but a required `validate`/`provenance` will sit at "Expected" on this particular PR until a human fires a fresh event for it (close/reopen, or an empty commit). See lokf-librarian's scheduled-task.md for the detail.

## `knowledge-librarian.yaml` - the scheduled refresh loop

Weekly (Mondays 05:00 UTC) and on demand. A read-only `refresh` job checks out full history, sets up `uv`, installs the sidecar, runs the reviewed agent wrapper, validates, and diffs `.lokf/knowledge/` only (so tool artifacts such as a fresh `uv.lock` never trigger a PR); if anything changed it packages the change - together with `.lokf/feedback.md`, the reader-feedback file lokf-docent writes and the librarian consumes - as a patch artifact. A separate privileged `publish` job (which runs no agent code) applies that patch on a clean checkout, commits it to a fresh `knowledge-librarian/<date>-<run_id>` branch, and opens a review PR via `github-script`. Guardrails: only the `publish` job holds `contents: write` + `pull-requests: write` (the agent runs in a `contents: read` job with no persisted credentials); never pushes to the default branch; never auto-merges; no PR when nothing
changed. It is **inert until wired**:

| Repository variable | Value |
| --- | --- |
| `KNOWLEDGE_LIBRARIAN_ENABLED` | `true` - arms the scheduled run; anything else (or unset) leaves the agent step skipped |
| `AGENT_CLI` | your non-interactive agent command, accepting a prompt via `-p` (use a repo *secret* instead if it embeds a token, and read `secrets.AGENT_CLI` in the workflow) |

With `KNOWLEDGE_LIBRARIAN_ENABLED` unset (or not `true`) the agent step is skipped, so the workflow is harmless until you wire it up. The workflow runs the reviewed `.lokf/scripts/knowledge-librarian.sh` directly rather than an arbitrary command string.

## `knowledge-librarian.sh` - the agent wrapper

Generic, no placeholders. Resolves the repo root from its own location, finds `lokf-librarian/SKILL.md` (`.claude/skills/`, `.github/skills/`, `.agents/skills/`, `skills/` - extend the `candidate` list if your repo differs, and run the script once to confirm), builds a prompt telling the agent to follow that skill, and calls `$AGENT_CLI -p`. Contract the workflow relies on: it only reads the repo and writes under `.lokf/knowledge/`; it never commits, pushes, or opens PRs; it exits 0 whether or not anything changed (the workflow diffs the tree to decide about a PR).

## `knowledge-conventions.sh` - what the gate checks that `lokf validate` cannot

Generic, no placeholders, no toolkit: bash, grep and awk over `knowledge/`. The `validate` job runs it after `lokf validate`, and lokf-librarian's audit runs it before handing off. It holds the bundle to five conventions the toolkit never sees because it reads a concept body as an opaque string and never opens `log.md`: one bare `## YYYY-MM-DD` heading per day in `log.md`, newest first (OKF §9, and how the LOKF Curator plugin finds today); every `at:` quoted; `verified` a list carrying at most one `process:lokf-librarian` event; each `## Open questions` bullet in the `- YYYY-MM-DD, <actor>: ...` shape the curator quotes; and every `resource:` that is not a URL naming a file or directory that still exists relative to the repository root, so a vanished source fails the gate rather than waiting for the librarian's next refresh (URLs are never fetched). Each rule has been broken by an agent that had it in prose, which is why it is a script. The same job also runs the justfile's `lokf-check-refs` through `uvx --from rust-just just`, so a typed relation pointing at no concept fails the gate too.

## Customising

Runner: `ubuntu-latest` is the only project-specific choice - swap in a self-hosted runner group and internal-CA env if your org needs them. Actions are pinned to commit SHAs with a version comment; bump them with your usual update tooling (Dependabot/Renovate handle SHA pins).
