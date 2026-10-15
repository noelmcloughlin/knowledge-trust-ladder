---
type: Explanation
id: https://w3id.org/ktl/knowledge/explanation/context-layer
title: "The curated context layer: one bundle, and a federation of bundles"
description: "What the industry means by a context layer, why one KTL bundle is already one repository's context layer and where it stops, and a design for federating bundles into one layer: domains as thin LOKF bundles that select releases, and a workspace rebuilt on each release with one named graph per bundle. It also says what exists today, the decisions an adopter makes, and which SPARQL stores, catalogues, agent surfaces and artifact repositories such a layer can use."
genre: explanation
resource: docs/context-layer.md
sources:
- resource: docs/context-layer.md
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
  at: "2026-10-13T15:08:54Z"
status: draft
verified:
- by: process:ktl-librarian
  at: "2026-10-15T01:30:10Z"
---

# Overview

`docs/context-layer.md` places Knowledge Trust Ladder (KTL) in the industry's talk of a **context layer**. A context layer is a governed layer between an organisation's sources and whoever consumes them, a person or an agent, and it persists from one task to the next. The architecture page uses the term in "Why libraries have catalogues" and links the page. It links the page again in "Prose, Structure, Meaning, Context", where it says that whoever uses a claim as context, person or agent, also reads how far it has been checked, whether from one bundle or from many federated into one layer. The page quotes each source from its own text, read on 2026-10-12. Both of its diagrams give a dashed outline to the parts that are a design, with no released code behind them yet.

**What the discourse means.** Unblocked names four properties: "heterogeneous source ingestion, on-demand surfacing, cross-source conflict resolution, and per-query permission enforcement". Atlan adds multi-domain federation, in which "Each domain owns its definitions but contributes to one graph", and the page sets that beside Zhamak Dehghani's "federated computational governance". Google Cloud's Open Knowledge Format (OKF) took a different approach, under the heading "Format, not platform", and left open the work KTL exists for: what counts as trusted knowledge and how updates are reviewed.

**One bundle is one repository's context layer.** A table on the page sets those properties against what a bundle does. The librarian derives each concept from a source it names. A reader opens `index.md` first, and the docent answers from the bundle with each concept's label. The curator records a person's verdict on a conflict inside one bundle. Every concept carries `generated` and `verified` events, and each trust label is computed on read. The bundle has no permissions of its own: the repository's access control is the bundle's. So one bundle is already one repository's context layer, with per-query permission left to whatever hosts it.

**Many bundles federated into one context layer: the design.** Domains select released bundles, and a person confirms each domain. A top domain selects domains and bounds the workspace. A repository that installed the sidecar releases its bundle with the template workflow `knowledge-release.yaml`. The bundle is validated with the registrar's checks, packed as a reproducible zip, checksummed, and attested where the forge offers it.

OKF says nothing about one bundle naming another, a catalogue of bundles, or what a reader may see of a bundle across a trust boundary, and its trackers ask for all three. Section 11 of the LOKF specification answers in linked-data terms. `lokf export` writes the files a registry reads, a `lokf-registry.yaml` keys each member bundle by its `base_iri`, and any IRI resolves to its owner by the longest matching `base_iri`. The toolkit's `lokf registry` commands do this offline today. The federated store that section 11.4 describes is marked informative and is not built.

The design adds domains as manifests. A domain is a thin LOKF bundle of its own, released the same way, whose concepts are its member bundles. Each member is a `Dataset` concept that names the release zip in its `distribution`, the release tag in its `version` and the domain in its `isPartOf`. The domain's cross-bundle claims sit beside its member concepts. LOKF has no catalogue class and no checksum slot, so a domain carries a one-file domain schema. Nothing is copied upward, so a member's new release never leaves a stale copy inside a domain. A domain's confirmation attests two things only: that its members belong, and that its cross-bundle claims hold.

**How the workspace stays current.** The workspace is a materialised view of the top domain, rebuilt when a release is published, by a job that runs no agent. The job resolves the manifests into a lock of releases and checksums, and verifies each zip. It registers and exports each release, and loads each `graph.nt` into a named graph whose IRI is the bundle's `base_iri`. A cross-bundle link no member owns fails the build, or is reported, as the domain's policy says. The new graphs replace the old under one snapshot version.

A reader gets the index first and traverses on demand, over a SPARQL endpoint and an MCP server. Each trust label is computed from the events at the moment of the query, and never stored in the snapshot, since a snapshot that stores labels drifts from what it describes within a day.

**Decisions an adopter makes.** The page lists them:

- whether a manifest pins its members or floats;
- whether a cross-bundle link no member owns fails the build (the page recommends making that resolution step a build gate from the start);
- a `base_iri` kept constant across releases, and a domain's namespace beside its members', never above them;
- who arbitrates when two bundles define one term differently;
- admission to a domain on vocabulary fit;
- per-query permission in the artifact repository and the store, since OKF says trust tiers are not access control.

The design pins. Each member concept names one release, so a pinned domain needs a release of its own for every member release. A floating manifest is fresher, but its curator has not seen each release it picks up, and the workspace's lock then holds the exact releases. Either way, the report must say at each tier which members have moved since the domain was last confirmed.

**What it integrates with.** `docs/context-layer-technology.md` surveys, from each vendor's own documentation, the artifact repositories, RDF stores with SPARQL, property-graph stores, catalogues and agent frameworks such a workspace could use. Stores whose documentation lists TriG or N-Quads keep one named graph per bundle through the load. Managed SPARQL exists on AWS, and natively on neither Azure nor Google Cloud. No retrieval framework it surveyed consumes RDF as its graph, so the agent surface is the store's own. Catalogues that take tables rather than RDF read what `lokf tables` writes.
