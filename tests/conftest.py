"""Shared helpers for the behavioural tests of the sidecar scripts and the prose checker.

These tests exercise the scripts under skills/ktl-sidecar/templates/ and
skills/ktl-prose/scripts/ on throwaway bundles and repositories. Until
2026-10-07 they were contract checks 11 (its synthetic bundle), 11c, 12, 12a,
13, 13a, 18, 19, 20, 20a and 22 of scripts/validate-repository.sh, and the
layout tests of scripts/test-sidecar-layouts.sh. Each module says which check
it carries. The contract script keeps the checks that assert facts about this
repository's own files: that each copy matches its template, that the pins
name a release, that the hand-kept lists match the LOKF schema.

Together they are the guarantee a host inherits with its copies of the
templates: each script does what its skill's page says, on a bundle like the
host's, at the toolkit version the templates lock. A host tests only what it
changed: a copy it edited, which the preflight reports as drift, or a port of
the gate to another forge. skills/ktl-sidecar/references/portability.md says
so to the host.

Run them from the repository root:

    uv run --no-project --with-requirements tests/requirements.txt pytest

Every subprocess runs under an isolated git config, so a global
`commit.gpgsign=true` signs no fixture commit, and under a TMPDIR of pytest's
own, so a script's temporary files are removed with the test's.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
TEMPLATES = REPO / "skills" / "ktl-sidecar" / "templates"
SCRIPTS = TEMPLATES / "scripts"
WORKFLOWS = TEMPLATES / "github"
BOM = bytes([0xEF, 0xBB, 0xBF])


def esc(code_point: int) -> str:
    """The YAML escape for a code point, as ASCII text.

    A fixture that needs a zero-width space or a bidirectional mark writes the
    escape, never the character, so no file under tests/ holds a character a
    reader cannot see (contract check 21).
    """
    if code_point <= 0xFFFF:
        return "\\" + "u%04x" % code_point
    return "\\" + "U%08x" % code_point


def have(tool: str) -> bool:
    return shutil.which(tool) is not None


def today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


@dataclass
class Result:
    """A command's exit status and its output, with trailing newlines removed as `$(...)` removes them."""

    rc: int
    out: str

    def __bool__(self) -> bool:
        return self.rc == 0


def run(args, cwd=None, env=None, stdin=None, stdout_only=False, unset=()) -> Result:
    """Run a command. Its output is stdout and stderr together, as the shell tests read them with 2>&1, unless stdout_only."""
    full_env = dict(os.environ)
    for name in unset:
        full_env.pop(name, None)
    if env:
        full_env.update({k: str(v) for k, v in env.items()})
    done = subprocess.run(
        [str(a) for a in args],
        cwd=str(cwd) if cwd else None,
        env=full_env,
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL if stdout_only else subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return Result(done.returncode, done.stdout.rstrip("\n"))


def bash(script, *args, cwd=None, env=None, stdin=None, stdout_only=False) -> Result:
    return run(["bash", script, *args], cwd=cwd, env=env, stdin=stdin, stdout_only=stdout_only)


class Git:
    """git on one repository, with the identity and defaults the shell fixtures set on every call."""

    OPTIONS = (
        "-c",
        "init.defaultBranch=main",
        "-c",
        "user.name=contract",
        "-c",
        "user.email=contract@example.invalid",
        "-c",
        "commit.gpgsign=false",
    )

    def __init__(self, repo: Path):
        self.repo = Path(repo)

    def __call__(self, *args, env=None, check=True) -> str:
        result = run(["git", "-C", self.repo, *self.OPTIONS, *args], env=env)
        if check and result.rc != 0:
            raise RuntimeError(f"git {' '.join(str(a) for a in args)} failed in {self.repo}: {result.out}")
        return result.out

    def init(self) -> None:
        self("init", "-q")


def write(path: Path, content) -> Path:
    """Write text or bytes, creating the parent folders. Text keeps CRLF endings as written."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8", newline="")
    return path


def read(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")


def has_line(text: str, line: str) -> bool:
    """grep -qxF: one line is exactly this."""
    return line in text.split("\n")


def count_lines(text: str, needle: str) -> int:
    """grep -c: how many lines hold the text."""
    return sum(1 for line in text.split("\n") if needle in line)


def matches(text: str, pattern: str) -> bool:
    """grep -q with a regular expression, line by line."""
    return re.search(pattern, text, re.M) is not None


def replace_in(path: Path, old: str, new: str) -> None:
    """sed -i 's/old/new/': every occurrence, in place."""
    write(path, read(path).replace(old, new))


def tree_digest(root: Path, skip=("patch.yaml",)) -> str:
    """One digest for every file under root, so a refused patch can be shown to have written nothing."""
    digest = hashlib.md5()
    for path in sorted(p for p in Path(root).rglob("*") if p.is_file() and p.name not in skip):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


class Checks:
    """Soft assertions for a scenario whose steps build on one another.

    Each step records a finding instead of stopping the scenario, and done()
    fails the test with every finding, as the shell tests printed one line per
    finding and failed at the end.
    """

    def __init__(self):
        self.failed: list[str] = []

    def ok(self, condition, what: str, detail: str = "") -> bool:
        if not condition:
            self.failed.append(f"{what}: {detail}" if detail else what)
        return bool(condition)

    def done(self) -> None:
        if self.failed:
            pytest.fail(f"{len(self.failed)} check(s) failed:\n- " + "\n- ".join(self.failed), pytrace=False)


@pytest.fixture(scope="session", autouse=True)
def _isolated_environment(tmp_path_factory):
    patch = pytest.MonkeyPatch()
    patch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    patch.setenv("GIT_CONFIG_SYSTEM", "/dev/null")
    patch.setenv("TMPDIR", str(tmp_path_factory.getbasetemp()))
    yield
    patch.undo()


@pytest.fixture
def checks() -> Checks:
    c = Checks()
    yield c
    c.done()
