---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/three-lines-of-defence
title: Three lines of defence - where each role sits, and what an auditor can check
description: Placing the librarian, curator, registrar, sidecar and docent roles in The Institute of Internal Auditors' Three Lines Model, with a diagram - who owns a claim, what a machine checks, and what a person can examine afterwards - the four limits on what that evidence shows, a pointer to the critics page, and what remains to do and who does it. The critics page quotes the model's critics (preliminary research) and says which of their points a LOKF bundle answers and what kind of gap each remainder is. Written for whoever adopts a bundle, not about this repository's own arrangements.
genre: explanation
resource: docs/three-lines.md
generated:
  by: process:ktl-librarian
  at: "2026-09-24T00:55:04Z"
status: draft
about:
- https://knowledge-trust-ladder.example/knowledge/explanation/why-four-roles
- https://knowledge-trust-ladder.example/knowledge/explanation/why-a-registrar-role
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/policies/ai-covenant
- https://knowledge-trust-ladder.example/knowledge/glossary/trust-label
---

# Overview

The README's "Three lines of defence" section points at this page. The
reference model is the Three Lines Model of The Institute of Internal
Auditors (IIA), updated in
[2020](https://www.theiia.org/en/content/position-papers/2020/the-iias-three-lines-model-an-update-of-the-three-lines-of-defense/)
and reissued as a
[Statement of Position](https://www.theiia.org/globalassets/site/resources/statements-of-position/tlm_assurance_advice_support_effective_gov_en.pdf)
in 2026. LOKF was not built to it, but each role fits, and the page shows
where in a table and a diagram (`.assets/ktl-three-lines.svg`, with a dimmed counterpart for dark mode), for any
organisation that adopts a bundle. First line: the **librarian**, which
derives every record from a named source and marks what it cannot settle
`status: draft`, and the **curator**, a named person who decides what the
team accepts as true - maker and checker, since the agent cannot vouch and
the person does not derive. Second line: the **registrar** - `lokf validate`
on every change and in CI, plus the KTL Registrar Obsidian plugin - which
keeps records well-formed and ties a `human:` verdict to that person's
approval or signature, without judging truth. Third line: the bundle ships
the evidence an independent reviewer needs, not the review. The **docent**
sits outside the lines, where the reader does, and reports what it could
not answer back to the librarian as untrusted input; the **sidecar** lays
down the tools and the gate. Above the lines sits the governing body - the
owners of the repository that holds the bundle - with the organisation's
rules for AI-assisted work (this project's are its AI covenant) and the
curation policy.

Lines are roles, not headcount: the IIA's text says the lines "are not
intended to denote structural elements but a useful differentiation in
roles" and "may overlap in practice" given "clear accountability,
transparency, and safeguards". The adopting organisation decides who plays
each line; the tooling holds the lines apart either way. Since 2026-09-17
the page says the curator's identity comes from the forge, never from the
person: the login the machine is signed in as, or the login
under which the forge lists the key the person signs with - never git
config, never what is typed into the agent's chat. The gate accepts a
`human:` verdict only on that person's approval of the pull request or
their signature on the commit; where one person both authors and confirms,
the signature is the route, and an Environment with required reviewers is
the one logged exception.

An auditor's questions each have a fixed place to look: provenance in
`resource`/`sources[].resource`/`derivedFrom`; who produced the current text
and when in `generated`; who confirmed it and when in `verified[]`; which
state of the source the check was made against in `revision` - a field
proposed for lokf 0.9.0 and not yet released - which the gate resolves
against the tree for a file and nothing checks for a URL; whether that
confirmation is really tied to the named person in the `provenance` job's
log; when it must be looked at again in `stale_after`; what changed, and
why, in `log.md` and git; and whether the checker is independent of the
checked in the JSON Schema and SHACL shapes, which are generated from the
upstream `lokf.yaml` rather than written by the bundle's authors. Four limits
bound what that evidence proves: a confirmation records who and when, and
the state of the source only when the event carries `revision`, and even
then what the skill fetched rather than what the person read; the gate
checks identity, not entitlement - `.lokf/curators/` settles who may confirm
at all, not yet what; an Environment attestation records only that a listed
reviewer clicked Approve; and the `provenance` job runs on GitHub, so
elsewhere `knowledge-provenance.sh` checks signatures against the keys on
file and nothing checks approvals, and a host without git has only its
platform's version history.

The critics have a page of their own, `docs/three-lines-critics.md`, marked
as preliminary research and, since 2026-09-23,
arranged by criticism rather than by critic. A table at the top lists nine
points with who raised them and a verdict; each section then quotes the
criticism from its source, says what a bundle does about it, and gives the
verdict, and a sources list closes the page with every paper by DOI. Three
points are met by construction: *accountability is diluted* (the UK
Parliamentary Commission on Banking Standards, 2013; Davies and Zhivitskaya,
2018; one named person per confirmation), *the second line cannot challenge
the first* (the Commission; Arndorfer and Minto, 2015; the second line is a
program) and *the second line sees only what it is shown* (Zhivitskaya as
Schuett, 2023, repeats it; the gate reads the whole change and asks the
forge, with the limit that a concept never derived surfaces only as a
docent miss). Three are answered in part: *process is followed, judgement
is absent* (the Commission, with Parasuraman and Manzey, 2010, Bansal et
al., 2021, Green, 2022, and Buçinca et al., 2021, on why; the curator
records only what the person says, the review session shows the source
first, curation is a reviewed policy, the docent's evidence-first mode is
off by default; left open, that nothing proves the person read, that a
dynamic page reads as changed on every re-check, and that evidence the
oversight works is third-line work the curator's sampling step only hands
over), *the machine invents* (Ji et al., 2023; every record names its
source and unsettled concepts stay `draft`; left open by design, since the
registrar never judges truth and the librarian's re-check is self-review)
and *the lines do not coordinate in practice* (Bantleon et al., 2021;
Valkenburg and Bongiovanni, 2024; every hand-off is written down and no
more is claimed). Three are not the bundle's role: *incentives and skill*
and *a fourth line for a weak internal audit* (Arndorfer and Minto) and
*the model's effectiveness is untested* (Davies and Zhivitskaya; Schuett),
each of which lands on the adopting organisation or on a third line.

The main page closes with what remains and who owns it, in three lines:
upstream, OKF adopting `revision` (knowledge-catalog#437) and LOKF's 0.9.0
shipping it; this project, `revision` from the KTL Curator plugin, an
entitlement check by kind of concept, the approval half of the gate on
GitLab and Forgejo, and an auditor skill for the third line; the
organisation, naming the independent re-checker, whether a red check blocks
a merge, and the incentives and skill of whoever curates.
