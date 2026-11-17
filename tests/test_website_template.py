"""The ktl-website templates install a complete site, and the files a host owns are named alike everywhere.

Step 1 of the skill copies templates/website/ into a host and fills four
placeholders in two files. The copy must be complete, no placeholder may
remain, and the build must refuse a site.toml that still holds one. The
tests run the snippet SKILL.md gives for the placeholders, so a value is
written as a TOML string and a value with a line break is refused. The site
takes no setting for what it shows: hugo.toml mounts each input from where a
repository keeps it, and a mount that finds nothing draws nothing, so the
mounts are the list of what the site can find.

The three files a repair never replaces are named in the skill's page, its
preflight, the contract and the sidecar's knowledge-sync.sh, and the four
must agree. The site's folder is website/, or ktl-website/ where website/ is
another site's, and the workflows and the sync look in both.

The site's plain Python is tested here: the link check, the cleaning of raw
HTML, the SVG check and the reading of site.toml. prepare.sh runs as far as
`lokf export`, under a uv that runs each command as it is. The build itself
is scripts/smoke-test-website.sh, which needs the network.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

from conftest import REPO, TEMPLATES, WEBSITE, WEBSITE_TEMPLATES, bash, read, run, write

SITE_TEMPLATES = WEBSITE_TEMPLATES / "website"
PLACEHOLDERS = {
    "REPO_OWNER": "acme",
    "REPO_NAME": "acme-platform",
    "PROJ_NAME": "Acme Platform",
    "PROJ_DESC": "The platform Acme runs.",
}
PLACEHOLDER = re.compile(r"<(?:REPO|PROJ)_[A-Z]+>")
BINARY = {".woff2", ".png"}
OWNED = {"site.toml", "README.md", "assets/css/custom.css"}


def template_files():
    return [p for p in SITE_TEMPLATES.rglob("*") if p.is_file()]


def text_files():
    return [p for p in template_files() if p.suffix not in BINARY]


def step_one(host, folder="website", **values):
    """The snippet SKILL.md gives for the placeholders, run in the host as written, on the site's folder."""
    found = re.search(r"```bash\n(export REPO_OWNER REPO_NAME PROJ_NAME PROJ_DESC\n.*?)```", read(WEBSITE / "SKILL.md"), re.S)
    assert found, "SKILL.md's Step 1 still gives the snippet that fills the placeholders"
    script = found.group(1).replace("website/", f"{folder}/")
    path = f"{Path(sys.executable).parent}{os.pathsep}{os.environ['PATH']}"
    return run(["bash", "-c", script], cwd=host, env={**PLACEHOLDERS, **values, "PATH": path})


def lay_down(host, folder="website", **values):
    """Step 1 as the skill gives it: copy, rename the gitignore, fill the placeholders in the two files."""
    site = host / folder
    shutil.copytree(SITE_TEMPLATES, site)
    (site / "gitignore").rename(site / ".gitignore")
    filled = step_one(host, folder, **values)
    assert filled, filled.out
    return site


def test_every_template_file_lands_and_no_placeholder_remains(tmp_path):
    site = lay_down(tmp_path)
    expected = {p.relative_to(SITE_TEMPLATES).as_posix() for p in template_files()}
    expected = {".gitignore" if f == "gitignore" else f for f in expected}
    landed = {p.relative_to(site).as_posix() for p in site.rglob("*") if p.is_file()}
    assert landed == expected
    leftovers = [p for p in site.rglob("*") if p.is_file() and p.suffix not in BINARY and PLACEHOLDER.search(p.read_text(encoding="utf-8"))]
    assert not leftovers, leftovers


def test_only_the_two_host_owned_text_files_carry_placeholders():
    carrying = sorted(p.relative_to(SITE_TEMPLATES).as_posix() for p in text_files() if PLACEHOLDER.search(p.read_text(encoding="utf-8")))
    assert carrying == ["README.md", "site.toml"]


def test_the_template_holds_nothing_of_one_repository_or_of_a_build():
    """The same files go into every host, so none names this repository, and none is what a build writes."""
    for path in text_files():
        text = path.read_text(encoding="utf-8")
        assert "noelmcloughlin" not in text, path
    names = {p.relative_to(SITE_TEMPLATES).parts[0] for p in template_files()}
    assert not names & {"dist", "generated", "resources", ".venv", "public", "node_modules", "data"}, names
    ignored = read(SITE_TEMPLATES / "gitignore")
    for folder in ("dist/", "generated/", "resources/", ".venv/", "static/pagefind/"):
        assert folder in ignored.splitlines(), folder


def named_in(text, pattern):
    m = re.search(pattern, text, re.S)
    assert m, pattern
    return set(re.findall(r"[\w./-]+\.(?:toml|md|css)", m.group(1)))


def test_the_host_owned_files_are_named_alike_everywhere():
    contract = (REPO / "scripts" / "validate-repository.sh").read_text()
    sync = (TEMPLATES / "scripts" / "knowledge-sync.sh").read_text()
    preflight = (WEBSITE / "scripts" / "website-preflight.sh").read_text()
    skill = (WEBSITE / "SKILL.md").read_text()
    assert named_in(contract, r"host_owned=\(([^)]*)\)") == OWNED
    assert named_in(sync, r"website_owned=\(([^)]*)\)") == OWNED
    assert named_in(preflight, r'case "\$rel" in ([^)]*)\)') == OWNED
    assert {f"website/{f}" for f in OWNED} <= set(re.findall(r"`(website/[\w./-]+)`", skill))
    for name in OWNED:
        assert (SITE_TEMPLATES / name).is_file(), f"a host-owned file still needs its template: {name}"


def test_site_toml_is_valid_toml_once_filled_and_sets_only_what_a_site_must(tmp_path):
    site = lay_down(tmp_path)
    settled = tomllib.loads(read(site / "site.toml"))
    assert settled == {
        "baseURL": "https://acme.github.io/acme-platform/",
        "title": "Acme Platform",
        "params": {"description": "The platform Acme runs.", "repo": "https://github.com/acme/acme-platform"},
    }, "every other value is found in the repository or has a default in hugo.toml"
    shared = tomllib.loads(read(site / "hugo.toml"))
    assert not {"baseURL", "title"} & set(shared), "hugo.toml is the same on every site"
    assert not {"description", "repo", "logo", "docsGroups", "redirects"} & set(shared["params"])
    assert shared["publishDir"] == "dist", "the workflows upload <site>/dist"


def test_the_build_refuses_a_placeholder_left_behind(tmp_path):
    write(tmp_path / ".lokf" / "knowledge" / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    site = tmp_path / "website"
    shutil.copytree(SITE_TEMPLATES, site)
    result = bash(site / "scripts" / "build.sh")
    assert not result and "site.toml still holds a <PLACEHOLDER>" in result.out, f"build.sh took a placeholder: {result.out}"
    assert not (site / "generated").exists(), "it stopped before it wrote anything"


def test_step_one_writes_a_value_as_a_toml_string_and_refuses_a_line_break(tmp_path):
    """The description comes from the bundle or the README, which a model may have written, and prepare.sh runs site.toml's browseBuild."""
    spoken = 'Acme\'s "platform" \N{EM DASH} with C:\\tools.'
    site = lay_down(tmp_path / "quoted", PROJ_NAME='The "Acme" Platform', PROJ_DESC=spoken)
    settled = tomllib.loads(read(site / "site.toml"))
    assert settled["title"] == 'The "Acme" Platform' and settled["params"]["description"] == spoken, settled
    assert read(site / "README.md").startswith('# The The "Acme" Platform website\n'), "the README takes the value as it is"

    for name, value in (
        ("a line break", 'The platform."\nbrowseBuild = "touch pwned'),
        ("a carriage return", "The platform.\rbrowseBuild = 1"),
        ("a character that does not print", "The platform." + chr(0x200B)),
    ):
        host = tmp_path / name.replace(" ", "-")
        shutil.copytree(SITE_TEMPLATES, host / "website")
        before = read(host / "website" / "site.toml")
        refused = step_one(host, PROJ_DESC=value)
        assert not refused and "PROJ_DESC: line break or unprintable character" in refused.out, f"Step 1 took {name}: {refused.out}"
        assert read(host / "website" / "site.toml") == before and "<PROJ_NAME>" in read(host / "website" / "README.md"), "it wrote neither file"


def site_values(tmp_path, text):
    return run([sys.executable, "-I", str(SITE_TEMPLATES / "scripts" / "site-values.py"), str(write(tmp_path / "site.toml", text))])


def test_prepare_reads_site_toml_as_hugo_does(tmp_path):
    """A TOML parser reads the file, so a line is a key only where TOML says it is, and a file Hugo would read another way stops the build."""
    site = lay_down(tmp_path)
    result = run([sys.executable, "-I", str(site / "scripts" / "site-values.py"), str(site / "site.toml")])
    assert result and result.out == "repo=https://github.com/acme/acme-platform", result.out
    result = site_values(tmp_path, 'title = "Acme"\nbrowseBuild = "not under params"\n[params]\n# browseBuild = "just build-browse"\ndescription = """\nA long one.\nbrowseBuild = "touch pwned"\n"""\n'
                         "repo = 'https://github.com/acme/acme-platform'\nBranch = \"trunk\"\nparams.unused = 1\n\"browse\" = \"data/browse\"\nsource = \".linkml/\"\n")
    assert result and result.out.splitlines() == ["repo=https://github.com/acme/acme-platform", "branch=trunk", "source=.linkml/", "browse=data/browse"], result.out
    for text, message in (
        ('[params]\nrepo = "a"\nbrowseBuild = "just x"\nbrowseBuild = "touch pwned"\n', "cannot be read as TOML"),
        ('[params]\nrepo = "a"\nbrowseBuild = "just x"\nbrowsebuild = "touch pwned"\n', "sets both browseBuild and browsebuild, which Hugo reads as one key"),
        ('[params]\nrepo = "a"\nbrowse = ["data"]\n', "sets browse to a value that is not a string"),
        ('[params]\nrepo = "a"\nbrowseBuild = "just x\\ntouch pwned"\n', "sets browseBuild to a value that holds a line break"),
        ('params = "none"\n', "where a [params] table is expected"),
        ('[params]\nrepo = "a\n', "cannot be read as TOML"),
    ):
        result = site_values(tmp_path, text)
        assert not result and f"site-values: {tmp_path / 'site.toml'}" in result.out and message in result.out, (text, result.out)
    prepare = read(SITE_TEMPLATES / "scripts" / "prepare.sh")
    assert "site.toml\")" not in prepare.replace('site-values.py" "$here/site.toml")', ""), "prepare.sh reads site.toml through site-values.py alone"
    for name in ("repo", "branch", "source", "linkml", "schema", "schemaProject", "browse", "browseBuild"):
        assert f"$(value {name})" in prepare, name


SVG = 'xmlns="http://www.w3.org/2000/svg"'
ACTIVE_SVG = {
    "prefixed.svg": (f'<svg {SVG}><h:script xmlns:h="http://www.w3.org/1999/xhtml">alert(1)</h:script></svg>', "holds a script element"),
    "charref.svg": (f'<svg {SVG}><a href="java&#115;cript:alert(1)"><rect/></a></svg>', "holds an address that runs, in href"),  # codespell:ignore cript
    "UPPER.SVG": (f"<svg {SVG}><script>alert(1)</script></svg>", "holds a script element"),
    "spaced.svg": (f'<svg {SVG} xmlns:x="http://www.w3.org/1999/xlink"><a x:href=" java&#x09;script:alert(1)"><rect/></a></svg>', "holds an address that runs, in href"),
    "handler.svg": (f'<svg {SVG} onload="alert(1)"/>', "holds an event handler, onload"),
    "foreign.svg": (f"<svg {SVG}><foreignObject><p>x</p></foreignObject></svg>", "holds a foreignObject element"),
    "frame.svg": (f'<svg {SVG}><iframe xmlns="http://www.w3.org/1999/xhtml" srcdoc="x"/></svg>', "holds an XHTML iframe element"),
    "animated.svg": (f'<svg {SVG}><a><animate attributeName="href" values="#a;javascript:alert(1)"/></a></svg>', "holds an address that runs, in values"),
    "page.svg": (f'<svg {SVG}><a href="data:text/html,x"><rect/></a></svg>', "holds an address that runs, in href"),
    "used.svg": (f'<svg {SVG}><use href="data:image/svg+xml,x#a"/></svg>', "holds an address that runs, in href"),
    "entity.svg": (f'<!DOCTYPE svg [<!ENTITY x "y">]><svg {SVG}>&x;</svg>', "holds a DOCTYPE"),
    "styled.svg": (f'<?xml-stylesheet type="text/xsl" href="#x"?><svg {SVG}/>', "holds an xml-stylesheet instruction"),
    "broken.svg": (f"<svg {SVG}><rect></svg>", "is not XML the check can read"),
    "packed.SVGZ": ("x", "is compressed, so it is not read"),
}
CLEAN_SVG = (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg {SVG} xmlns:x="http://www.w3.org/1999/xlink" viewBox="0 0 1 1"><title>on top: javascript:</title>'
             '<style>a { fill: red }</style><a x:href="https://example.org/"><rect width="1" height="1" style="fill:red"/></a>'
             '<image href="data:image/svg+xml;base64,AAAA"/><image href="data:image/png;base64,AAAA"/></svg>\n')


def check_svg(*folders):
    return run([sys.executable, "-I", str(SITE_TEMPLATES / "scripts" / "check-svg.py"), *map(str, folders)])


def test_the_svg_check_reads_each_file_as_a_browser_does(tmp_path):
    """A browser opens an SVG as a page of the site's origin, so the check parses it as XML: a prefix, a character reference or a capital hides nothing."""
    write(tmp_path / "clean" / "figures" / "ok.svg", CLEAN_SVG)
    write(tmp_path / "clean" / "notes.txt", "<script>alert(1)</script>")
    result = check_svg(tmp_path / "clean", tmp_path / "missing")
    assert result and result.out == "", f"a clean SVG was named, or a missing folder stopped it: {result.out}"
    for name, (text, _) in ACTIVE_SVG.items():
        write(tmp_path / "active" / "deep" / name, text)
    result = check_svg(tmp_path / "clean", tmp_path / "active")
    assert not result and "check-svg: these SVG files hold a script, an event handler, an address that runs or markup the check cannot read, and the site would serve them:" in result.out, result.out
    for name, (_, reason) in ACTIVE_SVG.items():
        assert f"  {tmp_path / 'active' / 'deep' / name}: {reason}" in result.out, (name, result.out)
    assert "ok.svg" not in result.out and "notes.txt" not in result.out, result.out
    own = check_svg(REPO / ".assets", REPO / "docs", REPO / ".lokf" / "knowledge", SITE_TEMPLATES / "static")
    assert own, f"one of this repository's own figures is named: {own.out}"


def prepare(host, tmp_path):
    """prepare.sh under a uv that runs each command as it is: python as this test's, and any other as a line that names it, with status 7."""
    stub = write(tmp_path / "bin" / "uv", '#!/usr/bin/env bash\n# uv run --project <folder> --frozen --quiet <command>\nshift 5\n'
                 'if [ "$1" = python ]; then shift; exec "$PYTHON" "$@"; fi\necho "stub: $*"\nexit 7\n')
    stub.chmod(0o755)
    return bash(host / "website" / "scripts" / "prepare.sh", env={"PATH": f"{stub.parent}{os.pathsep}{os.environ['PATH']}", "PYTHON": sys.executable})


def test_prepare_stops_on_an_svg_that_could_run_and_on_a_site_toml_it_cannot_read(tmp_path):
    host = tmp_path / "host"
    write(host / ".lokf" / "knowledge" / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n\n# Acme\n")
    write(host / ".assets" / "figure.svg", CLEAN_SVG)
    site = lay_down(host)
    result = prepare(host, tmp_path)
    assert result.rc == 7 and "stub: lokf export" in result.out and "check-svg" not in result.out, f"both checks pass, and prepare.sh goes on to the export: {result.out}"
    shutil.rmtree(site / "generated")
    for folder, name in ((host / "docs" / "img", "UPPER.SVG"), (host / ".assets", "charref.svg"), (site / "static", "prefixed.svg")):
        planted = write(folder / name, ACTIVE_SVG[name][0])
        result = prepare(host, tmp_path)
        assert result.rc == 1 and f"  {planted}: {ACTIVE_SVG[name][1]}" in result.out and "stub: lokf" not in result.out, f"prepare.sh went on past {name}: {result.out}"
        planted.unlink()
    write(site / "site.toml", read(site / "site.toml") + 'browse = "data"\nbrowseBuild = "just x"\nbrowseBuild = "touch pwned"\n')
    result = prepare(host, tmp_path)
    assert result.rc == 1 and "site-values:" in result.out and "cannot be read as TOML" in result.out and "stub:" not in result.out, f"prepare.sh read a site.toml that is not TOML: {result.out}"
    assert not (host / "pwned").exists() and not (site / "generated").exists(), "it stopped before it wrote or ran anything"


def test_the_site_finds_each_input_through_a_mount_and_takes_no_setting_for_it():
    """A mount whose source is missing mounts nothing, so each of these appears on a site only where the repository has it."""
    mounts = {m["source"]: m["target"] for m in tomllib.loads(read(SITE_TEMPLATES / "hugo.toml"))["module"]["mounts"]}
    for source, target in {
        "../README.md": "assets/readme/README.md",
        "../docs": "static/docs",
        "../.assets": "static/assets",
        "../CHANGELOG.md": "assets/changelog/CHANGELOG.md",
        "../.lokf/knowledge": "static/knowledge",
        "generated/schema": "assets/gendoc",
        "../.github/workflows/knowledge-federation.yaml": "assets/host/knowledge-federation.yaml",
        "../.lokf/ingest.lock.yaml": "assets/ingest/ingest.lock.yaml",
        "generated/browse": "static/browse",
    }.items():
        assert mounts.get(source) == target, source
    assert 'resources.Get "readme/README.md"' in read(SITE_TEMPLATES / "content" / "_content.gotmpl"), "the README is read as data, as the docs are"
    assert 'resources.Match "docs/**.md"' in read(SITE_TEMPLATES / "content" / "docs" / "_content.gotmpl")
    assert 'resources.Get "host/knowledge-federation.yaml"' in read(SITE_TEMPLATES / "layouts" / "graph.html")
    prepare = read(SITE_TEMPLATES / "scripts" / "prepare.sh")
    assert 'for model in ${linkml:+"$root/$linkml"/src/*/schema/*.yaml} "$root"/src/*/schema/*.yaml "$root"/.linkml/src/*/schema/*.yaml; do' in prepare, "the schema is looked for in site.toml's linkml folder, at the root, then in the .linkml/ sidecar"


def test_a_mount_that_serves_a_repository_folder_names_the_kinds_of_file_it_serves():
    """Each mount lists what it serves, since no list of what a browser runs as a page is complete."""
    config = tomllib.loads(read(SITE_TEMPLATES / "hugo.toml"))
    kinds = config["params"]["served"]
    assert kinds == ["avif", "gif", "ico", "jpeg", "jpg", "pdf", "png", "svg", "webp"], "figures and PDF files, and nothing a browser runs as a page"
    served = {m["source"]: m.get("files") for m in config["module"]["mounts"] if m["target"].startswith("static/") and m["source"].startswith("../")}
    dots = ["! .**", "! **/.**"]
    assert served == {
        "../.assets": [*dots, "**.{%s}" % ",".join(kinds), "**/"],
        "../docs": [*dots, "**.{%s}" % ",".join(kinds), "**/"],
        "../.lokf/knowledge": [*dots, "**.md", "**/"],
    }, "each served mount leaves out dot files first, then names what it serves"
    route = read(SITE_TEMPLATES / "layouts" / "_partials" / "route.html")
    assert '{{- $served := in site.Params.served (path.Ext $rel | strings.TrimPrefix "." | lower) -}}' in route
    assert '(hasPrefix $rel ".assets/") $served' in route and '(hasPrefix $rel "docs/") $served (resources.Get $rel)' in route, "a link to a file the site does not serve goes to GitHub"


def test_a_page_sends_no_referrer_and_still_loads_a_remote_image():
    base = read(SITE_TEMPLATES / "layouts" / "baseof.html")
    assert '<meta name="referrer" content="no-referrer">' in base
    assert "img-src 'self' https: data:;" in base, "a README's badges are remote images"


def test_a_source_folder_moves_the_four_root_mounts_and_build_reads_it_last(tmp_path):
    """site.toml's source moves the README, docs/, the changelog and .assets/ mounts, and no other; Hugo takes the last file's mounts whole."""
    prepare = read(SITE_TEMPLATES / "scripts" / "prepare.sh")
    block = prepare[prepare.index('  sed -n \'/^\\[\\[module'):prepare.index('>"$out/source.toml"')]
    hugo = tmp_path / "hugo.toml"
    hugo.write_text(read(SITE_TEMPLATES / "hugo.toml"), encoding="utf-8")
    script = f'source=.linkml; here={tmp_path}\n{block.strip()}'
    out = subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=True).stdout
    moved = {m["source"] for m in tomllib.loads(out)["module"]["mounts"]}
    before = {m["source"] for m in tomllib.loads(read(SITE_TEMPLATES / "hugo.toml"))["module"]["mounts"]}
    four = {"../README.md", "../docs", "../CHANGELOG.md", "../.assets"}
    assert moved == (before - four) | {s.replace("../", "../.linkml/", 1) for s in four}, moved ^ before
    build = read(SITE_TEMPLATES / "scripts" / "build.sh")
    assert build.index("scripts/prepare.sh") < build.index("config=$config,generated/source.toml") < build.index('hugo=("${tool[@]}" hugo --config "$config")')


def test_the_home_page_has_five_buttons_and_greys_the_one_it_cannot_find():
    heroes = read(SITE_TEMPLATES / "layouts" / "_partials" / "heroes.html")
    assert re.findall(r'\(dict "text" "([^"]+)"', heroes) == ["The schema", "The bundle", "Architecture", "Glossary", "Quick start"]
    assert '"architecture" (slice "/docs/architecture")' in heroes and '"schema" (slice "/schema")' in heroes
    assert '<span class="button button--missing" role="link" aria-disabled="true" title="{{ .missing }}">' in heroes, "a missing page is a greyed word, never a link"


def test_a_retelling_is_found_by_its_file_name_and_has_no_line_in_the_navigation():
    levels = read(SITE_TEMPLATES / "layouts" / "_partials" / "levels.html")
    pattern = re.search(r"findRESubmatch `(\^\(\.\+\)[^`]+)` \$file", levels).group(1)
    assert re.match(pattern, "docs/architecture.en-simple.md").group(1) == "docs/architecture"
    assert re.match(pattern, "docs/cast/curator.fra-simple.md")
    assert not re.match(pattern, "docs/simple.md") and not re.match(pattern, "docs/architecture.simple.md")
    groups = read(SITE_TEMPLATES / "layouts" / "_partials" / "docs-groups.html")
    assert "(not (index $retold $p.RelPermalink))" in groups, "a retelling is in no group of the navigation"


def test_no_file_frontmatter_reaches_hugo():
    """A docs page or a concept that sets url, draft or layout must change nothing, so each adapter passes frontmatter as data only."""
    for section in ("docs", "knowledge"):
        adapter = read(SITE_TEMPLATES / "content" / section / "_content.gotmpl")
        assert "$.AddPage (merge $page (dict" in adapter
        assert not re.search(r"AddPage \(merge \$page \$fm|merge \$fm ", adapter), section
    assert 'target = "content/docs"' not in read(SITE_TEMPLATES / "hugo.toml"), "a mounted docs file would be read with its own frontmatter"


def test_the_workflows_and_the_sync_look_in_either_folder():
    website = read(WEBSITE_TEMPLATES / "github" / "knowledge-website.yaml")
    assert 'if [ -f ktl-website/site.toml ]; then echo "dir=ktl-website" >> "$GITHUB_OUTPUT"; else echo "dir=website" >> "$GITHUB_OUTPUT"; fi' in website
    assert "path: ${{ steps.site.outputs.dir }}/dist" in website
    assert website.count('      - "ktl-website/**"') == 2, "a push and a pull request both start it"
    assert website == read(REPO / ".github" / "workflows" / "knowledge-website.yaml")
    assert "npm" not in website and "setup-node" not in website
    federation = read(TEMPLATES / "github" / "knowledge-federation.yaml")
    assert "hashFiles('website/site.toml', 'ktl-website/site.toml') != ''" in federation
    assert "if [ -d ktl-website/dist ]; then dist=ktl-website/dist; elif [ -d website/dist ]; then dist=website/dist;" in federation
    sync = read(TEMPLATES / "scripts" / "knowledge-sync.sh")
    assert "for o in website ktl-website; do" in sync


def test_both_workflows_that_build_the_site_install_the_just_the_sidecar_pins():
    """A browseBuild that runs just fails where just is missing, so the federation workflow, a domain host's one site build, installs it as the website workflow does."""
    pin = re.search(r'"rust-just==([0-9.]+)"', read(TEMPLATES / "pyproject.toml")).group(1)
    for workflow in (WEBSITE_TEMPLATES / "github" / "knowledge-website.yaml", TEMPLATES / "github" / "knowledge-federation.yaml"):
        text = read(workflow)
        assert "grep -q '^browseBuild = \"just ' \"$" in text, workflow.name
        assert 'ln -sf "$PWD/.lokf/.venv/bin/just" "$HOME/.local/bin/just"' in text, workflow.name
        assert f"uv tool install rust-just=={pin}" in text, workflow.name
        assert text.index("Install just, when the") < text.index("/scripts/build.sh"), f"{workflow.name} installs just after the build"


def test_the_workspace_folder_is_the_one_the_federation_workflow_serves():
    """The graph page fetches workspace/graph.json, so the workflow copies the snapshot to workspace/ under the site, and the page names that address."""
    workflow = read(TEMPLATES / "github" / "knowledge-federation.yaml")
    assert 'cp -R snapshot "$dist/workspace"' in workflow
    assert '/workspace"' in read(TEMPLATES / "scripts" / "knowledge-federate.py")
    assert 'data-workspace="{{ "workspace/graph.json" | relURL }}"' in read(SITE_TEMPLATES / "layouts" / "graph.html")


def test_the_federation_reads_the_site_s_address_from_site_toml_in_either_folder(tmp_path):
    script = f"import sys, pathlib; sys.path.insert(0, {str(TEMPLATES / 'scripts')!r}); import importlib.util\n" \
             f"spec = importlib.util.spec_from_file_location('federate', {str(TEMPLATES / 'scripts' / 'knowledge-federate.py')!r})\n" \
             "source = pathlib.Path(spec.origin).read_text()\n" \
             "start, end = source.index('def public_url('), source.index('def host_schema(')\n" \
             "scope = {'pathlib': pathlib, 're': __import__('re')}\n" \
             "exec('from __future__ import annotations\\n' + source[start:end], scope)\n" \
             "print(scope['public_url'](pathlib.Path(sys.argv[1]), None))\n"
    for folder in ("website", "ktl-website"):
        host = tmp_path / folder
        lay_down(host, folder)
        result = run([sys.executable, "-c", script, str(host)])
        assert result and result.out.strip() == "https://acme.github.io/acme-platform/workspace", (folder, result.out)
    assert run([sys.executable, "-c", script, str(tmp_path)]).out.strip() == "", "a host with no site has no address to give"


def check_links(site, address="https://acme.github.io/acme-platform/"):
    return run([sys.executable, str(SITE_TEMPLATES / "scripts" / "check-links.py"), str(site), address])


def test_the_link_check_follows_links_and_headings_within_the_site_alone(tmp_path):
    site = tmp_path / "dist"
    write(site / "index.html", '<meta property="og:image" content="https://acme.github.io/acme-platform/og/index.png">'
          '<a href="/acme-platform/docs/guide/#start">g</a> <a href="docs/guide.md">raw</a> <img src="/acme-platform/assets/a.svg">'
          ' <a href="https://example.org/missing">out</a> <a href="https://acme.github.io/other-site/x">another site</a> <a href="/acme-platform/workspace/graph.json">later</a>')
    write(site / "og" / "index.png", "png")
    write(site / "docs" / "guide" / "index.html", '<h2 id="start">Start</h2> <a href="../../">home</a> <a href="#start">here</a>')
    write(site / "docs" / "guide.md", "# The guide\n\nSee [home](https://acme.github.io/acme-platform/).\n")
    write(site / "assets" / "a.svg", "<svg/>")
    write(site / "llms.txt", "- [guide](https://acme.github.io/acme-platform/docs/guide.md)\n")
    result = check_links(site)
    assert result and "2 pages, 0 broken link(s)" in result.out, result.out
    write(site / "docs" / "guide" / "index.html", '<h2 id="begin">Start</h2> <a href="../nowhere/">gone</a>')
    write(site / "llms.txt", "- [guide](https://acme.github.io/acme-platform/docs/absent.md)\n")
    write(site / "docs" / "guide.md", "# The guide\n\n[ref]: https://acme.github.io/acme-platform/docs/gone/\n")
    (site / "og" / "index.png").unlink()
    write(site / "about" / "index.html", '<a href="/docs/guide.md">from the root</a>')
    result = check_links(site)
    assert not result, "a broken link passed"
    for line in ("index.html: /acme-platform/docs/guide/#start names no heading of that page",
                 "index.html: https://acme.github.io/acme-platform/og/index.png names no file of the site",
                 "docs/guide/index.html: ../nowhere/ names no file of the site",
                 "about/index.html: /docs/guide.md is outside the site's path, /acme-platform/",
                 "llms.txt: https://acme.github.io/acme-platform/docs/absent.md names no file of the site",
                 "docs/guide.md: https://acme.github.io/acme-platform/docs/gone/ names no file of the site"):
        assert line in result.out, (line, result.out)
    assert "6 broken link(s)" in result.out, result.out


def clean_html(site, mark="0123abcd"):
    return run([sys.executable, str(SITE_TEMPLATES / "scripts" / "clean-html.py"), str(site), mark])


def test_the_raw_html_cleaner_keeps_what_github_allows_and_shows_the_rest_as_text(tmp_path):
    """Between the build's two marks, raw HTML is cleaned as GitHub cleans a README; outside them the page is left alone."""
    site = tmp_path / "dist"
    region = ('<h2 id="a">A<a class="anchor" href="#a" data-pagefind-ignore data-site="0123abcd">#</a></h2>'
              '<meta http-equiv="refresh" content="0;url=https://example.com/"><style>p{display:none}</style><!-- a note -->'
              '<p onclick="alert(1)" style="color:red" align="center">Hi <a href="javascript:alert(1)">there</a>'
              ' <img src="/acme-platform/assets/a.svg" onerror="alert(1)" alt="a"> <kbd>Q</kbd></p>'
              '<table><tr><th style="text-align:left">T</th></tr></table><details open><summary>More</summary><div>'
              '<input type="checkbox" checked disabled> <input type="text" value="x">')
    write(site / "index.html", f'<html><head><script src="/acme-platform/js/site.js"></script></head><body><!--# raw 0123abcd -->{region}<!--# /raw 0123abcd --></body></html>')
    result = clean_html(site)
    assert result and "1 region(s) of raw HTML cleaned" in result.out, result.out
    page = (site / "index.html").read_text(encoding="utf-8")
    assert '<script src="/acme-platform/js/site.js"></script>' in page, "the page around the marks is the site's own, and is left alone"
    assert "0123abcd" not in page, "the marks go"
    for kept in ('<h2 id="a">A<a class="anchor" href="#a" data-pagefind-ignore="">#</a></h2>', '<p align="center">Hi <a>there</a>',
                 '<img src="/acme-platform/assets/a.svg" alt="a">', "<kbd>Q</kbd>", '<th style="text-align:left">T</th>',
                 '<details open=""><summary>More</summary><div><input type="checkbox" checked="" disabled="">',
                 '&lt;meta http-equiv="refresh"',
                 "&lt;style&gt;p{display:none}&lt;/style&gt;", "&lt;input type=\"text\" value=\"x\"&gt;", "</div></details></body>"):
        assert kept in page, (kept, page)
    for gone in ("onclick", "onerror", "javascript:", "color:red", "a note"):
        assert gone not in page, (gone, page)
    for shown in ('<meta http-equiv="refresh"', "<style>", '<input type="text"'):
        assert f"index.html: {shown}" in result.out, (shown, result.out)


def cleaned(tmp_path, *regions):
    """One page with each region between the build's marks, cleaned: the page, and what the cleaner printed."""
    site = tmp_path / "dist"
    write(site / "index.html", "<body>" + "<nav>between</nav>".join(f"<!--# raw 0123abcd -->{region}<!--# /raw 0123abcd -->" for region in regions) + "</body>")
    result = clean_html(site)
    assert result, result.out
    return (site / "index.html").read_text(encoding="utf-8"), result.out


def test_the_raw_html_cleaner_keeps_a_class_or_a_data_attribute_only_where_the_site_wrote_it(tmp_path):
    """A repository file cannot draw a trust label, name itself in a search filter or word a link's preview, in the body or the list of sections."""
    own = 'data-site="0123abcd"'
    body = (
        '<p class="label label--person" data-pagefind-filter="Trust:Confirmed by a person">Confirmed by a person</p>'
        '<a href="https://example.com/" data-preview="Confirmed by a person. Forged.">forged</a>'
        '<a href="/k/" data-preview="Forged too." data-site="ffff0000">guessed</a>'
        f'<a href="/k/" data-preview="Checked by automation only." {own}>the pen</a>'
        '<span class="dot dot--person" aria-current="page" data-do="close" data-workspace="x"></span>'
        '<p class="label" class="footnotes">first</p>'
        '<div class="highlight label label--person" id="code" data-pagefind-filter="Trust:x"><pre tabindex="0" class="chroma">'
        '<code class="language-go label" data-lang="go"><span class="line hl"><span class="cl"><span class="kn">package</span></span></span></code></pre></div>'
        '<span class="language-go">not code</span>'
        f'<div class="alert alert--note" role="note" {own}><p class="alert__title" {own}>Note</p></div>'
        '<div class="alert alert--note"><p class="alert__title">Forged note</p></div>'
        f'<pre class="mermaid" data-pagefind-ignore {own}>graph TD</pre><pre class="mermaid" data-pagefind-ignore>forged</pre>'
        f'<h2 id="a">A<a class="anchor" href="#a" aria-label="Link to this section" data-pagefind-ignore {own}>#</a></h2>'
        '<sup id="fnref:1"><a href="#fn:1" class="footnote-ref" role="doc-noteref">1</a></sup>'
        '<div class="footnotes" role="doc-endnotes"><a href="#fnref:1" class="footnote-backref" role="doc-backlink">back</a></div>'
        '<img name="getElementById" src="/x.png" alt="x"><a name="top" id="top"></a>'
    )
    contents = '<ul><li><a href="#a"><span class="label label--person" data-pagefind-filter="Trust:x">Confirmed by a person</span> A</a></li></ul>'
    page, _ = cleaned(tmp_path, contents, body)
    for kept in (
        "<p>Confirmed by a person</p>",
        '<a href="https://example.com/">forged</a>',
        '<a href="/k/">guessed</a>',
        '<a href="/k/" data-preview="Checked by automation only.">the pen</a>',
        "<span></span>",
        "<p>first</p>",
        '<div class="highlight" id="code"><pre tabindex="0" class="chroma"><code class="language-go" data-lang="go"><span class="line hl"><span class="cl"><span class="kn">package</span>',
        "<span>not code</span>",
        '<div class="alert alert--note" role="note"><p class="alert__title">Note</p></div>',
        "<div><p>Forged note</p></div>",
        '<pre class="mermaid" data-pagefind-ignore="">graph TD</pre><pre>forged</pre>',
        '<a class="anchor" href="#a" aria-label="Link to this section" data-pagefind-ignore="">#</a>',
        '<a href="#fn:1" class="footnote-ref" role="doc-noteref">1</a>',
        '<div class="footnotes" role="doc-endnotes"><a href="#fnref:1" class="footnote-backref" role="doc-backlink">back</a></div>',
        '<img src="/x.png" alt="x"><a name="top" id="top"></a>',
        '<ul><li><a href="#a"><span>Confirmed by a person</span> A</a></li></ul><nav>between</nav>',
    ):
        assert kept in page, (kept, page)
    for gone in ("label--person", "data-pagefind-filter", "Forged.", "Forged too.", "dot--person", "aria-current", "data-do", "data-workspace", "data-site", "0123abcd", "ffff0000", "getElementById"):
        assert gone not in page, (gone, page)


def test_the_raw_html_cleaner_keeps_none_of_the_site_s_own_classes(tmp_path):
    """Every class the site's stylesheets style is dropped from a file's HTML, but those Goldmark and Chroma write themselves."""
    css = read(SITE_TEMPLATES / "assets" / "css" / "site.css") + read(SITE_TEMPLATES / "assets" / "css" / "custom.css")
    classes = sorted(set(re.findall(r"\.([a-zA-Z][\w-]*)", re.sub(r"/\*.*?\*/|url\([^)]*\)", "", css, flags=re.S))))
    assert {"label", "label--person", "dot", "card", "chip", "button", "anchor", "mermaid", "alert", "highlight"} <= set(classes), "the stylesheet is read"
    page, _ = cleaned(tmp_path, "".join(f'<span class="{name}">{name}</span><code class="{name}"></code>' for name in classes))
    assert set(re.findall(r'class="([^"]*)"', page)) == {"highlight"}, "a class the site styles reached the page from a file"


def test_each_template_that_writes_into_a_page_s_text_marks_what_it_writes():
    """The cleaner keeps a class or a data-* attribute on an element that names the mark, so each hook and partial that writes one must name it."""
    hooks = SITE_TEMPLATES / "layouts" / "_markup"
    partials = SITE_TEMPLATES / "layouts" / "_partials"
    cleaner = read(SITE_TEMPLATES / "scripts" / "clean-html.py")
    assert 'OWN = "data-site"' in cleaner and 'printf ` data-site="%s"` .' in read(partials / "own.html")
    kept = set(re.search(r"SITE_DATA = \{([^}]*)\}", cleaner).group(1).replace('"', "").replace(" ", "").split(","))
    written = set()
    for template in sorted(hooks.glob("*.html")):
        for tag in re.findall(r"<[a-z][^<>]*(?:\{\{[^}]*\}\}[^<>]*)*>", read(template)):
            marks = re.findall(r"\bdata-[a-z-]+", tag)
            written |= set(marks)
            if "class=" in tag or marks:
                assert 'partial "own.html" .' in tag, f"{template.name} writes {tag} with no mark, so the cleaner drops its class or data attribute"
    assert written == kept, "the cleaner keeps the data-* attributes the hooks write, and no other"
    assert '(printf "<details data-pagefind-ignore%s>\\n<summary>YAML</summary>\\n" (partial "own.html" .))' in read(partials / "gendoc.html"), "search still leaves a schema element's YAML out"
    tools = read(partials / "tools.html")
    assert '{{ partial "raw.html" (dict "html" . "from" (partial "repo-path.html" $)) }}' in tools and "{{ . }}" not in tools, "the list of a page's sections is cleaned as its body is"
    assert '(replace (string .Content) (string (partial "own.html" .)) "")' in read(SITE_TEMPLATES / "layouts" / "page.atom.xml"), "the feed carries no mark"


def test_the_raw_html_cleaner_keeps_an_input_only_as_a_checkbox_and_writes_each_attribute_once(tmp_path):
    """A browser reads the first of an attribute written twice, so `type="password" type="checkbox"` is a password field."""
    page, log = cleaned(
        tmp_path,
        '<input type="password" type="checkbox"> <input type="checkbox" type="text"> <input value="x"> '
        '<input type="CHECKBOX" type="checkbox" checked disabled> <p align="left" align="right" title="a" title="b">twice</p>',
    )
    for kept in ('&lt;input type="password" type="checkbox"&gt;', '&lt;input type="checkbox" type="text"&gt;', '&lt;input value="x"&gt;',
                 '<input type="CHECKBOX" checked="" disabled="">', '<p align="left" title="a">twice</p>'):
        assert kept in page, (kept, page)
    assert "<input type=\"password\"" not in page and "<input value" not in page
    assert log.count("is not a tag GitHub allows, and is shown as text") == 3, log


def test_the_raw_html_cleaner_stops_on_a_mark_with_no_end_and_on_a_build_with_no_mark(tmp_path):
    site = tmp_path / "dist"
    write(site / "index.html", "<body><!--# raw 0123abcd --><p>Hi <!-- never closed<!--# /raw 0123abcd --></body>".replace("<!--# /raw 0123abcd -->", ""))
    result = clean_html(site)
    assert not result and "index.html holds a mark with no end" in result.out, result.out
    write(site / "index.html", '<body><!--# raw 0123abcd --><!--# raw 0123abcd --><p data-site="0123abcd">Hi</p><!--# /raw 0123abcd --></body>')
    result = clean_html(site)
    assert not result and "index.html holds a mark with no end" in result.out, "a region opened twice passed"
    write(site / "index.html", "<body><p>No mark.</p></body>")
    result = clean_html(site)
    assert not result and "no page holds the build's mark" in result.out, result.out
