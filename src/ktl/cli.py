"""The `ktl` command: list, locate, install and check the Knowledge Trust
Ladder skills that this package carries, and, with `ktl gh`, set the GitHub
settings the workflows those skills install need (src/ktl/gh.py).

The package holds the six skills under `ktl/skills/` and the Claude Code
plugin manifest under `ktl/.claude-plugin/`, each byte for byte as the
release tag holds them. `ktl skills install` copies skill folders into the
folder an agent reads, and calls no other tool, so it works the same on
every operating system and forge, and with no network once the package is
installed. `gh skill install --from-local` and `npx skills add` take the
folder `ktl skills path` prints, where either is at hand. `ktl skills
status` says, for each folder an agent reads, whether the KTL skills there
are this package's.

The command uses the standard library alone and runs on Python 3.9 or
later, the python3 that RHEL 9 includes. The verbs are those of the lokf
toolkit's `lokf skills` command, so a person who uses both meets one shape.
"""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import sys
import tempfile
from pathlib import Path

# Where each agent reads skills, at project scope (relative to the
# repository's top folder) and at user scope (relative to the home folder).
# Each placement was checked against `gh skill install` 2.101. An agent not
# listed here takes --dest. No one folder serves them all: Claude Code reads
# only its own, and Copilot and Codex differ at user scope. So, as with `gh
# skill install`, GitHub Copilot is the agent when none is named.
AGENTS = {
    "claude-code": (".claude/skills", ".claude/skills"),
    "codex": (".agents/skills", ".agents/skills"),
    "github-copilot": (".agents/skills", ".copilot/skills"),
}
DEFAULT_AGENT = "github-copilot"

# A project folder Copilot-style agents also read, which no installer here
# writes. `status` checks it, as the sidecar's preflight does.
OTHER_PROJECT_FOLDERS = {".github/skills": "github-copilot"}

# Files a copy never needs: bytecode a Python run may have left beside a
# script.
IGNORED = shutil.ignore_patterns("__pycache__", "*.pyc")


def package_root() -> Path:
    """Return the folder that holds `skills/` and `.claude-plugin/`.

    In an installed package that is the `ktl` package folder. In a checkout
    of the repository, where the build has not copied the skills in, it is
    the repository root, two folders above `src/ktl/`.
    """
    here = Path(__file__).resolve().parent
    if (here / "skills").is_dir():
        return here
    checkout = here.parent.parent
    if (checkout / "skills" / "ktl-docent" / "SKILL.md").is_file():
        return checkout
    raise SystemExit(f"ktl: no skills folder in {here} or in a checkout above it; reinstall the package")


def skills_dir() -> Path:
    return package_root() / "skills"


def skill_names() -> list[str]:
    return sorted(p.parent.name for p in skills_dir().glob("*/SKILL.md"))


def version() -> str:
    try:
        from importlib.metadata import PackageNotFoundError, version as dist_version
    except ImportError:  # pragma: no cover - every supported Python has it
        return "unknown"
    try:
        return dist_version("ktl")
    except PackageNotFoundError:
        return "0.0.0 (a checkout, not an installed package)"


def scalar(text: str) -> str:
    """One YAML scalar written on one line: plain, single-quoted or double-quoted."""
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] == "'":
        return text[1:-1].replace("''", "'")
    if len(text) >= 2 and text[0] == text[-1] == '"':
        return text[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return text


def read_skill_md(path: Path) -> tuple[dict[str, str], dict[str, str], str]:
    """Split a SKILL.md into its frontmatter values, its metadata block and its body.

    The skills write each value on one line, plain or quoted, so a line
    reader serves and the package needs no YAML parser. `gh skill install`
    rewrites the file as it installs it: the keys come out sorted, a quoted
    value can come out plain, a metadata block names the source, and the
    blank line after the frontmatter goes. Reading each value, and the body
    without its leading blank lines, undoes all four, so two copies of one
    release read the same however each was installed.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    values: dict[str, str] = {}
    metadata: dict[str, str] = {}
    if not lines or lines[0].strip() != "---":
        return values, metadata, "\n".join(lines).lstrip("\n")
    key = ""
    for number, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return values, metadata, "\n".join(lines[number + 1 :]).lstrip("\n")
        if line[:1] in (" ", "\t"):
            if key == "metadata" and ":" in line:
                name, value = line.split(":", 1)
                metadata[name.strip()] = scalar(value)
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            if key != "metadata":
                values[key] = scalar(value)
    return values, metadata, ""


def first_sentence(text: str) -> str:
    end = text.find(". ")
    return text if end < 0 else text[: end + 1]


def project_root(start: Path) -> Path:
    """Return the top folder of the repository that holds start: the nearest
    folder at or above it with a `.git` entry, which is a folder in a clone
    and a file in a worktree or a submodule. With none, start itself."""
    for folder in (start, *start.parents):
        if (folder / ".git").exists():
            return folder
    return start


def target_folder(agent: str, scope: str) -> Path:
    project, user = AGENTS[agent]
    return (Path.home() / user) if scope == "user" else (project_root(Path.cwd()) / project)


def install(names: list[str], dest: Path) -> None:
    """Copy each named skill folder into dest, replacing a folder of the
    same name.

    Every skill is copied into one hidden staging folder in dest first, and
    the old folders are swapped for the new ones only once all are copied.
    So a copy that fails, for want of space, say, leaves the earlier release
    whole rather than half replaced. The staging folder holds each skill a
    level down, where no agent looks for one.
    """
    dest.mkdir(parents=True, exist_ok=True)
    source = skills_dir()
    staging = Path(tempfile.mkdtemp(prefix=".ktl-", dir=dest))
    try:
        for name in names:
            shutil.copytree(source / name, staging / name, ignore=IGNORED)
        for name in names:
            target = dest / name
            if target.is_symlink() or target.is_file():
                target.unlink()
            elif target.exists():
                shutil.rmtree(target)
            (staging / name).rename(target)
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def files_of(folder: Path) -> dict[str, Path]:
    """Every file in a skill folder by its path inside it, bytecode aside."""
    return {
        p.relative_to(folder).as_posix(): p
        for p in sorted(folder.rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }


def executable(path: Path) -> bool:
    return bool(path.stat().st_mode & stat.S_IXUSR)


def same_skill_md(a: Path, b: Path) -> bool:
    """Whether two SKILL.md files read the same, gh's metadata block aside."""
    values_a, _, body_a = read_skill_md(a)
    values_b, _, body_b = read_skill_md(b)
    return values_a == values_b and body_a == body_b


def compare(installed: Path, carried: Path) -> tuple[list[str], list[str]]:
    """Compare an installed skill with this package's copy of it.

    Return the files whose content differs, or that only one copy holds,
    and the files this package marks executable that the installed copy
    does not. A SKILL.md counts as the same when it reads the same through
    read_skill_md. The skills run their scripts through bash, so a lost
    executable bit is reported apart from a change of content.
    """
    mine, theirs = files_of(carried), files_of(installed)
    changed = sorted(set(mine) ^ set(theirs))
    not_executable = []
    for rel in sorted(set(mine) & set(theirs)):
        a, b = mine[rel], theirs[rel]
        if a.read_bytes() != b.read_bytes() and not (rel == "SKILL.md" and same_skill_md(a, b)):
            changed.append(rel)
        if os.name != "nt" and executable(a) and not executable(b):
            not_executable.append(rel)
    return sorted(changed), not_executable


def where(folder: Path) -> str:
    try:
        return "~/" + folder.relative_to(Path.home()).as_posix()
    except ValueError:
        return str(folder)


def folders_to_check(dest: Path | None) -> dict[Path, list[str]]:
    """Each folder an agent reads skills from, with who reads it: the
    project's folders first, then the user's."""
    if dest is not None:
        return {dest: []}
    root = project_root(Path.cwd())
    readers: dict[Path, list[str]] = {}
    for agent, (project, _) in sorted(AGENTS.items()):
        readers.setdefault(root / project, []).append(f"{agent}, project")
    for folder, agent in OTHER_PROJECT_FOLDERS.items():
        readers.setdefault(root / folder, []).append(f"{agent}, project")
    for agent, (_, user) in sorted(AGENTS.items()):
        readers.setdefault(Path.home() / user, []).append(f"{agent}, user")
    return readers


def state(folder: Path, name: str, carried: list[str]) -> tuple[str, bool]:
    """One installed skill's line in `status`, and whether it matches this package."""
    skill = folder / name
    if name not in carried:
        return "not in this package: an older release's, or another's", False
    changed, not_executable = compare(skill, skills_dir() / name)
    ref = read_skill_md(skill / "SKILL.md")[1].get("github-ref", "")
    source = f"; installed by gh skill from {ref.rsplit('/', 1)[-1]}" if ref else ""
    if changed:
        shown = ", ".join(changed[:3]) + (", ..." if len(changed) > 3 else "")
        count = f"{len(changed)} file{'s' if len(changed) != 1 else ''}"
        return f"differs from this package in {count} ({shown}){source}", False
    lost = f", though {len(not_executable)} script{'s' if len(not_executable) != 1 else ''} lost the executable bit" if not_executable else ""
    return f"same as this package{lost}{source}", True


def cmd_list(args: argparse.Namespace) -> int:
    for name in skill_names():
        description = read_skill_md(skills_dir() / name / "SKILL.md")[0].get("description", "")
        print(f"{name}\t{first_sentence(description)}")
    return 0


def cmd_path(args: argparse.Namespace) -> int:
    print(package_root() if args.marketplace else skills_dir())
    return 0


def cmd_install(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    if args.dest is not None and (args.agent or args.scope):
        parser.error("give --dest, or --scope with an optional --agent, not both")
    if args.dest is None and not args.scope:
        parser.error("name the scope (--scope user|project), or a folder with --dest")
    available = skill_names()
    names = sorted(set(args.skill)) if args.skill else available
    unknown = [n for n in names if n not in available]
    if unknown:
        parser.error(f"no skill named {', '.join(unknown)}; this package carries {', '.join(available)}")
    dest = args.dest if args.dest is not None else target_folder(args.agent or DEFAULT_AGENT, args.scope)
    install(names, dest)
    print(f"Installed {len(names)} skill{'s' if len(names) != 1 else ''} from ktl {version()} into {dest}: {', '.join(names)}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    carried = skill_names()
    print(f"ktl {version()} carries {', '.join(carried)}.")
    in_step, empty = True, []
    for folder, readers in folders_to_check(args.dest).items():
        present = sorted(p.parent.name for p in folder.glob("ktl-*/SKILL.md")) if folder.is_dir() else []
        if not present:
            empty.append(where(folder))
            continue
        print(where(folder) + (f" (read by {'; '.join(readers)})" if readers else ""))
        for name in present:
            line, same = state(folder, name, carried)
            in_step = in_step and same
            print(f"  {name:<14} {line}")
        absent = [name for name in carried if name not in present]
        if absent:
            print(f"  {'not here':<14} {', '.join(absent)}")
    if empty:
        print(f"No KTL skill in {', '.join(empty)}.")
    return 0 if in_step else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ktl",
        description="List, locate, install and check the Knowledge Trust Ladder (KTL) skills this package carries, "
        "and set the GitHub settings the workflows they install need.",
    )
    parser.add_argument("--version", action="version", version=f"ktl {version()}")
    groups = parser.add_subparsers(dest="group", metavar="{skills,gh}")
    skills = groups.add_parser("skills", help="the six skills: list (the default), path, install, status")
    actions = skills.add_subparsers(dest="action", metavar="{list,path,install,status}")

    actions.add_parser("list", help="name each skill, with the first sentence of its description")

    path = actions.add_parser("path", help="print the folder that holds the skills")
    path.add_argument(
        "--marketplace",
        action="store_true",
        help="print the folder that holds .claude-plugin/ instead, for `claude plugin marketplace add`",
    )

    table = "\n".join(
        f"  {agent:<15} project: {project}/   user: ~/{user}/" for agent, (project, user) in sorted(AGENTS.items())
    )
    install_parser = actions.add_parser(
        "install",
        help="copy the skills into the folder an agent reads",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Copy the skills into the folder an agent reads, replacing any earlier copy of each.",
        epilog=f"Where each agent reads skills (project scope is relative to the repository's top folder):\n{table}\n\n"
        f"With no --agent, the agent is {DEFAULT_AGENT}. Give --dest for any other agent or folder.",
    )
    install_parser.add_argument(
        "--agent", choices=sorted(AGENTS), help=f"the agent whose folder to use (default: {DEFAULT_AGENT})"
    )
    install_parser.add_argument("--scope", choices=["user", "project"], help="the user's folder, or this project's")
    install_parser.add_argument("--dest", type=Path, help="install into this folder instead")
    install_parser.add_argument(
        "--skill",
        action="append",
        metavar="NAME",
        help="install only this skill; repeat for more (default: all six)",
    )

    status = actions.add_parser(
        "status",
        help="say whether the KTL skills in each folder an agent reads are this package's",
        description="For each folder an agent reads skills from, at project and user scope, say whether each KTL "
        "skill there is the same as this package's copy. A copy gh skill installed counts as the same when only "
        "gh's own rewrite of its SKILL.md differs. Exits 1 when an installed copy differs, so a script can act on it.",
    )
    status.add_argument("--dest", type=Path, help="check this folder only")

    from ktl import gh

    gh.add_parser(groups)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.group == "gh":
        from ktl import gh

        return gh.main(args)
    if args.group != "skills":
        parser.print_help()
        return 2
    try:
        if args.action in (None, "list"):
            return cmd_list(args)
        if args.action == "path":
            return cmd_path(args)
        if args.action == "status":
            return cmd_status(args)
        return cmd_install(args, parser)
    except OSError as error:
        reason = error.strerror or str(error)
        print(f"ktl: {reason}: {error.filename}" if error.filename else f"ktl: {reason}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
