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
#   7. One file per `id`. A sync client's conflict copy (OneDrive, Dropbox,
#      Drive, iCloud) or a pasted duplicate carries the same `id`, passes
#      `lokf validate`, and silently merges into the original in the graph.
#   8. Every path in the bundle is lowercase: a-z, 0-9, `.`, `_`, `-`. Two
#      paths that differ only by case collide on Windows, macOS and SharePoint,
#      and a space, a parenthesis or an upper-case host name in a file name is
#      how every sync client names a conflict copy.
#   9. Every concept starts with a `---` frontmatter block that closes, with no
#      byte order mark in front of it. A BOM from a web editor or Notepad, or a
#      file with no block at all, would otherwise pass this script unread.
#
# Files are read with carriage returns removed and a leading byte order mark
# stripped, so a Windows checkout (`core.autocrlf`) reads the same as CI. The
# sidecar's `.lokf/.gitattributes` keeps tracked files on LF; rule 9 still
# reports a BOM, because other readers do not strip it.
#
# Usage: knowledge-conventions.sh [bundle-dir]   (default: knowledge, i.e. run
# from .lokf/). Exit 1 with one line per finding; nothing else is written.
[ -n "${BASH_VERSION:-}" ] || { echo "run this with bash: bash ${0##*/} [bundle-dir]" >&2; exit 2; }
set -euo pipefail

# The bundle directory may be a link (a host that keeps the real folder as a
# visible knowledge_bundle/), and find never enters a link it is handed bare:
# the trailing slash below is what makes it read the files at all.
bundle="${1:-knowledge}"; bundle="${bundle%/}"
[ -d "$bundle" ] || { echo "no bundle directory at $bundle" >&2; exit 2; }
fail=0
say() { echo "$1"; fail=1; }

# POSIX tools only (head -c, od, tail -c, tr), so this reads the same on
# Linux, macOS and Git for Windows.
has_bom() { [ "$(head -c 3 "$1" | od -An -tx1 | tr -d ' \n')" = "efbbbf" ]; }
clean() { if has_bom "$1"; then tail -c +4 "$1"; else cat "$1"; fi | tr -d '\r'; }

# ---- 1. log.md headings ----------------------------------------------------
log="$bundle/log.md"
if [ -f "$log" ]; then
  if has_bom "$log"; then say "$log: starts with a byte order mark - save as UTF-8 without BOM"; fi
  while IFS= read -r line; do
    say "$log: heading is not a bare ISO date: $line"
  done < <(clean "$log" | grep -E '^## ' | grep -vE '^## [0-9]{4}-[0-9]{2}-[0-9]{2}$' || true)
  dates="$(clean "$log" | grep -oE '^## [0-9]{4}-[0-9]{2}-[0-9]{2}$' | cut -c4- || true)"
  if [ -n "$dates" ]; then
    if ! printf '%s\n' "$dates" | sort -rc 2>/dev/null; then
      say "$log: day headings are not newest-first"
    fi
    while IFS= read -r d; do
      [ -n "$d" ] && say "$log: day $d has more than one heading - add bullets under the existing one"
    done < <(printf '%s\n' "$dates" | uniq -d)
  fi
fi

# ---- 2-9. concept files -----------------------------------------------------
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
ids=""
while IFS= read -r f; do
  # 8. path shape, checked on every Markdown file, reserved ones included
  rel="${f#"$bundle"/}"
  if ! printf '%s\n' "$rel" | grep -qE '^([a-z0-9][a-z0-9._-]*/)*[a-z0-9][a-z0-9._-]*$'; then
    say "$f: path is not lowercase a-z, 0-9, '.', '_', '-' - case-insensitive hosts and sync conflict copies are why"
  fi
  case "$(basename "$f")" in index.md|log.md|diataxis.md) continue ;; esac
  # 9. a readable, closed frontmatter block
  if has_bom "$f"; then say "$f: starts with a byte order mark - save as UTF-8 without BOM"; fi
  if [ "$(clean "$f" | head -n 1)" != "---" ] || [ "$(clean "$f" | grep -c '^---$')" -lt 2 ]; then
    say "$f: no closed frontmatter block - a concept starts with '---' and closes it before the body"
    continue
  fi
  # Frontmatter only for 2, 3, 6 and 7: the text between the first two `---` lines.
  fm="$(clean "$f" | awk 'NR==1 && $0!="---" {exit} NR>1 && $0=="---" {exit} NR>1 {print}')"
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
  # 4. open-question bullets, checked in the body. The date is spelt out
  #    digit by digit because the awk on older macOS has no {n} intervals.
  while IFS= read -r line; do
    [ -n "$line" ] && say "$f: open question not '- YYYY-MM-DD, <actor>: ...': ${line:0:60}"
  done < <(clean "$f" | awk '
    /^## Open questions$/ {inq=1; next}
    inq && /^#/ {inq=0}
    inq && /^- / && $0 !~ /^- [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9], (human|process):[^ :]+: / {print}
  ')
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
  # 7. collect the id; duplicates are reported once every file has been read
  id="$(printf '%s\n' "$fm" | sed -nE 's/^id:[[:space:]]*(.*[^[:space:]])[[:space:]]*$/\1/p' | head -n 1)"
  id="${id#\"}"; id="${id%\"}"; id="${id#\'}"; id="${id%\'}"
  if [ -n "$id" ]; then ids="${ids}${id}"$'\t'"${f}"$'\n'; fi
done < <(find "$bundle/" -name '*.md' -not -path '*/.obsidian/*' | sort)

# ---- 7. one file per id -----------------------------------------------------
while IFS= read -r dup; do
  [ -z "$dup" ] && continue
  files="$(printf '%s' "$ids" | awk -F'\t' -v d="$dup" '$1==d {printf "%s ", $2}')"
  say "id $dup is declared by more than one file: ${files}- a sync conflict copy or a pasted duplicate; keep one"
done < <(printf '%s' "$ids" | cut -f1 | sort | uniq -d)

if [ "$fail" -eq 0 ]; then
  echo "OK - $bundle keeps the conventions lokf validate cannot check"
fi
exit "$fail"
