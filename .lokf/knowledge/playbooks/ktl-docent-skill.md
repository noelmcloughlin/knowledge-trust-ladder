---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/ktl-docent-skill
title: ktl-docent skill
description: "The reader's side: it answers questions from the bundle first, with each concept's trust label, falls back to the repository when the bundle cannot answer, and records misses and disagreements for the librarian."
genre: how-to
resource: skills/ktl-docent/SKILL.md
generated:
  by: human:noelmcloughlin
  at: "2026-10-13T01:17:30Z"
dependsOn:
- https://w3id.org/ktl/knowledge/playbooks/ktl-librarian-skill
about:
- https://w3id.org/ktl/knowledge/glossary/trust-label
definedBy:
- https://w3id.org/ktl/knowledge/references/agent-skills-specification
references:
- https://w3id.org/ktl/knowledge/playbooks/ktl-curator-skill
- https://w3id.org/ktl/knowledge/policies/threat-model
verified:
- by: process:ktl-librarian
  at: "2026-10-16T00:41:23Z"
- by: human:noelmcloughlin
  at: "2026-10-13T01:17:30Z"
sources:
- resource: skills/ktl-docent/SKILL.md
- resource: skills/ktl-docent/references/answering.md
- resource: skills/ktl-docent/references/feedback.md
- resource: README.md
- resource: CHANGELOG.md
status: draft
---

# Overview

ktl-docent runs **whenever anyone asks**. It answers from the bundle first:

- read `knowledge/index.md`;
- open one to three candidate concepts;
- widen along all thirteen typed relations rather than by grepping;
- verify exact values (versions, endpoints, paths) at the concept's `resource` before stating them.

Every answer carries a footing: which concepts it rests on and how far each has been trusted.

Each label comes from the skill's own copy of `knowledge-report.sh`, run from the repository as `labels <path>...`. The docent works out a label by hand from the label table only where that copy is missing. A retired concept carries no other label. The label *edited since a person last confirmed it* takes the place of *confirmed by a person*, because the person confirmed an earlier text (2026-10-05). A retired concept's label names the concept that replaced it, when the newest `**Deprecation**` line in `log.md` links one. The docent opens that successor before it falls back to the repository.

The label *a reader disputed this on* a day means a reader's Disagreement names the concept and waits for the librarian, so the docent checks the source before it relies on the concept. A confirmation's label carries the `revision` it was checked against where the event records one ("against 3f9c2a1", a commit hash cut to seven characters).

A person can set one switch in the curation policy: the line `Evidence first: yes` in `policies/knowledge-curation.md`. It reverses the order for any concept not yet confirmed by a person, or edited since that confirmation: the quoted source first, then the answer that rests on it. No policy, no line, or another value means the usual order, and the reader cannot switch it from the conversation.

**A younger reader (added 2026-10-11).** When the asker says an answer is for a younger reader, the docent uses the band of age they name: 8 to 12, or 13 to 18. It never asks a reader's age, and never guesses it. It prefers a retelling: a concept under `young-readers/` whose `tags` carry that band. It weighs the retelling by its own label and gives the label of the adult concept it names under `derivedFrom` too. With no retelling, it answers from the adult concept in shorter sentences and plainer words. It keeps every fact, number and name exact, keeps the labels word for word, and writes nothing to the bundle.

It is **read-only on `knowledge/`**. Its single write is `.lokf/feedback.md`, after asking once per session. The entry is one of these:

- a **Miss**: a question the bundle could not answer, plus where the answer was found;
- a **Disagreement**: a concept versus what its source now says, with `--concept <path>` naming that concept so its label shows the dispute.

It makes that write with `knowledge-feedback.sh` (2026-09-23). The script inserts the entry newest first and prints only a kind, a date and a count, so the reports other readers left in that file never enter the session. Before the script, an entry meant reading the file and rewriting it, and the only guard was a line of prose telling the agent to ignore what it had just read. The librarian consumes those entries on its next run. Its apply script moves each one into `.lokf/questions.md`, a ledger only programs read, which closes the loop from reader back to bundle. In a gitignored `.lokf/` the docent still records feedback, but says the scheduled librarian doesn't run there, so someone has to run ktl-librarian by hand.

**Its own scripts, never the repository's (2026-10-05).** Both scripts are copies in the skill's own `scripts/` folder, byte-identical to ktl-sidecar's templates. The skill never runs the copies under `.lokf/scripts/`, because anyone who can commit to a repository can change those, and a question is no reason to run its code. Where its own copies are missing, it works out each label by hand and gives the reader each feedback entry as one line to file, rather than recording it. It does not run the preflight.

An entry names the asker only when the asker agrees, and only by an authenticated login: `gh api user --jq .login`, `glab api user` filtered to its `username`, or the signing-key route the curator describes. The once-per-session question names that login, because the scheduled workflow commits `feedback.md`, often into a public pull request, and git history keeps an entry after the librarian clears it. Without a login, or without the asker's agreement, the entry is attributed to `docent` alone. A missing bundle is worth one sentence to the reader.

The skill never carries a secret, credential, token, or connection string into an answer or a feedback entry, even to explain where one was found. It names the file and line and the kind of value, never the value itself.

**The repository fallback, the second Snyk W011 finding (acknowledged 2026-09-25).** Falling back to the repository means opening text the skill did not author. Its guardrails treat that text as something to quote or summarize, never as instructions, even when a file is phrased as one.

The fallback is contained by what the skill cannot do. It never edits `.lokf/knowledge/`. Its one write is a feedback entry through the script, after asking once per session, and the script holds that entry to one line and one of two kinds. The Copilot variant cannot write the file at all and hands the reader the line to paste instead. The [threat model](../policies/threat-model.md) lists this surface and what it does not cover.

**The Gen Agent Trust Hub audit of 2026-10-04, addressed.** For command and dynamic execution, a trust label and a feedback entry each come from a script in the skill's own `scripts/` folder. So no label depends on the model's arithmetic, and the model never opens `.lokf/feedback.md`. The scripts treat bundle and reader text as data only. For data exposure, the skill keeps only the asker's login from `gh` or `glab`, and an entry carries it only when the asker agreed. The threat model says where that stops: a repository that holds its own copy of the skill supplies the scripts as well.

## Open questions

- 2026-10-13, process:ktl-librarian: Since 2026-10-13 the Runs column ("whenever anyone asks") is in the table of roles on `docs/architecture.md`, not in `README.md`. `sources` should list `docs/architecture.md` instead of `README.md`.
