"""Layout tests for the way ktl-sidecar installs a bundle (SKILL.md Step 2).

This was scripts/test-sidecar-layouts.sh. The bundle is `.lokf/knowledge`,
which the tools address, and `knowledge_bundle` beside it is the doorway link
people and Obsidian open. A git pathspec never traverses a symlink, so a
template that scopes a diff to the bundle names both paths. With the doorway
the second name matches nothing, harmlessly. It still covers a shared folder
someone rearranged by hand into a real `knowledge_bundle/` with
`.lokf/knowledge` linking onto it (see the sidecar's references/portability.md).
These tests pin that for the template files that do so, and for the
`just lokf-link` recipe:

1. the librarian wrapper:
   - refuses a run in which the agent edited anything itself, under either
     name of the bundle or outside it, and applies the one file the agent may
     write, .lokf/patch.yaml, with knowledge-apply.sh, which refuses a bad
     patch;
   - puts .git/config and .git/hooks/ back when the agent fails or the job is
     cancelled;
   - hands AGENT_API_KEY to the agent under AGENT_API_KEY_ENV's name only;
   - refuses a change that touches a person's record even when the pen let it
     through;
   - scores the retrieval test from an empty directory;
   - stops before the agent runs when the sidecar has no pen;
   - skips the agent for a quiet bundle only when KNOWLEDGE_SKIP_QUIET allows
     it;
   - passes the hand-off to its file through the pen, cleaned;
2. the librarian workflow:
   - its change detection sees a bundle edit in each shape, and its packaging
     step stages it;
   - its pull request says how the conventions script ended, and cleans the
     hand-off by Unicode category;
   - a scheduled run waits while an earlier pull request is open, and the step
     that reads those pull requests hands on what a person declined;
   - the install step installs the skill from the pinned tag only while that
     tag names the pinned commit, and stops when git does not ignore the
     folder it installs into;
3. the registrar workflow triggers on, and diffs, both names, and installs
   the sidecar from its lock. Its provenance step asks the person behind a
   confirmation that is added, changed or removed, and nobody when only a
   body changes;
4. `just lokf-link` creates the doorway, is a no-op when it is present,
   refuses a name taken by something else, and does nothing when
   `.lokf/knowledge` is itself a link;
5. the release workflow compares an unchanged bundle as unchanged and an
   edited one as changed in each shape, and its pack step gives the same bytes
   for the same bundle.

`just`, `jq`, `node`, `zip` and `unzip` are optional: a test that needs one
skips and says so.
"""

from __future__ import annotations

import os
import re
import shutil
import stat
import sys

import pytest
import yaml

from conftest import SCRIPTS, TEMPLATES, WORKFLOWS, has_line, have, matches, read, run, write

WRAPPER = SCRIPTS / "knowledge-librarian.sh"
LIBRARIAN_YAML = WORKFLOWS / "knowledge-librarian.yaml"
REGISTRAR_YAML = WORKFLOWS / "knowledge-registrar.yaml"
RELEASE_YAML = WORKFLOWS / "knowledge-release.yaml"
FEDERATION_YAML = WORKFLOWS / "knowledge-federation.yaml"
JUSTFILE = TEMPLATES / "justfile"
SHAPES = ["default", "no-doorway", "rearranged"]
# The wrapper must see no credential the test runner inherited.
INHERITED = (
    "AGENT_API_KEY",
    "AGENT_PROMPT_FLAG",
    "AGENT_API_KEY_ENV",
    "ANTHROPIC_API_KEY",
    "KNOWLEDGE_RETRIEVAL",
    "KNOWLEDGE_RETRIEVAL_OUT",
    "KNOWLEDGE_HANDOFF_OUT",
    "KNOWLEDGE_SKIP_QUIET",
    "KNOWLEDGE_DECLINED",
    "MEDDLE",
    "PLANT",
)

CREATE_OP = r"""ops:
  - op: create
    path: playbooks/b.md
    frontmatter: {type: Playbook, title: B, description: made through the pen.}
    body: "# B\n\nMade through the pen.\n"
"""
BAD_OP = """ops:
  - op: delete
    path: playbooks/missing.md
    log: gone
"""
HANDOFF_PATCH = CREATE_OP + 'handoff:\n  - "one line for the reviewer, with a `backtick`"\n'


def executable(path, text):
    write(path, text)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


@pytest.fixture(scope="module")
def agents(tmp_path_factory):
    """Stand-ins for AGENT_CLI, each writing what its case needs and nothing else."""
    d = tmp_path_factory.mktemp("agents")
    return {
        # Ignores the prompt and appends a line to the file EDIT_PATH names.
        "fake": executable(
            d / "fake-agent.sh",
            r"""#!/usr/bin/env bash
printf '\nedited by the fake agent\n' >> "$EDIT_PATH"
""",
        ),
        # Writes PATCH_TEXT to the patch file and nothing else.
        "patch": executable(
            d / "patch-agent.sh",
            r"""#!/usr/bin/env bash
printf '%s\n' "$PATCH_TEXT" > .lokf/patch.yaml
""",
        ),
        # Writes the patch, checks it, then applies it itself through the pen's
        # shell entry or its Python, as run 39289704507's agent did.
        "self-apply-sh": executable(
            d / "self-apply-sh-agent.sh",
            r"""#!/usr/bin/env bash
printf '%s\n' "$PATCH_TEXT" > .lokf/patch.yaml
bash .lokf/scripts/knowledge-apply.sh --dry-run >/dev/null 2>&1 || exit 9
bash .lokf/scripts/knowledge-apply.sh >/dev/null 2>&1 || true
""",
        ),
        "self-apply-py": executable(
            d / "self-apply-py-agent.sh",
            r"""#!/usr/bin/env bash
printf '%s\n' "$PATCH_TEXT" > .lokf/patch.yaml
uv run --quiet .lokf/scripts/knowledge-apply.py --root . >/dev/null 2>&1 || true
""",
        ),
        # Rewrites .git/config and .git/hooks/, then fails or gets the job cancelled.
        "poison": executable(
            d / "poison-agent.sh",
            r"""#!/usr/bin/env bash
git config core.hooksPath /nonexistent/hooks
printf '#!/bin/sh\necho hooked\n' > .git/hooks/pre-commit
case "${POISON_THEN:-fail}" in
  fail) exit 7 ;;
  term) kill -TERM "$PPID"; exit 0 ;;
esac
""",
        ),
        # Records how many arguments it got, and the first line of the first and of the last.
        "argv": executable(
            d / "argv-agent.sh",
            r"""#!/usr/bin/env bash
{ printf '%s\n' "$#"; printf '%s\n' "$1" | head -1; printf '%s\n' "${@: -1}" | head -1; } > "$ARGV_OUT"
""",
        ),
        # Records which of the credential names reached it.
        "env": executable(
            d / "env-agent.sh",
            r"""#!/usr/bin/env bash
env | grep -E '^(ANTHROPIC_API_KEY|AGENT_API_KEY|AGENT_API_KEY_ENV|PATH)=' | sed 's/^PATH=.*/PATH=set/' | sort > "$ENV_OUT"
""",
        ),
        # Writes the patch when it finds itself in the repository, and answers the one question otherwise.
        "retrieval": executable(
            d / "retrieval-agent.sh",
            r"""#!/usr/bin/env bash
if [ -d .lokf ]; then
  printf '%s\n' "$PATCH_TEXT" > .lokf/patch.yaml
else
  [ -z "${MEDDLE:-}" ] || printf 'meddled\n' >> "$MEDDLE"
  [ -z "${PLANT:-}" ] || printf 'planted in the retrieval call\n' > "$PLANT"
  echo "Q1: a.md"
fi
""",
        ),
        # Writes the patch, plants a hand-off, and leaves a link at the retrieval score's path.
        "plant": executable(
            d / "plant-agent.sh",
            r"""#!/usr/bin/env bash
printf '%s\n' "$PATCH_TEXT" > .lokf/patch.yaml
printf 'planted by the agent\n' > "$KNOWLEDGE_HANDOFF_OUT"
ln -sf "$PWD/README.md" "$KNOWLEDGE_RETRIEVAL_OUT"
""",
        ),
    }


def git(host, *args):
    result = run(["git", "-C", host, *args])
    if result.rc != 0:
        raise RuntimeError(f"git {' '.join(str(a) for a in args)} failed in {host}: {result.out}")
    return result.out


def make_host(host, shape):
    """A minimal host repository: the wrapper and justfile in place, one concept in the bundle, and the two names set up the way the shape says."""
    host.mkdir(parents=True, exist_ok=True)
    run(["git", "init", "-q", "-b", "main", "."], cwd=host)
    git(host, "config", "user.email", "layout-test@example.invalid")
    git(host, "config", "user.name", "layout test")
    scripts = host / ".lokf" / "scripts"
    scripts.mkdir(parents=True)
    for name in [
        "knowledge-librarian.sh",
        "knowledge-apply.sh",
        "knowledge-apply.py",
        "knowledge-provenance.sh",
        "knowledge-report.sh",
    ]:
        shutil.copy(SCRIPTS / name, scripts / name)
        (scripts / name).chmod(0o755)
    shutil.copy(JUSTFILE, host / ".lokf" / "justfile")
    write(host / "skills" / "ktl-librarian" / "SKILL.md", "# stub skill\n")
    if shape == "default":
        (host / ".lokf" / "knowledge").mkdir()
        os.symlink(".lokf/knowledge", host / "knowledge_bundle")
    elif shape == "no-doorway":
        (host / ".lokf" / "knowledge").mkdir()
    elif shape == "rearranged":
        (host / "knowledge_bundle").mkdir()
        os.symlink("../knowledge_bundle", host / ".lokf" / "knowledge")
    else:
        raise ValueError(f"unknown shape {shape}")
    write(host / ".lokf" / "knowledge" / "index.md", "---\nbase_iri: https://host.example/knowledge/\n---\n\n# Host\n")
    write(host / ".lokf" / "knowledge" / "a.md", "---\ntype: Service\ntitle: A\n---\n\n# A\n")
    write(host / "README.md", "# host\n")
    git(host, "add", "-A", ".")
    git(host, "commit", "-q", "-m", f"init ({shape})")
    return host


def wrapper(host, env):
    """The wrapper's exit status, run in a subshell as the workflow runs it, so a signal's status reads as 128 plus the signal."""
    result = run(
        ["bash", "-c", 'cd "$1" && bash .lokf/scripts/knowledge-librarian.sh >/dev/null 2>&1', "_", host],
        env=env,
        unset=INHERITED,
    )
    return result.rc


def reset(host):
    git(host, "checkout", "-q", "--", ".")
    git(host, "clean", "-qfd")


@pytest.fixture
def host(tmp_path):
    return make_host(tmp_path / "host", "default")


# 1. The wrapper's boundary: one patch file in, and only the pen writes the bundle.


@pytest.mark.parametrize(
    ("shape", "edit"),
    [
        (s, e)
        for s in ["default", "rearranged", "no-doorway"]
        for e in [".lokf/knowledge/a.md", "README.md"] + ([] if s == "no-doorway" else ["knowledge_bundle/a.md"])
    ],
)
def test_an_agent_that_edits_a_file_itself_is_refused(tmp_path, agents, shape, edit):
    h = make_host(tmp_path / shape, shape)
    status = wrapper(h, {"AGENT_CLI": agents["fake"], "EDIT_PATH": edit})
    assert status == 3, f"{shape}: an agent that edits {edit} itself was not refused (exit {status})"


@pytest.mark.parametrize("shape", ["default", "rearranged", "no-doorway"])
def test_a_patch_file_is_applied_by_the_pen_and_a_refused_one_writes_nothing(tmp_path, agents, shape):
    h = make_host(tmp_path / shape, shape)
    status = wrapper(h, {"AGENT_CLI": agents["patch"], "PATCH_TEXT": CREATE_OP})
    wrote = (h / ".lokf" / "knowledge" / "playbooks" / "b.md").is_file()
    patch_left = (h / ".lokf" / "patch.yaml").exists()
    assert (status, wrote, patch_left) == (0, True, False), (
        f"{shape}: a valid patch file was not applied as expected (exit {status}, wrote {wrote}, patch left {patch_left})"
    )
    reset(h)
    status = wrapper(h, {"AGENT_CLI": agents["patch"], "PATCH_TEXT": BAD_OP})
    wrote = (h / ".lokf" / "knowledge" / "playbooks" / "b.md").is_file()
    assert (status, wrote) == (4, False), (
        f"{shape}: a refused patch did not fail the run cleanly (exit {status}, wrote {wrote})"
    )



@pytest.mark.parametrize("agent", ["self-apply-sh", "self-apply-py"])
def test_an_agent_that_applies_its_own_patch_leaves_it_for_the_wrapper(host, agents, agent):
    status = wrapper(host, {"AGENT_CLI": agents[agent], "PATCH_TEXT": CREATE_OP, "KNOWLEDGE_PEN_DRY_RUN_ONLY": "1"})
    wrote = (host / ".lokf" / "knowledge" / "playbooks" / "b.md").is_file()
    patch_left = (host / ".lokf" / "patch.yaml").exists()
    assert (status, wrote, patch_left) == (0, True, False), (
        f"{agent}: the patch was not left for the wrapper to apply (exit {status}, wrote {wrote}, patch left {patch_left})"
    )

@pytest.mark.parametrize(("way", "want"), [("fail", 7), ("term", 143)])
def test_the_wrapper_restores_git_config_and_hooks_on_every_way_out(host, agents, way, want):
    """An agent that rewrites both and then exits non-zero, or gets the job cancelled, must leave neither behind, and the wrapper's status is the agent's or the signal's."""
    status = wrapper(host, {"AGENT_CLI": agents["poison"], "POISON_THEN": way})
    assert status == want, f"poison/{way}: the wrapper exited {status}, expected {want}"
    assert run(["git", "-C", host, "config", "core.hooksPath"]).rc != 0, (
        f"poison/{way}: core.hooksPath survived the agent's exit"
    )
    assert not (host / ".git" / "hooks" / "pre-commit").exists(), (
        f"poison/{way}: the dropped hook survived the agent's exit"
    )


KEY_CASES = [
    ("named", "sk-test", "ANTHROPIC_API_KEY", 0, "ANTHROPIC_API_KEY=sk-test PATH=set"),
    ("none", "", "", 0, "PATH=set"),
    ("no-name", "sk-test", "", 2, "agent did not run"),
    ("no-key", "", "ANTHROPIC_API_KEY", 2, "agent did not run"),
    ("path", "sk-test", "PATH", 2, "agent did not run"),
    ("github", "sk-test", "GITHUB_TOKEN", 2, "agent did not run"),
    ("lower", "sk-test", "anthropic_api_key", 2, "agent did not run"),
]


@pytest.mark.parametrize(("label", "key", "name", "want", "expect"), KEY_CASES, ids=[c[0] for c in KEY_CASES])
def test_the_key_reaches_the_agent_under_the_given_name_only(host, agents, tmp_path, label, key, name, want, expect):
    """Not as AGENT_API_KEY, and never when the name is one the wrapper refuses: it exits 2 before the agent runs."""
    out = tmp_path / "env.out"
    status = wrapper(
        host, {"AGENT_CLI": agents["env"], "ENV_OUT": out, "AGENT_API_KEY": key, "AGENT_API_KEY_ENV": name}
    )
    got = " ".join(read(out).split("\n")).strip() if out.is_file() else "agent did not run"
    assert (status, got) == (want, expect), (
        f"key/{label}: exit {status} (want {want}), agent saw: {got} (want: {expect})"
    )


PROMPT = "You are the repository knowledge librarian. Follow this skill file verbatim:"
PROMPT_CASES = [
    ("default", "", 0, ["2", "-p", PROMPT]),
    ("long flag", "--prompt", 0, ["2", "--prompt", PROMPT]),
    ("last argument", "arg", 0, ["1", PROMPT, PROMPT]),
    ("a word", "prompt", 2, None),
    ("a flag with a value", "-p=x", 2, None),
    ("a space", "-p x", 2, None),
]


@pytest.mark.parametrize(("label", "flag", "want", "head"), PROMPT_CASES, ids=[c[0] for c in PROMPT_CASES])
def test_the_prompt_goes_where_the_prompt_flag_says(host, agents, tmp_path, label, flag, want, head):
    """After -p by default, after another flag, or as the bare last argument with "arg"; anything else is refused before the agent runs."""
    out = tmp_path / "argv.out"
    status = wrapper(host, {"AGENT_CLI": agents["argv"], "ARGV_OUT": out, "AGENT_PROMPT_FLAG": flag})
    assert status == want, f"prompt/{label}: exit {status} (want {want})"
    if head is None:
        assert not out.exists(), f"prompt/{label}: the agent ran with a refused flag"
        return
    got = read(out).strip().split("\n")
    assert got == head, f"prompt/{label}: the agent got {got} (want {head})"


def test_a_persons_event_the_pen_let_through_fails_the_run(host, agents):
    """What the pen refuses before it writes is checked on the result as well, so a tampered pen in a shared workspace still fails the run."""
    executable(
        host / ".lokf" / "scripts" / "knowledge-apply.sh",
        r"""#!/usr/bin/env bash
printf -- '---\ntype: Service\ntitle: A\nverified: [{ by: human:nobody, at: "2026-01-01T00:00:00Z" }]\n---\n\n# A\n' > .lokf/knowledge/a.md
rm -f .lokf/patch.yaml
""",
    )
    git(host, "commit", "-q", "-am", "a pen that lets a person's event through")
    status = wrapper(host, {"AGENT_CLI": agents["patch"], "PATCH_TEXT": CREATE_OP})
    assert status == 3, f"unattended: a person's event reached the bundle unrefused (exit {status})"


def retrieval_host(host):
    write(
        host / ".lokf" / "questions.md",
        "# Questions readers asked\n\nKept by knowledge-apply.sh.\n\n- 2026-01-01 Miss a.md: `where is a?`\n",
    )
    git(host, "add", "-A")
    git(host, "commit", "-q", "-m", "a question on file")
    return host


def test_the_retrieval_test_is_scored_by_program_when_switched_on(host, agents, tmp_path):
    retrieval_host(host)
    score = tmp_path / "retrieval.txt"
    status = wrapper(
        host,
        {
            "AGENT_CLI": agents["retrieval"],
            "PATCH_TEXT": CREATE_OP,
            "KNOWLEDGE_RETRIEVAL": "true",
            "KNOWLEDGE_RETRIEVAL_OUT": score,
        },
    )
    assert (
        status == 0
        and score.is_file()
        and read(score).rstrip("\n") == "Retrieval from the index: 1 of 1 reader questions reach their concept"
        and (host / ".lokf" / "knowledge" / "playbooks" / "b.md").is_file()
    ), f"retrieval: exit {status}, score file: {read(score) if score.is_file() else 'none'}"


def test_the_retrieval_test_is_off_unless_switched_on(host, agents, tmp_path):
    retrieval_host(host)
    score = tmp_path / "retrieval.txt"
    status = wrapper(
        host, {"AGENT_CLI": agents["retrieval"], "PATCH_TEXT": CREATE_OP, "KNOWLEDGE_RETRIEVAL_OUT": score}
    )
    assert status == 0 and not score.exists(), f"retrieval: scored with the switch off (exit {status})"


def test_a_retrieval_call_that_changes_the_checkout_is_refused(host, agents, tmp_path):
    retrieval_host(host)
    score = tmp_path / "retrieval.txt"
    status = wrapper(
        host,
        {
            "AGENT_CLI": agents["retrieval"],
            "PATCH_TEXT": CREATE_OP,
            "KNOWLEDGE_RETRIEVAL": "true",
            "KNOWLEDGE_RETRIEVAL_OUT": score,
            "MEDDLE": host / "README.md",
        },
    )
    assert status == 3 and not score.exists(), (
        f"retrieval: a call that changed the checkout was not refused (exit {status})"
    )


def test_a_sidecar_with_no_pen_stops_before_the_agent_runs(host, agents, tmp_path):
    (host / ".lokf" / "scripts" / "knowledge-apply.py").unlink()
    out = tmp_path / "env.out"
    status = wrapper(host, {"AGENT_CLI": agents["env"], "ENV_OUT": out})
    assert status == 2 and not out.exists(), f"no pen: the wrapper ran the agent or did not stop (exit {status})"


def test_a_quiet_bundle_skips_the_agent_only_when_the_caller_allows_it(host, agents, tmp_path, checks):
    """With KNOWLEDGE_SKIP_QUIET "true" the wrapper asks knowledge-report.sh and, on a quiet bundle, exits 0 without calling the agent. A source that moved makes work, except once a person closed the pull request that changed its concept, until it moves again."""
    out = tmp_path / "env.out"
    declined = tmp_path / "declined.txt"

    def case(label, skip, expected, record=""):
        out.unlink(missing_ok=True)
        status = wrapper(
            host,
            {"AGENT_CLI": agents["env"], "ENV_OUT": out, "KNOWLEDGE_SKIP_QUIET": skip, "KNOWLEDGE_DECLINED": record},
        )
        got = "ran" if out.exists() else "skipped"
        checks.ok(
            status == 0 and got == expected, f"quiet/{label}: the agent {got}, exit {status} (want {expected}, exit 0)"
        )

    write(
        host / ".lokf" / "knowledge" / "a.md",
        '---\ntype: Service\ntitle: A\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n---\n\n# A\n',
    )
    git(host, "commit", "-q", "-am", "a stamped concept")
    case("nothing waits, skip allowed", "true", "skipped")
    case("nothing waits, skip not allowed", "", "ran")
    write(
        host / ".lokf" / "feedback.md", "# Reader feedback\n\n## 2026-01-02\n\n- **Miss** - a reader asked. - docent\n"
    )
    case("reader feedback waits", "true", "ran")
    (host / ".lokf" / "feedback.md").unlink()
    write(
        host / ".lokf" / "knowledge" / "a.md",
        '---\ntype: Service\ntitle: A\nresource: README.md\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-01-01T00:00:00Z"\n---\n\n# A\n',
    )
    git(host, "commit", "-q", "-am", "the concept names its source")
    write(host / "README.md", read(host / "README.md") + "more\n")
    git(host, "commit", "-q", "-am", "the source moves")
    case("a source moved", "true", "ran")
    write(declined, f"declined 7 2026-01-03 {git(host, 'rev-parse', 'HEAD')}\ntouched a.md\n")
    case("a source moved, and a person closed the pull request that changed its concept", "true", "skipped", declined)
    write(host / "README.md", read(host / "README.md") + "again\n")
    git(host, "commit", "-q", "-am", "the source moves again")
    case("the source moved again after that pull request", "true", "ran", declined)


def bundle_holds(host, text):
    return any(text in read(p) for p in (host / ".lokf" / "knowledge").rglob("*.md"))


def test_the_handoff_reaches_its_file_through_the_pen_over_what_the_agent_planted(host, agents, tmp_path):
    """What the agent left at the hand-off's path, or at the retrieval score's, is gone first: a file it wrote there, and a link that would send the next write into the checkout."""
    handoff, score = tmp_path / "handoff.txt", tmp_path / "retrieval.txt"
    status = wrapper(
        host,
        {
            "AGENT_CLI": agents["plant"],
            "PATCH_TEXT": HANDOFF_PATCH,
            "KNOWLEDGE_HANDOFF_OUT": handoff,
            "KNOWLEDGE_RETRIEVAL_OUT": score,
        },
    )
    assert (
        status == 0
        and handoff.is_file()
        and read(handoff).rstrip("\n") == "one line for the reviewer, with a 'backtick'"
        and (host / ".lokf" / "knowledge" / "playbooks" / "b.md").is_file()
        and not bundle_holds(host, "one line for the reviewer")
    ), f"hand-off: exit {status}, file holds: {read(handoff) if handoff.is_file() else 'nothing'}"
    assert (
        not score.is_symlink()
        and not (score.exists() and score.stat().st_size > 0)
        and read(host / "README.md") == "# host\n"
    ), "hand-off: the retrieval path is still a link, or holds the agent's text, or the checkout's README changed"


def test_the_handoff_is_written_again_after_the_retrieval_call(host, agents, tmp_path):
    """The retrieval call comes after the pen has written the hand-off, and its prompt carries readers' words, so what it leaves at the path is gone too."""
    retrieval_host(host)
    handoff, score = tmp_path / "handoff.txt", tmp_path / "retrieval.txt"
    status = wrapper(
        host,
        {
            "AGENT_CLI": agents["retrieval"],
            "PATCH_TEXT": HANDOFF_PATCH,
            "KNOWLEDGE_RETRIEVAL": "true",
            "PLANT": handoff,
            "KNOWLEDGE_HANDOFF_OUT": handoff,
            "KNOWLEDGE_RETRIEVAL_OUT": score,
        },
    )
    assert (
        status == 0
        and read(handoff).rstrip("\n") == "one line for the reviewer, with a 'backtick'"
        and "1 of 1" in read(score)
    ), (
        f"hand-off: exit {status} after a retrieval call that wrote the hand-off's path, file holds: {read(handoff) if handoff.is_file() else 'nothing'}"
    )


def test_a_patch_with_no_handoff_leaves_none_whatever_the_retrieval_call_wrote(host, agents, tmp_path):
    retrieval_host(host)
    handoff, score = tmp_path / "handoff.txt", tmp_path / "retrieval.txt"
    status = wrapper(
        host,
        {
            "AGENT_CLI": agents["retrieval"],
            "PATCH_TEXT": CREATE_OP,
            "KNOWLEDGE_RETRIEVAL": "true",
            "PLANT": handoff,
            "KNOWLEDGE_HANDOFF_OUT": handoff,
            "KNOWLEDGE_RETRIEVAL_OUT": score,
        },
    )
    assert status == 0 and not (handoff.exists() and handoff.stat().st_size > 0), (
        f"hand-off: exit {status}, and a hand-off the retrieval call wrote survived: {read(handoff) if handoff.is_file() else ''}"
    )


# 2. The librarian workflow's change detection and packaging.


def section(text, start, end=None):
    """sed -n '/start/,/end/p': the lines from the first match of start through the first later match of end, or to the end."""
    out, on = [], False
    for line in text.split("\n"):
        if not on and re.search(start, line):
            on = True
        if on:
            out.append(line)
            if end is not None and len(out) > 1 and re.search(end, line):
                break
    return "\n".join(out)


def step_body(yaml_path, name, stop):
    """The `run: |` block of the named step, its ten-space indent removed, up to the line the stop pattern names."""
    out, on, body = [], False, False
    for line in read(yaml_path).split("\n"):
        if line == f"      - name: {name}":
            on = True
        if on and not body and line == "        run: |":
            body = True
            continue
        if body and re.match(stop, line):
            break
        if body:
            out.append(line[10:] if line.startswith(" " * 10) else line)
    return "\n".join(out) + "\n"


LIBRARIAN_LINES = [
    (
        "template detects changes with: git status --porcelain -- .lokf/knowledge knowledge_bundle",
        ["git status --porcelain -- .lokf/knowledge knowledge_bundle"],
    ),
    (
        "template stages both names and guards the second one",
        ["git add -A -- .lokf/knowledge", "[ -e knowledge_bundle ] && git add -A -- knowledge_bundle || true"],
    ),
    (
        "template carries reader feedback and the ledger its handled entries move into",
        [
            "[ -e .lokf/feedback.md ] && git add -A -- .lokf/feedback.md || true",
            "[ -e .lokf/questions.md ] && git add -A -- .lokf/questions.md || true",
        ],
    ),
    (
        "template lets a scheduled run skip a quiet week, outside a month's first seven days",
        [
            "KNOWLEDGE_SKIP_QUIET: ${{ github.event_name == 'schedule' }}",
            'if [ "$(date -u +%d)" -le 7 ]; then export KNOWLEDGE_SKIP_QUIET=false; fi',
        ],
    ),
    (
        "template runs the conventions script in refresh and reports its outcome on the pull request",
        [
            "conventions_outcome: ${{ steps.conventions.outcome }}",
            "CONVENTIONS_OUTCOME: ${{ needs.refresh.outputs.conventions_outcome }}",
            "${check(CONVENTIONS_OUTCOME)}",
        ],
    ),
    (
        "template hands what a person declined to the agent step as a file, on a scheduled run only",
        [
            "KNOWLEDGE_DECLINED: ${{ runner.temp }}/declined.txt",
            "if: vars.KNOWLEDGE_LIBRARIAN_ENABLED == 'true' && github.event_name == 'schedule' && needs.earlier.outputs.record != ''",
            'run: printf \'%s\\n\' "$RECORD" > "$RUNNER_TEMP/declined.txt"',
        ],
    ),
    (
        "template names an earlier pull request in the new one by its number, and only when it is a number",
        [
            "OPEN_PR: ${{ needs.earlier.outputs.open }}",
            "DECLINED_PR: ${{ needs.earlier.outputs.declined }}",
            "if (/^[0-9]+$/.test(OPEN_PR || '')) {",
            "if (/^[0-9]+$/.test(DECLINED_PR || '')) {",
            "...earlier,",
        ],
    ),
    (
        "template lists the patch's paths with: git -c core.quotePath=false apply --numstat",
        ["git -c core.quotePath=false apply --numstat"],
    ),
    (
        "template refuses a patch path outside the bundle, the feedback file and the ledger",
        [r"grep -Ev '^(\.lokf/knowledge/|knowledge_bundle/|\.lokf/feedback\.md$|\.lokf/questions\.md$)'"],
    ),
]


@pytest.mark.parametrize(("what", "needles"), LIBRARIAN_LINES, ids=[w for w, _ in LIBRARIAN_LINES])
def test_the_librarian_template_still_holds(what, needles):
    text = read(LIBRARIAN_YAML)
    missing = [n for n in needles if n not in text]
    assert not missing, f"knowledge-librarian.yaml no longer contains: {missing} ({what})"


def test_the_hand_off_travels_from_the_pen_through_the_artifact_to_the_pull_request():
    text = read(LIBRARIAN_YAML)
    upload = section(text, r"name: Upload the bundle patch", r"if-no-files-found")
    assert (
        "KNOWLEDGE_HANDOFF_OUT: ${{ runner.temp }}/handoff.txt" in text
        and "${{ runner.temp }}/handoff.txt" in upload
        and "HANDOFF_FILE: ${{ runner.temp }}/handoff.txt" in text
        and "'```text', ...handoff, '```'" in text
    ), "knowledge-librarian.yaml lost the hand-off's path from the pen to the pull request"


def test_the_refresh_job_runs_the_conventions_script():
    """The registrar's gate does not run on the pull request this workflow opens, so refresh runs the script and the pull request says how it ended."""
    refresh_to_publish = section(read(LIBRARIAN_YAML), r"^  refresh:", r"^  publish:")
    assert "run: bash scripts/knowledge-conventions.sh knowledge" in refresh_to_publish, (
        "knowledge-librarian.yaml no longer runs the conventions script in refresh"
    )


def test_a_scheduled_refresh_waits_while_an_earlier_pull_request_is_open():
    text = read(LIBRARIAN_YAML)
    refresh_to_steps = section(text, r"^  refresh:", r"^    steps:")
    publish_to_steps = section(text, r"^  publish:", r"^    steps:")
    assert (
        has_line(refresh_to_steps, "    needs: earlier")
        and has_line(refresh_to_steps, "    if: github.event_name != 'schedule' || needs.earlier.outputs.open == ''")
        and has_line(publish_to_steps, "    needs: [earlier, refresh]")
    ), "knowledge-librarian.yaml no longer holds a scheduled refresh back while an earlier pull request is open"


def test_the_earlier_job_reads_pull_requests_under_a_read_only_token_and_runs_no_agent():
    earlier = section(read(LIBRARIAN_YAML), r"^  earlier:", r"^  refresh:")
    assert (
        matches(earlier, r"^      pull-requests: read")
        and not matches(earlier, r"^      [a-z-]+: write")
        and not re.search(r"actions/checkout|AGENT_", earlier)
    ), "knowledge-librarian.yaml's earlier job holds more than a token that reads pull requests"


CLEAN_LINE = r""".map((l) => l.replace(/[\p{Cc}\p{Cf}\p{Default_Ignorable_Code_Point}\p{Zl}\p{Zp}]/gu, '').replace(/`/g, "'").trim().slice(0, 300))"""


def clean_line():
    return next(line.strip() for line in read(LIBRARIAN_YAML).split("\n") if ".map((l) => l.replace(" in line)


def test_publish_cleans_each_hand_off_line_by_unicode_category():
    assert clean_line() == CLEAN_LINE, (
        f"knowledge-librarian.yaml no longer cleans the hand-off as expected: {clean_line()}"
    )


def js(code_point):
    """A JavaScript escape for a code point, built from its number so this file holds no character a reader cannot see."""
    return ("\\" + "u%04x" % code_point) if code_point <= 0xFFFF else ("\\" + "u{%X}" % code_point)


@pytest.mark.skipif(not have("node"), reason="node not installed locally - CI runs the hand-off's cleaning")
def test_the_cleaning_removes_a_bidirectional_mark_a_soft_hyphen_a_tag_character_a_variation_selector_and_a_line_separator():
    sample = (
        "a"
        + js(0x061C)
        + " line"
        + js(0x00AD)
        + " with"
        + js(0xE0041)
        + " more"
        + js(0xFFF9)
        + " than"
        + js(0xFE0F)
        + js(0xE0100)
        + js(0x3164)
        + js(0x180E)
        + " a"
        + js(0x200B)
        + " `list`"
        + js(0x2028)
    )
    script = (
        'const clean = eval("(l) => [l]" + process.env.CLEAN + "[0]"); process.stdout.write(clean("' + sample + '"));'
    )
    result = run(["node", "-e", script], env={"CLEAN": clean_line()})
    assert result.out == "a line with more than a 'list'", (
        f"template's cleaning left something a reader cannot see: {result.out!r}"
    )


@pytest.fixture
def earlier_step(tmp_path):
    """The step that reads the workflow's earlier pull requests, extracted from the template so the test breaks when its lines change, with `gh` stubbed to answer each API call from a file through the real jq."""
    if not have("jq"):
        pytest.skip("jq is not installed - the step that reads the earlier pull requests runs its filters through it")
    step = write(
        tmp_path / "earlier-step.sh",
        step_body(LIBRARIAN_YAML, "Read the pull requests this workflow opened", r"^  [a-z]"),
    )
    assert "KTL_EARLIER_END" in read(step) and run(["bash", "-n", step]).rc == 0, (
        "could not extract the step that reads the earlier pull requests from knowledge-librarian.yaml"
    )
    api = tmp_path / "api"
    api.mkdir()
    executable(
        tmp_path / "stub" / "gh",
        r"""#!/usr/bin/env bash
# gh api <url> [--paginate] --jq <filter>: the canned reply for that url, through jq.
url="$2"; filter=""
while [ $# -gt 0 ]; do [ "$1" = --jq ] && filter="$2"; shift; done
case "$url" in
  *"/pulls?"*"page=1") file="$STUB_API/pulls.json" ;;
  *"/pulls?"*)         file="$STUB_API/none.json" ;;
  *"/pulls/"*"/files") n="${url%/files}"; file="$STUB_API/files-${n##*/}.json" ;;
  *) echo "unexpected call: $url" >&2; exit 1 ;;
esac
[ -f "$file" ] || file="$STUB_API/none.json"
jq -r "$filter" "$file"
""",
    )
    write(api / "none.json", "[]\n")
    return step, api, tmp_path


def pull(number, state, merged_at, closed_at, base, branch, repository):
    return (
        f'{{"number":{number},"state":"{state}","merged_at":{merged_at},"closed_at":{closed_at},"base":{{"sha":"{base}"}},'
        f'"head":{{"ref":"{branch}","repo":{repository}}},"title":"a title nobody reads","body":"a body nobody reads"}}'
    )


def sha(n):
    return "%040d" % n


OURS = '{"full_name":"o/r"}'


def earlier_run(step, api, work):
    out = work / "earlier.out"
    write(out, "")
    result = run(
        ["bash", step],
        cwd=work,
        env={
            "PATH": f"{work / 'stub'}:{os.environ['PATH']}",
            "GH_TOKEN": "x",
            "GITHUB_REPOSITORY": "o/r",
            "GITHUB_OUTPUT": out,
            "STUB_API": api,
        },
    )
    return result.rc, read(out), result.out


def test_the_earlier_step_hands_on_what_a_person_declined(earlier_step):
    step, api, work = earlier_step
    write(
        api / "pulls.json",
        "["
        + ",".join(
            [
                pull(30, "open", "null", "null", sha(30), "knowledge-librarian/2026-10-05-1", '{"full_name":"fork/r"}'),
                pull(29, "closed", "null", '"2026-09-29T05:10:00Z"', sha(29), "knowledge-librarian/2026-09-28-9", OURS),
                pull(
                    28,
                    "closed",
                    '"2026-09-22T08:00:00Z"',
                    '"2026-09-22T08:00:00Z"',
                    sha(28),
                    "knowledge-librarian/2026-09-21-8",
                    OURS,
                ),
                pull(27, "closed", "null", '"2026-09-20T08:00:00Z"', sha(27), "feature/knowledge-librarian/x", OURS),
                pull(
                    26, "closed", "null", '"2026-09-15T08:00:00Z"', sha(26), "knowledge-librarian/2026-09-14-7", "null"
                ),
                pull(25, "closed", "null", '"2026-09-08T08:00:00Z"', sha(25), "knowledge-librarian/2026-09-07-6", OURS),
            ]
        )
        + "]\n",
    )
    write(
        api / "files-29.json",
        r"""[{"status":"modified","filename":".lokf/knowledge/x/two.md"},
 {"status":"added","filename":".lokf/knowledge/x/new.md"},
 {"status":"removed","filename":"knowledge_bundle/x/old.md"},
 {"status":"modified","filename":".lokf/knowledge/index.md"},
 {"status":"modified","filename":".lokf/knowledge/x/index.md"},
 {"status":"modified","filename":".lokf/knowledge/log.md"},
 {"status":"modified","filename":".lokf/knowledge/x/Bad Name.md"},
 {"status":"modified","filename":".lokf/knowledge/x/../../../README.md"},
 {"status":"modified","filename":"README.md"},
 {"status":"modified","filename":".lokf/questions.md"},
 {"status":"modified","filename":".lokf/feedback.md","patch":"@@ -3,7 +3,5 @@\n \n ## 2026-01-06\n \n-- **Miss** - Q: \"a reader wrote these declined words\" - docent\n - **Miss** - Q: \"second\" - docent\n-## 2026-01-01\n"}]
""",
    )
    write(api / "files-25.json", '[{"status":"modified","filename":".lokf/knowledge/x/five.md"}]\n')
    status, outputs, log = earlier_run(step, api, work)
    handled = run(
        ["git", "hash-object", "--stdin"], stdin='- **Miss** - Q: "a reader wrote these declined words" - docent\n'
    ).out
    want = "\n".join(
        [
            f"declined 29 2026-09-29 {sha(29)}",
            "touched x/two.md",
            "added x/new.md",
            "touched x/old.md",
            f"handled {handled}",
            f"declined 25 2026-09-08 {sha(25)}",
            "touched x/five.md",
        ]
    )
    record = section(outputs, r"^record<<KTL_EARLIER_END$", r"^KTL_EARLIER_END$").split("\n")[1:-1]
    assert status == 0 and has_line(outputs, "open=") and has_line(outputs, "declined=29"), (
        f"earlier: exit {status}, outputs: {outputs}, log: {log}"
    )
    assert "\n".join(record) == want, f"earlier: the record is not as expected: {record}"
    assert not re.search(r"declined words|nobody reads", outputs + log), (
        "earlier: a reader's words or a pull request's text reached the step's outputs or its log"
    )


def test_the_earlier_step_names_an_open_pull_request_and_a_merged_one_declines_nothing(earlier_step):
    step, api, work = earlier_step
    write(
        api / "pulls.json",
        "["
        + ",".join(
            [
                pull(31, "open", "null", "null", sha(31), "knowledge-librarian/2026-10-05-2", OURS),
                pull(
                    28,
                    "closed",
                    '"2026-09-22T08:00:00Z"',
                    '"2026-09-22T08:00:00Z"',
                    sha(28),
                    "knowledge-librarian/2026-09-21-8",
                    OURS,
                ),
            ]
        )
        + "]\n",
    )
    status, outputs, log = earlier_run(step, api, work)
    assert (
        status == 0
        and has_line(outputs, "open=31")
        and has_line(outputs, "declined=")
        and "Pull request #31 from this workflow is still open" in log
    ), f"earlier: exit {status} with an open pull request, outputs: {outputs}"


def test_the_earlier_step_with_no_pull_requests_has_nothing_open_and_nothing_declined(earlier_step):
    step, api, work = earlier_step
    write(api / "pulls.json", "[]\n")
    status, outputs, _ = earlier_run(step, api, work)
    assert status == 0 and has_line(outputs, "open=") and has_line(outputs, "declined="), (
        f"earlier: exit {status} with no pull requests, outputs: {outputs}"
    )


@pytest.fixture
def install_step(tmp_path):
    """The install step, extracted from the template, and a stand-in for the skills repository with the reviewed skill tagged."""
    step = write(
        tmp_path / "install-step.sh",
        step_body(LIBRARIAN_YAML, "Install the pinned ktl-librarian skill", r"^      [#-]"),
    )
    assert "TRUST_LADDER_SKILLS_SHA" in read(step) and run(["bash", "-n", step]).rc == 0, (
        "could not extract the install step from knowledge-librarian.yaml, or it no longer reads TRUST_LADDER_SKILLS_SHA"
    )
    skills_repo = tmp_path / "skills-repo"
    write(skills_repo / "skills" / "ktl-librarian" / "SKILL.md", "# the skill as it was reviewed\n")
    run(["git", "init", "-q", "-b", "main", "."], cwd=skills_repo)
    git(skills_repo, "config", "user.email", "layout-test@example.invalid")
    git(skills_repo, "config", "user.name", "layout test")
    git(skills_repo, "add", "-A")
    git(skills_repo, "commit", "-q", "-m", "the reviewed skill")
    git(skills_repo, "-c", "tag.gpgSign=false", "tag", "v9.9.9")
    return step, skills_repo, git(skills_repo, "rev-parse", "HEAD"), tmp_path


def install_run(step, skills_repo, pinned, into, ignored=True):
    """Run the step as Actions does, in a checkout whose root .gitignore leaves .agents/ out unless ignored is False."""
    into.mkdir(parents=True, exist_ok=True)
    run(["git", "init", "-q", "-b", "main", "."], cwd=into)
    if ignored:
        write(into / ".gitignore", ".agents/\n")
    return run(
        ["bash", step],
        cwd=into,
        env={
            "TRUST_LADDER_SKILLS_REPO": f"file://{skills_repo}",
            "TRUST_LADDER_SKILLS_REF": "v9.9.9",
            "TRUST_LADDER_SKILLS_SHA": pinned,
        },
    )


def test_the_skill_is_installed_from_the_pinned_tag_while_it_names_the_pinned_commit(install_step):
    step, skills_repo, pinned, work = install_step
    result = install_run(step, skills_repo, pinned, work / "install-ok")
    installed = work / "install-ok" / ".agents" / "skills" / "ktl-librarian" / "SKILL.md"
    assert result.rc == 0 and installed.is_file() and "as it was reviewed" in read(installed), (
        f"install: exit {result.rc} with the tag and the commit in agreement: {result.out}"
    )


def test_an_install_git_would_see_stops_before_any_agent_runs(install_step):
    step, skills_repo, pinned, work = install_step
    result = install_run(step, skills_repo, pinned, work / "install-seen", ignored=False)
    assert result.rc == 1 and "git does not ignore .agents/" in result.out, (
        f"install: exit {result.rc} where git does not ignore .agents/: {result.out}"
    )


def test_a_tag_that_names_another_commit_installs_nothing(install_step):
    step, skills_repo, pinned, work = install_step
    write(skills_repo / "skills" / "ktl-librarian" / "SKILL.md", "# other instructions\n")
    git(skills_repo, "commit", "-q", "-am", "the tag is moved to this")
    git(skills_repo, "-c", "tag.gpgSign=false", "tag", "-f", "v9.9.9")
    result = install_run(step, skills_repo, pinned, work / "install-moved")
    assert (
        result.rc == 1
        and not (work / "install-moved" / ".agents" / "skills" / "ktl-librarian").exists()
        and "nothing was installed" in result.out
    ), f"install: exit {result.rc} after the tag moved: {result.out}"


@pytest.mark.parametrize("shape", SHAPES)
def test_change_detection_sees_the_bundle_edit_and_packaging_stages_it(tmp_path, shape):
    h = make_host(tmp_path / shape, shape)
    write(h / ".lokf" / "knowledge" / "a.md", read(h / ".lokf" / "knowledge" / "a.md") + "\nchanged\n")
    write(h / "README.md", read(h / "README.md") + "\nchanged\n")
    seen = run(
        ["bash", "-c", "git status --porcelain -- .lokf/knowledge knowledge_bundle | cut -c4-"], cwd=h
    ).out.split()
    assert any("a.md" in s for s in seen) and not any("README" in s for s in seen), (
        f"{shape}: change detection saw {seen}"
    )
    staged = run(
        [
            "bash",
            "-c",
            "set -e; git add -A -- .lokf/knowledge && { [ -e knowledge_bundle ] && git add -A -- knowledge_bundle || true; } && git diff --cached --name-only",
        ],
        cwd=h,
    ).out.split()
    assert any("a.md" in s for s in staged) and not any("README" in s for s in staged), (
        f"{shape}: packaging staged {staged}"
    )


ALLOWED = r"^(\.lokf/knowledge/|knowledge_bundle/|\.lokf/feedback\.md$|\.lokf/questions\.md$)"


def test_publish_runs_the_gate_and_the_report_on_its_own_checkout():
    publish_to_end = section(read(LIBRARIAN_YAML), r"^  publish:")
    for line in [
        "bash .lokf/scripts/knowledge-provenance.sh --unattended",
        "bash .lokf/scripts/knowledge-report.sh health",
        "bash .lokf/scripts/knowledge-report.sh changes",
    ]:
        assert line in publish_to_end, f"knowledge-librarian.yaml's publish job no longer runs: {line}"


@pytest.mark.parametrize(
    ("where", "path"),
    [
        ("inside", ".lokf/knowledge/café.md"),
        ("inside", ".lokf/questions.md"),
        ("outside", "notes-café.md"),
        ("outside", ".lokf/scripts/knowledge-apply.sh"),
    ],
)
def test_the_publish_path_check(host, tmp_path, where, path):
    """A concept named with a byte above 0x7f is inside the bundle, and a file beside it is not."""
    write(host / path, "x\n")
    patch = tmp_path / "p.patch"
    run(["bash", "-c", f'git add -A && git diff --cached --binary > "{patch}" && git reset -q --hard'], cwd=host)
    bad = run(
        [
            "bash",
            "-c",
            f"git -c core.quotePath=false apply --numstat \"{patch}\" | cut -f3- | grep -Ev '{ALLOWED}' || true",
        ],
        cwd=host,
    ).out
    assert (where == "outside") == bool(bad), f"publish path check got {path} wrong (refused: {bad or 'nothing'})"


# 3. The registrar workflow.


@pytest.mark.parametrize("yaml_path", [REGISTRAR_YAML, LIBRARIAN_YAML, RELEASE_YAML, FEDERATION_YAML], ids=lambda p: p.name)
def test_each_template_installs_the_sidecar_from_its_lock(yaml_path):
    text = read(yaml_path)
    assert has_line(text, "        run: uv sync --locked") and not matches(text, r"^ *run: uv sync *$"), (
        f"{yaml_path.name} installs the sidecar without --locked, so it takes whatever resolves on the day"
    )


def test_the_registrar_triggers_on_and_diffs_both_names():
    text = read(REGISTRAR_YAML)
    assert matches(text, r'^\s*-\s*"\.lokf/\*\*"') and matches(text, r'^\s*-\s*"knowledge_bundle/\*\*"'), (
        "knowledge-registrar.yaml paths: must list both .lokf/** and knowledge_bundle/**"
    )
    both = text.count("-- .lokf/knowledge knowledge_bundle")
    single = len(re.findall(r"-- \.lokf/knowledge *$|-- \.lokf/knowledge \|", text, re.M))
    assert both >= 3 and single == 0, (
        f"knowledge-registrar.yaml: {both} pathspecs name both paths, {single} name only .lokf/knowledge"
    )


@pytest.fixture
def provenance_step(tmp_path):
    """The provenance step, extracted from the template, with `gh` stubbed to answer who approved and which commits GitHub verified for whom."""
    step = write(
        tmp_path / "provenance-step.sh",
        step_body(REGISTRAR_YAML, "Every new human confirmation must come from that person", r"^      [#-]"),
    )
    assert "removed_actors" in read(step) and run(["bash", "-n", step]).rc == 0, (
        "could not extract the provenance step from knowledge-registrar.yaml, or it no longer holds removed_actors"
    )
    executable(
        tmp_path / "stub" / "gh",
        r"""#!/usr/bin/env bash
case "$*" in
  *reviews*) cat "$STUB_APPROVERS" ;;
  *commits*) cat "$STUB_COMMITS" ;;
esac
""",
    )
    return step, tmp_path


CHANGES = {
    "strike": lambda k: write(
        k / "confirmed.md", "---\ntype: Service\nid: https://e.invalid/k/x/confirmed\n---\n\nText.\n"
    ),
    "remove": lambda k: (k / "confirmed.md").unlink(),
    "correct": lambda k: write(
        k / "authored.md",
        '---\ntype: Service\nid: https://e.invalid/k/x/authored\ngenerated:\n  by: human:bob\n  at: "2026-09-20T00:00:00Z"\n---\n\nCorrected.\n',
    ),
    "restamp": lambda k: write(
        k / "authored.md",
        '---\ntype: Service\nid: https://e.invalid/k/x/authored\ngenerated:\n  by: process:ktl-librarian\n  at: "2026-09-20T00:00:00Z"\n---\n\nRewritten.\n',
    ),
    "bodyonly": lambda k: write(k / "confirmed.md", read(k / "confirmed.md") + "More.\n"),
    "confirm": lambda k: write(
        k / "plain.md",
        '---\ntype: Service\nid: https://e.invalid/k/x/plain\nverified: [{ by: human:bob, at: "2026-09-20T00:00:00Z" }]\n---\n\nPlain.\n',
    ),
}

PROVENANCE_CASES = [
    (
        "struck-out-unbacked",
        "strike",
        "",
        "-",
        1,
        "removes a confirmation by human:ada but GitHub reports it verified=false",
    ),
    ("struck-out-approved", "strike", "ada", "-", 0, "ok: human:ada approved this pull request"),
    ("struck-out-signed", "strike", "", "ada", 0, "ok: human:ada signed each commit"),
    ("deleted-unbacked", "remove", "", "-", 1, "confirmation by human:ada"),
    ("corrected-by-another", "correct", "bob", "-", 0, "ok: human:bob approved this pull request"),
    ("restamped-by-process", "restamp", "", "-", 1, "confirmation by human:ada"),
    ("body-only", "bodyonly", "", "-", 0, "No human confirmation is added, changed or removed"),
    ("confirmed-approved", "confirm", "bob", "-", 0, "ok: human:bob approved this pull request"),
]


@pytest.mark.parametrize(
    ("label", "change", "approver", "signer", "want", "line"), PROVENANCE_CASES, ids=[c[0] for c in PROVENANCE_CASES]
)
def test_the_provenance_step(provenance_step, label, change, approver, signer, want, line):
    """A person's record is never removed without that person, so a confirmation struck out, or gone with its concept, needs the same backing as one that is added. A person's generated record may be replaced by another person's, the curator's Correct, and by nothing else."""
    step, work = provenance_step
    repo = work / f"provenance-{label}"
    k = repo / ".lokf" / "knowledge" / "x"
    write(
        k / "confirmed.md",
        '---\ntype: Service\nid: https://e.invalid/k/x/confirmed\nverified:\n  - by: human:ada\n    at: "2026-09-17T00:00:00Z"\n---\n\nText.\n',
    )
    write(
        k / "authored.md",
        '---\ntype: Service\nid: https://e.invalid/k/x/authored\ngenerated:\n  by: human:ada\n  at: "2026-09-17T00:00:00Z"\n---\n\nWritten.\n',
    )
    write(k / "plain.md", "---\ntype: Service\nid: https://e.invalid/k/x/plain\n---\n\nPlain.\n")
    run(["git", "init", "-q", "-b", "main", "."], cwd=repo)
    git(repo, "config", "user.email", "layout-test@example.invalid")
    git(repo, "config", "user.name", "layout test")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD")
    CHANGES[change](k)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "change")
    head = git(repo, "rev-parse", "HEAD")
    write(work / "approvers", f"{approver}\n" if approver else "")
    commits = "".join(
        f"{s}\tfalse\t-\n" if signer == "-" else f"{s}\ttrue\t{signer}\n"
        for s in git(repo, "rev-list", f"{base}..{head}").split()
    )
    write(work / "commits", commits)
    result = run(
        ["bash", step],
        cwd=repo,
        env={
            "PATH": f"{work / 'stub'}:{os.environ['PATH']}",
            "GH_TOKEN": "x",
            "PR_NUMBER": "1",
            "BASE_SHA": base,
            "HEAD_SHA": head,
            "ATTEST_ENV": "",
            "GITHUB_REPOSITORY": "o/r",
            "GITHUB_OUTPUT": work / "gh-output",
            "GITHUB_STEP_SUMMARY": work / "gh-summary",
            "STUB_APPROVERS": work / "approvers",
            "STUB_COMMITS": work / "commits",
        },
    )
    assert result.rc == want and line in result.out, (
        f"provenance/{label}: exit {result.rc} (want {want}), and no line matching '{line}' in: {result.out}"
    )


# 4. just lokf-link.

needs_just = pytest.mark.skipif(not have("just"), reason="just is not installed - the lokf-link recipe tests need it")


@needs_just
def test_lokf_link_creates_the_doorway_and_is_a_no_op_when_it_is_present(tmp_path):
    h = make_host(tmp_path / "host", "no-doorway")
    assert (
        run(["just", "--quiet", "lokf-link"], cwd=h / ".lokf").rc == 0
        and os.readlink(h / "knowledge_bundle") == ".lokf/knowledge"
    ), "did not create the doorway"
    assert "already present" in run(["just", "--quiet", "lokf-link"], cwd=h / ".lokf").out, (
        "a second run was not a no-op"
    )


@needs_just
def test_lokf_link_refuses_a_name_taken_by_a_real_folder(tmp_path):
    h = make_host(tmp_path / "host", "no-doorway")
    (h / "knowledge_bundle").mkdir()
    assert (
        run(["just", "--quiet", "lokf-link"], cwd=h / ".lokf").rc != 0
        and (h / "knowledge_bundle").is_dir()
        and not (h / "knowledge_bundle").is_symlink()
    ), "a real knowledge_bundle folder was not left alone"


@needs_just
def test_lokf_link_refuses_a_link_that_points_elsewhere(tmp_path):
    h = make_host(tmp_path / "host", "no-doorway")
    os.symlink("../nowhere", h / "knowledge_bundle")
    assert (
        run(["just", "--quiet", "lokf-link"], cwd=h / ".lokf").rc != 0
        and os.readlink(h / "knowledge_bundle") == "../nowhere"
    ), "a foreign knowledge_bundle link was not left alone"


@needs_just
def test_lokf_link_does_nothing_when_the_bundle_is_itself_a_link(tmp_path):
    h = make_host(tmp_path / "host", "rearranged")
    assert "nothing to do" in run(["just", "--quiet", "lokf-link"], cwd=h / ".lokf").out, (
        "a rearranged host was not left alone"
    )


# 5. The release workflow's compare and pack steps, run as the template has them.


@pytest.fixture(scope="module")
def pack_scripts(tmp_path_factory):
    """The template's own lines: the bundle_tree function, the mtime line and the lines from stage= to zip, each in a script that runs them."""
    text = read(RELEASE_YAML)
    bundle_tree_fn = section(text, r"^ *bundle_tree\(\) \{$", r"^          \}$")
    mtime_line = next((line.strip() for line in text.split("\n") if re.match(r"^\s*mtime=", line)), "")
    zip_lines = "\n".join(line.strip() for line in section(text, r"^ *stage=", r" zip -q -X -y -@ ").split("\n"))
    assert bundle_tree_fn and mtime_line and " zip -q -X -y -@ " in zip_lines, (
        "knowledge-release.yaml no longer has a bundle_tree function, an mtime= line and the stage= to 'zip -q -X -y -@' lines"
    )
    if not (have("zip") and have("unzip")):
        pytest.skip("zip and unzip are not installed - the pack tests need them")
    d = tmp_path_factory.mktemp("pack")
    tree = write(
        d / "bundle-tree.sh", f'#!/usr/bin/env bash\nset -euo pipefail\n{bundle_tree_fn}\ncd "$1" && bundle_tree "$2"\n'
    )
    pack = write(
        d / "pack.sh",
        f"#!/usr/bin/env bash\nset -euo pipefail\n{bundle_tree_fn}\n"
        '[ -z "${PACK_UMASK:-}" ] || umask "$PACK_UMASK"\n'
        'cd "$1" && git checkout -q "$2" && export RUNNER_TEMP="$3" TZ="${4:-UTC}" && mkdir -p "$RUNNER_TEMP/release" \\\n'
        '  && read -r _ BUNDLE_PATH < <(bundle_tree "$2") && asset=knowledge.zip \\\n'
        '  && src="$(cd "$BUNDLE_PATH" && pwd -P)" && eval "$MTIME_LINE" && eval "$ZIP_LINES"\n',
    )
    return tree, pack, {"MTIME_LINE": mtime_line, "ZIP_LINES": zip_lines}


@pytest.mark.parametrize("shape", SHAPES)
def test_the_release_compares_and_packs_a_bundle_the_same_in_each_shape(tmp_path, pack_scripts, shape, checks):
    tree, pack, env = pack_scripts
    h = make_host(tmp_path / shape, shape)
    os.symlink("./a.md", h / ".lokf" / "knowledge" / "alias.md")
    git(h, "add", "-A")
    git(h, "commit", "-q", "-m", "link")
    git(h, "-c", "tag.gpgSign=false", "tag", "v1")
    run(["sleep", "1"])
    write(h / "README.md", read(h / "README.md") + "more\n")
    git(h, "commit", "-qam", "readme")
    git(h, "-c", "tag.gpgSign=false", "tag", "v2")
    run(["sleep", "1"])
    write(h / ".lokf" / "knowledge" / "a.md", read(h / ".lokf" / "knowledge" / "a.md") + "more\n")
    git(h, "commit", "-qam", "concept")
    git(h, "-c", "tag.gpgSign=false", "tag", "v3")
    t1, t2, t3 = (run(["bash", tree, h, tag]).out for tag in ["v1", "v2", "v3"])
    checks.ok(t1 and t1 == t2, f"{shape}: a README-only release compared as changed", f"{t1} vs {t2}")
    checks.ok(t3.split()[0] != t2.split()[0], f"{shape}: a concept edit compared as unchanged")
    for tag in ["v1", "v2", "v3"]:
        result = run(["bash", pack, h, tag, tmp_path / f"rt-{tag}"], env=env)
        checks.ok(result.rc == 0, f"{shape}: the pack step failed at {tag}", result.out)
    result = run(["bash", pack, h, "v1", tmp_path / "rt-again", "Asia/Tokyo"], env={**env, "PACK_UMASK": "077"})
    checks.ok(result.rc == 0, f"{shape}: the pack step failed under another time zone and umask", result.out)
    zipfile = tmp_path / "rt-v1" / "release" / "knowledge.zip"
    listing = run(["unzip", "-Z1", zipfile]).out.split("\n")
    checks.ok(
        listing == ["knowledge/a.md", "knowledge/alias.md", "knowledge/index.md"],
        f"{shape}: unexpected zip listing",
        str(listing),
    )
    checks.ok(
        run(["unzip", "-Z", zipfile, "knowledge/alias.md"]).out.startswith("l")
        and run(["unzip", "-p", zipfile, "knowledge/alias.md"]).out == "./a.md",
        f"{shape}: a link inside the bundle was followed or lost its target",
    )
    checks.ok(
        zipfile.read_bytes() == (tmp_path / "rt-again" / "release" / "knowledge.zip").read_bytes(),
        f"{shape}: two packs of one tag differ",
    )
    checks.ok(
        zipfile.read_bytes() == (tmp_path / "rt-v2" / "release" / "knowledge.zip").read_bytes(),
        f"{shape}: an unchanged bundle packed differently at a later tag",
    )
    checks.ok(
        zipfile.read_bytes() != (tmp_path / "rt-v3" / "release" / "knowledge.zip").read_bytes(),
        f"{shape}: a changed bundle packed to the same bytes",
    )


def test_the_federation_site_leaves_out_a_workspace_that_holds_internal_metadata(tmp_path):
    """The step's own lines: a workspace whose lock says internal stays off the Pages artifact, and a public one is copied under workspace/."""
    body = step_body(FEDERATION_YAML, "Assemble the Pages artifact", r"^      [#-]")
    script = write(tmp_path / "assemble.sh", "#!/usr/bin/env bash\n" + body)
    for sensitivity, kept in (("public", True), ("internal", False)):
        host = tmp_path / sensitivity
        write(host / "snapshot" / "workspace.lock.yaml", f"knowledge_federate_lock: '4'\nsensitivity: {sensitivity}\nmembers:\n- slug: a\n  sensitivity: {sensitivity}\n")
        write(host / "snapshot" / "bundles" / "a" / ".lokf" / "knowledge" / "index.md", "# A\n")
        (host / "website" / "dist").mkdir(parents=True)
        r = run(["bash", script], cwd=host, env={"GITHUB_ENV": host / "github.env"})
        assert r.rc == 0, r.out
        assert (host / "website" / "dist" / "workspace" / "bundles" / "a" / ".lokf" / "knowledge" / "index.md").is_file() == kept, (sensitivity, r.out)
        assert read(host / "github.env") == "dist=website/dist\n"


def test_the_federation_notes_replace_the_workspace_changes_an_earlier_run_added(tmp_path):
    """The step's own lines, run twice against a stand-in gh: the notes keep what came before the marker, and the second run replaces the first one's changes."""
    body = step_body(FEDERATION_YAML, "Add the workspace's changes to the release notes", r"^(      [#-]|        [a-z])")
    script = write(tmp_path / "notes.sh", "#!/usr/bin/env bash\n" + body)
    gh = write(tmp_path / "bin" / "gh", "#!/bin/sh\n"
               '[ "$1 $2" = "release view" ] && { cat "$NOTES"; exit 0; }\n'
               '[ "$1 $2" = "release edit" ] && { cp "$5" "$NOTES"; exit 0; }\n'
               "exit 1\n")
    gh.chmod(0o755)
    notes = write(tmp_path / "notes.md", "## What changed\n\n- A fix.\n")
    env = {"PATH": f"{tmp_path / 'bin'}:{os.environ['PATH']}", "NOTES": notes, "TAG": "v0.3.0"}
    work = tmp_path / "release"
    work.mkdir()
    r = run(["bash", script], cwd=work, env=env)
    assert r.rc == 0 and "No comparison was made" in r.out and read(notes) == "## What changed\n\n- A fix.\n", r.out
    for changes in ("- **b** moved from v1 to v2.\n", "- **b** moved from v1 to v3.\n"):
        write(work / "workspace-changes.md", "## The workspace\n\n" + changes)
        r = run(["bash", script], cwd=work, env=env)
        assert r.rc == 0, r.out
    assert read(notes) == ("## What changed\n\n- A fix.\n\n<!-- knowledge-federation: workspace changes -->\n\n"
                           "## The workspace\n\n- **b** moved from v1 to v3.\n"), read(notes)


def test_the_federation_check_holds_a_member_as_the_release_build_would():
    """The check passes the newest released workspace and the release page, so it holds a member and checks that workspace's attestation as the release build does."""
    body = step_body(FEDERATION_YAML, "Fetch and verify every member's zip, and gate as the next release would", r"^  [a-z]")
    assert '--release-base "$GITHUB_SERVER_URL/$GITHUB_REPOSITORY/releases/tag"' in body and '${PREVIOUS:+--previous "$PREVIOUS"}' in body, body


def test_the_release_packs_the_domain_schema_the_justfile_names(tmp_path):
    """The step's own lines, run against six justfiles. They name a schema beside the bundle, none, one in a linkml-sidecar project, one outside the repository, a missing file, and a schema that imports a local file that is not there."""
    body = step_body(RELEASE_YAML, "Pack the domain schema", r"^      [#-]")
    assert 'asset="schema-${TAG//\\//-}-$NAME.yaml"' in body, "knowledge-release.yaml no longer packs the schema as schema-<tag>-<name>.yaml"
    script = write(tmp_path / "schema.sh", "#!/usr/bin/env bash\n" + body)
    write(tmp_path / "outside.yaml", "id: https://x.example/outside\n")
    linkml = (
        "id: https://x.example/acme\nname: acme\nimports:\n  - linkml:types\n"
        "  # LinkML resolves the path relative to this file.\n  - ../../../../.lokf/lokf\n"
        "classes:\n  Gadget:\n    is_a: Concept\n"
    )

    def attempt(line, files=()):
        host = tmp_path / f"host{len(list(tmp_path.iterdir()))}"
        write(host / ".lokf" / "justfile", f'set shell := ["bash", "-cu"]\n{line}\n')
        write(host / ".lokf" / "domain.yaml", "id: https://x.example/schema\nname: x\nimports:\n  - linkml:types\n  - lokf\n")
        write(host / ".lokf" / "lokf.yaml", "id: https://w3id.org/lokf\n")
        write(host / ".lokf" / ".venv" / "bin" / "python", f'#!/bin/sh\nexec "{sys.executable}" "$@"\n').chmod(0o755)
        for rel, text in files:
            write(host / rel, text)
        (host / "temp" / "release").mkdir(parents=True)
        return run(["bash", script], cwd=host, env={"RUNNER_TEMP": host / "temp", "TAG": "v1.2.3", "NAME": "host"}), host / "temp" / "release"

    r, out = attempt('schema := "domain.yaml"')
    assert r.rc == 0 and read(out / "schema-v1.2.3-host.yaml") == "id: https://x.example/schema\nname: x\nimports:\n  - linkml:types\n  - lokf\n", r.out
    assert run(["sha256sum", "-c", "schema-v1.2.3-host.yaml.sha256"], cwd=out).rc == 0
    r, out = attempt('schema := ""')
    assert r.rc == 0 and "none is attached" in r.out and not list(out.iterdir()), r.out
    r, out = attempt('schema := "../.linkml/src/acme/schema/acme.yaml"', [(".linkml/src/acme/schema/acme.yaml", linkml)])
    assert r.rc == 0 and read(out / "schema-v1.2.3-host.yaml") == linkml.replace("  - ../../../../.lokf/lokf\n", "  - lokf\n"), r.out
    r, out = attempt('schema := "../../outside.yaml"')
    assert r.rc == 1 and "outside this repository" in r.out and not list(out.iterdir()), r.out
    r, out = attempt('schema := "missing.yaml"')
    assert r.rc == 1 and "not a file" in r.out, r.out
    r, out = attempt('schema := "acme.yaml"', [(".lokf/acme.yaml", "id: https://x.example/acme\nimports:\n  - lokf\n  - parts\n")])
    assert r.rc == 1 and "imports parts.yaml, which is not a LinkML schema file" in r.out and not list(out.iterdir()), r.out


def pack_schema(tmp_path, files, core="id: https://w3id.org/lokf\nclasses:\n  Concept: {}\n"):
    """Run the template's "Pack the domain schema" lines in a host holding these .lokf/ files and a justfile naming acme.yaml."""
    script = write(tmp_path / "schema.sh", "#!/usr/bin/env bash\n" + step_body(RELEASE_YAML, "Pack the domain schema", r"^      [#-]"))
    host = tmp_path / "host"
    write(host / ".lokf" / "justfile", 'schema := "acme.yaml"\n')
    write(host / ".lokf" / "lokf.yaml", core)
    write(host / ".lokf" / ".venv" / "bin" / "python", f'#!/bin/sh\nexec "{sys.executable}" "$@"\n').chmod(0o755)
    for rel, text in files.items():
        write(host / ".lokf" / rel, text)
    (host / "temp" / "release").mkdir(parents=True)
    r = run(["bash", script], cwd=host, env={"RUNNER_TEMP": host / "temp", "TAG": "v1", "NAME": "host"})
    asset = host / "temp" / "release" / "schema-v1-host.yaml"
    return r, (yaml.safe_load(read(asset)) if asset.is_file() else None)


def test_the_release_merges_the_adapted_copies_a_composite_imports(tmp_path):
    """A host composite that imports two `lokf adapt` copies is released as one file: each copy merged with what it imports in turn, every IRI written out as LinkML derives it, and LOKF core still imported by name."""
    r, doc = pack_schema(tmp_path, {
        "acme.yaml": "id: https://x.example/acme\nname: acme\nprefixes:\n  linkml: https://w3id.org/linkml/\nimports: [linkml:types, lokf, slsa, 'gha']\n",
        "slsa.yaml": (
            "id: https://x.example/slsa-lokf\nname: slsa\ndefault_prefix: slsa\nprefixes:\n  slsa: https://x.example/slsa/\n"
            "imports:\n- linkml:types\n- lokf\n# A copy may import a module of its own.\n- parts/more  # beside it\n"
            "classes:\n  SlsaParty:\n    is_a: Concept\n    attributes:\n      party_name:\n      party_type:\n        slot_uri: schema:roleName\n"
            "enums:\n  SlsaLevel:\n    permissible_values:\n      L1: {}\n"
        ),
        "parts/more.yaml": "id: https://x.example/more\nname: more\nimports:\n  - ../lokf\nslots:\n  build level:\n    range: string\n",
        "gha.yaml": (
            "id: https://x.example/gha-lokf\nname: gha\ndefault_prefix: gha\nprefixes:\n  gha: https://x.example/gha/\n"
            "imports:\n  - lokf\nclasses:\n  GhaWorkflow:\n    is_a: Concept\n    class_uri: gha:Workflow\n"
        ),
    })
    assert r.rc == 0 and "Merged slsa.yaml" in r.out and "Merged parts/more.yaml" in r.out and "Merged gha.yaml" in r.out, r.out
    assert doc["imports"] == ["linkml:types", "lokf"], doc["imports"]
    assert doc["prefixes"] == {"linkml": "https://w3id.org/linkml/", "slsa": "https://x.example/slsa/", "gha": "https://x.example/gha/"}, doc["prefixes"]
    party = doc["classes"]["SlsaParty"]
    assert party["class_uri"] == "slsa:SlsaParty" and party["attributes"]["party_name"] == {"slot_uri": "slsa:party_name"}, party
    assert party["attributes"]["party_type"]["slot_uri"] == "schema:roleName", "an IRI the copy names was replaced"
    assert doc["classes"]["GhaWorkflow"]["class_uri"] == "gha:Workflow" and doc["enums"]["SlsaLevel"]["enum_uri"] == "slsa:SlsaLevel", doc
    assert doc["slots"]["build level"]["slot_uri"] == "https://x.example/more/build_level", "a schema with no default_prefix lost its id-based IRI"


def test_the_release_merge_keeps_what_linkml_reads_from_each_file(tmp_path):
    """LinkML takes an element's IRI, and the settings of its structured patterns, from the file that defines it. The merged copy keeps both: for a default prefix written as an IRI, for two classes a YAML alias shares, and for a copy's settings and CURIE maps."""
    r, doc = pack_schema(tmp_path, {
        "acme.yaml": "id: https://x.example/acme\nname: acme\nimports:\n  - lokf\n  - uri\n  - al\n",
        "uri.yaml": (
            "id: https://x.example/u-schema\ndefault_prefix: https://x.example/u/\nsettings:\n  code: '[A-Z]{3}'\n"
            "default_curi_maps:\n  - semweb_context\nclasses:\n  UriThing:\n    is_a: Concept\n"
        ),
        "al.yaml": "id: https://x.example/al\ndefault_prefix: al\nprefixes:\n  al: https://x.example/al/\nclasses:\n  AlOne: &shared\n    is_a: Concept\n  AlTwo: *shared\n",
    })
    assert r.rc == 0, r.out
    assert doc["classes"]["UriThing"]["class_uri"] == "https://x.example/u/UriThing", "a default prefix written as an IRI took a colon"
    assert doc["classes"]["AlOne"]["class_uri"] == "al:AlOne" and doc["classes"]["AlTwo"]["class_uri"] == "al:AlTwo", "two classes a YAML alias shares took one IRI"
    assert doc["settings"] == {"code": "[A-Z]{3}"} and doc["default_curi_maps"] == ["semweb_context"], doc


@pytest.mark.parametrize("files, why", [
    ({"acme.yaml": "id: https://x.example/acme\nimports:\n  - a\n  - b\n", "a.yaml": "id: https://x.example/a\nclasses:\n  Thing:\n    is_a: Concept\n",
      "b.yaml": "id: https://x.example/b\nclasses:\n  Thing:\n    is_a: Concept\n    class_uri: b:Thing\n"}, "b.yaml defines the class Thing, which an earlier file defines differently"),
    ({"acme.yaml": "id: https://x.example/acme\nimports:\n  - a\n", "a.yaml": "id: https://x.example/a\nclasses:\n  Concept:\n    description: mine\n"}, "a.yaml defines the class Concept, which LOKF core defines too"),
    ({"acme.yaml": "id: https://x.example/acme\nprefixes:\n  ex: https://x.example/one/\nimports:\n  - a\n", "a.yaml": "id: https://x.example/a\nprefixes:\n  ex: https://x.example/two/\n"}, "a.yaml maps the prefix ex to https://x.example/two/"),
    ({"acme.yaml": "id: https://x.example/acme\nsettings:\n  code: x\nimports:\n  - a\n", "a.yaml": "id: https://x.example/a\nsettings:\n  code: y\n"}, "a.yaml sets code to y, and an earlier file sets it to x"),
    ({"acme.yaml": "id: https://x.example/acme\nimports:\n  - ../../outside\n", "../../outside.yaml": "id: https://x.example/outside\n"}, "acme.yaml imports ../../outside, which is outside this repository"),
    ({"acme.yaml": "id: https://x.example/acme\nimports:\n  - a\n", "a.yaml": "id: https://x.example/a\nimports:\n  - b\n"}, "a.yaml imports b.yaml, which is not a LinkML schema file"),
], ids=["two-definitions", "core-name", "prefix", "setting", "outside", "nested-missing"])
def test_the_release_refuses_a_merge_that_would_lose_a_definition(tmp_path, files, why):
    """LinkML keeps the last definition of a name without a word, so a merge that would drop one stops the release instead. So does an import of a file outside the repository, or of one that is not there."""
    r, doc = pack_schema(tmp_path, files)
    assert r.rc == 1 and why in r.out and doc is None, r.out


def test_the_release_packs_again_when_only_the_domain_schema_changed(tmp_path):
    """The compare step's own lines, at six tags: a README edit, an edit to each copy the composite imports in a flow list over two lines, a refreshed lokf.yaml, and a justfile that names another schema already there. Only the README edit and the refreshed lokf.yaml leave an otherwise unchanged bundle without a zip."""
    body = step_body(RELEASE_YAML, "Compare with the last released bundle", r"^      [#-]")
    script = write(tmp_path / "compare.sh", "#!/usr/bin/env bash\n" + body)
    gh = write(tmp_path / "bin" / "gh", '#!/bin/sh\n[ "$1 $2" = "release view" ] && { echo "$3"; exit 0; }\n[ "$1" = api ] && { echo "$PREV"; exit 0; }\nexit 1\n')
    gh.chmod(0o755)
    h = make_host(tmp_path / "host", "default")
    write(h / ".lokf" / "justfile", re.sub(r'(?m)^schema := ""$', 'schema := "acme.yaml"', read(h / ".lokf" / "justfile")))
    write(h / ".lokf" / "acme.yaml", "id: https://x.example/acme\nimports: [linkml:types, lokf,  # core\n  'slsa', gha]  # two copies\n")
    write(h / ".lokf" / "slsa.yaml", "id: https://x.example/slsa\nimports:\n  # LOKF core by name\n  - lokf\n  - lokf.yaml\n")
    write(h / ".lokf" / "gha.yaml", "id: https://x.example/gha\n")
    write(h / ".lokf" / "lokf.yaml", "id: https://w3id.org/lokf\n")
    edits = {
        "v2": ("README.md", lambda text: text + "more\n"),
        "v3": (".lokf/slsa.yaml", lambda text: text + "classes: {}\n"),
        "v4": (".lokf/lokf.yaml", lambda text: text + "title: refreshed\n"),
        "v5": (".lokf/gha.yaml", lambda text: text + "classes: {}\n"),
        "v6": (".lokf/justfile", lambda text: text.replace('schema := "acme.yaml"', 'schema := "slsa.yaml"')),
    }
    git(h, "add", "-A")
    git(h, "commit", "-q", "-m", "schema")
    git(h, "-c", "tag.gpgSign=false", "tag", "v1")
    for tag, (rel, edit) in edits.items():
        write(h / rel, edit(read(h / rel)))
        git(h, "commit", "-qam", tag)
        git(h, "-c", "tag.gpgSign=false", "tag", tag)
    outputs = {}
    for prev, tag in zip(["v1", *edits], edits):
        git(h, "checkout", "-q", tag)
        out = write(tmp_path / f"out-{tag}", "")
        r = run(["bash", script], cwd=h, env={"PATH": f"{tmp_path / 'bin'}:{os.environ['PATH']}", "PREV": prev, "TAG": tag, "GH_REPO": "o/host", "GITHUB_OUTPUT": out, "FORCE": "false"})
        assert r.rc == 0, r.out
        outputs[tag] = (read(out), r.out)
    assert "changed=false" in outputs["v2"][0], outputs["v2"]
    assert "changed=true" in outputs["v3"][0] and "its domain schema changed" in outputs["v3"][1], outputs["v3"]
    assert "changed=false" in outputs["v4"][0], "a refreshed lokf.yaml, which the released copy imports by name, released the bundle again"
    assert "changed=true" in outputs["v5"][0] and "its domain schema changed" in outputs["v5"][1], "a copy on a flow list's second line was not compared"
    assert "changed=true" in outputs["v6"][0] and "now names slsa.yaml" in outputs["v6"][1], outputs["v6"]
