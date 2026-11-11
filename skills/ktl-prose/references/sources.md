# Sources: where the rules come from

This page is for whoever wants the reasons behind [rules.md](rules.md), or weighs a change to a rule. It says what the rules left out and why, what the sources say about line breaks, and how each source was read. No step of a rewording needs it.

## What was left out, and why

- **Fiction craft**: voice, the senses, dialogue tags. A bundle states facts.
- **Advice to vary your words.** It is rule 8 reversed.
- **Praise of the sentence that holds its main clause back.** It is rule 1 reversed.
- **Orwell's rule against the passive.** Rule 1 puts the actor first already, and gives way to a passive when the actor does not matter.
- **Varying the length of paragraphs for interest.** The Federal Plain Language Guidelines advise it. A bundle splits where the topic turns, and lets the lengths fall where they fall.
- **Hart's taste for the long form.** He writes "If you must choose between elegance and perfect clarity [...] always choose elegance", and "more is more and less is less". A bundle chooses clarity. He also makes the best case against rules 3 and 5: "A writer who disdains the semicolon is a fool", and of the dash, "Use it with abandon".
- **Contractions as a blanket rule.** The sources split, and the two passes kept them in prose written for people.

## Line breaks: what the sources say

[rules.md](rules.md#line-breaks-in-the-source) says which layout to use. This section gives the reasons.

No Markdown specification asks for a wrapped line. CommonMark reads a line ending inside a paragraph as a soft line break, which a browser shows as a space, so a standard renderer draws every layout alike. The choice concerns only the source, and three layouts are in wide use:

- **One line per paragraph.** The editor wraps each line on screen. The Plone documentation guide asks for it.
- **One sentence per line.** A line ends where a sentence ends. Brian Kernighan advised it in 1974, Semantic Line Breaks specifies it, Asciidoctor recommends it, and GitLab asks for each new sentence on a new line.
- **A fixed column.** Lines break near a set width. Google's Markdown style guide sets 80 characters, and Microsoft's PowerShell documentation sets 100.

Each layout has a benefit and a cost:

- **A line break gives line-based tools a finer grain.** A diff, `git blame`, a review comment, a suggested change and a merge each work line by line, so they reach one sentence only when it has a line of its own. Google keeps its column partly because "Code Search doesn't soft wrap". Microsoft keeps its column because it "improves the readability of git diffs and history".
- **A fixed column reflows.** Reword one sentence and every later line of the paragraph moves, so the diff marks lines whose words did not change. Kernighan, Semantic Line Breaks and Asciidoctor each give this as the reason to break at sentences instead.
- **One sentence per line keeps line-level review without reflow.** A changed sentence is a changed line, and a long sentence shows as a long line.
- **One line per paragraph is the cheapest to write, and it reads the same wherever a line break shows.** GitHub shows a single line break as a break in issues, pull requests and discussions, and Obsidian's Live Preview shows each source line as a line. No phrase spans two lines, so `grep`, the pen's `replace` and an agent's exact edit find it. No wrapped line can start a list, a heading or a block quote by accident (rule 5 of [rules.md](rules.md)). Its cost is the coarse diff: one changed word marks the whole paragraph. GitHub's rendered prose diff and `git diff --word-diff` mark the changed words.

The sources agree on no single layout. They agree that a project picks one and keeps every file to it, and that a tool keeps the project's choice: Prettier leaves a file's wrapping as it is unless told otherwise.

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
| Federal Plain Language Guidelines, March 2011, revised May 2011 | The sections on jargon, short paragraphs, topic sentences, and double negatives and exceptions to exceptions | Rule 3's paragraph and sentence limits, rule 4's rule before its exception, and rule 9's warning about terms a team knows well. |
| Joseph Williams and Joseph Bizup, *Style: Lessons in Clarity and Grace* | Secondary pages that summarise the lessons | Rule 3's method: the topic string, a passage's run of sentence subjects, as the test of coherence. |
| George Gopen and Judith Swan, "The Science of Scientific Writing" (1990) | A transcription of the article | Rule 4's rule before its exception, and rule 1: readers want the known before the new, and the verb close to the subject. |
| Steven Pinker, *The Sense of Style* | Secondary pages that quote the book | Rule 10: an intensifier reads as a hedge, because an unmodified word is read as absolute. |
| Emily Thrush, "Plain English? A study of plain English vocabulary and international audiences" (2001) | The abstract | Rule 9's quiet figures: a non-native reader can misread a phrasal verb. |
| Microsoft Writing Style Guide, "Writing tips" for global communications | In full | Rule 9: avoid idioms for a worldwide audience, include "that" and "who", and place "only" with care. Rule 2: limit sentence fragments. |
| Diátaxis, "How-to guides" and "Reference" | Both pages in full | What the genre asks: a how-to guide is a sequence that does not explain, and reference describes and is austere. |
| George Lakoff and Mark Johnson, *Metaphors We Live By* | Not read for this page; the term is theirs | Rule 9's quiet figures: a program as a place, and its parts as things that travel. |
| ASD-STE100, Simplified Technical English | The standard's FAQ, and secondary summaries of its rules | Rules 3 and 8: one topic to a paragraph, at most six sentences, and one meaning to a word. The counts come from the summaries, not the standard. |
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
https://www.antoinebuteau.com/lessons-from-joseph-m-williams-joseph-bizup/
https://www.win.tue.nl/~wstomv/quotes/science-of-scientific-writing.html
https://www.stafforini.com/quotes/?p=2300
https://newrepublic.com/article/119687/steven-pinker-language-interview-jesse-singal
https://digitalcommons.memphis.edu/facpubs/3866
https://learn.microsoft.com/en-us/style-guide/global-communications/writing-tips
https://asd-ste100.org/STE_faq.html
https://plainlanguage.gov/guidelines/concise/use-positive-language/
https://diataxis.fr/how-to-guides/
https://diataxis.fr/reference/
```
