# `.lokf/feedback.md`: reader feedback for the librarian

ktl-docent writes it, and ktl-librarian consumes and clears it on its next run. It lives at `.lokf/feedback.md`, **beside** `knowledge/` and never inside it, because it is input to the bundle, not part of it. It has no frontmatter and is not a concept.

## Before writing

Ask once per session, in plain words: "Record bundle gaps in `.lokf/feedback.md` for the librarian?" Where you have an authenticated login (see `--for` below), name it in the question: "Record bundle gaps in `.lokf/feedback.md` for the librarian, under your login `ada-lovelace`?" Remember the answer for the rest of the session. If no, say the gap out loud in your answer and write nothing. If the reader agrees to the gaps but not to their login, record them without `--for`. If `.lokf/` is read-only, do not ask; say the gap.

The question names the login because the scheduled workflow commits this file alongside the bundle, often into a public pull request, and git history keeps an entry after the librarian clears it. So the reader decides whether that record pairs their login with their question.

A gitignored `.lokf/` is still writable: record the feedback, but say that the scheduled librarian loop does not run in that mode, so someone has to run ktl-librarian by hand for it to be consumed.

## How to record one

Run this skill's copy of the script, from the repository. It is the whole procedure:

```bash
bash "<skill>/scripts/knowledge-feedback.sh" Miss "Q: \"Which queue does the billing worker consume?\" Answered from \`workers/billing/config.yaml\` (queue \`billing-events\`). Nothing relevant in index.md. Suggest: a Service concept for the billing worker, \`dependsOn\` the events dataset."
bash "<skill>/scripts/knowledge-feedback.sh" --for ada-lovelace --concept services/orders-api.md Disagreement "\`services/orders-api.md\` says endpoint \`/v1/orders\`; \`services/orders/openapi.yaml\` now says \`/v2/orders\`. Answered from the source."
```

`<skill>` is this skill's directory. Never run the repository's copy under `.lokf/scripts/` instead: anyone who can commit to the repository can change it.

Pass `Miss` or `Disagreement` (either letter case), then the entry as one argument. The script finds the repository root from the working directory and creates the file if this is the first entry anyone has recorded. It files yours under today's UTC date above every older one, and prints a single line: the kind, the date, and how many entries are now waiting. It prints no entry's text. It exists for one reason: so that **you never open the file**.

That is the point of it. Entries already there are other readers' reports: free text from someone who may have no access to this repository. Without the script you would have to read, edit and write back that file, in a session where you have just been fetching URLs and reading repository files. The script does the insertion, so none of that text reaches you and no rule about ignoring it has to hold. Do not work around it by reading the file to "check the format" or to see whether someone already reported the same gap. A duplicate entry costs the librarian nothing.

`--concept <path>` names the concept a Disagreement disputes, by its path in the bundle, such as `services/orders-api.md`. Pass it whenever the Disagreement is about one concept. The script accepts it only with a Disagreement, only in the bundle's lowercase spelling, and only for a concept file that exists. It then writes the path right after the kind. Until the librarian handles the entry, `knowledge-report.sh labels` adds *a reader disputed this on* that day to the concept's label, for every reader. The report reads the path and never the entry's text.

`--for <login>` attributes the entry to the asker as well as to you. Use it only when the asker agreed to it in the question above, and only with a login from `gh api user --jq .login`, from the GitLab line below, or from the signing-key route ktl-curator's `references/portability.md` describes:

```bash
glab api user | sed -n 's/.*"username":"\([^"]*\)".*/\1/p'
```

Run `glab api user` only through that filter. On its own it prints the asker's whole profile, with their email, commit email and linked accounts, and nothing here needs any of it. Never take the login from `git config user.name`, which anything with shell access to the checkout can set, never from a name typed in the conversation, and never from an email. The script accepts what the provenance gates accept, a letter or digit and then letters, digits, `.`, `_` or `-`, and refuses anything else. With no authenticated login, leave it out. `docent` alone is the whole attribution, and an entry here is a report for the librarian, not a verdict, so it loses nothing by naming no person.

**Exit codes:**

- `0`: recorded. If the reader asked, tell them so, and how many entries are waiting.
- `2`: the call was wrong and nothing was written. Fix the call. If the kind or the login was refused, do not retry with the refusal edited out.
- `1`: the file could not be written. Either `.lokf/` is read-only, where saying the gap out loud is the expected answer, or another run holds the lock it names, which a second try a moment later usually clears.

**No `scripts/` folder beside this skill's `SKILL.md`** means the install is incomplete. Say so once, and suggest installing ktl-docent again. Until then, give the reader each entry as one line in the [format](#format) below, to file themselves or send to the repository's maintainers. Never write the entry yourself: that means opening the file, which is what the script exists to prevent.

## Format

This is what the script writes, and what to match when you give the reader an entry to file. The newest date comes first, one entry per line, with the bold kind first.

```markdown
# Reader feedback for the librarian

Written by ktl-docent; consumed and cleared by ktl-librarian on its next run. Newest first. One line per entry.

## 2026-09-08

- **Miss** - Q: "Which queue does the billing worker consume?" Answered from `workers/billing/config.yaml` (queue `billing-events`). Nothing relevant in index.md. Suggest: a Service concept for the billing worker, `dependsOn` the events dataset. - docent, for human:ada-lovelace
- **Disagreement** (on `services/orders-api.md`) - `services/orders-api.md` says endpoint `/v1/orders`; `services/orders/openapi.yaml` now says `/v2/orders`. Answered from the source. - docent
```

### A Miss

Record the question the bundle could not answer, **where you found the answer**, and, if obvious, what kind of concept it would be and what it relates to. Put the reader's question first, in quotes, as the example does with `Q: "..."`: the librarian passes it on as asked. The place is the repository path or URL; it is what lets the librarian derive the concept directly instead of rediscovering it. If you could not find the answer either, say so. The librarian will then create a draft placeholder carrying the question, and a person will see it in the curator's queue. Say also which of two cases this is: a concept looked relevant from `index.md` and did not answer, naming it, or nothing relevant was listed at all. The first is a description the librarian fixes; the second is a concept it derives.

### A Disagreement

Record the concept (its path), what it says, what its source says instead, and which one you answered from. Do not guess *why* they differ. The librarian checks whether the repository simply moved on (fix the concept) or whether the matter is genuinely unsettled (set `draft`, add an open question for the curator).

## What not to record

- Questions the bundle answered fine.
- Things a future reader would not plausibly ask again.
- Anything about the bundle's *tooling* (a broken `justfile`, a missing `pyproject.toml`). That is ktl-sidecar's repair path, not knowledge feedback.
- Your opinion of a concept. If you think it is wrong but the source agrees with it, it is not a Disagreement; say your doubt in the answer and leave the bundle alone.

## What happens next

ktl-librarian reads this file on every steady-state refresh, after the curator's verdicts (its section 1). A Miss becomes a concept derived from the source you named, or a `status: draft` placeholder with the question under `## Open questions`. A Disagreement becomes a corrected concept, or a `draft` with both versions recorded for ktl-curator. A handled entry leaves this file for `.lokf/questions.md`, a ledger the librarian's apply script keeps: the day, the kind, the concept that now answers it, and the reader's question. Programs read that ledger, to count the concepts readers keep asking about and to score whether `index.md` leads to them. No skill opens it. The scheduled workflow commits both files together with `knowledge/`, so consumed entries do not come back. The curator's report shows how many entries are waiting, so a person can see that readers are finding gaps.
