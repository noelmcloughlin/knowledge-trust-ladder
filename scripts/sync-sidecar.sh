#!/usr/bin/env bash
# Bring a sibling repository's sidecar copies and skills pin up to one release
# of this repository, and leave it to a person to review and commit.
#
# A sibling (the two Obsidian plugins, ai-linkmo, any host that scaffolded
# from ktl-sidecar) carries byte-identical copies of the templates under
# skills/ktl-sidecar/templates/ and pins its scheduled librarian to one tag of
# this repository with TRUST_LADDER_SKILLS_REF. The two must move together:
# the skill that tag installs is written against the wrapper, gate and
# preflight that tag ships, and once the librarian is armed, the pin decides
# which agent instructions run unattended with a credential in the job. So
# this script takes a *tag* and nothing looser, reads the templates out of
# that tag rather than the working tree, refuses a tag that does not exist
# yet (which settles the merge order: release here first, then sync), and
# never commits. The diff it leaves behind is the review.
#
# Usage: scripts/sync-sidecar.sh <tag> <sibling-dir>...
#   scripts/sync-sidecar.sh v0.26.0 ../obsidian-ktl-registrar ../obsidian-ktl-curator ../ai-linkmo
#
# For each sibling it copies every template the sibling already carries (a
# template it never laid down is reported, not added: that is ktl-sidecar's
# Step 5, a decision for the host), sets the pin to the tag, runs the
# sidecar's own checks there, and prints a draft changelog line and the
# commit command. Exit 1 when a sibling's checks fail after the copy; exit 2
# when the arguments are wrong or the tag is not usable.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
templates="skills/ktl-sidecar/templates"
# The same pairs check 11 in validate-repository.sh holds this repository to.
pairs=(
  "github/knowledge-registrar.yaml:.github/workflows/knowledge-registrar.yaml"
  "github/knowledge-librarian.yaml:.github/workflows/knowledge-librarian.yaml"
  "github/knowledge-release.yaml:.github/workflows/knowledge-release.yaml"
  "scripts/knowledge-librarian.sh:.lokf/scripts/knowledge-librarian.sh"
  "scripts/knowledge-conventions.sh:.lokf/scripts/knowledge-conventions.sh"
  "scripts/knowledge-conventions.py:.lokf/scripts/knowledge-conventions.py"
  "scripts/knowledge-preflight.sh:.lokf/scripts/knowledge-preflight.sh"
  "scripts/knowledge-provenance.sh:.lokf/scripts/knowledge-provenance.sh"
  "scripts/knowledge-feedback.sh:.lokf/scripts/knowledge-feedback.sh"
  "m365/knowledge-m365.sh:.lokf/m365/knowledge-m365.sh"
  "m365/ktl-docent-m365.md:.lokf/m365/ktl-docent-m365.md"
  "gitattributes:.lokf/.gitattributes"
)

if [[ $# -lt 2 ]]; then
  echo "usage: scripts/sync-sidecar.sh <tag> <sibling-dir>..." >&2
  exit 2
fi
tag="$1"; shift
if [[ ! "$tag" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "sync-sidecar: '$tag' is not a release tag (vMAJOR.MINOR.PATCH) - a branch or commit would let unreleased instructions into a sibling" >&2
  exit 2
fi
# The tag must exist on the remote, not only here: a sibling's librarian
# clones it from GitHub, and a local tag nobody pushed installs nothing there.
git -C "$repo_root" fetch --quiet --tags origin 2>/dev/null || true
if ! git -C "$repo_root" rev-parse -q --verify "refs/tags/$tag^{commit}" >/dev/null; then
  echo "sync-sidecar: no tag $tag in this repository - publish the release first, then sync (that order is the point)" >&2
  exit 2
fi
if ! git -C "$repo_root" ls-remote --exit-code --tags origin "refs/tags/$tag" >/dev/null 2>&1; then
  echo "sync-sidecar: tag $tag is not on origin - a sibling's scheduled librarian clones from there and would fail to install" >&2
  exit 2
fi
if ! git -C "$repo_root" cat-file -e "$tag:skills/ktl-librarian/SKILL.md" 2>/dev/null; then
  echo "sync-sidecar: $tag has no skills/ktl-librarian/SKILL.md - the install step copies that path, so a sibling pinned to it fails every scheduled run" >&2
  exit 2
fi
tag_sha="$(git -C "$repo_root" rev-parse "$tag^{commit}")"

# The skills pin is each repository's own to move, so it is not drift.
unpin() { sed -E 's/(TRUST_LADDER_SKILLS_REF: )v[0-9]+\.[0-9]+\.[0-9]+/\1vX.Y.Z/'; }
at_tag() { git -C "$repo_root" show "$tag:$templates/$1"; }

status=0
for sibling in "$@"; do
  echo ""
  echo "== $sibling"
  if [[ ! -d "$sibling/.lokf" ]]; then
    echo "   no .lokf/ here - not a sidecar host; skipped"
    status=1
    continue
  fi
  sibling_root="$(cd "$sibling" && pwd)"
  if ! git -C "$sibling_root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "   not a git work tree - the sync leaves a diff for review, and there is no diff to leave here; skipped"
    status=1
    continue
  fi

  # What the sibling pins today, so the report can say what moves.
  wf="$sibling_root/.github/workflows/knowledge-librarian.yaml"
  old_pin=""
  if [[ -f "$wf" ]]; then
    old_pin="$(grep -oE 'TRUST_LADDER_SKILLS_REF: v[0-9]+\.[0-9]+\.[0-9]+' "$wf" | head -1 | sed 's/.*: //' || true)"
  fi

  copied=(); same=(); absent=()
  for pair in "${pairs[@]}"; do
    src="${pair%%:*}"; dst="${pair##*:}"
    if ! git -C "$repo_root" cat-file -e "$tag:$templates/$src" 2>/dev/null; then
      continue  # a template this release did not have yet
    fi
    if [[ ! -f "$sibling_root/$dst" ]]; then
      absent+=("$dst")
      continue
    fi
    if cmp -s <(at_tag "$src" | unpin) <(unpin < "$sibling_root/$dst"); then
      same+=("$dst")
    else
      at_tag "$src" > "$sibling_root/$dst"
      copied+=("$dst")
    fi
  done
  # The template's own pin is one release behind by design (the release
  # commit moves it to the newest tag that existed then), so the copy above
  # would move a sibling backwards. Set it to the tag being synced.
  if [[ -f "$wf" ]]; then
    sed -i.sync-bak -E "s/(TRUST_LADDER_SKILLS_REF: )v[0-9]+\.[0-9]+\.[0-9]+/\1$tag/" "$wf"
    rm -f "$wf.sync-bak"
  fi

  for f in "${copied[@]}"; do echo "   copied   $f"; done
  for f in "${same[@]}"; do echo "   same     $f"; done
  for f in "${absent[@]}"; do echo "   absent   $f (never laid down here: ktl-sidecar Step 5 decides, not this script)"; done
  if [[ -f "$wf" ]]; then
    if [[ "$old_pin" == "$tag" ]]; then
      echo "   pin      already $tag"
    else
      echo "   pin      ${old_pin:-none} -> $tag ($tag_sha)"
    fi
  else
    echo "   pin      no knowledge-librarian.yaml here, so no scheduled librarian to pin"
  fi
  # Whether the skill the librarian runs changed between the two pins: a
  # sibling with identical copies and an unchanged skill has nothing to
  # sync, and that is the usual case.
  if [[ -n "$old_pin" && "$old_pin" != "$tag" ]] && git -C "$repo_root" rev-parse -q --verify "refs/tags/$old_pin^{commit}" >/dev/null; then
    skill_changes="$(git -C "$repo_root" diff --name-only "$old_pin" "$tag" -- skills/ktl-librarian | wc -l | tr -d ' ')"
    if [[ "$skill_changes" -gt 0 ]]; then
      echo "   skill    ktl-librarian changed in $skill_changes file(s) between $old_pin and $tag"
    else
      echo "   skill    ktl-librarian unchanged between $old_pin and $tag"
    fi
  fi

  # The sidecar's own checks, run from the sibling's copies as its gate would.
  ok=1
  (
    cd "$sibling_root/.lokf"
    if [[ -x scripts/knowledge-preflight.sh ]]; then
      bash scripts/knowledge-preflight.sh | tail -1 | sed 's/^/   /'
    fi
    if command -v uv >/dev/null 2>&1; then
      uv run --quiet lokf validate --check-refs knowledge 2>&1 | tail -1 | sed 's/^/   /'
    else
      echo "   uv not found: lokf validate skipped, and the conventions script runs without its parser's half"
    fi
    if [[ -f scripts/knowledge-conventions.sh ]]; then
      bash scripts/knowledge-conventions.sh knowledge 2>&1 | sed 's/^/   /'
    fi
  ) || ok=0
  if [[ "$ok" -eq 0 ]]; then
    echo "   FAIL     a check above failed - fix the bundle in the same change (a time later than its commit, say), or the sibling's gate fails on it"
    status=1
  fi

  echo ""
  if [[ ${#copied[@]} -eq 0 && "$old_pin" == "$tag" ]]; then
    echo "   nothing to sync"
    continue
  fi
  echo "   changelog (under ## [Unreleased], ### Security):"
  echo "   - **The sidecar copies and the skills pin match \`$tag\`.** <what the release changed in the copies, from its changelog>. No plugin change."
  echo "   commit, from $sibling_root:"
  echo "   git add -A && git commit -m \"security(sidecar): sync copies and skills pin from $tag\""
done

exit "$status"
