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

# 7. The LOKF class vocabulary is stated as prose in several files, with no
#    generator behind it. Rule 3 in lokf-librarian/SKILL.md is the canonical
#    list; every other enumeration and every stated count must agree with it.
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
  canonical="$(printf '%s' "$rule3_list" | grep -o '`[A-Z][A-Za-z]*`' | tr -d '`' | grep -vx 'Concept' | sort -u)"
  canonical_count="$(printf '%s\n' "$canonical" | grep -c .)"
  ok "Rule 3 names $canonical_count classes"

  # 7a. The curator's trust-fields.md carries the other complete enumeration.
  tf_line="$(grep -m1 '^- \*\*The 15 classes\*\*\|^- \*\*The [a-z]* classes\*\*' skills/lokf-curator/references/trust-fields.md || true)"
  if [[ -z "$tf_line" ]]; then
    err "could not find the class enumeration in lokf-curator/references/trust-fields.md"
  else
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

say ""
if [[ "$fail" -eq 0 ]]; then
  say "Repository contract: PASS"
  exit 0
else
  say "Repository contract: FAIL"
  exit 1
fi
