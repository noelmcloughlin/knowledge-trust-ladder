"""The ktl-website templates lay down a complete site, and the files a host owns are named alike everywhere.

Step 1 of the skill copies templates/website/ into a host and fills four
placeholders in two files. The copy must be complete, the bracket file name
must survive, no placeholder may remain, and `node scripts/config.mjs` must
settle the options against the host it sits in and refuse a placeholder. It
finds a LinkML project's schema pages, and its data only when asked, and
trusts no folder name a shell would read as a command. The
three files a repair never replaces are named in the skill's page, its
preflight, the contract and sync-sidecar.sh, and the four must agree. The
build itself is scripts/smoke-test-website.sh, which needs the network.
"""

from __future__ import annotations

import json
import re
import shutil

import pytest

from conftest import REPO, WEBSITE, WEBSITE_TEMPLATES, have, run, write

SITE_TEMPLATES = WEBSITE_TEMPLATES / "website"
PLACEHOLDERS = {
    "REPO_OWNER": "acme",
    "REPO_NAME": "acme-platform",
    "PROJ_NAME": "Acme Platform",
    "PROJ_DESC": "The platform Acme runs.",
}
PLACEHOLDER = re.compile(r"<(?:REPO|PROJ)_[A-Z]+>")


def template_files():
    return [p for p in SITE_TEMPLATES.rglob("*") if p.is_file()]


def lay_down(host):
    """Step 1 as the skill gives it: copy, rename the gitignore, substitute as literal text."""
    site = host / "website"
    shutil.copytree(SITE_TEMPLATES, site)
    (site / "gitignore").rename(site / ".gitignore")
    for path in site.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for token, value in PLACEHOLDERS.items():
                text = text.replace(f"<{token}>", value)
            path.write_text(text, encoding="utf-8")
    return site


def test_every_template_file_lands_and_no_placeholder_remains(tmp_path):
    site = lay_down(tmp_path)
    expected = {p.relative_to(SITE_TEMPLATES).as_posix() for p in template_files()}
    expected = {".gitignore" if f == "gitignore" else f for f in expected}
    landed = {p.relative_to(site).as_posix() for p in site.rglob("*") if p.is_file()}
    assert landed == expected
    assert (site / "src" / "pages" / "og" / "[...route].ts").is_file()
    leftovers = [p for p in site.rglob("*") if p.is_file() and PLACEHOLDER.search(p.read_text(encoding="utf-8"))]
    assert not leftovers, leftovers


def test_only_the_two_host_owned_text_files_carry_placeholders():
    carrying = sorted(
        p.relative_to(SITE_TEMPLATES).as_posix() for p in template_files() if PLACEHOLDER.search(p.read_text(encoding="utf-8"))
    )
    assert carrying == ["README.md", "site.config.mjs"]


def named_in(text, pattern):
    m = re.search(pattern, text, re.S)
    assert m, pattern
    return set(re.findall(r"[\w./-]+\.(?:mjs|md|css)", m.group(1)))


def test_the_host_owned_files_are_named_alike_everywhere():
    expected = {"site.config.mjs", "README.md", "src/styles/custom.css"}
    contract = (REPO / "scripts" / "validate-repository.sh").read_text()
    sync = (REPO / "scripts" / "sync-sidecar.sh").read_text()
    preflight = (WEBSITE / "scripts" / "website-preflight.sh").read_text()
    skill = (WEBSITE / "SKILL.md").read_text()
    assert named_in(contract, r"host_owned=\(([^)]*)\)") == expected
    assert named_in(sync, r"website_owned=\(([^)]*)\)") == expected
    assert named_in(preflight, r'case "\$rel" in ([^)]*)\)') == expected
    assert {f"website/{f}" for f in expected} <= set(re.findall(r"`(website/[\w./-]+)`", skill))


@pytest.mark.skipif(not have("node"), reason="node is not installed")
def test_config_settles_the_options_against_the_host(tmp_path):
    """A host with a bundle, a README and a changelog, and no docs folder or figures."""
    write(tmp_path / ".lokf" / "knowledge" / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(tmp_path / "README.md", "# Acme\n\nThe platform.\n")
    write(tmp_path / "CHANGELOG.md", "# Changelog\n\n## [1.0.0] - 2026-01-01\n\n- The platform.\n")
    site = lay_down(tmp_path)
    result = run(["node", "scripts/config.mjs"], cwd=site, stdout_only=True)
    assert result, f"config.mjs failed: {result.out}"
    settled = json.loads(result.out)
    assert settled["TITLE"] == "Acme Platform"
    assert settled["REPO"] == "acme/acme-platform"
    assert settled["BASE"] == "/acme-platform"
    assert settled["CHANGELOG"] == "CHANGELOG.md"
    assert settled["DOCS"] is None
    assert settled["ASSETS"] is None
    assert settled["LOGO"] == {
        "light": "website/src/assets/knowledge-trust-ladder-logo.svg",
        "dark": "website/src/assets/knowledge-trust-ladder-logo-dark.svg",
        "favicon": "website/src/assets/knowledge-trust-ladder-logo.svg",
    }
    assert settled["HOME"]["source"] == "README.md"
    assert [a["text"] for a in settled["HOME"]["actions"]] == ["Browse the bundle", "Bundle health", "Knowledge graph"]


@pytest.mark.skipif(not have("node"), reason="node is not installed")
def test_the_home_page_offers_the_architecture_page_when_the_docs_have_one(tmp_path):
    write(tmp_path / ".lokf" / "knowledge" / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(tmp_path / "docs" / "architecture.md", "# Architecture\n\nHow the platform is built.\n")
    site = lay_down(tmp_path)
    result = run(["node", "scripts/config.mjs"], cwd=site, stdout_only=True)
    assert result, f"config.mjs failed: {result.out}"
    actions = json.loads(result.out)["HOME"]["actions"]
    assert [a["text"] for a in actions] == ["Browse the bundle", "Architecture", "Bundle health", "Knowledge graph"]
    assert actions[1]["link"] == "/docs/architecture/"


@pytest.mark.skipif(not have("node"), reason="node is not installed")
def test_config_takes_the_repository_s_own_ktl_logo(tmp_path):
    """A knowledge-trust-ladder-logo.svg the repository already has wins over the site's copy."""
    write(tmp_path / ".lokf" / "knowledge" / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(tmp_path / ".assets" / "knowledge-trust-ladder-logo.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>\n')
    site = lay_down(tmp_path)
    result = run(["node", "scripts/config.mjs"], cwd=site, stdout_only=True)
    assert result, f"config.mjs failed: {result.out}"
    logo = json.loads(result.out)["LOGO"]
    assert logo == {
        "light": ".assets/knowledge-trust-ladder-logo.svg",
        "dark": ".assets/knowledge-trust-ladder-logo.svg",
        "favicon": ".assets/knowledge-trust-ladder-logo.svg",
    }


@pytest.mark.skipif(not have("node"), reason="node is not installed")
def test_config_takes_one_logo_path_as_the_light_version(tmp_path):
    write(tmp_path / ".lokf" / "knowledge" / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(tmp_path / "brand" / "acme.png", "not really a png\n")
    site = lay_down(tmp_path)
    config = site / "site.config.mjs"
    config.write_text(config.read_text(encoding="utf-8").replace('export const LOGO = "auto";', 'export const LOGO = "brand/acme.png";'), encoding="utf-8")
    result = run(["node", "scripts/config.mjs"], cwd=site, stdout_only=True)
    assert result, f"config.mjs failed: {result.out}"
    assert json.loads(result.out)["LOGO"] == {"light": "brand/acme.png", "dark": "brand/acme.png", "favicon": None}


def settle(site, **options):
    """`node scripts/config.mjs` with some options of site.config.mjs replaced, as the settled JSON."""
    config = site / "site.config.mjs"
    text = config.read_text(encoding="utf-8")
    for name, value in options.items():
        text, n = re.subn(rf"^export const {name} = .*$", f"export const {name} = {value};", text, flags=re.M)
        assert n == 1, name
    config.write_text(text, encoding="utf-8")
    result = run(["node", "scripts/config.mjs"], cwd=site, stdout_only=True)
    assert result, f"config.mjs failed: {result.out}"
    return json.loads(result.out)


def bundle(root):
    write(root / ".lokf" / "knowledge" / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")


@pytest.mark.skipif(not have("node"), reason="node is not installed")
def test_config_takes_the_schema_from_a_gen_doc_recipe_and_leaves_the_data_off(tmp_path):
    bundle(tmp_path)
    write(tmp_path / "justfile", "# The schema's pages.\n[group('docs')]\ngen-doc: gen-examples\n    gen-doc s.yaml\n\nbuild-browse:\n    python b.py\n")
    settled = settle(lay_down(tmp_path))
    assert settled["SCHEMA"] == {"dir": "docs/elements", "build": "just gen-doc"}
    assert settled["BROWSE"] is None


@pytest.mark.skipif(not have("node"), reason="node is not installed")
def test_config_finds_a_linkmo_project_and_its_data_when_asked(tmp_path):
    bundle(tmp_path)
    write(tmp_path / ".copier-answers.linkmo.yml", "_commit: v0.1.0\nlinkmo_dir: acme-linkmo\n")
    write(tmp_path / "acme-linkmo" / "justfile", "gen-doc: gen-examples\n    gen-doc s.yaml\n\nbuild-browse:\n    python b.py\n")
    write(tmp_path / ".linkml" / "justfile", "gen-doc:\n    gen-doc s.yaml\n")
    settled = settle(lay_down(tmp_path), BROWSE='"auto"')
    assert settled["SCHEMA"] == {"dir": "acme-linkmo/docs/elements", "build": "just --justfile acme-linkmo/justfile gen-doc"}
    assert settled["BROWSE"] == {"dir": "acme-linkmo/browse", "build": "just --justfile acme-linkmo/justfile build-browse"}


@pytest.mark.skipif(not have("node"), reason="node is not installed")
def test_config_takes_the_linkml_sidecar_s_schema_and_no_assignment_for_a_recipe(tmp_path):
    bundle(tmp_path)
    write(tmp_path / "justfile", 'gen-doc := "docs"\n\nbuild:\n    echo {{gen-doc}}\n')
    write(tmp_path / ".linkml" / "justfile", "gen-doc: _gen-yaml\n    uv run gen-doc -d docs/elements s.yaml\n")
    settled = settle(lay_down(tmp_path))
    assert settled["SCHEMA"] == {"dir": ".linkml/docs/elements", "build": "just --justfile .linkml/justfile gen-doc"}


@pytest.mark.skipif(not have("node"), reason="node is not installed")
def test_config_trusts_no_linkmo_folder_a_shell_would_read_as_a_command(tmp_path):
    bundle(tmp_path)
    write(tmp_path / ".copier-answers.linkmo.yml", "linkmo_dir: 'x;touch pwned'\n")
    settled = settle(lay_down(tmp_path), BROWSE='"auto"')
    assert settled["SCHEMA"] is None
    assert settled["BROWSE"] is None


@pytest.mark.skipif(not have("node"), reason="node is not installed")
def test_the_docs_pages_leave_the_schema_folder_out(tmp_path):
    bundle(tmp_path)
    write(tmp_path / "docs" / "guide.md", "# The guide\n")
    write(tmp_path / "docs" / "elements" / "index.md", "# acme\n")
    write(tmp_path / "docs" / "elements" / "Action.md", "# Class: Action\n")
    write(tmp_path / "justfile", "gen-doc:\n    gen-doc s.yaml\n")
    settled = settle(lay_down(tmp_path))
    assert settled["docsPages"] == ["guide"]


@pytest.mark.skipif(not have("node"), reason="node is not installed")
def test_config_takes_a_built_folder_and_refuses_a_missing_one_with_no_command(tmp_path):
    bundle(tmp_path)
    write(tmp_path / "data" / "acme.sqlite", "not really a database\n")
    site = lay_down(tmp_path)
    assert settle(site, BROWSE='"data"')["BROWSE"] == {"dir": "data", "build": None}
    config = site / "site.config.mjs"
    config.write_text(re.sub(r"^export const SCHEMA = .*$", 'export const SCHEMA = { dir: "schema" };', config.read_text(encoding="utf-8"), flags=re.M), encoding="utf-8")
    result = run(["node", "scripts/config.mjs"], cwd=site)
    assert not result and "no build command" in result.out, f"config.mjs accepted a missing folder: {result.out}"


@pytest.mark.skipif(not have("node"), reason="node is not installed")
def test_config_refuses_a_placeholder_left_behind(tmp_path):
    write(tmp_path / ".lokf" / "knowledge" / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    site = tmp_path / "website"
    shutil.copytree(SITE_TEMPLATES, site)
    result = run(["node", "scripts/config.mjs"], cwd=site)
    assert not result and "placeholder" in result.out, f"config.mjs accepted a placeholder: {result.out}"
