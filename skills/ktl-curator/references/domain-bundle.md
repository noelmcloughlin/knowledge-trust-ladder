# A domain bundle: confirming that a bundle belongs

This page is for the **curator** of a domain host: a repository whose bundle names other repositories' knowledge bundles and whose releases build the workspace a reader queries across all of them. The design is the skills repository's [context layer page](https://w3id.org/ktl/docs/context-layer/), and the federation page it links to says how the workspace is built; the first such host is [ktl-federation](https://github.com/noelmcloughlin/ktl-federation). What follows is what its concepts are, what a confirmation of one attests, and what moves them.

## The four concept types

`templates/domain.yaml` in ktl-sidecar, laid down as `.lokf/domain.yaml` with `schema := "domain.yaml"` in the justfile, adds four classes over LOKF core. `lokf validate` checks them like any other.

- **`Domain`** (a `Dataset`, `dcat:Catalog`): the named set of bundles with one accountable owner. One concept, under `domains/`, named for the domain, as in `domains/ktl-federation`, and never for its position: the same domain is where its own build starts and a member of another domain. Its `unowned_targets` is the build's gate policy: `fail` stops the build on a typed relation whose target lies in no member's namespace; `report` lists it and goes on. Its `max_depth` is how many tiers of members the build follows when a member is itself a domain, 3 unless set.
- **`MemberBundle`** (a `Dataset`): one bundle the domain admits, under `members/`. It names the bundle's `base_iri`, the release `version` it pins, the `release` page, and one `distribution` whose `access_url` is the release's zip and whose `checksum` is that zip's digest. A second distribution names the schema released beside the zip (`schema-<tag>-<name>.yaml`), when the member's justfile names one; the build then validates the bundle against it rather than LOKF core alone. `isPartOf` names the domain concept.
- **`MemberDomain`** (a `MemberBundle`, `dcat:Catalog`): a member whose bundle is itself a domain. The build follows its members into the same workspace, tier by tier, as deep as `max_depth` allows. A `MemberBundle` whose zip turns out to hold a `Domain` concept is followed too, and the lock marks it a domain.
- **`ReleaseDistribution`** (a `Distribution`): the zip with its `checksum`, `sha256:` and 64 hex digits, as the release's `.sha256` file gives it.

A member names the newest release that carries a `knowledge-*.zip`, because a release whose bundle did not change carries none. Nothing is copied from a member into the domain: a member's new release changes nothing until a person confirms a member concept that names it.

The worked example is ktl-federation's `members/knowledge-trust-ladder.md`:

```yaml
type: MemberBundle
genre: reference
id: https://w3id.org/ktl/federation/knowledge/members/knowledge-trust-ladder
title: Knowledge Trust Ladder knowledge bundle
resource: https://github.com/noelmcloughlin/knowledge-trust-ladder/releases/tag/v0.43.0
base_iri: https://w3id.org/ktl/knowledge/
version: v0.43.0
release: https://github.com/noelmcloughlin/knowledge-trust-ladder/releases/tag/v0.43.0
distribution:
  - name: knowledge-v0.43.0-knowledge-trust-ladder.zip
    access_url: https://github.com/noelmcloughlin/knowledge-trust-ladder/releases/download/v0.43.0/knowledge-v0.43.0-knowledge-trust-ladder.zip
    media_type: application/zip
    checksum: sha256:a0a80fc411c23597968699716278d04918b795530f1fe55825709453eb6b8083
isPartOf:
  - https://w3id.org/ktl/federation/knowledge/domains/ktl-federation
```

## What a confirmation attests

Confirming a member concept is the ordinary confirm, in a signed commit the registrar's `provenance` job backs. It attests two things, and the note should say so: that this bundle belongs under the domain's admission rule, and that any claim the domain makes across bundles holds. It does not vouch for the member's own concepts; each member keeps its own trust labels, computed from its own events when the workspace is read.

A confirmation belongs to the concept's `id`. A concept moved to a new id waits for a confirmation of its own, and the `provenance` job reads an event copied across as a new confirmation.

Before confirming, open the release the concept names and check three things: the zip and its `.sha256` are attached, the digest in `.sha256` is the `checksum` in the concept, and the release's repository is the one the `base_iri` belongs to. The members script checked the zip's checksum and attestation when it wrote the change, and the pull request's hand-off lines say so. `knowledge-federate.py build --verify-only` checks the zip again before the merge, and also that its `index.md` names the member's `base_iri`. On GitHub the federation workflow's `check` job runs it on a pull request that touches `members/`. GitHub starts no workflow for a pull request the librarian's job token opened, so there it first runs when you push your confirmation. Elsewhere, run it yourself. `gh attestation verify <zip> --repo <owner>/<repo>` checks an attestation by hand.

A domain states its admission rule in its policy concept. A member:

- is released with the sidecar's release workflow;
- validates on LOKF core or on a schema the bundle publishes;
- has a stable `base_iri` under an authority its publisher controls, so no two members' namespaces nest;
- has one accountable owner.

A `.example` namespace fails the third.

## A member that is a domain

Every domain bounds a workspace of its own. The domain a build starts from is that build's top, and the same domain may be a member of another; a domain may not name itself or a domain above it. Confirming a `MemberDomain` attests that the domain belongs under the admission rule and who answers for it: the owner of that domain, whose own confirmations cover its members. It does not vouch for the members below it.

The diamond rule: two domains may name the same bundle. When both name the same release, the bundle joins once, and the lock records both domains. When they name different releases, the build stops, because one named graph holds one release; the two owners then agree on one. A model many domains share, an upper ontology such as gist or a domain model, is reached by several paths as a matter of course. The workspace index's "Named by" column says which domain's concept named each bundle.

## Cross-bundle claims

A claim the domain makes across bundles is a concept with typed relations whose targets are full IRIs in the members' namespaces, such as a glossary term `definedBy` one member's concept and `relatedTo` another's. It is the domain owner's arbitration, as the context layer page's "who arbitrates" decision describes, so the librarian proposes it as a question and the curator confirms it. The build resolves every such target against the registry: one no member owns fails the build under `fail`.

## What moves a member

The domain's librarian is a script, `knowledge-federate.py members`, which the sidecar's librarian workflow runs as `AGENT_CLI`, with the job's read-only token for the attestations ([automation.md](../../ktl-sidecar/references/automation.md#knowledge-federationyaml-the-workspace-of-a-domain-host) has the variables). It lists each member's releases, picks the newest that carries a bundle zip, verifies its checksum and attestation, and writes the move as a `patch` with a `question` for the pen. The pen restamps `generated`, so the member reads "edited since a person confirmed it" until you confirm the new release, and the health line counts it among what moved. Accepting the move is the same confirm again, after the same three checks; declining it is a note on the concept, or closing the pull request.

A new member starts the same way. `knowledge-federate.py members --add <owner>/<repo>` verifies that repository's newest bundle release, reads its `base_iri`, title and description from the zip, refuses a namespace that nests with a member's, and writes a `create` with a `question` for the pen. When that release is itself a domain, the concept is a `MemberDomain`, and its body says how many members the build will follow. The concept arrives as a draft; your confirmation admits it.

## Reading the workspace

The workspace is served under `/workspace/` of the host's site, its `index.md` first, and attached to each release as `workspace-<tag>.zip`. The index lists the members, their versions, which domain named each and their health lines at the release. `queries/labels.rq` computes every concept's trust label with the bundle that asserted it, `queries/moved.rq` lists the members that moved since the domain's last confirmation, and `queries/unowned.rq` is the gate.

Three ways to read it, each from the host's sidecar environment, or anywhere with `--snapshot <path>` pointing at an unpacked `workspace-<tag>.zip`:

- **An agent, over MCP.** `uv run --project .lokf .lokf/scripts/knowledge-federate.py mcp` is the `lokf-registry` server the LOKF specification's section 11.4 describes. `resolve_iri` says which bundle owns an IRI and what concept it names. `neighbors` and `subgraph` give a neighbourhood bounded in hops and size. `federated_sparql` queries the union with `GRAPH ?g` binding the asserting bundle, and takes a stored query by name, such as `labels.rq`. `read_document` returns a concept as released with its trust summary. The server's instructions are the workspace index, so an agent reads it before anything else. Register it as any stdio server: the command above, with the host as the working directory.
- **A person, over SPARQL.** `knowledge-federate.py serve` opens the toolkit's SPARQL endpoint and graph page over the union of the graphs.
- **A read-only endpoint from a container**, for a team: load `graph.nq` once and serve it with the Oxigraph server image, which answers queries and refuses updates.

  ```bash
  podman run --rm -v "$PWD/snapshot:/snapshot:ro" -v oxigraph-data:/data ghcr.io/oxigraph/oxigraph:0.5.11 load --location /data --file /snapshot/graph.nq
  podman run -d -p 7878:7878 -v oxigraph-data:/data:ro ghcr.io/oxigraph/oxigraph:0.5.11 serve-read-only --location /data --bind 0.0.0.0:7878 --union-default-graph
  ```

  `docker` takes the same arguments. The endpoint is then `http://localhost:7878/query`; `GRAPH ?g { ... }` still names the asserting bundle, and `--union-default-graph` lets a query without `GRAPH` see every bundle. Nothing is hosted by default: that is the team's decision, and the container is the whole setup.
