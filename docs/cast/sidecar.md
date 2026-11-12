# The sidecar

This page is for anyone about to add a knowledge bundle to a repository.

The **sidecar** *lays the network*. It installs `.lokf/`, a dot-folder beside the code like `.git/`, kept out of the project's build. It runs once, and again only to repair a file.

| | |
| --- | --- |
| **Played by** | the [`ktl-sidecar`](../../skills/ktl-sidecar/SKILL.md) skill, an agent |
| **Runs** | once |
| **Writes** | `.lokf/` with its tooling, docs and a dummy bundle at `.lokf/knowledge/`, and the `knowledge_bundle` link beside it |
| **Never** | writes a real concept, or overwrites one |
| **Hands off to** | the [librarian](librarian.md) |
| **Line of defence** | none: it installs the tools and the gate ([three-lines.md](../three-lines.md)) |

## Ask it

- "Add a LOKF knowledge bundle to this repository."
- "Repair the sidecar: the registrar workflow is missing."

## What it does

1. It runs a preflight, which prints what this machine can do and which steps that disables.
2. It copies every file from its templates, and retypes none.
3. It creates the `knowledge_bundle` doorway, a name a folder picker can see.
4. It validates the dummy bundle with the `lokf` toolkit.
5. When asked, it installs the registrar's gate and the scheduled librarian as GitHub Actions workflows. Each does nothing until a repository variable turns it on ([Turn on the workflows](../install.md#turn-on-the-workflows)).

## Where the rest is written

- **What it needs installed**: [install.md](../install.md#what-each-skill-needs).
- **Windows, macOS, other forges, no git and synced folders**: the skill's [portability page](../../skills/ktl-sidecar/references/portability.md).
- **Every switch and secret the workflows read**: the skill's [automation page](../../skills/ktl-sidecar/references/automation.md#switches-and-where-they-go).
- **Opening the bundle through the doorway**: [The bundle in Obsidian](../obsidian.md).
