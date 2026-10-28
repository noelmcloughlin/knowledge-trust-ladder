"""knowledge-report.sh computes what the skills used to have a model work out, so it has to get the arithmetic right on every layout the format allows.

This was checks 20 and 20a in scripts/validate-repository.sh:

- the health line;
- each label, with a same-day edit told from its confirmation by the two
  times compared whole;
- a retired concept counted once;
- events written as a block list, a flow sequence or a bare mapping;
- an open question read only under its real heading.

A source has moved when history, not a clock, puts its last commit after the
one that recorded the event, or when it carries an uncommitted edit; one
changed in the same commit has not. No reader's words leave the script,
except inside the one prompt the retrieval test builds. The script scores the
reply by program: against what the ledger expects and never against a line of
the reply, and without a question whose concept has left the bundle. `changes`
says what a change does to each confirmed concept's label. `quiet` and the
work list set a moved source aside once the librarian's own question covers
it, and set aside what a person declined by closing the workflow's pull
request, until it changes again.

The whole report also ranks the curator's queue (check 20a):

- how many other concepts rely on each concept, read from every spelling of a
  typed relation, each citing concept once and never a concept for itself;
- a review date due within 30 days;
- a confirmed concept derived from one edited after that confirmation;
- the five concepts worth ten minutes today, in trust-fields.md's order.

A retired concept's label names its successor from the newest **Deprecation**
line in log.md, and only one the bundle holds. A waiting Disagreement that
names its concept right after the kind marks that concept, from its newest
day.

A retired concept whose successor no person has confirmed is listed with that
successor's label, and only when the bundle holds the successor: exclusion
follows affirmation. A review date is read by its day, so a datetime value
counts from the day it names.
"""

from __future__ import annotations

import re
import shutil
from datetime import datetime, timedelta, timezone

import pytest

from conftest import BOM, SCRIPTS, Git, bash, has_line, matches, read, replace_in, run, write

REPORT = SCRIPTS / "knowledge-report.sh"


def report(root, *args, env=None):
    return bash(REPORT, *args, cwd=root, env=env)


def lines(*parts):
    return "\n".join(parts) + "\n"


def append(path, text):
    write(path, read(path) + text)


@pytest.fixture
def kr(tmp_path):
    """Sources and concepts committed together: every layout of an event, a retired concept, an answered question and a gone source."""
    kk = tmp_path / ".lokf" / "knowledge"
    write(tmp_path / "src" / "a.md", "a\n")
    write(tmp_path / "src" / "b.md", "b\n")
    write(tmp_path / "src" / "c.md", "c\n")
    write(
        kk / "index.md",
        "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n\n# X\n\n* [Confirmed](x/confirmed.md) - a confirmed concept about widgets.\n* [Draft one](x/draft.md) - a draft about gadgets.\n",
    )
    # confirmed.md confirms with a `+00:00` offset, and edited.md stamps its
    # edit with one: each must be converted to UTC, not dropped.
    write(
        kk / "x" / "confirmed.md",
        '---\ntype: Service\ntitle: Confirmed\nresource: src/a.md\nsources:\n- resource: src/a.md\n- resource: src/c.md\n- resource: https://example.invalid/never-fetched\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\nverified:\n- by: human:ada\n  at: "2026-01-02T10:00:00+00:00"\n  revision: "3f9c2a1b7e0d4c6a8f5e2d1c9b8a7f6e5d4c3b2a"\nstale_after: 2020-01-01\n---\n\n# Overview\n',
    )
    write(
        kk / "x" / "edited.md",
        '---\ntype: Service\ntitle: Edited\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-02T14:00:00+00:00"\nverified:\n  - by: human:ada\n    at: "2026-01-02T10:00:00Z"\n---\n',
    )
    # auto.md confirms in a flow sequence that spans lines, and gone.md
    # carries an empty flow list: one process event, and no event.
    write(
        kk / "x" / "auto.md",
        '---\ntype: Service\ntitle: Auto\nresource: src/b.md\nverified: [\n  { by: process:ktl-librarian, at: "2026-01-03T00:00:00Z" }\n]\n---\n',
    )
    write(
        kk / "x" / "draft.md",
        "---\ntype: Service\ntitle: Draft one\nstatus: draft\n---\n\n# Overview\n\n```markdown\n## Open questions\n\n- 2026-01-01, human:example: only an example in a fence\n```\n\n## Open questions\n\n- 2026-01-05, human:ada: send it back, with these words for the curator\n",
    )
    # reopened.md: a person confirmed it, and the librarian asked a question
    # since, which set status: draft. The rung stays; the label says what waits.
    write(
        kk / "x" / "reopened.md",
        '---\ntype: Service\ntitle: Reopened\nstatus: draft\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\nverified:\n- by: human:ada\n  at: "2026-01-02T10:00:00Z"\n---\n\n## Open questions\n\n- 2026-01-06, process:ktl-librarian: does the source still say so?\n',
    )
    write(
        kk / "x" / "retired.md",
        '---\ntype: Service\ntitle: Retired\nstatus: deprecated\nverified:\n- by: human:ada\n  at: "2026-01-02T10:00:00Z"\n---\n',
    )
    write(
        kk / "x" / "answered.md",
        "---\ntype: Service\ntitle: 'Ada''s answered concept'\nverified:\n  by: human:ada\n  at: \"2026-02-01T00:00:00Z\"\n---\n\n## Open questions\n\n- 2026-01-15, process:ktl-librarian: which is it?\n",
    )
    write(kk / "x" / "gone.md", "---\ntype: Service\ntitle: Gone\nresource: src/missing.md\nverified: [ ]\n---\n")
    write(kk / "log.md", "# Change Log\n")
    write(
        tmp_path / ".lokf" / "feedback.md",
        lines(
            "# Reader feedback for the librarian",
            "",
            "## 2026-03-03",
            "",
            '- **Miss** - Q: "a reader wrote these waiting words" - docent',
            "- **Disagreement** - another. - docent",
        ),
    )
    write(
        tmp_path / ".lokf" / "questions.md",
        lines(
            "# Questions readers asked",
            "",
            "Written by knowledge-apply.sh.",
            "",
            "- 2026-01-10 Miss x/confirmed.md: `Where are widgets?`",
            "- 2026-01-11 Miss x/confirmed.md: `a reader wrote these ledger words`",
            "- 2026-01-12 Disagreement x/draft.md",
            "- 2026-01-13 Miss x/deleted-since.md: `Where did the old concept go?`",
        ),
    )
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "sources and concepts in one commit")
    return tmp_path


def test_a_source_changed_in_the_recording_commit_has_not_moved_and_a_missing_one_is_named(kr):
    out = report(kr, "worklist").out
    assert (
        matches(out, r"^Sources that moved since the concept was derived or last checked: 1$")
        and "- x/gone.md: src/missing.md (gone)" in out
    ), f"report script misread a single-commit history: {out}"


@pytest.fixture
def moved(kr):
    """One source moved in a later commit, and another carries an uncommitted edit."""
    append(kr / "src" / "a.md", "a2\n")
    Git(kr)("commit", "-q", "-am", "a source moves on")
    append(kr / "src" / "b.md", "b2\n")
    return kr


HEALTH = "Confirmed by a person: 3 of 8 · Checked by automation only: 1 · Nobody has checked: 2 · Drafts: 1 · Reopened: 1 · Past review date: 1 · Edited since confirmed: 1 · Retired: 1"


def test_the_health_line_counts_each_label_an_edited_concept_under_its_own_and_a_retired_one_once(moved):
    out = report(moved, "health").out
    assert out == HEALTH, f"report script printed the wrong health line: {out}"


LABELS = [
    "- Confirmed (x/confirmed.md) - confirmed by a person, 2026-01-02, against 3f9c2a1, past its review date (2020-01-01)",
    "- Edited (x/edited.md) - edited since a person last confirmed it (confirmed 2026-01-02T10:00:00Z, edited 2026-01-02T14:00:00Z)",
    "- Auto (x/auto.md) - checked by automation only",
    "- Draft one (x/draft.md) - nobody has checked this yet, still a draft",
    "- Reopened (x/reopened.md) - confirmed by a person, 2026-01-02, reopened 2026-01-06 by the librarian: 1 question waits",
    "- Retired (x/retired.md) - retired",
    "- Ada's answered concept (x/answered.md) - confirmed by a person, 2026-02-01",
    "- x/none.md - no such concept in this bundle",
]


@pytest.mark.parametrize("want", LABELS)
def test_labels(moved, want):
    out = report(
        moved,
        "labels",
        "x/confirmed.md",
        "x/edited.md",
        "x/auto.md",
        "x/draft.md",
        "x/reopened.md",
        "x/retired.md",
        "x/answered.md",
        "x/none.md",
    ).out
    assert has_line(out, want), f"report script did not print '{want}': {out}"


WORKLIST = [
    "- x/confirmed.md: src/a.md (",
    "- x/auto.md: src/b.md (edited, not yet committed)",
    "- x/gone.md: src/missing.md (gone)",
    "Notes a person left that still wait: 1",
    "- x/draft.md (2026-01-05, human:ada)",
    "Open questions older than a person's later confirmation: 1",
    "- x/answered.md (2026-01-15, process:ktl-librarian; a person confirmed the concept 2026-02-01)",
    "Reader feedback waiting: 2",
    "- x/confirmed.md (2 times)",
]


@pytest.mark.parametrize("want", WORKLIST)
def test_the_work_list(moved, want):
    out = report(moved, "worklist").out
    assert want in out, f"report script's work list lacks '{want}': {out}"


def test_the_work_list_leaves_out_an_unmoved_source_a_url_and_a_fenced_example(moved):
    out = report(moved, "worklist").out
    assert not re.search(r"src/c\.md|never-fetched|example in a fence", out), (
        f"report script's work list names an unmoved source, a URL or a fenced example: {out}"
    )


def test_the_work_list_is_paths_and_dates_with_nobodys_words_in_it(moved):
    out = report(moved, "worklist").out
    assert not re.search(r"waiting words|ledger words|these words for the curator", out), (
        f"report script's work list carries a reader's or a person's words: {out}"
    )


def test_the_whole_report_names_a_moved_source_shows_a_persons_note_and_no_readers_words(moved):
    result = report(moved)
    assert (
        result
        and "Confirmed by a person, and a source moved after that confirmation: 1" in result.out
        and "- x/confirmed.md: src/a.md (" in result.out
        and "send it back, with these words for the curator" in result.out
        and not re.search(r"waiting words|ledger words", result.out)
    ), f"report script's whole report is not as expected: {result.out}"


def test_an_edited_since_concept_whose_source_moved_is_on_the_work_list_and_not_under_a_standing_confirmation(tmp_path):
    """The edit already overtook the person's confirmation, so it is counted once."""
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(tmp_path / "src" / "a.md", "a\n")
    write(
        kk / "x" / "edm.md",
        '---\ntype: Service\ntitle: Edm\nresource: src/a.md\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-03-01T00:00:00Z"\nverified:\n  - by: human:ada\n    at: "2026-01-02T10:00:00Z"\n---\n',
    )
    write(kk / "log.md", "# Change Log\n")
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "an edited-since concept and its source")
    append(tmp_path / "src" / "a.md", "a2\n")
    git("commit", "-q", "-am", "the source moves")
    whole = report(tmp_path)
    worklist = report(tmp_path, "worklist")
    assert (
        whole
        and has_line(whole.out, "Confirmed by a person, and a source moved after that confirmation: none")
        and worklist
        and "- x/edm.md: src/a.md (" in worklist.out
    ), (
        f"report script listed an edited-since concept under 'a source moved after that confirmation', or dropped it from the work list: {whole.out}"
    )


def test_changes_counts_the_working_tree_against_head_and_names_the_confirmed_concept_it_touches(moved):
    kk = moved / ".lokf" / "knowledge"
    append(kk / "x" / "confirmed.md", "\nmore\n")
    write(kk / "x" / "new.md", "---\ntype: Service\ntitle: New\n---\n")
    result = report(moved, "changes")
    assert (
        result
        and has_line(result.out, "Concepts added: 1 · changed: 1 · removed: 0")
        and has_line(result.out, "Confirmed by a person, and changed or removed here: 1")
        and has_line(result.out, "- x/confirmed.md: still reads as confirmed")
    ), f"report script's changes is not as expected: {result.out}"


@pytest.fixture
def changed(moved):
    """An edit the pen stamped, a deletion, and a confirmation struck out by hand."""
    kk = moved / ".lokf" / "knowledge"
    append(kk / "x" / "confirmed.md", "\nmore\n")
    write(kk / "x" / "new.md", "---\ntype: Service\ntitle: New\n---\n")
    replace_in(kk / "x" / "confirmed.md", 'at: "2026-01-01T00:00:00Z"', 'at: "2026-03-01T00:00:00Z"')
    (kk / "x" / "retired.md").unlink()
    write(kk / "x" / "answered.md", "---\ntype: Service\ntitle: 'Ada''s answered concept'\n---\n")
    return moved


@pytest.mark.parametrize(
    "want",
    [
        "Concepts added: 1 · changed: 2 · removed: 1",
        "Confirmed by a person, and changed or removed here: 3",
        "- x/confirmed.md: reads as edited since that confirmation",
        "- x/retired.md: removed",
        "- x/answered.md: its confirmation is gone",
    ],
)
def test_changes_says_what_a_change_does_to_each_confirmed_concepts_label(changed, want):
    out = report(changed, "changes").out
    assert has_line(out, want), f"report script's changes lacks '{want}': {out}"


def test_changes_reads_a_sidecar_in_a_subfolder_from_the_top(tmp_path):
    """git names each changed path from the top of the work tree; the concept is named bundle-relative, and the feedback delta reads HEAD from the subfolder."""
    pkg = tmp_path / "pkg"
    write(pkg / ".lokf" / "knowledge" / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(
        pkg / ".lokf" / "knowledge" / "x" / "sub.md",
        '---\ntype: Service\ntitle: Sub\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\nverified:\n  - by: human:ada\n    at: "2026-01-02T10:00:00Z"\n---\n',
    )
    write(
        pkg / ".lokf" / "feedback.md",
        lines("# Reader feedback for the librarian", "", "## 2026-03-03", "", '- **Miss** - Q: "one" - docent'),
    )
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "a sidecar in a subfolder")
    replace_in(pkg / ".lokf" / "knowledge" / "x" / "sub.md", 'at: "2026-01-01T00:00:00Z"', 'at: "2026-03-01T00:00:00Z"')
    append(pkg / ".lokf" / "feedback.md", "- **Disagreement** - two - docent\n")
    result = report(pkg, "changes")
    assert (
        result
        and has_line(result.out, "- x/sub.md: reads as edited since that confirmation")
        and "Reader feedback waiting: 2 (was 1)" in result.out
    ), f"report script's changes misread a sidecar in a subfolder: {result.out}"


@pytest.fixture
def reliance(tmp_path):
    """One concept that depends on another, under an index.md whose base_iri must be read."""
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "x" / "a.md", "---\ntype: Service\ntitle: A\ndependsOn:\n- x/hub.md\n---\n")
    write(kk / "x" / "hub.md", "---\ntype: Service\ntitle: Hub\n---\n")
    return tmp_path


def test_base_iri_is_read_from_a_crlf_index(reliance):
    write(
        reliance / ".lokf" / "knowledge" / "index.md",
        "---\r\nbase_iri: https://acme.example/knowledge/\r\n---\r\n\r\n# Acme\r\n",
    )
    result = report(reliance)
    assert result and "- x/hub.md (1)" in result.out, f"report script lost base_iri on a CRLF index.md: {result.out}"


def test_base_iri_is_read_from_a_byte_order_marked_index(reliance):
    write(
        reliance / ".lokf" / "knowledge" / "index.md",
        BOM + b"---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n",
    )
    result = report(reliance)
    assert result and "- x/hub.md (1)" in result.out, (
        f"report script lost base_iri on a byte-order-marked index.md: {result.out}"
    )


def test_the_retrieval_prompt_holds_the_index_and_the_ledgers_questions_and_asks_none_whose_concept_is_gone(moved):
    result = report(moved, "retrieval", "--prompt")
    assert (
        result
        and has_line(result.out, "x/confirmed.md | Confirmed | a confirmed concept about widgets.")
        and has_line(result.out, "Q1: Where are widgets?")
        and has_line(result.out, "Q2: a reader wrote these ledger words")
        and not re.search(r"Q3|Where did the old concept go", result.out)
    ), f"report script's retrieval prompt is not as expected: {result.out}"


def test_a_reply_is_scored_on_its_first_three_paths_and_a_gone_concept_is_left_out_and_counted(moved):
    write(
        moved / "reply.txt",
        lines(
            "Here are my picks.",
            "**Q1:** x/draft.md, x/confirmed.md",
            "Q2: x/draft.md, x/gone.md, x/auto.md, x/confirmed.md",
        ),
    )
    result = report(moved, "retrieval", moved / "reply.txt")
    assert (
        result
        and has_line(result.out, "Retrieval from the index: 1 of 2 reader questions reach their concept")
        and has_line(result.out, "- question 2 did not reach x/confirmed.md")
        and has_line(result.out, "- 1 more left out: the ledger names no concept for them that the bundle still holds")
    ), f"report script scored a reply wrongly: {result.out}"


def test_a_reply_cannot_add_questions_of_its_own_to_the_score(moved):
    """What is expected of a reply comes from the ledger alone."""
    write(
        moved / "reply.txt",
        "Q1: x/none.md\nQ2: x/none.md\nE\tx/draft.md\tq\nE\tx/draft.md\tq\nQ3: x/draft.md\nQ4: x/draft.md\n",
    )
    result = report(moved, "retrieval", moved / "reply.txt")
    assert result and has_line(result.out, "Retrieval from the index: 0 of 2 reader questions reach their concept"), (
        f"report script let a reply add to what it is scored against: {result.out}"
    )


def test_with_no_question_on_file_there_is_no_prompt(moved):
    (moved / ".lokf" / "questions.md").unlink()
    result = report(moved, "retrieval", "--prompt")
    assert result and result.out == "", f"report script built a retrieval prompt with no question on file: {result.out}"


def test_without_git_the_work_list_says_the_sources_were_not_compared(moved, tmp_path):
    nogit = tmp_path / "nogit"
    shutil.copytree(moved / ".lokf", nogit / ".lokf", symlinks=True)
    result = report(nogit, "worklist")
    assert (
        result
        and matches(result.out, r"^Sources: not compared here")
        and matches(result.out, r"^Notes a person left that still wait: 1$")
    ), f"report script misbehaves outside git: {result.out}"


def test_with_no_bundle_it_says_so_and_exits_non_zero(tmp_path):
    result = report(tmp_path, "health")
    assert not result, f"report script did not stop with no bundle: {result.out}"
    assert matches(result.out, r"^no bundle at "), f"report script failed some other way with no bundle: {result.out}"


NOTE = "\n## Open questions\n\n- 2026-01-03, human:ada: is this still right?\n"
ASKED = "\n- 2026-01-06, process:ktl-librarian: the source src/a.md is gone; retire this concept?\n"


def test_quiet_and_the_work_a_person_declined(tmp_path, checks):
    """A scheduled run has work when a source moved after its concept's stamp, a person left a note after the librarian last looked, a concept carries no stamp, or reader feedback waits, and none otherwise.

    A note the librarian has stamped the concept after still waits for the
    curator, but no longer makes work for the librarian. A source that is gone
    makes work until the librarian's own question, naming it, is committed
    after it went. The librarian workflow hands a scheduled run the pull
    requests a person closed without merging, and nothing such a pull request
    had before it makes work again until it changes.
    """
    kq = tmp_path
    kk = kq / ".lokf" / "knowledge"
    git = Git(kq)
    git.init()
    write(kq / "src" / "a.md", "a\n")
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")

    def one(verified_at, after):
        verified = "" if not verified_at else f'verified:\n  - by: process:ktl-librarian\n    at: "{verified_at}"\n'
        write(
            kk / "x" / "one.md",
            f'---\ntype: Service\ntitle: One\nresource: src/a.md\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n{verified}---\n\n# Overview\n{after}',
        )

    def quiet(status, text, what, declined=None):
        env = {"KNOWLEDGE_DECLINED": str(declined)} if declined else None
        result = report(kq, "quiet", env=env)
        kind = "report script declined" if declined else "report script quiet"
        checks.ok(result.rc == status and text in result.out, f"{kind}: {what}", f"exit {result.rc}: {result.out}")

    one("", "")
    git("add", "-A")
    git("commit", "-q", "-m", "a stamped concept and its source")
    quiet(
        0,
        "Quiet: no source moved",
        "a stamped concept whose source has not moved, with nothing else waiting, makes no work",
    )
    append(kq / "src" / "a.md", "a2\n")
    git("commit", "-q", "-am", "the source moves on")
    quiet(1, "concepts whose source moved: 1 ·", "a source that moved after the stamp makes work")
    one("2026-01-02T00:00:00Z", "")
    git("commit", "-q", "-am", "the librarian rechecks it")
    quiet(0, "Quiet:", "a recheck recorded after the move makes the run quiet again")
    one("2026-01-02T00:00:00Z", NOTE)
    git("commit", "-q", "-am", "a person leaves a note")
    quiet(
        1,
        "notes a person left since the librarian last looked: 1 ·",
        "a note a person left after the librarian's stamp makes work",
    )
    one("2026-01-04T00:00:00Z", NOTE)
    git("commit", "-q", "-am", "the librarian reads it and rechecks")
    quiet(0, "Quiet:", "a note the librarian stamped the concept after waits for the curator alone")
    append(kk / "x" / "one.md", "\n- 2026-01-05, human:ada: and another thing\n")
    quiet(
        1,
        "notes a person left since the librarian last looked: 1 ·",
        "a note not yet committed is newer than any stamp",
    )
    git("checkout", "-q", "--", ".")
    write(kk / "x" / "two.md", "---\ntype: Service\ntitle: Two\n---\n")
    quiet(1, "concepts with no stamp: 1 ·", "a concept with no stamp at all makes work, as the sidecar's skeleton does")
    (kk / "x" / "two.md").unlink()
    write(
        kq / ".lokf" / "feedback.md",
        lines("# Reader feedback for the librarian", "", "## 2026-01-06", "", "- **Miss** - a reader asked. - docent"),
    )
    quiet(1, "reader feedback: 1", "reader feedback waiting makes work")
    (kq / ".lokf" / "feedback.md").unlink()
    git("rm", "-q", "src/a.md")
    git("commit", "-q", "-m", "the source is deleted")
    quiet(1, "concepts whose source moved: 1 ·", "a source that is gone makes work")
    one(
        "2026-01-04T00:00:00Z",
        NOTE
        + "\n- 2026-01-06, process:ktl-librarian: has a person tried this in a real vault, as lib/src/a.md and src/a.md.bak suggest?\n",
    )
    quiet(
        1,
        "concepts whose source moved: 1 ·",
        "a question of the librarian's that does not name the source, only longer paths that hold it, leaves the work",
    )
    one("2026-01-04T00:00:00Z", NOTE + ASKED)
    quiet(
        0,
        "Already with a person: concepts whose moved source the librarian's own question covers: 1",
        "the librarian's own question naming a source that is gone, not yet committed, ends the work",
    )
    git("commit", "-q", "-am", "the librarian asks whether to retire it")
    quiet(
        0,
        "Quiet: nothing new waits for the librarian.",
        "that question, once committed after the source went, keeps the run quiet",
    )
    out = report(kq, "worklist").out
    checks.ok(
        has_line(out, "Sources that moved since the concept was derived or last checked: none")
        and has_line(out, "Sources that moved, where your own question has waited for a person since: 1")
        and has_line(out, "- x/one.md: src/a.md (gone)"),
        "report script's work list does not set a source its own question covers apart",
        out,
    )
    write(kq / "src" / "a.md", "back\n")
    git("add", "-A")
    git("commit", "-q", "-m", "the source comes back, changed")
    quiet(
        1, "concepts whose source moved: 1 ·", "a source that changes after the librarian's question makes work again"
    )
    one("2026-01-07T00:00:00Z", NOTE + ASKED)
    git("commit", "-q", "-am", "the librarian rechecks it")
    quiet(0, "Quiet: no source moved", "a recheck after that change makes the run quiet, with nothing set aside")
    # A source git never held has no commit to order against the question, so
    # any question of the librarian's on the concept covers it.
    write(
        kk / "x" / "never.md",
        '---\ntype: Service\ntitle: Never\nresource: src/never.md\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n---\n\n# Overview\n',
    )
    git("add", "-A")
    git("commit", "-q", "-m", "a concept whose source never existed")
    quiet(1, "concepts whose source moved: 1 ·", "a source that never existed makes work")
    append(kk / "x" / "never.md", "\n## Open questions\n\n- 2026-01-08, human:ada: where is this file?\n")
    git("commit", "-q", "-am", "a person asks, which is no question of the librarian")
    quiet(1, "concepts whose source moved: 1 ·", "a person's note covers no source for the librarian")
    append(
        kk / "x" / "never.md",
        "- 2026-01-09, process:ktl-librarian: no file was ever at src/never.md; which source is meant?\n",
    )
    git("commit", "-q", "-am", "the librarian asks")
    quiet(
        1,
        "concepts whose source moved: 0 · notes a person left since the librarian last looked: 1 ·",
        "the librarian's question covers a source git never held, and the person's note still waits for a stamp",
    )
    git("rm", "-q", ".lokf/knowledge/x/never.md")
    git("commit", "-q", "-m", "that concept goes")

    # What a person declined.
    write(kq / "src" / "b.md", "b\n")
    write(
        kk / "x" / "two.md",
        '---\ntype: Service\ntitle: Two\nresource: src/b.md\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n---\n\n# Overview\n',
    )
    git("add", "-A")
    git("commit", "-q", "-m", "a second stamped concept and its source")
    append(kq / "src" / "a.md", "a3\n")
    append(kq / "src" / "b.md", "b2\n")
    one("2026-01-07T00:00:00Z", NOTE + ASKED + "- 2026-01-20, human:ada: and is the limit still ten?\n")
    write(kk / "x" / "three.md", "---\ntype: Service\ntitle: Three\n---\n\n# Overview\n")
    first = '- **Miss** - Q: "a reader wrote these declined words" - docent'
    second = '- **Miss** - Q: "another reader asked" - docent'
    write(
        kq / ".lokf" / "feedback.md",
        lines("# Reader feedback for the librarian", "", "## 2026-01-21", "", first, second),
    )
    git("add", "-A")
    git("commit", "-q", "-m", "both sources move, a person leaves a note, readers ask, and a concept arrives unstamped")
    base = git("rev-parse", "HEAD")
    declined = kq / "declined.txt"

    def blob(entry):
        return run(["git", "hash-object", "--stdin"], stdin=entry + "\n").out

    quiet(
        1,
        "concepts whose source moved: 2 · notes a person left since the librarian last looked: 1 · concepts with no stamp: 1 · reader feedback: 2",
        "with no record, everything waiting makes work",
    )
    write(
        declined,
        lines(
            f"declined 12 2026-02-01 {base}",
            "touched x/one.md",
            "touched x/three.md",
            "added x/new.md",
            "added x/two.md",
            f"handled {blob(first)}",
            "touched ../../etc/passwd.md",
            "touched x/Two.md",
            "a line in no shape",
        ),
    )
    quiet(
        1,
        "concepts whose source moved: 1 · notes a person left since the librarian last looked: 0 · concepts with no stamp: 0 · reader feedback: 1 ·",
        "what a closed pull request had before it makes no work, and the rest still does",
        declined,
    )
    quiet(
        1,
        "left from a pull request a person closed without merging: 4",
        "the line of counts says how much was left",
        declined,
    )
    out = report(kq, "worklist", env={"KNOWLEDGE_DECLINED": str(declined)}).out
    for want in [
        "Sources that moved since the concept was derived or last checked: 1",
        "Declined, since a person closed the pull request without merging; propose none of it again: 5",
        "- x/one.md: a person's note of 2026-01-20; pull request #12, closed 2026-02-01",
        "- x/three.md: no stamp yet; pull request #12, closed 2026-02-01",
        "- x/new.md: a concept that pull request added; pull request #12, closed 2026-02-01",
        "- .lokf/feedback.md: the entry at line 5, which that pull request handled; pull request #12, closed 2026-02-01",
    ]:
        checks.ok(has_line(out, want), f"report script's work list with a declined record lacks '{want}'", out)
    checks.ok(
        matches(out, r"^- x/two\.md: src/b\.md \(")
        and matches(out, r"^- x/one\.md: src/a\.md \(.*\); pull request #12, closed 2026-02-01$")
        and not re.search(r"x/two\.md: a concept that pull request added|passwd|Two\.md|declined words", out),
        "report script declined: a source nobody declined still waits, a declined one is named with its pull request, and no reader's words or bad path is printed",
        out,
    )
    # The record is read on a scheduled run only, and one this clone cannot
    # order, since its base commit is no ancestor of HEAD, counts for nothing.
    write(
        declined,
        lines(
            "declined 13 2026-02-08 0123456789abcdef0123456789abcdef01234567", "touched x/one.md", "touched x/two.md"
        ),
    )
    quiet(
        1,
        "concepts whose source moved: 2 · notes a person left since the librarian last looked: 1 · concepts with no stamp: 1 · reader feedback: 2",
        "a record whose base commit this clone does not hold is left out",
        declined,
    )
    write(
        declined,
        lines(
            f"declined 12 2026-02-01 {base}",
            "touched x/one.md",
            "touched x/two.md",
            "touched x/three.md",
            f"handled {blob(first)}",
            f"handled {blob(second)}",
        ),
    )
    quiet(
        0,
        "Quiet: nothing new waits for the librarian. Already with a person: left from a pull request a person closed without merging: 6",
        "a week whose every item a person declined is quiet, and says what it left",
        declined,
    )
    # Each kind makes work again once it changes after that pull request.
    append(kq / "src" / "a.md", "a4\n")
    git("commit", "-q", "-am", "a source moves after the closed pull request")
    quiet(
        1,
        "concepts whose source moved: 1 ·",
        "a source that moves after the closed pull request makes work again",
        declined,
    )
    append(kk / "x" / "two.md", "\n## Open questions\n\n- 2026-02-10, human:ada: one more thing\n")
    replace_in(
        kq / ".lokf" / "feedback.md",
        "## 2026-01-21\n",
        '## 2026-02-10\n\n- **Miss** - Q: "a reader asks again" - docent\n\n## 2026-01-21\n',
    )
    append(kk / "x" / "three.md", "more\n")
    git("commit", "-q", "-am", "a new note, a new reader entry and an edit to the unstamped concept")
    quiet(
        1,
        "concepts whose source moved: 1 · notes a person left since the librarian last looked: 1 · concepts with no stamp: 1 · reader feedback: 1 ·",
        "a note, a reader's entry and an edit made after the closed pull request each make work again",
        declined,
    )
    whole = report(kq, env={"KNOWLEDGE_DECLINED": str(declined)})
    checks.ok(
        whole and not re.search(r"Declined|pull request #", whole.out),
        "report script's whole report changed with a declined record",
        whole.out,
    )
    git("rm", "-q", "-r", ".lokf/knowledge/x/two.md", ".lokf/knowledge/x/three.md", ".lokf/feedback.md")
    git("commit", "-q", "-m", "the fixture is put back to one concept")
    nogit = tmp_path / "nogit"
    shutil.copytree(kq / ".lokf", nogit / ".lokf", symlinks=True)
    result = report(nogit, "quiet")
    checks.ok(
        not result and matches(result.out, r"^Work may wait: git holds no full history"),
        "report script quiet: a bundle git holds no history of must never read as quiet",
        result.out,
    )


def test_a_concept_behind_a_byte_order_mark_is_read_not_dropped(tmp_path):
    write(tmp_path / ".lokf" / "knowledge" / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n")
    write(
        tmp_path / ".lokf" / "knowledge" / "x" / "bommed.md",
        BOM + b'---\ntype: Service\ntitle: Bommed\nverified:\n  - by: human:ada\n    at: "2026-01-02T10:00:00Z"\n---\n',
    )
    result = report(tmp_path, "labels", "x/bommed.md")
    assert result and "confirmed by a person" in result.out, (
        f"report script dropped a BOM-prefixed concept: {result.out}"
    )


@pytest.mark.parametrize(
    ("value", "past"),
    [
        ("{today}T23:59:59Z", True),
        ("{today}T10:00:00", True),
        ("{tomorrow}T00:00:00Z", False),
    ],
)
def test_a_datetime_review_date_is_read_as_its_day(tmp_path, value, past):
    """LOKF 0.9.0 types stale_after as a datetime, and a concept is stale from that instant on, so its day is what today is compared with, as the website compares it."""
    now = datetime.now(timezone.utc)
    value = value.format(today=now.strftime("%Y-%m-%d"), tomorrow=(now + timedelta(days=1)).strftime("%Y-%m-%d"))
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n")
    write(kk / "x" / "dated.md", f'---\ntype: Service\ntitle: Dated\nstale_after: "{value}"\n---\n')
    labels = report(tmp_path, "labels", "x/dated.md").out
    health = report(tmp_path, "health").out
    assert ("past its review date" in labels) == past and (" Past review date: 1 " in health) == past, (
        f"report script read the review date {value} wrongly: {labels}; {health}"
    )


def test_byte_order_mark_handling_runs_byte_oriented_for_any_awk():
    """A UTF-8 gawk reads sprintf("%c", 239) as a two-byte character and leaves the mark, so the script runs under LC_ALL=C."""
    assert has_line(read(REPORT), "export LC_ALL=C"), (
        "report script no longer exports LC_ALL=C, so its byte order mark strip breaks on a UTF-8 gawk"
    )


@pytest.fixture
def queue(tmp_path):
    """The curator's queue: reliance in every spelling, a review date due soon, a derived concept, retired ones whose successor a person confirmed, no person has, the bundle lacks, or that have none, and a disputed one."""
    kzk = tmp_path / ".lokf" / "knowledge"
    now = datetime.now(timezone.utc)
    soon = (now + timedelta(days=10)).strftime("%Y-%m-%d")
    later = (now + timedelta(days=40)).strftime("%Y-%m-%d")
    write(tmp_path / "src" / "c.md", "c\n")
    write(kzk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    # Old: the newest line names Hub, an earlier one named A; the newest wins.
    # Lost: its successor Missing is not in the bundle. Gone: the newest line
    # names no successor though an earlier one did. Prior: its successor
    # Origin is in the bundle, and no person has confirmed it.
    write(
        kzk / "log.md",
        "# Change Log\n\n## 2026-02-01\n\n* **Deprecation**: [Old](../x/old.md) retired - replaced by [Hub](../x/hub.md).\n* **Deprecation**: [Lost](../x/lost.md) retired - replaced by [Missing](../x/missing.md).\n* **Deprecation**: [Gone](../x/gone.md) retired, with no replacement.\n* **Deprecation**: [Prior](../x/prior.md) retired - replaced by [Origin](../x/origin.md).\n\n## 2026-01-01\n\n* **Deprecation**: [Old](../x/old.md) retired - replaced by [A](../x/a.md).\n* **Deprecation**: [Gone](../x/gone.md) retired - replaced by [A](../x/a.md).\n",
    )
    write(
        tmp_path / ".lokf" / "feedback.md",
        lines(
            "# Reader feedback for the librarian",
            "",
            "## 2026-03-04",
            "",
            "- **Disagreement** (on `x/hub.md`) - newer - docent",
            "",
            "## 2026-03-01",
            "",
            "- **Disagreement** (on `x/hub.md`) - older - docent",
            "- **Disagreement** - a reader wrote (on `x/a.md`) - docent",
            "- **Disagreement** (on `x/nowhere.md`) - gone - docent",
            "- **Miss** (on `x/e.md`) - a miss - docent",
        ),
    )

    def zc(name, kind, frontmatter, body=""):
        write(kzk / "x" / f"{name}.md", f"---\ntype: {kind}\n{frontmatter}---\n{body}")

    zc(
        "hub",
        "Service",
        f'id: https://acme.example/knowledge/x/hub\ntitle: Hub\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\nverified:\n- by: human:ada\n  at: "2026-01-02T10:00:00Z"\nstale_after: {soon}\n',
    )
    zc(
        "a",
        "Service",
        "id: https://acme.example/knowledge/x/a\ntitle: A\ndependsOn:\n- https://acme.example/knowledge/x/hub\nreferences: [https://acme.example/knowledge/x/hub#part]\n",
    )
    zc(
        "b",
        "Playbook",
        "id: https://acme.example/knowledge/x/b\ntitle: B\nstatus: draft\nabout: x/hub.md\n",
        "\n## Open questions\n\n- 2026-01-05, process:ktl-librarian: which hub?\n",
    )
    zc(
        "c",
        "Explanation",
        'id: https://acme.example/knowledge/x/c\ntitle: C\nresource: src/c.md\nrelations:\n- predicate: derivedFrom\n  target: https://acme.example/knowledge/x/origin\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\nverified:\n- by: human:ada\n  at: "2026-01-03T00:00:00Z"\n',
    )
    zc(
        "origin",
        "Reference",
        'id: https://acme.example/knowledge/x/origin\ntitle: Origin\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-05T00:00:00Z"\nverified:\n- by: process:ktl-librarian\n  at: "2026-01-05T00:00:00Z"\n',
    )
    zc(
        "d",
        "Service",
        'id: https://acme.example/knowledge/x/d\ntitle: D\nrelations:\n- {predicate: dependsOn, target: hub.md}\nverified: [{ by: process:ktl-librarian, at: "2026-01-04T00:00:00Z" }]\n',
    )
    zc(
        "self",
        "Service",
        f'id: https://acme.example/knowledge/x/self\ntitle: Self\nreferences:\n- https://acme.example/knowledge/x/self\nstale_after: {later}\nverified:\n- by: process:ktl-librarian\n  at: "2026-01-04T00:00:00Z"\n',
    )
    zc(
        "old",
        "Service",
        "id: https://acme.example/knowledge/x/old\ntitle: Old\nstatus: deprecated\ndependsOn:\n- https://acme.example/knowledge/x/hub\n",
    )
    zc("lost", "Service", "id: https://acme.example/knowledge/x/lost\ntitle: Lost\nstatus: deprecated\n")
    zc("gone", "Service", "id: https://acme.example/knowledge/x/gone\ntitle: Gone\nstatus: deprecated\n")
    zc("prior", "Service", "id: https://acme.example/knowledge/x/prior\ntitle: Prior\nstatus: deprecated\n")
    zc("no-id", "Service", "title: No id\n")
    zc(
        "e",
        "Service",
        "id: https://acme.example/knowledge/x/e\ntitle: E\ndependsOn: https://acme.example/knowledge/x/no-id\n",
    )
    zc(
        "r",
        "Policy",
        'id: https://acme.example/knowledge/x/r\ntitle: R\nstatus: draft\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\nverified:\n- by: human:ada\n  at: "2026-01-02T10:00:00Z"\n',
        "\n## Open questions\n\n- 2026-01-06, process:ktl-librarian: still so?\n",
    )
    zc(
        "stale",
        "Policy",
        'id: https://acme.example/knowledge/x/stale\ntitle: Stale\nresource: src/c.md\nverified:\n- by: human:ada\n  at: "2026-01-02T10:00:00Z"\nstale_after: 2020-01-01\n',
    )
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "the queue fixture")
    return tmp_path, soon, later


QUEUE = [
    "Worth ten minutes today: 5 of 9 waiting",
    "1. Stale (Policy) - past its review date (2020-01-01) - src/c.md",
    "2. R (Policy) - reopened 2026-01-06 by the librarian: 1 question waits - no source recorded",
    "3. B (Playbook) - still a draft, with an open question - no source recorded",
    "4. No id (Service) - nobody has checked this yet; 1 other concept relies on this - no source recorded",
    "5. A (Service) - nobody has checked this yet - no source recorded",
    "Due soon, a review date within 30 days: 1",
    "- x/hub.md ({soon})",
    "Confirmed by a person, and derived from a concept edited after that confirmation: 1",
    "- x/c.md: x/origin.md (edited 2026-01-05, confirmed 2026-01-03)",
    "Relied on by other concepts: 3",
    "- x/hub.md (3)",
    "- x/origin.md (1)",
    "- x/no-id.md (1)",
    "Retired, with a successor no person has confirmed: 1",
    "- x/prior.md: x/origin.md - checked by automation only",
    "Disputed by a reader, waiting for the librarian: 1",
    "- x/hub.md (2026-03-04)",
]


@pytest.mark.parametrize("want", QUEUE)
def test_the_curators_queue_and_its_counts(queue, want):
    root, soon, _ = queue
    out = report(root).out
    assert has_line(out, want.format(soon=soon)), (
        f"report script's queue or lists lack '{want.format(soon=soon)}': {out}"
    )


def test_a_concept_never_relies_on_itself_a_retired_one_counts_for_nothing_and_a_date_40_days_off_is_not_due_soon(
    queue,
):
    root, _, later = queue
    out = report(root).out
    assert "- x/self.md (" not in out and "- x/old.md (" not in out and f"- x/self.md ({later})" not in out, (
        f"report script counted a concept for itself, counted a retired one, or called a review date 40 days off due soon: {out}"
    )


def test_a_retirement_waits_only_while_no_person_has_confirmed_a_successor_the_bundle_holds(queue):
    """Old's successor Hub carries a person's event, Lost's is not in the bundle, and Gone names none."""
    root, _, _ = queue
    out = report(root).out
    assert not re.search(r"^- x/(old|lost|gone)\.md: ", out, re.M), (
        f"report script listed a retirement whose successor a person confirmed, the bundle lacks, or that names none: {out}"
    )


def test_a_retirement_log_md_links_no_successor_to_waits_on_none(moved):
    out = report(moved).out
    assert has_line(out, "Retired, with a successor no person has confirmed: none"), (
        f"report script listed a successor for a retirement log.md does not link: {out}"
    )


def test_labels_keep_the_docents_footer_shape(queue):
    root, _, _ = queue
    result = report(root, "labels", "x/c.md")
    assert result and result.out == "- C (x/c.md) - confirmed by a person, 2026-01-03", (
        f"report script's labels changed shape: {result.out}"
    )


@pytest.mark.parametrize(
    "want",
    [
        "- Old (x/old.md) - retired, replaced by x/hub.md",
        "- Lost (x/lost.md) - retired",
        "- Gone (x/gone.md) - retired",
        "- Prior (x/prior.md) - retired, replaced by x/origin.md",
        "- Hub (x/hub.md) - confirmed by a person, 2026-01-02, a reader disputed this on 2026-03-04",
        "- A (x/a.md) - nobody has checked this yet",
        "- E (x/e.md) - nobody has checked this yet",
    ],
)
def test_a_retired_concept_names_its_successor_and_a_disputed_one_its_newest_day(queue, want):
    root, _, _ = queue
    out = report(root, "labels", "x/old.md", "x/lost.md", "x/gone.md", "x/prior.md", "x/hub.md", "x/a.md", "x/e.md").out
    assert has_line(out, want), f"report script did not print '{want}': {out}"


def test_reliance_counts_measures_member_of_and_holder(tmp_path):
    """The schema ranges the three over Concept, as it does the ten generic relation fields, so a Metric relies on what it measures and a Role on its organization and its holder."""
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(kk / "x" / "hub.md", "---\ntype: Dataset\ntitle: Hub\n---\n")
    write(kk / "x" / "m.md", "---\ntype: Metric\ntitle: M\nmeasures:\n- https://acme.example/knowledge/x/hub\n---\n")
    write(kk / "x" / "r.md", "---\ntype: Role\ntitle: R\nmemberOf: [x/hub.md]\nholder:\n- x/hub.md\n---\n")
    result = report(tmp_path)
    assert result and has_line(result.out, "- x/hub.md (2)"), (
        f"report script did not count measures, memberOf and holder as reliance: {result.out}"
    )


# ---- coverage ----------------------------------------------------------------
@pytest.fixture
def cov(tmp_path):
    """A host whose concepts name one file, one folder and a file with a fragment, beside files nothing names and the sidecar's own tree."""
    kk = tmp_path / ".lokf" / "knowledge"
    for p in ("README.md", "docs/kept.md", "docs/orphan.md", "src/lib/a.py", "src/lib/b.py", "data/raw.csv", ".lokf/scripts/x.sh"):
        write(tmp_path / p, p + "\n")
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(kk / "x" / "kept.md", "---\ntype: Service\ntitle: Kept\nresource: docs/kept.md\n---\n")
    # The map names the root, which accounts for nothing, a folder with a
    # trailing slash, a file with a fragment, and a URL.
    write(
        kk / "x" / "map.md",
        "---\ntype: Playbook\ntitle: Sources\nresource: .\nsources:\n- resource: src/lib/\n- resource: README.md#top\n- resource: https://example.invalid/x\n---\n",
    )
    write(kk / "x" / "url.md", "---\ntype: Service\ntitle: Elsewhere\nresource: https://example.invalid/y\n---\n")
    write(kk / "log.md", "# Change Log\n")
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "host and bundle")
    return tmp_path


COUNT = "Tracked files under a path a concept names as its resource or one of its sources: "
SKIPPED = "skipped, since the sidecar's own files are the preflight's to compare with its templates"


def test_coverage_counts_the_tracked_files_no_concept_names_per_folder_and_leaves_the_sidecar_out(cov):
    r = report(cov, "coverage")
    assert r, r.out
    assert has_line(r.out, COUNT + "4 of 6 · under none: 2")
    assert has_line(r.out, "- data/: 1")
    assert has_line(r.out, "- docs/: 1")
    assert "README" not in r.out and ".lokf" not in r.out and "src/" not in r.out


def test_coverage_lists_the_files_under_a_folder_and_rejects_a_path_outside_the_root(cov):
    r = report(cov, "coverage", "docs/", "src")
    assert r, r.out
    assert has_line(r.out, "docs/: 1 under no named path")
    assert has_line(r.out, "- docs/orphan.md")
    assert has_line(r.out, "src/: none under no named path")
    assert "kept" not in r.out
    # Every spelling of one folder reads as that folder, and a file as a file.
    for spelt in ("./docs", "docs//", "docs/.", "./docs/./"):
        assert has_line(report(cov, "coverage", spelt).out, "docs/: 1 under no named path"), spelt
    assert has_line(report(cov, "coverage", "data/raw.csv").out, "data/raw.csv: 1 under no named path")
    assert report(cov, "coverage", "/etc").rc == 2
    assert report(cov, "coverage", "../x").rc == 2


def test_coverage_says_a_mistyped_folder_and_the_sidecar_hold_nothing_it_counts(cov):
    r = report(cov, "coverage", "typo", ".lokf/scripts")
    assert r, r.out
    assert has_line(r.out, "typo/: git tracks no file here")
    assert has_line(r.out, ".lokf/scripts: " + SKIPPED)
    assert "none under no named path" not in r.out


def test_coverage_counts_a_path_git_quotes_apart_and_never_prints_it(cov):
    try:
        write(cov / "docs" / "tab\there.md", "t\n")
    except OSError:
        pytest.skip("this filesystem refuses a tab in a file name")
    git = Git(cov)
    git("add", "-A")
    git("commit", "-q", "-m", "a path git quotes")
    r = report(cov, "coverage")
    assert r, r.out
    assert has_line(r.out, COUNT + "4 of 6 · under none: 2")
    assert has_line(r.out, "- and 1 more, whose paths hold characters this report does not print")
    assert "tab" not in r.out
    # A path it cannot compare is no pass under --strict.
    assert report(cov, "coverage", "--strict", "src").rc == 0
    write(cov / "data" / "raw.csv", "now named\n")
    write(cov / ".lokf" / "knowledge" / "x" / "data.md", "---\ntype: Dataset\ntitle: Data\nresource: data\n---\n")
    write(cov / ".lokf" / "knowledge" / "x" / "docs.md", "---\ntype: Service\ntitle: Docs\nresource: docs\n---\n")
    assert report(cov, "coverage", "--strict").rc == 1


def test_without_git_coverage_says_the_tracked_files_were_not_listed_and_strict_fails(cov, tmp_path):
    plain = tmp_path / "plain"
    shutil.copytree(cov, plain, ignore=shutil.ignore_patterns(".git"))
    # The copy sits in no repository: git must not find one above it either.
    env = {"GIT_CEILING_DIRECTORIES": str(tmp_path)}
    r = report(plain, "coverage", env=env)
    assert r, r.out
    assert r.out == "Coverage: not computed here, since this folder has no git history to list the tracked files"
    assert report(plain, "coverage", "--strict", env=env).rc == 1
    # The same copy inside another repository, which tracks nothing under it.
    inside = cov / "copy"
    shutil.copytree(plain, inside)
    r = report(inside, "coverage")
    assert r, r.out
    assert r.out.startswith("Coverage: not computed here, since git tracks no file under this folder")
    assert report(inside, "coverage", "--strict").rc == 1


def test_coverage_of_the_whole_tree_lists_every_file_nobody_named(cov):
    r = report(cov, "coverage", ".")
    assert r, r.out
    assert has_line(r.out, "the whole tree: 2 under no named path")
    assert has_line(r.out, "- data/raw.csv") and has_line(r.out, "- docs/orphan.md")


def test_coverage_counts_a_file_git_would_add_apart_and_not_one_it_ignores(cov):
    write(cov / "docs" / "new.md", "new\n")
    write(cov / "docs" / "ignored.md", "ignored\n")
    # The ignore file sits inside .git/, where git lists nothing, and does not
    # rely on git init having laid down info/exclude.
    write(cov / ".git" / "test-ignore", "docs/ignored.md\n")
    Git(cov)("config", "core.excludesFile", str(cov / ".git" / "test-ignore"))
    r = report(cov, "coverage")
    assert r, r.out
    assert has_line(r.out, COUNT + "4 of 6 · under none: 2")
    assert has_line(r.out, "Files git would add but does not track yet, so not counted: 1 · under no named path: 1")
    assert has_line(r.out, "Commit each file not tracked yet before a concept names it, or ignore it if it is runtime state, such as an installed skill.")
    r = report(cov, "coverage", "docs")
    assert has_line(r.out, "docs/: 1 under no named path, and 1 more not tracked yet")
    assert has_line(r.out, "- docs/new.md (not tracked yet)")
    assert "ignored" not in r.out
    # A file git would add never fails --strict, which reads what git tracks.
    assert report(cov, "coverage", "--strict", "src").rc == 0


def test_coverage_leaves_out_a_tracked_file_deleted_from_the_working_tree(cov):
    (cov / "docs" / "orphan.md").unlink()
    r = report(cov, "coverage")
    assert r, r.out
    assert has_line(r.out, COUNT + "4 of 5 · under none: 1")
    assert "docs" not in r.out


def test_coverage_why_names_the_concept_behind_a_path_with_or_without_git(cov, tmp_path):
    want = [
        "- docs/kept.md: named by x/kept.md",
        "- src/lib/a.py: under src/lib, which x/map.md names",
        "- docs/orphan.md: under no named path",
        "- .lokf/scripts/x.sh: " + SKIPPED,
        "- docs: under no named path; concepts name 1 path inside it, and coverage docs lists the files they leave out",
        "- docs/typo.md: under no named path (no such file or folder here)",
    ]
    args = ["coverage", "--why", "docs/kept.md", "./src/lib/a.py", "docs/orphan.md", ".lokf/scripts/x.sh", "docs/", "docs/typo.md"]
    r = report(cov, *args)
    assert r, r.out
    for line in want:
        assert has_line(r.out, line), r.out
    plain = tmp_path / "plain"
    shutil.copytree(cov, plain, ignore=shutil.ignore_patterns(".git"))
    r = report(plain, *args, env={"GIT_CEILING_DIRECTORIES": str(tmp_path)})
    assert r and all(has_line(r.out, line) for line in want), r.out
    assert report(cov, "coverage", "--why").rc == 2
    # Every path is checked before anything is printed.
    r = report(cov, "coverage", "--why", "docs/kept.md", "/etc/passwd")
    assert r.rc == 2 and "named by" not in r.out


def test_coverage_strict_exits_1_while_a_file_in_scope_is_named_by_nobody_or_a_folder_holds_none(cov):
    assert report(cov, "coverage", "--strict").rc == 1
    assert report(cov, "coverage", "--strict", "docs").rc == 1
    assert report(cov, "coverage", "--strict", "src").rc == 0
    assert report(cov, "coverage", "--strict", "typo").rc == 1
    assert report(cov, "coverage", "--strict", ".lokf").rc == 1
    assert report(cov, "coverage", "--strict", "--why", "docs").rc == 2
    assert report(cov, "coverage", "docs", "--why", "src").rc == 2
    assert report(cov, "coverage", "--bogus").rc == 2


def test_coverage_counts_a_file_left_out_on_purpose_apart_and_a_concept_naming_it_wins(cov):
    """An exclusion (lokf 0.9.0 and later) accounts for a file without naming it."""
    write(
        cov / ".lokf" / "knowledge" / "x" / "left.md",
        "---\ntype: Playbook\ntitle: Left out\nexclusions:\n- resource: data/raw.csv\n  reason: a generated extract\n  by: human:ada\n"
        "- resource: ./docs/\n  reason: drafts, apart from the page another concept uses\n---\n",
    )
    r = report(cov, "coverage")
    assert r, r.out
    assert has_line(r.out, COUNT + "4 of 6 · left out on purpose: 2 · under none: 0")
    assert "data/" not in r.out and "docs/" not in r.out
    r = report(cov, "coverage", "docs", "data/raw.csv")
    assert has_line(r.out, "docs/: none under no named path, 1 left out on purpose")
    assert has_line(r.out, "data/raw.csv: none under no named path, 1 left out on purpose")
    assert "orphan" not in r.out
    assert report(cov, "coverage", "--strict").rc == 0
    want = [
        "- data/raw.csv: left out on purpose by x/left.md",
        "- docs/orphan.md: under docs, which x/left.md leaves out on purpose",
        "- docs/kept.md: named by x/kept.md",
        "- docs/kept.md: under docs, which x/left.md leaves out on purpose",
    ]
    r = report(cov, "coverage", "--why", "data/raw.csv", "docs/orphan.md", "docs/kept.md")
    assert r and all(has_line(r.out, line) for line in want), r.out
    assert "docs/orphan.md: under no named path" not in r.out


def test_an_exclusion_never_moves_and_never_stands_for_the_concept(kr):
    """A concept's first source is the one the queue shows, never an exclusion listed above it."""
    kk = kr / ".lokf" / "knowledge"
    write(
        kk / "x" / "aside.md",
        '---\ntype: Service\ntitle: Aside\nexclusions:\n- resource: src/c.md\n  reason: a copy of b\nsources:\n- resource: src/b.md\n'
        'generated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n---\n',
    )
    git = Git(kr)
    git("add", "-A")
    git("commit", "-q", "-m", "a concept that leaves c out")
    append(kr / "src" / "c.md", "c2\n")
    git("commit", "-q", "-am", "the excluded file moves")
    out = report(kr, "worklist").out
    assert "- x/confirmed.md: src/c.md (" in out, out
    assert "x/aside.md" not in out, out
    out = report(kr).out
    assert matches(out, r"^\d\. Aside \(Service\) - .* - src/b\.md$"), out


def test_coverage_reads_a_sidecar_in_a_subfolder_from_its_own_root(tmp_path):
    host = tmp_path / "host"
    kk = host / ".lokf" / "knowledge"
    write(host / "docs" / "named.md", "a\n")
    write(host / "docs" / "orphan.md", "b\n")
    write(tmp_path / "elsewhere" / "outside.md", "c\n")
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(kk / "x" / "named.md", "---\ntype: Service\ntitle: Named\nresource: docs/named.md\n---\n")
    write(kk / "log.md", "# Change Log\n")
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "a host in a subfolder")
    r = report(host, "coverage")
    assert r, r.out
    assert has_line(r.out, COUNT + "1 of 2 · under none: 1")
    assert has_line(r.out, "- docs/: 1")
    assert "elsewhere" not in r.out and "outside" not in r.out
