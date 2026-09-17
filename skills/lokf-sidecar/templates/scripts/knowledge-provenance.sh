#!/usr/bin/env bash
# The signature half of the registrar's provenance gate, with no forge.
#
# The GitHub `provenance` job asks GitHub whether the person named in a new
# `by: human:<id>` line approved the pull request or signed its commit. Off
# GitHub there is no such job, and on GitHub it is the only check. This
# script does the signature half anywhere git runs: the repository carries
# one public key per curator id under `.lokf/curators/` - `<id>.asc`, a GPG
# key as `gpg --armor --export` writes it, or `<id>.pub`, an OpenSSH public
# key as `ssh-keygen` writes it, one key per line - and every commit in a
# range that adds a `human:<id>` line under the bundle must be signed by a
# key on file for exactly that id. A GPG key counts with every subkey it
# carries, since most keys sign with a subkey; an SSH key is verified with
# `ssh-keygen -Y verify` (OpenSSH 8.2+) against the commit's own payload.
#
# Findings, one line each, exit 1:
#   - the commit is unsigned, or its signature does not verify;
#   - it is signed by a key other than the one on file for that id, or by a
#     key that has expired or been revoked;
#   - the id has no key on file (a stranger, or a curator not yet added);
#   - the range adds, changes or removes that id's own key file *and* adds a
#     confirmation by them - a key lands in its own reviewed change first, so
#     nobody registers a key and vouches with it in one step.
# No `.lokf/curators/` directory: says so and exits 0 - nothing to verify
# against, and the forge's gate, if any, is the only check.
#
# What a pass proves: the holder of that key made that commit. Not that
# anyone read the source, and not who the person is beyond what the key file's
# reviewed history says. Bash 3.2 and POSIX tools; needs git, and gpg or
# ssh-keygen for the kind of key on file.
#
# Usage: knowledge-provenance.sh <base-ref> [head-ref] [bundle-dir]
#   e.g. knowledge-provenance.sh origin/main            (a branch, locally)
#        knowledge-provenance.sh "$BASE_SHA" "$HEAD_SHA"  (in CI)
[ -n "${BASH_VERSION:-}" ] || { echo "run this with bash: bash ${0##*/} <base-ref> [head-ref]" >&2; exit 2; }
set -u

base="${1:-}"; head="${2:-HEAD}"; bundle="${3:-.lokf/knowledge}"
[ -n "$base" ] || { echo "usage: knowledge-provenance.sh <base-ref> [head-ref] [bundle-dir]" >&2; exit 2; }
command -v git >/dev/null 2>&1 || { echo "git is required" >&2; exit 2; }
root="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "not inside a git work tree" >&2; exit 2; }
cd "$root" || exit 2
curators=".lokf/curators"
if [ ! -d "$curators" ]; then
  echo "skipped - no $curators/ directory; nothing to verify confirmations against (the forge's gate, if any, is the only check)"
  exit 0
fi

fail=0
say() { echo "$1"; fail=1; }
have() { command -v "$1" >/dev/null 2>&1; }

# Throwaway keyring for the GPG keys on file, and a scratch directory for the
# SSH payloads and signatures, both gone on exit.
home="$(mktemp -d)"
trap 'rm -rf "$home"' EXIT
chmod 700 "$home"
gpg_ok=0
if have gpg; then
  gpg_ok=1
  for k in "$curators"/*.asc; do
    [ -f "$k" ] || continue
    GNUPGHOME="$home" gpg --batch --quiet --import "$k" 2>/dev/null || say "$k: not an importable armored public key"
  done
fi
gpg_fprs() {  # id -> every fingerprint in .lokf/curators/<id>.asc, primary and subkeys, one per line
  GNUPGHOME="$home" gpg --batch --quiet --with-colons --import-options show-only --import "$curators/$1.asc" 2>/dev/null \
    | awk -F: '$1=="fpr" {print $10}'
}
# ssh-keygen verifies a detached signature against an allowed-signers file
# naming the principal, so each id's .pub becomes `<id> namespaces="git" <key>`.
allowed_of() {  # id -> path of an allowed-signers file listing that id's keys
  awk -v id="$1" '$1 ~ /^(ssh-|ecdsa-|sk-)/ {print id " namespaces=\"git\" " $0}' "$curators/$1.pub" > "$home/$1.allowed"
  echo "$home/$1.allowed"
}
# A commit's signed payload is the object with its `gpgsig` header and that
# header's continuation lines removed; the signature is those lines unindented.
payload_of() {
  git cat-file commit "$1" | awk '
    BEGIN {hdr = 1}
    hdr && $0 == "" {hdr = 0}
    hdr && /^gpgsig(-sha256)? / {skip = 1; next}
    hdr && skip && /^ / {next}
    {skip = 0; print}'
}
signature_of() {
  git cat-file commit "$1" | awk '
    !done && /^gpgsig(-sha256)? / {insig = 1; sub(/^gpgsig(-sha256)? /, ""); print; next}
    insig && /^ / {sub(/^ /, ""); print; next}
    insig {insig = 0; done = 1}'
}
sig_format() {  # commit -> pgp | ssh | none
  case "$(git cat-file commit "$1" | grep -m1 -E '^gpgsig(-sha256)? ' || true)" in
    *"BEGIN PGP SIGNATURE"*) echo pgp ;;
    *"BEGIN SSH SIGNATURE"*) echo ssh ;;
    *) echo none ;;
  esac
}

# The range, oldest first, and the ids whose key file it adds, changes or
# removes: a confirmation by one of them in the same range fails outright.
commits="$(git rev-list --reverse "$base..$head" 2>/dev/null)" || { echo "cannot resolve $base..$head" >&2; exit 2; }
rekeyed=""
for sha in $commits; do
  for f in $(git diff-tree --no-commit-id --name-only -r "$sha" -- "$curators" 2>/dev/null); do
    f="${f##*/}"; rekeyed="$rekeyed ${f%.*}"
  done
done
rekeyed_said=""

checked=0
for sha in $commits; do
  # Every id the schema would accept (anything after `human:` up to a space
  # or quote), so an id this script cannot check is a finding, never a skip.
  ids="$(git show --format= --unified=0 "$sha" -- "$bundle" knowledge_bundle 2>/dev/null \
    | grep -E '^\+ *-? *by: *.?human:' | grep -oE "human:[^[:space:]\"']+" | sed 's/^human://' | sort -u)"
  [ -n "$ids" ] || continue
  short="$(git rev-parse --short "$sha")"
  format="$(sig_format "$sha")"
  status=""; signer=""
  if [ "$format" = pgp ] && [ "$gpg_ok" -eq 1 ]; then
    status="$(GNUPGHOME="$home" git verify-commit --raw "$sha" 2>&1 || true)"
    signer="$(printf '%s\n' "$status" | awk '/^\[GNUPG:\] VALIDSIG/ {print $3; exit}')"
  fi
  for id in $ids; do
    checked=$((checked + 1))
    # A forge login is letters, digits, '.', '_' and '-'; anything else names
    # nobody the gate can look up, and could name a path outside $curators.
    case "$id" in
      *[!A-Za-z0-9._-]*|[!A-Za-z0-9]*)
        say "$short adds a confirmation by human:$id, which is not a login this gate can check (letters, digits, . _ - only)"
        continue ;;
    esac
    has_asc=0; has_pub=0
    [ -f "$curators/$id.asc" ] && has_asc=1
    [ -f "$curators/$id.pub" ] && has_pub=1
    case " $rekeyed " in
      *" $id "*)
        case " $rekeyed_said " in *" $id "*) ;; *)
          rekeyed_said="$rekeyed_said $id"
          say "$base..$head adds or changes the key on file for human:$id and a confirmation by them in the same range - land the key in its own reviewed change first" ;;
        esac
        continue ;;
    esac
    if [ "$has_asc" -eq 0 ] && [ "$has_pub" -eq 0 ]; then
      say "$short adds a confirmation by human:$id, who has no key on file at $curators/$id.asc or $id.pub"
      continue
    fi
    case "$format" in
      none)
        say "$short adds a confirmation by human:$id but is unsigned" ;;
      pgp)
        if [ "$has_asc" -eq 0 ]; then
          say "$short adds a confirmation by human:$id with a GPG signature, but the key on file for them is an SSH key ($id.pub)"
        elif [ "$gpg_ok" -eq 0 ]; then
          say "$short adds a confirmation by human:$id with a GPG signature, and gpg is not installed here to verify it"
        elif printf '%s\n' "$status" | grep -qE '^\[GNUPG:\] (EXPKEYSIG|REVKEYSIG|EXPSIG)'; then
          say "$short adds a confirmation by human:$id signed by a key that has expired or been revoked"
        elif [ -z "$signer" ]; then
          unknown="$(printf '%s\n' "$status" | awk '/^\[GNUPG:\] NO_PUBKEY/ {print $3; exit}')"
          if [ -n "$unknown" ]; then
            say "$short adds a confirmation by human:$id but is signed by another key ($unknown, on file for nobody)"
          else
            say "$short adds a confirmation by human:$id but its signature does not verify (damaged, or made over different content)"
          fi
        elif ! gpg_fprs "$id" | grep -qx "$signer"; then
          say "$short adds a confirmation by human:$id but is signed by another key (${signer#"${signer%????????????????}"} is not in $id.asc)"
        fi ;;
      ssh)
        if [ "$has_pub" -eq 0 ]; then
          say "$short adds a confirmation by human:$id with an SSH signature, but the key on file for them is a GPG key ($id.asc)"
        elif ! have ssh-keygen; then
          say "$short adds a confirmation by human:$id with an SSH signature, and ssh-keygen is not installed here to verify it"
        else
          signature_of "$sha" > "$home/$sha.sig"
          if ! payload_of "$sha" | ssh-keygen -Y verify -f "$(allowed_of "$id")" -I "$id" -n git -s "$home/$sha.sig" >/dev/null 2>&1; then
            say "$short adds a confirmation by human:$id but its SSH signature is not by a key in $id.pub"
          fi
        fi ;;
    esac
  done
done

if [ "$fail" -eq 0 ]; then
  echo "OK - $checked confirmation(s) in $base..$head signed by the key on file for their curator"
fi
exit "$fail"
