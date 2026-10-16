# A domain bundle: confirming that a bundle belongs

This page is for the **curator** of a domain host: a repository whose bundle names other repositories' knowledge bundles and whose releases build the workspace a reader queries across all of them. The design is the skills repository's [context layer page](https://noelmcloughlin.github.io/knowledge-trust-ladder/docs/context-layer/); the first such host is [ktl-federation](https://github.com/noelmcloughlin/ktl-federation). What follows is what its concepts are, what a confirmation of one attests, and what moves them.

## The three concept types

`templates/domain.yaml` in ktl-sidecar, laid down as `.lokf/domain.yaml` with `schema := "domain.yaml"` in the justfile, adds three classes over LOKF core. `lokf validate` checks them like any other.

- **`Domain`** (a `Dataset`, `dcat:Catalog`): the named set of bundles with one accountable owner. One concept, under `domains/`. Its `unowned_targets` is the build's gate policy: `fail` stops the build on a typed relation whose target lies in no member's namespace; `report` lists it and goes on.
- **`MemberBundle`** (a `Dataset`): one bundle the domain admits, under `members/`. It names the bundle's `base_iri`, the release `version` it pins, the `release` page, and one `distribution` whose `access_url` is the release's zip and whose `checksum` is that zip's digest. `isPartOf` names the domain concept.
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
- https://w3id.org/ktl/federation/knowledge/domains/top
```

## What a confirmation attests

Confirming a member concept is the ordinary confirm, in a signed commit the registrar's `provenance` job backs. It attests two things, and the note should say so: that this bundle belongs under the domain's admission rule, and that any claim the domain makes across bundles holds. It does not vouch for the member's own concepts; each member keeps its own trust labels, computed from its own events when the workspace is read.

Before confirming, open the release the concept names and check three things: the zip and its `.sha256` are attached, the digest in `.sha256` is the `checksum` in the concept, and the release's repository is the one the `base_iri` belongs to. The federation workflow's `check` job does the same against the real zip on every pull request that touches `members/`, and `gh attestation verify <zip> --repo <owner>/<repo>` confirms which workflow built it.

A domain states its admission rule in its policy concept. A member:

- is released with the sidecar's release workflow;
- validates on LOKF core or on a schema the bundle publishes;
- has a stable `base_iri` under an authority its publisher controls, so no two members' namespaces nest;
- has one accountable owner.

A `.example` namespace fails the third.

## Cross-bundle claims

A claim the domain makes across bundles is a concept with typed relations whose targets are full IRIs in the members' namespaces, such as a glossary term `definedBy` one member's concept and `relatedTo` another's. It is the domain owner's arbitration, as the context layer page's "who arbitrates" decision describes, so the librarian proposes it as a question and the curator confirms it. The build resolves every such target against the registry: one no member owns fails the build under `fail`.

## What moves a member

The domain's librarian is a script, `knowledge-federate.py members`, which the sidecar's librarian workflow runs as `AGENT_CLI`. It lists each member's releases, picks the newest that carries a bundle zip, verifies its checksum and attestation, and writes the move as a `patch` with a `question` for the pen. The pen restamps `generated`, so the member reads "edited since a person confirmed it" until you confirm the new release, and the health line counts it among what moved. Accepting the move is the same confirm again, after the same three checks; declining it is a note on the concept, or closing the pull request.

## Reading the workspace

The workspace is served under `/workspace/` of the host's site and attached to each release as `workspace-<tag>.zip`. Its `index.md` lists the members, their versions and their health lines at the release. `queries/labels.rq` computes every concept's trust label with the bundle that asserted it, `queries/moved.rq` lists the members that moved since the domain's last confirmation, and `queries/unowned.rq` is the gate. `knowledge-federate.py serve` opens the toolkit's SPARQL endpoint and graph page over it.
