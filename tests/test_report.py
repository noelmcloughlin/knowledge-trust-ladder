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


HEALTH = "Confirmed by a person: 2 of 7 · Checked by automation only: 1 · Nobody has checked: 2 · Drafts: 1 · Past review date: 1 · Edited since confirmed: 1 · Retired: 1"


def test_the_health_line_counts_each_label_an_edited_concept_under_its_own_and_a_retired_one_once(moved):
    out = report(moved, "health").out
    assert out == HEALTH, f"report script printed the wrong health line: {out}"


LABELS = [
    "- Confirmed (x/confirmed.md) - confirmed by a person, 2026-01-02, against 3f9c2a1, past its review date (2020-01-01)",
    "- Edited (x/edited.md) - edited since a person last confirmed it (confirmed 2026-01-02T10:00:00Z, edited 2026-01-02T14:00:00Z)",
    "- Auto (x/auto.md) - checked by automation only",
    "- Draft one (x/draft.md) - nobody has checked this yet, still a draft",
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


def test_byte_order_mark_handling_runs_byte_oriented_for_any_awk():
    """A UTF-8 gawk reads sprintf("%c", 239) as a two-byte character and leaves the mark, so the script runs under LC_ALL=C."""
    assert has_line(read(REPORT), "export LC_ALL=C"), (
        "report script no longer exports LC_ALL=C, so its byte order mark strip breaks on a UTF-8 gawk"
    )


@pytest.fixture
def queue(tmp_path):
    """The curator's queue: reliance in every spelling, a review date due soon, a derived concept, retired ones with and without a successor, and a disputed one."""
    kzk = tmp_path / ".lokf" / "knowledge"
    now = datetime.now(timezone.utc)
    soon = (now + timedelta(days=10)).strftime("%Y-%m-%d")
    later = (now + timedelta(days=40)).strftime("%Y-%m-%d")
    write(tmp_path / "src" / "c.md", "c\n")
    write(kzk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    # Old: the newest line names Hub, an earlier one named A; the newest wins.
    # Lost: its successor Missing is not in the bundle. Gone: the newest line
    # names no successor though an earlier one did.
    write(
        kzk / "log.md",
        "# Change Log\n\n## 2026-02-01\n\n* **Deprecation**: [Old](../x/old.md) retired - replaced by [Hub](../x/hub.md).\n* **Deprecation**: [Lost](../x/lost.md) retired - replaced by [Missing](../x/missing.md).\n* **Deprecation**: [Gone](../x/gone.md) retired, with no replacement.\n\n## 2026-01-01\n\n* **Deprecation**: [Old](../x/old.md) retired - replaced by [A](../x/a.md).\n* **Deprecation**: [Gone](../x/gone.md) retired - replaced by [A](../x/a.md).\n",
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
    zc("no-id", "Service", "title: No id\n")
    zc(
        "e",
        "Service",
        "id: https://acme.example/knowledge/x/e\ntitle: E\ndependsOn: https://acme.example/knowledge/x/no-id\n",
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
    "Worth ten minutes today: 5 of 8 waiting",
    "1. Stale (Policy) - past its review date (2020-01-01) - src/c.md",
    "2. B (Playbook) - still a draft, with an open question - no source recorded",
    "3. No id (Service) - nobody has checked this yet; 1 other concept relies on this - no source recorded",
    "4. A (Service) - nobody has checked this yet - no source recorded",
    "5. E (Service) - nobody has checked this yet - no source recorded",
    "Due soon, a review date within 30 days: 1",
    "- x/hub.md ({soon})",
    "Confirmed by a person, and derived from a concept edited after that confirmation: 1",
    "- x/c.md: x/origin.md (edited 2026-01-05, confirmed 2026-01-03)",
    "Relied on by other concepts: 3",
    "- x/hub.md (3)",
    "- x/origin.md (1)",
    "- x/no-id.md (1)",
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
        "- Hub (x/hub.md) - confirmed by a person, 2026-01-02, a reader disputed this on 2026-03-04",
        "- A (x/a.md) - nobody has checked this yet",
        "- E (x/e.md) - nobody has checked this yet",
    ],
)
def test_a_retired_concept_names_its_successor_and_a_disputed_one_its_newest_day(queue, want):
    root, _, _ = queue
    out = report(root, "labels", "x/old.md", "x/lost.md", "x/gone.md", "x/hub.md", "x/a.md", "x/e.md").out
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
