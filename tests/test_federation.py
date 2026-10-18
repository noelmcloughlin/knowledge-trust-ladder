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
4a. the diamond rule: a bundle two domains name at one release joins once,
   named by both, and named at two releases it stops the build;
4b. the depth a build follows is the top Domain concept's `max_depth`, 3
   unless set, and a `MemberDomain` whose zip holds no Domain stops it;
4c. a concept a curator retired (`status: deprecated`) takes no part: a
   retired Domain concept is not a second top, and a retired member is
   neither built into the workspace nor moved by `members`;
5. `--verify-only` writes nothing, and `members` leaves a non-GitHub member
   as it is;
5a. a schema released beside a member's zip, named as a second distribution,
   is what the member's fit is checked against, and a wrong digest for it
   stops the build;
5b. `mcp` serves the workspace index as its instructions and answers the
   five tools of the specification's section 11.4, each bounded;
6. `members` moves a member's old tag, zip name and day in its description
   and body as well as its frontmatter, in a patch the pen applies, and
   names the lines it had to leave in its question;
7. its question calls a member "confirmed" only when a person confirmed the
   concept as it stands, and puts the move to a person as a question alone
   when a person wrote the concept;
8. a dry run prints the patch while a librarian pull request is open, and a
   real run then writes nothing;
9. `members --add owner/repo` drafts a member concept from that repository's
   newest bundle release, with the schema released beside it, as a
   `MemberDomain` when that release is a domain, and refuses a path that
   exists or a namespace that nests with a member's.
10. under the librarian wrapper, `members` hands the job token that arrives
    as KNOWLEDGE_FEDERATE_TOKEN to gh alone, and with no credential at all
    it stops and says which variables give it one.

The `members` tests run the script through a small runner that serves the
GitHub API and the release files from fixture files, and put a stand-in
`gh` first on PATH, so no test reaches the network or a real repository.

`uv` is required: without it every test here skips and says so.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import zipfile
from pathlib import Path

import pytest
import yaml

from conftest import REPO, SCRIPTS, have, read, run, write

SCRIPT = SCRIPTS / "knowledge-federate.py"
APPLY = SCRIPTS / "knowledge-apply.sh"
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


def member(slug: str, base_iri: str, zip_path: Path, sha: str, domain_iri: str, version: str = "v1.0.0", kind: str = "MemberBundle") -> dict:
    return {
        "type": kind, "title": f"{slug} bundle", "description": f"The {slug} bundle at {version}.",
        "resource": zip_path.as_uri(), "base_iri": base_iri, "version": version,
        "distribution": [{"name": zip_path.name, "access_url": zip_path.as_uri(), "media_type": "application/zip", "checksum": f"sha256:{sha}"}],
        "isPartOf": [domain_iri],
    }


def make_domain(host: Path, base_iri: str, members: dict[str, dict], policy: str = "fail", title: str = "D") -> Path:
    """A domain host: .lokf/knowledge with a Domain concept and the member concepts, and the report script for health lines."""
    domain_iri = base_iri + "domains/federation"
    concepts = {"domains/federation.md": {"type": "Domain", "title": "The federation domain", "description": "The domain.", "resource": "https://example.test/d", "unowned_targets": policy}}
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
    sub = make_bundle(tmp_path / "s", s_iri, "S", {"domains/s.md": {"type": "Domain", "title": "Sub", "description": "A sub-domain.", "resource": "https://example.test/s"},
                                                  "members/c.md": member("c", c_iri, c_zip, c_sha, s_iri + "domains/s")})
    s_zip = tmp_path / "s.zip"
    s_sha = zip_bundle(sub, s_zip)
    write(host / ".lokf" / "knowledge" / "members" / "s.md", frontmatter(**member("s", s_iri, s_zip, s_sha, federation["d_iri"] + "domains/federation")) + "\n# Overview\n\nS.\n")
    r = federate(host, "build", "--no-attestation")
    assert r.rc == 0, r.out
    lock = (host / "snapshot" / "workspace.lock.yaml").read_text(encoding="utf-8")
    entries = {m["base_iri"]: m for m in yaml.safe_load(lock)["members"]}
    assert entries[c_iri]["tier"] == 2 and entries[c_iri]["member_of"] == [s_iri + "domains/s"] and entries[s_iri]["kind"] == "domain"
    assert c_iri in graphs_in(host / "snapshot" / "graph.nq")


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


def test_verify_only_writes_nothing_and_members_leaves_a_local_zip_alone(federation):
    host = federation["host"]
    r = federate(host, "build", "--verify-only", "--no-attestation")
    assert r.rc == 0 and "nothing written" in r.out, r.out
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
# document with every answer.
MCP_CLIENT = """\
import asyncio, json, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
project, script, snapshot, calls = sys.argv[1:5]

def text(result):
    return "\\n".join(c.text for c in result.content if getattr(c, "type", "") == "text")

async def main():
    out = {"calls": []}
    params = StdioServerParameters(command="uv", args=["run", "--project", project, script, "mcp", "--snapshot", snapshot])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            init = await s.initialize()
            out["server"], out["instructions"] = init.server_info.name, init.instructions
            out["tools"] = [t.name for t in (await s.list_tools()).tools]
            for name, args in json.loads(calls):
                out["calls"].append(json.loads(text(await s.call_tool(name, args))))
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
             ("resolve_iri", {"iri": "https://nobody.example/knowledge/x"}), ("neighbors", {"iri": a_term, "depth": 9, "limit": 1})]
    client = write(tmp_path / "client.py", MCP_CLIENT)
    r = run(["uv", "run", "--project", REPO / ".lokf", "python", "-I", client, REPO / ".lokf", SCRIPT, host / "snapshot", json.dumps(calls)], cwd=tmp_path, stdout_only=True)
    assert r.rc == 0, r.out
    out = json.loads(r.out)
    assert out["server"] == "lokf-registry" and out["tools"] == ["resolve_iri", "neighbors", "subgraph", "federated_sparql", "read_document"]
    assert out["instructions"].startswith("The workspace of a LOKF federation") and "# D: the workspace" in out["instructions"], "the index is the server's instructions"
    index, resolved, near, sub, labels, service, doc, traversal, outside, cut = out["calls"]
    assert index["path"] == "index.md" and index["markdown"].startswith("# D: the workspace")
    assert resolved["owner"]["slug"] == "b" and resolved["concept"]["type"] == "GlossaryTerm" and resolved["concept"]["trust"]["trust_tier"]
    assert any(t["graph"] == federation["a_iri"] and t["object"]["value"] == b_other for t in near["triples"]), "the cross-bundle edge is asserted by a's graph"
    assert sub["format"] == "trig" and federation["a_iri"] in sub["rdf"] and sub["count"] == near["count"]
    assert "g" in labels["columns"] and labels["rows"] and not labels["truncated"]
    assert "SERVICE" in service["error"]
    assert doc["bundle"]["slug"] == "b" and doc["markdown"].startswith("---") and doc["trust"]["status"]
    assert "error" in traversal and outside["owner"] is None
    assert cut["truncated"] and cut["count"] == 1


# ---------------------------------------------------------------------------
# members against GitHub releases, served from fixture files
# ---------------------------------------------------------------------------
# Loads the script as a module, answers its HTTP requests from the files a
# JSON map names, and runs its main(); any other address fails as an
# unreachable one would.
RUNNER = """\
import importlib.util, json, pathlib, sys, urllib.error
script, served, *argv = sys.argv[1:]
spec = importlib.util.spec_from_file_location("knowledge_federate", script)
federate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(federate)
urls = json.loads(pathlib.Path(served).read_text(encoding="utf-8"))
def http_get(url, accept=None, timeout=60):
    if url not in urls:
        raise urllib.error.URLError(url + " is not served by this test")
    return pathlib.Path(urls[url]).read_bytes()
federate.http_get = http_get
sys.exit(federate.main(argv))
"""

# Answers `gh pr list` with the pull requests FAKE_GH_PRS names, and fails
# every other command, so the script never asks a real repository.
FAKE_GH = """\
#!/bin/sh
[ "$1 $2" = "pr list" ] && { printf '%s\\n' "${FAKE_GH_PRS:-[]}"; exit 0; }
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
    # e has a bundle release of its own and no member concept yet; nested's
    # release is bundle A again, whose namespace a member already holds.
    e_bundle = make_bundle(tmp_path / "e_bundle", "https://e.example/knowledge/", "E", {"glossary/e.md": {"type": "GlossaryTerm", "title": "E term", "description": "E's term.", "resource": "https://example.test/e"}})
    e_zip = tmp_path / "e.zip"
    e_sums = write(tmp_path / "e.zip.sha256", f"{zip_bundle(e_bundle, e_zip)}  e.zip\n")
    # f's release is a domain in turn: a Domain concept and one member.
    f_zip, f_sha = domain_zip(tmp_path, "f", "https://f.example/federation/", {"a": github_member("a", "https://f.example/federation/domains/f")})
    f_sums = write(tmp_path / "f.zip.sha256", f"{f_sha}  f.zip\n")
    for slug, zipped, summed in (("e", e_zip, e_sums), ("nested", zip_path, sums), ("f", f_zip, f_sums)):
        release = with_schema(github_release(slug, *NEW)) if slug == "e" else github_release(slug, *NEW)
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
    assert "This member is the knowledge bundle of [acme/e](https://github.com/acme/e). Its own index describes it as: E." in text
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
    assert yaml.safe_load(text.split("---\n")[1])["type"] == "MemberDomain" and "It is itself a domain of 1 member, which the build follows." in text, text


def test_members_hands_the_job_token_to_gh_alone(released):
    r = members_run(released, "--dry-run", attest=True)
    assert r.rc != 0 and "gh has no credential" in r.out and "AGENT_API_KEY_ENV to KNOWLEDGE_FEDERATE_TOKEN" in r.out, r.out
    r = members_run(released, "--dry-run", attest=True, env={"KNOWLEDGE_FEDERATE_TOKEN": "job-token"})
    assert r.rc == 0 and "attested by acme/a" in r.out, r.out
