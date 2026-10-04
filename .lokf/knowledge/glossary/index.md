# Glossary

* [LOKF](lokf.md) - The Linked Open Knowledge Format, the semantic profile of OKF this bundle is written in, which binds every field to a public vocabulary so the bundle projects to RDF.
* [OKF](okf.md) - The Open Knowledge Format, Google's specification for a folder of Markdown concept files with YAML frontmatter, which LOKF profiles.
* [Knowledge bundle](knowledge-bundle.md) - The `.lokf/knowledge` directory - containing one-concept-per-file Markdown, carrying a semantic header, that is simultaneously human-readable documentation and a queryable graph.
* [Trust label](trust-label.md) - The plain words the skills use for how far a concept has been checked, derived from its frontmatter on every read and never stored.
* [The pen](the-pen.md) - The name for `knowledge-apply.sh`, the only way ktl-librarian writes the bundle: it applies the operations in `.lokf/patch.yaml`, stamps `generated`, keeps the index in step, and refuses a `human:` actor.
* [Docent](docent.md) - A museum's name for a guide, and the role that answers a reader's questions from the bundle, says how far each answer has been checked, and writes nothing in the bundle.
* [Desk](desk.md) - The README's word, in its library terms, for the place where a role does its work with the bundle: the registrar is `knowledge-apply.sh` at the librarian's desk, and `knowledge-report.sh` at the reader's and the curator's.
* [Registrar](registrar.md) - The person in a museum who keeps the collection's records, and Knowledge Trust Ladder's fifth role, which programs play: the `lokf` toolkit, the gate `knowledge-registrar.yaml`, the pen and the report script.
* [Sidecar](sidecar.md) - `.lokf/`, the folder beside a project's code that holds the bundle and the tooling that checks it, kept out of the project's build; also the role, and the ktl-sidecar skill, that installs it.
* [Accession](accession.md) - A museum's word for an item added to its collection, which the README's registrar keeps documented with its provenance filed; in the bundle, each concept added is one.
