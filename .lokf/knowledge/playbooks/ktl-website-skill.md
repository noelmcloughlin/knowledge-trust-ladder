---
type: Playbook
id: https://w3id.org/ktl/knowledge/playbooks/ktl-website-skill
title: ktl-website skill
description: Procedure that lays down an Astro Starlight website for the knowledge bundle in `website/` from bundled templates, with a page per concept and its trust label, a health page and the knowledge graph, and a workflow that publishes it to GitHub Pages once `KNOWLEDGE_WEBSITE_ENABLED` is set; or repairs and updates a site it laid down.
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
  at: "2026-10-14T22:07:45Z"
status: draft
verified:
- by: process:ktl-librarian
  at: "2026-10-14T22:07:45Z"
---

# Overview

ktl-website lays a website for the knowledge bundle down in the repository it is invoked from: an Astro Starlight site under `website/`, built from the bundle and from the repository's README, docs and changelog. The site shows a page per concept with the trust label `knowledge-report.sh` gives it, a health page, a knowledge graph, and search that filters by trust and type. It serves the four files `lokf export` writes under `/knowledge/`. When the repository has them, it also shows the LinkML schema's pages, which `gen-doc` writes, under a Schema topic, and it can serve SQLite databases that open in Datasette Lite in a new tab. The architecture page names it the sixth skill, optional like `ktl-prose`, and says the roles lose nothing without it.

It runs once, to lay `website/` down, or again to repair or update it. It writes nothing into the bundle, the README, the docs or the changelog. ktl-sidecar runs first, since the site builds from the sidecar's scripts and toolkit, and ktl-librarian and ktl-curator change what the pages say. Every file is copied from the skill's `templates/`, never retyped.

Three files are the repository's own once written, and a repair never replaces them: `website/site.config.mjs`, `website/README.md` and `website/src/styles/custom.css`. The skill never writes into a `website/` that is not its own, which is one with no `site.config.mjs`. It stops when the sidecar's preflight reports the bundle unhealthy.

It has seven steps, 0 to 6:

- **Step 0.** Run `scripts/website-preflight.sh`, which runs the sidecar's own preflight inside it and says whether another publisher already holds the repository's Pages. It also says whether a `justfile` has the `gen-doc` and `build-browse` recipes that write the schema's pages and the data, and whether `just` is installed to run them. Resolve four placeholders: `<REPO_OWNER>` and `<REPO_NAME>` from the origin remote, never from a person's name, and `<PROJ_NAME>` and `<PROJ_DESC>`, the site's title and description.
- **Step 1.** Copy `templates/website` to `website/`, and substitute the placeholders in `site.config.mjs` and `README.md` as literal text through Python, never sed. Then set the logo, the branch, a custom domain or a user site's empty `BASE`, and leave the `"auto"` options alone unless the person wants a part left out or placed. Set `BROWSE` only when the person wants the data published, since its databases become public.
- **Step 2.** Add an exclusion for the generated folders, `website/(dist|public|src/content|src/generated|node_modules)/`, to each Markdown lint, link check or spell check configuration, and change nothing else at the root.
- **Step 3.** Verify that no placeholder survives, and print what the sync will read with `node website/scripts/config.mjs`.
- **Step 4.** Build with `npm ci && npm run build`, which runs the sync, the build and a check of every link between the pages. With no Node.js or uv, report the build as skipped.
- **Step 5.** Optionally copy the deploy workflow, `knowledge-website.yaml`. Skip it when `.lokf/` is gitignored or the repository is not on GitHub.
- **Step 6.** Hand off: the guessed values, the build's result, what the site shows and leaves out, the preflight's last line, and the site's `/knowledge/` address as a candidate `base_iri`.

`references/customising.md` describes every option in `site.config.mjs`. Five are required: `REPO`, `SITE`, `BASE`, `TITLE` and `DESCRIPTION`. For each part of the repository the site can show, `"auto"` shows it when the repository has it, and `null` leaves it out. `SCHEMA` and `BROWSE` each name a folder the repository builds rather than commits, and the command the sync runs when the folder is missing. A command that starts with `just` makes the workflow install `just`. `references/inputs.md` says what each page is built from. `references/prerequisites.md` gives each preflight line in plain words, and the contract's check 12w holds that page to every line the preflight can print as missing or a warning.

# Deployment

The workflow has two jobs. `build` installs the lokf toolkit with `uv sync --locked` and the site's packages with `npm ci`, builds the site and uploads it, and holds `contents: read` and nothing else. `deploy` runs only GitHub's own `deploy-pages` action, in the `github-pages` environment. It runs on the default branch only, and only once the repository variable `KNOWLEDGE_WEBSITE_ENABLED` is `true`. Until then the workflow builds on every pull request and deploys nothing. It also runs every Monday from the default branch, and on a change to `.linkml/`, a justfile, a `pyproject.toml` or a `uv.lock`. A schema or data change anywhere else, and a promoted changelog, reach the site with that weekly run.

The variable goes under Repository variables, never on an environment, because the deploy job's `if:` sees only repository and organization variables. Setting it, and telling Pages once to take its site from Actions, are the maintainer's: the skill gives the two commands and does not run them. A repository whose Pages another publisher already holds keeps the variable unset until that publisher is retired, since two publishers overwrite each other's site.

# In this repository

This repository's own `website/` is the template's first copy, and `.github/workflows/knowledge-website.yaml` is the workflow's. The contract's check 11w holds every template byte-identical to its copy, apart from the three files the repository owns, and fails a tracked file under `website/` that has no template. The `smoke-test-website` job builds the template on a host made from the sidecar's dummy skeleton twice: once with a README, a docs page, a changelog, the schema's pages and the data, and once with none of them. The skill was added in 0.39.0 (2026-10-13), and 0.41.0 added the Schema topic, the data pages and the weekly run (2026-10-14, `CHANGELOG.md`).
