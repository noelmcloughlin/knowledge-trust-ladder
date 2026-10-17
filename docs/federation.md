# A federation of bundles: domains, tiers and the workspace

> [!NOTE]
> This page is for whoever runs a domain host of Knowledge Trust Ladder (KTL), or reads its workspace. It says how a domain names bundles and other domains, how the workspace is built and kept current, what exists today, and what an adopter decides. [The curated context layer](context-layer.md) says what a context layer is and why KTL federates by domains. The templates were released on 2026-10-16 in ktl-sidecar, and [ktl-federation](https://w3id.org/ktl/federation/) is the first host. The curator's [domain-bundle.md](../skills/ktl-curator/references/domain-bundle.md) has the worked example, and the sidecar's [automation.md](../skills/ktl-sidecar/references/automation.md#knowledge-federationyaml-the-workspace-of-a-domain-host) the workflow and its variables.

A *domain* is a named set of bundles with one accountable owner, kept as a thin LOKF bundle in a repository of its own. A domain may name other domains. The domain a build starts from is that build's *top domain*, and the same domain may be a member of another. *The workspace* is the graph built from the top domain's members, one named graph per bundle.

## Tiers: a domain of domains

A member whose released bundle is itself a domain is followed: its members join the same workspace, and the lock says which domain named each. A tree of domains ends at bundles the way a flat domain does. A company's legal structure is one such tree, a legal domain of lines of business, each a domain of business segments; a competence structure is a second tree over the same bundles. Each tier is a repository of its own, with its own curator and its own releases.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../.assets/ktl-federation-tiers-dark.svg">
    <img src="../.assets/ktl-federation-tiers.svg" alt="Tiers of domains, each box labelled with its domain concept's path and its namespace, https://w3id.org/ then the publisher's w3id namespace, the project and knowledge/: domains/federation, where this build starts and perhaps a member of another domain, names domains/domain1 and domains/domain2; each names a domain in turn, domains/domain3 and domains/domain4; those name the bundles, any number under each, drawn as a stack, and one shared model such as gist-linkml, biolink-model or the FINOS CDM, named by both at one release, so it joins once. Each card carries a small ladder whose rungs are the three actors and three pills reading derived, checked and confirmed, green for an agent, gold for deterministic tools, blue for a named person; each domain box carries the same three dots. Below, four numbered rules: every domain bounds a workspace of its own; confirming a domain member attests that it belongs and who answers for it; the diamond rule; and max_depth, with a note that every namespace takes that form, a domain's beside its members', never above them." width="720" />
  </picture>
</p>

Four rules keep a tree of domains sound.

1. **Every domain bounds a workspace of its own.** The domain a build starts from is that build's top; the same domain may be a member of another, and its own build knows nothing of the one above. A member concept is typed `MemberDomain` when the bundle it names is a domain, so a reader of the manifest sees a delegation without unpacking the zip. A `MemberBundle` whose zip holds a `Domain` concept is followed all the same, and the lock marks it.
2. **Confirming a domain confirms the delegation.** The upper curator's confirmation of a domain member attests that the domain belongs and who answers for it, not what its members say. Each tier's owner answers for that tier, as [Lines are roles, not people](three-lines.md#lines-are-roles-not-people) says a role is held.
3. **The diamond rule.** Two domains may name the same bundle. When both name the same release, the bundle joins the workspace once, and the lock records both domains, because both name the same file. When they name different releases, the build stops, because one named graph holds one release; the two owners then agree on one. A model many domains share, an upper ontology such as gist or a domain model, is the ordinary case, not the edge: every sub-domain that links to its terms names it.
4. **The depth is the top domain's to set.** `max_depth` on the top `Domain` concept is how many tiers of members the build follows, 3 unless set, and the domain's own members are tier 1. A domain found at the last tier stops the build rather than being cut without a word. A domain may not name itself or a domain above it.

Namespaces may mirror the tree. The registry refuses one `base_iri` nested inside another, and a path hierarchy satisfies it when each tier's namespace ends in its own segment: `https://corp.example/knowledge/`, `https://corp.example/legal/knowledge/` and `https://corp.example/legal/lob-a/knowledge/` are accepted together, and `https://corp.example/legal/` alone is refused. The gate is the top domain's: one workspace has one `unowned_targets`, and a sub-domain's applies to its own build.

## How the workspace stays current

The workspace is a materialised view of the top domain, built ahead of time and rebuilt on publish, by a job that runs no agent.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../.assets/ktl-context-workspace-dark.svg">
    <img src="../.assets/ktl-context-workspace.svg" alt="How the context workspace stays current: a publish event in the artifact repository starts a refresh job that resolves, verifies, builds and swaps; inside the workspace a manifest and lock, the released bundle files and one named graph per bundle sit behind a read interface that readers query over MCP or SPARQL." width="720" />
  </picture>
</p>

1. **A publish event starts it.** Artifactory sends a webhook when an artifact is "deployed to a repository", and its documentation shows that webhook starting a GitHub Actions workflow through `workflow_dispatch`, with the artifact path as an input. A forge's own release event does the same for GitHub Releases.
2. **Resolve.** The job reads the top domain's manifest, follows each domain to its members, and writes a lock: one entry per release with its URL, its checksum, its tier and the domains that named it.
3. **Verify.** Each zip is checked against its `.sha256`, and on GitHub against its attestation with `gh attestation verify`. A failure stops the job, and the old snapshot stays.
4. **Register and export.** Each release is unpacked, registered with `lokf registry add` and exported with `lokf export`. Registering it counts its triples and checks that its concepts sit under its declared `base_iri`.
5. **Load.** Each `graph.nt` goes into a named graph whose IRI is the bundle's `base_iri`, as section 11.4 of the LOKF specification intends. In SPARQL, `GRAPH ?g` then says which bundle asserted a triple.
6. **Gate.** `lokf validate --check-refs` resolves only targets inside a bundle's own namespace, so a link from A to C is first checkable here. The job lists every out-of-namespace target by SPARQL and resolves each against the registry. An unowned IRI fails the build, or is reported, as the domain's policy says.
7. **Swap.** The new graphs replace the old under one snapshot version, in one atomic step. A reader never sees half a federation.

**Pre-built is not pre-loaded.** Anthropic's guidance is that agents "maintain lightweight identifiers (file paths, stored queries, web links, etc.) and use these references to dynamically load data into context at runtime", which "enables progressive disclosure". OKF gives `index.md` the same job, "to support progressive disclosure". So the workspace serves the index first and lets a reader traverse on demand, over a SPARQL endpoint and a Model Context Protocol (MCP) server.

**Trust at read time.** No trust label is stored in the snapshot, because a snapshot that stores labels drifts from what it describes within a day. SPARQL over `generated` and `verified` gives the same labels the report script computes from frontmatter ([the same labels as SPARQL](../skills/ktl-curator/references/queries.md)), against the clock at the moment of the query. A concept reads as past its review date the day after that date, with no rebuild. A release is the only event that changes a graph, and the publish hook catches every release.

## What exists today, and what is design

| Part | Status | Where |
| --- | --- | --- |
| A bundle validated, packed, checksummed, attested and attached to a release | exists | `knowledge-release.yaml` in the sidecar's templates |
| The registrar's gate and the report script | exist | [the fifth role](architecture.md#the-fifth-role-which-is-not-a-skill) |
| `lokf export`: `graph.nt`, `concepts.jsonld`, `graph.json`, `datasets.jsonld` | exists | lokf 0.8.0 |
| `lokf registry init`, `add`, `list` and `resolve`: the routing table, offline | exists | lokf 0.8.0, specification sections 11.1 to 11.3 |
| `lokf serve`, `query` and `mcp` over one bundle | exist | lokf 0.8.0 |
| `lokf tables` to Parquet, with BigQuery or Athena table definitions | exists | lokf 0.8.0 |
| Domains as thin bundles, their domain schema, a person's confirmation of membership | exists | `domain.yaml` in the sidecar's templates; the first host, [ktl-federation](https://w3id.org/ktl/federation/), whose members are this bundle, ai-linkmo's and lmodel/gist's; the curator's [domain-bundle.md](../skills/ktl-curator/references/domain-bundle.md) |
| The lock, the refresh job and the atomic swap | exists | `knowledge-federate.py` and `knowledge-federation.yaml` in the sidecar's templates ([automation.md](../skills/ktl-sidecar/references/automation.md#knowledge-federationyaml-the-workspace-of-a-domain-host)) |
| One named graph per bundle | exists | `knowledge-federate.py build` |
| A domain of domains: tiers followed to the depth the top domain sets, the diamond rule, a `MemberDomain` type | exists | `knowledge-federate.py build` and `domain.yaml` ([Tiers](#tiers-a-domain-of-domains)) |
| A `lokf-registry` MCP server: `resolve_iri`, `neighbors`, `subgraph`, `federated_sparql`, `read_document` | exists | `knowledge-federate.py mcp`, over the workspace, the index as its instructions; specification section 11.4 |
| A read-only SPARQL endpoint over the workspace | exists | `knowledge-federate.py serve`, or the Oxigraph server image loading `graph.nq` ([domain-bundle.md](../skills/ktl-curator/references/domain-bundle.md#reading-the-workspace)) |
| A domain schema released beside its bundle | exists | `knowledge-release.yaml` attaches `schema-<tag>-<name>.yaml` when the justfile names one; the build validates the member against it |
| Lazy loading of a member's graph on first use | design | specification section 11.4, marked informative; the workspace loads every member at build |
| Harvesting remote artifacts, and the `sensitivity` gate | design | specification section 11.5; the field exists, and nothing reads it |
| Per-query permissions | design | the store's and the artifact repository's access control, not the bundle's |

## Decisions an adopter must make

- **Pin or float.** This design pins: each member concept names one release, and a person's confirmation of the domain covers those releases. A member's new release changes nothing until a person confirms a domain release that names it, so a pinned domain needs a release of its own for every member release. A manifest that floats on a range is fresher, but its curator has not seen each release it picks up. The workspace's lock then holds the exact releases, as package managers keep broad requirements in a project file and exact versions in a lockfile. Either way, the report must say, at each tier, which members have moved since the domain was last confirmed.
- **Pin across tiers.** Pinning compounds: a leaf's release reaches the top workspace only after a confirmation and a release at every tier between. The templates pin at every tier today. The decision left open is whether a domain member may float on its sub-domain's newest release, so that an upper tier's confirmation attests membership and ownership rather than one release, while leaf members stay pinned where the content is.
- **Cross-bundle links.** Make the resolution step a build gate from the start. A dangling link that a bundle must tolerate, as OKF requires, is a defect in a domain, because a person confirmed the claim it belongs to.
- **Stable IRIs.** Keep each bundle's `base_iri` constant across releases and record the version on the graph's metadata, or every cross-bundle edge breaks at each release. Give a domain a namespace beside its members', never above them: the registry refuses a `base_iri` that nests inside another, and a path that mirrors the tree satisfies it when each tier's namespace ends in its own segment ([Tiers](#tiers-a-domain-of-domains)).
- **Who arbitrates.** When A and C define one term differently, the domain's owner decides, and the decision is a confirmed concept in the domain bundle, not a rewrite of either member. Atlan's "Conflicts get arbitrated, not duplicated" names the duty, and [Lines are roles, not people](three-lines.md#lines-are-roles-not-people) says who may hold it.
- **Vocabulary fit.** A concept whose type is outside the schema is tolerated as a generic concept and carries no agreed meaning. Admit a bundle to a domain on vocabulary fit, and publish each domain schema as an artifact so the workspace can load it ([when the vocabulary stops fitting](for-the-curious.md#when-the-vocabulary-stops-fitting)).
- **What a member adds.** A domain admits a bundle on its admission rule: released with the sidecar's workflow, validating against a published schema, a stable namespace under an authority its publisher controls, one accountable owner. Whether a member adds value is another test, and the strict one is whether readers query across it or other members link into it. A federation whose members never link to one another has proved its mechanism, not yet its worth. A public bundle cannot decline to be catalogued, as with any public dataset; the domain's owner answers for the admission.
- **Permissions.** OKF is explicit: "Trust tiers are advisory signals, not access control." Section 11.5 of the LOKF specification keeps credentials out of the registry and admits public artifacts or local checkouts only. Per-query permission lives in the artifact repository and in the store the workspace runs on. A bundle that must not be seen whole does not join a domain.

## Sources

- Anthropic (2025). Effective context engineering for AI agents. <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>
- Atlan (2026). Context layer. Atlan Documentation. <https://docs.atlan.com/agents/concepts/context-layer>
- GitHub. Artifact attestations. GitHub Docs. <https://docs.github.com/en/actions/concepts/security/artifact-attestations>
- Google Cloud (2026). Open Knowledge Format, specification version 0.2. <https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md>
- Harris, S. and Seaborne, A. (2013). SPARQL 1.1 Query Language, section 13. W3C Recommendation. <https://www.w3.org/TR/sparql11-query/>
- JFrog. Webhook Event Types, and Trigger a GitHub Action using a Custom Webhook. <https://docs.jfrog.com/integrations/docs/webhook-event-types>, <https://docs.jfrog.com/integrations/docs/trigger-a-github-action-using-a-custom-webhook>
- Nichols, N. (2026). LOKF specification, version 0.2, section 11: Federation, registries of bundles. <https://lokf.nolan-nichols.com/specification/#11-federation-registries-of-bundles>. The toolkit as released at 0.8.0: <https://github.com/nicholsn/lokf/blob/v0.8.0/SPEC.md>
