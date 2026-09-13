#!/usr/bin/env bash
# Layout tests for the way lokf-sidecar lays a bundle down (SKILL.md Step 2).
#
# The bundle is `.lokf/knowledge`, which the tools address, and `knowledge_bundle`
# beside it is the doorway link people and Obsidian open. A git pathspec never
# traverses a symlink, so a template that scopes a diff to the bundle names both
# paths: with the doorway the second name matches nothing, harmlessly, and it
# still covers a shared folder someone rearranged by hand into a real
# `knowledge_bundle/` with `.lokf/knowledge` linking onto it (see the sidecar's
# references/portability.md). These tests pin that for the template files that
# do so, and for the `just lokf-link` recipe:
#
#   1. the librarian wrapper's boundary check accepts an edit made under either
#      name - with the doorway, without it, and in the rearranged shape - and
#      still refuses one outside the bundle;
#   2. the librarian workflow's change detection sees a bundle edit in each of
#      those shapes, and its packaging step stages it without failing when the
#      second name does not exist;
#   3. the registrar workflow triggers on, and diffs, both names;
#   4. `just lokf-link` creates the doorway, is a no-op when it is present,
#      refuses a name taken by something else, and does nothing when
#      `.lokf/knowledge` is itself a link.
#
# Needs bash and git. `just` is optional: without it, test 4 is skipped and says so.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
templates="$repo_root/skills/lokf-sidecar/templates"
wrapper="$templates/scripts/knowledge-librarian.sh"
librarian_yaml="$templates/github/knowledge-librarian.yaml"
registrar_yaml="$templates/github/knowledge-registrar.yaml"
justfile="$templates/justfile"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

fail=0
ok()  { printf 'OK:   %s\n' "$*"; }
err() { printf 'FAIL: %s\n' "$*" >&2; fail=1; }

# Stands in for AGENT_CLI: ignores the prompt it is handed and appends a line to
# the file named in EDIT_PATH (relative to the repo root the wrapper cd's to).
fake_agent="$work/fake-agent.sh"
cat > "$fake_agent" <<'AGENT'
#!/usr/bin/env bash
printf '\nedited by the fake agent\n' >> "$EDIT_PATH"
AGENT
chmod +x "$fake_agent"

# make_host <dir> <default|no-doorway|rearranged>
# A minimal host repository: the wrapper and justfile in place, one concept in
# the bundle, and the two names wired the way the shape says.
make_host() {
  local dir="$1" shape="$2"
  mkdir -p "$dir"
  (
    cd "$dir"
    git init -q -b main .
    git config user.email "layout-test@example.invalid"
    git config user.name "layout test"
    mkdir -p .lokf/scripts skills/lokf-librarian
    cp "$wrapper" .lokf/scripts/knowledge-librarian.sh
    chmod +x .lokf/scripts/knowledge-librarian.sh
    cp "$justfile" .lokf/justfile
    printf '# stub skill\n' > skills/lokf-librarian/SKILL.md
    case "$shape" in
      default)     mkdir -p .lokf/knowledge; ln -s .lokf/knowledge knowledge_bundle ;;
      no-doorway)  mkdir -p .lokf/knowledge ;;
      rearranged)  mkdir -p knowledge_bundle; ln -s ../knowledge_bundle .lokf/knowledge ;;
      *) echo "unknown shape $shape" >&2; exit 2 ;;
    esac
    printf -- '---\ntype: Service\ntitle: A\n---\n\n# A\n' > .lokf/knowledge/a.md
    printf '# host\n' > README.md
    git add -A .
    git commit -q -m "init ($shape)"
  )
}

# run_wrapper <dir> <path the fake agent edits> - prints the wrapper's exit status
# and resets the working tree for the next case.
run_wrapper() {
  local dir="$1" edit="$2" status=0
  ( cd "$dir" && AGENT_CLI="$fake_agent" EDIT_PATH="$edit" bash .lokf/scripts/knowledge-librarian.sh >/dev/null 2>&1 ) || status=$?
  git -C "$dir" checkout -q -- .
  printf '%s' "$status"
}

echo "1. the librarian wrapper's boundary check"
for shape in default rearranged; do
  host="$work/wrapper-$shape"
  make_host "$host" "$shape"
  for edit in .lokf/knowledge/a.md knowledge_bundle/a.md; do
    status="$(run_wrapper "$host" "$edit")"
    if [ "$status" = 0 ]; then ok "$shape: an edit via $edit is inside the bundle (exit 0)"
    else err "$shape: an edit via $edit was refused (exit $status)"; fi
  done
  status="$(run_wrapper "$host" README.md)"
  if [ "$status" = 3 ]; then ok "$shape: an edit to README.md is refused (exit 3)"
  else err "$shape: an edit outside the bundle was not refused (exit $status)"; fi
done
host="$work/wrapper-no-doorway"
make_host "$host" no-doorway
status="$(run_wrapper "$host" .lokf/knowledge/a.md)"
if [ "$status" = 0 ]; then ok "no-doorway: an edit via .lokf/knowledge/a.md is inside the bundle (exit 0)"
else err "no-doorway: an edit via .lokf/knowledge/a.md was refused (exit $status)"; fi
status="$(run_wrapper "$host" README.md)"
if [ "$status" = 3 ]; then ok "no-doorway: an edit to README.md is refused (exit 3)"
else err "no-doorway: an edit outside the bundle was not refused (exit $status)"; fi

echo "2. the librarian workflow's change detection and packaging"
detect='git status --porcelain -- .lokf/knowledge knowledge_bundle'
if grep -qF "$detect" "$librarian_yaml"; then ok "template detects changes with: $detect"
else err "knowledge-librarian.yaml no longer contains: $detect"; fi
stage_second='[ -e knowledge_bundle ] && git add -A -- knowledge_bundle || true'
if grep -qF 'git add -A -- .lokf/knowledge' "$librarian_yaml" && grep -qF "$stage_second" "$librarian_yaml"; then
  ok "template stages both names and guards the second one"
else err "knowledge-librarian.yaml packaging lines changed"; fi
for shape in default no-doorway rearranged; do
  host="$work/workflow-$shape"
  make_host "$host" "$shape"
  printf '\nchanged\n' >> "$host/.lokf/knowledge/a.md"
  printf '\nchanged\n' >> "$host/README.md"
  seen="$(cd "$host" && git status --porcelain -- .lokf/knowledge knowledge_bundle | cut -c4- | tr '\n' ' ')"
  case "$seen" in
    *a.md*README*|*README*a.md*) err "$shape: change detection leaked a file outside the bundle ($seen)" ;;
    *a.md*) ok "$shape: change detection sees the bundle edit and nothing else ($seen)" ;;
    *) err "$shape: change detection saw nothing" ;;
  esac
  staged="$(cd "$host" && set -e && git add -A -- .lokf/knowledge && { [ -e knowledge_bundle ] && git add -A -- knowledge_bundle || true; } && git diff --cached --name-only | tr '\n' ' ')"
  case "$staged" in
    *README*) err "$shape: packaging staged a file outside the bundle ($staged)" ;;
    *a.md*)   ok "$shape: packaging stages the edited concept ($staged)" ;;
    *)        err "$shape: packaging staged nothing" ;;
  esac
done

echo "3. the registrar workflow"
if grep -qE '^\s*-\s*"\.lokf/\*\*"' "$registrar_yaml" && grep -qE '^\s*-\s*"knowledge_bundle/\*\*"' "$registrar_yaml"; then
  ok "registrar triggers on .lokf/** and knowledge_bundle/**"
else err "knowledge-registrar.yaml paths: must list both .lokf/** and knowledge_bundle/**"; fi
pathspecs="$(grep -c -- '-- .lokf/knowledge knowledge_bundle' "$registrar_yaml" || true)"
single="$(grep -cE -- '-- \.lokf/knowledge *$|-- \.lokf/knowledge \|' "$registrar_yaml" || true)"
if [ "$pathspecs" -ge 3 ] && [ "$single" -eq 0 ]; then ok "provenance job names both paths in all $pathspecs of its git pathspecs"
else err "knowledge-registrar.yaml: $pathspecs pathspecs name both paths, $single name only .lokf/knowledge"; fi

echo "4. just lokf-link"
if command -v just >/dev/null 2>&1; then
  host="$work/link-create"
  make_host "$host" no-doorway
  if ( cd "$host/.lokf" && just --quiet lokf-link >/dev/null && [ "$(readlink ../knowledge_bundle)" = ".lokf/knowledge" ] ); then
    ok "creates knowledge_bundle -> .lokf/knowledge at the host root"
  else err "did not create the doorway"; fi
  if ( cd "$host/.lokf" && just --quiet lokf-link | grep -q "already present" ); then ok "is a no-op when the doorway is present"
  else err "a second run was not a no-op"; fi
  host="$work/link-taken-folder"
  make_host "$host" no-doorway
  mkdir "$host/knowledge_bundle"
  if ( cd "$host/.lokf" && ! just --quiet lokf-link >/dev/null 2>&1 && [ -d "$host/knowledge_bundle" ] && [ ! -L "$host/knowledge_bundle" ] ); then
    ok "refuses a name taken by a real folder, and leaves it alone"
  else err "a real knowledge_bundle folder was not left alone"; fi
  host="$work/link-taken-link"
  make_host "$host" no-doorway
  ln -s ../nowhere "$host/knowledge_bundle"
  if ( cd "$host/.lokf" && ! just --quiet lokf-link >/dev/null 2>&1 && [ "$(readlink "$host/knowledge_bundle")" = "../nowhere" ] ); then
    ok "refuses a link that points elsewhere, and leaves it alone"
  else err "a foreign knowledge_bundle link was not left alone"; fi
  host="$work/link-rearranged"
  make_host "$host" rearranged
  if ( cd "$host/.lokf" && just --quiet lokf-link | grep -q "nothing to do" ); then ok "does nothing when .lokf/knowledge is itself a link"
  else err "a rearranged host was not left alone"; fi
else
  echo "SKIP: just is not installed - the lokf-link recipe tests need it"
fi

echo ""
if [ "$fail" -eq 0 ]; then echo "Layout tests: PASS"; exit 0; else echo "Layout tests: FAIL"; exit 1; fi
