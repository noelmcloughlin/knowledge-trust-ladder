"""Tests of this repository's own scripts and workflows, the ones no skill installs.

1. scripts/smoke-test-install.sh fails when the install leaves installer
   metadata in this source repository, though .gitignore ignores all three
   paths, and passes when the metadata was there before it ran.
"""

from __future__ import annotations

import shutil

import pytest

from conftest import REPO, Git, read, run, write

SMOKE = REPO / "scripts" / "smoke-test-install.sh"

# A stand-in for npx: `skills add` writes .agents/ into the source repository
# when LEAK is set, as a misbehaving installer would.
FAKE_NPX = """#!/usr/bin/env bash
if [ -n "${LEAK:-}" ]; then mkdir -p "$LEAK/.agents/skills/x"; : > "$LEAK/.agents/skills/x/SKILL.md"; fi
exit 0
"""


@pytest.fixture
def source(tmp_path):
    """A source repository with the real script and .gitignore, an ignored .claude/ already in it, and a fake npx on PATH."""
    repo = tmp_path / "source"
    write(repo / "scripts" / "smoke-test-install.sh", read(SMOKE))
    write(repo / ".gitignore", read(REPO / ".gitignore"))
    write(repo / ".claude" / "settings.local.json", "{}\n")
    git = Git(repo)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    bin_dir = tmp_path / "bin"
    write(bin_dir / "npx", FAKE_NPX)
    (bin_dir / "npx").chmod(0o755)
    return repo, bin_dir


def smoke(repo, bin_dir, leak):
    env = {"PATH": f"{bin_dir}:/usr/bin:/bin"}
    if leak:
        env["LEAK"] = str(repo)
    return run(["bash", repo / "scripts" / "smoke-test-install.sh", repo], env=env)


@pytest.mark.skipif(not shutil.which("git"), reason="git is not installed")
def test_the_smoke_tests_leak_check_sees_an_ignored_path_and_only_a_new_one(source):
    repo, bin_dir = source
    clean = smoke(repo, bin_dir, leak=False)
    assert "OK:   no installer metadata leaked back into this source repo" in clean.out, clean.out
    leaked = smoke(repo, bin_dir, leak=True)
    assert "FAIL: no installer metadata leaked back into this source repo" in leaked.out, leaked.out
