"""prose-check.py reports each thing it claims to see, and stays quiet on what the hand passes kept.

This was check 18 in scripts/validate-repository.sh. The script must refuse a
rewording that touches a concept a person wrote or confirmed, or a byte of
frontmatter, or that adds a character no reader sees. It reads events the way
the provenance gates do, so each form they read is staged here.

Two assertions about this repository's own files stay in the contract
script: that its bundle is given its verdicts, and that the skill's own pages
pass the style rules they state.
"""

from __future__ import annotations

import sys

import pytest

from conftest import REPO, Git, run, write

PROSE = REPO / "skills" / "ktl-prose" / "scripts" / "prose-check.py"
PARA = "Each check reads one file. " * 32
LIB = 'generated:\n  by: process:ktl-librarian\n  at: "2026-09-01T05:00:00Z"\n'
BODY_A = "The Orders API serves order data. It reads 3 tables."
BODY_B = "The Orders API reads 3 tables and serves order data."
# Each character a reader cannot see is built from its code point, so this
# file holds none of them.
RLO = chr(0x202E)
ZWSP = chr(0x200B)


def prose(*args):
    return run([sys.executable, PROSE, *args])


def expect(status, text, what, *args):
    result = prose(*args)
    assert result.rc == status and text in result.out, (
        f"prose-check.py: this does not hold: {what} (wanted exit {status} and '{text}', got exit {result.rc} and: {result.out})"
    )


def plain(title, body, link):
    return (
        f"---\ntitle: {title}\n---\n\n# Guide\n\n{body}\n\n<!-- lokf:related -->\n[[{link}]]\n<!-- /lokf:related -->\n"
    )


def concept(frontmatter, body):
    return f"---\ntype: Service\nid: https://example.invalid/k/x/a\n{frontmatter}---\n\n{body}\n"


@pytest.fixture(scope="module")
def pc(tmp_path_factory):
    """The files the style and comparison cases read."""
    d = tmp_path_factory.mktemp("prose")
    # The style rules, one finding each, with the line it sits on.
    write(
        d / "bad.md",
        "# A page\n\nThe gate is strict - it checks every change.\n\nWe run the check in order to catch drift.\n\nThe gate reads every changed file in the bundle and then compares each one against the earlier version that the repository holds and then reports every difference that it finds to the person who asked for the check before it lets the change go any further.\n",
    )
    write(d / "long.md", (d / "bad.md").read_text().split("\n")[6] + "\n")
    # What the hand passes kept: a dash in frontmatter, a heading, a code
    # span, a fenced block, a quoted string, a short emphasised label and a table cell.
    write(
        d / "quiet.md",
        '---\ntitle: A - B\n---\n\n# A heading - with a dash\n\nRun `a - b` to subtract.\n\n```text\nx - y\n```\n\nThe button reads "X - Y" when it is ready.\n\nPick *Wrong - send back* when you are unsure.\n\n| Field | Value |\n| --- | --- |\n| a | - |\n',
    )
    # A figure of speech is a listed word, and the same letters inside another
    # word or a code span are not.
    write(
        d / "figure.md",
        "# A page\n\nThe fix lands in the next release.\n\nThe arm64 runner checks the wire-format, and `ships` is a code span.\n",
    )
    write(d / "literal.md", (d / "figure.md").read_text().split("\n")[4] + "\n")
    # A paragraph or a list item past 150 words is reported, and a table cell
    # is not: a cell has no room to split.
    write(d / "para.md", f"# A page\n\n{PARA}\n\n- {PARA}\n")
    write(d / "cell.md", f"| a | b |\n| --- | --- |\n| {PARA} | x |\n")
    # A character no reader sees is reported in code as well as in prose, and
    # a rewording that adds one is refused.
    write(d / "override.md", f"# A page\n\nRun `a{RLO}b` now.\n")
    write(d / "u-old.md", "# A page\n\nPlain text.\n")
    write(d / "u-new.md", f"# A page\n\nPlain{ZWSP} text.\n")
    # An indented code block is code, not prose: a figure or a dash in it is
    # no style finding, where the same words laid out as prose are read.
    write(d / "indent.md", "# A page\n\n    the fix lands - it ships every file in order to catch drift\n\nDone.\n")
    write(d / "indent-prose.md", "# A page\n\nthe fix lands - it ships every file in order to catch drift\n\nDone.\n")
    # A prose line that opens with an inline HTML tag is prose, the tag
    # masked; a line that is only HTML opens no prose and is left alone.
    write(d / "htmlled.md", "# A page\n\n<code>x</code> the fix lands in the next release.\n")
    write(d / "htmlblock.md", '# A page\n\n<img src="x.png" alt="a diagram of the gate">\n\nText.\n')
    # --before on plain files: wording may change, and nothing else.
    write(
        d / "p-old.md",
        plain(
            "Guide",
            "The gate checks 20 files, and [the guide](docs/guide.md) says why. It is strict.",
            "services/orders-api",
        ),
    )
    write(
        d / "p-new.md",
        plain(
            "Guide",
            "[The guide](docs/guide.md) says why the gate checks 20 files. The gate is strict.",
            "services/orders-api",
        ),
    )
    write(
        d / "p-num.md",
        plain(
            "Guide",
            "The gate checks 21 files, and [the guide](docs/guide.md) says why. It is strict.",
            "services/orders-api",
        ),
    )
    write(
        d / "p-link.md",
        plain(
            "Guide",
            "The gate checks 20 files, and [the guide](docs/other.md) says why. It is strict.",
            "services/orders-api",
        ),
    )
    write(
        d / "p-rel.md",
        plain(
            "Guide",
            "The gate checks 20 files, and [the guide](docs/guide.md) says why. It is strict.",
            "services/billing",
        ),
    )
    write(
        d / "p-fm.md",
        plain(
            "Guidebook",
            "The gate checks 20 files, and [the guide](docs/guide.md) says why. It is strict.",
            "services/orders-api",
        ),
    )
    # A number that begins a wrapped line is a fact, not a list number, and
    # laying a wrapped paragraph out on one line changes no fact.
    write(d / "w-old.md", "# A page\n\nThe first release came out in\n2024, and the next in 2025.\n")
    write(d / "w-new.md", "# A page\n\nThe first release came out in\n2023, and the next in 2025.\n")
    write(d / "w-flat.md", "# A page\n\nThe first release came out in 2024, and the next in 2025.\n")
    # A day or a month written out, and a text cut or grown by more than a
    # fifth, are notes for the reader, never a refusal.
    write(d / "d-old.md", "# A page\n\nThe job runs on Mondays in October, and it reads every file.\n")
    write(d / "d-new.md", "# A page\n\nThe job runs on Tuesdays in October, and it reads every file.\n")
    write(d / "s-old.md", f"# A page\n\n{PARA}\n\n{PARA}\n")
    write(d / "s-new.md", f"# A page\n\n{PARA}\n")
    # An inline HTML tag and a hard line break are layout a reader sees, so a
    # rewording keeps them.
    write(d / "t-old.md", "# A page\n\nThe value is <sub>n</sub> here, and it holds.\n")
    write(d / "t-new.md", "# A page\n\nThe value is <sup>n</sup> here, and it holds.\n")
    write(d / "hb-old.md", "# A page\n\nFirst half here  \nsecond half here now.\n")
    write(d / "hb-new.md", "# A page\n\nFirst half here\nsecond half here now.\n")
    return d


STYLE = [
    (1, "bad.md:3: dash:", "a dash used as punctuation is reported with its line", ["bad.md"]),
    (1, "bad.md:5: words:", "a stock phrase is reported with its line", ["bad.md"]),
    (1, "bad.md:7: long:", "a sentence over 40 words is reported with its line", ["bad.md"]),
    (0, "OK", "a higher --max-words lets that sentence pass", ["--max-words", "60", "long.md"]),
    (
        0,
        "OK",
        "a dash is left alone in frontmatter, a heading, code, a quotation, a short label and a table cell",
        ["quiet.md"],
    ),
    (1, 'figure.md:3: words: "lands"', "a figure of speech is reported with its line", ["figure.md"]),
    (0, "OK", "a figure's letters inside another word or a code span are left alone", ["literal.md"]),
    (
        1,
        "para.md:3: paragraph: 160 words in one paragraph",
        "a paragraph over 150 words is reported with its line",
        ["para.md"],
    ),
    (
        1,
        "para.md:5: paragraph: 160 words in one list item",
        "a list item over 150 words is reported as one",
        ["para.md"],
    ),
    (0, "OK", "a higher --max-paragraph lets them pass", ["--max-paragraph", "200", "para.md"]),
    (0, "OK", "a table cell is no paragraph, however long", ["cell.md"]),
    (
        1,
        "override.md:3: unseen: U+202E RIGHT-TO-LEFT OVERRIDE",
        "a right-to-left override is reported, inside a code span too",
        ["override.md"],
    ),
    (
        1,
        "u-new.md:3: unseen: U+200B ZERO WIDTH SPACE is new",
        "a rewording that adds a zero-width space is refused",
        ["--before", "u-old.md", "u-new.md"],
    ),
    (0, "OK", "an indented code block is not held to the style rules", ["indent.md"]),
    (1, "dash:", "the same words laid out as prose are read, so the skip is the indent's doing", ["indent-prose.md"]),
    (1, 'words: "lands"', "a prose line that opens with an inline tag is read, not skipped", ["htmlled.md"]),
    (0, "OK", "a line that is only HTML opens no prose and is left to the host", ["htmlblock.md"]),
    (0, "OK", "a change of wording alone passes", ["--before", "p-old.md", "p-new.md"]),
    (1, "digits:", "a changed number is reported", ["--before", "p-old.md", "p-num.md"]),
    (1, "link:", "a changed link target is reported", ["--before", "p-old.md", "p-link.md"]),
    (1, "related:", "a changed wikilink in the lokf:related region is reported", ["--before", "p-old.md", "p-rel.md"]),
    (1, "frontmatter:", "a changed frontmatter value is reported", ["--before", "p-old.md", "p-fm.md"]),
    (
        1,
        'digits: the number "2024" is gone',
        "a number that begins a wrapped line is a fact, and a change to it is caught",
        ["--before", "w-old.md", "w-new.md"],
    ),
    (0, "OK", "laying a wrapped paragraph out on one line changes no fact", ["--before", "w-old.md", "w-flat.md"]),
    (
        0,
        "OK: only the wording differs (1 file): 15 words, and the earlier text had 15",
        "a comparison that passes says how many words each version holds",
        ["--before", "p-old.md", "p-new.md"],
    ),
    (
        0,
        'date-word: the day or month "Tuesday" is new',
        "a changed day of the week is a note for the reader",
        ["--before", "d-old.md", "d-new.md"],
    ),
    (
        0,
        "shrink: 163 words, and the earlier text had 323",
        "a text cut by more than a fifth is a note for the reader",
        ["--max-paragraph", "400", "--before", "s-old.md", "s-new.md"],
    ),
    (
        0,
        "growth: 323 words, and the earlier text had 163",
        "a text grown by more than a fifth is a note for the reader",
        ["--max-paragraph", "400", "--before", "s-new.md", "s-old.md"],
    ),
    (1, "html:", "a changed inline HTML tag is reported", ["--before", "t-old.md", "t-new.md"]),
    (1, "hard-break:", "a dropped hard line break is reported", ["--before", "hb-old.md", "hb-new.md"]),
]


@pytest.mark.parametrize(("status", "text", "what", "args"), STYLE, ids=[w for _, _, w, _ in STYLE])
def test_style_and_comparison(pc, status, text, what, args):
    expect(status, text, what, *[pc / a if a.endswith(".md") else a for a in args])


# --before on concepts: a body may change only where no person vouched for
# it, and the frontmatter never. The confirmation is staged in each form the
# provenance gates read, and in one they cannot, which must fail closed.
CONCEPTS = [
    (0, "OK", "a reworded draft the librarian wrote passes, its frontmatter untouched", LIB, None),
    (
        1,
        "person:",
        "a reworded concept a person wrote is refused",
        'generated:\n  by: human:ada\n  at: "2026-09-08T14:05:00Z"\n',
        None,
    ),
    (
        1,
        "confirmed:",
        "a reworded concept is refused under a confirmation in a block list",
        LIB + 'verified:\n  - by: human:ada\n    at: "2026-09-08T14:00:00Z"\n',
        None,
    ),
    (
        1,
        "confirmed:",
        "a reworded concept is refused under a confirmation in a list at column zero",
        LIB + 'verified:\n- by: human:ada\n  at: "2026-09-08T14:00:00Z"\n',
        None,
    ),
    (
        1,
        "confirmed:",
        "a reworded concept is refused under a confirmation in a flow sequence",
        LIB
        + 'verified: [{ by: process:ktl-librarian, at: "2026-09-07T05:00:00Z" }, { by: human:ada, at: "2026-09-08T14:00:00Z" }]\n',
        None,
    ),
    (
        1,
        "confirmed:",
        "a reworded concept is refused under a confirmation in a bare mapping",
        LIB + 'verified:\n  by: human:ada\n  at: "2026-09-08T14:00:00Z"\n',
        None,
    ),
    (
        1,
        "unreadable:",
        "a reworded concept is refused when its confirmation is spelt so the gates cannot read it",
        LIB + 'verified:\n  - by: !!str human:ada\n    at: "2026-09-08T14:00:00Z"\n',
        None,
    ),
    (1, "retired:", "a reworded retired concept is refused", LIB + "status: deprecated\n", None),
    (1, "frontmatter:", "a moved generated.at is reported", LIB, LIB.replace("09-01T05", "10-02T09")),
    (0, "no generated record", "a reworded concept with no generated record passes with a note", "", None),
]


@pytest.mark.parametrize(("status", "text", "what", "before", "after"), CONCEPTS, ids=[w for _, _, w, _, _ in CONCEPTS])
def test_rewording_a_concept(tmp_path, status, text, what, before, after):
    write(tmp_path / "c-old.md", concept(before, BODY_A))
    write(tmp_path / "c-new.md", concept(before if after is None else after, BODY_B))
    expect(status, text, what, "--before", tmp_path / "c-old.md", tmp_path / "c-new.md")


@pytest.fixture
def prose_repo(tmp_path):
    """A committed bundle with one concept, reached through the knowledge_bundle link, which git stores as a link and cannot show a file through."""
    kx = tmp_path / ".lokf" / "knowledge" / "x"
    write(tmp_path / ".lokf" / "knowledge" / "index.md", "---\nbase_iri: https://example.invalid/k/\n---\n\n# Index\n")
    write(kx / "a.md", concept(LIB, BODY_A))
    (tmp_path / "knowledge_bundle").symlink_to(".lokf/knowledge")
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "bundle")
    return tmp_path


def test_a_reworded_concept_through_the_link_passes_against_head(prose_repo):
    write(prose_repo / ".lokf" / "knowledge" / "x" / "a.md", concept(LIB, BODY_B))
    expect(
        0,
        "OK",
        "a reworded concept reached through the knowledge_bundle link passes against HEAD",
        "--against",
        "HEAD",
        prose_repo / "knowledge_bundle" / "x" / "a.md",
    )


def test_a_changed_number_is_reported_against_head(prose_repo):
    write(prose_repo / ".lokf" / "knowledge" / "x" / "a.md", concept(LIB, BODY_B.replace("3 tables", "4 tables")))
    expect(
        1,
        "digits:",
        "a changed number is reported against HEAD",
        "--against",
        "HEAD",
        prose_repo / "knowledge_bundle" / "x" / "a.md",
    )


def test_a_file_git_does_not_hold_yet_cannot_be_proved_against_head(prose_repo):
    write(prose_repo / ".lokf" / "knowledge" / "x" / "new.md", concept(LIB, BODY_A))
    expect(
        1,
        "baseline:",
        "a file git does not hold yet cannot be proved against HEAD",
        "--against",
        "HEAD",
        prose_repo / ".lokf" / "knowledge" / "x" / "new.md",
    )


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    """One file for each verdict --bundle gives, in the order the skill's table gives."""
    k = tmp_path_factory.mktemp("prose-bundle") / "k"
    write(k / "index.md", "---\nbase_iri: https://example.invalid/k/\n---\n\n# Index\n")
    write(k / "log.md", "# Change Log\n\n## 2026-09-15\n\n* **A**: b - c.\n")
    write(k / "x" / "a-person.md", concept('generated:\n  by: human:ada\n  at: "2026-09-08T14:05:00Z"\n', BODY_A))
    write(
        k / "x" / "b-confirmed.md", concept(LIB + 'verified: [{ by: human:ada, at: "2026-09-08T14:00:00Z" }]\n', BODY_A)
    )
    write(k / "x" / "c-retired.md", concept(LIB + "status: deprecated\n", BODY_A))
    write(k / "x" / "d-unreadable.md", "---\ntype: Service\n\nThe block above never closes.\n")
    write(k / "x" / "e-unrecorded.md", concept("", BODY_A))
    write(k / "x" / "f-rewrite.md", concept(LIB, BODY_A))
    return k


@pytest.mark.parametrize(
    "want",
    [
        "index.md: skip: reserved file",
        "log.md: skip: reserved file",
        "a-person.md: skip: written by a person",
        "b-confirmed.md: skip: confirmed by a person",
        "c-retired.md: skip: retired",
        "d-unreadable.md: skip: frontmatter the script cannot read",
        "e-unrecorded.md: skip: no record of who wrote it",
        "f-rewrite.md: rewrite",
    ],
)
def test_bundle_verdicts(bundle, want):
    verdicts = prose("--bundle", bundle).out
    assert want in verdicts, f"prose-check.py --bundle did not give '{want}' on a bundle staged for it: {verdicts}"


def test_a_reserved_bundle_file_is_not_held_to_the_style_rules(bundle):
    expect(0, "OK", "a reserved bundle file is not held to the style rules", bundle / "log.md")


def test_no_argument_is_a_usage_error():
    expect(2, "usage", "no argument is a usage error")
