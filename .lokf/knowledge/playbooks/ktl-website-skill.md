---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/ktl-website-skill
title: ktl-website skill
description: Procedure that installs a Hugo website for the knowledge bundle in `website/`, or in `ktl-website/` where `website/` is another site's, from bundled templates. The site finds the README, the docs, retellings, the changelog, the figures, a LinkML schema and a domain host's workspace with no setting, shows a page per concept with its trust label, a health page and the knowledge graph, and builds with uv and no Node.js. A workflow publishes it to GitHub Pages once `KNOWLEDGE_WEBSITE_ENABLED` is set; the skill also repairs or updates a site it installed, moves its earlier Astro site to Hugo, and hands the maintainer the steps that retire an mkdocs site it replaces.
genre: how-to
resource: skills/ktl-website/SKILL.md
sources:
  - resource: skills/ktl-website/SKILL.md
    id: skill.md
    excerpt: "The home page has five buttons on every site: the schema, the bundle, the architecture page, the glossary and the quick start."
  - resource: skills/ktl-website/references/customising.md
  - resource: skills/ktl-website/references/deploy.md
  - resource: skills/ktl-website/references/inputs.md
    id: inputs.md
    excerpt: one that is not found keeps its place, greyed, with the reason on hover
  - resource: skills/ktl-website/references/prerequisites.md
  - resource: skills/ktl-website/scripts/website-preflight.sh
  - resource: skills/ktl-website/templates/github/knowledge-website.yaml
  - resource: skills/ktl-website/templates/website
  - resource: scripts/validate-repository.sh
  - resource: .github/workflows/validate.yml
  - resource: scripts/smoke-test-website.sh
    id: smoke-test-website.sh
    excerpt: "the site three times: once with a README, docs pages, a changelog, ... source and data, once with none of them, and once with a domain"
  - resource: docs/architecture.md
  - resource: docs/cast/website.md
  - resource: CHANGELOG.md
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
  at: "2026-11-17T20:29:12Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-11-17T22:28:06Z"
---

# Overview

ktl-website installs a website for the knowledge bundle in the repository it is invoked from: a Hugo site under `website/`, built from the bundle and from whatever else the repository holds. The site shows a page per concept with the trust label `knowledge-report.sh` gives it, a health page, a knowledge graph, and search that filters by trust and type. It serves the four files `lokf export` writes under `/knowledge/`, and `/badge.json`, labelled `KTL scorecard`, which says how many of the bundle's concepts a person confirmed, as `n of m`, where `m` counts every concept, a retired one included, as the health line does, in the form a shields.io endpoint badge reads, for a README to show. The architecture page names it the sixth skill, optional like `ktl-prose`, and links this repository's own site, at `https://w3id.org/ktl/`, as the template's first copy.

It runs once, to install the site, or again to repair or update it. It writes nothing into the bundle, the README, the docs or the changelog. ktl-sidecar runs first, since the site builds from the sidecar's scripts and toolkit. ktl-librarian and ktl-curator change what the pages say. Every file is copied from the skill's `templates/`, never retyped. The build needs uv, git and a POSIX shell, and no Node.js.

# What the site finds by itself

No setting names what the site shows, though `site.toml`'s `source` can move where the README, the docs, the changelog and the figures come from, `linkml` can move the LinkML project whose schema the site shows, and `schema` can name the schema file itself, in the repository or inside a Python package. The build otherwise looks for each input and shows what it finds:

- `.lokf/knowledge/`: the bundle's pages, the health page and the graph. The build needs it.
- `README.md`: the home page. Without one, the home page opens with the bundle's own introduction.
- `docs/**.md`: the Guide part, a page per file, each also served as Markdown at `/docs/<name>.md` with every address made full.
- `docs/<page>.<language>-simple.md`: a retelling, which `docs/<page>.md` offers above its title. A concept that names its readers in `audience` or in a tag such as `audience-13-18` retells the one concept it is `derivedFrom`.
- `src/<name>/schema/<name>.yaml`, at the root or under `.linkml/`: the Schema part, written by LinkML's `gen-doc` with the LinkML that `.lokf/uv.lock` already pins. Each element also answers at `/elements/<Name>/`, the address mkdocs gave it and the one a schema's w3id rules point at, and the home page leads with the schema.
- `.lokf/schema/domain.yaml`, else LOKF core, `.lokf/schema/lokf.yaml` or the copy in the `lokf` package: with no schema of the repository's own, the Schema part shows the bundle's domain vocabulary or LOKF core, and the home page does not lead with it.
- `CHANGELOG.md`: a page per release.
- `.assets/`: the figures.
- `.lokf/ingest.lock.yaml`: a mirrored source's origin, version and day of fetching, on its concept's card.
- `.github/workflows/knowledge-federation.yaml`: the workspace, on the graph page.

The home page has five buttons on every site: the schema, the bundle, the architecture page, the glossary and the quick start.[^skill.md] A button whose page is not there keeps its place, greyed, with the reason on hover.[^inputs.md] Quick start is the filled one, or, on a site without a quick start, the first button found. One part is set, never found: the data. `browse` in `site.toml` names a folder of SQLite databases, because the databases go on the public site. The site serves them under `/browse/`, with a page that opens each in Datasette Lite.

`references/inputs.md` gives the rule for each input. It also says that raw HTML in any Markdown the site renders is cleaned after the build, by `scripts/clean-html.py`, to the tags GitHub allows in a README, with a Content-Security-Policy in every page as a second guard. An SVG that holds a script, an event handler or a `javascript:` address stops the build. After the build, `scripts/check-links.py` fails it on a link between the site's own pages that does not resolve.

# The site's folder

A folder is this skill's when it holds `site.toml` and `hugo.toml`. The preflight's `website` line settles which folder a run uses, and the first rule that holds decides:

- When `website/` is this skill's, the skill repairs or updates the site there.
- When `ktl-website/` is this skill's, the site is there, since `website/` was another site's when the skill first ran.
- When `website/site.config.mjs` exists, it is the skill's earlier Astro site, which Step 1 moves to Hugo in place.
- When `website/` exists otherwise, it is another site's, and the skill installs into `ktl-website/`.
- When neither folder exists, the skill installs into `website/`.

Three files are the repository's own once written, and a repair never replaces them: `site.toml`, `README.md` and `assets/css/custom.css`. The skill stops when the sidecar's preflight reports the bundle unhealthy.

# Steps

It has eight steps, 0 to 6 with a 5b:

- **Step 0.** Run `scripts/website-preflight.sh`, which runs the sidecar's own preflight inside it. It says whether another publisher already holds the repository's Pages, which folder the site is in or goes in, and which inputs the site will find. Its `mkdocs` line says whether an mkdocs site is there for the website to replace. Resolve four placeholders: `<REPO_OWNER>` and `<REPO_NAME>` from the origin remote, never from a person's name, and `<PROJ_NAME>` and `<PROJ_DESC>`, the site's title and description. When the site replaces an mkdocs site, read `mkdocs.yml` once, by eye, for a `[params.redirects]` entry for each page its `nav` names and the folders `exclude_docs` names for `docsExclude`.
- **Step 1.** Copy `templates/website` to the site's folder, and substitute the placeholders in `site.toml` and `README.md` through Python, never sed. The script writes each value into `site.toml` as an escaped TOML string, and stops before it writes either file on a value with a line break or a character that does not print. Then edit `site.toml` only for what the preflight settled: `branch`, `baseURL` for a custom domain or a user site, and a logo. Set `browse` only when the person asks to publish the data. A repair copies each template that is missing or differs, one file at a time. With the person's agreement, an earlier Astro site's values move into `site.toml` and its old files are removed, as `references/customising.md` lists.
- **Step 2.** Add an exclusion for `website/(dist|generated|resources|\.venv)/` to each Markdown lint, link check or spell check configuration, and change nothing else at the root. Where the repository runs Dependabot, suggest the `uv` entry for the site's folder in one line.
- **Step 3.** Verify with `grep` that no placeholder survives in `site.toml` or `README.md`. The build refuses a `site.toml` that still holds one.
- **Step 4.** Build with `bash website/scripts/build.sh`. It runs `scripts/prepare.sh`, which runs `lokf export`, `gen-doc` for a schema and the report script from `.lokf/`'s own environment. Then it runs Hugo and Pagefind, which uv installs from PyPI at the versions the site's `uv.lock` holds. The raw-HTML cleaning and the link check run last. `build.sh serve` serves the site locally and rebuilds it on each edit. With no uv, report the build as skipped.
- **Step 5.** Optionally copy the deploy workflow, `knowledge-website.yaml`. Skip it when `.lokf/` is gitignored or the repository is not on GitHub.
- **Step 5b.** When the preflight's `mkdocs` line found `mkdocs.yml`, give the maintainer the retirement list in `references/deploy.md`, and run none of its Pages or branch steps. In order, the list says to remove both publishers, remove what only mkdocs used, switch Pages to Actions, check the kept addresses, and delete the `gh-pages` branch last. With the maintainer's agreement, put the list's file changes on the site's branch, and say once that the pull request preview is lost.
- **Step 6.** Hand off: the site's folder, the guessed values, the build's result, which parts the site found and which home buttons are greyed, what was left alone, the preflight's last line, and the site's `/knowledge/` address as a candidate `base_iri`.

`references/customising.md` describes the values in `site.toml`. Four are required: `baseURL`, `title`, `params.description` and `params.repo`. The others are optional: the branch, the release tag, a logo, `source`, `linkml`, `schema` and `schemaProject`, `docsExclude`, `docsGroups`, `redirects`, `browse` and `browseBuild`, and a mirror's address for Cytoscape and Mermaid. `hugo.toml` beside it holds what is the same on every site, and a value in `site.toml` wins. `references/prerequisites.md` gives each preflight line in plain words, and the contract's check 12w holds that page to every line the preflight can print as missing or a warning.

# Deployment

The workflow has two jobs. `build` checks the repository out with its full history, finds the site's folder, `website/` or `ktl-website/`, and runs its `scripts/build.sh`. When `browseBuild` runs `just`, a step before the build installs the copy `.lokf/uv.lock` pins. The job uploads the folder's `dist` as the Pages artifact, and holds `contents: read` and no secret. Third-party code runs in that job only, beside the repository's own.

`deploy` runs harden-runner and GitHub's own `deploy-pages` action, in the `github-pages` environment, which GitHub limits to the default branch when it creates it. It runs on the default branch only, and only once the repository variable `KNOWLEDGE_WEBSITE_ENABLED` is `true`. Until then the workflow builds on every pull request that touches the site's inputs and deploys nothing. It also runs every Monday from the default branch, so a change elsewhere, such as a promoted changelog, reaches the site with that weekly run.

A domain host deploys the site from its federation workflow, from the release's tag as well as the default branch, so its `github-pages` Environment admits release tags too. `uvx ktl gh enable website --run` switches Pages on, sets the variable and starts the first run, where Pages is off and no other publisher remains.

The variable goes under Repository variables, never on an environment, because the deploy job's `if:` sees only repository and organization variables. The maintainer sets it, and tells Pages once to take its site from Actions. The skill gives the two commands and does not run them. A repository whose Pages another publisher already holds keeps the variable unset until that publisher is retired, since two publishers overwrite each other's site. A domain host leaves the variable unset, because its federation workflow builds the site and deploys it with the workspace beside it.

On another forge, the same `bash website/scripts/build.sh` runs in that forge's CI, and the forge publishes `website/dist`. Behind a proxy, the build fetches from three places, and each has a setting. With a mirror of PyPI named in `UV_DEFAULT_INDEX`, `scripts/uv-env.sh` installs Hugo, Pagefind and the toolkit in `.lokf/` from it, at the versions and hashes the locks pin, so no lock is written again. uv downloads a Python from github.com where the machine has none at 3.11 or later, and the workflow's `setup-uv` step fetches uv from there, so a runner that cannot reach github.com needs uv on its image. Each job looks for uv first and keeps the runner's own. For Cytoscape and Mermaid, `site.toml` can name a mirror's address, or the site's folder can hold a copy of each, `assets/vendor/cytoscape.js` and `assets/vendor/mermaid.js`, which the build takes first and checks against the same hash in `hugo.toml`. `scripts/vendor.sh` writes both copies from an npm registry.

# In this repository

This repository's own `website/` is the template's first copy, and `.github/workflows/knowledge-website.yaml` is the workflow's. The contract's check 11w holds every template byte-identical to its copy, apart from the three files the repository owns, and fails a tracked file under `website/` that has no template. The `smoke-test-website` job builds the template three times, on a host made from the sidecar's dummy skeleton. The first build has a README, docs pages, a changelog, figures, a LinkML schema, retellings, the federation workflow, a mirrored source and data. The second has none of them, and the third has a domain vocabulary alone.[^smoke-test-website.sh]

[^skill.md]: skills/ktl-website/SKILL.md, *What the site finds by itself*
[^inputs.md]: skills/ktl-website/references/inputs.md, *The home page*
[^smoke-test-website.sh]: scripts/smoke-test-website.sh, the header comment
