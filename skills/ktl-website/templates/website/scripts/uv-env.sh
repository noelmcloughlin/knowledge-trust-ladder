#!/usr/bin/env bash
# Installs the tools a uv project pins, and prints how to run them.
#
#   scripts/uv-env.sh <project folder>
#
# Prints `--frozen` or `--no-sync`: the option that `uv run --project
# <project folder>` takes to run one of the project's tools.
#
# uv fetches a locked file from the address uv.lock holds for it, whichever
# index uv is set to read. The lock this site comes with holds PyPI's
# addresses, so behind a package mirror `uv run --frozen` reaches for a host
# the network blocks. There this script exports the lock's versions and
# hashes, and installs them into the project's .venv from the index uv reads.
# uv checks each file against the lock's hash, so a mirror serves the files
# the lock names or the build stops, and uv.lock stays as it is.
#
# The script takes that route when UV_DEFAULT_INDEX, UV_INDEX_URL or UV_INDEX
# names an index. With none set it installs from the lock's own addresses,
# and takes the route only when that fails, as it does where a uv.toml names
# the mirror.
set -euo pipefail
project=${1:?usage: scripts/uv-env.sh <project folder>}
[ -f "$project/uv.lock" ] || { echo "uv-env.sh: $project holds no uv.lock; run uv lock in that folder and commit the file" >&2; exit 1; }

from_index() {
  local pins status=0
  pins=$(mktemp "${TMPDIR:-/tmp}/uv-env.XXXXXX")
  {
    uv export --project "$project" --frozen --no-emit-project --format requirements-txt --quiet --output-file "$pins" &&
      { [ -f "$project/.venv/pyvenv.cfg" ] || (cd "$project" && uv venv --quiet); } &&
      uv pip install --quiet --require-hashes --python "$project/.venv" --requirements "$pins"
  } >&2 || status=$?
  rm -f "$pins"
  return "$status"
}

if [ -n "${UV_DEFAULT_INDEX:-}${UV_INDEX_URL:-}${UV_INDEX:-}" ]; then
  from_index || { echo "uv-env.sh: the index uv reads did not give the files $project/uv.lock pins, each checked against its hash there" >&2; exit 1; }
  echo --no-sync
elif said=$(uv sync --project "$project" --frozen --inexact --quiet 2>&1); then
  echo --frozen
elif from_index 2>/dev/null; then
  echo --no-sync
else
  printf '%s\n' "$said" >&2
  echo "uv-env.sh: uv installed $project's tools neither from the addresses in its uv.lock nor from the index it reads; set UV_DEFAULT_INDEX to a mirror of PyPI to see what that index answers" >&2
  exit 1
fi
