"""The federation build: knowledge-federate.py over fixture bundles.

Two tiny bundles and a domain that names them by zip are built under a
temporary host, and the script is run the way a host runs it, through the
repository's own sidecar environment (`uv run --project .lokf`), so the lokf
toolkit and pyoxigraph it needs are the ones the lock pins. It checks:

1. a build resolves the members into a lock, loads one named graph per
   bundle plus the lock graph, gates clean, and writes the same bytes twice;
2. a tampered checksum, a zip whose index.md names another base_iri, a zip
   holding a symbolic link, a hidden file such as a .git folder or a file a
   browser runs, a distribution name that is not one plain file name, and a
   domain that names a bundle already in the federation each stop the build
   and leave the previous snapshot in place, and the health line runs git on
   no repository a member's zip could carry,
   as do a checksum that is not 64 hex digits, a namespace that nests with
   another's, a redirect out of http, and a zip that cannot be read; a
   download that meets a server error is tried again;
2a. a bundle that releases no zip joins by the concepts.jsonld its site
   serves, written out as the bundle, with the graph its own export gave;
   a file that names another base_iri, a concept outside its namespace or a
   path that climbs out of the bundle is refused;
2b. a member whose file cannot be fetched is held at its last good state,
   as the previous workspace holds it, as a folder or a zip, at the same
   release or an earlier one; a check does the same, and a workspace of
   another domain is not taken; a release zip that serves other bytes is
   held only at the release a build fetched, a check holds nothing its pull
   request proposes, and a member no previous workspace held is left out;
3. a typed relation whose target no member owns stops the build under
   `unowned_targets: fail` and is reported under `report`, and so does one
   whose target lies in a member's namespace and names no concept of it;
3a. the links between members are counted in the lock, the index and
   `links.rq`, and `graph.json` draws every bundle with those links; a
   reified `relations` entry is gated and counted as the slot it names;
4. a member that is itself a domain is followed one tier down;
4a. the diamond rule: a bundle two domains name at one release joins once,
   named by both, and named at two releases it stops the build, as a
   second naming with an unknown sensitivity does;
4b. the depth a build follows is the top Domain concept's `max_depth`, 3
   unless set, and a `MemberDomain` whose zip holds no Domain stops it;
4c. a concept a curator retired (`status: deprecated`) takes no part: a
   retired Domain concept is not a second top, and a retired member is
   neither built into the workspace nor moved by `members`;
4d. a member joins only as a person confirmed it: one no person confirmed
   is left out and listed as waiting, at the top tier and in a member
   domain's zip, while `--verify-only` still checks its zip; one moved by a
   commit no person confirmed is built at the release the default branch
   held confirmed, until a person confirms the move, and an error about
   that release says what waits; a member a person sent back stays;
4e. the walk through history takes only the default branch's own line, the
   concept's own path and IRI, and a confirmation whose event still stands:
   a removed confirmation, a renamed concept, an `id` changed in place, a
   retirement undone without a confirmation and a text that only stood on
   a side branch each leave the member out or at its earlier release;
4f. the Domain concept's `unowned_targets` and `max_depth` count only as a
   person confirmed them, and the gate names a member that waits when a
   link lies in its namespace;
4g. a member that waits in a member domain joins at the release that
   domain's own build took, from the lock in the workspace the
   `MemberDomain` names; a workspace that is another domain's, or whose
   checksum is wrong, stops the build, and a lock that names no member
   concept or no release of that member leaves it out;
4h. a member names the files of one release: a workspace from another
   release of the same repository is refused;
4i. a member joins only at the `sensitivity` its domain cleared: an
   internal one once a person confirms `internal` on the Domain concept,
   and only in a private or internal repository, and a confidential one
   never; a raised sensitivity counts before a person confirms it, and
   domain.yaml lets a Domain clear public or internal alone;
5. `--verify-only` runs the gate as the next release build would, so a link
   into a member no person has confirmed fails before the merge, and writes
   nothing; `members` leaves a non-GitHub member as it is;
5a. a schema released beside a member's zip, named as a second distribution,
   is what the member's fit is checked against, and a wrong digest for it
   stops the build;
5b. `mcp` serves the workspace index as its instructions and answers the
   five tools of the specification's section 11.4, each bounded, a
   SPARQL CONSTRUCT and SELECT too, and `read_document` falls back to a
   bundle's concepts.jsonld;
5c. it loads a graph when a walk first reaches a namespace that graph
   names, and each answer is the one a workspace loaded whole gives;
5d. `diff` says which members joined, moved, left, were released again or
   grew sensitive between two workspaces, and the links that went with them;
5e. a walk that steps to an IRI no bundle owns loads the graphs that share
   it and no more;
5f. the readers read a workspace from its zip, or from the site that serves
   it, a graph at a time by range request, with the answers a folder gives;
5g. a reader given members reads those bundles alone, and refuses the
   stored queries that read the lock graph;
5h. a licence given as text, and a concept whose id lies outside its
   bundle's namespace, read as released;
6. `members` moves a member's old tag, zip name and day in its description
   and body as well as its frontmatter, in a patch the pen applies, and
   names the lines it had to leave in its question;
7. its question calls a member "confirmed" only when a person confirmed the
   concept as it stands, and puts the move to a person as a question alone
   when a person wrote the concept;
8. a dry run prints the patch while a librarian pull request is open, and a
   real run then writes nothing;
9. `members --add owner/repo` drafts a member concept from that repository's
   newest bundle release, quoting the description in the release's own
   index, with the schema released beside it, as a
   `MemberDomain` when that release is a domain, and refuses a path that
   exists or a namespace that nests with a member's;
9a. for a member domain, `members` names the workspace its release
   carries: on a move, on its own when the release attached it later, and
   again when the workspace was attached again with other bytes.
10. under the librarian wrapper, `members` hands the job token that arrives
    as KNOWLEDGE_FEDERATE_TOKEN to gh alone, and with no credential at all
    it stops and says which variables give it one;
11. `members` moves a member its site serves to the file the site serves
    now, asking with the validators it kept, and `members --add <address>`
    drafts one from a site's concepts.jsonld;
12. `members` moves the others when it cannot check one, and asks gh for a
    release list the API refuses as rate limited.

The `members` tests run the script through a small runner that serves the
GitHub API and the release files from fixture files, and put a stand-in
`gh` first on PATH, so no test reaches the network or a real repository.

`uv` is required: without it every test here skips and says so.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import shutil
import stat
import zipfile
from pathlib import Path

import pytest
import yaml

from conftest import REPO, SCRIPTS, TEMPLATES, Git, have, read, run, today_utc, write

SCRIPT = SCRIPTS / "knowledge-federate.py"
APPLY = SCRIPTS / "knowledge-apply.sh"
needs_uv = pytest.mark.skipif(not have("uv"), reason="uv is not installed - the federation build runs in the sidecar's environment")
pytestmark = needs_uv


@pytest.fixture(scope="module", autouse=True)
def _sidecar_environment(tmp_path_factory):
    """The sidecar's environment, made once before any test runs uv in it.

    Parallel workers each start with `uv run --project .lokf`. In a fresh
    checkout the first ones would all create .lokf/.venv at once, and one finds
    it half made. So each worker takes a lock in the temporary folder all of
    them share, and the first to hold it makes the environment.
    """
    import fcntl

    lock = tmp_path_factory.getbasetemp().parent / "sidecar-environment.lock"
    with open(lock, "w") as held:
        fcntl.flock(held, fcntl.LOCK_EX)
        run(["uv", "run", "--quiet", "--project", REPO / ".lokf", "python", "-c", "pass"])


def federate(host: Path, *args: str, **kw):
    return run(["uv", "run", "--project", REPO / ".lokf", SCRIPT, "--root", host, *args], cwd=host, **kw)


def frontmatter(**fields) -> str:
    import yaml

    return "---\n" + yaml.safe_dump(fields, sort_keys=False) + "---\n"


def make_bundle(root: Path, base_iri: str, title: str, concepts: dict[str, dict], description: str | None = None) -> Path:
    """A bundle folder: index.md with the base_iri, and one concept per path."""
    k = root / "knowledge"
    write(k / "index.md", frontmatter(lokf_version="0.2", okf_version="0.2", base_iri=base_iri, title=title,
                                      description=description or f"{title}.", license="https://creativecommons.org/licenses/by/4.0/",
                                      publisher={"type": "Person", "id": base_iri + "person/x", "name": "X"})
          + f"\n# {title}\n")
    write(k / "log.md", "# Change Log\n\n## 2026-01-01\n\n* **Initialization**: fixture.\n")
    for path, fm in concepts.items():
        write(k / path, frontmatter(**fm) + f"\n# Overview\n\n{fm['title']}.\n")
    return k


def zip_bundle(knowledge: Path, zip_path: Path, symlink: bool = False, extra: dict[str, str] | None = None) -> str:
    """The bundle as the release workflow packs it: root knowledge/, names sorted, and any extra entries. Returns the sha256."""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(knowledge.rglob("*")):
            if p.is_file():
                zf.write(p, "knowledge/" + p.relative_to(knowledge).as_posix())
        for name, content in (extra or {}).items():
            zf.writestr(name, content)
        if symlink:
            info = zipfile.ZipInfo("knowledge/link.md")
            info.create_system = 3
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            zf.writestr(info, "../../etc/passwd")
    return hashlib.sha256(zip_path.read_bytes()).hexdigest()


CONFIRMED = [{"by": "human:noel", "at": "2026-01-02T00:00:00Z"}]


def member(slug: str, base_iri: str, zip_path: Path, sha: str, domain_iri: str, version: str = "v1.0.0", kind: str = "MemberBundle", confirmed: bool = True) -> dict:
    """A member concept naming one zip; a person confirmed it unless `confirmed` is false, since a build takes only what a person confirmed."""
    concept = {
        "type": kind, "title": f"{slug} bundle", "description": f"The {slug} bundle at {version}.",
        "resource": zip_path.as_uri(), "base_iri": base_iri, "version": version,
        "distribution": [{"name": zip_path.name, "access_url": zip_path.as_uri(), "media_type": "application/zip", "checksum": f"sha256:{sha}"}],
        "isPartOf": [domain_iri],
    }
    if confirmed:
        concept["verified"] = CONFIRMED
    else:
        concept["status"] = "draft"
    return concept


def make_domain(host: Path, base_iri: str, members: dict[str, dict], policy: str = "fail", title: str = "D") -> Path:
    """A domain host: .lokf/knowledge with a Domain concept and the member concepts, and the report script for health lines."""
    domain_iri = base_iri + "domains/federation"
    concepts = {"domains/federation.md": {"type": "Domain", "title": "The federation domain", "description": "The domain.", "resource": "https://example.test/d", "unowned_targets": policy, "verified": CONFIRMED}}
    concepts.update({f"members/{slug}.md": fm for slug, fm in members.items()})
    make_bundle(host / ".lokf", base_iri, title, concepts)
    scripts = host / ".lokf" / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    shutil.copy(SCRIPTS / "knowledge-report.sh", scripts / "knowledge-report.sh")
    return host


def domain_zip(tmp_path: Path, slug: str, base_iri: str, members: dict[str, dict]) -> tuple[Path, str]:
    """A domain bundle zipped as its release would be: a Domain concept and the member concepts. Returns the zip and its sha256."""
    concepts = {f"domains/{slug}.md": {"type": "Domain", "title": f"{slug} domain", "description": "A domain.", "resource": f"https://example.test/{slug}", "unowned_targets": "fail"}}
    concepts.update({f"members/{m}.md": fm for m, fm in members.items()})
    k = make_bundle(tmp_path / f"{slug}-domain", base_iri, slug.upper(), concepts)
    zip_path = tmp_path / f"{slug}.zip"
    return zip_path, zip_bundle(k, zip_path)


@pytest.fixture
def federation(tmp_path):
    """Bundles a and b (a relates to b across the boundary), zipped, and a domain naming both."""
    a_iri, b_iri, d_iri = "https://a.example/knowledge/", "https://b.example/knowledge/", "https://d.example/federation/"
    a = make_bundle(tmp_path / "a", a_iri, "A", {"glossary/term.md": {"type": "GlossaryTerm", "title": "Term", "description": "A term.", "resource": "https://example.test/a", "relatedTo": [b_iri + "glossary/other"]}})
    b = make_bundle(tmp_path / "b", b_iri, "B", {"glossary/other.md": {"type": "GlossaryTerm", "title": "Other", "description": "Another term.", "resource": "https://example.test/b"}})
    a_zip, b_zip = tmp_path / "a.zip", tmp_path / "b.zip"
    a_sha, b_sha = zip_bundle(a, a_zip), zip_bundle(b, b_zip)
    host = make_domain(tmp_path / "host", d_iri, {"a": member("a", a_iri, a_zip, a_sha, d_iri + "domains/federation"), "b": member("b", b_iri, b_zip, b_sha, d_iri + "domains/federation")})
    return {"host": host, "a": a, "b": b, "a_zip": a_zip, "b_zip": b_zip, "a_sha": a_sha, "b_sha": b_sha, "a_iri": a_iri, "b_iri": b_iri, "d_iri": d_iri}


def graphs_in(nq: Path) -> set[str]:
    out = set()
    for line in nq.read_text(encoding="utf-8").splitlines():
        parts = line.rsplit(" ", 2)
        if len(parts) == 3 and parts[1].startswith("<"):
            out.add(parts[1][1:-1])
    return out


def test_a_build_locks_loads_gates_and_repeats(federation):
    host = federation["host"]
    r = federate(host, "build", "--tag", "v0.2.0", "--snapshot-iri", "https://d.example/snapshots/v0.2.0", "--no-attestation")
    assert r.rc == 0, r.out
    snap = host / "snapshot"
    lock = (snap / "workspace.lock.yaml").read_text(encoding="utf-8")
    assert lock.index(federation["a_iri"]) < lock.index(federation["b_iri"]), "members are locked in base_iri order"
    assert federation["a_sha"] in lock and federation["b_sha"] in lock
    registry = (snap / "lokf-registry.yaml").read_text(encoding="utf-8")
    assert "path:" not in registry and "file://" not in registry, "the registry carries no runner path, in `path` or in `source_base`"
    assert "knowledge-federate.py mcp" in (snap / "index.md").read_text(encoding="utf-8")
    assert graphs_in(snap / "graph.nq") == {federation["a_iri"], federation["b_iri"], federation["d_iri"], "https://d.example/snapshots/v0.2.0"}
    assert "0 typed-relation target(s) lie in no member's namespace" in (snap / "gate-report.md").read_text(encoding="utf-8")
    for name in ("index.md", "llms.txt", "registry.jsonld", "queries/labels.rq", "queries/unowned.rq", "export/a/graph.nt", "export/b/concepts.jsonld", "bundles/a/.lokf/knowledge/index.md", "bundles/domain/.lokf/knowledge/index.md"):
        assert (snap / name).is_file(), name
    first = (snap / "graph.nq").read_bytes(), (snap / "workspace.lock.yaml").read_bytes()
    r = federate(host, "build", "--tag", "v0.2.0", "--snapshot-iri", "https://d.example/snapshots/v0.2.0", "--no-attestation")
    assert r.rc == 0, r.out
    assert ((snap / "graph.nq").read_bytes(), (snap / "workspace.lock.yaml").read_bytes()) == first, "the same releases give the same bytes"


def test_a_cross_bundle_target_no_member_owns_fails_or_is_reported(federation, tmp_path):
    host = federation["host"]
    c_iri = "https://c.example/knowledge/"
    a2 = make_bundle(tmp_path / "a2", federation["a_iri"], "A", {"glossary/term.md": {"type": "GlossaryTerm", "title": "Term", "description": "A term.", "resource": "https://example.test/a", "relatedTo": [c_iri + "glossary/nowhere"]}})
    sha = zip_bundle(a2, federation["a_zip"])
    concept = host / ".lokf" / "knowledge" / "members" / "a.md"
    concept.write_text(concept.read_text(encoding="utf-8").replace(federation["a_sha"], sha), encoding="utf-8")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 1 and "lie in no member's namespace" in r.out and "glossary/nowhere" in r.out, r.out
    assert not (host / "snapshot").exists() and not (host / "snapshot.new").exists()
    top = host / ".lokf" / "knowledge" / "domains" / "federation.md"
    top.write_text(top.read_text(encoding="utf-8").replace("unowned_targets: fail", "unowned_targets: report"), encoding="utf-8")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0, r.out
    assert "1 typed-relation target(s) lie in no member's namespace" in (host / "snapshot" / "gate-report.md").read_text(encoding="utf-8")


def test_a_link_into_a_member_must_name_one_of_its_concepts(federation, tmp_path):
    """a's term relates to b's: the build counts that link, in the lock, the index and links.rq.

    A target in b's namespace that names no concept of b is held to the rule
    --check-refs applies inside one bundle: it stops the build under
    `unowned_targets: fail`, as a target no member owns does, and is
    reported under `report`.
    """
    host, a_iri, b_iri = federation["host"], federation["a_iri"], federation["b_iri"]
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0 and "1 link(s) between members" in r.out, r.out
    snap = host / "snapshot"
    lock = yaml.safe_load((snap / "workspace.lock.yaml").read_text(encoding="utf-8"))
    assert lock["links"] == [{"from": a_iri, "to": b_iri, "slot": "relatedTo", "count": 1}]
    assert "| A | B | `relatedTo` | 1 |" in (snap / "index.md").read_text(encoding="utf-8")
    r = federate(host, "query", "snapshot/queries/links.rq")
    assert r.rc == 0 and f"{a_iri}\t{b_iri}\thttp://purl.org/dc/terms/relation\t1" in r.out, r.out
    a2 = make_bundle(tmp_path / "a2", a_iri, "A", {"glossary/term.md": {"type": "GlossaryTerm", "title": "Term", "description": "A term.", "resource": "https://example.test/a", "relatedTo": [b_iri + "glossary/missing"]}})
    sha = zip_bundle(a2, federation["a_zip"])
    concept = host / ".lokf" / "knowledge" / "members" / "a.md"
    concept.write_text(concept.read_text(encoding="utf-8").replace(federation["a_sha"], sha), encoding="utf-8")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 1 and "1 typed-relation target(s) name no concept of the member whose namespace holds them and the domain's policy is fail" in r.out, r.out
    assert f"no such concept in {b_iri}: {a_iri}glossary/term relatedTo {b_iri}glossary/missing" in r.out, r.out
    top = host / ".lokf" / "knowledge" / "domains" / "federation.md"
    top.write_text(top.read_text(encoding="utf-8").replace("unowned_targets: fail", "unowned_targets: report"), encoding="utf-8")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0, r.out
    gate = (snap / "gate-report.md").read_text(encoding="utf-8")
    assert "1 typed-relation target(s) lie in a member's namespace and name no concept of that member" in gate and "glossary/missing" in gate, gate
    assert yaml.safe_load((snap / "workspace.lock.yaml").read_text(encoding="utf-8"))["links"] == []
    assert "No typed relation in one bundle names a concept of another yet." in (snap / "index.md").read_text(encoding="utf-8")


def test_a_reified_relation_is_gated_and_counted_as_a_named_one_is(federation, tmp_path):
    """a names b's concept in a reified `relations` entry: the lock and links.rq count the link. Named to an outside resource instead, it meets the gate."""
    host, a_iri, b_iri = federation["host"], federation["a_iri"], federation["b_iri"]

    def a_relates(target: str) -> None:
        a2 = make_bundle(tmp_path / "a2", a_iri, "A", {"glossary/term.md": {"type": "GlossaryTerm", "title": "Term", "description": "A term.", "resource": "https://example.test/a",
                                                                         "relations": [{"predicate": "dependsOn", "target": target}]}})
        sha = zip_bundle(a2, federation["a_zip"])
        concept = host / ".lokf" / "knowledge" / "members" / "a.md"
        text = concept.read_text(encoding="utf-8")
        concept.write_text(re.sub(r"sha256:[0-9a-f]{64}", f"sha256:{sha}", text, count=1), encoding="utf-8")

    a_relates(b_iri + "glossary/other")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0, r.out
    lock = yaml.safe_load((host / "snapshot" / "workspace.lock.yaml").read_text(encoding="utf-8"))
    assert lock["links"] == [{"from": a_iri, "to": b_iri, "slot": "dependsOn", "count": 1}], lock["links"]
    r = federate(host, "query", "snapshot/queries/links.rq")
    assert r.rc == 0 and f"{a_iri}\t{b_iri}\t" in r.out and r.out.rstrip().endswith("\t1"), r.out
    a_relates("https://nobody.example/thing")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 1 and "1 typed-relation target(s) lie in no member's namespace" in r.out and "dependsOn https://nobody.example/thing" in r.out, r.out
    top = host / ".lokf" / "knowledge" / "domains" / "federation.md"
    top.write_text(top.read_text(encoding="utf-8").replace("unowned_targets: fail", "unowned_targets: report"), encoding="utf-8")
    assert federate(host, "build", "--no-attestation").rc == 0
    r = federate(host, "query", "snapshot/queries/unowned.rq")
    assert r.rc == 0 and "https://nobody.example/thing" in r.out, r.out


def test_the_workspace_graph_json_draws_every_bundle_and_the_links_between_them(federation):
    """graph.json holds each bundle's concepts as lokf export draws them, each naming its bundle, and a's link into b as an edge marked cross."""
    host, a_iri, b_iri = federation["host"], federation["a_iri"], federation["b_iri"]
    review = host / ".lokf" / "knowledge" / "domains" / "federation.md"
    review.write_text(review.read_text(encoding="utf-8").replace("unowned_targets: fail", "unowned_targets: fail\nstale_after: '2027-04-18'"), encoding="utf-8")
    assert federate(host, "build", "--no-attestation").rc == 0
    graph = json.loads((host / "snapshot" / "graph.json").read_text(encoding="utf-8"))
    nodes = {n["data"]["id"]: n["data"] for n in graph["nodes"]}
    assert nodes[a_iri + "glossary/term"]["bundle"] == "a" and nodes[b_iri + "glossary/other"]["bundle"] == "b"
    assert nodes[federation["d_iri"] + "members/a"]["bundle"] == "domain" and nodes[federation["d_iri"] + "domains/federation"]["stale_after"] == "2027-04-18"
    assert not any("stale" in n for n in nodes.values()), "staleness is judged where the graph is drawn, from stale_after"
    cross = [e["data"] for e in graph["edges"] if e["data"].get("cross")]
    assert cross == [{"id": f"{a_iri}glossary/term dcterms:relation {b_iri}glossary/other", "source": f"{a_iri}glossary/term", "target": f"{b_iri}glossary/other",
                      "predicate": "dcterms:relation", "slot": "relatedTo", "reified": False, "cross": True}]
    assert all(e["data"]["source"] in nodes and e["data"]["target"] in nodes for e in graph["edges"]), "every edge joins two nodes, as cytoscape.js needs"
    assert [b["slug"] for b in graph["meta"]["bundles"]] == ["a", "b", "domain"] and graph["meta"]["bundles"][0]["title"] == "A"


def test_diff_says_what_changed_between_two_workspaces(federation, tmp_path):
    """b moves to v2.0.0 and a leaves: diff names both, and the link from a into b that left with it, from a lock, a folder or a zip."""
    host, b_iri = federation["host"], federation["b_iri"]
    assert federate(host, "build", "--tag", "v0.2.0", "--release-base", "https://github.com/acme/d/releases/tag", "--no-attestation").rc == 0
    old = tmp_path / "old"
    shutil.copytree(host / "snapshot", old)
    b2 = make_bundle(tmp_path / "b2", b_iri, "B", {"glossary/other.md": {"type": "GlossaryTerm", "title": "Other", "description": "Another term, revised.", "resource": "https://example.test/b"}})
    b2_zip = tmp_path / "b2.zip"
    rewrite(host, "b", member("b", b_iri, b2_zip, zip_bundle(b2, b2_zip), federation["d_iri"] + "domains/federation", version="v2.0.0"))
    (host / ".lokf" / "knowledge" / "members" / "a.md").unlink()
    assert federate(host, "build", "--tag", "v0.3.0", "--no-attestation").rc == 0
    expected = ["## The workspace", "", "Compared with the workspace of v0.2.0:", "",
                "- **b bundle** moved from v1.0.0 to v2.0.0.",
                "- **a bundle** left; the workspace held it at v1.0.0.",
                "- Links from **a bundle** to **b bundle**: 0, and 1 before."]
    zipped = tmp_path / "workspace-v0.2.0.zip"
    workspace_zip(old, zipped)
    for before in (old / "workspace.lock.yaml", old, zipped):
        r = federate(host, "diff", str(before), "snapshot", stdout_only=True)
        assert r.rc == 0 and r.out.splitlines() == expected, (before, r.out)
    r = federate(host, "diff", "snapshot", "snapshot", "--out", str(tmp_path / "same.md"))
    assert r.rc == 0 and (tmp_path / "same.md").read_text(encoding="utf-8") == "## The workspace\n\nNo member joined, moved or left since the workspace of urn:knowledge-federate:snapshot:v0.3.0.\n"
    shutil.copytree(host / "snapshot", tmp_path / "v0.3.0")
    top = host / ".lokf" / "knowledge" / "domains" / "federation.md"
    top.write_text(top.read_text(encoding="utf-8").replace("unowned_targets: fail", "unowned_targets: report"), encoding="utf-8")
    assert federate(host, "build", "--tag", "v0.4.0", "--no-attestation").rc == 0
    r = federate(host, "diff", str(tmp_path / "v0.3.0"), "snapshot", stdout_only=True)
    assert r.rc == 0 and r.out.splitlines()[-1] == "- The gate's policy is `report` now, and was `fail`.", r.out


def test_diff_says_who_joined_who_was_released_again_and_what_grew_sensitive(federation, tmp_path):
    """c joins, b's v1.0.0 is released again with other bytes, and a turns internal in a private repository: diff says each."""
    host, a_iri, b_iri, d_iri = federation["host"], federation["a_iri"], federation["b_iri"], federation["d_iri"]
    top = d_iri + "domains/federation"
    assert federate(host, "build", "--tag", "v0.2.0", "--release-base", "https://github.com/acme/d/releases/tag", "--no-attestation").rc == 0
    old = tmp_path / "old"
    shutil.copytree(host / "snapshot", old)
    c_iri = "https://c.example/knowledge/"
    c = make_bundle(tmp_path / "c", c_iri, "C", {"glossary/third.md": {"type": "GlossaryTerm", "title": "Third", "description": "A third term.", "resource": "https://example.test/c"}})
    c_zip = tmp_path / "c.zip"
    rewrite(host, "c", member("c", c_iri, c_zip, zip_bundle(c, c_zip), top))
    b2 = make_bundle(tmp_path / "b2", b_iri, "B", {"glossary/other.md": {"type": "GlossaryTerm", "title": "Other", "description": "Another term, rebuilt.", "resource": "https://example.test/b"}})
    b2_zip = tmp_path / "b2.zip"
    rewrite(host, "b", member("b", b_iri, b2_zip, zip_bundle(b2, b2_zip), top))
    rewrite(host, "a", {**member("a", a_iri, federation["a_zip"], federation["a_sha"], top), "sensitivity": "internal"})
    domain = host / ".lokf" / "knowledge" / "domains" / "federation.md"
    domain.write_text(domain.read_text(encoding="utf-8").replace("unowned_targets: fail", "unowned_targets: fail\nsensitivity: internal"), encoding="utf-8")
    assert federate(host, "build", "--tag", "v0.3.0", "--no-attestation", "--visibility", "private").rc == 0
    r = federate(host, "diff", str(old), "snapshot", stdout_only=True)
    assert r.rc == 0 and r.out.splitlines() == [
        "## The workspace", "", "Compared with the workspace of v0.2.0:", "",
        f"- **c bundle** joined at v1.0.0, in `{c_iri}`.",
        "- **a bundle** is internal now, and was public.",
        "- **b bundle** was released again at v1.0.0, with other bytes.",
        "- The workspace's sensitivity is `internal` now, and was `public`."], r.out


def export_bundle(knowledge: Path, out: Path) -> Path:
    """The four files lokf export writes for a bundle, in a folder, as the bundle's site serves them."""
    r = run(["uv", "run", "--project", REPO / ".lokf", "lokf", "export", knowledge, "--out-dir", out])
    assert r.rc == 0, r.out
    return out


def served_member(slug: str, base_iri: str, served: Path, domain_iri: str, version: str = "2026-10-01") -> dict:
    """A member concept naming the concepts.jsonld a bundle's site serves, with its checksum, as a person confirmed it."""
    return {"type": "MemberBundle", "title": f"{slug} bundle", "description": f"The {slug} bundle its site served on {version}.",
            "resource": served.parent.as_uri() + "/", "base_iri": base_iri, "version": version,
            "distribution": [{"name": served.name, "access_url": served.as_uri(), "media_type": "application/ld+json",
                              "checksum": "sha256:" + hashlib.sha256(served.read_bytes()).hexdigest()}],
            "isPartOf": [domain_iri], "verified": CONFIRMED}


def test_a_bundle_that_releases_no_zip_joins_by_the_file_its_site_serves(federation, tmp_path):
    """c releases no zip: its site serves the concepts.jsonld lokf export writes, which a person confirmed by its checksum.

    The build writes that file out as the bundle it was exported from and
    builds it as any member: c's link into a is counted, its graph is the
    one its own export gave, and the file is kept beside it. When the site
    serves another file since, the build stops, or, given the previous
    workspace, holds c as that file. A file that names another base_iri, a
    concept outside its namespace or a path that climbs out is refused.
    """
    host, a_iri, d_iri = federation["host"], federation["a_iri"], federation["d_iri"]
    c_iri, top = "https://c.example/knowledge/", d_iri + "domains/federation"
    c = make_bundle(tmp_path / "c", c_iri, "C", {"glossary/third.md": {"type": "GlossaryTerm", "title": "Third", "description": "A third term.",
                                                                        "resource": "https://example.test/c", "relatedTo": [a_iri + "glossary/term"]}})
    site = export_bundle(c, tmp_path / "site" / "knowledge")
    served = site / "concepts.jsonld"
    original = served.read_bytes()
    rewrite(host, "c", served_member("c", c_iri, served, top))
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0 and "c: 2026-10-01 checksum matches; a served file" in r.out, r.out
    snap = host / "snapshot"
    lock = yaml.safe_load((snap / "workspace.lock.yaml").read_text(encoding="utf-8"))
    entry = next(m for m in lock["members"] if m["slug"] == "c")
    assert entry["served"] == served.as_uri() and "zip" not in entry, entry
    assert (snap / "bundles" / "c" / ".lokf" / "concepts.jsonld").read_bytes() == original, "the file is kept beside the bundle it was written out as"
    third = (snap / "bundles" / "c" / ".lokf" / "knowledge" / "glossary" / "third.md").read_text(encoding="utf-8")
    assert yaml.safe_load(third.split("---", 2)[1])["relatedTo"] == [a_iri + "glossary/term"] and "A third term." in third
    assert {"from": c_iri, "to": a_iri, "slot": "relatedTo", "count": 1} in lock["links"], lock["links"]
    quads = next(g["quads"] for g in lock["graphs"] if g["graph"] == c_iri)
    assert quads == len((site / "graph.nt").read_text(encoding="utf-8").splitlines()), "the bundle written out gives the graph its own export gave"
    previous = tmp_path / "previous"
    shutil.copytree(snap, previous)
    served.write_text(served.read_text(encoding="utf-8").replace("A third term.", "A third term, revised."), encoding="utf-8")
    empty = ["--cache", str(tmp_path / "empty-cache")]
    r = federate(host, "build", "--no-attestation", *empty)
    assert r.rc == 1 and "c: " + served.as_uri() + " has sha256" in r.out, r.out
    r = federate(host, "build", "--no-attestation", *empty, "--previous", str(previous))
    assert r.rc == 0 and "c: held at its last good state" in r.out, r.out
    assert (snap / "bundles" / "c" / ".lokf" / "concepts.jsonld").read_bytes() == original
    assert "has sha256" in next(m for m in yaml.safe_load((snap / "workspace.lock.yaml").read_text(encoding="utf-8"))["members"] if m["slug"] == "c")["held"]
    rewrite(host, "c", served_member("c", c_iri, served, top, version="2026-10-02"))
    served.write_text(served.read_text(encoding="utf-8").replace("revised.", "revised again."), encoding="utf-8")
    r = federate(host, "build", "--no-attestation", *empty, "--previous", str(previous))
    assert r.rc == 0, "a served file changes as its site does, so it may be held at an earlier file: " + r.out
    entry = next(m for m in yaml.safe_load((snap / "workspace.lock.yaml").read_text(encoding="utf-8"))["members"] if m["slug"] == "c")
    assert entry["version"] == "2026-10-01" and entry["held"].startswith("its concept names 2026-10-02"), entry
    doc = json.loads(original)
    for fault, change, said in (
        ("base", lambda d: {**d, "@context": [d["@context"][0], {"@base": "https://elsewhere.example/knowledge/"}]},
         "says base_iri 'https://elsewhere.example/knowledge/' in its @context"),
        ("outside", lambda d: {**d, "@graph": [{**d["@graph"][0], "id": "https://elsewhere.example/x"}]}, "lies outside the base_iri"),
        ("climbs", lambda d: {**d, "@graph": [{**d["@graph"][0], "id": c_iri + "../../etc/passwd"}]}, "is no file a bundle can hold"),
        ("twice", lambda d: {**d, "@graph": [d["@graph"][0], d["@graph"][0]]}, "is no file a bundle can hold"),
        ("index", lambda d: {**d, "@graph": [{**d["@graph"][0], "id": c_iri + "index"}]}, "is no file a bundle can hold"),
        ("graph", lambda d: {k: v for k, v in d.items() if k != "@graph"}, "holds no @graph of concepts"),
        ("json", None, "is not JSON"),
    ):
        bad = write(tmp_path / f"bad-{fault}" / "concepts.jsonld", json.dumps(change(doc)) if change else "{ not json")
        rewrite(host, "c", served_member("c", c_iri, bad, top))
        r = federate(host, "build", "--no-attestation")
        assert r.rc == 1 and said in r.out, (fault, r.out)


def test_a_member_whose_release_cannot_be_fetched_is_held_at_its_last_good_state(federation, tmp_path):
    """b's zip is gone from where its concept names it: section 11.5 has an unreachable member degrade to its last good state.

    Without the previous workspace the build stops, as before. Given it, as
    a folder or as its zip, the build takes b as that workspace holds it,
    and the lock, the registry, the index and diff say so. When b's concept
    has since moved to a release that cannot be fetched either, b is held at
    the earlier release. A check reads the previous workspace as the build
    does, and a workspace of another domain is not taken.
    """
    host, a_iri, b_iri, d_iri = federation["host"], federation["a_iri"], federation["b_iri"], federation["d_iri"]
    assert federate(host, "build", "--tag", "v0.2.0", "--release-base", "https://github.com/acme/d/releases/tag", "--no-attestation").rc == 0
    previous = tmp_path / "previous"
    shutil.copytree(host / "snapshot", previous)
    zipped = tmp_path / "workspace-v0.2.0.zip"
    workspace_zip(previous, zipped)
    federation["b_zip"].unlink()
    empty = ["--cache", str(tmp_path / "empty-cache")]
    r = federate(host, "build", "--no-attestation", *empty)
    assert r.rc == 1 and "b.zip: no such file" in r.out and "keeps" not in r.out, r.out
    snap = host / "snapshot"
    for given in (previous, zipped):
        r = federate(host, "build", "--tag", "v0.3.0", "--no-attestation", *empty, "--previous", str(given))
        assert r.rc == 0 and "b: held at its last good state" in r.out, (given, r.out)
        lock = yaml.safe_load((snap / "workspace.lock.yaml").read_text(encoding="utf-8"))
        entry = next(m for m in lock["members"] if m["slug"] == "b")
        assert entry["version"] == "v1.0.0" and "b.zip: no such file" in entry["held"], entry
        assert {"from": a_iri, "to": b_iri, "slot": "relatedTo", "count": 1} in lock["links"]
        registry = {e["base_iri"]: e for e in yaml.safe_load((snap / "lokf-registry.yaml").read_text(encoding="utf-8"))["repos"]}
        assert registry[b_iri]["status"] == "last-good" and registry[a_iri].get("status", "ok") == "ok"
        index = (snap / "index.md").read_text(encoding="utf-8")
        assert "## Held at its last good state" in index and "- b bundle at v1.0.0: " in index, index
    r = federate(host, "diff", str(previous), "snapshot", stdout_only=True)
    assert r.rc == 0 and "- **b bundle** is held at its last good state, v1.0.0: " in r.out, r.out
    b2 = make_bundle(tmp_path / "b2", b_iri, "B", {"glossary/other.md": {"type": "GlossaryTerm", "title": "Other", "description": "Another term, revised.", "resource": "https://example.test/b"}})
    b2_zip = tmp_path / "b2.zip"
    rewrite(host, "b", member("b", b_iri, b2_zip, zip_bundle(b2, b2_zip), d_iri + "domains/federation", version="v2.0.0"))
    b2_zip.unlink()
    r = federate(host, "build", "--no-attestation", *empty, "--previous", str(previous))
    assert r.rc == 0, r.out
    entry = next(m for m in yaml.safe_load((snap / "workspace.lock.yaml").read_text(encoding="utf-8"))["members"] if m["slug"] == "b")
    assert entry["version"] == "v1.0.0" and entry["held"].startswith("its concept names v2.0.0, which could not be fetched: "), entry
    r = federate(host, "build", "--verify-only", "--no-attestation", *empty, "--previous", str(previous))
    assert r.rc == 0 and "b: held at its last good state" in r.out and "nothing written (--verify-only)" in r.out, r.out
    other = tmp_path / "other"
    shutil.copytree(previous, other)
    lock_file = other / "workspace.lock.yaml"
    lock_file.write_text(lock_file.read_text(encoding="utf-8").replace(f"domain_base_iri: {d_iri}", "domain_base_iri: https://other.example/federation/"), encoding="utf-8")
    r = federate(host, "build", "--no-attestation", *empty, "--previous", str(other))
    assert r.rc == 1 and "not a workspace of the domain under" in r.out and "b2.zip: no such file" in r.out, r.out


def test_a_release_zip_with_other_bytes_is_held_only_at_the_release_a_build_fetched(federation, tmp_path):
    """b's zip answers with other bytes: held when the previous workspace holds that very release, refused when it holds only an earlier one.

    The second case is a wrong checksum or a replaced asset, so the check
    and the build stop instead of building the earlier release unasked.
    """
    host, b_iri, d_iri = federation["host"], federation["b_iri"], federation["d_iri"]
    assert federate(host, "build", "--tag", "v0.2.0", "--no-attestation").rc == 0
    previous = tmp_path / "previous"
    shutil.copytree(host / "snapshot", previous)
    empty = ["--cache", str(tmp_path / "empty-cache")]
    federation["b_zip"].write_bytes(b"other bytes at the same address")
    r = federate(host, "build", "--no-attestation", *empty, "--previous", str(previous))
    assert r.rc == 0 and "b: held at its last good state" in r.out, r.out
    b2 = make_bundle(tmp_path / "b2", b_iri, "B", {"glossary/other.md": {"type": "GlossaryTerm", "title": "Other", "description": "Revised.", "resource": "https://example.test/b"}})
    b2_zip = tmp_path / "b2.zip"
    real = zip_bundle(b2, b2_zip)
    typo = ("0" if real[0] != "0" else "1") + real[1:]
    rewrite(host, "b", member("b", b_iri, b2_zip, typo, d_iri + "domains/federation", version="v2.0.0"))
    for check in ([], ["--verify-only"]):
        r = federate(host, "build", *check, "--no-attestation", *empty, "--previous", str(previous))
        assert r.rc == 1 and "the previous workspace holds it only at v1.0.0" in r.out and "held at its last good state" not in r.out, (check, r.out)


def test_a_check_holds_no_member_the_pull_request_proposes(federation, tmp_path):
    """A pull request moves b to a release that cannot be fetched: the check fails, though the previous workspace holds b, since a person is asked to confirm that release."""
    host, b_iri, d_iri = federation["host"], federation["b_iri"], federation["d_iri"]
    assert federate(host, "build", "--tag", "v0.2.0", "--no-attestation").rc == 0
    previous = tmp_path / "previous"
    shutil.copytree(host / "snapshot", previous)
    proposed = member("b", b_iri, tmp_path / "gone.zip", "a" * 64, d_iri + "domains/federation", version="v2.0.0")
    proposed["generated"] = {"by": "process:knowledge-federate", "at": "2026-02-01T00:00:00Z"}
    rewrite(host, "b", proposed)
    r = federate(host, "build", "--verify-only", "--no-attestation", "--previous", str(previous))
    assert r.rc == 1 and "gone.zip: no such file; a check holds no member the pull request proposes" in r.out, r.out


def test_a_member_no_previous_workspace_held_is_left_out_until_it_can_be_fetched(federation, tmp_path):
    """b joins after the release before, and its file cannot be fetched: there is no last good state, so the release builds without it and names it."""
    a_iri, b_iri, d_iri = federation["a_iri"], federation["b_iri"], federation["d_iri"]
    top = d_iri + "domains/federation"
    host = make_domain(tmp_path / "h2", d_iri, {"a": member("a", a_iri, federation["a_zip"], federation["a_sha"], top)}, policy="report")
    assert federate(host, "build", "--tag", "v0.2.0", "--no-attestation").rc == 0
    previous = tmp_path / "previous"
    shutil.copytree(host / "snapshot", previous)
    rewrite(host, "b", member("b", b_iri, federation["b_zip"], federation["b_sha"], top))
    federation["b_zip"].unlink()
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 1 and "b.zip: no such file" in r.out, "without a previous workspace nothing says b is new: " + r.out
    r = federate(host, "build", "--no-attestation", "--previous", str(previous))
    assert r.rc == 0 and "b: left out, because" in r.out, r.out
    snap = host / "snapshot"
    lock = yaml.safe_load((snap / "workspace.lock.yaml").read_text(encoding="utf-8"))
    assert [u["base_iri"] for u in lock["unfetched"]] == [b_iri] and b_iri not in {m["base_iri"] for m in lock["members"]}, lock
    assert "## Left out until its file can be fetched" in (snap / "index.md").read_text(encoding="utf-8")
    assert f"in the namespace of <{d_iri}members/b>, which could not be fetched" in (snap / "gate-report.md").read_text(encoding="utf-8")
    r = federate(host, "diff", str(previous), "snapshot", stdout_only=True)
    assert r.rc == 0 and f"- <{d_iri}members/b> is left out at v1.0.0, because its file could not be fetched" in r.out, r.out


def test_a_member_held_at_an_earlier_release_still_answers_a_second_domain_naming_its_new_one(federation, tmp_path):
    """Sub-domains s and t both move c to a release that cannot be fetched: c is held once at the release before, named by both, as the diamond rule has it."""
    host, top = federation["host"], federation["d_iri"] + "domains/federation"
    c_iri, s_iri, t_iri = "https://c.example/knowledge/", "https://s.example/federation/", "https://t.example/federation/"
    c = make_bundle(tmp_path / "c", c_iri, "C", {"glossary/third.md": {"type": "GlossaryTerm", "title": "Third", "description": "A third term.", "resource": "https://example.test/c"}})
    c_zip = tmp_path / "c.zip"
    c_sha = zip_bundle(c, c_zip)

    def name_c(zip_path: Path, sha: str, version: str = "v1.0.0") -> None:
        for slug, iri in (("s", s_iri), ("t", t_iri)):
            d_zip, d_sha = domain_zip(tmp_path, slug, iri, {"c": member("c", c_iri, zip_path, sha, iri + f"domains/{slug}", version=version)})
            write(host / ".lokf" / "knowledge" / "members" / f"{slug}.md", frontmatter(**member(slug, iri, d_zip, d_sha, top, kind="MemberDomain")) + f"\n# Overview\n\n{slug}.\n")

    name_c(c_zip, c_sha)
    assert federate(host, "build", "--no-attestation").rc == 0
    previous = tmp_path / "previous"
    shutil.copytree(host / "snapshot", previous)
    name_c(tmp_path / "c2.zip", "b" * 64, version="v2.0.0")
    r = federate(host, "build", "--no-attestation", "--previous", str(previous))
    assert r.rc == 0 and "c: held at its last good state" in r.out and "named by a second domain, not followed again" in r.out, r.out
    entry = next(m for m in yaml.safe_load((host / "snapshot" / "workspace.lock.yaml").read_text(encoding="utf-8"))["members"] if m["base_iri"] == c_iri)
    assert entry["version"] == "v1.0.0" and entry["member_of"] == [s_iri + "domains/s", t_iri + "domains/t"], entry


def test_a_member_whose_namespace_nests_with_another_is_refused_before_anything_is_fetched(federation, tmp_path):
    """c's namespace lies inside a's: the registry could route no IRI between them, so the build stops and names both, before it downloads c."""
    host, a_iri, d_iri = federation["host"], federation["a_iri"], federation["d_iri"]
    nested = a_iri + "sub/"
    c = make_bundle(tmp_path / "c", nested, "C", {"glossary/x.md": {"type": "GlossaryTerm", "title": "X", "description": "X.", "resource": "https://example.test/c"}})
    c_zip = tmp_path / "c.zip"
    rewrite(host, "c", member("c", nested, c_zip, zip_bundle(c, c_zip), d_iri + "domains/federation"))
    r = federate(host, "build", "--verify-only", "--no-attestation")
    assert r.rc == 1 and f"c: base_iri {nested} nests with {a_iri}, the namespace of a" in r.out, r.out
    assert "Traceback" not in r.out and "c: v1.0.0 checksum matches" not in r.out, r.out


def test_a_checksum_must_be_64_hex_digits(federation, tmp_path):
    """A checksum names the file in the cache, so one that climbs out of it is refused before it is used, and the file it names stays."""
    host, b_iri, d_iri = federation["host"], federation["b_iri"], federation["d_iri"]
    victim = tmp_path / "victim.zip"
    victim.write_bytes(b"kept")
    cache = tmp_path / "cache" / "federation"
    climb = "../../" + "./" * 26 + "victim"
    rewrite(host, "b", member("b", b_iri, federation["b_zip"], climb, d_iri + "domains/federation"))
    r = federate(host, "build", "--verify-only", "--no-attestation", "--cache", str(cache))
    assert r.rc == 1 and "distribution.checksum must be sha256:<64 hex digits>" in r.out, r.out
    assert victim.read_bytes() == b"kept"


@pytest.mark.parametrize("fault", ["checksum", "namespace", "symlink", "duplicate", "gitdir", "page", "name"])
def test_a_bad_member_stops_the_build_and_keeps_the_snapshot(federation, tmp_path, fault):
    host = federation["host"]
    assert federate(host, "build", "--no-attestation").rc == 0
    before = (host / "snapshot" / "graph.nq").read_bytes()
    concept = host / ".lokf" / "knowledge" / "members" / "b.md"
    text = concept.read_text(encoding="utf-8")
    if fault == "checksum":
        concept.write_text(text.replace(federation["b_sha"], "0" * 64), encoding="utf-8")
        expect = "has sha256"
    elif fault == "namespace":
        concept.write_text(text.replace("base_iri: https://b.example/knowledge/", "base_iri: https://b.example/other/"), encoding="utf-8")
        expect = "the zip's index.md says base_iri"
    elif fault == "symlink":
        sha = zip_bundle(federation["b"], federation["b_zip"], symlink=True)
        concept.write_text(text.replace(federation["b_sha"], sha), encoding="utf-8")
        expect = "symbolic link"
    elif fault == "gitdir":
        # git reads a .git folder in the unpacked member as a repository,
        # and its configuration can name a command git runs.
        marker = tmp_path / "ran"
        sha = zip_bundle(federation["b"], federation["b_zip"], extra={
            "knowledge/.git/HEAD": "ref: refs/heads/main\n",
            "knowledge/.git/config": f"[core]\n\trepositoryformatversion = 0\n\tfsmonitor = \"touch {marker}; false\"\n",
        })
        concept.write_text(text.replace(federation["b_sha"], sha), encoding="utf-8")
        expect = "is hidden"
    elif fault == "page":
        sha = zip_bundle(federation["b"], federation["b_zip"], extra={"knowledge/glossary/other.svg": "<svg onload='alert(1)'/>"})
        concept.write_text(text.replace(federation["b_sha"], sha), encoding="utf-8")
        expect = "a file a browser runs"
    elif fault == "name":
        concept.write_text(text.replace("name: b.zip", "name: ../../../.lokf/scripts/knowledge-report.sh"), encoding="utf-8")
        expect = "must be one plain file name"
    else:
        concept.write_text(text.replace("base_iri: https://b.example/knowledge/", "base_iri: https://a.example/knowledge/"), encoding="utf-8")
        expect = "already in the federation"
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 1 and expect in r.out, r.out
    assert (host / "snapshot" / "graph.nq").read_bytes() == before, "the previous snapshot stays"
    assert not (host / "snapshot.new").exists()
    assert not (tmp_path / "ran").exists(), "nothing in the member's zip ran"
    assert read(host / ".lokf" / "scripts" / "knowledge-report.sh") == read(SCRIPTS / "knowledge-report.sh"), "the host's report script is its own"


@needs_uv
def test_the_report_on_a_member_reads_no_git_configuration_from_it(tmp_path):
    """The member's folder holds what its zip held, so the health line runs git on no repository there."""
    member_root = tmp_path / "workspace" / "bundles" / "b"
    k = make_bundle(member_root / ".lokf", "https://b.example/knowledge/", "B", {})
    marker = tmp_path / "ran"
    write(k / ".git" / "HEAD", "ref: refs/heads/main\n")
    write(k / ".git" / "config", f"[core]\n\trepositoryformatversion = 0\n\tfsmonitor = \"touch {marker}; false\"\n")
    (k / ".git" / "objects").mkdir()
    (k / ".git" / "refs").mkdir()
    host = tmp_path / "host"
    write(host / ".lokf" / "scripts" / "knowledge-report.sh", read(SCRIPTS / "knowledge-report.sh"))
    Git(tmp_path).init()
    code = (
        "import importlib.util, pathlib, sys\n"
        f"spec = importlib.util.spec_from_file_location('kf', {str(SCRIPT)!r})\n"
        "kf = importlib.util.module_from_spec(spec); spec.loader.exec_module(kf)\n"
        f"print(kf.health_line(pathlib.Path({str(host)!r}), pathlib.Path({str(member_root)!r})))\n"
    )
    r = run(["uv", "run", "--project", REPO / ".lokf", "python", "-c", code], cwd=tmp_path)
    assert r.rc == 0 and "Confirmed by a person" in r.out, r.out
    assert not marker.exists(), "git ran the member's fsmonitor command"


def test_a_member_that_is_a_domain_is_followed(federation, tmp_path):
    host = federation["host"]
    c_iri, s_iri = "https://c.example/knowledge/", "https://s.example/federation/"
    c = make_bundle(tmp_path / "c", c_iri, "C", {"glossary/third.md": {"type": "GlossaryTerm", "title": "Third", "description": "A third term.", "resource": "https://example.test/c"}})
    c_zip = tmp_path / "c.zip"
    c_sha = zip_bundle(c, c_zip)
    sub = make_bundle(tmp_path / "s", s_iri, "S", {"domains/s.md": {"type": "Domain", "title": "Sub", "description": "A sub-domain.", "resource": "https://example.test/s"},
                                                  "members/c.md": member("c", c_iri, c_zip, c_sha, s_iri + "domains/s"),
                                                  "members/e.md": member("e", "https://e.example/knowledge/", c_zip, c_sha, s_iri + "domains/s", confirmed=False)})
    s_zip = tmp_path / "s.zip"
    s_sha = zip_bundle(sub, s_zip)
    write(host / ".lokf" / "knowledge" / "members" / "s.md", frontmatter(**member("s", s_iri, s_zip, s_sha, federation["d_iri"] + "domains/federation")) + "\n# Overview\n\nS.\n")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0, r.out
    lock = (host / "snapshot" / "workspace.lock.yaml").read_text(encoding="utf-8")
    entries = {m["base_iri"]: m for m in yaml.safe_load(lock)["members"]}
    assert entries[c_iri]["tier"] == 2 and entries[c_iri]["member_of"] == [s_iri + "domains/s"] and entries[s_iri]["kind"] == "domain"
    assert c_iri in graphs_in(host / "snapshot" / "graph.nq")
    assert "https://e.example/knowledge/" not in entries, "a member domain's member no person confirmed is left out"
    assert yaml.safe_load(lock)["waiting"] == [{"concept": s_iri + "members/e", "base_iri": "https://e.example/knowledge/", "proposed": "v1.0.0", "built": None}]
    assert "that domain's release, whose zip holds no history" in r.out and "and that domain releases again" in r.out, r.out


def test_a_bundle_two_domains_name_at_one_release_joins_once(federation, tmp_path):
    """The diamond rule: sub-domains s and t both name c at one zip, so c joins once under both; t naming another release of c stops the build."""
    host, top = federation["host"], federation["d_iri"] + "domains/federation"
    c_iri, s_iri, t_iri = "https://c.example/knowledge/", "https://s.example/federation/", "https://t.example/federation/"
    c = make_bundle(tmp_path / "c", c_iri, "C", {"glossary/third.md": {"type": "GlossaryTerm", "title": "Third", "description": "A third term.", "resource": "https://example.test/c"}})
    c_zip = tmp_path / "c.zip"
    c_sha = zip_bundle(c, c_zip)
    s_zip, s_sha = domain_zip(tmp_path, "s", s_iri, {"c": member("c", c_iri, c_zip, c_sha, s_iri + "domains/s")})
    t_zip, t_sha = domain_zip(tmp_path, "t", t_iri, {"c": member("c", c_iri, c_zip, c_sha, t_iri + "domains/t")})
    write(host / ".lokf" / "knowledge" / "members" / "s.md", frontmatter(**member("s", s_iri, s_zip, s_sha, top, kind="MemberDomain")) + "\n# Overview\n\nS.\n")
    write(host / ".lokf" / "knowledge" / "members" / "t.md", frontmatter(**member("t", t_iri, t_zip, t_sha, top)) + "\n# Overview\n\nT.\n")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0 and "named by a second domain, not followed again" in r.out, r.out
    snapshot_before = (host / "snapshot" / "graph.nq").read_bytes()
    t_bad, t_bad_sha = domain_zip(tmp_path, "t", t_iri, {"c": {**member("c", c_iri, c_zip, c_sha, t_iri + "domains/t"), "sensitivity": "secret"}})
    write(host / ".lokf" / "knowledge" / "members" / "t.md", frontmatter(**member("t", t_iri, t_bad, t_bad_sha, top)) + "\n# Overview\n\nT.\n")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 1 and "c: sensitivity must be public, internal or confidential, not 'secret'" in r.out, "the second domain's word is checked too: " + r.out
    assert (host / "snapshot" / "graph.nq").read_bytes() == snapshot_before
    lock = yaml.safe_load((host / "snapshot" / "workspace.lock.yaml").read_text(encoding="utf-8"))
    entries = [m for m in lock["members"] if m["base_iri"] == c_iri]
    assert len(entries) == 1 and entries[0]["member_of"] == [s_iri + "domains/s", t_iri + "domains/t"] and entries[0]["kind"] == "bundle"
    kinds = {m["base_iri"]: m["kind"] for m in lock["members"]}
    assert kinds[s_iri] == "domain" and kinds[t_iri] == "domain", "a MemberBundle whose zip is a domain is a domain in the lock, as a MemberDomain is"
    nq = (host / "snapshot" / "graph.nq").read_text(encoding="utf-8")
    assert f"<{s_iri}domains/s> <http://www.w3.org/ns/dcat#dataset> <{c_iri}>" in nq and f"<{top}> <http://www.w3.org/ns/dcat#catalog> <{s_iri}>" in nq
    index = (host / "snapshot" / "index.md").read_text(encoding="utf-8")
    assert "| [S (a domain)](bundles/s/" in index and "| S, T |" in index, index
    before = (host / "snapshot" / "graph.nq").read_bytes()
    c2 = make_bundle(tmp_path / "c2", c_iri, "C", {"glossary/fourth.md": {"type": "GlossaryTerm", "title": "Fourth", "description": "A fourth term.", "resource": "https://example.test/c"}})
    c2_zip = tmp_path / "c2.zip"
    c2_sha = zip_bundle(c2, c2_zip)
    t_zip, t_sha = domain_zip(tmp_path, "t", t_iri, {"c": member("c", c_iri, c2_zip, c2_sha, t_iri + "domains/t", version="v2.0.0")})
    write(host / ".lokf" / "knowledge" / "members" / "t.md", frontmatter(**member("t", t_iri, t_zip, t_sha, top)) + "\n# Overview\n\nT.\n")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 1 and "a bundle joins once, at one release" in r.out and "v2.0.0" in r.out, r.out
    assert (host / "snapshot" / "graph.nq").read_bytes() == before, "the previous snapshot stays"


def test_the_depth_a_build_follows_is_the_domain_s_to_set(federation, tmp_path):
    """Domains t1 > t2 > t3 > a leaf: the default depth of 3 stops at t3, max_depth: 4 on the top Domain concept follows it, and a depth below 1 is refused."""
    host, top = federation["host"], federation["d_iri"] + "domains/federation"
    leaf_iri = "https://leaf.example/knowledge/"
    leaf = make_bundle(tmp_path / "leaf", leaf_iri, "Leaf", {"glossary/l.md": {"type": "GlossaryTerm", "title": "L", "description": "A leaf term.", "resource": "https://example.test/l"}})
    leaf_zip = tmp_path / "leaf.zip"
    zip_path, sha, inner = leaf_zip, zip_bundle(leaf, leaf_zip), leaf_iri
    for slug in ("t3", "t2", "t1"):  # from the bottom up: t3 names the leaf, t2 names t3, t1 names t2, each as members/inner.md
        iri = f"https://{slug}.example/federation/"
        zip_path, sha = domain_zip(tmp_path, slug, iri, {"inner": member("inner", inner, zip_path, sha, iri + f"domains/{slug}")})
        inner = iri
    write(host / ".lokf" / "knowledge" / "members" / "t1.md", frontmatter(**member("t1", inner, zip_path, sha, top, kind="MemberDomain")) + "\n# Overview\n\nT1.\n")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 1 and "a domain at tier 3, and this domain's max_depth is 3" in r.out, r.out
    assert not (host / "snapshot").exists()
    top_md = host / ".lokf" / "knowledge" / "domains" / "federation.md"
    top_md.write_text(top_md.read_text(encoding="utf-8").replace("unowned_targets: fail", "unowned_targets: fail\nmax_depth: 4"), encoding="utf-8")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0, r.out
    lock = yaml.safe_load((host / "snapshot" / "workspace.lock.yaml").read_text(encoding="utf-8"))
    tiers = {m["base_iri"]: (m["tier"], m["slug"]) for m in lock["members"]}
    assert tiers[leaf_iri] == (4, "inner-3") and tiers["https://t3.example/federation/"] == (3, "inner-2") and tiers["https://t1.example/federation/"] == (1, "t1"), tiers
    assert (host / "snapshot" / "export" / "inner-3" / "graph.nt").is_file(), "three members named inner.md keep folders of their own"
    top_md.write_text(top_md.read_text(encoding="utf-8").replace("max_depth: 4", "max_depth: 0"), encoding="utf-8")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 1 and "max_depth must be a whole number of tiers" in r.out, r.out


def test_a_member_declared_a_domain_must_hold_one(federation):
    host = federation["host"]
    concept = host / ".lokf" / "knowledge" / "members" / "b.md"
    concept.write_text(concept.read_text(encoding="utf-8").replace("type: MemberBundle", "type: MemberDomain"), encoding="utf-8")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 1 and "the concept is a MemberDomain, but the zip holds no concept of type Domain" in r.out, r.out


def test_a_retired_domain_concept_is_not_a_second_top(federation):
    """A renamed domain keeps its old concept, retired, beside the new one."""
    host = federation["host"]
    old = {"type": "Domain", "title": "The old domain", "description": "The domain before its rename.", "resource": "https://example.test/d", "status": "deprecated"}
    write(host / ".lokf" / "knowledge" / "domains" / "old.md", frontmatter(**old) + "\n# Overview\n\nRetired.\n")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0 and "domains/old: retired" in r.out, r.out
    lock = yaml.safe_load((host / "snapshot" / "workspace.lock.yaml").read_text(encoding="utf-8"))
    assert lock["domain"] == federation["d_iri"] + "domains/federation"


def test_a_retired_member_is_left_out_of_the_workspace(federation):
    host = federation["host"]
    concept = host / ".lokf" / "knowledge" / "members" / "a.md"
    concept.write_text(concept.read_text(encoding="utf-8").replace("type: MemberBundle\n", "type: MemberBundle\nstatus: deprecated\n"), encoding="utf-8")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0 and "members/a: retired" in r.out, r.out
    lock = yaml.safe_load((host / "snapshot" / "workspace.lock.yaml").read_text(encoding="utf-8"))
    assert [m["base_iri"] for m in lock["members"]] == [federation["b_iri"]], "the retired member is not in the lock"
    assert federation["a_iri"] not in graphs_in(host / "snapshot" / "graph.nq") and not (host / "snapshot" / "bundles" / "a").exists()


def test_a_member_no_person_confirmed_waits_outside_the_workspace(federation):
    """A merged pull request that adds a member admits nothing until a person confirms it."""
    host = federation["host"]
    write(host / ".lokf" / "knowledge" / "members" / "a.md",
          frontmatter(**member("a", federation["a_iri"], federation["a_zip"], federation["a_sha"], federation["d_iri"] + "domains/federation", confirmed=False)) + "\n# Overview\n\na.\n")
    r = federate(host, "build", "--verify-only", "--no-attestation")
    assert r.rc == 0 and "a: v1.0.0" in r.out, "--verify-only checks the zip a person is asked to confirm\n" + r.out
    assert "the next release build would take this domain's members as follows:" in r.out and "members/a: left out, because no person has confirmed it" in r.out, \
        "the check says what the next release build would leave out\n" + r.out
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0 and "members/a: left out, because no person has confirmed it" in r.out, r.out
    lock = yaml.safe_load((host / "snapshot" / "workspace.lock.yaml").read_text(encoding="utf-8"))
    assert [m["base_iri"] for m in lock["members"]] == [federation["b_iri"]]
    assert lock["waiting"] == [{"concept": federation["d_iri"] + "members/a", "base_iri": federation["a_iri"], "proposed": "v1.0.0", "built": None}]
    assert federation["a_iri"] not in graphs_in(host / "snapshot" / "graph.nq")
    index = (host / "snapshot" / "index.md").read_text(encoding="utf-8")
    assert "## Waiting for a person" in index and "members/a>: v1.0.0 waits; left out." in index, index


def test_a_moved_member_is_built_at_the_release_a_person_confirmed(federation, tmp_path):
    """The members librarian's move, merged, waits for a person; git history holds the release they confirmed."""
    host = federation["host"]
    git = Git(host)
    git.init()
    git("add", "-A")
    git("commit", "-qm", "the members as a person confirmed them")
    b2 = make_bundle(tmp_path / "b2", federation["b_iri"], "B", {"glossary/other.md": {"type": "GlossaryTerm", "title": "Other", "description": "Another term, revised.", "resource": "https://example.test/b"}})
    b2_zip = tmp_path / "b2.zip"
    b2_sha = zip_bundle(b2, b2_zip)
    moved = member("b", federation["b_iri"], b2_zip, b2_sha, federation["d_iri"] + "domains/federation", version="v2.0.0")
    moved["generated"] = {"by": "process:knowledge-federate", "at": "2026-02-01T00:00:00Z"}
    concept = host / ".lokf" / "knowledge" / "members" / "b.md"
    write(concept, frontmatter(**moved) + "\n# Overview\n\nb at v2.0.0.\n")
    git("commit", "-qam", "move b to v2.0.0")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0 and "members/b: v2.0.0 waits for a person's confirmation; built at v1.0.0, as a person confirmed it at commit" in r.out, r.out
    lock = yaml.safe_load((host / "snapshot" / "workspace.lock.yaml").read_text(encoding="utf-8"))
    entries = {m["base_iri"]: m for m in lock["members"]}
    assert entries[federation["b_iri"]]["version"] == "v1.0.0" and entries[federation["b_iri"]]["sha256"] == federation["b_sha"]
    assert lock["waiting"] == [{"concept": federation["d_iri"] + "members/b", "base_iri": federation["b_iri"], "proposed": "v2.0.0", "built": "v1.0.0"}]
    assert "members/b>: v2.0.0 waits; built at v1.0.0." in (host / "snapshot" / "index.md").read_text(encoding="utf-8")
    shutil.rmtree(host / ".lokf" / ".cache")
    federation["b_zip"].unlink()
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 1 and "no such file" in r.out and "b is built at v1.0.0, the release a person last confirmed, and its concept now names v2.0.0, which joins once a person confirms it" in r.out, \
        "a release a person confirmed that is gone says what waits\n" + r.out
    moved["verified"] = [*CONFIRMED, {"by": "human:noel", "at": "2026-02-02T00:00:00Z"}]
    write(concept, frontmatter(**moved) + "\n# Overview\n\nb at v2.0.0.\n")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0, r.out
    lock = yaml.safe_load((host / "snapshot" / "workspace.lock.yaml").read_text(encoding="utf-8"))
    assert {m["base_iri"]: m["sha256"] for m in lock["members"]}[federation["b_iri"]] == b2_sha and "waiting" not in lock, "a person's confirmation admits the move"


def rewrite(host: Path, slug: str, fm: dict, body: str = "") -> Path:
    """A member concept written again with this frontmatter."""
    return write(host / ".lokf" / "knowledge" / "members" / f"{slug}.md", frontmatter(**fm) + f"\n# Overview\n\n{slug}.\n{body}")


def committed(host: Path, env: dict | None = None) -> Git:
    """The host as a git repository with everything committed, as a person confirmed it."""
    git = Git(host)
    git.init()
    git("add", "-A")
    git("commit", "-qm", "the members as a person confirmed them", env=env)
    return git


def dated(day: int) -> dict:
    """A commit's dates, one day apart, so the order by date is the order of the steps, as it is outside a test."""
    stamp = f"2026-01-{day:02d}T12:00:00Z"
    return {"GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp}


def a_moved(federation, version: str, at: str, **extra) -> dict:
    """Member a's concept moved to `version` by the pen at `at`: its zip label changed, a person's event kept."""
    moved = member("a", federation["a_iri"], federation["a_zip"], federation["a_sha"], federation["d_iri"] + "domains/federation", version=version)
    moved["generated"] = {"by": "process:knowledge-federate", "at": at}
    moved.update(extra)
    return moved


def built_a(host: Path):
    lock = yaml.safe_load((host / "snapshot" / "workspace.lock.yaml").read_text(encoding="utf-8"))
    return {m["base_iri"]: m["version"] for m in lock["members"]}, lock.get("waiting")


def test_a_confirmation_its_person_removed_counts_for_no_earlier_release(federation):
    host = federation["host"]
    git = committed(host)
    rewrite(host, "a", a_moved(federation, "v2.0.0", "2026-02-01T00:00:00Z"))
    git("commit", "-qam", "move a to v2.0.0")
    withdrawn = a_moved(federation, "v2.0.0", "2026-02-01T00:00:00Z")
    withdrawn.pop("verified")
    rewrite(host, "a", withdrawn)
    git("commit", "-qam", "the person removes their confirmation")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0 and "members/a: left out, because the person who confirmed an earlier text has removed that confirmation" in r.out, r.out
    versions, waiting = built_a(host)
    assert federation["a_iri"] not in versions and waiting[0]["built"] is None


def test_a_renamed_concept_waits_for_a_confirmation_of_its_own(federation):
    """A confirmation belongs to the concept it names: a new path is a new concept."""
    host = federation["host"]
    git = committed(host)
    git("mv", ".lokf/knowledge/members/a.md", ".lokf/knowledge/members/a-renamed.md")
    rewrite(host, "a-renamed", member("a", federation["a_iri"], federation["a_zip"], federation["a_sha"], federation["d_iri"] + "domains/federation", confirmed=False))
    git("add", "-A")
    git("commit", "-qm", "rename a; its confirmation stays with the old IRI")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0 and "members/a-renamed: left out, because no person has confirmed it;" in r.out, r.out
    assert federation["a_iri"] not in built_a(host)[0]


def test_an_id_changed_in_place_waits_for_a_confirmation_of_its_own(federation):
    host = federation["host"]
    git = committed(host)
    rewrite(host, "a", a_moved(federation, "v1.0.0", "2026-02-01T00:00:00Z", id=federation["d_iri"] + "members/another"))
    git("commit", "-qam", "a given another id")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0 and "members/another: left out, because no person has confirmed it;" in r.out, r.out
    assert federation["a_iri"] not in built_a(host)[0]


def test_a_retirement_undone_without_a_confirmation_keeps_the_member_out(federation):
    host = federation["host"]
    git = committed(host)
    rewrite(host, "a", {**member("a", federation["a_iri"], federation["a_zip"], federation["a_sha"], federation["d_iri"] + "domains/federation"), "status": "deprecated"})
    git("commit", "-qam", "a retired")
    rewrite(host, "a", a_moved(federation, "v1.0.0", "2026-02-01T00:00:00Z"))
    git("commit", "-qam", "a brought back by an edit no person confirmed")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0 and "members/a: left out, because no person has confirmed it;" in r.out, r.out
    assert federation["a_iri"] not in built_a(host)[0]


def test_a_text_that_only_stood_on_a_side_branch_is_not_built(federation):
    """With a merge commit, the walk reads the states the default branch held, not a branch's steps on the way."""
    host = federation["host"]
    git = committed(host, dated(1))
    git("switch", "-q", "-c", "side")
    rewrite(host, "a", a_moved(federation, "v2.0.0", "2026-02-01T00:00:00Z", verified=[*CONFIRMED, {"by": "human:noel", "at": "2026-02-02T00:00:00Z"}]))
    git("commit", "-qam", "side: a moved to v2.0.0 and confirmed", env=dated(2))
    rewrite(host, "a", a_moved(federation, "v3.0.0", "2026-02-03T00:00:00Z", verified=[*CONFIRMED, {"by": "human:noel", "at": "2026-02-02T00:00:00Z"}]))
    git("commit", "-qam", "side: a moved again, to v3.0.0", env=dated(3))
    git("switch", "-q", "main")
    git("merge", "-q", "--no-ff", "side", "-m", "merge side", env=dated(4))
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0 and "members/a: v3.0.0 waits for a person's confirmation; built at v1.0.0" in r.out, r.out
    assert built_a(host)[0][federation["a_iri"]] == "v1.0.0"


def test_a_member_a_person_sent_back_stays_at_the_release_they_confirmed(federation):
    """A send-back adds a question and keeps the person's event, so the member stays; retiring it is what takes it out."""
    host = federation["host"]
    sent_back = {**member("a", federation["a_iri"], federation["a_zip"], federation["a_sha"], federation["d_iri"] + "domains/federation"), "status": "draft"}
    rewrite(host, "a", sent_back, "\n## Open questions\n\n- 2026-02-01, human:noel: is this the right release?\n")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0, r.out
    versions, waiting = built_a(host)
    assert versions[federation["a_iri"]] == "v1.0.0" and waiting is None


def test_the_domain_s_settings_count_only_as_a_person_confirmed_them(federation, tmp_path):
    host = federation["host"]
    a2 = make_bundle(tmp_path / "a2", federation["a_iri"], "A", {"glossary/term.md": {"type": "GlossaryTerm", "title": "Term", "description": "A term.", "resource": "https://example.test/a", "relatedTo": ["https://c.example/knowledge/glossary/nowhere"]}})
    sha = zip_bundle(a2, federation["a_zip"])
    concept = host / ".lokf" / "knowledge" / "members" / "a.md"
    concept.write_text(concept.read_text(encoding="utf-8").replace(federation["a_sha"], sha), encoding="utf-8")
    top = host / ".lokf" / "knowledge" / "domains" / "federation.md"
    edited = top.read_text(encoding="utf-8").replace("unowned_targets: fail", "unowned_targets: report\ngenerated:\n  by: process:ktl-librarian\n  at: '2026-02-01T00:00:00Z'")
    top.write_text(edited, encoding="utf-8")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 1 and "its unowned_targets, max_depth and sensitivity wait for a person's confirmation" in r.out and "the build uses the defaults, fail, 3 and public" in r.out, r.out
    top.write_text(edited.replace("verified:\n", "verified:\n- by: human:noel\n  at: '2026-02-02T00:00:00Z'\n"), encoding="utf-8")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0 and "1 typed-relation target(s) lie in no member's namespace." in (host / "snapshot" / "gate-report.md").read_text(encoding="utf-8"), r.out


def test_a_member_joins_only_at_the_sensitivity_its_domain_cleared(federation):
    """Section 11.5's gate: b says it is internal.

    It joins only once a person has confirmed `sensitivity: internal` on the
    Domain concept, and only in a private or internal repository, since the
    release that carries the workspace is as public as the repository; an
    unknown visibility counts as public. A confidential bundle joins no
    workspace, and a Domain concept clears public or internal alone.
    """
    host, b_iri = federation["host"], federation["b_iri"]
    concept = host / ".lokf" / "knowledge" / "members" / "b.md"
    concept.write_text(concept.read_text(encoding="utf-8").replace("version: v1.0.0", "version: v1.0.0\nsensitivity: internal"), encoding="utf-8")
    r = federate(host, "build", "--no-attestation", "--visibility", "private")
    assert r.rc == 1 and "b: its sensitivity is internal, and the domain has cleared public only" in r.out, r.out
    top = host / ".lokf" / "knowledge" / "domains" / "federation.md"
    top.write_text(top.read_text(encoding="utf-8").replace("unowned_targets: fail", "unowned_targets: fail\nsensitivity: internal"), encoding="utf-8")
    for visibility, said in (("public", "this repository is public"), ("unknown", "this repository has an unknown visibility, which counts as public")):
        r = federate(host, "build", "--no-attestation", "--visibility", visibility)
        assert r.rc == 1 and f"b: its sensitivity is internal, and {said}" in r.out, r.out
    r = federate(host, "build", "--no-attestation", "--visibility", "private")
    assert r.rc == 0 and "sensitivity=internal" in r.out, r.out
    snap = host / "snapshot"
    lock = yaml.safe_load((snap / "workspace.lock.yaml").read_text(encoding="utf-8"))
    assert lock["sensitivity"] == "internal" and {m["slug"]: m["sensitivity"] for m in lock["members"]} == {"a": "public", "b": "internal"}
    registry = {e["base_iri"]: e.get("sensitivity") for e in yaml.safe_load((snap / "lokf-registry.yaml").read_text(encoding="utf-8"))["repos"]}
    assert registry[b_iri] == "internal" and registry[federation["a_iri"]] == "public", registry
    assert "It holds internal metadata, which a person cleared on the Domain concept" in (snap / "index.md").read_text(encoding="utf-8")
    concept.write_text(concept.read_text(encoding="utf-8").replace("sensitivity: internal", "sensitivity: confidential"), encoding="utf-8")
    r = federate(host, "build", "--no-attestation", "--visibility", "private")
    assert r.rc == 1 and "b: its sensitivity is confidential, and a confidential bundle joins no workspace" in r.out, r.out
    top.write_text(top.read_text(encoding="utf-8").replace("sensitivity: internal", "sensitivity: confidential"), encoding="utf-8")
    r = federate(host, "build", "--no-attestation", "--visibility", "private")
    assert r.rc == 1 and "sensitivity on the Domain concept is the most sensitive member its workspace may hold, public or internal" in r.out, r.out


def test_a_sensitivity_raised_as_it_stands_counts_before_a_person_confirms_it(federation):
    """b's concept, edited since a person confirmed it, now says internal: b is built at the text confirmed, but as internal at once. A clearance lowered on the Domain concept counts at once too."""
    host = federation["host"]
    knowledge = host / ".lokf" / "knowledge"
    edited = "generated:\n  by: process:knowledge-federate\n  at: '2026-02-01T00:00:00Z'\n"
    git = committed(host)
    b = knowledge / "members" / "b.md"
    b.write_text(b.read_text(encoding="utf-8").replace("version: v1.0.0\n", "version: v1.0.0\nsensitivity: internal\n" + edited), encoding="utf-8")
    r = federate(host, "build", "--no-attestation", "--visibility", "private")
    assert r.rc == 1 and "b: its concept as it stands says sensitivity internal, which counts at once" in r.out, r.out
    assert "b: its sensitivity is internal, and the domain has cleared public only" in r.out, r.out
    b.write_text(b.read_text(encoding="utf-8").replace(edited, ""), encoding="utf-8")
    top = knowledge / "domains" / "federation.md"
    top.write_text(top.read_text(encoding="utf-8").replace("unowned_targets: fail\n", "unowned_targets: fail\nsensitivity: internal\n"), encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "b is internal, and the domain clears internal")
    assert federate(host, "build", "--no-attestation", "--visibility", "private").rc == 0
    top.write_text(top.read_text(encoding="utf-8").replace("sensitivity: internal\n", "sensitivity: public\n" + edited), encoding="utf-8")
    r = federate(host, "build", "--no-attestation", "--visibility", "private")
    assert r.rc == 1 and "its sensitivity as it stands, public, clears less than the internal a person confirmed" in r.out, r.out


def test_the_domain_schema_clears_public_or_internal_alone(tmp_path):
    """domain.yaml lets a member say confidential, and a Domain concept clear public or internal alone, as the build reads them."""
    found = run(["uv", "run", "--project", REPO / ".lokf", "python", "-c", "import lokf, pathlib; print(next(pathlib.Path(lokf.__file__).parent.rglob('lokf.yaml')))"],
                stdout_only=True)
    shutil.copy(found.out.strip(), tmp_path / "lokf.yaml")
    shutil.copy(TEMPLATES / "domain.yaml", tmp_path / "domain.yaml")
    for word, rc in (("public", 0), ("internal", 0), ("confidential", 1)):
        k = make_bundle(tmp_path / word, "https://d.example/federation/", "D", {"domains/top.md": {"type": "Domain", "title": "Top", "description": "The domain.", "resource": "https://example.test/d", "sensitivity": word}})
        r = run(["uv", "run", "--project", REPO / ".lokf", "lokf", "validate", "--schema", "domain.yaml", str(k)], cwd=tmp_path)
        assert r.rc == rc, (word, r.out)


def test_the_gate_names_a_member_that_waits_when_a_link_lies_in_its_namespace(federation):
    """a links into b's namespace; b is proposed and not yet confirmed, so the link is unowned, and the error says what admits it.

    The check finds the same before the merge, although it verifies b's zip
    as it stands, because its gate judges the workspace the next release
    build would make.
    """
    host = federation["host"]
    rewrite(host, "b", member("b", federation["b_iri"], federation["b_zip"], federation["b_sha"], federation["d_iri"] + "domains/federation", confirmed=False))
    waiting_b = f"<{federation['d_iri']}members/b>"
    for args in (("--verify-only",), ()):
        r = federate(host, "build", *args, "--no-attestation")
        assert r.rc == 1 and f"in the namespace of {waiting_b}, which waits for a person's confirmation" in r.out, (args, r.out)
        assert f"1 of them lie in the namespace of {waiting_b}, which joins once a person confirms it" in r.out, (args, r.out)
    assert not (host / "snapshot").exists() and not (host / "snapshot.new").exists()


def test_verify_only_meets_the_gate_before_the_merge(federation, tmp_path):
    """a's new release links to a namespace no member owns: the pull request's check fails, as the release build after the merge would."""
    host = federation["host"]
    a2 = make_bundle(tmp_path / "a2", federation["a_iri"], "A", {"glossary/term.md": {"type": "GlossaryTerm", "title": "Term", "description": "A term.", "resource": "https://example.test/a", "relatedTo": ["https://c.example/knowledge/glossary/nowhere"]}})
    sha = zip_bundle(a2, federation["a_zip"])
    concept = host / ".lokf" / "knowledge" / "members" / "a.md"
    concept.write_text(concept.read_text(encoding="utf-8").replace(federation["a_sha"], sha), encoding="utf-8")
    r = federate(host, "build", "--verify-only", "--no-attestation")
    assert r.rc == 1 and "glossary/nowhere" in r.out and "lie in no member's namespace and the domain's policy is fail; nothing written (--verify-only)" in r.out, r.out
    assert not (host / "snapshot").exists() and not (host / "snapshot.new").exists()
    top = host / ".lokf" / "knowledge" / "domains" / "federation.md"
    top.write_text(top.read_text(encoding="utf-8").replace("unowned_targets: fail", "unowned_targets: report"), encoding="utf-8")
    r = federate(host, "build", "--verify-only", "--no-attestation")
    assert r.rc == 0 and "glossary/nowhere, reported under unowned_targets: report" in r.out, r.out
    assert "gated 3 bundles as the next release build would take them: 1 typed-relation target(s) in no member's namespace; nothing written" in r.out, r.out
    assert not (host / "snapshot").exists()


def workspace_zip(snapshot: Path, zip_path: Path, lock: dict | None = None) -> str:
    """A domain's snapshot packed as its release's workspace zip, under workspace/, with another lock in it when given. Returns the sha256."""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(snapshot.rglob("*")):
            if p.is_file():
                rel = p.relative_to(snapshot).as_posix()
                zf.writestr("workspace/" + rel, yaml.safe_dump(lock, sort_keys=False) if lock is not None and rel == "workspace.lock.yaml" else p.read_bytes())
    return hashlib.sha256(zip_path.read_bytes()).hexdigest()


def test_a_member_that_waits_in_a_member_domain_joins_as_that_domain_built_it(federation, tmp_path):
    """Sub-domain s confirmed c at v1.0.0 and has since moved it to v2.0.0, which no person confirmed.

    s's own build took c at v1.0.0, from its git history. s's zip holds no
    history, so the top build reads s's released workspace, whose lock says
    so. A workspace that is not s's, or whose checksum is not the one
    named, stops the build; a lock that names no member concept, or no
    release of c, leaves c out.
    """
    host, top = federation["host"], federation["d_iri"] + "domains/federation"
    c_iri, s_iri = "https://c.example/knowledge/", "https://s.example/federation/"
    zips = {}
    for version, words in (("v1.0.0", "A third term."), ("v2.0.0", "A third term, revised.")):
        c = make_bundle(tmp_path / f"c-{version}", c_iri, "C", {"glossary/third.md": {"type": "GlossaryTerm", "title": "Third", "description": words, "resource": "https://example.test/c"}})
        zips[version] = (tmp_path / f"c-{version}.zip", zip_bundle(c, tmp_path / f"c-{version}.zip"))
    sub = make_domain(tmp_path / "sub", s_iri, {"c": member("c", c_iri, *zips["v1.0.0"], s_iri + "domains/federation")}, title="S")
    git = committed(sub)
    moved = member("c", c_iri, *zips["v2.0.0"], s_iri + "domains/federation", version="v2.0.0")
    moved["generated"] = {"by": "process:knowledge-federate", "at": "2026-02-01T00:00:00Z"}
    rewrite(sub, "c", moved)
    git("commit", "-qam", "move c to v2.0.0")
    r = federate(sub, "build", "--no-attestation")
    assert r.rc == 0 and "members/c: v2.0.0 waits for a person's confirmation; built at v1.0.0" in r.out, r.out
    s_lock = yaml.safe_load((sub / "snapshot" / "workspace.lock.yaml").read_text(encoding="utf-8"))
    assert s_lock["knowledge_federate_lock"] == "4" and s_lock["members"][0]["concepts"] == [s_iri + "members/c"], "the lock names the member concept"
    s_zip = tmp_path / "s.zip"
    s_sha = zip_bundle(sub / ".lokf" / "knowledge", s_zip)

    def build_with(lock: dict | None = None, checksum: str | None = None):
        ws = tmp_path / "workspace-v1.zip"
        ws_sha = workspace_zip(sub / "snapshot", ws, lock)
        s = member("s", s_iri, s_zip, s_sha, top, kind="MemberDomain")
        s["distribution"].append({"name": ws.name, "access_url": ws.as_uri(), "media_type": "application/zip", "checksum": f"sha256:{checksum or ws_sha}"})
        rewrite(host, "s", s)
        return federate(host, "build", "--no-attestation"), ws, ws_sha

    r, ws, ws_sha = build_with()
    assert r.rc == 0 and "members/c: v2.0.0 waits for a person's confirmation; built at v1.0.0, as that domain's own build took it, which the lock in workspace-v1.zip records" in r.out, r.out
    lock = yaml.safe_load((host / "snapshot" / "workspace.lock.yaml").read_text(encoding="utf-8"))
    entries = {m["base_iri"]: m for m in lock["members"]}
    assert entries[c_iri]["version"] == "v1.0.0" and entries[c_iri]["sha256"] == zips["v1.0.0"][1] and entries[c_iri]["tier"] == 2
    assert entries[c_iri]["concepts"] == [s_iri + "members/c"] and entries[s_iri]["workspace"] == {"url": ws.as_uri(), "sha256": ws_sha}
    assert {"concept": s_iri + "members/c", "base_iri": c_iri, "proposed": "v2.0.0", "built": "v1.0.0"} in lock["waiting"]
    assert c_iri in graphs_in(host / "snapshot" / "graph.nq")
    r = federate(host, "build", "--verify-only", "--no-attestation")
    assert r.rc == 0 and "c: v1.0.0 checksum matches" in r.out and "c: v2.0.0 checksum" not in r.out, "the check takes a member domain's members as the build does\n" + r.out

    r, *_ = build_with(checksum="0" * 64)
    assert r.rc == 1 and "workspace-v1.zip has sha256" in r.out, r.out
    r, *_ = build_with({**s_lock, "domain": "https://t.example/federation/domains/t"})
    assert r.rc == 1 and "workspace-v1.zip is the workspace of <https://t.example/federation/domains/t>" in r.out, r.out
    r, *_ = build_with({**s_lock, "knowledge_federate_lock": "2", "members": [{k: v for k, v in m.items() if k != "concepts"} for m in s_lock["members"]]})
    assert r.rc == 0 and "members/c: left out, because no person has confirmed it in that domain's release, and the lock in workspace-v1.zip predates format 3, so it names no member concept" in r.out, r.out
    r, *_ = build_with({**s_lock, "members": []})
    assert r.rc == 0 and "and the lock in workspace-v1.zip lists no release of it" in r.out, r.out
    assert c_iri not in built_a(host)[0]


def test_verify_only_writes_nothing_and_members_leaves_a_local_zip_alone(federation):
    host = federation["host"]
    r = federate(host, "build", "--verify-only", "--no-attestation")
    assert r.rc == 0 and "nothing written" in r.out and "every member as it stands, since a person confirmed each" in r.out, r.out
    assert not (host / "snapshot").exists() and not (host / "snapshot.new").exists()
    r = federate(host, "members", "--dry-run", "--no-attestation")
    assert r.rc == 0 and "not a GitHub release" in r.out and "no patch written" in r.out, r.out
    assert not (host / ".lokf" / "patch.yaml").exists()


SCHEMA = """\
id: https://b.example/schema
name: bschema
imports:
  - linkml:types
  - lokf
default_prefix: bschema
default_range: string
prefixes:
  bschema: https://b.example/schema/
  linkml: https://w3id.org/linkml/
  lokf: https://w3id.org/lokf/
classes:
  Widget:
    is_a: Concept
"""


def test_a_schema_released_with_a_bundle_is_what_its_fit_is_checked_against(federation, tmp_path):
    """b's new release holds a Widget, a class outside LOKF core, and the schema that declares it is released beside the zip."""
    host = federation["host"]
    b2 = make_bundle(tmp_path / "b2", federation["b_iri"], "B", {"glossary/other.md": {"type": "Widget", "title": "Other", "description": "A widget.", "resource": "https://example.test/b"}})
    sha = zip_bundle(b2, federation["b_zip"])
    concept = host / ".lokf" / "knowledge" / "members" / "b.md"
    text = concept.read_text(encoding="utf-8").replace(federation["b_sha"], sha)
    concept.write_text(text, encoding="utf-8")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0, r.out
    assert "`b`: does not validate against LOKF core alone" in (host / "snapshot" / "gate-report.md").read_text(encoding="utf-8")
    schema = write(tmp_path / "schema-v1.0.0-b.yaml", SCHEMA)
    schema_sha = hashlib.sha256(schema.read_bytes()).hexdigest()
    fm = yaml.safe_load(text.split("---\n")[1])
    fm["distribution"].append({"name": schema.name, "access_url": schema.as_uri(), "media_type": "application/yaml", "checksum": f"sha256:{schema_sha}"})
    concept.write_text(frontmatter(**fm) + "\n# Overview\n\nb bundle.\n", encoding="utf-8")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0, r.out
    assert "`b`: validates against the schema released with it, `schema-v1.0.0-b.yaml`" in (host / "snapshot" / "gate-report.md").read_text(encoding="utf-8")
    lock = yaml.safe_load((host / "snapshot" / "workspace.lock.yaml").read_text(encoding="utf-8"))
    assert next(m for m in lock["members"] if m["slug"] == "b")["schema"] == {"url": schema.as_uri(), "sha256": schema_sha}
    concept.write_text(concept.read_text(encoding="utf-8").replace(schema_sha, "1" * 64), encoding="utf-8")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 1 and "has sha256" in r.out, "a schema whose digest is not the one named stops the build"


# Drives the server over stdio with the SDK's own client: initialize, list
# the tools, then the calls named on the command line, and prints one JSON
# document with every answer. With a fifth argument, the server's log goes
# to that file, and each call's answer comes with the lines it logged.
MCP_CLIENT = """\
import asyncio, json, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
project, script, snapshot, calls = sys.argv[1:5]
errpath = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] else None
extra = json.loads(sys.argv[6]) if len(sys.argv) > 6 else []

def text(result):
    return "\\n".join(c.text for c in result.content if getattr(c, "type", "") == "text")

async def main():
    out = {"calls": [], "logs": []}
    params = StdioServerParameters(command="uv", args=["run", "--project", project, script, "mcp", "--snapshot", snapshot, *extra])
    errlog = open(errpath, "w") if errpath else sys.stderr
    read = 0
    async with stdio_client(params, errlog=errlog) as (r, w):
        async with ClientSession(r, w) as s:
            init = await s.initialize()
            out["server"], out["instructions"] = init.server_info.name, init.instructions
            out["tools"] = [t.name for t in (await s.list_tools()).tools]
            for name, args in json.loads(calls):
                out["calls"].append(json.loads(text(await s.call_tool(name, args))))
                if errpath:
                    log = open(errpath, encoding="utf-8").read()
                    out["logs"].append(log[read:])
                    read = len(log)
    print(json.dumps(out))

asyncio.run(main())
"""


def test_mcp_serves_the_index_first_and_each_tool_bounded(federation, tmp_path):
    host = federation["host"]
    assert federate(host, "build", "--snapshot-iri", "https://d.example/snapshots/v0.2.0", "--no-attestation").rc == 0
    a_term, b_other = federation["a_iri"] + "glossary/term", federation["b_iri"] + "glossary/other"
    calls = [("read_document", {}), ("resolve_iri", {"iri": b_other}), ("neighbors", {"iri": a_term, "depth": 1, "limit": 50}),
             ("subgraph", {"iris": [a_term], "depth": 1, "format": "trig"}), ("federated_sparql", {"query": "labels.rq"}),
             ("federated_sparql", {"query": "SELECT * WHERE { SERVICE <https://x.example/sparql> { ?s ?p ?o } }"}),
             ("read_document", {"iri": b_other}), ("read_document", {"iri": federation["a_iri"] + "../../etc/passwd"}),
             ("resolve_iri", {"iri": "https://nobody.example/knowledge/x"}), ("neighbors", {"iri": a_term, "depth": 9, "limit": 1}),
             ("federated_sparql", {"query": 'CONSTRUCT { ?s ?p ?x } WHERE { GRAPH ?g { ?s ?p ?o } GRAPH ?h { ?a ?b ?c } BIND(IRI(CONCAT("urn:x:", MD5(CONCAT(STR(?o), STR(?a), STR(?b), STR(?c))))) AS ?x) }'}), ("federated_sparql", {"query": "SELECT * WHERE { GRAPH ?g { ?s ?p ?o } }", "limit": 3})]
    client = write(tmp_path / "client.py", MCP_CLIENT)
    r = run(["uv", "run", "--project", REPO / ".lokf", "python", "-I", client, REPO / ".lokf", SCRIPT, host / "snapshot", json.dumps(calls)], cwd=tmp_path, stdout_only=True)
    assert r.rc == 0, r.out
    out = json.loads(r.out)
    assert out["server"] == "lokf-registry" and out["tools"] == ["resolve_iri", "neighbors", "subgraph", "federated_sparql", "read_document"]
    assert out["instructions"].startswith("The workspace of a LOKF federation") and "# D: the workspace" in out["instructions"], "the index is the server's instructions"
    index, resolved, near, sub, labels, service, doc, traversal, outside, cut, constructed, selected = out["calls"]
    assert index["path"] == "index.md" and index["markdown"].startswith("# D: the workspace")
    assert resolved["owner"]["slug"] == "b" and resolved["concept"]["type"] == "GlossaryTerm" and resolved["concept"]["trust"]["trust_tier"]
    assert any(t["graph"] == federation["a_iri"] and t["object"]["value"] == b_other for t in near["triples"]), "the cross-bundle edge is asserted by a's graph"
    assert sub["format"] == "trig" and federation["a_iri"] in sub["rdf"] and sub["count"] == near["count"]
    assert "g" in labels["columns"] and labels["rows"] and not labels["truncated"]
    assert "SERVICE" in service["error"]
    assert doc["bundle"]["slug"] == "b" and doc["markdown"].startswith("---") and doc["trust"]["status"]
    assert "error" in traversal and outside["owner"] is None
    assert cut["truncated"] and cut["count"] == 1
    assert constructed["truncated"] and constructed["count"] == 2000 and constructed["turtle"], "a CONSTRUCT is bounded as a walk is"
    assert selected["truncated"] and len(selected["rows"]) == 3 and sorted(selected["columns"]) == ["g", "o", "p", "s"]


def test_mcp_loads_a_graph_when_a_walk_first_reaches_it(federation, tmp_path):
    """The server starts with no graph loaded, and every answer is the one a workspace loaded whole gives.

    A neighbourhood of b's term loads b's graph, a's, which links into b, and
    the lock graph, which names every bundle, and not the domain's. One of
    a's term then loads nothing more, and a SPARQL query loads the rest. The
    lock says where each graph lies in graph.nq and which namespaces it names.
    """
    host, a_iri, b_iri, d_iri = federation["host"], federation["a_iri"], federation["b_iri"], federation["d_iri"]
    snap_iri = "https://d.example/snapshots/v0.2.0"
    assert federate(host, "build", "--snapshot-iri", snap_iri, "--no-attestation").rc == 0
    snap = host / "snapshot"
    lock = yaml.safe_load((snap / "workspace.lock.yaml").read_text(encoding="utf-8"))
    graphs = {g["graph"]: g for g in lock["graphs"]}
    assert set(graphs) == {a_iri, b_iri, d_iri, snap_iri}
    assert graphs[a_iri]["names"] == [b_iri] and graphs[b_iri]["names"] == [] and graphs[snap_iri]["names"] == sorted([a_iri, b_iri, d_iri])
    nq = (snap / "graph.nq").read_bytes()
    for g, entry in graphs.items():
        lines = nq[entry["offset"]:entry["offset"] + entry["bytes"]].decode("utf-8").splitlines()
        assert len(lines) == entry["quads"] and all(line.endswith(f" <{g}> .") for line in lines), g
    a_term, b_other = a_iri + "glossary/term", b_iri + "glossary/other"
    calls = [("resolve_iri", {"iri": b_other}), ("neighbors", {"iri": b_other, "depth": 1}), ("neighbors", {"iri": a_term, "depth": 2}),
             ("federated_sparql", {"query": "SELECT (COUNT(*) AS ?n) WHERE { GRAPH ?g { ?s ?p ?o } }"})]
    client = write(tmp_path / "client.py", MCP_CLIENT)

    def answers(snapshot: Path) -> dict:
        r = run(["uv", "run", "--project", REPO / ".lokf", "python", "-I", client, REPO / ".lokf", SCRIPT, snapshot, json.dumps(calls), tmp_path / f"{snapshot.name}.log"],
                cwd=tmp_path, stdout_only=True)
        assert r.rc == 0, r.out
        return json.loads(r.out)

    lazy = answers(snap)
    loaded = [sorted(re.findall(r"loaded <([^>]+)>", log)) for log in lazy["logs"]]
    assert loaded == [[], sorted([a_iri, b_iri, snap_iri]), [], [d_iri]], loaded
    assert any(t["graph"] == a_iri and t["object"]["value"] == b_other for t in lazy["calls"][1]["triples"]), "a's link into b is there when the walk starts in b"
    whole = tmp_path / "whole"
    shutil.copytree(snap, whole)
    (whole / "workspace.lock.yaml").write_text(yaml.safe_dump({k: v for k, v in lock.items() if k != "graphs"}, sort_keys=False), encoding="utf-8")
    eager = answers(whole)
    assert not any("loaded <" in log for log in eager["logs"]), "a lock with no graphs index loads graph.nq whole"

    def same(answer: dict) -> dict:
        return {**answer, "triples": sorted(answer.get("triples", []), key=json.dumps)} if "triples" in answer else answer
    assert [same(a) for a in lazy["calls"]] == [same(a) for a in eager["calls"]]
    assert int(lazy["calls"][3]["rows"][0]["n"]) == len(nq.decode("utf-8").splitlines())


def test_read_document_falls_back_to_the_bundle_s_concepts_jsonld(federation, tmp_path):
    """A workspace that lacks b's copy of a concept reads it from b's concepts.jsonld, as section 11.4 chains them, and says so; with neither, and no public source, it says there is none."""
    host, b_iri = federation["host"], federation["b_iri"]
    assert federate(host, "build", "--no-attestation").rc == 0
    snap = tmp_path / "snap"
    shutil.copytree(host / "snapshot", snap)
    (snap / "bundles" / "b" / ".lokf" / "knowledge" / "glossary" / "other.md").unlink()
    b_other = b_iri + "glossary/other"
    out = mcp_answers(tmp_path, snap, [("read_document", {"iri": b_other})], "fallback")
    doc = out["calls"][0]
    assert doc["read_from"] == "concepts.jsonld" and "Another term." in doc["markdown"] and doc["trust"], doc
    (snap / "export" / "b" / "concepts.jsonld").unlink()
    out = mcp_answers(tmp_path, snap, [("read_document", {"iri": b_other})], "none")
    assert out["calls"][0]["error"] == "b has no document at bundles/b/.lokf/knowledge/glossary/other.md", out["calls"][0]


def mcp_answers(tmp_path: Path, snapshot, calls: list, name: str, *server_args: str) -> dict:
    """The MCP client's answers to these calls, with the server's log of each, the server run with any further arguments."""
    client = write(tmp_path / "client.py", MCP_CLIENT)
    r = run(["uv", "run", "--project", REPO / ".lokf", "python", "-I", client, REPO / ".lokf", SCRIPT, snapshot, json.dumps(calls),
             tmp_path / f"{name}.log", json.dumps(list(server_args))], cwd=tmp_path, stdout_only=True)
    assert r.rc == 0, r.out
    return json.loads(r.out)


def same_answers(answers: list[dict]) -> list[dict]:
    """Answers with their triples in one order, since a store gives them in the order it loaded them."""
    return [{**a, "triples": sorted(a["triples"], key=json.dumps)} if "triples" in a else a for a in answers]


def test_mcp_loads_the_graphs_that_share_an_iri_no_bundle_owns_and_no_more(federation, tmp_path):
    """a's and b's terms are each defined by one outside resource, which no bundle owns.

    The lock lists it under `shares` in a's graph and in b's. A walk from
    a's term that steps to it loads the graphs that share it, and not the
    domain's, which holds no such IRI; a walk that starts at it loads every
    graph, since only a graph that shares an IRI lists it. Each answer is
    the one a workspace loaded whole gives.
    """
    host, a_iri, b_iri, d_iri = federation["host"], federation["a_iri"], federation["b_iri"], federation["d_iri"]
    spec, top = "https://standards.example/spec", d_iri + "domains/federation"
    a2 = make_bundle(tmp_path / "a2", a_iri, "A", {"glossary/term.md": {"type": "GlossaryTerm", "title": "Term", "description": "A term.", "resource": "https://example.test/a",
                                                                         "relatedTo": [b_iri + "glossary/other"], "definedBy": [spec]}})
    b2 = make_bundle(tmp_path / "b2", b_iri, "B", {"glossary/other.md": {"type": "GlossaryTerm", "title": "Other", "description": "Another term.", "resource": "https://example.test/b", "definedBy": [spec]}})
    for slug, k, iri in (("a", a2, a_iri), ("b", b2, b_iri)):
        zipped = tmp_path / f"{slug}2.zip"
        rewrite(host, slug, member(slug, iri, zipped, zip_bundle(k, zipped), top))
    snap_iri = "https://d.example/snapshots/v0.2.0"
    assert federate(host, "build", "--snapshot-iri", snap_iri, "--no-attestation").rc == 0
    snap = host / "snapshot"
    lock = yaml.safe_load((snap / "workspace.lock.yaml").read_text(encoding="utf-8"))
    shares = {g["graph"]: g["shares"] for g in lock["graphs"]}
    assert shares == {a_iri: [spec], b_iri: [spec], d_iri: [], snap_iri: []}, shares
    a_term = a_iri + "glossary/term"
    calls = [("neighbors", {"iri": a_term, "depth": 2}), ("neighbors", {"iri": spec, "depth": 1})]
    lazy = mcp_answers(tmp_path, snap, calls, "lazy")
    loaded = [sorted(re.findall(r"loaded <([^>]+)>", log)) for log in lazy["logs"]]
    assert loaded == [sorted([a_iri, b_iri, snap_iri]), [d_iri]], loaded
    assert any(t["graph"] == b_iri and t["subject"] == b_iri + "glossary/other" for t in lazy["calls"][0]["triples"]), "b's term, which shares the IRI, is in the walk"
    whole = tmp_path / "whole"
    shutil.copytree(snap, whole)
    (whole / "workspace.lock.yaml").write_text(yaml.safe_dump({k: v for k, v in lock.items() if k != "graphs"}, sort_keys=False), encoding="utf-8")
    assert same_answers(lazy["calls"]) == same_answers(mcp_answers(tmp_path, whole, calls, "whole")["calls"])


# A static server for a workspace folder that answers a range request with
# 206 and the bytes asked for, as GitHub Pages does, and logs each request.
RANGE_SERVER = """\
import http.server, pathlib, re, sys
root, portfile, logfile = sys.argv[1:4]
FAILED = set()  # the /fail-once/ paths already answered 503
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kw):
        super().__init__(*args, directory=root, **kw)
    def log_message(self, fmt, *args):
        with open(logfile, "a", encoding="utf-8") as log:
            log.write(f"{self.command} {self.path} {self.headers.get('Range') or '-'}\\n")
    def do_GET(self):
        if self.path.startswith("/redirect-to/"):
            self.send_response(302)
            self.send_header("Location", self.path[len("/redirect-to/"):])
            self.end_headers()
            return
        if self.path.startswith("/fail-once/"):
            if self.path not in FAILED:
                FAILED.add(self.path)
                self.send_error(503)
                return
            self.path = self.path[len("/fail-once"):]
        wanted = re.fullmatch(r"bytes=(\\d+)-(\\d+)", self.headers.get("Range") or "")
        path = pathlib.Path(self.translate_path(self.path))
        if wanted and path.is_file():
            data = path.read_bytes()
            start, end = int(wanted.group(1)), min(int(wanted.group(2)), len(data) - 1)
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{len(data)}")
            self.send_header("Content-Length", str(end - start + 1))
            self.end_headers()
            self.wfile.write(data[start:end + 1])
            return
        super().do_GET()
server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
pathlib.Path(portfile).write_text(str(server.server_address[1]), encoding="utf-8")
server.serve_forever()
"""


@contextlib.contextmanager
def serving(root: Path, work: Path):
    """RANGE_SERVER serving a folder over HTTP: its address and its request log."""
    import subprocess
    import time

    work.mkdir(parents=True, exist_ok=True)
    script, port, log = write(work / "server.py", RANGE_SERVER), work / "port", work / "requests.log"
    proc = subprocess.Popen(["python3", "-I", str(script), str(root), str(port), str(log)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            if port.is_file() and port.read_text(encoding="utf-8"):
                break
            time.sleep(0.1)
        yield f"http://127.0.0.1:{port.read_text(encoding='utf-8')}/", log
    finally:
        proc.terminate()
        proc.wait(timeout=10)


@pytest.fixture
def served_workspace(federation, tmp_path):
    """The federation's workspace, built, and served over HTTP from its folder by RANGE_SERVER: its address and its request log."""
    host = federation["host"]
    assert federate(host, "build", "--snapshot-iri", "https://d.example/snapshots/v0.2.0", "--no-attestation").rc == 0
    with serving(host / "snapshot", tmp_path / "server") as (url, log):
        yield {"url": url, "log": log, "snapshot": host / "snapshot"}


def test_a_download_is_tried_again_after_a_server_error_and_follows_no_redirect_out_of_http(federation, tmp_path):
    """b's zip answers 503 once and then the file: the build tries again and gets it. A redirect to another scheme, or a file that is no zip, stops the build with a finding."""
    host, b_iri, d_iri = federation["host"], federation["b_iri"], federation["d_iri"]
    files = tmp_path / "files"
    files.mkdir()
    shutil.copy(federation["b_zip"], files / "b.zip")
    (files / "junk.zip").write_bytes(b"no zip at all")
    with serving(files, tmp_path / "server") as (url, log):
        def b_at(address: str, sha: str = federation["b_sha"]) -> None:
            fm = member("b", b_iri, federation["b_zip"], sha, d_iri + "domains/federation")
            fm["distribution"][0]["access_url"] = address
            rewrite(host, "b", fm)

        b_at(url + "fail-once/b.zip")
        r = federate(host, "build", "--no-attestation", "--cache", str(tmp_path / "c1"))
        assert r.rc == 0, r.out
        assert read(log).count("GET /fail-once/b.zip") == 2, read(log)
        b_at(url + "redirect-to/ftp://example.test/b.zip")
        r = federate(host, "build", "--no-attestation", "--cache", str(tmp_path / "c2"))
        assert r.rc == 1 and "a redirect from http to ftp is refused" in r.out, r.out
        b_at(url + "junk.zip", hashlib.sha256(b"no zip at all").hexdigest())
        r = federate(host, "build", "--no-attestation", "--cache", str(tmp_path / "c3"))
        assert r.rc == 1 and "matches its checksum but is no readable zip" in r.out and "Traceback" not in r.out, r.out
        r = federate(host, "build", "--no-attestation", "--cache", str(tmp_path / "c3"), "--previous", url)
        assert r.rc == 1 and "takes a workspace folder or a workspace-<tag>.zip, not a site" in r.out, r.out


def test_the_readers_read_a_workspace_from_its_zip_or_the_site_that_serves_it(federation, served_workspace, tmp_path):
    """The MCP server reads the workspace as a site serves it, and as a workspace-<tag>.zip, as it reads the folder.

    Over HTTP it reads the lock, the registry and the index first, then each
    graph by a range request when a walk reaches it, and a document when one
    is asked for; it fetches graph.nq whole for no walk. `query` takes a
    stored query by name from the served workspace, and `diff` reads the
    served lock.
    """
    host, a_iri, b_iri = federation["host"], federation["a_iri"], federation["b_iri"]
    url, snap = served_workspace["url"], served_workspace["snapshot"]
    b_other = b_iri + "glossary/other"
    calls = [("resolve_iri", {"iri": b_other}), ("neighbors", {"iri": b_other, "depth": 1}), ("read_document", {"iri": b_other}),
             ("federated_sparql", {"query": "links.rq"})]
    local = mcp_answers(tmp_path, snap, calls, "local")
    served = mcp_answers(tmp_path, url, calls, "served")
    zipped = tmp_path / "workspace-v0.2.0.zip"
    workspace_zip(snap, zipped)
    in_zip = mcp_answers(tmp_path, zipped, calls, "zip")
    assert same_answers(served["calls"]) == same_answers(local["calls"]) == same_answers(in_zip["calls"])
    assert served["calls"][2]["read_from"] == "workspace" and served["calls"][2]["markdown"].startswith("---")
    requests = served_workspace["log"].read_text(encoding="utf-8").splitlines()
    walk = requests[:next(i for i, line in enumerate(requests) if "/queries/links.rq" in line)]
    assert any(line.startswith("GET /graph.nq bytes=") for line in walk), requests
    assert not any(line == "GET /graph.nq -" for line in walk), "a walk reads the graphs it reaches by range, never graph.nq whole"
    r = federate(host, "query", "links.rq", "--snapshot", url)
    assert r.rc == 0 and f"{a_iri}\t{b_iri}\thttp://purl.org/dc/terms/relation\t1" in r.out, r.out
    r = federate(host, "diff", url, "snapshot", stdout_only=True)
    assert r.rc == 0 and "No member joined, moved or left since the workspace of https://d.example/snapshots/v0.2.0." in r.out, r.out


def test_a_reader_given_members_reads_those_bundles_alone(federation, tmp_path):
    """`--member a` is a reader of a's graph alone: per-query permission as a store grants it, graph by graph.

    Its instructions name a alone, b's IRIs read as ones no member owns, a
    walk never loads b's graph, and SPARQL counts a's quads; `query` takes
    the same scope, and a slug the workspace lacks stops the reader.
    """
    host, a_iri, b_iri = federation["host"], federation["a_iri"], federation["b_iri"]
    assert federate(host, "build", "--no-attestation").rc == 0
    snap = host / "snapshot"
    lock = yaml.safe_load((snap / "workspace.lock.yaml").read_text(encoding="utf-8"))
    a_quads = next(g["quads"] for g in lock["graphs"] if g["graph"] == a_iri)
    a_term, b_other = a_iri + "glossary/term", b_iri + "glossary/other"
    count = "SELECT (COUNT(*) AS ?n) WHERE { GRAPH ?g { ?s ?p ?o } }"
    calls = [("resolve_iri", {"iri": b_other}), ("read_document", {"iri": b_other}), ("neighbors", {"iri": a_term, "depth": 2}),
             ("federated_sparql", {"query": count}), ("read_document", {}), ("federated_sparql", {"query": "links.rq"})]
    out = mcp_answers(tmp_path, snap, calls, "scoped", "--member", "a")
    assert "as this reader reads it" in out["instructions"] and "a bundle" in out["instructions"] and "b bundle" not in out["instructions"]
    resolved, doc, near, counted, index, links = out["calls"]
    assert links["error"].startswith("links.rq reads the lock graph"), links
    assert resolved["owner"] is None and doc["error"] == f"no bundle this reader reads owns {b_other}"
    assert {t["graph"] for t in near["triples"]} == {a_iri} and not any(f"loaded <{b_iri}>" in log for log in out["logs"])
    assert int(counted["rows"][0]["n"]) == a_quads and "b bundle" not in index["markdown"]
    r = federate(host, "query", count, "--member", "a")
    assert r.rc == 0 and r.out.splitlines()[-1] == str(a_quads), r.out
    r = federate(host, "query", "unowned.rq", "--member", "a")
    assert r.rc == 1 and "unowned.rq reads the lock graph, which a reader given --member leaves out" in r.out, r.out
    r = federate(host, "query", count, "--member", "nobody")
    assert r.rc == 1 and "--member nobody: no bundle of this workspace has that slug or base_iri; those here are a, b, domain" in r.out, r.out


def test_a_member_s_text_licence_and_an_explicit_id_outside_its_namespace_read_as_released(federation, tmp_path):
    """b's index gives its licence as `MIT`, and one of its concepts has an `id` outside b's namespace.

    The lock graph keeps the licence as text, since no store takes it as an
    IRI, and the MCP server reads the concept by that id, which the
    registry routes to b through its id_index.
    """
    host, b_iri = federation["host"], federation["b_iri"]
    legacy = "https://legacy.example/b/old-term"
    b2 = make_bundle(tmp_path / "b2", b_iri, "B", {"glossary/other.md": {"type": "GlossaryTerm", "title": "Other", "description": "Another term.", "resource": "https://example.test/b"},
                                                   "glossary/legacy.md": {"type": "GlossaryTerm", "id": legacy, "title": "Legacy", "description": "An older term.", "resource": "https://example.test/b"}})
    index = b2 / "index.md"
    index.write_text(index.read_text(encoding="utf-8").replace("license: https://creativecommons.org/licenses/by/4.0/", "license: MIT"), encoding="utf-8")
    zipped = tmp_path / "b2.zip"
    rewrite(host, "b", member("b", b_iri, zipped, zip_bundle(b2, zipped), federation["d_iri"] + "domains/federation"))
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0, r.out
    assert f'<{b_iri}> <http://purl.org/dc/terms/license> "MIT"' in (host / "snapshot" / "graph.nq").read_text(encoding="utf-8")
    assert f"| `{b_iri}` | D | MIT |" in (host / "snapshot" / "index.md").read_text(encoding="utf-8"), "a text licence is written as text, not as an address"
    resolved, doc = mcp_answers(tmp_path, host / "snapshot", [("resolve_iri", {"iri": legacy}), ("read_document", {"iri": legacy})], "legacy")["calls"]
    assert resolved["owner"]["slug"] == "b" and resolved["concept"]["title"] == "Legacy", resolved
    assert doc["path"] == "bundles/b/.lokf/knowledge/glossary/legacy.md" and "title: Legacy" in doc["markdown"], doc


# ---------------------------------------------------------------------------
# members against GitHub releases, served from fixture files
# ---------------------------------------------------------------------------
# Loads the script as a module, answers its HTTP requests from the files a
# JSON map names, and runs its main(); any other address fails as an
# unreachable one would.
RUNNER = """\
import importlib.util, json, os, pathlib, sys, urllib.error
script, served, *argv = sys.argv[1:]
spec = importlib.util.spec_from_file_location("knowledge_federate", script)
federate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(federate)
urls = json.loads(pathlib.Path(served).read_text(encoding="utf-8"))
def http_fetch(url, accept=None, headers=None, max_bytes=None, timeout=60):
    if url not in urls:
        raise urllib.error.URLError(url + " is not served by this test")
    entry = urls[url]
    if isinstance(entry, dict) and entry.get("status"):
        log.append(url + " " + str(entry["status"]))
        raise urllib.error.HTTPError(url, entry["status"], "refused by this test", {}, None)
    path, sent = (entry, {}) if isinstance(entry, str) else (entry["path"], entry.get("headers") or {})
    if sent.get("etag") and (headers or {}).get("If-None-Match") == sent["etag"]:
        log.append(url + " 304")
        return 304, dict(sent), b""
    log.append(url + " 200")
    return 200, dict(sent), pathlib.Path(path).read_bytes()
log = []
federate.http_fetch = http_fetch
try:
    sys.exit(federate.main(argv))
finally:
    if os.environ.get("RUNNER_LOG"):
        pathlib.Path(os.environ["RUNNER_LOG"]).write_text("\\n".join(log) + "\\n", encoding="utf-8")
"""

# Answers `gh pr list` with the pull requests FAKE_GH_PRS names, and
# `gh api repos/<owner>/<repo>/releases...` from <repo>.json in FAKE_GH_API
# when that is set, and fails every other command, so the script never asks
# a real repository.
FAKE_GH = """\
#!/bin/sh
[ "$1 $2" = "pr list" ] && { printf '%s\\n' "${FAKE_GH_PRS:-[]}"; exit 0; }
if [ "$1" = api ] && [ -n "${FAKE_GH_API:-}" ]; then
  repo=$(printf '%s' "$2" | cut -d/ -f3)
  cat "$FAKE_GH_API/$repo.json" && exit 0
fi
if [ "$1 $2" = "attestation verify" ]; then
  [ "${GH_TOKEN:-}" = job-token ] && [ -z "${KNOWLEDGE_FEDERATE_TOKEN:-}" ] && exit 0
  echo "gh: To use GitHub CLI in a GitHub Actions workflow, set the GH_TOKEN environment variable." >&2
fi
exit 1
"""

OLD, NEW = ("v1.0.0", "2026-10-15T08:00:00Z"), ("v1.1.0", "2026-10-20T09:00:00Z")


def github_member(slug: str, domain_iri: str, **extra) -> dict:
    """A member concept that names its zip in a GitHub release of acme/<slug> at the old tag."""
    tag, day = OLD[0], OLD[1][:10]
    name = f"knowledge-{tag}-{slug}.zip"
    page = f"https://github.com/acme/{slug}/releases/tag/{tag}"
    return {
        "type": "MemberBundle", "title": f"{slug} bundle", "description": f"The {slug} bundle as released at {tag} on {day}.",
        "resource": page, "base_iri": f"https://{slug}.example/knowledge/", "version": tag, "release": page,
        "distribution": [{"name": name, "access_url": f"https://github.com/acme/{slug}/releases/download/{tag}/{name}",
                          "media_type": "application/zip", "checksum": "sha256:" + "0" * 64}],
        "isPartOf": [domain_iri], **extra,
    }


def github_release(slug: str, tag: str, published_at: str) -> dict:
    """One release as the GitHub API lists it, carrying a bundle zip and its .sha256."""
    name = f"knowledge-{tag}-{slug}.zip"
    base = f"https://github.com/acme/{slug}/releases/download/{tag}/"
    return {"tag_name": tag, "draft": False, "published_at": published_at,
            "assets": [{"name": name, "browser_download_url": base + name}, {"name": name + ".sha256", "browser_download_url": base + name + ".sha256"}]}


A_BODY = f"""
# Overview

The a bundle as released at {OLD[0]} on {OLD[1][:10]}, attached as `knowledge-{OLD[0]}-a.zip`.

Download it from https://github.com/acme/a/releases/download/{OLD[0]}/knowledge-{OLD[0]}-a.zip.

Built at {OLD[0]}.

Built at {OLD[0]}.

Neither {OLD[0]}-rc1, {OLD[0]}1 nor the build at {OLD[1]} is this release.

<!-- lokf:related -->
- [Release {OLD[0]}](https://github.com/acme/a/releases/tag/{OLD[0]})
<!-- /lokf:related -->

## Open questions

- 2026-10-16, process:knowledge-federate: acme/a released {OLD[0]} after v0.9.0; does this member move to it?
"""


@pytest.fixture
def released(tmp_path):
    """A domain of four members released on GitHub, each with a newer release, and stand-ins for the GitHub API and gh.

    a is a draft whose body names the old release in lines that move, in a
    line that occurs twice, and in its lokf:related block and open
    questions; b is confirmed by a person; c was edited after a person
    confirmed it; d was written by a person.
    """
    d_iri = "https://d.example/federation/"
    top = d_iri + "domains/federation"
    agent = {"by": "process:knowledge-federate", "at": "2026-10-16T10:00:00Z"}
    concepts = {
        "a": github_member("a", top, generated=agent, status="draft"),
        "b": github_member("b", top, generated=agent, verified=[{"by": "human:noel", "at": "2026-10-16T12:00:00Z"}]),
        "c": github_member("c", top, generated=agent, verified=[{"by": "human:noel", "at": "2026-10-16T09:00:00Z"}]),
        "d": github_member("d", top, generated={"by": "human:noel", "at": "2026-10-16T10:00:00Z"}),
    }
    host = make_domain(tmp_path / "host", d_iri, concepts)
    write(host / ".lokf" / "knowledge" / "members" / "a.md", frontmatter(**concepts["a"]) + A_BODY)
    bundle = make_bundle(tmp_path / "bundle", "https://a.example/knowledge/", "A", {"glossary/term.md": {"type": "GlossaryTerm", "title": "Term", "description": "A term.", "resource": "https://example.test/a"}})
    zip_path = tmp_path / "release.zip"
    sha = zip_bundle(bundle, zip_path)
    sums = write(tmp_path / "release.zip.sha256", f"{sha}  release.zip\n")
    schema = write(tmp_path / "schema.yaml", SCHEMA)
    schema_sums = write(tmp_path / "schema.yaml.sha256", f"{hashlib.sha256(schema.read_bytes()).hexdigest()}  schema.yaml\n")

    def with_schema(release: dict) -> dict:
        """The release with schema-<tag>-<slug>.yaml and its .sha256 beside the zip, as knowledge-release.yaml attaches them."""
        base = release["assets"][0]["browser_download_url"].rsplit("/", 1)[0] + "/"
        name = f"schema-{release['tag_name']}-{base.split('/')[4]}.yaml"
        release["assets"] += [{"name": name, "browser_download_url": base + name}, {"name": name + ".sha256", "browser_download_url": base + name + ".sha256"}]
        served[base + name], served[base + name + ".sha256"] = str(schema), str(schema_sums)
        return release

    served = {}
    for slug in concepts:
        releases = [github_release(slug, *NEW), github_release(slug, *OLD)]
        if slug == "b":
            with_schema(releases[0])
        listing = write(tmp_path / "api" / f"{slug}.json", json.dumps(releases))
        served[f"https://api.github.com/repos/acme/{slug}/releases?per_page=100"] = str(listing)
        asset, checksum = releases[0]["assets"][:2]
        served[asset["browser_download_url"]] = str(zip_path)
        served[checksum["browser_download_url"]] = str(sums)
    # e has a bundle release of its own and no member concept yet, and its
    # index describes it with no full stop; nested's release is bundle A
    # again, whose namespace a member already holds.
    e_bundle = make_bundle(tmp_path / "e_bundle", "https://e.example/knowledge/", "E", {"glossary/e.md": {"type": "GlossaryTerm", "title": "E term", "description": "E's term.", "resource": "https://example.test/e"}},
                           description='Help a person check the "E" bundle')
    e_zip = tmp_path / "e.zip"
    e_sums = write(tmp_path / "e.zip.sha256", f"{zip_bundle(e_bundle, e_zip)}  e.zip\n")
    # f's release is a domain in turn: a Domain concept and one member, with
    # the workspace its build attached, whose lock is f's.
    f_zip, f_sha = domain_zip(tmp_path, "f", "https://f.example/federation/", {"a": github_member("a", "https://f.example/federation/domains/f")})
    f_sums = write(tmp_path / "f.zip.sha256", f"{f_sha}  f.zip\n")
    f_workspace = tmp_path / "f-workspace.zip"
    with zipfile.ZipFile(f_workspace, "w") as zf:
        zf.writestr("workspace/workspace.lock.yaml", yaml.safe_dump({"knowledge_federate_lock": "3", "domain": "https://f.example/federation/domains/f",
                                                                     "domain_base_iri": "https://f.example/federation/", "members": []}))
    f_workspace_sums = write(tmp_path / "f-workspace.zip.sha256", f"{hashlib.sha256(f_workspace.read_bytes()).hexdigest()}  f-workspace.zip\n")

    def with_workspace(release: dict) -> dict:
        """The release with workspace-<tag>.zip and its .sha256, as a domain host's federation workflow attaches them."""
        base = release["assets"][0]["browser_download_url"].rsplit("/", 1)[0] + "/"
        name = f"workspace-{release['tag_name']}.zip"
        release["assets"] += [{"name": name, "browser_download_url": base + name}, {"name": name + ".sha256", "browser_download_url": base + name + ".sha256"}]
        served[base + name], served[base + name + ".sha256"] = str(f_workspace), str(f_workspace_sums)
        return release

    for slug, zipped, summed in (("e", e_zip, e_sums), ("nested", zip_path, sums), ("f", f_zip, f_sums)):
        release = with_schema(github_release(slug, *NEW)) if slug == "e" else with_workspace(github_release(slug, *NEW)) if slug == "f" else github_release(slug, *NEW)
        served[f"https://api.github.com/repos/acme/{slug}/releases?per_page=100"] = str(write(tmp_path / "api" / f"{slug}.json", json.dumps([release])))
        asset, checksum = release["assets"][:2]
        served[asset["browser_download_url"]], served[checksum["browser_download_url"]] = str(zipped), str(summed)
    write(tmp_path / "served.json", json.dumps(served))
    write(tmp_path / "runner.py", RUNNER)
    gh = write(tmp_path / "bin" / "gh", FAKE_GH)
    gh.chmod(0o755)
    return {"host": host, "tmp": tmp_path, "sha": sha}


def members_run(released, *args: str, prs: str = "[]", stdout_only: bool = False, attest: bool = False, env: dict | None = None):
    tmp = released["tmp"]
    return run(["uv", "run", "--project", REPO / ".lokf", tmp / "runner.py", SCRIPT, tmp / "served.json",
                "--root", released["host"], "members", *([] if attest else ["--no-attestation"]), *args],
               cwd=released["host"], env={"PATH": f"{tmp / 'bin'}:{os.environ['PATH']}", "FAKE_GH_PRS": prs, **(env or {})},
               stdout_only=stdout_only, unset=("GH_TOKEN", "GITHUB_TOKEN", "KNOWLEDGE_FEDERATE_TOKEN"))


def ops_for(patch: dict, slug: str) -> dict:
    return {op["op"]: op for op in patch["ops"] if op["path"] == f"members/{slug}.md"}


def test_members_moves_the_text_with_the_version_in_a_patch_the_pen_applies(released):
    host = released["host"]
    r = members_run(released)
    assert r.rc == 0 and "4 member(s) moved" in r.out, r.out
    r = run(["bash", APPLY, "--root", host], cwd=host)
    assert r.rc == 0, r.out
    text = read(host / ".lokf" / "knowledge" / "members" / "a.md")
    fm = yaml.safe_load(text.split("---\n")[1])
    assert fm["version"] == "v1.1.0" and fm["release"] == fm["resource"] == "https://github.com/acme/a/releases/tag/v1.1.0"
    assert fm["distribution"][0]["name"] == "knowledge-v1.1.0-a.zip" and fm["distribution"][0]["checksum"] == "sha256:" + released["sha"]
    assert fm["description"] == "The a bundle as released at v1.1.0 on 2026-10-20."
    for line in ("The a bundle as released at v1.1.0 on 2026-10-20, attached as `knowledge-v1.1.0-a.zip`.",
                 "Download it from https://github.com/acme/a/releases/download/v1.1.0/knowledge-v1.1.0-a.zip.",
                 "Neither v1.0.0-rc1, v1.0.01 nor the build at 2026-10-15T08:00:00Z is this release.",
                 "- [Release v1.0.0](https://github.com/acme/a/releases/tag/v1.0.0)",
                 "- 2026-10-16, process:knowledge-federate: acme/a released v1.0.0 after v0.9.0; does this member move to it?"):
        assert line in text.split("\n"), f"{line!r} is not a line of:\n{text}"
    assert text.count("\nBuilt at v1.0.0.\n") == 2, "a line that occurs twice is left as it was"
    assert "acme/a released v1.1.0 after v1.0.0; does this member move to it? 2 line(s) of the body still name v1.0.0" in text, text
    for slug in ("b", "c"):
        moved = read(host / ".lokf" / "knowledge" / "members" / f"{slug}.md")
        assert "version: v1.1.0" in moved and f"The {slug} bundle as released at v1.1.0 on 2026-10-20." in moved, moved
    b = yaml.safe_load(read(host / ".lokf" / "knowledge" / "members" / "b.md").split("---\n")[1])
    assert [d["name"] for d in b["distribution"]] == ["knowledge-v1.1.0-b.zip", "schema-v1.1.0-b.yaml"], "a schema released beside the zip is named as a second distribution"
    assert b["distribution"][1]["media_type"] == "application/yaml" and b["distribution"][1]["checksum"] == "sha256:" + hashlib.sha256(SCHEMA.encode()).hexdigest()
    person = read(host / ".lokf" / "knowledge" / "members" / "d.md")
    assert "version: v1.0.0" in person and "The d bundle as released at v1.0.0 on 2026-10-15." in person, "a concept a person wrote keeps its text"
    assert "A person wrote this concept, so this patch leaves its text and frontmatter as they are." in person, person


def test_members_calls_a_member_confirmed_only_when_a_person_confirmed_it(released):
    r = members_run(released, "--dry-run", stdout_only=True)
    assert r.rc == 0, r.out
    patch = yaml.safe_load(r.out)
    asked = {slug: ops_for(patch, slug)["question"]["text"] for slug in "abcd"}
    assert asked["a"].startswith("acme/a released v1.1.0 after v1.0.0; "), "a draft is not called confirmed"
    assert asked["b"].startswith("acme/b released v1.1.0 after the confirmed v1.0.0; "), "a person confirmed b as it stands"
    assert asked["c"].startswith("acme/c released v1.1.0 after v1.0.0; "), "c was edited after its confirmation"
    assert asked["d"].startswith("acme/d released v1.1.0 after v1.0.0; ") and "patch" not in ops_for(patch, "d"), "a person wrote d"
    assert not (released["host"] / ".lokf" / "patch.yaml").exists(), "a dry run writes nothing"


def test_members_leaves_a_retired_member_alone(released):
    concept = released["host"] / ".lokf" / "knowledge" / "members" / "a.md"
    concept.write_text(concept.read_text(encoding="utf-8").replace("status: draft", "status: deprecated"), encoding="utf-8")
    r = members_run(released, "--dry-run")
    assert r.rc == 0 and "members/a: retired" in r.out and "path: members/b.md" in r.out, r.out
    assert "path: members/a.md" not in r.out, "no move is proposed for a retired member"


def test_a_dry_run_prints_the_patch_while_a_librarian_pull_request_is_open(released):
    host = released["host"]
    r = members_run(released, "--dry-run", prs='[{"number": 7}]')
    assert r.rc == 0 and "op: patch" in r.out and "pull request is already open" in r.out, r.out
    r = members_run(released, prs='[{"number": 7}]')
    assert r.rc == 0 and "already open; no patch written" in r.out, r.out
    assert not (host / ".lokf" / "patch.yaml").exists()


def test_members_add_drafts_a_member_from_a_repository_release(released):
    host = released["host"]
    r = members_run(released, "--add", "acme/e")
    assert r.rc == 0 and "5 member(s) moved or proposed" in r.out, r.out
    r = run(["bash", APPLY, "--root", host], cwd=host)
    assert r.rc == 0, r.out
    text = read(host / ".lokf" / "knowledge" / "members" / "e.md")
    fm = yaml.safe_load(text.split("---\n")[1])
    assert fm["type"] == "MemberBundle" and fm["status"] == "draft" and fm["version"] == "v1.1.0" and fm["base_iri"] == "https://e.example/knowledge/"
    assert fm["id"] == "https://d.example/federation/members/e" and fm["isPartOf"] == ["https://d.example/federation/domains/federation"] and fm["title"] == "E"
    assert [d["name"] for d in fm["distribution"]] == ["knowledge-v1.1.0-e.zip", "schema-v1.1.0-e.yaml"] and fm["distribution"][1]["media_type"] == "application/yaml"
    assert "This member is the knowledge bundle of [acme/e](https://github.com/acme/e). The description in its own index reads \"Help a person check the 'E' bundle\". It was released at v1.1.0" in text, text
    assert "acme/e is proposed as a member at v1.1.0; does it belong under the admission rule?" in text
    assert "**Added**: E, acme/e at v1.1.0" in read(host / ".lokf" / "knowledge" / "log.md")
    r = members_run(released, "--add", "acme/a")
    assert r.rc == 1 and "members/a.md exists already" in r.out, r.out
    r = members_run(released, "--add", "acme/nested")
    assert r.rc == 1 and "nests with members/a's https://a.example/knowledge/" in r.out, r.out
    r = members_run(released, "--add", "acme")
    assert r.rc == 1 and "--add takes owner/repo" in r.out, r.out
    r = members_run(released, "--add", "acme/f")
    assert r.rc == 0, r.out
    r = run(["bash", APPLY, "--root", host], cwd=host)
    assert r.rc == 0, r.out
    text = read(host / ".lokf" / "knowledge" / "members" / "f.md")
    fm = yaml.safe_load(text.split("---\n")[1])
    assert fm["type"] == "MemberDomain" and "It is itself a domain of 1 member, which the build follows." in text, text
    assert [d["name"] for d in fm["distribution"]] == ["knowledge-v1.1.0-f.zip", "workspace-v1.1.0.zip"], "a domain's release names its workspace"
    assert "The federation workflow attached its workspace as `workspace-v1.1.0.zip`, whose lock says which release of each member that domain built." in text, text
    assert 'The description in its own index reads "F." It was released at v1.1.0' in text, "a description that ends a sentence keeps its own full stop"


def test_members_names_the_workspace_a_member_domain_released(released):
    """f is a member domain: a move names the workspace its new release carries, and a member at the current release without one gets it in a patch of its own."""
    host = released["host"]
    top = "https://d.example/federation/domains/federation"
    f = github_member("f", top, type="MemberDomain", base_iri="https://f.example/federation/", generated={"by": "process:knowledge-federate", "at": "2026-10-16T10:00:00Z"})
    rewrite(host, "f", f)
    r = members_run(released, "--dry-run", stdout_only=True)
    assert r.rc == 0, r.out
    patch = yaml.safe_load(r.out)
    names = [d["name"] for d in ops_for(patch, "f")["patch"]["set"]["distribution"]]
    assert names == ["knowledge-v1.1.0-f.zip", "workspace-v1.1.0.zip"], names
    assert any(line.startswith("f: v1.0.0 -> v1.1.0; checksum matches") and "; workspace workspace-v1.1.0.zip checked, and its lock is that domain's" in line for line in patch["handoff"]), patch["handoff"]
    current = {**f, "version": NEW[0], "distribution": [{**f["distribution"][0], "name": "knowledge-v1.1.0-f.zip",
                                                         "access_url": f["distribution"][0]["access_url"].replace("v1.0.0", "v1.1.0")}]}
    rewrite(host, "f", current)
    r = members_run(released, "--dry-run", stdout_only=True)
    assert r.rc == 0, r.out
    ops = ops_for(yaml.safe_load(r.out), "f")
    assert [d["name"] for d in ops["patch"]["set"]["distribution"]] == ["knowledge-v1.1.0-f.zip", "workspace-v1.1.0.zip"] and set(ops["patch"]["set"]) == {"distribution"}
    assert ops["question"]["text"].startswith("acme/f attached its workspace, `workspace-v1.1.0.zip`, to v1.1.0 after this member moved to it; does this member name it?"), ops
    # The workspace attached again with other bytes: the checksum the member
    # names is stale, and the patch replaces that distribution alone.
    stale = {**current, "distribution": [*current["distribution"], {**ops["patch"]["set"]["distribution"][1], "checksum": "sha256:" + "1" * 64}]}
    rewrite(host, "f", stale)
    r = members_run(released, "--dry-run", stdout_only=True)
    assert r.rc == 0, r.out
    ops = ops_for(yaml.safe_load(r.out), "f")
    dists = ops["patch"]["set"]["distribution"]
    assert [d["name"] for d in dists] == ["knowledge-v1.1.0-f.zip", "workspace-v1.1.0.zip"] and dists[1]["checksum"] != "sha256:" + "1" * 64, dists
    assert "to v1.1.0 again, with other bytes, so the checksum this member names no longer matches" in ops["question"]["text"], ops
    rewrite(host, "f", {**current, "distribution": dists})
    r = members_run(released, "--dry-run")
    assert r.rc == 0 and "f: v1.1.0 is current" in r.out, "a member naming the workspace as attached is current\n" + r.out


def test_a_member_names_the_files_of_one_release(federation):
    """A workspace from another release of the same repository is refused before anything is fetched."""
    host = federation["host"]
    fm = github_member("g", federation["d_iri"] + "domains/federation", type="MemberDomain", base_iri="https://g.example/federation/")
    fm["distribution"].append({"name": "workspace-v1.1.0.zip", "access_url": "https://github.com/acme/g/releases/download/v1.1.0/workspace-v1.1.0.zip",
                               "media_type": "application/zip", "checksum": "sha256:" + "0" * 64})
    rewrite(host, "g", fm)
    r = federate(host, "build", "--verify-only", "--no-attestation")
    assert r.rc == 1 and "the workspace distribution is from release v1.1.0 of acme/g, and the zip from v1.0.0 of acme/g; a member names the files of one release" in r.out, r.out


def test_members_moves_the_others_when_one_cannot_be_checked_and_asks_gh_when_rate_limited(released):
    """The API refuses c's release list as rate limited, and a's cannot be reached.

    gh, holding the job's token, lists c's releases in its place, so c
    moves. a stays as it is, the others move, and the hand-off names a.
    """
    tmp = released["tmp"]
    served = json.loads(read(tmp / "served.json"))
    del served["https://api.github.com/repos/acme/a/releases?per_page=100"]
    served["https://api.github.com/repos/acme/c/releases?per_page=100"] = {"status": 403}
    write(tmp / "served.json", json.dumps(served))
    r = members_run(released, "--dry-run", stdout_only=True, env={"GH_TOKEN": "job-token", "FAKE_GH_API": tmp / "api"})
    assert r.rc == 0, r.out
    patch = yaml.safe_load(r.out)
    assert {op["path"] for op in patch["ops"]} == {"members/b.md", "members/c.md", "members/d.md"}, patch["ops"]
    assert patch["handoff"][0].startswith("members/a: could not be checked, so it stays as it is: acme/a: the release list could not be read"), patch["handoff"]
    del served["https://api.github.com/repos/acme/c/releases?per_page=100"]
    for slug in "bd":
        del served[f"https://api.github.com/repos/acme/{slug}/releases?per_page=100"]
    write(tmp / "served.json", json.dumps(served))
    r = members_run(released)
    assert r.rc == 1 and "members/d: could not be checked" in r.out and "no patch written" not in r.out, r.out


def test_members_hands_the_job_token_to_gh_alone(released):
    r = members_run(released, "--dry-run", attest=True)
    assert r.rc != 0 and "gh has no credential" in r.out and "AGENT_API_KEY_ENV to KNOWLEDGE_FEDERATE_TOKEN" in r.out, r.out
    r = members_run(released, "--dry-run", attest=True, env={"KNOWLEDGE_FEDERATE_TOKEN": "job-token"})
    assert r.rc == 0 and "attested by acme/a" in r.out, r.out


def test_members_moves_a_served_member_to_the_file_its_site_serves_now(tmp_path):
    """s releases no zip, and its site now serves another concepts.jsonld than the one its concept names.

    The patch sets the new checksum and, as the version, the day the file
    last changed, and moves that day in the text. The script keeps the
    validators it was sent, so a run that finds the file unchanged costs a
    304 and no download. `members --add <address>` drafts a member concept
    from a site's concepts.jsonld, with its title and description from the
    index.md the site serves beside it.
    """
    d_iri, s_iri, t_iri = "https://d.example/federation/", "https://s.example/knowledge/", "https://t.example/ktl/knowledge/"
    top, url = d_iri + "domains/federation", s_iri + "concepts.jsonld"
    s = make_bundle(tmp_path / "s", s_iri, "S", {"glossary/s.md": {"type": "GlossaryTerm", "title": "S term", "description": "S's term.", "resource": "https://example.test/s"}})
    s_site = export_bundle(s, tmp_path / "s-site")
    concept = {"type": "MemberBundle", "title": "s bundle", "description": "The s bundle its site served on 2026-10-01.", "resource": s_iri, "base_iri": s_iri,
               "version": "2026-10-01", "distribution": [{"name": "concepts.jsonld", "access_url": url, "media_type": "application/ld+json", "checksum": "sha256:" + "0" * 64}],
               "isPartOf": [top], "generated": {"by": "process:knowledge-federate", "at": "2026-10-16T10:00:00Z"}, "verified": [{"by": "human:noel", "at": "2026-10-16T12:00:00Z"}]}
    host = make_domain(tmp_path / "host", d_iri, {"s": concept})
    t = make_bundle(tmp_path / "t", t_iri, "T", {"glossary/t.md": {"type": "GlossaryTerm", "title": "T term", "description": "T's term.", "resource": "https://example.test/t"}},
                    description="The T bundle")
    t_site = export_bundle(t, tmp_path / "t-site")
    served = {url: {"path": str(s_site / "concepts.jsonld"), "headers": {"etag": '"s-1"', "last-modified": "Tue, 20 Oct 2026 09:00:00 GMT"}},
              t_iri + "concepts.jsonld": str(t_site / "concepts.jsonld"), t_iri + "index.md": str(t / "index.md")}
    write(tmp_path / "served.json", json.dumps(served))
    write(tmp_path / "runner.py", RUNNER)
    write(tmp_path / "bin" / "gh", FAKE_GH).chmod(0o755)
    released = {"host": host, "tmp": tmp_path}
    r = members_run(released, "--dry-run", stdout_only=True)
    assert r.rc == 0, r.out
    patch = yaml.safe_load(r.out)
    ops = ops_for(patch, "s")
    sha = hashlib.sha256((s_site / "concepts.jsonld").read_bytes()).hexdigest()
    assert ops["patch"]["set"]["version"] == "2026-10-20" and ops["patch"]["set"]["distribution"][0]["checksum"] == f"sha256:{sha}", ops
    assert ops["patch"]["set"]["description"] == "The s bundle its site served on 2026-10-20."
    assert f"{url} serves another file since the confirmed 2026-10-01, last changed on 2026-10-20; does this member move to it?" in ops["question"]["text"]
    assert any("served file read and written out, 1 concept(s)" in line for line in patch["handoff"]), patch["handoff"]
    log = tmp_path / "requests.log"
    r = members_run(released, "--dry-run", stdout_only=True, env={"RUNNER_LOG": str(log)})
    assert r.rc == 0 and yaml.safe_load(r.out) == patch and f"{url} 304" in log.read_text(encoding="utf-8"), "an unchanged file costs a 304"
    r = members_run(released, "--dry-run", "--add", t_iri, stdout_only=True)
    assert r.rc == 0, r.out
    created = ops_for(yaml.safe_load(r.out), "ktl")["create"]
    fm = created["frontmatter"]
    assert fm["type"] == "MemberBundle" and fm["base_iri"] == t_iri and fm["title"] == "T" and fm["version"] == today_utc(), fm
    assert fm["distribution"] == [{"name": "concepts.jsonld", "access_url": t_iri + "concepts.jsonld", "media_type": "application/ld+json",
                                   "checksum": "sha256:" + hashlib.sha256((t_site / "concepts.jsonld").read_bytes()).hexdigest()}]
    assert 'The description in its own index reads "The T bundle". Its site served `concepts.jsonld`' in created["body"] and "which releases no zip" in created["body"]


IN_PROCESS = r"""
import importlib.util, json, os, sys
spec = importlib.util.spec_from_file_location("federate", sys.argv[1])
federate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(federate)
here = os.getcwd()
missing = federate.run_lokf(["validate", sys.argv[2]])
broken = federate.run_lokf(["validate", "--schema", "absent.yaml", sys.argv[3]], cwd=sys.argv[3])
print(json.dumps({"missing": [missing.returncode, missing.stderr], "broken": [broken.returncode, broken.stderr], "cwd_kept": os.getcwd() == here}))
"""


def test_a_lokf_command_run_in_the_build_s_process_fails_as_a_process_would(tmp_path):
    """The build runs lokf's export and validate in its own process: a failing command reads as a failed command, and the working directory is put back."""
    k = make_bundle(tmp_path / "b", "https://b.example/knowledge/", "B", {})
    runner = write(tmp_path / "in-process.py", IN_PROCESS)
    r = run(["uv", "run", "--project", REPO / ".lokf", "python", "-I", runner, SCRIPT, tmp_path / "missing", k], cwd=tmp_path, stdout_only=True)
    got = json.loads(r.out.splitlines()[-1])
    assert got["missing"][0] != 0 and "missing" in got["missing"][1], f"validating a missing folder did not fail with its name: {got['missing']}"
    assert got["broken"][0] != 0 and got["broken"][1].strip(), f"validating against a missing schema did not fail with a message: {got['broken']}"
    assert got["cwd_kept"], "the build's working directory was not put back after a command run in another"
