"""The `ktl` package on PyPI carries the skills unchanged, installs them, and checks them.

pyproject.toml builds a wheel that holds skills/ and .claude-plugin/ beside
the `ktl` command (src/ktl/cli.py), and alias/pyproject.toml builds
`knowledge-trust-ladder`, which holds no code and installs ktl at its own
version. A person at a site that reaches only a package index installs the
skills with that command, so it has to earn the trust the other installers
have:

- every file of every skill, and nothing else, byte for byte, with each
  script's executable bit;
- the folder each agent reads, at each scope, the project's being the
  repository's top folder, and a folder given by hand;
- one skill or all six, and a refusal of a name the package does not carry;
- an earlier copy replaced whole, so a file the new release dropped is gone,
  and left whole when a copy fails;
- a plain message, not a traceback, when a folder cannot be written;
- a status that tells this package's copy from a changed one, and reads a
  copy `gh skill install` rewrote as the same release;
- the standard library alone, on Python 3.9, the oldest Python the package
  claims;
- a build from the hashes .github/pypi/requirements.txt holds that makes the
  same bytes twice, into a folder holding the two files pypi.yml expects.

The command tests run the command from this checkout, where it finds the
skills in the repository. The wheel tests build the packages with uv, and
are skipped where uv is missing.
"""

from __future__ import annotations

import ast
import filecmp
import importlib
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
CONSTRAINTS = REPO / ".github" / "pypi" / "requirements.txt"


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


def as_gh_installs(skill_md: str, ref: str) -> str:
    """A SKILL.md as `gh skill install` leaves it: the keys sorted, a quote
    YAML does not need dropped, a metadata block naming the source, and no
    blank line after the frontmatter."""
    lines = skill_md.splitlines()
    end = lines.index("---", 1)
    head = {}
    for line in lines[1:end]:
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith("'") and ": " not in value and "#" not in value:
            value = value[1:-1].replace("''", "'")
        head[key] = value
    head["metadata"] = f"\n    github-path: skills/x\n    github-ref: {ref}\n    github-tree-sha: {'0' * 40}"
    rows = [f"{key}:{value}" if key == "metadata" else f"{key}: {value}" for key, value in sorted(head.items())]
    body = "\n".join(lines[end + 1 :]).lstrip("\n")
    return "\n".join(["---", *rows, "---", body]) + "\n"


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


def test_skills_with_no_action_lists_them_as_lokf_skills_does():
    run = ktl("skills")
    assert run.returncode == 0, run.stderr
    assert run.stdout == ktl("skills", "list").stdout


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
    assert sorted(p.name for p in dest.iterdir()) == ["ktl-docent"], "no staging folder is left behind"


def test_a_failed_copy_leaves_the_earlier_release_whole(tmp_path, monkeypatch):
    """Every skill is copied before any old one is swapped out, so a copy that fails part way changes nothing."""
    monkeypatch.syspath_prepend(str(SRC))
    cli = importlib.import_module("ktl.cli")
    dest = tmp_path / "skills"
    for name in ("ktl-curator", "ktl-docent"):
        (dest / name).mkdir(parents=True)
        (dest / name / "SKILL.md").write_text("an earlier release\n")
    copytree = shutil.copytree

    def copy_until_the_second_skill(source, target, *args, **kwargs):
        if Path(target).name == "ktl-docent":
            raise OSError(28, "No space left on device", str(target))
        return copytree(source, target, *args, **kwargs)

    monkeypatch.setattr(cli.shutil, "copytree", copy_until_the_second_skill)
    with pytest.raises(OSError):
        cli.install(["ktl-curator", "ktl-docent"], dest)
    for name in ("ktl-curator", "ktl-docent"):
        assert (dest / name / "SKILL.md").read_text() == "an earlier release\n", name
    assert sorted(p.name for p in dest.iterdir()) == ["ktl-curator", "ktl-docent"], "the staging folder is removed"


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


@pytest.mark.skipif(os.name == "nt" or os.geteuid() == 0, reason="needs a folder the user cannot write")
def test_install_says_plainly_when_it_cannot_write_the_folder(tmp_path):
    locked = tmp_path / "locked"
    locked.mkdir()
    locked.chmod(0o500)
    try:
        run = ktl("skills", "install", "--dest", str(locked / "skills"))
    finally:
        locked.chmod(0o700)
    assert run.returncode == 1
    assert run.stderr.startswith("ktl: Permission denied: "), run.stderr
    assert "Traceback" not in run.stderr


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


@pytest.mark.parametrize("marker", ["folder", "file"], ids=["a clone", "a worktree"])
def test_project_scope_is_the_repository_top_folder_from_any_folder_in_it(tmp_path, marker):
    project = tmp_path / "project"
    deeper = project / "docs" / "guides"
    deeper.mkdir(parents=True)
    if marker == "folder":
        (project / ".git").mkdir()
    else:
        (project / ".git").write_text("gitdir: /elsewhere/.git/worktrees/project\n")
    run = ktl("skills", "install", "--agent", "claude-code", "--scope", "project", "--skill", "ktl-prose", cwd=deeper, home=tmp_path)
    assert run.returncode == 0, run.stderr
    assert [p for p in tmp_path.rglob("SKILL.md")] == [project / ".claude" / "skills" / "ktl-prose" / "SKILL.md"]


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


def test_status_says_a_fresh_install_is_this_packages(tmp_path):
    dest = tmp_path / "skills"
    assert ktl("skills", "install", "--dest", str(dest)).returncode == 0
    run = ktl("skills", "status", "--dest", str(dest))
    assert run.returncode == 0, run.stdout + run.stderr
    for name in SKILLS:
        assert f"  {name:<14} same as this package\n" in run.stdout, run.stdout
    assert "not here" not in run.stdout


def test_status_names_what_changed_and_exits_1(tmp_path):
    dest = tmp_path / "skills"
    assert ktl("skills", "install", "--dest", str(dest), "--skill", "ktl-docent").returncode == 0
    (dest / "ktl-docent" / "references" / "added-by-hand.md").write_text("mine\n")
    run = ktl("skills", "status", "--dest", str(dest))
    assert run.returncode == 1
    assert "ktl-docent     differs from this package in 1 file (references/added-by-hand.md)" in run.stdout, run.stdout


def test_status_reads_a_copy_gh_rewrote_as_the_same_release(tmp_path):
    dest = tmp_path / "skills"
    assert ktl("skills", "install", "--dest", str(dest), "--skill", "ktl-docent").returncode == 0
    skill_md = dest / "ktl-docent" / "SKILL.md"
    skill_md.write_text(as_gh_installs(skill_md.read_text(encoding="utf-8"), "refs/tags/v9.9.9"), encoding="utf-8")
    script = next((dest / "ktl-docent" / "scripts").glob("*.sh"))
    script.chmod(0o644)
    run = ktl("skills", "status", "--dest", str(dest))
    assert run.returncode == 0, run.stdout
    assert (
        "ktl-docent     same as this package, though 1 script lost the executable bit; installed by gh skill from v9.9.9"
        in run.stdout
    ), run.stdout
    skill_md.write_text(skill_md.read_text(encoding="utf-8") + "A line the release does not hold.\n", encoding="utf-8")
    run = ktl("skills", "status", "--dest", str(dest))
    assert run.returncode == 1
    assert "differs from this package in 1 file (SKILL.md); installed by gh skill from v9.9.9" in run.stdout, run.stdout


def test_status_checks_each_agents_folder_at_both_scopes_and_names_the_empty_ones(tmp_path):
    home, project = tmp_path / "home", tmp_path / "project"
    home.mkdir()
    (project / ".git").mkdir(parents=True)
    assert ktl("skills", "install", "--agent", "claude-code", "--scope", "project", cwd=project, home=home).returncode == 0
    assert ktl("skills", "install", "--scope", "user", "--skill", "ktl-docent", cwd=project, home=home).returncode == 0
    run = ktl("skills", "status", cwd=project, home=home)
    assert run.returncode == 0, run.stdout
    assert f"{project / '.claude' / 'skills'} (read by claude-code, project)" in run.stdout, run.stdout
    assert "~/.copilot/skills (read by github-copilot, user)" in run.stdout, run.stdout
    assert "  not here       ktl-curator, ktl-librarian, ktl-prose, ktl-sidecar, ktl-website" in run.stdout, run.stdout
    assert "No KTL skill in " in run.stdout and "~/.agents/skills" in run.stdout, run.stdout


def test_the_command_imports_the_standard_library_alone():
    imported = set()
    for module in sorted((SRC / "ktl").glob("*.py")):
        for node in ast.walk(ast.parse(module.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                imported |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module != "__future__":
                imported.add(node.module.split(".")[0])
    imported.discard("ktl")
    assert imported, "the walk found the imports"
    assert imported <= set(sys.stdlib_module_names), imported - set(sys.stdlib_module_names)


uv = shutil.which("uv")
needs_uv = pytest.mark.skipif(uv is None, reason="uv is not installed")


def build(out: Path, source: Path) -> None:
    """Build as pypi.yml does, from the build backend at the hashes .github/pypi/requirements.txt holds."""
    subprocess.run(
        [uv, "build", "--quiet", "--build-constraints", str(CONSTRAINTS), "--require-hashes", "--out-dir", str(out), str(source)],
        check=True,
    )


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
def dist(tmp_path_factory) -> Path:
    if uv is None:
        pytest.skip("uv is not installed")
    out = tmp_path_factory.mktemp("dist")
    build(out / "ktl", REPO)
    build(out / "alias", REPO / "alias")
    return out


@pytest.fixture(scope="module")
def wheel(dist) -> Path:
    (built,) = (dist / "ktl").glob("ktl-*-py3-none-any.whl")
    return built


@needs_uv
def test_each_build_folder_holds_the_two_files_pypi_yml_expects(dist):
    (wheel_file,) = (dist / "ktl").glob("*.whl")
    version = wheel_file.name.split("-")[1]
    shown = {folder: sorted(p.name for p in (dist / folder).iterdir() if not p.name.startswith(".")) for folder in ("ktl", "alias")}
    assert shown == {
        "ktl": [f"ktl-{version}-py3-none-any.whl", f"ktl-{version}.tar.gz"],
        "alias": [f"knowledge_trust_ladder-{version}-py3-none-any.whl", f"knowledge_trust_ladder-{version}.tar.gz"],
    }


@needs_uv
def test_a_second_build_makes_the_same_bytes(dist, tmp_path):
    build(tmp_path / "ktl", REPO)
    build(tmp_path / "alias", REPO / "alias")
    for folder in ("ktl", "alias"):
        for file in (dist / folder).iterdir():
            if not file.name.startswith("."):
                assert filecmp.cmp(file, tmp_path / folder / file.name, shallow=False), file.name


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
    assert code == {"ktl/README.md", "ktl/__init__.py", "ktl/__main__.py", "ktl/cli.py", "ktl/gh.py"}


@needs_uv
def test_the_alias_holds_no_code_and_needs_ktl_at_its_own_version(dist):
    (alias_wheel,) = (dist / "alias").glob("*.whl")
    version = alias_wheel.name.split("-")[1]
    with zipfile.ZipFile(alias_wheel) as z:
        assert all(".dist-info/" in name for name in z.namelist()), z.namelist()
        info = f"knowledge_trust_ladder-{version}.dist-info"
        metadata = z.read(f"{info}/METADATA").decode()
        entry_points = z.read(f"{info}/entry_points.txt").decode()
    assert "Name: knowledge-trust-ladder" in metadata
    assert [line for line in metadata.splitlines() if line.startswith("Requires-Dist:")] == [f"Requires-Dist: ktl=={version}"]
    assert "knowledge-trust-ladder = ktl.cli:main" in entry_points


@needs_uv
def test_the_installed_wheels_install_the_skills(dist, tmp_path):
    venv = tmp_path / "venv"
    subprocess.run([uv, "venv", "--quiet", "--python", "3.9", str(venv)], check=True)
    bin_dir = venv / ("Scripts" if os.name == "nt" else "bin")
    python = bin_dir / ("python.exe" if os.name == "nt" else "python")
    wheels = [str(p) for p in sorted(dist.glob("*/*.whl"))]
    subprocess.run([uv, "pip", "install", "--quiet", "--no-index", "--python", str(python), *wheels], check=True)
    dest = tmp_path / "skills"
    command = bin_dir / ("knowledge-trust-ladder.exe" if os.name == "nt" else "knowledge-trust-ladder")
    run = subprocess.run([str(command), "skills", "install", "--dest", str(dest)], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    paths = [line.split(maxsplit=3)[3][len("skills/") :] for line in tracked("skills")]
    assert sorted(tree(dest)) == sorted(paths)
    for rel in paths:
        assert (dest / rel).read_bytes() == (REPO / "skills" / rel).read_bytes(), rel
    status = subprocess.run([str(bin_dir / "ktl"), "skills", "status", "--dest", str(dest)], capture_output=True, text=True)
    assert status.returncode == 0, status.stdout + status.stderr
