"""website-preflight.sh always ends on its summary line and exits 0, whatever the host lacks.

It runs on this repository, and on a bare directory with no bundle, no git and
no site, where every section has to cope with absence rather than fail. It:

- reads a README's title, and says when there is none;
- warns of another Pages publisher, but not of its own workflow, and names
  an mkdocs site as the one the site replaces;
- warns of a changelog with no released version;
- reads the owner and the name from the origin remote;
- names the report script the sidecar must still install;
- finds a LinkML schema at the root or under .linkml/, and a domain host's
  federation workflow;
- settles the site's folder: website/, or ktl-website/ where website/ is
  another site's, on a first run and on a rerun, and names the earlier Astro
  site as one to move.

Run under sh it stops on one line that names bash.

The rows its prerequisites page must carry for each line stay in the contract
script, check 12w: that is a fact about this repository's own pages.
"""

from __future__ import annotations

import shutil

from conftest import REPO, SCRIPTS, TEMPLATES, WEBSITE_PREFLIGHT, WEBSITE_TEMPLATES, Git, bash, matches, read, run, write


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
        and matches(result.out, r"^ok      website .*no website/ yet - Step 1 installs the site there")
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
    assert not matches(result.out, r"^info    mkdocs"), f"preflight named an mkdocs site with no mkdocs.yml: {result.out}"
    write(tmp_path / "mkdocs.yml", "site_name: acme\nsite_url: https://acme.github.io/acme-platform\n")
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^warn    pages .*deploy-docs\.yaml, mkdocs\.yml with a site_url"), f"preflight missed mkdocs' site_url: {result.out}"
    assert matches(result.out, r"^info    mkdocs +mkdocs\.yml at the root - the site replaces it: .*redirects and docsExclude"), (
        f"preflight did not name the mkdocs site the site replaces: {result.out}"
    )


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


def test_prints_no_credential_a_remote_address_carries(tmp_path):
    """The line goes to the agent and to any job log."""
    skeleton(tmp_path)
    git = Git(tmp_path)
    git.init()
    git("remote", "add", "origin", "https://oauth2:glpat-SECRETTOKEN1234567890@gitlab.example.com/acme/platform.git")
    result = preflight(tmp_path)
    assert result and "gitlab.example.com/acme/platform.git" in result.out and "SECRETTOKEN" not in result.out and "oauth2" not in result.out, (
        f"preflight printed the credential in the remote's address: {result.out}"
    )


def test_finds_a_schema_at_the_root_first_then_in_the_linkml_sidecar(tmp_path):
    skeleton(tmp_path)
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^info    schema +no src/<name>/schema/<name>\.yaml"), f"preflight found a schema in a bare host: {result.out}"
    write(tmp_path / ".linkml" / "src" / "acme" / "schema" / "acme.yaml", "id: https://acme.example/schema\nname: acme\n")
    write(tmp_path / ".linkml" / "src" / "acme" / "schema" / "other.yaml", "id: https://acme.example/other\nname: other\n")
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^ok      schema +\.linkml/src/acme/schema/acme\.yaml: the Schema part"), f"preflight missed the sidecar's schema: {result.out}"
    write(tmp_path / "src" / "platform" / "schema" / "platform.yaml", "id: https://acme.example/platform\nname: platform\n")
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^ok      schema +src/platform/schema/platform\.yaml"), f"the root's schema does not come first: {result.out}"


def test_names_a_domain_host_by_its_federation_workflow(tmp_path):
    skeleton(tmp_path)
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^info    workspace .*greys the workspace"), result.out
    write(tmp_path / ".github" / "workflows" / "knowledge-federation.yaml", "name: Knowledge federation\n")
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^ok      workspace .*a domain host"), result.out


def test_says_what_the_docs_folder_gives_the_home_page(tmp_path):
    skeleton(tmp_path)
    write(tmp_path / "docs" / "guide.md", "# The guide\n")
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^ok      docs .*no architecture\.md.*; 0 retelling"), result.out
    write(tmp_path / "docs" / "architecture.md", "# Architecture\n")
    write(tmp_path / "docs" / "architecture.en-simple.md", "# Architecture, in short\n")
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^ok      docs .*architecture\.md, the home page's Architecture button; 1 retelling"), result.out


def install(root, folder):
    """The site as Step 1 leaves it, placeholders filled."""
    site = root / folder
    shutil.copytree(WEBSITE_TEMPLATES / "website", site)
    (site / "gitignore").rename(site / ".gitignore")
    for name in ("site.toml", "README.md"):
        text = (site / name).read_text(encoding="utf-8")
        for token in ("REPO_OWNER", "REPO_NAME", "PROJ_NAME", "PROJ_DESC"):
            text = text.replace(f"<{token}>", "acme")
        (site / name).write_text(text, encoding="utf-8")
    return site


def test_installs_beside_another_site_s_website_folder_and_finds_its_own_on_a_rerun(tmp_path):
    skeleton(tmp_path)
    write(tmp_path / "website" / "index.html", "<p>another site</p>\n")
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^info    website +website/ exists and is not this skill's .* installs the site in ktl-website/ instead"), (
        f"preflight did not send the site to ktl-website/: {result.out}"
    )
    assert "(no site.toml or hugo.toml)" in result.out, result.out
    assert not matches(result.out, r"^missing website"), f"another site's folder stopped the skill: {result.out}"
    write(tmp_path / "website" / "site.toml", "")
    result = preflight(tmp_path)
    assert result and "website/ exists and is not this skill's (no hugo.toml)" in result.out, f"the message named a file that is there: {result.out}"
    (tmp_path / "website" / "site.toml").unlink()
    site = install(tmp_path, "ktl-website")
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^ok      website +ktl-website/ installed, and its files match"), f"the rerun missed ktl-website/: {result.out}"
    (site / "hugo.toml").write_text(read(site / "hugo.toml") + "# an edit\n")
    (site / "layouts" / "404.html").unlink()
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^warn    website +ktl-website/ installed; differs from the templates: hugo\.toml, layouts/404\.html \(missing\)"), result.out
    assert "site.toml" not in result.out.split("differs from the templates:")[1].splitlines()[0], "a host-owned file is never compared"


def test_prefers_website_when_it_is_this_skill_s_and_warns_of_a_placeholder(tmp_path):
    skeleton(tmp_path)
    install(tmp_path, "website")
    (tmp_path / "ktl-website").mkdir()
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^ok      website +website/ installed"), result.out
    shutil.copy(WEBSITE_TEMPLATES / "website" / "site.toml", tmp_path / "website" / "site.toml")
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^warn    website +website/site\.toml still holds a <PLACEHOLDER>"), result.out


def test_names_the_earlier_astro_site_as_one_to_move_and_two_foreign_folders_as_a_stop(tmp_path):
    skeleton(tmp_path)
    write(tmp_path / "website" / "site.config.mjs", 'export const TITLE = "Acme";\n')
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^warn    website +website/ is this skill's earlier Astro site"), result.out
    (tmp_path / "website" / "site.config.mjs").unlink()
    (tmp_path / "ktl-website").mkdir()
    result = preflight(tmp_path)
    assert result and matches(result.out, r"^missing website +ktl-website/ exists and is not this skill's") and "Step 1 and every step after it" in result.out, result.out


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
