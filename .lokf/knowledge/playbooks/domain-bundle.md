---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/domain-bundle
genre: how-to
title: Curating a domain bundle
description: How the curator of a domain host confirms that a bundle belongs, what the domain's four concept types hold, what moves a member, and how to read the workspace the domain's releases build.
resource: skills/ktl-curator/references/domain-bundle.md
sources:
  - resource: skills/ktl-curator/references/domain-bundle.md
  - resource: skills/ktl-sidecar/templates/domain.yaml
  - resource: docs/federation.md
dependsOn:
  - https://w3id.org/ktl/knowledge/playbooks/ktl-curator-skill
relatedTo:
  - https://w3id.org/ktl/knowledge/explanation/context-layer
  - https://w3id.org/ktl/knowledge/glossary/domain-schema
about:
  - https://w3id.org/ktl/knowledge/glossary/context-layer
generated:
  by: process:ktl-librarian
  at: "2026-10-18T12:25:08Z"
status: draft
---

# Overview

A **domain host** is a repository whose bundle names other repositories' knowledge bundles, and whose releases build the workspace a reader queries across all of them. Its curator confirms that each bundle belongs. `skills/ktl-curator/references/domain-bundle.md` says what the domain's concepts are, what a confirmation of one attests, what moves a member, and how to read the workspace. The first such host is ktl-federation.

# The four concept types

ktl-sidecar's `templates/domain.yaml` is laid down as `.lokf/domain.yaml`, with `schema := "domain.yaml"` in the justfile. It adds four classes over LOKF core, and `lokf validate` checks them like any other.

- **`Domain`** (a `Dataset`, `dcat:Catalog`): the named set of bundles with one accountable owner. It is one concept under `domains/`, named for the domain, as in `domains/ktl-federation`, and never for its position, because the same domain is where its own build starts and a member of another domain. Its `unowned_targets` is the build's gate policy: `fail` stops the build on a typed relation whose target lies in no member's namespace, and `report` lists it and goes on. Its `max_depth` is how many tiers of members the build follows, 3 unless set.
- **`MemberBundle`** (a `Dataset`): one bundle the domain admits, under `members/`. It names the bundle's `base_iri`, the release `version` it pins, the `release` page, and one `distribution` whose `access_url` is the release's zip and whose `checksum` is that zip's digest. A second distribution names the schema released beside the zip, `schema-<tag>-<name>.yaml`, when the member's justfile names one, and the build then validates the bundle against it. `isPartOf` names the domain concept.
- **`MemberDomain`** (a `MemberBundle`, `dcat:Catalog`): a member whose bundle is a domain in turn. The build follows its members into the same workspace, tier by tier, as deep as `max_depth` allows. A `MemberBundle` whose zip holds a `Domain` concept is followed too, and the lock marks it a domain.
- **`ReleaseDistribution`** (a `Distribution`): the zip with its `checksum`, `sha256:` and 64 hexadecimal digits, as the release's `.sha256` file gives it.

A member names the newest release that carries a `knowledge-*.zip`, because a release whose bundle did not change carries none. Nothing is copied from a member into the domain, so a member's new release changes nothing until a person confirms a member concept that names it.

# The worked example

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

A member released somewhere the members script cannot list is written and moved by hand from this example. The build fetches its zip from any `https` address and checks it against the `checksum`.

# What a confirmation attests

Confirming a member concept is the curator's ordinary confirm, in a signed commit the registrar's `provenance` job backs. It attests two things: that the bundle belongs under the domain's admission rule, and that any claim the domain makes across bundles holds. It does not vouch for the member's own concepts. Each member keeps its own trust labels, computed from its own events when the workspace is read.

A confirmation belongs to the concept's `id`. A concept moved to a new id waits for a confirmation of its own, and the `provenance` job reads an event copied across as a new confirmation.

Before confirming, open the release the concept names and check three things:

1. the zip and its `.sha256` are attached to the release;
2. the digest in `.sha256` is the `checksum` in the concept;
3. the release's repository is the one the `base_iri` belongs to.

`knowledge-federate.py build --verify-only` checks the zip again before the merge, and also that its `index.md` names the member's `base_iri`. `gh attestation verify <zip> --repo <owner>/<repo>` checks an attestation by hand.

The domain states its admission rule in its policy concept. A member is released with the sidecar's release workflow, validates on LOKF core or on a schema the bundle publishes, has a stable `base_iri` under an authority its publisher controls, and has one accountable owner.

# A member that is a domain

Every domain bounds a workspace of its own, and a domain may not name itself or a domain above it. Confirming a `MemberDomain` attests that the domain belongs under the admission rule and who answers for it: the owner of that domain, whose own confirmations cover its members. It does not vouch for the members below it.

The diamond rule: when two domains name the same bundle at the same release, the bundle joins once, and the lock records both domains. When they name different releases, the build stops, because one named graph holds one release. The two owners then agree on one release. The workspace index's "Named by" column says which domain's concept named each bundle.

# What moves a member

The domain's librarian is a script, `knowledge-federate.py members`, which the sidecar's librarian workflow runs as `AGENT_CLI`. It picks each member's newest release that carries a bundle zip, verifies its checksum and attestation, and writes the move for the pen with a question for the curator. The member then reads as edited since a person confirmed it, until a person confirms the new release after the same three checks. `knowledge-federate.py members --add <owner>/<repo>` drafts a new member the same way, and drafts a `MemberDomain` when that release is a domain.

A member leaves when the curator retires its concept. The concept stays for links and history with `status: deprecated`, the next build leaves its bundle out of the workspace, and the members script proposes no move for it. The build passes over a retired `Domain` concept the same way, so a renamed domain's old concept can stay beside the new one.

# Reading the workspace

The workspace is served under `/workspace/` of the host's site, its `index.md` first, and is attached to each release as `workspace-<tag>.zip`. `queries/labels.rq` computes every concept's trust label with the bundle that asserted it, `queries/moved.rq` lists the members that moved since the domain's last confirmation, and `queries/unowned.rq` is the gate.

There are three ways to read it, each from the host's sidecar environment, or anywhere with `--snapshot <path>` pointing at an unpacked `workspace-<tag>.zip`:

- **An agent, over MCP.** `uv run --project .lokf .lokf/scripts/knowledge-federate.py mcp` is the `lokf-registry` Model Context Protocol (MCP) server that section 11.4 of the LOKF specification describes, with the tools `resolve_iri`, `neighbors`, `subgraph`, `federated_sparql` and `read_document`. Its instructions are the workspace index, so an agent reads the index first. Register it as any stdio server, with the host as the working directory.
- **A person, over SPARQL.** `knowledge-federate.py serve` opens the toolkit's SPARQL endpoint and graph page over the union of the graphs.
- **A team, from a container.** Load `graph.nq` once and serve it read-only with the Oxigraph server image:

```bash
podman run --rm -v "$PWD/snapshot:/snapshot:ro" -v oxigraph-data:/data ghcr.io/oxigraph/oxigraph:0.5.11 load --location /data --file /snapshot/graph.nq
podman run -d -p 7878:7878 -v oxigraph-data:/data:ro ghcr.io/oxigraph/oxigraph:0.5.11 serve-read-only --location /data --bind 0.0.0.0:7878 --union-default-graph
```

`docker` takes the same arguments. The endpoint is then `http://localhost:7878/query`. `GRAPH ?g { ... }` still names the asserting bundle, and `--union-default-graph` lets a query without `GRAPH` see every bundle. Nothing is hosted by default: hosting is the team's decision.
