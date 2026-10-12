# The Knowledge Trust Ladder website

This folder builds the site that `.github/workflows/website.yml` publishes to GitHub Pages at <https://noelmcloughlin.github.io/knowledge-trust-ladder/>. Every page comes from a file the repository already holds, so a change to the site is a change to that file:

- the README and `README.en-simple.md` become the home page and the page for readers aged 13 to 18;
- each page under `docs/` becomes a page under `docs/`, placed in the sidebar by `site.config.mjs`;
- each concept in `.lokf/knowledge/` becomes a page under `knowledge/`, with its trust label from `knowledge-report.sh`, its sources and its typed relations both ways;
- the four files `lokf export` writes are served under `knowledge/`, beside each concept's own Markdown file and its JSON-LD;
- `CHANGELOG.md` becomes a page per release under `changelog/`, which search leaves out. The commit that promotes a release's changelog skips CI, so its page appears with the next build, or when `website.yml` is run by hand.

## Preview it

You need Node.js 22.12 or later and [uv](https://docs.astral.sh/uv/).

```bash
cd website
npm ci
npm run dev        # http://localhost:4321/knowledge-trust-ladder/
npm run build      # dist/, then checks every link between its pages
```

Both commands run `npm run sync` first, which runs `lokf export` from the sidecar's own environment in `.lokf/` and writes the generated pages. Nothing it writes is committed. Run `astro` commands through `npm run`, or run `npm run sync` first.

`package.json` overrides the Astro that starlight-changelogs' loader helper asks for with the site's own. Without the override npm installs Astro 5 beside it, and the build fails.

## What to edit

- **A page's words:** the file it comes from: the README, a page under `docs/`, or a concept, through the librarian and the curator like any other change to the bundle.
- **A new page under `docs/`:** add it to `DOCS_GROUPS` in `site.config.mjs`. The sync stops with an error until every page has a place.
- **How a concept page looks:** `src/components/ConceptCard.astro` and `src/styles/catalogue.css`; the trust colours are in `src/styles/theme.css`, and the map in the right-hand column is `src/components/Neighbourhood.astro`.
- **The health page:** `src/pages/health.astro` and its chart, `src/components/TrustChart.astro`; the trust states' words are in `src/trust.ts`.
- **A page's link preview:** `src/pages/og/[...route].ts` draws its social card, and `src/routeData.ts` points the page at it.
- **How a link is rewritten:** `scripts/routes.mjs`, which the sync and the Markdown plugin both use.

The graph explorer is adapted from the LOKF toolkit's own site under Apache-2.0; see [NOTICE](NOTICE).

The two typefaces, Source Serif 4 for headings and Atkinson Hyperlegible Next for text, are self-hosted from Fontsource under the SIL Open Font License 1.1.
