#!/usr/bin/env bash
# The ingest's shell half. It runs knowledge-ingest.py beside it with the
# first of these that it finds:
#   - the sidecar's own .venv, when that holds pyyaml and pypdf;
#   - `uv run` after uv_ready, since the script's header names both;
#   - the .venv or python3 with pyyaml alone, which reads every source but a
#     PDF.
# knowledge-apply.sh explains the order, the Python 3.9 floor and uv_ready.
# `uv add pypdf` in .lokf/ puts pypdf in the .venv, so no run needs `uv run`.
#
# The script reads .lokf/ingest.yaml, mirrors
# the sources it names under .lokf/mirror/ and records them in
# .lokf/ingest.lock.yaml. The ingest workflow runs it with the manifest's
# secrets and no agent; ktl-librarian runs it in a live session.
#
# Usage: knowledge-ingest.sh [--root <dir>] [--visibility <v>] [--only <id>]... [--dry-run] [--prune] [--strict] [--summary <file>] [--status] [--patch [<file>]] [--time-limit <minutes>]
#   The Python half's header says what each flag does. --root is the
#   repository root; default: two levels above this script.
# Exit 0 completed; 1 stopped before any write; 2 usage or no runner.
[ -n "${BASH_VERSION:-}" ] || { echo "run this with bash: bash ${0##*/} [--root <dir>] [--visibility <v>] [--only <id>] [--dry-run] [--prune] [--strict] [--summary <file>] [--status] [--patch [<file>]] [--time-limit <minutes>]" >&2; exit 2; }
set -u
usage() { echo "usage: ${0##*/} [--root <dir>] [--visibility <v>] [--only <id>] [--dry-run] [--prune] [--strict] [--summary <file>] [--status] [--patch [<file>]] [--time-limit <minutes>]" >&2; exit 2; }
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root=""
args=()
status=""
while [ $# -gt 0 ]; do
  case "$1" in
    --root) [ $# -ge 2 ] || usage; root="$2"; shift 2 ;;
    --visibility|--only|--summary|--timeout|--time-limit|--now|--manifest|--lock) [ $# -ge 2 ] || usage; args+=("$1" "$2"); shift 2 ;;
    --patch) args+=("$1"); shift; if [ $# -gt 0 ] && [ "${1#-}" = "$1" ]; then args+=("$1"); shift; fi ;;
    --status) status=1; args+=("$1"); shift ;;
    --dry-run|--prune|--strict) args+=("$1"); shift ;;
    -h|--help) usage ;;
    --) shift; while [ $# -gt 0 ]; do args+=("$1"); shift; done ;;
    *) echo "unknown option: $1" >&2; usage ;;
  esac
done
[ -n "$root" ] || root="$(cd "$here/../.." && pwd)"
py="$here/knowledge-ingest.py"
[ -f "$py" ] || { echo "knowledge-ingest: $py is missing beside this script; run ktl-sidecar's repair path" >&2; exit 2; }
usable() { command -v "$1" >/dev/null 2>&1 && "$1" -c "import sys; assert sys.version_info >= (3, 9); import $2" >/dev/null 2>&1; }
uvflags=(); uverr=""; uvhint="Run uv add pypdf in .lokf/ to pin them by hash."
uv_ready() {
  local err names name again unpinned lifted=""
  command -v uv >/dev/null 2>&1 || return 1
  uv sync --offline --quiet --script "$1" >/dev/null 2>&1 && return 0
  until err="$(uv sync --color never --script "$1" ${uvflags[@]+"${uvflags[@]}"} 2>&1 >/dev/null)"; do
    names="$(printf '%s\n' "$err" | sed -n 's/^warning: \([^ ]*\) is missing an upload date.*/\1/p' | tr -d '\140' | sed 's/-[0-9].*//' | tr '[:upper:]' '[:lower:]' | tr '_.' '--' | sort -u)"
    again=""; unpinned=""
    for name in $names; do
      case " $lifted " in *" $name "*) again=1 ;; esac
      case "$name" in *[!a-z0-9-]*) unpinned="$unpinned $name"; continue ;; esac
      grep -qiE "^# dependencies = .*\"${name//-/[-_.]}==" "$1" || unpinned="$unpinned $name"
    done
    if [ -z "$names" ] || [ -n "$again$unpinned" ]; then
      uverr="$(printf '%s\n' "$err" | grep -v ' is missing an upload date' || true)"
      [ -z "$unpinned" ] || uverr+=$'\n'"${0##*/}: the package index serves no upload times for$unpinned, which the script's header does not pin with ==, so exclude-newer stays."
      return 1
    fi
    for name in $names; do uvflags+=(--exclude-newer-package "$name=false"); lifted="$lifted $name"; done
  done
  [ -z "$lifted" ] || echo "${0##*/}: the package index serves no upload times, so exclude-newer is lifted for$lifted. The versions stay pinned. $uvhint" >&2
  return 0
}
venv="$root/.lokf/.venv/bin/python"; [ -e "$venv" ] || venv="$root/.lokf/.venv/Scripts/python.exe"
# --status reads the manifest and the lock and nothing else, so pyyaml alone
# serves it without uv resolving the script's packages: the preflight calls it
# on machines that may be offline.
if [ -n "$status" ]; then
  for p in "$venv" python3; do
    usable "$p" yaml && exec "$p" "$py" --root "$root" ${args[@]+"${args[@]}"}
  done
fi
if usable "$venv" "yaml, pypdf"; then
  exec "$venv" "$py" --root "$root" ${args[@]+"${args[@]}"}
elif uv_ready "$py"; then
  exec uv run --quiet ${uvflags[@]+"${uvflags[@]}"} "$py" --root "$root" ${args[@]+"${args[@]}"}
fi
for p in "$venv" python3; do
  if usable "$p" yaml; then
    [ -z "$uverr" ] || usable "$p" pypdf || echo "knowledge-ingest: uv could not install the script's packages, so this run refuses each PDF" >&2
    exec "$p" "$py" --root "$root" ${args[@]+"${args[@]}"}
  fi
done
[ -z "$uverr" ] || printf '%s\n' "$uverr" >&2
echo "knowledge-ingest: needs the sidecar's .venv (uv sync in .lokf/), uv, which installs pyyaml and pypdf for the script, or python3 3.9 or later with pyyaml; nothing was written. The sidecar's references/prerequisites.md says who installs uv." >&2
exit 2
