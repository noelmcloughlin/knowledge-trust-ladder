# Three lines of defence: where each LOKF role sits, and what an auditor can check

Regulated industries use the **three lines of defence** to say who owns a risk, who keeps the rules, and who checks independently - the [Three Lines Model](https://www.theiia.org/en/content/position-papers/2020/the-iias-three-lines-model-an-update-of-the-three-lines-of-defense/), as the IIA has called it since 2020. LOKF was not designed from it, but reading the cast through it answers the three questions a governance reader brings: who is accountable for a claim, what is checked mechanically, and what can be examined afterwards. Nothing here adds a mechanism; every row names one that already exists.

| Line | In the model | In a LOKF bundle |
| --- | --- | --- |
| **First** - owns the work and its risk, with the controls built into the work | operational management | The **librarian** derives every record from a source it names, records its own re-checks as `process:` and never as a person, and marks what it cannot settle `status: draft` with an open question. The **curator**, a named person, decides what the team accepts as true: confirm, correct, retire, send back. Maker and checker: the agent cannot vouch, and the person does not derive. |
| **Second** - ensures compliance, without owning the content | risk and compliance functions | The **registrar**. `lokf validate` on every change and again as the CI gate, and the LOKF Registrar plugin live in Obsidian, keep every record well-formed; the gate's `provenance` job ties each new `human:` verdict to that person's approval of the pull request or their signature on the commit. It never judges truth. The rule it holds to is the covenant's: a verdict is only ever what that person actually said ([AI_COVENANT.md](../AI_COVENANT.md)). |
| **Third** - independent assurance | internal audit | Not shipped, and it could not be: independence means it does not come from the same authors. What ships is the evidence, below. |

The **docent** sits where the customer does, outside the lines: it reads, and what it could not answer goes to `.lokf/feedback.md` as a report the librarian treats as untrusted. The **sidecar** lays down the first line's tools and the second line's gate. Above the lines, the governing body has two instruments: the covenant, and `policies/knowledge-curation.md`, a normal concept that says who curates and how often each kind of concept is re-confirmed - reviewed and confirmed like any other. The [four levels of checking](for-the-curious.md#four-levels-of-checking) are this picture by phase rather than by role: schema-valid is the second line, source-consistent and human-confirmed the first, proven in use the docent's loop.

## Lines are roles, not people

The model's own revision says so, and it matters here because a small team, or one person, plays every line. What keeps the lines apart is then tooling, not headcount. The curator's identity comes from the forge (`gh api user`), never from git config or from the conversation, since both can be set by whoever is steering the agent. The gate accepts no `human:` event on anyone's say-so, and because GitHub will not let an author approve their own pull request, a solo maintainer signs. An Environment with required reviewers is the logged exception - one click per pull request, never a switch.

## What an auditor can check

Every trust label is computed from the frontmatter on each read and never stored, so a label cannot be asserted, only earned. The questions an auditor asks each have a place where the answer is written:

| Question | Where the answer is |
| --- | --- |
| Where did this come from? | `resource`, `sources[].resource`, `derivedFrom` |
| Who produced the current text, and when? | `generated.by`, `generated.at` |
| Who confirmed it, and when? | `verified[].by`, `verified[].at` |
| Was that really them? | the `provenance` job's log on the pull request - GitHub's verdict on the approval or the signature, not the runner's; locally, the curator skill's *Not tied to a signed commit* count |
| When must it be looked at again, and by what rule? | `stale_after`, proposed from `policies/knowledge-curation.md` |
| What changed, and why? | `log.md`, and git |
| Is the checker independent of the checked? | the JSON Schema and SHACL shapes are generated from the upstream `lokf.yaml`, not written here; the bundle projects to RDF and answers [SPARQL](../skills/lokf-curator/references/queries.md) |

Three limits on what the evidence holds. A confirmation records who and when, not what the source said at that moment: when the source is a file in the same repository, the commit that recorded the confirmation pins it; when it is a URL, nothing does. The gate checks identity, not entitlement: that `human:ada` is ada, not that ada was the right person to confirm a policy - who may confirm what is for `policies/knowledge-curation.md` and review to settle. And an Environment attestation records that someone with access to the repository's settings vouched, not that anything was read; the job's own log says as much.
