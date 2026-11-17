# Repository layout

This page is for contributors looking for a file in the repository. [The architecture](architecture.md) says what each skill is for.

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
.release/
  package.json, package-lock.json  the release tools semantic-release.yml installs with npm ci, every package pinned
.pypi/
  requirements.in, requirements.txt  the build backend of the PyPI packages; pypi.yml and the tests build with --require-hashes
.github/repository-settings.json  what this repository's own workflows need from GitHub, and the hardening it keeps; `ktl gh` reads it beside the skills' catalogues
.github/docent-eval/
  package.json, package-lock.json  Claude Code, which docent-eval.yml installs with npm ci, pinned by hash
.github/workflows/
  validate.yml               repository contract, Agent Skills spec, Markdown and links (every PR)
  knowledge-registrar.yaml   the sidecar's schema and provenance gate (PRs touching the bundle)
  knowledge-librarian.yaml   the sidecar's scheduled librarian refresh
  knowledge-release.yaml     the sidecar's release step: bundle and Copilot zips (from publish.yml)
  semantic-release.yml       version and changelog from Conventional Commits on main; never tags
  publish.yml                maintainer-gated release (workflow_dispatch only)
  pypi.yml                   builds ktl and its alias from a release tag, uploads them to PyPI and attaches their checksums (from publish.yml)
  knowledge-website.yaml     ktl-website's workflow: builds website/ on each PR, publishes the default branch's build to Pages
  docent-eval.yml            the docent holdout, run through `claude plugin eval` weekly and by hand under a cost cap; never on a pull request
  scorecard.yml              OpenSSF Scorecard on each push to main and weekly: publishes the score the README's badge shows, and adds its findings to code scanning
  codeql.yml                 CodeQL on the Python, the JavaScript and the workflows, on each PR, each push to main and weekly
docs/
  architecture.md       the architecture the poem, LOKF and LinkML inspired: the catalogue, the five roles and the trust ladder
  architecture.en-simple.md  the architecture page retold for readers aged 13 to 18
  first-bundle.md       a first run: from no bundle to a confirmed concept and an answer
  install.md            the quick start, every way to install the six skills, and pinning to one release
  cast/                 a page for each role and each optional skill: what it does, how to ask it, what checks it
  how-it-works.md       the architecture's mechanics: who writes the bundle, four levels of checking, domain vocabularies
  context-layer.md      the context layer: what it is, one bundle as one, and why bundles federate
  federation.md         a federation of bundles: domains, tiers, the workspace and the decisions
  context-layer-technology.md  the products a workspace can use: artifact repositories, stores, catalogues, agents
  obsidian.md           the bundle as a vault of its own, and the two plugins
  m365.md               read-only roles as Microsoft 365 Copilot skills, the docent first
  ingest.md             how to mirror knowledge from outside the repository, and review the ingest pull request
  ingest-reference.md   the ingest's sources, manifest, mirror and lock, and how sensitivity bounds them
  uses.md               what KTL is for, what it is not, and how to judge a use this page does not list
  three-lines.md        the roles in the three lines of defence, what an auditor can check, and the critics
  skills-repositories.md  KTL in a repository whose content is Agent Skills, and what remains to do
  young-readers.md      knowledge retold for readers aged 8 to 18: what a retelling is, and who does what
  releasing.md          how the three repositories release, and the settings it needs
  signing-commits.md    signing commits, which the provenance gate reads
  threat-model.md       shared security design: what an agent can reach, and what guards it
  repository-layout.md  this page
  examples/
    first-bundle.md     one captured run of the four roles on a repository that had no bundle
    docent.md           eight captured docent answers against this repository's own bundle
    curator.md          placeholder: the curator sessions still to capture
    prose.md            captured ktl-prose runs that write for younger readers
scripts/
  validate-repository.sh   the contract: the checks validate.yml runs on this repository's own files
  smoke-test-install.sh    installs the six skills into a throwaway repo and checks them
  smoke-test-website.sh    copies the website templates into a host built from the dummy bundle and builds the site twice
  companion-diagrams.mjs   draws the Archify companions in .assets/companions/ again; a maintainer runs it by hand
tests/                     the behavioural tests of the sidecar scripts and the prose checker, run with pytest; -n auto runs them in parallel
  conftest.py              the shared helpers, and how to run the tests
  test_*.py                one module per script: the pen, the gate, the report, the conventions checker,
                           the feedback recorder, the preflight, the prose checker, the layouts the
                           wrapper and the workflows run in, the website skill's preflight and templates,
                           and the ktl package and its two commands
  docent-holdout.yaml      the eight captured docent questions and the concept each answer should rest on, as data; outside .lokf/ so the docent cannot read it
  docent-holdout-schema.yaml  its LinkML shape, importing LOKF's schema for Concept
  test_docent_holdout.py   checks that each expected concept still exists and that evals/ asks the same questions
evals/                     the holdout as `claude plugin eval` cases, one directory per question with its prompt, graders and scaffold; README.md says how to run it
  scaffold-bundle.sh       copies .lokf/knowledge/ alone into a run's empty directory
pyproject.toml             builds the ktl package for PyPI: the skills and .claude-plugin/ verbatim, and the command in src/ktl/
src/ktl/                   the `ktl` command, standard library only: `ktl skills list|path|install|status`, `ktl gh` for a repository's GitHub settings, and the package's PyPI page
alias/                     the knowledge-trust-ladder package: no code, it installs ktl at the same version under the repository's name
justfile                   `just docent-eval` runs that suite under a cost cap, `just docent-holdout` its test; the sidecar's recipes stay in .lokf/justfile
website/                   the website: Hugo, this repository's copy of ktl-website's templates
  site.toml                this repository's values: address, title, repository, docs groups, redirects
  hugo.toml                what every site shares: the mounts that find each input, the output formats
  content/*/_content.gotmpl  the adapters that make the home page and a page per docs file, concept, release and schema element
  scripts/build.sh         prepare, Hugo, the raw-HTML cleaning, Pagefind and the link check; `serve` and `preview` for a local look
  scripts/prepare.sh       `lokf export`, the trust labels, gen-doc for a LinkML schema and the data site.toml names, into generated/
  scripts/clean-html.py    cleans each page's raw HTML to the tags GitHub allows
  scripts/check-svg.py     stops the build on an SVG that could run a script
  scripts/site-values.py   reads site.toml through a TOML parser for prepare.sh
  scripts/check-links.py   fails the build on a link between two pages that does not resolve
.lokf/                  this repository's own sidecar: the bundle and its tooling
knowledge_bundle        -> .lokf/knowledge, the doorway link ktl-sidecar creates (Step 2)
```

Each `SKILL.md` is a short router. Anything not needed on every invocation is in that skill's `references/`, loaded only when the router points to it, so the cost of a trigger stays small. Contract check 10a holds each `SKILL.md` to a word budget.

`ktl-sidecar/templates/` and `ktl-website/templates/` hold the files each installs, copied verbatim, never retyped. `ktl-prose/scripts/` and `ktl-website/scripts/` hold the one script each runs in place. `ktl-docent/scripts/` holds the docent's own copies of `knowledge-report.sh` and `knowledge-feedback.sh`. Contract check 11a keeps them identical to the sidecar's templates, so a question to the docent runs no script the host repository supplies.
