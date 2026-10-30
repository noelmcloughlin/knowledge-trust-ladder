# Step 1: the options in site.config.mjs, and the files the repository owns

`website/site.config.mjs` holds every value the site takes from the repository: its addresses, its title, and which of its files the site shows beside the knowledge bundle. `scripts/config.mjs` reads it, fills in each option left out, settles each `"auto"` against the repository and checks the required values. `node scripts/config.mjs` prints the result. Three files are the repository's own, and the skill's repair never replaces them: `site.config.mjs`, `README.md` and `src/styles/custom.css`. Every other file under `website/` is a copy of a template.

## The options

| Option | Takes | Left out, or `"auto"` | `null` |
| --- | --- | --- | --- |
| `REPO` | `"owner/name"` on GitHub | required | |
| `SITE`, `BASE` | the Pages domain, `https://<owner>.github.io`, and the path under it, `/<name>` | required | |
| `TITLE`, `DESCRIPTION` | the site's title, and one sentence for search engines and link previews | required | |
| `BRANCH` | the branch an "Edit page" link opens | `main` | |
| `CUSTOM_DOMAIN` | a domain the sync writes to `public/CNAME`; `SITE` and `BASE` follow from it | no custom domain | the same |
| `LOGO` | `{ light, dark, favicon }`, paths from the repository root, or one path as the light version alone; `dark` defaults to `light`, and `favicon` to `light` when that is an SVG | the Knowledge Trust Ladder (KTL) logo, also the favicon: a `knowledge-trust-ladder-logo.svg` the repository already has, or else the copy in `src/assets/` | the title as text, and the site's own ladder mark as favicon |
| `ASSETS` | the folder of figures the README and the docs pages show, served under `/assets/` | `.assets/` when there is one | no figures folder; a link to a figure goes to the repository |
| `DOCS` | `{ dir, groups, exclude }`: the docs folder, the sidebar groups its pages sit in (each page named by its path under the folder, without `.md`), and the paths under the folder that are not pages | `docs/` when there is one, every page in one Guides group by title, `index.md` first | no docs pages |
| `REDIRECTS` | `{ "/old/": "/page/" }`: old addresses under `BASE`, each redirected to a page of the site; an entry whose key and value both end in `/[...slug]` stands for one redirect per schema page | none | |
| `CHANGELOG` | a Keep a Changelog file, read as a page per release | `CHANGELOG.md` when it holds a released version | no Releases topic |
| `RELEASE_TAG` | the tag a release carries, with `{version}` for its number; a release page links the repository, the docs and the bundle at that tag, and the release itself, when git has the tag | `v{version}` | no such links |
| `PAGES` | `[{ slug, source, label, retells, level }]`: pages from files outside the docs folder, each at `/<slug>/`, listed after Home; `retells` names the file whose page this one retells, and `level` the words for its reading level, the label when left out | none | |
| `SCHEMA` | `{ dir, build }`: the folder of the LinkML schema's pages that `gen-doc` writes, and the command that writes it, which the sync runs when the folder is missing; a folder alone needs no command | the first of the root, a linkmo project's folder and `.linkml/` whose `justfile` has a `gen-doc` recipe: its `docs/elements`, built with that recipe. Failing those, the domain schema on `.lokf/justfile`'s `schema :=` line: `.lokf/docs/elements`, built with `gen-doc --render-imports` in the sidecar's environment | no Schema topic or button |
| `BROWSE` | `{ dir, build }`: a folder of SQLite databases and their Datasette metadata, and the command that writes it | `null`, since the databases go on the public site; `"auto"` takes a linkmo project's `browse/` and its `build-browse` recipe | no data page |
| `HOME` | `{ source, tagline, actions }`: the home page's source file, the tagline under its title, and its buttons | the README when it has a `#` title, else the bundle's own introduction; `DESCRIPTION` as the tagline; Browse the bundle, Architecture when the docs folder has `architecture.md`, Schema when the site shows the schema's pages, Bundle health and Knowledge graph as the buttons | |
| `WORKSPACE` | whether the graph page offers to draw the workspace a domain host's federation workflow serves at `workspace/` under the site, every bundle the domain names: `"auto"`, `true` or `null` | on when the repository has `.github/workflows/knowledge-federation.yaml` | no workspace view |

`HOME.tagline` is a string, or `{ boldLineOf: "<file>" }` for the first line of that file that is bold throughout. `HOME.actions` is a list of `{ text, link, icon, variant }` with site-relative links such as `/knowledge/`; the first is the primary button, and `variant: "secondary"` marks the rest.

With `DOCS.groups`, the sync stops with an error when a group names a page that is not there or a page has no group, so a new page cannot go missing from the sidebar. A page named after its group, such as `docs/guides.md` under a group labelled Guides, becomes that group's overview. The pages git sees count: a folder a generator writes and `.gitignore` names stays out, and so does the `SCHEMA` folder. A path `DOCS.exclude` names stays out, and a path there that names no file or folder stops the build.

`REDIRECTS` writes a page for each old address, which redirects the browser to its new page. The link check fails when that new page is missing. Astro cannot point a wildcard at Starlight's pages, so `/[...slug]` is expanded against the schema's pages at build time.

`SCHEMA` and `BROWSE` each name a folder the repository builds rather than commits. The sync runs the `build` command from the repository root when the folder is missing, which in CI is every time, and stops when the command fails or the folder is still not there. Locally it runs once, so run the command again, or remove the folder, to see a change to the schema or the data. A `build` that starts with `just` makes the workflow install `just`.

## Two configurations

A bare repository, with a bundle and a README, is the template as Step 1 fills it: the five required values, `LOGO`, `ASSETS`, `DOCS`, `CHANGELOG` and `SCHEMA` at `"auto"`, no `PAGES`, no `BROWSE`, and `HOME` at its defaults. Such a site has the KTL logo, a home page from the README, the bundle's pages, the health page, the graph and search. It gains a Guide topic, a Releases topic or a Schema topic once a `docs/` folder, a changelog or a `gen-doc` recipe is added.

The skills repository's own `website/site.config.mjs` sets every option: a logo, four docs groups, a tagline taken from a docs page, four buttons and a page for younger readers. It is the fuller example to copy from.

## The look

`src/styles/custom.css` is loaded last, so a rule there wins over the house style in `theme.css` and `catalogue.css`. The accent and the trust colours are custom properties at the top of `theme.css`. Copy the ones to change into `custom.css` rather than editing `theme.css`, which a repair replaces.

## What a repair keeps

Repair mode copies each template over a copy that is missing or differs, and never touches the three files above. Each new option has a default in `scripts/config.mjs`, so an older `site.config.mjs` keeps working after a repair, and a person adds the option only to use it.
