"""knowledge-provenance.sh, the forge-free provenance gate, with throwaway keys.

This was checks 13, 13a and 22 in scripts/validate-repository.sh.

The signed form (check 13): a confirmation signed by the curator on file
passes, with a GPG primary key, a GPG signing subkey, or an SSH key. An
unsigned one, one by an id with no key, one by another key, and one whose own
key is added in the same range each fail, while another curator's key added
alongside does not. A removed confirmation needs its curator's signature as
an added one does, whether the event is struck out or its concept deleted. A
person's generated record may be replaced by another person's, or by the
curator's process when the person it names releases the text they wrote, and
by nothing else. Each change needs the signature of the person who backs it.
A repository with no .lokf/curators/ is a stated skip. It needs gpg and
ssh-keygen, which CI has.

The unattended form (check 13a) needs no key and no forge. The scheduled
librarian's change is one nobody stands behind, so it may add, change or
remove no person's event in any YAML layout, add or remove no person's note,
and rewrite no text a person wrote. A process's own open question under a
person's text is none of those, and nor is a rewrite of text its author
released.

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

import os
import shutil

import pytest
import yaml

from conftest import BOM, SCRIPTS, WORKFLOWS, Git, bash, have, matches, read, replace_in, run, write

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
    expect("HEAD~1", 0, r"^OK - 1 concept\(s\) hold a person's record", "pass a confirmation signed by the curator on file")
    # A confirmation is the whole event, not its `by:` line: re-dating an
    # existing one, in a flow-style layout or a block one, is a claim by that
    # curator; moving the concept is not, since events are keyed by its id.
    replace_in(k / "a.md", "2026-09-17T00:00:00Z", "2026-09-18T00:00:00Z")
    git("commit", "-q", "--no-gpg-sign", "-am", "redated, unsigned")
    expect("HEAD~1", 1, "is unsigned", "report a re-dated confirmation nobody signed")
    replace_in(k / "a.md", "2026-09-18T00:00:00Z", "2026-09-19T00:00:00Z")
    git("commit", "-q", "-S", "-am", "redated by its curator")
    expect("HEAD~1", 0, r"^OK - 1 concept\(s\) hold a person's record", "pass a re-dated confirmation its curator signed")
    # One curator confirming two concepts in one commit counts two, not one.
    write(k / "b.md", confirmed("contract"))
    write(k / "c.md", confirmed("contract"))
    git("add", "-A")
    git("commit", "-q", "-S", "-m", "confirm two")
    expect("HEAD~1", 0, r"^OK - 2 concept\(s\) hold a person's record", "count each concept one commit confirms")
    git("reset", "-q", "--hard", "HEAD~1")
    write(
        k / "flow.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/flow\nverified: [{ by: human:contract, at: "2026-09-17T00:00:00Z" }]\n---\n',
    )
    git("add", "-A")
    git("commit", "-q", "--no-gpg-sign", "-m", "flow style, unsigned")
    expect("HEAD~1", 1, "is unsigned", "see a flow-style event that leaves no by: line in the diff")
    git("mv", k / "flow.md", k / "moved.md")
    git("commit", "-q", "--no-gpg-sign", "-m", "moved, unsigned")
    expect("HEAD~1", 0, r"^OK - 0 concept\(s\) hold a person's record", "let a confirmed concept move under its id without a new claim")
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
    expect("HEAD~1", 0, r"^OK - 1 concept\(s\) hold a person's record", "pass a confirmation once that key landed in an earlier range")
    write(c / "sub.asc", gpg("--armor", "--export", fpr3).out + "\n")
    git("add", "-A")
    git("commit", "-q", "-S", "-m", "subkey curator")
    write(k / "g.md", confirmed("sub"))
    git("add", "-A")
    git("-c", f"user.signingkey={fpr3}", "commit", "-q", "-S", "-m", "signed with the subkey")
    expect("HEAD~1", 0, r"^OK - 1 concept\(s\) hold a person's record", "accept a signature made with a GPG signing subkey")
    shutil.copy(pv / "sshcur.pub", c / "sshcur.pub")
    git("add", "-A")
    git("commit", "-q", "-S", "-m", "ssh curator")
    write(k / "h.md", confirmed("sshcur"))
    git("add", "-A")
    git("-c", "gpg.format=ssh", "-c", f"user.signingkey={pv / 'sshcur.pub'}", "commit", "-q", "-S", "-m", "ssh signed")
    expect("HEAD~1", 0, r"^OK - 1 concept\(s\) hold a person's record", "accept an SSH signature by the key on file")
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
    expect("HEAD~1", 0, r"^OK - 1 concept\(s\) hold a person's record", "let another curator's key land beside a confirmation")
    # Only the frontmatter is a claim: an example event in a body code fence
    # is not, and a human `generated` record, which the curator's Correct
    # writes, is, whatever its layout.
    write(
        k / "fence.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/fence\n---\n\n```yaml\nverified:\n  - by: human:contract\n    at: "2026-09-17T00:00:00Z"\n```\n',
    )
    git("add", "-A")
    git("commit", "-q", "--no-gpg-sign", "-m", "example in a fence, unsigned")
    expect("HEAD~1", 0, r"^OK - 0 concept\(s\) hold a person's record", "ignore an example event in a body code fence")
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
    expect("HEAD~1", 0, r"^OK - 1 concept\(s\) hold a person's record", "read a concept whose name holds a byte above 0x7f")
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
    expect("HEAD~1", 0, r"^OK - 1 concept\(s\) hold a person's record", "let a merge bring in a confirmation its curator signed")
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
    expect("HEAD~1", 0, r"^OK - 1 concept\(s\) hold a person's record", "pass a confirmation its own curator struck out and signed")
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
        r"^OK - 1 concept\(s\) hold a person's record",
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
    # A person may release the text they wrote to the librarian: ktl-curator's
    # send-back names process:ktl-curator in their generated record and keeps
    # the time. Only that person can sign the release.
    git("reset", "-q", "--hard", "HEAD~1")
    write(
        k / "gen.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/gen\ngenerated: { by: process:ktl-curator, at: "2026-09-20T00:00:00Z" }\n---\n',
    )
    git("commit", "-q", "-S", "-am", "released, signed by another curator")
    expect(
        "HEAD~1",
        1,
        "removes a confirmation by human:other but is signed by another key",
        "report a person's text released under another curator's signature",
    )
    git("-c", f"user.signingkey={fpr2}", "commit", "-q", "-S", "--amend", "-m", "released by the person who wrote it")
    expect(
        "HEAD~1",
        0,
        r"^OK - 1 concept\(s\) hold a person's record",
        "let a person release their own text to the curator's process, signed by them",
    )
    git("rm", "-rq", ".lokf/curators")
    git("commit", "-q", "-S", "-m", "nokeys")
    expect("HEAD~1", 0, r"^OK - 0 concept\(s\) hold a person's record", "read a range that deletes the keys and records nobody, and pass it")
    git("commit", "-q", "-S", "--allow-empty", "-m", "still no keys")
    expect("HEAD~1", 0, r"^skipped", "say so and pass with no .lokf/curators/")


@pytest.fixture
def unattended(tmp_path):
    """A committed bundle with a confirmed concept, one a person wrote, one its author released, one with a person's note, and a plain one."""
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
    write(
        uk / "released.md",
        '---\ntype: Service\nid: https://example.invalid/k/x/released\ngenerated:\n  by: process:ktl-curator\n  at: "2026-09-17T00:00:00Z"\nverified:\n  - by: human:ada\n    at: "2026-09-17T00:00:00Z"\nstatus: draft\n---\n\n# Overview\n\nWritten by a person, then released.\n\n## Open questions\n\n- 2026-09-18, human:ada: bring this up to date with its source\n',
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
    (
        "pass a rewrite of text its author released on a send-back",
        lambda uk: (
            replace_in(uk / "released.md", "Written by a person, then released.", "Rewritten by the librarian."),
            replace_in(
                uk / "released.md",
                'by: process:ktl-curator\n  at: "2026-09-17T00:00:00Z"',
                'by: process:ktl-librarian\n  at: "2026-09-19T00:00:00Z"',
            ),
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
    'verified:\n  -\n    by: human:ada\n    at: "2026-01-02T10:00:00Z"\n  -\n    by: process:x\n    at: "2026-01-02T10:00:00Z"',
    'verified: [\n  { at: "2026-01-02T10:00:00Z", by: human:ada }\n]',
    'verified:\n  - # a comment line opens the item\n    by: human:ada\n    at: "2026-01-02T10:00:00Z"',
    '"verified": [{ by: human:ada, at: "2026-01-02T10:00:00Z" }]',
    "'verified':\n  - by: human:ada\n    at: \"2026-01-02T10:00:00Z\"",
    '"verifie\\x64":\n  - by: human:ada\n    at: "2026-01-02T10:00:00Z"',
    'verified : [{ by: human:ada, at: "2026-01-02T10:00:00Z" }]',
    '? verified\n: - by: human:ada\n    at: "2026-01-02T10:00:00Z"',
    '<<: { verified: [{ by: human:ada, at: "2026-01-02T10:00:00Z" }] }',
    'revised: &who { by: human:ada, at: "2026-01-02T10:00:00Z" }\nverified:\n  - *who',
    'revised: &who { by: human:ada, at: "2026-01-02T10:00:00Z" }\nverified:\n  - <<: *who',
    'verified:\n  - "by": human:ada\n    at: "2026-01-02T10:00:00Z"',
    'verified:\n  - "b\\x79": human:ada\n    at: "2026-01-02T10:00:00Z"',
    'verified:\n  - by : human:ada\n    at: "2026-01-02T10:00:00Z"',
    'verified:\n  - by: !!str human:ada\n    at: "2026-01-02T10:00:00Z"',
    'verified:\n  - !!str by: human:ada\n    at: "2026-01-02T10:00:00Z"',
    'verified:\n  - by:\n      human:ada\n    at: "2026-01-02T10:00:00Z"',
    'verified:\n  - by: >-\n      human:ada\n    at: "2026-01-02T10:00:00Z"',
    'verified:\n  - by: "hum\\x61n:ada"\n    at: "2026-01-02T10:00:00Z"',
    'verified:\n  - by: "\\x68uman:ada/x"\n    at: "2026-01-02T10:00:00Z"',
    'verified: [ # ]\n  { by: human:ada, at: "2026-01-02T10:00:00Z" }\n]',
    'verified:\n  - &e { by: human:ada, at: "2026-01-02T10:00:00Z" }',
    '"generated": { by: human:ada, at: "2026-01-02T10:00:00Z" }',
    'verified: null',
    'verified: [{ by: process:x, at: "2026-01-02T10:00:00Z" },]',
    'verified:\n  - # a comment line opens the item\n    by: process:x\n    at: "2026-01-02T10:00:00Z"',
    'exclusions:\n  - resource: a\n    reason: b\n    by: human:ada',
    'revised:\n  by: human:ada\n  at: "2026-01-02T10:00:00Z"',
    # A comment in the first column once ended the block for the gate, and the event below it went unread.
    'verified:\n  - by: process:ktl-librarian\n    at: "2026-01-01T00:00:00Z"\n# a note in the first column\n  - by: human:ada\n    at: "2026-01-02T10:00:00Z"',
    # A bracket inside a quoted value once closed the flow list for the gate, and the next line was read by no rule.
    'verified: [ { by: "process:ktl-librarian", at: "2026-01-01T00:00:00Z", revision: "W/]" },\n  { by: "human:ada", at: "2026-01-02T10:00:00Z" } ]',
    'generated: { by: "process:x", at: "2026-01-01T00:00:00Z", revision: "a}b" }\nverified:\n  - by: human:ada\n    at: "2026-01-02T10:00:00Z"',
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

# Shapes the toolkit reads as frontmatter and a line reader cannot follow, each
# holding a person's event. They do not fit concept_with, and a parser run on
# the text between two bare "---" lines would not see them either, as the
# toolkit does.
BLOCK = 'type: Service\nid: https://acme.example/knowledge/x/c\ntitle: C\nstatus: draft\n'
EVENT = 'verified:\n  - by: human:ada\n    at: "2026-01-02T10:00:00Z"\n'
WHOLE_FILES = {
    "the block indented whole": '---\n  type: Service\n  verified:\n    - by: human:ada\n      at: "2026-01-02T10:00:00Z"\n---\n\n# C\n',
    "one flow mapping": '---\n{type: Service, verified: [{by: human:ada, at: "2026-01-02T10:00:00Z"}]}\n---\n\n# C\n',
    "a bare carriage return": f"---\n{BLOCK}note: x\rverified:\r  - by: human:ada\n---\n\n# C\n",
    "U+2028": f"---\n{BLOCK}note: x{chr(0x2028)}verified:{chr(0x2028)}  - by: human:ada\n---\n\n# C\n",
    "U+0085": f"---\n{BLOCK}note: x{chr(0x85)}verified:{chr(0x85)}  - by: human:ada\n---\n\n# C\n",
    "a space after the opener": f"--- \n{BLOCK}{EVENT}---\n\n# C\n",
    "a blank line before the opener": f"\n---\n{BLOCK}{EVENT}---\n\n# C\n",
    "an indented opener": f"  ---\n{BLOCK}{EVENT}---\n\n# C\n",
    "text before the opener": f"note\n---\n{BLOCK}{EVENT}---\n\n# C\n",
    "carriage returns alone": f"---\n{BLOCK}{EVENT}---\n\n# C\n".replace("\n", "\r"),
}


@pytest.mark.parametrize("shape", WHOLE_FILES)
def test_the_gate_refuses_frontmatter_it_cannot_read(parity, shape):
    write(parity / ".lokf" / "knowledge" / "x" / "c.md", WHOLE_FILES[shape].encode("utf-8"))
    result = bash(PROVENANCE, "--unattended", cwd=parity)
    assert result.rc != 0 and "cannot read" in result.out, f"the gate passed {shape}: {result.out}"


def test_a_log_with_rules_is_not_refused_as_frontmatter_it_cannot_read(parity):
    write(parity / ".lokf" / "knowledge" / "log.md", "# Change Log\n\n---\n\n## 2026-01-02\n\n---\n")
    result = bash(PROVENANCE, "--unattended", cwd=parity)
    assert result.rc == 0, f"the gate refused a log that holds two rules: {result.out}"


def test_the_signed_form_refuses_frontmatter_it_cannot_read(parity):
    """A commit needs no key to be refused here, so the test needs no gpg."""
    write(parity / ".lokf" / "curators" / ".gitkeep", "")
    git = Git(parity)
    git("add", "-A")
    git("commit", "-q", "-m", "the curators folder")
    write(parity / ".lokf" / "knowledge" / "x" / "c.md", concept_with('"verified": [{ by: human:ada, at: "2026-01-02T10:00:00Z" }]'))
    git("add", "-A")
    git("commit", "-q", "-m", "an event in a quoted key")
    result = bash(PROVENANCE, "HEAD~1", "HEAD", cwd=parity)
    assert result.rc != 0 and "cannot read" in result.out, f"the signed form passed a quoted key: {result.out}"


FORGED = '---\ntype: Service\nid: https://acme.example/knowledge/x/f\nverified:\n  - by: human:ada\n    at: "2026-01-02T10:00:00Z"\n---\n'


def test_a_concept_that_is_a_link_is_refused_in_the_signed_form(parity):
    """The toolkit reads the link's target, a plain confirmation no reader here would see."""
    write(parity / ".lokf" / "curators" / ".gitkeep", "")
    write(parity / "docs" / "forged.md", FORGED)
    git = Git(parity)
    git("add", "-A")
    git("commit", "-q", "-m", "a file outside the bundle")
    os.symlink("../../../docs/forged.md", parity / ".lokf" / "knowledge" / "x" / "f.md")
    git("add", "-A")
    git("commit", "-q", "-m", "a concept that is a link onto it")
    result = bash(PROVENANCE, "HEAD~1", "HEAD", cwd=parity)
    assert result.rc != 0 and "symbolic link" in result.out, f"the signed form passed a link: {result.out}"


def test_a_concept_that_is_a_link_is_refused_in_the_unattended_form(parity):
    write(parity / "docs" / "plain.md", "plain\n")
    git = Git(parity)
    git("add", "-A")
    git("commit", "-q", "-m", "a file outside the bundle")
    os.symlink("../../../docs/plain.md", parity / ".lokf" / "knowledge" / "x" / "f.md")
    result = bash(PROVENANCE, "--unattended", cwd=parity)
    assert result.rc != 0 and "symbolic link" in result.out, f"the unattended form passed a link: {result.out}"


def test_the_doorway_link_is_no_link_the_gate_refuses(parity):
    os.symlink(".lokf/knowledge", parity / "knowledge_bundle")
    assert bash(PROVENANCE, "--unattended", cwd=parity).rc == 0
    write(parity / ".lokf" / "curators" / ".gitkeep", "")
    git = Git(parity)
    git("add", "-A")
    git("commit", "-q", "-m", "the doorway")
    result = bash(PROVENANCE, "HEAD~1", "HEAD", cwd=parity)
    assert result.rc == 0, f"the signed form refused the doorway: {result.out}"


def test_a_doorway_pointed_elsewhere_is_refused(parity):
    os.symlink("docs", parity / "knowledge_bundle")
    result = bash(PROVENANCE, "--unattended", cwd=parity)
    assert result.rc != 0 and "symbolic link" in result.out, f"the gate passed a doorway that leaves the bundle: {result.out}"


def test_a_sidecar_moved_behind_a_link_is_refused(parity):
    """A link at `.lokf` takes every path under it out of what the script lists."""
    write(parity / ".lokf" / "curators" / ".gitkeep", "")
    git = Git(parity)
    git("add", "-A")
    git("commit", "-q", "-m", "the curators folder")
    write(parity / "elsewhere" / "knowledge" / "x" / "f.md", FORGED)
    shutil.rmtree(parity / ".lokf")
    os.symlink("elsewhere", parity / ".lokf")
    git("add", "-A")
    git("commit", "-q", "-m", "the sidecar behind a link")
    result = bash(PROVENANCE, "HEAD~1", "HEAD", cwd=parity)
    assert result.rc != 0 and "symbolic link" in result.out, f"the signed form passed a moved sidecar: {result.out}"


def test_a_bundle_pointed_elsewhere_is_refused(parity):
    write(parity / ".lokf" / "curators" / ".gitkeep", "")
    git = Git(parity)
    git("add", "-A")
    git("commit", "-q", "-m", "the curators folder")
    write(parity / "docs" / "x" / "f.md", FORGED)
    shutil.rmtree(parity / ".lokf" / "knowledge")
    os.symlink("../docs", parity / ".lokf" / "knowledge")
    git("add", "-A")
    git("commit", "-q", "-m", "the bundle behind a link")
    result = bash(PROVENANCE, "HEAD~1", "HEAD", cwd=parity)
    assert result.rc != 0 and "symbolic link" in result.out, f"the signed form passed a moved bundle: {result.out}"


def test_a_range_that_deletes_the_keys_has_not_opted_out(parity):
    write(parity / ".lokf" / "curators" / "ada.pub", "ssh-ed25519 AAAA ada\n")
    git = Git(parity)
    git("add", "-A")
    git("commit", "-q", "-m", "a curator's key")
    shutil.rmtree(parity / ".lokf" / "curators")
    write(parity / ".lokf" / "knowledge" / "x" / "c.md", concept_with(HUMAN))
    git("add", "-A")
    git("commit", "-q", "-m", "no keys, and a confirmation")
    result = bash(PROVENANCE, "HEAD~1", "HEAD", cwd=parity)
    assert result.rc != 0, f"the signed form skipped a range that deletes the keys: {result.out}"


def keyed(repo):
    """The repository with one curator's key on file, committed, so the signed form checks and does not skip."""
    write(repo / ".lokf" / "curators" / "ada.pub", "ssh-ed25519 AAAA ada\n")
    git = Git(repo)
    git("add", "-A")
    git("commit", "-q", "-m", "a curator's key")
    return git


def test_a_commit_with_no_parent_is_read_like_any_other(parity):
    """A history merged in from elsewhere starts at a commit with no parent, which git lists nothing for unless asked."""
    git = keyed(parity)
    base = git("rev-parse", "HEAD")
    git("checkout", "-q", "--orphan", "elsewhere")
    git("rm", "-rqf", ".")
    write(parity / ".lokf" / "knowledge" / "x" / "d.md", concept_with(HUMAN).replace("/x/c", "/x/d"))
    git("add", "-A")
    git("commit", "-q", "-m", "a root commit that types a confirmation")
    git("checkout", "-q", "main")
    git("merge", "-q", "--allow-unrelated-histories", "--no-edit", "elsewhere")
    result = bash(PROVENANCE, base, "HEAD", cwd=parity)
    assert result.rc == 1 and "confirmation by human:ada" in result.out, f"the gate did not read a commit with no parent: {result.out}"


def test_a_shallow_clone_is_not_checked_as_if_it_were_whole(parity, tmp_path_factory):
    git = keyed(parity)
    write(parity / ".lokf" / "knowledge" / "x" / "c.md", concept_with(HUMAN))
    git("add", "-A")
    git("commit", "-q", "-m", "a confirmation")
    shallow = tmp_path_factory.mktemp("shallow") / "clone"
    assert run(["git", "clone", "-q", "--depth", "1", f"file://{parity}", str(shallow)]).rc == 0
    result = bash(PROVENANCE, "HEAD", "HEAD", cwd=shallow)
    assert result.rc == 2 and "shallow" in result.out, f"the gate checked a shallow clone: {result.out}"


def test_keys_behind_a_link_are_not_the_repository_s_own(parity):
    """A range that makes the keys folder a link onto a folder it adds would supply a key and vouch with it in one step."""
    git = keyed(parity)
    base = git("rev-parse", "HEAD")
    write(parity / "docs" / "keys" / "eve.pub", "ssh-ed25519 BBBB eve\n")
    shutil.rmtree(parity / ".lokf" / "curators")
    os.symlink("../docs/keys", parity / ".lokf" / "curators")
    write(parity / ".lokf" / "knowledge" / "x" / "c.md", concept_with(HUMAN.replace("human:ada", "human:eve")))
    git("add", "-A")
    git("commit", "-q", "-m", "keys behind a link, and a confirmation")
    result = bash(PROVENANCE, base, "HEAD", cwd=parity)
    assert result.rc == 1 and "is a symbolic link" in result.out, f"the gate took keys from behind a link: {result.out}"


@pytest.fixture
def subfolder(tmp_path):
    """A repository whose sidecar sits in svc/, with its own copy of the gate, a key on file and a committed draft."""
    side = tmp_path / "svc"
    write(side / ".lokf" / "knowledge" / "index.md", "---\nbase_iri: https://acme.example/knowledge/\n---\n")
    write(side / ".lokf" / "knowledge" / "x" / "c.md", concept_with("generated:\n  by: process:ktl-librarian\n  at: \"2026-01-01T00:00:00Z\""))
    write(side / ".lokf" / "curators" / "ada.pub", "ssh-ed25519 AAAA ada\n")
    write(side / ".lokf" / "scripts" / "knowledge-provenance.sh", read(PROVENANCE))
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "a sidecar in a subfolder")
    return tmp_path


def test_a_sidecar_in_a_subfolder_is_read_from_its_folder_or_by_its_own_copy(subfolder):
    """The gate once stopped, and before that skipped or passed, whatever changed in a sidecar below the top folder."""
    side = subfolder / "svc"
    write(side / ".lokf" / "knowledge" / "x" / "c.md", concept_with(HUMAN))
    result = bash(PROVENANCE, "--unattended", cwd=side)
    assert result.rc == 1 and "adds or changes a confirmation by human:ada" in result.out, f"the unattended form missed the event: {result.out}"
    own = side / ".lokf" / "scripts" / "knowledge-provenance.sh"
    result = bash(own, "--unattended", cwd=subfolder)
    assert result.rc == 1 and "adds or changes a confirmation by human:ada" in result.out, f"the sidecar's own copy, run from the top, missed it: {result.out}"
    git = Git(subfolder)
    git("commit", "-q", "-am", "an unsigned confirmation")
    for cwd, script in ((side, PROVENANCE), (subfolder, own)):
        result = bash(script, "HEAD~1", "HEAD", cwd=cwd)
        assert result.rc == 1 and "confirmation by human:ada but is unsigned" in result.out, f"the signed form passed an unsigned confirmation ({cwd}): {result.out}"
    git("rm", "-rq", "svc/.lokf/curators")
    git("commit", "-q", "-m", "keys gone")
    result = bash(PROVENANCE, "HEAD~1", "HEAD", cwd=side)
    assert result.rc == 0 and "OK - 0 concept(s) hold" in result.out, f"the keys were not read under the prefix: {result.out}"


def test_a_sidecar_the_gate_cannot_find_is_not_passed(tmp_path):
    """With no .lokf/ above the working directory and the gate not in one, it stops and says why."""
    write(tmp_path / "svc" / "README.md", "no sidecar here\n")
    git = Git(tmp_path)
    git.init()
    git("add", "-A")
    git("commit", "-q", "-m", "no sidecar")
    for form in (["--unattended"], ["HEAD", "HEAD"]):
        result = bash(PROVENANCE, *form, cwd=tmp_path / "svc")
        assert result.rc == 2 and "no bundle at" in result.out, f"the gate passed a repository with no bundle ({form}): {result.out}"


def test_the_gate_passes_nothing_when_a_tool_it_reads_with_is_missing(parity, tmp_path_factory):
    write(parity / ".lokf" / "knowledge" / "x" / "c.md", concept_with(HUMAN))
    tools = tmp_path_factory.mktemp("tools")
    for name in ("bash", "git", "awk", "sort", "cut", "sed", "grep", "mktemp"):
        os.symlink(shutil.which(name), tools / name)
    result = bash(PROVENANCE, "--unattended", cwd=parity, env={"PATH": str(tools)})
    assert result.rc == 2 and "comm is required" in result.out, f"the gate ran without comm: {result.out}"


def test_a_repository_that_never_had_keys_is_still_a_stated_skip(parity):
    write(parity / ".lokf" / "knowledge" / "x" / "c.md", concept_with(HUMAN))
    git = Git(parity)
    git("add", "-A")
    git("commit", "-q", "-m", "a confirmation, with no curators folder")
    result = bash(PROVENANCE, "HEAD~1", "HEAD", cwd=parity)
    assert result.rc == 0 and "skipped" in result.out, f"the signed form did not skip: {result.out}"


def test_a_repaired_spelling_is_reported_as_a_removal_in_the_unattended_form(parity):
    """A process may not repair it: only a person can say what the block held."""
    path = parity / ".lokf" / "knowledge" / "x" / "c.md"
    write(path, concept_with('"verified": [{ by: human:ada, at: "2026-01-02T10:00:00Z" }]'))
    git = Git(parity)
    git("add", "-A")
    git("commit", "-q", "-m", "an event in a quoted key")
    write(path, concept_with(""))
    result = bash(PROVENANCE, "--unattended", cwd=parity)
    assert result.rc != 0 and "could not read" in result.out, f"the gate let a process remove what it could not read: {result.out}"


REWRITES = [
    ('"verified": [{ by: human:ada, at: "2026-01-02T10:00:00Z" }]', '"verified": [{ by: human:mallory, at: "2026-01-02T10:00:00Z" }]'),
    ('verified:\n  - "by": human:ada', 'verified:\n  - "by": human:mallory'),
    ("x: &a human:ada\nverified:\n  - by: *a", "x: &a human:mallory\nverified:\n  - by: *a"),
]


def forge_inside_the_unreadable(repo, before, after):
    """Hold a spelling the reader cannot follow on the base, then change only what it says."""
    path = repo / ".lokf" / "knowledge" / "x" / "c.md"
    write(path, concept_with(before))
    git = Git(repo)
    git("add", "-A")
    git("commit", "-q", "-m", "a spelling already merged")
    write(path, concept_with(after))
    return git


@pytest.mark.parametrize(("before", "after"), REWRITES, ids=["quoted key", "quoted by", "alias"])
def test_an_edit_inside_unreadable_frontmatter_is_refused_unattended(parity, before, after):
    forge_inside_the_unreadable(parity, before, after)
    result = bash(PROVENANCE, "--unattended", cwd=parity)
    assert result.rc != 0 and "cannot read" in result.out, f"the gate passed an edit it could not read: {result.out}"


@pytest.mark.parametrize(("before", "after"), REWRITES, ids=["quoted key", "quoted by", "alias"])
def test_an_edit_inside_unreadable_frontmatter_is_refused_when_signed(parity, before, after):
    write(parity / ".lokf" / "curators" / "someone.pub", "")
    git = forge_inside_the_unreadable(parity, before, after)
    base = git("rev-parse", "HEAD").strip()
    git("add", "-A")
    git("commit", "-q", "-m", "an edit inside it")
    result = bash(PROVENANCE, base, "HEAD", cwd=parity)
    assert result.rc != 0 and "cannot read" in result.out, f"the signed form passed an edit it could not read: {result.out}"


@pytest.mark.parametrize(("before", "after"), REWRITES, ids=["quoted key", "quoted by", "alias"])
def test_an_edit_inside_unreadable_frontmatter_is_refused_by_the_registrar(parity, tmp_path, before, after):
    git = forge_inside_the_unreadable(parity, before, after)
    git("add", "-A")
    git("commit", "-q", "-m", "an edit inside it")
    result, output = registrar_step(parity, tmp_path)
    assert "frontmatter this gate cannot read" in result.out, f"the registrar job passed an edit it could not read: {result.out}"
    assert "verdict=ok" not in output, f"the registrar job backed an edit it could not read: {output}"


def test_a_body_edit_under_unreadable_frontmatter_passes(parity):
    """Only what a parser could read as frontmatter is carried, so a wording change costs nothing."""
    path = parity / ".lokf" / "knowledge" / "x" / "c.md"
    forge_inside_the_unreadable(parity, REWRITES[0][0], REWRITES[0][0])
    write(path, read(path) + "\nA further line of body.\n")
    result = bash(PROVENANCE, "--unattended", cwd=parity)
    assert result.rc == 0, f"the gate refused a body edit: {result.out}"


def test_a_tab_in_a_plain_event_is_still_read_as_a_space(parity):
    write(parity / ".lokf" / "knowledge" / "x" / "c.md", concept_with('verified:\n  - by:\thuman:mallory\n    at: "2026-01-02T10:00:00Z"'))
    result = bash(PROVENANCE, "--unattended", cwd=parity)
    assert "human:mallory" in result.out, f"the gate did not read a tabbed event: {result.out}"


def test_a_readable_event_beside_an_unreadable_one_is_still_read(parity):
    forge_inside_the_unreadable(parity, 'x: &a y\nverified:\n  - by: *a', 'x: &a y\nverified:\n  - by: *a\n  - by: human:mallory\n    at: "2026-01-02T10:00:00Z"')
    result = bash(PROVENANCE, "--unattended", cwd=parity)
    assert result.rc != 0 and "human:mallory" in result.out, f"the gate lost a plain event: {result.out}"


def program(text, start):
    """The awk program of human_events() in a file, a line each, with no indent and no comment line."""
    body = text[text.index(start) :]
    body = body[: body.index("\n", body.index("END {"))]
    return [line.strip() for line in body.split("\n") if line.strip() and not line.strip().startswith("#")]


def test_the_registrar_reads_events_as_the_forge_free_gate_does():
    """The two copies are one reader: a shape one of them refuses and the other reads would be a way past the gate."""
    gate = program(read(PROVENANCE), 'awk -v path="$1"')
    job = program(read(WORKFLOWS / "knowledge-registrar.yaml"), 'awk -v path="$1"')
    assert gate == job, "knowledge-registrar.yaml and knowledge-provenance.sh read events differently"


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


def registrar_step(repo, tmp_path):
    """Run the provenance job's own check on HEAD~1..HEAD, with a gh that finds no approval and no commits."""
    jobs = yaml.safe_load(read(WORKFLOWS / "knowledge-registrar.yaml"))["jobs"]
    step = next(s for s in jobs["provenance"]["steps"] if s.get("id") == "check")
    bin_dir = tmp_path / "stub-bin"
    write(bin_dir / "gh", "#!/bin/sh\nexit 0\n")
    (bin_dir / "gh").chmod(0o755)
    script = write(tmp_path / "step.sh", "set -euo pipefail\n" + step["run"])
    output = tmp_path / "github-output"
    git = Git(repo)
    env = {
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "BASE_SHA": git("rev-parse", "HEAD~1").strip(),
        "HEAD_SHA": git("rev-parse", "HEAD").strip(),
        "PR_NUMBER": "1",
        "ATTEST_ENV": "",
        "GITHUB_REPOSITORY": "acme/repo",
        "GITHUB_OUTPUT": str(output),
        "GITHUB_STEP_SUMMARY": str(tmp_path / "github-summary"),
    }
    result = bash(script, cwd=repo, env=env)
    return result, read(output) if output.exists() else ""


def test_the_registrar_job_refuses_a_concept_that_is_a_link(parity, tmp_path):
    write(parity / "docs" / "forged.md", FORGED)
    git = Git(parity)
    git("add", "-A")
    git("commit", "-q", "-m", "a file outside the bundle")
    os.symlink("../../../docs/forged.md", parity / ".lokf" / "knowledge" / "x" / "f.md")
    git("add", "-A")
    git("commit", "-q", "-m", "a concept that is a link onto it")
    result, _ = registrar_step(parity, tmp_path)
    assert result.rc != 0 and "symbolic links" in result.out, f"the registrar job passed a link: {result.out}"


def test_the_registrar_job_does_not_back_frontmatter_it_cannot_read(parity, tmp_path):
    write(parity / ".lokf" / "knowledge" / "x" / "c.md", concept_with('"verified": [{ by: human:ada, at: "2026-01-02T10:00:00Z" }]'))
    git = Git(parity)
    git("add", "-A")
    git("commit", "-q", "-m", "an event in a quoted key")
    result, output = registrar_step(parity, tmp_path)
    assert "frontmatter this gate cannot read" in result.out, f"the registrar job read past a quoted key: {result.out}"
    assert "verdict=ok" not in output, f"the registrar job backed what it could not read: {output}"


def test_the_registrar_job_passes_a_change_with_no_person_in_it(parity, tmp_path):
    write(parity / ".lokf" / "knowledge" / "x" / "c.md", concept_with('verified:\n  - by: process:ktl-librarian\n    at: "2026-01-02T10:00:00Z"'))
    git = Git(parity)
    git("add", "-A")
    git("commit", "-q", "-m", "a process's event")
    result, output = registrar_step(parity, tmp_path)
    assert result.rc == 0 and "verdict=ok" in output, f"the registrar job refused a process's event: {result.out}"
