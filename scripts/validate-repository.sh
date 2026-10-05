#!/usr/bin/env bash
# Repository-contract checks for the knowledge-trust-ladder distribution
# repo. Separate from specification/Markdown checks (workflows/validate.yml
# runs those as their own jobs) so failures are easy to diagnose.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fail=0
say() { printf '%s\n' "$*"; }
err() { printf 'FAIL: %s\n' "$*" >&2; fail=1; }
ok() { printf 'OK:   %s\n' "$*"; }

# 1. Exactly the intended published skill directories exist. This list is the
#    one place their number is written: checks 1 and 4 count it.
mapfile -t skill_dirs < <(find skills -mindepth 1 -maxdepth 1 -type d | sort)
expected_dirs=("skills/ktl-curator" "skills/ktl-docent" "skills/ktl-librarian" "skills/ktl-prose" "skills/ktl-sidecar")
if [[ "${skill_dirs[*]}" == "${expected_dirs[*]}" ]]; then
  ok "exactly the ${#expected_dirs[@]} intended skill directories exist (${expected_dirs[*]})"
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
#     field (agentskills.io/specification: 1-500 characters). So git, a POSIX
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

# 3c. Catalogs have no tag field: `gh skill search` matches name and
#     description, skills.sh matches file text. So each description ends in a
#     `Keywords:` list, inside the spec's 1024 characters. The Claude Code
#     plugin manifest and its marketplace entry carry one keyword list between
#     them, written on one line in each so the two can be compared.
for dir in "${expected_dirs[@]}"; do
  skill_file="$dir/SKILL.md"
  [[ -f "$skill_file" ]] || continue
  desc="$(awk 'NR>1 && /^---$/ {exit} /^description:/ {sub(/^description:[[:space:]]*/, ""); print}' "$skill_file")"
  if (( ${#desc} > 1024 )); then
    err "$skill_file description is ${#desc} characters; the Agent Skills spec allows 1024"
  elif ! grep -qE ' Keywords: [^.]+\.'"'"'?$' <<<"$desc"; then
    err "$skill_file description does not end in a 'Keywords: a, b, c.' list - it is the only tag a skills catalog reads"
  else
    ok "$skill_file description ends in a Keywords list (${#desc} characters)"
  fi
done
plugin_kw="$(grep '"keywords"' .claude-plugin/plugin.json 2>/dev/null | sed 's/^ *//' || true)"
market_kw="$(grep '"keywords"' .claude-plugin/marketplace.json 2>/dev/null | sed 's/^ *//' || true)"
if [[ -z "$plugin_kw" || -z "$market_kw" ]]; then
  err ".claude-plugin/plugin.json or marketplace.json is missing, or has no one-line keywords array"
elif [[ "$plugin_kw" == "$market_kw" ]]; then
  ok "plugin.json and marketplace.json carry the same keywords"
else
  err ".claude-plugin/plugin.json and marketplace.json list different keywords - keep the one-line arrays identical"
fi

# 4. No unexpected duplicate SKILL.md files in publishable paths.
mapfile -t all_skill_md < <(find skills -iname 'SKILL.md' | sort)
if [[ ${#all_skill_md[@]} -eq ${#expected_dirs[@]} ]]; then
  ok "no duplicate SKILL.md files under skills/"
else
  err "expected exactly ${#expected_dirs[@]} SKILL.md files under skills/, found ${#all_skill_md[@]}: ${all_skill_md[*]}"
fi

# 5. Relative references remain valid after the complete skill directory is
#    copied, that is, resolved from each linking file's own directory. This
#    is exactly how an installer copies one skill/ subtree at a time.
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
#    generator behind it. Rule 3 in ktl-librarian/SKILL.md is the canonical
#    list; the other enumeration, and any count a page still states, must
#    agree with it. Prose elsewhere says "small" rather than a number: the
#    count is the schema's to change, not this repository's.
#    (On 2026-09-14 Rule 3 said fourteen and omitted Role while README.md and
#    docs/for-the-curious.md said fifteen, and nobody noticed until a person
#    read both. This check is why that cannot happen twice.)
rule3_line="$(grep -m1 '^3\. \*\*Use a class from the LOKF type vocabulary' skills/ktl-librarian/SKILL.md || true)"
if [[ -z "$rule3_line" ]]; then
  err "could not find Rule 3's class list in skills/ktl-librarian/SKILL.md"
else
  # The list ends where the domain-schema sentence begins; that sentence names
  # `Concept` and a sample parent class, neither of which is part of the list.
  rule3_list="${rule3_line%%\*\*A host may have extended*}"
  # shellcheck disable=SC2016 # literal backticks for grep to match (markdown
  # code spans around a class name), not a command substitution. Double
  # quotes here would make the shell try to run `[A-Z][A-Za-z]*` as a command.
  canonical="$(printf '%s' "$rule3_list" | grep -o '`[A-Z][A-Za-z]*`' | tr -d '`' | grep -vx 'Concept' | sort -u)"
  canonical_count="$(printf '%s\n' "$canonical" | grep -c .)"
  ok "Rule 3 names $canonical_count classes"

  # 7a. The curator's trust-fields.md carries the other complete enumeration.
  tf_line="$(grep -m1 '^- \*\*The 15 classes\*\*\|^- \*\*The [a-z]* classes\*\*' skills/ktl-curator/references/trust-fields.md || true)"
  if [[ -z "$tf_line" ]]; then
    err "could not find the class enumeration in ktl-curator/references/trust-fields.md"
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
#    (github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/<path>), and their
#    link checks follow those for real. Moving or renaming one of these paths
#    passes every check in this repo, and breaks the build in
#    obsidian-ktl-curator and obsidian-ktl-registrar. (The mirror image
#    happened on 2026-09-14: the curator referenced domain-schema.md while it
#    was still on a branch here, and its build failed with a 404 until this
#    side merged. CONTRIBUTING.md carries the ordering rule; this check carries
#    the paths.)
say ""
say "Checking the paths sibling repositories link into..."
sibling_paths=(
  "AI_COVENANT.md"
  "SECURITY.md"
  ".lokf/knowledge/playbooks/open-bundle-in-obsidian.md"
  "docs/obsidian.md"
  "docs/releasing.md"
  "docs/signing-commits.md"
  "docs/threat-model.md"
  "docs/three-lines.md"
  "skills/ktl-librarian/references/domain-schema.md"
  "skills/ktl-curator/references/review-session.md"
  "skills/ktl-curator/references/trust-fields.md"
)
for p in "${sibling_paths[@]}"; do
  if [[ -e "$p" ]]; then
    ok "sibling-linked path exists: $p"
  else
    err "sibling-linked path is gone: $p - obsidian-ktl-curator, and obsidian-ktl-registrar link to it by URL; restore it, or update their links in the same change"
  fi
done

# 9a. When the siblings are cloned beside this repo, confirm the list above is
#     still complete: a sibling that adds a deep link should record the path
#     here in the same breath, or the check silently stops covering it. CI has
#     no siblings checked out, so this half only runs locally. The recorded
#     list is the contract either way.
mapfile -t cloned < <(for s in obsidian-ktl-curator obsidian-ktl-registrar; do
  [[ -d "../$s/.git" ]] && printf '%s\n' "../$s"
done || true)
if [[ ${#cloned[@]} -eq 0 ]]; then
  say "      (no sibling clones beside this repo - skipping the completeness cross-check)"
else
  # Each sibling installs these skills under .agents/skills (with .claude/skills
  # symlinked to it), so those trees are copies of this repository. Their
  # self-links are not a sibling depending on us, and counting them reports
  # every page the skills link to internally. Skip them, and .venv, which is
  # only slow. (git-aware greps hide these via .gitignore; plain grep does not.)
  mapfile -t linked < <(grep -rhoE 'https://github\.com/noelmcloughlin/knowledge-trust-ladder/blob/main/[^)"#[:space:]]+' \
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
#     policy, not a threat model. Each rule or surface is a line or two that
#     links to where its reasoning lives: a code comment, a workflow header,
#     a page under docs/. A word budget is the one signal every contributor,
#     person or agent, reliably reads. CONTRIBUTING sits between 700 and 850
#     across the three repositories, and 1000 is where one has started to
#     become a design log again. SECURITY sits between 450 and 800, and was
#     1,400 to 1,900 before docs/threat-model.md took the design, so 900 is
#     its line. The siblings keep the same budgets in their own checks.
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

# 11. This repository runs its own sidecar from the templates, and CI lints
#     the copies under .github/ and .lokf/scripts/ rather than the templates
#     themselves (actionlint is pointed at both, ShellCheck scans the tree).
#     So the copies must stay byte-identical, or a template change is
#     released unlinted. knowledge-librarian.yaml is among them, apart from
#     the values of TRUST_LADDER_SKILLS_REF and TRUST_LADDER_SKILLS_SHA: the
#     release commit moves the template's pin but may not touch
#     .github/workflows/, and the install step that reads the pin is skipped
#     in this repository anyway.
#     Then the conventions script itself is exercised: it must pass on this
#     repository's own bundle and fail on a bundle that breaks each rule. A
#     checker that cannot fail is not covering anything.
say ""
say "Checking the sidecar templates are the copies CI lints..."
templates="skills/ktl-sidecar/templates"
# The skills pin is each repository's own to move, so it is not drift.
unpin() { sed -E -e 's/(TRUST_LADDER_SKILLS_REF: )v[0-9]+\.[0-9]+\.[0-9]+/\1vX.Y.Z/' -e 's/(TRUST_LADDER_SKILLS_SHA: )[0-9a-f]{40}/\1COMMIT/' "$1"; }
for pair in \
  "$templates/github/knowledge-registrar.yaml:.github/workflows/knowledge-registrar.yaml" \
  "$templates/github/knowledge-librarian.yaml:.github/workflows/knowledge-librarian.yaml" \
  "$templates/github/knowledge-release.yaml:.github/workflows/knowledge-release.yaml" \
  "$templates/scripts/knowledge-librarian.sh:.lokf/scripts/knowledge-librarian.sh" \
  "$templates/scripts/knowledge-conventions.sh:.lokf/scripts/knowledge-conventions.sh" \
  "$templates/scripts/knowledge-conventions.py:.lokf/scripts/knowledge-conventions.py" \
  "$templates/scripts/knowledge-preflight.sh:.lokf/scripts/knowledge-preflight.sh" \
  "$templates/scripts/knowledge-provenance.sh:.lokf/scripts/knowledge-provenance.sh" \
  "$templates/scripts/knowledge-feedback.sh:.lokf/scripts/knowledge-feedback.sh" \
  "$templates/scripts/knowledge-apply.sh:.lokf/scripts/knowledge-apply.sh" \
  "$templates/scripts/knowledge-apply.py:.lokf/scripts/knowledge-apply.py" \
  "$templates/scripts/knowledge-report.sh:.lokf/scripts/knowledge-report.sh" \
  "$templates/m365/knowledge-m365.sh:.lokf/m365/knowledge-m365.sh" \
  "$templates/m365/ktl-docent-m365.md:.lokf/m365/ktl-docent-m365.md" \
  "$templates/gitattributes:.lokf/.gitattributes"; do
  src="${pair%%:*}"; dst="${pair##*:}"
  if cmp -s <(unpin "$src") <(unpin "$dst"); then
    ok "$dst matches its template"
  else
    err "$dst differs from $src - this repository dogfoods its own sidecar, so the two must match: copy the template over the workflow after editing the template, or the workflow over the template after a Dependabot action bump, which only ever edits .github/workflows/"
  fi
done

# The two Python halves install PyYAML through `uv run`, from the dependency
# block each carries. That block names one release and takes no file uploaded
# after a date, so a gate never runs a parser nobody reviewed. The two files
# must name the same release and the same date.
pyyaml_pins="$(grep -hE '^# (dependencies = \["pyyaml==[0-9]+(\.[0-9]+)+"\]|exclude-newer = "[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:]+Z")$' \
                 "$templates/scripts/knowledge-apply.py" "$templates/scripts/knowledge-conventions.py" | sort | uniq -c | awk '{ print $1 }' | tr '\n' ' ')"
if [[ "$pyyaml_pins" == "2 2 " ]]; then
  ok "knowledge-apply.py and knowledge-conventions.py pin the same PyYAML release and the same cut-off date"
else
  err "knowledge-apply.py and knowledge-conventions.py must each carry 'dependencies = [\"pyyaml==<version>\"]' and an 'exclude-newer' date, the same in both - one is missing, unpinned or different"
fi

say ""
say "Exercising knowledge-conventions.sh..."
# Eight of the thirteen rules run through `uv run`, so without uv the script reports
# none of them, and every expectation below fails saying only that it "failed
# to report" something, never why. Name the cause once, up front: a job that
# runs this contract installs uv (validate.yml and publish.yml both do).
if ! command -v uv >/dev/null 2>&1; then
  err "uv is not on PATH, so rules 2, 3, 4, 7, 9, 10, 12 and 13 cannot run and every expectation for them below will fail - install uv, or add the setup-uv step to the workflow running this"
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
printf -- '---\ntype: Service\nverified:\n  by: process:ktl-librarian\n  at: 2026-09-14T00:00:00Z\n---\n\n## Open questions\n\n- unclear (process:ktl-librarian, 2026-09-12)\n' > "$bad/k/x/a.md"
printf -- '---\ntype: Service\nverified:\n  - by: process:ktl-librarian\n    at: "2026-09-13T00:00:00Z"\n  - by: process:ktl-librarian\n    at: "2026-09-14T00:00:00Z"\n---\n' > "$bad/k/x/b.md"
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
# Rule 11, in three cases:
#   - a time later than the commit that recorded it, committed at a fixed
#     committer date so the verdict does not depend on today;
#   - a time in the future on a file not committed yet;
#   - a time before its commit, which must pass.
stamped() { printf -- '---\ntype: Service\ngenerated:\n  by: process:ktl-librarian\n  at: "%s"\n---\n' "$1"; }
stamped "2026-09-17T01:00:00Z" > "$bad/k/x/r11-late.md"
stamped "2026-09-16T23:00:00Z" > "$bad/k/x/r11-ok.md"
"${tmpgit[@]}" add k/x/r11-late.md k/x/r11-ok.md
GIT_COMMITTER_DATE="2026-09-17T00:00:00Z" "${tmpgit[@]}" commit -q -m stamp
stamped "2999-01-01T00:00:00Z" > "$bad/k/x/r11-future.md"
# Rule 13: a confirmed concept edited after its confirmation, with
# `generated` left as it was, in its body or in its description. What a
# confirmation does not cover must pass: a person's note with the status it
# sets, KTL Registrar's block with its own `## Related` heading, and values
# written back requoted. So must an edit that moved `generated` past the
# confirmation, and one its person confirmed again.
r13() {  # <name> <title as written> <description> <generated.at> <more frontmatter> <body>, confirmed by human:contract
  printf -- '---\ntype: Service\nid: https://example.invalid/k/x/%s\ntitle: %s\ndescription: %s\ngenerated:\n  by: process:ktl-librarian\n  at: "%s"\nverified:\n  - by: human:contract\n    at: "2026-09-02T00:00:00Z"\n%s---\n\n# Overview\n\n%s\n' \
    "$1" "$2" "$3" "$4" "$5" "$6" > "$bad/k/x/$1.md"
}
for n in r13-edited r13-description r13-notes r13-restamped r13-reconfirmed; do
  r13 "$n" "$n" "what it was." "2026-09-01T00:00:00Z" "" "The text a person confirmed."
done
"${tmpgit[@]}" add k/x/r13-*.md
"${tmpgit[@]}" commit -q -m confirmed
r13 r13-reconfirmed r13-reconfirmed "what it was." "2026-09-01T00:00:00Z" $'  - by: human:contract\n    at: "2026-09-05T00:00:00Z"\n' "The text changed, then confirmed again."
"${tmpgit[@]}" commit -q -am 'edited, and confirmed again'
r13 r13-edited r13-edited "what it was." "2026-09-01T00:00:00Z" "" "The text someone changed by hand."
r13 r13-description r13-description "what it says now." "2026-09-01T00:00:00Z" "" "The text a person confirmed."
r13 r13-restamped r13-restamped "what it was." "2026-09-03T00:00:00Z" "" "The text the pen changed."
r13 r13-notes '"r13-notes"' "what it was." "2026-09-01T00:00:00Z" $'status: draft\n' \
  $'The text a person confirmed.\n\n## Open questions\n\n- 2026-09-03, human:contract: is this still current?\n\n<!-- lokf:related -->\n#how-to\n\n## Related\n\n- [[r13-edited]] (dependsOn)\n<!-- /lokf:related -->'
# Rules 7-9 and the line-ending tolerance:
#   - a CRLF copy of a file that breaks rule 2 must still be reported (a
#     Windows checkout used to make the script skip every frontmatter rule
#     unread);
#   - a byte order mark and a file with no frontmatter are findings;
#   - a sync client's conflict copy shares its original's id and has a name
#     no slug would;
#   - a directory whose case differs is a path-shape finding.
printf -- '---\r\ntype: Service\r\nverified:\r\n  - by: process:ktl-librarian\r\n    at: 2026-09-14T00:00:00Z\r\n---\r\n' > "$bad/k/x/f-crlf.md"
printf '\357\273\277---\ntype: Service\n---\n' > "$bad/k/x/g-bom.md"
printf 'type: Service\n' > "$bad/k/x/h-nofm.md"
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/i\n---\n' > "$bad/k/x/i.md"
cp "$bad/k/x/i.md" "$bad/k/x/i (conflicted copy 2026-09-17).md"
mkdir -p "$bad/k/Upper" && printf -- '---\ntype: Service\n---\n' > "$bad/k/Upper/j.md"
# Rule 10: an event spelt so that the gates' line readers cannot see it.
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/q\nverified:\n  - "by": human:contract\n    at: "2026-09-17T00:00:00Z"\n---\n' > "$bad/k/x/q-quotedkey.md"
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/t\nverified: [{ by: !!str human:contract, at: "2026-09-17T00:00:00Z" }]\n---\n' > "$bad/k/x/t-tag.md"
# A comment beside such a field is valid YAML that a parser drops and a line
# reader takes for part of the value: the report script then cannot read the
# time, so the concept never reads as edited since. A comment on a line of its
# own, and a `#` inside a quoted value, must pass.
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/cm\nverified:\n  - by: human:contract\n    at: "2026-09-17T00:00:00Z" # checked on site\n---\n' > "$bad/k/x/cm-comment.md"
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/co\nverified:\n  # a comment on a line of its own\n  - by: human:contract\n    at: "2026-09-17T00:00:00Z"\n    revision: "etag#1"\n---\n' > "$bad/k/x/co-comment-apart.md"
# What only a parser sees:
#   - a multi-line flow item with an unquoted `at`;
#   - a number where a timestamp should be;
#   - a block that does not parse, reported on one line;
#   - a block that is a list rather than a mapping.
# And what a parser must not see: a second librarian event inside a body code
# fence.
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/fl\nverified: [\n  { by: process:ktl-librarian,\n    at: 2026-09-14T00:00:00Z }\n]\n---\n' > "$bad/k/x/fl-flow.md"
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/n\nverified:\n  - by: process:ktl-librarian\n    at: 20260914\n---\n' > "$bad/k/x/n-int.md"
printf -- '---\ntype: Service\nverified: [unclosed\n---\n' > "$bad/k/x/y-bad.md"
printf -- '---\n- just a list\n---\n' > "$bad/k/x/l-list.md"
# shellcheck disable=SC2016 # the backticks are a Markdown code fence, not a command
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/fence\nverified:\n  - by: process:ktl-librarian\n    at: "2026-09-14T00:00:00Z"\n---\n\n```yaml\nverified:\n  - by: process:ktl-librarian\n    at: "2026-09-15T00:00:00Z"\n```\n' > "$bad/k/x/fence.md"
# Rule 12: a bullet left behind by an edited description fails, in the
# folder's index and in the root's. A bullet that still agrees, a concept no
# index lists, and a line that lists two concepts, which is neither one's
# bullet, must all pass.
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/stale\ntitle: Stale\ndescription: what the concept says now.\n---\n' > "$bad/k/x/idx-stale.md"
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/fresh\ntitle: Fresh\ndescription: >-\n  folded, and\n  still equal.\n---\n' > "$bad/k/x/idx-fresh.md"
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/shared\ntitle: Shared\ndescription: listed only beside another.\n---\n' > "$bad/k/x/idx-shared.md"
printf -- '# K\n\n* [Stale](x/idx-stale.md) - what the concept said before.\n* [Fresh](x/idx-fresh.md) - folded, and still equal.\n* [Fresh](x/idx-fresh.md), [Shared](x/idx-shared.md) - a line that lists two.\n' > "$bad/k/index.md"
printf -- '# X\n\n* [Stale, renamed](idx-stale.md) - what the concept says now.\n* [Fresh](idx-fresh.md) - folded, and still equal.\n' > "$bad/k/x/index.md"
findings="$(bash "$templates/scripts/knowledge-conventions.sh" "$bad/k" 2>&1 || true)"
rm -rf "$bad"
for want in "not a bare ISO date" "not newest-first" "x/a.md: unquoted timestamp" "bare mapping" "open question not" "2 process:ktl-librarian events" "resource not found" "does not hold" \
            "f-crlf.md: unquoted timestamp" "g-bom.md: starts with a byte order mark" "h-nofm.md: no closed frontmatter block" \
            "is declared by more than one file" "conflicted copy 2026-09-17).md: path is not lowercase" "Upper/j.md: path is not lowercase" \
            "q-quotedkey.md: frontmatter uses a quoted key (by)" "t-tag.md: frontmatter uses a tag on" "cm-comment.md: frontmatter uses a comment beside at" \
            "r11-late.md: at \"2026-09-17T01:00:00Z\" is later than the commit that recorded it (2026-09-17T00:00:00Z)" "r11-future.md: at \"2999-01-01T00:00:00Z\" is in the future" \
            "fl-flow.md: unquoted timestamp" "n-int.md: unquoted timestamp" "y-bad.md: frontmatter is not valid YAML" "l-list.md: frontmatter is not a mapping" \
            "idx-stale.md: its bullet in .*/k/index.md does not match" "idx-stale.md: its bullet in .*/k/x/index.md does not match" \
            "r13-edited.md: changed since human:contract confirmed it (2026-09-02, in " \
            "r13-description.md: changed since human:contract confirmed it"; do
  if grep -q "$want" <<<"$findings"; then
    ok "conventions script reports: $want"
  else
    err "conventions script failed to report '$want' on a bundle that breaks it"
  fi
done
for quiet in "x/e.md:whose revision holds its resource" "r11-ok.md:whose time is before the commit that recorded it" "fence.md:whose second librarian event is only an example in a code fence" \
             "co-comment-apart.md:whose comment sits on a line of its own, and whose revision holds a # inside its quotes" \
             "idx-fresh.md:whose index bullets carry its title and its folded description" \
             "idx-shared.md:whose only listing is a root line that names it beside another concept" \
             "r13-notes.md:whose changes since its confirmation are a person's note, its status, the registrar's block and a requoted title" \
             "r13-restamped.md:whose edit moved generated past the confirmation" \
             "r13-reconfirmed.md:whose person confirmed it again after the edit"; do
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
printf -- '---\r\ntype: Service\r\nid: https://example.invalid/k/x/a\r\ndescription: >-\r\n  folded, which the gates\r\n  never read\r\nverified:\r\n  - by: process:ktl-librarian\r\n    at: "2026-09-14T00:00:00Z"\r\n---\r\n\r\n## Open questions\r\n\r\n- 2026-09-14, process:ktl-librarian: fine\r\n' > "$good/k/x/a.md"
if out="$(bash "$templates/scripts/knowledge-conventions.sh" "$good/k" 2>&1)"; then
  ok "conventions script reads a CRLF checkout as CI reads LF"
else
  err "conventions script misreads a CRLF checkout: $out"
fi
# Without uv the shell half still runs, and its OK line says what it skipped.
if PATH=/usr/bin:/bin command -v uv >/dev/null 2>&1; then
  say "uv is on /usr/bin - the without-uv case cannot be staged here"
elif out="$(PATH=/usr/bin:/bin bash "$templates/scripts/knowledge-conventions.sh" "$good/k" 2>/dev/null)" && grep -q '^OK - .*(rules 2, 3, 4, 7, 9, 10, 12 and 13 not checked: uv not found)' <<<"$out"; then
  ok "conventions script without uv passes on its own rules and says which it skipped"
else
  err "conventions script without uv did not say what it skipped: $out"
fi
# A bundle reached through a link, the rearranged layout the sidecar's
# portability page allows, must be read, not passed with zero files seen.
ln -s "$good/k" "$good/linked" && printf 'x' > "$good/k/x/Bad.md"
if out="$(bash "$templates/scripts/knowledge-conventions.sh" "$good/linked" 2>&1)"; then
  err "conventions script passed a linked bundle unread: $out"
elif grep -q 'Bad.md: path is not lowercase' <<<"$out"; then
  ok "conventions script reads a bundle reached through a link"
else
  err "conventions script misread a linked bundle: $out"
fi
rm -rf "$good"

# 11a. ktl-docent runs its own copies of knowledge-report.sh and
#      knowledge-feedback.sh, from its scripts/ folder, and never the
#      repository's under .lokf/scripts/. A question is enough to start the
#      docent, often in a repository the reader has not reviewed, and anyone
#      who can commit to a repository can change its copies. So the docent's
#      copies must match their templates and must run from wherever an
#      installer puts them, against the repository the reader is in. And no
#      page of the docent may send an agent to the repository's copies.
say ""
say "Checking ktl-docent runs its own copies of two sidecar scripts..."
docent_scripts="skills/ktl-docent/scripts"
for s in knowledge-report.sh knowledge-feedback.sh; do
  if cmp -s "$templates/scripts/$s" "$docent_scripts/$s"; then
    ok "$docent_scripts/$s matches its template"
  else
    err "$docent_scripts/$s differs from $templates/scripts/$s - ktl-docent runs its own copy, so copy the template over it in the same change"
  fi
done
# shellcheck disable=SC2016 # the backtick is a Markdown code span, matched as text
if hits="$(grep -rnE 'bash[^`]*\.lokf/scripts/' skills/ktl-docent --include='*.md')"; then
  err "a ktl-docent page runs a script under .lokf/scripts/, which anyone who can commit to the repository can change - point it at <skill>/scripts/ instead: $hits"
else
  ok "no ktl-docent page runs a script under .lokf/scripts/"
fi
# The copies run from a folder outside the reader's repository, as an
# installer leaves them, with the working directory inside it. Each finds
# that repository's root from the working directory, and neither needs git.
ds="$(mktemp -d)"; dr="$(mktemp -d)"
cp -R "$docent_scripts" "$ds/"
mkdir -p "$dr/.lokf/knowledge/x"
printf -- '---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n' > "$dr/.lokf/knowledge/index.md"
printf -- '---\ntype: Service\ntitle: Auto\nverified: [{ by: process:ktl-librarian, at: "2026-01-03T00:00:00Z" }]\n---\n' > "$dr/.lokf/knowledge/x/auto.md"
if out="$(cd "$dr/.lokf/knowledge/x" && bash "$ds/scripts/knowledge-report.sh" labels x/auto.md 2>&1)" \
   && [[ "$out" == '- Auto (x/auto.md) - checked by automation only' ]]; then
  ok "ktl-docent's knowledge-report.sh labels a concept of the repository it is run in"
else
  err "ktl-docent's knowledge-report.sh, run from outside the repository, did not label its concept: $out"
fi
if out="$(cd "$dr/.lokf/knowledge/x" && bash "$ds/scripts/knowledge-feedback.sh" Miss 'asked from inside the repository' 2>&1)" \
   && grep -qx -- '- \*\*Miss\*\* - asked from inside the repository - docent' "$dr/.lokf/feedback.md"; then
  ok "ktl-docent's knowledge-feedback.sh records a gap in the repository it is run in"
else
  err "ktl-docent's knowledge-feedback.sh, run from outside the repository, did not record the gap there: $out"
fi
rm -rf "$ds" "$dr"

# 12. The preflight script every skill runs first must always end on its
#     summary line and exit 0. That holds on this repository, and on a bare
#     directory with no bundle, no git and no skills, where every section has
#     to cope with absence rather than fail. A CRLF file must raise its
#     warning.
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
# A scripts/ directory with no knowledge-feedback.sh sends ktl-docent back to
# editing feedback.md by hand, which is the exposure that script removes, so
# the preflight names it rather than leaving it to be discovered.
if out="$(bash "$templates/scripts/knowledge-preflight.sh" "$bare" 2>&1)" && grep -q '^warn    copies .*knowledge-feedback.sh missing' <<<"$out"; then
  ok "preflight warns when knowledge-feedback.sh is missing from a sidecar's scripts/"
else
  err "preflight did not report the missing knowledge-feedback.sh: $out"
fi
cp "$templates/scripts/knowledge-feedback.sh" "$bare/.lokf/scripts/"
if out="$(bash "$templates/scripts/knowledge-preflight.sh" "$bare" 2>&1)" && ! grep -q 'knowledge-feedback.sh missing' <<<"$out"; then
  ok "preflight stops naming knowledge-feedback.sh once it is there"
else
  err "preflight still reports knowledge-feedback.sh as missing after it was laid down: $out"
fi
rm -rf "$bare"
# The gate installs the toolkit with `uv sync --locked`, which fails when git
# holds no lock. A host that carries the gate and never committed
# .lokf/uv.lock hears so from the preflight, before its next pull request does.
locked="$(mktemp -d)"; mkdir -p "$locked/.lokf/knowledge" "$locked/.github/workflows"
locked_git=(env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null git -C "$locked"
  -c init.defaultBranch=main -c user.name=contract -c user.email=contract@example.invalid -c commit.gpgsign=false)
"${locked_git[@]}" init -q
printf -- '---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n' > "$locked/.lokf/knowledge/index.md"
cp "$templates/pyproject.toml" "$locked/.lokf/pyproject.toml"
cp "$templates/github/knowledge-registrar.yaml" "$locked/.github/workflows/"
"${locked_git[@]}" add -A && "${locked_git[@]}" commit -q -m 'a host with the gate and no lock'
if out="$(bash "$templates/scripts/knowledge-preflight.sh" "$locked" 2>&1)" && grep -q '^warn    toolkit .*uv.lock is not in git' <<<"$out"; then
  ok "preflight warns when the gate is installed and git holds no .lokf/uv.lock for it to install from"
else
  err "preflight did not report the missing .lokf/uv.lock: $out"
fi
printf 'version = 1\n' > "$locked/.lokf/uv.lock" && "${locked_git[@]}" add -A && "${locked_git[@]}" commit -q -m 'the lock is committed'
if out="$(bash "$templates/scripts/knowledge-preflight.sh" "$locked" 2>&1)" && ! grep -q 'uv.lock is not in git' <<<"$out"; then
  ok "preflight stops naming .lokf/uv.lock once git holds it"
else
  err "preflight still reports .lokf/uv.lock as missing after it was committed: $out"
fi
rm -rf "$locked"
# Every line the preflight can print as missing or a warning has a row on the
# sidecar's prerequisites page: the plain-words meaning, who fixes it and what
# to send them. So a new preflight line cannot be added without one.
prereq="skills/ktl-sidecar/references/prerequisites.md"
while IFS= read -r key; do
  if grep -q "^| \`$key\` |" "$prereq"; then
    ok "prerequisites.md explains the preflight's '$key' line"
  else
    err "prerequisites.md has no row for the preflight's '$key' line - add what it means, who fixes it and what to send them"
  fi
done < <(grep -oE '\b(miss|warn) [a-z]+' "$templates/scripts/knowledge-preflight.sh" | awk '{print $2}' | sort -u)
for s in knowledge-preflight.sh knowledge-conventions.sh knowledge-provenance.sh knowledge-feedback.sh knowledge-apply.sh knowledge-report.sh; do
  if out="$(sh "$templates/scripts/$s" x 2>&1)"; then
    err "$s run under sh did not stop: $out"
  elif grep -q '^run this with bash' <<<"$out"; then
    ok "$s run under sh stops and names bash"
  else
    err "$s run under sh failed some other way: $out"
  fi
done

# 12a. ktl-docent records a reader's gap by running knowledge-feedback.sh
#      rather than by opening .lokf/feedback.md, so that no other reader's
#      report enters its session. The script has to earn that trust:
#        - newest first across days and within a day, with a day after today
#          (another machine's clock) left above rather than doubled;
#        - the two kinds the librarian can consume, in any letter case, and
#          no third;
#        - an attribution shaped as both provenance gates shape a login, or
#          none at all;
#        - one line per entry, whatever it is handed;
#        - not a word of what is already in the file on its own output;
#        - a refusal that leaves the file exactly as it was;
#        - a bundle told apart from no bundle, a read-only one, and one
#          another run holds.
say ""
say "Exercising knowledge-feedback.sh..."
feedback="$repo_root/$templates/scripts/knowledge-feedback.sh"
fb="$(mktemp -d)"; mkdir -p "$fb/.lokf"
fbfile="$fb/.lokf/feedback.md"
recorded='^recorded: (Miss|Disagreement) under ([0-9]{4}-[0-9]{2}-[0-9]{2}) in \.lokf/feedback\.md \(([0-9]+) waiting'
# No bundle, no entry: the docent is told to say the gap out loud instead.
set +e
out="$(bash "$feedback" --root "$fb" Miss 'nowhere to go' 2>&1)"; rc=$?
set -e
if [[ "$rc" == 2 && ! -e "$fbfile" ]]; then
  ok "knowledge-feedback.sh refuses to record against a .lokf/ with no bundle"
else
  err "knowledge-feedback.sh wrote feedback for a .lokf/ with no knowledge/ (exit $rc): $out"
fi
mkdir -p "$fb/.lokf/knowledge"
today=""
# UTC is read before and after the call, so a run that straddles midnight
# still passes and a script that fell back to local time still fails.
utc_before="$(date -u +%Y-%m-%d)"
if out="$(bash "$feedback" --root "$fb" Miss 'the first gap SENTINEL' 2>&1)" && [[ "$out" =~ $recorded ]] \
   && [[ "${BASH_REMATCH[1]}" == Miss && "${BASH_REMATCH[3]}" == 1 ]]; then
  today="${BASH_REMATCH[2]}"
  if grep -qx '# Reader feedback for the librarian' "$fbfile" && grep -qx "## $today" "$fbfile" \
     && grep -qx -- '- \*\*Miss\*\* - the first gap SENTINEL - docent' "$fbfile" \
     && [[ "$today" == "$utc_before" || "$today" == "$(date -u +%Y-%m-%d)" ]]; then
    ok "knowledge-feedback.sh creates feedback.md and files the first entry under today, UTC"
  else
    err "knowledge-feedback.sh reported $today but wrote something else: $(grep -n '^## \|^- ' "$fbfile" | tr '\n' ' ')"
  fi
else
  err "knowledge-feedback.sh did not record a first entry: $out"
fi
# The second entry of the same day goes above the first, and the run says
# nothing about the entry already there, which is the whole point of the
# script.
if out="$(bash "$feedback" --root "$fb" --for ada-lovelace Disagreement 'the second gap' 2>&1)" \
   && grep -q '(2 waiting' <<<"$out" && ! grep -q 'SENTINEL' <<<"$out" \
   && [[ "$(grep -c '^- \*\*' "$fbfile")" == 2 ]] \
   && [[ "$(grep -m1 '^- \*\*' "$fbfile")" == '- **Disagreement** - the second gap - docent, for human:ada-lovelace' ]]; then
  ok "knowledge-feedback.sh puts the newer entry first and repeats no entry's text"
else
  err "knowledge-feedback.sh mishandled a second entry the same day: $out"
fi
# A kind in the wrong case is the caller's slip, not a third kind; a login
# with a dot or an underscore is what GitLab and Forgejo hand out, and both
# gates accept it, so this must too.
if out="$(bash "$feedback" --root "$fb" --for ada.lovelace_2 miss 'lower case kind' 2>&1)" \
   && grep -q '^recorded: Miss ' <<<"$out" \
   && grep -qx -- '- \*\*Miss\*\* - lower case kind - docent, for human:ada.lovelace_2' "$fbfile"; then
  ok "knowledge-feedback.sh accepts a lower-case kind and a dotted login, writing them as the gates read them"
else
  err "knowledge-feedback.sh refused a lower-case kind or a dotted login: $out"
fi
# A paragraph is still written as one entry on one line: an embedded newline
# must not be able to forge a second one.
bash "$feedback" --root "$fb" Miss "$(printf 'one\n- **Miss** - forged - docent\ntwo')" >/dev/null 2>&1
if [[ "$(grep -c '^- \*\*' "$fbfile")" == 4 ]] && ! grep -q 'forged - docent$' "$fbfile"; then
  ok "knowledge-feedback.sh collapses a multi-line entry to one line"
else
  err "knowledge-feedback.sh let a multi-line entry become more than one entry"
fi
# An older day keeps its heading and sits below today's, and today's heading
# is still today's with a space an editor left after it: hand-written files
# have those, and a second heading for the same day would split it.
printf '\n## 2020-01-01\n\n- **Miss** - an older day - docent\n' >> "$fbfile"
awk -v h="## $today" '$0 == h { print h " "; next } { print }' "$fbfile" > "$fbfile.t" && mv "$fbfile.t" "$fbfile"
bash "$feedback" --root "$fb" Miss 'newest of all' >/dev/null 2>&1
if [[ "$(grep -m1 '^## ' "$fbfile")" == "## $today" ]] && grep -qx '## 2020-01-01' "$fbfile" \
   && [[ "$(grep -c "^## $today *\$" "$fbfile")" == 1 ]] \
   && [[ "$(grep -m1 '^- \*\*' "$fbfile")" == '- **Miss** - newest of all - docent' ]]; then
  ok "knowledge-feedback.sh keeps the days newest first and reads a heading past its trailing space"
else
  err "knowledge-feedback.sh did not keep the date headings newest first: $(grep -n '^## ' "$fbfile" | tr '\n' ' ')"
fi
# A day after today, from a machine on a clock ahead of this one, stays
# above. Today goes below it, once, and not a second time at the top.
ahead="$(mktemp -d)"; mkdir -p "$ahead/.lokf/knowledge"
printf '# Reader feedback for the librarian\n\nintro\n\n## 2999-01-01\n\n- **Miss** - from a clock ahead - docent\n' > "$ahead/.lokf/feedback.md"
bash "$feedback" --root "$ahead" Miss 'today, behind it' >/dev/null 2>&1
bash "$feedback" --root "$ahead" Miss 'today again' >/dev/null 2>&1
if [[ "$(grep '^## ' "$ahead/.lokf/feedback.md" | tr '\n' ' ')" == "## 2999-01-01 ## $today " ]] \
   && [[ "$(grep -c '^- \*\*' "$ahead/.lokf/feedback.md")" == 3 ]]; then
  ok "knowledge-feedback.sh leaves a day after today above and files today once beneath it"
else
  err "knowledge-feedback.sh misfiled today under a day ahead of it: $(grep -n '^## \|^- ' "$ahead/.lokf/feedback.md" | tr '\n' ' ')"
fi
rm -rf "$ahead"
before="$(cat "$fbfile")"
feedback_refuses() { # <what it should refuse> <argument...>
  local what="$1"; shift
  local out rc
  set +e
  out="$(bash "$feedback" --root "$fb" "$@" 2>&1)"
  rc=$?
  set -e
  if [[ "$rc" == 2 ]]; then
    ok "knowledge-feedback.sh refuses $what and writes nothing"
  else
    err "knowledge-feedback.sh accepted $what (exit $rc): $out"
  fi
}
feedback_refuses "a kind the librarian has no rule for" Question 'x'
feedback_refuses "an attribution with a space in it" --for 'ada lovelace' Miss 'x'
feedback_refuses "an attribution starting with a dot" --for '.ada' Miss 'x'
feedback_refuses "an attribution starting with a hyphen" --for '-ada' Miss 'x'
feedback_refuses "an empty entry" Miss '   '
feedback_refuses "a call with no entry text" Miss
feedback_refuses "a root that does not exist" --root "$fb/nowhere" Miss 'x'
if [[ "$before" == "$(cat "$fbfile")" ]]; then
  ok "knowledge-feedback.sh left feedback.md untouched on every refusal"
else
  err "knowledge-feedback.sh changed feedback.md while refusing a call"
fi
# A lock another run holds is exit 1 after a short wait, naming the lock, and
# the file is untouched. A read-only bundle is exit 1 too, since either is
# the docent's cue to say the gap out loud rather than to fix its call.
mkdir "$fbfile.lock"
set +e
out="$(bash "$feedback" --root "$fb" Miss 'held' 2>&1)"; rc=$?
set -e
rmdir "$fbfile.lock"
if [[ "$rc" == 1 ]] && grep -q 'feedback.md.lock' <<<"$out" && [[ "$before" == "$(cat "$fbfile")" ]]; then
  ok "knowledge-feedback.sh exits 1, names the lock another run holds, and writes nothing"
else
  err "knowledge-feedback.sh mishandled a held lock (exit $rc): $out"
fi
if [[ "$EUID" -eq 0 ]]; then
  say "skipping the read-only check: running as root, which no chmod keeps out"
else
  chmod a-w "$fb/.lokf"
  set +e
  out="$(bash "$feedback" --root "$fb" Miss 'no room' 2>&1)"; rc=$?
  set -e
  chmod u+w "$fb/.lokf"
  if [[ "$rc" == 1 ]] && grep -q 'read-only' <<<"$out"; then
    ok "knowledge-feedback.sh exits 1 and names the read-only bundle"
  else
    err "knowledge-feedback.sh misreported a read-only bundle (exit $rc): $out"
  fi
fi
leftover=""
for f in "$fb/.lokf"/* "$fb/.lokf"/.[!.]*; do
  [[ -e "$f" ]] || continue
  case "${f##*/}" in feedback.md|knowledge) ;; *) leftover="$leftover ${f##*/}" ;; esac
done
if [[ -z "$leftover" ]]; then
  ok "knowledge-feedback.sh leaves no temporary file or lock behind"
else
  err "knowledge-feedback.sh left something beside feedback.md:$leftover"
fi
rm -rf "$fb"

# 13. The forge-free provenance gate, with throwaway keys:
#       - a confirmation signed by the curator on file passes, with a GPG
#         primary key, a GPG signing subkey, or an SSH key;
#       - an unsigned one, one by an id with no key, one by another key, and
#         one whose own key is added in the same range each fail, while
#         another curator's key added alongside does not;
#       - a removed confirmation needs its curator's signature as an added
#         one does, whether the event is struck out or its concept deleted;
#       - a person's generated record may be replaced only by another
#         person's;
#       - a repository with no .lokf/curators/ is a stated skip.
#     It needs gpg and ssh-keygen, which CI has.
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
    # is not, and a human `generated` record, which the curator's Correct
    # writes, is, whatever its layout.
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
    # A person's record is never removed without that person: striking an
    # event out, or deleting the concept that carries it, is a claim its
    # curator signs. A person's generated record may give way to another
    # person's, the curator's Correct, which that person signs as their own;
    # it may not give way to a process's.
    printf -- '---\ntype: Service\n---\n' > "$k/j.md" && pv_git commit -q --no-gpg-sign -am 'event struck out, unsigned'
    expect_pv "HEAD~1" 1 'removes a confirmation by human:contract but is unsigned' "report a confirmation struck out by an unsigned commit"
    printf -- '---\ntype: Service\n---\n' > "$k/b.md" && pv_git commit -q -S -am 'event struck out by its curator'
    expect_pv "HEAD~1" 0 '^OK - 1 confirmation' "pass a confirmation its own curator struck out and signed"
    pv_git rm -q "$k/d.md" && pv_git commit -q --no-gpg-sign -m 'confirmed concept deleted, unsigned'
    expect_pv "HEAD~1" 1 'removes a confirmation by human:contract but is unsigned' "report the deletion of a concept a person confirmed"
    printf -- '---\ntype: Service\nid: https://example.invalid/k/x/gen\ngenerated: { by: human:other, at: "2026-09-20T00:00:00Z" }\n---\n' > "$k/gen.md" && pv_git -c user.signingkey="$fpr2" commit -q -S -am 'corrected by another curator'
    expect_pv "HEAD~1" 0 '^OK - 1 confirmation' "let one person's generated record give way to another's, signed by the second"
    printf -- '---\ntype: Service\nid: https://example.invalid/k/x/gen\ngenerated: { by: process:ktl-librarian, at: "2026-09-21T00:00:00Z" }\n---\n' > "$k/gen.md" && pv_git commit -q --no-gpg-sign -am 'restamped by a process, unsigned'
    expect_pv "HEAD~1" 1 'removes a confirmation by human:other but is unsigned' "report a person's generated record replaced by a process's"
    pv_git rm -rq .lokf/curators && pv_git commit -q -S -m nokeys
    expect_pv "HEAD~1" 0 '^skipped' "say so and pass with no .lokf/curators/"
  else
    err "could not generate the provenance fixture's keys (gpg --quick-generate-key or ssh-keygen failed)"
  fi
  rm -rf "$pv"
else
  say "gpg or ssh-keygen not installed locally - CI runs check 13; skipping here"
fi

# 13a. The same script's --unattended form, which needs no key and no forge.
#      The scheduled librarian's change is one nobody stands behind. So it may
#      add, change or remove no person's event in any YAML layout, add or
#      remove no person's note, and rewrite no text a person wrote. A
#      process's own open question under a person's text is none of those.
say ""
say "Exercising knowledge-provenance.sh --unattended..."
ua="$(mktemp -d)"; uk="$ua/.lokf/knowledge/x"; mkdir -p "$uk"
ua_git=(env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null git -C "$ua"
  -c init.defaultBranch=main -c user.name=contract -c user.email=contract@example.invalid -c commit.gpgsign=false)
"${ua_git[@]}" init -q
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/confirmed\nverified:\n  - by: human:ada\n    at: "2026-09-17T00:00:00Z"\n---\n\n# Overview\n\nConfirmed text.\n' > "$uk/confirmed.md"
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/authored\ngenerated:\n  by: human:ada\n  at: "2026-09-17T00:00:00Z"\n---\n\n# Overview\n\nWritten by a person.\n' > "$uk/authored.md"
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/noted\n---\n\n# Overview\n\n## Open questions\n\n- 2026-09-17, human:ada: send this back\n' > "$uk/noted.md"
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/plain\n---\n\n# Overview\n' > "$uk/plain.md"
"${ua_git[@]}" add -A && "${ua_git[@]}" commit -q -m base
expect_ua() {  # <exit status> <line expected> <what>, then the tree is put back
  local out rc=0
  out="$(cd "$ua" && bash "$repo_root/$templates/scripts/knowledge-provenance.sh" --unattended 2>&1)" || rc=$?
  if [[ "$rc" -eq "$1" ]] && grep -q "$2" <<<"$out"; then ok "unattended gate: $3"; else err "unattended gate did not $3 (exit $rc): $out"; fi
  "${ua_git[@]}" checkout -q -- . && "${ua_git[@]}" clean -qfd
}
printf '\nA paragraph the librarian adds.\n' >> "$uk/plain.md"; printf '\nAnother.\n' >> "$uk/confirmed.md"
expect_ua 0 '^OK - the change against HEAD' "pass a change that edits a draft and a confirmed concept and touches no person's record"
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/plain\nverified: [{ by: human:ada, at: "2026-09-18T00:00:00Z" }]\n---\n\n# Overview\n' > "$uk/plain.md"
expect_ua 1 'x/plain: an unattended change adds or changes a confirmation by human:ada' "refuse a person's event added in a flow layout no line pattern sees"
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/new\nverified:\n  - by: human:ada\n    at: "2026-09-18T00:00:00Z"\n---\n' > "$uk/new.md"
expect_ua 1 'x/new: an unattended change adds or changes a confirmation by human:ada' "refuse a person's event in a concept not yet tracked"
rm "$uk/confirmed.md"
expect_ua 1 'x/confirmed: an unattended change removes a confirmation by human:ada' "refuse the deletion of a concept a person confirmed"
sed -i 's/2026-09-17T00:00:00Z/2026-09-19T00:00:00Z/' "$uk/confirmed.md"
expect_ua 1 'x/confirmed: an unattended change removes a confirmation by human:ada' "refuse a person's event re-dated"
printf -- '- 2026-09-18, human:ada: looks right to me\n' >> "$uk/noted.md"
expect_ua 1 'noted.md: an unattended change adds a note in a person' "refuse a note added in a person's name"
printf -- '---\ntype: Service\nid: https://example.invalid/k/x/noted\n---\n\n# Overview\n' > "$uk/noted.md"
expect_ua 1 "noted.md: an unattended change removes a person's note" "refuse a person's note removed"
sed -i 's/Written by a person./Rewritten by an agent./' "$uk/authored.md"
expect_ua 1 'authored.md: a person wrote this text, and an unattended change rewrites it' "refuse a change to text a person wrote"
printf '\n## Open questions\n\n- 2026-09-18, process:ktl-librarian: the source now says otherwise\n' >> "$uk/authored.md"
expect_ua 0 '^OK - the change against HEAD' "pass a process's own question added under text a person wrote"
rm -rf "$ua"

# 14. CHANGELOG.md never carries two headings for one released version, and
#     changelog-release.mjs's promote merges a second qualifying push between
#     publish.yml runs into the still-unpublished section instead of adding
#     one. That bug released two "## [0.19.0]" headings on 2026-09-17,
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
  # CI runner's account does not carry. Set one explicitly, as check 13's
  # pv_git does, rather than depend on that fallback existing.
  cl_git init -q \
    && cl_git config user.name contract \
    && cl_git config user.email contract@example.invalid \
    && cl_git commit -q --allow-empty -m base \
    && cl_git tag v0.18.0
  # The state right after the first push's promote merged and a second push
  # then wrote its own Unreleased entry above it, with v0.19.0 still untagged:
  # exactly main's state before publish.yml ever ran for it.
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

# 15. The librarian template's TRUST_LADDER_SKILLS_REF pins the release of *this*
#     repository that a host installs the skill from, so it goes stale
#     silently: nothing fails when it falls behind, the host just keeps
#     running an old librarian. It sat at v0.9.0 while this repository
#     released v0.19.2.
#
#     The pin must name a release that a host can actually clone, so it is
#     held to one of the *two* newest released headings in CHANGELOG.md, not
#     just the newest. The newest heading exists before its tag does:
#     semantic-release.yml promotes it on merge to main, and publish.yml
#     creates the tag later. During that window, which is exactly when
#     publish.yml runs this contract, the only valid pin is the heading
#     below the top one, so requiring the top one failed every release.
#     Two headings of slack covers that window and still catches real rot,
#     which is measured in many versions, not one.
say ""
say "Checking the librarian template's skills pin is a current release..."
pin="$(grep -oE 'TRUST_LADDER_SKILLS_REF: v[0-9]+\.[0-9]+\.[0-9]+' \
         skills/ktl-sidecar/templates/github/knowledge-librarian.yaml | head -1 | sed 's/.*: //')"
mapfile -t recent < <(grep -oE '^## \[[0-9]+\.[0-9]+\.[0-9]+\]' CHANGELOG.md \
                        | head -2 | tr -d '#[] ' | sed 's/^/v/')
if [[ -z "$pin" ]]; then
  err "no TRUST_LADDER_SKILLS_REF pin found in the librarian template - check 15 cannot read what a host would install"
elif [[ "${#recent[@]}" -eq 0 ]]; then
  err "CHANGELOG.md has no released version heading, so check 15 cannot tell whether $pin is current"
elif printf '%s\n' "${recent[@]}" | grep -qxF -- "$pin"; then
  ok "the librarian template pins $pin, one of this repository's two newest releases"
else
  err "the librarian template pins TRUST_LADDER_SKILLS_REF: $pin but this repository's two newest releases are ${recent[*]} - a host scaffolded from this template installs a librarian that old; bump the pin in the template and in each sibling's own copy of the workflow"
fi
# A current version is not the whole test. The install step clones that tag
# and copies one path out of it, and a rename leaves the two disagreeing with
# neither line looking wrong. Here v0.21.0 is a real release and skills/ktl-librarian
# is a real path, but that path is not in that tag, since the skills were
# lokf-* until v0.22.0. So every scheduled run on such a host failed there.
# Read the tag where the clone has it. CI checks out one commit without tags,
# and the newest heading is tagged after this contract runs, so a tag that is
# not here skips this half rather than failing it.
# shellcheck disable=SC2016 # $tmp is the template's own literal, not ours
skill_path="$(grep -oE '\$tmp/skills/[A-Za-z0-9._-]+' \
                skills/ktl-sidecar/templates/github/knowledge-librarian.yaml \
                | head -1 | sed 's|^\$tmp/||')"
if [[ -z "$pin" ]]; then
  : # already reported above
elif [[ -z "$skill_path" ]]; then
  err "the librarian template's install step copies no skills/ path that check 15 can read - it cannot tell whether $pin carries the skill a host would install"
elif ! git rev-parse -q --verify "refs/tags/$pin" >/dev/null; then
  say "skipping the pinned tag's contents: $pin is not a tag on this clone"
elif git ls-tree --name-only "$pin" -- "$skill_path" | grep -qxF -- "$skill_path"; then
  ok "$pin carries $skill_path, the path the install step copies out of it"
else
  err "the librarian template pins $pin, which has no $skill_path - the install step clones that tag and copies that path, so every scheduled run on a host scaffolded from this template fails there; this is what a rename does to a pin that still names a current release"
fi
# The pin is a tag and the commit that tag names, since a tag can be moved and
# what it names here is the instructions an agent follows unattended. The
# install step refuses a tag that names another commit. So the template's
# commit must be the one its tag names, and whatever moves the tag must move
# the commit with it: the release step, and the sync into a sibling.
pin_sha="$(grep -oE 'TRUST_LADDER_SKILLS_SHA: [0-9a-f]{40}' \
             skills/ktl-sidecar/templates/github/knowledge-librarian.yaml | head -1 | sed 's/.*: //')"
if [[ -z "$pin_sha" ]]; then
  err "no TRUST_LADDER_SKILLS_SHA beside the pin in the librarian template - a host would install whatever commit the tag names on the day"
elif [[ -z "$pin" ]] || ! git rev-parse -q --verify "refs/tags/$pin" >/dev/null; then
  say "skipping the pinned commit: ${pin:-the pin} is not a tag on this clone"
elif [[ "$(git rev-parse "refs/tags/$pin^{commit}")" == "$pin_sha" ]]; then
  ok "the librarian template pins the commit $pin names (${pin_sha:0:12})"
else
  err "the librarian template pins $pin with commit $pin_sha, but $pin names $(git rev-parse "refs/tags/$pin^{commit}") - the install step refuses that on every host, so move the two together"
fi
# shellcheck disable=SC2016 # the template's own $ expressions, matched as text
if grep -qF '"$TRUST_LADDER_SKILLS_SHA"' skills/ktl-sidecar/templates/github/knowledge-librarian.yaml \
   && grep -qF 'got="$(git -C "$tmp" rev-parse HEAD)"' skills/ktl-sidecar/templates/github/knowledge-librarian.yaml; then
  ok "the install step compares the commit it cloned with the pinned one"
else
  err "the librarian template's install step no longer compares the cloned commit with TRUST_LADDER_SKILLS_SHA"
fi
for mover in .github/workflows/semantic-release.yml scripts/sync-sidecar.sh; do
  if grep -qF 's/(TRUST_LADDER_SKILLS_REF: )' "$mover" && grep -qF 's/(TRUST_LADDER_SKILLS_SHA: )[0-9a-f]{40}/' "$mover"; then
    ok "$mover moves the pinned commit with the pinned tag"
  else
    err "$mover moves TRUST_LADDER_SKILLS_REF without TRUST_LADDER_SKILLS_SHA, so the install step would refuse the next pin it writes"
  fi
done

# 16. The repository's old name stays gone from anything that still speaks in
#     the present tense. It was renamed from lokf-agent-skills on 2026-09-19,
#     and a branch written before that merges without conflict: the old name
#     simply reappears, in a clone URL or an `npx skills add` path that then
#     depends on GitHub's redirect. Three files keep it on purpose, and they
#     are the ones whose job is history:
#       - CHANGELOG.md;
#       - the bundle's log.md, whose entries describe the repository as it
#         was on the day they were written, since a log that renames its own
#         past is no longer a record;
#       - one "formerly" line in docs/install.md, where the install commands
#         moved on 2026-09-19. Anywhere else is a merge that predates the rename; run
#     the same replacement over it.
say ""
say "Checking the old repository name has not come back..."
old_name="lokf-agent-skills"
# Filter in bash, not with :!pathspecs: an exclude pathspec naming a file that
# is absent or untracked (rename-plan.md, until someone commits it) makes git
# grep exit 128, and a `|| true` around it would turn that into a silent pass.
history_files=(CHANGELOG.md .lokf/knowledge/log.md rename-plan.md
               scripts/validate-repository.sh)
set +e
hits="$(git grep -lI -- "$old_name")"
grep_rc=$?
set -e
if [[ "$grep_rc" -gt 1 ]]; then
  err "git grep exited $grep_rc while looking for $old_name, so this check did not run"
else
  unexpected=()
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    skip=""
    for h in "${history_files[@]}"; do
      if [[ "$f" == "$h" ]]; then skip=1; fi
    done
    # The install page names it on one line, as history; more is a stale merge.
    if [[ "$f" == "docs/install.md" ]]; then
      if [[ "$(git grep -c -- "$old_name" -- "$f" | cut -d: -f2)" -le 1 ]]; then skip=1; fi
    fi
    if [[ -z "$skip" ]]; then unexpected+=("$f"); fi
  done <<<"$hits"
  if [[ "${#unexpected[@]}" -eq 0 ]]; then
    ok "no file outside the ones that record history reintroduces $old_name"
  else
    err "these files name $old_name again, which this repository was renamed from: ${unexpected[*]} - a branch written before the rename was merged; replace $old_name with knowledge-trust-ladder there (CHANGELOG.md, the bundle's log.md, the rename plan and one 'formerly' line in docs/install.md are the exceptions, because they record history)"
  fi
fi

# 16a. The skills and plugins took the ktl- prefix on 2026-09-22; their lokf-
#      names, and the ones before those, stay gone the same way. Only
#      CHANGELOG.md keeps them, for the releases that carried them and the one
#      line telling a host what to remove.
say ""
say "Checking the old skill and plugin names have not come back..."
old_names='lokf-(curator|docent|librarian|sidecar|registrar|enforcer|scaffolding)|LOKF (Curator|Registrar|Enforcer|Docent|Librarian|Sidecar)'
set +e
hits="$(git grep -lIE -- "$old_names")"
grep_rc=$?
set -e
if [[ "$grep_rc" -gt 1 ]]; then
  err "git grep exited $grep_rc while looking for the old skill and plugin names, so this check did not run"
else
  unexpected=()
  while IFS= read -r f; do
    [[ -z "$f" || "$f" == CHANGELOG.md || "$f" == scripts/validate-repository.sh ]] && continue
    unexpected+=("$f")
  done <<<"$hits"
  if [[ "${#unexpected[@]}" -eq 0 ]]; then
    ok "no file outside CHANGELOG.md names a lokf- skill or plugin"
  else
    err "these files name a lokf- skill or plugin: ${unexpected[*]} - use the ktl- name (only CHANGELOG.md keeps the old ones)"
  fi
fi

# 16b. LOKF is the format, its schema and its toolkit. The roles, skills and
#      repositories that keep a bundle are KTL's, and a page that names them
#      after the format leaves a reader unsure which project answers for
#      them. CHANGELOG.md and the bundle's log.md keep what was written at
#      the time, and so do the dated maintainer notes in the source map.
say ""
say "Checking that KTL's roles, skills and repositories are not named after LOKF..."
named_after_format='LOKF (roles?|skills?|repositories)([^A-Za-z]|$)'
set +e
hits="$(git grep -lIE -- "$named_after_format")"
grep_rc=$?
set -e
if [[ "$grep_rc" -gt 1 ]]; then
  err "git grep exited $grep_rc while looking for KTL's roles, skills and repositories named after LOKF, so this check did not run"
else
  unexpected=()
  while IFS= read -r f; do
    case "$f" in
      "" | CHANGELOG.md | scripts/validate-repository.sh | .lokf/knowledge/log.md | .lokf/knowledge/playbooks/knowledge-sources.md) continue ;;
    esac
    unexpected+=("$f")
  done <<<"$hits"
  if [[ "${#unexpected[@]}" -eq 0 ]]; then
    ok "no file calls a role, skill or repository of KTL a LOKF one"
  else
    err "these files call a role, skill or repository of KTL a LOKF one: ${unexpected[*]} - LOKF is the format and its toolkit; write KTL"
  fi
fi

# 17. The Microsoft 365 Copilot skills are sidecar templates, not skills of
#     this repository: one shared builder and one instructions file per
#     read-only role, the docent first. No file under templates/ may be a
#     SKILL.md, every instructions file's trust labels stay word for word the
#     docent's, this repository's own bundle builds inside Copilot's limits,
#     and one input gives one zip, since the release workflow attaches it.
say ""
say "Checking the Microsoft 365 Copilot skills build..."
m365="$templates/m365"
if [[ -n "$(find "$templates" -iname 'SKILL.md' 2>/dev/null)" ]]; then
  err "a SKILL.md sits under $templates - installers would list it as a skill; name an instructions file after the skill it builds (ktl-docent-m365.md)"
else
  ok "no SKILL.md under $templates"
fi
labels() { awk '/^## Trust labels/{f=1; next} /^## /{f=0} f && /^\|/' "$1"; }
docent_labels="$(labels skills/ktl-docent/SKILL.md)"
[[ -n "$docent_labels" ]] || err "could not find the trust-label table in skills/ktl-docent/SKILL.md"
for f in "$m365"/*.md; do
  if ! grep -q '^## Trust labels' "$f"; then
    err "$f has no '## Trust labels' section - every Copilot skill says the same words for trust as ktl-docent"
  elif [[ "$(labels "$f")" == "$docent_labels" ]]; then
    ok "$f carries ktl-docent's trust labels word for word"
  else
    err "$f's trust-label table differs from ktl-docent's - the two must say the same words"
  fi
done
m365_out="$(mktemp -d)"
# A fixed fallback, so a checkout whose history does not reach the bundle
# still builds twice from one epoch rather than from two "now"s.
m365_epoch="$(git log -1 --format=%ct -- .lokf/knowledge)"
m365_epoch="${m365_epoch:-1700000000}"
m365_build() { SOURCE_DATE_EPOCH="$m365_epoch" bash "$m365/knowledge-m365.sh" --repo-url https://github.com/noelmcloughlin/knowledge-trust-ladder --ref test .lokf/knowledge "$1" 2>&1; }
if build_log="$(m365_build "$m365_out/a")" \
   && [[ -f "$m365_out/a/ktl-docent-m365/SKILL.md" && -f "$m365_out/a/ktl-docent-m365/SNAPSHOT.md" && -f "$m365_out/a/ktl-docent-m365/knowledge/index.md" && -f "$m365_out/a/ktl-docent-m365.zip" ]]; then
  ok "knowledge-m365.sh builds ktl-docent-m365 from this repository's bundle ($(printf '%s\n' "$build_log" | grep -m1 '^built' | sed 's/.*: //'))"
else
  err "knowledge-m365.sh failed on this repository's bundle: $build_log"
fi
if command -v zip >/dev/null 2>&1; then
  if (umask 077 && TZ=Asia/Tokyo m365_build "$m365_out/b" >/dev/null) && cmp -s "$m365_out/a/ktl-docent-m365.zip" "$m365_out/b/ktl-docent-m365.zip"; then
    ok "knowledge-m365.sh gives the same zip bytes under another time zone and umask, as a release asset must"
  else
    err "knowledge-m365.sh gave different zip bytes for one input under another time zone and umask"
  fi
fi
rm -rf "${m365_out:?}"

# 18. ktl-prose's check script is exercised as the conventions script is at
#     check 11. It must report each thing it claims to see, and stay quiet on
#     what the hand passes kept. It must refuse a rewording that touches a
#     concept a person wrote or confirmed, or a byte of frontmatter, or that
#     adds a character no reader sees. It reads events the way the provenance
#     gates do, so each form they read is staged here. The skill's own pages
#     must pass the style rules they state.
say ""
say "Exercising ktl-prose's prose-check.py..."
prose_py="skills/ktl-prose/scripts/prose-check.py"
if command -v python3 >/dev/null 2>&1; then
  prose=(python3 "$prose_py")
elif command -v uv >/dev/null 2>&1; then
  prose=(uv run --quiet "$prose_py")
else
  prose=(false)
  err "neither python3 nor uv is on PATH, so prose-check.py cannot run and every expectation for it below will fail"
fi
# expect_prose <exit status> <substring> <what must hold> -- <arguments>
expect_prose() {
  local want_status="$1" want_text="$2" what="$3" out status=0
  shift 4
  out="$("${prose[@]}" "$@" 2>&1)" || status=$?
  if [[ "$status" -eq "$want_status" ]] && grep -qF -- "$want_text" <<<"$out"; then
    ok "prose-check.py: $what"
  else
    err "prose-check.py: this does not hold: $what (wanted exit $want_status and '$want_text', got exit $status and: $out)"
  fi
}
pc="$(mktemp -d)"
# The style rules, one finding each, with the line it sits on.
printf '# A page\n\nThe gate is strict - it checks every change.\n\nWe run the check in order to catch drift.\n\nThe gate reads every changed file in the bundle and then compares each one against the earlier version that the repository holds and then reports every difference that it finds to the person who asked for the check before it lets the change go any further.\n' > "$pc/bad.md"
expect_prose 1 "bad.md:3: dash:" "a dash used as punctuation is reported with its line" -- "$pc/bad.md"
expect_prose 1 "bad.md:5: words:" "a stock phrase is reported with its line" -- "$pc/bad.md"
expect_prose 1 "bad.md:7: long:" "a sentence over 40 words is reported with its line" -- "$pc/bad.md"
sed -n '7p' "$pc/bad.md" > "$pc/long.md"
expect_prose 0 "OK" "a higher --max-words lets that sentence pass" -- --max-words 60 "$pc/long.md"
# What the hand passes kept: a dash in frontmatter, a heading, a code span, a
# fenced block, a quoted string, a short emphasised label and a table cell.
# shellcheck disable=SC2016 # the backticks are Markdown, not a command
printf -- '---\ntitle: A - B\n---\n\n# A heading - with a dash\n\nRun `a - b` to subtract.\n\n```text\nx - y\n```\n\nThe button reads "X - Y" when it is ready.\n\nPick *Wrong - send back* when you are unsure.\n\n| Field | Value |\n| --- | --- |\n| a | - |\n' > "$pc/quiet.md"
expect_prose 0 "OK" "a dash is left alone in frontmatter, a heading, code, a quotation, a short label and a table cell" -- "$pc/quiet.md"
# A figure of speech is a listed word, and the same letters inside another
# word or a code span are not.
# shellcheck disable=SC2016 # the backticks are Markdown, not a command
printf '# A page\n\nThe fix lands in the next release.\n\nThe arm64 runner checks the wire-format, and `ships` is a code span.\n' > "$pc/figure.md"
expect_prose 1 'figure.md:3: words: "lands"' "a figure of speech is reported with its line" -- "$pc/figure.md"
sed -n '5p' "$pc/figure.md" > "$pc/literal.md"
expect_prose 0 "OK" "a figure's letters inside another word or a code span are left alone" -- "$pc/literal.md"
# A paragraph or a list item past 150 words is reported, and a table cell is
# not: a cell has no room to split.
para=""
for _ in $(seq 32); do para+="Each check reads one file. "; done
printf '# A page\n\n%s\n\n- %s\n' "$para" "$para" > "$pc/para.md"
expect_prose 1 "para.md:3: paragraph: 160 words in one paragraph" "a paragraph over 150 words is reported with its line" -- "$pc/para.md"
expect_prose 1 "para.md:5: paragraph: 160 words in one list item" "a list item over 150 words is reported as one" -- "$pc/para.md"
expect_prose 0 "OK" "a higher --max-paragraph lets them pass" -- --max-paragraph 200 "$pc/para.md"
printf '| a | b |\n| --- | --- |\n| %s | x |\n' "$para" > "$pc/cell.md"
expect_prose 0 "OK" "a table cell is no paragraph, however long" -- "$pc/cell.md"
# A character no reader sees is reported in code as well as in prose, and a
# rewording that adds one is refused. printf writes each from its UTF-8 bytes,
# so this file holds none.
# shellcheck disable=SC2016 # the backticks are Markdown, not a command
printf '# A page\n\nRun `a\xe2\x80\xaeb` now.\n' > "$pc/override.md"
expect_prose 1 "override.md:3: unseen: U+202E RIGHT-TO-LEFT OVERRIDE" "a right-to-left override is reported, inside a code span too" -- "$pc/override.md"
printf '# A page\n\nPlain text.\n' > "$pc/u-old.md"
printf '# A page\n\nPlain\xe2\x80\x8b text.\n' > "$pc/u-new.md"
expect_prose 1 "u-new.md:3: unseen: U+200B ZERO WIDTH SPACE is new" "a rewording that adds a zero-width space is refused" -- --before "$pc/u-old.md" "$pc/u-new.md"

# --before on plain files: wording may change, and nothing else.
plain() { printf -- '---\ntitle: %s\n---\n\n# Guide\n\n%s\n\n<!-- lokf:related -->\n[[%s]]\n<!-- /lokf:related -->\n' "$1" "$2" "$3"; }
plain Guide 'The gate checks 20 files, and [the guide](docs/guide.md) says why. It is strict.' services/orders-api > "$pc/p-old.md"
plain Guide '[The guide](docs/guide.md) says why the gate checks 20 files. The gate is strict.' services/orders-api > "$pc/p-new.md"
plain Guide 'The gate checks 21 files, and [the guide](docs/guide.md) says why. It is strict.' services/orders-api > "$pc/p-num.md"
plain Guide 'The gate checks 20 files, and [the guide](docs/other.md) says why. It is strict.' services/orders-api > "$pc/p-link.md"
plain Guide 'The gate checks 20 files, and [the guide](docs/guide.md) says why. It is strict.' services/billing > "$pc/p-rel.md"
plain Guidebook 'The gate checks 20 files, and [the guide](docs/guide.md) says why. It is strict.' services/orders-api > "$pc/p-fm.md"
expect_prose 0 "OK" "a change of wording alone passes" -- --before "$pc/p-old.md" "$pc/p-new.md"
expect_prose 1 "digits:" "a changed number is reported" -- --before "$pc/p-old.md" "$pc/p-num.md"
expect_prose 1 "link:" "a changed link target is reported" -- --before "$pc/p-old.md" "$pc/p-link.md"
expect_prose 1 "related:" "a changed wikilink in the lokf:related region is reported" -- --before "$pc/p-old.md" "$pc/p-rel.md"
expect_prose 1 "frontmatter:" "a changed frontmatter value is reported" -- --before "$pc/p-old.md" "$pc/p-fm.md"
# A program counts the words before and after, so the hand-off quotes them and
# no model works them out. What digits cannot show is a note, never a refusal:
# a day or a month written out, and a text cut by more than a fifth, which a
# reader checks for a fact that went with the words.
expect_prose 0 "OK: only the wording differs (1 file): 15 words, and the earlier text had 15" "a comparison that passes says how many words each version holds" -- --before "$pc/p-old.md" "$pc/p-new.md"
printf '# A page\n\nThe job runs on Mondays in October, and it reads every file.\n' > "$pc/d-old.md"
printf '# A page\n\nThe job runs on Tuesdays in October, and it reads every file.\n' > "$pc/d-new.md"
expect_prose 0 'date-word: the day or month "Tuesday" is new' "a changed day of the week is a note for the reader" -- --before "$pc/d-old.md" "$pc/d-new.md"
printf '# A page\n\n%s\n\n%s\n' "$para" "$para" > "$pc/s-old.md"
printf '# A page\n\n%s\n' "$para" > "$pc/s-new.md"
expect_prose 0 "shrink: 163 words, and the earlier text had 323" "a text cut by more than a fifth is a note for the reader" -- --max-paragraph 400 --before "$pc/s-old.md" "$pc/s-new.md"

# --before on concepts: a body may change only where no person vouched for it,
# and the frontmatter never. The confirmation is staged in each form the
# provenance gates read, and in one they cannot, which must fail closed.
concept() { printf -- '---\ntype: Service\nid: https://example.invalid/k/x/a\n%s---\n\n%s\n' "$1" "$2"; }
lib=$'generated:\n  by: process:ktl-librarian\n  at: "2026-09-01T05:00:00Z"\n'
body_a='The Orders API serves order data. It reads 3 tables.'
body_b='The Orders API reads 3 tables and serves order data.'
changed() {  # <exit status> <substring> <what must hold> <frontmatter before> [<frontmatter after>]
  concept "$4" "$body_a" > "$pc/c-old.md"
  concept "${5:-$4}" "$body_b" > "$pc/c-new.md"
  expect_prose "$1" "$2" "$3" -- --before "$pc/c-old.md" "$pc/c-new.md"
}
changed 0 "OK" "a reworded draft the librarian wrote passes, its frontmatter untouched" "$lib"
changed 1 "person:" "a reworded concept a person wrote is refused" $'generated:\n  by: human:ada\n  at: "2026-09-08T14:05:00Z"\n'
changed 1 "confirmed:" "a reworded concept is refused under a confirmation in a block list" "$lib"$'verified:\n  - by: human:ada\n    at: "2026-09-08T14:00:00Z"\n'
changed 1 "confirmed:" "a reworded concept is refused under a confirmation in a list at column zero" "$lib"$'verified:\n- by: human:ada\n  at: "2026-09-08T14:00:00Z"\n'
changed 1 "confirmed:" "a reworded concept is refused under a confirmation in a flow sequence" "$lib"$'verified: [{ by: process:ktl-librarian, at: "2026-09-07T05:00:00Z" }, { by: human:ada, at: "2026-09-08T14:00:00Z" }]\n'
changed 1 "confirmed:" "a reworded concept is refused under a confirmation in a bare mapping" "$lib"$'verified:\n  by: human:ada\n  at: "2026-09-08T14:00:00Z"\n'
changed 1 "unreadable:" "a reworded concept is refused when its confirmation is spelt so the gates cannot read it" "$lib"$'verified:\n  - by: !!str human:ada\n    at: "2026-09-08T14:00:00Z"\n'
changed 1 "retired:" "a reworded retired concept is refused" "$lib"$'status: deprecated\n'
changed 1 "frontmatter:" "a moved generated.at is reported" "$lib" "${lib/09-01T05/10-02T09}"
changed 0 "no generated record" "a reworded concept with no generated record passes with a note" ""

# --against HEAD, on a concept reached through the knowledge_bundle link, which
# git stores as a link and cannot show a file through.
prose_repo="$pc/repo"
mkdir -p "$prose_repo/.lokf/knowledge/x"
prosegit=(env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null git -C "$prose_repo"
  -c init.defaultBranch=main -c user.name=contract -c user.email=contract@example.invalid
  -c commit.gpgsign=false)
"${prosegit[@]}" init -q
printf -- '---\nbase_iri: https://example.invalid/k/\n---\n\n# Index\n' > "$prose_repo/.lokf/knowledge/index.md"
concept "$lib" "$body_a" > "$prose_repo/.lokf/knowledge/x/a.md"
ln -s .lokf/knowledge "$prose_repo/knowledge_bundle"
"${prosegit[@]}" add -A
"${prosegit[@]}" commit -q -m bundle
concept "$lib" "$body_b" > "$prose_repo/.lokf/knowledge/x/a.md"
expect_prose 0 "OK" "a reworded concept reached through the knowledge_bundle link passes against HEAD" -- --against HEAD "$prose_repo/knowledge_bundle/x/a.md"
concept "$lib" "${body_b/3 tables/4 tables}" > "$prose_repo/.lokf/knowledge/x/a.md"
expect_prose 1 "digits:" "a changed number is reported against HEAD" -- --against HEAD "$prose_repo/knowledge_bundle/x/a.md"
concept "$lib" "$body_a" > "$prose_repo/.lokf/knowledge/x/new.md"
expect_prose 1 "baseline:" "a file git does not hold yet cannot be proved against HEAD" -- --against HEAD "$prose_repo/.lokf/knowledge/x/new.md"

# --bundle: one file for each verdict, in the order the skill's table gives.
mkdir -p "$pc/b/k/x"
printf -- '---\nbase_iri: https://example.invalid/k/\n---\n\n# Index\n' > "$pc/b/k/index.md"
printf '# Change Log\n\n## 2026-09-15\n\n* **A**: b - c.\n' > "$pc/b/k/log.md"
concept $'generated:\n  by: human:ada\n  at: "2026-09-08T14:05:00Z"\n' "$body_a" > "$pc/b/k/x/a-person.md"
concept "$lib"$'verified: [{ by: human:ada, at: "2026-09-08T14:00:00Z" }]\n' "$body_a" > "$pc/b/k/x/b-confirmed.md"
concept "$lib"$'status: deprecated\n' "$body_a" > "$pc/b/k/x/c-retired.md"
printf -- '---\ntype: Service\n\nThe block above never closes.\n' > "$pc/b/k/x/d-unreadable.md"
concept "" "$body_a" > "$pc/b/k/x/e-unrecorded.md"
concept "$lib" "$body_a" > "$pc/b/k/x/f-rewrite.md"
verdicts="$("${prose[@]}" --bundle "$pc/b/k" 2>&1 || true)"
for want in "index.md: skip: reserved file" "log.md: skip: reserved file" "a-person.md: skip: written by a person" \
            "b-confirmed.md: skip: confirmed by a person" "c-retired.md: skip: retired" \
            "d-unreadable.md: skip: frontmatter the script cannot read" "e-unrecorded.md: skip: no record of who wrote it" \
            "f-rewrite.md: rewrite"; do
  if grep -qF -- "$want" <<<"$verdicts"; then
    ok "prose-check.py --bundle gives: $want"
  else
    err "prose-check.py --bundle did not give '$want' on a bundle staged for it: $verdicts"
  fi
done
expect_prose 0 "OK" "a reserved bundle file is not held to the style rules" -- "$pc/b/k/log.md"
rm -rf "${pc:?}"

expect_prose 2 "usage" "no argument is a usage error" --
expect_prose 0 "rewrite" "this repository's own bundle is given its verdicts" -- --bundle .lokf/knowledge
expect_prose 0 "OK" "the skill's own pages pass the style rules they state" -- skills/ktl-prose/SKILL.md skills/ktl-prose/references/*.md

# 19. knowledge-apply.sh is the pen, the librarian's only way to write the
#     bundle, so it has to earn the refusals the skill promises:
#       - nothing is written unless every operation passes;
#       - a human: actor anywhere, a rewrite of text a person wrote and the
#         deletion of a concept a person confirmed are refused;
#       - a person's own verified event survives a patch;
#       - a person's record is the same after a patch as before, whatever the
#         operations were;
#       - a frontmatter value the operation did not name keeps the text the
#         file held, where YAML would read it as a number, a boolean or a time;
#       - a reader's question reaches the ledger, and a hand-off line its
#         file, with no character a reader cannot see;
#       - the index bullets and the log heading are kept in step;
#       - the lokf:related block survives a rewrite;
#       - a handled feedback entry leaves feedback.md for the ledger, with the
#         reader's question in a code span;
#       - a dry run writes nothing;
#       - a quoted timestamp keeps its double quotes;
#       - reindex re-derives a bullet without touching the concept;
#       - resolve withdraws the librarian's own question and never a person's
#         note;
#       - a root index shaped by hand keeps its shape;
#       - the hand-off reaches the file --handoff names as plain single lines,
#         and never the bundle;
#       - --format prints the block patch.md shows.
say ""
say "Exercising knowledge-apply.sh..."
apply="$repo_root/$templates/scripts/knowledge-apply.sh"
ka="$(mktemp -d)"; kb="$ka/.lokf/knowledge"; mkdir -p "$kb/playbooks"
printf '%s\n' '---' 'base_iri: https://acme.example/knowledge/' '---' '' '# Acme' '' '# Playbooks' '' \
  '* [Draft](playbooks/draft.md) - a draft.' '* [Confirmed](playbooks/confirmed.md) - confirmed.' '* [Authored](playbooks/authored.md) - authored.' > "$kb/index.md"
printf '%s\n' '# Playbooks' '' '* [Draft](draft.md) - a draft.' '* [Confirmed](confirmed.md) - confirmed.' '* [Authored](authored.md) - authored.' > "$kb/playbooks/index.md"
printf '%s\n' '---' 'type: Playbook' 'id: https://acme.example/knowledge/playbooks/draft' 'title: Draft' 'description: a draft.' \
  'generated:' '  by: process:ktl-librarian' '  at: "2026-01-01T00:00:00Z"' 'status: draft' '---' '' '# Overview' '' 'The old text.' > "$kb/playbooks/draft.md"
printf '%s\n' '---' 'type: Playbook' 'id: https://acme.example/knowledge/playbooks/confirmed' 'title: Confirmed' 'description: confirmed.' \
  'generated:' '  by: process:ktl-librarian' '  at: "2026-01-01T00:00:00Z"' 'verified:' '  - by: human:ada' '    at: "2026-02-02T00:00:00Z"' '---' '' \
  '# Overview' '' 'Confirmed text.' '' '<!-- lokf:related -->' '#how-to' '<!-- /lokf:related -->' > "$kb/playbooks/confirmed.md"
printf '%s\n' '---' 'type: Playbook' 'id: https://acme.example/knowledge/playbooks/authored' 'title: Authored' 'description: authored.' \
  'generated:' '  by: human:ada' '  at: "2026-01-01T00:00:00Z"' 'verified:' '  - by: human:ada' '    at: "2026-01-01T00:00:00Z"' '---' '' '# Overview' '' 'Written by a person.' > "$kb/playbooks/authored.md"
printf '%s\n' '# Change Log' '' '## 2020-01-01' '' '* **Old**: an old line.' > "$kb/log.md"
printf '%s\n' '# Reader feedback for the librarian' '' 'Newest first.' '' '## 2026-03-03' '' '- **Miss** - Q: "where?" Answered from here. - docent' > "$ka/.lokf/feedback.md"
kpatch="$ka/.lokf/patch.yaml"
ksum() { (cd "$ka" && find . -type f ! -name patch.yaml -exec md5sum {} + | sort | md5sum); }
apply_refuses() {  # <what> <expected finding>; the patch file is already in place
  local before out rc; before="$(ksum)"
  set +e; out="$(bash "$apply" --root "$ka" "$kpatch" 2>&1)"; rc=$?; set -e
  if [[ "$rc" == 1 ]] && grep -qF -- "$2" <<<"$out" && [[ "$(ksum)" == "$before" ]]; then
    ok "knowledge-apply.sh refuses $1 and writes nothing"
  else
    err "knowledge-apply.sh did not refuse $1 cleanly (exit $rc): $out"
  fi
}
cat > "$kpatch" <<'EOF'
ops:
  - op: create
    path: playbooks/new.md
    frontmatter: {type: Playbook, title: New, description: brand new., resource: README.md}
    body: "# Overview\n\nBrand new.\n"
  - op: patch
    path: playbooks/draft.md
    edits:
      - replace: {target: "The old text.", content: "The new text."}
    set: {description: a better draft.}
    log: "the text moved on"
    from_feedback: '- **Miss** - Q: "where?" Answered from here. - docent'
    asked: "where is `it`?"
  - op: patch
    path: playbooks/confirmed.md
    edits:
      - append: {content: "A new paragraph."}
    log: "**Changed**: one more paragraph."
  - op: question
    path: playbooks/authored.md
    text: is this still right?
EOF
kday="$(date -u +%Y-%m-%d)"
if out="$(bash "$apply" --root "$ka" "$kpatch" 2>&1)" && [[ ! -e "$kpatch" ]]; then
  ok "knowledge-apply.sh applies a valid patch and removes the patch file"
else
  err "knowledge-apply.sh failed on a valid patch: $out"
fi
knew="$kb/playbooks/new.md"
if [[ -f "$knew" ]] && grep -q '^status: draft$' "$knew" && grep -q '^id: https://acme.example/knowledge/playbooks/new$' "$knew" \
   && grep -qE "^  at: ['\"]${kday}T[0-9:]+Z['\"]$" "$knew" && grep -q '^  by: process:ktl-librarian$' "$knew" \
   && grep -qF '* [New](playbooks/new.md) - brand new.' "$kb/index.md" && grep -qF '* [New](new.md) - brand new.' "$kb/playbooks/index.md"; then
  ok "create mints the id, stamps generated from the clock, starts as a draft, and adds both index bullets"
else
  err "create did not produce the expected concept and bullets: $(head -12 "$knew" 2>/dev/null | tr '\n' '|')"
fi
if grep -q 'The new text.' "$kb/playbooks/draft.md" && ! grep -q 'The old text.' "$kb/playbooks/draft.md" \
   && ! grep -q '2026-01-01T00:00:00Z' "$kb/playbooks/draft.md" \
   && grep -qF '* [Draft](playbooks/draft.md) - a better draft.' "$kb/index.md" && grep -qF '* [Draft](draft.md) - a better draft.' "$kb/playbooks/index.md"; then
  ok "patch replaces the one target, restamps generated, and rewrites both bullets from the new description"
else
  err "patch did not edit the draft as expected: $(head -14 "$kb/playbooks/draft.md" | tr '\n' '|')"
fi
if grep -q 'A new paragraph.' "$kb/playbooks/confirmed.md" && grep -q '^ *- by: human:ada$' "$kb/playbooks/confirmed.md" \
   && grep -qE '^ +at: "2026-02-02T00:00:00Z"$' "$kb/playbooks/confirmed.md" \
   && grep -q 'Edited since a person confirmed it' "$kb/log.md"; then
  ok "patch on a confirmed concept keeps the person's event, with its double quotes, and says so in the log"
else
  err "patch on a confirmed concept lost the person's event or the log note: $(tr '\n' '|' < "$kb/playbooks/confirmed.md")"
fi
if grep -q '^status: draft$' "$kb/playbooks/authored.md" && grep -q "^- ${kday}, process:ktl-librarian: is this still right?$" "$kb/playbooks/authored.md" \
   && grep -q '^  by: human:ada$' "$kb/playbooks/authored.md" && grep -q 'Written by a person.' "$kb/playbooks/authored.md"; then
  ok "question adds the curator-shaped bullet with this run's actor and touches neither text nor generated"
else
  err "question did not leave the authored concept as expected: $(tr '\n' '|' < "$kb/playbooks/authored.md")"
fi
if [[ "$(grep -m1 '^## ' "$kb/log.md")" == "## $kday" ]] && grep -q '^## 2020-01-01$' "$kb/log.md" \
   && grep -q '^\* \*\*From reader feedback\*\*: the text moved on' "$kb/log.md" && grep -q '^\* \*\*Added\*\*: New' "$kb/log.md" \
   && ! grep -q 'where?' "$ka/.lokf/feedback.md" && ! grep -q '^## 2026-03-03$' "$ka/.lokf/feedback.md"; then
  ok "the log gains today's heading above the old one, and the handled feedback entry and its emptied day are gone"
else
  err "the log or the feedback file is not as expected: $(head -8 "$kb/log.md" | tr '\n' '|') // $(tr '\n' '|' < "$ka/.lokf/feedback.md")"
fi
# The entry is not lost: it leaves feedback.md for the ledger, as the day, the
# kind and the concept, with the reader's question in a code span whose
# backticks are gone, so none of it renders as Markdown. And the reader's
# words stay out of log.md, which the curator opens.
# shellcheck disable=SC2016 # the backticks are a Markdown code span, not a command
if [[ "$(head -1 "$ka/.lokf/questions.md" 2>/dev/null)" == "# Questions readers asked" ]] \
   && grep -qxF -- "- $kday Miss playbooks/draft.md: \`where is 'it'?\`" "$ka/.lokf/questions.md" && ! grep -q 'where is' "$kb/log.md"; then
  ok "a handled feedback entry lands in the ledger with its question in a code span, and the question stays out of the log"
else
  err "the ledger is not as expected: $(tr '\n' '|' < "$ka/.lokf/questions.md" 2>/dev/null)"
fi
cat > "$kpatch" <<'EOF'
ops:
  - op: rewrite
    path: playbooks/confirmed.md
    body: "# Overview\n\nRewritten from the source.\n"
    log: "rewritten from the source"
EOF
if bash "$apply" --root "$ka" "$kpatch" >/dev/null 2>&1 && grep -q 'Rewritten from the source.' "$kb/playbooks/confirmed.md" \
   && grep -q '<!-- lokf:related -->' "$kb/playbooks/confirmed.md" && [[ "$(grep -c "^## $kday$" "$kb/log.md")" == 1 ]]; then
  ok "rewrite carries the lokf:related block over, and a second run today reuses the heading"
else
  err "rewrite lost the lokf:related block or doubled today's heading: $(tr '\n' '|' < "$kb/playbooks/confirmed.md")"
fi
cat > "$kpatch" <<'EOF'
ops:
  - op: delete
    path: playbooks/draft.md
    log: "**Removal**: Draft; its source is gone."
EOF
if bash "$apply" --root "$ka" "$kpatch" >/dev/null 2>&1 && [[ ! -e "$kb/playbooks/draft.md" ]] \
   && ! grep -q 'draft.md' "$kb/index.md" && ! grep -q 'draft.md' "$kb/playbooks/index.md" && grep -q '^\* \*\*Removal\*\*: Draft' "$kb/log.md"; then
  ok "delete removes a draft, both its bullets, and logs why"
else
  err "delete did not remove the draft and its bullets: $(grep -n draft "$kb/index.md" "$kb/playbooks/index.md" | tr '\n' '|')"
fi
printf '%s\n' 'by: human:ada' 'ops:' '  - {op: recheck, path: playbooks/new.md}' > "$kpatch"
apply_refuses "a human: actor anywhere in the file" "names a human: actor"
printf '%s\n' 'ops:' '  - {op: delete, path: playbooks/confirmed.md, log: gone}' > "$kpatch"
apply_refuses "deleting a concept a person confirmed" "a person confirmed this concept"
printf '%s\n' 'ops:' '  - {op: patch, path: playbooks/authored.md, edits: [{append: {content: x}}], log: x}' > "$kpatch"
apply_refuses "patching text a person wrote" "a person wrote this text"
printf '%s\n' 'ops:' '  - {op: patch, path: playbooks/new.md, set: {status: stable}, log: x}' > "$kpatch"
apply_refuses "setting status" "set may not touch status"
printf '%s\n' 'ops:' '  - {op: create, path: playbooks/other.md, frontmatter: {type: Playbook, title: Other, description: d.}, body: b}' \
               '  - {op: patch, path: playbooks/new.md, edits: [{replace: {target: "not there", content: x}}], log: x}' > "$kpatch"
apply_refuses "a missing target, with a valid create beside it" "must occur exactly once"
if [[ ! -e "$kb/playbooks/other.md" ]]; then ok "a refused file lands none of its operations"; else err "a refused file still created playbooks/other.md"; fi
printf '%s\n' 'ops:' '  - {op: create, path: playbooks/dry.md, frontmatter: {type: Playbook, title: Dry, description: d.}, body: b}' > "$kpatch"
if out="$(bash "$apply" --root "$ka" --dry-run "$kpatch" 2>&1)" && grep -q 'would write' <<<"$out" && [[ ! -e "$kb/playbooks/dry.md" && -e "$kpatch" ]]; then
  ok "a dry run reports what it would write, writes nothing, and keeps the patch file"
else
  err "the dry run wrote something or lost the patch file: $out"
fi
# The hand-off: lines for the reviewer, which never reach the bundle. The pen
# accepts each only as one line of printable text with no backtick. It writes
# them to the file --handoff names, empties that file when a patch has none,
# and refuses a hand-off that is not a short list of short lines.
khand="$ka/handoff.txt"
cat > "$kpatch" <<'EOF'
ops:
  - {op: recheck, path: playbooks/new.md}
handoff:
  - "two concepts came back for the same `date`;\u200b the rule\tneeds a look"
  - "a source did not answer"
EOF
printf 'planted by the agent\n' > "$khand"
if out="$(bash "$apply" --root "$ka" --handoff "$khand" "$kpatch" 2>&1)" \
   && [[ "$(cat "$khand")" == $'two concepts came back for the same \'date\'; the rule needs a look\na source did not answer' ]] \
   && grep -qxF '  a source did not answer' <<<"$out" && ! grep -rq 'did not answer' "$kb"; then
  ok "the hand-off lands in the file --handoff names as plain single lines, is printed, and stays out of the bundle"
else
  err "the hand-off was not written as expected: $out // $(tr '\n' '|' < "$khand")"
fi
printf 'planted by the agent\n' > "$khand"
printf '%s\n' 'ops:' '  - {op: recheck, path: playbooks/new.md}' > "$kpatch"
if bash "$apply" --root "$ka" --handoff "$khand" "$kpatch" >/dev/null 2>&1 && [[ ! -s "$khand" ]]; then
  ok "a patch with no hand-off empties the file --handoff names, so nothing planted there survives"
else
  err "a patch with no hand-off left the --handoff file holding: $(cat "$khand")"
fi
rm -f "$khand"
{ printf '%s\n' 'ops:' '  - {op: recheck, path: playbooks/new.md}' 'handoff:'; for i in 1 2 3 4 5 6 7 8 9 10 11; do printf '  - "line %s"\n' "$i"; done; } > "$kpatch"
apply_refuses "a hand-off of more than ten lines" "a reviewer gets at most 10"
printf '%s\n' 'ops:' '  - {op: recheck, path: playbooks/new.md}' "handoff: [\"$(printf 'x%.0s' $(seq 301))\"]" > "$kpatch"
apply_refuses "a hand-off line longer than 300 characters" "handoff line 1 is 301 characters"
printf '%s\n' 'ops:' '  - {op: recheck, path: playbooks/new.md}' 'handoff: "one line, not a list"' > "$kpatch"
apply_refuses "a hand-off that is not a list" "handoff is a list of lines"
printf '%s\n' 'ops:' '  - {op: recheck, path: playbooks/new.md}' 'handoff: ["\u200b\u202e"]' > "$kpatch"
apply_refuses "a hand-off line of invisible characters alone" "handoff line 1 holds no printable text"
sed -i 's|^\* \[New\](playbooks/new.md) - brand new.$|* [New](playbooks/new.md) - stale.|' "$kb/index.md"
kbefore="$(md5sum < "$kb/playbooks/new.md")"
printf '%s\n' 'ops:' '  - {op: reindex, path: playbooks/new.md}' > "$kpatch"
if bash "$apply" --root "$ka" "$kpatch" >/dev/null 2>&1 && grep -qF '* [New](playbooks/new.md) - brand new.' "$kb/index.md" \
   && [[ "$(md5sum < "$kb/playbooks/new.md")" == "$kbefore" ]] && ! grep -q 'brand new' "$kb/log.md"; then
  ok "reindex restores a drifted bullet from the frontmatter and touches neither the concept nor the log"
else
  err "reindex did not restore the bullet, or touched the concept or the log: $(grep -n 'New' "$kb/index.md" "$kb/log.md" | tr '\n' '|')"
fi
# resolve withdraws a question the librarian itself asked and takes the
# heading with its last question; the person's text, their generated record
# and the status stay as they were. A person's note is never the pen's to
# clear, a concept carrying one is never the pen's to delete, and a second
# ledger line joins the first rather than replacing it.
printf '%s\n' 'ops:' '  - {op: resolve, path: playbooks/authored.md, target: "still right", log: "the source settles it"}' > "$kpatch"
if bash "$apply" --root "$ka" "$kpatch" >/dev/null 2>&1 && ! grep -q 'Open questions' "$kb/playbooks/authored.md" && ! grep -q 'still right' "$kb/playbooks/authored.md" \
   && grep -q '^status: draft$' "$kb/playbooks/authored.md" && grep -q '^  by: human:ada$' "$kb/playbooks/authored.md" && grep -q 'Written by a person.' "$kb/playbooks/authored.md" \
   && grep -q '^\* \*\*Resolved\*\*: the source settles it' "$kb/log.md"; then
  ok "resolve withdraws the librarian's own question and its heading, and leaves the text, generated and status alone"
else
  err "resolve did not withdraw the question cleanly: $(tr '\n' '|' < "$kb/playbooks/authored.md")"
fi
printf '\n## Open questions\n\n- 2026-03-03, human:ada: send this back\n' >> "$kb/playbooks/new.md"
printf '%s\n' 'ops:' '  - {op: resolve, path: playbooks/new.md, target: "send this back", log: x}' > "$kpatch"
apply_refuses "resolving a note a person left" "is not one process:ktl-librarian asked"
printf '%s\n' 'ops:' '  - {op: delete, path: playbooks/new.md, log: gone}' > "$kpatch"
apply_refuses "deleting a concept a person left a note on" "a person left a note on this concept"
printf '%s\n' 'ops:' '  - {op: patch, path: playbooks/new.md, edits: [{append: {content: x}}], log: x, asked: "why?"}' > "$kpatch"
apply_refuses "a reader's question with no feedback entry behind it" "asked goes with from_feedback"
printf '%s\n' '# Reader feedback for the librarian' '' '## 2026-03-04' '' '- **Disagreement** - it says one thing. - docent' > "$ka/.lokf/feedback.md"
printf '%s\n' 'ops:' "  - {op: patch, path: playbooks/new.md, edits: [{append: {content: fixed}}], log: fixed, from_feedback: '- **Disagreement** - it says one thing. - docent'}" > "$kpatch"
if bash "$apply" --root "$ka" "$kpatch" >/dev/null 2>&1 && grep -qxF -- "- $kday Disagreement playbooks/new.md" "$ka/.lokf/questions.md" \
   && [[ "$(grep -c '^- ' "$ka/.lokf/questions.md")" == 2 ]] && [[ "$(grep -c '^# Questions readers asked$' "$ka/.lokf/questions.md")" == 1 ]]; then
  ok "a second handled entry joins the ledger under the first, with no question where the entry held none"
else
  err "the ledger did not grow as expected: $(tr '\n' '|' < "$ka/.lokf/questions.md" 2>/dev/null)"
fi
# A person's record is the same after a patch as before, whatever the
# operations were. The pen compares each concept it is about to write with the
# file it read. So these are refused, though each operation is one it allows:
#   - a rewrite whose body brings its own `## Open questions` section, which
#     would replace the one that holds a person's note;
#   - a note in a person's name spelt with an escaped line break, which no
#     scan of the patch file's lines can see, in a new concept's body and in
#     an appended paragraph;
#   - a delete behind a second `## Open questions` heading placed above the
#     real one.
# A rewrite with no such section of its own still carries the note over.
cat > "$kpatch" <<'EOF'
ops:
  - op: rewrite
    path: playbooks/new.md
    body: "# Overview\n\nRewritten.\n\n## Open questions\n\n- 2026-03-04, process:ktl-librarian: mine now\n"
    log: rewritten
EOF
apply_refuses "a rewrite whose own open questions would replace a person's note" "playbooks/new.md: this patch would remove a note a person left (human:ada, 2026-03-03)"
cat > "$kpatch" <<'EOF'
ops:
  - op: create
    path: playbooks/planted.md
    frontmatter: {type: Playbook, title: Planted, description: planted.}
    body: "# Overview\n\nText.\n\n## Open questions\n\n- 2026-03-04, human:ada: looks right to me\n"
EOF
apply_refuses "a person's note spelt with an escaped line break in a new concept" "playbooks/planted.md: this patch would add a note in a person's name (human:ada, 2026-03-04)"
printf '%s\n' 'ops:' '  - {op: patch, path: playbooks/confirmed.md, edits: [{append: {content: "## Open questions\n\n- 2026-03-04, human:ada: I checked this\n"}}], log: x}' > "$kpatch"
apply_refuses "a person's note spelt with an escaped line break in an appended paragraph" "playbooks/confirmed.md: this patch would add a note in a person's name (human:ada, 2026-03-04)"
cat > "$kpatch" <<'EOF'
ops:
  - {op: patch, path: playbooks/new.md, edits: [{append: {content: "## Open questions\n\nnothing here"}}], log: x}
  - {op: delete, path: playbooks/new.md, log: gone}
EOF
apply_refuses "a delete behind a second open-questions heading placed above a person's note" "playbooks/new.md: this patch would remove a note a person left (human:ada, 2026-03-03)"
printf '%s\n' 'ops:' '  - {op: rewrite, path: playbooks/new.md, body: "# Overview\n\nRewritten from the source.\n", log: rewritten}' > "$kpatch"
if bash "$apply" --root "$ka" "$kpatch" >/dev/null 2>&1 && grep -q 'Rewritten from the source.' "$kb/playbooks/new.md" \
   && grep -qxF -- '- 2026-03-03, human:ada: send this back' "$kb/playbooks/new.md"; then
  ok "a rewrite with no open-questions section of its own carries a person's note over"
else
  err "a rewrite lost a person's note, or was refused: $(tr '\n' '|' < "$kb/playbooks/new.md")"
fi
# A value the operation did not name goes back as the file held it. YAML reads
# each of these as a number, a boolean or a time, and written back from that
# they would read 1.1, 45000, true and, on a person's own event, 42798 and a
# time in another shape, which the gate reads as a changed confirmation. An
# all-digit commit hash given as `revision` is text too, and is written quoted.
printf '%s\n' '---' 'type: Playbook' 'id: https://acme.example/knowledge/playbooks/kept' 'title: Kept' 'description: kept.' \
  'version: 1.10' 'window: 12:30:00' 'flag: yes' 'generated:' '  by: process:ktl-librarian' '  at: "2026-01-01T00:00:00Z"' \
  'verified:' '  - by: human:ada' '    at: 2026-02-02T10:00:00Z' '    revision: 0123456' '---' '' '# Overview' '' 'Text.' > "$kb/playbooks/kept.md"
printf '%s\n' 'ops:' '  - {op: patch, path: playbooks/kept.md, edits: [{append: {content: more}}], set: {build: 1.20}, revision: 1234567, log: x}' > "$kpatch"
if out="$(bash "$apply" --root "$ka" "$kpatch" 2>&1)"; then
  for want in 'version: 1.10' 'window: 12:30:00' 'flag: yes' 'build: 1.20' '- by: human:ada' '  at: 2026-02-02T10:00:00Z' '  revision: 0123456' '  revision: "1234567"'; do
    if grep -qxF -- "$want" "$kb/playbooks/kept.md"; then ok "the pen writes a value back as it was read: $want"; else err "the pen did not keep '$want': $(tr '\n' '|' < "$kb/playbooks/kept.md")"; fi
  done
else
  err "knowledge-apply.sh failed on a concept holding values YAML reads as numbers and times: $out"
fi
# A reader's question and a hand-off line are shown to a person, in a code
# span and a code block. Neither keeps a character a reader cannot see, by
# Unicode's own categories: a zero-width space and a right-to-left override,
# and also an Arabic letter mark, a soft hyphen and a tag character, which a
# list of ranges left out. The patch spells each as an escape, so this file
# holds none.
printf '%s\n' '# Reader feedback for the librarian' '' '## 2026-03-05' '' '- **Miss** - Q: "hidden?" - docent' > "$ka/.lokf/feedback.md"
cat > "$kpatch" <<'EOF'
ops:
  - op: patch
    path: playbooks/kept.md
    edits:
      - append: {content: "and more"}
    log: fixed
    from_feedback: '- **Miss** - Q: "hidden?" - docent'
    asked: "is\u200b it\u202e hidden\u061c from\u00ad a\U000E0041 reader\uFEFF?"
handoff:
  - "a\u061c line\u00ad with\U000E0041 more\uFFF9 than\u180e a\u200b list"
EOF
# shellcheck disable=SC2016 # the backticks are a Markdown code span, not a command
if bash "$apply" --root "$ka" --handoff "$khand" "$kpatch" >/dev/null 2>&1 \
   && grep -qxF -- "- $kday Miss playbooks/kept.md: \`is it hidden from a reader?\`" "$ka/.lokf/questions.md" \
   && [[ "$(cat "$khand")" == "a line with more than a list" ]]; then
  ok "a reader's question and a hand-off line lose every character a reader cannot see, a bidirectional mark and a tag character included"
else
  err "an unseen character reached the ledger or the hand-off: $(tail -1 "$ka/.lokf/questions.md" | od -c | head -5) // $(od -c "$khand" | head -3)"
fi
rm -f "$khand"
printf '%s\n' '# Reader feedback for the librarian' '' '## 2026-03-05' '' '- **Miss** - Q: "unseen?" - docent' > "$ka/.lokf/feedback.md"
printf '%s\n' 'ops:' "  - {op: patch, path: playbooks/kept.md, edits: [{append: {content: again}}], log: fixed, from_feedback: '- **Miss** - Q: \"unseen?\" - docent', asked: \"\\u200b\\u202e\"}" > "$kpatch"
apply_refuses "a reader's question of invisible characters alone" "asked holds no printable text"
# One run handles at most ten reader entries, which the skill states and the
# pen holds it to: an eleventh waits for the next run.
{ printf '%s\n' '# Reader feedback for the librarian' '' '## 2026-03-05' ''; for i in 1 2 3 4 5 6 7 8 9 10 11; do printf -- '- **Miss** - entry %s - docent\n' "$i"; done; } > "$ka/.lokf/feedback.md"
{ printf '%s\n' 'ops:'; for i in 1 2 3 4 5 6 7 8 9 10 11; do printf "  - {op: patch, path: playbooks/kept.md, edits: [{append: {content: 'line %s'}}], log: fixed, from_feedback: '- **Miss** - entry %s - docent'}\n" "$i" "$i"; done; } > "$kpatch"
apply_refuses "a patch that handles eleven reader entries" "one run handles at most 10"
sed -i '$d' "$kpatch"
if bash "$apply" --root "$ka" "$kpatch" >/dev/null 2>&1 && [[ "$(grep -c '^- \*\*' "$ka/.lokf/feedback.md")" == 1 ]]; then
  ok "a patch that handles ten reader entries is applied, and the eleventh waits in feedback.md"
else
  err "a patch that handles ten reader entries was not applied as expected: $(grep -c '^- \*\*' "$ka/.lokf/feedback.md") entries left"
fi
rm -rf "$ka"
# A root index a person shaped by hand keeps its shape. Its sections may be
# `##` headings, and a line may list several concepts or name one in a
# sentence. The pen:
#   - rewrites every line that holds one concept's link alone and nothing else;
#   - files a new bullet under the folder's heading at whatever level it has,
#     or in the section that links the folder's index.md, but never under the
#     title;
#   - on delete, takes the link out of a list of links and leaves no double
#     blank line;
#   - refuses a delete that would reword a sentence.
ka="$(mktemp -d)"; kb="$ka/.lokf/knowledge"; kpatch="$ka/.lokf/patch.yaml"; mkdir -p "$kb/glossary" "$kb/org"
kvocab='The vocabulary ([index](glossary/index.md)): [Risk](glossary/risk.md), [Taxonomy](glossary/taxonomy.md)'
kmulti='* [Acme Corp](org/acme.md), [Widget Co](org/widget.md)'
printf '%s\n' '---' 'base_iri: https://acme.example/knowledge/' '---' '' '# Acme' '' 'Start at the [explanations](explanation/index.md).' '' \
  '## Start here' '' '* [Risk](glossary/risk.md) - stale.' '' '## Glossary' '' "$kvocab" '' \
  '## Organizations' '' '([index](org/index.md))' '' "$kmulti" '' \
  'Start with [Model](glossary/model.md), then read the rest.' 'Read [Harm](glossary/harm.md) first.' > "$kb/index.md"
printf '%s\n' '# Glossary' '' '* [Risk](risk.md) - a harm.' '* [Taxonomy](taxonomy.md) - a catalogue of risks.' '* [Model](model.md) - the model.' \
  '* [Harm](harm.md) - a harm done.' '' '## See also' '' '* [Risk](risk.md) - a harm.' > "$kb/glossary/index.md"
printf '%s\n' '# Org' '' '* [Acme Corp](acme.md) - stale.' '' '## Makers' '' '* [Widget Co](widget.md) - a maker of widgets.' > "$kb/org/index.md"
for kc in glossary/risk:Risk:'a named harm.' glossary/taxonomy:Taxonomy:'a catalogue of risks.' glossary/model:Model:'the model.' \
          glossary/harm:Harm:'a harm done.' org/acme:'Acme Corp':'a company.' org/widget:'Widget Co':'a maker of widgets.'; do
  IFS=: read -r kpath ktitle kdesc <<<"$kc"
  printf '%s\n' '---' 'type: Reference' "id: https://acme.example/knowledge/$kpath" "title: $ktitle" "description: $kdesc" \
    'generated:' '  by: process:ktl-librarian' '  at: "2026-01-01T00:00:00Z"' 'status: draft' '---' '' '# Overview' '' 'Text.' > "$kb/$kpath.md"
done
printf '%s\n' '# Change Log' > "$kb/log.md"
ksection() { awk -v h="$1" '$0 == h {s = 1; next} /^#/ {s = 0} s' "$kb/index.md"; }  # the lines under one root heading
printf '%s\n' 'ops:' '  - {op: reindex, path: org/acme.md}' '  - {op: reindex, path: glossary/risk.md}' > "$kpatch"
if bash "$apply" --root "$ka" "$kpatch" >/dev/null 2>&1 && grep -qxF "$kvocab" "$kb/index.md" && grep -qxF "$kmulti" "$kb/index.md" \
   && ksection '## Start here' | grep -qxF '* [Risk](glossary/risk.md) - a named harm.' \
   && [[ "$(grep -cxF '* [Risk](risk.md) - a named harm.' "$kb/glossary/index.md")" == 2 ]] \
   && grep -qxF '* [Acme Corp](acme.md) - a company.' "$kb/org/index.md" \
   && [[ "$(grep -cE '^#+ Glossary$' "$kb/index.md")" == 1 ]] && ! grep -qE '^#+ Org$' "$kb/index.md"; then
  ok "reindex rewrites every line that holds the concept's link alone, and leaves a root line that lists it among others as it was"
else
  err "reindex rewrote a hand-shaped root index, or missed a bullet: $(tr '\n' '|' < "$kb/index.md") // $(tr '\n' '|' < "$kb/glossary/index.md")"
fi
cat > "$kpatch" <<'EOF'
ops:
  - {op: create, path: glossary/crosswalk.md, frontmatter: {type: Reference, title: Crosswalk, description: a mapping across taxonomies.}, body: "# Overview\n\nA mapping.\n"}
  - {op: create, path: org/newco.md, frontmatter: {type: Reference, title: Newco, description: a new company.}, body: "# Overview\n\nNew.\n"}
  - {op: create, path: explanation/why.md, frontmatter: {type: Explanation, title: Why, description: why it exists.}, body: "# Overview\n\nBecause.\n"}
  - {op: create, path: policies/retention.md, frontmatter: {type: Policy, title: Retention, description: how long rows are kept.}, body: "# Overview\n\nThirteen months.\n"}
EOF
if bash "$apply" --root "$ka" "$kpatch" >/dev/null 2>&1 && [[ "$(grep -cE '^#+ Glossary$' "$kb/index.md")" == 1 ]] \
   && ksection '## Glossary' | grep -qxF '* [Crosswalk](glossary/crosswalk.md) - a mapping across taxonomies.' \
   && grep -qx '## Organizations' "$kb/index.md" && [[ -z "$(grep -B1 -x '## Organizations' "$kb/index.md" | head -1)" ]] \
   && ksection '## Organizations' | grep -qxF '* [Newco](org/newco.md) - a new company.' && ! grep -qE '^#+ Org$' "$kb/index.md" \
   && ksection '## Explanation' | grep -qxF '* [Why](explanation/why.md) - why it exists.' \
   && ksection '## Policies' | grep -qxF '* [Retention](policies/retention.md) - how long rows are kept.' && ! grep -qx '# Policies' "$kb/index.md"; then
  ok "create files a bullet under the folder's heading at any level, or in the section that links the folder's index.md, and otherwise opens a section at the root's level"
else
  err "create misplaced a bullet in a hand-shaped root index: $(tr '\n' '|' < "$kb/index.md")"
fi
cat > "$kpatch" <<'EOF'
ops:
  - {op: delete, path: glossary/taxonomy.md, log: "**Removal**: Taxonomy; its source is gone."}
  - {op: delete, path: org/widget.md, log: "**Removal**: Widget Co; its source is gone."}
EOF
knodouble() { awk 'NR > 1 && prev == "" && $0 == "" {bad = 1} {prev = $0} END {exit bad}' "$1"; }
if bash "$apply" --root "$ka" "$kpatch" >/dev/null 2>&1 \
   && grep -qxF 'The vocabulary ([index](glossary/index.md)): [Risk](glossary/risk.md)' "$kb/index.md" && grep -qxF '* [Acme Corp](org/acme.md)' "$kb/index.md" \
   && ! grep -qE 'taxonomy\.md|widget\.md' "$kb/index.md" "$kb/glossary/index.md" "$kb/org/index.md" \
   && knodouble "$kb/index.md" && knodouble "$kb/org/index.md"; then
  ok "delete takes the concept's link out of a list of links, keeps the rest of the line, and leaves no double blank line"
else
  err "delete did not take the link out of a shared line cleanly: $(tr '\n' '|' < "$kb/index.md") // $(tr '\n' '|' < "$kb/org/index.md")"
fi
printf '%s\n' 'ops:' '  - {op: delete, path: glossary/model.md, log: gone}' > "$kpatch"
apply_refuses "deleting a concept a sentence links, with a comma after the link" "inside other text"
printf '%s\n' 'ops:' '  - {op: delete, path: glossary/harm.md, log: gone}' > "$kpatch"
apply_refuses "deleting a concept a sentence links, with no comma" "inside other text"
rm -rf "$ka"
# The format comes from the script that enforces it, so a host needs no
# particular release of the skill to learn it. The skill's page shows the
# same block, and this check keeps the two equal.
# shellcheck disable=SC2016 # the backticks are a Markdown code fence, not a command
if diff <(bash "$apply" --format) <(awk '/^```yaml$/ {on = 1; next} /^```$/ {on = 0} on' skills/ktl-librarian/references/patch.md) >/dev/null; then
  ok "knowledge-apply.sh --format prints the block ktl-librarian's references/patch.md shows"
else
  err "knowledge-apply.sh --format and the yaml block in skills/ktl-librarian/references/patch.md differ - one was edited without the other"
fi

# 20. knowledge-report.sh computes what the skills used to have a model work
#     out, so it has to get the arithmetic right on every layout the format
#     allows:
#       - the health line;
#       - each label, with a same-day edit told from its confirmation by the
#         two times compared whole;
#       - a retired concept counted once;
#       - events written as a block list, a flow sequence or a bare mapping;
#       - an open question read only under its real heading.
#     A source
#     has moved when history, not a clock, puts its last commit after the one
#     that recorded the event, or when it carries an uncommitted edit; one
#     changed in the same commit has not. And no reader's words leave it,
#     except inside the one prompt the retrieval test builds, whose reply it
#     scores by program: against what the ledger expects and never against a
#     line of the reply, and without a question whose concept has left the
#     bundle. `changes` says what a change does to each confirmed concept's
#     label. `quiet` and the work list set a moved source aside once the
#     librarian's own question covers it, and set aside what a person
#     declined by closing the workflow's pull request, until it changes again.
say ""
say "Exercising knowledge-report.sh..."
report="$repo_root/$templates/scripts/knowledge-report.sh"
kr="$(mktemp -d)"; kk="$kr/.lokf/knowledge"; mkdir -p "$kk/x" "$kr/src"
kr_git=(env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null git -C "$kr"
  -c init.defaultBranch=main -c user.name=contract -c user.email=contract@example.invalid -c commit.gpgsign=false)
"${kr_git[@]}" init -q
printf 'a\n' > "$kr/src/a.md"; printf 'b\n' > "$kr/src/b.md"; printf 'c\n' > "$kr/src/c.md"
printf -- '---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n\n# X\n\n* [Confirmed](x/confirmed.md) - a confirmed concept about widgets.\n* [Draft one](x/draft.md) - a draft about gadgets.\n' > "$kk/index.md"
printf -- '---\ntype: Service\ntitle: Confirmed\nresource: src/a.md\nsources:\n- resource: src/a.md\n- resource: src/c.md\n- resource: https://example.invalid/never-fetched\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\nverified:\n- by: human:ada\n  at: "2026-01-02T10:00:00Z"\n  revision: "3f9c2a1b7e0d4c6a8f5e2d1c9b8a7f6e5d4c3b2a"\nstale_after: 2020-01-01\n---\n\n# Overview\n' > "$kk/x/confirmed.md"
printf -- '---\ntype: Service\ntitle: Edited\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-02T14:00:00Z"\nverified:\n  - by: human:ada\n    at: "2026-01-02T10:00:00Z"\n---\n' > "$kk/x/edited.md"
printf -- '---\ntype: Service\ntitle: Auto\nresource: src/b.md\nverified: [{ by: process:ktl-librarian, at: "2026-01-03T00:00:00Z" }]\n---\n' > "$kk/x/auto.md"
# shellcheck disable=SC2016 # the backticks are a Markdown code fence, not a command
printf -- '---\ntype: Service\ntitle: Draft one\nstatus: draft\n---\n\n# Overview\n\n```markdown\n## Open questions\n\n- 2026-01-01, human:example: only an example in a fence\n```\n\n## Open questions\n\n- 2026-01-05, human:ada: send it back, with these words for the curator\n' > "$kk/x/draft.md"
printf -- '---\ntype: Service\ntitle: Retired\nstatus: deprecated\nverified:\n- by: human:ada\n  at: "2026-01-02T10:00:00Z"\n---\n' > "$kk/x/retired.md"
printf -- "---\ntype: Service\ntitle: 'Ada''s answered concept'\nverified:\n  by: human:ada\n  at: \"2026-02-01T00:00:00Z\"\n---\n\n## Open questions\n\n- 2026-01-15, process:ktl-librarian: which is it?\n" > "$kk/x/answered.md"
printf -- '---\ntype: Service\ntitle: Gone\nresource: src/missing.md\n---\n' > "$kk/x/gone.md"
printf '# Change Log\n' > "$kk/log.md"
printf '%s\n' '# Reader feedback for the librarian' '' '## 2026-03-03' '' '- **Miss** - Q: "a reader wrote these waiting words" - docent' '- **Disagreement** - another. - docent' > "$kr/.lokf/feedback.md"
# shellcheck disable=SC2016 # the backticks are Markdown code spans, not commands
printf '%s\n' '# Questions readers asked' '' 'Written by knowledge-apply.sh.' '' '- 2026-01-10 Miss x/confirmed.md: `Where are widgets?`' '- 2026-01-11 Miss x/confirmed.md: `a reader wrote these ledger words`' '- 2026-01-12 Disagreement x/draft.md' \
  '- 2026-01-13 Miss x/deleted-since.md: `Where did the old concept go?`' > "$kr/.lokf/questions.md"
"${kr_git[@]}" add -A && "${kr_git[@]}" commit -q -m 'sources and concepts in one commit'
kr_run() { (cd "$kr" && bash "$report" "$@" 2>&1); }
if out="$(kr_run worklist)" && grep -q '^Sources that moved since the concept was derived or last checked: 1$' <<<"$out" && grep -qF -- '- x/gone.md: src/missing.md (gone)' <<<"$out"; then
  ok "report script: a source changed in the commit that recorded the event has not moved, and a missing one is named"
else
  err "report script misread a single-commit history: $out"
fi
printf 'a2\n' >> "$kr/src/a.md" && "${kr_git[@]}" commit -q -am 'a source moves on'
printf 'b2\n' >> "$kr/src/b.md"
want_health='Confirmed by a person: 2 of 7 · Checked by automation only: 1 · Nobody has checked: 2 · Drafts: 1 · Past review date: 1 · Edited since confirmed: 1 · Retired: 1'
if out="$(kr_run health)" && [[ "$out" == "$want_health" ]]; then
  ok "report script: the health line counts each label, an edited concept under its own, a retired one once"
else
  err "report script printed the wrong health line: $out"
fi
out="$(kr_run labels x/confirmed.md x/edited.md x/auto.md x/draft.md x/retired.md x/answered.md x/none.md)"
for want in '- Confirmed (x/confirmed.md) - confirmed by a person, 2026-01-02, against 3f9c2a1, past its review date (2020-01-01)' \
            '- Edited (x/edited.md) - edited since a person last confirmed it (confirmed 2026-01-02T10:00:00Z, edited 2026-01-02T14:00:00Z)' \
            '- Auto (x/auto.md) - checked by automation only' \
            '- Draft one (x/draft.md) - nobody has checked this yet, still a draft' \
            '- Retired (x/retired.md) - retired' \
            "- Ada's answered concept (x/answered.md) - confirmed by a person, 2026-02-01" \
            '- x/none.md - no such concept in this bundle'; do
  if grep -qxF -- "$want" <<<"$out"; then ok "report script labels: $want"; else err "report script did not print '$want': $out"; fi
done
out="$(kr_run worklist)"
for want in '- x/confirmed.md: src/a.md (' '- x/auto.md: src/b.md (edited, not yet committed)' '- x/gone.md: src/missing.md (gone)' \
            'Notes a person left that still wait: 1' '- x/draft.md (2026-01-05, human:ada)' \
            "Open questions older than a person's later confirmation: 1" '- x/answered.md (2026-01-15, process:ktl-librarian; a person confirmed the concept 2026-02-01)' \
            'Reader feedback waiting: 2' '- x/confirmed.md (2 times)'; do
  if grep -qF -- "$want" <<<"$out"; then ok "report script work list: $want"; else err "report script's work list lacks '$want': $out"; fi
done
if grep -q 'src/c.md\|never-fetched\|example in a fence' <<<"$out"; then
  err "report script's work list names an unmoved source, a URL or a fenced example: $out"
else
  ok "report script: an unmoved source, a URL and a question shown inside a code fence are left out"
fi
if grep -q 'waiting words\|ledger words\|these words for the curator' <<<"$out"; then
  err "report script's work list carries a reader's or a person's words: $out"
else
  ok "report script: the work list is paths and dates, with nobody's words in it"
fi
if out="$(kr_run)" && grep -qF 'Confirmed by a person, and a source moved after that confirmation: 1' <<<"$out" && grep -qF -- '- x/confirmed.md: src/a.md (' <<<"$out" \
   && grep -qF 'send it back, with these words for the curator' <<<"$out" && ! grep -q 'waiting words\|ledger words' <<<"$out"; then
  ok "report script: the whole report names a confirmed concept whose source moved, shows a person's note, and no reader's words"
else
  err "report script's whole report is not as expected: $out"
fi
printf '\nmore\n' >> "$kk/x/confirmed.md"; printf -- '---\ntype: Service\ntitle: New\n---\n' > "$kk/x/new.md"
if out="$(kr_run changes)" && grep -qxF 'Concepts added: 1 · changed: 1 · removed: 0' <<<"$out" && grep -qxF 'Confirmed by a person, and changed or removed here: 1' <<<"$out" && grep -qxF -- '- x/confirmed.md: still reads as confirmed' <<<"$out"; then
  ok "report script: changes counts the working tree against HEAD and names the confirmed concept it touches, which still reads as confirmed"
else
  err "report script's changes is not as expected: $out"
fi
# What a change does to a confirmed concept's label: an edit the pen stamped
# turns it to edited since, a deletion removes it, and a confirmation struck
# out by hand is gone. A reviewer reads which of these each concept met.
sed -i 's/at: "2026-01-01T00:00:00Z"/at: "2026-03-01T00:00:00Z"/' "$kk/x/confirmed.md"
rm "$kk/x/retired.md"
printf -- "---\ntype: Service\ntitle: 'Ada''s answered concept'\n---\n" > "$kk/x/answered.md"
out="$(kr_run changes)"
for want in 'Concepts added: 1 · changed: 2 · removed: 1' 'Confirmed by a person, and changed or removed here: 3' \
            '- x/confirmed.md: reads as edited since that confirmation' '- x/retired.md: removed' '- x/answered.md: its confirmation is gone'; do
  if grep -qxF -- "$want" <<<"$out"; then ok "report script changes: $want"; else err "report script's changes lacks '$want': $out"; fi
done
"${kr_git[@]}" checkout -q -- .lokf/knowledge/x/retired.md .lokf/knowledge/x/answered.md
# A sidecar in a subfolder of a larger repository: git names each changed path
# from the top of the work tree, and the report must still read the file there.
km="$(mktemp -d)"; mkdir -p "$km/pkg/.lokf/knowledge/x"
km_git=(env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null git -C "$km"
  -c init.defaultBranch=main -c user.name=contract -c user.email=contract@example.invalid -c commit.gpgsign=false)
"${km_git[@]}" init -q
printf -- '---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n' > "$km/pkg/.lokf/knowledge/index.md"
printf -- '---\ntype: Service\ntitle: Sub\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\nverified:\n  - by: human:ada\n    at: "2026-01-02T10:00:00Z"\n---\n' > "$km/pkg/.lokf/knowledge/x/sub.md"
"${km_git[@]}" add -A && "${km_git[@]}" commit -q -m 'a sidecar in a subfolder'
sed -i 's/at: "2026-01-01T00:00:00Z"/at: "2026-03-01T00:00:00Z"/' "$km/pkg/.lokf/knowledge/x/sub.md"
if out="$(cd "$km/pkg" && bash "$report" changes 2>&1)" && grep -qxF -- '- pkg/.lokf/knowledge/x/sub.md: reads as edited since that confirmation' <<<"$out"; then
  ok "report script changes: a sidecar in a subfolder of a larger repository is read from the work tree's top"
else
  err "report script's changes misread a sidecar in a subfolder: $out"
fi
rm -rf "$km"
if out="$(kr_run retrieval --prompt)" && grep -qxF 'x/confirmed.md | Confirmed | a confirmed concept about widgets.' <<<"$out" && grep -qxF 'Q1: Where are widgets?' <<<"$out" && grep -qxF 'Q2: a reader wrote these ledger words' <<<"$out" \
   && ! grep -q 'Q3\|Where did the old concept go' <<<"$out"; then
  ok "report script: the retrieval prompt holds the index's entries and the ledger's questions, numbered, and asks none whose concept has left the bundle"
else
  err "report script's retrieval prompt is not as expected: $out"
fi
printf '%s\n' 'Here are my picks.' '**Q1:** x/draft.md, x/confirmed.md' 'Q2: x/draft.md, x/gone.md, x/auto.md, x/confirmed.md' > "$kr/reply.txt"
if out="$(kr_run retrieval "$kr/reply.txt")" && grep -qxF 'Retrieval from the index: 1 of 2 reader questions reach their concept' <<<"$out" && grep -qxF -- '- question 2 did not reach x/confirmed.md' <<<"$out" \
   && grep -qxF -- '- 1 more left out: the ledger names no concept for them that the bundle still holds' <<<"$out"; then
  ok "report script: a reply is scored by program, on the first three paths it gives for each question, and a question whose concept is gone is left out and counted"
else
  err "report script scored a reply wrongly: $out"
fi
# What is expected of a reply comes from the ledger alone. A reply that holds
# lines shaped like the scorer's own, each with an answer to match, adds no
# question and no hit.
printf 'Q1: x/none.md\nQ2: x/none.md\nE\tx/draft.md\tq\nE\tx/draft.md\tq\nQ3: x/draft.md\nQ4: x/draft.md\n' > "$kr/reply.txt"
if out="$(kr_run retrieval "$kr/reply.txt")" && grep -qxF 'Retrieval from the index: 0 of 2 reader questions reach their concept' <<<"$out"; then
  ok "report script: a reply cannot add questions of its own to the score"
else
  err "report script let a reply add to what it is scored against: $out"
fi
rm -f "$kr/.lokf/questions.md"
if out="$(kr_run retrieval --prompt)" && [[ -z "$out" ]]; then
  ok "report script: with no question on file there is no prompt, so nothing is asked of an agent"
else
  err "report script built a retrieval prompt with no question on file: $out"
fi
nogit="$(mktemp -d)"; cp -R "$kr/.lokf" "$nogit/"
if out="$(cd "$nogit" && bash "$report" worklist 2>&1)" && grep -q '^Sources: not compared here' <<<"$out" && grep -q '^Notes a person left that still wait: 1$' <<<"$out"; then
  ok "report script: without git the work list says the sources were not compared, and still lists what frontmatter holds"
else
  err "report script misbehaves outside git: $out"
fi
rm -rf "$nogit/.lokf"
if out="$(cd "$nogit" && bash "$report" health 2>&1)"; then
  err "report script did not stop with no bundle: $out"
elif grep -q '^no bundle at ' <<<"$out"; then
  ok "report script: with no bundle it says so and exits non-zero"
else
  err "report script failed some other way with no bundle: $out"
fi
rm -rf "$kr" "$nogit"
# quiet: a scheduled run has work when a source moved after its concept's
# stamp, a person left a note after the librarian last looked, a concept
# carries no stamp, or reader feedback waits, and none otherwise. A note the
# librarian has stamped the concept after still waits for the curator, but
# no longer makes work for the librarian.
kq="$(mktemp -d)"; mkdir -p "$kq/.lokf/knowledge/x" "$kq/src"
kq_git=(env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null git -C "$kq"
  -c init.defaultBranch=main -c user.name=contract -c user.email=contract@example.invalid -c commit.gpgsign=false)
"${kq_git[@]}" init -q
printf 'a\n' > "$kq/src/a.md"
printf -- '---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n' > "$kq/.lokf/knowledge/index.md"
kq_one() {  # <the librarian's own verified.at, or empty> <what follows the overview>
  local verified=""
  [[ -z "$1" ]] || verified="verified:"$'\n'"  - by: process:ktl-librarian"$'\n'"    at: \"$1\""$'\n'
  printf -- '---\ntype: Service\ntitle: One\nresource: src/a.md\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n%s---\n\n# Overview\n%s' \
    "$verified" "$2" > "$kq/.lokf/knowledge/x/one.md"
}
kq_expect() {  # <exit status> <text the line holds> <what>
  local out rc=0
  out="$(cd "$kq" && bash "$report" quiet 2>&1)" || rc=$?
  if [[ "$rc" == "$1" ]] && grep -qF -- "$2" <<<"$out"; then ok "report script quiet: $3"; else err "report script quiet: $3 - exit $rc: $out"; fi
}
kq_note=$'\n## Open questions\n\n- 2026-01-03, human:ada: is this still right?\n'
kq_one "" ""
"${kq_git[@]}" add -A && "${kq_git[@]}" commit -q -m 'a stamped concept and its source'
kq_expect 0 "Quiet: no source moved" "a stamped concept whose source has not moved, with nothing else waiting, makes no work"
printf 'a2\n' >> "$kq/src/a.md" && "${kq_git[@]}" commit -q -am 'the source moves on'
kq_expect 1 "concepts whose source moved: 1 ·" "a source that moved after the stamp makes work"
kq_one "2026-01-02T00:00:00Z" "" && "${kq_git[@]}" commit -q -am 'the librarian rechecks it'
kq_expect 0 "Quiet:" "a recheck recorded after the move makes the run quiet again"
kq_one "2026-01-02T00:00:00Z" "$kq_note" && "${kq_git[@]}" commit -q -am 'a person leaves a note'
kq_expect 1 "notes a person left since the librarian last looked: 1 ·" "a note a person left after the librarian's stamp makes work"
kq_one "2026-01-04T00:00:00Z" "$kq_note" && "${kq_git[@]}" commit -q -am 'the librarian reads it and rechecks'
kq_expect 0 "Quiet:" "a note the librarian stamped the concept after waits for the curator alone"
printf '\n- 2026-01-05, human:ada: and another thing\n' >> "$kq/.lokf/knowledge/x/one.md"
kq_expect 1 "notes a person left since the librarian last looked: 1 ·" "a note not yet committed is newer than any stamp"
"${kq_git[@]}" checkout -q -- .
printf -- '---\ntype: Service\ntitle: Two\n---\n' > "$kq/.lokf/knowledge/x/two.md"
kq_expect 1 "concepts with no stamp: 1 ·" "a concept with no stamp at all makes work, as the sidecar's skeleton does"
rm "$kq/.lokf/knowledge/x/two.md"
printf '%s\n' '# Reader feedback for the librarian' '' '## 2026-01-06' '' '- **Miss** - a reader asked. - docent' > "$kq/.lokf/feedback.md"
kq_expect 1 "reader feedback: 1" "reader feedback waiting makes work"
rm "$kq/.lokf/feedback.md"
# A source that is gone makes work, and the librarian cannot always end it: a
# concept a person confirmed is the curator's to retire, so all it may do is
# ask. Its own question, naming the source and committed after the source
# last changed, says it read that state and put it to a person. The source
# then makes no work until it changes again, and the work list names it
# apart. A question that names no source may ask about anything, so it covers
# none.
kq_asked=$'\n- 2026-01-06, process:ktl-librarian: the source src/a.md is gone; retire this concept?\n'
"${kq_git[@]}" rm -q src/a.md && "${kq_git[@]}" commit -q -m 'the source is deleted'
kq_expect 1 "concepts whose source moved: 1 ·" "a source that is gone makes work"
kq_one "2026-01-04T00:00:00Z" "$kq_note"$'\n- 2026-01-06, process:ktl-librarian: has a person tried this in a real vault, as lib/src/a.md and src/a.md.bak suggest?\n'
kq_expect 1 "concepts whose source moved: 1 ·" "a question of the librarian's that does not name the source, only longer paths that hold it, leaves the work"
kq_one "2026-01-04T00:00:00Z" "$kq_note$kq_asked"
kq_expect 0 "Already with a person: concepts whose moved source the librarian's own question covers: 1" "the librarian's own question naming a source that is gone, not yet committed, ends the work"
"${kq_git[@]}" commit -q -am 'the librarian asks whether to retire it'
kq_expect 0 "Quiet: nothing new waits for the librarian." "that question, once committed after the source went, keeps the run quiet"
out="$(cd "$kq" && bash "$report" worklist 2>&1)"
if grep -qxF 'Sources that moved since the concept was derived or last checked: none' <<<"$out" \
   && grep -qxF 'Sources that moved, where your own question has waited for a person since: 1' <<<"$out" && grep -qxF -- '- x/one.md: src/a.md (gone)' <<<"$out"; then
  ok "report script work list: a source the librarian's question covers is named apart from the sources that still wait"
else
  err "report script's work list does not set a source its own question covers apart: $out"
fi
mkdir -p "$kq/src" && printf 'back\n' > "$kq/src/a.md" && "${kq_git[@]}" add -A && "${kq_git[@]}" commit -q -m 'the source comes back, changed'
kq_expect 1 "concepts whose source moved: 1 ·" "a source that changes after the librarian's question makes work again"
kq_one "2026-01-07T00:00:00Z" "$kq_note$kq_asked" && "${kq_git[@]}" commit -q -am 'the librarian rechecks it'
kq_expect 0 "Quiet: no source moved" "a recheck after that change makes the run quiet, with nothing set aside"
# A source git never held has no commit to order against the question, so any
# question of the librarian's on the concept covers it.
printf -- '---\ntype: Service\ntitle: Never\nresource: src/never.md\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n---\n\n# Overview\n' > "$kq/.lokf/knowledge/x/never.md"
"${kq_git[@]}" add -A && "${kq_git[@]}" commit -q -m 'a concept whose source never existed'
kq_expect 1 "concepts whose source moved: 1 ·" "a source that never existed makes work"
printf '\n## Open questions\n\n- 2026-01-08, human:ada: where is this file?\n' >> "$kq/.lokf/knowledge/x/never.md" && "${kq_git[@]}" commit -q -am 'a person asks, which is no question of the librarian'
kq_expect 1 "concepts whose source moved: 1 ·" "a person's note covers no source for the librarian"
printf -- '- 2026-01-09, process:ktl-librarian: no file was ever at src/never.md; which source is meant?\n' >> "$kq/.lokf/knowledge/x/never.md" && "${kq_git[@]}" commit -q -am 'the librarian asks'
kq_expect 1 "concepts whose source moved: 0 · notes a person left since the librarian last looked: 1 ·" "the librarian's question covers a source git never held, and the person's note still waits for a stamp"
"${kq_git[@]}" rm -q .lokf/knowledge/x/never.md && "${kq_git[@]}" commit -q -m 'that concept goes'

# What a person declined. The librarian workflow hands a scheduled run the
# pull requests of its own that a person closed without merging, in the file
# KNOWLEDGE_DECLINED names. Nothing such a pull request had before it makes
# work again until it changes: a source of a concept it touched, a note left
# there, a concept it tried to stamp, a feedback entry it handled. The work
# list names each, and the concepts it added, so none is proposed twice.
kd_base_one() { kq_one "2026-01-07T00:00:00Z" "$1"; }
printf 'b\n' > "$kq/src/b.md"
printf -- '---\ntype: Service\ntitle: Two\nresource: src/b.md\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n---\n\n# Overview\n' > "$kq/.lokf/knowledge/x/two.md"
"${kq_git[@]}" add -A && "${kq_git[@]}" commit -q -m 'a second stamped concept and its source'
printf 'a3\n' >> "$kq/src/a.md"; printf 'b2\n' >> "$kq/src/b.md"
kd_base_one "$kq_note$kq_asked"$'- 2026-01-20, human:ada: and is the limit still ten?\n'
printf -- '---\ntype: Service\ntitle: Three\n---\n\n# Overview\n' > "$kq/.lokf/knowledge/x/three.md"
kd_first='- **Miss** - Q: "a reader wrote these declined words" - docent'
printf '%s\n' '# Reader feedback for the librarian' '' '## 2026-01-21' '' "$kd_first" '- **Miss** - Q: "another reader asked" - docent' > "$kq/.lokf/feedback.md"
"${kq_git[@]}" add -A && "${kq_git[@]}" commit -q -m 'both sources move, a person leaves a note, readers ask, and a concept arrives unstamped'
kd_base="$("${kq_git[@]}" rev-parse HEAD)"
kd="$kq/declined.txt"
kd_expect() {  # <exit status> <text the line holds> <what>
  local out rc=0
  out="$(cd "$kq" && KNOWLEDGE_DECLINED="$kd" bash "$report" quiet 2>&1)" || rc=$?
  if [[ "$rc" == "$1" ]] && grep -qF -- "$2" <<<"$out"; then ok "report script declined: $3"; else err "report script declined: $3 - exit $rc: $out"; fi
}
kq_expect 1 "concepts whose source moved: 2 · notes a person left since the librarian last looked: 1 · concepts with no stamp: 1 · reader feedback: 2" "with no record, everything waiting makes work"
printf '%s\n' "declined 12 2026-02-01 $kd_base" 'touched x/one.md' 'touched x/three.md' 'added x/new.md' 'added x/two.md' \
  "handled $(printf '%s\n' "$kd_first" | git hash-object --stdin)" 'touched ../../etc/passwd.md' 'touched x/Two.md' 'a line in no shape' > "$kd"
kd_expect 1 "concepts whose source moved: 1 · notes a person left since the librarian last looked: 0 · concepts with no stamp: 0 · reader feedback: 1 ·" "what a closed pull request had before it makes no work, and the rest still does"
kd_expect 1 "left from a pull request a person closed without merging: 4" "the line of counts says how much was left"
out="$(cd "$kq" && KNOWLEDGE_DECLINED="$kd" bash "$report" worklist 2>&1)"
for want in 'Sources that moved since the concept was derived or last checked: 1' \
            'Declined, since a person closed the pull request without merging; propose none of it again: 5' \
            "- x/one.md: a person's note of 2026-01-20; pull request #12, closed 2026-02-01" \
            '- x/three.md: no stamp yet; pull request #12, closed 2026-02-01' \
            '- x/new.md: a concept that pull request added; pull request #12, closed 2026-02-01' \
            '- .lokf/feedback.md: the entry at line 5, which that pull request handled; pull request #12, closed 2026-02-01'; do
  if grep -qxF -- "$want" <<<"$out"; then ok "report script declined, work list: $want"; else err "report script's work list with a declined record lacks '$want': $out"; fi
done
if grep -q '^- x/two.md: src/b.md (' <<<"$out" && grep -q '^- x/one.md: src/a.md (.*); pull request #12, closed 2026-02-01$' <<<"$out" \
   && ! grep -q 'x/two.md: a concept that pull request added\|passwd\|Two.md\|declined words' <<<"$out"; then
  ok "report script declined: a source nobody declined still waits, a declined one is named with its pull request, and no reader's words or bad path is printed"
else
  err "report script's work list with a declined record is not as expected: $out"
fi
# The record is read on a scheduled run only: with none, as on a run a person
# starts, everything is work again. A record this clone cannot order, since
# its base commit is no ancestor of HEAD, counts for nothing.
printf '%s\n' 'declined 13 2026-02-08 0123456789abcdef0123456789abcdef01234567' 'touched x/one.md' 'touched x/two.md' > "$kd"
kd_expect 1 "concepts whose source moved: 2 · notes a person left since the librarian last looked: 1 · concepts with no stamp: 1 · reader feedback: 2" "a record whose base commit this clone does not hold is left out"
printf '%s\n' "declined 12 2026-02-01 $kd_base" 'touched x/one.md' 'touched x/two.md' 'touched x/three.md' \
  "handled $(printf '%s\n' "$kd_first" | git hash-object --stdin)" "handled $(printf '%s\n' '- **Miss** - Q: "another reader asked" - docent' | git hash-object --stdin)" > "$kd"
kd_expect 0 "Quiet: nothing new waits for the librarian. Already with a person: left from a pull request a person closed without merging: 6" "a week whose every item a person declined is quiet, and says what it left"
# Each kind makes work again once it changes after that pull request.
printf 'a4\n' >> "$kq/src/a.md" && "${kq_git[@]}" commit -q -am 'a source moves after the closed pull request'
kd_expect 1 "concepts whose source moved: 1 ·" "a source that moves after the closed pull request makes work again"
printf '\n## Open questions\n\n- 2026-02-10, human:ada: one more thing\n' >> "$kq/.lokf/knowledge/x/two.md"
sed -i 's/^## 2026-01-21$/## 2026-02-10\n\n- **Miss** - Q: "a reader asks again" - docent\n\n## 2026-01-21/' "$kq/.lokf/feedback.md"
printf 'more\n' >> "$kq/.lokf/knowledge/x/three.md"
"${kq_git[@]}" commit -q -am 'a new note, a new reader entry and an edit to the unstamped concept'
kd_expect 1 "concepts whose source moved: 1 · notes a person left since the librarian last looked: 1 · concepts with no stamp: 1 · reader feedback: 1 ·" "a note, a reader's entry and an edit made after the closed pull request each make work again"
if out="$(cd "$kq" && KNOWLEDGE_DECLINED="$kd" bash "$report" 2>&1)" && ! grep -q 'Declined\|pull request #' <<<"$out"; then
  ok "report script declined: the curator's report reads no record of declined changes"
else
  err "report script's whole report changed with a declined record: $out"
fi
"${kq_git[@]}" rm -q -r .lokf/knowledge/x/two.md .lokf/knowledge/x/three.md .lokf/feedback.md && "${kq_git[@]}" commit -q -m 'the fixture is put back to one concept'
nogit="$(mktemp -d)"; cp -R "$kq/.lokf" "$nogit/"
if out="$(cd "$nogit" && bash "$report" quiet 2>&1)"; then
  err "report script quiet: a bundle with no history read as quiet: $out"
elif grep -q '^Work may wait: git holds no full history' <<<"$out"; then
  ok "report script quiet: a bundle git holds no history of is never quiet"
else
  err "report script quiet: a bundle with no history failed some other way: $out"
fi
rm -rf "$kq" "$nogit"

# 21. No tracked file holds a character a reader cannot see. That is a
#     control character other than a tab or a line's closing carriage return,
#     or a format character, such as a zero-width space, a byte order mark or
#     the right-to-left override that the "Trojan Source" attack
#     (CVE-2021-42574) hides code behind. A diff shows none of them, and GitHub warns of only
#     some. An agent that types such a character's escape into a tool call
#     can write the character itself, which once put three of them into a
#     sanitizer here. Code that needs one spells it as an escape.
say ""
say "Searching tracked files for characters a reader cannot see..."
read -r -d '' unseen_py <<'PY' || true
import sys, unicodedata
hits = 0
for raw in sys.stdin.buffer.read().split(b"\0"):
    try:
        with open(raw, "rb") as handle:
            data = handle.read()
    except OSError:
        continue
    if b"\0" in data[:8000]:
        continue
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        continue
    for number, line in enumerate(text.split("\n"), start=1):
        for char in sorted(set(line[:-1] if line.endswith("\r") else line)):
            kind = unicodedata.category(char)
            if kind == "Cf" or (kind == "Cc" and char != "\t"):
                hits += 1
                print(f"{raw.decode('utf-8', 'replace')}:{number}: U+{ord(char):04X} {unicodedata.name(char, '')}".rstrip())
sys.exit(1 if hits else 0)
PY
if command -v python3 >/dev/null 2>&1; then
  unseen_run=(python3 -c "$unseen_py")
elif command -v uv >/dev/null 2>&1; then
  unseen_run=(uv run --quiet --no-project python -c "$unseen_py")
else
  unseen_run=(false)
  err "neither python3 nor uv is on PATH, so no tracked file was searched for characters a reader cannot see"
fi
if unseen_out="$(git ls-files -z | "${unseen_run[@]}" 2>&1)"; then
  ok "no tracked file holds a character a reader cannot see"
else
  err "these tracked lines hold a character a reader cannot see; delete it, or spell it as an escape in code: $unseen_out"
fi
unseen_dir="$(mktemp -d)"
printf 'echo ok # a\xe2\x80\xaeb\n' > "$unseen_dir/planted.sh"
if printf '%s\0' "$unseen_dir/planted.sh" | "${unseen_run[@]}" >/dev/null 2>&1; then
  err "the search missed a right-to-left override planted in a script"
else
  ok "the search finds a right-to-left override planted in a script"
fi
rm -rf "${unseen_dir:?}"

say ""
if [[ "$fail" -eq 0 ]]; then
  say "Repository contract: PASS"
  exit 0
else
  say "Repository contract: FAIL"
  exit 1
fi
