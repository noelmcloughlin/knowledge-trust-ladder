"""tests/docent-holdout.yaml names, for each captured docent question, a concept the bundle still holds, and evals/ asks the same questions.

docs/examples/docent.md captured eight questions the docent answered against
this repository's own bundle, with a table naming the concept each answer
should rest on today. tests/docent-holdout.yaml holds those pairs as data,
outside .lokf/ and the docent's search path, so the docent cannot read a
question beside its answer. evals/ holds the same holdout as `claude plugin
eval` cases, which docent-eval.yml runs weekly under a cost ceiling and no
pull request ever runs. None of the three is read from another, so these
tests hold them together, at no model call:

- the holdout's base_iri is the bundle's, every expected IRI starts with
  it, and the concept it names is a file under .lokf/knowledge/, so a
  concept that moves fails here as `lokf validate --check-refs` fails a
  relation that names it;
- each slug is unique, each question has text, each says whether all of
  its concepts belong in the answer or any one suffices, and the page's
  headings and table still carry the same questions and concepts;
- evals/ has one case per question and no other. Its prompt carries the
  question, a regex grader names each expected concept's path, and a
  tool_used grader requires the ktl-docent skill. No grader asks a judge, no
  case may run a shell, and each case's scaffold runs the one script that
  copies the bundle, and nothing else, into a run's empty directory;
- the holdout validates against tests/docent-holdout-schema.yaml with
  LinkML's validator from the sidecar's .lokf/.venv, when that environment
  holds linkml, from a directory where the schema sits beside the toolkit's
  pinned lokf.yaml, since LinkML resolves a relative import beside the
  importing file.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from conftest import REPO, read, run

HOLDOUT = REPO / "tests" / "docent-holdout.yaml"
SCHEMA = REPO / "tests" / "docent-holdout-schema.yaml"
PAGE = REPO / "docs" / "examples" / "docent.md"
BUNDLE = REPO / ".lokf" / "knowledge"
EVALS = REPO / "evals"
SHARED_SCAFFOLD = EVALS / "scaffold-bundle.sh"
VENV_PYTHON = REPO / ".lokf" / ".venv" / "bin" / "python"
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
CONCEPT_PATH = re.compile(r"^[a-z0-9][a-z0-9._-]*(/[a-z0-9][a-z0-9._-]*)*$")

HOLDOUT_DATA = yaml.safe_load(read(HOLDOUT))
QUESTIONS = HOLDOUT_DATA["questions"]
IDS = [q["id"] for q in QUESTIONS]


def split_frontmatter(text: str) -> tuple[dict, str]:
    """The YAML between the first two `---` lines, and the body after them."""
    assert text.startswith("---\n"), "no frontmatter"
    front, _, body = text[4:].partition("\n---\n")
    return yaml.safe_load(front) or {}, body


def concept_path(iri: str) -> str:
    """The bundle path a concept IRI names: the IRI without the base and without `.md`."""
    base = HOLDOUT_DATA["base_iri"]
    assert iri.startswith(base), f"{iri} is not under the bundle's base_iri {base}"
    path = iri[len(base):]
    assert CONCEPT_PATH.match(path), f"{iri} does not name a concept path"
    return path


def cases() -> list[Path]:
    """The case directories under evals/: those with a prompt.md or a case.yaml, as the harness counts them."""
    return sorted(d for d in EVALS.iterdir() if d.is_dir() and ((d / "prompt.md").is_file() or (d / "case.yaml").is_file()))


def linkml_in_venv() -> bool:
    return VENV_PYTHON.is_file() and run([VENV_PYTHON, "-c", "import linkml"]).rc == 0


def test_base_iri_is_the_bundles():
    index, _ = split_frontmatter(read(BUNDLE / "index.md"))
    assert HOLDOUT_DATA["base_iri"] == index["base_iri"]


def test_every_expected_concept_is_in_the_bundle():
    missing = []
    for q in QUESTIONS:
        for iri in q["expects"]:
            path = concept_path(iri)
            if not (BUNDLE / f"{path}.md").is_file():
                missing.append(f"{q['id']}: {iri} ({path}.md)")
    assert not missing, "the holdout expects concepts the bundle no longer holds:\n- " + "\n- ".join(missing)


def test_slugs_are_unique_and_questions_have_text():
    assert len(IDS) == len(set(IDS)), f"duplicate slugs: {sorted({i for i in IDS if IDS.count(i) > 1})}"
    for q in QUESTIONS:
        assert SLUG.match(q["id"]), f"{q['id']!r} is not a slug"
        assert q["question"].strip(), f"{q['id']} has no question text"
        assert q["expects"], f"{q['id']} expects no concept"
        assert isinstance(q["all_expected"], bool), f"{q['id']} does not say whether all of its concepts are expected"
        assert q["all_expected"] or len(q["expects"]) > 1, f"{q['id']} says any one concept suffices but names only one"


def test_page_carries_the_same_questions_and_concepts():
    """docs/examples/docent.md is the page a person reads; its headings and its table name what the holdout holds."""
    page = read(PAGE)
    rows = {int(m.group(1)): m.group(2) for m in re.finditer(r"^\| (\d+)\. [^|]*\| ([^\n]*)$", page, re.M)}
    for n, q in enumerate(QUESTIONS, 1):
        assert f'## {n}. "{q["question"]}"' in page.split("\n"), f"{q['id']}: the page has no heading {n} with this question"
        assert n in rows, f"the page's table has no row {n}"
        for iri in q["expects"]:
            assert f"(../../.lokf/knowledge/{concept_path(iri)}.md)" in rows[n], f"{q['id']}: row {n} of the page's table does not link {concept_path(iri)}.md"


def test_eval_suite_has_one_case_per_question():
    assert sorted(d.name for d in cases()) == sorted(IDS)


@pytest.mark.parametrize("q", QUESTIONS, ids=IDS)
def test_case_asks_the_question_and_grades_its_concepts(q):
    case = EVALS / q["id"]
    front, body = split_frontmatter(read(case / "prompt.md"))
    assert front.get("name", case.name) == q["id"]
    assert q["question"] in body, f"{case.name}/prompt.md does not carry the question"
    assert "ktl-docent" in body and ".lokf/knowledge" in body, f"{case.name}/prompt.md does not ask ktl-docent to answer from the bundle"
    tools = front.get("allowed_tools", [])
    assert "Skill" in tools, f"{case.name} cannot invoke a skill"
    assert not {"Bash", "PowerShell", "Write", "Edit"} & set(tools), f"{case.name} asks for a tool the holdout never grants: {tools}"
    assert front.get("runs") == 1, f"{case.name} runs more than once"
    meta = yaml.safe_load(read(case / "case.yaml"))
    assert meta["schema_version"] == "1.1" and meta["name"] == q["id"]
    script = meta["context"]["scaffold_script"]
    assert "/" not in script and (case / script).is_file(), f"{case.name}: scaffold_script {script!r} is not a file in the case directory"
    assert SHARED_SCAFFOLD.name in read(case / script), f"{case.name}/{script} does not run {SHARED_SCAFFOLD.name}"

    graders = {p.stem: split_frontmatter(read(p))[0] for p in sorted((case / "graders").glob("*.md"))}
    assert graders, f"{case.name} has no grader"
    types = {g["type"] for g in graders.values()}
    assert types <= {"regex", "tool_used"}, f"{case.name} has a grader that asks a judge or reads a file: {types}"
    assert any(
        g["type"] == "tool_used" and g.get("tool") == "Skill" and "ktl-docent" in str(g.get("input_match", "")) for g in graders.values()
    ), f"{case.name}: no tool_used grader requires the ktl-docent skill"
    patterns = [g["pattern"] for g in graders.values() if g["type"] == "regex"]
    paths = [concept_path(iri) for iri in q["expects"]]
    for pattern in patterns:
        assert any(re.search(pattern, path) and re.search(pattern, path + ".md") for path in paths), f"{case.name}: grader {pattern!r} names no expected concept"
    if q["all_expected"]:
        assert len(patterns) == len(paths), f"{case.name}: {len(paths)} concepts expected, {len(patterns)} regex graders"
        for path in paths:
            assert any(re.search(p, path) for p in patterns), f"{case.name}: no regex grader names {path}"
    else:
        assert len(patterns) == 1, f"{case.name}: any one concept suffices, so one grader holds the alternatives"
        assert all(re.search(patterns[0], path) for path in paths), f"{case.name}: grader {patterns[0]!r} does not name every alternative"


@pytest.mark.parametrize("case", [EVALS / i for i in IDS], ids=IDS)
def test_scaffold_copies_the_bundle_and_nothing_else(case, tmp_path):
    """Each case's scaffold, run as the harness runs it: as a file, in an empty directory, with a minimal environment."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (tmp_path / "home").mkdir()
    (tmp_path / "tmp").mkdir()
    script = case / yaml.safe_load(read(case / "case.yaml"))["context"]["scaffold_script"]
    env = {"PATH": os.environ["PATH"], "HOME": str(tmp_path / "home"), "TMPDIR": str(tmp_path / "tmp"), "TERM": "dumb"}
    done = subprocess.run(["bash", str(script)], cwd=workspace, env=env, capture_output=True, text=True, timeout=120)
    assert done.returncode == 0, done.stdout + done.stderr
    assert sorted(p.name for p in workspace.iterdir()) == [".lokf", "knowledge_bundle"], "the scaffold wrote more than the bundle and its link"
    assert [p.name for p in (workspace / ".lokf").iterdir()] == ["knowledge"], "the scaffold copied more of .lokf/ than the bundle"
    link = workspace / "knowledge_bundle"
    assert link.is_symlink() and os.readlink(link) == os.readlink(REPO / "knowledge_bundle")
    copied = {p.relative_to(workspace / ".lokf" / "knowledge") for p in (workspace / ".lokf" / "knowledge").rglob("*.md")}
    assert copied == {p.relative_to(BUNDLE) for p in BUNDLE.rglob("*.md") if ".obsidian" not in p.parts}
    for q in QUESTIONS:
        for iri in q["expects"]:
            assert (workspace / ".lokf" / "knowledge" / f"{concept_path(iri)}.md").is_file()
    again = subprocess.run(["bash", str(script)], cwd=workspace, env=env, capture_output=True, text=True, timeout=120)
    assert again.returncode != 0 and "not empty" in again.stderr, "a second run into the same directory should refuse"


def test_results_are_ignored():
    """What a run writes under evals/results/ never reaches a commit."""
    assert run(["git", "-C", REPO, "check-ignore", "-q", "evals/results/docent-eval.json"]).rc == 0


@pytest.mark.skipif(
    not linkml_in_venv(),
    reason=f"{VENV_PYTHON} cannot import linkml; `uv sync` in .lokf/ installs it through the toolkit's [build] extra",
)
def test_holdout_validates_against_the_schema(tmp_path):
    lokf_yaml = run([VENV_PYTHON, "-c", "from importlib.resources import files; print(files('lokf') / 'data' / 'lokf.yaml')"], stdout_only=True)
    assert lokf_yaml and Path(lokf_yaml.out).is_file(), f"the toolkit's lokf.yaml was not found: {lokf_yaml.out}"
    shutil.copy(SCHEMA, tmp_path / SCHEMA.name)
    shutil.copy(lokf_yaml.out, tmp_path / "lokf.yaml")
    result = run([VENV_PYTHON, "-c", "from linkml.validator.cli import cli; cli()", "-s", tmp_path / SCHEMA.name, "-C", "DocentHoldout", HOLDOUT])
    assert result.rc == 0 and "No issues found" in result.out, result.out
