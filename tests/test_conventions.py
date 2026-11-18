"""knowledge-conventions.sh reports each convention a bundle breaks, and accepts what a convention allows.

This was check 11's synthetic bundle, and check 11c, in
scripts/validate-repository.sh. A checker that cannot fail is not covering
anything, so one bundle breaks each rule and the script must name each break.
A bundle that keeps every rule must pass: with CRLF line endings, through a
link, and without uv. Rule 14 reads the commits after a pull request's base,
so a small history stages a confirmation alone, one with an edit, Correct now
and a merge. Rule 6 reads a pin against that base too, so another stages a
pull request merged into a base that moved on, and a squash merge. Rule 17 reads log.md against the bundle, so another history
stages two days of logged writes after a base.

Thirteen of the eighteen rules run through `uv run`, so without uv the script
reports none of them. These tests fail, rather than skip, when uv is missing:
the job that runs them installs it.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import tomllib
from pathlib import Path

import pytest
import yaml

from conftest import BOM, SCRIPTS, Git, bash, count_lines, have, matches, mawk_path, mirror_uv, read, run, stopping_awk, write

CONVENTIONS = SCRIPTS / "knowledge-conventions.sh"


@pytest.fixture(scope="module", autouse=True)
def _uv_is_needed():
    if not have("uv"):
        pytest.fail(
            "uv is not on PATH, so rules 2, 3, 4, 7, 9, 10, 12, 13, 15, 16, 17 and 18 cannot run - install uv, or add the setup-uv step to the workflow running this"
        )


def r13(x, name, title, description, generated_at, more, body, base="https://example.invalid/k/"):
    """A concept human:contract confirmed on 2026-09-02, for rule 13."""
    write(
        x / f"{name}.md",
        "---\ntype: Service\nresource: pinned.md\n"
        f"id: {base}x/{name}\n"
        f"title: {title}\n"
        f"description: {description}\n"
        "generated:\n  by: process:ktl-librarian\n"
        f'  at: "{generated_at}"\n'
        'verified:\n  - by: human:contract\n    at: "2026-09-02T00:00:00Z"\n'
        f"{more}---\n\n# Overview\n\n{body}\n",
    )


def pinned(revision):
    return (
        "---\ntype: Service\nresource: pinned.md\nverified:\n  - by: human:contract\n"
        f'    at: "2026-09-17T00:00:00Z"\n    revision: "{revision}"\n---\n'
    )


def stamped(at):
    return f'---\ntype: Service\nresource: pinned.md\ngenerated:\n  by: process:ktl-librarian\n  at: "{at}"\n---\n'


def sourced(x, name, sources, body):
    """A concept with `sources` entries and a body, for rule 16."""
    write(
        x / f"{name}.md",
        f"---\ntype: Service\nid: https://example.invalid/k/x/{name}\nsources:\n{sources}---\n\n# Overview\n\n{body}\n",
    )


# Rule 2: quoted times that one reader takes differently from another. No
# script reads a lower-case z. The report cannot read a lower-case t or a time
# with no offset, which the federation build reads. The stored queries,
# comparing times as written, put an offset, a fraction or a date alone out
# of order. The report reads 30 February, and the build cannot; some Pythons
# read 24:00 and others refuse it. The report reads a leap second, which the
# build refuses, and which time.strptime takes and only datetime refuses. A
# zero-width space after the Z is invisible, so the finding prints the time
# as JSON writes it.
ODD_TIMES = [
    ("ts-lower-z", "2026-09-14T00:00:00z"),
    ("ts-lower-t", "2026-09-14t00:00:00Z"),
    ("ts-no-offset", "2026-09-14T00:00:00"),
    ("ts-offset", "2026-09-14T01:00:00+01:00"),
    ("ts-fraction", "2026-09-14T00:00:00.5Z"),
    ("ts-date", "2026-09-14"),
    ("ts-no-day", "2026-02-30T00:00:00Z"),
    ("ts-hour-24", "2026-09-14T24:00:00Z"),
    ("ts-second-60", "2016-12-31T23:59:60Z"),
    ("ts-hidden", "2026-09-14T00:00:00Z" + chr(0x200B)),
]
# The rule holds a `generated` record too. This one is to the minute, which
# every script reads, and which the stored queries put after each time in
# that minute.
ODD_STAMP = ("ts-stamp-minutes", "2026-09-14T00:00Z")


@pytest.fixture(scope="module")
def findings(tmp_path_factory) -> str:
    """What the script reports on a bundle that breaks each rule once."""
    bad = tmp_path_factory.mktemp("conventions-bad")
    k = bad / "k"
    x = k / "x"
    # A suffixed heading, then two bare dates in ascending order: one finding each.
    write(
        k / "log.md",
        "# Change Log\n\n## 2026-09-14 (2)\n\n* **A**: b.\n\n## 2026-09-13\n\n* **C**: d.\n\n## 2026-09-15\n\n* **E**: f.\n",
    )
    write(
        x / "a.md",
        "---\ntype: Service\nverified:\n  by: process:ktl-librarian\n  at: 2026-09-14T00:00:00Z\n---\n\n## Open questions\n\n- unclear (process:ktl-librarian, 2026-09-12)\n",
    )
    write(
        x / "b.md",
        '---\ntype: Service\nverified:\n  - by: process:ktl-librarian\n    at: "2026-09-13T00:00:00Z"\n  - by: process:ktl-librarian\n    at: "2026-09-14T00:00:00Z"\n---\n',
    )
    # A local resource that does not exist (a URL would be skipped, never fetched).
    write(x / "c.md", "---\ntype: Service\nresource: no-such-file.md\n---\n")
    # A commit-shaped `revision` must name a commit holding the resource: make
    # the directory a repository with one committed file, pin d.md to a commit
    # that does not exist and e.md to the one that does. Only d.md may be reported.
    git = Git(bad)
    git.init()
    write(bad / "pinned.md", "pinned\n")
    git("add", "pinned.md")
    git("commit", "-q", "-m", "pin")
    real = git("rev-parse", "HEAD")
    write(x / "d.md", pinned("0" * 40))
    write(x / "e.md", pinned(real))
    # Rule 11, in three cases:
    # - a time later than the commit that recorded it, committed at a fixed
    #   committer date so the verdict does not depend on today;
    # - a time in the future on a file not committed yet;
    # - a time before its commit, which must pass.
    write(x / "r11-late.md", stamped("2026-09-17T01:00:00Z"))
    write(x / "r11-ok.md", stamped("2026-09-16T23:00:00Z"))
    git("add", "k/x/r11-late.md", "k/x/r11-ok.md")
    git("commit", "-q", "-m", "stamp", env={"GIT_COMMITTER_DATE": "2026-09-17T00:00:00Z"})
    write(x / "r11-future.md", stamped("2999-01-01T00:00:00Z"))
    # Rule 13: a confirmed concept edited after its confirmation, with
    # `generated` left as it was, in its body or in its description. What a
    # confirmation does not cover must pass: a person's note with the status
    # it sets, KTL Registrar's block with its own `## Related` heading, and
    # values written back requoted. So must an edit that moved `generated`
    # past the confirmation, one its person confirmed again, and an id that
    # moved with the bundle's base_iri; an edit made beside that move fails.
    for n in ["r13-edited", "r13-description", "r13-notes", "r13-restamped", "r13-reconfirmed", "r13-moved", "r13-moved-edited"]:
        r13(x, n, n, "what it was.", "2026-09-01T00:00:00Z", "", "The text a person confirmed.")
    write(k / "index.md", "---\nbase_iri: https://example.invalid/k/\n---\n\n# K\n")
    git("add", "k/index.md", *[f"k/x/{p.name}" for p in sorted(x.glob("r13-*.md"))])
    git("commit", "-q", "-m", "confirmed")
    r13(
        x,
        "r13-reconfirmed",
        "r13-reconfirmed",
        "what it was.",
        "2026-09-01T00:00:00Z",
        '  - by: human:contract\n    at: "2026-09-05T00:00:00Z"\n',
        "The text changed, then confirmed again.",
    )
    git("commit", "-q", "-am", "edited, and confirmed again")
    r13(x, "r13-edited", "r13-edited", "what it was.", "2026-09-01T00:00:00Z", "", "The text someone changed by hand.")
    r13(
        x,
        "r13-description",
        "r13-description",
        "what it says now.",
        "2026-09-01T00:00:00Z",
        "",
        "The text a person confirmed.",
    )
    r13(x, "r13-restamped", "r13-restamped", "what it was.", "2026-09-03T00:00:00Z", "", "The text the pen changed.")
    moved = "https://example.invalid/moved/"
    r13(x, "r13-moved", "r13-moved", "what it was.", "2026-09-01T00:00:00Z", "", "The text a person confirmed.", moved)
    r13(x, "r13-moved-edited", "r13-moved-edited", "what it was.", "2026-09-01T00:00:00Z", "", "The text changed in the move.", moved)
    r13(
        x,
        "r13-notes",
        '"r13-notes"',
        "what it was.",
        "2026-09-01T00:00:00Z",
        "status: draft\n",
        "The text a person confirmed.\n\n## Open questions\n\n- 2026-09-03, human:contract: is this still current?\n\n"
        "<!-- lokf:related -->\n#how-to\n\n## Related\n\n- [[r13-edited]] (dependsOn)\n<!-- /lokf:related -->",
    )
    # Rules 7 to 9 and the line-ending tolerance:
    # - a CRLF copy of a file that breaks rule 2 must still be reported;
    # - a byte order mark and a file with no frontmatter are findings;
    # - a sync client's conflict copy shares its original's id and has a name
    #   no slug would;
    # - a directory whose case differs is a path-shape finding.
    write(
        x / "f-crlf.md",
        "---\r\ntype: Service\r\nverified:\r\n  - by: process:ktl-librarian\r\n    at: 2026-09-14T00:00:00Z\r\n---\r\n",
    )
    write(x / "g-bom.md", BOM + b"---\ntype: Service\n---\n")
    write(x / "h-nofm.md", "type: Service\n")
    write(x / "i.md", "---\ntype: Service\nid: https://example.invalid/k/x/i\n---\n")
    shutil.copy(x / "i.md", x / "i (conflicted copy 2026-09-17).md")
    write(k / "Upper" / "j.md", "---\ntype: Service\n---\n")
    # Rule 10: an event spelt so that the gates' line readers cannot see it.
    write(
        x / "q-quotedkey.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/q\nverified:\n  - "by": human:contract\n    at: "2026-09-17T00:00:00Z"\n---\n',
    )
    write(
        x / "t-tag.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/t\nverified: [{ by: !!str human:contract, at: "2026-09-17T00:00:00Z" }]\n---\n',
    )
    # An anchor and an alias on fields no gate reads: refused all the same.
    write(
        x / "t-anchor.md",
        "---\ntype: Service\nid: https://example.invalid/k/x/t-anchor\ntitle: &t Anchored\ndescription: *t\n---\n",
    )
    write(
        x / "q2-quotedevent.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/q2-quotedevent\n"verified":\n  - by: human:contract\n    at: "2026-09-17T00:00:00Z"\n---\n',
    )
    write(
        x / "q3-explicit.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/q3-explicit\n? verified\n: - by: human:contract\n    at: "2026-09-17T00:00:00Z"\n---\n',
    )
    write(
        x / "q4-space.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/q4-space\nverified :\n  - by: human:contract\n    at: "2026-09-17T00:00:00Z"\n---\n',
    )
    write(
        x / "q5-merge.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/q5-merge\n<<: { note: x }\n---\n',
    )
    write(
        x / "q6-below.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/q6-below\nverified:\n  - by:\n      human:contract\n    at: "2026-09-17T00:00:00Z"\n---\n',
    )
    write(
        x / "q7-escape.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/q7-escape\nverified:\n  - by: "hum\\x61n:contract"\n    at: "2026-09-17T00:00:00Z"\n---\n',
    )
    write(
        x / "q8-flowcomment.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/q8-flowcomment\nverified: [ # ]\n  { by: process:x, at: "2026-09-17T00:00:00Z" }\n]\n---\n',
    )
    write(x / "q9-indented.md", "---\n  type: Service\n  id: https://example.invalid/k/x/q9\n---\n")
    write(x / "qa-rootflow.md", '---\n{type: Service, id: "https://example.invalid/k/x/qa"}\n---\n')
    write(x / "qb-break.md", f"---\ntype: Service\nid: https://example.invalid/k/x/qb\nnote: x{chr(0x2028)}other: y\n---\n")
    write(x / "qd-dashes.md", "---\ntype: Service\nid: https://example.invalid/k/x/qd\ndescription: a---b\n---\n")
    os.symlink("qd-dashes.md", x / "qe-link.md")
    write(x / "qc-cr.md", "---\ntype: Service\nid: https://example.invalid/k/x/qc\nnote: x\rother: y\n---\n")
    # A comment beside such a field is valid YAML that a parser drops and a
    # line reader takes for part of the value. A comment on a line of its own,
    # and a `#` inside a quoted value, must pass.
    write(
        x / "cm-comment.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/cm\nverified:\n  - by: human:contract\n    at: "2026-09-17T00:00:00Z" # checked on site\n---\n',
    )
    write(
        x / "co-comment-apart.md",
        '---\ntype: Service\nresource: pinned.md\nid: https://example.invalid/k/x/co\nverified:\n  # a comment on a line of its own\n  - by: human:contract\n    at: "2026-09-17T00:00:00Z"\n    revision: "etag#1"\n---\n',
    )
    for name, at in ODD_TIMES:
        write(
            x / f"{name}.md",
            f'---\ntype: Service\nid: https://example.invalid/k/x/{name}\nverified:\n  - by: human:contract\n    at: "{at}"\n---\n',
        )
    write(x / f"{ODD_STAMP[0]}.md", stamped(ODD_STAMP[1]))
    # What only a parser sees: a multi-line flow item with an unquoted `at`; a
    # number where a timestamp should be; a block that does not parse,
    # reported on one line; a block that is a list rather than a mapping. And
    # what a parser must not see: a second librarian event inside a body code fence.
    write(
        x / "fl-flow.md",
        "---\ntype: Service\nid: https://example.invalid/k/x/fl\nverified: [\n  { by: process:ktl-librarian,\n    at: 2026-09-14T00:00:00Z }\n]\n---\n",
    )
    write(
        x / "n-int.md",
        "---\ntype: Service\nid: https://example.invalid/k/x/n\nverified:\n  - by: process:ktl-librarian\n    at: 20260914\n---\n",
    )
    write(x / "y-bad.md", "---\ntype: Service\nverified: [unclosed\n---\n")
    write(x / "l-list.md", "---\n- just a list\n---\n")
    write(
        x / "fence.md",
        '---\ntype: Service\nresource: pinned.md\nid: https://example.invalid/k/x/fence\nverified:\n  - by: process:ktl-librarian\n    at: "2026-09-14T00:00:00Z"\n---\n\n```yaml\nverified:\n  - by: process:ktl-librarian\n    at: "2026-09-15T00:00:00Z"\n```\n',
    )
    # Rule 18: an exclusion with a blank reason, one with none, and a material
    # listed as a source and, spelt another way, as an exclusion. A folder
    # left out apart from the one file the concept uses must pass, written as
    # a bare mapping, which every reader takes as a one-item list.
    write(bad / "docs" / "a.md", "a\n")
    write(bad / "tests" / "x.md", "x\n")
    write(x / "ex-blank.md", "---\ntype: Service\nresource: pinned.md\nexclusions:\n- resource: docs/a.md\n  reason: '  '\n- resource: tests\n---\n")
    write(
        x / "ex-both.md",
        "---\ntype: Service\nsources:\n- resource: docs/a.md\nexclusions:\n- resource: ./docs/a.md\n  reason: a draft\n---\n",
    )
    write(
        x / "ex-folder.md",
        "---\ntype: Service\nsources:\n- resource: tests/x.md\nexclusions:\n  resource: tests\n  reason: the suite, apart from the fixture this concept uses\n---\n",
    )
    # Rule 12: a bullet left behind by an edited description fails, in the
    # folder's index and in the root's. A bullet that still agrees, a concept
    # no index lists, and a line that lists two concepts must all pass.
    write(
        x / "idx-stale.md",
        "---\ntype: Service\nid: https://example.invalid/k/x/stale\ntitle: Stale\ndescription: what the concept says now.\n---\n",
    )
    write(
        x / "idx-fresh.md",
        "---\ntype: Service\nresource: pinned.md\nid: https://example.invalid/k/x/fresh\ntitle: Fresh\ndescription: >-\n  folded, and\n  still equal.\n---\n",
    )
    write(
        x / "idx-shared.md",
        "---\ntype: Service\nresource: pinned.md\nid: https://example.invalid/k/x/shared\ntitle: Shared\ndescription: listed only beside another.\n---\n",
    )
    write(
        k / "index.md",
        "---\nbase_iri: https://example.invalid/moved/\n---\n\n# K\n\n* [Stale](x/idx-stale.md) - what the concept said before.\n* [Fresh](x/idx-fresh.md) - folded, and still equal.\n* [Fresh](x/idx-fresh.md), [Shared](x/idx-shared.md) - a line that lists two.\n",
    )
    write(
        x / "index.md",
        "# X\n\n* [Stale, renamed](idx-stale.md) - what the concept says now.\n* [Fresh](idx-fresh.md) - folded, and still equal.\n",
    )
    # Rule 15: a concept with neither `resource` nor `sources` fails, and one
    # with only `sources` passes.
    write(x / "r15-none.md", "---\ntype: Service\nid: https://example.invalid/k/x/r15-none\n---\n")
    write(x / "r15-sources.md", "---\ntype: Service\nid: https://example.invalid/k/x/r15-sources\nsources:\n  - resource: pinned.md\n---\n")
    # Rule 16: a footnote whose label no id matches, a cited id with no
    # definition line, a definition that lacks its resource, an id no footnote
    # cites, an id with an upper-case letter, and one id naming two resources
    # in two concepts. A concept whose footnotes are all in order, one of them
    # quoting its resource inside backticks, must pass, and so must one whose
    # only footnote marks sit in a code fence and a code span.
    pin = "  - id: pin\n    resource: pinned.md\n"
    other = "  - id: other\n    resource: https://example.invalid/other\n"
    sourced(x, "fn-nolabel", pin, "A claim.[^pin] Another.[^ghost]\n\n[^pin]: pinned.md, line 1")
    sourced(x, "fn-nodef", pin, "A claim.[^pin]")
    sourced(x, "fn-noresource", pin, "A claim.[^pin]\n\n[^pin]: the pinned file, line 1")
    sourced(x, "fn-uncited", pin, "A claim with no footnote.")
    sourced(x, "fn-upper", "  - id: Pin\n    resource: pinned.md\n", "A claim.[^Pin]\n\n[^Pin]: pinned.md, line 1")
    sourced(x, "fn-two-a", "  - id: shared\n    resource: pinned.md\n", "A claim.[^shared]\n\n[^shared]: pinned.md, line 1")
    sourced(x, "fn-two-b", "  - id: shared\n    resource: https://example.invalid/other\n", "A claim.[^shared]\n\n[^shared]: https://example.invalid/other, section 2")
    sourced(x, "fn-ok", pin + other, "A claim.[^pin] Another.[^other]\n\n[^pin]: `pinned.md`, line 1\n[^other]: https://example.invalid/other, section 2")
    sourced(x, "fn-code", "  - resource: pinned.md\n", "Write `[^id]` after the claim.\n\n```markdown\nA claim.[^example]\n\n[^example]: docs/x.md, line 1\n```")
    return bash(CONVENTIONS, k).out


REPORTED = [
    "not a bare ISO date",
    "not newest-first",
    "x/a.md: unquoted timestamp",
    "bare mapping",
    "open question not",
    "2 process:ktl-librarian events",
    "resource not found",
    "does not hold",
    "f-crlf.md: unquoted timestamp",
    "g-bom.md: starts with a byte order mark",
    "h-nofm.md: no closed frontmatter block",
    "is declared by more than one file",
    "conflicted copy 2026-09-17).md: path is not lowercase",
    "Upper/j.md: path is not lowercase",
    "q-quotedkey.md: frontmatter uses a quoted key (by)",
    "q2-quotedevent.md: frontmatter uses a quoted key (verified)",
    "q3-explicit.md: frontmatter uses an explicit key (? verified)",
    "q4-space.md: frontmatter uses a space before the colon of verified",
    "q5-merge.md: frontmatter uses a merge key",
    "q6-below.md: frontmatter uses a by on the line below its key",
    "q7-escape.md: frontmatter uses an escape in by",
    "q8-flowcomment.md: frontmatter uses a comment inside the flow form of verified",
    "q9-indented.md: frontmatter uses a frontmatter block indented whole",
    "qa-rootflow.md: frontmatter uses a flow mapping for the whole frontmatter",
    "qb-break.md: frontmatter uses a line break a line reader does not see (U+2028)",
    "qc-cr.md: frontmatter uses a bare carriage return",
    "qd-dashes.md: frontmatter holds '---'",
    "qe-link.md: is a symbolic link",
    "t-tag.md: frontmatter uses a tag on",
    "t-anchor.md: frontmatter uses an anchor (&t)",
    "t-anchor.md: frontmatter uses an alias (*t)",
    "cm-comment.md: frontmatter uses a comment beside at",
    'r11-late.md: at "2026-09-17T01:00:00Z" is later than the commit that recorded it (2026-09-17T00:00:00Z)',
    'r11-future.md: at "2999-01-01T00:00:00Z" is in the future',
    "fl-flow.md: unquoted timestamp",
    "n-int.md: unquoted timestamp",
    "y-bad.md: frontmatter is not valid YAML",
    "l-list.md: frontmatter is not a mapping",
    re.compile(r"idx-stale\.md: its bullet in .*/k/index\.md does not match"),
    re.compile(r"idx-stale\.md: its bullet in .*/k/x/index\.md does not match"),
    "r13-edited.md: changed since human:contract confirmed it (2026-09-02, in ",
    "r13-description.md: changed since human:contract confirmed it",
    "r13-moved-edited.md: changed since human:contract confirmed it",
    "ex-blank.md: exclusions[0] gives no reason",
    "ex-blank.md: exclusions[1] gives no reason",
    'ex-both.md: exclusions[0].resource "./docs/a.md" is also one of its sources',
    *(f"{name}.md: timestamp {json.dumps(at)} at verified.[0].at is not a UTC time to the second" for name, at in ODD_TIMES),
    f"{ODD_STAMP[0]}.md: timestamp {json.dumps(ODD_STAMP[1])} at generated.at is not a UTC time to the second",
    "r15-none.md: neither resource nor sources names where it came from",
    "fn-nolabel.md: footnote [^ghost] names no sources[].id",
    "fn-nodef.md: footnote [^pin] has no definition line",
    "fn-noresource.md: footnote definition [^pin] does not quote its resource pinned.md",
    "fn-uncited.md: sources[].id pin is cited by no footnote",
    'fn-upper.md: sources[].id "Pin" is not lowercase',
    "id shared names more than one resource",
]


@pytest.mark.parametrize("want", REPORTED, ids=lambda w: w.pattern if isinstance(w, re.Pattern) else w)
def test_reports_each_break(findings, want):
    found = want.search(findings) if isinstance(want, re.Pattern) else want in findings
    assert found, f"conventions script failed to report '{want}' on a bundle that breaks it:\n{findings}"


ACCEPTED = [
    ("x/e.md", "whose revision holds its resource"),
    ("r11-ok.md", "whose time is before the commit that recorded it"),
    ("fence.md", "whose second librarian event is only an example in a code fence"),
    ("co-comment-apart.md", "whose comment sits on a line of its own, and whose revision holds a # inside its quotes"),
    ("idx-fresh.md", "whose index bullets carry its title and its folded description"),
    ("idx-shared.md", "whose only listing is a root line that names it beside another concept"),
    (
        "r13-notes.md",
        "whose changes since its confirmation are a person's note, its status, the registrar's block and a requoted title",
    ),
    ("r13-restamped.md", "whose edit moved generated past the confirmation"),
    ("r13-reconfirmed.md", "whose person confirmed it again after the edit"),
    ("r13-moved.md", "whose id moved with the bundle's base_iri and nothing else"),
    ("r15-sources.md", "whose sources list stands in for a resource"),
    ("fn-ok.md", "whose footnotes each name an id, each have a definition line, and quote their resources"),
    ("fn-code.md", "whose only footnote marks sit in a code fence and a code span"),
    ("ex-folder.md", "whose exclusion is a folder holding the one file it uses, written as a bare mapping"),
]


@pytest.mark.parametrize(("quiet", "why"), ACCEPTED, ids=[q for q, _ in ACCEPTED])
def test_accepts_what_a_rule_allows(findings, quiet, why):
    assert quiet not in findings, f"conventions script reported {quiet}, {why}:\n{findings}"


def test_rule_2_reports_only_the_times_in_another_shape(findings):
    shaped = {line.split(": timestamp ", 1)[0].rsplit("/", 1)[-1] for line in findings.splitlines() if ": timestamp " in line}
    assert shaped == {f"{name}.md" for name, _ in [*ODD_TIMES, ODD_STAMP]}, (
        f"conventions rule 2 reported a time written as date -u writes it, or missed one in another shape:\n{findings}"
    )


def test_reports_a_parse_error_on_one_line(findings):
    assert count_lines(findings, "y-bad.md") == 1, "conventions script spread a YAML parse error over several lines"


@pytest.mark.parametrize("name", ["fn-nolabel.md", "fn-nodef.md", "fn-noresource.md", "fn-uncited.md", "fn-upper.md"])
def test_rule_16_reports_each_failure_once(findings, name):
    assert count_lines(findings, name) == 1, f"conventions rule 16 reported {name} more than once, or not at all:\n{findings}"


@pytest.fixture
def good(tmp_path):
    """A bundle that keeps every convention, checked out with CRLF line endings."""
    k = tmp_path / "k"
    write(
        k / "log.md", "# Change Log\r\n\r\n## 2026-09-15\r\n\r\n* **A**: b.\r\n\r\n## 2026-09-14\r\n\r\n* **C**: d.\r\n"
    )
    write(
        k / "x" / "a.md",
        '---\r\ntype: Service\r\nresource: https://example.invalid/a\r\nid: https://example.invalid/k/x/a\r\ndescription: >-\r\n  folded, which the gates\r\n  never read\r\nverified:\r\n  - by: process:ktl-librarian\r\n    at: "2026-09-14T00:00:00Z"\r\n---\r\n\r\n## Open questions\r\n\r\n- 2026-09-14, process:ktl-librarian: fine\r\n',
    )
    return k


def test_reads_a_crlf_checkout_as_ci_reads_lf(good):
    """A folded description is fine: rule 10 reads only the fields the gates read."""
    result = bash(CONVENTIONS, good)
    assert result, f"conventions script misreads a CRLF checkout: {result.out}"


def test_without_uv_the_shell_half_says_what_it_skipped(good):
    path = "/usr/bin:/bin"
    if shutil.which("uv", path=path):
        pytest.skip("uv is on /usr/bin - the without-uv case cannot be staged here")
    result = bash(CONVENTIONS, good, env={"PATH": path}, stdout_only=True)
    assert result and matches(
        result.out, r"^OK - .*\(rules 2, 3, 4, 7, 9, 10, 12, 13, 15, 16, 17 and 18 not checked: uv not found\)"
    ), f"conventions script without uv did not say what it skipped: {result.out}"


def test_without_uv_strict_fails_rather_than_pass_rules_it_did_not_check(good):
    """A gate that forgot uv passed thirteen rules it never checked. With --strict, as every workflow runs it, that is exit 2, and a finding still exit 1."""
    path = "/usr/bin:/bin"
    if shutil.which("uv", path=path):
        pytest.skip("uv is on /usr/bin - the without-uv case cannot be staged here")
    result = bash(CONVENTIONS, good, "--strict", env={"PATH": path})
    assert result.rc == 2 and "not checked: uv not found" in result.out and "OK -" not in result.out, (
        f"conventions script --strict passed without uv (exit {result.rc}): {result.out}"
    )
    write(good / "log.md", "# Change Log\n\n## 15 September\n")
    result = bash(CONVENTIONS, "--strict", good, env={"PATH": path})
    assert result.rc == 1 and "heading is not a bare ISO date" in result.out, (
        f"conventions script --strict hid a finding behind the skipped rules (exit {result.rc}): {result.out}"
    )


def test_a_folder_named_like_a_concept_hides_no_finding(good, tmp_path):
    """mawk stopped at a folder named x.md, and the gate said OK for every rule the shell half reads."""
    write(good / "x" / "dir.md" / "keep", "")
    (good / "x" / "linked.md").symlink_to(good / "x" / "dir.md")
    write(good / "x" / "Upper.md", "---\ntype: Service\ntitle: U\nresource: https://example.invalid/u\n---\n")
    result = bash(CONVENTIONS, good, env=mawk_path(tmp_path))
    assert result.rc == 1 and "x/Upper.md: path is not lowercase" in result.out, (
        f"a folder named like a concept hid a finding (exit {result.rc}): {result.out}"
    )
    assert "Traceback" not in result.out and "read error" not in result.out, f"a folder named like a concept was read as one: {result.out}"


def test_an_awk_that_stops_early_is_no_pass(good, tmp_path):
    result = bash(CONVENTIONS, good, env=stopping_awk(tmp_path, "KC_LINKS"))
    assert result.rc == 2 and "could not be read to its end" in result.out and "OK -" not in result.out, (
        f"the gate passed rules its awk never finished reading (exit {result.rc}): {result.out}"
    )


@pytest.mark.parametrize("args", [["--strict", "--since"], ["--head", "HEAD"], ["--bogus"], ["a", "b"]])
def test_a_call_it_cannot_read_is_refused(good, args):
    result = bash(CONVENTIONS, *args)
    assert result.rc == 2 and "usage:" in result.out, f"conventions script accepted {args} (exit {result.rc}): {result.out}"


def failing_uv(tmp_path):
    """A PATH whose uv fails as uv does behind a package mirror that serves no upload times."""
    fake = write(
        tmp_path / "fakebin" / "uv",
        "#!/bin/sh\necho 'x No solution found when resolving script dependencies:' >&2\nexit 1\n",
    )
    fake.chmod(0o755)
    return f"{fake.parent}{os.pathsep}{os.environ['PATH']}"


def test_a_runner_that_cannot_start_is_not_a_finding(good, tmp_path):
    result = bash(CONVENTIONS, good, env={"PATH": failing_uv(tmp_path)})
    assert result.rc == 2, f"conventions script did not exit 2 when uv could not run its parser's half: {result.out}"
    assert "could not run" in result.out and "OK -" not in result.out, f"conventions script misreported a runner failure: {result.out}"
    shown = bash(CONVENTIONS, good, env={"PATH": failing_uv(tmp_path)}, stdout_only=True)
    assert "No solution" not in shown.out, f"conventions script printed uv's error as a finding: {shown.out}"


def test_behind_a_mirror_without_upload_times_the_parser_half_still_runs(good, tmp_path):
    """uv drops every file it cannot date, so the shell half lifts exclude-newer for the package uv names, and says so."""
    path, log = mirror_uv(tmp_path, "PyYAML-6.0.3.tar.gz")
    result = bash(CONVENTIONS, good, env={"PATH": path})
    assert result and "not checked" not in result.out, f"conventions script did not run its parser's half behind the mirror: {result.out}"
    assert "exclude-newer is lifted for pyyaml." in result.out, f"conventions script did not say it lifted the date: {result.out}"
    assert "--exclude-newer-package pyyaml=false" in read(log), f"uv run did not get the lifted date: {read(log)}"


def test_the_sidecar_venv_runs_the_parser_half_before_uv(good, tmp_path):
    """A host behind a mirror runs the parser's half from .lokf/.venv, which uv sync installed from uv.lock."""
    scripts = tmp_path / ".lokf" / "scripts"
    scripts.mkdir(parents=True)
    for name in ("knowledge-conventions.sh", "knowledge-conventions.py"):
        shutil.copy(SCRIPTS / name, scripts / name)
    write(tmp_path / ".lokf" / ".venv" / "bin" / "python", f'#!/bin/sh\nexec "{sys.executable}" "$@"\n').chmod(0o755)
    result = bash(scripts / "knowledge-conventions.sh", good, env={"PATH": failing_uv(tmp_path)})
    assert result and "not checked" not in result.out, f"conventions script did not run its parser's half from the sidecar's .venv: {result.out}"


SKELETON = {
    "PROJ_NAME": "Acme",
    "PROJ_DESC": "The Acme project.",
    "PROJ_SLUG": "acme",
    "BASE_IRI": "https://acme.example/knowledge/",
    "OWNER_NAME": "Ada",
    "OWNER_SLUG": "ada",
    "OWNER_TYPE": "Person",
    "TODAY": "2026-09-14",
}


def step_one(host, **values):
    """The block ktl-sidecar's SKILL.md gives for the placeholders, run in the host as written, less its mkdir."""
    found = re.search(r"```bash\nmkdir -p \.lokf/knowledge/services\n(.*?)```", read(SCRIPTS.parent.parent / "SKILL.md"), re.S)
    assert found, "SKILL.md's Step 1 still gives the block that fills the placeholders"
    path = f"{Path(sys.executable).parent}{os.pathsep}{os.environ['PATH']}"
    return run(["bash", "-c", found.group(1).replace("<skill>", str(SCRIPTS.parent.parent))], cwd=host, env={**SKELETON, **values, "PATH": path})


def skeleton(host):
    """The files of Step 1 that carry a placeholder, and Step 2's llms.txt, copied and not yet filled."""
    templates = SCRIPTS.parent
    shutil.copytree(templates / "knowledge", host / ".lokf" / "knowledge")
    for name in ("pyproject.toml", "justfile", "README.md", "queries.http"):
        shutil.copy(templates / name, host / ".lokf" / name)
    shutil.copy(templates / "llms.txt", host / "llms.txt")
    return host / ".lokf" / "knowledge"


def test_the_installed_skeleton_keeps_every_convention(tmp_path):
    """The bundle ktl-sidecar installs, with its placeholders filled, passes the gate before anyone edits it."""
    k = skeleton(tmp_path)
    filled = step_one(tmp_path)
    assert filled, filled.out
    left = [p for p in [*tmp_path.rglob("*.md"), *tmp_path.rglob("*.toml"), tmp_path / "llms.txt"] if re.search(r"<(PROJ|OWNER)_[A-Z]+>|<BASE_IRI>|<TODAY>", read(p))]
    assert not left, f"Step 1 left a placeholder in {left}"
    result = bash(CONVENTIONS, k)
    assert result, f"the sidecar's skeleton breaks its own conventions: {result.out}"


def test_step_one_writes_a_value_as_a_quoted_string_and_refuses_what_is_not_one_line(tmp_path):
    """The description comes from a manifest or a README, so a colon, a quote or a # in it stays text, and a line break adds no key."""
    spoken = 'Acme: the "platform" # with C:\\tools and <BASE_IRI>.'
    host = tmp_path / "quoted"
    k = skeleton(host)
    filled = step_one(host, PROJ_NAME='The "Acme": Platform', PROJ_DESC=spoken, OWNER_NAME="Ada: #1", OWNER_TYPE="Organization")
    assert filled, filled.out
    index = yaml.safe_load(read(k / "index.md").split("\n---\n")[0].removeprefix("---\n"))
    assert index["title"] == 'The "Acme": Platform Knowledge Bundle' and index["description"] == spoken and index["publisher"]["name"] == "Ada: #1", index
    assert index["publisher"]["type"] == "Organization" and index["publisher"]["id"] == "https://acme.example/knowledge/organization/ada", index
    service = yaml.safe_load(read(k / "services" / "example-service-a.md").split("\n---\n")[0].removeprefix("---\n"))
    assert service["description"].endswith('of The "Acme": Platform.'), service
    assert tomllib.loads(read(host / ".lokf" / "pyproject.toml"))["project"]["description"] == 'LOKF knowledge-bundle tooling for The "Acme": Platform.'
    assert f"> {spoken}\n" in read(host / "llms.txt") and '# The "Acme": Platform Knowledge Bundle\n' in read(k / "index.md"), "a body takes the value as it is"

    for token, value, said in (
        ("PROJ_DESC", "The platform.\nlicense: none", "PROJ_DESC: empty, or a line break or unprintable character"),
        ("OWNER_NAME", "Ada" + chr(0x200B), "OWNER_NAME: empty, or a line break or unprintable character"),
        ("PROJ_NAME", " ", "PROJ_NAME: empty"),
        ("BASE_IRI", "https://acme.example/knowledge", "BASE_IRI: not of the form"),
        ("PROJ_SLUG", "acme platform", "PROJ_SLUG: not of the form"),
        ("TODAY", "today", "TODAY: not of the form"),
        ("OWNER_TYPE", "Team", "OWNER_TYPE: not of the form"),
    ):
        host = tmp_path / f"refused-{token}"
        k = skeleton(host)
        before = read(k / "index.md")
        refused = step_one(host, **{token: value})
        assert not refused and said in refused.out, f"Step 1 took {token}={value!r}: {refused.out}"
        assert read(k / "index.md") == before and "<PROJ_NAME>" in read(host / "llms.txt"), "it wrote no file"


def test_every_free_text_placeholder_in_frontmatter_sits_in_a_quoted_string():
    """Step 1 escapes a value for a double-quoted string there, so a bare placeholder would take a colon as a key."""
    for path in sorted((SCRIPTS.parent / "knowledge").rglob("*.md")):
        text = read(path)
        if not text.startswith("---\n"):
            continue
        for line in text.split("\n---\n")[0].splitlines():
            if re.search(r"<(PROJ_NAME|PROJ_DESC|OWNER_NAME)>", line):
                assert re.fullmatch(r'\s*[a-z_]+: "[^"]*"', line), f"{path.name}: {line}"


def test_reads_a_bundle_reached_through_a_link(good):
    """The rearranged layout the sidecar's portability page allows must be read, not passed with zero files seen."""
    os.symlink(good, good.parent / "linked")
    write(good / "x" / "Bad.md", "x")
    result = bash(CONVENTIONS, good.parent / "linked")
    assert not result, f"conventions script passed a linked bundle unread: {result.out}"
    assert "Bad.md: path is not lowercase" in result.out, f"conventions script misread a linked bundle: {result.out}"


# Rule 14 (check 11c). A commit after the base that records a person's
# confirmation may change what the concept says only when that person is also
# its author, as Correct now records them. A confirmation alone passes; one
# with an edit fails; Correct now passes. A merge passes when the other side
# holds the confirmation, after a librarian's edit there: read against its
# first parent alone it would look like an edit and a confirmation together.

CONFIRMED = 'verified:\n  - by: human:contract\n    at: "2026-09-04T00:00:00Z"\n'


def v14c(k, name, by, at, verified, body):
    write(
        k / "x" / f"{name}.md",
        f"---\ntype: Service\nid: https://example.invalid/k/x/{name}\ntitle: {name}\nresource: https://example.invalid/src/{name}\n"
        f'generated:\n  by: {by}\n  at: "{at}"\n{verified}---\n\n# Overview\n\n{body}\n',
    )


@pytest.fixture(scope="module")
def rule14(tmp_path_factory):
    """The history, its base commit and the commit that confirmed with an edit."""
    v14 = tmp_path_factory.mktemp("conventions-rule14")
    k = v14 / "k"
    git = Git(v14)
    git.init()
    for n in ["only", "edited", "corrected", "merged"]:
        v14c(k, n, "process:ktl-librarian", "2026-09-01T00:00:00Z", "", "What the librarian wrote.")
    git("add", "-A")
    git("commit", "-q", "-m", "the librarian derives four concepts")
    base = git("rev-parse", "HEAD")
    git("checkout", "-q", "-b", "elsewhere")
    v14c(k, "merged", "process:ktl-librarian", "2026-09-03T00:00:00Z", "", "What the librarian wrote again.")
    git("commit", "-q", "-am", "the librarian refreshes one concept")
    v14c(k, "merged", "process:ktl-librarian", "2026-09-03T00:00:00Z", CONFIRMED, "What the librarian wrote again.")
    git("commit", "-q", "-am", "a person confirms the refreshed text")
    git("checkout", "-q", "main")
    v14c(k, "only", "process:ktl-librarian", "2026-09-01T00:00:00Z", CONFIRMED, "What the librarian wrote.")
    git("commit", "-q", "-am", "a person confirms, and changes nothing else")
    v14c(
        k,
        "edited",
        "process:ktl-librarian",
        "2026-09-01T00:00:00Z",
        CONFIRMED,
        "What someone changed in the same commit.",
    )
    git("commit", "-q", "-am", "a person confirms, and an edit rides along")
    v14c(k, "corrected", "human:contract", "2026-09-04T00:00:00Z", CONFIRMED, "What the person corrected.")
    git("commit", "-q", "-am", "Correct now: the person edits and confirms")
    git("merge", "-q", "--no-ff", "--no-edit", "elsewhere")
    edited_commit = git("log", "--format=%h", "-n", "1", "--grep=an edit rides along")
    return k, base, edited_commit


def test_rule_14_reports_a_confirmation_whose_commit_also_changed_the_text(rule14):
    k, base, edited_commit = rule14
    out = bash(CONVENTIONS, k, "--since", base).out
    want = f"k/x/edited.md: commit {edited_commit} records a confirmation by human:contract and changes what the concept says"
    assert want in out, f"conventions rule 14 did not report a confirmation made with an edit: {out}"


@pytest.mark.parametrize(
    ("quiet", "why"),
    [
        ("only.md", "a confirmation alone"),
        ("corrected.md", "Correct now, where the person is the author"),
        ("merged.md", "a merge whose other side holds the confirmation"),
    ],
)
def test_rule_14_accepts(rule14, quiet, why):
    k, base, _ = rule14
    out = bash(CONVENTIONS, k, "--since", base).out
    assert quiet not in out, f"conventions rule 14 reported {quiet}, {why}: {out}"


def test_rule_14_is_not_asked_without_since(rule14):
    k, _, _ = rule14
    result = bash(CONVENTIONS, k)
    assert result and "records a confirmation" not in result.out, (
        f"conventions script reported rule 14, or failed, with no base: {result.out}"
    )


def test_rule_14_says_when_the_clone_lacks_the_base(rule14):
    k, _, _ = rule14
    result = bash(CONVENTIONS, k, "--since", "0123456789abcdef")
    assert not result, f"conventions rule 14 passed a base the clone does not hold: {result.out}"
    assert "rule 14: the base commit 0123456789abcdef is not in this clone's history" in result.out, (
        f"conventions rule 14 failed some other way on an unknown base: {result.out}"
    )


# Rule 6 on a pull request. A pin names a commit the base holds, or the
# content as a digest. A commit the pull request made is replaced by a squash
# merge or a rebase, and the pin then names nothing: PR #383 left one on main,
# where only a fresh clone reported it. The gate checks out a merge into a
# base that moved on, so it names the last commit of the pull request, and
# the commits the base gained are not read as the pull request's.


def v6c(k, name, resource, verified="", body="What the librarian wrote."):
    write(
        k / "x" / f"{name}.md",
        f"---\ntype: Service\nid: https://example.invalid/k/x/{name}\ntitle: {name}\nresource: {resource}\n"
        f'generated:\n  by: process:ktl-librarian\n  at: "2026-09-01T00:00:00Z"\n{verified}---\n\n# Overview\n\n{body}\n',
    )


def confirmed_with(revision):
    return f'verified:\n  - by: human:contract\n    at: "2026-09-04T00:00:00Z"\n    revision: "{revision}"\n'


@pytest.fixture(scope="module")
def pull_request(tmp_path_factory):
    """The bundle on a merge of a pull request into its base, the base, the pull request's last commit and the commit it pinned of its own."""
    repo = tmp_path_factory.mktemp("conventions-rule6-pull-request")
    k = repo / "k"
    git = Git(repo)
    git.init()
    write(repo / "docs" / "a.md", "a\n")
    write(repo / "docs" / "b.md", "b\n")
    for name, resource in [("own", "docs/a.md"), ("digest", "docs/a.md"), ("held", "docs/b.md"), ("late", "docs/b.md"), ("folded", "docs/b.md")]:
        v6c(k, name, resource)
    git("add", "-A")
    git("commit", "-q", "-m", "the base")
    base = git("rev-parse", "HEAD")
    git("checkout", "-q", "-b", "pr")
    write(repo / "docs" / "a.md", "a, as the pull request changed it\n")
    git("commit", "-q", "-am", "the pull request changes a source")
    own = git("rev-parse", "HEAD")
    v6c(k, "own", "docs/a.md", confirmed_with(own))
    v6c(k, "digest", "docs/a.md", confirmed_with("sha256:" + hashlib.sha256((repo / "docs" / "a.md").read_bytes()).hexdigest()))
    v6c(k, "held", "docs/b.md", confirmed_with(base))
    git("commit", "-q", "-am", "a person confirms three concepts")
    head = git("rev-parse", "HEAD")
    git("checkout", "-q", "main")
    write(repo / "docs" / "b.md", "b, as the base changed it\n")
    git("commit", "-q", "-am", "the base changes a source")
    v6c(k, "late", "docs/b.md", confirmed_with(git("rev-parse", "HEAD")))
    v6c(k, "folded", "docs/b.md", CONFIRMED, "What a squash merge folded in with the confirmation.")
    git("commit", "-q", "-am", "another pull request, squash-merged")
    git("merge", "-q", "--no-ff", "--no-edit", "pr")
    return k, base, head, own


def test_rule_6_reports_a_pin_on_a_commit_the_pull_request_made(pull_request):
    k, base, head, own = pull_request
    out = bash(CONVENTIONS, k, "--since", base, "--head", head).out
    want = f"k/x/own.md: revision {own} names a commit made after the base, which a squash merge or a rebase replaces - pin the content of docs/a.md instead, as a sha256: digest"
    assert want in out, f"conventions rule 6 passed a pin on the pull request's own commit: {out}"


@pytest.mark.parametrize(
    ("quiet", "why"),
    [
        ("held.md", "a pin on a commit the base holds"),
        ("digest.md", "a digest of the file the pull request changed"),
        ("late.md", "a pin the base gained since, on a commit the base made since"),
        ("folded.md", "a squash merge on the base, which is not the pull request's commit"),
    ],
)
def test_rules_6_and_14_read_the_pull_request_and_not_what_the_base_gained(pull_request, quiet, why):
    k, base, head, _ = pull_request
    out = bash(CONVENTIONS, k, "--since", base, "--head", head).out
    assert quiet not in out, f"conventions script reported {quiet}, {why}: {out}"


def test_without_head_the_commits_after_the_base_are_read_up_to_the_checkout(pull_request):
    """On a branch the checkout is the pull request's last commit. On a gate's merge it also holds what the base gained, which is why the gate names the head."""
    k, base, _, _ = pull_request
    out = bash(CONVENTIONS, k, "--since", base).out
    for want in ["k/x/late.md: revision", "k/x/folded.md: commit"]:
        assert want in out, f"conventions script did not read up to HEAD with no --head ('{want}'): {out}"


def test_rule_6_is_asked_about_the_base_only_with_since(pull_request):
    k, _, _, _ = pull_request
    result = bash(CONVENTIONS, k)
    assert result, f"conventions script reported a pin on a commit in the history, with no base: {result.out}"


def test_rule_14_says_when_the_clone_lacks_the_head(pull_request):
    k, base, _, _ = pull_request
    result = bash(CONVENTIONS, k, "--since", base, "--head", "0123456789abcdef")
    assert not result, f"conventions rule 14 passed a head the clone does not hold: {result.out}"
    assert "rule 14: the head commit 0123456789abcdef is not in this clone's history" in result.out, (
        f"conventions rule 14 failed some other way on an unknown head: {result.out}"
    )


def test_rule_6_reports_a_pin_a_squash_merge_left_behind(tmp_path):
    """The commit is still in the clone that made it, on the branch, so asking git for the object passed there and failed in a fresh clone."""
    k = tmp_path / "k"
    git = Git(tmp_path)
    git.init()
    write(tmp_path / "docs" / "a.md", "a\n")
    v6c(k, "own", "docs/a.md")
    git("add", "-A")
    git("commit", "-q", "-m", "the base")
    git("checkout", "-q", "-b", "pr")
    write(tmp_path / "docs" / "a.md", "a, as the pull request changed it\n")
    git("commit", "-q", "-am", "the pull request changes a source")
    own = git("rev-parse", "HEAD")
    v6c(k, "own", "docs/a.md", confirmed_with(own))
    git("commit", "-q", "-am", "a person confirms")
    git("checkout", "-q", "main")
    git("merge", "-q", "--squash", "pr")
    git("commit", "-q", "-m", "the pull request, squash-merged")
    out = bash(CONVENTIONS, k).out
    want = f"k/x/own.md: revision {own} is not in the history of HEAD - a squash merge or a rebase has replaced that commit, or another branch holds it"
    assert want in out, f"conventions rule 6 passed a pin on a commit the history does not hold: {out}"


# Rule 17. Each Added and Deprecation bullet names a concept the bundle holds,
# by its first link or by starting with a concept's title. Two days of claims
# are committed after a base: `--since` reads both days, and no base reads
# the newest day only, where the latest run's claims sit. An old claim nobody
# can check sits in the base commit, out of both scopes.


@pytest.fixture(scope="module")
def rule17(tmp_path_factory):
    """A bundle whose newest day claims two writes nothing backs, and the base commit before that day."""
    v17 = tmp_path_factory.mktemp("conventions-rule17")
    k = v17 / "k"
    git = Git(v17)
    git.init()
    concepts = [("orders-api", "Orders API", ""), ("build", "Build, preview and edit the website", ""), ("legacy", "Legacy Sync", "status: deprecated\n")]
    for name, title, more in concepts:
        write(
            k / "x" / f"{name}.md",
            f"---\ntype: Service\nid: https://example.invalid/k/x/{name}\ntitle: {title}\nresource: https://example.invalid/src/{name}\n{more}---\n",
        )
    old = "\n## 2026-09-01\n\n* **Added**: An old claim nobody checks, from `nowhere.md`.\n"
    write(k / "log.md", "# Change Log\n" + old)
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    write(
        k / "log.md",
        "# Change Log\n\n## 2026-09-03\n\n"
        "* **Added**: Nothing of the kind, from `nowhere.md`.\n"
        "* **Deprecation**: [Gone](../x/gone.md) retired - replaced by [Orders API](../x/orders-api.md).\n"
        "* **Deprecation**: [Legacy Sync](../x/legacy.md) retired - replaced by [Orders API](../x/orders-api.md).\n"
        "* **Added**: Build, preview and edit the website, from `website/README.md`.\n"
        "* **Added**: [Orders API](./x/orders-api.md), from\n  `services/orders/openapi.yaml`.\n"
        "* **Added**: Orders API, from `services/orders/openapi.yaml`.\n"
        "* **Removal**: Short lived.\n"
        "* **Removal**: [Briefly](../x/briefly.md) deleted with its source.\n"
        "* **Added**: Gone today, from `c.md`.\n"
        "* **Removal**: Gone today.\n"
        "\n## 2026-09-02\n\n"
        "* **Added**: Short lived, from `a.md`.\n"
        "* **Added**: [Briefly](../x/briefly.md), from `b.md`.\n"
        "* **Added**: Yesterday's slip, from `d.md`.\n" + old,
    )
    git("commit", "-q", "-am", "two days of logged writes")
    return k, base


def rule17_out(rule17, since):
    k, base = rule17
    return bash(CONVENTIONS, k, *(["--since", base] if since else [])).out


R17_REPORTED = [
    "log.md: Added bullet under 2026-09-03 names no concept the bundle holds: Nothing of the kind",
    re.compile(r"log\.md: Deprecation bullet under 2026-09-03 links .*k/x/gone\.md, which the bundle lacks"),
]
R17_ACCEPTED = [
    ("An old claim", "an Added bullet under a day older than the newest, and older than the base"),
    ("Build, preview", "an Added bullet naming a concept by a title with a comma in it"),
    ("Orders API", "an Added bullet linking the concept across a wrapped line, and one naming it by title"),
    ("Legacy Sync", "a Deprecation bullet linking a retired concept the bundle still holds"),
    ("Short lived", "an Added bullet excused by a Removal under a newer day"),
    ("Briefly", "a linked Added bullet excused by a Removal that links the same path"),
    ("Gone today", "an Added bullet excused by a Removal under the same day"),
]


@pytest.mark.parametrize("since", [True, False], ids=["since-base", "newest-day"])
@pytest.mark.parametrize("want", R17_REPORTED, ids=lambda w: w.pattern if isinstance(w, re.Pattern) else w)
def test_rule_17_reports_a_logged_write_nothing_backs(rule17, since, want):
    out = rule17_out(rule17, since)
    found = want.search(out) if isinstance(want, re.Pattern) else want in out
    assert found, f"conventions rule 17 did not report '{want}': {out}"


@pytest.mark.parametrize("since", [True, False], ids=["since-base", "newest-day"])
@pytest.mark.parametrize(("quiet", "why"), R17_ACCEPTED, ids=[q for q, _ in R17_ACCEPTED])
def test_rule_17_accepts(rule17, since, quiet, why):
    out = rule17_out(rule17, since)
    assert quiet not in out, f"conventions rule 17 reported {quiet}, {why}: {out}"


def test_rule_17_reads_an_older_day_only_since_a_base(rule17):
    """A slip under the day before the newest is new since the base, and out of scope without one."""
    assert "Yesterday's slip" in rule17_out(rule17, True), "conventions rule 17 missed a bullet the commits after the base added under an older day"
    assert "Yesterday's slip" not in rule17_out(rule17, False), "conventions rule 17 read past the newest day with no base"


# ---- what an audit of the gate found, 2026-11-12 -----------------------------


def bundle_of(tmp_path, concepts):
    k = tmp_path / "k"
    write(k / "log.md", "# Change Log\n\n## 2026-09-15\n\n* **A**: b.\n")
    for name, text in concepts.items():
        write(k / "x" / name, text)
    return k


STAMP = 'generated:\n  by: process:ktl-librarian\n  at: "2026-09-01T00:00:00Z"\n'


def test_rule_10_refuses_a_comment_line_among_the_events(tmp_path):
    """A line reader once took a comment in the first column for the end of the block, and never read the event below it."""
    events = 'verified:\n  - by: process:ktl-librarian\n    at: "2026-09-02T00:00:00Z"\n# a note\n  - by: process:x\n    at: "2026-09-03T00:00:00Z"\n'
    k = bundle_of(tmp_path, {"a.md": f"---\ntype: Service\nid: https://example.invalid/k/x/a\nresource: https://example.invalid/a\n{STAMP}{events}---\n"})
    result = bash(CONVENTIONS, k)
    assert result.rc == 1 and "a comment line inside verified at line" in result.out, result.out
    after = events.replace("# a note\n", "") + "# a note after the last event\n"
    k = bundle_of(tmp_path / "after", {"a.md": f"---\ntype: Service\nid: https://example.invalid/k/x/a\nresource: https://example.invalid/a\n{STAMP}{after}status: draft\n---\n"})
    result = bash(CONVENTIONS, k)
    assert result, f"a comment after the last event was refused: {result.out}"


def test_rule_5_takes_an_identifier_with_a_scheme_for_no_file(tmp_path):
    k = bundle_of(tmp_path, {"a.md": f'---\ntype: Reference\nid: https://example.invalid/k/x/a\nresource: urn:ietf:rfc:9110\nsources:\n  - resource: doi:10.1000/182\n  - resource: "urn:isbn:0451450523"\n{STAMP}---\n'})
    result = bash(CONVENTIONS, k)
    assert result, f"rule 5 looked for a file named by a urn or a doi: {result.out}"


def test_a_concept_that_is_a_dangling_link_is_reported_and_stops_no_other_rule(tmp_path):
    k = bundle_of(tmp_path, {"a.md": f"---\ntype: Service\nid: https://example.invalid/k/x/a\nresource: https://example.invalid/a\n{STAMP}---\n"})
    os.symlink("nowhere.md", k / "x" / "dangling.md")
    result = bash(CONVENTIONS, k)
    assert result.rc == 1 and "dangling.md" in result.out and "cannot open" not in result.out and "No such file" not in result.out, (
        f"a dangling link stopped the script before the rule that reports it: {result.out}"
    )


def test_rule_16_reads_one_resource_written_two_ways_as_one(tmp_path):
    def concept(name, resource):
        return (
            f"---\ntype: Service\nid: https://example.invalid/k/x/{name}\nresource: https://example.invalid/{name}\n"
            f"sources:\n  - resource: {resource}\n    id: a.md\n{STAMP}---\n\nA claim.[^a.md]\n\n[^a.md]: {resource}, the first line\n"
        )

    root = tmp_path
    write(root / "docs" / "a.md", "a\n")
    k = bundle_of(root, {"one.md": concept("one", "docs/a.md"), "two.md": concept("two", "./docs/a.md")})
    result = bash(CONVENTIONS, k)
    assert "names more than one resource" not in result.out, f"rule 16 read ./docs/a.md and docs/a.md as two resources: {result.out}"


@pytest.mark.parametrize(
    ("spelling", "what"),
    [
        ("sources: [{resource: docs/gone.md}]\n", "a flow form inside sources"),
        ("sources:\n  - {resource: docs/gone.md}\n", "a flow form inside sources"),
        ("exclusions:\n  - {resource: docs/gone.md, reason: old}\n", "a flow form inside exclusions"),
        ("resource: >-\n  docs/gone.md\n", "a block scalar for resource"),
        ("resource:\n  docs/gone.md\n", "a resource on the line below its key"),
    ],
)
def test_rule_10_holds_resource_and_the_lists_that_carry_one_to_a_line_readers_spelling(tmp_path, spelling, what):
    """A line reader saw no `resource:` in a flow form: a gone source failed no rule 5, never moved, and counted for no file."""
    own = "" if spelling.startswith("resource") else "resource: https://example.invalid/a\n"
    k = bundle_of(tmp_path, {"a.md": f"---\ntype: Service\nid: https://example.invalid/k/x/a\n{own}{spelling}{STAMP}---\n"})
    result = bash(CONVENTIONS, k)
    assert result.rc == 1 and f"frontmatter uses {what}" in result.out, f"rule 10 passed {spelling!r}: {result.out}"


def test_rule_10_lets_a_comment_stand_beside_a_resource(tmp_path):
    """Every line reader cuts a comment from a resource, as it cuts a fragment."""
    k = bundle_of(tmp_path, {"a.md": f"---\ntype: Service\nid: https://example.invalid/k/x/a\nresource: https://example.invalid/a  # the page\n{STAMP}---\n"})
    result = bash(CONVENTIONS, k)
    assert result, f"rule 10 refused a comment beside a resource: {result.out}"


def test_rules_6_and_11_read_an_event_written_as_a_flow_mapping(tmp_path):
    """Rule 11 read `at:` only at the start of a line, so a flow event passed with a time ahead of its commit, and rule 6 never checked its revision."""
    git = Git(tmp_path)
    git.init()
    write(tmp_path / "docs" / "a.md", "a\n")
    flow = (
        "---\ntype: Service\nid: https://example.invalid/k/x/{n}\nresource: docs/a.md\n"
        'generated: {{ by: process:ktl-librarian, at: "2026-09-01T00:00:00Z" }}\n'
        "verified:\n  - {{ by: human:ada, at: {at}, revision: {rev} }}\n---\n"
    )
    k = bundle_of(tmp_path, {"late.md": flow.format(n="late", at='"2031-01-01T00:00:00Z"', rev="0" * 40)})
    write(k / "x" / "single.md", flow.format(n="single", at="'2031-02-01T00:00:00Z'", rev="1" * 40).replace("verified:\n  - ", "verified: [").replace(" }\n---", " }]\n---"))
    git("add", "-A")
    git("commit", "-q", "-m", "stamp", env={"GIT_COMMITTER_DATE": "2026-09-17T00:00:00Z"})
    out = bash(CONVENTIONS, k).out
    for want in [
        'late.md: at "2031-01-01T00:00:00Z" is later than the commit that recorded it (2026-09-17T00:00:00Z)',
        'single.md: at "2031-02-01T00:00:00Z" is later than the commit that recorded it',
        f"late.md: revision {'0' * 40} does not hold docs/a.md",
        f"single.md: revision {'1' * 40} does not hold docs/a.md",
    ]:
        assert want in out, f"conventions script missed '{want}' in a flow event:\n{out}"


def test_rule_11_finds_the_commit_of_a_path_git_quotes_or_ends_with_a_tab(tmp_path):
    """The one walk took a path from its diff header as printed, so a folder with a space or a name git quotes lost the commit, and a time between it and now passed."""
    git = Git(tmp_path)
    git.init()
    late = '---\ntype: Service\nid: https://example.invalid/k/x/{n}\nresource: https://example.invalid/a\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-09-18T00:00:00Z"\n---\n'
    k = bundle_of(tmp_path / "my docs", {"late.md": late.format(n="late"), 'q"t.md': late.format(n="q")})
    git("add", "-A")
    git("commit", "-q", "-m", "stamp", env={"GIT_COMMITTER_DATE": "2026-09-17T00:00:00Z"})
    out = bash(CONVENTIONS, k).out
    for name in ("late.md", 'q"t.md'):
        want = f'{name}: at "2026-09-18T00:00:00Z" is later than the commit that recorded it (2026-09-17T00:00:00Z)'
        assert want in out, f"conventions script missed '{want}':\n{out}"


def test_a_larger_bundle_asks_git_no_more_often(tmp_path):
    """The shell half once started about 24 processes a concept, a `git log -p` among them: 63 seconds at 2,000 concepts."""
    calls = []
    for n in (3, 12):
        root = tmp_path / str(n)
        root.mkdir()
        git = Git(root)
        git.init()
        write(root / "docs" / "a.md", "a\n")
        git("add", "-A")
        git("commit", "-q", "-m", "docs")
        head = git("rev-parse", "HEAD")
        k = bundle_of(root, {f"c{i}.md": f"---\ntype: Service\nid: https://example.invalid/k/x/c{i}\nresource: docs/a.md\n{STAMP}verified:\n  - by: human:ada\n    at: \"2026-09-02T00:00:00Z\"\n    revision: {head}\n---\n" for i in range(n)})
        git("add", "-A")
        git("commit", "-q", "-m", "concepts", env={"GIT_COMMITTER_DATE": "2026-09-17T00:00:00Z"})
        shim = tmp_path / f"shim{n}"
        real = shutil.which("git")
        write(shim / "git", f'#!/bin/sh\necho git >> "{shim}/calls"\nexec "{real}" "$@"\n')
        (shim / "git").chmod(0o755)
        result = bash(CONVENTIONS, k, env={"PATH": f"{shim}{os.pathsep}/usr/bin:/bin"})
        assert "not checked" in result.out or result, result.out
        calls.append(read(shim / "calls").count("\n"))
    assert calls[0] == calls[1], f"the shell half ran git {calls[0]} times for 3 concepts and {calls[1]} for 12"


# ---- what an audit of the gate found, 2026-11-17 -----------------------------

ADA_AT = "2026-09-02T00:00:00Z"


def confirmed_by_ada(name, body, more="", ident=None):
    ident = ident or f"https://example.invalid/k/x/{name}"
    return (
        f"---\ntype: Service\nid: {ident}\ntitle: {name}\nresource: https://example.invalid/src/{name}\n{STAMP}"
        f'verified:\n  - by: human:ada\n    at: "{ADA_AT}"\n{more}---\n\n# Overview\n\n{body}\n'
    )


@pytest.fixture
def confirmed_repo(tmp_path):
    """A bundle in git with one concept human:ada confirmed, and the base commit before a change."""
    git = Git(tmp_path)
    git.init()
    k = bundle_of(tmp_path, {"a.md": confirmed_by_ada("a", "What ada read.")})
    git("add", "-A")
    git("commit", "-q", "-m", "ada confirms", env={"GIT_COMMITTER_DATE": "2026-09-17T00:00:00Z"})
    return k, git, git("rev-parse", "HEAD").strip()


def test_rule_13_is_not_misled_by_the_time_of_the_confirmation_repeated_in_an_edit(confirmed_repo):
    """`git log -S` names the edit as the newest commit that changed how often the time occurs, and the edit is not the confirmation."""
    k, git, base = confirmed_repo
    write(k / "x" / "a.md", confirmed_by_ada("a", f"What nobody read.\n\n<!-- {ADA_AT} -->"))
    git("commit", "-q", "-am", "an edit that repeats the time", env={"GIT_COMMITTER_DATE": "2026-09-18T00:00:00Z"})
    result = bash(CONVENTIONS, k, "--since", base)
    assert result.rc == 1 and "a.md: changed since human:ada confirmed it" in result.out, result.out


def test_rule_13_still_passes_the_text_the_person_saw(confirmed_repo):
    k, git, base = confirmed_repo
    write(k / "x" / "b.md", f"---\ntype: Service\nid: https://example.invalid/k/x/b\nresource: https://example.invalid/b\n{STAMP}---\n")
    git("add", "-A")
    git("commit", "-q", "-m", "another concept", env={"GIT_COMMITTER_DATE": "2026-09-18T00:00:00Z"})
    result = bash(CONVENTIONS, k, "--since", base)
    assert result, result.out


def test_rule_14_passes_a_confirmed_concept_that_is_renamed(confirmed_repo):
    """A rename claims nothing: the concept keeps its id, its events and its text."""
    k, git, base = confirmed_repo
    git("mv", str(k / "x" / "a.md"), str(k / "x" / "renamed.md"))
    git("commit", "-q", "-m", "renamed", env={"GIT_COMMITTER_DATE": "2026-09-18T00:00:00Z"})
    result = bash(CONVENTIONS, k, "--since", base)
    assert result, f"a rename alone was refused: {result.out}"


def test_a_confirmed_concept_renamed_and_rewritten_is_reported(confirmed_repo):
    """Rule 13 follows the concept to the path it was confirmed under, by its id."""
    k, git, base = confirmed_repo
    (k / "x" / "a.md").unlink()
    write(k / "x" / "renamed.md", confirmed_by_ada("renamed", "What nobody read.", ident="https://example.invalid/k/x/a"))
    git("add", "-A")
    git("commit", "-q", "-m", "renamed and rewritten", env={"GIT_COMMITTER_DATE": "2026-09-18T00:00:00Z"})
    result = bash(CONVENTIONS, k, "--since", base)
    assert result.rc == 1 and "renamed.md: changed since human:ada confirmed it" in result.out, result.out


def test_a_confirmed_concept_renamed_under_a_new_id_and_rewritten_is_reported(confirmed_repo):
    """With another id it is a new concept, and the commit that adds it records a confirmation with text of its own."""
    k, git, base = confirmed_repo
    (k / "x" / "a.md").unlink()
    write(k / "x" / "renamed.md", confirmed_by_ada("renamed", "What nobody read."))
    git("add", "-A")
    git("commit", "-q", "-m", "renamed, re-identified and rewritten", env={"GIT_COMMITTER_DATE": "2026-09-18T00:00:00Z"})
    result = bash(CONVENTIONS, k, "--since", base)
    assert result.rc == 1 and "renamed.md: commit" in result.out and "records a confirmation by human:ada" in result.out, result.out


def test_diataxis_md_is_no_concept_at_the_root_of_the_bundle_alone(tmp_path):
    """The toolkit reads a file of that name in a folder below as a concept, so the rules read it too."""
    odd = "---\ntype: Service\nid: https://example.invalid/k/x/a\nverified:\n  - by: human:ada\n    at: 2026-09-02\n---\n"
    k = bundle_of(tmp_path, {"a.md": f"---\ntype: Service\nid: https://example.invalid/k/x/a\nresource: https://example.invalid/a\n{STAMP}---\n"})
    write(k / "diataxis.md", "# Map\n")
    result = bash(CONVENTIONS, k)
    assert result, f"the map at the root was read as a concept: {result.out}"
    write(k / "x" / "diataxis.md", odd)
    result = bash(CONVENTIONS, k)
    assert result.rc == 1 and "x/diataxis.md" in result.out and "is declared by more than one file" in result.out, result.out


def test_rule_10_refuses_a_key_the_gates_read_given_twice(tmp_path):
    """Parsers settle a repeated key in different ways, and the gates read the id as the key of every event."""
    k = bundle_of(tmp_path, {"a.md": f"---\ntype: Service\nid: https://example.invalid/k/x/a\nid: https://example.invalid/k/x/b\nresource: https://example.invalid/a\n{STAMP}---\n"})
    result = bash(CONVENTIONS, k)
    assert result.rc == 1 and "a second id key at line 4" in result.out, result.out


def test_the_shell_half_reads_a_diataxis_md_in_a_folder_as_a_concept(tmp_path):
    """Rule 5 is the shell half's: a missing resource in x/diataxis.md is a finding, and none in the root's map."""
    k = bundle_of(tmp_path, {"a.md": f"---\ntype: Service\nid: https://example.invalid/k/x/a\nresource: https://example.invalid/a\n{STAMP}---\n"})
    write(k / "diataxis.md", "---\nresource: docs/not-there.md\n---\n\n# Map\n")
    assert bash(CONVENTIONS, k), "the map at the root was read as a concept"
    write(k / "x" / "diataxis.md", f"---\ntype: Service\nid: https://example.invalid/k/x/diataxis\nresource: docs/not-there.md\n{STAMP}---\n")
    result = bash(CONVENTIONS, k)
    assert result.rc == 1 and "x/diataxis.md" in result.out and "docs/not-there.md" in result.out, result.out


def test_rule_5_finds_a_quoted_resource_with_a_comment_beside_it(tmp_path):
    k = bundle_of(tmp_path, {"a.md": f'---\ntype: Service\nid: https://example.invalid/k/x/a\nresource: "pinned.md" # the pin\n{STAMP}---\n'})
    write(tmp_path / "pinned.md", "pinned\n")
    result = bash(CONVENTIONS, k)
    assert result, f"a comment after a quoted resource was read as part of its path: {result.out}"


@pytest.mark.parametrize("spelling", ["verified: !!seq\n  - by: process:ktl-librarian\n    at: \"2026-09-02T00:00:00Z\"\n", "generated: !!map\n  by: process:ktl-librarian\n  at: \"2026-09-02T00:00:00Z\"\n"])
def test_rule_10_refuses_a_tag_on_a_list_or_a_mapping(tmp_path, spelling):
    k = bundle_of(tmp_path, {"a.md": f"---\ntype: Service\nid: https://example.invalid/k/x/a\nresource: https://example.invalid/a\n{spelling}---\n"})
    result = bash(CONVENTIONS, k)
    assert result.rc == 1 and "a tag (" in result.out and "on a collection" in result.out, result.out
