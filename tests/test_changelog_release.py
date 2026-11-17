"""changelog-release.mjs reads and promotes CHANGELOG.md's Unreleased section for the release.

semantic-release.yml runs its `check`, `notes` and `promote` commands, and
contract check 14 runs the fold once. These tests run each command in a
throwaway git repository, and skip without node.
"""

from __future__ import annotations

import shutil

import pytest

from conftest import REPO, Git, read, run, write

SCRIPT = REPO / ".github" / "scripts" / "changelog-release.mjs"

pytestmark = pytest.mark.skipif(
    not (shutil.which("node") and shutil.which("git")),
    reason="node or git is not installed - the release jobs run changelog-release.mjs with both",
)

HEAD = "# Changelog\n\nAll notable changes are documented here.\n\n"
OLDER = "## [0.18.0] - 2026-09-16\n\n### Added\n\n- older\n"


@pytest.fixture
def repo(tmp_path):
    """A git repository whose only tag is v0.18.0, the last published release."""
    root = tmp_path / "repo"
    root.mkdir()
    git = Git(root)
    git.init()
    git("commit", "-q", "--allow-empty", "-m", "base")
    git("tag", "v0.18.0")
    return root


def changelog(root, *sections):
    """Write CHANGELOG.md as its head, the given sections and the published 0.18.0."""
    write(root / "CHANGELOG.md", HEAD + "\n".join([*sections, OLDER]))


def release(root, *args, output=None):
    env = {"GITHUB_OUTPUT": output} if output else None
    return run(["node", SCRIPT, *args], cwd=root, env=env, unset=("GITHUB_OUTPUT", "GITHUB_ACTIONS"))


def notes(root, *args, output=None):
    """The command's standard output alone, which semantic-release takes as the release notes."""
    env = {"GITHUB_OUTPUT": output} if output else None
    return run(["node", SCRIPT, "notes", *args], cwd=root, env=env, unset=("GITHUB_OUTPUT", "GITHUB_ACTIONS"), stdout_only=True)


def section(root, heading):
    """The lines under one `## ` heading, up to the next one."""
    lines = read(root / "CHANGELOG.md").split("\n")
    start = lines.index(heading)
    rest = lines[start + 1:]
    end = next((n for n, line in enumerate(rest) if line.startswith("## ")), len(rest))
    return "\n".join(rest[:end]).strip()


def headings(root):
    return [line for line in read(root / "CHANGELOG.md").split("\n") if line.startswith("## ")]


# check


def test_check_refuses_an_empty_section_and_passes_one_with_entries(repo):
    changelog(repo, "## [Unreleased]\n")
    empty = release(repo, "check")
    assert empty.rc == 1 and 'CHANGELOG.md\'s "## [Unreleased]" section is empty' in empty.out, empty.out
    assert release(repo, "check", "0.19.0").rc == 1, "a version nobody promoted has no notes"
    changelog(repo, "## [Unreleased]\n\n### Fixed\n\n- a fix\n")
    filled = release(repo, "check")
    assert filled and "characters to release" in filled.out, filled.out


def test_check_names_the_reason_as_an_annotation_inside_a_workflow(repo):
    changelog(repo, "## [Unreleased]\n")
    inside = run(["node", SCRIPT, "check"], cwd=repo, env={"GITHUB_ACTIONS": "true"})
    assert inside.rc == 1 and "::error title=CHANGELOG.md::" in inside.out, inside.out


def test_check_and_notes_pass_for_the_version_already_promoted_and_no_other(repo, tmp_path):
    """A docs merge after a promotion: semantic-release asks again for the version that waits for publish.yml."""
    changelog(repo, "## [Unreleased]\n", "## [0.19.0] - 2026-09-17\n\n### Added\n\n- promoted, not yet published\n")
    output = tmp_path / "github-output"
    write(output, "")
    waiting = release(repo, "check", "0.19.0")
    assert waiting and 'nothing new since "## [0.19.0]"' in waiting.out, waiting.out
    printed = notes(repo, "0.19.0", output=output)
    assert printed and printed.out == "### Added\n\n- promoted, not yet published", printed.out
    assert read(output) == "", "a version already promoted asks for no second promotion"
    assert release(repo, "check", "0.20.0").rc == 1, "another version would release with no notes"
    assert release(repo, "check").rc == 1
    Git(repo)("tag", "v0.19.0")
    assert release(repo, "check", "0.19.0").rc == 1, "a tagged version is published, so an empty section has nothing to release"


def test_a_file_without_the_heading_fails_every_command(repo):
    write(repo / "CHANGELOG.md", HEAD + OLDER)
    for args in (["check"], ["notes"], ["promote", "0.19.0", "2026-09-17"]):
        done = release(repo, *args)
        assert done.rc != 0 and 'has no "## [Unreleased]" heading' in done.out, f"{args}: {done.out}"
    assert read(repo / "CHANGELOG.md") == HEAD + OLDER


def test_a_command_the_script_does_not_know_prints_its_usage(repo):
    changelog(repo, "## [Unreleased]\n")
    for args in ([], ["release"]):
        done = release(repo, *args)
        assert done.rc == 1 and "usage: changelog-release.mjs <check|notes|promote>" in done.out, done.out


# notes


def test_notes_prints_the_section_and_names_the_next_version(repo, tmp_path):
    changelog(repo, "## [Unreleased]\n\n### Added\n\n- a feature\n\n### Fixed\n\n- a fix\n")
    output = tmp_path / "github-output"
    write(output, "")
    printed = notes(repo, "0.19.0", output=output)
    assert printed and printed.out == "### Added\n\n- a feature\n\n### Fixed\n\n- a fix", printed.out
    assert read(output) == "next_version=0.19.0\n"
    write(output, "")
    assert notes(repo, output=output).out == printed.out
    assert read(output) == "", "without a version there is none to name"
    assert notes(repo, "0.19.0").out == printed.out, "outside a workflow there is no file to write"


# promote


def test_promote_retitles_the_section_and_leaves_an_empty_one_above_it(repo, tmp_path):
    changelog(repo, "## [Unreleased]\n\n### Added\n\n- a feature\n")
    output = tmp_path / "github-output"
    write(output, "")
    done = release(repo, "promote", "0.19.0", "2026-09-17", output=output)
    assert done and 'promoted "## [Unreleased]" to "## [0.19.0] - 2026-09-17"' in done.out, done.out
    assert headings(repo) == ["## [Unreleased]", "## [0.19.0] - 2026-09-17", "## [0.18.0] - 2026-09-16"]
    assert section(repo, "## [Unreleased]") == ""
    assert section(repo, "## [0.19.0] - 2026-09-17") == "### Added\n\n- a feature"
    assert section(repo, "## [0.18.0] - 2026-09-16") == "### Added\n\n- older"
    assert read(repo / "CHANGELOG.md").startswith(HEAD + "## [Unreleased]\n\n## [0.19.0] - 2026-09-17\n\n### Added\n")
    assert read(output) == "released=true\nversion=0.19.0\n"


def test_promote_refuses_an_empty_section_and_a_call_without_a_date(repo):
    changelog(repo, "## [Unreleased]\n")
    before = read(repo / "CHANGELOG.md")
    empty = release(repo, "promote", "0.19.0", "2026-09-17")
    assert empty.rc == 1 and "refusing to promote nothing" in empty.out, empty.out
    changelog(repo, "## [Unreleased]\n\n- an entry\n")
    undated = release(repo, "promote", "0.19.0")
    assert undated.rc == 1 and "usage: changelog-release.mjs promote <version> <date>" in undated.out, undated.out
    assert read(repo / "CHANGELOG.md") == before.replace("## [Unreleased]\n", "## [Unreleased]\n\n- an entry\n")


def test_a_second_promote_before_the_tag_folds_into_the_pending_section(repo):
    """Two qualifying pushes between publish.yml runs: one heading, the newer version and date, each subsection once."""
    changelog(
        repo,
        "## [Unreleased]\n\n### Security\n\n- a hardening\n\n### Added\n\n- a second feature\n\n### Performance\n\n- a faster path\n",
        "## [0.19.0] - 2026-09-17\n\n### Added\n\n- a first feature\n\n### Fixed\n\n- a first fix\n",
    )
    done = release(repo, "promote", "0.20.0", "2026-09-18")
    assert done and 'folded "## [Unreleased]" into the unpublished "## [0.19.0]" section, now "## [0.20.0] - 2026-09-18"' in done.out, done.out
    assert headings(repo) == ["## [Unreleased]", "## [0.20.0] - 2026-09-18", "## [0.18.0] - 2026-09-16"]
    assert section(repo, "## [Unreleased]") == ""
    assert section(repo, "## [0.20.0] - 2026-09-18") == (
        "### Added\n\n- a first feature\n- a second feature\n\n### Fixed\n\n- a first fix\n\n### Security\n\n- a hardening\n\n### Performance\n\n- a faster path"
    ), "the subsections merge by title, in Keep a Changelog's order, with an unlisted title last"
    assert section(repo, "## [0.18.0] - 2026-09-16") == "### Added\n\n- older"


def test_promote_leaves_a_tagged_section_alone(repo):
    changelog(repo, "## [Unreleased]\n\n### Fixed\n\n- a change after 0.19.0 was published\n", "## [0.19.0] - 2026-09-17\n\n### Added\n\n- a first feature\n")
    Git(repo)("tag", "v0.19.0")
    assert release(repo, "promote", "0.19.1", "2026-09-19")
    assert headings(repo) == ["## [Unreleased]", "## [0.19.1] - 2026-09-19", "## [0.19.0] - 2026-09-17", "## [0.18.0] - 2026-09-16"]
    assert section(repo, "## [0.19.1] - 2026-09-19") == "### Fixed\n\n- a change after 0.19.0 was published"
    assert section(repo, "## [0.19.0] - 2026-09-17") == "### Added\n\n- a first feature"


def test_promote_outside_a_repository_says_it_could_not_list_the_tags(tmp_path):
    """The fold asks git whether the section under Unreleased is tagged, so it cannot guess without a repository."""
    bare = tmp_path / "no-repository"
    bare.mkdir()
    changelog(bare, "## [Unreleased]\n\n- an entry\n", "## [0.19.0] - 2026-09-17\n\n- pending\n")
    before = read(bare / "CHANGELOG.md")
    done = run(["node", SCRIPT, "promote", "0.20.0", "2026-09-18"], cwd=bare, env={"GIT_CEILING_DIRECTORIES": tmp_path})
    assert done.rc != 0 and "could not list tags" in done.out, done.out
    assert read(bare / "CHANGELOG.md") == before


# The fold lists each entry once.


def test_the_fold_leaves_out_an_entry_the_pending_section_already_holds(repo):
    """A branch stacked on another still carries the other's entry under Unreleased after the first promotion."""
    changelog(
        repo,
        "## [Unreleased]\n\n### Added\n\n- first push's entry\n\n### Fixed\n\n- second push's entry\n",
        "## [0.19.0] - 2026-09-17\n\n### Added\n\n- first push's entry\n",
    )
    assert release(repo, "promote", "0.19.0", "2026-09-18")
    assert section(repo, "## [0.19.0] - 2026-09-18") == "### Added\n\n- first push's entry\n\n### Fixed\n\n- second push's entry"


def test_a_subsection_whose_every_entry_is_held_adds_no_empty_heading(repo):
    changelog(
        repo,
        "## [Unreleased]\n\n### Changed\n\n- held already\n\n### Fixed\n\n- new\n",
        "## [0.19.0] - 2026-09-17\n\n### Added\n\n- held already\n",
    )
    assert release(repo, "promote", "0.19.0", "2026-09-18")
    assert section(repo, "## [0.19.0] - 2026-09-18") == "### Added\n\n- held already\n\n### Fixed\n\n- new"


def test_the_fold_leaves_out_a_held_entry_with_the_lines_under_it(repo):
    """An entry is its bullet and the indented lines that continue it. Left
    behind, those lines would read as part of the entry above."""
    held = "- first push's entry\n  with a second line\n  - and a nested point\n"
    changelog(
        repo,
        f"## [Unreleased]\n\n### Added\n\n- second push's entry\n{held}- third push's entry\n  with its own second line\n",
        f"## [0.19.0] - 2026-09-17\n\n### Added\n\n{held}",
    )
    assert release(repo, "promote", "0.19.0", "2026-09-18")
    assert section(repo, "## [0.19.0] - 2026-09-18") == (
        "### Added\n\n- first push's entry\n  with a second line\n  - and a nested point\n"
        "- second push's entry\n- third push's entry\n  with its own second line"
    )


def test_an_entry_that_differs_below_its_first_line_is_kept_whole(repo):
    changelog(
        repo,
        "## [Unreleased]\n\n### Added\n\n- the same first line\n  and a different second\n",
        "## [0.19.0] - 2026-09-17\n\n### Added\n\n- the same first line\n  and a second\n",
    )
    assert release(repo, "promote", "0.19.0", "2026-09-18")
    assert section(repo, "## [0.19.0] - 2026-09-18") == (
        "### Added\n\n- the same first line\n  and a second\n- the same first line\n  and a different second"
    )


# The heading is a line of its own.

QUOTED_HEAD = "# Changelog\n\nWrite each change under `## [Unreleased]` as you make it.\n\n"


def test_a_preamble_that_quotes_the_heading_is_not_the_section(repo):
    write(repo / "CHANGELOG.md", QUOTED_HEAD + "## [Unreleased]\n\n" + OLDER)
    empty = release(repo, "check")
    assert empty.rc == 1 and "section is empty" in empty.out, f"the quoted phrase was read as the section: {empty.out}"
    write(repo / "CHANGELOG.md", QUOTED_HEAD + "## [Unreleased]\n\n### Fixed\n\n- a fix\n\n" + OLDER)
    assert notes(repo).out == "### Fixed\n\n- a fix"
    assert release(repo, "promote", "0.19.0", "2026-09-17")
    assert read(repo / "CHANGELOG.md") == QUOTED_HEAD + "## [Unreleased]\n\n## [0.19.0] - 2026-09-17\n\n### Fixed\n\n- a fix\n\n" + OLDER


def test_an_entry_that_quotes_the_heading_stays_an_entry(repo):
    entry = "- **A push between releases promotes `## [Unreleased]` once**, and folds the rest.\n"
    changelog(repo, f"## [Unreleased]\n\n### Fixed\n\n{entry}", f"## [0.19.0] - 2026-09-17\n\n### Fixed\n\n{entry}- an earlier fix\n")
    assert notes(repo).out == "### Fixed\n\n" + entry.rstrip("\n")
    assert release(repo, "promote", "0.19.0", "2026-09-18")
    assert section(repo, "## [0.19.0] - 2026-09-18") == "### Fixed\n\n" + entry + "- an earlier fix"
    assert headings(repo) == ["## [Unreleased]", "## [0.19.0] - 2026-09-18", "## [0.18.0] - 2026-09-16"]


def test_the_heading_is_found_whatever_ends_its_line(repo):
    """A checkout with CRLF line endings, or a space left after the heading, still has its section."""
    write(repo / "CHANGELOG.md", (HEAD + "## [Unreleased]\n\n### Fixed\n\n- a fix\n\n" + OLDER).replace("\n", "\r\n"))
    assert notes(repo).out.split() == ["###", "Fixed", "-", "a", "fix"]
    write(repo / "CHANGELOG.md", HEAD + "## [Unreleased]  \n\n### Fixed\n\n- a fix\n\n" + OLDER)
    assert release(repo, "promote", "0.19.0", "2026-09-17")
    assert headings(repo) == ["## [Unreleased]", "## [0.19.0] - 2026-09-17", "## [0.18.0] - 2026-09-16"], "the new heading carries no space the next promote would trip on"
