#!/usr/bin/env bash
# Copy this repository's knowledge bundle into the empty directory an eval
# run starts in. Each case's scaffold.sh runs this script.
#
# `claude plugin eval` runs a scaffold only under --scaffold: before the
# agent starts, as the operator and outside the agent's sandbox, in the run's
# empty working directory, with only PATH, a temporary HOME and TMPDIR set.
# It has 120 seconds, and a non-zero exit scores the run 0 with the message.
# Nothing there names the repository, so this script finds it from its own
# path, under evals/.
#
# Only .lokf/knowledge/ and the knowledge_bundle link go in. tests/, evals/
# and .lokf/feedback.md stay out, since they hold the expected concepts, the
# graders and other readers' reports.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd -P)"
bundle="$repo/.lokf/knowledge"
if [ ! -f "$bundle/index.md" ]; then
  echo "scaffold-bundle: no bundle at $bundle; this script finds the repository from its own path, which must be evals/ in it" >&2
  exit 1
fi
if [ -e .lokf ] || [ -e knowledge_bundle ]; then
  echo "scaffold-bundle: $(pwd) is not empty: .lokf or knowledge_bundle is already here" >&2
  exit 1
fi

mkdir .lokf
cp -R "$bundle" .lokf/knowledge
# Obsidian's workspace state, which a maintainer who opened the bundle as a
# vault leaves inside it; never bundle content (.lokf/.gitignore says so).
rm -rf .lokf/knowledge/.obsidian
if [ -L "$repo/knowledge_bundle" ]; then
  ln -s "$(readlink "$repo/knowledge_bundle")" knowledge_bundle
fi
echo "scaffold-bundle: copied .lokf/knowledge, $(find .lokf/knowledge -type f -name '*.md' | wc -l) files, into $(pwd)"
