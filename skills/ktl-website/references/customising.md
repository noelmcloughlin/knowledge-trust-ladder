# Step 1: the values in site.toml, and the files the repository owns

The site finds what it shows, so `site.toml` is short: four values every site needs, and a few a repository may add. `hugo.toml` beside it holds what is the same on every site, and `scripts/build.sh` reads both, `site.toml` second, so a value there wins. Three files are the repository's own, and the skill's repair never replaces them: `site.toml`, `README.md` and `assets/css/custom.css`. Every other file in the site's folder is a copy of a template.

## The values

| Value | Takes | Left out |
| --- | --- | --- |
| `baseURL` | the site's address, ending in `/`: `https://<owner>.github.io/<name>/` | required |
| `title` | the site's title, in the header and on every social card | required |
| `params.description` | one sentence, for search engines and link previews | required |
| `params.repo` | the repository's address on GitHub; a link to a file that is not a page goes there | required |
| `params.branch` | the branch an "Edit this page" link opens | `main` |
| `params.releaseTag` | the tag a release carries, with `{version}` for its number | `v{version}` |
| `params.logo`, `params.logoDark` | a logo of the repository's own, each a file under `.assets/` | the Knowledge Trust Ladder logo |
| `params.docsExclude` | folders under `docs/` that are not pages | `templates-linkml` and `elements`, which LinkML's `gen-doc` keeps there |
| `params.docsGroups` | the docs pages in groups: a list of `label` and `pages`, each page by its path under `docs/` without `.md` | the pages at the top of `docs/` in one group, Guides, by title, and each folder a group named by its `index.md` or by the folder |
| `params.redirects` | old addresses, each sent on to the page built from a repository file: `"about" = "docs/about.md"`. `"schema/*" = "schema/*"` stands for every page of the schema | none; a site with a schema has `"elements/*" = "schema/*"` with no setting |
| `params.browse`, `params.browseBuild` | a folder of SQLite databases, from the repository's root, to serve under `browse/` with a page that opens each in Datasette Lite, and the command that writes the folder when it holds no database | no data: the databases go on the public site, so none is served until this is set |
| `params.vendor.cytoscape.url`, `params.vendor.mermaid.url` | another address for a library the build fetches once and checks against the hash in `hugo.toml` | the public CDN |

With `docsGroups`, the build stops when a group names a page that is not there or a page is in no group, so a new page cannot go missing from the navigation. A retelling is in no group: the page it retells offers it.

A redirect whose file has no page stops the build.

## What has no value

These are found, never set. To change one, change the repository:

- **The home page** is the README. Its five buttons are the same on every site, and one is greyed until its page exists: add `docs/architecture.md`, a `glossary` group in the bundle or `docs/glossary.md`, or a docs page or heading named Quick start.
- **A retelling** is a docs file named `<page>.<language>-simple.md` beside `<page>.md`. A sentence in it such as "This page is for readers aged 13 to 18." words its button.
- **The schema** is `src/<name>/schema/<name>.yaml`, at the root first, then under `.linkml/`.
- **The workspace** appears on the graph page of a repository that has `.github/workflows/knowledge-federation.yaml`.

## The look

`assets/css/custom.css` is loaded last, so a rule there wins over the house style in `assets/css/site.css`. The colours and the trust tones are custom properties at the top of `site.css`. Copy the ones to change into `custom.css` rather than editing `site.css`, which a repair replaces.

## From the earlier Astro site

A `website/` with `site.config.mjs` is the site this skill installed before it moved to Hugo. With the person's agreement:

1. Read `site.config.mjs` and note `TITLE`, `DESCRIPTION`, `SITE`, `BASE`, `BRANCH`, `LOGO`, `DOCS.groups`, `DOCS.exclude`, `REDIRECTS`, `RELEASE_TAG` and `BROWSE`.
2. Remove the folder: `git rm -r website`, then delete what is left of it (`node_modules/`, `dist/`).
3. Install as Step 1 says, and write the noted values into `site.toml`. A redirect's target is now the file the page is built from, not its address. `BROWSE`'s `dir` and `build` become `browse` and `browseBuild`.
4. Drop what the site now finds: `HOME`, `ASSETS`, `CHANGELOG`, `SCHEMA`, `WORKSPACE`, and each `PAGES` retelling whose file is named `<page>.<language>-simple.md`. Rename a retelling that is not.
5. Change the lint exclusions and the Dependabot entry as Step 2 says: the generated folders have new names, and the packages are uv's, not npm's.

Two things change for readers. A retelling moves from its `PAGES` slug to `/docs/<page>.<language>-simple/`; add a redirect from the old slug. The schema's pages move from `/schema/<Name>/` to a folder per kind, `/schema/classes/<Name>/`; the redirect `"schema/*" = "schema/*"` keeps the old addresses working.

## What a repair keeps

Repair mode copies each template over a copy that is missing or differs, and never touches the three files above. A new value always has a default in `hugo.toml`, so an older `site.toml` keeps working after a repair.
