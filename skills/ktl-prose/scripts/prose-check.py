#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
# The check ktl-prose runs before and after it rewords a file. A script can
# answer two questions about prose, and this one answers both. Where does the
# text break a rule a script can see? Did a rewording change anything but the
# wording? Whether the meaning held is a question for a reader.
#
#   prose-check.py FILE...                what a script sees: dash, long, paragraph, words, unseen
#   prose-check.py --audience BAND FILE...  the same at the limits of a band of readers, with sentences and a grade
#   prose-check.py --before OLD NEW       what differs besides the wording, and the words before and after
#   prose-check.py --against REF FILE...  the same, against the version git holds at REF
#   prose-check.py --bundle DIR           which files of a bundle ktl-prose may reword
#
# A band holds a page to the limits references/young-readers.md gives for
# readers aged 8 to 12, aged 13 to 18, or dyslexic. A page that opens by
# naming its readers, as "This page is for readers aged 13 to 18." does, is
# held to that band with no flag. Under a band the script also counts the
# sentences in each paragraph, and notes the page's Automated Readability
# Index with the counts it comes from. The index is a hint, never a finding.
#
# `unseen` is a character no reader sees: a control character other than a
# tab, or a format character such as a zero-width space or the right-to-left
# override that the "Trojan Source" attack hides code behind. An agent that
# types the escape for one into a tool call can write the character itself.
# A style run reports each line that holds one, code and frontmatter included,
# and a comparison reports one the rewording added.
#
# The contract is the one knowledge-conventions.sh keeps, with a line number
# and a rule name added. Each finding is one line on stdout, as
# `path:line: rule: message`, and the script exits 1 if there is any. With
# none it prints one `OK` line and exits 0. A usage error exits 2. A note goes
# to stderr and never changes the exit status.
#
# The script reads the files it is given, and the word book in the skill's
# assets/ folder, and asks git for an earlier version. It writes nothing
# and opens no network connection. It needs python3 3.9 or later and
# nothing else. `uv run` reads the empty dependency block above.

from __future__ import annotations

import argparse
import bisect
import re
import subprocess
import sys
import textwrap
import unicodedata
from collections import Counter, namedtuple
from pathlib import Path

RESERVED = {"index.md", "log.md", "diataxis.md"}
MAX_WORDS = 40
# The Federal Plain Language Guidelines' ceiling for a paragraph.
MAX_PARAGRAPH = 150
# The bands of readers, as references/young-readers.md gives them with their
# sources: the words in a sentence and in a paragraph, the sentences in a
# paragraph, and the Automated Readability Index a page should stay at or
# under. A grade of None notes the index with no target.
Band = namedtuple("Band", "words paragraph sentences grade")
BANDS = {
    "8-12": Band(15, 50, 3, 7),
    "13-18": Band(20, 75, 5, 9),
    "dyslexia": Band(20, 75, 5, None),
}
# Words a band of readers is spared, on top of WORDS: a Latin abbreviation a
# younger reader has not met, and a word of the trade with a plain one.
BAND_WORDS = {
    "i.e.": 'write "that is"',
    "vs": 'write "against" or "compared with"',
    "cf.": 'write "compare"',
    "etc.": 'name the rest, or write "and others"',
    "via": 'write "through" or "by"',
}
BAND_WORD = re.compile(r"(?<![A-Za-z])i\.e\.|(?<![\w.-])(?:vs|cf|etc|via)\b\.?", re.I)
# The words a younger reader can be expected to know: the VOA Learning
# English Word Book, in the skill's assets/ folder, which credits its
# source. Under a band, a note names the words of a page that fall outside
# it, most frequent first. A word is known when the book lists it, or a
# form of it that a suffix, a prefix the book lists as common, or an
# irregular form leads to.
WORD_BOOK = Path(__file__).resolve().parent.parent / "assets" / "voa-word-book.txt"
ENDINGS = (
    ("ies", "y"), ("ied", "y"), ("ier", "y"), ("iest", "y"), ("ily", "y"), ("es", ""), ("s", ""),
    ("ed", ""), ("ed", "e"), ("ing", ""), ("ing", "e"), ("er", ""), ("er", "e"), ("est", ""), ("est", "e"),
    ("ly", ""), ("ness", ""), ("ment", ""), ("ful", ""), ("less", ""), ("al", ""), ("ion", ""), ("ion", "e"),
)
PREFIXES = ("anti", "dis", "mis", "pro", "re", "self", "un")
IRREGULAR = {
    form: word
    for word, forms in {
        "be": "am is are was were been being", "have": "has had", "do": "does did done", "go": "goes went gone",
        "say": "said", "make": "made", "take": "took taken", "give": "gave given", "get": "got gotten",
        "see": "saw seen", "know": "knew known", "think": "thought", "find": "found", "tell": "told",
        "become": "became", "leave": "left", "feel": "felt", "bring": "brought", "begin": "began begun",
        "keep": "kept", "hold": "held", "write": "wrote written", "stand": "stood", "hear": "heard",
        "mean": "meant", "meet": "met", "run": "ran", "pay": "paid", "sit": "sat", "speak": "spoke spoken",
        "lead": "led", "grow": "grew grown", "lose": "lost", "fall": "fell fallen", "send": "sent",
        "build": "built", "understand": "understood", "draw": "drew drawn", "break": "broke broken",
        "spend": "spent", "rise": "rose risen", "drive": "drove driven", "buy": "bought", "wear": "wore worn",
        "choose": "chose chosen", "seek": "sought", "throw": "threw thrown", "catch": "caught", "win": "won",
        "forget": "forgot forgotten", "sell": "sold", "fight": "fought", "teach": "taught", "eat": "ate eaten",
        "fly": "flew flown", "hide": "hid hidden", "shoot": "shot", "steal": "stole stolen",
        "child": "children", "man": "men", "woman": "women", "person": "people", "foot": "feet",
        "good": "better best", "bad": "worse worst", "much": "more most", "little": "less least",
        "i": "me my mine", "he": "him his", "she": "her hers", "it": "its", "we": "us our ours",
        "they": "them their theirs", "you": "your yours", "can": "could", "will": "would", "shall": "should",
        "may": "might",
    }.items()
    for form in forms.split()
}
CONTRACTION = re.compile(r"(?:n't|'s|'re|'ll|'ve|'d|'m)$")
# A word of prose, and not a piece of a path or a file name such as
# docs/install.md, which a link's text may show, nor a piece of a name joined
# by hyphens, such as ktl-librarian.
WORD_TOKEN = re.compile(r"(?<![\w./-])[A-Za-z]+(?:'[A-Za-z]+)?(?![\w/-]|\.\w)")
# How a page names its readers in its first paragraph, as rule 12 asks of a
# retelling: "This page is for readers aged 13 to 18."
DECLARED = re.compile(
    r"\bthis [\w.-]+ is for (?P<who>readers aged (?P<low>\d{1,2}) to (?P<high>\d{1,2})|dyslexic readers|readers with dyslexia)\b",
    re.I,
)
# One private-use character stands in for each character a rule skips, so
# every offset and line number stays true after masking.
MASK = ""

# The words the first hand pass cut, and the stock phrases it replaced.
# "actually", "really", "simply" and "just" stay off the list on purpose: the
# second pass kept every one of them.
WORDS = {
    "deliberately": "cut it, or say what was chosen",
    "honestly": "cut it",
    "in order to": 'write "to"',
    "due to the fact that": 'write "because"',
    "e.g.": 'write "for example"',
}
# The figures of speech the third pass replaced, each with its forms. Each
# names an action by a picture, and a reader new to the trade has to turn the
# picture back into the action. None of them is literal in a technical text.
FIGURES = {
    ("land", "lands", "landed", "landing"): 'say what happens, such as "is merged", "is added" or "is written"',
    ("mint", "mints", "minted", "minting"): 'say what happens, such as "makes", "builds" or "issues"',
    ("ship", "ships", "shipped", "shipping"): 'say what happens, such as "is released" or "is included"',
    ("arm", "arms", "armed", "arming"): 'say what happens, such as "turn on"',
    ("wire", "wires", "wired", "wiring"): 'say what happens, such as "connect", "add" or "set"',
    ("dogfood", "dogfoods", "dogfooded", "dogfooding"): 'say what happens, such as "uses its own"',
    ("load-bearing",): "say what depends on it",
}
WORDS.update((form, advice) for forms, advice in FIGURES.items() for form in forms)
# A letter, a digit, an underscore or a hyphen on either side makes another
# word: `arm64`, `wire-format`.
WORD = re.compile(
    r"(?<![\w-])(?:"
    + "|".join(sorted((re.escape(word) for word in WORDS if word != "e.g."), key=len, reverse=True))
    + r")(?![\w-])|(?<![A-Za-z])e\.g\.",
    re.I,
)
# A spaced hyphen, an em dash anywhere, and an en dash that is not a range.
DASH = re.compile(r"(?<=\S) --? (?=\S)|—|(?<!\d)–|–(?!\d)")
SENTENCE_END = re.compile(r"(?<=[.!?])[\"')\]*_”]*\s+(?=[A-Z`*\[(\"“])")
ABBREVIATION = re.compile(r"\b(?:e\.g|i\.e|vs|cf)\.$", re.I)

FENCE = re.compile(r"^\s*(?:>\s?)*(`{3,}|~{3,})")
HEADING = re.compile(r"^ {0,3}#{1,6}(?:\s|$)")
RULE_LINE = re.compile(r"^ {0,3}([-*_=])(?:\s*\1){2,}\s*$")
TABLE_ROW = re.compile(r"^\s*\|")
RULE_CELL = re.compile(r"^\s*:?-{3,}:?\s*$")
HTML_LINE = re.compile(r"^\s*</?(?!https?:|mailto:)[A-Za-z!]")
# Four spaces or a tab of indent, where a block begins: an indented code block.
INDENT_CODE = re.compile(r"^(?: {4}|\t)")
# A hard line break: two or more spaces, or a backslash, at a line's end.
HARD_BREAK = re.compile(r"(?:  +|\\)$")
LINK_DEF = re.compile(r"^ {0,3}\[[^\]]+\]:\s*(\S+)")
QUOTE_MARK = re.compile(r"^\s*(?:>\s?)+")
LIST_MARK = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(?:\[[ xX]\]\s+)?")
ORDERED_MARK = re.compile(r"^(\s*(?:>\s*)*)(\d+)([.)]\s)")
CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
COMMENT = re.compile(r"<!--.*?-->")
INLINE_LINK = re.compile(r"\]\(([^)]*)\)")
WIKILINK = re.compile(r"\[\[([^\]]*)\]\]")
AUTOLINK = re.compile(r"<((?:https?://|mailto:)[^>\s]*)>")
HTML_ATTR = re.compile(r"\b(?:href|src|srcset)=\"([^\"]*)\"")
HTML_TAG = re.compile(r"</?[A-Za-z][^>]*>")
BARE_URL = re.compile(r"https?://[^\s)>\]\"']+")
QUOTED = re.compile(r"\"([^\"]+)\"|“([^”]+)”")
LABEL = re.compile(r"(?<![\w*])(\*{1,2})(?=\S)([^*]+?)(?<=\S)\1(?![\w*])")
NUMBER = re.compile(r"\d+(?:[.,:/-]\d+)*")
RFC_WORD = re.compile(r"\b(?:MUST NOT|SHALL NOT|SHOULD NOT|MUST|SHALL|SHOULD|REQUIRED|RECOMMENDED|MAY|OPTIONAL)\b")
NUMBER_WORD = re.compile(
    r"\b(?:two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty|thirty|forty|fifty|hundred|thousand)\b",
    re.I,
)
# A day of the week or a month, written out. "May" is left out: it is a verb
# far more often than a month.
DATE_WORD = re.compile(
    r"\b(?:(?:Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)days?"
    r"|January|February|March|April|June|July|August|September|October|November|December)\b"
)
STRENGTH = ("must", "never", "only", "always", "unless", "except")
NEGATION = re.compile(r"\b(?:not|no|nor|neither|cannot|without)\b|n't\b", re.I)

# The KTL Registrar plugin writes each marker on a line of its own. Prose
# that names a marker in a code span is prose, and opens no region.
RELATED_OPEN = "<!-- lokf:related -->"
RELATED_CLOSE = "<!-- /lokf:related -->"
OPEN_QUESTIONS = "## Open questions"

# The actor shapes the LOKF schema allows for `by`. Anything else is a value
# this script cannot read, and it must not guess.
ACTOR = re.compile(r"^(?:(?:human|process):\S+|[^\s/]+/[^\s/]+)$")
BY_LINE = re.compile(r"^\s*(?:-\s*)?(?:\{\s*)?[\"']?by[\"']?\s*:")
BY_FLOW = re.compile(r"[{,\[]\s*[\"']?by[\"']?\s*:")


class Usage(Exception):
    """A request the script cannot act on. It exits 2."""


def normalise(raw: bytes) -> str:
    """Read bytes as CI reads them: no byte order mark, and LF line endings."""
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")


def read(path: Path) -> str:
    try:
        return normalise(path.read_bytes())
    except OSError as exc:
        raise Usage(f"cannot read {path}: {exc.strerror}") from exc


class Doc:
    """One version of a file: its frontmatter lines, and its body lines."""

    def __init__(self, text: str):
        self.lines = text.split("\n")
        self.fm: list[str] | None = None
        self.unclosed = False
        self.body_at = 0
        if self.lines and self.lines[0] == "---":
            for i in range(1, len(self.lines)):
                if self.lines[i] == "---":
                    self.fm = self.lines[1:i]
                    self.body_at = i + 1
                    break
            else:
                self.unclosed = True
        self.body = self.lines[self.body_at :]

    def numbered_body(self):
        return enumerate(self.body, start=self.body_at + 1)


class Block:
    """A run of prose joined into one string, with the line each character sits on.

    Its kind is `paragraph`, `item` for a list item, or `cell` for a table cell.
    """

    def __init__(self, kind: str = "paragraph"):
        self.kind = kind
        self.text = ""
        self.starts: list[int] = []
        self.numbers: list[int] = []

    def add(self, number: int, text: str) -> None:
        if self.text:
            self.text += " "
        self.starts.append(len(self.text))
        self.numbers.append(number)
        self.text += text

    def line_at(self, offset: int) -> int:
        return self.numbers[max(bisect.bisect_right(self.starts, offset) - 1, 0)]


def closes(fence: str, line: str) -> bool:
    """A fence closes on a line of the same mark, at least as long, and nothing else."""
    mark = QUOTE_MARK.sub("", line, count=1).strip()
    return bool(mark) and set(mark) == {fence[0]} and len(mark) >= len(fence)


def html_only(content: str) -> bool:
    """True when a line is HTML markup with nothing a reader reads as prose: tags and whitespace alone. A prose line that merely opens with an inline tag is not HTML-only, and its style is read like any other line's."""
    return not HTML_TAG.sub("", content).strip()


def tag_name(tag: str) -> str:
    """An inline HTML tag reduced to what a rewording must not change: its name, and a leading slash where it closes. Attributes are left out, since a link's target is kept on its own."""
    found = re.match(r"</?\s*([A-Za-z][A-Za-z0-9-]*)", tag)
    return ("/" if tag.lstrip().startswith("</") else "") + (found.group(1).lower() if found else "")


# --- who vouched for a concept -------------------------------------------------


def events(fm: list[str]) -> list[tuple[str, str, str, str]]:
    """The `generated` record and each `verified` event, as (key, by, at, revision).

    This is a port of human_events() in knowledge-provenance.sh, and it keeps
    to that reading on purpose: the script must see an event exactly where the
    gates see one. It reads a block list at any indent, a flow item, a flow
    sequence and a bare mapping. The gates keep only human actors, and this
    keeps every actor.
    """
    out: list[tuple[str, str, str, str]] = []
    key: str | None = None
    cur: dict[str, str] | None = None

    def emit() -> None:
        nonlocal cur
        if cur is not None and cur.get("by"):
            out.append((cur["key"], cur["by"], cur.get("at", ""), cur.get("revision", "")))
        cur = None

    def value(text: str) -> str:
        text = re.sub(r"^[^:]*:\s*", "", text, count=1)
        return text.replace('"', "").replace("'", "").rstrip()

    def pair(text: str) -> None:
        name = text.split(":", 1)[0].lstrip()
        if cur is not None and name in ("by", "at", "revision"):
            cur[name] = value(text)

    def flow(text: str) -> None:
        nonlocal cur
        emit()
        cur = {"key": key or ""}
        for part in text.replace("{", "").replace("}", "").split(","):
            pair(part)
        emit()

    for line in fm:
        opened = re.match(r"^(verified|generated):\s*(.*)$", line)
        if opened:
            emit()
            key, rest = opened.group(1), opened.group(2)
            if rest.startswith("{"):
                flow(rest)
                key = None
            elif rest.startswith("["):
                for item in re.split(r"\}\s*,", rest.replace("[", "").replace("]", "")):
                    flow(item)
                key = None
            continue
        if key is None:
            continue
        if re.match(r"^[^\s-]", line):
            emit()
            key = None
        elif re.match(r"^\s*-\s*\{", line):
            flow(re.sub(r"^\s*-\s*", "", line, count=1))
        elif re.match(r"^\s*-\s+", line):
            emit()
            cur = {"key": key}
            pair(re.sub(r"^\s*-\s+", "", line, count=1))
        elif re.match(r"^\s+[a-z_]+:", line):
            if cur is None:
                cur = {"key": key}
            pair(line)
    emit()
    return out


def by_keys(fm: list[str]) -> int:
    """How many events the frontmatter spells out, whether or not events() saw them."""
    count = 0
    for line in fm:
        if BY_LINE.match(line):
            count += 1
        elif re.match(r"^(?:verified|generated)\s*:", line):
            count += len(BY_FLOW.findall(line))
    return count


def top_value(fm: list[str], key: str) -> str | None:
    for line in fm:
        found = re.match(rf"^{key}\s*:\s*(.*)$", line)
        if found:
            return found.group(1).split(" #")[0].strip().strip("\"'")
    return None


def standing(doc: Doc, expect_concept: bool = False) -> tuple[str, str]:
    """Where a file stands, as a rule name and the words for it.

    Only `rewrite` allows a rewording outright, and `unrecorded` allows one a
    person named. The order is the order of the table in SKILL.md. The script
    fails closed: an event it cannot read is never taken for a missing one.
    """
    unreadable = ("unreadable", "frontmatter the script cannot read")
    if doc.fm is None:
        return unreadable if doc.unclosed or expect_concept else ("plain", "not a concept")
    found = events(doc.fm)
    for key, by, _, _ in found:
        if key == "generated" and by.startswith("human:"):
            return "person", f"written by a person ({by})"
    for key, by, _, _ in found:
        if key == "verified" and by.startswith("human:"):
            return "confirmed", f"confirmed by a person ({by})"
    if top_value(doc.fm, "status") == "deprecated":
        return "retired", "retired"
    if by_keys(doc.fm) != len(found) or any(not ACTOR.match(by) for _, by, _, _ in found):
        return unreadable
    if top_value(doc.fm, "type") is None:
        return unreadable if expect_concept else ("plain", "not a concept")
    if not any(key == "generated" for key, _, _, _ in found):
        return "unrecorded", "no record of who wrote it"
    return "rewrite", "rewrite"


def bundle_root(path: Path) -> Path | None:
    """The bundle a file sits in: the nearest folder whose index.md declares base_iri."""
    for parent in path.resolve().parents:
        index = parent / "index.md"
        if not index.is_file():
            continue
        fm = Doc(read(index)).fm
        if fm and any(re.match(r"^base_iri\s*:", line) for line in fm):
            return parent
    return None


# --- what a script can see of the style rules ----------------------------------


def hide(text: str, start: int, end: int) -> str:
    """Mask text[start:end]. A closing full stop stays, so the sentence still ends."""
    if end > start and text[end - 1] in ".!?":
        end -= 1
    return text[:start] + MASK * (end - start) + text[end:]


def mask(text: str) -> str:
    """The text with everything the style rules skip masked, and its length kept."""
    out = text
    for found in CODE_SPAN.finditer(out):
        out = out[: found.start(2)] + MASK * len(found.group(2)) + out[found.end(2) :]
    for pattern in (COMMENT, AUTOLINK, HTML_TAG):
        for found in pattern.finditer(out):
            out = out[: found.start()] + MASK * len(found.group()) + out[found.end() :]
    for pattern in (WIKILINK, INLINE_LINK):
        for found in pattern.finditer(out):
            out = out[: found.start(1)] + MASK * len(found.group(1)) + out[found.end(1) :]
    for found in BARE_URL.finditer(out):
        out = out[: found.start()] + MASK * len(found.group()) + out[found.end() :]
    for found in QUOTED.finditer(out):
        group = 1 if found.group(1) is not None else 2
        out = hide(out, found.start(group), found.end(group))
    # A short emphasised label is a name, as `*Wrong - send back*` is a verb of
    # the curator. Five words or fewer, a lone dash not counted.
    for found in LABEL.finditer(out):
        if len([word for word in found.group(2).split() if word not in "-–—"]) <= 5:
            out = hide(out, found.start(2), found.end(2))
    return out


def prose_blocks(doc: Doc):
    """Each paragraph, list item and table cell of the body that the style rules read."""
    block: Block | None = None
    fence: str | None = None
    comment = related = quoted = False
    indent_code = in_list = False
    prev_blank = True

    for number, line in doc.numbered_body():
        opening = FENCE.match(line)
        if fence:
            if closes(fence, line):
                fence = None
            continue
        if opening:
            fence = opening.group(1)
            if block:
                yield block
            block = None
            indent_code = prev_blank = False
            continue
        if line.strip() == RELATED_OPEN:
            related = True
        if related:
            related = line.strip() != RELATED_CLOSE
            if block:
                yield block
            block = None
            indent_code = prev_blank = False
            continue
        if comment:
            end = line.find("-->")
            if end < 0:
                prev_blank = False
                continue
            line, comment = " " * (end + 3) + line[end + 3 :], False
        line = COMMENT.sub(lambda found: " " * len(found.group()), line)
        if "<!--" in line:
            line, comment = line[: line.index("<!--")], True

        quote = QUOTE_MARK.match(line)
        content = line[quote.end() :] if quote else line
        blank = not content.strip()
        # An indented code block: a run of lines each indented four spaces or a
        # tab, begun at a block boundary after a blank line and outside a list,
        # where the same indent would instead be a list item's own continuation.
        # Its lines are code, so no style rule reads them; a blank line ends it.
        if indent_code:
            if blank or not INDENT_CODE.match(content):
                indent_code = False
            else:
                prev_blank = False
                continue
        # A line that is only HTML opens no prose and ends a block, as before. A
        # line that opens with an inline tag but carries prose is prose: its
        # style is read, with the tags masked, rather than skipped whole.
        is_html_block = bool(HTML_LINE.match(content)) and html_only(content)
        breaks = (
            blank
            or bool(quote) != quoted
            or HEADING.match(content)
            or RULE_LINE.match(content)
            or LINK_DEF.match(content)
            or is_html_block
            or TABLE_ROW.match(content)
            or LIST_MARK.match(content)
        )
        if breaks and block:
            yield block
            block = None
        quoted = bool(quote)
        if block is None and prev_blank and not in_list and not blank and INDENT_CODE.match(content):
            indent_code = True
            prev_blank = False
            continue
        if blank or HEADING.match(content) or RULE_LINE.match(content):
            prev_blank = blank
            continue
        if LINK_DEF.match(content) or is_html_block:
            prev_blank = False
            continue
        # The line under a quotation that names who said it.
        if quote and re.match(r"\s*(?:—|–|--)", content):
            prev_blank = False
            continue
        if TABLE_ROW.match(content):
            yield from cells(number, content)
            in_list = prev_blank = False
            continue
        marker = LIST_MARK.match(content)
        if marker:
            in_list = True
            content = content[marker.end() :]
        elif not INDENT_CODE.match(content):
            in_list = False
        if block is None:
            block = Block("item" if marker else "paragraph")
        block.add(number, content.strip())
        prev_blank = False
    if block:
        yield block


def cells(number: int, row: str):
    """Each cell of a table row as a block of its own. The rule row gives none."""
    hidden = row
    for found in CODE_SPAN.finditer(hidden):
        hidden = hidden[: found.start(2)] + MASK * len(found.group(2)) + hidden[found.end(2) :]
    cuts = [found.start() for found in re.finditer(r"(?<!\\)\|", hidden)]
    edges = [-1] + cuts + [len(row)]
    texts = [row[a + 1 : b].strip() for a, b in zip(edges, edges[1:])]
    texts = [text for text in texts if text]
    if texts and all(RULE_CELL.match(text) for text in texts):
        return
    for text in texts:
        if text in ("-", "–", "—"):
            continue
        block = Block("cell")
        block.add(number, text)
        yield block


def sentences(text: str):
    """Each sentence of a masked block, as a (start, end) pair."""
    start = 0
    for found in SENTENCE_END.finditer(text):
        if ABBREVIATION.search(text[: found.start()]):
            continue
        yield start, found.start()
        start = found.end()
    yield start, len(text)


def excerpt(text: str, start: int, end: int, room: int = 30) -> str:
    left, right = max(start - room, 0), min(end + room, len(text))
    return ("..." if left else "") + text[left:right].strip() + ("..." if right < len(text) else "")


def spoken(hidden: str) -> list[list[str]]:
    """The words of each sentence of a masked block, leaving out a sentence with none. A word wholly masked is no word."""
    said = []
    for start, end in sentences(hidden):
        words = [word for word in hidden[start:end].split() if word.strip(MASK)]
        if words:
            said.append(words)
    return said


def style(
    doc: Doc,
    max_words: int,
    max_paragraph: int = MAX_PARAGRAPH,
    max_sentences: int | None = None,
    band_words: bool = False,
) -> list[tuple[int, str, str]]:
    """Dash, long, paragraph, sentences and words: what a script can see of the house style.

    A table cell is no paragraph, and a list item is held to the same limit.
    Only a band sets a limit on the sentences in a paragraph, and a list item
    has none.
    """
    findings: list[tuple[int, str, str]] = []
    for block in prose_blocks(doc):
        hidden = mask(block.text)
        size = len(hidden.split())
        if block.kind != "cell" and size > max_paragraph:
            opening = " ".join(block.text.split()[:8])
            what = "list item" if block.kind == "item" else "paragraph"
            findings.append(
                (block.line_at(0), "paragraph", f'{size} words in one {what}, and the limit is {max_paragraph}: "{opening}..."')
            )
        if max_sentences is not None and block.kind == "paragraph":
            count = len(spoken(hidden))
            if count > max_sentences:
                opening = " ".join(block.text.split()[:8])
                findings.append(
                    (
                        block.line_at(0),
                        "sentences",
                        f'{count} sentences in one paragraph, and the limit is {max_sentences}: "{opening}..."',
                    )
                )
        for start, end in sentences(hidden):
            sentence = hidden[start:end]
            if not sentence.strip():
                continue
            words = len(sentence.split())
            if words > max_words:
                opening = " ".join(block.text[start:end].split()[:8])
                findings.append(
                    (block.line_at(start), "long", f'{words} words in one sentence, and the limit is {max_words}: "{opening}..."')
                )
            dash = DASH.search(sentence)
            if dash:
                at = start + dash.start()
                shown = excerpt(block.text, at, start + dash.end())
                findings.append((block.line_at(at), "dash", f'a dash used as punctuation: "{shown}"'))
            for word in WORD.finditer(sentence):
                advice = WORDS[" ".join(word.group().lower().split())]
                findings.append((block.line_at(start + word.start()), "words", f'"{word.group()}": {advice}'))
            for word in BAND_WORD.finditer(sentence) if band_words else ():
                found = word.group().lower()
                advice = BAND_WORDS.get(found) or BAND_WORDS.get(found.rstrip(".")) or BAND_WORDS[found.rstrip(".") + "."]
                findings.append((block.line_at(start + word.start()), "words", f'"{word.group()}": {advice}'))
    return findings


def declared(doc: Doc):
    """The readers a page names in its first paragraph, as (band, line, words), or None.

    The band is None when the ages match none of the bands. The words are the
    readers as the page names them, such as "readers aged 13 to 18".
    """
    block = next(iter(prose_blocks(doc)), None)
    if block is None or block.kind != "paragraph":
        return None
    found = DECLARED.search(block.text)
    if not found:
        return None
    line, who = block.line_at(found.start()), " ".join(found.group("who").split())
    if found.group("low") is None:
        return "dyslexia", line, who
    name = f"{int(found.group('low'))}-{int(found.group('high'))}"
    return (name if name in BANDS else None), line, who


def grade(doc: Doc):
    """The Automated Readability Index of a page, and what it is made of.

    ARI = 4.71 x (letters and digits per word) + 0.5 x (words per sentence) - 21.43,
    read from the paragraphs and list items the style rules read, on the
    masked text. A table cell is left out: it is a label, not a sentence. The
    result is (index, words a sentence, letters and digits a word, the share
    of words of seven letters or more), or None for a page with no prose.
    """
    words = sentences_seen = characters = long_words = 0
    for block in prose_blocks(doc):
        if block.kind == "cell":
            continue
        for said in spoken(mask(block.text)):
            sentences_seen += 1
            words += len(said)
            for word in said:
                characters += sum(1 for char in word if char.isalnum())
                long_words += sum(1 for char in word if char.isalpha()) >= 7
    if not words:
        return None
    per_word, per_sentence = characters / words, words / sentences_seen
    return 4.71 * per_word + 0.5 * per_sentence - 21.43, per_sentence, per_word, long_words / words


def graded(doc: Doc, name: str, band: Band) -> str | None:
    """The grade note for a page held to a band, or None for a page with no prose."""
    measured = grade(doc)
    if measured is None:
        return None
    index, per_sentence, per_word, share = measured
    said = (
        f"Automated Readability Index {index:.1f}, from {per_sentence:.1f} words a sentence and"
        f" {per_word:.1f} letters or digits a word, with {share:.0%} of the words seven letters or longer"
    )
    if band.grade is None:
        return f"{said}; the {name} band sets no target"
    if index <= band.grade:
        return f"{said}; the {name} target is {band.grade} or under"
    return f"{said}; the {name} target is {band.grade} or under, so look first at the long words and the long sentences"


def word_book() -> frozenset:
    """The words of the word book, or none when the file is missing."""
    try:
        lines = WORD_BOOK.read_text(encoding="utf-8").split("\n")
    except OSError:
        return frozenset()
    return frozenset(line.strip() for line in lines if line.strip() and not line.startswith("#"))


def known(word: str, book: frozenset, prefixed: bool = True) -> bool:
    """Whether the word book lists the word, or a form that leads to it."""
    if word in book or IRREGULAR.get(word) in book:
        return True
    if word.endswith("n't"):
        return known({"can't": "can", "won't": "will"}.get(word, word[:-3]), book)
    if CONTRACTION.search(word):
        return known(CONTRACTION.sub("", word), book)
    for ending, put in ENDINGS:
        if word.endswith(ending) and len(word) > len(ending) + 1:
            stem = word[: -len(ending)] + put
            if stem in book or IRREGULAR.get(stem) in book:
                return True
            # A doubled consonant: running, stopped, bigger.
            if ending in ("ing", "ed", "er", "est") and len(stem) > 2 and stem[-1] == stem[-2] and stem[:-1] in book:
                return True
    return prefixed and any(
        word.startswith(prefix) and len(word) - len(prefix) > 2 and known(word[len(prefix) :], book, False)
        for prefix in PREFIXES
    )


def vocabulary(doc: Doc) -> str | None:
    """The note on the words of a page the word book does not hold, or None.

    It reads the paragraphs and list items, masked as the style rules mask
    them. A word with a capital that the book does not hold is taken for a
    name, and left out of the count along with every abbreviation in capitals.
    """
    book = word_book()
    if not book:
        return None
    total, outside = 0, Counter()
    for block in prose_blocks(doc):
        if block.kind == "cell":
            continue
        for found in WORD_TOKEN.finditer(mask(block.text).replace("’", "'")):
            word, lowered = found.group(), found.group().lower()
            # A single letter is a list label or a piece of "i.e.", and a
            # band word is reported as a finding already.
            if len(lowered) == 1 and lowered not in book or lowered.rstrip(".") in ("etc", "vs", "cf", "via"):
                continue
            if known(lowered, book):
                total += 1
            elif not word[0].isupper():
                total += 1
                outside[lowered] += 1
    if not outside:
        return None
    grouped, forms = Counter(), {}
    for word, count in outside.items():
        stem = lemma(word, outside)
        grouped[stem] += count
        forms.setdefault(stem, Counter())[word] += count
    order = list(forms)
    named = sorted(grouped, key=lambda stem: (-grouped[stem], order.index(stem)))[:10]
    return (
        f"{sum(outside.values())} of {total} words are outside the VOA Learning English word book, most often: "
        + ", ".join(f"{forms[stem].most_common(1)[0][0]} ({grouped[stem]})" for stem in named)
        + "; explain each where it first appears, or choose a plainer word"
    )


def lemma(word: str, seen) -> str:
    """The form a word is counted under, so that "files" counts with "file", and "checks" with "checked".

    A plain form the page also uses wins; otherwise the first rough stem does.
    """
    candidates = []
    if word.endswith("ies") and len(word) > 4:
        candidates.append(word[:-3] + "y")
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        candidates.append(word[:-1])
    if word.endswith("es") and len(word) > 4:
        candidates.append(word[:-2])
    if word.endswith("ing") and len(word) > 5:
        candidates += [word[:-3], word[:-3] + "e"]
    if word.endswith("ed") and len(word) > 4:
        candidates += [word[:-2], word[:-1]]
    return next((candidate for candidate in candidates if candidate in seen), candidates[0] if candidates else word)


def unseen_char(char: str) -> bool:
    """A character no reader sees: a format character, or a control character other than a tab."""
    kind = unicodedata.category(char)
    return kind == "Cf" or (kind == "Cc" and char not in "\t\n")


def described(char: str) -> str:
    return f"U+{ord(char):04X} {unicodedata.name(char, '')}".rstrip()


def unseen(doc: Doc) -> list[tuple[int, str, str]]:
    """Each line that holds a character no reader sees, frontmatter and code included."""
    findings: list[tuple[int, str, str]] = []
    for number, line in enumerate(doc.lines, start=1):
        chars = sorted({char for char in line if unseen_char(char)})
        if chars:
            names = ", ".join(described(char) for char in chars)
            findings.append((number, "unseen", f"{names}: a character no reader sees; delete it, or write it as an escape in code"))
    return findings


# --- what a rewording must leave alone ----------------------------------------


class Kept:
    """What one version of a file holds besides its wording."""

    def __init__(self, doc: Doc):
        self.fences: list[tuple[int, str]] = []
        self.related: list[str] = []
        self.related_at = 1
        self.questions: list[str] = []
        self.questions_at = 1
        self.headings: list[tuple[int, str]] = []
        self.list_items = 0
        self.table_rows = 0
        self.breaks = 0
        self.codes: list[tuple[str, int]] = []
        self.html: list[tuple[str, int]] = []
        self.links: list[tuple[str, int]] = []
        self.numbers: list[tuple[str, int]] = []
        self.quotes: list[tuple[str, int]] = []
        self.rfc: list[tuple[str, int]] = []
        self.number_words: list[tuple[str, int]] = []
        self.date_words: list[tuple[str, int]] = []
        self.strength: Counter = Counter()
        self.words = 0
        self._read(doc)

    def _read(self, doc: Doc) -> None:
        block: Block | None = None
        fence: str | None = None
        fenced: list[str] = []
        fence_at = 0
        related = questions = False
        block_is_list = block_is_table = False
        prev_in_block = ""

        def flush() -> None:
            nonlocal block, block_is_list, block_is_table, prev_in_block
            if block:
                self._tokens(block)
            block = None
            block_is_list = block_is_table = False
            prev_in_block = ""

        for number, line in doc.numbered_body():
            if fence:
                fenced.append(line)
                if closes(fence, line):
                    self.fences.append((fence_at, textwrap.dedent("\n".join(fenced))))
                    fence = None
                continue
            opening = FENCE.match(line)
            if opening:
                flush()
                fence, fenced, fence_at = opening.group(1), [line], number
                continue
            if line.strip() == RELATED_OPEN and not related:
                flush()
                related, self.related_at = True, number
            if related:
                self.related.append(line)
                related = line.strip() != RELATED_CLOSE
                continue
            if line.rstrip() == OPEN_QUESTIONS:
                flush()
                questions, self.questions_at = True, number
                self.questions.append(line.rstrip())
                continue
            if questions:
                if not HEADING.match(line):
                    self.questions.append(line.rstrip())
                    continue
                questions = False
            if not line.strip():
                flush()
                continue
            definition = LINK_DEF.match(line)
            if definition:
                self.links.append((definition.group(1), number))
            content = QUOTE_MARK.sub("", line, count=1)
            if HEADING.match(content):
                flush()
                self.headings.append((number, " ".join(content.split())))
            # A list, ordered or table marker counts only where it opens a
            # block or continues one of its own kind. On a wrapped prose line it
            # is text, and a number that starts such a line is a fact, not an
            # item number - so re-laying a paragraph out does not seem to change
            # a list or lose a year.
            at_start = block is None
            is_item = bool(LIST_MARK.match(content)) and (at_start or block_is_list)
            if is_item:
                self.list_items += 1
            is_row = False
            if (at_start or block_is_table) and TABLE_ROW.match(content):
                row = [cell for cell in re.split(r"(?<!\\)\|", content) if cell.strip()]
                if not all(RULE_CELL.match(cell) for cell in row):
                    self.table_rows += 1
                is_row = True
            if is_item:  # the number of an ordered list item is a marker, not a fact
                line = ORDERED_MARK.sub(lambda found: found.group(1) + " " * len(found.group(2)) + found.group(3), line)
            # A hard line break joins two lines of one block, so it is the kind
            # of layout a rewording leaves alone; count one where the line before
            # this one in the block ended with it.
            if block is None:
                block = Block()
                block_is_list, block_is_table = is_item, is_row
            elif HARD_BREAK.search(prev_in_block):
                self.breaks += 1
            prev_in_block = line
            block.add(number, line)
            if HEADING.match(content):
                flush()
        if fence:
            self.fences.append((fence_at, textwrap.dedent("\n".join(fenced))))
        flush()
        while self.questions and not self.questions[-1]:
            self.questions.pop()

    def _tokens(self, block: Block) -> None:
        text = block.text
        hidden = text

        def take(pattern: re.Pattern, into: list[tuple[str, int]], group: int = 1, whole: bool = False) -> None:
            """Record each match, read from the unmasked text, then mask it."""
            nonlocal hidden
            for found in pattern.finditer(hidden):
                token = " ".join(text[found.start(group) : found.end(group)].split())
                into.append((token, block.line_at(found.start())))
            for found in list(pattern.finditer(hidden)):
                a, b = (found.start(), found.end()) if whole else (found.start(group), found.end(group))
                hidden = hidden[:a] + MASK * (b - a) + hidden[b:]

        take(CODE_SPAN, self.codes, group=2)
        for found in WIKILINK.finditer(hidden):
            target = text[found.start(1) : found.end(1)].split("|")[0].strip()
            self.links.append((target, block.line_at(found.start())))
        take(WIKILINK, [])
        take(INLINE_LINK, self.links)
        take(AUTOLINK, self.links)
        take(HTML_ATTR, self.links)
        # An inline HTML tag carries meaning a rewording must not drop: a <br>, a
        # <sub>, a <kbd>. Record its name (its target is already a link above),
        # then mask it so it counts as neither a word nor anything else.
        for found in HTML_TAG.finditer(hidden):
            self.html.append((tag_name(found.group()), block.line_at(found.start())))
        for found in list(HTML_TAG.finditer(hidden)):
            hidden = hidden[: found.start()] + MASK * len(found.group()) + hidden[found.end() :]
        take(BARE_URL, self.links, group=0)
        for found in QUOTED.finditer(hidden):
            group = 1 if found.group(1) is not None else 2
            quoted = " ".join(text[found.start(group) : found.end(group)].split())
            self.quotes.append((quoted, block.line_at(found.start())))
        for pattern, into in ((NUMBER, self.numbers), (RFC_WORD, self.rfc)):
            for found in pattern.finditer(hidden):
                into.append((found.group(), block.line_at(found.start())))
        for found in NUMBER_WORD.finditer(hidden):
            self.number_words.append((found.group().lower(), block.line_at(found.start())))
        for found in DATE_WORD.finditer(hidden):
            self.date_words.append((found.group().rstrip("s"), block.line_at(found.start())))
        lowered = hidden.lower()
        for word in STRENGTH:
            self.strength[word] += len(re.findall(rf"\b{word}\b", lowered))
        self.strength["a negation"] += len(NEGATION.findall(hidden))
        self.words += len(hidden.split())


def times(count: int) -> str:
    return "once" if count == 1 else f"{count} times"


def differences(rule: str, what: str, old: list[tuple[str, int]], new: list[tuple[str, int]]):
    """Each token whose count changed, as (line, rule, message, how)."""
    before, after = Counter(token for token, _ in old), Counter(token for token, _ in new)
    old_line = {token: line for token, line in reversed(old)}
    new_line = {token: line for token, line in reversed(new)}
    for token in sorted(set(before) | set(after)):
        was, now = before[token], after[token]
        if was == now:
            continue
        if now == 0:
            yield old_line[token], rule, f'{what} "{token}" is gone (line {old_line[token]} of the earlier text)', "gone"
        elif was == 0:
            yield new_line[token], rule, f'{what} "{token}" is new', "new"
        else:
            how = "fewer" if now < was else "more"
            yield new_line[token], rule, f'{what} "{token}" appears {times(now)}, and the earlier text had it {times(was)}', how


def compare(path: Path, old: Doc, new: Doc, expect_concept: bool):
    """What differs between two versions besides the wording: findings, notes, and the words each version holds."""
    findings: list[tuple[int, str, str]] = []
    notes: list[tuple[int, str, str]] = []
    was, now = standing(old, expect_concept), standing(new, expect_concept)
    concept = was[0] != "plain" or now[0] != "plain"

    # The frontmatter, byte for byte.
    if old.fm != new.fm or old.unclosed != new.unclosed:
        line = 1
        if old.fm is not None and new.fm is not None:
            pairs = zip(old.fm + [None] * len(new.fm), new.fm + [None] * len(old.fm))
            line = 2 + next(i for i, (a, b) in enumerate(pairs) if a != b)
        findings.append((line, "frontmatter", "this line differs from the earlier text, and a rewording changes no frontmatter"))

    # A character no reader sees, which no rewording has cause to add.
    had = Counter(char for line in old.lines for char in line if unseen_char(char))
    has = Counter(char for line in new.lines for char in line if unseen_char(char))
    for char in sorted(has):
        if has[char] > had[char]:
            line = next(number for number, text in enumerate(new.lines, start=1) if char in text)
            findings.append((line, "unseen", f"{described(char)} is new, and a rewording adds no character a reader cannot see"))

    # A concept somebody vouched for keeps its body. No flag turns this off.
    if concept and old.body != new.body:
        said = {
            "person": "a person wrote this concept ({}), so its body must stay as it was",
            "confirmed": "a person confirmed this concept ({}), so its body must stay as it was; send it back through ktl-curator to have it reworded",
            "retired": "this concept is retired, so its body must stay as it was",
            "unreadable": "the script cannot read this frontmatter, so it cannot tell who vouched for the concept",
        }
        for rule, words in dict((was, now)).items() if was != now else [was]:
            if rule in said:
                actor = words[words.find("(") + 1 : -1] if "(" in words else ""
                findings.append((1, rule, said[rule].format(actor)))
        if now[0] == "unrecorded":
            notes.append((1, "unrecorded", "no generated record says who wrote this concept; reword it only when a person named it"))

    a, b = Kept(old), Kept(new)

    texts_a, texts_b = [text for _, text in a.fences], [text for _, text in b.fences]
    if len(texts_a) != len(texts_b):
        findings.append((1, "fence", f"{len(texts_b)} fenced blocks, and the earlier text had {len(texts_a)}"))
    for index, (text_a, (line, text_b)) in enumerate(zip(texts_a, b.fences), start=1):
        if text_a != text_b:
            findings.append((line, "fence", f"fenced block {index} differs from the earlier text"))

    for rule, what, list_a, list_b in (
        ("link", "the link target", a.links, b.links),
        ("digits", "the number", a.numbers, b.numbers),
        ("quote", "the quoted text", a.quotes, b.quotes),
        ("rfc2119", "the keyword", a.rfc, b.rfc),
        ("html", "the inline HTML tag", a.html, b.html),
    ):
        findings.extend((line, rule, words) for line, rule, words, _ in differences(rule, what, list_a, list_b))
    for line, rule, words, how in differences("code", "the code span", a.codes, b.codes):
        (findings if how == "gone" else notes).append((line, rule, words))

    if a.related != b.related:
        findings.append((b.related_at, "related", "the lokf:related region differs from the earlier text"))
    if a.questions != b.questions:
        findings.append((b.questions_at, "open-questions", f'the "{OPEN_QUESTIONS}" section differs from the earlier text'))
    if b.list_items < a.list_items:
        findings.append((1, "list", f"{b.list_items} list items, and the earlier text had {a.list_items}"))
    if b.table_rows < a.table_rows:
        findings.append((1, "table", f"{b.table_rows} table rows, and the earlier text had {a.table_rows}"))
    if a.breaks != b.breaks:
        findings.append((1, "hard-break", f"{b.breaks} hard line breaks, and the earlier text had {a.breaks}; a rewording keeps the breaks a reader sees"))

    heads_a, heads_b = [text for _, text in a.headings], [text for _, text in b.headings]
    if heads_a != heads_b:
        pairs = list(zip(heads_a + [""] * len(heads_b), b.headings + [(1, "")] * len(heads_a)))
        before, (line, after) = next((x, y) for x, y in pairs if x != y[1])
        words = f'a heading differs from the earlier text: "{after}" was "{before}"'
        (findings if concept else notes).append((line, "heading", words + ("" if concept else "; links may point at it")))

    for line, rule, words, _ in differences("number-word", "the number word", a.number_words, b.number_words):
        notes.append((line, rule, words + "; digits cannot show whether a count changed"))
    for line, rule, words, _ in differences("date-word", "the day or month", a.date_words, b.date_words):
        notes.append((line, rule, words + "; digits cannot show whether a date changed"))
    for word in (*STRENGTH, "a negation"):
        if a.strength[word] != b.strength[word]:
            name = word if word == "a negation" else f'"{word}"'
            notes.append((1, "strength", f"{name} appears {times(b.strength[word])}, and the earlier text had it {times(a.strength[word])}"))
    # A fifth either way, as SKILL.md says: more than a fifth more words, or
    # fewer than four fifths of them. The earlier 8% growth floor, and the
    # 40-word floor that hid a third cut of a short text, are gone.
    if b.words > a.words * 1.2:
        notes.append((1, "growth", f"{b.words} words, and the earlier text had {a.words}; a rewording adds no fact"))
    if b.words < a.words * 0.8:
        notes.append((1, "shrink", f"{b.words} words, and the earlier text had {a.words}; a rewording cuts words that carry nothing, and no fact"))

    return findings, notes, (a.words, b.words)


# --- the four uses -------------------------------------------------------------


def earlier(path: Path, ref: str) -> str | None:
    """The file as git holds it at REF, or None when REF holds no such file.

    The real path is resolved first: git stores `knowledge_bundle` as a link
    and cannot show a file through it.
    """
    real = path.resolve()
    top = subprocess.run(
        ["git", "-C", str(real.parent), "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
    )
    if top.returncode != 0:
        raise Usage(f"{path} is not inside a git work tree, so there is no earlier version; keep a copy and use --before")
    root = Path(top.stdout.strip()).resolve()
    known = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"], capture_output=True, check=False
    )
    if known.returncode != 0:
        raise Usage(f"{ref} names no commit in {root}")
    shown = subprocess.run(
        ["git", "-C", str(root), "show", f"{ref}:{real.relative_to(root).as_posix()}"], capture_output=True, check=False
    )
    return normalise(shown.stdout) if shown.returncode == 0 else None


def reserved_in_bundle(path: Path) -> bool:
    return path.name in RESERVED and bundle_root(path) is not None


def check_style(files: list[Path], max_words: int | None = None, max_paragraph: int | None = None, audience: str | None = None):
    """The style rules for each file, and a character no reader sees in any of them.

    A file is held to the band --audience names, or else to the band its
    first paragraph names, or else to the adult limits. --max-words and
    --max-paragraph set their own limit over any band's.
    """
    findings, notes = [], []
    for path in files:
        doc = Doc(read(path))
        found = unseen(doc)
        if reserved_in_bundle(path):
            notes.append((path, 1, "reserved", "a reserved bundle file is not held to the style rules"))
        else:
            name = audience
            said = declared(doc)
            if said:
                named, line, who = said
                if audience and named != audience:
                    found.append((line, "audience", f"the page says it is for {who}, and --audience asked for {audience}"))
                elif not audience and named:
                    name = named
                    notes.append((path, line, "audience", f"the page says it is for {who}, so the {named} limits apply"))
                elif not audience:
                    notes.append((path, line, "audience", f"the page says it is for {who}, which no band covers, so the adult limits apply"))
            band = BANDS.get(name) if name else None
            words = max_words if max_words is not None else band.words if band else MAX_WORDS
            paragraph = max_paragraph if max_paragraph is not None else band.paragraph if band else MAX_PARAGRAPH
            found += style(doc, words, paragraph, band.sentences if band else None, band_words=band is not None)
            for rule, note in (("grade", graded(doc, name, band)), ("vocabulary", vocabulary(doc))) if band else ():
                if note:
                    notes.append((path, 1, rule, note))
        findings.extend((path, *finding) for finding in sorted(found, key=lambda finding: finding[0]))
    return findings, notes, f"{len(files)} file(s), and nothing a script can see breaks the style rules or hides from a reader"


def check_pair(label: Path, old_text: str, new_text: str, in_bundle: bool):
    """Compare two versions of one file, with the bundle's reserved files set apart. The third value is the words before and after, which a reserved file does not count towards."""
    if in_bundle and label.name == "log.md":
        return [], [(label, 1, "reserved", "the bundle's log is not compared; ktl-prose adds one line to it")], (0, 0)
    old, new = Doc(old_text), Doc(new_text)
    if in_bundle and label.name in RESERVED:
        if old.lines != new.lines:
            return [(label, 1, "reserved", "ktl-prose never rewords a reserved bundle file")], [], (0, 0)
        return [], [], (0, 0)
    findings, notes, words = compare(label, old, new, expect_concept=in_bundle)
    return [(label, *found) for found in findings], [(label, *note) for note in notes], words


def counted(was: int, now: int) -> str:
    """The words before and after, for the hand-off: a program counts them, so no model has to."""
    return f"{now} words, and the earlier text had {was}"


def check_before(old_path: Path, new_path: Path):
    in_bundle = bundle_root(new_path) is not None
    findings, notes, (was, now) = check_pair(new_path, read(old_path), read(new_path), in_bundle)
    return findings, notes, f"only the wording differs (1 file): {counted(was, now)}"


def check_against(ref: str, files: list[Path]):
    if ref.startswith("-") or not re.fullmatch(r"[\w./@^~{}-]+", ref):
        raise Usage(f"{ref!r} is not a revision this script will pass to git")
    findings, notes = [], []
    was = now = 0
    for path in files:
        new_text = read(path)
        old_text = earlier(path, ref)
        if old_text is None:
            findings.append(
                (path, 1, "baseline", f"git holds no version of this file at {ref}; keep a copy before rewording it and compare with --before")
            )
            continue
        found, noted, words = check_pair(path, old_text, new_text, bundle_root(path) is not None)
        findings.extend(found)
        notes.extend(noted)
        was, now = was + words[0], now + words[1]
    return findings, notes, f"only the wording differs ({len(files)} file(s) against {ref}): {counted(was, now)}"


def list_bundle(directory: Path) -> int:
    """Every Markdown file of a bundle with its verdict: `rewrite` or `skip: <why>`."""
    if not directory.is_dir():
        raise Usage(f"no bundle directory at {directory}")
    tally: Counter = Counter()
    for path in sorted(directory.rglob("*.md")):
        if ".obsidian" in path.parts:
            continue
        if path.name in RESERVED:
            rule, words = "reserved", "reserved file"
        else:
            rule, words = standing(Doc(read(path)), expect_concept=True)
        tally[rule] += 1
        print(f"{path}: {words if rule == 'rewrite' else 'skip: ' + words}")
    left = ", ".join(
        f"{tally[rule]} {name}"
        for rule, name in (
            ("confirmed", "confirmed by a person"),
            ("person", "written by a person"),
            ("retired", "retired"),
            ("unreadable", "unreadable"),
            ("unrecorded", "with no record of who wrote them"),
            ("reserved", "reserved"),
        )
        if tally[rule]
    )
    print(f"OK: {tally['rewrite']} to reword, and {sum(tally.values()) - tally['rewrite']} to leave ({left or 'none'})")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="prose-check.py",
        usage="prose-check.py [--audience BAND] [--max-words N] [--max-paragraph N] FILE... | --before OLD NEW | --against REF FILE... | --bundle DIR",
        description="Report what a script can see of plain prose, and prove that a rewording changed only wording.",
    )
    parser.add_argument("files", nargs="*", type=Path, metavar="FILE")
    parser.add_argument("--before", nargs=2, type=Path, metavar=("OLD", "NEW"))
    parser.add_argument("--against", metavar="REF")
    parser.add_argument("--bundle", type=Path, metavar="DIR")
    parser.add_argument("--audience", choices=sorted(BANDS), metavar="BAND")
    parser.add_argument("--max-words", type=int, metavar="N")
    parser.add_argument("--max-paragraph", type=int, metavar="N")
    if len(argv) < 2:
        parser.print_usage(sys.stderr)
        return 2
    args = parser.parse_args(argv[1:])
    chosen = [name for name in ("before", "against", "bundle") if getattr(args, name) is not None]
    if len(chosen) > 1:
        parser.error("give one of --before, --against and --bundle")
    if (args.before or args.bundle) and args.files:
        parser.error(f"--{chosen[0]} takes no FILE")
    if not args.before and not args.bundle and not args.files:
        parser.error("name at least one FILE")
    if args.audience and chosen:
        parser.error(f"--audience holds a FILE to a band's limits, and --{chosen[0]} compares; run them apart")

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    try:
        if args.bundle:
            return list_bundle(args.bundle)
        if args.before:
            findings, notes, fine = check_before(*args.before)
        elif args.against:
            findings, notes, fine = check_against(args.against, args.files)
        else:
            findings, notes, fine = check_style(args.files, args.max_words, args.max_paragraph, args.audience)
    except Usage as exc:
        print(f"prose-check.py: {exc}", file=sys.stderr)
        return 2

    for path, line, rule, words in notes:
        print(f"note: {path}:{line}: {rule}: {words}", file=sys.stderr)
    for path, line, rule, words in findings:
        print(f"{path}:{line}: {rule}: {words}")
    if findings:
        return 1
    print(f"OK: {fine}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
