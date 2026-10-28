---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/website
title: Build, preview and edit the website
description: How the project website in `website/` is built with Astro Starlight from the README, `docs/`, the knowledge bundle, `CHANGELOG.md` and, when shown, the LinkML schema's pages and data; how to preview it locally with npm and uv; which file to edit for each kind of change; and how `knowledge-website.yaml` publishes it to GitHub Pages, on a push, weekly or by hand.
genre: how-to
resource: website/README.md
sources:
  - resource: website/README.md
  - resource: .github/workflows/knowledge-website.yaml
  - resource: website/NOTICE
  - resource: CHANGELOG.md
dependsOn:
  - https://w3id.org/ktl/knowledge/references/lokf-toolkit
about:
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
relatedTo:
  - https://w3id.org/ktl/knowledge/glossary/trust-label
generated:
  by: process:ktl-librarian
  at: "2026-10-26T20:05:58Z"
verified:
  - by: human:noelmcloughlin
    at: "2026-10-13T01:04:01Z"
  - by: human:noelmcloughlin
    at: "2026-10-13T23:50:44Z"
  - by: process:ktl-librarian
    at: "2026-10-28T00:35:16Z"
stale_after: 2027-10-14
status: draft
---

# Overview

The folder `website/` builds the project's site with Astro Starlight. The Knowledge website workflow, `.github/workflows/knowledge-website.yaml`, publishes the default branch's build to GitHub Pages at <https://noelmcloughlin.github.io/knowledge-trust-ladder/>. Since 0.42.0 (`CHANGELOG.md`) the README and the architecture page link the site at its persistent address, <https://w3id.org/ktl/>, which redirects to the GitHub Pages site. Every page comes from a file the repository already holds, so a change to the site is a change to that file. `CHANGELOG.md` records the site under the 0.38.1 release. Since 0.53.0 (`CHANGELOG.md`) the site copies only files inside the repository, and passes raw HTML as GitHub renders a README. A link out of the repository and an SVG holding a script are left out, and other markup is shown as text.

# What each page comes from

- Each concept in `.lokf/knowledge/` becomes a page under `knowledge/`, with its trust label from `knowledge-report.sh`, its sources and its typed relations both ways.

- The four files `lokf export` writes are served under `knowledge/`, beside each concept's own Markdown file and its JSON-LD. The bundle log is served there too, as an Atom feed, `knowledge/log.xml`.

- The README becomes the home page, each page under `docs/` a page under `docs/`, and `CHANGELOG.md` a page per release under `changelog/`, which search leaves out. `site.config.mjs` says which of these the site shows and where each sits in the sidebar.

- The home page, each docs page and each extra page is served as Markdown too, at its path with `.md` added, with every link a full address.

- Each release page links the repository, the docs and the bundle at the release's tag, so a reader can see them as they stood. The commit that promotes a release's changelog skips CI, so its page appears with the next build: the workflow's weekly run at the latest, or a run by hand.

- The LinkML schema's pages, which `gen-doc` writes, become a page each under `schema/`, with their class diagrams drawn in the browser.

- SQLite databases, when `site.config.mjs` names their folder, are served under `browse/` with a page that opens each in Datasette Lite. Neither the data's folder nor the schema's is committed, so the sync runs the command that builds each when it is missing.

# Preview it

Install Node.js 22.12 or later and uv. Then run these from `website/`:

```bash
npm ci --ignore-scripts
npm run dev        # http://localhost:4321/knowledge-trust-ladder/
npm run build      # dist/, then checks every link between its pages
```

Both commands run `npm run sync` first. The sync runs `lokf export` from the sidecar's own environment in `.lokf/` and writes the generated pages, and nothing it writes is committed. Run `astro` commands through `npm run`, or run `npm run sync` first. `node scripts/config.mjs` prints what the sync will read.

`package.json` overrides the Astro that starlight-changelogs' loader helper asks for with the site's own. Without the override, npm installs Astro 5 beside it, and the build fails.

# What to edit

- **A page's words:** edit the file the page comes from: the README, a page under `docs/`, or a concept, through the librarian and the curator like any other change to the bundle. A schema page's words come from the schema, and the data page's from the databases' metadata.
- **The site's values and options:** edit `site.config.mjs`, which holds the addresses, the title, the logo, the home page's tagline and buttons, the docs groups and the extra pages. A comment above each option says what it takes.
- **Its look:** edit `src/styles/custom.css`, which is loaded last and is this repository's own. `theme.css` and `catalogue.css` are the house style, and the trust colours are in `theme.css`.
- **How a concept page looks:** edit `src/components/ConceptCard.astro` and `src/styles/catalogue.css`. The map in the right-hand column is `src/components/Neighbourhood.astro`.
- **The reading levels under a title:** edit `src/components/ReadingLevels.astro`, which shows on a page that has a retelling and on the retelling.
- **What a link to a concept shows on hover:** edit `src/components/ConceptPreviews.astro`, which reads `knowledge/previews.json`, written by the sync.
- **The health page:** edit `src/pages/health.astro` and its chart, `src/components/TrustChart.astro`. The words for the trust states are in `src/trust.ts`.
- **A page's link preview:** edit `src/pages/og/[...route].ts`, which draws the page's social card, and `src/routeData.ts`, which points the page at it.
- **How a link is rewritten:** edit `scripts/routes.mjs`, which the sync and the Markdown plugin both use.
- **How a diagram is drawn:** edit `src/components/Mermaid.astro`.

# How it is published

`knowledge-website.yaml` runs on a push and on a pull request that touch `website/`, `.lokf/`, `knowledge_bundle/`, `README.md`, `docs/`, `.assets/`, `CHANGELOG.md`, `llms.txt`, `.linkml/`, a justfile, a `pyproject.toml`, a `uv.lock` or the workflow itself. It also runs every Monday at 05:23 UTC, and it can be run by hand. A push builds on the default branch only. A pull request gets the same build, link check included, and no deployment.

The workflow has two jobs, for least privilege. `build` installs the lokf toolkit the sidecar pins with `uv sync --locked`, runs the `just` that `.lokf/uv.lock` pins where it pins one, with that command alone linked onto PATH (0.56.1), and runs npm's and the toolkit's packages, and the repository's own site code, under a read-only token. It installs the site's packages with `npm ci --ignore-scripts` and builds with Astro's telemetry off. `deploy` runs harden-runner and GitHub's own deploy-pages action and nothing else, and holds the Pages scopes. It runs for the default branch only, and the scheduled run deploys too, once the repository variable `KNOWLEDGE_WEBSITE_ENABLED` is `true`. Before setting the variable, a maintainer tells Pages once to take its site from Actions, under **Settings > Pages > Source**.

The graph explorer, `src/components/KnowledgeGraph.astro`, is adapted from the LOKF toolkit's own site under Apache-2.0, as `website/NOTICE` records. Since 0.54.0 its search and filters sit in a side panel beside a graph that keeps its full height in full screen, and each filter shows a count, with *All* and *None* on each group (`CHANGELOG.md`). The two typefaces, Source Serif 4 for headings and Atkinson Hyperlegible Next for text, are self-hosted from Fontsource under the SIL Open Font License 1.1.

Since 0.56.1 (`CHANGELOG.md`) a concept's card, its link preview and its social card give the genre beside the type, a genre that repeats the type is left off, and search gains a Genre filter. A type is worded as the bundle's prose spells it. A page the browser kept from before a deploy reloads once when the deploy removed its stylesheet, instead of showing unstyled for up to ten minutes.
