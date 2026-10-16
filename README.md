<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".assets/knowledge-trust-ladder-logo-dark.svg">
  <img src=".assets/knowledge-trust-ladder-logo.svg" alt="" width="56" align="right" />
</picture>

# Knowledge Trust Ladder (ktl)

> "We lasso the world with networks of silver-coloured Italian hemp,\
> We bind down the world into some sort of order;\
> We balance the earth in a pair of scales of our own devising."\
> — Amy Lowell, *The Congressional Library* (1922)

Knowledge Trust Ladder keeps any repository's scattered knowledge as a **collection**: catalogued, authenticated and explained, with the trust in every claim left visible. Four Agent Skills build and keep it. Registrar automation checks every record and guards every confirmation, in CI on each pull request, as a museum's registrar keeps its collection's records. A toolkit underneath supplies schema and tooling. Two Obsidian plugins are optional, for a vault with no CI.

The complete documentation is at [w3id.org/ktl](https://w3id.org/ktl/). To install, see [the quick start](https://w3id.org/ktl/docs/install/#quick-start). Readers aged 13 to 18 can start with [a shorter version](https://w3id.org/ktl/simple/).

Knowledge Trust Ladder is an architecture inspired by the poem above, by [LOKF](https://lokf.nolan-nichols.com/specification/) (Linked Open Knowledge Format), the format its bundles are written in, and by [LinkML](https://linkml.io/linkml/), the schema language LOKF is written in. Each of the poem's three lines is one role's work, and [the architecture](https://w3id.org/ktl/docs/architecture/) says who plays each role and what checks their work.

> **Agents:** if `.lokf/knowledge/index.md` exists, read it first. `llms.txt` says how to weigh it.

## Exhibitions

Each site below shows a repository's collection, built by `ktl-website`:

- [Knowledge Trust Ladder](https://w3id.org/ktl/knowledge/): this repository's own bundle, the knowledge behind the skills.
- [Obsidian KTL Curator](https://noelmcloughlin.github.io/obsidian-ktl-curator/knowledge/): the Obsidian plugin that helps a person judge what a bundle claims.
- [Obsidian KTL Registrar](https://noelmcloughlin.github.io/obsidian-ktl-registrar/knowledge/): the Obsidian plugin that keeps a bundle well-formed as a person edits it.
- [KTL Federation](https://github.com/noelmcloughlin/ktl-federation): the top domain that federates the bundles above with ai-linkmo's and gist's into one workspace, as [the context layer page](docs/context-layer.md) designs it.
- [AI-LinkMO](https://noelmcloughlin.github.io/ai-linkmo/knowledge/): a reference implementation of operational AI governance over open AI-risk data.
