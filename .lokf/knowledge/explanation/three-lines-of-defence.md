---
type: Explanation
id: https://lokf-agent-skills.example/knowledge/explanation/three-lines-of-defence
title: Three lines of defence - where each role sits, and what an auditor can check
description: Reading the librarian/curator/registrar/docent cast through the Three Lines Model - who owns a claim, what is checked mechanically, and what a person can examine afterwards - and the three limits on what that evidence actually shows.
genre: explanation
resource: docs/three-lines.md
generated:
  by: process:lokf-librarian
  at: "2026-09-14T23:10:00Z"
status: draft
about:
- https://lokf-agent-skills.example/knowledge/explanation/why-four-roles
- https://lokf-agent-skills.example/knowledge/explanation/why-a-registrar-role
relatedTo:
- https://lokf-agent-skills.example/knowledge/policies/ai-covenant
- https://lokf-agent-skills.example/knowledge/glossary/trust-label
verified:
- by: process:lokf-librarian
  at: "2026-09-14T23:10:00Z"
---

# Overview

Added 2026-09-14: the README gained a "Three lines of defence" section
pointing at this page. LOKF was not designed from the
[Three Lines Model](https://www.theiia.org/en/content/position-papers/2020/the-iias-three-lines-model-an-update-of-the-three-lines-of-defense/) -
the model regulated industries use to say who owns a risk, who makes sure
the rules are kept, and who checks independently - but the cast maps onto it
cleanly. First line: the **librarian**, who derives every record from a
named source and marks what it cannot settle `status: draft`, and the
**curator**, a named person who decides what the team accepts as true -
maker and checker, since the agent cannot vouch and the person does not
derive. Second line: the **registrar** - `lokf validate` on every change and
in CI, plus the LOKF Registrar Obsidian plugin - which keeps records
well-formed and ties a `human:` verdict to that person's approval or
signature, without judging truth. Third line, independent assurance, is not
shipped and could not be - independence means it does not come from the same
authors - so what ships instead is the evidence itself.

The **docent** sits outside the lines, where the reader does: what it cannot
answer becomes an untrusted report in `.lokf/feedback.md`. Lines are roles,
not headcount - the model's own 2020 revision says so - so a solo maintainer
can still hold them apart: the curator's identity comes from the forge
(`gh api user`), never from git config or the conversation, and the gate
accepts a `human:` verdict only on that person's own approval or signed
commit, an Environment's required reviewers being the one logged exception.

An auditor's five questions each have a fixed place to look: provenance in
`resource`/`sources[].resource`/`derivedFrom`; who produced the current text
and when in `generated.by`/`generated.at`; who confirmed it and when in
`verified[].by`/`verified[].at`; whether that confirmation is really tied to
the named person in the `provenance` gate's log (GitHub's verdict on the
review or signature, not the runner's); and when it must be looked at again
in `stale_after`. Three limits bound what that evidence proves: a
confirmation records who and when, not what the source said at that instant
(pinned by the commit when the source is in-repository, by nothing when it
is a URL); the registrar gate checks identity, not entitlement - that
`human:ada` is ada, not that ada was the right person to confirm that
concept; and a GitHub Environment attestation records that someone with
settings access approved, not that anything was read.
