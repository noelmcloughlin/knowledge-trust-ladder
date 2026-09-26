---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-docent-skill
title: ktl-docent skill
description: The reader's side - answers questions from the bundle first with each concept's trust label, falls back to the repository deliberately, and records misses and disagreements for the librarian.
genre: how-to
resource: skills/ktl-docent/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-09-26T19:52:21Z"
status: draft
dependsOn:
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-librarian-skill
about:
  - https://knowledge-trust-ladder.example/knowledge/glossary/trust-label
definedBy:
- https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
references:
  - https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-curator-skill
  - https://knowledge-trust-ladder.example/knowledge/policies/threat-model
verified:
- by: process:ktl-librarian
  at: "2026-09-26T19:52:21Z"
---

# Overview

Runs **whenever anyone asks**. Bundle first: read `knowledge/index.md`, open
one to three candidate concepts, widen along typed relations rather than by
grepping, and verify exact values (versions, endpoints, paths) at the
concept's `resource` before stating them. Every answer carries a footing -
which concepts it rests on and how far each has been trusted, with the
`revision` a person's confirmation was checked against where the event
records one ("against 3f9c2a1", a commit hash cut to seven characters). One switch,
set by a person in the curation policy (`policies/knowledge-curation.md`,
the line `Evidence first: yes`), reverses the order for any concept not yet
confirmed by a person: the quoted source first, then the answer that rests
on it. No policy, no line, or another value means the usual order, and the
reader cannot switch it from the conversation.

It is **read-only on `knowledge/`**. Its single write is `.lokf/feedback.md`,
after asking once per session: a **Miss** (a question the bundle could not
answer, plus where the answer was found) or a **Disagreement** (a concept
versus what its source now says). It makes that write by running
`.lokf/scripts/knowledge-feedback.sh` (2026-09-23), which inserts the entry
newest first and prints only a kind, a date and a count, so the reports other
readers left in that file never enter the session. Before the script, an
entry meant reading the file and rewriting it, and the only guard was a line
of prose telling the agent to ignore what it had just read. The librarian
consumes and clears those entries on its next run, which closes the loop from
reader back to bundle.
An entry names the asker only from an authenticated login - `gh api user`,
`glab api user`, or the signing-key route the curator describes - and is
attributed to `docent` alone without one; the preflight's identity line
says which applies (2026-09-17), and a reader is shown nothing else from
the preflight - a missing bundle is the one thing worth a sentence.
It never carries a secret, credential, token, or connection string into an
answer or a feedback entry, even to explain where one was found - it names
the file and line and the kind of value, never the value itself, since the
scheduled workflow commits `feedback.md` into a pull request that can be
public.

**The repository fallback, the second Snyk W011 finding (acknowledged 2026-09-25).** Falling back to the repository means opening text the skill did not author, and its guardrails treat that text as something to quote or summarize, never as instructions, even when a file is phrased as one. What contains it is what the skill cannot do: it never edits `.lokf/knowledge/`, and its one write is a feedback entry through the script, after asking once per session, which the script holds to one line and one of two kinds. The Copilot variant cannot write the file at all and hands the reader the line to paste instead. The [threat model](../policies/threat-model.md) lists this surface and what it does not cover.
