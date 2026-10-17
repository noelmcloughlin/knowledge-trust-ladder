#!/usr/bin/env bash
# Bring sibling repositories' sidecar copies and skills pins up to one release
# of this repository, each on a branch of its own, and finish the branches
# once their pull requests are merged.
#
# The sync itself is skills/ktl-sidecar/templates/scripts/knowledge-sync.sh,
# a template every sibling carries as .lokf/scripts/knowledge-sync.sh. That
# script's header says what a sync copies, adds and refuses, and why the
# copies and the pin move together from one tag. It reads what to sync out
# of the release's knowledge-sync.manifest, so the release is data to it.
# This script runs each sibling's own copy, as the sibling's workflow does,
# and the tag's copy in a sibling that has none yet. A sibling's own
# knowledge-sync.yaml workflow does the same on a schedule; this script is
# for the day of the release, and for a sibling with no workflow.
#
# Usage: scripts/sync-sidecar.sh [--commit | --push | --pr] [--no-checks] [--source <dir>] <tag> <sibling-dir>...
#        scripts/sync-sidecar.sh --finish <tag> <sibling-dir>...
#   scripts/sync-sidecar.sh --pr v0.47.0 ../obsidian-ktl-registrar ../obsidian-ktl-curator
#
#   --commit   commit each sibling's sync on its sync-<tag> branch
#   --push     --commit, then push the branch to the sibling's origin
#   --pr       --push, then open the pull request with gh, from the
#              sibling's .github/PULL_REQUEST_TEMPLATE/knowledge-sync.md
#   --no-checks  skip the sidecar's checks in each sibling
#   --source <dir>  read the tag from another clone of this repository
#   --finish   after the pull requests are merged: in each sibling, go back
#              to the default branch, bring it up to date, and delete the
#              sync-<tag> branch. A branch whose remote branch still exists,
#              or that was never pushed, is kept and reported.
#
# Without --commit the sync is left uncommitted on the branch, with the
# commit command printed, and the diff is the review. Exit 1 when a sibling
# was skipped or a check failed there; exit 2 when the arguments are wrong
# or the tag is not usable.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
sync_template="skills/ktl-sidecar/templates/scripts/knowledge-sync.sh"
manifest_template="skills/ktl-sidecar/templates/knowledge-sync.manifest"

usage() {
  sed -n '/^# Usage:/,/^# Without --commit/p' "$0" | sed -e '$d' -e 's/^# \{0,1\}//' >&2
  exit 2
}

flags=(); finish=0; source="$repo_root"; tag=""; siblings=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --commit|--push|--pr|--no-checks) flags+=("$1"); shift ;;
    --finish) finish=1; shift ;;
    --source) [[ $# -ge 2 ]] || usage; source="$2"; shift 2 ;;
    -h|--help) usage ;;
    -*) echo "sync-sidecar: unknown option $1" >&2; usage ;;
    *) if [[ -z "$tag" ]]; then tag="$1"; else siblings+=("$1"); fi; shift ;;
  esac
done
[[ -n "$tag" && ${#siblings[@]} -gt 0 ]] || usage
if [[ ! "$tag" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "sync-sidecar: '$tag' is not a release tag (vMAJOR.MINOR.PATCH); a branch or commit would let unreleased instructions into a sibling" >&2
  exit 2
fi

# The default branch of a sibling, as origin has it: origin/main or the like.
default_branch() {
  local base
  base="$(git -C "$1" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)"
  if [[ -z "$base" ]]; then
    local candidate
    for candidate in origin/main origin/master main master; do
      if git -C "$1" rev-parse -q --verify "$candidate^{commit}" >/dev/null; then base="$candidate"; break; fi
    done
  fi
  printf '%s\n' "$base"
}

status=0
if [[ "$finish" -eq 1 ]]; then
  branch="sync-$tag"
  for sibling in "${siblings[@]}"; do
    echo ""
    echo "== $sibling"
    if ! git -C "$sibling" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      echo "   not a git work tree; skipped"; status=1; continue
    fi
    if ! git -C "$sibling" rev-parse -q --verify "refs/heads/$branch" >/dev/null; then
      echo "   no $branch here; nothing to finish"; continue
    fi
    git -C "$sibling" fetch --quiet --prune origin 2>/dev/null || true
    if [[ -z "$(git -C "$sibling" config --get "branch.$branch.remote" || true)" ]]; then
      echo "   $branch was never pushed, so it is kept: push it, or delete it yourself"; status=1; continue
    fi
    if git -C "$sibling" rev-parse -q --verify "refs/remotes/origin/$branch" >/dev/null; then
      echo "   origin/$branch still exists, so its pull request is not merged and deleted yet; kept"; continue
    fi
    base="$(default_branch "$sibling")"
    if [[ -z "$base" ]]; then
      echo "   no default branch to go back to (origin/HEAD, main or master); kept"; status=1; continue
    fi
    local_base="${base#origin/}"
    if [[ -n "$(git -C "$sibling" status --porcelain --untracked-files=no)" ]]; then
      echo "   uncommitted changes here; commit or stash them first; kept"; status=1; continue
    fi
    git -C "$sibling" switch --quiet "$local_base" || { echo "   could not switch to $local_base (git said why above); kept"; status=1; continue; }
    git -C "$sibling" merge --quiet --ff-only "$base" || { echo "   $local_base cannot fast-forward to $base; kept"; status=1; continue; }
    git -C "$sibling" branch --quiet -D "$branch"
    echo "   on $local_base at $(git -C "$sibling" rev-parse --short HEAD); $branch removed"
  done
  echo ""
  exit "$status"
fi

# The tag must exist on the remote, not only here: a sibling's librarian
# clones it from GitHub, and a local tag nobody pushed installs nothing there.
source="$(cd "$source" 2>/dev/null && pwd)" || { echo "sync-sidecar: no such directory: $source" >&2; exit 2; }
git -C "$source" fetch --quiet --tags origin 2>/dev/null || true
if ! git -C "$source" rev-parse -q --verify "refs/tags/$tag^{commit}" >/dev/null; then
  echo "sync-sidecar: no tag $tag in $source: publish the release first, then sync (that order is the point)" >&2
  exit 2
fi
if ! git -C "$source" ls-remote --exit-code --tags origin "refs/tags/$tag" >/dev/null 2>&1; then
  echo "sync-sidecar: tag $tag is not on origin: a sibling's scheduled librarian clones from there and would fail to install" >&2
  exit 2
fi
if ! git -C "$source" cat-file -e "$tag:skills/ktl-librarian/SKILL.md" 2>/dev/null; then
  echo "sync-sidecar: $tag has no skills/ktl-librarian/SKILL.md: the install step copies that path, so a sibling pinned to it fails every scheduled run" >&2
  exit 2
fi
for needed in "$sync_template" "$manifest_template"; do
  if ! git -C "$source" cat-file -e "$tag:$needed" 2>/dev/null; then
    echo "sync-sidecar: $tag has no $needed, so it predates the sync; sync to a release that carries it" >&2
    exit 2
  fi
done
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
git -C "$source" show "$tag:$sync_template" > "$tmp/knowledge-sync.sh"

for sibling in "${siblings[@]}"; do
  echo ""
  echo "== $sibling"
  # The sibling's own copy does the sync, as its workflow's run does. A
  # sibling that has none yet is synced by the tag's copy, which lays the
  # sibling's own down.
  script="$sibling/.lokf/scripts/knowledge-sync.sh"
  if [[ -f "$script" ]]; then
    echo "   running  the sibling's own .lokf/scripts/knowledge-sync.sh"
  else
    script="$tmp/knowledge-sync.sh"
    echo "   running  $tag's knowledge-sync.sh, since the sibling has no copy yet"
  fi
  rc=0
  bash "$script" --source "$source" --host "$sibling" --branch ${flags[@]+"${flags[@]}"} "$tag" || rc=$?
  # The tag was checked above, so a 2 here is the sibling's: a path that
  # is not there, say. It is reported, and the others go ahead.
  [[ "$rc" -eq 0 ]] || status=1
done
echo ""
echo "When the pull requests are merged: scripts/sync-sidecar.sh --finish $tag ${siblings[*]}"
echo ""
exit "$status"
