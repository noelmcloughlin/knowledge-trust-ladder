"""knowledge-ingest.py mirrors sources from outside the repository, and has to keep the promises its header makes.

The script is the template every host carries as .lokf/scripts/knowledge-ingest.py.
These tests run it on throwaway repositories against servers of their own,
and pin:

1. an http address is mirrored with its header and its lock record, a second
   run that gets 304 writes nothing, and a changed page is fetched again;
2. a private address is refused unless the manifest allows it;
3. a PDF's text layer is mirrored, and a PDF without one is refused;
4. a Confluence selection is listed with its versions and fetched by v2 on
   Cloud and v1 on Data Center; an unchanged page costs no body; a page that
   leaves the selection is unlisted; --prune removes an uncited file and
   keeps a cited one;
5. a git path at a ref is mirrored by its commit, with a file that is not
   Markdown kept in a fence;
6. a command's output is mirrored, an untracked command is refused, and a
   command past its timeout fails the entry and nothing else;
7. the manifest's refusals: an unknown key, a variable name outside the
   KNOWLEDGE_INGEST_ namespace, an internal entry in a public repository,
   and a confidential entry that goes to the cache;
8. --patch writes a Reference concept per mirrored item of an entry that asks;
9. --status prints one line with the token names and no value;
10. the converter turns Confluence storage format into Markdown blocks;
11. the shell half refuses to run under sh.
"""

from __future__ import annotations

import http.server
import importlib.util
import json
import sys
import threading
from pathlib import Path

import pytest
import yaml

from conftest import SCRIPTS, Git, has_line, matches, read, run, write

INGEST = SCRIPTS / "knowledge-ingest.sh"
INGEST_PY = SCRIPTS / "knowledge-ingest.py"
IDENT = {"GIT_AUTHOR_NAME": "contract", "GIT_AUTHOR_EMAIL": "contract@example.invalid",
         "GIT_COMMITTER_NAME": "contract", "GIT_COMMITTER_EMAIL": "contract@example.invalid"}
TOKENS = {"KNOWLEDGE_INGEST_ATLASSIAN_USER": "me@example.invalid", "KNOWLEDGE_INGEST_ATLASSIAN_TOKEN": "secret-token-value"}


def load_module():
    spec = importlib.util.spec_from_file_location("knowledge_ingest", INGEST_PY)
    module = importlib.util.module_from_spec(spec)
    sys.modules["knowledge_ingest"] = module
    spec.loader.exec_module(module)
    return module


class Stub(http.server.BaseHTTPRequestHandler):
    """Serves the routes a test sets: path -> (status, headers, body), recording every request."""

    routes: dict = {}
    requests: list = []

    def log_message(self, *args):  # noqa: D102 - quiet
        pass

    def do_GET(self):  # noqa: N802 - the handler's name
        path = self.path.split("?", 1)[0]
        Stub.requests.append((self.path, dict(self.headers)))
        route = Stub.routes.get(path) or Stub.routes.get(self.path)
        if route is None:
            self.send_response(404)
            self.end_headers()
            return
        status, headers, body = route
        if headers.get("ETag") and self.headers.get("If-None-Match") == headers["ETag"]:
            self.send_response(304)
            self.end_headers()
            return
        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@pytest.fixture
def server():
    Stub.routes = {}
    Stub.requests = []
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Stub)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()


def host(tmp_path: Path, manifest: dict, git: bool = True) -> Path:
    root = tmp_path / "host"
    write(root / ".lokf" / "knowledge" / "index.md", "---\nbase_iri: https://acme.example/knowledge/\ntitle: Acme\n---\n# Acme\n\n## references\n")
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest, sort_keys=False))
    if git:
        g = Git(root)
        g.init()
        g("add", "-A")
        g("commit", "-q", "-m", "host", env=IDENT)
    return root


def ingest(root: Path, *args, env=None):
    full = dict(TOKENS)
    full.update(env or {})
    return run([sys.executable, INGEST_PY, "--root", root, "--now", "2026-10-18T06:00:00Z", *args], env=full)


def manifest_for(entries: list, **top) -> dict:
    m = {"ingest_version": "1", "allow_private_addresses": True, "entries": entries}
    m.update(top)
    return m


def lock_of(root: Path) -> dict:
    return yaml.safe_load(read(root / ".lokf" / "ingest.lock.yaml"))


def minimal_pdf(text: str) -> bytes:
    """A one-page PDF with the text in Helvetica, its cross-reference table computed."""
    stream = f"BT /F1 24 Tf 72 700 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode() + b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)


# 1. http


def test_http_mirrors_a_page_then_writes_nothing_on_304_and_fetches_a_change(tmp_path, server, checks):
    page = b"<html><head><title>Wire protocol</title></head><body><h1>Wire protocol</h1><p>Frames are <b>length</b>-prefixed.</p></body></html>"
    Stub.routes["/spec/v3.html"] = (200, {"Content-Type": "text/html; charset=utf-8", "ETag": '"v3-abc"'}, page)
    root = host(tmp_path, manifest_for([{"id": "vendor", "kind": "http", "urls": [f"{server}/spec/v3.html"], "sensitivity": "public", "owner": "vendor/v3", "why": "the protocol"}]))
    result = ingest(root)
    checks.ok(result, "first run", result.out)
    files = sorted(p.name for p in (root / ".lokf" / "mirror" / "vendor").glob("*.md"))
    checks.ok(len(files) == 1 and files[0].startswith("v3-"), "one mirror file named by the address", str(files))
    text = read(root / ".lokf" / "mirror" / "vendor" / files[0])
    checks.ok(text.startswith("---\norigin: " + server + "/spec/v3.html\ntitle: Wire protocol\ningest: vendor\nkind: http\nversion: v3-abc\n"), "the header", text[:300])
    checks.ok("# Wire protocol\n\nFrames are **length**-prefixed.\n" in text, "the body as Markdown", text)
    lock = lock_of(root)
    item = lock["entries"]["vendor"]["items"][files[0][:-3]]
    checks.ok(item["status"] == "ok" and item["etag"] == '"v3-abc"' and item["retrieved_at"] == "2026-10-18T06:00:00Z", "the lock record", str(item))
    checks.ok(matches(result.out, r"^- vendor \(http, 1 address\): 1 fetched$"), "the summary line", result.out)
    before = read(root / ".lokf" / "ingest.lock.yaml")
    Stub.requests = []
    result = ingest(root)
    checks.ok(result and "Nothing changed since the last run." in result.out, "second run writes nothing", result.out)
    checks.ok(read(root / ".lokf" / "ingest.lock.yaml") == before, "the lock is byte-identical after a 304")
    checks.ok(any(h.get("If-None-Match") == '"v3-abc"' for _, h in Stub.requests), "the second run sent If-None-Match", str(Stub.requests))
    Stub.routes["/spec/v3.html"] = (200, {"Content-Type": "text/html", "ETag": '"v4-def"'}, page.replace(b"length", b"type"))
    result = ingest(root)
    checks.ok(result and "1 fetched" in result.out, "a changed page is fetched again", result.out)
    checks.ok("**type**-prefixed" in read(root / ".lokf" / "mirror" / "vendor" / files[0]), "the mirror holds the new text")
    checks.ok(lock_of(root)["entries"]["vendor"]["items"][files[0][:-3]]["version"] == "v4-def", "the version moved")
    Stub.routes.pop("/spec/v3.html")
    result = ingest(root)
    checks.ok(result and "1 gone" in result.out, "a 404 marks the item gone", result.out)
    checks.ok((root / ".lokf" / "mirror" / "vendor" / files[0]).is_file(), "the gone file stays")


# 2. private addresses


def test_a_private_address_is_refused_unless_the_manifest_allows_it(tmp_path, server, checks):
    Stub.routes["/p.md"] = (200, {"Content-Type": "text/markdown"}, b"# P\n")
    m = manifest_for([{"id": "p", "kind": "http", "urls": [f"{server}/p.md"], "sensitivity": "public"}])
    m["allow_private_addresses"] = False
    root = host(tmp_path, m)
    result = ingest(root)
    checks.ok(result and "1 refused" in result.out and "refused, 127.0.0.1 is a private or link-local address" in result.out, "loopback refused, with the reason in the summary", result.out)
    checks.ok(not (root / ".lokf" / "mirror").exists(), "nothing written")
    item = next(iter(lock_of(root)["entries"]["p"]["items"].values()))
    checks.ok(item["status"] == "refused" and "private" in item["reason"], "the lock says refused", str(item))
    result = ingest(root, "--strict")
    checks.ok(result.rc == 1, "--strict exits 1 on a refusal", result.out)


# 3. pdf


def test_a_pdf_text_layer_is_mirrored_and_a_blank_pdf_is_refused(tmp_path, server, checks):
    pytest.importorskip("pypdf")
    Stub.routes["/spec.pdf"] = (200, {"Content-Type": "application/pdf"}, minimal_pdf("Hello mirror"))
    Stub.routes["/blank.pdf"] = (200, {"Content-Type": "application/pdf"}, minimal_pdf(""))
    root = host(tmp_path, manifest_for([
        {"id": "spec", "kind": "http", "urls": [f"{server}/spec.pdf"], "sensitivity": "public"},
        {"id": "blank", "kind": "http", "urls": [f"{server}/blank.pdf"], "sensitivity": "public"},
    ]))
    result = ingest(root)
    checks.ok(result, "the run completes", result.out)
    mirrored = list((root / ".lokf" / "mirror" / "spec").glob("*.md"))
    checks.ok(len(mirrored) == 1 and "Hello mirror" in read(mirrored[0]), "the text layer is mirrored", result.out)
    checks.ok("converted_by: pdf-text/1" in read(mirrored[0]), "the converter is named")
    lock = lock_of(root)
    blank = next(iter(lock["entries"]["blank"]["items"].values()))
    checks.ok(blank["status"] == "refused" and "no text layer" in blank["reason"], "a blank PDF is refused", str(blank))


# 4. confluence

STORAGE = """<h1>Deploy runbook</h1><p>Deploy with <strong>care</strong> and <a href="https://acme.example/x">the console</a>.</p>
<ac:structured-macro ac:name="info"><ac:rich-text-body><p>Read the checklist first.</p></ac:rich-text-body></ac:structured-macro>
<ul><li>Stop the <code>worker</code></li><li>Run the migration<ul><li>then the smoke test</li></ul></li></ul>
<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">bash</ac:parameter><ac:plain-text-body><![CDATA[just deploy --env prod
echo <done>]]></ac:plain-text-body></ac:structured-macro>
<table><tbody><tr><th>Step</th><th>Owner</th></tr><tr><td>Deploy</td><td>team:platform</td></tr></tbody></table>
<ac:task-list><ac:task><ac:task-status>complete</ac:task-status><ac:task-body>Tell the channel</ac:task-body></ac:task></ac:task-list>
<p>See <ac:link><ri:page ri:content-title="Rollback" /></ac:link> and <ac:structured-macro ac:name="toc" />.</p>"""


def confluence_routes(server: str, cloud: bool, pages: dict) -> None:
    prefix = "/wiki" if cloud else ""
    results = [{"id": pid, "title": p["title"], "version": {"number": p["version"], "when": "2026-10-03T09:12:44.000+01:00", "by": {"accountId": "5b10ac8d"}},
                "_links": {"webui": f"/spaces/PLAT/pages/{pid}/{p['title'].replace(' ', '+')}"}} for pid, p in pages.items()]
    Stub.routes[f"{prefix}/rest/api/content/search"] = (200, {"Content-Type": "application/json"}, json.dumps({"results": results, "size": len(results)}).encode())
    for pid, p in pages.items():
        body = {"id": pid, "title": p["title"], "version": {"number": p["version"]}, "body": {"storage": {"value": p["storage"]}}}
        if cloud:
            Stub.routes[f"/wiki/api/v2/pages/{pid}"] = (200, {"Content-Type": "application/json"}, json.dumps(body).encode())
        else:
            Stub.routes[f"/rest/api/content/{pid}"] = (200, {"Content-Type": "application/json"}, json.dumps(body).encode())


def confluence_manifest(server: str, cloud: bool) -> dict:
    return manifest_for([{"id": "runbooks", "service": "confluence", "select": {"label": "ktl", "space": "PLAT"}, "owner": "team:platform", "why": "the runbooks"}],
                        services={"confluence": {"kind": "confluence", "site": server, "api": "cloud" if cloud else "datacenter",
                                                 "auth": {"scheme": "basic", "user_env": "KNOWLEDGE_INGEST_ATLASSIAN_USER", "env": "KNOWLEDGE_INGEST_ATLASSIAN_TOKEN"}}})


@pytest.mark.parametrize("cloud", [True, False], ids=["cloud", "datacenter"])
def test_a_confluence_selection_is_listed_fetched_and_kept_current(tmp_path, server, checks, cloud):
    pages = {"123": {"title": "Deploy runbook", "version": 14, "storage": STORAGE}, "124": {"title": "Rollback", "version": 3, "storage": "<p>Roll back with <em>care</em>.</p>"}}
    confluence_routes(server, cloud, pages)
    root = host(tmp_path, confluence_manifest(server, cloud))
    result = ingest(root, "--visibility", "private")
    checks.ok(result and "2 fetched" in result.out, "two pages fetched", result.out)
    searched = [p for p, _ in Stub.requests if "content/search" in p]
    checks.ok(searched and "cql=type+%3D+page+AND+label+%3D+%22ktl%22+AND+space+%3D+%22PLAT%22" in searched[0] and "expand=version" in searched[0], "the label became a CQL query with versions", str(searched))
    checks.ok(all("Authorization" in h and h["Authorization"].startswith("Basic ") for _, h in Stub.requests), "every request carried the credential", str(Stub.requests[:1]))
    text = read(root / ".lokf" / "mirror" / "runbooks" / "123.md")
    checks.ok("version: '14'\nlast_modified: '2026-10-03T08:12:44Z'\nauthor: 5b10ac8d\n" in text, "the header carries version, time in UTC and author", text[:400])
    checks.ok(f"origin: {server}{'/wiki' if cloud else ''}/spaces/PLAT/pages/123/Deploy+runbook" in text, "the origin is the page's address", text[:200])
    for piece in ("# Deploy runbook", "Deploy with **care** and [the console](https://acme.example/x).", "> **Info**\n\n> Read the checklist first.",
                  "- Stop the `worker`\n- Run the migration\n  - then the smoke test", "```bash\njust deploy --env prod\necho <done>\n```",
                  "| Step | Owner |\n| --- | --- |\n| Deploy | team:platform |", "- [x] Tell the channel", "See Rollback and [Confluence macro: toc]."):
        checks.ok(piece in text, f"the body holds {piece[:30]!r}", text)
    checks.ok("secret-token-value" not in read(root / ".lokf" / "ingest.lock.yaml") and "secret-token-value" not in result.out, "no secret in the lock or the output")
    Stub.requests = []
    result = ingest(root, "--visibility", "private")
    checks.ok(result and "2 unchanged" in result.out and "Nothing changed" in result.out, "unchanged versions cost no body", result.out)
    checks.ok(not any("pages/" in p or "content/12" in p for p, _ in Stub.requests), "no body was requested", str(Stub.requests))
    pages["124"]["version"] = 4
    pages["124"]["storage"] = "<p>Roll back with <em>great care</em>.</p>"
    confluence_routes(server, cloud, pages)
    result = ingest(root, "--visibility", "private")
    checks.ok(result and "1 fetched, 1 unchanged" in result.out, "only the moved page is fetched", result.out)
    checks.ok("*great care*" in read(root / ".lokf" / "mirror" / "runbooks" / "124.md"), "the moved page is rewritten")
    del pages["124"]
    confluence_routes(server, cloud, pages)
    result = ingest(root, "--visibility", "private")
    checks.ok(result and "1 unlisted" in result.out, "a page that left the selection is unlisted", result.out)
    checks.ok((root / ".lokf" / "mirror" / "runbooks" / "124.md").is_file(), "the unlisted file stays")
    write(root / ".lokf" / "knowledge" / "playbooks" / "rollback.md", "---\ntype: Playbook\ntitle: Rollback\nresource: .lokf/mirror/runbooks/124.md\n---\n# Rollback\n")
    result = ingest(root, "--visibility", "private", "--prune")
    checks.ok(result and "a concept still cites it, so it stays" in result.out, "a cited file is kept by --prune", result.out)
    (root / ".lokf" / "knowledge" / "playbooks" / "rollback.md").unlink()
    result = ingest(root, "--visibility", "private", "--prune")
    checks.ok(result and "no concept cites it; removed" in result.out, "an uncited file is removed by --prune", result.out)
    checks.ok(not (root / ".lokf" / "mirror" / "runbooks" / "124.md").exists(), "the file is gone")
    checks.ok("124" not in lock_of(root)["entries"]["runbooks"]["items"], "and so is its lock record")


def test_a_selection_over_max_items_is_refused_whole(tmp_path, server, checks):
    pages = {str(n): {"title": f"Page {n}", "version": 1, "storage": "<p>x</p>"} for n in range(100, 104)}
    confluence_routes(server, True, pages)
    m = confluence_manifest(server, True)
    m["entries"][0]["max_items"] = 3
    root = host(tmp_path, m)
    result = ingest(root, "--visibility", "private")
    checks.ok(result and "refused, the selector returns more than max_items (3)" in result.out, "refused whole", result.out)
    checks.ok(not (root / ".lokf" / "mirror").exists(), "nothing mirrored")


# 5. git


def test_a_git_path_at_a_ref_is_mirrored_by_its_commit(tmp_path, checks):
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    g = Git(upstream)
    g.init()
    write(upstream / "runbooks" / "deploy.md", "# Deploy\n\nPush the button.\n")
    write(upstream / "runbooks" / "limits.yaml", "cpu: 2\n")
    write(upstream / "runbooks" / "draft-notes.md", "secret draft\n")
    write(upstream / "README.md", "# Not mirrored\n")
    g("add", "-A")
    g("commit", "-q", "-m", "one", env=IDENT)
    sha = g("rev-parse", "HEAD")
    root = host(tmp_path, manifest_for([{"id": "wiki", "kind": "git", "url": str(upstream), "ref": "main", "path": "runbooks",
                                         "include": ["*.md", "*.yaml"], "exclude": ["draft-*"], "sensitivity": "public"}]))
    result = ingest(root)
    checks.ok(result and "2 fetched" in result.out, "two files mirrored", result.out)
    deploy = read(root / ".lokf" / "mirror" / "wiki" / "deploy.md")
    checks.ok(f"version: {sha}\n" in deploy and "kind: git\n" in deploy and "Push the button." in deploy, "the commit is the version", deploy)
    limits = read(root / ".lokf" / "mirror" / "wiki" / "limits.yaml.md")
    checks.ok("```yaml\ncpu: 2\n```" in limits, "a file that is not Markdown is fenced", limits)
    checks.ok(not (root / ".lokf" / "mirror" / "wiki" / "draft-notes.md").exists(), "an excluded file is not mirrored")
    result = ingest(root)
    checks.ok(result and "Nothing changed" in result.out, "the same commit changes nothing", result.out)
    write(upstream / "runbooks" / "deploy.md", "# Deploy\n\nPush the other button.\n")
    g("add", "-A")
    g("commit", "-q", "-m", "two", env=IDENT)
    result = ingest(root)
    checks.ok(result and "1 fetched, 1 unchanged" in result.out, "a new commit refetches the changed file only", result.out)


# 6. command


def test_a_command_is_mirrored_only_once_tracked_and_fails_on_its_own(tmp_path, checks):
    root = host(tmp_path, manifest_for([
        {"id": "schema", "kind": "command", "command": ".lokf/ingest/schema.sh", "sensitivity": "public"},
        {"id": "slow", "kind": "command", "command": ".lokf/ingest/slow.sh", "timeout": 1, "sensitivity": "public"},
    ]))
    write(root / ".lokf" / "ingest" / "schema.sh", "#!/bin/sh\necho \"# Schema\"\necho\necho \"table orders (id, total) entry=$KNOWLEDGE_INGEST_ENTRY token=${KNOWLEDGE_INGEST_ATLASSIAN_TOKEN:-none}\"\n")
    write(root / ".lokf" / "ingest" / "slow.sh", "#!/bin/sh\nsleep 5\n")
    for name in ("schema.sh", "slow.sh"):
        (root / ".lokf" / "ingest" / name).chmod(0o755)
    result = ingest(root)
    checks.ok(result and "refused, .lokf/ingest/schema.sh is not tracked by git" in result.out, "an untracked command is refused", result.out)
    g = Git(root)
    g("add", "-A")
    g("commit", "-q", "-m", "commands", env=IDENT)
    result = ingest(root)
    checks.ok(result and "- schema (command, .lokf/ingest/schema.sh): 1 fetched" in result.out, "the output is mirrored", result.out)
    text = read(root / ".lokf" / "mirror" / "schema" / "schema.md")
    checks.ok("table orders (id, total) entry=schema token=none" in text, "the command sees its entry id and no credential it was not given", text)
    checks.ok("origin: command:.lokf/ingest/schema.sh" in text, "the origin names the command")
    checks.ok("failed, the command ran past its timeout (1s)" in result.out, "the slow command fails its entry alone", result.out)
    checks.ok(lock_of(root)["entries"]["slow"]["status"] == "failed", "the lock says failed")
    checks.ok(lock_of(root)["entries"]["schema"]["items"]["schema"]["command_sha256"], "the command's own digest is recorded")


# 7. the manifest


def test_the_manifest_refuses_what_its_header_says(tmp_path, server, checks):
    Stub.routes["/a.md"] = (200, {"Content-Type": "text/markdown"}, b"# A\n")
    url = f"{server}/a.md"
    root = host(tmp_path, manifest_for([{"id": "a", "kind": "http", "urls": [url], "sensitivity": "public", "colour": "red"}]))
    result = ingest(root)
    checks.ok(result.rc == 1 and "a key this script does not know: colour" in result.out, "an unknown key", result.out)
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for([{"id": "a", "kind": "http", "urls": [url], "auth": {"scheme": "bearer", "env": "MY_TOKEN"}}])))
    result = ingest(root)
    checks.ok(result.rc == 1 and "MY_TOKEN is not an environment variable name starting KNOWLEDGE_INGEST_" in result.out, "a name outside the namespace", result.out)
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for([{"id": "a", "kind": "http", "urls": [url]}])))
    result = ingest(root, "--visibility", "public")
    checks.ok(result and "refused, internal content is not committed to a public repository" in result.out, "internal in a public repository", result.out)
    result = ingest(root, "--visibility", "unknown")
    checks.ok(result and "visibility is unknown" in result.out, "unknown counts as public", result.out)
    result = ingest(root, "--visibility", "private")
    checks.ok(result and "1 fetched" in result.out and (root / ".lokf" / "mirror" / "a").is_dir(), "internal in a private repository", result.out)
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for([{"id": "c", "kind": "http", "urls": [url], "sensitivity": "confidential"}])))
    result = ingest(root, "--visibility", "public")
    checks.ok(result and "1 fetched" in result.out, "confidential is fetched anywhere", result.out)
    checks.ok(list((root / ".lokf" / ".cache" / "mirror" / "c").glob("*.md")), "and goes to the cache")
    checks.ok(not (root / ".lokf" / "mirror" / "c").exists(), "never to the mirror")
    checks.ok(lock_of(root)["entries"]["c"]["items"] and "a" not in lock_of(root)["entries"], "the lock follows the manifest")
    before = read(root / ".lokf" / "ingest.lock.yaml")
    result = ingest(root, "--visibility", "public", "--dry-run")
    checks.ok(result and read(root / ".lokf" / "ingest.lock.yaml") == before, "a dry run writes nothing", result.out)


# 8. --patch


def test_patch_writes_a_reference_concept_per_mirrored_item_of_an_entry_that_asks(tmp_path, server, checks):
    Stub.routes["/spec.md"] = (200, {"Content-Type": "text/markdown"}, b"# Spec\n\nThe spec.\n")
    root = host(tmp_path, manifest_for([{"id": "vendor", "kind": "http", "urls": [f"{server}/spec.md"], "sensitivity": "public", "owner": "vendor/v3", "reference": True, "why": "the protocol"}]))
    ingest(root)
    result = ingest(root, "--patch")
    checks.ok(result and "wrote 1 operation for the pen" in result.out, "one create", result.out)
    patch = yaml.safe_load(read(root / ".lokf" / "patch.yaml"))
    op = patch["ops"][0]
    checks.ok(op["op"] == "create" and op["path"].startswith("references/vendor-spec-") and op["frontmatter"]["type"] == "Reference", "the operation's shape", str(op))
    checks.ok(op["frontmatter"]["resource"] == f"{server}/spec.md" and op["frontmatter"]["sources"][0]["resource"].startswith(".lokf/mirror/vendor/"), "origin as resource, mirror as source", str(op))
    checks.ok(op["frontmatter"]["sources"][0]["author"] == "vendor/v3" and op["frontmatter"]["id"].startswith("https://acme.example/knowledge/references/vendor-"), "owner and id", str(op))
    result = ingest(root, "--patch")
    checks.ok(result.rc == 1 and "exists; apply or remove it first" in result.out, "an existing patch file is never overwritten", result.out)


# 9. --status


def test_status_prints_one_line_with_names_and_no_value(tmp_path, server, checks):
    root = host(tmp_path, confluence_manifest(server, True))
    result = ingest(root, "--status", env={"KNOWLEDGE_INGEST_ATLASSIAN_TOKEN": ""})
    checks.ok(result and result.out.startswith("ingest: 1 entries in .lokf/ingest.yaml; 0 mirrored files, no lock yet; tokens present: KNOWLEDGE_INGEST_ATLASSIAN_USER; tokens absent: KNOWLEDGE_INGEST_ATLASSIAN_TOKEN"), "the status line", result.out)
    checks.ok("me@example.invalid" not in result.out, "no value")
    result = run(["bash", INGEST, "--root", root, "--status"], env=TOKENS)
    checks.ok(result and result.out.startswith("ingest: 1 entries"), "the shell half passes --status through", result.out)


# 10. the converter


def test_the_converter_turns_storage_format_into_markdown_blocks(checks):
    m = load_module()
    text, title = m.html_to_markdown("<html><head><title>T</title></head><body><h2>Two</h2><p>One <i>two</i>  three<br/>four</p><pre>a\n  b</pre><blockquote><p>q</p></blockquote><hr/><ol><li>x</li><li>y</li></ol></body></html>")
    checks.ok(title == "T", "the title", title)
    checks.ok(text == "## Two\n\nOne *two* three\nfour\n\n```\na\n  b\n```\n\n> q\n\n---\n\n1. x\n2. y\n", "the blocks", text)
    checks.ok(m.shown("a​b‮c\x07d e") == "abcd e", "invisible characters are removed and a no-break space becomes a space", m.shown("a​b‮c\x07d e"))
    checks.ok(m.utc("2026-10-03T09:12:44.123+01:00") == "2026-10-03T08:12:44Z" and m.utc("Sat, 18 Oct 2026 06:00:00 GMT") == "2026-10-18T06:00:00Z", "timestamps in one UTC shape")


# 11. the shell half


def test_the_shell_half_refuses_sh(tmp_path, checks):
    result = run(["sh", INGEST, "--status"])
    checks.ok(result.rc == 2 and has_line(result.out, "run this with bash: bash knowledge-ingest.sh [--root <dir>] [--visibility <v>] [--only <id>] [--dry-run] [--prune] [--strict] [--summary <file>] [--status] [--patch [<file>]]"), "refused under sh", result.out)
    result = run(["bash", INGEST, "--root", tmp_path, "--status"])
    checks.ok(result and result.out == "ingest: no .lokf/ingest.yaml, so no source outside the repository is mirrored", "no manifest is one line", result.out)
