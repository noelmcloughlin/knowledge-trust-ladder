#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml==6.0.3", "pypdf==6.1.1"]
# [tool.uv]
# exclude-newer = "2025-10-01T00:00:00Z"
# ///
# The ingest: knowledge outside the repository, mirrored into it.
#
# Reads .lokf/ingest.yaml, fetches each source it names, converts it to
# Markdown and writes it under .lokf/mirror/<entry id>/, one file per page
# or document, with a header: origin, title, version, digest, retrieval
# time, converter. .lokf/ingest.lock.yaml records the same per item and a
# status: ok, gone, unlisted, failed or refused. A mirror file is repository
# content the librarian reads as any tracked file. It is not knowledge yet.
#
# Kinds: confluence (a label, space, page, tree or CQL selection; v1 search
# everywhere, v2 body on Cloud and v1 on Data Center; the version number is
# the change signal), http (addresses serving HTML, Markdown, text or PDF;
# ETag and Last-Modified when the server gives them, else the digest), git
# (a path at a ref, over https, or http and a local path where the manifest
# allows private addresses; the commit is the version and the blob id the
# change signal; a file that is not Markdown is fenced), command (a tracked
# command's output; the command's own digest is recorded too). Listing comes
# before fetching, so an unchanged source costs a listing and no body. The
# mirror and the lock change only when content changes. An entry that leaves
# the manifest takes its folder with it. A file the lock names and the disk
# has lost is fetched again and reported as restored.
#
# Refused and recorded: a token in the manifest (auth names environment
# variables starting KNOWLEDGE_INGEST_); an entry the repository's
# visibility does not allow (internal: a private repository only;
# confidential: never committed, kept under .lokf/.cache/mirror/, and refused
# where git does not ignore that folder or tracks a file in it); more
# than max_items; a body over max_item_bytes or a mirror over
# max_total_bytes; a private address unless the manifest allows it; a path
# outside the mirror root; an unexpected content type; a PDF with no text
# layer. Characters no reader sees are removed, apart from the two joiners
# some scripts spell with. One entry's failure, expected or not, never stops
# the others.
#
# Usage, through knowledge-ingest.sh beside it:
#   knowledge-ingest.py [--root DIR] [--visibility public|private|internal|unknown]
#                       [--only ID]... [--dry-run] [--prune] [--strict]
#                       [--summary FILE] [--status] [--patch [FILE]]
#   --dry-run   compare and fetch, write nothing
#   --only      one entry; the others keep their lock state
#   --prune     delete a gone or unlisted file no concept cites, once an
#               earlier run recorded it so; the lock's `since` says when
#   --strict    exit 1 when any entry failed or was refused
#   --summary   the run's summary, in Markdown, to FILE
#   --status    one line for the preflight
#   --patch     Reference concepts for entries with `reference: true`, as
#               operations for knowledge-apply.sh, to .lokf/patch.yaml or FILE
# Exit 0 completed (the lock says how each entry fared); 1 stopped by the
# manifest or an argument before any write; 2 a tool is missing.
"""The ingest: knowledge outside the repository, mirrored into it."""

from __future__ import annotations

import argparse
import base64
import codecs
import fnmatch
import hashlib
import html
import http.client
import io
import ipaddress
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath

try:
    import yaml
except ImportError:  # pragma: no cover - the shell half checks first
    print("knowledge-ingest: needs pyyaml; run through uv, or install it for python3", file=sys.stderr)
    sys.exit(2)

USER_AGENT = "knowledge-ingest/1 (+https://w3id.org/ktl/docs/ingest/)"
MANIFEST_VERSION = "1"
LOCK_VERSION = "1"
KINDS = ("confluence", "http", "git", "command")
ENV_NAME = re.compile(r"^KNOWLEDGE_INGEST_[A-Z0-9_]+$")
ENTRY_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SENSITIVITIES = ("public", "internal", "confidential")
MIRROR = ".lokf/mirror"
TOP_KEYS = {"ingest_version", "max_total_bytes", "allow_private_addresses", "services", "defaults", "entries"}
SERVICE_KEYS = {"kind", "site", "api", "auth"}
AUTH_KEYS = {"scheme", "env", "user_env", "header"}
DEFAULT_KEYS = {"sensitivity", "max_items", "max_item_bytes", "authors"}
ENTRY_KEYS = {
    "id", "kind", "service", "site", "api", "auth", "select", "urls", "url", "ref", "path", "include", "exclude",
    "command", "args", "timeout", "convert", "owner", "why", "license", "sensitivity", "max_items",
    "max_item_bytes", "authors", "disabled", "reference",
}
SELECT_KEYS = {"label", "space", "page", "tree", "cql"}
CONVERTS = ("html-markdown", "pdf-text", "text")
DEFAULTS = {"sensitivity": "internal", "max_items": 200, "max_item_bytes": 1_000_000, "authors": True}
DEFAULT_TOTAL_BYTES = 50_000_000
TIMEOUT = 30
ATTEMPTS = 3
TEXT_TYPES = {"text/markdown": "text", "text/x-markdown": "text", "text/plain": "text", "text/html": "html-markdown",
              "application/xhtml+xml": "html-markdown", "application/pdf": "pdf-text"}
KEPT = "\u200c\u200d"  # the zero-width non-joiner and joiner, which Persian, Arabic and Indic scripts and emoji sequences spell with
PASSED_THROUGH = ("http_proxy", "https_proxy", "no_proxy", "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "SSL_CERT_FILE", "SSL_CERT_DIR",
                  "GIT_SSL_CAINFO", "GIT_SSL_CAPATH", "CURL_CA_BUNDLE")  # a proxy and a company's certificate reach git and a command


class Stop(Exception):
    """The manifest or an argument stopped the run before any write."""


class Refused(Exception):
    """One item or entry is refused, with the reason the lock records."""


class FetchFailed(Exception):
    """A request did not complete, with the reason the lock records."""


class Gone(Exception):
    """The source answered 404 or 410."""


def say(msg: str) -> None:
    print(msg, flush=True)


def now_utc(given: str | None) -> str:
    if given:
        return given
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc(text: str) -> str:
    """A timestamp in the one UTC shape the sidecar's scripts compare, or the text as given when it is not one."""
    if not text:
        return ""
    t = text.strip()
    if t.endswith("Z"):
        t = t[:-1] + "+00:00"
    t = re.sub(r"(\.\d{1,6})\d+", r"\1", t)
    try:
        d = datetime.fromisoformat(t)
    except ValueError:
        try:
            from email.utils import parsedate_to_datetime

            d = parsedate_to_datetime(text)
        except (TypeError, ValueError):
            return text.strip()
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def shown(text: str) -> str:
    """The text without the characters no reader sees, line breaks, tabs and the two joiners kept."""
    out = []
    for ch in text:
        if ch in "\n\t" or ch in KEPT:
            out.append(ch)
        elif ch == "\r":
            continue
        elif unicodedata.category(ch) in ("Cc", "Cf"):
            continue
        elif ch in "\u2028\u2029":
            out.append("\n")
        elif ch == "\xa0":
            out.append(" ")
        else:
            out.append(ch)
    return "".join(out)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:60] or "item"


# ---- the manifest -----------------------------------------------------------


@dataclass
class Auth:
    scheme: str = ""
    env: str = ""
    user_env: str = ""
    header: str = ""

    def names(self) -> list[str]:
        return [n for n in (self.env, self.user_env) if n]

    def value(self, environ: dict) -> tuple[str, str]:
        """The header name and value, from the environment, or a FetchFailed naming the variable."""
        if not self.scheme:
            return "", ""
        token = environ.get(self.env, "")
        if not token:
            raise FetchFailed(f"no credential in {self.env}")
        if self.scheme == "basic":
            user = environ.get(self.user_env, "") if self.user_env else "x-access-token"
            if self.user_env and not user:
                raise FetchFailed(f"no user in {self.user_env}")
            return "Authorization", "Basic " + base64.b64encode(f"{user}:{token}".encode()).decode()
        if self.scheme == "bearer":
            return "Authorization", "Bearer " + token
        return self.header, token


@dataclass
class Entry:
    id: str
    kind: str
    site: str = ""
    api: str = ""
    auth: Auth = field(default_factory=Auth)
    select: dict = field(default_factory=dict)
    urls: list = field(default_factory=list)
    url: str = ""
    ref: str = ""
    path: str = ""
    include: list = field(default_factory=list)
    exclude: list = field(default_factory=list)
    command: str = ""
    args: list = field(default_factory=list)
    timeout: int = 120
    convert: str = ""
    owner: str = ""
    why: str = ""
    license: str = ""
    sensitivity: str = "internal"
    max_items: int = 200
    max_item_bytes: int = 1_000_000
    authors: bool = True
    disabled: bool = False
    reference: bool = False

    def describe(self) -> str:
        if self.kind == "confluence":
            k, v = next(iter(self.select.items()))
            return f"confluence, {k} {v}"
        if self.kind == "http":
            return f"http, {len(self.urls)} address{'es' if len(self.urls) != 1 else ''}"
        if self.kind == "git":
            return f"git, {self.path or '/'} at {self.ref}"
        return f"command, {self.command}"


@dataclass
class Manifest:
    mirror: str
    max_total_bytes: int
    allow_private: bool
    entries: list


def only_keys(mapping, allowed: set, where: str) -> None:
    if not isinstance(mapping, dict):
        raise Stop(f"{where} is not a mapping")
    extra = sorted(k for k in mapping if k not in allowed)
    if extra:
        raise Stop(f"{where} has a key this script does not know: {', '.join(str(k) for k in extra)}")


def read_auth(raw, where: str) -> Auth:
    if raw is None:
        return Auth()
    only_keys(raw, AUTH_KEYS, where)
    scheme = str(raw.get("scheme", ""))
    if scheme not in ("basic", "bearer", "header"):
        raise Stop(f"{where}: scheme is basic, bearer or header")
    env = str(raw.get("env", ""))
    user_env = str(raw.get("user_env", ""))
    header = str(raw.get("header", ""))
    for name in (env, user_env):
        if name and not ENV_NAME.match(name):
            raise Stop(f"{where}: {name} is not an environment variable name starting KNOWLEDGE_INGEST_")
    if not env:
        raise Stop(f"{where}: env names the variable that holds the token")
    if scheme == "header" and not re.match(r"^[A-Za-z][A-Za-z0-9-]*$", header):
        raise Stop(f"{where}: a header scheme names the header")
    if scheme != "header" and header:
        raise Stop(f"{where}: header goes with the header scheme only")
    for key in ("env", "user_env"):
        value = str(raw.get(key, ""))
        if value and (" " in value or ":" in value or len(value) > 64):
            raise Stop(f"{where}: {key} is a variable name, never a value")
    return Auth(scheme, env, user_env, header)


def positive_int(value, where: str, default: int) -> int:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise Stop(f"{where} is a whole number above zero")
    return value


def read_manifest(path: Path) -> Manifest:
    if not path.is_file():
        raise Stop(f"no manifest at {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as e:
        raise Stop(f"{path} is not YAML: {e}") from e
    only_keys(raw, TOP_KEYS, path.name)
    if str(raw.get("ingest_version", "")) != MANIFEST_VERSION:
        raise Stop(f"{path.name}: ingest_version is \"{MANIFEST_VERSION}\" for this script")
    total = positive_int(raw.get("max_total_bytes"), "max_total_bytes", DEFAULT_TOTAL_BYTES)
    allow_private = bool(raw.get("allow_private_addresses", False))
    services = raw.get("services") or {}
    if not isinstance(services, dict):
        raise Stop(f"{path.name}: services is a mapping of names to services")
    parsed_services = {}
    for name, svc in services.items():
        where = f"services.{name}"
        only_keys(svc, SERVICE_KEYS, where)
        kind = str(svc.get("kind", ""))
        if kind not in KINDS:
            raise Stop(f"{where}: kind is one of {', '.join(KINDS)}")
        parsed_services[str(name)] = {
            "kind": kind, "site": str(svc.get("site", "")), "api": str(svc.get("api", "")),
            "auth": read_auth(svc.get("auth"), f"{where}.auth"),
        }
    defaults = dict(DEFAULTS)
    raw_defaults = raw.get("defaults") or {}
    only_keys(raw_defaults, DEFAULT_KEYS, "defaults")
    defaults.update(raw_defaults)
    entries_raw = raw.get("entries")
    if not isinstance(entries_raw, list) or not entries_raw:
        raise Stop(f"{path.name}: entries is a list with at least one entry")
    entries, seen = [], set()
    for i, e in enumerate(entries_raw):
        where = f"entries[{i}]"
        only_keys(e, ENTRY_KEYS, where)
        eid = str(e.get("id", ""))
        if not ENTRY_ID.match(eid):
            raise Stop(f"{where}: id is lowercase a-z, 0-9 and hyphens, since it names a folder: {eid or 'missing'}")
        if eid in seen:
            raise Stop(f"{where}: id {eid} is used twice")
        seen.add(eid)
        where = f"entries.{eid}"
        svc = parsed_services.get(str(e["service"])) if e.get("service") else None
        if e.get("service") and svc is None:
            raise Stop(f"{where}: service {e['service']} is not under services")
        kind = str(e.get("kind") or (svc["kind"] if svc else ""))
        if kind not in KINDS:
            raise Stop(f"{where}: kind is one of {', '.join(KINDS)}, on the entry or its service")
        if svc and e.get("kind") and e["kind"] != svc["kind"]:
            raise Stop(f"{where}: kind {e['kind']} differs from its service's {svc['kind']}")
        auth = read_auth(e.get("auth"), f"{where}.auth") if e.get("auth") else (svc["auth"] if svc else Auth())
        site = str(e.get("site") or (svc["site"] if svc else ""))
        api = str(e.get("api") or (svc["api"] if svc else ""))
        sens = str(e.get("sensitivity", defaults["sensitivity"]))
        if sens not in SENSITIVITIES:
            raise Stop(f"{where}: sensitivity is public, internal or confidential")
        convert = str(e.get("convert", ""))
        if convert and convert not in CONVERTS:
            raise Stop(f"{where}: convert is one of {', '.join(CONVERTS)}")
        owner = str(e.get("owner", ""))
        if owner and not re.match(r"^[^\s:/]+:\S+$|^[^\s/]+/[^\s/]+$", owner):
            raise Stop(f"{where}: owner is an actor string such as team:platform or vendor/v3")
        entry = Entry(
            id=eid, kind=kind, site=site, api=api, auth=auth,
            select=dict(e.get("select") or {}), urls=[str(u) for u in (e.get("urls") or [])],
            url=str(e.get("url", "")), ref=str(e.get("ref", "")), path=str(e.get("path", "")).strip("/"),
            include=[str(g) for g in (e.get("include") or [])], exclude=[str(g) for g in (e.get("exclude") or [])],
            command=str(e.get("command", "")), args=[str(a) for a in (e.get("args") or [])],
            timeout=positive_int(e.get("timeout"), f"{where}.timeout", 120), convert=convert,
            owner=owner, why=str(e.get("why", "")),
            license=str(e.get("license", "")), sensitivity=sens,
            max_items=positive_int(e.get("max_items", defaults["max_items"]), f"{where}.max_items", 200),
            max_item_bytes=positive_int(e.get("max_item_bytes", defaults["max_item_bytes"]), f"{where}.max_item_bytes", 1_000_000),
            authors=bool(e.get("authors", defaults["authors"])), disabled=bool(e.get("disabled", False)),
            reference=bool(e.get("reference", False)),
        )
        check_entry(entry, where)
        if entry.kind == "confluence" and entry.site.startswith("http://") and not allow_private:
            raise Stop(f"{where}: {entry.site} is over http; use https, or allow_private_addresses: true for an intranet site")
        if entry.kind == "git":
            how = git_url_kind(entry.url)
            if how == "other":
                raise Stop(f"{where}: url is an https address, or http:// or a local path with allow_private_addresses: true; "
                           "ssh and git protocols are not fetched, since the credential is a token")
            if how != "https" and not allow_private:
                raise Stop(f"{where}: {entry.url} is not https; allow_private_addresses: true permits http and local paths")
        entries.append(entry)
    return Manifest(MIRROR, total, allow_private, entries)


def check_entry(entry: Entry, where: str) -> None:
    if entry.kind == "confluence":
        if not entry.site.startswith(("https://", "http://")):
            raise Stop(f"{where}: a confluence entry or its service names the site, as https://...")
        only_keys(entry.select, SELECT_KEYS, f"{where}.select")
        if len(entry.select) == 0:
            raise Stop(f"{where}: select names a label, a space, a page, a tree or a cql")
        if "label" in entry.select and not re.match(r"^[A-Za-z0-9._-]+$", str(entry.select["label"])):
            raise Stop(f"{where}: select.label is a label name")
        if "space" in entry.select and not re.match(r"^[A-Za-z0-9~_-]+$", str(entry.select["space"])):
            raise Stop(f"{where}: select.space is a space key")
        for key in ("page", "tree"):
            if key in entry.select and not re.match(r"^[0-9]+$", str(entry.select[key])):
                raise Stop(f"{where}: select.{key} is a page id")
        if entry.api and entry.api not in ("cloud", "datacenter"):
            raise Stop(f"{where}: api is cloud or datacenter")
    elif entry.kind == "http":
        if not entry.urls:
            raise Stop(f"{where}: urls lists at least one address")
        for u in entry.urls:
            p = urllib.parse.urlsplit(u)
            if p.scheme not in ("http", "https") or not p.netloc or "@" in p.netloc:
                raise Stop(f"{where}: {u} is not a plain http(s) address")
    elif entry.kind == "git":
        if not entry.url or not entry.ref:
            raise Stop(f"{where}: a git entry names url and ref")
        if "@" in urllib.parse.urlsplit(entry.url).netloc:
            raise Stop(f"{where}: no credential in url; the auth block names it")
        if not re.match(r"^[A-Za-z0-9._/-]+$", entry.ref) or entry.ref.startswith("-"):
            raise Stop(f"{where}: ref is a branch, a tag or a commit")
        if ".." in PurePosixPath(entry.path).parts:
            raise Stop(f"{where}: path stays inside the repository")
    elif entry.kind == "command":
        if not entry.command or entry.command.startswith("/") or ".." in PurePosixPath(entry.command).parts:
            raise Stop(f"{where}: command is a tracked path under the repository root")
        for a in entry.args:
            if "\n" in a:
                raise Stop(f"{where}: an argument is one line")


# ---- the lock ----------------------------------------------------------------


def read_lock(path: Path) -> dict:
    if not path.is_file():
        return {"ingest_lock_version": LOCK_VERSION, "entries": {}}
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (yaml.YAMLError, UnicodeDecodeError) as e:
        raise Stop(f"{path} is not YAML: {e}") from e
    if str(raw.get("ingest_lock_version", "")) != LOCK_VERSION:
        raise Stop(f"{path.name}: ingest_lock_version is \"{LOCK_VERSION}\" for this script")
    raw.setdefault("entries", {})
    return raw


class Dumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def str_presenter(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


Dumper.add_representer(str, str_presenter)


def to_yaml(data) -> str:
    return yaml.dump(data, Dumper=Dumper, sort_keys=True, allow_unicode=True, default_flow_style=False, width=10_000)


# ---- http ---------------------------------------------------------------------


def address_is_private(host: str) -> bool:
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as e:
        raise FetchFailed(f"{host} does not resolve ({e})") from e
    for info in infos:
        addr = ipaddress.ip_address(info[4][0])
        if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved or addr.is_multicast or addr.is_unspecified:
            return True
    return False


class Redirects(urllib.request.HTTPRedirectHandler):
    """Follows at most five redirects, checks each target as the first address was checked, and drops the credential on a change of host."""

    def __init__(self, allow_private: bool):
        self.allow_private = allow_private
        self.hops = 0

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.hops += 1
        if self.hops > 5:
            raise FetchFailed("more than five redirects")
        new = urllib.parse.urlsplit(newurl)
        if new.scheme not in ("http", "https") or "@" in new.netloc:
            raise FetchFailed(f"redirected to an address this script does not fetch: {new.scheme}://{new.netloc}")
        if not self.allow_private and address_is_private(new.hostname or ""):
            raise FetchFailed(f"redirected to a private address: {new.hostname}")
        nxt = super().redirect_request(req, fp, code, msg, headers, newurl)
        if nxt is not None and new.hostname != urllib.parse.urlsplit(req.full_url).hostname:
            nxt.remove_header("Authorization")
            for name in list(nxt.headers):
                if name.lower() == "authorization":
                    del nxt.headers[name]
        return nxt


@dataclass
class Response:
    status: int
    headers: dict
    data: bytes


def http_get(url: str, headers: dict, allow_private: bool, max_bytes: int, timeout: int = TIMEOUT, accept_304: bool = False) -> Response:
    """GET with retries on 429, 5xx and a broken connection, a size cap read as it streams, and the address checks. 404 and 410 raise Gone."""
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.netloc or "@" in parts.netloc:
        raise Refused(f"{url} is not a plain http(s) address")
    if not allow_private and address_is_private(parts.hostname or ""):
        raise Refused(f"{parts.hostname} is a private or link-local address; allow_private_addresses: true permits them")
    redirects = Redirects(allow_private)
    opener = urllib.request.build_opener(redirects)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **headers})
    last = ""
    for attempt in range(ATTEMPTS):
        redirects.hops = 0
        delay = 2 ** attempt
        try:
            with opener.open(req, timeout=timeout) as resp:  # noqa: S310 - an address the manifest names
                data = resp.read(max_bytes + 1)
                if len(data) > max_bytes:
                    raise Refused(f"over max_item_bytes ({max_bytes})")
                return Response(resp.status, {k.lower(): v for k, v in resp.headers.items()}, data)
        except urllib.error.HTTPError as e:
            if e.code == 304 and accept_304:
                return Response(304, {k.lower(): v for k, v in e.headers.items()}, b"")
            if e.code in (404, 410):
                raise Gone(f"{e.code}") from e
            if e.code in (401, 403):
                raise FetchFailed(f"{e.code} from {parts.netloc}: the credential was refused or lacks a scope") from e
            if e.code != 429 and e.code < 500:
                raise FetchFailed(f"{e.code} from {parts.netloc}") from e
            last = f"{e.code} from {parts.netloc}"
            wait = e.headers.get("Retry-After", "")
            if wait.isdigit():
                delay = min(int(wait), 60)
        except ValueError as e:  # http.client.InvalidURL and its kin
            raise FetchFailed(f"{url} is not an address this script can fetch ({e})") from e
        except (OSError, http.client.HTTPException) as e:  # a timeout, TLS, a reset, a broken or truncated response
            last = f"{parts.netloc}: {getattr(e, 'reason', e)}"
        if attempt < ATTEMPTS - 1:
            time.sleep(delay)
    raise FetchFailed(f"gave up after {ATTEMPTS} attempts: {last}")


def content_type_of(headers: dict) -> str:
    return (headers.get("content-type", "") or "").split(";")[0].strip().lower()


def charset_of(headers: dict) -> str:
    m = re.search(r"charset\s*=\s*\"?([A-Za-z0-9._:-]+)", headers.get("content-type", "") or "", re.I)
    return m.group(1) if m else ""


# ---- converters --------------------------------------------------------------

HEADINGS = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}
PARAGRAPHS = {"p", "div", "section", "article", "header", "footer", "main", "aside", "nav", "figure", "figcaption",
              "details", "summary", "center", "address", "dl", "dt", "dd", "ac:layout", "ac:layout-section",
              "ac:layout-cell", "ac:adf-content", "ac:adf-extension", "ac:adf-node", "ac:adf-node-group", "body", "html"}
SKIPPED = {"script", "style", "head", "ac:parameter", "ac:emoticon", "ac:placeholder", "template", "noscript", "ac:adf-attribute"}
INLINE = {"strong": "**", "b": "**", "em": "*", "i": "*", "s": "~~", "del": "~~", "strike": "~~", "code": "`", "kbd": "`"}
PANELS = {"info": "Info", "note": "Note", "warning": "Warning", "tip": "Tip", "panel": "Panel", "expand": "Expand", "excerpt": "Excerpt"}
CDATA = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.S)


class Markdowner(HTMLParser):
    """HTML, XHTML and Confluence storage format to Markdown, as blocks. Links are resolved against the page's address; a Confluence page link becomes the site's display address."""

    def __init__(self, base: str = ""):
        super().__init__(convert_charrefs=True)
        self.base = base
        m = re.match(r"^(.*?)/(?:spaces|display)/([^/?#]+)/", base)
        self.site, self.space = (m.group(1), m.group(2)) if m else ("", "")
        self.blocks: list[str] = []
        self.buf: list[str] = []
        self.inline: list[tuple[str, int]] = []
        self.links: list[tuple[str, int]] = []
        self.lists: list[list] = []
        self.heading = 0
        self.pre = 0
        self.pre_buf: list[str] = []
        self.skip = 0
        self.quote = 0
        self.table = None
        self.cell = None
        self.title_buf = None
        self.title = ""
        self.macros: list[dict] = []
        self.link = None
        self.image = None
        self.task = None
        self.plain_target = None

    # -- blocks
    def prefix(self) -> str:
        return "> " * self.quote

    def text(self) -> str:
        raw = "".join(self.buf)
        self.buf = []
        lines = [" ".join(line.split()) for line in raw.split("\n")]
        return "\n".join(line for line in lines if line)

    def emit(self, block: str) -> None:
        if not block:
            return
        if self.lists and self.lists[-1][2] is not None:
            self.lists[-1][2].append(block)
            return
        self.blocks.append("\n".join(self.prefix() + line for line in block.split("\n")))

    def flush(self) -> None:
        if self.cell is not None:
            self.cell.append(self.text())
            return
        if self.title_buf is not None:
            return
        t = self.text()
        if not t:
            return
        if self.heading:
            self.emit("#" * self.heading + " " + " ".join(t.split()))
        else:
            self.emit(t)

    def href(self, url: str) -> str:
        if not url or not self.base or url.startswith(("javascript:", "data:", "#")):
            return url
        return urllib.parse.urljoin(self.base, url)

    # -- the parser's calls
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            if self.title_buf is None and not self.title:
                self.title_buf = []
            return
        if tag in SKIPPED:
            # Only a skipped tag's own end tag closes it, so a void tag inside
            # one, a <meta> in <head> or a page link in a macro parameter, never
            # leaves the rest of the page skipped.
            if tag == "ac:parameter" and self.macros:
                self.plain_target = ("param", a.get("ac:name", ""))
                self.macros[-1]["params"][a.get("ac:name", "")] = ""
            self.skip += 1
            return
        if self.skip or self.pre:
            return
        if tag in HEADINGS:
            self.flush()
            self.heading = HEADINGS[tag]
        elif tag in PARAGRAPHS:
            self.flush()
        elif tag == "br":
            self.buf.append("\n")
        elif tag == "hr":
            self.flush()
            self.emit("---")
        elif tag in ("ul", "ol"):
            self.flush()
            self.lists.append([tag, 0, None])
        elif tag == "li":
            self.flush()
            if not self.lists:
                self.lists.append(["ul", 0, None])
            if self.lists[-1][2] is not None:
                self.end_item()
            self.lists[-1][1] += 1
            self.lists[-1][2] = []
        elif tag == "pre":
            self.flush()
            self.pre = 1
            self.pre_buf = []
        elif tag == "blockquote":
            self.flush()
            self.quote += 1
        elif tag == "table":
            self.flush()
            self.table = []
        elif tag == "tr" and self.table is not None:
            self.table.append([])
        elif tag in ("td", "th") and self.table is not None:
            if not self.table:
                self.table.append([])
            self.cell = []
            self.buf = []
        elif tag == "a":
            self.links.append((self.href(a.get("href", "")), len(self.buf)))
        elif tag == "img":
            alt = a.get("alt", "") or a.get("title", "") or "image"
            self.buf.append(f"![{alt}]({self.href(a['src'])})" if a.get("src") else f"[image: {alt}]")
        elif tag in INLINE:
            self.inline.append((INLINE[tag], len(self.buf)))
        elif tag == "time" and a.get("datetime"):
            self.buf.append(a["datetime"])
        elif tag == "ac:structured-macro" or tag == "ac:macro":
            self.macros.append({"name": a.get("ac:name", "macro"), "params": {}, "plain": [], "body": False})
        elif tag == "ac:plain-text-body":
            self.plain_target = ("plain", None)
        elif tag == "ac:rich-text-body":
            self.flush()
            if self.macros:
                m = self.macros[-1]
                m["body"] = True
                if m["name"] in PANELS:
                    self.quote += 1
                    label = m["params"].get("title") or PANELS[m["name"]]
                    self.emit(f"**{label}**")
        elif tag == "ac:link":
            self.link = {"title": "", "url": "", "text": None, "start": len(self.buf), "page": "", "space": ""}
        elif tag == "ac:link-body":
            pass
        elif tag == "ac:plain-text-link-body":
            self.plain_target = ("linktext", None)
        elif tag == "ri:page" and self.link is not None:
            self.link["title"] = self.link["page"] = a.get("ri:content-title", "")
            self.link["space"] = a.get("ri:space-key", "")
        elif tag == "ri:attachment":
            if self.image is not None:
                self.image["name"] = a.get("ri:filename", "")
            elif self.link is not None:
                self.link["title"] = a.get("ri:filename", "")
        elif tag == "ri:url":
            if self.image is not None:
                self.image["url"] = a.get("ri:value", "")
            elif self.link is not None:
                self.link["url"] = a.get("ri:value", "")
        elif tag == "ri:user" and self.link is not None:
            self.link["title"] = "a user"
        elif tag == "ac:image":
            self.image = {"name": "", "url": ""}
        elif tag == "ac:task-list":
            self.flush()
        elif tag == "ac:task":
            self.flush()
            self.task = {"status": "", "text": None}
        elif tag == "ac:task-status":
            self.plain_target = ("status", None)
        elif tag == "ac:task-body":
            self.buf = []

    def handle_endtag(self, tag):
        if tag == "title":
            if self.title_buf is not None:
                self.title = " ".join("".join(self.title_buf).split())
                self.title_buf = None
            return
        if tag in SKIPPED:
            self.skip = max(0, self.skip - 1)
            if tag == "ac:parameter":
                self.plain_target = None
            return
        if self.skip:
            return
        if self.pre:
            if tag == "pre":
                self.pre = 0
                self.emit(fence("".join(self.pre_buf), ""))
            return
        if tag in HEADINGS:
            self.flush()
            self.heading = 0
        elif tag in PARAGRAPHS:
            self.flush()
        elif tag in ("ul", "ol"):
            self.flush()
            if self.lists:
                self.end_item()
                lst = self.lists.pop()
                block = "\n".join(lst[3:]) if len(lst) > 3 else ""
                self.emit(block)
        elif tag == "li":
            self.flush()
            self.end_item()
        elif tag == "blockquote":
            self.flush()
            self.quote = max(0, self.quote - 1)
        elif tag in ("td", "th") and self.cell is not None:
            self.cell.append(self.text())
            self.table[-1].append(" ".join(" ".join(self.cell).split()).replace("|", "\\|"))
            self.cell = None
        elif tag == "table" and self.table is not None:
            rows = [r for r in self.table if r]
            self.table = None
            if rows:
                width = max(len(r) for r in rows)
                rows = [r + [""] * (width - len(r)) for r in rows]
                lines = ["| " + " | ".join(rows[0]) + " |", "| " + " | ".join("---" for _ in range(width)) + " |"]
                lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
                self.emit("\n".join(lines))
        elif tag == "a" and self.links:
            href, start = self.links.pop()
            text = "".join(self.buf[start:]).strip()
            del self.buf[start:]
            if href and not href.startswith(("javascript:", "data:")):
                self.buf.append(f"[{text or href}]({href})")
            else:
                self.buf.append(text)
        elif tag in INLINE and self.inline:
            marker, start = self.inline.pop()
            segment = "".join(self.buf[start:])
            del self.buf[start:]
            core = segment.strip()
            if core:
                lead = segment[: len(segment) - len(segment.lstrip())]
                trail = segment[len(segment.rstrip()):]
                self.buf.append(f"{lead}{marker}{core}{marker}{trail}")
        elif tag in ("ac:structured-macro", "ac:macro") and self.macros:
            m = self.macros.pop()
            name = m["name"]
            if name in ("code", "noformat") or (m["plain"] and not m["body"]):
                self.flush()
                self.emit(fence("".join(m["plain"]), m["params"].get("language", "") if name == "code" else ""))
            elif m["body"]:
                self.flush()
            else:
                self.buf.append(f"[Confluence macro: {name}]")
        elif tag == "ac:plain-text-body":
            self.plain_target = None
        elif tag == "ac:rich-text-body":
            self.flush()
            if self.macros and self.macros[-1]["name"] in PANELS:
                self.quote = max(0, self.quote - 1)
        elif tag == "ac:plain-text-link-body":
            self.plain_target = None
        elif tag == "ac:link" and self.link is not None:
            link = self.link
            self.link = None
            body = "".join(self.buf[link["start"]:]).strip()
            del self.buf[link["start"]:]
            text = link["text"] or body or link["title"] or link["url"]
            url = link["url"]
            if not url and link["page"] and self.site:
                space = link["space"] or self.space
                url = f"{self.site}/display/{urllib.parse.quote(space)}/{urllib.parse.quote(link['page'])}" if space else ""
            if url:
                self.buf.append(f"[{text}]({url})")
            else:
                self.buf.append(text)
        elif tag == "ac:image" and self.image is not None:
            img = self.image
            self.image = None
            self.buf.append(f"![image]({img['url']})" if img["url"] else f"[image: {img['name'] or 'attachment'}]")
        elif tag == "ac:task-status":
            self.plain_target = None
        elif tag == "ac:task" and self.task is not None:
            text = self.text()
            box = "x" if self.task["status"].strip() == "complete" else " "
            self.task = None
            self.emit(f"- [{box}] {text}")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in ("br", "hr", "img", "time"):
            self.handle_endtag(tag)

    def handle_data(self, data):
        if self.plain_target is not None:
            kind, name = self.plain_target
            if kind == "param" and self.macros:
                self.macros[-1]["params"][name] = self.macros[-1]["params"].get(name, "") + data
            elif kind == "plain" and self.macros:
                self.macros[-1]["plain"].append(data)
            elif kind == "linktext" and self.link is not None:
                self.link["text"] = (self.link["text"] or "") + data
            elif kind == "status" and self.task is not None:
                self.task["status"] += data
            return
        if self.title_buf is not None:
            self.title_buf.append(data)
            return
        if self.skip:
            return
        if self.pre:
            self.pre_buf.append(data)
            return
        self.buf.append(data.replace("\xa0", " "))

    # -- lists
    def end_item(self):
        lst = self.lists[-1]
        if lst[2] is None:
            return
        parts = lst[2]
        lst[2] = None
        marker = "-" if lst[0] == "ul" else f"{lst[1]}."
        first = parts[0] if parts else ""
        lines = [f"{marker} {first}".rstrip()]
        for part in parts[1:]:
            lines += ["  " + line for line in part.split("\n")]
        lst.append("\n".join(lines))

    def result(self) -> str:
        self.flush()
        while self.lists:
            self.end_item()
            lst = self.lists.pop()
            self.emit("\n".join(lst[3:]) if len(lst) > 3 else "")
        return "\n\n".join(b for b in self.blocks if b.strip()).strip() + "\n"


def fence(text: str, language: str) -> str:
    text = text.strip("\n")
    ticks = "```"
    while ticks in text:
        ticks += "`"
    lang = re.sub(r"[^A-Za-z0-9+#.-]", "", language)[:20]
    return f"{ticks}{lang}\n{text}\n{ticks}"


def html_to_markdown(text: str, base: str = "") -> tuple[str, str]:
    """The Markdown and the title, from HTML, XHTML or Confluence storage format, with links resolved against base."""
    text = CDATA.sub(lambda m: html.escape(m.group(1), quote=False), text)
    p = Markdowner(base)
    p.feed(text)
    p.close()
    return p.result(), p.title


def pdf_to_text(data: bytes) -> tuple[str, str]:
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise Refused("pypdf is not installed; run through uv, which installs it") from e
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:  # noqa: BLE001 - any failure to open means no text
                raise Refused("the PDF is encrypted") from None
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
        title = ""
        if reader.metadata and reader.metadata.title:
            title = str(reader.metadata.title)
    except Refused:
        raise
    except Exception as e:  # noqa: BLE001 - a broken PDF is a refusal, not a crash
        raise Refused(f"the PDF could not be read ({type(e).__name__})") from e
    # A page marker before each page's text, so a concept can cite the page.
    marked = [f"<!-- page {n} -->\n{t}" if len(pages) > 1 else t for n, t in enumerate(pages, start=1) if t]
    text = "\n\n".join(marked)
    if not text.strip():
        raise Refused("no text layer in the PDF")
    return text + "\n", title


def decode(data: bytes, charset: str = "", html_page: bool = False) -> str:
    """The text: by its byte order mark, else as UTF-8 when it is, else by the charset the server declared, then one the page declares, then Latin-1."""
    if data.startswith(codecs.BOM_UTF8):
        return data[len(codecs.BOM_UTF8):].decode("utf-8", "replace")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        pass
    names = [charset] if charset else []
    if html_page:
        m = re.search(rb"<meta[^>]+charset\s*=\s*[\"']?\s*([A-Za-z0-9._:-]+)", data[:4096], re.I)
        if m:
            names.append(m.group(1).decode("ascii", "replace"))
    for name in names:
        try:
            codecs.lookup(name)
            return data.decode(name)
        except (LookupError, UnicodeDecodeError):
            continue
    return data.decode("latin-1")


def convert(data: bytes, content_type: str, how: str, charset: str = "", base: str = "") -> tuple[str, str, str]:
    """The Markdown, the title it carried and the converter's name, or a Refused."""
    how = how or TEXT_TYPES.get(content_type, "")
    if not how:
        raise Refused(f"content type {content_type or 'unknown'} is not text; convert: text takes it as text, convert: html-markdown or pdf-text converts it")
    if how == "pdf-text":
        text, title = pdf_to_text(data)
        return shown(text), shown(title), "pdf-text/1"
    if how == "html-markdown":
        text, title = html_to_markdown(decode(data, charset, html_page=True), base)
        return shown(text), shown(title), "html-markdown/1"
    text = decode(data, charset).replace("\r\n", "\n")
    if "\x00" in text:
        raise Refused("the content is binary, not text")
    return shown(text).rstrip("\n") + "\n", "", "text/1"


# ---- the kinds -----------------------------------------------------------------


@dataclass
class Item:
    """One mirrored item, as the lock and the mirror header record it."""

    item: str
    origin: str
    title: str = ""
    version: str = ""
    last_modified: str = ""
    author: str = ""
    etag: str = ""
    blob: str = ""
    text: str = ""
    converted_by: str = ""
    sha256: str = ""
    size: int = 0


class Context:
    def __init__(self, manifest: Manifest, environ: dict, now: str, timeout: int):
        self.manifest = manifest
        self.environ = environ
        self.now = now
        self.timeout = timeout

    def headers(self, entry: Entry) -> dict:
        name, value = entry.auth.value(self.environ)
        return {name: value} if name else {}

    def get(self, url: str, entry: Entry, extra: dict | None = None, accept_304: bool = False) -> Response:
        headers = self.headers(entry)
        headers.update(extra or {})
        return http_get(url, headers, self.manifest.allow_private, entry.max_item_bytes, self.timeout, accept_304)


class Confluence:
    """Listing by CQL on the v1 search path, which Cloud and Data Center both serve, and the body by v2 on Cloud and v1 on Data Center."""

    def __init__(self, ctx: Context, entry: Entry):
        self.ctx, self.entry = ctx, entry
        site = entry.site.rstrip("/")
        self.site = site
        host = urllib.parse.urlsplit(site).hostname or ""
        self.cloud = entry.api == "cloud" or (not entry.api and (host.endswith(".atlassian.net") or host == "api.atlassian.com"))
        self.prefix = site + ("/wiki" if self.cloud and not host == "api.atlassian.com" and "/wiki" not in site else "")
        if host == "api.atlassian.com":
            self.prefix = site + "/wiki"
        self.web = self.prefix
        self.gateway_tried = False

    def api(self, path: str, query: dict | None = None, accept_304: bool = False) -> dict:
        url = self.prefix + path + ("?" + urllib.parse.urlencode(query) if query else "")
        try:
            resp = self.ctx.get(url, self.entry, {"Accept": "application/json"}, accept_304)
        except FetchFailed as e:
            if self.cloud and not self.gateway_tried and str(e).startswith(("401", "403")):
                self.gateway()
                return self.api(path, query, accept_304)
            raise
        try:
            return json.loads(resp.data.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as e:
            raise FetchFailed(f"{url} did not return JSON") from e

    def gateway(self) -> None:
        """A scoped token calls Atlassian's gateway, under the site's cloud id, which the site itself tells."""
        self.gateway_tried = True
        resp = http_get(self.site + "/_edge/tenant_info", {}, self.ctx.manifest.allow_private, 10_000, self.ctx.timeout)
        try:
            cloud_id = json.loads(resp.data.decode("utf-8"))["cloudId"]
        except (UnicodeDecodeError, ValueError, KeyError) as e:
            raise FetchFailed("the site did not tell its cloud id, which a scoped token needs") from e
        if not re.match(r"^[A-Za-z0-9-]+$", cloud_id):
            raise FetchFailed("the cloud id the site gave is not one")
        self.prefix = f"https://api.atlassian.com/ex/confluence/{cloud_id}/wiki"

    def cql(self) -> str:
        s = self.entry.select
        if "cql" in s:
            return str(s["cql"])
        space = f' AND space = "{s["space"]}"' if s.get("space") else ""
        if "label" in s:
            return f'type = page AND label = "{s["label"]}"{space}'
        if "page" in s:
            return f'id = {s["page"]}'
        if "tree" in s:
            return f'(id = {s["tree"]} OR ancestor = {s["tree"]}) AND type = page'
        return f"type = page{space}"

    def listing(self) -> list[dict]:
        items, start, limit = [], 0, 50
        query = {"cql": self.cql(), "expand": "version", "limit": limit, "start": start}
        while True:
            page = self.api("/rest/api/content/search", query)
            results = page.get("results") or []
            for r in results:
                v = r.get("version") or {}
                by = v.get("by") or {}
                items.append({
                    "id": str(r.get("id", "")), "title": str(r.get("title", "")),
                    "version": str(v.get("number", "")), "when": utc(str(v.get("when", "") or v.get("createdAt", ""))),
                    "author": str(by.get("accountId") or by.get("username") or by.get("userKey") or v.get("authorId") or ""),
                    "webui": str((r.get("_links") or {}).get("webui", "")),
                })
                if len(items) > self.entry.max_items:
                    return items
            nxt = (page.get("_links") or {}).get("next")
            if nxt:
                q = urllib.parse.parse_qs(urllib.parse.urlsplit(nxt).query)
                query = {k: v[0] for k, v in q.items()}
                query.setdefault("expand", "version")
                continue
            if len(results) < limit:
                return items
            start += limit
            query = {"cql": self.cql(), "expand": "version", "limit": limit, "start": start}

    def body(self, page_id: str) -> tuple[str, dict]:
        if self.cloud:
            page = self.api(f"/api/v2/pages/{page_id}", {"body-format": "storage"})
            return str(((page.get("body") or {}).get("storage") or {}).get("value", "")), page
        page = self.api(f"/rest/api/content/{page_id}", {"expand": "body.storage,version"})
        return str(((page.get("body") or {}).get("storage") or {}).get("value", "")), page

    def origin(self, webui: str, page_id: str) -> str:
        if webui:
            return self.web + webui
        return f"{self.web}/pages/{page_id}"


def run_confluence(ctx: Context, entry: Entry, prior: dict) -> tuple[list[Item], dict, list[str]]:
    """The items to keep or write, by id; the items left untouched because unchanged; and the ids listed. One page's failure is that page's."""
    c = Confluence(ctx, entry)
    listed = c.listing()
    if len(listed) > entry.max_items:
        raise Refused(f"the selector returns more than max_items ({entry.max_items}); narrow it or raise the cap")
    items, unchanged = [], {}
    for r in listed:
        pid = r["id"]
        if not pid.isdigit():
            continue
        was = prior.get(pid)
        if was and was.get("status") == "ok" and was.get("version") == r["version"] and r["version"]:
            unchanged[pid] = was
            continue
        origin = c.origin(r["webui"], pid)
        try:
            storage, _page = c.body(pid)
            text, title, _how = convert(storage.encode("utf-8"), "text/html", "html-markdown", base=origin)
        except Gone:
            items.append(Item(item=pid, origin=origin, title=r["title"], version="gone"))
            continue
        except Refused as e:
            it = Item(item=pid, origin=origin, title=r["title"])
            it.refused = str(e)  # type: ignore[attr-defined]
            items.append(it)
            continue
        except FetchFailed as e:
            it = Item(item=pid, origin=origin, title=r["title"])
            it.failed = str(e)  # type: ignore[attr-defined]
            items.append(it)
            continue
        raw = storage.encode("utf-8")
        items.append(Item(
            item=pid, origin=origin, title=r["title"] or title, version=r["version"], last_modified=r["when"],
            author=r["author"] if entry.authors else "", text=text, converted_by="confluence-storage-markdown/1",
            sha256=sha256_hex(raw), size=len(raw),
        ))
    return items, unchanged, [r["id"] for r in listed]


def run_http(ctx: Context, entry: Entry, prior: dict) -> tuple[list[Item], dict, list[str]]:
    items, unchanged, listed = [], {}, []
    for url in entry.urls:
        name = slug(PurePosixPath(urllib.parse.urlsplit(url).path).stem or urllib.parse.urlsplit(url).hostname or "page")
        item_id = f"{name}-{sha256_hex(url.encode())[:8]}"
        listed.append(item_id)
        was = prior.get(item_id) or {}
        extra = {}
        if was.get("status") == "ok" and was.get("etag"):
            extra["If-None-Match"] = was["etag"]
        if was.get("status") == "ok" and was.get("last_modified_header"):
            extra["If-Modified-Since"] = was["last_modified_header"]
        try:
            resp = ctx.get(url, entry, extra, accept_304=bool(extra))
            if resp.status == 304:
                unchanged[item_id] = was
                continue
            digest = sha256_hex(resp.data)
            if was.get("status") == "ok" and was.get("sha256") == "sha256:" + digest:
                unchanged[item_id] = was
                continue
            text, title, how = convert(resp.data, content_type_of(resp.headers), entry.convert, charset_of(resp.headers), base=url)
        except Gone:
            items.append(Item(item=item_id, origin=url, title=was.get("title", ""), version="gone"))
            continue
        except Refused as e:
            it = Item(item=item_id, origin=url, title=was.get("title", ""))
            it.refused = str(e)  # type: ignore[attr-defined]
            items.append(it)
            continue
        except FetchFailed as e:
            it = Item(item=item_id, origin=url, title=was.get("title", ""))
            it.failed = str(e)  # type: ignore[attr-defined]
            items.append(it)
            continue
        etag = resp.headers.get("etag", "")
        lm = resp.headers.get("last-modified", "")
        version = re.sub(r"^W/", "", etag).strip('"') if etag else (utc(lm) if lm else digest[:12])
        it = Item(item=item_id, origin=url, title=title or name, version=version, last_modified=utc(lm) if lm else "",
                  etag=etag, text=text, converted_by=how, sha256=digest, size=len(resp.data))
        it.last_modified_header = lm  # type: ignore[attr-defined]
        items.append(it)
    return items, unchanged, listed


def git_url_kind(url: str) -> str:
    """https, http, local or other."""
    if url.startswith("https://"):
        return "https"
    if url.startswith("http://"):
        return "http"
    if url.startswith(("file://", "/", "./", "../")):
        return "local"
    return "other"


def passed_through(env: dict) -> dict:
    """The proxy and certificate variables of this process, for a program that fetches."""
    return {name: os.environ[name] for name in PASSED_THROUGH if os.environ.get(name)} | env


def git_env(entry: Entry, ctx: Context) -> dict:
    """A clean environment for git: the protocols the manifest allows, and the credential as configuration scoped to the entry's address, so it is never on the command line and never sent to another host."""
    # The identity is for the reflog of the fetched ref: without one, git looks
    # the user up, which on a machine with a slow name service waits seconds.
    env = passed_through({"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "/"), "GIT_TERMINAL_PROMPT": "0",
                          "GIT_CONFIG_GLOBAL": os.environ.get("GIT_CONFIG_GLOBAL", "/dev/null"), "GIT_CONFIG_SYSTEM": "/dev/null",
                          "GIT_AUTHOR_NAME": "knowledge-ingest", "GIT_AUTHOR_EMAIL": "knowledge-ingest@localhost",
                          "GIT_COMMITTER_NAME": "knowledge-ingest", "GIT_COMMITTER_EMAIL": "knowledge-ingest@localhost",
                          "LC_ALL": "C.UTF-8", "TMPDIR": os.environ.get("TMPDIR", tempfile.gettempdir())})
    config = [("credential.helper", ""), ("protocol.allow", "never"), ("protocol.https.allow", "always")]
    if ctx.manifest.allow_private:
        config += [("protocol.http.allow", "always"), ("protocol.file.allow", "always")]
    if entry.auth.scheme and git_url_kind(entry.url) in ("https", "http"):
        name, value = entry.auth.value(ctx.environ)
        config.append((f"http.{entry.url}.extraHeader", f"{name}: {value}"))
    env["GIT_CONFIG_COUNT"] = str(len(config))
    for i, (key, value) in enumerate(config):
        env[f"GIT_CONFIG_KEY_{i}"] = key
        env[f"GIT_CONFIG_VALUE_{i}"] = value
    return env


def git_origin(entry: Entry, sha: str, file: str) -> str:
    url = entry.url[:-4] if entry.url.endswith(".git") else entry.url
    parts = urllib.parse.urlsplit(url)
    if parts.hostname == "github.com":
        if url.endswith(".wiki"):
            return f"{url[:-5]}/wiki/{PurePosixPath(file).stem}"
        return f"{url}/blob/{sha}/{file}"
    return f"{entry.url}@{sha}:{file}"


def run_git(ctx: Context, entry: Entry, prior: dict) -> tuple[list[Item], dict, list[str]]:
    """A shallow fetch of the ref, then each chosen file by its blob id, which the lock records so an unchanged file costs no read."""
    if not shutil.which("git"):
        raise FetchFailed("git is not installed")
    if git_url_kind(entry.url) in ("https", "http") and not ctx.manifest.allow_private \
            and address_is_private(urllib.parse.urlsplit(entry.url).hostname or ""):
        raise Refused("the repository is at a private address; allow_private_addresses: true permits it")
    env = git_env(entry, ctx)
    tmp = Path(tempfile.mkdtemp(prefix="ingest-git-"))
    try:
        def git(*args, data=False):
            done = subprocess.run(["git", "-C", str(tmp), *args], env=env, capture_output=True, timeout=600)
            if done.returncode != 0:
                err = done.stderr.decode("utf-8", "replace").strip().splitlines()
                raise FetchFailed("git " + args[0] + " failed: " + (err[-1] if err else "no message"))
            return done.stdout if data else done.stdout.decode("utf-8", "replace")

        git("init", "-q")
        git("remote", "add", "origin", entry.url)
        git("fetch", "-q", "--depth", "1", "origin", entry.ref)
        sha = git("rev-parse", "FETCH_HEAD").strip()
        when = utc(git("log", "-1", "--format=%cI", "FETCH_HEAD").strip())
        spec = ["FETCH_HEAD"] + (["--", entry.path] if entry.path else [])
        blobs = {}
        for line in git("ls-tree", "-r", "-z", *spec, data=True).decode("utf-8", "replace").split("\0"):
            meta, _, name = line.partition("\t")
            fields = meta.split()
            if len(fields) == 3 and fields[1] == "blob" and fields[0] != "120000" and name:  # a symbolic link is not content
                blobs[name] = fields[2]
        include = entry.include or ["*.md"]
        chosen = []
        for f, oid in blobs.items():
            rel = f[len(entry.path) + 1:] if entry.path and f.startswith(entry.path + "/") else f
            if any(fnmatch.fnmatch(rel, g) for g in include) and not any(fnmatch.fnmatch(rel, g) for g in entry.exclude):
                chosen.append((f, rel, oid))
        if len(chosen) > entry.max_items:
            raise Refused(f"the path holds more than max_items ({entry.max_items}) matching files; narrow include or raise the cap")
        items, unchanged = [], {}
        for f, rel, oid in chosen:
            if ".." in PurePosixPath(rel).parts or rel.startswith("/"):
                continue
            item_id = rel if rel.endswith(".md") else rel + ".md"
            was = prior.get(item_id)
            if was and was.get("status") == "ok" and was.get("blob") == oid:
                unchanged[item_id] = was
                continue
            data = git("cat-file", "blob", oid, data=True)
            if b"\x00" in data[:8000]:
                it = Item(item=item_id, origin=git_origin(entry, sha, f), title=rel)
                it.skipped = "a binary file"  # type: ignore[attr-defined]
                items.append(it)
                continue
            if len(data) > entry.max_item_bytes:
                items.append(Item(item=item_id, origin=git_origin(entry, sha, f), version=sha, title=rel))
                items[-1].refused = f"over max_item_bytes ({entry.max_item_bytes})"  # type: ignore[attr-defined]
                continue
            digest = sha256_hex(data)
            if was and was.get("status") == "ok" and was.get("sha256") == "sha256:" + digest:
                unchanged[item_id] = dict(was, blob=oid)
                continue
            text = shown(decode(data).replace("\r\n", "\n")).rstrip("\n") + "\n"
            if not rel.endswith(".md"):
                text = fence(text, PurePosixPath(rel).suffix.lstrip(".")) + "\n"
            items.append(Item(item=item_id, origin=git_origin(entry, sha, f), title=rel, version=sha, last_modified=when,
                              blob=oid, text=text, converted_by="git/1", sha256=digest, size=len(data)))
        return items, unchanged, [c[1] if c[1].endswith(".md") else c[1] + ".md" for c in chosen]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run_command(ctx: Context, entry: Entry, prior: dict, root: Path) -> tuple[list[Item], dict, list[str]]:
    path = root / entry.command
    if not path.is_file():
        raise Refused(f"{entry.command} is not a file under the repository root")
    if shutil.which("git") and subprocess.run(["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"], capture_output=True).returncode == 0:
        tracked = subprocess.run(["git", "-C", str(root), "ls-files", "--error-unmatch", "--", entry.command], capture_output=True)
        if tracked.returncode != 0:
            raise Refused(f"{entry.command} is not tracked by git; a command runs only once it is committed")
    command_digest = sha256_hex(path.read_bytes())
    env = passed_through({"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "/"), "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
                          "TMPDIR": os.environ.get("TMPDIR", tempfile.gettempdir()), "KNOWLEDGE_INGEST_ENTRY": entry.id})
    for name in entry.auth.names():
        if name in ctx.environ:
            env[name] = ctx.environ[name]
    try:
        done = subprocess.run([str(path), *entry.args], cwd=str(root), env=env, capture_output=True, timeout=entry.timeout)
    except subprocess.TimeoutExpired as e:
        raise FetchFailed(f"the command ran past its timeout ({entry.timeout}s)") from e
    except OSError as e:
        raise FetchFailed(f"the command could not be run ({e.strerror})") from e
    if done.returncode != 0:
        err = done.stderr.decode("utf-8", "replace").strip().splitlines()
        raise FetchFailed(f"the command exited {done.returncode}: {err[-1][:200] if err else 'no message'}")
    data = done.stdout
    if len(data) > entry.max_item_bytes:
        raise Refused(f"the output is over max_item_bytes ({entry.max_item_bytes})")
    digest = sha256_hex(data)
    was = prior.get(entry.id)
    if was and was.get("status") == "ok" and was.get("sha256") == "sha256:" + digest and was.get("command_sha256") == command_digest:
        return [], {entry.id: was}, [entry.id]
    text, title, how = convert(data, "text/plain", entry.convert or "text")
    it = Item(item=entry.id, origin=f"command:{entry.command}", title=title or entry.command, version=digest[:12],
              text=text, converted_by=how, sha256=digest, size=len(data))
    it.command_sha256 = command_digest  # type: ignore[attr-defined]
    return [it], {}, [entry.id]


# ---- the run -------------------------------------------------------------------


def repository_visibility(root: Path, given: str) -> str:
    if given:
        return given
    env = os.environ.get("KNOWLEDGE_INGEST_VISIBILITY", "")
    if env:
        return env
    if shutil.which("gh"):
        done = subprocess.run(["gh", "repo", "view", "--json", "visibility", "--jq", ".visibility"], cwd=str(root), capture_output=True, text=True)
        if done.returncode == 0 and done.stdout.strip().lower() in ("public", "private", "internal"):
            return done.stdout.strip().lower()
    return "unknown"


def allowed_here(sensitivity: str, visibility: str) -> str:
    """Empty when the entry may be written where it goes, else the reason it may not."""
    if sensitivity == "public" or sensitivity == "confidential":
        return ""
    if visibility in ("private", "internal"):
        return ""
    if visibility == "public":
        return "internal content is not committed to a public repository; set sensitivity: public on the entry if it may be"
    return "the repository's visibility is unknown, so internal content is not committed; pass --visibility private or public"


def cache_exposed(root: Path) -> str:
    """Empty when git would commit nothing a confidential entry writes, else the reason the entry is refused. A root outside git commits nothing."""
    cache = ".lokf/.cache/mirror/"
    if not shutil.which("git") or subprocess.run(["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"], capture_output=True).returncode != 0:
        return ""
    # check-ignore reads the ignore rules for a path that need not exist. It
    # exits 1 when no rule ignores the path, and 128 when it cannot tell, and
    # either refuses the entry.
    if subprocess.run(["git", "-C", str(root), "check-ignore", "-q", "--no-index", cache + "probe"], capture_output=True).returncode != 0:
        return f"git does not ignore {cache}, where a confidential copy goes; add .cache/ to .lokf/.gitignore, as the sidecar's template does"
    if subprocess.run(["git", "-C", str(root), "ls-files", "--", cache], capture_output=True, text=True).stdout.strip():
        return f"git tracks files under {cache}; remove them with git rm --cached before a confidential entry runs"
    return ""


def mirror_header(entry: Entry, it: Item, lock_item: dict) -> str:
    fm = {"origin": it.origin, "title": it.title, "ingest": entry.id, "kind": entry.kind, "version": str(it.version),
          "sha256": "sha256:" + it.sha256, "retrieved_at": lock_item["retrieved_at"], "converted_by": it.converted_by}
    if it.last_modified:
        fm["last_modified"] = it.last_modified
    if it.author:
        fm["author"] = it.author
    if entry.license:
        fm["license"] = entry.license
    order = ["origin", "title", "ingest", "kind", "version", "last_modified", "author", "sha256", "retrieved_at", "converted_by", "license"]
    lines = ["---"]
    for key in order:
        if key in fm:
            lines.append(yaml.dump({key: fm[key]}, Dumper=Dumper, allow_unicode=True, width=10_000, default_flow_style=False).rstrip("\n"))
    lines.append("---")
    lines.append(f"<!-- A mirror of {it.origin}, kept by the ingest. Edit the source, not this file: the next run writes it again. -->")
    return "\n".join(lines) + "\n\n"


def frontmatter_of(path: Path) -> dict:
    """The frontmatter of a bundle file as a mapping, or an empty one."""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    try:
        fm = yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError:
        return {}
    return fm if isinstance(fm, dict) else {}


def cited_paths(root: Path) -> set:
    """Every path a concept names in resource or sources, relative to the root, with a fragment cut off."""
    out = set()
    knowledge = root / ".lokf" / "knowledge"
    if not knowledge.is_dir():
        return out
    for md in knowledge.rglob("*.md"):
        if ".obsidian" in md.parts:
            continue
        fm = frontmatter_of(md)
        values = [fm.get("resource")]
        for s in fm.get("sources") or []:
            if isinstance(s, dict):
                values.append(s.get("resource"))
        for v in values:
            if isinstance(v, str) and "://" not in v and not v.startswith("/"):
                v = v.split("#", 1)[0]
                out.add((v[2:] if v.startswith("./") else v).rstrip("/"))
    return out


class Run:
    def __init__(self, args, root: Path, manifest: Manifest, lock: dict, visibility: str, environ: dict):
        self.args, self.root, self.manifest, self.lock, self.visibility = args, root, manifest, lock, visibility
        self.now = now_utc(args.now)
        self.ctx = Context(manifest, environ, self.now, args.timeout)
        self.summary: list[str] = []
        self.failed = 0
        self.writes: list[tuple[Path, str]] = []
        self.removals: list[Path] = []
        self.counts = {"fetched": 0, "restored": 0, "unchanged": 0, "gone": 0, "unlisted": 0, "failed": 0, "refused": 0, "skipped": 0}

    def mirror_root(self, entry: Entry) -> Path:
        if entry.sensitivity == "confidential":
            return self.root / ".lokf" / ".cache" / "mirror"
        return self.root / self.manifest.mirror

    def rel(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()

    def entry_mirror_size(self, prior: dict) -> int:
        return sum(int(v.get("bytes", 0) or 0) for v in prior.values() if v.get("status") == "ok")

    def total_mirror_size(self) -> int:
        return sum(self.entry_mirror_size(e.get("items", {})) for e in self.lock["entries"].values())

    def run_entry(self, entry: Entry) -> None:
        record = self.lock["entries"].setdefault(entry.id, {"status": "ok", "items": {}})
        prior = record.get("items", {})
        counts = {"fetched": 0, "restored": 0, "unchanged": 0, "gone": 0, "unlisted": 0, "failed": 0, "refused": 0, "skipped": 0}
        # A file the lock calls current and the disk has lost is handed to the
        # kind as if new, so it is fetched again instead of skipped as unchanged.
        missing = {i for i, was in prior.items() if was.get("status") == "ok" and was.get("path") and not (self.root / was["path"]).is_file()}
        present = {i: was for i, was in prior.items() if i not in missing}
        why = allowed_here(entry.sensitivity, self.visibility)
        if not why and entry.sensitivity == "confidential":
            why = cache_exposed(self.root)
        if why:
            record.update({"status": "refused", "reason": why})
            self.failed += 1
            self.summary.append(f"- {entry.id} ({entry.describe()}): refused, {why}")
            return
        try:
            if entry.kind == "confluence":
                items, unchanged, listed = run_confluence(self.ctx, entry, present)
            elif entry.kind == "http":
                items, unchanged, listed = run_http(self.ctx, entry, present)
            elif entry.kind == "git":
                items, unchanged, listed = run_git(self.ctx, entry, present)
            else:
                items, unchanged, listed = run_command(self.ctx, entry, present, self.root)
        except Refused as e:
            record.update({"status": "refused", "reason": str(e)})
            self.failed += 1
            self.summary.append(f"- {entry.id} ({entry.describe()}): refused, {e}")
            return
        except (FetchFailed, Gone) as e:
            record.update({"status": "failed", "reason": str(e)})
            self.failed += 1
            self.summary.append(f"- {entry.id} ({entry.describe()}): failed, {e}")
            return
        except Exception as e:  # noqa: BLE001 - a surprise in one entry is recorded there, and the run goes on
            reason = f"an error this script did not expect, {type(e).__name__}: {' '.join(str(e).split())[:200]}"
            record.update({"status": "failed", "reason": reason})
            self.failed += 1
            self.summary.append(f"- {entry.id} ({entry.describe()}): failed, {reason}")
            return
        record["status"] = "ok"
        record.pop("reason", None)
        new_items: dict = {}
        skipped: list[str] = []
        folder = self.mirror_root(entry) / entry.id
        total = self.total_mirror_size() - self.entry_mirror_size(prior)
        for item_id, was in unchanged.items():
            new_items[item_id] = was
            counts["unchanged"] += 1
            total += int(was.get("bytes", 0) or 0)
        for it in items:
            was = prior.get(it.item) or {}
            if getattr(it, "skipped", ""):
                skipped.append(f"  - {it.item}: skipped, {it.skipped}")  # type: ignore[attr-defined]
                counts["skipped"] += 1
                continue
            if getattr(it, "refused", ""):
                new_items[it.item] = dict(was, status="refused", reason=it.refused, origin=it.origin, title=it.title)  # type: ignore[attr-defined]
                counts["refused"] += 1
                continue
            if getattr(it, "failed", ""):
                new_items[it.item] = dict(was, status="failed", reason=it.failed, origin=it.origin, title=it.title)  # type: ignore[attr-defined]
                counts["failed"] += 1
                continue
            if it.version == "gone":
                new_items[it.item] = dict(was, status="gone", origin=it.origin, since=self.away_since(was))
                counts["gone"] += 1
                continue
            target = (folder / (it.item if it.item.endswith(".md") else it.item + ".md")).resolve()
            try:
                target.relative_to(folder.resolve())
            except ValueError:
                new_items[it.item] = dict(was, status="refused", reason="a path outside the entry's folder", origin=it.origin)
                counts["refused"] += 1
                continue
            if target.suffix != ".md" or "\n" in it.item or any(unicodedata.category(c) in ("Cc", "Cf") for c in it.item):
                new_items[it.item] = dict(was, status="refused", reason="a name this script does not write", origin=it.origin)
                counts["refused"] += 1
                continue
            if total + it.size > self.manifest.max_total_bytes:
                reason = f"the mirror would pass max_total_bytes ({self.manifest.max_total_bytes})"
                new_items[it.item] = dict(was, status="refused", reason=reason, origin=it.origin)
                counts["refused"] += 1
                continue
            total += it.size
            lock_item = {"path": self.rel(target), "origin": it.origin, "title": it.title, "version": str(it.version),
                         "sha256": "sha256:" + it.sha256, "bytes": it.size, "retrieved_at": self.now, "status": "ok"}
            if it.last_modified:
                lock_item["last_modified"] = it.last_modified
            if it.author:
                lock_item["author"] = it.author
            if it.etag:
                lock_item["etag"] = it.etag
            if it.blob:
                lock_item["blob"] = it.blob
            if getattr(it, "last_modified_header", ""):
                lock_item["last_modified_header"] = it.last_modified_header  # type: ignore[attr-defined]
            if getattr(it, "command_sha256", ""):
                lock_item["command_sha256"] = it.command_sha256  # type: ignore[attr-defined]
            new_items[it.item] = lock_item
            counts["restored" if it.item in missing else "fetched"] += 1
            self.writes.append((target, mirror_header(entry, it, lock_item) + it.text))
        for item_id, was in prior.items():
            if item_id not in new_items:
                new_items[item_id] = dict(was, status="unlisted", since=self.away_since(was))
                counts["unlisted"] += 1
        record["items"] = new_items
        for k, v in counts.items():
            self.counts[k] += v
        parts = [f"{v} {k}" for k, v in counts.items() if v]
        self.summary.append(f"- {entry.id} ({entry.describe()}): " + (", ".join(parts) if parts else "nothing listed"))
        for item_id, it in sorted(new_items.items()):
            if it.get("status") in ("refused", "failed", "gone", "unlisted"):
                reason = f", {it['reason']}" if it.get("reason") else ""
                since = f" since {it['since'][:10]}" if it.get("since") and it["status"] in ("gone", "unlisted") else ""
                self.summary.append(f"  - {item_id}: {it['status']}{since}{reason}")
        self.summary.extend(skipped)
        if counts["failed"] or counts["refused"]:
            self.failed += 1

    def away_since(self, was: dict) -> str:
        """When the item first went gone or unlisted: kept from the lock while it stays away, else this run."""
        return str(was.get("since") or self.now) if was.get("status") in ("gone", "unlisted") else self.now

    def prune(self) -> None:
        """Remove a gone or unlisted file no concept cites, once an earlier run recorded it so: the pull request shows the status one week and the removal the next."""
        cited = cited_paths(self.root)
        for eid, record in self.lock["entries"].items():
            for item_id in list(record.get("items", {})):
                it = record["items"][item_id]
                if it.get("status") not in ("gone", "unlisted"):
                    continue
                path = it.get("path", "")
                if path in cited:
                    self.summary.append(f"- {eid}: {path} is {it['status']} and a concept still cites it, so it stays")
                    continue
                if str(it.get("since", "")) >= self.now:
                    self.summary.append(f"- {eid}: {path} went {it['status']} on this run, so it stays until the next")
                    continue
                self.removals.append(self.root / path)
                del record["items"][item_id]
                self.summary.append(f"- {eid}: {path} was {it['status']} since {str(it.get('since', ''))[:10] or 'an earlier run'} and no concept cites it; removed")

    def commit(self, lock_path: Path) -> bool:
        """Write the mirror files and the lock, or say what would be written. True when anything changed on disk."""
        changed = False
        for path, text in self.writes:
            if path.is_file() and path.read_text(encoding="utf-8") == text:
                continue
            changed = True
            if not self.args.dry_run:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8", newline="\n")
        left = [eid for eid in self.lock["entries"] if not any(e.id == eid for e in self.manifest.entries)]
        cited = cited_paths(self.root) if left else set()
        for eid in left:
            record = self.lock["entries"].pop(eid)
            for _item_id, it in sorted(record.get("items", {}).items()):
                path = str(it.get("path", ""))
                if not path:
                    continue
                self.removals.append(self.root / path)
                note = ", and a concept still cites it, so the work list will name its source as gone" if path in cited else ""
                self.summary.append(f"- {eid}: no longer in the manifest, so {path} is removed{note}")
            if not record.get("items"):
                self.summary.append(f"- {eid}: no longer in the manifest, so its record is dropped")
        for path in self.removals:
            if path.is_file():
                changed = True
                if not self.args.dry_run:
                    path.unlink()
                    parent = path.parent
                    while parent != self.root and parent.is_dir() and not any(parent.iterdir()):
                        parent.rmdir()
                        parent = parent.parent
        text = to_yaml(self.lock)
        if not lock_path.is_file() or lock_path.read_text(encoding="utf-8") != text:
            changed = True
            if not self.args.dry_run:
                lock_path.parent.mkdir(parents=True, exist_ok=True)
                lock_path.write_text(text, encoding="utf-8", newline="\n")
        return changed


def status_line(root: Path, manifest_path: Path, lock_path: Path, environ: dict) -> str:
    if not manifest_path.is_file():
        return "ingest: no .lokf/ingest.yaml, so no source outside the repository is mirrored"
    try:
        manifest = read_manifest(manifest_path)
    except Stop as e:
        return f"ingest: .lokf/ingest.yaml cannot be read ({e})"
    names = sorted({n for e in manifest.entries for n in e.auth.names()})
    present = [n for n in names if environ.get(n)]
    absent = [n for n in names if not environ.get(n)]
    files, newest, missing, away, named = 0, "", 0, 0, set()
    try:
        lock = read_lock(lock_path)
        for record in lock["entries"].values():
            for it in record.get("items", {}).values():
                path = str(it.get("path", ""))
                named.add(path)
                if it.get("status") == "ok":
                    files += 1
                    newest = max(newest, str(it.get("retrieved_at", "")))
                    if path and not (root / path).is_file():
                        missing += 1
                elif it.get("status") in ("gone", "unlisted"):
                    away += 1
    except Stop:
        pass
    mirror = root / MIRROR
    stray = sum(1 for f in mirror.rglob("*") if f.is_file() and f.relative_to(root).as_posix() not in named) if mirror.is_dir() else 0
    parts = [f"{len(manifest.entries)} entries in .lokf/ingest.yaml", f"{files} mirrored files" + (f", newest {newest[:10]}" if newest else ", no lock yet")]
    if missing:
        parts.append(f"{missing} missing from the mirror, which a run restores")
    if stray:
        parts.append(f"{stray} files in the mirror the lock does not name")
    if away:
        parts.append(f"{away} gone or unlisted, which --prune removes once no concept cites them")
    if present:
        parts.append("tokens present: " + ", ".join(present))
    if absent:
        parts.append("tokens absent: " + ", ".join(absent))
    return "ingest: " + "; ".join(parts)


def write_patch(root: Path, manifest: Manifest, lock: dict, patch_path: Path) -> int:
    """Reference concepts for the entries that ask for them, as operations for the pen; how many."""
    if patch_path.exists():
        raise Stop(f"{patch_path} exists; apply or remove it first")
    index = root / ".lokf" / "knowledge" / "index.md"
    base_iri = str(frontmatter_of(index).get("base_iri") or "") if index.is_file() else ""
    ops, used = [], set()
    for entry in manifest.entries:
        if not entry.reference:
            continue
        record = lock["entries"].get(entry.id) or {}
        committed = entry.sensitivity != "confidential"
        for item_id, it in sorted(record.get("items", {}).items()):
            if it.get("status") != "ok":
                continue
            stem = item_id[:-3] if item_id.endswith(".md") else item_id
            concept = f"references/{entry.id}-{slug(stem)}.md"
            if concept in used:  # two items whose names slug alike
                concept = f"references/{entry.id}-{slug(stem)[:50]}-{sha256_hex(item_id.encode())[:8]}.md"
            used.add(concept)
            title = str(it.get("title") or item_id)
            version = str(it.get("version", ""))
            when = str(it.get("last_modified") or it.get("retrieved_at", ""))[:10]
            source = {"resource": it["path"], "title": f"{title}, mirrored by the ingest"}
            if it.get("last_modified"):
                source["last_modified"] = it["last_modified"]
            if entry.owner:
                source["author"] = entry.owner
            where = f"kept at {it['path']} by the ingest" if committed else "kept outside the repository by the ingest"
            description = f"A copy of {title}, {where} from {entry.kind}; version {version} as of {when}."
            path = root / ".lokf" / "knowledge" / concept
            if path.is_file():
                fm = frontmatter_of(path)
                if f"version {version} " in str(fm.get("description", "")):
                    continue
                # The ingest's own source entry is replaced; every other one a person or the librarian added stays.
                sources = [s for s in (fm.get("sources") or []) if not (isinstance(s, dict) and s.get("resource") == it["path"])]
                sets = {"description": description}
                if committed:
                    sets["sources"] = sources + [source]
                ops.append({"op": "patch", "path": concept, "set": sets,
                            "log": f"**Changed**: the ingest mirrored a newer version of {title} ({version})."})
                continue
            fm = {"type": "Reference", "title": title, "description": description, "resource": it["origin"], "tags": ["ingest", entry.id]}
            if committed:
                fm["sources"] = [source]
            if base_iri:
                fm["id"] = base_iri + concept[:-3]
            copy = (f"A copy of <{it['origin']}> is kept at `{it['path']}` by the ingest. The copy is what the bundle's concepts cite, "
                    "and the source is where it is edited." if committed else
                    f"A copy of <{it['origin']}> is kept outside the repository by the ingest, under `.lokf/.cache/mirror/`, "
                    "which is never committed; the source is where it is edited.")
            body = f"# {title}\n\n{copy}" + (f" {entry.why[0].upper() + entry.why[1:]}." if entry.why else "") + "\n"
            ops.append({"op": "create", "path": concept, "frontmatter": fm, "body": body,
                        "log": f"**Added**: {title}, a reference to a source the ingest mirrors."})
    if not ops:
        return 0
    patch_path.write_text(to_yaml({"by": "process:knowledge-ingest", "ops": ops}), encoding="utf-8", newline="\n")
    return len(ops)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="knowledge-ingest.py", description="Mirror knowledge from outside the repository into .lokf/mirror/.")
    ap.add_argument("--root", default="")
    ap.add_argument("--manifest", default="")
    ap.add_argument("--lock", default="")
    ap.add_argument("--visibility", default="", choices=["", "public", "private", "internal", "unknown"])
    ap.add_argument("--only", action="append", default=[])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--prune", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--summary", default="")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--patch", nargs="?", const=".lokf/patch.yaml", default="")
    ap.add_argument("--now", default="")
    ap.add_argument("--timeout", type=int, default=TIMEOUT)
    args = ap.parse_args(argv)
    root = Path(args.root).resolve() if args.root else Path.cwd().resolve()
    manifest_path = Path(args.manifest) if args.manifest else root / ".lokf" / "ingest.yaml"
    lock_path = Path(args.lock) if args.lock else root / ".lokf" / "ingest.lock.yaml"
    environ = dict(os.environ)
    if args.status:
        say(status_line(root, manifest_path, lock_path, environ))
        return 0
    try:
        manifest = read_manifest(manifest_path)
        lock = read_lock(lock_path)
        for eid in args.only:
            if not any(e.id == eid for e in manifest.entries):
                raise Stop(f"--only {eid} names no entry in the manifest")
        if args.patch:
            n = write_patch(root, manifest, lock, root / args.patch if not Path(args.patch).is_absolute() else Path(args.patch))
            say(f"wrote {n} operation{'s' if n != 1 else ''} for the pen" if n else "no entry asks for Reference concepts, or every one has its concept")
            return 0
        visibility = repository_visibility(root, args.visibility)
        run = Run(args, root, manifest, lock, visibility, environ)
        for entry in manifest.entries:
            if args.only and entry.id not in args.only:
                continue
            if entry.disabled:
                run.summary.append(f"- {entry.id}: disabled, its mirror kept as it is")
                continue
            run.run_entry(entry)
        if args.prune:
            run.prune()
        changed = run.commit(lock_path)
    except Stop as e:
        print(f"knowledge-ingest: {e}", file=sys.stderr)
        return 1
    heading = f"## Ingest on {run.now[:10]}" + (" (dry run)" if args.dry_run else "")
    files = sum(1 for r in lock["entries"].values() for it in r.get("items", {}).values() if it.get("status") == "ok")
    size = run.total_mirror_size()
    tail = (f"Mirror: {files} file{'s' if files != 1 else ''}, {size / 1_000_000:.1f} MB, repository {visibility}. "
            "Nothing fetched is knowledge yet: the librarian derives concepts from the mirror on its next run.")
    if not changed:
        tail = "Nothing changed since the last run. " + tail
    lines = [heading, "", *run.summary, "", tail, ""]
    text = "\n".join(lines)
    say(text.rstrip("\n"))
    if args.summary:
        Path(args.summary).write_text(text, encoding="utf-8", newline="\n")
    if args.strict and run.failed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
