# Repository layout

[The architecture](architecture.md) says what each skill is for. This is the tree behind it.

```text
skills/
  ktl-sidecar/         SKILL.md + references/ + templates/
  ktl-librarian/       SKILL.md + references/
  ktl-curator/         SKILL.md + references/
  ktl-docent/          SKILL.md + references/ + scripts/
  ktl-prose/           SKILL.md + references/ + scripts/
  ktl-website/         SKILL.md + references/ + scripts/ + templates/
.assets/
  *.svg, *-dark.svg     the logo, the social card and each figure the docs show, light and dark
  companions/           Archify flow diagrams beside some figures: each candidate and its two SVGs
.claude-plugin/
  plugin.json           the six skills as one Claude Code plugin, with catalogue keywords
  marketplace.json      lets `/plugin marketplace add` find that plugin
.github/workflows/
  validate.yml               repository contract, Agent Skills spec, Markdown and links (every PR)
  knowledge-registrar.yaml   the sidecar's schema and provenance gate (PRs touching the bundle)
  knowledge-librarian.yaml   the sidecar's scheduled librarian refresh
  knowledge-release.yaml     the sidecar's release step: bundle and Copilot zips (from publish.yml)
  semantic-release.yml       version and changelog from Conventional Commits on main; never tags
  publish.yml                maintainer-gated release (workflow_dispatch only)
  knowledge-website.yaml     ktl-website's workflow: builds website/ on each PR, publishes the default branch's build to Pages
docs/
  architecture.md       the architecture the poem, LOKF and LinkML inspired: the catalogue, the five roles and the trust ladder
  architecture.en-simple.md  the architecture page retold for readers aged 13 to 18
  install.md            the quick start, every way to install the six skills, and pinning to one release
  for-the-curious.md    the architecture's mechanics: four levels of checking, domain schemas
  context-layer.md      the context layer: what it is, one bundle as one, and why bundles federate
  federation.md         a federation of bundles: domains, tiers, the workspace and the decisions
  context-layer-technology.md  the products a workspace can use: artifact repositories, stores, catalogues, agents
  obsidian.md           the bundle as a vault of its own, and the two plugins
  m365.md               read-only roles as Microsoft 365 Copilot skills, the docent first
  ingest.md             knowledge outside the repository: the manifest, the mirror and the ingest pull request
  three-lines.md        the roles in the three lines of defence, and what an auditor can check
  three-lines-critics.md  the model's critics, quoted, and what a bundle answers
  skills-repositories.md  KTL in a repository whose content is Agent Skills, and what remains to do
  releasing.md          how the three repositories release, and the settings it needs
  signing-commits.md    signing commits, which the provenance gate reads
  threat-model.md       shared security design: what an agent can reach, and what guards it
  repository-layout.md  this page
  examples/
    docent.md           eight captured docent answers against this repository's own bundle
    curator.md          placeholder: the curator sessions still to capture
    prose.md            captured ktl-prose runs that write for younger readers
scripts/
  validate-repository.sh   the contract: the checks validate.yml runs on this repository's own files
  smoke-test-install.sh    installs the six skills into a throwaway repo and checks them
  smoke-test-website.sh    lays the website templates down on a dummy bundle and builds the site twice
  sync-sidecar.sh          runs one release's knowledge-sync.sh in each sibling repository, and finishes the branches
  companion-diagrams.mjs   draws the Archify companions in .assets/companions/ again; a maintainer runs it by hand
tests/                     the behavioural tests of the sidecar scripts and the prose checker, run with pytest; -n auto runs them in parallel
  conftest.py              the shared helpers, and how to run the tests
  test_*.py                one module per script: the pen, the gate, the report, the conventions checker,
                           the feedback recorder, the preflight, the prose checker, the layouts the
                           wrapper and the workflows run in, and the website skill's preflight and templates
website/                   the website: Astro Starlight, this repository's copy of ktl-website's templates
  site.config.mjs          the site's values and options: addresses, title, logo, docs groups, extra pages
  scripts/config.mjs       settles those options against the repository; `node scripts/config.mjs` prints them
  scripts/sync.mjs         writes the pages and the bundle's exported files before each build
  scripts/check-links.mjs  fails the build on a link between two pages that does not resolve
.lokf/                  this repository's own sidecar: the bundle and its tooling
knowledge_bundle        -> .lokf/knowledge, the doorway link ktl-sidecar creates (Step 2)
```

Each `SKILL.md` is a lean router. Anything not needed on every invocation lives in that skill's `references/`, loaded only when the router points to it, so the cost of a trigger stays small. Contract check 10a holds each `SKILL.md` to a word budget. `ktl-sidecar/templates/` and `ktl-website/templates/` hold the files each installs, copied verbatim, never retyped. `ktl-prose/scripts/` and `ktl-website/scripts/` hold the one script each runs in place.
