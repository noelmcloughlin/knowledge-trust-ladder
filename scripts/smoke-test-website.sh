#!/usr/bin/env bash
# Copies the ktl-website templates into a throwaway host built from the
# sidecar's own dummy skeleton, as the skill's Steps 1 to 4 would. It builds
# the site twice: once with a README, docs pages, a changelog, figures, a
# LinkML schema, retellings, the federation workflow, a mirrored source and
# data, and once with none of them. No setting names any of those: the site must find each, and show
# none of what is not there. So both shapes of host are proved before a
# template change reaches one. This repository's own site proves a fuller
# site.toml; this proves a bundle that is not this repository's.
#
# Usage: scripts/smoke-test-website.sh [--keep]   (--keep leaves the host behind)
# Needs: uv, git and python3, and the network for `uv lock`, for Hugo and
# Pagefind from PyPI, and for the two libraries the site fetches once.
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
for tool in uv git python3; do
  command -v "$tool" >/dev/null 2>&1 || { echo "$tool not found - the website smoke test needs uv, git and python3" >&2; exit 1; }
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
  printf '# Acme Platform\n\nThe platform Acme runs. See [the bundle](.lokf/knowledge/index.md), [the guide](docs/guide.md) and [the about page](/docs/about.md), the last from the root as GitHub reads it.\n' > README.md
  mkdir -p docs
  printf '# The guide\n\nHow to use the platform. See [the tutorial](how-to/first.md) and ![the map](img/map.png).\n' > docs/guide.md
  # Links that leave the docs folder, raw HTML GitHub would not show, and a
  # shortcode, which Hugo would otherwise run.
  cat >> docs/guide.md <<'MD'

## Out of the folder

See [the README](../README.md), [the first release](../CHANGELOG.md#100---2026-01-01) and <a href="about.md">About, in raw HTML</a>.

```text
A fenced [link](../README.md) stays as written.
```

<meta http-equiv="refresh" content="0;url=https://example.com/">
<p onclick="alert(1)" style="color:red">Click <a href="javascript:alert(1)">here</a> or press <kbd>Q</kbd>.</p>

Hugo shows {{< mention >}} as written.
MD
  printf '<!doctype html><title>A report</title><script>alert(1)</script>\n' > docs/report.html
  # shellcheck disable=SC2016 # literal backticks: a Markdown code fence
  printf '# Architecture\n\nHow the platform is built.\n\n> ```mermaid title="The platform"\n> flowchart LR\n>   web --> api\n> ```\n' > docs/architecture.md
  # A docs folder as an mkdocs site leaves it: an index.md, a folder with one
  # of its own, a figure, a page with a frontmatter title that tries to move
  # itself, and the templates and pages gen-doc keeps there, which are not pages.
  mkdir -p docs/how-to docs/img docs/templates-linkml docs/elements .assets
  printf '# Acme docs\n\nWhere to start.\n' > docs/index.md
  printf '# How-to guides\n\nTask by task.\n' > docs/how-to/index.md
  printf '# A first service\n\n## Quick start\n\nRun it.\n' > docs/how-to/first.md
  printf -- '---\ntitle: About Acme\nurl: /stolen/\ndraft: true\n---\n\n# About Acme\n\nWho runs the platform.\n' > docs/about.md
  printf 'not really a png\n' > docs/img/map.png
  printf '# Templates for gen-doc\n' > docs/templates-linkml/README.md
  printf '# Class: Old\n' > docs/elements/Old.md
  printf '<svg xmlns="http://www.w3.org/2000/svg"/>\n' > .assets/figure.svg
  # A retelling of the guide, and one of a concept, each for one audience.
  printf '# The guide, in short\n\nThis page is for readers aged 13 to 18.\n\nThe platform, in fewer words.\n' > docs/guide.en-simple.md
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
  # A source the ingest mirrored, as its committed lock records it.
  mkdir -p .lokf/mirror/vendor
  printf -- '---\norigin: https://vendor.example/page\n---\n\nThe vendor page.\n' > .lokf/mirror/vendor/page.md
  printf 'ingest_lock_version: 1\nentries:\n  vendor:\n    status: ok\n    items:\n      page:\n        path: .lokf/mirror/vendor/page.md\n        origin: https://vendor.example/page\n        version: "2.1"\n        retrieved_at: "2026-03-04T05:06:07Z"\n' > .lokf/ingest.lock.yaml
  python3 - .lokf/knowledge/services/example-service-a.md <<'PY'
import sys
path = sys.argv[1]
text = open(path, encoding="utf-8").read()
text = text.replace("\n---\n", "\nsources:\n- resource: .lokf/mirror/vendor/page.md\n  excerpt: The vendor page.\n---\n", 1)
open(path, "w", encoding="utf-8").write(text)
PY
  # The data, which its command writes on the first build. Its metadata
  # carries plugin settings that must not reach the site.
  cat > make-data.sh <<'SH'
mkdir -p data/browse
python3 - <<'PY'
import sqlite3
db = sqlite3.connect("data/browse/acme.sqlite")
db.execute("create table service (id text primary key, owner text)")
db.execute("insert into service values ('a', 'Acme')")
db.commit()
PY
printf 'plugins:\n  datasette-auth-tokens:\n    tokens: [SECRET-TOKEN]\ndatabases:\n  acme:\n    title: The services\n    plugins: {x: SECRET-DB}\n' > data/browse/metadata.yaml
printf 'create table service (id text);\n' > data/browse/schema.sql
SH
  printf 'data/\n' > .gitignore
  # A LinkML schema where linkml-sidecar keeps one, and a domain host's workflow.
  mkdir -p .linkml/src/acme_platform/schema .github/workflows
  cat > .linkml/src/acme_platform/schema/acme_platform.yaml <<'YAML'
id: https://acme.example/schema
name: acme_platform
title: Acme platform schema
description: What the platform runs.
prefixes:
  acme: https://acme.example/schema/
  linkml: https://w3id.org/linkml/
default_prefix: acme
default_range: string
imports:
  - linkml:types
classes:
  Service:
    description: A service the platform runs.
    attributes:
      owner:
        description: Who owns the service.
      status:
        range: ServiceStatus
enums:
  ServiceStatus:
    permissible_values:
      LIVE:
      RETIRED:
YAML
  printf 'name: Knowledge federation\n' > .github/workflows/knowledge-federation.yaml
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
    -- -e '<REPO_' -e '<PROJ_' website/site.toml website/README.md
  git add -A
  git commit -q -m "the site"
)
assert "every template file landed" \
  "[[ \$(find \"$skill/templates/website\" -type f | wc -l) -eq \$(find \"$host/website\" -type f | wc -l) ]]"
assert "no placeholder is left in the two files that carry one" "! grep -q -e '<REPO_' -e '<PROJ_' \"$host/website/site.toml\" \"$host/website/README.md\""

echo ""
echo "Step 4: build, with everything the site can find, and site.toml as Step 1 left it but for two old addresses and the data"
build() {
  # The whole log on a failure, its last line otherwise.
  if (cd "$host/website" && bash scripts/build.sh > "$test_root/build.log" 2>&1); then
    tail -n 1 "$test_root/build.log"
  else
    echo "FAIL: the build failed; its log:"
    sed 's/^/    /' "$test_root/build.log"
    fail=1
  fi
}
python3 - "$host/website/site.toml" <<'PY'
import sys
path = sys.argv[1]
text = open(path, encoding="utf-8").read()
text = text.replace('repo = "https://github.com/acme/acme-platform"\n', 'repo = "https://github.com/acme/acme-platform"\nbrowse = "data/browse"\nbrowseBuild = "bash make-data.sh"\n', 1)
open(path, "w", encoding="utf-8").write(text + '\n[params.redirects]\n"about" = "docs/about.md"\n"schema/*" = "schema/*"\n')
PY
git -C "$host" commit -qam "two old addresses, and the data"
build
dist="$host/website/dist"
for f in index.html knowledge/index.html knowledge/services/example-service-a/index.html health/index.html graph/index.html \
         knowledge/concepts.jsonld knowledge/graph.json knowledge/graph.nt knowledge/datasets.jsonld \
         knowledge/services/example-service-a.md knowledge/services/example-service-a.jsonld \
         knowledge/log.xml llms.txt llms-full.txt docs/index.html docs/guide/index.html docs/guide.md docs/how-to/index.html \
         docs/how-to/first/index.html docs/img/map.png assets/figure.svg changelog/index.html changelog/version/1-0-0/index.html \
         og/index.png brand/knowledge-trust-ladder-logo.svg pagefind/pagefind.js \
         schema/index.html schema/classes/Service/index.html schema/enums/ServiceStatus/index.html schema/slots/owner/index.html \
         schema/types/String/index.html schema/acme_platform.yaml; do
  assert "dist/$f is there" "[[ -f \"$dist/$f\" ]]"
done
assert "the link check passed" "grep -q 'check-links: .* 0 broken link' \"$test_root/build.log\""
assert "the home page is the README's" "grep -q 'The platform Acme runs' \"$dist/index.html\""
assert "the README's link to the guide goes to its page" "grep -q 'href=\"\\?/acme-platform/docs/guide/\"\\?' \"$dist/index.html\""
assert "the home page leads with the schema" "grep -q 'On exhibit' \"$dist/index.html\" && grep -q 'Acme platform schema' \"$dist/index.html\""
assert "four buttons are links (schema, bundle, architecture, quick start) and the glossary's, which the bundle lacks, is greyed" \
  "grep -q 'href=\"\\?/acme-platform/schema/>The schema' \"$dist/index.html\" && grep -q 'href=\"\\?/acme-platform/docs/architecture/' \"$dist/index.html\" && grep -q 'href=\"\\?/acme-platform/docs/how-to/first/#quick-start' \"$dist/index.html\" && [[ \$(grep -o 'button--missing' \"$dist/index.html\" | wc -l) -eq 1 ]] && grep -q 'The bundle has no glossary group' \"$dist/index.html\""
assert "the header shows the Knowledge Trust Ladder logo" "grep -q 'brand/knowledge-trust-ladder-logo.svg' \"$dist/index.html\""
assert "a concept page carries its trust label" "grep -qi 'checked' \"$dist/knowledge/services/example-service-a/index.html\""
assert "a concept page links the graph opened on it" "grep -q 'graph/?concept=services%2fexample-service-a' \"$dist/knowledge/services/example-service-a/index.html\""
assert "a concept page links its file's history at the built commit" \
  "grep -q 'https://github.com/acme/acme-platform/commits/[0-9a-f]\\{40\\}/.lokf/knowledge/services/example-service-a.md' \"$dist/knowledge/services/example-service-a/index.html\""
assert "a release page links the repository, the docs and the bundle at the release's tag, and the release" \
  "grep -q 'https://github.com/acme/acme-platform/tree/v1.0.0/docs' \"$dist/changelog/version/1-0-0/index.html\" && grep -q 'https://github.com/acme/acme-platform/tree/v1.0.0/.lokf/knowledge' \"$dist/changelog/version/1-0-0/index.html\" && grep -q 'https://github.com/acme/acme-platform/releases/tag/v1.0.0' \"$dist/changelog/version/1-0-0/index.html\""
assert "llms.txt offers llms-full.txt, the docs pages as Markdown and the schema" \
  "grep -q '/llms-full.txt)' \"$dist/llms.txt\" && grep -q '(https://acme.github.io/acme-platform/docs/guide.md)' \"$dist/llms.txt\" && grep -q '/schema/acme_platform.yaml)' \"$dist/llms.txt\""
assert "the log feed is well-formed" "python3 -c 'import sys, xml.dom.minidom; xml.dom.minidom.parse(sys.argv[1])' \"$dist/knowledge/log.xml\""
assert "every page names the log feed" "grep -q 'application/atom+xml[^>]*knowledge/log.xml' \"$dist/index.html\""
assert "every page carries the policy that stops raw HTML running a script" "grep -q \"Content-Security-Policy.*script-src https://acme.github.io/acme-platform/js/\" \"$dist/docs/guide/index.html\""
assert "a docs folder's index.md is that folder's page, and names its group" \
  "grep -q 'Task by task' \"$dist/docs/how-to/index.html\" && grep -q '<summary>How-to guides</summary>' \"$dist/docs/guide/index.html\" && grep -q '<summary>Guides</summary>' \"$dist/docs/guide/index.html\""
assert "a docs page's frontmatter gives its title and cannot move or hide it" \
  "grep -q '<h1>About Acme</h1>' \"$dist/docs/about/index.html\" && [[ ! -e \"$dist/stolen\" ]]"
assert "a figure in the docs folder is served from the site, and a link between docs pages goes to the page" \
  "grep -q 'src=\"\\?/acme-platform/docs/img/map.png' \"$dist/docs/guide/index.html\" && grep -q 'href=\"\\?/acme-platform/docs/how-to/first/' \"$dist/docs/guide/index.html\""
assert "gen-doc's own folders under docs/ are not pages" "[[ ! -e \"$dist/docs/templates-linkml/readme\" && ! -e \"$dist/docs/elements/old\" ]]"
assert "a quoted diagram with words after its language is drawn, and a page with none loads no mermaid" \
  "grep -q 'class=\"\\?mermaid' \"$dist/docs/architecture/index.html\" && grep -q 'js/vendor/mermaid' \"$dist/docs/architecture/index.html\" && ! grep -q 'js/vendor/mermaid' \"$dist/docs/guide/index.html\""
assert "a class page has gen-doc's diagram and its YAML as a code block, without the mkdocs wrapper" \
  "grep -q 'class=\"\\?mermaid' \"$dist/schema/classes/Service/index.html\" && grep -q '<summary>YAML</summary>' \"$dist/schema/classes/Service/index.html\" && ! grep -q 'data-search-exclude' \"$dist/schema/classes/Service/index.html\""
assert "search leaves the schema's slots and types out" "! grep -q 'data-pagefind-body' \"$dist/schema/slots/owner/index.html\" && grep -q 'data-pagefind-body' \"$dist/schema/classes/Service/index.html\""
assert "a page and its retelling offer each other, among the docs and in the bundle, and a page with none offers nothing" \
  "grep -q 'docs/guide.en-simple/[^>]*>For readers aged 13 to 18</a>' \"$dist/docs/guide/index.html\" && grep -q 'docs/guide/[^>]*>Full</a>' \"$dist/docs/guide.en-simple/index.html\" && grep -q 'example-service-a-simple/[^>]*>For readers aged 13 to 18</a>' \"$dist/knowledge/services/example-service-a/index.html\" && ! grep -q 'Reading level' \"$dist/docs/architecture/index.html\""
assert "a retelling has no line in the navigation" "! grep -q 'guide.en-simple' \"$dist/docs/architecture/index.html\""
assert "a docs page's Markdown has every address made full and its fenced code as written" \
  "grep -qF '[the README](https://acme.github.io/acme-platform/)' \"$dist/docs/guide.md\" && grep -qF '[the tutorial](https://acme.github.io/acme-platform/docs/how-to/first/)' \"$dist/docs/guide.md\" && grep -qF 'href=\"https://acme.github.io/acme-platform/docs/about/\"' \"$dist/docs/guide.md\" && grep -qF 'A fenced [link](../README.md)' \"$dist/docs/guide.md\""
assert "the README's Markdown is served at index.md, from its title, and the page names it" \
  "head -n 1 \"$dist/index.md\" | grep -qx '# Acme Platform' && grep -q 'text/markdown[^>]*acme-platform/index.md' \"$dist/index.html\""
assert "a link from the root, one to a release's heading and one in raw HTML go to their pages" \
  "grep -q 'href=\"\\?/acme-platform/docs/about/\"\\?>the about page' \"$dist/index.html\" && grep -q 'href=\"\\?/acme-platform/changelog/version/1-0-0/\"\\?>the first release' \"$dist/docs/guide/index.html\" && grep -q 'href=\"\\?/acme-platform/docs/about/\"\\?>About, in raw HTML' \"$dist/docs/guide/index.html\""
assert "raw HTML GitHub would not show is shown as text, and no handler, style or javascript: address is left" \
  "grep -q '&lt;meta http-equiv' \"$dist/docs/guide/index.html\" && ! grep -qiE '<meta http-equiv=\"?refresh|onclick|javascript:|color:red' \"$dist/docs/guide/index.html\" && grep -q '<kbd>Q</kbd>' \"$dist/docs/guide/index.html\" && grep -q 'clean-html: docs/guide/index.html: <meta' \"$test_root/build.log\""
assert "a shortcode in a docs page is shown as written" "grep -q '{{&lt; mention' \"$dist/docs/guide/index.html\""
assert "an HTML document in the docs folder is not served" "[[ ! -e \"$dist/docs/report.html\" ]]"
assert "a mirrored source names its origin, version and fetch day, and links its own path" \
  "grep -q 'A copy of <a href=\"\\?https://vendor.example/page' \"$dist/knowledge/services/example-service-a/index.html\" && grep -q 'version <code>2.1</code>, fetched 2026-03-04' \"$dist/knowledge/services/example-service-a/index.html\" && grep -q 'blob/[0-9a-f]\\{40\\}/.lokf/mirror/vendor/page.md' \"$dist/knowledge/services/example-service-a/index.html\""
assert "the data's command ran, and its database and metadata are served, without plugin settings or the folder's other files" \
  "[[ -f \"$dist/browse/acme.sqlite\" && -f \"$dist/browse/metadata.json\" && ! -e \"$dist/browse/schema.sql\" ]] && ! grep -q SECRET \"$dist/browse/metadata.json\" && grep -q 'building data/browse with' \"$test_root/build.log\""
assert "the data page opens each database in Datasette Lite, and the navigation and llms.txt name it" \
  "grep -q 'lite.datasette.io/?analytics=off&amp;metadata=https%3A%2F%2Facme.github.io%2Facme-platform%2Fbrowse%2Fmetadata.json&amp;url=https%3A%2F%2Facme.github.io%2Facme-platform%2Fbrowse%2Facme.sqlite#/acme' \"$dist/browse/index.html\" && grep -q '>The services<' \"$dist/browse/index.html\" && grep -q 'Browse the data</a>' \"$dist/index.html\" && grep -q '/browse/)' \"$dist/llms.txt\""
assert "a schema page's old address sends the browser on to its page, with no setting for /elements/, and so does the About page's" \
  "grep -q 'url=/acme-platform/schema/classes/Service/' \"$dist/elements/Service/index.html\" && grep -q 'url=/acme-platform/schema/' \"$dist/elements/index.html\" && grep -q 'url=/acme-platform/schema/classes/Service/' \"$dist/schema/Service/index.html\" && grep -q 'url=/acme-platform/docs/about/' \"$dist/about/index.html\""
assert "the graph page offers the workspace on a domain host" "grep -q 'graph=workspace' \"$dist/graph/index.html\""
assert "nothing of the build is left to commit" "[[ -z \$(git -C \"$host\" status --porcelain) ]]"

echo ""
echo "Step 4 again: the bare shape, with a bundle and nothing else, and site.toml as Step 1 left it"
(
  cd "$host"
  git rm -rq README.md docs CHANGELOG.md .assets .linkml .github
  git checkout -q HEAD~1 -- website/site.toml
  git commit -q -m "a bare host"
)
build
assert "the link check passed" "grep -q 'check-links: .* 0 broken link' \"$test_root/build.log\""
assert "the home page is there, from the bundle's own introduction" "[[ -f \"$dist/index.html\" ]] && grep -q '<h1>Acme Platform</h1>' \"$dist/index.html\""
assert "no docs pages, no release pages, no schema pages and their old addresses, and no data" "[[ ! -d \"$dist/docs\" && ! -d \"$dist/changelog\" && ! -d \"$dist/schema\" && ! -d \"$dist/elements\" && ! -d \"$dist/browse\" && ! -e \"$dist/index.md\" ]]"
assert "the home page keeps its five buttons, with the bundle's a link and the schema's, the architecture page's and the quick start's greyed" \
  "[[ \$(grep -o 'button--missing' \"$dist/index.html\" | wc -l) -ge 3 ]] && grep -q 'This repository holds no LinkML schema' \"$dist/index.html\" && grep -q 'This repository has no docs/architecture.md' \"$dist/index.html\" && ! grep -q 'On exhibit' \"$dist/index.html\""
assert "the navigation has no Schema part and no changelog" "! grep -q '>Schema</summary>' \"$dist/index.html\" && ! grep -q 'changelog/' \"$dist/index.html\""
assert "the graph page greys the workspace" "grep -q 'aria-disabled=\"\\?true\"\\?[^>]*>The workspace' \"$dist/graph/index.html\" && ! grep -q 'graph=workspace' \"$dist/graph/index.html\""
assert "the bundle's pages, the health page and the graph are still there" \
  "[[ -f \"$dist/knowledge/index.html\" && -f \"$dist/health/index.html\" && -f \"$dist/graph/index.html\" ]]"

echo ""
if [[ "$fail" -eq 0 ]]; then
  echo "Website smoke test: PASS"
else
  echo "Website smoke test: FAIL"
  exit 1
fi
