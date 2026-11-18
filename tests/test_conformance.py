"""knowledge-report.sh reports what tests/conformance/reader/expected.json holds.

The bundle beside that file has one concept for each trust label a program
can compute from the files alone, and the expected values were worked out by
hand from section 8 of SPEC.md. A second program that reports trust, such as
the KTL Curator plugin, reads the same two things and must agree.

The bundle is copied out of this repository first, so git holds no history of
it and the labels that read git are left out.
"""

from __future__ import annotations

import json
import re
import shutil

import pytest

from conftest import REPO, SCRIPTS, bash

READER = REPO / "tests" / "conformance" / "reader"
REPORT = SCRIPTS / "knowledge-report.sh"

# The words of a label in a `labels` line, and its key in expected.json.
PHRASES = [
    ("confirmed by a person", "confirmed"),
    ("checked by automation only", "automation-only"),
    ("nobody has checked this yet", "unchecked"),
    ("still a draft", "draft"),
    ("reopened ", "reopened"),
    ("edited since a person last confirmed it", "edited-since"),
    ("past its review date", "past-review"),
    ("a reader disputed this", "disputed"),
    ("retired", "retired"),
]
HEALTH = {
    "confirmed": r"Confirmed by a person: (\d+) of \d+",
    "total": r"Confirmed by a person: \d+ of (\d+)",
    "automation_only": r"Checked by automation only: (\d+)",
    "unchecked": r"Nobody has checked: (\d+)",
    "drafts": r"Drafts: (\d+)",
    "reopened": r"Reopened: (\d+)",
    "past_review": r"Past review date: (\d+)",
    "edited_since": r"Edited since confirmed: (\d+)",
    "retired": r"Retired: (\d+)",
}


@pytest.fixture(scope="module")
def expected():
    return json.loads((READER / "expected.json").read_text())


@pytest.fixture(scope="module")
def whole(tmp_path_factory):
    root = tmp_path_factory.mktemp("reader")
    shutil.copytree(READER / ".lokf", root / ".lokf")
    result = bash(REPORT, cwd=root)
    assert result.rc == 0, result.out
    return result.out


def section(report, heading):
    """The `- ` lines under the line that starts with `heading`."""
    lines = report.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(heading))
    found = []
    for line in lines[start + 1:]:
        if not line.startswith("- "):
            break
        found.append(line[2:])
    return found


def concepts(report):
    """Each concept's title and label text, by path, from the Concepts section."""
    found = {}
    for line in section(report, "Concepts"):
        match = re.fullmatch(r"(.+) \(([^()]+\.md)\) - (.+)", line)
        assert match, line
        found[match.group(2)] = (match.group(1), match.group(3))
    return found


def test_the_health_line_counts_each_label_once(whole, expected):
    line = whole.splitlines()[1]
    counts = {key: int(re.search(pattern, line).group(1)) for key, pattern in HEALTH.items()}
    assert counts == expected["health"]


def test_each_concept_carries_its_labels_and_no_other(whole, expected):
    found = {
        path: [key for phrase, key in PHRASES if phrase in text]
        for path, (_, text) in concepts(whole).items()
    }
    assert found == expected["labels"]


def test_a_retired_concept_names_its_successor(whole, expected):
    found = {}
    for path, (_, text) in concepts(whole).items():
        match = re.search(r"retired, replaced by (\S+)", text)
        if match:
            found[path] = match.group(1)
    assert found == expected["successor"]


def test_each_citing_concept_counts_once_and_a_retired_one_never(whole, expected):
    found = {}
    for line in section(whole, "Relied on by other concepts"):
        path, count = re.fullmatch(r"(\S+) \((\d+)\)", line).groups()
        found[path] = int(count)
    assert found == expected["relied_on"]


def test_the_lists_beside_the_labels(whole, expected):
    derived = [line.split(":")[0] for line in section(whole, "Confirmed by a person, and derived from")]
    misfit = [line.split(":")[0] for line in section(whole, "Vocabulary fit")]
    questions = [line.split(" ")[0] for line in section(whole, "Open questions a person left")]
    assert derived == expected["derived_from_edited"]
    assert misfit == expected["vocabulary_misfit"]
    assert questions == expected["open_questions"]


def test_the_queue_is_in_the_order_section_8_2_gives(whole, expected):
    by_title = {title: path for path, (title, _) in concepts(whole).items()}
    lines = whole.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("Worth ten minutes today"))
    queue = []
    for line in lines[start + 1:]:
        match = re.match(r"\d+\. (.+?) \(\w+\) - ", line)
        if not match:
            break
        queue.append(by_title[match.group(1)])
    assert queue == expected["queue"]


def test_every_concept_of_the_bundle_is_expected(expected):
    paths = sorted(
        str(path.relative_to(READER / ".lokf" / "knowledge"))
        for path in (READER / ".lokf" / "knowledge").rglob("*.md")
        if path.name not in ("index.md", "log.md")
    )
    assert paths == sorted(expected["labels"])
