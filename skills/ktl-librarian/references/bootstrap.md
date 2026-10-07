# Bootstrap discovery: the first run

This page is for the **librarian** on its first run, or on any run that finds the bundle holding no concept beyond the sidecar's two examples. Every later run is a steady-state refresh, which starts from the work list instead (SKILL.md section 1).

Sweep the repository with generic heuristics and map what you find to LOKF classes:

| Look at | Typical finds | Class |
| ------- | ------------- | ----- |
| manifests (`package.json`, `pyproject.toml`, `go.mod`, ...), entry points, `Dockerfile` and compose files, CI config | APIs, CLIs, UIs, workers, databases | `Service` |
| data and schema files (CSV, YAML, JSON, SQL), fixtures, migrations | datasets, tables | `Dataset` or `Table` (use `fields` and `distribution`) |
| external standards, specs and ontologies the code or data encodes | upstream authorities | `Reference` (the encoding `Dataset` gets `derivedFrom` pointing at it) |
| README and docs guides, split by reader need (Diátaxis) | getting-started lessons, task recipes, austere API or schema descriptions, why-and-context discussions | `Tutorial` (learning), `Playbook` (how-to), `Reference`, `Dataset` or `Table` (reference), `Explanation` (understanding); set `genre` to match |
| Agent Skills folders: a `SKILL.md` with `name` and `description` | the host's own skills, never an installed or vendored one | one `Playbook` per skill, `genre: how-to`, holding what [agent-skills.md](agent-skills.md) says |
| domain terms recurring across code, data and docs | vocabulary | `GlossaryTerm` |
| ownership files (`CODEOWNERS`, manifest authors), publishers named inside data files | owners, publishers | `Organization` or `Person`, added only when something links to them through `author` on a concept or `publisher` on the bundle, the only slots whose range is an Agent. No relation slot, and no `relations[].target`, may point at one, since their range is Concept |

Replace the sidecar's two example services: `delete` them through the pen once real concepts stand in their place. A concept you create carries no `human:` actor and starts as `status: draft`, as every concept the pen creates does.

Record the resulting map as a concept, **`playbooks/knowledge-sources.md`** (`type: Playbook`). List each knowledge source, as a repository path or an external URL, the classes it yields, and how to re-check it. Give it each listed path as a `sources` entry: the work list then flags the map as moved when anything inside a listed directory changes, a new file included. Discovery output lives in the bundle this way, versioned and reviewed like every other concept, and not in this skill.
