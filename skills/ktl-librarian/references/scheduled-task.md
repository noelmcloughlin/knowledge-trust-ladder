# Scheduled librarian task (Karpathy rule): operating manual

**Everything here assumes `.lokf/` is git-tracked** (ktl-sidecar's Step 0). If it is gitignored, do not scaffold or rely on any of this. `knowledge-registrar.yaml` never triggers, since nothing under `.lokf/**` is ever part of a pull request diff. `knowledge-librarian.yaml`'s change-detection step (`git status --porcelain -- .lokf/knowledge`, in the workflow) silently reports no changes for an ignored path. That is not a failure you would notice, just a scheduled job that quietly does nothing, forever. Get periodic freshness in that mode from a scheduler that is not gated on git history instead: cron, a systemd timer, or re-running this skill by hand.

Keep the graph continuously accurate rather than rewriting it in bursts. Three pieces automate this rebuild loop. The **ktl-sidecar** skill's Step 5 scaffolds them from `../../ktl-sidecar/templates/` (`github/*.yaml`, `scripts/knowledge-librarian.sh`), and its [automation.md](../../ktl-sidecar/references/automation.md) and [gate.md](../../ktl-sidecar/references/gate.md) say what each file does and how to wire it. This file is their operating manual: what a run does, and what this skill must keep true for it.

## `knowledge-librarian.yaml`: the rebuild workflow

It runs weekly (Mondays, 05:00 UTC) and on demand (`workflow_dispatch`). A scheduled week with nothing waiting for this skill runs no agent: `knowledge-report.sh quiet` decides, before the agent is called, from the same facts as the work list. A scheduled run in a month's first seven days goes ahead regardless, so that sources given as a URL and files the source map leaves out are read at least monthly. A run a person starts always goes ahead. Each run that goes ahead has two jobs:

1. A read-only `refresh` job checks out the full history, sets up `uv`, and installs the `lokf` sidecar. It installs this skill from the tag `TRUST_LADDER_SKILLS_REF` pins into `.agents/skills/`; that step is skipped in the repository that publishes the skills, where the wrapper finds them under bare `skills/`. Then it sets up Node for the agent, runs the agent, applies the `.lokf/patch.yaml` it wrote with `knowledge-apply.sh`, fails if the agent changed anything else, validates, and diffs `.lokf/knowledge/`. Only the bundle is diffed, so tool artifacts never trigger a pull request. If anything changed, it packages the change as a patch artifact: `.lokf/knowledge/` plus `.lokf/feedback.md`, ktl-docent's reader-feedback file, and `.lokf/questions.md`, the ledger a handled entry moves into, so entries the librarian consumed do not return. The hand-off the pen took from the patch file travels beside it.
2. A separate privileged `publish` job applies the patch on a clean checkout and checks the result before it commits. It then commits to a fresh `knowledge-librarian/<date>-<run_id>` branch and opens a review pull request via `github-script`.

The guardrails: the agent runs in a `contents: read` job with no persisted credentials, and only the `publish` job, which runs no agent code, holds `contents: write` and `pull-requests: write`. The workflow never pushes to the default branch, never auto-merges, and opens no pull request when nothing changed.

Three things this skill must keep true for it:

- A no-change run must leave the bundle byte-for-byte untouched, `log.md` included (section 1's log policy).
- What a reviewer must know about the bundle goes in the bundle, as a `log` line or an open question. What a reviewer must know that is no change to the bundle goes in the patch file's `handoff`, in your own words and never a reader's. That is the same send-back twice, a source that did not answer, or entries left for the next run. The rest of the pull request body is the workflow's: the `publish` job computes the bundle's health line and what the change does to the record with `knowledge-report.sh`, on its own checkout. It shows the hand-off under *From the librarian*, in a code block, as your words and nothing more. Your final reply is read in the job's log and nowhere else.
- A note a person left that you have read leaves your stamp on its concept: a `patch` or `rewrite` when the source changes what the concept says, or a `recheck` when the source bears the concept out. Add a `question` beside either when the note needs the person again; a `question` alone moves no stamp. The quiet check counts a note as waiting for you until a stamp of yours comes after it, so a note you read and left unmarked keeps every later week busy.

## `knowledge-librarian.sh`: the agent wrapper

The workflow invokes `.lokf/scripts/knowledge-librarian.sh` directly, a fixed, reviewed path. To arm it:

1. Set the `KNOWLEDGE_LIBRARIAN_ENABLED` repository variable to `true`.
2. Set `AGENT_CLI` to your non-interactive agent command.
3. Name the variable the agent reads its credential from in `AGENT_API_KEY_ENV`.
4. Either set `AGENT_USE_JOB_TOKEN` to `true` (Copilot CLI, billed to the repository owner's seat) or put a key in the `AGENT_API_KEY` secret. The wrapper hands it to the agent under that name only.
5. Optionally set `KNOWLEDGE_RETRIEVAL` to `true`. Each run that changes the bundle then makes one more agent call, which scores whether the index leads to the concept behind each question readers asked, and the pull request carries the score.

The sidecar's automation.md gives the full settings for Copilot CLI and Claude Code. If `KNOWLEDGE_LIBRARIAN_ENABLED` is not `true`, the workflow's agent step is skipped, so the workflow is harmless until you wire the agent up.

The script selects the ktl-librarian skill, builds a prompt telling the agent to follow it and re-scrape the repository, then calls `AGENT_CLI`. On a scheduled run it first asks `knowledge-report.sh quiet`, and calls no agent when nothing waits. The prompt takes the patch file's format from `knowledge-apply.sh --format`, so it holds for whichever release of this skill the pin installs. Its contract: the agent writes one file, `.lokf/patch.yaml`, and the wrapper applies it with `knowledge-apply.sh` once the agent has finished. The pen writes the file's hand-off to the path the workflow names, after the wrapper has removed whatever the agent left there. The wrapper refuses a run that changed anything else, and one whose result touches a person's record. So `.lokf/knowledge/` changes only through that script, and the wrapper performs no git or pull request operations. The workflow owns the branch, the commit and the pull request.

## `knowledge-registrar.yaml`: the gate

The registrar keeps records well-formed and provenanced. It never judges whether their content is true, a different job from this skill's own.

Its `pull_request` trigger does **not** fire on the librarian's own pull request. GitHub does not start `pull_request`-triggered workflows for a pull request opened with the default `GITHUB_TOKEN`, which is how `publish` opens it. That is a deliberate anti-recursion rule, not a bug here. So `publish` carries the two checks that matter for this pull request itself, before it ever opens it:

- Every changed path falls inside the bundle, the feedback file or the ledger. `publish` re-derives this from the patch's own `git apply --numstat` output against an allow-list, since the `refresh` job's own boundary check shared a workspace with the agent and so cannot be trusted alone.
- The patch touches no person's record. `knowledge-provenance.sh --unattended` reads that off the patched tree: no `human:` event added, changed or removed in any YAML layout, no person's note added or removed, and no text a person wrote changed. This skill never does any of those, and the pen refuses each before it writes.

To get the registrar's own `validate` and `provenance` checks to run and show green on the librarian pull request, useful if your branch protection requires them, close and reopen the pull request, or push an empty commit to its branch. Either is a human action and fires a fresh `pull_request` event. A curation pull request from ktl-curator, opened normally by a person, triggers the gate immediately with no extra step; that is what `provenance` exists for.

The bar is that the projected RDF graph always describes the repository as it is *today*.
