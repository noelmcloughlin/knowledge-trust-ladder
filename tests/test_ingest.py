"""knowledge-ingest.py mirrors sources from outside the repository, and has to keep the promises its header makes.

The script is the template every host carries as .lokf/scripts/knowledge-ingest.py.
These tests run it on throwaway repositories against servers of their own,
and pin:

1. an http address is mirrored with its header and its lock record, a second
   run that gets 304 writes nothing, and a changed page is fetched again;
2. a private address, which is any address that is not global, is refused
   unless the manifest allows it, and so is a name that turns private
   between the check and the connection. Git is held to every address the
   check found, and stops at a redirect it would otherwise follow. An IP
   address takes no pin, and an address git's own configuration rewrites is
   refused. Through a proxy, the name is checked once and the proxy
   resolves it, and a name that resolves only at the proxy is not checked.
   Git uses the proxy the check found, or none, whatever its configuration
   or no_proxy says, and through a proxy that resolves names it takes no
   pin;
3. a PDF's text layer is mirrored, and a PDF without one is refused. The
   script's header pins the pypdf these tests install;
4. a Confluence selection is listed with its versions and fetched by v2 on
   Cloud and v1 on Data Center. An unchanged page costs no body, and a page
   that leaves the selection is unlisted. --prune removes an uncited file
   and keeps a cited one;
5. a git path at a ref is mirrored by its commit, with a file that is not
   Markdown kept in a fence. A git older than 2.31 is refused, git reads no
   ~/.netrc, and with a credential git follows no redirect. Only the files
   that changed are downloaded, and a server that refuses files by their
   ids gets the ref fetched whole;
6. a command's output is mirrored, an untracked command is refused, and a
   command past its timeout fails the entry and nothing else. The timeout
   stops every process the command started;
7. the manifest's refusals: an unknown key, a variable name outside the
   KNOWLEDGE_INGEST_ namespace, a value of the wrong type, an internal entry
   in a public repository, and a confidential entry where git would see its
   copy or its record. That entry goes to the cache once git ignores it and
   tracks nothing there, and an entry made confidential leaves the committed
   mirror. The committed lock holds a confidential entry's status alone, and
   no title, address or author, unless the entry sets lock_details. A lock of
   another shape stops the run by name;
8. --patch writes a Reference concept per mirrored item of an entry that asks,
   and a later patch keeps the sources a person added;
9. --status prints one line with the token names and no value, and names
   each git entry a git older than 2.31 or 2.37 would refuse;
10. the converter turns Confluence storage format into Markdown blocks, keeps
    the body after head metadata and macro parameters, resolves links,
    honours a declared charset and keeps the joiners. It reads a head left
    open, keeps a link to an http, https or mailto address only, makes a
    line break in the text a space, and writes no lone surrogate;
11. the shell half refuses to run under sh;
12. a redirect to another host, port or scheme drops the credential, of any
    header name, a 503 is retried, and a weak ETag is the version without
    its prefix. A new ETag for the same bytes is recorded only by a run that
    changes the lock anyway. A secret's trailing line break is trimmed, one
    inside it is refused by name, and a body sent a byte at a time fails at
    a deadline;
13. a Confluence listing is paged, one page's missing body is that page's
    alone, and an answer of the wrong shape fails the entry and nothing else.
    A title arrives as one clean line, and a listing without end is cut off;
14. a git entry follows a changed include at the same commit, and skips a
    binary file by name. A file whose mirror name a Markdown file beside it
    has is skipped, a name the workflow would not publish is spelled plain,
    and a large file is refused;
15. an entry that leaves the manifest takes its folder with it, and no run
    removes or writes a file outside the mirror;
16. the mirror cap refuses the item that would pass it;
17. the workflow's filter hands over the KNOWLEDGE_INGEST_ secrets and no
    other, and a source not fetched or a run cut short is a warning on the run;
18. at its time limit a run starts no more work, and an item or an entry it
    did not reach keeps its record for the next run. A wait the limit cuts
    is the limit's, not the source's.
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
import time
from pathlib import Path

import pytest
import yaml

from conftest import REPO, SCRIPTS, TEMPLATES, Git, has_line, matches, read, run, write

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
    # https, since plain http needs the allowance too. The check refuses the address before any TLS.
    m = manifest_for([{"id": "p", "kind": "http", "urls": [f"{server.replace('http://', 'https://')}/p.md"], "sensitivity": "public"}])
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


def no_outside_dns(real):
    """getaddrinfo as behind a proxy with no outside DNS: a name under example.invalid does not resolve, and the rest as real does."""
    def lookup(host, *args, **kwargs):
        if str(host).endswith(".example.invalid"):
            raise socket.gaierror(socket.EAI_NONAME, "Name or service not known")
        return real(host, *args, **kwargs)
    return lookup


def test_behind_a_proxy_a_name_that_does_not_resolve_here_goes_to_the_proxy(server, checks, monkeypatch):
    """Behind a proxy with no outside DNS only the proxy resolves a source's name, so the ingest sends the request there unchecked, a redirect's too, as the federation build does."""
    m = load_module()
    url = "http://outside.example.invalid/old.md"

    def moved(handler):
        handler.send_response(302)
        handler.send_header("Location", "http://moved.example.invalid/r.md")
        handler.send_header("Content-Length", "0")
        handler.end_headers()

    Stub.routes[url] = moved
    Stub.routes["http://moved.example.invalid/r.md"] = (200, {"Content-Type": "text/markdown"}, b"# R\n")
    for name in ("no_proxy", "NO_PROXY", "HTTP_PROXY", "http_proxy"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(m.socket, "getaddrinfo", no_outside_dns(m.socket.getaddrinfo))
    try:
        m.http_get(url, {}, False, 10_000)
        checks.ok(False, "without a proxy, a name that does not resolve fails")
    except m.FetchFailed as e:
        checks.ok("outside.example.invalid does not resolve" in str(e) and not Stub.requests, "without a proxy, a name that does not resolve fails before the request", str(e))
    monkeypatch.setenv("http_proxy", server)
    checks.ok(m.http_get(url, {}, False, 10_000).data == b"# R\n", "the proxy fetches a name, and a redirect's name, that do not resolve here")
    checks.ok([p for p, _ in Stub.requests] == [url, "http://moved.example.invalid/r.md"], "both requests went to the proxy", str(Stub.requests))
    monkeypatch.setenv("no_proxy", "outside.example.invalid")
    try:
        m.http_get(url, {}, False, 10_000)
        checks.ok(False, "a name that no_proxy sends past the proxy must resolve here")
    except m.FetchFailed as e:
        checks.ok("does not resolve" in str(e), "a name that no_proxy sends past the proxy must resolve here", str(e))


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
    ctx = m.Context(m.Manifest(m.MIRROR, 1_000_000, False, []), {}, 30)
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
    checks.ok(pinned == {f"http.{url}.followRedirects": "false", f"http.{url}.proxy": "",
                         f"http.{url}.curloptResolve": f"rebind.example.invalid:{port}:127.0.0.1"},
              "the pin, no proxy and no redirect", str(pinned))
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


def recording_listener():
    """A socket on 127.0.0.1 that records each connection it accepts, and the list it records them in."""
    listener = socket.create_server(("127.0.0.1", 0))
    listener.settimeout(0.2)
    reached = []

    def accept():
        while True:
            try:
                conn, _ = listener.accept()
            except socket.timeout:
                continue
            except OSError:
                return
            reached.append(True)
            conn.close()

    threading.Thread(target=accept, daemon=True).start()
    return listener, reached


def test_a_pinned_git_stops_at_a_redirect_that_git_would_otherwise_follow(tmp_path, checks, monkeypatch):
    """A redirect would send git to a name it resolves itself, so the pinned fetch stops at the 302; git's default follows it."""
    import ssl

    m = load_module()
    if m.git_version() < (2, 37):
        pytest.skip("git 2.37 or later reads http.curloptResolve")
    if not shutil.which("openssl"):
        pytest.skip("openssl makes the test's certificate")
    for name in m.PASSED_THROUGH:
        monkeypatch.delenv(name, raising=False)
    cert, key = tmp_path / "cert.pem", tmp_path / "key.pem"
    subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", str(key), "-out", str(cert), "-days", "1",
                    "-subj", "/CN=rebind.example.invalid", "-addext", "subjectAltName=DNS:rebind.example.invalid"], check=True, capture_output=True)
    monkeypatch.setenv("GIT_SSL_CAINFO", str(cert))  # passed through to git, as a company's certificate is
    elsewhere, reached = recording_listener()
    asked = []

    class Redirect(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):  # noqa: D102 - quiet
            pass

        def do_GET(self):  # noqa: N802 - the handler's name
            asked.append(self.path)
            self.send_response(302)
            self.send_header("Location", f"https://127.0.0.1:{elsewhere.getsockname()[1]}{self.path}")
            self.send_header("Content-Length", "0")
            self.end_headers()

    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Redirect)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert, key)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        url = f"https://rebind.example.invalid:{httpd.server_address[1]}/acme/wiki.git"
        real = m.socket.getaddrinfo
        monkeypatch.setattr(m.socket, "getaddrinfo", lambda host, *a, **k: real("127.0.0.1" if host == "rebind.example.invalid" else host, *a, **k))
        monkeypatch.setattr(m, "ip_is_private", lambda address: False)  # 127.0.0.1 stands for a public address
        ctx = m.Context(m.Manifest(m.MIRROR, 1_000_000, False, []), {}, 30)
        entry = m.Entry(id="wiki", kind="git", url=url, ref="main")
        try:
            m.run_git(ctx, entry, {})
            checks.ok(False, "the redirect stops the fetch")
        except m.FetchFailed as e:
            checks.ok("302" in str(e), "git stops at the 302", str(e))
        checks.ok(asked == ["/acme/wiki.git/info/refs?service=git-upload-pack"] and not reached,
                  "git asked once, over the pinned TLS connection, and went nowhere else", f"{asked} {reached}")
        # The same pin without followRedirects=false: git follows the redirect, so the setting is what stops it.
        control = tmp_path / "control"
        env = m.git_env(entry, ctx, tmp_path, [p for p in m.git_pin(url) if p[0].endswith("curloptResolve")])
        subprocess.run(["git", "init", "-q", str(control)], env=env, capture_output=True, timeout=60)
        for args in (["remote", "add", "origin", url], ["fetch", "-q", "--depth", "1", "origin", "main"]):
            subprocess.run(["git", "-C", str(control), *args], env=env, capture_output=True, timeout=60)
        checks.ok(reached == [True], "without the setting, git follows the redirect to the other address", str(reached))
    finally:
        httpd.shutdown()
        httpd.server_close()
        elsewhere.close()


def answering(*addresses):
    """getaddrinfo's answer for the addresses, IPv4 and IPv6, port 443, with no resolver asked."""
    return [(socket.AF_INET6, socket.SOCK_STREAM, 6, "", (a, 443, 0, 0)) if ":" in a else (socket.AF_INET, socket.SOCK_STREAM, 6, "", (a, 443))
            for a in addresses]


def test_the_pin_checks_every_answer_and_holds_only_a_named_host(checks, monkeypatch):
    """Every answer is checked and pinned, IPv6 in brackets; an IP address, or a name a proxy resolves, needs no pin and no newer git; a manifest that allows private addresses takes no pin."""
    m = load_module()
    for name in m.PASSED_THROUGH:
        monkeypatch.delenv(name, raising=False)
    names = {"mixed.example.invalid": ["93.184.216.34", "10.0.0.7"], "dual.example.invalid": ["93.184.216.34", "2606:2800:220:1:248:1893:25c8:1946"],
             "six.example.invalid": ["2606:2800:220:1:248:1893:25c8:1946"]}
    monkeypatch.setattr(m.socket, "getaddrinfo", lambda host, *a, **k: answering(*names.get(host, [host])))
    monkeypatch.setattr(m, "git_version", lambda: (2, 43))
    try:
        m.git_pin("https://mixed.example.invalid/wiki.git")
        checks.ok(False, "a name with one private answer among public ones is refused")
    except m.Refused as e:
        checks.ok("mixed.example.invalid resolves to 10.0.0.7" in str(e), "a name with one private answer among public ones is refused", str(e))
    url = "https://dual.example.invalid/wiki.git"
    checks.ok(dict(m.git_pin(url)).get(f"http.{url}.curloptResolve") == "dual.example.invalid:443:93.184.216.34,[2606:2800:220:1:248:1893:25c8:1946]",
              "every answer is pinned, an IPv6 one in brackets", str(m.git_pin(url)))
    url = "https://six.example.invalid/wiki.git"
    checks.ok(dict(m.git_pin(url)).get(f"http.{url}.curloptResolve") == "six.example.invalid:443:[2606:2800:220:1:248:1893:25c8:1946]",
              "an IPv6 answer alone is pinned in brackets", str(m.git_pin(url)))
    monkeypatch.setattr(m, "git_version", lambda: (2, 36))
    url = "https://93.184.216.34/wiki.git"
    checks.ok(m.git_pin(url) == [(f"http.{url}.followRedirects", "false"), (f"http.{url}.proxy", "")], "an IP address takes no pin, so an older git serves",
              str(m.git_pin(url)))
    # A proxy that resolves names gets the name, so a pin would change nothing. For SOCKS5, curl resolves the name, so the pin stays.
    url = "https://dual.example.invalid/wiki.git"
    monkeypatch.setenv("https_proxy", "http://proxy.acme.example.invalid:3128")
    checks.ok(m.git_pin(url) == [(f"http.{url}.followRedirects", "false"), (f"http.{url}.proxy", "http://proxy.acme.example.invalid:3128")],
              "a name an http proxy resolves is checked, takes no pin, and an older git serves", str(m.git_pin(url)))
    monkeypatch.setenv("https_proxy", "socks5://proxy.acme.example.invalid:1080")
    try:
        m.git_pin(url)
        checks.ok(False, "through SOCKS5, curl resolves the name, so the pin and git 2.37 are needed")
    except m.FetchFailed as e:
        checks.ok("git 2.37 or later" in str(e), "through SOCKS5, curl resolves the name, so the pin and git 2.37 are needed", str(e))
    monkeypatch.delenv("https_proxy")
    # A manifest that allows private addresses takes no pin and no check: git connects as it would by hand.
    monkeypatch.setattr(m, "git_pin", lambda url: pytest.fail("a manifest that allows private addresses takes no pin"))
    closed = socket.create_server(("127.0.0.1", 0))
    port = closed.getsockname()[1]
    closed.close()
    ctx = m.Context(m.Manifest(m.MIRROR, 1_000_000, True, []), {}, 30)
    try:
        m.run_git(ctx, m.Entry(id="wiki", kind="git", url=f"https://127.0.0.1:{port}/wiki.git", ref="main"), {})
        checks.ok(False, "nothing listens, so the fetch fails")
    except m.FetchFailed as e:
        checks.ok("fetch failed" in str(e), "the fetch ran unpinned and failed at the closed port", str(e))


def test_behind_a_proxy_git_takes_a_name_that_does_not_resolve_here_unpinned(checks, monkeypatch):
    """Only the proxy can resolve such a name, so git is sent there with no pin and needs no newer git, and still follows no redirect.

    Without a proxy, through SOCKS5, for which curl resolves names, or past the proxy by no_proxy, the name fails.
    """
    m = load_module()
    for name in m.PASSED_THROUGH:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(m.socket, "getaddrinfo", no_outside_dns(m.socket.getaddrinfo))
    monkeypatch.setattr(m, "git_version", lambda: (2, 36))
    url = "https://git.acme.example.invalid/wiki.git"
    try:
        m.git_pin(url)
        checks.ok(False, "without a proxy, a name that does not resolve fails")
    except m.FetchFailed as e:
        checks.ok("git.acme.example.invalid does not resolve" in str(e), "without a proxy, a name that does not resolve fails", str(e))
    proxy = "http://proxy.acme.example.invalid:3128"
    monkeypatch.setenv("https_proxy", proxy)
    checks.ok(m.git_pin(url) == [(f"http.{url}.followRedirects", "false"), (f"http.{url}.proxy", proxy)],
              "through a proxy, the name goes unpinned, to the proxy named, with no redirect", str(m.git_pin(url)))
    monkeypatch.setenv("https_proxy", "socks5h://proxy.acme.example.invalid:1080")
    checks.ok(dict(m.git_pin(url)).get(f"http.{url}.proxy") == "socks5h://proxy.acme.example.invalid:1080", "SOCKS5 with remote names resolves at the proxy too",
              str(m.git_pin(url)))
    monkeypatch.setenv("https_proxy", "socks5://proxy.acme.example.invalid:1080")
    try:
        m.git_pin(url)
        checks.ok(False, "through SOCKS5, curl resolves the name itself, so it must resolve here")
    except m.FetchFailed as e:
        checks.ok("does not resolve" in str(e), "through SOCKS5, curl resolves the name itself, so it must resolve here", str(e))
    monkeypatch.delenv("https_proxy")
    monkeypatch.setenv("ALL_PROXY", proxy)
    checks.ok(dict(m.git_pin(url)).get(f"http.{url}.proxy") == proxy, "git reads all_proxy for https, so the check counts it too", str(m.git_pin(url)))
    monkeypatch.setenv("no_proxy", ".acme.example.invalid")
    try:
        m.git_pin(url)
        checks.ok(False, "a name that no_proxy sends past the proxy must resolve here")
    except m.FetchFailed as e:
        checks.ok("does not resolve" in str(e), "a name that no_proxy sends past the proxy must resolve here", str(e))


def first_lines():
    """A socket on 127.0.0.1 that records the first line of each connection, such as a proxy's CONNECT, and the list it records them in."""
    listener = socket.create_server(("127.0.0.1", 0))
    listener.settimeout(0.2)
    lines = []

    def accept():
        while True:
            try:
                conn, _ = listener.accept()
            except socket.timeout:
                continue
            except OSError:
                return
            conn.settimeout(5)
            with contextlib.suppress(OSError):
                lines.append(conn.recv(4096).decode("latin-1").split("\r\n", 1)[0])
            conn.close()

    threading.Thread(target=accept, daemon=True).start()
    return listener, lines


def test_git_takes_the_route_the_check_found_whatever_its_configuration_says(tmp_path, checks, monkeypatch):
    """Git's own configuration may name another proxy or none, and curl reads no_proxy its own way, so git is told the route the check found."""
    m = load_module()
    for name in m.PASSED_THROUGH:
        monkeypatch.delenv(name, raising=False)
    proxy, through = first_lines()
    other, around = first_lines()
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(write(tmp_path / "gitconfig", f"[http]\n\tproxy = http://127.0.0.1:{other.getsockname()[1]}\n")))
    ctx = m.Context(m.Manifest(m.MIRROR, 1_000_000, False, []), {}, 30)
    real = m.socket.getaddrinfo
    try:
        # Behind a proxy with no outside DNS. curl splits no_proxy at a space and Python does not, so only curl would bypass the proxy.
        monkeypatch.setattr(m.socket, "getaddrinfo", no_outside_dns(real))
        monkeypatch.setenv("https_proxy", f"http://127.0.0.1:{proxy.getsockname()[1]}")
        monkeypatch.setenv("no_proxy", "git.acme.example.invalid unused.example.invalid")
        with contextlib.suppress(m.FetchFailed):
            m.run_git(ctx, m.Entry(id="wiki", kind="git", url="https://git.acme.example.invalid/acme/wiki.git", ref="main"), {})
        checks.ok(set(through) == {"CONNECT git.acme.example.invalid:443 HTTP/1.1"} and not around,
                  "git went through the proxy the check found, by name", f"{through} {around}")
        if m.git_version() < (2, 37):
            return  # the direct route below takes the pin, which an older git refuses
        # No proxy in the environment: git connects to the checked address, not to the proxy its configuration names.
        monkeypatch.delenv("https_proxy")
        monkeypatch.delenv("no_proxy")
        monkeypatch.setattr(m.socket, "getaddrinfo", lambda host, *a, **k: real("127.0.0.1" if host == "git.acme.example.invalid" else host, *a, **k))
        monkeypatch.setattr(m, "ip_is_private", lambda address: False)  # 127.0.0.1 stands for a public address
        closed = socket.create_server(("127.0.0.1", 0))
        port = closed.getsockname()[1]
        closed.close()
        with contextlib.suppress(m.FetchFailed):
            m.run_git(ctx, m.Entry(id="wiki", kind="git", url=f"https://git.acme.example.invalid:{port}/acme/wiki.git", ref="main"), {})
        checks.ok(not around, "git connected directly, as the check did, and not to the proxy its configuration names", str(around))
    finally:
        proxy.close()
        other.close()


def test_git_reads_no_netrc(server, tmp_path, checks, monkeypatch):
    """curl sends the credential of a ~/.netrc default entry to any host that asks, so git runs with a HOME of the run's own."""
    m = load_module()
    for name in m.PASSED_THROUGH:
        monkeypatch.delenv(name, raising=False)
    write(tmp_path / "home" / ".netrc", "default login netrc-user password netrc-secret\n").chmod(0o600)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))

    def challenge(handler):
        handler.send_response(401)
        handler.send_header("WWW-Authenticate", 'Basic realm="wiki"')
        handler.send_header("Content-Length", "0")
        handler.end_headers()

    Stub.routes["/wiki.git/info/refs"] = challenge
    ctx = m.Context(m.Manifest(m.MIRROR, 1_000_000, True, []), {}, 30)
    with contextlib.suppress(m.FetchFailed):
        m.run_git(ctx, m.Entry(id="wiki", kind="git", url=f"{server}/wiki.git", ref="main"), {})
    sent = [h.get("Authorization", "") for _, h in Stub.requests]
    checks.ok(sent and not any(sent), "git asked, and sent no credential from ~/.netrc", str(sent))


def test_a_git_address_that_git_rewrites_is_refused(tmp_path, checks, monkeypatch):
    """Git rewrites an address by a url.<base>.insteadOf in its own configuration, which the pin and the credential would not cover, so the entry is refused before any fetch."""
    m = load_module()
    for name in m.PASSED_THROUGH:
        monkeypatch.delenv(name, raising=False)
    config = write(tmp_path / "gitconfig", '[url "https://mirror.example.invalid/"]\n\tinsteadOf = https://git.acme.example.invalid/\n')
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(config))
    monkeypatch.setattr(m.socket, "getaddrinfo", lambda host, *a, **k: answering("93.184.216.34"))
    monkeypatch.setattr(m, "git_version", lambda: (2, 43))
    ctx = m.Context(m.Manifest(m.MIRROR, 1_000_000, False, []), {}, 30)
    try:
        m.run_git(ctx, m.Entry(id="wiki", kind="git", url="https://git.acme.example.invalid/acme/wiki.git", ref="main"), {})
        checks.ok(False, "a rewritten address is refused")
    except m.Refused as e:
        checks.ok("rewrites https://git.acme.example.invalid/acme/wiki.git to https://mirror.example.invalid/acme/wiki.git" in str(e),
                  "a rewritten address is refused, naming both addresses", str(e))


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


def test_the_header_pins_the_pypdf_the_tests_install(checks):
    """pypdf reads PDFs from outside the repository, and Dependabot raises it in tests/requirements.txt but cannot read the script's header."""
    header = re.search(r'"pypdf==([^"]+)"', read(INGEST_PY))
    tests = re.search(r"^pypdf==(\S+)$", read(REPO / "tests" / "requirements.txt"), re.M)
    checks.ok(header and tests and header.group(1) == tests.group(1),
              "the script's header pins the pypdf the tests run; move exclude-newer past its upload with it",
              f"header {header and header.group(1)}, tests {tests and tests.group(1)}")


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
    write(root / ".lokf" / "ingest.yaml", read(root / ".lokf" / "ingest.yaml").replace(str(upstream), "../upstream"))
    result = ingest(root)
    checks.ok(result and "2 unchanged" in result.out, "a relative path is read against the repository root, not git's own folder", result.out)


def test_a_git_older_than_2_31_is_refused_for_every_git_entry(tmp_path, checks, monkeypatch):
    """An older git ignores GIT_CONFIG_COUNT, so the protocol limits and the credential would not hold. The entry is refused even where no pin is taken."""
    m = load_module()
    monkeypatch.setattr(m, "git_version", lambda: (2, 30))
    monkeypatch.setattr(m, "git_pin", lambda url: pytest.fail("the version is checked before any address"))
    ctx = m.Context(m.Manifest(m.MIRROR, 1_000_000, True, []), {}, 30)
    try:
        m.run_git(ctx, m.Entry(id="wiki", kind="git", url=str(tmp_path), ref="main"), {})
        checks.ok(False, "a git older than 2.31 is refused")
    except m.FetchFailed as e:
        checks.ok("git 2.31 or later" in str(e) and str(e).endswith("this git is 2.30"), "a git older than 2.31 is refused, naming its version", str(e))


def test_a_git_entry_with_a_credential_follows_no_redirect(tmp_path, server, checks):
    """On a redirect to another host, curl drops an Authorization header and keeps a header of any other name, so with a credential git follows none, even where the manifest allows private addresses."""
    port = server.rsplit(":", 1)[1]
    Stub.routes["/wiki.git/info/refs"] = (302, {"Location": f"http://localhost:{port}/moved.git/info/refs?service=git-upload-pack"}, b"")
    auth = {"scheme": "header", "header": "X-Api-Key", "env": "KNOWLEDGE_INGEST_ATLASSIAN_TOKEN"}
    root = host(tmp_path, manifest_for([{"id": "wiki", "kind": "git", "url": f"{server}/wiki.git", "ref": "main", "auth": auth, "sensitivity": "public"}]))
    result = ingest(root)
    checks.ok(result and "- wiki (git, / at main): failed, git fetch failed" in result.out, "the fetch stops at the redirect", result.out)
    checks.ok(any(p.startswith("/wiki.git/") and h.get("X-Api-Key") == "secret-token-value" for p, h in Stub.requests),
              "the address the manifest names gets the credential", str(Stub.requests))
    checks.ok(not any(p.startswith("/moved.git/") for p, _ in Stub.requests), "the other host gets no request, so no credential", str(Stub.requests))


def test_a_git_entry_downloads_only_the_files_that_changed(tmp_path, checks, monkeypatch):
    """The first fetch takes the commit and its trees, then the run asks for each chosen file whose blob id the lock does not hold. A file refused
    for its size is not asked for again while it and the cap stay the same. Where the server takes the filter and then refuses files by their
    ids, as a server that speaks only git's first protocol does, the ref is fetched again whole."""
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    g = Git(upstream)
    g.init()
    g("config", "uploadpack.allowFilter", "true")
    for name in ("a", "b", "c"):
        write(upstream / f"{name}.md", f"# {name}\n")
    write(upstream / "big.md", "x" * 3000)
    write(upstream / "elsewhere" / "huge.bin", "y" * 50_000)
    g("add", "-A")
    g("commit", "-q", "-m", "one", env=IDENT)
    m = load_module()
    calls = []
    real = subprocess.run

    def recording(args, *rest, **kwargs):
        if args[:1] == ["git"]:
            calls.append((list(args), kwargs.get("input") or b""))
        return real(args, *rest, **kwargs)

    monkeypatch.setattr(m.subprocess, "run", recording)
    ctx = m.Context(m.Manifest(m.MIRROR, 1_000_000, True, []), {}, 30)
    entry = m.Entry(id="wiki", kind="git", url=str(upstream), ref="main", include=["*.md"], max_item_bytes=2000)
    oid = {name: g("rev-parse", f"HEAD:{name}") for name in ("a.md", "b.md", "c.md", "big.md")}
    items, unchanged = m.run_git(ctx, entry, {})
    fetches = [(args, data.decode().split()) for args, data in calls if "fetch" in args]
    checks.ok(len(fetches) == 2 and "--filter=blob:none" in fetches[0][0] and sorted(fetches[1][1]) == sorted(oid.values()),
              "the first fetch takes no file, and the second the four chosen ones, not the file outside the include", str(fetches))
    by = {it.item: it for it in items}
    checks.ok(by["big.md"].refused == "over max_item_bytes (2000)" and by["big.md"].blob == oid["big.md"] and "# b" in by["b.md"].text,
              "a file over the cap is refused with its blob id, and the others are read", str(items))
    prior = {it.item: {"status": "ok", "blob": it.blob, "sha256": "sha256:" + it.sha256} for it in items if not it.refused}
    prior["big.md"] = {"status": "refused", "reason": "over max_item_bytes (2000)", "blob": oid["big.md"]}
    write(upstream / "a.md", "# a, changed\n")
    g("add", "-A")
    g("commit", "-q", "-m", "two", env=IDENT)
    calls.clear()
    items, unchanged = m.run_git(ctx, entry, prior)
    asked = [data.decode().split() for args, data in calls if "--stdin" in args]
    checks.ok(asked == [[g("rev-parse", "HEAD:a.md")]] and [it.item for it in items] == ["a.md"] and sorted(unchanged) == ["b.md", "big.md", "c.md"],
              "the next run asks for the changed file alone, and leaves the refused one as it was", str(asked))
    real_env = m.git_env

    def first_protocol(*args, **kwargs):
        env = real_env(*args, **kwargs)
        n = int(env["GIT_CONFIG_COUNT"])
        env[f"GIT_CONFIG_KEY_{n}"], env[f"GIT_CONFIG_VALUE_{n}"], env["GIT_CONFIG_COUNT"] = "protocol.version", "0", str(n + 1)
        return env

    monkeypatch.setattr(m, "git_env", first_protocol)
    calls.clear()
    items, unchanged = m.run_git(ctx, entry, {})
    fetches = [args for args, _ in calls if "fetch" in args]
    checks.ok(len(fetches) == 3 and "--filter=blob:none" in fetches[0] and "--stdin" in fetches[1] and "--filter=blob:none" not in fetches[2]
              and sorted(it.item for it in items if it.text) == ["a.md", "b.md", "c.md"], "refused its files by id, the run fetches the ref whole", str(fetches))


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
    write(root / ".lokf" / "ingest" / "schema.sh", read(root / ".lokf" / "ingest" / "schema.sh") + "echo edited\n")
    result = ingest(root)
    checks.ok(result and "refused, .lokf/ingest/schema.sh has changes git has not committed" in result.out, "a command edited since its commit is refused", result.out)


def alive(pid: int) -> bool:
    """Whether a process runs, a zombie counting as gone."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    try:
        return read(Path(f"/proc/{pid}/stat")).rsplit(")", 1)[-1].split()[0] != "Z"
    except (FileNotFoundError, ProcessLookupError):  # gone between the two looks, or no /proc to ask
        return not Path("/proc/self").exists()


def test_a_command_stopped_by_a_timeout_takes_every_process_it_started(tmp_path, checks):
    """A command stopped alone would leave a process it started in the background running, holding its output open. Its own timeout and the run's
    time limit both stop the whole group, and the time limit leaves the entry's record for the next run."""
    if not hasattr(os, "killpg"):
        pytest.skip("no process groups here")
    m = load_module()
    root = host(tmp_path, manifest_for([{"id": "slow", "kind": "command", "command": ".lokf/ingest/slow.sh", "sensitivity": "public"}]))
    write(root / ".lokf" / "ingest" / "slow.sh", "#!/bin/sh\nsleep 30 &\necho $! > \"$1\"\nwait\n").chmod(0o755)
    Git(root)("add", "-A")
    Git(root)("commit", "-q", "-m", "slow", env=IDENT)
    for name, raised in (("timeout", m.FetchFailed), ("time limit", m.OutOfTime)):
        pid_file = tmp_path / f"{name.replace(' ', '-')}.pid"
        until = time.monotonic() + 1 if raised is m.OutOfTime else 0.0
        ctx = m.Context(m.Manifest(m.MIRROR, 1_000_000, True, []), {}, 30, root, until)
        started = time.monotonic()
        try:
            m.run_command(ctx, m.Entry(id="slow", kind="command", command=".lokf/ingest/slow.sh", args=[str(pid_file)], timeout=1 if not until else 60), {}, root)
            checks.ok(False, f"the {name} stops the command")
        except raised:
            pass
        pid = int(read(pid_file))
        deadline = time.monotonic() + 3
        while alive(pid) and time.monotonic() < deadline:
            time.sleep(0.05)
        checks.ok(not alive(pid) and time.monotonic() - started < 5, f"the {name} stops the process the command left in the background too")


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
    write(root / ".lokf" / ".gitignore", ".cache/mirror/\n")
    result = ingest(root, "--visibility", "public")
    checks.ok(result and "refused, git does not ignore .lokf/.cache/ingest.lock.yaml" in result.out and not (root / ".lokf" / ".cache").exists(),
              "and where git would see the records of its copy", result.out)
    write(root / ".lokf" / ".gitignore", read(TEMPLATES / "gitignore"))
    result = ingest(root, "--visibility", "public")
    checks.ok(result and "1 fetched" in result.out, "confidential is fetched anywhere, once git ignores the cache", result.out)
    checks.ok(list((root / ".lokf" / ".cache" / "mirror" / "c").glob("*.md")), "and goes to the cache")
    checks.ok(not (root / ".lokf" / "mirror" / "c").exists(), "never to the mirror")
    checks.ok(lock_of(root)["entries"]["c"] == {"status": "ok"} and "a" not in lock_of(root)["entries"],
              "the committed lock holds the confidential entry's status alone, and follows the manifest", str(lock_of(root)))
    checks.ok(yaml.safe_load(read(root / ".lokf" / ".cache" / "ingest.lock.yaml"))["entries"]["c"]["items"]
              and ".cache" not in Git(root)("status", "--porcelain", "--untracked-files=all"), "its records are in the cache's lock, which git ignores")
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
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for([{"id": "h", "kind": "http", "urls": ["http://vendor.example/spec.md"]}], allow_private_addresses=False)))
    result = ingest(root)
    checks.ok(result.rc == 1 and "http://vendor.example/spec.md is over http; use https, or allow_private_addresses: true" in result.out,
              "an http address needs the allowance too, as the manifest's comment says", result.out)


def test_the_manifest_refuses_a_value_of_the_wrong_type(tmp_path, checks):
    """Python counts the string "false" as true, and a string where a list belongs as a list of its characters, so each is refused by name."""
    url = "https://vendor.example/spec.md"
    cases = [
        (manifest_for([{"id": "a", "kind": "http", "urls": [url]}], allow_private_addresses="false"), "allow_private_addresses is true or false, without quotes"),
        (manifest_for([{"id": "a", "kind": "http", "urls": [url], "disabled": "no"}]), "entries.a.disabled is true or false, without quotes"),
        (manifest_for([{"id": "a", "kind": "http", "urls": url}]), "entries.a.urls is a list, not a single string"),
        (manifest_for([{"id": "a", "kind": "git", "url": "https://acme.example/wiki.git", "ref": "main", "include": "docs/*.md"}]),
         "entries.a.include is a list, not a single string"),
        (manifest_for([{"id": "a", "kind": "command", "command": "x.sh", "args": "--format markdown"}]), "entries.a.args is a list, not a single string"),
        (manifest_for([{"id": "a", "kind": "confluence", "site": "https://acme.atlassian.net", "select": "label"}]),
         "entries.a: select is a mapping, such as label: ktl"),
    ]
    root = host(tmp_path, cases[0][0], git=False)
    for manifest, message in cases:
        write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest))
        result = ingest(root)
        checks.ok(result.rc == 1 and f"knowledge-ingest: {message}" in result.out and "Traceback" not in result.out, message, result.out)
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for([{"id": "a", "kind": "http", "urls": [url]}])))
    for lock in ("ingest_lock_version: '1'\nentries:\n  a: [1, 2]\n", "ingest_lock_version: '1'\nentries:\n  a:\n    items:\n      x: one\n", "- one\n"):
        write(root / ".lokf" / "ingest.lock.yaml", lock)
        result = ingest(root)
        checks.ok(result.rc == 1 and "knowledge-ingest: ingest.lock.yaml: " in result.out and "Traceback" not in result.out,
                  "a lock edited into another shape stops the run by name", result.out)


def test_an_entry_made_confidential_leaves_the_committed_mirror(tmp_path, server, checks):
    """Sensitivity picks the mirror, so a copy written while the entry was internal is removed once it is confidential, and fetched again into the cache."""
    Stub.routes["/pay.md"] = (200, {"Content-Type": "text/markdown"}, b"# Pay bands\n")
    entry = {"id": "pay", "kind": "http", "urls": [f"{server}/pay.md"], "sensitivity": "internal"}
    root = host(tmp_path, manifest_for([entry]))
    write(root / ".lokf" / ".gitignore", read(TEMPLATES / "gitignore"))
    ingest(root, "--visibility", "private")
    committed = list((root / ".lokf" / "mirror" / "pay").glob("*.md"))
    checks.ok(len(committed) == 1, "an internal entry is mirrored where git commits it")
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for([dict(entry, sensitivity="confidential")])))
    result = ingest(root, "--visibility", "private")
    cached = list((root / ".lokf" / ".cache" / "mirror" / "pay").glob("*.md"))
    checks.ok(result and committed and not committed[0].exists() and len(cached) == 1 and "# Pay bands" in read(cached[0]),
              "made confidential, its copy leaves the committed mirror for the cache", result.out)
    item = next(iter(yaml.safe_load(read(root / ".lokf" / ".cache" / "ingest.lock.yaml"))["entries"]["pay"]["items"].values()))
    checks.ok(item["path"].startswith(".lokf/.cache/mirror/pay/") and lock_of(root)["entries"]["pay"] == {"status": "ok"},
              "the record follows the copy to the cache's lock", str(item))
    checks.ok("- pay: its sensitivity puts its files in .lokf/.cache/mirror/pay/, so 1 file elsewhere is removed" in result.out, "the summary says so", result.out)
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for([entry])))
    result = ingest(root, "--visibility", "private")
    checks.ok(result and len(list((root / ".lokf" / "mirror" / "pay").glob("*.md"))) == 1 and not list((root / ".lokf" / ".cache" / "mirror").rglob("*.md"))
              and "pay" not in yaml.safe_load(read(root / ".lokf" / ".cache" / "ingest.lock.yaml"))["entries"]
              and lock_of(root)["entries"]["pay"]["items"], "made internal again, the copy and its record come back to the committed mirror and lock", result.out)


def test_a_confidential_entry_commits_no_title_address_or_author_unless_it_asks(tmp_path, server, checks):
    """The lock is committed, so a confidential page's record stays in the cache's lock, and the committed one says how the entry's run went.
    lock_details: true records the items in the committed lock, as for any entry, and turned off again they move back."""
    pages = {"908123": {"title": "Pay review", "version": 2, "storage": "<p>Bands rise in April.</p>"}}
    confluence_routes(server, True, pages)
    Stub.routes["/wiki/rest/api/content/search"] = (200, {"Content-Type": "application/json"}, json.dumps({"results": [
        {"id": "908123", "title": "Pay review", "version": {"number": 2, "when": "2026-10-03T09:12:44Z", "by": {"accountId": "5b10ac8d"}},
         "_links": {"webui": "/spaces/HR/pages/908123/Pay+review"}},
        {"id": "908124", "title": "Redundancy list", "version": {"number": 1, "by": {"accountId": "7c20bd9e"}},
         "_links": {"webui": "/spaces/HR/pages/908124/Redundancy+list"}},
        {"id": "908125", "title": "Board minutes", "version": {"number": 5, "by": {"accountId": "7c20bd9e"}},
         "_links": {"webui": "/spaces/HR/pages/908125/Board+minutes"}}]}).encode())
    Stub.routes["/wiki/api/v2/pages/908125"] = (200, {"Content-Type": "text/html"}, b"<html><body>Sign in</body></html>")
    m = confluence_manifest(server, True)
    m["entries"][0]["sensitivity"] = "confidential"
    root = host(tmp_path, m)
    write(root / ".lokf" / ".gitignore", read(TEMPLATES / "gitignore"))
    result = ingest(root, "--visibility", "public")
    committed = read(root / ".lokf" / "ingest.lock.yaml")
    checks.ok(result and "- runbooks (confluence, label ktl): 1 fetched, 1 gone, 1 failed" in result.out and lock_of(root)["entries"]["runbooks"] == {"status": "ok"},
              "the committed lock says how the run went", result.out + committed)
    for secret in ("Pay review", "Redundancy", "Board minutes", "/spaces/HR", "5b10ac8d", "908123", "908124", "908125", "/wiki/api"):
        checks.ok(secret not in committed and secret not in result.out, f"neither the committed lock nor the summary holds {secret}", result.out + committed)
    checks.ok("  - 1 item: gone" in result.out and f"  - 1 item: failed, {server} did not return JSON" in result.out,
              "the summary counts the pages that went and failed, names none, and cuts an address in a reason to its site", result.out)
    cached = yaml.safe_load(read(root / ".lokf" / ".cache" / "ingest.lock.yaml"))["entries"]["runbooks"]["items"]
    checks.ok(cached["908123"]["title"] == "Pay review" and cached["908123"]["author"] == "5b10ac8d" and "/spaces/HR/pages/908123/" in cached["908123"]["origin"],
              "the cache's lock records title, address and author", str(cached))
    checks.ok("author: 5b10ac8d" in read(root / ".lokf" / ".cache" / "mirror" / "runbooks" / "908123.md"), "and the copy's header holds them, for the librarian")
    result = ingest(root, "--visibility", "public")
    checks.ok(result and "1 unchanged" in result.out, "the cache's lock is what keeps an unchanged page from being fetched again", result.out)
    shutil.rmtree(root / ".lokf" / ".cache")
    result = ingest(root, "--visibility", "public", "--now", "2026-10-25T06:00:00Z")
    checks.ok(result and "1 fetched" in result.out and read(root / ".lokf" / "ingest.lock.yaml") == committed,
              "a checkout without the cache, as in the workflow, fetches the copy again and changes no line of the committed lock", result.out)
    m["entries"][0]["lock_details"] = True
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(m))
    result = ingest(root, "--visibility", "public")
    items = lock_of(root)["entries"]["runbooks"]["items"]
    checks.ok(result and items["908123"]["title"] == "Pay review" and items["908123"]["author"] == "5b10ac8d" and "908124: gone" in result.out
              and "runbooks" not in yaml.safe_load(read(root / ".lokf" / ".cache" / "ingest.lock.yaml"))["entries"],
              "lock_details: true moves the records to the committed lock, and the summary names the pages", result.out + str(items))
    checks.ok("1 unchanged" in result.out, "the copy in the cache counts as current, so the switch fetches nothing", result.out)
    m["entries"][0]["disabled"] = True
    del m["entries"][0]["lock_details"]
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(m))
    with_details = read(root / ".lokf" / "ingest.lock.yaml")
    result = ingest(root, "--visibility", "public")
    checks.ok(result and read(root / ".lokf" / "ingest.lock.yaml") == with_details,
              "turned off again on an entry that does not run, the records stay where they are until it does", result.out)
    del m["entries"][0]["disabled"]
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(m))
    result = ingest(root, "--visibility", "public")
    checks.ok(result and "1 unchanged" in result.out and lock_of(root)["entries"]["runbooks"] == {"status": "ok"}
              and yaml.safe_load(read(root / ".lokf" / ".cache" / "ingest.lock.yaml"))["entries"]["runbooks"]["items"]["908123"]["title"] == "Pay review",
              "once it runs, they move to the cache's lock, and the copy there counts as current", read(root / ".lokf" / "ingest.lock.yaml"))
    Stub.routes["/wiki/rest/api/content/search"] = (200, {"Content-Type": "application/json"}, json.dumps({"results": []}).encode())
    copy = root / ".lokf" / ".cache" / "mirror" / "runbooks" / "908123.md"
    result = ingest(root, "--visibility", "public", "--prune", "--now", "2026-11-01T06:00:00Z")
    checks.ok(result and "- runbooks: a confidential copy went unlisted on this run, so it stays until the next" in result.out and copy.is_file(),
              "a page that left the selection is unlisted, and the summary names no path", result.out)
    result = ingest(root, "--visibility", "public", "--prune", "--now", "2026-11-08T06:00:00Z")
    checks.ok(result and "- runbooks: a confidential copy was unlisted since 2026-11-01 and no concept cites it; removed" in result.out
              and not copy.exists() and "908123" not in result.out, "a later prune removes the copy, naming none", result.out)


def test_records_move_between_the_locks_only_when_the_entry_runs(tmp_path, server, checks, monkeypatch, capsys):
    """An entry that does not run, or that is refused, keeps its records and its copies where they are, so a record that names a committed copy is
    never lost before the copy goes. Only an entry that runs to an end rewrites its line in the committed lock: a stop at the time limit, or
    --only another entry, leaves it as it was."""
    Stub.routes["/pay.md"] = (200, {"Content-Type": "text/markdown"}, b"# Pay bands\n")
    Stub.routes["/pub.md"] = (200, {"Content-Type": "text/markdown"}, b"# Public\n")
    pay = {"id": "pay", "kind": "http", "urls": [f"{server}/pay.md"], "sensitivity": "internal"}
    pub = {"id": "pub", "kind": "http", "urls": [f"{server}/pub.md"], "sensitivity": "public"}
    root = host(tmp_path / "a", manifest_for([pay, pub]))
    write(root / ".lokf" / ".gitignore", read(TEMPLATES / "gitignore"))
    ingest(root, "--visibility", "private")
    copy = next((root / ".lokf" / "mirror" / "pay").glob("*.md"))
    before = lock_of(root)["entries"]["pay"]
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for([dict(pay, sensitivity="confidential", disabled=True), pub])))
    result = ingest(root, "--visibility", "private")
    checks.ok(result and lock_of(root)["entries"]["pay"] == before and copy.is_file(),
              "made confidential and disabled in one change, the entry keeps its records and its copy", result.out)
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for([dict(pay, sensitivity="confidential"), pub])))
    shutil.rmtree(root / ".lokf" / ".cache", ignore_errors=True)
    result = ingest(root, "--visibility", "private")
    status = ingest(root, "--status")
    checks.ok(result and not copy.exists() and lock_of(root)["entries"]["pay"] == {"status": "ok"} and "does not name" not in status.out,
              "once it runs, on a checkout without the cache, its copy leaves the committed mirror and no stray file stays", result.out + status.out)

    exposed = host(tmp_path / "b", manifest_for([pay]))
    ingest(exposed, "--visibility", "private")
    copy = next((exposed / ".lokf" / "mirror" / "pay").glob("*.md"))
    before = lock_of(exposed)["entries"]["pay"]
    write(exposed / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for([dict(pay, sensitivity="confidential")])))
    result = ingest(exposed, "--visibility", "private")
    line = lock_of(exposed)["entries"]["pay"]
    checks.ok(result and "refused, git does not ignore .lokf/.cache/mirror/" in result.out and line["status"] == "refused"
              and line["items"] == before["items"] and copy.is_file(), "refused where git would see the cache, it keeps its records and its copy", str(line))
    checks.ok("Mirror: 1 file," in result.out, "and the summary still counts the copy those records name", result.out)
    write(exposed / ".lokf" / ".gitignore", read(TEMPLATES / "gitignore"))
    result = ingest(exposed, "--visibility", "private")
    checks.ok(result and not copy.exists() and lock_of(exposed)["entries"]["pay"] == {"status": "ok"}, "and once git ignores the cache, they go", result.out)

    write(root / ".lokf" / "ingest.lock.yaml", yaml.safe_dump({"ingest_lock_version": "1", "entries": {
        "pay": {"status": "failed", "reason": "gave up after 3 attempts"}, "pub": lock_of(root)["entries"]["pub"]}}))
    failed = read(root / ".lokf" / "ingest.lock.yaml")
    shutil.rmtree(root / ".lokf" / ".cache", ignore_errors=True)
    m = load_module()

    def stopped(*args, **kwargs):
        raise m.OutOfTime()

    monkeypatch.setattr(m, "run_http", stopped)
    rc = m.main(["--root", str(root), "--visibility", "private", "--only", "pay"])
    out = capsys.readouterr().out
    checks.ok(rc == 0 and "- pay (http, 1 address): stopped, the run's time limit passed while it ran" in out and read(root / ".lokf" / "ingest.lock.yaml") == failed,
              "a stop at the time limit leaves the committed line as it was", out)
    write(root / ".lokf" / ".cache" / "ingest.lock.yaml", yaml.safe_dump({"ingest_lock_version": "1", "entries": {"pay": {"status": "refused", "reason": "an old run here", "items": {}}}}))
    result = ingest(root, "--visibility", "private", "--only", "pub")
    checks.ok(result and lock_of(root)["entries"]["pay"] == {"status": "failed", "reason": "gave up after 3 attempts"},
              "--only another entry leaves it as it was, whatever this machine's cache says", read(root / ".lokf" / "ingest.lock.yaml"))


def test_a_confidential_command_s_output_stays_out_of_the_summary_and_the_committed_lock(tmp_path, checks):
    """A command prints what it likes when it fails, so for a confidential entry the summary and the committed lock give its exit status alone."""
    root = host(tmp_path, manifest_for([{"id": "hr", "kind": "command", "command": ".lokf/ingest/hr.sh", "sensitivity": "confidential"}]))
    write(root / ".lokf" / ".gitignore", read(TEMPLATES / "gitignore"))
    write(root / ".lokf" / "ingest" / "hr.sh", "#!/bin/sh\necho 'no access to Pay review for Alice Example' >&2\nexit 3\n").chmod(0o755)
    Git(root)("add", "-A")
    Git(root)("commit", "-q", "-m", "hr", env=IDENT)
    result = ingest(root, "--visibility", "private")
    checks.ok(result and "- hr (command, .lokf/ingest/hr.sh): failed, the command exited 3" in result.out and "Alice" not in result.out
              and lock_of(root)["entries"]["hr"] == {"status": "failed", "reason": "the command exited 3"}, "the exit status alone", result.out)
    checks.ok("Alice" in yaml.safe_load(read(root / ".lokf" / ".cache" / "ingest.lock.yaml"))["entries"]["hr"]["reason"],
              "the cache's lock keeps the line, for the person who runs it")


def test_lock_details_change_no_line_when_only_the_cache_is_missing(tmp_path, server, checks):
    """With lock_details: true, the workflow's checkout restores every confidential copy. A copy whose bytes did not change keeps its record, as an
    unchanged one does, though the repository's commit or the server's validators moved, and its file comes back byte for byte."""
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    g = Git(upstream)
    g.init()
    write(upstream / "docs" / "a.md", "# A\n")
    write(upstream / "other" / "b.txt", "one\n")
    g("add", "-A")
    g("commit", "-q", "-m", "one", env=IDENT)
    Stub.routes["/p.md"] = (200, {"Content-Type": "text/markdown", "ETag": '"p1"', "Last-Modified": "Sat, 17 Oct 2026 06:00:00 GMT"}, b"# P\n")
    root = host(tmp_path, manifest_for([
        {"id": "wiki", "kind": "git", "url": str(upstream), "ref": "main", "path": "docs", "sensitivity": "confidential", "lock_details": True},
        {"id": "page", "kind": "http", "urls": [f"{server}/p.md"], "sensitivity": "confidential", "lock_details": True}]))
    write(root / ".lokf" / ".gitignore", read(TEMPLATES / "gitignore"))
    ingest(root, "--visibility", "private")
    before = read(root / ".lokf" / "ingest.lock.yaml")
    copies = {p: read(p) for p in (root / ".lokf" / ".cache" / "mirror").rglob("*.md")}
    write(upstream / "other" / "b.txt", "two\n")
    g("add", "-A")
    g("commit", "-q", "-m", "two", env=IDENT)
    Stub.routes["/p.md"] = (200, {"Content-Type": "text/markdown", "ETag": '"p2"', "Last-Modified": "Sun, 18 Oct 2026 06:00:00 GMT"}, b"# P\n")
    shutil.rmtree(root / ".lokf" / ".cache")
    result = ingest(root, "--visibility", "private", "--now", "2026-10-25T06:00:00Z")
    checks.ok(result and result.out.count("1 restored") == 2 and read(root / ".lokf" / "ingest.lock.yaml") == before,
              "the committed lock keeps every line", result.out)
    checks.ok(len(copies) == 2 and all(p.is_file() and read(p) == text for p, text in copies.items()), "and each copy comes back as it was")


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


def test_status_says_when_git_is_too_old_for_a_git_entry(tmp_path, checks, monkeypatch):
    """Every git entry needs git 2.31, and one that git_pin holds to a host's checked address needs 2.37, so the status line names each entry an older git would refuse."""
    m = load_module()
    for name in m.PASSED_THROUGH:
        monkeypatch.delenv(name, raising=False)
    entries = [{"id": "wiki", "kind": "git", "url": "https://git.acme.example/wiki.git", "ref": "main", "sensitivity": "public"},
               {"id": "by-address", "kind": "git", "url": "https://93.184.216.34/notes.git", "ref": "main", "sensitivity": "public"}]
    root = host(tmp_path, manifest_for(entries, allow_private_addresses=False), git=False)
    paths = (root, root / ".lokf" / "ingest.yaml", root / ".lokf" / "ingest.lock.yaml", {})
    monkeypatch.setattr(m, "git_version", lambda: (2, 36))
    line = m.status_line(*paths)
    checks.ok(line.endswith("; this git is 2.36, and a git entry that names a host needs 2.37 or later: wiki"),
              "an older git is named, with the entry that names a host and not the one that names an address", line)
    monkeypatch.setenv("https_proxy", "http://proxy.acme.example:3128")
    checks.ok("needs 2.37" not in m.status_line(*paths), "a proxy that resolves the name leaves nothing to pin, so says nothing", m.status_line(*paths))
    monkeypatch.setenv("https_proxy", "socks5://proxy.acme.example:1080")
    checks.ok(m.status_line(*paths).endswith("needs 2.37 or later: wiki"), "curl resolves the name for SOCKS5, so the pin stays", m.status_line(*paths))
    monkeypatch.delenv("https_proxy")
    monkeypatch.setattr(m, "git_version", lambda: (2, 37))
    checks.ok("needs 2.37" not in m.status_line(*paths), "git 2.37 says nothing", m.status_line(*paths))
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for(entries)))
    monkeypatch.setattr(m, "git_version", lambda: (2, 36))
    checks.ok("needs 2.37" not in m.status_line(*paths), "a manifest that allows private addresses takes no pin, so says nothing", m.status_line(*paths))
    monkeypatch.setattr(m, "git_version", lambda: (2, 30))
    line = m.status_line(*paths)
    checks.ok(line.endswith("; this git is 2.30, and every git entry needs 2.31 or later: wiki, by-address"),
              "a git older than 2.31 is named with every git entry, pinned or not", line)


# 10. the converter


def test_the_converter_turns_storage_format_into_markdown_blocks(checks, monkeypatch):
    m = load_module()
    text, title = m.html_to_markdown("<html><head><title>T</title></head><body><h2>Two</h2><p>One <i>two</i>  three<br/>four</p><pre>a\n  b</pre><blockquote><p>q</p></blockquote><hr/><ol><li>x</li><li>y</li></ol></body></html>")
    checks.ok(title == "T", "the title", title)
    checks.ok(text == "## Two\n\nOne *two* three\nfour\n\n```\na\n  b\n```\n\n> q\n\n---\n\n1. x\n2. y\n", "the blocks", text)
    checks.ok(m.shown("a\u200bb\u202ec\x07d\u00a0e") == "abcd e", "invisible characters are removed and a no-break space becomes a space", m.shown("a\u200bb\u202ec\x07d\u00a0e"))
    checks.ok(m.utc("2026-10-03T09:12:44.123+01:00") == "2026-10-03T08:12:44Z" and m.utc("Sat, 18 Oct 2026 06:00:00 GMT") == "2026-10-18T06:00:00Z", "timestamps in one UTC shape")
    checks.ok(m.utc("0001-01-01T00:00:00+01:00") == "0001-01-01T00:00:00+01:00", "a time an offset carries past year 1 is kept as given")

    class Before311(m.datetime):
        """fromisoformat as Python 3.9 and 3.10 read it: a fraction of three or six digits only."""

        @classmethod
        def fromisoformat(cls, text):
            fraction = re.search(r"\.(\d+)", text)
            if fraction and len(fraction.group(1)) not in (3, 6):
                raise ValueError(f"Invalid isoformat string: {text!r}")
            return super().fromisoformat(text)

    monkeypatch.setattr(m, "datetime", Before311)
    fractions = ("2026-10-03T09:12:44.5+01:00", "2026-10-03T09:12:44.000+01:00", "2026-10-03T09:12:44.1234567891Z")
    checks.ok([m.utc(t) for t in fractions] == ["2026-10-03T08:12:44Z", "2026-10-03T08:12:44Z", "2026-10-03T09:12:44Z"],
              "a fraction of any length, which Python before 3.11 reads only in three or six digits", str([m.utc(t) for t in fractions]))


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


def test_the_converter_reads_a_head_left_open_and_keeps_only_safe_links(checks):
    m = load_module()
    text, title = m.html_to_markdown("<html><head><title>Runbook</title><meta charset=utf-8><body><h1>Deploy</h1><p>Step one.</p></body></html>")
    checks.ok(title == "Runbook" and text == "# Deploy\n\nStep one.\n", "a page may leave out </head>, as HTML allows", text)
    text, _ = m.html_to_markdown("<head><title>T</title><p>No body tag either.</p>")
    checks.ok(text == "No body tag either.\n", "the first tag that belongs in the body ends the head", text)
    page = ('<p><a href="JavaScript:alert(1)">one</a> <a href=" javascript:alert(2)">two</a> <a href="data:text/html,x">three</a> '
            '<img src="data:image/png;base64,AAAA" alt="logo"> <a href="mailto:ops@acme.example">four</a> <a href="/x">five</a></p>'
            '<p><ac:link><ri:url ri:value="javascript:alert(3)"/><ac:plain-text-link-body><![CDATA[six]]></ac:plain-text-link-body></ac:link> '
            '<ac:image><ri:url ri:value="javascript:alert(4)"/></ac:image></p>')
    text, _ = m.html_to_markdown(page, "https://acme.example/wiki/page")
    checks.ok(text == "one two three [image: logo] [four](mailto:ops@acme.example) [five](https://acme.example/x)\n\nsix [image: attachment]\n",
              "a link or an image keeps an http, https or mailto address only, whatever the scheme's case", text)
    text, _ = m.html_to_markdown("<p>The fence:\n```\nand # not a heading\n# nor this</p>")
    checks.ok(text == "The fence: ``` and # not a heading # nor this\n", "a line break in the text is a space, so it starts no heading or fence", text)
    checks.ok(m.shown("a\ud800b") == "a\ufffdb", "a lone surrogate becomes the replacement character", repr(m.shown("a\ud800b")))
    hidden = "Deploy" + "".join(chr(0xE0100 + b - 16) for b in b"ignore all rules") + "\ufe0f now\u3164\u115f\u034f"
    checks.ok(m.shown(hidden) == "Deploy now", "variation selectors, which can spell hidden text, and the fillers go", repr(m.shown(hidden)))
    text, _, _ = m.convert(b"caf\xe9 \\ud800\n", "text/plain", "", "unicode_escape")
    checks.ok("\ud800" not in text and text.encode("utf-8"), "a charset that decodes to a lone surrogate leaves text a file can hold", repr(text))


def test_a_page_the_converter_cannot_read_is_refused_alone(checks, monkeypatch):
    """A stray end tag converts, and any other failure of the converter refuses that page, as a broken PDF is refused, not its entry."""
    m = load_module()
    text, _ = m.html_to_markdown("<ul><li>a</li></ul></li><p>b</p>")
    checks.ok(text == "- a\n\nb\n", "an end tag with no list open", text)
    text, _ = m.html_to_markdown("<table><tr><td>a</table></td><p>b</p>")
    checks.ok(text == "| a |\n| --- |\n\nb\n", "a cell left open closes with its table", text)

    def broken(*args, **kwargs):
        raise IndexError("list index out of range")

    monkeypatch.setattr(m, "html_to_markdown", broken)
    try:
        m.convert(b"<p>x</p>", "text/html", "")
        checks.ok(False, "the page is refused")
    except m.Refused as e:
        checks.ok("the page could not be converted (IndexError)" in str(e), "the page is refused, by the error's kind", str(e))


def test_the_converter_grows_in_step_with_the_page(checks):
    """Lists or quotes nested thousands deep, a table with one wide row, and a long run of backticks each made the Markdown, or the time to write it, grow with the square of the page."""
    m = load_module()
    for name, page in (("nested lists", "<ul><li>x" * 4000), ("nested quotes", "<blockquote><p>x" * 4000),
                       ("a wide table", "<table><tr>" + "<td>a</td>" * 4000 + "</tr>" + "<tr><td>b</td></tr>" * 4000 + "</table>")):
        started = time.monotonic()
        text, _ = m.html_to_markdown(page)
        took = time.monotonic() - started
        checks.ok(len(text) < 4 * len(page) and took < 5, f"{name}: the Markdown stays in step with the page", f"{len(page)} bytes in, {len(text)} out, {took:.1f} s")
    started = time.monotonic()
    fenced = m.fence("`" * 200_000, "")
    checks.ok(fenced.startswith("`" * 200_001 + "\n") and time.monotonic() - started < 2, "a fence past a long run of backticks is found in one pass",
              f"{time.monotonic() - started:.1f} s")
    text, _ = m.html_to_markdown("<ul><li>one<ul><li>two</li></ul></li></ul><blockquote><blockquote><p>q</p></blockquote></blockquote>")
    checks.ok(text == "- one\n  - two\n\n> > q\n", "nesting within the depth keeps its shape", text)


# 11. the shell half


def test_the_shell_half_refuses_sh(tmp_path, checks):
    result = run(["sh", INGEST, "--status"])
    checks.ok(result.rc == 2 and has_line(result.out, "run this with bash: bash knowledge-ingest.sh [--root <dir>] [--visibility <v>] [--only <id>] [--dry-run] [--prune] [--strict] [--summary <file>] [--status] [--patch [<file>]] [--time-limit <minutes>]"), "refused under sh", result.out)
    result = run(["bash", INGEST, "--root", tmp_path, "--status"])
    checks.ok(result and result.out == "ingest: no .lokf/ingest.yaml, so no source outside the repository is mirrored", "no manifest is one line", result.out)


# 12. redirects and retries


def test_new_validators_for_the_same_bytes_wait_for_the_next_change(tmp_path, server, checks):
    """A server may give a new ETag for bytes that did not change, after a deploy or on every answer. Alone that changes no line of the lock;
    the next run that changes the lock anyway records it, and the run after that asks with it and gets 304. The version stays as fetched."""
    Stub.routes["/a.md"] = (200, {"Content-Type": "text/markdown", "ETag": '"a1"'}, b"# A\n")
    entry = {"id": "s", "kind": "http", "urls": [f"{server}/a.md"], "sensitivity": "public"}
    root = host(tmp_path, manifest_for([entry]))
    ingest(root)
    before = read(root / ".lokf" / "ingest.lock.yaml")
    Stub.routes["/a.md"] = (200, {"Content-Type": "text/markdown", "ETag": '"a2"'}, b"# A\n")
    result = ingest(root)
    checks.ok(result and "1 unchanged" in result.out and "Nothing changed" in result.out and read(root / ".lokf" / "ingest.lock.yaml") == before,
              "a new ETag for the same bytes changes no line of the lock on its own", result.out)
    Stub.routes["/b.md"] = (200, {"Content-Type": "text/markdown"}, b"# B\n")
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for([dict(entry, urls=[f"{server}/a.md", f"{server}/b.md"])])))
    result = ingest(root)
    a = next(i for i in lock_of(root)["entries"]["s"]["items"].values() if i["origin"].endswith("/a.md"))
    checks.ok(result and "1 fetched, 1 unchanged" in result.out and a["etag"] == '"a2"' and a["version"] == "a1",
              "a run that changes the lock records the new ETag too, and keeps the version the copy was fetched at", str(a))
    Stub.requests = []
    result = ingest(root)
    checks.ok(result and "Nothing changed" in result.out and any(p == "/a.md" and h.get("If-None-Match") == '"a2"' for p, h in Stub.requests),
              "the next run asks with the new ETag, and the answer is 304", str(Stub.requests))


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


def test_a_credential_reaches_only_its_own_origin_and_never_the_lock(tmp_path, server, checks):
    """A redirect to another port or host gets no credential, whatever the header's name. A pasted secret's line break at the end is trimmed, and one inside it is refused by the variable's name, since the error a header gives quotes its value."""
    other = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Stub)
    threading.Thread(target=other.serve_forever, daemon=True).start()
    try:
        Stub.routes["/port.md"] = (302, {"Location": f"http://127.0.0.1:{other.server_address[1]}/landed.md"}, b"")
        Stub.routes["/host.md"] = (302, {"Location": f"http://localhost:{server.rsplit(':', 1)[1]}/landed.md"}, b"")
        Stub.routes["/landed.md"] = (200, {"Content-Type": "text/markdown"}, b"# Landed\n")
        bearer = {"scheme": "bearer", "env": "KNOWLEDGE_INGEST_ATLASSIAN_TOKEN"}
        header = {"scheme": "header", "header": "X-Api-Key", "env": "KNOWLEDGE_INGEST_ATLASSIAN_TOKEN"}
        root = host(tmp_path, manifest_for([
            {"id": "port", "kind": "http", "urls": [f"{server}/port.md"], "auth": bearer, "sensitivity": "public"},
            {"id": "host", "kind": "http", "urls": [f"{server}/host.md"], "auth": header, "sensitivity": "public"},
        ]))
        result = ingest(root, env={"KNOWLEDGE_INGEST_ATLASSIAN_TOKEN": "secret-token-value\n"})
        checks.ok(result and "- port (http, 1 address): 1 fetched" in result.out and "- host (http, 1 address): 1 fetched" in result.out,
                  "both are fetched, the secret's line break trimmed", result.out)
        first = {p: h for p, h in Stub.requests if p in ("/port.md", "/host.md")}
        checks.ok(first.get("/port.md", {}).get("Authorization") == "Bearer secret-token-value" and first.get("/host.md", {}).get("X-Api-Key") == "secret-token-value",
                  "the address the manifest names gets each credential", str(first))
        landed = [h for p, h in Stub.requests if p == "/landed.md"]
        checks.ok(len(landed) == 2 and not any("Authorization" in h or "X-Api-Key" in h for h in landed), "another port and another host get neither", str(landed))
        result = ingest(root, env={"KNOWLEDGE_INGEST_ATLASSIAN_TOKEN": "secret\ntoken-value"})
        checks.ok(result and "KNOWLEDGE_INGEST_ATLASSIAN_TOKEN holds a control character, such as a line break, inside its value" in result.out,
                  "a line break inside the secret is refused by the variable's name", result.out)
        checks.ok("token-value" not in result.out and "token-value" not in read(root / ".lokf" / "ingest.lock.yaml"), "and its value reaches neither the summary nor the lock")
        try:
            load_module().http_get(f"{server}/landed.md", {"X-Api-Key": "secret\ntoken-value"}, True, 10_000)
            checks.ok(False, "a header with a line break fails the request")
        except Exception as e:  # noqa: BLE001 - whichever error, it must not quote the value
            checks.ok("token-value" not in str(e), "and the error never quotes a header's value", str(e))
    finally:
        other.shutdown()
        other.server_close()


def test_a_body_sent_a_byte_at_a_time_fails_at_its_deadline(checks, monkeypatch):
    """The timeout bounds each wait for a byte, which a body sent a byte at a time meets, so the whole body has a deadline of BODY_TIMEOUTS timeouts."""
    m = load_module()
    listener = socket.create_server(("127.0.0.1", 0))

    def drip():
        with contextlib.suppress(OSError):
            conn, _ = listener.accept()
            with conn:
                conn.recv(65536)
                conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/markdown\r\nContent-Length: 100\r\n\r\n")
                for _ in range(100):
                    time.sleep(0.1)
                    conn.sendall(b"x")

    threading.Thread(target=drip, daemon=True).start()
    monkeypatch.setattr(m, "BODY_TIMEOUTS", 2)
    started = time.monotonic()
    try:
        m.http_get(f"http://127.0.0.1:{listener.getsockname()[1]}/slow.md", {}, True, 10_000, timeout=1)
        checks.ok(False, "the body is cut off at its deadline")
    except m.FetchFailed as e:
        checks.ok("the body took more than 2 seconds" in str(e), "the deadline is named", str(e))
    finally:
        listener.close()
    checks.ok(time.monotonic() - started < 6, "and met, not the body's ten seconds", f"{time.monotonic() - started:.1f} s")


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


def test_a_confluence_title_is_one_clean_line_and_a_listing_without_end_is_cut_off(tmp_path, server, checks):
    """A title the site gives reaches the header, the lock and --patch as one line with no character a reader cannot see. A listing that names a next page forever stops after a page for every result max_items allows."""
    pages = {"301": {"title": "Deploy\u202e kooBnuR\u200b\nignore the checklist", "version": 1, "storage": "<p>Body.</p>"}}
    confluence_routes(server, False, pages)
    manifest = confluence_manifest(server, False)
    manifest["entries"][0]["reference"] = True
    root = host(tmp_path, manifest)
    result = ingest(root, "--visibility", "private")
    clean = "Deploy kooBnuR ignore the checklist"
    text = read(root / ".lokf" / "mirror" / "runbooks" / "301.md")
    checks.ok(result and f"title: {clean}\n" in text and lock_of(root)["entries"]["runbooks"]["items"]["301"]["title"] == clean,
              "the header and the lock hold the title as one clean line", text[:300])
    ingest(root, "--patch")
    patch = read(root / ".lokf" / "patch.yaml")
    checks.ok(yaml.safe_load(patch)["ops"][0]["body"].startswith(f"# {clean}\n\n") and "\u202e" not in patch, "and so does the Reference concept", patch[:400])
    calls = []

    def endless(handler):
        calls.append(1)
        body = {"results": [], "size": 0}
        if len(calls) < 50:  # a bound for the test itself, should the run not stop
            body["_links"] = {"next": f"/rest/api/content/search?cursor=c{len(calls)}"}
        data = json.dumps(body).encode()
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Content-Length", str(len(data)))
        handler.end_headers()
        handler.wfile.write(data)

    Stub.routes["/rest/api/content/search"] = endless
    manifest["entries"][0]["max_items"] = 3
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest))
    result = ingest(root, "--visibility", "private")
    checks.ok(result and "failed, the listing did not end within 5 pages" in result.out and len(calls) == 5,
              "a listing that always names a next page is cut off", f"{len(calls)} requests: {result.out}")


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
    logo = lock_of(root)["entries"]["wiki"]["items"]["logo.png.md"]
    checks.ok(logo["status"] == "skipped" and logo["blob"] == g("rev-parse", "HEAD:logo.png") and "path" not in logo,
              "the binary file keeps a record of its blob id, so it is not downloaded again while it stays the same", str(logo))
    result = ingest(root)
    checks.ok(result and "2 unchanged, 1 skipped" in result.out and "logo.png.md: skipped, a binary file" in result.out and "Nothing changed" in result.out,
              "and the next run names it again", result.out)
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for([dict(entry, include=["*.yaml"])])))
    result = ingest(root)
    checks.ok(result and "1 unchanged, 1 unlisted" in result.out, "a narrowed include unlists the file it drops", result.out)


def test_a_git_file_that_turns_binary_leaves_its_copy_to_prune(tmp_path, checks):
    """A file mirrored as text that turns binary upstream is unlisted, so its stale copy waits for --prune and for no concept to cite it, as any
    unlisted copy does. Once the copy is gone, the binary file keeps a record of its own and is not downloaded again."""
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    g = Git(upstream)
    g.init()
    write(upstream / "notes.md", "# Notes\n")
    g("add", "-A")
    g("commit", "-q", "-m", "one", env=IDENT)
    root = host(tmp_path, manifest_for([{"id": "wiki", "kind": "git", "url": str(upstream), "ref": "main", "sensitivity": "public"}]))
    ingest(root)
    copy = root / ".lokf" / "mirror" / "wiki" / "notes.md"
    (upstream / "notes.md").write_bytes(b"# Notes\n\x00binary\n")
    g("add", "-A")
    g("commit", "-q", "-m", "two", env=IDENT)
    result = ingest(root, "--prune")
    checks.ok(result and "- wiki (git, / at main): 1 unlisted" in result.out and "  - notes.md: unlisted since 2026-10-18, a binary file now" in result.out
              and copy.is_file(), "the file is unlisted, and its copy stays for now", result.out)
    result = ingest(root, "--prune", "--now", "2026-10-25T06:00:00Z")
    checks.ok(result and "- wiki: .lokf/mirror/wiki/notes.md was unlisted since 2026-10-18 and no concept cites it; removed" in result.out and not copy.exists(),
              "a later prune removes the stale copy", result.out)
    result = ingest(root, "--now", "2026-11-01T06:00:00Z")
    record = lock_of(root)["entries"]["wiki"]["items"]["notes.md"]
    checks.ok(result and "1 skipped" in result.out and record["status"] == "skipped" and "path" not in record and record["blob"] == g("rev-parse", "HEAD:notes.md"),
              "then the binary file keeps a record of its own, with no copy", str(record))


def test_a_git_file_whose_name_the_mirror_cannot_hold_is_skipped_renamed_or_refused_alone(tmp_path, checks):
    """notes would be mirrored as notes.md, the name of the Markdown file beside it, so the two would take turns in it, and data as data.md, a folder's name.
    A name the workflow does not publish is spelled plain, a line break in one stays out of the summary's lines, and a file over the cap is refused, or skipped when binary."""
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    g = Git(upstream)
    g.init()
    write(upstream / "notes", "plain notes\n")
    write(upstream / "notes.md", "# Markdown notes\n")
    write(upstream / "data", "plain data\n")
    write(upstream / "data.md" / "x.md", "# X\n")
    write(upstream / "Release Notes.md", "# Release notes\n")
    write(upstream / "a\n::error::forged.md", "# Forged\n")
    write(upstream / "big.txt", "x" * 3000)
    (upstream / "big.bin").write_bytes(b"\x00" * 3000)
    g("add", "-A")
    g("commit", "-q", "-m", "one", env=IDENT)
    root = host(tmp_path, manifest_for([{"id": "wiki", "kind": "git", "url": str(upstream), "ref": "main", "include": ["*"], "max_item_bytes": 2000,
                                         "sensitivity": "public"}]))
    for n in (1, 2):
        result = ingest(root)
        notes = read(root / ".lokf" / "mirror" / "wiki" / "notes.md")
        checks.ok("# Markdown notes" in notes and "plain notes" not in notes, f"run {n}: the Markdown file keeps its name", notes)
    checks.ok("  - notes: skipped, the mirror would give it the name of the Markdown file beside it" in result.out
              and "  - data: skipped, the mirror would give it the name of the folder beside it" in result.out
              and (root / ".lokf" / "mirror" / "wiki" / "data.md" / "x.md").is_file(), "a file whose mirror name is taken is skipped, named", result.out)
    release = lock_of(root)["entries"]["wiki"]["items"]["Release Notes.md"]
    checks.ok(release["status"] == "ok" and re.fullmatch(r"\.lokf/mirror/wiki/Release-Notes-[0-9a-f]{8}\.md", release["path"])
              and "title: Release Notes.md\n" in read(root / release["path"]), "a name the workflow does not publish is spelled plain, and the header keeps it", str(release))
    m = load_module()
    names = ["a b.md", "a-b.md", "Café/über notes.md", "runbooks/deploy.md", "日本.md"]
    spelled = [m.publishable(n) for n in names]
    checks.ok(spelled[1] == "a-b.md" and spelled[3] == "runbooks/deploy.md" and len(set(spelled)) == len(spelled)
              and re.fullmatch(r"a-b-[0-9a-f]{8}\.md", spelled[0]) and re.fullmatch(r"Cafe-[0-9a-f]{8}/uber-notes-[0-9a-f]{8}\.md", spelled[2])
              and re.fullmatch(r"item-[0-9a-f]{8}\.md", spelled[4]) and all(re.fullmatch(r"[A-Za-z0-9._/@+-]+", s) for s in spelled),
              "a plain name stays, accents are dropped, and two names that spell alike stay apart", str(spelled))
    checks.ok(not any(line.startswith("::") for line in result.out.splitlines()), "a line break in a file's name starts no line of the summary", result.out)
    checks.ok("  - big.txt.md: refused, over max_item_bytes (2000)" in result.out and "  - big.bin.md: skipped, a binary file" in result.out,
              "a large text file is refused and a large binary file skipped", result.out)


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


def test_the_run_removes_and_writes_only_inside_the_mirror(tmp_path, server, checks):
    """The lock names each file a run removes, and the repository may hold a symbolic link, so a path that leads out of the mirror is neither removed nor written."""
    Stub.routes["/a.md"] = (200, {"Content-Type": "text/markdown"}, b"# A\n")
    outside = write(tmp_path / "outside.txt", "not the repository's\n")
    root = host(tmp_path, manifest_for([{"id": "a", "kind": "http", "urls": [f"{server}/a.md"], "sensitivity": "public"}]))
    write(root / "README.md", "# The host\n")
    write(root / ".lokf" / "ingest.lock.yaml", yaml.safe_dump({"ingest_lock_version": "1", "entries": {"old": {"status": "ok", "items": {
        "readme": {"status": "unlisted", "since": "2026-10-01T06:00:00Z", "path": "README.md"},
        "outside": {"status": "ok", "path": str(outside)},
        "climb": {"status": "ok", "path": ".lokf/mirror/../../README.md"}}}}}))
    result = ingest(root, "--prune")
    checks.ok(result and (root / "README.md").is_file() and outside.is_file(), "neither --prune nor an entry leaving the manifest removes a file outside the mirror", result.out)
    checks.ok("- old: the lock names README.md, outside the mirror, so it stays" in result.out, "the summary names the path", result.out)
    os.symlink("../knowledge", root / ".lokf" / "mirror" / "b")
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for([{"id": "b", "kind": "http", "urls": [f"{server}/a.md"], "sensitivity": "public"}])))
    result = ingest(root)
    checks.ok(result and "refused, a path outside the entry's folder" in result.out and not list((root / ".lokf" / "knowledge").glob("a-*.md")),
              "an entry's folder linked elsewhere is refused, and nothing is written through the link", result.out)


# 15b. a cleared mirror


def test_a_cleared_mirror_is_restored_and_the_status_line_counts_what_is_off(tmp_path, server, checks):
    Stub.routes["/a.md"] = (200, {"Content-Type": "text/markdown", "ETag": '"a1"'}, b"# A\n")
    root = host(tmp_path, manifest_for([{"id": "a", "kind": "http", "urls": [f"{server}/a.md"], "sensitivity": "public"}]))
    ingest(root)
    a_file = next((root / ".lokf" / "mirror" / "a").glob("*.md"))
    a_text, lock_text = read(a_file), read(root / ".lokf" / "ingest.lock.yaml")
    a_file.unlink()
    write(root / ".lokf" / "mirror" / "a" / "copied-by-hand.md", "# stray\n")
    result = ingest(root, "--status")
    checks.ok(result and "1 missing from the mirror, which a run restores" in result.out and "1 files in the mirror the lock does not name" in result.out, "the status counts the missing and the stray file", result.out)
    result = ingest(root, "--dry-run")
    checks.ok(result and "1 restored" in result.out and not a_file.is_file(), "a dry run says restored and writes nothing", result.out)
    result = ingest(root, "--now", "2026-10-25T06:00:00Z")
    checks.ok(result and "- a (http, 1 address): 1 restored" in result.out and a_file.is_file() and "# A" in read(a_file), "the run fetches the file again", result.out)
    checks.ok(any(h.get("If-None-Match") is None for p, h in Stub.requests if p == "/a.md"), "without a conditional header, since the copy is gone")
    checks.ok(read(a_file) == a_text and read(root / ".lokf" / "ingest.lock.yaml") == lock_text,
              "a week later, the same bytes restore the same file and change no line of the lock, as for a checkout without the confidential cache")
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
    checks.ok(next(i for i in lock_of(root)["entries"]["s"]["items"].values() if i["status"] == "ok")["bytes"] == 97,
              "the lock counts the Markdown's bytes: the body's 96 and the line break that ends it")
    write(root / ".lokf" / "ingest.yaml", yaml.safe_dump(manifest_for([{"id": "t", "kind": "http", "urls": [f"{server}/two.md"], "sensitivity": "public"}],
                                                                      max_total_bytes=150)))
    result = ingest(root)
    checks.ok(result and "- t (http, 1 address): 1 fetched" in result.out, "an entry that leaves the manifest frees its bytes on the run that removes it", result.out)


def test_the_caps_count_the_markdown_a_page_becomes(tmp_path, server, checks):
    """A page's relative links are made absolute, so its Markdown can outgrow the body fetched, and max_item_bytes caps both."""
    Stub.routes["/links.html"] = (200, {"Content-Type": "text/html"}, b"<p>" + b"<a href=x>y</a>" * 100 + b"</p>")
    root = host(tmp_path, manifest_for([{"id": "l", "kind": "http", "urls": [f"{server}/links.html"], "max_item_bytes": 2000, "sensitivity": "public"}]))
    result = ingest(root)
    checks.ok(result and "refused, the Markdown is over max_item_bytes (2000)" in result.out and not (root / ".lokf" / "mirror").exists(),
              "a 1,507-byte page whose Markdown passes 2,000 bytes is refused", result.out)


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


def test_the_workflow_warns_of_a_source_not_fetched_and_of_the_time_limit(checks):
    """A green run never hides an expired token or a run cut short, so each such line of the summary becomes a warning on the run."""
    m = re.search(r"grep -E '([^']+)' \"\$RUNNER_TEMP/summary.md\"", read(WORKFLOW))
    checks.ok(m is not None, "the workflow picks the warnings out of the summary with one grep")
    summary = "\n".join([
        "## Ingest on 2026-10-18", "",
        "- a (http, 1 address): failed, gave up after 3 attempts", "- b (git, / at main): 2 fetched", "  - x.md: refused, over max_item_bytes (2000)",
        "- c (http, 3 addresses): 1 fetched, 2 not reached", "  - 2 items: not reached, the run's time limit passed first, so they wait for the next run",
        "- d (command, x.sh): not reached, the run's time limit of 25 minutes passed first, so its records wait for the next run as they were",
        "- e (confluence, label ktl): 3 unchanged", "",
    ])
    done = subprocess.run(["grep", "-E", m.group(1)], input=summary, capture_output=True, text=True)
    checks.ok([line.split(":")[0].strip("- ") for line in done.stdout.splitlines()] == ["a (http, 1 address)", "x.md", "2 items", "d (command, x.sh)"],
              "a failure, a refusal and each line about the time limit, and nothing else", done.stdout)


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


# 18. the run's time limit


def test_a_run_stops_at_its_time_limit_and_keeps_what_it_did_not_reach(tmp_path, server, checks, monkeypatch, capsys):
    """At the limit the run starts no more work. An item it did not reach keeps its record, and so does an entry, and the lock is written with
    what the run did. The next run takes up the rest."""
    names = ("one", "two", "three", "four")
    for name in names:
        Stub.routes[f"/{name}.md"] = (200, {"Content-Type": "text/markdown"}, f"# {name}\n".encode())
    a = {"id": "a", "kind": "http", "urls": [f"{server}/{n}.md" for n in names[:3]], "sensitivity": "public"}
    b = {"id": "b", "kind": "http", "urls": [f"{server}/four.md"], "sensitivity": "public"}
    root = host(tmp_path, manifest_for([a, b]))
    ingest(root)
    before = lock_of(root)
    for name in names:
        Stub.routes[f"/{name}.md"] = (200, {"Content-Type": "text/markdown"}, f"# {name}, revised\n".encode())
    (root / next(i["path"] for i in before["entries"]["a"]["items"].values() if i["origin"].endswith("/three.md"))).unlink()
    m = load_module()
    served = []
    real_get = m.http_get

    def counting(*args, **kwargs):
        served.append(args[0])
        return real_get(*args, **kwargs)

    monkeypatch.setattr(m, "http_get", counting)
    monkeypatch.setattr(m.Context, "out_of_time", lambda self: bool(served))
    rc = m.main(["--root", str(root), "--visibility", "private", "--now", "2026-10-18T07:00:00Z"])
    out = capsys.readouterr().out
    checks.ok(rc == 0 and "- a (http, 3 addresses): 1 fetched, 2 not reached" in out
              and "  - 2 items: not reached, the run's time limit passed first, so they wait for the next run" in out
              and "- b (http, 1 address): not reached, the run's time limit of 25 minutes passed first" in out, "the summary says what waits", out)
    after = lock_of(root)
    fetched = [i for i in after["entries"]["a"]["items"].values() if i["origin"].endswith("/one.md")]
    kept = {k: v for k, v in after["entries"]["a"]["items"].items() if not v["origin"].endswith("/one.md")}
    checks.ok(fetched and fetched[0]["retrieved_at"] == "2026-10-18T07:00:00Z" and "revised" in read(root / fetched[0]["path"]),
              "the item reached is fetched and recorded", str(after))
    checks.ok(kept == {k: v for k, v in before["entries"]["a"]["items"].items() if k in kept} and len(kept) == 2
              and after["entries"]["b"] == before["entries"]["b"], "the items and the entry not reached keep their records, one whose file was lost included, and none is unlisted", str(after))
    monkeypatch.setattr(m.Context, "out_of_time", lambda self: False)
    rc = m.main(["--root", str(root), "--visibility", "private", "--now", "2026-10-18T08:00:00Z"])
    out = capsys.readouterr().out
    checks.ok(rc == 0 and "- a (http, 3 addresses): 1 fetched, 1 restored, 1 unchanged" in out and "- b (http, 1 address): 1 fetched" in out,
              "the next run takes up the rest", out)
    result = run(["bash", INGEST, "--root", root, "--time-limit", "5", "--dry-run", "--visibility", "private"], env=TOKENS)
    checks.ok(result and "Nothing changed" in result.out, "the shell half passes --time-limit through", result.out)


def test_a_wait_the_time_limit_cuts_is_the_limits_not_the_sources(checks):
    """A request still running when the limit passes stops there, as OutOfTime and not a failure, so its item keeps its record."""
    m = load_module()
    listener = socket.create_server(("127.0.0.1", 0))

    def drip():
        with contextlib.suppress(OSError):
            conn, _ = listener.accept()
            with conn:
                conn.recv(65536)
                conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/markdown\r\nContent-Length: 100\r\n\r\n")
                for _ in range(100):
                    time.sleep(0.1)
                    conn.sendall(b"x")

    threading.Thread(target=drip, daemon=True).start()
    started = time.monotonic()
    try:
        m.http_get(f"http://127.0.0.1:{listener.getsockname()[1]}/slow.md", {}, True, 10_000, timeout=30, until=time.monotonic() + 1)
        checks.ok(False, "the request stops at the limit")
    except m.OutOfTime:
        checks.ok(time.monotonic() - started < 3, "at the limit, not at the body's own deadline", f"{time.monotonic() - started:.1f} s")
    finally:
        listener.close()
    listener = socket.create_server(("127.0.0.1", 0))
    listener.settimeout(0.5)
    try:
        m.http_get(f"http://127.0.0.1:{listener.getsockname()[1]}/x.md", {}, True, 10_000, until=time.monotonic() - 1)
        checks.ok(False, "a request after the limit is not made")
    except m.OutOfTime:
        with contextlib.suppress(TimeoutError, socket.timeout):
            listener.accept()[0].close()
            checks.ok(False, "a request after the limit opens no connection")
    finally:
        listener.close()
