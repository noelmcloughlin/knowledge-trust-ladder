# Contributing to LOKF Agent Skills

Thanks for your interest in improving `lokf-agent-skills`.

## Development setup

There is no build step - the skills are Markdown, YAML, and one shell script.

```bash
git clone https://github.com/noelmcloughlin/lokf-agent-skills.git
cd lokf-agent-skills
bash scripts/validate-repository.sh
```

To try a change end-to-end before publishing, install from your local clone instead of GitHub:

```bash
gh skill install ./lokf-agent-skills lokf-sidecar --from-local
# or:
npx skills add ./lokf-agent-skills --skill lokf-sidecar
```

## Layout

| Path | Responsibility |
| --- | --- |
| `skills/lokf-sidecar/SKILL.md` | One-shot bootstrap: creates `.lokf/` from `templates/`. Router only - see its `references/` for portability and automation detail. |
| `skills/lokf-sidecar/templates/` | Every file the sidecar skill writes, copied verbatim - never inlined into `SKILL.md`. |
| `skills/lokf-librarian/SKILL.md` | Day-to-day: scrape, build, audit, and hand off `.lokf/` concepts. Facts, never verdicts. |
| `skills/lokf-curator/SKILL.md` | A human curator's assistant: the trust/freshness report and the review session that records a person's Confirm / Wrong / Retire / Later as frontmatter. Verdicts, never facts. |
| `skills/lokf-docent/SKILL.md` | The reader's side: answer from the bundle first with each concept's trust label, fall back to the repository deliberately, and record misses/disagreements in `.lokf/feedback.md`. Read-only on the bundle. |
| `skills/*/references/*.md` | Detail loaded only when the router points to it - keeps each `SKILL.md` small. |
| `scripts/validate-repository.sh` | The repository-contract checks CI runs on every PR. |
| `scripts/smoke-test-install.sh` | Installs all four skills into a throwaway repo and asserts the result. CI runs this on every PR against the checked-out branch. |

## Before opening a pull request

- Run `bash scripts/validate-repository.sh` - checks all four `SKILL.md` files exist under the right names, frontmatter `name:` matches its directory, there's no stray duplicate `SKILL.md`, and every relative Markdown link under `skills/` still resolves.
- If you have the GitHub CLI installed, run `gh skill publish --dry-run` - this is the same Agent Skills spec check `validate.yml` runs in CI.
- If you changed a shell script, run `shellcheck` on it (CI runs this too).
- If you changed a workflow (here or under `skills/lokf-sidecar/templates/github/`), CI lints it with `actionlint` - a YAML parse alone won't catch a bad expression or context.
- If your change alters what either skill actually *does* (not just wording), add an entry under `[Unreleased]` in `CHANGELOG.md`.

## Editing scope

This repository packages and distributes the four skills; it does not second-guess their operational content on its own. If you're proposing a change to what an agent should actually do (a new Golden Rule interpretation, a different sidecar step, a new curator verb), explain the *why* in the PR and keep the role boundary intact: the librarian derives facts from the
repository and never vouches for them; the curator records a person's verdicts and never derives facts. A change that blurs that line needs a stronger argument than one that respects it.

## Release process

Releases are maintainer-gated via the `publish.yml` workflow (`workflow_dispatch`, not tag-triggered - see that file's header comment for why). All four skills always ship together under one tag, under one semantic version - `vMAJOR.MINOR.PATCH`:

- **Patch** - corrections that don't materially change expected behavior.
- **Minor** - backward-compatible additions or broader supported workflows.
- **Major** - breaking changes to behavior, structure, assumptions, or interoperability.

The version itself is no longer hand-picked. Write `## [Unreleased]` in `CHANGELOG.md` as you go, describing what changed with a [Conventional Commits](https://www.conventionalcommits.org/) type (`feat:`, `fix:`, `security:` for a patch, `BREAKING CHANGE:` in a footer, or `!` after the type, for a major). **Only those types cut a release**: `docs:`, `chore:`, `refactor:`, `style:` and `test:` deliberately do not, so a branch carrying only those merges cleanly, releases nothing, and leaves its `## [Unreleased]` entries to ship with the next release that does. Type the commit for what the change *is* - a skill whose behaviour changed is a `feat:` even when most of the diff is prose - and never promote the changelog by hand: that is `semantic-release.yml`'s job, and an already-promoted section leaves `## [Unreleased]` empty, which the `check` step then refuses. Once a PR merges to `main`, [`semantic-release.yml`](.github/workflows/semantic-release.yml) computes the next version from the commits since the last tag, refuses to proceed if `## [Unreleased]` is empty, retitles it to `## [X.Y.Z] - YYYY-MM-DD` with a fresh empty section above it, and commits that - but stops there. It never tags: `gh skill publish` is this repository's one tag creator (see `publish.yml`'s header comment for why two tools racing to create the same tag would be worse than either alone), so a maintainer still runs `publish.yml` by hand with the version to ship. That workflow now cross-checks the typed version against what `semantic-release.yml` already promoted, so a transcription error is caught before anything reaches the registry.

Both `semantic-release.yml`'s `release` job and `publish.yml` sit behind the `release` GitHub Environment - **configure required reviewers on it once, in this repository's Settings → Environments**, or a qualifying merge promotes the changelog unattended (publishing to the registry still needs the separate, explicit `workflow_dispatch`).

### What the repository settings mean for you

Three of them are worth knowing because they explain what a pull request waits on, or refuses:

- **Changes reach `main` by pull request, but the rule is not enforced by a ruleset.** A ruleset that requires pull requests rejects every direct push, and the release job's own push - the changelog promotion - cannot be exempted from it: a ruleset bypass list accepts roles, teams, GitHub Apps and Dependabot, and `github-actions[bot]` is none of those. So the pull-request discipline here is a convention, held to by the maintainer, not a gate. Open one anyway.
- **Sign your commits.** Required only for a pull request that records a human confirmation; worth doing on all of them. See [Signing your commits](#signing-your-commits) below.
- **"Require signed commits" as a branch rule is deliberately off**, and must stay off. A `git commit` made inside a runner is unsigned; GitHub only auto-signs commits made through the web UI or API. Turning the rule on would reject the release job's own changelog promotion and break every release. The bullet above is the substitute, applied where it works.

### Signing your commits

A signature ties a commit to you cryptographically, so GitHub can show it `Verified`. Only pull requests that add a `by: human:` verification event to `.lokf/knowledge/` *require* one - the [`provenance`](.github/workflows/knowledge-registrar.yaml) job checks those, because a claim that a named person checked a concept has to be tied back to that person, and it accepts either an approving review from the confirming account or a verified commit attributed to it. A sole maintainer cannot approve their own pull request, so for them the signature is the only path.

You are encouraged to sign everything. It costs one setup and nothing afterwards.

**Choose one format: GPG or SSH.** They are not interchangeable, and mixing them is the usual beginner failure - git reads `user.signingkey` in whichever format `gpg.format` names, so a file in the wrong format fails with `could not load public key`. If you have no preference, GPG is the one to pick: it carries an identity and an expiry of its own, which is what the paragraphs below manage. Either way, the address in `git config user.email` must be a **verified email** on your GitHub account, or every commit stays `Unverified`.

#### GPG, step by step

The key lives in `~/.gnupg/`. You never save it to a file of your own - exporting prints it to the screen for pasting.

1. **Create it.** Choose `ECC (sign only)` with `Curve 25519`, and an expiry of 1-2 years rather than `0` (never expires): an expiry limits the damage if the key is ever lost, and extending it later is one command.

   ```bash
   gpg --full-generate-key
   ```

2. **Set a passphrase, and record it in your password manager as you type it.** There is no recovery: a forgotten passphrase means the key is dead and you start again.

3. **Find the fingerprint** - the 40-character string on the line under `sec`:

   ```bash
   gpg --list-secret-keys --keyid-format=long
   ```

4. **Point git at it:**

   ```bash
   git config --global gpg.format openpgp
   git config --global user.signingkey <fingerprint>
   git config --global commit.gpgsign true
   ```

5. **Give the public half to GitHub.** Copy the whole block, `BEGIN`/`END` lines included, and paste it at github.com/settings/keys → **New GPG key**:

   ```bash
   gpg --armor --export <fingerprint>
   ```

6. **Test it.** Make any commit, then:

   ```bash
   git log --show-signature -1
   ```

   You want `gpg: Good signature from ...`. GitHub's own verdict is the `Verified` badge next to the commit once pushed.

7. **Optional, but it removes most of the friction:** cache the passphrase for the working day instead of being asked every commit. Put this in `~/.gnupg/gpg-agent.conf`, then run `gpgconf --reload gpg-agent`:

   ```text
   default-cache-ttl 28800
   max-cache-ttl 86400
   ```

#### SSH, step by step

Simpler, and reuses a key you may already have. The file must be a real SSH public key - one line starting `ssh-ed25519 AAAA...` - *not* a GPG export saved under an SSH-looking name.

```bash
ssh-keygen -t ed25519 -C "you@example.com"     # skip if ~/.ssh/id_ed25519 exists
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
cat ~/.ssh/id_ed25519.pub                      # paste this into GitHub
```

Add it at github.com/settings/keys under **SSH keys** → **New SSH key** → **Key type: Signing Key**. GitHub keeps authentication and signing keys in separate lists; a key registered only for auth leaves every commit `Unverified`, even though it is the same key.

#### Renew a GPG key before it expires

Put a calendar reminder a month before the expiry date `gpg --list-secret-keys` shows. Renewing is routine maintenance and takes a minute:

```bash
gpg --quick-set-expire <fingerprint> 2y
gpg --armor --export <fingerprint>
```

Then, on github.com/settings/keys, **delete the old entry and add the exported key again** - GitHub stores the expiry from the copy you uploaded and does not re-read it, so this step is what actually renews it there.

Two things worth knowing so you renew calmly rather than in a panic:

- **Extending keeps the same key and fingerprint**, so past commits keep verifying and nothing else needs reconfiguring. Prefer it to making a new key.
- **An expiry is not a compromise.** GitHub still shows commits signed before the key expired as `Verified`. What an expired key stops is *new* signatures. So renew whenever you notice - but if the key is ever actually stolen, revoke it instead, and do not extend it.

#### If signing fails

- `could not load public key` - `gpg.format` does not match the key `user.signingkey` points at. Check the file is what its name implies: a GPG export begins `-----BEGIN PGP PUBLIC KEY BLOCK-----`, an SSH key begins `ssh-ed25519`.
- **No prompt appears and the commit fails** - GPG has nowhere to ask for your passphrase, common over SSH or in a terminal-less session. Add `export GPG_TTY=$(tty)` to your shell profile and open a new shell.
- **Signed locally but GitHub says `Unverified`** - the commit email is not a verified address on your account, or the key was added to the wrong list (auth instead of signing).
