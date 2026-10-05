# The patch file: how the librarian writes the bundle

The librarian never edits a file under `.lokf/knowledge/` by hand. It describes each change as an operation in `.lokf/patch.yaml`, checks the file with `bash .lokf/scripts/knowledge-apply.sh --dry-run`, and applies it with the same script. The script, not the agent, writes the files. It stamps `generated` from the clock, keeps a concept's `description` equal to its bullet in the folder's `index.md` and in the root `index.md`, and files each log line under the day's heading in `log.md`. It moves a feedback entry an operation says it handled into the ledger of questions readers asked, and it writes nothing unless every operation passes. In the scheduled run the wrapper applies the file after the agent has finished and refuses a run that changed anything else. The file is deleted once applied, and `.lokf/.gitignore` keeps it out of git.

## The file

`bash .lokf/scripts/knowledge-apply.sh --format` prints this block. A host learns the format from the script it has, whatever release of this skill it runs.

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
    from_feedback: "- **Miss** - Q: \"Which API serves orders?\" Answered from `services/orders/openapi.yaml`. Nothing relevant in index.md. - docent"   # the exact entry, which the script moves out of feedback.md; ten to a patch at most
    asked: "Which API serves orders?"   # the reader's question from that entry, for the ledger in .lokf/questions.md

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

  - op: resolve                  # withdraws one open question this run's actor asked, once the source settles it
    path: policies/retention.md
    target: "which is current?"  # text found in exactly one of that actor's questions; a person's note is the curator's to clear
    log: "**Resolved**: the policy and the ETL config both name 13 months since a1b2c3d."

  - op: recheck                  # this run's own verified event, replacing its previous one where it stood
    path: glossary/order.md

  - op: reindex                  # both index bullets re-derived from the frontmatter; the concept is not written
    path: policies/retention.md

  - op: delete                   # the file and its index bullets; refused when a person confirmed it or left a note on it, or an index names it in a sentence
    path: services/legacy-sync.md
    log: "**Removal**: Legacy Sync; `services/legacy-sync/` was deleted in a1b2c3d."

handoff:                         # optional; at most ten lines of 300 characters for the reviewer, in your own words and never a reader's; written nowhere in the bundle
  - "datasets/orders-db.md and playbooks/release.md came back for the same misread date; the skill's rule on dates needs a look."
  - "https://acme.example/spec did not answer, so references/acme-spec.md was not rechecked."
```

The values are fictional, as in the skill page's example; build ids from the bundle's real `base_iri`.

## What the script does for you

- **Provenance.** `create`, `patch` and `rewrite` stamp `generated: { by, at }` with this run's actor and the clock. Pass `revision: "<full commit hash>"` on an operation to record it where the toolkit accepts the key.
- **Status.** `create` sets `status: draft`; `question` sets it too. Nothing else touches `status`.
- **The index.** `create` adds the concept's bullet, its title linked to its file and followed by its description, to the folder's `index.md` and to the root `index.md`. `set` of `title` or `description` rewrites both, and `delete` removes both. `reindex` re-derives both from the frontmatter as it stands, for a bullet that drifted or a concept the script may not patch, and touches neither the concept nor the log.

  In the root, a bullet goes under the heading named after its folder, at any level, or else in a section below the title that links the folder's `index.md`. A new folder gets a new section, at the level the root's other sections use. A concept's bullet is a line that holds its link alone, optionally followed by its description, and the script rewrites every such line. An index that lists the concept another way, among other links on one line or in a sentence, keeps that line: `create`, `set` and `reindex` leave it alone, and `delete` takes the link out of a comma-separated list of links. A link inside another concept's bullet does not count as a listing.
- **The log.** Every operation but `recheck` and `reindex` gives one bullet under today's `## YYYY-MM-DD` heading, newest day first, reusing the heading a run earlier today made. A `log` line that does not start with `**` gets the label `**Changed**` (or `**Rewrite**`, or `**Resolved**`). A `from_feedback` operation's bullet is labelled `**From reader feedback**`. Say there what changed and why, in your own words, and never copy the reader's.
- **Feedback and the ledger.** `from_feedback` is the exact one-line entry as `.lokf/feedback.md` holds it. The script removes it there, and a day left with no entry loses its heading. It then adds one line to `.lokf/questions.md`: the day, the entry's kind and the concept the operation names, with the reader's question from `asked` where the entry held one. That file only grows, and programs read it: `knowledge-report.sh` counts the concepts readers keep asking about, and scores whether the index leads to them.
- **Open questions.** `question` adds one in the curator's shape. `resolve` withdraws one this run's actor asked, once the source settles it, and the heading goes with its last question. Neither stamps `generated`, since an open question is no part of what the concept claims. `resolve` leaves `status` as it finds it, because confirming the concept is the curator's.
- **Carry-overs.** `rewrite` keeps the `<!-- lokf:related -->` block and the `## Open questions` section from the old body when the new body lacks them. No edit may target text inside either. So leave `## Open questions` out of a `rewrite` body: a body that brings its own replaces the section, and the script refuses that when a person's note would go with it.
- **Confirmed concepts it edits.** After an apply, or a dry run, the script names each concept a person confirmed that the patch edits. Each reads as *edited since a person last confirmed it* until the curator looks again, so name them in the hand-off.
- **Lines for the reviewer.** `handoff` carries what a reviewer should know that is no change to the bundle: the same send-back twice, a source that did not answer, entries left for the next run. The script prints the lines and writes none of them to the bundle. Each becomes one line of printable text, with any backtick turned into `'`. In a scheduled run the wrapper passes them to the pull request, which shows them as the librarian's own words in a code block. Write them yourself, and never quote a reader.

## What it refuses

Any one of these refuses the whole file, and nothing is written:

- a line anywhere in the file that would read as a person's event (`by: human:...`) or a person's note (`- <date>, human:...`); prose may mention the actor prefix, but only ktl-curator writes one, in a live session;
- a patch after which any concept it writes would hold a person's record other than the one the file held: a `human:` event or a person's note added, changed or removed, however the operations spelt it;
- `by` that is not `process:<id>`;
- a path that is not lowercase a-z, 0-9 and hyphens under a folder, or that is `index.md`, `log.md` or `diataxis.md`;
- `create` on a path that exists, or any other operation on one that does not;
- `create` or `set` carrying `generated`, `verified`, `status`, `stale_after` or `timestamp`; `set` carrying `id` or `type`; an `id` that is not `base_iri` plus the path;
- `patch`, `rewrite`, `set` or `delete` on a concept whose `generated.by` starts with `human:` (a person wrote that text; add a `question` instead);
- `delete` on a concept with a `human:` event under `verified`, or with a person's note under `## Open questions` (add a `question` saying the source is gone; the curator retires it);
- `delete` on a concept that an `index.md` links in a sentence, or anywhere but in its own bullet or a comma-separated list of links (a person takes that link out, and the delete can then run);
- a `replace` target that occurs zero or several times, an `insert_after` target on zero or several lines, or either inside the `lokf:related` block or under `## Open questions`;
- a `resolve` target found in no open question or in several, or found in one another actor asked: a person's note is the curator's to clear, on that person's word;
- a `patch`, `rewrite`, `delete` or `resolve` with no `log` line; a `title` with square brackets;
- a `from_feedback` line the feedback file does not hold, or more than ten of them in one file; `asked` on an operation with no `from_feedback`, or with no printable text;
- a `handoff` that is not a list, or holds more than ten lines, or a line that is empty or longer than 300 characters once the characters no reader sees are gone. Those are the controls and the format characters, such as a zero-width space, a bidirectional mark or a tag character, and the script takes them out of a reader's question too.

## Exit codes

- `0`: applied, or with `--dry-run` would apply, or `--format` printed the block above. The patch file is removed after an apply unless `--keep` is passed.
- `1`: findings, one per line, and nothing written. Fix the file and run again.
- `2`: no bundle, no patch file, a file that is not YAML, a `--handoff` file that cannot be written, or no `uv` and no `pyyaml` for `python3`. The sidecar's prerequisites page says who installs `uv`.

Then run `just lokf-validate`, `just lokf-check-refs` and `bash scripts/knowledge-conventions.sh knowledge` as section 2 says. The script writes a touched concept's frontmatter back with double quotes where a value needs quoting and keeps the blank line after the closing `---` as it found it, so the diff shows the change and not the rewrite. A value YAML would read as a number, a boolean or a time goes back as the text the file held: `1.10` stays `1.10`, and an unquoted time on a person's event stays as that person's commit wrote it. The script keeps the conventions it knows; the schema and the relation targets are the toolkit's to check.
