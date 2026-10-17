# The curated context layer: one bundle, and a federation of bundles

> [!NOTE]
> This page is for anyone deciding what a context layer is, what one Knowledge Trust Ladder (KTL) bundle already provides, and why KTL federates many LOKF bundles through domains. Each quotation is from the source's own text, read on 2026-10-12. [A federation of bundles](federation.md) says how a federation runs: tiers of domains, the workspace, what exists today and what an adopter decides. [What a KTL context layer integrates with](context-layer-technology.md) surveys the stores, catalogues, agent surfaces and artifact repositories.

Below, a *context layer* is a governed layer between an organisation's sources and whoever consumes them, a person or an agent, that persists from one task to the next. *The bundle* is the corpus KTL keeps in `.lokf/knowledge/`, one Markdown concept per file. A *domain* is a named set of bundles with one accountable owner. *The workspace* is the built graph a reader queries.

## What people mean by a context layer

Unblocked states the minimum: "A real context layer in 2026 has four non-negotiable properties: heterogeneous source ingestion, on-demand surfacing, cross-source conflict resolution, and per-query permission enforcement." Atlan adds what enterprise scale requires: "Multi-domain federation. Each domain owns its definitions but contributes to one graph. Conflicts get arbitrated, not duplicated." That is the shape Zhamak Dehghani named in 2020 for data mesh, "federated computational governance", a model "led by the federation of domain data product owners and data platform product owners" under "a set of global rules".

The ownership point is older than the agents. Efficiently Connected notes that federation technology "cannot make a Head of Retail Banking agree to share definitional ownership with an AML team", and that conversational agents return "whichever definition they encountered most frequently".

Google Cloud took a different approach. The Open Knowledge Format (OKF) "formalizes the LLM-wiki pattern into a portable, interoperable format": "a directory of markdown files with YAML frontmatter". Under the heading "Format, not platform", Google adds: "No complex compression scheme, no new runtime, no required SDK." A format leaves the work open: deciding what counts as trusted knowledge, how updates are reviewed, and what a consumer does with an unknown type or stale context. KTL exists for that work. [Prose, Structure, Meaning, Context](architecture.md#prose-structure-meaning-context) says how it reads OKF's trust goal.

## One bundle is one repository's context layer

The table sets Unblocked's four properties, and the two the others add, against what a bundle does.

| In the discourse | In a KTL bundle | Where it stops |
| --- | --- | --- |
| Heterogeneous source ingestion | The **librarian** derives each concept from a source it names in `resource` and `sources` ([who writes the bundle](for-the-curious.md#who-writes-the-bundle-and-what-checks-it)) | One repository's sources. A second repository is a second bundle |
| On-demand surfacing | A reader opens `index.md` first. The **docent** answers from the bundle and labels each concept it used ([the index as the retrieval interface](wikiskill.md)) | Files, and one in-process graph, until something serves them |
| Cross-source conflict resolution | The **curator**, a named person, records the verdict: confirm, correct, retire or send back. A reader's disagreement goes to `feedback.md` | One bundle. Two bundles that define one term differently have no arbiter yet |
| Per-query permission enforcement | None of its own. The repository's access control is the bundle's | Nothing finer than the repository |
| Provenance and trust | `generated` and `verified` events on every concept, and each label computed on read, never stored ([Trust stays visible](architecture.md#trust-stays-visible), [four levels of checking](for-the-curious.md#four-levels-of-checking)) | Who checked and when, not that the source is right |
| Format, not platform | LOKF, a semantic profile of OKF: Markdown a person reads, a LinkML schema that checks it, a graph any SPARQL store loads | A domain outside LOKF's vocabulary needs a [domain schema](for-the-curious.md#when-the-vocabulary-stops-fitting) |

So one bundle is already one repository's context layer, with the fourth of Unblocked's properties left to whatever hosts it.

## Many bundles federated into one context layer: the design

Domains select released bundles, and a person confirms each domain. A domain may select domains in turn, and the one a build starts from bounds the workspace.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../.assets/ktl-federated-context-layer-dark.svg">
    <img src="../.assets/ktl-federated-context-layer.svg" alt="From repository bundles to a context layer: four bundles, each released from its own repository into an artifact repository; domains as manifests that select releases and are confirmed by a person, labelled domains/domain-1, domains/domain-2 and domains/federation, where the build starts; one context layer built from domains/federation; and the readers." width="720" />
  </picture>
</p>

**What exists.** A repository that installed the sidecar releases its bundle. The template workflow [`knowledge-release.yaml`](../skills/ktl-sidecar/templates/github/knowledge-release.yaml) validates the bundle with the registrar's checks and packs it as a reproducible zip whose root is `knowledge/`. It writes a `.sha256` beside the zip, attaches both to the release, and records a build attestation where the forge offers one. Nothing in that zip is edited afterwards. A domain schema the justfile's `schema` line names is released beside the bundle as `schema-<tag>-<name>.yaml`, with its own checksum.

**What OKF leaves open.** OKF calls a bundle "The unit of distribution" and lets it be distributed as a git repository, as a tarball or zip, or as a subdirectory of a larger repository. It says nothing about one bundle naming another, a catalogue of bundles, or what a reader may see of a bundle across a trust boundary. Its trackers ask for all three, in these requests:

- a bundle-local registry for external references ([knowledge-catalog #175](https://github.com/GoogleCloudPlatform/knowledge-catalog/issues/175));
- discovery across a set of bundles ([#302](https://github.com/GoogleCloudPlatform/knowledge-catalog/issues/302));
- collection-scoped metadata ([#214](https://github.com/GoogleCloudPlatform/knowledge-catalog/issues/214));
- an `imported` marker that does not inherit trust ([open-knowledge-format #15](https://github.com/GoogleCloudPlatform/open-knowledge-format/issues/15));
- partial visibility across a trust boundary ([#32](https://github.com/GoogleCloudPlatform/open-knowledge-format/issues/32)).

None had a maintainer's reply when read.

**What LOKF specifies.** Section 11 of the LOKF specification, "Federation: registries of bundles", answers in linked-data terms. A bundle publishes the four files `lokf export` writes, `graph.nt` among them. A registry is a `lokf-registry.yaml`, a DCAT catalogue of VoID datasets, one entry per member bundle keyed by its `base_iri`. Any IRI resolves to its owner by the longest matching `base_iri`, which the specification calls "pure string arithmetic" with "no network, no shared database". An IRI no member owns is "a tolerated dangling link, not an error". Member namespaces may not nest. The toolkit's `lokf registry init`, `add`, `list` and `resolve` implement the registry offline. The federated store that section 11.4 describes is informative there, and the sidecar's build supplies it.

**What this design adds: domains as manifests.** A domain is itself a thin LOKF bundle, kept in its own repository and released the same way. Its concepts are the member bundles: each a `Dataset` concept whose `distribution` names the release zip by `access_url`, whose `version` is the release tag, and whose `isPartOf` names the domain concept. A member may itself be a domain, and the build follows it tier by tier.

Each cross-bundle claim a domain makes is a concept with typed relations whose targets are full IRIs in the members' namespaces: that bundle A's term is bundle C's term, for example, or that A depends on C. LOKF has no catalogue class and no checksum slot, so the domain bundle carries a one-file domain schema, written as [the librarian's recipe](../skills/ktl-librarian/references/domain-schema.md) says. It defines `Domain` as a `Dataset` with `class_uri: dcat:Catalog`, `MemberBundle` as a `Dataset` with `checksum` and `release`, and `MemberDomain` for a member that is a domain. The same validator checks it.

Nothing is copied upward: a domain selects releases, so a new release of a member can never leave a stale copy inside the domain. A domain confirmation therefore attests two things only: that these members belong, and that the cross-bundle claims hold. Each member keeps its own labels. The **curator** confirms a membership concept as any other, and the **registrar**'s gate ties the confirmation to the person.

How a domain of domains is followed, how the workspace is built and swapped, what exists today and what an adopter decides: [A federation of bundles](federation.md).

## Sources

- Alexander, K., Cyganiak, R., Hausenblas, M. and Zhao, J. (2011). Describing Linked Datasets with the VoID Vocabulary. W3C Interest Group Note. <https://www.w3.org/TR/void/>
- Atlan (2026). Context layer. Atlan Documentation. <https://docs.atlan.com/agents/concepts/context-layer>
- Dehghani, Z. (2020). Data Mesh Principles and Logical Architecture. <https://martinfowler.com/articles/data-mesh-principles.html>
- GitHub. Artifact attestations. GitHub Docs. <https://docs.github.com/en/actions/concepts/security/artifact-attestations>
- Google Cloud (2026). Open Knowledge Format, specification version 0.2. <https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md>
- McVeety, S. and Hormati, A. (2026). Introducing the Open Knowledge Format. Google Cloud. <https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing>
- Nashawaty, P. and Weston, S. (2026). Enterprise AI Governance: The Operating Model AI Agents Need. Efficiently Connected. <https://www.efficientlyconnected.com/enterprise-ai-governance-operating-model/>
- Nichols, N. (2026). LOKF specification, version 0.2, section 11: Federation, registries of bundles. <https://lokf.nolan-nichols.com/specification/#11-federation-registries-of-bundles>. The toolkit as released at 0.8.0: <https://github.com/nicholsn/lokf/blob/v0.8.0/SPEC.md>
- Pilarinos, D. (2026). The Context Layer: What It Is and Why Every AI Agent Needs One. Unblocked. <https://getunblocked.com/blog/context-layer-ai-agents>
