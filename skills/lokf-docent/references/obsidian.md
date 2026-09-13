# Opening the bundle in Obsidian

Obsidian is optional: the bundle is plain Markdown, and every skill works without it. Asked how to open, see, or browse the bundle in Obsidian -
or whether it should sit inside someone's vault - answer from this page. It is the same on every host, so the bundle itself will not carry it; if
the host bundle has a playbook of its own on the subject, that one wins.

## The answer

Two vaults. The one the person already has is their **workshop** and stays exactly as it is - nothing is moved into it, nothing migrated out. The
bundle is the **exhibition**, and it is opened as a vault of its own:

1. **File → Open folder as vault**, and pick `knowledge_bundle` at the host root - the link `lokf-sidecar` laid beside `.lokf/` so the bundle has a
   name a folder picker can see. Open the link *itself*, never the host root: a vault opened at the root cannot see a dot-folder or a link that
   resolves inside it, which is exactly what keeps the workshop clean.
2. Install [LOKF Registrar](https://github.com/noelmcloughlin/obsidian-lokf-registrar) and
   [LOKF Curator](https://github.com/noelmcloughlin/obsidian-lokf-curator) *in that vault* - Obsidian installs plugins per vault. Nothing to
   configure: the root `index.md` carries the bundle's header, so the whole vault is the bundle. Both are optional; the bundle is only Markdown.

If `knowledge_bundle` is missing - a sync service such as OneDrive drops links, and a Windows checkout without `core.symlinks` shows it as a small
text file - the person can open `.lokf/knowledge` by typing the path into the picker, or make the link once, from the host root:

```bash
ln -s .lokf/knowledge knowledge_bundle      # or `just lokf-link` from .lokf/
```

```bat
mklink /J knowledge_bundle .lokf\knowledge   # Windows: a junction, no administrator rights
```

## What not to suggest first

- **Putting the bundle inside their vault.** Obsidian indexes a real folder inside a vault like any other, so link suggestions, the quick switcher,
  graph and search would mix exhibits with everyday notes; *Settings → Files and links → Excluded files* only makes that less noticeable. If they
  want it anyway, say that cost, and that both plugins detect a top-level `knowledge_bundle/` folder or any folder listed under *Bundle root
  folders*.
- **Making the link yourself.** This skill is read-only outside `.lokf/feedback.md`, and a missing link is not a knowledge gap - never record it
  there. Give the command; if they want an agent to do it, that is `lokf-sidecar`'s repair path (`just lokf-link`).
