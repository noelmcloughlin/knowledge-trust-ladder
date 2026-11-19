"""The sidecar's sync script brings a host to one release of the ktl package.

knowledge-sync.sh is the template every host carries as
.lokf/scripts/knowledge-sync.sh. These tests release the real templates as
two ktl wheels on a local file:// index, and run the script on a host whose
.lokf/pyproject.toml pins the first:

1. it moves the pin and relocks, copies the templates the release changed,
   adds a template a file the host carries needs, reports one ktl-sidecar's
   Step 5 decides, and writes the changelog entry under "## [Unreleased]"
   and "### Security";
2. a host at the release has nothing to sync, and the entry is written once;
3. the entry joins a Security section the changelog already has, at its end,
   and a section is added last when there is none;
4. the host's justfile keeps its own first line and `schema :=` line;
5. --commit works on sync-<tag> from origin's default branch. A dirty tree, a
   branch that exists, a tag that is not a release, a release the index
   lacks and a host with no pin are each refused, and a refused release
   leaves the pin and the lock as they were;
6. the host's own copy reads the release from its own index, or from a
   --source folder of wheels, and reports a manifest rule it does not know;
7. a manifest that names a copy path outside the host, or inside a .git
   folder, is refused;
8. a run that copies a longer script over its own file stops when main
   returns, and so does a copy that ends with a bare `main "$@"`;
9. --apply takes the pin's line at the run's tag and a lock uv writes the
   same from the index, and holds every workflow change;
10. --workflow runs the steps of knowledge-sync.yaml: read picks the
    release, sync writes the patch, apply holds the workflow changes, and
    publish pushes the branch and opens or refreshes the pull request.

Every run skips the sidecar's checks (--no-checks): the preflight, the
toolkit and the conventions script have modules of their own.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import shutil
import sys
import zipfile

import pytest

from conftest import REPO, SCRIPTS, TEMPLATES, WEBSITE_TEMPLATES, WORKFLOWS, Git, has_line, have, matches, read, run, write

SYNC = SCRIPTS / "knowledge-sync.sh"
LIBRARIAN = ".github/workflows/knowledge-librarian.yaml"
PYPROJECT = ".lokf/pyproject.toml"
LOCK = ".lokf/uv.lock"
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
    "gitignore": ".lokf/.gitignore",
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


def bare_main(text):
    """The sync script as copies ended before the exit after main: a bare `main "$@"` and nothing below it."""
    return text[: text.rindex("\n}\n") + 3] + '\nmain "$@"\n'


def bare(path):
    run(["git", "init", "-q", "--bare", path], env=IDENT)
    return path


def wheel(repo, version, into):
    """A ktl wheel of repo's skills/, laid out as hatchling builds it (ktl/skills/...), each file's mode kept."""
    files = []
    for path in sorted((repo / "skills").rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            files.append((f"ktl/{path.relative_to(repo).as_posix()}", path.read_bytes(), path.stat().st_mode))
    meta = f"ktl-{version}.dist-info"
    files += [
        ("ktl/__init__.py", b"", 0o644),
        (f"{meta}/METADATA", f"Metadata-Version: 2.1\nName: ktl\nVersion: {version}\n".encode(), 0o644),
        (f"{meta}/WHEEL", b"Wheel-Version: 1.0\nGenerator: tests\nRoot-Is-Purelib: true\nTag: py3-none-any\n", 0o644),
    ]
    digest = lambda data: base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()  # noqa: E731
    record = [f"{name},sha256={digest(data)},{len(data)}" for name, data, _ in files] + [f"{meta}/RECORD,,"]
    files.append((f"{meta}/RECORD", ("\n".join(record) + "\n").encode(), 0o644))
    path = into / f"ktl-{version}-py3-none-any.whl"
    with zipfile.ZipFile(path, "w") as z:
        for name, data, mode in files:
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.external_attr = ((mode & 0o777) | 0o100000) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    return path


class Releases:
    """The skills repository, each release of it as a ktl wheel, and a file:// index that serves them."""

    def __init__(self, root):
        self.repo = root / "skills"
        self.wheels = root / "wheels"
        self.index = root / "index"
        self.env = {**IDENT, "UV_CACHE_DIR": str(root / "uv-cache"), "UV_NO_PROGRESS": "1", "UV_PYTHON_DOWNLOADS": "never"}

    def __fspath__(self):
        return str(self.repo)

    def __str__(self):
        return str(self.repo)

    def __truediv__(self, other):
        return self.repo / other

    def release(self, version):
        """Commit and tag the tree as v<version>, and put its wheel on the index."""
        git = Git(self.repo)
        git("add", "-A")
        git("commit", "-qm", f"v{version}")
        git("tag", f"v{version}")
        self.wheels.mkdir(exist_ok=True)
        wheel(self.repo, version, self.wheels)
        links = "".join(
            f'<a href="../../wheels/{w.name}#sha256={hashlib.sha256(w.read_bytes()).hexdigest()}">{w.name}</a>\n'
            for w in sorted(self.wheels.glob("*.whl"))
        )
        write(self.index / "ktl" / "index.html", f"<!DOCTYPE html>\n<html><body>\n{links}</body></html>\n")

    def hash(self, version):
        return hashlib.sha256((self.wheels / f"ktl-{version}-py3-none-any.whl").read_bytes()).hexdigest()


@pytest.fixture
def skills(tmp_path):
    """The skills repository: the real templates released as v1.0.0, then as v1.1.0 changing three of them, with an origin that holds both tags."""
    releases = Releases(tmp_path)
    repo = releases.repo
    repo.mkdir()
    git = Git(repo)
    git.init()
    shutil.copytree(TEMPLATES, repo / "skills" / "ktl-sidecar" / "templates", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(WEBSITE_TEMPLATES, repo / "skills" / "ktl-website" / "templates")
    write(repo / "skills" / "ktl-librarian" / "SKILL.md", "# skill\n")
    releases.release("1.0.0")
    templates = repo / "skills" / "ktl-sidecar" / "templates"
    with (templates / "scripts" / "knowledge-report.sh").open("a") as f:
        f.write("\n# a line the next release adds\n")
    # The new line goes under the first, not at the end, so the old copy's
    # end falls in the middle of the new one's code, as it does in a release.
    sync_script = templates / "scripts" / "knowledge-sync.sh"
    first, rest = sync_script.read_text().split("\n", 1)
    sync_script.write_text(f"{first}\n# a line the next release adds to the sync script\n{rest}")
    with (templates / "justfile").open("a") as f:
        f.write("\n# a recipe comment the next release adds\n")
    with (templates / "knowledge-sync.manifest").open("a") as f:
        f.write("mirror docs/example.md .lokf/example.md\n")
    releases.release("1.1.0")
    git("remote", "add", "origin", str(bare(tmp_path / "skills-origin.git")))
    git("push", "-q", "origin", "main", "--tags")
    return releases


def pyproject(skills, version="1.0.0", index=True):
    """A host's .lokf/pyproject.toml that pins ktl, and names the releases' index as `knowledge` unless index is False."""
    text = (
        '[project]\nname = "acme-knowledge"\nversion = "0.1.0"\nrequires-python = ">=3.9"\n'
        f'dependencies = [\n    "ktl=={version}",\n]\n\n[tool.uv]\npackage = false\n'
    )
    if index:
        text += f'\n[[tool.uv.index]]\nname = "knowledge"\nurl = "{skills.index.as_uri()}"\ndefault = true\n'
    return text


def make_host(tmp_path, skills, name="host", changelog=CHANGELOG, index=True):
    """A host at v1.0.0: the copies, a titled justfile with its own schema line, the ktl pin and its lock, a changelog and an origin."""
    host = tmp_path / name
    host.mkdir()
    git = Git(host)
    git.init()
    src = Git(skills.repo)
    for template, copy in COPIES.items():
        write(host / copy, src("show", f"v1.0.0:skills/ktl-sidecar/templates/{template}") + "\n")
        if copy.endswith((".sh", ".py")):
            (host / copy).chmod(0o755)
    justfile = src("show", "v1.0.0:skills/ktl-sidecar/templates/justfile").split("\n")[1:]
    justfile = [line if not line.startswith("schema := ") else 'schema := "acme.yaml"' for line in justfile]
    write(host / ".lokf" / "justfile", "# LOKF knowledge-bundle recipes for Acme.\n" + "\n".join(justfile) + "\n")
    write(host / PYPROJECT, pyproject(skills, index=index))
    where = [] if index else ["--no-index", "--find-links", skills.wheels]
    locked = run(["uv", "lock", "--quiet", *where], cwd=host / ".lokf", env=skills.env)
    assert locked.rc == 0, locked.out
    write(host / "CHANGELOG.md", changelog)
    write(host / ".lokf" / "knowledge" / "index.md", "# Acme\n")
    git("add", "-A")
    git("commit", "-qm", "host at v1.0.0")
    git("remote", "add", "origin", str(bare(tmp_path / f"{name}-origin.git")))
    git("push", "-q", "-u", "origin", "main")
    return host


def sync(host, skills, *args, cwd=None):
    return run(["bash", SYNC, "--host", host, "--no-checks", *args, "v1.1.0"], cwd=cwd or host, env=skills.env)


def test_a_sync_copies_adds_reports_pins_and_writes_the_entry(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    changed = tmp_path / "changed.txt"
    report = tmp_path / "report.md"
    result = sync(host, skills, "--changed", changed, "--report", report)
    checks.ok(result.rc == 0, "exit 0", result.out)
    out = result.out
    checks.ok(has_line(out, "   copied   .lokf/scripts/knowledge-report.sh"), "the changed template is copied", out)
    checks.ok(has_line(out, "   copied   .lokf/scripts/knowledge-sync.sh"), "the sync script's own copy is copied", out)
    checks.ok(matches(out, r"^   added    \.github/workflows/knowledge-sync\.yaml \(\.github/workflows/knowledge-librarian\.yaml installs the skill from the ktl pin"), "the sync workflow is added beside the librarian", out)
    checks.ok(matches(out, r"^   added    \.github/PULL_REQUEST_TEMPLATE/knowledge-sync\.md \(\.github/workflows/knowledge-sync\.yaml opens"), "the pull request template is added beside the workflow", out)
    checks.ok(matches(out, r"^   absent   \.lokf/schema/domain\.yaml \(never installed here"), "a domain host's file is reported, not added", out)
    checks.ok(matches(out, r"^   unknown  mirror docs/example\.md: a manifest rule this copy of knowledge-sync\.sh does not know"), "a rule the script does not know is reported", out)
    checks.ok(not (host / ".lokf" / "example.md").exists(), "and nothing is done for it")
    checks.ok(has_line(out, "   same     .github/workflows/knowledge-registrar.yaml"), "an unchanged copy is left alone", out)
    checks.ok(has_line(out, "   locking  ktl==1.1.0") and has_line(out, "   pin      v1.0.0 to v1.1.0"), "the pin moves to the release", out)
    checks.ok('"ktl==1.1.0"' in read(host / PYPROJECT) and '"ktl==1.0.0"' not in read(host / PYPROJECT), "pyproject.toml pins the release")
    checks.ok(f"sha256:{skills.hash('1.1.0')}" in read(host / LOCK), "the lock holds the release's hash from the index")
    checks.ok("a line the next release adds" in read(host / ".lokf" / "scripts" / "knowledge-report.sh"), "the copy carries the release's bytes")
    changelog = read(host / "CHANGELOG.md")
    checks.ok("## [Unreleased]\n\n### Security\n\n" + ENTRY_START in changelog, "the entry sits under Unreleased and Security", changelog)
    checks.ok("compare/v1.0.0...v1.1.0" in changelog, "the entry links the comparison between the two pins", changelog)
    checks.ok("`.lokf/scripts/knowledge-report.sh`" in changelog and "No plugin change" not in changelog, "the entry names the files and says nothing of a plugin", changelog)
    listed = read(changed).split("\n")
    checks.ok(len(listed) == len(set(listed)), "each changed path is listed once", str(listed))
    for path in (".lokf/scripts/knowledge-report.sh", ".github/workflows/knowledge-sync.yaml", PYPROJECT, LOCK, "CHANGELOG.md"):
        checks.ok(path in listed, f"{path} is listed as changed", str(listed))
    body = read(report)
    checks.ok(body.startswith("Brings the sidecar copies and the skills pin of this repository to Knowledge Trust Ladder [v1.1.0]("), "the report opens with the release", body)
    checks.ok("- `.lokf/scripts/knowledge-report.sh`" in body and "skipped (--no-checks)" in body, "the report lists the copies and the checks", body)
    checks.ok("does not know their rule:\n\n- `mirror docs/example.md`" in body, "the report names the rule the script does not know, so the pull request shows it", body)
    checks.ok(matches(out, r"^   git commit -m \"security\(sidecar\): sync copies and skills pin from v1\.1\.0\"$"), "the commit command is printed", out)
    checks.ok((host / ".lokf" / "scripts" / "knowledge-sync.sh").stat().st_mode & 0o111, "an added script is executable")


def test_a_folder_of_wheels_stands_in_for_the_index(tmp_path, skills, checks):
    """A host with no index syncs from --source, a folder that holds every package its lock names."""
    host = make_host(tmp_path, skills, index=False)
    result = sync(host, skills, "--source", skills.wheels)
    checks.ok(result.rc == 0, "exit 0", result.out)
    checks.ok(has_line(result.out, "   pin      v1.0.0 to v1.1.0") and has_line(result.out, "   copied   .lokf/scripts/knowledge-report.sh"), "the pin moves and the copies follow", result.out)
    text = read(host / PYPROJECT)
    checks.ok('"ktl==1.1.0"' in text and "[[tool.uv.index]]" not in text, "the pin moves, and no index is written into pyproject.toml", text)


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


@pytest.mark.parametrize("folder", ["website", "ktl-website"])
def test_a_host_with_a_site_gets_the_site_templates_in_whichever_folder_holds_it(tmp_path, skills, checks, folder):
    """The site is in website/, or in ktl-website/ where website/ was another site's, which the sync then leaves alone."""
    host = make_host(tmp_path, skills)
    write(host / folder / "site.toml", 'title = "Acme"\n')
    if folder == "ktl-website":
        write(host / "website" / "index.html", "<p>another site</p>\n")
    git = Git(host)
    git("add", "-A")
    git("commit", "-qm", "a site")
    result = sync(host, skills)
    checks.ok(result.rc == 0, "exit 0", result.out)
    adapter = "content/docs/_content.gotmpl"
    checks.ok(has_line(result.out, f"   added    {folder}/{adapter} (the site cannot build without it)"), "a template the site lacks is added", result.out)
    checks.ok(read(host / folder / adapter) == read(WEBSITE_TEMPLATES / "website" / adapter), "with the template's bytes")
    checks.ok((host / folder / ".gitignore").is_file() and not (host / folder / "gitignore").exists(), "the gitignore gets its dot")
    checks.ok(read(host / folder / "site.toml") == 'title = "Acme"\n', "the site file the host owns is left alone")
    if folder == "ktl-website":
        checks.ok(sorted(p.name for p in (host / "website").iterdir()) == ["index.html"], "another site's website/ is left alone")


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
    not_a_tag = run(["bash", SYNC, "--host", host, "--no-checks", "main"], cwd=host, env=skills.env)
    checks.ok(not_a_tag.rc == 2 and "is not a release tag" in not_a_tag.out, "a branch name is refused", not_a_tag.out)
    missing = run(["bash", SYNC, "--host", host, "--no-checks", "v9.9.9"], cwd=host, env=skills.env)
    checks.ok(missing.rc == 2 and "no release v9.9.9 of ktl on the index" in missing.out, "a release the index lacks is refused", missing.out)
    checks.ok(not Git(host)("status", "--porcelain"), "and the pin and the lock are as they were")
    nowhere = run(["bash", SYNC, "--host", tmp_path, "--no-checks", "v1.1.0"], cwd=tmp_path, env=skills.env)
    checks.ok(nowhere.rc == 1 and "no .lokf/" in nowhere.out, "a directory with no sidecar is skipped", nowhere.out)
    write(host / PYPROJECT, read(host / PYPROJECT).replace('    "ktl==1.0.0",\n', ""))
    Git(host)("commit", "-qam", "no pin")
    unpinned = sync(host, skills)
    checks.ok(unpinned.rc == 1 and 'uv add --project .lokf "ktl==1.1.0"' in unpinned.out, "a host with no pin is told the command that adds it", unpinned.out)


def test_a_sync_told_to_wait_asks_the_index_again_for_a_release_it_does_not_show(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    index = skills.index / "ktl" / "index.html"
    write(index, "\n".join(line for line in read(index).splitlines() if "ktl-1.1.0" not in line) + "\n")
    env = {**skills.env, "KNOWLEDGE_SYNC_INDEX_WAIT": "1"}
    result = run(["bash", ".lokf/scripts/knowledge-sync.sh", "--no-checks", "v1.1.0"], cwd=host, env=env)
    checks.ok(result.rc == 2 and "publish the release first" in result.out, "a release the index never shows is missing", result.out)
    checks.ok(has_line(result.out, "   waiting  the index does not show the release yet; asking again in 1 s"), "after it was asked for again", result.out)
    checks.ok(not Git(host)("status", "--porcelain"), "the pin and the lock are as they were")
    result = run(["bash", ".lokf/scripts/knowledge-sync.sh", "--no-checks", "v1.1.0"], cwd=host, env={**skills.env, "KNOWLEDGE_SYNC_INDEX_WAIT": "soon"})
    checks.ok(result.rc == 2 and "not a number of seconds" in result.out, "a wait that is not a number is refused", result.out)


def test_the_hosts_own_copy_reads_the_release_from_the_index_its_pyproject_names(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    result = run(["bash", ".lokf/scripts/knowledge-sync.sh", "--no-checks", "v1.1.0"], cwd=host, env=skills.env)
    checks.ok(result.rc == 0, "exit 0", result.out)
    checks.ok(has_line(result.out, "   locking  ktl==1.1.0"), "the pin is locked from the host's index", result.out)
    checks.ok(has_line(result.out, "   copied   .lokf/scripts/knowledge-sync.sh"), "the script's own copy is synced like any other", result.out)
    checks.ok("a line the next release adds to the sync script" in read(host / ".lokf" / "scripts" / "knowledge-sync.sh"), "the host's copy is the release's afterwards")
    checks.ok('"ktl==1.1.0"' in read(host / PYPROJECT), "the pin moved")
    checks.ok(not (host / ".lokf" / ".venv").exists(), "nothing is installed into the host's environment")


def test_a_copy_that_ends_with_a_bare_main_stops_when_it_syncs_the_exit_in(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    script = host / ".lokf" / "scripts" / "knowledge-sync.sh"
    write(script, bare_main(read(script)))
    Git(host)("commit", "-qam", "a copy from before the exit")
    # v1.0.0's script differs from this copy only in its last line, so the
    # copy reads " exit" next when main returns.
    result = run(["bash", ".lokf/scripts/knowledge-sync.sh", "--no-checks", "v1.0.0"], cwd=host, env=skills.env)
    checks.ok(result.rc == 0, "exit 0", result.out)
    # The host pins v1.0.0 and its copy differs from v1.0.0's, so the sync
    # calls it a local edit.
    checks.ok(matches(result.out, r"^   local    \.lokf/scripts/knowledge-sync\.sh differed from its template at v1\.0\.0"), "the script's own copy is synced", result.out)
    checks.ok(has_line(read(script), 'main "$@"; exit'), "the copy ends with the exit afterwards")


def test_a_manifest_that_names_a_path_outside_the_host_is_refused(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    git = Git(skills)
    with (skills / "skills" / "ktl-sidecar" / "templates" / "knowledge-sync.manifest").open("a") as f:
        f.write("copy scripts/knowledge-report.sh ../escaped.sh\n")
    skills.release("1.2.0")
    result = run(["bash", SYNC, "--host", host, "--no-checks", "v1.2.0"], cwd=host, env=skills.env)
    checks.ok(result.rc == 2 and "outside the host" in result.out, "the manifest is refused before anything is written", result.out)
    checks.ok(not Git(host)("status", "--porcelain"), "the host is untouched")


@pytest.mark.parametrize("copy", [".git/config", ".GIT/hooks/pre-commit", ".lokf/.git/config"])
def test_a_manifest_that_names_a_path_in_a_git_folder_is_refused(tmp_path, skills, checks, copy):
    """A copy under .git is git's own configuration, which can name a command the next git command runs."""
    host = make_host(tmp_path, skills)
    config = read(host / ".git" / "config")
    git = Git(skills)
    with (skills / "skills" / "ktl-sidecar" / "templates" / "knowledge-sync.manifest").open("a") as f:
        f.write(f"copy scripts/knowledge-report.sh {copy}\n")
    skills.release("1.2.0")
    result = run(["bash", SYNC, "--host", host, "--no-checks", "v1.2.0"], cwd=host, env=skills.env)
    checks.ok(result.rc == 2 and "inside a .git folder" in result.out, "the manifest is refused before anything is written", result.out)
    checks.ok(not Git(host)("status", "--porcelain"), "the host is untouched")
    checks.ok(read(host / ".git" / "config") == config, "and so is its git configuration")


def test_a_changelog_with_crlf_endings_keeps_them(tmp_path, skills, checks):
    changelog = CHANGELOG.replace("\n", "\r\n")
    host = make_host(tmp_path, skills, changelog=changelog)
    result = sync(host, skills)
    checks.ok(result.rc == 0, "exit 0", result.out)
    raw = (host / "CHANGELOG.md").read_bytes()
    checks.ok(b"\n" not in raw.replace(b"\r\n", b""), "every line still ends with CRLF")
    checks.ok(b"## [Unreleased]\r\n\r\n### Security\r\n\r\n" + ENTRY_START.encode() in raw, "the entry sits under Unreleased and Security", raw.decode())


def test_a_sync_to_an_older_release_says_so(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    write(host / PYPROJECT, read(host / PYPROJECT).replace('"ktl==1.0.0"', '"ktl==1.2.0"'))
    git = Git(host)
    git("add", "-A")
    git("commit", "-qm", "pinned ahead")
    result = sync(host, skills)
    checks.ok(result.rc == 0, "exit 0", result.out)
    checks.ok(matches(result.out, r"^   pin      v1\.2\.0 back to v1\.1\.0: an older release than the host had$"), "the backwards move is named", result.out)


def test_a_sync_changes_pyproject_toml_on_the_pin_line_alone(tmp_path, skills, checks):
    """The host's own settings, such as the index it names, stay as they were."""
    host = make_host(tmp_path, skills)
    result = sync(host, skills)
    checks.ok(result.rc == 0, "exit 0", result.out)
    lines = [line for line in Git(host)("diff", "-U0", "--", PYPROJECT).split("\n") if re.match(r"^[-+][^-+]", line)]
    checks.ok(lines == ['-    "ktl==1.0.0",', '+    "ktl==1.1.0",'], "one line out, one in", str(lines))
    checks.ok(f'url = "{skills.index.as_uri()}"' in read(host / PYPROJECT), "the index stays")


def test_an_index_without_ktl_is_not_called_a_missing_release(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    shutil.rmtree(skills.index)
    result = sync(host, skills)
    checks.ok(result.rc == 2 and "has no ktl package, or could not be read" in result.out, "the index is named", result.out)
    checks.ok("publish the release first" not in result.out, "and not a missing release", result.out)
    checks.ok(not Git(host)("status", "--porcelain"), "the pin and the lock are as they were")


def test_a_copy_bumped_by_dependabot_is_reported(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    copy = host / ".github" / "workflows" / "knowledge-release.yaml"
    text = read(copy)
    line = next(l for l in text.split("\n") if "uses: actions/checkout@" in l)
    write(copy, text.replace(line, line.replace("actions/checkout@", "actions/checkout@0000000000000000000000000000000000000000 # v9.9.9 was "), 1))
    git = Git(host)
    git("add", "-A")
    git("commit", "-qm", "dependabot bump")
    result = sync(host, skills)
    checks.ok(result.rc == 0, "exit 0", result.out)
    checks.ok(has_line(result.out, "   copied   .github/workflows/knowledge-release.yaml"), "the copy is brought back to the template", result.out)
    checks.ok(matches(result.out, r"^   pins     \.github/workflows/knowledge-release\.yaml differed only on its action pins"), "the report names the bump", result.out)


def test_a_copy_that_differs_on_another_line_is_not_called_a_pin_bump(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    copy = host / ".github" / "workflows" / "knowledge-release.yaml"
    text = read(copy)
    line = next(l for l in text.split("\n") if "uses: actions/checkout@" in l)
    write(copy, text.replace(line, line.replace("actions/checkout@", "actions/checkout@0000000000000000000000000000000000000000 # v9.9.9 was "), 1) + "# a line the host added\n")
    git = Git(host)
    git("add", "-A")
    git("commit", "-qm", "dependabot bump and an edit")
    result = sync(host, skills)
    checks.ok(result.rc == 0, "exit 0", result.out)
    checks.ok(matches(result.out, r"^   local    \.github/workflows/knowledge-release\.yaml differed from its template at v1\.0\.0, a local edit"), "the copy is brought back to the template, as a local edit", result.out)
    checks.ok(has_line(result.out, "   copied   .lokf/scripts/knowledge-report.sh"), "the release's own change is copied", result.out)
    checks.ok(not matches(result.out, r"^   pins     "), "neither copy is called a pin bump, since each differs on a line that is not a pin", result.out)


def test_a_local_edit_the_sync_overwrites_is_not_blamed_on_the_release(tmp_path, skills, checks):
    """A copy that differs from its template at the old pin was edited here, and the report says so rather than that the release changed it."""
    host = make_host(tmp_path, skills)
    copy = host / ".lokf" / "scripts" / "knowledge-feedback.sh"
    write(copy, read(copy) + "# a line the host added\n")
    git = Git(host)
    git("add", "-A")
    git("commit", "-qm", "a local edit")
    report = tmp_path / "report.md"
    changed = tmp_path / "changed.txt"
    result = sync(host, skills, "--report", report, "--changed", changed)
    checks.ok(result.rc == 0, "exit 0", result.out)
    checks.ok(matches(result.out, r"^   local    \.lokf/scripts/knowledge-feedback\.sh differed from its template at v1\.0\.0"), "the edit is named as local", result.out)
    checks.ok(not has_line(result.out, "   copied   .lokf/scripts/knowledge-feedback.sh"), "and not as copied", result.out)
    checks.ok("a line the host added" not in read(copy), "the template is written over it")
    body = read(report)
    release_part = body.split("The release changed these copies:")[1].split("\n\n", 2)[1] if "The release changed these copies:" in body else ""
    checks.ok("knowledge-feedback.sh" not in release_part and "A local edit this sync overwrote" in body and "- `.lokf/scripts/knowledge-feedback.sh`" in body,
              "the report lists it under the local edit, not under the release", body)
    checks.ok("local edit of `.lokf/scripts/knowledge-feedback.sh`" in read(host / "CHANGELOG.md"), "the entry says so too", read(host / "CHANGELOG.md"))
    checks.ok(".lokf/scripts/knowledge-feedback.sh" in read(changed).split("\n"), "the overwritten copy is staged with the rest", read(changed))


def test_a_host_file_no_manifest_line_names_is_reported_and_left_alone(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    write(host / ".lokf" / "scripts" / "knowledge-old.sh", "#!/usr/bin/env bash\n")
    write(host / ".github" / "workflows" / "knowledge-old.yaml", "name: old\n")
    git = Git(host)
    git("add", "-A")
    git("commit", "-qm", "a template a release dropped")
    report = tmp_path / "report.md"
    result = sync(host, skills, "--report", report)
    checks.ok(result.rc == 0, "exit 0", result.out)
    for path in (".lokf/scripts/knowledge-old.sh", ".github/workflows/knowledge-old.yaml"):
        checks.ok(matches(result.out, rf"^   unlisted {re.escape(path)}: no line of v1\.1\.0's manifest names it"), f"{path} is named", result.out)
        checks.ok(f"- `{path}`" in read(report), f"{path} is in the report", read(report))
    checks.ok(not matches(result.out, r"^   unlisted \.lokf/scripts/knowledge-report\.sh"), "a listed copy is not called unlisted", result.out)
    checks.ok(read(host / ".lokf" / "scripts" / "knowledge-old.sh") == "#!/usr/bin/env bash\n", "the unlisted file is left as it was")


WORKFLOW = WORKFLOWS / "knowledge-sync.yaml"
PREFLIGHT = SCRIPTS / "knowledge-preflight.sh"
SKILL = REPO / "skills" / "ktl-sidecar" / "SKILL.md"


MANIFEST = TEMPLATES / "knowledge-sync.manifest"
CONTRACT = REPO / "scripts" / "validate-repository.sh"


def manifest():
    """The manifest's lines, as (rule, template, copy-or-step, rest)."""
    lines = []
    for line in read(MANIFEST).split("\n"):
        line = line.split("#", 1)[0].split()
        if line:
            lines.append((line[0], line[1], line[2] if len(line) > 2 else "", " ".join(line[3:])))
    return lines


def synced_pairs():
    """The <template>:<copy> pairs the manifest holds a host to."""
    return [(t, c) for rule, t, c, _ in manifest() if rule in ("copy", "titled")]


def test_every_synced_copy_passes_the_publish_jobs_path_check():
    """A template the script lays down that the privileged job would refuse is a sync that can never open its pull request."""
    text = read(SYNC)
    allow = re.search(r"^sync_paths='([^']+)'$", text, re.M).group(1)
    odd = re.search(r"^plain_path='([^']+)'$", text, re.M).group(1)
    owned = re.search(r"^owned_paths='([^']+)'$", text, re.M).group(1)
    for _, copy in synced_pairs() + [("", "CHANGELOG.md"), ("", PYPROJECT), ("", LOCK), ("", "website/content/docs/_content.gotmpl"), ("", "ktl-website/layouts/_partials/route.html")]:
        assert re.search(allow, copy), f"{copy} is outside the paths the publish job allows"
        assert re.search(odd, copy), f"{copy} has a character the publish job refuses"
        assert not re.search(owned, copy), f"{copy} is a site file the host owns"
    for path in ("website/site.toml", "website/README.md", "website/assets/css/custom.css", "ktl-website/site.toml"):
        assert re.search(owned, path), path
    assert "knowledge-sync.sh --workflow apply" in read(WORKFLOW), "the publish job puts the patch on with the host's own script"


def sync_patch(tmp_path, host, skills, tag):
    """The patch the workflow's sync job hands on, for one run of the script on the host; the host is left clean."""
    changed = tmp_path / f"changed-{tag}.txt"
    result = run(["bash", SYNC, "--host", host, "--no-checks", "--changed", changed, tag], cwd=host, env=skills.env)
    assert result.rc == 0, result.out
    git = Git(host)
    for path in read(changed).split("\n"):
        if path:
            git("add", "--", path)
    patch = tmp_path / f"sync-{tag}.patch"
    patch.write_text(git("diff", "--cached", "--binary") + "\n")
    full = git("write-tree")
    git("reset", "-q", "--hard")
    return patch, full


def apply(host, skills, patch, held, tag):
    return run(["bash", SYNC, "--host", host, "--apply", patch, "--held", held, tag], cwd=host, env=skills.env)


def test_apply_puts_the_sync_on_and_holds_every_workflow_change(tmp_path, skills, checks):
    """A workflow on a branch pushed with a token runs on that push, with the repository's secrets, so the branch carries none."""
    host = make_host(tmp_path, skills)
    with (skills / "skills" / "ktl-sidecar" / "templates" / "github" / "knowledge-registrar.yaml").open("a") as f:
        f.write("# a step the next release adds\n")
    skills.release("1.2.0")
    patch, full = sync_patch(tmp_path, host, skills, "v1.2.0")
    held = tmp_path / "workflows.patch"
    result = apply(host, skills, patch, held, "v1.2.0")
    checks.ok(result.rc == 0, "exit 0", result.out)
    checks.ok(has_line(result.out, "   staged   .lokf/scripts/knowledge-report.sh"), "a script the release changed is staged", result.out)
    checks.ok(has_line(result.out, f"   staged   {PYPROJECT}") and has_line(result.out, f"   staged   {LOCK}"), "the pin and its lock are staged", result.out)
    checks.ok(has_line(result.out, "   held     .github/workflows/knowledge-registrar.yaml (a workflow change, for a person to apply)"), "a workflow the release changed is held", result.out)
    checks.ok(has_line(result.out, "   held     .github/workflows/knowledge-sync.yaml (a workflow change, for a person to apply)"), "and so is one it adds", result.out)
    h = Git(host)
    checks.ok(not h("diff", "--cached", "--name-only", "HEAD", "--", ".github/workflows/"), "no workflow change is staged")
    checks.ok('"ktl==1.2.0"' in read(host / PYPROJECT) and f"sha256:{skills.hash('1.2.0')}" in read(host / LOCK), "the pin is the release, at the index's hash")
    h("commit", "-qm", "the sync")
    h("apply", "--index", held)
    checks.ok(h("write-tree") == full, "the held patch on top of the branch gives the whole sync")


def test_apply_takes_the_pin_at_the_runs_tag_and_a_lock_the_index_gives(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    patch, _ = sync_patch(tmp_path, host, skills, "v1.1.0")
    other = apply(host, skills, patch, tmp_path / "workflows.patch", "v1.2.0")
    checks.ok(other.rc == 2 and "pins another ktl release than v1.2.0" in other.out, "a pin at another release is refused", other.out)
    checks.ok(not Git(host)("status", "--porcelain"), "the checkout is put back")
    tampered = tmp_path / "tampered.patch"
    text = read(patch)
    assert skills.hash("1.1.0") in text
    tampered.write_text(text.replace(skills.hash("1.1.0"), "0" * 64))
    result = apply(host, skills, tampered, tmp_path / "workflows.patch", "v1.1.0")
    checks.ok(result.rc == 2 and "differs from the one uv resolves from the index" in result.out, "a lock with another hash is refused", result.out)
    checks.ok(not Git(host)("status", "--porcelain"), "the checkout is put back")
    extra = tmp_path / "extra.patch"
    extra.write_text(hand_patch(host, lambda h, g: write(h / PYPROJECT, read(h / PYPROJECT).replace('version = "0.1.0"', 'version = "0.2.0"'))))
    result = apply(host, skills, extra, tmp_path / "workflows.patch", "v1.1.0")
    checks.ok(result.rc == 2 and "on a line other than the ktl pin" in result.out, "a change beside the pin is refused", result.out)
    result = apply(host, skills, patch, tmp_path / "workflows.patch", "v1.1.0")
    checks.ok(result.rc == 0, "the sync's own patch goes on", result.out)


def hand_patch(host, change):
    """A patch of one change made in the host's tree, as a compromised sync job could build it; the host is left clean."""
    git = Git(host)
    change(host, git)
    git("add", "-A")
    text = git("diff", "--cached", "--binary") + "\n"
    git("reset", "-q", "--hard")
    git("clean", "-qfd")
    return text


def _delete(host, git):
    git("rm", "-q", ".lokf/scripts/knowledge-report.sh")


def _link(host, git):
    (host / ".lokf" / "scripts" / "knowledge-extra.sh").symlink_to("/etc/passwd")


def _mode(host, git):
    path = host / ".lokf" / "scripts" / "knowledge-report.sh"
    path.chmod(0o777)
    git("update-index", "--chmod=+x", ".lokf/scripts/knowledge-report.sh")


def _outside(host, git):
    write(host / "README.md", "# changed\n")


def _owned(host, git):
    write(host / "website" / "site.toml", 'title = "x"\n')


@pytest.mark.parametrize(
    "change, says",
    [
        (_delete, "more than edit and add plain files"),
        (_link, "more than edit and add plain files"),
        (_outside, "paths a sync may not"),
        (_owned, "paths a sync may not"),
    ],
)
def test_apply_refuses_what_a_sync_never_does(tmp_path, skills, checks, change, says):
    host = make_host(tmp_path, skills)
    patch = tmp_path / "bad.patch"
    patch.write_text(hand_patch(host, change))
    result = apply(host, skills, patch, tmp_path / "workflows.patch", "v1.1.0")
    checks.ok(result.rc == 2 and says in result.out, f"refused: {says}", result.out)
    checks.ok(not Git(host)("status", "--porcelain"), "the checkout is untouched")


def _domain_in_folder(host, git):
    write(host / ".lokf" / "schema" / "domain.yaml", "id: https://w3id.org/ktl/domain\n")


def _domain_at_root(host, git):
    write(host / ".lokf" / "domain.yaml", "id: https://w3id.org/ktl/domain\n")


def _other_schema(host, git):
    write(host / ".lokf" / "schema" / "acme.yaml", "id: https://acme.example/schema\n")


@pytest.mark.parametrize(
    "change, path",
    [(_domain_in_folder, ".lokf/schema/domain.yaml"), (_domain_at_root, ".lokf/domain.yaml"), (_other_schema, None)],
    ids=["the schema folder", "the root of .lokf", "a host's own schema"],
)
def test_apply_takes_the_domain_vocabulary_in_either_place_and_no_other(tmp_path, skills, checks, change, path):
    """The sync keeps domain.yaml in .lokf/schema/, and a host's script from before the folder keeps it at the root. A schema the host wrote is its own."""
    host = make_host(tmp_path, skills)
    patch = tmp_path / "domain.patch"
    patch.write_text(hand_patch(host, change))
    result = apply(host, skills, patch, tmp_path / "workflows.patch", "v1.1.0")
    if path:
        checks.ok(result.rc == 0 and has_line(result.out, f"   staged   {path}"), f"{path} is staged", result.out)
    else:
        checks.ok(result.rc == 2 and "paths a sync may not" in result.out, "a host's own schema is refused", result.out)


def test_apply_refuses_a_git_folder(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    patch = tmp_path / "git.patch"
    patch.write_text("diff --git a/website/.git/config b/website/.git/config\nnew file mode 100644\n--- /dev/null\n+++ b/website/.git/config\n@@ -0,0 +1 @@\n+[core]\n")
    result = apply(host, skills, patch, tmp_path / "workflows.patch", "v1.1.0")
    checks.ok(result.rc == 2 and "paths a sync may not" in result.out, "a path in a .git folder is refused", result.out)
    checks.ok(not Git(host)("status", "--porcelain"), "the checkout is untouched")


def test_apply_allows_a_script_made_executable_and_refuses_a_dirty_checkout(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    (host / ".lokf" / "scripts" / "knowledge-report.sh").chmod(0o644)
    Git(host)("update-index", "--chmod=-x", ".lokf/scripts/knowledge-report.sh")
    Git(host)("commit", "-qam", "not executable")
    patch = tmp_path / "mode.patch"
    patch.write_text(hand_patch(host, _mode))
    result = apply(host, skills, patch, tmp_path / "workflows.patch", "v1.1.0")
    checks.ok(result.rc == 0, "644 to 755 is a mode a sync sets", result.out)
    result = apply(host, skills, patch, tmp_path / "workflows.patch", "v1.1.0")
    checks.ok(result.rc == 2 and "changes of its own" in result.out, "a checkout with changes is refused", result.out)


def test_every_synced_template_is_in_step_5_and_the_manifest_is_the_one_list():
    """A new template is added in two places: the manifest, which the sync script, the preflight and contract check 11 read, and ktl-sidecar's Step 5 table."""
    skill = read(SKILL)
    pairs = synced_pairs()
    assert pairs, "the manifest lists nothing"
    for template, copy in pairs:
        assert f"`templates/{template}`" in skill, f"templates/{template} is not in SKILL.md's Step 5 table"
        assert f"`{copy}`" in skill, f"{copy} is not in SKILL.md's Step 5 table"
        assert (TEMPLATES / template).is_file(), f"the manifest lists {template}, which is not a template"
    listed = {t for t, _ in pairs}
    for rule, template, _, _ in manifest():
        assert rule in ("copy", "titled", "always", "needs"), f"the manifest has a rule the script does not know: {rule}"
        assert template in listed, f"the {rule} line for {template} names a template no copy line lists"
    for name in ("github", "scripts", "m365"):
        for f in (TEMPLATES / name).rglob("*"):
            if f.is_file() and "__pycache__" not in f.parts:
                assert str(f.relative_to(TEMPLATES)) in listed, f"{f.relative_to(TEMPLATES)} is not in the manifest"
    assert "knowledge-sync.manifest" in read(PREFLIGHT), "the preflight does not read the manifest"
    assert "knowledge-sync.manifest" in read(CONTRACT), "contract check 11 does not read the manifest"
    assert "\npairs=(\n" not in read(SYNC), "the sync script carries a list of its own beside the manifest"


# The steps of knowledge-sync.yaml, which the workflow runs as --workflow <step>.

BOT = "knowledge-sync[bot]"
SUBJECT = "security(sidecar): sync copies and skills pin from v1.1.0"
needs_jq = pytest.mark.skipif(not have("jq"), reason="jq is not installed")
GH = r"""#!{python}
import json, os, subprocess, sys
args = sys.argv[1:]
here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "calls.txt"), "a") as f:
    f.write(" ".join(args) + "\n")
if args[:1] == ["api"]:
    answers = json.load(open(os.path.join(here, "answers.json")))
    answer = next((a for fragment, a in answers.items() if fragment in args[1]), None)
    if answer is None:
        sys.exit(1)
    done = subprocess.run(["jq", "-r", args[args.index("--jq") + 1]], input=json.dumps(answer), text=True, capture_output=True)
    sys.stdout.write(done.stdout)
    sys.exit(done.returncode)
if args[:2] == ["pr", "create"]:
    print("https://github.test/acme/host/pull/7")
if args[:2] == ["pr", "view"]:
    print("https://github.test/acme/host/pull/" + args[2])
"""


def pull(number, state="open", merged=False, sha="a" * 40, repo="acme/host"):
    """A pull request as GitHub lists it, with the fields the read step takes."""
    return {"number": number, "state": state, "merged_at": "2026-01-02T00:00:00Z" if merged else None, "head": {"sha": sha, "repo": {"full_name": repo}}}


def commits(*names):
    return [{"commit": {"committer": {"name": name}}} for name in names]


class Runner:
    """A job of knowledge-sync.yaml: its environment, a gh that answers from a table, and the step's outputs."""

    def __init__(self, tmp_path, skills, host, event="schedule"):
        self.host = host
        self.temp = tmp_path / "runner"
        self.temp.mkdir()
        self.bin = tmp_path / "ghbin"
        write(self.bin / "gh", GH.replace("{python}", sys.executable)).chmod(0o755)
        self.answers = {}
        origin = Git(host)("remote", "get-url", "origin")
        self.env = {
            **skills.env,
            "PATH": f"{self.bin}{os.pathsep}{os.environ['PATH']}",
            "GITHUB_OUTPUT": self.temp / "output.txt",
            "GITHUB_STEP_SUMMARY": self.temp / "summary.md",
            "GITHUB_REPOSITORY": "acme/host",
            "GITHUB_SERVER_URL": "https://github.test",
            "GITHUB_RUN_ID": "42",
            "GITHUB_EVENT_NAME": event,
            "RUNNER_TEMP": self.temp,
            "KNOWLEDGE_SYNC_INDEX_WAIT": "0",
            # Send the push address, with token t, to the host's own origin.
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": f"url.{origin}.insteadOf",
            "GIT_CONFIG_VALUE_0": "https://x-access-token:t@github.test/acme/host.git",
        }

    def step(self, name, *tag, **env):
        """Run one step. gh matches the answers in order, so the repository's own goes last."""
        write(self.bin / "answers.json", json.dumps({**self.answers, "repos/acme/host": {"default_branch": "main"}}))
        return run(["bash", ".lokf/scripts/knowledge-sync.sh", "--workflow", name, *tag], cwd=self.host, env={**self.env, **env})

    @property
    def outputs(self):
        path = self.temp / "output.txt"
        return dict(line.split("=", 1) for line in read(path).split("\n") if "=" in line) if path.exists() else {}

    @property
    def summary(self):
        path = self.temp / "summary.md"
        return read(path) if path.exists() else ""

    @property
    def calls(self):
        path = self.bin / "calls.txt"
        return read(path) if path.exists() else ""


def pin_at(skills, version):
    """pyproject.toml at a commit, as the contents API answers."""
    return {"content": base64.b64encode(pyproject(skills, version).encode()).decode()}


@needs_jq
def test_the_read_step_takes_the_newest_release_and_stops_at_a_current_pin(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    job = Runner(tmp_path, skills, host)
    job.answers = {"/pulls?head=": []}
    result = job.step("read", "")
    checks.ok(result.rc == 0 and has_line(result.out, "Syncing to v1.1.0, from v1.0.0."), "the newest release on the host's index is the tag", result.out)
    out = job.outputs
    checks.ok(out.get("tag") == "v1.1.0" and out.get("from") == "v1.0.0" and out.get("open") == "" and out.get("branch") == "", "the outputs say so", str(out))
    write(host / PYPROJECT, pyproject(skills, "1.1.0"))
    result = job.step("read", "")
    checks.ok(result.rc == 0 and "::notice::The pin is at v1.1.0 and the newest release is v1.1.0" in result.out, "a pin at the newest release has nothing to sync", result.out)
    checks.ok(job.outputs.get("tag") == "", "and the tag is empty", str(job.outputs))
    named = job.step("read", "v1.0.0")
    checks.ok(named.rc == 0 and job.outputs.get("tag") == "v1.0.0", "a tag a person names is taken as it is", named.out)
    odd = job.step("read", "main")
    checks.ok(odd.rc == 2 and "::error::'main' is not a release tag" in odd.out, "a name that is no tag is refused", odd.out)


@needs_jq
def test_the_read_step_stops_at_an_open_pull_request_for_the_same_release_and_refreshes_an_older_one(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    job = Runner(tmp_path, skills, host)
    job.answers = {"head=acme:knowledge-sync&": [pull(5)], "head=acme:sync-": [], "/contents/": pin_at(skills, "1.1.0")}
    result = job.step("read", "")
    checks.ok(result.rc == 0 and "Pull request #5 from this workflow already proposes v1.1.0" in result.out and job.outputs.get("tag") == "", "the same release, still open, stops the run", result.out)
    job.answers.update({"/contents/": pin_at(skills, "1.0.5"), "/pulls/5/commits": commits(BOT, BOT)})
    result = job.step("read", "")
    out = job.outputs
    checks.ok(out.get("tag") == "v1.1.0" and out.get("open") == "5" and out.get("open_tag") == "v1.0.5" and out.get("branch") == "a" * 40, "an older release, with the workflow's commits alone, is refreshed and leased to its commit", f"{result.out}\n{out}")
    job.answers["/pulls/5/commits"] = commits(BOT, "a person")
    result = job.step("read", "")
    checks.ok("carries a commit a person added" in result.out and job.outputs.get("tag") == "", "a person's commit on it stops the run", result.out)


@needs_jq
def test_the_read_step_leaves_a_declined_release_to_a_person_and_ignores_a_forks_branch(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    job = Runner(tmp_path, skills, host)
    job.answers = {"head=acme:knowledge-sync&": [pull(5, state="closed")], "head=acme:sync-": [], "/contents/": pin_at(skills, "1.1.0")}
    result = job.step("read", "")
    checks.ok("A person closed pull request #5, which proposed v1.1.0, without merging" in result.out and job.outputs.get("tag") == "", "the schedule proposes it no more", result.out)
    result = job.step("read", "v1.1.0", GITHUB_EVENT_NAME="workflow_dispatch")
    checks.ok(job.outputs.get("tag") == "v1.1.0" and job.outputs.get("declined") == "5", "a run a person starts takes it up again", f"{result.out}\n{job.outputs}")
    job.answers["head=acme:knowledge-sync&"] = [pull(6, repo="mallory/host")]
    result = job.step("read", "")
    checks.ok(job.outputs.get("tag") == "v1.1.0" and job.outputs.get("declined") == "", "a pull request from a fork's branch of that name does not count", f"{result.out}\n{job.outputs}")
    job.answers = {"/pulls?head=": [], "/git/ref/heads/": {"object": {"sha": "b" * 40}}, "/compare/": {"commits": commits(BOT, "a person")}}
    result = job.step("read", "")
    checks.ok("holds a commit this workflow did not make" in result.out and job.outputs.get("tag") == "", "a branch with a person's commit and no pull request is left alone", result.out)
    job.answers["/compare/"] = {"commits": commits(BOT)}
    job.step("read", "")
    checks.ok(job.outputs.get("tag") == "v1.1.0" and job.outputs.get("branch") == "b" * 40, "a branch of the workflow's own commits is leased to its tip", str(job.outputs))


def test_the_sync_step_writes_the_patch_and_says_when_nothing_changed(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    job = Runner(tmp_path, skills, host)
    result = job.step("sync", "v1.1.0")
    checks.ok(result.rc == 0 and job.outputs.get("changed") == "true", "a sync that changed files says so", result.out)
    patch = read(job.temp / "sync.patch")
    checks.ok('+    "ktl==1.1.0",' in patch and "a line the next release adds" in patch, "the patch carries the pin and the copies", patch[:400])
    checks.ok(job.summary.startswith("## Knowledge sync to v1.1.0\n\nBrings the sidecar copies"), "the report is the job's summary", job.summary[:200])
    git = Git(host)
    git("add", "-A")
    git("commit", "-qm", "synced")
    result = job.step("sync", "v1.1.0")
    checks.ok(result.rc == 0 and job.outputs.get("changed") == "false" and "::notice::The copies and the pin match v1.1.0 already" in result.out, "a host at the release has nothing to hand on", result.out)
    missing = job.step("sync", "v9.9.9")
    checks.ok(missing.rc == 2 and "no release v9.9.9 of ktl on the index" in missing.out, "an unusable release fails the step", missing.out)
    checks.ok(job.step("sync").rc == 2, "and so does a step with no tag")


def synced(job, tag="v1.1.0"):
    """The publish job's checkout: the sync step's patch in the runner's folder, and the tree as the default branch has it."""
    result = job.step("sync", tag)
    assert result.rc == 0, result.out
    git = Git(job.host)
    git("reset", "-q", "--hard")
    git("clean", "-qfd")


@needs_jq
def test_the_publish_step_pushes_the_branch_without_a_workflow_and_opens_the_pull_request(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    job = Runner(tmp_path, skills, host)
    synced(job)
    result = job.step("apply", "v1.1.0")
    checks.ok(result.rc == 0 and job.outputs.get("held") == "true", "the apply step holds the workflow the release adds", result.out)
    result = job.step("publish", "v1.1.0", SYNC_TOKEN="t", SYNC_FROM="v1.0.0")
    checks.ok(result.rc == 0 and has_line(result.out, "Opened https://github.test/acme/host/pull/7"), "exit 0, with the pull request opened", result.out)
    origin = Git(Git(host)("remote", "get-url", "origin"))
    checks.ok(origin("log", "-1", "--format=%cn|%s", "knowledge-sync") == f"{BOT}|{SUBJECT}", "the branch holds one commit, the bot's", origin("log", "--format=%cn|%s", "knowledge-sync"))
    changed = origin("diff", "--name-only", "main", "knowledge-sync").split("\n")
    checks.ok(PYPROJECT in changed and ".lokf/scripts/knowledge-report.sh" in changed, "the commit carries the pin and the copies", str(changed))
    checks.ok(not [p for p in changed if p.startswith(".github/workflows/")], "and no workflow", str(changed))
    checks.ok(f"pr create --title {SUBJECT} --body-file {job.temp / 'body.md'} --head knowledge-sync --base main" in job.calls, "the pull request goes from the branch to the default branch", job.calls)
    body = read(job.temp / "body.md")
    checks.ok("[v1.1.0](https://github.com/noelmcloughlin/knowledge-trust-ladder/compare/v1.0.0...v1.1.0), from v1.0.0." in body and "moves from v1.0.0 to v1.1.0" in body, "the body names the two releases", body)
    checks.ok("- `.lokf/scripts/knowledge-report.sh`" in body and "CHANGELOG.md has the entry" in body, "and the copies and the entry", body)
    checks.ok("### Workflow changes held for a person" in body and "- `.github/workflows/knowledge-sync.yaml`" in body, "and the held workflow, with its diff", body)
    checks.ok("gh run download 42 --repo acme/host --name knowledge-sync-workflows" in body and "git switch knowledge-sync && git pull" in body, "and the commands that apply it on the branch", body)
    checks.ok("### Workflow changes held for a person" in job.summary and "Pull request: https://github.test/acme/host/pull/7" in job.summary, "the summary shows both", job.summary)


@needs_jq
def test_the_publish_step_refreshes_an_open_pull_request_over_its_lease_alone(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    git = Git(host)
    git("push", "-q", "origin", "main:knowledge-sync")
    tip = git("rev-parse", "main")
    job = Runner(tmp_path, skills, host)
    synced(job)
    assert job.step("apply", "v1.1.0").rc == 0
    stale = job.step("publish", "v1.1.0", SYNC_TOKEN="t", SYNC_FROM="v1.0.0", SYNC_OPEN_PR="5", SYNC_OPEN_TAG="v1.0.5", SYNC_LEASE="c" * 40)
    checks.ok(stale.rc == 1 and "::error::The push was refused" in stale.out, "a branch that moved since the run read it is not written over", stale.out)
    git("checkout", "-q", "main")
    git("branch", "-qD", "knowledge-sync")
    synced(job)
    assert job.step("apply", "v1.1.0").rc == 0
    result = job.step("publish", "v1.1.0", SYNC_TOKEN="t", SYNC_FROM="v1.0.0", SYNC_OPEN_PR="5", SYNC_OPEN_TAG="v1.0.5", SYNC_LEASE=tip)
    checks.ok(result.rc == 0 and has_line(result.out, "Refreshed https://github.test/acme/host/pull/5"), "the leased branch is written over", result.out)
    checks.ok(f"pr edit 5 --title {SUBJECT}" in job.calls and "pr create" not in job.calls, "and the open pull request is edited, not opened again", job.calls)
    checks.ok("This pull request proposed v1.0.5 before." in read(job.temp / "body.md"), "the body says what it proposed before", read(job.temp / "body.md"))


def test_the_publish_step_opens_nothing_without_the_token_or_with_workflow_changes_alone(tmp_path, skills, checks):
    host = make_host(tmp_path, skills, changelog="# Changelog\n\n## [1.0.0] - 2026-01-01\n")
    job = Runner(tmp_path, skills, host)
    synced(job)
    assert job.step("apply", "v1.1.0").rc == 0
    result = job.step("publish", "v1.1.0", SYNC_FROM="v1.0.0")
    checks.ok(result.rc == 0 and "::warning::KNOWLEDGE_SYNC_TOKEN is not set" in result.out, "no token is a warning, and the run ends green", result.out)
    checks.ok("## No pull request opened" in job.summary and "pr create" not in job.calls, "nothing is opened", job.summary)
    origin = Git(Git(host)("remote", "get-url", "origin"))
    checks.ok("knowledge-sync" not in origin("branch", "--list"), "and nothing is pushed", origin("branch", "--list"))
    # A host at the release that lacks only the sync workflow: the one change is held.
    git = Git(host)
    git("reset", "-q", "--hard")
    git("clean", "-qfd")
    assert sync(host, skills).rc == 0
    (host / ".github" / "workflows" / "knowledge-sync.yaml").unlink()
    git("add", "-A")
    git("commit", "-qm", "synced, without the sync workflow")
    synced(job)
    result = job.step("apply", "v1.1.0")
    checks.ok(result.rc == 0 and job.outputs.get("held") == "true", "the workflow is held", result.out)
    result = job.step("publish", "v1.1.0", SYNC_TOKEN="t", SYNC_FROM="v1.1.0")
    checks.ok(result.rc == 0 and "::notice::v1.1.0 changes nothing here but workflows" in result.out, "a run with workflow changes alone ends green", result.out)
    checks.ok("so no pull request was opened" in job.summary and "git switch -c sync-workflows-v1.1.0" in job.summary, "and its summary says how to apply them on a branch of the person's own", job.summary)
    checks.ok("pr create" not in job.calls and "knowledge-sync" not in origin("branch", "--list"), "nothing is pushed or opened", job.calls)


def test_a_workflow_step_runs_only_inside_the_workflow(tmp_path, skills, checks):
    host = make_host(tmp_path, skills)
    result = run(["bash", ".lokf/scripts/knowledge-sync.sh", "--workflow", "sync", "v1.1.0"], cwd=host, env=skills.env, unset=("GITHUB_OUTPUT",))
    checks.ok(result.rc == 2 and "runs as a step of knowledge-sync.yaml, and GITHUB_OUTPUT is not set" in result.out, "a step with no job around it is refused", result.out)
    job = Runner(tmp_path, skills, host)
    odd = job.step("deploy", "v1.1.0")
    checks.ok(odd.rc == 2 and "takes read, sync, apply or publish" in odd.out, "and so is a step the script does not have", odd.out)
    checks.ok(not Git(host)("status", "--porcelain"), "the host is untouched")
