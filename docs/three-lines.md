# Three lines of defence: where each LOKF role sits, and what an auditor can check

Regulated industries use the **three lines of defence** to say who owns a risk, who keeps the rules, and who checks independently. The reference version is the Three Lines Model of The Institute of Internal Auditors (IIA), which dropped "defence" from the name in [2020](https://www.theiia.org/en/content/position-papers/2020/the-iias-three-lines-model-an-update-of-the-three-lines-of-defense/) and reissued the model as a [Statement of Position](https://www.theiia.org/globalassets/site/resources/statements-of-position/tlm_assurance_advice_support_effective_gov_en.pdf) in 2026.

LOKF was not built to this model, but each LOKF role fits into it. This page shows where, and answers the three questions a governance reader brings: who is accountable for a claim, what a machine checks, and what can be examined afterwards. Nothing here is new: every control the page names already exists in a LOKF bundle.

| Line | In the model | In a LOKF bundle |
| --- | --- | --- |
| **First** - owns the work and its risk, with the controls built into the work | operational management | The **librarian** derives every record from a source it names, records its own re-checks as `process:` and never as a person, and marks what it cannot settle `status: draft` with an open question. The **curator**, a named person, decides what the team accepts as true: confirm, correct, send back, retire, or leave for later. Maker and checker: the agent cannot vouch, and the person does not derive. The **sidecar** lays down their tools. |
| **Second** - ensures compliance, without owning the content | risk and compliance functions | The **registrar**. `lokf validate` on every change and again as the CI gate, and the LOKF Registrar plugin live in Obsidian, keep every record well-formed; the gate's `provenance` job ties each new `human:` verdict to that person's approval of the pull request or their signature on the commit. It never judges truth. Its rule: a verdict is only ever what that person actually said. The **sidecar** lays down the gate. |
| **Third** - independent assurance | internal audit | The **bundle** ships the evidence an independent reviewer needs, listed below. The review itself is not shipped, because assurance is independent only when it comes from someone other than the authors. |

<p align="center">
  <img src="../.assets/lokf-three-lines.svg" alt="The three lines of defence with each LOKF role in place: the governing body above, the librarian and curator in the first line, the registrar in the second, the evidence for an unshipped third line, and the docent outside the lines feeding back to the librarian" width="720" />
</p>

The **docent** sits outside the lines, where the reader does, and reports what it could not answer back to the librarian as untrusted input.

Above the lines the Three Lines Model places a governing body: for a bundle, the owners of the repository that holds it. They have two instruments:

1. The organisation's own rules for AI-assisted work, which make the person who submits the owner of what was submitted. This project's are its [AI covenant](../AI_COVENANT.md).
2. The curation policy, a concept in the bundle that says who curates and how often each kind of concept is re-confirmed; it is itself reviewed and confirmed like any other concept.

The [four levels of checking](for-the-curious.md#four-levels-of-checking) are the bundle's own checks from the table above, ordered by when they happen rather than by line: schema-valid is the **second line**'s check, source-consistent and human-confirmed are the **first line**'s, and proven in use is the docent's loop.

## Lines are roles, not people

The IIA's model says (2020 text): the lines "are not intended to denote structural elements but a useful differentiation in roles", and "first and second line roles may be blended or separated". And (2026 text): roles "may overlap in practice", and what makes an overlap safe is "clear accountability, transparency, and safeguards to preserve objectivity and avoid self-review risks".

A bundle does not decide who plays each line; the organisation that adopts it does, and the model allows one person or a whole department per line. The tooling below holds the lines apart either way, so the separation does not rest on headcount.

The **curator**'s identity comes from GitHub itself, through `gh api user`. It is never taken from git config, which anyone can edit, or from what the person types into the agent's chat, where anyone can claim any name.

The gate accepts no `human:` event on anyone's say-so: it wants that person's approval of the pull request or their signature on the commit. Approval is the usual route. Where an organisation's policy lets one person both author and confirm, GitHub will not let them approve their own pull request, so the signature is the route. An Environment with required reviewers is the logged exception - one click per pull request, never a switch.

## What an auditor can check

Every trust label is computed from the frontmatter on each read and never stored, so a label cannot be asserted, only earned. The questions an auditor asks each have a place where the answer is written:

| Question | Where the answer is |
| --- | --- |
| Where did this come from? | `resource`, `sources[].resource`, `derivedFrom` |
| Who produced the current text, and when? | `generated.by`, `generated.at` |
| Who confirmed it, and when? | `verified[].by`, `verified[].at` |
| Which state of the source was the check made against? | `verified[].revision` and `generated.revision` (lokf 0.9.0+): the full commit hash of a file in the repository, which the gate resolves against the tree; an ETag or content digest for a URL, which nothing checks. Absent means unrecorded, never unchanged |
| Was that really them? | the `provenance` job's log on the pull request - GitHub's verdict on the approval or the signature, not the runner's; locally, the curator skill's *Not tied to a signed commit* count |
| When must it be looked at again, and by what rule? | `stale_after`, proposed from `policies/knowledge-curation.md` |
| What changed, and why? | `log.md`, and git |
| Is the checker independent of the checked? | the JSON Schema and SHACL shapes are generated from the upstream `lokf.yaml`, not written by the bundle's authors; the bundle projects to RDF and answers [SPARQL](../skills/lokf-curator/references/queries.md) |

Three limits on what the evidence shows:

- A confirmation records who and when, and which state of the source only when the event carries `revision` (lokf 0.9.0+; the curator skill writes it when it confirms, the LOKF Curator plugin does not yet). Without it, a file in the same repository is pinned by the commit that recorded the confirmation, and a URL by nothing. `revision` names the state the skill fetched; it does not prove the person read it.
- The gate checks identity, not entitlement: that `human:ada` is ada, not that ada was the right person to confirm a policy - who may confirm what is for the curation policy and review to settle.
- When a confirmation is backed by a GitHub Environment attestation instead, the record shows only that a person on that environment's reviewer list clicked Approve. It does not show that they opened the concept's source. The job prints that caveat in its own log.

## What the critics say

The three lines model has critics, and so has the kind of tool a bundle is: a machine's output checked by a person. [Critics of the Three Lines Model](three-lines-critics.md) quotes them from their own texts, as preliminary research, and sets against each what a bundle answers and what it leaves open. Three of their points a bundle meets by construction, two it answers in part, and one is not the bundle's role. What is left open is collected below.

## What remains to do, and who does it

The gaps that no control in a bundle closes, as [the critics page](three-lines-critics.md#what-a-bundle-answers-and-what-it-leaves-open) sets them out, labelled by whose they are.

- **Upstream, for OKF.** Adopting `revision` ([knowledge-catalog#437](https://github.com/GoogleCloudPlatform/knowledge-catalog/issues/437)). LOKF carries the field from 0.9.0, and a bundle that uses it is still a valid OKF bundle, since OKF tolerates the key without reading it; until OKF adopts it, a consumer that reads only OKF's `{ by, at }` does not see it.
- **This project, once a design is chosen.** Writing `revision` from the LOKF Curator plugin, which still records `by` and `at` alone. An entitlement check in the provenance job, which needs the curation policy's "who may confirm what" in a shape a machine can read. An `lokf-auditor` skill for the third line, which would walk a second person through the sampled concepts source-first and record their verdict as a separate `verified` event; the curator's sampling step, which hands a second person a random sample of confirmed concepts with their sources, is its first half. Neither confers independence: the person running it must be someone other than the authors.
- **The organisation's.** Naming that person. Whether a red check blocks a merge. The incentives and skill of whoever curates.
