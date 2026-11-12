# Extending the vocabulary: a domain vocabulary the validator checks

This page is for the **librarian**: it answers how to give a host's bundle a domain vocabulary that `lokf validate` checks.

LOKF's core vocabulary is small: its classes and its typed relations. Rule 7 keeps every consumer tolerant of what falls outside them. Some domains need more: a degree programme's `Module`, a clinic's `Protocol`, an `ects` or `dosage` key. A bundle in such a domain does not loosen anything. It declares a *domain vocabulary*: a file in `.lokf/schema/`, written in the same [LinkML](https://linkml.io) as LOKF's schema and importing it, that names the extra classes and keys. It then validates against both with the flag the toolkit already has: `lokf validate --schema <file>`. The **curator**'s [domain-schemas.md](../../ktl-curator/references/domain-schemas.md) covers when to do this and what it costs (nothing new to install). This page is the recipe.

## Domain schema, domain vocabulary

A *domain schema* is a LinkML schema that models a domain, and a LinkML project owns it. A *domain vocabulary* is the bundle's: the classes and keys its concepts may use beyond LOKF's own.

| | Domain schema | Domain vocabulary |
| --- | --- | --- |
| Says | what a domain's data looks like | what a bundle's concepts may be called and carry |
| Owner | a LinkML project, in this repository or another | the bundle |
| Folder | `src/<slug>/schema/`, or `.linkml/src/<slug>/schema/` | `.lokf/schema/` |
| Imports `lokf` | never | always |
| Written by | its authors | `lokf adapt`, from a domain schema, or the librarian, for the bundle alone |

`lokf adapt` reads a domain schema and writes a domain vocabulary. No step writes a schema from the bundle, so never add a `lokf` import to a file outside `.lokf/schema/`.

A domain vocabulary is itself a LinkML file, so its folder is `schema/` and its flag is `--schema`. LOKF's specification and the toolkit's messages call it a *LOKF domain schema*.

## What the validator expects

`lokf validate` checks a bundle against the classes and slots a schema declares, and nothing else. Three consequences shape the recipe:

- **Every class is closed.** A concept fails its class on any key the class does not declare, so a built-in class plus one key of your own is not valid. Subclass it and declare the key.
- **`type` names the class exactly.** Each class's schema pins `type` to its own name, and the bundle's concepts are matched against all classes at once. A record of a subclass writes the subclass name, not the parent's.
- **A slot that holds a concept holds its whole IRI.** `knowledge-report.sh` reads one as a relation with no schema to hand, and it cannot tell a prefixed name or a relative path from a plain value.

A concept outside the declared vocabulary reports as `is not valid under any of the given schemas`. That line is the signal you have reached this page, not an error to route around.

## The recipe

1. **A pinned copy of the core schema in `.lokf/schema/`.** Every file of the vocabulary goes in that folder: this copy, the domain vocabulary and each file it imports. LinkML resolves `imports:` relative to the importing file, so `.lokf/schema/lokf.yaml` must exist, and it must come from the lokf release that `.lokf/uv.lock` pins. Copy it out of the installed package:

   ```bash
   cd .lokf && mkdir -p schema && uv run python -c "from importlib.resources import files; print(files('lokf') / 'data' / 'lokf.yaml')" | xargs -I{} cp {} schema/lokf.yaml
   ```

   Copy it again whenever the lock pins another lokf release. A copy from another release can reject what the toolkit reads, and the preflight's `core` line warns when the copy and the lock differ.

2. **The domain vocabulary**, `.lokf/schema/<slug>.yaml`, with its namespace under the same authority as `base_iri` (Rule 2). A learning-programme bundle, for instance:

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

   A published schema the domain vocabulary needs does not go into `imports:` as it is. Import the copy `lokf adapt` makes instead ([Adapting a published schema](#adapting-a-published-schema)).

3. **Frontmatter names the class exactly.** A record with `type: Reference` and a `source_kind` key fails: `Reference` does not declare the key, and `SourceSnapshotReference` requires its own name. Write the subclass name. `is_a` still makes it `rdfs:subClassOf` its parent in the projected graph.

4. **Name the domain vocabulary.** In the sidecar's `justfile`, set the one variable: `schema := "schema/<slug>.yaml"`. The `lokf-validate`, `lokf-check-refs`, `lokf-convert` and `lokf-serve` recipes pass it as `--schema`, and the three workflows (`knowledge-registrar.yaml`, `knowledge-librarian.yaml`, `knowledge-release.yaml`) run the recipes, so nothing else in the sidecar changes. A sidecar scaffolded before the variable existed runs `lokf validate` inline in its justfile and its workflows; ktl-sidecar's repair lays down the current copies of those four files. That one variable is also how the **librarian** learns the host's vocabulary. Rule 3 has it read the file the justfile names, and every file that file imports in turn, and treat each `Concept` descendant there as a class it may choose. `lokf vocab` reads LOKF core alone and takes no `--schema`, so the file itself is the source.

   A `lokf` command given no `--schema` reads `[tool.lokf] schema` in `.lokf/pyproject.toml`, and so does a recipe when the variable is empty. Set it to the same path or leave it out; the preflight warns when the two differ.

   The folder may hold several files, in subfolders too:

   ```text
   .lokf/schema/
   |-- lokf.yaml            # the pinned copy of LOKF core
   |-- <slug>.yaml          # the root: imports lokf and foo
   |-- foo.yaml             # imports bar/bar_module
   |-- bar/bar_module.yaml  # imports ../baz
   |-- baz.yaml
   ```

   The line names the root: the file whose imports reach `lokf` and every other file, directly or in turn. Usually the root alone imports `lokf`, and the other files import each other without a cycle. A copy that `lokf adapt` wrote imports `lokf` too, by that bare name, so it sits beside `lokf.yaml`. LinkML resolves an import from the importing file's folder and adds `.yaml` to the name, so:

   - write each import without the suffix, as `foo` or `bar/bar_module`;
   - give every file that another file imports the `.yaml` ending; the root, which nothing imports, may end in `.yml`;
   - from a subfolder, name a file above it with `../`, as `../baz` or `../lokf`.

   The line names a file in `.lokf/schema/`. A domain schema stays in the LinkML project that owns it, in this repository or another. In this repository it is `.linkml/src/<slug>/schema/<slug>.yaml`, which the [linkml-sidecar](https://github.com/noelmcloughlin/linkml-sidecar#install) skill installs, or `src/<slug>/schema/<slug>.yaml` in a project made with copier at the root. Copy the project's schema into `.lokf/schema/` and adapt the copy with `lokf adapt` ([Adapting a published schema](#adapting-a-published-schema)), or copy a release that is adapted already. The line names the copy, never the project's own file, and the project's file never imports `lokf`. Copy it again when the project's schema changes. linkml-sidecar's [ktl.md](https://github.com/noelmcloughlin/linkml-sidecar/blob/main/skills/linkml-sidecar/references/ktl.md) and its linkml-author skill cover the project's side.

   Until the copy is there and the line names it, a `.lokf/` beside a schema project is a bundle *about* the repository. The bundle's presence alone connects nothing.

5. **Tell both plugins.** KTL Registrar and KTL Curator each have a *Known LOKF types* setting listing the built-in classes. Add your classes to both, the same list in each. Neither plugin can read the schema itself: the exhibition vault's root is `.lokf/knowledge`, and the schema sits outside it. Listed, a domain class stops opening with the **registrar**'s unknown-type warning and joins its autocomplete. It stops counting against the **curator**'s *vocabulary fit* line, and can carry a review interval of its own in `policies/knowledge-curation.md`. A list you have edited is yours to keep current when the core schema gains a class. Before KTL Curator gained the setting, its vocabulary-fit line counted against the built-ins only. Read that line on an older build as "concepts outside LOKF core", not as errors. The *skills* need no telling: the **curator** reads the same `schema` line Rule 3 does ([ktl-curator/references/trust-fields.md](../../ktl-curator/references/trust-fields.md)).

## Moving the schema files into the folder

A sidecar laid out before `.lokf/schema/` existed keeps its schema files at the root of `.lokf/`, where they still work, and the preflight's `schema` line lists them. Move them together, so that each import still resolves beside it:

```bash
cd .lokf && mkdir -p schema && git mv lokf.yaml <slug>.yaml schema/   # and each file <slug>.yaml imports
```

Then set `schema := "schema/<slug>.yaml"` in the justfile, and `[tool.lokf] schema` in `pyproject.toml` to the same path if it is set.

An older linkml-sidecar names its project's own schema on the line, such as `../.linkml/src/<slug>/schema/<slug>.yaml`, and that schema imports `.lokf/lokf.yaml` by its path. Put a copy in `.lokf/schema/` as step 4 says, and point the line and `[tool.lokf] schema` at it. Until then, leave `.lokf/lokf.yaml` where it is.

A domain host moves `domain.yaml` and `lokf.yaml` the same way before its first sync to a release that keeps `domain.yaml` in the folder. Until then, the host's own sync script, which allows only `.lokf/domain.yaml`, refuses that sync.

## Adapting a published schema

A domain vocabulary can take its classes from a published domain schema instead of, or as well as, declaring classes of its own. Import a copy that `lokf adapt` makes, never the schema itself. LinkML merges imported names into one namespace without a warning and keeps the last definition, so a schema's own `id`, `type`, `name` or `Person` would replace LOKF's. `lokf adapt`, from lokf 0.9.0, replaces the schema's identifier and type slots with LOKF's, renames every other shared name while keeping its IRI, and re-roots the schema's top classes on `Concept`, so they become types a concept can name ([adapt](https://lokf.nolan-nichols.com/toolkit/adapt/)):

```bash
cd .lokf/schema && uv run lokf adapt <schema>.yaml --root <TopClass> ...   # writes <schema>_lokf.yaml
```

List `<schema>_lokf` under `imports:` with `lokf`. A schema whose root class carries an identifier, such as biolink-model's `entity`, needs no `--root`: `adapt` finds it. `--root` re-roots a class on `Concept` only, never on a LOKF class such as `Service`. LOKF's [domain schemas guide](https://lokf.nolan-nichols.com/guide/domain-schemas/) walks through biolink-model. Two rules remain:

- **Name the class in frontmatter.** `type: SlsaSourceRepository` projects as `a slsa:SlsaSourceRepository`.
- **List its slots on a class of your own.** Every class is closed, and a schema such as gist attaches few slots to its classes. Declare `GovernedRequirement: {is_a: Requirement, class_uri: gist:Requirement, slots: [is_governed_by]}` and write `type: GovernedRequirement`. A slot ranging over one of the schema's classes takes a concept IRI that `--check-refs` checks. One ranging over `Any` takes an IRI that `--check-refs` leaves alone.

[lmodel/slsa](https://github.com/lmodel/slsa), SLSA v1.2 in LinkML, is the tested case. Each release from v0.7.0 attaches the copy the released `adapt` makes, as `schema-<tag>-slsa.yaml`. Verify it and put it in `.lokf/schema/` beside `lokf.yaml`:

```bash
gh release download <tag> -R lmodel/slsa -p 'schema-<tag>-slsa.yaml*' -D /tmp/slsa
(cd /tmp/slsa && sha256sum -c schema-<tag>-slsa.yaml.sha256)
gh attestation verify /tmp/slsa/schema-<tag>-slsa.yaml -R lmodel/slsa
cp /tmp/slsa/schema-<tag>-slsa.yaml .lokf/schema/slsa.yaml
```

Then set `schema := "schema/slsa.yaml"`, and record the tag in the commit that adds the copy. `uv run lokf convert --schema schema/slsa.yaml knowledge` gives `a slsa:SlsaSourceRepository ; slsa:hosted_by <…>`, and the rest of the bundle projects as before.

A host that needs two published schemas, such as SLSA's and GitHub Actions', keeps one adapt copy of each in `.lokf/schema/` beside `lokf.yaml`. A composite of a few lines imports `lokf` and both copies, declares nothing, and is the file the `schema :=` line names (step 4). LinkML merges the copies into one namespace as it merges any import, so two copies may share a class, slot, enum or type name only where it means the same thing. The release attaches the composite as one file with the copies merged in. It stops on a name that two files define differently, and on a name a copy shares with LOKF core ([automation.md](../../ktl-sidecar/references/automation.md#the-domain-vocabulary-beside-it)).

Which schema to adapt, if any, is the team's call ([ktl-curator/references/domain-schemas.md](../../ktl-curator/references/domain-schemas.md)). LOKF's own classes already map onto schema.org, PROV, DCAT and SKOS.

## What a domain vocabulary does not do

- **The graph, unless the command is given the file.** The core JSON-LD context declares `@vocab: https://w3id.org/lokf/`, so a key no schema declares projects in LOKF's namespace, as `lokf:ects`. Up to lokf 0.8.0 an undeclared type projects the same way (`a lokf:Module`). From lokf 0.9.0 it projects as `a lokf:Concept` with the name kept in `schema:additionalType "Module"`, so filter on that literal rather than on a generated class such as `lokf:Module`.

  From lokf 0.9.0, `convert`, `query`, `serve` and `export` take `--schema` as `validate` does, and project each class and slot the domain vocabulary declares under its own IRI. The `lokf-convert` and `lokf-serve` recipes and the website's export pass it. A bare `lokf query` or `lokf export` takes `--schema schema/<slug>.yaml`, or reads `[tool.lokf] schema`. Without it, read `lokf:<key>` in a query result as "declared to the validator, not yet to the graph".
- **Keeping the copy current.** Section 1's tooling-version step gains one line on such a host. When the floor moves, or the lock otherwise pins another `lokf` release, copy the pinned `lokf.yaml` again from the installed package in the same change, and re-run `just lokf-validate`. A copy older than the toolkit validates against classes and slots the toolkit no longer means.
- **A domain bundle.** A bundle whose concepts are other bundles has a ready-made domain vocabulary, `templates/domain.yaml` in ktl-sidecar, and its own page: the **curator**'s [domain-bundle.md](../../ktl-curator/references/domain-bundle.md).
- **Deciding whether to do it.** That is the **curator**'s conversation and the team's call: [ktl-curator/references/domain-schemas.md](../../ktl-curator/references/domain-schemas.md). Until a domain vocabulary exists, a concept with a type or key of its own is still knowledge under Rule 7. It is also still outside what `lokf validate` checks, so the **registrar** gate stays red. The **librarian**'s choices are to fit the concept onto a built-in class with no extra keys, or to write the domain vocabulary, never to loosen the validator.
