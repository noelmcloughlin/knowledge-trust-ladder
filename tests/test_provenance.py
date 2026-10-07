"""knowledge-provenance.sh, the forge-free provenance gate, with throwaway keys.

This was checks 13, 13a and 22 in scripts/validate-repository.sh.

The signed form (check 13): a confirmation signed by the curator on file
passes, with a GPG primary key, a GPG signing subkey, or an SSH key. An
unsigned one, one by an id with no key, one by another key, and one whose own
key is added in the same range each fail, while another curator's key added
alongside does not. A removed confirmation needs its curator's signature as
an added one does, whether the event is struck out or its concept deleted. A
person's generated record may be replaced only by another person's. A
repository with no .lokf/curators/ is a stated skip. It needs gpg and
ssh-keygen, which CI has.

The unattended form (check 13a) needs no key and no forge. The scheduled
librarian's change is one nobody stands behind, so it may add, change or
remove no person's event in any YAML layout, add or remove no person's note,
and rewrite no text a person wrote. A process's own open question under a
person's text is none of those.

Parser parity (check 22): the gate reads a concept's `verified` and
`generated` events with a hand-written awk reader, not a YAML parser, for
portability. So a human event in a layout the reader skips, but a real parser
reads, is a forged confirmation the gate cannot challenge. For each layout a
person might write, the gate must flag an unsigned human event exactly when a
YAML parser sees one. This is what caught a multi-line flow event slipping
the gate, and a forgery hidden behind a byte order mark or in CRLF line
endings, which a bare-"---" first-line reader skipped.
"""

from __future__ import annotations

import shutil

import pytest
import yaml

from conftest import BOM, SCRIPTS, Git, bash, have, matches, read, replace_in, run, write

PROVENANCE = SCRIPTS / "knowledge-provenance.sh"


def confirmed(who):
    return f'---\ntype: Service\nverified:\n  - by: human:{who}\n    at: "2026-09-17T00:00:00Z"\n---\n'


@pytest.mark.skipif(
    not (have("gpg") and have("ssh-keygen")), reason="gpg or ssh-keygen not installed locally - CI runs the signed form"
)
def test_signed_confirmations(tmp_path, checks):
    pv = tmp_path
    gnupg = pv / "gnupg"
    gnupg.mkdir(mode=0o700)
    repo = pv / "repo"
    k = repo / ".lokf" / "knowledge" / "x"
    c = repo / ".lokf" / "curators"
    env = {"GNUPGHOME": str(gnupg)}

    def gpg(*args):
        return run(["gpg", "--batch", "--quiet", *args], env=env)

    def git(*args):
        result = run(["git", *args], cwd=repo, env=env)
        if result.rc != 0:
            raise RuntimeError(f"git {' '.join(str(a) for a in args)} failed: {result.out}")
        return result.out

    def expect(range_, status, want, what):
        result = run(["bash", PROVENANCE, *range_.split()], cwd=repo, env=env)
        checks.ok(
            result.rc == status and matches(result.out, want),
            f"provenance script did not {what}",
            f"exit {result.rc}: {result.out}",
        )

    def fingerprint(who):
        # Read gpg's output whole: an awk that exits on the first match closes
        # the pipe early, which a runner that ignores SIGPIPE reports as a write error.
        for line in gpg("--with-colons", "--list-keys", who).out.split("\n"):
            if line.startswith("fpr:"):
                return line.split(":")[9]
        raise RuntimeError(f"no fingerprint for {who}")

    generate = ["--pinentry-mode", "loopback", "--passphrase", "", "--quick-generate-key"]
    if not (
        gpg(*generate, "contract <contract@example.invalid>", "ed25519", "sign", "1d")
        and gpg(*generate, "other <other@example.invalid>", "ed25519", "sign", "1d")
        and gpg(*generate, "sub <sub@example.invalid>", "ed25519", "cert", "1d")
        and run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", "sshcur", "-f", pv / "sshcur"])
        and run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", "stranger", "-f", pv / "stranger"])
    ):
        pytest.fail("could not generate the provenance fixture's keys (gpg --quick-generate-key or ssh-keygen failed)")
    fpr = fingerprint("contract")
    fpr2 = fingerprint("other")
    fpr3 = fingerprint("sub@example.invalid")
    # The third key certifies only and signs with a subkey, the common layout.
    gpg("--pinentry-mode", "loopback", "--passphrase", "", "--quick-add-key", fpr3, "ed25519", "sign", "1d")
    run(["git", "init", "-q", repo])
    git("config", "user.name", "contract")
    git("config", "user.email", "contract@example.invalid")
    git("config", "gpg.format", "openpgp")
    git("config", "user.signingkey", fpr)
    k.mkdir(parents=True)
    c.mkdir(parents=True)
    write(c / "contract.asc", gpg("--armor", "--export", fpr).out + "\n")
    write(k / "a.md", "---\ntype: Service\n---\n")
    git("add", "-A")
    git("commit", "-q", "--no-gpg-sign", "-m", "base")
    write(k / "a.md", confirmed("contract"))
    git("commit", "-q", "-S", "-am", "confirm")
    expect("HEAD~1", 0, r"^OK - 1 confirmation", "pass a confirmation signed by the curator on file")
    # A confirmation is the whole event, not its `by:` line: re-dating an
    # existing one, in a flow-style layout or a block one, is a claim by that
    # curator; moving the concept is not, since events are keyed by its id.
    replace_in(k / "a.md", "2026-09-17T00:00:00Z", "2026-09-18T00:00:00Z")
    git("commit", "-q", "--no-gpg-sign", "-am", "redated, unsigned")
    expect("HEAD~1", 1, "is unsigned", "report a re-dated confirmation nobody signed")
    replace_in(k / "a.md", "2026-09-18T00:00:00Z", "2026-09-19T00:00:00Z")
    git("commit", "-q", "-S", "-am", "redated by its curator")
    expect("HEAD~1", 0, r"^OK - 1 confirmation", "pass a re-dated confirmation its curator signed")
    write(
        k / "flow.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/flow\nverified: [{ by: human:contract, at: "2026-09-17T00:00:00Z" }]\n---\n',
    )
    git("add", "-A")
    git("commit", "-q", "--no-gpg-sign", "-m", "flow style, unsigned")
    expect("HEAD~1", 1, "is unsigned", "see a flow-style event that leaves no by: line in the diff")
    git("mv", k / "flow.md", k / "moved.md")
    git("commit", "-q", "--no-gpg-sign", "-m", "moved, unsigned")
    expect("HEAD~1", 0, r"^OK - 0 confirmation", "let a confirmed concept move under its id without a new claim")
    write(k / "b.md", confirmed("contract"))
    git("add", "-A")
    git("commit", "-q", "--no-gpg-sign", "-m", "unsigned")
    expect("HEAD~1", 1, "is unsigned", "report an unsigned confirmation")
    write(k / "c.md", confirmed("nobody"))
    git("add", "-A")
    git("commit", "-q", "-S", "-m", "nobody")
    expect("HEAD~1", 1, "no key on file", "report an id with no key on file")
    write(k / "c2.md", confirmed("../odd"))
    git("add", "-A")
    git("commit", "-q", "--no-gpg-sign", "-m", "odd id")
    expect("HEAD~1", 1, "not a login this gate can check", "refuse an id it cannot look up rather than skip it")
    write(k / "d.md", confirmed("contract"))
    git("add", "-A")
    git("-c", f"user.signingkey={fpr2}", "commit", "-q", "-S", "-m", "wrongkey")
    expect("HEAD~1", 1, "signed by another key", "report a confirmation signed by a key that is not that curator's")
    write(c / "other.asc", gpg("--armor", "--export", fpr2).out + "\n")
    write(k / "e.md", confirmed("other"))
    git("add", "-A")
    git("-c", f"user.signingkey={fpr2}", "commit", "-q", "-S", "-m", "key and own confirmation")
    expect("HEAD~1", 1, "same range", "refuse a curator's own key and their confirmation in one range")
    write(k / "f.md", confirmed("other"))
    git("add", "-A")
    git("-c", f"user.signingkey={fpr2}", "commit", "-q", "-S", "-m", "confirm after the key landed")
    expect("HEAD~1", 0, r"^OK - 1 confirmation", "pass a confirmation once that key landed in an earlier range")
    write(c / "sub.asc", gpg("--armor", "--export", fpr3).out + "\n")
    git("add", "-A")
    git("commit", "-q", "-S", "-m", "subkey curator")
    write(k / "g.md", confirmed("sub"))
    git("add", "-A")
    git("-c", f"user.signingkey={fpr3}", "commit", "-q", "-S", "-m", "signed with the subkey")
    expect("HEAD~1", 0, r"^OK - 1 confirmation", "accept a signature made with a GPG signing subkey")
    shutil.copy(pv / "sshcur.pub", c / "sshcur.pub")
    git("add", "-A")
    git("commit", "-q", "-S", "-m", "ssh curator")
    write(k / "h.md", confirmed("sshcur"))
    git("add", "-A")
    git("-c", "gpg.format=ssh", "-c", f"user.signingkey={pv / 'sshcur.pub'}", "commit", "-q", "-S", "-m", "ssh signed")
    expect("HEAD~1", 0, r"^OK - 1 confirmation", "accept an SSH signature by the key on file")
    write(k / "i.md", confirmed("sshcur"))
    git("add", "-A")
    git(
        "-c",
        "gpg.format=ssh",
        "-c",
        f"user.signingkey={pv / 'stranger.pub'}",
        "commit",
        "-q",
        "-S",
        "-m",
        "ssh by a stranger",
    )
    expect("HEAD~1", 1, "not by a key in sshcur.pub", "report an SSH signature by a key not on file for that id")
    shutil.copy(pv / "stranger.pub", c / "stranger.pub")
    write(k / "j.md", confirmed("contract"))
    git("add", "-A")
    git("commit", "-q", "-S", "-m", "another key lands beside a confirmation")
    expect("HEAD~1", 0, r"^OK - 1 confirmation", "let another curator's key land beside a confirmation")
    # Only the frontmatter is a claim: an example event in a body code fence
    # is not, and a human `generated` record, which the curator's Correct
    # writes, is, whatever its layout.
    write(
        k / "fence.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/fence\n---\n\n```yaml\nverified:\n  - by: human:contract\n    at: "2026-09-17T00:00:00Z"\n```\n',
    )
    git("add", "-A")
    git("commit", "-q", "--no-gpg-sign", "-m", "example in a fence, unsigned")
    expect("HEAD~1", 0, r"^OK - 0 confirmation", "ignore an example event in a body code fence")
    write(
        k / "gen.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/gen\ngenerated: { by: human:contract, at: "2026-09-17T00:00:00Z" }\n---\n',
    )
    git("add", "-A")
    git("commit", "-q", "--no-gpg-sign", "-m", "human generated, flow style, unsigned")
    expect("HEAD~1", 1, "is unsigned", "read a flow-style human generated record as a claim")
    # A flow verified/generated that spans lines is valid YAML every parser
    # reads, so the gate must see the event too: a block-only reader skipped
    # it and let an unsigned confirmation through.
    write(
        k / "mlflow.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/mlflow\nverified: [\n  { by: human:contract, at: "2026-09-17T00:00:00Z" }\n]\n---\n',
    )
    git("add", "-A")
    git("commit", "-q", "--no-gpg-sign", "-m", "multi-line flow sequence, unsigned")
    expect("HEAD~1", 1, "is unsigned", "see a human event in a flow sequence that spans lines")
    write(
        k / "mlgen.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/mlgen\ngenerated: {\n  by: human:contract,\n  at: "2026-09-17T00:00:00Z"\n}\n---\n',
    )
    git("add", "-A")
    git("commit", "-q", "--no-gpg-sign", "-m", "multi-line flow mapping, unsigned")
    expect("HEAD~1", 1, "is unsigned", "see a human generated record in a flow mapping that spans lines")
    # Names git would quote by default: a byte above 0x7f is read like any
    # other concept; a double quote is refused. Neither is silently dropped.
    write(k / "café.md", confirmed("contract"))
    git("add", "-A")
    git("commit", "-q", "-S", "-m", "utf-8 name, signed")
    expect("HEAD~1", 0, r"^OK - 1 confirmation", "read a concept whose name holds a byte above 0x7f")
    write(k / 'qu"ote.md', confirmed("contract"))
    git("add", "-A")
    git("commit", "-q", "--no-gpg-sign", "-m", "quoted name, unsigned")
    expect("HEAD~1", 1, "cannot read", "refuse a concept path git has to quote rather than pass it unread")
    # A merge that brings in a confirmation its curator signed claims nothing;
    # one that adds an event neither side held is a claim by whoever merged.
    trunk = git("rev-parse", "--abbrev-ref", "HEAD")
    git("checkout", "-q", "-b", "side")
    write(repo / "side.txt", "side\n")
    git("add", "-A")
    git("commit", "-q", "--no-gpg-sign", "-m", "side work")
    git("checkout", "-q", trunk)
    write(k / "m.md", confirmed("contract"))
    git("add", "-A")
    git("commit", "-q", "-S", "-m", "confirmed on the trunk")
    git("checkout", "-q", "side")
    git("merge", "-q", "--no-gpg-sign", "--no-edit", trunk)
    expect("HEAD~1", 0, r"^OK - 1 confirmation", "let a merge bring in a confirmation its curator signed")
    git("checkout", "-q", trunk)
    write(repo / "more.txt", "more\n")
    git("add", "-A")
    git("commit", "-q", "--no-gpg-sign", "-m", "unrelated on the trunk")
    git("checkout", "-q", "side")
    git("merge", "-q", "--no-commit", "--no-ff", trunk)
    write(k / "evil.md", confirmed("contract"))
    git("add", "-A")
    git("commit", "-q", "--no-gpg-sign", "-m", "evil merge")
    expect("HEAD~1", 1, "is unsigned", "read an event a merge adds that neither side held")
    git("checkout", "-q", trunk)
    # A person's record is never removed without that person: striking an
    # event out, or deleting the concept that carries it, is a claim its
    # curator signs. A person's generated record may give way to another
    # person's, the curator's Correct, which that person signs as their own;
    # it may not give way to a process's.
    write(k / "j.md", "---\ntype: Service\n---\n")
    git("commit", "-q", "--no-gpg-sign", "-am", "event struck out, unsigned")
    expect(
        "HEAD~1",
        1,
        "removes a confirmation by human:contract but is unsigned",
        "report a confirmation struck out by an unsigned commit",
    )
    write(k / "b.md", "---\ntype: Service\n---\n")
    git("commit", "-q", "-S", "-am", "event struck out by its curator")
    expect("HEAD~1", 0, r"^OK - 1 confirmation", "pass a confirmation its own curator struck out and signed")
    git("rm", "-q", k / "d.md")
    git("commit", "-q", "--no-gpg-sign", "-m", "confirmed concept deleted, unsigned")
    expect(
        "HEAD~1",
        1,
        "removes a confirmation by human:contract but is unsigned",
        "report the deletion of a concept a person confirmed",
    )
    write(
        k / "gen.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/gen\ngenerated: { by: human:other, at: "2026-09-20T00:00:00Z" }\n---\n',
    )
    git("-c", f"user.signingkey={fpr2}", "commit", "-q", "-S", "-am", "corrected by another curator")
    expect(
        "HEAD~1",
        0,
        r"^OK - 1 confirmation",
        "let one person's generated record give way to another's, signed by the second",
    )
    write(
        k / "gen.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/gen\ngenerated: { by: process:ktl-librarian, at: "2026-09-21T00:00:00Z" }\n---\n',
    )
    git("commit", "-q", "--no-gpg-sign", "-am", "restamped by a process, unsigned")
    expect(
        "HEAD~1",
        1,
        "removes a confirmation by human:other but is unsigned",
        "report a person's generated record replaced by a process's",
    )
    git("rm", "-rq", ".lokf/curators")
    git("commit", "-q", "-S", "-m", "nokeys")
    expect("HEAD~1", 0, r"^skipped", "say so and pass with no .lokf/curators/")


@pytest.fixture
def unattended(tmp_path):
    """A committed bundle with a confirmed concept, one a person wrote, one with a person's note, and a plain one."""
    uk = tmp_path / ".lokf" / "knowledge" / "x"
    write(
        uk / "confirmed.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/confirmed\nverified:\n  - by: human:ada\n    at: "2026-09-17T00:00:00Z"\n---\n\n# Overview\n\nConfirmed text.\n',
    )
    write(
        uk / "authored.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/authored\ngenerated:\n  by: human:ada\n  at: "2026-09-17T00:00:00Z"\n---\n\n# Overview\n\nWritten by a person.\n',
    )
    write(
        uk / "noted.md",
        "---\ntype: Service\nid: https://example.invalid/k/x/noted\n---\n\n# Overview\n\n## Open questions\n\n- 2026-09-17, human:ada: send this back\n",
    )
    write(uk / "plain.md", "---\ntype: Service\nid: https://example.invalid/k/x/plain\n---\n\n# Overview\n")
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    return tmp_path


def append(path, text):
    write(path, read(path) + text)


UNATTENDED = [
    (
        "pass a change that edits a draft and a confirmed concept and touches no person's record",
        lambda uk: (
            append(uk / "plain.md", "\nA paragraph the librarian adds.\n"),
            append(uk / "confirmed.md", "\nAnother.\n"),
        ),
        0,
        r"^OK - the change against HEAD",
    ),
    (
        "refuse a person's event added in a flow layout no line pattern sees",
        lambda uk: write(
            uk / "plain.md",
            '---\ntype: Service\nid: https://example.invalid/k/x/plain\nverified: [{ by: human:ada, at: "2026-09-18T00:00:00Z" }]\n---\n\n# Overview\n',
        ),
        1,
        "x/plain: an unattended change adds or changes a confirmation by human:ada",
    ),
    (
        "refuse a person's event in a concept not yet tracked",
        lambda uk: write(
            uk / "new.md",
            '---\ntype: Service\nid: https://example.invalid/k/x/new\nverified:\n  - by: human:ada\n    at: "2026-09-18T00:00:00Z"\n---\n',
        ),
        1,
        "x/new: an unattended change adds or changes a confirmation by human:ada",
    ),
    (
        "refuse the deletion of a concept a person confirmed",
        lambda uk: (uk / "confirmed.md").unlink(),
        1,
        "x/confirmed: an unattended change removes a confirmation by human:ada",
    ),
    (
        "refuse a person's event re-dated",
        lambda uk: replace_in(uk / "confirmed.md", "2026-09-17T00:00:00Z", "2026-09-19T00:00:00Z"),
        1,
        "x/confirmed: an unattended change removes a confirmation by human:ada",
    ),
    (
        "refuse a note added in a person's name",
        lambda uk: append(uk / "noted.md", "- 2026-09-18, human:ada: looks right to me\n"),
        1,
        "noted.md: an unattended change adds a note in a person",
    ),
    (
        "refuse a person's note removed",
        lambda uk: write(
            uk / "noted.md", "---\ntype: Service\nid: https://example.invalid/k/x/noted\n---\n\n# Overview\n"
        ),
        1,
        "noted.md: an unattended change removes a person's note",
    ),
    (
        "refuse a change to text a person wrote",
        lambda uk: replace_in(uk / "authored.md", "Written by a person.", "Rewritten by an agent."),
        1,
        "authored.md: a person wrote this text, and an unattended change rewrites it",
    ),
    (
        "pass a process's own question added under text a person wrote",
        lambda uk: append(
            uk / "authored.md",
            "\n## Open questions\n\n- 2026-09-18, process:ktl-librarian: the source now says otherwise\n",
        ),
        0,
        r"^OK - the change against HEAD",
    ),
]


@pytest.mark.parametrize(("what", "change", "status", "want"), UNATTENDED, ids=[w for w, *_ in UNATTENDED])
def test_unattended_gate(unattended, what, change, status, want):
    change(unattended / ".lokf" / "knowledge" / "x")
    result = bash(PROVENANCE, "--unattended", cwd=unattended)
    assert result.rc == status and matches(result.out, want), (
        f"unattended gate did not {what} (exit {result.rc}): {result.out}"
    )


@pytest.fixture
def parity(tmp_path):
    """A committed draft with no event, for the layouts to be written over."""
    ppk = tmp_path / ".lokf" / "knowledge" / "x"
    write(tmp_path / ".lokf" / "knowledge" / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n")
    write(
        ppk / "c.md",
        "---\ntype: Service\nid: https://acme.example/knowledge/x/c\ntitle: C\nstatus: draft\n---\n\n# C\n",
    )
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "a draft with no event")
    return tmp_path


def concept_with(layout):
    return (
        f"---\ntype: Service\nid: https://acme.example/knowledge/x/c\ntitle: C\nstatus: draft\n{layout}\n---\n\n# C\n"
    )


def parser_sees_a_human(path):
    """What a YAML parser reads: a human actor on any `verified` or `generated` event."""
    text = read(path)
    front = text.split("\n---\n", 1)[0]
    front = front[4:] if front.startswith("---\n") else front
    try:
        data = yaml.safe_load(front) or {}
    except yaml.YAMLError:
        data = {}
    for key in ("verified", "generated"):
        value = data.get(key) if isinstance(data, dict) else None
        for event in [value] if isinstance(value, dict) else value if isinstance(value, list) else []:
            if isinstance(event, dict) and str(event.get("by", "")).startswith("human:"):
                return True
    return False


LAYOUTS = [
    'verified:\n- by: human:ada\n  at: "2026-01-02T10:00:00Z"',
    'verified: [{ by: human:ada, at: "2026-01-02T10:00:00Z" }]',
    'verified: [\n  { by: human:ada, at: "2026-01-02T10:00:00Z" }\n]',
    'generated: { by: human:ada, at: "2026-01-02T10:00:00Z" }',
    'generated: {\n  by: human:ada,\n  at: "2026-01-02T10:00:00Z"\n}',
    'verified:\n  - by: process:ktl-librarian\n    at: "2026-01-01T00:00:00Z"\n  - by: human:ada\n    at: "2026-01-02T10:00:00Z"',
    "verified:\n  - by: human:ada\n    at: 2026-01-02T10:00:00+00:00",
    "verified: [ ]",
    'verified:\n  - by: process:ktl-librarian\n    at: "2026-01-01T00:00:00Z"',
]


@pytest.mark.parametrize("layout", LAYOUTS, ids=[f"layout {n}" for n in range(1, len(LAYOUTS) + 1)])
def test_the_gate_agrees_with_a_yaml_parser(parity, layout):
    path = parity / ".lokf" / "knowledge" / "x" / "c.md"
    write(path, concept_with(layout))
    parser = parser_sees_a_human(path)
    result = bash(PROVENANCE, "--unattended", cwd=parity)
    gate = result.rc != 0
    assert parser == gate, (
        f"the gate and a YAML parser disagree: the parser sees {'human' if parser else 'none'}, the gate sees {'human' if gate else 'none'} ({result.out})"
    )


HUMAN = 'verified:\n- by: human:ada\n  at: "2026-01-02T10:00:00Z"'


def test_the_gate_flags_an_unsigned_human_event_behind_a_byte_order_mark(parity):
    """A reader that keys on a bare "---" first line sees neither the frontmatter nor the event, though every YAML parser strips the mark."""
    path = parity / ".lokf" / "knowledge" / "x" / "c.md"
    write(path, BOM + concept_with(HUMAN).encode("utf-8"))
    result = bash(PROVENANCE, "--unattended", cwd=parity)
    assert result.rc != 0, f"the gate missed an unsigned human event behind a byte order mark: {result.out}"


def test_the_gate_flags_an_unsigned_human_event_in_crlf_line_endings(parity):
    path = parity / ".lokf" / "knowledge" / "x" / "c.md"
    write(path, concept_with(HUMAN).replace("\n", "\r\n"))
    result = bash(PROVENANCE, "--unattended", cwd=parity)
    assert result.rc != 0, f"the gate missed an unsigned human event in CRLF line endings: {result.out}"
