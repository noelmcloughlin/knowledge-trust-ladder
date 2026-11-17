"""knowledge-m365.sh builds the Microsoft 365 Copilot skills from a bundle, as its header says.

The script is the template every host carries as .lokf/m365/knowledge-m365.sh,
and contract check 17 builds this repository's bundle with it. These tests run
a copy of the template folder on a small bundle of their own.
"""

from __future__ import annotations

import os
import shutil
import stat
import time
import zipfile

import pytest

from conftest import TEMPLATES, Git, bash, have, read, tree_digest, write

M365 = TEMPLATES / "m365"
EPOCH = 1700000000  # 2023-11-14T22:13:20Z
INDEX = "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n\n- [Term](glossary/term.md) - a term\n"
TERM = "---\ntype: GlossaryTerm\ntitle: Term\n---\n\nA term, with a second line.\n"
ROLE = "---\nname: second-role\ndescription: >\n  A second read-only role,\n  written as a block.\n---\n\n# second-role\n\nAnswer from the snapshot.\n"

needs_zip = pytest.mark.skipif(not have("zip"), reason="zip is not installed - the script builds the folder alone without it")


@pytest.fixture
def host(tmp_path):
    """A copy of the template folder, as a host carries it, and a bundle of two concepts outside any git repository."""
    shutil.copytree(M365, tmp_path / "m365")
    bundle = tmp_path / "host" / ".lokf" / "knowledge"
    write(bundle / "index.md", INDEX)
    write(bundle / "glossary" / "term.md", TERM)
    return tmp_path


def build(host, *args, bundle=None, out=None, env=None, epoch=EPOCH):
    """Run the host's copy of the script on its bundle, into out/ unless told otherwise."""
    full = {"GIT_CEILING_DIRECTORIES": host}
    if epoch is not None:
        full["SOURCE_DATE_EPOCH"] = epoch
    full.update(env or {})
    return bash(host / "m365" / "knowledge-m365.sh", *args, bundle or host / "host" / ".lokf" / "knowledge", out or host / "out", env=full)


def refused(host, result, status, text):
    """The run stopped with this status and this reason, and left nothing behind."""
    assert result.rc == status and text in result.out, f"wanted exit {status} and {text!r}: exit {result.rc}: {result.out}"
    assert not (host / "out").exists(), "a refused build left files behind"
    return True


# The build


def test_builds_a_folder_with_the_instructions_the_snapshot_and_the_concepts(host):
    bundle = host / "host" / ".lokf" / "knowledge"
    before = tree_digest(bundle)
    done = build(host, "--repo-url", "https://github.com/acme/widgets", "--ref", "v1.2.0")
    assert done, done.out
    skill = host / "out" / "ktl-docent-m365"
    assert read(skill / "SKILL.md") == read(M365 / "ktl-docent-m365.md"), "the instructions are copied unchanged"
    assert read(skill / "knowledge" / "index.md") == INDEX and read(skill / "knowledge" / "glossary" / "term.md") == TERM
    assert sorted(p.name for p in skill.iterdir()) == ["SKILL.md", "SNAPSHOT.md", "knowledge"]
    snapshot = read(skill / "SNAPSHOT.md").split("\n")
    for line in (
        "- Repository: https://github.com/acme/widgets",
        "- Revision: v1.2.0",
        "- Built: 2023-11-14 (UTC)",
        "- Source link pattern: https://github.com/acme/widgets/blob/v1.2.0/<path>",
    ):
        assert line in snapshot, f"SNAPSHOT.md lacks {line!r}: {snapshot}"
    assert any(line.startswith("- Report gaps to: https://github.com/acme/widgets/issues/new") for line in snapshot), snapshot
    assert f"built {host / 'out'}/ktl-docent-m365: 4 files, " in done.out, done.out
    assert "snapshot: https://github.com/acme/widgets at v1.2.0, built 2023-11-14" in done.out, done.out
    assert tree_digest(bundle) == before, "the build changed the source bundle"
    assert not list(host.glob("m365/*.zip")) and sorted(p.name for p in (host / "m365").iterdir()) == ["knowledge-m365.sh", "ktl-docent-m365.md"]


@pytest.mark.parametrize(
    "args, pattern, report",
    [
        (["--repo-url", "https://gitlab.com/acme/widgets", "--ref", "abc123"], "https://gitlab.com/acme/widgets/-/blob/abc123/<path>", "https://gitlab.com/acme/widgets/issues/new"),
        (["--repo-url", "https://github.com/acme/widgets"], "none - give the path and the revision", "https://github.com/acme/widgets/issues/new"),
        (["--repo-url", "https://git.acme.example/acme/widgets", "--ref", "v1"], "none - give the path and the revision", "the maintainers of https://git.acme.example/acme/widgets"),
        ([], "none - give the path and the revision", "the maintainers of the repository"),
    ],
    ids=["gitlab", "no revision", "another forge", "nothing recorded"],
)
def test_the_snapshot_says_how_to_link_a_source_and_where_to_report_a_gap(host, args, pattern, report):
    done = build(host, *args)
    assert done, done.out
    snapshot = read(host / "out" / "ktl-docent-m365" / "SNAPSHOT.md")
    assert f"- Source link pattern: {pattern}\n" in snapshot, snapshot
    assert f"- Report gaps to: {report}" in snapshot, snapshot
    if not args:
        assert "- Repository: not recorded\n- Revision: not recorded\n" in snapshot, snapshot
        assert "snapshot: repository not recorded at revision not recorded" in done.out, done.out


def test_each_instructions_file_beside_the_script_becomes_a_skill(host):
    """A new read-only role is another .md file in the folder, and shares the one snapshot."""
    write(host / "m365" / "second-role.md", ROLE)
    done = build(host)
    assert done, done.out
    for name in ("ktl-docent-m365", "second-role"):
        assert read(host / "out" / name / "knowledge" / "glossary" / "term.md") == TERM, name
        assert have("zip") == (host / "out" / f"{name}.zip").is_file(), name
    assert read(host / "out" / "second-role" / "SKILL.md") == ROLE
    assert read(host / "out" / "second-role" / "SNAPSHOT.md") == read(host / "out" / "ktl-docent-m365" / "SNAPSHOT.md")


def test_without_an_epoch_the_build_is_dated_now(host):
    before = time.strftime("%Y-%m-%d", time.gmtime())
    done = build(host, epoch=None, env={"SOURCE_DATE_EPOCH": ""})
    after = time.strftime("%Y-%m-%d", time.gmtime())
    assert done, done.out
    assert any(f"- Built: {day} (UTC)" in read(host / "out" / "ktl-docent-m365" / "SNAPSHOT.md") for day in (before, after))


# What the snapshot takes


@pytest.mark.skipif(not have("git"), reason="git is not installed")
def test_in_a_git_clone_only_tracked_files_reach_the_snapshot(host):
    bundle = host / "host" / ".lokf" / "knowledge"
    write(host / "host" / ".gitignore", "*.local.md\n")
    write(bundle / ".obsidian" / "app.json", "{}\n")
    git = Git(host / "host")
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "bundle")
    write(bundle / "notes.local.md", "an ignored note\n")
    write(bundle / "draft.md", "an untracked draft\n")
    write(bundle / "staged.md", "a staged concept\n")
    git("add", ".lokf/knowledge/staged.md")
    (bundle / "glossary" / "term.md").unlink()
    done = build(host)
    assert done, done.out
    kept = sorted(str(p.relative_to(host / "out" / "ktl-docent-m365" / "knowledge")) for p in (host / "out" / "ktl-docent-m365" / "knowledge").rglob("*") if p.is_file())
    assert kept == ["index.md", "staged.md"], "untracked, ignored, hidden and deleted files stay out; a staged one is tracked"
    assert "left out hidden files, which are tool state, not concepts: knowledge/.obsidian" in done.out, done.out


def test_outside_git_the_folder_is_copied_without_its_hidden_files(host):
    bundle = host / "host" / ".lokf" / "knowledge"
    write(bundle / ".obsidian" / "plugins" / "token.json", '{"token": "secret"}\n')
    write(bundle / "glossary" / ".DS_Store", "x")
    done = build(host)
    assert done, done.out
    built = host / "out" / "ktl-docent-m365"
    assert not [p for p in built.rglob(".*")], "a hidden file reached the skill"
    assert "knowledge/.obsidian" in done.out and "knowledge/glossary/.DS_Store" in done.out, done.out
    assert (bundle / ".obsidian" / "plugins" / "token.json").is_file(), "the source keeps its own hidden files"
    if have("zip"):
        with zipfile.ZipFile(host / "out" / "ktl-docent-m365.zip") as packed:
            assert not [n for n in packed.namelist() if "/." in n], packed.namelist()


# One input gives one zip


@needs_zip
def test_one_input_gives_the_same_zip_under_another_time_zone_and_umask(host):
    first = build(host, "--ref", "v1.2.0", out=host / "a", env={"TZ": "UTC"})
    old = os.umask(0o077)
    try:
        second = build(host, "--ref", "v1.2.0", out=host / "b", env={"TZ": "Asia/Tokyo"})
    finally:
        os.umask(old)
    assert first and second, first.out + second.out
    one, two = (host / "a" / "ktl-docent-m365.zip").read_bytes(), (host / "b" / "ktl-docent-m365.zip").read_bytes()
    assert one == two, "one input gave two zips"
    later = build(host, "--ref", "v1.2.0", out=host / "c", epoch=EPOCH + 86400)
    assert later and (host / "c" / "ktl-docent-m365.zip").read_bytes() != one, "the build date is part of the input"


@needs_zip
def test_the_zip_lists_sorted_names_at_the_epochs_time_with_fixed_modes(host):
    assert build(host)
    with zipfile.ZipFile(host / "out" / "ktl-docent-m365.zip") as packed:
        names = packed.namelist()
        assert names == sorted(names) == [
            "ktl-docent-m365/SKILL.md",
            "ktl-docent-m365/SNAPSHOT.md",
            "ktl-docent-m365/knowledge/glossary/term.md",
            "ktl-docent-m365/knowledge/index.md",
        ], names
        for info in packed.infolist():
            assert info.date_time == (2023, 11, 14, 22, 13, 20), f"{info.filename} is dated {info.date_time}"
            assert stat.S_IMODE(info.external_attr >> 16) == 0o644, f"{info.filename} has mode {oct(info.external_attr >> 16)}"
            assert info.extra == b"", f"{info.filename} carries an extra field, which holds a uid or a second time"
        assert packed.read("ktl-docent-m365/knowledge/glossary/term.md").decode() == TERM
    for path in (host / "out" / "ktl-docent-m365").rglob("*"):
        assert int(path.stat().st_mtime) == EPOCH, f"{path} is not dated at the epoch"


# The refusals


@pytest.mark.parametrize(
    "args, reason",
    [
        (["--repo-url", "http://github.com/acme/widgets"], "--repo-url must be a plain https URL"),
        (["--repo-url", "https://github.com/acme/widgets?tab=readme"], "--repo-url must be a plain https URL"),
        (["--repo-url", "https://github.com/acme/widgets); rm -rf x"], "--repo-url must be a plain https URL"),
        (["--ref", "v1.2.0 and more"], "--ref must be a tag or commit"),
        (["--ref", "$(id)"], "--ref must be a tag or commit"),
        (["--unknown"], "build: unknown option --unknown"),
        (["--repo-url"], "usage: .lokf/m365/knowledge-m365.sh"),
    ],
    ids=["http", "a query", "shell text in the URL", "a ref with spaces", "a ref with a command", "an unknown option", "an option without its value"],
)
def test_an_argument_that_is_not_plain_is_refused(host, args, reason):
    assert refused(host, build(host, *args), 2, reason)


def test_the_script_wants_a_bundle_and_an_out_folder_and_no_more(host):
    script = host / "m365" / "knowledge-m365.sh"
    for args in ([], [host / "host" / ".lokf" / "knowledge"], [host / "host" / ".lokf" / "knowledge", host / "out", "extra"], ["--help"]):
        done = bash(script, *args)
        assert refused(host, done, 2, "usage: .lokf/m365/knowledge-m365.sh [--repo-url URL] [--ref REF] <bundle-dir> <out-dir>"), args


def test_an_epoch_that_is_no_number_is_refused(host):
    assert refused(host, build(host, epoch="yesterday"), 2, "SOURCE_DATE_EPOCH must be seconds since the epoch, got 'yesterday'")


def test_a_folder_that_is_no_bundle_is_refused(host):
    assert refused(host, build(host, bundle=host / "host" / ".lokf"), 2, "is not a bundle folder (no index.md)")
    assert refused(host, build(host, bundle=host / "nowhere"), 2, "is not a bundle folder (no index.md)")


def test_a_skill_already_built_there_is_never_overwritten(host):
    assert build(host)
    built = tree_digest(host / "out", skip=())
    again = build(host)
    assert again.rc == 2 and "already exists - remove it or pick another <out-dir>; this script never overwrites a skill" in again.out, again.out
    assert tree_digest(host / "out", skip=()) == built
    shutil.rmtree(host / "out" / "ktl-docent-m365")
    if have("zip"):
        only_zip = build(host)
        assert only_zip.rc == 2 and "already exists" in only_zip.out, "a zip left from an earlier build counts too"


@pytest.mark.parametrize(
    "name, text, reason",
    [
        ("notes.md", "# Notes\n\nNo frontmatter here.\n", "has no frontmatter, so it cannot be a skill; move it out of this folder"),
        ("unnamed.md", "---\ndescription: A role.\n---\n\nBody.\n", "has no name: in its frontmatter"),
        ("other.md", "---\nname: second-role\ndescription: A role.\n---\n\nBody.\n", "must be named after its frontmatter name 'second-role'"),
        ("Second_Role.md", "---\nname: Second_Role\ndescription: A role.\n---\n\nBody.\n", "in lower-case letters, digits and hyphens"),
        ("second-role.md", "---\nname: second-role\n---\n\nBody.\n", "needs a description: of 1 to 1024 characters"),
        ("second-role.md", "---\nname: second-role\ndescription: " + "long " * 205 + "\n---\n\nBody.\n", "needs a description: of 1 to 1024 characters"),
    ],
    ids=["no frontmatter", "no name", "a name that is not the file's", "a name Copilot refuses", "no description", "a description too long"],
)
def test_an_instructions_file_that_cannot_be_a_skill_refuses_the_run(host, name, text, reason):
    write(host / "m365" / name, text)
    assert refused(host, build(host), 2, reason)


def test_a_folder_with_no_instructions_file_is_refused(host):
    (host / "m365" / "ktl-docent-m365.md").unlink()
    assert refused(host, build(host), 2, "no instructions file beside")


# Copilot's limits


def over_a_limit(host, reason):
    done = build(host)
    assert refused(host, done, 1, reason)
    assert f"build: nothing written to {host / 'out'}" in done.out, done.out


def test_a_link_in_the_bundle_is_refused_not_followed(host):
    bundle = host / "host" / ".lokf" / "knowledge"
    write(host / "outside.md", "a file outside the bundle\n")
    (bundle / "glossary" / "linked.md").symlink_to(host / "outside.md")
    over_a_limit(host, "ktl-docent-m365: the bundle holds links, which this build refuses to follow: knowledge/glossary/linked.md")


def test_a_file_more_than_three_folders_deep_is_refused(host):
    bundle = host / "host" / ".lokf" / "knowledge"
    write(bundle / "a" / "b" / "ok.md", "three folders deep, with knowledge/\n")
    assert build(host), "knowledge/a/b/ is three folders, which Copilot takes"
    shutil.rmtree(host / "out")
    write(bundle / "a" / "b" / "c" / "deep.md", "four folders deep\n")
    over_a_limit(host, "these files sit more than 3 directories deep: knowledge/a/b/c/deep.md")


def test_a_file_type_copilot_does_not_accept_is_refused(host):
    bundle = host / "host" / ".lokf" / "knowledge"
    write(bundle / "tools" / "run.sh", "#!/bin/sh\n")
    write(bundle / "LICENSE", "no extension\n")
    done = build(host)
    assert refused(host, done, 1, "Copilot does not accept these file types:")
    assert "knowledge/tools/run.sh" in done.out and "knowledge/LICENSE" in done.out, done.out


def test_more_than_350_files_are_refused(host):
    bundle = host / "host" / ".lokf" / "knowledge"
    for n in range(347):
        write(bundle / "many" / f"c{n:03}.md", "x\n")
    over_a_limit(host, "ktl-docent-m365: 351 files; Copilot allows 350 across all of an agent's skills")
    (bundle / "many" / "c000.md").unlink()
    done = build(host)
    assert done and ": 350 files, " in done.out, done.out


def test_instructions_of_20000_characters_are_refused(host):
    write(host / "m365" / "second-role.md", ROLE + "x" * 20000 + "\n")
    done = build(host)
    assert refused(host, done, 1, "second-role: SKILL.md instructions are ")
    assert "Copilot allows under 20,000" in done.out, "one skill over a limit refuses every skill of the run"


def test_ten_megabytes_are_refused(host):
    write(host / "host" / ".lokf" / "knowledge" / "big.md", "0123456789abcde\n" * (10 * 1024 * 64))
    over_a_limit(host, "KB; the whole app package, this skill included, must stay under 10 MB")


# Without zip


def path_without(folder, *tools):
    """A PATH of one folder that links to every command on this PATH but the named ones."""
    folder.mkdir()
    for source in os.environ["PATH"].split(os.pathsep):
        if not os.path.isdir(source):
            continue
        for name in os.listdir(source):
            link, target = folder / name, os.path.join(source, name)
            if name in tools or link.is_symlink() or not (os.path.isfile(target) and os.access(target, os.X_OK)):
                continue
            link.symlink_to(target)
    return str(folder)


def test_without_zip_the_folder_is_built_and_the_script_says_so(host):
    done = build(host, env={"PATH": path_without(host / "bin", "zip")})
    assert done, done.out
    assert "build: zip not found, so no ktl-docent-m365.zip; zip the folder before adding it" in done.out, done.out
    assert (host / "out" / "ktl-docent-m365" / "SKILL.md").is_file() and not (host / "out" / "ktl-docent-m365.zip").exists()
