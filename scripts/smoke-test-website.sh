#!/usr/bin/env bash
# Copies the ktl-website templates into a throwaway host built from the
# sidecar's own dummy skeleton, as the skill's Steps 1 to 4 would. It builds
# the site twice: once with a README, a docs page, a changelog, the schema's
# pages and the data, and once with none of them. So both shapes of host are
# proved before a template change reaches one. This repository's own site
# proves the fuller configuration; this proves a bundle that is not this
# repository's.
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
  git config tag.gpgsign false
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
  printf '# Architecture\n\nHow the platform is built.\n' > docs/architecture.md
  printf '# Changelog\n\n## [Unreleased]\n\n## [1.0.0] - 2026-01-01\n\n### Added\n\n- The platform.\n' > CHANGELOG.md
  (cd .lokf && UV_EXCLUDE_NEWER="$newest_upload" uv lock -q && UV_EXCLUDE_NEWER="$newest_upload" uv sync -q --locked)
  git add -A
  git commit -q -m "a host with a bundle"
  git tag v1.0.0
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
echo "Step 1: install the site"
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
echo "Step 1 again: the schema's pages and the data, which the host's own commands build"
(
  cd "$host"
  # Stand-ins for LinkML's gen-doc and a build-browse recipe, so the test
  # needs neither LinkML nor just. The pages carry what gen-doc writes and
  # the site must undo: mkdocs-material's frontmatter and search wrapper, a
  # type's title with no line break after its frontmatter, YAML in a
  # <details>, and a class diagram whose links keep the element's case.
  mkdir -p tools
  cat > tools/schema-pages.py <<'PY'
from pathlib import Path

out = Path("docs/elements")
out.mkdir(parents=True, exist_ok=True)
fence = "`" * 3
(out / "index.md").write_text(
    "# acme\n\nThe Acme platform's schema\n\nURI: https://acme.example/schema\n\n"
    "## Classes\n\n| Class | Description |\n| --- | --- |\n| [Service](Service.md) | A service the platform runs |\n\n"
    "## Slots\n\n| Slot | Description |\n| --- | --- |\n| [owner](owner.md) | Who owns the service |\n\n"
    "## Types\n\n| Type | Description |\n| --- | --- |\n| [String](String.md) | A character string |\n"
)
(out / "Service.md").write_text(
    "---\nsearch:\n  boost: 10.0\n---\n\n# Class: Service \n\n\n_A service the platform runs_\n\n\n\n"
    '<div data-search-exclude markdown="1">\n\n\n\nURI: [acme:Service](https://acme.example/schema/Service)\n\n\n\n'
    f'{fence}mermaid\n classDiagram\n    class Service\n    click Service href "../Service/"\n'
    f'      Service --> "0..1" String : owner\n        click String href "../String/"\n{fence}\n\n\n'
    "## Slots\n\n| Name | Cardinality and Range | Description |\n| --- | --- | --- |\n"
    "| [owner](owner.md) | 0..1 <br/> [String](String.md) | Who owns the service |\n\n"
    f"## LinkML Source\n\n<details>\n{fence}yaml\nname: Service\nslots:\n- owner\n\n{fence}\n</details></div>\n"
)
(out / "owner.md").write_text(
    "---\nsearch:\n  boost: 1.0\n---\n\n# Slot: owner \n\n\n_Who owns the service_\n\n\n\n"
    '<div data-search-exclude markdown="1">\n\n## Applicable Classes\n\n| Name | Description |\n| --- | --- |\n'
    "| [Service](Service.md) | A service the platform runs |\n\n</div>\n"
)
(out / "String.md").write_text(
    "---\nsearch:\n  boost: 1.0\n---# Type: String \n\n\n\n\n_A character string_\n\n\n\n"
    '<div data-search-exclude markdown="1">\n\nURI: [xsd:string](http://www.w3.org/2001/XMLSchema#string)\n\n</div>\n'
)
PY
  cat > tools/data.py <<'PY'
import sqlite3
from pathlib import Path

out = Path("data")
out.mkdir(exist_ok=True)
db = sqlite3.connect(out / "acme.sqlite")
db.execute("create table Service (id text primary key, name text, owner text)")
db.execute("insert into Service values ('svc-a', 'Service A', 'Acme')")
db.commit()
db.close()
(out / "metadata.yaml").write_text(
    "plugins:\n  datasette-auth-tokens:\n    secret: not-for-the-site\n"
    "databases:\n  acme:\n    description: The services the platform runs.\n"
    "    plugins:\n      datasette-cluster-map:\n        api_key: not-for-the-site-either\n"
)
(out / "notes.txt").write_text("Not a database, and never published.\n")
PY
  printf '/docs/elements/\n/data/\n' > .gitignore
  # The Markdown parser reads this quoted block, with more words after its
  # language, as a diagram, so the sync must still mark the page for drawing.
  cat >> docs/architecture.md <<'MD'

> ```mermaid title="The platform"
> flowchart LR
>   web --> api
> ```
MD
  # A retired mkdocs site leaves an About page, whose old address a w3id rule
  # names, and gen-doc's templates folder, which is not a page.
  printf '# About\n\nWho runs the platform.\n' > docs/about.md
  mkdir -p docs/templates-linkml
  printf '# Templates for gen-doc\n' > docs/templates-linkml/README.md
  # A retelling of the guide, and one of a concept, each for one audience.
  printf '# The guide, in short\n\nThe platform, in fewer words.\n' > docs/guide.en-simple.md
  cat > .lokf/knowledge/services/example-service-a-simple.md <<'MD'
---
type: Service
id: https://acme.example/knowledge/services/example-service-a-simple
title: Example Service A, for readers aged 13 to 18
description: Example Service A retold for readers aged 13 to 18.
derivedFrom:
- https://acme.example/knowledge/services/example-service-a
tags:
- audience-13-18
---

# Overview

Example Service A, in fewer words.
MD
  python3 - <<'PY'
from pathlib import Path

config = Path("website/site.config.mjs")
text = config.read_text(encoding="utf-8")
for old, new in (
    ('export const SCHEMA = "auto";', 'export const SCHEMA = { dir: "docs/elements", build: "python3 tools/schema-pages.py" };'),
    ("export const BROWSE = null;", 'export const BROWSE = { dir: "data", build: "python3 tools/data.py" };'),
    ("export const PAGES = [];", 'export const PAGES = [{ slug: "simple", source: "docs/guide.en-simple.md", label: "In short", retells: "docs/guide.md" }];'),
    ('export const DOCS = "auto";', 'export const DOCS = { dir: "docs", exclude: ["templates-linkml"] };'),
    ("export const REDIRECTS = {};", 'export const REDIRECTS = { "/elements": "/schema/", "/elements/[...slug]": "/schema/[...slug]", "/about": "/docs/about/" };'),
):
    assert text.count(old) == 1, old
    text = text.replace(old, new)
config.write_text(text, encoding="utf-8")
PY
  git add -A
  git commit -q -m "the schema's pages and the data"
)

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
(cd "$host/website" && npm ci --ignore-scripts --no-audit --no-fund --silent)
build
for f in index.html knowledge/index.html knowledge/services/example-service-a/index.html health/index.html graph/index.html \
         knowledge/concepts.jsonld knowledge/graph.json knowledge/graph.nt knowledge/datasets.jsonld \
         knowledge/services/example-service-a.md knowledge/services/example-service-a.jsonld \
         knowledge/log.xml llms.txt llms-full.txt docs/guide/index.html changelog/index.html og/index.png favicon.svg; do
  assert "dist/$f is there" "[[ -f \"$host/website/dist/$f\" ]]"
done
assert "the home page is the README's" "grep -q 'The platform Acme runs' \"$host/website/dist/index.html\""
assert "the README's link to the guide goes to its page" "grep -q 'href=\"/acme-platform/docs/guide/\"' \"$host/website/dist/index.html\""
assert "the home page offers the architecture page as a button" "grep -q 'class=\"sl-link-button[^\"]*\" href=\"/acme-platform/docs/architecture/\"' \"$host/website/dist/index.html\""
assert "the home page offers the schema's pages as a button" "grep -q 'class=\"sl-link-button[^\"]*\" href=\"/acme-platform/schema/\"' \"$host/website/dist/index.html\""
assert "the header shows the Knowledge Trust Ladder logo" "grep -q '_astro/logo-light[^\"]*\\.svg' \"$host/website/dist/index.html\""
assert "a concept page carries its trust label" "grep -qi 'checked' \"$host/website/dist/knowledge/services/example-service-a/index.html\""
assert "the sync writes each concept's preview, and a concept page carries the script that shows one" \
  "python3 -c 'import json, sys; p = json.load(open(sys.argv[1]))[\"services/example-service-a\"]; assert p[\"title\"] == \"Example Service A\" and p[\"type\"] == \"Service\" and p[\"label\"] and p[\"tone\"]' \"$host/website/dist/knowledge/previews.json\" && { grep -q 'previews.json' \"$host/website/dist/knowledge/services/example-service-a/index.html\" || grep -rq 'previews.json' \"$host/website/dist/_astro\"; }"
assert "a concept page links the graph opened on it" "grep -q 'href=\"/acme-platform/graph/?concept=services/example-service-a\"' \"$host/website/dist/knowledge/services/example-service-a/index.html\""
assert "a concept page links its file's history and names the bundle's licence" \
  "grep -q 'href=\"https://github.com/acme/acme-platform/commits/[0-9a-f]*/.lokf/knowledge/services/example-service-a.md\"' \"$host/website/dist/knowledge/services/example-service-a/index.html\" && grep -q '>CC BY 4.0</a>' \"$host/website/dist/knowledge/services/example-service-a/index.html\" && grep -q 'rel=\"license\"[^>]*href=\"https://creativecommons.org/licenses/by/4.0/\"' \"$host/website/dist/knowledge/services/example-service-a/index.html\""
assert "llms-full.txt opens each concept with its label and its page, its headings under its title" \
  "grep -A2 '^## Example Service A$' \"$host/website/dist/llms-full.txt\" | grep -q '^- Label: ' && grep -q '^- Page: https://acme.github.io/acme-platform/knowledge/services/example-service-a/$' \"$host/website/dist/llms-full.txt\" && grep -q '^### Overview$' \"$host/website/dist/llms-full.txt\""
assert "a release page links the repository, the docs and the bundle at the release's tag, and the release" \
  "grep -q 'href=\"https://github.com/acme/acme-platform/tree/v1.0.0/docs\"' \"$host/website/dist/changelog/version/1-0-0/index.html\" && grep -q 'href=\"https://github.com/acme/acme-platform/tree/v1.0.0/.lokf/knowledge\"' \"$host/website/dist/changelog/version/1-0-0/index.html\" && grep -q 'href=\"https://github.com/acme/acme-platform/releases/tag/v1.0.0\"' \"$host/website/dist/changelog/version/1-0-0/index.html\""
assert "the link check reads the text files too" "grep -q 'text files all resolve' \"$test_root/build.log\""
assert "llms.txt offers llms-full.txt" "grep -q '/llms-full.txt)' \"$host/website/dist/llms.txt\""
assert "a docs page and the home page are served as Markdown, their links full addresses, named by the page's head and by llms.txt" \
  "grep -q '^# The guide$' \"$host/website/dist/docs/guide.md\" && grep -q '](https://acme.github.io/acme-platform/docs/guide/)' \"$host/website/dist/index.md\" && grep -q 'type=\"text/markdown\"[^>]*href=\"/acme-platform/docs/guide.md\"' \"$host/website/dist/docs/guide/index.html\" && grep -q '(https://acme.github.io/acme-platform/docs/guide.md)' \"$host/website/dist/llms.txt\" && grep -q '(https://acme.github.io/acme-platform/index.md)' \"$host/website/dist/llms.txt\""
assert "the log feed is well-formed, with the skeleton's day as an entry, dated from git, in its category" \
  "python3 -c 'import sys, xml.dom.minidom; xml.dom.minidom.parse(sys.argv[1])' \"$host/website/dist/knowledge/log.xml\" && grep -q 'Initialization: 1</title>' \"$host/website/dist/knowledge/log.xml\" && grep -q '<published>' \"$host/website/dist/knowledge/log.xml\" && grep -q '<category term=\"Initialization\"/>' \"$host/website/dist/knowledge/log.xml\""
assert "the feed's entries are named by the bundle's base_iri" "grep -q '<id>https://acme.example/knowledge/log#' \"$host/website/dist/knowledge/log.xml\""
assert "the feed, the overview page and the text files name the bundle's licence" \
  "grep -q '<rights>CC BY 4.0</rights>' \"$host/website/dist/knowledge/log.xml\" && grep -q '<link rel=\"license\" href=\"https://creativecommons.org/licenses/by/4.0/\"/>' \"$host/website/dist/knowledge/log.xml\" && grep -q 'href=\"https://creativecommons.org/licenses/by/4.0/\"[^>]*>CC BY 4.0</a>' \"$host/website/dist/knowledge/index.html\" && grep -q 'offered under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)' \"$host/website/dist/llms.txt\" && grep -q 'offered under CC BY 4.0' \"$host/website/dist/llms-full.txt\""
assert "every page names the log feed" "grep -q 'type=\"application/atom+xml\"[^>]*href=\"/acme-platform/knowledge/log.xml\"' \"$host/website/dist/index.html\""
assert "the sync built the schema's pages and the data with their commands" \
  "grep -q 'building docs/elements with' \"$test_root/build.log\" && grep -q 'building data with' \"$test_root/build.log\""
for f in schema/index.html schema/Service/index.html schema/owner/index.html schema/String/index.html \
         browse/index.html browse/acme.sqlite browse/metadata.json; do
  assert "dist/$f is there" "[[ -f \"$host/website/dist/$f\" ]]"
done
dist="$host/website/dist"
assert "a class page leaves its diagram for the browser to draw, with the script that draws it" \
  "grep -q 'class=\"ktl-mermaid\"' \"$dist/schema/Service/index.html\" && grep -q '_astro/Mermaid' \"$dist/schema/Service/index.html\""
assert "a page with no diagram loads no mermaid" "! grep -q '_astro/Mermaid' \"$dist/schema/owner/index.html\""
assert "the YAML inside <details> is a code block" "grep -q 'data-language=\"yaml\"' \"$dist/schema/Service/index.html\""
assert "gen-doc's search wrapper is gone" "! grep -q 'data-search-exclude' \"$dist/schema/Service/index.html\""
assert "search leaves the schema's pages out" "! grep -q 'data-pagefind-body' \"$dist/schema/Service/index.html\""
assert "a type's title glued to its frontmatter is its title" "grep -q '<title>Type: String' \"$dist/schema/String/index.html\""
assert "a schema page links its neighbour by the neighbour's own name" "grep -q 'href=\"/acme-platform/schema/owner/\"' \"$dist/schema/Service/index.html\""
assert "the data page opens the database in Datasette Lite in a new tab, with its analytics off" \
  "grep -q 'lite.datasette.io/?url=' \"$dist/browse/index.html\" && grep -q 'analytics=off' \"$dist/browse/index.html\" && grep -q 'target=\"_blank\" rel=\"noopener\">Open in Datasette Lite' \"$dist/browse/index.html\""
assert "the data page describes the database from its metadata" "grep -q 'The services the platform runs' \"$dist/browse/index.html\""
assert "only the databases and their metadata are published" "[[ ! -e \"$dist/browse/notes.txt\" && ! -e \"$dist/browse/metadata.yaml\" ]]"
assert "the metadata is published without its plugins' settings" \
  "grep -q 'The services the platform runs' \"$dist/browse/metadata.json\" && ! grep -q 'not-for-the-site' \"$dist/browse/metadata.json\""
assert "a quoted diagram with words after its language is drawn" \
  "grep -q 'class=\"ktl-mermaid\"' \"$dist/docs/architecture/index.html\" && grep -q '_astro/Mermaid' \"$dist/docs/architecture/index.html\""
assert "a page and its retelling offer each other as reading levels, among the docs and in the bundle" \
  "grep -q 'aria-label=\"Reading levels\"' \"$dist/docs/guide/index.html\" && grep -q 'href=\"/acme-platform/simple/\">In short</a>' \"$dist/docs/guide/index.html\" && grep -q 'href=\"/acme-platform/docs/guide/\">Full</a>' \"$dist/simple/index.html\" && grep -q 'href=\"/acme-platform/knowledge/services/example-service-a-simple/\">Ages 13 to 18</a>' \"$dist/knowledge/services/example-service-a/index.html\" && grep -q 'href=\"/acme-platform/knowledge/services/example-service-a/\">Full</a>' \"$dist/knowledge/services/example-service-a-simple/index.html\" && ! grep -q 'Reading levels' \"$dist/docs/architecture/index.html\""
assert "a schema page's old address sends the browser on to its page" \
  "grep -q 'http-equiv=\"refresh\" content=\"0;url=/acme-platform/schema/Service/\"' \"$dist/elements/Service/index.html\""
assert "the About page's old address sends the browser on to its page" "grep -q 'url=/acme-platform/docs/about/\"' \"$dist/about/index.html\""
assert "the folder DOCS.exclude names is not on the site" "[[ ! -e \"$dist/docs/templates-linkml\" ]]"
assert "llms.txt lists the schema and the data" "grep -q '/schema/)' \"$dist/llms.txt\" && grep -q '/browse/)' \"$dist/llms.txt\""
assert "nothing of the template is left to commit" "[[ -z \$(git -C \"$host\" status --porcelain) ]]"

echo ""
echo "Step 4 again: the bare shape, with no README, docs or changelog, and the configuration as Step 1 left it"
(
  cd "$host"
  git rm -rq README.md docs CHANGELOG.md
  git checkout -q HEAD~1 -- website/site.config.mjs
  git commit -q -m "a bare host"
)
build
assert "the home page is there, from the bundle's own introduction" "[[ -f \"$host/website/dist/index.html\" ]] && grep -q 'Acme Platform' \"$host/website/dist/index.html\""
assert "no docs pages" "[[ ! -d \"$host/website/dist/docs\" ]]"
assert "the home page offers no architecture page" "! grep -q 'docs/architecture/' \"$host/website/dist/index.html\""
assert "the home page offers no schema" "! grep -q '/acme-platform/schema/' \"$host/website/dist/index.html\""
assert "no release pages" "[[ ! -d \"$host/website/dist/changelog\" ]]"
assert "no schema pages and no data page" "[[ ! -d \"$host/website/dist/schema\" && ! -d \"$host/website/dist/browse\" ]]"
assert "the bundle's pages, the health page and the graph are still there" \
  "[[ -f \"$host/website/dist/knowledge/index.html\" && -f \"$host/website/dist/health/index.html\" && -f \"$host/website/dist/graph/index.html\" ]]"
assert "the Knowledge Trust Ladder logo is the favicon" "cmp -s \"$host/website/dist/favicon.svg\" \"$skill/templates/website/src/assets/knowledge-trust-ladder-logo.svg\""

echo ""
if [[ "$fail" -eq 0 ]]; then
  echo "Website smoke test: PASS"
else
  echo "Website smoke test: FAIL"
  exit 1
fi
