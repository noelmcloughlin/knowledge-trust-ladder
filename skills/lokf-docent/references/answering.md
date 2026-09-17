# Answering from the bundle - procedure and edge cases

## Economy

The point of a bundle is to *not* re-read the repository. Spend tokens in this order and stop as soon as the question is answered:

1. `.lokf/knowledge/index.md` - header and TOC only (it may be long; scan the section headings first: Services, References, Glossary, Playbooks, Policies, ...).
2. One to three concept files chosen from the TOC. A concept's `description` in the TOC bullet usually tells you whether to open it.
3. Concepts reached by following a typed relation from one you already have.
4. The concept's `resource` (or a `sources[].resource`) - only for exact values or when the label demands a check.
5. The repository at large - only after 1-4 have failed, and say so.

## Finding the right concept

| The question sounds like | Look for |
| --- | --- |
| "What is X?" / "What does X mean?" | a `GlossaryTerm` (`definition`), or an `Explanation` |
| "Who owns / publishes / maintains X?" | a `Person` or `Organization`, reached from X via `source`, `author`, or the bundle-root `publisher` |
| "Which policy governs X?" | a `Policy` whose `about` points at X |
| "How do A and B relate?" | the typed relations on A and B (`dependsOn`, `isPartOf`, `hasPart`, `derivedFrom`, `references`) |
| "How do I ...?" | a `Playbook` (how-to) or `Tutorial` (learning) |
| "Where is X defined / configured?" | the concept's `resource` |
| "What's the endpoint / version / schema of X?" | a `Service` (`endpoint`, `documentation`), `Dataset`/`Table` (`fields`, `distribution`) - then confirm at `resource` |

## Deriving the label

Same rules as lokf-curator's `references/trust-fields.md`; restated here so this skill stands alone:

- `verified` may be a list or a bare `{ by, at }` mapping - a bare mapping is one event.
- *Confirmed by a person*: any event's `by` starts with `human:`. Quote the latest such date in the footer, and its `revision` when the event carries one ("against 3f9c2a1"): that is the state of the source the person saw, so a reader can tell whether the page in front of them is the one that was confirmed.
- *Checked by automation only*: events exist, none human.
- *Nobody has checked this yet*: no `verified` key.
- *Still a draft*: `status: draft`. *Retired*: `status: deprecated`. Absent `status` means stable.
- *Past its review date*: `stale_after` (a datetime, or a bare `YYYY-MM-DD` date) is on or before today. Compare as strings after trimming to ten characters.
- Labels overlap. Report every one that applies, most cautionary first.

## When to go to the source

Always for: versions, endpoints, ports, numbers, file paths, dates, anything the user is about to act on. Also whenever the only concept is *nobody has
checked this yet* or *past its review date* and the question is about the present. Say what you opened: "checked `services/orders/openapi.yaml`".

If the source **disagrees** with the concept, answer from the source, say the bundle is behind, and record a Disagreement (references/feedback.md). Don't edit the concept.

## Several concepts, different answers

Say so. Prefer the one *confirmed by a person*; if the source settles it, record a Disagreement for the loser; if nothing settles it, present both with
their labels and let the reader decide.

## Historical questions

"What did X used to be?" - a *retired* concept is exactly the right answer. Label it retired and don't treat it as current.

## Footer variants

Full footer (several concepts, a source check, a gap):

```text
From the bundle:
- Orders API (services/orders-api.md) - confirmed by a person, 2026-09-01, against 3f9c2a1
- Data retention (policies/data-retention.md) - confirmed by a person, past its review date (2026-08-01)
Checked at source: services/orders/openapi.yaml (the endpoint)
Gap recorded: Miss - no concept for the billing worker
```

Inline (one concept, one label, no source check):

> The Orders API depends on the Orders DB (bundle: `services/orders-api.md`,
> nobody has checked this yet).

Evidence first (the curation policy, `.lokf/knowledge/policies/knowledge-curation.md`, says `Evidence first: yes`, and the concept is anything less than *confirmed by a person*; no file, no line, or another value means the usual order): the source's lines come before the answer that rests on them, then the footer as usual.

> From `services/orders/openapi.yaml`, lines 12-15: `paths: /orders: get: ...`.
> So the Orders API exposes a read endpoint for orders (bundle:
> `services/orders-api.md`, nobody has checked this yet).

Repository fallback:

> The bundle has no concept for this. From `workers/billing/config.yaml`: the
> billing worker consumes the `billing-events` queue. Recorded as a gap for
> the librarian.

## No bundle at all

If `.lokf/knowledge/index.md` doesn't exist, this skill has nothing to guide through. Answer from the repository as the agent normally would, and mention
once that lokf-sidecar can create a bundle so the next reader doesn't repeat the search. Don't create `.lokf/feedback.md` in that case - there is
no librarian loop to consume it.
