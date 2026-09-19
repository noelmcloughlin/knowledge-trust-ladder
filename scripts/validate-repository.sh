#!/usr/bin/env bash
# Repository-contract checks for the lokf-agent-skills distribution
# repo. Separate from specification/Markdown checks (workflows/validate.yml
# runs those as their own jobs) so failures are easy to diagnose.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fail=0
say() { printf '%s\n' "$*"; }
err() { printf 'FAIL: %s\n' "$*" >&2; fail=1; }
ok() { printf 'OK:   %s\n' "$*"; }

# 1. Exactly the two intended published skill directories exist.
mapfile -t skill_dirs < <(find skills -mindepth 1 -maxdepth 1 -type d | sort)
expected_dirs=("skills/lokf-curator" "skills/lokf-docent" "skills/lokf-librarian" "skills/lokf-sidecar")
if [[ "${skill_dirs[*]}" == "${expected_dirs[*]}" ]]; then
  ok "exactly the four intended skill directories exist (${expected_dirs[*]})"
else
  err "expected skill directories ${expected_dirs[*]}, found ${skill_dirs[*]:-none}"
fi

# 2. Each required SKILL.md exists with the exact case-sensitive filename.
for dir in "${expected_dirs[@]}"; do
  if [[ -f "$dir/SKILL.md" ]]; then
    ok "$dir/SKILL.md exists"
  else
    err "$dir/SKILL.md is missing (check exact case: SKILL.md, not skill.md/Skill.md)"
  fi
done

# 3. Each declared skill name matches its parent directory.
for dir in "${expected_dirs[@]}"; do
  skill_file="$dir/SKILL.md"
  [[ -f "$skill_file" ]] || continue
  declared="$(sed -n 's/^name:[[:space:]]*//p' "$skill_file" | sed -n 1p | tr -d '"'"'"'')"
  expected="$(basename "$dir")"
  if [[ "$declared" == "$expected" ]]; then
    ok "$skill_file frontmatter name '$declared' matches directory"
  else
    err "$skill_file frontmatter name '$declared' does not match directory '$expected'"
  fi
done

# 3b. Each skill states what it needs in the spec's optional `compatibility`
#     field (agentskills.io/specification: 1-500 characters), so git, a POSIX
#     shell, uv or an authenticated identity is declared where every installer
#     shows it, not discovered after a report has offered a step. (The curator
#     used to name `gh` only inside its Step 2.)
for dir in "${expected_dirs[@]}"; do
  skill_file="$dir/SKILL.md"
  [[ -f "$skill_file" ]] || continue
  compat="$(awk 'NR>1 && /^---$/ {exit} /^compatibility:/ {sub(/^compatibility:[[:space:]]*/, ""); print}' "$skill_file")"
  if [[ -z "$compat" ]]; then
    err "$skill_file declares no compatibility field - say what the skill needs (shell, git, uv, an identity) in 1-500 characters"
  elif (( ${#compat} > 500 )); then
    err "$skill_file compatibility is ${#compat} characters; the Agent Skills spec allows 500"
  else
    ok "$skill_file declares compatibility (${#compat} characters)"
  fi
done

# 4. No unexpected duplicate SKILL.md files in publishable paths.
mapfile -t all_skill_md < <(find skills -iname 'SKILL.md' | sort)
if [[ ${#all_skill_md[@]} -eq 4 ]]; then
  ok "no duplicate SKILL.md files under skills/"
else
  err "expected exactly 4 SKILL.md files under skills/, found ${#all_skill_md[@]}: ${all_skill_md[*]}"
fi

# 5. Relative references remain valid after the complete skill directory is
#    copied (i.e. resolved from each linking file's own directory - this is
#    exactly how an installer copies one skill/ subtree at a time).
say ""
say "Checking relative link targets..."
broken=0
while IFS= read -r file; do
  # Blank out fenced code blocks first (keeping line numbers stable): example
  # links inside ``` fences are documentation of syntax, not real links.
  while IFS=: read -r line match; do
    link="${match#\](}"
    link="${link%)}"
    # Skip absolute URLs and in-page anchors.
    [[ "$link" =~ ^https?:// ]] && continue
    [[ "$link" =~ ^# ]] && continue
    link="${link%%#*}"
    [[ -z "$link" ]] && continue
    target="$(dirname "$file")/$link"
    if [[ ! -e "$target" ]]; then
      err "$file:$line: broken relative link '$link' (resolved: $target)"
      broken=1
    fi
  done < <(awk 'BEGIN{f=0} /^[[:space:]]*```/{f=!f; print ""; next} {print (f ? "" : $0)}' "$file" \
             | grep -noE '\]\(([^)]+)\)' || true)
done < <(find skills -name '*.md' | sort)
[[ "$broken" -eq 0 ]] && ok "all relative Markdown links under skills/ resolve (fenced examples ignored)"
[[ "$broken" -eq 1 ]] && fail=1

# 6. Executable scripts pass language-specific linting.
say ""
say "Linting executable scripts..."
mapfile -t scripts < <(find skills scripts -type f -name '*.sh' | sort)
if command -v shellcheck >/dev/null 2>&1; then
  for s in "${scripts[@]}"; do
    if shellcheck "$s"; then
      ok "shellcheck clean: $s"
    else
      err "shellcheck failed: $s"
    fi
  done
else
  say "shellcheck not installed locally - CI runs it; skipping here (${#scripts[@]} script(s) found: ${scripts[*]:-none})"
fi

# 7. The LOKF class vocabulary is enumerated as prose in two files, with no
#    generator behind it. Rule 3 in lokf-librarian/SKILL.md is the canonical
#    list; the other enumeration, and any count a page still states, must
#    agree with it. Prose elsewhere says "small" rather than a number: the
#    count is the schema's to change, not this repository's.
#    (On 2026-09-14 Rule 3 said fourteen and omitted Role while README.md and
#    docs/for-the-curious.md said fifteen - undetected until a person read
#    both. This check is why that cannot happen twice.)
rule3_line="$(grep -m1 '^3\. \*\*Use a class from the LOKF type vocabulary' skills/lokf-librarian/SKILL.md || true)"
if [[ -z "$rule3_line" ]]; then
  err "could not find Rule 3's class list in skills/lokf-librarian/SKILL.md"
else
  # The list ends where the domain-schema sentence begins; that sentence names
  # `Concept` and a sample parent class, neither of which is part of the list.
  rule3_list="${rule3_line%%\*\*A host may have extended*}"
  # shellcheck disable=SC2016 # literal backticks for grep to match (markdown
  # code spans around a class name), not a command substitution - double
  # quotes here would make the shell try to run `[A-Z][A-Za-z]*` as a command.
  canonical="$(printf '%s' "$rule3_list" | grep -o '`[A-Z][A-Za-z]*`' | tr -d '`' | grep -vx 'Concept' | sort -u)"
  canonical_count="$(printf '%s\n' "$canonical" | grep -c .)"
  ok "Rule 3 names $canonical_count classes"

  # 7a. The curator's trust-fields.md carries the other complete enumeration.
  tf_line="$(grep -m1 '^- \*\*The 15 classes\*\*\|^- \*\*The [a-z]* classes\*\*' skills/lokf-curator/references/trust-fields.md || true)"
  if [[ -z "$tf_line" ]]; then
    err "could not find the class enumeration in lokf-curator/references/trust-fields.md"
  else
    # shellcheck disable=SC2016 # same literal-backtick grep pattern as above.
    tf_classes="$(printf '%s' "$tf_line" | grep -o '`[A-Z][A-Za-z]*`' | tr -d '`' | sort -u)"
    if [[ "$tf_classes" == "$canonical" ]]; then
      ok "trust-fields.md enumerates the same classes as Rule 3"
    else
      err "trust-fields.md and Rule 3 disagree: $(comm -3 <(printf '%s\n' "$canonical") <(printf '%s\n' "$tf_classes") | tr -d '\t' | tr '\n' ' ')"
    fi
  fi

  # 7b. Every stated count, in digits or words, must equal that number.
  declare -A word_for=([14]=fourteen [15]=fifteen [16]=sixteen [17]=seventeen)
  expected_word="${word_for[$canonical_count]:-}"
  bad_counts=0
  while IFS= read -r hit; do
    file="${hit%%:*}"
    stated="$(printf '%s' "${hit#*:}" | grep -oiE '([0-9]+|fourteen|fifteen|sixteen|seventeen)([ -](concept[ -])?class)' | grep -oiE '^[0-9]+|^fourteen|^fifteen|^sixteen|^seventeen' | head -1)"
    [[ -z "$stated" ]] && continue
    shopt -s nocasematch
    if [[ "$stated" != "$canonical_count" && "$stated" != "$expected_word" ]]; then
      err "$file states \"$stated classes\"; Rule 3 names $canonical_count"
      bad_counts=1
    fi
    shopt -u nocasematch
  done < <(grep -rniE '([0-9]+|fourteen|fifteen|sixteen|seventeen)[ -](concept[ -])?class(es)?' \
             README.md docs skills --include='*.md' || true)
  [[ "$bad_counts" -eq 0 ]] && ok "every stated class count agrees with Rule 3 ($canonical_count)"
fi

# 8. Every template that scopes a diff to the bundle (the wrapper and both
#    workflows) behaves as documented with and without the doorway link, and
#    the lokf-link recipe creates it.
say ""
say "Running the layout tests..."
if bash scripts/test-sidecar-layouts.sh; then
  ok "layout tests pass"
else
  err "layout tests failed"
fi

# 9. Three sibling repositories deep-link into files here by URL
#    (github.com/noelmcloughlin/lokf-agent-skills/blob/main/<path>), and their
#    link checks follow those for real. Moving or renaming one of these paths
#    passes every check in this repo and breaks the build in obsidian-lokf-
#    curator, and obsidian-lokf-registrar - (The mirror image happened on
#    2026-09-14: the curator referenced domain-schema.md while it was still on
#    a branch here, and its build 404'd until this side landed. CONTRIBUTING.md
#    carries the ordering rule; this check carries the paths.)
say ""
say "Checking the paths sibling repositories link into..."
sibling_paths=(
  "AI_COVENANT.md"
  "SECURITY.md"
  ".lokf/knowledge/playbooks/open-bundle-in-obsidian.md"
  "docs/releasing.md"
  "docs/signing-commits.md"
  "docs/threat-model.md"
  "docs/three-lines.md"
  "skills/lokf-librarian/references/domain-schema.md"
)
for p in "${sibling_paths[@]}"; do
  if [[ -e "$p" ]]; then
    ok "sibling-linked path exists: $p"
  else
    err "sibling-linked path is gone: $p - obsidian-lokf-curator, and obsidian-lokf-registrar link to it by URL; restore it, or update their links in the same change"
  fi
done

# 9a. When the siblings are cloned beside this repo, confirm the list above is
#     still complete: a sibling that adds a deep link should record the path
#     here in the same breath, or the check silently stops covering it. CI has
#     no siblings checked out, so this half only runs locally - the recorded
#     list is the contract either way.
mapfile -t cloned < <(for s in obsidian-lokf-curator obsidian-lokf-registrar; do
  [[ -d "../$s/.git" ]] && printf '%s\n' "../$s"
done || true)
if [[ ${#cloned[@]} -eq 0 ]]; then
  say "      (no sibling clones beside this repo - skipping the completeness cross-check)"
else
  # Each sibling installs these skills under .agents/skills (with .claude/skills
  # symlinked to it), so those trees are copies of this repository - their
  # self-links are not a sibling depending on us, and counting them reports
  # every page the skills link to internally. Skip them, and .venv, which is
  # only slow. (git-aware greps hide these via .gitignore; plain grep does not.)
  mapfile -t linked < <(grep -rhoE 'https://github\.com/noelmcloughlin/lokf-agent-skills/blob/main/[^)"#[:space:]]+' \
    "${cloned[@]}" --include='*.md' --include='*.yaml' --include='justfile' \
    --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=.agents \
    --exclude-dir=.claude --exclude-dir=.venv 2>/dev/null \
    | sed 's|.*/blob/main/||; s/[.,]$//' | sort -u || true)
  unrecorded=0
  for l in "${linked[@]}"; do
    found=0
    for p in "${sibling_paths[@]}"; do
      [[ "$l" == "$p" ]] && { found=1; break; }
    done
    if [[ "$found" -eq 0 ]]; then
      err "a sibling links to '$l', which check 9's list does not record - add it there"
      unrecorded=1
    fi
  done
  [[ "$unrecorded" -eq 0 ]] && ok "every path the ${#cloned[@]} cloned sibling(s) link to is recorded here (${#linked[@]} target(s))"
fi

# 10. CONTRIBUTING.md is a checklist, not a design log, and SECURITY.md is a
#     policy, not a threat model: each rule or surface is a line or two that
#     links to where its reasoning lives - a code comment, a workflow header,
#     a page under docs/. A word budget is the one signal every contributor,
#     person or agent, reliably reads. CONTRIBUTING sits between 700 and 850
#     across the three repositories and 1000 is where one has started to
#     become a design log again; SECURITY sits between 450 and 800 and was
#     1,400 to 1,900 before docs/threat-model.md took the design, so 900
#     is its line. The siblings hold the same budgets from their own checks.
say ""
say "Checking CONTRIBUTING.md and SECURITY.md stay short..."
for spec in "CONTRIBUTING.md:1000:a checklist" "SECURITY.md:900:a policy"; do
  IFS=: read -r file budget kind <<< "$spec"
  words="$(wc -w < "$file")"
  if (( words <= budget )); then
    ok "$file is $words words (budget $budget)"
  else
    err "$file is $words words; the budget is $budget - it is $kind, so move the reasoning next to the code or workflow it explains, or into docs/, and link to it"
  fi
done

# 11. This repository dogfoods its own sidecar templates, and CI lints the
#     copies under .github/ and .lokf/scripts/ rather than the templates
#     themselves (actionlint is pointed at both, ShellCheck scans the tree),
#     so the copies must stay byte-identical or a template change ships
#     unlinted. knowledge-librarian.yaml is the one deliberate exception: the
#     repository that publishes the skill does not install it from itself.
#     Then the conventions script itself is exercised: it must pass on this
#     repository's own bundle and fail on a bundle that breaks each rule -
#     a checker that cannot fail is not covering anything.
say ""
say "Checking the sidecar templates are the copies CI lints..."
templates="skills/lokf-sidecar/templates"
for pair in \
  "$templates/github/knowledge-registrar.yaml:.github/workflows/knowledge-registrar.yaml" \
  "$templates/scripts/knowledge-librarian.sh:.lokf/scripts/knowledge-librarian.sh" \
  "$templates/scripts/knowledge-conventions.sh:.lokf/scripts/knowledge-conventions.sh" \
  "$templates/scripts/knowledge-conventions.py:.lokf/scripts/knowledge-conventions.py" \
  "$templates/scripts/knowledge-preflight.sh:.lokf/scripts/knowledge-preflight.sh" \
  "$templates/scripts/knowledge-provenance.sh:.lokf/scripts/knowledge-provenance.sh" \
  "$templates/gitattributes:.lokf/.gitattributes"; do
  src="${pair%%:*}"; dst="${pair##*:}"
  if cmp -s "$src" "$dst"; then
    ok "$dst matches its template"
  else
    err "$dst differs from $src - this repository dogfoods its own sidecar, so the two must match: copy the template over the workflow after editing the template, or the workflow over the template after a Dependabot action bump, which only ever edits .github/workflows/"
  fi
done

say ""
say "Exercising knowledge-conventions.sh..."
# Six of the ten rules run through `uv run`, so without uv the script reports
# none of them and every expectation below fails saying only that it "failed
# to report" something - never why. Name the cause once, up front: a job that
# runs this contract installs uv (validate.yml and publish.yml both do).
if ! command -v uv >/dev/null 2>&1; then
  err "uv is not on PATH, so rules 2, 3, 4, 7, 9 and 10 cannot run and every expectation for them below will fail - install uv, or add the setup-uv step to the workflow running this"
fi
if (cd .lokf && bash scripts/knowledge-conventions.sh knowledge >/dev/null); then
  ok "this repository's bundle keeps the conventions"
else
  err "this repository's bundle breaks a convention knowledge-conventions.sh checks - run it from .lokf/ to see which"
fi
bad="$(mktemp -d)"
mkdir -p "$bad/k/x"
# A suffixed heading, then two bare dates in ascending order: one finding each.
printf '# Change Log\n\n## 2026-09-14 (2)\n\n* **A**: b.\n\n## 2026-09-13\n\n* **C**: d.\n\n## 2026-09-15\n\n* **E**: f.\n' > "$bad/k/log.md"
printf -- '---\ntype: Service\nverified:\n  by: process:lokf-librarian\n  at: 2026-09-14T00:00:00Z\n---\n\n## Open questions\n\n- unclear (process:lokf-librarian, 2026-09-12)\n' > "$bad/k/x/a.md"
printf -- '---\ntype: Service\nverified:\n  - by: process:lokf-librarian\n    at: "2026-09-13T00:00:00Z"\n  - by: process:lokf-librarian\n    at: "2026-09-14T00:00:00Z"\n---\n' > "$bad/k/x/b.md"
# A local resource that does not exist (a URL would be skipped, never fetched).
printf -- '---\ntype: Service\nresource: no-such-file.md\n---\n' > "$bad/k/x/c.md"
# A commit-shaped `revision` must name a commit holding the resource: make the
# temp directory a repository with one committed file, pin d.md to a commit
# that does not exist and e.md to the one that does. Only d.md may be reported.
# The user's git config stays out of it, so no signing key or hook is involved.
tmpgit=(env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null git -C "$bad"
  -c init.defaultBranch=main -c user.name=contract -c user.email=contract@example.invalid
  -c commit.gpgsign=false)
"${tmpgit[@]}" init -q
printf 'pinned\n' > "$bad/pinned.md"
"${tmpgit[@]}" add pinned.md
"${tmpgit[@]}" commit -q -m pin
real="$("${tmpgit[@]}" rev-parse HEAD)"
pinned() { printf -- '---\ntype: Service\nresource: pinned.md\nverified:\n  - by: human:contract\n    at: "2026-09-17T00:00:00Z"\n    revision: "%s"\n---\n' "$1"; }
pinned "0000000000000000000000000000000000000000" > "$bad/k/x/d.md"
pinned "$real" > "$bad/k/x/e.md"
# Rules 7-9 and the line-ending tolerance. A CRLF copy of a file that breaks
# rule 2 must still be reported (a Windows checkout used to make the script
# skip every frontmatter rule unread); a byte order mark and a file with no
# frontmatter are findings; a sync client's conflict copy shares its
# original's id and has a name no slug would; a directory whose case differs
# is a path-shape finding.
printf -- '---\r\ntype: Service\r\nverified:\r\n  - by: process:lokf-librarian\r\n    at: 2026-09-14T00:00:00Z\r\n---\r\n' > "$bad/k/x/f-crlf.md"
printf '\357\273\277---\ntype: Service\n---\n' > "$bad/k/x/g-bom.md"
printf 'type: Service\n' > "$bad/k/x/h-nofm.md"
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/i\n---\n' > "$bad/k/x/i.md"
cp "$bad/k/x/i.md" "$bad/k/x/i (conflicted copy 2026-09-17).md"
mkdir -p "$bad/k/Upper" && printf -- '---\ntype: Service\n---\n' > "$bad/k/Upper/j.md"
# Rule 10: an event spelt so that the gates' line readers cannot see it.
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/q\nverified:\n  - "by": human:contract\n    at: "2026-09-17T00:00:00Z"\n---\n' > "$bad/k/x/q-quotedkey.md"
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/t\nverified: [{ by: !!str human:contract, at: "2026-09-17T00:00:00Z" }]\n---\n' > "$bad/k/x/t-tag.md"
# What only a parser sees: a multi-line flow item with an unquoted `at`, a
# number where a timestamp should be, a block that does not parse (reported
# on one line), and a block that is a list rather than a mapping. And what a
# parser must not see: a second librarian event inside a body code fence.
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/fl\nverified: [\n  { by: process:lokf-librarian,\n    at: 2026-09-14T00:00:00Z }\n]\n---\n' > "$bad/k/x/fl-flow.md"
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/n\nverified:\n  - by: process:lokf-librarian\n    at: 20260914\n---\n' > "$bad/k/x/n-int.md"
printf -- '---\ntype: Service\nverified: [unclosed\n---\n' > "$bad/k/x/y-bad.md"
printf -- '---\n- just a list\n---\n' > "$bad/k/x/l-list.md"
# shellcheck disable=SC2016 # the backticks are a Markdown code fence, not a command
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/fence\nverified:\n  - by: process:lokf-librarian\n    at: "2026-09-14T00:00:00Z"\n---\n\n```yaml\nverified:\n  - by: process:lokf-librarian\n    at: "2026-09-15T00:00:00Z"\n```\n' > "$bad/k/x/fence.md"
findings="$(bash "$templates/scripts/knowledge-conventions.sh" "$bad/k" 2>&1 || true)"
rm -rf "$bad"
for want in "not a bare ISO date" "not newest-first" "x/a.md: unquoted timestamp" "bare mapping" "open question not" "2 process:lokf-librarian events" "resource not found" "does not hold" \
            "f-crlf.md: unquoted timestamp" "g-bom.md: starts with a byte order mark" "h-nofm.md: no closed frontmatter block" \
            "is declared by more than one file" "conflicted copy 2026-09-17).md: path is not lowercase" "Upper/j.md: path is not lowercase" \
            "q-quotedkey.md: frontmatter uses a quoted key (by)" "t-tag.md: frontmatter uses a tag on" \
            "fl-flow.md: unquoted timestamp" "n-int.md: unquoted timestamp" "y-bad.md: frontmatter is not valid YAML" "l-list.md: frontmatter is not a mapping"; do
  if grep -q "$want" <<<"$findings"; then
    ok "conventions script reports: $want"
  else
    err "conventions script failed to report '$want' on a bundle that breaks it"
  fi
done
for quiet in "x/e.md:whose revision holds its resource" "fence.md:whose second librarian event is only an example in a code fence"; do
  if grep -q "${quiet%%:*}" <<<"$findings"; then
    err "conventions script reported ${quiet%%:*}, ${quiet#*:}"
  else
    ok "conventions script accepts ${quiet%%:*}, ${quiet#*:}"
  fi
done
if [[ "$(grep -c 'y-bad.md' <<<"$findings")" -eq 1 ]]; then
  ok "conventions script reports a YAML parse error on one line"
else
  err "conventions script spread a YAML parse error over several lines: $(grep 'y-bad.md' <<<"$findings")"
fi
# And a bundle that keeps every convention but was checked out with CRLF line
# endings must pass outright: the script reads it exactly as CI reads LF. A
# folded description is fine: rule 10 reads only the fields the gates read.
good="$(mktemp -d)"
mkdir -p "$good/k/x"
printf '# Change Log\r\n\r\n## 2026-09-15\r\n\r\n* **A**: b.\r\n\r\n## 2026-09-14\r\n\r\n* **C**: d.\r\n' > "$good/k/log.md"
printf -- '---\r\ntype: Service\r\nid: https://example.invalid/k/x/a\r\ndescription: >-\r\n  folded, which the gates\r\n  never read\r\nverified:\r\n  - by: process:lokf-librarian\r\n    at: "2026-09-14T00:00:00Z"\r\n---\r\n\r\n## Open questions\r\n\r\n- 2026-09-14, process:lokf-librarian: fine\r\n' > "$good/k/x/a.md"
if out="$(bash "$templates/scripts/knowledge-conventions.sh" "$good/k" 2>&1)"; then
  ok "conventions script reads a CRLF checkout as CI reads LF"
else
  err "conventions script misreads a CRLF checkout: $out"
fi
# Without uv the shell half still runs, and its OK line says what it skipped.
if PATH=/usr/bin:/bin command -v uv >/dev/null 2>&1; then
  say "uv is on /usr/bin - the without-uv case cannot be staged here"
elif out="$(PATH=/usr/bin:/bin bash "$templates/scripts/knowledge-conventions.sh" "$good/k" 2>/dev/null)" && grep -q '^OK - .*(rules 2, 3, 4, 7, 9 and 10 not checked: uv not found)' <<<"$out"; then
  ok "conventions script without uv passes on its own rules and says which it skipped"
else
  err "conventions script without uv did not say what it skipped: $out"
fi
# A bundle reached through a link - the rearranged layout the sidecar's
# portability page allows - must be read, not passed with zero files seen.
ln -s "$good/k" "$good/linked" && printf 'x' > "$good/k/x/Bad.md"
if out="$(bash "$templates/scripts/knowledge-conventions.sh" "$good/linked" 2>&1)"; then
  err "conventions script passed a linked bundle unread: $out"
elif grep -q 'Bad.md: path is not lowercase' <<<"$out"; then
  ok "conventions script reads a bundle reached through a link"
else
  err "conventions script misread a linked bundle: $out"
fi
rm -rf "$good"

# 12. The preflight script every skill runs first must always end on its
#     summary line and exit 0 - on this repository, and on a bare directory
#     with no bundle, no git and no skills, where every section has to cope
#     with absence rather than fail. A CRLF file must raise its warning.
say ""
say "Exercising knowledge-preflight.sh..."
if out="$(bash "$templates/scripts/knowledge-preflight.sh" . 2>&1)" && grep -q '^Preflight: ' <<<"$out"; then
  ok "preflight runs on this repository and ends on its summary line"
else
  err "preflight failed on this repository: $out"
fi
bare="$(mktemp -d)"
if out="$(cd "$bare" && bash "$repo_root/$templates/scripts/knowledge-preflight.sh" 2>&1)" \
   && grep -q '^missing bundle' <<<"$out" && grep -q '^info    git ' <<<"$out" && grep -q '^Preflight: ' <<<"$out"; then
  ok "preflight copes with a bare directory (no bundle, no git, no skills)"
else
  err "preflight misbehaves on a bare directory: $out"
fi
mkdir -p "$bare/.lokf/knowledge/x" && printf -- '---\r\ntype: Service\r\n---\r\n' > "$bare/.lokf/knowledge/x/a.md"
if out="$(bash "$templates/scripts/knowledge-preflight.sh" "$bare" 2>&1)" && grep -q '^warn    endings .*CRLF' <<<"$out"; then
  ok "preflight warns about CRLF files in the bundle"
else
  err "preflight did not warn about a CRLF file: $out"
fi
# The same bundle behind a link is still counted; `commit.gpgsign = yes` is
# signing on, with no user.signingkey meaning git's default key; and a run
# under sh stops on one line naming bash rather than mid-screen.
mv "$bare/.lokf/knowledge" "$bare/knowledge_bundle" && ln -s ../knowledge_bundle "$bare/.lokf/knowledge"
if out="$(bash "$templates/scripts/knowledge-preflight.sh" "$bare" 2>&1)" && grep -q '^ok      bundle .*, 1 concepts' <<<"$out"; then
  ok "preflight counts a bundle reached through a link"
else
  err "preflight did not read a linked bundle: $out"
fi
git init -q "$bare" && git -C "$bare" -c user.name=c -c user.email=c@example.invalid commit -q --allow-empty --no-gpg-sign -m x \
  && git -C "$bare" config commit.gpgsign yes
if out="$(GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null bash "$templates/scripts/knowledge-preflight.sh" "$bare" 2>&1)" && grep -q '^ok      signing .*by committer email' <<<"$out"; then
  ok "preflight reads commit.gpgsign = yes with no signing key as signing on"
else
  err "preflight misread commit.gpgsign = yes: $out"
fi
# A host holding the conventions script without its Python half has a gate
# that fails outright; the preflight says so even with no sidecar installed.
mkdir -p "$bare/.lokf/scripts" && cp "$templates/scripts/knowledge-conventions.sh" "$bare/.lokf/scripts/"
if out="$(bash "$templates/scripts/knowledge-preflight.sh" "$bare" 2>&1)" && grep -q '^warn    copies .*knowledge-conventions.py missing' <<<"$out"; then
  ok "preflight warns when knowledge-conventions.py is missing beside the .sh"
else
  err "preflight did not report the missing knowledge-conventions.py: $out"
fi
rm -rf "$bare"
# Every line the preflight can print as missing or a warning has a row on the
# sidecar's prerequisites page - the plain-words meaning, who fixes it and
# what to send them - so a new preflight line cannot land without one.
prereq="skills/lokf-sidecar/references/prerequisites.md"
while IFS= read -r key; do
  if grep -q "^| \`$key\` |" "$prereq"; then
    ok "prerequisites.md explains the preflight's '$key' line"
  else
    err "prerequisites.md has no row for the preflight's '$key' line - add what it means, who fixes it and what to send them"
  fi
done < <(grep -oE '\b(miss|warn) [a-z]+' "$templates/scripts/knowledge-preflight.sh" | awk '{print $2}' | sort -u)
for s in knowledge-preflight.sh knowledge-conventions.sh knowledge-provenance.sh; do
  if out="$(sh "$templates/scripts/$s" x 2>&1)"; then
    err "$s run under sh did not stop: $out"
  elif grep -q '^run this with bash' <<<"$out"; then
    ok "$s run under sh stops and names bash"
  else
    err "$s run under sh failed some other way: $out"
  fi
done

# 13. The forge-free provenance gate, with throwaway keys: a confirmation
#     signed by the curator on file passes - with a GPG primary key, a GPG
#     signing subkey, or an SSH key; an unsigned one, one by an id with no
#     key, one by another key, and one whose own key lands in the same range
#     each fail, while another curator's key landing alongside does not; a
#     repository with no .lokf/curators/ is a stated skip. Needs gpg and
#     ssh-keygen, which CI has.
say ""
say "Exercising knowledge-provenance.sh..."
if command -v gpg >/dev/null 2>&1 && command -v ssh-keygen >/dev/null 2>&1; then
  pv="$(mktemp -d)"
  mkdir -m 700 "$pv/gnupg"
  script="$repo_root/$templates/scripts/knowledge-provenance.sh"
  confirmed() { printf -- '---\ntype: Service\nverified:\n  - by: human:%s\n    at: "2026-09-17T00:00:00Z"\n---\n' "$1"; }
  pv_git() { (cd "$pv/repo" && GNUPGHOME="$pv/gnupg" GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null git "$@"); }
  pv_gpg() { GNUPGHOME="$pv/gnupg" gpg --batch --quiet "$@"; }
  # Each case: the range to check, the exit status expected, the line expected, and the verdict wording.
  # The keyring is read from the working tree, so each case runs as soon as its commit exists.
  expect_pv() {
    local range="$1" status="$2" want="$3" what="$4" out rc=0
    # shellcheck disable=SC2086 # $range is one or two refs on purpose
    out="$(cd "$pv/repo" && GNUPGHOME="$pv/gnupg" bash "$script" $range 2>&1)" || rc=$?
    if [[ "$rc" -eq "$status" ]] && grep -q "$want" <<<"$out"; then
      ok "provenance script: $what"
    else
      err "provenance script did not $what (exit $rc): $out"
    fi
  }
  k="$pv/repo/.lokf/knowledge/x"; c="$pv/repo/.lokf/curators"
  if pv_gpg --pinentry-mode loopback --passphrase '' --quick-generate-key 'contract <contract@example.invalid>' ed25519 sign 1d 2>/dev/null \
     && pv_gpg --pinentry-mode loopback --passphrase '' --quick-generate-key 'other <other@example.invalid>' ed25519 sign 1d 2>/dev/null \
     && pv_gpg --pinentry-mode loopback --passphrase '' --quick-generate-key 'sub <sub@example.invalid>' ed25519 cert 1d 2>/dev/null \
     && ssh-keygen -q -t ed25519 -N '' -C sshcur -f "$pv/sshcur" && ssh-keygen -q -t ed25519 -N '' -C stranger -f "$pv/stranger"; then
    # Read gpg's output whole: an awk that exits on the first match closes the
    # pipe early, which a runner that ignores SIGPIPE reports as a write error.
    fpr="$(pv_gpg --with-colons --list-keys contract | awk -F: '$1=="fpr" && !f {print $10; f=1}')"
    fpr2="$(pv_gpg --with-colons --list-keys other | awk -F: '$1=="fpr" && !f {print $10; f=1}')"
    fpr3="$(pv_gpg --with-colons --list-keys sub@example.invalid | awk -F: '$1=="fpr" && !f {print $10; f=1}')"
    # The third key certifies only and signs with a subkey, the common layout.
    pv_gpg --pinentry-mode loopback --passphrase '' --quick-add-key "$fpr3" ed25519 sign 1d 2>/dev/null
    git init -q "$pv/repo"
    pv_git config user.name contract && pv_git config user.email contract@example.invalid
    pv_git config gpg.format openpgp && pv_git config user.signingkey "$fpr"
    mkdir -p "$k" "$c"
    pv_gpg --armor --export "$fpr" > "$c/contract.asc"
    printf -- '---\ntype: Service\n---\n' > "$k/a.md"
    pv_git add -A && pv_git commit -q --no-gpg-sign -m base
    confirmed contract > "$k/a.md" && pv_git commit -q -S -am confirm
    expect_pv "HEAD~1" 0 '^OK - 1 confirmation' "pass a confirmation signed by the curator on file"
    # A confirmation is the whole event, not its `by:` line: re-dating an
    # existing one, in a flow-style layout or a block one, is a claim by that
    # curator; moving the concept is not, since events are keyed by its id.
    sed -i 's/2026-09-17T00:00:00Z/2026-09-18T00:00:00Z/' "$k/a.md" && pv_git commit -q --no-gpg-sign -am 'redated, unsigned'
    expect_pv "HEAD~1" 1 'is unsigned' "report a re-dated confirmation nobody signed"
    sed -i 's/2026-09-18T00:00:00Z/2026-09-19T00:00:00Z/' "$k/a.md" && pv_git commit -q -S -am 'redated by its curator'
    expect_pv "HEAD~1" 0 '^OK - 1 confirmation' "pass a re-dated confirmation its curator signed"
    printf -- '---\ntype: Service\nid: https://example.invalid/k/x/flow\nverified: [{ by: human:contract, at: "2026-09-17T00:00:00Z" }]\n---\n' > "$k/flow.md" && pv_git add -A && pv_git commit -q --no-gpg-sign -m 'flow style, unsigned'
    expect_pv "HEAD~1" 1 'is unsigned' "see a flow-style event that leaves no by: line in the diff"
    pv_git mv "$k/flow.md" "$k/moved.md" && pv_git commit -q --no-gpg-sign -m 'moved, unsigned'
    expect_pv "HEAD~1" 0 '^OK - 0 confirmation' "let a confirmed concept move under its id without a new claim"
    confirmed contract > "$k/b.md" && pv_git add -A && pv_git commit -q --no-gpg-sign -m unsigned
    expect_pv "HEAD~1" 1 'is unsigned' "report an unsigned confirmation"
    confirmed nobody > "$k/c.md" && pv_git add -A && pv_git commit -q -S -m nobody
    expect_pv "HEAD~1" 1 'no key on file' "report an id with no key on file"
    confirmed '../odd' > "$k/c2.md" && pv_git add -A && pv_git commit -q --no-gpg-sign -m 'odd id'
    expect_pv "HEAD~1" 1 'not a login this gate can check' "refuse an id it cannot look up rather than skip it"
    confirmed contract > "$k/d.md" && pv_git add -A && pv_git -c user.signingkey="$fpr2" commit -q -S -m wrongkey
    expect_pv "HEAD~1" 1 'signed by another key' "report a confirmation signed by a key that is not that curator's"
    pv_gpg --armor --export "$fpr2" > "$c/other.asc" && confirmed other > "$k/e.md" && pv_git add -A && pv_git -c user.signingkey="$fpr2" commit -q -S -m 'key and own confirmation'
    expect_pv "HEAD~1" 1 'same range' "refuse a curator's own key and their confirmation in one range"
    confirmed other > "$k/f.md" && pv_git add -A && pv_git -c user.signingkey="$fpr2" commit -q -S -m 'confirm after the key landed'
    expect_pv "HEAD~1" 0 '^OK - 1 confirmation' "pass a confirmation once that key landed in an earlier range"
    pv_gpg --armor --export "$fpr3" > "$c/sub.asc" && pv_git add -A && pv_git commit -q -S -m 'subkey curator'
    confirmed sub > "$k/g.md" && pv_git add -A && pv_git -c user.signingkey="$fpr3" commit -q -S -m 'signed with the subkey'
    expect_pv "HEAD~1" 0 '^OK - 1 confirmation' "accept a signature made with a GPG signing subkey"
    cp "$pv/sshcur.pub" "$c/sshcur.pub" && pv_git add -A && pv_git commit -q -S -m 'ssh curator'
    confirmed sshcur > "$k/h.md" && pv_git add -A && pv_git -c gpg.format=ssh -c user.signingkey="$pv/sshcur.pub" commit -q -S -m 'ssh signed'
    expect_pv "HEAD~1" 0 '^OK - 1 confirmation' "accept an SSH signature by the key on file"
    confirmed sshcur > "$k/i.md" && pv_git add -A && pv_git -c gpg.format=ssh -c user.signingkey="$pv/stranger.pub" commit -q -S -m 'ssh by a stranger'
    expect_pv "HEAD~1" 1 'not by a key in sshcur.pub' "report an SSH signature by a key not on file for that id"
    cp "$pv/stranger.pub" "$c/stranger.pub" && confirmed contract > "$k/j.md" && pv_git add -A && pv_git commit -q -S -m 'another key lands beside a confirmation'
    expect_pv "HEAD~1" 0 '^OK - 1 confirmation' "let another curator's key land beside a confirmation"
    # Only the frontmatter is a claim: an example event in a body code fence
    # is not, and a human `generated` record - the curator's Correct writes
    # one - is, whatever its layout.
    # shellcheck disable=SC2016 # the backticks are a Markdown code fence, not a command
    printf -- '---\ntype: Service\nid: https://example.invalid/k/x/fence\n---\n\n```yaml\nverified:\n  - by: human:contract\n    at: "2026-09-17T00:00:00Z"\n```\n' > "$k/fence.md" && pv_git add -A && pv_git commit -q --no-gpg-sign -m 'example in a fence, unsigned'
    expect_pv "HEAD~1" 0 '^OK - 0 confirmation' "ignore an example event in a body code fence"
    printf -- '---\ntype: Service\nid: https://example.invalid/k/x/gen\ngenerated: { by: human:contract, at: "2026-09-17T00:00:00Z" }\n---\n' > "$k/gen.md" && pv_git add -A && pv_git commit -q --no-gpg-sign -m 'human generated, flow style, unsigned'
    expect_pv "HEAD~1" 1 'is unsigned' "read a flow-style human generated record as a claim"
    # Names git would quote by default: a byte above 0x7f is read like any
    # other concept; a double quote is refused. Neither is silently dropped.
    confirmed contract > "$k/café.md" && pv_git add -A && pv_git commit -q -S -m 'utf-8 name, signed'
    expect_pv "HEAD~1" 0 '^OK - 1 confirmation' "read a concept whose name holds a byte above 0x7f"
    confirmed contract > "$k/qu\"ote.md" && pv_git add -A && pv_git commit -q --no-gpg-sign -m 'quoted name, unsigned'
    expect_pv "HEAD~1" 1 'cannot read' "refuse a concept path git has to quote rather than pass it unread"
    # A merge that brings in a confirmation its curator signed claims nothing;
    # one that adds an event neither side held is a claim by whoever merged.
    trunk="$(pv_git rev-parse --abbrev-ref HEAD)"
    pv_git checkout -q -b side && printf 'side\n' > "$pv/repo/side.txt" && pv_git add -A && pv_git commit -q --no-gpg-sign -m 'side work'
    pv_git checkout -q "$trunk" && confirmed contract > "$k/m.md" && pv_git add -A && pv_git commit -q -S -m 'confirmed on the trunk'
    pv_git checkout -q side && pv_git merge -q --no-gpg-sign --no-edit "$trunk"
    expect_pv "HEAD~1" 0 '^OK - 1 confirmation' "let a merge bring in a confirmation its curator signed"
    pv_git checkout -q "$trunk" && printf 'more\n' > "$pv/repo/more.txt" && pv_git add -A && pv_git commit -q --no-gpg-sign -m 'unrelated on the trunk'
    pv_git checkout -q side && pv_git merge -q --no-commit --no-ff "$trunk" >/dev/null && confirmed contract > "$k/evil.md" && pv_git add -A && pv_git commit -q --no-gpg-sign -m 'evil merge'
    expect_pv "HEAD~1" 1 'is unsigned' "read an event a merge adds that neither side held"
    pv_git checkout -q "$trunk"
    pv_git rm -rq .lokf/curators && pv_git commit -q -S -m nokeys
    expect_pv "HEAD~1" 0 '^skipped' "say so and pass with no .lokf/curators/"
  else
    err "could not generate the provenance fixture's keys (gpg --quick-generate-key or ssh-keygen failed)"
  fi
  rm -rf "$pv"
else
  say "gpg or ssh-keygen not installed locally - CI runs check 13; skipping here"
fi

# 14. CHANGELOG.md never carries two headings for one released version, and
#     changelog-release.mjs's promote folds a second qualifying push between
#     publish.yml runs into the still-unpublished section instead of adding
#     one - the bug that shipped two "## [0.19.0]" headings on 2026-09-17,
#     because semantic-release.yml promotes on every push to main but only
#     publish.yml tags. The first part needs nothing but the file on disk and
#     always runs; the second exercises the fold in a throwaway repository
#     and needs node.
say ""
say "Checking CHANGELOG.md for a version promoted twice..."
mapfile -t headings < <(grep -oE '^## \[[0-9]+\.[0-9]+\.[0-9]+\]' CHANGELOG.md)
dupes="$(printf '%s\n' "${headings[@]}" | sort | uniq -d)"
if [[ -z "$dupes" ]]; then
  ok "every released version in CHANGELOG.md has exactly one heading"
else
  err "CHANGELOG.md has more than one heading for: $(printf '%s' "$dupes" | tr '\n' ' ')"
fi

say ""
say "Exercising changelog-release.mjs's fold..."
if command -v node >/dev/null 2>&1; then
  cl="$(mktemp -d)"
  cl_git() { (cd "$cl/repo" && GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null git "$@"); }
  mkdir -p "$cl/repo/.github/scripts"
  cp "$repo_root/.github/scripts/changelog-release.mjs" "$cl/repo/.github/scripts/"
  # A blank identity falls back to the OS account's GECOS full name, which a
  # CI runner's account does not carry - set one explicitly, as check 13's
  # pv_git does, rather than depend on that fallback existing.
  cl_git init -q \
    && cl_git config user.name contract \
    && cl_git config user.email contract@example.invalid \
    && cl_git commit -q --allow-empty -m base \
    && cl_git tag v0.18.0
  # The state right after the first push's promote landed and a second push
  # then wrote its own Unreleased entry above it, with v0.19.0 still untagged
  # - exactly main's state before publish.yml ever ran for it.
  cat > "$cl/repo/CHANGELOG.md" <<'EOF'
## [Unreleased]

### Fixed

- second push's entry, before publish.yml ever tagged 0.19.0

## [0.19.0] - 2026-09-17

### Added

- first push's entry

## [0.18.0] - 2026-09-16

- older
EOF
  (cd "$cl/repo" && node .github/scripts/changelog-release.mjs promote 0.19.0 2026-09-18 >/dev/null 2>&1)
  count="$(grep -cE '^## \[0\.19\.0\]' "$cl/repo/CHANGELOG.md")"
  if [[ "$count" -eq 1 ]] \
     && grep -q "first push's entry" "$cl/repo/CHANGELOG.md" \
     && grep -q "second push's entry" "$cl/repo/CHANGELOG.md" \
     && grep -qE '^## \[Unreleased\]$' "$cl/repo/CHANGELOG.md"; then
    ok "a second push before publish.yml tags folds into the one pending section"
  else
    err "promote wrote $count heading(s) for 0.19.0 instead of folding"
  fi
  cl_git tag v0.19.0
  # promote already left one empty "## [Unreleased]" at the top; fill it in
  # place rather than appending a second one, which readUnreleased would
  # never see (it reads the first "## [Unreleased]" in the file).
  printf '\n### Fixed\n\n- a change after 0.19.0 shipped\n' \
    | sed -i '/^## \[Unreleased\]$/r /dev/stdin' "$cl/repo/CHANGELOG.md"
  (cd "$cl/repo" && node .github/scripts/changelog-release.mjs promote 0.19.1 2026-09-19 >/dev/null 2>&1)
  if [[ "$(grep -cE '^## \[0\.19\.[01]\]' "$cl/repo/CHANGELOG.md")" -eq 2 ]]; then
    ok "a version already tagged is left alone and the next one gets its own heading"
  else
    err "promote folded into 0.19.0 even though v0.19.0 is already tagged"
  fi
  rm -rf "$cl"
else
  say "node not installed locally - CI runs check 14; skipping here"
fi

# 15. The librarian template's LOKF_SKILLS_REF pins the release of *this*
#     repository that a host installs the skill from, so it goes stale
#     silently: nothing fails when it falls behind, the host just keeps
#     running an old librarian. It sat at v0.9.0 while this repository
#     released v0.19.2.
#
#     The pin must name a release that a host can actually clone, so it is
#     held to one of the *two* newest released headings in CHANGELOG.md, not
#     just the newest. The newest heading exists before its tag does:
#     semantic-release.yml promotes it on merge to main, and publish.yml
#     creates the tag later. During that window - which is exactly when
#     publish.yml runs this contract - the only valid pin is the heading
#     below the top one, so requiring the top one failed every release.
#     Two headings of slack covers that window and still catches real rot,
#     which is measured in many versions, not one.
say ""
say "Checking the librarian template's skills pin is a current release..."
pin="$(grep -oE 'LOKF_SKILLS_REF: v[0-9]+\.[0-9]+\.[0-9]+' \
         skills/lokf-sidecar/templates/github/knowledge-librarian.yaml | head -1 | sed 's/.*: //')"
mapfile -t recent < <(grep -oE '^## \[[0-9]+\.[0-9]+\.[0-9]+\]' CHANGELOG.md \
                        | head -2 | tr -d '#[] ' | sed 's/^/v/')
if [[ -z "$pin" ]]; then
  err "no LOKF_SKILLS_REF pin found in the librarian template - check 15 cannot read what a host would install"
elif [[ "${#recent[@]}" -eq 0 ]]; then
  err "CHANGELOG.md has no released version heading, so check 15 cannot tell whether $pin is current"
elif printf '%s\n' "${recent[@]}" | grep -qxF -- "$pin"; then
  ok "the librarian template pins $pin, one of this repository's two newest releases"
else
  err "the librarian template pins LOKF_SKILLS_REF: $pin but this repository's two newest releases are ${recent[*]} - a host scaffolded from this template installs a librarian that old; bump the pin in the template and in each sibling's own copy of the workflow"
fi

say ""
if [[ "$fail" -eq 0 ]]; then
  say "Repository contract: PASS"
  exit 0
else
  say "Repository contract: FAIL"
  exit 1
fi
