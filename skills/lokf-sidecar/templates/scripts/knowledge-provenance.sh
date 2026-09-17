#!/usr/bin/env bash
# The signature half of the registrar's provenance gate, with no forge.
#
# The GitHub `provenance` job asks GitHub whether the person named in a new
# `by: human:<id>` line approved the pull request or signed its commit. Off
# GitHub there is no such job, and on GitHub it is the only check. This
# script does the signature half anywhere git and gpg run: the repository
# carries one armored public key per curator id under `.lokf/curators/<id>.asc`,
# and every commit in a range that adds a `human:<id>` line under the bundle
# must be signed by exactly that id's key.
#
# Findings, one line each, exit 1:
#   - the commit is unsigned, or its signature does not verify;
#   - it is signed by a key other than the one on file for that id;
#   - the id has no key on file (a stranger, or a curator not yet added);
#   - the range adds or changes a key file *and* adds a confirmation - a key
#     lands in its own reviewed change first, so nobody registers a key and
#     vouches with it in one step.
# SSH signatures are reported as unsupported for now; GPG ones are verified.
# No `.lokf/curators/` directory: says so and exits 0 - nothing to verify
# against, and the forge's gate, if any, is the only check.
#
# What a pass proves: the holder of that key made that commit. Not that
# anyone read the source, and not who the person is beyond what the key file's
# reviewed history says. Bash 3.2 and POSIX tools; needs git and gpg.
#
# Usage: knowledge-provenance.sh <base-ref> [head-ref] [bundle-dir]
#   e.g. knowledge-provenance.sh origin/main            (a branch, locally)
#        knowledge-provenance.sh "$BASE_SHA" "$HEAD_SHA"  (in CI)
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
command -v gpg >/dev/null 2>&1 || { echo "gpg is required to verify signatures" >&2; exit 2; }

fail=0
say() { echo "$1"; fail=1; }

# Throwaway keyring holding every curator key on file, and each id's
# fingerprint, so a signature can be matched to the id it claims.
home="$(mktemp -d)"
trap 'rm -rf "$home"' EXIT
chmod 700 "$home"
fpr_of() {  # id -> fingerprint of .lokf/curators/<id>.asc, or empty
  [ -f "$curators/$1.asc" ] || return 0
  GNUPGHOME="$home" gpg --batch --quiet --with-colons --import-options show-only --import "$curators/$1.asc" 2>/dev/null \
    | awk -F: '$1=="fpr" {print $10; exit}'
}
for k in "$curators"/*.asc; do
  [ -f "$k" ] || continue
  GNUPGHOME="$home" gpg --batch --quiet --import "$k" 2>/dev/null || say "$k: not an importable armored public key"
done

# The range, oldest first; the self-registration guard first of all.
commits="$(git rev-list --reverse "$base..$head" 2>/dev/null)" || { echo "cannot resolve $base..$head" >&2; exit 2; }
adds_key=0; adds_claim=0
for sha in $commits; do
  if [ -n "$(git diff-tree --no-commit-id --name-only -r "$sha" -- "$curators" 2>/dev/null)" ]; then adds_key=1; fi
  if git show --format= --unified=0 "$sha" -- "$bundle" knowledge_bundle 2>/dev/null | grep -qE '^\+ *-? *by: *.?human:'; then adds_claim=1; fi
done
if [ "$adds_key" -eq 1 ] && [ "$adds_claim" -eq 1 ]; then
  say "$base..$head adds or changes a curator key and a human: confirmation in the same range - land the key in its own reviewed change first"
fi

checked=0
for sha in $commits; do
  ids="$(git show --format= --unified=0 "$sha" -- "$bundle" knowledge_bundle 2>/dev/null \
    | grep -E '^\+ *-? *by: *.?human:' | grep -oE 'human:[A-Za-z0-9][A-Za-z0-9._-]*' | sed 's/^human://' | sort -u)"
  [ -n "$ids" ] || continue
  short="$(git rev-parse --short "$sha")"
  if git cat-file commit "$sha" | grep -qE '^gpgsig -----BEGIN SSH SIGNATURE-----'; then
    say "$short adds a human: confirmation with an SSH signature - not verified by this script yet (GPG keys only)"
    continue
  fi
  status="$(GNUPGHOME="$home" git verify-commit --raw "$sha" 2>&1 || true)"
  signer="$(printf '%s\n' "$status" | awk '/^\[GNUPG:\] VALIDSIG/ {print $3; exit}')"
  for id in $ids; do
    checked=$((checked + 1))
    expected="$(fpr_of "$id")"
    if [ -z "$expected" ]; then
      say "$short adds a confirmation by human:$id, who has no key on file at $curators/$id.asc"
    elif [ -z "$signer" ]; then
      say "$short adds a confirmation by human:$id but is unsigned, or its signature does not verify"
    elif [ "$signer" != "$expected" ]; then
      say "$short adds a confirmation by human:$id but is signed by another key (${signer#"${signer%????????????????}"}, not ${expected#"${expected%????????????????}"})"
    fi
  done
done

if [ "$fail" -eq 0 ]; then
  echo "OK - $checked confirmation(s) in $base..$head signed by the key on file for their curator"
fi
exit "$fail"
