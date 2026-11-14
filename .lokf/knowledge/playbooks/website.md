---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/website
title: Build, preview and edit the website
description: How the project website in `website/` is built with Hugo from the README, `docs/`, retellings, the knowledge bundle, `CHANGELOG.md`, the figures and, when the repository has one, a LinkML schema, each found with no setting; how to preview it locally with uv and `scripts/build.sh`; which file to edit for each kind of change; how raw HTML is cleaned; and how `knowledge-website.yaml` publishes it to GitHub Pages, on a push, weekly or by hand.
genre: how-to
resource: website/README.md
sources:
  - resource: website/README.md
  - resource: website
  - resource: .github/workflows/knowledge-website.yaml
  - resource: CHANGELOG.md
dependsOn:
  - https://w3id.org/ktl/knowledge/references/lokf-toolkit
about:
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
relatedTo:
  - https://w3id.org/ktl/knowledge/glossary/trust-label
generated:
  by: process:ktl-librarian
  at: "2026-11-14T10:17:06Z"
verified:
  - by: human:noelmcloughlin
    at: "2026-10-13T01:04:01Z"
  - by: human:noelmcloughlin
    at: "2026-10-13T23:50:44Z"
  - by: process:ktl-librarian
    at: "2026-11-13T14:41:35Z"
stale_after: 2027-10-14
status: draft
---

# Overview

The folder `website/` builds the project's site with Hugo. The Knowledge website workflow, `.github/workflows/knowledge-website.yaml`, publishes the default branch's build to GitHub Pages at <https://noelmcloughlin.github.io/knowledge-trust-ladder/>. The README and the architecture page link the site at its persistent address, <https://w3id.org/ktl/>, which redirects to the GitHub Pages site. Every page comes from a file the repository already holds, so a change to the site is a change to that file.

# What each page comes from

No setting names any of these. The build looks for each and shows what it finds:

- Each concept in `.lokf/knowledge/` becomes a page under `knowledge/`, with its trust label from `knowledge-report.sh`, its sources and its relations both ways. The bundle also gives the health page, the graph, the four files `lokf export` writes, each concept's Markdown and JSON-LD, and the bundle log as an Atom feed, `knowledge/log.xml`.
- The README becomes the home page, and its Markdown is served at `index.md`. With no README, the home page opens with the bundle's own introduction.
- Each page under `docs/` becomes a page under `docs/`, and its Markdown is served at `docs/<name>.md`, with every address made full.
- `docs/<page>.<language>-simple.md` is a retelling of `docs/<page>.md`. Both pages offer each other above their titles, and the retelling has no line in the navigation. A concept tagged `audience-13-18` retells the one concept it is `derivedFrom` in the same way.
- `docs/architecture.md` lights the home page's Architecture button.
- `CHANGELOG.md` becomes a page per release under `changelog/`, which search leaves out.
- `.assets/` gives the figures, under `assets/`.
- `.lokf/ingest.lock.yaml` says where each source the ingest mirrored came from, on its concept's card.
- A LinkML schema at `src/<name>/schema/<name>.yaml`, or the same under `.linkml/`, gives the Schema part: a page per class, slot, enumeration and type, written by LinkML's `gen-doc`, each also at `elements/<Name>/`, where a schema's w3id rules point. The home page then leads with the schema.
- `.github/workflows/knowledge-federation.yaml` adds, on the graph page, the workspace a domain host's federation serves.

One part is set, never found: the data. `browse` in `site.toml` names a folder of SQLite databases, which the site serves under `browse/` with a page that opens each in Datasette Lite.

The home page has the same five buttons on every site: the schema, the bundle, the architecture page, the glossary and the quick start. One whose page is not there is greyed. The glossary is the bundle's `glossary` group or `docs/glossary.md`. The quick start is a docs page named `quick-start`, `quickstart` or `getting-started`, or the first heading of one of those names.

A release page links the repository, the docs and the bundle at the release's tag. The commit that promotes a release's changelog skips CI, so its page appears with the next build: the workflow's weekly run at the latest, or a run by hand.

# Preview it

Install bash, git and uv, then run these from `website/`:

```bash
scripts/build.sh          # dist/, with the search index, then checks every link between its pages
scripts/build.sh serve    # http://localhost:1313/knowledge-trust-ladder/, rebuilt as you edit
scripts/build.sh preview  # the site as it will be published, at http://localhost:1313/
```

`PORT=1400 scripts/build.sh serve` uses another port.

Hugo and Pagefind come from PyPI, at the versions `pyproject.toml` names and the hashes `uv.lock` holds. The PyPI package `hugo` is a rebuild of Hugo by another maintainer, hugo-python-distributions. The first build fetches Cytoscape and Mermaid, once, and checks each against the hash in `hugo.toml`. Where PyPI or the CDN is blocked, point uv at a mirror, and give `params.vendor.cytoscape.url` and `params.vendor.mermaid.url` a mirror's address in `site.toml`.

`serve` shows raw HTML as written and leaves the security policy off, since Hugo's reload script would break it. Its search index is the one built when it started.

# What to edit

- **A page's words:** edit the file it comes from: the README, a page under `docs/`, the schema, or a concept, through the librarian and the curator like any other change to the bundle.
- **The site's own values:** edit `site.toml`: its address, title and description, the repository, and optionally a logo, the docs pages' groups, more docs folders to leave out, old addresses to redirect, and the data to publish. A comment above each says what it takes.
- **Its look:** edit `assets/css/custom.css`, which is loaded last and is this repository's own. The colours and the trust tones are custom properties at the top of `assets/css/site.css`.

Those two files and the folder's `README.md` are the repository's own. Every other file in `website/` is a copy of the ktl-website skill's template, and the skill's repair replaces it, so change one of those in the skill's templates.

# Security

`scripts/clean-html.py` cleans raw HTML in the repository's Markdown after the build, to the tags GitHub allows in a README. Any other markup, such as a `<meta>` refresh or a `<style>`, is shown as text, and an event handler, a style or a `javascript:` address is dropped. A Content-Security-Policy in every page stays as a second guard: a script loads only from the site's own `js/` and `pagefind/` folders, where no repository file is served. `scripts/prepare.sh` stops the build on an SVG that holds a script. No HTML or XML document is served, and neither is a file or folder whose name starts with a dot. Raw HTML that GitHub allows can still mislead, such as a link whose words name another address, so review still matters.

The two typefaces, Source Serif 4 for headings and Atkinson Hyperlegible Next for text, are served from the site under the SIL Open Font License 1.1, whose text is beside them in `static/fonts/`.

# How it is published

`knowledge-website.yaml` runs on a push and on a pull request that touch `website/`, `ktl-website/`, `.lokf/`, `knowledge_bundle/`, `README.md`, `docs/`, `.assets/`, `CHANGELOG.md`, `.linkml/`, a schema under `src/*/schema/`, the workflow itself or `knowledge-federation.yaml`. It also runs every Monday at 05:23 UTC, and it can be run by hand. A push builds on the default branch only. A pull request gets the same build, link check included, and no deployment.

The workflow has two jobs, for least privilege. `build` checks out the whole history, since the health page's "a source moved" lines come from git. It finds the site's folder, installs `just` when the data is built with it, runs `scripts/build.sh` under a read-only token, and uploads the folder's `dist`. `deploy` runs harden-runner and GitHub's own deploy-pages action, holds the Pages scopes, and warns when a private repository's site is public. It runs for the default branch only, and the scheduled run deploys too, once the repository variable `KNOWLEDGE_WEBSITE_ENABLED` is `true`. Before setting the variable, a maintainer tells Pages once to take its site from Actions, under **Settings > Pages > Source**.
