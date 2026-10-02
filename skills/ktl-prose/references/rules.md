# The rules: plain English for a knowledge bundle

This page is for whoever rewords a text with **ktl-prose**, agent or person. It gives each rule with a before and an after, says why the rule holds, and says when it gives way. The pairs come from the two hand passes that set this style, in the repository these skills ship from. A script checks three of the rules, and a reader checks the rest.

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

## 3. Keep one idea to a sentence

Split a sentence that runs past 40 words, and look twice at one past 30. A semicolon that joins two ideas becomes a full stop.

```text
Before: The number to watch is **confirmed by a person: n of N**, and it is meant to rise slowly - a handful of concepts in a sitting, cumulative and partial by design. A small, young bundle can reach fully-confirmed quickly; a large or fast-growing one never quite does, and the report says so instead of pretending.
After:  The number to watch is **confirmed by a person: n of N**. It is meant to rise slowly, a handful of concepts in a sitting. A small, young bundle can reach fully-confirmed quickly. A large or fast-growing one never quite does, and the report says so.
```

The script reports each such sentence as `long`. It counts 29 in the docs before the first pass and 11 after it, and 96 in the skills before the second pass and 31 after it.

It gives way to sense. The aim is that every word tells, and some sentences need their length. A semicolon is right in a series whose items hold commas.

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

This is a house rule, and it is stricter than the style books. Two things earn it a place. A spaced dash that lands at the start of a wrapped line becomes a list item in Markdown, and the dash is the plainest mark of an agent's voice. The script reports each one as `dash`. It counts 64 in the docs before the first pass and 18 after it, and 218 in the skills before the second pass and 2 after it.

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
After:  [...] a public key it carries under `.lokf/curators/`. The file is named after your login on the forge (GitHub, GitLab or Forgejo). Export the key you sign with and open a pull request holding only that file. The gate, the CI job that checks a pull request, refuses a change that lands a key and a confirmation by its holder together:
```

The second pass cut "PR" from 45 to 5 and "e.g." from 8 to 3. The script reports the stock phrases above, and "e.g.", as `words`.

It gives way to an abbreviation that is the thing's own name: CI, YAML, IRI. A term the page has defined needs no second definition.

## 10. Cut words that carry nothing

A word that carries nothing costs the reader a moment, and tells them the writer is selling.

```text
Before: **"Require signed commits" as a branch rule is deliberately off, and must stay off.** A commit made inside a runner is unsigned - GitHub only auto-signs commits made through the web UI or API - so the rule would reject the release job's promotion commit and break every release.
After:  **"Require signed commits" as a branch rule is off, and must stay off.** A commit made inside a runner is unsigned: GitHub only auto-signs commits made through the web UI or API. So the rule would reject the release job's promotion commit and break every release.
```

The first pass cut "deliberately" four times and "honest" or "honestly" four times, and added neither back. The script reports "deliberately" and "honestly" as `words`.

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

## Three things to know about the rules

- **The rules are defaults.** Strunk opens his own rules by observing that "the best writers sometimes disregard the rules of rhetoric". That is why each rule above says when it gives way.
- **Rules 4, 5 and 6 are house rules, stricter than the books.** The conventions the gate checks are stricter than OKF in the same way. The reason is the same: an agent told a rule in prose breaks it, and a strict rule is one a script can check.
- **A script sees three rules.** `scripts/prose-check.py` reports `dash`, `long` and `words`, and each finding is a candidate, not a verdict. It skips frontmatter, fenced blocks, code spans, link targets, headings, quotations and a short emphasised label. The other ten rules need a reader.

## What was left out, and why

- **Fiction craft**: voice, the senses, dialogue tags. A bundle states facts.
- **Advice to vary your words.** It is rule 8 reversed.
- **Praise of the sentence that holds its main clause back.** It is rule 1 reversed.
- **Hart's taste for the long form.** He writes "If you must choose between elegance and perfect clarity [...] always choose elegance", and "more is more and less is less". A bundle chooses clarity. He also makes the best case against rules 3 and 5: "A writer who disdains the semicolon is a fool", and of the dash, "Use it with abandon".
- **Contractions as a blanket rule.** The sources split, and the two passes kept them in prose written for people.

## Sources, and how each was read

The addresses sit in a fenced block so that a link checker does not fetch sites that refuse automated clients.

| Source | How it was read | What it gave |
| --- | --- | --- |
| NBS, "Five essential tips for writing effective specifications" | In full | Rules 8, 9, 10 and 13. Its seven Cs include clear, concise and consistent, and the spare tiles are its example. |
| Paul Graham, "Good Writing" (2025) | In full | Rule 13, and the limit on what a rewording can promise. |
| David Bentley Hart's "How to Write English Prose" | In full | Rules 8 and 9: "Do not use a thesaurus", and "Know the names of things and the names of places". He argues against rules 3, 5 and 10. |
| Strunk and White, *The Elements of Style*, fourth edition | The table of contents, and Strunk's text of 1918 | Rules 1, 2, 3, 5, 7, 9, 10, 11 and 12. Rule 1 is its "Keep related words together", rule 7 its "Express coordinate ideas in similar form", rule 10 its "Omit needless words", and rule 11 its "Put statements in positive form". |
| William Zinsser, *On Writing Well* | Secondary pages that quote the book | Rules 3, 4, 8, 9, 10 and 12: clutter, unity, and the first sentence. |
| Writer's Digest, on basic writing principles | In full | Rules 3 and 7. |
| Grammarly, on words to cut | In full | Rule 3, and the list behind rule 10. |
| The Write Practice, on Strunk and White | In full | The habit behind the check: keep the original beside what you have rewritten. |
| NowNovel, GrammarHow, The Novelry | In full | The dangling opening in rule 1, and "in order to" in rule 9. The rest is fiction craft or synonym lists. |

```text
https://www.thenbs.com/knowledge/five-essential-tips-for-writing-effective-specifications
https://www.paulgraham.com/goodwriting.html
https://thelampmagazine.com/blog/how-to-write-english-prose
https://www.goodreads.com/book/show/51478748-the-elements-of-style-fourth-edition
https://www.goodreads.com/book/show/53343.On_Writing_Well
https://www.thenovelry.com/blog/good-writing
```
