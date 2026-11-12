# The registrar

This page is for anyone who wants to know what checks a bundle, and when.

The **registrar** keeps the records in order, as a museum's registrar keeps its collection's records. No skill plays this role, and no person has to. Programs play it, so each check gives the same answer every time.

| | |
| --- | --- |
| **Played by** | programs: the `lokf` toolkit, the sidecar's scripts and one workflow |
| **Runs** | on every write, on every read, and on every pull request that touches the bundle |
| **Never** | judges whether a claim is true |
| **In Obsidian** | the [KTL Registrar](https://w3id.org/ktl/registrar/) plugin, which checks each record as it is typed ([obsidian.md](../obsidian.md#plugin-for-skill)) |
| **Line of defence** | second ([three-lines.md](../three-lines.md)) |

## Its parts

| Part | Where it works | What it does |
| --- | --- | --- |
| `lokf validate` | on every change, and again in continuous integration (CI) | Checks each concept's frontmatter against the schema, and that every typed relation points at a concept that exists |
| `knowledge-apply.sh`, *the pen* | at the librarian's desk | Applies the librarian's patch, and is the only way the librarian writes the bundle. It refuses an operation that would fake or change a person's record |
| `knowledge-report.sh` | at the reader's desk and the curator's | Computes every trust label and the bundle's health line, so that neither is a model's arithmetic |
| `knowledge-registrar.yaml`, *the gate* | on each pull request that touches the bundle | Runs `lokf validate`, the conventions script and the `provenance` job. That job ties each confirmation that is added or removed to that person's approval or signed commit |
| `knowledge-provenance.sh` | on another forge, or none | Checks each confirmation's signature against the keys under `.lokf/curators/` |

## Run it yourself

```bash
cd .lokf && just lokf-validate && just lokf-check-refs
bash .lokf/scripts/knowledge-report.sh health
```

The second command runs from the repository's root and prints one line, such as `Confirmed by a person: 3 of 40`.

## Where the rest is written

- **Who writes the bundle, and what checks each write**: [how-it-works.md](../how-it-works.md#who-writes-the-bundle-and-what-checks-it).
- **What each check proves, and what it cannot**: [Four levels of checking](../how-it-works.md#four-levels-of-checking).
- **How the gate ties a confirmation to a person**: the sidecar's [gate page](../../skills/ktl-sidecar/references/gate.md) and [signing-commits.md](../signing-commits.md).
- **What the guards defend against**: [threat-model.md](../threat-model.md).
