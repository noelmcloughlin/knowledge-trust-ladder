# Auditing the bundle: what each check catches, and what is left to you

This page is for the **librarian**: it backs SKILL.md section 2 with what each tool proves, what it cannot, and what to audit by hand.

## What the tools prove

- **`just lokf-validate`** checks frontmatter and the assembled bundle against the declared vocabulary with the generated JSON Schema. A bundle that extends the vocabulary validates with `--schema` ([domain-schema.md](domain-schema.md)). It reads a body as an opaque string and never opens `log.md`.
- **`just lokf-check-refs`** runs `lokf validate --check-refs`. It takes the relation slots from the schema and resolves every target inside `base_iri` to a concept in the bundle. JSON Schema alone passes a fabricated or stale IRI in `dependsOn` and the other slots, since it is still a valid IRI, and this closes that gap. It cannot tell you a target is *wrong*, only that it is *missing*: a `dependsOn` pointed at the right concept's evil twin still passes.
- **The SHACL shapes** the toolkit generates for the projected graph run nowhere in this sidecar. A check only the shapes express, such as a relation target being a Concept rather than a Person, is therefore not made.
- **`bash scripts/knowledge-conventions.sh`** checks the fourteen conventions `lokf validate` cannot see, the ones this skill and both Obsidian plugins rely on. The ktl-sidecar skill lays it down, and the registrar gate runs it on every `.lokf/**` pull request, so a bundle it rejects fails the gate. Run it before handing off. Its rules are listed in ktl-sidecar's [gate.md](../../ktl-sidecar/references/gate.md).
- **`bash scripts/knowledge-report.sh`** computes every trust label and the health line. Quote it; never work a label out yourself.

## What to audit by hand

- **Correctness.** The class matches the asset. Typed relations point the right way (`isPartOf` versus `hasPart`, `dependsOn` versus `derivedFrom`). Each relation target resolves to the *intended* concept, not merely to *a* concept, which `lokf-check-refs` cannot catch. `id` and `base_iri` give the expected IRIs, and the namespace passes Rule 2's authority test. `endpoint` and `resource` still resolve.
- **Gaps.** New code or data files with no concept. Untyped body links that should be typed relations. A missing `id` on a concept other bundles link to. A class left as a generic `lokf:Concept` where the vocabulary has a proper type, in the core list or the host's domain schema. Provenance or trust that is knowable but unrecorded: a missing `generated` or `sources`, or no `status` or `stale_after` on content that has clearly gone deprecated or stale.
- **Bugs.** Malformed YAML. An invalid enum or datatype. A relation target that resolves to nothing. A missing `base_iri` or `context` in the root `index.md`. A `lokf` constraint in `.lokf/pyproject.toml` with no `>=` floor, or one behind the latest release (SKILL.md section 1, step 7).

Report the findings as a checklist, fix the mechanical ones through the pen, and run `just lokf-validate` again.

## Lint the Markdown too

The toolkit validates frontmatter and the projected graph, so a bundle can be schema-valid and still fail the host's lint gate on its bodies. Treat that as part of the audit, not as the host's problem. If the host has a markdownlint config at its root (`.markdownlint-cli2.jsonc`, `.markdownlint.jsonc`, `.markdownlint.json` or `.markdownlint.yaml`), run `npx markdownlint-cli2 '**/*.md'`, quoted so the shell does not expand the glob, and fix what it reports on files you touched.

Where `npx` is missing, grep the files you changed for the mistake that has already failed CI for this skill. Markdown reads a line that begins with a dash and a space as a list item. So a spaced dash ("X - Y") in carried-over text that wrapping moves to the start of a line turns a paragraph into a list, and fails `MD032/blanks-around-lists`. Look for such a line whose previous line is unindented prose: not blank, not a heading, not another list item, and not the indented continuation of a wrapped bullet. Writing each paragraph as one unwrapped line avoids the trap, since there is then no line break before the dash.

## Without `uv`

Without `uv` or the `lokf` package there is no substitute for the generated validator and the reference check. Fall back to the manual structural cross-check against the raw schema that ktl-sidecar's Step 4 describes, and say so in the audit report rather than claim full coverage. The fallback has no cardinality check, so a bare scalar where a slot is multivalued (Rule 4) passes it and fails only real `lokf validate`. A bundle that has only passed the manual fallback is not proven schema-valid; report it as such.
