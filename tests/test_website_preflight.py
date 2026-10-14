"""website-preflight.sh always ends on its summary line and exits 0, whatever the host lacks.

It runs on this repository, and on a bare directory with no bundle, no git and
no site, where every section has to cope with absence rather than fail. It:

- reads a README's title, and says when there is none;
- warns of another Pages publisher, but not of its own workflow;
- warns of a changelog with no released version;
- reads the owner and the name from the origin remote;
- names the report script the sidecar must still install;
- finds a linkmo project's gen-doc and build-browse recipes, in a justfile of
  any name just reads and with parameters, but not an assignment of the same
  name.

Run under sh it stops on one line that names bash.

The rows its prerequisites page must carry for each line stay in the contract
script, check 12w: that is a fact about this repository's own pages.
"""

from __future__ import annotations

import shutil

from conftest import REPO, SCRIPTS, TEMPLATES, WEBSITE_PREFLIGHT, WEBSITE_TEMPLATES, Git, bash, matches, run, write


def preflight(*args, cwd=None):
    return bash(WEBSITE_PREFLIGHT, *args, cwd=cwd)


def skeleton(root):
    """A host with the sidecar's dummy bundle and its report script, and nothing else."""
    shutil.copytree(TEMPLATES / "knowledge", root / ".lokf" / "knowledge")
    (root / ".lokf" / "scripts").mkdir()
    shutil.copy(SCRIPTS / "knowledge-report.sh", root / ".lokf" / "scripts")
    return root


def test_runs_on_this_repository_and_ends_on_its_summary_line():
    result = preflight(".", cwd=REPO)
    assert result and matches(result.out, r"^Preflight: "), f"preflight failed on this repository: {result.out}"


def test_copes_with_a_bare_directory(tmp_path):
    result = preflight(cwd=tmp_path)
    assert (
        result
        and matches(result.out, r"^missing bundle")
        and matches(result.out, r"^info    git ")
        and matches(result.out, r"^ok      website .*no website/ yet")
        and matches(result.out, r"^Preflight: ")
    ), f"preflight misbehaves on a bare directory: {result.out}"


def test_reads_a_readme_title_and_says_when_there_is_none(tmp_path):
    skeleton(tmp_path)
    write(tmp_path / "README.md", "# Acme\n\nThe platform.\n")
    result = preflight(tmp_path)
    assert result and matches(result.out, r'^ok      readme .*titled "Acme"'), f"preflight missed the title: {result.out}"
    write(tmp_path / "README.md", "Acme\n\nThe platform.\n")
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^warn    readme .*no '# ' title"), f"preflight missed the missing title: {result.out}"


def test_warns_of_another_pages_publisher(tmp_path):
    skeleton(tmp_path)
    write(
        tmp_path / ".github" / "workflows" / "deploy-docs.yaml",
        "name: docs\non: push\njobs:\n  d:\n    runs-on: ubuntu-latest\n    steps:\n      - run: mkdocs gh-deploy --force\n",
    )
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^warn    pages .*deploy-docs\.yaml"), f"preflight missed the publisher: {result.out}"


def test_leaves_its_own_workflow_out_of_the_publishers(tmp_path):
    skeleton(tmp_path)
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    shutil.copy(WEBSITE_TEMPLATES / "github" / "knowledge-website.yaml", tmp_path / ".github" / "workflows")
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^ok      pages "), f"preflight took its own workflow for a publisher: {result.out}"


def test_warns_of_a_changelog_with_no_released_version(tmp_path):
    skeleton(tmp_path)
    write(tmp_path / "CHANGELOG.md", "# Changelog\n\n## [Unreleased]\n\n- Something.\n")
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^warn    changelog .*no '## \[version\] - date' heading"), (
        f"preflight missed the unreleased changelog: {result.out}"
    )
    write(tmp_path / "CHANGELOG.md", "# Changelog\n\n## [1.0.0] - 2026-01-01\n\n- Something.\n")
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^ok      changelog .*1 released version"), f"preflight missed the release: {result.out}"


def test_reads_the_owner_and_the_name_from_the_remote(tmp_path):
    skeleton(tmp_path)
    git = Git(tmp_path)
    git.init()
    git("remote", "add", "origin", "git@github.com:acme/acme-platform.git")
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^ok      git .*acme/acme-platform"), f"preflight misread the remote: {result.out}"


def test_finds_a_linkmo_project_s_schema_and_data_recipes(tmp_path):
    skeleton(tmp_path)
    write(tmp_path / ".copier-answers.linkmo.yml", "linkmo_dir: acme-linkmo\nproject_slug: acme\n")
    write(tmp_path / "acme-linkmo" / "justfile", "gen-doc: gen-examples\n    gen-doc x\n\nbuild-browse:\n    python b.py\n")
    result = preflight(tmp_path)
    assert result and matches(
        result.out, r"^ok      schema .*acme-linkmo/docs/elements.*just --justfile acme-linkmo/justfile gen-doc"
    ), f"preflight missed linkmo's gen-doc recipe: {result.out}"
    assert matches(result.out, r"^info    data .*just --justfile acme-linkmo/justfile build-browse"), (
        f"preflight missed linkmo's build-browse recipe: {result.out}"
    )
    assert matches(result.out, r"^(ok|warn) +just "), f"preflight did not say whether just is installed: {result.out}"


def test_reads_a_justfile_by_any_name_just_reads_and_a_recipe_with_parameters(tmp_path):
    skeleton(tmp_path)
    write(tmp_path / ".linkml" / ".justfile", 'gen-doc dir="docs/elements": _gen-yaml\n    uv run gen-doc -d {{dir}} s.yaml\n')
    result = preflight(tmp_path)
    assert result and matches(
        result.out, r"^ok      schema .*\.linkml/docs/elements.*just --justfile \.linkml/\.justfile gen-doc"
    ), f"preflight missed a recipe with a parameter in .justfile: {result.out}"
    write(tmp_path / "Justfile", "build-browse *ARGS:\n    python b.py {{ARGS}}\n")
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^info    data .*\(just build-browse\)"), f"preflight missed the Justfile: {result.out}"


def test_takes_no_assignment_for_a_recipe(tmp_path):
    skeleton(tmp_path)
    write(tmp_path / "justfile", 'gen-doc := "docs"\n\nbuild:\n    echo {{gen-doc}}\n')
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^info    schema .*no justfile with a gen-doc recipe"), (
        f"preflight read an assignment as a recipe: {result.out}"
    )
    assert not matches(result.out, r"^(ok|warn) +just "), f"preflight asked for just with no recipe to run: {result.out}"


def test_names_the_report_script_the_sidecar_must_lay_down(tmp_path):
    shutil.copytree(TEMPLATES / "knowledge", tmp_path / ".lokf" / "knowledge")
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^missing report ") and "Step 4's build" in result.out, (
        f"preflight did not name the missing report script: {result.out}"
    )


def test_run_under_sh_stops_and_names_bash():
    result = run(["sh", WEBSITE_PREFLIGHT, "x"])
    assert not result, f"the preflight run under sh did not stop: {result.out}"
    assert matches(result.out, r"^run this with bash"), f"the preflight run under sh failed some other way: {result.out}"
