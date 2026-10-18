---
type: Explanation
id: https://w3id.org/ktl/knowledge/explanation/context-layer
title: "The curated context layer: one bundle, and a federation of bundles"
description: "What the industry means by a context layer, why one KTL bundle is already one repository's context layer and where it stops, and how bundles federate into one layer: domains as thin LOKF bundles that select releases, tiers of domains with the diamond rule and `max_depth`, and a workspace rebuilt on each release with one named graph per bundle. It also says what exists today (the sidecar's federation templates, a `lokf-registry` MCP server and a SPARQL endpoint) and what remains a design, the decisions an adopter makes, and which SPARQL stores, catalogues, agent surfaces and artifact repositories such a layer can use."
genre: explanation
resource: docs/context-layer.md
sources:
  - resource: docs/context-layer.md
  - resource: docs/federation.md
  - resource: docs/context-layer-technology.md
  - resource: docs/architecture.md
  - resource: CHANGELOG.md
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
  at: "2026-10-18T10:22:18Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-15T01:30:10Z"
---

# Overview

`docs/context-layer.md` places Knowledge Trust Ladder (KTL) in the industry's talk of a **context layer**. A context layer is a governed layer between an organisation's sources and whoever consumes them, a person or an agent, and it persists from one task to the next. The architecture page uses the term in "Why libraries have catalogues" and links the page. It links the page again in "Prose, Structure, Meaning, Context". There it says that whoever uses a claim as context, person or agent, also reads how far it has been checked, whether from one bundle or from many federated into one layer. The page quotes each source from its own text, read on 2026-10-12. It keeps the discourse, the one-bundle table and the design. Since 0.48.0, `docs/federation.md` holds the federation's mechanics: the tiers of domains, how the workspace stays current, what exists and what remains a design, and the decisions an adopter makes. [ktl-federation](https://w3id.org/ktl/federation/) is the first domain host.

**What the discourse means.** Unblocked names four properties: "heterogeneous source ingestion, on-demand surfacing, cross-source conflict resolution, and per-query permission enforcement". Atlan adds multi-domain federation, in which "Each domain owns its definitions but contributes to one graph", and the page sets that beside Zhamak Dehghani's "federated computational governance". Google Cloud's Open Knowledge Format (OKF) took a different approach, under the heading "Format, not platform". It left open the work KTL exists for: what counts as trusted knowledge, how updates are reviewed, and what a consumer does with an unknown type or stale context.

**One bundle is one repository's context layer.** A table on the page sets those properties against what a bundle does. The librarian derives each concept from a source it names. A reader opens `index.md` first, and the docent answers from the bundle with each concept's label. The curator records a person's verdict on a conflict inside one bundle. Every concept carries `generated` and `verified` events, and each trust label is computed on read. The bundle has no permissions of its own: the repository's access control is the bundle's. So one bundle is already one repository's context layer, with per-query permission left to whatever hosts it.

**Many bundles federated into one context layer: the design.** Domains select released bundles, and a person confirms each domain. A domain may select domains in turn, and the one a build starts from bounds the workspace. A repository that installed the sidecar releases its bundle with the template workflow `knowledge-release.yaml`. The workflow validates the bundle with the registrar's checks, packs it as a reproducible zip, attaches the zip and its `.sha256` to the release, and records a build attestation where the forge offers one. A domain schema the justfile's `schema` line names is released beside the bundle as `schema-<tag>-<name>.yaml`.

OKF says nothing about one bundle naming another, a catalogue of bundles, or what a reader may see of a bundle across a trust boundary, and its trackers ask for all three. Section 11 of the LOKF specification answers in linked-data terms. `lokf export` writes the files a registry reads, a `lokf-registry.yaml` keys each member bundle by its `base_iri`, and any IRI resolves to its owner by the longest matching `base_iri`. The toolkit's `lokf registry init`, `add`, `list` and `resolve` implement the registry offline. The federated store of section 11.4 is informative there, and the sidecar's build supplies it.

The design adds domains as manifests. A domain is a thin LOKF bundle in a repository of its own, released the same way, whose concepts are its member bundles. Each member is a `Dataset` concept that names the release zip in its `distribution`, the release tag in its `version` and the domain in its `isPartOf`. A member may be a domain in turn, and the build follows it tier by tier. LOKF has no catalogue class and no checksum slot, so a domain carries a one-file domain schema that defines `Domain`, `MemberBundle` and `MemberDomain`. Nothing is copied upward, so a member's new release leaves no stale copy in the domain. A domain confirmation attests two things: that these members belong, and that the cross-bundle claims hold.

**Tiers of domains.** `docs/federation.md` gives four rules for a tree of domains:

- every domain bounds a workspace of its own;
- confirming a domain member attests that the domain belongs and who answers for it, not what its members say;
- the diamond rule: two domains that name the same bundle at the same release add it once, and at different releases the build stops, because one named graph holds one release;
- `max_depth` on the top `Domain` concept sets how many tiers the build follows, 3 unless set.

**How the workspace stays current.** The workspace is a materialised view of the top domain, built ahead of time and rebuilt on publish, by a job that runs no agent. The job resolves the manifests into a lock of releases and checksums, and verifies each zip. It registers and exports each release, and loads each `graph.nt` into a named graph whose IRI is the bundle's `base_iri`. A cross-bundle link no member owns fails the build, or is reported, as the domain's `unowned_targets` says. The new graphs replace the old under one snapshot version, in one atomic step.

A reader gets the index first and traverses on demand, over a SPARQL endpoint and a Model Context Protocol (MCP) server. No trust label is stored in the snapshot, because a stored label drifts from what it describes within a day. SPARQL over `generated` and `verified` gives the labels against the clock at the moment of the query.

**What exists today, and what is design.** A table in `docs/federation.md` sorts the parts. It counts these as existing:

- a bundle validated, packed, checksummed, attested and attached to a release, by `knowledge-release.yaml` in the sidecar's templates;
- `lokf export`, `lokf registry init`, `add`, `list` and `resolve`, `lokf serve`, `query` and `mcp` over one bundle, and `lokf tables`, all in lokf 0.8.0;
- the registrar's gate and the report script;
- domains as thin bundles, their domain schema and a person's confirmation of membership: `domain.yaml` in the sidecar's templates, the first host ktl-federation, and the curator's `domain-bundle.md`;
- the lock, one named graph per bundle, tiers followed to the depth the top domain sets, the diamond rule, the gate on unowned targets and the atomic swap: `knowledge-federate.py build` and `knowledge-federation.yaml` in the sidecar's templates;
- a `lokf-registry` MCP server, `knowledge-federate.py mcp`;
- a read-only SPARQL endpoint over the workspace, `knowledge-federate.py serve` or the Oxigraph server image loading `graph.nq`.

It lists three parts as designs:

- lazy loading of a member's graph on first use, which section 11.4 of the specification marks informative (the workspace loads every member at build);
- harvesting remote artifacts, and the `sensitivity` gate of section 11.5, where the field exists and nothing reads it;
- per-query permissions, which stay with the store's and the artifact repository's access control, not the bundle's.

**Decisions an adopter makes.** `docs/federation.md` lists them:

- whether a manifest pins its members or floats;
- whether a domain member may float on its sub-domain's newest release, since pinning compounds across tiers (the templates pin at every tier);
- making the resolution of cross-bundle links a build gate from the start;
- a `base_iri` kept constant across releases, and a domain's namespace beside its members', never above them;
- who arbitrates when two bundles define one term differently;
- admission to a domain on vocabulary fit, and what a member adds;
- per-query permission in the artifact repository and the store, since OKF says trust tiers are not access control.

The design pins. Each member concept names one release, so a pinned domain releases for every member release. A floating manifest is fresher, but its curator has not seen each release it picks up, and the lock then holds the exact releases. Either way, the report must say at each tier which members have moved since the domain was last confirmed.

**What it integrates with.** `docs/context-layer-technology.md` surveys, from each vendor's own documentation, the artifact repositories, RDF stores with SPARQL, property-graph stores, catalogues and agent frameworks such a workspace could use. Stores whose documentation lists TriG or N-Quads keep one named graph per bundle through the load. Managed SPARQL exists on AWS, and natively on neither Azure nor Google Cloud. No retrieval framework it surveyed consumes RDF as its graph, so the agent surface is the store's own. Catalogues that take tables rather than RDF read what `lokf tables` writes.
