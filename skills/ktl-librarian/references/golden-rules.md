# The Golden Rules in full

This page is for the **librarian**: it holds the tables and the detail behind the seven Golden Rules in SKILL.md. Read it before you create a concept or change a concept's frontmatter. [lokf.nolan-nichols.com](https://lokf.nolan-nichols.com/specification/) is the canonical statement of what each field means.

## Rule 2: the semantic header and `base_iri`

The bundle-root `index.md` declares the keys that lift the whole bundle into RDF. The values below are illustrative; the real ones are minted when the sidecar is laid down:

```yaml
lokf_version: "0.2"
okf_version: "0.2"
base_iri: https://acme.example/knowledge/
context: https://w3id.org/lokf/context.jsonld
title: Acme Platform Knowledge Bundle
description: ...
license: https://creativecommons.org/licenses/by/4.0/
publisher: { type: Person, id: https://acme.example/knowledge/person/jane-doe, name: Jane Doe }
```

`base_iri` plus the concept ID mints each concept's IRI (`@id`), and `context` maps frontmatter keys to IRIs. Without these keys the bundle degrades to plain OKF.

**Choose `base_iri` as an identifier in a namespace you control.** A concept's `id` is a globally unique *name* that merely looks like a URL, so a 404 on it is valid. Linked Data practice ("Cool URIs") still says identifiers *should* eventually work as links. Test a `base_iri` for authority and future resolvability:

- **Never mint inside a URL space the project does not control**, such as `https://github.com/<org>/<repo>/knowledge/...` or any third-party domain. The host owns that path space, so the IRIs can never be made to resolve, and they misattribute naming authority to the host.
- **Prefer, in order:** (a) a namespace the project already publishes under. If its schemas or ontologies use a persistent-identifier namespace (w3id.org, purl.org, an owned domain), put the bundle there, for example `https://w3id.org/<org>/<project>/knowledge/`. (b) A new persistent-identifier registration; a w3id.org rule is a small pull request to `perma-id/w3id.org`, redirectable later to rendered pages such as GitHub Pages. (c) A project-owned domain. Repository cues are schema `id` or namespace declarations, a docs `site_url`, a Pages deployment.
- **Migrate early if the base is wrong.** Changing `base_iri` rewrites every concept `id` and breaks any outside link to the old ones. That is cheap while the bundle is young and expensive later. To migrate, replace the namespace in `base_iri`, the publisher `id`, every concept `id`, and every typed-relation target. Leave `resource` and `distribution` URLs alone, since they are real links and not minted identifiers. Log the migration and its reason, run `just lokf-validate` again, and confirm the converted graph holds only the new namespace.
- **When a person asks "these IDs don't resolve; is that a problem?"**, answer that it is valid by design, then apply the test above. An uncontrolled namespace can never resolve and should be migrated. A controlled one that is not yet registered needs the pending registration noted, not the 404 treated as a defect.

## Rule 3: classes and `genre`

Consumers read an unknown class as `lokf:Concept`; the validator rejects it (Rule 7). The type-specific fields:

| class | type-specific fields |
| ----- | ---------------------- |
| `Table`, `Dataset` | `fields`, a list of `Field` (`name?`, `description?`, `datatype?`, `is_key?`, `unit?`, `constraints?`); `distribution`, a list of `Distribution` (`access_url`, `name?`, `description?`, `media_type?`). These are structured objects, **never** plain strings or URLs |
| `Metric` | `unit`, `formula`, `measures` |
| `Service` | `endpoint`, `documentation`; `http_method` only where one verb applies, and then one of `GET`/`POST`/`PUT`/`PATCH`/`DELETE`/`HEAD`/`OPTIONS`, uppercase (a closed enum since lokf 0.8.0) |
| `GlossaryTerm` | `definition`, `abbreviation` |

The optional Diátaxis facet `genre` (`tutorial`, `how-to`, `reference` or `explanation`) tags how a concept's *prose* serves the reader. It is orthogonal to `type`, and a concept has one mode: split it and link the parts with `references` or `about` when it drifts. Pick it with the compass: is the reader *studying or working*, and *doing or thinking*? Study and do is `tutorial`, work and do is `how-to`, work and think is `reference`, study and think is `explanation`. The schema's `DiataxisMode` values carry `diataxis_action_cognition` and `diataxis_acquisition_application` annotations, so derive the mapping from the schema rather than guessing.

## Rule 4: typed relationships

Typed relations are LOKF's core upgrade over plain OKF. Each maps to a fixed RDF predicate. Values are concept IRIs, or IDs resolved against `base_iri`, all optional and multivalued:

| field | predicate | meaning |
| ----- | --------- | ------- |
| `isPartOf` | `dcterms:isPartOf` | this is part of the target |
| `hasPart` | `schema:hasPart` | the target is part of this |
| `references` | `dcterms:references` | this refers to the target |
| `dependsOn` | `dcterms:requires` | this depends on the target |
| `derivedFrom` | `prov:wasDerivedFrom` | provenance |
| `about` | `schema:about` | subject matter |
| `sameAs` | `schema:sameAs` | same entity |
| `relatedTo` | `dcterms:relation` | generic association |
| `definedBy` | `rdfs:isDefinedBy` | formally defined by |
| `source` | `dcterms:source` | sourced from the target |

**Multivalued means always a YAML list, even for one value.** A bare scalar (`dependsOn: <iri>`) reads naturally but fails schema validation, because the generated schema requires an array for every one of these ten slots. Write a one-item list instead: `dependsOn:` on its own line, then `- <iri>` indented below it. A real audit of this bundle found the bare form in 12 of 25 concepts, and only `lokf validate` catches it.

For a predicate outside this set, use the generic `relations` list of reified objects: a `predicate` from the `RelationType` vocabulary, such as `joinsWith`, and a `target`. Markdown links in the body stay valid and welcome beside the typed fields.

## Rule 5: core fields

`title` maps to `schema:name`, `description` to `schema:description`, `resource` to `schema:url`, `tags` to `schema:keywords`, `timestamp` to `schema:dateModified`, and the body, the Markdown after the frontmatter, to `schema:text`. The optional `id`, `created`, `version`, `license`, `author`, `genre` (`schema:genre`, Rule 3) and `citations` complete the set. Two JSON-LD aliases let plain OKF frontmatter behave as Linked Data: `type` becomes `@type`, the concept's class, and `id` becomes `@id`, the subject IRI.

Two v0.1 fields are **superseded in v0.2** and still read as fallbacks: `timestamp` by `generated.at`, and `citations` by `sources` (Rule 6). Keep `timestamp` only on a v0.1 concept you are not otherwise touching.

A local `resource` must be a path git *tracks*. Gitignored runtime state, such as an installed skill under `.agents/` or `.claude/`, a build artifact or a local virtualenv, resolves on the machine that has it and nowhere else. It fails conventions rule 5 in CI and tells a reader to open a file they do not have. Point at the published copy instead, pinned to the version the host installs (a skill's release tag, for example), and say in the body where it lands locally if that helps.

## Rule 6: trust, provenance and lifecycle

These optional families (OKF v0.2 §5.4) make trust signals queryable RDF instead of loose YAML. Their absence carries meaning: an unverified concept stays valid and is never rejected. Never invent them; record only what the origin states.

| family | field | shape and RDF predicate | meaning |
| ------ | ----- | ---------------------- | ------- |
| provenance | `generated` | `{ by, at, revision? }`, `prov:wasGeneratedBy` | who or what produced the current content, and when; `revision` (lokf 0.9.0 and later) is the state of the `resource` it was derived from. **Supersedes `timestamp`**. |
| trust | `verified` | list of `{ by, at, revision? }`, `lokf:verified` | verification events; a bare `{ by, at }` mapping MUST be read as a one-element list. |
| provenance | `sources` | list of Source, `schema:isBasedOn` | materials the concept derives from, each with a `resource` (REQUIRED). A Source may also carry `id` (a footnote or merge key), `title`, `author`, `usage_count`, `last_modified` (a datetime) and `excerpt` (lokf 0.9.0 and later: the exact passage the concept relies on, quoted verbatim). `author` is an actor string: `<prefix>:<id>` such as `team:docs`, or `<producer>/<version>`. Supersedes `citations`. |
| usage | `usage_window` | `{ from, to }` (datetimes), `lokf:usageWindow` | the window framing `usage_count` signals; a sibling of `sources`, which a Source entry MAY override. |
| lifecycle | `status` | `draft`, `stable` or `deprecated`, `schema:creativeWorkStatus` | absent means stable. |
| lifecycle | `stale_after` | datetime, `schema:expires` | stale when `now >= stale_after`; a bare `YYYY-MM-DD` is read as that day at 00:00:00Z. |

**Actors** (`generated.by`, `verified[].by`, `sources[].author`) are plain OKF §7 literal strings (`<producer>/<version>`, `human:<id>`, `process:<id>`), carried verbatim and never coerced to IRIs. **Trust tiers derive from them and are never stored:** no `verified` event means *unverified*; only non-human actors mean *machine-confirmed*; any `human:` actor means *human-reviewed*. `knowledge-report.sh` computes each concept's label from these fields.

**This skill's own `verified` event.** When a refresh actually re-confirms a concept against its `resource`, record it with the pen's `recheck`, which writes one `{ by: process:ktl-librarian, at }` event and replaces this skill's previous one. It never touches a `human:` event, and you never record one on a concept you did not re-check this run. That makes "the bot checked this last week" distinguishable from "nobody ever looked". It is not a claim of truth. Only **ktl-curator** writes a `human:` event, and only on a person's explicit say-so.

**`generated` comes from the pen.** It stamps `{ by, at }` from the clock on every concept an operation creates or changes, and never on an untouched one, so the diff never fills with churn. A concept a person confirmed reads as *edited since a person last confirmed it* once the pen changes it; conventions rule 13 holds every other hand to the same restamp.

**`revision`, where the toolkit accepts it.** The field is proposed for lokf 0.9.0 and not yet released, and the 0.8.0 validator rejects the key. Pass it on an operation as the state of the `resource` you derived from. For a committed path in the repository, it is the full hash from `git log -1 --format=%H -- <path>`, since an abbreviation can become ambiguous as the repository grows and the gate resolves the pin against the tree. For a URL, it is its `ETag` or a `sha256:` digest of what you fetched. Always quote it: an all-digit commit id is otherwise read as a number and fails `lokf validate`. Leave it out on an older toolkit, when the file has uncommitted changes or is not under version control, and when you did not read the source this run.

**AttestedComputation** (`type: AttestedComputation`; OKF's spaced `Attested Computation` normalizes to it) carries an immutable, sanctioned recipe, semantically a `prov:Plan`. Its fields are `runtime` (REQUIRED, for example `bigquery`, `postgres`, `dbt` or `python`) and `parameters`, each `{ name, type, required }` with `type` drawn from `ParameterType`. Then come `computation` (an optional file path; without it, the body's `# Computation` fenced block IS the recipe), `executor` (`{ resource, receipt }`) and `attester` (`{ resource }`).

## Rule 7: stay permissive

Missing optional fields, an unknown `type`, unknown keys and broken cross-links MUST NOT cause rejection. That rule binds consumers: readers, converters, `lokf serve`. `lokf validate` checks against the declared vocabulary, so a bundle that extends it declares its classes and keys in a domain schema and validates with `--schema`: [domain-schema.md](domain-schema.md).
