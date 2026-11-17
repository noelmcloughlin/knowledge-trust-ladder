# What the site reads from the repository

Every page comes from a file the repository already holds, so a change to the site is a change to that file. This page lists each input and the rule applied to it, so a page that looks wrong can be traced to its source. Nothing is copied into the site's folder before a build: Hugo reads the files where they are, through the mounts in `hugo.toml`. Only `scripts/prepare.sh` runs first, and what it writes into `generated/` is never committed. After Hugo, `scripts/clean-html.py` cleans each page's raw HTML and `scripts/check-links.py` checks its links.

A file the repository lacks is passed over without a setting: its mount finds nothing, and the part of the site built from it is not drawn.

## The bundle

- `.lokf/knowledge/index.md`: its frontmatter (`base_iri`, `license`, `publisher`, `description`) fills the table on the bundle's overview page, and its text is that page's. The build needs this file.
- Each concept file becomes a page at `/knowledge/<id>/`. Its frontmatter is read as data, so a concept that sets `url`, `aliases`, `draft` or `layout` changes nothing. An id with a capital keeps it in the address. The page shows the concept's type, genre and tags, its definition, its checks, its review date, its sources with any `excerpt`, and its licence or the bundle's. A source under `.lokf/mirror/` names where the ingest fetched it, the source's version and the day, from the committed `.lokf/ingest.lock.yaml`; the confidential cache's lock is never read. The typed relations come from the `graph.json` that `lokf export` writes, both ways, not from the frontmatter.
- Each folder of the bundle is a group in the navigation, from its `index.md`. A new folder needs no line anywhere.
- Three names are not concepts, by the rule `knowledge-report.sh` follows: `index.md` and `log.md` in any folder, which the lokf toolkit reserves, and `diataxis.md` at the bundle's root, where the KTL Registrar plugin writes its map. A `log.md` in a folder and the root's `diataxis.md` have no page, and `scripts/lokf-export.py` keeps the root's `diataxis.md` out of the four export files, where the toolkit alone would write it as a node. Each is served as Markdown, and a link to one goes to GitHub. A `diataxis.md` in a folder is a concept like any other.
- A concept's neighbours are listed beside its words: the concepts that point at it, then the concepts it points at, each with its trust dot and the relation.
- `.lokf/knowledge/log.md`: the bundle log page, and `/knowledge/log.xml`, an Atom feed of its newest thirty days, a day being a `## YYYY-MM-DD` section. Every page names the feed in its head.
- `.lokf/scripts/knowledge-report.sh labels` and `health`: the trust label on each concept page and the numbers the health page charts. The site never derives a label itself, and the build stops on a concept with no label.
- `lokf export`, from the sidecar's own environment under the justfile's domain vocabulary: `concepts.jsonld`, `graph.json`, `graph.nt` and `datasets.jsonld` under `/knowledge/`, with every bundle `.md` file as it is in the repository and one `.jsonld` per concept. The graph page draws `graph.json`, and `/graph/?concept=<id>` opens it on that concept.

## The home page

- `README.md`, as written, its `#` title included. Its frontmatter is read as data, so no key in it can move or hide the page. Its Markdown is served at `/index.md`, as a docs page's is. With no README, the page opens with the site's title, its description and the bundle's own introduction.
- A repository with a LinkML schema of its own leads with it: the schema's title and description, how many classes, slots, enumerations and types it has, and its first six classes.
- Five buttons, the same on every site and in the same order. Quick start is the filled one, or, on a site without a quick start, the first button found. Each is looked for among the site's pages, and one that is not found keeps its place, greyed, with the reason on hover:

| Button | Found when |
| --- | --- |
| The schema | always: the repository's own schema, or else the bundle's domain vocabulary or LOKF core, as *The schema's pages* below says |
| The bundle | always |
| Architecture | `docs/architecture.md` exists |
| Glossary | the bundle has a `glossary` group, or `docs/glossary.md` exists |
| Quick start | a docs page is named `quick-start`, `quickstart` or `getting-started`; or the install page, another docs page or the README has a heading of one of those names, or *Get started* |

## The docs pages

- Each `.md` file under `docs/` becomes a page at `/docs/<name>/`, in lower case. A folder's `index.md` is that folder's own page. A file or folder whose name starts with a dot is left out, and so is a folder `docsExclude` names.
- The title is the frontmatter's `title`, or the file's first `#` heading. No other frontmatter key reaches Hugo.
- Each page's Markdown is served at `/docs/<name>.md`: the file from its `#` title down, with every link, image and raw-HTML address made a full one, so it reads the same away from the site. Fenced code is left as written. The page's head names the file as its `text/markdown` alternate, and `llms.txt` lists it.
- A figure or a PDF file of the folder is served as it is: a file whose name ends in `.avif`, `.gif`, `.ico`, `.jpeg`, `.jpg`, `.pdf`, `.png`, `.svg` or `.webp`, in capitals or not. No file of another kind is served, since a browser would run an HTML or XML document, whatever its name ends in, as a page of the site's origin. A link to one goes to the file on GitHub. The same holds for `.assets/`, and the bundle serves its Markdown alone.
- The pages sit in groups in the navigation, found or set as [customising.md](customising.md) says.

## Retellings

- A docs file named `<page>.<language>-simple.md` retells `<page>.md` beside it. Both pages offer *Full* and the retelling above their titles. The retelling's button reads *For readers aged 13 to 18* when the file says "This page is for readers aged 13 to 18.", and *In shorter words* otherwise.
- A concept retells the one concept it is `derivedFrom` when it names its readers, in `audience` or in a tag such as `audience-13-18`.
- A retelling has no line in the navigation, and a page with no retelling shows no choice.

## The schema's pages

- The schema is the file `site.toml`'s `schema` names, when it is set: a path from the root, or `pkg:<package>/<path>` for a schema inside a Python package, found without importing it in the environment of the uv project `schemaProject` names. Otherwise it is the first `src/<name>/schema/<name>.yaml` whose folder and file share a name, in `site.toml`'s `linkml` folder, at the root, then under `.linkml/`.
- With none, it is the schema the bundle is written in: the domain vocabulary in `.lokf/schema/domain.yaml`, on a host whose bundle federates others, or else LOKF core, `.lokf/schema/lokf.yaml` or the copy in the `lokf` package that `.lokf/uv.lock` pins. Its overview says so and names LOKF's version, and its elements have no `/elements/<Name>/` address, since their identifiers resolve elsewhere.
- `prepare.sh` runs LinkML's `gen-doc` on it, with the LinkML that `.lokf/uv.lock` already pins, so the site adds no tool for it. Each class, slot, enumeration and type has `gen-doc`'s own page under `/schema/classes/`, `/schema/slots/`, `/schema/enums/` and `/schema/types/`, its name's case kept: a class has its Mermaid diagram, its slots with the inherited ones, where it is used, its mappings, and its YAML as written and as induced. Imports are read, so a type such as `string` has a page.
- Each element also answers at `/elements/<Name>/`, whatever its kind, which sends the browser on to its page. That is the address mkdocs gave it and the one a schema's w3id rules point at, so it needs no setting. `/elements/` itself goes to the overview.
- The overview shows an entity-relationship diagram of the whole schema, which `gen-erdiagram` writes, unless it is too large for Mermaid to draw. The schema file is served beside the pages, with each local file it imports at the same relative path, so the served copy loads as the repository's does.
- `gen-doc` writes for mkdocs, so its frontmatter and search wrapper are removed and each `<details>` is given the blank lines that make its YAML a code block.
- Search covers the schema's overview, classes and enumerations, and leaves its slots and types out.

## The workspace

- A repository with `.github/workflows/knowledge-federation.yaml` is a domain host, whose workflow serves the host's workspace at `workspace/` beside the site. Its graph page offers *The workspace*, under the heading *Context workspace*: each member bundle in a room of its own, with the links between bundles dashed. On any other repository the choice is greyed.

## The data

- `site.toml`'s `browse` names a folder of SQLite databases, from the repository's root. Nothing is served until it is set, since the databases go on the public site.
- Each `.sqlite`, `.sqlite3` or `.db` file in the folder is served under `/browse/`, and nothing else in it is. When the folder holds none, `prepare.sh` first runs `browseBuild` from the repository's root.
- The Datasette metadata beside them, `metadata.yaml`, `metadata.yml` or `metadata.json`, is served as `metadata.json` without its `plugins` settings. Datasette Lite runs no plugin, and those settings can hold a credential.
- Two metadata files stop the build, and so does a database with a journal beside it that is not empty, since a copy of it could be torn.
- The page at `/browse/` gives each database a section, titled and described from the metadata's `databases` entry when it has one, with its size, a download link and a link that opens it in Datasette Lite with the metadata and its analytics off. Datasette Lite runs Datasette in the reader's browser. The navigation lists the page before the changelog.

## Diagrams and figures

- A ```` ```mermaid ```` block on any page, quoted or not, is drawn in the reader's browser. The script that draws it loads only on a page that has one.
- The figures and PDF files of `.assets/` are served under `/assets/`. A click on a figure opens it over the page, as large as the window allows.
- An SVG that holds a script, an event handler or a `javascript:` address stops the build, since a browser opens an SVG as a page of its own. `scripts/check-svg.py` reads each as XML, so a prefix, a character reference or a name in capitals hides nothing. The build stops too on a `foreignObject` or XHTML element, a `data:` address a browser opens as a page, a DOCTYPE, an `xml-stylesheet` instruction, a file that is not well-formed XML, and a compressed `.svgz`.
- An image from another site loads from that site's own address. The page sends no referrer with the request.

## Links

- A relative link or image in any Markdown the site renders is resolved against the file it was written in, and a path that starts with `/` against the repository's root, as GitHub reads it. It goes to the page built from the file it names, to the figure or PDF file under `/assets/` or `/docs/`, or to the file on GitHub at the commit the site was built from. A `knowledge_bundle/...` path reads as `.lokf/knowledge/...`. A link to a release's heading in the changelog, as GitHub names it, goes to that release's page.
- An Obsidian `[[wikilink]]` in a concept becomes a link to the concept whose id is the name, or ends in `/name`, when exactly one does. Otherwise the text stays as written. The match is by pattern, so one inside a code span is rewritten too.
- A link to a concept shows the concept's trust label and definition on hover or focus.
- Raw HTML's relative `src`, `srcset` and `href` addresses resolve as a Markdown link's do. After the build, `scripts/clean-html.py` cleans it to the tags GitHub allows in a README: a tag GitHub allows keeps the attributes it allows, an address that is not `http`, `https`, `mailto`, a path or a fragment is dropped, and any other markup, such as a `<meta>` refresh or a `<style>`, is shown as text and named on the build's log. Comments go, and every element is closed. A class or a `data-` attribute stays only where the site's own rendering wrote it: on a heading's link, a diagram, an alert, a link's preview, a footnote and highlighted code. So a file cannot draw a trust label, name itself in a search filter or word a preview, in its text or in the list of a page's sections. An `<input>` stays only as a task list's checkbox. A Content-Security-Policy in every page stays as a second guard: a script loads only from the site's own `js/` and `pagefind/` folders. A Markdown link whose address is not `http`, `https`, `mailto` or a path goes nowhere.
- A Hugo shortcode, `{{< name >}}` or `{{% name %}}`, is shown as written, in a code block or out of one.
- After the build, `scripts/check-links.py` fails it when a link between the site's own pages, a link to a heading or a page's social card does not resolve, or when a link that starts with `/` falls outside the site's path. It reads the full addresses in `llms.txt`, `llms-full.txt` and every Markdown file the site serves. Links that leave the site are not checked.

## The changelog

- Keep a Changelog headings, `## [x.y.z] - YYYY-MM-DD`, become one page per release under `/changelog/version/`. What is under `## [Unreleased]` stays on the changelog's own page, under an Unreleased heading. The changelog is last in the navigation.
- A release whose tag git has links the repository, the docs folder and `.lokf/knowledge/` at that tag on GitHub, and the release itself. The tag is `releaseTag` with the release's number in place of `{version}`.

## `llms.txt` and `llms-full.txt`

- `/llms.txt` opens with the site's description, then lists the four export files, the data page and the schema file when there are, the home page and each docs page by its Markdown file, and every concept with its Markdown file and its trust label.
- `/llms-full.txt` holds every concept's text in one file, each under its address, trust label, type and definition, with every link a full address and its headings under the concept's title.

## `badge.json`

- `/badge.json` says how many of the bundle's concepts a person confirmed, as `n of m`, where `m` counts every concept, a retired one included, as the health line and the health page count them, under the label `KTL scorecard` and the mark of the Knowledge Trust Ladder (KTL), in the form a shields.io endpoint badge reads. A README shows the image `https://img.shields.io/endpoint?url=<site>/badge.json` and links it to `<site>/health/`, where `<site>` is the site's address.

## What search leaves out

- The release pages, the schema's slots and types, and a concept's record card apart from its definition. The card's type, genre and trust label are the Type, Genre and Trust filters beside the search box.
