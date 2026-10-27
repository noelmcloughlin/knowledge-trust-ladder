#!/usr/bin/env bash
# Copies this repository's knowledge bundle into the empty directory an eval
# run starts in, so the docent has something to answer from. Each case's
# scaffold.sh runs this one script, so the copy is written once.
#
# `claude plugin eval` runs a case's scaffold only when --scaffold is passed,
# before the agent starts, as the operator and outside the agent's sandbox,
# in the run's empty working directory, with a minimal environment: PATH, a
# temporary HOME and TMPDIR. It has 120 seconds, and a non-zero exit scores
# the run 0 with the message. Nothing in that environment names the
# repository, so it is found from this script's own path, under evals/.
#
# Only the bundle goes in: .lokf/knowledge/, and the knowledge_bundle
# doorway link beside it, pointing where the repository's points. Nothing
# else: not tests/, where the holdout names each question's expected
# concept; not evals/, where the cases and graders are; not
# .lokf/feedback.md, which holds other readers' reports and which the docent
# never reads anyway. So the agent under test sees the bundle a reader
# would, and no crib.
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
