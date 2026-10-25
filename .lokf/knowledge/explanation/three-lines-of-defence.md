---
type: Explanation
id: https://w3id.org/ktl/knowledge/explanation/three-lines-of-defence
title: Three lines of defence - where each role sits, and what an auditor can check
description: "The librarian, curator, registrar, sidecar and docent placed in the IIA's Three Lines Model, for whoever adopts KTL: who owns a claim, what a machine checks, what a person can examine afterwards, the four limits on that evidence, the model's critics with KTL's answer to each, and what remains to do and who does it."
genre: explanation
resource: docs/three-lines.md
generated:
  by: process:ktl-librarian
  at: "2026-10-25T23:53:02Z"
about: []
relatedTo:
  - https://w3id.org/ktl/knowledge/policies/ai-covenant
  - https://w3id.org/ktl/knowledge/glossary/trust-label
  - https://w3id.org/ktl/knowledge/explanation/context-layer
  - https://w3id.org/ktl/knowledge/explanation/why-four-roles
  - https://w3id.org/ktl/knowledge/explanation/why-a-registrar-role
verified:
  - by: process:ktl-librarian
    at: "2026-10-20T23:23:33Z"
  - by: human:noelmcloughlin
    at: "2026-10-13T01:11:23Z"
  - by: human:noelmcloughlin
    at: "2026-10-19T20:41:59Z"
stale_after: 2027-10-19
sources:
  - resource: docs/three-lines.md
  - resource: CHANGELOG.md
  - resource: docs/architecture.md
---
# Overview

The architecture page's section on the fifth role, the registrar, points at this page. The reference model is the Three Lines Model of The Institute of Internal Auditors (IIA), updated in [2020](https://www.theiia.org/en/content/position-papers/2020/the-iias-three-lines-model-an-update-of-the-three-lines-of-defense/) and reissued as a [Statement of Position](https://www.theiia.org/globalassets/site/resources/statements-of-position/tlm_assurance_advice_support_effective_gov_en.pdf) in 2026. KTL was not built to it, but each of its roles fits. The page shows where, in a table and a diagram (`.assets/ktl-three-lines.svg`, with a dark counterpart), for any organisation that adopts KTL. Every control it names already exists in KTL.

- **First line**: the **librarian** and the **curator**. The librarian derives every record from a named source, records its own re-checks as `process:` and never as a person, and marks what it cannot settle `status: draft` with an open question. The curator is a named person who decides what the team accepts as true: confirm, correct, send back, retire, or leave for later. They are maker and checker, since the agent cannot vouch and the person does not derive.
- **Second line**: the **registrar**, which keeps records well-formed: `lokf validate` on every change and in CI, `knowledge-apply.sh` as the librarian's only pen, `knowledge-report.sh` computing every trust label, and the KTL Registrar Obsidian plugin. The gate ties a `human:` verdict that is added or removed to that person's approval or signature, and the pen refuses to write a `human:` actor at all. Neither judges truth.
- **Third line**: the bundle holds the evidence an independent reviewer needs, not the review.

The **docent** sits outside the lines, where the reader does, and reports what it could not answer back to the librarian as untrusted input. The **sidecar** installs the tools and the gate. `ktl-prose`, an optional helper, sits on the maker's side of the first line: a copy editor that writes no `generated` record, although `log.md` and git record the pass. The governing body sits above the lines: the owners of the repository that holds the bundle, with the organisation's rules for AI-assisted work and the curation policy. The curation policy is itself a concept, reviewed like any other. The [four levels of checking](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/docs/for-the-curious.md#four-levels-of-checking) are these same checks ordered by when they happen. This project's rules for AI-assisted work are its AI covenant.

Lines are roles, not headcount: the IIA's text says the lines "are not intended to denote structural elements but a useful differentiation in roles" and "may overlap in practice" given "clear accountability, transparency, and safeguards". The adopting organisation decides who plays each line, and the tooling holds the lines apart either way.

The page says the curator's identity comes from the forge, never from the person. It is the login the machine is signed in as, or the login under which the forge lists the key the person signs with. It is never git config, and never what is typed into the agent's chat. The gate accepts a `human:` verdict only on that person's approval of the pull request or their signature on the commit. Where one person both authors and confirms, the signature is the route, and an Environment with required reviewers is the one logged exception.

An auditor's questions each have a fixed place to look:

- Provenance: `resource`, `sources[].resource` and `derivedFrom`.
- Who produced the current text, and when: `generated`.
- Who confirmed it, and when: `verified[]`.
- Which state of the source the check was made against: `revision`, a field proposed for lokf 0.9.0 and not yet released. For a file it is the commit hash, which the gate resolves against the tree. For a URL it is an ETag or a digest, which nothing checks. An absent `revision` means unrecorded, never unchanged. Until it is released, `knowledge-report.sh` lists each confirmed concept whose source has a commit after the one that recorded the confirmation.
- Whether the confirmed text is still the one the person saw: the `validate` job's log, where conventions rule 13 fails an edit that leaves `generated` older than the confirmation.
- Whether that confirmation is really tied to the named person: the `provenance` job's log carries the forge's verdict on the approval or the signature. Locally, the curator's *Not tied to a signed commit* count does the same. Whether a person's record has been removed without them: the same job's log, since a confirmation struck out or gone with its concept needs that person's approval or signature, as an added one does. On the scheduled librarian's pull request, `knowledge-provenance.sh --unattended` checks it in the job that holds the write token.
- When it must be looked at again, and by what rule: `stale_after`, proposed from `policies/knowledge-curation.md`.
- What changed, and why: `log.md` and git.
- Whether the checker is independent of the checked: the JSON Schema, which is generated from the upstream `lokf.yaml` rather than written by the bundle's authors. The toolkit also generates SHACL shapes, which nothing here runs yet. The bundle projects to RDF and answers SPARQL.

Four limits bound what that evidence proves:

- A confirmation records who and when. It records the state of the source only when the event carries `revision`, and even then what the skill fetched rather than what the person read.
- The gate checks identity, not entitlement: `.lokf/curators/` settles who may confirm at all, not yet what.
- An Environment attestation records only that a listed reviewer clicked Approve.
- The `provenance` job runs on GitHub. Elsewhere `knowledge-provenance.sh` checks signatures against the keys on file, and nothing checks approvals. A host without git has only its platform's version history.

The critics have a section of the page, arranged since 2026-09-23 by criticism rather than by critic. A table at its head lists nine points with who raised them and a verdict. Each criticism then has a section that quotes the criticism from its source, says what KTL does about it, and gives the verdict. A sources list closes the page, citing each paper by DOI and the two reports by URL.

Three points are met by construction:

- *accountability is diluted*, raised by the UK Parliamentary Commission on Banking Standards (2013) and by Davies and Zhivitskaya (2018). The answer is one named person per confirmation.
- *the second line cannot challenge the first*, raised by the Commission and by Arndorfer and Minto (2015). The answer is that the second line is a program.
- *the second line sees only what it is shown*, Zhivitskaya's point as Schuett (2023) repeats it. The gate reads the whole change and asks the forge, with the limit that a concept never derived shows up only as a docent miss.

Three are answered in part:

- *process is followed, judgement is absent*, raised by the Commission, with Parasuraman and Manzey (2010), Bansal et al. (2021), Green (2022) and Buçinca et al. (2021) on why. The curator records only what the person says, the review session shows the source first, curation is a reviewed policy, and the docent's evidence-first mode is off by default. Left open: nothing proves the person read, a dynamic page reads as changed on every re-check, and evidence that the oversight works is third-line work KTL should not produce about itself.
- *the machine invents*, raised by Ji et al. (2023). Every record names its source, and unsettled concepts stay `draft`. Left open by design: the registrar never judges truth, and the librarian's re-check is self-review.
- *the lines do not coordinate in practice*, raised by Bantleon et al. (2021) and by Valkenburg and Bongiovanni (2024). Every hand-off is written down, and no more is claimed.

Three are not KTL's role, and each is the job of the adopting organisation or of a third line:

- *incentives and skill*, raised by Arndorfer and Minto.
- *a fourth line for a weak internal audit*, raised by Arndorfer and Minto.
- *the model's effectiveness is untested*, raised by Davies and Zhivitskaya and by Schuett.

The page then lists what remains and who owns it, in three lines:

- upstream: OKF adopting `revision` (knowledge-catalog#437) and LOKF releasing it in 0.9.0.
- this project: `revision` from the KTL Curator plugin, an entitlement check by kind of concept, the approval half of the gate on GitLab and Forgejo, and an auditor skill for the third line, of which the curator's sampling step is the first half. The auditor skill's Microsoft 365 Copilot form is to be one more instructions file beside the docent's under `.lokf/m365/`. The list also names fetching a federation member from a private repository, which `docs/federation.md` says remains a design.
- the organisation: naming the independent re-checker, whether a red check blocks a merge, and the incentives and skill of whoever curates.
