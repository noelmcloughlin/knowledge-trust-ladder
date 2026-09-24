# Repository layout

[The README](../README.md) says what the skills are for. This is the tree behind it.

```text
skills/
  ktl-sidecar/         SKILL.md + references/ + templates/  (~4.5k tokens loaded on trigger)
  ktl-librarian/       SKILL.md + references/               (~7.5k tokens loaded on trigger)
  ktl-curator/         SKILL.md + references/               (~3k tokens loaded on trigger)
  ktl-docent/          SKILL.md + references/               (~1.5k tokens loaded on trigger)
.claude-plugin/
  plugin.json           the four skills as one Claude Code plugin, with catalog keywords
  marketplace.json      lets `/plugin marketplace add` find that plugin
.github/workflows/
  validate.yml               repository contract, Agent Skills spec, Markdown and links (every PR)
  knowledge-registrar.yaml   the sidecar's schema and provenance gate (PRs touching the bundle)
  knowledge-librarian.yaml   the sidecar's scheduled librarian refresh
  knowledge-release.yaml     the sidecar's release step: bundle and Copilot zips (from publish.yml)
  semantic-release.yml       version and changelog from Conventional Commits on main; never tags
  publish.yml                maintainer-gated release (workflow_dispatch only)
docs/
  for-the-curious.md    the README's mechanics: four levels of checking, domain schemas
  obsidian.md           the bundle as a vault of its own, and the two plugins
  m365.md               read-only roles as Microsoft 365 Copilot skills, the docent first
  three-lines.md        the roles in the three lines of defence, and what an auditor can check
  three-lines-critics.md  the model's critics, quoted, and what a bundle answers
  releasing.md          how the three repositories release, and the settings it needs
  signing-commits.md    signing commits, which the provenance gate reads
  threat-model.md       shared security design: what an agent can reach, and what holds it
  repository-layout.md  this page
  examples/
    docent.md           eight captured docent answers against this repository's own bundle
    curator.md          placeholder: the curator sessions still to capture
scripts/
  validate-repository.sh   the checks validate.yml runs
  smoke-test-install.sh    installs the four skills into a throwaway repo and checks them
  test-sidecar-layouts.sh  the wrapper, workflows and lokf-link, with and without the doorway
  sync-sidecar.sh          copies one release's templates and skills pin into a sibling repository
.lokf/                  this repository's own sidecar: the bundle and its tooling
knowledge_bundle        -> .lokf/knowledge, the doorway link ktl-sidecar lays down (Step 2)
```

Each `SKILL.md` is a lean router. Anything not needed on every invocation lives in that skill's `references/`, loaded only when the router points to it, so the cost of a trigger stays small. `ktl-sidecar/templates/` holds the files it lays down, copied verbatim, never retyped.
