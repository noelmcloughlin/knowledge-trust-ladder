# Other files: a Markdown file outside the bundle

This page is for the case a person forces: they name a Markdown file outside `.lokf/knowledge/` and ask **ktl-prose** to reword it. The rules are the same as in the bundle. What differs is what the file is to the bundle, and what you may not touch.

## Only a file the person names

Work outside the bundle only on a file the person names in a turn addressed to you. Never widen the request: "the README" is one file, not the docs beside it. The rule about a live session in SKILL.md's Step 2 holds here unchanged.

## What you never touch

- **A record of the past**: the released sections of a changelog, a log, a captured transcript. Rewording it changes what was said.
- **Text taken from elsewhere**: a licence, a code of conduct, a quoted specification.
- **An installed copy**: anything under `.agents/` or `.claude/`. Reword the source it was installed from.
- **A file ktl-sidecar laid down**: everything under `.lokf/` outside `knowledge/`, and the three `knowledge-*.yaml` workflows. Each is a copy of a template, and an edited copy is what the sidecar's next repair replaces.

## Before you reword a source

A file outside the bundle is often a source: a concept names it as its `resource`, or lists it under `sources`. Find those concepts first:

```sh
grep -rnF 'resource: <path>' .lokf/knowledge
```

A rewording changes no fact in the source, and it still costs those concepts something. Tell the person what, before you start:

- **The file's revision moves.** From lokf 0.9.0 an event may carry the `revision` of the source it rested on. Each such event now names a state the file has left, so a person must open the source again to learn that nothing changed.
- **An excerpt may no longer be found.** From lokf 0.9.0 a source may carry an `excerpt`: a passage copied from the file word for word. Reword that passage and the copy matches nothing.
- **The librarian checks again.** Its next run finds the source changed and goes through each concept derived from it.

Say how many concepts rest on the file, and how many of those a person confirmed. Then wait for a yes. Afterwards name **ktl-librarian** as the next step, so those concepts are checked against the reworded source.

## Proving the change

```sh
python3 <skill>/scripts/prose-check.py --against HEAD <files>     # a file git already held
python3 <skill>/scripts/prose-check.py --before <copy> <file>     # a file you copied first
```

Fix each finding, or explain it in the hand-off. Outside the bundle a person may ask for a change of content in the same request, and the script cannot know that. A changed heading is only a note here, and other pages may link to it. Search for its anchor before you keep the change.

Hand off the files the person named and no others. Give the counts before and after, each sentence you left alone, and what no script proved: that the meaning held.

## Comments in scripts and workflows

The script reads Markdown. A comment gets the same rules by hand.

Never touch either of these:

- a directive: `#!`, `# shellcheck`, a `# ///` block, or the version comment after a pinned `uses:`;
- a `#` line inside a heredoc, which is data.

Then show that only comments changed:

```sh
git diff -U0 -- <file> | grep -E '^[+-]' | grep -vE '^(\+\+\+|---) ' | grep -vE '^[+-][[:space:]]*(#|//|$)'
```

That prints every changed line that is not a whole-line comment. Each line it prints must differ only after its comment mark.
