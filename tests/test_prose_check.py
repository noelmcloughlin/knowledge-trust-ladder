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
import time

import pytest

from conftest import REPO, Git, run, write

PROSE = REPO / "skills" / "ktl-prose" / "scripts" / "prose-check.py"
# 160 words in eight sentences: over the word limit, and inside the sentence count.
PARA = "Each check reads one file and compares it with the earlier version the repository holds before it reports what differs. " * 8
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
    # A band of readers: a sentence of 17 words, a paragraph of four
    # sentences and 60 words, and a paragraph of four short sentences.
    long_17 = "The librarian reads each changed file and writes one new concept for every source it finds today."
    write(d / "band-long.md", f"# A page\n\n{long_17}\n")
    write(d / "band-para.md", "# A page\n\n" + "The gate reads each file in the bundle and checks it against the earlier version. " * 4 + "\n")
    write(d / "band-four.md", "# A page\n\n" + "The gate reads each file. " * 4 + "\n")
    # A page that names its readers in its first paragraph, as rule 12 asks
    # of a retelling.
    opening = "# A page\n\nThis page is for {}. It says what the gate does.\n"
    write(d / "names-band.md", opening.format("readers aged 8 to 12") + f"\n{long_17}\n")
    write(d / "names-band-ok.md", opening.format("readers aged 8 to 12"))
    write(d / "names-dyslexia.md", opening.format("dyslexic readers"))
    write(d / "names-other.md", opening.format("readers aged 10 to 14"))
    # Words a band of readers is spared: a word of the trade and three Latin
    # abbreviations.
    write(d / "band-words.md", "# A page\n\nThe gate reads each file via the pen, etc. Use the short form, i.e. the label, vs the long one.\n")
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
        "OK: nothing the script reads differs (1 file): 15 words, and the earlier text had 15",
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
    (
        1,
        "band-long.md:3: long: 17 words in one sentence, and the limit is 15",
        "a sentence of 17 words is long for readers aged 8 to 12",
        ["--audience", "8-12", "band-long.md"],
    ),
    (0, "OK", "the same sentence passes for readers aged 13 to 18", ["--audience", "13-18", "band-long.md"]),
    (0, "OK", "and at the adult limits, with no band", ["band-long.md"]),
    (0, "OK", "--max-words sets its own limit over a band's", ["--audience", "8-12", "--max-words", "30", "band-long.md"]),
    (
        1,
        "band-para.md:3: paragraph: 60 words in one paragraph, and the limit is 50",
        "a paragraph of 60 words is long for readers aged 8 to 12",
        ["--audience", "8-12", "band-para.md"],
    ),
    (0, "OK", "the same paragraph passes for readers aged 13 to 18", ["--audience", "13-18", "band-para.md"]),
    (
        1,
        "band-four.md:3: sentences: 4 sentences in one paragraph, and the limit is 3",
        "a fourth sentence in a paragraph is reported for readers aged 8 to 12",
        ["--audience", "8-12", "band-four.md"],
    ),
    (0, "OK", "four sentences in a paragraph pass for readers aged 13 to 18", ["--audience", "13-18", "band-four.md"]),
    (
        0,
        "grade: Automated Readability Index",
        "a band notes the grade, and a page within the limits still passes",
        ["--audience", "13-18", "band-four.md"],
    ),
    (0, "the 13-18 target is 9 or under", "the grade note names the band's target", ["--audience", "13-18", "band-four.md"]),
    (0, "the dyslexia band sets no target", "the dyslexia band notes the grade with no target", ["--audience", "dyslexia", "band-four.md"]),
    (2, "invalid choice", "an unknown band is a usage error", ["--audience", "7-9", "band-long.md"]),
    (2, "run them apart", "a band with a comparison is a usage error", ["--audience", "8-12", "--before", "p-old.md", "p-new.md"]),
    (
        1,
        "names-band.md:5: long: 17 words in one sentence, and the limit is 15",
        "a page that names its readers is held to their band with no flag",
        ["names-band.md"],
    ),
    (
        0,
        "audience: the page says it is for readers aged 8 to 12, so the 8-12 limits apply",
        "a note says which band a page named",
        ["names-band-ok.md"],
    ),
    (
        1,
        "names-band-ok.md:3: audience: the page says it is for readers aged 8 to 12, and --audience asked for 13-18",
        "a flag that asks for another band than the page names is a finding",
        ["--audience", "13-18", "names-band-ok.md"],
    ),
    (0, "so the dyslexia limits apply", "a page for dyslexic readers names its band too", ["names-dyslexia.md"]),
    (
        0,
        "which no band covers, so the adult limits apply",
        "ages that match no band keep the adult limits",
        ["names-other.md"],
    ),
    (1, 'band-words.md:3: words: "via"', "a word of the trade is reported for a band of readers", ["--audience", "8-12", "band-words.md"]),
    (1, 'words: "etc."', "a Latin abbreviation is reported for a band of readers", ["--audience", "13-18", "band-words.md"]),
    (1, 'words: "i.e."', "and so is another", ["--audience", "dyslexia", "band-words.md"]),
    (0, "OK", "and none of them at the adult limits", ["band-words.md"]),
]


@pytest.mark.parametrize(("status", "text", "what", "args"), STYLE, ids=[w for _, _, w, _ in STYLE])
def test_style_and_comparison(pc, status, text, what, args):
    expect(status, text, what, *[pc / a if a.endswith(".md") else a for a in args])


TURNED = [
    (1, 'opposite: "enabled" became "disabled"', "Pushes to main are enabled by the ruleset.", "Pushes to main are disabled by the ruleset."),
    (1, 'opposite: "at least" became "at most"', "A pull request needs at least two reviewers.", "A pull request needs at most two reviewers."),
    (1, 'opposite: "must" became "may"', "A person must sign the commit.", "A person may sign the commit."),
    (1, 'opposite: "after" became "before"', "The sync runs after the release.", "The sync runs before the release."),
    (1, 'opposite: "required" became "optional"', "The input is required.", "The input is optional."),
    (1, "negative: a sentence that otherwise stayed lost its negative", "The agent does not push the tag.", "The agent does push the tag."),
    (1, "negative: a sentence that otherwise stayed gained a negative", "The agent pushes the tag.", "The agent never pushes the tag."),
    (0, 'new.md:1: opposite: "after" became "before"', "Run lint after the build step.", "Run the build step before lint."),
    (0, "new.md:1: negative: a sentence that otherwise stayed lost its negative", "The gate does not read the old file.", "The gate skips the old file."),
    (0, "sentence-gone: few words of this sentence came through", "The gate reads commits. A person must sign each confirmation.", "The gate reads commits."),
    (0, "OK", "It does not change the file.", "It changes nothing in the file."),
    (0, "OK", "A run with no token stops.", "A run without a token stops."),
    (0, "OK", "It can't read the file.", "It cannot read the file."),
    (0, "OK", "The gate reads every commit. It runs on merge.", "The gate runs on merge. It reads every commit."),
    # A negating prefix, a count in words, and two runs of words that changed places.
    (1, 'opposite: "confirmed" became "unconfirmed"', "The report lists each confirmed concept.", "The report lists each unconfirmed concept."),
    (1, 'opposite: "valid" became "invalid"', "The pen writes the patch when the frontmatter is valid.", "The pen writes the patch when the frontmatter is invalid."),
    (1, 'number-word: "three" became "four"', "The sidecar installs three workflows.", "The sidecar installs four workflows."),
    (1, 'order: "librarian" and "curator" changed places', "The librarian hands the change to the curator.", "The curator hands the change to the librarian."),
    (1, 'order: "build fails" and "lock is stale" changed places', "The build fails because the lock is stale.", "The lock is stale because the build fails."),
    (1, 'order: "template" and "host" changed places', "The script copies each file from the template to the host.", "The script copies each file from the host to the template."),
    # A number or a code span that changed places with one in another sentence.
    (1, "swap: the number 40 and the number 150 changed places", "Split a sentence past 40 words. Split a paragraph past 150 words.", "Split a sentence past 150 words. Split a paragraph past 40 words."),
    (1, "swap: the code span uv and the code span npm changed places", "`uv` installs the packages. `npm` builds the site.", "`npm` installs the packages. `uv` builds the site."),
    # A list item is a sentence of its own, so a swap between two items shows.
    (1, 'opposite: "required" became "optional"', "- `A_TOKEN` is required.\n- `B_TOKEN` is optional.", "- `A_TOKEN` is optional.\n- `B_TOKEN` is required."),
    # An earlier sentence that shares as many words must not take the changed one's place.
    (
        1,
        'opposite: "enabled" became "disabled"',
        "The release workflow turns signing on after the gate checks each confirmation. Signing is enabled in the release workflow.",
        "The release workflow turns signing on after the gate checks each confirmation. Signing is disabled in the release workflow.",
    ),
    # Notes, each with its line: a reader decides.
    (0, 'new.md:1: strength: "may" left a sentence that otherwise stayed', "The check may fail behind a proxy.", "The check fails behind a proxy."),
    (0, 'new.md:1: strength: "only" left a sentence that otherwise stayed', "The token reads only this repository.", "The token reads this repository."),
    (0, 'new.md:1: strength: "all" left a sentence that otherwise stayed', "All workflows read the runner variable.", "Some workflows read the runner variable."),
    (0, 'new.md:1: word: "curator" became "librarian" once', "The curator confirms each concept against its source.", "The librarian confirms each concept against its source."),
    (0, 'new.md:1: word: "weekly" became "daily" once', "The librarian workflow runs weekly on the default branch.", "The librarian workflow runs daily on the default branch."),
    (0, "new.md:1: negative: a sentence that otherwise stayed has 1 negative, and had 2", "The job never runs without a token.", "The job never runs with a token."),
    (0, "new.md:1: order: the same words stand in a new order", "The gate only checks signed commits.", "Only the gate checks signed commits."),
    (0, "new.md:1: order: the same words stand in a new order", "The README and the docs name it.", "The docs and the README name it."),
    (0, "page-words: words gone from the page: logs, account; words new on the page: none", "The gate refuses a push with no signature, and it logs the account that pushed.", "The gate refuses a push with no signature."),
    (0, "code: code spans new on the page: `npm`", "Run uv, then build the site.", "Run uv, then build the site with `npm`."),
]


@pytest.mark.parametrize(("status", "text", "old", "new"), TURNED, ids=[f"{o} -> {n}" for _, _, o, n in TURNED])
def test_a_sentence_that_turned_over(tmp_path, status, text, old, new):
    """Nothing but the wording differs, so only comparing sentence with sentence can show that the claim reversed."""
    write(tmp_path / "old.md", f"{old}\n")
    write(tmp_path / "new.md", f"{new}\n")
    expect(status, text, f"{old} -> {new}", "--before", tmp_path / "old.md", tmp_path / "new.md")


def test_the_ok_line_claims_only_what_the_script_read(tmp_path):
    """It once said that only the wording differs, of a text whose meaning it cannot read."""
    write(tmp_path / "old.md", "The gate reads every commit.\n")
    write(tmp_path / "new.md", "Every commit is read by the gate.\n")
    result = prose("--before", tmp_path / "old.md", tmp_path / "new.md")
    assert result.rc == 0 and "nothing the script reads differs" in result.out and "only the wording" not in result.out, result.out


def test_a_word_cut_by_rule_10_gives_no_note(tmp_path):
    """`at all` is on the list of words to cut, so its `all` is no word of strength."""
    write(tmp_path / "old.md", "The gate reads no file at all.\n")
    write(tmp_path / "new.md", "The gate reads no file.\n")
    result = prose("--before", tmp_path / "old.md", tmp_path / "new.md")
    assert result.rc == 0 and "strength" not in result.out and "page-words" not in result.out, result.out


def test_a_word_of_strength_is_noted_on_the_page_only_where_no_sentence_places_it(tmp_path):
    write(tmp_path / "old.md", "The token reads only this repository.\n\nThe gate runs on each pull request.\n")
    write(tmp_path / "new.md", "The token reads this repository.\n\nThe gate runs on each pull request.\n")
    result = prose("--before", tmp_path / "old.md", tmp_path / "new.md")
    assert result.rc == 0 and 'new.md:1: strength: "only" left' in result.out and '"only" appears' not in result.out, result.out


def test_no_control_character_reaches_the_terminal(tmp_path):
    """A finding quotes the text, and an escape sequence in it could redraw a terminal or forge a line of a CI log."""
    write(tmp_path / "page.md", f"The gate {chr(0x1B)}[31mfailed{chr(0x1B)}[0m - it stops the merge here.\n")
    result = prose(tmp_path / "page.md")
    assert result.rc == 1 and "<U+001B>[31mfailed" in result.out and chr(0x1B) not in result.out, result.out


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
    (
        0,
        "OK",
        "a reworded concept passes when an exclusions entry says who left a material out",
        LIB + "exclusions:\n  - resource: a\n    reason: b\n    by: process:ktl-librarian\n",
        None,
    ),
    (
        0,
        "OK",
        "a reworded concept passes when an exclusions list at column zero is followed by another key",
        LIB + "exclusions:\n- by: human:ada\n  resource: a\n  reason: b\nstatus: draft\n",
        None,
    ),
    (
        1,
        "unreadable:",
        "a reworded concept is refused when a by below the exclusions list is no event the script can read",
        LIB + "exclusions:\n  - resource: a\n    reason: b\nother:\n  by: human:ada\n",
        None,
    ),
    (
        1,
        "unreadable:",
        "a reworded concept is refused under a confirmation under an alias of another event",
        LIB + 'revised: &who { by: human:ada, at: "2026-09-08T14:00:00Z" }\nverified:\n  - *who\n',
        None,
    ),
    (
        1,
        "unreadable:",
        "a reworded concept is refused under a confirmation that merges in another event",
        LIB + 'revised: &who { by: human:ada, at: "2026-09-08T14:00:00Z" }\nverified:\n  - <<: *who\n',
        None,
    ),
    (
        1,
        "unreadable:",
        "a reworded concept is refused under a confirmation under a quoted key",
        LIB + '"verified": [{ at: "2026-09-08T14:00:00Z", by: human:ada }]\n',
        None,
    ),
    (
        1,
        "unreadable:",
        "a reworded concept is refused under a confirmation under a quoted key in a block list",
        LIB + '"verified":\n  - { at: "2026-09-08T14:00:00Z", by: human:ada }\n',
        None,
    ),
    (
        1,
        "confirmed:",
        "a reworded concept is refused under a confirmation in a flow sequence across lines, with by second",
        LIB + 'verified: [\n  { at: "2026-09-08T14:00:00Z", by: human:ada }\n]\n',
        None,
    ),
    (
        1,
        "unreadable:",
        "a reworded concept is refused under a confirmation under an explicit key",
        LIB + '? verified\n: - by: human:ada\n    at: "2026-09-08T14:00:00Z"\n',
        None,
    ),
    (
        1,
        "unreadable:",
        "a reworded concept is refused under a confirmation whose by key is escaped",
        LIB + 'verified:\n  - "b\\x79": human:ada\n    at: "2026-09-08T14:00:00Z"\n',
        None,
    ),
    (
        1,
        "unreadable:",
        "a reworded concept is refused when an escaped actor would read as a person",
        LIB + 'verified:\n  - by: "\\x68uman:ada/x"\n    at: "2026-09-08T14:00:00Z"\n',
        None,
    ),
    (
        1,
        "unreadable:",
        "a reworded concept is refused under a merge key at the top level",
        LIB + '<<: { verified: [{ at: "2026-09-08T14:00:00Z", by: human:ada }] }\n',
        None,
    ),
    (
        1,
        "unreadable:",
        "a reworded concept is refused when a comment hides the bracket a reader looks for",
        LIB + 'verified: [ # ]\n  { by: human:ada, at: "2026-09-08T14:00:00Z" }\n]\n',
        None,
    ),
    (
        1,
        "unreadable:",
        "a reworded concept is refused when a line break no reader sees holds an event",
        LIB + 'note: x' + chr(0x2028) + 'verified:' + chr(0x2028) + '  - by: human:ada\n',
        None,
    ),
    (
        1,
        "confirmed:",
        "a reworded concept is refused under a confirmation in an item whose dash stands alone",
        LIB + 'verified:\n  -\n    by: human:ada\n    at: "2026-09-08T14:00:00Z"\n  -\n    by: process:x\n    at: "2026-09-08T14:00:00Z"\n',
        None,
    ),
    (
        1,
        "edited:",
        "a reworded concept is refused when a person revised it",
        LIB + 'revised:\n  by: human:ada\n  at: "2026-09-08T14:00:00Z"\n',
        None,
    ),
    (
        0,
        "OK",
        "a reworded concept passes when a process revised it",
        LIB + 'revised:\n  by: process:ktl-librarian\n  at: "2026-09-08T14:00:00Z"\n',
        None,
    ),
    (
        1,
        "refuted:",
        "a reworded concept is refused when it stands refuted",
        LIB + 'refuted:\n  - by: process:x\n    at: "2026-09-08T14:00:00Z"\n    reason: wrong\n',
        None,
    ),
    (
        1,
        "unreadable:",
        "a reworded concept is refused when a by sits under a key no reader knows",
        LIB + 'x_extra:\n  by: human:ada\n',
        None,
    ),
    (
        0,
        "OK",
        "a reworded concept passes when a glob in a description looks like an alias",
        LIB + 'description: checks *.md, *.py\n',
        None,
    ),
    (
        0,
        "OK",
        "a reworded concept passes when a comment item opens an event",
        LIB + 'verified:\n  - # the librarian\n    by: process:x\n    at: "2026-09-08T14:00:00Z"\n',
        None,
    ),
    (
        0,
        "OK",
        "a reworded concept passes when verified is null",
        LIB + 'verified: null\n',
        None,
    ),
    (
        0,
        "OK",
        "a reworded concept passes when an exclusions reason holds an ampersand",
        LIB + "exclusions:\n  - resource: a\n    reason: the &amp; entity\n    by: process:ktl-librarian\n",
        None,
    ),
    (
        1,
        "retired:",
        "a reworded retired concept is refused when its status key is quoted",
        LIB + '"status": deprecated\n',
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
    write(k / "x" / "g-edited.md", concept(LIB + 'revised:\n  by: human:ada\n  at: "2026-09-08T14:00:00Z"\n', BODY_A))
    write(k / "x" / "h-refuted.md", concept(LIB + 'refuted:\n  - by: human:ada\n    at: "2026-09-08T14:00:00Z"\n    reason: wrong\n', BODY_A))
    write(k / "x" / "i-indented.md", "---\n  type: Service\n  verified:\n    - by: human:ada\n---\n\nBody.\n")
    write(k / "x" / "j-prefixed.md", "note\n---\ntype: Service\n---\n\nBody.\n")
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
        "g-edited.md: skip: edited by a person",
        "h-refuted.md: skip: refuted",
        "i-indented.md: skip: frontmatter the script cannot read",
        "j-prefixed.md: skip: frontmatter the script cannot read",
    ],
)
def test_bundle_verdicts(bundle, want):
    verdicts = prose("--bundle", bundle).out
    assert want in verdicts, f"prose-check.py --bundle did not give '{want}' on a bundle staged for it: {verdicts}"


def test_a_bundle_with_no_declared_readers_says_so(bundle):
    expect(0, "audience: none declared\nOK:", "a bundle that declares no readers says so before its tally", "--bundle", bundle)


POLICY = '---\ntype: Policy\ntitle: Knowledge curation\ngenerated:\n  by: human:ada\n  at: "2026-09-08T14:05:00Z"\n---\n\n# Younger readers\n\n{line}\n'


@pytest.mark.parametrize(
    ("policy", "description", "want", "what"),
    [
        ("Younger readers: 8-12", None, "audience: 8-12 (policies/knowledge-curation.md)", "the curation policy declares a band"),
        ("Younger readers: 8-12, 13-18", None, "audience: 8-12, 13-18 (policies/knowledge-curation.md)", "and may declare two"),
        ("Younger readers: no", None, "audience: none declared (policies/knowledge-curation.md says no)", "or none"),
        ("Younger readers: kids", None, "names 'kids', which is no band of age", "a value that is no band declares nothing"),
        (None, "A bundle for readers aged 13 to 18.", "audience: 13-18 (the description in index.md)", "with no policy line, the index description may declare a band"),
        ("Younger readers: no", "A bundle for readers aged 13 to 18.", "says no", "the policy line decides over the description"),
    ],
)
def test_a_bundle_declares_its_younger_readers(tmp_path, policy, description, want, what):
    k = tmp_path / "k"
    front = f"base_iri: https://example.invalid/k/\n" + (f"description: {description}\n" if description else "")
    write(k / "index.md", f"---\n{front}---\n\n# Index\n")
    write(k / "x" / "f-rewrite.md", concept(LIB, BODY_A))
    if policy:
        write(k / "policies" / "knowledge-curation.md", POLICY.format(line=policy))
    expect(0, want, what, "--bundle", k)


def test_a_reserved_bundle_file_is_not_held_to_the_style_rules(bundle):
    expect(0, "OK", "a reserved bundle file is not held to the style rules", bundle / "log.md")


def test_no_argument_is_a_usage_error():
    expect(2, "usage", "no argument is a usage error")


def test_the_vocabulary_note_names_the_words_the_word_book_lacks(tmp_path):
    write(tmp_path / "v.md", "# A page\n\nThe curator confirms the concept. The curators read it.\n")
    out = prose("--audience", "13-18", tmp_path / "v.md").out
    want = "vocabulary: 3 of 9 words are outside the VOA Learning English word book, most often: curator (2), concept (1)"
    assert want in out, f"prose-check.py did not note the words the word book lacks: {out}"


def test_the_vocabulary_note_leaves_out_file_names_and_hyphenated_names(tmp_path):
    write(tmp_path / "f.md", "# A page\n\nRead [docs/install.md](docs/install.md) to set ktl-xyzzy up today.\n")
    out = prose("--audience", "13-18", tmp_path / "f.md").out
    assert ": vocabulary: " not in out, f"prose-check.py counted a piece of a file name as a hard word: {out}"


def test_the_vocabulary_note_counts_the_forms_of_a_word_together(tmp_path):
    write(tmp_path / "g.md", "# A page\n\nThe file holds the files. The gate checked them, and it checks them again.\n")
    out = prose("--audience", "13-18", tmp_path / "g.md").out
    assert "most often: file (2), checked (2), gate (1)" in out, f"prose-check.py counted the forms of one word apart: {out}"


def test_the_vocabulary_note_knows_inflected_and_irregular_forms(tmp_path):
    write(tmp_path / "k.md", "# A page\n\nThe children were running to the stores, and they did not stop.\n")
    out = prose("--audience", "13-18", tmp_path / "k.md").out
    assert ": vocabulary: " not in out, f"prose-check.py took a plain form for a hard word: {out}"


def test_no_band_means_no_vocabulary_note(tmp_path):
    write(tmp_path / "v.md", "# A page\n\nThe curator confirms the concept.\n")
    out = prose(tmp_path / "v.md").out
    assert ": vocabulary: " not in out and ": grade: " not in out, f"prose-check.py noted a grade or words with no band: {out}"


def test_the_word_book_credits_its_source():
    text = (PROSE.parent.parent / "assets" / "voa-word-book.txt").read_text(encoding="ascii")
    assert "learningenglish.voanews.com" in text and "public domain" in text, "voa-word-book.txt lost its credit lines"


# --derived-from: a retelling may say less than the text it retells, and
# never more. Outside a bundle it links the adult file in its first
# paragraph; in a bundle it also names the adult concept under derivedFrom.
ADULT = """# The gate

The gate checks 20 files, and [the guide](docs/guide.md) says why. It MUST run on every change.

```sh
just check
```

## Details

The gate reads `config.yaml` and reports "drift" when it finds it. It runs 3 times a day.
"""
YOUNG = """# What does the gate do?

This page is for readers aged 13 to 18. It retells [the full page](adult.md) in shorter words. The full page has every detail.

The gate checks 20 files. It must run on every change.
"""
PEN = """---
type: GlossaryTerm
id: https://example.invalid/k/glossary/the-pen
title: The pen
{events}---

# Overview

The pen writes 3 kinds of change, and refuses a `human:` actor.
"""
PEN_YOUNG = """---
type: GlossaryTerm
id: https://example.invalid/k/young-readers/the-pen
title: The pen, for readers aged 13 to 18
{derived}tags:
- {tag}
{events}---

This page is for readers aged 13 to 18. It retells [[the-pen]] in shorter words. The full page has every detail.

The pen writes 3 kinds of change. A [[knowledge-bundle]] is the folder it writes.
"""
DERIVED_FROM = "derivedFrom:\n- https://example.invalid/k/glossary/the-pen\n"
LIB_LATER = LIB.replace("09-01T05", "09-02T05")


@pytest.fixture(scope="module")
def retold(tmp_path_factory):
    """An adult page and its retellings outside a bundle, and an adult concept and its retellings inside one."""
    d = tmp_path_factory.mktemp("retold")
    write(d / "adult.md", ADULT)
    write(d / "young.md", YOUNG)
    write(d / "young-number.md", YOUNG.replace("20 files", "25 files"))
    write(d / "young-link.md", YOUNG + "\nRead [another page](docs/other.md) too.\n")
    write(d / "young-code.md", YOUNG + "\nIt reads `other.yaml` too.\n")
    write(d / "young-quote.md", YOUNG + '\nIt says "safe" when it passes.\n')
    write(d / "young-nolink.md", YOUNG.replace("[the full page](adult.md)", "the full page"))
    write(d / "young-openq.md", YOUNG + "\n## Open Questions\n")
    write(d / "young-should.md", YOUNG.replace("It must run", "It should run"))
    write(d / "young-caps.md", YOUNG.replace("It must run", "It MUST run"))
    write(d / "young-noaud.md", YOUNG.replace("This page is for readers aged 13 to 18. ", ""))
    k = d / "k"
    write(k / "index.md", "---\nbase_iri: https://example.invalid/k/\n---\n\n# Index\n")
    write(k / "glossary" / "the-pen.md", PEN.format(events=LIB))
    young = k / "young-readers"
    write(young / "the-pen.md", PEN_YOUNG.format(derived=DERIVED_FROM, tag="audience-13-18", events=LIB_LATER))
    write(young / "no-derived.md", PEN_YOUNG.format(derived="", tag="audience-13-18", events=LIB_LATER))
    write(young / "no-tag.md", PEN_YOUNG.format(derived=DERIVED_FROM, tag="glossary", events=LIB_LATER))
    confirmed = LIB_LATER + 'verified:\n  - by: human:ada\n    at: "2026-09-08T14:00:00Z"\n'
    write(young / "confirmed.md", PEN_YOUNG.format(derived=DERIVED_FROM, tag="audience-13-18", events=confirmed))
    return d


RETOLD = [
    (
        0,
        "OK: the retelling holds nothing the adult text does not (1 file)",
        "a retelling that says less, under another heading and with must for MUST, passes",
        ["adult.md", "young.md"],
    ),
    (0, 'digits: 1 number of the adult text left out: "3"', "a number left out is a note", ["adult.md", "young.md"]),
    (0, "fence: 1 fenced block of the adult text left out", "a fenced block left out is a note", ["adult.md", "young.md"]),
    (0, "link: 1 link target of the adult text left out", "a link left out is a note", ["adult.md", "young.md"]),
    (1, 'digits: the number "25" is not in the adult text', "a new number is a finding", ["adult.md", "young-number.md"]),
    (1, 'link: the link target "docs/other.md" is not in the adult text', "a new link is a finding", ["adult.md", "young-link.md"]),
    (1, 'code: the code span "other.yaml" is not in the adult text', "a new code span is a finding", ["adult.md", "young-code.md"]),
    (1, 'quote: the quoted text "safe" is not in the adult text', "a new quotation is a finding", ["adult.md", "young-quote.md"]),
    (
        1,
        "derived-from: the first paragraph does not link adult.md",
        "a retelling that does not link the page it retells is a finding",
        ["adult.md", "young-nolink.md"],
    ),
    (1, "open-questions:", "a misspelt open questions heading is a finding", ["adult.md", "young-openq.md"]),
    (
        0,
        'strength: "should" appears once, and the adult text never has it',
        "a should the adult text never has is a note",
        ["adult.md", "young-should.md"],
    ),
    (0, 'rfc2119: "MUST" is in capitals', "a keyword left in capitals is a note", ["adult.md", "young-caps.md"]),
    (0, "audience: the first paragraph names no readers", "a retelling that names no readers is a note", ["adult.md", "young-noaud.md"]),
    (0, "OK", "a retelling in a bundle that names its concept passes", ["k/glossary/the-pen.md", "k/young-readers/the-pen.md"]),
    (
        0,
        '"knowledge-bundle" is a concept the adult text does not link',
        "a link to another concept of the bundle is a note, for a term the retelling explains",
        ["k/glossary/the-pen.md", "k/young-readers/the-pen.md"],
    ),
    (
        1,
        "derived-from: derivedFrom does not name https://example.invalid/k/glossary/the-pen",
        "a retelling in a bundle that does not name its concept under derivedFrom is a finding",
        ["k/glossary/the-pen.md", "k/young-readers/no-derived.md"],
    ),
    (
        0,
        "the tags hold no audience-13-18",
        "a band the tags do not carry is a note",
        ["k/glossary/the-pen.md", "k/young-readers/no-tag.md"],
    ),
    (
        0,
        "confirmed: confirmed by a person (human:ada); this check changes nothing",
        "a retelling a person confirmed is checked, and the confirmation is a note",
        ["k/glossary/the-pen.md", "k/young-readers/confirmed.md"],
    ),
]


@pytest.mark.parametrize(("status", "text", "what", "files"), RETOLD, ids=[w for _, _, w, _ in RETOLD])
def test_a_retelling_says_less_and_never_more(retold, status, text, what, files):
    expect(status, text, what, "--derived-from", *[retold / f for f in files])


def test_derived_from_takes_no_file(retold):
    expect(2, "takes no FILE", "--derived-from takes no FILE", "--derived-from", retold / "adult.md", retold / "young.md", retold / "young-link.md")


def test_a_band_with_derived_from_is_a_usage_error(retold):
    expect(2, "run them apart", "--audience with --derived-from is a usage error", "--audience", "8-12", "--derived-from", retold / "adult.md", retold / "young.md")


# A script's prose: its whole-line `#` comments, and in Python its docstrings,
# read under the same rules. Code, a directive, a PEP 723 block and a heredoc
# body are not prose, and are left alone.
FILLER = "The gate reads each changed file and compares it with the earlier version the repository holds before it reports a difference. "


@pytest.fixture(scope="module")
def scripts(tmp_path_factory):
    d = tmp_path_factory.mktemp("scripts")
    write(d / "para.sh", "#!/usr/bin/env bash\n# " + (FILLER * 8).strip() + "\nset -eu\n")
    write(d / "split.sh", "#!/usr/bin/env bash\n# " + (FILLER * 4).strip() + "\n#\n# " + (FILLER * 4).strip() + "\nset -eu\n")
    write(
        d / "quiet.sh",
        "#!/bin/bash -\n# shellcheck disable=SC2016 # a - b\n# /// script\n# dependencies = [\"a - b\"]\n# ///\ncat <<'EOF'\n# x - y\nEOF\necho 'a - b'  # trailing - here\n",
    )
    write(d / "items.sh", "# Steps:\n#   - the fix lands\n#     in the release\n#   - the key - is read\n")
    write(
        d / "doc.py",
        '"""A module - with a dash."""\n\nFORMAT = """\na - b\n"""\n\n\ndef f():\n    """Say what happens: the key lands.\n\n    - a - b\n    """\n    return 1  # the fix lands\n',
    )
    write(d / "flow.yaml", "name: x\n# The job - runs.\njobs:\n  a:\n    run: |\n      # inside - a comment\n      python - <<'PY'\n      # data - not read\n      PY\n")
    write(d / "justfile", '# Recipes - for the bundle.\nbundle := "knowledge"\n\nlokf-validate:\n    #!/usr/bin/env bash\n    uv run lokf validate\n')
    write(d / "sentences.md", "# A page\n\n" + "It reads. " * 9 + "\n\n- " + "It reads. " * 9 + "\n")
    write(d / "words.md", "# A page\n\nThe pen refuses it outright. Nothing in the bundle changes at all.\n")
    # A comment's layout: a usage line, a command under it, and a table of
    # options whose rows run to 60 words together and to 25 each.
    write(
        d / "table.sh",
        "#!/usr/bin/env bash\n"
        "# Usage: tool.sh [--root <dir>] [--dry-run] [--keep] <patch>\n"
        "#        tool.sh --format | grep - x\n"
        "#   --root <dir>   the folder the run reads its files from and writes its\n"
        "#                  report into, by default two levels above this script\n"
        "#   --dry-run      report every finding and what the run would write, and\n"
        "#                  write nothing to the bundle or to any other folder\n"
        "#   --keep         leave the patch file in place once the run applied it,\n"
        "#                  so a person can read it again after the run\n"
        "# The run then reads the patch file and writes each change it names.\n"
        "set -eu\n",
    )
    # A row's own text is still read: a dash in one, and a listed word in a
    # row whose name is too wide to leave a gap.
    write(
        d / "rows.sh",
        "# Inputs:\n"
        "#   AGENT_CLI           the command - it runs the agent\n"
        "#   KNOWLEDGE_SKIP_QUIET optional: the fix lands when nothing waits\n",
    )
    # A command after a colon or an empty line is not read, and a line that
    # starts as a sentence does is.
    write(
        d / "command.yaml",
        "# Run this once:\n#   gh api -X POST repos/o/r/pages - f\n#\n#   The fix lands in the next release.\nname: x\n",
    )
    # A list item's paragraphs after an empty line, and an item numbered with a
    # letter, keep their prose.
    write(
        d / "items.py",
        '"""Checks.\n\n1. a build resolves the members.\n\n   The fix lands in the lock.\n2a. a bundle that releases no zip\n   joins - by its site.\n"""\n',
    )
    # A sentence that starts with a name in lowercase is a sentence of its own.
    write(
        d / "names.md",
        "# A page\n\n"
        + "The report counts the tracked files that no concept names and lists them under each folder it reads. " * 2
        + "ktl-docent reads the bullets alone and chooses a concept from them before it opens any file at all."
        + " .lokf/ holds the bundle.\n",
    )
    write(
        d / "spans.md",
        "# A page\n\nThe grade is 4.71 x letters - 21.43, and `run` ends its options as in cmd -- <args> here."
        " The gate stops at all of them, and at all times.\n",
    )
    return d


SCRIPTS = [
    (1, "para.sh:2: paragraph: 168 words in one paragraph", "a comment block over 150 words is reported, on the line it starts", ["para.sh"]),
    (0, "OK", "an empty comment line splits a block", ["split.sh"]),
    (0, "OK", "a shebang, a shellcheck directive, a PEP 723 block, a heredoc body and code are left alone", ["quiet.sh"]),
    (1, 'items.sh:2: words: "lands"', "a list in a comment is read as items", ["items.sh"]),
    (1, "items.sh:4: dash:", "and a dash in an item is reported with its line", ["items.sh"]),
    (1, "doc.py:1: dash:", "a module docstring is read", ["doc.py"]),
    (1, 'doc.py:9: words: "lands"', "a function docstring is read, on its own lines", ["doc.py"]),
    (1, "doc.py:11: dash:", "a list in a docstring is read", ["doc.py"]),
    (1, "flow.yaml:2: dash:", "a workflow's comment is read", ["flow.yaml"]),
    (1, "flow.yaml:6: dash:", "and so is a comment inside a run block", ["flow.yaml"]),
    (1, "justfile:1: dash:", "a justfile's comment is read, and a recipe's shebang is not", ["justfile"]),
    (1, "sentences.md:3: sentences: 9 sentences in one paragraph, and the limit is 8", "a paragraph over eight sentences is reported", ["sentences.md"]),
    (0, "OK", "a higher --max-sentences lets it pass, and a list item has no count", ["--max-sentences", "12", "sentences.md"]),
    (1, 'words.md:3: words: "outright"', "an intensifier that names no comparison is reported", ["words.md"]),
    (1, 'words.md:3: words: "at all"', "and so is the tail of a negative", ["words.md"]),
    (0, "OK", "a usage line, a command under it and a table of options are not one long sentence", ["table.sh"]),
    (1, "rows.sh:2: dash:", "a row's own text is still read", ["rows.sh"]),
    (1, 'rows.sh:3: words: "lands"', "and so is a row whose name leaves no gap", ["rows.sh"]),
    (1, 'command.yaml:4: words: "lands"', "a command is not read, and a line that starts as a sentence is", ["command.yaml"]),
    (1, 'items.py:5: words: "lands"', "a list item's paragraph after an empty line is read", ["items.py"]),
    (1, "items.py:7: dash:", "and so is the continuation of an item numbered with a letter", ["items.py"]),
    (1, 'names.md:3: words: "at all"', "a sentence that starts with a lowercase name is a sentence of its own", ["names.md"]),
    (0, "OK", "a minus, an end of options and \"at all\" before a noun are not reported", ["spans.md"]),
]


@pytest.mark.parametrize(("status", "text", "what", "args"), SCRIPTS, ids=[w for _, _, w, _ in SCRIPTS])
def test_scripts_and_sentences(scripts, status, text, what, args):
    expect(status, text, what, *[scripts / a if "." in a or a == "justfile" else a for a in args])


def test_code_data_and_a_trailing_comment_are_not_read(scripts):
    out = prose(scripts / "doc.py", scripts / "flow.yaml", scripts / "quiet.sh").out
    for line in ("doc.py:4:", "doc.py:13:", "flow.yaml:8:", "quiet.sh:"):
        assert line not in out, f"prose-check.py read code, data or a trailing comment as prose: {out}"


def test_layout_findings_name_only_their_own_lines(scripts):
    out = prose(scripts / "table.sh", scripts / "command.yaml", scripts / "names.md").out
    for line in ("table.sh:", "command.yaml:2:", "names.md:3: long:"):
        assert line not in out, f"prose-check.py read a command or a table as prose, or ran two sentences together: {out}"


@pytest.fixture
def script_repo(tmp_path):
    """A committed script with comments, a docstring and quoted strings in its code."""
    write(
        tmp_path / "tool.py",
        '"""Read the bundle - and report."""\n\n# The gate reads every file it is given.\nNAME = "a - b"\nprint("it reads", NAME)\n',
    )
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "tool")
    return tmp_path


def test_a_script_is_compared_as_its_comments_against_head(script_repo):
    write(
        script_repo / "tool.py",
        '"""Read the bundle, and report."""\n\n# The gate reads each file it is given.\n#\n# It reads no other.\nNAME = "a - b"\nprint("it reads", NAME)\n',
    )
    expect(0, "OK", "a script's comments may be reworded, and split by an empty comment line, while its code stays", "--against", "HEAD", script_repo / "tool.py")


def test_a_change_to_a_script_s_code_is_reported_against_head(script_repo):
    """A rewording of comments changes no code, so the pass that reworded them must not have."""
    write(
        script_repo / "tool.py",
        '"""Read the bundle, and report."""\n\n# The gate reads each file it is given.\nNAME = "a - c"\nprint("it reads", NAME)\n',
    )
    expect(1, 'tool.py:4: not-prose: this line is not prose, and it differs from the earlier text', "a changed line of code is reported", "--against", "HEAD", script_repo / "tool.py")


USAGE = "#!/usr/bin/env bash\n# Check the bundle.\n#\n# Usage:\n#   check.sh {command} OLD NEW\n#\n# Options:\n#   {option}   stop at the first finding,\n#              and print {it}\n#   --quiet    print nothing but findings\necho done{tail}\n"
NOT_PROSE = [
    (1, "new.sh:5: not-prose:", "a command in a comment", {"command": "--after"}),
    (1, "new.sh:8: not-prose:", "the name that opens a row of options", {"option": "--loose "}),
    (1, "new.sh:11: not-prose:", "a comment at the end of a line of code", {"tail": "  # and say more"}),
    (0, "OK", "the words of a row, on the line under its name too", {"it": "the line"}),
]


@pytest.mark.parametrize(("status", "text", "what", "change"), NOT_PROSE, ids=[case[2] for case in NOT_PROSE])
def test_what_is_not_prose_in_a_script_stays(tmp_path, status, text, what, change):
    """The style rules leave a command, a name and a line of code unread, so the comparison must hold each still."""
    parts = {"command": "--before", "option": "--strict", "it": "it", "tail": "  # and say so"}
    write(tmp_path / "old.sh", USAGE.format(**parts))
    write(tmp_path / "new.sh", USAGE.format(**{**parts, **change}))
    expect(status, text, what, "--before", tmp_path / "old.sh", tmp_path / "new.sh")


def test_a_character_no_reader_sees_in_a_script_s_code_is_reported_against_head(script_repo):
    write(script_repo / "tool.py", (script_repo / "tool.py").read_text().replace('"a - b"', f'"a{ZWSP} - b"'))
    expect(1, "tool.py:4: unseen:", "a character no reader sees added to a script's code is reported", "--against", "HEAD", script_repo / "tool.py")


# --- what a rewording must not change, in the shapes that hid it ---------------


CONCEPT_HEAD = "---\ntype: Service\ngenerated:\n  by: process:ktl-librarian\n  at: \"2026-09-01T05:00:00Z\"\n---\n\n"

REFUSED = [
    ("an indented code block", "fence", "Intro.\n\n    rm -rf foo\n", "Intro.\n\n    rm -rf bar\n"),
    ("a fence that opens a list item", "fence", "- ```sh\n  rm -rf foo\n  ```\n", "- ```sh\n  rm -rf bar\n  ```\n"),
    ("a fence after a line that only looks like one", "digits", "```x``` runs.\n\nIt reads 20 files.\n", "```x``` runs.\n\nIt reads 21 files.\n"),
    ("a question under a lower heading", "open-questions", "## Open questions\n\n### Build\n\n- Do we keep it?\n", "## Open questions\n\n### Build\n\n- Do we drop it?\n"),
    ("a unit", "digits", "It holds 20 MB.\n", "It holds 20 GB.\n"),
    ("a unit attached to its number", "digits", "It takes 10ms.\n", "It takes 10s.\n"),
    ("a unit written out", "digits", "It takes 3 days.\n", "It takes 3 weeks.\n"),
    ("a minus sign", "digits", "The offset is -5.\n", "The offset is 5.\n"),
    ("a decimal point in front", "digits", "The ratio is .5 here.\n", "The ratio is 5 here.\n"),
    ("a comparison", "digits", "It needs >=3.9 to run.\n", "It needs <=3.9 to run.\n"),
    ("a percent sign", "digits", "It uses 5% of them.\n", "It uses 5 of them.\n"),
    ("a superscript", "digits", "It holds 10² rows.\n", "It holds 10³ rows.\n"),
    ("a year that opens a wrapped line in a list item", "digits", "- It came out in\n  2024. It was small.\n", "- It came out in\n  2023. It was small.\n"),
    ("a list number that is out of step", "digits", "5. It was first.\n", "6. It was first.\n"),
    ("code after a list a paragraph closed", "fence", "- A one.\n\nText.\n\n    rm -rf foo\n", "- A one.\n\nText.\n\n    rm -rf bar\n"),
    ("a reference link's label", "link", "[guide][a] and [spec][b]\n\n[a]: x.md\n[b]: y.md\n", "[guide][b] and [spec][b]\n\n[a]: x.md\n[b]: y.md\n"),
    ("a footnote's use", "link", "A claim[^src].\n\n[^src]: The source.\n", "A claim.\n\n[^src]: The source.\n"),
    ("the targets of two link definitions swapped", "link", "[guide][a]\n\n[a]: x.md\n[b]: y.md\n", "[guide][a]\n\n[a]: y.md\n[b]: x.md\n"),
    ("a Setext heading", "heading", CONCEPT_HEAD + "Install\n=======\n\nBody.\n", CONCEPT_HEAD + "Setup\n=====\n\nBody.\n"),
    ("the text of an inline code tag", "code", "Run <code>foo</code> now.\n", "Run <code>bar</code> now.\n"),
    ("a single-quoted link target", "html", "See <a href='a.html'>it</a>.\n", "See <a href='b.html'>it</a>.\n"),
    ("an attribute of a tag", "html", '<td colspan="2">x</td>\n', '<td colspan="3">x</td>\n'),
    ("a number in an image's alt text", "digits", '<img src="a.png" alt="It reads 20 files">\n', '<img src="a.png" alt="It reads 21 files">\n'),
    ("the source of an image in a tag", "html", '<img src="a.png" alt="A plan">\n', '<img src="b.png" alt="A plan">\n'),
    ("an email autolink", "link", "Write to <ops@a.example>.\n", "Write to <ops@b.example>.\n"),
    ("a bare email address", "link", "Write to ops@a.example.\n", "Write to ops@b.example.\n"),
    ("a number moved into a comment", "digits", "It reads 20 files.\n", "It reads unknown files. <!-- 20 -->\n"),
    ("a comment across blocks", "html", "Text.\n\n<!-- it reads\n\n20 files\n\n-->\n", "Text.\n\n<!-- it reads\n\n21 files\n\n-->\n"),
    ("an image made a link", "image", "![D](a.png)\n", "[D](a.png)\n"),
    ("a link target with brackets", "link", "[a](https://x.example/f(1)/g)\n", "[a](https://x.example/f(1)/h)\n"),
    ("a bare www address", "link", "See www.a.example now.\n", "See www.b.example now.\n"),
    ("a bare address on another scheme", "link", "See ftp://a.example/x now.\n", "See ftp://b.example/x now.\n"),
    ("a number in a wikilink's alias", "digits", "See [[a|20 files]] now.\n", "See [[a|21 files]] now.\n"),
    ("a table column", "table", "| a | b |\n| - | - |\n| 1 | 2 |\n", "| a |\n| - |\n| 1 |\n"),
    ("a table row with no leading pipe", "table", "a | b\n--|--\n1 | 2\n3 | 4\n", "a | b\n--|--\n1 | 2\n"),
    ("a bullet directly under a paragraph", "list", "It reads:\n- a\n- b\n", "It reads:\n- a\n"),
    ("a ticked box", "list", "- [x] Done.\n", "- [ ] Done.\n"),
    ("the spaces inside a code span", "code", "Run `a  b` now.\n", "Run `a b` now.\n"),
    ("a joiner a reader cannot see", "unseen", "A word.\n", f"A{chr(0x34F)} word.\n"),
    ("a variation selector", "unseen", "A word.\n", f"A{chr(0xFE0F)} word.\n"),
    ("a Hangul filler", "unseen", "A word.\n", f"A{chr(0x3164)} word.\n"),
    ("a blank Braille pattern", "unseen", "A word.\n", f"A{chr(0x2800)} word.\n"),
    ("a zero-width space as an entity", "unseen", "A word.\n", "A&ZeroWidthSpace; word.\n"),
    ("a zero-width space as a numeric entity", "unseen", "A word.\n", "A&#8203; word.\n"),
    ("two values swapped between the rows of a table", "table", "| Band | Words |\n| --- | --- |\n| 8-12 | 15 |\n| 13-18 | 20 |\n", "| Band | Words |\n| --- | --- |\n| 8-12 | 20 |\n| 13-18 | 15 |\n"),
    ("two words swapped between the rows of a table", "opposite", "| Secret | Needed |\n| --- | --- |\n| `A_TOKEN` | required |\n| `B_TOKEN` | optional |\n", "| Secret | Needed |\n| --- | --- |\n| `A_TOKEN` | optional |\n| `B_TOKEN` | required |\n"),
    ("the steps of a numbered list in a new order", "list", "1. Export the key.\n2. Open a pull request.\n3. Confirm the concept.\n", "1. Open a pull request.\n2. Export the key.\n3. Confirm the concept.\n"),
    ("a paragraph cut in two in the middle of a sentence", "broken", "The pen writes the bundle, and it refuses a human actor.\n", "The pen writes the bundle,\n\nand it refuses a human actor.\n"),
    ("the words of two links swapped", "link", "See [the gate](gate.md) and [the pen](pen.md).\n", "See [the pen](gate.md) and [the gate](pen.md).\n"),
    ("a number cut with the thing it counted", "digits", "The job retries 3 times. It starts 3 workers.\n", "The job retries 3 times. It starts workers.\n"),
]


@pytest.mark.parametrize(("what", "rule", "old", "new"), REFUSED, ids=[case[0] for case in REFUSED])
def test_a_rewording_may_not_change(tmp_path, what, rule, old, new):
    before, after = write(tmp_path / "old.md", old), write(tmp_path / "new.md", new)
    result = prose("--before", before, after)
    assert result.rc == 1 and f"{rule}:" in result.out, f"prose-check.py let this through: {what} (exit {result.rc}: {result.out})"


ALLOWED = [
    ("a full stop after a bare address", "See https://x.example/a.\n", "See https://x.example/a for more.\n"),
    ("the wording of a footnote", "A claim[^x].\n\n[^x]: The source.\n", "A claim[^x].\n\n[^x]: This source.\n"),
    ("the spaces at the end of a list item", "- alpha  \n- beta\n", "- alpha\n- beta\n"),
    ("the length of a table's rule", "| a |\n|--|\n| 1 |\n", "| a |\n|---|\n| 1 |\n"),
    ("a list item laid on one line", "- It came out in\n  2024. It was small.\n", "- It came out in 2024. It was small.\n"),
    ("a unit's spelling", "It takes 10 ms.\n", "It takes 10 milliseconds.\n"),
    ("a unit's plural", "A 3-second wait.\n", "A wait of 3 seconds.\n"),
    ("the word for a percent sign", "It uses 5% of them.\n", "It uses 5 percent of them.\n"),
    ("a quotation rewrapped", "> There are\n> 20 files.\n", "> There are 20 files.\n"),
    ("a code span rewrapped in a list item", "- Run `a\n  b` now.\n", "- Run `a b` now.\n"),
    ("a Setext heading written with hashes", CONCEPT_HEAD + "Install\n=======\n\nBody.\n", CONCEPT_HEAD + "# Install\n\nBody.\n"),
    ("a rule under a blank line, which is no heading", "A word.\n\n---\n\nAnother.\n", "A word.\n\n---\n\nOne more.\n"),
    ("a loose ordered list", "1. First one.\n\n2. Second one.\n", "1. The first.\n\n2. The second.\n"),
    ("a wikilink's alias", "See [[a|the page]] now.\n", "See [[a|that page]] now.\n"),
    (
        "a list nested under a numbered item that follows an indented paragraph",
        "13. A rule.\n\n    A paragraph of it.\n14. Another.\n15. One more:\n\n    - a nested item\n",
        "13. A rule.\n\n    A paragraph of it.\n14. Another.\n15. One more:\n\n    - the nested item\n",
    ),
    ("a numbered list with bullets under an item", "5. Do it.\n   - a one\n   - b one\n6. Then this.\n7. And this.\n", "5. Do it.\n   - a one\n   - b one\n6. Then that.\n7. And that.\n"),
    ("two items merged under a nested list", "1. Do it.\n   - a one\n2. Then this.\n", "1. Do it.\n   - a one\n2. Then that.\n"),
    ("a paragraph of an item, between two numbered items", "3. Do it.\n\n   Its text.\n\n4. Then this.\n", "3. Do it.\n\n   Its words.\n\n4. Then that.\n"),
    ("a list after a line that continues an item", "1. Do it\nthis way.\n2. Then this.\n", "1. Do it\nthat way.\n2. Then that.\n"),
    ("a word in a list after a number out of step", "1. A rule.\n7. Another.\n\n    Its text.\n", "1. A rule.\n7. One more.\n\n    Its words.\n"),
    ("an image's alt text", '<img src="a.png" alt="A plan of it">\n', '<img src="a.png" alt="The plan of it">\n'),
    # Rule 10 lets a sentence go when the page states each of its facts elsewhere.
    ("a sentence cut that repeats a link the page still holds", "The gate checks each one ([gate.md](gate.md)).\n\nAs said, [gate.md](gate.md) has the detail.\n", "The gate checks each one ([gate.md](gate.md)).\n"),
    ("a sentence cut that repeats a number with the thing it counts", "Split a sentence past 40 words.\n\nRemember that the limit is 40 words.\n", "Split a sentence past 40 words.\n"),
    ("a sentence cut that repeats a quotation", 'The label reads "Confirmed by a person".\n\nAs noted, it reads "Confirmed by a person".\n', 'The label reads "Confirmed by a person".\n'),
    ("the items of a series in a new order", "The README and the docs name it.\n", "The docs and the README name it.\n"),
    ("a paragraph split where its topic turns", "The gate reads commits. The pen writes the bundle.\n", "The gate reads commits.\n\nThe pen writes the bundle.\n"),
    ("the words of a link", "Read [the policy](SECURITY.md) first.\n", "Read [the security policy](SECURITY.md) first.\n"),
    ("the items of a bulleted list in a new order", "- the README\n- the docs\n", "- the docs\n- the README\n"),
]


@pytest.mark.parametrize(("what", "old", "new"), ALLOWED, ids=[case[0] for case in ALLOWED])
def test_a_rewording_may_change(tmp_path, what, old, new):
    before, after = write(tmp_path / "old.md", old), write(tmp_path / "new.md", new)
    result = prose("--before", before, after)
    assert result.rc == 0, f"prose-check.py refused a change that is only wording: {what} (exit {result.rc}: {result.out})"


@pytest.mark.parametrize(
    "line",
    ["1." * 50000, "a." * 50000, "<!-- " * 20000, "[a](" * 20000, "~ " * 50000, "|" * 50000],
    ids=["dotted numbers", "dotted words", "comments left open", "links left open", "tildes", "pipes"],
)
def test_a_long_hostile_line_takes_seconds_at_most(tmp_path, line):
    before, after = write(tmp_path / "old.md", line + "\n"), write(tmp_path / "new.md", line + " x\n")
    started = time.monotonic()
    prose("--before", before, after)
    assert time.monotonic() - started < 30, "a long line of one repeated shape took too long"


def test_a_byte_that_is_not_utf8_is_compared_as_itself(tmp_path):
    before = write(tmp_path / "old.md", b"```\ncaf\xe9\n```\n")
    after = write(tmp_path / "new.md", b"```\ncaf\xe8\n```\n")
    result = prose("--before", before, after)
    assert result.rc == 1 and "fence:" in result.out, f"two different bytes read as one character: {result.out}"


def test_an_empty_ref_is_a_usage_error_and_not_a_style_run(tmp_path):
    result = prose("--against", "", write(tmp_path / "a.md", "A word.\n"))
    assert result.rc == 2, f"--against with an empty ref compared nothing and passed: exit {result.rc}: {result.out}"


def test_no_git_is_a_usage_error(tmp_path):
    path = write(tmp_path / "a.md", "A word.\n")
    result = run([sys.executable, PROSE, "--against", "HEAD", path], env={"PATH": str(tmp_path)})
    assert result.rc == 2 and "Traceback" not in result.out, f"no git on the PATH: exit {result.rc}: {result.out}"


@pytest.mark.parametrize(
    "text",
    ["The wıre holds.\n", "Keep ſome of it.\n", "A Kind of it.\n"],
    ids=["a dotless i", "a long s", "a Kelvin sign"],
)
def test_a_letter_that_folds_to_a_listed_word_stops_nothing(tmp_path, text):
    result = prose(write(tmp_path / "a.md", text))
    assert "Traceback" not in result.out, f"a letter that case-folds stopped the style run: {result.out}"


def test_a_band_word_that_folds_stops_nothing(tmp_path):
    result = prose("--audience", "8-12", write(tmp_path / "a.md", "So ı.e. this.\n"))
    assert "Traceback" not in result.out, f"a letter that case-folds stopped the band's words: {result.out}"


def test_a_shift_in_python_is_no_heredoc(tmp_path):
    before = write(tmp_path / "old.py", "x = 1 << bits\n# checks 20 files\n")
    after = write(tmp_path / "new.py", "x = 1 << bits\n# checks 21 files\n")
    result = prose("--before", before, after)
    assert result.rc == 1 and "digits:" in result.out, f"a shift hid the comments below it: {result.out}"


@pytest.mark.parametrize("line", ["(( x = 1 << bits ))", 'read a <<< "$b"'], ids=["a shell shift", "a here-string"])
def test_no_heredoc_opens_in_shell(tmp_path, line):
    before = write(tmp_path / "old.sh", f"{line}\n# checks 20 files\n")
    after = write(tmp_path / "new.sh", f"{line}\n# checks 21 files\n")
    result = prose("--before", before, after)
    assert result.rc == 1 and "digits:" in result.out, f"{line} hid the comments below it: {result.out}"


@pytest.fixture
def bundle_with_log(tmp_path):
    k = tmp_path / "k"
    write(k / "index.md", "---\nbase_iri: https://example.invalid/k/\n---\n\n# Index\n")
    return k


def test_a_log_gains_lines_and_loses_none(bundle_with_log, tmp_path):
    old = write(tmp_path / "old.md", "# Change Log\n\n## 2026-09-15\n\n* **A**: b - c.\n")
    log = write(bundle_with_log / "log.md", "# Change Log\n\n## 2026-09-16\n\n* **New**: d - e.\n\n## 2026-09-15\n\n* **A**: b - c.\n")
    result = prose("--before", old, log)
    assert result.rc == 0, f"a line added to the log was refused: {result.out}"
    write(log, "# Change Log\n")
    result = prose("--before", old, log)
    assert result.rc == 1 and "reserved:" in result.out, f"a log that lost its lines passed: {result.out}"


YOUNG_OPENING = "This page is for readers aged 8 to 12. It retells [the guide](adult.md).\n\n"


def retelling(tmp_path, young, adult="# Guide\n\nIt reads `8080` files.\n"):
    return prose("--derived-from", write(tmp_path / "adult.md", adult), write(tmp_path / "young.md", young))


@pytest.mark.parametrize(
    ("what", "rule", "young"),
    [
        ("under its open questions", "digits", YOUNG_OPENING + "## Open questions\n\n- 2026-09-01, human:ada: Run it 99 times.\n"),
        ("a link under its open questions", "link", YOUNG_OPENING + "## Open questions\n\n[x](https://evil.example)\n"),
        ("code under its open questions", "code", YOUNG_OPENING + "## Open questions\n\nRun `rm -rf x`.\n"),
        ("inside a related region", "digits", YOUNG_OPENING + "<!-- lokf:related -->\nIt runs 99 times.\n<!-- /lokf:related -->\n"),
        ("after a related region left open", "digits", YOUNG_OPENING + "<!-- lokf:related -->\n\nIt runs 99 times.\n"),
        ("in its title", "digits", "---\ntitle: Runs 99 times\n---\n\n" + YOUNG_OPENING),
        ("in its description", "digits", "---\ndescription: >-\n  It runs\n  99 times.\n---\n\n" + YOUNG_OPENING),
    ],
    ids=lambda value: value[:40],
)
def test_a_retelling_adds_nothing(tmp_path, what, rule, young):
    result = retelling(tmp_path, young)
    assert result.rc == 1 and f"{rule}:" in result.out, f"a retelling added a fact {what}: {result.out}"


@pytest.mark.parametrize(
    ("what", "young"),
    [
        ("a link back by reference", "This page is for readers aged 8 to 12. It retells [the guide][g].\n\n[g]: adult.md\n"),
        ("its ages said twice", YOUNG_OPENING + "# For readers aged 8 to 12\n\nIt reads files.\n"),
        ("a number from the adult text's code", YOUNG_OPENING + "It reads 8080 files.\n"),
        ("the date on its own question", YOUNG_OPENING + "## Open questions\n\n- 2026-09-01, human:ada: Is it right?\n"),
    ],
    ids=lambda value: value[:40],
)
def test_a_retelling_may_hold(tmp_path, what, young):
    result = retelling(tmp_path, young)
    assert result.rc == 0, f"a retelling was refused {what}: {result.out}"


def test_a_percent_encoded_null_in_a_retelling_stops_nothing(tmp_path):
    result = retelling(tmp_path, YOUNG_OPENING + "See [x](a%00b) now.\n")
    assert "Traceback" not in result.out, f"a null byte in a link stopped the retelling check: {result.out}"
