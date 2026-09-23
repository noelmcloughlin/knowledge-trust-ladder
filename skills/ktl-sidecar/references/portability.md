# Portability: reusing the LOKF skills on another host

The skills are repository-agnostic. Run them in any directory tree, including an empty one. The bundle is the same on every host: `.lokf/knowledge/`, one Markdown file per concept, validated by the same toolkit. What varies is the shell, the version control, the forge (GitHub, GitLab, Forgejo, or none), and what each of the four skills can do there.

**Run the preflight first.** Before the sidecar exists it is `bash templates/scripts/knowledge-preflight.sh`; afterwards it is `.lokf/scripts/knowledge-preflight.sh`. Its last line names your case, and the matching section below says what to do. If a line names something you cannot fix yourself, [prerequisites.md](prerequisites.md) says who can, and what to send them.

| Host | Works | Lost | Substitute |
| --- | --- | --- | --- |
| Linux, git, GitHub | everything | - | - |
| macOS | everything, on the stock bash 3.2 | `sha256sum` | `shasum -a 256` |
| Windows, Git for Windows | everything from its bash | the `ln -s` doorway | a junction (below) |
| Windows, PowerShell | the toolkit, git, the plugins | every script and command, which are bash | run them through Git for Windows' bash (below) |
| GitLab, Forgejo, Gitea | the sidecar, librarian, docent; the curator with `glab` or the signing-key route | the two GitHub Actions workflows | the wrapper in that CI, the gate ported per the recipe below, or the forge-free gate |
| No forge, git only | everything local | the gate, pull requests, the scheduled loop | review by the host's own mechanism; the forge-free gate for confirmations |
| No git (a synced or shared folder) | the bundle, validation, all four skills' reading | `revision`, the gate, signed-commit checks, the scheduled loop | the platform's version history as the record; the curator's no-forge identity rule |
| An Obsidian vault as host | everything | - | open `knowledge_bundle` itself as a vault (below) |

## It pairs with ktl-librarian

The wrapper script the sidecar lays down resolves `ktl-librarian/SKILL.md` from the repository's skill directory. It checks `.claude/skills/` (Claude Code), then `.github/skills/` (Copilot-style agents), then `.agents/skills/` (a generic, tool-agnostic convention), then bare `skills/` (a repository that publishes the skills it also uses). Install **all four** skills, `ktl-sidecar`, `ktl-librarian`, `ktl-curator` and `ktl-docent`, into whichever of those the new repository uses. Each is a directory, `templates/` and `references/` included. If none of those directories fits, add the one you use to the wrapper's `candidate` list rather than leaving a fourth, unchecked convention. All four skills are generic: copy them unmodified, and the **librarian**'s first run discovers the project's knowledge sources itself.

Two copies of a skill in two of those directories drift: an installer updates one and not the other, and whichever an agent reads wins. The preflight compares every pair it finds and warns when they differ. Keep one, or reinstall both from the same release.

[`knowledge-trust-ladder`](https://github.com/noelmcloughlin/knowledge-trust-ladder) is the sole, canonical source of all four skills. Install from it with `gh skill install` or `npx skills add` rather than by copying files, and pin all four to the same release.

## Tooling

Validation uses [`uv`](https://docs.astral.sh/uv/) and the `lokf` PyPI package. [`just`](https://just.systems/) is optional: `uvx --from rust-just just` runs the same recipes. The files scaffold without them; only Step 4's validation needs them installed, and Step 4 gives the raw-schema fallback when Python is unavailable. Every script this skill lays down runs on bash 3.2 with POSIX tools, so macOS's stock shell and Git for Windows are covered. `mapfile`, `declare -A` and GNU-only flags are avoided for that reason.

The host copies of those scripts and workflows are meant to stay byte-identical to the templates they came from, so that a template fix reaches the host on the next sidecar repair. The preflight compares each host copy with the installed sidecar's template and warns on a difference. A host that edits a copy knowingly (a stricter checkout step, say) owns that copy from then on, and should say so where it documents its automation.

## The host need not be git, GitHub, or Linux

The scaffold is files, so any directory tree works: a local or shared filesystem, or storage mounted or synced locally (Drive, Dropbox, an S3 or blob mount, and the like). Find your case below.

### No git

`.lokf/.gitignore` and `.lokf/.gitattributes` are inert. Keep them, since version control may arrive later, or drop them. Skip the "commit" instructions, rely on the platform's own versioning or backup, and review changes by whatever mechanism the host offers instead of pull requests. Step 5 does not apply, except the preflight, which needs nothing. The **librarian** leaves `revision` out and hands off by pointing at the changed files. The **curator**'s identity is the account the platform's version history shows, and that history is the only thing that checks a confirmation; the curator's [portability.md](../../ktl-curator/references/portability.md) has the rule.

### Not GitHub: GitLab, Forgejo, Gitea, another forge, or none

Step 5's workflow files are GitHub Actions. What ports unchanged: the wrapper script (bash), the conventions and preflight scripts, and `lokf validate` as the gate. The `publish` job's own guards port too: the patch-scope check and the refusal of an added `by: human:` line, both plain shell.

What has to be rewritten is the two things that talk to GitHub:

- In the librarian workflow, the review pull request is opened with `actions/github-script`. On GitLab, open a merge request with `glab mr create` or the API, using a project access token with `api` scope; a job token cannot open one.
- In the registrar workflow, the `provenance` job reads reviews and commit verification through `gh api`. GitLab exposes the same facts as `GET /projects/:id/merge_requests/:iid/approvals` and `GET /projects/:id/repository/commits/:sha/signature`. Forgejo and Gitea expose them as the pull request's reviews and the commit's `verification` object.

One difference to carry over: GitHub forbids approving one's own pull request, and GitLab does so only when the project's *Prevent approval by author* setting is on. A port must therefore check that the approver is not the author instead of assuming it. Forgejo Actions runs GitHub Actions syntax, so the workflows may run nearly as they are there, with those two calls replaced. Where porting the gate is not worth it, the forge-free gate below needs no forge at all.

### Not Linux: Windows and PowerShell

Run the `justfile` recipes and the wrapper from a POSIX shell (on Windows, WSL or Git Bash), or bypass them and call `uv run lokf ...` directly; `uv` and the toolkit are cross-platform.

**From PowerShell**, every command the four skills give is a bash command. Run it through the bash that Git for Windows installs, which is not on PowerShell's path by default:

  ```powershell
  & "$env:ProgramFiles\Git\bin\bash.exe" -c "bash .lokf/scripts/knowledge-preflight.sh"
  # or, wherever git is installed:
  & (Join-Path (Split-Path -Parent (Get-Command git).Source) "..\bin\bash.exe") -c "bash .lokf/scripts/knowledge-conventions.sh knowledge"
  ```

Claude Code on Windows runs its commands through that bash already. A Copilot session whose terminal is PowerShell needs the line above. Where this skill's own Step 1 says `python3`, `uv run python` is the portable spelling, and `Get-FileHash -Algorithm SHA256` stands in for `sha256sum`.

Three Windows habits to know about:

- **Line endings.** Git for Windows checks files out with CRLF unless told otherwise. `.lokf/.gitattributes` (Step 1) tells it otherwise for the bundle, and the conventions script reads CRLF and a byte order mark the same as LF regardless, so a Windows checkout gives the verdict CI gives.
- **Path length.** Windows limits a path to 260 characters unless `git config core.longpaths true` is set; a deep bundle under a synced folder can reach it.
- **The doorway link.** Step 2's `knowledge_bundle` doorway is `ln -s` from a POSIX shell. On Windows prefer a junction, `mklink /J knowledge_bundle .lokf\knowledge`, which needs neither administrator rights nor Developer Mode, and which Obsidian follows exactly as it follows a symlink. `mklink /D` under Developer Mode makes a true symlink if one is wanted. A filesystem that supports neither (some FAT32 or exFAT volumes, older network mounts) skips it: the doorway is a convenience pointer, and every skill and toolkit command still addresses `.lokf/knowledge` directly.

### Synced or shared folders: OneDrive, SharePoint, Drive, Dropbox, iCloud

The sidecar syncs as ordinary files. Microsoft's restricted-name list for OneDrive and SharePoint has nothing against a leading dot, so `.lokf/knowledge` is the same real folder on every machine. OneDrive syncs neither symbolic links nor junctions, so the Step 2 doorway is the one per-machine piece. Recreate it after the first sync (`just lokf-link` from `.lokf/`, or the junction above), or open `.lokf/knowledge` by path. Git, unlike a sync client, carries the link itself.

A sync client does three things git does not, and each is caught:

- It resolves a concurrent edit by writing a **conflict copy** beside the file (`name-HOSTNAME.md`, `name (conflicted copy ...).md`, `name (1).md`). The copy validates and silently merges into the original in the graph; conventions rule 7 reports the duplicate `id` and rule 8 the name.
- A web editor may save with **CRLF or a byte order mark**; the scripts read through both and report the mark.
- A **case-insensitive** library cannot hold two paths differing only by case; rule 8 keeps every path lowercase.

With no git, the platform's version history is the record of who changed what, and the curator's [portability.md](../../ktl-curator/references/portability.md) says how an id is taken from it.

A team that wants the bundle synced under a visible name (a document library nobody reaches through git) may rearrange it by hand at the host root: `mv .lokf/knowledge knowledge_bundle && ln -s ../knowledge_bundle .lokf/knowledge`. On Windows: `mklink /J .lokf\knowledge %CD%\knowledge_bundle`, per machine. Every skill and recipe still addresses `.lokf/knowledge` and follows the link, the Step 5 templates name both paths, and the Obsidian plugins detect a top-level `knowledge_bundle/` on their own. Never do this inside an Obsidian vault; the next section says why.

### An Obsidian vault as host

Obsidian is optional; nothing in the skills needs it. The default layout is the right one: the person opens `knowledge_bundle` *itself* as a second vault (File → Open folder as vault) and installs the plugins there. Obsidian writes that vault's workspace state through the link into `.lokf/knowledge/.obsidian/`, which `templates/gitignore` excludes.

The host vault stays clean for two reasons. Obsidian never indexes a dot-folder. And its file reconciler (`reconcileSymbolicLinkCreation`, 1.13.7; the help page says the same in words) skips a link whose resolved path equals, contains or lies inside a folder it already watches, the vault root included. So a vault opened at the host root lists neither `.lokf/` nor `knowledge_bundle`.

A real folder inside the vault is indexed like any other, and so is a link whose target lies *outside* the vault. (A vault may link a repository's `.lokf/knowledge` into one of its folders and list it under the plugins' *Bundle root folders*.) Either way the exhibition enters the workshop's link suggestions, quick switcher, graph and search. *Settings → Files and links → Excluded files* only makes that less noticeable, and Obsidian Sync carries no links. Hence the rule: the bundle is never laid down as a real folder inside a vault.

## The forge-free gate

The `provenance` job needs GitHub. Where it cannot run (another forge, or no forge), or as a second opinion where it does, `templates/scripts/knowledge-provenance.sh` does the signature half of its work. It uses plain git and gpg, on any CI or by hand.

- **Who may confirm.** The repository carries one public key per curator id under `.lokf/curators/`: `<id>.asc` for GPG (`gpg --armor --export <key>`, subkeys included) or `<id>.pub` for SSH (the `ssh-keygen` public key file, one key per line). That directory is the machine-readable list of who may confirm: a key not there is not a curator, whatever the forge says. The id is the forge login the curator skill records, so the two gates name the same person.
- **What is checked.** For every commit in a range that adds or changes a `human:<id>` event under the bundle, a `verified` entry or the `generated` record, the script verifies the commit's signature against that id's key. Events are read whole from the frontmatter, against every parent of the commit, and keyed by the concept's `id`. So a re-dated `at`, a moved `revision` or a flow-style event counts, while a renamed concept, a merge that brings in another curator's confirmation, and an example in a body code fence do not. A GPG signature is checked with `git verify-commit` in a throwaway keyring, matched against every fingerprint the key file carries, since most keys sign with a subkey. An SSH signature is checked with `ssh-keygen -Y verify` (OpenSSH 8.2+) over the commit's own payload, with the id as the principal. Unsigned, signed by another key, by an expired or revoked key, by a key of the other kind, or an id with no key file: one finding each, and exit 1.
- **Keys land on their own.** A change that adds, alters or removes an id's key file and adds a confirmation *by that id* in the same range fails outright. So nobody registers a key and vouches with it in one step; a key lands in its own reviewed change first. Another curator's key landing beside a confirmation is fine.
- **What it proves** is the same as the GitHub job's signature route: that the holder of that key made that commit. It does not prove anyone read the source, and it says so.

Lay it down as Step 5 does the conventions script (`.lokf/scripts/knowledge-provenance.sh`, `chmod +x`), and run it in whatever CI the host has with the range `<base>..HEAD`. The preflight's `curators` line says how many keys are on file and whether the current machine's signing key is among them. So a curator learns before a session, not at the gate, that theirs is missing. The request to send is on [prerequisites.md](prerequisites.md).
