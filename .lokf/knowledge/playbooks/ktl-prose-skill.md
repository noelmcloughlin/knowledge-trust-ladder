---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-prose-skill
title: ktl-prose skill
description: The librarian's copy editor. It rewords the body of a concept an agent wrote, in plain English, before a person confirms it, changing the wording and never a fact or a frontmatter byte, and its script proves that only the wording changed.
genre: how-to
resource: skills/ktl-prose/SKILL.md
sources:
- resource: skills/ktl-prose/SKILL.md
- resource: skills/ktl-prose/references/rules.md
- resource: skills/ktl-prose/references/other-files.md
- resource: skills/ktl-prose/scripts/prose-check.py
- resource: README.md
references:
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-curator-skill
- https://knowledge-trust-ladder.example/knowledge/policies/threat-model
dependsOn:
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-librarian-skill
about:
- https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
definedBy:
- https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
generated:
  by: process:ktl-librarian
  at: "2026-10-05T12:41:36Z"
status: draft
verified:
- by: process:ktl-librarian
  at: "2026-10-03T13:27:24Z"
---
# Overview

A museum edits its labels before the exhibition opens. `ktl-prose` does that for the `.lokf/` knowledge bundle: it rewords what the librarian wrote, in plain English, before a person confirms it. It changes the wording and never a fact. A curator can only confirm a claim they can read. The skill is a copy editor, not an author: the librarian stays the maker of every concept it derived, so `generated` keeps naming it, and `log.md` and git record the rewording. The README calls it the fifth skill, which is not a role, and says the roles lose nothing without it.

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

# Which concepts it may reword

Only a body an agent wrote that no person has confirmed. It never rewords `index.md`, `log.md` or `diataxis.md`, a concept whose `generated.by` starts `human:`, a concept with a `human:` event under `verified`, a retired concept, or one whose frontmatter the script cannot read. A concept with no `generated.by` is reworded only when a person names it. Naming a confirmed concept does not unlock it, because a confirmation is a person's time spent against a source and a rewording must not spend it.

# What a rewording never changes

- A fact, a name, a number, a command or a piece of code.
- A link target, or a heading.
- Text in quotation marks.
- An RFC 2119 keyword, or the strength of an instruction.
- Any byte of frontmatter.
- The `lokf:related` region, the `## Open questions` section, and every fenced block.

# Steps

1. **Preflight**, as every skill that touches the bundle does.
2. **Report**, always and read-only. `prose-check.py --bundle .lokf/knowledge` says which files may be reworded; the style checks `dash`, `long`, `paragraph` and `words` run over those, with `unseen` for a character no reader sees; then the agent reads them, because only a reader sees a late verb.
3. **Reword**, only in a live session on a request addressed to the skill. Keep the earlier text, work one file at a time, change the wording only, and leave what cannot be fixed.
4. **Prove** that only the wording changed, with `prose-check.py --against HEAD` or `--before <copy>`. A finding names something other than wording that differs, such as a character no reader sees that the rewording added, and the agent undoes it. The script enforces the table above with no override.
5. **Log** one **Prose** line in `log.md`.
6. **Hand off** a change scoped to `.lokf/`, with the counts before and after, the words before and after from the script's `OK` line, each sentence left alone, each concept skipped, and what no script proved: that the meaning held. End with a **For the CURATOR** section.

# Outside the bundle

The bundle is where the skill works. A person may still name another Markdown file. `references/other-files.md` says what never to touch, how to list the concepts derived from that file and what a rewording costs them, and how to apply the rules by hand to comments in scripts and workflows.
