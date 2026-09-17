# Signing your commits

A signature ties a commit to you cryptographically, so GitHub can show it `Verified`. In the LOKF repositories it is *required* for one thing: a pull request that adds a `by: human:` verification event to `.lokf/knowledge/`. The `provenance` job in each repository's `knowledge-registrar.yaml` checks those, because a claim that a named person checked a concept has to be tied back to that person, and it accepts either an approving review from the confirming account or a verified commit attributed to it. A sole maintainer cannot approve their own pull request, so for them the signature is the only path.

You are encouraged to sign everything. It costs one setup and nothing afterwards.

**Choose one format: GPG or SSH.** They are not interchangeable, and mixing them is the usual beginner failure - git reads `user.signingkey` in whichever format `gpg.format` names, so a file in the wrong format fails with `could not load public key`. If you have no preference, GPG is the one to pick: it carries an identity and an expiry of its own, which is what the sections below manage. Either way, the address in `git config user.email` must be a **verified email** on your GitHub account, or every commit stays `Unverified`.

## GPG, step by step

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

## SSH, step by step

Simpler, and reuses a key you may already have. The file must be a real SSH public key - one line starting `ssh-ed25519 AAAA...` - *not* a GPG export saved under an SSH-looking name.

```bash
ssh-keygen -t ed25519 -C "you@example.com"     # skip if ~/.ssh/id_ed25519 exists
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
cat ~/.ssh/id_ed25519.pub                      # paste this into GitHub
```

Add it at github.com/settings/keys under **SSH keys** → **New SSH key** → **Key type: Signing Key**. GitHub keeps authentication and signing keys in separate lists; a key registered only for auth leaves every commit `Unverified`, even though it is the same key.

## Renew a GPG key before it expires

Put a calendar reminder a month before the expiry date `gpg --list-secret-keys` shows. Renewing is routine maintenance and takes a minute:

```bash
gpg --quick-set-expire <fingerprint> 2y
gpg --armor --export <fingerprint>
```

Then, on github.com/settings/keys, **delete the old entry and add the exported key again** - GitHub stores the expiry from the copy you uploaded and does not re-read it, so this step is what actually renews it there.

Two things worth knowing so you renew calmly rather than in a panic:

- **Extending keeps the same key and fingerprint**, so past commits keep verifying and nothing else needs reconfiguring. Prefer it to making a new key.
- **An expiry is not a compromise.** GitHub still shows commits signed before the key expired as `Verified`. What an expired key stops is *new* signatures. So renew whenever you notice - but if the key is ever actually stolen, revoke it instead, and do not extend it.

## Put your key on file for the forge-free gate

A repository that runs `knowledge-provenance.sh` (lokf-sidecar Step 5) checks each confirmation's signature against a public key it carries under `.lokf/curators/`, named after your forge login. Export the key you sign with and open a pull request holding only that file - the gate refuses a change that lands a key and a confirmation by its holder together:

```bash
gpg --armor --export YOUR_KEY_ID > .lokf/curators/YOUR_LOGIN.asc   # GPG (subkeys travel with it)
cp ~/.ssh/id_ed25519.pub .lokf/curators/YOUR_LOGIN.pub               # SSH
```

One kind per login. When the key changes, replace the file in its own pull request the same way; a maintainer reviewing that change is what makes the key on file worth anything.

## If signing fails

- `could not load public key` - `gpg.format` does not match the key `user.signingkey` points at. Check the file is what its name implies: a GPG export begins `-----BEGIN PGP PUBLIC KEY BLOCK-----`, an SSH key begins `ssh-ed25519`.
- **No prompt appears and the commit fails** - GPG has nowhere to ask for your passphrase, common over SSH or in a terminal-less session. Add `export GPG_TTY=$(tty)` to your shell profile and open a new shell.
- **Signed locally but GitHub says `Unverified`** - the commit email is not a verified address on your account, or the key was added to the wrong list (auth instead of signing).
