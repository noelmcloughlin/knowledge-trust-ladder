# What the check cannot see

A pass from `prose-check.py` says that what the script reads came through. It does not say that the meaning held, which only a reader can check. This page lists what the script cannot see, so that you read for it and say so in the hand-off.

## What a finding and a note name

A **finding** names something other than wording that differs, and the script exits 1:

- a number or its unit, a link, a code span, an HTML tag, a quotation or a code block;
- a list or a table cut short, a hard line break, or a paragraph cut in two inside a sentence;
- a frontmatter byte, a body a person vouched for, or a new character no reader sees;
- in a script, any line that is not prose;
- a sentence, list item or table row that otherwise stayed and turned over.

A sentence turned over when a word gave way to its opposite, a negative came or went, one count gave way to another, or two things changed places.

A **note** asks you to look again, and never changes the exit status. Most give the line:

- a word of strength that came or went, one word that gave way to another, the same words in a new order, or a link whose words changed;
- a number, day or month written as a word that came or went, and a sentence with few of its words left;
- a code span that is new, or that appears more or less often;
- a text that grew or lost over a fifth of its words.

A `page-words` note lists the words the page lost and gained. A cut sentence shows there when it took a fact with it, and so does a fact that came in. A link, a number or a quotation that a cut sentence held is a note when the page still holds it. A number is one only when the page still says each thing it counted.

## Mistakes it can miss

The script changes nothing. You reword the text, and you can slip. Each item below is a slip that the script would pass, so read for it.

- **A reversal in other words.** The script compares each changed sentence, list item or table row with the new one closest to it. It stops four things in a sentence that otherwise stayed. A word gave way to its opposite, as `enabled` to `disabled` or `confirmed` to `unconfirmed`. A negative came or went while every other word stayed. One number word gave way to another. Two runs of words changed places, as `the librarian hands it to the curator` reversed. Its list of opposites is fixed, and most of the sentence's words must stay. So `turned off` written for `turned on` gets a note and no more, and a sentence reworded throughout that now says the reverse passes.
- **What gets a note at most.** Each of these gets a note with its line:
  - a word of strength that came or went, such as `must`, `only`, `may`, `usually`, `all` or `most`;
  - one word that gave way to another, as `curator` to `librarian`, `and` to `or` or `weekly` to `daily`;
  - the same words in a new order, as `only` moved to another place;
  - a link whose words changed.

  A number, day or month written as a word gets a note for the page. A note never stops the script, so say in the hand-off what you decided about each.
- **A sentence that went.** A cut sentence gets a `sentence-gone` note when few of its words stand anywhere near. It gets a `page-words` note when a word of it is gone from the page. A sentence whose every word stands elsewhere on the page gets neither. That is the cut rule 10 allows, and the words may still say something else where they stand.
- **A swap in a sentence that also changed.** The script counts numbers, links, tags and keywords across the page. It stops two that changed places between two sentences it matched, between two rows of a table, and between two links. It matches a row by its first cell and a sentence by its words. So a swap passes when the first cells changed too, or when both sentences were reworded throughout.
- **Order and nesting.** It stops the items of a numbered list in a new order, when the first line of each item stayed. It does not see the order of bullets, which item a sentence sits under, or which paragraph a sentence moved to. A dropped list item or table cell is a finding.
- **The noun after a number.** `20 folders` written for `20 files` gets a note, and passes. Only percent and the units of size, time, frequency, length and weight count as part of a number.
- **Wording the script does not hold still.** That is single-quoted text, a blockquote, the type of a callout, and a letter swapped for one that looks the same.
- **Whether a link works.** It compares each target as written and opens none. It tracks `[text][label]` and each definition, and it does not see a `[label]` used by itself.
- **HTML across a blank line.** It reads the text of `<code>` or `<pre>` as code only within one block. After a blank line it reads the rest as prose.
- **Meaning in a script's code.** In a script it reads the comments and docstrings as prose. It holds every other line as it was: code, a directive, a command in a comment and the name that opens a row of a table. So it never says whether a comment still describes its code.
- **Line endings.** It reads files as CI does, with CRLF as LF, so a change of only the line endings is no finding. A byte order mark at the start goes the same way.
- **A rewording committed with the stamp.** The librarian's work list names a body that changed after the commit that recorded its stamp. A rewording in that same commit goes unseen, and so does one squashed into it, so keep the rewording in a pull request of its own.
- **A rewording already committed.** `--against` knows only the revision you name. A rewording committed before the check passes against `HEAD`, so name the revision from before it.
- **A retelling's sense.** A retelling's number passes if the adult text holds it anywhere, and a claim turned upside down passes.

## A character no reader sees

Never type the escape for such a character into a tool call: the call may decode it into the character itself. The script prints one as its code point, such as `<U+001B>`, so that no file can write to your terminal or a CI log through a finding.

## What it refuses although nothing is wrong

- **A number said another way.** `<5` to `less than 5`, or `20 MB` to `twenty megabytes`, reads as a number gone. Keep the number as it was. A spelling of a listed unit is fine: `10 ms` and `10 milliseconds` are one number.
- **A list number out of order.** A number in its list's order is a marker, which may change. Any other opens a fact, so renumbering a list that starts at 5 is a finding.
- **A reversal that is not one.** `Add a bullet? No.` to `Do not add a bullet.` reads as a negative gained, since the negative moved in from the next sentence. Keep the earlier sentence, or the person reads the two and rewords it by hand. Replayed over 351 real rewordings, this happened in 2.
- **Two things that changed places and agree.** `The key matches the login.` to `The login matches the key.` reads as two runs of words that changed places. Keep the earlier order. Two items joined by `and` or `or` may change places.
- **A count that grew with its list.** `The gate runs three checks, and one more on a release.` to `The gate runs four checks on a release.` reads as one number word for another. Keep the earlier count, or explain the finding in the hand-off.
- **A paragraph that ends without a full stop.** A reworded paragraph that ends on a bare word reads as one cut in two. End it with its full stop.
- **A change to a script's code that the person asked for.** The script cannot know that. Explain the `not-prose` finding in the hand-off.
- **Frontmatter it cannot place.** A `by:` under a key it does not know is unreadable, and so is a line of a folded description that opens with `by:`. It skips the concept and says so. The person spells it plainly, or rewords it by hand.

Replayed over 688 file versions from six repositories that passed before these checks, the checks stop 32. Each of the 32 holds a count in words that had changed, as `four skills` to `five skills`.

## Who vouched for a concept

The script reads `generated`, `verified`, `revised` and `refuted` line by line, as the gates do. It reads the plain spellings, and takes anything else for frontmatter it cannot read. It reads what the frontmatter says, and proves nothing about who wrote it. A forged `human:` event only stops a rewording here. The gates answer for the rest: *What the gates cannot see*, in ktl-sidecar's `references/gate.md`, says how far.
