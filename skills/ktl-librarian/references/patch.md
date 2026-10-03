# The patch file: how the librarian writes the bundle

The librarian never edits a file under `.lokf/knowledge/` by hand. It describes each change as an operation in `.lokf/patch.yaml`, checks the file with `bash .lokf/scripts/knowledge-apply.sh --dry-run`, and applies it with the same script. The script, not the agent, writes the files. It stamps `generated` from the clock, keeps a concept's `description` equal to its bullet in the folder's `index.md` and in the root `index.md`, and files each log line under the day's heading in `log.md`. It removes a feedback entry an operation says it handled, and it writes nothing unless every operation passes. In the scheduled run the wrapper applies the file after the agent has finished and refuses a run that changed anything else. The file is deleted once applied, and `.lokf/.gitignore` keeps it out of git.

## The file

```yaml
by: process:ktl-librarian        # optional; the actor every stamp carries, always process:<id>
ops:
  - op: create                   # a concept that does not exist yet
    path: services/orders-api.md # lowercase, under a folder, .md; the id is base_iri plus this path
    frontmatter:                 # type, title and description are required; never generated, verified, status, stale_after
      type: Service
      title: Orders API
      description: REST API serving order data to the CLI and web UI.
      resource: services/orders/openapi.yaml
      dependsOn:
        - https://acme.example/knowledge/datasets/orders-db
    body: |
      # Overview

      The **Orders API** generates its endpoints from `services/orders/openapi.yaml`...
    log: "**Added**: Orders API, from `services/orders/openapi.yaml`."   # optional on create

  - op: patch                    # minimal edits to a body, and frontmatter keys to set
    path: datasets/orders-db.md
    edits:
      - replace: { target: "nightly at 02:00", content: "nightly at 03:00" }   # target occurs exactly once
      - insert_after: { target: "## Columns", content: "" }                     # new lines after the one line holding the target
      - append: { content: "## Retention\n\nRows older than 13 months are dropped." }   # before ## Open questions, if any
    set:
      description: The orders table, loaded nightly at 03:00 from the Orders API.
    log: "**Changed**: the load moved to 03:00; `etl/orders.yaml` says so since 2026-08-01."
    from_feedback: "- **Disagreement** - `datasets/orders-db.md` says 02:00; `etl/orders.yaml` now says 03:00. - docent"

  - op: rewrite                  # a whole new body; the lokf:related block and ## Open questions carry over
    path: playbooks/release.md
    body: |
      # Overview
      ...
    log: "the release page was rewritten around the new workflow"

  - op: question                 # one open question in the curator's shape; sets status: draft
    path: policies/retention.md
    text: "the policy names 13 months and the ETL config names 12; which is current?"

  - op: recheck                  # this run's own verified event, replacing its previous one where it stood
    path: glossary/order.md

  - op: reindex                  # both index bullets re-derived from the frontmatter; the concept is not written
    path: policies/retention.md

  - op: delete                   # the file and its index bullets; refused when a person confirmed it
    path: services/legacy-sync.md
    log: "**Removal**: Legacy Sync; `services/legacy-sync/` was deleted in a1b2c3d."
```

The values are fictional, as in the skill page's example; mint ids from the bundle's real `base_iri`.

## What the script does for you

- **Provenance.** `create`, `patch` and `rewrite` stamp `generated: { by, at }` with this run's actor and the clock. Pass `revision: "<full commit hash>"` on an operation to record it where the toolkit accepts the key.
- **Status.** `create` sets `status: draft`; `question` sets it too. Nothing else touches `status`.
- **The index.** `create` adds the concept's bullet, its title linked to its file and followed by its description, to the folder's `index.md` and, under the matching `# Section` heading, to the root `index.md`; `set` of `title` or `description` rewrites both; `delete` removes both; `reindex` re-derives both from the frontmatter as it stands, touching neither the concept nor the log, for a bullet that drifted or a concept the script may not patch. A new folder gets a new section.
- **The log.** Every operation but `recheck` and `reindex` gives one bullet under today's `## YYYY-MM-DD` heading, newest day first, reusing the heading a run earlier today made. A `log` line that does not start with `**` gets the label `**Changed**` (or `**Rewrite**`). A `from_feedback` operation's bullet is labelled `**From reader feedback**`, so quote the reader's question in its `log` line.
- **Feedback.** `from_feedback` is the exact one-line entry as `.lokf/feedback.md` holds it. The script removes it, and a day left with no entry loses its heading.
- **Carry-overs.** `rewrite` keeps the `<!-- lokf:related -->` block and the `## Open questions` section from the old body when the new body lacks them. No edit may target text inside either.

## What it refuses

Any one of these refuses the whole file, and nothing is written:

- a line anywhere in the file that would read as a person's event (`by: human:...`) or a person's note (`- <date>, human:...`); prose may mention the actor prefix, but only ktl-curator writes one, in a live session;
- `by` that is not `process:<id>`;
- a path that is not lowercase a-z, 0-9 and hyphens under a folder, or that is `index.md`, `log.md` or `diataxis.md`;
- `create` on a path that exists, or any other operation on one that does not;
- `create` or `set` carrying `generated`, `verified`, `status`, `stale_after` or `timestamp`; `set` carrying `id` or `type`; an `id` that is not `base_iri` plus the path;
- `patch`, `rewrite`, `set` or `delete` on a concept whose `generated.by` starts with `human:` (a person wrote that text; add a `question` instead);
- `delete` on a concept with a `human:` event under `verified` (add a `question` saying the source is gone; the curator retires it);
- a `replace` target that occurs zero or several times, an `insert_after` target on zero or several lines, or either inside the `lokf:related` block or under `## Open questions`;
- a `patch`, `rewrite` or `delete` with no `log` line; a `title` with square brackets; a `from_feedback` line the feedback file does not hold.

## Exit codes

- `0`: applied, or with `--dry-run` would apply. The patch file is removed after an apply unless `--keep` is passed.
- `1`: findings, one per line, and nothing written. Fix the file and run again.
- `2`: no bundle, no patch file, a file that is not YAML, or no `uv` and no `pyyaml` for `python3`. The sidecar's prerequisites page says who installs `uv`.

Then run `just lokf-validate`, `just lokf-check-refs` and `bash scripts/knowledge-conventions.sh knowledge` as section 2 says. The script writes a touched concept's frontmatter back with double quotes where a value needs quoting and keeps the blank line after the closing `---` as it found it, so the diff shows the change and not the rewrite. The script keeps the conventions it knows; the schema and the relation targets are the toolkit's to check.
