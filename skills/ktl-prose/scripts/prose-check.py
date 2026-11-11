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
#   prose-check.py FILE...                what a script sees: dash, long, paragraph, sentences, words, unseen
#   prose-check.py --audience BAND FILE...  the same at the limits of a band of readers, with a grade
#   prose-check.py --before OLD NEW       what differs besides the wording, and the words before and after
#   prose-check.py --against REF FILE...  the same, against the version git holds at REF
#   prose-check.py --bundle DIR           which files of a bundle ktl-prose may reword, and its readers
#   prose-check.py --derived-from ADULT YOUNG  what a retelling holds that the text it retells does not
#
# A FILE is Markdown, or a script. A `.sh`, `.bash`, `.py`, `.yaml`, `.yml`
# or `.toml` file, or a justfile, is read as its `#` comments and, in Python,
# its docstrings: each block of comment lines is a paragraph, and an empty
# comment line splits one. The shebang, a directive such as `# shellcheck`, a
# `# /// script` block and the body of a heredoc are left out. Code is never
# read, so a fact in it is not checked.
#
# A comment's layout is read as a person reads it. An indented line laid out
# in columns, as a table of options or exit codes is, starts a row. Its first
# column is a name. The rest of the row, with the lines indented under it, is
# read as one table cell. An indented line that follows a `Usage` line, a
# line ending with a colon or an empty line is a command, and is not read. So
# a table or a command is never taken for one long sentence.
#
# A band holds a page to the limits references/young-readers.md gives for
# readers aged 8 to 12, aged 13 to 18, or dyslexic. A page that opens by
# naming its readers, as "This page is for readers aged 13 to 18." does, is
# held to that band with no flag. A band sets its own count of sentences in
# a paragraph, and the script notes the page's Automated Readability Index
# with the counts it comes from. The index is a hint, never a finding.
#
# A retelling may say less than the text it retells, and never more. So
# --derived-from reports a number, a link, a code span, a quotation, an HTML
# tag or a fenced block that the retelling holds and the adult text does not,
# and notes what the retelling left out. The retelling must link the text it
# retells in its first paragraph, and in a bundle name it under derivedFrom.
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
# A pass says that what the script reads came through, and not that the meaning
# held, so its OK line says no more than that. references/limits.md lists what
# it cannot see.
#
# A comparison reads a list item and a table row as a sentence each. In a
# sentence that otherwise stayed it stops a word given way to its opposite, and
# a negative gained or lost with every other word in place. It stops one number
# word given way to another, and two runs of words that changed places. It
# stops a number, a link or a code span that changed places with one in another
# sentence or row. It stops the steps of a numbered list in a new order, and a
# paragraph cut in two inside a sentence. In a script it stops a change to any
# line that is not prose.
#
# A comparison notes, with the line, a word of strength that came or went and
# one word that gave way to another. It notes the words a page lost or gained.
#
# The script reads the files it is given, and the word book in the skill's
# assets/ folder, and asks git for an earlier version. It writes nothing
# and opens no network connection. It needs python3 3.9 or later and
# nothing else. `uv run` reads the empty dependency block above.

from __future__ import annotations

import argparse
import bisect
import difflib
import heapq
import html
import re
import subprocess
import sys
import textwrap
import unicodedata
from urllib.parse import unquote
from collections import Counter, namedtuple
from pathlib import Path

RESERVED = {"index.md", "log.md", "diataxis.md"}
MAX_WORDS = 40
# The Federal Plain Language Guidelines' ceiling for a paragraph.
MAX_PARAGRAPH = 150
# The top of the same guidelines' "three to eight sentences" for a paragraph.
# A band sets its own count, and a list item has none.
MAX_SENTENCES = 8
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
# The line a person puts in the bundle's curation policy to declare its
# younger readers, as "Younger readers: 8-12" or "Younger readers: no".
YOUNGER = re.compile(r"^\s*Younger readers\s*:\s*(.*?)\s*$", re.I)
NAMES_READERS = re.compile(r"\bfor readers aged (\d{1,2}) to (\d{1,2})\b", re.I)
# One private-use character stands in for each character a rule skips, so
# every offset and line number stays true after masking.
MASK = ""

# The words the first hand pass cut, the stock phrases it replaced, and two a
# later reading added: an intensifier that points at a comparison the
# sentence never makes, and the tail of a negative that is already whole.
# "actually", "really", "simply" and "just" stay off the list on purpose: the
# second pass kept every one of them.
WORDS = {
    "deliberately": "cut it, or say what was chosen",
    "honestly": "cut it",
    "outright": "cut it, or say what it is compared with",
    "at all": "cut it: the negative before it is already whole",
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
# A listed phrase that is not one when certain words follow it. In "at all
# of them" and "at all times", "all" belongs to the words after it, and no
# negative comes before.
NOT_BEFORE = {"at all": r"(?!\s+(?:of|times|costs|hours|levels|stages|points)\b)"}
# A letter, a digit, an underscore or a hyphen on either side makes another
# word: `arm64`, `wire-format`.
WORD = re.compile(
    r"(?<![\w-])(?:"
    + "|".join(
        re.escape(word) + NOT_BEFORE.get(word, "")
        for word in sorted((word for word in WORDS if word != "e.g."), key=len, reverse=True)
    )
    + r")(?![\w-])|(?<![A-Za-z])e\.g\.",
    re.I,
)
# The files read as scripts rather than as Markdown, by suffix; a file called
# justfile is one too. In a script the prose is its whole-line `#` comments,
# and in Python its docstrings as well.
SCRIPT_SUFFIXES = {".sh", ".bash", ".py", ".yaml", ".yml", ".toml"}
COMMENT_LINE = re.compile(r"^\s*#(.*)$")
# A comment that is not prose: the shebang, and a directive a tool reads.
DIRECTIVE = re.compile(r"^#(?:!|\s*(?:shellcheck|noqa|type:|fmt:|ruff:|pylint:|mypy:|pyright:|yamllint|-\*-)\b)")
# The `# /// script` block of PEP 723, which names a script's packages.
SCRIPT_BLOCK = re.compile(r"^#\s*///\s*\w+\s*$")
SCRIPT_BLOCK_END = re.compile(r"^#\s*///\s*$")
HEREDOC = re.compile(r"(?<!<)<<(?!<)-?\s*(['\"]?)([A-Za-z_]\w*)\1")
DOCSTRING = re.compile(r"^(\s*)[rRuUbB]{0,2}(\"\"\"|''')(.*)$")
# A comment's columns: two spaces or more between words. Two spaces after a
# full stop are a sentence's own spacing, and three or more are a column.
COLUMN_GAP = re.compile(r"(?:[^\s.!?] {2,}|\S {3,})\S")
# How an indented line that opens a block starts when it is prose, not a
# command: a capital that does not set a variable, a code span or emphasis.
SENTENCE_START = re.compile(r"^\s*(?:[A-Z](?![A-Z0-9_]*=)|[`*])")
# An item numbered with a letter as well, as `2a.` is, which Markdown does
# not count as a list item.
LETTERED_MARK = re.compile(r"^\s*\d+[a-z][.)]\s+")
USAGE = re.compile(r"^\s*usage\s*[:,]", re.I)
# A spaced hyphen, an em dash anywhere, and an en dash that is not a range. A
# spaced hyphen before a digit is a minus or a range, and a double one before
# a placeholder ends a command's options, as in `cmd -- <args>`: neither is
# punctuation. The placeholder may already be masked as a tag.
DASH = re.compile(r"(?<=\S) (?:-(?! \d)|--(?! [<" + MASK + r"])) (?=\S)|—|(?<!\d)–|–(?!\d)")
# A sentence starts with a capital, a code span, emphasis, a link or a
# quotation. It also starts with a name written in lowercase: a path such as
# `.lokf/`, an option such as `--root`, or a name with a hyphen, a dot, a
# slash or brackets inside it, such as ktl-docent, knowledge-report.sh or
# main().
SENTENCE_END = re.compile(
    r"(?<=[.!?])[\"')\]*_”]*\s+"
    r"(?=[A-Z`*\[(\"“]|(?:\.|--?)[a-z]|[a-z][\w']*(?:[-_/]\w|\.[a-z]|\(\)))"
)
ABBREVIATION = re.compile(r"\b(?:e\.g|i\.e|vs|cf)\.$", re.I)

# A fence may open a list item. A backtick fence's info string holds no backtick,
# so a line that opens with a long code span is prose.
FENCE = re.compile(r"^\s*(?:>\s?)*(?:(?:[-*+]|\d+[.)])\s+)*(`{3,}(?=[^`]*$)|~{3,})")
HEADING = re.compile(r"^ {0,3}#{1,6}(?:\s|$)")
# What ends `## Open questions`, which may hold lower headings of its own.
SECTION_END = re.compile(r"^ {0,3}#{1,2}(?:\s|$)")
# The line under a Setext heading. One dash alone opens an empty list item.
SETEXT = re.compile(r"^ {0,3}(=+|-{2,})\s*$")
RULE_LINE = re.compile(r"^ {0,3}([-*_=])(?:\s*\1){2,}\s*$")
TABLE_ROW = re.compile(r"^\s*\|")
RULE_CELL = re.compile(r"^\s*:?-+:?\s*$")
# A table's rule, which with a pipe in it makes a table of a row with no leading pipe.
TABLE_RULE = re.compile(r"^\s*\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)*\|?\s*$")
HTML_LINE = re.compile(r"^\s*</?(?!https?:|mailto:)[A-Za-z!]")
# Four spaces or a tab of indent, where a block begins: an indented code block.
INDENT_CODE = re.compile(r"^(?: {4}|\t)")
# A hard line break: two or more spaces, or a backslash, at a line's end.
HARD_BREAK = re.compile(r"(?:  +|\\)$")
LINK_DEF = re.compile(r"^ {0,3}\[([^\]]+)\]:\s*(\S+)")
QUOTE_MARK = re.compile(r"^\s*(?:>\s?)+")
LIST_MARK = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(?:\[[ xX]\]\s+)?")
ORDERED_MARK = re.compile(r"^(\s*(?:>\s*)*)(\d+)([.)]\s)")
ORDERED_VALUE = re.compile(r"^\s*(\d+)[.)]\s+")
ITEM_TEXT = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
TICKED = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\[[xX]\]\s")
# The date and actor that open a person's or a process's question.
QUESTION_MARK = re.compile(r"^(\s*[-*+]\s+)\d{4}-\d{2}-\d{2},\s*\S+?:\s")
CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
COMMENT = re.compile(r"<!--.*?-->")
INLINE_LINK = re.compile(r"\]\(((?:[^()]|\([^()]*\))*)\)")
IMAGE = re.compile(r"!\[[^\]]*\]\(((?:[^()]|\([^()]*\))*)\)")
WIKILINK = re.compile(r"\[\[([^\]]*)\]\]")
REFERENCE = re.compile(r"\]\[([^\]\[]+)\]")
FOOTNOTE = re.compile(r"\[\^[^\]\s]+\]")
AUTOLINK = re.compile(r"<((?:[A-Za-z][A-Za-z0-9+.-]{1,31}:|[^\s<>@]+@)[^>\s]*)>")
# The text inside a tag that shows code, which a rewording keeps as code.
HTML_CODE = re.compile(r"<(code|kbd|pre|samp|tt|var)\b[^>]*>(.*?)</\1\s*>", re.I)
HTML_ATTR = re.compile(r"\b(?:href|src|srcset)=\"([^\"]*)\"")
HTML_TAG = re.compile(r"</?[A-Za-z][^>]*>")
TAG_WORDS = re.compile(r"""\b(alt|title|aria-label)=(?:"([^"]*)"|'([^']*)')""", re.I)
# A bare address, a `www.` one or an email address. It holds brackets that close,
# and stops short of the punctuation that ends a sentence.
BARE_URL = re.compile(
    r"(?:(?<![A-Za-z0-9+.-])[A-Za-z][A-Za-z0-9+.-]*://|\bwww\.)"
    r"(?:[^\s()<>\]\"']|\([^\s()<>]*\))*(?:[^\s()<>\]\"'.,;:!?*_]|\([^\s()<>]*\))"
    r"|(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+"
)
QUOTED = re.compile(r"\"([^\"]+)\"|“([^”]+)”")
LABEL = re.compile(r"(?<![\w*])(\*{1,2})(?=\S)([^*]+?)(?<=\S)\1(?![\w*])")
# The units a number's meaning hangs on, each spelling with the name it counts
# as, so that a rewording may spell one out and may not swap it for another.
UNITS = {
    "%": ("%", "percent"),
    "byte": ("B", "byte", "bytes"),
    "kilobyte": ("KB", "kB", "kilobyte", "kilobytes"),
    "kibibyte": ("KiB", "kibibyte", "kibibytes"),
    "megabyte": ("MB", "megabyte", "megabytes"),
    "mebibyte": ("MiB", "mebibyte", "mebibytes"),
    "gigabyte": ("GB", "gigabyte", "gigabytes"),
    "gibibyte": ("GiB", "gibibyte", "gibibytes"),
    "terabyte": ("TB", "terabyte", "terabytes"),
    "tebibyte": ("TiB", "tebibyte", "tebibytes"),
    "bit": ("bit", "bits"),
    "nanosecond": ("ns", "nanosecond", "nanoseconds"),
    "microsecond": ("us", "\u00b5s", "\u03bcs", "microsecond", "microseconds"),
    "millisecond": ("ms", "millisecond", "milliseconds"),
    "second": ("s", "sec", "secs", "second", "seconds"),
    "minute": ("min", "mins", "minute", "minutes"),
    "hour": ("h", "hr", "hrs", "hour", "hours"),
    "day": ("day", "days"),
    "week": ("week", "weeks"),
    "month": ("month", "months"),
    "year": ("year", "years"),
    "hertz": ("Hz", "hertz"),
    "kilohertz": ("kHz", "kilohertz"),
    "megahertz": ("MHz", "megahertz"),
    "gigahertz": ("GHz", "gigahertz"),
    "pixel": ("px", "pixel", "pixels"),
    "metre": ("m", "metre", "metres", "meter", "meters"),
    "kilometre": ("km", "kilometre", "kilometres", "kilometer", "kilometers"),
    "centimetre": ("cm", "centimetre", "centimetres", "centimeter", "centimeters"),
    "millimetre": ("mm", "millimetre", "millimetres", "millimeter", "millimeters"),
    "gram": ("g", "gram", "grams"),
    "kilogram": ("kg", "kilogram", "kilograms"),
}
UNIT_NAME = {spelling: name for name, spellings in UNITS.items() for spelling in spellings}
UNIT_WORDS = "|".join(sorted((re.escape(word) for word in UNIT_NAME if word != "%"), key=len, reverse=True))
SIGNS = {"\u2265": ">=", "\u2264": "<=", "\u2248": "~", "\u2212": "-"}
# A number with what changes its meaning: a comparison or a sign in front, and a
# power or a unit behind. A sign counts where it touches the number and follows
# no word, so `- 5` is a list item and `pages-5` a name.
NUMBER = re.compile(
    r"(?:(?P<compare>[<>]=?|[=!~]=|[\u2265\u2264\u2248\u00b1~^])\s*)?"
    r"(?P<sign>(?<![\w.)\]])[-+\u2212](?=[\d.]))?"
    r"(?P<value>(?<![\w.])\.\d+|\d+(?:[.,:/-]\d+)*[\u2070\u00b9\u00b2\u00b3\u2074-\u2079\u2080-\u2089]*"
    r"|[\u2070\u00b9\u00b2\u00b3\u2074-\u2079\u2080-\u2089\u00bc-\u00be\u2150-\u215e]+)"
    r"(?:[ \u00a0-]?(?P<unit>%|(?:" + UNIT_WORDS + r")\b))?"
)
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
# What makes one sentence negative, which is more than the count above reads.
NEGATIVE = re.compile(r"\b(?:not|no|nor|neither|never|none|nothing|nobody|nowhere|cannot|without|unless|except)\b|n't\b", re.I)
# Pairs of words that say the opposite of each other. In one sentence that a
# rewording otherwise kept, one word of a pair giving way to the other is how a
# claim turns upside down, and no number, link or code span shows it.
OPPOSITES = (
    ("enable", "disable"), ("enables", "disables"), ("enabled", "disabled"), ("enabling", "disabling"),
    ("at least", "at most"), ("minimum", "maximum"), ("more than", "less than"), ("more than", "fewer than"),
    ("above", "below"), ("over", "under"), ("increase", "decrease"), ("increases", "decreases"),
    ("higher", "lower"), ("highest", "lowest"), ("larger", "smaller"), ("largest", "smallest"),
    ("older", "newer"), ("oldest", "newest"), ("earlier", "later"), ("earliest", "latest"),
    ("before", "after"), ("first", "last"), ("always", "never"),
    ("must", "may"), ("must", "should"), ("must", "can"), ("required", "optional"),
    ("allow", "deny"), ("allows", "denies"), ("allowed", "denied"), ("allow", "block"), ("allows", "blocks"), ("allowed", "blocked"),
    ("accept", "reject"), ("accepts", "rejects"), ("accepted", "rejected"),
    ("accept", "refuse"), ("accepts", "refuses"), ("accepted", "refused"),
    ("include", "exclude"), ("includes", "excludes"), ("included", "excluded"),
    ("add", "remove"), ("adds", "removes"), ("added", "removed"),
    ("pass", "fail"), ("passes", "fails"), ("passed", "failed"), ("success", "failure"), ("succeeds", "fails"),
    ("true", "false"), ("public", "private"), ("internal", "external"), ("inside", "outside"), ("local", "remote"),
    ("signed", "unsigned"), ("tracked", "untracked"), ("start", "stop"), ("starts", "stops"),
)
OPPOSITE_WORD = re.compile(
    r"\b(?:" + "|".join(sorted({re.escape(w).replace(r"\ ", r"\s+") for pair in OPPOSITES for w in pair}, key=len, reverse=True)) + r")\b(?!['\u2019]t)", re.I
)
CONTENT_WORD = re.compile(r"[a-z]{3,}")
# Every word of a sentence as written, a hyphen or an apostrophe inside it kept.
RAW_WORD = re.compile(r"[a-z]+(?:[-'\u2019][a-z]+)*")
# A prefix that turns a word into its opposite: `confirmed` and `unconfirmed`.
NEGATING = ("un", "in", "im", "ir", "il", "non", "non-", "dis", "mis")
# The words that join the items of a series. Two items that change places
# around one of them claim the same.
JOINERS = frozenset(("and", "or", "nor", "plus"))
# The words a claim's strength hangs on: how sure it is, and how much it
# covers. The `all` of `at all` covers nothing, and rule 10 cuts it.
WEIGHT = re.compile(
    r"\b(?:must|never|only|always|unless|except|should|may|might|usually|often|sometimes|rarely"
    r"|(?<!\bat )all|every|most|some|many|few|several|none)\b"
)
# A link with the words a reader sees for it.
LINK_TEXT = re.compile(r"(?<!!)\[([^\]\[]+)\]\(((?:[^()]|\([^()]*\))*)\)")
# How a paragraph ends when its last sentence is whole.
WHOLE_END = re.compile(r"[.!?:;\u2026)\]\"'\u201d\u2019*_`|>" + MASK + r"]$")
# A comment line that holds nothing, which splits a block of comments.
EMPTY_COMMENT = re.compile(r"^\s*#\s*$")
COMMON_WORDS = frozenset(
    "the and for are was were has had have but you your can may its out all any one two who how why this that these those "
    "with from into onto than then them they their there here when where which while what whom whose been will would "
    "could should must shall each every some such more most much many only also very just even both same does did doing done "
    "about again once because through other another not nor neither never none nothing nobody nowhere cannot without unless except least".split()
) | frozenset(part for pair in OPPOSITES for word in pair for part in word.split())

# The KTL Registrar plugin writes each marker on a line of its own. Prose
# that names a marker in a code span is prose, and opens no region.
RELATED_OPEN = "<!-- lokf:related -->"
RELATED_CLOSE = "<!-- /lokf:related -->"
OPEN_QUESTIONS = "## Open questions"

# Letters and marks that print nothing: a joiner, variation selectors, fillers
# and a blank Braille pattern.
BLANKS = frozenset(
    chr(code)
    for code in (0x34F, 0x115F, 0x1160, 0x17B4, 0x17B5, 0x180B, 0x180C, 0x180D, 0x180F, 0x2800, 0x3164, 0xFFA0)
) | frozenset(map(chr, (*range(0xFE00, 0xFE10), *range(0xE0100, 0xE01F0))))

# The actor shapes the LOKF schema allows for `by`. Anything else is a value
# this script cannot read, and it must not guess. A backslash is an escape a
# parser would read as something else.
ACTOR = re.compile(r"^(?:(?:human|process):[^\s\\]+|[^\s/\\]+/[^\s/\\]+)$")
# An event no reader here can follow comes out with this actor, which is none.
UNREADABLE = "(unreadable)"
# What a parser ends a line at and this script does not. It reads \r as a line
# break already, as the toolkit does.
UNSEEN_BREAK = re.compile("[\x85\u2028\u2029]")
# A top-level key no plain `key:` spells: a quoted key, `? key`, `<<:` or a flow
# mapping. Each can hold an event.
ODD_KEY = re.compile(r"""^["'?{\[<!&*:|>]|^(?:verified|generated|revised|refuted)\s+:""")
# A `by` key at the start of a line or of a flow item. The events are counted
# against these, so a `by` the readers cannot place is never taken for no event.
BY_KEY = re.compile(r"""(?:^[\s?:-]*|[\[{,]\s*)["']?by["']?\s*:""")


class Usage(Exception):
    """A request the script cannot act on. It exits 2."""


def normalise(raw: bytes) -> str:
    """Read bytes as CI reads them: no byte order mark, and LF line endings. A byte that is not UTF-8 stays itself, so two different ones still differ."""
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8", errors="surrogateescape").replace("\r\n", "\n").replace("\r", "\n")


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
        # For a script: each line that is not read as prose, with its number.
        self.apart: list[tuple[int, str]] = []

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
        # Where each list item or table row after the first begins.
        self.units: list[int] = []

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


def number_token(found: re.Match) -> str:
    """A number as the text means it: `5 percent` and `5%` are one number, and `10 ms` and `10 s` are two."""
    compare = found.group("compare") or ""
    sign = found.group("sign") or ""
    unit = found.group("unit")
    name = UNIT_NAME.get(unit, unit.lower()) if unit else ""
    behind = name if name == "%" or not name else f" {UNIT_NAME.get(name, name)}"
    return f"{SIGNS.get(compare, compare)}{SIGNS.get(sign, sign)}{found.group('value')}{behind}"


def table_row(content: str) -> list[str]:
    """The cells of a table row: its outer pipes make no cell, and an empty cell inside it is one."""
    cells = re.split(r"(?<!\\)\|", content.strip())
    if cells and not cells[0].strip():
        cells = cells[1:]
    if cells and not cells[-1].strip():
        cells = cells[:-1]
    return cells


def open_comment(line: str) -> int | None:
    """Where a comment opens that this line does not close, a code span aside."""
    hidden = CODE_SPAN.sub(lambda found: MASK * len(found.group()), line)
    start = hidden.rfind("<!--")
    return start if start >= 0 and "-->" not in hidden[start:] else None


# --- who vouched for a concept -------------------------------------------------


def events(fm: list[str]) -> list[tuple[str, str, str, str]]:
    """The event records of a concept's frontmatter, as (key, by, at, revision).

    The keys are `generated`, `verified`, `revised` and `refuted`. This is a
    port of human_events() in knowledge-provenance.sh, and it keeps to that
    reading on purpose: the script must see an event exactly where the gates
    see one. It reads a block list at any indent, a flow item, a flow sequence
    across lines and a bare mapping. The gates keep only human actors, and this
    keeps every actor. A shape it cannot follow comes out as the actor
    UNREADABLE, never as no event.
    """
    out: list[tuple[str, str, str, str]] = []
    key: str | None = None
    cur: dict[str, str] | None = None
    held = ""  # a flow form still open, from its bracket on
    fields = ("by", "at", "revision")

    def emit() -> None:
        nonlocal cur
        if cur is not None:
            by = cur.get("by", "")
            if "odd" in cur or not ACTOR.match(by):
                by = UNREADABLE
            out.append((cur["key"], by, cur.get("at", ""), cur.get("revision", "")))
        cur = None

    def unread() -> None:
        out.append(("verified", UNREADABLE, "", ""))

    def value(text: str) -> str:
        text = re.sub(r"^[^:]*:\s*", "", text, count=1)
        return text.replace('"', "").replace("'", "").rstrip()

    def pair(text: str) -> None:
        name = text.split(":", 1)[0].lstrip()
        if cur is None:
            return
        if name in fields:
            cur[name] = value(text)
        elif not (name == "reason" and cur["key"] == "refuted"):
            cur["odd"] = ""

    def flow(text: str) -> None:
        nonlocal cur
        emit()
        cur = {"key": key or ""}
        for part in text.replace("{", "").replace("}", "").split(","):
            if part.strip():
                pair(part)
        emit()

    def flush() -> None:
        nonlocal held, key
        text, held = held, ""
        if re.search(r"(?:^|\s)#", text):
            unread()
        if text.startswith("["):
            for item in re.split(r"\}\s*,", text[1:].split("]", 1)[0]):
                if item.strip():
                    flow(item)
        else:
            inner = text[1:].split("}", 1)[0]
            if inner.strip():
                flow(inner)
        key = None

    if any(UNSEEN_BREAK.search(line) for line in fm):
        unread()
    first = next((line for line in fm if line.strip() and not line.lstrip().startswith("#")), "")
    if first[:1].isspace():
        unread()
    for line in fm:
        if held:
            held += " " + line
            if ("]" if held.startswith("[") else "}") in line:
                flush()
            continue
        if ODD_KEY.match(line):
            emit()
            key = None
            unread()
            continue
        opened = re.match(r"^(verified|generated|revised|refuted):\s*(.*?)\s*$", line)
        if opened:
            emit()
            key, rest = opened.group(1), opened.group(2)
            if rest[:1] in ("{", "["):
                held = rest
                if ("]" if rest.startswith("[") else "}") in rest:
                    flush()
            elif rest and not rest.startswith("#") and rest not in ("null", "~"):
                unread()
            continue
        if key is None:
            continue
        if re.match(r"^[^\s-]", line):
            emit()
            key = None
        elif re.match(r"^\s*-\s*(?:#.*)?$", line):
            emit()
            cur = {"key": key}
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
        elif re.match(r"^\s+[^\s#]", line):
            if cur is None:
                cur = {"key": key}
            cur["odd"] = ""
    if held:
        flush()
    emit()
    return out


def by_keys(fm: list[str]) -> int:
    """How many events the frontmatter spells out, whether or not events() saw them.

    The `by` of an `exclusions` entry names who left a material out. It says
    nothing about who wrote or confirmed the concept, so it is not counted.
    """
    count = 0
    excluded = False
    for line in fm:
        if re.match(r"^[^\s#-]", line):
            excluded = re.match(r"^exclusions\s*:", line) is not None
        if not excluded:
            count += len(BY_KEY.findall(line))
    return count


def top_value(fm: list[str], key: str) -> str | None:
    for line in fm:
        found = re.match(rf"^[\"']?{key}[\"']?\s*:\s*(.*)$", line)
        if found:
            return found.group(1).split(" #")[0].strip().strip("\"'")
    return None


def standing(doc: Doc, expect_concept: bool = False) -> tuple[str, str]:
    """Where a file stands, as a rule name and the words for it.

    Only `rewrite` allows a rewording with no condition, and `unrecorded`
    allows one a person named. The order is the order of the table in
    SKILL.md. The script fails closed: an event it cannot read is never
    taken for a missing one.
    """
    unreadable = ("unreadable", "frontmatter the script cannot read")
    if doc.fm is None:
        return unreadable if doc.unclosed or expect_concept else ("plain", "not a concept")
    found = events(doc.fm)
    for key, by, _, _ in found:
        if key == "generated" and by.startswith("human:"):
            return "person", f"written by a person ({by})"
    for key, by, _, _ in found:
        if key == "revised" and by.startswith("human:"):
            return "edited", f"edited by a person ({by})"
    for key, by, _, _ in found:
        if key == "verified" and by.startswith("human:"):
            return "confirmed", f"confirmed by a person ({by})"
    if top_value(doc.fm, "status") == "deprecated":
        return "retired", "retired"
    for key, by, _, _ in found:
        if key == "refuted":
            return "refuted", f"refuted ({by})"
    if by_keys(doc.fm) != len(found) or any(by == UNREADABLE for _, by, _, _ in found):
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


def is_script(path: Path) -> bool:
    return path.suffix.lower() in SCRIPT_SUFFIXES or path.name.lower() == "justfile"


def script_doc(text: str, python: bool = False) -> Doc:
    """The prose of a script, laid out on the lines it came from.

    Each whole-line `#` comment keeps its text with the mark removed, and in
    Python each docstring keeps its lines, less the indent of its opening
    quotes. Every other line is blank, so a block of comments reads as a
    paragraph, an empty comment line splits one, and a line of code ends one,
    as a blank line does in Markdown. Left out: the shebang, a directive such
    as `# shellcheck`, a `# /// script` block, and the body of a heredoc,
    which is data. A triple-quoted string is a docstring when it opens the
    module or follows a line that ends with a colon, so a quoted block
    assigned to a name is data too. Each block of comments and each docstring
    is then read for its layout, as `laid_out` says.

    The result also holds, as `apart`, what a rewording of the comments must
    leave as it was: each line that is not read as prose, and the name that
    opens each row of a table. That is code, a directive, a heredoc and a
    command in a comment. An empty comment line is layout, and is left out.
    """
    out: list[str] = []
    blocks: list[list[int]] = []
    block: list[int] | None = None
    terminator: str | None = None
    in_block = False
    in_doc: tuple[str, int] | None = None
    seen_code = False
    previous = ""
    for line in text.split("\n"):
        stripped = line.strip()
        if terminator is not None:
            out.append("")
            if stripped == terminator:
                terminator = None
            continue
        if in_doc:
            quotes, indent = in_doc
            end = line.find(quotes)
            content = line if end < 0 else line[:end]
            if end >= 0:
                in_doc = None
            out.append(content[indent:] if not content[:indent].strip() else content.lstrip())
            blocks[-1].append(len(out) - 1)
            continue
        found = COMMENT_LINE.match(line)
        if found:
            if in_block:
                in_block = not SCRIPT_BLOCK_END.match(stripped)
                out.append("")
                block = None
            elif SCRIPT_BLOCK.match(stripped) or DIRECTIVE.match(stripped):
                in_block = bool(SCRIPT_BLOCK.match(stripped))
                out.append("")
                block = None
            else:
                body = found.group(1)
                out.append(body[1:] if body.startswith(" ") else body)
                if block is None:
                    block = []
                    blocks.append(block)
                block.append(len(out) - 1)
            continue
        block = None
        opening = DOCSTRING.match(line) if python else None
        if opening and (not seen_code or previous.rstrip().endswith(":")):
            indent, quotes, rest = len(opening.group(1)), opening.group(2), opening.group(3)
            end = rest.find(quotes)
            out.append((rest if end < 0 else rest[:end]).strip())
            blocks.append([len(out) - 1])
            if end < 0:
                in_doc = (quotes, indent)
            seen_code = True
            previous = ""
            continue
        # In Python `<<` is a shift, as it is in a shell's `((`.
        heredoc = HEREDOC.search(line) if not python else None
        if heredoc and "((" not in line[: heredoc.start()]:
            terminator = heredoc.group(2)
        out.append("")
        if stripped:
            seen_code = True
            previous = line
    names: list[tuple[int, str]] = []
    moved: set[int] = set()
    for numbers in blocks:
        laid_out(out, numbers, names, moved)
    doc = Doc("\n".join(out))
    for n, (raw, read_as) in enumerate(zip(text.split("\n"), out)):
        if raw.strip() and not read_as.strip() and n not in moved and not EMPTY_COMMENT.match(raw):
            doc.apart.append((n + 1, raw.rstrip()))
    doc.apart.extend((n + 1, name) for n, name in names)
    doc.apart.sort()
    return doc


def laid_out(lines: list[str], numbers: list[int], names: list[tuple[int, str]], moved: set[int]) -> None:
    """Read one block of comments, or one docstring, for its layout, in place.

    NAMES gains the name that opens each row, with its line, and MOVED the
    lines whose prose went into a row's cell. The caller needs both to tell a
    line that is not prose from one that was read elsewhere.

    Indent is measured from the block's own text. A line indented further is
    prose when it is a list item, continues one (an empty line between does
    not end the item, as in Markdown), or continues the line above it. It is
    a command, and is blanked, when it follows a `Usage` line, a line that
    ends with a colon, an empty line or the top of the block, and does not
    start as a sentence does.

    When its words stand in columns, the line starts a row, which becomes one
    table cell on the row's first line: the first column, a name, is dropped,
    and each line indented under the row is moved into the cell. A line level
    with a row starts the next one, even when its name is too wide to leave a
    gap. So a table of options or a command line is not read as one long
    sentence, the prose after a table is not run into its last row, and each
    row's own text is still read whole.
    """
    texts = [lines[n] for n in numbers if lines[n].strip()]
    if not texts:
        return
    base = min(len(text) - len(text.lstrip()) for text in texts)
    state, edge, opens = "", 0, True
    row_at, row = 0, ""

    def cell(text: str) -> str:
        return "| " + text.replace("|", "\\|") + " |"

    for n in numbers:
        text = lines[n]
        if not text.strip():
            state, opens = ("item" if state == "item" else ""), True
            continue
        indent = len(text) - len(text.lstrip())
        inner = indent - base >= 2
        if not inner and USAGE.match(text):
            lines[n], state = "", "command"
        elif LIST_MARK.match(text) or LETTERED_MARK.match(text):
            state, edge = "item", indent
        elif inner and state == "item" and indent > edge:
            pass
        elif inner and COLUMN_GAP.search(text.strip()):
            rest = " ".join(re.split(r"\s{2,}", text.strip())[1:])
            if state == "row" and indent > edge:
                row, lines[n] = f"{row} {rest}", ""
                moved.add(n)
            else:
                row_at, row, state, edge = n, rest, "row", indent
                names.append((n, re.split(r"\s{2,}", text.strip())[0]))
            lines[row_at] = cell(row)
        elif inner and state == "row" and indent > edge:
            row, lines[n] = f"{row} {text.strip()}", ""
            moved.add(n)
            lines[row_at] = cell(row)
        elif inner and state == "row" and indent == edge:
            row_at, row = n, (text.split(None, 1) + [""])[1]
            names.append((n, text.split(None, 1)[0]))
            lines[n] = cell(row)
        elif inner and (opens or state == "command") and not SENTENCE_START.match(text):
            lines[n], state = "", "command"
        else:
            state = "prose"
        opens = text.rstrip().endswith(":")


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
        if "-->" in line:
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

    A table cell is no paragraph, and a list item is held to the same limit
    on words. The limit on sentences is a paragraph's alone.
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
                # Case folding lets a dotless i match an i, and it lists no word.
                advice = WORDS.get(" ".join(word.group().lower().split()))
                if advice:
                    findings.append((block.line_at(start + word.start()), "words", f'"{word.group()}": {advice}'))
            for word in BAND_WORD.finditer(sentence) if band_words else ():
                found = word.group().lower()
                advice = BAND_WORDS.get(found) or BAND_WORDS.get(found.rstrip(".")) or BAND_WORDS.get(found.rstrip(".") + ".")
                if advice:
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
    """A character no reader sees: a format character, a control character other than a tab, or one of the blanks Unicode classes as a letter or a mark."""
    kind = unicodedata.category(char)
    return kind == "Cf" or (kind == "Cc" and char not in "\t\n") or char in BLANKS


def unseen_in(line: str) -> list[str]:
    """Each character no reader sees in a line, an HTML entity read as the character it writes."""
    return [char for char in html.unescape(line) if unseen_char(char)]


def described(char: str) -> str:
    return f"U+{ord(char):04X} {unicodedata.name(char, '')}".rstrip()


def unseen(doc: Doc) -> list[tuple[int, str, str]]:
    """Each line that holds a character no reader sees, frontmatter and code included."""
    findings: list[tuple[int, str, str]] = []
    for number, line in enumerate(doc.lines, start=1):
        chars = sorted(set(unseen_in(line)))
        if chars:
            names = ", ".join(described(char) for char in chars)
            findings.append((number, "unseen", f"{names}: a character no reader sees; delete it, or write it as an escape in code"))
    return findings


# --- what a rewording must leave alone ----------------------------------------


# One sentence, list item or table row, as `turned` compares it. `words` is
# what it is matched by. `raw` is every word as written, `tokens` its code
# spans, link targets and numbers, and `weight` the words its strength hangs on.
Said = namedtuple("Said", "line text words opposites negatives raw tokens number_words weight")
ROOT_ENDINGS = (("ies", "y"), ("ied", "y"), ("ing", ""), ("ed", ""), ("es", ""), ("s", ""))


def root(word: str) -> str:
    """A word less its plural or verb ending and a last `e`, cut to six letters.

    It makes `file` and `files` one, and `sign`, `signs`, `signed` and
    `signing`. It is a rough key for matching two texts, and no reader sees it.
    """
    if not word.endswith("ss"):
        for ending, put in ROOT_ENDINGS:
            if word.endswith(ending) and len(word) - len(ending) >= 2:
                word = word[: -len(ending)] + put
                break
    return (word[:-1] if len(word) >= 3 and word.endswith("e") else word)[:6]


def content_words(text: str) -> list[str]:
    """The words of a sentence that carry its subject, in order, each as its root."""
    return [root(word) for word in CONTENT_WORD.findall(text.lower()) if word not in COMMON_WORDS]


def transposed(x: list[str], y: list[str]):
    """Two runs of up to three words that changed places around words that stayed, with those words, or None.

    `the librarian hands the change to the curator` and `the curator hands
    the change to the librarian` give `librarian`, `curator` and the five
    words between them.
    """
    if len(x) != len(y) or x == y:
        return None
    i, j = 0, len(x)
    while x[i] == y[i]:
        i += 1
    while x[j - 1] == y[j - 1]:
        j -= 1
    xs, ys = x[i:j], y[i:j]
    for la in range(1, 4):
        for lb in range(1, 4):
            between = len(xs) - la - lb
            if between >= 1 and xs[:la] == ys[len(ys) - la :] and xs[len(xs) - lb :] == ys[:lb] and xs[la : la + between] == ys[lb : lb + between]:
                return " ".join(xs[:la]), " ".join(xs[len(xs) - lb :]), xs[la : la + between]
    return None


def replaced(old: Said, new: Said):
    """The one run of words that gave way to another while every other word stayed, as two lists, or None."""
    changes = [op for op in difflib.SequenceMatcher(a=old.raw, b=new.raw, autojunk=False).get_opcodes() if op[0] != "equal"]
    if len(changes) != 1 or changes[0][0] != "replace":
        return None
    _, a1, a2, b1, b2 = changes[0]
    return (old.raw[a1:a2], new.raw[b1:b2]) if a2 - a1 <= 2 and b2 - b1 <= 3 else None


def turned(a: Kept, b: Kept):
    """What a rewording did to each sentence that changed: findings, notes, and the words of strength the notes placed.

    Each changed sentence is compared with the sentence of the new text that
    shares the largest part of its words. A list item and a table row count as
    a sentence each. Three in five shared means the rewording kept it.

    In a kept sentence these are findings. A word gave way to its opposite, or
    to itself behind a negating prefix, as `confirmed` to `unconfirmed`. One
    number word gave way to another. Two runs of words changed places around
    words that stayed, as an actor and what it acts on do. A number, a link or
    a code span changed places with one in another kept sentence. When the
    shared words also moved, an opposite is a note, since `lint after build`
    and `build before lint` agree. A negative that came or went is a finding
    only when every other word stayed in its place, since `does not change`
    and `changes nothing` agree.

    The rest are notes, each with its line: the same words in a new order, a
    word of strength that came or went, and one word that gave way to another.
    A sentence with too few of its words anywhere near it may have gone. The
    third value counts each word of strength the notes placed, so that the
    caller reports only the rest for the page.
    """
    findings, notes = [], []
    placed: Counter = Counter()
    same = {said.text for said in b.said}

    def anchors(said: Said) -> set:
        """What a sentence is matched by: its words, or what it names when it has none, as a table row may."""
        return set(said.words) or set(said.tokens)

    new = [(said, anchors(said)) for said in b.said if anchors(said)]
    sizes = [len(other) for _, other in new]
    named = [set(said.tokens) for said, _ in new]
    kept: list[tuple[Said, Said]] = []
    swaps: Counter = Counter()
    first: dict[tuple[str, str], int] = {}
    for old in a.said:
        words = anchors(old)
        if old.text in same or not words or not new:
            continue
        shared = [len(words & other) for _, other in new]
        scores = [(count / (len(words) + size - count), count) for count, size in zip(shared, sizes)]
        top = max(scores)
        # Of the sentences that share as much, take the one that names the
        # same code, links and numbers, and then the nearest.
        ties = [n for n, score in enumerate(scores) if score == top]
        mine = set(old.tokens)
        at = ties[0] if len(ties) == 1 else max(ties, key=lambda n: (len(mine & named[n]), -abs(new[n][0].line - old.line)))
        best, others = new[at]
        if shared[at] < 0.6 * (len(words) + sizes[at] - shared[at]):
            if len(words) >= 3 and sum(heapq.nlargest(2, shared)) < 0.4 * len(words):
                notes.append((old.line, "sentence-gone", f'few words of this sentence came through (line {old.line} of the earlier text): "{old.text[:90]}"'))
            continue
        kept.append((old, best))
        tail = f'(line {old.line} of the earlier text): "{best.text[:90]}"'
        common = words & others
        kept_order = [w for w in old.words if w in common] == [w for w in best.words if w in common]
        where = findings if kept_order else notes
        # The words a check below has already answered for.
        answered: set[str] = set()

        for one, other in OPPOSITES:
            for gone, came in ((one, other), (other, one)):
                if best.opposites[gone] < old.opposites[gone] and best.opposites[came] > old.opposites[came]:
                    where.append((best.line, "opposite", f'"{gone}" became "{came}" in a sentence that otherwise stayed {tail}'))
                    answered.update((*gone.split(), *came.split()))
        went, arrived = set(old.raw) - set(best.raw), set(best.raw) - set(old.raw)
        for gone in sorted(went):
            for came in sorted(arrived):
                if min(len(gone), len(came)) >= 4 and any(came == prefix + gone or gone == prefix + came for prefix in NEGATING):
                    where.append((best.line, "opposite", f'"{gone}" became "{came}" in a sentence that otherwise stayed {tail}'))
                    answered.update((gone, came))

        counts_gone, counts_came = old.number_words - best.number_words, best.number_words - old.number_words
        if counts_gone and counts_came:
            gone, came = ", ".join(sorted(counts_gone)), ", ".join(sorted(counts_came))
            findings.append((best.line, "number-word", f'"{gone}" became "{came}" in a sentence that otherwise stayed {tail}'))
            answered.update((*counts_gone, *counts_came))

        literal = old.words == best.words
        if (old.negatives > 0) != (best.negatives > 0):
            how = "lost its" if old.negatives else "gained a"
            (findings if literal else notes).append((best.line, "negative", f"a sentence that otherwise stayed {how} negative {tail}"))
        elif literal and old.negatives != best.negatives:
            notes.append((best.line, "negative", f"a sentence that otherwise stayed has {counted_as(best.negatives, 'negative', 'negatives')}, and had {old.negatives} {tail}"))

        if old.raw != best.raw and Counter(old.raw) == Counter(best.raw):
            moved = transposed(old.raw, best.raw)
            # The items of a series may change places and claim the same.
            if moved and not JOINERS.intersection(moved[2]):
                findings.append((best.line, "order", f'"{moved[0]}" and "{moved[1]}" changed places in a sentence that otherwise stayed {tail}'))
            else:
                notes.append((best.line, "order", f"the same words stand in a new order {tail}"))

        for word in sorted(set(old.weight) | set(best.weight)):
            change = best.weight[word] - old.weight[word]
            if change:
                placed[word] += change
                if word not in answered:
                    notes.append((best.line, "strength", f'"{word}" {"came into" if change > 0 else "left"} a sentence that otherwise stayed {tail}'))

        change = replaced(old, best)
        if change:
            gone, came = change
            # No note for a word the style rules list, a contraction spelt
            # out, one word in two forms, or a word answered for above.
            listed = any(word in WORDS for word in (*gone, " ".join(gone)))
            spelt = any("'" in word or "’" in word for word in gone) or "".join(gone).replace("-", "") == "".join(came).replace("-", "")
            one_word = len(gone) == 1 and len(came) == 1 and root(gone[0]) == root(came[0])
            weighed = any(WEIGHT.fullmatch(word) for word in (*gone, *came))
            if not (listed or spelt or one_word or weighed or answered.intersection((*gone, *came))):
                pair = (" ".join(gone), " ".join(came))
                swaps[pair] += 1
                first.setdefault(pair, best.line)

    for (gone, came), count in swaps.items():
        notes.append((first[(gone, came)], "word", f'"{gone}" became "{came}" {times(count)} in a sentence that otherwise stayed; check that both name the same thing'))

    # A number, a link or a code span that changed places with one in another
    # kept sentence. Each sentence is looked up by what it gained, so the
    # search does not compare every pair.
    moves = [(old, best, old.tokens - best.tokens, best.tokens - old.tokens) for old, best in kept]
    moves = [move for move in moves if move[2] and move[3]]
    gained_by: dict[str, list[int]] = {}
    for at, move in enumerate(moves):
        for token in move[3]:
            gained_by.setdefault(token, []).append(at)
    reported: set[int] = set()
    for at, (old, best, lost, gained) in enumerate(moves):
        for other in sorted({n for token in lost for n in gained_by.get(token, ()) if n != at}):
            other_old, other_best, other_lost, other_gained = moves[other]
            there, back = lost & other_gained, gained & other_lost
            if there and back and at not in reported:
                reported.update((at, other))
                findings.append((best.line, "swap", f"{', '.join(sorted(there))} and {', '.join(sorted(back))} changed places between this sentence and the one on line {other_best.line} (lines {old.line} and {other_old.line} of the earlier text)"))
    return findings, notes, placed


class Kept:
    """What one version of a file holds besides its wording.

    A rewording keeps `## Open questions` and the lokf:related region whole, so
    they are compared whole. A retelling may hold neither, and may add nothing
    in them, so `whole=True` reads them as it reads the rest of the page.
    """

    def __init__(self, doc: Doc, whole: bool = False):
        self.whole = whole
        self.fences: list[tuple[int, str]] = []
        self.indented: list[tuple[str, int]] = []
        self.related: list[str] = []
        self.related_at = 1
        self.questions: list[str] = []
        self.questions_at = 1
        self.headings: list[tuple[int, str]] = []
        self.said: list[Said] = []
        self.list_items = 0
        self.ticked = 0
        self.table_rows = 0
        self.table_cells = 0
        self.breaks = 0
        self.codes: list[tuple[str, int]] = []
        self.html: list[tuple[str, int]] = []
        self.links: list[tuple[str, int]] = []
        self.wikilinks: list[tuple[str, int]] = []
        self.images: list[tuple[str, int]] = []
        self.labels: list[tuple[str, int]] = []
        self.definitions: dict[str, str] = {}
        self.numbers: list[tuple[str, int]] = []
        self.quotes: list[tuple[str, int]] = []
        self.rfc: list[tuple[str, int]] = []
        self.number_words: list[tuple[str, int]] = []
        self.date_words: list[tuple[str, int]] = []
        self.strength: Counter = Counter()
        # Each number with the word after it, as `3 workers`: what it counts.
        self.claims: Counter = Counter()
        # Each link's target with the words a reader sees for it.
        self.link_texts: list[tuple[str, str]] = []
        # Each table row as (line, first cell, the code, links and numbers of the other cells).
        self.rows: list[tuple[int, str, Counter]] = []
        # The first line of each item of a numbered list, in order.
        self.steps: list[str] = []
        # The words of the page, each under its root, as first written.
        self.page_words: dict[str, str] = {}
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
        code: list[str] = []
        code_at = 0
        comment: list[str] = []
        comment_at = 0
        in_list = False
        lists: list[tuple[int, int, int]] = []

        def flush() -> None:
            nonlocal block, block_is_list, block_is_table, prev_in_block
            if block:
                self._tokens(block)
            block = None
            block_is_list = block_is_table = False
            prev_in_block = ""

        def flush_code() -> None:
            nonlocal code
            if code:
                self.indented.append((textwrap.dedent("\n".join(code)), code_at))
            code = []

        def count_row(content: str, number: int) -> None:
            row = table_row(content)
            if not all(RULE_CELL.match(cell) for cell in row):
                self.table_rows += 1
                self.table_cells += len(row)
                rest = " | ".join(row[1:])
                held = Counter(f"`{found.group(2).strip()}`" for found in CODE_SPAN.finditer(rest))
                rest = CODE_SPAN.sub(lambda found: MASK * len(found.group()), rest)
                held.update(found.group(1).strip() for found in INLINE_LINK.finditer(rest))
                rest = INLINE_LINK.sub(lambda found: MASK * len(found.group()), rest)
                held.update(number_token(found) for found in NUMBER.finditer(rest))
                self.rows.append((number, " ".join(row[0].split()) if row else "", held))

        body = list(doc.numbered_body())
        for index, (number, line) in enumerate(body):
            if fence:
                fenced.append(line)
                if closes(fence, line):
                    self.fences.append((fence_at, textwrap.dedent("\n".join(fenced))))
                    fence = None
                continue
            opening = FENCE.match(line)
            if opening:
                flush()
                flush_code()
                fence, fenced, fence_at = opening.group(1), [line], number
                continue
            if self.whole:
                # A retelling's own markers and question stamps are no facts.
                if line.strip() in (RELATED_OPEN, RELATED_CLOSE):
                    flush()
                    continue
                if line.rstrip() == OPEN_QUESTIONS:
                    questions = True
                elif SECTION_END.match(line):
                    questions = False
                if questions:
                    line = QUESTION_MARK.sub(lambda found: found.group(1), line)
            else:
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
                    underlined = index + 1 < len(body) and line.strip() and SETEXT.match(body[index + 1][1])
                    if not SECTION_END.match(line) and not underlined:
                        self.questions.append(line.rstrip())
                        continue
                    questions = False
            # A comment holds no fact a reader sees, so what it holds is kept
            # whole and a number moved into one is gone from the text.
            if comment:
                comment.append(line)
                if "-->" in line:
                    self.html.append((" ".join(" ".join(comment).split()), comment_at))
                    comment = []
                continue
            start = open_comment(line)
            if start is not None:
                comment, comment_at = [line[start:]], number
                line = line[:start]
            content = QUOTE_MARK.sub("", line, count=1)
            # An indented code block, read as prose_blocks reads one.
            if code:
                if line.strip() and INDENT_CODE.match(content):
                    code.append(line)
                    continue
                flush_code()
            if block is None and not in_list and line.strip() and INDENT_CODE.match(content):
                code, code_at = [line], number
                continue
            if not line.strip():
                flush()
                continue
            definition = LINK_DEF.match(line)
            if definition and not definition.group(1).startswith("^"):
                label, target = definition.group(1), definition.group(2)
                self.links.append((target, number))
                self.labels.append((f"[{label}]: {target}", number))
                self.definitions[label.lower()] = target
            underline = SETEXT.match(content)
            if underline and block is not None and not block_is_list and not block_is_table:
                level = "#" if underline.group(1).startswith("=") else "##"
                self.headings.append((block.numbers[0], f"{level} {' '.join(block.text.split())}"))
                flush()
                continue
            if HEADING.match(content):
                flush()
                lists.clear()
                in_list = False
                self.headings.append((number, " ".join(content.split())))
            # A bullet opens a list wherever it stands. A number opens one where
            # a block begins, where it is 1, or where it lines up with an open
            # numbered list, as the next item of it. On any other line it is text,
            # and a fact: `2024.` on a wrapped line is a year. Only a number in
            # its list's order is a marker and not a fact.
            at_start = block is None
            marker = LIST_MARK.match(content)
            ordered = ORDERED_VALUE.match(content) if marker else None
            value = int(ordered.group(1)) if ordered else None
            indent = len(content) - len(content.lstrip())
            # The open lists, outermost first, as (marker's indent, text's indent,
            # last number). The deepest whose marker this line lines up with is its own.
            level = next((i for i in range(len(lists) - 1, -1, -1) if lists[i][0] <= indent < lists[i][1]), None)
            previous = lists[level][2] if level is not None else 0
            sibling = in_list and previous > 0
            in_order = value == 1 or (value == previous + 1 and (at_start or block_is_list or sibling))
            is_item = bool(marker) and (ordered is None or at_start or in_order or sibling)
            if is_item:
                self.list_items += 1
                in_list = True
                while lists and (level is not None and len(lists) > level or level is None and lists[-1][1] > indent):
                    lists.pop()
                lists.append((indent, ITEM_TEXT.match(content).end(), value or 0))
                if TICKED.match(content):
                    self.ticked += 1
            elif at_start:
                # A new block left of an item's text closes that item's list.
                while lists and indent < lists[-1][1]:
                    lists.pop()
                in_list = bool(lists)
            is_row = False
            if (at_start or block_is_table) and (TABLE_ROW.match(content) or (block_is_table and "|" in content)):
                count_row(content, number)
                is_row = True
            elif block is not None and len(block.numbers) == 1 and "|" in content and TABLE_RULE.match(content):
                # The row above this rule is a table's header, with no leading pipe.
                header = QUOTE_MARK.sub("", prev_in_block, count=1)
                if "|" in header:
                    count_row(header, number - 1)
                    block_is_table = is_row = True
            if is_item and ordered:
                self.steps.append(" ".join(ITEM_TEXT.sub("", content, count=1).split()))
            if is_item and in_order:
                line = ORDERED_MARK.sub(lambda found: found.group(1) + " " * len(found.group(2)) + found.group(3), line)
            # A hard line break joins two lines of one block, so it is the kind
            # of layout a rewording leaves alone; count one where the line before
            # this one in the block ended with it. Before a new item it breaks nothing.
            if block is None:
                block = Block()
                block_is_list, block_is_table = is_item, is_row
            else:
                if HARD_BREAK.search(prev_in_block) and not is_item:
                    self.breaks += 1
                block_is_list = block_is_list or is_item
            prev_in_block = line
            block.add(number, QUOTE_MARK.sub("", line, count=1).strip())
            if (is_item or is_row) and len(block.numbers) > 1:
                block.units.append(block.starts[-1])
            if HEADING.match(content):
                flush()
        if fence:
            self.fences.append((fence_at, textwrap.dedent("\n".join(fenced))))
        if comment:
            self.html.append((" ".join(" ".join(comment).split()), comment_at))
        flush_code()
        flush()
        while self.questions and not self.questions[-1]:
            self.questions.pop()

    def _tokens(self, block: Block) -> None:
        text = block.text
        hidden = text
        # Where each code span, link target and number stands, for the sentence that holds it.
        marks: list[tuple[int, str]] = []
        for found in LINK_TEXT.finditer(CODE_SPAN.sub(lambda span: MASK * len(span.group()), text)):
            target, shown = text[found.start(2) : found.end(2)], text[found.start(1) : found.end(1)]
            self.link_texts.append((" ".join(target.split()), " ".join(shown.split())))

        def take(pattern: re.Pattern, into: list[tuple[str, int]], group: int = 1, whole: bool = False, exact: bool = False, mark: str = "") -> None:
            """Record each match, read from the unmasked text, then mask it."""
            nonlocal hidden
            for found in pattern.finditer(hidden):
                token = text[found.start(group) : found.end(group)]
                into.append((token if exact else " ".join(token.split()), block.line_at(found.start())))
                if mark:
                    marks.append((found.start(), f"{mark} {' '.join(token.split())}"))
            for found in list(pattern.finditer(hidden)):
                a, b = (found.start(), found.end()) if whole else (found.start(group), found.end(group))
                hidden = hidden[:a] + MASK * (b - a) + hidden[b:]

        # Inside a code span every space counts. Block.add joins wrapped lines with one.
        take(CODE_SPAN, self.codes, group=2, exact=True, mark="the code span")
        if "-->" in hidden:
            take(COMMENT, self.html, group=0, whole=True)
        take(HTML_CODE, self.codes, group=2, exact=True)
        # A wikilink's target is a link. Its alias is what a reader reads.
        for found in list(WIKILINK.finditer(hidden)):
            target = text[found.start(1) : found.end(1)].split("|")[0]
            self.links.append((target.strip(), block.line_at(found.start())))
            self.wikilinks.append((target.strip(), block.line_at(found.start())))
            at = found.start(1)
            hidden = hidden[:at] + MASK * len(target) + hidden[at + len(target) :]
        for found in IMAGE.finditer(hidden):
            self.images.append((" ".join(text[found.start(1) : found.end(1)].split()), block.line_at(found.start())))
        take(INLINE_LINK, self.links, mark="the link target")
        take(REFERENCE, self.labels)
        take(FOOTNOTE, self.labels, group=0)
        take(AUTOLINK, self.links)
        take(HTML_ATTR, self.links)
        # An inline HTML tag carries meaning a rewording must not drop: a <br>, a
        # <sub>, a colspan. Record it whole, then mask it so it counts as neither
        # a word nor anything else.
        # What a reader hears of a tag is wording, and a rewording may change it,
        # all but the numbers in it.
        for found in HTML_TAG.finditer(hidden):
            tag = text[found.start() : found.end()]
            self.html.append((" ".join(TAG_WORDS.sub(r"\1", tag).split()), block.line_at(found.start())))
            for said in TAG_WORDS.finditer(tag):
                for number in NUMBER.finditer(said.group(2) or said.group(3) or ""):
                    self.numbers.append((number_token(number), block.line_at(found.start())))
        take(HTML_TAG, [], group=0)
        take(BARE_URL, self.links, group=0)
        for found in QUOTED.finditer(hidden):
            group = 1 if found.group(1) is not None else 2
            quoted = " ".join(text[found.start(group) : found.end(group)].split())
            self.quotes.append((quoted, block.line_at(found.start())))
        for found in NUMBER.finditer(hidden):
            token = number_token(found)
            self.numbers.append((token, block.line_at(found.start())))
            marks.append((found.start(), f"the number {token}"))
            after = RAW_WORD.search(hidden.lower(), found.end())
            self.claims[(token, after.group() if after and after.start() - found.end() <= 2 else "")] += 1
        for found in RFC_WORD.finditer(hidden):
            self.rfc.append((found.group(), block.line_at(found.start())))
        for found in NUMBER_WORD.finditer(hidden):
            self.number_words.append((found.group().lower(), block.line_at(found.start())))
        for found in DATE_WORD.finditer(hidden):
            self.date_words.append((found.group().rstrip("s"), block.line_at(found.start())))
        lowered = hidden.lower()
        for word in STRENGTH:
            self.strength[word] += len(re.findall(rf"\b{word}\b", lowered))
        self.strength["a negation"] += len(NEGATION.findall(hidden))
        self.strength["should"] += len(re.findall(r"\bshould\b", lowered))
        self.words += len(hidden.split())
        for word in RAW_WORD.findall(hidden.lower()):
            if len(word) >= 4 and word not in COMMON_WORDS and word not in WORDS:
                self.page_words.setdefault(root(word.replace("-", "")), word)
        # A list item and a table row are each read apart, so that a change in
        # one cannot hide behind the others.
        edges = [0, *block.units, len(hidden)]
        for unit, unit_end in zip(edges, edges[1:]):
            for start, end in sentences(hidden[unit:unit_end]):
                start, end = start + unit, end + unit
                part = hidden[start:end]
                lowered = part.lower()
                self.said.append(
                    Said(
                        block.line_at(start),
                        " ".join(text[start:end].split()),
                        content_words(part),
                        Counter(" ".join(found.group().lower().split()) for found in OPPOSITE_WORD.finditer(part)),
                        len(NEGATIVE.findall(part)),
                        RAW_WORD.findall(lowered),
                        Counter(token for at, token in marks if start <= at < end),
                        Counter(NUMBER_WORD.findall(lowered)),
                        Counter(WEIGHT.findall(lowered)),
                    )
                )


def times(count: int) -> str:
    return "once" if count == 1 else f"{count} times"


def counted_as(count: int, one: str, many: str) -> str:
    return f"{count} {one if count == 1 else many}"


def some(items: list[str], limit: int = 12) -> str:
    """Up to LIMIT items on one line, with the count of the rest."""
    return ", ".join(items[:limit]) + (f", and {len(items) - limit} more" if len(items) > limit else "")


def shown(text: object) -> str:
    """Text for a terminal or a CI log: a character no reader sees, a line break among them, is written as its code point."""
    return "".join(f"<U+{ord(char):04X}>" if unseen_char(char) or char in "\n\r" else char for char in str(text))


def moved_in_table(a: Kept, b: Kept) -> list[tuple[int, str, str]]:
    """Each row of a table that now holds what another row held.

    A value moved from one row to another changes two claims and no count on
    the page. Rows are matched by their first cell, so this reads a table
    only where the first cells came through and each names one row.
    """
    names_a, names_b = Counter(name for _, name, _ in a.rows), Counter(name for _, name, _ in b.rows)
    if names_a != names_b:
        return []
    earlier = {name: held for _, name, held in a.rows if names_a[name] == 1}
    later = {name: held for _, name, held in b.rows if names_b[name] == 1}
    findings = []
    for line, name, held in b.rows:
        if name not in earlier:
            continue
        lost, gained = earlier[name] - held, held - earlier[name]
        if any(gained & (earlier[other] - later[other]) for other in earlier if other != name):
            was = f"held {some(sorted(lost))}, and now holds" if lost else "now holds"
            findings.append((line, "table", f'the row "{name[:40]}" {was} {some(sorted(gained))}, which another row held'))
    return findings


def reordered_steps(a: Kept, b: Kept, new: Doc) -> list[tuple[int, str, str]]:
    """The items of a numbered list in a new order, which changes what a reader does first."""
    if a.steps == b.steps or Counter(a.steps) != Counter(b.steps):
        return []
    moved = next(step for step, other in zip(b.steps, a.steps) if step != other)
    line = next((number for number, text in new.numbered_body() if moved[:40] in text), 1)
    return [(line, "list", f'the items of a numbered list stand in a new order, from "{moved[:70]}"')]


def renamed_links(a: Kept, b: Kept, new: Doc):
    """Each link whose words changed while its target stayed: findings and notes.

    The words a reader sees for a link name its target. Two links that changed
    their words with each other are a finding, as two targets swapped are. Any
    other change of a link's words is a note.
    """
    findings, notes = [], []
    read: list[dict[str, Counter]] = [{}, {}]
    for texts, kept in zip(read, (a, b)):
        for target, words in kept.link_texts:
            texts.setdefault(target, Counter())[words] += 1
    was, now = read
    renamed = {
        target: (was[target] - now[target], now[target] - was[target])
        for target in was
        if target in now and sum(was[target].values()) == sum(now[target].values()) and was[target] != now[target]
    }
    for target, (words_gone, words_new) in renamed.items():
        line = next((number for number, text in new.numbered_body() if target in text), 1)
        crossed = next((other for other in renamed if other != target and renamed[other][0] & words_new and renamed[other][1] & words_gone), None)
        if crossed:
            findings.append((line, "link", f'the links to "{target}" and "{crossed}" changed their words with each other'))
        else:
            notes.append((line, "link-text", f'the link to "{target}" read "{some(sorted(words_gone))}", and now reads "{some(sorted(words_new))}"; check that the words still name that page'))
    return findings, notes


def broken(old: Doc, new: Doc) -> list[tuple[int, str, str]]:
    """A paragraph that now stops in the middle of a sentence, as one cut in two by accident does."""

    def open_ended(doc: Doc) -> list[tuple[int, str]]:
        return [(block.line_at(0), block.text) for block in prose_blocks(doc) if block.kind == "paragraph" and not WHOLE_END.search(mask(block.text).rstrip())]

    before, after = open_ended(old), open_ended(new)
    if len(after) <= len(before):
        return []
    earlier = {text for _, text in before}
    line, text = next(((line, text) for line, text in after if text not in earlier), after[0])
    return [(line, "broken", f'a paragraph ends in the middle of a sentence, and the earlier text had {len(before)} that did: "...{text[-60:]}"')]


def page_words(a: Kept, b: Kept) -> str | None:
    """The note on the words a rewording took from the page and brought to it, or None.

    A sentence may go when the page states each of its facts elsewhere, and
    then no word goes with it. So a word that is gone from the whole page is
    where a cut may have taken a fact, and a new word is where one may have
    come in. A plainer word for the same thing shows here too, and a reader
    tells the two apart.
    """
    gone = [word for key, word in a.page_words.items() if key not in b.page_words]
    came = [word for key, word in b.page_words.items() if key not in a.page_words]
    if not gone and not came:
        return None
    return f"words gone from the page: {some(gone) or 'none'}; words new on the page: {some(came) or 'none'}; check that no fact went or came with them"


def not_prose(old: Doc, new: Doc) -> list[tuple[int, str, str]]:
    """The first line of a script that is not prose and differs: code, a directive, a command in a comment, or the name that opens a row."""
    was, now = [text for _, text in old.apart], [text for _, text in new.apart]
    if was == now:
        return []
    at = next((n for n, (x, y) in enumerate(zip(was, now)) if x != y), min(len(was), len(now)))
    if at < len(now):
        line, text = new.apart[at]
        return [(line, "not-prose", f'this line is not prose, and it differs from the earlier text; a rewording of comments changes no code, command or name: "{text.strip()[:80]}"')]
    line, text = old.apart[at]
    return [(1, "not-prose", f'a line that is not prose is gone (line {line} of the earlier text): "{text.strip()[:80]}"')]


def differences(rule: str, what: str, old: list[tuple[str, int]], new: list[tuple[str, int]]):
    """Each token whose count changed, as (line, rule, message, how, token)."""
    before, after = Counter(token for token, _ in old), Counter(token for token, _ in new)
    old_line = {token: line for token, line in reversed(old)}
    new_line = {token: line for token, line in reversed(new)}
    for token in sorted(set(before) | set(after)):
        was, now = before[token], after[token]
        if was == now:
            continue
        if now == 0:
            yield old_line[token], rule, f'{what} "{token}" is gone (line {old_line[token]} of the earlier text)', "gone", token
        elif was == 0:
            yield new_line[token], rule, f'{what} "{token}" is new', "new", token
        else:
            how = "fewer" if now < was else "more"
            yield new_line[token], rule, f'{what} "{token}" appears {times(now)}, and the earlier text had it {times(was)}', how, token


def compare(path: Path, old: Doc, new: Doc, expect_concept: bool, raw: tuple[Doc, Doc] | None = None):
    """What differs between two versions besides the wording: findings, notes, and the words each version holds.

    For a script, OLD and NEW are its prose, and RAW is the whole file twice,
    which the search for a character no reader sees reads, code included.

    A finding is something a rewording never changes. A note is something a
    rewording may change and a reader should look at, such as a link target,
    a quotation or a number that a cut sentence held and the page still holds.
    """
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
    whole_old, whole_new = raw or (old, new)
    had = Counter(char for line in whole_old.lines for char in unseen_in(line))
    has = Counter(char for line in whole_new.lines for char in unseen_in(line))
    for char in sorted(has):
        if has[char] > had[char]:
            line = next(number for number, text in enumerate(whole_new.lines, start=1) if char in unseen_in(text))
            findings.append((line, "unseen", f"{described(char)} is new, and a rewording adds no character a reader cannot see"))

    # A concept somebody vouched for keeps its body. No flag turns this off.
    if concept and old.body != new.body:
        said = {
            "person": "a person wrote this concept ({}), so its body must stay as it was",
            "edited": "a person edited this concept ({}), so its body must stay as it was",
            "refuted": "this concept is refuted ({}), so its body must stay as it was until someone corrects it",
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
        ("link", "the link label", a.labels, b.labels),
        ("image", "the image", a.images, b.images),
        ("fence", "the indented code block", a.indented, b.indented),
        ("rfc2119", "the keyword", a.rfc, b.rfc),
        ("html", "the inline HTML tag or comment", a.html, b.html),
    ):
        findings.extend((line, rule, words) for line, rule, words, _, _ in differences(rule, what, list_a, list_b))

    # A sentence that repeats what the page already says may go (rule 10). So a
    # link target or a quotation that the page still holds is a note. A number
    # is a note only when each thing it counted still stands: cut `3 workers`
    # from a page that also says `3 times`, and a fact is gone.
    still = "; the page still holds it, so check that what was cut said nothing more"
    for rule, what, list_a, list_b in (("link", "the link target", a.links, b.links), ("quote", "the quoted text", a.quotes, b.quotes)):
        for line, rule, words, how, _ in differences(rule, what, list_a, list_b):
            (notes if how == "fewer" else findings).append((line, rule, words + (still if how == "fewer" else "")))
    for line, rule, words, how, token in differences("digits", "the number", a.numbers, b.numbers):
        stands = how == "fewer" and all(b.claims[claim] for claim in a.claims if claim[0] == token)
        (notes if stands else findings).append((line, rule, words + (still if stands else "")))

    # A code span that is gone is a finding. One that came, or that appears
    # more or less often, is a note, since a rewording may name a thing in
    # code. One note lists each kind, so that a long page gives two lines.
    fresh: list[tuple[int, str]] = []
    recounted: list[tuple[int, str]] = []
    for line, rule, words, how, token in differences("code", "the code span", a.codes, b.codes):
        if how == "gone":
            findings.append((line, rule, words))
        else:
            (fresh if how == "new" else recounted).append((line, f"`{token}`"))
    for spans, what in ((fresh, "code spans new on the page"), (recounted, "code spans that appear more or less often than in the earlier text")):
        if spans:
            notes.append((spans[0][0], "code", f"{what}: {some([span for _, span in spans])}"))

    if a.related != b.related:
        findings.append((b.related_at, "related", "the lokf:related region differs from the earlier text"))
    if a.questions != b.questions:
        findings.append((b.questions_at, "open-questions", f'the "{OPEN_QUESTIONS}" section differs from the earlier text'))
    if b.list_items < a.list_items:
        findings.append((1, "list", f"{b.list_items} list items, and the earlier text had {a.list_items}"))
    if a.ticked != b.ticked:
        findings.append((1, "list", f"{b.ticked} ticked items, and the earlier text had {a.ticked}"))
    if b.table_rows < a.table_rows:
        findings.append((1, "table", f"{b.table_rows} table rows, and the earlier text had {a.table_rows}"))
    if b.table_cells < a.table_cells:
        findings.append((1, "table", f"{b.table_cells} table cells, and the earlier text had {a.table_cells}"))
    if a.breaks != b.breaks:
        findings.append((1, "hard-break", f"{b.breaks} hard line breaks, and the earlier text had {a.breaks}; a rewording keeps the breaks a reader sees"))

    heads_a, heads_b = [text for _, text in a.headings], [text for _, text in b.headings]
    if heads_a != heads_b:
        pairs = list(zip(heads_a + [""] * len(heads_b), b.headings + [(1, "")] * len(heads_a)))
        before, (line, after) = next((x, y) for x, y in pairs if x != y[1])
        words = f'a heading differs from the earlier text: "{after}" was "{before}"'
        (findings if concept else notes).append((line, "heading", words + ("" if concept else "; links may point at it")))

    findings.extend(moved_in_table(a, b))
    findings.extend(reordered_steps(a, b, new))
    findings.extend(broken(old, new))
    renamed, reworded = renamed_links(a, b, new)
    findings.extend(renamed)
    notes.extend(reworded)

    for line, rule, words, _, _ in differences("number-word", "the number word", a.number_words, b.number_words):
        notes.append((line, rule, words + "; digits cannot show whether a count changed"))
    flips, doubts, placed = turned(a, b)
    findings.extend(flips)
    notes.extend(doubts)
    for line, rule, words, _, _ in differences("date-word", "the day or month", a.date_words, b.date_words):
        notes.append((line, rule, words + "; digits cannot show whether a date changed"))
    # A word of strength is noted on the page only for what no sentence above
    # accounts for, since a note with a line is the one a reader can act on.
    for word in (*STRENGTH, "a negation"):
        change = b.strength[word] - a.strength[word]
        if change and change != placed[word]:
            name = word if word == "a negation" else f'"{word}"'
            beyond = ", beyond the sentences noted" if placed[word] else ""
            notes.append((1, "strength", f"{name} appears {times(b.strength[word])}, and the earlier text had it {times(a.strength[word])}{beyond}"))
    lost_or_gained = page_words(a, b)
    if lost_or_gained:
        notes.append((1, "page-words", lost_or_gained))
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
    try:
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
    except OSError as exc:
        raise Usage(f"cannot run git: {exc.strerror}; keep a copy and use --before") from exc
    return normalise(shown.stdout) if shown.returncode == 0 else None


def reserved_in_bundle(path: Path) -> bool:
    return path.name in RESERVED and bundle_root(path) is not None


def check_style(
    files: list[Path],
    max_words: int | None = None,
    max_paragraph: int | None = None,
    audience: str | None = None,
    max_sentences: int | None = None,
):
    """The style rules for each file, and a character no reader sees in any of them.

    A file is held to the band --audience names, or else to the band its
    first paragraph names, or else to the adult limits. --max-words,
    --max-paragraph and --max-sentences set their own limit over any band's.
    A script is read as its comments; the search for a character no reader
    sees reads its every line.
    """
    findings, notes = [], []
    for path in files:
        text = read(path)
        whole = Doc(text)
        doc = script_doc(text, python=path.suffix.lower() == ".py") if is_script(path) else whole
        found = unseen(whole)
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
            count = max_sentences if max_sentences is not None else band.sentences if band else MAX_SENTENCES
            found += style(doc, words, paragraph, count, band_words=band is not None)
            for rule, note in (("grade", graded(doc, name, band)), ("vocabulary", vocabulary(doc))) if band else ():
                if note:
                    notes.append((path, 1, rule, note))
        findings.extend((path, *finding) for finding in sorted(found, key=lambda finding: finding[0]))
    return findings, notes, f"{len(files)} file(s), and nothing a script can see breaks the style rules or hides from a reader"


def check_pair(label: Path, old_text: str, new_text: str, in_bundle: bool):
    """Compare two versions of one file, with the bundle's reserved files set apart. The third value is the words before and after, which a reserved file does not count towards.

    A script is compared as its comments and docstrings. Every other line
    must stay as it was, since a rewording of comments changes no code. The
    search for a character no reader sees reads every line.
    """
    if in_bundle and label.name == "log.md":
        # A line of the earlier log must still be there, and in its order.
        rest = iter(new_text.split("\n"))
        lost = next((line for line in old_text.split("\n") if line.strip() and line not in rest), None)
        if lost is not None:
            return [(label, 1, "reserved", f'ktl-prose adds one line to the log and takes none away: "{lost}" is gone')], [], (0, 0)
        return [], [(label, 1, "reserved", "the bundle's log is not compared; ktl-prose adds one line to it")], (0, 0)
    old, new = Doc(old_text), Doc(new_text)
    if is_script(label):
        python = label.suffix.lower() == ".py"
        old_prose, new_prose = script_doc(old_text, python), script_doc(new_text, python)
        found, noted, words = compare(label, old_prose, new_prose, expect_concept=False, raw=(old, new))
        found.extend(not_prose(old_prose, new_prose))
        return [(label, *f) for f in found], [(label, *n) for n in noted], words
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
    return findings, notes, f"nothing the script reads differs (1 file): {counted(was, now)}"


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
    return findings, notes, f"nothing the script reads differs ({len(files)} file(s) against {ref}): {counted(was, now)}"


def frontmatter_list(fm: list[str] | None, key: str) -> list[str]:
    """The values of one top-level frontmatter key, as a block list, a flow list or a single value."""
    lines = fm or []
    for index, line in enumerate(lines):
        found = re.match(rf"^{re.escape(key)}\s*:\s*(.*)$", line)
        if not found:
            continue
        rest = found.group(1).split(" #")[0].strip()
        if rest.startswith("["):
            return [value.strip().strip("\"'") for value in rest.strip("[]").split(",") if value.strip()]
        if rest:
            return [rest.strip("\"'")]
        values = []
        for item in lines[index + 1 :]:
            entry = re.match(r"^\s*-\s+(.*)$", item)
            if entry:
                values.append(entry.group(1).split(" #")[0].strip().strip("\"'"))
            elif item.strip() and not item[0].isspace():
                break
        return values
    return []


def link_keys(kept: Kept, path: Path) -> list[tuple[str, int, str]]:
    """Each link of one file as (key, line, target as written).

    The key lets two files in different folders compare their links: a
    wikilink by the name of the note it opens, a relative path resolved from
    the file's own folder, and a URL or an anchor as written.
    """
    wikis = Counter(target for target, _ in kept.wikilinks)
    keys = []
    for target, line in kept.links:
        if wikis[target] > 0:
            wikis[target] -= 1
            name = target.split("#")[0].strip().rsplit("/", 1)[-1]
            keys.append((f"[[{(name[:-3] if name.lower().endswith('.md') else name).lower()}]]", line, target))
            continue
        written = target.strip().split()[0] if target.strip() else ""
        if not written or written.startswith("#") or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", written):
            keys.append((written, line, target))
            continue
        where, _, fragment = written.partition("#")
        try:
            key = str((path.parent / unquote(where)).resolve()) if where else ""
        except (OSError, ValueError):  # a null byte or a name too long is no path
            key = where
        keys.append((key + (f"#{fragment}" if fragment else ""), line, target))
    return keys


def told_in_frontmatter(kept: Kept, doc: Doc) -> None:
    """Add what a page's title and description say: a retelling states facts there too."""
    told, inside = [], False
    for line in doc.fm or []:
        if not line[:1].isspace():
            inside = re.match(r"^(?:title|description)\s*:\s*(.*)$", line) is not None
            line = re.sub(r"^[^:]*:\s*", "", line, count=1).strip().strip("\"'") if inside else ""
            line = "" if re.fullmatch(r"[>|][+-]?\d?", line) else line
        if inside and line.strip():
            told.append(line.strip())
    said = Kept(Doc("\n".join(["---", "---", " ".join(told)])))
    for name in ("numbers", "links", "wikilinks", "codes", "quotes"):
        getattr(kept, name).extend((token, 1) for token, _ in getattr(said, name))


def check_derived(adult_path: Path, young_path: Path):
    """What a retelling holds that the adult text it retells does not: findings, notes, and the words of each.

    A retelling may leave out anything and add no fact, so each comparison
    runs one way: what is new in the retelling is a finding, and what it left
    out is a note. Outside a bundle the retelling's first paragraph must link
    the adult file; in a bundle it must also name the adult concept under
    derivedFrom. Whether a person wrote or confirmed the retelling is a note
    here, since this check changes nothing; --before and --against keep the
    refusals for a rewording.
    """
    adult, young = Doc(read(adult_path)), Doc(read(young_path))
    root = bundle_root(young_path)
    a, y = Kept(adult, whole=True), Kept(young, whole=True)
    told_in_frontmatter(a, adult)
    told_in_frontmatter(y, young)
    findings: list[tuple[int, str, str]] = []
    notes: list[tuple[int, str, str]] = []
    back = {str(adult_path.resolve()), f"[[{adult_path.stem.lower()}]]"}

    def links_back(key: str) -> bool:
        return key.split("#")[0] in back

    # Who the retelling is for, and the page it retells.
    said = declared(young)
    ages = Counter(re.findall(r"\d+", said[2])) if said else Counter()
    if said is None:
        notes.append((1, "audience", "the first paragraph names no readers, and a retelling opens by saying who it is for"))
    first = next(iter(prose_blocks(young)), None)
    opening = []
    if first is not None and first.kind == "paragraph":
        # A link back by reference: its definition stands apart, further down.
        used = {label.lower() for label in re.findall(r"\[([^\]\[]+)\]", first.text)}
        defined = [f"[{label}]: {target}" for label, target in y.definitions.items() if label in used]
        opening_doc = Kept(Doc("\n".join(["---", "---", first.text, "", *defined])))
        opening = [key for key, _, _ in link_keys(opening_doc, young_path)]
    if not any(links_back(key) for key in opening):
        line = first.line_at(0) if first is not None else 1
        findings.append((line, "derived-from", f"the first paragraph does not link {adult_path.name}, and a retelling opens by linking the page it retells"))
    if root is not None:
        adult_id = top_value(adult.fm or [], "id")
        if not adult_id or adult_id not in frontmatter_list(young.fm, "derivedFrom"):
            findings.append((1, "derived-from", f"derivedFrom does not name {adult_id or 'the adult concept'}, and a retelling in a bundle names the concept it retells"))
        if said and said[0] and f"audience-{said[0]}" not in frontmatter_list(young.fm, "tags"):
            notes.append((1, "audience", f"the tags hold no audience-{said[0]}, the band the first paragraph names"))
    rule, words = standing(young, expect_concept=root is not None)
    if rule in ("person", "edited", "confirmed", "retired", "refuted"):
        notes.append((1, rule, f"{words}; this check changes nothing, and only a person changes that body"))

    # A character no reader sees, which the adult text did not hold either.
    had = {char for line in adult.lines for char in unseen_in(line)}
    for char in sorted({char for line in young.lines for char in unseen_in(line)} - had):
        line = next(number for number, text in enumerate(young.lines, start=1) if char in unseen_in(text))
        findings.append((line, "unseen", f"{described(char)} is not in the adult text, and a retelling adds no character a reader cannot see"))

    # Links: the link back, and in a bundle a link to another concept, are allowed.
    adult_keys = {key for key, _, _ in link_keys(a, adult_path)}
    young_keys = link_keys(y, young_path)
    for key, line, target in young_keys:
        if key in adult_keys or links_back(key) or key.startswith("#"):
            continue
        inside = root is not None and (key.startswith("[[") or (key.endswith(".md") and key.startswith(str(root.resolve()))))
        if inside:
            notes.append((line, "link", f'"{target}" is a concept the adult text does not link; keep it only where it explains a term'))
        else:
            findings.append((line, "link", f'the link target "{target}" is not in the adult text, and a retelling adds no link'))
    left_out = adult_keys - {key for key, _, _ in young_keys}
    if left_out:
        notes.append((1, "link", f"{counted_as(len(left_out), 'link target', 'link targets')} of the adult text left out"))

    # Numbers, code, quotations and HTML, one way. The ages a retelling's first
    # paragraph names are its own, wherever it says them. A number the adult text
    # gives only in its code is still a number it gives.
    in_code = [text for text, _ in (*a.codes, *a.indented)] + [text for _, text in a.fences]
    coded = {number_token(found) for text in in_code for found in NUMBER.finditer(text)}
    for rule, what, (one, many), old, new in (
        ("digits", "the number", ("number", "numbers"), a.numbers, y.numbers),
        ("code", "the code span", ("code span", "code spans"), a.codes, y.codes),
        ("quote", "the quoted text", ("quotation", "quotations"), a.quotes, y.quotes),
        ("html", "the inline HTML tag", ("inline HTML tag", "inline HTML tags"), a.html, y.html),
        ("image", "the image", ("image", "images"), a.images, y.images),
        ("fence", "the indented code block", ("indented code block", "indented code blocks"), a.indented, y.indented),
    ):
        holds = {token for token, _ in old}
        reported = set()
        for token, line in new:
            if token in holds or token in reported:
                continue
            if rule == "digits" and (token in ages or token in coded):
                continue
            reported.add(token)
            findings.append((line, rule, f'{what} "{token}" is not in the adult text, and a retelling adds none'))
        gone = sorted(holds - {token for token, _ in new})
        if gone:
            shown = ", ".join(f'"{token}"' for token in gone[:5]) + (", and more" if len(gone) > 5 else "")
            notes.append((1, rule, f"{counted_as(len(gone), one, many)} of the adult text left out: {shown}"))

    # Fenced blocks are carried whole or left out.
    adult_fences = {text for _, text in a.fences}
    for index, (line, text) in enumerate(y.fences, start=1):
        if text not in adult_fences:
            findings.append((line, "fence", f"fenced block {index} is not in the adult text, and a retelling carries a block whole or leaves it out"))
    dropped = len(adult_fences - {text for _, text in y.fences})
    if dropped:
        notes.append((1, "fence", f"{counted_as(dropped, 'fenced block', 'fenced blocks')} of the adult text left out"))

    # The curator, both plugins and the pen match this heading whole.
    for line, heading in y.headings:
        if heading.lstrip("#").strip().lower() == OPEN_QUESTIONS.lstrip("#").strip().lower() and heading != OPEN_QUESTIONS:
            findings.append((line, "open-questions", f'"{heading}" must be spelt "{OPEN_QUESTIONS}", which the curator, both plugins and the pen match whole'))

    # Words a reader should check by hand.
    for keyword in sorted({token for token, _ in y.rfc}):
        notes.append((1, "rfc2119", f'"{keyword}" is in capitals; write it in lower case, and keep its strength'))
    for word in (*STRENGTH, "should"):
        if y.strength[word] > a.strength[word]:
            why = "a retelling never weakens must into should" if word == "should" else "check that no instruction grew stronger"
            had = f"has it {times(a.strength[word])}" if a.strength[word] else "never has it"
            notes.append((1, "strength", f'"{word}" appears {times(y.strength[word])}, and the adult text {had}; {why}'))
    for rule, what, old, new in (("number-word", "the number word", a.number_words, y.number_words), ("date-word", "the day or month", a.date_words, y.date_words)):
        holds = {token for token, _ in old}
        for token in sorted({token for token, _ in new} - holds):
            line = next(line for found, line in new if found == token)
            notes.append((line, rule, f'{what} "{token}" is not in the adult text; check that it says what the adult text says'))

    return findings, notes, (a.words, y.words)


def check_derived_files(adult_path: Path, young_path: Path):
    findings, notes, (adult_words, young_words) = check_derived(adult_path, young_path)
    fine = f"the retelling holds nothing the adult text does not (1 file): {young_words} words, and the adult text has {adult_words}"
    return [(young_path, *found) for found in findings], [(young_path, *note) for note in notes], fine


def bundle_audience(directory: Path) -> str:
    """The readers a bundle declares, as the line --bundle prints.

    The curation policy's `Younger readers:` line decides, and a person
    writes it with ktl-curator. Without one, a description in the root index
    that names readers aged in a band declares that band. Nothing else does:
    the readers are declared, never guessed.
    """
    policy = directory / "policies" / "knowledge-curation.md"
    if policy.is_file():
        for number, line in Doc(read(policy)).numbered_body():
            found = YOUNGER.match(line)
            if not found:
                continue
            value = found.group(1).strip("`'\" ")
            if value.lower() in ("", "no", "none"):
                return "audience: none declared (policies/knowledge-curation.md says no)"
            bands = [band.strip() for band in value.split(",")]
            if all(band in BANDS and band != "dyslexia" for band in bands):
                return f"audience: {', '.join(bands)} (policies/knowledge-curation.md)"
            return f"audience: none declared; line {number} of policies/knowledge-curation.md names {value!r}, which is no band of age"
    index = directory / "index.md"
    description = top_value(Doc(read(index)).fm or [], "description") if index.is_file() else None
    found = NAMES_READERS.search(description or "")
    if found and f"{int(found.group(1))}-{int(found.group(2))}" in BANDS:
        return f"audience: {int(found.group(1))}-{int(found.group(2))} (the description in index.md)"
    return "audience: none declared"


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
        print(f"{shown(path)}: {words if rule == 'rewrite' else 'skip: ' + words}")
    left = ", ".join(
        f"{tally[rule]} {name}"
        for rule, name in (
            ("confirmed", "confirmed by a person"),
            ("person", "written by a person"),
            ("edited", "edited by a person"),
            ("retired", "retired"),
            ("refuted", "refuted"),
            ("unreadable", "unreadable"),
            ("unrecorded", "with no record of who wrote them"),
            ("reserved", "reserved"),
        )
        if tally[rule]
    )
    print(bundle_audience(directory))
    print(f"OK: {tally['rewrite']} to reword, and {sum(tally.values()) - tally['rewrite']} to leave ({left or 'none'})")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="prose-check.py",
        usage="prose-check.py [--audience BAND] [--max-words N] [--max-paragraph N] [--max-sentences N] FILE... | --before OLD NEW | --against REF FILE... | --bundle DIR | --derived-from ADULT YOUNG",
        description="Report what a script can see of plain prose, and prove that a rewording changed only wording.",
    )
    parser.add_argument("files", nargs="*", type=Path, metavar="FILE")
    parser.add_argument("--before", nargs=2, type=Path, metavar=("OLD", "NEW"))
    parser.add_argument("--against", metavar="REF")
    parser.add_argument("--bundle", type=Path, metavar="DIR")
    parser.add_argument("--derived-from", nargs=2, type=Path, metavar=("ADULT", "YOUNG"))
    parser.add_argument("--audience", choices=sorted(BANDS), metavar="BAND")
    parser.add_argument("--max-words", type=int, metavar="N")
    parser.add_argument("--max-paragraph", type=int, metavar="N")
    parser.add_argument("--max-sentences", type=int, metavar="N")
    if len(argv) < 2:
        parser.print_usage(sys.stderr)
        return 2
    args = parser.parse_args(argv[1:])
    chosen = [name.replace("_", "-") for name in ("before", "against", "bundle", "derived_from") if getattr(args, name) is not None]
    if len(chosen) > 1:
        parser.error("give one of --before, --against, --bundle and --derived-from")
    if (args.before or args.bundle or args.derived_from) and args.files:
        parser.error(f"--{chosen[0]} takes no FILE")
    if not args.before and not args.bundle and not args.derived_from and not args.files:
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
        elif args.derived_from:
            findings, notes, fine = check_derived_files(*args.derived_from)
        elif args.against is not None:
            findings, notes, fine = check_against(args.against, args.files)
        else:
            findings, notes, fine = check_style(args.files, args.max_words, args.max_paragraph, args.audience, args.max_sentences)
    except Usage as exc:
        print(f"prose-check.py: {exc}", file=sys.stderr)
        return 2

    for path, line, rule, words in notes:
        print(f"note: {shown(path)}:{line}: {rule}: {shown(words)}", file=sys.stderr)
    for path, line, rule, words in findings:
        print(f"{shown(path)}:{line}: {rule}: {shown(words)}")
    if findings:
        return 1
    print(f"OK: {fine}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
