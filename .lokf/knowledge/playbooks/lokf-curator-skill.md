---
type: Playbook
id: https://lokf-agent-skills.example/knowledge/playbooks/lokf-curator-skill
title: lokf-curator skill
description: A human curator's assistant - reports what needs a person's attention, then records that person's confirm/correct/retire/send-back verdicts into the bundle's frontmatter.
genre: how-to
resource: skills/lokf-curator/SKILL.md
generated:
  by: process:lokf-librarian
  at: "2026-09-17T15:27:51Z"
status: draft
dependsOn:
- https://lokf-agent-skills.example/knowledge/playbooks/lokf-librarian-skill
about:
  - https://lokf-agent-skills.example/knowledge/glossary/trust-label
definedBy:
- https://lokf-agent-skills.example/knowledge/references/agent-skills-specification
verified:
- by: process:lokf-librarian
  at: "2026-09-17T15:27:51Z"
---

# Overview

Runs **a little, regularly**. Step 1 is always a read-only one-screen report
computed from frontmatter alone (no toolkit needed): a health line, at most
five items "worth ten minutes today", the librarian's open questions, waiting
reader feedback, vocabulary fit, (only when the curation policy sets
`Independent re-check: <n>`) n confirmed concepts,
picked by a rule the curator cannot steer, with their sources for a second
person to re-check, and (since 2026-09-17) a *Ready to record* line from the
preflight - the id a confirmation would carry, signing on or off, attended
or not - so the session that follows offers only the verbs it can do. What
is missing is said in plain words before any command, because the curator is
often the person who knows the subject and not the repository; one who
cannot fix it themselves gets a request note for the maintainer, written
from lokf-sidecar's `references/prerequisites.md`. Step 2 is an opt-in review session that
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

From lokf 0.9.0 a confirmation event also carries `revision`, the state of
the source the person was shown (`references/review-session.md`, added
2026-09-17): the full commit hash for a file in the repository, or the ETag,
else a `sha256:` digest, for a URL. The skill leaves it out when the file
has uncommitted changes or the toolkit is older. It records what the skill
fetched, not proof that the person read it.

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
