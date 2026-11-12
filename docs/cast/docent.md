# The docent

This page is for anyone with a question about a repository that has a bundle.

The **docent** *guides the visitors*. A docent is a museum's guide. It answers from the bundle, and says how far each concept it used has been checked. Like a real docent it explains the exhibition and moves nothing on the shelves.

| | |
| --- | --- |
| **Played by** | the [`ktl-docent`](../../skills/ktl-docent/SKILL.md) skill, an agent |
| **Runs** | whenever anyone asks |
| **Reads** | the bundle's `index.md` first, then one to three concepts, then the source for an exact value |
| **Writes** | nothing in the bundle. A script records what a reader missed in `.lokf/feedback.md`, after the docent asks once |
| **Never** | edits or confirms a concept |
| **Line of defence** | none: it sits where the reader does ([three-lines.md](../three-lines.md)) |

## Ask it

Ask anything about the project: what a service does, who owns it, which policy applies, what a term means.

## What it does

- It answers from the bundle first, and goes to the repository only when the bundle has no answer.
- It names each concept the answer rests on, with its trust label, such as *confirmed by a person* or *still a draft*.
- It opens the source before it states a version, a number or a path.
- It gives the passage a concept quotes from its source, and says that the bundle quotes it.
- It records a miss, or a disagreement between the bundle and a source. The librarian handles that record on its next run.

## Where the rest is written

- **Eight captured answers**: [examples/docent.md](../examples/docent.md).
- **Only want to ask?** Install this one skill, by a route from [install.md](../install.md#quick-start).
- **In Microsoft 365 Copilot**, where it answers from a snapshot of the bundle: [m365.md](../m365.md).
- **What the labels mean**: [Trust stays visible](../architecture.md#trust-stays-visible).
