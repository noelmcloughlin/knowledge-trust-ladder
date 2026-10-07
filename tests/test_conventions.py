"""knowledge-conventions.sh reports each convention a bundle breaks, and accepts what a convention allows.

This was check 11's synthetic bundle, and check 11c, in
scripts/validate-repository.sh. A checker that cannot fail is not covering
anything, so one bundle breaks each rule and the script must name each break.
A bundle that keeps every rule must pass: with CRLF line endings, through a
link, and without uv. Rule 14 reads the commits after a pull request's base,
so a small history stages a confirmation alone, one with an edit, Correct now
and a merge.

Nine of the fourteen rules run through `uv run`, so without uv the script
reports none of them. These tests fail, rather than skip, when uv is missing:
the job that runs them installs it.
"""

from __future__ import annotations

import os
import re
import shutil

import pytest

from conftest import BOM, SCRIPTS, Git, bash, count_lines, have, matches, write

CONVENTIONS = SCRIPTS / "knowledge-conventions.sh"


@pytest.fixture(scope="module", autouse=True)
def _uv_is_needed():
    if not have("uv"):
        pytest.fail(
            "uv is not on PATH, so rules 2, 3, 4, 7, 9, 10, 12 and 13 cannot run - install uv, or add the setup-uv step to the workflow running this"
        )


def r13(x, name, title, description, generated_at, more, body):
    """A concept human:contract confirmed on 2026-09-02, for rule 13."""
    write(
        x / f"{name}.md",
        "---\ntype: Service\n"
        f"id: https://example.invalid/k/x/{name}\n"
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
    return f'---\ntype: Service\ngenerated:\n  by: process:ktl-librarian\n  at: "{at}"\n---\n'


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
    # past the confirmation, and one its person confirmed again.
    for n in ["r13-edited", "r13-description", "r13-notes", "r13-restamped", "r13-reconfirmed"]:
        r13(x, n, n, "what it was.", "2026-09-01T00:00:00Z", "", "The text a person confirmed.")
    git("add", *[f"k/x/{p.name}" for p in sorted(x.glob("r13-*.md"))])
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
    # A comment beside such a field is valid YAML that a parser drops and a
    # line reader takes for part of the value. A comment on a line of its own,
    # and a `#` inside a quoted value, must pass.
    write(
        x / "cm-comment.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/cm\nverified:\n  - by: human:contract\n    at: "2026-09-17T00:00:00Z" # checked on site\n---\n',
    )
    write(
        x / "co-comment-apart.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/co\nverified:\n  # a comment on a line of its own\n  - by: human:contract\n    at: "2026-09-17T00:00:00Z"\n    revision: "etag#1"\n---\n',
    )
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
        '---\ntype: Service\nid: https://example.invalid/k/x/fence\nverified:\n  - by: process:ktl-librarian\n    at: "2026-09-14T00:00:00Z"\n---\n\n```yaml\nverified:\n  - by: process:ktl-librarian\n    at: "2026-09-15T00:00:00Z"\n```\n',
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
        "---\ntype: Service\nid: https://example.invalid/k/x/fresh\ntitle: Fresh\ndescription: >-\n  folded, and\n  still equal.\n---\n",
    )
    write(
        x / "idx-shared.md",
        "---\ntype: Service\nid: https://example.invalid/k/x/shared\ntitle: Shared\ndescription: listed only beside another.\n---\n",
    )
    write(
        k / "index.md",
        "# K\n\n* [Stale](x/idx-stale.md) - what the concept said before.\n* [Fresh](x/idx-fresh.md) - folded, and still equal.\n* [Fresh](x/idx-fresh.md), [Shared](x/idx-shared.md) - a line that lists two.\n",
    )
    write(
        x / "index.md",
        "# X\n\n* [Stale, renamed](idx-stale.md) - what the concept says now.\n* [Fresh](idx-fresh.md) - folded, and still equal.\n",
    )
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
    "t-tag.md: frontmatter uses a tag on",
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
]


@pytest.mark.parametrize(("quiet", "why"), ACCEPTED, ids=[q for q, _ in ACCEPTED])
def test_accepts_what_a_rule_allows(findings, quiet, why):
    assert quiet not in findings, f"conventions script reported {quiet}, {why}:\n{findings}"


def test_reports_a_parse_error_on_one_line(findings):
    assert count_lines(findings, "y-bad.md") == 1, "conventions script spread a YAML parse error over several lines"


@pytest.fixture
def good(tmp_path):
    """A bundle that keeps every convention, checked out with CRLF line endings."""
    k = tmp_path / "k"
    write(
        k / "log.md", "# Change Log\r\n\r\n## 2026-09-15\r\n\r\n* **A**: b.\r\n\r\n## 2026-09-14\r\n\r\n* **C**: d.\r\n"
    )
    write(
        k / "x" / "a.md",
        '---\r\ntype: Service\r\nid: https://example.invalid/k/x/a\r\ndescription: >-\r\n  folded, which the gates\r\n  never read\r\nverified:\r\n  - by: process:ktl-librarian\r\n    at: "2026-09-14T00:00:00Z"\r\n---\r\n\r\n## Open questions\r\n\r\n- 2026-09-14, process:ktl-librarian: fine\r\n',
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
        result.out, r"^OK - .*\(rules 2, 3, 4, 7, 9, 10, 12 and 13 not checked: uv not found\)"
    ), f"conventions script without uv did not say what it skipped: {result.out}"


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
        f"---\ntype: Service\nid: https://example.invalid/k/x/{name}\ntitle: {name}\n"
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
