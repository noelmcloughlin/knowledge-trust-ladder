"""knowledge-apply.sh is the pen, the librarian's only way to write the bundle, so it has to earn the refusals the skill promises.

This was check 19 in scripts/validate-repository.sh:

- nothing is written unless every operation passes;
- a human: actor anywhere, a rewrite of text a person wrote and the deletion
  of a concept a person confirmed are refused;
- a person's own verified event survives a patch;
- a person's record is the same after a patch as before, whatever the
  operations were;
- a frontmatter value the operation did not name keeps the text the file
  held, where YAML would read it as a number, a boolean or a time;
- a reader's question reaches the ledger, and a hand-off line its file, with
  no character a reader cannot see;
- the index bullets and the log heading are kept in step;
- the lokf:related block survives a rewrite;
- a handled feedback entry leaves feedback.md for the ledger, with the
  reader's question in a code span;
- a dry run writes nothing;
- a quoted timestamp keeps its double quotes;
- reindex re-derives a bullet without touching the concept;
- resolve withdraws the librarian's own question and never a person's note;
- a root index shaped by hand keeps its shape;
- the hand-off reaches the file --handoff names as plain single lines, and
  never the bundle.

That `--format` prints the block ktl-librarian's references/patch.md shows
stays in the contract script: it is a fact about this repository's own pages.
"""

from __future__ import annotations

import hashlib
import re

import pytest

from conftest import SCRIPTS, bash, esc, has_line, matches, read, today_utc, tree_digest, write

APPLY = SCRIPTS / "knowledge-apply.sh"


def lines(*parts):
    """printf '%s\\n' a b c: each part on its own line."""
    return "\n".join(parts) + "\n"


def md5(path):
    return hashlib.md5(path.read_bytes()).hexdigest()


def apply(root, *args):
    return bash(APPLY, "--root", root, *args)


def patch_file(root):
    return root / ".lokf" / "patch.yaml"


def refuses(root, text, what, expected):
    """The pen refuses the patch in place with the expected finding, and writes nothing."""
    write(patch_file(root), text)
    before = tree_digest(root)
    result = apply(root, patch_file(root))
    assert result.rc == 1 and expected in result.out and tree_digest(root) == before, (
        f"knowledge-apply.sh did not refuse {what} cleanly (exit {result.rc}): {result.out}"
    )


def applies(root, text):
    write(patch_file(root), text)
    result = apply(root, patch_file(root))
    assert result, f"knowledge-apply.sh refused a valid patch: {result.out}"
    return result


@pytest.fixture
def ka(tmp_path):
    """A bundle with a draft, a concept a person confirmed and one a person wrote, their index bullets, a log and one reader entry."""
    kb = tmp_path / ".lokf" / "knowledge"
    write(
        kb / "index.md",
        lines(
            "---",
            "base_iri: https://acme.example/knowledge/",
            "---",
            "",
            "# Acme",
            "",
            "# Playbooks",
            "",
            "* [Draft](playbooks/draft.md) - a draft.",
            "* [Confirmed](playbooks/confirmed.md) - confirmed.",
            "* [Authored](playbooks/authored.md) - authored.",
        ),
    )
    write(
        kb / "playbooks" / "index.md",
        lines(
            "# Playbooks",
            "",
            "* [Draft](draft.md) - a draft.",
            "* [Confirmed](confirmed.md) - confirmed.",
            "* [Authored](authored.md) - authored.",
        ),
    )
    write(
        kb / "playbooks" / "draft.md",
        lines(
            "---",
            "type: Playbook",
            "id: https://acme.example/knowledge/playbooks/draft",
            "title: Draft",
            "description: a draft.",
            "generated:",
            "  by: process:ktl-librarian",
            '  at: "2026-01-01T00:00:00Z"',
            "status: draft",
            "---",
            "",
            "# Overview",
            "",
            "The old text.",
        ),
    )
    write(
        kb / "playbooks" / "confirmed.md",
        lines(
            "---",
            "type: Playbook",
            "id: https://acme.example/knowledge/playbooks/confirmed",
            "title: Confirmed",
            "description: confirmed.",
            "generated:",
            "  by: process:ktl-librarian",
            '  at: "2026-01-01T00:00:00Z"',
            "verified:",
            "  - by: human:ada",
            '    at: "2026-02-02T00:00:00Z"',
            "---",
            "",
            "# Overview",
            "",
            "Confirmed text.",
            "",
            "<!-- lokf:related -->",
            "#how-to",
            "<!-- /lokf:related -->",
        ),
    )
    write(
        kb / "playbooks" / "authored.md",
        lines(
            "---",
            "type: Playbook",
            "id: https://acme.example/knowledge/playbooks/authored",
            "title: Authored",
            "description: authored.",
            "generated:",
            "  by: human:ada",
            '  at: "2026-01-01T00:00:00Z"',
            "verified:",
            "  - by: human:ada",
            '    at: "2026-01-01T00:00:00Z"',
            "---",
            "",
            "# Overview",
            "",
            "Written by a person.",
        ),
    )
    write(kb / "log.md", lines("# Change Log", "", "## 2020-01-01", "", "* **Old**: an old line."))
    write(
        tmp_path / ".lokf" / "feedback.md",
        lines(
            "# Reader feedback for the librarian",
            "",
            "Newest first.",
            "",
            "## 2026-03-03",
            "",
            '- **Miss** - Q: "where?" Answered from here. - docent',
        ),
    )
    return tmp_path


FIRST_PATCH = r"""ops:
  - op: create
    path: playbooks/new.md
    frontmatter: {type: Playbook, title: New, description: brand new., resource: README.md}
    body: "# Overview\n\nBrand new.\n"
  - op: patch
    path: playbooks/draft.md
    edits:
      - replace: {target: "The old text.", content: "The new text."}
    set: {description: a better draft.}
    log: "the text moved on"
    from_feedback: '- **Miss** - Q: "where?" Answered from here. - docent'
    asked: "where is `it`?"
  - op: patch
    path: playbooks/confirmed.md
    edits:
      - append: {content: "A new paragraph."}
    log: "**Changed**: one more paragraph."
  - op: question
    path: playbooks/authored.md
    text: is this still right?
"""


@pytest.fixture
def applied(ka):
    """The bundle after the first valid patch: a create, two patches and a question."""
    write(patch_file(ka), FIRST_PATCH)
    result = apply(ka, patch_file(ka))
    assert result and not patch_file(ka).exists(), f"knowledge-apply.sh failed on a valid patch: {result.out}"
    return ka


def kb_of(root):
    return root / ".lokf" / "knowledge"


def test_create_mints_the_id_stamps_generated_starts_as_a_draft_and_adds_both_bullets(applied):
    kb = kb_of(applied)
    new = read(kb / "playbooks" / "new.md")
    assert (
        has_line(new, "status: draft")
        and has_line(new, "id: https://acme.example/knowledge/playbooks/new")
        and matches(new, rf"^  at: ['\"]{today_utc()}T[0-9:]+Z['\"]$")
        and has_line(new, "  by: process:ktl-librarian")
        and "* [New](playbooks/new.md) - brand new." in read(kb / "index.md")
        and "* [New](new.md) - brand new." in read(kb / "playbooks" / "index.md")
    ), f"create did not produce the expected concept and bullets: {new}"


def test_patch_replaces_the_target_restamps_generated_and_rewrites_both_bullets(applied):
    kb = kb_of(applied)
    draft = read(kb / "playbooks" / "draft.md")
    assert (
        "The new text." in draft
        and "The old text." not in draft
        and "2026-01-01T00:00:00Z" not in draft
        and "* [Draft](playbooks/draft.md) - a better draft." in read(kb / "index.md")
        and "* [Draft](draft.md) - a better draft." in read(kb / "playbooks" / "index.md")
    ), f"patch did not edit the draft as expected: {draft}"


def test_patch_on_a_confirmed_concept_keeps_the_persons_event_and_says_so_in_the_log(applied):
    kb = kb_of(applied)
    confirmed = read(kb / "playbooks" / "confirmed.md")
    assert (
        "A new paragraph." in confirmed
        and matches(confirmed, r"^ *- by: human:ada$")
        and matches(confirmed, r'^ +at: "2026-02-02T00:00:00Z"$')
        and "Edited since a person confirmed it" in read(kb / "log.md")
    ), f"patch on a confirmed concept lost the person's event or the log note: {confirmed}"


def test_question_adds_the_curator_shaped_bullet_and_touches_neither_text_nor_generated(applied):
    authored = read(kb_of(applied) / "playbooks" / "authored.md")
    assert (
        has_line(authored, "status: draft")
        and has_line(authored, f"- {today_utc()}, process:ktl-librarian: is this still right?")
        and has_line(authored, "  by: human:ada")
        and "Written by a person." in authored
    ), f"question did not leave the authored concept as expected: {authored}"


def test_the_log_gains_todays_heading_and_the_handled_feedback_entry_is_gone(applied):
    log = read(kb_of(applied) / "log.md")
    feedback = read(applied / ".lokf" / "feedback.md")
    first_heading = next(line for line in log.split("\n") if line.startswith("## "))
    assert (
        first_heading == f"## {today_utc()}"
        and has_line(log, "## 2020-01-01")
        and matches(log, r"^\* \*\*From reader feedback\*\*: the text moved on")
        and matches(log, r"^\* \*\*Added\*\*: New")
        and "where?" not in feedback
        and not has_line(feedback, "## 2026-03-03")
    ), f"the log or the feedback file is not as expected: {log} // {feedback}"


def test_a_handled_entry_reaches_the_ledger_with_its_question_in_a_code_span(applied):
    """The reader's words stay out of log.md, which the curator opens."""
    questions = read(applied / ".lokf" / "questions.md")
    assert (
        questions.split("\n")[0] == "# Questions readers asked"
        and has_line(questions, f"- {today_utc()} Miss playbooks/draft.md: `where is 'it'?`")
        and "where is" not in read(kb_of(applied) / "log.md")
    ), f"the ledger is not as expected: {questions}"


def test_rewrite_carries_the_related_block_over_and_reuses_todays_heading(applied):
    applies(
        applied,
        'ops:\n  - op: rewrite\n    path: playbooks/confirmed.md\n    body: "# Overview'
        + r"\n\nRewritten from the source.\n"
        + '"\n    log: "rewritten from the source"\n',
    )
    confirmed = read(kb_of(applied) / "playbooks" / "confirmed.md")
    log = read(kb_of(applied) / "log.md")
    assert (
        "Rewritten from the source." in confirmed
        and "<!-- lokf:related -->" in confirmed
        and log.split("\n").count(f"## {today_utc()}") == 1
    ), f"rewrite lost the lokf:related block or doubled today's heading: {confirmed}"


def test_delete_removes_a_draft_both_its_bullets_and_logs_why(applied):
    kb = kb_of(applied)
    applies(
        applied,
        'ops:\n  - op: delete\n    path: playbooks/draft.md\n    log: "**Removal**: Draft; its source is gone."\n',
    )
    assert (
        not (kb / "playbooks" / "draft.md").exists()
        and "draft.md" not in read(kb / "index.md")
        and "draft.md" not in read(kb / "playbooks" / "index.md")
        and matches(read(kb / "log.md"), r"^\* \*\*Removal\*\*: Draft")
    ), "delete did not remove the draft and its bullets"


REFUSED = [
    (
        "a human: actor anywhere in the file",
        lines("by: human:ada", "ops:", "  - {op: recheck, path: playbooks/new.md}"),
        "names a human: actor",
    ),
    (
        "deleting a concept a person confirmed",
        lines("ops:", "  - {op: delete, path: playbooks/confirmed.md, log: gone}"),
        "a person confirmed this concept",
    ),
    (
        "patching text a person wrote",
        lines("ops:", "  - {op: patch, path: playbooks/authored.md, edits: [{append: {content: x}}], log: x}"),
        "a person wrote this text",
    ),
    (
        "setting status",
        lines("ops:", "  - {op: patch, path: playbooks/new.md, set: {status: stable}, log: x}"),
        "set may not touch status",
    ),
    (
        "setting a capitalised Verified",
        lines("ops:", "  - {op: patch, path: playbooks/new.md, set: {Verified: x}, log: x}"),
        "set may not touch Verified",
    ),
    (
        "setting a top-level by",
        lines("ops:", '  - {op: patch, path: playbooks/new.md, set: {by: "human:ada"}, log: x}'),
        "set may not touch by",
    ),
]


@pytest.mark.parametrize(("what", "text", "expected"), REFUSED, ids=[w for w, _, _ in REFUSED])
def test_refuses(applied, what, text, expected):
    refuses(applied, text, what, expected)


def test_a_refused_file_applies_none_of_its_operations(applied):
    refuses(
        applied,
        lines(
            "ops:",
            "  - {op: create, path: playbooks/other.md, frontmatter: {type: Playbook, title: Other, description: d.}, body: b}",
            '  - {op: patch, path: playbooks/new.md, edits: [{replace: {target: "not there", content: x}}], log: x}',
        ),
        "a missing target, with a valid create beside it",
        "must occur exactly once",
    )
    assert not (kb_of(applied) / "playbooks" / "other.md").exists(), "a refused file still created playbooks/other.md"


def test_a_dry_run_reports_writes_nothing_and_keeps_the_patch_file(applied):
    write(
        patch_file(applied),
        lines(
            "ops:",
            "  - {op: create, path: playbooks/dry.md, frontmatter: {type: Playbook, title: Dry, description: d.}, body: b}",
        ),
    )
    result = apply(applied, "--dry-run", patch_file(applied))
    assert (
        result
        and "would write" in result.out
        and not (kb_of(applied) / "playbooks" / "dry.md").exists()
        and patch_file(applied).exists()
    ), f"the dry run wrote something or lost the patch file: {result.out}"


# The hand-off: lines for the reviewer, which never reach the bundle. The pen
# accepts each only as one line of printable text with no backtick. It writes
# them to the file --handoff names, empties that file when a patch has none,
# and refuses a hand-off that is not a short list of short lines.


def test_the_handoff_reaches_its_file_as_plain_single_lines_and_stays_out_of_the_bundle(applied):
    khand = applied / "handoff.txt"
    write(
        patch_file(applied),
        "ops:\n  - {op: recheck, path: playbooks/new.md}\nhandoff:\n"
        '  - "two concepts came back for the same `date`;' + esc(0x200B) + " the rule" + "\\t" + 'needs a look"\n'
        '  - "a source did not answer"\n',
    )
    write(khand, "planted by the agent\n")
    result = apply(applied, "--handoff", khand, patch_file(applied))
    kept_out = not any("did not answer" in read(p) for p in kb_of(applied).rglob("*.md"))
    assert (
        result
        and read(khand).rstrip("\n")
        == "two concepts came back for the same 'date'; the rule needs a look\na source did not answer"
        and has_line(result.out, "  a source did not answer")
        and kept_out
    ), f"the hand-off was not written as expected: {result.out} // {read(khand)}"


def test_a_patch_with_no_handoff_empties_the_file(applied):
    khand = applied / "handoff.txt"
    write(khand, "planted by the agent\n")
    write(patch_file(applied), lines("ops:", "  - {op: recheck, path: playbooks/new.md}"))
    result = apply(applied, "--handoff", khand, patch_file(applied))
    assert result and khand.read_bytes() == b"", (
        f"a patch with no hand-off left the --handoff file holding: {read(khand)}"
    )


HANDOFF_REFUSED = [
    (
        "a hand-off of more than ten lines",
        "ops:\n  - {op: recheck, path: playbooks/new.md}\nhandoff:\n"
        + "".join(f'  - "line {i}"\n' for i in range(1, 12)),
        "a reviewer gets at most 10",
    ),
    (
        "a hand-off line longer than 300 characters",
        lines("ops:", "  - {op: recheck, path: playbooks/new.md}", 'handoff: ["' + "x" * 301 + '"]'),
        "handoff line 1 is 301 characters",
    ),
    (
        "a hand-off that is not a list",
        lines("ops:", "  - {op: recheck, path: playbooks/new.md}", 'handoff: "one line, not a list"'),
        "handoff is a list of lines",
    ),
    (
        "a hand-off line of invisible characters alone",
        lines("ops:", "  - {op: recheck, path: playbooks/new.md}", 'handoff: ["' + esc(0x200B) + esc(0x202E) + '"]'),
        "handoff line 1 holds no printable text",
    ),
]


@pytest.mark.parametrize(("what", "text", "expected"), HANDOFF_REFUSED, ids=[w for w, _, _ in HANDOFF_REFUSED])
def test_refuses_a_bad_handoff(applied, what, text, expected):
    refuses(applied, text, what, expected)


def test_reindex_restores_a_drifted_bullet_and_touches_neither_the_concept_nor_the_log(applied):
    kb = kb_of(applied)
    write(
        kb / "index.md",
        read(kb / "index.md").replace("* [New](playbooks/new.md) - brand new.", "* [New](playbooks/new.md) - stale."),
    )
    before = md5(kb / "playbooks" / "new.md")
    applies(applied, lines("ops:", "  - {op: reindex, path: playbooks/new.md}"))
    assert (
        "* [New](playbooks/new.md) - brand new." in read(kb / "index.md")
        and md5(kb / "playbooks" / "new.md") == before
        and "brand new" not in read(kb / "log.md")
    ), "reindex did not restore the bullet, or touched the concept or the log"


def test_resolve_withdraws_the_librarians_own_question_and_leaves_the_rest_alone(applied):
    """The heading goes with its last question; the person's text, their generated record and the status stay."""
    kb = kb_of(applied)
    applies(
        applied,
        lines(
            "ops:",
            '  - {op: resolve, path: playbooks/authored.md, target: "still right", log: "the source settles it"}',
        ),
    )
    authored = read(kb / "playbooks" / "authored.md")
    assert (
        "Open questions" not in authored
        and "still right" not in authored
        and has_line(authored, "status: draft")
        and has_line(authored, "  by: human:ada")
        and "Written by a person." in authored
        and matches(read(kb / "log.md"), r"^\* \*\*Resolved\*\*: the source settles it")
    ), f"resolve did not withdraw the question cleanly: {authored}"


@pytest.fixture
def noted(applied):
    """The bundle after a person left a note on the new concept."""
    path = kb_of(applied) / "playbooks" / "new.md"
    write(path, read(path) + "\n## Open questions\n\n- 2026-03-03, human:ada: send this back\n")
    return applied


def test_resolve_never_clears_a_persons_note(noted):
    refuses(
        noted,
        lines("ops:", '  - {op: resolve, path: playbooks/new.md, target: "send this back", log: x}'),
        "resolving a note a person left",
        "is not one process:ktl-librarian asked",
    )


def test_delete_never_removes_a_concept_a_person_left_a_note_on(noted):
    refuses(
        noted,
        lines("ops:", "  - {op: delete, path: playbooks/new.md, log: gone}"),
        "deleting a concept a person left a note on",
        "a person left a note on this concept",
    )


@pytest.fixture
def sent_back(applied):
    """A concept the curator sent back as process:ktl-curator, with no authenticated login."""
    kb = kb_of(applied)
    write(
        kb / "playbooks" / "sentback.md",
        lines(
            "---",
            "type: Playbook",
            "id: https://acme.example/knowledge/playbooks/sentback",
            "title: Sentback",
            "description: sent back.",
            "generated:",
            "  by: process:ktl-librarian",
            '  at: "2026-01-01T00:00:00Z"',
            "status: draft",
            "---",
            "",
            "# Overview",
            "",
            "Body.",
            "",
            "## Open questions",
            "",
            "- 2026-03-03, process:ktl-curator: re-derive this from the source",
        ),
    )
    write(
        kb / "playbooks" / "index.md", read(kb / "playbooks" / "index.md") + "* [Sentback](sentback.md) - sent back.\n"
    )
    return applied


def test_a_curators_send_back_is_not_the_pens_to_withdraw(sent_back):
    refuses(
        sent_back,
        lines("ops:", '  - {op: resolve, path: playbooks/sentback.md, target: "re-derive this", log: x}'),
        "withdrawing a curator's send-back",
        "that is a curator's send-back",
    )


def test_a_concept_the_curator_sent_back_is_not_the_pens_to_delete(sent_back):
    refuses(
        sent_back,
        lines("ops:", "  - {op: delete, path: playbooks/sentback.md, log: gone}"),
        "deleting a concept the curator sent back",
        "the curator left a send-back on this concept",
    )


def test_an_edit_may_not_glue_a_protected_heading_onto_the_line_before(sent_back):
    refuses(
        sent_back,
        lines(
            "ops:",
            '  - {op: patch, path: playbooks/sentback.md, edits: [{replace: {target: "Body.'
            + r"\n\n"
            + '", content: "Body. "}}], log: x}',
        ),
        "an edit that would glue the Open questions heading onto the text before it",
        "would merge the ## Open questions heading",
    )


def test_the_librarian_re_derives_a_sent_back_concept_and_the_send_back_stays(sent_back):
    applies(
        sent_back,
        lines(
            "ops:",
            '  - {op: patch, path: playbooks/sentback.md, set: {description: "re-derived."}, log: re-derived from the source}',
        ),
    )
    assert "process:ktl-curator" in read(kb_of(sent_back) / "playbooks" / "sentback.md"), (
        "re-deriving a sent-back concept lost the curator's note"
    )


def test_an_empty_revision_round_trips_as_empty_not_null(applied):
    """The gate would otherwise read null as a changed confirmation."""
    kb = kb_of(applied)
    write(
        kb / "playbooks" / "nullrev.md",
        lines(
            "---",
            "type: Playbook",
            "id: https://acme.example/knowledge/playbooks/nullrev",
            "title: Nullrev",
            "description: nr.",
            "generated:",
            "  by: process:ktl-librarian",
            '  at: "2026-01-01T00:00:00Z"',
            "verified:",
            "  - by: human:ada",
            '    at: "2026-02-02T00:00:00Z"',
            "    revision:",
            "---",
            "",
            "# Overview",
            "",
            "Body.",
        ),
    )
    write(kb / "playbooks" / "index.md", read(kb / "playbooks" / "index.md") + "* [Nullrev](nullrev.md) - nr.\n")
    applies(applied, lines("ops:", "  - {op: recheck, path: playbooks/nullrev.md}"))
    nullrev = read(kb / "playbooks" / "nullrev.md")
    assert "revision:" in nullrev and "revision: null" not in nullrev, (
        f"the pen turned an empty revision into null: {nullrev}"
    )


def test_asked_goes_with_from_feedback(applied):
    refuses(
        applied,
        lines(
            "ops:", '  - {op: patch, path: playbooks/new.md, edits: [{append: {content: x}}], log: x, asked: "why?"}'
        ),
        "a reader's question with no feedback entry behind it",
        "asked goes with from_feedback",
    )


def test_a_second_handled_entry_joins_the_ledger_under_the_first(applied):
    write(
        applied / ".lokf" / "feedback.md",
        lines(
            "# Reader feedback for the librarian",
            "",
            "## 2026-03-04",
            "",
            "- **Disagreement** - it says one thing. - docent",
        ),
    )
    applies(
        applied,
        lines(
            "ops:",
            "  - {op: patch, path: playbooks/new.md, edits: [{append: {content: fixed}}], log: fixed, from_feedback: '- **Disagreement** - it says one thing. - docent'}",
        ),
    )
    questions = read(applied / ".lokf" / "questions.md")
    assert (
        has_line(questions, f"- {today_utc()} Disagreement playbooks/new.md")
        and questions.count("\n- ") + questions.startswith("- ") == 2
        and questions.split("\n").count("# Questions readers asked") == 1
    ), f"the ledger did not grow as expected: {questions}"


def test_a_disagreement_that_names_its_concept_is_handled_and_filed(applied):
    write(
        applied / ".lokf" / "feedback.md",
        lines(
            "# Reader feedback for the librarian",
            "",
            "## 2026-03-05",
            "",
            "- **Disagreement** (on `playbooks/new.md`) - it says a third thing. - docent",
        ),
    )
    applies(
        applied,
        lines(
            "ops:",
            "  - {op: patch, path: playbooks/new.md, edits: [{append: {content: fixed again}}], log: fixed, from_feedback: '- **Disagreement** (on `playbooks/new.md`) - it says a third thing. - docent'}",
        ),
    )
    questions = read(applied / ".lokf" / "questions.md")
    assert sum(1 for line in questions.split("\n") if line.startswith("- ")) == 2 and "- **" not in read(
        applied / ".lokf" / "feedback.md"
    ), f"the pen did not handle a Disagreement that names its concept: {questions}"


# A person's record is the same after a patch as before, whatever the
# operations were. The pen compares each concept it is about to write with the
# file it read. So these are refused, though each operation is one it allows.
RECORD_REFUSED = [
    (
        "a rewrite whose own open questions would replace a person's note",
        'ops:\n  - op: rewrite\n    path: playbooks/new.md\n    body: "# Overview'
        + r"\n\nRewritten.\n\n## Open questions\n\n- 2026-03-04, process:ktl-librarian: mine now\n"
        + '"\n    log: rewritten\n',
        "playbooks/new.md: this patch would remove a note a person left (human:ada, 2026-03-03)",
    ),
    (
        "a person's note spelt with an escaped line break in a new concept",
        'ops:\n  - op: create\n    path: playbooks/planted.md\n    frontmatter: {type: Playbook, title: Planted, description: planted.}\n    body: "# Overview'
        + r"\n\nText.\n\n## Open questions\n\n- 2026-03-04, human:ada: looks right to me\n"
        + '"\n',
        "playbooks/planted.md: this patch would add a note in a person's name (human:ada, 2026-03-04)",
    ),
    (
        "a person's note spelt with an escaped line break in an appended paragraph",
        lines(
            "ops:",
            '  - {op: patch, path: playbooks/confirmed.md, edits: [{append: {content: "## Open questions'
            + r"\n\n- 2026-03-04, human:ada: I checked this\n"
            + '"}}], log: x}',
        ),
        "playbooks/confirmed.md: this patch would add a note in a person's name (human:ada, 2026-03-04)",
    ),
    (
        "a delete behind a second open-questions heading placed above a person's note",
        lines(
            "ops:",
            '  - {op: patch, path: playbooks/new.md, edits: [{append: {content: "## Open questions'
            + r"\n\nnothing here"
            + '"}}], log: x}',
            "  - {op: delete, path: playbooks/new.md, log: gone}",
        ),
        "playbooks/new.md: this patch would remove a note a person left (human:ada, 2026-03-03)",
    ),
]


@pytest.mark.parametrize(("what", "text", "expected"), RECORD_REFUSED, ids=[w for w, _, _ in RECORD_REFUSED])
def test_a_persons_record_is_the_same_after_a_patch_as_before(noted, what, text, expected):
    refuses(noted, text, what, expected)


def test_a_rewrite_with_no_open_questions_of_its_own_carries_a_persons_note_over(noted):
    applies(
        noted,
        lines(
            "ops:",
            '  - {op: rewrite, path: playbooks/new.md, body: "# Overview'
            + r"\n\nRewritten from the source.\n"
            + '", log: rewritten}',
        ),
    )
    new = read(kb_of(noted) / "playbooks" / "new.md")
    assert "Rewritten from the source." in new and has_line(new, "- 2026-03-03, human:ada: send this back"), (
        f"a rewrite lost a person's note, or was refused: {new}"
    )


@pytest.fixture
def with_kept(applied):
    """A concept holding values YAML reads as numbers, a boolean and times, and a person's event with an unquoted time and an all-digit revision."""
    kb = kb_of(applied)
    write(
        kb / "playbooks" / "kept.md",
        lines(
            "---",
            "type: Playbook",
            "id: https://acme.example/knowledge/playbooks/kept",
            "title: Kept",
            "description: kept.",
            "version: 1.10",
            "window: 12:30:00",
            "flag: yes",
            "generated:",
            "  by: process:ktl-librarian",
            '  at: "2026-01-01T00:00:00Z"',
            "verified:",
            "  - by: human:ada",
            "    at: 2026-02-02T10:00:00Z",
            "    revision: 0123456",
            "---",
            "",
            "# Overview",
            "",
            "Text.",
        ),
    )
    return applied


@pytest.mark.parametrize(
    "want",
    [
        "version: 1.10",
        "window: 12:30:00",
        "flag: yes",
        "build: 1.20",
        "- by: human:ada",
        "  at: 2026-02-02T10:00:00Z",
        "  revision: 0123456",
        '  revision: "1234567"',
    ],
)
def test_a_value_the_operation_did_not_name_goes_back_as_the_file_held_it(with_kept, want):
    """Written back from what YAML read, 1.10 would read 1.1, 12:30:00 would read 45000 and a person's time would change shape, which the gate reads as a changed confirmation."""
    applies(
        with_kept,
        lines(
            "ops:",
            "  - {op: patch, path: playbooks/kept.md, edits: [{append: {content: more}}], set: {build: 1.20}, revision: 1234567, log: x}",
        ),
    )
    kept = read(kb_of(with_kept) / "playbooks" / "kept.md")
    assert has_line(kept, want), f"the pen did not keep '{want}': {kept}"


def test_a_readers_question_and_a_handoff_line_lose_every_character_a_reader_cannot_see(with_kept):
    """By Unicode's own categories: a zero-width space, a right-to-left override, an Arabic letter mark, a soft hyphen and a tag character."""
    khand = with_kept / "handoff.txt"
    write(
        with_kept / ".lokf" / "feedback.md",
        lines("# Reader feedback for the librarian", "", "## 2026-03-05", "", '- **Miss** - Q: "hidden?" - docent'),
    )
    write(
        patch_file(with_kept),
        'ops:\n  - op: patch\n    path: playbooks/kept.md\n    edits:\n      - append: {content: "and more"}\n    log: fixed\n'
        "    from_feedback: '- **Miss** - Q: \"hidden?\" - docent'\n"
        '    asked: "is'
        + esc(0x200B)
        + " it"
        + esc(0x202E)
        + " hidden"
        + esc(0x061C)
        + " from"
        + esc(0x00AD)
        + " a"
        + esc(0xE0041)
        + " reader"
        + esc(0xFEFF)
        + '?"\n'
        'handoff:\n  - "a'
        + esc(0x061C)
        + " line"
        + esc(0x00AD)
        + " with"
        + esc(0xE0041)
        + " more"
        + esc(0xFFF9)
        + " than"
        + esc(0x180E)
        + " a"
        + esc(0x200B)
        + ' list"\n',
    )
    result = apply(with_kept, "--handoff", khand, patch_file(with_kept))
    assert (
        result
        and has_line(
            read(with_kept / ".lokf" / "questions.md"),
            f"- {today_utc()} Miss playbooks/kept.md: `is it hidden from a reader?`",
        )
        and read(khand).rstrip("\n") == "a line with more than a list"
    ), f"an unseen character reached the ledger or the hand-off: {result.out} // {read(khand)!r}"


def test_a_readers_question_of_invisible_characters_alone_is_refused(with_kept):
    write(
        with_kept / ".lokf" / "feedback.md",
        lines("# Reader feedback for the librarian", "", "## 2026-03-05", "", '- **Miss** - Q: "unseen?" - docent'),
    )
    refuses(
        with_kept,
        lines(
            "ops:",
            '  - {op: patch, path: playbooks/kept.md, edits: [{append: {content: again}}], log: fixed, from_feedback: \'- **Miss** - Q: "unseen?" - docent\', asked: "'
            + esc(0x200B)
            + esc(0x202E)
            + '"}',
        ),
        "a reader's question of invisible characters alone",
        "asked holds no printable text",
    )


def test_one_run_handles_at_most_ten_reader_entries(with_kept):
    """An eleventh waits for the next run."""
    write(
        with_kept / ".lokf" / "feedback.md",
        lines(
            "# Reader feedback for the librarian",
            "",
            "## 2026-03-05",
            "",
            *[f"- **Miss** - entry {i} - docent" for i in range(1, 12)],
        ),
    )
    ops = [
        f"  - {{op: patch, path: playbooks/kept.md, edits: [{{append: {{content: 'line {i}'}}}}], log: fixed, from_feedback: '- **Miss** - entry {i} - docent'}}"
        for i in range(1, 12)
    ]
    refuses(with_kept, lines("ops:", *ops), "a patch that handles eleven reader entries", "one run handles at most 10")
    applies(with_kept, lines("ops:", *ops[:10]))
    left = sum(1 for line in read(with_kept / ".lokf" / "feedback.md").split("\n") if line.startswith("- **"))
    assert left == 1, f"a patch that handles ten reader entries was not applied as expected: {left} entries left"


# A root index a person shaped by hand keeps its shape. Its sections may be
# `##` headings, and a line may list several concepts or name one in a
# sentence. The pen:
# - rewrites every line that holds one concept's link alone and nothing else;
# - files a new bullet under the folder's heading at whatever level it has, or
#   in the section that links the folder's index.md, but never under the title;
# - on delete, takes the link out of a list of links and leaves no double blank
#   line;
# - refuses a delete that would reword a sentence.

VOCAB = "The vocabulary ([index](glossary/index.md)): [Risk](glossary/risk.md), [Taxonomy](glossary/taxonomy.md)"
MULTI = "* [Acme Corp](org/acme.md), [Widget Co](org/widget.md)"


def reference(kb, path, title, description):
    write(
        kb / f"{path}.md",
        lines(
            "---",
            "type: Reference",
            f"id: https://acme.example/knowledge/{path}",
            f"title: {title}",
            f"description: {description}",
            "generated:",
            "  by: process:ktl-librarian",
            '  at: "2026-01-01T00:00:00Z"',
            "status: draft",
            "---",
            "",
            "# Overview",
            "",
            "Text.",
        ),
    )


def section(index, heading):
    """The lines under one root heading."""
    out, on = [], False
    for line in read(index).split("\n"):
        if line == heading:
            on = True
            continue
        if line.startswith("#"):
            on = False
        if on:
            out.append(line)
    return out


def no_double_blank(path):
    text = read(path).split("\n")
    return not any(a == "" and b == "" for a, b in zip(text, text[1:]))


@pytest.fixture
def hand_shaped(tmp_path):
    kb = tmp_path / ".lokf" / "knowledge"
    write(
        kb / "index.md",
        lines(
            "---",
            "base_iri: https://acme.example/knowledge/",
            "---",
            "",
            "# Acme",
            "",
            "Start at the [explanations](explanation/index.md).",
            "",
            "## Start here",
            "",
            "* [Risk](glossary/risk.md) - stale.",
            "",
            "## Glossary",
            "",
            VOCAB,
            "",
            "## Organizations",
            "",
            "([index](org/index.md))",
            "",
            MULTI,
            "",
            "Start with [Model](glossary/model.md), then read the rest.",
            "Read [Harm](glossary/harm.md) first.",
        ),
    )
    write(
        kb / "glossary" / "index.md",
        lines(
            "# Glossary",
            "",
            "* [Risk](risk.md) - a harm.",
            "* [Taxonomy](taxonomy.md) - a catalogue of risks.",
            "* [Model](model.md) - the model.",
            "* [Harm](harm.md) - a harm done.",
            "",
            "## See also",
            "",
            "* [Risk](risk.md) - a harm.",
        ),
    )
    write(
        kb / "org" / "index.md",
        lines(
            "# Org",
            "",
            "* [Acme Corp](acme.md) - stale.",
            "",
            "## Makers",
            "",
            "* [Widget Co](widget.md) - a maker of widgets.",
        ),
    )
    for path, title, description in [
        ("glossary/risk", "Risk", "a named harm."),
        ("glossary/taxonomy", "Taxonomy", "a catalogue of risks."),
        ("glossary/model", "Model", "the model."),
        ("glossary/harm", "Harm", "a harm done."),
        ("org/acme", "Acme Corp", "a company."),
        ("org/widget", "Widget Co", "a maker of widgets."),
    ]:
        reference(kb, path, title, description)
    write(kb / "log.md", "# Change Log\n")
    return tmp_path


def test_reindex_rewrites_each_lone_link_line_and_leaves_a_shared_root_line_as_it_was(hand_shaped):
    kb = kb_of(hand_shaped)
    applies(
        hand_shaped, lines("ops:", "  - {op: reindex, path: org/acme.md}", "  - {op: reindex, path: glossary/risk.md}")
    )
    index, glossary, org = read(kb / "index.md"), read(kb / "glossary" / "index.md"), read(kb / "org" / "index.md")
    assert (
        has_line(index, VOCAB)
        and has_line(index, MULTI)
        and "* [Risk](glossary/risk.md) - a named harm." in section(kb / "index.md", "## Start here")
        and glossary.split("\n").count("* [Risk](risk.md) - a named harm.") == 2
        and has_line(org, "* [Acme Corp](acme.md) - a company.")
        and len(re.findall(r"^#+ Glossary$", index, re.M)) == 1
        and not matches(index, r"^#+ Org$")
    ), f"reindex rewrote a hand-shaped root index, or missed a bullet: {index} // {glossary}"


def test_create_files_a_bullet_under_the_folders_heading_or_section_or_opens_one_at_the_roots_level(hand_shaped):
    kb = kb_of(hand_shaped)
    applies(
        hand_shaped,
        lines(
            "ops:",
            '  - {op: create, path: glossary/crosswalk.md, frontmatter: {type: Reference, title: Crosswalk, description: a mapping across taxonomies.}, body: "# Overview'
            + r"\n\nA mapping.\n"
            + '"}',
            '  - {op: create, path: org/newco.md, frontmatter: {type: Reference, title: Newco, description: a new company.}, body: "# Overview'
            + r"\n\nNew.\n"
            + '"}',
            '  - {op: create, path: explanation/why.md, frontmatter: {type: Explanation, title: Why, description: why it exists.}, body: "# Overview'
            + r"\n\nBecause.\n"
            + '"}',
            '  - {op: create, path: policies/retention.md, frontmatter: {type: Policy, title: Retention, description: how long rows are kept.}, body: "# Overview'
            + r"\n\nThirteen months.\n"
            + '"}',
        ),
    )
    index = read(kb / "index.md")
    text = index.split("\n")
    assert (
        len(re.findall(r"^#+ Glossary$", index, re.M)) == 1
        and "* [Crosswalk](glossary/crosswalk.md) - a mapping across taxonomies."
        in section(kb / "index.md", "## Glossary")
        and "## Organizations" in text
        and text[text.index("## Organizations") - 1] == ""
        and "* [Newco](org/newco.md) - a new company." in section(kb / "index.md", "## Organizations")
        and not matches(index, r"^#+ Org$")
        and "* [Why](explanation/why.md) - why it exists." in section(kb / "index.md", "## Explanation")
        and "* [Retention](policies/retention.md) - how long rows are kept." in section(kb / "index.md", "## Policies")
        and "# Policies" not in text
    ), f"create misplaced a bullet in a hand-shaped root index: {index}"


def test_delete_takes_a_link_out_of_a_list_of_links_and_leaves_no_double_blank_line(hand_shaped):
    kb = kb_of(hand_shaped)
    applies(
        hand_shaped,
        lines(
            "ops:",
            '  - {op: delete, path: glossary/taxonomy.md, log: "**Removal**: Taxonomy; its source is gone."}',
            '  - {op: delete, path: org/widget.md, log: "**Removal**: Widget Co; its source is gone."}',
        ),
    )
    index = read(kb / "index.md")
    others = read(kb / "glossary" / "index.md") + read(kb / "org" / "index.md")
    assert (
        has_line(index, "The vocabulary ([index](glossary/index.md)): [Risk](glossary/risk.md)")
        and has_line(index, "* [Acme Corp](org/acme.md)")
        and not re.search(r"taxonomy\.md|widget\.md", index + others)
        and no_double_blank(kb / "index.md")
        and no_double_blank(kb / "org" / "index.md")
    ), f"delete did not take the link out of a shared line cleanly: {index}"


@pytest.mark.parametrize(
    ("what", "path"),
    [
        ("deleting a concept a sentence links, with a comma after the link", "glossary/model.md"),
        ("deleting a concept a sentence links, with no comma", "glossary/harm.md"),
    ],
)
def test_delete_refuses_a_concept_a_sentence_links(hand_shaped, what, path):
    refuses(hand_shaped, lines("ops:", f"  - {{op: delete, path: {path}, log: gone}}"), what, "inside other text")


@pytest.fixture
def fragment_links(tmp_path):
    """A host that wrote a concept's link with a ./ lead or a #fragment."""
    kb = tmp_path / ".lokf" / "knowledge"
    write(
        kb / "index.md",
        lines(
            "---",
            "base_iri: https://acme.example/knowledge/",
            "---",
            "",
            "# Acme",
            "",
            "## X",
            "",
            "* [A](x/a.md) - a.",
            "* [B](x/b.md) - b.",
            "* [C](x/c.md) - c.",
            "",
            "Links: [A](./x/a.md#over), [B](x/b.md).",
            "See [C](./x/c.md#frag) for the rest.",
        ),
    )
    write(
        kb / "x" / "index.md",
        lines(
            "# X",
            "",
            "* [A](a.md) - a.",
            "* [B](b.md) - b.",
            "* [C](c.md) - c.",
            "",
            "Both: [A](./a.md#over), [B](b.md).",
        ),
    )
    for name, title in [("a", "A"), ("b", "B"), ("c", "C")]:
        reference(kb, f"x/{name}", title, f"{title}.")
    write(kb / "log.md", "# Change Log\n")
    return tmp_path


def test_delete_refuses_a_sentence_link_that_leads_with_dot_slash_and_carries_a_fragment(fragment_links):
    kb = kb_of(fragment_links)
    before = read(kb / "index.md") + read(kb / "x" / "index.md")
    write(patch_file(fragment_links), lines("ops:", "  - {op: delete, path: x/c.md, log: gone}"))
    result = apply(fragment_links, patch_file(fragment_links))
    assert not result, (
        f"delete of a concept a sentence links with ./ and a #fragment was not refused, leaving a dangling link: {result.out}"
    )
    assert "inside other text" in result.out and read(kb / "index.md") + read(kb / "x" / "index.md") == before, (
        f"delete of a ./#fragment sentence link failed for the wrong reason, or still wrote: {result.out}"
    )


def test_delete_takes_a_dot_slash_fragment_link_out_of_a_list_of_links(fragment_links):
    kb = kb_of(fragment_links)
    applies(fragment_links, lines("ops:", "  - {op: delete, path: x/a.md, log: gone}"))
    index, folder = read(kb / "index.md"), read(kb / "x" / "index.md")
    assert (
        not re.search(r"a\.md", index + folder)
        and has_line(index, "Links: [B](x/b.md).")
        and has_line(folder, "Both: [B](b.md).")
    ), f"delete left a ./#fragment link in a list, or did not keep the rest: {index} // {folder}"
