#!/usr/bin/env bash
# Repository-contract checks for knowledge-trust-ladder. validate.yml runs
# the specification and Markdown checks as jobs of their own, and pytest runs
# the behavioural tests under tests/ (tests/conftest.py says how). A check
# that moved to tests/ keeps its number here, with a line saying where it
# went, because changelog entries and bundle concepts cite the numbers.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
templates="skills/ktl-sidecar/templates"

fail=0
say() { printf '%s\n' "$*"; }
err() { printf 'FAIL: %s\n' "$*" >&2; fail=1; }
ok() { printf 'OK:   %s\n' "$*"; }

# 1. Exactly the intended published skill directories exist. This list is the
#    one place their number is written: checks 1 and 4 count it.
mapfile -t skill_dirs < <(find skills -mindepth 1 -maxdepth 1 -type d | sort)
expected_dirs=("skills/ktl-curator" "skills/ktl-docent" "skills/ktl-librarian" "skills/ktl-prose" "skills/ktl-sidecar" "skills/ktl-website")
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
#     field (agentskills.io/specification: 1-500 characters), which every
#     installer shows. So a need for git, a POSIX shell, uv or an
#     authenticated identity is known before a step asks for it.
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
#     plugin manifest and its marketplace entry carry the same keyword list,
#     on one line in each so the two can be compared.
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

# 5. Each relative link resolves from its file's directory, so it still works
#    when an installer copies one skill/ subtree at a time.
say ""
say "Checking relative link targets..."
broken=0
while IFS= read -r file; do
  # Blank out fenced code first, keeping line numbers: a link inside ```
  # fences is an example of syntax, not a real link.
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

# 7. Two files list the LOKF classes in prose, with no generator behind them.
#    Rule 3 in ktl-librarian/SKILL.md is the canonical list, and the other
#    list and any count a page states must agree with it. Other prose says
#    "small" rather than a number, since the count is the schema's to change.
rule3_line="$(grep -m1 '^3\. \*\*Use a class from the LOKF type vocabulary' skills/ktl-librarian/SKILL.md || true)"
if [[ -z "$rule3_line" ]]; then
  err "could not find Rule 3's class list in skills/ktl-librarian/SKILL.md"
else
  # The list ends where the sentence on a host's own classes begins; it names
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

# 7c. Rule 3's list is held to the classes the schema declares at the lokf
#     floor the templates pin. `lokf vocab --all --json` marks each type a
#     concept may name with `is_type_value`. uvx runs the toolkit at that
#     floor, so the check reads the schema a host installs, not whatever this
#     machine holds. Without uv the check fails, as check 11's does.
#
# 7d. knowledge-report.sh counts how many concepts rely on each concept from
#     a fixed list of relation fields. It runs without the toolkit and cannot
#     read the schema, so the list is held here to the slots the schema ranges
#     over Concept, apart from two structural ones: `concepts`, the bundle's
#     list, and `target`, a reified relation's.
say ""
say "Checking the class list and the relation fields against the LOKF schema..."
lokf_floor="$(sed -n 's/.*"lokf\[build\]>=\([0-9.]*\)".*/\1/p' "$templates/pyproject.toml" | head -n 1)"
read -r -d '' vocab_py <<'PY' || true
import json, sys
d = json.load(sys.stdin)
print(" ".join(sorted(c["name"] for c in d["classes"] if c.get("is_type_value"))))
print(" ".join(sorted(s["name"] for s in d["slots"] if s.get("range") == "Concept" and s["name"] not in ("concepts", "target"))))
PY
if command -v python3 >/dev/null 2>&1; then
  vocab_run=(python3 -c "$vocab_py")
else
  vocab_run=(uv run --quiet --no-project python -c "$vocab_py")
fi
if [[ -z "$lokf_floor" ]]; then
  err "could not read the lokf floor from $templates/pyproject.toml"
elif [[ -z "${canonical:-}" ]]; then
  err "check 7 found no class list in Rule 3, so there is nothing to hold to the schema"
elif ! command -v uvx >/dev/null 2>&1; then
  err "uvx is not on PATH, so the class list and the relation fields cannot be checked against the schema - install uv"
elif ! vocab="$(uvx --from "lokf==$lokf_floor" lokf vocab --all --json 2>/dev/null)"; then
  err "lokf $lokf_floor did not print its vocabulary (uvx --from lokf==$lokf_floor lokf vocab --all --json) - the floor $templates/pyproject.toml sets must be a release on PyPI"
elif ! schema_lists="$(printf '%s' "$vocab" | "${vocab_run[@]}" 2>/dev/null)"; then
  err "could not read the classes and the relation slots out of lokf $lokf_floor's vocabulary"
else
  schema_classes="$(sed -n 1p <<<"$schema_lists" | tr ' ' '\n' | LC_ALL=C sort -u)"
  schema_relations="$(sed -n 2p <<<"$schema_lists" | tr ' ' '\n' | LC_ALL=C sort -u)"
  rule3_classes="$(LC_ALL=C sort -u <<<"$canonical")"
  if [[ "$rule3_classes" == "$schema_classes" ]]; then
    ok "Rule 3 names the $(grep -c . <<<"$schema_classes") classes lokf $lokf_floor's schema declares as types"
  else
    err "Rule 3's class list and lokf $lokf_floor's schema disagree: $(LC_ALL=C comm -3 <(printf '%s\n' "$rule3_classes") <(printf '%s\n' "$schema_classes") | tr -d '\t' | tr '\n' ' ')- the schema is the source; change Rule 3 and trust-fields.md to match it"
  fi
  report_relations="$(grep -oE 'split\("[A-Za-z ]+", relnames' "$templates/scripts/knowledge-report.sh" | sed -E 's/^split\("//; s/", relnames$//' | tr ' ' '\n' | LC_ALL=C sort -u)"
  if [[ -z "$report_relations" ]]; then
    err "could not find the relation fields knowledge-report.sh counts reliance from: its split(\"...\", relnames) line"
  elif [[ "$report_relations" == "$schema_relations" ]]; then
    ok "knowledge-report.sh counts reliance from the $(grep -c . <<<"$schema_relations") relation slots lokf $lokf_floor's schema ranges over Concept"
  else
    err "knowledge-report.sh's relation fields and lokf $lokf_floor's schema disagree: $(LC_ALL=C comm -3 <(printf '%s\n' "$report_relations") <(printf '%s\n' "$schema_relations") | tr -d '\t' | tr '\n' ' ')- add the schema's slots to the split(\"...\", relnames) line, and to the list in ktl-curator/references/trust-fields.md"
  fi
fi

# 8. The layout tests are in tests/test_layouts.py: the wrapper, the three
#    workflows and the lokf-link recipe, with and without the doorway link.

# 9. The sibling repositories link into files here by URL, as
#    github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/<path> or as
#    the site's persistent address, w3id.org/ktl/docs/<page>/ and
#    w3id.org/ktl/knowledge/<id>, and their link checks follow those links.
#    Moving or renaming one of these paths passes every check here and breaks
#    the build of the sibling that links to it: the two Obsidian plugins,
#    ktl-federation, ai-linkmo or gist. An entry that names a heading, as
#    path#anchor, also needs that heading, since a link can still find its
#    page after the heading has gone. CONTRIBUTING.md says which side merges
#    first; this list holds the paths.
say ""
say "Checking the paths sibling repositories link into..."
sibling_paths=(
  "AI_COVENANT.md"
  "SECURITY.md"
  ".lokf/knowledge/glossary/registrar.md"
  ".lokf/knowledge/playbooks/domain-bundle.md"
  ".lokf/knowledge/playbooks/domain-bundle.md#reading-the-workspace"
  ".lokf/knowledge/playbooks/domain-bundle.md#the-four-concept-types"
  ".lokf/knowledge/playbooks/domain-bundle.md#the-worked-example"
  ".lokf/knowledge/playbooks/ktl-curator-skill.md"
  ".lokf/knowledge/playbooks/open-bundle-in-obsidian.md"
  ".lokf/knowledge/playbooks/open-bundle-in-obsidian.md#why-the-bundle-is-never-a-real-folder-inside-a-vault"
  "docs/architecture.md"
  "docs/architecture.md#four-skills-three-lines-of-the-poem"
  "docs/architecture.md#the-fifth-role-which-is-not-a-skill"
  "docs/architecture.md#trust-stays-visible"
  "docs/context-layer.md"
  "docs/federation.md"
  "docs/federation.md#decisions-an-adopter-must-make"
  "docs/federation.md#how-the-workspace-stays-current"
  "docs/federation.md#what-exists-and-what-remains-a-design"
  "docs/how-it-works.md#four-levels-of-checking"
  "docs/install.md"
  "docs/obsidian.md"
  "docs/obsidian.md#where-the-bundle-lives-host-by-host"
  "docs/releasing.md"
  "docs/signing-commits.md"
  "docs/threat-model.md"
  "docs/threat-model.md#human-attribution-human-is-a-claim-not-a-credential"
  "docs/threat-model.md#interactive-use-scope-is-advisory-not-enforced"
  "docs/threat-model.md#prompt-injection-guards"
  "docs/threat-model.md#repository-hardening"
  "docs/threat-model.md#the-sync-workflow"
  "docs/threat-model.md#the-website"
  "docs/three-lines.md"
  "skills/ktl-librarian/references/domain-vocabulary.md"
  "skills/ktl-curator/references/review-session.md"
  "skills/ktl-curator/references/trust-fields.md"
)
# The GitHub anchor of each heading in a Markdown file, one per line, passing
# over fenced code. GitHub lowercases a heading, drops its punctuation and
# writes each space as a hyphen.
heading_anchors() {
  awk '/^[[:space:]]*(```|~~~)/ { fence = !fence; next } !fence && /^#+ / { sub(/^#+ +/, ""); print }' "$1" \
    | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9 _-]//g; s/ /-/g'
}
for entry in "${sibling_paths[@]}"; do
  p="${entry%%#*}"
  if [[ ! -e "$p" ]]; then
    err "sibling-linked path is gone: $p - a sibling repository links to it by URL; restore it, or update that sibling's links in the same change"
  elif [[ "$entry" == *#* ]] && ! heading_anchors "$p" | grep -qxF "${entry#*#}"; then
    err "sibling-linked heading is gone: $entry - a sibling repository links to it by URL; restore the heading, or update that sibling's links in the same change"
  else
    ok "sibling-linked path exists: $entry"
  fi
done

# 9a. Where the siblings are cloned beside this repository, check that the
#     list above records every path they link to, since check 9 does not
#     cover a link the list lacks. A sibling that adds a link records its
#     path here in the same change. CI clones no sibling, so this half runs
#     only locally.
mapfile -t cloned < <(for s in obsidian-ktl-curator obsidian-ktl-registrar ktl-federation ai-linkmo gist; do
  [[ -d "../$s/.git" ]] && printf '%s\n' "../$s"
done || true)
if [[ ${#cloned[@]} -eq 0 ]]; then
  say "      (no sibling clones beside this repo - skipping the completeness cross-check)"
else
  # Skip .agents and .claude: each sibling installs these skills under
  # .agents/skills, with .claude/skills a link to it, and the links between
  # those copies are not a sibling depending on this repository. Skip .venv,
  # which is only slow. Plain grep, unlike a git-aware one, reads what
  # .gitignore hides.
  #
  # A link to a heading is recorded as path#anchor, and one to a heading of
  # the front page as README.md#anchor, apart from GitHub's #readme. A
  # w3id.org/ktl address names a file by its page: docs/<page>/ is
  # docs/<page>.md, knowledge/<id> is .lokf/knowledge/<id>.md, and the site's
  # root is the README. A sibling's own namespace under w3id.org/ktl/ is not
  # a link into this repository, and is dropped.
  #
  # Skip what a sibling's build writes and git ignores. Its website build
  # copies its pages under the site's folder, where a link quoted in a folded
  # YAML string ends in a backslash. A domain host's snapshot/ holds each
  # member's bundle, this repository's among them, whose IRIs would read as
  # links.
  mapfile -t linked < <(grep -rHoE 'https://github\.com/noelmcloughlin/knowledge-trust-ladder(/blob/main/[^)"#[:space:]]+)?(#[A-Za-z0-9_-]+)?|https://w3id\.org/ktl/(docs/[a-z0-9.-]+/|knowledge/[a-z0-9-]+(/[a-z0-9-]+)*/?)?(#[A-Za-z0-9_-]+)?' \
    "${cloned[@]}" --include='*.md' --include='*.yaml' --include='justfile' \
    --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=.agents \
    --exclude-dir=.claude --exclude-dir=.venv 2>/dev/null \
    | grep -vE '/(ktl-)?website/(dist|generated|resources|public|src/content|src/generated)/|^\.\./[^/]+/snapshot(\.new)?/' | sed -E 's|^[^:]*:||' \
    | sed -E 's|^https://w3id\.org/ktl/docs/([a-z0-9.-]+)/|docs/\1.md|; s|^https://w3id\.org/ktl/knowledge/([a-z0-9-]+(/[a-z0-9-]+)*)/?|.lokf/knowledge/\1.md|; s|^https://w3id\.org/ktl/#|README.md#|; /^https:\/\/w3id\.org\/ktl\//d; s|^https://github\.com/noelmcloughlin/knowledge-trust-ladder||; s|^/blob/main/||; s|^#|README.md#|; s/[.,]$//; /^$/d; /^README\.md#readme$/d' \
    | sort -u || true)
  unrecorded=0
  for l in "${linked[@]}"; do
    found=0
    for p in "${sibling_paths[@]}"; do
      [[ "$l" == "$p" ]] && { found=1; break; }
    done
    if [[ "$found" -eq 0 ]]; then
      lp="${l%%#*}"
      if [[ ! -e "$lp" ]] || { [[ "$l" == *#* ]] && ! heading_anchors "$lp" | grep -qxF "${l#*#}"; }; then
        err "a sibling links to '$l', which this repository no longer has - update the sibling's link"
      else
        err "a sibling links to '$l', which check 9's list does not record - add it there"
      fi
      unrecorded=1
    fi
  done
  [[ "$unrecorded" -eq 0 ]] && ok "every path the ${#cloned[@]} cloned sibling(s) link to is recorded here (${#linked[@]} target(s))"
fi

# 10. CONTRIBUTING.md is a checklist, not a design log, and SECURITY.md is a
#     policy, not a threat model. Each rule or surface is a line or two that
#     links to its reasoning: a code comment, a workflow header or a page
#     under docs/. A word budget is the one signal every contributor, person
#     or agent, reads. CONTRIBUTING sits between 700 and 850 words in the
#     three repositories, and past 1000 it becomes a design log again.
#     SECURITY sits between 450 and 800, and was 1,400 to 1,900 before
#     docs/threat-model.md took the design, so 900 is its line. The siblings
#     check the same budgets.
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

# 10a. Each SKILL.md has a word budget too. An agent loads the whole page
#      when the skill starts, and the Agent Skills specification recommends
#      under 5,000 tokens for it. The detail a step needs goes in
#      references/, which an agent opens only when a step sends it there.
#      Each budget sits just above its page's size, so an edit that adds
#      words moves as many into references/. A skill with no budget fails. A
#      table's pipes and separator row are not counted as words, since a
#      table is the densest way to state a vocabulary.
say ""
say "Checking each SKILL.md stays within its word budget..."
declare -A skill_budget=(
  [skills/ktl-curator]=2700
  [skills/ktl-docent]=2200
  [skills/ktl-librarian]=4000
  [skills/ktl-prose]=2350
  [skills/ktl-sidecar]=3600
  [skills/ktl-website]=2000
)
for dir in "${expected_dirs[@]}"; do
  file="$dir/SKILL.md"
  budget="${skill_budget[$dir]:-}"
  if [[ -z "$budget" ]]; then
    err "$file has no word budget in check 10a - give it one there"
    continue
  fi
  words="$(sed -E -e '/^\|[ :-]+(\|[ :-]+)*\|?[[:space:]]*$/d' -e 's/\|/ /g' "$file" | wc -w)"
  if (( words <= budget )); then
    ok "$file is $words words (budget $budget)"
  else
    err "$file is $words words; the budget is $budget - an agent loads the whole page when the skill starts, so move the detail a step needs into $dir/references/ and link to it"
  fi
done

# 11. This repository runs its own sidecar from the templates, so each copy
#     under .github/ and .lokf/scripts/ must stay byte-identical to its
#     template. knowledge-librarian.yaml may differ only in the values of
#     TRUST_LADDER_SKILLS_REF and TRUST_LADDER_SKILLS_SHA: the release commit
#     moves the pin in the template but may not touch .github/workflows/, and
#     the install step that reads the pin is skipped in this repository.
#
#     The sidecar's knowledge-sync.manifest is the one list of copies that the
#     sync script, the preflight and this check read, so it is checked first.
#     Each template it names must exist, each always and needs line must name
#     a template it lists, and each file under the templates' github/,
#     scripts/ and m365/ folders must be in it. So no new workflow or script
#     is released without a sync.
#
#     Last, knowledge-conventions.sh runs on this repository's bundle.
say ""
say "Checking the sidecar's manifest names every template, and nothing else..."
manifest="$templates/knowledge-sync.manifest"
listed=""
while read -r rule template copy _; do
  [ -n "$rule" ] || continue
  case "$rule" in
    copy|titled)
      [ -f "$templates/$template" ] || err "$manifest lists $template, which is not under $templates/"
      [ -n "$copy" ] || err "$manifest has a $rule line for $template with no copy path"
      listed="$listed $template" ;;
    always|needs)
      case " $listed " in
        *" $template "*) ;;
        *) err "$manifest has a $rule line for $template, which no copy or titled line before it lists" ;;
      esac ;;
    *) err "$manifest has a rule knowledge-sync.sh does not know: $rule $template" ;;
  esac
done < <(sed 's/#.*//' "$manifest")
while IFS= read -r f; do
  rel="${f#"$templates/"}"
  case " $listed " in
    *" $rel "*) ok "$rel is in the manifest" ;;
    *) err "$f is not in $manifest, so no host would get a sync of it" ;;
  esac
done < <(find "$templates/github" "$templates/scripts" "$templates/m365" -type f ! -path '*/__pycache__/*' | sort)
for rule in copy titled always needs; do
  grep -qE "^rules=\".*\b$rule\b" "$templates/scripts/knowledge-sync.sh" || err "knowledge-sync.sh does not know the manifest rule $rule"
done

say ""
say "Checking the sidecar templates are the copies CI lints..."
# The skills pin is each repository's to move, so it is not drift.
unpin() { sed -E -e 's/(TRUST_LADDER_SKILLS_REF: )v[0-9]+\.[0-9]+\.[0-9]+/\1vX.Y.Z/' -e 's/(TRUST_LADDER_SKILLS_SHA: )[0-9a-f]{40}/\1COMMIT/' "$1"; }
# Three sets of copies may be absent here. The federation templates are for
# a domain host only (ktl-sidecar Step 5), and this bundle is not a domain.
# The sync templates bring a host up to a release of this repository, which
# has nothing to sync to. The ingest templates serve a host with sources
# outside its repository, and this one has none. Each such copy is held to
# its template only where it exists: actionlint reads the templates, and
# tests/test_federation.py, tests/test_sync.py and tests/test_ingest.py run
# the scripts from them. Every other copy must be here.
optional_here=" github/knowledge-federation.yaml scripts/knowledge-federate.py domain.yaml github/knowledge-sync.yaml github/knowledge-sync-pull-request.md scripts/knowledge-sync.sh github/knowledge-ingest.yaml github/knowledge-ingest-pull-request.md scripts/knowledge-ingest.sh scripts/knowledge-ingest.py "
while read -r rule template copy _; do
  src="$templates/$template"; dst="$copy"
  case "$rule" in
    copy)
      if [ ! -f "$dst" ]; then
        case "$optional_here" in
          *" $template "*) ok "$dst is not installed here (a domain host's file, or a host's sync); its template is checked directly" ;;
          *) err "$dst is missing, but $src is a template every host carries - copy the template over" ;;
        esac
      elif cmp -s <(unpin "$src") <(unpin "$dst"); then
        ok "$dst matches its template"
      else
        err "$dst differs from $src - this repository dogfoods its own sidecar, so the two must match: copy the template over the workflow after editing the template, or the workflow over the template after a Dependabot action bump, which only ever edits .github/workflows/"
      fi ;;
    titled)
      # The justfile's first line names the host (Step 1's <PROJ_NAME>), so
      # it is held to its template from the second line on, as the sync
      # copies it.
      if cmp -s <(tail -n +2 "$src") <(tail -n +2 "$dst"); then
        ok "$dst matches its template below the first line"
      else
        err "$dst differs from $src below the first line - copy the template over it and keep this repository's own first line"
      fi ;;
  esac
done < <(sed 's/#.*//' "$manifest")

# 11w. The website skill installs website/ and its deploy workflow in every
#      host, this repository included, so the copies here must stay
#      byte-identical to the templates, as check 11 holds the sidecar's.
#      Three files belong to each host once written: site.toml, README.md and
#      assets/css/custom.css. The README template is compared with this
#      repository's values filled in. Every tracked file under website/ must
#      be a template or one of the three, so a host gets each file of this
#      site.
say ""
say "Checking the website skill's templates are this repository's own site..."
wtemplates="skills/ktl-website/templates"
host_owned=("site.toml" "README.md" "assets/css/custom.css")
owned() { local f; for f in "${host_owned[@]}"; do [[ "$1" == "$f" ]] && return 0; done; return 1; }
while IFS= read -r src; do
  rel="${src#"$wtemplates/website/"}"
  owned "$rel" && continue
  dst="website/$rel"; [[ "$rel" == gitignore ]] && dst="website/.gitignore"
  if [[ ! -f "$dst" ]]; then
    err "$dst is missing, but $src is a template - copy the template over, or delete the template"
  elif cmp -s "$src" "$dst"; then
    ok "$dst matches its template"
  else
    err "$dst differs from $src - this repository runs the site its skill lays down, so the two must match: copy the template over the site file after editing the template, or the site file over the template after a Dependabot uv bump, which only ever edits website/pyproject.toml and uv.lock"
  fi
done < <(find "$wtemplates/website" -type f | sort)
if cmp -s "$wtemplates/github/knowledge-website.yaml" ".github/workflows/knowledge-website.yaml"; then
  ok ".github/workflows/knowledge-website.yaml matches its template"
else
  err ".github/workflows/knowledge-website.yaml differs from $wtemplates/github/knowledge-website.yaml - copy one over the other, as check 11 says"
fi
# The logo a host's site shows when its site.toml names none is a copy of
# this repository's, and must stay one.
for logo in knowledge-trust-ladder-logo.svg knowledge-trust-ladder-logo-dark.svg; do
  if cmp -s ".assets/$logo" "$wtemplates/website/static/brand/$logo"; then
    ok "$wtemplates/website/static/brand/$logo matches .assets/$logo"
  else
    err "$wtemplates/website/static/brand/$logo differs from .assets/$logo - copy .assets/$logo over it, and over website/static/brand/$logo, so every site shows this repository's logo"
  fi
done
filled="$(sed -e 's|<REPO_OWNER>|noelmcloughlin|g' -e 's|<REPO_NAME>|knowledge-trust-ladder|g' -e 's|<PROJ_NAME>|Knowledge Trust Ladder|g' "$wtemplates/website/README.md")"
if [[ "$filled" == "$(cat website/README.md)" ]]; then
  ok "website/README.md is the template with this repository's values filled in"
else
  err "website/README.md is not $wtemplates/website/README.md with this repository's values filled in - edit the template and fill it, or carry an edit of the copy back into the template"
fi
while IFS= read -r f; do
  rel="${f#website/}"
  owned "$rel" && continue
  t="$wtemplates/website/$rel"; [[ "$rel" == .gitignore ]] && t="$wtemplates/website/gitignore"
  [[ -f "$t" ]] || err "$f is tracked under website/ but has no template under $wtemplates/website/ - a file of this repository's site that no host would get; add the template, or move the file"
done < <(git ls-files website)
for f in "${host_owned[@]}"; do
  [[ -f "$wtemplates/website/$f" ]] || err "$wtemplates/website/$f is missing - a host-owned file still needs its template"
done

# The two Python halves install PyYAML through `uv run`, from a dependency
# block that names one release and takes no file uploaded after a date, so a
# gate never runs a parser nobody reviewed. Both must name the same release
# and date.
pyyaml_pins="$(grep -hE '^# (dependencies = \["pyyaml==[0-9]+(\.[0-9]+)+"\]|exclude-newer = "[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:]+Z")$' \
                 "$templates/scripts/knowledge-apply.py" "$templates/scripts/knowledge-conventions.py" | sort | uniq -c | awk '{ print $1 }' | tr '\n' ' ')"
if [[ "$pyyaml_pins" == "2 2 " ]]; then
  ok "knowledge-apply.py and knowledge-conventions.py pin the same PyYAML release and the same cut-off date"
else
  err "knowledge-apply.py and knowledge-conventions.py must each carry 'dependencies = [\"pyyaml==<version>\"]' and an 'exclude-newer' date, the same in both - one is missing, unpinned or different"
fi
# The three shell halves that run a Python half through uv carry one
# uv_ready function, which knowledge-apply.sh explains, and the preflight
# carries it too to ask whether they can. A fix to one copy must reach the
# other three.
uv_ready_copies="$(for f in apply conventions ingest preflight; do sed -n '/^uv_ready() {$/,/^}$/p' "$templates/scripts/knowledge-$f.sh" | cksum; done | sort -u)"
if [[ "$(printf '%s\n' "$uv_ready_copies" | wc -l | tr -d ' ')" == 1 && "$uv_ready_copies" != "4294967295 0" ]]; then
  ok "knowledge-apply.sh, knowledge-conventions.sh, knowledge-ingest.sh and knowledge-preflight.sh carry the same uv_ready"
else
  err "knowledge-apply.sh, knowledge-conventions.sh, knowledge-ingest.sh and knowledge-preflight.sh must each carry the same uv_ready function - one is missing or differs"
fi

say ""
say "Running knowledge-conventions.sh on this repository's bundle..."
# Thirteen of the eighteen rules run through `uv run`, so without uv the
# script reports none of them. Say so once, up front: a job that runs this
# contract installs uv, as validate.yml and publish.yml do.
if ! command -v uv >/dev/null 2>&1; then
  err "uv is not on PATH, so rules 2, 3, 4, 7, 9, 10, 12, 13, 15, 16, 17 and 18 cannot run on this repository's bundle - install uv, or add the setup-uv step to the workflow running this"
fi
if (cd .lokf && bash scripts/knowledge-conventions.sh knowledge --strict >/dev/null); then
  ok "this repository's bundle keeps the conventions"
else
  err "this repository's bundle breaks a convention knowledge-conventions.sh checks - run it from .lokf/ to see which"
fi
# tests/test_conventions.py tests what the script reports on a bundle that
# breaks each rule, on a CRLF checkout, through a link and without uv.

# 11a. ktl-docent runs its own copies of knowledge-report.sh and
#      knowledge-feedback.sh, never the repository's, which anyone who can
#      commit there can change: a question starts the docent, often in a
#      repository the reader has not reviewed. So the copies must match their
#      templates and run from wherever an installer puts them, and no docent
#      page may send an agent to a script under .lokf/scripts/.
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
# Each copy runs from outside the repository, as an installer leaves it, and
# finds the root from the working directory, without git.
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

# 11b. Without Python, ktl-librarian and ktl-sidecar read LOKF's schema from
#      GitHub. A tag can be moved, so every page that gives the URL names the
#      same commit. Each page also names the tag of the lokf floor that
#      templates/pyproject.toml sets, so the floor cannot move without the
#      pages. `git ls-remote https://github.com/nicholsn/lokf
#      'refs/tags/v<floor>^{}'` prints the commit a tag names.
say ""
say "Checking the no-Python schema URL names a commit, not a tag..."
lokf_floor="$(sed -n 's/.*"lokf\[build\]>=\([0-9.]*\)".*/\1/p' "$templates/pyproject.toml" | head -n 1)"
schema_url_re='(raw\.githubusercontent\.com/nicholsn/lokf|github\.com/nicholsn/lokf/blob)/[^/[:space:]<>()]+/lokf\.yaml'
mapfile -t schema_pages < <(grep -rlE "$schema_url_re" skills .lokf/README.md | sort)
mapfile -t schema_refs < <(grep -rhoE "$schema_url_re" skills .lokf/README.md | sed -E 's#^.*/nicholsn/lokf/(blob/)?##; s#/lokf\.yaml$##' | sort -u)
if (( ${#schema_pages[@]} == 0 )); then
  err "no page gives the no-Python schema URL - drop this check with the fallback, or fix its pattern"
elif [[ -z "$lokf_floor" ]]; then
  err "could not read the lokf floor from $templates/pyproject.toml"
else
  bad_refs="$(printf '%s\n' "${schema_refs[@]}" | grep -vxE '[0-9a-f]{40}' || true)"
  if [[ -n "$bad_refs" ]]; then
    err "the no-Python schema URL names $(tr '\n' ' ' <<<"$bad_refs")- a tag or a branch can be moved, so name the commit it points at instead"
  elif (( ${#schema_refs[@]} != 1 )); then
    err "the pages that give the no-Python schema URL pin ${#schema_refs[@]} different commits (${schema_refs[*]}) - pin one, the commit tagged v$lokf_floor"
  else
    ok "every page that gives the no-Python schema URL pins commit ${schema_refs[0]} (${#schema_pages[@]} pages)"
  fi
  for page in "${schema_pages[@]}"; do
    if grep -qF "v$lokf_floor" "$page"; then
      ok "$page names v$lokf_floor, the lokf floor its schema URL matches"
    else
      err "$page gives the no-Python schema URL but names no v$lokf_floor, the floor $templates/pyproject.toml sets - move the URL to the commit that tag names"
    fi
  done
fi

# 11c. Conventions rule 14, which reads the commits after a pull request's
#      base, is tested in tests/test_conventions.py.

# 12. Every line the preflight can print as missing or a warning has a row on
#     the sidecar's prerequisites page: what it means in plain words, who
#     fixes it and what to send them. tests/test_preflight.py tests the
#     preflight on this repository and on a bare directory, and each sidecar
#     script's refusal to run under sh.
say ""
say "Checking the prerequisites page explains each preflight line..."
prereq="skills/ktl-sidecar/references/prerequisites.md"
while IFS= read -r key; do
  if grep -q "^| \`$key\` |" "$prereq"; then
    ok "prerequisites.md explains the preflight's '$key' line"
  else
    err "prerequisites.md has no row for the preflight's '$key' line - add what it means, who fixes it and what to send them"
  fi
done < <(grep -oE '\b(miss|warn) [a-z]+' "$templates/scripts/knowledge-preflight.sh" | awk '{print $2}' | sort -u)

# 12w. The same for the website skill: every line its preflight can print as
#      missing or a warning has a row on its own prerequisites page.
say ""
say "Checking the website skill's prerequisites page explains each preflight line..."
wprereq="skills/ktl-website/references/prerequisites.md"
while IFS= read -r key; do
  if grep -q "^| \`$key\` |" "$wprereq"; then
    ok "ktl-website prerequisites.md explains the preflight's '$key' line"
  else
    err "ktl-website prerequisites.md has no row for the preflight's '$key' line - add what it means, who fixes it and what to send them"
  fi
done < <(grep -oE '\b(miss|warn) [a-z]+' skills/ktl-website/scripts/website-preflight.sh | awk '{print $2}' | sort -u)

# 12a. knowledge-feedback.sh, the recorder ktl-docent runs so that no other
#      reader's report enters its session, is tested in tests/test_feedback.py.

# 13. The forge-free provenance gate, with throwaway GPG and SSH keys, is
#     tested in tests/test_provenance.py.

# 13a. The gate's --unattended form, which needs no key and no forge, is
#      tested in tests/test_provenance.py.

# 14. CHANGELOG.md never carries two headings for one released version, and
#     changelog-release.mjs's promote merges a second qualifying push between
#     publish.yml runs into the unpublished section instead of adding one:
#     semantic-release.yml promotes on every push to main, but only
#     publish.yml tags. The first part reads the file and always runs; the
#     second tests the fold in a throwaway repository and needs node.
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
  # Set an identity: without one, git falls back to the OS account's GECOS
  # full name, which a CI runner's account does not carry.
  cl_git init -q \
    && cl_git config user.name contract \
    && cl_git config user.email contract@example.invalid \
    && cl_git commit -q --allow-empty -m base \
    && cl_git tag v0.18.0
  # The state after the first push's promote merged and a second push wrote
  # its Unreleased entry above it, with v0.19.0 still untagged. The second
  # push also carries the first one's entry, as a branch stacked on it does,
  # and the fold must list that entry once.
  cat > "$cl/repo/CHANGELOG.md" <<'EOF'
## [Unreleased]

### Added

- first push's entry

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
     && [[ "$(grep -c "first push's entry" "$cl/repo/CHANGELOG.md")" -eq 1 ]] \
     && grep -q "second push's entry" "$cl/repo/CHANGELOG.md" \
     && grep -qE '^## \[Unreleased\]$' "$cl/repo/CHANGELOG.md"; then
    ok "a second push before publish.yml tags folds into the one pending section, each entry once"
  else
    err "promote wrote $count heading(s) for 0.19.0 instead of folding, or listed an entry the section held twice"
  fi
  cl_git tag v0.19.0
  # promote left one empty "## [Unreleased]" at the top. Fill it in place:
  # readUnreleased reads only the first such heading, so it would never see
  # a second one.
  printf '\n### Fixed\n\n- a change after 0.19.0 shipped\n' \
    | sed -i '/^## \[Unreleased\]$/r /dev/stdin' "$cl/repo/CHANGELOG.md"
  (cd "$cl/repo" && node .github/scripts/changelog-release.mjs promote 0.19.1 2026-09-19 >/dev/null 2>&1)
  if [[ "$(grep -cE '^## \[0\.19\.[01]\]' "$cl/repo/CHANGELOG.md")" -eq 2 ]]; then
    ok "a version already tagged is left alone and the next one gets its own heading"
  else
    err "promote folded into 0.19.0 even though v0.19.0 is already tagged"
  fi
  # A push with nothing to release, such as a docs merge, after a promote and
  # before publish.yml: semantic-release still finds the feat since the last
  # tag and asks for the version already promoted. Unreleased is rightly
  # empty, so check must pass and notes must ask for no second promote.
  printf '## [Unreleased]\n\n## [0.20.0] - 2026-09-20\n\n### Added\n\n- promoted, not yet published\n\n## [0.19.1] - 2026-09-19\n' \
    > "$cl/repo/CHANGELOG.md"
  cl_out="$cl/github-output"
  : > "$cl_out"
  if (cd "$cl/repo" && node .github/scripts/changelog-release.mjs check 0.20.0 >/dev/null 2>&1) \
     && (cd "$cl/repo" && GITHUB_OUTPUT="$cl_out" node .github/scripts/changelog-release.mjs notes 0.20.0 >/dev/null 2>&1) \
     && [[ ! -s "$cl_out" ]] \
     && ! (cd "$cl/repo" && node .github/scripts/changelog-release.mjs check 0.21.0 >/dev/null 2>&1) \
     && ! (cd "$cl/repo" && node .github/scripts/changelog-release.mjs check >/dev/null 2>&1); then
    ok "a push with nothing new passes for the version already promoted, and fails for any other"
  else
    err "check or notes mishandled an empty Unreleased above the promoted, untagged 0.20.0"
  fi
  rm -rf "$cl"
else
  say "node not installed locally - CI runs check 14; skipping here"
fi

# 15. The librarian template's TRUST_LADDER_SKILLS_REF pins the release of
#     this repository that a host installs the skill from. Nothing fails when
#     the pin falls behind: the host keeps running an old librarian.
#
#     The pin must name a release that a host can clone, so it is held to one
#     of the two newest released headings in CHANGELOG.md. The newest heading
#     exists before its tag: semantic-release.yml promotes it on merge to
#     main, and publish.yml runs this contract before it creates the tag.
#     Two headings cover that window and still catch a stale pin, which falls
#     many versions behind, not one.
say ""
say "Checking the librarian template's skills pin is a current release..."
pin="$(grep -oE 'TRUST_LADDER_SKILLS_REF: v[0-9]+\.[0-9]+\.[0-9]+' \
         skills/ktl-sidecar/templates/github/knowledge-librarian.yaml | head -1 | sed 's/.*: //')"
pin_sha="$(grep -oE 'TRUST_LADDER_SKILLS_SHA: [0-9a-f]{40}' \
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
# The install step clones the pinned tag and copies one skills/ path out of
# it, so the tag must hold that path. After a rename, a current release and a
# real path can disagree with neither looking wrong, and every scheduled run
# on the host fails. CI checks out one commit without tags, and the newest
# heading is tagged after this contract runs, so the tag is often not here.
# The commit recorded beside the pin is an ancestor of this checkout, so the
# path is read from the commit the tag names where the clone has the tag,
# and otherwise from the recorded commit. The half skips only when the clone
# has neither.
# shellcheck disable=SC2016 # $tmp is the template's own literal, not ours
skill_path="$(grep -oE '\$tmp/skills/[A-Za-z0-9._-]+' \
                skills/ktl-sidecar/templates/github/knowledge-librarian.yaml \
                | head -1 | sed 's|^\$tmp/||')"
if [[ -z "$pin" ]]; then
  : # already reported above
elif [[ -z "$skill_path" ]]; then
  err "the librarian template's install step copies no skills/ path that check 15 can read - it cannot tell whether $pin carries the skill a host would install"
elif pin_commit="$(git rev-parse -q --verify "refs/tags/$pin^{commit}" 2>/dev/null)" \
     || { [[ -n "$pin_sha" ]] && pin_commit="$(git rev-parse -q --verify "$pin_sha^{commit}" 2>/dev/null)"; }; then
  if git ls-tree --name-only "$pin_commit" -- "$skill_path" | grep -qxF -- "$skill_path"; then
    ok "the commit $pin names (${pin_commit:0:12}) carries $skill_path, the path the install step copies out of it"
  else
    err "the librarian template pins $pin, whose commit ${pin_commit:0:12} has no $skill_path - the install step clones that tag and copies that path, so every scheduled run on a host scaffolded from this template fails there; this is what a rename does to a pin that still names a current release"
  fi
else
  say "skipping the pinned tag's contents: neither $pin nor its commit ${pin_sha:0:12} is on this clone"
fi
# The pin is a tag and the commit that tag names, since a tag can be moved and
# what it names is the instructions an agent follows unattended. The install
# step refuses a tag that names another commit, so the template's commit must
# be the one its tag names, and whatever moves the tag must move the commit
# too: the release step and the sync into a sibling. A shallow or tag-less
# checkout has no tag to compare, so this half skips there, and says whether
# the recorded commit is at least a real object here.
if [[ -z "$pin_sha" ]]; then
  err "no TRUST_LADDER_SKILLS_SHA beside the pin in the librarian template - a host would install whatever commit the tag names on the day"
elif [[ -z "$pin" ]] || ! git rev-parse -q --verify "refs/tags/$pin" >/dev/null; then
  if git rev-parse -q --verify "$pin_sha^{commit}" >/dev/null; then
    say "skipping the tag/commit agreement: ${pin:-the pin} is not a tag on this clone (its commit ${pin_sha:0:12} is a real object here)"
  else
    say "skipping the tag/commit agreement: neither ${pin:-the pin} nor its commit ${pin_sha:0:12} is on this clone"
  fi
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
for mover in .github/workflows/semantic-release.yml skills/ktl-sidecar/templates/scripts/knowledge-sync.sh; do
  if grep -qF 's/(TRUST_LADDER_SKILLS_REF: )' "$mover" && grep -qF 's/(TRUST_LADDER_SKILLS_SHA: )[0-9a-f]{40}/' "$mover"; then
    ok "$mover moves the pinned commit with the pinned tag"
  else
    err "$mover moves TRUST_LADDER_SKILLS_REF without TRUST_LADDER_SKILLS_SHA, so the install step would refuse the next pin it writes"
  fi
done
# Stage a commit that carries the skill path, with no tag for it, and confirm
# that the content half resolves the recorded commit and reads the path, as
# it must on a scheduled, tag-less checkout.
p15="$(mktemp -d)"
p15_git=(env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null git -C "$p15"
  -c init.defaultBranch=main -c user.name=contract -c user.email=contract@example.invalid -c commit.gpgsign=false)
"${p15_git[@]}" init -q
mkdir -p "$p15/skills/ktl-librarian"
printf 'name: ktl-librarian\n' > "$p15/skills/ktl-librarian/SKILL.md"
"${p15_git[@]}" add -A && "${p15_git[@]}" commit -q -m 'a release commit, left untagged'
p15_sha="$("${p15_git[@]}" rev-parse HEAD)"
if ! "${p15_git[@]}" rev-parse -q --verify "refs/tags/v9.9.9^{commit}" >/dev/null 2>&1 \
   && p15_commit="$("${p15_git[@]}" rev-parse -q --verify "refs/tags/v9.9.9^{commit}" 2>/dev/null || "${p15_git[@]}" rev-parse -q --verify "$p15_sha^{commit}" 2>/dev/null)" \
   && [[ "$p15_commit" == "$p15_sha" ]] \
   && "${p15_git[@]}" ls-tree --name-only "$p15_commit" -- skills/ktl-librarian | grep -qxF -- skills/ktl-librarian; then
  ok "check 15's content half resolves the recorded commit and reads the skill path when the tag ref is absent"
else
  err "check 15's content half could not read the skill path from the recorded commit without the tag"
fi
rm -rf "$p15"

# 16. The repository's old name, lokf-agent-skills, stays gone from every
#     file that speaks in the present tense. A branch written before the
#     rename merges without conflict and brings the name back, in a clone URL
#     or an `npx skills add` path that then depends on GitHub's redirect.
#     Only the files whose job is history keep it:
#       - CHANGELOG.md;
#       - the bundle's log.md, whose entries describe the repository as it
#         was on the day they were written;
#       - rename-plan.md, while it exists.
#     Anywhere else, replace it.
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
    if [[ -z "$skip" ]]; then unexpected+=("$f"); fi
  done <<<"$hits"
  if [[ "${#unexpected[@]}" -eq 0 ]]; then
    ok "no file outside the ones that record history reintroduces $old_name"
  else
    err "these files name $old_name again, which this repository was renamed from: ${unexpected[*]} - a branch written before the rename was merged; replace $old_name with knowledge-trust-ladder there (CHANGELOG.md, the bundle's log.md and the rename plan are the exceptions, because they record history)"
  fi
fi

# 16a. The old lokf- names of the skills and plugins, and the names before
#      those, stay gone the same way. Only CHANGELOG.md keeps them, for the
#      releases that carried them and the line telling a host what to remove.
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
#      them. CHANGELOG.md, the bundle's log.md and the dated maintainer notes
#      in the source map keep what was written at the time.
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
#     docent's, this repository's bundle builds inside Copilot's limits, and
#     one input gives one zip, since the release workflow attaches it.
say ""
say "Checking the Microsoft 365 Copilot skills build..."
m365="$templates/m365"
if [[ -n "$(find skills -path '*/templates/*' -iname 'SKILL.md' 2>/dev/null)" ]]; then
  err "a SKILL.md sits under a skill's templates/ - installers would list it as a skill; name an instructions file after the skill it builds (ktl-docent-m365.md)"
else
  ok "no SKILL.md under any skill's templates/"
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

# 17a. docs/install.md installs with `gh skill install --all`, and `npx skills
#      add` lists the same set, so every SKILL.md git tracks must be one of
#      the ktl- skills at skills/ktl-*/SKILL.md. Both installers discover a
#      SKILL.md anywhere in the tree, including under a prefix, so the walk
#      is the whole index and not skills/ alone.
say ""
say "Checking every tracked SKILL.md is a ktl- skill..."
stray_skills="$(git ls-files | grep -iE '(^|/)SKILL\.md$' | grep -vE '^skills/ktl-[a-z0-9-]+/SKILL\.md$' || true)"
if [[ -n "$stray_skills" ]]; then
  err "a SKILL.md outside skills/ktl-*/ would be installed by --all: $(printf '%s' "$stray_skills" | tr '\n' ' ')"
else
  ok "every tracked SKILL.md is at skills/ktl-*/SKILL.md ($(git ls-files 'skills/ktl-*/SKILL.md' | wc -l | tr -d ' ') skills), so --all installs the ktl- skills only"
fi

# 18. ktl-prose's check script runs on this repository's files: the bundle is
#     given its verdicts, and the skill's pages pass the style rules they
#     state. tests/test_prose_check.py tests what the script reports on staged
#     files, and what it refuses.
say ""
say "Running prose-check.py on this repository..."
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
expect_prose 0 "rewrite" "this repository's own bundle is given its verdicts" -- --bundle .lokf/knowledge
expect_prose 0 "OK" "the skill's own pages pass the style rules they state" -- skills/ktl-prose/SKILL.md skills/ktl-prose/references/*.md

# 19. knowledge-apply.sh --format prints the block that ktl-librarian's
#     references/patch.md shows, so a host learns the format from the script
#     it has, whatever release of the skill it runs. tests/test_apply.py
#     tests the pen's writes and refusals on a throwaway bundle.
say ""
say "Checking knowledge-apply.sh --format against patch.md..."
apply="$repo_root/$templates/scripts/knowledge-apply.sh"
# shellcheck disable=SC2016 # the backticks are a Markdown code fence, not a command
if diff <(bash "$apply" --format) <(awk '/^```yaml$/ {on = 1; next} /^```$/ {on = 0} on' skills/ktl-librarian/references/patch.md) >/dev/null; then
  ok "knowledge-apply.sh --format prints the block ktl-librarian's references/patch.md shows"
else
  err "knowledge-apply.sh --format and the yaml block in skills/ktl-librarian/references/patch.md differ - one was edited without the other"
fi

# 20. tests/test_report.py tests knowledge-report.sh on a throwaway
#     repository: the health line, each label, the work list, `changes`,
#     `quiet`, the retrieval test and the curator's queue (20a).

# 21. No tracked file holds a character a reader cannot see:
#       - a control character other than a tab or a line's closing carriage
#         return;
#       - a format character, such as a zero-width space, a byte order mark
#         or the right-to-left override that the "Trojan Source" attack
#         (CVE-2021-42574) hides code behind;
#       - a line or paragraph separator;
#       - a character of the pen's IGNORABLE class, which tests/test_apply.py
#         holds equal to the class below.
#     A diff shows none of them, and GitHub warns of only some. An agent that
#     types such a character's escape into a tool call can write the
#     character itself. Code that needs one spells it as an escape.
say ""
say "Searching tracked files for characters a reader cannot see..."
read -r -d '' unseen_py <<'PY' || true
import re, sys, unicodedata
hits = 0
IGNORABLE = re.compile("[\u034f\u115f\u1160\u17b4\u17b5\u180b-\u180f\u2065\u3164\ufe00-\ufe0f\uffa0\ufff0-\ufff8\U000e0000-\U000e0fff]")
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
            if kind in ("Cf", "Zl", "Zp") or (kind == "Cc" and char != "\t") or IGNORABLE.match(char):
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

# 22. Parser parity, which holds the gate's event reader to a YAML parser on
#     every layout a person might write, is tested in tests/test_provenance.py.

say ""
if [[ "$fail" -eq 0 ]]; then
  say "Repository contract: PASS"
  exit 0
else
  say "Repository contract: FAIL"
  exit 1
fi
