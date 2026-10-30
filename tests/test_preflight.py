"""knowledge-preflight.sh always ends on its summary line and exits 0, whatever the host lacks.

This was check 12 in scripts/validate-repository.sh. The preflight runs on
this repository, and on a bare directory with no bundle, no git and no skills,
where every section has to cope with absence rather than fail. It warns about
a CRLF file, counts a bundle reached through a link, and reads
`commit.gpgsign = yes` with no signing key as signing on. It names a sidecar
script that is missing beside its partner, and says when the gate would
install from a lock git does not hold. It warns when git is too old for an
ingest `git` entry, and when uv cannot install the packages the pen and the
conventions script run on. Each sidecar script run under sh stops on one line
that names bash.

The rows the sidecar's prerequisites page must carry for each preflight line
stay in the contract script: that is a fact about this repository's own pages.
"""

from __future__ import annotations

import os
import re
import shutil

import pytest

from conftest import REPO, SCRIPTS, TEMPLATES, WORKFLOWS, Git, bash, matches, mirror_uv, run, write

PREFLIGHT = SCRIPTS / "knowledge-preflight.sh"


def preflight(*args, cwd=None, env=None):
    return bash(PREFLIGHT, *args, cwd=cwd, env=env)


def test_runs_on_this_repository_and_ends_on_its_summary_line():
    result = preflight(".", cwd=REPO)
    assert result and matches(result.out, r"^Preflight: "), f"preflight failed on this repository: {result.out}"


def test_copes_with_a_bare_directory(tmp_path):
    result = preflight(cwd=tmp_path)
    assert (
        result
        and matches(result.out, r"^missing bundle")
        and matches(result.out, r"^info    git ")
        and matches(result.out, r"^Preflight: ")
    ), f"preflight misbehaves on a bare directory: {result.out}"


def test_warns_about_crlf_files_in_the_bundle(tmp_path):
    write(tmp_path / ".lokf" / "knowledge" / "x" / "a.md", "---\r\ntype: Service\r\n---\r\n")
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^warn    endings .*CRLF"), (
        f"preflight did not warn about a CRLF file: {result.out}"
    )


def test_counts_a_bundle_reached_through_a_link(tmp_path):
    write(tmp_path / "knowledge_bundle" / "x" / "a.md", "---\r\ntype: Service\r\n---\r\n")
    (tmp_path / ".lokf").mkdir()
    os.symlink("../knowledge_bundle", tmp_path / ".lokf" / "knowledge")
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^ok      bundle .*, 1 concepts"), (
        f"preflight did not read a linked bundle: {result.out}"
    )


def test_reads_gpgsign_yes_with_no_signing_key_as_signing_on(tmp_path):
    run(["git", "init", "-q", tmp_path])
    run(
        [
            "git",
            "-C",
            tmp_path,
            "-c",
            "user.name=c",
            "-c",
            "user.email=c@example.invalid",
            "commit",
            "-q",
            "--allow-empty",
            "--no-gpg-sign",
            "-m",
            "x",
        ]
    )
    run(["git", "-C", tmp_path, "config", "commit.gpgsign", "yes"])
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^ok      signing .*by committer email"), (
        f"preflight misread commit.gpgsign = yes: {result.out}"
    )


@pytest.fixture
def half_installed(tmp_path):
    """A host with a bundle, holding the conventions script without its Python half, and no feedback recorder."""
    write(tmp_path / ".lokf" / "knowledge" / "x" / "a.md", "---\ntype: Service\n---\n")
    scripts = tmp_path / ".lokf" / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy(SCRIPTS / "knowledge-conventions.sh", scripts)
    return tmp_path


def test_warns_when_the_conventions_parser_is_missing_beside_the_shell_half(half_installed):
    """On such a host the gate fails, so the preflight says so even with no sidecar installed."""
    result = preflight(half_installed)
    assert result and matches(result.out, r"^warn    copies .*knowledge-conventions\.py missing"), (
        f"preflight did not report the missing knowledge-conventions.py: {result.out}"
    )


def test_names_a_missing_feedback_recorder_until_it_is_there(half_installed):
    """A scripts/ directory with no knowledge-feedback.sh sends ktl-docent back to editing feedback.md by hand."""
    result = preflight(half_installed)
    assert result and matches(result.out, r"^warn    copies .*knowledge-feedback\.sh missing"), (
        f"preflight did not report the missing knowledge-feedback.sh: {result.out}"
    )
    shutil.copy(SCRIPTS / "knowledge-feedback.sh", half_installed / ".lokf" / "scripts")
    result = preflight(half_installed)
    assert result and "knowledge-feedback.sh missing" not in result.out, (
        f"preflight still reports knowledge-feedback.sh as missing after it was laid down: {result.out}"
    )



@pytest.fixture
def scripted(tmp_path):
    """A host with a bundle, the pen and the conventions script, and no .venv."""
    write(tmp_path / ".lokf" / "knowledge" / "x" / "a.md", "---\ntype: Service\n---\n")
    scripts = tmp_path / ".lokf" / "scripts"
    scripts.mkdir(parents=True)
    for name in ("knowledge-apply.sh", "knowledge-apply.py", "knowledge-conventions.sh", "knowledge-conventions.py"):
        shutil.copy(SCRIPTS / name, scripts)
    return tmp_path


def test_says_when_uv_lifts_the_date_for_the_scripts_behind_a_mirror(scripted, tmp_path):
    """Behind an index with no upload times, the scripts still run, as their own uv_ready lifts the date; the line says so."""
    path, log = mirror_uv(tmp_path, "PyYAML-6.0.3.tar.gz")
    result = preflight(scripted, env={"PATH": path})
    assert result and matches(result.out, r"^ok      scripts .*exclude-newer is lifted"), f"preflight did not report the lifted date: {result.out}"
    assert "--exclude-newer-package pyyaml=false" in log.read_text(), f"preflight did not install as the scripts do: {log.read_text()}"


def test_reports_scripts_uv_cannot_install_as_missing(scripted, tmp_path):
    """A host whose index uv cannot install from looked ready while the pen and the gate could not start."""
    fakebin = tmp_path / "fakebin"
    write(fakebin / "uv", "#!/bin/sh\necho 'x No solution found when resolving script dependencies:' >&2\nexit 1\n").chmod(0o755)
    write(fakebin / "python3", "#!/bin/sh\nexit 1\n").chmod(0o755)
    result = preflight(scripted, env={"PATH": f"{fakebin}{os.pathsep}{os.environ['PATH']}"})
    assert result and matches(result.out, r"^missing scripts .*knowledge-apply\.py and knowledge-conventions\.py \(x No solution found"), (
        f"preflight did not report the scripts uv could not install: {result.out}"
    )
    assert matches(result.out, r"^Preflight: [1-9]"), f"preflight did not count the scripts as missing: {result.out}"

def test_warns_when_the_gate_has_no_lock_in_git(tmp_path):
    """`uv sync --locked` fails when git holds no lock, so a host with the gate hears so before its next pull request does."""
    git = Git(tmp_path)
    git.init()
    write(
        tmp_path / ".lokf" / "knowledge" / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n"
    )
    shutil.copy(TEMPLATES / "pyproject.toml", tmp_path / ".lokf" / "pyproject.toml")
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    shutil.copy(WORKFLOWS / "knowledge-registrar.yaml", tmp_path / ".github" / "workflows")
    git("add", "-A")
    git("commit", "-q", "-m", "a host with the gate and no lock")
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^warn    toolkit .*uv\.lock is not in git"), (
        f"preflight did not report the missing .lokf/uv.lock: {result.out}"
    )
    write(tmp_path / ".lokf" / "uv.lock", "version = 1\n")
    git("add", "-A")
    git("commit", "-q", "-m", "the lock is committed")
    result = preflight(tmp_path)
    assert result and "uv.lock is not in git" not in result.out, (
        f"preflight still reports .lokf/uv.lock as missing after it was committed: {result.out}"
    )


@pytest.mark.parametrize(
    "script",
    [
        "knowledge-preflight.sh",
        "knowledge-conventions.sh",
        "knowledge-provenance.sh",
        "knowledge-feedback.sh",
        "knowledge-apply.sh",
        "knowledge-report.sh",
    ],
)
def test_run_under_sh_stops_and_names_bash(script):
    result = run(["sh", SCRIPTS / script, "x"])
    assert not result, f"{script} run under sh did not stop: {result.out}"
    assert matches(result.out, r"^run this with bash"), f"{script} run under sh failed some other way: {result.out}"


def test_warns_about_a_python3_older_than_the_scripts_need(tmp_path):
    fake = write(tmp_path / "fakebin" / "python3", "#!/bin/sh\necho 3.6\n")
    fake.chmod(0o755)
    result = preflight(tmp_path / "fakebin", env={"PATH": f"{fake.parent}{os.pathsep}{os.environ['PATH']}"})
    assert result and matches(result.out, r"^warn    python +python3 is 3\.6 .*uv run"), (
        f"preflight did not warn about python3 3.6: {result.out}"
    )


@pytest.mark.parametrize("top, url, version, warning", [
    ("", "https://git.acme.example/wiki.git", "2.36.6", r"this git is 2\.36, and a git entry that names a host needs 2\.37 or later: wiki"),
    ("allow_private_addresses: true\n", "http://git.lan/wiki.git", "2.30.9", r"this git is 2\.30, and every git entry needs 2\.31 or later: wiki"),
], ids=["a host name needs 2.37", "any entry needs 2.31"])
def test_warns_when_git_is_too_old_for_an_ingest_git_entry(tmp_path, top, url, version, warning):
    """The ingest refuses a git entry with a git older than it needs, 2.31 for any and 2.37 for one held to a host's address, so the preflight warns first."""
    write(tmp_path / ".lokf" / "ingest.yaml", f'ingest_version: "1"\n{top}entries:\n  - id: wiki\n    kind: git\n    url: {url}\n    ref: main\n')
    scripts = tmp_path / ".lokf" / "scripts"
    scripts.mkdir(parents=True)
    for name in ("knowledge-ingest.sh", "knowledge-ingest.py"):
        shutil.copy(SCRIPTS / name, scripts)
    fake = write(tmp_path / "fakebin" / "git", f'#!/bin/sh\n[ "$1" = "--version" ] && {{ echo "git version {version}"; exit 0; }}\nexec {shutil.which("git")} "$@"\n')
    fake.chmod(0o755)
    # Through a proxy that resolves names, git gets no pin and needs no 2.37, so the run names no proxy.
    unproxied = {name: "" for name in ("https_proxy", "HTTPS_PROXY", "all_proxy", "ALL_PROXY")}
    result = preflight(tmp_path, env={"PATH": f"{fake.parent}{os.pathsep}{os.environ['PATH']}", **unproxied})
    assert result and matches(result.out, r"^warn    ingest +.*" + warning), f"preflight did not warn about git {version}: {result.out}"


def test_warns_when_it_screens_the_sidecar_skill_itself(tmp_path):
    """A skill installed for one user sits outside every repository, so run from its folder the preflight screens that folder."""
    skill = tmp_path / "ktl-sidecar"
    write(skill / "SKILL.md", "---\nname: ktl-sidecar\n---\n")
    shutil.copy(PREFLIGHT, write(skill / "templates" / "scripts" / "knowledge-preflight.sh", ""))
    result = bash(skill / "templates" / "scripts" / "knowledge-preflight.sh", cwd=skill)
    assert result and matches(result.out, r"^warn    root .*skill's own folder"), (
        f"preflight screened the ktl-sidecar skill as if it were the host: {result.out}"
    )


def test_names_skills_installed_for_one_user(tmp_path):
    home = tmp_path / "home"
    write(home / ".copilot" / "skills" / "ktl-prose" / "SKILL.md", "---\nname: ktl-prose\n---\n")
    result = preflight(tmp_path, env={"HOME": home})
    assert result and matches(result.out, r"^info    skills +user scope: ~/\.copilot/skills: prose; the scheduled librarian"), (
        f"preflight did not name a skill installed for one user: {result.out}"
    )


def test_warns_when_run_from_a_folder_inside_the_sidecar_skill(tmp_path):
    skill = tmp_path / "ktl-sidecar"
    write(skill / "SKILL.md", "---\nname: ktl-sidecar\n---\n")
    script = write(skill / "templates" / "scripts" / "knowledge-preflight.sh", "")
    shutil.copy(PREFLIGHT, script)
    result = bash(script, cwd=script.parent)
    assert result and matches(result.out, r"^warn    root .*skill's own folder"), (
        f"preflight screened a folder inside the ktl-sidecar skill as if it were the host: {result.out}"
    )


def test_a_repository_that_holds_the_skill_is_not_the_skill():
    result = preflight(".", cwd=REPO)
    assert result and not matches(result.out, r"^warn    root "), f"preflight took the skills repository for the skill: {result.out}"


def test_warns_when_the_lock_was_made_against_another_index(tmp_path):
    host = tmp_path / "host"
    write(host / ".lokf" / "uv.lock", '[[package]]\nname = "lokf"\nsource = { registry = "https://pypi.org/simple" }\n')
    # uv's settings come from the environment and a user uv.toml, so the test
    # runs with neither, and with an empty configuration folder.
    clean = {"unset": ("UV_DEFAULT_INDEX", "UV_INDEX_URL")}
    config = {"XDG_CONFIG_HOME": tmp_path / "config"}
    result = run(["bash", PREFLIGHT, host], env={**config, "UV_DEFAULT_INDEX": "https://reader:s3cret@nexus.example/repository/pypi/simple"}, **clean)
    assert result and matches(result.out, r"^warn    lock         \.lokf/uv\.lock was made against pypi\.org, and uv here reads nexus\.example "), (
        f"preflight did not say the lock names another index than uv reads: {result.out}"
    )
    assert "s3cret" not in result.out and "reader" not in result.out, f"preflight printed an index URL's credentials: {result.out}"
    write(tmp_path / "config" / "uv" / "uv.toml", '[[index]]\nname = "corp"\nurl = "https://pypi.org/simple"\ndefault = true\n')
    result = run(["bash", PREFLIGHT, host], env=config, **clean)
    assert result and not matches(result.out, r"^warn    lock"), f"preflight warned about a lock made against the index uv reads: {result.out}"


@pytest.mark.skipif(shutil.which("uv") is None, reason="the toolkit lines need uv")
def test_warns_when_the_floor_is_below_what_the_recipes_need(tmp_path):
    """The recipes pass --check-excerpts, and --schema to convert and serve, which lokf 0.8.0 rejects."""
    pyproject = write(tmp_path / ".lokf" / "pyproject.toml", (TEMPLATES / "pyproject.toml").read_text().replace("lokf[build]>=0.9.0", "lokf[build]>=0.8.0"))
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^warn    toolkit +the floor is >=0\.8\.0 and the justfile's recipes need lokf 0\.9\.0"), (
        f"preflight did not warn about a 0.8.0 floor: {result.out}"
    )
    write(pyproject, (TEMPLATES / "pyproject.toml").read_text().replace("lokf[build]>=0.9.0", "lokf[build]>=0.10.0"))
    result = preflight(tmp_path)
    assert result and "the floor is" not in result.out, f"preflight read 0.10.0 as below 0.9.0: {result.out}"


@pytest.mark.skipif(shutil.which("uv") is None, reason="the toolkit lines need uv")
@pytest.mark.parametrize("copy, locked, stale", [
    ("0.8.0", "0.9.0", True),
    ("0.9.0", "0.9.0", False),
    ("0.9.1", "0.9.1", False),
    ("0.9.0", "0.9.1", True),
    (None, "0.9.0", False),
], ids=["an older copy", "the locked release's copy", "a lock above the floor", "a copy behind the lock", "no copy"])
def test_warns_when_the_pinned_core_schema_is_not_the_locked_lokfs(tmp_path, copy, locked, stale):
    """A domain schema imports .lokf/lokf.yaml, and the gate runs the lokf that uv.lock pins. Under lokf 0.9.0 a bare-date stale_after is a datetime, which 0.8.0's copy rejects.

    The floor stays >=0.9.0 in every case, so a lock on 0.9.1 with a copy to match gives no warning.
    """
    write(tmp_path / ".lokf" / "pyproject.toml", (TEMPLATES / "pyproject.toml").read_text())
    write(tmp_path / ".lokf" / "uv.lock", f'version = 1\n\n[[package]]\nname = "lokf"\nversion = "{locked}"\nsource = {{ registry = "https://pypi.org/simple" }}\n')
    if copy:
        write(tmp_path / ".lokf" / "lokf.yaml", f"id: https://w3id.org/lokf/schema\nname: lokf\nversion: {copy}\n")
    result = preflight(tmp_path)
    found = matches(result.out, rf"^warn    core +\.lokf/lokf\.yaml is lokf {re.escape(str(copy))}'s schema and the toolkit is lokf {re.escape(locked)} ")
    assert result and found == stale, f"preflight {'did not warn' if stale else 'warned'} about a {copy} copy under a lock on {locked}: {result.out}"


@pytest.mark.parametrize("line, table, warning", [
    ("", 'schema = "acme.yaml"', r"the justfile's schema line is empty - the recipes check against it, the release and the librarian do not"),
    ("other.yaml", "schema = 'acme.yaml'", r"the justfile's schema line is other\.yaml - the recipes check against the line"),
    ("acme.yaml", 'schema = "./acme.yaml"  # beside the bundle', None),
], ids=["the line is empty", "the two differ", "one file, spelt two ways"])
def test_warns_when_tool_lokf_names_another_schema_than_the_justfile(tmp_path, line, table, warning):
    """A lokf command given no --schema reads `[tool.lokf] schema`; the release and the librarian read only the justfile's line."""
    write(tmp_path / ".lokf" / "justfile", f'bundle := "knowledge"\nschema := "{line}"\n')
    write(tmp_path / ".lokf" / "pyproject.toml", f'[project]\nname = "x"\n\n[tool.lokf]\n{table}\n\n[tool.other]\nschema = "z.yaml"\n')
    result = preflight(tmp_path)
    if warning is None:
        assert result and not matches(result.out, r"^warn    schema"), f"preflight warned about one schema file: {result.out}"
    else:
        assert result and matches(result.out, r"^warn    schema +\[tool\.lokf\] schema in \.lokf/pyproject\.toml is acme\.yaml and " + warning), (
            f"preflight did not warn about the two schema settings: {result.out}"
        )
