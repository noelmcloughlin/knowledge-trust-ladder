#!/usr/bin/env bash
# The ingest's shell half. It runs knowledge-ingest.py beside it through
# `uv run` (the script's header names pyyaml and pypdf) or, without uv,
# through python3 with pyyaml. The script reads .lokf/ingest.yaml, mirrors
# the sources it names under .lokf/mirror/ and records them in
# .lokf/ingest.lock.yaml. The ingest workflow runs it with the manifest's
# secrets and no agent; ktl-librarian runs it in a live session.
#
# Usage: knowledge-ingest.sh [--root <dir>] [--visibility <v>] [--only <id>]... [--dry-run] [--prune] [--strict] [--summary <file>] [--status] [--patch [<file>]]
#   The Python half's header says what each flag does. --root is the
#   repository root; default: two levels above this script.
# Exit 0 completed; 1 stopped before any write; 2 usage or no runner.
[ -n "${BASH_VERSION:-}" ] || { echo "run this with bash: bash ${0##*/} [--root <dir>] [--visibility <v>] [--only <id>] [--dry-run] [--prune] [--strict] [--summary <file>] [--status] [--patch [<file>]]" >&2; exit 2; }
set -u
usage() { echo "usage: ${0##*/} [--root <dir>] [--visibility <v>] [--only <id>] [--dry-run] [--prune] [--strict] [--summary <file>] [--status] [--patch [<file>]]" >&2; exit 2; }
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root=""
args=()
status=""
while [ $# -gt 0 ]; do
  case "$1" in
    --root) [ $# -ge 2 ] || usage; root="$2"; shift 2 ;;
    --visibility|--only|--summary|--timeout|--now|--manifest|--lock) [ $# -ge 2 ] || usage; args+=("$1" "$2"); shift 2 ;;
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
# --status reads the manifest and the lock and nothing else, so python3 with
# pyyaml serves it without uv resolving the script's packages: the preflight
# calls it on machines that may be offline.
if [ -n "$status" ] && command -v python3 >/dev/null 2>&1 && python3 -c 'import yaml' >/dev/null 2>&1; then
  exec python3 "$py" --root "$root" ${args[@]+"${args[@]}"}
fi
if command -v uv >/dev/null 2>&1; then
  exec uv run --quiet "$py" --root "$root" ${args[@]+"${args[@]}"}
elif command -v python3 >/dev/null 2>&1 && python3 -c 'import yaml' >/dev/null 2>&1; then
  exec python3 "$py" --root "$root" ${args[@]+"${args[@]}"}
fi
echo "knowledge-ingest: needs uv, which installs pyyaml and pypdf for the script, or python3 with pyyaml; nothing was written. The sidecar's references/prerequisites.md says who installs uv." >&2
exit 2
