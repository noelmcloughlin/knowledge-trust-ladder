#!/usr/bin/env bash
# Record one reader-feedback entry in .lokf/feedback.md without reading it.
#
# ktl-docent appends a Miss or a Disagreement here and ktl-librarian consumes
# it. Entries already in the file are other readers' reports: free text that
# can come from someone with no access to this repository. Keeping the file
# newest first used to mean the docent read it, edited it and wrote it back,
# so those reports entered the session of an agent that had just been fetching
# URLs and reading repository files - held off by nothing but a line of prose
# telling it not to act on them. This script does the insertion instead. The
# caller hands over its own entry and never opens the file, so no other
# reader's text reaches the model at all. The guard is the call, not a rule an
# agent has to keep (docs/threat-model.md, "Prompt-injection guards").
#
# It prints one line - the kind, the date, and how many entries now wait - and
# never any entry's text, the new one included. A caller that wants to show
# the reader what it recorded already has that text; it does not need this
# file to tell it.
#
# Bash 3.2 and POSIX tools only, so it runs on macOS's stock bash and on Git
# for Windows, like the other scripts here.
#
# Usage:
#   knowledge-feedback.sh [--root <dir>] [--for <login>] <kind> <text>
#
#   kind    Miss or Disagreement, and nothing else - the two shapes
#           ktl-librarian knows how to consume.
#   text    the entry itself, one argument. Whitespace is collapsed, so a
#           multi-line string still lands as one line per entry.
#   --for   an authenticated login (gh api user --jq .login, or glab), which
#           records the entry as `- docent, for human:<login>`. Left out, the
#           entry is `- docent` alone. Never a name typed in conversation and
#           never git config user.name: the attribution is only worth carrying
#           if the forge stands behind it.
#   --root  the repository root (default: the nearest ancestor of the current
#           directory holding .lokf/, else the current directory).
#
# Exit: 0 recorded; 2 the call was wrong and nothing was written; 1 the file
# could not be written (a read-only .lokf/, most often) - the caller should
# tell the reader the gap out loud instead.
[ -n "${BASH_VERSION:-}" ] || { echo "run this with bash: bash ${0##*/} [--root <dir>] [--for <login>] <kind> <text>" >&2; exit 2; }
set -u

usage() {
  echo "usage: ${0##*/} [--root <dir>] [--for <login>] <Miss|Disagreement> <text>" >&2
  exit 2
}

root=""; asker=""
while [ $# -gt 0 ]; do
  case "$1" in
    --root) [ $# -ge 2 ] || usage; root="$2"; shift 2 ;;
    --for)  [ $# -ge 2 ] || usage; asker="$2"; shift 2 ;;
    -h|--help) usage ;;
    --) shift; break ;;
    -*) echo "unknown option: $1" >&2; usage ;;
    *) break ;;
  esac
done
[ $# -eq 2 ] || usage
kind="$1"; text="$2"

# ---- what the librarian can consume ----------------------------------------
# A third kind would reach the librarian as an entry it has no rule for, so
# the set is closed here rather than left to whatever the caller typed.
case "$kind" in
  Miss|Disagreement) ;;
  *) echo "kind must be Miss or Disagreement, not '$kind'" >&2; exit 2 ;;
esac

# The attribution is the one field a later reader may take as evidence that a
# named person asked, so it is held to a login's characters before it is
# written - the same shape the registrar's provenance job insists on.
if [ -n "$asker" ]; then
  case "$asker" in
    *[!A-Za-z0-9-]*|-*|"") echo "--for takes a forge login (letters, digits and hyphens), not '$asker'" >&2; exit 2 ;;
  esac
  [ "${#asker}" -le 39 ] || { echo "--for: '$asker' is too long for a forge login" >&2; exit 2; }
fi

# One entry is one line. Collapse every whitespace run, drop control
# characters, and trim: a caller that passes a paragraph still cannot break
# the file's shape or forge a second entry with an embedded newline.
text="$(printf '%s' "$text" | tr -d '\000-\010\013\014\016-\037\177' | tr '\t\n\r' '   ' | sed -e 's/  */ /g' -e 's/^ //' -e 's/ $//')"
[ -n "$text" ] || { echo "the entry text is empty" >&2; exit 2; }

# ---- root ------------------------------------------------------------------
if [ -z "$root" ]; then
  d="$(pwd -P)"; root="$d"
  while [ "$d" != "/" ]; do
    if [ -d "$d/.lokf" ]; then root="$d"; break; fi
    d="$(dirname "$d")"
  done
fi
root="$(cd "$root" 2>/dev/null && pwd -P)" || { echo "no such directory: $root" >&2; exit 2; }
[ -d "$root/.lokf" ] || { echo "no .lokf/ under $root - ktl-sidecar creates the bundle" >&2; exit 2; }

file="$root/.lokf/feedback.md"
today="$(date +%Y-%m-%d)"
entry="- **$kind** - $text - docent${asker:+, for human:$asker}"

# ---- the file --------------------------------------------------------------
readonly_bundle() {
  echo "cannot write $file - if .lokf/ is read-only, say the gap out loud to the reader instead" >&2
  exit 1
}
# The rewrite below lands a temporary file beside this one, so the directory
# has to be writable even when the file itself already is.
[ -w "$root/.lokf" ] || readonly_bundle
# feedback.md is not knowledge and has no frontmatter; it appears the first
# time a reader's agent records a gap, which may be this call.
if [ ! -s "$file" ]; then
  {
    echo "# Reader feedback for the librarian"
    echo ""
    echo "Written by ktl-docent; consumed and cleared by ktl-librarian on its next run. Newest first. One line per entry."
  } > "$file" 2>/dev/null || readonly_bundle
fi
[ -w "$file" ] || readonly_bundle

# Newest first, which is why this cannot be a plain append: today's entry goes
# above every older date, and above today's own earlier entries. The entry
# travels in the environment rather than through -v, which would read a
# backslash in the text as an escape.
tmp="$file.$$"
trap 'rm -f "$tmp"' EXIT INT TERM
if KF_ENTRY="$entry" awk -v hdr="## $today" '
  BEGIN { entry = ENVIRON["KF_ENTRY"]; done = 0; skipblank = 0; last = "" }
  # The first date heading in the file is the newest one. Today either is it,
  # or belongs immediately above it.
  /^## / && done == 0 {
    h = $0; sub(/\r$/, "", h)
    if (h == hdr) { print hdr; print ""; print entry; skipblank = 1 }
    else { print hdr; print ""; print entry; print ""; print; last = $0 }
    done = 1
    next
  }
  # The blank line that followed the heading we just reprinted with one of
  # our own.
  skipblank == 1 { skipblank = 0; if ($0 == "") next }
  { print; last = $0 }
  # No date heading at all: a file that has only ever held its intro.
  END { if (done == 0) { if (last != "") print ""; print hdr; print ""; print entry } }
' "$file" > "$tmp" && mv "$tmp" "$file"; then
  trap - EXIT INT TERM
else
  echo "could not record the entry in $file" >&2
  exit 1
fi

# The same expression ktl-curator counts with, so the two never disagree about
# how many entries are waiting. It reads no entry's text, and neither does the
# caller from this line.
waiting="$(grep -c '^- \*\*' "$file" 2>/dev/null || true)"
printf 'recorded: %s under %s in .lokf/feedback.md (%s waiting for the librarian)\n' "$kind" "$today" "${waiting:-1}"
