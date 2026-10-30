# Portability: reusing the KTL skills on another host

The skills are repository-agnostic. Run them in any directory tree, including an empty one. The bundle is the same on every host: `.lokf/knowledge/`, one Markdown file per concept, validated by the same toolkit. What varies is the shell, the version control, the forge (GitHub, GitLab, Codeberg, Forgejo, Gitea, or none), and what each of the four skills can do there.

**Run the preflight first.** Before the sidecar exists, run `bash <skill>/templates/scripts/knowledge-preflight.sh` from the repository's root, where `<skill>` is ktl-sidecar's directory. Afterwards, run `.lokf/scripts/knowledge-preflight.sh`. Its last line names your case, and the matching section below says what to do. If a line names something you cannot fix yourself, [prerequisites.md](prerequisites.md) says who can, and what to send them.

| Host | Works | Lost | Substitute |
| --- | --- | --- | --- |
| Linux, git, GitHub | everything | - | - |
| macOS | everything, on the stock bash 3.2 | `sha256sum` | `shasum -a 256` |
| Windows, Git for Windows | everything from its bash | the `ln -s` doorway | a junction (below) |
| Windows, PowerShell | the toolkit, git, the plugins | every script and command, which are bash | run them through Git for Windows' bash (below) |
| GitLab, Codeberg, Forgejo, Gitea | the sidecar, librarian, docent; the curator with `glab` or the signing-key route | the GitHub Actions workflows, ktl-website's deploy included | the wrapper in that CI, the gate ported per the recipe below, or the forge-free gate |
| No forge, git only | everything local | the gate, pull requests, the scheduled loop | review by the host's own mechanism; the forge-free gate for confirmations |
| No git (a synced or shared folder) | the bundle, validation, all four skills' reading | `revision`, the gate, signed-commit checks, the scheduled loop | the platform's version history as the record; the curator's no-forge identity rule |
| Behind a package mirror or a proxy, or python3 older than 3.9 | everything | `uv run` of the sidecar's scripts; python3 for any script | `.lokf/.venv` after `uv sync`; a lock made where the gate installs from; uv told to trust the proxy's certificate; `uv run` for ktl-prose's check (below) |
| An Obsidian vault as host | everything | - | open `knowledge_bundle` itself as a vault (below) |
| Microsoft 365 Copilot (declarative agent) | the docent, from a snapshot of the bundle; the auditor once it exists | the other three skills, source checks, `feedback.md` | the `ktl-docent-m365-<tag>-<repository>.zip` a release carries, or `.lokf/m365/knowledge-m365.sh` on the bundle folder ([m365.md](m365.md)) |

## Install all four skills together

Install **all four** skills, `ktl-sidecar`, `ktl-librarian`, `ktl-curator` and `ktl-docent`, into one skill directory: `.claude/skills/` (Claude Code), `.github/skills/` (Copilot-style agents), `.agents/skills/` (a generic, tool-agnostic convention) or bare `skills/` (a repository that publishes the skills it also uses). Those are the directories the wrapper script searches for `ktl-librarian/SKILL.md`, in that order; any other directory goes into its `candidate` list ([automation.md](automation.md)). Each skill is a directory, `templates/` and `references/` included, and all four are generic: copy them unmodified, and the **librarian**'s first run discovers the project's knowledge sources itself.

A skill installed for one user, under `~/.copilot/skills/`, `~/.claude/skills/` or `~/.agents/skills/`, serves that user's live sessions. The preflight lists it, but the scheduled librarian runs on a fresh runner and needs a copy in the repository.

Two copies of a skill in two of those directories drift: an installer updates one and not the other, and whichever an agent reads wins. The preflight compares every pair it finds and warns when they differ. Keep one, or reinstall both from the same release.

[`knowledge-trust-ladder`](https://github.com/noelmcloughlin/knowledge-trust-ladder) is the sole, canonical source of all four skills. Install from it with `gh skill install` or `npx skills add` rather than by copying files, and pin all four to the same release.

## Tooling

Validation uses [`uv`](https://docs.astral.sh/uv/) and the `lokf` PyPI package. [`just`](https://just.systems/) is optional: `uv sync` installs the version `uv.lock` pins, and `uv run just` runs the same recipes. The files scaffold without them; only Step 4's validation needs them installed, and Step 4 gives the raw-schema fallback when Python is unavailable. Every script this skill installs runs on bash 3.2 with POSIX tools, so macOS's stock shell and Git for Windows are covered. `mapfile`, `declare -A` and GNU-only flags are avoided for that reason.

The host copies of those scripts and workflows are meant to stay byte-identical to the templates they came from, so that a template fix reaches the host on the next sidecar repair. The preflight compares each host copy with the installed sidecar's template and warns on a difference. A host that edits a copy knowingly (a stricter checkout step, say) owns that copy from then on, and should say so where it documents its automation.

## What is tested before a release, and what stays yours

The skills repository tests every script and workflow under `templates/` before a release. Its `tests/` run each one on throwaway bundles and repositories, with the toolkit version the templates lock. Its contract script holds its own copies byte-identical to the templates, and holds the two hand-kept lists to the LOKF schema: the classes a concept may name, and the relation fields the report counts. A host whose copies are as the sidecar laid them down inherits that testing and need not test the templates again. Three things stay with the host:

- **A copy the host edited.** The preflight reports it as drift. From then on the host owns that copy, and any test of it.
- **A port.** The gate ported to another forge by the recipe below, or a step rewritten for another shell, is the host's, with its tests.
- **Another operating system.** The tests run on Linux. The scripts are written for bash 3.2 and POSIX tools, so macOS and Git for Windows are covered by design and not by a run there. Run the preflight and the conventions check once on such a host, and report a difference as an issue on the skills repository.

No test can prove that an agent follows a `SKILL.md`. The trust labels, the gate and the curator's verdicts guard against that, and they are the same on every host.

## The host need not be git, GitHub, or Linux

The scaffold is files, so any directory tree works: a local or shared filesystem, or storage mounted or synced locally (Drive, Dropbox, an S3 or blob mount, and the like). Find your case below.

### No git

`.lokf/.gitignore` and `.lokf/.gitattributes` are inert. Keep them, since version control may arrive later, or drop them. Skip the "commit" instructions, rely on the platform's own versioning or backup, and review changes by whatever mechanism the host offers instead of pull requests. Step 5 does not apply, except the preflight and `knowledge-feedback.sh`, which need nothing. The **librarian** leaves `revision` out and hands off by pointing at the changed files. The **curator**'s identity is the account the platform's version history shows, and that history is the only thing that checks a confirmation; the curator's [portability.md](../../ktl-curator/references/portability.md) has the rule. A SharePoint or OneDrive workspace whose curators sign in to Microsoft 365 would need an identity of its own, which the curator's [domain-schemas.md](../../ktl-curator/references/domain-schemas.md) records as a shape held in reserve.

### Not GitHub: GitLab, Codeberg, Forgejo, Gitea, another forge, or none

Step 5's workflow files are GitHub Actions. What ports unchanged: the wrapper script (bash), the conventions and preflight scripts, and `lokf validate` as the gate. The `publish` job's own guards port too: the patch-scope check and the refusal of an added `by: human:` line, both plain shell.

What has to be rewritten is what talks to GitHub:

- In the librarian workflow, the review pull request is opened with `actions/github-script`. On GitLab, open a merge request with `glab mr create` or the API, using a project access token with `api` scope; a job token cannot open one.
- In the registrar workflow, the `provenance` job reads reviews and commit verification through `gh api`. GitLab exposes the same facts as `GET /projects/:id/merge_requests/:iid/approvals` and `GET /projects/:id/repository/commits/:sha/signature`. Forgejo, which Codeberg runs, and Gitea expose them as the pull request's reviews and the commit's `verification` object.
- The release workflow uploads the zip with `gh release upload` and records a GitHub attestation. On another forge, attach the zip through that forge's release API, or skip the workflow; the bundle is in git either way.

One difference to carry over: GitHub forbids approving one's own pull request, and GitLab does so only when the project's *Prevent approval by author* setting is on. A port must therefore check that the approver is not the author instead of assuming it. Forgejo Actions, on Codeberg among other hosts, and Gitea Actions run GitHub Actions syntax, so the workflows may run nearly as they are there, with those calls replaced. Where porting the gate is not worth it, the forge-free gate below needs no forge.

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

### Behind a package mirror or proxy, or with an old python3

A company package index, such as Nexus or Artifactory, often serves no upload times. `uv sync` in `.lokf/` still installs the toolkit: it resolves the same versions through the mirror, and rewrites every address in `uv.lock` to the mirror's. There uv drops every file it cannot date. So the pen, the conventions check and the ingest lift `exclude-newer` for each package uv names that the script pins, keep its version, and say so. Run `uv sync` in `.lokf/` once to run them from `.lokf/.venv`, which `uv.lock` pins by hash. The ingest reads a PDF with pypdf, which the toolkit does not install. Run `uv add pypdf` in `.lokf/` to add it. When the conventions check exits 2 and says "could not run", the runner failed, not the bundle.

Make the lock where the gate installs from. `.lokf/uv.lock` records the index it was made against, and every file's address there. A lock made against PyPI fails the gate's `uv sync --locked` on a runner whose index is a mirror. A lock rewritten behind the mirror fails on GitHub's own runners, and names the mirror's host in the repository. So commit a lock made against PyPI where GitHub's runners run the gate, and one made against the mirror where the runners install through it. The preflight's `lock` line says when the two differ.

A proxy that inspects TLS signs traffic with the company's own root certificate. Once that is in the system's store, git and curl trust it. uv trusts its own bundled roots until `UV_SYSTEM_CERTS=true` is set (uv 0.11 or later; `UV_NATIVE_TLS=1` before that). `SSL_CERT_FILE` serves too, when it names the system's bundle, such as `/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem` on RHEL. `UV_DEFAULT_INDEX` names the mirror, and git, curl and uv all read `HTTPS_PROXY`.

Every script needs Python 3.9 or later. Where python3 is older, as RHEL 8's 3.6 is, the preflight warns. Run each sidecar script through its `.sh` half, which chooses the interpreter, and ktl-prose's check through `uv run`. Never run a script with bare `python`, which is Python 2 on some hosts, except as last resort.

### Synced or shared folders: OneDrive, SharePoint, Drive, Dropbox, iCloud

The sidecar syncs as ordinary files. Microsoft's restricted-name list for OneDrive and SharePoint has nothing against a leading dot, so `.lokf/knowledge` is the same real folder on every machine. OneDrive syncs neither symbolic links nor junctions, so the Step 2 doorway is the one per-machine piece. Recreate it after the first sync (`just lokf-link` from `.lokf/`, or the junction above), or open `.lokf/knowledge` by path. Git, unlike a sync client, carries the link itself.

A sync client does three things git does not, and each is caught:

- It resolves a concurrent edit by writing a **conflict copy** beside the file (`name-HOSTNAME.md`, `name (conflicted copy ...).md`, `name (1).md`). The copy validates and silently merges into the original in the graph; conventions rule 7 reports the duplicate `id` and rule 8 the name.
- A web editor may save with **CRLF or a byte order mark**; the scripts read through both and report the mark.
- A **case-insensitive** library cannot hold two paths differing only by case; rule 8 keeps every path lowercase.

A team that wants the bundle synced under a visible name (a document library nobody reaches through git) may rearrange it by hand at the host root: `mv .lokf/knowledge knowledge_bundle && ln -s ../knowledge_bundle .lokf/knowledge`. On Windows: `mklink /J .lokf\knowledge %CD%\knowledge_bundle`, per machine. Every skill and recipe still addresses `.lokf/knowledge` and follows the link, the Step 5 templates name both paths, and the Obsidian plugins detect a top-level `knowledge_bundle/` on their own. Never do this inside an Obsidian vault; the next section says why.

### An Obsidian vault as host

Obsidian is optional; nothing in the skills needs it. The default layout is the right one: the person opens `knowledge_bundle` *itself* as a second vault (File → Open folder as vault) and installs the plugins there. Obsidian writes that vault's workspace state through the link into `.lokf/knowledge/.obsidian/`, which `templates/gitignore` excludes.

The host vault stays clean for two reasons. Obsidian never indexes a dot-folder. And its file reconciler (`reconcileSymbolicLinkCreation`, 1.13.7; the help page says the same in words) skips a link whose resolved path equals, contains or lies inside a folder it already watches, the vault root included. So a vault opened at the host root lists neither `.lokf/` nor `knowledge_bundle`.

A real folder inside the vault is indexed like any other, and so is a link whose target lies *outside* the vault. (A vault may link a repository's `.lokf/knowledge` into one of its folders and list it under the plugins' *Bundle root folders*.) Either way the exhibition enters the workshop's link suggestions, quick switcher, graph and search. *Settings → Files and links → Excluded files* hides it from search, graph view and unlinked mentions, but only makes it less noticeable in the quick switcher and link suggestions ([Obsidian's settings help](https://obsidian.md/help/settings)), and Obsidian Sync carries no links. Hence the rule: the bundle is never placed as a real folder inside a vault.

### The ingest on another host

`knowledge-ingest.sh` is bash and Python, and runs wherever `uv` or `python3` with PyYAML does. Without git it runs by hand, with the credentials in the environment, and the lock is the record of what was fetched. The `command` kind then takes any file under the root, since no git can say whether it is tracked. Its lock record, its mirror's header and the run's summary then carry `command_unchecked` with the reason, so a lock copied into a repository does not pass for a checked run's. On a forge other than GitHub, schedule the script in that CI with the secrets it names, pass `--visibility`, and open the merge request from the branch it leaves, as the sync's recipe above does for its workflow.

## The forge-free gate

Where the `provenance` job cannot run (another forge, or none), and as a second opinion where it does, `knowledge-provenance.sh` checks each confirmation's signature against a public key the repository carries for that curator under `.lokf/curators/`. It needs plain git and gpg or ssh-keygen, and runs on any CI or by hand. That directory is then the machine-readable list of who may confirm. [gate.md](gate.md) has what it checks, what fails, and how to lay it down. The preflight's `curators` line says whether your own key is on file, and [prerequisites.md](prerequisites.md) has the request to send if it is not.
