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
  at: "2026-10-19T12:30:15Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-19T20:01:11Z"
---

# Overview

A **domain host** is a repository whose bundle names other repositories' knowledge bundles, and whose releases build the workspace a reader queries across all of them. Its curator confirms that each bundle belongs, as `skills/ktl-curator/references/domain-bundle.md` says step by step, and `docs/federation.md` holds the design. The first such host is ktl-federation.

# The four concept types

ktl-sidecar's `templates/domain.yaml` is laid down as `.lokf/domain.yaml`, with `schema := "domain.yaml"` in the justfile. It adds four classes over LOKF core, and `lokf validate` checks them like any other. Neither Obsidian plugin can read that file, so list `Domain`, `MemberBundle` and `MemberDomain` under *Known LOKF types* in both.

- **`Domain`** (a `Dataset`, `dcat:Catalog`): the named set of bundles with one accountable owner, one concept under `domains/` named for the domain and never for its position. The build reads three settings as a person last confirmed them. Under `unowned_targets`, `fail` stops the build on a link into no member's namespace, or to no concept of the member whose namespace holds it, and `report` lists it. `max_depth` is how many tiers the build follows, 3 unless set. `sensitivity` is `public` unless set, and `internal` admits internal members, only in a private or internal repository.
- **`MemberBundle`** (a `Dataset`): one admitted bundle, under `members/`. It names the bundle's `base_iri`, the release `version` it pins, the `release` page, and a `distribution` whose `access_url` is the release's zip and whose `checksum` is its digest. A bundle that releases no zip is named by the `concepts.jsonld` its site serves, with that file's checksum. A second distribution names a schema released beside the zip, and the build validates against it. `isPartOf` names the domain. Its `sensitivity` is `public` unless set, `internal`, or `confidential`, which joins no workspace.
- **`MemberDomain`** (a `MemberBundle`, `dcat:Catalog`): a member whose bundle is a domain in turn. The build follows its members into the same workspace, as deep as `max_depth` allows, and follows a `MemberBundle` whose zip holds a `Domain` concept too.
- **`ReleaseDistribution`** (a `Distribution`): the file with its `checksum`, `sha256:` and 64 hexadecimal digits.

A member names the newest release that carries a `knowledge-*.zip`. Nothing is copied into the domain, so a member's new release changes nothing until a person confirms a member concept that names it.

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

# What a confirmation attests

Confirming a member concept is the curator's ordinary confirm, in a signed commit the registrar's `provenance` job backs. It attests that the bundle belongs under the domain's admission rule, and that any claim the domain makes across bundles holds. It does not vouch for the member's own concepts, whose labels come from their own events. A claim across bundles is the domain owner's arbitration, so the librarian proposes it as a question. A confirmation belongs to the concept's `id`, so a concept moved to a new id waits for one of its own.

Before confirming, open the release the concept names. Check that the zip and its `.sha256` are attached, that the digest is the concept's `checksum`, and that the release's repository is the one the `base_iri` belongs to. Check a `MemberDomain`'s `workspace-<tag>.zip` the same way, and a served member's file by its digest. When the bundle's subject is not public, set its `sensitivity` first. `knowledge-federate.py build --verify-only` checks the zip again and runs the gate before the merge.

The domain's policy concept states its admission rule. A member is released with the sidecar's release workflow, validates on LOKF core or on a schema it publishes, and has one accountable owner. Its `base_iri` is stable, under an authority its publisher controls, so that no two members' namespaces nest.

# A member that is a domain

Every domain bounds a workspace of its own, and a domain may not name itself or a domain above it. Confirming a `MemberDomain` attests that the domain belongs and who answers for it, not what its members say. A member that waits for a confirmation in that domain joins at the release that domain's own build took, as the lock in its `workspace-<tag>.zip` records. The `MemberDomain` names that workspace with its checksum, and without it the member is left out above.

The diamond rule: when two domains name the same bundle at the same release, the bundle joins once, and the lock records both domains. When they name different releases, the build stops until the two owners agree on one release and both pin it. The workspace index's "Named by" column says which domain named each bundle.

# What moves a member

The domain's librarian is a script, `knowledge-federate.py members`, which the sidecar's librarian workflow runs as `AGENT_CLI`. It picks each member's newest release that carries a bundle zip and verifies its checksum and attestation, or the new file a served member's site now serves. It writes the move for the pen with a question for the curator. The member then reads as edited since a person confirmed it, and the build keeps the confirmed release and lists the move under *Waiting for a person*.

A member whose file cannot be fetched at a release is held as the previous release's workspace holds it, under *Held at its last good state*, and left out when that workspace never held it. A release zip that serves other bytes stops the build, unless an earlier build fetched that very release.

`members --add <owner>/<repo>` drafts a new member, a `MemberDomain` when that release is a domain, and refuses a namespace that nests with a member's. `members --add <address>` drafts one from the `concepts.jsonld` a site serves. The build leaves a draft out until a person confirms it. A member leaves when the curator retires its concept, which stays for links and history with `status: deprecated` while the build and the members script pass over it. A member sent back stays at the release a person confirmed.

# Reading the workspace

The workspace is served under `/workspace/` of the host's site, its `index.md` first, and is attached to each release as `workspace-<tag>.zip`. The index lists the members, their versions, which domain named each and their health lines, and counts the links between members. `queries/labels.rq` computes every trust label with the bundle that asserted it, and `queries/moved.rq` lists the members that moved since the domain's last confirmation. `queries/unowned.rq` lists the targets the gate finds in no member's namespace, and `queries/links.rq` counts the links between members.

Each of three readers runs from the host's sidecar environment, with `--snapshot` naming an unpacked workspace, a `workspace-<tag>.zip` or the site that serves it:

- **An agent, over MCP.** `uv run --project .lokf .lokf/scripts/knowledge-federate.py mcp` is the `lokf-registry` Model Context Protocol (MCP) server that section 11.4 of the LOKF specification describes, with the tools `resolve_iri`, `neighbors`, `subgraph`, `federated_sparql` and `read_document`. Its instructions are the workspace index. It loads a member's graph when a walk first reaches it, and `--member <slug>` serves some bundles alone. Register it as any stdio server, with the host as the working directory.
- **A person, over SPARQL.** `knowledge-federate.py serve` opens the toolkit's SPARQL endpoint and graph page over the union of the graphs.
- **A team, from a container.** Load `graph.nq` once and serve it read-only with the Oxigraph server image:

```bash
podman run --rm -v "$PWD/snapshot:/snapshot:ro" -v oxigraph-data:/data ghcr.io/oxigraph/oxigraph:0.5.11 load --location /data --file /snapshot/graph.nq
podman run -d -p 7878:7878 -v oxigraph-data:/data:ro ghcr.io/oxigraph/oxigraph:0.5.11 serve-read-only --location /data --bind 0.0.0.0:7878 --union-default-graph
```

`docker` takes the same arguments, and the endpoint is then `http://localhost:7878/query`. `GRAPH ?g` names the asserting bundle, and `--union-default-graph` lets a query without it see every bundle. Nothing is hosted by default: hosting is the team's decision.
