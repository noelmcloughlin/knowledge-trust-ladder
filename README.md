<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".assets/knowledge-trust-ladder-logo-dark.svg">
  <img src=".assets/knowledge-trust-ladder-logo.svg" alt="" width="56" align="right" />
</picture>

# Knowledge Trust Ladder (KTL)

[![PyPI](https://img.shields.io/pypi/v/ktl?label=PyPI)](https://pypi.org/project/ktl/)
[![Validate](https://github.com/noelmcloughlin/knowledge-trust-ladder/actions/workflows/validate.yml/badge.svg)](https://github.com/noelmcloughlin/knowledge-trust-ladder/actions/workflows/validate.yml)
[![Licence](https://img.shields.io/github/license/noelmcloughlin/knowledge-trust-ladder?label=licence)](LICENSE)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/noelmcloughlin/knowledge-trust-ladder/badge)](https://scorecard.dev/viewer/?uri=github.com/noelmcloughlin/knowledge-trust-ladder)
[![KTL scorecard](https://img.shields.io/endpoint?url=https://noelmcloughlin.github.io/knowledge-trust-ladder/badge.json)](https://w3id.org/ktl/health/)

> "We lasso the world with networks of silver-coloured Italian hemp,\
> We bind down the world into some sort of order;\
> We balance the earth in a pair of scales of our own devising."\
> — Amy Lowell, *The Congressional Library* (1922)

Inspired by the poem, the Knowledge Trust Ladder (KTL) keeps any repository's scattered knowledge as a portable **collection**: catalogued, authenticated and explained, with trust in every claim left visible. An agent derives each claim, deterministic tools check it, and a named person vouches for it.

Documentation is at [w3id.org/ktl](https://w3id.org/ktl/). Young readers get [a shorter version](https://w3id.org/ktl/simple/). Built on [lokf](https://w3id.org/lokf/).

## Get started

Install the skills:

```bash
gh skill install noelmcloughlin/knowledge-trust-ladder --all --scope user
```

Or install [`ktl`](https://pypi.org/project/ktl/) from PyPI via `uv/pipx`. Default is GitHub Copilot, unless `--agent` is passed:

```bash
uvx ktl skills install --scope user
```

Then open your agent in a repository and say, in turn:

1. "ktl-sidecar, Add a LOKF knowledge bundle to this repository."
2. "ktl-librarian, Fill the knowledge bundle from this repository."
3. "ktl-curator, What in the bundle needs my confirmation?"
4. "ktl-docent, I have questions about the project.

[Your first bundle](https://w3id.org/ktl/docs/first-bundle/) guides you. On GitHub, `uvx ktl gh plan` lists the settings your bundle's workflows need, and `uvx ktl gh apply` sets them. [The install page](https://w3id.org/ktl/docs/install/#quick-start) shows other ways to install, and names the agents.

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

The same ladder serves both ends of a range: [a school or a youth group](https://w3id.org/ktl/docs/young-readers/) that retells adult knowledge for younger readers, and [a regulated team](https://w3id.org/ktl/docs/three-lines/) that must show who vouched for each claim.

## Exhibitions

Knowledge bundles exist anywhere skills run:

- [KTL](https://w3id.org/ktl/knowledge/): this repository's own bundle, the knowledge behind the skills.
- [Obsidian KTL Curator](https://w3id.org/ktl/curator/knowledge/): the Obsidian plugin that helps a person judge what a bundle claims.
- [Obsidian KTL Registrar](https://w3id.org/ktl/registrar/knowledge/): the Obsidian plugin that keeps a bundle well-formed as a person edits it.
- [lmodel catalog](https://github.com/lmodel): has dozens of knowledge bundles.

### Federation of Bundles (Context Layer)

- [KTL federation](https://w3id.org/ktl/federation/knowledge/): the domain that federates member bundles into one workspace, as [a context layer](docs/context-layer.md).

## Feedback and contributing

Report a bug or ask for a change in [the issue tracker](https://github.com/noelmcloughlin/knowledge-trust-ladder/issues). [CONTRIBUTING.md](CONTRIBUTING.md) lists what a pull request needs, and [SECURITY.md](SECURITY.md) says how to report a vulnerability privately.
