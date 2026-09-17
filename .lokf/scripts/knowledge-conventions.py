#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml"]
# ///
# The frontmatter-shape half of knowledge-conventions.sh: rules 2, 3, 4, 7 and
# 9 (see that script's header for the full list of nine). Those five are
# grep/awk approximations of a YAML question - is this scalar quoted, is this
# key a list or a mapping, do two files share an id - that a real parser
# answers outright instead of pattern-matching around. An unquoted `at:` is
# only visible as a `datetime`/`date` object once something actually parses
# the document; a flow-style `verified: { by: ... }`, a multi-line flow item,
# or a `by:` inside a body code fence are exactly where the line-oriented
# regex approach used to guess wrong. Rules 1, 5, 6 and 8 stay in the shell
# script: they are git and filesystem facts, not frontmatter shape, and
# needn't wait on uv.
#
# Usage: knowledge-conventions.py <bundle-dir>. Same contract as the shell
# half: one line per finding on stdout, exit 1 if any; "OK" and exit 0 if
# none. Invoked by knowledge-conventions.sh through `uv run`, which reads the
# dependency block above and needs nothing preinstalled; run directly it
# needs python3 and pyyaml.

from __future__ import annotations

import re
import sys
from datetime import date, datetime
from pathlib import Path

import yaml

RESERVED = {"index.md", "log.md", "diataxis.md"}
OPEN_QUESTION = re.compile(r"^- \d{4}-\d{2}-\d{2}, (human|process):[^ :]+: ")


def split_frontmatter(text: str) -> tuple[str, str] | None:
    lines = text.split("\n")
    if not lines or lines[0] != "---":
        return None
    for i, line in enumerate(lines[1:], start=1):
        if line == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1 :])
    return None


def find_unquoted_at(node, where: str) -> list[str]:
    findings: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "at" and isinstance(value, (date, datetime)):
                findings.append(f"{where}at")
            findings.extend(find_unquoted_at(value, f"{where}{key}."))
    elif isinstance(node, list):
        for index, item in enumerate(node):
            findings.extend(find_unquoted_at(item, f"{where}[{index}]."))
    return findings


def check_file(path: Path, ids: dict[str, list[Path]]) -> list[str]:
    findings: list[str] = []
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        findings.append(f"{path}: starts with a byte order mark - save as UTF-8 without BOM")
        raw = raw[3:]
    text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")

    split = split_frontmatter(text)
    if split is None:
        findings.append(
            f"{path}: no closed frontmatter block - a concept starts with '---' and closes it before the body"
        )
        return findings
    fm_text, body = split

    try:
        frontmatter = yaml.safe_load(fm_text)
    except yaml.YAMLError as exc:
        findings.append(f"{path}: frontmatter is not valid YAML - {exc}")
        return findings
    if not isinstance(frontmatter, dict):
        findings.append(f"{path}: frontmatter is not a mapping")
        return findings

    # 2. every `at:` quoted - unquoted, YAML resolves it to a date/datetime.
    for where in find_unquoted_at(frontmatter, ""):
        findings.append(f"{path}: unquoted timestamp at {where}")

    # 3. verified is a list, never a bare mapping, and carries at most one
    #    process:lokf-librarian event.
    verified = frontmatter.get("verified")
    if isinstance(verified, dict):
        findings.append(f"{path}: verified is a bare mapping - write a one-item list")
        events = [verified]
    elif isinstance(verified, list):
        events = [item for item in verified if isinstance(item, dict)]
    else:
        events = []
    librarian_events = [e for e in events if e.get("by") == "process:lokf-librarian"]
    if len(librarian_events) > 1:
        findings.append(
            f"{path}: {len(librarian_events)} process:lokf-librarian events - "
            "the librarian replaces its own, never stacks"
        )

    # 4. a bullet under `## Open questions` is `- YYYY-MM-DD, <actor>: ...`.
    in_section = False
    for line in body.split("\n"):
        if line == "## Open questions":
            in_section = True
            continue
        if in_section and line.startswith("#"):
            in_section = False
        if in_section and line.startswith("- ") and not OPEN_QUESTION.match(line):
            findings.append(f"{path}: open question not '- YYYY-MM-DD, <actor>: ...': {line[:60]}")

    # 7. one file per id - collected here, reported once every file is read.
    concept_id = frontmatter.get("id")
    if isinstance(concept_id, str) and concept_id:
        ids.setdefault(concept_id, []).append(path)

    return findings


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: knowledge-conventions.py <bundle-dir>", file=sys.stderr)
        return 2
    bundle = Path(argv[1])
    if not bundle.is_dir():
        print(f"no bundle directory at {bundle}", file=sys.stderr)
        return 2

    findings: list[str] = []
    ids: dict[str, list[Path]] = {}
    for path in sorted(bundle.rglob("*.md")):
        if ".obsidian" in path.parts or path.name in RESERVED:
            continue
        findings.extend(check_file(path, ids))

    for concept_id, paths in ids.items():
        if len(paths) > 1:
            files = "".join(f"{p} " for p in paths)
            findings.append(
                f"id {concept_id} is declared by more than one file: {files}- "
                "a sync conflict copy or a pasted duplicate; keep one"
            )

    for line in findings:
        print(line)
    if findings:
        return 1
    print(f"OK - {bundle} keeps the frontmatter conventions lokf validate cannot check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
