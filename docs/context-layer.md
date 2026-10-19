# The curated context layer: one bundle, and a federation of bundles

> [!NOTE]
> This page is for anyone deciding what a context layer is, what one Knowledge Trust Ladder (KTL) bundle provides, and why KTL federates LOKF bundles through domains. Each quotation is from the source's own text, read on 2026-10-12. [A federation of bundles](federation.md) says how a federation is built and run, and [What a KTL context layer integrates with](context-layer-technology.md) names the products a workspace can use.

Below, a *context layer* is a governed layer between an organisation's sources and whoever consumes them, a person or an agent, that persists from one task to the next. *The bundle* is the corpus KTL keeps in `.lokf/knowledge/`, one Markdown concept per file.

## What people mean by a context layer

Unblocked states the minimum: "A real context layer in 2026 has four non-negotiable properties: heterogeneous source ingestion, on-demand surfacing, cross-source conflict resolution, and per-query permission enforcement." Atlan adds what enterprise scale requires: "Multi-domain federation. Each domain owns its definitions but contributes to one graph. Conflicts get arbitrated, not duplicated." Zhamak Dehghani named that shape in 2020 for data mesh: "federated computational governance" under "a set of global rules".

The ownership point is older than the agents. Efficiently Connected notes that federation technology "cannot make a Head of Retail Banking agree to share definitional ownership with an AML team", and that conversational agents return "whichever definition they encountered most frequently".

Google Cloud's Open Knowledge Format (OKF) "formalizes the LLM-wiki pattern into a portable, interoperable format": "a directory of markdown files with YAML frontmatter". Under "Format, not platform", Google adds: "No complex compression scheme, no new runtime, no required SDK." A format leaves the work open: what counts as trusted knowledge, how updates are reviewed, and what a consumer does with an unknown type or stale context. KTL exists for that work, and [Prose, Structure, Meaning, Context](architecture.md#prose-structure-meaning-context) says how it reads OKF's trust goal.

## One bundle is one repository's context layer

The table sets Unblocked's four properties, and the two the others add, against what a bundle does.

| In the discourse | In a KTL bundle | Where it stops |
| --- | --- | --- |
| Heterogeneous source ingestion | The **librarian** derives each concept from a source it names in `resource` and `sources` ([who writes the bundle](for-the-curious.md#who-writes-the-bundle-and-what-checks-it)) | One repository's sources. A second repository is a second bundle |
| On-demand surfacing | A reader opens `index.md` first. The **docent** answers from the bundle and labels each concept it used ([the index as the retrieval interface](for-the-curious.md#how-readers-and-verdicts-steer-the-next-run)) | Files, and one in-process graph, until something serves them |
| Cross-source conflict resolution | The **curator**, a named person, records the verdict: confirm, correct, retire or send back. A reader's disagreement goes to `feedback.md` | One bundle. Between bundles, a domain's owner arbitrates ([who arbitrates](federation.md#decisions-an-adopter-must-make)) |
| Per-query permission enforcement | None of its own. The repository's access control is the bundle's | Nothing finer than the repository |
| Provenance and trust | `generated` and `verified` events on every concept, and each label computed on read, never stored ([Trust stays visible](architecture.md#trust-stays-visible), [four levels of checking](for-the-curious.md#four-levels-of-checking)) | Who checked and when, not that the source is right |
| Format, not platform | LOKF, a semantic profile of OKF: Markdown a person reads, a LinkML schema that checks it, a graph any SPARQL store loads | A domain outside LOKF's vocabulary needs a [domain schema](for-the-curious.md#when-the-vocabulary-stops-fitting) |

So one bundle is already one repository's context layer, with the fourth of Unblocked's properties left to whatever hosts it.

## Many bundles federated into one context layer: the design

OKF calls a bundle "The unit of distribution", as a git repository, a tarball or zip, or a subdirectory of a larger repository. It says nothing about one bundle naming another, a catalogue of bundles, or what a reader may see of a bundle across a trust boundary. Its trackers ask for all three:

- a bundle-local registry for external references ([knowledge-catalog #175](https://github.com/GoogleCloudPlatform/knowledge-catalog/issues/175));
- discovery across a set of bundles ([#302](https://github.com/GoogleCloudPlatform/knowledge-catalog/issues/302));
- collection-scoped metadata ([#214](https://github.com/GoogleCloudPlatform/knowledge-catalog/issues/214));
- an `imported` marker that does not inherit trust ([open-knowledge-format #15](https://github.com/GoogleCloudPlatform/open-knowledge-format/issues/15));
- partial visibility across a trust boundary ([#32](https://github.com/GoogleCloudPlatform/open-knowledge-format/issues/32)).

None had a maintainer's reply when read.

Section 11 of the LOKF specification answers in linked-data terms: a registry of bundles, each keyed by its namespace, through which any IRI resolves to the bundle that owns it. KTL adds who answers for the set. A *domain* is a thin bundle in a repository of its own that selects released bundles, and one accountable owner confirms each bundle it admits. A domain may select domains in turn, and a build turns the one it starts from into one workspace, one named graph per bundle. [A federation of bundles](federation.md) says how.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../.assets/ktl-federated-context-layer-dark.svg">
    <img src="../.assets/ktl-federated-context-layer.svg" alt="Drawn bottom to top, from repository bundles to a context layer and its readers: four bundles, each released from its own repository into an artifact repository; domains as manifests that select releases and are confirmed by a person, labelled domains/domain1, domains/domain2 and domains/federation, where the build starts; one context layer built from domains/federation; and, at the top, the readers." width="720" />
  </picture>
</p>

***As a flow diagram, drawn with Archify: [light](../.assets/companions/ktl-federated-context-layer.svg), [dark](../.assets/companions/ktl-federated-context-layer-dark.svg).***

## Sources

- Atlan (2026). Context layer. Atlan Documentation. <https://docs.atlan.com/agents/concepts/context-layer>
- Dehghani, Z. (2020). Data Mesh Principles and Logical Architecture. <https://martinfowler.com/articles/data-mesh-principles.html>
- Google Cloud (2026). Open Knowledge Format, specification version 0.2. <https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md>
- McVeety, S. and Hormati, A. (2026). Introducing the Open Knowledge Format. Google Cloud. <https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing>
- Nashawaty, P. and Weston, S. (2026). Enterprise AI Governance: The Operating Model AI Agents Need. Efficiently Connected. <https://www.efficientlyconnected.com/enterprise-ai-governance-operating-model/>
- Nichols, N. (2026). LOKF specification, version 0.2, section 11: Federation, registries of bundles. <https://lokf.nolan-nichols.com/specification/#11-federation-registries-of-bundles>. The toolkit as released at 0.8.0: <https://github.com/nicholsn/lokf/blob/v0.8.0/SPEC.md>
- Pilarinos, D. (2026). The Context Layer: What It Is and Why Every AI Agent Needs One. Unblocked. <https://getunblocked.com/blog/context-layer-ai-agents>
