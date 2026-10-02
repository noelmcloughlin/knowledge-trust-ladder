---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/three-lines-of-defence
title: "Three lines of defence: where each role sits, and what an auditor can check"
description: "How the librarian, curator, registrar, sidecar, docent and ktl-prose fit the Institute of Internal Auditors' Three Lines Model: who is accountable for a claim, what a machine checks, what can be examined afterwards, and what the model's critics say."
genre: explanation
resource: docs/three-lines.md
sources:
- resource: docs/three-lines.md
- resource: docs/three-lines-critics.md
- resource: README.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
about:
  - https://knowledge-trust-ladder.example/knowledge/glossary/trust-label
relatedTo:
  - https://knowledge-trust-ladder.example/knowledge/explanation/why-four-roles
  - https://knowledge-trust-ladder.example/knowledge/explanation/why-a-registrar-role
  - https://knowledge-trust-ladder.example/knowledge/policies/threat-model
---

# Overview

Regulated industries use the three lines of defence to say who owns a risk, who keeps the rules, and who checks independently. `docs/three-lines.md` places each role in the Institute of Internal Auditors' Three Lines Model, updated in 2020 and reissued as a Statement of Position in 2026. The bundle was not built to the model, but each role fits, and the page answers the three questions a governance reader brings: who is accountable for a claim, what a machine checks, and what can be examined afterwards.

# The lines

- **First line**, which owns the work and its risk: the librarian derives every record from a source it names and marks what it cannot settle as a draft with an open question. The curator, a named person, decides what the team accepts as true. Maker and checker: the agent cannot vouch, and the person does not derive.
- **Second line**, which ensures compliance without owning the content: the registrar keeps every record well-formed, and its `provenance` job ties each new `human:` verdict to that person's approval of the pull request or their signature on the commit. It never judges truth.
- **Third line**, independent assurance: the bundle ships the evidence an independent reviewer needs, and not the review, because assurance is independent only when it comes from someone other than the authors.

The docent sits outside the lines, where the reader does, and reports what it could not answer back to the librarian as untrusted input. The sidecar lays down the tools and the gate. `ktl-prose` sits on the maker's side of the first line: it rewords what the librarian wrote before a person confirms it, writes no `generated` record, and `log.md` and git record the pass. Above the lines sits a governing body, the owners of the repository, whose instruments are the organisation's rules for AI-assisted work and the curation policy.

# Lines are roles, not people

The IIA's own text says the lines "are not intended to denote structural elements but a useful differentiation in roles". A bundle does not decide who plays each line; the organisation that adopts it does. The tooling holds the lines apart either way: the curator's identity comes from the forge, never from the person, and the gate accepts a `human:` verdict only on that person's approval or signature.

# What an auditor can check

Every trust label is computed from the frontmatter on each read and never stored, so a label cannot be asserted, only earned. The page lists where each auditor's question is answered.

- Where did this come from? `resource` and `sources`.
- Who produced the current text? `generated`.
- Who confirmed it? `verified`.
- Which state of the source? `revision`, proposed for lokf 0.9.0.
- Was that really them? The `provenance` job's log.
- When must it be looked at again? `stale_after`.
- What changed? `log.md`, and git.

It also states four limits, among them that a confirmation records who and when, not what the person read.

# The critics

`docs/three-lines-critics.md` quotes the model's critics from their own texts: the UK Parliamentary Commission on Banking Standards, academics, and the research on human oversight of automated systems. It gives each criticism one of three verdicts: met by construction, answered in part, or not the bundle's role. Every gap left open is collected by owner under what remains to do.
