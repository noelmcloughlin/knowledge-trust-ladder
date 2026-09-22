#!/usr/bin/env bash
# Isolated install smoke test. Installs four skills into a throwaway
# "consumer" repo via the open skills CLI, so generated agent directories
# never contaminate this distribution source.
#
# Usage:
#   scripts/smoke-test-install.sh                  # source = git origin remote
#   scripts/smoke-test-install.sh /path/to/local    # source = local path (pre-push)
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_arg="${1:-}"

if [[ -z "$source_arg" ]]; then
  source_arg="$(git -C "$repo_root" remote get-url origin 2>/dev/null || true)"
  if [[ -z "$source_arg" ]]; then
    echo "No source given and no git origin remote configured on $repo_root." >&2
    echo "Pass a local path or push the repo and set an origin remote first." >&2
    exit 1
  fi
fi

if ! command -v npx >/dev/null 2>&1; then
  echo "npx not found - install Node.js to run this smoke test." >&2
  exit 1
fi

test_root="$(mktemp -d)"
trap 'rm -rf "$test_root"' EXIT

echo "Source:    $source_arg"
echo "Test root: $test_root"

mkdir -p "$test_root/consumer"
(
  cd "$test_root/consumer"
  git init -q
  npx --yes skills add "$source_arg" \
    --skill ktl-librarian \
    --skill ktl-sidecar \
    --skill ktl-curator \
    --skill ktl-docent \
    --yes
)

echo ""
echo "Assertions:"
fail=0
assert() {
  local description="$1"
  local check="$2"
  if eval "$check"; then
    echo "OK:   $description"
  else
    echo "FAIL: $description"
    fail=1
  fi
}

assert "ktl-librarian discovered by name" \
  "[[ -n \"\$(find \"\$test_root/consumer\" -path \"*.agents/skills/ktl-librarian\" -o -path \"*.claude/skills/ktl-librarian\" 2>/dev/null)\" ]]"
assert "ktl-sidecar discovered by name" \
  "[[ -n \"\$(find \"\$test_root/consumer\" -path \"*.agents/skills/ktl-sidecar\" -o -path \"*.claude/skills/ktl-sidecar\" 2>/dev/null)\" ]]"
assert "ktl-librarian SKILL.md installed" \
  "[[ -n \"\$(find \"\$test_root/consumer\" -path \"*.agents/skills/ktl-librarian/SKILL.md\" -o -path \"*.claude/skills/ktl-librarian/SKILL.md\" 2>/dev/null)\" ]]"
assert "ktl-sidecar SKILL.md installed" \
  "[[ -n \"\$(find \"\$test_root/consumer\" -path \"*.agents/skills/ktl-sidecar/SKILL.md\" -o -path \"*.claude/skills/ktl-sidecar/SKILL.md\" 2>/dev/null)\" ]]"
assert "ktl-sidecar templates/ carried along" \
  "[[ -n \"\$(find \"\$test_root/consumer\" \( -path \"*.agents/skills/ktl-sidecar/templates\" -o -path \"*.claude/skills/ktl-sidecar/templates\" \) -type d 2>/dev/null)\" ]]"
assert "ktl-curator discovered by name" \
  "[[ -n \"\$(find \"\$test_root/consumer\" -path \"*.agents/skills/ktl-curator\" -o -path \"*.claude/skills/ktl-curator\" 2>/dev/null)\" ]]"
assert "ktl-curator SKILL.md installed" \
  "[[ -n \"\$(find \"\$test_root/consumer\" -path \"*.agents/skills/ktl-curator/SKILL.md\" -o -path \"*.claude/skills/ktl-curator/SKILL.md\" 2>/dev/null)\" ]]"
assert "ktl-docent discovered by name" \
  "[[ -n \"\$(find \"\$test_root/consumer\" -path \"*.agents/skills/ktl-docent\" -o -path \"*.claude/skills/ktl-docent\" 2>/dev/null)\" ]]"
assert "ktl-docent SKILL.md installed" \
  "[[ -n \"\$(find \"\$test_root/consumer\" -path \"*.agents/skills/ktl-docent/SKILL.md\" -o -path \"*.claude/skills/ktl-docent/SKILL.md\" 2>/dev/null)\" ]]"
assert "no installer metadata leaked back into this source repo" \
  "[[ -z \"\$(git -C \"\$repo_root\" status --porcelain --untracked-files=all -- .agents .claude skills-lock.json 2>/dev/null)\" ]]"

echo ""
if [[ "$fail" -eq 0 ]]; then
  echo "Smoke test: PASS"
else
  echo "Smoke test: FAIL"
  exit 1
fi
