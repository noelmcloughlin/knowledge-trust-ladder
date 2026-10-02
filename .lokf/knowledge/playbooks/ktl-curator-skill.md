---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-curator-skill
title: ktl-curator skill
description: A human curator's assistant - reports what needs a person's attention, then records that person's confirm/correct/retire/send-back verdicts into the bundle's frontmatter.
genre: how-to
resource: skills/ktl-curator/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-09-24T00:55:04Z"
status: draft
dependsOn:
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-librarian-skill
about:
  - https://knowledge-trust-ladder.example/knowledge/glossary/trust-label
definedBy:
- https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
---

# Overview

Runs **a little, regularly**. Step 1 is always a read-only one-screen report
computed from frontmatter, and from git history for one count (no toolkit
needed): a health line (including how many confirmations no signed commit
stands behind), at most
five items "worth ten minutes today", the librarian's open questions, how many
reader feedback entries wait - counted with `grep -c`, never read, so no
reader's text enters the session - vocabulary fit, the confirmations git
cannot back (named, only when there are any), (only when the curation policy sets
`Independent re-check: <n>`) n confirmed concepts,
picked by a rule the curator cannot steer, with their sources for a second
person to re-check, and (since 2026-09-17) a *Ready to record* line from the
preflight - the id a confirmation would carry, signing on or off, attended
or not - so the session that follows offers only the verbs it can do. What
is missing is said in plain words before any command, because the curator is
often the person who knows the subject and not the repository; one who
cannot fix it themselves gets a request note for the maintainer, written
from ktl-sidecar's `references/prerequisites.md`. Step 2 is an opt-in review session that
shows the source *before* the claim and takes one verb per item. Step 3 covers
the curation policy, gap intake, domain-schema guidance, and the same labels
as SPARQL queries for `lokf serve` (`references/queries.md`).

**Vocabulary fit counts against the host's vocabulary, not only LOKF's**
(stated 2026-09-14): where `.lokf/justfile` validates with `--schema
<slug>.yaml`, the skill reads that file and counts its `Concept` descendants
as known - the same widening the librarian's Rule 3 applies, and the reason
the line goes quiet once a team adopts a domain schema instead of naming
every domain class a misfit for good. The label is now "doesn't fit the known
vocabulary", matching what the KTL Curator plugin already says.

The curation policy's table is read **tolerantly** (`references/review-session.md`,
stated 2026-09-14): rows name classes in prose, so the match ignores spaces
and plural form - "Glossary terms" is `GlossaryTerm`, "people" is `Person` -
and an unknown class binds nothing. A host extending the vocabulary sets
intervals for its own classes the same way. Stated because the KTL Curator
plugin implements this document and matched literally, ignoring four rows of
the skill's own template.

It deals in **judgments a person made, never facts it derived**. It writes only
`verified` (human events), `status`, `stale_after`, `generated` (on a dictated
correction), and an `## Open questions` section - and never without an explicit
per-item answer. There is deliberately no "confirm everything".

Where the toolkit accepts it, a confirmation event also carries `revision`,
the state of the source the person was shown (`references/review-session.md`,
added 2026-09-17): the full commit hash for a file in the repository, or the
ETag, else a `sha256:` digest, for a URL. The field is proposed for lokf
0.9.0 and not yet released - the 0.8.0 validator rejects it - so the skill
leaves it out on every released toolkit, and when the file has uncommitted
changes. It records what the skill fetched, not proof that the person read it.

**Where the id comes from (added 2026-09-17).** Three routes, in order:
`gh api user` on GitHub, `glab api user` on GitLab, and on any forge the
login whose registered signing key is the one in `git config
user.signingkey`, checked through the forge's public key listing. On a host
with no forge, the account the platform's version history shows is the id,
and that history is the only check. `references/portability.md` carries the
steps for each host - including that a GPG key usually signs with a subkey,
which the forge lists under `subkeys` - and the frontmatter's `compatibility`
field says the skill needs git, a POSIX shell and one of those identities to
record a confirmation in a person's name. Where the repository keeps curator
keys under `.lokf/curators/` for the forge-free gate, the preflight says
whether this person's key is on file before the session starts.
