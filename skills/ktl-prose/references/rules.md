# The rules: plain English for a knowledge bundle

This page is for whoever rewords a text with **ktl-prose**, agent or person. It gives each rule with a before and an after, says why the rule holds, and says when it gives way. The pairs come from the three hand passes that set this style, in the repository these skills are published from, and from a fourth over three sibling bundles. A script checks parts of four of the rules, and a reader checks the rest. A last section, apart from the thirteen, says where a line ends in the source.

One rule stands above the thirteen: a rewording changes the wording and never a fact. When a rule and a fact pull apart, the fact wins and the sentence stays as it was.

## 1. Put the actor first and the verb early

A reader holds every word in mind until the verb arrives. Name who acts, then say what they do.

```text
Before: The whole tree, workflows and docs included: [docs/repository-layout.md](docs/repository-layout.md).
After:  [docs/repository-layout.md](docs/repository-layout.md) shows the whole tree, workflows and docs included.
```

No script finds a late verb, so here is a method. Find the main verb, count the words before it, and restructure when there are more than about eight. An opening that dangles is the same fault: "Running on a schedule, the bundle is refreshed" says that the bundle runs.

It gives way to a passive when the actor does not matter or is not known, as in "the key was revoked".

## 2. Give every sentence a verb, and start an instruction with it

A fragment leaves the reader to supply the verb, and an agent supplies the wrong one. An instruction that starts with its verb tells the reader at once that the step is theirs.

```text
Before: One **Curation** line with the counts, plus one **Deprecation** line per retired concept, prepended to `.lokf/knowledge/log.md` under today's date.
After:  Prepend one **Curation** line with the counts, plus one **Deprecation** line per retired concept, to `.lokf/knowledge/log.md` under today's date.
```

Spell out `do not` in an instruction. The second pass cut contractions from 49 to 9, and kept the rest in prose written for people.

It gives way in a label, a table cell or a list item that only names a thing.

## 3. Keep one idea to a sentence, and one topic to a paragraph

Split a sentence that runs past 40 words, and look twice at one past 30. A semicolon that joins two ideas becomes a full stop.

```text
Before: The number to watch is **confirmed by a person: n of N**, and it is meant to rise slowly - a handful of concepts in a sitting, cumulative and partial by design. A small, young bundle can reach fully-confirmed quickly; a large or fast-growing one never quite does, and the report says so instead of pretending.
After:  The number to watch is **confirmed by a person: n of N**. It is meant to rise slowly, a handful of concepts in a sitting. A small, young bundle can reach fully-confirmed quickly. A large or fast-growing one never quite does, and the report says so.
```

The script reports each such sentence as `long`. It counts 29 in the docs before the first pass and 11 after it, and 96 in the skills before the second pass and 31 after it.

A paragraph holds one topic, and its first sentence says what that topic is. Split a paragraph that runs past 150 words where its topic turns, and look twice at one past 100. Hold a list item to the same limit: a long one becomes a short item with a paragraph under it. Strunk makes the paragraph "the unit of composition", and its break the sign that "a new step in the development of the subject has been reached". A long block also costs the reader before they start. Zinsser warns that "one long chunk of type can discourage the reader from even starting to read".

```text
Before: Commits typed with Conventional Commits decide the version [...] All five skills ship together under that one tag. After a release that changes a template [...] once a sibling arms its scheduled librarian, the pin decides which instructions run unattended. [How the three repositories release](docs/releasing.md) has the whole pipeline [...]
After:  Commits typed with Conventional Commits decide the version [...] All five skills are released together under that one tag.

        After a release that changes a template [...] once a sibling turns on its scheduled librarian, the pin decides which instructions run unattended.

        [How the three repositories release](docs/releasing.md) has the whole pipeline [...]
```

The script reports each paragraph or list item past 150 words as `paragraph`, and never a table cell. The limit is the Federal Plain Language Guidelines' "no more than 150 words in three to eight sentences". The script counts 21 in the docs and skills before the third pass and none after it.

It gives way to sense. The aim is that every word tells, and some sentences need their length. A semicolon is right in a series whose items hold commas. A paragraph gives way to an argument that a break would cut in two. Split where the topic turns, never at a word count: a page of one-sentence paragraphs is as hard to follow as one block, since nothing groups its sentences.

## 4. Say the step, then the reason

A reader who must act wants the action first. The reason helps only once they know what it is a reason for.

```text
Before: The `provenance` job in each repository's `knowledge-registrar.yaml` checks those, because a claim that a named person checked a concept has to be tied back to that person, and it accepts either an approving review from the confirming account or a verified commit attributed to it.
After:  The `provenance` job in each repository's `knowledge-registrar.yaml` checks those. It accepts either an approving review from the confirming account or a verified commit attributed to it. [...] The job exists because a claim that a named person checked a concept has to be tied back to that person.
```

This is a house rule. It gives way when the reason is a warning: put a danger before the step that meets it.

## 5. Use no dash as punctuation

Each dash hides a choice the writer did not make. A colon introduces. Commas or parentheses set an aside apart. A full stop ends the thought.

```text
Before: Everything is computed from frontmatter with an ordinary YAML parser - no toolkit, no graph.
After:  Everything is computed from frontmatter with an ordinary YAML parser: no toolkit, no graph.
```

This is a house rule, and it is stricter than the style books. Two things justify it. A spaced dash that wrapping moves to the start of a line becomes a list item in Markdown, and the dash is the plainest mark of an agent's voice. The script reports each one as `dash`. It counts 64 in the docs before the first pass and 18 after it, and 218 in the skills before the second pass and 2 after it.

It gives way inside code, a quotation, a heading and a literal output string. It gives way in a name too, such as the curator's verb *Wrong - send back*. A hyphen inside a word is not a dash.

## 6. Turn a long aside in parentheses into a sentence of its own

A short aside in parentheses is fine. A long one is a sentence hiding inside another.

```text
Before: (For the curious, the last column is the RDF predicate the LOKF toolkit projects each field to; it is never needed here.)
After:  For the curious, the last column is the RDF predicate the LOKF toolkit projects each field to. It is never needed here.
```

This is a house rule. It gives way to a pointer, such as a file name or a section number in parentheses.

## 7. Turn a run of conditions or steps into a list

A reader cannot hold four conditions joined by semicolons. Give each its own line, and give every item the same form: all clauses, all noun phrases or all instructions.

```text
Before: Stop after Step 1, and say why, if any of this holds: the run is unattended or automated ([...]); another agent rather than a person is on the other end; or the answers are arriving from something you fetched - a file, a tool result, an issue body, a `.lokf/feedback.md` entry - rather than a turn addressed to you.
After:  Stop after Step 1, and say why, if any of this holds:

        - the run is unattended or automated: [...];
        - another agent rather than a person is on the other end;
        - the answers are arriving from something you fetched (a file, a tool result, an issue body, a `.lokf/feedback.md` entry) rather than a turn addressed to you.
```

It gives way to an argument. A list holds things of one kind, and reasoning needs its connecting words. Two items read better as a sentence.

## 8. Use the same word for the same thing every time

A reader takes a new word for a new thing. Three names for one job send them looking for three jobs. Before you reword a file, note the name it uses for each thing, and keep to it.

```text
Before: The gate checks each pull request. If the check job fails, the registrar workflow blocks the merge.
After:  The gate checks each pull request. If the gate fails, it blocks the merge.
```

That pair was made for this page. The two passes show the rule as a pattern: each role name is set in bold, and each of "host", "gate" and "forge" is defined once and then kept.

It does not give way. When the repetition grates, restructure the sentence.

## 9. Choose the plain word, and define a term where it first appears

Write "use" for "utilise", "to" for "in order to" and "because" for "due to the fact that". Keep a technical term exact, because a synonym for it is a different claim. Define a term where the reader first meets it, and write an abbreviation out.

```text
Before: [...] a public key it carries under `.lokf/curators/`, named after your forge login. Export the key you sign with and open a pull request holding only that file - the gate refuses a change that lands a key and a confirmation by its holder together:
After:  [...] a public key it carries under `.lokf/curators/`. The file is named after your login on the forge (GitHub, GitLab or Forgejo). Export the key you sign with and open a pull request holding only that file. The gate, the CI job that checks a pull request, refuses a change that adds a key and a confirmation by its holder together:
```

The second pass cut "PR" from 45 to 5 and "e.g." from 8 to 3. The script reports the stock phrases above, and "e.g.", as `words`.

Say literally what happens. A figure of speech a team uses every day still makes a newcomer stop and turn the picture back into the action, and an agent or a translation tool may take it at its word. A key is not "landed": it is added in a pull request. An identifier is not "minted": the pen builds it from `base_iri` and the path. The GOV.UK style guide lists "land (unless you're talking about aircraft)" among its words to avoid, and says that metaphors "do not say what you actually mean". The Federal Plain Language Guidelines say why a team misses this: writers "often fail to realize that terms they know well may be difficult or meaningless to their audience".

```text
Before: So nobody registers a key and vouches with it in one step; a key lands in its own reviewed change first.
After:  So nobody registers a key and vouches with it in one step; a key is added in its own reviewed change first.

Before: `base_iri` plus a concept's path mints its IRI. Never remove these keys, and never mint inside a URL space the project does not control.
After:  A concept's IRI is `base_iri` plus its path. Never remove these keys, and never build IRIs in a URL space the project does not control.
```

The third pass replaced the figures below. The script reports the words of the first five rows as `words`, since none is literal in a technical text. The words of the last four have literal uses too, so a reader decides.

| Figure | Say instead |
| --- | --- |
| "land", "lands", "landed" | "is merged", "is added", "is written" or "is installed" |
| "mint", "minted" | "builds", "makes" or "issues" |
| "ship", "ships", "shipped" | "is released", "is published", "includes" or "holds" |
| "arm", "armed", "wire", "wiring" | "turn on", "set up", "connect" or "link" |
| "dogfood", "load-bearing" | "uses its own", or say what depends on it |
| "lay down", "laid down" | "install", "copy" or "create" |
| "travels with", "reads off" | "is uploaded with", "checks on" or "finds on" |
| "holds every other hand to the same" | "asks the same of every other writer" |
| "door", "through one door" | the way in, by its name, or "in one way only" |

It gives way to an abbreviation that is the thing's own name: CI, YAML, IRI. A term the page has defined needs no second definition. A figure gives way to a name the project defines, such as *the pen* or *the doorway*, once its page has defined it. It gives way to a word of the analogy the project names its roles by, such as the librarian's *desk*, once the project's glossary defines it. It gives way too to a term of art the reader's own field uses in that exact sense, such as pinning a version.

## 10. Cut words that carry nothing

A word that carries nothing costs the reader a moment, and tells them the writer is selling.

```text
Before: **"Require signed commits" as a branch rule is deliberately off, and must stay off.** A commit made inside a runner is unsigned - GitHub only auto-signs commits made through the web UI or API - so the rule would reject the release job's promotion commit and break every release.
After:  **"Require signed commits" as a branch rule is off, and must stay off.** A commit made inside a runner is unsigned: GitHub only auto-signs commits made through the web UI or API. So the rule would reject the release job's promotion commit and break every release.
```

The first pass cut "deliberately" four times and "honest" or "honestly" four times, and added neither back. The script reports "deliberately" and "honestly" as `words`.

A possessive already says whose a thing is, a noun already names it, and a negative is already whole. So read each "own" after a possessive, each "itself" after a noun and each "at all" after a negative, and cut the one that draws no contrast.

```text
Before: It never touches the Node build (`build.yml`) or the LOKF bundle's own semantics. The tool itself is installed at exact pinned versions inside the workflow.
After:  It never touches the Node build (`build.yml`) or the LOKF bundle's semantics. The tool is installed at exact pinned versions inside the workflow.
```

A fourth pass reworded the bundles of three sibling repositories. It cut "own" 58 times of 84, and "itself" or "themselves" 33 times of 43. It kept each one that draws a contrast, as "its own two checks" and "approves itself" do, so the script lists neither word.

That pass also measured what a rewording does to length. It cleared 305 of the script's 312 findings, and the text went from 15,526 words to 15,688. A fragment given its verb, and "pull request" written for "PR", cost more words than the cuts saved. The 7 findings left sit under `## Open questions`, which a rewording never touches.

It gives way to a hedge that states a real condition: "usually" is a fact when the exception exists. The second pass kept "actually", "really", "simply" and "just" wherever they carried a contrast, so the script lists none of them.

## 11. Say what is, and what to do

A sentence that says what a thing is not leaves the reader to work out what it is.

```text
Before: A large or fast-growing one never quite does, and the report says so instead of pretending.
After:  A large or fast-growing one never quite does, and the report says so.
```

It gives way to a prohibition that guards something. "Never write a `human:` event" is the rule itself, and no positive form says it as well. Keep its strength too: `must` stays `must`.

## 12. Open each page by saying who it is for

The first sentence tells a reader whether to keep reading.

```text
Before: The human-facing labels in SKILL.md map onto OKF v0.2 §5 / LOKF Golden Rule 6 fields.
After:  This page is for the **curator** and for anyone reading its report: it defines each trust label by the frontmatter fields behind it.
```

A concept body opens by saying what the thing is, as its `description` does. Add no sentence the text did not hold. Reorder what is there, and report the opening that is missing.

It gives way in a reference table or a glossary entry, which names no reader and says what the thing is.

## 13. Report what you cannot fix

Only the author knows the number. You do not.

```text
Vague:  The contractor shall provide some spare tiles.
Exact:  Provide 20 spare tiles of each type used, including all variations in colour and finish.
```

Report a vague quantity, a sentence you cannot parse and a claim that looks wrong, each with its line. Leave the text as it is, and never guess. A wrong fact in a concept is ktl-librarian's to correct from the source.

Plain wording is no proof of a true claim. Paul Graham argues that writing which sounds good is more likely to be right, because the writer who repairs a clumsy sentence often has to repair the idea in it. He limits that to writing used to develop ideas. A copy editor who smooths another's sentence gets the sound without the repair.

## Line breaks in the source

This section is about layout, not wording, so it stands apart from the thirteen rules. It says where a line ends in the source of a text you reword. Keep the layout the file's project uses. In the bundle, that is one line for each paragraph and each list item.

```text
Before: The pen is the librarian's only way to write the bundle, and the bundle
        has other writers: a person writes the curator's verdicts through
        ktl-curator or the KTL Curator plugin.
After:  The pen is the librarian's only way to write the bundle, and the bundle has other writers: a person writes the curator's verdicts through ktl-curator or the KTL Curator plugin.
```

No Markdown specification asks for a wrapped line. CommonMark reads a line ending inside a paragraph as a soft line break, which a browser shows as a space, so a standard renderer draws every layout alike. The choice concerns only the source, and three layouts are in wide use:

- **One line per paragraph.** The editor wraps each line on screen. The Plone documentation guide asks for it.
- **One sentence per line.** A line ends where a sentence ends. Brian Kernighan advised it in 1974, Semantic Line Breaks specifies it, Asciidoctor recommends it, and GitLab asks for each new sentence on a new line.
- **A fixed column.** Lines break near a set width. Google's Markdown style guide sets 80 characters, and Microsoft's PowerShell documentation sets 100.

Each layout has a benefit and a cost:

- **A line break gives line-based tools a finer grain.** A diff, `git blame`, a review comment, a suggested change and a merge each work line by line, so they reach one sentence only when it has a line of its own. Google keeps its column partly because "Code Search doesn't soft wrap". Microsoft keeps its column because it "improves the readability of git diffs and history".
- **A fixed column reflows.** Reword one sentence and every later line of the paragraph moves, so the diff marks lines whose words did not change. Kernighan, Semantic Line Breaks and Asciidoctor each give this as the reason to break at sentences instead.
- **One sentence per line keeps line-level review without reflow.** A changed sentence is a changed line, and a long sentence shows as a long line.
- **One line per paragraph is the cheapest to write, and it reads the same wherever a line break shows.** GitHub shows a single line break as a break in issues, pull requests and discussions, and Obsidian's Live Preview shows each source line as a line. No phrase spans two lines, so `grep`, the pen's `replace` and an agent's exact edit find it. No wrapped line can start a list, a heading or a block quote by accident (rule 5). Its cost is the coarse diff: one changed word marks the whole paragraph. GitHub's rendered prose diff and `git diff --word-diff` mark the changed words.

The sources agree on no single layout. They agree that a project picks one and keeps every file to it, and that a tool keeps the project's choice: Prettier leaves a file's wrapping as it is unless told otherwise. So:

- **In the bundle**, use ktl-librarian's layout: one line for each paragraph and each list item. ktl-librarian writes it in every bundle, and the repository these skills are published from turns off markdownlint's line-length rule, MD013, for its own pages too. In a concept you reword, give the whole body this layout, so no concept is left in two. Leave the `## Open questions` section, the region between the `<!-- lokf:related -->` markers and every fenced block as they are.
- **Outside the bundle**, use the host's layout. Its tooling may set one: a markdownlint configuration that leaves MD013 on (as markdownlint does by default, at 80 columns), Prettier's `proseWrap`, or an `.editorconfig` `max_line_length` for Markdown. Otherwise the file shows it. Lay out each paragraph you reword to match, and leave the others as they are.
- **Change a file's layout only when the person asks.** A layout is the project's choice, not a matter of wording.

It gives way in a table, frontmatter and a heading, which keep their own lines, and at a hard line break the author wrote (two trailing spaces, a backslash or `<br>`), which is content. A comment in a script or a workflow keeps the wrapping of the code around it. The comparison in Step 3 does not count a moved line break, so a paragraph laid out anew passes when nothing else differs.

## Four things to know about the rules

- **The rules are defaults.** Strunk opens his own rules by observing that "the best writers sometimes disregard the rules of rhetoric". That is why each rule above says when it gives way.
- **Rules 4, 5 and 6 are house rules, stricter than the books.** The conventions the gate checks are stricter than OKF in the same way. The reason is the same: an agent told a rule in prose breaks it, and a strict rule is one a script can check.
- **A script sees part of four rules.** `scripts/prose-check.py` reports `long` and `paragraph` for rule 3, `dash` for rule 5, and `words` for rules 9 and 10. Each finding is a candidate, not a verdict. It skips frontmatter, fenced blocks, code spans, link targets, headings, quotations and a short emphasised label. The other nine rules need a reader, and so does every figure of speech it does not list.
- **The script also reports a character no reader sees, as `unseen`.** That is no rule of style but a hazard. A zero-width space or a byte order mark renders as nothing. A right-to-left override reorders what a reader sees: the "Trojan Source" attack (CVE-2021-42574) uses it to make code read differently from how it runs. An agent that types such a character's escape into a tool call can write the character itself. Delete one from prose you may reword, and report one in code, in a quotation or in a concept you may not touch.

## What was left out, and why

- **Fiction craft**: voice, the senses, dialogue tags. A bundle states facts.
- **Advice to vary your words.** It is rule 8 reversed.
- **Praise of the sentence that holds its main clause back.** It is rule 1 reversed.
- **Orwell's rule against the passive.** Rule 1 puts the actor first already, and gives way to a passive when the actor does not matter.
- **Varying the length of paragraphs for interest.** The Federal Plain Language Guidelines advise it. A bundle splits where the topic turns, and lets the lengths fall where they fall.
- **Hart's taste for the long form.** He writes "If you must choose between elegance and perfect clarity [...] always choose elegance", and "more is more and less is less". A bundle chooses clarity. He also makes the best case against rules 3 and 5: "A writer who disdains the semicolon is a fool", and of the dash, "Use it with abandon".
- **Contractions as a blanket rule.** The sources split, and the two passes kept them in prose written for people.

## Sources, and how each was read

The addresses sit in a fenced block so that a link checker does not fetch sites that refuse automated clients.

| Source | How it was read | What it gave |
| --- | --- | --- |
| NBS, "Five essential tips for writing effective specifications" | In full | Rules 8, 9, 10 and 13. Its seven Cs include clear, concise and consistent, and the spare tiles are its example. |
| Paul Graham, "Good Writing" (2025) | In full | Rule 13, and the limit on what a rewording can promise. |
| David Bentley Hart's "How to Write English Prose" | In full | Rules 8 and 9: "Do not use a thesaurus", and "Know the names of things and the names of places". He argues against rules 3, 5 and 10. |
| Strunk and White, *The Elements of Style*, fourth edition | The table of contents, and Strunk's text of 1918 | Rules 1, 2, 3, 5, 7, 9, 10, 11 and 12. Rule 1 is its "Keep related words together", rule 3's paragraph its "Make the paragraph the unit of composition", rule 7 its "Express coordinate ideas in similar form", rule 10 its "Omit needless words", and rule 11 its "Put statements in positive form". |
| William Zinsser, *On Writing Well* | Secondary pages that quote the book | Rules 3, 4, 8, 9, 10 and 12: clutter, unity, short paragraphs and the first sentence. |
| GOV.UK style guide, "A to Z", its words to avoid | The entry in full | Rule 9's figures of speech: "land (unless you're talking about aircraft)", and the advice to replace a metaphor "by breaking the term into what you're actually doing". |
| Federal Plain Language Guidelines, March 2011, revised May 2011 | The sections on jargon, short paragraphs and topic sentences | Rule 3's paragraph limit, and rule 9's warning about terms a team knows well. |
| George Orwell, "Politics and the English Language" (1946) | Its six rules, and its passage on dying metaphors | Rule 9: "Never use a metaphor, simile or other figure of speech which you are used to seeing in print". |
| Writer's Digest, on basic writing principles | In full | Rules 3 and 7. |
| Grammarly, on words to cut | In full | Rule 3, and the list behind rule 10. |
| The Write Practice, on Strunk and White | In full | The habit behind the check: keep the original beside what you have rewritten. |
| NowNovel, GrammarHow, The Novelry | In full | The dangling opening in rule 1, and "in order to" in rule 9. The rest is fiction craft or synonym lists. |
| CommonMark Spec, version 0.31.2 | The sections on paragraphs, soft line breaks and list items | Line breaks: a line ending inside a paragraph shows as a space, and a list item or a heading can interrupt a paragraph. |
| Brian Kernighan, "UNIX for Beginners" (1974), as Brandon Rhodes quotes it in "Semantic Linefeeds" (2012), and Semantic Line Breaks | Both pages in full | Line breaks: "Start each sentence on a new line", and the reflow that a break at a sentence avoids. |
| Asciidoctor, "AsciiDoc Recommended Practices", and GitLab's "Documentation Style Guide" | The sections on line length and on one sentence per line | Line breaks: one sentence per line instead of a fixed column, and GitLab's "Start each new sentence on a new line". |
| Google's Markdown style guide, and Microsoft's PowerShell "Markdown best practices" | The sections on line length | Line breaks: the case for a column, from tools built for code and from the readability of diffs. |
| Plone Documentation Guide, "Whitespace" | In full | Line breaks: no character limit for flowing text. |
| Ciro Santilli's "Markdown Style Guide", and markdownlint's rule MD013 | The guide's section on line wrapping, which the rule cites, and the rule in full | Line breaks: the cost of each layout, and MD013's 80-column default. |
| Prettier, "Options" | The `proseWrap` option | Line breaks: the default keeps a file's wrapping, because "some services use a linebreak-sensitive renderer". |
| GitHub Docs, on formatting syntax and on non-code files | The sections on line breaks and on rendered prose diffs | Line breaks: issues, pull requests and discussions show a single line break, and a pull request can show a rendered prose diff. |
| Obsidian Help, "Basic formatting syntax", and a forum request of January 2026 | The section on line breaks, and the request | Line breaks: Reading view joins a paragraph's lines, and Live Preview shows each source line. |
| One page each from GitHub Docs, MDN, Azure, PowerShell, Kubernetes, GitLab, the Rust book, VS Code, Google's style guide, react.dev, Docker and Astro (October 2026) | Line breaks counted by a script | Line breaks: five pages put each paragraph on one line, five wrap at a column, MDN puts each sentence on its own line, and GitLab mixes them. |

```text
https://www.thenbs.com/knowledge/five-essential-tips-for-writing-effective-specifications
https://www.paulgraham.com/goodwriting.html
https://thelampmagazine.com/blog/how-to-write-english-prose
https://www.goodreads.com/book/show/51478748-the-elements-of-style-fourth-edition
https://www.goodreads.com/book/show/53343.On_Writing_Well
https://www.gutenberg.org/ebooks/37134
https://www.advicetowriters.com/advice/2015/3/1/short-paragraphs.html
https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/style-guides/a-to-z-style-guide/
https://www.fai.gov/sites/fai/files/2016-12-22-Federal-Rulemaking-VAAR-FederalPLGuidelines.pdf
https://www.orwellfoundation.com/the-orwell-foundation/orwell/essays-and-other-works/politics-and-the-english-language/
https://www.thenovelry.com/blog/good-writing
https://spec.commonmark.org/0.31.2/
https://rhodesmill.org/brandon/2012/one-sentence-per-line/
https://sembr.org/
https://asciidoctor.org/docs/asciidoc-recommended-practices/
https://docs.gitlab.com/development/documentation/styleguide/
https://google.github.io/styleguide/docguide/style.html
https://learn.microsoft.com/en-us/powershell/scripting/community/contributing/general-markdown
https://docs-guide.plone.org/markdown/whitespace
https://cirosantilli.com/markdown-style-guide
https://github.com/DavidAnson/markdownlint/blob/main/doc/md013.md
https://prettier.io/docs/options
https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax
https://docs.github.com/en/repositories/working-with-files/using-files/working-with-non-code-files
https://obsidian.md/help/syntax
https://forum.obsidian.md/t/strict-line-breaks-in-live-preview/109696
```
