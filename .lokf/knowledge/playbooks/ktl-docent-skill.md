---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-docent-skill
title: ktl-docent skill
description: "The reader's side: it answers questions from the bundle first, with each concept's trust label, falls back to the repository when the bundle cannot answer, and records misses and disagreements for the librarian."
genre: how-to
resource: skills/ktl-docent/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-06T11:10:52Z"
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
  at: "2026-10-06T11:10:52Z"
sources:
- resource: skills/ktl-docent/SKILL.md
- resource: skills/ktl-docent/references/answering.md
- resource: skills/ktl-docent/references/feedback.md
- resource: README.md
- resource: CHANGELOG.md
---

# Overview

ktl-docent runs **whenever anyone asks**. Bundle first: read `knowledge/index.md`, open one to three candidate concepts, widen along typed relations rather than by grepping, and verify exact values (versions, endpoints, paths) at the concept's `resource` before stating them. Every answer carries a footing: which concepts it rests on and how far each has been trusted.

Each label comes from the skill's own copy of `knowledge-report.sh`, run from the repository as `labels <path>...`, and is worked out by hand from the label table only where that copy is missing. A retired concept carries no other label, and *edited since a person last confirmed it* takes the place of *confirmed by a person*, because the person confirmed an earlier text (2026-10-05). A confirmation's label carries the `revision` it was checked against where the event records one ("against 3f9c2a1", a commit hash cut to seven characters).

A person can set one switch in the curation policy: the line `Evidence first: yes` in `policies/knowledge-curation.md`. It reverses the order for any concept not yet confirmed by a person, or edited since that confirmation: the quoted source first, then the answer that rests on it. No policy, no line, or another value means the usual order, and the reader cannot switch it from the conversation.

It is **read-only on `knowledge/`**. Its single write is `.lokf/feedback.md`, after asking once per session: a **Miss** (a question the bundle could not answer, plus where the answer was found) or a **Disagreement** (a concept versus what its source now says). It makes that write with `knowledge-feedback.sh` (2026-09-23), which inserts the entry newest first and prints only a kind, a date and a count, so the reports other readers left in that file never enter the session. Before the script, an entry meant reading the file and rewriting it, and the only guard was a line of prose telling the agent to ignore what it had just read. The librarian consumes those entries on its next run, and its apply script moves each one into `.lokf/questions.md`, a ledger only programs read, which closes the loop from reader back to bundle.

**Its own scripts, never the repository's (2026-10-05).** Both scripts are copies in the skill's own `scripts/` folder, byte-identical to ktl-sidecar's templates. The skill never runs the copies under `.lokf/scripts/`, because anyone who can commit to a repository can change those, and a question is no reason to run its code. Where its own copies are missing, it works out each label by hand and gives the reader each feedback entry as one line to file, rather than recording it. It does not run the preflight.

An entry names the asker only when the asker agrees, and only by an authenticated login: `gh api user --jq .login`, `glab api user` filtered to its `username`, or the signing-key route the curator describes. The once-per-session question names that login, because the scheduled workflow commits `feedback.md`, often into a public pull request, and git history keeps an entry after the librarian clears it. Without a login, or without the asker's agreement, the entry is attributed to `docent` alone. A missing bundle is worth one sentence to the reader. The skill never carries a secret, credential, token, or connection string into an answer or a feedback entry, even to explain where one was found: it names the file and line and the kind of value, never the value itself.

**The repository fallback, the second Snyk W011 finding (acknowledged 2026-09-25).** Falling back to the repository means opening text the skill did not author, and its guardrails treat that text as something to quote or summarize, never as instructions, even when a file is phrased as one. What contains it is what the skill cannot do. It never edits `.lokf/knowledge/`. Its one write is a feedback entry through the script, after asking once per session, and the script holds that entry to one line and one of two kinds. The Copilot variant cannot write the file at all and hands the reader the line to paste instead. The [threat model](../policies/threat-model.md) lists this surface and what it does not cover.

**The Gen Agent Trust Hub audit of 2026-10-04, addressed.** For command and dynamic execution, a trust label and a feedback entry each come from a script in the skill's own `scripts/` folder, so no label depends on the model's arithmetic and the model never opens `.lokf/feedback.md`. The scripts treat bundle and reader text as data only. For data exposure, the skill keeps only the asker's login from `gh` or `glab`, and an entry carries it only when the asker agreed. The threat model says where that stops: a repository that holds its own copy of the skill supplies the scripts as well.
