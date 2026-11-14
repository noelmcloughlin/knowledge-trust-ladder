"""The `ktl` command: list, locate and install the Knowledge Trust Ladder
skills that this package carries.

The package holds the six skills under `ktl/skills/` and the Claude Code
plugin manifest under `ktl/.claude-plugin/`, each byte for byte as the
release tag holds them. `ktl skills install` copies skill folders into the
folder an agent reads, and calls no other tool, so it works the same on
every operating system and forge, and with no network once the package is
installed. `gh skill install --from-local` and `npx skills add` take the
folder `ktl skills path` prints, where either is at hand.

The command uses the standard library alone and runs on Python 3.9 or
later, the python3 that RHEL 9 includes. The verbs are those of the lokf
toolkit's `lokf skills` command, so a person who uses both meets one shape.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

# Where each agent reads skills, at project scope (relative to the current
# folder) and at user scope (relative to the home folder). Each placement
# was checked against `gh skill install` 2.101. An agent not listed here
# takes --dest. No one folder serves them all: Claude Code reads only its
# own, and Copilot and Codex differ at user scope. So, as with `gh skill
# install`, GitHub Copilot is the agent when none is named.
AGENTS = {
    "claude-code": (".claude/skills", ".claude/skills"),
    "codex": (".agents/skills", ".agents/skills"),
    "github-copilot": (".agents/skills", ".copilot/skills"),
}
DEFAULT_AGENT = "github-copilot"

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


def frontmatter_value(skill_md: Path, key: str) -> str:
    """Read one top-level scalar from a SKILL.md's frontmatter.

    The skills write each value on one line, plain or single-quoted, so a
    line reader serves and the package needs no YAML parser.
    """
    lines = skill_md.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith(key + ":"):
            value = line[len(key) + 1 :].strip()
            if len(value) >= 2 and value[0] == value[-1] == "'":
                value = value[1:-1].replace("''", "'")
            elif len(value) >= 2 and value[0] == value[-1] == '"':
                value = value[1:-1]
            return value
    return ""


def first_sentence(text: str) -> str:
    end = text.find(". ")
    return text if end < 0 else text[: end + 1]


def target_folder(agent: str, scope: str) -> Path:
    project, user = AGENTS[agent]
    return (Path.home() / user) if scope == "user" else (Path.cwd() / project)


def install(names: list[str], dest: Path) -> None:
    """Copy each named skill folder into dest, replacing a folder of the
    same name. Each copy is made beside its target first and then renamed
    into place, so a failed copy leaves the old folder as it was."""
    dest.mkdir(parents=True, exist_ok=True)
    source = skills_dir()
    for name in names:
        target = dest / name
        staging = dest / f".{name}.ktl-new"
        if staging.is_symlink() or staging.is_file():
            staging.unlink()
        elif staging.exists():
            shutil.rmtree(staging)
        shutil.copytree(source / name, staging, ignore=IGNORED)
        if target.is_symlink() or target.is_file():
            target.unlink()
        elif target.exists():
            shutil.rmtree(target)
        staging.rename(target)


def cmd_list(args: argparse.Namespace) -> int:
    for name in skill_names():
        description = frontmatter_value(skills_dir() / name / "SKILL.md", "description")
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
    names = args.skill or available
    unknown = [n for n in names if n not in available]
    if unknown:
        parser.error(f"no skill named {', '.join(unknown)}; this package carries {', '.join(available)}")
    dest = args.dest if args.dest is not None else target_folder(args.agent or DEFAULT_AGENT, args.scope)
    install(names, dest)
    print(f"Installed {len(names)} skill{'s' if len(names) != 1 else ''} from ktl {version()} into {dest}: {', '.join(names)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ktl",
        description="List, locate and install the Knowledge Trust Ladder (KTL) skills this package carries.",
    )
    parser.add_argument("--version", action="version", version=f"ktl {version()}")
    groups = parser.add_subparsers(dest="group", metavar="skills")
    skills = groups.add_parser("skills", help="the six skills: list, path, install")
    actions = skills.add_subparsers(dest="action", metavar="{list,path,install}")

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
        epilog=f"Where each agent reads skills (project scope is relative to the current folder):\n{table}\n\n"
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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.group != "skills" or args.action is None:
        parser.print_help()
        return 2
    if args.action == "list":
        return cmd_list(args)
    if args.action == "path":
        return cmd_path(args)
    return cmd_install(args, parser)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
