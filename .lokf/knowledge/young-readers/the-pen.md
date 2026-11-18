---
type: GlossaryTerm
id: https://w3id.org/ktl/knowledge/young-readers/the-pen
title: The pen, for readers aged 13 to 18
description: The pen retold for readers aged 13 to 18, the script that is ktl-librarian's only way to write the bundle, and what it refuses.
definition: The name the docs give `knowledge-apply.sh`, the script through which ktl-librarian writes every change to the bundle.
genre: reference
resource: skills/ktl-sidecar/templates/scripts/knowledge-apply.sh
derivedFrom:
  - https://w3id.org/ktl/knowledge/glossary/the-pen
sources:
  - resource: .lokf/knowledge/glossary/the-pen.md
about:
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
tags:
  - audience-13-18
generated:
  by: process:ktl-librarian
  at: "2026-11-18T08:53:06Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-11-17T22:28:06Z"
relatedTo:
  - https://w3id.org/ktl/knowledge/glossary/registrar
---

This page is for readers aged 13 to 18. It retells [[the-pen]] in shorter words. The full page has every detail.

# What is the pen?

**The pen** is the name the docs give `knowledge-apply.sh`. It is the script through which ktl-librarian writes every change to the bundle ([[knowledge-bundle]]).

# How does the librarian use it?

ktl-librarian never edits a file under `.lokf/knowledge/` by hand. It describes each change as an operation in `.lokf/patch.yaml`. The pen checks every operation. Then it writes the files, or it refuses the whole file and writes nothing.

# What does the pen do with a change?

- It stamps `generated` from the clock.
- It keeps a concept's `description` equal to its two index bullets.
- It files each line in `log.md`.
- It runs `lokf validate` on every concept a patch would write, when `.lokf/.venv` holds the toolkit. It does this with `--dry-run` too.
- It moves a feedback entry the librarian handled into `.lokf/questions.md`. A patch handles ten entries at most.

# What does the pen refuse?

The pen refuses:

- a `human:` actor, which marks a person's record;
- a rewrite of text a person wrote;
- the deletion of a concept a person confirmed or left a note on;
- a `question` or a `delete` on a concept a person retired;
- a change to the concept that replaced a retired one. Only a person names it;
- a `log` line that starts with `**Curation**` or `**Deprecation**`. ktl-curator writes those two lines for a person.

It also refuses a patch that would add, change or remove a person's record. That record is each entry whose `by` names a person, with every key it holds. So an exclusion a person decided keeps its `resource` and `reason`. The record is also each note a person left, with the lines under it and its place in the order.

# What happens in the scheduled run?

In the scheduled run, the wrapper applies the patch file after the agent has finished. It refuses a run in which the agent changed any other file.

In the agent's step, the pen only checks the patch. The wrapper sets `KNOWLEDGE_PEN_DRY_RUN_ONLY`. So a run without `--dry-run` stops with exit code 2. It writes nothing, and it leaves the patch file for the wrapper.

# What exit codes does the pen give?

The pen ends with one of three exit codes:

- 0: it applied the patch, or with `--dry-run` it would apply it.
- 1: it found problems, and it wrote nothing.
- 2: there is no bundle, no patch file, a file that is not YAML, or no runner. It also gives 2 on a run without `--dry-run` in the agent's step of a scheduled run.

# What can the librarian tell the reviewer?

A patch may also carry `handoff`. These are up to ten lines for the person reviewing the change, in the librarian's own words. The pen holds each one to one line of printable text, and writes none of them to the bundle. The scheduled pull request shows them under *From the librarian*.

# Who else writes the bundle?

The pen is the librarian's only way to write the bundle. A person writes the curator's verdicts another way, through ktl-curator or the KTL Curator plugin. The architecture page names the pen as the [[registrar]] for the librarian.

## Open questions

- 2026-10-27, human:noelmcloughlin: carry over four things `glossary/the-pen.md` says that this retelling leaves out: the `lokf validate` run (:11); moving feedback into `.lokf/questions.md` (:12); the scheduled-run wrapper and `KNOWLEDGE_PEN_DRY_RUN_ONLY` (:16); the `handoff` lines (:16). The :NN numbers count lines of `glossary/the-pen.md` after its frontmatter.
- 2026-11-13, human:noelmcloughlin: add exit code, and tell the human to remove release number 0.55.0 as versions in user facing prose are unnecessary
