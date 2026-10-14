# What the site reads from the repository

Every page comes from a file the repository already holds, so a change to the site is a change to that file. This page lists each input and the rule the sync applies to it, so a page that looks wrong can be traced to its source. The sync is `website/scripts/sync.mjs`; it runs before every build and commits nothing.

## The bundle

- `.lokf/knowledge/index.md`: its frontmatter (`base_iri`, `context`, `license`, `publisher`, `title`, `description`) fills the table on the bundle's overview page, and its text before the first heading opens that page. The sync stops without this file.
- Each concept file: `title` (the page title; the concept's path when absent), `description` (the page's meta description, as plain words), `type`, `status`, `definition`, `stale_after` (shown as the review date), `tags`, `generated` and `verified`. Its `sources`, or its `resource`, each become a link to the file on GitHub at the built commit, or to the address given. The body is rendered from its first line, with every heading moved down one level when the body starts at `#`. The typed relations come from the `graph.json` that `lokf export` writes, both ways, not from the frontmatter.
- `.lokf/knowledge/log.md`: the bundle log page.
- `.lokf/scripts/knowledge-report.sh labels` and `health`: the trust label on each concept page and the numbers the health page charts. The site never derives a label itself.
- `lokf export`, from the sidecar's own environment: `concepts.jsonld`, `graph.json`, `graph.nt` and `datasets.jsonld` under `/knowledge/`, with every bundle `.md` file as it is in the repository and one `.jsonld` per concept beside it. Each concept page links its own two files in its head.

## The home page and the extra pages

- The home page's source, from its first `#` title down (a `#` heading inside fenced code does not count). A line that links the site's own address is dropped, since on the site it would link to the page it is on. With no source, the page opens with the bundle's own introduction.
- A `PAGES` entry, from its file's `#` title down, with the entry's label as the title when the file has none.
- GitHub's `> [!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]` and `[!CAUTION]` alerts become the site's asides.
- A `<picture>` with a dark source becomes two images, one shown in each of the site's themes. When the dark source names a `-dimmed` figure and the figures folder holds a `-dark` one beside it, the site's dark theme takes the `-dark` one.

## The docs pages

- Each `.md` file git sees under the docs folder (tracked, or untracked and not ignored), except a file `PAGES` names. The title is the file's `#` line, and the description its first sentence.
- With `DOCS.groups`, a page sits where its group says; without, every page sits in one group by title, nested folders included.

## The schema's pages

- Each `.md` file in the `SCHEMA` folder, as LinkML's `gen-doc` writes it: `index.md` is the Schema topic's overview at `/schema/`, and every other page sits at `/schema/<file name>/`, its case kept, so the links in its diagram resolve. Its title is its `#` line, such as `Class: Action`, and its description the italic line under it. The sidebar groups the pages by the word that opens the title: Classes, Slots, Enumerations, Types and Subsets. A page whose title opens with none of them, the schema's own, has a page and no sidebar entry.
- mkdocs-material's frontmatter and its `<div data-search-exclude>` wrapper are dropped, and a blank line goes around each `<details>`, so the YAML inside is a code block.
- Search leaves the schema's pages out, and they share the home page's social card.
- A concept whose source is in the `SCHEMA` folder links that source's page on the site, since the folder is never on GitHub.

## Diagrams

- A ```` ```mermaid ```` block on any page, a schema page's class diagram among them, is drawn in the reader's browser, in the site's light or dark theme, with a button that shows it at its own size. The script that draws it loads only on a page that has one. A diagram's link to another page of the site opens in the same tab.

## The data

- Each `.sqlite`, `.sqlite3` or `.db` file in the `BROWSE` folder, and a `metadata.yaml`, `metadata.yml` or `metadata.json` beside them, are served under `/browse/`. Nothing else in the folder is.
- The page at `/browse/` gives each database a section, titled and described from the metadata's `databases` entry when it has one, with its size, a download link and a link that opens it in Datasette Lite with the metadata. Datasette Lite runs Datasette in the reader's browser, and the link turns its analytics off.

## Links

- A relative link, image or raw-HTML `src` or `href` in any of the pages above is rewritten to the page it names. The home page's source goes to `/`, a docs page to `/docs/<name>/`, a `PAGES` source to `/<slug>/`, a schema page to `/schema/<name>/`, a concept to `/knowledge/<id>/`, a bundle folder to its overview, and a figure to `/assets/...`. A `knowledge_bundle/...` path reads as `.lokf/knowledge/...`. Any other file goes to its page on GitHub at the commit the site was built from.
- An Obsidian `[[wikilink]]` in a concept becomes a link to the concept whose path is the name, or ends in `/name`, when exactly one does; otherwise the text stays as written.
- After the build, `scripts/check-links.mjs` fails the build when a link between the site's own pages, a link to a heading, or a page's social card does not resolve. Links that leave the site are not checked.

## The changelog

- Keep a Changelog headings, `## [x.y.z] - YYYY-MM-DD`, become one page per release and a comparison page between each pair; `## [Unreleased]` is skipped. The brackets are stripped for the plugin, and links to repository files are rewritten as above.

## The figures and the logo

- The figures folder is served under `/assets/`. The logo's light and dark files are copied to `src/generated/`, and the favicon to `/favicon.<type>`; with `LOGO = null`, the site's own ladder mark is the favicon and the title is shown as text.
- `LOGO` left out or `"auto"` takes the Knowledge Trust Ladder logo. That is a `knowledge-trust-ladder-logo.svg` git sees in the repository, tracked or untracked but never ignored, outside `website/` and outside a skill's templates, the one nearest the root first. With none, it is the copy in `website/src/assets/`. The `-dark.svg` file beside it is the dark version when there is one.

## `llms.txt`

- The quoted `>` line of the repository's `llms.txt` is the summary of the site's own `/llms.txt`; `DESCRIPTION` stands in without it. The rest of that file is generated: the docs pages, then every concept with its Markdown file and its trust label, and under Optional the schema's overview and the data page when the site has them.

## What search leaves out

- The release pages, the schema's pages, and a concept's record card apart from its definition. The card's type and trust label become the Trust and Type filters beside the search box.
