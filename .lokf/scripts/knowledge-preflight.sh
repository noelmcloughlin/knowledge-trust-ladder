#!/usr/bin/env bash
# What this host can and cannot do for the four LOKF skills: one read-only
# screen, no toolkit needed. Every skill runs it first and repeats its summary
# line in the hand-off, so a missing tool disables a step out loud instead of
# being discovered after a report has already offered that step.
#
# Each line is `ok`, `warn`, `missing` or `info`, then one summary line:
#   Preflight: <n> missing, <m> warnings. Missing disables: <steps>.
# Exit 0 always: the skills read the lines; nothing here is a gate.
#
# Bash 3.2 and POSIX tools only, so it runs on macOS's stock bash and on Git
# for Windows. From PowerShell, run it through Git for Windows' bash - the
# one-liner is in lokf-sidecar/references/portability.md.
#
# Usage: knowledge-preflight.sh [repo-root]   (default: the nearest ancestor of
# the current directory holding `.lokf/`, else the current directory)
set -u

missing=0; warns=0; disables=""
line() { printf '%-8s%-13s%s\n' "$1" "$2" "$3"; }
ok()   { line ok "$1" "$2"; }
info() { line info "$1" "$2"; }
warn() { line warn "$1" "$2"; warns=$((warns + 1)); }
miss() { line missing "$1" "$2"; missing=$((missing + 1)); [ -n "${3:-}" ] && disables="${disables}${disables:+; }$3"; }
have() { command -v "$1" >/dev/null 2>&1; }

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
if have sha256sum; then digest="sha256sum"; elif have shasum; then digest="shasum -a 256"; else digest=""; fi
if have python3; then py=python3; elif have python; then py=python; else py=""; fi
printf 'Preflight for %s\n' "$root"
ok host "$host, bash ${BASH_VERSION%%(*}; digest: ${digest:-none (macOS: install coreutils, or use uv run python)}; python: ${py:-none (use uv run python)}"

# ---- bundle ----------------------------------------------------------------
bundle="$root/.lokf/knowledge"
if [ -d "$bundle" ]; then
  n="$(find "$bundle" -name '*.md' -not -path '*/.obsidian/*' -not -name index.md -not -name log.md -not -name diataxis.md | wc -l | tr -d ' ')"
  door="$root/knowledge_bundle"
  if [ -L "$door" ]; then doorway="knowledge_bundle -> $(readlink "$door")"
  elif [ -d "$door" ]; then doorway="knowledge_bundle is a folder or junction"
  else doorway="no knowledge_bundle doorway (ln -s .lokf/knowledge knowledge_bundle, or mklink /J on Windows)"; fi
  ok bundle ".lokf/knowledge, $n concepts; $doorway"
else
  miss bundle "no .lokf/knowledge under $root - run lokf-sidecar first" "every skill but lokf-sidecar"
fi
case "$root" in
  *OneDrive*|*Dropbox*|*iCloud*|*"Google Drive"*|*GoogleDrive*|*Nextcloud*)
    info sync "synced folder: links are per machine, and a conflict copy shows up as a duplicate id (conventions rule 7)" ;;
esac

# ---- git -------------------------------------------------------------------
ingit=0; tracked=""; forge=none
if have git && git -C "$root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  ingit=1
  if [ -n "$(git -C "$root" ls-files .lokf/knowledge 2>/dev/null | head -n 1)" ]; then tracked="tracked"
  elif git -C "$root" check-ignore -q .lokf 2>/dev/null; then tracked="gitignored (no gate, no pull requests, no scheduled librarian)"
  else tracked="not yet committed"; fi
  shallow="$(git -C "$root" rev-parse --is-shallow-repository 2>/dev/null || echo false)"
  crlf="$(git -C "$root" config --get core.autocrlf 2>/dev/null || echo unset)"
  attrs="absent"; [ -f "$root/.lokf/.gitattributes" ] && attrs="present"
  ok git "bundle $tracked; history $([ "$shallow" = true ] && echo shallow || echo full); core.autocrlf=$crlf; .lokf/.gitattributes $attrs"
  [ "$shallow" = true ] && warn git "shallow clone: the conventions script cannot resolve a revision - fetch the full history"
  [ "$attrs" = absent ] && [ -d "$bundle" ] && warn git "no .lokf/.gitattributes: a Windows checkout may differ from CI - lokf-sidecar Step 1 lays it down"
  remote="$(git -C "$root" remote get-url origin 2>/dev/null || true)"
  case "$remote" in
    *github.com*) forge=github ;;
    *gitlab*) forge=gitlab ;;
    *codeberg*|*forgejo*|*gitea*) forge=forgejo ;;
    *bitbucket*) forge=bitbucket ;;
    "") forge=none ;;
    *) forge=other ;;
  esac
  gate="$root/.github/workflows/knowledge-registrar.yaml"
  case "$forge" in
    github) if [ -f "$gate" ]; then ok forge "github; gate workflow present"; else warn forge "github; no knowledge-registrar.yaml - lokf-sidecar Step 5 lays it down"; fi ;;
    none) info forge "no origin remote - no gate applies; the host's own review is the record" ;;
    *) info forge "$forge - no gate template for it; the porting recipe is in lokf-sidecar/references/portability.md" ;;
  esac
else
  info git "no git: gate, pull requests and signed-commit checks do not apply; the host's own version history is the record"
fi
if [ -d "$bundle" ]; then
  crlf_files="$(grep -rl "$(printf '\r')" "$bundle" --include='*.md' 2>/dev/null | wc -l | tr -d ' ')"
  [ "${crlf_files:-0}" -gt 0 ] && warn endings "$crlf_files file(s) use CRLF - the conventions script reads them; other tools may not"
  bom_files=0
  while IFS= read -r f; do
    [ "$(head -c 3 "$f" | od -An -tx1 | tr -d ' \n')" = "efbbbf" ] && bom_files=$((bom_files + 1))
  done < <(find "$bundle" -name '*.md' -not -path '*/.obsidian/*')
  [ "$bom_files" -gt 0 ] && warn endings "$bom_files file(s) start with a byte order mark - conventions rule 9 reports them"
fi

# ---- identity and signing --------------------------------------------------
id=""
if have gh; then
  if gh auth status >/dev/null 2>&1; then
    id="$(gh api user --jq .login 2>/dev/null || true)"
    [ -n "$id" ] && ok identity "gh logged in: confirmations record as human:$id"
    [ -z "$id" ] && warn identity "gh logged in but the login could not be read (offline?)"
  else
    warn identity "gh installed but not logged in - gh auth login"
  fi
elif have glab; then
  if glab auth status >/dev/null 2>&1; then
    id="$(glab api user 2>/dev/null | sed -n 's/.*"username":"\([^"]*\)".*/\1/p' | head -n 1)"
    [ -n "$id" ] && ok identity "glab logged in: confirmations record as human:$id"
  else
    warn identity "glab installed but not logged in - glab auth login"
  fi
fi
if [ -z "$id" ]; then
  case "$forge" in
    github) miss identity "no authenticated login (gh) - the signing-key route in lokf-curator/references/portability.md is the alternative" "Confirm, Correct now (lokf-curator), named feedback (lokf-docent)" ;;
    gitlab|forgejo|bitbucket|other) miss identity "no authenticated login (glab, or the signing-key route in lokf-curator/references/portability.md)" "Confirm, Correct now (lokf-curator)" ;;
    none) info identity "no forge: on a synced folder the id is the account the platform's version history shows (lokf-curator/references/portability.md)" ;;
  esac
fi
if [ "$ingit" -eq 1 ]; then
  sign="$(git -C "$root" config --get commit.gpgsign 2>/dev/null || echo false)"
  key="$(git -C "$root" config --get user.signingkey 2>/dev/null || true)"
  fmt="$(git -C "$root" config --get gpg.format 2>/dev/null || echo openpgp)"
  headsig="unsigned"; git -C "$root" cat-file commit HEAD 2>/dev/null | grep -qE '^gpgsig' && headsig="signed"
  if [ "$sign" = true ] && [ -n "$key" ]; then
    ok signing "commit.gpgsign on ($fmt key ${key##*/}); HEAD $headsig"
  else
    warn signing "commit signing off - a curation pull request you open yourself fails the gate (docs/signing-commits.md in lokf-agent-skills)"
  fi
fi

# ---- toolkit ---------------------------------------------------------------
if have uv; then
  floor="$(sed -n 's/.*"lokf\[build\]>=\([0-9.]*\)".*/\1/p' "$root/.lokf/pyproject.toml" 2>/dev/null | head -n 1)"
  if [ -d "$root/.lokf/.venv" ]; then
    installed="$(cd "$root/.lokf" && uv run --no-sync lokf --version 2>/dev/null | sed -n 's/^lokf //p')"
    ok toolkit "uv $(uv --version 2>/dev/null | sed 's/^uv //'); lokf ${installed:-unknown} installed (floor >=${floor:-?})"
  elif [ -f "$root/.lokf/pyproject.toml" ]; then
    warn toolkit "uv present, toolkit not installed - run just lokf-install (or uv sync) in .lokf/ (floor >=${floor:-?})"
  else
    info toolkit "uv $(uv --version 2>/dev/null | sed 's/^uv //') present; no .lokf/pyproject.toml yet"
  fi
  if have just; then ok just "just $(just --version 2>/dev/null | sed 's/^just //')"; else info just "just not installed - uvx --from rust-just just works the same"; fi
else
  miss toolkit "uv not installed - lokf validate, convert and query unavailable; only the manual schema cross-check remains" "lokf validate (every skill's audit)"
fi

# ---- installed skills, and drift between copies -----------------------------
found=""; templates=""
for dir in .claude/skills .github/skills .agents/skills skills; do
  here=""
  for s in lokf-sidecar lokf-librarian lokf-curator lokf-docent; do
    [ -f "$root/$dir/$s/SKILL.md" ] && here="$here ${s#lokf-}"
  done
  [ -n "$here" ] && found="${found}${found:+; }$dir:$here"
done
# The templates to compare host copies against: bare skills/ first (a
# repository that publishes the skills is its own canonical copy), then the
# wrapper's install locations in its order.
for dir in skills .claude/skills .github/skills .agents/skills; do
  [ -z "$templates" ] && [ -d "$root/$dir/lokf-sidecar/templates" ] && templates="$root/$dir/lokf-sidecar/templates"
done
if [ -n "$found" ]; then
  ok skills "$found"
  for s in lokf-sidecar lokf-librarian lokf-curator lokf-docent; do
    first=""
    for dir in .claude/skills .github/skills .agents/skills skills; do
      [ -d "$root/$dir/$s" ] || continue
      if [ -z "$first" ]; then first="$root/$dir/$s"
      elif [ "$(cd "$first" && pwd -P)" != "$(cd "$root/$dir/$s" && pwd -P)" ] && ! diff -rq "$first" "$root/$dir/$s" >/dev/null 2>&1; then
        warn skills "two copies of $s differ: ${first#"$root"/} and $dir/$s - one is stale; reinstall or remove it"
      fi
    done
  done
else
  info skills "no LOKF skill installed under .claude/skills, .github/skills, .agents/skills or skills/"
fi

# ---- host copies of the sidecar's templates ----------------------------------
if [ -n "$templates" ] && [ -d "$root/.lokf" ]; then
  drift=""
  for pair in "scripts/knowledge-conventions.sh:.lokf/scripts/knowledge-conventions.sh" \
              "scripts/knowledge-librarian.sh:.lokf/scripts/knowledge-librarian.sh" \
              "scripts/knowledge-preflight.sh:.lokf/scripts/knowledge-preflight.sh" \
              "gitattributes:.lokf/.gitattributes" \
              "github/knowledge-registrar.yaml:.github/workflows/knowledge-registrar.yaml" \
              "github/knowledge-librarian.yaml:.github/workflows/knowledge-librarian.yaml"; do
    src="$templates/${pair%%:*}"; dst="$root/${pair##*:}"
    [ -f "$dst" ] || continue
    [ -f "$src" ] || { drift="${drift}${drift:+, }${pair##*:} (the installed sidecar predates it)"; continue; }
    cmp -s "$src" "$dst" || drift="${drift}${drift:+, }${pair##*:}"
  done
  if [ -z "$drift" ]; then
    ok copies "host copies match the installed sidecar's templates (${templates#"$root"/})"
  else
    warn copies "differ from ${templates#"$root"/}: $drift - a deliberate host edit, or a template bump not yet copied (lokf-sidecar repair)"
  fi
fi

# ---- session ---------------------------------------------------------------
unattended=""
for v in CI GITHUB_ACTIONS GITLAB_CI TF_BUILD; do
  eval "val=\${$v:-}"; [ -n "$val" ] && unattended="${unattended}${unattended:+, }$v"
done
agent=""
[ -n "${CLAUDECODE:-}" ] && agent="Claude Code"
[ -n "${CODESPACES:-}" ] && agent="${agent}${agent:+, }Codespaces"
[ "${TERM_PROGRAM:-}" = vscode ] && agent="${agent}${agent:+, }VS Code terminal"
if [ -n "$unattended" ]; then
  info session "unattended ($unattended set): lokf-curator stops after its report; lokf-librarian edits only under the bundle"
else
  info session "attended${agent:+ ($agent)}: a person can answer item by item"
fi
if have curl; then
  if curl -sI --max-time 4 https://pypi.org/simple/lokf/ >/dev/null 2>&1; then info network "pypi.org reachable"; else warn network "pypi.org unreachable - version checks and skill installs will fail here"; fi
fi

printf 'Preflight: %d missing, %d warning(s).%s\n' "$missing" "$warns" "${disables:+ Missing disables: $disables.}"
exit 0
