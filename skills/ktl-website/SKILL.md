---
name: ktl-website
description: 'Build a browsable website for the `.lokf/` knowledge bundle that ktl-sidecar installed in this repository: an Astro Starlight site in `website/`, with a page per concept and its trust label, a health page, a knowledge graph, search by trust and type, the four `lokf export` files served beside the pages, and the README, the docs, the changelog, the LinkML schema''s pages and the data in Datasette Lite when the repository has them, deployed to GitHub Pages by a workflow. Use when: someone asks to publish, browse, present or deploy the knowledge bundle; wants a website, a docs site or GitHub Pages for it, or one to replace an mkdocs site; or asks to repair or update a `website/` this skill laid down. Not for writing or confirming concepts; that is ktl-librarian and ktl-curator. Not for installing the bundle itself; that is ktl-sidecar, which runs first. Keywords: website, GitHub Pages, Astro, Starlight, documentation site, knowledge graph, LinkML, Datasette, OKF, LOKF, trust ladder.'
license: Apache-2.0
compatibility: 'Requires a `.lokf/` sidecar from ktl-sidecar 0.30.0 or later (its `knowledge-report.sh`, and a committed `uv.lock`), uv, Node.js 22.12 or later with npm, a POSIX shell (bash; Git for Windows on Windows) and python3 or uv for placeholder substitution. Step 5''s workflow is GitHub Actions and GitHub Pages; on another forge the host publishes `website/dist` itself.'
---

# ktl-website

Lay down a **website** for the knowledge bundle in the repository this skill is invoked from. It is an Astro Starlight site under `website/`, built from the bundle and from the repository's README, docs and changelog, with a workflow that publishes it to GitHub Pages. Every file is copied from `templates/` (paths below are relative to this skill's directory), never retyped. The site shows a page per concept with the trust label `knowledge-report.sh` gives it, a health page, a knowledge graph, and search that filters by trust and type. It serves the four files `lokf export` writes under `/knowledge/`, so the repository becomes a producer node for the bundle's IRIs.

> Model: a small or mid-tier model is enough here: Step 1 copies templates and substitutes placeholders, and Step 0 is structured file lookup. Mistakes are caught by Step 3's grep, Step 4's build and Step 6's hand-off.

## Scope

- **This skill** runs **once**, to lay `website/` down, or again to **repair** or **update** it: copy each template over a copy that is missing or differs. It writes nothing into the bundle, the README, the docs or the changelog.
- **ktl-sidecar** runs first: the site builds from the sidecar's scripts and toolkit. **ktl-librarian** and **ktl-curator** change what the pages say.

> Guardrails: three files are the repository's own once written, and a repair never replaces them: `website/site.config.mjs`, `website/README.md` and `website/src/styles/custom.css`. A `website/` that is not this skill's (no `site.config.mjs` in it) is never written into; stop and ask. Stop too when the sidecar's preflight reports the bundle unhealthy, and send that to ktl-sidecar or ktl-librarian first. Deployment is GitHub Actions and GitHub Pages; elsewhere, [references/deploy.md](references/deploy.md) says what the host does itself.

## Step 0 - Gather the facts

**First, the preflight.** Run `bash scripts/website-preflight.sh <repo-root>` from this skill's directory and read its screen before anything else. It runs the sidecar's own preflight inside it, then checks the report script, the toolkit and its lock, Node.js and npm, and the origin remote and the default branch. It says whether another publisher already holds the repository's Pages, whether `website/` exists, and which of the README, `docs/`, `CHANGELOG.md` and `.assets/` the site can show. Its `mkdocs` line says whether an mkdocs site is there for the website to replace. Its last line names what is missing and which steps that disables; repeat that line in the Step 6 hand-off. When the person cannot act on a `missing` or `warn` line, write them a request note from [references/prerequisites.md](references/prerequisites.md).

Resolve every placeholder from real sources before writing anything; never leave a `<...>` token behind.

| Placeholder | Meaning | Where to find it |
| --- | --- | --- |
| `<REPO_OWNER>` | the repository's owner on GitHub, as its address spells it | `git remote get-url origin`: the part before the repository name (`noelmcloughlin` in `github.com/noelmcloughlin/ai-linkmo`); the preflight's `git` line prints both |
| `<REPO_NAME>` | the repository's name on GitHub | the same remote, after the owner, without `.git` |
| `<PROJ_NAME>` | the project's human-readable name, which is the site's title | the bundle's `index.md` `title` without "Knowledge Bundle", the README's `#` title, or a manifest `name` |
| `<PROJ_DESC>` | one sentence, the site's description and the home page's tagline when no other is set | the bundle's `index.md` `description`, the quoted `>` line of `llms.txt`, or the README's first sentence |

`<REPO_OWNER>` and `<REPO_NAME>` come from the remote, never from a person's name: Pages serves the site at `https://<REPO_OWNER>.github.io/<REPO_NAME>/`, and the sidecar's `<OWNER_SLUG>` is a different thing. A user site (the `<owner>.github.io` repository) and a custom domain change `SITE` and `BASE` as [references/deploy.md](references/deploy.md) says.

Then settle, from the preflight's lines, what the site shows: whether the README, the docs, the changelog, the figures and the schema's pages are there, and whether a `build-browse` recipe writes data. The data goes on the site only when the person asks for it, since its databases become public. The logo (`LOGO`) stays `"auto"`, the Knowledge Trust Ladder logo, unless the person names a file of the repository's own, such as one the `assets` line lists. The template's `"auto"` settings take each when it is. [references/customising.md](references/customising.md) describes every option.

**When the site replaces an mkdocs site**, which the `mkdocs` line names, read `mkdocs.yml` once, by eye. Give each page `nav` names an entry in `REDIRECTS` from its mkdocs address, such as `"/about": "/docs/about/"`. Give the schema's folder two entries, `"/elements": "/schema/"` and `"/elements/[...slug]": "/schema/[...slug]"`, which follow the schema as it grows. Put each folder `exclude_docs` names in `DOCS.exclude`, and check the Pages address against `site_url`. The redirects keep those addresses after `mkdocs.yml` is gone, because the w3id rules for a schema name them.

## Step 1 - Lay the site down

```bash
cp -R <this skill>/templates/website website && mv website/gitignore website/.gitignore
```

Only two files carry placeholders: `website/site.config.mjs` (REPO_OWNER, REPO_NAME, PROJ_NAME, PROJ_DESC) and `website/README.md` (the same). Substitute them as literal text through Python, as ktl-sidecar does, never through sed:

```bash
export REPO_OWNER REPO_NAME PROJ_NAME PROJ_DESC
grep -rl -e '<REPO_' -e '<PROJ_' website \
  | xargs -I{} python3 -c '
import os, sys
path = sys.argv[1]
text = open(path, encoding="utf-8").read()
for token in ("REPO_OWNER", "REPO_NAME", "PROJ_NAME", "PROJ_DESC"):
    text = text.replace("<" + token + ">", os.environ[token])
open(path, "w", encoding="utf-8").write(text)
' {}
```

Then edit `website/site.config.mjs` for what the preflight settled: `LOGO` when the person named a logo of the repository's own, `BRANCH` when the default branch is not `main`, `CUSTOM_DOMAIN` for a custom domain, and `BASE = ""` for a user site. Leave the `"auto"` options alone unless the person wants a part left out (`null`) or placed (`DOCS.groups`, `PAGES`, `HOME.actions`). When the site replaces an mkdocs site, write the `REDIRECTS` and `DOCS.exclude` entries that Step 0 read. Set `BROWSE` to the data's folder and the command that writes it when the person wants the data published.

**Repair or update.** When `website/site.config.mjs` already exists, the preflight's `website` line names each file that differs from its template or is missing. Copy those templates over, one file at a time, and never the three files the repository owns. A new option arrives with a default in `scripts/config.mjs`, so an older `site.config.mjs` keeps working.

## Step 2 - Keep the repository's checks off the generated folders (add only)

The build writes `website/dist/`, `website/public/`, `website/src/content/`, `website/src/generated/` and `website/node_modules/`, which `website/.gitignore` keeps out of git. A Markdown lint, link check or spell check that runs over `**/*.md` still reaches them locally; the preflight's `lint` line names the configurations. Add an exclusion for `website/(dist|public|src/content|src/generated|node_modules)/` to each, as the skills repository's `lychee.toml` and `.markdownlint-cli2.jsonc` do, and nothing else at the root. If the repository runs Dependabot, suggest the `npm` entry for `/website` from [references/deploy.md](references/deploy.md) in one line; do not add it unasked.

## Step 3 - Verify

```bash
grep -rn -e '<REPO_' -e '<PROJ_' website/
```

Zero hits means fully resolved. Then `node website/scripts/config.mjs` prints what the sync will read: check that `LOGO`, `DOCS`, `CHANGELOG` and `HOME.source` say what the person expects.

## Step 4 - Build

```bash
cd website && npm ci --ignore-scripts && npm run build
```

`npm ci --ignore-scripts` installs the pinned packages and runs none of their install scripts, and `npm run build` runs the sync (`lokf export` from `.lokf/`'s own environment, the report script, the pages), the build, and a check of every link between the pages. A schema or data folder not built yet is built first, with its command. The three errors a first build meets: a docs page with no group (`DOCS.groups` is out of step), a home source with no `#` title (`HOME.source`), and a missing `knowledge-report.sh` (the sidecar repair). `npm run dev` serves the site at `http://localhost:4321<BASE>/`. Commit `website/`; the generated folders are ignored. With no Node.js or uv, report the build as skipped: the workflow builds in CI. [references/inputs.md](references/inputs.md) says what each page is built from.

## Step 5 - Install the deploy workflow (optional)

Skip this step when `.lokf/` is gitignored (the workflow builds from the checkout) or the repository is not on GitHub. Copy `templates/github/knowledge-website.yaml` to `.github/workflows/knowledge-website.yaml`; it has no placeholders. It builds the site on every pull request that touches its inputs and deploys nothing until the repository variable `KNOWLEDGE_WEBSITE_ENABLED` is `true`. Setting it, and the one-time switch of Pages to Actions, are the maintainer's: give the two commands from [references/deploy.md](references/deploy.md), and do not run them. When the preflight's `pages` line warned of another publisher, install the workflow all the same and say that the variable stays unset until that publisher is retired; the page has the options. An mkdocs site is retired in Step 5b.

## Step 5b - Retire mkdocs (the maintainer's)

When the preflight's `mkdocs` line found `mkdocs.yml`, this site replaces it, and the build's link check has followed every redirect Step 1 wrote. Retiring mkdocs changes Pages and deletes a branch, so give the maintainer the list in [references/deploy.md](references/deploy.md#retiring-mkdocs) and run none of its Pages or branch steps. With the maintainer's agreement, put the list's file changes on the site's branch. Say once that the pull request preview is lost.

## Step 6 - Hand off

Tell the person:

- which Step 0 values were **guessed** rather than found (`<PROJ_DESC>` above all, and a logo when the person did not name one);
- whether Step 4's build ran and passed, or was skipped, and what the sync printed (`sync: N concept pages, ...`);
- which parts the site shows (README, docs, changelog, figures, logo, the schema's pages, the data) and which it left out, and why;
- what was left alone: an existing `website/`, the lint configurations, Pages and the variable;
- when the site replaces an mkdocs site, the redirects written and the Step 5b steps that are still the maintainer's;
- the preflight's last line, as printed;
- that the site serves the four `lokf export` files at `<SITE>/<BASE>/knowledge/`, so that address is a candidate `base_iri` for the bundle when its current one is a placeholder or a code-host URL (ktl-librarian's Rule 2 has the migration);
- that the next ktl-librarian run reads the site as any other change to the repository, with `website/README.md` as the source for a playbook concept.
