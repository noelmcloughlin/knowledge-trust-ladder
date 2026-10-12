# What a KTL context layer integrates with

> [!NOTE]
> For anyone choosing the artifact repository, the store and the agent surface for the workspace that [The KTL context layer](context-layer.md) describes. Every product fact below comes from that vendor's own documentation, read on 2026-10-12, and a product is listed only where its own page states the capability. Nothing here is an endorsement, and the pages that could not be read are named at the end.

Below, *the toolkit* is `lokf` at 0.8.0, the floor the sidecar pins. A bundle leaves the toolkit in three forms:

- Markdown files;
- RDF, as Turtle, N-Triples, JSON-LD or TriG from `lokf convert`, and as the four files `lokf export` writes;
- tables, as CSV, Parquet or SQLite from `lokf tables`.

The workspace adds one named graph per bundle and a registry keyed by `base_iri`.

## Find your case

| Role in the workspace | What the toolkit does today | Where a product fits |
| --- | --- | --- |
| Artifact repository | The sidecar's release workflow attaches the bundle zip, its checksum and an attestation to a GitHub release | Any repository that stores a file and sends a webhook on arrival |
| Store | `lokf serve` and `lokf query` run SPARQL over one bundle in an in-process Oxigraph store | A store that loads N-Quads or TriG and answers SPARQL 1.1 |
| Agent surface | `lokf mcp` exposes seven tools over one bundle; the **docent** runs in any agent that installs it | A store's own Model Context Protocol (MCP) server or natural-language layer |
| Catalog or semantic layer | `lokf tables` writes one table per concept type and a relations table, with BigQuery or Athena definitions | A catalog that takes tables or YAML and not RDF |
| Stable identifiers | `base_iri` in each bundle's `index.md` | A persistent-identifier service, and a static host for exported files |

## Artifact repositories

| Product | What it takes | How it notifies |
| --- | --- | --- |
| GitHub Releases | "Each file included in a release must be under 2 GiB", and "Up to 1000 release assets may be associated with a single release." The template workflow uploads the zip and its `.sha256` here and records an attestation that `gh attestation verify` checks | The `release` event. GitHub Packages has no generic format, so a zip reaches `ghcr.io` only as an Open Container Initiative (OCI) artifact |
| JFrog Artifactory | "You can define a repository as Generic, where you can upload packages of any type." | A webhook on the `deployed` artifact event, filtered by repository and path; JFrog's own example starts a GitHub Actions workflow through `workflow_dispatch` |
| Sonatype Nexus Repository | The raw format: "A simple `HTTP PUT` can upload files." | Webhooks "defined as an HTTP callback", signed with "a sha1 hash of the JSON body using a shared secret key" |
| GitLab generic package registry | "Use the generic packages repository to publish and manage generic files"; one `PUT` per file, up to 5 GB on object storage | Project webhooks and pipelines |
| Cloudsmith raw | "Any file, any extension, suitable for datasets, images or whatever you want to throw at it"; not on the Core plan | Webhooks such as `package.synced`, with a hash-based message authentication code (HMAC) in `X-Cloudsmith-Signature` |
| An OCI registry with ORAS | "the ORAS project provides a way to push and pull OCI Artifacts to and from OCI Registries"; the compatibility list names GitHub's, Amazon's, Azure's and Google's registries, Artifactory and Harbor | The registry's own events; cosign signs the blob keyless through OpenID Connect, or `actions/attest` records provenance |

Two services sit beside the repository. w3id.org is "a secure, permanent URL redirection service run by the W3C Permanent Identifier Community Group", registered by pull request, and gives a bundle a `base_iri` that outlives its host. GitHub Pages is "a static site hosting service" with sites "no larger than 1 GB" and "a soft bandwidth limit of 100 GB per month". That is enough to serve `lokf export`'s files as the LOKF specification's producer contract asks.

## RDF stores with SPARQL

Each store below answers SPARQL 1.1. The second column says whether its own documentation lists TriG or N-Quads as a load format, which keeps one named graph per bundle through the load.

| Store | Hosting | TriG or N-Quads | How a graph gets in | Agent features |
| --- | --- | --- | --- | --- |
| Oxigraph | self-hosted or embedded; the toolkit's own engine | both; the server implements "the SPARQL 1.1 Protocol and the SPARQL 1.1 Graph Store Protocol" | `oxigraph load --file x.nq`, a `POST` to `/store`, SPARQL Update | none |
| Apache Jena Fuseki | self-hosted | both | the Graph Store protocol, SPARQL Update, `tdb2.tdbloader --graph` | none |
| GraphDB (Graphwise) | self-hosted; AWS and Azure images; an AWS Marketplace managed evaluation "limited to a 6-month term" | "Support for all RDF serialization formats"; import into a context | Workbench, server files, the SPARQL endpoint, ImportRDF preload | Talk to Your Graph, "a chatbot that lets you converse with your data", and an MCP gateway with `sparql_query` |
| Stardog | self-managed, or Stardog Cloud, "a fully-managed Stardog platform on AWS" | both | `stardog data add --named-graph`, the Graph Store protocol, SPARQL `LOAD` from S3 | Voicebox "translates natural language queries into SPARQL queries", with an MCP server |
| OpenLink Virtuoso | self-hosted; AWS and Azure images | both; "the graph name specified in such dataset files in quad format will always be used" | the bulk loader, SPARQL Update, the Graph Store protocol | OPAL, with "AI Agent Deployment with Skills from Stored Procedures, OpenAPI, MCP Servers" |
| QLever | self-hosted | N-Quads only | an index built from N-Triples, Turtle or N-Quads, then SPARQL Update | none |
| Eclipse RDF4J | self-hosted | both | the Workbench, a REST API, SPARQL Update | none |
| AllegroGraph (Franz) | on-premises, or AllegroGraph Cloud | both | `agload`, data import | "integration with Large Language Models", natural language to SPARQL |
| MarkLogic 12 (Progress) | self-hosted | both: "A document with a file extension of `.nq` or `.trig` is identified as quad data" | `/v1/graphs`, "an implementation of the W3C Graph Store HTTP Protocol", and the content pump | none stated |
| Amazon Neptune | managed, AWS only | N-Quads only; "Amazon Neptune associates every triple with a named graph" | the bulk loader from S3, with `namedGraphUri` for triple files; SPARQL Update | Bedrock GraphRAG below; its MCP server speaks openCypher and Gremlin, not SPARQL |

Azure and Google Cloud offer no SPARQL service. Cosmos DB for Apache Gremlin is "a fully managed graph database service" for "the Gremlin query language". Graph in Microsoft Fabric "Supports the international standard for the graph query language GQL (ISO/IEC 39075)". "Spanner Graph supports an ISO Graph Query Language (GQL)-compatible graph query interface". A workspace on either cloud runs one of the stores above on a virtual machine or a marketplace image, or takes the tables route below.

## Property-graph stores and the RDF bridge

- **Neo4j.** AuraDB is "a fully automated graph platform offered as a cloud service" on AWS, Azure and Google Cloud, and speaks Cypher. RDF enters through neosemantics (n10s), which imports "Turtle, N-Triples, JSON-LD, RDF/XML, TriG and N-Quads", but "neosemantics is only available for Neo4j self-hosted (CE and EE) and is not available in Aura". Neo4j's official MCP server runs Cypher.
- **Amazon Neptune Analytics.** A "memory-optimized graph database engine for analytics" that speaks openCypher and loads N-Triples, CSV and Parquet from S3. Graph names do not survive the load.
- **Memgraph.** Memgraph Cloud runs on AWS. The migration page lists Parquet, CSV, JSON, Cypher, streams and other databases, and no RDF. It has an MCP server.
- **TigerGraph.** GSQL, with "the majority of openCypher features"; Savanna is the managed service. No RDF import is documented.
- **FalkorDB.** "a high-performance graph database built as a Redis module", with openCypher, CSV bulk insert and an MCP server. No RDF import is documented.
- **Kuzu.** Its repository was archived on 10 October 2025.

So the bridge is narrow. n10s on self-hosted Neo4j keeps named graphs, Neptune Analytics keeps triples without their graph names, and the rest take tables.

## Catalogs and semantic layers

| Product | What it says of itself | What a bundle can feed it | What comes out |
| --- | --- | --- | --- |
| data.world (ServiceNow) | SPARQL "is also the query language upon which the data.world platform is based" | RDF upload takes Turtle, N-Triples and RDF/XML; TriG, N-Quads and JSON-LD are listed as not supported. Each dataset is a named graph | SPARQL, and a hosted MCP server |
| Microsoft Fabric IQ and Purview | an ontology (preview) that can "import them from open standards like RDF or OWL" | the schema as "TTL, RDF/RDFS, or OWL", with the caveat that they "don't provide complete or lossless support for the full RDF or OWL specification"; Purview's Data Map speaks the Apache Atlas 2.2 APIs | Work IQ and Foundry IQ for Copilot; no SPARQL |
| Atlan | "The Context Layer for AI" | metadata through its connectors; no RDF path on the pages read | a hosted MCP server |
| Databricks Unity Catalog | "Metric views are the core implementation of Unity Catalog semantics" | `lokf tables` output as tables; metric views in SQL or YAML | Genie, and a `genie_one_mcp` server |
| Snowflake | semantic views, "a schema-level object" | tables, and YAML | Cortex Agents, and a managed MCP server |
| dbt Semantic Layer | "powered by MetricFlow" | YAML metrics over tables | "AI tools like Claude and ChatGPT can connect to the Semantic Layer through the dbt MCP server" |
| Palantir Foundry Ontology | "an operational layer for the organization" over datasets | tables; no RDF named | the ontology's own interfaces |
| Google Cloud Knowledge Catalog (formerly Dataplex Universal Catalog) | "Retrieve LLM-ready metadata and Active Context to ground generative AI agents" | the OKF bundle itself: Google's announcement says Knowledge Catalog ingests OKF, and the OKF repository carries a connector that pushes one bundle per entry group | the catalog's search and context APIs |
| TopQuadrant TQ Data Foundation | "Built entirely on open knowledge-graph standards" of RDF, OWL and SHACL, serving context "through MCP, a Python SDK and REST" | RDF, in principle; the import pages could not be read | SPARQL and MCP, per its documentation index |
| PoolParty (Semantic Web Company, Graphwise) | a thesaurus manager with "an internal SPARQL endpoint" per project | SKOS for a glossary; it exports TriG and N-Quads | SPARQL |

The OKF repository's own README names the places an OKF bundle can be consumed, by reading the files: BigQuery, Dataplex, Vertex AI, Gemini, the Agent Development Kit, LangChain, Unity Catalog, Collibra, Obsidian, Notion and the static site generators.

## Agent-facing retrieval

The Model Context Protocol (MCP) is "an open protocol that enables seamless integration between LLM applications and external data sources and tools". Its current version is 2026-07-28. The toolkit's `lokf mcp` serves one bundle today, and the stores above bring servers of their own. Microsoft 365 Copilot takes the **docent** as a skill ([m365.md](m365.md)). The retrieval frameworks that build graphs do the following:

- **Amazon Bedrock Knowledge Bases GraphRAG**: "a fully managed GraphRAG feature with Amazon Neptune" that builds its own graph in Neptune Analytics from documents in S3; "Configuration options to customize the graph build are not supported."
- **Azure AI Search agentic retrieval**: "a multi-query pipeline designed for complex questions" over indexed knowledge sources, reached through a retrieve action or an MCP endpoint; no graph.
- **Vertex AI RAG Engine**: retrieval over files and drives through a vector store; no graph.
- **Microsoft GraphRAG**: "a structured, hierarchical approach to Retrieval Augmented Generation" that extracts entities, relationships and communities from text; bring-your-own-graph takes Parquet.
- **LightRAG**: "a lightweight knowledge-graph RAG framework" that extracts its own graph into NetworkX, Neo4j, Memgraph, PostgreSQL or MongoDB.
- **Cognee**: builds its own memory graph, and "An ontology is an optional RDF/OWL file you can provide to Cognee", parsed with RDFLib to validate the nodes it extracts. It is the one framework surveyed that reads an RDF file.
- **Graphiti (Zep)**: "Build Real-Time Knowledge Graphs for AI Agents" over Neo4j, FalkorDB or Neptune, with an MCP server.

None of them consumes a bundle's graph as its graph. Each builds its own from text. The workspace's agent surface is therefore the store's: SPARQL behind an MCP server, with the index served first. The frameworks can still read the bundle's Markdown as documents, which is how OKF expects a bundle to be consumed.

## The tables route

`lokf tables` projects a bundle to "one table per concept type (the nodes) plus a single `relations` table (the typed edges: `source`, `predicate`, `target`)", as CSV, Parquet or SQLite. For BigQuery or Athena it writes the Parquet to the location given and prints the external-table statements that register it. Every catalog above that takes tables and not RDF can read that output. The tables carry the structure and the frontmatter. The bound predicates, the meaning a graph carries, stay in the RDF.

## What fits a Markdown-plus-RDF bundle

- Stores whose documentation lists TriG or N-Quads keep one named graph per bundle through the load: Oxigraph, Jena, GraphDB, Stardog, Virtuoso, RDF4J, AllegroGraph and MarkLogic. QLever and Neptune take N-Quads and not TriG.
- Managed SPARQL exists on AWS, through Neptune, Stardog Cloud, GraphDB's marketplace offerings and AllegroGraph Cloud, and natively on neither Azure nor Google Cloud.
- Among catalogs, only data.world is SPARQL-native, and it takes Turtle per dataset rather than TriG.
- The property-graph bridge is n10s on self-hosted Neo4j, and nothing on Aura.
- Fabric IQ takes the schema, with loss; the lakehouse catalogs take the tables; Knowledge Catalog takes the OKF bundle itself.
- No retrieval framework surveyed consumes RDF as its graph. The RDF-native agent surfaces are the stores' MCP servers and the toolkit's own.
- Every artifact repository surveyed stores a zip and its checksum. Artifactory, Nexus and Cloudsmith send a filtered or signed webhook on arrival, and an OCI registry adds a signature through ORAS and cosign.
- w3id.org gives a bundle a `base_iri` that outlives its host, and GitHub Pages serves `lokf export`'s files within its limits.

## Pages that could not be read

TopQuadrant's documentation sub-pages, PoolParty's import API page, Kuzu's documentation hosts, TigerGraph CoPilot and data.world's AI Context Engine page all failed to load on 2026-10-12. The rows above say what the readable pages state and no more.

## Sources

- Oxigraph: <https://github.com/oxigraph/oxigraph>
- Apache Jena Fuseki: <https://jena.apache.org/documentation/fuseki2/>; TDB2 commands: <https://jena.apache.org/documentation/tdb2/tdb2_cmds.html>
- GraphDB: <https://graphdb.ontotext.com/documentation/11.5/talk-to-graph.html>, <https://graphdb.ontotext.com/documentation/11.5/loading-data.html>; AWS Marketplace: <https://aws.amazon.com/marketplace/pp/prodview-es5xupioynhd4>
- Stardog: <https://docs.stardog.com/operating-stardog/database-administration/adding-data>, <https://docs.stardog.com/voicebox/>
- OpenLink Virtuoso: <https://vos.openlinksw.com/owiki/wiki/VOS/VirtBulkRDFLoader>
- QLever: <https://github.com/ad-freiburg/qlever>
- Eclipse RDF4J: <https://rdf4j.org/about/>
- AllegroGraph: <https://franz.com/agraph/support/documentation/agraph-introduction.html>, <https://franz.com/agraph/support/documentation/llm.html>
- MarkLogic: <https://docs.progress.com/bundle/marklogic-server-develop-with-semantic-graphs-12/page/topics/intro.html>
- Amazon Neptune: <https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-sparql.html>, <https://docs.aws.amazon.com/neptune/latest/userguide/bulk-load-tutorial-format-rdf.html>; Neptune Analytics: <https://docs.aws.amazon.com/neptune-analytics/latest/userguide/neptune-analytics-features.html>; MCP server: <https://awslabs.github.io/mcp/servers/amazon-neptune-mcp-server>
- Azure Cosmos DB for Apache Gremlin: <https://learn.microsoft.com/en-us/azure/cosmos-db/gremlin/overview>; Graph in Microsoft Fabric: <https://learn.microsoft.com/en-us/fabric/graph/overview>
- Spanner Graph: <https://docs.cloud.google.com/spanner/docs/graph/overview>
- Neo4j Aura: <https://neo4j.com/docs/aura/>; neosemantics: <https://neo4j.com/labs/neosemantics/4.3/import/>; MCP server: <https://github.com/neo4j/mcp>
- Memgraph: <https://memgraph.com/docs/data-migration>, <https://memgraph.com/docs/ai-ecosystem/mcp>
- TigerGraph: <https://www.tigergraph.com/docs/gsql-ref/4.3/opencypher-in-gsql/>, <https://www.tigergraph.com/docs/savanna/main/overview/>
- FalkorDB: <https://docs.falkordb.com/>, <https://github.com/FalkorDB/FalkorDB-MCPServer>
- Kuzu: <https://github.com/kuzudb/kuzu>
- data.world: <https://docs.data.world/en/114339-rdf.html>, <https://docs.data.world/en/114345-named-graphs.html>, <https://docs.data.world/en/413220-data-world-mcp-server-for-ai-assistants.html>
- Microsoft Fabric IQ ontology: <https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-import-export>; Purview: <https://learn.microsoft.com/en-us/purview/data-gov-api-atlas-2-2>; Work IQ: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/add-work-iq>; Foundry IQ: <https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/what-is-foundry-iq>
- Atlan: <https://docs.atlan.com/>
- Databricks: <https://docs.databricks.com/aws/en/uc-semantics/metric-views>, <https://docs.databricks.com/aws/en/agents/mcp-tools/built-in-mcp-services>
- Snowflake: <https://docs.snowflake.com/en/user-guide/views-semantic/overview>, <https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp>
- dbt: <https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl>, <https://docs.getdbt.com/docs/dbt-ai/about-mcp>
- Palantir Foundry Ontology: <https://www.palantir.com/docs/foundry/ontology/overview>
- Google Cloud Knowledge Catalog: <https://docs.cloud.google.com/knowledge-catalog/docs/metadata-overview>; OKF and its connector: <https://github.com/GoogleCloudPlatform/open-knowledge-format>, <https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/connectors/gcp-knowledge-catalog.md>
- TopQuadrant: <https://www.topquadrant.com/tq-data-foundation>, <https://docs.topquadrant.com/latest/>
- PoolParty and Graphwise: <https://help.poolparty.biz/>, <https://graphwise.ai/about-us/>
- Model Context Protocol: <https://modelcontextprotocol.io/specification/latest>
- Amazon Bedrock Knowledge Bases GraphRAG: <https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-build-graphs.html>
- Azure AI Search agentic retrieval: <https://learn.microsoft.com/en-us/azure/search/agentic-retrieval-overview>
- Vertex AI RAG Engine: <https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/rag-engine/rag-overview>
- Microsoft GraphRAG: <https://microsoft.github.io/graphrag/>, <https://microsoft.github.io/graphrag/index/byog/>
- LightRAG: <https://github.com/HKUDS/LightRAG>
- Cognee: <https://docs.cognee.ai/core-concepts/further-concepts/ontologies>
- Graphiti: <https://github.com/getzep/graphiti>
- JFrog Artifactory: <https://docs.jfrog.com/artifactory/docs/repository-management-overview>, <https://docs.jfrog.com/integrations/docs/webhooks>, <https://docs.jfrog.com/integrations/docs/trigger-a-github-action-using-a-custom-webhook>
- Sonatype Nexus Repository: <https://help.sonatype.com/en/raw-repositories.html>, <https://help.sonatype.com/en/webhooks.html>
- GitHub Releases, Packages and attestations: <https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases>, <https://docs.github.com/en/packages/learn-github-packages/introduction-to-github-packages>, <https://docs.github.com/en/actions/concepts/security/artifact-attestations>
- GitLab generic package registry: <https://docs.gitlab.com/user/packages/generic_packages/>
- Cloudsmith: <https://docs.cloudsmith.com/formats/raw-repository>, <https://docs.cloudsmith.com/developer-tools/webhooks>
- ORAS and cosign: <https://oras.land/docs/>, <https://oras.land/docs/compatible_oci_registries>, <https://docs.sigstore.dev/cosign/signing/signing_with_blobs/>
- w3id.org: <https://github.com/perma-id/w3id.org>
- GitHub Pages: <https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages>, <https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits>
- The toolkit's tables and MCP pages: <https://lokf.nolan-nichols.com/toolkit/tables/>, <https://lokf.nolan-nichols.com/toolkit/mcp/>
