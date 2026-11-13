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
- a log line many operations give, or the patch gives for them, is written once;
- a bare web address in a log line or a question is written as an autolink;
- the lokf:related block survives a rewrite, and a rewrite sets frontmatter
  as a patch does;
- an operation takes only the keys it reads, and any other is refused by name;
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
import os
import re
import sys

import pytest

from conftest import REPO, SCRIPTS, bash, esc, has_line, matches, mirror_uv, read, run, today_utc, tree_digest, write

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


def test_a_log_line_that_already_says_edited_since_gets_no_second_note(applied):
    """The note is the pen's own sentence, so a log line that carries it, capital and all, keeps one copy."""
    applies(
        applied,
        lines(
            "ops:",
            "  - op: patch",
            "    path: playbooks/confirmed.md",
            "    edits:",
            '      - append: {content: "A second paragraph."}',
            '    log: "**Changed**: a second paragraph. Edited since a person confirmed it; the label says so until the curator looks again."',
        ),
    )
    entry = [line for line in read(kb_of(applied) / "log.md").split("\n") if "a second paragraph." in line]
    assert len(entry) == 1 and entry[0].count("dited since a person confirmed it") == 1, f"the note was added twice: {entry}"


def test_the_same_log_line_from_many_operations_is_written_once(applied):
    """A conversion that gave each of 22 concepts the same line once left 21 copies to delete by hand."""
    applies(
        applied,
        lines(
            "ops:",
            '  - {op: patch, path: playbooks/draft.md, edits: [{append: {content: "One."}}], log: cites its source by path}',
            '  - {op: patch, path: playbooks/new.md, edits: [{append: {content: "Two."}}], log: cites its source by path}',
        ),
    )
    log = read(kb_of(applied) / "log.md")
    assert log.count("* **Changed**: cites its source by path") == 1, f"the same line was written more than once: {log}"


def test_the_patchs_log_line_stands_in_for_each_operation_that_gives_none(applied):
    """An operation's own line still wins, and a concept a person confirmed is named beside the shared line."""
    applies(
        applied,
        lines(
            "log: each playbook cites its source by path",
            "ops:",
            '  - {op: patch, path: playbooks/draft.md, edits: [{append: {content: "One."}}]}',
            '  - {op: patch, path: playbooks/new.md, edits: [{append: {content: "Two."}}]}',
            '  - {op: create, path: playbooks/newer.md, frontmatter: {type: Playbook, title: Newer, description: newer.}, body: "# Overview"}',
            '  - {op: patch, path: playbooks/confirmed.md, edits: [{append: {content: "Three."}}]}',
            '  - {op: delete, path: playbooks/new.md, log: "**Removal**: New; its source is gone."}',
        ),
    )
    today = read(kb_of(applied) / "log.md").split(f"## {today_utc()}")[1].split("\n## ")[0]
    assert (
        today.count("* **Changed**: each playbook cites its source by path") == 1
        and has_line(
            today,
            "* **Changed**: each playbook cites its source by path `playbooks/confirmed.md` was edited since a person confirmed it; the label says so until the curator looks again.",
        )
        and "**Added**: Newer" not in today
        and has_line(today, "* **Removal**: New; its source is gone.")
    ), f"the patch's line did not stand in once for the operations without one: {today}"


def test_the_patchs_log_line_is_written_once_for_many_confirmed_concepts(applied):
    """One sentence after the shared line names every concept a person confirmed, rather than one copy of the line for each."""
    kb = kb_of(applied)
    second = read(kb / "playbooks" / "confirmed.md").replace("playbooks/confirmed", "playbooks/second").replace("Confirmed", "Second")
    write(kb / "playbooks" / "second.md", second)
    write(kb / "playbooks" / "index.md", read(kb / "playbooks" / "index.md") + "* [Second](second.md) - confirmed.\n")
    write(kb / "index.md", read(kb / "index.md") + "* [Second](playbooks/second.md) - confirmed.\n")
    applies(
        applied,
        lines(
            "log: each playbook cites its source by path.",
            "ops:",
            '  - {op: patch, path: playbooks/confirmed.md, edits: [{append: {content: "One."}}]}',
            '  - {op: patch, path: playbooks/draft.md, edits: [{append: {content: "Two."}}]}',
            '  - {op: patch, path: playbooks/second.md, edits: [{append: {content: "Three."}}]}',
        ),
    )
    today = read(kb / "log.md").split(f"## {today_utc()}")[1].split("\n## ")[0]
    assert today.count("each playbook cites its source by path.") == 1 and has_line(
        today,
        "* **Changed**: each playbook cites its source by path. `playbooks/confirmed.md` and `playbooks/second.md` were edited since a person confirmed them; each label says so until the curator looks again.",
    ), f"the shared line was not written once with one sentence naming both: {today}"


def test_a_bare_web_address_in_a_question_and_its_log_line_becomes_an_autolink(applied):
    """markdownlint refused the bare addresses a question carried into the concept and log.md; one in a code span or a link stays as written."""
    applies(
        applied,
        lines(
            "ops:",
            "  - op: question",
            "    path: playbooks/draft.md",
            '    text: "https://a.example/x/ moved (see https://a.example/y). `curl https://a.example/z` and [the page](https://a.example/p) agree?"',
        ),
    )
    wanted = "<https://a.example/x/> moved (see <https://a.example/y>). `curl https://a.example/z` and [the page](https://a.example/p) agree?"
    draft = read(kb_of(applied) / "playbooks" / "draft.md")
    log = read(kb_of(applied) / "log.md")
    assert has_line(draft, f"- {today_utc()}, process:ktl-librarian: {wanted}") and has_line(
        log, f"* **Open question**: Draft: {wanted}"
    ), f"the addresses were not written as autolinks: {draft} // {log}"


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


def test_rewrite_sets_frontmatter_as_patch_does_and_both_bullets_follow(applied):
    """A `set` on a rewrite was once dropped without a word, and the dry run passed."""
    kb = kb_of(applied)
    applies(
        applied,
        lines(
            "ops:",
            '  - {op: rewrite, path: playbooks/draft.md, body: "# Overview'
            + r"\n\nRewritten from the source.\n"
            + '", set: {title: Draft Two, description: a rewritten draft.}, log: rewritten}',
        ),
    )
    draft = read(kb / "playbooks" / "draft.md")
    assert (
        "Rewritten from the source." in draft
        and has_line(draft, "title: Draft Two")
        and has_line(draft, "description: a rewritten draft.")
        and has_line(read(kb / "index.md"), "* [Draft Two](playbooks/draft.md) - a rewritten draft.")
        and has_line(read(kb / "playbooks" / "index.md"), "* [Draft Two](draft.md) - a rewritten draft.")
    ), f"rewrite did not set the title and description, or the bullets did not follow: {draft}"


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
    (
        "setting status on a rewrite",
        lines("ops:", "  - {op: rewrite, path: playbooks/new.md, body: b, set: {status: stable}, log: x}"),
        "set may not touch status",
    ),
    (
        "setting a title with square brackets on a rewrite",
        lines("ops:", '  - {op: rewrite, path: playbooks/new.md, body: b, set: {title: "New [2]"}, log: x}'),
        "a title may not contain square brackets",
    ),
]


@pytest.mark.parametrize(("what", "text", "expected"), REFUSED, ids=[w for w, _, _ in REFUSED])
def test_refuses(applied, what, text, expected):
    refuses(applied, text, what, expected)


# An operation takes only the keys it reads. Any other key is refused by name,
# so a patch never passes a dry run with a key the pen would drop.
UNKNOWN_KEY_REFUSED = [
    (
        "edits on a rewrite",
        lines("ops:", "  - {op: rewrite, path: playbooks/new.md, body: b, edits: [{append: {content: x}}], log: x}"),
        "playbooks/new.md: rewrite does not take edits; it takes op, path, body, set, revision, log, from_feedback, asked",
    ),
    (
        "a revision on a recheck",
        lines("ops:", '  - {op: recheck, path: playbooks/new.md, revision: "0123456789abcdef0123456789abcdef01234567"}'),
        "playbooks/new.md: recheck does not take revision; it takes op, path",
    ),
    (
        "a misspelt set on a patch",
        lines("ops:", "  - {op: patch, path: playbooks/new.md, edits: [{append: {content: x}}], sets: {description: d.}, log: x}"),
        "patch does not take sets",
    ),
    (
        "an actor on one operation",
        lines("ops:", '  - {op: question, path: playbooks/new.md, text: "is this right?", by: "process:other"}'),
        "question does not take by",
    ),
]


@pytest.mark.parametrize(("what", "text", "expected"), UNKNOWN_KEY_REFUSED, ids=[w for w, _, _ in UNKNOWN_KEY_REFUSED])
def test_refuses_a_key_the_operation_does_not_take(applied, what, text, expected):
    refuses(applied, text, what, expected)


def test_a_replace_target_quoted_in_an_open_question_is_found_once_in_the_text(applied):
    """A question that quotes the text it asks about does not make the target occur twice."""
    applies(applied, lines("ops:", '  - {op: question, path: playbooks/draft.md, text: "is The new text. still right?"}'))
    applies(applied, lines("ops:", '  - {op: patch, path: playbooks/draft.md, edits: [{replace: {target: "The new text.", content: "Newer text."}}], log: x}'))
    draft = read(kb_of(applied) / "playbooks" / "draft.md")
    assert "Newer text." in draft and "is The new text. still right?" in draft, f"the replace missed its one target or edited the question: {draft}"
    refuses(
        applied,
        lines("ops:", '  - {op: patch, path: playbooks/draft.md, edits: [{replace: {target: "still right?", content: "x"}}], log: x}'),
        "a target found only under Open questions",
        "the target lies in the lokf:related block or under ## Open questions",
    )


def test_one_feedback_entry_named_by_two_operations_is_refused_as_such(applied):
    """The second operation used to read as naming an entry the file does not hold."""
    write(
        applied / ".lokf" / "feedback.md",
        read(applied / ".lokf" / "feedback.md") + '- **Miss** - Q: "how?" Answered from here. - docent\n',
    )
    entry = """'- **Miss** - Q: "how?" Answered from here. - docent'"""
    refuses(
        applied,
        lines(
            "ops:",
            f'  - {{op: patch, path: playbooks/draft.md, edits: [{{append: {{content: "One."}}}}], log: x, from_feedback: {entry}}}',
            f'  - {{op: patch, path: playbooks/new.md, edits: [{{append: {{content: "Two."}}}}], log: y, from_feedback: {entry}}}',
        ),
        "one entry named by two operations",
        "from_feedback names an entry another operation of this patch already handles",
    )


def test_a_dry_run_with_diff_shows_each_change_and_writes_nothing(applied):
    write(
        patch_file(applied),
        lines(
            "ops:",
            '  - {op: patch, path: playbooks/draft.md, edits: [{replace: {target: "The new text.", content: "Diffed text."}}], log: x}',
        ),
    )
    before = tree_digest(applied)
    result = apply(applied, "--dry-run", "--diff", patch_file(applied))
    assert (
        result
        and has_line(result.out, "--- a/.lokf/knowledge/playbooks/draft.md")
        and has_line(result.out, "+++ b/.lokf/knowledge/playbooks/draft.md")
        and has_line(result.out, "-The new text.")
        and has_line(result.out, "+Diffed text.")
        and tree_digest(applied) == before
    ), f"the dry run did not show the diff or wrote something: {result.out}"
    result = apply(applied, "--diff", patch_file(applied))
    assert result.rc == 2 and "--diff goes with --dry-run" in result.out and tree_digest(applied) == before, (
        f"--diff without --dry-run was not refused: {result.out}"
    )


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



def test_in_the_agents_step_of_a_scheduled_run_the_pen_only_checks(applied):
    """The wrapper sets KNOWLEDGE_PEN_DRY_RUN_ONLY for the agent: a write is refused and the patch file stays for the wrapper, while a dry run still checks it."""
    write(
        patch_file(applied),
        lines(
            "ops:",
            "  - {op: create, path: playbooks/held.md, frontmatter: {type: Playbook, title: Held, description: d.}, body: b}",
        ),
    )
    before = tree_digest(applied)
    only = {"KNOWLEDGE_PEN_DRY_RUN_ONLY": "1"}
    refused = bash(APPLY, "--root", applied, patch_file(applied), env=only)
    checked = bash(APPLY, "--root", applied, "--dry-run", patch_file(applied), env=only)
    assert (
        refused.rc == 2
        and "Nothing was written" in refused.out
        and tree_digest(applied) == before
        and patch_file(applied).exists()
    ), f"the pen wrote in the agent's step, or lost the patch file (exit {refused.rc}): {refused.out}"
    assert checked and "leave the patch file in place" in checked.out, f"the dry run did not tell the agent to leave the file: {checked.out}"

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


def test_a_concept_with_no_description_gets_its_link_alone_in_both_indexes(ka):
    kb = kb_of(ka)
    write(
        kb / "playbooks" / "bare.md",
        lines(
            "---",
            "type: Playbook",
            "id: https://acme.example/knowledge/playbooks/bare",
            "title: Bare",
            "generated:",
            "  by: process:ktl-librarian",
            '  at: "2026-01-01T00:00:00Z"',
            "status: draft",
            "---",
            "",
            "# Overview",
            "",
            "Bare.",
        ),
    )
    applies(ka, lines("ops:", "  - {op: patch, path: playbooks/bare.md, edits: [{append: {content: More.}}], log: x}"))
    folder, root = read(kb / "playbooks" / "index.md"), read(kb / "index.md")
    assert has_line(folder, "* [Bare](bare.md)") and has_line(root, "* [Bare](playbooks/bare.md)") and " - \n" not in folder + root, (
        "a concept with no description got a bullet that ends in a bare dash"
    )


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


@pytest.fixture
def related(tmp_path):
    """A bundle of two concepts, the first relating to the second."""
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    stamp = "generated:\n  by: process:ktl-librarian\n  at: 2026-01-01T00:00:00Z\nstatus: draft\n"
    write(kk / "x" / "a.md", f"---\ntype: Service\ntitle: A\ndependsOn:\n  - https://acme.example/knowledge/x/b\n{stamp}---\n\n# A\n")
    write(kk / "x" / "b.md", f"---\ntype: Service\ntitle: B\n{stamp}---\n\n# B\n")
    return tmp_path


def set_relation(field_and_value: str) -> str:
    return lines("ops:", "  - op: patch", "    path: x/b.md", "    set:", f"      {field_and_value}", '    log: "**Changed**: a relation."')


@pytest.mark.parametrize(
    "value",
    [
        "references: [https://acme.example/knowledge/x/none]",
        "references: [x/none.md]",
        "references: [none]",
        "relations: [{predicate: joinsWith, target: https://acme.example/knowledge/x/none}]",
        "isReplacedBy: https://acme.example/knowledge/x/none",
    ],
)
def test_a_relation_that_names_no_concept_is_refused(related, value):
    """Schema validation passes it as a well-formed value, and only --check-refs would catch it, after the patch is written."""
    refuses(related, set_relation(value), "a relation to nothing", "no concept of the bundle has that id")


@pytest.mark.parametrize(
    "value",
    [
        "references: [https://acme.example/knowledge/x/a]",
        "references: [x/a.md]",
        "references: [x/a]",
        "references: [a.md]",
        "references: ['https://acme.example/knowledge/x/a#part']",
        "relations: [{predicate: joinsWith, target: x/a}]",
        "references: [https://elsewhere.example/thing]",
    ],
)
def test_a_relation_to_a_concept_or_outside_the_bundle_is_written(related, value):
    applies(related, set_relation(value))


def test_a_relation_to_a_concept_this_patch_creates_is_written(related):
    applies(
        related,
        lines(
            "ops:",
            "  - op: create",
            "    path: x/new.md",
            "    frontmatter: {type: Service, title: New, description: New.}",
            "    body: |",
            "      # New",
            '    log: "**Added**: New."',
            "  - op: patch",
            "    path: x/b.md",
            "    set: {references: [x/new.md]}",
            '    log: "**Changed**: a relation."',
        ),
    )


def test_a_description_in_a_slot_that_also_takes_one_is_written(related):
    """`measures` takes a description as well as an IRI, and --check-refs skips a value with a space."""
    applies(related, set_relation('measures: ["orders per day"]'))


@pytest.mark.parametrize(
    "value",
    [
        "references: [/x/a.md]",
        "references: [/x/a]",
        "references: [https://acme.example/knowledge/x/a.md]",
        "references: [gist:Thing]",
    ],
)
def test_each_spelling_check_refs_accepts_is_written(related, value):
    applies(related, set_relation(value))


def test_a_concept_with_a_fragment_in_its_own_id_is_found(related):
    kk = kb_of(related)
    b = kk / "x" / "b.md"
    write(b, read(b).replace("title: B\n", "title: B\nid: https://acme.example/knowledge/vocab#B\n"))
    applies(related, lines("ops:", "  - op: patch", "    path: x/a.md", "    set: {references: ['https://acme.example/knowledge/vocab#B']}", '    log: "**Changed**: a relation."'))


def test_deleting_a_concept_a_domain_slot_names_is_refused(related):
    """The report reads a whole IRI in a host's own slot as a relation, so the pen has to see it too."""
    kk = kb_of(related)
    a = kk / "x" / "a.md"
    write(a, read(a).replace("dependsOn:\n  - https://acme.example/knowledge/x/b\n", "emitted_by: https://acme.example/knowledge/x/b\n"))
    refuses(related, lines("ops:", "  - op: delete", "    path: x/b.md", '    log: "**Removal**: B."'), "a delete a domain slot still names", "emitted_by still names x/b.md")


def test_the_sidecars_two_examples_can_be_deleted_together_or_in_the_order_they_relate(tmp_path):
    """Bootstrap deletes them, and the second example relates to the first."""
    kk = tmp_path / ".lokf" / "knowledge"
    write(kk / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    stamp = "generated:\n  by: process:ktl-librarian\n  at: 2026-01-01T00:00:00Z\nstatus: draft\n"
    write(kk / "s" / "a.md", f"---\ntype: Service\ntitle: A\n{stamp}---\n\n# A\n")
    write(kk / "s" / "b.md", f"---\ntype: Service\ntitle: B\ndependsOn:\n  - s/a.md\n{stamp}---\n\n# B\n")
    log = '    log: "**Removal**: an example."'
    refuses(tmp_path, lines("ops:", "  - op: delete", "    path: s/a.md", log), "the first example alone", "still names s/a.md")
    applies(tmp_path, lines("ops:", "  - op: delete", "    path: s/a.md", log, "  - op: delete", "    path: s/b.md", log))


def test_the_pen_and_the_report_read_the_same_relation_fields():
    pen = re.search(r"RELATION_FIELDS = \((.*?)\)", read(SCRIPTS / "knowledge-apply.py"), re.S).group(1)
    report = re.search(r'split\("([A-Za-z ]+)", relnames', read(SCRIPTS / "knowledge-report.sh")).group(1)
    assert sorted(re.findall(r'"(\w+)"', pen)) == sorted(report.split()), "the pen and knowledge-report.sh read different relation fields"
    pen = re.search(r"NOT_LINKS = \{(.*?)\}", read(SCRIPTS / "knowledge-apply.py"), re.S).group(1)
    report = re.search(r'split\("([a-z_ ]+)", notlink', read(SCRIPTS / "knowledge-report.sh")).group(1)
    assert sorted(re.findall(r'"(\w+)"', pen)) == sorted(report.split()), "the pen and knowledge-report.sh leave out different fields"


def test_a_relation_already_broken_does_not_stop_another_edit(related):
    """The patch did not break it, and a person's old typo must not hold up an unrelated change."""
    kk = kb_of(related)
    a = kk / "x" / "a.md"
    write(a, read(a).replace("x/b\n", "x/missing\n"))
    applies(related, lines("ops:", "  - op: patch", "    path: x/a.md", "    set: {description: New words.}", '    log: "**Changed**: words."'))


def test_deleting_a_concept_another_relates_to_is_refused_until_the_patch_drops_the_relation(related):
    delete = ["  - op: delete", "    path: x/b.md", '    log: "**Removal**: B; its source is gone."']
    refuses(related, lines("ops:", *delete), "a delete that leaves a relation behind", "still names x/b.md")
    applies(related, lines("ops:", "  - op: patch", "    path: x/a.md", "    set: {dependsOn: []}", '    log: "**Changed**: drop it."', *delete))


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
    (
        "a second heading and an open fence above a person's note, which the report then no longer lists",
        lines(
            "ops:",
            '  - {op: patch, path: playbooks/new.md, edits: [{append: {content: "## Open questions'
            + r"\n\n- 2026-03-04, process:ktl-librarian: is this right?\n\n```text"
            + '"}}], log: x}',
        ),
        "playbooks/new.md: this patch would hide a note a person left (human:ada, 2026-03-03) from the report",
    ),
    (
        "a person's event in a flow mapping under a key the gates do not read",
        lines(
            "ops:",
            '  - {op: patch, path: playbooks/draft.md, set: {exclusions: [{resource: docs/a.md, reason: left out, by: "human:ada"}]}, log: x}',
        ),
        "playbooks/draft.md: this patch would add a person's exclusions event (human:ada, no time)",
    ),
] + [
    (
        f"a person's note spelt {spelling!r}, which a Markdown reader shows as one",
        'ops:\n  - op: create\n    path: playbooks/planted.md\n    frontmatter: {type: Playbook, title: Planted, description: planted.}\n    body: "# Overview'
        + r"\n\nText.\n\n## Open questions\n\n" + spelling + r" looks right to me\n"
        + '"\n',
        "playbooks/planted.md: this patch would add a note in a person's name",
    )
    for spelling in (" - 2026-03-04, human:ada:", "-  2026-03-04, human:ada:", "* 2026-03-04, human:ada:", "+ 2026-03-04, human:ada:", r"- 2026-03-04,\thuman:ada:")
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
        "  - by: human:ada",
        "    at: 2026-02-02T10:00:00Z",
        "    revision: 0123456",
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


def test_a_list_is_written_indented_under_its_key(ka):
    """PyYAML on its own writes a list's dashes at its key's column, which yamllint's default rules reject."""
    applies(
        ka,
        lines(
            "ops:",
            "  - op: create",
            "    path: playbooks/listed.md",
            "    frontmatter: {type: Playbook, title: Listed, description: listed., tags: [a, b], references: [https://acme.example/knowledge/playbooks/draft]}",
            '    body: "# Overview\n\nListed.\n"',
        ),
    )
    text = read(kb_of(ka) / "playbooks" / "listed.md")
    assert all(has_line(text, line) for line in ("tags:", "  - a", "  - b", "references:", "  - https://acme.example/knowledge/playbooks/draft")), (
        f"a list was not indented under its key: {text}"
    )


def test_a_readers_question_and_a_handoff_line_lose_every_character_a_reader_cannot_see(with_kept):
    """As Unicode marks them: a zero-width space, a right-to-left override, an Arabic letter mark, a soft hyphen, a tag character, variation selectors and a Hangul filler."""
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
        + esc(0xFE0F)
        + esc(0xE0100)
        + esc(0x3164)
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


def fake_lokf(root, rc):
    """A toolkit in .lokf/.venv whose validate rejects every concept it is given, or accepts them all."""
    say = 'echo "[ERROR] $2/playbooks/draft.md: sources is not of type object"' if rc else 'echo "OK"'
    write(root / ".lokf" / ".venv" / "bin" / "lokf", f"#!/bin/sh\n{say}\nexit {rc}\n").chmod(0o755)


DRAFT_EDIT = lines(
    "ops:",
    "  - op: patch",
    "    path: playbooks/draft.md",
    '    edits: [{replace: {target: "The old text.", content: "The new text."}}]',
    '    log: "the draft now says the new text"',
)


def test_a_patch_the_schema_rejects_writes_nothing(ka):
    fake_lokf(ka, 1)
    for dry in ([], ["--dry-run"]):
        write(patch_file(ka), DRAFT_EDIT)
        before = tree_digest(ka)
        result = apply(ka, *dry, patch_file(ka))
        assert result.rc == 1 and tree_digest(ka) == before, f"the pen wrote what lokf validate rejects ({dry}): {result.out}"
        assert "schema: [ERROR] .lokf/knowledge/playbooks/draft.md" in result.out, f"the pen did not name the rejected concept by its own path: {result.out}"
    assert not [p for p in (ka / ".lokf").iterdir() if p.name.startswith(".pen-check-")], "the pen left its staged copy behind"


def test_a_patch_the_schema_accepts_is_written_and_says_so(ka):
    fake_lokf(ka, 0)
    result = applies(ka, DRAFT_EDIT)
    assert "schema checked" in result.out and "The new text." in read(ka / ".lokf" / "knowledge" / "playbooks" / "draft.md"), (
        f"the pen did not write a patch lokf validate accepts, or did not say it checked: {result.out}"
    )


def test_without_the_toolkit_the_pen_says_the_schema_was_not_checked(ka):
    result = applies(ka, DRAFT_EDIT)
    assert "schema not checked" in result.out, f"the pen did not say it skipped the schema: {result.out}"


def test_the_sidecar_venv_runs_the_pen_before_uv(tmp_path):
    """A host behind a mirror runs the pen from .lokf/.venv, which uv sync installed from uv.lock."""
    scripts = tmp_path / ".lokf" / "scripts"
    for name in ("knowledge-apply.sh", "knowledge-apply.py"):
        write(scripts / name, (SCRIPTS / name).read_text(encoding="utf-8"))
    write(tmp_path / ".lokf" / ".venv" / "bin" / "python", f'#!/bin/sh\nexec "{sys.executable}" "$@"\n').chmod(0o755)
    uv = write(tmp_path / "fakebin" / "uv", "#!/bin/sh\necho 'x No solution found' >&2\nexit 1\n")
    uv.chmod(0o755)
    result = bash(scripts / "knowledge-apply.sh", "--format", env={"PATH": f"{uv.parent}{os.pathsep}{os.environ['PATH']}"})
    assert result and "ops:" in result.out, f"the pen did not run from the sidecar's .venv: {result.out}"


def test_behind_a_mirror_without_upload_times_the_pen_lifts_the_date_and_keeps_the_pin(tmp_path):
    """uv drops every file it cannot date, so the pen lifts exclude-newer for the package uv names, and says so."""
    path, log = mirror_uv(tmp_path, "PyYAML-6.0.3.tar.gz")
    result = bash(SCRIPTS / "knowledge-apply.sh", "--format", "--root", tmp_path, env={"PATH": path})
    assert result and "ops:" in result.out, f"the pen did not run behind the mirror: {result.out}"
    assert "exclude-newer is lifted for pyyaml. The versions stay pinned" in result.out, f"the pen did not say it lifted the date: {result.out}"
    runs = [line for line in read(log).split("\n") if line.startswith("run ")]
    assert runs and "--exclude-newer-package pyyaml=false" in runs[0], f"uv run did not get the lifted date: {read(log)}"


def test_a_uv_that_cannot_install_pyyaml_is_not_a_finding(tmp_path):
    """uv exits 1 when it cannot resolve, the pen's exit for findings; a failure with no missing upload date is not retried."""
    fakebin = tmp_path / "fakebin"
    write(fakebin / "uv", "#!/bin/sh\necho 'x No solution found when resolving script dependencies:' >&2\nexit 1\n").chmod(0o755)
    write(fakebin / "python3", "#!/bin/sh\nexit 1\n").chmod(0o755)
    result = bash(SCRIPTS / "knowledge-apply.sh", "--format", "--root", tmp_path, env={"PATH": f"{fakebin}{os.pathsep}{os.environ['PATH']}"})
    assert result.rc == 2, f"the pen did not exit 2 when uv could not install pyyaml: {result.rc} {result.out}"
    assert "No solution found" in result.out and "nothing was written" in result.out, f"the pen did not show uv's error: {result.out}"


def test_a_uv_that_cannot_install_pyyaml_leaves_the_pen_to_python3_and_says_so(tmp_path):
    """python3's own PyYAML is a release no pin holds, so the run says it fell back."""
    fakebin = tmp_path / "fakebin"
    write(fakebin / "uv", "#!/bin/sh\necho 'x No solution found when resolving script dependencies:' >&2\nexit 1\n").chmod(0o755)
    write(fakebin / "python3", f'#!/bin/sh\nexec "{sys.executable}" "$@"\n').chmod(0o755)
    result = bash(SCRIPTS / "knowledge-apply.sh", "--format", "--root", tmp_path, env={"PATH": f"{fakebin}{os.pathsep}{os.environ['PATH']}"})
    assert result and "ops:" in result.out, f"the pen did not run with python3: {result.out}"
    assert "so this run uses python3's own" in result.out, f"the pen did not say it fell back to python3: {result.out}"


def test_a_complete_script_environment_runs_the_pen_with_the_index_down(tmp_path):
    """uv_ready tries offline first, so a script environment already built needs no index."""
    path, log = mirror_uv(tmp_path, ready=True)
    result = bash(SCRIPTS / "knowledge-apply.sh", "--format", "--root", tmp_path, env={"PATH": path})
    assert result and "ops:" in result.out, f"the pen did not run with the index down: {result.out}"
    syncs = [line for line in read(log).split("\n") if line.startswith("sync ")]
    assert syncs and all("--offline" in line for line in syncs), f"the pen asked the index although the environment was complete: {read(log)}"


def test_forced_colour_does_not_hide_the_missing_upload_date(tmp_path):
    """With FORCE_COLOR set, uv colours each warning, and a coloured warning names no package."""
    path, log = mirror_uv(tmp_path, "PyYAML-6.0.3.tar.gz")
    result = bash(SCRIPTS / "knowledge-apply.sh", "--format", "--root", tmp_path, env={"PATH": path, "FORCE_COLOR": "1"})
    assert result and "exclude-newer is lifted for pyyaml." in result.out, f"the pen did not lift the date with FORCE_COLOR set: {result.out}"


def test_a_file_name_in_backticks_still_names_its_package(tmp_path):
    """uv 0.13 puts the file name in backticks, and earlier releases do not."""
    path, log = mirror_uv(tmp_path, "PyYAML-6.0.3.tar.gz", ticks=True)
    result = bash(SCRIPTS / "knowledge-apply.sh", "--format", "--root", tmp_path, env={"PATH": path})
    assert result and "exclude-newer is lifted for pyyaml." in result.out, f"the pen did not read a file name in backticks: {result.out}"


def test_the_pen_lifts_no_date_for_a_package_its_header_does_not_pin(tmp_path):
    """No pin holds such a package, so the mirror could serve any version of it. Its date stays, and the pen exits 2."""
    path, log = mirror_uv(tmp_path, "other_pkg-1.0-py3-none-any.whl")
    write(tmp_path / "mirrorbin" / "python3", "#!/bin/sh\nexit 1\n").chmod(0o755)
    result = bash(SCRIPTS / "knowledge-apply.sh", "--format", "--root", tmp_path, env={"PATH": path})
    assert result.rc == 2 and "other-pkg, which the script's header does not pin" in result.out, f"the pen did not refuse to lift an unpinned package: {result.rc} {result.out}"
    assert "other-pkg=false" not in read(log), f"the pen lifted the date of a package its header does not pin: {read(log)}"


def test_the_pen_stops_when_a_lifted_date_changes_nothing(tmp_path):
    """A uv that warns again about a package already lifted is not retried round after round."""
    path, log = mirror_uv(tmp_path, "PyYAML-6.0.3.tar.gz", ignores_lift=True)
    write(tmp_path / "mirrorbin" / "python3", "#!/bin/sh\nexit 1\n").chmod(0o755)
    result = bash(SCRIPTS / "knowledge-apply.sh", "--format", "--root", tmp_path, env={"PATH": path})
    online = [line for line in read(log).split("\n") if line.startswith("sync ") and "--offline" not in line]
    assert result.rc == 2 and len(online) == 2, f"the pen retried a lift that changed nothing: {result.rc} {read(log)}"


def recording_lokf(root, say, rc):
    """A toolkit in .lokf/.venv that notes the folder it ran in and its arguments, says `say` and exits `rc`."""
    calls = root.parent / f"{root.name}-lokf-calls.txt"
    write(root / ".lokf" / ".venv" / "bin" / "lokf", f'#!/bin/sh\necho "$(pwd -P) $*" >> "{calls}"\n{say}\nexit {rc}\n').chmod(0o755)
    return calls


def test_a_toolkit_that_cannot_validate_does_not_refuse_the_patch(ka):
    """A failure with no [ERROR] line is the toolkit's, such as one installed without LinkML."""
    recording_lokf(ka, "echo 'validation needs LinkML, which the core install leaves out.' >&2", 1)
    result = applies(ka, DRAFT_EDIT)
    assert "schema not checked: lokf validate could not run (validation needs LinkML" in result.out, (
        f"the pen did not say the toolkit could not run: {result.out}"
    )


def test_the_pen_validates_with_the_domain_vocabulary_the_justfile_names(ka):
    write(ka / ".lokf" / "justfile", 'bundle := "knowledge"\nschema := "schemas/acme.yaml"\n')
    write(ka / ".lokf" / "schemas" / "acme.yaml", "id: https://acme.example/schema\n")
    calls = recording_lokf(ka, "echo OK", 0)
    result = applies(ka, DRAFT_EDIT)
    line = read(calls).strip()
    folder, _, args = line.partition(" ")
    assert "schema checked" in result.out and folder == str((ka / ".lokf" / "schemas").resolve()) and args.startswith("validate --schema acme.yaml "), (
        f"the pen did not run lokf validate from the schema's folder with --schema: {line} // {result.out}"
    )


def test_an_unreadable_schema_line_is_reported_not_read_as_no_schema(ka):
    """Validated against LOKF core alone, every concept of a domain type would be refused."""
    write(ka / ".lokf" / "justfile", "schema := 'acme.yaml'\n")
    calls = recording_lokf(ka, "echo OK", 0)
    result = applies(ka, DRAFT_EDIT)
    assert 'schema line is not in the form schema := "<file>"' in result.out and not calls.exists(), (
        f"the pen read an unreadable schema line as no schema: {result.out}"
    )


# ---- what an audit of the pen found, 2026-11-12 ------------------------------
# Each of these wrote, or deleted, what the rules above say the pen never
# does, by a spelling the rule did not read.


@pytest.mark.parametrize("slot", ["revised", "refuted"])
def test_the_event_slots_lokf_0_9_0_added_are_not_the_librarians_to_write(ka, slot):
    event = '{by: "process:ktl-librarian", at: "2026-03-04T00:00:00Z", reason: wrong}'
    refuses(ka, lines("ops:", f"  - {{op: patch, path: playbooks/draft.md, set: {{{slot}: {event}}}, log: x}}"), f"a set of {slot}", f"set may not touch {slot}")
    refuses(
        ka,
        lines("ops:", "  - op: create", "    path: playbooks/fresh.md", f"    frontmatter: {{type: Playbook, title: Fresh, description: fresh., {slot}: {event}}}", '    body: "# Overview"'),
        f"a create with {slot}",
        f"create may not set {slot}",
    )


def test_a_concept_that_spells_a_key_twice_is_not_read_as_its_last_spelling(ka):
    """A clean merge of a confirmation and a re-check leaves `verified` twice; PyYAML alone would show the pen the second block only."""
    path = kb_of(ka) / "playbooks" / "twice.md"
    write(
        path,
        lines(
            "---", "type: Playbook", "id: https://acme.example/knowledge/playbooks/twice", "title: Twice", "description: twice.",
            "verified:", "  - by: human:ada", '    at: "2026-02-02T00:00:00Z"',
            "verified:", "  - by: process:ktl-librarian", '    at: "2026-02-03T00:00:00Z"',
            "---", "", "# Overview",
        ),
    )
    refuses(ka, lines("ops:", "  - {op: delete, path: playbooks/twice.md, log: gone}"), "a delete of a concept that spells verified twice", "the key 'verified' is given twice")


def test_an_operation_that_gives_a_key_twice_is_refused_not_half_applied(ka):
    write(patch_file(ka), lines("ops:", "  - op: patch", "    path: playbooks/draft.md", "    set: {title: One}", "    set: {description: two.}", "    log: x"))
    before = tree_digest(ka)
    result = apply(ka, patch_file(ka))
    assert result.rc == 2 and "the key 'set' is given twice" in result.out and tree_digest(ka) == before, f"the pen applied half of a doubled key: {result.out}"


def test_a_concept_created_and_deleted_in_one_patch_is_refused_before_anything_is_written(ka):
    refuses(
        ka,
        lines(
            "ops:",
            "  - {op: patch, path: playbooks/draft.md, edits: [{replace: {target: The old text., content: The new text.}}], log: x}",
            '  - {op: create, path: playbooks/tmp.md, frontmatter: {type: Playbook, title: Tmp, description: tmp.}, body: "# Overview"}',
            "  - {op: delete, path: playbooks/tmp.md, log: gone}",
        ),
        "a create and a delete of one path",
        "this patch creates the concept, so there is no file to delete",
    )
    assert not list(kb_of(ka).rglob("*.tmp")), "the pen left a temporary file in the bundle"


def test_a_path_or_an_actor_that_ends_in_a_line_break_is_refused(ka):
    refuses(
        ka,
        'ops:\n  - op: create\n    path: "playbooks/index.md\\n"\n    frontmatter: {type: Playbook, title: Sneaky, description: sneaky.}\n    body: "# Overview"\n',
        "a path ending in a line break",
        "is not a concept path",
    )
    refuses(ka, 'by: "process:x\\n"\nops:\n  - {op: question, path: playbooks/draft.md, text: "is this right?"}\n', "an actor ending in a line break", "by must be a process:<id> actor")


def test_a_patch_never_writes_under_the_curators_own_actor(ka):
    """`process:ktl-curator` stands for a person who could not sign in; the pen protects that line from the librarian."""
    refuses(ka, lines("by: process:ktl-curator", "ops:", '  - {op: question, path: playbooks/draft.md, text: "Sent back: wrong."}'), "a patch by the curator's actor", "by may not be process:ktl-curator")


def test_the_pen_writes_nothing_through_a_link_that_leaves_the_bundle(ka):
    outside = ka / "docs"
    write(outside / "index.md", "# Docs\n")
    (kb_of(ka) / "guides").symlink_to(outside, target_is_directory=True)
    refuses(
        ka,
        lines("ops:", '  - {op: create, path: guides/setup.md, frontmatter: {type: Playbook, title: Setup, description: setup.}, body: "# Overview"}'),
        "a create through a folder that links out of the bundle",
        "a link on this path leads out of the bundle",
    )
    assert not (outside / "setup.md").exists(), "the pen wrote outside the bundle"


def test_a_file_the_pen_writes_keeps_its_mode_and_a_new_one_takes_the_umasks(ka):
    draft = kb_of(ka) / "playbooks" / "draft.md"
    draft.chmod(0o644)
    applies(ka, lines("ops:", "  - {op: recheck, path: playbooks/draft.md}", '  - {op: create, path: playbooks/fresh.md, frontmatter: {type: Playbook, title: Fresh, description: fresh.}, body: "# Overview"}'))
    umask = os.umask(0)
    os.umask(umask)
    fresh = (kb_of(ka) / "playbooks" / "fresh.md").stat().st_mode & 0o777
    assert draft.stat().st_mode & 0o777 == 0o644 and fresh == 0o666 & ~umask, f"the pen changed a mode: {oct(draft.stat().st_mode & 0o777)}, {oct(fresh)}"


def test_an_operation_that_leaves_the_frontmatter_alone_writes_it_back_as_it_was(ka):
    """A comment and a folded line in the block survive a `resolve`, which changes the body only."""
    path = kb_of(ka) / "playbooks" / "folded.md"
    block = lines(
        "---", "type: Playbook", "id: https://acme.example/knowledge/playbooks/folded", "title: Folded",
        "# keep this wording", "description: >-", "  a folded", "  description.", "status: draft", "---",
    )
    write(path, block + lines("", "# Overview", "", "## Open questions", "", "- 2026-03-01, process:ktl-librarian: is it so?"))
    applies(ka, lines("ops:", '  - {op: resolve, path: playbooks/folded.md, target: "is it so?", log: "**Resolved**: the source settles it."}'))
    assert read(path).startswith(block) and "is it so?" not in read(path), f"the pen rewrote a frontmatter block it did not change: {read(path)}"


def test_a_root_index_or_a_log_the_pen_cannot_read_is_a_finding_not_a_traceback(ka):
    index = kb_of(ka) / "index.md"
    kept = read(index)
    write(index, "---\nbase_iri: [unclosed\n---\n\n# Acme\n")
    result = applies_not(ka, DRAFT_EDIT)
    assert result.rc == 1 and "index.md: the bundle's root index.md cannot be read" in result.out and "Traceback" not in result.out, result.out
    write(index, kept)
    (kb_of(ka) / "log.md").write_bytes(b"# Change Log\n\n\xff\xfe not utf-8\n")
    result = applies_not(ka, DRAFT_EDIT)
    assert result.rc == 1 and "log.md: the log cannot be read" in result.out and "Traceback" not in result.out, result.out


def applies_not(root, text):
    write(patch_file(root), text)
    return apply(root, patch_file(root))


def quoting(excerpt):
    """A patch that gives the draft one source with an excerpt."""
    return lines(
        "ops:",
        "  - op: patch",
        "    path: playbooks/draft.md",
        "    set:",
        "      sources:",
        "        - resource: docs/limits.md",
        f"          excerpt: {excerpt}",
        '    log: "the draft quotes its source"',
    )


def test_the_pen_has_the_toolkit_look_for_an_excerpt_in_its_file(ka):
    """The staged copy sits a folder below the bundle, so the pen names the root the gate's recipe finds."""
    (ka / ".git").mkdir()
    calls = recording_lokf(ka, "echo 'OK - 2 concepts validate against KnowledgeBundle. Every local excerpt is in its resource.'", 0)
    result = applies(ka, quoting('"600 requests per minute"'))
    args = read(calls).strip().partition(" ")[2]
    assert f"--check-excerpts --root {ka.resolve()} " in args and "Every local excerpt is in its resource" in result.out, (
        f"the pen did not ask for the excerpt check from the repository root, or did not say what it found: {args} // {result.out}"
    )


def test_a_patch_that_quotes_nothing_is_validated_without_the_excerpt_check(ka):
    """A toolkit before lokf 0.9.0 does not take the flag, and a host on one writes no excerpt."""
    calls = recording_lokf(ka, "echo OK", 0)
    applies(ka, DRAFT_EDIT)
    assert "--check-excerpts" not in read(calls), f"the pen passed the excerpt check with no excerpt to find: {read(calls)}"


def test_an_excerpt_its_file_does_not_hold_writes_nothing(ka):
    recording_lokf(ka, "echo \"[ERROR] https://acme.example/knowledge/playbooks/draft: \\`sources[0].excerpt\\` ('600 requests') is not in 'docs/limits.md'\" >&2", 1)
    refuses(ka, quoting('"600 requests"'), "an excerpt its file does not hold", "is not in 'docs/limits.md'")


def test_a_toolkit_without_the_excerpt_check_refuses_an_excerpt(ka):
    """Its schema has no `excerpt` either, so the concept would fail the gate once written."""
    recording_lokf(ka, "echo 'No such option: --check-excerpts' >&2", 2)
    refuses(ka, quoting('"600 requests"'), "an excerpt under a toolkit before lokf 0.9.0", "older than lokf 0.9.0")


def test_an_excerpt_is_a_passage_and_not_the_page(ka):
    fake_lokf(ka, 0)
    refuses(ka, quoting('"' + "word " * 101 + '"'), "an excerpt past the limit", "the pen writes at most 500")
    refuses(ka, quoting('"   "'), "an excerpt with no text", "holds no text")
    applies(ka, quoting('"' + "word " * 99 + '"'))


def test_create_refuses_an_excerpt_past_the_limit(ka):
    fake_lokf(ka, 0)
    refuses(
        ka,
        lines(
            "ops:",
            "  - op: create",
            "    path: playbooks/limits.md",
            "    frontmatter:",
            "      type: Playbook",
            "      title: Limits",
            "      description: The rate limit.",
            "      sources:",
            "        - resource: docs/limits.md",
            '          excerpt: "' + "x" * 501 + '"',
            '    body: "# Overview"',
        ),
        "a new concept whose excerpt is past the limit",
        "the pen writes at most 500",
    )


CONTRACT = REPO / "scripts" / "validate-repository.sh"


def test_the_contracts_unseen_character_check_is_as_wide_as_the_pen(tmp_path):
    """Check 21 of validate-repository.sh carries the pen's IGNORABLE class and also refuses a line or paragraph separator."""
    pen = re.search(r'^IGNORABLE = re\.compile\("([^"]+)"\)$', read(SCRIPTS / "knowledge-apply.py"), re.M).group(1)
    contract = read(CONTRACT)
    assert f'IGNORABLE = re.compile("{pen}")' in contract, "check 21's class differs from the pen's IGNORABLE"
    snippet = re.search(r"unseen_py <<'PY' \|\| true\n(.*?)\nPY\n", contract, re.S).group(1)
    for code in (0x34F, 0x3164, 0xFE0F, 0x2028, 0x2029, 0x200B):
        write(tmp_path / f"u{code:04x}.md", f"A{chr(code)} word.\n")
    write(tmp_path / "clean.md", "A word.\n")
    names = "\0".join(sorted(p.name for p in tmp_path.iterdir()))
    result = run([sys.executable, "-c", snippet], cwd=tmp_path, stdin=names)
    found = {line.split(":")[0] for line in result.out.split("\n") if line}
    assert result.rc == 1 and found == {p.name for p in tmp_path.iterdir()} - {"clean.md"}, result.out
