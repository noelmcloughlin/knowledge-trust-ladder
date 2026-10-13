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
  by: human:noelmcloughlin
  at: "2026-10-13T01:04:01Z"
verified:
- by: human:noelmcloughlin
  at: "2026-10-13T01:04:01Z"
stale_after: 2026-10-14
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

The graph explorer, `src/components/KnowledgeGraph.astro`, is adapted from the LOKF toolkit's own site under Apache-2.0, as `website/NOTICE` records. The two typefaces, Source Serif 4 and Atkinson Hyperlegible Next, are self-hosted under the SIL Open Font License.

## Open questions

- 2026-10-13, process:ktl-librarian: Since 2026-10-13 `website/README.md` says `docs/architecture.en-simple.md` becomes the page for readers aged 13 to 18, and that the home page's tagline is the first line of `docs/architecture.md` that is bold throughout; `.github/workflows/website.yml` no longer lists `README.en-simple.md`. This concept still names `README.en-simple.md`. `CHANGELOG.md` changed too, only in its unreleased notes, and still records the site under the 0.38.1 release.
- 2026-10-13, human:noelmcloughlin: website.yml: on main the workflow still matches this page, except that its paths name `README.md` only, not "the two READMEs". Once feat/ktl-website merges, `.github/workflows/website.yml` becomes a byte-identical copy of the ktl-website template `skills/ktl-website/templates/github/knowledge-website.yaml`. Its deploy job will then run only when the repository variable `KNOWLEDGE_WEBSITE_ENABLED` is `true`, and on the default branch rather than `main` by name. Its triggers will add `knowledge_bundle/**`, and its concurrency group becomes `knowledge-website-<ref>`. The file will later be renamed to the template's name, `.github/workflows/knowledge-website.yaml`. This page names `website.yml` in `sources` and three times in its text, and the sources entry fails the conventions check (rule 5) as soon as the file moves. So the rename has to land in the same pull request as this page's correction.
