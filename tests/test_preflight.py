"""knowledge-preflight.sh always ends on its summary line and exits 0, whatever the host lacks.

This was check 12 in scripts/validate-repository.sh. The preflight runs on
this repository, and on a bare directory with no bundle, no git and no skills,
where every section has to cope with absence rather than fail. It warns about
a CRLF file, counts a bundle reached through a link, and reads
`commit.gpgsign = yes` with no signing key as signing on. It names a sidecar
script that is missing beside its partner, and says when the gate would
install from a lock git does not hold. Each sidecar script run under sh stops
on one line that names bash.

The rows the sidecar's prerequisites page must carry for each preflight line
stay in the contract script: that is a fact about this repository's own pages.
"""

from __future__ import annotations

import os
import shutil

import pytest

from conftest import REPO, SCRIPTS, TEMPLATES, WORKFLOWS, Git, bash, matches, run, write

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
    """A host with that gate fails outright, so the preflight says so even with no sidecar installed."""
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
