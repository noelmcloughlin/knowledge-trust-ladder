"""The ktl-website templates install a complete site, and the files a host owns are named alike everywhere.

Step 1 of the skill copies templates/website/ into a host and fills four
placeholders in two files. The copy must be complete, no placeholder may
remain, and the build must refuse a site.toml that still holds one. The site
takes no setting for what it shows: hugo.toml mounts each input from where a
repository keeps it, and a mount that finds nothing draws nothing, so the
mounts are the list of what the site can find.

The three files a repair never replaces are named in the skill's page, its
preflight, the contract and the sidecar's knowledge-sync.sh, and the four
must agree. The site's folder is website/, or ktl-website/ where website/ is
another site's, and the workflows and the sync look in both. The link check
is plain Python and is tested here. The build itself is
scripts/smoke-test-website.sh, which needs the network.
"""

from __future__ import annotations

import re
import shutil
import sys
import tomllib

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


def lay_down(host, folder="website"):
    """Step 1 as the skill gives it: copy, rename the gitignore, substitute as literal text in the two files."""
    site = host / folder
    shutil.copytree(SITE_TEMPLATES, site)
    (site / "gitignore").rename(site / ".gitignore")
    for name in ("site.toml", "README.md"):
        text = (site / name).read_text(encoding="utf-8")
        for token, value in PLACEHOLDERS.items():
            text = text.replace(f"<{token}>", value)
        (site / name).write_text(text, encoding="utf-8")
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
    served = [m for m in tomllib.loads(read(SITE_TEMPLATES / "hugo.toml"))["module"]["mounts"] if m["target"].startswith("static/") and m["source"].startswith("../")]
    for mount in served:
        assert "! **.{html,htm,xhtml,xht,xml,xsl,xslt,shtml,mht,mhtml}" in mount.get("files", []), f"{mount['source']} could serve a page that runs on the site's origin"
    assert 'resources.Match "docs/**.md"' in read(SITE_TEMPLATES / "content" / "docs" / "_content.gotmpl")
    assert 'resources.Get "host/knowledge-federation.yaml"' in read(SITE_TEMPLATES / "layouts" / "graph.html")
    prepare = read(SITE_TEMPLATES / "scripts" / "prepare.sh")
    assert 'for model in "$root"/src/*/schema/*.yaml "$root"/.linkml/src/*/schema/*.yaml; do' in prepare, "the schema is looked for at the root first, then in the .linkml/ sidecar"


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
    region = ('<h2 id="a">A<a class="anchor" href="#a" data-pagefind-ignore>#</a></h2>'
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


def test_the_raw_html_cleaner_stops_on_a_mark_with_no_end_and_on_a_build_with_no_mark(tmp_path):
    site = tmp_path / "dist"
    write(site / "index.html", "<body><!--# raw 0123abcd --><p>Hi <!-- never closed<!--# /raw 0123abcd --></body>".replace("<!--# /raw 0123abcd -->", ""))
    result = clean_html(site)
    assert not result and "index.html holds a mark with no end" in result.out, result.out
    write(site / "index.html", "<body><p>No mark.</p></body>")
    result = clean_html(site)
    assert not result and "no page holds the build's mark" in result.out, result.out
