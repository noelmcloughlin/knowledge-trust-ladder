# References

* [LOKF specification](lokf-specification.md) - The canonical definition of the Linked Open Knowledge Format - a semantic profile of OKF binding every field, type, and relationship to schema.org, DCAT, and PROV-O.
* [OKF specification (v0.2)](okf-specification.md) - Google's Open Knowledge Format - a folder of Markdown concept files with YAML frontmatter, requiring only `type`, plus the v0.2 provenance, trust, and lifecycle families.
* [Agent Skills specification](agent-skills-specification.md) - The specification defining a skill directory - a required SKILL.md with name/description frontmatter, plus optional scripts/, references/, and assets/.
* [LOKF toolkit (lokf on PyPI)](lokf-toolkit.md) - The Python package that validates, converts, and serves a LOKF bundle - the dependency the scaffolded .lokf/pyproject.toml declares.
* [LinkML](linkml.md) - The schema-modelling language LOKF is written in, and the generator suite that turns a schema into JSON Schema, Pydantic models, SHACL shapes, docs, and OWL.
* [gh skill (GitHub CLI)](gh-skill-cli.md) - The GitHub CLI command group that installs, pins, and publishes agent skills from GitHub repositories; the publish path this repository uses for releases.
* [Open Skills CLI (npx skills)](open-skills-cli.md) - The vendor-neutral installer for agent skills, supporting GitHub, git, and local sources with repeatable --skill and --agent selection.
