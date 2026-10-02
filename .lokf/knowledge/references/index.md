# References

* [Agent Skills specification](agent-skills-specification.md) - The specification that defines a skill directory: a required SKILL.md with name and description frontmatter, plus optional scripts/, references/ and assets/ folders.
* [gh skill (GitHub CLI)](gh-skill-cli.md) - The GitHub CLI command group that installs, pins and publishes agent skills from GitHub repositories. It is the publish path this repository's releases use.
* [LinkML](linkml.md) - The schema-modelling language LOKF is written in, and the generator suite that turns a schema into JSON Schema, Pydantic models, SHACL shapes, documentation and OWL.
* [LOKF specification](lokf-specification.md) - The canonical definition of the Linked Open Knowledge Format: a semantic profile of OKF that binds every field, type and relationship to schema.org, DCAT and PROV-O terms.
* [LOKF toolkit (lokf on PyPI)](lokf-toolkit.md) - The Python package that validates, converts and serves a LOKF bundle. It is the dependency the scaffolded .lokf/pyproject.toml declares.
* [OKF specification (v0.2)](okf-specification.md) - Google Cloud's Open Knowledge Format: a folder of Markdown concept files with YAML frontmatter that requires only `type`, plus the v0.2 provenance, trust and lifecycle fields LOKF makes queryable.
* [Open Skills CLI (npx skills)](open-skills-cli.md) - The vendor-neutral installer for agent skills, `npx skills add`, which takes a GitHub repository, a git URL or a local path and repeatable --skill selections.
