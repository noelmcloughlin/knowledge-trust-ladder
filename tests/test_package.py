"""The `ktl` package on PyPI carries the skills unchanged, and installs them.

pyproject.toml builds a wheel that holds skills/ and .claude-plugin/ beside
the `ktl` command (src/ktl/cli.py). A person at a site that reaches only a
package index installs the skills with that command, so it has to earn the
trust the other installers have:

- every file of every skill, and nothing else, byte for byte, with each
  script's executable bit;
- the folder each agent reads, at each scope, and a folder given by hand;
- one skill or all six, and a refusal of a name the package does not carry;
- an earlier copy replaced whole, so a file the new release dropped is gone;
- the standard library alone, on Python 3.9, the oldest Python the package
  claims.

The command tests run the command from this checkout, where it finds the
skills in the repository. The wheel tests build the package with uv, and
are skipped where uv is missing.
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from conftest import REPO

SRC = REPO / "src"
SKILLS = sorted(p.parent.name for p in (REPO / "skills").glob("*/SKILL.md"))


def ktl(*args: str, cwd: Path | None = None, home: Path | None = None, python: list[str] | None = None):
    env = dict(os.environ, PYTHONPATH=str(SRC))
    if home is not None:
        env["HOME"] = str(home)
        env["USERPROFILE"] = str(home)
    return subprocess.run(
        [*(python or [sys.executable]), "-m", "ktl", *args],
        cwd=cwd or REPO,
        env=env,
        capture_output=True,
        text=True,
    )


def tracked(*paths: str) -> list[str]:
    out = subprocess.run(["git", "ls-files", "-s", *paths], cwd=REPO, capture_output=True, text=True, check=True)
    return [line for line in out.stdout.splitlines() if line]


def tree(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def test_the_six_skills_are_what_the_package_carries():
    assert SKILLS == [
        "ktl-curator",
        "ktl-docent",
        "ktl-librarian",
        "ktl-prose",
        "ktl-sidecar",
        "ktl-website",
    ]


def test_list_names_each_skill_with_its_first_sentence():
    run = ktl("skills", "list")
    assert run.returncode == 0, run.stderr
    rows = [line.split("\t") for line in run.stdout.splitlines()]
    assert [name for name, _ in rows] == SKILLS
    for name, summary in rows:
        assert summary.endswith("."), (name, summary)
        assert "''" not in summary, (name, summary)


def test_path_prints_the_skills_and_the_marketplace():
    assert ktl("skills", "path").stdout.strip() == str(REPO / "skills")
    marketplace = Path(ktl("skills", "path", "--marketplace").stdout.strip())
    assert (marketplace / ".claude-plugin" / "marketplace.json").is_file()
    assert (marketplace / "skills" / "ktl-docent" / "SKILL.md").is_file()


def test_install_copies_every_skill_byte_for_byte_with_its_modes(tmp_path):
    dest = tmp_path / "skills"
    run = ktl("skills", "install", "--dest", str(dest))
    assert run.returncode == 0, run.stderr
    assert "Installed 6 skills" in run.stdout
    expected = {}
    for line in tracked("skills"):
        mode, _, _, path = line.split(maxsplit=3)
        expected[path[len("skills/") :]] = mode
    assert sorted(tree(dest)) == sorted(expected)
    for rel, mode in expected.items():
        assert (dest / rel).read_bytes() == (REPO / "skills" / rel).read_bytes(), rel
        executable = bool((dest / rel).stat().st_mode & stat.S_IXUSR)
        assert executable == (mode == "100755"), rel


def test_install_replaces_an_earlier_copy_whole(tmp_path):
    dest = tmp_path / "skills"
    stale = dest / "ktl-docent" / "scripts" / "dropped-in-a-later-release.sh"
    stale.parent.mkdir(parents=True)
    stale.write_text("echo old\n")
    assert ktl("skills", "install", "--dest", str(dest), "--skill", "ktl-docent").returncode == 0
    assert not stale.exists()
    assert (dest / "ktl-docent" / "SKILL.md").is_file()
    assert sorted(p.name for p in dest.iterdir()) == ["ktl-docent"]


def test_install_follows_no_link_out_of_the_folder(tmp_path):
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    (outside / "keep.txt").write_text("mine\n")
    dest = tmp_path / "skills"
    dest.mkdir()
    (dest / "ktl-docent").symlink_to(outside, target_is_directory=True)
    assert ktl("skills", "install", "--dest", str(dest), "--skill", "ktl-docent").returncode == 0
    assert (outside / "keep.txt").read_text() == "mine\n"
    assert not (dest / "ktl-docent").is_symlink()
    assert (dest / "ktl-docent" / "SKILL.md").is_file()


@pytest.mark.parametrize(
    ("agent", "scope", "folder"),
    [
        ("claude-code", "user", "home/.claude/skills"),
        ("claude-code", "project", "project/.claude/skills"),
        ("codex", "user", "home/.agents/skills"),
        ("codex", "project", "project/.agents/skills"),
        ("github-copilot", "user", "home/.copilot/skills"),
        ("github-copilot", "project", "project/.agents/skills"),
    ],
)
def test_install_finds_each_agents_folder(tmp_path, agent, scope, folder):
    home, project = tmp_path / "home", tmp_path / "project"
    home.mkdir()
    project.mkdir()
    run = ktl("skills", "install", "--agent", agent, "--scope", scope, "--skill", "ktl-prose", cwd=project, home=home)
    assert run.returncode == 0, run.stderr
    assert (tmp_path / folder / "ktl-prose" / "SKILL.md").is_file()
    assert [p for p in tmp_path.rglob("SKILL.md")] == [tmp_path / folder / "ktl-prose" / "SKILL.md"]


@pytest.mark.parametrize(("scope", "folder"), [("user", "home/.copilot/skills"), ("project", "project/.agents/skills")])
def test_install_with_no_agent_named_serves_github_copilot(tmp_path, scope, folder):
    home, project = tmp_path / "home", tmp_path / "project"
    home.mkdir()
    project.mkdir()
    run = ktl("skills", "install", "--scope", scope, "--skill", "ktl-docent", cwd=project, home=home)
    assert run.returncode == 0, run.stderr
    assert [p for p in tmp_path.rglob("SKILL.md")] == [tmp_path / folder / "ktl-docent" / "SKILL.md"]


@pytest.mark.parametrize(
    ("args", "says"),
    [
        (["--skill", "ktl-nonesuch", "--dest", "x"], "no skill named ktl-nonesuch"),
        (["--agent", "codex"], "name the scope"),
        (["--agent", "codex", "--scope", "user", "--dest", "x"], "not both"),
        (["--scope", "user", "--dest", "x"], "not both"),
        ([], "name the scope"),
    ],
)
def test_install_refuses_what_it_cannot_do_and_writes_nothing(tmp_path, args, says):
    run = ktl("skills", "install", *args, cwd=tmp_path, home=tmp_path)
    assert run.returncode == 2
    assert says in run.stderr
    assert list(tmp_path.iterdir()) == []


def test_the_command_imports_the_standard_library_alone():
    source = (SRC / "ktl" / "cli.py").read_text()
    imported = {
        line.split()[1].split(".")[0]
        for line in source.splitlines()
        if line.startswith(("import ", "from ")) and not line.startswith("from __future__")
    }
    assert imported <= set(sys.stdlib_module_names), imported - set(sys.stdlib_module_names)


uv = shutil.which("uv")
needs_uv = pytest.mark.skipif(uv is None, reason="uv is not installed")


@needs_uv
def test_the_command_runs_on_python_3_9(tmp_path):
    run = ktl(
        "skills",
        "install",
        "--dest",
        str(tmp_path / "skills"),
        python=[uv, "run", "--no-project", "--python", "3.9", "python"],
    )
    assert run.returncode == 0, run.stderr
    assert sorted(p.name for p in (tmp_path / "skills").iterdir()) == SKILLS


@pytest.fixture(scope="module")
def wheel(tmp_path_factory) -> Path:
    if uv is None:
        pytest.skip("uv is not installed")
    out = tmp_path_factory.mktemp("dist")
    subprocess.run([uv, "build", "--quiet", "--out-dir", str(out), str(REPO)], check=True)
    (built,) = out.glob("ktl-*-py3-none-any.whl")
    return built


@needs_uv
def test_the_wheel_carries_the_skills_and_plugin_and_nothing_else(wheel):
    with zipfile.ZipFile(wheel) as z:
        members = {i.filename: i for i in z.infolist() if not i.filename.endswith("/")}
    carried = {name for name in members if name.startswith(("ktl/skills/", "ktl/.claude-plugin/"))}
    expected = {}
    for line in tracked("skills", ".claude-plugin"):
        mode, _, _, path = line.split(maxsplit=3)
        expected["ktl/" + path] = mode
    assert carried == set(expected)
    for name, mode in expected.items():
        wheel_mode = (members[name].external_attr >> 16) & 0o777
        assert bool(wheel_mode & stat.S_IXUSR) == (mode == "100755"), name
    code = {name for name in members if name.startswith("ktl/") and name not in carried}
    assert code == {"ktl/README.md", "ktl/__init__.py", "ktl/__main__.py", "ktl/cli.py"}


@needs_uv
def test_the_installed_wheel_installs_the_skills(wheel, tmp_path):
    venv = tmp_path / "venv"
    subprocess.run([uv, "venv", "--quiet", "--python", "3.9", str(venv)], check=True)
    python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    subprocess.run([uv, "pip", "install", "--quiet", "--no-index", "--python", str(python), str(wheel)], check=True)
    command = venv / ("Scripts/ktl.exe" if os.name == "nt" else "bin/ktl")
    dest = tmp_path / "skills"
    run = subprocess.run([str(command), "skills", "install", "--dest", str(dest)], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    paths = [line.split(maxsplit=3)[3][len("skills/") :] for line in tracked("skills")]
    assert sorted(tree(dest)) == sorted(paths)
    for rel in paths:
        assert (dest / rel).read_bytes() == (REPO / "skills" / rel).read_bytes(), rel
