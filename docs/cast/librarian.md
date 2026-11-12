# The librarian

This page is for anyone who wants a bundle filled, refreshed or audited.

The **librarian** *binds it into order*. It derives the bundle's concepts from the repository, each with the source it came from. Like a real librarian it catalogues without vouching: it records facts about the repository, never verdicts about truth.

| | |
| --- | --- |
| **Played by** | the [`ktl-librarian`](../../skills/ktl-librarian/SKILL.md) skill, an agent |
| **Runs** | often, including on a schedule |
| **Reads** | the repository, the curator's verdicts in `log.md`, and what readers missed in `.lokf/feedback.md` |
| **Writes** | one file, `.lokf/patch.yaml`, which the [registrar](registrar.md)'s pen applies to the bundle |
| **Never** | writes in a person's name, or confirms anything |
| **Checked by** | the registrar on every write, and the [curator](curator.md) |
| **Line of defence** | first, as the maker ([three-lines.md](../three-lines.md)) |

## Ask it

- "Fill the knowledge bundle from this repository."
- "Refresh the bundle."
- "Audit the bundle for gaps and broken relations."

## What it does

- It derives each concept from a source it names, gives it a LOKF class, and links it to other concepts with typed relations.
- It writes the bundle only through the pen. The pen marks each new concept `status: draft` and stamps who generated it, and when.
- It quotes the passage a footnoted claim rests on, as an excerpt that the registrar finds in the source file on every change.
- It leaves an open question on what it cannot settle, for a person to decide.
- It starts each later run from a work list a script computes, which says of each source that moved whether the quoted passage still holds. It reads the curator's verdicts before it derives anything.
- On a schedule it opens a pull request with whatever changed. In most weeks in which nothing waits, no agent runs.

## Where the rest is written

- **What it needs installed**: [install.md](../install.md#what-each-skill-needs).
- **How verdicts and readers steer its next run**: [how-it-works.md](../how-it-works.md#how-readers-and-verdicts-steer-the-next-run).
- **Knowledge that sits outside the repository**: [ingest.md](../ingest.md).
- **Its copy editor**: [`ktl-prose`](prose.md).
