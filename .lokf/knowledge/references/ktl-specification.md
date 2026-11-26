---
type: Reference
id: https://w3id.org/ktl/knowledge/references/ktl-specification
title: KTL specification
description: "The Knowledge Trust Ladder (KTL) specification, `SPEC.md`, version 0.2, a draft: the rules KTL adds to a LOKF bundle. It states the ladder, who writes each record, the eighteen conventions, what counts as a person's confirmation, how each trust label is computed, and what conformance means."
genre: reference
resource: SPEC.md
sources:
  - resource: SPEC.md
    id: spec.md
    excerpt: "**Version 0.2, a draft.** It is written for OKF 0.2 and LOKF 0.2, the versions a bundle declares in its root `index.md`."
  - resource: skills/ktl-website/references/inputs.md
about:
  - https://w3id.org/ktl/knowledge/glossary/trust-ladder
  - https://w3id.org/ktl/knowledge/glossary/trust-label
  - https://w3id.org/ktl/knowledge/glossary/the-pen
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
  - https://w3id.org/ktl/knowledge/glossary/sidecar
references:
  - https://w3id.org/ktl/knowledge/references/okf-specification
  - https://w3id.org/ktl/knowledge/references/lokf-specification
  - https://w3id.org/ktl/knowledge/policies/threat-model
  - https://w3id.org/ktl/knowledge/policies/versioning
  - https://w3id.org/ktl/knowledge/playbooks/repository-validation
  - https://w3id.org/ktl/knowledge/playbooks/ktl-librarian-skill
  - https://w3id.org/ktl/knowledge/playbooks/ktl-curator-skill
  - https://w3id.org/ktl/knowledge/playbooks/ktl-docent-skill
  - https://w3id.org/ktl/knowledge/playbooks/ktl-sidecar-skill
  - https://w3id.org/ktl/knowledge/playbooks/ktl-website-skill
generated:
  by: process:ktl-librarian
  at: "2026-11-18T00:03:28Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-11-26T02:26:42Z"
---

# Overview

`SPEC.md`, at the repository's root, is the Knowledge Trust Ladder (KTL) specification. It is version 0.2, a draft, written for OKF 0.2 and LOKF 0.2, the versions a bundle declares in its root `index.md`.[^spec.md] It states the rules that KTL adds to a [LOKF](lokf-specification.md) knowledge bundle. It is for anyone who writes a program that reads or writes a bundle KTL keeps, and for anyone who must say what *confirmed by a person* means there.

The page calls KTL an [OKF](okf-specification.md) runtime. OKF defines the format and prescribes no runtime, and LOKF gives each field of that format its meaning. The specification defines no field, type or relation, and a field KTL needs is asked of LOKF. It states what neither specification states, and what more than one program applies. How each role does its work is in that role's skill, and is no part of the page.

# What it states

- **The ladder** (section 3). A concept that is not retired stands on one of three rungs: nobody has checked this yet, checked by automation only, and confirmed by a person. Four rules move a concept on the [trust ladder](../glossary/trust-ladder.md): an event raises it, an edit drops it, everything else flags it, and a retirement takes it off. No rung and no label is stored.
- **The sidecar's files** (section 4). A program finds the bundle, the patch file, the reader feedback, the ledger of questions, the curators' keys and the mirror at fixed paths. `index.md` and `log.md` are reserved in every folder of the bundle, and `diataxis.md` at the bundle's root alone.
- **Who writes what** (section 5). Every write to the bundle goes one of four ways: an agent's patch file, which [the pen](../glossary/the-pen.md) applies, the curator's verdict, ktl-prose's rewording of a body, and the KTL Registrar plugin's block and map. The section defines the actors, the pen's operations and the refusals that keep a person's record, the curator's verdicts, and the shape of a reader's entry and of a ledger line.
- **The conventions** (section 6). A bundle KTL keeps holds to eighteen conventions beyond the format, which `knowledge-conventions.sh` checks. Conventions 2, 3, 8, 10 and 18 are stricter than the format, so a bundle written to the letter of OKF may fail them. The page calls that a policy of the gate, and no defect in the bundle.
- **A person's confirmation** (section 7). A `human:<id>` event claims that a named person checked a concept against its source, and nothing in the format proves the claim. A gate accepts it only with evidence from outside the bundle: an approving review from that account that still stands, or that person's signature on each commit that added or removed the event. A repository that cannot sign and has nobody else to approve may turn on a third route, the attestation. A person's record is never removed without that person.
- **Trust labels** (section 8). The section gives the rule and the fields for each [trust label](../glossary/trust-label.md), the inputs a label is computed from, and the order of the curator's queue. A program computes each label on every read and stores none.
- **Conformance** (section 10). The section says when a bundle, a program that writes a bundle, a gate and a program that reports trust conform. `tests/conformance/reader/` holds a bundle with one concept for each label that needs neither git nor today's date, and `expected.json` beside it holds what such a program reports of it.

Sections 3 to 8 and section 10 are rules. The examples, section 9 and section 12 explain and add no rule. Section 9 covers security, and points to [the threat model](../policies/threat-model.md) for each measure and its reasons.

# Versions

The version of the page is `<major>.<minor>`, as OKF's and LOKF's are, and it matches theirs. KTL's releases, `vMAJOR.MINOR.PATCH`, are a separate track, which the [versioning policy](../policies/versioning.md) covers. A release may change a rule of the page, and the changelog records each change. A convention keeps its number, and a new one takes the next number, because other pages cite the numbers.

# The copies of its rules

The page is the source for its rules. Each skill is installed alone, so the scripts and the skills' reference pages carry copies, and section 12 names each copy and what applies the rule:

- Section 5.2 is applied by the pen, `knowledge-apply.sh`, and copied in `skills/ktl-librarian/references/patch.md`, which the [ktl-librarian playbook](../playbooks/ktl-librarian-skill.md) covers.
- Section 5.3 is applied by ktl-curator and the KTL Curator plugin, and copied in `skills/ktl-curator/references/review-session.md`, which the [ktl-curator playbook](../playbooks/ktl-curator-skill.md) covers.
- Section 5.4 is applied by `knowledge-feedback.sh` and the pen, and copied in `skills/ktl-docent/references/feedback.md`, which the [ktl-docent playbook](../playbooks/ktl-docent-skill.md) covers.
- Sections 6 and 7 are applied by `knowledge-conventions.sh`, the `provenance` job of `knowledge-registrar.yaml` and `knowledge-provenance.sh`, and copied in `skills/ktl-sidecar/references/gate.md`, which the [ktl-sidecar playbook](../playbooks/ktl-sidecar-skill.md) covers.
- Section 8 is applied by `knowledge-report.sh` and the KTL Curator plugin, and copied in `skills/ktl-curator/references/trust-fields.md`.

Contract check 24, in `scripts/validate-repository.sh`, holds four copies to the page word for word: the conventions in the script's header, the operations and the refusals in patch.md, and the label table and the queue's order in trust-fields.md. The [repository validation playbook](../playbooks/repository-validation.md) lists the check. `tests/test_conformance.py` holds `knowledge-report.sh` to the expected values of section 10.

The project's website shows a root `SPEC.md` as the page `/spec/`, which the [ktl-website playbook](../playbooks/ktl-website-skill.md) describes.

[^spec.md]: SPEC.md, the line under the title
