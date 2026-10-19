// The site's values and options, in one place. scripts/config.mjs reads this
// file, fills in every option left out, settles each "auto" against the
// repository and checks the required values; `node scripts/config.mjs`
// prints the result. Nothing here runs code, so the pages that show the
// title import it too.
//
// The first five values are required. The rest are optional: leave one out,
// or set it to "auto", and the site shows that part of the repository when
// the repository has it; set it to null to leave that part out.

// The repository, as owner/name, and the site's address: the owner's GitHub
// Pages domain and the path under it. A user site (the <owner>.github.io
// repository) or a custom domain sets BASE to "".
export const REPO = "noelmcloughlin/knowledge-trust-ladder";
export const SITE = "https://noelmcloughlin.github.io";
export const BASE = "/knowledge-trust-ladder";

// The site's title, in the header and on every social card, and its
// description, for search engines and as the home page's tagline when
// HOME.tagline is not set.
export const TITLE = "Knowledge Trust Ladder";
export const DESCRIPTION =
  "Agent Skills that keep a repository's knowledge as a catalogued LOKF bundle, with the trust in every claim left visible.";

// The branch an "Edit page" link opens.
export const BRANCH = "main";

// A custom domain, which the sync writes to public/CNAME, or null for a
// Pages address. The domain's DNS stays the repository's own business.
export const CUSTOM_DOMAIN = null;

// The logo, as paths from the repository root: a light version, a dark one
// (the light one again when left out) and a favicon (the light logo when it
// is an SVG, else the site's own ladder mark). "auto" takes the Knowledge
// Trust Ladder logo: a knowledge-trust-ladder-logo.svg the repository
// already has, or else the copy in src/assets/. A single path is the light
// version alone. null shows the title as text.
export const LOGO = {
  light: ".assets/knowledge-trust-ladder-logo.svg",
  dark: ".assets/knowledge-trust-ladder-logo-dark.svg",
};

// The folder of figures the README and the docs pages show, served under
// /assets/. "auto" takes .assets/ when there is one.
export const ASSETS = ".assets";

// The docs pages: a folder, and the sidebar groups its pages sit in, each
// page named by its path under the folder without .md. With no groups, every
// page sits in one Guides group, by title. With groups, the sync stops with
// an error when a group names a missing page or a page has no group, so a new
// page cannot go missing from the sidebar. "auto" takes docs/ when there is
// one; null shows no docs pages.
export const DOCS = {
  dir: "docs",
  groups: [
    { label: "Guides", pages: ["install", "obsidian", "m365", "ingest", "skills-repositories"] },
    {
      label: "Architecture",
      pages: [
        "architecture",
        "for-the-curious",
        "context-layer",
        "federation",
        "context-layer-technology",
        "three-lines",
        "three-lines-critics",
      ],
    },
    { label: "Maintaining", pages: ["releasing", "signing-commits", "threat-model", "repository-layout"] },
    { label: "Captured sessions", pages: ["examples/docent", "examples/curator", "examples/prose"] },
  ],
};

// A Keep a Changelog file, read as a page per release. "auto" takes
// CHANGELOG.md when it holds a released version.
export const CHANGELOG = "CHANGELOG.md";

// The tag a release carries, with {version} for its number. A release page
// links the repository, the docs and the bundle at that tag, and the release
// itself, when git has the tag. null links nothing.
export const RELEASE_TAG = "v{version}";

// Pages from files outside the docs folder, each at /<slug>/, listed in the
// Guide sidebar after Home under its label. An entry's `retells` names the
// file whose page it retells, and `level` the words for its reading level:
// both pages then offer each other under their titles.
export const PAGES = [
  {
    slug: "simple",
    source: "docs/architecture.en-simple.md",
    label: "For readers aged 13 to 18",
    retells: "docs/architecture.md",
    level: "Ages 13 to 18",
  },
];

// The LinkML schema's pages, which gen-doc writes, under a Schema topic: a
// folder, and the command that writes it, which the sync runs when the
// folder is missing. This repository has no LinkML schema of its own.
export const SCHEMA = null;

// The data: a folder of SQLite databases and their Datasette metadata, served
// under /browse/ with a page that opens each in Datasette Lite. This
// repository has no data to browse.
export const BROWSE = null;

// The home page: its source, from the file's `# ` title down ("auto" takes
// the README when it has one, else the bundle's own introduction); the
// tagline under the title (a string, { boldLineOf: <file> } for the first
// line of that file that is bold throughout, or DESCRIPTION when null); and
// the buttons, with site-relative links (Browse the bundle, Architecture when
// the docs have an architecture page, Bundle health and Knowledge graph when
// null).
export const HOME = {
  source: "README.md",
  tagline: { boldLineOf: "docs/architecture.md" },
  actions: [
    { text: "Browse the bundle", link: "/knowledge/", icon: "right-arrow" },
    { text: "Architecture", link: "/docs/architecture/", variant: "secondary" },
    { text: "Glossary", link: "/knowledge/glossary/", variant: "secondary" },
    { text: "Quick start", link: "/docs/install/#quick-start", variant: "secondary" },
  ],
};
