"""The ktl-website templates lay down a complete site, and the files a host owns are named alike everywhere.

Step 1 of the skill copies templates/website/ into a host and fills four
placeholders in two files. The copy must be complete, the bracket file name
must survive, no placeholder may remain, and `node scripts/config.mjs` must
settle the options against the host it sits in and refuse a placeholder. It
finds a LinkML project's schema pages in a justfile of any name just reads,
and its data only when asked. It trusts no folder name a shell would read as
a command, and refuses gen-doc's subfolders, two metadata files and a
database caught mid-write.

A docs page's address is the one Starlight gives it, DOCS.exclude keeps a
folder off the site, and REDIRECTS follows the schema's pages. The three
files a repair never replaces are named in the skill's page, its preflight,
the contract and the sidecar's knowledge-sync.sh, and the four must agree.
The build itself is scripts/smoke-test-website.sh, which needs the network.
"""

from __future__ import annotations

import json
import re
import shutil

import pytest

from conftest import REPO, TEMPLATES, WEBSITE, WEBSITE_TEMPLATES, have, read, run, write

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
    sync = (REPO / "skills" / "ktl-sidecar" / "templates" / "scripts" / "knowledge-sync.sh").read_text()
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


def configure(site, stdout_only=False, **options):
    """`node scripts/config.mjs` with some options of site.config.mjs replaced, as its result."""
    config = site / "site.config.mjs"
    text = config.read_text(encoding="utf-8")
    for name, value in options.items():
        text, n = re.subn(rf"^export const {name} = .*$", lambda _: f"export const {name} = {value};", text, flags=re.M)
        assert n == 1, name
    config.write_text(text, encoding="utf-8")
    return run(["node", "scripts/config.mjs"], cwd=site, stdout_only=stdout_only)


def settle(site, **options):
    """`configure`, as the settled JSON."""
    result = configure(site, stdout_only=True, **options)
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
def test_docs_exclude_keeps_a_folder_off_and_refuses_a_path_that_names_nothing(tmp_path):
    bundle(tmp_path)
    for name in ("index", "guide", "templates-linkml/README", "notes/draft"):
        write(tmp_path / "docs" / f"{name}.md", "# A page\n")
    site = lay_down(tmp_path)
    assert settle(site)["docsPages"] == ["guide", "index", "notes/draft", "templates-linkml/README"]
    assert settle(site, DOCS='{ exclude: ["templates-linkml/", "notes/draft.md"] }')["docsPages"] == ["guide", "index"]
    result = configure(site, DOCS='{ exclude: ["template-linkml"] }')
    assert not result and "DOCS.exclude names template-linkml" in result.out, f"config.mjs took an exclude that names nothing: {result.out}"


@pytest.mark.skipif(not have("node"), reason="node is not installed")
def test_a_docs_page_s_address_is_the_one_starlight_gives_it(tmp_path):
    bundle(tmp_path)
    write(tmp_path / "docs" / "index.md", "# Home\n")
    write(tmp_path / "docs" / "Getting Started.md", "# Start\n")
    site = lay_down(tmp_path)
    names = ["index", "guide", "how-to/index", "templates-linkml/README", "Getting Started"]
    result = evaluate(site, f"{json.dumps(names)}.map(config.docsRoute)")
    assert result, f"docsRoute failed: {result.out}"
    assert value(result) == ["/docs/", "/docs/guide/", "/docs/how-to/", "/docs/templates-linkml/readme/", "/docs/getting-started/"]
    script = "import { route } from './scripts/routes.mjs'; console.log(JSON.stringify(['docs/index.md', 'docs/Getting Started.md'].map(route)));"
    result = run(["node", "--input-type=module", "-e", script], cwd=site)
    assert result and value(result) == ["/acme-platform/docs/", "/acme-platform/docs/getting-started/"], f"a link to a docs page missed it: {result.out}"


@pytest.mark.skipif(not have("node"), reason="node is not installed")
def test_redirects_take_the_base_and_follow_the_schema_s_pages(tmp_path):
    bundle(tmp_path)
    write(tmp_path / "docs" / "elements" / "index.md", "# acme\n")
    write(tmp_path / "docs" / "elements" / "Service.md", "# Class: Service\n")
    write(tmp_path / "docs" / "elements" / "Status.md", "# Enum: Status\n")
    write(tmp_path / "justfile", "gen-doc:\n    gen-doc s.yaml\n")
    site = lay_down(tmp_path)
    assert settle(site)["redirects"] == {}
    old = '{ "/elements": "/schema/", "/elements/[...slug]": "/schema/[...slug]", "/about": "/docs/about/" }'
    assert settle(site, REDIRECTS=old)["redirects"] == {
        "/elements": "/acme-platform/schema/",
        "/elements/Service": "/acme-platform/schema/Service/",
        "/elements/Status": "/acme-platform/schema/Status/",
        "/about": "/acme-platform/docs/about/",
    }
    result = configure(site, REDIRECTS='{ "/elements/[...slug]": "/schema/" }')
    assert not result and "or neither does" in result.out, f"config.mjs took a slug with one end: {result.out}"
    result = configure(site, REDIRECTS='{ "/a/[...slug]": "/b/[...slug]" }', SCHEMA="null")
    assert not result and "shows no schema" in result.out, f"config.mjs took a slug with no schema: {result.out}"


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


def evaluate(site, expression):
    """An expression over scripts/config.mjs's exports, as `config.<name>`, run by node; its value is the last line, as JSON."""
    script = f"import * as config from './scripts/config.mjs'; console.log(JSON.stringify({expression}));"
    return run(["node", "--input-type=module", "-e", script], cwd=site)


def value(result):
    """The value `evaluate` printed, after whatever git said about a host that is not a repository."""
    return json.loads(result.out.splitlines()[-1])


@pytest.mark.skipif(not have("node"), reason="node is not installed")
def test_config_reads_a_justfile_by_any_name_just_reads_and_a_recipe_with_parameters(tmp_path):
    bundle(tmp_path)
    write(tmp_path / ".linkml" / ".justfile", 'gen-doc dir="docs/elements": _gen-yaml\n    uv run gen-doc -d {{dir}} s.yaml\n')
    site = lay_down(tmp_path)
    assert settle(site)["SCHEMA"] == {"dir": ".linkml/docs/elements", "build": "just --justfile .linkml/.justfile gen-doc"}
    write(tmp_path / "Justfile", "gen-doc *ARGS:\n    gen-doc {{ARGS}} s.yaml\n")
    assert settle(site)["SCHEMA"] == {"dir": "docs/elements", "build": "just gen-doc"}


@pytest.mark.skipif(not have("node"), reason="node is not installed")
def test_the_schema_pages_come_from_one_flat_folder_and_gen_doc_s_subfolders_stop_the_build(tmp_path):
    bundle(tmp_path)
    write(tmp_path / "docs" / "elements" / "index.md", "# acme\n")
    write(tmp_path / "docs" / "elements" / "Service.md", "---\nsearch:\n  boost: 10.0\n---\n\n# Class: Service \n")
    write(tmp_path / "docs" / "elements" / "String.md", "---\nsearch:\n  boost: 1.0\n---# Type: String \n")
    write(tmp_path / "docs" / "elements" / "acme.md", "# acme \n")
    site = lay_down(tmp_path)
    settle(site, SCHEMA='{ dir: "docs/elements", build: null }')
    result = evaluate(site, "config.schemaPages().map((p) => [p.name, p.label, p.kind])")
    assert result, f"schemaPages failed: {result.out}"
    assert value(result) == [["acme", "acme", None], ["Service", "Service", "Class"], ["String", "String", "Type"]]
    for name in ("Service.md", "String.md", "acme.md"):
        (tmp_path / "docs" / "elements" / name).unlink()
    write(tmp_path / "docs" / "elements" / "classes" / "Service.md", "# Class: Service\n")
    result = evaluate(site, "config.schemaPages()")
    assert not result and "--subfolder-type-separation" in result.out, f"schemaPages took gen-doc's subfolders: {result.out}"


@pytest.mark.skipif(not have("node"), reason="node is not installed")
def test_the_data_is_its_databases_and_one_metadata_file_and_a_torn_copy_stops_the_build(tmp_path):
    bundle(tmp_path)
    data = tmp_path / "data"
    for name in ("acme.sqlite", "audit.db", "notes.txt", "metadata.yaml"):
        write(data / name, "stand-in\n")
    site = lay_down(tmp_path)
    settle(site, BROWSE='"data"')
    result = evaluate(site, "config.browseFiles()")
    assert result, f"browseFiles failed: {result.out}"
    assert value(result) == {
        "databases": [{"file": "acme.sqlite", "name": "acme"}, {"file": "audit.db", "name": "audit"}],
        "metadata": "metadata.yaml",
    }
    write(data / "acme.sqlite-wal", b"")
    assert evaluate(site, "config.browseFiles()"), "an empty journal stopped the build"
    write(data / "acme.sqlite-wal", b"\x37\x7f\x06\x82")
    result = evaluate(site, "config.browseFiles()")
    assert not result and "could be torn" in result.out, f"browseFiles copied a database mid-write: {result.out}"
    (data / "acme.sqlite-wal").unlink()
    write(data / "metadata.json", "{}\n")
    result = evaluate(site, "config.browseFiles()")
    assert not result and "Datasette reads one" in result.out, f"browseFiles chose between two metadata files: {result.out}"


@pytest.mark.skipif(not have("node"), reason="node is not installed")
def test_config_refuses_a_placeholder_left_behind(tmp_path):
    write(tmp_path / ".lokf" / "knowledge" / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    site = tmp_path / "website"
    shutil.copytree(SITE_TEMPLATES, site)
    result = run(["node", "scripts/config.mjs"], cwd=site)
    assert not result and "placeholder" in result.out, f"config.mjs accepted a placeholder: {result.out}"


@pytest.mark.skipif(not have("node"), reason="node is not installed")
def test_config_offers_the_workspace_on_a_domain_host_alone(tmp_path):
    """A host with the knowledge-federation workflow is a domain host, whose graph page offers the workspace the workflow serves."""
    write(tmp_path / ".lokf" / "knowledge" / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    site = lay_down(tmp_path)
    settled = json.loads(run(["node", "scripts/config.mjs"], cwd=site, stdout_only=True).out)
    assert settled["WORKSPACE"] is None, "a bundle that is no domain has no workspace"
    write(tmp_path / ".github" / "workflows" / "knowledge-federation.yaml", "name: Knowledge federation\n")
    settled = json.loads(run(["node", "scripts/config.mjs"], cwd=site, stdout_only=True).out)
    assert settled["WORKSPACE"] == "workspace"
    base = settled["BASE"]
    assert settled["workspace"] == {"folder": "workspace", "graph": f"{base}/workspace/graph.json", "index": f"{settled['SITE']}{base}/workspace/index.md"}, \
        "the graph page fetches graph.json under the site's base, where the workflow serves it"
    config = site / "site.config.mjs"
    config.write_text(config.read_text(encoding="utf-8").replace('export const WORKSPACE = "auto";', "export const WORKSPACE = null;"), encoding="utf-8")
    settled = json.loads(run(["node", "scripts/config.mjs"], cwd=site, stdout_only=True).out)
    assert settled["WORKSPACE"] is None and settled["workspace"] is None
    config.write_text(config.read_text(encoding="utf-8").replace("export const WORKSPACE = null;", 'export const WORKSPACE = "ws";'), encoding="utf-8")
    result = run(["node", "scripts/config.mjs"], cwd=site)
    assert not result and 'WORKSPACE must be "auto", true or null, since the federation workflow serves the workspace at workspace/' in result.out, result.out


def test_the_workspace_folder_is_the_one_the_federation_workflow_serves():
    """The graph page fetches workspace/graph.json, so the workflow copies the snapshot to workspace/ under the site, and the build names that address."""
    workflow = read(TEMPLATES / "github" / "knowledge-federation.yaml")
    assert 'cp -R snapshot "$dist/workspace"' in workflow
    assert '/workspace"' in read(TEMPLATES / "scripts" / "knowledge-federate.py")


def test_the_workspace_view_links_a_node_only_to_an_http_iri():
    """A member writes its concepts' ids, so the graph page links an id only when it is an http or https address, never javascript: or another scheme."""
    component = read(SITE_TEMPLATES / "src" / "components" / "KnowledgeGraph.astro")
    assert "if (workspace ? /^https?:\\/\\//i.test(String(d.id)) : !!d.concept_id) {" in component
    assert "page.href = workspace ? d.id" in component


RAW_HTML_CASES = {
    # Passed as they are: what the repositories' own pages use.
    '<picture><source media="(prefers-color-scheme: dark)" srcset="a-dark.svg"><img src="a.svg" alt="A" width="600"></picture>':
        '<picture><source media="(prefers-color-scheme: dark)" srcset="a-dark.svg"><img src="a.svg" alt="A" width="600"></picture>',
    '<p align="center"><a href="https://w3id.org/ktl/">KTL</a></p>': '<p align="center"><a href="https://w3id.org/ktl/">KTL</a></p>',
    "<details>": "<details>",
    "</details>": "</details>",
    "<!-- a note -->": "<!-- a note -->",
    # Kept, with what GitHub drops dropped.
    '<img src="badge.svg" style="height:20px" onerror="alert(1)">': '<img src="badge.svg">',
    '<a href="javascript:alert(1)">x</a>': "<a>x</a>",
    '<a href="jav&#x09;ascript:alert(1)">x</a>': "<a>x</a>",
    '<img srcset="ok.png 1x, data:image/svg+xml,x 2x">': "<img>",
    # Shown as text.
    "<script>alert(1)</script>": None,
    "<iframe src=https://example.test></iframe>": None,
    '<img src=x onerror=alert(1)>': None,
    "<svg onload=alert(1)>": None,
    "<id>": None,
    "<!-- open": None,
}


@pytest.mark.skipif(not have("node"), reason="node is not installed")
def test_raw_html_passes_only_as_github_renders_it(tmp_path):
    """A tag GitHub allows keeps the attributes it allows, an unsafe address is dropped, and anything else is shown as text."""
    cases = write(tmp_path / "cases.json", json.dumps(list(RAW_HTML_CASES)))
    script = write(tmp_path / "check.mjs",
                   f"import {{ readFileSync }} from 'node:fs';\n"
                   f"import {{ cleanRawHtml }} from {json.dumps(str(SITE_TEMPLATES / 'scripts' / 'raw-html.mjs'))};\n"
                   f"console.log(JSON.stringify(JSON.parse(readFileSync({json.dumps(str(cases))}, 'utf8')).map((f) => cleanRawHtml(f).html)));\n")
    result = run(["node", script], stdout_only=True)
    got = dict(zip(RAW_HTML_CASES, json.loads(result.out)))
    for fragment, want in RAW_HTML_CASES.items():
        assert got[fragment] == want, (fragment, got[fragment])


def test_the_markdown_plugin_checks_raw_html_on_every_page():
    plugin = read(SITE_TEMPLATES / "scripts" / "markdown-ktl.mjs")
    assert 'if (!source) return { name: "ktl-raw-html", html:' in plugin, "a page the sync did not write still gets the raw HTML check"
    assert "cleanHtmlNode(node, ctx, source, rewriteHtml(source, node.value))" in plugin
    assert "cleanHtmlNode" in read(SITE_TEMPLATES / "scripts" / "sync.mjs"), "the feed's HTML gets the same check"
