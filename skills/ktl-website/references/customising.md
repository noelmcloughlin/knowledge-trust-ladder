# Step 1: the options in site.config.mjs, and the files the repository owns

`website/site.config.mjs` holds every value the site takes from the repository: its addresses, its title, and which of its files the site shows beside the knowledge bundle. `scripts/config.mjs` reads it, fills in each option left out, settles each `"auto"` against the repository and checks the required values; `node scripts/config.mjs` prints the result. Three files are the repository's own, and the skill's repair never replaces them: `site.config.mjs`, `README.md` and `src/styles/custom.css`. Every other file under `website/` is a copy of a template.

## The options

| Option | Takes | Left out, or `"auto"` | `null` |
| --- | --- | --- | --- |
| `REPO` | `"owner/name"` on GitHub | required | |
| `SITE`, `BASE` | the Pages domain, `https://<owner>.github.io`, and the path under it, `/<name>` | required | |
| `TITLE`, `DESCRIPTION` | the site's title, and one sentence for search engines and link previews | required | |
| `BRANCH` | the branch an "Edit page" link opens | `main` | |
| `CUSTOM_DOMAIN` | a domain the sync writes to `public/CNAME`; `SITE` and `BASE` follow from it | no custom domain | the same |
| `LOGO` | `{ light, dark, favicon }`, paths from the repository root, or one path as the light version alone; `dark` defaults to `light`, and `favicon` to `light` when that is an SVG | the Knowledge Trust Ladder logo, also the favicon: a `knowledge-trust-ladder-logo.svg` the repository already has, or else the copy in `src/assets/` | the title as text, and the site's own ladder mark as favicon |
| `ASSETS` | the folder of figures the README and the docs pages show, served under `/assets/` | `.assets/` when there is one | no figures folder; a link to a figure goes to the repository |
| `DOCS` | `{ dir, groups }`: the docs folder, and the sidebar groups its pages sit in, each page named by its path under the folder without `.md` | `docs/` when there is one, every page in one Guides group by title | no docs pages |
| `CHANGELOG` | a Keep a Changelog file, read as a page per release | `CHANGELOG.md` when it holds a released version | no Releases topic |
| `PAGES` | `[{ slug, source, label }]`: pages from files outside the docs folder, each at `/<slug>/`, listed after Home | none | |
| `HOME` | `{ source, tagline, actions }`: the home page's source file, the tagline under its title, and its buttons | the README when it has a `#` title, else the bundle's own introduction; `DESCRIPTION` as the tagline; Browse the bundle, Bundle health and Knowledge graph as the buttons | |

`HOME.tagline` is a string, or `{ boldLineOf: "<file>" }` for the first line of that file that is bold throughout. `HOME.actions` is a list of `{ text, link, icon, variant }` with site-relative links such as `/knowledge/`; the first is the primary button, and `variant: "secondary"` marks the rest.

With `DOCS.groups`, the sync stops with an error when a group names a page that is not there or a page has no group, so a new page cannot go missing from the sidebar. A page named after its group, such as `docs/guides.md` under a group labelled Guides, becomes that group's overview. The pages git sees count: a folder a generator writes and `.gitignore` names stays out.

## Two configurations

A bare repository, with a bundle and a README, is the template as Step 1 fills it: the five required values, `LOGO`, `ASSETS`, `DOCS` and `CHANGELOG` at `"auto"`, no `PAGES`, and `HOME` at its defaults. Such a site has the Knowledge Trust Ladder logo, a home page from the README, the bundle's pages, the health page, the graph and search. It gains a Guide topic or a Releases topic the day a `docs/` folder or a changelog appears.

The skills repository's own `website/site.config.mjs` sets every option: a logo, four docs groups, a tagline taken from a docs page, four buttons and a page for younger readers. It is the fuller example to copy from.

## The look

`src/styles/custom.css` is loaded last, so a rule there wins over the house style in `theme.css` and `catalogue.css`. The accent and the trust colours are custom properties at the top of `theme.css`; copy the ones to change into `custom.css` rather than editing `theme.css`, which a repair replaces.

## What a repair keeps

Repair mode copies each template over a copy that is missing or differs, and never touches the three files above. A new option arrives with a default in `scripts/config.mjs`, so an older `site.config.mjs` keeps working after a repair, and a person adds the option only to use it.
