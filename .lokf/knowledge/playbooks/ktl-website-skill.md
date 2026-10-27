---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/ktl-website-skill
title: ktl-website skill
description: Procedure that installs an Astro Starlight website for the knowledge bundle in `website/` from bundled templates, with a page per concept and its trust label, a health page and the knowledge graph, and a workflow that publishes it to GitHub Pages once `KNOWLEDGE_WEBSITE_ENABLED` is set; or repairs and updates a site it installed, and hands the maintainer the steps that retire an mkdocs site it replaces.
genre: how-to
resource: skills/ktl-website/SKILL.md
sources:
  - resource: skills/ktl-website/SKILL.md
  - resource: skills/ktl-website/references/customising.md
  - resource: skills/ktl-website/references/deploy.md
  - resource: skills/ktl-website/references/inputs.md
  - resource: skills/ktl-website/references/prerequisites.md
  - resource: skills/ktl-website/templates/github/knowledge-website.yaml
  - resource: scripts/validate-repository.sh
  - resource: .github/workflows/validate.yml
  - resource: docs/architecture.md
  - resource: CHANGELOG.md
  - resource: skills/ktl-website/scripts/website-preflight.sh
  - resource: skills/ktl-website/templates/website/site.config.mjs
dependsOn:
  - https://w3id.org/ktl/knowledge/playbooks/ktl-sidecar-skill
  - https://w3id.org/ktl/knowledge/references/lokf-toolkit
relatedTo:
  - https://w3id.org/ktl/knowledge/playbooks/website
about:
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
definedBy:
  - https://w3id.org/ktl/knowledge/references/agent-skills-specification
generated:
  by: process:ktl-librarian
  at: "2026-10-26T20:05:58Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-18T17:45:03Z"
---

# Overview

ktl-website installs a website for the knowledge bundle in the repository it is invoked from: an Astro Starlight site under `website/`, built from the bundle and from the repository's README, docs and changelog. The site shows a page per concept with the trust label `knowledge-report.sh` gives it, a health page, a knowledge graph, and search that filters by trust and type. It serves the four files `lokf export` writes under `/knowledge/`. When the repository has them, it also shows the LinkML schema's pages, which `gen-doc` writes, under a Schema topic, and it can serve SQLite databases that open in Datasette Lite in a new tab. The architecture page names it the sixth skill, optional like `ktl-prose`, and links this repository's own site, at `https://w3id.org/ktl/`, as the template's first copy.

It runs once, to install `website/`, or again to repair or update it. It writes nothing into the bundle, the README, the docs or the changelog. ktl-sidecar runs first, since the site builds from the sidecar's scripts and toolkit, and ktl-librarian and ktl-curator change what the pages say. Every file is copied from the skill's `templates/`, never retyped.

Three files are the repository's own once written, and a repair never replaces them: `website/site.config.mjs`, `website/README.md` and `website/src/styles/custom.css`. The skill never writes into a `website/` that is not its own, which is one with no `site.config.mjs`. It stops when the sidecar's preflight reports the bundle unhealthy.

It has eight steps, 0 to 6 with a 5b:

- **Step 0.** Run `scripts/website-preflight.sh`, which runs the sidecar's own preflight inside it and says whether another publisher already holds the repository's Pages. It also says whether a `justfile` has the `gen-doc` and `build-browse` recipes that write the schema's pages and the data, and whether `just` is installed to run them. Its `mkdocs` line says whether `mkdocs.yml` is at the root: an mkdocs site, which the knowledge site replaces (0.56.0). The skill then reads `mkdocs.yml` once, by eye, to find a `REDIRECTS` entry for each page its `nav` names, the two entries that follow the schema's `/elements/` addresses, and the folders `exclude_docs` names for `DOCS.exclude`. Resolve four placeholders: `<REPO_OWNER>` and `<REPO_NAME>` from the origin remote, never from a person's name, and `<PROJ_NAME>` and `<PROJ_DESC>`, the site's title and description.
- **Step 1.** Copy `templates/website` to `website/`, and substitute the placeholders in `site.config.mjs` and `README.md` as literal text through Python, never sed. Then set the logo, the branch, a custom domain or a user site's empty `BASE`, and leave the `"auto"` options alone unless the person wants a part left out or placed. When the site replaces an mkdocs site, write the `REDIRECTS` and `DOCS.exclude` entries Step 0 read. Set `BROWSE` only when the person wants the data published, since its databases become public.
- **Step 2.** Add an exclusion for the generated folders, `website/(dist|public|src/content|src/generated|node_modules)/`, to each Markdown lint, link check or spell check configuration, and change nothing else at the root.
- **Step 3.** Verify that no placeholder survives, and print what the sync will read with `node website/scripts/config.mjs`.
- **Step 4.** Build with `npm ci --ignore-scripts && npm run build`. The first installs the pinned packages and runs none of their install scripts. The second runs the sync, the build and a check of every link between the pages. With no Node.js or uv, report the build as skipped.
- **Step 5.** Optionally copy the deploy workflow, `knowledge-website.yaml`. Skip it when `.lokf/` is gitignored or the repository is not on GitHub.
- **Step 5b.** When the preflight's `mkdocs` line found `mkdocs.yml`, give the maintainer the retirement list in `references/deploy.md`, and run none of its Pages or branch steps. In order, the list says to remove both publishers, remove what only mkdocs used, switch Pages to Actions, check the kept addresses, and delete the `gh-pages` branch last. With the maintainer's agreement, put the list's file changes on the site's branch, and say once that the pull request preview is lost (0.56.0).
- **Step 6.** Hand off: the guessed values, the build's result, what the site shows and leaves out, the preflight's last line, and the site's `/knowledge/` address as a candidate `base_iri`.

`references/customising.md` describes every option in `site.config.mjs`. Five are required: `REPO`, `SITE`, `BASE`, `TITLE` and `DESCRIPTION`. For each part of the repository the site can show, `"auto"` shows it when the repository has it, and `null` leaves it out. Since 0.56.0 `REDIRECTS` maps an old address under `BASE` to a page of the site, and an entry whose key and value both end in `/[...slug]` stands for one redirect per schema page. The same release added `DOCS.exclude`, which names the paths under the docs folder that are not pages. A path in it that names nothing stops the build. `SCHEMA` and `BROWSE` each name a folder the repository builds rather than commits, and the command the sync runs when the folder is missing. A command that starts with `just` makes the workflow install `just`.

`references/inputs.md` says what each page is built from. Since 0.53.0 it also says that raw HTML in any Markdown the site renders passes as GitHub renders a README, through `scripts/raw-html.mjs`, and that the sync copies a file only when the file is inside the repository. An SVG that holds a script, an event handler or a `javascript:` address is left out. Since 0.56.0 a docs page's address is the one Starlight gives it, `/docs/<name>/` in lower case, and a folder's `index.md` is at the folder's address and comes first in its group as the Overview. `references/prerequisites.md` gives each preflight line in plain words, and the contract's check 12w holds that page to every line the preflight can print as missing or a warning.

Since 0.43.0 (2026-10-15, `CHANGELOG.md`) the site also serves the whole bundle as `llms-full.txt`, each concept after its trust label, and the bundle log as an Atom feed, `knowledge/log.xml`, one entry per day. It serves the home page, each docs page and each extra page as Markdown too, at the page's path with `.md` added. A concept page links the concept's history and names its licence, and opens the knowledge graph on the concept at `/graph/?concept=<id>`. A link to a concept shows the concept's title, type, trust label and definition on hover and on focus, from `knowledge/previews.json`.

Since 0.45.0 (2026-10-16, `CHANGELOG.md`) a concept's card shows its open questions beside its trust label. The label of a confirmed concept that a question put back to draft reads *reopened*, not *still a draft*.

Since 0.48.0 (2026-10-17, `CHANGELOG.md`) a figure on a wide screen stays in the text column, and a click opens it at full size. The change is in the template's `theme.css` and `Mermaid.astro`, so a host gets it with its next website repair.

Since 0.53.0 (2026-10-19, `CHANGELOG.md`) a domain host's graph page draws the workspace. Its *The workspace* view draws every bundle the domain names, each in a colour and shape of its own, with the links between bundles dashed, from the `graph.json` the federation workflow serves. `WORKSPACE` in `site.config.mjs` turns the view on or off, and `"auto"` turns it on when the repository has `.github/workflows/knowledge-federation.yaml` (`references/customising.md`).

Since 0.54.0 (2026-10-20, `CHANGELOG.md`) the graph page keeps the graph at full height in full screen. Search and filters sit in a side panel that scrolls, and switching between *This bundle* and *The workspace* draws the other graph in place, so full screen stays on. Each filter shows a count, each group has *All* and *None*, and a line says "N of M concepts shown" whenever a filter is off. Every filter still starts on.

Since 0.56.1 (`CHANGELOG.md`) a concept's card, its link preview and its social card give the genre beside the type as a plain tag. A genre that repeats the type is left off, and search gains a Genre filter. A type is worded as the bundle's prose spells it, so `SlsaSourceControlSystem` reads "SLSA source control system" on every card and in relation names. The site's host is lowercased, as Astro writes it, so an owner spelt with capitals passes the link check. A page the browser kept from before a deploy reloads once when the deploy removed its stylesheet.

A release page links the repository, the docs and the bundle at the release's tag, which the `RELEASE_TAG` option names. A page and its retelling offer each other as reading levels: a `PAGES` entry's `retells` names the page it retells, and a concept with an `audience` field or an `audience-` tag retells the concept its `derivedFrom` names.

# Deployment

The workflow has two jobs. `build` installs the lokf toolkit with `uv sync --locked`, and runs the `just` that `.lokf/uv.lock` pins where it pins one, with that command alone linked onto PATH (0.56.1). It installs the site's packages with `npm ci --ignore-scripts`, so no package runs an install script. It builds the site with Astro's telemetry off and uploads it, and holds `contents: read` and no secret. Third-party code runs in that job only, beside the repository's own: `site.config.mjs`, the files under `website/`, and the commands that build the schema's pages and the data.

`deploy` runs harden-runner and GitHub's own `deploy-pages` action and nothing else, in the `github-pages` environment, which GitHub limits to the default branch when it creates it. It runs on the default branch only, and only once the repository variable `KNOWLEDGE_WEBSITE_ENABLED` is `true`. Until then the workflow builds on every pull request and deploys nothing. It also runs every Monday from the default branch, and on a change to `.linkml/`, a justfile, a `pyproject.toml` or a `uv.lock`. A schema or data change anywhere else, and a promoted changelog, reach the site with that weekly run.

The variable goes under Repository variables, never on an environment, because the deploy job's `if:` sees only repository and organization variables. Setting it, and telling Pages once to take its site from Actions, are the maintainer's: the skill gives the two commands and does not run them. A repository whose Pages another publisher already holds keeps the variable unset until that publisher is retired, since two publishers overwrite each other's site.

# In this repository

This repository's own `website/` is the template's first copy, and `.github/workflows/knowledge-website.yaml` is the workflow's. The contract's check 11w holds every template byte-identical to its copy, apart from the three files the repository owns, and fails a tracked file under `website/` that has no template. The `smoke-test-website` job builds the template on a host made from the sidecar's dummy skeleton twice: once with a README, a docs page, a changelog, the schema's pages and the data, and once with none of them. The skill was added in 0.39.0 (2026-10-13), and 0.41.0 added the Schema topic, the data pages and the weekly run (2026-10-14, `CHANGELOG.md`).
