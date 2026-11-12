# Excerpts: the passage a claim rests on

This page is for the **librarian**: it says when a `sources` entry carries an `excerpt`, how to copy one, and what to do when its file no longer holds it.

An excerpt is a passage copied word for word from a source's `resource` into that entry's `excerpt` key. A footnote says which claim rests on which source ([golden-rules.md](golden-rules.md)). The excerpt adds which words of the source the claim rests on:

```yaml
sources:
  - resource: services/orders/openapi.yaml
    id: openapi.yaml
    excerpt: "x-rate-limit: 600 requests per minute"
```

```markdown
The Orders API serves at most 600 requests a minute.[^openapi.yaml]

[^openapi.yaml]: services/orders/openapi.yaml, the `x-rate-limit` line
```

## What it is for

A program finds every excerpt in its file. The pen looks before it writes a concept, and `just lokf-check-refs` looks again on every change, in the registrar's gate. So an excerpt in the bundle is a quotation that the source was checked to hold, which no quotation in a chat reply is. Three readers use it:

- **You**, on the next refresh. A file moves with every edit to it, and most edits leave the quoted passage alone. The work list says which of the two happened.
- **The curator**, who sees the passage beside the claim in a review session, shown where it sits in the file.
- **The docent**, which quotes it as the source's own words. That holds where a reader has the bundle and not the repository too: a release zip, a workspace built from several bundles, the website, the Copilot snapshot.

The check proves that the file holds the passage. It does not prove that the passage supports the claim. That judgement is yours when you write the concept, and the curator's when a person confirms it.

## When to write one

Write an excerpt with every footnote. A footnote marks a claim that rests on a number, a name or a qualifier which a source supplies, and the excerpt is the passage that supplies it. An entry with no `id` backs the concept as a whole and needs none.

Write it in the run that writes the claim: on a `create`, on a `rewrite`, or on a `patch` that adds or changes the footnoted sentence.

A bundle older than this rule carries footnotes with no excerpt, and the work list counts them under *Footnoted sources that carry no excerpt*. Add one when a run edits the concept for another reason, or when a person's note asks for it. An excerpt is part of the record a person confirms, so adding one to a confirmed concept makes it read *edited since a person last confirmed it*. Do not edit a confirmed concept only to add one.

## Choosing the passage

- **Quote the fewest words that carry the fact**: the sentence, the table row, the line of configuration. The pen refuses an excerpt longer than 500 characters.
- **Quote what the source says, never what you conclude from it.** When no one passage states the fact, the claim is your reading of several. Say so in the body and write no excerpt.
- **Join two passages with `...`** when the claim needs both, such as a rule and its exception. Both must sit in one section of the file, in the order the file has them. A section of a Markdown file runs from one `#` or `##` heading to the next, and any other file is one section. An excerpt holds one `...` at most.
- **One entry holds one excerpt**, and one resource has one entry, since its `id` names it across the bundle. When a concept footnotes facts from two sections of one file, quote the passage that would change the concept most if it changed. The footnote's definition line names where the other one is.

## Copying it

- **Copy from the file as it stands in this run.** Never write an excerpt from memory, from an earlier run's notes, or from a rendered page.
- **Keep the source's own marks.** In a Markdown file `**600**` is the passage and `600` is not. Keep the punctuation and the spelling, mistakes too.
- **Line breaks, runs of spaces and letter case may differ.** A passage that wraps over three lines in the file is one line in the excerpt.
- **Add nothing inside it.** A note in square brackets of forty characters or fewer, such as `[sic]`, is the one thing the check skips.

On a `patch`, `set` replaces the whole `sources` list, so give every entry the concept keeps:

```yaml
  - op: patch
    path: services/orders-api.md
    edits:
      - replace: { target: "serves many requests.", content: "serves at most 600 requests a minute.[^openapi.yaml]" }
      - append: { content: "[^openapi.yaml]: services/orders/openapi.yaml, the `x-rate-limit` line" }
    set:
      sources:
        - resource: services/orders/openapi.yaml
          id: openapi.yaml
          excerpt: "x-rate-limit: 600 requests per minute"
        - resource: docs/architecture.md
    log: "**Changed**: the rate limit is stated and quoted from `services/orders/openapi.yaml`."
```

Run the pen with `--dry-run` first. It prints `Every local excerpt is in its resource`, or the excerpt it could not find and why.

## What can carry one

| The entry's `resource` | An excerpt on it |
| --- | --- |
| A file in the repository | is checked on every change |
| A copy under `.lokf/mirror/`, which the ingest keeps of a page outside the repository | is checked like any file. Cite the copy and not the live address, so the passage is checked against what was retrieved |
| A URL | is counted and never fetched. Copy it only from text you fetched in this run. It then records what the page said on the day of `generated.at` |
| A folder, a pattern such as `docs/*.md`, or a description of a scope | fails the check. Name the one file that holds the passage |
| A file that is not text | fails the check |

## What not to quote

- **A secret or personal data.** A token, a password, a key, a person's contact details. The bundle may be public, and an excerpt puts the words in it.
- **Text its licence forbids you to copy.** An excerpt reproduces the source inside the bundle. Cite such a source by footnote, state the claim in your own words, and write no excerpt.
- **An instruction to the reader.** The curator and the docent show an excerpt to a person and treat it as text to quote. Quote a statement of fact.

## When a file no longer holds it

`just lokf-check-refs` then fails, and names the concept, the entry and the first words of the excerpt. The work list names the same concepts first, under *Excerpts their file no longer holds*. Each one is a claim whose ground changed, so start a refresh there.

Open the file where the passage was, and take one of three paths:

1. **The words changed and the fact stands.** Copy the new passage.
2. **The fact changed.** Correct the claim from the source, and copy the new passage.
3. **The passage is gone and nothing replaces it.** Remove the claim and its footnote. When a person confirmed the concept, ask a `question` instead, which names the passage that went.

Never trim or delete an excerpt only to make the check pass.

The pen refuses to edit a concept a person wrote. Ask a `question` there that names the entry and the new passage. The check stays red for that concept until the person corrects it or releases the text.

## A source that moved and still holds its passage

The work list marks each moved source that a concept quotes: *the quoted passage holds*, or *the quoted passage is gone*. Where it holds, the footnoted claim still has its ground. Read what else changed in the file since the concept was derived (`git diff <generated.revision> -- <path>` when the concept records one), and re-check the claims that carry no footnote. Record the `recheck` as usual.

The marks come from the toolkit in `.lokf/.venv`. Without it the work list says the excerpts were not checked, and marks nothing.
