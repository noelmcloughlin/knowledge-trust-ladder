"""The `ktl gh` command: the GitHub settings a repository's workflows need.

A host that adopts the Knowledge Trust Ladder (KTL) sets repository
variables, Environments with their branch rules and reviewers, secrets,
rulesets and a few repository settings. Which ones depends on the workflows
it carries. Each skill that installs workflows carries a catalogue of them
beside its pages, references/repository-settings.json, and a repository may
describe its own workflows in .github/repository-settings.json and in any
file under .github/repository-settings/. This command reads those
catalogues, compares them with the repository's settings, and sets what is
missing. skills/ktl-sidecar/references/repository-settings.md describes the
verbs and the catalogue's fields.

It calls the GitHub CLI for everything, with the person's own login, so it
holds no token and needs no library. gh makes each API call, and seals each
secret to the repository's public key, which the standard library cannot do.
A secret's value reaches gh on standard input, never in an argument, where
other users of the machine could read it.

apply never loosens a setting and never turns a switch on. What it cannot
judge, such as a wider branch rule or a variable with another value, it
reports for a person. prune is the one verb that removes anything, and it
removes only what no workflow here can read, or a copy that a safer place
already holds. Every change is printed before it is made.
"""

from __future__ import annotations

import argparse
import base64
import fnmatch
import functools
import getpass
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from ktl import cli

FORMAT = 1
CATALOGUE = "repository-settings.json"
OWN_CATALOGUE = ".github/repository-settings.json"
OWN_CATALOGUE_DIR = ".github/repository-settings"
WORKFLOWS = ".github/workflows"
LEVELS = ("required", "recommended", "optional")
RANK = {level: n for n, level in enumerate(LEVELS)}

# The fields each kind of entry may carry. A field outside these is a typo,
# and a catalogue that holds one is refused rather than half read.
COMMON = {"kind", "name", "workflows", "level", "why", "docs"}
KEYS = {
    "variable": COMMON | {"switch", "job_level", "pattern", "check"},
    "secret": COMMON | {"environment", "repository_copy", "names_from", "unless"},
    "environment": COMMON | {"branches", "tags", "reviewers", "named_by"},
    "setting": COMMON | {"value", "report_only", "visibility"},
    "ruleset": COMMON | {"target", "include", "rules"},
}
TOP_KEYS = {"format", "source", "about", "docs", "roles", "presets", "settings", "retired"}
SWITCH_KEYS = {"name", "values", "requires", "run", "environment"}
RETIRED_KEYS = {"kind", "name", "replaced_by", "changelog", "why"}
PRESET_KEYS = {"title", "variables", "default_for", "docs"}
ROLE_KEYS = {"title", "workflows", "with"}
REQUIREMENT_KEYS = {
    "variable", "equals", "unset", "secret", "environment", "any", "setting", "value", "pages",
    "without", "without_publishers", "file", "secrets_from", "confirm", "visibility", "text",
}

# The repository settings a catalogue may name, in the order apply sets
# them: Dependabot's security updates need its alerts on first.
SETTINGS = (
    "actions.default_workflow_permissions",
    "actions.can_approve_pull_request_reviews",
    "actions.sha_pinning_required",
    "pages.build_type",
    "repository.default_branch",
    "repository.has_issues",
    "security.secret_scanning",
    "security.secret_scanning_push_protection",
    "security.private_vulnerability_reporting",
    "security.vulnerability_alerts",
    "security.dependabot_security_updates",
)

# The order apply makes its changes in: an Environment exists before its
# branch rules and reviewers, and settings come before the values that
# depend on them.
STAGE_ENVIRONMENT, STAGE_RULES, STAGE_SETTING, STAGE_RULESET, STAGE_VARIABLE = 10, 20, 30, 60, 70

READS = re.compile(r"\b(vars|secrets)\.([A-Za-z_][A-Za-z0-9_]*)")
USES = re.compile(r"^\s*(?:-\s+)?uses:\s*['\"]?([^\s'\"#]+)", re.M)
JOB_KEY = re.compile(r"^ {4}(if|runs-on|environment):(.*)$")
# A job's Environment, written on the key's own line or as the `name:` on
# the line after it.
ENVIRONMENT_VALUE = re.compile(r"^[ \t]+environment:[ \t]*(?:\n[ \t]+name:[ \t]*)?([^\n#]*?)[ \t]*$", re.M)
SHA = re.compile(r"[0-9a-f]{40}")
# What the website skill's deploy page counts as another Pages publisher.
PUBLISHERS = ("deploy-pages", "upload-pages-artifact", "gh-pages", "gh-deploy", "github-pages-deploy-action")
KTL_PUBLISHERS = ("knowledge-website.yaml", "knowledge-federation.yaml")
# Values a list of repositories reads as naming none.
NO_REPOSITORIES = {"", "false", "off", "no", "0", "none", "true", "on", "yes", "1"}


class GhError(Exception):
    """gh could not answer, or answered with an error the command cannot pass over."""


class CatalogueError(Exception):
    """A catalogue that cannot be read, or that holds a field this command does not know."""


# The catalogues


@dataclass
class Catalogue:
    source: str
    path: str
    roles: dict
    presets: dict
    entries: list
    retired: list


def requirement_problems(req: object, where: str) -> list:
    if not isinstance(req, dict) or not req:
        return [f"{where}: a requirement is a non-empty object"]
    problems = [f"{where}: unknown requirement field {key!r}" for key in req if key not in REQUIREMENT_KEYS]
    for sub in req.get("any", []):
        problems += requirement_problems(sub, where)
    if "setting" in req and req["setting"] not in SETTINGS:
        problems.append(f"{where}: unknown setting {req['setting']!r}")
    return problems


def problems_of(data: object, path: str) -> list:
    """Every way a catalogue breaks the format, so that a test names them all at once."""
    if not isinstance(data, dict):
        return [f"{path}: a catalogue is a JSON object"]
    problems = []
    if data.get("format") != FORMAT:
        problems.append(f"{path}: format is {data.get('format')!r}; this ktl reads format {FORMAT}")
    problems += [f"{path}: unknown top-level field {key!r}" for key in data if key not in TOP_KEYS]
    for name, role in data.get("roles", {}).items():
        problems += [f"{path}: role {name}: unknown field {k!r}" for k in role if k not in ROLE_KEYS]
    for name, preset in data.get("presets", {}).items():
        problems += [f"{path}: preset {name}: unknown field {k!r}" for k in preset if k not in PRESET_KEYS]
    for n, entry in enumerate(data.get("settings", [])):
        where = f"{path}: settings[{n}] {entry.get('name', '?')}"
        kind = entry.get("kind")
        if kind not in KEYS:
            problems.append(f"{where}: kind {kind!r} is not one of {', '.join(KEYS)}")
            continue
        problems += [f"{where}: unknown field {k!r}" for k in entry if k not in KEYS[kind]]
        if not entry.get("name") or not entry.get("why"):
            problems.append(f"{where}: every entry has a name and a why")
        if entry.get("level", "required") not in LEVELS:
            problems.append(f"{where}: level is one of {', '.join(LEVELS)}")
        if kind == "setting" and entry.get("name") not in SETTINGS:
            problems.append(f"{where}: unknown setting; this ktl knows {', '.join(SETTINGS)}")
        switch = entry.get("switch")
        if switch is not None:
            problems += [f"{where}: switch: unknown field {k!r}" for k in switch if k not in SWITCH_KEYS]
            for req in switch.get("requires", []):
                problems += requirement_problems(req, where)
        if entry.get("unless") is not None:
            problems += requirement_problems(entry["unless"], where)
        if entry.get("pattern"):
            try:
                re.compile(entry["pattern"])
            except re.error as error:
                problems.append(f"{where}: pattern does not compile: {error}")
    for n, old in enumerate(data.get("retired", [])):
        where = f"{path}: retired[{n}] {old.get('name', '?')}"
        problems += [f"{where}: unknown field {k!r}" for k in old if k not in RETIRED_KEYS]
        if old.get("kind") not in ("variable", "secret"):
            problems.append(f"{where}: a retired name is a variable or a secret")
    return problems


def load_catalogue(text: str, path: str) -> Catalogue:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise CatalogueError(f"{path} is not JSON: {error}") from None
    problems = problems_of(data, path)
    if problems:
        raise CatalogueError("\n".join(problems))
    source = data.get("source", path)
    base = data.get("docs", "")
    entries = []
    for entry in data.get("settings", []):
        docs = entry.get("docs", "")
        url = docs if not docs or "://" in docs else base + docs
        entries.append(dict(entry, level=entry.get("level", "required"), source=source, url=url))
    presets = {}
    for name, preset in data.get("presets", {}).items():
        docs = preset.get("docs", "")
        presets[name] = dict(preset, url=docs if not docs or "://" in docs else base + docs)
    return Catalogue(source, path, data.get("roles", {}), presets, entries, data.get("retired", []))


def package_catalogues() -> list:
    """The catalogues of the skills this package carries: one for each skill that installs workflows."""
    return sorted(cli.skills_dir().glob(f"*/references/{CATALOGUE}"))


# Reading workflow files without a YAML parser. Each question asked of a
# workflow is a pattern over its text, which serves files written in
# GitHub's usual two-space layout, as every KTL and lmodel workflow is.


def names_read(text: str) -> set:
    """Each variable and secret a workflow names, as (kind, name) pairs."""
    return {
        ("variable" if scope == "vars" else "secret", name)
        for scope, name in READS.findall(text)
        if name != "GITHUB_TOKEN"
    }


def job_level_reads(text: str) -> set:
    """The variables a job's own `if:`, `runs-on:` or `environment:` reads.

    GitHub works those out before the job's Environment applies, so a copy
    of such a variable on an Environment is never seen there.
    """
    names = set()
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        match = JOB_KEY.match(lines[i])
        i += 1
        if not match:
            continue
        block = [match.group(2)]
        while i < len(lines) and (not lines[i].strip() or len(lines[i]) - len(lines[i].lstrip()) > 4):
            block.append(lines[i])
            i += 1
        names |= {name for scope, name in READS.findall("\n".join(block)) if scope == "vars"}
    return names


def unpinned_actions(text: str) -> list:
    """Each action or reusable workflow a workflow uses that is not pinned to a commit."""
    found = []
    for ref in USES.findall(text):
        if ref.startswith(("./", "docker://")):
            continue
        if not SHA.fullmatch(ref.partition("@")[2]):
            found.append(ref)
    return found


def environment_values(text: str) -> list:
    return [value for value in ENVIRONMENT_VALUE.findall(text) if value]


def literal_environments(text: str) -> set:
    """The Environments a workflow names in so many words, not through an expression."""
    return {v for v in environment_values(text) if re.fullmatch(r"[A-Za-z0-9._-]+", v)}


def names_environment(text: str, name: str) -> bool:
    """Whether a job runs in the Environment: named outright, or as one of
    the quoted names an expression picks from, as pypi.yml picks 'pypi' or
    'testpypi'. A step or an artifact of the same name does not count."""
    if name in literal_environments(text):
        return True
    return any(name in re.findall(r"'([^']*)'", v) for v in environment_values(text) if "${{" in v)


def same(a: str, b: str) -> bool:
    """Whether two values compare equal in a workflow expression, which
    ignores case when it compares strings."""
    return a.lower() == b.lower()


def mentions(text: str, word: str) -> bool:
    return re.search(rf"(?<![A-Za-z0-9_-]){re.escape(word)}(?![A-Za-z0-9_-])", text) is not None


# gh


def message(payload: object) -> str:
    if isinstance(payload, dict) and payload.get("message"):
        return str(payload["message"])
    return str(payload or "").strip()[:300]


def parse_response(stdout: str) -> tuple:
    """Split what `gh api --include` printed into the HTTP status and the JSON body.

    A redirect gh followed prints a header block of its own first, so the
    status is the last block's.
    """
    text, status = stdout, None
    while text.startswith("HTTP/"):
        parts = re.split(r"\r?\n\r?\n", text, maxsplit=1)
        try:
            status = int(parts[0].split(None, 2)[1])
        except (IndexError, ValueError):
            return None, None
        text = parts[1] if len(parts) > 1 else ""
    text = text.strip()
    if status is None or not text:
        return status, None
    try:
        return status, json.loads(text)
    except json.JSONDecodeError:
        return status, text


class GitHub:
    """Every call goes through gh, with the person's own login."""

    def __init__(self, run: Callable = subprocess.run):
        self._run = run

    def _gh(self, args: list, stdin: str | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess:
        try:
            return self._run(["gh", *args], input=stdin, capture_output=True, text=True, cwd=cwd)
        except FileNotFoundError:
            raise GhError("gh is not installed; install the GitHub CLI and sign in with `gh auth login`") from None

    def call(self, method: str, path: str, body: object = None) -> tuple:
        args = ["api", "--include", "--method", method, path, "-H", "X-GitHub-Api-Version: 2022-11-28"]
        stdin = None
        if body is not None:
            args += ["--input", "-"]
            stdin = json.dumps(body)
        proc = self._gh(args, stdin)
        status, payload = parse_response(proc.stdout or "")
        if status is None:
            raise GhError((proc.stderr or proc.stdout or f"gh api {path} failed").strip())
        return status, payload

    def set_secret(self, repo: str, name: str, value: str, environment: str | None) -> None:
        """Seal a value to the repository's or the Environment's key and store it.

        The value goes to gh on standard input: `gh secret set` reads it
        from there when no --body is given.
        """
        args = ["secret", "set", name, "--repo", repo]
        if environment:
            args += ["--env", environment]
        proc = self._gh(args, value)
        if proc.returncode != 0:
            raise GhError((proc.stderr or "gh secret set failed").strip())

    def current_repo(self, cwd: Path) -> str:
        proc = self._gh(["repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"], cwd=cwd)
        if proc.returncode != 0 or not (proc.stdout or "").strip():
            reason = (proc.stderr or "").strip() or "it has no GitHub remote"
            raise GhError(f"cannot tell which GitHub repository {cwd} is: {reason}. Name it with --repo OWNER/NAME.")
        return proc.stdout.strip()


# The repository and its settings


@dataclass
class Repository:
    slug: str
    workflows: dict
    where: str
    read_file: Callable
    list_dir: Callable
    local: bool


def local_repository(github: GitHub) -> Repository:
    root = cli.project_root(Path.cwd())
    folder = root / WORKFLOWS
    workflows = {}
    if folder.is_dir():
        for path in sorted(folder.iterdir()):
            if path.suffix in (".yml", ".yaml") and path.is_file():
                workflows[path.name] = path.read_text(encoding="utf-8", errors="replace")

    def read_file(rel: str) -> str | None:
        path = root / rel
        return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else None

    def list_dir(rel: str) -> list:
        path = root / rel
        return sorted(p.name for p in path.iterdir() if p.is_file()) if path.is_dir() else []

    return Repository(github.current_repo(root), workflows, f"the working tree at {root}", read_file, list_dir, True)


def remote_repository(github: GitHub, slug: str) -> Repository:
    def listing(rel: str) -> list:
        status, payload = github.call("GET", f"repos/{slug}/contents/{rel}")
        if status == 404:
            return []
        if status != 200 or not isinstance(payload, list):
            raise GhError(f"cannot list {rel} in {slug}: HTTP {status}: {message(payload)}")
        return payload

    def read_file(rel: str) -> str | None:
        status, payload = github.call("GET", f"repos/{slug}/contents/{rel}")
        if status != 200 or not isinstance(payload, dict) or payload.get("type") != "file":
            return None
        return base64.b64decode(payload.get("content", "")).decode("utf-8", errors="replace")

    def list_dir(rel: str) -> list:
        return sorted(i["name"] for i in listing(rel) if i.get("type") == "file")

    workflows = {}
    for item in listing(WORKFLOWS):
        name = item.get("name", "")
        if item.get("type") == "file" and name.endswith((".yml", ".yaml")):
            workflows[name] = read_file(f"{WORKFLOWS}/{name}") or ""
    return Repository(slug, workflows, "the default branch on GitHub", read_file, list_dir, False)


class State:
    """The repository's settings as the API reports them, each read once, and only when asked for."""

    def __init__(self, github: GitHub, slug: str):
        self.github = github
        self.slug = slug
        self.unreadable: list = []
        self._read: dict = {}

    def once(self, key: tuple, read: Callable) -> object:
        """Read something once: a second ask returns the first answer."""
        if key not in self._read:
            self._read[key] = read()
        return self._read[key]

    def get(self, path: str, missing: object = None, soft: bool = False) -> object:
        status, payload = self.github.call("GET", path)
        if status == 404:
            return missing
        if status >= 400:
            if soft:
                self.unreadable.append(f"{path.split('?')[0]} (HTTP {status})")
                return missing
            raise GhError(f"GET {path}: HTTP {status}: {message(payload)}")
        return payload if payload is not None else {}

    def listing(self, path: str, key: str | None, per_page: int) -> list:
        items, page = [], 1
        while True:
            data = self.get(f"{path}?per_page={per_page}&page={page}", missing={}, soft=True)
            batch = data.get(key, []) if key and isinstance(data, dict) else (data if isinstance(data, list) else [])
            items += batch
            if len(batch) < per_page:
                return items
            page += 1

    @functools.cached_property
    def info(self) -> dict:
        info = self.get(f"repos/{self.slug}")
        if not info:
            raise GhError(f"no repository {self.slug}, or your gh login cannot see it")
        return info

    @property
    def visibility(self) -> str:
        return self.info.get("visibility") or ("private" if self.info.get("private") else "public")

    @property
    def default_branch(self) -> str:
        return self.info.get("default_branch") or "main"

    @property
    def admin(self) -> bool:
        return bool((self.info.get("permissions") or {}).get("admin", True))

    @functools.cached_property
    def user(self) -> dict:
        return self.get("user", missing={}, soft=True) or {}

    @functools.cached_property
    def plan_name(self) -> str | None:
        """The owner's GitHub plan, where the login can see it, or None.

        It decides what a private repository has: no Environments or
        rulesets on GitHub Free, and no required reviewers short of
        Enterprise.
        """
        owner = self.info.get("owner") or {}
        if owner.get("type") == "Organization":
            org = self.get(f"orgs/{owner.get('login')}", missing={}, soft=True) or {}
            return (org.get("plan") or {}).get("name")
        if owner.get("login") and owner.get("login") == self.user.get("login"):
            return (self.user.get("plan") or {}).get("name")
        return None

    @property
    def environments_available(self) -> bool:
        return self.visibility == "public" or self.plan_name != "free"

    @property
    def reviewers_available(self) -> bool:
        return self.visibility == "public" or self.plan_name not in ("free", "pro", "team")

    @functools.cached_property
    def environments(self) -> dict:
        if not self.environments_available:
            return {}
        return {env["name"]: env for env in self.listing(f"repos/{self.slug}/environments", "environments", 100)}

    def branch_policies(self, environment: str) -> list:
        def read() -> list:
            found = self.listing(f"repos/{self.slug}/environments/{environment}/deployment-branch-policies", "branch_policies", 100)
            return [(p.get("type") or "branch", p["name"]) for p in found]

        return self.once(("policies", environment), read)

    @functools.cached_property
    def variables(self) -> dict:
        return {v["name"]: v.get("value", "") for v in self.listing(f"repos/{self.slug}/actions/variables", "variables", 30)}

    def env_variables(self, environment: str) -> dict:
        def read() -> dict:
            found = self.listing(f"repos/{self.slug}/environments/{environment}/variables", "variables", 30)
            return {v["name"]: v.get("value", "") for v in found}

        return self.once(("variables", environment), read)

    @functools.cached_property
    def secrets(self) -> set:
        return {s["name"] for s in self.listing(f"repos/{self.slug}/actions/secrets", "secrets", 100)}

    def env_secrets(self, environment: str) -> set:
        def read() -> set:
            return {s["name"] for s in self.listing(f"repos/{self.slug}/environments/{environment}/secrets", "secrets", 100)}

        return self.once(("secrets", environment), read)

    @functools.cached_property
    def actions_permissions(self) -> dict:
        return self.get(f"repos/{self.slug}/actions/permissions", missing={}, soft=True) or {}

    @functools.cached_property
    def workflow_permissions(self) -> dict:
        return self.get(f"repos/{self.slug}/actions/permissions/workflow", missing={}, soft=True) or {}

    @functools.cached_property
    def pages(self) -> dict | None:
        return self.get(f"repos/{self.slug}/pages", missing=None, soft=True)

    @functools.cached_property
    def rulesets(self) -> list:
        summaries = self.listing(f"repos/{self.slug}/rulesets", None, 100)
        return [self.get(f"repos/{self.slug}/rulesets/{r['id']}", missing=None, soft=True) or r for r in summaries]

    def flag(self, path: str) -> bool | None:
        """A setting the API turns on with a PUT: True, False, or None when it cannot be read."""
        status, payload = self.github.call("GET", path)
        if status == 204:
            return True
        if status == 404:
            return False
        if status >= 400:
            self.unreadable.append(f"{path} (HTTP {status})")
            return None
        return bool((payload or {}).get("enabled"))

    def setting(self, name: str) -> object:
        """The current value of a setting a catalogue names, or None when it cannot be read."""
        return self.once(("setting", name), lambda: self.read_setting(name))

    def read_setting(self, name: str) -> object:
        security = self.info.get("security_and_analysis") or {}
        if name == "actions.can_approve_pull_request_reviews":
            return self.workflow_permissions.get("can_approve_pull_request_reviews")
        if name == "actions.default_workflow_permissions":
            return self.workflow_permissions.get("default_workflow_permissions")
        if name == "actions.sha_pinning_required":
            return bool(self.actions_permissions.get("sha_pinning_required")) if self.actions_permissions else None
        if name == "pages.build_type":
            return "off" if self.pages is None else self.pages.get("build_type")
        if name == "repository.default_branch":
            return self.default_branch
        if name == "repository.has_issues":
            return self.info.get("has_issues")
        if name == "security.vulnerability_alerts":
            return self.flag(f"repos/{self.slug}/vulnerability-alerts")
        if name == "security.private_vulnerability_reporting":
            return self.flag(f"repos/{self.slug}/private-vulnerability-reporting")
        if name == "security.dependabot_security_updates":
            status = (security.get("dependabot_security_updates") or {}).get("status")
            return status == "enabled" if status else self.flag(f"repos/{self.slug}/automated-security-fixes")
        status = (security.get(name.split(".", 1)[1]) or {}).get("status")
        return None if status is None else status == "enabled"


@dataclass
class Op:
    """One change the command makes: an API call."""

    method: str
    path: str
    body: object = None

    def run(self, github: GitHub) -> None:
        status, payload = github.call(self.method, self.path, self.body)
        if status >= 400:
            raise GhError(f"{self.method} {self.path}: HTTP {status}: {message(payload)}")


def setting_ops(state: State, name: str, value: object) -> list:
    """The calls that give a repository setting a value."""
    slug = state.slug
    if name in ("actions.can_approve_pull_request_reviews", "actions.default_workflow_permissions"):
        body = {
            "default_workflow_permissions": state.workflow_permissions.get("default_workflow_permissions") or "read",
            "can_approve_pull_request_reviews": bool(state.workflow_permissions.get("can_approve_pull_request_reviews")),
        }
        body[name.split(".", 1)[1]] = value
        return [Op("PUT", f"repos/{slug}/actions/permissions/workflow", body)]
    if name == "actions.sha_pinning_required":
        current = state.actions_permissions
        body = {"enabled": current.get("enabled", True), "sha_pinning_required": value}
        if current.get("allowed_actions"):
            body["allowed_actions"] = current["allowed_actions"]
        return [Op("PUT", f"repos/{slug}/actions/permissions", body)]
    if name == "pages.build_type":
        return [Op("POST" if state.pages is None else "PUT", f"repos/{slug}/pages", {"build_type": value})]
    if name == "repository.has_issues":
        return [Op("PATCH", f"repos/{slug}", {"has_issues": value})]
    if name == "security.vulnerability_alerts":
        return [Op("PUT", f"repos/{slug}/vulnerability-alerts")]
    if name == "security.private_vulnerability_reporting":
        return [Op("PUT", f"repos/{slug}/private-vulnerability-reporting")]
    if name == "security.dependabot_security_updates":
        return [Op("PUT", f"repos/{slug}/automated-security-fixes")]
    if name.startswith("security."):
        return [Op("PATCH", f"repos/{slug}", {"security_and_analysis": {name.split(".", 1)[1]: {"status": "enabled"}}})]
    return []


# What the command proposes


@dataclass
class Finding:
    """One line of the plan: what is missing or different, which verb deals
    with it, and why the setting matters."""

    verb: str  # apply, secrets, prune, person or note
    level: str
    text: str
    why: str = ""
    url: str = ""
    ops: list = field(default_factory=list)
    stage: int = STAGE_VARIABLE
    tag: str = ""


@dataclass
class Switch:
    entry: dict
    on: bool
    value: str
    unmet: list  # (text, the ops enable makes to meet it or None, who meets it)
    conflict: str = ""


@dataclass
class Options:
    roles: list = field(default_factory=list)
    reviewers: list = field(default_factory=list)
    agent: str | None = None


def refs_text(branches: list, tags: list) -> str:
    return " and ".join(list(branches) + [f"tags {t}" for t in tags]) or "no branch"


def entry_key(entry: dict) -> tuple:
    return (entry["kind"], entry.get("named_by") or entry["name"], entry.get("environment"))


def merge(entries: list) -> list:
    """One entry per setting: the union of what several catalogues, or
    several workflows, ask of it, at the strictest level any asks."""
    merged: dict = {}
    for entry in entries:
        key = entry_key(entry)
        if key not in merged:
            merged[key] = dict(entry, workflows=list(entry.get("workflows", [])))
            if entry.get("reviewers"):
                merged[key]["reviewers_level"] = entry["level"]
            continue
        into = merged[key]
        into["workflows"] = sorted(set(into["workflows"]) | set(entry.get("workflows", [])))
        if RANK[entry["level"]] < RANK[into["level"]]:
            into["level"] = entry["level"]
        for listed in ("branches", "tags", "rules", "include"):
            if listed in entry:
                into[listed] = list(dict.fromkeys(list(into.get(listed, [])) + list(entry[listed])))
        if "reviewers" in entry:
            into["reviewers"] = max(into.get("reviewers", 0), entry["reviewers"])
        if entry.get("reviewers"):
            # A reviewer keeps the level of the entries that ask for one, so
            # a required Environment does not make a recommended reviewer
            # required too.
            was = into.get("reviewers_level", "optional")
            into["reviewers_level"] = entry["level"] if RANK[entry["level"]] < RANK[was] else was
    return list(merged.values())


class Planner:
    """Compares the catalogues with one repository, and says what each verb would do."""

    def __init__(self, repo: Repository, state: State, catalogues: list, options: Options):
        self.repo = repo
        self.state = state
        self.catalogues = catalogues
        self.options = options
        self.role_workflows = set()
        for wanted in options.roles:
            self.role_workflows |= self.role(wanted)
        self.present = set(repo.workflows) | self.role_workflows
        self.reads = {name: names_read(text) for name, text in repo.workflows.items()}
        self.read_anywhere = set().union(*self.reads.values())
        self.job_level = set().union(*(job_level_reads(text) for text in repo.workflows.values()))
        self.entries = merge([e for e in self.all_entries() if self.applies(e)])
        self.findings: list = []
        self.switches: list = []

    # Which entries apply here

    def all_entries(self) -> list:
        return [entry for catalogue in self.catalogues for entry in catalogue.entries]

    def role(self, name: str) -> set:
        for catalogue in self.catalogues:
            if name in catalogue.roles:
                role = catalogue.roles[name]
                found = set(role.get("workflows", []))
                for other in role.get("with", []):
                    found |= self.role(other)
                return found
        known = sorted({r for c in self.catalogues for r in c.roles})
        raise GhError(f"no role named {name}; the catalogues know {', '.join(known)}")

    def roles_present(self) -> list:
        found = []
        for catalogue in self.catalogues:
            for name, role in catalogue.roles.items():
                if set(role.get("workflows", [])) & self.present:
                    found.append(role.get("title", name))
        return list(dict.fromkeys(found))

    def applies(self, entry: dict) -> bool:
        workflows = entry.get("workflows")
        if not workflows:
            return True
        here = [w for w in workflows if w in self.present]
        if not here:
            return False
        if any(w not in self.repo.workflows for w in here):
            return True
        texts = [self.repo.workflows[w] for w in here]
        kind = entry["kind"]
        if kind in ("variable", "secret") and not entry.get("names_from"):
            # A copy of a workflow older than the name reads none of it, so
            # the catalogue follows the copy the repository holds.
            return any((kind, entry["name"]) in names_read(text) for text in texts)
        if kind == "environment":
            if entry.get("named_by"):
                return any(("variable", entry["named_by"]) in names_read(text) for text in texts)
            return any(names_environment(text, entry["name"]) for text in texts)
        return True

    def entries_of(self, kind: str) -> list:
        return [e for e in self.entries if e["kind"] == kind]

    # The whole plan

    def run(self) -> Planner:
        if not self.state.admin:
            self.add("note", "optional", f"Your gh login is not an admin of {self.repo.slug}, so some settings cannot be read, and changes would fail")
        if self.state.info.get("archived"):
            self.add("note", "optional", f"{self.repo.slug} is archived, and GitHub refuses every change to it")
        self.environments()
        self.variables()
        self.secrets()
        self.settings()
        self.rulesets()
        self.switch_states()
        self.presets()
        self.retired()
        self.stray()
        if self.state.unreadable:
            self.add("note", "optional", "Could not read " + ", ".join(sorted(set(self.state.unreadable))))
        return self

    def add(self, verb: str, level: str, text: str, entry: dict | None = None, ops: list | None = None, stage: int = STAGE_VARIABLE, why: str = "", url: str = "", tag: str = "") -> None:
        why = why or (entry or {}).get("why", "")
        url = url or (entry or {}).get("url", "")
        self.findings.append(Finding(verb, level, text, why, url, ops or [], stage, tag))

    # Environments

    def wanted_reviewers(self) -> list:
        """The people apply adds where a reviewer is required: those
        --reviewer names, or else the person running the command."""
        logins = self.options.reviewers or [self.state.user.get("login")]
        people = []
        for login in logins:
            user = self.state.get(f"users/{login}") if login else None
            if not user:
                raise GhError(f"no GitHub user {login!r} to add as a reviewer")
            people.append({"type": "User", "id": user["id"], "login": user["login"]})
        return people

    def env_body(self, env: dict | None, policy: object = "keep", add: list | None = None) -> dict:
        """The whole state an Environment should have after a change, so a
        PUT that means only to add a reviewer cannot drop another rule."""
        reviewers, prevent, wait = [], False, 0
        for rule in (env or {}).get("protection_rules", []):
            if rule.get("type") == "required_reviewers":
                prevent = bool(rule.get("prevent_self_review"))
                for r in rule.get("reviewers", []):
                    reviewers.append({"type": r.get("type", "User"), "id": (r.get("reviewer") or {}).get("id")})
            elif rule.get("type") == "wait_timer":
                wait = rule.get("wait_timer", 0)
        for person in add or []:
            if {"type": person["type"], "id": person["id"]} not in reviewers:
                reviewers.append({"type": person["type"], "id": person["id"]})
        body: dict = {}
        if reviewers:
            body["reviewers"] = reviewers
            body["prevent_self_review"] = prevent
        if wait:
            body["wait_timer"] = wait
        body["deployment_branch_policy"] = (env or {}).get("deployment_branch_policy") if policy == "keep" else policy
        return body

    def environments(self) -> None:
        for entry in self.entries_of("environment"):
            name = self.state.variables.get(entry["named_by"]) if entry.get("named_by") else entry["name"]
            if name:
                self.environment(entry, name)

    def environment(self, entry: dict, name: str) -> list:
        """Add the findings for one Environment, and return the calls that
        make it so, which enable also makes for an Environment a switch names."""
        level = entry["level"]
        branches = [b.replace("{default}", self.state.default_branch) for b in entry.get("branches", [])]
        tags = list(entry.get("tags", []))
        need = entry.get("reviewers") or 0
        reviewer_level = entry.get("reviewers_level", entry["level"])
        if reviewer_level == "optional":
            reviewer_level = "recommended"
        path = f"repos/{self.repo.slug}/environments/{name}"
        if not self.state.environments_available:
            self.add("note", level, f"Environment {name}: a private repository on GitHub Free has none, so a secret stays a repository secret, which a workflow on any branch can read", entry)
            return []
        env = self.state.environments.get(name)
        if level == "optional":
            # An optional Environment is never created, but one that exists
            # is held to its entry, as a recommendation.
            if env is None:
                return []
            level = "recommended"
        made = []
        custom = {"protected_branches": False, "custom_branch_policies": True}
        rules = [Op("POST", f"{path}/deployment-branch-policies", {"name": b, "type": "branch"}) for b in branches]
        rules += [Op("POST", f"{path}/deployment-branch-policies", {"name": t, "type": "tag"}) for t in tags]
        if env is None:
            add = self.wanted_reviewers() if need and self.state.reviewers_available and reviewer_level == level else []
            made = [Op("PUT", path, self.env_body(None, custom if rules else None, add)), *rules]
            limited = f", limited to {refs_text(branches, tags)}" if rules else ""
            who = f", with {', '.join(p['login'] for p in add)} as required reviewer" if add else ""
            self.add("apply", level, f"Environment {name}: create it{limited}{who}", entry, made, STAGE_ENVIRONMENT)
            return made
        policy = env.get("deployment_branch_policy")
        if rules and (policy is None or policy.get("protected_branches")):
            was = "every branch" if policy is None else "protected branches only, which counts no ruleset"
            ops = [Op("PUT", path, self.env_body(env, custom)), *rules]
            self.add("apply", level, f"Environment {name}: limit it to {refs_text(branches, tags)}; it admits {was} now", entry, ops, STAGE_RULES)
            made += ops
        elif rules:
            have = self.state.branch_policies(name)
            wanted = [("branch", b) for b in branches] + [("tag", t) for t in tags]
            missing = [w for w in wanted if w not in have]
            if missing:
                ops = [Op("POST", f"{path}/deployment-branch-policies", {"name": n, "type": t}) for t, n in missing]
                shown = refs_text([n for t, n in missing if t == "branch"], [n for t, n in missing if t == "tag"])
                self.add("apply", level, f"Environment {name}: admit {shown} too", entry, ops, STAGE_RULES)
                made += ops
            extra = [h for h in have if h not in wanted]
            if extra:
                shown = refs_text([n for t, n in extra if t == "branch"], [n for t, n in extra if t == "tag"])
                self.add("person", "recommended", f"Environment {name} also admits {shown}, which no catalogue names, so a job on those refs can read its secrets", entry)
        reviewers = [r for rule in env.get("protection_rules", []) if rule.get("type") == "required_reviewers" for r in rule.get("reviewers", [])]
        if need and len(reviewers) < need:
            if not self.state.reviewers_available:
                self.add("note", level, f"Environment {name}: a private repository needs GitHub Enterprise for required reviewers", entry)
            else:
                add = self.wanted_reviewers()
                ops = [Op("PUT", path, self.env_body(env, "keep", add))]
                self.add("apply", reviewer_level, f"Environment {name}: add {', '.join(p['login'] for p in add)} as required reviewer", entry, ops, STAGE_RULES)
                made += ops
        elif "reviewers" in entry and not need and reviewers:
            self.add("person", "optional", f"Environment {name} has {len(reviewers)} required reviewer(s), so each of its runs waits for one", entry)
        return made

    # Variables

    def variables(self) -> None:
        for entry in self.entries_of("variable"):
            value = self.state.variables.get(entry["name"])
            if value is not None:
                self.check_value(entry, value)
            self.environment_copies(entry, value)

    def check_value(self, entry: dict, value: str) -> None:
        name = entry["name"]
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            self.add("person", "required", f"Variable {name} is {value}: GitHub keeps the quotes as part of the value, so set it again without them", entry)
            return
        pattern = entry.get("pattern")
        if pattern and value and not re.fullmatch(pattern, value):
            self.add("person", "required", f"Variable {name} is {value!r}, which its workflow refuses", entry)
        if entry.get("check") == "repositories":
            self.check_repositories(entry, value)

    def check_repositories(self, entry: dict, value: str) -> None:
        """Each owner/name a list holds should be a repository under that
        name today. GitHub redirects a renamed one for a while, so a stale
        name works until the old name is taken."""
        name = entry["name"]
        if value.strip().lower() in NO_REPOSITORIES:
            return
        current, renamed = [], False
        for word in value.split():
            info = self.state.get(f"repos/{word}", soft=True)
            if not info:
                self.add("person", "recommended", f"Variable {name} names {word}, which your gh login cannot find", entry)
                current.append(word)
            elif info.get("full_name", word).lower() != word.lower():
                self.add("note", "recommended", f"Variable {name} names {word}, which is now {info['full_name']}", entry)
                current.append(info["full_name"])
                renamed = True
            else:
                current.append(word)
        if renamed:
            body = {"name": name, "value": " ".join(current)}
            op = Op("PATCH", f"repos/{self.repo.slug}/actions/variables/{name}", body)
            self.add("apply", "recommended", f"Variable {name}: write each renamed repository's current name", entry, [op])

    def environment_copies(self, entry: dict, value: str | None) -> None:
        """A catalogue variable set on an Environment. Every one belongs on
        the repository, and one a job's `if:` reads has no effect anywhere else."""
        name = entry["name"]
        job_level = entry.get("job_level") or name in self.job_level
        copies = {env: self.state.env_variables(env)[name] for env in sorted(self.state.environments) if name in self.state.env_variables(env)}
        for env, copy in copies.items():
            delete = Op("DELETE", f"repos/{self.repo.slug}/environments/{env}/variables/{name}")
            if job_level:
                self.add("prune", "recommended", f"Variable {name} on Environment {env}: remove it; a job's condition never reads it there", entry, [delete])
            elif value == copy:
                self.add("prune", "recommended", f"Variable {name} on Environment {env}: remove it; the repository variable holds the same value", entry, [delete])
            elif value is None and len(set(copies.values())) == 1:
                move = Op("POST", f"repos/{self.repo.slug}/actions/variables", {"name": name, "value": copy})
                self.add("prune", "recommended", f"Variable {name}: move it from Environment {env} to the repository", entry, [move, delete])
                value = copy
            else:
                self.add("person", "recommended", f"Variable {name} on Environment {env} holds another value than the repository's; keep one, on the repository", entry)

    # Secrets

    def ingest_names(self) -> list:
        """The secret names .lokf/ingest.yaml asks for. The ingest workflow hands over those and no other."""
        text = self.repo.read_file(".lokf/ingest.yaml") or ""
        lines = [line.split("#", 1)[0] for line in text.splitlines()]
        return sorted(set(re.findall(r"\bKNOWLEDGE_INGEST_[A-Z0-9_]+\b", "\n".join(lines))))

    def secret_entries(self) -> list:
        found = []
        for entry in self.entries_of("secret"):
            if entry.get("names_from") == "ingest":
                found += [dict(entry, name=name) for name in self.ingest_names()]
            else:
                found.append(entry)
        return found

    def secret_target(self, environment: str | None) -> str | None:
        return environment if environment and self.state.environments_available else None

    def has_secret(self, name: str, environment: str | None) -> bool:
        if environment:
            return environment in self.state.environments and name in self.state.env_secrets(environment)
        return name in self.state.secrets

    def needed(self, entry: dict) -> bool:
        return not (entry.get("unless") and self.met(entry["unless"]))

    def secrets(self) -> None:
        by_name: dict = {}
        for entry in self.secret_entries():
            by_name.setdefault(entry["name"], []).append(entry)
        for name, group in sorted(by_name.items()):
            copy = name in self.state.secrets
            moving = copy and all(self.secret_target(e.get("environment")) and not e.get("repository_copy") for e in group)
            for entry in group:
                target = self.secret_target(entry.get("environment"))
                where = f"Environment {target}" if target else "the repository"
                if self.has_secret(name, target):
                    continue
                if moving:
                    self.add("secrets", "required", f"Secret {name}: set it in {where}; ktl gh prune then removes the repository copy, which a workflow on any branch can read", entry)
                elif entry["level"] != "optional" and self.needed(entry):
                    self.add("secrets", entry["level"], f"Secret {name} in {where}: not set", entry)
            if moving and all(self.has_secret(name, self.secret_target(e.get("environment"))) for e in group):
                op = Op("DELETE", f"repos/{self.repo.slug}/actions/secrets/{name}")
                places = ", ".join(sorted({e["environment"] for e in group}))
                self.add("prune", "required", f"Secret {name}: remove the repository copy; Environment {places} holds it, and a workflow on any branch can read a repository secret", group[0], [op])

    # Repository settings

    def settings(self) -> None:
        for entry in self.entries_of("setting"):
            name, want, level = entry["name"], entry.get("value"), entry["level"]
            if entry.get("visibility") and self.state.visibility not in entry["visibility"]:
                continue
            label = name.split(".", 1)[1].replace("_", " ")
            if name == "actions.sha_pinning_required" and want:
                loose = sorted({f"{ref} in {wf}" for wf, text in self.repo.workflows.items() for ref in unpinned_actions(text)})
                if loose and self.state.setting(name) is not True:
                    shown = ", ".join(loose[:3]) + (f" and {len(loose) - 3} more" if len(loose) > 3 else "")
                    self.add("note", level, f"Requiring actions pinned to a commit would stop {shown}; pin them first", entry)
                    continue
            have = self.state.setting(name)
            if have is None or have == want:
                continue
            if entry.get("report_only"):
                self.add("person", level, f"Setting {label} is {have}, not {want}", entry)
                continue
            shown = want if isinstance(want, str) else json.dumps(want)
            stage = STAGE_SETTING + SETTINGS.index(name)
            self.add("apply", level, f"Setting {label}: set it to {shown}", entry, setting_ops(self.state, name, want), stage)

    # Rulesets

    def covers(self, ruleset: dict, entry: dict) -> bool:
        """Whether an active ruleset applies to every ref an entry names."""
        if ruleset.get("enforcement") != "active" or ruleset.get("target", "branch") != entry.get("target", "branch"):
            return False
        refs = (ruleset.get("conditions") or {}).get("ref_name") or {}
        include, exclude = refs.get("include", []), refs.get("exclude", [])
        for wanted in entry.get("include", []):
            literal = f"refs/heads/{self.state.default_branch}" if wanted == "~DEFAULT_BRANCH" else wanted
            if wanted in exclude or literal in exclude:
                return False
            if not any(i in (wanted, "~ALL") or fnmatch.fnmatchcase(literal, i) for i in include):
                return False
        return True

    def rulesets(self) -> None:
        for entry in self.entries_of("ruleset"):
            name, level = entry["name"], entry["level"]
            if self.state.visibility != "public" and self.state.plan_name == "free":
                self.add("note", level, f"Ruleset {name}: a private repository on GitHub Free has no rulesets", entry)
                continue
            covering = [r for r in self.state.rulesets if self.covers(r, entry)]
            have = {rule.get("type") for r in covering for rule in r.get("rules", [])}
            missing = [t for t in entry.get("rules", []) if t not in have]
            for r in covering:
                if r.get("bypass_actors"):
                    self.add("person", "optional", f"Ruleset {r.get('name')} lets {len(r['bypass_actors'])} actor(s) bypass it", entry)
            if not missing:
                continue
            own = [r for r in self.state.rulesets if r.get("name") == name and r.get("source_type", "Repository") == "Repository"]
            if own and own[0].get("enforcement") != "active":
                self.add("person", level, f"Ruleset {name} is {own[0].get('enforcement')}, so it blocks nothing; it should block {', '.join(missing)}", entry)
                continue
            if own:
                body = {k: own[0][k] for k in ("name", "target", "enforcement", "conditions", "bypass_actors") if k in own[0]}
                body["rules"] = list(own[0].get("rules", [])) + [{"type": t} for t in missing]
                op = Op("PUT", f"repos/{self.repo.slug}/rulesets/{own[0]['id']}", body)
                self.add("apply", level, f"Ruleset {name}: add {', '.join(missing)}", entry, [op], STAGE_RULESET)
            else:
                body = {
                    "name": name,
                    "target": entry.get("target", "branch"),
                    "enforcement": "active",
                    "conditions": {"ref_name": {"include": list(entry.get("include", [])), "exclude": []}},
                    "rules": [{"type": t} for t in missing],
                    "bypass_actors": [],
                }
                op = Op("POST", f"repos/{self.repo.slug}/rulesets", body)
                refs = ", ".join(entry.get("include", [])).replace("~DEFAULT_BRANCH", "the default branch")
                self.add("apply", level, f"Ruleset {name}: create it for {refs}, blocking {', '.join(missing)}", entry, [op], STAGE_RULESET)

    # Switches

    def met(self, req: dict) -> bool:
        if "any" in req:
            return any(self.met(sub) for sub in req["any"])
        if "variable" in req:
            value = self.state.variables.get(req["variable"])
            return bool(value) and ("equals" not in req or same(value, req["equals"]))
        if "unset" in req:
            return self.state.variables.get(req["unset"], "").lower() in ("", "false")
        if "secret" in req:
            return self.has_secret(req["secret"], self.secret_target(req.get("environment")))
        if "setting" in req:
            return self.state.setting(req["setting"]) == req.get("value", True)
        if "pages" in req:
            return self.state.setting("pages.build_type") == req["pages"]
        if "without" in req:
            return req["without"] not in self.present
        if "without_publishers" in req:
            return not self.other_publishers()
        if "file" in req:
            return self.repo.read_file(req["file"]) is not None
        if "secrets_from" in req:
            target = self.secret_target(req.get("environment"))
            return all(self.has_secret(name, target) for name in self.ingest_names())
        if "visibility" in req:
            return self.state.visibility in req["visibility"]
        return "confirm" not in req

    def other_publishers(self) -> list:
        """Whatever else publishes this repository's Pages site, which would overwrite the knowledge site."""
        found = []
        for name, text in sorted(self.repo.workflows.items()):
            hits = [p for p in PUBLISHERS if mentions(text, p)]
            if hits and name not in KTL_PUBLISHERS:
                found.append(f"{name} ({', '.join(hits)})")
        if self.repo.read_file("CNAME") is not None:
            found.append("a CNAME file")
        mkdocs = self.repo.read_file("mkdocs.yml")
        if mkdocs and re.search(r"^site_url:", mkdocs, re.M):
            found.append("mkdocs.yml, which names a site_url")
        return found

    def unmet(self, req: dict) -> tuple:
        """What a requirement that does not hold needs: (text, the calls
        enable makes to meet it or None, who meets it otherwise)."""
        text = req.get("text") or json.dumps(req)
        if "confirm" in req:
            return (req["confirm"], None, "confirm")
        if "setting" in req:
            return (text, setting_ops(self.state, req["setting"], req.get("value", True)), "enable")
        if "pages" in req:
            if self.state.pages is None:
                return (text, setting_ops(self.state, "pages.build_type", req["pages"]), "enable")
            branch = (self.state.pages.get("source") or {}).get("branch", "a branch")
            return (f"Pages builds from {branch}: retire that publisher, then switch Pages to GitHub Actions", None, "person")
        if "without_publishers" in req:
            return (f"{text}: {', '.join(self.other_publishers())}", None, "person")
        if "secret" in req or "secrets_from" in req:
            return (text, None, "ktl gh secrets")
        if "any" in req:
            return (text, None, "ktl gh apply --agent, or ktl gh secrets")
        if "variable" in req and req["variable"].startswith("AGENT_"):
            return (text, None, "ktl gh apply --agent")
        return (text, None, "a person")

    def evaluate(self, entry: dict) -> Switch:
        switch = entry["switch"]
        value = self.state.variables.get(entry["name"], "")
        on = bool(value) if switch.get("environment") else any(same(value, v) for v in switch.get("values", ["true"]))
        unmet, conflict = [], ""
        for req in switch.get("requires", []):
            if "without" in req and req["without"] in self.present:
                conflict = req.get("text") or f"{req['without']} is here"
            elif not self.met(req):
                unmet.append(self.unmet(req))
        return Switch(entry, on, value, unmet, conflict)

    def switch_states(self) -> None:
        for entry in [e for e in self.entries_of("variable") if e.get("switch")]:
            sw = self.evaluate(entry)
            self.switches.append(sw)
            label = f"Switch {entry['switch']['name']} ({entry['name']})"
            if sw.on and sw.conflict:
                self.add("person", "required", f"{label} is on, but should be off: {sw.conflict}", entry)
            if not sw.on:
                continue
            for text, fix, who in sw.unmet:
                if who == "confirm":
                    continue
                if fix:
                    self.add("apply", "required", f"{label} is on, and needs this: {text}", entry, fix, STAGE_SETTING)
                else:
                    verb = "secrets" if who == "ktl gh secrets" else "person"
                    self.add(verb, "required", f"{label} is on, and needs this: {text}", entry)

    def named_environment(self, variable: str) -> dict | None:
        """The catalogue's entry for the Environment whose name a variable holds."""
        for entry in self.all_entries():
            if entry["kind"] == "environment" and entry.get("named_by") == variable:
                return dict(entry, level="required")
        return None

    # Presets, such as the agent the librarian runs

    def preset(self, name: str) -> dict:
        for catalogue in self.catalogues:
            if name in catalogue.presets:
                return catalogue.presets[name]
        known = sorted({p for c in self.catalogues for p in c.presets})
        raise GhError(f"no preset named {name}; the catalogues know {', '.join(known)}")

    def presets(self) -> None:
        """The values a preset sets: the one --agent names, or the one a
        catalogue gives a workflow here when AGENT_CLI is unset, such as the
        members script a domain host runs."""
        chosen, asked = self.options.agent, bool(self.options.agent)
        if not chosen and "AGENT_CLI" not in self.state.variables:
            for catalogue in self.catalogues:
                for name, preset in catalogue.presets.items():
                    if preset.get("default_for") in self.present:
                        chosen = name
        if not chosen:
            return
        preset = self.preset(chosen)
        title = preset.get("title", chosen)
        level = "required" if asked else "recommended"
        path = f"repos/{self.repo.slug}/actions/variables"
        for var, want in preset.get("variables", {}).items():
            have = self.state.variables.get(var)
            if want is None and have is not None and asked:
                self.add("apply", level, f"Variable {var}: remove it; {title} needs it unset", ops=[Op("DELETE", f"{path}/{var}")], why=f"for {title}", url=preset.get("url", ""))
            elif want is not None and have is None:
                self.add("apply", level, f"Variable {var}: set it to {want}", ops=[Op("POST", path, {"name": var, "value": want})], why=f"for {title}", url=preset.get("url", ""))
            elif want is not None and have != want and asked:
                self.add("apply", level, f"Variable {var}: change it from {have} to {want}", ops=[Op("PATCH", f"{path}/{var}", {"name": var, "value": want})], why=f"for {title}", url=preset.get("url", ""))

    # Retired names

    def retired(self) -> None:
        for catalogue in self.catalogues:
            for old in catalogue.retired:
                self.retired_name(old)

    def retired_name(self, old: dict) -> None:
        kind, name = old["kind"], old["name"]
        where = []
        if kind == "variable":
            if name in self.state.variables:
                where.append(("the repository", f"repos/{self.repo.slug}/actions/variables/{name}"))
            where += [(f"Environment {env}", f"repos/{self.repo.slug}/environments/{env}/variables/{name}") for env in sorted(self.state.environments) if name in self.state.env_variables(env)]
        else:
            if name in self.state.secrets:
                where.append(("the repository", f"repos/{self.repo.slug}/actions/secrets/{name}"))
            where += [(f"Environment {env}", f"repos/{self.repo.slug}/environments/{env}/secrets/{name}") for env in sorted(self.state.environments) if name in self.state.env_secrets(env)]
        replaced = f", replaced by {old['replaced_by']}" if old.get("replaced_by") else ""
        since = f" (CHANGELOG {old['changelog']})" if old.get("changelog") else ""
        readers = sorted(wf for wf, found in self.reads.items() if (kind, name) in found)
        for place, path in where:
            text = f"{kind.capitalize()} {name} in {place}: retired{replaced}{since}"
            if readers:
                self.add("person", "recommended", f"{text}, but {', '.join(readers)} still reads it; sync that workflow first", why=old.get("why", ""), tag="retired")
            else:
                self.add("prune", "recommended", text, ops=[Op("DELETE", path)], why=old.get("why", ""), tag="retired")

    # What no catalogue describes

    def stray(self) -> None:
        catalogued = {(e["kind"], e["name"]) for e in self.all_entries() if e["kind"] in ("variable", "secret")}
        retired = {(o["kind"], o["name"]) for c in self.catalogues for o in c.retired}
        prefixes = [e["name"].rstrip("*_") for e in self.all_entries() if e.get("names_from")]
        for wf, found in sorted(self.reads.items()):
            for kind, name in sorted(found):
                if (kind, name) in catalogued or (kind, name) in retired or any(p and name.startswith(p) for p in prefixes):
                    continue
                self.add("note", "optional", f"{wf} reads {'vars' if kind == 'variable' else 'secrets'}.{name}, which no catalogue describes")
        for name in sorted(self.state.variables):
            if ("variable", name) not in self.read_anywhere and ("variable", name) not in retired:
                self.add("note", "optional", f"Variable {name} is read by no workflow here; remove it by hand if nothing else uses it")
        for name in sorted(self.state.secrets):
            covered = any(p and name.startswith(p) for p in prefixes)
            if ("secret", name) not in self.read_anywhere and ("secret", name) not in retired and not covered:
                self.add("note", "optional", f"Secret {name} is read by no workflow here, and a workflow on any branch could read it; remove it by hand if nothing else uses it")
        # A variable on an Environment that a job's condition reads, which
        # no catalogue describes: GitHub never reads it there.
        handled = {e["name"] for e in self.entries_of("variable")}
        for env in sorted(self.state.environments):
            for name in sorted(self.state.env_variables(env)):
                if name in self.job_level and name not in handled and ("variable", name) not in retired:
                    op = Op("DELETE", f"repos/{self.repo.slug}/environments/{env}/variables/{name}")
                    self.add("prune", "recommended", f"Variable {name} on Environment {env}: remove it; a job's condition reads it, and never there", ops=[op], why="A job's if: reads repository and organisation variables only; set it on the repository instead.")
        catalogued_envs = {e.get("named_by") or e["name"] for e in self.all_entries() if e["kind"] == "environment"}
        for wf, text in sorted(self.repo.workflows.items()):
            for env in sorted(literal_environments(text)):
                if env not in catalogued_envs and self.state.environments_available and env not in self.state.environments:
                    self.add("person", "recommended", f"Environment {env}, which {wf} names, does not exist, so a run would create it with no rules; describe it in {OWN_CATALOGUE}")


# Output


def section(findings: list, verb: str, levels: tuple) -> list:
    return sorted([f for f in findings if f.verb == verb and f.level in levels], key=lambda f: (f.stage, f.text))


def failures(planner: Planner, strict: bool) -> list:
    levels = ("required", "recommended") if strict else ("required",)
    return [f for f in planner.findings if f.verb in ("apply", "secrets", "prune", "person") and f.level in levels]


def render(planner: Planner, strict: bool = False) -> None:
    state, repo = planner.state, planner.repo
    print(f"{repo.slug}: {state.visibility}, default branch {state.default_branch}")
    print(f"Workflows, from {repo.where}: {', '.join(sorted(repo.workflows)) or 'none'}")
    if planner.role_workflows - set(repo.workflows):
        print(f"Treated as present: {', '.join(sorted(planner.role_workflows - set(repo.workflows)))}")
    roles = planner.roles_present()
    if roles:
        print(f"Roles: {', '.join(roles)}")
    print(f"Catalogues: {', '.join(c.path for c in planner.catalogues)}")
    for title, verb, levels in (
        ("To apply, with ktl gh apply", "apply", ("required",)),
        ("Recommended, with ktl gh apply --recommended", "apply", ("recommended", "optional")),
        ("Secrets, with ktl gh secrets", "secrets", LEVELS),
        ("To remove, with ktl gh prune", "prune", LEVELS),
        ("For a person to decide", "person", LEVELS),
        ("Notes", "note", LEVELS),
    ):
        items = section(planner.findings, verb, levels)
        if not items:
            continue
        print(f"\n{title}")
        for f in items:
            print(f"  {f.text}")
            reason = " ".join(x for x in (f.why, f"<{f.url}>" if f.url else "") if x)
            if reason:
                print(f"      {reason}")
    if planner.switches:
        print("\nSwitches, with ktl gh enable NAME")
        for sw in sorted(planner.switches, key=lambda s: s.entry["switch"]["name"]):
            names_env = sw.entry["switch"].get("environment")
            detail = f", naming {sw.value}" if sw.on and names_env else ""
            print(f"  {sw.entry['switch']['name']:<14} {'on' if sw.on else 'off':<4} {sw.entry['name']}{detail}")
            if sw.on:
                continue
            if sw.conflict:
                print(f"      leave it off: {sw.conflict}")
                continue
            if names_env:
                print(f"      enable names {names_env}, once that Environment has a required reviewer, which it adds")
            for text, fix, who in sw.unmet:
                if who == "confirm":
                    print(f"      enable asks you to confirm that {text}")
                elif fix:
                    print(f"      enable also sets: {text}")
                else:
                    print(f"      needs first, from {who}: {text}")
    gaps = failures(planner, strict)
    kind = "required or recommended" if strict else "required"
    print(f"\n{len(gaps)} {kind} item(s) to deal with." if gaps else f"\nNothing {kind} is missing.")


def as_json(planner: Planner) -> dict:
    return {
        "repository": planner.repo.slug,
        "visibility": planner.state.visibility,
        "default_branch": planner.state.default_branch,
        "workflows": sorted(planner.repo.workflows),
        "roles": planner.roles_present(),
        "findings": [
            {"verb": f.verb, "level": f.level, "text": f.text, "why": f.why, "docs": f.url, "calls": [f"{o.method} {o.path}" for o in f.ops]}
            for f in planner.findings
        ],
        "switches": [
            {"name": s.entry["switch"]["name"], "variable": s.entry["name"], "on": s.on, "conflict": s.conflict, "needs": [t for t, _, _ in s.unmet]}
            for s in planner.switches
        ],
    }


# The verbs


def confirm(question: str, yes: bool) -> bool:
    if yes:
        return True
    if not sys.stdin.isatty():
        print(f"{question} No terminal to ask on, so nothing was changed; add --yes to go ahead.", file=sys.stderr)
        return False
    return input(f"{question} [y/N] ").strip().lower() in ("y", "yes")


def make(github: GitHub, items: list) -> int:
    for finding in items:
        for op in finding.ops:
            try:
                op.run(github)
            except GhError as error:
                print(f"ktl gh: {error}", file=sys.stderr)
                print("Stopped there: what was printed as done is done. ktl gh plan shows what remains.", file=sys.stderr)
                return 1
        print(f"  done: {finding.text}")
    return 0


def catalogues_for(repo: Repository, extra: list) -> list:
    found = [load_catalogue(path.read_text(encoding="utf-8"), f"{path.parent.parent.name} ({CATALOGUE})") for path in package_catalogues()]
    own = repo.read_file(OWN_CATALOGUE)
    if own is not None:
        found.append(load_catalogue(own, OWN_CATALOGUE))
    for name in repo.list_dir(OWN_CATALOGUE_DIR):
        if name.endswith(".json"):
            text = repo.read_file(f"{OWN_CATALOGUE_DIR}/{name}")
            if text is not None:
                found.append(load_catalogue(text, f"{OWN_CATALOGUE_DIR}/{name}"))
    for path in extra:
        found.append(load_catalogue(Path(path).read_text(encoding="utf-8"), str(path)))
    return found


def planner_for(github: GitHub, slug: str | None, args: argparse.Namespace) -> Planner:
    repo = remote_repository(github, slug) if slug else local_repository(github)
    options = Options(
        roles=getattr(args, "role", None) or [],
        reviewers=getattr(args, "reviewer", None) or [],
        agent=getattr(args, "agent", None),
    )
    state = State(github, repo.slug)
    # GitHub redirects a renamed repository's old name for reads, and not
    # for every write, so every call after this one uses the current name.
    current, asked = state.info.get("full_name") or repo.slug, repo.slug
    repo.slug = state.slug = current
    planner = Planner(repo, state, catalogues_for(repo, getattr(args, "catalogue", None) or []), options)
    if current.lower() != asked.lower():
        planner.add("note", "optional", f"{asked} is now {current}, so the command acts on {current}")
    return planner.run()


def cmd_plan(github: GitHub, args: argparse.Namespace) -> int:
    for n, slug in enumerate(args.repo or [None]):
        planner = planner_for(github, slug, args)
        if args.json:
            print(json.dumps(as_json(planner), indent=2))
            continue
        if n:
            print("\n" + "-" * 72)
        render(planner)
    return 0


def cmd_check(github: GitHub, args: argparse.Namespace) -> int:
    worst = 0
    for slug in args.repo or [None]:
        planner = planner_for(github, slug, args)
        gaps = failures(planner, args.strict)
        kind = "required or recommended" if args.strict else "required"
        if not gaps:
            print(f"{planner.repo.slug}: nothing {kind} is missing")
            continue
        worst = 1
        print(f"{planner.repo.slug}: {len(gaps)} {kind} item(s) to deal with")
        for f in sorted(gaps, key=lambda f: (f.verb, f.stage, f.text)):
            print(f"  {f.verb:<8} {f.text}")
    return worst


def cmd_apply(github: GitHub, args: argparse.Namespace) -> int:
    planner = planner_for(github, args.repo, args)
    levels = ("required", "recommended", "optional") if args.recommended else ("required",)
    items = sorted([f for f in planner.findings if f.verb == "apply" and f.level in levels], key=lambda f: (f.stage, f.text))
    left = [f for f in planner.findings if f.verb == "apply" and f.level not in levels]
    if not items:
        print(f"{planner.repo.slug}: nothing to apply.")
    else:
        print(f"{planner.repo.slug}: {len(items)} change(s)")
        for f in items:
            print(f"  {f.text}")
        if not confirm(f"Make these {len(items)} change(s)?", args.yes):
            return 1
        if make(github, items):
            return 1
    if left:
        print(f"{len(left)} recommended change(s) left; ktl gh apply --recommended makes them too.")
    if args.with_secrets:
        return set_secrets(github, planner_for(github, args.repo, args), [], None)
    rest = [f for f in planner.findings if f.verb in ("secrets", "prune", "person") and f.level == "required"]
    if rest:
        print(f"{len(rest)} required item(s) are for ktl gh secrets, ktl gh prune or a person; ktl gh plan lists them.")
    return 0


def read_dotenv(text: str) -> dict:
    """NAME=value lines, as a .env file holds them: blank lines, comments
    and `export` are allowed, and one pair of quotes around a value is
    taken off."""
    values = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key.startswith("export "):
            key = key[len("export "):].strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        values[key] = value
    return values


def set_secrets(github: GitHub, planner: Planner, names: list, source: str | None) -> int:
    """Set each secret the workflows can read and lack, or each one named.

    A value comes from a prompt that does not echo, or, with no terminal,
    from standard input or the file --from names, as NAME=value lines. Each
    goes to gh on standard input.
    """
    wanted = []
    for entry in planner.secret_entries():
        name = entry["name"]
        target = planner.secret_target(entry.get("environment"))
        if names:
            if name in names:
                wanted.append((entry, target))
        elif planner.needed(entry) and not planner.has_secret(name, target):
            wanted.append((entry, target))
    unknown = [n for n in names if n not in {e["name"] for e, _ in wanted}]
    if unknown:
        print(f"ktl gh: no workflow here reads a secret named {', '.join(unknown)}", file=sys.stderr)
        return 2
    if not wanted:
        print(f"{planner.repo.slug}: every secret the workflows read is set.")
        return 0
    absent = sorted({t for _, t in wanted if t and t not in planner.state.environments})
    if absent:
        print(f"ktl gh: create the Environment {', '.join(absent)} first, with ktl gh apply, so that its branch rule holds before a secret is in it", file=sys.stderr)
        return 1
    supplied = None
    if source:
        supplied = read_dotenv(Path(source).read_text(encoding="utf-8"))
    elif not sys.stdin.isatty():
        supplied = read_dotenv(sys.stdin.read())
    done = 0
    for entry, target in wanted:
        name = entry["name"]
        where = f"Environment {target}" if target else "the repository"
        if supplied is not None:
            value = supplied.get(name, "")
        else:
            print(f"{name}, for {where}: {entry.get('why', '')}")
            value = getpass.getpass(f"{name} (empty to skip): ")
        if not value:
            print(f"  skipped: {name} in {where}")
            continue
        try:
            github.set_secret(planner.repo.slug, name, value, target)
        except GhError as error:
            print(f"ktl gh: {name}: {error}", file=sys.stderr)
            return 1
        done += 1
        print(f"  set: {name} in {where}")
    if any(e["name"] in planner.state.secrets for e, t in wanted if t):
        print("The repository copies a workflow on any branch can read are still there; ktl gh prune removes them.")
    return 0


def cmd_secrets(github: GitHub, args: argparse.Namespace) -> int:
    return set_secrets(github, planner_for(github, args.repo, args), args.names, args.from_file)


def list_switches(planner: Planner) -> None:
    if not planner.switches:
        print(f"{planner.repo.slug}: no workflow here has a switch.")
        return
    for sw in sorted(planner.switches, key=lambda s: s.entry["switch"]["name"]):
        print(f"{sw.entry['switch']['name']:<14} {'on' if sw.on else 'off':<4} {sw.entry['name']}")
        for text, fix, who in [] if sw.on else sw.unmet:
            print(f"    {'enable also sets' if fix else 'needs first, from ' + who}: {text}")


def cmd_enable(github: GitHub, args: argparse.Namespace) -> int:
    planner = planner_for(github, args.repo, args)
    if not args.switch:
        list_switches(planner)
        return 0
    found = [s for s in planner.switches if s.entry["switch"]["name"] == args.switch]
    if not found:
        known = [e for e in planner.all_entries() if e.get("switch") and e["switch"]["name"] == args.switch]
        if known:
            print(f"ktl gh: no workflow here reads {known[0]['name']}; install {' or '.join(known[0]['workflows'])} first", file=sys.stderr)
        else:
            names = sorted(s.entry["switch"]["name"] for s in planner.switches)
            print(f"ktl gh: no switch named {args.switch}; this repository has {', '.join(names) or 'none'}", file=sys.stderr)
        return 2
    sw = found[0]
    entry, switch = sw.entry, sw.entry["switch"]
    if sw.conflict:
        print(f"ktl gh: leave {args.switch} off: {sw.conflict}", file=sys.stderr)
        return 1
    blocking = [(text, who) for text, fix, who in sw.unmet if fix is None and who != "confirm"]
    if blocking:
        print(f"{args.switch} needs these first:")
        for text, who in blocking:
            print(f"  {text} ({who})")
        return 1
    values = switch.get("values", ["true"])
    value = args.value or switch.get("environment") or values[0]
    if not switch.get("environment") and not any(same(value, v) for v in values):
        print(f"ktl gh: {entry['name']} takes {' or '.join(values)}", file=sys.stderr)
        return 2
    ops, lines = [], []
    for text, fix, _ in sw.unmet:
        if fix:
            ops += fix
            lines.append(text)
    if switch.get("environment"):
        env_entry = planner.named_environment(entry["name"])
        if env_entry:
            before = len(planner.findings)
            ops += planner.environment(env_entry, value)
            lines += [f.text for f in planner.findings[before:] if f.verb == "apply"]
    if sw.value != value:
        path = f"repos/{planner.repo.slug}/actions/variables"
        body = {"name": entry["name"], "value": value}
        ops.append(Op("PATCH", f"{path}/{entry['name']}", body) if entry["name"] in planner.state.variables else Op("POST", path, body))
        lines.append(f"Variable {entry['name']}: set it to {value}")
    for text, _, who in sw.unmet:
        if who == "confirm" and not confirm(f"Confirm that {text}.", args.yes):
            return 1
    if not ops:
        print(f"{args.switch} is already on.")
    else:
        print(f"{planner.repo.slug}: to turn {args.switch} on")
        for line in lines:
            print(f"  {line}")
        if not confirm(f"Make these {len(lines)} change(s)?", args.yes):
            return 1
        if make(github, [Finding("apply", "required", f"{args.switch} is on", ops=ops)]):
            return 1
    run = switch.get("run")
    if not run:
        return 0
    if args.run:
        try:
            Op("POST", f"repos/{planner.repo.slug}/actions/workflows/{run}/dispatches", {"ref": planner.state.default_branch}).run(github)
        except GhError as error:
            print(f"ktl gh: {error}", file=sys.stderr)
            return 1
        print(f"Started {run}; read its log in the Actions tab.")
    else:
        print(f"Run it once by hand now, and read its log: gh workflow run {run} --repo {planner.repo.slug}")
    return 0


def cmd_prune(github: GitHub, args: argparse.Namespace) -> int:
    planner = planner_for(github, args.repo, args)
    for f in [f for f in planner.findings if f.verb == "person" and f.tag == "retired"]:
        print(f"  kept: {f.text}")
    items = sorted([f for f in planner.findings if f.verb == "prune"], key=lambda f: f.text)
    if not items:
        print(f"{planner.repo.slug}: nothing to remove.")
        return 0
    print(f"{planner.repo.slug}: {len(items)} removal(s)")
    for f in items:
        print(f"  {f.text}")
    if not confirm(f"Make these {len(items)} change(s)?", args.yes):
        return 1
    return make(github, items)


# The command line


def add_parser(groups: argparse._SubParsersAction) -> None:
    gh = groups.add_parser(
        "gh",
        help="the GitHub settings the repository's workflows need: plan, check, apply, secrets, enable, prune",
        description="Compare the GitHub settings the repository's workflows need, as the skills' catalogues "
        "describe them, with the repository's own, and set what is missing. Every call goes through the GitHub "
        "CLI with your own login. Run it in a clone of the repository, or name one with --repo.",
    )
    verbs = gh.add_subparsers(dest="verb", metavar="{plan,check,apply,secrets,enable,prune}")

    def common(p: argparse.ArgumentParser, many: bool = False) -> None:
        if many:
            p.add_argument("--repo", action="append", metavar="OWNER/NAME", help="read this repository's default branch on GitHub, not the clone you are in; repeat for more")
        else:
            p.add_argument("--repo", metavar="OWNER/NAME", help="act on this repository, reading its default branch on GitHub, not the clone you are in")
        p.add_argument("--role", action="append", metavar="ROLE", help="count a role's workflows as present, for a repository that does not carry them yet: bundle, domain, ingest or website")
        p.add_argument("--catalogue", action="append", metavar="FILE", help="read this catalogue too")

    plan = verbs.add_parser("plan", help="say what is missing, different or retired, and which verb deals with it; changes nothing")
    common(plan, many=True)
    plan.add_argument("--json", action="store_true", help="print the plan as JSON")

    check = verbs.add_parser("check", help="list what is missing and exit 1 when anything is; changes nothing")
    common(check, many=True)
    check.add_argument("--strict", action="store_true", help="count what is recommended too")

    apply = verbs.add_parser("apply", help="create the Environments, rules, settings and values that are missing")
    common(apply)
    apply.add_argument("--recommended", action="store_true", help="make the recommended changes too")
    apply.add_argument("--agent", metavar="PRESET", help="set the librarian's agent variables from a preset: copilot, claude-code or members")
    apply.add_argument("--reviewer", action="append", metavar="LOGIN", help="whom to add where a reviewer is required (default: you); repeat for more")
    apply.add_argument("--with-secrets", action="store_true", help="then set the secrets that are missing, as ktl gh secrets does")
    apply.add_argument("--yes", action="store_true", help="make the changes without asking")

    secrets = verbs.add_parser("secrets", help="set the secrets the workflows read, from a prompt that does not echo")
    common(secrets)
    secrets.add_argument("names", nargs="*", metavar="NAME", help="set these, even when they are set already (default: each one missing)")
    secrets.add_argument("--from", dest="from_file", metavar="FILE", help="read NAME=value lines from this file instead of asking")

    enable = verbs.add_parser("enable", help="turn one switch on once what it needs is in place; with no name, list the switches")
    common(enable)
    enable.add_argument("switch", nargs="?", metavar="SWITCH", help="the switch, such as librarian, release, website, ingest or federation")
    enable.add_argument("--value", help="the value to set, where the switch takes more than one")
    enable.add_argument("--reviewer", action="append", metavar="LOGIN", help="the reviewer of an Environment the switch names (default: you)")
    enable.add_argument("--run", action="store_true", help="start the workflow once by hand afterwards")
    enable.add_argument("--yes", action="store_true", help="make the changes, and confirm what GitHub cannot check, without asking")

    prune = verbs.add_parser("prune", help="remove retired variables and secrets, and copies no workflow here can read")
    common(prune)
    prune.add_argument("--yes", action="store_true", help="remove them without asking")
    gh.set_defaults(gh_help=gh.print_help)


def main(args: argparse.Namespace, github: GitHub | None = None) -> int:
    verbs = {
        "plan": cmd_plan,
        "check": cmd_check,
        "apply": cmd_apply,
        "secrets": cmd_secrets,
        "enable": cmd_enable,
        "prune": cmd_prune,
    }
    if getattr(args, "verb", None) not in verbs:
        args.gh_help()
        return 2
    try:
        return verbs[args.verb](github or GitHub(), args)
    except (GhError, CatalogueError) as error:
        print(f"ktl gh: {error}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\nktl gh: stopped; each change printed as done is done, and nothing after it", file=sys.stderr)
        return 130
