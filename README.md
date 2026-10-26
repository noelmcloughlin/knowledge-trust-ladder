<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".assets/knowledge-trust-ladder-logo-dark.svg">
  <img src=".assets/knowledge-trust-ladder-logo.svg" alt="" width="56" align="right" />
</picture>

# Knowledge Trust Ladder (KTL)

> "We lasso the world with networks of silver-coloured Italian hemp,\
> We bind down the world into some sort of order;\
> We balance the earth in a pair of scales of our own devising."\
> — Amy Lowell, *The Congressional Library* (1922)

Knowledge Trust Ladder (KTL) keeps any repository's scattered knowledge as a **collection**: catalogued, authenticated and explained, with the trust in every claim left visible. Four Agent Skills build and keep it. Registrar automation checks every record and guards every confirmation, in CI on each pull request, as a museum's registrar keeps its collection's records. A toolkit underneath supplies schema and tooling. Two Obsidian plugins are optional, for a vault with no CI.

Documentation is at [w3id.org/ktl](https://w3id.org/ktl/). See the [the quick start](https://w3id.org/ktl/docs/install/#quick-start). Readers aged 13 to 18 get [a shorter version](https://w3id.org/ktl/simple/).

KTL architecture is inspired by the poem above, by [LOKF](https://lokf.nolan-nichols.com/specification/) (Linked Open Knowledge Format), its bundle format, and by [LinkML](https://linkml.io/linkml/). Each of the poem's three lines is one role's work, and [the architecture](https://w3id.org/ktl/docs/architecture/) says who plays each role and what checks their work.

> **Only want to ask?** Install `ktl-docent` into any agent you use, by a route from [the install page](https://w3id.org/ktl/docs/install/), and ask it about this project. It answers from the bundle and says how far each answer has been checked.
>
> **Agents:** if `.lokf/knowledge/index.md` exists, read it first. `llms.txt` says how to weigh it.

## Exhibitions

Knowledge Bundles, site built by `ktl-website`:

- [KTL](https://w3id.org/ktl/knowledge/): this repository's own bundle, the knowledge behind the skills.
- [Obsidian KTL Curator](https://w3id.org/ktl/curator/knowledge/): the Obsidian plugin that helps a person judge what a bundle claims.
- [Obsidian KTL Registrar](https://w3id.org/ktl/registrar/knowledge/): the Obsidian plugin that keeps a bundle well-formed as a person edits it.
- [KTL Federation](https://w3id.org/ktl/federation/knowledge/): the domain that federates member bundles into one workspace, as [a context layer](docs/context-layer.md).
- [AI-LinkMO](https://noelmcloughlin.github.io/ai-linkmo/knowledge/): a reference implementation of operational AI governance over open AI-risk data.
