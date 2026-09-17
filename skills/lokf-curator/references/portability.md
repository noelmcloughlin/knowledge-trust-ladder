# Portability - who is recording, and what checks it, on each host

The rule never changes: a `human:<id>` event carries an id that something outside the bundle can independently confirm, and this skill writes one only for an answer that person gave to that item. What changes from host to host is where the id comes from and what checks it afterwards. The preflight (`.lokf/scripts/knowledge-preflight.sh`) names the host, the forge and the identity it could resolve; this page is the rule for each case.

| Host | Where the id comes from | What checks a confirmation afterwards |
| --- | --- | --- |
| GitHub | `gh api user --jq .login`; or the signing-key route below | the `provenance` job: an approving review by that account, or its verified signature on the commit |
| GitLab | `glab api user` (the `username` field); or the signing-key route | no template ships; the recipe is in lokf-sidecar's [portability.md](../../lokf-sidecar/references/portability.md) |
| Forgejo, Gitea, Codeberg | the signing-key route, with a token where the key listing needs one | same: no template, recipe there |
| Another forge, Bitbucket included | the signing-key route if the forge lists keys; else no *Confirm* | untested; the forge-free gate below is the safe choice |
| No forge: a synced or shared folder, a plain directory | the account the platform's version history attributes the save to | that version history, and nothing else |
| `.lokf/` gitignored | as the forge above, but nothing will ever check it | nothing; say so in the report |

## The signing-key route

For a forge with no CLI at hand, or a forge this skill has no CLI for. It binds a claimed login to possession of a key, which is the same fact the gate relies on later.

1. Read the key the person signs with: `git config user.signingkey`. For GPG that is a key id, and the key that actually signs is often a *subkey* of it - `gpg --list-keys --with-subkey-fingerprints <id>` shows both; for SSH (`gpg.format ssh`) a public key file or its contents. No value with signing on means git picks the GPG key by the committer's email; `git log -1 --format=%GK` after a signed commit names the key it used.
2. The person states their login. On its own that is a claim, as this skill says elsewhere.
3. Fetch the forge's public key listing for that login and look for that key. GitHub: `https://api.github.com/users/<login>/gpg_keys` (match `key_id`, or a `subkeys[].key_id`) or `/users/<login>/ssh_signing_keys` (match the key line). GitLab: `https://<host>/api/v4/users?username=<login>` for the id, then `/api/v4/users/<id>/gpg_keys` or `/users/<id>/keys`. Forgejo and Gitea: `/api/v1/users/<login>/gpg_keys` and `/users/<login>/keys`, which some instances (Codeberg among them) serve only with a token. All of it needs `curl`; the preflight's `network` line says when there is none.
4. Only when the key is listed under that login, record `human:<login>`. If it is not listed, or the listing cannot be read, *Confirm* and *Correct now* stay unavailable: say so, and offer the three verbs that assert nothing.

The commit the person then makes is signed with that key, or fails: with `commit.gpgsign` on, a session cannot leave an unsigned claim behind. The gate, where one runs, verifies the same signature against the same account.

## No forge

A synced folder (SharePoint, OneDrive, Drive, Dropbox, iCloud) or a plain directory has no gate and no signatures. The platform's version history is the only record of who saved what, so the id is the account that history shows for this person, written as a handle, never an email (the bundle may be public): the local part of a work account, or the handle the platform displays. Say in the report, every time, that confirmations here rest on the platform's version history, not on a gate; and skip the *Not tied to a signed commit* check, saying so rather than reporting zero, as [trust-fields.md](trust-fields.md) already requires.

## The forge-free gate

Where no gate runs, or as a second opinion where one does, lokf-sidecar can lay down `knowledge-provenance.sh` beside the conventions script: it verifies the signature on every commit that adds or changes a `human:<id>` event - a `verified` entry, or the `generated` record Correct writes - against a public key the repository carries for that id under `.lokf/curators/` - GPG as `<id>.asc`, SSH as `<id>.pub` - with plain git and gpg or ssh-keygen, on any CI or by hand. Its rules, and the guard that stops a change adding an id's key and their confirmation together, are in lokf-sidecar's [portability.md](../../lokf-sidecar/references/portability.md). The preflight's `curators` line says whether this person's key is on file; when it is not, the Step 1 readiness line says so, and the request to send an administrator is on lokf-sidecar's [prerequisites.md](../../lokf-sidecar/references/prerequisites.md).

## Shells and tools

- **Windows.** The git checks in [trust-fields.md](trust-fields.md) are shell pipelines; run them from Git for Windows' bash (Claude Code on Windows already does; from PowerShell, the launch line is in lokf-sidecar's [portability.md](../../lokf-sidecar/references/portability.md)). `Get-FileHash -Algorithm SHA256` is the PowerShell digest.
- **macOS.** `sha256sum` is not installed by default; `shasum -a 256` is, and every place this skill names one accepts the other.
- **No `uv`.** `just lokf-validate` after a session is skipped and said so; the frontmatter edits are still exact.
- **CRLF, byte order marks, sync conflict copies.** The conventions script the gate runs reads through the first two and reports the third as a duplicate `id`; run it before handing off, as the librarian does.
