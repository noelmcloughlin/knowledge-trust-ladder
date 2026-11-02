# What the check cannot see

A pass from `prose-check.py` says that what the script reads came through. It does not say that the meaning held, which only a reader can check. This page lists what the script cannot see, so that you read for it and say so in the hand-off.

## What can still change unseen

- **Plain words.** `enabled` can become `disabled`, and `at least` can become `at most`. A sentence with no number, link or code can go. A `must`, a `not` or a number written as a word gets a note at most.
- **A swap between claims.** The script counts numbers, links, tags and keywords across the page. So two numbers swapped between two sentences pass, and so do two link targets swapped between two links.
- **Order and nesting.** It does not see the order of steps, which item a sentence sits under, or which cell of a table holds a value. A dropped list item or table cell is a finding, and a moved one is not.
- **The noun after a number.** `20 files` can become `20 folders`. Only percent and the units of size, time, frequency, length and weight count as part of a number.
- **Wording the script does not hold still.** That is a table cell's words, single-quoted text, a blockquote, the type of a callout, and a letter swapped for one that looks the same.
- **Whether a link works.** It compares each target as written and opens none. It tracks `[text][label]` and each definition, and it does not see a `[label]` used alone.
- **HTML across a blank line.** It reads the text of `<code>` or `<pre>` as code only within one block. After a blank line it reads the rest as prose.
- **Code in a script.** In a script it reads the comments and docstrings. It never reads code, a string or a comment at the end of a line of code.
- **Line endings.** It reads files as CI does, with CRLF as LF, so a change of line endings alone is no finding. A byte order mark at the start goes the same way.
- **A rewording already committed.** `--against` knows only the revision you name. A rewording committed before the check passes against `HEAD`, so name the revision from before it.
- **A retelling's sense.** A retelling's number passes if the adult text holds it anywhere, and a claim turned upside down passes.

## What it refuses although nothing is wrong

- **A number said another way.** `<5` to `less than 5`, or `20 MB` to `twenty megabytes`, reads as a number gone. Keep the number as it was. A spelling of a listed unit is fine: `10 ms` and `10 milliseconds` are one number.
- **A list number out of order.** A number in its list's order is a marker, which may change. Any other opens a fact, so renumbering a list that starts at 5 is a finding.
- **Frontmatter it cannot place.** A `by:` under a key it does not know is unreadable, and so is a line of a folded description that opens with `by:`. It skips the concept and says so. The person spells it plainly, or rewords it by hand.

## Who vouched for a concept

The script reads `generated`, `verified`, `revised` and `refuted` line by line, as the gates do. It reads the plain spellings, and takes anything else for frontmatter it cannot read. It reads what the frontmatter says, and proves nothing about who wrote it. A forged `human:` event only stops a rewording here. The gates answer for the rest: *What the gates cannot see*, in ktl-sidecar's `references/gate.md`, says how far.
