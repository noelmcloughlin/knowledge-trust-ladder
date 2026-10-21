# Younger readers: retellings, and the pass for dyslexic readers

This page is for whoever writes or checks a text for a younger reader with **ktl-prose**, agent or person. It gives the two bands of age and the pass for dyslexic readers, with the limits of each. It says what a retelling may change, what it never changes, and how the work runs in the bundle and outside it.

## A retelling is not a rewording

ktl-prose makes three kinds of change, and each has its own rules.

- **A rewording** changes the wording and never a fact. It is the rest of this skill: the thirteen rules, Steps 1 to 5, and the script's proof that only the wording moved.

- **A retelling** is a new text for readers in a band of ages. It leaves detail out, explains each term and may reorder what it keeps. It never says what the original does not say.

- **A pass for dyslexic readers** is a rewording under tighter limits. A dyslexic reader needs every fact, so the pass keeps them all and changes the page where it stands.

A retelling leaves facts out and adds explanations, and a rewording must never do either. So a retelling is always a new file, linked to the original, and the original stays as it is.

Research on simplified texts shows why the line matters. Editors who level texts for children delete content in about 84 percent of sentence pairs and add content in about 31 percent, and models trained on their work do the same ([Devaraj et al. 2022](https://doi.org/10.18653/v1/2022.acl-long.506)). The child-friendly versions that children's rights bodies publish take the same shape: a shorter text, labelled as a version, linked to the full one, and checked with the original's authors ([Lundy 2021](https://doi.org/10.2838/559340)).

## The bands

| Band | The reader | Split a sentence over | Split a paragraph over | Sentences in one paragraph, at most | Grade target |
| --- | --- | --- | --- | --- | --- |
| `8-12` | aged 8 to 12 | 15 words | 50 words | 3 | 7 or under |
| `13-18` | aged 13 to 18 | 20 words | 75 words | 5 | 9 or under |
| `dyslexia` | dyslexic, of any age | 20 words | 75 words | 5 | none |
| none | an adult | 40 words | 150 words | no limit | none |

Look twice at a sentence past 12 words in the band for 8 to 12, and past 15 words in the other two. Split where the topic turns, never at a word count: a page of one-sentence paragraphs groups nothing.

The numbers come from plain-language guides, and each band sits inside them:

- **A sentence.** WCAG 2.2, the Web Content Accessibility Guidelines, gives 25 words as the English limit for text at lower secondary level ([Understanding 3.1.5](https://www.w3.org/WAI/WCAG22/Understanding/reading-level.html)). The NHS asks for sentences of up to 20 words ([How we write](https://service-manual.nhs.uk/content/how-we-write)). Dyslexia guides ask for an average of 15 to 20 ([Dyslexia Association of Ireland](https://dyslexia.ie/info-hub/assistive-technology/inclusive-communications/)). Easy-read guidance warns that "More than 15 words is harder to read" ([Department of Health and Social Care](https://www.gov.uk/government/publications/making-written-information-easier-to-understand-for-people-with-learning-disabilities-guidance-for-people-who-commission-or-produce-easy-read-information-revised-edition-2010)).

- **A paragraph.** The NHS asks for paragraphs of up to 3 sentences, and GOV.UK for no more than 5 ([Clear language](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/)). The word limits follow from those counts at the band's sentence length.

- **The grade.** The target uses the Automated Readability Index, which turns letters per word and words per sentence into a United States school grade plus one. A score of 7 matches readers aged 11 to 12, and 9 matches 13 to 14. WCAG asks for text no harder than lower secondary education, or a simpler version beside it. A grade is a hint and never a verdict: a page of short list items scores low whatever its words, and no formula knows which terms a reader has met.

Ages are the scale, because readers come from many school systems. ISCED, UNESCO's International Standard Classification of Education, names the levels. A school year in one country is only an example of how a person may say it.

| Band | ISCED level | United States grades | England school years | CEFR, roughly |
| --- | --- | --- | --- | --- |
| 8 to 12 | 1, and the start of 2 | 3 to 7 | Years 4 to 8 | A1 to B1 |
| 13 to 18 | 2 and 3 | 8 to 12 | Years 9 to 13 | B1 to C1 |

## Checking a page against a band

The check script holds a page to a band's limits:

```sh
uv run <skill>/scripts/prose-check.py --audience 13-18 <file>
```

A page that opens as rule 1 below asks, "This page is for readers aged 13 to 18.", names its own band. A plain style run then holds it to that band, and a note says so. Give `--audience` to a page that names no band, such as an original before its pass for dyslexic readers. A page that names one band while `--audience` asks for another is a finding. `--max-words` and `--max-paragraph` still set their own limit when given.

Under a band, the script also counts the sentences in each paragraph, and reports "via" and the Latin abbreviations "i.e.", "vs", "cf." and "etc." It notes two things that never change the exit status:

- **the grade**, with the words in a sentence, the letters in a word and the share of long words it comes from;
- **the words a younger reader may not know**: those the VOA Learning English word book does not hold, most frequent first. The word book lists about 1,600 words that learners of English meet first, and sits in this skill's `assets/` folder with its credit. A technical page always has some words outside it, so explain each where it first appears, as rule 2 says.

## Proving that a retelling adds nothing

The check script compares a retelling with the text it retells, in one direction:

```sh
uv run <skill>/scripts/prose-check.py --derived-from <original> <retelling>
```

A number, a link target, a code span, a quotation, an inline HTML tag or a fenced block that the retelling holds and the original does not is a finding. So is a first paragraph that does not link the original, and in the bundle a `derivedFrom` that does not name the adult concept. A heading spelt like `## Open questions` but not exactly so is a finding too. What the retelling left out is a note, and so is a `should` the original never has, a keyword left in capitals, or a link to another concept of the bundle.

The check changes nothing, so a retelling a person confirmed is a note, never a refusal. A rewording of a retelling is still proved with `--before` or `--against`, as Step 3 says, and that refuses a body a person vouched for.

## Who the reader is

A person names the band, and the skill never guesses it. Take the band from the first of these that holds:

1. the request, in a live session: "for my class of ten-year-olds", "for teenagers", "explain it like I'm five";
2. the page's own opening sentence, such as "This page is for readers aged 13 to 18.";
3. in the bundle, a band in the concept's `tags`, such as `audience-13-18`;
4. in the bundle, the curation policy's `Younger readers:` line, which a person sets with ktl-curator. `prose-check.py --bundle` prints it as its `audience:` line, so repeat that line in Step 1's report.

Map a request to a band by age. A school year or a grade maps through the table above. "Explain it like I'm five" means the band for 8 to 12, the lowest these limits cover. A range that crosses two bands takes the younger one. When a request names no age, grade or year, ask the person: "Which ages is it for: 8 to 12, or 13 to 18?"

Never infer the age of the person typing from how they write, and never ask a reader's own age. Estimating an age from someone's writing is a form of profiling under the EU's General Data Protection Regulation, whose Recital 71 says that automated decisions of that kind "should not concern a child". Such estimates are also often wrong. Never write anyone's age or name into a file. When a person says they are young, offer a retelling, and record nothing about them.

## What a retelling may change, and what it never changes

A retelling may:

- leave out any detail, section, table or fenced block, and say that the full page has them;
- split, reorder and regroup what it keeps, and ask questions in its headings;
- speak to the reader as "you" in a step;
- explain a term, and give an example, under the rules below.

A retelling never:

- adds a fact, a name, a number, a command, a code span, a link target or a quotation that the original does not hold, except a link to the original and, in the bundle, a link to a glossary concept;
- changes or rounds a number, and writes "about" only where the original hedges;
- adds an analogy, because an analogy claims something the source does not;
- weakens an instruction: `MUST` may become `must`, and `must` never becomes `should`;
- leaves out a warning or a prohibition about something the reader might do;
- renames `## Open questions`: a retelling that has the section spells the heading exactly so, because the curator, both plugins and the pen match that line whole.

An explanation or an example comes from a source, never from the writer:

- **A definition** repeats the description of a glossary concept, or links to that concept. Outside the bundle it repeats the original's own definition, or links to where the project defines the term.
- **An example** comes from the original, or from a source the original cites.

Where a passage cannot be retold without a new fact or an analogy, leave it out and say so in the hand-off. In a live session, ask the person instead.

## The rules a retelling adds

A retelling keeps the thirteen rules at its band's limits, and adds these.

1. Open by saying who the page is for and what it retells, with a link to the original: "This page is for readers aged 13 to 18. It retells the full page in shorter words. The full page has every detail."
2. Keep every technical term, and explain it where it first appears, as in "the pen (the script that writes the bundle)". Replace none.
3. Write every abbreviation out where it first appears. In the band for 8 to 12, that includes names the adult rules accept, such as CI and YAML.
4. Use headings that ask the questions a reader would ask, in the order they would ask them.
5. Give the concrete case before the general rule, where the original gives the case.
6. Use "you" in steps, and the third person in definitions.
7. Use no idiom and no slang.
8. Use no word in capitals in running text. Write an RFC 2119 keyword in lower case, and keep its strength.
9. Use bold for a term where it first appears and for a button or a menu item. Never use italics or underlining for emphasis.
10. Number the steps, with one action in each.
11. Bring in one new term to a paragraph.
12. End a how-to with a short check the reader can make, such as a question the page answers.

In the band for 13 to 18, a sentence may carry one subordinate clause, an idea may be named once it is explained, and the page may say why the thing matters and what it costs. In the band for 8 to 12, a sentence carries no subordinate clause, and the page assumes nothing beyond school and everyday devices.

## In the bundle

**ktl-librarian** writes a retelling through the pen, as a new concept, and its [retellings.md](../../ktl-librarian/references/retellings.md) gives its half of the work. ktl-prose never creates a concept.

- **Its path** is `young-readers/` and the adult concept's file name, in one flat folder at the top of the bundle. The index then lists the retellings in a section of their own, away from the adult bullets the docent picks from.
- **Its frontmatter** has the adult concept's `type`, `genre`, `about` and `resource`. Its `title` names the band, as in "The pen, for readers aged 13 to 18", and its `description` says who it is for and what it retells. `derivedFrom` names the adult concept's `id`, a `sources` entry gives the adult concept's own path as its `resource`, and `tags` carries the band, such as `audience-13-18`.
- **Its body** opens with the sentence in rule 1, and links the adult concept as a wikilink: "It retells [[the-pen]] in shorter words."

The `sources` entry matters. It puts the retelling on the librarian's work list whenever the adult concept changes, so the two cannot drift apart unseen.

ktl-prose then treats the retelling as any concept the librarian wrote: Step 1 lists it, and it is held to its band's limits. A **curator**, an adult with a forge login, confirms it against the adult concept, and asks whether the adult concept supports every sentence. Retell a concept a person has confirmed where you can: the retelling reads its body and spends nothing of its confirmation.

Where a host tests a retelling with young readers, as the child-friendly guides recommend, record a count in a band in the curation log line, such as "read with two readers in the band for 8 to 12". Never record a name, an age or a reader's words. Consent from the readers and from their parents or carers stays with the host.

## Outside the bundle

ktl-prose writes the retelling itself, in a live session, in a new file beside one a person names. [other-files.md](other-files.md#a-version-for-younger-readers) gives the steps, and [docs/examples/prose.md](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/docs/examples/prose.md), in this skill's home repository, holds a captured run on its README. The person who reads the pull request checks that the meaning held, as the original's authors do in the child-friendly guides.

## The pass for dyslexic readers

A pass for dyslexic readers is a rewording at the `dyslexia` limits: the same facts, in shorter sentences and paragraphs, where the page stands. Run the style check with `--audience dyslexia` before and after, and prove the rewording with `--before` or `--against` as Step 3 says. In the bundle it covers the concepts Step 1 marks `rewrite`. Outside the bundle it covers a file a person names, at the cost [other-files.md](other-files.md#before-you-reword-a-source) describes.

Two rules join the thirteen, because a dyslexic reader meets crowded text as a barrier:

- Use bold for emphasis and for a term where it first appears, never italics or underlining.
- Use no capitals in running text. A rewording never changes an RFC 2119 keyword, so a keyword in capitals stays.

Never add HTML or CSS to set a font, a size, spacing or a colour. Those belong to the renderer and to the reader's own settings. Studies find that the shape of the letters does not help ([Azzarello et al. 2026](https://doi.org/10.1007/s11881-026-00389-8)), while wider spacing can ([Zorzi et al. 2012](https://doi.org/10.1073/pnas.1205566109)), and spacing is the reader's to set.

## The hand-off for a retelling

Add these to Step 5's hand-off:

- the band, the original and the retelling, with the words in each, as the `--derived-from` line gives them;
- what the retelling left out, in a line or two;
- each definition and example it added, and where each came from;
- each passage left out because it could not be retold without a new fact or an analogy;
- who checks it against the original: in the bundle a curator, and outside it the person who reads the pull request;
- that no script shows the text is easier to read, and that reading it with readers in the band is the test.
