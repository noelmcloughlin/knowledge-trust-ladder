---
type: Playbook
id: https://knowledge-trust-ladder.example/knowledge/playbooks/website
title: Build, preview and edit the website
description: How the project website in `website/` is built with Astro Starlight from the README, `docs/`, the knowledge bundle and `CHANGELOG.md`, how to preview it locally with npm and uv, which file to edit for each kind of change, and how `website.yml` publishes it to GitHub Pages.
genre: how-to
resource: website/README.md
sources:
- resource: website/README.md
- resource: .github/workflows/website.yml
- resource: website/NOTICE
- resource: CHANGELOG.md
dependsOn:
- https://knowledge-trust-ladder.example/knowledge/references/lokf-toolkit
about:
- https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/glossary/trust-label
generated:
  by: process:ktl-librarian
  at: "2026-10-12T23:54:05Z"
status: draft
---

# Overview

The folder `website/` builds the project's site with Astro Starlight. `.github/workflows/website.yml` publishes the build of `main` to GitHub Pages at <https://noelmcloughlin.github.io/knowledge-trust-ladder/>. Every page comes from a file the repository already holds, so a change to the site is a change to that file. `CHANGELOG.md` records the site under the 0.38.1 release.

# What each page comes from

- `README.md` and `README.en-simple.md` become the home page and the page for readers aged 13 to 18.
- Each page under `docs/` becomes a page under `docs/`, placed in the sidebar by `website/site.config.mjs`.
- Each concept in `.lokf/knowledge/` becomes a page under `knowledge/`, with its trust label from `knowledge-report.sh`, its sources and its typed relations both ways.
- The four files `lokf export` writes are served under `knowledge/`, beside each concept's own Markdown file and its JSON-LD.
- `CHANGELOG.md` becomes a page per release under `changelog/`, which search leaves out. The commit that promotes a release's changelog skips CI, so that release's page appears with the next build, or when `website.yml` is run by hand.

# Preview it

Install Node.js 22.12 or later and uv. Then run these from `website/`:

```bash
npm ci
npm run dev        # http://localhost:4321/knowledge-trust-ladder/
npm run build      # dist/, then checks every link between its pages
```

Both commands run `npm run sync` first. The sync runs `lokf export` from the sidecar's own environment in `.lokf/` and writes the generated pages, and nothing it writes is committed. Run `astro` commands through `npm run`, or run `npm run sync` first.

`package.json` overrides the Astro that starlight-changelogs' loader helper asks for with the site's own. Without the override, npm installs Astro 5 beside it and the build fails.

# What to edit

- **A page's words:** edit the file the page comes from. A concept changes through the librarian and the curator, like any other change to the bundle.
- **A new page under `docs/`:** add it to `DOCS_GROUPS` in `site.config.mjs`. The sync stops with an error until every page has a place.
- **How a concept page looks:** edit `src/components/ConceptCard.astro` and `src/styles/catalogue.css`. The trust colours are in `src/styles/theme.css`, and `src/components/Neighbourhood.astro` draws the map in the right-hand column.
- **The health page:** edit `src/pages/health.astro` and its chart, `src/components/TrustChart.astro`. The words for the trust states are in `src/trust.ts`.
- **A page's link preview:** edit `src/pages/og/[...route].ts`, which draws the page's social card, and `src/routeData.ts`, which points the page at it.
- **How a link is rewritten:** edit `scripts/routes.mjs`, which the sync and the Markdown plugin both use.

# How it is published

`website.yml` runs on a push to `main` and on a pull request when either touches `website/`, `docs/`, `.assets/`, `.lokf/`, the two READMEs, `CHANGELOG.md`, `llms.txt` or the workflow itself. It can also be run by hand. A pull request gets the same build, link check included, and no deployment.

The workflow has two jobs, for least privilege. `build` installs the lokf toolkit the sidecar pins with `uv sync --locked`, and runs npm's and the toolkit's packages under a read-only token. `deploy` runs nothing but GitHub's own deploy-pages action, holds the Pages scopes, and runs for `main` only. A maintainer tells Pages once to take its site from Actions, under **Settings > Pages > Source**.

The graph explorer, `src/components/KnowledgeGraph.astro`, is adapted from the LOKF toolkit's own site under Apache-2.0, as `website/NOTICE` records.
