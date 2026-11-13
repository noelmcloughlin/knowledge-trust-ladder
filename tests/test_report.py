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

A concept's own body counts as a source: one that differs from the body its
stamp's commit held has been checked against nothing since, unless only its
layout, its notes or the plugin's block changed.

`isolated` names what no relation joins to the rest of the bundle. The work
list shows ten of them, taking turns by month with nothing stamped.

A retired concept's label names its successor from the newest **Deprecation**
line in log.md, and only one the bundle holds. A waiting Disagreement that
names its concept right after the kind marks that concept, from its newest
day.

A retired concept whose successor no person has confirmed is listed with that
successor's label, and only when the bundle holds the successor: exclusion
follows affirmation. A review date is read by its day, so a datetime value
counts from the day it names.

`sample` draws the lists the curation policy asks for, so that no model sorts
one: each population in the order of the SHA-256 of the seed, a space and the
path. The seed is stated, the sizes come from the policy or from a flag, and
the whole report prints the same section. Among a person's events the
earliest is the first confirmation, and a later one by another id is a second
person's re-check, which the sample counts.

`evidence` prints every `generated` record and `verified` event as a
tab-separated table, the same bytes on every run.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
from datetime import datetime, timedelta, timezone

import pytest

from conftest import BOM, SCRIPTS, Git, bash, has_line, have, matches, mawk_path, read, replace_in, run, stopping_awk, today_utc, write

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


def test_an_item_whose_dash_stands_alone_is_an_event_of_its_own(tmp_path):
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(
        kk / "x" / "alone.md",
        '---\ntype: Service\ntitle: Alone\nverified:\n  -\n    by: human:ada\n    at: "2026-01-02T10:00:00Z"\n  -\n    by: process:ktl-librarian\n    at: "2026-01-03T00:00:00Z"\n---\n',
    )
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "an event in an item whose dash stands alone")
    out = report(tmp_path, "labels", "x/alone.md").out
    assert "confirmed by a person, 2026-01-02" in out, f"the report lost a person's event: {out}"


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


def test_an_exclusion_is_not_read_as_a_readers_dispute(tmp_path):
    """A concept's `exclusions` entry names a material left out on purpose. Its line once shared a letter with a reader's Disagreement, so the label named the excluded path as the day of a dispute."""
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(kk / "x" / "map.md", "---\ntype: Playbook\ntitle: Map\nexclusions:\n  - resource: docs/old\n    reason: superseded\n---\n")
    write(kk / "x" / "hub.md", "---\ntype: Dataset\ntitle: Hub\n---\n")
    write(tmp_path / ".lokf" / "feedback.md", "# Feedback\n\n## 2026-03-04\n\n- **Disagreement** (on `x/hub.md`) - the hub is gone. - docent\n")
    out = report(tmp_path, "labels").out
    assert has_line(out, "- Map (x/map.md) - nobody has checked this yet"), f"an exclusion read as a dispute: {out}"
    assert has_line(out, "- Hub (x/hub.md) - nobody has checked this yet, a reader disputed this on 2026-03-04"), f"a reader's dispute was lost: {out}"
    whole = report(tmp_path).out
    assert "x/map.md (docs/old)" not in whole and has_line(whole, "- x/hub.md (2026-03-04)"), f"the whole report listed an exclusion as a dispute: {whole}"


def test_a_dispute_filed_on_a_reserved_file_names_no_concept(tmp_path):
    """index.md, log.md and diataxis.md are files of the bundle and no concept, so a Disagreement filed by hand on one is not listed as a dispute."""
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(kk / "diataxis.md", "# Diataxis\n")
    write(kk / "x" / "hub.md", "---\ntype: Dataset\ntitle: Hub\n---\n")
    write(
        tmp_path / ".lokf" / "feedback.md",
        "# Feedback\n\n## 2026-03-04\n\n- **Disagreement** (on `diataxis.md`) - x - docent\n- **Disagreement** (on `index.md`) - x - docent\n",
    )
    whole = report(tmp_path).out
    assert has_line(whole, "Disputed by a reader, waiting for the librarian: none"), f"a reserved file was listed as disputed: {whole}"


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


# ---- a body that changed after its stamp --------------------------------------
STAMP = 'generated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n'


def concept_text(body="# One\n\nThe feature is enabled by default for each run.\n", head="", stamp=STAMP):
    return f"---\ntype: Service\ntitle: One\nresource: src/a.md\n{stamp}{head}---\n\n{body}"


@pytest.fixture
def stamped(tmp_path):
    """A concept and its source, both committed, so nothing waits."""
    kk = tmp_path / ".lokf" / "knowledge"
    write(tmp_path / "src" / "a.md", "a\n")
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(kk / "x" / "one.md", concept_text())
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "the concept and its source")
    return tmp_path


def commit_concept(root, text, message="an edit"):
    write(root / ".lokf" / "knowledge" / "x" / "one.md", text)
    git = Git(root)
    git("add", "-A")
    git("commit", "-q", "-m", message)


def test_a_rewording_that_left_the_stamp_alone_goes_to_the_librarian(stamped):
    """A ktl-prose pass leaves the stamp alone on purpose, so nothing else would ever compare the new text with its source."""
    assert report(stamped, "quiet"), "nothing should wait before the rewording"
    commit_concept(stamped, concept_text(body="# One\n\nThe feature is disabled by default for each run.\n"))
    out = report(stamped, "worklist").out
    assert matches(out, r"^- x/one\.md: its own body \(\d{4}-\d{2}-\d{2}\)$"), out
    quiet = report(stamped, "quiet")
    assert quiet.rc == 1 and "concepts whose source moved: 1" in quiet.out, quiet.out


def test_a_rewording_not_yet_committed_is_named(stamped):
    write(stamped / ".lokf" / "knowledge" / "x" / "one.md", concept_text(body="# One\n\nThe feature is off.\n"))
    assert has_line(report(stamped, "worklist").out, "- x/one.md: its own body (edited, not yet committed)")


@pytest.mark.parametrize(
    "text",
    [
        concept_text(body="# One\n\nThe feature is enabled by default\nfor each   run.\n"),
        concept_text(body="# One\n\nThe feature is enabled by default for each run.\n\n## Open questions\n\n- 2026-02-01, process:ktl-librarian: is this current?\n"),
        concept_text(body="# One\n\nThe feature is enabled by default for each run.\n\n<!-- lokf:related -->\n- [[two]]\n<!-- /lokf:related -->\n"),
        concept_text(head="stale_after: 2027-01-01\n"),
    ],
    ids=["laid out afresh", "a note", "the plugin's block", "frontmatter alone"],
)
def test_what_says_nothing_new_makes_no_work(stamped, text):
    commit_concept(stamped, text)
    assert "its own body" not in report(stamped, "worklist").out
    assert report(stamped, "quiet"), "a change that claims nothing new made work"


def test_a_stamp_after_the_rewording_clears_it(stamped):
    reworded = "# One\n\nThe feature is disabled by default for each run.\n"
    commit_concept(stamped, concept_text(body=reworded))
    checked = 'verified:\n  - by: process:ktl-librarian\n    at: "2026-03-01T00:00:00Z"\n'
    commit_concept(stamped, concept_text(body=reworded, head=checked), "the librarian checks it")
    assert "its own body" not in report(stamped, "worklist").out
    assert report(stamped, "quiet"), "the librarian's check should clear the rewording"


def test_a_rewording_in_the_commit_that_recorded_the_stamp_is_not_seen(stamped):
    """A squash merge leaves the two in one commit, as it does a source. limits.md says so."""
    stamp = STAMP.replace("2026-01-01", "2026-04-01")
    commit_concept(stamped, concept_text(body="# One\n\nThe feature is off.\n", stamp=stamp))
    assert "its own body" not in report(stamped, "worklist").out


def test_a_retired_concept_makes_no_work(stamped):
    commit_concept(stamped, concept_text(body="# One\n\nGone.\n", head="status: deprecated\n"))
    assert "its own body" not in report(stamped, "worklist").out


def test_a_question_the_librarian_asked_since_sets_it_aside(stamped):
    """Where the pen refuses the fix the librarian asks a person, and must not be sent back every week."""
    reworded = "# One\n\nThe feature is off.\n"
    commit_concept(stamped, concept_text(body=reworded))
    asked = reworded + "\n## Open questions\n\n- 2026-03-01, process:ktl-librarian: the text says off and the source says on; which is it?\n"
    commit_concept(stamped, concept_text(body=asked), "the librarian asks")
    out = report(stamped, "worklist").out
    assert matches(out, r"^Sources that moved, where your own question has waited for a person since: 1$"), out
    assert report(stamped, "quiet"), "a question already asked should make no work"


def test_a_person_who_declined_the_check_is_not_asked_again_until_it_changes(stamped):
    commit_concept(stamped, concept_text(body="# One\n\nThe feature is off.\n"))
    git = Git(stamped)
    declined = stamped / "declined.txt"
    write(declined, f"declined 7 2026-03-01 {git('rev-parse', 'HEAD').strip()}\ntouched x/one.md\n")
    env = {"KNOWLEDGE_DECLINED": str(declined)}
    out = report(stamped, "worklist", env=env).out
    assert not matches(out, r"^- x/one\.md: its own body \([^)]*\)$") and "Declined, since a person closed" in out, out
    assert report(stamped, "quiet", env=env), "what a person declined should make no work"
    commit_concept(stamped, concept_text(body="# One\n\nThe feature is on.\n"))
    assert matches(report(stamped, "worklist", env=env).out, r"^- x/one\.md: its own body \(\d")


def test_a_body_changed_after_a_confirmation_is_on_the_curators_list(stamped):
    """Conventions rule 13 refuses this where the gate runs. Where it does not, the curator still hears of it."""
    confirmed = 'verified:\n  - by: human:ann\n    at: "2026-02-01T00:00:00Z"\n'
    commit_concept(stamped, concept_text(head=confirmed), "ann confirms")
    assert "its own body" not in report(stamped).out
    commit_concept(stamped, concept_text(body="# One\n\nThe feature is off.\n", head=confirmed))
    out = report(stamped).out
    assert matches(out, r"^Confirmed by a person, and a source moved after that confirmation: 1$"), out
    assert matches(out, r"^- x/one\.md: its own body \(\d"), out
    assert "confirmed by a person, and a source moved since" in out, out


def test_a_linked_bundle_is_read_as_any_other(tmp_path):
    """The folder may be a link to knowledge_bundle, and git names the file by its real path."""
    kb = tmp_path / "knowledge_bundle"
    write(tmp_path / "src" / "a.md", "a\n")
    write(kb / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(kb / "x" / "one.md", concept_text())
    (tmp_path / ".lokf").mkdir()
    (tmp_path / ".lokf" / "knowledge").symlink_to("../knowledge_bundle")
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "start")
    write(kb / "x" / "one.md", concept_text(body="# One\n\nThe feature is off.\n"))
    git("add", "-A")
    git("commit", "-q", "-m", "reworded")
    assert matches(report(tmp_path, "worklist").out, r"^- x/one\.md: its own body \(\d")


@pytest.mark.parametrize(
    "slot",
    [
        "requires_check:\n  - https://acme.example/knowledge/x/hub\n",
        "emitted_by: https://acme.example/knowledge/x/hub\n",
        "emitted_by: 'https://acme.example/knowledge/x/hub'\n",
        "requires_check: [https://acme.example/knowledge/x/other, https://acme.example/knowledge/x/hub]\n",
        "rules:\n  - name: one\n    target_concept: https://acme.example/knowledge/x/hub\n",
    ],
)
def test_reliance_counts_a_whole_iri_in_a_domain_vocabularys_own_slot(tmp_path, slot):
    """A host's schema adds slots ranged over Concept, which no list in the script can name, and the curator's queue undercounted what relies on their targets."""
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(kk / "x" / "hub.md", "---\ntype: Dataset\ntitle: Hub\n---\n")
    write(kk / "x" / "m.md", f"---\ntype: Service\ntitle: M\n{slot}---\n")
    result = report(tmp_path)
    assert result and has_line(result.out, "- x/hub.md (1)"), f"a domain slot's target was not counted as reliance: {result.out}"


@pytest.mark.parametrize(
    "field",
    [
        "description: https://acme.example/knowledge/x/hub\n",
        "resource: https://acme.example/knowledge/x/hub\n",
        "sources:\n  - resource: https://acme.example/knowledge/x/hub\n",
        "summary: see https://acme.example/knowledge/x/hub for more\n",
        "homepage: https://elsewhere.example/x/hub\n",
        "genre: x/hub\n",
    ],
)
def test_reliance_ignores_an_iri_a_field_holds_for_another_reason(tmp_path, field):
    """A source, a resource, a description or a sentence that holds an address relates nothing, and a plain value is never read as a path."""
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(kk / "x" / "hub.md", "---\ntype: Dataset\ntitle: Hub\n---\n")
    write(kk / "x" / "m.md", f"---\ntype: Service\ntitle: M\n{field}---\n")
    result = report(tmp_path)
    assert result and "- x/hub.md (" not in result.out, f"a field that relates nothing was counted as reliance: {result.out}"


# ---- concepts that stand apart -----------------------------------------------
def isolated_host(tmp_path):
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    return kk


def isolated(root, *args, env=None):
    result = report(root, *(args or ("isolated",)), env=env)
    assert result, f"report failed: {result.out}"
    return result.out


def at_month(tmp_path, day):
    """An environment in which the script's clock reads the given day."""
    shim = tmp_path / "clock"
    write(shim / "date", f"#!/bin/sh\necho {day}\n")
    (shim / "date").chmod(0o755)
    return {"PATH": f"{shim}{os.pathsep}{os.environ['PATH']}"}


def many_apart(kk, count):
    write(kk / "x" / "a.md", "---\ntype: Service\ntitle: A\ndependsOn:\n  - x/b.md\n---\n")
    write(kk / "x" / "b.md", "---\ntype: Service\ntitle: B\n---\n")
    for n in range(count):
        write(kk / "y" / f"c{n:02}.md", f"---\ntype: Service\ntitle: C{n}\n---\n")


def test_isolated_names_a_concept_no_relation_joins_and_a_group_joined_only_to_itself(tmp_path):
    """Direction does not matter, a concept pointing at itself or at another bundle is still apart, and the largest group is the graph the others stand apart from."""
    kk = isolated_host(tmp_path)
    write(kk / "x" / "a.md", "---\ntype: Service\ntitle: A\ndependsOn:\n  - x/b.md\n---\n")
    write(kk / "x" / "b.md", "---\ntype: Service\ntitle: B\n---\n")
    write(kk / "x" / "c.md", "---\ntype: Service\ntitle: C\nrequires_check: [https://acme.example/knowledge/x/a]\n---\n")
    write(kk / "y" / "d.md", "---\ntype: Service\ntitle: D\nreferences:\n  - y/e.md\n---\n")
    write(kk / "y" / "e.md", "---\ntype: Service\ntitle: E\n---\n")
    write(kk / "z" / "self.md", "---\ntype: Service\ntitle: Self\nabout:\n  - z/self.md\n---\n")
    write(kk / "z" / "out.md", "---\ntype: Service\ntitle: Out\nabout:\n  - https://elsewhere.example/thing\n---\n")
    out = isolated(tmp_path)
    assert has_line(out, "Concepts no relation joins to another: 2"), out
    assert has_line(out, "- z/out.md") and has_line(out, "- z/self.md"), out
    assert has_line(out, "Groups of concepts joined only to each other: 1") and has_line(out, "- y/d.md, y/e.md"), out
    assert "x/a.md" not in out and "x/b.md" not in out and "x/c.md" not in out, out


@pytest.mark.parametrize(
    "target",
    ["/x/b.md", "/x/b", "x/b.md", "x/b", "b.md", "./b.md", "https://acme.example/knowledge/x/b.md", "https://acme.example/knowledge/x/b#part"],
)
def test_isolated_joins_each_spelling_of_a_target(tmp_path, target):
    """A false listing sends the librarian after a relation that already exists, so the report reads what lokf and the plugin read."""
    kk = isolated_host(tmp_path)
    write(kk / "x" / "a.md", f"---\ntype: Service\ntitle: A\nreferences:\n  - {target}\n---\n")
    write(kk / "x" / "b.md", "---\ntype: Service\ntitle: B\n---\n")
    assert has_line(isolated(tmp_path), "Concepts no relation joins to another: none"), target


def test_isolated_finds_a_concept_with_a_fragment_in_its_own_id(tmp_path):
    kk = isolated_host(tmp_path)
    write(kk / "x" / "a.md", "---\ntype: Service\ntitle: A\nreferences:\n  - https://other.example/vocab#B\n---\n")
    write(kk / "x" / "b.md", "---\ntype: Service\ntitle: B\nid: https://other.example/vocab#B\n---\n")
    assert has_line(isolated(tmp_path), "Concepts no relation joins to another: none")


def test_a_hyphen_in_a_field_name_does_not_hide_its_value_under_the_field_before(tmp_path):
    kk = isolated_host(tmp_path)
    write(kk / "x" / "a.md", "---\ntype: Service\ntitle: A\nresource: x\nemitted-by: https://acme.example/knowledge/x/b\n---\n")
    write(kk / "x" / "b.md", "---\ntype: Service\ntitle: B\n---\n")
    assert has_line(isolated(tmp_path), "Concepts no relation joins to another: none")


def test_isolated_leaves_out_what_cannot_join_and_a_retired_concept_joins_nothing(tmp_path):
    """An agent is reached only through author or publisher, the sources map has no source to state a relation from, and a link to a retired concept holds nothing together."""
    kk = isolated_host(tmp_path)
    write(kk / "x" / "a.md", "---\ntype: Service\ntitle: A\ndependsOn:\n  - x/b.md\n---\n")
    write(kk / "x" / "b.md", "---\ntype: Service\ntitle: B\n---\n")
    write(kk / "x" / "alone.md", "---\ntype: Service\ntitle: Alone\nabout:\n  - x/gone.md\n---\n")
    write(kk / "x" / "gone.md", "---\ntype: Service\ntitle: Gone\nstatus: deprecated\n---\n")
    write(kk / "x" / "org.md", "---\ntype: Organization\ntitle: Org\n---\n")
    write(kk / "x" / "me.md", "---\ntype: Person\ntitle: Me\n---\n")
    write(kk / "playbooks" / "knowledge-sources.md", "---\ntype: Playbook\ntitle: Map\n---\n")
    out = isolated(tmp_path)
    assert has_line(out, "Concepts no relation joins to another: 1") and has_line(out, "- x/alone.md"), out


def test_isolated_reports_nothing_of_a_bundle_too_small_to_join(tmp_path):
    kk = isolated_host(tmp_path)
    write(kk / "x" / "only.md", "---\ntype: Service\ntitle: Only\n---\n")
    out = isolated(tmp_path)
    assert has_line(out, "Concepts no relation joins to another: none"), out


def test_isolated_says_it_cannot_tell_without_a_base_iri(tmp_path):
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "# Acme\n")
    write(kk / "x" / "a.md", "---\ntype: Service\ntitle: A\ndependsOn:\n  - x/b.md\n---\n")
    write(kk / "x" / "b.md", "---\ntype: Service\ntitle: B\n---\n")
    assert "not computed" in isolated(tmp_path)


def test_the_work_list_shows_ten_and_the_isolated_command_shows_all(tmp_path):
    kk = isolated_host(tmp_path)
    many_apart(kk, 12)
    out = isolated(tmp_path, "worklist")
    assert has_line(out, "Concepts no relation joins to another: 12"), out
    assert len(re.findall(r"^- y/c\d\d\.md$", out, re.M)) == 10, out
    assert "- and 2 more, whose turn comes in a later month" in out, out
    assert len(re.findall(r"^- y/c\d\d\.md$", isolated(tmp_path), re.M)) == 12


@pytest.mark.parametrize("count", [11, 20, 25, 30, 37])
def test_every_concept_takes_a_turn_in_the_work_list_with_nothing_stamped(tmp_path, count):
    """A concept whose source states no relation stays listed and takes no stamp, so a fixed order would hold the same ten at the top for good."""
    kk = isolated_host(tmp_path)
    many_apart(kk, count)
    seen = set()
    for month in range(1, 13):
        env = at_month(tmp_path, f"2026-{month:02}-01")
        seen |= set(re.findall(r"^- (y/c\d\d\.md)$", isolated(tmp_path, "worklist", env=env), re.M))
    assert len(seen) == count, f"only {len(seen)} of {count} concepts took a turn in a year"


def test_the_work_list_shows_the_same_ten_within_a_month(tmp_path):
    """A busy week in the same month reads the sources a person may still be reviewing, and proposes the same concepts."""
    kk = isolated_host(tmp_path)
    many_apart(kk, 25)
    shown = lambda day: re.findall(r"^- y/c\d\d\.md$", isolated(tmp_path, "worklist", env=at_month(tmp_path, day)), re.M)
    assert shown("2026-03-01") == shown("2026-03-29")


def test_the_work_list_cuts_a_long_group_short(tmp_path):
    kk = isolated_host(tmp_path)
    for n in range(10):
        write(kk / "x" / f"main{n}.md", "---\ntype: Service\ntitle: M\nreferences:\n  - x/main0.md\n---\n")
    for n in range(8):
        write(kk / "y" / f"g{n}.md", "---\ntype: Service\ntitle: G\nreferences:\n  - y/g0.md\n---\n")
    out = isolated(tmp_path, "worklist")
    assert has_line(out, "- y/g0.md, y/g1.md, y/g2.md, y/g3.md, y/g4.md, and 3 more"), out
    assert "y/g7.md" in isolated(tmp_path)


def test_the_work_list_leaves_out_a_concept_a_person_declined_until_it_changes(tmp_path):
    """A person closed the pull request that touched it, so the same relation is not proposed again next month."""
    kk = isolated_host(tmp_path)
    many_apart(kk, 2)
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "start")
    base = git("rev-parse", "HEAD").strip()
    declined = tmp_path / "declined.txt"
    write(declined, f"declined 7 2026-01-01 {base}\ntouched y/c00.md\n")
    env = {"KNOWLEDGE_DECLINED": str(declined)}
    out = isolated(tmp_path, "worklist", env=env)
    assert not has_line(out, "- y/c00.md") and has_line(out, "- y/c01.md"), out
    assert has_line(isolated(tmp_path, env=env), "- y/c00.md"), "the isolated command should list every concept"
    write(kk / "y" / "c00.md", "---\ntype: Service\ntitle: C0 changed\n---\n")
    git("add", "-A")
    git("commit", "-q", "-m", "it changes")
    assert has_line(isolated(tmp_path, "worklist", env=env), "- y/c00.md"), "a change should bring the concept back"


def test_a_concept_standing_apart_makes_no_scheduled_run_busy(tmp_path):
    """It stays listed when its source states no relation, so counting it as work would mean a bundle that is never quiet."""
    kk = isolated_host(tmp_path)
    stamp = "generated:\n  by: process:ktl-librarian\n  at: 2026-01-01T00:00:00Z\n"
    write(kk / "x" / "a.md", f"---\ntype: Service\ntitle: A\n{stamp}---\n")
    write(kk / "x" / "b.md", f"---\ntype: Service\ntitle: B\n{stamp}---\n")
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "start")
    assert has_line(isolated(tmp_path), "Concepts no relation joins to another: 2"), "both concepts should stand apart"
    assert report(tmp_path, "quiet"), "a concept standing apart made the bundle busy"


def test_the_whole_report_counts_what_stands_apart_and_names_none_of_it(tmp_path):
    kk = isolated_host(tmp_path)
    write(kk / "x" / "a.md", "---\ntype: Service\ntitle: A\n---\n")
    write(kk / "x" / "b.md", "---\ntype: Service\ntitle: B\n---\n")
    out = isolated(tmp_path, "report")
    assert has_line(out, "Concepts no relation joins to another: 2; groups joined only to each other: none; the librarian takes these from its work list"), out


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
    assert "- x/aside.md: " not in out, out
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


# ---- the sample, and the evidence table ----------------------------------------
ADA = '- by: human:ada\n  at: "2026-01-02T10:00:00Z"\n'
GRACE_LATER = '- by: human:grace\n  at: "2026-01-05T10:00:00Z"\n'
AUTO = 'resource: src/b.md\nverified:\n- by: process:ktl-librarian\n  at: "2026-01-03T00:00:00Z"\n'
CONFIRMED = ["x/one.md", "x/reopened.md", "x/second.md", "x/three.md", "x/twice.md", "x/two.md"]
AUTOMATION = ["x/auto1.md", "x/auto2.md", "x/auto3.md"]
SECOND = "For a second person to re-check"
PASSED = "For a person to check what automation passed"
NO_DIGEST = "Sample: not drawn here, since the pick needs sha256sum or shasum and this host has neither"
HEADER = "path\ttype\tstatus\tstale_after\tresource\tevent\tby\tat\trevision\tcheck"


@pytest.fixture
def audit(tmp_path):
    """A bundle to sample and to table.

    Six concepts read as confirmed by a person: one of them twice by the same
    person, one by a second person, and one reopened. Three are checked by
    automation only, and a fourth such is a draft. An edited concept and a
    retired one each carry a second person's re-check, and neither reads as
    confirmed. One concept carries no event. The reserved files carry
    frontmatter a concept could, and are no concepts.
    """
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(kk / "log.md", "---\ntype: Service\ntitle: The log\nverified:\n" + ADA + "---\n\n# Change Log\n")
    write(kk / "x" / "index.md", "---\ntype: Service\ntitle: A folder index\nverified:\n" + ADA + "---\n")

    def concept(name, head, body=""):
        write(kk / "x" / f"{name}.md", f"---\ntype: Service\ntitle: {name.capitalize()}\n{head}---\n{body}")

    concept(
        "one",
        'resource: src/a.md\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n  revision: "1111111111111111111111111111111111111111"\n'
        'verified:\n- by: process:ktl-librarian\n  at: "2026-01-01T12:00:00Z"\n- by: human:ada\n  at: "2026-01-02T10:00:00Z"\n  revision: "3f9c2a1b7e0d4c6a8f5e2d1c9b8a7f6e5d4c3b2a"\n'
        "stale_after: 2030-06-01T00:00:00Z\n",
    )
    concept("two", 'verified:\n  by: human:ada\n  at: "2026-01-03T10:00:00Z"\n')
    concept("three", 'verified: [{ by: human:grace, at: "2026-01-04T10:00:00Z" }]\n')
    concept("twice", "verified:\n" + ADA + '- by: human:ada\n  at: "2026-02-02T10:00:00Z"\n')
    # second.md lists its later event first, and with an offset: the time
    # decides who was first, never the place in the file.
    concept("second", 'resource: src/a.md\nverified:\n- by: human:grace\n  at: "2026-03-01T09:00:00+02:00"\n' + ADA)
    concept("reopened", "status: draft\nverified:\n" + ADA, "\n## Open questions\n\n- 2026-01-06, process:ktl-librarian: still so?\n")
    for n in (1, 2, 3):
        concept(f"auto{n}", AUTO)
    concept("autodraft", "status: draft\n" + AUTO)
    concept("edited", 'generated:\n  by: process:ktl-librarian\n  at: "2026-02-01T00:00:00Z"\nverified:\n' + ADA + GRACE_LATER)
    concept("retired", "status: deprecated\nverified:\n" + ADA + GRACE_LATER)
    concept("unchecked", "")
    return tmp_path


def policy(root, body):
    """The curation policy concept, with these lines in its body. Nobody has checked it, so it is on no list."""
    write(
        root / ".lokf" / "knowledge" / "policies" / "knowledge-curation.md",
        f"---\ntype: Policy\ntitle: Knowledge curation policy\n---\n\n# Samples\n\n{body}\n",
    )


def by_digest(seed, paths):
    """The documented order: the SHA-256 of the seed, one space and the path, as hex, lowest first."""
    return sorted(paths, key=lambda path: hashlib.sha256(f"{seed} {path}".encode()).hexdigest())


def listed(out, heading):
    """The paths of the list under the heading that starts so, in the order printed."""
    paths, on = [], False
    for line in out.split("\n"):
        if line.startswith(heading + " ("):
            on = True
        elif on and line.startswith("- "):
            paths.append(re.search(r" \(([^()]+\.md)\) - ", line).group(1))
        elif on:
            break
    return paths


def path_without(tmp_path, *tools):
    """A PATH that holds every program on this one but the tools named."""
    folder = tmp_path / "bin-without"
    folder.mkdir()
    for source in reversed(os.environ["PATH"].split(os.pathsep)):
        if not os.path.isdir(source):
            continue
        for name in os.listdir(source):
            link = folder / name
            if name in tools:
                continue
            if link.is_symlink():
                link.unlink()
            os.symlink(os.path.join(source, name), link)
    return str(folder)


def test_each_list_is_its_population_in_the_order_of_the_digest_of_seed_and_path(audit):
    out = report(audit, "sample", "--seed", "s1", "--independent", "3", "--automation", "2").out
    assert listed(out, SECOND) == by_digest("s1", CONFIRMED)[:3] and listed(out, PASSED) == by_digest("s1", AUTOMATION)[:2], (
        f"report script's sample is not the first of each population by the digest of 's1 <path>': {out}"
    )


def test_the_sample_states_its_seed_and_the_same_seed_draws_the_same_lists(audit):
    first = report(audit, "sample", "--seed", "audit 7", "--independent", "2", "--automation", "2")
    again = report(audit, "sample", "--seed", "audit 7", "--independent", "2", "--automation", "2")
    assert first and first.out.split("\n")[0].startswith('Sample - seed "audit 7" (computed by knowledge-report.sh'), (
        f"report script's sample does not state its seed first: {first.out}"
    )
    assert first.out == again.out and listed(first.out, SECOND) == by_digest("audit 7", CONFIRMED)[:2], (
        f"report script drew two samples from one seed: {first.out} and then {again.out}"
    )


def test_two_seeds_draw_two_samples(audit):
    assert by_digest("s1", CONFIRMED)[:2] != by_digest("s2", CONFIRMED)[:2], "the two seeds of this test must order the fixture differently"
    one = listed(report(audit, "sample", "--seed", "s1", "--independent", "2").out, SECOND)
    two = listed(report(audit, "sample", "--seed", "s2", "--independent", "2").out, SECOND)
    assert one == by_digest("s1", CONFIRMED)[:2] and two == by_digest("s2", CONFIRMED)[:2], (
        f"report script's sample does not follow its seed: {one} for s1 and {two} for s2"
    )


def test_a_seed_is_hashed_as_written_with_its_spaces_and_backslashes(audit):
    seed = r"a\tb  \n 100%s"
    out = report(audit, "sample", "--seed", seed, "--independent", "3").out
    assert out.split("\n")[0].startswith(f'Sample - seed "{seed}" (') and listed(out, SECOND) == by_digest(seed, CONFIRMED)[:3], (
        f"report script read an escape or a format in a seed: {out}"
    )


def test_with_no_seed_given_the_seed_is_todays_date_in_utc(audit):
    before = today_utc()
    out = report(audit, "sample", "--independent", "3").out
    assert any(
        out.split("\n")[0].startswith(f'Sample - seed "{day}" (') and listed(out, SECOND) == by_digest(day, CONFIRMED)[:3]
        for day in {before, today_utc()}
    ), f"report script's sample is not seeded by today's date in UTC: {out}"


@pytest.mark.parametrize(
    ("line", "size"),
    [
        ("Independent re-check: 2", 2),
        ("- **Independent re-check:** 2", 2),
        ("  * Independent re-check : `2`  ", 2),
        ("> 1. **independent re-check**: 2 each month", 2),
        ("Independent re-check: 002", 2),
        ("Independent re-check: 0", 0),
        ("Independent re-check: 00", 0),
        ("Independent re-check: two", 0),
        ("Independent re-check: 2nd", 0),
        ("An independent re-check: 2", 0),
        ("```text\nIndependent re-check: 2\n```", 0),
    ],
)
def test_a_list_takes_its_size_from_its_line_in_the_curation_policy(audit, line, size):
    policy(audit, line)
    result = report(audit, "sample", "--seed", "s")
    if size:
        assert result and listed(result.out, SECOND) == by_digest("s", CONFIRMED)[:size], (
            f"report script did not read the size {size} from the policy line {line!r}: {result.out}"
        )
    else:
        assert result and result.out == "Sample: none drawn, since the curation policy asks for none", (
            f"report script read a size from the policy line {line!r}: {result.out}"
        )


def test_each_list_has_a_line_of_its_own_in_the_policy(audit):
    policy(audit, "Independent re-check: 2\n\nAutomation re-check: 1")
    out = report(audit, "sample", "--seed", "s").out
    assert has_line(out, f"{SECOND} (2, picked by a rule the curator cannot steer):") and has_line(
        out, f"{PASSED} (1, picked by the same rule):"
    ), f"report script did not draw each list at the size its policy line gives: {out}"
    assert listed(out, PASSED) == by_digest("s", AUTOMATION)[:1], f"report script drew the wrong automation list: {out}"


def test_a_policy_line_for_one_list_draws_that_list_only(audit):
    policy(audit, "Automation re-check: 2")
    out = report(audit, "sample", "--seed", "s").out
    assert listed(out, PASSED) == by_digest("s", AUTOMATION)[:2] and SECOND not in out, (
        f"report script drew a list the policy does not ask for: {out}"
    )


def test_a_size_given_as_a_flag_decides_over_the_policy(audit):
    policy(audit, "Independent re-check: 2\n\nAutomation re-check: 1")
    out = report(audit, "sample", "--seed", "s", "--independent", "4", "--automation", "0").out
    assert listed(out, SECOND) == by_digest("s", CONFIRMED)[:4] and PASSED not in out, (
        f"report script let the policy decide over --independent 4 and --automation 0: {out}"
    )


def test_a_population_smaller_than_the_size_is_listed_whole_and_the_sample_says_so(audit):
    out = report(audit, "sample", "--seed", "s", "--independent", "9", "--automation", "9").out
    assert listed(out, SECOND) == by_digest("s", CONFIRMED) and listed(out, PASSED) == by_digest("s", AUTOMATION), (
        f"report script did not list a short population whole: {out}"
    )
    for want in [
        f"{SECOND} (6, picked by a rule the curator cannot steer):",
        "Asked for 9: the bundle holds 6 confirmed by a person, so the list holds every one.",
        f"{PASSED} (3, picked by the same rule):",
        "Asked for 9: the bundle holds 3 checked by automation only, drafts apart, so the list holds every one.",
    ]:
        assert has_line(out, want), f"report script's sample lacks '{want}': {out}"


def test_a_population_as_large_as_the_size_is_listed_with_no_such_line(audit):
    out = report(audit, "sample", "--seed", "s", "--independent", "6").out
    assert len(listed(out, SECOND)) == 6 and "Asked for" not in out, f"report script called a full list short: {out}"


def test_a_list_with_nothing_to_draw_from_says_it_is_empty(tmp_path):
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n")
    write(kk / "x" / "a.md", "---\ntype: Service\ntitle: A\n---\n")
    result = report(tmp_path, "sample", "--seed", "s", "--independent", "2")
    assert result and result.out.split("\n")[1:] == [
        f"{SECOND} (0, picked by a rule the curator cannot steer):",
        "Asked for 2: the bundle holds none confirmed by a person, so the list is empty.",
        "Re-checked by a second person: 0 of 0 confirmed",
    ], f"report script's sample of an unconfirmed bundle is not as expected: {result.out}"


@pytest.mark.parametrize("flags", [[], ["--independent", "0", "--automation", "00"]], ids=["no policy", "two sizes of 0"])
def test_with_no_list_asked_for_the_sample_is_one_line_that_says_so(audit, flags):
    result = report(audit, "sample", *flags)
    want = "Sample: none drawn, since " + ("no size above 0 was given" if flags else "the curation policy asks for none")
    assert result and result.out == want, f"report script's sample, with no list asked for, is not the one line '{want}': {result.out}"


@pytest.mark.parametrize(
    "args",
    [
        ["sample", "--independent", "x"],
        ["sample", "--automation", "-1"],
        ["sample", "--independent"],
        ["sample", "--seed"],
        ["sample", "--size", "2"],
        ["sample", "--seed", ""],
        ["sample", "--seed", "two\nlines"],
        ["evidence", "x/one.md"],
    ],
    ids=lambda args: " ".join(args).replace("\n", " "),
)
def test_a_call_the_sample_or_the_table_cannot_read_is_refused(audit, args):
    result = report(audit, *args)
    assert result.rc == 2 and "Sample - seed" not in result.out and HEADER not in result.out, (
        f"report script accepted {args}: {result.out}"
    )


def test_with_no_digest_tool_the_sample_says_which_it_needs_and_exits_2(audit, tmp_path):
    result = report(audit, "sample", "--independent", "1", env={"PATH": path_without(tmp_path, "sha256sum", "shasum")})
    assert result.rc == 2 and result.out == NO_DIGEST, f"report script's sample, with no digest tool, did not say so and exit 2: {result.out}"


def test_with_no_digest_tool_the_whole_report_says_so_and_goes_on(audit, tmp_path):
    policy(audit, "Independent re-check: 2")
    result = report(audit, env={"PATH": path_without(tmp_path, "sha256sum", "shasum")})
    assert result.rc == 0 and result.out.split("\n")[-2:] == ["", NO_DIGEST] and "Confirmed by a person: 6 of 14" in result.out, (
        f"report script's whole report, with no digest tool, is not the report and then one line: {result.out}"
    )


def test_where_there_is_no_sha256sum_the_sample_uses_shasum(audit, tmp_path):
    if not (have("shasum") and have("sha256sum")):
        pytest.skip("this test compares the two digest tools, and one is not installed")
    args = ["sample", "--seed", "s", "--independent", "3", "--automation", "2"]
    result = report(audit, *args, env={"PATH": path_without(tmp_path, "sha256sum")})
    assert result and result.out == report(audit, *args).out and listed(result.out, SECOND) == by_digest("s", CONFIRMED)[:3], (
        f"report script drew another sample with shasum: {result.out}"
    )


def test_the_automation_list_leaves_out_a_draft_and_whatever_a_person_confirmed(audit):
    """one.md carries automation's event and a person's, autodraft.md is a draft, and edited.md and retired.md read as neither."""
    out = report(audit, "sample", "--seed", "s", "--automation", "99").out
    assert sorted(listed(out, PASSED)) == AUTOMATION, f"report script's automation list is not the three concepts checked by automation only: {out}"


def test_the_list_for_a_second_person_is_what_reads_as_confirmed_by_a_person(audit):
    """A reopened concept reads as confirmed, as the health line counts it. An edited one and a retired one do not."""
    out = report(audit, "sample", "--seed", "s", "--independent", "99").out
    assert sorted(listed(out, SECOND)) == CONFIRMED and "Confirmed by a person: 6 of 13" in report(audit, "health").out, (
        f"report script's list for a second person is not the six concepts the health line counts as confirmed: {out}"
    )


@pytest.mark.parametrize(
    "want",
    [
        "- One (x/one.md) - src/a.md - confirmed by ada",
        "- Second (x/second.md) - src/a.md - confirmed by ada, grace",
        "- Twice (x/twice.md) - no source recorded - confirmed by ada",
        "- Three (x/three.md) - no source recorded - confirmed by grace",
    ],
)
def test_the_list_for_a_second_person_names_each_person_who_confirmed_the_concept_once(audit, want):
    out = report(audit, "sample", "--seed", "s", "--independent", "99").out
    assert has_line(out, want), f"report script's list for a second person lacks '{want}': {out}"


def test_the_automation_list_names_the_concept_and_its_source_and_nobody(audit):
    out = report(audit, "sample", "--seed", "s", "--automation", "99").out
    assert has_line(out, "- Auto1 (x/auto1.md) - src/b.md"), f"report script's automation list lacks '- Auto1 (x/auto1.md) - src/b.md': {out}"


def test_a_second_persons_re_check_is_counted_and_the_same_persons_is_not(audit):
    """second.md is counted. twice.md is one person twice. edited.md and retired.md carry a second person's re-check and do not read as confirmed."""
    out = report(audit, "sample", "--seed", "s", "--independent", "1").out
    assert out.split("\n")[-1] == "Re-checked by a second person: 1 of 6 confirmed", (
        f"report script miscounted the second-person re-checks: {out}"
    )


def test_the_whole_report_ends_with_the_sample_the_policy_asks_for(audit):
    policy(audit, "Independent re-check: 2\n\nAutomation re-check: 1")
    before = today_utc()
    whole = report(audit).out
    assert any(
        whole.endswith("\n\n" + report(audit, "sample", "--seed", day).out) and f'Sample - seed "{day}" (' in whole
        for day in {before, today_utc()}
    ), f"report script's whole report does not end with today's sample: {whole}"


def test_the_whole_report_says_nothing_of_a_sample_the_policy_does_not_ask_for(audit):
    policy(audit, "Independent re-check: 0")
    result = report(audit)
    assert result and "Sample" not in result.out and "re-check" not in result.out, (
        f"report script's whole report names a sample no policy asks for: {result.out}"
    )


def table(root):
    """The evidence table as its lines, and the same split into columns."""
    result = bash(REPORT, "evidence", cwd=root, stdout_only=True)
    assert result, f"report script's evidence form failed: {result.out}"
    rows = result.out.split("\n")
    return rows, [row.split("\t") for row in rows]


def test_the_evidence_table_starts_with_its_header_and_every_row_has_ten_columns(audit):
    rows, cells = table(audit)
    assert rows[0] == HEADER and len(rows) == 21 and all(len(row) == 10 for row in cells), (
        f"report script's evidence table is not a header and 20 rows of ten columns: {rows}"
    )


def test_a_concept_has_a_row_for_its_generated_record_and_one_for_each_verified_event(audit):
    rows, _ = table(audit)
    head = "x/one.md\tService\t\t2030-06-01\tsrc/a.md\t"
    assert [row for row in rows if row.startswith("x/one.md\t")] == [
        head + "generated\tprocess:ktl-librarian\t2026-01-01T00:00:00Z\t1111111111111111111111111111111111111111\t",
        head + "verified\tprocess:ktl-librarian\t2026-01-01T12:00:00Z\t\t",
        head + "verified\thuman:ada\t2026-01-02T10:00:00Z\t3f9c2a1b7e0d4c6a8f5e2d1c9b8a7f6e5d4c3b2a\tfirst",
    ], f"report script's evidence rows for x/one.md are not its three events: {rows}"


def test_a_concept_with_no_event_has_one_row_with_the_event_columns_empty(audit):
    rows, _ = table(audit)
    assert [row for row in rows if row.startswith("x/unchecked.md\t")] == ["x/unchecked.md\tService\t\t\t\t\t\t\t\t"], (
        f"report script's evidence table does not give an unchecked concept one row with no event: {rows}"
    )


def test_the_evidence_rows_go_by_path_then_generated_before_verified_then_time(audit):
    """edited.md was generated after both its confirmations, and second.md lists its later event first."""
    _, cells = table(audit)
    got = [(row[0], row[5], row[7]) for row in cells[1:]]
    assert got == sorted(got, key=lambda row: (row[0], row[1] != "generated", row[2])), (
        f"report script's evidence rows are not in the order of path, event and time: {got}"
    )
    assert [row for row in got if row[0] == "x/edited.md"] == [
        ("x/edited.md", "generated", "2026-02-01T00:00:00Z"),
        ("x/edited.md", "verified", "2026-01-02T10:00:00Z"),
        ("x/edited.md", "verified", "2026-01-05T10:00:00Z"),
    ] and [row[2] for row in got if row[0] == "x/second.md"] == ["2026-01-02T10:00:00Z", "2026-03-01T07:00:00Z"], (
        f"report script's evidence rows put a later event first: {got}"
    )


CHECKS = [
    ("x/twice.md", [("human:ada", "first"), ("human:ada", "same-person")]),
    ("x/second.md", [("human:ada", "first"), ("human:grace", "second-person")]),
    ("x/retired.md", [("human:ada", "first"), ("human:grace", "second-person")]),
    ("x/one.md", [("process:ktl-librarian", ""), ("process:ktl-librarian", ""), ("human:ada", "first")]),
    ("x/auto1.md", [("process:ktl-librarian", "")]),
]


@pytest.mark.parametrize(("path", "want"), CHECKS, ids=[path for path, _ in CHECKS])
def test_the_check_column_says_first_same_person_or_second_person_for_a_persons_event_only(audit, path, want):
    _, cells = table(audit)
    got = [(row[6], row[9]) for row in cells if row[0] == path]
    assert got == want, f"report script's check column for {path} is {got}, not {want}"


def test_an_event_whose_time_cannot_be_read_is_given_as_written_and_takes_no_place(tmp_path):
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n")
    write(
        kk / "x" / "a.md",
        '---\ntype: Service\ntitle: A\nstale_after: next spring\nverified:\n- by: human:zed\n  at: sometime\n' + ADA + GRACE_LATER + "---\n",
    )
    _, cells = table(tmp_path)
    assert [(row[3], row[6], row[7], row[9]) for row in cells[1:]] == [
        ("next spring", "human:ada", "2026-01-02T10:00:00Z", "first"),
        ("next spring", "human:grace", "2026-01-05T10:00:00Z", "second-person"),
        ("next spring", "human:zed", "sometime", ""),
    ], f"report script gave an undated event a place among the dated ones: {cells}"


def test_a_tab_or_a_line_break_inside_a_value_is_one_space(tmp_path):
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n")
    write(
        kk / "x" / "a.md",
        '---\ntype: "Ser\tvice"\ntitle: A\nstatus: "dra\rft"\nresource: "src/a\tb.md"\nverified:\n- by: "process:two\twords"\n  at: "2026-01-03T00:00:00Z"\n  revision: "W/\tetag"\n---\n',
    )
    result = bash(REPORT, "evidence", cwd=tmp_path, stdout_only=True)
    assert result.out.split("\n")[1:] == ["x/a.md\tSer vice\tdra ft\t\tsrc/a b.md\tverified\tprocess:two words\t2026-01-03T00:00:00Z\tW/ etag\t"], (
        f"report script let a tab or a line break inside a value through: {result.out!r}"
    )


def test_the_evidence_table_is_the_same_bytes_on_every_run_with_git_or_without(audit, tmp_path):
    def once(root, **env):
        return run(["bash", REPORT, "evidence"], cwd=root, env=env, stdout_only=True).out

    first = once(audit)
    git = Git(audit)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "the bundle")
    write(audit / "src" / "a.md", "an edit nobody committed\n")
    assert first.split("\n")[0] == HEADER and first == once(audit) == once(audit, TZ="Asia/Tokyo"), (
        "report script's evidence table changed with git history, an uncommitted source or the time zone"
    )


def test_the_evidence_table_leaves_out_index_md_and_log_md(audit):
    _, cells = table(audit)
    paths = sorted({row[0] for row in cells[1:]})
    assert paths == sorted([*CONFIRMED, *AUTOMATION, "x/autodraft.md", "x/edited.md", "x/retired.md", "x/unchecked.md"]), (
        f"report script's evidence table holds a reserved file, or lacks a concept: {paths}"
    )


# ---- what an audit of the report found, 2026-11-12 ---------------------------


def labelled(tmp_path, name, frontmatter):
    kk = tmp_path / ".lokf" / "knowledge"
    if not (kk / "index.md").exists():
        write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(kk / "t" / f"{name}.md", f"---\ntype: Service\ntitle: {name}\n{frontmatter}---\n")
    return report(tmp_path, "labels", f"t/{name}.md").out


CONFIRMED_AT_NOON = 'verified:\n  - by: human:ada\n    at: "2026-11-12T12:00:00Z"\n'


@pytest.mark.parametrize("edited", ["2026-11-12T10:00:00-0500", "2026-11-12T10:00:00-05:00", "2026-11-12T16:00:00+0100"])
def test_a_compact_offset_is_read_as_the_offset_it_is(tmp_path, edited):
    """`date +%z` writes -0500. Read as UTC, an edit at 15:00Z hid behind a confirmation at noon."""
    out = labelled(tmp_path, "m", f'generated:\n  by: process:ktl-librarian\n  at: "{edited}"\n{CONFIRMED_AT_NOON}')
    assert "edited since a person last confirmed it (confirmed 2026-11-12T12:00:00Z, edited 2026-11-12T15:00:00Z)" in out, out


def test_a_comment_beside_a_quoted_value_is_no_part_of_the_value(tmp_path):
    out = labelled(tmp_path, "a", f'status: "deprecated"  # superseded in March\n{CONFIRMED_AT_NOON}')
    assert out.rstrip().endswith("- retired"), f"a quoted status with a comment beside it was not read: {out}"
    out = labelled(tmp_path, "b", "status: 'draft' # wip\nstale_after: \"2020-01-01\"  # quarterly\n")
    assert "still a draft" in out and "past its review date (2020-01-01)" in out, f"a quoted review date with a comment beside it was not read: {out}"


def test_a_comment_line_among_the_events_ends_no_event_block(tmp_path):
    out = labelled(tmp_path, "c", 'verified:\n  - by: process:ktl-librarian\n    at: "2026-11-01T00:00:00Z"\n# a note in the first column\n  - by: human:ada\n    at: "2026-11-12T12:00:00Z"\n')
    assert "confirmed by a person, 2026-11-12" in out, f"the event below a comment line went unread: {out}"


def test_an_identifier_with_a_scheme_is_no_file_that_can_be_gone(tmp_path):
    """A urn or a doi names no file, as the toolkit reads it. Listed as gone on every run, it kept the work list from ever being quiet."""
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(kk / "references" / "rfc.md", '---\ntype: Reference\ntitle: RFC\nresource: urn:ietf:rfc:9110\nsources:\n  - resource: doi:10.1000/182\n  - resource: "urn:isbn:0451450523"\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n---\n')
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "one")
    out = report(tmp_path, "worklist").out
    assert has_line(out, "Sources that moved since the concept was derived or last checked: none") and "(gone)" not in out, out
    assert report(tmp_path, "quiet").rc == 0, report(tmp_path, "quiet").out
    assert "urn:" not in report(tmp_path, "coverage").out


def test_the_root_as_a_source_moves_with_the_repository_and_not_with_the_bundle(tmp_path):
    """A source map names `.`, which holds the bundle too: the librarian's own commit once moved it, so no later week was quiet."""
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    stamp = 'generated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n'
    write(kk / "playbooks" / "map.md", f"---\ntype: Playbook\ntitle: Map\nresource: .\n{stamp}---\n")
    write(kk / "glossary" / "a.md", f"---\ntype: GlossaryTerm\ntitle: A\nresource: README.md\n{stamp}---\n")
    write(tmp_path / "README.md", "# Acme\n")
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "one")
    write(kk / "glossary" / "b.md", f"---\ntype: GlossaryTerm\ntitle: B\nresource: README.md\n{stamp}---\n")
    git("add", "-A")
    git("commit", "-q", "-m", "a commit that touches the bundle alone")
    quiet = report(tmp_path, "quiet")
    assert quiet.rc == 0 and quiet.out.startswith("Quiet"), f"a bundle-only commit moved the root: {quiet.out}"
    append(tmp_path / "README.md", "more\n")
    git("commit", "-q", "-am", "a source moves")
    out = report(tmp_path, "worklist").out
    assert matches(out, r"^- playbooks/map\.md: \. \(\d{4}-\d\d-\d\d\)$"), f"a commit outside the bundle did not move the root: {out}"


def test_the_work_list_names_each_concept_quiet_counts_as_having_no_stamp(tmp_path):
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(kk / "glossary" / "a.md", "---\ntype: GlossaryTerm\ntitle: A\n---\n")
    write(kk / "glossary" / "b.md", '---\ntype: GlossaryTerm\ntitle: B\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n---\n')
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "one")
    quiet, out = report(tmp_path, "quiet"), report(tmp_path, "worklist").out
    assert quiet.rc == 1 and "concepts with no stamp: 1" in quiet.out, quiet.out
    assert has_line(out, "Concepts with no stamp, neither derived by the pen nor checked: 1") and has_line(out, "- glossary/a.md: no stamp") and "glossary/b.md: no stamp" not in out, out


@pytest.fixture
def quoting(tmp_path):
    """Two concepts quote one file and a third cites it by footnote alone; the file then moves in a later commit."""
    kk = tmp_path / ".lokf" / "knowledge"
    write(tmp_path / "docs" / "limits.md", "# Limits\n\nThe API serves 600 requests a minute.\n\nRows are kept 13 months.\n")
    write(tmp_path / "docs" / "other.md", "other\n")
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    stamp = 'generated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n'
    # rate.md quotes in its second entry, and names its own id.
    write(
        kk / "x" / "rate.md",
        "---\ntype: Service\nid: https://acme.example/knowledge/x/rate\ntitle: Rate\nsources:\n  - resource: docs/other.md\n  - resource: docs/limits.md\n"
        f'    id: limits.md\n    excerpt: "The API serves 600 requests a minute."\n{stamp}---\n\nIt serves 600.[^limits.md]\n\n[^limits.md]: docs/limits.md, the first line\n',
    )
    # kept.md has no id, and its excerpt is a block scalar whose lines look like keys and items.
    write(
        kk / "x" / "kept.md",
        f"---\ntype: Service\ntitle: Kept\nsources:\n  - excerpt: >-\n      resource: not/a/key.md\n      - Rows are kept 13 months.\n    resource: docs/limits.md\n{stamp}---\n",
    )
    write(
        kk / "x" / "cited.md",
        f"---\ntype: Service\ntitle: Cited\nsources:\n  - resource: docs/limits.md\n    id: limits.md\n{stamp}---\n\nRows.[^limits.md]\n\n[^limits.md]: docs/limits.md\n",
    )
    write(kk / "log.md", "# Change Log\n")
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "sources and concepts in one commit")
    append(tmp_path / "docs" / "limits.md", "\nA new section.\n")
    git("commit", "-q", "-am", "the file moves on")
    return tmp_path


def toolkit(root, say, rc):
    """A toolkit in .lokf/.venv that notes the folder it ran in and its arguments, says `say` and exits `rc`."""
    calls = root.parent / f"{root.name}-lokf-calls.txt"
    write(root / ".lokf" / ".venv" / "bin" / "lokf", f'#!/bin/sh\necho "$(pwd -P) $*" >> "{calls}"\n{say}\nexit {rc}\n').chmod(0o755)
    return calls


HOLDS = "echo 'OK - 3 concepts in knowledge validate against KnowledgeBundle. Every local excerpt is in its resource.'"


def test_the_work_list_says_a_moved_source_still_holds_the_passage_a_concept_quotes(quoting):
    """Most edits to a file leave the quoted passage alone, and the list says so of each concept that quotes it."""
    calls = toolkit(quoting, HOLDS, 0)
    out = report(quoting, "worklist").out
    assert (
        has_line(out, "Excerpts their file no longer holds, each a claim whose ground changed: none")
        and matches(out, r"^- x/rate\.md: docs/limits\.md \(\d{4}-\d\d-\d\d, the quoted passage holds\)$")
        and matches(out, r"^- x/kept\.md: docs/limits\.md \(\d{4}-\d\d-\d\d, the quoted passage holds\)$")
        and matches(out, r"^- x/cited\.md: docs/limits\.md \(\d{4}-\d\d-\d\d\)$")
        and read(calls).count("validate") == 1
    ), f"the work list did not say the quoted passages hold, or ran the toolkit more than once: {out}"


def test_the_work_list_puts_first_an_excerpt_its_file_no_longer_holds(quoting):
    """The toolkit names the concept by its IRI and the entry by its place: one concept is found by its id, the other by its path."""
    toolkit(
        quoting,
        "echo \"[ERROR] https://acme.example/knowledge/x/rate: \\`sources[1].excerpt\\` ('The API serves 600') is not in 'docs/limits.md'\" >&2\n"
        "echo \"[ERROR] https://acme.example/knowledge/x/kept: \\`sources[0].excerpt\\` ('resource: not') is not in 'docs/limits.md'\" >&2",
        1,
    )
    out = report(quoting, "worklist").out
    first = out.split("\n")[1:4]
    assert first == [
        "Excerpts their file no longer holds, each a claim whose ground changed: 2",
        "- x/kept.md: docs/limits.md",
        "- x/rate.md: docs/limits.md",
    ] and matches(out, r"^- x/rate\.md: docs/limits\.md \(\d{4}-\d\d-\d\d, the quoted passage is gone\)$"), (
        f"the work list did not name each excerpt its file no longer holds: {out}"
    )


def test_the_work_list_counts_the_footnoted_sources_that_quote_nothing(quoting):
    toolkit(quoting, HOLDS, 0)
    out = report(quoting, "worklist").out
    assert has_line(out, "Footnoted sources that carry no excerpt: 1") and has_line(out, "- x/cited.md: docs/limits.md"), (
        f"the work list did not list the footnoted source with no excerpt: {out}"
    )


@pytest.mark.parametrize(
    "say, rc, want",
    [
        (None, 0, "Excerpts: not checked here, since .lokf/.venv holds no lokf toolkit"),
        ("echo 'No such option: --check-excerpts' >&2", 2, "Excerpts: not checked here, since lokf validate gave no verdict on them"),
        ("echo '[ERROR] x/rate.md: type is required' >&2", 1, "Excerpts: not checked here, since lokf validate gave no verdict on them"),
    ],
    ids=["no toolkit", "a toolkit before lokf 0.9.0", "a bundle the schema rejects"],
)
def test_without_a_verdict_on_the_excerpts_the_work_list_says_none_holds(quoting, say, rc, want):
    """Nothing is said to hold unless the toolkit said so of the excerpts."""
    if say is not None:
        toolkit(quoting, say, rc)
    out = report(quoting, "worklist").out
    assert want in out and "the quoted passage" not in out and "Excerpts their file" not in out, (
        f"the work list gave a verdict the toolkit did not give: {out}"
    )


def test_the_toolkit_checks_excerpts_with_the_domain_vocabulary_the_justfile_names(quoting):
    write(quoting / ".lokf" / "justfile", 'bundle := "knowledge"\nschema := "schema/domain.yaml"\n')
    write(quoting / ".lokf" / "schema" / "domain.yaml", "id: https://acme.example/schema\n")
    calls = toolkit(quoting, HOLDS, 0)
    report(quoting, "worklist")
    folder, _, args = read(calls).strip().partition(" ")
    assert folder == str((quoting / ".lokf" / "schema").resolve()) and args.startswith("validate --schema domain.yaml --check-excerpts "), (
        f"the toolkit was not run from the schema's folder with --schema: {read(calls)}"
    )


def test_a_bundle_that_quotes_nothing_never_runs_the_toolkit(moved):
    """Only the work list runs it, and only when a concept carries an excerpt."""
    calls = toolkit(moved, HOLDS, 0)
    out = report(moved, "worklist").out
    assert not calls.exists() and "Excerpts" not in out and has_line(out, "Footnoted sources that carry no excerpt: none"), (
        f"the work list ran the toolkit, or spoke of excerpts, with none in the bundle: {out}"
    )


def test_no_other_form_runs_the_toolkit(quoting):
    calls = toolkit(quoting, HOLDS, 0)
    for form in ([], ["health"], ["labels"], ["quiet"], ["evidence"]):
        report(quoting, *form)
    assert not calls.exists(), f"a form other than the work list ran the toolkit: {read(calls)}"


# ---- what it costs, as the bundle grows --------------------------------------


def counting(tmp_path, *tools):
    """A PATH on which each of these tools logs one line a call, then runs the real one."""
    shim = tmp_path / "counting"
    for tool in tools:
        real = shutil.which(tool)
        write(shim / tool, f'#!/bin/sh\necho {tool} >> "{shim}/calls"\nexec "{real}" "$@"\n')
        (shim / tool).chmod(0o755)
    return shim, {"PATH": f"{shim}{os.pathsep}{os.environ['PATH']}"}


def grown(root, n):
    """A committed bundle of n concepts, each stamped against a source of its own that moved since."""
    root.mkdir(parents=True)
    git = Git(root)
    git.init()
    kk = root / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    for i in range(n):
        write(root / "src" / f"s{i}.md", "one\n")
        write(
            kk / "x" / f"c{i}.md",
            f'---\ntype: Service\ntitle: C{i}\nresource: src/s{i}.md\nsources:\n  - resource: src\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:{i % 60:02d}Z"\n'
            f'verified:\n  - by: human:ada\n    at: "2026-01-02T00:00:{i % 60:02d}Z"\n---\n\nBody {i}.\n\n## Open questions\n\n- 2026-01-03, process:ktl-librarian: is src/s{i}.md still right?\n',
        )
    git("add", "-A")
    git("commit", "-q", "-m", "concepts")
    for i in range(0, n, 2):
        write(root / "src" / f"s{i}.md", "two\n")
    git("commit", "-q", "-am", "sources")
    return root


@pytest.mark.parametrize(("form", "tool"), [(["labels"], "awk"), (["labels", "x/c1.md"], "awk"), (["evidence"], "awk"), (["worklist"], "git"), (["quiet"], "git"), ([], "git")])
def test_a_larger_bundle_starts_no_more_processes(tmp_path, form, tool):
    """Each mode once started an awk for each concept, 3.5 seconds for one label at 2,000 concepts, and the work list asked git about each source of each concept, one question at a time, 208 seconds."""
    calls = []
    for n in (3, 12):
        root = grown(tmp_path / str(n), n)
        shim, env = counting(tmp_path / f"shim{n}", tool)
        result = report(root, *form, env=env)
        assert result.rc in (0, 1), result.out
        calls.append(read(shim / "calls").count("\n") if (shim / "calls").exists() else 0)
    assert calls[0] == calls[1], f"{' '.join(form) or 'the whole report'} ran {tool} {calls[0]} times for 3 concepts and {calls[1]} for 12"


def test_a_link_that_points_nowhere_hides_no_other_concept(tmp_path):
    """One awk reads every concept, and awk stops at a file it cannot open."""
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(kk / "t" / "zz.md", "---\ntype: GlossaryTerm\ntitle: A\n---\n")
    os.symlink("nowhere.md", kk / "t" / "dangling.md")
    out = report(tmp_path, "labels").out
    assert has_line(out, "- A (t/zz.md) - nobody has checked this yet"), f"a dangling link hid a concept: {out}"


# ---- what the comparison could not see ----------------------------------------


def waited(tmp_path, revision):
    """A source changed on the default branch while the pull request that stamps its concept waited, then the squash merge."""
    git = Git(tmp_path)
    git.init()
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(tmp_path / "docs" / "a.md", "one\n")
    write(tmp_path / "docs" / "b.md", "one\n")
    git("add", "-A")
    git("commit", "-q", "-m", "init")
    base = git("rev-parse", "HEAD")
    append(tmp_path / "docs" / "a.md", "two\n")
    git("commit", "-q", "-am", "docs: a.md changes while the pull request waits")
    rev = {"base": f"\n  revision: {base}", "none": "", "unknown": "\n  revision: " + "0" * 40}[revision]
    write(
        kk / "t" / "a.md",
        f'---\ntype: GlossaryTerm\ntitle: A\nresource: docs/a.md\nsources:\n  - resource: docs/b.md\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-11-01T00:00:00Z"{rev}\n---\n\nSays what docs/a.md said.\n',
    )
    append(tmp_path / "docs" / "b.md", "changed in the pull request\n")
    git("add", "-A")
    git("commit", "-q", "-m", "the librarian pull request, squash-merged")
    return tmp_path


def test_a_source_changed_while_the_pull_request_waited_has_moved_when_the_event_names_its_revision(tmp_path):
    """The squash merge records the stamp after the change, so the commit that recorded it once hid the move."""
    out = report(waited(tmp_path, "base"), "worklist").out
    assert matches(out, r"^- t/a\.md: docs/a\.md \(\d{4}-\d\d-\d\d\)$"), f"a source that changed while the pull request waited did not move: {out}"
    assert "docs/b.md (" not in out, f"a source changed in the recording commit itself moved: {out}"
    assert report(tmp_path, "quiet").rc == 1


def test_a_revision_pins_the_resource_alone_and_the_recording_commit_decides_the_other_sources(tmp_path):
    """A curator pins the last commit of the resource, so a source changed after that commit but before the confirmation read as moved."""
    git = Git(tmp_path)
    git.init()
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(tmp_path / "docs" / "a.md", "one\n")
    write(tmp_path / "docs" / "c.md", "one\n")
    git("add", "-A")
    git("commit", "-q", "-m", "init")
    pin = git("rev-parse", "HEAD")
    append(tmp_path / "docs" / "c.md", "two, which the curator was shown\n")
    git("commit", "-q", "-am", "docs: c.md changes before the confirmation")
    write(
        kk / "t" / "a.md",
        "---\ntype: GlossaryTerm\ntitle: A\nresource: docs/a.md\nsources:\n  - resource: docs/c.md\n"
        f'verified:\n  - by: human:ada\n    at: "2026-11-01T00:00:00Z"\n    revision: "{pin}"\n---\n\nSays what docs/a.md and docs/c.md say.\n',
    )
    git("add", "-A")
    git("commit", "-q", "-m", "the curation pull request, squash-merged")
    out = report(tmp_path).out
    assert "docs/c.md (" not in out, f"a source that changed before the confirmation read as moved: {out}"
    append(tmp_path / "docs" / "c.md", "three\n")
    git("commit", "-q", "-am", "docs: c.md changes after the confirmation")
    out = report(tmp_path).out
    assert matches(out, r"^- t/a\.md: docs/c\.md \(\d{4}-\d\d-\d\d\)$"), f"a source that changed after the confirmation did not move: {out}"


@pytest.mark.parametrize("revision", ["none", "unknown"])
def test_without_a_revision_this_history_holds_the_recording_commit_decides(tmp_path, revision):
    out = report(waited(tmp_path, revision), "worklist").out
    assert has_line(out, "Sources that moved since the concept was derived or last checked: none"), out


def test_a_source_git_holds_no_history_of_is_named_and_makes_no_run_busy(tmp_path):
    """An ignored file never moved, and nothing said it was never compared."""
    git = Git(tmp_path)
    git.init()
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(tmp_path / ".gitignore", "build/\n")
    write(tmp_path / "build" / "api.md", "generated\n")
    write(tmp_path / "docs" / "a.md", "a\n")
    stamp = 'generated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n'
    write(kk / "t" / "ign.md", f"---\ntype: GlossaryTerm\ntitle: Ign\nresource: build/api.md\n{stamp}---\n")
    write(kk / "t" / "doc.md", f"---\ntype: GlossaryTerm\ntitle: Doc\nresource: docs/a.md\n{stamp}---\n")
    git("add", "-A")
    git("commit", "-q", "-m", "one")
    out = report(tmp_path, "worklist").out
    assert has_line(out, "Sources git holds no history of, so not compared (an ignored file, or one inside a submodule): 1") and has_line(
        out, "- t/ign.md: build/api.md"
    ), f"the work list did not name a source git holds no history of: {out}"
    quiet = report(tmp_path, "quiet")
    assert quiet.rc == 0, f"a source git holds no history of made a run busy: {quiet.out}"


def test_a_folder_named_like_a_concept_hides_no_concept(tmp_path):
    """mawk stopped at a folder named x.md, and the report read a bundle of none, and quiet called a busy week quiet."""
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(kk / "t" / "zz.md", "---\ntype: GlossaryTerm\ntitle: A\n---\n")
    write(kk / "t" / "dir.md" / "keep", "")
    (kk / "t" / "linked.md").symlink_to(kk / "t" / "dir.md")
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "one")
    env = mawk_path(tmp_path)
    out = report(tmp_path, "labels", env=env).out
    assert has_line(out, "- A (t/zz.md) - nobody has checked this yet") and "read error" not in out, f"a folder named like a concept hid a concept: {out}"
    quiet = report(tmp_path, "quiet", env=env)
    assert quiet.rc != 0 and "concepts with no stamp: 1" in quiet.out, f"a folder named like a concept made a busy week quiet: {quiet.out}"


def test_a_read_that_stops_early_is_not_a_smaller_bundle(tmp_path):
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(kk / "t" / "zz.md", "---\ntype: GlossaryTerm\ntitle: A\n---\n")
    for form in ("health", "quiet"):
        result = report(tmp_path, form, env=stopping_awk(tmp_path, "KR_LIST"))
        assert result.rc == 2 and "could not be read to its end" in result.out and "of 0" not in result.out and "Quiet" not in result.out, (
            f"{form}: a read that stopped early was reported as a bundle (exit {result.rc}): {result.out}"
        )


def test_a_source_renamed_after_the_librarian_asked_has_moved(tmp_path):
    """Both names were cited, so git paired the rename and the old name took the edit before the question as its last commit."""
    git = Git(tmp_path)
    git.init()
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    stamp = 'generated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n'
    write(tmp_path / "src" / "old.md", "one\ntwo\nthree\n")
    write(kk / "x" / "ren.md", f"---\ntype: Service\ntitle: Ren\nresource: src/old.md\n{stamp}---\n")
    write(kk / "x" / "new.md", f"---\ntype: Service\ntitle: New\nresource: src/new.md\n{stamp}---\n")
    git("add", "-A")
    git("commit", "-q", "-m", "one")
    append(tmp_path / "src" / "old.md", "four\n")
    git("commit", "-q", "-am", "old edited")
    append(kk / "x" / "ren.md", "\n## Open questions\n\n- 2026-01-05, process:ktl-librarian: src/old.md changed, is the claim right?\n")
    git("commit", "-q", "-am", "the librarian asks")
    git("mv", "src/old.md", "src/new.md")
    git("commit", "-q", "-m", "renamed after the question")
    out = report(tmp_path, "worklist").out
    assert has_line(out, "- x/ren.md: src/old.md (gone)") and has_line(
        out, "Sources that moved, where your own question has waited for a person since: none"
    ), f"a source renamed after the question was filed under it: {out}"


def test_a_name_git_quotes_and_a_source_outside_the_work_tree_are_compared(tmp_path):
    """Git quotes a name with a double quote and ends one with a space with a tab in a diff, and the batched reads once matched neither."""
    git = Git(tmp_path)
    git.init()
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    stamp = 'generated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n'
    write(tmp_path / "docs" / "a.md", "a\n")
    write(tmp_path / "docs" / 'q"uote.md', "q\n")
    write(kk / "x" / "sp ace.md", f"---\ntype: Service\ntitle: Space\nresource: docs/a.md\n{stamp}---\n")
    write(kk / "x" / "quote.md", f"---\ntype: Service\ntitle: Quote\nresource: 'docs/q\"uote.md'\n{stamp}---\n")
    write(kk / "x" / "up.md", f"---\ntype: Service\ntitle: Up\nresource: ../outside.md\n{stamp}---\n")
    git("add", "-A")
    git("commit", "-q", "-m", "one")
    append(tmp_path / "docs" / "a.md", "b\n")
    append(tmp_path / "docs" / 'q"uote.md', "r\n")
    git("commit", "-q", "-am", "both sources change")
    out = report(tmp_path, "worklist").out
    assert matches(out, r"^- x/sp ace\.md: docs/a\.md \(\d{4}-\d\d-\d\d\)$"), f"a concept whose name holds a space was not compared: {out}"
    assert matches(out, r'^- x/quote\.md: docs/q"uote\.md \(\d{4}-\d\d-\d\d\)$'), f"a source git quotes was not compared: {out}"
    assert has_line(out, "- x/up.md: ../outside.md (gone)"), f"a source outside the work tree that is gone went unnamed: {out}"


# ---- the two lines the curator once worked out by hand ------------------------


def test_the_whole_report_names_each_confirmation_no_signed_commit_stands_behind(tmp_path):
    git = Git(tmp_path)
    git.init()
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")

    def confirmed(name, at):
        return f'---\ntype: Service\ntitle: {name}\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\nverified:\n  - by: human:ada\n    at: "{at}"\n---\n'

    write(kk / "x" / "unsigned.md", confirmed("Unsigned", "2026-01-02T00:00:00Z"))
    write(kk / "x" / "auto.md", '---\ntype: Service\ntitle: Auto\nverified:\n  - by: process:ktl-librarian\n    at: "2026-01-02T00:00:00Z"\n---\n')
    git("add", "-A")
    git("commit", "-q", "-m", "unsigned")
    # A signed commit, as git writes one: a gpgsig header before the message.
    write(kk / "x" / "signed.md", confirmed("Signed", "2026-01-03T00:00:00Z"))
    git("add", "-A")
    tree = git("write-tree")
    parent = git("rev-parse", "HEAD")
    obj = f"tree {tree}\nparent {parent}\nauthor a <a@example.invalid> 1767225600 +0000\ncommitter a <a@example.invalid> 1767225600 +0000\ngpgsig -----BEGIN SSH SIGNATURE-----\n U1NIU0lH\n -----END SSH SIGNATURE-----\n\nsigned\n"
    sha = run(["git", "-C", tmp_path, "hash-object", "-t", "commit", "-w", "--stdin"], stdin=obj).out
    git("update-ref", "HEAD", sha)
    # A confirmation not yet committed has no commit to ask about.
    write(kk / "x" / "new.md", confirmed("New", "2026-01-04T00:00:00Z"))
    out = report(tmp_path).out
    assert matches(out, r"^Confirmed by a person: .* · Not tied to a signed commit: 1$"), f"the health line did not end with the count: {out}"
    assert has_line(out, "Not tied to a signed commit: 1") and has_line(out, "- x/unsigned.md") and "- x/signed.md" not in out and "- x/new.md" not in out, out
    assert not matches(report(tmp_path, "health").out, "signed"), "the health form gained a field the curator alone reads"


def test_a_confirmation_only_a_merge_commit_added_is_listed_with_a_note(tmp_path):
    """The walk reads no line a merge commit added of its own, so git holds no commit that added such a confirmation: it counts, and its line says so."""
    git = Git(tmp_path)
    git.init()
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    plain = '---\ntype: Service\ntitle: Merged\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n'
    write(kk / "x" / "merged.md", plain + "---\n")
    write(tmp_path / "a.txt", "a\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    git("checkout", "-q", "-b", "side")
    write(tmp_path / "b.txt", "b\n")
    git("add", "-A")
    git("commit", "-q", "-m", "side")
    git("checkout", "-q", "main")
    write(tmp_path / "a.txt", "a, again\n")
    git("commit", "-q", "-am", "main")
    git("merge", "-q", "--no-ff", "--no-commit", "side")
    write(kk / "x" / "merged.md", plain + 'verified:\n  - by: human:ada\n    at: "2026-01-05T00:00:00Z"\n---\n')
    git("add", "-A")
    git("commit", "-q", "-m", "merge, with a confirmation written in it")
    out = report(tmp_path).out
    assert has_line(out, "Not tied to a signed commit: 1") and has_line(out, "- x/merged.md (git holds no commit that added this confirmation)"), out


def test_without_git_the_whole_report_says_it_did_not_check_signatures(moved, tmp_path):
    bare = tmp_path / "bare"
    shutil.copytree(moved / ".lokf", bare / ".lokf")
    out = report(bare).out
    assert has_line(out, "Not tied to a signed commit: not checked here, since git holds no full history of this bundle (no git, a shallow clone, or a gitignored .lokf/)"), out
    assert "· Not tied to a signed commit" not in out, out


def test_vocabulary_fit_counts_a_type_and_a_status_outside_core_and_the_domain_vocabulary(tmp_path):
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(tmp_path / ".lokf" / "justfile", 'bundle := "knowledge"\nschema := "schema/acme.yaml"\n')
    write(
        tmp_path / ".lokf" / "schema" / "acme.yaml",
        "id: https://acme.example/schema\nimports:\n  - linkml:types\n  - lokf\n  - ./more\nclasses:\n  Widget:\n    is_a: Concept\n    slot_usage:\n      part:\n        is_a: Gadget\n  Gizmo:\n    is_a: Widget\n  Note:\n    description: no parent\n",
    )
    write(tmp_path / ".lokf" / "schema" / "more.yaml", "id: https://acme.example/more\nclasses:\n  Runbook:\n    is_a: Playbook\n")
    for name, kind, status in [
        ("a", "Service", ""),
        ("b", "Widget", ""),
        ("c", "Gizmo", "status: stable\n"),
        ("d", "Runbook", ""),
        ("e", "Attested Computation", ""),
        ("f", "Note", ""),
        ("g", "Service", "status: wip\n"),
        ("h", "Gadget", "status: deprecated\n"),
    ]:
        write(kk / "x" / f"{name}.md", f"---\ntype: {kind}\ntitle: {name}\n{status}---\n")
    out = report(tmp_path).out
    assert has_line(out, "Vocabulary fit: 2 concepts do not fit the known vocabulary (Note, status wip)"), out
    assert has_line(out, "- x/f.md: type Note") and has_line(out, "- x/g.md: status wip") and "x/h.md:" not in out, out
    write(tmp_path / ".lokf" / "justfile", 'bundle := "knowledge"\nschema := ""\n')
    out = report(tmp_path).out
    assert has_line(out, "Vocabulary fit: 5 concepts do not fit the known vocabulary (Widget, Gizmo, Runbook, Note, status wip)"), out
