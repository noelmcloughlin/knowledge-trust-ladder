# Other files: a Markdown file outside the bundle

This page is for the case a person forces: they name a Markdown file outside `.lokf/knowledge/` and ask **ktl-prose** to reword it. The rules are the same as in the bundle. What differs is what the file is to the bundle, and what you may not touch.

## Only a file the person names

Work outside the bundle only on a file the person names in a turn addressed to you. Never widen the request: "the README" is one file, not the docs beside it. The rule about a live session in SKILL.md's Step 2 holds here unchanged.

## What you never touch

- **A record of the past**: the released sections of a changelog, a log, a captured transcript. Rewording it changes what was said.
- **Text taken from elsewhere**: a licence, a code of conduct, a quoted specification.
- **An installed copy**: anything under `.agents/` or `.claude/`. Reword the source it was installed from.
- **A file ktl-sidecar installed**: everything under `.lokf/` outside `knowledge/`, and the three `knowledge-*.yaml` workflows. Each is a copy of a template, and an edited copy is what the sidecar's next repair replaces.

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

## A version for younger readers

A person may ask for a version of a file for younger readers, such as a README for teenagers or a docs page for a class. Write it as a retelling, under the rules in [young-readers.md](young-readers.md), in a new file. The original stays as it is, apart from one sentence that points to the new file.

1. **Name both files.** The new file sits beside the original, and its name carries the register after the language: `README.en-simple.md` beside `README.md`. `simple` is the variant subtag the IANA language registry gives a simplified form. The band goes in the opening sentence, never in the name. Ask the person to agree the name.
2. **Write the retelling** at its band's limits. Open with who it is for and a link back:

   ```markdown
   This page is for readers aged 13 to 18. It retells [README.md](README.md) in shorter words. The full page has every detail.
   ```

3. **Point the original to it.** Add one sentence to the original that names the new file, once the person agrees. That sentence changes a file concepts may rest on, so say first what it costs, as [Before you reword a source](#before-you-reword-a-source) describes.
4. **Check it.** Run the style check on the new file. Its opening sentence names its band, so the script holds it to that band's limits. Then run `prose-check.py --derived-from <original> <new file>`, and fix each finding. No script reads meaning, so read the new file against the original, sentence by sentence: each sentence must rest on one the original holds.
5. **Hand it off** with the band, both files, what the retelling left out and where each explanation came from. The person who reads the pull request checks that the meaning held.

A new file costs the bundle nothing beyond that one sentence, because no concept rests on it yet. A file this page says you never touch is never retold either.

For dyslexic readers there is no second file. Reword the original where it stands, at the `dyslexia` limits in [young-readers.md](young-readers.md#the-pass-for-dyslexic-readers).

## Line breaks

Lay out each paragraph you reword the way the host does, and leave the others as they are. Look for the layout in the host's tooling first: a markdownlint configuration that leaves MD013 on (as markdownlint does by default, at 80 columns), Prettier's `proseWrap`, or an `.editorconfig` `max_line_length` for Markdown. Otherwise follow the file: one line per paragraph, one sentence per line, or a fixed column. Change the file's layout only when the person asks. [rules.md](rules.md) gives the reasons under *Line breaks in the source*.

## Proving the change

```sh
uv run <skill>/scripts/prose-check.py --against HEAD <files>     # a file git already held
uv run <skill>/scripts/prose-check.py --before <copy> <file>     # a file you copied first
```

Fix each finding, or explain it in the hand-off. Outside the bundle a person may ask for a change of content in the same request, and the script cannot know that. A changed heading is only a note here, and other pages may link to it. Search for its anchor before you keep the change.

Hand off the files the person named and no others. Give the counts before and after, each sentence you left alone, and what no script proved: that the meaning held.

## Comments in scripts and workflows

Given a `.sh`, `.py`, `.yaml`, `.yml` or `.toml` file, or a justfile, the script reads its `#` comments, and in Python its docstrings, under the same rules. Each block of comment lines is a paragraph, and an empty comment line splits one. It leaves out a shebang, a `# shellcheck` or similar directive, a `# /// script` block, and a `#` line inside a heredoc, which is data. It reads a comment's layout as a person does. An indented line in columns is a table row, read as one cell with the lines indented under it, so a table of options is never one long sentence. An indented line after a `Usage` line, a line ending with a colon or an empty line is a command, and is not read, unless it starts as a sentence does.

The unit of a comment review is the block a change touches, not the lines it adds. A change that puts two sentences into a paragraph of five can take it past the limit, and only the whole block shows that. Read and count the block. Split a long one with an empty comment line where its topic turns, and keep the comment's line breaks as the code around it wraps them.

Never touch either of these:

- a directive: `#!`, `# shellcheck`, a `# ///` block, or the version comment after a pinned `uses:`;
- a `#` line inside a heredoc, which is data.

Then show that only comments changed:

```sh
git diff -U0 -- <file> | grep -E '^[+-]' | grep -vE '^(\+\+\+|---) ' | grep -vE '^[+-][[:space:]]*(#|//|$)'
```

That prints every changed line that is not a whole-line comment. Each line it prints must differ only after its comment mark. `--against` and `--before` compare a script as its comments and docstrings, and read every line for a character no reader sees, so only this command shows that the code did not change.
