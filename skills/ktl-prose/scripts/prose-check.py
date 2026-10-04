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
#   prose-check.py --before OLD NEW       what differs besides the wording
#   prose-check.py --against REF FILE...  the same, against the version git holds at REF
#   prose-check.py --bundle DIR           which files of a bundle ktl-prose may reword
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
# The script reads the files it is given and asks git for an earlier version.
# It writes nothing and opens no network connection. It needs python3 3.9 or
# later and nothing else. `uv run` reads the empty dependency block above.

from __future__ import annotations

import argparse
import bisect
import re
import subprocess
import sys
import textwrap
import unicodedata
from collections import Counter
from pathlib import Path

RESERVED = {"index.md", "log.md", "diataxis.md"}
MAX_WORDS = 40
# The Federal Plain Language Guidelines' ceiling for a paragraph.
MAX_PARAGRAPH = 150
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
            continue
        if line.strip() == RELATED_OPEN:
            related = True
        if related:
            related = line.strip() != RELATED_CLOSE
            if block:
                yield block
            block = None
            continue
        if comment:
            end = line.find("-->")
            if end < 0:
                continue
            line, comment = " " * (end + 3) + line[end + 3 :], False
        line = COMMENT.sub(lambda found: " " * len(found.group()), line)
        if "<!--" in line:
            line, comment = line[: line.index("<!--")], True

        quote = QUOTE_MARK.match(line)
        content = line[quote.end() :] if quote else line
        breaks = (
            not content.strip()
            or bool(quote) != quoted
            or HEADING.match(content)
            or RULE_LINE.match(content)
            or LINK_DEF.match(content)
            or HTML_LINE.match(content)
            or TABLE_ROW.match(content)
            or LIST_MARK.match(content)
        )
        if breaks and block:
            yield block
            block = None
        quoted = bool(quote)
        if not content.strip() or HEADING.match(content) or RULE_LINE.match(content):
            continue
        if LINK_DEF.match(content) or HTML_LINE.match(content):
            continue
        # The line under a quotation that names who said it.
        if quote and re.match(r"\s*(?:—|–|--)", content):
            continue
        if TABLE_ROW.match(content):
            yield from cells(number, content)
            continue
        marker = LIST_MARK.match(content)
        if marker:
            content = content[marker.end() :]
        if block is None:
            block = Block("item" if marker else "paragraph")
        block.add(number, content.strip())
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


def style(doc: Doc, max_words: int, max_paragraph: int = MAX_PARAGRAPH) -> list[tuple[int, str, str]]:
    """Dash, long, paragraph and words: what a script can see of the house style.

    A table cell is no paragraph, and a list item is held to the same limit.
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
    return findings


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
        self.codes: list[tuple[str, int]] = []
        self.links: list[tuple[str, int]] = []
        self.numbers: list[tuple[str, int]] = []
        self.quotes: list[tuple[str, int]] = []
        self.rfc: list[tuple[str, int]] = []
        self.number_words: list[tuple[str, int]] = []
        self.strength: Counter = Counter()
        self.words = 0
        self._read(doc)

    def _read(self, doc: Doc) -> None:
        block: Block | None = None
        fence: str | None = None
        fenced: list[str] = []
        fence_at = 0
        related = questions = False

        def flush() -> None:
            nonlocal block
            if block:
                self._tokens(block)
            block = None

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
            if LIST_MARK.match(content):
                self.list_items += 1
            if TABLE_ROW.match(content):
                row = [cell for cell in re.split(r"(?<!\\)\|", content) if cell.strip()]
                if not all(RULE_CELL.match(cell) for cell in row):
                    self.table_rows += 1
            # The number of an ordered list item is a marker, not a fact.
            line = ORDERED_MARK.sub(lambda found: found.group(1) + " " * len(found.group(2)) + found.group(3), line)
            if block is None:
                block = Block()
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
    """What differs between two versions besides the wording: findings, then notes."""
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

    heads_a, heads_b = [text for _, text in a.headings], [text for _, text in b.headings]
    if heads_a != heads_b:
        pairs = list(zip(heads_a + [""] * len(heads_b), b.headings + [(1, "")] * len(heads_a)))
        before, (line, after) = next((x, y) for x, y in pairs if x != y[1])
        words = f'a heading differs from the earlier text: "{after}" was "{before}"'
        (findings if concept else notes).append((line, "heading", words + ("" if concept else "; links may point at it")))

    for line, rule, words, _ in differences("number-word", "the number word", a.number_words, b.number_words):
        notes.append((line, rule, words + "; digits cannot show whether a count changed"))
    for word in (*STRENGTH, "a negation"):
        if a.strength[word] != b.strength[word]:
            name = word if word == "a negation" else f'"{word}"'
            notes.append((1, "strength", f"{name} appears {times(b.strength[word])}, and the earlier text had it {times(a.strength[word])}"))
    if b.words > a.words * 1.08 and b.words - a.words > 40:
        notes.append((1, "growth", f"{b.words} words, and the earlier text had {a.words}; a rewording adds no fact"))

    return findings, notes


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


def check_style(files: list[Path], max_words: int, max_paragraph: int = MAX_PARAGRAPH):
    """The style rules for each file, and a character no reader sees in any of them."""
    findings, notes = [], []
    for path in files:
        doc = Doc(read(path))
        found = unseen(doc)
        if reserved_in_bundle(path):
            notes.append((path, 1, "reserved", "a reserved bundle file is not held to the style rules"))
        else:
            found += style(doc, max_words, max_paragraph)
        findings.extend((path, *finding) for finding in sorted(found, key=lambda finding: finding[0]))
    return findings, notes, f"{len(files)} file(s), and nothing a script can see breaks the style rules or hides from a reader"


def check_pair(label: Path, old_text: str, new_text: str, in_bundle: bool):
    """Compare two versions of one file, with the bundle's reserved files set apart."""
    if in_bundle and label.name == "log.md":
        return [], [(label, 1, "reserved", "the bundle's log is not compared; ktl-prose adds one line to it")]
    old, new = Doc(old_text), Doc(new_text)
    if in_bundle and label.name in RESERVED:
        if old.lines != new.lines:
            return [(label, 1, "reserved", "ktl-prose never rewords a reserved bundle file")], []
        return [], []
    findings, notes = compare(label, old, new, expect_concept=in_bundle)
    return [(label, *found) for found in findings], [(label, *note) for note in notes]


def check_before(old_path: Path, new_path: Path):
    in_bundle = bundle_root(new_path) is not None
    findings, notes = check_pair(new_path, read(old_path), read(new_path), in_bundle)
    return findings, notes, "only the wording differs (1 file)"


def check_against(ref: str, files: list[Path]):
    if ref.startswith("-") or not re.fullmatch(r"[\w./@^~{}-]+", ref):
        raise Usage(f"{ref!r} is not a revision this script will pass to git")
    findings, notes = [], []
    for path in files:
        new_text = read(path)
        old_text = earlier(path, ref)
        if old_text is None:
            findings.append(
                (path, 1, "baseline", f"git holds no version of this file at {ref}; keep a copy before rewording it and compare with --before")
            )
            continue
        found, noted = check_pair(path, old_text, new_text, bundle_root(path) is not None)
        findings.extend(found)
        notes.extend(noted)
    return findings, notes, f"only the wording differs ({len(files)} file(s) against {ref})"


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
        usage="prose-check.py [--max-words N] [--max-paragraph N] FILE... | --before OLD NEW | --against REF FILE... | --bundle DIR",
        description="Report what a script can see of plain prose, and prove that a rewording changed only wording.",
    )
    parser.add_argument("files", nargs="*", type=Path, metavar="FILE")
    parser.add_argument("--before", nargs=2, type=Path, metavar=("OLD", "NEW"))
    parser.add_argument("--against", metavar="REF")
    parser.add_argument("--bundle", type=Path, metavar="DIR")
    parser.add_argument("--max-words", type=int, default=MAX_WORDS, metavar="N")
    parser.add_argument("--max-paragraph", type=int, default=MAX_PARAGRAPH, metavar="N")
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
            findings, notes, fine = check_style(args.files, args.max_words, args.max_paragraph)
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
