# Extending the vocabulary: a domain schema the validator checks

This page is for the **librarian**: it answers how to give a host's domain a schema that `lokf validate` checks.

LOKF's core vocabulary is small: its classes and its typed relations. Rule 7 keeps every consumer tolerant of what falls outside them. Some domains need more: a degree programme's `Module`, a clinic's `Protocol`, an `ects` or `dosage` key. A bundle in such a domain does not loosen anything. It gives the domain a schema of its own, written in the same [LinkML](https://linkml.io) as LOKF's and importing LOKF's. It then validates against both with the flag the toolkit already has: `lokf validate --schema <file>`. The **curator**'s [domain-schemas.md](../../ktl-curator/references/domain-schemas.md) covers when to do this and what it costs (nothing new to install). This page is the recipe.

## What the validator expects

`lokf validate` checks a bundle against the classes and slots a schema declares, and nothing else. Two consequences shape the recipe:

- **Every class is closed.** A concept fails its class on any key the class does not declare, so a built-in class plus one key of your own is not valid. Subclass it and declare the key.
- **`type` names the class exactly.** Each class's schema pins `type` to its own name, and the bundle's concepts are matched against all classes at once. A record of a subclass writes the subclass name, not the parent's.

A concept outside the declared vocabulary reports as `is not valid under any of the given schemas`. That line is the signal you have reached this page, not an error to route around.

## The recipe

1. **A pinned copy of the core schema beside it.** LinkML resolves `imports:` relative to the importing file, so `.lokf/lokf.yaml` must exist, at the version the sidecar's `pyproject.toml` floors. Copy it out of the installed package:

   ```bash
   cd .lokf && uv run python -c "from importlib.resources import files; print(files('lokf') / 'data' / 'lokf.yaml')" | xargs -I{} cp {} lokf.yaml
   ```

   The copy does double duty. `convert`, `serve` and `query` take no `--schema` flag and resolve `lokf.yaml` from the current directory and its ancestors before the packaged copy. From `.lokf/`, this is therefore also the schema they read.

2. **The domain schema**, `.lokf/<slug>.yaml`, with its namespace under the same authority as `base_iri` (Rule 2). A learning-programme bundle, for instance:

   ```yaml
   id: https://<project namespace>/schema/<slug>
   name: <slug>
   imports:
     - linkml:types
     - lokf                      # ./lokf.yaml, the pinned copy
   default_range: string
   default_prefix: <slug>
   prefixes:
     <slug>: https://<project namespace>/schema/<slug>/
     linkml: https://w3id.org/linkml/
     lokf: https://w3id.org/lokf/
   classes:
     Module:                     # a concept LOKF has no class for
       is_a: Concept
       slots: [module_code, ects, semester]
     SourceSnapshotReference:    # a built-in that fits, plus keys it lacks
       is_a: Reference
       slots: [source_kind, reviewed_at]
   slots:
     module_code: {range: string}
     ects: {range: integer}
     semester: {range: integer}
     source_kind: {range: string}
     reviewed_at: {range: date}
   ```

   A class `is_a: Concept` joins the bundle's concept union automatically, and so does any descendant of it: the core classes become the core plus yours. Subclass a built-in whose meaning fits. Give a class of its own to what no built-in describes (a delivery pattern is not a `Policy`, however tempting the stretch). Never leave extra keys on a built-in unchanged.

   A published vocabulary the domain schema needs does not go into `imports:` as it is. LinkML merges every imported name into one namespace without a warning, so the vocabulary's own `id`, `type` or `name` would merge with LOKF's. The `adapt` command, in lokf's main branch and not yet in 0.8.0, writes a copy that can sit beside `lokf.yaml`. It replaces the vocabulary's identifier and type slots with LOKF's, renames every other shared name while keeping its IRI, and re-roots the vocabulary's top classes on `Concept` ([adapt](https://lokf.nolan-nichols.com/toolkit/adapt/)).

3. **Frontmatter names the class exactly.** A record with `type: Reference` and a `source_kind` key fails: `Reference` does not declare the key, and `SourceSnapshotReference` requires its own name. Write the subclass name. `is_a` still makes it `rdfs:subClassOf` its parent in the projected graph.

4. **Name the schema.** In the sidecar's `justfile`, set the one variable: `schema := "<slug>.yaml"`. The `lokf-validate` and `lokf-check-refs` recipes pass it as `--schema`, running from the schema's directory so a relative import in it resolves, and the three workflows (`knowledge-registrar.yaml`, `knowledge-librarian.yaml`, `knowledge-release.yaml`) run the recipes, so nothing else in the sidecar changes. A sidecar scaffolded before the variable existed runs `lokf validate` inline in its justfile and its workflows; ktl-sidecar's repair lays down the current copies of those four files. That one variable is also how the **librarian** learns the host's vocabulary. Rule 3 has it read the schema the justfile names and treat every `Concept` descendant there as a class it may choose. `lokf vocab` lists relations only and takes no `--schema`, so the file itself is the source.

   The schema need not sit beside the bundle. The variable takes any path relative to `.lokf/`, and the schema's own `imports:` entry names `lokf.yaml` relative to the schema file. Three layouts recur:

   - **A linkml-sidecar.** A host that wants the full LinkML toolchain for the schema (lint, generators, docs, tests, `copier update`) installs the [linkml-sidecar](https://github.com/noelmcloughlin/linkml-sidecar#install) skill. It writes the schema as `.linkml/src/<slug>/schema/<slug>.yaml`, imports `.lokf/lokf.yaml` from there, and sets `schema := "../.linkml/src/<slug>/schema/<slug>.yaml"` itself.
   - **A schema project at the root.** A repository that is itself a LinkML schema project, made with copier at its root, sets `schema := "../src/<slug>/schema/<slug>.yaml"`.
   - **A schema anywhere else.** A schema the repository keeps elsewhere sets the path to that file.

   In the last two layouts, a `.lokf/` beside the schema is a bundle *about* the repository until its maintainers add the import and this variable. The bundle's presence alone connects nothing.

   linkml-sidecar's [ktl.md](https://github.com/noelmcloughlin/linkml-sidecar/blob/main/skills/linkml-sidecar/references/ktl.md) and its linkml-author skill cover the authoring side. Every class the bundle may use is `is_a: Concept`, the linter is told to excuse LOKF's camelCase slot names, and a valid example is kept where the example runner does not compile LOKF's `from` slot.

5. **Tell both plugins.** KTL Registrar and KTL Curator each have a *Known LOKF types* setting listing the built-in classes. Add your classes to both, the same list in each. Neither plugin can read the schema itself: the exhibition vault's root is `.lokf/knowledge`, and the schema sits outside it. Listed, a domain class stops opening with the **registrar**'s unknown-type warning and joins its autocomplete. It stops counting against the **curator**'s *vocabulary fit* line, and can carry a review interval of its own in `policies/knowledge-curation.md`. A list you have edited is yours to keep current when the core schema gains a class. Before KTL Curator gained the setting, its vocabulary-fit line counted against the built-ins only. Read that line on an older build as "concepts outside LOKF core", not as errors. The *skills* need no telling: the **curator** reads the same `schema` line Rule 3 does ([ktl-curator/references/trust-fields.md](../../ktl-curator/references/trust-fields.md)).

## What a domain schema does not do

- **The graph.** The core JSON-LD context declares `@vocab: https://w3id.org/lokf/`. So `convert`, `serve` and `query` already project undeclared keys, as `lokf:ects`, in LOKF's namespace rather than yours. Up to lokf 0.8.0 they project undeclared types the same way (`a lokf:Module`). From lokf 0.9.0 an undeclared type projects as `a lokf:Concept` with the name kept in `schema:additionalType "Module"`, so filter on that literal rather than on a generated class such as `lokf:Module`.

  A domain schema does not change that: the three commands take no `--schema` or `--context`. A raw `gen-jsonld-context <slug>.yaml` output cannot simply replace the packaged context beside the bundle, because it lacks the packaged aliases `type` → `@type` and `id` → `@id`. In a test, every node became a blank node carrying a literal `lokf:type`. Read `lokf:<key>` in a query result as "declared to the validator, not yet to the graph". A domain context that keeps the core aliases and maps your terms to your prefix is a toolkit feature that does not exist yet.
- **Keeping the copy current.** Section 1's tooling-version step gains one line on such a host. When the `lokf` floor moves, refresh the pinned `lokf.yaml` to the new version in the same change and re-run `just lokf-validate`. A copy older than the toolkit validates against classes and slots the toolkit no longer means.
- **A domain bundle.** A bundle whose concepts are other bundles has a ready-made schema, `templates/domain.yaml` in ktl-sidecar, and its own page: the **curator**'s [domain-bundle.md](../../ktl-curator/references/domain-bundle.md).
- **Deciding whether to do it.** That is the **curator**'s conversation and the team's call: [ktl-curator/references/domain-schemas.md](../../ktl-curator/references/domain-schemas.md). Until a schema exists, a concept with a type or key of its own is still knowledge under Rule 7. It is also still outside what `lokf validate` checks, so the **registrar** gate stays red. The **librarian**'s choices are to fit the concept onto a built-in class with no extra keys, or to write the schema, never to loosen the validator.
