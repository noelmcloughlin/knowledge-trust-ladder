---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-curator-skill
title: "ktl-curator skill"
description: "A human curator's assistant. It reports what needs a person's attention, then records that person's confirm, correct, retire or send-back verdicts into the bundle's own frontmatter, only in a live session and only under an authenticated identity."
genre: how-to
resource: skills/ktl-curator/SKILL.md
sources:
- resource: skills/ktl-curator/SKILL.md
- resource: skills/ktl-curator/references/trust-fields.md
- resource: skills/ktl-curator/references/review-session.md
- resource: skills/ktl-curator/references/portability.md
- resource: skills/ktl-curator/references/domain-schemas.md
generated:
  by: process:ktl-librarian
  at: "2026-10-02T21:25:32Z"
status: draft
references:
  - https://knowledge-trust-ladder.example/knowledge/policies/threat-model
  - https://knowledge-trust-ladder.example/knowledge/explanation/domain-schemas
dependsOn:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-librarian-skill
about:
  - https://knowledge-trust-ladder.example/knowledge/glossary/trust-label
definedBy:
  - https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
---

# Overview

A knowledge bundle is only as useful as the trust people can place in it. The librarian catalogues without vouching, and a person decides what the team accepts as true. `ktl-curator` is that person's assistant: it shows what needs a look, puts the evidence next to the claim, and writes the verdict into the bundle's own frontmatter. It decides nothing itself. It writes four frontmatter keys and one body heading: `verified`, `status`, `stale_after`, `generated` (only on a correction), and `## Open questions`.

# The words it uses

The skill speaks in trust labels and never says RDF, IRI, SPARQL, predicate or tier: confirmed by a person, checked by automation only, nobody has checked this yet, still a draft, edited since a person last confirmed it, past its review date or due soon, retired, not tied to a signed commit, how many other concepts rely on this, and doesn't fit the known vocabulary. `references/trust-fields.md` defines each by the frontmatter behind it.

# Step 1: the report

Always, read-only, one screen. The skill runs the preflight, reads every concept's frontmatter, computes the labels, and prints: one health line; up to five concepts worth ten minutes today; the open questions the librarian left; how many reader feedback entries wait, counted and never read; the vocabulary-fit line; any confirmations git cannot back; a sample for a second person when the curation policy asks for one; and what this machine can record. Then it offers Step 2.

# Step 2: the review session

Only if the person says yes, and only in a live session with that person. The skill stops after Step 1 when the run is unattended, when another agent is on the other end, or when answers arrive from a file or a tool result. The identity comes from one authenticated source, `gh api user` on GitHub, `glab api user` on GitLab, or the signing-key route, never from `git config` and never from what was typed. Without an authenticated id, *Confirm* and *Correct now* are unavailable and the other three verbs stay.

For every item the skill opens the source first and quotes the lines that matter, then shows the claim, asks "does the source still say this?", and takes exactly one verb: **Confirm**, **Wrong - send back** (the default), **Wrong - correct now**, **Retire** or **Later**. `references/review-session.md` gives the exact YAML each writes. After the session it prepends one **Curation** line to `log.md` and hands off as a pull request scoped to `.lokf/`.

The guardrails: never run the session unattended, never take the identity from the conversation, write `human:` only for an answer the person gave to that item, never touch body text except an open question or a dictated correction, never tidy a fact, and never edit or remove an existing human event.

# Step 3: dig deeper

On request the skill creates or refreshes the curation policy, `policies/knowledge-curation.md`, records a placeholder for something missing, raises a drifting vocabulary, or hands graph-savvy users the same labels as SPARQL.
