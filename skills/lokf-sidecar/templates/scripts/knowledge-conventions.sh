#!/usr/bin/env bash
# Conventions of a LOKF bundle that `lokf validate` cannot see.
#
# The toolkit checks frontmatter against the schema and reads a concept body
# as an opaque string; it never reads log.md. The four skills and both
# Obsidian plugins rely on a few conventions beyond that, and each has been
# broken at least once by an agent that had been told the rule in prose:
#
#   1. log.md has one `## YYYY-MM-DD` heading per day - the bare ISO date,
#      newest first, no duplicates. OKF §9 makes the date form a MUST, and the
#      LOKF Curator plugin finds today's section by that exact heading.
#   2. Every `at:` is a quoted string. Unquoted, YAML hands the toolkit a
#      datetime object and the curator's string comparison a surprise.
#   3. `verified` is a list, never a bare `{ by, at }` mapping, and carries at
#      most one `process:lokf-librarian` event - the librarian replaces its
#      own, it does not stack them.
#   4. A bullet under `## Open questions` is `- YYYY-MM-DD, <actor>: ...`, the
#      shape the curator and both plugins write and read; the curator quotes
#      the first bullet, so a trailing signature would become the question.
#   5. Every `resource:` that is not a URL names a file or directory that
#      exists, relative to the repository root (the nearest directory holding
#      `.lokf/`; failing that, the bundle's parent). A source that has gone
#      should fail the gate now, not wait for the librarian's next refresh.
#      URLs are never fetched.
#   6. A commit-shaped `revision` on a `generated` or `verified` event (lokf
#      0.9.0+ records one) names a commit in this repository that holds the
#      concept's local `resource`. ETags, digests and version labels pin URLs
#      and are not checked. Needs the full history: a shallow clone is reported.
#
# Usage: knowledge-conventions.sh [bundle-dir]   (default: knowledge, i.e. run
# from .lokf/). Exit 1 with one line per finding; nothing else is written.
set -euo pipefail

bundle="${1:-knowledge}"
[ -d "$bundle" ] || { echo "no bundle directory at $bundle" >&2; exit 2; }
fail=0
say() { echo "$1"; fail=1; }

# ---- 1. log.md headings ----------------------------------------------------
log="$bundle/log.md"
if [ -f "$log" ]; then
  while IFS= read -r line; do
    say "$log: heading is not a bare ISO date: $line"
  done < <(grep -E '^## ' "$log" | grep -vE '^## [0-9]{4}-[0-9]{2}-[0-9]{2}$' || true)
  dates="$(grep -oE '^## [0-9]{4}-[0-9]{2}-[0-9]{2}$' "$log" | cut -c4- || true)"
  if [ -n "$dates" ]; then
    if ! printf '%s\n' "$dates" | sort -rc 2>/dev/null; then
      say "$log: day headings are not newest-first"
    fi
    while IFS= read -r d; do
      [ -n "$d" ] && say "$log: day $d has more than one heading - add bullets under the existing one"
    done < <(printf '%s\n' "$dates" | uniq -d)
  fi
fi

# ---- 2-6. concept files -----------------------------------------------------
# Repository root for rule 5: the nearest ancestor holding `.lokf/`, else the
# bundle's parent (a bare bundle handed to this script on its own).
real="$(cd "$bundle" && pwd -P)"
root="$(dirname "$real")"
d="$real"
while [ "$d" != "/" ]; do
  if [ -d "$d/.lokf" ]; then root="$d"; break; fi
  d="$(dirname "$d")"
done
# Rule 6 needs git: whether the root is in a work tree, and whether that tree
# has its full history. Outside git the rule is skipped; a shallow clone is
# reported, because a pin the script cannot resolve is not a pin it has checked.
gitroot="$(git -C "$root" rev-parse --show-toplevel 2>/dev/null || true)"
shallow="$(git -C "$root" rev-parse --is-shallow-repository 2>/dev/null || echo false)"
while IFS= read -r f; do
  case "$(basename "$f")" in index.md|log.md|diataxis.md) continue ;; esac
  # Frontmatter only for 2 and 3: the text between the first two `---` lines.
  fm="$(awk 'NR==1 && $0!="---" {exit} NR>1 && $0=="---" {exit} NR>1 {print}' "$f")"
  # 2. unquoted timestamps
  while IFS= read -r line; do
    [ -n "$line" ] && say "$f: unquoted timestamp: $line"
  done < <(printf '%s\n' "$fm" | grep -E '^\s*(- )?at: [0-9]' || true)
  # 3. verified as a bare mapping (inline or block form), and stacked events
  if printf '%s\n' "$fm" | grep -qE '^verified:\s*\{'; then
    say "$f: verified is an inline mapping - write a one-item list"
  fi
  if printf '%s\n' "$fm" | awk 'prev=="verified:" && $0 ~ /^  by:/ {found=1} {prev=$0} END {exit !found}'; then
    say "$f: verified is a bare mapping - write a one-item list"
  fi
  n="$(printf '%s\n' "$fm" | grep -cE '^\s*- by: process:lokf-librarian$' || true)"
  if [ "${n:-0}" -gt 1 ]; then
    say "$f: $n process:lokf-librarian events - the librarian replaces its own, never stacks"
  fi
  # 4. open-question bullets, checked in the body
  while IFS= read -r line; do
    [ -n "$line" ] && say "$f: open question not '- YYYY-MM-DD, <actor>: ...': ${line:0:60}"
  done < <(awk '
    /^## Open questions$/ {inq=1; next}
    inq && /^#/ {inq=0}
    inq && /^- / && $0 !~ /^- [0-9]{4}-[0-9]{2}-[0-9]{2}, (human|process):[^ :]+: / {print}
  ' "$f")
  # 5. local resource paths exist: top-level `resource:` and `sources[].resource`
  while IFS= read -r res; do
    [ -z "$res" ] && continue
    case "$res" in *://*) continue ;; esac
    res="${res%%#*}"
    res="${res#\"}"; res="${res%\"}"; res="${res#\'}"; res="${res%\'}"
    res="${res%"${res##*[![:space:]]}"}"
    [ -z "$res" ] && continue
    case "$res" in /*) target="$res" ;; *) target="$root/$res" ;; esac
    [ -e "$target" ] || say "$f: resource not found: $res (looked at $target)"
  done < <(printf '%s\n' "$fm" | sed -nE 's/^[[:space:]]*(- )?resource:[[:space:]]*(.*[^[:space:]])[[:space:]]*$/\2/p')
  # 6. a commit-shaped `revision` names a commit that holds the concept's own
  #    local `resource`. Anything with a character outside [0-9a-f] - an ETag,
  #    a `sha256:` digest, a version label - pins a URL and is skipped, as is
  #    every revision on a concept whose `resource` is a URL, absolute or absent.
  res="$(printf '%s\n' "$fm" | sed -nE 's/^resource:[[:space:]]*(.*[^[:space:]])[[:space:]]*$/\1/p' | head -n 1)"
  res="${res%%#*}"
  res="${res#\"}"; res="${res%\"}"; res="${res#\'}"; res="${res%\'}"
  res="${res%"${res##*[![:space:]]}"}"
  case "$res" in ""|*://*|/*) res="" ;; esac
  while IFS= read -r rev; do
    rev="${rev#\"}"; rev="${rev%\"}"; rev="${rev#\'}"; rev="${rev%\'}"
    case "$rev" in ""|*[!0-9a-f]*) continue ;; esac
    if [ "${#rev}" -lt 7 ] || [ -z "$res" ] || [ -z "$gitroot" ]; then continue; fi
    if [ "$shallow" = true ]; then
      say "$f: revision $rev cannot be checked in a shallow clone - check out with fetch-depth: 0"
    elif ! git -C "$root" cat-file -e "$rev:./$res" 2>/dev/null; then
      say "$f: revision $rev does not hold $res - no such commit, or the path was absent in it"
    fi
  done < <(printf '%s\n' "$fm" | sed -nE 's/^[[:space:]]*(- )?revision:[[:space:]]*(.*[^[:space:]])[[:space:]]*$/\2/p')
done < <(find "$bundle" -name '*.md' -not -path '*/.obsidian/*' | sort)

if [ "$fail" -eq 0 ]; then
  echo "OK - $bundle keeps the conventions lokf validate cannot check"
fi
exit "$fail"
