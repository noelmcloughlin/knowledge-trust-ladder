#!/usr/bin/env bash
# Build the ktl-docent-m365 skill directory: a snapshot of one LOKF knowledge
# bundle, with the docent's Copilot instructions beside it, ready for
# Microsoft 365 Agents Toolkit to add to a declarative agent.
#
# Copilot runs a skill in a sandbox with no repository, no shell and no
# network, so the bundle has to travel inside the skill. This script copies
# it there, writes SNAPSHOT.md to say which repository and revision it came
# from, and refuses a result that breaks Copilot's documented limits for
# custom skills (preview): instructions under 20,000 characters, a directory
# depth of 3, allowed file types only, 350 files, and a 10 MB app package.
# It never touches the source bundle.
#
# Usage: integrations/m365/build.sh [--repo-url URL] [--ref REF] <bundle> <out-dir>
#   <bundle>   a bundle directory (.lokf/knowledge), or a release's
#              knowledge-<tag>-<repository>.zip
#   <out-dir>  where to create ktl-docent-m365/; it must not exist there yet
#   --repo-url the repository's https URL; read from the git remote when
#              <bundle> sits in a git work tree
#   --ref      the tag or commit the bundle was taken at; read from the zip's
#              name, or from git
#
#   integrations/m365/build.sh .lokf/knowledge /tmp/m365
#   integrations/m365/build.sh --repo-url https://github.com/o/r knowledge-v1.2.0-r.zip ./dist
#
# Exit 0 when built, 1 when the result breaks a limit (nothing is left
# behind), 2 when the arguments are wrong.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_name="ktl-docent-m365"

usage() {
  echo "usage: integrations/m365/build.sh [--repo-url URL] [--ref REF] <bundle-dir|bundle.zip> <out-dir>" >&2
  exit 2
}

repo_url=""; ref=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-url) [[ $# -ge 2 ]] || usage; repo_url="$2"; shift 2 ;;
    --ref) [[ $# -ge 2 ]] || usage; ref="$2"; shift 2 ;;
    -h|--help) usage ;;
    --) shift; break ;;
    -*) echo "build: unknown option $1" >&2; usage ;;
    *) break ;;
  esac
done
[[ $# -eq 2 ]] || usage
bundle="$1"; out_parent="$2"

if [[ -n "$repo_url" && ! "$repo_url" =~ ^https://[A-Za-z0-9.-]+/[A-Za-z0-9._/-]+$ ]]; then
  echo "build: --repo-url must be a plain https URL, got '$repo_url'" >&2
  exit 2
fi
if [[ -n "$ref" && ! "$ref" =~ ^[A-Za-z0-9._/-]+$ ]]; then
  echo "build: --ref must be a tag or commit, got '$ref'" >&2
  exit 2
fi
out="$out_parent/$skill_name"
if [[ -e "$out" ]]; then
  echo "build: $out already exists - remove it or pick another <out-dir>; this script never overwrites a skill" >&2
  exit 2
fi

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
stage="$work/$skill_name"
mkdir -p "$stage"

# Take the bundle. A link inside it is refused rather than followed, so
# nothing outside the bundle can reach the package: the release step stores
# links as links for the same reason.
if [[ -f "$bundle" && "$bundle" == *.zip ]]; then
  command -v unzip >/dev/null 2>&1 || { echo "build: unzip is needed to read $bundle" >&2; exit 2; }
  unzip -q "$bundle" -d "$work/zip"
  if [[ ! -f "$work/zip/knowledge/index.md" ]]; then
    echo "build: $bundle has no knowledge/index.md - not a knowledge-release zip" >&2
    exit 2
  fi
  cp -R -P "$work/zip/knowledge" "$stage/knowledge"
  if [[ -z "$ref" ]]; then
    # knowledge-<tag>-<repository>.zip, where the tag is vMAJOR.MINOR.PATCH.
    ref="$(basename "$bundle" | sed -nE 's/^knowledge-(v[0-9]+\.[0-9]+\.[0-9]+)-.*\.zip$/\1/p')"
  fi
elif [[ -d "$bundle" ]]; then
  if [[ ! -f "$bundle/index.md" ]]; then
    echo "build: $bundle has no index.md - point at the bundle itself (.lokf/knowledge)" >&2
    exit 2
  fi
  src="$(cd "$bundle" && pwd -P)"
  cp -R -P "$src" "$stage/knowledge"
  if git -C "$src" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    if [[ -z "$ref" ]]; then
      ref="$(git -C "$src" describe --tags --exact-match 2>/dev/null || git -C "$src" rev-parse --short=12 HEAD)"
      if [[ -n "$(git -C "$src" status --porcelain -- .)" ]]; then
        echo "build: warning - $bundle has uncommitted changes, so the snapshot is not exactly $ref" >&2
      fi
    fi
    if [[ -z "$repo_url" ]]; then
      remote="$(git -C "$src" remote get-url origin 2>/dev/null || true)"
      # git@host:owner/repo(.git) and https://host/owner/repo(.git) both become https://host/owner/repo.
      repo_url="$(printf '%s' "$remote" | sed -E 's#^git@([^:]+):#https://\1/#; s#^ssh://git@([^/]+)/#https://\1/#; s#\.git$##')"
      [[ "$repo_url" =~ ^https:// ]] || repo_url=""
    fi
  fi
else
  echo "build: $bundle is neither a bundle directory nor a .zip" >&2
  exit 2
fi

cp "$here/skill-template.md" "$stage/SKILL.md"

# SNAPSHOT.md is what the skill reads first: where the concepts came from, and
# how to turn a concept's resource path into a link pinned to that revision.
built="$(date -u +%Y-%m-%d)"
source_pattern=""; report_to=""
case "$repo_url" in
  https://github.com/*|https://gitlab.com/*)
    blob="blob"; [[ "$repo_url" == https://gitlab.com/* ]] && blob="-/blob"
    if [[ -n "$ref" ]]; then source_pattern="$repo_url/$blob/$ref/<path>"; fi
    report_to="$repo_url/issues/new, titled \"Knowledge bundle feedback\", or a pull request that adds the line to \`.lokf/feedback.md\`"
    ;;
  "") report_to="the maintainers of the repository, as a line for \`.lokf/feedback.md\`" ;;
  *) report_to="the maintainers of $repo_url, as a line for \`.lokf/feedback.md\`" ;;
esac
[[ -n "$source_pattern" ]] || source_pattern="none - give the path and the revision"
{
  echo "# Snapshot"
  echo ""
  echo "- Repository: ${repo_url:-not recorded}"
  echo "- Revision: ${ref:-not recorded}"
  echo "- Built: $built (UTC)"
  echo "- Source link pattern: $source_pattern"
  echo "- Report gaps to: $report_to"
  echo ""
  echo "The concepts under \`knowledge/\` are copied unchanged from that revision. The repository may have moved on since the build date."
} > "$stage/SNAPSHOT.md"

# Copilot's limits for a custom skill added through Agents Toolkit.
fail=0
limit() { echo "build: $*" >&2; fail=1; }

body_chars="$(awk 'BEGIN{n=0} /^---$/ && n<2 {n++; next} n>=2' "$stage/SKILL.md" | wc -m | tr -d ' ')"
[[ "$body_chars" -lt 20000 ]] || limit "SKILL.md instructions are $body_chars characters; Copilot allows under 20,000"

links="$(find "$stage" -type l | sed "s#^$stage/##")"
[[ -z "$links" ]] || limit "the bundle holds links, which this build refuses to follow: $links"

deep="$(cd "$stage" && find . -type f | awk -F/ 'NF-2 > 3 {print substr($0, 3)}')"
[[ -z "$deep" ]] || limit "these files sit more than 3 directories deep: $deep"

allowed='json|xml|yaml|yml|ini|config|utf8|docx|doc|docm|pdf|txt|rtf|md|ppt|pptx|ppsm|xlsx|xls|xlsm|csv|tsv|html|htm|png|jpg|jpeg|gif|bmp|log'
bad_type="$(cd "$stage" && find . -type f | { grep -viE "\.($allowed)$" || true; } | sed 's#^\./##')"
[[ -z "$bad_type" ]] || limit "Copilot does not accept these file types: $bad_type"

files="$(find "$stage" -type f | wc -l | tr -d ' ')"
[[ "$files" -le 350 ]] || limit "$files files; Copilot allows 350 across all of an agent's skills"

kb="$(du -sk "$stage" | cut -f1)"
[[ "$kb" -lt 10240 ]] || limit "${kb} KB; the whole app package, this skill included, must stay under 10 MB"

if [[ "$fail" -ne 0 ]]; then
  echo "build: nothing written to $out" >&2
  exit 1
fi

mkdir -p "$out_parent"
mv "$stage" "$out"
echo "built $out: $files files, ${kb} KB, SKILL.md $body_chars characters"
echo "snapshot: ${repo_url:-repository not recorded} at ${ref:-revision not recorded}, built $built"
echo "counts against the agent's limit: $files of 350 files, across all its skills"
