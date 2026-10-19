# What a KTL context layer integrates with

> [!NOTE]
> This page is for anyone choosing the artifact repository, the store and the agent surface for the workspace that [A federation of bundles](federation.md) describes. Every product fact comes from the vendor's own documentation, read on 2026-10-12, and nothing here is an endorsement.

Below, *the toolkit* is `lokf` at 0.8.0, the floor the sidecar pins. A bundle leaves the toolkit in three forms:

- Markdown files;
- RDF, as Turtle, N-Triples, JSON-LD or TriG from `lokf convert`, and as the four files `lokf export` writes;
- tables, as CSV, Parquet or SQLite from `lokf tables`.

A domain's workspace adds `graph.nq`, one named graph per bundle, and a registry keyed by `base_iri`.

## Find your case

| Role in the workspace | What KTL does today | Where a product fits |
| --- | --- | --- |
| Artifact repository | The sidecar's release workflow attaches the bundle zip, its checksum and an attestation to a GitHub release | Any repository that stores a file and sends a webhook on arrival: a generic repository in JFrog Artifactory, Sonatype Nexus or GitLab, or an OCI registry through ORAS. JFrog documents Artifactory's webhook starting a GitHub Actions workflow through `workflow_dispatch` |
| Store | `knowledge-federate.py serve` answers SPARQL over the workspace, and `lokf serve` over one bundle, in an in-process Oxigraph store | A store that loads N-Quads and answers SPARQL 1.1 ([below](#rdf-stores-with-sparql)) |
| Agent surface | `knowledge-federate.py mcp` is the `lokf-registry` MCP server over the workspace, `lokf mcp` serves one bundle, and the **docent** runs in any agent that installs it | A store's own MCP server or natural-language layer ([below](#agent-facing-retrieval)) |
| Catalogue or semantic layer | `lokf tables` writes the concepts and their relations as tables | A catalogue that takes tables or YAML rather than RDF ([below](#catalogues-and-semantic-layers)) |
| Stable identifiers | `base_iri` in each bundle's `index.md` | w3id.org, a permanent redirection service, for a `base_iri` that outlives its host, and a static host such as GitHub Pages for the files `lokf export` writes |

## RDF stores with SPARQL

The workspace's graph is `graph.nq`, in N-Quads, and every SPARQL 1.1 store surveyed loads N-Quads with its named graphs: among them Oxigraph, the toolkit's own engine, Apache Jena Fuseki, GraphDB, Stardog, OpenLink Virtuoso and Amazon Neptune. What separates them is hosting, scale and price, which their own documentation covers. Managed SPARQL exists on AWS, through Amazon Neptune and marketplace offerings such as GraphDB's, and natively on neither Azure nor Google Cloud, whose graph services speak Gremlin or GQL. There, a store runs on a virtual machine or a marketplace image, or the bundle takes the tables route. Among the property-graph stores surveyed, only Neo4j's neosemantics imports N-Quads with their named graphs, and only on self-hosted Neo4j, not on Aura; the others take the tables.

## Catalogues and semantic layers

`lokf tables` projects a bundle to "one table per concept type (the nodes) plus a single `relations` table (the typed edges: `source`, `predicate`, `target`)", as CSV, Parquet or SQLite. For BigQuery or Athena it writes the Parquet to the location given and prints the external-table statements that register it. Every catalogue below that takes tables can read that output. The tables carry the structure and the frontmatter; the bound predicates, the meaning a graph carries, stay in the RDF.

| Product | What a bundle can feed it | What comes out |
| --- | --- | --- |
| data.world (ServiceNow), whose platform SPARQL "is also the query language upon which the data.world platform is based" | RDF upload takes Turtle, N-Triples and RDF/XML; TriG, N-Quads and JSON-LD are listed as not supported. Each dataset is a named graph | SPARQL, and a hosted MCP server |
| Microsoft Fabric IQ and Purview | the schema as "TTL, RDF/RDFS, or OWL", with the caveat that they "don't provide complete or lossless support for the full RDF or OWL specification"; Purview's Data Map speaks the Apache Atlas 2.2 APIs | Work IQ and Foundry IQ for Copilot; no SPARQL |
| Databricks Unity Catalog | `lokf tables` output as tables; metric views in SQL or YAML | Genie, and a `genie_one_mcp` server |
| Snowflake | tables, and YAML for semantic views | Cortex Agents, and a managed MCP server |
| dbt Semantic Layer | YAML metrics over tables | "AI tools like Claude and ChatGPT can connect to the Semantic Layer through the dbt MCP server" |
| Google Cloud Knowledge Catalog (formerly Dataplex Universal Catalog) | the OKF bundle itself: Google's announcement says Knowledge Catalog ingests OKF, and the OKF repository carries a connector that pushes one bundle per entry group | the catalogue's search and context APIs |
| TopQuadrant TQ Data Foundation, "Built entirely on open knowledge-graph standards" of RDF, OWL and SHACL | RDF, in principle; its import pages could not be read | SPARQL and MCP, per its documentation index |

The OKF repository's README names the places an OKF bundle can be consumed by reading the files: BigQuery, Dataplex, Vertex AI, Gemini, the Agent Development Kit, LangChain, Unity Catalog, Collibra, Obsidian, Notion and the static site generators.

## Agent-facing retrieval

A workspace's agent surface is the sidecar's `lokf-registry` MCP server, or a store's own. GraphDB and Stardog, among others, bring an MCP server and a natural-language layer of their own, while Amazon Neptune's MCP server speaks openCypher and Gremlin, not SPARQL. Microsoft 365 Copilot takes the **docent** as a skill ([m365.md](m365.md)). Graph-building retrieval frameworks, such as Microsoft GraphRAG and Amazon Bedrock Knowledge Bases GraphRAG, extract a graph of their own from text and consume no bundle's graph. They can still read the bundle's Markdown as documents, as OKF expects.

## Sources

- Oxigraph: <https://github.com/oxigraph/oxigraph>
- Apache Jena Fuseki: <https://jena.apache.org/documentation/fuseki2/>
- GraphDB: <https://graphdb.ontotext.com/documentation/11.5/talk-to-graph.html>, <https://graphdb.ontotext.com/documentation/11.5/loading-data.html>; AWS Marketplace: <https://aws.amazon.com/marketplace/pp/prodview-es5xupioynhd4>
- Stardog: <https://docs.stardog.com/operating-stardog/database-administration/adding-data>, <https://docs.stardog.com/voicebox/>
- OpenLink Virtuoso: <https://vos.openlinksw.com/owiki/wiki/VOS/VirtBulkRDFLoader>
- Amazon Neptune: <https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-sparql.html>, <https://docs.aws.amazon.com/neptune/latest/userguide/bulk-load-tutorial-format-rdf.html>; MCP server: <https://awslabs.github.io/mcp/servers/amazon-neptune-mcp-server>
- Azure Cosmos DB for Apache Gremlin: <https://learn.microsoft.com/en-us/azure/cosmos-db/gremlin/overview>; Graph in Microsoft Fabric: <https://learn.microsoft.com/en-us/fabric/graph/overview>; Spanner Graph: <https://docs.cloud.google.com/spanner/docs/graph/overview>
- Neo4j Aura: <https://neo4j.com/docs/aura/>; neosemantics: <https://neo4j.com/labs/neosemantics/4.3/import/>
- data.world: <https://docs.data.world/en/114339-rdf.html>, <https://docs.data.world/en/114345-named-graphs.html>, <https://docs.data.world/en/413220-data-world-mcp-server-for-ai-assistants.html>
- Microsoft Fabric IQ ontology: <https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-import-export>; Purview: <https://learn.microsoft.com/en-us/purview/data-gov-api-atlas-2-2>; Work IQ: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/add-work-iq>; Foundry IQ: <https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/what-is-foundry-iq>
- Databricks: <https://docs.databricks.com/aws/en/uc-semantics/metric-views>, <https://docs.databricks.com/aws/en/agents/mcp-tools/built-in-mcp-services>
- Snowflake: <https://docs.snowflake.com/en/user-guide/views-semantic/overview>, <https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp>
- dbt: <https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl>, <https://docs.getdbt.com/docs/dbt-ai/about-mcp>
- Google Cloud Knowledge Catalog: <https://docs.cloud.google.com/knowledge-catalog/docs/metadata-overview>; OKF and its connector: <https://github.com/GoogleCloudPlatform/open-knowledge-format>, <https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/connectors/gcp-knowledge-catalog.md>
- TopQuadrant: <https://www.topquadrant.com/tq-data-foundation>, <https://docs.topquadrant.com/latest/>
- Microsoft GraphRAG: <https://microsoft.github.io/graphrag/>; Amazon Bedrock Knowledge Bases GraphRAG: <https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-build-graphs.html>
- JFrog Artifactory: <https://docs.jfrog.com/artifactory/docs/repository-management-overview>, <https://docs.jfrog.com/integrations/docs/webhooks>, <https://docs.jfrog.com/integrations/docs/trigger-a-github-action-using-a-custom-webhook>
- Sonatype Nexus Repository: <https://help.sonatype.com/en/raw-repositories.html>, <https://help.sonatype.com/en/webhooks.html>
- GitLab generic package registry: <https://docs.gitlab.com/user/packages/generic_packages/>
- ORAS: <https://oras.land/docs/>
- w3id.org: <https://github.com/perma-id/w3id.org>
- The toolkit's tables and MCP pages: <https://lokf.nolan-nichols.com/toolkit/tables/>, <https://lokf.nolan-nichols.com/toolkit/mcp/>
