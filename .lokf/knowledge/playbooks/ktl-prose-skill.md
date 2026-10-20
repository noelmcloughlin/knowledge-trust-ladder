---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/ktl-prose-skill
title: ktl-prose skill
description: The librarian's copy editor. It rewords the body of a concept an agent wrote, in plain English, before a person confirms it, changing the wording and never a fact or a frontmatter byte, and its script proves that only the wording changed.
genre: how-to
resource: skills/ktl-prose/SKILL.md
sources:
  - resource: skills/ktl-prose/SKILL.md
  - resource: skills/ktl-prose/references/rules.md
  - resource: skills/ktl-prose/references/other-files.md
  - resource: skills/ktl-prose/references/young-readers.md
  - resource: skills/ktl-prose/scripts/prose-check.py
  - resource: docs/architecture.md
  - resource: CHANGELOG.md
  - resource: skills/ktl-prose/assets/voa-word-book.txt
references:
  - https://w3id.org/ktl/knowledge/playbooks/ktl-curator-skill
  - https://w3id.org/ktl/knowledge/policies/threat-model
dependsOn:
  - https://w3id.org/ktl/knowledge/playbooks/ktl-librarian-skill
about:
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
definedBy:
  - https://w3id.org/ktl/knowledge/references/agent-skills-specification
generated:
  by: process:ktl-librarian
  at: "2026-10-20T23:23:33Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-19T23:21:13Z"
---
# Overview

A museum edits its labels before the exhibition opens. `ktl-prose` does that for the `.lokf/` knowledge bundle: it rewords what the librarian wrote, in plain English, before a person confirms it. It changes the wording and never a fact. A curator can only confirm a claim they can read. The skill is a copy editor, not an author. The librarian stays the maker of every concept it derived, so `generated` keeps naming it, and `log.md` and git record the rewording. The architecture page calls it the fifth skill, which is not a role, and says the roles lose nothing without it.

# The rules

`references/rules.md` gives thirteen rules, each with a before and an after.

1. Put the actor first and the verb early.
2. Give every sentence a verb.
3. Keep one idea to a sentence and one topic to a paragraph, and split a sentence past forty words or a paragraph past 150.
4. Say the step, then the reason.
5. Use no dash as punctuation.
6. Turn a long aside into a sentence of its own.
7. Turn a run of conditions into a list.
8. Use the same word for the same thing.
9. Choose the plain word, say literally what happens, and keep each technical term exact.
10. Cut words that carry nothing.
11. Say what is, and what to do.
12. Open each page by saying who it is for.
13. Report what you cannot fix.

Since 0.55.0 `references/rules.md` also gives a method for a paragraph with two topics, the rule before its exception, pointing words as names, and the quiet figures of motion.

A last section of `references/rules.md`, apart from the thirteen, says where a line ends in the source. In the bundle that is one line for each paragraph and each list item, as ktl-librarian writes it. Outside the bundle the host's layout holds: one line per paragraph, one sentence per line, or a fixed column. A file's layout changes only when the person asks.

# Which concepts it may reword

It rewords only a body an agent wrote that no person has confirmed. It never rewords:

- `index.md`, `log.md` or `diataxis.md`;
- a concept whose `generated.by` starts `human:`;
- a concept with a `human:` event under `verified`;
- a retired concept;
- a concept whose frontmatter the script cannot read.

A concept with no `generated.by` is reworded only when a person names it. Naming a confirmed concept does not unlock it, because a confirmation is a person's time spent against a source and a rewording must not spend it.

# What a rewording never changes

- A fact, a name, a number, a command or a piece of code.
- A link target, or a heading.
- Text in quotation marks.
- An RFC 2119 keyword, or the strength of an instruction.
- Any byte of frontmatter.
- The `lokf:related` region, the `## Open questions` section, and every fenced block.

# Steps

0. **Preflight**: run the preflight and the conventions script first, as every skill that touches the bundle does. The skill never opens `.lokf/feedback.md`.
1. **Report**, always and read-only. `prose-check.py --bundle .lokf/knowledge` says which files may be reworded. The style checks `dash`, `long`, `paragraph`, `sentences` and `words` run over those, with `unseen` for a character no reader sees. Since 0.55.0 `sentences` reports a paragraph of more than eight sentences, and the listed words include "outright" and "at all". The script runs through `uv run`, or a python3 of 3.9 or later, never bare `python`. Then the agent reads them, because only a reader sees a late verb.
2. **Reword**, only in a live session on a request addressed to the skill. Keep the earlier text, work one file at a time, change the wording only, lay out what it rewords the way the file's project does, and leave what cannot be fixed.
3. **Prove** that only the wording changed, with `prose-check.py --against HEAD` or `--before <copy>`. A finding names something other than wording that differs, such as a character no reader sees that the rewording added, and the agent undoes it.
4. **Log** one **Prose** line in `log.md`.
5. **Hand off** a change scoped to `.lokf/`. Give the counts before and after, the words before and after from the script's `OK` line, each sentence left alone, each concept skipped, and what no script proved: that the meaning held. End with a **For the CURATOR** section.

# Outside the bundle

The bundle is where the skill works. A person may still name another Markdown file. `references/other-files.md` says what never to touch, how to list the concepts derived from that file, and what a rewording costs them. It also says how to find the host's layout. Since 0.55.0 the script reads a script too: given a `.sh`, `.bash`, `.py`, `.yaml`, `.yml` or `.toml` file, or a justfile, it reads the `#` comments and, in Python, the docstrings, each block of comment lines as a paragraph, and never the code. `references/other-files.md` makes the block a change touches, not the lines it adds, the unit of a comment review.

# Younger readers

A text for a younger reader is a retelling, not a rewording. It leaves detail out and explains terms, so it is a new file and the original stays as it is. In the bundle, ktl-librarian writes it and this skill checks it. Outside the bundle, this skill writes it beside a file a person names, such as `README.en-simple.md` beside `README.md`. It adds one sentence to the original that points to it.

A pass for dyslexic readers is a rewording at tighter limits. `references/young-readers.md` gives the two bands of age, 8 to 12 and 13 to 18, and the pass for dyslexic readers, with the limits of each (since 2026-10-11). The script supports the work:

- `prose-check.py --audience 8-12`, `13-18` or `dyslexia` sets the band's limits, counts the sentences in each paragraph, and notes the page's Automated Readability Index. A page that opens "This page is for readers aged 13 to 18." is held to that band with no flag.
- Under a band, the script reports `i.e.`, `vs`, `cf.`, `etc.` and `via`. It also notes the words a page uses that the VOA Learning English word book does not hold. The word book is in the public domain and sits in the skill's `assets/` folder with its credit.
- `--derived-from ADULT YOUNG` reports a number, link, code span, quotation, HTML tag or fenced block that the retelling holds and the text it retells does not, and notes what it left out.
- `--bundle` reports the band the curation policy's `Younger readers:` line declares, as `audience: 8-12`, or `audience: none declared`.
