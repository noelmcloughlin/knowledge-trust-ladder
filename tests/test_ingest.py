"""knowledge-ingest.py mirrors sources from outside the repository, and has to keep the promises its header makes.

The script is the template every host carries as .lokf/scripts/knowledge-ingest.py.
These tests run it on throwaway repositories against servers of their own,
and pin:

1. an http address is mirrored with its header and its lock record, a second
   run that gets 304 writes nothing, and a changed page is fetched again;
2. a private address is refused unless the manifest allows it, and so is a
   name that turns private between the check and the connection. Git is
   held to the address the check found and follows no redirect. Through a
   proxy, the name is checked once and the proxy resolves it;
3. a PDF's text layer is mirrored, and a PDF without one is refused;
4. a Confluence selection is listed with its versions and fetched by v2 on
   Cloud and v1 on Data Center. An unchanged page costs no body, and a page
   that leaves the selection is unlisted. --prune removes an uncited file
   and keeps a cited one;
5. a git path at a ref is mirrored by its commit, with a file that is not
   Markdown kept in a fence;
6. a command's output is mirrored, an untracked command is refused, and a
   command past its timeout fails the entry and nothing else;
7. the manifest's refusals: an unknown key, a variable name outside the
   KNOWLEDGE_INGEST_ namespace, an internal entry in a public repository,
   and a confidential entry where git would see its copy. That entry goes to
   the cache once git ignores it and tracks nothing there;
8. --patch writes a Reference concept per mirrored item of an entry that asks,
   and a later patch keeps the sources a person added;
9. --status prints one line with the token names and no value;
10. the converter turns Confluence storage format into Markdown blocks, keeps
    the body after head metadata and macro parameters, resolves links,
    honours a declared charset and keeps the joiners;
11. the shell half refuses to run under sh;
12. a redirect to another host drops the credential, a 503 is retried, and a
    weak ETag is the version without its prefix;
13. a Confluence listing is paged, one page's missing body is that page's
    alone, and an answer of the wrong shape fails the entry and nothing else;
14. a git entry follows a changed include at the same commit, and skips a
    binary file by name;
15. an entry that leaves the manifest takes its folder with it;
16. the mirror cap refuses the item that would pass it;
17. the workflow's filter hands over the KNOWLEDGE_INGEST_ secrets and no other.
"""

from __future__ import annotations

import contextlib
import http.server
import importlib.util
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
from pathlib import Path

import pytest
import yaml

from conftest import SCRIPTS, TEMPLATES, Git, has_line, matches, read, run, write

INGEST = SCRIPTS / "knowledge-ingest.sh"
INGEST_PY = SCRIPTS / "knowledge-ingest.py"
WORKFLOW = SCRIPTS.parent / "github" / "knowledge-ingest.yaml"
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
    """Serves the routes a test sets: path -> (status, headers, body), or a callable that answers itself, recording every request."""

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
        if callable(route):
            route(self)
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


@pytest.mark.parametrize(("address", "refused"), [
    ("127.0.0.1", True), ("10.0.0.1", True), ("169.254.169.254", True), ("::1", True), ("fe80::1", True), ("fd00::1", True),
    # The shared address space, which is_private leaves out: carrier NAT, Tailscale, Alibaba Cloud's metadata service.
    ("100.64.0.1", True), ("100.100.100.200", True), ("::ffff:100.100.100.200", True),
    ("8.8.8.8", False), ("140.82.112.3", False), ("2606:4700:4700::1111", False), ("2a00:1450:4009::200e", False),
])
def test_an_address_that_is_not_global_is_private(address, refused):
    """Every address that is not global counts as private, and a public one never does."""
    assert load_module().ip_is_private(address) is refused, address


def test_a_name_in_the_shared_address_space_is_refused_before_the_request(checks, monkeypatch):
    """A name that answers 100.100.100.200, Alibaba Cloud's metadata service, is refused like any private address, and nothing is requested."""
    m = load_module()
    real = m.socket.getaddrinfo
    monkeypatch.setattr(m.socket, "getaddrinfo", lambda host, *a, **k: real("100.100.100.200" if host == "meta.example.invalid" else host, *a, **k))
    try:
        m.http_get("http://meta.example.invalid/latest/meta-data/", {}, False, 10_000, timeout=2)
        checks.ok(False, "an address in the shared address space is refused")
    except m.Refused as e:
        checks.ok("private or link-local" in str(e), "an address in the shared address space is refused", str(e))


def test_a_name_that_turns_private_after_the_check_is_refused_at_the_connection(server, checks, monkeypatch):
    """A name may answer a public address to the check and a private one to the connection (DNS rebinding), so the connection checks the address it opens."""
    m = load_module()
    Stub.routes["/r.md"] = (200, {"Content-Type": "text/markdown"}, b"# R\n")
    port = server.rsplit(":", 1)[1]
    url = f"http://rebind.example.invalid:{port}/r.md"
    real = m.socket.getaddrinfo
    answers = iter(["93.184.216.34", "127.0.0.1"])

    def rebinding(host, *args, **kwargs):
        address = next(answers, "127.0.0.1") if host == "rebind.example.invalid" else host
        return real(address, *args, **kwargs)

    monkeypatch.setattr(m.socket, "getaddrinfo", rebinding)
    try:
        m.http_get(url, {}, False, 10_000)
        checks.ok(False, "the second answer is refused")
    except m.Refused as e:
        checks.ok("resolves to 127.0.0.1" in str(e), "the second answer is refused, by the address it named", str(e))
    checks.ok(not Stub.requests, "nothing reached the server", str(Stub.requests))
    # The checked connection still opens to an address it permits.
    monkeypatch.setattr(m.socket, "getaddrinfo", lambda host, *a, **k: real("127.0.0.1", *a, **k))
    monkeypatch.setattr(m, "ip_is_private", lambda address: False)
    checks.ok(m.http_get(url, {}, False, 10_000).data == b"# R\n", "a permitted address is fetched through the checked connection")


def test_through_a_proxy_the_name_is_checked_once_and_the_proxy_resolves_it(server, checks, monkeypatch):
    """A proxy, which may sit on a private address, resolves the source's name itself, so the ingest checks the name before the request and no more."""
    m = load_module()
    url = "http://rebind.example.invalid/r.md"
    Stub.routes[url] = (200, {"Content-Type": "text/markdown"}, b"# R\n")
    for name in ("no_proxy", "NO_PROXY", "HTTP_PROXY"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("http_proxy", server)
    real = m.socket.getaddrinfo
    answers = iter(["93.184.216.34", "127.0.0.1"])
    looked_up = []

    def rebinding(host, *args, **kwargs):
        if host == "rebind.example.invalid":
            looked_up.append(host)
            return real(next(answers, "127.0.0.1"), *args, **kwargs)
        return real(host, *args, **kwargs)

    monkeypatch.setattr(m.socket, "getaddrinfo", rebinding)
    checks.ok(m.http_get(url, {}, False, 10_000).data == b"# R\n", "the proxy, at a private address, fetches a name that answered public")
    checks.ok(looked_up == ["rebind.example.invalid"] and [p for p, _ in Stub.requests] == [url],
              "the ingest looked the name up once, and the proxy got the whole address", f"{looked_up} {Stub.requests}")
    Stub.requests = []
    try:
        m.http_get(url, {}, False, 10_000)
        checks.ok(False, "a name that answers private to the check is refused")
    except m.Refused as e:
        checks.ok("private or link-local" in str(e) and not Stub.requests, "a name that answers private to the check never reaches the proxy", str(e))


def test_git_is_held_to_the_address_the_check_found_and_follows_no_redirect(checks, monkeypatch):
    """Git resolves a name again when it connects, so the ingest hands it the addresses it checked, and a later answer (DNS rebinding) is never asked for."""
    m = load_module()
    if m.git_version() < (2, 37):
        pytest.skip("git 2.37 or later reads http.curloptResolve")
    for name in m.PASSED_THROUGH:
        monkeypatch.delenv(name, raising=False)
    listener = socket.create_server(("127.0.0.1", 0))
    listener.settimeout(30)
    port, reached = listener.getsockname()[1], []

    def accept():
        with contextlib.suppress(OSError):
            conn, _ = listener.accept()
            reached.append(True)
            conn.close()

    threading.Thread(target=accept, daemon=True).start()
    url = f"https://rebind.example.invalid:{port}/acme/wiki.git"
    real = m.socket.getaddrinfo
    answers = iter(["127.0.0.1", "127.0.0.2"])
    looked_up = []

    def rebinding(host, *args, **kwargs):
        if host == "rebind.example.invalid":
            looked_up.append(host)
            return real(next(answers, "127.0.0.2"), *args, **kwargs)
        return real(host, *args, **kwargs)

    # 127.0.0.1 stands for the public answer the check gets, 127.0.0.2 for the private one after it.
    monkeypatch.setattr(m.socket, "getaddrinfo", rebinding)
    monkeypatch.setattr(m, "ip_is_private", lambda address: address != "127.0.0.1")
    ctx = m.Context(m.Manifest(m.MIRROR, 1_000_000, False, []), {}, "2026-10-18T06:00:00Z", 30)
    entry = m.Entry(id="wiki", kind="git", url=url, ref="main")
    try:
        m.run_git(ctx, entry, {})
        checks.ok(False, "the listener speaks no TLS, so the fetch fails")
    except m.FetchFailed:
        pass
    listener.close()
    # The name does not resolve outside this process, so only the pin takes git to the listener.
    checks.ok(reached == [True] and looked_up == ["rebind.example.invalid"], "git connected to the address the check found, which it asked for once",
              f"{reached} {looked_up}")
    answers = iter(["127.0.0.1"])
    pinned = dict(m.git_pin(url))
    checks.ok(pinned == {f"http.{url}.followRedirects": "false", f"http.{url}.curloptResolve": f"rebind.example.invalid:{port}:127.0.0.1"},
              "the pin, and no redirect", str(pinned))
    answers = iter(["127.0.0.2"])
    try:
        m.run_git(ctx, entry, {})
        checks.ok(False, "a name that answers private to the check is refused")
    except m.Refused as e:
        checks.ok("rebind.example.invalid resolves to 127.0.0.2, a private" in str(e), "a name that answers private to the check is refused before git runs, by name and address", str(e))
    answers = iter(["127.0.0.1"])
    monkeypatch.setattr(m, "git_version", lambda: (2, 36))
    try:
        m.git_pin(url)
        checks.ok(False, "a git that cannot be pinned is refused")
    except m.FetchFailed as e:
        checks.ok("git 2.37 or later" in str(e), "a git older than 2.37, which would resolve the name again, is refused", str(e))
    try:
        m.git_pin("https://bücher.example/wiki.git")
        checks.ok(False, "a host name outside ASCII is refused")
    except m.Refused as e:
        checks.ok("xn--" in str(e), "a host name outside ASCII, which git would not match to its pin, is refused", str(e))


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
                  "| Step | Owner |\n| --- | --- |\n| Deploy | team:platform |", "- [x] Tell the channel", "See [Rollback](",
                  "/display/PLAT/Rollback) and [Confluence macro: toc]."):
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
    checks.ok(result and "1 unlisted" in result.out and "124: unlisted since 2026-10-18" in result.out, "a page that left the selection is unlisted, dated", result.out)
    checks.ok((root / ".lokf" / "mirror" / "runbooks" / "124.md").is_file(), "the unlisted file stays")
    result = ingest(root, "--visibility", "private", "--prune")
    checks.ok(result and "went unlisted on this run, so it stays until the next" in result.out and (root / ".lokf" / "mirror" / "runbooks" / "124.md").is_file(), "a prune on the same run keeps it", result.out)
    write(root / ".lokf" / "knowledge" / "playbooks" / "rollback.md", "---\ntype: Playbook\ntitle: Rollback\nresource: .lokf/mirror/runbooks/124.md\n---\n# Rollback\n")
    later = ("--now", "2026-10-25T06:00:00Z")
    result = ingest(root, "--visibility", "private", "--prune", *later)
    checks.ok(result and "a concept still cites it, so it stays" in result.out, "a cited file is kept by --prune", result.out)
    (root / ".lokf" / "knowledge" / "playbooks" / "rollback.md").unlink()
    result = ingest(root, "--visibility", "private", "--prune", *later)
    checks.ok(result and "was unlisted since 2026-10-18 and no concept cites it; removed" in result.out, "an uncited file is removed by a later --prune", result.out)
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
    checks.ok(result and "refused, git does not ignore .lokf/.cache/mirror/" in result.out, "confidential is refused where git would see its copy", result.out)
    checks.ok(not (root / ".lokf" / ".cache").exists(), "and nothing is fetched")
    write(root / ".lokf" / ".gitignore", read(TEMPLATES / "gitignore"))
    result = ingest(root, "--visibility", "public")
    checks.ok(result and "1 fetched" in result.out, "confidential is fetched anywhere, once git ignores the cache", result.out)
    checks.ok(list((root / ".lokf" / ".cache" / "mirror" / "c").glob("*.md")), "and goes to the cache")
    checks.ok(not (root / ".lokf" / "mirror" / "c").exists(), "never to the mirror")
    checks.ok(lock_of(root)["entries"]["c"]["items"] and "a" not in lock_of(root)["entries"], "the lock follows the manifest")
    before = read(root / ".lokf" / "ingest.lock.yaml")
    result = ingest(root, "--visibility", "public", "--dry-run")
    checks.ok(result and read(root / ".lokf" / "ingest.lock.yaml") == before, "a dry run writes nothing", result.out)
    Git(root)("add", "-f", ".lokf/.cache")
    result = ingest(root, "--visibility", "public")
    checks.ok(result and "refused, git tracks files under .lokf/.cache/mirror/" in result.out, "and refused where git tracks a copy", result.out)
    Git(root)("rm", "-r", "-q", "--cached", ".lokf/.cache")
    plain = host(tmp_path / "plain", manifest_for([{"id": "c", "kind": "http", "urls": [url], "sensitivity": "confidential"}]), git=False)
    result = ingest(plain, "--visibility", "public")
    checks.ok(result and "1 fetched" in result.out, "a host without git keeps the copy unchecked, since nothing there commits", result.out)
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for([{"id": "g", "kind": "git", "url": "git://acme.example/x.git", "ref": "main"}])))
    result = ingest(root)
    checks.ok(result.rc == 1 and "ssh and git protocols are not fetched" in result.out, "a git url over the git protocol", result.out)
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for([{"id": "g", "kind": "git", "url": "http://wiki.acme.example/x.git", "ref": "main"}], allow_private_addresses=False)))
    result = ingest(root)
    checks.ok(result.rc == 1 and "is not https; allow_private_addresses: true permits http and local paths" in result.out, "a git url over http needs the allowance", result.out)


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
    (root / ".lokf" / "patch.yaml").unlink()
    # As if the pen had applied it, and a person then added a source of their own.
    fm = dict(op["frontmatter"], sources=[{"resource": "docs/notes.md", "title": "Notes"}, *op["frontmatter"]["sources"]])
    write(root / ".lokf" / "knowledge" / op["path"], "---\n" + yaml.safe_dump(fm, sort_keys=False) + "---\n" + op["body"])
    result = ingest(root, "--patch")
    checks.ok(result and "no entry asks for Reference concepts, or every one has its concept" in result.out, "the concept is current, so nothing is written", result.out)
    Stub.routes["/spec.md"] = (200, {"Content-Type": "text/markdown", "ETag": '"spec-2"'}, b"# Spec\n\nThe spec, revised.\n")
    ingest(root)
    result = ingest(root, "--patch")
    checks.ok(result and "wrote 1 operation for the pen" in result.out, "a newer version gives one patch", result.out)
    op2 = yaml.safe_load(read(root / ".lokf" / "patch.yaml"))["ops"][0]
    checks.ok(op2["op"] == "patch" and op2["path"] == op["path"] and "version spec-2 " in op2["set"]["description"], "a patch of the same concept", str(op2))
    checks.ok([s["resource"] for s in op2["set"]["sources"]] == ["docs/notes.md", op["frontmatter"]["sources"][0]["resource"]], "the person's source stays, the ingest's is replaced", str(op2))


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
    checks.ok(m.shown("a\u200bb\u202ec\x07d\u00a0e") == "abcd e", "invisible characters are removed and a no-break space becomes a space", m.shown("a\u200bb\u202ec\x07d\u00a0e"))
    checks.ok(m.utc("2026-10-03T09:12:44.123+01:00") == "2026-10-03T08:12:44Z" and m.utc("Sat, 18 Oct 2026 06:00:00 GMT") == "2026-10-18T06:00:00Z", "timestamps in one UTC shape")


def test_the_converter_keeps_the_body_after_head_metadata_and_macro_parameters(checks):
    m = load_module()
    page = '<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="x.css"><title>Spec</title></head>' \
           '<body><h1>Spec</h1><p>Frames are <a href="/v3/frames.html">length-prefixed</a>.</p><noscript><img src="x.png"></noscript><p>After.</p></body></html>'
    text, title = m.html_to_markdown(page, "https://vendor.example/spec/v3.html")
    checks.ok(title == "Spec" and text == "# Spec\n\nFrames are [length-prefixed](https://vendor.example/v3/frames.html).\n\nAfter.\n", "a head with metadata keeps the body, and a link is resolved", text)
    storage = '<p>Before.</p><ac:structured-macro ac:name="excerpt-include"><ac:parameter ac:name="page"><ac:link><ri:page ri:content-title="Rollback" /></ac:link></ac:parameter>' \
              '</ac:structured-macro><h2>After</h2><p>See <ac:link><ri:page ri:space-key="OPS" ri:content-title="On call" /></ac:link>.</p>'
    text, _ = m.html_to_markdown(storage, "https://acme.atlassian.net/wiki/spaces/PLAT/pages/123/Deploy")
    checks.ok(text == "Before.\n\n[Confluence macro: excerpt-include]\n\n## After\n\nSee [On call](https://acme.atlassian.net/wiki/display/OPS/On%20call).\n", "a macro parameter holding a page link skips the parameter only", text)
    text, _, _ = m.convert("<html><body><p>caf\xe9</p></body></html>".encode("latin-1"), "text/html", "", "iso-8859-1")
    checks.ok(text == "café\n", "the declared charset decodes a page that is not UTF-8", text)
    text, _, _ = m.convert('<html><head><meta charset="windows-1252"></head><body><p>€ 5</p></body></html>'.encode("cp1252"), "text/html", "")
    checks.ok(text == "€ 5\n", "a charset the page declares is read too", text)
    checks.ok(m.shown("\u0646\u200c\u0647 \U0001f468\u200d\U0001f469 a\u200bb") == "\u0646\u200c\u0647 \U0001f468\u200d\U0001f469 ab", "the joiners stay and the zero-width space goes", m.shown("\u0646\u200c\u0647"))


# 11. the shell half


def test_the_shell_half_refuses_sh(tmp_path, checks):
    result = run(["sh", INGEST, "--status"])
    checks.ok(result.rc == 2 and has_line(result.out, "run this with bash: bash knowledge-ingest.sh [--root <dir>] [--visibility <v>] [--only <id>] [--dry-run] [--prune] [--strict] [--summary <file>] [--status] [--patch [<file>]]"), "refused under sh", result.out)
    result = run(["bash", INGEST, "--root", tmp_path, "--status"])
    checks.ok(result and result.out == "ingest: no .lokf/ingest.yaml, so no source outside the repository is mirrored", "no manifest is one line", result.out)


# 12. redirects and retries


def test_a_redirect_to_another_host_drops_the_credential_and_a_503_is_retried(tmp_path, server, checks):
    port = server.rsplit(":", 1)[1]
    Stub.routes["/a.md"] = (302, {"Location": f"http://localhost:{port}/b.md"}, b"")
    Stub.routes["/b.md"] = (200, {"Content-Type": "text/markdown", "ETag": 'W/"Wv1"'}, b"# B\n")
    calls = []

    def flaky(handler):
        calls.append(1)
        if len(calls) == 1:
            handler.send_response(503)
            handler.send_header("Retry-After", "0")
            handler.end_headers()
            return
        body = b"# C\n"
        handler.send_response(200)
        handler.send_header("Content-Type", "text/markdown")
        handler.send_header("Content-Length", str(len(body)))
        handler.end_headers()
        handler.wfile.write(body)

    Stub.routes["/c.md"] = flaky
    auth = {"scheme": "bearer", "env": "KNOWLEDGE_INGEST_ATLASSIAN_TOKEN"}
    root = host(tmp_path, manifest_for([
        {"id": "r", "kind": "http", "urls": [f"{server}/a.md"], "auth": auth, "sensitivity": "public"},
        {"id": "c", "kind": "http", "urls": [f"{server}/c.md"], "auth": auth, "sensitivity": "public"},
    ]))
    result = ingest(root)
    checks.ok(result and "- r (http, 1 address): 1 fetched" in result.out and "- c (http, 1 address): 1 fetched" in result.out, "both fetched", result.out)
    first = [h for p, h in Stub.requests if p == "/a.md"]
    second = [h for p, h in Stub.requests if p == "/b.md"]
    checks.ok(first and first[0].get("Authorization") == "Bearer secret-token-value", "the first address got the credential", str(first))
    checks.ok(second and "Authorization" not in second[0], "the other host did not", str(second))
    checks.ok(len(calls) == 2, "the 503 was retried once", str(calls))
    item = next(iter(lock_of(root)["entries"]["r"]["items"].values()))
    checks.ok(item["version"] == "Wv1" and item["etag"] == 'W/"Wv1"' and "# B" in read(root / item["path"]), "the redirect target is the mirror, and a weak ETag is the version", str(item))


# 13. a paged Confluence listing, one page gone, an answer of the wrong shape


def test_a_confluence_listing_is_paged_and_one_pages_failure_is_its_own(tmp_path, server, checks):
    pages = {"201": {"title": "One", "version": 1, "storage": "<p>one</p>"}, "202": {"title": "Two", "version": 1, "storage": "<p>two</p>"}}
    confluence_routes(server, True, pages)
    first, second = [{"id": "201", "title": "One", "version": {"number": 1}}], [{"id": "202", "title": "Two", "version": {"number": 1}}]

    def search(handler):
        page = second if "cursor=p2" in handler.path else first
        body = {"results": page, "size": 1}
        if page is first:
            body["_links"] = {"next": "/wiki/rest/api/content/search?cursor=p2&cql=x&limit=50"}
        data = json.dumps(body).encode()
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Content-Length", str(len(data)))
        handler.end_headers()
        handler.wfile.write(data)

    Stub.routes["/wiki/rest/api/content/search"] = search
    Stub.routes.pop("/wiki/api/v2/pages/202")
    root = host(tmp_path, confluence_manifest(server, True))
    result = ingest(root, "--visibility", "private")
    checks.ok(result and "- runbooks (confluence, label ktl): 1 fetched, 1 gone" in result.out, "the second page of the listing was read, and the page without a body is gone on its own", result.out)
    checks.ok("202: gone" in result.out and (root / ".lokf" / "mirror" / "runbooks" / "201.md").is_file(), "the other page is mirrored", result.out)
    Stub.routes["/wiki/rest/api/content/search"] = (200, {"Content-Type": "application/json"}, b"[]")
    result = ingest(root, "--visibility", "private")
    checks.ok(result and "failed, an error this script did not expect, AttributeError" in result.out, "an answer of the wrong shape fails the entry and the run completes", result.out)
    checks.ok(lock_of(root)["entries"]["runbooks"]["items"]["201"]["status"] == "ok", "the entry's items are kept as they were")


# 14. a git entry follows its include, and skips a binary file


def test_a_git_entry_follows_a_changed_include_and_skips_a_binary_file(tmp_path, checks):
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    g = Git(upstream)
    g.init()
    write(upstream / "deploy.md", "# Deploy\n")
    write(upstream / "limits.yaml", "cpu: 2\n")
    (upstream / "logo.png").write_bytes(b"\x89PNG\x00\x00binary")
    g("add", "-A")
    g("commit", "-q", "-m", "one", env=IDENT)
    entry = {"id": "wiki", "kind": "git", "url": str(upstream), "ref": "main", "sensitivity": "public"}
    root = host(tmp_path, manifest_for([entry]))
    result = ingest(root)
    checks.ok(result and "- wiki (git, / at main): 1 fetched" in result.out, "the default include takes the Markdown file", result.out)
    checks.ok(lock_of(root)["entries"]["wiki"]["items"]["deploy.md"]["blob"], "the blob id is recorded")
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for([dict(entry, include=["*"])])))
    result = ingest(root)
    checks.ok(result and "1 fetched, 1 unchanged, 1 skipped" in result.out and "logo.png.md: skipped, a binary file" in result.out, "a changed include at the same commit is followed, and the binary file is named", result.out)
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for([dict(entry, include=["*.yaml"])])))
    result = ingest(root)
    checks.ok(result and "1 unchanged, 1 unlisted" in result.out, "a narrowed include unlists the file it drops", result.out)


# 15. an entry that leaves the manifest


def test_an_entry_that_leaves_the_manifest_takes_its_folder(tmp_path, server, checks):
    Stub.routes["/a.md"] = (200, {"Content-Type": "text/markdown"}, b"# A\n")
    Stub.routes["/b.md"] = (200, {"Content-Type": "text/markdown"}, b"# B\n")
    a = {"id": "a", "kind": "http", "urls": [f"{server}/a.md"], "sensitivity": "public"}
    b = {"id": "b", "kind": "http", "urls": [f"{server}/b.md"], "sensitivity": "public"}
    root = host(tmp_path, manifest_for([a, b]))
    ingest(root)
    b_file = next((root / ".lokf" / "mirror" / "b").glob("*.md"))
    write(root / ".lokf" / "knowledge" / "playbooks" / "b.md", f"---\ntype: Playbook\ntitle: B\nresource: .lokf/mirror/b/{b_file.name}\n---\n# B\n")
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for([a])))
    result = ingest(root, "--dry-run")
    checks.ok(result and f"- b: no longer in the manifest, so .lokf/mirror/b/{b_file.name} is removed, and a concept still cites it" in result.out, "a dry run says what goes", result.out)
    checks.ok(b_file.is_file(), "and removes nothing")
    result = ingest(root)
    checks.ok(result and not (root / ".lokf" / "mirror" / "b").exists() and "b" not in lock_of(root)["entries"], "the folder and the record are gone", result.out)
    checks.ok((root / ".lokf" / "mirror" / "a").is_dir() and "a" in lock_of(root)["entries"], "the other entry is untouched")


# 15b. a cleared mirror


def test_a_cleared_mirror_is_restored_and_the_status_line_counts_what_is_off(tmp_path, server, checks):
    Stub.routes["/a.md"] = (200, {"Content-Type": "text/markdown", "ETag": '"a1"'}, b"# A\n")
    root = host(tmp_path, manifest_for([{"id": "a", "kind": "http", "urls": [f"{server}/a.md"], "sensitivity": "public"}]))
    ingest(root)
    a_file = next((root / ".lokf" / "mirror" / "a").glob("*.md"))
    a_file.unlink()
    write(root / ".lokf" / "mirror" / "a" / "copied-by-hand.md", "# stray\n")
    result = ingest(root, "--status")
    checks.ok(result and "1 missing from the mirror, which a run restores" in result.out and "1 files in the mirror the lock does not name" in result.out, "the status counts the missing and the stray file", result.out)
    result = ingest(root, "--dry-run")
    checks.ok(result and "1 restored" in result.out and not a_file.is_file(), "a dry run says restored and writes nothing", result.out)
    result = ingest(root)
    checks.ok(result and "- a (http, 1 address): 1 restored" in result.out and a_file.is_file() and "# A" in read(a_file), "the run fetches the file again", result.out)
    checks.ok(any(h.get("If-None-Match") is None for p, h in Stub.requests if p == "/a.md"), "without a conditional header, since the copy is gone")
    Stub.routes.pop("/a.md")
    ingest(root)
    result = ingest(root, "--status")
    checks.ok(result and "1 gone or unlisted, which --prune removes" in result.out, "the status counts what waits for a prune", result.out)


# 16. the mirror cap


def test_the_mirror_cap_refuses_the_item_that_would_pass_it(tmp_path, server, checks):
    Stub.routes["/one.md"] = (200, {"Content-Type": "text/markdown"}, b"# One\n" + b"x" * 90)
    Stub.routes["/two.md"] = (200, {"Content-Type": "text/markdown"}, b"# Two\n" + b"y" * 90)
    root = host(tmp_path, manifest_for([{"id": "s", "kind": "http", "urls": [f"{server}/one.md", f"{server}/two.md"], "sensitivity": "public"}], max_total_bytes=150))
    result = ingest(root)
    checks.ok(result and "1 fetched, 1 refused" in result.out and "refused, the mirror would pass max_total_bytes (150)" in result.out, "the second item is refused by name", result.out)
    checks.ok(len(list((root / ".lokf" / "mirror" / "s").glob("*.md"))) == 1, "one file written")


# 17. the workflow's filter


def test_the_workflow_hands_over_the_ingest_secrets_and_no_other(checks):
    if not shutil.which("jq"):
        pytest.skip("jq is not installed")
    m = re.search(r"jq -r '([^']+)'", read(WORKFLOW))
    checks.ok(m is not None, "the workflow filters the secrets with one jq expression")
    secrets = {"github_token": "ghs_x", "KNOWLEDGE_INGEST_ATLASSIAN_TOKEN": "tok=en", "KNOWLEDGE_INGEST_MULTI": "a\nb",
               "knowledge_ingest_lower": "no", "OTHER_SECRET": "z", "KNOWLEDGE_INGEST_GITHUB_TOKEN": "ghp_y"}
    done = subprocess.run(["jq", "-r", m.group(1)], input=json.dumps(secrets), capture_output=True, text=True)
    checks.ok(done.returncode == 0 and done.stdout == "KNOWLEDGE_INGEST_ATLASSIAN_TOKEN=tok=en\nKNOWLEDGE_INGEST_GITHUB_TOKEN=ghp_y\n", "two names, a value with an equals sign kept whole, a multi-line value left out", done.stdout + done.stderr)


def venv_python(root, refuse=""):
    """A .lokf/.venv python that runs this interpreter, and fails the wrapper's import check when it names `refuse`."""
    guard = f'case "$*" in *{refuse}*) exit 1 ;; esac\n' if refuse else ""
    write(root / ".lokf" / ".venv" / "bin" / "python", f'#!/bin/sh\n{guard}exec "{sys.executable}" "$@"\n').chmod(0o755)


def failing_uv(tmp_path):
    """A PATH whose uv fails as uv does behind a package mirror that serves no upload times."""
    uv = write(tmp_path / "fakebin" / "uv", "#!/bin/sh\necho 'x No solution found' >&2\nexit 2\n")
    uv.chmod(0o755)
    return f"{uv.parent}:{os.environ['PATH']}"


def test_a_venv_with_pypdf_runs_the_ingest_before_uv(tmp_path):
    root = tmp_path / "repo"
    (root / ".lokf" / "knowledge").mkdir(parents=True)
    venv_python(root)
    result = run(["bash", INGEST, "--root", root], env={"PATH": failing_uv(tmp_path)})
    assert "no manifest" in result.out and "No solution" not in result.out, f"the ingest did not run from the sidecar's .venv: {result.out}"


def test_a_venv_without_pypdf_leaves_the_ingest_to_uv(tmp_path):
    """uv installs pypdf for the script, so a .venv without it is the fallback, not the first choice."""
    root = tmp_path / "repo"
    (root / ".lokf" / "knowledge").mkdir(parents=True)
    venv_python(root, refuse="pypdf")
    result = run(["bash", INGEST, "--root", root], env={"PATH": failing_uv(tmp_path)})
    assert "No solution" in result.out, f"the ingest chose a .venv without pypdf over uv: {result.out}"


def test_without_uv_a_venv_without_pypdf_still_runs_the_ingest(tmp_path):
    path = "/usr/bin:/bin"
    if shutil.which("uv", path=path):
        pytest.skip("uv is on /usr/bin - the without-uv case cannot be staged here")
    root = tmp_path / "repo"
    (root / ".lokf" / "knowledge").mkdir(parents=True)
    venv_python(root, refuse="pypdf")
    result = run(["bash", INGEST, "--root", root], env={"PATH": path})
    assert "no manifest" in result.out, f"the ingest did not fall back to the .venv's pyyaml: {result.out}"
