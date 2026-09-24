#!/usr/bin/env bash
# Layout tests for the way ktl-sidecar lays a bundle down (SKILL.md Step 2).
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
#      still refuses one outside the bundle; and (1b) the wrapper puts
#      .git/config and .git/hooks/ back when the agent fails or the job is
#      cancelled, not only when it returns cleanly; and (1c) the wrapper hands
#      AGENT_API_KEY to the agent under AGENT_API_KEY_ENV's name only, and
#      refuses a name that is not a credential's;
#   2. the librarian workflow's change detection sees a bundle edit in each of
#      those shapes, and its packaging step stages it without failing when the
#      second name does not exist;
#   3. the registrar workflow triggers on, and diffs, both names;
#   4. `just lokf-link` creates the doorway, is a no-op when it is present,
#      refuses a name taken by something else, and does nothing when
#      `.lokf/knowledge` is itself a link;
#   5. the release workflow compares an unchanged bundle as unchanged and an
#      edited one as changed in each shape; its pack step puts the bundle, and
#      nothing beside it, under `knowledge/`, keeps a link's target as written,
#      and gives the same bytes for the same bundle, at the same tag or a later one.
#
# Needs bash and git. `just` is optional: without it, test 4 is skipped and says so.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
templates="$repo_root/skills/ktl-sidecar/templates"
wrapper="$templates/scripts/knowledge-librarian.sh"
librarian_yaml="$templates/github/knowledge-librarian.yaml"
registrar_yaml="$templates/github/knowledge-registrar.yaml"
release_yaml="$templates/github/knowledge-release.yaml"
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
    mkdir -p .lokf/scripts skills/ktl-librarian
    cp "$wrapper" .lokf/scripts/knowledge-librarian.sh
    chmod +x .lokf/scripts/knowledge-librarian.sh
    cp "$justfile" .lokf/justfile
    printf '# stub skill\n' > skills/ktl-librarian/SKILL.md
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

# 1b. The wrapper restores .git/config and .git/hooks/ on every way out, not
# only after a clean return: an agent that poisons both and then exits non-zero
# (set -e ends the wrapper there) or gets the job cancelled (SIGTERM, which
# bash delivers once the agent has exited) must leave neither behind, and the
# wrapper's own exit status must be the agent's, or the signal's.
poison_agent="$work/poison-agent.sh"
cat > "$poison_agent" <<'AGENT'
#!/usr/bin/env bash
git config core.hooksPath /nonexistent/hooks
printf '#!/bin/sh\necho hooked\n' > .git/hooks/pre-commit
case "${POISON_THEN:-fail}" in
  fail) exit 7 ;;
  term) kill -TERM "$PPID"; exit 0 ;;
esac
AGENT
chmod +x "$poison_agent"
for way in fail term; do
  host="$work/wrapper-poison-$way"
  make_host "$host" default
  status=0
  ( cd "$host" && AGENT_CLI="$poison_agent" POISON_THEN="$way" bash .lokf/scripts/knowledge-librarian.sh >/dev/null 2>&1 ) || status=$?
  case "$way" in fail) want=7 ;; term) want=143 ;; esac
  if [ "$status" = "$want" ]; then ok "poison/$way: the wrapper exits with the agent's status ($want)"
  else err "poison/$way: the wrapper exited $status, expected $want"; fi
  if git -C "$host" config core.hooksPath >/dev/null 2>&1; then err "poison/$way: core.hooksPath survived the agent's exit"
  else ok "poison/$way: .git/config was restored"; fi
  if [ -e "$host/.git/hooks/pre-commit" ]; then err "poison/$way: the dropped hook survived the agent's exit"
  else ok "poison/$way: .git/hooks/ was restored"; fi
done

# 1c. The key reaches the agent under the name AGENT_API_KEY_ENV gives, and
# under no other: not as AGENT_API_KEY, and not at all when the name is one
# the wrapper refuses (it exits 2 before the agent runs).
env_agent="$work/env-agent.sh"
cat > "$env_agent" <<'AGENT'
#!/usr/bin/env bash
env | grep -E '^(ANTHROPIC_API_KEY|AGENT_API_KEY|AGENT_API_KEY_ENV|PATH)=' | sed 's/^PATH=.*/PATH=set/' | sort > "$ENV_OUT"
AGENT
chmod +x "$env_agent"
host="$work/wrapper-key"
make_host "$host" default
# key_case <label> <key> <name> <expected exit> <expected env lines, space-separated>
key_case() {
  local label="$1" key="$2" name="$3" want="$4" expect="$5" status=0 got
  rm -f "$work/env.out"
  ( cd "$host" && AGENT_CLI="$env_agent" ENV_OUT="$work/env.out" AGENT_API_KEY="$key" AGENT_API_KEY_ENV="$name" \
      bash .lokf/scripts/knowledge-librarian.sh >/dev/null 2>&1 ) || status=$?
  got="$( [ -f "$work/env.out" ] && tr '\n' ' ' < "$work/env.out" | sed 's/ $//' || echo "agent did not run")"
  if [ "$status" = "$want" ] && [ "$got" = "$expect" ]; then ok "key/$label: exit $status, agent saw: $got"
  else err "key/$label: exit $status (want $want), agent saw: $got (want: $expect)"; fi
}
key_case named   sk-test ANTHROPIC_API_KEY 0 "ANTHROPIC_API_KEY=sk-test PATH=set"
key_case none    ""      ""                0 "PATH=set"
key_case no-name sk-test ""                2 "agent did not run"
key_case no-key  ""      ANTHROPIC_API_KEY 2 "agent did not run"
key_case path    sk-test PATH              2 "agent did not run"
key_case github  sk-test GITHUB_TOKEN      2 "agent did not run"
key_case lower   sk-test anthropic_api_key 2 "agent did not run"

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

# The publish job's path check: a concept named with a byte above 0x7f is
# inside the bundle, and a file beside it is not.
listing='git -c core.quotePath=false apply --numstat'
if grep -qF "$listing" "$librarian_yaml"; then ok "template lists the patch's paths with: $listing"
else err "knowledge-librarian.yaml no longer contains: $listing"; fi
host="$work/publish-paths"
make_host "$host" default
allowed='^(\.lokf/knowledge/|knowledge_bundle/|\.lokf/feedback\.md$)'
for case in "inside:.lokf/knowledge/café.md" "outside:notes-café.md"; do
  printf 'x\n' > "$host/${case#*:}"
  (cd "$host" && git add -A && git diff --cached --binary > "$work/p.patch" && git reset -q --hard)
  bad="$(cd "$host" && { git -c core.quotePath=false apply --numstat "$work/p.patch" | cut -f3- | grep -Ev "$allowed" || true; })"
  case "${case%%:*}:${bad:+refused}" in
    inside:)         ok "publish accepts a non-ASCII concept path" ;;
    outside:refused) ok "publish still refuses a non-ASCII path outside the bundle" ;;
    *)               err "publish path check got ${case#*:} wrong (refused: ${bad:-nothing})" ;;
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

echo "5. the release workflow's compare and pack steps"
# Run the template's own lines, so the test breaks if they change: the
# bundle_tree function, the mtime line and the tar line.
bundle_tree_fn="$(sed -n '/^ *bundle_tree() {$/,/^          }$/p' "$release_yaml")"
mtime_line="$(grep -E '^\s*mtime=' "$release_yaml" | sed 's/^[[:space:]]*//')"
# shellcheck disable=SC2016 # the pattern matches a literal "$src"
tar_line="$(grep -E '^\s*tar -C "\$src"' "$release_yaml" | sed 's/^[[:space:]]*//')"
if [ -z "$bundle_tree_fn" ] || [ -z "$mtime_line" ] || [ -z "$tar_line" ]; then
  err "knowledge-release.yaml no longer has a bundle_tree function, an mtime= line and a 'tar -C \"\$src\"' line"
else
  eval "$bundle_tree_fn"
  # pack <host> <tag> <out dir> - runs the template's pack lines at the tag's checkout
  pack() {
    # shellcheck disable=SC2034 # asset, src and mtime are read by the eval'd lines
    ( cd "$1" && git checkout -q "$2" && export RUNNER_TEMP="$3" && mkdir -p "$RUNNER_TEMP/release" \
        && read -r _ BUNDLE_PATH < <(bundle_tree HEAD) && asset=knowledge.tar.gz \
        && src="$(cd .lokf/knowledge && pwd -P)" && eval "$mtime_line" && eval "$tar_line" )
  }
  for shape in default no-doorway rearranged; do
    host="$work/release-$shape"
    make_host "$host" "$shape"
    ln -s ./a.md "$host/.lokf/knowledge/alias.md"
    ( cd "$host" && git add -A && git commit -q -m link && git -c tag.gpgSign=false tag v1 \
        && sleep 1 && printf 'more\n' >> README.md && git commit -qam readme && git -c tag.gpgSign=false tag v2 \
        && sleep 1 && printf 'more\n' >> .lokf/knowledge/a.md && git commit -qam concept && git -c tag.gpgSign=false tag v3 )
    t1="$(cd "$host" && bundle_tree v1)"; t2="$(cd "$host" && bundle_tree v2)"; t3="$(cd "$host" && bundle_tree v3)"
    if [ -n "$t1" ] && [ "$t1" = "$t2" ]; then ok "$shape: a README-only release compares as unchanged ($t1)"
    else err "$shape: a README-only release compared as changed ($t1 vs $t2)"; fi
    if [ "${t3%% *}" != "${t2%% *}" ]; then ok "$shape: a concept edit compares as changed"
    else err "$shape: a concept edit compared as unchanged"; fi
    for tag in v1 v2 v3; do pack "$host" "$tag" "$work/rt-$shape-$tag"; done
    pack "$host" v1 "$work/rt-$shape-again"
    tarball="$work/rt-$shape-v1/release/knowledge.tar.gz"
    listing="$(tar -tzf "$tarball" | tr '\n' ' ')"
    if [ "$listing" = "knowledge/ knowledge/a.md knowledge/alias.md " ]; then
      ok "$shape: the tarball holds the bundle under knowledge/ and nothing else"
    else err "$shape: unexpected tarball listing ($listing)"; fi
    if tar -tvzf "$tarball" | grep -q 'knowledge/alias.md -> \./a\.md$'; then ok "$shape: a link inside the bundle keeps its target"
    else err "$shape: a link inside the bundle lost its target"; fi
    if cmp -s "$tarball" "$work/rt-$shape-again/release/knowledge.tar.gz"; then ok "$shape: two packs of one tag give the same bytes"
    else err "$shape: two packs of one tag differ"; fi
    if cmp -s "$tarball" "$work/rt-$shape-v2/release/knowledge.tar.gz"; then ok "$shape: an unchanged bundle packs to the same bytes at a later tag"
    else err "$shape: an unchanged bundle packed differently at a later tag"; fi
    if ! cmp -s "$tarball" "$work/rt-$shape-v3/release/knowledge.tar.gz"; then ok "$shape: a changed bundle packs to different bytes"
    else err "$shape: a changed bundle packed to the same bytes"; fi
  done
fi

echo ""
if [ "$fail" -eq 0 ]; then echo "Layout tests: PASS"; exit 0; else echo "Layout tests: FAIL"; exit 1; fi
