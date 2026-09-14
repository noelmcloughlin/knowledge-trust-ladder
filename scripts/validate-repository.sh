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
  declared="$(sed -n 's/^name:[[:space:]]*//p' "$skill_file" | head -1 | tr -d '"'"'"'')"
  expected="$(basename "$dir")"
  if [[ "$declared" == "$expected" ]]; then
    ok "$skill_file frontmatter name '$declared' matches directory"
  else
    err "$skill_file frontmatter name '$declared' does not match directory '$expected'"
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
  "$templates/scripts/knowledge-conventions.sh:.lokf/scripts/knowledge-conventions.sh"; do
  src="${pair%%:*}"; dst="${pair##*:}"
  if cmp -s "$src" "$dst"; then
    ok "$dst matches its template"
  else
    err "$dst differs from $src - copy the template over it (this repository dogfoods its own sidecar)"
  fi
done

say ""
say "Exercising knowledge-conventions.sh..."
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
findings="$(bash "$templates/scripts/knowledge-conventions.sh" "$bad/k" 2>&1 || true)"
rm -rf "$bad"
for want in "not a bare ISO date" "not newest-first" "unquoted timestamp" "bare mapping" "open question not" "2 process:lokf-librarian events"; do
  if grep -q "$want" <<<"$findings"; then
    ok "conventions script reports: $want"
  else
    err "conventions script failed to report '$want' on a bundle that breaks it"
  fi
done

say ""
if [[ "$fail" -eq 0 ]]; then
  say "Repository contract: PASS"
  exit 0
else
  say "Repository contract: FAIL"
  exit 1
fi
