#!/usr/bin/env bash
# What this host can and cannot do for the ktl-website skill: one read-only
# screen before the site is laid down, built or deployed. The skill runs it
# first and repeats its summary line in the hand-off, so a missing tool
# disables a step out loud instead of failing a build.
#
# Each line is `ok`, `warn`, `missing` or `info`, then one summary line:
#   Preflight: <n> missing, <m> warnings. Missing disables: <steps>.
# Exit 0 always: the skill reads the lines; nothing here is a gate.
#
# Bash 3.2 and POSIX tools only, as the sidecar's preflight, so it runs on
# macOS's stock bash and on Git for Windows.
#
# Usage: website-preflight.sh [repo-root]   (default: the nearest ancestor of
# the current directory holding `.lokf/`, else the current directory)
[ -n "${BASH_VERSION:-}" ] || { echo "run this with bash: bash ${0##*/} [repo-root]" >&2; exit 2; }
set -u

missing=0; warns=0; disables=""
line() { printf '%-8s%-13s%s\n' "$1" "$2" "$3"; }
ok()   { line ok "$1" "$2"; }
info() { line info "$1" "$2"; }
warn() { line warn "$1" "$2"; warns=$((warns + 1)); }
miss() {
  line missing "$1" "$2"; missing=$((missing + 1))
  case "; $disables; " in *"; ${3:-}; "*) ;; *) [ -n "${3:-}" ] && disables="${disables}${disables:+; }$3" ;; esac
}
have() { command -v "$1" >/dev/null 2>&1; }
skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"

# ---- root ------------------------------------------------------------------
root="${1:-}"
if [ -z "$root" ]; then
  d="$(pwd -P)"; root="$d"
  while [ "$d" != "/" ]; do
    if [ -d "$d/.lokf" ]; then root="$d"; break; fi
    d="$(dirname "$d")"
  done
fi
root="$(cd "$root" 2>/dev/null && pwd -P)" || { echo "no such directory: ${1:-.}" >&2; exit 2; }

# ---- host ------------------------------------------------------------------
os="$(uname -s 2>/dev/null || echo unknown)"
case "$os" in
  Linux) host=Linux ;;
  Darwin) host=macOS ;;
  MINGW*|MSYS*|CYGWIN*) host="Windows (Git for Windows bash)" ;;
  *) host="$os" ;;
esac
if have python3; then py=python3; elif have python; then py=python; else py=""; fi
printf 'Website preflight for %s\n' "$root"
ok host "$host, bash ${BASH_VERSION%%(*}; python: ${py:-none (use uv run python for the placeholders)}"

# ---- the bundle and its sidecar ----------------------------------------------
bundle="$root/.lokf/knowledge"
if [ -f "$bundle/index.md" ]; then
  n="$(find "$bundle/" -name '*.md' -not -path '*/.obsidian/*' -not -name index.md -not -name log.md | wc -l | tr -d ' ')"
  ok bundle ".lokf/knowledge, $n concepts"
else
  miss bundle "no .lokf/knowledge/index.md under $root - run ktl-sidecar first" "every step"
fi
if [ -f "$root/.lokf/scripts/knowledge-preflight.sh" ]; then
  verdict="$(bash "$root/.lokf/scripts/knowledge-preflight.sh" "$root" 2>/dev/null | tail -n 1)"
  case "$verdict" in
    "Preflight: 0 missing"*) ok sidecar "the sidecar's preflight: $verdict" ;;
    Preflight:*) warn sidecar "the sidecar's preflight says: $verdict - settle that first; the site builds from what the sidecar's scripts report" ;;
    *) warn sidecar "the sidecar's preflight printed no summary line - run it by hand: bash .lokf/scripts/knowledge-preflight.sh" ;;
  esac
else
  info sidecar "no .lokf/scripts/knowledge-preflight.sh: a sidecar older than 0.30.0, or none - the ktl-sidecar repair lays it down"
fi
# The concept pages show the labels knowledge-report.sh prints, so the site
# never works a label out a second way; without the script there is no page.
if [ -f "$root/.lokf/scripts/knowledge-report.sh" ]; then
  health="$(cd "$root" && bash .lokf/scripts/knowledge-report.sh --root "$root" health 2>/dev/null | tail -n 1)"
  if [ -n "$health" ]; then ok report "knowledge-report.sh: $health"; else warn report "knowledge-report.sh printed no health line - run it by hand: bash .lokf/scripts/knowledge-report.sh health"; fi
else
  miss report "no .lokf/scripts/knowledge-report.sh - the concept pages take their trust labels from it; run the ktl-sidecar repair (sidecar 0.30.0 or later)" "Step 4's build and Step 5's workflow"
fi

# ---- the toolkit -------------------------------------------------------------
# The sync runs `lokf export` with `uv run --frozen`, and the workflow installs
# the toolkit with `uv sync --locked`: both need the lock file, and the
# workflow needs it committed.
ingit=0
if have git && git -C "$root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then ingit=1; fi
if have uv; then
  if [ ! -f "$root/.lokf/pyproject.toml" ]; then
    miss toolkit "no .lokf/pyproject.toml - run ktl-sidecar first" "Step 4's build"
  elif [ ! -f "$root/.lokf/uv.lock" ]; then
    miss toolkit "no .lokf/uv.lock - the sync runs lokf export with uv run --frozen; run uv lock in .lokf/ and commit the file" "Step 4's build and Step 5's workflow"
  elif [ "$ingit" = 1 ] && [ -z "$(git -C "$root" ls-files .lokf/uv.lock 2>/dev/null | head -n 1)" ]; then
    warn toolkit "uv $(uv --version 2>/dev/null | awk '{print $2}'); .lokf/uv.lock is not in git - the workflow installs the toolkit with uv sync --locked and fails without it; commit the file"
  else
    ok toolkit "uv $(uv --version 2>/dev/null | awk '{print $2}'); .lokf/uv.lock present"
  fi
else
  miss toolkit "uv not found (docs.astral.sh/uv) - the sync runs lokf export through it" "Step 4's build"
fi

# ---- node and npm ------------------------------------------------------------
if have node; then
  v="$(node --version 2>/dev/null)"; v="${v#v}"
  major="${v%%.*}"; rest="${v#*.}"; minor="${rest%%.*}"
  if [ "${major:-0}" -gt 22 ] || { [ "${major:-0}" -eq 22 ] && [ "${minor:-0}" -ge 12 ]; }; then
    ok node "node $v"
  else
    miss node "node $v is older than 22.12, the oldest Astro runs on - install a newer Node.js (nodejs.org, or nvm)" "Step 4's build"
  fi
else
  miss node "node not found - install Node.js 22.12 or later (nodejs.org, or nvm); the workflow brings its own" "Step 4's build"
fi
if have npm; then ok npm "npm $(npm --version 2>/dev/null)"; else miss npm "npm not found - it comes with Node.js" "Step 4's build"; fi

# ---- git and the forge --------------------------------------------------------
slug=""; branch=""
if [ "$ingit" = 1 ]; then
  remote="$(git -C "$root" remote get-url origin 2>/dev/null || true)"
  # The default branch: what origin says, else main or master if origin has one, else the branch checked out.
  branch="$(git -C "$root" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')"
  if [ -z "$branch" ]; then
    for b in main master; do
      if git -C "$root" rev-parse -q --verify "refs/remotes/origin/$b" >/dev/null 2>&1; then branch="$b"; break; fi
    done
  fi
  [ -z "$branch" ] && branch="$(git -C "$root" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
  case "$remote" in
    *github.com[:/]*)
      slug="$(printf '%s' "$remote" | sed -E 's#^(https?://[^/]+/|git@[^:]+:|ssh://git@[^/]+/)##; s#\.git$##; s#/$##')"
      ok git "github.com, $slug, default branch ${branch:-unknown}: REPO, SITE and BASE follow from it" ;;
    "") info git "no origin remote - the site builds; the workflow and the links to files need one" ;;
    *) info git "origin is not github.com ($remote) - the site builds; Step 5's workflow is GitHub Actions, and links to files name github.com" ;;
  esac
  if git -C "$root" check-ignore -q .lokf 2>/dev/null; then
    warn git ".lokf/ is gitignored - the workflow builds from the checkout, which lacks the bundle; build the site locally and skip Step 5"
  fi
else
  info git "no git: the site builds from the files; the workflow does not apply, and a link to a file cannot name a commit"
fi

# ---- pages: another publisher? ---------------------------------------------
# Two publishers overwrite each other's site, so the deploy job stays off
# where one exists; the site still builds.
publishers=""
own_wf="$skill_dir/templates/github/knowledge-website.yaml"; own_found=""
for wf in "$root"/.github/workflows/*.yml "$root"/.github/workflows/*.yaml; do
  [ -f "$wf" ] || continue
  # This skill's own workflow, under its name or another, publishes nothing new.
  if [ "${wf##*/}" = knowledge-website.yaml ] || { [ -f "$own_wf" ] && cmp -s "$wf" "$own_wf"; }; then
    own_found=".github/workflows/${wf##*/}"; continue
  fi
  if grep -qE 'deploy-pages|upload-pages-artifact|gh-pages|gh-deploy|github-pages-deploy-action' "$wf"; then
    publishers="${publishers}${publishers:+, }.github/workflows/${wf##*/}"
  fi
done
[ -f "$root/CNAME" ] && publishers="${publishers}${publishers:+, }a CNAME file at the root"
[ -f "$root/docs/CNAME" ] && publishers="${publishers}${publishers:+, }docs/CNAME"
if [ -f "$root/mkdocs.yml" ] && grep -q '^site_url:' "$root/mkdocs.yml"; then
  publishers="${publishers}${publishers:+, }mkdocs.yml with a site_url"
fi
pages_api=""
if have gh && [ -n "$slug" ] && gh auth status >/dev/null 2>&1; then
  # A 404 means Pages is not on yet, and gh prints the error body; only a success counts.
  pages_api="$(gh api "repos/$slug/pages" --jq '"Pages is on: built from \(.build_type)" + (if .source.branch then ", branch " + .source.branch else "" end) + (if .cname then ", custom domain " + .cname else "" end)' 2>/dev/null)" || pages_api=""
fi
if [ -n "$publishers" ]; then
  warn pages "another publisher: $publishers - the site builds, but leave KNOWLEDGE_WEBSITE_ENABLED unset here until that publisher is retired (references/deploy.md)"
elif [ -n "$pages_api" ]; then
  info pages "$pages_api"
else
  ok pages "no other Pages publisher found${slug:+; gh api repos/$slug/pages says whether Pages is on}"
fi

# ---- website/: not yet, this skill's, or someone else's -----------------------
# The three files the host owns are never compared: site.config.mjs,
# README.md and src/styles/custom.css. Every other file is a copy of a
# template, and a difference is a deliberate edit or a bump not yet copied.
if [ -d "$root/website" ]; then
  if [ -f "$root/website/site.config.mjs" ]; then
    drift=""; tdir="$skill_dir/templates/website"
    if [ ! -d "$tdir" ]; then
      warn website "website/ installed, but this skill's templates/website folder is missing beside its SKILL.md, so the copies cannot be compared - reinstall the skill"
    else
      while IFS= read -r f; do
        rel="${f#"$tdir"/}"
        case "$rel" in site.config.mjs|README.md|src/styles/custom.css) continue ;; esac
        dst="$root/website/$rel"; [ "$rel" = gitignore ] && dst="$root/website/.gitignore"
        if [ ! -f "$dst" ]; then drift="${drift}${drift:+, }$rel (missing)"
        elif ! cmp -s "$f" "$dst"; then drift="${drift}${drift:+, }$rel"; fi
      done < <(find "$tdir" -type f | sort)
      if [ -z "$drift" ]; then
        ok website "website/ installed, and its files match this skill's templates"
      else
        warn website "website/ installed; differs from the templates: $drift - a deliberate edit, or a template bump not yet copied (repair mode)"
      fi
    fi
    if [ -n "$own_found" ]; then
      info workflow "$own_found present; the deploy runs once KNOWLEDGE_WEBSITE_ENABLED is true"
    else
      info workflow "no .github/workflows/knowledge-website.yaml - Step 5 lays it down"
    fi
  else
    miss website "website/ exists and is not this skill's (no site.config.mjs) - this skill writes nothing into it; ask before going on" "Step 1 and every step after it"
  fi
else
  ok website "no website/ yet"
fi

# ---- what the site can show beside the bundle ---------------------------------
if [ -f "$root/README.md" ]; then
  title="$(awk '/^[[:space:]]*(```|~~~)/ { fence = !fence; next } !fence && /^# / { sub(/^# /, ""); print; exit }' "$root/README.md")"
  if [ -n "$title" ]; then
    ok readme "README.md, titled \"$title\": the home page"
  else
    warn readme "README.md has no '# ' title - the home page opens with the bundle's own introduction instead (HOME.source)"
  fi
else
  info readme "no README.md - the home page opens with the bundle's own introduction"
fi
if [ -d "$root/docs" ]; then
  if [ "$ingit" = 1 ]; then
    n="$(git -C "$root" ls-files --cached --others --exclude-standard -- docs 2>/dev/null | grep -c '\.md$' || true)"
  else
    n="$(find "$root/docs/" -name '*.md' | wc -l | tr -d ' ')"
  fi
  ok docs "docs/, $n Markdown page(s) as git sees them: the Guide topic"
else
  info docs "no docs/ - the Guide topic lists the home page alone (DOCS)"
fi
if [ -f "$root/CHANGELOG.md" ]; then
  n="$(grep -cE '^## \[[^]]+\] - [0-9]{4}-[0-9]{2}-[0-9]{2}' "$root/CHANGELOG.md" || true)"
  if [ "${n:-0}" -gt 0 ]; then
    ok changelog "CHANGELOG.md, $n released version(s): the Releases topic"
  else
    warn changelog "CHANGELOG.md has no '## [version] - date' heading, so no release page can be made from it (Keep a Changelog form; CHANGELOG)"
  fi
else
  info changelog "no CHANGELOG.md - no Releases topic"
fi
if [ -d "$root/.assets" ]; then
  n="$(find "$root/.assets/" -type f | wc -l | tr -d ' ')"
  logos="$(find "$root/.assets/" -maxdepth 1 -type f -iname '*logo*' | sed "s#^$root/##" | sort | tr '\n' ' ')"
  ok assets ".assets/, $n file(s)${logos:+; logo candidates: ${logos% }}"
else
  info assets "no .assets/ folder - set ASSETS to the figures folder and LOGO to a logo file, or leave both out"
fi

# These lines find the schema's pages and the data as scripts/config.mjs
# finds them. The schema's pages come from a justfile with a gen-doc recipe,
# in the root, a linkmo project's folder or .linkml/. The data comes from a
# build-browse recipe, and its databases stay off the site until a person
# sets BROWSE. A justfile goes by any name just reads, and a recipe line may
# carry parameters and their defaults. An assignment such as
# `gen-doc := ...` is not a recipe.
justfile_in() {
  for f in "$1"/.[Jj][Uu][Ss][Tt][Ff][Ii][Ll][Ee] "$1"/[Jj][Uu][Ss][Tt][Ff][Ii][Ll][Ee]; do
    if [ -f "$f" ]; then printf '%s\n' "${f##*/}"; return 0; fi
  done
}
has_recipe() { [ -f "$1" ] && grep -qE "^@?$2([[:space:]]+[^:=[:space:]][^:]*)?:([^=]|\$)" "$1"; }
linkmo=""
if [ -f "$root/.copier-answers.linkmo.yml" ]; then
  linkmo="$(sed -n "s/^linkmo_dir:[[:space:]]*[\"']\{0,1\}\([A-Za-z0-9._-]*\).*/\1/p" "$root/.copier-answers.linkmo.yml" | head -n 1)"
  { [ -n "$linkmo" ] && [ -d "$root/$linkmo" ]; } || linkmo=""
fi
schema_cmd=""; schema_dir=""
for d in . ${linkmo:+"$linkmo"} .linkml; do
  jf="$(justfile_in "$root/$d")"
  if [ -n "$jf" ] && has_recipe "$root/$d/$jf" gen-doc; then
    if [ "$d" = . ]; then schema_dir="docs/elements"; schema_cmd="just gen-doc"
    else schema_dir="$d/docs/elements"; schema_cmd="just --justfile $d/$jf gen-doc"; fi
    break
  fi
done
if [ -n "$schema_cmd" ]; then
  ok schema "a gen-doc recipe: the Schema topic, from $schema_dir, which the sync builds with $schema_cmd (SCHEMA)"
else
  info schema "no justfile with a gen-doc recipe in the root, a linkmo project or .linkml/ - no Schema topic (SCHEMA)"
fi
browse_cmd=""
if [ -n "$linkmo" ]; then
  jf="$(justfile_in "$root/$linkmo")"
  if [ -n "$jf" ] && has_recipe "$root/$linkmo/$jf" build-browse; then browse_cmd="just --justfile $linkmo/$jf build-browse"; fi
fi
if [ -z "$browse_cmd" ]; then
  jf="$(justfile_in "$root")"
  if [ -n "$jf" ] && has_recipe "$root/$jf" build-browse; then browse_cmd="just build-browse"; fi
fi
if [ -n "$browse_cmd" ]; then
  info data "a build-browse recipe ($browse_cmd): the data page shows its databases when BROWSE names the folder it writes; left out, BROWSE is null"
else
  info data "no build-browse recipe - no data page unless BROWSE names a folder of SQLite databases"
fi
if [ -n "$schema_cmd" ] || [ -n "$browse_cmd" ]; then
  if have just; then
    ok just "just $(just --version 2>/dev/null | awk '{print $2}'): the sync runs the recipes above"
  else
    warn just "just not found - the sync builds the schema's pages, and the data once BROWSE is set, through just; install it (uv tool install rust-just), or set SCHEMA to null; the workflow installs its own"
  fi
fi

lint=""
for f in "$root"/.markdownlint* "$root/lychee.toml" "$root/.codespellrc"; do
  [ -e "$f" ] && lint="${lint}${lint:+ }${f#"$root"/}"
done
if [ -n "$lint" ]; then
  info lint "lint configs to exclude website/'s generated folders from (Step 2): $lint"
else
  info lint "no Markdown lint config at the root, so Step 2 has nothing to exclude"
fi

# ---- session ---------------------------------------------------------------
unattended=""
for v in CI GITHUB_ACTIONS GITLAB_CI TF_BUILD; do
  val="${!v:-}"; [ -n "$val" ] && unattended="${unattended}${unattended:+, }$v"
done
if [ -n "$unattended" ]; then
  info session "unattended ($unattended set): the placeholders and the options need a person's values, so stop after this screen"
else
  info session "attended: a person can answer item by item"
fi

printf 'Preflight: %d missing, %d warning(s).%s\n' "$missing" "$warns" "${disables:+ Missing disables: $disables.}"
exit 0
