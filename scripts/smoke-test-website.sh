#!/usr/bin/env bash
# Lays the ktl-website templates down on a throwaway host built from the
# sidecar's own dummy skeleton, as the skill's Steps 1 to 4 would, and builds
# the site twice: once with a README, a docs page and a changelog, and once
# with none of them, so both shapes of host are proved before a template
# change reaches one. This repository's own site proves the fuller
# configuration; this proves a bundle that is not this repository's.
#
# Usage: scripts/smoke-test-website.sh [--keep]   (--keep leaves the host behind)
# Needs: uv, node 22.12 or later, npm, git and python3, and the network for
# `uv lock` and `npm ci`.
#
# The host's toolkit is resolved as of the newest file this repository's own
# .lokf/uv.lock took, never as of today. A release uploaded since then could
# otherwise fail the test before anyone relocks here: wrapt 2.5.1 reached
# PyPI with wheels for CPython 3.10 and 3.11 only, and broke every run.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skill="$repo_root/skills/ktl-website"
sidecar="$repo_root/skills/ktl-sidecar/templates"
newest_upload="$(grep -o 'upload-time = "[^"]*"' "$repo_root/.lokf/uv.lock" | cut -d'"' -f2 | sort | tail -1)"
[[ -n "$newest_upload" ]] || { echo "no upload-time in .lokf/uv.lock - the host's toolkit cannot be resolved as of this repository's lock" >&2; exit 1; }
for tool in uv node npm git python3; do
  command -v "$tool" >/dev/null 2>&1 || { echo "$tool not found - the website smoke test needs uv, node, npm, git and python3" >&2; exit 1; }
done

test_root="$(mktemp -d)"
keep="${1:-}"
cleanup() { if [[ "$keep" == "--keep" ]]; then echo "kept $test_root"; else rm -rf "${test_root:?}"; fi; }
trap cleanup EXIT
host="$test_root/host"
mkdir -p "$host"
echo "Test host: $host"

fail=0
assert() {
  local description="$1" check="$2"
  if eval "$check"; then echo "OK:   $description"; else echo "FAIL: $description"; fail=1; fi
}
substitute() {
  # substitute TOKEN=value ... -- <grep arguments>: literal replacement of each
  # <TOKEN> through Python, as the skills do, with no sed mini-language.
  local -a pairs=() names=()
  while [[ $# -gt 0 && "$1" != "--" ]]; do pairs+=("$1"); names+=("${1%%=*}"); shift; done
  shift
  grep -rl "$@" | xargs -I{} env "${pairs[@]}" TOKENS="${names[*]}" python3 -c '
import os, sys
path = sys.argv[1]
text = open(path, encoding="utf-8").read()
for token in os.environ["TOKENS"].split():
    text = text.replace("<" + token + ">", os.environ[token])
open(path, "w", encoding="utf-8").write(text)
' {}
}

# ---- a host from the sidecar's skeleton: the bundle, its tooling, a README, a docs page, a changelog ----
(
  cd "$host"
  git init -q
  git config user.name smoke
  git config user.email smoke@example.invalid
  git config commit.gpgsign false
  git remote add origin https://github.com/acme/acme-platform.git
  mkdir -p .lokf/scripts
  cp -R "$sidecar/knowledge" .lokf/knowledge
  cp "$sidecar/pyproject.toml" .lokf/pyproject.toml
  cp "$sidecar/gitignore" .lokf/.gitignore
  cp "$sidecar/scripts/knowledge-report.sh" "$sidecar/scripts/knowledge-preflight.sh" .lokf/scripts/
  chmod +x .lokf/scripts/*.sh
  substitute PROJ_NAME="Acme Platform" PROJ_DESC="The platform Acme runs." PROJ_SLUG=acme-platform \
    BASE_IRI=https://acme.example/knowledge/ OWNER_NAME=Acme OWNER_SLUG=acme TODAY=2026-01-01 \
    -- -e '<PROJ_' -e '<BASE_IRI>' -e '<OWNER_' -e '<TODAY>' .lokf
  printf '# Acme Platform\n\nThe platform Acme runs. See [the bundle](.lokf/knowledge/index.md) and [the guide](docs/guide.md).\n' > README.md
  mkdir -p docs
  printf '# The guide\n\nHow to use the platform.\n' > docs/guide.md
  printf '# Changelog\n\n## [Unreleased]\n\n## [1.0.0] - 2026-01-01\n\n### Added\n\n- The platform.\n' > CHANGELOG.md
  (cd .lokf && UV_EXCLUDE_NEWER="$newest_upload" uv lock -q && UV_EXCLUDE_NEWER="$newest_upload" uv sync -q --locked)
  git add -A
  git commit -q -m "a host with a bundle"
)

echo ""
echo "Step 0: the preflight"
preflight="$(bash "$skill/scripts/website-preflight.sh" "$host")"
printf '%s\n' "$preflight" | sed 's/^/  /'
assert "the preflight ends on its summary line" "grep -qE '^Preflight: ' <<<\"\$preflight\""
assert "the preflight sees the README, the docs and the changelog" \
  "grep -qE '^ok +readme ' <<<\"\$preflight\" && grep -qE '^ok +docs ' <<<\"\$preflight\" && grep -qE '^ok +changelog ' <<<\"\$preflight\""
assert "the preflight reads the owner and the name from the remote" "grep -qE '^ok +git .*acme/acme-platform' <<<\"\$preflight\""

echo ""
echo "Step 1: lay the site down"
(
  cd "$host"
  cp -R "$skill/templates/website" website
  mv website/gitignore website/.gitignore
  substitute REPO_OWNER=acme REPO_NAME=acme-platform PROJ_NAME="Acme Platform" PROJ_DESC="The platform Acme runs." \
    -- -e '<REPO_' -e '<PROJ_' website
  git add -A
  git commit -q -m "the site"
)
assert "every template file landed" \
  "[[ \$(find \"$skill/templates/website\" -type f | wc -l) -eq \$(find \"$host/website\" -type f -not -path '*/node_modules/*' | wc -l) ]]"
assert "the bracket file name survived the copy" "[[ -f \"$host/website/src/pages/og/[...route].ts\" ]]"
assert "no placeholder is left in website/" "! grep -rq -e '<REPO_' -e '<PROJ_' \"$host/website\""
assert "the settled configuration shows the docs and the changelog" \
  "(cd \"$host/website\" && node scripts/config.mjs | grep -q '\"CHANGELOG\": \"CHANGELOG.md\"' && node scripts/config.mjs | grep -q '\"dir\": \"docs\"')"

echo ""
echo "Step 4: build, with a README, a docs page and a changelog"
build() {
  # The whole log on a failure, its last line otherwise.
  if (cd "$host/website" && npm run build > "$test_root/build.log" 2>&1); then
    tail -n 1 "$test_root/build.log"
  else
    echo "FAIL: the build failed; its log:"
    sed 's/^/    /' "$test_root/build.log"
    fail=1
  fi
}
(cd "$host/website" && npm ci --no-audit --no-fund --silent)
build
for f in index.html knowledge/index.html knowledge/services/example-service-a/index.html health/index.html graph/index.html \
         knowledge/concepts.jsonld knowledge/graph.json knowledge/graph.nt knowledge/datasets.jsonld \
         knowledge/services/example-service-a.md knowledge/services/example-service-a.jsonld \
         llms.txt docs/guide/index.html changelog/index.html og/index.png favicon.svg; do
  assert "dist/$f is there" "[[ -f \"$host/website/dist/$f\" ]]"
done
assert "the home page is the README's" "grep -q 'The platform Acme runs' \"$host/website/dist/index.html\""
assert "the README's link to the guide goes to its page" "grep -q 'href=\"/acme-platform/docs/guide/\"' \"$host/website/dist/index.html\""
assert "a concept page carries its trust label" "grep -qi 'checked' \"$host/website/dist/knowledge/services/example-service-a/index.html\""
assert "nothing of the template is left to commit" "[[ -z \$(git -C \"$host\" status --porcelain) ]]"

echo ""
echo "Step 4 again: the bare shape, with no README, docs or changelog, and the configuration untouched"
(
  cd "$host"
  git rm -rq README.md docs CHANGELOG.md
  git commit -q -m "a bare host"
)
build
assert "the home page is there, from the bundle's own introduction" "[[ -f \"$host/website/dist/index.html\" ]] && grep -q 'Acme Platform' \"$host/website/dist/index.html\""
assert "no docs pages" "[[ ! -d \"$host/website/dist/docs\" ]]"
assert "no release pages" "[[ ! -d \"$host/website/dist/changelog\" ]]"
assert "the bundle's pages, the health page and the graph are still there" \
  "[[ -f \"$host/website/dist/knowledge/index.html\" && -f \"$host/website/dist/health/index.html\" && -f \"$host/website/dist/graph/index.html\" ]]"
assert "the site's own favicon stands in" "[[ -f \"$host/website/dist/favicon.svg\" ]]"

echo ""
if [[ "$fail" -eq 0 ]]; then
  echo "Website smoke test: PASS"
else
  echo "Website smoke test: FAIL"
  exit 1
fi
