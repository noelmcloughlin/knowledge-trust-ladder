#!/usr/bin/env python3
# The federation build: the job that turns a domain bundle into a workspace.
# A domain is a thin LOKF bundle whose concepts are other bundles, each a
# `MemberBundle` that names one released zip and that zip's checksum (the
# schema is .lokf/domain.yaml, laid down by ktl-sidecar for a domain host).
# This script reads those concepts and builds the workspace the KTL context
# layer page describes: resolve the members into a lock, fetch and verify
# each zip, register and export each bundle with the lokf toolkit, load one
# named graph per bundle, gate the links that cross bundles, and swap the
# result in whole. It runs no agent, and it never writes to the bundle.
#
# Run it from the host's sidecar environment, so it uses the lokf and
# pyoxigraph the host's lock names and installs nothing of its own:
#
#   uv run --project .lokf .lokf/scripts/knowledge-federate.py build --tag v0.2.0
#   uv run --project .lokf .lokf/scripts/knowledge-federate.py build --verify-only
#   uv run --project .lokf .lokf/scripts/knowledge-federate.py members
#   uv run --project .lokf .lokf/scripts/knowledge-federate.py serve
#   uv run --project .lokf .lokf/scripts/knowledge-federate.py query snapshot/queries/labels.rq
#
# `build` writes snapshot.new/ and renames it to snapshot/ in one step, so a
# reader never sees half a federation; a failed build leaves the previous
# snapshot in place. `--verify-only` stops after the zips are checked, which
# is what a pull request that changes a member runs. `members` is the
# domain's librarian: a script, not a model, that lists each member's
# releases, picks the newest that carries a bundle zip, verifies it, and
# writes the change as operations in .lokf/patch.yaml for the pen
# (knowledge-apply.sh) to apply, so the sidecar's librarian workflow can run
# it as AGENT_CLI. The change moves the old release's tag, zip name and day
# in the concept's description and body as well as its frontmatter, so the
# text never contradicts `version`. `serve` and `query` read the snapshot
# through the toolkit's own store and server, with the union of the named
# graphs as the default graph.
#
# What the snapshot holds: index.md (the members, their versions, licences
# and health lines, each member's own index first), llms.txt,
# workspace.lock.yaml, lokf-registry.yaml, registry.jsonld, graph.nq,
# bundles/<slug>/.lokf/knowledge/ (each release, unpacked and read-only),
# export/<slug>/ (the four files lokf export writes), queries/*.rq and
# gate-report.md.
#
# Why each check is here: the checksum ties the bytes to what a person
# confirmed; the attestation (gh attestation verify, when gh is present and
# the zip came from a GitHub release) ties them to the workflow that built
# them; a zip is refused when it holds a symlink, a path outside its root,
# or more bytes than --max-bytes, before anything in it is read; the
# unpacked index.md must name the base_iri the member concept declared, a
# check the toolkit's own registry cannot make; and blank nodes are given
# canonical labels before the graph is written, because lokf export labels
# them at random and the same releases must give the same bytes.
"""The federation build, the domain's librarian, and a reader over the snapshot."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile

import yaml

NAME = "knowledge-federate"
ACTOR = "process:knowledge-federate"
USER_AGENT = "knowledge-federate (https://github.com/noelmcloughlin/knowledge-trust-ladder)"
DEFAULT_MAX_BYTES = 200 * 1024 * 1024
MAX_DEPTH = 3
DCAT = "http://www.w3.org/ns/dcat#"
VOID = "http://rdfs.org/ns/void#"
DCTERMS = "http://purl.org/dc/terms/"
SPDX = "http://spdx.org/rdf/terms#"
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
XSD = "http://www.w3.org/2001/XMLSchema#"
LOKF_NS = "https://w3id.org/lokf/"
# Relation slots whose target is documented as an outside resource, so a
# target no member owns is correct usage there, not a link the gate judges
# (the toolkit's --check-refs reads them the same way).
EXTERNAL_OK = {"definedBy", "source"}
GITHUB_RELEASE = re.compile(
    r"^https://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+)/releases/download/(?P<tag>[^/]+)/(?P<asset>[^/]+)$"
)


class Failed(Exception):
    """A finding that stops the build; the message says what and where."""


def say(msg: str) -> None:
    print(f"{NAME}: {msg}", flush=True)


def warn(msg: str) -> None:
    print(f"{NAME}: {msg}", file=sys.stderr, flush=True)


# ---------------------------------------------------------------------------
# the host and its domain bundle
# ---------------------------------------------------------------------------
def find_root(given: str | None) -> pathlib.Path:
    """The repository root: the directory holding .lokf/knowledge/index.md, given or found above the current one."""
    if given:
        root = pathlib.Path(given).resolve()
        if not (root / ".lokf" / "knowledge" / "index.md").is_file():
            raise Failed(f"{root} has no .lokf/knowledge/index.md")
        return root
    here = pathlib.Path.cwd().resolve()
    for candidate in (here, *here.parents):
        if (candidate / ".lokf" / "knowledge" / "index.md").is_file():
            return candidate
    raise Failed("no .lokf/knowledge/index.md here or above; pass --root")


def read_frontmatter(path: pathlib.Path) -> dict:
    """A concept's frontmatter as the toolkit reads it (its parser, so a bare `verified` mapping and OKF aliases read the same)."""
    from lokf.parse import parse_concept

    return parse_concept(str(path))


class Member:
    """One MemberBundle concept, resolved: where its zip is and what it must be."""

    def __init__(self, concept_path: pathlib.Path, data: dict, parent_iri: str, tier: int):
        self.concept_path = concept_path
        self.slug = concept_path.stem
        self.data = data
        self.parent_iri = parent_iri
        self.tier = tier
        self.base_iri = str(data.get("base_iri") or "")
        self.version = str(data.get("version") or "")
        self.release = str(data.get("release") or "")
        self.title = str(data.get("title") or self.slug)
        dists = data.get("distribution") or []
        if not isinstance(dists, list) or not dists:
            raise Failed(f"{concept_path}: a MemberBundle names its zip under distribution")
        dist = dists[0]
        self.zip_url = str(dist.get("access_url") or "")
        self.zip_name = str(dist.get("name") or pathlib.PurePosixPath(urllib.parse.urlparse(self.zip_url).path).name)
        checksum = str(dist.get("checksum") or "")
        if not checksum.startswith("sha256:") or len(checksum) != 71:
            raise Failed(f"{concept_path}: distribution.checksum must be sha256:<64 hex digits>")
        self.sha256 = checksum[7:].lower()
        if not self.base_iri or not self.zip_url:
            raise Failed(f"{concept_path}: base_iri and distribution.access_url are required")
        m = GITHUB_RELEASE.match(self.zip_url)
        self.github = (m.group("owner"), m.group("repo"), m.group("tag")) if m else None
        if self.github:
            owner, repo, tag = self.github
            self.source_base = f"https://raw.githubusercontent.com/{owner}/{repo}/{tag}/.lokf/knowledge"
            self.repo = f"git+https://github.com/{owner}/{repo}.git@{tag}"
        else:
            self.source_base = ""
            self.repo = None

    def lock_entry(self) -> dict:
        entry = {
            "slug": self.slug,
            "base_iri": self.base_iri,
            "version": self.version,
            "zip": self.zip_url,
            "sha256": self.sha256,
            "member_of": self.parent_iri,
            "tier": self.tier,
        }
        if self.release:
            entry["release"] = self.release
        if self.github:
            entry["repository"] = f"{self.github[0]}/{self.github[1]}"
            entry["source_base"] = self.source_base
        return entry


def read_domain(knowledge: pathlib.Path):
    """The top Domain concept and the MemberBundle concepts of one bundle folder."""
    from lokf.model import load_bundle

    bundle = load_bundle(knowledge)
    domains = [c for c in bundle.concepts if c.type == "Domain"]
    members = [c for c in bundle.concepts if c.type == "MemberBundle"]
    return bundle, domains, members


def top_domain(bundle, domains):
    """The one Domain concept no other Domain in the bundle contains."""
    if not domains:
        raise Failed(f"{bundle.root}: no concept of type Domain; this bundle is not a domain")
    iris = {bundle.iri(d) for d in domains}
    tops = [d for d in domains if not any(t in iris for t in (d.data.get("isPartOf") or []))]
    if len(tops) != 1:
        raise Failed(f"{bundle.root}: expected one top Domain concept, found {len(tops)}")
    return tops[0]


# ---------------------------------------------------------------------------
# fetching and verifying a release zip
# ---------------------------------------------------------------------------
def http_get(url: str, accept: str | None = None, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **({"Accept": accept} if accept else {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - the URL is the one a person confirmed
        return resp.read()


def fetch(url: str, dest: pathlib.Path) -> None:
    """Copy a local path or file:// URL, or download an http(s) URL, to dest."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme in ("", "file"):
        src = pathlib.Path(urllib.request.url2pathname(parsed.path) if parsed.scheme == "file" else url)
        if not src.is_file():
            raise Failed(f"{url}: no such file")
        shutil.copyfile(src, dest)
        return
    if parsed.scheme not in ("http", "https"):
        raise Failed(f"{url}: only http(s), file:// and local paths are fetched")
    try:
        dest.write_bytes(http_get(url))
    except (urllib.error.URLError, TimeoutError) as e:
        raise Failed(f"{url}: could not be fetched ({e})") from e


def digest(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_zip(path: pathlib.Path, max_bytes: int) -> None:
    """Refuse a zip that could reach outside the bundle or exhaust the disk, before anything in it is read."""
    with zipfile.ZipFile(path) as zf:
        total = 0
        for info in zf.infolist():
            name = info.filename
            total += info.file_size
            if total > max_bytes:
                raise Failed(f"{path.name}: unpacks to more than {max_bytes} bytes")
            if name.startswith(("/", "\\")) or ".." in pathlib.PurePosixPath(name).parts or "\\" in name:
                raise Failed(f"{path.name}: entry {name!r} leaves the archive root")
            if not name.startswith("knowledge/"):
                raise Failed(f"{path.name}: entry {name!r} is outside knowledge/, the root the release workflow packs")
            if (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise Failed(f"{path.name}: entry {name!r} is a symbolic link, which a bundle zip never carries")


def verify_attestation(path: pathlib.Path, owner: str, repo: str) -> str:
    """gh attestation verify, when gh is present; the verdict as one line."""
    gh = shutil.which("gh")
    if not gh:
        return "not checked: gh is not installed"
    done = subprocess.run([gh, "attestation", "verify", str(path), "--repo", f"{owner}/{repo}"],
                          capture_output=True, text=True)
    if done.returncode != 0:
        raise Failed(f"{path.name}: gh attestation verify failed for {owner}/{repo}: {(done.stderr or done.stdout).strip()[:300]}")
    return f"attested by {owner}/{repo}"


def obtain(member: Member, cache: pathlib.Path, max_bytes: int, attest: bool) -> tuple[pathlib.Path, str]:
    """The member's zip, in the cache under its digest, checked against the checksum, the zip rules and the attestation."""
    cache.mkdir(parents=True, exist_ok=True)
    cached = cache / f"{member.sha256}.zip"
    if not cached.is_file():
        tmp = cache / f"{member.sha256}.part"
        fetch(member.zip_url, tmp)
        got = digest(tmp)
        if got != member.sha256:
            tmp.unlink(missing_ok=True)
            raise Failed(f"{member.slug}: {member.zip_url} has sha256 {got}, not the {member.sha256} the member concept names")
        tmp.replace(cached)
    elif digest(cached) != member.sha256:
        cached.unlink()
        raise Failed(f"{member.slug}: the cached zip no longer matches its digest; removed, run again")
    check_zip(cached, max_bytes)
    verdict = "checksum matches"
    if member.github and attest:
        verdict += "; " + verify_attestation(cached, member.github[0], member.github[1])
    elif member.github:
        verdict += "; attestation not checked (--no-attestation)"
    return cached, verdict


def unpack(zip_path: pathlib.Path, into: pathlib.Path) -> pathlib.Path:
    """Unpack knowledge/ to into/.lokf/knowledge, the layout the sidecar's scripts read, and return that folder."""
    target = into / ".lokf"
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(target)
    knowledge = target / "knowledge"
    if not (knowledge / "index.md").is_file():
        raise Failed(f"{zip_path.name}: no knowledge/index.md inside")
    return knowledge


# ---------------------------------------------------------------------------
# the build
# ---------------------------------------------------------------------------
def lokf_cli() -> list[str]:
    exe = shutil.which("lokf") or str(pathlib.Path(sys.executable).parent / "lokf")
    if not pathlib.Path(exe).exists():
        raise Failed("the lokf command is not on PATH; run this script with `uv run --project .lokf`")
    return [exe]


def run_lokf(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([*lokf_cli(), *args], capture_output=True, text=True)


def public_url(root: pathlib.Path, given: str | None) -> str:
    """Where the snapshot is served: --public-url, else the website's SITE + BASE + /workspace, else nothing."""
    if given is not None:
        return given.rstrip("/")
    cfg = root / "website" / "site.config.mjs"
    if cfg.is_file():
        text = cfg.read_text(encoding="utf-8")
        site = re.search(r'export const SITE = "([^"]*)"', text)
        base = re.search(r'export const BASE = "([^"]*)"', text)
        if site:
            return f"{site.group(1).rstrip('/')}{(base.group(1) if base else '').rstrip('/')}/workspace"
    return ""


def host_schema(root: pathlib.Path) -> pathlib.Path | None:
    """The domain schema the host's justfile names on its `schema :=` line, as a path, or None."""
    justfile = root / ".lokf" / "justfile"
    if not justfile.is_file():
        return None
    m = re.search(r'^schema := "([^"]*)"$', justfile.read_text(encoding="utf-8"), re.M)
    if not m or not m.group(1):
        return None
    path = (root / ".lokf" / m.group(1)).resolve()
    return path if path.is_file() else None


def health_line(root: pathlib.Path, bundle_root: pathlib.Path) -> str:
    """The member's health line from the sidecar's own report script, or why there is none."""
    script = root / ".lokf" / "scripts" / "knowledge-report.sh"
    if not script.is_file():
        return "no knowledge-report.sh in this host"
    done = subprocess.run(["bash", str(script), "--root", str(bundle_root), "health"], capture_output=True, text=True)
    out = (done.stdout or done.stderr).strip().splitlines()
    return out[-1] if out else "no health line"


def canonical_quads(nt_path: pathlib.Path, graph_iri: str):
    """The triples of one graph.nt as quads in the named graph, blank nodes relabelled canonically."""
    import pyoxigraph as ox

    graph = ox.NamedNode(graph_iri)
    ds = ox.Dataset()
    for q in ox.parse(path=str(nt_path), format=ox.RdfFormat.N_TRIPLES):
        ds.add(ox.Quad(q.subject, q.predicate, q.object, graph))
    ds.canonicalize(ox.CanonicalizationAlgorithm.UNSTABLE)
    # Canonical labels start again at each graph, so two graphs loaded into
    # one store would share a node. A prefix from the graph's IRI keeps each
    # graph's blank nodes its own, and stays the same from build to build.
    prefix = "g" + hashlib.sha256(graph_iri.encode("utf-8")).hexdigest()[:10]
    def own(term):
        return ox.BlankNode(prefix + term.value) if isinstance(term, ox.BlankNode) else term
    out = ox.Dataset()
    for q in ds:
        out.add(ox.Quad(own(q.subject), q.predicate, own(q.object), graph))
    return out


def lock_graph(snapshot_iri: str, domain_iri: str, domain_title: str, records: list[dict]):
    """The lock as RDF, in its own graph: a DCAT catalogue of VoID datasets, each with its distribution and checksum, no blank nodes."""
    import pyoxigraph as ox

    g = ox.NamedNode(snapshot_iri)
    ds = ox.Dataset()

    def add(s, p, o):
        ds.add(ox.Quad(s, ox.NamedNode(p), o, g))

    cat = ox.NamedNode(domain_iri)
    add(ox.NamedNode(snapshot_iri), RDF_TYPE, ox.NamedNode(DCAT + "Catalog"))
    add(ox.NamedNode(snapshot_iri), DCTERMS + "title", ox.Literal(f"{domain_title}: workspace"))
    add(ox.NamedNode(snapshot_iri), DCAT + "catalog", cat)
    for r in records:
        d = ox.NamedNode(r["base_iri"])
        add(ox.NamedNode(snapshot_iri), DCAT + "dataset", d)
        add(d, RDF_TYPE, ox.NamedNode(VOID + "Dataset"))
        add(d, VOID + "uriSpace", ox.Literal(r["base_iri"]))
        add(d, DCTERMS + "title", ox.Literal(r["title"]))
        if r.get("version"):
            add(d, DCAT + "version", ox.Literal(r["version"]))
        if r.get("license"):
            add(d, DCTERMS + "license", ox.NamedNode(r["license"]))
        if r.get("publisher"):
            add(d, DCTERMS + "publisher", ox.NamedNode(r["publisher"]))
        if r.get("member_of"):
            add(d, DCTERMS + "isPartOf", ox.NamedNode(r["member_of"]))
        add(d, VOID + "triples", ox.Literal(str(r["triples"]), datatype=ox.NamedNode(XSD + "integer")))
        if r.get("zip") and r["zip"].startswith("http"):
            dist = ox.NamedNode(r["zip"])
            add(d, DCAT + "distribution", dist)
            add(dist, RDF_TYPE, ox.NamedNode(DCAT + "Distribution"))
            add(dist, DCAT + "downloadURL", dist)
            add(dist, DCAT + "mediaType", ox.Literal("application/zip"))
            add(dist, DCAT + "byteSize", ox.Literal(str(r["bytes"]), datatype=ox.NamedNode(XSD + "integer")))
            chk = ox.NamedNode(r["zip"] + "#sha256")
            add(dist, SPDX + "checksum", chk)
            add(chk, RDF_TYPE, ox.NamedNode(SPDX + "Checksum"))
            add(chk, SPDX + "algorithm", ox.NamedNode(SPDX + "checksumAlgorithm_sha256"))
            add(chk, SPDX + "checksumValue", ox.Literal(r["sha256"]))
    return ds


def gate_predicates() -> dict[str, str]:
    """IRI -> slot name for every typed relation whose target is a concept and not documented as an outside resource."""
    from lokf.schema import vocabulary

    vocab = vocabulary()
    return {rel.uri: name for name, rel in vocab.relation_slots.items() if name not in EXTERNAL_OK}


QUERIES = {
    "labels.rq": """# Each concept's trust label, with the bundle that asserted it (GRAPH ?g binds its base_iri).
# The same rules as knowledge-report.sh, against the clock at the moment of the query.
PREFIX lokf: <https://w3id.org/lokf/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX schema: <http://schema.org/>
SELECT ?g ?c ?title ?label WHERE {
  GRAPH ?g { ?c schema:name ?title . }
  OPTIONAL { GRAPH ?g { ?c lokf:verified ?h . ?h prov:wasAssociatedWith ?by ; prov:endedAtTime ?at . FILTER(STRSTARTS(STR(?by), "human:")) } }
  OPTIONAL { GRAPH ?g { ?c lokf:verified ?any . } }
  OPTIONAL { GRAPH ?g { ?c prov:wasGeneratedBy ?gen . ?gen prov:endedAtTime ?edited . } }
  BIND(IF(BOUND(?at) && BOUND(?edited) && STR(?edited) > STR(?at), "edited since a person confirmed it",
       IF(BOUND(?at), "confirmed by a person",
       IF(BOUND(?any), "checked by automation only", "nobody has checked this yet"))) AS ?label)
}
ORDER BY ?g ?c
""",
    "moved.rq": """# Members whose concept in the domain bundle was edited after a person last confirmed it:
# the members that moved since the domain was confirmed.
PREFIX lokf: <https://w3id.org/lokf/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX schema: <http://schema.org/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?member ?title ?edited (MAX(?at) AS ?lastConfirmed) WHERE {
  GRAPH ?g {
    ?member rdf:type ?t ; schema:name ?title ; prov:wasGeneratedBy ?gen . ?gen prov:endedAtTime ?edited .
    FILTER(STRENDS(STR(?t), "MemberBundle"))
    OPTIONAL { ?member lokf:verified ?v . ?v prov:wasAssociatedWith ?by ; prov:endedAtTime ?at . FILTER(STRSTARTS(STR(?by), "human:")) }
  }
}
GROUP BY ?member ?title ?edited
HAVING (!BOUND(?lastConfirmed) || STR(?edited) > STR(MAX(?at)))
ORDER BY ?member
""",
    "unowned.rq": """# Typed-relation targets that lie in no member's namespace: the gate, as SPARQL over the lock graph's void:uriSpace list.
PREFIX void: <http://rdfs.org/ns/void#>
SELECT DISTINCT ?g ?s ?p ?o WHERE {
  GRAPH ?g { ?s ?p ?o . }
  FILTER(isIRI(?o) && STRSTARTS(STR(?o), "http") && !STRSTARTS(STR(?o), STR(?g)))
  FILTER(?p IN (<http://purl.org/dc/terms/isPartOf>, <http://schema.org/hasPart>, <http://purl.org/dc/terms/requires>,
                <http://www.w3.org/ns/prov#wasDerivedFrom>, <http://schema.org/about>, <http://purl.org/dc/terms/references>,
                <http://purl.org/dc/terms/relation>, <http://www.w3.org/2002/07/owl#sameAs>,
                <https://w3id.org/lokf/measures>, <https://w3id.org/lokf/joinsWith>))
  FILTER NOT EXISTS { ?ds void:uriSpace ?ns . FILTER(STRSTARTS(STR(?o), ?ns)) }
}
ORDER BY ?g ?s
""",
    "members.rq": """# The lock graph: every bundle in the workspace with its version, triples and distribution.
PREFIX void: <http://rdfs.org/ns/void#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?bundle ?title ?version ?triples ?zip WHERE {
  ?bundle a void:Dataset ; dcterms:title ?title ; void:triples ?triples .
  OPTIONAL { ?bundle dcat:version ?version }
  OPTIONAL { ?bundle dcat:distribution ?zip }
}
ORDER BY ?bundle
""",
}


def build(args) -> int:
    """The build, with snapshot.new removed whenever it stops short of the swap."""
    new = None
    try:
        return _build(args, lambda path: globals().__setitem__("_NEW", path))
    finally:
        new = globals().pop("_NEW", None)
        if new is not None and pathlib.Path(new).exists() and not getattr(sys, "_federate_swapped", False):
            shutil.rmtree(new, ignore_errors=True)


def _build(args, note_new) -> int:
    import pyoxigraph as ox
    from lokf.registry import REGISTRY_VERSION, Registry, entry_for_bundle

    root = find_root(args.root)
    knowledge = root / ".lokf" / "knowledge"
    bundle, domains, member_concepts = read_domain(knowledge)
    top = top_domain(bundle, domains)
    domain_iri = bundle.iri(top)
    policy = str(top.data.get("unowned_targets") or "fail")
    if policy not in ("fail", "report"):
        raise Failed(f"{top.path}: unowned_targets must be fail or report, not {policy!r}")
    domain_base = bundle.base_iri
    domain_title = str(bundle.meta.get("title") or top.title)
    tag = args.tag or ""
    snapshot_iri = args.snapshot_iri or (f"{args.release_base.rstrip('/')}/{tag}" if tag and args.release_base else f"urn:knowledge-federate:snapshot:{tag or 'untagged'}")
    out = root / args.out
    new = root / (args.out + ".new")
    cache = pathlib.Path(args.cache).expanduser() if args.cache else root / ".lokf" / ".cache" / "federation"
    say(f"domain {domain_iri} ({len(member_concepts)} members), policy unowned_targets={policy}")

    # 1. Resolve: follow the members, and a member that is itself a domain, into a lock.
    work = pathlib.Path(tempfile.mkdtemp(prefix="federate-")) if args.verify_only else new / "bundles"
    if new.exists():
        shutil.rmtree(new)
    if not args.verify_only:
        note_new(new)
    sys._federate_swapped = False
    work.mkdir(parents=True, exist_ok=True)
    queue: list[tuple[Member, int]] = [(Member(c.path, c.data, domain_iri, 1), 1) for c in member_concepts]
    seen: dict[str, str] = {domain_base: "the domain itself"}
    resolved: list[tuple[Member, pathlib.Path, pathlib.Path, str]] = []  # member, zip, knowledge dir, verdict
    while queue:
        member, depth = queue.pop(0)
        if member.base_iri in seen:
            raise Failed(f"{member.slug}: base_iri {member.base_iri} is already in the federation as {seen[member.base_iri]}; a bundle joins once, and a domain may not name its own ancestors")
        seen[member.base_iri] = member.slug
        zip_path, verdict = obtain(member, cache, args.max_bytes, not args.no_attestation)
        bundle_dir = work / member.slug
        kdir = unpack(zip_path, bundle_dir)
        sub_bundle, sub_domains, sub_members = read_domain(kdir)
        if sub_bundle.base_iri != member.base_iri:
            raise Failed(f"{member.slug}: the zip's index.md says base_iri {sub_bundle.base_iri!r}, the member concept says {member.base_iri!r}")
        say(f"{member.slug}: {member.version} {verdict}; base_iri checked")
        resolved.append((member, zip_path, kdir, verdict))
        if sub_domains:
            if depth >= MAX_DEPTH:
                raise Failed(f"{member.slug}: a domain nested deeper than {MAX_DEPTH} tiers")
            sub_top = top_domain(sub_bundle, sub_domains)
            sub_iri = sub_bundle.iri(sub_top)
            for c in sub_members:
                queue.append((Member(c.path, c.data, sub_iri, depth + 1), depth + 1))
            say(f"{member.slug}: a domain of {len(sub_members)} members, followed")
    lock = {
        "knowledge_federate_lock": "1",
        "domain": domain_iri,
        "domain_base_iri": domain_base,
        "snapshot": snapshot_iri,
        "unowned_targets": policy,
        "members": sorted((m.lock_entry() for m, *_ in resolved), key=lambda e: e["base_iri"]),
    }
    if args.verify_only:
        shutil.rmtree(work, ignore_errors=True)
        say(f"verified {len(resolved)} member zip(s); nothing written (--verify-only)")
        return 0
    new.mkdir(parents=True, exist_ok=True)
    (new / "workspace.lock.yaml").write_text(yaml.safe_dump(lock, sort_keys=False, allow_unicode=True), encoding="utf-8")

    # 2. Register and export each bundle, the domain's own first.
    export_root = new / "export"
    export_root.mkdir()
    public = public_url(root, args.public_url)
    registry = Registry(path=new / "lokf-registry.yaml", id=domain_iri, title=f"{domain_title}: registry",
                        publisher={}, version=REGISTRY_VERSION, repos=[])
    records: list[dict] = []
    graphs: list[tuple[str, pathlib.Path]] = []
    fit: list[str] = []
    domain_copy = work / "domain" / ".lokf" / "knowledge"
    shutil.copytree(knowledge, domain_copy, ignore=shutil.ignore_patterns(".obsidian"))
    bundles = [("domain", domain_copy, None)] + [(m.slug, kdir, m) for m, _, kdir, _ in resolved]
    for slug, kdir, member in sorted(bundles, key=lambda b: b[2].base_iri if b[2] else domain_base):
        source_base = member.source_base if member else ""
        entry = entry_for_bundle(kdir, source_base or None)
        entry.path = None
        entry.status = "ok"
        if member and member.repo:
            entry.repo = member.repo
        if public:
            entry.distribution = {"rdf": f"{public}/export/{slug}/graph.nt", "concepts": f"{public}/export/{slug}/concepts.jsonld"}
        registry.add(entry)
        out_dir = export_root / slug
        done = run_lokf(["export", str(kdir), "--out-dir", str(out_dir), *(["--source-base", source_base] if source_base else [])])
        if done.returncode != 0:
            raise Failed(f"{slug}: lokf export failed: {(done.stderr or done.stdout).strip()[:400]}")
        schema = host_schema(root) if member is None else None
        if schema:
            check = subprocess.run([*lokf_cli(), "validate", "--schema", schema.name, str(kdir)], capture_output=True, text=True, cwd=str(schema.parent))
            fit.append(f"- `{slug}`: " + (f"validates against its domain schema `{schema.name}`" if check.returncode == 0 else f"does not validate against `{schema.name}`: " + (check.stderr or check.stdout).strip().splitlines()[-1][:200]))
        else:
            check = run_lokf(["validate", str(kdir)])
            fit.append(f"- `{slug}`: " + ("validates against LOKF core" if check.returncode == 0 else "does not validate against LOKF core alone (a schema of its own, or a vocabulary outside LOKF): " + (check.stderr or check.stdout).strip().splitlines()[-1][:200]))
        meta = read_frontmatter(kdir / "index.md") if (kdir / "index.md").read_text(encoding="utf-8").startswith("---") else {}
        pub = meta.get("publisher") or {}
        records.append({
            "slug": slug, "base_iri": entry.base_iri, "title": entry.title, "version": member.version if member else tag,
            "license": meta.get("license"), "publisher": pub.get("id") if isinstance(pub, dict) else None,
            "member_of": member.parent_iri if member else None, "triples": entry.void.get("triples", 0),
            "zip": member.zip_url if member else None, "sha256": member.sha256 if member else None,
            "bytes": zip_path_size(resolved, member), "description": meta.get("description", ""),
            "health": health_line(root, kdir.parent.parent), "kdir": kdir,
        })
        graphs.append((entry.base_iri, out_dir / "graph.nt"))
        say(f"{slug}: registered {entry.base_iri} ({entry.void.get('triples', 0)} triples) and exported")
    registry.save()

    # 3. Load: one named graph per bundle, blank nodes canonical, plus the lock graph; then the quads, sorted.
    store = ox.Store()
    lines: list[str] = []
    for base_iri, nt in graphs:
        ds = canonical_quads(nt, base_iri)
        store.extend(ds)
        lines.extend(ox.serialize(ds, format=ox.RdfFormat.N_QUADS).decode("utf-8").splitlines())
    lg = lock_graph(snapshot_iri, domain_iri, domain_title, records)
    store.extend(lg)
    lines.extend(ox.serialize(lg, format=ox.RdfFormat.N_QUADS).decode("utf-8").splitlines())
    (new / "graph.nq").write_text("\n".join(sorted(set(lines))) + "\n", encoding="utf-8")

    # 4. Gate: every typed-relation target outside its graph's namespace, resolved against the registry.
    predicates = gate_predicates()
    unowned: list[tuple[str, str, str, str]] = []
    for base_iri, _ in graphs:
        for q in store.quads_for_pattern(None, None, None, ox.NamedNode(base_iri)):
            if q.predicate.value in predicates and isinstance(q.object, ox.NamedNode):
                target = q.object.value
                if target.startswith(base_iri) or target.startswith(LOKF_NS):
                    continue
                if registry.owner(target) is None:
                    unowned.append((base_iri, q.subject.value, predicates[q.predicate.value], target))
    report = ["# Gate report", "", f"Policy: `unowned_targets: {policy}`. {len(unowned)} typed-relation target(s) lie in no member's namespace.", ""]
    for g, s, p, o in unowned:
        report.append(f"- in `{g}`: `{s}` `{p}` `{o}`")
    report += ["", "## Vocabulary fit", ""] + fit
    (new / "gate-report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    # 5. The index, llms.txt, registry.jsonld and the stored queries.
    write_index(new, domain_title, domain_iri, snapshot_iri, policy, records, unowned, public)
    (new / "registry.jsonld").write_text(json.dumps(registry_jsonld(registry, records), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (new / "queries").mkdir()
    for name, text in QUERIES.items():
        (new / "queries" / name).write_text(text, encoding="utf-8")
    for r in records:  # the unpacked releases stay read-only, as released
        for p in r["kdir"].rglob("*"):
            if p.is_file():
                p.chmod(0o444)
    if unowned and policy == "fail":
        shutil.rmtree(new, ignore_errors=True)
        for g, s, p, o in unowned:
            warn(f"unowned target in {g}: {s} {p} {o}")
        raise Failed(f"{len(unowned)} typed-relation target(s) lie in no member's namespace and the domain's policy is fail; the previous snapshot stays")

    # 6. Swap.
    old = root / (args.out + ".old")
    if old.exists():
        shutil.rmtree(old)
    if out.exists():
        out.rename(old)
    new.rename(out)
    sys._federate_swapped = True
    if old.exists():
        shutil.rmtree(old)
    say(f"workspace built: {len(records)} bundles, {len(lines)} quads, {len(unowned)} unowned target(s) reported -> {out}")
    return 0


def zip_path_size(resolved, member) -> int:
    if member is None:
        return 0
    for m, zip_path, _, _ in resolved:
        if m is member:
            return zip_path.stat().st_size
    return 0


def write_index(new: pathlib.Path, domain_title: str, domain_iri: str, snapshot_iri: str, policy: str,
                records: list[dict], unowned, public: str) -> None:
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    lines = [f"# {domain_title}: the workspace", "",
             f"The graph built from the releases the domain <{domain_iri}> names, one named graph per bundle, named by that bundle's `base_iri`, with the lock as a graph of its own, <{snapshot_iri}>. Built on {today}; the members and their versions below are the lock's, and each health line is that member's own at the release named, computed when this was built. A trust label is never stored: `queries/labels.rq` computes each from the events at the moment it runs.",
             "", "Read a member's own `index.md` first, then its concepts; `export/<slug>/concepts.jsonld` holds every concept of a bundle with its body.", "",
             "## Members", "", "| Bundle | Version | Namespace | Licence | Health at this release |", "| --- | --- | --- | --- | --- |"]
    for r in records:
        if r["slug"] == "domain":
            continue
        licence = f"<{r['license']}>" if r.get("license") else ""
        lines.append(f"| [{r['title']}](bundles/{r['slug']}/.lokf/knowledge/index.md) | {r['version']} | `{r['base_iri']}` | {licence} | {r['health']} |")
    dom = next((r for r in records if r["slug"] == "domain"), None)
    if dom:
        lines += ["", f"The domain bundle itself: [{dom['title']}](bundles/domain/.lokf/knowledge/index.md) at `{dom['base_iri']}`, {dom['triples']} triples; its health line: {dom['health']}."]
    lines += ["", "## Files", "",
              "- `workspace.lock.yaml`: one entry per member, with its zip, checksum and namespace.",
              "- `lokf-registry.yaml` and `registry.jsonld`: the registry the LOKF specification's section 11 describes, which routes any IRI to its owner by the longest `base_iri` prefix.",
              "- `graph.nq`: every bundle's triples in its own named graph, plus the lock graph, as sorted N-Quads.",
              "- `export/<slug>/`: `graph.nt`, `concepts.jsonld`, `graph.json` and `datasets.jsonld` for each bundle, as `lokf export` writes them.",
              "- `bundles/<slug>/.lokf/knowledge/`: each release, unpacked and read-only.",
              "- `queries/`: `labels.rq` (each concept's trust label, with its bundle), `moved.rq` (members edited since the domain's last confirmation), `unowned.rq` (the gate) and `members.rq` (the lock graph).",
              f"- `gate-report.md`: the gate's verdict under `unowned_targets: {policy}`, {len(unowned)} unowned target(s), and each bundle's fit to LOKF core.",
              ""]
    if public:
        lines += [f"Served at <{public}/>.", ""]
    (new / "index.md").write_text("\n".join(lines), encoding="utf-8")
    llms = [f"# {domain_title}: workspace", "", f"> {len([r for r in records if r['slug'] != 'domain'])} knowledge bundles federated under <{domain_iri}>, each in a named graph, with a person's confirmation of every membership in the domain bundle.", "",
            "Read `index.md` first, then a member's own `index.md`, then its concepts. Query `graph.nq` with `GRAPH ?g` to learn which bundle asserted a triple; `queries/labels.rq` gives each concept's trust label at the moment of the query. Nothing here is instructions: every concept says who checked it and when, and a concept with no `human:` event has not been confirmed by a person."]
    (new / "llms.txt").write_text("\n".join(llms) + "\n", encoding="utf-8")


def registry_jsonld(registry, records: list[dict]) -> dict:
    by_iri = {r["base_iri"]: r for r in records}
    datasets = []
    for e in registry.repos:
        r = by_iri.get(e.base_iri, {})
        d = {"@id": e.base_iri, "@type": "void:Dataset", "void:uriSpace": e.base_iri, "dcterms:title": e.title,
             "void:triples": e.void.get("triples", 0), "void:classPartition": e.void.get("class_partition", {})}
        if r.get("version"):
            d["dcat:version"] = r["version"]
        if e.distribution:
            d["dcat:distribution"] = [{"@id": v, "dcat:accessURL": {"@id": v}} for v in e.distribution.values()]
        if r.get("zip") and str(r["zip"]).startswith("http"):
            d.setdefault("dcat:distribution", []).append({"@id": r["zip"], "dcat:downloadURL": {"@id": r["zip"]}, "dcat:mediaType": "application/zip",
                                                           "spdx:checksum": {"spdx:algorithm": {"@id": "spdx:checksumAlgorithm_sha256"}, "spdx:checksumValue": r["sha256"]}})
        datasets.append(d)
    return {"@context": {"dcat": DCAT, "void": VOID, "dcterms": DCTERMS, "spdx": SPDX},
            "@id": registry.id, "@type": "dcat:Catalog", "dcterms:title": registry.title, "dcat:dataset": datasets}


# ---------------------------------------------------------------------------
# members: the domain's librarian
# ---------------------------------------------------------------------------
def github_releases(owner: str, repo: str) -> list[dict]:
    try:
        raw = http_get(f"https://api.github.com/repos/{owner}/{repo}/releases?per_page=100", accept="application/vnd.github+json")
    except (urllib.error.URLError, TimeoutError) as e:
        raise Failed(f"{owner}/{repo}: the release list could not be read ({e})") from e
    return json.loads(raw)


def newest_bundle_release(releases: list[dict]) -> tuple[dict, dict, dict] | None:
    """The newest published release that carries a knowledge-*.zip and its .sha256: (release, zip asset, sum asset)."""
    for rel in releases:  # the API lists newest first
        if rel.get("draft"):
            continue
        assets = {a["name"]: a for a in rel.get("assets", [])}
        for name, asset in assets.items():
            if name.startswith("knowledge-") and name.endswith(".zip") and name + ".sha256" in assets:
                return rel, asset, assets[name + ".sha256"]
    return None


def release_day(release: dict | None) -> str:
    """The day a release was published, as a concept's text writes it (YYYY-MM-DD), or "" when the release list does not say."""
    day = str((release or {}).get("published_at") or "")[:10]
    return day if re.fullmatch(r"\d{4}-\d{2}-\d{2}", day) else ""


def open_librarian_pr() -> bool:
    gh = shutil.which("gh")
    if not gh:
        return False
    done = subprocess.run([gh, "pr", "list", "--state", "open", "--search", "head:knowledge-librarian/", "--json", "number"],
                          capture_output=True, text=True)
    return done.returncode == 0 and bool(json.loads(done.stdout or "[]"))


def when(value) -> dt.datetime | None:
    """A provenance time as an aware datetime, or None when it is not one. The toolkit's parser gives times as ISO text, and one with no offset is read as UTC."""
    try:
        t = dt.datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def confirmed_by_person(data: dict) -> bool:
    """Whether a person confirmed the concept as it stands, by the rule knowledge-report.sh uses.

    That takes a `verified` event whose actor starts human:, and no edit
    stamped after the latest such event, because a later edit means the
    person confirmed an earlier text.
    """
    events = data.get("verified")
    events = [events] if isinstance(events, dict) else events if isinstance(events, list) else []
    times = [when(e.get("at")) for e in events if isinstance(e, dict) and str(e.get("by", "")).startswith("human:")]
    if not times:
        return False
    generated = data.get("generated")
    edited = when(generated.get("at")) if isinstance(generated, dict) else None
    confirmed = max((t for t in times if t is not None), default=None)
    return not (edited and confirmed and edited > confirmed)


def written_by_person(data: dict) -> bool:
    """Whether a person wrote the concept's text, which the pen refuses to patch."""
    generated = data.get("generated")
    return isinstance(generated, dict) and str(generated.get("by", "")).startswith("human:")


# The lines of a concept's body the pen never edits, and the lines it reads
# as a person's event or note, with the same markers and patterns the pen
# (knowledge-apply.py) uses, so no edit built here is one the pen refuses.
RELATED_START, RELATED_END = "<!-- lokf:related -->", "<!-- /lokf:related -->"
OPEN_Q = "## Open questions"
PERSON_LINE = re.compile(r"^\s*-?\s*by:\s*human:|^\s*-\s*\d{4}-\d{2}-\d{2},\s*human:")


def mover(pairs: dict[str, str]):
    """A function that writes each old value in a text as its new one.

    It works in one pass, so a value already moved is never moved again, and
    a value counts only as a whole token: the tag is not moved inside
    v0.43.10 or v0.43.0-rc1, nor the day inside a timestamp.
    """
    pairs = {old: new for old, new in pairs.items() if old and new and old != new}
    if not pairs:
        return lambda text: text
    alternatives = "|".join(re.escape(old) for old in sorted(pairs, key=len, reverse=True))
    pattern = re.compile(rf"(?<![\w.])(?:{alternatives})(?![\w-]|\.\w)")
    return lambda text: pattern.sub(lambda m: pairs[m.group(0)], text)


def concept_body(path: pathlib.Path) -> str | None:
    """A concept's body as the pen reads it: everything after the line that closes the frontmatter."""
    lines = path.read_text(encoding="utf-8").split("\n")
    if not lines or lines[0] != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i] == "---":
            return "\n".join(lines[i + 1:])
    return None


def protected_lines(lines: list[str]) -> set[int]:
    """The numbers of the lines in the lokf:related block and the ## Open questions section, found as the pen finds them."""
    kept: set[int] = set()
    for i, line in enumerate(lines):
        if line.strip() == RELATED_START:
            end = next((j for j in range(i + 1, len(lines)) if lines[j].strip() == RELATED_END), None)
            if end is not None:
                kept.update(range(i, end + 1))
            break
    fenced = False
    for i, line in enumerate(lines):
        if line.startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if not fenced and line.strip() == OPEN_Q:
            end = next((j for j in range(i + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
            kept.update(range(i, end))
            break
    return kept


def body_edits(body: str, move) -> tuple[list[dict], int]:
    """The pen's edits that move the old release in a body, and how many lines naming it are left as they were.

    Each edit replaces one whole line. The pen applies the edits in order
    and refuses the whole patch when a target occurs other than exactly once
    in the body as it then stands, so each target is counted in the body the
    edits before it leave. A line that occurs more than once, or that reads
    as a person's event or note, is left for a person and counted. Lines in
    the lokf:related block and under ## Open questions are never edited and
    are not counted, since an open question may name the old release on
    purpose.
    """
    lines = body.split("\n")
    kept = protected_lines(lines)
    edits: list[dict] = []
    left = 0
    current = body
    for i, line in enumerate(lines):
        moved = move(line)
        if i in kept or moved == line:
            continue
        if current.count(line) != 1 or PERSON_LINE.match(line):
            left += 1
            continue
        current = current.replace(line, moved, 1)
        edits.append({"replace": {"target": line, "content": moved}})
    return edits, left


def members(args) -> int:
    root = find_root(args.root)
    knowledge = root / ".lokf" / "knowledge"
    bundle, domains, member_concepts = read_domain(knowledge)
    top_domain(bundle, domains)
    cache = pathlib.Path(args.cache).expanduser() if args.cache else root / ".lokf" / ".cache" / "federation"
    ops: list[dict] = []
    handoff: list[str] = []
    current: list[str] = []
    for c in member_concepts:
        member = Member(c.path, c.data, "", 1)
        if not member.github:
            current.append(f"{member.slug}: not a GitHub release, left as it is")
            continue
        owner, repo, _ = member.github
        releases = github_releases(owner, repo)
        found = newest_bundle_release(releases)
        if not found:
            current.append(f"{member.slug}: no release of {owner}/{repo} carries a bundle zip")
            continue
        release, zip_asset, sum_asset = found
        tag = release["tag_name"]
        if tag == member.version:
            current.append(f"{member.slug}: {tag} is current")
            continue
        sum_text = http_get(sum_asset["browser_download_url"]).decode("utf-8", "replace").split()
        if not sum_text or not re.fullmatch(r"[0-9a-f]{64}", sum_text[0]):
            raise Failed(f"{member.slug}: {sum_asset['name']} does not start with a sha256 digest")
        new_sha = sum_text[0]
        distribution = [{"name": zip_asset["name"], "access_url": zip_asset["browser_download_url"], "media_type": "application/zip", "checksum": f"sha256:{new_sha}"}]
        moved = Member(c.path, {**c.data, "version": tag, "distribution": distribution}, "", 1)
        _, verdict = obtain(moved, cache, args.max_bytes, not args.no_attestation)
        release_url = f"https://github.com/{owner}/{repo}/releases/tag/{tag}"
        path = c.concept_id + ".md"
        # "Confirmed" only when a person confirmed the concept as it stands; a
        # draft, or a member moved since its confirmation, names the release
        # it holds and claims nothing more.
        confirmed = confirmed_by_person(c.data)
        asked = f"{owner}/{repo} released {tag} after {'the confirmed ' if confirmed else ''}{member.version}; does this member move to it?"
        if written_by_person(c.data):
            # The pen refuses any patch of a concept a person wrote, so the
            # move goes to the curator as a question alone.
            ops.append({"op": "question", "path": path, "text": f"{asked} A person wrote this concept, so this patch leaves its text and frontmatter as they are."})
            handoff.append(f"{member.slug}: {member.version} -> {tag}; {verdict}; a person wrote the concept, so only a question was added.")
            continue
        # The move reaches the text too: the old tag, zip name and day become
        # the new ones in the description and in the body, so the concept no
        # longer says one release in `version` and another in its prose.
        old_day = release_day(next((r for r in releases if r.get("tag_name") == member.version), None))
        move = mover({member.version: tag, member.zip_name: zip_asset["name"], old_day: release_day(release)})
        sets: dict = {"version": tag, "release": release_url, "resource": release_url, "distribution": distribution}
        description = str(c.data.get("description") or "")
        if move(description) != description:
            sets["description"] = move(description)
        body = concept_body(c.path)
        edits, left = body_edits(body, move) if body is not None else ([], 0)
        op: dict = {"op": "patch", "path": path}
        if edits:
            op["edits"] = edits
        op["set"] = sets
        op["log"] = f"**Changed**: {member.title} moved from {member.version} to {tag}; the release carries `{zip_asset['name']}`."
        ops.append(op)
        if left:
            asked += (f" {left} line(s) of the body still name {member.version}, its zip or its day; this patch left them as they were,"
                      " because each occurs more than once in the body or reads as a person's record.")
        ops.append({"op": "question", "path": path, "text": asked})
        note = "" if old_day else f"; {member.version} is not in the release list, so its day was not moved"
        handoff.append(f"{member.slug}: {member.version} -> {tag}; {verdict}{note}; a person confirms the member{' again' if confirmed else ''} to accept it.")
    for line in current:
        say(line)
    if not ops:
        say("every member is current; no patch written")
        return 0
    patch = {"by": ACTOR, "ops": ops, "handoff": handoff[:10]}
    # One line per value, so a replace target reaches the pen exactly as the
    # body holds it and no folded line can start like a person's event.
    text = yaml.safe_dump(patch, sort_keys=False, allow_unicode=True, width=1_000_000)
    pr_open = open_librarian_pr()
    if args.dry_run:
        # A dry run always shows the patch it would write; only a real run
        # stands back for an open pull request, so the note goes to stderr.
        print(text)
        if pr_open:
            warn("a knowledge-librarian pull request is already open, so a run without --dry-run would write no patch")
        return 0
    if pr_open:
        say(f"{len(handoff)} member(s) moved, but a knowledge-librarian pull request is already open; no patch written")
        return 0
    target = root / ".lokf" / "patch.yaml"
    target.write_text(text, encoding="utf-8")
    say(f"{len(handoff)} member(s) moved; operations written to {target} for the pen")
    return 0


# ---------------------------------------------------------------------------
# serve and query: the toolkit's store and server over the union of the graphs
# ---------------------------------------------------------------------------
def union_store(snapshot: pathlib.Path):
    import pyoxigraph as ox
    from lokf.schema import vocabulary
    from lokf.store import GraphStore

    nq = snapshot / "graph.nq"
    if not nq.is_file():
        raise Failed(f"{nq} not found; run build first")

    class UnionStore(GraphStore):
        def query(self, sparql: str, **kw):
            kw.setdefault("use_default_graph_as_union", True)
            return super().query(sparql, **kw)

        def rdflib_graph(self, sparql: str | None = None):
            if sparql is not None:
                return super().rdflib_graph(sparql)
            from rdflib import Graph

            triples = ox.Dataset()
            for q in self.store:
                triples.add(ox.Quad(q.subject, q.predicate, q.object, ox.DefaultGraph()))
            g = Graph()
            g.parse(data=ox.serialize(triples, format=ox.RdfFormat.N_QUADS).decode("utf-8"), format="nquads")
            for prefix, ns in self.prefixes.items():
                g.bind(prefix, ns)
            return g

    store = ox.Store()
    store.load(path=str(nq), format=ox.RdfFormat.N_QUADS)
    prefixes = {**vocabulary().prefixes, "void": VOID, "dcat": DCAT, "spdx": SPDX, "dcterms": DCTERMS}
    return UnionStore(store, prefixes)


def serve(args) -> int:
    from lokf.server import build_server

    root = find_root(args.root)
    store = union_store(root / args.snapshot)
    httpd = build_server(store, args.host, args.port)
    say(f"{len(store)} quads from {args.snapshot}; SPARQL at http://{args.host}:{args.port}/sparql, graph at http://{args.host}:{args.port}/ ; Ctrl-C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


def query(args) -> int:
    root = find_root(args.root)
    store = union_store(root / args.snapshot)
    text = pathlib.Path(args.query).read_text(encoding="utf-8") if pathlib.Path(args.query).is_file() else args.query
    if args.format == "json":
        sys.stdout.buffer.write(store.serialize_results(text, "json"))
        return 0
    rows = store.select(text)
    if not rows:
        say("no rows")
        return 0
    cols = list(rows[0].keys())
    print("\t".join(cols))
    for row in rows:
        print("\t".join(str(row.get(c, "")) for c in cols))
    return 0


# ---------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog=NAME, description=__doc__)
    ap.add_argument("--root", help="the repository root (default: found above the current directory)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="build the workspace from the domain bundle")
    b.add_argument("--out", default="snapshot", help="the snapshot folder under the root (default: snapshot)")
    b.add_argument("--tag", default="", help="this domain release's tag, named in the lock graph")
    b.add_argument("--release-base", default="", help="the release page prefix, e.g. https://github.com/o/r/releases/tag; with --tag it names the snapshot")
    b.add_argument("--snapshot-iri", default="", help="the lock graph's IRI, when not derived from --release-base and --tag")
    b.add_argument("--public-url", default=None, help="where the snapshot is served; default from website/site.config.mjs")
    b.add_argument("--cache", default=None, help="where zips are kept by digest (default .lokf/.cache/federation)")
    b.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES, help="refuse a zip that unpacks to more than this")
    b.add_argument("--no-attestation", action="store_true", help="skip gh attestation verify")
    b.add_argument("--verify-only", action="store_true", help="fetch and verify every zip, write nothing")
    b.set_defaults(func=build)
    m = sub.add_parser("members", help="propose moving each member to its newest released zip, as a patch for the pen")
    m.add_argument("--cache", default=None)
    m.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    m.add_argument("--no-attestation", action="store_true")
    m.add_argument("--dry-run", action="store_true", help="print the patch instead of writing .lokf/patch.yaml")
    m.set_defaults(func=members)
    s = sub.add_parser("serve", help="SPARQL endpoint and graph page over the snapshot")
    s.add_argument("--snapshot", default="snapshot")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8000)
    s.set_defaults(func=serve)
    q = sub.add_parser("query", help="run SPARQL (a file or text) over the snapshot")
    q.add_argument("query")
    q.add_argument("--snapshot", default="snapshot")
    q.add_argument("--format", choices=["table", "json"], default="table")
    q.set_defaults(func=query)
    args = ap.parse_args(argv)
    # The librarian wrapper hands its prompt to AGENT_CLI as `-p "<prompt>"`;
    # argparse rejects it, so it is stripped before parsing above.
    try:
        return args.func(args)
    except Failed as e:
        warn(str(e))
        return 1


if __name__ == "__main__":
    argv = sys.argv[1:]
    if "-p" in argv:  # the librarian wrapper's prompt flag and its one argument
        i = argv.index("-p")
        del argv[i:i + 2]
    sys.exit(main(argv))
