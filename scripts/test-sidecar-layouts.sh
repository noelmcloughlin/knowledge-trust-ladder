#!/usr/bin/env bash
# Layout tests for the way ktl-sidecar installs a bundle (SKILL.md Step 2).
#
# The bundle is `.lokf/knowledge`, which the tools address, and `knowledge_bundle`
# beside it is the doorway link people and Obsidian open. A git pathspec never
# traverses a symlink, so a template that scopes a diff to the bundle names both
# paths. With the doorway the second name matches nothing, harmlessly. It still
# covers a shared folder someone rearranged by hand into a real
# `knowledge_bundle/` with `.lokf/knowledge` linking onto it (see the sidecar's
# references/portability.md). These tests pin that for the template files that
# do so, and for the `just lokf-link` recipe:
#
#   1. the librarian wrapper:
#      (1)  refuses a run in which the agent edited anything itself, under
#           either name of the bundle or outside it, and applies the one file
#           the agent may write, .lokf/patch.yaml, with knowledge-apply.sh,
#           which refuses a bad patch: with the doorway, without it, and in
#           the rearranged shape;
#      (1b) puts .git/config and .git/hooks/ back when the agent fails or the
#           job is cancelled, not only when it returns cleanly;
#      (1c) hands AGENT_API_KEY to the agent under AGENT_API_KEY_ENV's name
#           only, and refuses a name that is not a credential's;
#      (1d) refuses a change that touches a person's record even when the pen
#           let it through;
#      (1e) with KNOWLEDGE_RETRIEVAL on, has the agent answer the index-only
#           retrieval test from an empty directory, writes the score a
#           program computes, and refuses a call that changed the checkout;
#      (1f) stops before the agent runs when the sidecar has no pen;
#      (1g) skips the agent for a quiet bundle only when KNOWLEDGE_SKIP_QUIET
#           allows it, and counts a change a person declined as no work;
#      (1h) passes the hand-off to its file through the pen, cleaned, after
#           whatever the agent left at either output path is gone, and writes
#           it again after the retrieval call;
#   2. the librarian workflow's change detection sees a bundle edit in each of
#      those shapes, and its packaging step stages it without failing when the
#      second name does not exist. Its pull request says how the conventions
#      script ended, and cleans the hand-off by Unicode category. A scheduled
#      run waits while an earlier pull request of the workflow's is open, and
#      the step that reads those pull requests (2b), run here as the template
#      has it with `gh` stubbed, hands on what a person declined as numbers,
#      paths and hashes. Its install step (2c) installs the skill from the
#      pinned tag only while that tag names the pinned commit;
#   3. the registrar workflow triggers on, and diffs, both names, and like
#      the other two templates installs the sidecar from its lock. Its
#      provenance step (3b), run here as the template has it with `gh`
#      stubbed, asks the person behind a confirmation that is added, changed
#      or removed, and nobody when only a body changes;
#   4. `just lokf-link` creates the doorway, is a no-op when it is present,
#      refuses a name taken by something else, and does nothing when
#      `.lokf/knowledge` is itself a link;
#   5. the release workflow compares an unchanged bundle as unchanged and an
#      edited one as changed in each shape. Its pack step puts the bundle, and
#      nothing beside it, under `knowledge/`, keeps a link's target as
#      written, and gives the same bytes for the same bundle, at the same tag
#      or a later one.
#
# Needs bash and git. `just` and `jq` are optional: without `just`, test 4 is
# skipped and says so, and without `jq`, test 2b is.
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
# Isolate the fixtures from the machine's git config, so a global
# commit.gpgsign=true does not sign every fixture commit (and fail where no key
# is cached), and keep temporary files the extracted workflow steps create
# under $work, where the trap removes them, rather than in the system TMPDIR.
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export TMPDIR="$work"

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
# the bundle, and the two names set up the way the shape says.
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

# run_wrapper <dir> <path the fake agent edits>: prints the wrapper's exit status
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

# run_patch <dir> <patch text>: prints the wrapper's exit status and whether
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
# only after a clean return. An agent that rewrites both and then exits
# non-zero (set -e ends the wrapper there), or gets the job cancelled (SIGTERM,
# which bash delivers once the agent has exited), must leave neither behind.
# The wrapper's own exit status must be the agent's, or the signal's.
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

# 1d. What the pen refuses before it writes is checked on the result as well.
# So a pen that let a person's event through, such as a tampered copy in a
# workspace the agent shared, still fails the run. The stand-in pen here writes one.
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
  [ -z "${PLANT:-}" ] || printf 'planted in the retrieval call\n' > "$PLANT"
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

# 1g. A run with nothing waiting skips the agent when the caller allows it:
# with KNOWLEDGE_SKIP_QUIET "true", the wrapper asks knowledge-report.sh and,
# on a quiet bundle, exits 0 without calling the agent. Unset, or with work
# waiting, the agent runs as before.
host="$work/wrapper-quiet"
make_host "$host" default
printf -- '---\ntype: Service\ntitle: A\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n---\n\n# A\n' > "$host/.lokf/knowledge/a.md"
git -C "$host" commit -q -am "a stamped concept"
quiet_case() {  # <label> <KNOWLEDGE_SKIP_QUIET> <ran|skipped> [<the file KNOWLEDGE_DECLINED names>]
  local status=0 got=skipped
  rm -f "$work/env.out"
  ( cd "$host" && AGENT_CLI="$env_agent" ENV_OUT="$work/env.out" KNOWLEDGE_SKIP_QUIET="$2" KNOWLEDGE_DECLINED="${4:-}" bash .lokf/scripts/knowledge-librarian.sh >/dev/null 2>&1 ) || status=$?
  [ -e "$work/env.out" ] && got=ran
  if [ "$status" = 0 ] && [ "$got" = "$3" ]; then ok "quiet/$1: the agent $got (exit 0)"
  else err "quiet/$1: the agent $got, exit $status (want $3, exit 0)"; fi
}
quiet_case "nothing waits, skip allowed" true skipped
quiet_case "nothing waits, skip not allowed" "" ran
printf '%s\n' '# Reader feedback' '' '## 2026-01-02' '' '- **Miss** - a reader asked. - docent' > "$host/.lokf/feedback.md"
quiet_case "reader feedback waits" true ran
rm "$host/.lokf/feedback.md"
# A source that moved makes work. On a scheduled run it makes none once a
# person has closed the pull request that changed its concept, which the
# workflow says in the file KNOWLEDGE_DECLINED names. The source makes work
# again when it moves after that pull request.
printf -- '---\ntype: Service\ntitle: A\nresource: README.md\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n---\n\n# A\n' > "$host/.lokf/knowledge/a.md"
git -C "$host" commit -q -am "the concept names its source"
printf 'more\n' >> "$host/README.md" && git -C "$host" commit -q -am "the source moves"
quiet_case "a source moved" true ran
printf 'declined 7 2026-01-03 %s\ntouched a.md\n' "$(git -C "$host" rev-parse HEAD)" > "$work/declined.txt"
quiet_case "a source moved, and a person closed the pull request that changed its concept" true skipped "$work/declined.txt"
printf 'again\n' >> "$host/README.md" && git -C "$host" commit -q -am "the source moves again"
quiet_case "the source moved again after that pull request" true ran "$work/declined.txt"

# 1h. The patch file's hand-off reaches the file KNOWLEDGE_HANDOFF_OUT names
# through the pen, cleaned. What the agent left at that path, or at the
# retrieval score's, is gone first: a file it wrote there, and a link that
# would send the next write into the checkout.
plant_agent="$work/plant-agent.sh"
cat > "$plant_agent" <<'AGENT'
#!/usr/bin/env bash
printf '%s\n' "$PATCH_TEXT" > .lokf/patch.yaml
printf 'planted by the agent\n' > "$KNOWLEDGE_HANDOFF_OUT"
ln -sf "$PWD/README.md" "$KNOWLEDGE_RETRIEVAL_OUT"
AGENT
chmod +x "$plant_agent"
handoff_patch="$create_op
handoff:
  - \"one line for the reviewer, with a \`backtick\`\""
host="$work/wrapper-handoff"
make_host "$host" default
status=0; rm -f "$work/handoff.txt" "$work/retrieval.txt"
( cd "$host" && AGENT_CLI="$plant_agent" PATCH_TEXT="$handoff_patch" KNOWLEDGE_HANDOFF_OUT="$work/handoff.txt" KNOWLEDGE_RETRIEVAL_OUT="$work/retrieval.txt" \
    bash .lokf/scripts/knowledge-librarian.sh >/dev/null 2>&1 ) || status=$?
if [ "$status" = 0 ] && [ "$(cat "$work/handoff.txt" 2>/dev/null)" = "one line for the reviewer, with a 'backtick'" ] \
   && [ -f "$host/.lokf/knowledge/playbooks/b.md" ] && ! grep -rq 'one line for the reviewer' "$host/.lokf/knowledge"; then
  ok "hand-off: the pen's cleaned lines replace what the agent wrote at the path, and none reach the bundle (exit 0)"
else err "hand-off: exit $status, file holds: $(cat "$work/handoff.txt" 2>/dev/null || echo nothing)"; fi
if [ ! -L "$work/retrieval.txt" ] && [ ! -s "$work/retrieval.txt" ] && [ "$(cat "$host/README.md")" = "# host" ]; then
  ok "hand-off: a link the agent left at the retrieval score's path is gone, and nothing was written through it"
else err "hand-off: the retrieval path is still a link, or holds the agent's text, or the checkout's README changed"; fi
# The retrieval call comes after the pen has written the hand-off, and its
# prompt carries readers' words. What that call leaves at the hand-off's path
# is gone too: the reviewer reads the pen's lines, or none when the patch held
# none.
host="$work/wrapper-handoff-retrieval"
retrieval_host "$host"
status=0; rm -f "$work/handoff.txt" "$work/retrieval.txt"
( cd "$host" && AGENT_CLI="$retrieval_agent" PATCH_TEXT="$handoff_patch" KNOWLEDGE_RETRIEVAL=true PLANT="$work/handoff.txt" \
    KNOWLEDGE_HANDOFF_OUT="$work/handoff.txt" KNOWLEDGE_RETRIEVAL_OUT="$work/retrieval.txt" bash .lokf/scripts/knowledge-librarian.sh >/dev/null 2>&1 ) || status=$?
if [ "$status" = 0 ] && [ "$(cat "$work/handoff.txt" 2>/dev/null)" = "one line for the reviewer, with a 'backtick'" ] && grep -q '1 of 1' "$work/retrieval.txt"; then
  ok "hand-off: the pen's lines are written again after the retrieval call, over what that call left at the path (exit 0)"
else err "hand-off: exit $status after a retrieval call that wrote the hand-off's path, file holds: $(cat "$work/handoff.txt" 2>/dev/null || echo nothing)"; fi
host="$work/wrapper-handoff-retrieval-none"
retrieval_host "$host"
status=0; rm -f "$work/handoff.txt" "$work/retrieval.txt"
( cd "$host" && AGENT_CLI="$retrieval_agent" PATCH_TEXT="$create_op" KNOWLEDGE_RETRIEVAL=true PLANT="$work/handoff.txt" \
    KNOWLEDGE_HANDOFF_OUT="$work/handoff.txt" KNOWLEDGE_RETRIEVAL_OUT="$work/retrieval.txt" bash .lokf/scripts/knowledge-librarian.sh >/dev/null 2>&1 ) || status=$?
if [ "$status" = 0 ] && [ ! -s "$work/handoff.txt" ]; then
  ok "hand-off: a patch with none leaves none, whatever the retrieval call wrote at the path (exit 0)"
else err "hand-off: exit $status, and a hand-off the retrieval call wrote survived: $(cat "$work/handoff.txt" 2>/dev/null)"; fi

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
# A scheduled run may skip a quiet week, except in a month's first seven
# days; a run a person starts never skips.
# shellcheck disable=SC2016 # the template's own $(...), matched as text
if grep -qF "KNOWLEDGE_SKIP_QUIET: \${{ github.event_name == 'schedule' }}" "$librarian_yaml" \
   && grep -qF 'if [ "$(date -u +%d)" -le 7 ]; then export KNOWLEDGE_SKIP_QUIET=false; fi' "$librarian_yaml"; then
  ok "template lets a scheduled run skip a quiet week, outside a month's first seven days"
else err "knowledge-librarian.yaml no longer sets KNOWLEDGE_SKIP_QUIET for scheduled runs, or lost the monthly full run"; fi
# The hand-off goes from the pen, through the artifact, to the pull request.
# shellcheck disable=SC2016 # the template's own ${{ }} expressions, matched as text
if grep -qF 'KNOWLEDGE_HANDOFF_OUT: ${{ runner.temp }}/handoff.txt' "$librarian_yaml" \
   && grep -qF '${{ runner.temp }}/handoff.txt' <(sed -n '/name: Upload the bundle patch/,/if-no-files-found/p' "$librarian_yaml") \
   && grep -qF 'HANDOFF_FILE: ${{ runner.temp }}/handoff.txt' "$librarian_yaml" && grep -qF "'\`\`\`text', ...handoff, '\`\`\`'" "$librarian_yaml"; then
  ok "template carries the hand-off in the artifact and shows it in a code block"
else err "knowledge-librarian.yaml lost the hand-off's path from the pen to the pull request"; fi
# `publish` cleans the hand-off again, by Unicode category as the pen does: a
# control, a format character or a line separator, whichever block it sits in.
# The expression is run as the template has it where node is installed.
clean_line="$(grep -F '.map((l) => l.replace(' "$librarian_yaml" | sed 's/^ *//')"
# shellcheck disable=SC2016 # the backtick is JavaScript's, matched as text
if [ "$clean_line" = '.map((l) => l.replace(/[\p{Cc}\p{Cf}\p{Zl}\p{Zp}]/gu, '"''"').replace(/`/g, "'"'"'").trim().slice(0, 300))' ]; then
  ok "template cleans each hand-off line by Unicode category, then of backticks, to 300 characters"
else err "knowledge-librarian.yaml no longer cleans the hand-off as expected: $clean_line"; fi
if command -v node >/dev/null 2>&1; then
  # shellcheck disable=SC2016 # the backticks and the escapes are JavaScript's
  cleaned="$(CLEAN="$clean_line" node -e '
    const clean = eval("(l) => [l]" + process.env.CLEAN + "[0]");
    process.stdout.write(clean("a\u061c line\u00ad with\u{E0041} more\ufff9 than\u180e a\u200b `list`\u2028"));')"
  if [ "$cleaned" = "a line with more than a 'list'" ]; then
    ok "template's cleaning removes a bidirectional mark, a soft hyphen, a tag character and a line separator"
  else err "template's cleaning left something a reader cannot see: $(printf '%s' "$cleaned" | od -c | head -3)"; fi
else
  echo "node not installed locally - CI runs the hand-off's cleaning; skipping here"
fi
# The registrar's gate does not run on the pull request this workflow opens.
# So the refresh job runs the conventions script, and the pull request says
# how it ended beside the validation.
# These sections are captured first, not piped into `grep -q`: `grep -q` exits
# on its first match, and sed writing the rest of a large section into the
# closed pipe takes SIGPIPE, which `set -o pipefail` would turn into a spurious
# failure under load.
refresh_to_publish="$(sed -n '/^  refresh:/,/^  publish:/p' "$librarian_yaml")"
refresh_to_steps="$(sed -n '/^  refresh:/,/^    steps:/p' "$librarian_yaml")"
publish_to_steps="$(sed -n '/^  publish:/,/^    steps:/p' "$librarian_yaml")"
# shellcheck disable=SC2016 # the template's own ${{ }} and ${...} expressions, matched as text
if grep -qF 'run: bash scripts/knowledge-conventions.sh knowledge' <<<"$refresh_to_publish" \
   && grep -qF 'conventions_outcome: ${{ steps.conventions.outcome }}' "$librarian_yaml" \
   && grep -qF 'CONVENTIONS_OUTCOME: ${{ needs.refresh.outputs.conventions_outcome }}' "$librarian_yaml" \
   && grep -qF '${check(CONVENTIONS_OUTCOME)}' "$librarian_yaml"; then
  ok "template runs the conventions script in refresh and reports its outcome on the pull request"
else err "knowledge-librarian.yaml no longer runs the conventions script, or no longer reports it on the pull request"; fi
# A scheduled run waits its turn: the refresh job needs the job that read the
# workflow's earlier pull requests, and does not run on a schedule while one
# is open. What a person declined reaches the agent step as a file, on a
# scheduled run only. The job that reads them holds a token that can read
# pull requests, checks nothing out and runs no agent.
# shellcheck disable=SC2016 # the template's own ${{ }} expressions, matched as text
if grep -qxF '    needs: earlier' <<<"$refresh_to_steps" \
   && grep -qxF "    if: github.event_name != 'schedule' || needs.earlier.outputs.open == ''" <<<"$refresh_to_steps" \
   && grep -qxF '    needs: [earlier, refresh]' <<<"$publish_to_steps"; then
  ok "template skips a scheduled refresh while a pull request of the workflow's is open, and a run a person starts goes ahead"
else err "knowledge-librarian.yaml no longer holds a scheduled refresh back while an earlier pull request is open"; fi
# shellcheck disable=SC2016 # the template's own ${{ }} expressions, matched as text
if grep -qF 'KNOWLEDGE_DECLINED: ${{ runner.temp }}/declined.txt' "$librarian_yaml" \
   && grep -qF "if: vars.KNOWLEDGE_LIBRARIAN_ENABLED == 'true' && github.event_name == 'schedule' && needs.earlier.outputs.record != ''" "$librarian_yaml" \
   && grep -qF 'run: printf '"'"'%s\n'"'"' "$RECORD" > "$RUNNER_TEMP/declined.txt"' "$librarian_yaml"; then
  ok "template hands what a person declined to the agent step as a file, on a scheduled run only"
else err "knowledge-librarian.yaml no longer writes the declined record for a scheduled run, or no longer names it for the agent step"; fi
# shellcheck disable=SC2016 # the template's own ${{ }} expressions and JavaScript, matched as text
if grep -qF 'OPEN_PR: ${{ needs.earlier.outputs.open }}' "$librarian_yaml" && grep -qF 'DECLINED_PR: ${{ needs.earlier.outputs.declined }}' "$librarian_yaml" \
   && grep -qF "if (/^[0-9]+\$/.test(OPEN_PR || '')) {" "$librarian_yaml" && grep -qF "if (/^[0-9]+\$/.test(DECLINED_PR || '')) {" "$librarian_yaml" \
   && grep -qF "...earlier," "$librarian_yaml"; then
  ok "template names an earlier pull request in the new one by its number, and only when it is a number"
else err "knowledge-librarian.yaml no longer names the earlier pull requests in the one it opens, or shows more than a number"; fi
earlier_job="$(sed -n '/^  earlier:/,/^  refresh:/p' "$librarian_yaml")"
if grep -q '^      pull-requests: read' <<<"$earlier_job" && ! grep -qE '^      [a-z-]+: write' <<<"$earlier_job" \
   && ! grep -q 'actions/checkout\|AGENT_' <<<"$earlier_job"; then
  ok "the earlier job reads pull requests under a read-only token, checks nothing out and runs no agent"
else err "knowledge-librarian.yaml's earlier job holds more than a token that reads pull requests"; fi

# 2b. The step that reads those pull requests, extracted from the template so
# the test breaks when its lines change. `gh` is a stand-in that answers each
# API call from a file, through the real jq, so the template's own filters
# run. A pull request counts when its branch is knowledge-librarian/... in
# this repository: a fork's branch of that name does not, and neither does a
# branch whose repository is gone. One closed without merging is declined, and
# what goes on about it is its number, its day, its base commit, the concepts
# it touched or added, and a hash of each feedback entry it handled.
step="$work/earlier-step.sh"
awk '/^      - name: Read the pull requests this workflow opened$/ { on = 1 }
     on && /^        run: \|$/ { body = 1; next }
     body && /^  [a-z]/ { exit }
     body { sub(/^          /, ""); print }' "$librarian_yaml" > "$step"
if ! grep -q 'KTL_EARLIER_END' "$step" || ! bash -n "$step" 2>/dev/null; then
  err "could not extract the step that reads the earlier pull requests from knowledge-librarian.yaml"
elif ! command -v jq >/dev/null 2>&1; then
  echo "SKIP: jq is not installed - the step that reads the earlier pull requests runs its filters through it"
else
  api="$work/api"; mkdir -p "$api" "$work/stub-earlier"
  cat > "$work/stub-earlier/gh" <<'GH'
#!/usr/bin/env bash
# gh api <url> [--paginate] --jq <filter>: the canned reply for that url, through jq.
url="$2"; filter=""
while [ $# -gt 0 ]; do [ "$1" = --jq ] && filter="$2"; shift; done
case "$url" in
  *"/pulls?"*"page=1") file="$STUB_API/pulls.json" ;;
  *"/pulls?"*)         file="$STUB_API/none.json" ;;
  *"/pulls/"*"/files") n="${url%/files}"; file="$STUB_API/files-${n##*/}.json" ;;
  *) echo "unexpected call: $url" >&2; exit 1 ;;
esac
[ -f "$file" ] || file="$STUB_API/none.json"
jq -r "$filter" "$file"
GH
  chmod +x "$work/stub-earlier/gh"
  printf '[]\n' > "$api/none.json"
  # pull <number> <state> <merged_at> <closed_at> <base> <branch> <repository, as JSON>
  pull() { printf '{"number":%s,"state":"%s","merged_at":%s,"closed_at":%s,"base":{"sha":"%s"},"head":{"ref":"%s","repo":%s},"title":"a title nobody reads","body":"a body nobody reads"}' "$@"; }
  sha() { printf '%040d' "$1"; }
  ours='{"full_name":"o/r"}'
  earlier_run() {  # prints the step's exit status; its outputs go to $work/earlier.out and its log to $work/earlier.log
    local status=0
    : > "$work/earlier.out"
    ( cd "$work" && PATH="$work/stub-earlier:$PATH" GH_TOKEN=x GITHUB_REPOSITORY=o/r GITHUB_OUTPUT="$work/earlier.out" STUB_API="$api" bash "$step" > "$work/earlier.log" 2>&1 ) || status=$?
    printf '%s' "$status"
  }
  printf '[%s,%s,%s,%s,%s,%s]\n' \
    "$(pull 30 open null null "$(sha 30)" knowledge-librarian/2026-10-05-1 '{"full_name":"fork/r"}')" \
    "$(pull 29 closed null '"2026-09-29T05:10:00Z"' "$(sha 29)" knowledge-librarian/2026-09-28-9 "$ours")" \
    "$(pull 28 closed '"2026-09-22T08:00:00Z"' '"2026-09-22T08:00:00Z"' "$(sha 28)" knowledge-librarian/2026-09-21-8 "$ours")" \
    "$(pull 27 closed null '"2026-09-20T08:00:00Z"' "$(sha 27)" feature/knowledge-librarian/x "$ours")" \
    "$(pull 26 closed null '"2026-09-15T08:00:00Z"' "$(sha 26)" knowledge-librarian/2026-09-14-7 null)" \
    "$(pull 25 closed null '"2026-09-08T08:00:00Z"' "$(sha 25)" knowledge-librarian/2026-09-07-6 "$ours")" > "$api/pulls.json"
  cat > "$api/files-29.json" <<'JSON'
[{"status":"modified","filename":".lokf/knowledge/x/two.md"},
 {"status":"added","filename":".lokf/knowledge/x/new.md"},
 {"status":"removed","filename":"knowledge_bundle/x/old.md"},
 {"status":"modified","filename":".lokf/knowledge/index.md"},
 {"status":"modified","filename":".lokf/knowledge/x/index.md"},
 {"status":"modified","filename":".lokf/knowledge/log.md"},
 {"status":"modified","filename":".lokf/knowledge/x/Bad Name.md"},
 {"status":"modified","filename":".lokf/knowledge/x/../../../README.md"},
 {"status":"modified","filename":"README.md"},
 {"status":"modified","filename":".lokf/questions.md"},
 {"status":"modified","filename":".lokf/feedback.md","patch":"@@ -3,7 +3,5 @@\n \n ## 2026-01-06\n \n-- **Miss** - Q: \"a reader wrote these declined words\" - docent\n - **Miss** - Q: \"second\" - docent\n-## 2026-01-01\n"}]
JSON
  printf '[{"status":"modified","filename":".lokf/knowledge/x/five.md"}]\n' > "$api/files-25.json"
  status="$(earlier_run)"
  want="$(printf '%s\n' "declined 29 2026-09-29 $(sha 29)" 'touched x/two.md' 'added x/new.md' 'touched x/old.md' \
    "handled $(printf '%s\n' '- **Miss** - Q: "a reader wrote these declined words" - docent' | git hash-object --stdin)" \
    "declined 25 2026-09-08 $(sha 25)" 'touched x/five.md')"
  got="$(sed -n '/^record<<KTL_EARLIER_END$/,/^KTL_EARLIER_END$/p' "$work/earlier.out" | sed '1d;$d')"
  if [ "$status" = 0 ] && grep -qxF 'open=' "$work/earlier.out" && grep -qxF 'declined=29' "$work/earlier.out"; then
    ok "earlier: a fork's branch of the same name is no pull request of the workflow's, and the newest one closed without merging is the declined one"
  else err "earlier: exit $status, outputs: $(tr '\n' ' ' < "$work/earlier.out"), log: $(cat "$work/earlier.log")"; fi
  if [ "$got" = "$want" ]; then
    ok "earlier: the record holds each declined pull request's base, the concepts it touched or added, and a hash of the feedback entry it handled"
  else err "earlier: the record is not as expected: $got"; fi
  if ! grep -q 'declined words\|nobody reads' "$work/earlier.out" "$work/earlier.log"; then
    ok "earlier: no reader's words, and no pull request's title or body, leave the step"
  else err "earlier: a reader's words or a pull request's text reached the step's outputs or its log"; fi
  printf '[%s,%s]\n' \
    "$(pull 31 open null null "$(sha 31)" knowledge-librarian/2026-10-05-2 "$ours")" \
    "$(pull 28 closed '"2026-09-22T08:00:00Z"' '"2026-09-22T08:00:00Z"' "$(sha 28)" knowledge-librarian/2026-09-21-8 "$ours")" > "$api/pulls.json"
  status="$(earlier_run)"
  if [ "$status" = 0 ] && grep -qxF 'open=31' "$work/earlier.out" && grep -qxF 'declined=' "$work/earlier.out" && grep -q 'Pull request #31 from this workflow is still open' "$work/earlier.log"; then
    ok "earlier: an open pull request of the workflow's is named, and a merged one declines nothing"
  else err "earlier: exit $status with an open pull request, outputs: $(tr '\n' ' ' < "$work/earlier.out")"; fi
  printf '[]\n' > "$api/pulls.json"
  status="$(earlier_run)"
  if [ "$status" = 0 ] && grep -qxF 'open=' "$work/earlier.out" && grep -qxF 'declined=' "$work/earlier.out"; then
    ok "earlier: a repository with no pull request of the workflow's has nothing open and nothing declined"
  else err "earlier: exit $status with no pull requests, outputs: $(tr '\n' ' ' < "$work/earlier.out")"; fi
fi

# 2c. The install step, extracted from the template and run against a
# stand-in for the skills repository. The pin is a tag and the commit it
# named when it was set. The skill is installed while the two agree, and
# nothing is installed once the tag names another commit.
step="$work/install-step.sh"
awk '/^      - name: Install the pinned ktl-librarian skill$/ { on = 1 }
     on && /^        run: \|$/ { body = 1; next }
     body && /^      [#-]/ { exit }
     body { sub(/^          /, ""); print }' "$librarian_yaml" > "$step"
if ! grep -q 'TRUST_LADDER_SKILLS_SHA' "$step" || ! bash -n "$step" 2>/dev/null; then
  err "could not extract the install step from knowledge-librarian.yaml, or it no longer reads TRUST_LADDER_SKILLS_SHA"
else
  skills_repo="$work/skills-repo"
  mkdir -p "$skills_repo/skills/ktl-librarian"
  (
    cd "$skills_repo"
    git init -q -b main . && git config user.email "layout-test@example.invalid" && git config user.name "layout test"
    printf '# the skill as it was reviewed\n' > skills/ktl-librarian/SKILL.md
    git add -A && git commit -q -m "the reviewed skill" && git -c tag.gpgSign=false tag v9.9.9
  )
  pinned="$(git -C "$skills_repo" rev-parse HEAD)"
  install_run() {  # <dir to install into>: prints the step's exit status; its log goes to $work/install.log
    local status=0
    mkdir -p "$1"
    ( cd "$1" && TRUST_LADDER_SKILLS_REPO="file://$skills_repo" TRUST_LADDER_SKILLS_REF=v9.9.9 TRUST_LADDER_SKILLS_SHA="$pinned" bash "$step" > "$work/install.log" 2>&1 ) || status=$?
    printf '%s' "$status"
  }
  status="$(install_run "$work/install-ok")"
  if [ "$status" = 0 ] && grep -q 'as it was reviewed' "$work/install-ok/.agents/skills/ktl-librarian/SKILL.md" 2>/dev/null; then
    ok "install: the skill is installed from the pinned tag while it names the pinned commit (exit 0)"
  else err "install: exit $status with the tag and the commit in agreement: $(cat "$work/install.log")"; fi
  ( cd "$skills_repo" && printf '# other instructions\n' > skills/ktl-librarian/SKILL.md && git commit -q -am "the tag is moved to this" && git -c tag.gpgSign=false tag -f v9.9.9 >/dev/null )
  status="$(install_run "$work/install-moved")"
  if [ "$status" = 1 ] && [ ! -e "$work/install-moved/.agents/skills/ktl-librarian" ] && grep -q 'nothing was installed' "$work/install.log"; then
    ok "install: a tag that names another commit installs nothing, and the step says so (exit 1)"
  else err "install: exit $status after the tag moved, and the skill is $( [ -e "$work/install-moved/.agents/skills/ktl-librarian" ] && echo installed || echo absent ): $(cat "$work/install.log")"; fi
fi

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
publish_to_end="$(sed -n '/^  publish:/,$p' "$librarian_yaml")"  # captured first, against the SIGPIPE race above
for line in 'bash .lokf/scripts/knowledge-provenance.sh --unattended' 'bash .lokf/scripts/knowledge-report.sh health' 'bash .lokf/scripts/knowledge-report.sh changes'; do
  if grep -qF -- "$line" <<<"$publish_to_end"; then ok "publish runs: $line"
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
# Each template installs the toolkit from the sidecar's lock, so a gate, a
# release and a scheduled run all install the files a person reviewed.
for yaml in "$registrar_yaml" "$librarian_yaml" "$release_yaml"; do
  if grep -qxF '        run: uv sync --locked' "$yaml" && ! grep -qE '^ *run: uv sync *$' "$yaml"; then ok "${yaml##*/} installs the sidecar from its lock (uv sync --locked)"
  else err "${yaml##*/} installs the sidecar without --locked, so it takes whatever resolves on the day"; fi
done
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
# as one that is added. A person's generated record may be replaced by another
# person's, the curator's Correct, and by nothing else.
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
  # pack <host> <tag> <out dir> [TZ]: runs the template's pack lines at the tag's checkout
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
