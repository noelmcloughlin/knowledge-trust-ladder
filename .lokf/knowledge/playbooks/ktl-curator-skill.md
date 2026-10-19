---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/ktl-curator-skill
title: ktl-curator skill
description: "A human curator's assistant: it reports what needs a person's attention, then records that person's confirm, correct, retire or send-back verdicts in the bundle's frontmatter."
genre: how-to
resource: skills/ktl-curator/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-19T20:01:11Z"
dependsOn:
  - https://w3id.org/ktl/knowledge/playbooks/ktl-librarian-skill
about:
  - https://w3id.org/ktl/knowledge/glossary/trust-label
definedBy:
  - https://w3id.org/ktl/knowledge/references/agent-skills-specification
sources:
  - resource: skills/ktl-curator/SKILL.md
  - resource: skills/ktl-curator/references/review-session.md
  - resource: skills/ktl-curator/references/trust-fields.md
  - resource: skills/ktl-curator/references/portability.md
  - resource: skills/ktl-curator/references/domain-bundle.md
  - resource: skills/ktl-curator/references/domain-schemas.md
  - resource: docs/architecture.md
  - resource: CHANGELOG.md
  - resource: skills/ktl-curator/references/queries.md
verified:
  - by: process:ktl-librarian
    at: "2026-10-18T17:45:03Z"
  - by: human:noelmcloughlin
    at: "2026-10-13T01:13:17Z"
status: draft
---

# Overview

ktl-curator runs **a little, regularly**. Step 1 is always a read-only one-screen report that quotes `knowledge-report.sh`. The script computes every label, the health line, the queue, the open questions and the sources that moved, from frontmatter and git history (no toolkit needed). The skill works out the vocabulary fit, the confirmations git cannot back and the sample for a second person by hand. The report holds:

- a health line (including how many concepts are reopened and how many confirmations no signed commit backs);
- at most five items "worth ten minutes today", which the script ranks and prints (since 2026-10-06), counting how many other concepts rely on each concept through the thirteen relation fields;
- the open questions, with those a person's later confirmation answered listed separately;
- how many reader feedback entries wait, counted with `grep -c` and never read, so no reader's text enters the session;
- vocabulary fit;
- the confirmations git cannot back (named, only when there are any);
- the confirmed concepts whose source has a commit after the one that recorded the confirmation, and each confirmed concept derived from one edited after that confirmation (again only when there are any);
- n confirmed concepts, picked by a rule the curator cannot steer, with their sources for a second person to re-check (only when the curation policy sets `Independent re-check: <n>`);
- a *Ready to record* line from the preflight (since 2026-09-17): the id a confirmation would carry, signing on or off, and attended or not. So the session that follows offers only the verbs it can do.

What is missing is said in plain words before any command, because the curator is often the person who knows the subject and not the repository. A curator who cannot fix it themselves gets a request note for the maintainer, written from ktl-sidecar's `references/prerequisites.md`.

Step 2 is an opt-in review session that shows the source *before* the claim and takes one verb per item. It runs only in a live session with that person, and stops after Step 1 if the run is unattended or automated. Before the first verb it asks once whether the confirmations will survive the gate: whether commit signing is on and `HEAD` is signed. *Correct now* is the widest verb, because a wrong fact recorded with it survives every later refresh. The hand-off pull request opens only when the person says so. Step 3 covers the curation policy, gap intake, domain-schema guidance, and the same labels as SPARQL queries for `lokf serve` (`references/queries.md`).

**Vocabulary fit counts against the host's vocabulary, not only LOKF's** (stated 2026-09-14). Where the `schema` line in `.lokf/justfile` names a file, the skill reads that file and any schema it imports besides LOKF's, and counts their `Concept` descendants as known. That is the same widening the librarian's Rule 3 applies. It is also the reason the line goes quiet once a team adopts a domain schema, instead of naming every domain class a misfit for good. The Obsidian plugins cannot read a schema outside the vault, so they are told the list by hand in their *Known LOKF types* setting. One domain schema ships with the sidecar: `domain.yaml`, for a bundle that federates other bundles (`references/domain-schemas.md`).

The curation policy's table is read **tolerantly** (`references/review-session.md`, stated 2026-09-14). Rows name classes in prose, so the match ignores spaces and plural form: "Glossary terms" is `GlossaryTerm`, and "people" is `Person`. An unknown class binds nothing. A host extending the vocabulary sets intervals for its own classes the same way.

The skill deals in **judgments a person made, never facts it derived**. It writes only `verified` (human events), `status`, `stale_after`, `generated` (on a dictated correction, and on a send-back where the person releases text they wrote), and an `## Open questions` section, and never without an explicit per-item answer. There is no "confirm everything".

Where the toolkit accepts it, a confirmation event also carries `revision`, the state of the source the person was shown (`references/review-session.md`, added 2026-09-17). A later reader can then tell whether the page they see is the one the confirmation rested on. For a file in the repository, the state is the full commit hash. For a URL it is the ETag, else a `sha256:` digest. The field is proposed for lokf 0.9.0 and not yet released, and the 0.8.0 validator rejects it. So the skill leaves it out on every released toolkit, when the file has uncommitted changes, and where the host has no version control.

A `resource` under `.lokf/mirror/` is a copy the ingest keeps of a page or document outside the repository, added in 0.49.0. The skill quotes it as it quotes any source, and shows the header above it: the origin, the version and the retrieval date. It offers the origin link to a person who can reach it. The confirmation attests the concept against the copy as retrieved, and `revision` pins that state (`references/review-session.md`).

**Where the id comes from (added 2026-09-17).** The id comes from three routes, in order:

1. `gh api user` on GitHub;
2. `glab api user` on GitLab, filtered to its `username` because the whole profile includes the person's email;
3. on any forge, the login whose registered signing key is the one in `git config user.signingkey`, checked through the forge's public key listing.

On a host with no forge, the account the platform's version history shows is the id, and that history is the only check. `references/portability.md` carries the steps for each host, including that a GPG key often signs with a subkey, which GitHub lists under `subkeys`. The frontmatter's `compatibility` field says the skill needs git, a POSIX shell and one of those identities to record a confirmation in a person's name. Where the repository keeps curator keys under `.lokf/curators/` for the forge-free gate, the preflight says whether this person's key is on file before the session starts.

The health line counts a concept edited since its confirmation once, under *Edited since confirmed*, because the person confirmed an earlier text (`references/trust-fields.md`). *Correct now* clears the open questions the person says are answered, as *Confirm* does (`references/review-session.md`).

The label table reads *Still a draft* for a concept no person has confirmed, and *Reopened* for one a person confirmed where a question has since put it back to `status: draft`. A reopened concept still counts as confirmed, so the rung stays, added in 0.45.0 (`SKILL.md`, `references/trust-fields.md`). Confirming a member of a domain bundle is the ordinary confirm: it attests that the member's bundle belongs under the domain's admission rule and that any claim the domain makes across bundles holds, never that the member's own concepts are true. The same confirm on a `MemberDomain` attests the domain itself, never the members below it, added in 0.44.0 (`references/domain-bundle.md`).

The curation policy carries three optional switches: `Independent re-check:`, `Evidence first:` and `Younger readers:` (`references/review-session.md`). The last names a band of age, 8-12 or 13-18, or both, and ktl-librarian may then write retellings of confirmed concepts for those readers on its scheduled runs. Each one is a new concept, which a person confirms against the concept it retells.

*Retire* asks what replaced the concept. When the person names another concept, the `**Deprecation**` line in `log.md` links it after "replaced by", and `knowledge-report.sh` labels the retired concept *retired, replaced by* that path. The label *a reader disputed this* means a reader's Disagreement naming the concept waits for the librarian.

**Releasing text a person wrote (0.51.0).** The librarian never rewrites a concept whose `generated.by` starts with `human:`. So when a person sends back text they wrote, the skill asks whether to release it to the librarian. On a yes, it changes `generated.by` to `process:ktl-curator` and keeps the time, and the librarian's next run rewrites the text from its sources instead of only adding a question. `verified` stays as it is, and the concept stays a draft until the person confirms the new text. The skill offers the release only to the person `generated.by` names, and only with an authenticated id. The gate reads a release as the removal of a person's record, so it needs that person's signed commit or their approval of the pull request (`references/review-session.md`).

## Open questions

- 2026-10-18, human:noelmcloughlin: review the changes to the ktl-curator skill and its sources over the 16 to 20 commits since this concept was last confirmed (0c3ea0a, 2026-10-13), and bring the concept up to date with them.
