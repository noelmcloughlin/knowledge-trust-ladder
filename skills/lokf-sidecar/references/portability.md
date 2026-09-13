# Portability - reusing lokf-sidecar in another repo

This skill is repo-agnostic; run it in any repository, including an empty one.

## It pairs with lokf-librarian

The scaffolded wrapper script resolves `lokf-librarian/SKILL.md` from the repo's skill directory, checking `.claude/skills/` (Claude Code), then
`.github/skills/` (Copilot-style agents), `.agents/skills/` (a generic, tool-agnostic convention), then bare `skills/` (a repo that publishes the
skills it also uses). Install **all four** - `lokf-sidecar`, `lokf-librarian`, `lokf-curator`, `lokf-docent` - each is a directory,
including `templates/` and `references/` - into whichever of those the new repo uses. If none fits, add that directory to the wrapper's `candidate` list rather than leaving a fourth, silently-unchecked convention. All skills are generic: copy them unmodified; the librarian's first run discovers the project's knowledge sources itself.

This repository ([`lokf-agent-skills`](https://github.com/noelmcloughlin/lokf-agent-skills)) is the sole, canonical source of all four LOKF skills - install from it via `gh skill install` / `npx skills add` rather than copy-pasting, and pin them all to the same release.

## Tooling

Validation uses [`uv`](https://docs.astral.sh/uv/) + the `lokf` PyPI package ([`just`](https://just.systems/) is optional). The files scaffold fine without them; only Step 4's validation needs them installed - see Step 4 for the raw-schema fallback when Python is unavailable.

## The host need not be git, GitHub, or Linux

The scaffold is just files, so any directory tree works: a local or shared filesystem, or Storage-as-a-Service content mounted/synced locally (Drive,
Dropbox, an S3/blob mount, ...).

- **No git** - `.lokf/.gitignore` is inert: keep it (a VCS may arrive later) or drop it. Skip the "commit" instructions, rely on the platform's own versioning/backup, and review changes by whatever mechanism the host offers instead of PRs. Step 5 does not apply.
- **Not GitHub** (other forges, or none) - Step 5's workflow files are GitHub Actions-specific. Scaffold only the wrapper script and schedule it, plus `lokf validate` as the gate, with the platform's equivalent: another CI's pipeline, cron, or a systemd timer. The wrapper needs only `bash` and the
  lokf-librarian skill file.
- **Not Linux/POSIX** - run the `justfile` recipes and the wrapper from a POSIX shell (Windows: WSL or Git Bash), or bypass them and call `uv run lokf ...` directly; `uv` and the toolkit are cross-platform. The Step 2 `knowledge_bundle` doorway is `ln -s` from a POSIX shell; on Windows prefer a junction - `mklink /J knowledge_bundle .lokf\knowledge`, which needs neither administrator rights nor Developer Mode, and which Obsidian follows exactly as it follows a symlink - falling back to `mklink /D` under Developer Mode if a true symlink is wanted; a filesystem that supports neither (some FAT32/exFAT or older network mounts) just skips it - it's a convenience pointer, and every skill and toolkit command still addresses `.lokf/knowledge` directly.
- **Synced or shared folders** (OneDrive/SharePoint, Drive, Dropbox, iCloud) - the sidecar syncs as ordinary files (Microsoft's restricted-name list for OneDrive and SharePoint has nothing against a leading dot), so `.lokf/knowledge` is the same real folder on every machine; but OneDrive syncs neither symbolic links nor junctions, so the Step 2 doorway is the one per-machine piece: recreate it after the first sync (`just lokf-link` from `.lokf/`, or the junction above), or open `.lokf/knowledge` by path. Git, unlike a sync client, carries the link itself. A team that wants the bundle *synced under a visible name* - a document library nobody reaches through git - may rearrange it by hand at the host root: `mv .lokf/knowledge knowledge_bundle && ln -s ../knowledge_bundle .lokf/knowledge` (Windows: `mklink /J .lokf\knowledge %CD%\knowledge_bundle`, per machine). Every skill and recipe still addresses `.lokf/knowledge` and follows the link, the Step 5 templates name both paths, and the Obsidian plugins detect a top-level `knowledge_bundle/` on their own. Never inside an Obsidian vault - next bullet.
- **An Obsidian vault as host** (optional - nothing in the skills needs Obsidian) - the default layout is the right one: the person opens `knowledge_bundle` *itself* as a second vault (File → Open folder as vault) and installs the plugins there, and Obsidian writes that vault's workspace state through the link into `.lokf/knowledge/.obsidian/`, which `templates/gitignore` excludes. The host vault stays clean because Obsidian never indexes a dot-folder, and its file reconciler (`reconcileSymbolicLinkCreation`, 1.13.7; the help page says the same in words) skips a link whose resolved path equals, contains or lies inside a folder it already watches, the vault root included - so a vault opened at the host root lists neither `.lokf/` nor `knowledge_bundle`. A real folder inside the vault is indexed like any other, and so is a link whose target lies *outside* the vault (a vault may link a repository's `.lokf/knowledge` into one of its folders and list it under the plugins' *Bundle root folders*): either way the exhibition enters the workshop's link suggestions, quick switcher, graph and search, *Settings → Files and links → Excluded files* only makes that less noticeable, and Obsidian Sync carries no links. Hence the rule: the bundle is never laid down as a real folder inside a vault.
