# Portability - what this skill loses on each host, and the substitute

Run `.lokf/scripts/knowledge-preflight.sh` first; its summary line says which of these cases applies. The bundle, the concepts and `lokf validate` are the same everywhere. What varies is provenance, the hand-off and the scheduled loop.

| Host | Lost | Substitute |
| --- | --- | --- |
| No git (a synced or shared folder, a plain directory) | `revision` on `generated`, the gate, pull requests, the scheduled loop, conventions rule 6 | leave `revision` out; hand over the validate output and the changed files; the platform's version history is the record of who changed what |
| `.lokf/` gitignored | the gate, pull requests, the scheduled loop | the same hand-off; the bundle is still validated locally |
| GitLab, Forgejo, Gitea | the two GitHub Actions workflows | the wrapper script is plain bash: schedule it in that CI and open the merge request there - the recipe is in lokf-sidecar's [portability.md](../../lokf-sidecar/references/portability.md) |
| Windows | nothing, from Git for Windows' bash | from PowerShell, run every command here through that bash (launch line in the same page); write `uv run python` where this skill says `python3` |
| macOS | `sha256sum` | `shasum -a 256` |
| No `uv` | `lokf validate`, `convert`, `query`, `lokf-check-refs` | the manual schema cross-check in section 2, reported as such - a bundle that has only passed it is not proven schema-valid |
| Synced folder (OneDrive, SharePoint, Drive, Dropbox, iCloud) | nothing in the bundle | a conflict copy shares its original's `id`: conventions rule 7 reports it, rule 8 its name; delete the copy after reading it. Files On-Demand placeholders download on first read, so the first refresh is slow, not broken |

Three rules that hold on every host:

- **Lowercase paths.** The path is the concept's id, and two paths differing only by case collide on Windows, macOS and SharePoint. Name files and directories in a-z, 0-9 and hyphens; the gate rejects anything else (conventions rule 8).
- **LF line endings.** The sidecar's `.lokf/.gitattributes` keeps a tracked bundle on LF. Without git, an editor that writes CRLF or a byte order mark is tolerated by the conventions script and `lokf validate`, and the mark is reported (rule 9) because other readers do not strip it.
- **The version check.** `uvx --from pip pip index versions lokf` works wherever `uv` does; `uv pip` has no `index` subcommand. Offline, PyPI's JSON is unreachable too: skip the check and say so in the hand-off.

The identity behind a `human:` event is the curator's concern, not this skill's; this skill never writes one.
