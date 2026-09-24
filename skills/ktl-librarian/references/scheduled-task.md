# Scheduled librarian task (Karpathy rule): operating manual

**Everything here assumes `.lokf/` is git-tracked** (ktl-sidecar's Step 0). If it is gitignored, do not scaffold or rely on any of this. `knowledge-registrar.yaml` never triggers, since nothing under `.lokf/**` is ever part of a pull request diff. `knowledge-librarian.yaml`'s change-detection step (`git status --porcelain -- .lokf/knowledge`, in the workflow) silently reports no changes for an ignored path. That is not a failure you would notice, just a scheduled job that quietly does nothing, forever. Get periodic freshness in that mode from a scheduler that is not gated on git history instead: cron, a systemd timer, or re-running this skill by hand.

Keep the graph continuously accurate rather than rewriting it in bursts. Three pieces automate this rebuild loop. The **ktl-sidecar** skill's Step 5 scaffolds them from `../../ktl-sidecar/templates/` (`github/*.yaml`, `scripts/knowledge-librarian.sh`), and its [automation.md](../../ktl-sidecar/references/automation.md) and [gate.md](../../ktl-sidecar/references/gate.md) say what each file does and how to wire it. This file is their operating manual: what a run does, and what this skill must keep true for it.

## `knowledge-librarian.yaml`: the rebuild workflow

It runs weekly (Mondays, 05:00 UTC) and on demand (`workflow_dispatch`). Each run has two jobs:

1. A read-only `refresh` job checks out the full history, sets up `uv`, installs the `lokf` sidecar, runs the agent, validates, and diffs `.lokf/knowledge/`. Only the bundle is diffed, so tool artifacts never trigger a pull request. If anything changed, it packages the change as a patch artifact: `.lokf/knowledge/` plus `.lokf/feedback.md`, ktl-docent's reader-feedback file, so entries the librarian consumed do not return.
2. A separate privileged `publish` job applies the patch on a clean checkout, commits it to a fresh `knowledge-librarian/<date>-<run_id>` branch, and opens a review pull request via `github-script`.

The guardrails: the agent runs in a `contents: read` job with no persisted credentials, and only the `publish` job, which runs no agent code, holds `contents: write` and `pull-requests: write`. The workflow never pushes to the default branch, never auto-merges, and opens no pull request when nothing changed.

Two things this skill must keep true for it:

- A no-change run must leave the bundle byte-for-byte untouched, `log.md` included (section 1's log policy).
- The pull request body ends with a **For the curator** section: counts of drafts, open questions and person-confirmed concepts. The workflow computes them from frontmatter with `grep` rather than taking them from the agent's output, and points the reviewer at the **ktl-curator** skill. It is a nudge; the curator's own report is the authoritative view.

## `knowledge-librarian.sh`: the agent wrapper

The workflow invokes `.lokf/scripts/knowledge-librarian.sh` directly, a fixed, reviewed path. To arm it:

1. Set the `KNOWLEDGE_LIBRARIAN_ENABLED` repository variable to `true`.
2. Set `AGENT_CLI` to your non-interactive agent command.
3. Name the variable the agent reads its credential from in `AGENT_API_KEY_ENV`.
4. Either set `AGENT_USE_JOB_TOKEN` to `true` (Copilot CLI, billed to the repository owner's seat) or put a key in the `AGENT_API_KEY` secret. The wrapper hands it to the agent under that name only.

The sidecar's automation.md gives the full settings for Copilot CLI and Claude Code. If `KNOWLEDGE_LIBRARIAN_ENABLED` is not `true`, the workflow's agent step is skipped, so the workflow is harmless until you wire the agent up.

The script selects the ktl-librarian skill, builds a prompt telling the agent to follow it and re-scrape the repository, then calls `AGENT_CLI`. Its contract: it edits **only** files under `.lokf/knowledge/` and performs no git or pull request operations. The workflow owns the branch, the commit and the pull request.

## `knowledge-registrar.yaml`: the gate

The registrar keeps records well-formed and provenanced. It never judges whether their content is true, a different job from this skill's own.

Its `pull_request` trigger does **not** fire on the librarian's own pull request. GitHub does not start `pull_request`-triggered workflows for a pull request opened with the default `GITHUB_TOKEN`, which is how `publish` opens it. That is a deliberate anti-recursion rule, not a bug here. So `publish` carries the two checks that matter for this pull request itself, before it ever opens it:

- Every changed path falls inside the bundle. `publish` re-derives this from the patch's own `git apply --numstat` output against an allow-list, since the `refresh` job's own boundary check shared a workspace with the agent and so cannot be trusted alone.
- The patch adds no `by: human:` claim. This skill never writes one.

To get the registrar's own `validate` and `provenance` checks to run and show green on the librarian pull request, useful if your branch protection requires them, close and reopen the pull request, or push an empty commit to its branch. Either is a human action and fires a fresh `pull_request` event. A curation pull request from ktl-curator, opened normally by a person, triggers the gate immediately with no extra step; that is what `provenance` exists for.

The bar is that the projected RDF graph always describes the repository as it is *today*.
