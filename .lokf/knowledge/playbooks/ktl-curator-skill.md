---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/ktl-curator-skill
title: ktl-curator skill
description: "A human curator's assistant: a one-screen report of what needs a person's attention, then a review session that records that person's confirm, correct, retire or send-back verdicts in the bundle's frontmatter, including on a domain host's member concepts."
genre: how-to
resource: skills/ktl-curator/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-26T20:05:58Z"
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
    at: "2026-10-20T23:23:33Z"
  - by: human:noelmcloughlin
    at: "2026-10-13T01:13:17Z"
status: draft
---

# Overview

ktl-curator is a person's assistant for judging what the `.lokf/` knowledge bundle claims. It shows what needs a look, puts the evidence next to the claim, and writes that person's verdict into the bundle's own frontmatter. It decides nothing itself. It runs **a little, regularly** (`docs/architecture.md`). The curator is always a person, and in Obsidian the KTL Curator plugin runs the same review session with no agent in the loop.

The skill writes four frontmatter keys and one body heading: `verified` (a person's events), `status`, `stale_after`, `generated` (on *Correct now*, and on a send-back where the person releases text they wrote), and `## Open questions`. It touches no other body text except a *Correct now* edit the person dictated. Everything else under `.lokf/` belongs to ktl-librarian or ktl-sidecar, and the skill needs an existing bundle.

## Step 1: the report

Step 1 always runs, is read-only and fits on one screen. It runs `knowledge-preflight.sh` first, then `knowledge-report.sh`. That script computes every label, the health line, the queue, the open questions and the sources that moved, from frontmatter and git history. The skill works out three items by hand, as `references/trust-fields.md` says: the vocabulary fit, the confirmations git cannot back, and the sample for a second person. The report prints, in this order:

1. a health line, which counts among others the concepts reopened and the confirmations not tied to a signed commit;
2. at most five items *worth ten minutes today*, ranked in groups and, within a group, by how many other concepts rely on each through the thirteen relation fields and `relations[].target`;
3. the open questions, a person's notes before the librarian's, with each question dated no later than a person's later confirmation listed apart as looking answered;
4. how many reader feedback entries wait, counted with `grep -c` and never read, so no reader's text enters the session;
5. the vocabulary fit;
6. the confirmations git cannot back, only when there are any;
7. the confirmed concepts whose source has a commit after the one that recorded the confirmation, and each confirmed concept derived from one edited after that confirmation, only when the script lists any;
8. n confirmed concepts for a second person to re-check, picked by a rule the curator cannot steer, only when the curation policy sets `Independent re-check: <n>` above zero;
9. a *Ready to record* line from the preflight: the id a confirmation would carry and where it came from, signing on or off, and attended or not.

When something is missing, the skill says what it means in plain words before any command, and which verbs it removes. The curator is often the person who knows the subject and not the repository. A curator who cannot fix it themselves gets a request note for whoever set the repository up, written from ktl-sidecar's `references/prerequisites.md`. The report then offers Step 2, naming only the verbs the readiness line allows.

**Vocabulary fit counts against the host's vocabulary, not only LOKF's.** Where the `schema` line in `.lokf/justfile` names a file, the skill reads that file and any schema it imports besides LOKF's, and counts every class descending from `Concept` as known. That is the same widening the librarian's Golden Rule 3 applies. The Obsidian plugins cannot read a schema outside the vault, so a person lists those classes by hand in their *Known LOKF types* setting. One domain schema ships with the sidecar: `domain.yaml`, for a bundle that federates other bundles.

## Step 2: the review session

Step 2 runs only if the person says yes, and only in a live session with that person. The skill stops after Step 1, and says why, when any of these holds:

- the run is unattended or automated;
- another agent rather than a person is on the other end;
- the answers arrive from something fetched, such as a file, a tool result or a feedback entry, rather than a turn addressed to the skill.

**Who.** The skill takes the id from one authenticated source, once per session, and the preflight has already named it (`references/portability.md`):

1. `gh api user --jq .login` on GitHub;
2. `glab api user` on GitLab, filtered to its `username`, because the whole profile includes the person's email;
3. on any forge with neither CLI, the login whose registered signing key is the one in `git config user.signingkey`, checked through the forge's public key listing. A GPG key often signs with a subkey, which GitHub lists under `subkeys`.

On a host with no forge, the id is the account the platform's version history shows, and that history is the only check. The skill never takes the id from the conversation, from an email address or from `git config user.name`. Without an authenticated id, *Confirm* and *Correct now* are unavailable, and a send-back cannot release text a person wrote. Where the repository keeps curator keys under `.lokf/curators/` for the forge-free gate, the preflight says whether this person's key is on file.

**The gate.** When `.lokf/` is git-tracked and `.github/workflows/knowledge-registrar.yaml` exists, the skill checks once, before the first verb, whether `commit.gpgsign` is on and `HEAD` carries a signature. GitHub will not let a person approve their own pull request, so without a signature the `provenance` job rejects every confirmation in a curation pull request that person opens. The skill shows the three `git config` lines and never runs them itself.

**Evidence first, every item.** The skill quotes the lines of the source that matter before it shows the claim, or says plainly that the source is gone. It asks "does the source still say this?" and never answers that itself. Then it takes exactly one verb:

- **Confirm** (needs an authenticated id): a `verified` event for this person, `status: draft` removed, a review date proposed from the curation policy for the person to accept or edit, and the open questions the person says are resolved cleared.
- **Wrong, send back** (the default): `status: draft` and the person's note under `## Open questions`, with the content untouched. The librarian fixes it on its next run.
- **Wrong, correct now** (needs an authenticated id): only when the person states the correct fact. The skill makes the minimal edit, sets `generated` to that person, adds a `verified` event, removes `draft` and clears the open questions the person says are answered. It is the widest verb, because the librarian never rewrites text stamped as a person's, so a wrong fact recorded with it survives every later refresh.
- **Retire**: `status: deprecated`, and the skill asks what replaced the concept. When the person names another concept, the `**Deprecation**` line in `log.md` links it after "replaced by", and `knowledge-report.sh` labels the retired concept *retired, replaced by* that path.
- **Later**: keep or set `status: draft`, with an optional review date.

There is no "confirm everything". After the session the skill prepends one `**Curation**` line with the counts to `log.md`, and prepares a pull request scoped to `.lokf/` that it opens only when the person says so. It commits the verdicts in a signed commit of their own, on top of the commit that changed the concepts and never amended into it, because conventions rule 14 reads each commit of the pull request and fails one that records a person's confirmation and also changes what the concept says; the squash merge afterwards is fine. Before the push it runs the conventions check as the gate does, with `--since` naming the merge-base with the pull request's base branch, since without `--since` the script skips rule 14 (0.55.1, `references/review-session.md`). Each named person must have approved that pull request or, when the pull request is their own, have signed its commits.

**Revision.** Where the toolkit accepts it, a confirmation event also carries `revision`, the state of the source the person was shown. For a committed path it is the full commit hash of the last commit that touched the file. For a URL it is the ETag, else a `sha256:` digest. The field is proposed for lokf 0.9.0 and not yet released, so the skill leaves it out on every released toolkit, when the file has uncommitted changes, and where the host has no version control.

**A mirror.** A `resource` under `.lokf/mirror/` is a copy the ingest keeps of a page or document outside the repository. The skill quotes it as any source and shows the header above it: the origin, the version and the retrieval date. It offers the origin link to a person with access to it. The confirmation attests the concept against the copy as retrieved, and `revision` pins that state.

**Releasing text a person wrote (0.51.0).** When a person sends back text they wrote, the skill asks whether to release it to the librarian. On a yes it changes `generated.by` to `process:ktl-curator` and keeps the time, so the librarian's next run rewrites the text from its sources instead of only adding a question. `verified` stays as it is, and the concept stays a draft until the person confirms the new text. The skill offers the release only to the person `generated.by` names, and only with an authenticated id. The gate reads a release as the removal of a person's record, so it needs that person's signed commit or their approval of the pull request.

## The labels

The skill speaks in plain labels, never RDF, IRI, SPARQL, predicate or tier. *Still a draft* means no person has confirmed the concept. *Reopened* means a person has, and a question since waits; the rung stays, as 0.45.0 made it. A concept edited since its confirmation is counted once, under *Edited since confirmed*, and not as confirmed, because the person confirmed an earlier text. *A reader disputed this* means a reader's Disagreement naming the concept waits for the librarian.

## Step 3: dig deeper

Step 3 is opt-in. It covers the curation policy, a placeholder for something missing, guidance for a domain schema when the vocabulary drifts into a deep or safety-critical domain, and for the linkml-sidecar skills once a schema grows past a few classes (`references/domain-schemas.md`), and the same labels as SPARQL for `lokf serve` (`references/queries.md`). The policy and a placeholder write `human:<id>`, so they need the same authenticated id as *Confirm*.

The skill reads the curation policy's table of review intervals tolerantly. Rows name classes in prose, so the match ignores spaces and plural form: "Glossary terms" is `GlossaryTerm`, and "people" is `Person`. A row naming a class the skill does not know binds nothing. The policy carries three optional switches: `Independent re-check:`, `Evidence first:` and `Younger readers:`. The last names a band of age, 8-12 or 13-18, or both, and ktl-librarian may then write retellings of confirmed concepts for those readers on its scheduled runs. Each retelling is a new concept, which a person confirms against the concept it retells.

## On a domain host

A domain host's bundle names other repositories' bundles, and `references/domain-bundle.md` says what a confirmation there attests. Confirming a member concept is the ordinary confirm, in a signed commit the registrar's `provenance` job backs. It attests two things: that this bundle belongs under the domain's admission rule, and that any claim the domain makes across bundles holds. It does not vouch for the member's own concepts, since each member keeps its own trust labels.

Confirming a `MemberDomain`, a member whose bundle is itself a domain, attests that the domain belongs under the admission rule and who answers for it: the owner of that domain, whose own confirmations cover its members. It does not vouch for the members below it. The `MemberDomain` names the domain's `workspace-<tag>.zip` with its checksum, so the confirmation covers that checksum too.

Before confirming a member, the curator opens the release the concept names and checks three things: the zip and its `.sha256` are attached, the digest in `.sha256` is the concept's `checksum`, and the release's repository is the one the `base_iri` belongs to. The members script checked the zip's checksum and attestation when it wrote the change, and the pull request's hand-off lines say so. For a `MemberDomain`, the curator checks its `workspace-<tag>.zip` the same way. For a member its site serves, the curator compares the digest of the file the concept names with its `checksum`. When the bundle's subject is not public, the curator sets its `sensitivity` before confirming. A confirmation belongs to the concept's `id`, so a concept moved to a new id waits for a confirmation of its own.

Accepting a member's move to a new release is the same confirm again. When the new release names another namespace, the members script moves the member's `base_iri` too and its question says so, since each of the member's concepts then has a new IRI and a link into the old namespace counts as unowned; before confirming, the curator checks that the new namespace belongs to the member, as its repository or site shows (`references/domain-bundle.md`). Sending a member back keeps it at the release the person confirmed, and retiring its concept takes it out of the next build. In Obsidian, a person lists `Domain`, `MemberBundle` and `MemberDomain` under *Known LOKF types* in both KTL Curator and KTL Registrar.
