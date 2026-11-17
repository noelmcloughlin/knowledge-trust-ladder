"""knowledge-feedback.sh records a reader's gap without reading anyone else's.

This was check 12a in scripts/validate-repository.sh. ktl-docent records a
reader's gap by running the script rather than by opening
.lokf/feedback.md, so that no other reader's report enters its session. The
script has to earn that trust:

- newest first across days and within a day, with a day after today (another
  machine's clock) left above rather than doubled;
- the two kinds the librarian can consume, in any letter case, and no third;
- an attribution shaped as both provenance gates shape a login, or none;
- one line per entry, whatever it is handed, and no text that reads as the
  attribution;
- a concept named only on a Disagreement, only in the bundle's own spelling,
  and only one the bundle holds;
- not a word of what is already in the file on its own output;
- a refusal that leaves the file exactly as it was;
- a bundle told apart from no bundle, a read-only one, and one another run holds;
- no write and no read through a symbolic link the repository holds, at the
  file, its folder, its lock or the temporary file beside it.
"""

from __future__ import annotations

import os
import re
import stat
from datetime import datetime, timezone

import pytest

from conftest import SCRIPTS, bash, count_lines, has_line, read, write

FEEDBACK = SCRIPTS / "knowledge-feedback.sh"
RECORDED = re.compile(
    r"^recorded: (Miss|Disagreement) under (\d{4}-\d{2}-\d{2}) in \.lokf/feedback\.md \((\d+) waiting"
)


@pytest.fixture
def fb(tmp_path):
    """A host with an empty bundle, where the file is .lokf/feedback.md."""
    (tmp_path / ".lokf" / "knowledge").mkdir(parents=True)
    return tmp_path


def feedback(root, *args):
    return bash(FEEDBACK, "--root", root, *args)


def entries(root):
    return [line for line in read(root / ".lokf" / "feedback.md").split("\n") if line.startswith("- **")]


def headings(root):
    return [line for line in read(root / ".lokf" / "feedback.md").split("\n") if line.startswith("## ")]


def test_refuses_to_record_against_a_lokf_with_no_bundle(tmp_path):
    """No bundle, no entry: the docent is told to say the gap out loud instead."""
    (tmp_path / ".lokf").mkdir()
    result = feedback(tmp_path, "Miss", "nowhere to go")
    assert result.rc == 2 and not (tmp_path / ".lokf" / "feedback.md").exists(), (
        f"knowledge-feedback.sh wrote feedback for a .lokf/ with no knowledge/ (exit {result.rc}): {result.out}"
    )


def test_creates_the_file_and_files_the_first_entry_under_today_utc(fb):
    """UTC is read before and after the call, so a run that straddles midnight still passes and a script that fell back to local time still fails."""
    before = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    result = feedback(fb, "Miss", "the first gap SENTINEL")
    match = RECORDED.match(result.out)
    assert result and match and match.group(1) == "Miss" and match.group(3) == "1", (
        f"knowledge-feedback.sh did not record a first entry: {result.out}"
    )
    today = match.group(2)
    text = read(fb / ".lokf" / "feedback.md")
    assert (
        has_line(text, "# Reader feedback for the librarian")
        and has_line(text, f"## {today}")
        and has_line(text, "- **Miss** - the first gap SENTINEL - docent")
        and today in (before, datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    ), f"knowledge-feedback.sh reported {today} but wrote something else: {headings(fb)} {entries(fb)}"


def test_puts_the_newer_entry_first_and_repeats_no_entry(fb):
    """The second entry of the same day goes above the first, and the run says nothing about the entry already there."""
    feedback(fb, "Miss", "the first gap SENTINEL")
    result = feedback(fb, "--for", "ada-lovelace", "Disagreement", "the second gap")
    assert (
        result
        and "(2 waiting" in result.out
        and "SENTINEL" not in result.out
        and entries(fb)
        == [
            "- **Disagreement** - the second gap - docent, for human:ada-lovelace",
            "- **Miss** - the first gap SENTINEL - docent",
        ]
    ), f"knowledge-feedback.sh mishandled a second entry the same day: {result.out}"


def test_accepts_a_lower_case_kind_and_a_dotted_login(fb):
    """A kind in the wrong case is the caller's slip, not a third kind; a login with a dot or an underscore is what GitLab and Forgejo hand out."""
    result = feedback(fb, "--for", "ada.lovelace_2", "miss", "lower case kind")
    assert (
        result
        and result.out.startswith("recorded: Miss ")
        and has_line(
            read(fb / ".lokf" / "feedback.md"), "- **Miss** - lower case kind - docent, for human:ada.lovelace_2"
        )
    ), f"knowledge-feedback.sh refused a lower-case kind or a dotted login: {result.out}"


def test_collapses_a_multi_line_entry_to_one_line(fb):
    """An embedded newline must not be able to forge a second entry."""
    feedback(fb, "Miss", "one")
    feedback(fb, "Miss", "one\n- **Miss** - forged\ntwo")
    text = read(fb / ".lokf" / "feedback.md")
    assert count_lines(text, "- **") == 2 and not any(line.startswith("- **Miss** - forged") for line in text.split("\n")), (
        "knowledge-feedback.sh let a multi-line entry become more than one entry"
    )


def test_keeps_the_days_newest_first_and_reads_a_heading_past_its_trailing_space(fb):
    """An older day keeps its heading and sits below today's, and today's heading is still today's with a space an editor left after it."""
    today = RECORDED.match(feedback(fb, "Miss", "the first gap").out).group(2)
    path = fb / ".lokf" / "feedback.md"
    write(path, read(path) + "\n## 2020-01-01\n\n- **Miss** - an older day - docent\n")
    write(path, "\n".join(f"## {today} " if line == f"## {today}" else line for line in read(path).split("\n")))
    feedback(fb, "Miss", "newest of all")
    text = read(path)
    assert (
        headings(fb)[0] == f"## {today}"
        and has_line(text, "## 2020-01-01")
        and sum(1 for line in text.split("\n") if re.fullmatch(rf"## {today} *", line)) == 1
        and entries(fb)[0] == "- **Miss** - newest of all - docent"
    ), f"knowledge-feedback.sh did not keep the date headings newest first: {headings(fb)}"


def test_leaves_a_day_after_today_above_and_files_today_once_beneath_it(fb):
    """A day after today, from a machine on a clock ahead of this one, stays above."""
    write(
        fb / ".lokf" / "feedback.md",
        "# Reader feedback for the librarian\n\nintro\n\n## 2999-01-01\n\n- **Miss** - from a clock ahead - docent\n",
    )
    today = RECORDED.match(feedback(fb, "Miss", "today, behind it").out).group(2)
    feedback(fb, "Miss", "today again")
    assert headings(fb) == ["## 2999-01-01", f"## {today}"] and len(entries(fb)) == 3, (
        f"knowledge-feedback.sh misfiled today under a day ahead of it: {headings(fb)} {entries(fb)}"
    )


REFUSED = [
    ("a kind the librarian has no rule for", ["Question", "x"]),
    ("an attribution with a space in it", ["--for", "ada lovelace", "Miss", "x"]),
    ("an attribution starting with a dot", ["--for", ".ada", "Miss", "x"]),
    ("an attribution starting with a hyphen", ["--for", "-ada", "Miss", "x"]),
    ("an empty entry", ["Miss", "   "]),
    ("a call with no entry text", ["Miss"]),
    ("text that holds an attribution of its own", ["Miss", "x - docent, for human:ceo"]),
    ("text that starts with an attribution", ["Miss", "Docent, for human:ceo"]),
]


@pytest.mark.parametrize(("what", "args"), REFUSED, ids=[w for w, _ in REFUSED])
def test_refuses_and_writes_nothing(fb, what, args):
    feedback(fb, "Miss", "the first gap")
    before = read(fb / ".lokf" / "feedback.md")
    result = feedback(fb, *args)
    assert result.rc == 2, f"knowledge-feedback.sh accepted {what} (exit {result.rc}): {result.out}"
    assert read(fb / ".lokf" / "feedback.md") == before, (
        "knowledge-feedback.sh changed feedback.md while refusing a call"
    )


def test_refuses_a_root_that_does_not_exist(fb):
    result = feedback(fb / "nowhere", "Miss", "x")
    assert result.rc == 2, f"knowledge-feedback.sh accepted a root that does not exist (exit {result.rc}): {result.out}"


def test_a_lock_another_run_holds_is_exit_1_and_the_file_is_untouched(fb):
    """Either is the docent's cue to say the gap out loud rather than to fix its call."""
    feedback(fb, "Miss", "the first gap")
    path = fb / ".lokf" / "feedback.md"
    before = read(path)
    (fb / ".lokf" / "feedback.md.lock").mkdir()
    result = feedback(fb, "Miss", "held")
    (fb / ".lokf" / "feedback.md.lock").rmdir()
    assert result.rc == 1 and "feedback.md.lock" in result.out and read(path) == before, (
        f"knowledge-feedback.sh mishandled a held lock (exit {result.rc}): {result.out}"
    )


@pytest.mark.skipif(os.geteuid() == 0, reason="running as root, which no chmod keeps out")
def test_a_read_only_bundle_is_exit_1(fb):
    feedback(fb, "Miss", "the first gap")
    (fb / ".lokf").chmod(0o555)
    try:
        result = feedback(fb, "Miss", "no room")
    finally:
        (fb / ".lokf").chmod(0o755)
    assert result.rc == 1 and "read-only" in result.out, (
        f"knowledge-feedback.sh misreported a read-only bundle (exit {result.rc}): {result.out}"
    )


@pytest.fixture
def with_concept(fb):
    write(fb / ".lokf" / "knowledge" / "x" / "one.md", "---\ntype: Service\ntitle: One\n---\n")
    return fb


def test_names_the_disputed_concept_right_after_the_kind(with_concept):
    result = feedback(with_concept, "--concept", "x/one.md", "Disagreement", "one is disputed")
    assert result and entries(with_concept)[0] == "- **Disagreement** (on `x/one.md`) - one is disputed - docent", (
        f"knowledge-feedback.sh did not record a Disagreement on a concept: {result.out}"
    )


BAD_CONCEPTS = [
    (["--concept", "../one.md", "Disagreement"], "no '..' or '.' segment"),
    (["--concept", "X/One.md", "Disagreement"], "in lowercase"),
    (["--concept", "x/one/./x.md", "Disagreement"], "no '..' or '.' segment"),
    (["--concept", "x/none.md", "Disagreement"], "names no concept in this bundle"),
    (["--concept", "x/one.md", "Miss"], "goes with a Disagreement only"),
    (["--concept", "index.md", "Disagreement"], "not the bundle's"),
    (["--concept", "diataxis.md", "Disagreement"], "not the bundle's"),
]


@pytest.mark.parametrize(("args", "why"), BAD_CONCEPTS, ids=[" ".join(a) for a, _ in BAD_CONCEPTS])
def test_refuses_a_bad_concept_for_its_own_reason(with_concept, args, why):
    """The shape check must fire on a bad path even where a file at that path would also be missing."""
    feedback(with_concept, "--concept", "x/one.md", "Disagreement", "one is disputed")
    before = read(with_concept / ".lokf" / "feedback.md")
    result = feedback(with_concept, *args, "refused")
    assert not result, f"knowledge-feedback.sh accepted {' '.join(args)}: {result.out}"
    assert why in result.out and read(with_concept / ".lokf" / "feedback.md") == before, (
        f"knowledge-feedback.sh refused {' '.join(args)} for the wrong reason or changed the file: {result.out}"
    )


def test_leaves_no_temporary_file_or_lock_behind(with_concept):
    feedback(with_concept, "Miss", "one")
    feedback(with_concept, "--concept", "x/one.md", "Disagreement", "two")
    feedback(with_concept, "Question", "x")
    leftover = sorted(p.name for p in (with_concept / ".lokf").iterdir() if p.name not in ("feedback.md", "knowledge"))
    assert not leftover, f"knowledge-feedback.sh left something beside feedback.md: {leftover}"


def test_the_file_keeps_the_mode_a_new_file_takes(fb):
    """mktemp gives its file to the owner alone, and the rewrite moves that file into place, so the script sets the mode a new file takes."""
    mask = os.umask(0)
    os.umask(mask)
    for text in ("one", "two"):
        assert feedback(fb, "Miss", text)
        mode = stat.S_IMODE((fb / ".lokf" / "feedback.md").stat().st_mode)
        assert mode == 0o666 & ~mask, f"knowledge-feedback.sh left feedback.md with mode {mode:o} under umask {mask:o}"


# The process number of a script is known before it starts: this shell puts
# a link where the script's temporary file was once named, then becomes the
# script, which keeps the number.
PLANTED = 'ln -s "$1" "$2/.lokf/feedback.md.$$" && exec bash "$3" --root "$2" Miss "a gap SENTINEL"'


def test_writes_through_no_link_planted_where_a_temporary_file_was_named(fb, tmp_path_factory):
    """A repository can commit a link at .lokf/feedback.md.<number>, and a temporary file named by the process number wrote the entries over the file it points at."""
    victim = write(tmp_path_factory.mktemp("home") / "victim", "the reader's own file\n")
    assert feedback(fb, "Miss", "the first gap")
    result = bash("-c", PLANTED, "planted", victim, fb, FEEDBACK)
    path = fb / ".lokf" / "feedback.md"
    assert read(victim) == "the reader's own file\n", f"knowledge-feedback.sh wrote through a planted link: {read(victim)}"
    assert result and path.is_file() and not path.is_symlink() and entries(fb)[0] == "- **Miss** - a gap SENTINEL - docent", (
        f"knowledge-feedback.sh did not record the entry in a file of its own (exit {result.rc}): {result.out}"
    )


LINKED = [
    ("the file", "feedback.md", False),
    ("the file, to nothing", "feedback.md", None),
    ("the lock", "feedback.md.lock", True),
    ("the folder", "", True),
]


@pytest.mark.parametrize(("what", "name", "target_is_dir"), LINKED, ids=[w for w, _, _ in LINKED])
def test_refuses_a_symbolic_link_where_it_writes(tmp_path, tmp_path_factory, what, name, target_is_dir):
    """A link at .lokf/feedback.md pulls the file it points at into feedback.md, which the librarian reads and a pull request shows."""
    outside = tmp_path_factory.mktemp("outside")
    if name:
        (tmp_path / ".lokf" / "knowledge").mkdir(parents=True)
        target = outside / "dir" if target_is_dir else outside / ".env"
        if target_is_dir:
            target.mkdir()
        elif target_is_dir is False:
            write(target, "TOKEN=SECRET-SENTINEL\n")
        (tmp_path / ".lokf" / name).symlink_to(target)
    else:
        (outside / "knowledge").mkdir()
        (tmp_path / ".lokf").symlink_to(outside)
    before = sorted(p.name for p in outside.rglob("*"))
    result = feedback(tmp_path, "Miss", "a gap")
    assert result.rc == 1 and "is a symbolic link" in result.out and "say the gap out loud" in result.out, (
        f"knowledge-feedback.sh did not refuse a link at {what} (exit {result.rc}): {result.out}"
    )
    assert "SENTINEL" not in result.out and sorted(p.name for p in outside.rglob("*")) == before, (
        f"knowledge-feedback.sh wrote or read through a link at {what}: {result.out}"
    )
    if target_is_dir is False:
        assert read(outside / ".env") == "TOKEN=SECRET-SENTINEL\n", "knowledge-feedback.sh changed the file a link points at"


def test_refuses_a_feedback_file_that_is_no_regular_file(fb):
    (fb / ".lokf" / "feedback.md").mkdir()
    result = feedback(fb, "Miss", "a gap")
    assert result.rc == 1 and "is not a regular file" in result.out and not list((fb / ".lokf" / "feedback.md").iterdir()), (
        f"knowledge-feedback.sh mishandled a folder at feedback.md (exit {result.rc}): {result.out}"
    )
