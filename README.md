<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".assets/knowledge-trust-ladder-logo-dark.svg">
  <img src=".assets/knowledge-trust-ladder-logo.svg" alt="" width="56" align="right" />
</picture>

# Knowledge Trust Ladder (KTL)

> "We lasso the world with networks of silver-coloured Italian hemp,\
> We bind down the world into some sort of order;\
> We balance the earth in a pair of scales of our own devising."\
> — Amy Lowell, *The Congressional Library* (1922)

Inspired by the poem, Knowledge Trust Ladder (KTL) keeps any repository's scattered knowledge as a **collection**: catalogued, authenticated and explained, with the trust in every claim left visible. An agent derives each claim, deterministic tools check it, and a named person vouches for it.

Documentation is at [w3id.org/ktl](https://w3id.org/ktl/). Readers aged 13 to 18 get [a shorter version](https://w3id.org/ktl/simple/).

## Get started

Install the skills:

```bash
gh skill install noelmcloughlin/knowledge-trust-ladder --all --scope user
```

Then open your agent in a repository and say, in turn:

1. "Add a LOKF knowledge bundle to this repository."
2. "Fill the knowledge bundle from this repository."
3. "What in the bundle needs my confirmation?"
4. Any question about the project.

[Your first bundle](https://w3id.org/ktl/docs/first-bundle/) walks through those steps. [The install page](https://w3id.org/ktl/docs/install/#quick-start) gives the other ways to install, and names the agents.

> **Only want to ask?** Install `ktl-docent` into any agent you use, by a route from [the install page](https://w3id.org/ktl/docs/install/), and ask it about this project. It answers from the bundle and says how far each answer has been checked.
>
> **Agents:** if `.lokf/knowledge/index.md` exists, read it first. `llms.txt` says how to weigh it.

## The cast

Five roles keep a bundle, named after the people who work in libraries and museums. Each of the poem's three lines is one role's work.

| Role | Played by | What it does | Runs |
| --- | --- | --- | --- |
| [**Sidecar**](https://w3id.org/ktl/docs/cast/sidecar/) | `ktl-sidecar` | *Lays the network.* Installs `.lokf/`, the folder that holds the bundle and its tools | once |
| [**Librarian**](https://w3id.org/ktl/docs/cast/librarian/) | `ktl-librarian` | *Binds it into order.* Derives each concept from a source it names. It catalogues and never vouches | often, including on a schedule |
| [**Registrar**](https://w3id.org/ktl/docs/cast/registrar/) | programs: the `lokf` toolkit, scripts and a gate in CI | Checks every record and guards every confirmation. It never judges truth | on every change |
| [**Curator**](https://w3id.org/ktl/docs/cast/curator/) | a named person, helped by `ktl-curator` | *Holds the scales.* Confirms, corrects, sends back or retires what the bundle claims | a little, regularly |
| [**Docent**](https://w3id.org/ktl/docs/cast/docent/) | `ktl-docent` | Answers from the bundle, and says how far each answer has been checked | whenever anyone asks |

Two optional skills work beside them. [`ktl-prose`](https://w3id.org/ktl/docs/cast/prose/) rewords what the librarian wrote, in plain English. [`ktl-website`](https://w3id.org/ktl/docs/cast/website/) publishes the bundle as a website. In Obsidian, two optional plugins do the registrar's work and the curator's in a vault with no CI.

[The architecture](https://w3id.org/ktl/docs/architecture/) says how the roles fit together and what checks their work.

## Exhibitions

### Knowledge Bundles

`ktl-website` built a site for each of these knowledge bundles:

- [KTL](https://w3id.org/ktl/knowledge/): this repository's own bundle, the knowledge behind the skills.
- [Obsidian KTL Curator](https://w3id.org/ktl/curator/knowledge/): the Obsidian plugin that helps a person judge what a bundle claims.
- [Obsidian KTL Registrar](https://w3id.org/ktl/registrar/knowledge/): the Obsidian plugin that keeps a bundle well-formed as a person edits it.
- [AI-LinkMO](https://noelmcloughlin.github.io/ai-linkmo/knowledge/): a reference implementation of operational AI governance over open AI-risk data.

### Federation of Bundles (Context Layer)

- [KTL Federation](https://w3id.org/ktl/federation/knowledge/): the domain that federates member bundles into one workspace, as [a context layer](docs/context-layer.md).
- todo
