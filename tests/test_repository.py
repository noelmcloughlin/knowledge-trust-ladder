"""Tests of this repository's own scripts and workflows, the ones no skill installs.

1. scripts/smoke-test-install.sh fails when the install leaves installer
   metadata in this source repository, though .gitignore ignores all three
   paths, and passes when the metadata was there before it ran;
2. publish.yml runs the contract and the tests in a job that holds a
   read-only token, and the job that holds the write token needs it and runs
   neither;
3. that job publishes only while main is still the commit the run checked,
   reads the tag back, and asks for nothing built from a tag on another
   commit;
4. the jobs that run the contract set up the tools its checks need;
5. the contract fails under CI when a tool one of its checks needs is
   missing, and skips that check with a notice anywhere else;
6. semantic-release.yml's `plan` job counts a commit as releasing when the
   pinned commit-analyzer does, a `perf:` commit and a revert among them,
   and the pages that list the releasing types list the same ones;
7. each skill's frontmatter is YAML an installer can read, with a name and
   a description inside the Agent Skills limits.
"""

from __future__ import annotations

import os
import shutil

import pytest
import yaml

from conftest import REPO, Git, read, run, write

SMOKE = REPO / "scripts" / "smoke-test-install.sh"
CONTRACT = REPO / "scripts" / "validate-repository.sh"
PUBLISH = REPO / ".github" / "workflows" / "publish.yml"
SEMANTIC = REPO / ".github" / "workflows" / "semantic-release.yml"
VALIDATE = REPO / ".github" / "workflows" / "validate.yml"

# A stand-in for npx: `skills add` writes .agents/ into the source repository
# when LEAK is set, as a misbehaving installer would.
FAKE_NPX = """#!/usr/bin/env bash
if [ -n "${LEAK:-}" ]; then mkdir -p "$LEAK/.agents/skills/x"; : > "$LEAK/.agents/skills/x/SKILL.md"; fi
exit 0
"""


@pytest.fixture
def source(tmp_path):
    """A source repository with the real script and .gitignore, an ignored .claude/ already in it, and a fake npx on PATH."""
    repo = tmp_path / "source"
    write(repo / "scripts" / "smoke-test-install.sh", read(SMOKE))
    write(repo / ".gitignore", read(REPO / ".gitignore"))
    write(repo / ".claude" / "settings.local.json", "{}\n")
    git = Git(repo)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    bin_dir = tmp_path / "bin"
    write(bin_dir / "npx", FAKE_NPX)
    (bin_dir / "npx").chmod(0o755)
    return repo, bin_dir


def smoke(repo, bin_dir, leak):
    env = {"PATH": f"{bin_dir}:/usr/bin:/bin"}
    if leak:
        env["LEAK"] = str(repo)
    return run(["bash", repo / "scripts" / "smoke-test-install.sh", repo], env=env)


@pytest.mark.skipif(not shutil.which("git"), reason="git is not installed")
def test_the_smoke_tests_leak_check_sees_an_ignored_path_and_only_a_new_one(source):
    repo, bin_dir = source
    clean = smoke(repo, bin_dir, leak=False)
    assert "OK:   no installer metadata leaked back into this source repo" in clean.out, clean.out
    leaked = smoke(repo, bin_dir, leak=True)
    assert "FAIL: no installer metadata leaked back into this source repo" in leaked.out, leaked.out


def runs(job):
    return "\n".join(str(step.get("run", "")) for step in job["steps"])


def test_the_release_runs_its_checks_under_a_read_only_token():
    jobs = yaml.safe_load(read(PUBLISH))["jobs"]
    verify, publish = jobs["verify"], jobs["publish"]
    assert verify["permissions"] == {"contents": "read"}, verify["permissions"]
    assert publish["needs"] == "verify" and publish["environment"] == "release", publish
    for check in ("bash scripts/validate-repository.sh", "pytest"):
        assert check in runs(verify), f"verify does not run {check}"
        assert check not in runs(publish), f"the job with the write token runs {check}"
    assert not any("setup-uv" in str(step.get("uses", "")) for step in publish["steps"]), "the job with the write token installs uv"


# 3. The release tags the commit it checked.


def step(job, name):
    return next(s for s in job["steps"] if s.get("name") == name)


def run_step(job, name, cwd, **env):
    """Run one step's script as a runner does: bash, stopping at the first failure."""
    return run(["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", step(job, name)["run"]], cwd=cwd, env=env)


@pytest.fixture
def release(tmp_path):
    """A remote, the clone a publish run checked out, and the commit it stands on, with a second clone to move main from."""
    origin = tmp_path / "origin.git"
    origin.mkdir()
    Git(origin)("init", "-q", "--bare")
    elsewhere = Git(tmp_path / "elsewhere")
    elsewhere.repo.mkdir()
    elsewhere.init()
    elsewhere("commit", "-q", "--allow-empty", "-m", "the commit the run checks")
    elsewhere("remote", "add", "origin", origin)
    elsewhere("push", "-q", "origin", "HEAD:main")
    checkout = tmp_path / "checkout"
    Git(tmp_path)("clone", "-q", origin, checkout)
    return yaml.safe_load(read(PUBLISH))["jobs"]["publish"], checkout, elsewhere, elsewhere("rev-parse", "HEAD")


@pytest.mark.skipif(not shutil.which("git"), reason="git is not installed")
def test_the_release_publishes_only_while_main_is_the_commit_it_checked(release):
    publish, checkout, elsewhere, checked = release
    name = "Check main is still the commit verify checked"
    assert run_step(publish, name, checkout, GITHUB_SHA=checked), "main has not moved, so the release goes ahead"
    elsewhere("commit", "-q", "--allow-empty", "-m", "a merge that arrived during the run")
    elsewhere("push", "-q", "origin", "HEAD:main")
    moved = run_step(publish, name, checkout, GITHUB_SHA=checked)
    assert moved.rc == 1, moved.out
    assert f"main is at {elsewhere('rev-parse', 'HEAD')}, and this run checked {checked}" in moved.out, moved.out
    assert "Run the Publish workflow again" in moved.out, moved.out
    empty = checkout.parent / "empty.git"
    empty.mkdir()
    Git(empty)("init", "-q", "--bare")
    Git(checkout)("remote", "set-url", "origin", empty)
    unread = run_step(publish, name, checkout, GITHUB_SHA=checked)
    assert unread.rc == 1 and "Could not read where main is" in unread.out, "a remote that gives no main publishes nothing"


@pytest.mark.skipif(not shutil.which("git"), reason="git is not installed")
def test_the_release_reads_the_tag_back_and_stops_at_one_on_another_commit(release):
    publish, checkout, elsewhere, checked = release
    name = "Check the tag names the commit verify checked"
    elsewhere("tag", "-a", "-m", "release", "v1.2.3")
    elsewhere("commit", "-q", "--allow-empty", "-m", "a merge between the check and the publish")
    elsewhere("tag", "v1.2.4")
    elsewhere("push", "-q", "origin", "HEAD:main", "v1.2.3", "v1.2.4")
    assert run_step(publish, name, checkout, GITHUB_SHA=checked, VERSION="v1.2.3"), "an annotated tag on the checked commit passes"
    other = run_step(publish, name, checkout, GITHUB_SHA=checked, VERSION="v1.2.4")
    assert other.rc == 1, other.out
    assert f"Tag v1.2.4 names {elsewhere('rev-parse', 'HEAD')}, and this run checked {checked}" in other.out, other.out
    assert not run_step(publish, name, checkout, GITHUB_SHA=checked, VERSION="v1.2.5"), "a tag the release did not make fails the step"


def test_the_release_checks_main_just_before_it_publishes_and_the_tag_just_after():
    steps = yaml.safe_load(read(PUBLISH))["jobs"]["publish"]["steps"]
    names = [s.get("name") for s in steps]
    at = next(n for n, s in enumerate(steps) if "gh skill publish --tag" in str(s.get("run", "")))
    assert names[at - 1] == "Check main is still the commit verify checked", names
    assert names[at + 1] == "Check the tag names the commit verify checked" and steps[at + 1]["id"] == "tagged", names
    assert "git ls-remote origin refs/heads/main" in steps[at - 1]["run"]
    after = steps[at + 2:]
    assert [s["name"] for s in after] == ["Attach the knowledge bundle", "Publish the ktl package", "Ask the siblings to sync"]
    for s in after:
        assert "steps.tagged.outcome == 'success'" in s["if"], f"{s['name']} runs for a tag on a commit no check ran on"


# 4. The jobs that run the contract have its tools.


def test_each_job_that_runs_the_contract_sets_up_node_and_uv_first():
    """shellcheck and zip come with the runner image; the contract fails
    under CI where either is missing (5)."""
    jobs = {
        "publish.yml verify": yaml.safe_load(read(PUBLISH))["jobs"]["verify"],
        "validate.yml validate-skills": yaml.safe_load(read(VALIDATE))["jobs"]["validate-skills"],
    }
    for name, job in jobs.items():
        uses = [str(s.get("uses", "")).split("@")[0] if "uses" in s else str(s.get("run", "")) for s in job["steps"]]
        contract = next(n for n, u in enumerate(uses) if "bash scripts/validate-repository.sh" in u)
        for action in ("astral-sh/setup-uv", "actions/setup-node"):
            assert action in uses[:contract], f"{name} runs the contract before {action}"


def test_the_release_runs_the_tests_as_validate_yml_does():
    verify = yaml.safe_load(read(PUBLISH))["jobs"]["verify"]
    tests = yaml.safe_load(read(VALIDATE))["jobs"]["test-scripts"]
    assert "-m pytest -n auto" in runs(verify), "one worker per CPU keeps the time main can move in short"
    assert "-m pytest -n auto" in runs(tests)
    assert step(verify, "Install just")["run"] == step(tests, "Install just")["run"]
    node = step(verify, "Use Node.js")
    assert node["uses"] == step(tests, "Use Node.js")["uses"]
    assert node["with"]["package-manager-cache"] is False, "a release restores no cache another job saved"


# 5. The contract and a missing tool.

HIDDEN = ("node", "shellcheck", "zip")


def path_without(folder, *tools):
    """A PATH of one folder that links to every command on this PATH but the named ones."""
    folder.mkdir()
    for source in os.environ["PATH"].split(os.pathsep):
        if not os.path.isdir(source):
            continue
        for name in os.listdir(source):
            link, target = folder / name, os.path.join(source, name)
            if name in tools or link.is_symlink() or not (os.path.isfile(target) and os.access(target, os.X_OK)):
                continue
            link.symlink_to(target)
    return str(folder)


@pytest.mark.skipif(not shutil.which("git"), reason="git is not installed")
def test_the_contract_fails_under_ci_when_a_tool_is_missing_and_skips_the_check_elsewhere(tmp_path):
    """Only the lines about the three tools are read: a shallow clone, or a
    machine with no network, fails other checks of the contract."""
    path = path_without(tmp_path / "bin", *HIDDEN)
    local = run(["bash", CONTRACT], env={"PATH": path}, unset=("CI",))
    ci = run(["bash", CONTRACT], env={"PATH": path, "CI": "true"})
    for tool in HIDDEN:
        assert f"\n{tool} is not installed here, so " in local.out, f"{tool}: no notice outside CI"
        assert f"FAIL: {tool} is not on PATH" not in local.out, f"{tool}: a missing tool fails a contributor's run"
        assert f"FAIL: {tool} is not on PATH, so " in ci.out, f"{tool}: a missing tool passes under CI"
    assert "OK:   knowledge-m365.sh builds ktl-docent-m365 from this repository's bundle" in local.out, "without zip the folder is still checked"
    assert ci.rc == 1 and ci.out.endswith("Repository contract: FAIL"), ci.out[-400:]


# 6. What the plan job counts as releasing.

REVERTS = "This reverts commit 0123abc."
# What @semantic-release/commit-analyzer 13.0.1 answers for each message under
# .releaserc.json, asked of the package installed from .release/package-lock.json.
RELEASING = [
    "feat: a",
    "fix(scope): a",
    "security(ci): a",
    "perf: a",
    "perf(report): a",
    "FEAT: a",
    "FIX: a",
    "chore!: a",
    "docs(x)!: a",
    "docs: a\n\nBREAKING CHANGE: b",
    "docs: a\n\nBREAKING-CHANGE: b",
    "docs: a\n\nbreaking change: b",
    f"revert: feat: a\n\n{REVERTS}",
    f'Revert "feat: a"\n\n{REVERTS}',
    f'Revert "docs: a"\n\n{REVERTS}',
    f'Revert "feat: a" (#12)\n\n{REVERTS}',
]
RELEASING_NOTHING = [
    "docs: a",
    "Fix: a",
    "feat:a",
    "revert: feat: a",
    'Revert "feat: a"',
    'Revert "feat: a" (#12)\n\nReverts owner/repo#12',
    f"revert(scope): feat: a\n\n{REVERTS}",
    "build(deps): a",
    "chore(deps): a\n\nfix: a line of the body, which is no subject",
    "refactor: a",
    "style: a",
    "test: a",
    "ci: a",
    "Fix the thing (#46)",
]


@pytest.fixture(scope="module")
def plan(tmp_path_factory):
    """The plan job, and a repository whose main holds one commit, to put a pull request's commits on."""
    job = yaml.safe_load(read(SEMANTIC))["jobs"]["plan"]
    git = Git(tmp_path_factory.mktemp("plan") / "repo")
    git.repo.mkdir()
    git.init()
    git("commit", "-q", "--allow-empty", "-m", "chore: base")
    return job, git, git("rev-parse", "HEAD")


def commits_release(plan, *messages):
    """The step's outputs for a pull request that holds these commits."""
    job, git, base = plan
    git("checkout", "-q", "-B", "work", base)
    for message in messages:
        git("commit", "-q", "--allow-empty", "--cleanup=verbatim", "-m", message)
    output = git.repo.parent / "github-output"
    write(output, "")
    done = run_step(job, "Read whether these commits would release", git.repo, BASE=base, HEAD_SHA=git("rev-parse", "HEAD"), GITHUB_OUTPUT=output, **job["env"])
    assert done, done.out
    return dict(line.split("=", 1) for line in read(output).splitlines())


def title_passes(plan, title, reverts="false"):
    job, git, _ = plan
    return run_step(job, "Refuse a title that would lose the release on a squash merge", git.repo, TITLE=title, REVERTS=reverts, **job["env"])


@pytest.mark.skipif(not shutil.which("git"), reason="git is not installed")
@pytest.mark.parametrize("message", RELEASING)
def test_the_plan_job_counts_a_commit_the_analyzer_releases(plan, message):
    found = commits_release(plan, "docs: an earlier commit", message)
    assert found["releases"] == "true", message
    assert found["reverts"] == ("true" if REVERTS in message else "false"), message


@pytest.mark.skipif(not shutil.which("git"), reason="git is not installed")
@pytest.mark.parametrize("message", RELEASING_NOTHING)
def test_the_plan_job_passes_over_a_commit_the_analyzer_releases_nothing_for(plan, message):
    assert commits_release(plan, message, "docs: a later commit") == {"releases": "false", "reverts": "false"}, message


@pytest.mark.skipif(not shutil.which("git"), reason="git is not installed")
def test_a_title_must_release_as_a_squash_merge_of_the_commits_would(plan):
    for title in ("feat: a (#1)", "fix(report): a", "perf: a", "security(ci): a", "docs!: a"):
        assert title_passes(plan, title), title
    for title in ("Fix the thing (#46)", "docs: a", "perf a", 'Revert "feat: a"', "revert: feat: a"):
        refused = title_passes(plan, title)
        assert refused.rc == 1 and "retitle the pull request" in refused.out, title
    for title in ('Revert "feat: a" (#12)', "revert: feat: a"):
        assert title_passes(plan, title, reverts="true"), "a squash merge keeps the sentence that names the reverted commit in its body"
    assert not title_passes(plan, "docs: undo a", reverts="true"), "a typed title over a revert releases nothing"


def test_the_pages_list_the_types_the_plan_job_releases():
    job = yaml.safe_load(read(SEMANTIC))["jobs"]["plan"]
    refusal = step(job, "Refuse a title that would lose the release on a squash merge")["run"]
    pages = {
        "semantic-release.yml's refusal": refusal,
        "CONTRIBUTING.md": read(REPO / "CONTRIBUTING.md"),
        "docs/releasing.md": read(REPO / "docs" / "releasing.md"),
        "the pull request template": read(REPO / ".github" / "pull_request_template.md"),
    }
    for name, text in pages.items():
        for word in ("feat:", "fix:", "perf:", "security:", "Revert"):
            assert word in text, f"{name} does not name {word}"


# 7. The frontmatter an installer reads.


@pytest.mark.parametrize("skill", sorted(p.parent.name for p in (REPO / "skills").glob("*/SKILL.md")))
def test_a_skills_frontmatter_parses_and_keeps_to_the_agent_skills_limits(skill):
    """The contract reads the fields with awk, which passes a quote YAML refuses; `gh skill publish` parses them."""
    text = read(REPO / "skills" / skill / "SKILL.md")
    assert text.startswith("---\n"), skill
    front = yaml.safe_load(text[4:].split("\n---\n", 1)[0])
    assert front["name"] == skill
    description = front["description"]
    assert isinstance(description, str) and 1 <= len(description) <= 1024, f"{skill}: {len(description)} characters"
    assert description.rstrip().endswith("."), "the description ends its Keywords list with a full stop"
    assert "Keywords: " in description, skill
    assert 1 <= len(front["compatibility"]) <= 500, skill
