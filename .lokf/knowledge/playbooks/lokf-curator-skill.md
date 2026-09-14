---
type: Playbook
id: https://lokf-agent-skills.example/knowledge/playbooks/lokf-curator-skill
title: lokf-curator skill
description: A human curator's assistant - reports what needs a person's attention, then records that person's confirm/correct/retire/send-back verdicts into the bundle's frontmatter.
genre: how-to
resource: skills/lokf-curator/SKILL.md
generated:
  by: process:lokf-librarian
  at: "2026-09-14T11:30:00Z"
status: draft
dependsOn:
- https://lokf-agent-skills.example/knowledge/playbooks/lokf-librarian-skill
about:
  - https://lokf-agent-skills.example/knowledge/glossary/trust-label
definedBy:
- https://lokf-agent-skills.example/knowledge/references/agent-skills-specification
verified:
- by: process:lokf-librarian
  at: "2026-09-14T11:30:00Z"
---

# Overview

Runs **a little, regularly**. Step 1 is always a read-only one-screen report
computed from frontmatter alone (no toolkit needed): a health line, at most
five items "worth ten minutes today", the librarian's open questions, waiting
reader feedback, and vocabulary fit. Step 2 is an opt-in review session that
shows the source *before* the claim and takes one verb per item. Step 3 covers
the curation policy, gap intake, and domain-schema guidance.

**Vocabulary fit counts against the host's vocabulary, not only LOKF's**
(stated 2026-09-14): where `.lokf/justfile` validates with `--schema
<slug>.yaml`, the skill reads that file and counts its `Concept` descendants
as known - the same widening the librarian's Rule 3 applies, and the reason
the line goes quiet once a team adopts a domain schema instead of naming
every domain class a misfit for good. The label is now "doesn't fit the known
vocabulary", matching what the LOKF Curator plugin already says.

The curation policy's table is read **tolerantly** (`references/review-session.md`,
stated 2026-09-14): rows name classes in prose, so the match ignores spaces
and plural form - "Glossary terms" is `GlossaryTerm`, "people" is `Person` -
and an unknown class binds nothing. A host extending the vocabulary sets
intervals for its own classes the same way. Stated because the LOKF Curator
plugin implements this document and matched literally, ignoring four rows of
the skill's own template.

It deals in **judgments a person made, never facts it derived**. It writes only
`verified` (human events), `status`, `stale_after`, `generated` (on a dictated
correction), and an `## Open questions` section - and never without an explicit
per-item answer. There is deliberately no "confirm everything".
