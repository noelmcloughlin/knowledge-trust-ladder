---
type: Explanation
id: https://w3id.org/ktl/knowledge/explanation/context-layer
title: "The curated context layer: one bundle, and a federation of bundles"
description: "What a context layer is, and why one KTL bundle is already one repository's context layer and where it stops. How bundles federate into one: domains as thin LOKF bundles that select releases, tiers of domains and the diamond rule, a workspace with one named graph per bundle served over SPARQL and MCP, and the products it can use."
genre: explanation
resource: docs/context-layer.md
sources:
  - resource: docs/context-layer.md
  - resource: docs/federation.md
  - resource: docs/context-layer-technology.md
  - resource: docs/architecture.md
about:
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
  - https://w3id.org/ktl/knowledge/glossary/context-layer
relatedTo:
  - https://w3id.org/ktl/knowledge/explanation/intended-uses
  - https://w3id.org/ktl/knowledge/explanation/domain-schemas
  - https://w3id.org/ktl/knowledge/explanation/three-lines-of-defence
references:
  - https://w3id.org/ktl/knowledge/references/lokf-specification
  - https://w3id.org/ktl/knowledge/references/okf-specification
  - https://w3id.org/ktl/knowledge/references/lokf-toolkit
generated:
  by: process:ktl-librarian
  at: "2026-10-19T12:30:15Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-19T20:01:11Z"
---

# Overview

Three pages place Knowledge Trust Ladder (KTL) in the industry's talk of a **context layer**: a governed layer between an organisation's sources and whoever consumes them, a person or an agent, that persists from one task to the next. `docs/context-layer.md` says what a context layer is, what one bundle provides and why KTL federates bundles. `docs/federation.md` says how a federation is built and run, and `docs/context-layer-technology.md` names the products a workspace can use. The architecture page links the first from "Why libraries have catalogues" and from "Prose, Structure, Meaning, Context". [ktl-federation](https://w3id.org/ktl/federation/) is the first domain host.

# One bundle is one repository's context layer

Unblocked names four properties of a context layer: "heterogeneous source ingestion, on-demand surfacing, cross-source conflict resolution, and per-query permission enforcement". Atlan adds multi-domain federation, in which "Each domain owns its definitions but contributes to one graph", and the page sets that beside Zhamak Dehghani's "federated computational governance". Google Cloud's Open Knowledge Format (OKF) chose "Format, not platform". It left open the work KTL exists for: what counts as trusted knowledge, how updates are reviewed, and what a consumer does with an unknown type or stale context.

A table on the page sets those properties against a bundle. The librarian derives each concept from a source it names, and a reader opens `index.md` first. The curator records a person's verdict on a conflict inside one bundle, and between bundles a domain's owner arbitrates. Every concept carries `generated` and `verified` events, and each trust label is computed on read. The bundle has no permissions of its own, since the repository's access control is the bundle's. So one bundle is already one repository's context layer, with per-query permission left to whatever hosts it.

# Many bundles federated into one layer

OKF says nothing about one bundle naming another, a catalogue of bundles, or what a reader may see across a trust boundary, and its trackers ask for all three. Section 11 of the LOKF specification answers with a registry of bundles keyed by `base_iri`, through which any IRI resolves to the bundle that owns it by the longest match. The toolkit's `lokf registry` commands keep the registry offline, and the sidecar's `knowledge-federate.py` supplies the federated store of section 11.4. KTL adds who answers for the set:

- **A domain** is a thin LOKF bundle in a repository of its own, whose concepts are its member bundles. Each member names one release by its zip and checksum, or by the `concepts.jsonld` its site serves. A one-file domain schema defines `Domain`, `MemberBundle` and `MemberDomain`. Nothing is copied upward, and a person's confirmation of a member attests that it belongs and that the domain's claims across bundles hold.
- **Tiers.** A member that is itself a domain is followed into the same workspace. Every domain bounds a workspace of its own, and confirming a domain member attests the delegation, not what its members say. Under the diamond rule, a bundle that two domains name at one release joins once, and at different releases the build stops. `max_depth` on the top domain sets how many tiers the build follows, 3 unless set.
- **The workspace** is a materialised view of the top domain, rebuilt on each release by `knowledge-federate.py build`, and no agent runs. The build locks and verifies each release, loads one named graph per bundle, gates every link between bundles against the registry, and swaps the graphs in one atomic step. A member whose file cannot be fetched is held at its last good state. A reader takes the index first and traverses on demand over the `lokf-registry` MCP server or a SPARQL endpoint, and trust labels are computed when the query runs.

The federation page sorts what exists from what remains a design. Of section 11, only fetching a member from a private repository remains a design, and per-query permission stays with the store and the artifact repository. An adopter decides whether to pin or float, how pinning compounds across tiers, how to keep IRIs stable, who arbitrates, what vocabulary fits, what a member adds, and who may see what. The `sensitivity` gate of section 11.5 admits an internal member only to a workspace built in a private or internal repository, and a confidential one to none.

# What a workspace can use

`docs/context-layer-technology.md` maps each role to what KTL does today and where a product fits. Any artifact repository that stores a file and sends a webhook on arrival can hold the releases. The workspace's `graph.nq` loads with its named graphs into every SPARQL 1.1 store the page surveyed, among them Oxigraph, Apache Jena Fuseki, GraphDB, Stardog, OpenLink Virtuoso and Amazon Neptune. Managed SPARQL exists on AWS, and natively on neither Azure nor Google Cloud. Catalogues that take tables read what `lokf tables` writes. The agent surface is the sidecar's MCP server or a store's own. Graph-building retrieval frameworks extract a graph of their own from text and consume no bundle's graph, though they can read its Markdown.
