"""The sidecar's sync script brings a host to one release, and the fan-out runs it in each sibling.

knowledge-sync.sh is the template every host carries as
.lokf/scripts/knowledge-sync.sh. These tests run it on a stand-in for the
skills repository, the real templates at two tags, and on a host at the
first tag, and pin what the script's header says:

1. it copies the templates the release changed, adds a template a file the
   host carries needs, reports one ktl-sidecar's Step 5 decides, moves the
   pin to the tag and the commit it names, and writes the changelog entry
   under "## [Unreleased]" and "### Security";
2. a host at the release has nothing to sync, and the entry is written once;
3. the entry joins a Security section the changelog already has, at its end,
   and a section is added last when there is none;
4. the host's justfile keeps its own first line and `schema :=` line;
5. --commit works on sync-<tag> from origin's default branch and leaves the
   default branch and the tree as they were, and a tree with uncommitted
   changes, a branch that exists, a tag that is not a release and a tag the
   source lacks are each refused;
6. without --source the host's copy clones the tag and hands over to the
   copy of itself there;
7. scripts/sync-sidecar.sh runs the tag's copy in each sibling, and its
   --finish keeps a branch that was never pushed, or whose remote branch
   still exists, and removes one whose pull request was merged.

Every run skips the sidecar's checks (--no-checks): the preflight, the
toolkit and the conventions script have modules of their own.
"""

from __future__ import annotations

import re
import shutil

import pytest

from conftest import REPO, SCRIPTS, TEMPLATES, WEBSITE_TEMPLATES, Git, has_line, matches, read, run, write

SYNC = SCRIPTS / "knowledge-sync.sh"
FANOUT = REPO / "scripts" / "sync-sidecar.sh"
LIBRARIAN = ".github/workflows/knowledge-librarian.yaml"
COPIES = {
    "scripts/knowledge-librarian.sh": ".lokf/scripts/knowledge-librarian.sh",
    "scripts/knowledge-conventions.sh": ".lokf/scripts/knowledge-conventions.sh",
    "scripts/knowledge-conventions.py": ".lokf/scripts/knowledge-conventions.py",
    "scripts/knowledge-preflight.sh": ".lokf/scripts/knowledge-preflight.sh",
    "scripts/knowledge-provenance.sh": ".lokf/scripts/knowledge-provenance.sh",
    "scripts/knowledge-feedback.sh": ".lokf/scripts/knowledge-feedback.sh",
    "scripts/knowledge-apply.sh": ".lokf/scripts/knowledge-apply.sh",
    "scripts/knowledge-apply.py": ".lokf/scripts/knowledge-apply.py",
    "scripts/knowledge-report.sh": ".lokf/scripts/knowledge-report.sh",
    "scripts/knowledge-sync.sh": ".lokf/scripts/knowledge-sync.sh",
    "m365/knowledge-m365.sh": ".lokf/m365/knowledge-m365.sh",
    "m365/ktl-docent-m365.md": ".lokf/m365/ktl-docent-m365.md",
    "gitattributes": ".lokf/.gitattributes",
    "github/knowledge-registrar.yaml": ".github/workflows/knowledge-registrar.yaml",
    "github/knowledge-librarian.yaml": LIBRARIAN,
    "github/knowledge-release.yaml": ".github/workflows/knowledge-release.yaml",
}
CHANGELOG = "# Changelog\n\n## [Unreleased]\n\n## [1.0.0] - 2026-01-01\n\n### Added\n\n- The thing.\n"
ENTRY_START = "- **The sidecar copies and the skills pin are at Knowledge Trust Ladder [v1.1.0]("
# Git reads the committer from these when no config names one, so no run looks
# the machine's name up to build one, which can wait on DNS for seconds.
IDENT = {
    "GIT_AUTHOR_NAME": "contract",
    "GIT_AUTHOR_EMAIL": "contract@example.invalid",
    "GIT_COMMITTER_NAME": "contract",
    "GIT_COMMITTER_EMAIL": "contract@example.invalid",
}


def bare(path):
    run(["git", "init", "-q", "--bare", path], env=IDENT)
    return path


@pytest.fixture
def skills(tmp_path):
    """The skills repository: the real templates at v1.0.0, then v1.1.0 changing three of them, with an origin that holds both."""
    repo = tmp_path / "skills"
    repo.mkdir()
    git = Git(repo)
    git.init()
    shutil.copytree(TEMPLATES, repo / "skills" / "ktl-sidecar" / "templates", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(WEBSITE_TEMPLATES, repo / "skills" / "ktl-website" / "templates")
    write(repo / "skills" / "ktl-librarian" / "SKILL.md", "# skill\n")
    git("add", "-A")
    git("commit", "-qm", "v1.0.0")
    git("tag", "v1.0.0")
    templates = repo / "skills" / "ktl-sidecar" / "templates"
    with (templates / "scripts" / "knowledge-report.sh").open("a") as f:
        f.write("\n# a line the next release adds\n")
    with (templates / "scripts" / "knowledge-sync.sh").open("a") as f:
        f.write("\n# a line the next release adds to the sync script\n")
    with (templates / "justfile").open("a") as f:
        f.write("\n# a recipe comment the next release adds\n")
    git("add", "-A")
    git("commit", "-qm", "v1.1.0")
    git("tag", "v1.1.0")
    git("remote", "add", "origin", str(bare(tmp_path / "skills-origin.git")))
    git("push", "-q", "origin", "main", "--tags")
    return repo


def make_host(tmp_path, skills, name="host", changelog=CHANGELOG):
    """A host at v1.0.0: the copies, a titled justfile with its own schema line, the pin, a changelog and an origin."""
    host = tmp_path / name
    host.mkdir()
    git = Git(host)
    git.init()
    src = Git(skills)
    for template, copy in COPIES.items():
        write(host / copy, src("show", f"v1.0.0:skills/ktl-sidecar/templates/{template}") + "\n")
        if copy.endswith((".sh", ".py")):
            (host / copy).chmod(0o755)
    justfile = src("show", "v1.0.0:skills/ktl-sidecar/templates/justfile").split("\n")[1:]
    justfile = [line if not line.startswith("schema := ") else 'schema := "acme.yaml"' for line in justfile]
    write(host / ".lokf" / "justfile", "# LOKF knowledge-bundle recipes for Acme.\n" + "\n".join(justfile) + "\n")
    sha = src("rev-parse", "v1.0.0^{commit}")
    librarian = re.sub(r"TRUST_LADDER_SKILLS_REF: v[0-9]+\.[0-9]+\.[0-9]+", "TRUST_LADDER_SKILLS_REF: v1.0.0", read(host / LIBRARIAN))
    librarian = re.sub(r"TRUST_LADDER_SKILLS_SHA: [0-9a-f]{40}", f"TRUST_LADDER_SKILLS_SHA: {sha}", librarian)
    write(host / LIBRARIAN, librarian)
    write(host / "CHANGELOG.md", changelog)
    write(host / ".lokf" / "knowledge" / "index.md", "# Acme\n")
    git("add", "-A")
    git("commit", "-qm", "host at v1.0.0")
    git("remote", "add", "origin", str(bare(tmp_path / f"{name}-origin.git")))
    git("push", "-q", "-u", "origin", "main")
    return host


def sync(host, skills, *args, cwd=None):
    return run(["bash", SYNC, "--source", skills, "--host", host, "--no-checks", *args, "v1.1.0"], cwd=cwd or host, env=IDENT)


def test_a_sync_copies_adds_reports_pins_and_writes_the_entry(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    changed = tmp_path / "changed.txt"
    report = tmp_path / "report.md"
    result = sync(host, skills, "--changed", changed, "--report", report)
    checks.ok(result.rc == 0, "exit 0", result.out)
    out = result.out
    checks.ok(has_line(out, "   copied   .lokf/scripts/knowledge-report.sh"), "the changed template is copied", out)
    checks.ok(has_line(out, "   copied   .lokf/scripts/knowledge-sync.sh"), "the sync script's own copy is copied", out)
    checks.ok(matches(out, r"^   added    \.github/workflows/knowledge-sync\.yaml \(\.github/workflows/knowledge-librarian\.yaml pins"), "the sync workflow is added beside a pinned librarian", out)
    checks.ok(matches(out, r"^   added    \.github/PULL_REQUEST_TEMPLATE/knowledge-sync\.md \(\.github/workflows/knowledge-sync\.yaml opens"), "the pull request template is added beside the workflow", out)
    checks.ok(matches(out, r"^   absent   \.lokf/domain\.yaml \(never installed here"), "a domain host's file is reported, not added", out)
    checks.ok(has_line(out, "   same     .github/workflows/knowledge-registrar.yaml"), "an unchanged copy is left alone", out)
    sha = Git(skills)("rev-parse", "v1.1.0^{commit}")
    checks.ok(has_line(out, f"   pin      v1.0.0 to v1.1.0 ({sha})"), "the pin moves to the tag and its commit", out)
    librarian = read(host / LIBRARIAN)
    checks.ok("TRUST_LADDER_SKILLS_REF: v1.1.0" in librarian and f"TRUST_LADDER_SKILLS_SHA: {sha}" in librarian, "both pin lines are written")
    checks.ok("a line the next release adds" in read(host / ".lokf" / "scripts" / "knowledge-report.sh"), "the copy carries the release's bytes")
    changelog = read(host / "CHANGELOG.md")
    checks.ok("## [Unreleased]\n\n### Security\n\n" + ENTRY_START in changelog, "the entry sits under Unreleased and Security", changelog)
    checks.ok("compare/v1.0.0...v1.1.0" in changelog, "the entry links the comparison between the two pins", changelog)
    checks.ok("`.lokf/scripts/knowledge-report.sh`" in changelog and "No plugin change" not in changelog, "the entry names the files and says nothing of a plugin", changelog)
    listed = read(changed).split("\n")
    checks.ok(len(listed) == len(set(listed)), "each changed path is listed once", str(listed))
    for path in (".lokf/scripts/knowledge-report.sh", ".github/workflows/knowledge-sync.yaml", LIBRARIAN, "CHANGELOG.md"):
        checks.ok(path in listed, f"{path} is listed as changed", str(listed))
    body = read(report)
    checks.ok(body.startswith("Brings the sidecar copies and the skills pin of this repository to Knowledge Trust Ladder [v1.1.0]("), "the report opens with the release", body)
    checks.ok("- `.lokf/scripts/knowledge-report.sh`" in body and "skipped (--no-checks)" in body, "the report lists the copies and the checks", body)
    checks.ok(matches(out, r"^   git commit -m \"security\(sidecar\): sync copies and skills pin from v1\.1\.0\"$"), "the commit command is printed", out)
    checks.ok((host / ".lokf" / "scripts" / "knowledge-sync.sh").stat().st_mode & 0o111, "an added script is executable")


def test_a_host_at_the_release_has_nothing_to_sync(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    sync(host, skills)
    git = Git(host)
    git("add", "-A")
    git("commit", "-qm", "synced")
    result = sync(host, skills)
    checks.ok(result.rc == 0, "exit 0", result.out)
    checks.ok(has_line(result.out, "   nothing to sync") and has_line(result.out, "   pin      already v1.1.0"), "nothing to sync", result.out)
    checks.ok(not git("status", "--porcelain"), "the tree is left clean")
    checks.ok(read(host / "CHANGELOG.md").count(ENTRY_START) == 1, "the entry is written once")


def test_the_entry_joins_an_existing_security_section_at_its_end(tmp_path, skills, checks):
    changelog = "# Changelog\n\n## [Unreleased]\n\n### Changed\n\n- Something.\n\n### Security\n\n- Earlier line.\n\n## [1.0.0] - 2026-01-01\n"
    host = make_host(tmp_path, skills, changelog=changelog)
    sync(host, skills)
    text = read(host / "CHANGELOG.md")
    checks.ok("- Earlier line.\n" + ENTRY_START in text, "the entry follows the section's last line", text)
    checks.ok(text.count("### Security") == 1, "no second Security section", text)
    checks.ok(text.endswith("\n\n## [1.0.0] - 2026-01-01\n"), "the released section is untouched", text)


def test_a_security_section_is_added_last_in_unreleased(tmp_path, skills, checks):
    changelog = "# Changelog\n\n## [Unreleased]\n\n### Changed\n\n- Something.\n\n## [1.0.0] - 2026-01-01\n"
    host = make_host(tmp_path, skills, changelog=changelog)
    sync(host, skills)
    text = read(host / "CHANGELOG.md")
    checks.ok("- Something.\n\n### Security\n\n" + ENTRY_START in text, "the section follows the last line of Unreleased", text)
    checks.ok(text.endswith("\n\n## [1.0.0] - 2026-01-01\n"), "one blank line before the next release heading", text)


def test_a_changelog_without_unreleased_gets_the_entry_printed(tmp_path, skills, checks):
    host = make_host(tmp_path, skills, changelog="# Changelog\n\n## [1.0.0] - 2026-01-01\n")
    result = sync(host, skills)
    checks.ok(result.rc == 0, "exit 0", result.out)
    checks.ok(matches(result.out, r"^   entry    CHANGELOG\.md has no Unreleased heading, so add the entry by hand:$"), "the person is asked", result.out)
    checks.ok(ENTRY_START in result.out, "the entry is printed", result.out)
    checks.ok(read(host / "CHANGELOG.md") == "# Changelog\n\n## [1.0.0] - 2026-01-01\n", "the file is left alone")


def test_the_hosts_justfile_keeps_its_first_line_and_schema_line(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    result = sync(host, skills)
    checks.ok(has_line(result.out, "   copied   .lokf/justfile"), "the justfile is copied", result.out)
    text = read(host / ".lokf" / "justfile")
    checks.ok(text.startswith("# LOKF knowledge-bundle recipes for Acme.\n"), "the first line is the host's", text)
    checks.ok('schema := "acme.yaml"' in text and 'schema := ""' not in text, "the schema line is the host's", text)
    checks.ok("a recipe comment the next release adds" in text, "the rest is the release's", text)


def test_commit_mode_works_on_its_own_branch(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    git = Git(host)
    before = git("rev-parse", "main")
    result = sync(host, skills, "--commit")
    checks.ok(result.rc == 0, "exit 0", result.out)
    checks.ok(has_line(result.out, "   branch   sync-v1.1.0, from origin/main"), "the branch starts from origin's default branch", result.out)
    checks.ok(git("branch", "--show-current") == "sync-v1.1.0", "the host is on the sync branch")
    checks.ok(git("log", "-1", "--format=%s") == "security(sidecar): sync copies and skills pin from v1.1.0", "the commit carries the subject")
    checks.ok(git("rev-list", "--count", "main..sync-v1.1.0") == "1", "one commit on the branch")
    checks.ok(git("rev-parse", "main") == before, "main is where it was")
    checks.ok(not git("status", "--porcelain"), "the tree is clean after the commit")
    checks.ok((host / ".git" / "knowledge-sync-body.md").is_file(), "the pull request body is kept under .git/")
    again = sync(host, skills, "--commit")
    checks.ok(again.rc == 1 and "sync-v1.1.0 already exists" in again.out, "a branch that exists is refused", again.out)


def test_what_is_refused(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    with (host / "CHANGELOG.md").open("a") as f:
        f.write("\n- a change nobody committed\n")
    dirty = sync(host, skills, "--branch")
    checks.ok(dirty.rc == 1 and "uncommitted changes" in dirty.out, "a dirty tree is refused", dirty.out)
    Git(host)("checkout", "--", "CHANGELOG.md")
    not_a_tag = run(["bash", SYNC, "--source", skills, "--host", host, "--no-checks", "main"], cwd=host, env=IDENT)
    checks.ok(not_a_tag.rc == 2 and "is not a release tag" in not_a_tag.out, "a branch name is refused", not_a_tag.out)
    missing = run(["bash", SYNC, "--source", skills, "--host", host, "--no-checks", "v9.9.9"], cwd=host, env=IDENT)
    checks.ok(missing.rc == 2 and "no tag v9.9.9" in missing.out, "a tag the source lacks is refused", missing.out)
    nowhere = run(["bash", SYNC, "--source", skills, "--host", tmp_path, "--no-checks", "v1.1.0"], cwd=tmp_path, env=IDENT)
    checks.ok(nowhere.rc == 1 and "no .lokf/" in nowhere.out, "a directory with no sidecar is skipped", nowhere.out)


def test_without_a_source_the_hosts_copy_clones_the_tag_and_hands_over(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    result = run(["bash", ".lokf/scripts/knowledge-sync.sh", "--repo", f"file://{skills}", "--no-checks", "v1.1.0"], cwd=host, env=IDENT)
    checks.ok(result.rc == 0, "exit 0", result.out)
    checks.ok(has_line(result.out, f"   cloning v1.1.0 from file://{skills}"), "the tag is cloned", result.out)
    checks.ok(has_line(result.out, "   handing over to v1.1.0's copy of this script"), "the tag's copy takes over", result.out)
    checks.ok("a line the next release adds to the sync script" in read(host / ".lokf" / "scripts" / "knowledge-sync.sh"), "the host's copy is the tag's afterwards")
    checks.ok("TRUST_LADDER_SKILLS_REF: v1.1.0" in read(host / LIBRARIAN), "the pin moved")


def test_the_fan_out_runs_the_tags_copy_in_each_sibling_and_finishes_merged_branches(tmp_path, skills, checks):
    one = make_host(tmp_path, skills, "one")
    two = make_host(tmp_path, skills, "two")
    result = run(["bash", FANOUT, "--push", "--no-checks", "--source", skills, "v1.1.0", one, two], cwd=tmp_path, env=IDENT)
    checks.ok(result.rc == 0, "exit 0", result.out)
    for host in (one, two):
        git = Git(host)
        checks.ok(has_line(result.out, f"== {host}"), f"{host.name} is reported", result.out)
        checks.ok(git("branch", "--show-current") == "sync-v1.1.0", f"{host.name} is on the sync branch")
        checks.ok(git("rev-list", "--count", "main..sync-v1.1.0") == "1", f"{host.name} has the one commit")
        checks.ok(git("rev-parse", "origin/sync-v1.1.0") == git("rev-parse", "sync-v1.1.0"), f"{host.name}'s branch is pushed")
    checks.ok(matches(result.out, r"^When the pull requests are merged: scripts/sync-sidecar\.sh --finish v1\.1\.0 "), "the finish command is printed", result.out)
    not_a_tag = run(["bash", FANOUT, "--no-checks", "--source", skills, "main", one], cwd=tmp_path, env=IDENT)
    checks.ok(not_a_tag.rc == 2, "a branch name is refused", not_a_tag.out)

    kept = run(["bash", FANOUT, "--finish", "v1.1.0", one], cwd=tmp_path, env=IDENT)
    checks.ok(kept.rc == 0 and "origin/sync-v1.1.0 still exists" in kept.out, "a branch whose remote branch still exists is kept", kept.out)
    # The pull request is squash-merged on origin and its branch deleted,
    # as a merge in the browser does.
    merger = tmp_path / "merger"
    run(["git", "clone", "-q", "-b", "main", tmp_path / "one-origin.git", merger], env=IDENT)
    m = Git(merger)
    m("fetch", "-q", "origin", "sync-v1.1.0")
    m("merge", "-q", "--squash", "FETCH_HEAD")
    m("commit", "-qm", "security(sidecar): sync copies and skills pin from v1.1.0 (#1)")
    m("push", "-q", "origin", "main")
    m("push", "-q", "origin", "--delete", "sync-v1.1.0")
    done = run(["bash", FANOUT, "--finish", "v1.1.0", one], cwd=tmp_path, env=IDENT)
    git = Git(one)
    checks.ok(done.rc == 0 and "sync-v1.1.0 removed" in done.out, "the merged branch is removed", done.out)
    checks.ok(git("branch", "--show-current") == "main", "the host is back on main")
    checks.ok(git("rev-parse", "main") == git("rev-parse", "origin/main"), "main is up to date")
    checks.ok("sync-v1.1.0" not in git("branch"), "the branch is gone")

    Git(two)("branch", "--unset-upstream", "sync-v1.1.0")
    never = run(["bash", FANOUT, "--finish", "v1.1.0", two], cwd=tmp_path, env=IDENT)
    checks.ok(never.rc == 1 and "was never pushed" in never.out, "a branch with no upstream is kept and reported", never.out)
