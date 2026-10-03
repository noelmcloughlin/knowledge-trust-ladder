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
#   1. the librarian wrapper refuses a run in which the agent edited anything
#      itself, under either name of the bundle or outside it, and applies the
#      one file the agent may write, .lokf/patch.yaml, with knowledge-apply.sh,
#      which refuses a bad patch - with the doorway, without it, and in the
#      rearranged shape; and (1b) the wrapper puts
#      .git/config and .git/hooks/ back when the agent fails or the job is
#      cancelled, not only when it returns cleanly; and (1c) the wrapper hands
#      AGENT_API_KEY to the agent under AGENT_API_KEY_ENV's name only, and
#      refuses a name that is not a credential's; and (1d) a change that
#      touches a person's record is refused even when the pen let it through;
#      and (1e) with KNOWLEDGE_RETRIEVAL on, the wrapper has the agent answer
#      the index-only retrieval test from an empty directory, writes the score
#      a program computes, and refuses a call that changed the checkout; and
#      (1f) a sidecar with no pen stops the wrapper before the agent runs;
#   2. the librarian workflow's change detection sees a bundle edit in each of
#      those shapes, and its packaging step stages it without failing when the
#      second name does not exist;
#   3. the registrar workflow triggers on, and diffs, both names; and (3b) its
#      provenance step, run here as the template has it with `gh` stubbed,
#      asks the person behind a confirmation that is added, changed or
#      removed, and nobody when only a body changes;
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
    cp "$templates/scripts/knowledge-apply.sh" "$templates/scripts/knowledge-apply.py" .lokf/scripts/
    cp "$templates/scripts/knowledge-provenance.sh" "$templates/scripts/knowledge-report.sh" .lokf/scripts/
    chmod +x .lokf/scripts/knowledge-*.sh .lokf/scripts/knowledge-apply.py
    cp "$justfile" .lokf/justfile
    printf '# stub skill\n' > skills/ktl-librarian/SKILL.md
    case "$shape" in
      default)     mkdir -p .lokf/knowledge; ln -s .lokf/knowledge knowledge_bundle ;;
      no-doorway)  mkdir -p .lokf/knowledge ;;
      rearranged)  mkdir -p knowledge_bundle; ln -s ../knowledge_bundle .lokf/knowledge ;;
      *) echo "unknown shape $shape" >&2; exit 2 ;;
    esac
    printf -- '---\nbase_iri: https://host.example/knowledge/\n---\n\n# Host\n' > .lokf/knowledge/index.md
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

# The wrapper applies .lokf/patch.yaml with knowledge-apply.sh after the agent
# returns, and refuses a run in which the agent changed anything else, so the
# agent never writes the bundle itself. This stand-in writes PATCH_TEXT to the
# patch file and nothing else.
patch_agent="$work/patch-agent.sh"
cat > "$patch_agent" <<'AGENT'
#!/usr/bin/env bash
printf '%s\n' "$PATCH_TEXT" > .lokf/patch.yaml
AGENT
chmod +x "$patch_agent"
create_op='ops:
  - op: create
    path: playbooks/b.md
    frontmatter: {type: Playbook, title: B, description: made through the pen.}
    body: "# B\n\nMade through the pen.\n"'
bad_op='ops:
  - op: delete
    path: playbooks/missing.md
    log: gone'

# run_patch <dir> <patch text> - prints the wrapper's exit status and whether
# the pen wrote playbooks/b.md and removed the patch file, then resets the tree.
run_patch() {
  local dir="$1" text="$2" status=0 wrote=no
  ( cd "$dir" && AGENT_CLI="$patch_agent" PATCH_TEXT="$text" bash .lokf/scripts/knowledge-librarian.sh >/dev/null 2>&1 ) || status=$?
  [ -f "$dir/.lokf/knowledge/playbooks/b.md" ] && wrote=yes
  [ -e "$dir/.lokf/patch.yaml" ] && wrote="$wrote,patch-left"
  git -C "$dir" checkout -q -- . && git -C "$dir" clean -qfd
  printf '%s %s' "$status" "$wrote"
}

echo "1. the librarian wrapper's boundary: one patch file in, and only the pen writes the bundle"
for shape in default rearranged no-doorway; do
  host="$work/wrapper-$shape"
  make_host "$host" "$shape"
  edits=".lokf/knowledge/a.md README.md"
  [ "$shape" != no-doorway ] && edits="$edits knowledge_bundle/a.md"
  for edit in $edits; do
    status="$(run_wrapper "$host" "$edit")"
    if [ "$status" = 3 ]; then ok "$shape: an agent that edits $edit itself is refused (exit 3)"
    else err "$shape: an agent that edits $edit itself was not refused (exit $status)"; fi
  done
  result="$(run_patch "$host" "$create_op")"
  if [ "$result" = "0 yes" ]; then ok "$shape: a patch file is applied by the pen, which writes playbooks/b.md and removes the file (exit 0)"
  else err "$shape: a valid patch file was not applied as expected (got: $result)"; fi
  result="$(run_patch "$host" "$bad_op")"
  if [ "$result" = "4 no" ]; then ok "$shape: a patch the pen refuses fails the run and writes nothing (exit 4)"
  else err "$shape: a refused patch did not fail the run cleanly (got: $result)"; fi
done

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

# 1d. What the pen refuses before it writes is read off the result as well, so
# a pen that let a person's event through - a poisoned copy, in a workspace
# the agent shared - still fails the run. The stand-in pen here writes one.
host="$work/wrapper-unattended"
make_host "$host" default
cat > "$host/.lokf/scripts/knowledge-apply.sh" <<'PEN'
#!/usr/bin/env bash
printf -- '---\ntype: Service\ntitle: A\nverified: [{ by: human:nobody, at: "2026-01-01T00:00:00Z" }]\n---\n\n# A\n' > .lokf/knowledge/a.md
rm -f .lokf/patch.yaml
PEN
git -C "$host" commit -q -am "a pen that lets a person's event through"
status=0
( cd "$host" && AGENT_CLI="$patch_agent" PATCH_TEXT="$create_op" bash .lokf/scripts/knowledge-librarian.sh >/dev/null 2>&1 ) || status=$?
if [ "$status" = 3 ]; then ok "unattended: a person's event the pen let through fails the run (exit 3)"
else err "unattended: a person's event reached the bundle unrefused (exit $status)"; fi

# 1e. The retrieval test is off unless KNOWLEDGE_RETRIEVAL is "true". On, the
# same agent command is called a second time from an empty directory: this
# stand-in writes the patch when it finds itself in the repository, and
# answers the one question otherwise.
retrieval_agent="$work/retrieval-agent.sh"
cat > "$retrieval_agent" <<'AGENT'
#!/usr/bin/env bash
if [ -d .lokf ]; then
  printf '%s\n' "$PATCH_TEXT" > .lokf/patch.yaml
else
  [ -z "${MEDDLE:-}" ] || printf 'meddled\n' >> "$MEDDLE"
  echo "Q1: a.md"
fi
AGENT
chmod +x "$retrieval_agent"
# shellcheck disable=SC2016 # the backticks are a Markdown code span, not a command
retrieval_host() {
  make_host "$1" default
  printf '%s\n' '# Questions readers asked' '' 'Kept by knowledge-apply.sh.' '' '- 2026-01-01 Miss a.md: `where is a?`' > "$1/.lokf/questions.md"
  git -C "$1" add -A && git -C "$1" commit -q -m "a question on file"
}
host="$work/wrapper-retrieval"
retrieval_host "$host"
status=0; rm -f "$work/retrieval.txt"
( cd "$host" && AGENT_CLI="$retrieval_agent" PATCH_TEXT="$create_op" KNOWLEDGE_RETRIEVAL=true KNOWLEDGE_RETRIEVAL_OUT="$work/retrieval.txt" \
    bash .lokf/scripts/knowledge-librarian.sh >/dev/null 2>&1 ) || status=$?
if [ "$status" = 0 ] && [ "$(cat "$work/retrieval.txt" 2>/dev/null)" = "Retrieval from the index: 1 of 1 reader questions reach their concept" ] && [ -f "$host/.lokf/knowledge/playbooks/b.md" ]; then
  ok "retrieval: with the switch on, the reply is scored by program and the one line is written (exit 0)"
else err "retrieval: exit $status, score file: $(cat "$work/retrieval.txt" 2>/dev/null || echo none)"; fi
host="$work/wrapper-retrieval-off"
retrieval_host "$host"
status=0; rm -f "$work/retrieval.txt"
( cd "$host" && AGENT_CLI="$retrieval_agent" PATCH_TEXT="$create_op" KNOWLEDGE_RETRIEVAL_OUT="$work/retrieval.txt" bash .lokf/scripts/knowledge-librarian.sh >/dev/null 2>&1 ) || status=$?
if [ "$status" = 0 ] && [ ! -e "$work/retrieval.txt" ]; then ok "retrieval: with the switch off, the agent is called once and nothing is scored"
else err "retrieval: scored with the switch off (exit $status)"; fi
host="$work/wrapper-retrieval-meddle"
retrieval_host "$host"
status=0; rm -f "$work/retrieval.txt"
( cd "$host" && AGENT_CLI="$retrieval_agent" PATCH_TEXT="$create_op" KNOWLEDGE_RETRIEVAL=true KNOWLEDGE_RETRIEVAL_OUT="$work/retrieval.txt" MEDDLE="$host/README.md" \
    bash .lokf/scripts/knowledge-librarian.sh >/dev/null 2>&1 ) || status=$?
if [ "$status" = 3 ] && [ ! -e "$work/retrieval.txt" ]; then ok "retrieval: a call that changes the checkout is refused and no score is written (exit 3)"
else err "retrieval: a call that changed the checkout was not refused (exit $status)"; fi

# 1f. A sidecar that never laid the pen down is said before an agent run is
# spent on it: the wrapper exits 2 and the agent is not called.
host="$work/wrapper-no-pen"
make_host "$host" default
rm "$host/.lokf/scripts/knowledge-apply.py"
status=0; rm -f "$work/env.out"
( cd "$host" && AGENT_CLI="$env_agent" ENV_OUT="$work/env.out" bash .lokf/scripts/knowledge-librarian.sh >/dev/null 2>&1 ) || status=$?
if [ "$status" = 2 ] && [ ! -e "$work/env.out" ]; then ok "no pen: the wrapper stops before the agent runs (exit 2)"
else err "no pen: the wrapper ran the agent or did not stop (exit $status)"; fi

echo "2. the librarian workflow's change detection and packaging"
detect='git status --porcelain -- .lokf/knowledge knowledge_bundle'
if grep -qF "$detect" "$librarian_yaml"; then ok "template detects changes with: $detect"
else err "knowledge-librarian.yaml no longer contains: $detect"; fi
stage_second='[ -e knowledge_bundle ] && git add -A -- knowledge_bundle || true'
if grep -qF 'git add -A -- .lokf/knowledge' "$librarian_yaml" && grep -qF "$stage_second" "$librarian_yaml"; then
  ok "template stages both names and guards the second one"
else err "knowledge-librarian.yaml packaging lines changed"; fi
if grep -qF '[ -e .lokf/feedback.md ] && git add -A -- .lokf/feedback.md || true' "$librarian_yaml" \
   && grep -qF '[ -e .lokf/questions.md ] && git add -A -- .lokf/questions.md || true' "$librarian_yaml"; then
  ok "template carries reader feedback and the ledger its handled entries move into"
else err "knowledge-librarian.yaml no longer stages .lokf/feedback.md and .lokf/questions.md"; fi
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
allowed='^(\.lokf/knowledge/|knowledge_bundle/|\.lokf/feedback\.md$|\.lokf/questions\.md$)'
if grep -qF -- "grep -Ev '$allowed'" "$librarian_yaml"; then ok "template refuses a patch path outside: $allowed"
else err "knowledge-librarian.yaml no longer filters the patch's paths with: $allowed"; fi
# The publish job reads a person's events off the patched tree, and fills the
# pull request from its own checkout, with the scripts that checkout holds.
for line in 'bash .lokf/scripts/knowledge-provenance.sh --unattended' 'bash .lokf/scripts/knowledge-report.sh health' 'bash .lokf/scripts/knowledge-report.sh changes'; do
  if sed -n '/^  publish:/,$p' "$librarian_yaml" | grep -qF -- "$line"; then ok "publish runs: $line"
  else err "knowledge-librarian.yaml's publish job no longer runs: $line"; fi
done
for case in "inside:.lokf/knowledge/café.md" "inside:.lokf/questions.md" "outside:notes-café.md" "outside:.lokf/scripts/knowledge-apply.sh"; do
  printf 'x\n' > "$host/${case#*:}"
  (cd "$host" && git add -A && git diff --cached --binary > "$work/p.patch" && git reset -q --hard)
  bad="$(cd "$host" && { git -c core.quotePath=false apply --numstat "$work/p.patch" | cut -f3- | grep -Ev "$allowed" || true; })"
  case "${case%%:*}:${bad:+refused}" in
    inside:)         ok "publish accepts ${case#*:}" ;;
    outside:refused) ok "publish refuses ${case#*:}, a path outside the bundle, the feedback file and the ledger" ;;
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

# 3b. The provenance step itself, extracted from the template so the test
# breaks when its lines change. `gh` is a stand-in that answers the two API
# calls the step makes: who approved, and which commits GitHub verified for
# whom. A person's record is never removed without that person, so a
# confirmation struck out, or gone with its concept, needs the same backing
# as one that is added; a person's generated record may give way to another
# person's, the curator's Correct, and to nothing else.
step="$work/provenance-step.sh"
awk '/^      - name: Every new human confirmation must come from that person$/ { on = 1 }
     on && /^        run: \|$/ { body = 1; next }
     body && /^      [#-]/ { exit }
     body { sub(/^          /, ""); print }' "$registrar_yaml" > "$step"
if ! grep -q 'removed_actors' "$step" || ! bash -n "$step" 2>/dev/null; then
  err "could not extract the provenance step from knowledge-registrar.yaml, or it no longer holds removed_actors"
else
  mkdir -p "$work/stub"
  cat > "$work/stub/gh" <<'GH'
#!/usr/bin/env bash
case "$*" in
  *reviews*) cat "$STUB_APPROVERS" ;;
  *commits*) cat "$STUB_COMMITS" ;;
esac
GH
  chmod +x "$work/stub/gh"
  # provenance_case <label> <change> <approver or ""> <signer or "-"> <expected exit> <expected line>
  provenance_case() {
    local label="$1" change="$2" approver="$3" signer="$4" want="$5" line="$6" repo="$work/provenance-$1" k base head sha out status=0
    k="$repo/.lokf/knowledge/x"; mkdir -p "$k"
    (
      cd "$repo"
      git init -q -b main . && git config user.email "layout-test@example.invalid" && git config user.name "layout test"
      printf -- '---\ntype: Service\nid: https://e.invalid/k/x/confirmed\nverified:\n  - by: human:ada\n    at: "2026-09-17T00:00:00Z"\n---\n\nText.\n' > "$k/confirmed.md"
      printf -- '---\ntype: Service\nid: https://e.invalid/k/x/authored\ngenerated:\n  by: human:ada\n  at: "2026-09-17T00:00:00Z"\n---\n\nWritten.\n' > "$k/authored.md"
      printf -- '---\ntype: Service\nid: https://e.invalid/k/x/plain\n---\n\nPlain.\n' > "$k/plain.md"
      git add -A && git commit -q -m base
    )
    base="$(git -C "$repo" rev-parse HEAD)"
    case "$change" in
      strike)   printf -- '---\ntype: Service\nid: https://e.invalid/k/x/confirmed\n---\n\nText.\n' > "$k/confirmed.md" ;;
      remove)   rm "$k/confirmed.md" ;;
      correct)  printf -- '---\ntype: Service\nid: https://e.invalid/k/x/authored\ngenerated:\n  by: human:bob\n  at: "2026-09-20T00:00:00Z"\n---\n\nCorrected.\n' > "$k/authored.md" ;;
      restamp)  printf -- '---\ntype: Service\nid: https://e.invalid/k/x/authored\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-09-20T00:00:00Z"\n---\n\nRewritten.\n' > "$k/authored.md" ;;
      bodyonly) printf 'More.\n' >> "$k/confirmed.md" ;;
      confirm)  printf -- '---\ntype: Service\nid: https://e.invalid/k/x/plain\nverified: [{ by: human:bob, at: "2026-09-20T00:00:00Z" }]\n---\n\nPlain.\n' > "$k/plain.md" ;;
      *) echo "unknown change $change" >&2; exit 2 ;;
    esac
    (cd "$repo" && git add -A && git commit -q -m change)
    head="$(git -C "$repo" rev-parse HEAD)"
    printf '%s\n' "$approver" | sed '/^$/d' > "$work/approvers"
    : > "$work/commits"
    for sha in $(git -C "$repo" rev-list "$base..$head"); do
      if [ "$signer" = "-" ]; then printf '%s\tfalse\t-\n' "$sha"; else printf '%s\ttrue\t%s\n' "$sha" "$signer"; fi >> "$work/commits"
    done
    out="$(cd "$repo" && PATH="$work/stub:$PATH" GH_TOKEN=x PR_NUMBER=1 BASE_SHA="$base" HEAD_SHA="$head" ATTEST_ENV="" GITHUB_REPOSITORY=o/r \
            GITHUB_OUTPUT="$work/gh-output" GITHUB_STEP_SUMMARY="$work/gh-summary" STUB_APPROVERS="$work/approvers" STUB_COMMITS="$work/commits" bash "$step" 2>&1)" || status=$?
    if [ "$status" = "$want" ] && grep -q -- "$line" <<<"$out"; then ok "provenance/$label: exit $status"
    else err "provenance/$label: exit $status (want $want), and no line matching '$line' in: $out"; fi
  }
  provenance_case struck-out-unbacked  strike   ""  -   1 'removes a confirmation by human:ada but GitHub reports it verified=false'
  provenance_case struck-out-approved  strike   ada -   0 'ok: human:ada approved this pull request'
  provenance_case struck-out-signed    strike   ""  ada 0 'ok: human:ada signed each commit'
  provenance_case deleted-unbacked     remove   ""  -   1 'confirmation by human:ada'
  provenance_case corrected-by-another correct  bob -   0 'ok: human:bob approved this pull request'
  provenance_case restamped-by-process restamp  ""  -   1 'confirmation by human:ada'
  provenance_case body-only            bodyonly ""  -   0 'No human confirmation is added, changed or removed'
  provenance_case confirmed-approved   confirm  bob -   0 'ok: human:bob approved this pull request'
fi

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
# bundle_tree function, the mtime line and the lines from stage= to zip.
bundle_tree_fn="$(sed -n '/^ *bundle_tree() {$/,/^          }$/p' "$release_yaml")"
mtime_line="$(grep -E '^\s*mtime=' "$release_yaml" | sed 's/^[[:space:]]*//')"
zip_lines="$(sed -n '/^ *stage=/,/ zip -q -X -y -@ /p' "$release_yaml" | sed 's/^[[:space:]]*//')"
if [ -z "$bundle_tree_fn" ] || [ -z "$mtime_line" ] || ! grep -q ' zip -q -X -y -@ ' <<<"$zip_lines"; then
  err "knowledge-release.yaml no longer has a bundle_tree function, an mtime= line and the stage= to 'zip -q -X -y -@' lines"
elif ! command -v zip >/dev/null || ! command -v unzip >/dev/null; then
  echo "SKIP: zip and unzip are not installed - the pack tests need them"
else
  eval "$bundle_tree_fn"
  # pack <host> <tag> <out dir> [TZ] - runs the template's pack lines at the tag's checkout
  pack() {
    # shellcheck disable=SC2034 # asset, src and mtime are read by the eval'd lines
    ( cd "$1" && git checkout -q "$2" && export RUNNER_TEMP="$3" TZ="${4:-UTC}" && mkdir -p "$RUNNER_TEMP/release" \
        && read -r _ BUNDLE_PATH < <(bundle_tree "$2") && asset=knowledge.zip \
        && src="$(cd "$BUNDLE_PATH" && pwd -P)" && eval "$mtime_line" && eval "$zip_lines" )
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
    # A second pack of v1 in another time zone and under a tight umask.
    ( umask 077 && pack "$host" v1 "$work/rt-$shape-again" Asia/Tokyo )
    zipfile="$work/rt-$shape-v1/release/knowledge.zip"
    listing="$(unzip -Z1 "$zipfile" | tr '\n' ' ')"
    if [ "$listing" = "knowledge/a.md knowledge/alias.md knowledge/index.md " ]; then
      ok "$shape: the zip holds the bundle under knowledge/ and nothing else"
    else err "$shape: unexpected zip listing ($listing)"; fi
    if unzip -Z "$zipfile" knowledge/alias.md | grep -q '^l' && [ "$(unzip -p "$zipfile" knowledge/alias.md)" = "./a.md" ]; then
      ok "$shape: a link inside the bundle is stored as a link and keeps its target"
    else err "$shape: a link inside the bundle was followed or lost its target"; fi
    if cmp -s "$zipfile" "$work/rt-$shape-again/release/knowledge.zip"; then ok "$shape: two packs of one tag give the same bytes, whatever the time zone and umask"
    else err "$shape: two packs of one tag differ"; fi
    if cmp -s "$zipfile" "$work/rt-$shape-v2/release/knowledge.zip"; then ok "$shape: an unchanged bundle packs to the same bytes at a later tag"
    else err "$shape: an unchanged bundle packed differently at a later tag"; fi
    if ! cmp -s "$zipfile" "$work/rt-$shape-v3/release/knowledge.zip"; then ok "$shape: a changed bundle packs to different bytes"
    else err "$shape: a changed bundle packed to the same bytes"; fi
  done
fi

echo ""
if [ "$fail" -eq 0 ]; then echo "Layout tests: PASS"; exit 0; else echo "Layout tests: FAIL"; exit 1; fi
