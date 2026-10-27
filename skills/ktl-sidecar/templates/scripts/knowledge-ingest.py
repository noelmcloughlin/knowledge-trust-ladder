#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml==6.0.3", "pypdf==6.21.2"]
# [tool.uv]
# exclude-newer = "2026-10-22T00:00:00Z"
# ///
# The ingest: knowledge outside the repository, mirrored into it.
#
# Reads .lokf/ingest.yaml, fetches each source it names, converts it to
# Markdown and writes it under .lokf/mirror/<entry id>/, one file per page
# or document, with a header: origin, title, version, digest, retrieval
# time, converter. The lock, .lokf/ingest.lock.yaml, records the same per
# item and a status: ok, gone, unlisted, failed, refused or skipped. A mirror file is repository
# content the librarian reads as any tracked file. It is not knowledge yet.
#
# A confidential entry's copies and their records stay out of git: the copies
# under .lokf/.cache/mirror/ and the records in .lokf/.cache/ingest.lock.yaml.
# The committed lock holds the entry's status alone, so no title, address or
# author of a confidential page is committed, unless the entry sets
# lock_details: true. Records move between the locks on the entry's next run.
#
# Kinds:
#   - `confluence`: a label, space, page, tree or CQL selection; v1 search
#     everywhere, v2 body on Cloud and v1 on Data Center; the version number
#     is the change signal.
#   - `http`: addresses serving HTML, Markdown, text or PDF; ETag and
#     Last-Modified when the server gives them, else the digest.
#   - `git`: a path at a ref, over https, or http and a local path where the
#     manifest allows private addresses; the commit is the version and the
#     blob id the change signal, so a file is downloaded only when it
#     changed; a file that is not Markdown is fenced.
#   - `command`: a tracked command's output; the command's own digest is
#     recorded too.
#
# Listing comes before fetching, so an unchanged source costs a listing and no body. The
# mirror and the lock change only when content changes. An entry that leaves
# the manifest takes its folder with it. A file the lock names and the disk
# has lost is fetched again and reported as restored. A name the workflow
# would not publish, such as one with a space, is spelled in plain
# characters, with a digest of the name so no two meet. At its time limit
# the run starts no more work and writes what it has, and what it did not
# reach keeps its record for the next run.
#
# Refused and recorded:
#   - a token in the manifest (auth names environment variables starting
#     KNOWLEDGE_INGEST_);
#   - an entry the repository's visibility does not allow (internal: a
#     private repository only; confidential: never committed, kept under
#     .lokf/.cache/mirror/, and refused where git does not ignore that folder
#     or tracks a file in it);
#   - more than max_items;
#   - a body over max_item_bytes or a mirror over max_total_bytes;
#   - a private address unless the manifest allows it;
#   - a git host name outside ASCII, where the manifest refuses private
#     addresses, and a git address that git's own configuration rewrites;
#   - a path outside the mirror root;
#   - an unexpected content type;
#   - a PDF with no text layer.
#
# Characters no reader sees are removed, apart from the two joiners
# some scripts spell with. One entry's failure, expected or not, never stops
# the others.
#
# Usage, through knowledge-ingest.sh beside it:
#   knowledge-ingest.py [--root DIR] [--visibility public|private|internal|unknown]
#                       [--only ID]... [--dry-run] [--prune] [--strict]
#                       [--summary FILE] [--status] [--patch [FILE]]
#                       [--time-limit MINUTES]
#   --dry-run   compare and fetch, write nothing
#   --only      one entry; the others keep their lock state
#   --prune     delete a gone or unlisted file no concept cites, once an
#               earlier run recorded it so; the lock's `since` says when
#   --strict    exit 1 when any entry failed or was refused
#   --summary   the run's summary, in Markdown, to FILE
#   --status    one line for the preflight
#   --patch     Reference concepts for entries with `reference: true`, as
#               operations for knowledge-apply.sh, to .lokf/patch.yaml or FILE
#   --time-limit  the minutes after which the run starts no more work (25),
#               so it ends inside the workflow job's 30 with its work written
# Exit 0 completed (the lock says how each entry fared); 1 stopped by the
# manifest or an argument before any write; 2 a tool is missing.
#
# The dependency block names one pypdf release, and `exclude-newer` takes no
# file uploaded after its date. pypdf reads PDFs from outside the repository,
# so when a release fixes a flaw in it, move both.
"""The ingest: knowledge outside the repository, mirrored into it."""

from __future__ import annotations

import argparse
import base64
import codecs
import contextlib
import fnmatch
import functools
import hashlib
import html
import http.client
import io
import ipaddress
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
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
CACHE = ".lokf/.cache/mirror"  # a confidential entry's copies, which git ignores
CACHE_LOCK = ".lokf/.cache/ingest.lock.yaml"  # their records, beside them
TOP_KEYS = {"ingest_version", "max_total_bytes", "allow_private_addresses", "services", "defaults", "entries"}
SERVICE_KEYS = {"kind", "site", "api", "auth"}
AUTH_KEYS = {"scheme", "env", "user_env", "header"}
DEFAULT_KEYS = {"sensitivity", "max_items", "max_item_bytes", "authors", "lock_details"}
ENTRY_KEYS = {
    "id", "kind", "service", "site", "api", "auth", "select", "urls", "url", "ref", "path", "include", "exclude",
    "command", "args", "timeout", "convert", "owner", "why", "license", "sensitivity", "max_items",
    "max_item_bytes", "authors", "lock_details", "disabled", "reference",
}
SELECT_KEYS = {"label", "space", "page", "tree", "cql"}
CONVERTS = ("html-markdown", "pdf-text", "text")
DEFAULTS = {"sensitivity": "internal", "max_items": 200, "max_item_bytes": 1_000_000, "authors": True, "lock_details": False}
DEFAULT_TOTAL_BYTES = 50_000_000
TIMEOUT = 30
TIME_LIMIT = 25  # minutes; the workflow's job stops at 30, and the work after the run takes about one
GIT_BATCH = 50  # the files a git entry downloads at a time, so a run stopped at its limit keeps those it read
BODY_TIMEOUTS = 10  # the time a whole body may take, in timeouts: the timeout bounds each wait for a byte, and a body sent a byte at a time meets it
ATTEMPTS = 3
TEXT_TYPES = {"text/markdown": "text", "text/x-markdown": "text", "text/plain": "text", "text/html": "html-markdown",
              "application/xhtml+xml": "html-markdown", "application/pdf": "pdf-text"}
KEPT = "\u200c\u200d"  # the zero-width non-joiner and joiner, which Persian, Arabic and Indic scripts and emoji sequences spell with
# The characters Unicode calls default ignorable, which a renderer draws as
# nothing, beyond the format and control characters: variation selectors,
# which can spell hidden text after a visible character, the Hangul fillers
# and the combining grapheme joiner, among others.
IGNORABLE = re.compile("[\u034f\u115f\u1160\u17b4\u17b5\u180b-\u180f\u2065\u3164\ufe00-\ufe0f\uffa0\ufff0-\ufff8\U000e0000-\U000e0fff]")
PLAIN_PATH = re.compile(r"[A-Za-z0-9._/@+-]+")  # the characters the workflow's publish job lets a path hold
PASSED_THROUGH = ("http_proxy", "https_proxy", "all_proxy", "no_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
                  "SSL_CERT_FILE", "SSL_CERT_DIR", "GIT_SSL_CAINFO", "GIT_SSL_CAPATH", "CURL_CA_BUNDLE")  # a proxy and a company's certificate reach git and a command


class Stop(Exception):
    """The manifest or an argument stopped the run before any write."""


class Refused(Exception):
    """One item or entry is refused, with the reason the lock records."""


class FetchFailed(Exception):
    """A request did not complete, with the reason the lock records."""


class Gone(Exception):
    """The source answered 404 or 410."""


class OutOfTime(Exception):
    """The run passed its time limit. The item in hand, and every one after it, keeps its record for the next run."""


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
    # The fraction gets six digits, which fromisoformat reads on every Python
    # from 3.9. Before 3.11 it reads three or six digits only, so .5 and
    # .000123456 would both stop it.
    t = re.sub(r"\.(\d+)", lambda m: "." + (m.group(1) + "000000")[:6], t)
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
    try:
        return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except OverflowError:  # an offset that carries the time past year 1 or 9999
        return text.strip()


def shown(text: str) -> str:
    """The text without the characters no reader sees, line breaks, tabs and the two joiners kept.

    A lone surrogate, which a server's charset such as unicode_escape can
    decode to and no UTF-8 file can hold, becomes the replacement character,
    as a byte that does not decode does.
    """
    out = []
    for ch in text:
        if ch in "\n\t" or ch in KEPT:
            out.append(ch)
        elif ch == "\r":
            continue
        elif unicodedata.category(ch) in ("Cc", "Cf") or IGNORABLE.match(ch):
            continue
        elif unicodedata.category(ch) == "Cs":
            out.append("\ufffd")
        elif ch in "\u2028\u2029":
            out.append("\n")
        elif ch == "\xa0":
            out.append(" ")
        else:
            out.append(ch)
    return "".join(out)


def one_line(text: str) -> str:
    """A title or a name as the mirror header and the lock record it: one line, with no character a reader cannot see."""
    return " ".join(shown(text).split())


def discreet(reason: str) -> str:
    """A reason as the summary and the committed lock give it for a confidential entry: each address cut to its site, and no line a command printed."""
    reason = re.sub(r"\b([a-z][a-z0-9+.-]*://[^/\s?#'\")]*)[^\s'\")]*", r"\1", reason)
    return re.sub(r"^(the command exited -?\d+):.*$", r"\1", reason, flags=re.S)


def write_text(path: Path, text: str) -> None:
    """Write UTF-8 text with line feeds on every platform. Path.write_text takes newline= only from Python 3.10, and the script runs on 3.9."""
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:60] or "item"


def md_name(item: str) -> str:
    """The mirror's name for an item: its own when it ends .md, else with .md added."""
    return item if item.endswith(".md") else item + ".md"


def publishable(name: str) -> str:
    """A mirror path the workflow publishes: the name as it is when it is plain, else each part that is not spelled in plain characters.

    Accents are dropped, any other character outside the plain set becomes
    a hyphen, and a digest of the part as it was is added, so two names
    that spell alike, such as "a b.md" and "a-b.md", never meet.
    """
    if PLAIN_PATH.fullmatch(name):
        return name
    parts = []
    for part in name.split("/"):
        if PLAIN_PATH.fullmatch(part):
            parts.append(part)
            continue
        stem, ext = (part[:-3], ".md") if part.endswith(".md") else (part, "")
        plain = unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode()
        plain = re.sub(r"[^A-Za-z0-9._@+-]+", "-", plain).strip("-")[:60].rstrip("-") or "item"
        parts.append(f"{plain}-{sha256_hex(part.encode('utf-8', 'surrogatepass'))[:8]}{ext}")
    return "/".join(parts)


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
        token = secret(environ, self.env)
        if not token:
            raise FetchFailed(f"no credential in {self.env}")
        if self.scheme == "basic":
            user = secret(environ, self.user_env) if self.user_env else "x-access-token"
            if self.user_env and not user:
                raise FetchFailed(f"no user in {self.user_env}")
            return "Authorization", "Basic " + base64.b64encode(f"{user}:{token}".encode()).decode()
        if self.scheme == "bearer":
            return "Authorization", "Bearer " + token
        return self.header, token


def secret(environ: dict, name: str) -> str:
    """A value from the environment, without the spaces or line break a pasted secret can end with.

    A control character inside it is refused by the variable's name. In a
    header, a line break makes the request fail with an error that quotes
    the header, and that error would carry the credential into the lock.
    """
    value = environ.get(name, "").strip()
    if any(unicodedata.category(ch) == "Cc" for ch in value):
        raise FetchFailed(f"{name} holds a control character, such as a line break, inside its value")
    return value


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
    lock_details: bool = False
    disabled: bool = False
    reference: bool = False

    @property
    def local_lock(self) -> bool:
        """Whether the entry's item records stay out of the committed lock: a confidential entry's do, unless it sets lock_details."""
        return self.sensitivity == "confidential" and not self.lock_details

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


def flag(value, where: str, default: bool) -> bool:
    """A yes or no. A string is refused, since Python counts "false" as true."""
    if value is None:
        return default
    if not isinstance(value, bool):
        raise Stop(f"{where} is true or false, without quotes")
    return value


def strings(value, where: str) -> list[str]:
    """A list of values, as text. A string is refused, since each of its characters would count as an item: a glob, an argument or an address."""
    if value is None:
        return []
    if not isinstance(value, list) or any(isinstance(v, (dict, list)) for v in value):
        raise Stop(f"{where} is a list, not a single string")
    return [str(v) for v in value]


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
    allow_private = flag(raw.get("allow_private_addresses"), "allow_private_addresses", False)
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
    for key in ("authors", "lock_details"):
        defaults[key] = flag(raw_defaults.get(key), f"defaults.{key}", DEFAULTS[key])
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
        select = e.get("select") or {}
        if not isinstance(select, dict):
            raise Stop(f"{where}: select is a mapping, such as label: ktl")
        entry = Entry(
            id=eid, kind=kind, site=site, api=api, auth=auth,
            select=dict(select), urls=strings(e.get("urls"), f"{where}.urls"),
            url=str(e.get("url", "")), ref=str(e.get("ref", "")), path=str(e.get("path", "")).strip("/"),
            include=strings(e.get("include"), f"{where}.include"), exclude=strings(e.get("exclude"), f"{where}.exclude"),
            command=str(e.get("command", "")), args=strings(e.get("args"), f"{where}.args"),
            timeout=positive_int(e.get("timeout"), f"{where}.timeout", 120), convert=convert,
            owner=owner, why=str(e.get("why", "")),
            license=str(e.get("license", "")), sensitivity=sens,
            max_items=positive_int(e.get("max_items", defaults["max_items"]), f"{where}.max_items", 200),
            max_item_bytes=positive_int(e.get("max_item_bytes", defaults["max_item_bytes"]), f"{where}.max_item_bytes", 1_000_000),
            authors=flag(e.get("authors"), f"{where}.authors", defaults["authors"]),
            lock_details=flag(e.get("lock_details"), f"{where}.lock_details", defaults["lock_details"]),
            disabled=flag(e.get("disabled"), f"{where}.disabled", False),
            reference=flag(e.get("reference"), f"{where}.reference", False),
        )
        check_entry(entry, where)
        if entry.kind == "confluence" and entry.site.startswith("http://") and not allow_private:
            raise Stop(f"{where}: {entry.site} is over http; use https, or allow_private_addresses: true for an intranet site")
        for u in entry.urls if entry.kind == "http" and not allow_private else []:
            if urllib.parse.urlsplit(u).scheme == "http":
                raise Stop(f"{where}: {u} is over http; use https, or allow_private_addresses: true for an intranet site")
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
    if not isinstance(raw, dict) or str(raw.get("ingest_lock_version", "")) != LOCK_VERSION:
        raise Stop(f"{path.name}: ingest_lock_version is \"{LOCK_VERSION}\" for this script")
    # A lock edited by hand into another shape stops the run here, by name,
    # and not with a traceback halfway through.
    shape = f"{path.name}: entries maps each entry id to its record, and a record's items map each item id to its record"
    raw["entries"] = raw.get("entries") or {}
    if not isinstance(raw["entries"], dict):
        raise Stop(shape)
    for record in raw["entries"].values():
        if not isinstance(record, dict):
            raise Stop(shape)
        if "items" in record:
            record["items"] = record["items"] or {}
        if not isinstance(record.get("items", {}), dict) or not all(isinstance(it, dict) for it in record.get("items", {}).values()):
            raise Stop(shape)
    return raw


def read_cache_lock(path: Path) -> dict:
    """The records of the confidential entries' copies, or none when the cache was cleared or cannot be read, since a run then fetches the copies again."""
    try:
        return read_lock(path)
    except Stop:
        return {"ingest_lock_version": LOCK_VERSION, "entries": {}}


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


def proxy_for(url: str, git: bool = False) -> str:
    """The proxy a request to url goes through, as urllib decides it, or "" for none.

    urllib reads the environment, and on macOS and Windows the system's
    settings too. For git, all_proxy counts too: git reads it when no
    variable names a proxy for the scheme.
    """
    parts = urllib.parse.urlsplit(url)
    proxies = urllib.request.getproxies()
    proxy = proxies.get(parts.scheme) or (proxies.get("all", "") if git else "")
    return "" if not proxy or urllib.request.proxy_bypass(parts.netloc) else proxy


def proxy_resolves(proxy: str) -> bool:
    """Whether a proxy resolves the names it is asked for. Every kind does except SOCKS4 and SOCKS5, for which curl resolves the names."""
    kind = proxy.lower()
    return bool(proxy) and (not kind.startswith("socks") or kind.startswith(("socks5h", "socks4a")))


def address_is_private(url: str) -> bool:
    """Whether the name in url resolves to an address that is not public.

    Behind a proxy with no outside DNS, a name may resolve only at the
    proxy. For such a name this answers False, as the federation build
    does, and the proxy must refuse a private address itself.
    """
    host = urllib.parse.urlsplit(url).hostname or ""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as e:
        if proxy_for(url):
            return False
        raise FetchFailed(f"{host} does not resolve ({e})") from e
    return any(ip_is_private(info[4][0]) for info in infos)


def ip_is_private(address: str) -> bool:
    """Whether an address is anything but a public one.

    is_private leaves out the shared address space, 100.64.0.0/10, which
    carrier NAT, a Tailscale network and Alibaba Cloud's metadata service
    (100.100.100.200) use. So an address that is not global is refused too.
    """
    addr = ipaddress.ip_address(address.split("%", 1)[0])
    return (addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved or addr.is_multicast
            or addr.is_unspecified or not addr.is_global)


def connect_public(address, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None):
    """Open a connection as socket.create_connection does, to an address that was checked.

    http_get checks the host before the request, and the connection resolves
    the name again. A name whose answer changes between the two (DNS
    rebinding) would pass the first and reach the second, so the name is
    resolved once, here, and the socket connects to the address that was
    checked.
    """
    host, port = address
    infos = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)
    for *_, sockaddr in infos:
        if ip_is_private(sockaddr[0]):
            raise Refused(f"{host} resolves to {sockaddr[0]}, a private or link-local address; allow_private_addresses: true permits them")
    last: OSError | None = None
    for family, kind, proto, _, sockaddr in infos:
        sock = socket.socket(family, kind, proto)
        try:
            if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
                sock.settimeout(timeout)
            if source_address:
                sock.bind(source_address)
            sock.connect(sockaddr)
            return sock
        except OSError as e:
            sock.close()
            last = e
    raise last or OSError(f"{host} resolves to no address")


class PublicHTTPConnection(http.client.HTTPConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._create_connection = connect_public


class PublicHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._create_connection = connect_public


# Through a proxy the connection is to the proxy, which resolves the
# source's name itself, so only the check before the request applies.
class PublicHTTPHandler(urllib.request.HTTPHandler):
    def http_open(self, req):
        return self.do_open(http.client.HTTPConnection if req.has_proxy() else PublicHTTPConnection, req)


class PublicHTTPSHandler(urllib.request.HTTPSHandler):
    def https_open(self, req):
        proxied = req.has_proxy() or req._tunnel_host
        return self.do_open(http.client.HTTPSConnection if proxied else PublicHTTPSConnection, req, context=self._context)


def origin(url: str) -> tuple[str, str, int]:
    """The scheme, host and port of an address, which a credential is scoped to, as curl scopes one."""
    parts = urllib.parse.urlsplit(url)
    return parts.scheme, parts.hostname or "", parts.port or (443 if parts.scheme == "https" else 80)


class Redirects(urllib.request.HTTPRedirectHandler):
    """Follows at most five redirects, checks each target as the first address was checked, and drops the credential on a change of host, port or scheme."""

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
        if not self.allow_private and address_is_private(newurl):
            raise FetchFailed(f"redirected to a private address: {new.hostname}")
        nxt = super().redirect_request(req, fp, code, msg, headers, newurl)
        # Another origin gets only the headers any address may see. The
        # credential is a header of whatever name the manifest gives, and a
        # conditional header describes the first address's copy.
        if nxt is not None and origin(newurl) != origin(req.full_url):
            for name in list(nxt.headers):
                if name.lower() not in ("user-agent", "accept"):
                    nxt.remove_header(name)
        return nxt


@dataclass
class Response:
    status: int
    headers: dict
    data: bytes


def capped(seconds: float, until: float) -> float:
    """A wait of up to seconds, cut to the time left before until, a time.monotonic() or 0 for no limit, and never under a second."""
    return seconds if not until else max(1.0, min(seconds, until - time.monotonic()))


def http_get(url: str, headers: dict, allow_private: bool, max_bytes: int, timeout: int = TIMEOUT, accept_304: bool = False,
             until: float = 0.0) -> Response:
    """GET with retries on 429, 5xx and a broken connection, a size cap read as it streams, and the address checks. 404 and 410 raise Gone.

    until is when the run's time limit passes, as a time.monotonic(), or 0
    for none. Each wait is cut to it, and once it passes OutOfTime is raised.
    """
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.netloc or "@" in parts.netloc:
        raise Refused(f"{url} is not a plain http(s) address")
    if not allow_private and address_is_private(url):
        raise Refused(f"{parts.hostname} is a private or link-local address; allow_private_addresses: true permits them")
    redirects = Redirects(allow_private)
    opener = urllib.request.build_opener(redirects, *(() if allow_private else (PublicHTTPHandler(), PublicHTTPSHandler())))
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **headers})
    last = ""
    for attempt in range(ATTEMPTS):
        if until and time.monotonic() >= until:
            raise OutOfTime()
        redirects.hops = 0
        delay = 2 ** attempt
        try:
            with opener.open(req, timeout=capped(timeout, until)) as resp:  # noqa: S310 - an address the manifest names
                deadline = time.monotonic() + timeout * BODY_TIMEOUTS
                data = bytearray()
                while len(data) <= max_bytes:
                    chunk = resp.read1(max_bytes + 1 - len(data))
                    if not chunk:
                        break
                    data += chunk
                    if until and time.monotonic() > until:
                        raise OutOfTime()
                    if time.monotonic() > deadline:
                        raise FetchFailed(f"the body took more than {timeout * BODY_TIMEOUTS} seconds")
                if len(data) > max_bytes:
                    raise Refused(f"over max_item_bytes ({max_bytes})")
                return Response(resp.status, {k.lower(): v for k, v in resp.headers.items()}, bytes(data))
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
            # An error about a header quotes the header's value, which may be the credential.
            why = "a header holds a character HTTP does not allow" if "header" in str(e).lower() else str(e)
            raise FetchFailed(f"{url} is not an address this script can fetch ({why})") from e
        except (OSError, http.client.HTTPException) as e:  # a timeout, TLS, a reset, a broken or truncated response
            last = f"{parts.netloc}: {getattr(e, 'reason', e)}"
        # A wait the time limit cuts short is the limit's, not the source's.
        if until and time.monotonic() + (delay if attempt < ATTEMPTS - 1 else 0) >= until:
            raise OutOfTime()
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
# Not <head>: HTML lets a page leave out </head>, and the skip would then
# cover the body. A head holds no text a reader sees anyway: its title is
# read apart, and its scripts and styles are skipped here.
SKIPPED = {"script", "style", "ac:parameter", "ac:emoticon", "ac:placeholder", "template", "noscript", "ac:adf-attribute"}
INLINE = {"strong": "**", "b": "**", "em": "*", "i": "*", "s": "~~", "del": "~~", "strike": "~~", "code": "`", "kbd": "`"}
PANELS = {"info": "Info", "note": "Note", "warning": "Warning", "tip": "Tip", "panel": "Panel", "expand": "Expand", "excerpt": "Excerpt"}
CDATA = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.S)
# How deep lists and quotes nest in the Markdown. Each level indents every
# line below it again, so the Markdown of a page nested thousands deep would
# grow with the square of the page. A deeper list or quote stays at this depth.
DEPTH = 8


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
        self.flat = 0  # lists opened past DEPTH, whose items join the deepest list
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
        return "> " * min(self.quote, DEPTH)

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

    def href(self, url) -> str:
        """The address a link or an image keeps: made absolute against the page's, or "" for a scheme other than http, https and mailto, such as javascript: or data:.

        The scheme is read as a browser reads it: in any case, after the
        spaces and the characters no reader sees, which shown() removes from
        the mirror afterwards.
        """
        url = shown(url or "").strip()
        if not url or url.startswith("#"):
            return url
        try:
            full = urllib.parse.urljoin(self.base, url) if self.base else url
            scheme = urllib.parse.urlsplit(full).scheme.lower()
        except ValueError:  # a malformed address, such as an IPv6 bracket left open
            return ""
        return full if scheme in ("http", "https", "mailto", "") else ""

    # -- the parser's calls
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            if self.title_buf is None and not self.title:
                self.title_buf = []
            return
        if tag in SKIPPED:
            # Only a skipped tag's own end tag closes it, so a void tag inside
            # one, such as a page link in a macro parameter, never leaves the
            # rest of the page skipped.
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
            if len(self.lists) < DEPTH:
                self.lists.append([tag, 0, None])
            else:
                self.flat += 1
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
            src = self.href(a.get("src"))
            self.buf.append(f"![{alt}]({src})" if src else f"[image: {alt}]")
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
                self.image["url"] = self.href(a.get("ri:value"))
            elif self.link is not None:
                self.link["url"] = self.href(a.get("ri:value"))
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
            if self.flat:
                self.flat -= 1
            elif self.lists:
                self.end_item()
                lst = self.lists.pop()
                block = "\n".join(lst[3:]) if len(lst) > 3 else ""
                self.emit(block)
        elif tag == "li":
            self.flush()
            if self.lists:  # an end tag with no list open is the page's error
                self.end_item()
        elif tag == "blockquote":
            self.flush()
            self.quote = max(0, self.quote - 1)
        elif tag in ("td", "th") and self.cell is not None:
            self.cell.append(self.text())
            self.table[-1].append(" ".join(" ".join(self.cell).split()).replace("|", "\\|"))
            self.cell = None
        elif tag == "table" and self.table is not None:
            if self.cell is not None:  # a cell left open closes with its table
                self.handle_endtag("td")
            rows = [r for r in self.table if r]
            self.table = None
            if rows:
                # Only the header row is padded to the widest row: a renderer
                # fills a shorter row itself, and padding every row would let a
                # table grow with the square of its size.
                width = max(len(r) for r in rows)
                header = rows[0] + [""] * (width - len(rows[0]))
                lines = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in range(width)) + " |"]
                lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
                self.emit("\n".join(lines))
        elif tag == "a" and self.links:
            href, start = self.links.pop()
            text = "".join(self.buf[start:]).strip()
            del self.buf[start:]
            if href:
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
            text = " ".join((link["text"] or body or link["title"] or link["url"]).split())
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
        # A line break in HTML text is a space. Kept, it would start a line of
        # Markdown, and a line the source began with # or ``` would become a
        # heading or a fence. Only <br> breaks a line.
        self.buf.append(data.replace("\xa0", " ").replace("\n", " "))

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
    # One backtick more than the longest run in the text, found in one pass:
    # a search for each longer fence would take time in the square of the run.
    ticks = "`" * max(3, max((len(run) for run in re.findall(r"`+", text)), default=0) + 1)
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
        raise Refused("pypdf is not installed; run through uv, which installs it, or run uv add pypdf in .lokf/") from e
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
        return shown(text), one_line(title), "pdf-text/1"
    if how == "html-markdown":
        try:
            text, title = html_to_markdown(decode(data, charset, html_page=True), base)
        except Exception as e:  # noqa: BLE001 - a page the converter cannot read is refused alone, as a broken PDF is, not its whole entry
            raise Refused(f"the page could not be converted ({type(e).__name__})") from e
        return shown(text), one_line(title), "html-markdown/1"
    text = decode(data, charset).replace("\r\n", "\n")
    if "\x00" in text:
        raise Refused("the content is binary, not text")
    return shown(text).rstrip("\n") + "\n", "", "text/1"


# ---- the kinds -----------------------------------------------------------------


@dataclass
class Item:
    """One mirrored item, as the lock and the mirror header record it, or the reason it was refused, failed or skipped."""

    item: str
    origin: str
    title: str = ""
    version: str = ""
    last_modified: str = ""
    author: str = ""
    etag: str = ""
    last_modified_header: str = ""  # as served, for If-Modified-Since
    blob: str = ""
    text: str = ""
    converted_by: str = ""
    sha256: str = ""
    command_sha256: str = ""
    refused: str = ""
    failed: str = ""
    skipped: str = ""


class Context:
    def __init__(self, manifest: Manifest, environ: dict, timeout: int, root: Path | None = None, until: float = 0.0):
        self.manifest = manifest
        self.environ = environ
        self.timeout = timeout
        self.root = root
        self.until = until  # when the run's time limit passes, as a time.monotonic(), or 0 for none
        self.fresher: dict = {}  # (entry id, item id): the validators a server now gives for content that did not change
        self.left: dict = {}  # entry id: {item id: its record, or None}, for the items the time limit left for the next run

    def out_of_time(self) -> bool:
        return bool(self.until) and time.monotonic() >= self.until

    def leave(self, entry: Entry, item_id: str, was: dict | None) -> None:
        """An item the time limit left for the next run, with the record it keeps, if it has one."""
        self.left.setdefault(entry.id, {})[item_id] = was

    def headers(self, entry: Entry) -> dict:
        name, value = entry.auth.value(self.environ)
        return {name: value} if name else {}

    def get(self, url: str, entry: Entry, extra: dict | None = None, accept_304: bool = False) -> Response:
        headers = self.headers(entry)
        headers.update(extra or {})
        return http_get(url, headers, self.manifest.allow_private, entry.max_item_bytes, self.timeout, accept_304, self.until)


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
        resp = http_get(self.site + "/_edge/tenant_info", {}, self.ctx.manifest.allow_private, 10_000, self.ctx.timeout, until=self.ctx.until)
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
        """The selector's pages, with the title, version and author the site gives, each title and name as one line a reader sees whole.

        A page of results may hold none and still name a next one, so a
        listing still going after a page for every result max_items allows
        is cut off, and an answer that always names a next page cannot keep
        the run.
        """
        items, start, limit = [], 0, 50
        query = {"cql": self.cql(), "expand": "version", "limit": limit, "start": start}
        for _ in range(self.entry.max_items + 2):
            page = self.api("/rest/api/content/search", query)
            results = page.get("results") or []
            for r in results:
                v = r.get("version") or {}
                by = v.get("by") or {}
                items.append({
                    "id": str(r.get("id", "")), "title": one_line(str(r.get("title", ""))),
                    "version": one_line(str(v.get("number", ""))), "when": utc(str(v.get("when", "") or v.get("createdAt", ""))),
                    "author": one_line(str(by.get("accountId") or by.get("username") or by.get("userKey") or v.get("authorId") or "")),
                    "webui": one_line(str((r.get("_links") or {}).get("webui", ""))),
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
        raise FetchFailed(f"the listing did not end within {self.entry.max_items + 2} pages")

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


def run_confluence(ctx: Context, entry: Entry, prior: dict) -> tuple[list[Item], dict]:
    """The items to keep or write, by id, and the records of the items left untouched because unchanged. One page's failure is that page's."""
    c = Confluence(ctx, entry)
    listed = c.listing()
    if len(listed) > entry.max_items:
        raise Refused(f"the selector returns more than max_items ({entry.max_items}); narrow it or raise the cap")
    items, unchanged = [], {}
    for r in listed:
        pid = r["id"]
        if not (pid.isascii() and pid.isdigit()):
            continue
        was = prior.get(pid)
        if was and was.get("status") == "ok" and was.get("version") == r["version"] and r["version"]:
            unchanged[pid] = was
            continue
        if ctx.out_of_time():
            ctx.leave(entry, pid, was)
            continue
        origin = c.origin(r["webui"], pid)
        try:
            storage, _page = c.body(pid)
            text, title, _how = convert(storage.encode("utf-8"), "text/html", "html-markdown", base=origin)
        except OutOfTime:
            ctx.leave(entry, pid, was)
            continue
        except Gone:
            items.append(Item(item=pid, origin=origin, title=r["title"], version="gone"))
            continue
        except Refused as e:
            items.append(Item(item=pid, origin=origin, title=r["title"], refused=str(e)))
            continue
        except FetchFailed as e:
            items.append(Item(item=pid, origin=origin, title=r["title"], failed=str(e)))
            continue
        raw = storage.encode("utf-8")
        items.append(Item(
            item=pid, origin=origin, title=r["title"] or title, version=r["version"], last_modified=r["when"],
            author=r["author"] if entry.authors else "", text=text, converted_by="confluence-storage-markdown/1",
            sha256=sha256_hex(raw),
        ))
    return items, unchanged


def run_http(ctx: Context, entry: Entry, prior: dict) -> tuple[list[Item], dict]:
    items, unchanged = [], {}
    for url in entry.urls:
        name = slug(PurePosixPath(urllib.parse.urlsplit(url).path).stem or urllib.parse.urlsplit(url).hostname or "page")
        item_id = f"{name}-{sha256_hex(url.encode())[:8]}"
        was = prior.get(item_id) or {}
        if ctx.out_of_time():
            ctx.leave(entry, item_id, was or None)
            continue
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
                # A server may give new validators for the same bytes, after
                # a deploy or on every answer. The run that next changes the
                # lock records them, so they change no line of a lock that
                # would not change anyway.
                fresh = {"etag": resp.headers.get("etag", ""), "last_modified_header": resp.headers.get("last-modified", "")}
                if any(fresh[k] != was.get(k, "") for k in fresh):
                    ctx.fresher[(entry.id, item_id)] = fresh
                unchanged[item_id] = was
                continue
            text, title, how = convert(resp.data, content_type_of(resp.headers), entry.convert, charset_of(resp.headers), base=url)
        except OutOfTime:
            ctx.leave(entry, item_id, was or None)
            continue
        except Gone:
            items.append(Item(item=item_id, origin=url, title=was.get("title", ""), version="gone"))
            continue
        except Refused as e:
            items.append(Item(item=item_id, origin=url, title=was.get("title", ""), refused=str(e)))
            continue
        except FetchFailed as e:
            items.append(Item(item=item_id, origin=url, title=was.get("title", ""), failed=str(e)))
            continue
        etag = resp.headers.get("etag", "")
        lm = resp.headers.get("last-modified", "")
        # The version is for reading, so it drops a weak ETag's W/ prefix and
        # the quotes. The lock keeps the ETag as served, for If-None-Match.
        version = one_line(re.sub(r"^W/", "", etag).strip('"')) if etag else (utc(lm) if lm else digest[:12])
        items.append(Item(item=item_id, origin=url, title=title or name, version=version, last_modified=utc(lm) if lm else "",
                          etag=etag, last_modified_header=lm, text=text, converted_by=how, sha256=digest))
    return items, unchanged


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


@functools.lru_cache(maxsize=None)
def git_version() -> tuple[int, int]:
    """The major and minor version of the git on PATH, read once a run, or (0, 0) when it cannot be read."""
    try:
        out = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.TimeoutExpired):
        return (0, 0)
    found = re.search(r"(\d+)\.(\d+)", out)
    return (int(found[1]), int(found[2])) if found else (0, 0)


def shown_version(version: tuple[int, int]) -> str:
    return f"{version[0]}.{version[1]}" if version != (0, 0) else "of a version this script cannot read"


def ip_literal(host: str) -> bool:
    """Whether a URL's host is an address, which git connects to without resolving it."""
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return False
    return True


def pin_needed(url: str, allow_private: bool) -> bool:
    """Whether git must be held to the addresses checked here: an http(s) address where the manifest refuses private ones."""
    return git_url_kind(url) in ("https", "http") and not allow_private


def git_pin(url: str) -> list[tuple[str, str]]:
    """The configuration that holds git to the addresses checked here: no redirect, the proxy, and the name resolved once.

    Git resolves the name again when it connects, so a name that answers a
    public address to the check and a private one to git (DNS rebinding)
    would pass. http.curloptResolve, which git reads from 2.37 and an older
    git ignores, hands git the addresses that were checked. A redirect would
    send git to a name it resolves itself, so none is followed.

    Git uses the proxy proxy_for chose, or none, whatever its own
    configuration says, and git_env removes no_proxy, which curl would read
    to choose again. So the check and the fetch agree on the route. Through
    a proxy that resolves names, curl does not resolve the name, so a pin
    would change nothing and git gets none. A name that resolves only at
    such a proxy is sent to it unchecked.
    """
    parts = urllib.parse.urlsplit(url)
    host, port = parts.hostname or "", parts.port or (443 if parts.scheme == "https" else 80)
    if not host.isascii():
        raise Refused(f"{host}: write the host name in ASCII, its xn-- form, so git can be held to the address that was checked")
    proxy = proxy_for(url, git=True)
    config = [(f"http.{url}.followRedirects", "false"), (f"http.{url}.proxy", proxy)]
    try:
        infos = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)
    except socket.gaierror as e:
        if proxy_resolves(proxy):
            return config
        raise FetchFailed(f"{host} does not resolve ({e})") from e
    addresses = list(dict.fromkeys(info[4][0] for info in infos))
    for address in addresses:
        if ip_is_private(address):
            raise Refused(f"{host} resolves to {address}, a private or link-local address; allow_private_addresses: true permits it")
    if ip_literal(host) or proxy_resolves(proxy):
        return config  # git does not resolve an address, nor a name the proxy resolves
    found = git_version()
    if found < (2, 37):
        raise FetchFailed(f"git 2.37 or later is needed to hold the fetch to the address that was checked, and this git is {shown_version(found)}")
    pinned = ",".join(f"[{address}]" if ":" in address else address for address in addresses)
    return config + [(f"http.{url}.curloptResolve", f"{host}:{port}:{pinned}")]


def git_env(entry: Entry, ctx: Context, home: Path, pinned: list | tuple = ()) -> dict:
    """A clean environment for git: the protocols the manifest allows, the route git_pin checked, and the credential as configuration scoped to the entry's address, so it is never on the command line and never sent to another host."""
    # The identity is for the reflog of the fetched ref: without one, git looks
    # the user up, which on a machine with a slow name service waits seconds.
    #
    # HOME is a folder of the run's own: curl sends the credential of a
    # ~/.netrc default entry to any host, and git 2.31, which predates
    # GIT_CONFIG_GLOBAL and GIT_CONFIG_SYSTEM, reads ~/.gitconfig. With
    # GIT_CONFIG_NOSYSTEM, no version of git reads /etc/gitconfig.
    env = passed_through({"PATH": os.environ.get("PATH", ""), "HOME": str(home), "GIT_TERMINAL_PROMPT": "0",
                          "GIT_CONFIG_GLOBAL": os.environ.get("GIT_CONFIG_GLOBAL", "/dev/null"), "GIT_CONFIG_NOSYSTEM": "1",
                          "GIT_AUTHOR_NAME": "knowledge-ingest", "GIT_AUTHOR_EMAIL": "knowledge-ingest@localhost",
                          "GIT_COMMITTER_NAME": "knowledge-ingest", "GIT_COMMITTER_EMAIL": "knowledge-ingest@localhost",
                          "LC_ALL": "C.UTF-8", "TMPDIR": os.environ.get("TMPDIR", tempfile.gettempdir())})
    if pinned:
        # git_pin named the proxy, or none, and no_proxy would let curl choose again.
        env.pop("no_proxy", None)
        env.pop("NO_PROXY", None)
    config = [("credential.helper", ""), ("protocol.allow", "never"), ("protocol.https.allow", "always")]
    if ctx.manifest.allow_private:
        config += [("protocol.http.allow", "always"), ("protocol.file.allow", "always")]
    config += pinned
    if entry.auth.scheme and git_url_kind(entry.url) in ("https", "http"):
        name, value = entry.auth.value(ctx.environ)
        # On a redirect to another host, curl drops an Authorization header
        # and keeps a header of any other name, so with a credential git
        # follows no redirect, as where git_pin holds it.
        config += [(f"http.{entry.url}.followRedirects", "false"), (f"http.{entry.url}.extraHeader", f"{name}: {value}")]
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


def run_git(ctx: Context, entry: Entry, prior: dict) -> tuple[list[Item], dict]:
    """The ref's commit and its trees, then each chosen file that changed, by its blob id, which the lock records so an unchanged file is never downloaded."""
    if not shutil.which("git"):
        raise FetchFailed("git is not installed")
    # git_env sets git's protocol limits and the credential through
    # GIT_CONFIG_COUNT, which a git older than 2.31 ignores silently.
    found = git_version()
    if found < (2, 31):
        raise FetchFailed(f"git 2.31 or later is needed to read the protocol limits and the credential the ingest sets, "
                          f"and this git is {shown_version(found)}")
    pinned = git_pin(entry.url) if pin_needed(entry.url, ctx.manifest.allow_private) else []
    tmp = Path(tempfile.mkdtemp(prefix="ingest-git-"))
    try:
        env = git_env(entry, ctx, tmp, pinned)  # the fetch's folder is HOME too: it holds no .netrc or .gitconfig
        # Git reads a relative path against the folder it runs in, the fetch's
        # own, so a path the manifest writes that way is read against the root.
        url = str((ctx.root / entry.url).resolve()) if ctx.root and entry.url.startswith(("./", "../")) else entry.url
        try:
            return mirror_git(ctx, entry, prior, env, tmp / "partial", url, partial=True)
        except FilesRefused:
            # The server took the filter and then refused the files by their
            # ids, as one that speaks only git's first protocol does. The
            # ref is fetched again whole, into a folder of its own, since
            # git fetches nothing for a commit it already holds.
            return mirror_git(ctx, entry, prior, env, tmp / "whole", url, partial=False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


class FilesRefused(Exception):
    """The server sent a commit's trees and refused its files by their ids."""


def mirror_git(ctx: Context, entry: Entry, prior: dict, env: dict, repo: Path, url: str, partial: bool) -> tuple[list[Item], dict]:
    """The items of a git entry, fetched into repo: with partial, the commit's trees alone at first, and then only the files that changed."""
    repo.mkdir()

    def git(*args, data=False, stdin=None):
        try:
            done = subprocess.run(["git", "-C", str(repo), *args], env=env, input=stdin, capture_output=True, timeout=capped(600, ctx.until))
        except subprocess.TimeoutExpired as e:
            if ctx.out_of_time():
                raise OutOfTime() from e
            raise FetchFailed(f"git {args[0]} ran past 600 seconds") from e
        if done.returncode != 0:
            err = done.stderr.decode("utf-8", "replace").strip().splitlines()
            raise FetchFailed("git " + args[0] + " failed: " + (err[-1] if err else "no message"))
        return done.stdout if data else done.stdout.decode("utf-8", "replace")

    def start_of(oid: str) -> bytes:
        """The first 8000 bytes of a blob, which say whether it is binary, read without the rest of it."""
        with subprocess.Popen(["git", "-C", str(repo), "cat-file", "blob", oid], env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as p:
            start = p.stdout.read(8000)
            p.kill()
        return start

    git("init", "-q")
    # A fetch of files by their ids must name no commit the repository
    # holds. A commit it named would tell the server that the commit's files
    # are here too, and the server would send none.
    git("config", "fetch.negotiationAlgorithm", "noop")
    git("remote", "add", "origin", url)
    # Git rewrites an address by any url.<base>.insteadOf it reads, the
    # global configuration's included, and fetches the rewritten one. The
    # pin and the credential are scoped to the address as the manifest
    # writes it, so git would fetch a rewritten address with neither, and
    # resolve its name itself. ls-remote --get-url applies the rewrite
    # without connecting.
    fetched = git("ls-remote", "--get-url", "origin").strip()
    if fetched != url:
        raise Refused(f"git's configuration rewrites {url} to {fetched} (url.<base>.insteadOf), which the address check and the "
                      "credential do not cover; name the address git fetches in the manifest, or remove the rewrite")
    # With the filter the server sends the commit and its trees, and no file
    # until one is asked for. A server that knows no filter sends them all.
    git("fetch", "-q", "--depth", "1", *(["--filter=blob:none"] if partial else []), "origin", entry.ref)
    sha = git("rev-parse", "FETCH_HEAD").strip()
    when = utc(git("log", "-1", "--format=%cI", "FETCH_HEAD").strip())
    spec = ["FETCH_HEAD"] + (["--", entry.path] if entry.path else [])
    blobs = {}
    # ls-tree runs without -l, which would download every file to give its size.
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
    # A file that is not Markdown is mirrored as its name with .md added,
    # which a Markdown file or a folder beside it may already have. That
    # one keeps the name: two files would take turns in it from run to
    # run, and a file and a folder cannot share it.
    markdown = {rel for _, rel, _ in chosen if rel.endswith(".md")}
    folders = {str(p) for _, rel, _ in chosen for p in PurePosixPath(rel).parents}
    too_big = f"over max_item_bytes ({entry.max_item_bytes})"
    items, unchanged, wanted = [], {}, []
    for f, rel, oid in chosen:
        if ".." in PurePosixPath(rel).parts or rel.startswith("/"):
            continue
        item_id = md_name(rel)
        if item_id != rel and (item_id in markdown or item_id in folders):
            beside = "Markdown file" if item_id in markdown else "folder"
            items.append(Item(item=rel, origin=git_origin(entry, sha, f), title=rel, skipped=f"the mirror would give it the name of the {beside} beside it"))
            continue
        was = prior.get(item_id)
        # A binary file, and one refused for its size, is not downloaded again
        # while it, and the cap, stay the same.
        if was and was.get("blob") == oid and (was.get("status") in ("ok", "skipped") or (was.get("status") == "refused" and was.get("reason") == too_big)):
            unchanged[item_id] = was
            continue
        wanted.append((f, rel, oid, item_id, was))
    # The files that changed, a batch at a time, so a run stopped at its
    # time limit keeps the batches it read.
    for start in range(0, len(wanted), GIT_BATCH):
        batch = wanted[start:start + GIT_BATCH]
        try:
            if ctx.out_of_time():
                raise OutOfTime()
            if partial:
                try:
                    git("fetch", "-q", "--no-tags", "--no-write-fetch-head", "--recurse-submodules=no", "--filter=blob:none", "--stdin", "origin",
                        stdin="".join(oid + "\n" for _, _, oid, _, _ in batch).encode())
                except FetchFailed as e:
                    raise FilesRefused() from e
        except OutOfTime:
            for _, _, _, item_id, was in wanted[start:]:
                ctx.leave(entry, item_id, was)
            break
        sizes = {}
        for line in git("cat-file", "--batch-check=%(objectname) %(objectsize)", stdin="".join(oid + "\n" for _, _, oid, _, _ in batch).encode()).splitlines():
            oid, _, size = line.partition(" ")
            if size.isdigit():
                sizes[oid] = int(size)
        for f, rel, oid, item_id, was in batch:
            size = sizes.get(oid, 0)
            # Of a file over the cap only the start is read: enough to tell a
            # binary file, which is skipped, from text, which is refused.
            data = git("cat-file", "blob", oid, data=True) if size <= entry.max_item_bytes else start_of(oid)
            if b"\x00" in data[:8000]:
                items.append(Item(item=item_id, origin=git_origin(entry, sha, f), title=rel, blob=oid, skipped="a binary file"))
                continue
            if size > entry.max_item_bytes:
                items.append(Item(item=item_id, origin=git_origin(entry, sha, f), version=sha, title=rel, blob=oid, refused=too_big))
                continue
            digest = sha256_hex(data)
            if was and was.get("status") == "ok" and was.get("sha256") == "sha256:" + digest:
                unchanged[item_id] = dict(was, blob=oid)
                continue
            text = shown(decode(data).replace("\r\n", "\n")).rstrip("\n") + "\n"
            if not rel.endswith(".md"):
                text = fence(text, PurePosixPath(rel).suffix.lstrip(".")) + "\n"
            items.append(Item(item=item_id, origin=git_origin(entry, sha, f), title=rel, version=sha, last_modified=when,
                              blob=oid, text=text, converted_by="git/1", sha256=digest))
    return items, unchanged


def run_command(ctx: Context, entry: Entry, prior: dict, root: Path) -> tuple[list[Item], dict]:
    path = root / entry.command
    if not path.is_file():
        raise Refused(f"{entry.command} is not a file under the repository root")
    if shutil.which("git") and subprocess.run(["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"], capture_output=True).returncode == 0:
        tracked = subprocess.run(["git", "-C", str(root), "ls-files", "--error-unmatch", "--", entry.command], capture_output=True)
        if tracked.returncode != 0:
            raise Refused(f"{entry.command} is not tracked by git; a command runs only once it is committed")
        edited = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--", entry.command], capture_output=True, text=True)
        if edited.stdout.strip():
            raise Refused(f"{entry.command} has changes git has not committed; a command runs only as committed")
    command_digest = sha256_hex(path.read_bytes())
    env = passed_through({"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "/"), "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
                          "TMPDIR": os.environ.get("TMPDIR", tempfile.gettempdir()), "KNOWLEDGE_INGEST_ENTRY": entry.id})
    for name in entry.auth.names():
        if name in ctx.environ:
            env[name] = ctx.environ[name]
    if ctx.out_of_time():
        raise OutOfTime()
    # The command leads a process group of its own, so its timeout stops
    # every process it started. Stopped alone, it would leave one it started
    # in the background running, and holding its output open.
    group = hasattr(os, "killpg")
    try:
        with subprocess.Popen([str(path), *entry.args], cwd=str(root), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              start_new_session=group) as proc:
            try:
                out, err = proc.communicate(timeout=capped(entry.timeout, ctx.until))
            except subprocess.TimeoutExpired as e:
                if group:
                    with contextlib.suppress(OSError):
                        os.killpg(proc.pid, signal.SIGKILL)
                proc.kill()
                if ctx.out_of_time():
                    raise OutOfTime() from e
                raise FetchFailed(f"the command ran past its timeout ({entry.timeout}s)") from e
    except OSError as e:
        raise FetchFailed(f"the command could not be run ({e.strerror})") from e
    if proc.returncode != 0:
        lines = err.decode("utf-8", "replace").strip().splitlines()
        raise FetchFailed(f"the command exited {proc.returncode}: {lines[-1][:200] if lines else 'no message'}")
    data = out
    if len(data) > entry.max_item_bytes:
        raise Refused(f"the output is over max_item_bytes ({entry.max_item_bytes})")
    digest = sha256_hex(data)
    was = prior.get(entry.id)
    if was and was.get("status") == "ok" and was.get("sha256") == "sha256:" + digest and was.get("command_sha256") == command_digest:
        return [], {entry.id: was}
    text, title, how = convert(data, "text/plain", entry.convert or "text")
    return [Item(item=entry.id, origin=f"command:{entry.command}", title=title or entry.command, version=digest[:12],
                 text=text, converted_by=how, sha256=digest, command_sha256=command_digest)], {}


# ---- the run -------------------------------------------------------------------


def repository_visibility(root: Path, given: str) -> str:
    if given:
        return given
    env = os.environ.get("KNOWLEDGE_INGEST_VISIBILITY", "")
    if env:
        return env
    if shutil.which("gh"):
        try:
            done = subprocess.run(["gh", "repo", "view", "--json", "visibility", "--jq", ".visibility"], cwd=str(root), capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:  # gh waits on the network behind a proxy it cannot pass
            return "unknown"
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
    """Empty when git would commit nothing a confidential entry writes, its copies and their records, else the reason the entry is refused. A root outside git commits nothing."""
    if not shutil.which("git") or subprocess.run(["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"], capture_output=True).returncode != 0:
        return ""
    # check-ignore reads the ignore rules for a path that need not exist. It
    # exits 1 when no rule ignores the path, and 128 when it cannot tell, and
    # either refuses the entry.
    for path, what in ((CACHE + "/probe", f"{CACHE}/, where a confidential copy goes"), (CACHE_LOCK, f"{CACHE_LOCK}, where a confidential copy's record goes")):
        if subprocess.run(["git", "-C", str(root), "check-ignore", "-q", "--no-index", path], capture_output=True).returncode != 0:
            return f"git does not ignore {what}; add .cache/ to .lokf/.gitignore, as the sidecar's template does"
    if subprocess.run(["git", "-C", str(root), "ls-files", "--", CACHE + "/", CACHE_LOCK], capture_output=True, text=True).stdout.strip():
        return f"git tracks files under {CACHE}/ or {CACHE_LOCK}; remove them with git rm --cached before a confidential entry runs"
    return ""


def mirror_header(entry: Entry, record: dict, converted_by: str) -> str:
    """The header a mirror file opens with, from the item's lock record."""
    fm = {"origin": record.get("origin", ""), "title": record.get("title", ""), "ingest": entry.id, "kind": entry.kind,
          "version": str(record.get("version", "")), "sha256": record["sha256"], "retrieved_at": record["retrieved_at"], "converted_by": converted_by}
    for key in ("last_modified", "author"):
        if record.get(key):
            fm[key] = record[key]
    if entry.license:
        fm["license"] = entry.license
    order = ["origin", "title", "ingest", "kind", "version", "last_modified", "author", "sha256", "retrieved_at", "converted_by", "license"]
    lines = ["---"]
    for key in order:
        if key in fm:
            lines.append(yaml.dump({key: fm[key]}, Dumper=Dumper, allow_unicode=True, width=10_000, default_flow_style=False).rstrip("\n"))
    lines.append("---")
    lines.append(f"<!-- A mirror of {fm['origin']}, kept by the ingest. Edit the source, not this file: the next run writes it again. -->")
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


COUNTS = ("fetched", "restored", "unchanged", "gone", "unlisted", "failed", "refused", "skipped", "not reached")
# What each kind compares, beside the digest, to keep an item's record as it is.
KEPT_BY = {"confluence": ("version",), "http": (), "git": (), "command": ("command_sha256",)}


def refresh(record: dict, fresh: dict) -> None:
    """Put a server's new validators in an item's record, and drop one the server no longer gives."""
    for key, value in fresh.items():
        if value:
            record[key] = value
        else:
            record.pop(key, None)


class Run:
    def __init__(self, args, root: Path, manifest: Manifest, lock: dict, visibility: str, environ: dict, cache_lock: dict | None = None):
        self.args, self.root, self.manifest, self.lock, self.visibility = args, root, manifest, lock, visibility
        self.cache_lock = cache_lock if cache_lock is not None else {"ingest_lock_version": LOCK_VERSION, "entries": {}}
        self.now = now_utc(args.now)
        self.ctx = Context(manifest, environ, args.timeout, root, time.monotonic() + args.time_limit * 60 if args.time_limit else 0.0)
        self.summary: list[str] = []
        self.failed = 0
        self.writes: list[tuple[Path, str]] = []
        self.removals: list[Path] = []
        self.exposed: str | None = None
        self.settled: set = set()  # the confidential entries that ran to an end, whose committed line this run writes

    def mirror_root(self, entry: Entry) -> Path:
        if entry.sensitivity == "confidential":
            return self.root / CACHE
        return self.root / self.manifest.mirror

    def book(self, entry: Entry) -> dict:
        """The lock that holds an entry's item records: the cache's for a confidential entry, unless it sets lock_details, else the committed one."""
        return self.cache_lock if entry.local_lock else self.lock

    def records(self, entry: Entry) -> dict:
        """An entry's item records, from both locks, with those of the lock that holds them first. An entry that has not run since its
        sensitivity or lock_details changed keeps some in the other lock, and its files where they were."""
        other = self.cache_lock if self.book(entry) is self.lock else self.lock
        merged = dict((other["entries"].get(entry.id) or {}).get("items") or {})
        merged.update((self.book(entry)["entries"].get(entry.id) or {}).get("items") or {})
        return merged

    def cache_exposed(self) -> str:
        """cache_exposed's answer for this root, asked once a run."""
        if self.exposed is None:
            self.exposed = cache_exposed(self.root)
        return self.exposed

    def rel(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()

    def within(self, path: str, folder: Path) -> bool:
        """Whether a path the lock records lies in the folder, with each symbolic link on the way followed."""
        try:
            (self.root / path).resolve().relative_to(folder)
        except ValueError:
            return False
        return True

    def removable(self, path: str) -> bool:
        """Whether the run may remove a file the lock names: only one inside either mirror, whatever else the lock says."""
        return any(self.within(path, mirror) for mirror in (self.root / self.manifest.mirror, self.root / CACHE))

    def entry_mirror_size(self, prior: dict) -> int:
        return sum(int(v.get("bytes", 0) or 0) for v in prior.values() if v.get("status") == "ok")

    def total_mirror_size(self) -> int:
        """The mirror's bytes, the cache's included, over the entries the manifest names: one that left it is removed by this run, so it frees its bytes now."""
        return sum(self.entry_mirror_size(self.records(e)) for e in self.manifest.entries)

    def run_entry(self, entry: Entry) -> None:
        book = self.book(entry)
        other = self.cache_lock if book is self.lock else self.lock
        shown = discreet if entry.local_lock else str
        counts = dict.fromkeys(COUNTS, 0)
        why = allowed_here(entry.sensitivity, self.visibility)
        if not why and entry.sensitivity == "confidential":
            why = self.cache_exposed()
        if why:
            # An entry refused before any fetch keeps its records where they
            # are, and the committed lock says why.
            book["entries"].setdefault(entry.id, {"status": "ok", "items": {}}).update({"status": "refused", "reason": why})
            if book is self.cache_lock:
                self.lock["entries"].setdefault(entry.id, {}).update({"status": "refused", "reason": discreet(why)})
            self.failed += 1
            self.summary.append(f"- {entry.id} ({entry.describe()}): refused, {shown(why)}")
            return
        # The other lock may hold the entry's records from before: from a run
        # with lock_details set the other way, or from before the entry was
        # made confidential or stopped being so. They join this lock's once the
        # entry has run. Nothing changes before then, so an entry the time
        # limit stops keeps both locks and its files as they were.
        prior = self.records(entry)
        folder = self.mirror_root(entry) / entry.id
        # The sensitivity picks the folder, so after a change the entry's files
        # are in the other mirror. Each is removed there and its record
        # dropped, and a current one is fetched again into this folder. So an
        # entry made confidential leaves the committed mirror.
        moved = [i for i, was in prior.items() if was.get("path") and not self.within(str(was["path"]), folder)]
        elsewhere = [self.root / str(prior[i]["path"]) for i in moved if self.removable(str(prior[i]["path"]))]
        for i in moved:
            del prior[i]
        # A file the lock calls current and the disk has lost is handed to the
        # kind as if new, so it is fetched again instead of skipped as unchanged.
        lost = {i for i, was in prior.items() if was.get("status") == "ok" and was.get("path") and not (self.root / was["path"]).is_file()}
        present = {i: was for i, was in prior.items() if i not in lost}
        failure = None
        try:
            if entry.kind == "confluence":
                items, unchanged = run_confluence(self.ctx, entry, present)
            elif entry.kind == "http":
                items, unchanged = run_http(self.ctx, entry, present)
            elif entry.kind == "git":
                items, unchanged = run_git(self.ctx, entry, present)
            else:
                items, unchanged = run_command(self.ctx, entry, present, self.root)
        except OutOfTime:
            self.summary.append(f"- {entry.id} ({entry.describe()}): stopped, the run's time limit passed while it ran, so its records wait "
                                "for the next run as they were")
            return
        except Refused as e:
            failure = ("refused", str(e))
        except (FetchFailed, Gone) as e:
            failure = ("failed", str(e))
        except Exception as e:  # noqa: BLE001 - a surprise in one entry is recorded there, and the run goes on
            failure = ("failed", f"an error this script did not expect, {type(e).__name__}: {' '.join(str(e).split())[:200]}")
        record = book["entries"].setdefault(entry.id, {"status": "ok", "items": {}})
        other["entries"].pop(entry.id, None)
        self.removals += elsewhere
        if book is self.cache_lock:
            self.settled.add(entry.id)
        if moved:
            n = len(moved)
            self.summary.append(f"- {entry.id}: its sensitivity puts its files in {self.rel(folder)}/, so {n} file{'s' if n != 1 else ''} "
                                f"elsewhere {'are' if n != 1 else 'is'} removed")
        if failure:
            status, reason = failure
            record.update({"status": status, "reason": reason, "items": prior})
            self.failed += 1
            self.summary.append(f"- {entry.id} ({entry.describe()}): {status}, {shown(reason)}")
            return
        record["status"] = "ok"
        record.pop("reason", None)
        new_items: dict = {}
        skipped: list[tuple[str, str]] = []
        total = self.total_mirror_size() - self.entry_mirror_size(self.records(entry))
        for item_id, was in unchanged.items():
            fresh = self.ctx.fresher.get((entry.id, item_id))
            if fresh and book is self.cache_lock:
                refresh(was, fresh)  # a lock git never sees takes them at once
            new_items[item_id] = was
            status = str(was.get("status", "ok"))
            counts[status if status in ("refused", "skipped") else "unchanged"] += 1
            total += int(was.get("bytes", 0) or 0) if status == "ok" else 0
        # An item the time limit left keeps the record it had, one whose file
        # was lost included, and one it never had waits for the next run.
        for item_id, was in self.ctx.left.get(entry.id, {}).items():
            was = was or prior.get(item_id)
            if was:
                new_items[item_id] = was
                total += int(was.get("bytes", 0) or 0) if was.get("status") == "ok" else 0
            counts["not reached"] += 1
        for it in items:
            was = prior.get(it.item) or {}
            # A binary file, and one refused for its size, keeps the blob id it
            # was skipped or refused at, so it is not downloaded again while it
            # stays so. A file skipped for its name needs no record. A file
            # mirrored before that is binary now is unlisted, so its copy waits
            # for --prune, and for no concept to cite it, as any unlisted copy does.
            blob = {"blob": it.blob} if it.blob else {}
            if it.skipped and it.blob and was.get("path"):
                new_items[it.item] = dict(was, status="unlisted", since=self.away_since(was), reason=f"{it.skipped} now")
                counts["unlisted"] += 1
                continue
            if it.skipped:
                counts["skipped"] += 1
                if it.blob:
                    new_items[it.item] = {"status": "skipped", "reason": it.skipped, "origin": it.origin, "title": it.title, **blob}
                else:
                    skipped.append((it.item, it.skipped))
                continue
            if it.refused:
                new_items[it.item] = dict(was, status="refused", reason=it.refused, origin=it.origin, title=it.title, **blob)
                counts["refused"] += 1
                continue
            if it.failed:
                new_items[it.item] = dict(was, status="failed", reason=it.failed, origin=it.origin, title=it.title)
                counts["failed"] += 1
                continue
            if it.version == "gone":
                new_items[it.item] = dict(was, status="gone", origin=it.origin, since=self.away_since(was))
                counts["gone"] += 1
                continue
            # The folder is the resolved root and the names below it, so a path
            # that leaves it, by `..` or by a symbolic link the repository
            # holds, such as the entry's folder linked elsewhere, is refused.
            # A name the workflow would not publish is spelled plain.
            target = (folder / publishable(md_name(it.item))).resolve()
            try:
                target.relative_to(folder)
            except ValueError:
                new_items[it.item] = dict(was, status="refused", reason="a path outside the entry's folder", origin=it.origin)
                counts["refused"] += 1
                continue
            if target.suffix != ".md" or "\n" in it.item or any(unicodedata.category(c) in ("Cc", "Cf") for c in it.item):
                new_items[it.item] = dict(was, status="refused", reason="a name this script does not write", origin=it.origin)
                counts["refused"] += 1
                continue
            # The caps count the Markdown the mirror holds, which can outgrow the
            # body fetched: links made absolute, or a PDF's compressed text.
            written = len(it.text.encode("utf-8"))
            if written > entry.max_item_bytes:
                reason = f"the Markdown is over max_item_bytes ({entry.max_item_bytes})"
                new_items[it.item] = dict(was, status="refused", reason=reason, origin=it.origin)
                counts["refused"] += 1
                continue
            if total + written > self.manifest.max_total_bytes:
                reason = f"the mirror would pass max_total_bytes ({self.manifest.max_total_bytes})"
                new_items[it.item] = dict(was, status="refused", reason=reason, origin=it.origin)
                counts["refused"] += 1
                continue
            total += written
            # A copy restored with the bytes its record names keeps the record,
            # as an unchanged copy does. So a checkout without the confidential
            # cache, or a file deleted by hand, changes no line of the lock and
            # no byte of the file, even after a commit or a validator moved.
            same = (it.item in lost and was.get("status") == "ok" and was.get("sha256") == "sha256:" + it.sha256 and was.get("retrieved_at")
                    and all(str(was.get(key, "")) == str(getattr(it, key)) for key in KEPT_BY[entry.kind]))
            if same:
                lock_item = dict(was, path=self.rel(target), bytes=written)
            else:
                lock_item = {"path": self.rel(target), "origin": it.origin, "title": it.title, "version": str(it.version),
                             "sha256": "sha256:" + it.sha256, "bytes": written, "retrieved_at": self.now, "status": "ok"}
                for key in ("last_modified", "author", "etag", "blob", "last_modified_header", "command_sha256"):
                    if getattr(it, key):
                        lock_item[key] = getattr(it, key)
            new_items[it.item] = lock_item
            counts["restored" if it.item in lost else "fetched"] += 1
            self.writes.append((target, mirror_header(entry, lock_item, it.converted_by) + it.text))
        for item_id, was in prior.items():
            # A file no longer listed is unlisted, and one that was skipped needs its record no more.
            if item_id not in new_items and was.get("status") != "skipped":
                new_items[item_id] = dict(was, status="unlisted", since=self.away_since(was))
                counts["unlisted"] += 1
        record["items"] = new_items
        parts = [f"{v} {k}" for k, v in counts.items() if v]
        self.summary.append(f"- {entry.id} ({entry.describe()}): " + (", ".join(parts) if parts else "nothing listed"))
        if counts["not reached"]:
            n = counts["not reached"]
            self.summary.append(f"  - {n} item{'s' if n != 1 else ''}: not reached, the run's time limit passed first, so "
                                f"{'they wait' if n != 1 else 'it waits'} for the next run")
        problems = [(item_id, it) for item_id, it in sorted(new_items.items()) if it.get("status") in ("refused", "failed", "gone", "unlisted", "skipped")]
        if entry.local_lock:
            # The summary is the pull request's body, so a confidential
            # entry's lines count its items, name none, and cut each address
            # in a reason to its site.
            tally = Counter((str(it["status"]), discreet(str(it.get("reason") or ""))) for _, it in problems)
            tally.update(("skipped", reason) for _, reason in skipped)
            for (status, reason), n in sorted(tally.items()):
                self.summary.append(f"  - {n} item{'s' if n != 1 else ''}: {status}" + (f", {reason}" if reason else ""))
        else:
            for item_id, it in problems:
                reason = f", {it['reason']}" if it.get("reason") else ""
                since = f" since {it['since'][:10]}" if it.get("since") and it["status"] in ("gone", "unlisted") else ""
                self.summary.append(f"  - {item_id}: {it['status']}{since}{reason}")
            self.summary.extend(f"  - {item_id}: skipped, {reason}" for item_id, reason in skipped)
        if counts["failed"] or counts["refused"]:
            self.failed += 1

    def away_since(self, was: dict) -> str:
        """When the item first went gone or unlisted: kept from the lock while it stays away, else this run."""
        return str(was.get("since") or self.now) if was.get("status") in ("gone", "unlisted") else self.now

    def prune(self) -> None:
        """Remove a gone or unlisted file no concept cites, once an earlier run recorded it so: the pull request shows the status one week and the removal the next."""
        cited = cited_paths(self.root)
        for book in (self.lock, self.cache_lock):
            for eid, record in book["entries"].items():
                for item_id in list(record.get("items", {})):
                    it = record["items"][item_id]
                    if it.get("status") not in ("gone", "unlisted"):
                        continue
                    path = it.get("path", "")
                    # A line about a confidential copy names no path, since the summary is the pull request's body.
                    shown_path = "a confidential copy" if book is self.cache_lock else path
                    if path and not self.removable(str(path)):
                        self.summary.append(f"- {eid}: the lock names {shown_path}, outside the mirror, so it stays")
                        continue
                    if path in cited:
                        self.summary.append(f"- {eid}: {shown_path} is {it['status']} and a concept still cites it, so it stays")
                        continue
                    if str(it.get("since", "")) >= self.now:
                        self.summary.append(f"- {eid}: {shown_path} went {it['status']} on this run, so it stays until the next")
                        continue
                    if path:
                        self.removals.append(self.root / path)
                    del record["items"][item_id]
                    self.summary.append(f"- {eid}: {shown_path} was {it['status']} since {str(it.get('since', ''))[:10] or 'an earlier run'} "
                                        "and no concept cites it; removed")

    def commit(self, lock_path: Path, cache_path: Path) -> bool:
        """Write the mirror files and both locks, or say what would be written. True when anything changed on disk."""
        changed = False
        for path, text in self.writes:
            if path.is_file() and path.read_text(encoding="utf-8") == text:
                continue
            changed = True
            if not self.args.dry_run:
                path.parent.mkdir(parents=True, exist_ok=True)
                write_text(path, text)
        named = {e.id for e in self.manifest.entries}
        for book in (self.lock, self.cache_lock):
            left = [eid for eid in book["entries"] if eid not in named]
            cited = cited_paths(self.root) if left and book is self.lock else set()
            for eid in left:
                record = book["entries"].pop(eid)
                paths = [str(it.get("path", "")) for _, it in sorted(record.get("items", {}).items()) if it.get("path")]
                if book is self.cache_lock:
                    # The summary names no confidential copy.
                    gone = [p for p in paths if self.removable(p)]
                    self.removals += [self.root / p for p in gone]
                    if gone:
                        self.summary.append(f"- {eid}: no longer in the manifest, so its {len(gone)} confidential "
                                            f"cop{'ies are' if len(gone) != 1 else 'y is'} removed")
                    continue
                for path in paths:
                    if not self.removable(path):
                        self.summary.append(f"- {eid}: no longer in the manifest, and the lock names {path}, outside the mirror, so it stays")
                        continue
                    self.removals.append(self.root / path)
                    note = ", and a concept still cites it, so the work list will name its source as gone" if path in cited else ""
                    self.summary.append(f"- {eid}: no longer in the manifest, so {path} is removed{note}")
                if not record.get("items"):
                    self.summary.append(f"- {eid}: no longer in the manifest, so its record is dropped")
        # The committed lock's line for a confidential entry that ran says how
        # the run went, and nothing of its items, whose records are in the
        # cache's lock. An entry that did not run keeps its line as it was,
        # records from before included, until it does.
        for eid in sorted(self.settled):
            record = self.cache_lock["entries"].get(eid) or {}
            self.lock["entries"][eid] = {key: discreet(str(record[key])) if key == "reason" else record[key] for key in ("status", "reason") if key in record}
        for path in self.removals:
            if path.is_file():
                changed = True
                if not self.args.dry_run:
                    path.unlink()
                    parent = path.parent
                    while parent != self.root and parent.is_dir() and not any(parent.iterdir()):
                        parent.rmdir()
                        parent = parent.parent
        before = lock_path.read_text(encoding="utf-8") if lock_path.is_file() else None
        text = to_yaml(self.lock)
        if self.ctx.fresher and text != before:
            # New validators are written only with another change: a lock
            # that changes anyway takes those a server gave for bytes that
            # did not change.
            for (eid, item_id), fresh in self.ctx.fresher.items():
                it = ((self.lock["entries"].get(eid) or {}).get("items") or {}).get(item_id)
                if it and it.get("status") == "ok":
                    refresh(it, fresh)
            text = to_yaml(self.lock)
        if text != before:
            changed = True
            if not self.args.dry_run:
                lock_path.parent.mkdir(parents=True, exist_ok=True)
                write_text(lock_path, text)
        # The cache's lock is written only where git ignores it, and only once
        # it holds a record.
        if self.cache_lock["entries"] or cache_path.is_file():
            text = to_yaml(self.cache_lock)
            if (not cache_path.is_file() or cache_path.read_text(encoding="utf-8") != text) and not self.cache_exposed():
                changed = True
                if not self.args.dry_run:
                    cache_path.parent.mkdir(parents=True, exist_ok=True)
                    write_text(cache_path, text)
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
        books = [read_lock(lock_path), read_cache_lock(root / CACHE_LOCK)]
    except Stop:
        books = []
    for lock in books:
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
    # Every git entry needs git 2.31, which reads the configuration the run
    # sets in the environment. An entry that git_pin holds to a checked
    # address, a host name that no proxy resolves, needs 2.37, which reads
    # http.curloptResolve. The run refuses either with an older git, so the
    # preflight warns first.
    gits = [e.id for e in manifest.entries if e.kind == "git" and not e.disabled]
    pinned = [e.id for e in manifest.entries if e.kind == "git" and not e.disabled and pin_needed(e.url, manifest.allow_private)
              and not ip_literal(urllib.parse.urlsplit(e.url).hostname or "") and not proxy_resolves(proxy_for(e.url, git=True))]
    if gits and shutil.which("git"):
        found = git_version()
        if found < (2, 31):
            parts.append(f"this git is {shown_version(found)}, and every git entry needs 2.31 or later: {', '.join(gits)}")
        elif pinned and found < (2, 37):
            parts.append(f"this git is {shown_version(found)}, and a git entry that names a host needs 2.37 or later: {', '.join(pinned)}")
    return "ingest: " + "; ".join(parts)


def write_patch(root: Path, manifest: Manifest, lock: dict, patch_path: Path, cache_lock: dict | None = None) -> int:
    """Reference concepts for the entries that ask for them, as operations for the pen; how many."""
    if patch_path.exists():
        raise Stop(f"{patch_path} exists; apply or remove it first")
    index = root / ".lokf" / "knowledge" / "index.md"
    base_iri = str(frontmatter_of(index).get("base_iri") or "") if index.is_file() else ""
    ops, used = [], set()
    for entry in manifest.entries:
        if not entry.reference:
            continue
        # A confidential entry's records are in the cache's lock, unless it sets lock_details.
        book = cache_lock if entry.local_lock and cache_lock is not None else lock
        record = book["entries"].get(entry.id) or {}
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
    write_text(patch_path, to_yaml({"by": "process:knowledge-ingest", "ops": ops}))
    return len(ops)


def minutes(text: str) -> int:
    """--time-limit's value: whole minutes, 0 for none."""
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError("whole minutes, 0 for no limit") from None
    if value < 0:
        raise argparse.ArgumentTypeError("whole minutes, 0 for no limit")
    return value


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
    ap.add_argument("--time-limit", type=minutes, default=TIME_LIMIT)
    args = ap.parse_args(argv)
    root = Path(args.root).resolve() if args.root else Path.cwd().resolve()
    manifest_path = Path(args.manifest) if args.manifest else root / ".lokf" / "ingest.yaml"
    lock_path = Path(args.lock) if args.lock else root / ".lokf" / "ingest.lock.yaml"
    cache_path = root / CACHE_LOCK
    environ = dict(os.environ)
    if args.status:
        say(status_line(root, manifest_path, lock_path, environ))
        return 0
    try:
        manifest = read_manifest(manifest_path)
        lock = read_lock(lock_path)
        cache_lock = read_cache_lock(cache_path)
        for eid in args.only:
            if not any(e.id == eid for e in manifest.entries):
                raise Stop(f"--only {eid} names no entry in the manifest")
        if args.patch:
            n = write_patch(root, manifest, lock, root / args.patch if not Path(args.patch).is_absolute() else Path(args.patch), cache_lock)
            say(f"wrote {n} operation{'s' if n != 1 else ''} for the pen" if n else "no entry asks for Reference concepts, or every one has its concept")
            return 0
        visibility = repository_visibility(root, args.visibility)
        run = Run(args, root, manifest, lock, visibility, environ, cache_lock)
        for entry in manifest.entries:
            if args.only and entry.id not in args.only:
                continue
            if entry.disabled:
                run.summary.append(f"- {entry.id}: disabled, its mirror kept as it is")
                continue
            if run.ctx.out_of_time():
                run.summary.append(f"- {entry.id} ({entry.describe()}): not reached, the run's time limit of {args.time_limit} minutes "
                                   "passed first, so its records wait for the next run as they were")
                continue
            run.run_entry(entry)
        if args.prune:
            run.prune()
        changed = run.commit(lock_path, cache_path)
    except Stop as e:
        print(f"knowledge-ingest: {e}", file=sys.stderr)
        return 1
    heading = f"## Ingest on {run.now[:10]}" + (" (dry run)" if args.dry_run else "")
    files = sum(1 for e in manifest.entries for it in run.records(e).values() if it.get("status") == "ok")
    size = run.total_mirror_size()
    tail = (f"Mirror: {files} file{'s' if files != 1 else ''}, {size / 1_000_000:.1f} MB, repository {visibility}. "
            "Nothing fetched is knowledge yet: the librarian derives concepts from the mirror on its next run.")
    if not changed:
        tail = "Nothing changed since the last run. " + tail
    # Each line of the summary stays one line, indent kept: a file name or a
    # reason a source gave may hold a line break, which would start a line of
    # the pull request's body, or a workflow command in the job's log.
    summary = [line[: len(line) - len(line.lstrip(" "))] + one_line(line) for line in run.summary]
    lines = [heading, "", *summary, "", tail, ""]
    text = "\n".join(lines)
    say(text.rstrip("\n"))
    if args.summary:
        write_text(Path(args.summary), text)
    if args.strict and run.failed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
