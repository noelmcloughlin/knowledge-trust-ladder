# Repository layout

[The README](../README.md) says what the skills are for. This is the tree behind it.

```text
skills/
  ktl-sidecar/         SKILL.md + references/ + templates/  (~4.5k tokens loaded on trigger)
  ktl-librarian/       SKILL.md + references/               (~7.5k tokens loaded on trigger)
  ktl-curator/         SKILL.md + references/               (~3k tokens loaded on trigger)
  ktl-docent/          SKILL.md + references/               (~1.5k tokens loaded on trigger)
.claude-plugin/
  plugin.json           the four skills as one Claude Code plugin, with the keywords a plugin catalog searches
  marketplace.json      lets `/plugin marketplace add` find that plugin in this repository
.github/workflows/
  validate.yml               repository contract + Agent Skills spec + Markdown/link checks (every PR)
  knowledge-registrar.yaml   this repository's copy of the gate the sidecar ships: schema-valid and provenance (every PR that touches the bundle)
  knowledge-librarian.yaml   this repository's copy of the scheduled librarian refresh
  semantic-release.yml       version and changelog from Conventional Commits on main; never tags
  publish.yml                maintainer-gated release (workflow_dispatch only)
docs/
  for-the-curious.md    the mechanics behind the README: four levels of checking, domain schemas
  obsidian.md           the bundle as a vault of its own, and the two plugins
  three-lines.md        the roles placed in the three lines of defence, what an auditor can check, and what remains to do and who does it
  three-lines-critics.md  what the model's critics say, quoted from their own texts, and what a bundle answers and leaves open
  releasing.md          how the three repositories release, and the repository settings it depends on
  signing-commits.md    signing commits, which the provenance gate reads
  threat-model.md       the three repositories' shared security design: what an agent can reach, what holds it, and what a human: confirmation proves
  repository-layout.md  this page
  examples/
    docent.md           eight captured docent answers against this repository's own bundle
    curator.md          placeholder: the curator sessions still to capture
scripts/
  validate-repository.sh   the checks validate.yml runs
  smoke-test-install.sh    installs all four skills into a throwaway consumer repo and asserts the result
  test-sidecar-layouts.sh  the wrapper, both workflows and the lokf-link recipe, with and without the doorway link
.lokf/                  this repository's own sidecar: the bundle the docent answers from, and its tooling
knowledge_bundle        -> .lokf/knowledge, the doorway link ktl-sidecar lays down (Step 2)
```

Each `SKILL.md` is a lean router; anything not needed on every invocation lives in that skill's `references/` (loaded only when the router points to it) so the cost of a trigger stays small. `ktl-sidecar/templates/` holds the actual files it lays down - copied verbatim, never retyped.
