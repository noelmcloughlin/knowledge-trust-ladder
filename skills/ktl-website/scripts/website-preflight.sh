#!/usr/bin/env bash
# What this host can and cannot do for the ktl-website skill: one read-only
# screen before the site is installed, built or deployed. The skill runs it
# first and repeats its summary line in the hand-off, so a missing tool
# disables a step out loud instead of failing a build.
#
# Each line is `ok`, `warn`, `missing` or `info`, then one summary line:
#   Preflight: <n> missing, <m> warnings. Missing disables: <steps>.
# Exit 0 always: the skill reads the lines, and nothing here is a gate.
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
# never works a label out a second way. Without the script there is no page.
if [ -f "$root/.lokf/scripts/knowledge-report.sh" ]; then
  health="$(cd "$root" && bash .lokf/scripts/knowledge-report.sh --root "$root" health 2>/dev/null | tail -n 1)"
  if [ -n "$health" ]; then ok report "knowledge-report.sh: $health"; else warn report "knowledge-report.sh printed no health line - run it by hand: bash .lokf/scripts/knowledge-report.sh health"; fi
else
  miss report "no .lokf/scripts/knowledge-report.sh - the concept pages take their trust labels from it; run the ktl-sidecar repair (sidecar 0.30.0 or later)" "Step 4's build and Step 5's workflow"
fi

# ---- the toolkit -------------------------------------------------------------
# The build runs `lokf export`, and LinkML's gen-doc for a schema, with `uv
# run --frozen` from the sidecar's own environment, so it needs the lock
# file, and the workflow needs it committed. Hugo and Pagefind come through
# uv too, from the site's own lock.
ingit=0
if have git && git -C "$root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then ingit=1; fi
if have uv; then
  if [ ! -f "$root/.lokf/pyproject.toml" ]; then
    miss toolkit "no .lokf/pyproject.toml - run ktl-sidecar first" "Step 4's build"
  elif [ ! -f "$root/.lokf/uv.lock" ]; then
    miss toolkit "no .lokf/uv.lock - the build runs lokf export with uv run --frozen; run uv lock in .lokf/ and commit the file" "Step 4's build and Step 5's workflow"
  elif [ "$ingit" = 1 ] && [ -z "$(git -C "$root" ls-files .lokf/uv.lock 2>/dev/null | head -n 1)" ]; then
    warn toolkit "uv $(uv --version 2>/dev/null | awk '{print $2}'); .lokf/uv.lock is not in git - the workflow runs the toolkit with uv run --frozen and fails without it; commit the file"
  else
    ok toolkit "uv $(uv --version 2>/dev/null | awk '{print $2}'); .lokf/uv.lock present"
  fi
else
  miss toolkit "uv not found (docs.astral.sh/uv) - the build runs Hugo, Pagefind and lokf export through it" "Step 4's build"
fi

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
      ok git "github.com, $slug, default branch ${branch:-unknown}: the site's address and its repository follow from it" ;;
    "") info git "no origin remote - the site builds; the workflow and the links to files need one" ;;
    # The address may carry a token, as https://user:token@host/ does, and
    # this line goes to the agent and to any job log.
    *) info git "origin is not github.com ($(printf '%s' "$remote" | sed -E 's#(://)[^/@]*@#\1#')) - the site builds; Step 5's workflow is GitHub Actions, and links to files name github.com" ;;
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
  # A 404 means Pages is not on yet, and gh prints the error body. Only a success counts.
  pages_api="$(gh api "repos/$slug/pages" --jq '"Pages is on: built from \(.build_type)" + (if .source.branch then ", branch " + .source.branch else "" end) + (if .cname then ", custom domain " + .cname else "" end)' 2>/dev/null)" || pages_api=""
fi
if [ -n "$publishers" ]; then
  warn pages "another publisher: $publishers - the site builds, but leave KNOWLEDGE_WEBSITE_ENABLED unset here until that publisher is retired (references/deploy.md)"
elif [ -n "$pages_api" ]; then
  info pages "$pages_api"
else
  ok pages "no other Pages publisher found${slug:+; gh api repos/$slug/pages says whether Pages is on}"
fi
# The knowledge site replaces an mkdocs site: Step 0 reads mkdocs.yml once,
# and Step 5b gives the maintainer the retirement list.
if [ -f "$root/mkdocs.yml" ]; then
  info mkdocs "mkdocs.yml at the root - the site replaces it: Step 0 reads its nav and exclude_docs into site.toml's redirects and docsExclude, and Step 5b retires it (references/deploy.md)"
fi

# ---- the site's folder: not yet, this skill's, or someone else's ---------------
# The site lives in website/. Where that folder is another site's, it lives
# in ktl-website/ instead, and a rerun finds it there. A folder is this
# skill's when it holds site.toml. The three files the host owns are never
# compared: site.toml, README.md and assets/css/custom.css. Every other file
# is a copy of a template, and a difference is a deliberate edit or a bump
# not yet copied.
site=""
for d in website ktl-website; do
  if [ -f "$root/$d/site.toml" ] && [ -f "$root/$d/hugo.toml" ]; then site="$d"; break; fi
done
if [ -n "$site" ]; then
  drift=""; tdir="$skill_dir/templates/website"
  if [ ! -d "$tdir" ]; then
    warn website "$site/ installed, but this skill's templates/website folder is missing beside its SKILL.md, so the copies cannot be compared - reinstall the skill"
  else
    while IFS= read -r f; do
      rel="${f#"$tdir"/}"
      case "$rel" in site.toml|README.md|assets/css/custom.css) continue ;; esac
      dst="$root/$site/$rel"; [ "$rel" = gitignore ] && dst="$root/$site/.gitignore"
      if [ ! -f "$dst" ]; then drift="${drift}${drift:+, }$rel (missing)"
      elif ! cmp -s "$f" "$dst"; then drift="${drift}${drift:+, }$rel"; fi
    done < <(find "$tdir" -type f | sort)
    if [ -z "$drift" ]; then
      ok website "$site/ installed, and its files match this skill's templates"
    else
      warn website "$site/ installed; differs from the templates: $drift - a deliberate edit, or a template bump not yet copied (repair mode)"
    fi
  fi
  if grep -qE '<(REPO|PROJ)_[A-Z]+>' "$root/$site/site.toml"; then
    warn website "$site/site.toml still holds a <PLACEHOLDER> - Step 1 fills it, and the build refuses it until then"
  fi
  if [ -f "$root/$site/site.config.mjs" ]; then
    warn website "$site/ still holds files of the earlier Astro site (site.config.mjs, package.json, src/) - Step 1's move removes them"
  fi
elif [ -f "$root/website/site.config.mjs" ]; then
  site="website"
  warn website "website/ is this skill's earlier Astro site (site.config.mjs) - Step 1 moves it to Hugo in place: its values go into site.toml and its other files are removed"
elif [ -d "$root/ktl-website" ]; then
  miss website "ktl-website/ exists and is not this skill's (no site.toml), and so is website/ or it would be used - this skill writes nothing into either; ask where the site should go" "Step 1 and every step after it"
elif [ -e "$root/website" ]; then
  site="ktl-website"
  info website "website/ exists and is not this skill's (no site.toml), so it is left alone - Step 1 installs the site in ktl-website/ instead"
else
  site="website"
  ok website "no website/ yet - Step 1 installs the site there"
fi
if [ -n "$own_found" ]; then
  info workflow "$own_found present; the deploy runs once KNOWLEDGE_WEBSITE_ENABLED is true"
elif [ -n "$site" ] && [ -f "$root/$site/site.toml" ]; then
  info workflow "no .github/workflows/knowledge-website.yaml - Step 5 lays it down"
fi

# ---- what the site can show beside the bundle ---------------------------------
if [ -f "$root/README.md" ]; then
  title="$(awk '/^[[:space:]]*(```|~~~)/ { fence = !fence; next } !fence && /^# / { sub(/^# /, ""); print; exit }' "$root/README.md")"
  if [ -n "$title" ]; then
    ok readme "README.md, titled \"$title\": the home page"
  else
    warn readme "README.md has no '# ' title - the home page shows it under no heading; give it one"
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
  arch="no architecture.md, so the home page's Architecture button is greyed"
  [ -f "$root/docs/architecture.md" ] && arch="architecture.md, the home page's Architecture button"
  simple="$(find "$root/docs/" -name '*.*-simple.md' | wc -l | tr -d ' ')"
  ok docs "docs/, $n Markdown page(s) as git sees them: the Guide part; $arch; $simple retelling(s) named <page>.<language>-simple.md"
else
  info docs "no docs/ - the Guide part lists the home page alone, and the home page's Architecture button is greyed"
fi
if [ -f "$root/CHANGELOG.md" ]; then
  n="$(grep -cE '^## \[[^]]+\] - [0-9]{4}-[0-9]{2}-[0-9]{2}' "$root/CHANGELOG.md" || true)"
  if [ "${n:-0}" -gt 0 ]; then
    ok changelog "CHANGELOG.md, $n released version(s): a page per release"
  else
    warn changelog "CHANGELOG.md has no '## [version] - date' heading, so no release page can be made from it (Keep a Changelog form)"
  fi
else
  info changelog "no CHANGELOG.md - no release pages"
fi
if [ -d "$root/.assets" ]; then
  n="$(find "$root/.assets/" -type f | wc -l | tr -d ' ')"
  logos="$(find "$root/.assets/" -maxdepth 1 -type f -iname '*logo*' | sed "s#^$root/##" | sort | tr '\n' ' ')"
  ok assets ".assets/, $n file(s)${logos:+; logo candidates: ${logos% }}"
else
  info assets "no .assets/ folder - the site serves no figures, and shows the Knowledge Trust Ladder logo"
fi

# The schema, as the site's scripts/prepare.sh finds it: a LinkML project's
# src/<name>/schema/<name>.yaml, at the root first, then in the .linkml/
# sidecar. gen-doc from the sidecar's own environment writes its pages.
schema=""
for f in "$root"/src/*/schema/*.yaml "$root"/.linkml/src/*/schema/*.yaml; do
  [ -f "$f" ] || continue
  name="$(basename "$f" .yaml)"
  [ "$(basename "${f%/schema/*}")" = "$name" ] || continue
  schema="${f#"$root"/}"; break
done
if [ -n "$schema" ]; then
  ok schema "$schema: the Schema part, a page per class, slot, enumeration and type, and the home page leads with it"
else
  info schema "no src/<name>/schema/<name>.yaml at the root or under .linkml/ - no Schema part, and the home page's schema button is greyed"
fi
if [ -f "$root/.github/workflows/knowledge-federation.yaml" ]; then
  ok workspace ".github/workflows/knowledge-federation.yaml: a domain host, so the graph page offers the workspace"
else
  info workspace "no .github/workflows/knowledge-federation.yaml - the graph page greys the workspace"
fi

lint=""
for f in "$root"/.markdownlint* "$root/lychee.toml" "$root/.codespellrc"; do
  [ -e "$f" ] && lint="${lint}${lint:+ }${f#"$root"/}"
done
if [ -n "$lint" ]; then
  info lint "lint configs to exclude ${site:-website}/'s generated folders from (Step 2): $lint"
else
  info lint "no Markdown lint config at the root, so Step 2 has nothing to exclude"
fi

# ---- session ---------------------------------------------------------------
unattended=""
for v in CI GITHUB_ACTIONS GITLAB_CI TF_BUILD; do
  val="${!v:-}"; [ -n "$val" ] && unattended="${unattended}${unattended:+, }$v"
done
if [ -n "$unattended" ]; then
  info session "unattended ($unattended set): the placeholders need a person's values, so stop after this screen"
else
  info session "attended: a person can answer item by item"
fi

printf 'Preflight: %d missing, %d warning(s).%s\n' "$missing" "$warns" "${disables:+ Missing disables: $disables.}"
exit 0
