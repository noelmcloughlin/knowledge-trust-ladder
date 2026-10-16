"""The federation build: knowledge-federate.py over fixture bundles.

Two tiny bundles and a domain that names them by zip are built under a
temporary host, and the script is run the way a host runs it, through the
repository's own sidecar environment (`uv run --project .lokf`), so the lokf
toolkit and pyoxigraph it needs are the ones the lock pins. It checks:

1. a build resolves the members into a lock, loads one named graph per
   bundle plus the lock graph, gates clean, and writes the same bytes twice;
2. a tampered checksum, a zip whose index.md names another base_iri, a zip
   holding a symbolic link, and a domain that names a bundle already in the
   federation each stop the build and leave the previous snapshot in place;
3. a typed relation whose target no member owns stops the build under
   `unowned_targets: fail` and is reported under `report`;
4. a member that is itself a domain is followed one tier down;
5. `--verify-only` writes nothing, and `members` leaves a non-GitHub member
   as it is.

`uv` is required: without it every test here skips and says so.
"""

from __future__ import annotations

import hashlib
import shutil
import stat
import zipfile
from pathlib import Path

import pytest

from conftest import REPO, SCRIPTS, have, run, write

SCRIPT = SCRIPTS / "knowledge-federate.py"
needs_uv = pytest.mark.skipif(not have("uv"), reason="uv is not installed - the federation build runs in the sidecar's environment")
pytestmark = needs_uv


def federate(host: Path, *args: str):
    return run(["uv", "run", "--project", REPO / ".lokf", SCRIPT, "--root", host, *args], cwd=host)


def frontmatter(**fields) -> str:
    import yaml

    return "---\n" + yaml.safe_dump(fields, sort_keys=False) + "---\n"


def make_bundle(root: Path, base_iri: str, title: str, concepts: dict[str, dict]) -> Path:
    """A bundle folder: index.md with the base_iri, and one concept per path."""
    k = root / "knowledge"
    write(k / "index.md", frontmatter(lokf_version="0.2", okf_version="0.2", base_iri=base_iri, title=title,
                                      description=f"{title}.", license="https://creativecommons.org/licenses/by/4.0/",
                                      publisher={"type": "Person", "id": base_iri + "person/x", "name": "X"})
          + f"\n# {title}\n")
    write(k / "log.md", "# Change Log\n\n## 2026-01-01\n\n* **Initialization**: fixture.\n")
    for path, fm in concepts.items():
        write(k / path, frontmatter(**fm) + f"\n# Overview\n\n{fm['title']}.\n")
    return k


def zip_bundle(knowledge: Path, zip_path: Path, symlink: bool = False) -> str:
    """The bundle as the release workflow packs it: root knowledge/, names sorted. Returns the sha256."""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(knowledge.rglob("*")):
            if p.is_file():
                zf.write(p, "knowledge/" + p.relative_to(knowledge).as_posix())
        if symlink:
            info = zipfile.ZipInfo("knowledge/link.md")
            info.create_system = 3
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            zf.writestr(info, "../../etc/passwd")
    return hashlib.sha256(zip_path.read_bytes()).hexdigest()


def member(slug: str, base_iri: str, zip_path: Path, sha: str, domain_iri: str, version: str = "v1.0.0") -> dict:
    return {
        "type": "MemberBundle", "title": f"{slug} bundle", "description": f"The {slug} bundle at {version}.",
        "resource": zip_path.as_uri(), "base_iri": base_iri, "version": version,
        "distribution": [{"name": zip_path.name, "access_url": zip_path.as_uri(), "media_type": "application/zip", "checksum": f"sha256:{sha}"}],
        "isPartOf": [domain_iri],
    }


def make_domain(host: Path, base_iri: str, members: dict[str, dict], policy: str = "fail", title: str = "D") -> Path:
    """A domain host: .lokf/knowledge with a Domain concept and the member concepts, and the report script for health lines."""
    domain_iri = base_iri + "domains/top"
    concepts = {"domains/top.md": {"type": "Domain", "title": "The top domain", "description": "The domain.", "resource": "https://example.test/d", "unowned_targets": policy}}
    concepts.update({f"members/{slug}.md": fm for slug, fm in members.items()})
    make_bundle(host / ".lokf", base_iri, title, concepts)
    scripts = host / ".lokf" / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    shutil.copy(SCRIPTS / "knowledge-report.sh", scripts / "knowledge-report.sh")
    return host


@pytest.fixture
def federation(tmp_path):
    """Bundles a and b (a relates to b across the boundary), zipped, and a domain naming both."""
    a_iri, b_iri, d_iri = "https://a.example/knowledge/", "https://b.example/knowledge/", "https://d.example/federation/"
    a = make_bundle(tmp_path / "a", a_iri, "A", {"glossary/term.md": {"type": "GlossaryTerm", "title": "Term", "description": "A term.", "resource": "https://example.test/a", "relatedTo": [b_iri + "glossary/other"]}})
    b = make_bundle(tmp_path / "b", b_iri, "B", {"glossary/other.md": {"type": "GlossaryTerm", "title": "Other", "description": "Another term.", "resource": "https://example.test/b"}})
    a_zip, b_zip = tmp_path / "a.zip", tmp_path / "b.zip"
    a_sha, b_sha = zip_bundle(a, a_zip), zip_bundle(b, b_zip)
    host = make_domain(tmp_path / "host", d_iri, {"a": member("a", a_iri, a_zip, a_sha, d_iri + "domains/top"), "b": member("b", b_iri, b_zip, b_sha, d_iri + "domains/top")})
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
    assert "path:" not in (snap / "lokf-registry.yaml").read_text(encoding="utf-8"), "the registry carries no runner path"
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
    top = host / ".lokf" / "knowledge" / "domains" / "top.md"
    top.write_text(top.read_text(encoding="utf-8").replace("unowned_targets: fail", "unowned_targets: report"), encoding="utf-8")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0, r.out
    assert "1 typed-relation target(s) lie in no member's namespace" in (host / "snapshot" / "gate-report.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("fault", ["checksum", "namespace", "symlink", "duplicate"])
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
    else:
        concept.write_text(text.replace("base_iri: https://b.example/knowledge/", "base_iri: https://a.example/knowledge/"), encoding="utf-8")
        expect = "already in the federation"
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 1 and expect in r.out, r.out
    assert (host / "snapshot" / "graph.nq").read_bytes() == before, "the previous snapshot stays"
    assert not (host / "snapshot.new").exists()


def test_a_member_that_is_a_domain_is_followed(federation, tmp_path):
    host = federation["host"]
    c_iri, s_iri = "https://c.example/knowledge/", "https://s.example/federation/"
    c = make_bundle(tmp_path / "c", c_iri, "C", {"glossary/third.md": {"type": "GlossaryTerm", "title": "Third", "description": "A third term.", "resource": "https://example.test/c"}})
    c_zip = tmp_path / "c.zip"
    c_sha = zip_bundle(c, c_zip)
    sub = make_bundle(tmp_path / "s", s_iri, "S", {"domains/top.md": {"type": "Domain", "title": "Sub", "description": "A sub-domain.", "resource": "https://example.test/s"},
                                                  "members/c.md": member("c", c_iri, c_zip, c_sha, s_iri + "domains/top")})
    s_zip = tmp_path / "s.zip"
    s_sha = zip_bundle(sub, s_zip)
    write(host / ".lokf" / "knowledge" / "members" / "s.md", frontmatter(**member("s", s_iri, s_zip, s_sha, federation["d_iri"] + "domains/top")) + "\n# Overview\n\nS.\n")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0, r.out
    lock = (host / "snapshot" / "workspace.lock.yaml").read_text(encoding="utf-8")
    assert "tier: 2" in lock and c_iri in lock and "member_of: https://s.example/federation/domains/top" in lock
    assert c_iri in graphs_in(host / "snapshot" / "graph.nq")


def test_verify_only_writes_nothing_and_members_leaves_a_local_zip_alone(federation):
    host = federation["host"]
    r = federate(host, "build", "--verify-only", "--no-attestation")
    assert r.rc == 0 and "nothing written" in r.out, r.out
    assert not (host / "snapshot").exists() and not (host / "snapshot.new").exists()
    r = federate(host, "members", "--dry-run", "--no-attestation")
    assert r.rc == 0 and "not a GitHub release" in r.out and "no patch written" in r.out, r.out
    assert not (host / ".lokf" / "patch.yaml").exists()
