---
type: GlossaryTerm
id: https://knowledge-trust-ladder.example/knowledge/glossary/the-pen
title: The pen
description: "The name for `knowledge-apply.sh`, the only way ktl-librarian writes the bundle: it applies the operations in `.lokf/patch.yaml`, stamps `generated`, keeps the index in step, and refuses a `human:` actor."
definition: The name the README and the docs give `knowledge-apply.sh`, the script through which ktl-librarian writes every change to the bundle. The librarian describes each change as an operation in `.lokf/patch.yaml`, and the pen checks every operation and writes the files, or writes nothing.
genre: reference
resource: skills/ktl-sidecar/templates/scripts/knowledge-apply.sh
sources:
- resource: README.md
- resource: docs/for-the-curious.md
- resource: skills/ktl-librarian/references/patch.md
about:
- https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-librarian-skill
- https://knowledge-trust-ladder.example/knowledge/explanation/why-a-registrar-role
generated:
  by: process:ktl-librarian
  at: "2026-10-05T12:41:36Z"
status: draft
---

# Overview

*The pen* is the name the README and the docs give `knowledge-apply.sh`. ktl-librarian never edits a file under `.lokf/knowledge/` by hand. It describes each change as an operation in `.lokf/patch.yaml`, and the pen checks every operation and writes the files, or refuses the whole file and writes nothing.

The pen stamps `generated` from the clock, keeps a concept's `description` equal to its two index bullets, files each line in `log.md`, and moves a feedback entry the librarian handled into `.lokf/questions.md`, ten to a patch at most. It refuses a `human:` actor, a rewrite of text a person wrote, and the deletion of a concept a person confirmed or left a note on. It also refuses a patch after which any concept it writes would hold a person's record other than the one the file held: a `human:` event or a person's note added, changed or removed, however the operations spelt it.

In the scheduled run, the wrapper applies the patch file after the agent has finished, and refuses a run in which the agent changed any other file. A patch may also carry `handoff`, up to ten lines for the person reviewing the change, in the librarian's own words. The pen holds each to one line of printable text and writes none of it to the bundle, and the scheduled pull request shows them under *From the librarian*.

The pen is the librarian's only way to write the bundle, and the bundle has other writers: a person writes the curator's verdicts through ktl-curator or the KTL Curator plugin. The README names the pen as the registrar for the librarian.
