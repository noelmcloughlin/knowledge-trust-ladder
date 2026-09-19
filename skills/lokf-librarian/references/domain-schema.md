# Extending the vocabulary: a domain schema the validator checks

LOKF's core vocabulary - its classes and typed relations - is small on purpose, and Rule 7 keeps every consumer tolerant of what falls outside them. A bundle whose domain needs more - a degree programme's `Module`, a clinic's `Protocol`, an `ects` or `dosage` key - does not loosen anything. It gives the domain a schema of its own, written in the same [LinkML](https://linkml.io) as LOKF's, importing LOKF's, and validates against both with the flag the toolkit already has: `lokf validate --schema <file>`. The curator's [domain-schemas.md](../../lokf-curator/references/domain-schemas.md) covers when to do this and what it costs (nothing new to install); this page is the recipe.

## What the validator expects

`lokf validate` checks a bundle against the classes and slots a schema declares, and nothing else. Two consequences shape the recipe:

- **Every class is closed.** A concept fails its class on any key the class does not declare, so a built-in class plus one key of your own is not valid - subclass it and declare the key.
- **`type` names the class exactly.** Each class's schema pins `type` to its own name, and the bundle's concepts are matched against all classes at once. A record of a subclass writes the subclass name, not the parent's.

A concept outside the declared vocabulary reports as `is not valid under any of the given schemas`; that line is the signal you have reached this page, not an error to route around.

## The recipe

1. **A pinned copy of the core schema beside it.** LinkML resolves `imports:` relative to the importing file, so `.lokf/lokf.yaml` must exist, at the version the sidecar's `pyproject.toml` floors. Copy it out of the installed package:

   ```bash
   cd .lokf && uv run python -c "from importlib.resources import files; print(files('lokf') / 'data' / 'lokf.yaml')" | xargs -I{} cp {} lokf.yaml
   ```

   The copy does double duty: `convert`, `serve` and `query` take no `--schema` flag and resolve `lokf.yaml` from the current directory and its ancestors before the packaged copy, so from `.lokf/` this is also the schema they read.

2. **The domain schema**, `.lokf/<slug>.yaml`, minted under the same authority as `base_iri` (Rule 2). A learning-programme bundle, for instance:

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

   A class `is_a: Concept`, or any descendant of it, joins the bundle's concept union automatically: the core classes become the core plus yours. Subclass a built-in whose meaning fits; give a class of its own to what no built-in describes (a delivery pattern is not a `Policy`, however tempting the stretch); never leave extra keys on a built-in unchanged.

3. **Frontmatter names the class exactly.** A record with `type: Reference` and a `source_kind` key fails: `Reference` does not declare the key, and `SourceSnapshotReference` requires its own name. Write the subclass name; `is_a` still makes it `rdfs:subClassOf` its parent in the projected graph.

4. **Wire the flag in.** In the sidecar's `justfile`, add `schema := "<slug>.yaml"` and make `lokf-validate` run `uv run lokf validate --schema {{ schema }} {{ bundle }}`; pass the same `--schema <slug>.yaml` on the validate step of both workflows (`knowledge-registrar.yaml`, `knowledge-librarian.yaml`). `lokf-check-refs` needs it too, since it runs `lokf validate --check-refs`: without the flag a domain class fails that recipe as an unknown type. Nothing else in the sidecar changes. That one variable is also how the librarian learns the host's vocabulary: Rule 3 has it read the schema the justfile names and treat every `Concept` descendant there as a class it may choose (`lokf vocab` lists relations only and takes no `--schema`, so the file itself is the source).

5. **Tell both plugins.** LOKF Registrar and LOKF Curator each have a *Known LOKF types* setting listing the built-in classes; add your classes to both, the same list in each. Neither plugin can read the schema itself - the exhibition vault's root is `.lokf/knowledge`, and `<slug>.yaml` sits one level up, outside it. Listed, a domain class stops opening with the registrar's unknown-type warning and joins its autocomplete, stops counting against the curator's *vocabulary fit* line, and can carry a review interval of its own in `policies/knowledge-curation.md`. A list you have edited is yours to keep current when the core schema gains a class. (Before LOKF Curator gained the setting, its vocabulary-fit line counted against the built-ins only; read that line on an older build as "concepts outside LOKF core", not as errors.) The *skills* need no telling: the curator reads the justfile for the same `--schema` Rule 3 does ([lokf-curator/references/trust-fields.md](../../lokf-curator/references/trust-fields.md)).

## What a domain schema does not do

- **The graph.** The core JSON-LD context declares `@vocab: https://w3id.org/lokf/`, so `convert`, `serve` and `query` already project undeclared keys - as `lokf:ects`, in LOKF's namespace rather than yours - and, up to lokf 0.8.0, undeclared types the same way (`a lokf:Module`). From lokf 0.9.0 an undeclared type projects as `a lokf:Concept` with the name kept in `schema:additionalType "Module"`, so filter on that literal rather than on a minted class. A domain schema does not change that: the three commands take no `--schema` or `--context`, and a raw `gen-jsonld-context <slug>.yaml` output cannot simply replace the packaged context beside the bundle, because it lacks the packaged aliases `type` → `@type` and `id` → `@id` (tested: every node becomes a blank node carrying a literal `lokf:type`). Read `lokf:<key>` in a query result as "declared to the validator, not yet to the graph"; a domain context that keeps the core aliases and maps your terms to your prefix is a toolkit feature that does not exist yet.
- **Keeping the copy current.** Section 1's tooling-version step gains one line on such a host: when the `lokf` floor moves, refresh the pinned `lokf.yaml` to the new version in the same change and re-run `just lokf-validate`. A copy older than the toolkit validates against classes and slots the toolkit no longer means.
- **Deciding whether to do it.** That is the curator's conversation and the team's call: [lokf-curator/references/domain-schemas.md](../../lokf-curator/references/domain-schemas.md). Until a schema exists, a concept with a type or key of its own is still knowledge under Rule 7 - and still outside what `lokf validate` checks, so the registrar gate stays red. The librarian's choices are to fit the concept onto a built-in class with no extra keys, or to write the schema; never to loosen the validator.
