---
type: Explanation
id: https://lokf-agent-skills.example/knowledge/explanation/three-lines-of-defence
title: Three lines of defence - where each role sits, and what an auditor can check
description: Placing the librarian, curator, registrar, sidecar and docent roles in The Institute of Internal Auditors' Three Lines Model, with a diagram - who owns a claim, what a machine checks, and what a person can examine afterwards - the three limits on what that evidence shows, a paragraph that sends the reader to the critics page, and what remains to do and who does it. The critics page quotes the model's critics (preliminary research) and says which of their points a LOKF bundle answers and what kind of gap each remainder is. Written for whoever adopts a bundle, not about this repository's own arrangements.
genre: explanation
resource: docs/three-lines.md
generated:
  by: process:lokf-librarian
  at: "2026-09-17T15:00:00Z"
status: draft
about:
- https://lokf-agent-skills.example/knowledge/explanation/why-four-roles
- https://lokf-agent-skills.example/knowledge/explanation/why-a-registrar-role
relatedTo:
- https://lokf-agent-skills.example/knowledge/policies/ai-covenant
- https://lokf-agent-skills.example/knowledge/glossary/trust-label
verified:
- by: process:lokf-librarian
  at: "2026-09-16T09:10:00Z"
---

# Overview

The README's "Three lines of defence" section points at this page. The
reference model is the Three Lines Model of The Institute of Internal
Auditors (IIA), which dropped "defence" from the name
in [2020](https://www.theiia.org/en/content/position-papers/2020/the-iias-three-lines-model-an-update-of-the-three-lines-of-defense/)
and reissued it as a
[Statement of Position](https://www.theiia.org/globalassets/site/resources/statements-of-position/tlm_assurance_advice_support_effective_gov_en.pdf)
in 2026. LOKF was not built to it, but each role fits into it, and the page
shows where, in a table and a diagram (`.assets/lokf-three-lines.svg`) -
for any organisation that adopts a bundle, not for this repository's own
practice. First line: the **librarian**, which derives every record from
a named source and marks what it cannot settle `status: draft`, and the
**curator**, a named person who decides what the team accepts as true -
maker and checker, since the agent cannot vouch and the person does not
derive; the **sidecar** lays down their tools. Second line: the
**registrar** - `lokf validate` on every change and in CI, plus the LOKF
Registrar Obsidian plugin - which keeps records well-formed and ties a
`human:` verdict to that person's approval or signature, without judging
truth, on the rule that a verdict is only ever what that person said; the
sidecar lays down the gate. Third line: the bundle ships the evidence an
independent reviewer needs, not the review, since assurance is independent
only when it comes from someone other than the authors.

The **docent** sits outside the lines, where the reader does, and reports
what it could not answer back to the librarian as untrusted input. Above
the lines sits the governing body - the owners of the repository that
holds the bundle - with two instruments: the organisation's own rules for
AI-assisted work (this project's are its AI covenant) and the curation
policy. Lines are roles, not headcount - the IIA's 2020 text says the
lines "are not intended to denote structural elements but a useful
differentiation in roles", and the 2026 Statement keeps that roles "may
overlap in practice" given "clear accountability, transparency, and
safeguards" - and a bundle does not decide who plays each line; the
adopting organisation does. Tooling holds the lines apart either way: the
curator's identity comes from GitHub itself (`gh api user`), never from
git config or from what the person types into the agent's chat, and the
gate accepts a `human:` verdict only on that person's own approval or
signed commit. Approval is the usual route; where an organisation's policy
lets one person both author and confirm, the signature is the route, since
GitHub will not let them approve their own pull request. An Environment's
required reviewers are the one logged exception.

An auditor's questions each have a fixed place to look: provenance in
`resource`/`sources[].resource`/`derivedFrom`; who produced the current text
and when in `generated.by`/`generated.at`; who confirmed it and when in
`verified[].by`/`verified[].at`; which state of the source the check was
made against in `verified[].revision`/`generated.revision` (lokf 0.9.0+:
the full commit hash of a file, which the gate resolves against the tree,
or an ETag or digest for a URL, which nothing checks); whether that
confirmation is really tied to the named person in the `provenance` gate's
log (GitHub's verdict on the review or signature, not the runner's); and
when it must be looked at again in `stale_after`. Three limits bound what
that evidence proves: a confirmation records who and when, and the state
of the source only when the event carries `revision` (the curator skill
writes it; the LOKF Curator plugin does not yet) - without it, pinned by
the commit when the source is in-repository and by nothing when it is a
URL, and `revision` names what the skill fetched, not what the person
read; the registrar gate checks identity, not entitlement - that
`human:ada` is ada, not that ada was the right person to confirm that
concept; and a GitHub Environment attestation records only that a person
on the environment's reviewer list clicked Approve, not that they opened
the source.

The critics, and the answers to them, have a page of their own,
`docs/three-lines-critics.md`; the main page keeps one paragraph that says
the model has critics and so has the kind of tool a bundle is, that three
of their points a bundle meets by construction, two it answers in part and
one is not the bundle's role, and sends the reader there. The critics page
quotes each from their own text, marked as preliminary research read in
September 2026: the UK Parliamentary Commission on Banking Standards
(2013), Davies and Zhivitskaya (2018), Arndorfer and Minto (2015), Schuett
(2023), Bantleon et al. (2021) and Valkenburg and Bongiovanni (2024), and
after them the research on automation bias (Parasuraman and Manzey, 2010;
Bansal et al., 2021; Green, 2022; Buçinca et al., 2021) and on
hallucination (Ji et al., 2023). Its second half answers them, each
attribution and each entry linking to the other. Three points met by
construction: accountability is per claim (`verified[].by` names one
person, agent re-checks are `process:`); the second line is a program that
returns the same verdict whoever opened the change, though whether a red
check blocks a merge is a setting of the host repository; and the gate
reads the whole pull request and asks GitHub, not the author, about
approvals and signatures. Two critiques of the kind of solution LOKF is
are answered in part, and each remaining gap is labelled by kind.
*Judgement absent while process is followed*: answered by the curator
recording only what the person says, by the review session showing the
source before the claim, by curation being a reviewed policy, and by the
docent's evidence-first mode (`Evidence first: yes` in the curation
policy; off by default), and by the event recording which state of the
source the confirmation was made against (`revision`, lokf 0.9.0+, LOKF's
own field until OKF adopts it); left open - inherent, that nothing proves
the person read, and `revision` names what the skill fetched; a limit of
the technique, that a page differing on every fetch reads as moved on
every re-check; not the bundle's role, the evidence Green asks for that
oversight works, which is third-line sampling - the curator's report hands
over the sample when the policy sets `Independent re-check: <n>`; and off
by default, that where the policy leaves evidence-first off a docent
answer arrives with its label and no pause. *The machine invents*:
answered by every record naming its source, by unsettled concepts staying
`draft`, and by the conventions script the registrar runs failing when a
local `resource` no longer exists or a commit-shaped `revision` names no
commit holding it; left open by design, since the
registrar never judges truth and the librarian's re-check is self-review.
Incentives and skill in the lines are not the bundle's role: the
organisation assigns curators through the curation policy.

The main page closes with the gaps no control in a bundle closes, under
the heading "What remains to do, and who does it", labelled by owner. Upstream, for
OKF: adopting `revision` (knowledge-catalog#437); LOKF carries it from
0.9.0, and a bundle that uses it is still a valid OKF bundle. This
project, once a design is chosen: writing `revision` from the LOKF Curator
plugin, an entitlement check in the provenance job (needs a
machine-readable "who may confirm what"), and an `lokf-auditor` skill for
the third line, of which the curator's sampling step is the first half.
The organisation's: naming the independent re-checker, whether a red check
blocks a merge, and the incentives and skill of whoever curates.
