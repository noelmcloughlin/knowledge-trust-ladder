---
type: Explanation
id: https://w3id.org/ktl/knowledge/explanation/domain-schemas
title: "When the built-in vocabulary stops fitting: domain schemas"
description: "How a bundle in a specialised or regulated domain goes beyond LOKF's core classes: the signs a domain schema is due, a LinkML schema importing LOKF's, named by one `schema` variable in the sidecar's justfile and checked with `lokf validate --schema`, the three layouts that variable allows, the `domain.yaml` the sidecar ships for a bundle that federates other bundles, reusing a domain's own vocabulary such as the AI Risk Ontology through `lokf adapt`, the Microsoft 365 identity shape held in reserve, and who raises, decides and applies it."
genre: explanation
resource: skills/ktl-curator/references/domain-schemas.md
sources:
  - resource: skills/ktl-curator/references/domain-schemas.md
  - resource: skills/ktl-librarian/references/domain-schema.md
  - resource: skills/ktl-sidecar/templates/justfile
  - resource: docs/architecture.md
generated:
  by: process:ktl-librarian
  at: "2026-10-29T00:48:33Z"
about: []
references:
  - https://w3id.org/ktl/knowledge/playbooks/ktl-librarian-skill
  - https://w3id.org/ktl/knowledge/references/linkml
  - https://w3id.org/ktl/knowledge/references/lokf-toolkit
relatedTo:
  - https://w3id.org/ktl/knowledge/explanation/three-lines-of-defence
  - https://w3id.org/ktl/knowledge/playbooks/docent-in-m365-copilot
  - https://w3id.org/ktl/knowledge/playbooks/ktl-curator-skill
verified:
  - by: process:ktl-librarian
    at: "2026-10-20T23:23:33Z"
  - by: human:noelmcloughlin
    at: "2026-10-13T01:19:37Z"
status: draft
---

# Overview

LOKF has a small vocabulary: a short list of classes, the typed relations and a handful of trust fields, which keeps bundles portable. `docs/architecture.md` says that LOKF supplies "a fixed taxonomy of concept types", which OKF leaves to the producer. It also says that a domain whose concepts stop fitting it extends the schema, so its own types are checked rather than tolerated.

**The signs.** A domain schema is due when any of these holds:

- The curator's *vocabulary fit* line keeps growing. It counts concepts whose `type` is outside the known classes, tolerated under Golden Rule 7 but carrying no agreed meaning.
- Concepts gain many producer-defined keys, such as `dosage`, `jurisdiction` or `failure_mode`, that no validator checks.
- The domain is one where a wrong or ambiguous field has consequences: medicine, law, finance, safety engineering, anything regulated.

**The mechanism.** Keep the OKF/LOKF mechanics and give the domain a LinkML schema of its own that imports LOKF's, validated with `lokf validate --schema <slug>.yaml`. Every class is closed, so a built-in class plus an extra key fails. Subclass it (`is_a: Reference`) or add a class of its own (`is_a: Concept`), and have frontmatter name the subclass exactly.

The recipe keeps a pinned copy of `lokf.yaml` in `.lokf/` and names the domain schema in one variable, `schema`, in the sidecar's justfile. The `lokf-validate`, `lokf-check-refs`, `lokf-convert` and `lokf-serve` recipes pass it as `--schema`, and the registrar, librarian and release workflows run those recipes, so nothing else in the sidecar changes. The schema need not sit beside the bundle. The variable takes any path relative to `.lokf/`, and three layouts recur: a linkml-sidecar, which writes the schema under `.linkml/` and sets the variable itself; a schema project made with copier at the repository's root; and a schema the repository keeps anywhere else. In the last two, a `.lokf/` beside the schema is a bundle about the repository until its maintainers add the import and the variable. The two Obsidian plugins are told the new classes through their *Known LOKF types* setting. Neither plugin can read the schema itself, so the same list of classes goes into both. When the `lokf` floor moves, the pinned `lokf.yaml` is refreshed to the new version in the same change and `just lokf-validate` is run again.

The sidecar already depends on `lokf[build]`, so the LinkML generators are installed and a domain schema costs one file, with nothing new to install. A domain schema that grows past a few classes is worth a project of its own, with lint, tests and a docs site, which the linkml-sidecar skills install beside the bundle or around a schema the repository already holds; their linkml-author skill knows what `lokf validate` expects of a domain schema. From lokf 0.9.0, `convert`, `query`, `serve` and `export` take `--schema` as `validate` does, so the graph names each class and slot the schema declares under its own IRI. A key no schema declares still projects in LOKF's namespace, and an undeclared type projects as `lokf:Concept` with the name kept in `schema:additionalType`.

One domain schema ships with the sidecar: `domain.yaml`, in ktl-sidecar's templates, for a bundle whose concepts are other bundles. The curator's `domain-bundle.md` is its page, and ktl-librarian's `references/domain-schema.md` points a domain bundle at both.

**When the domain already has a vocabulary**, reuse it rather than re-describe it. For AI governance, the curator's guidance names IBM AI Atlas Nexus's [AI Risk Ontology](https://ibm.github.io/ai-atlas-nexus/ontology/), a LinkML vocabulary covering risks, controls, obligations, taxonomies, incidents and evaluations. It also names [ai-linkmo](https://github.com/noelmcloughlin/ai-linkmo) as a reference implementation over it, with a LOKF sidecar beside it.

A domain schema can bring that vocabulary in beside LOKF's, so a concept names a control or an obligation by the identifier the domain already uses. A published vocabulary does not go into `imports:` as it is, because LinkML merges every imported name into one namespace without a warning, so the vocabulary's own `id`, `type` or `name` would merge with LOKF's. The `adapt` command, from lokf 0.9.0, writes a copy that sits beside `lokf.yaml`: it replaces the vocabulary's identifier and type slots with LOKF's, renames every other shared name while keeping its IRI, and re-roots the vocabulary's top classes on `Concept`. A host may import more than one such copy through a composite schema, which the `schema :=` line names and the release attaches as one file with the copies merged in. Such a vocabulary usually lacks the bundle's half: who encoded a record, from which edition, who confirmed it, and when to look again. Whether those fields belong on the domain's own records is left to the domain's owners and to OKF as it evolves.

**A shape held in reserve: Microsoft 365 provenance.** A host whose curators work in Microsoft 365 Copilot rather than a forge has no `gh` login and no signed commit to back a `human:` verdict. Nothing writes such a verdict yet, because a Copilot curator needs a write action that does not exist. Nothing checks one either, because the gate reads `human:` only. So no schema is built. The curator's guidance records the shape it would take, so the decision is not made twice:

- a subclass of the verification event carrying the Entra `tenant_id` and `object_id`;
- an `assurance` level (`attested`, `delegated-me`, `directory-lookup`, `platform-history`, `unverified`, `anonymous`);
- a revision as the item's `etag` plus a content digest;
- `by:` under a scheme of its own, `entra:<tenant>/<object>`, so no reader mistakes it for a forge login.

The shape waits for the curator's write path.

Where a domain schema binds a slot to an external code list (SNOMED CT, for example), neither LOKF's schema nor `lokf validate` checks that the term still exists. `linkml-term-validator` can, as an optional extra gate whose "service unreachable" counts as not passing.

**Roles stay as they are.** The curator raises the question, as a report line and a conversation. The team decides whether a domain schema, a small piece of governed software, is worth owning. The librarian applies it. Until then a misfit concept is still knowledge, just not yet checkable knowledge, since the spec says consumers MUST NOT reject unknown types. It is also still outside what `lokf validate` checks, so the registrar gate stays red.
