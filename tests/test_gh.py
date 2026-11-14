"""`ktl gh` against a GitHub that lives in memory, and its catalogues against the templates.

`ktl gh` sets a repository's GitHub settings from the catalogues the skills
carry (skills/*/references/repository-settings.json) and the repository's
own (.github/repository-settings.json). No test here reaches GitHub: each
runs the command against FakeGitHub, which keeps one repository's settings
in memory and answers each call as GitHub's REST API does, so a test can
apply a plan and read the result back.

The contract tests hold the catalogues to the files they describe:

- each catalogue keeps to the format, and every page and heading it links
  to exists;
- every variable and secret a template reads, and every Environment it
  names, has an entry, and every entry is read by a workflow it names;
- the switches table in ktl-sidecar's automation.md lists the same names;
- this repository's own workflows read nothing the catalogues leave out;
- a retired name is read by no template, and the changelog says so under
  the release the catalogue cites;
- the agent presets are the commands automation.md gives.

The behaviour tests say what each verb does: plan changes nothing; apply
creates and tightens, never loosens and never removes; prune removes only
retired names and copies a workflow cannot read; secrets passes each value
to gh on standard input; enable checks what a switch needs first.
"""

from __future__ import annotations

import base64
import copy
import io
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from conftest import REPO

sys.path.insert(0, str(REPO / "src"))

from ktl import cli, gh  # noqa: E402

SIDECAR = REPO / "skills" / "ktl-sidecar"
WEBSITE = REPO / "skills" / "ktl-website"
TEMPLATES = {p.name: p for p in sorted((SIDECAR / "templates" / "github").glob("*.yaml"))}
TEMPLATES["knowledge-website.yaml"] = WEBSITE / "templates" / "github" / "knowledge-website.yaml"
CATALOGUES = {"ktl-sidecar": SIDECAR / "references" / "repository-settings.json", "ktl-website": WEBSITE / "references" / "repository-settings.json"}
OWN = REPO / ".github" / "repository-settings.json"
BUNDLE = ["knowledge-librarian.yaml", "knowledge-registrar.yaml", "knowledge-release.yaml", "knowledge-sync.yaml"]


# A GitHub in memory


class FakeGitHub:
    """One repository's settings, and the answers GitHub's API gives about them.

    It starts hardened as the catalogues recommend, so a test sees only what
    it changes. Every call but a GET is kept in `changes`.
    """

    def __init__(self, slug="acme/host", visibility="public", plan="pro", owner_type="User", default_branch="main"):
        owner = slug.split("/")[0]
        self.slug = slug
        self.login = owner if owner_type == "User" else "maintainer"
        self.plan = plan
        self.users = {self.login: 101, "second": 102}
        self.repo = {
            "full_name": slug,
            "visibility": visibility,
            "private": visibility != "public",
            "default_branch": default_branch,
            "has_issues": True,
            "archived": False,
            "owner": {"login": owner, "type": owner_type},
            "permissions": {"admin": True},
            "security_and_analysis": {
                "secret_scanning": {"status": "enabled"},
                "secret_scanning_push_protection": {"status": "enabled"},
                "dependabot_security_updates": {"status": "enabled"},
            },
        }
        self.environments = {}
        self.variables = {}
        self.secrets = set()
        self.workflow_permissions = {"default_workflow_permissions": "read", "can_approve_pull_request_reviews": False}
        self.actions_permissions = {"enabled": True, "allowed_actions": "all", "sha_pinning_required": True}
        self.pages = None
        self.pvr = True
        self.alerts = True
        self.rulesets = [
            {"id": 1, "name": "default branch", "target": "branch", "source_type": "Repository", "enforcement": "active",
             "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
             "rules": [{"type": "deletion"}, {"type": "non_fast_forward"}], "bypass_actors": []},
            {"id": 2, "name": "release tags", "target": "tag", "source_type": "Repository", "enforcement": "active",
             "conditions": {"ref_name": {"include": ["refs/tags/v*"], "exclude": []}},
             "rules": [{"type": "update"}, {"type": "deletion"}], "bypass_actors": []},
        ]
        self.contents = {}
        self.elsewhere = {}
        self.changes = []
        self.secrets_set = []
        self.old_names = set()
        # The Actions tab's state of each workflow file, by name: a file
        # missing here counts as active.
        self.workflow_states = {}

    # What a test sets up

    def environment(self, name, branches=(), tags=(), reviewers=(), policy="custom", wait=0, variables=None, secrets=()):
        if policy == "custom":
            dbp = {"protected_branches": False, "custom_branch_policies": True}
        elif policy == "protected":
            dbp = {"protected_branches": True, "custom_branch_policies": False}
        else:
            dbp = None
        refs = [("branch", b) for b in branches] + [("tag", t) for t in tags]
        self.environments[name] = {
            "policy": dbp, "refs": refs, "reviewers": [self.users[r] for r in reviewers], "prevent": False,
            "wait": wait, "variables": dict(variables or {}), "secrets": set(secrets),
        }

    def mutations(self, method=None):
        return [c for c in self.changes if method is None or c[0] == method]

    # The calls

    def current_repo(self, cwd):
        return self.slug

    def set_secret(self, repo, name, value, environment):
        assert repo == self.slug
        if environment:
            if environment not in self.environments:
                raise gh.GhError("HTTP 404: Not Found")
            self.environments[environment]["secrets"].add(name)
        else:
            self.secrets.add(name)
        self.secrets_set.append((name, environment, value))

    def call(self, method, path, body=None):
        if method != "GET":
            self.changes.append((method, path, copy.deepcopy(body)))
        parts = urlsplit(path)
        query = {k: v[0] for k, v in parse_qs(parts.query).items()}
        route, base = parts.path, f"repos/{self.slug}"
        for old in self.old_names:
            # GitHub answers a renamed repository's old name as its new one.
            if route == f"repos/{old}" or route.startswith(f"repos/{old}/"):
                route = base + route[len(f"repos/{old}"):]
        if route == "user":
            return 200, {"login": self.login, "id": self.users[self.login], "plan": {"name": self.plan}}
        if route.startswith("users/"):
            login = route.split("/", 1)[1]
            return (200, {"login": login, "id": self.users[login]}) if login in self.users else (404, {"message": "Not Found"})
        if route.startswith("orgs/"):
            return 200, {"login": route.split("/")[1], "plan": {"name": self.plan}}
        if route == base:
            return self.repository(method, body)
        if route.startswith("repos/") and not route.startswith(base + "/") and route.count("/") == 2:
            other = route[len("repos/"):]
            return (200, {"full_name": self.elsewhere[other]}) if other in self.elsewhere else (404, {"message": "Not Found"})
        rest = route[len(base) + 1:]
        for pattern, handler in (
            (r"environments", self.list_environments),
            (r"environments/(?P<env>[^/]+)", self.put_environment),
            (r"environments/(?P<env>[^/]+)/deployment-branch-policies", self.branch_policies),
            (r"environments/(?P<env>[^/]+)/variables(?:/(?P<name>[^/]+))?", self.env_variables),
            (r"environments/(?P<env>[^/]+)/secrets(?:/(?P<name>[^/]+))?", self.env_secrets),
            (r"actions/variables(?:/(?P<name>[^/]+))?", self.repo_variables),
            (r"actions/secrets(?:/(?P<name>[^/]+))?", self.repo_secrets),
            (r"actions/permissions", self.permissions),
            (r"actions/permissions/workflow", self.permissions),
            (r"actions/workflows", self.list_workflows),
            (r"actions/workflows/(?P<id>[0-9]+)/enable", self.enable_workflow),
            (r"actions/workflows/(?P<name>[^/]+)/dispatches", self.dispatch),
            (r"pages", self.pages_site),
            (r"private-vulnerability-reporting|vulnerability-alerts|automated-security-fixes", self.flag),
            (r"rulesets(?:/(?P<id>\d+))?", self.ruleset),
            (r"contents/(?P<path>.+)", self.content),
        ):
            match = re.fullmatch(pattern, rest)
            if match:
                return handler(method, body, query=query, rest=rest, **match.groupdict())
        raise AssertionError(f"FakeGitHub has no answer for {method} {path}")

    def repository(self, method, body):
        if method == "GET":
            return 200, copy.deepcopy(self.repo)
        for key, value in (body or {}).get("security_and_analysis", {}).items():
            self.repo["security_and_analysis"][key] = value
        if "has_issues" in (body or {}):
            self.repo["has_issues"] = body["has_issues"]
        return 200, self.repo

    def page(self, items, query):
        size, number = int(query.get("per_page", 30)), int(query.get("page", 1))
        return items[(number - 1) * size : number * size]

    def env_json(self, name):
        e = self.environments[name]
        rules = []
        if e["reviewers"]:
            logins = {i: login for login, i in self.users.items()}
            rules.append({"type": "required_reviewers", "prevent_self_review": e["prevent"],
                          "reviewers": [{"type": "User", "reviewer": {"id": i, "login": logins[i]}} for i in e["reviewers"]]})
        if e["wait"]:
            rules.append({"type": "wait_timer", "wait_timer": e["wait"]})
        if e["policy"]:
            rules.append({"type": "branch_policy"})
        return {"name": name, "protection_rules": rules, "deployment_branch_policy": e["policy"], "can_admins_bypass": True}

    def list_environments(self, method, body, query, rest):
        names = sorted(self.environments)
        return 200, {"total_count": len(names), "environments": [self.env_json(n) for n in self.page(names, query)]}

    def put_environment(self, method, body, query, rest, env):
        if method == "GET":
            return (200, self.env_json(env)) if env in self.environments else (404, {"message": "Not Found"})
        assert method == "PUT", method
        if self.repo["private"] and self.plan == "free":
            return 422, {"message": "Environments are not available for this repository"}
        e = self.environments.setdefault(env, {"policy": None, "refs": [], "reviewers": [], "prevent": False, "wait": 0, "variables": {}, "secrets": set()})
        # A field the PUT leaves out is reset, as the strictest reading of
        # GitHub's API would have it, so a body that drops a reviewer shows.
        e["reviewers"] = [r["id"] for r in body.get("reviewers") or []]
        e["prevent"] = bool(body.get("prevent_self_review", False))
        e["wait"] = body.get("wait_timer", 0)
        policy = body.get("deployment_branch_policy")
        if not (policy and policy.get("custom_branch_policies")):
            e["refs"] = []
        e["policy"] = policy
        return 200, self.env_json(env)

    def branch_policies(self, method, body, query, rest, env):
        if env not in self.environments:
            return 404, {"message": "Not Found"}
        e = self.environments[env]
        if method == "GET":
            found = [{"id": n, "name": name, "type": kind} for n, (kind, name) in enumerate(e["refs"])]
            return 200, {"total_count": len(found), "branch_policies": self.page(found, query)}
        if not (e["policy"] and e["policy"].get("custom_branch_policies")):
            return 404, {"message": "Not Found"}
        ref = (body.get("type", "branch"), body["name"])
        if ref in e["refs"]:
            return 303, None
        e["refs"].append(ref)
        return 200, {"name": body["name"], "type": ref[0]}

    def variables_of(self, store, method, body, query, name):
        if method == "GET" and not name:
            items = [{"name": k, "value": v} for k, v in sorted(store.items())]
            return 200, {"total_count": len(items), "variables": self.page(items, query)}
        if method == "POST":
            if body["name"] in store:
                return 409, {"message": "Already exists"}
            store[body["name"]] = body["value"]
            return 201, {}
        if name not in store:
            return 404, {"message": "Not Found"}
        if method == "PATCH":
            store[name] = body["value"]
            return 204, None
        if method == "DELETE":
            del store[name]
            return 204, None
        return 200, {"name": name, "value": store[name]}

    def secrets_of(self, store, method, query, name):
        if method == "GET" and not name:
            items = [{"name": n} for n in sorted(store)]
            return 200, {"total_count": len(items), "secrets": self.page(items, query)}
        if name not in store:
            return 404, {"message": "Not Found"}
        if method == "DELETE":
            store.discard(name)
            return 204, None
        return 200, {"name": name}

    def env_variables(self, method, body, query, rest, env, name):
        if env not in self.environments:
            return 404, {"message": "Not Found"}
        return self.variables_of(self.environments[env]["variables"], method, body, query, name)

    def env_secrets(self, method, body, query, rest, env, name):
        if env not in self.environments:
            return 404, {"message": "Not Found"}
        return self.secrets_of(self.environments[env]["secrets"], method, query, name)

    def repo_variables(self, method, body, query, rest, name):
        return self.variables_of(self.variables, method, body, query, name)

    def repo_secrets(self, method, body, query, rest, name):
        return self.secrets_of(self.secrets, method, query, name)

    def permissions(self, method, body, query, rest):
        store = self.workflow_permissions if rest.endswith("workflow") else self.actions_permissions
        if method == "PUT":
            store.update(body)
            return 204, None
        return 200, dict(store)

    def dispatch(self, method, body, query, rest, name):
        return 204, None

    def list_workflows(self, method, body, query, rest):
        # GitHub lists the Pages build it runs itself beside the files.
        found = [{"id": 900, "name": "pages-build-deployment", "path": "dynamic/pages/pages-build-deployment", "state": "active"}]
        for n, (name, state) in enumerate(sorted(self.workflow_states.items()), start=1):
            found.append({"id": n, "name": name, "path": f".github/workflows/{name}", "state": state})
        return 200, {"total_count": len(found), "workflows": self.page(found, query)}

    def enable_workflow(self, method, body, query, rest, id):
        assert method == "PUT", method
        names = sorted(self.workflow_states)
        if not 1 <= int(id) <= len(names):
            return 404, {"message": "Not Found"}
        self.workflow_states[names[int(id) - 1]] = "active"
        return 204, None

    def pages_site(self, method, body, query, rest):
        if method == "GET":
            return (404, {"message": "Not Found"}) if self.pages is None else (200, dict(self.pages))
        if method == "POST" and self.pages is not None:
            return 409, {"message": "Pages is already on"}
        self.pages = {"build_type": body["build_type"], "source": {"branch": self.repo["default_branch"], "path": "/"}}
        return 201, self.pages

    def flag(self, method, body, query, rest):
        if rest == "vulnerability-alerts":
            if method == "PUT":
                self.alerts = True
                return 204, None
            return (204, None) if self.alerts else (404, {"message": "Not Found"})
        if rest == "private-vulnerability-reporting":
            if method == "PUT":
                self.pvr = True
                return 204, None
            return 200, {"enabled": self.pvr}
        status = self.repo["security_and_analysis"]["dependabot_security_updates"]
        if method == "PUT":
            if not self.alerts:
                return 422, {"message": "Vulnerability alerts are off"}
            status["status"] = "enabled"
            return 204, None
        return 200, {"enabled": status["status"] == "enabled", "paused": False}

    def ruleset(self, method, body, query, rest, id):
        if method == "GET" and id is None:
            keys = ("id", "name", "target", "source_type", "enforcement")
            return 200, self.page([{k: r[k] for k in keys} for r in self.rulesets], query)
        if method == "POST":
            made = dict(body, id=max([r["id"] for r in self.rulesets] + [0]) + 1, source_type="Repository")
            self.rulesets.append(made)
            return 201, made
        found = [r for r in self.rulesets if r["id"] == int(id)]
        if not found:
            return 404, {"message": "Not Found"}
        if method == "PUT":
            found[0].update(body)
        return 200, copy.deepcopy(found[0])

    def content(self, method, body, query, rest, path):
        if path in self.contents:
            data = base64.b64encode(self.contents[path].encode()).decode()
            return 200, {"type": "file", "name": path.rsplit("/", 1)[-1], "path": path, "content": data, "encoding": "base64"}
        inside = sorted({p[len(path) + 1:].split("/")[0] for p in self.contents if p.startswith(path + "/")})
        if inside:
            return 200, [{"type": "file", "name": n, "path": f"{path}/{n}"} for n in inside]
        return 404, {"message": "Not Found"}


# Running the command


def host(tmp_path, *workflows, extra=None, files=None):
    """A clone holding copies of the named templates, and any other workflow or file given."""
    root = tmp_path / "host"
    (root / ".git").mkdir(parents=True)
    folder = root / ".github" / "workflows"
    folder.mkdir(parents=True)
    for name in workflows:
        shutil.copy(TEMPLATES[name], folder / name)
    for name, text in (extra or {}).items():
        (folder / name).write_text(text)
    for rel, text in (files or {}).items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text)
    return root


def ktl(fake, *argv, stdin=""):
    """Run `ktl gh` in process against the fake, with stdin as the input
    and no terminal, and return its exit status."""
    args = cli.build_parser().parse_args(["gh", *argv])
    saved = sys.stdin
    sys.stdin = io.StringIO(stdin)
    try:
        return gh.main(args, github=fake)
    finally:
        sys.stdin = saved


@pytest.fixture
def at(monkeypatch):
    """Move into a host's top folder, as a person runs the command in a clone."""
    def move(root):
        monkeypatch.chdir(root)
        return root
    return move


def plan(fake, *argv, capsys=None):
    rc = ktl(fake, "plan", *argv)
    assert rc == 0
    return capsys.readouterr().out if capsys else ""


def planned(fake, *argv):
    """The plan as JSON: each finding's verb, level and text."""
    args = cli.build_parser().parse_args(["gh", "plan", "--json", *argv])
    out = io.StringIO()
    saved = sys.stdout
    sys.stdout = out
    try:
        assert gh.main(args, github=fake) == 0
    finally:
        sys.stdout = saved
    return json.loads(out.getvalue())


def texts(result, verb=None):
    return [f["text"] for f in result["findings"] if verb is None or f["verb"] == verb]


# The catalogues


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def all_catalogues():
    return {**{k: load(v) for k, v in CATALOGUES.items()}, "own": load(OWN)}


@pytest.mark.parametrize("name", ["ktl-sidecar", "ktl-website", "own"])
def test_each_catalogue_keeps_to_the_format(name):
    path = OWN if name == "own" else CATALOGUES[name]
    assert gh.problems_of(load(path), str(path)) == []
    gh.load_catalogue(path.read_text(encoding="utf-8"), str(path))


def test_a_catalogue_with_a_field_the_command_does_not_know_is_refused(tmp_path, at, capsys):
    root = at(host(tmp_path, *BUNDLE))
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"format": 1, "settings": [{"kind": "variable", "name": "X", "why": "y", "swtich": {}}]}))
    assert ktl(FakeGitHub(), "plan", "--catalogue", str(bad)) == 2
    assert "unknown field 'swtich'" in capsys.readouterr().err
    assert root.exists()


def test_a_workflow_entry_names_an_action_and_no_files():
    entry = {"kind": "workflow", "name": "W", "why": "y", "uses": "a/b@v1", "workflows": ["w.yml"], "inputs": {"x": True}}
    problems = " ".join(gh.problems_of({"format": 1, "settings": [entry]}, "c.json"))
    assert "uses names an action as owner/name" in problems
    assert "not the files in workflows" in problems
    assert "inputs maps each input" in problems


def test_the_package_carries_a_catalogue_for_each_skill_that_installs_workflows():
    assert {p.parent.parent.name for p in gh.package_catalogues()} == set(CATALOGUES)


def slugs(markdown: str) -> set:
    """The anchors GitHub gives a page's headings, a repeated heading numbered from 1."""
    seen, found = {}, set()
    for heading in re.findall(r"^#{1,6} (.+)$", markdown, re.M):
        slug = re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")
        n = seen.get(slug, 0)
        found.add(slug if n == 0 else f"{slug}-{n}")
        seen[slug] = n + 1
    return found


def page_of(url: str) -> tuple:
    """The file and anchor a catalogue's link names, in this repository."""
    blob = "https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/"
    w3id = "https://w3id.org/ktl/docs/"
    target, _, anchor = url.partition("#")
    if target.startswith(blob):
        return REPO / target[len(blob):], anchor
    if target.startswith(w3id):
        return REPO / "docs" / (target[len(w3id):].strip("/") + ".md"), anchor
    raise AssertionError(f"a catalogue links outside this repository: {url}")


@pytest.mark.parametrize("name", ["ktl-sidecar", "ktl-website", "own"])
def test_every_page_and_heading_a_catalogue_links_to_exists(name):
    path = OWN if name == "own" else CATALOGUES[name]
    catalogue = gh.load_catalogue(path.read_text(encoding="utf-8"), str(path))
    urls = [e["url"] for e in catalogue.entries] + [p["url"] for p in catalogue.presets.values()]
    assert all(urls), "every entry and preset links to its page"
    for url in urls:
        page, anchor = page_of(url)
        assert page.is_file(), url
        assert anchor in slugs(page.read_text(encoding="utf-8")), url


def entries_for(workflow: str, catalogue_names=("ktl-sidecar", "ktl-website")):
    return [e for n in catalogue_names for e in load(CATALOGUES[n])["settings"] if workflow in e.get("workflows", [])]


@pytest.mark.parametrize("workflow", sorted(TEMPLATES))
def test_every_name_a_template_reads_has_an_entry_for_it(workflow):
    text = TEMPLATES[workflow].read_text(encoding="utf-8")
    described = {(e["kind"], e["name"]) for e in entries_for(workflow) if e["kind"] in ("variable", "secret")}
    assert gh.names_read(text) <= described, gh.names_read(text) - described
    environments = {e["name"] for e in entries_for(workflow) if e["kind"] == "environment" and not e.get("named_by")}
    for name in gh.literal_environments(text):
        assert name in environments, f"{workflow} runs a job in Environment {name}, which no entry describes for it"
    named = {e["named_by"] for e in entries_for(workflow) if e.get("named_by")}
    for value in gh.environment_values(text):
        for variable in re.findall(r"vars\.([A-Z_]+)", value):
            assert variable in named, f"{workflow} names an Environment through {variable}, which no entry describes"


@pytest.mark.parametrize("name", ["ktl-sidecar", "ktl-website"])
def test_every_entry_is_read_by_a_workflow_it_names(name):
    for entry in load(CATALOGUES[name])["settings"]:
        workflows = entry.get("workflows", [])
        for workflow in workflows:
            assert workflow in TEMPLATES, f"{entry['name']} names {workflow}, which is no template"
        if not workflows or entry.get("names_from"):
            continue
        texts_ = [TEMPLATES[w].read_text(encoding="utf-8") for w in workflows]
        if entry["kind"] in ("variable", "secret"):
            assert any((entry["kind"], entry["name"]) in gh.names_read(t) for t in texts_), entry["name"]
        elif entry["kind"] == "environment":
            word = entry.get("named_by")
            assert any((("variable", word) in gh.names_read(t)) if word else gh.names_environment(t, entry["name"]) for t in texts_), entry["name"]


def table_names(page: Path, heading: str) -> set:
    text = page.read_text(encoding="utf-8")
    body = text.split(heading, 1)[1].split("\n## ", 1)[0]
    return set(re.findall(r"^\| `([A-Z][A-Z0-9_]*\*?)` \|", body, re.M))


def test_the_switches_table_lists_every_name_the_templates_read():
    """automation.md's table is the one list a host reads; the catalogue is
    the one the command reads. Neither may leave a name out."""
    described = {e["name"] for n in CATALOGUES for e in load(CATALOGUES[n])["settings"] if e["kind"] in ("variable", "secret")}
    listed = table_names(SIDECAR / "references" / "automation.md", "## Switches and where they go")
    assert listed == described


def test_this_repositorys_own_workflows_read_nothing_the_catalogues_leave_out():
    described = {(e["kind"], e["name"]) for c in all_catalogues().values() for e in c["settings"] if e["kind"] in ("variable", "secret")}
    for path in sorted((REPO / ".github" / "workflows").glob("*.y*ml")):
        missing = gh.names_read(path.read_text(encoding="utf-8")) - described
        assert not missing, f"{path.name} reads {missing}; describe each in .github/repository-settings.json"
    for role in load(OWN)["roles"].values():
        for workflow in role["workflows"]:
            assert (REPO / ".github" / "workflows" / workflow).is_file(), workflow


def test_a_retired_name_is_read_by_nothing_and_the_changelog_says_when():
    changelog = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    workflows = [*TEMPLATES.values(), *(REPO / ".github" / "workflows").glob("*.y*ml")]
    retired = [old for c in all_catalogues().values() for old in c.get("retired", [])]
    assert retired, "the catalogues name the retired names"
    for old in retired:
        for path in workflows:
            assert (old["kind"], old["name"]) not in gh.names_read(path.read_text(encoding="utf-8")), f"{path.name} still reads {old['name']}"
        section = changelog.split(f"## [{old['changelog']}]", 1)
        assert len(section) == 2, f"CHANGELOG.md has no release {old['changelog']}"
        assert old["name"] in section[1].split("\n## [", 1)[0], f"the {old['changelog']} entry does not name {old['name']}"


def preset_rows(heading: str) -> dict:
    text = (SIDECAR / "references" / "automation.md").read_text(encoding="utf-8")
    body = text.split(heading + "\n", 1)[1].split("\n### ", 1)[0]
    return dict(re.findall(r"^\| `([A-Z_]+)`(?: \(secret\))? \| `([^`]+)`", body, re.M))


def test_the_agent_presets_are_the_commands_automation_md_gives():
    presets = load(CATALOGUES["ktl-sidecar"])["presets"]
    for preset, heading in (("copilot", "### Copilot CLI"), ("claude-code", "### Claude Code")):
        rows = preset_rows(heading)
        assert presets[preset]["variables"]["AGENT_CLI"] == rows["AGENT_CLI"], preset
        assert presets[preset]["variables"]["AGENT_API_KEY_ENV"] == rows["AGENT_API_KEY_ENV"], preset
    text = (SIDECAR / "references" / "automation.md").read_text(encoding="utf-8")
    assert f"Set `AGENT_CLI` to `{presets['members']['variables']['AGENT_CLI']}`" in text


def test_each_switch_that_offers_a_run_names_a_workflow_that_can_be_started_by_hand():
    for entry in [e for n in CATALOGUES for e in load(CATALOGUES[n])["settings"] if e.get("switch", {}).get("run")]:
        assert "workflow_dispatch:" in TEMPLATES[entry["switch"]["run"]].read_text(encoding="utf-8"), entry["name"]


# Reading workflows


def test_names_read_and_job_level_reads():
    text = (
        "jobs:\n  a:\n    if: vars.ON == 'true'\n    runs-on: ${{ vars.RUNNER || 'ubuntu-latest' }}\n"
        "    environment:\n      name: ${{ vars.ENV_NAME }}\n    steps:\n      - if: vars.STEP == 'x'\n"
        "        env:\n          K: ${{ secrets.KEY }}\n          T: ${{ secrets.GITHUB_TOKEN }}\n"
    )
    assert gh.names_read(text) == {("variable", "ON"), ("variable", "RUNNER"), ("variable", "ENV_NAME"), ("variable", "STEP"), ("secret", "KEY")}
    assert gh.job_level_reads(text) == {"ON", "RUNNER", "ENV_NAME"}


def test_an_environment_counts_only_where_a_job_runs_in_it():
    text = (
        "jobs:\n  a:\n    environment: release\n  b:\n    environment:\n      name: github-pages\n"
        "  c:\n    environment:\n      name: ${{ vars.X == 'true' && 'pypi' || 'testpypi' }}\n"
        "    steps:\n      - uses: actions/upload-artifact@" + "0" * 40 + "\n        with:\n          name: knowledge-federation\n"
    )
    assert gh.literal_environments(text) == {"release", "github-pages"}
    assert gh.names_environment(text, "pypi") and gh.names_environment(text, "testpypi")
    assert not gh.names_environment(text, "knowledge-federation")


def test_unpinned_actions_are_found():
    text = "steps:\n  - uses: actions/checkout@v4\n  - uses: ./local\n  - uses: a/b@" + "a" * 40 + " # v1\n  - uses: docker://x\n"
    assert gh.unpinned_actions(text) == ["actions/checkout@v4"]


def scorecard(value="true"):
    """A workflow that runs Scorecard, with publish_results set to the value given."""
    return (
        "on: push\njobs:\n  analysis:\n    runs-on: ubuntu-latest\n    steps:\n"
        "      - uses: OSSF/scorecard-action@" + "f" * 40 + " # v2.5.0\n"
        f"        with:\n          results_file: results.sarif\n          publish_results: {value}\n"
    )


def test_an_action_and_its_inputs_are_found_at_any_ref_and_in_any_case():
    assert gh.uses_action(scorecard(), "ossf/scorecard-action")
    assert not gh.uses_action(scorecard(), "ossf/scorecard")
    for value in ("true", "True", "'true'", '"true"  # publish'):
        assert gh.sets_input(scorecard(value), "publish_results", "true"), value
    for value in ("false", "truex", "'true"):
        assert not gh.sets_input(scorecard(value), "publish_results", "true"), value


# gh itself


class Recorder:
    """Stands in for subprocess.run and keeps each command and its input."""

    def __init__(self, stdout="", returncode=0):
        self.calls = []
        self.stdout = stdout
        self.returncode = returncode

    def __call__(self, args, input=None, **kwargs):
        self.calls.append((args, input))
        return subprocess.CompletedProcess(args, self.returncode, self.stdout, "")


def test_a_call_sends_its_body_on_standard_input_and_reads_the_status():
    run = Recorder("HTTP/2.0 201 Created\nContent-Type: application/json\n\n{\"ok\": true}")
    status, payload = gh.GitHub(run).call("POST", "repos/a/b/actions/variables", {"name": "X", "value": "y"})
    assert (status, payload) == (201, {"ok": True})
    args, stdin = run.calls[0]
    assert args[:6] == ["gh", "api", "--include", "--method", "POST", "repos/a/b/actions/variables"]
    assert args[-2:] == ["--input", "-"] and json.loads(stdin) == {"name": "X", "value": "y"}


@pytest.mark.parametrize(
    "stdout, expected",
    [
        ("HTTP/2.0 204 No Content\nX: y\n\n", (204, None)),
        ("HTTP/2.0 404 Not Found\n\n{\"message\": \"Not Found\"}", (404, {"message": "Not Found"})),
        ("HTTP/2.0 301 Moved\nLocation: z\n\nHTTP/2.0 200 OK\n\n{\"full_name\": \"b/c\"}", (200, {"full_name": "b/c"})),
        ("HTTP/1.1 200 OK\r\nA: b\r\n\r\n[1, 2]", (200, [1, 2])),
        ("", (None, None)),
    ],
)
def test_responses_are_read_from_gh_api_include(stdout, expected):
    assert gh.parse_response(stdout) == expected


def test_no_answer_from_gh_is_an_error_not_a_status():
    with pytest.raises(gh.GhError, match="not logged in"):
        gh.GitHub(lambda *a, **k: subprocess.CompletedProcess(a, 1, "", "not logged in")).call("GET", "user")


def test_a_secret_reaches_gh_on_standard_input_and_never_in_an_argument():
    run = Recorder()
    gh.GitHub(run).set_secret("a/b", "AGENT_API_KEY", "s3cret-value", "knowledge-librarian")
    args, stdin = run.calls[0]
    assert args == ["gh", "secret", "set", "AGENT_API_KEY", "--repo", "a/b", "--env", "knowledge-librarian"]
    assert stdin == "s3cret-value"
    assert not any("s3cret" in a for a in args)


# plan and check


def test_plan_on_a_new_bundle_host_lists_the_environments_and_changes_nothing(tmp_path, at, capsys):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub()
    out = plan(fake, capsys=capsys)
    assert "Environment knowledge-librarian: create it, limited to main" in out
    assert "Environment knowledge-sync: create it, limited to main" in out
    assert "librarian      off" in out
    assert "needs first, from ktl gh apply --agent: AGENT_API_KEY_ENV" in out
    assert fake.changes == []


def test_check_exits_1_while_something_required_is_missing_and_0_after_apply(tmp_path, at, capsys):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub()
    assert ktl(fake, "check") == 1
    assert "knowledge-librarian" in capsys.readouterr().out
    assert ktl(fake, "apply", "--yes") == 0
    assert ktl(fake, "check") == 0


def test_check_strict_counts_what_is_recommended(tmp_path, at, capsys):
    at(host(tmp_path))
    fake = FakeGitHub()
    fake.pvr = False
    assert ktl(fake, "check") == 0
    assert ktl(fake, "check", "--strict") == 1
    assert "private vulnerability reporting" in capsys.readouterr().out


def test_a_public_repository_is_asked_for_a_workflow_that_publishes_a_scorecard_result(tmp_path, at, capsys):
    root = at(host(tmp_path, extra={"scorecard.yml": scorecard("false")}))
    fake = FakeGitHub()
    wanted = "Workflow OpenSSF Scorecard: no workflow here runs ossf/scorecard-action with publish_results: true; add one"
    assert [f["level"] for f in planned(fake)["findings"] if f["text"] == wanted] == ["recommended"]
    assert ktl(fake, "check") == 0
    assert ktl(fake, "check", "--strict") == 1
    assert "OpenSSF Scorecard" in capsys.readouterr().out
    (root / ".github" / "workflows" / "scorecard.yml").write_text(scorecard("true"))
    assert wanted not in texts(planned(fake))
    assert ktl(fake, "check", "--strict") == 0
    (root / ".github" / "workflows" / "scorecard.yml").unlink()
    assert wanted not in texts(planned(FakeGitHub(visibility="private", plan="enterprise"))), "Scorecard publishes for a public repository only"


def test_apply_turns_on_a_workflow_github_turned_off_and_leaves_one_a_person_turned_off(tmp_path, at):
    own = "on:\n  schedule:\n    - cron: '0 6 * * 1'\njobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n      - run: true\n"
    at(host(tmp_path, *BUNDLE, extra={"own.yml": own}))
    fake = FakeGitHub()
    fake.environment("knowledge-librarian", branches=["main"])
    fake.environment("knowledge-sync", branches=["main"])
    fake.workflow_states = {"knowledge-sync.yaml": "disabled_inactivity", "knowledge-librarian.yaml": "disabled_manually", "own.yml": "disabled_inactivity", "knowledge-release.yaml": "active"}
    result = planned(fake)
    assert "Workflow knowledge-sync.yaml: GitHub turned it off after 60 days with no activity in the repository; turn it on again" in texts(result, "apply")
    assert "Workflow knowledge-librarian.yaml is turned off in the Actions tab; turn it on there, or remove the file" in texts(result, "person")
    assert any(t.startswith("Workflow own.yml: GitHub turned it off") for t in texts(result, "note")), "a workflow no catalogue describes is the repository's own"
    assert ktl(fake, "check") == 1
    assert ktl(fake, "apply", "--yes") == 0
    assert fake.workflow_states == {"knowledge-sync.yaml": "active", "knowledge-librarian.yaml": "disabled_manually", "own.yml": "disabled_inactivity", "knowledge-release.yaml": "active"}
    assert ktl(fake, "check") == 0


def test_a_copy_older_than_a_name_is_not_asked_for_it(tmp_path, at):
    """A host's copy of a workflow from an older release reads fewer names,
    and the catalogue follows the copy it holds."""
    old = TEMPLATES["knowledge-federation.yaml"].read_text().replace("name: knowledge-federation\n      deployment: false", "name: other\n      deployment: false")
    old = old.replace("environment:\n      name: other\n      deployment: false\n", "")
    at(host(tmp_path, *BUNDLE, extra={"knowledge-federation.yaml": old}))
    result = planned(FakeGitHub())
    assert not [t for t in texts(result) if "Environment knowledge-federation" in t]


def test_a_role_counts_its_workflows_before_they_are_installed(tmp_path, at):
    at(host(tmp_path))
    result = planned(FakeGitHub(), "--role", "domain")
    created = [t for t in texts(result, "apply") if t.startswith("Environment")]
    assert any("knowledge-federation: create it, limited to main and tags v*" in t for t in created)
    assert any("knowledge-sync: create it" in t for t in created), "the domain role carries the bundle role"


def test_a_renamed_repository_is_changed_under_its_current_name(tmp_path, at):
    at(tmp_path)
    fake = FakeGitHub(slug="acme/new-name")
    fake.old_names = {"acme/old-name"}
    for name in BUNDLE:
        fake.contents[f".github/workflows/{name}"] = TEMPLATES[name].read_text()
    assert "acme/old-name is now acme/new-name, so the command acts on acme/new-name" in texts(planned(fake, "--repo", "acme/old-name"), "note")
    assert ktl(fake, "apply", "--yes", "--repo", "acme/old-name") == 0
    assert fake.changes and all(path.startswith("repos/acme/new-name/") for _, path, _ in fake.changes)


def test_plan_reads_another_repository_through_the_api(tmp_path, at):
    at(tmp_path)
    fake = FakeGitHub()
    for name in BUNDLE:
        fake.contents[f".github/workflows/{name}"] = TEMPLATES[name].read_text()
    result = planned(fake, "--repo", fake.slug)
    assert result["workflows"] == sorted(BUNDLE)
    assert "Environment knowledge-sync: create it, limited to main" in texts(result, "apply")


def test_the_repositorys_own_catalogue_is_read_and_can_require_more(tmp_path, at):
    own = {"format": 1, "settings": [{"kind": "environment", "name": "release", "workflows": ["release.yml"], "branches": ["{default}"], "reviewers": 1, "why": "w"}]}
    workflow = "on: push\njobs:\n  go:\n    runs-on: ubuntu-latest\n    environment: release\n    steps:\n      - run: true\n"
    at(host(tmp_path, extra={"release.yml": workflow}, files={".github/repository-settings.json": json.dumps(own)}))
    result = planned(FakeGitHub())
    assert "Environment release: create it, limited to main, with acme as required reviewer" in texts(result, "apply")


# apply


def test_apply_creates_each_environment_limited_to_its_refs_and_a_second_run_does_nothing(tmp_path, at, capsys):
    at(host(tmp_path, *BUNDLE, "knowledge-federation.yaml"))
    fake = FakeGitHub()
    assert ktl(fake, "apply", "--yes") == 0
    assert fake.environments["knowledge-federation"]["refs"] == [("branch", "main"), ("tag", "v*")]
    assert fake.environments["github-pages"]["refs"] == [("branch", "main"), ("tag", "v*")]
    assert fake.environments["knowledge-librarian"]["reviewers"] == []
    capsys.readouterr()
    before = len(fake.changes)
    assert ktl(fake, "apply", "--yes") == 0
    assert "nothing to apply" in capsys.readouterr().out
    assert len(fake.changes) == before


def test_apply_asks_first_and_changes_nothing_without_an_answer(tmp_path, at, capsys):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub()
    assert ktl(fake, "apply") == 1
    assert "add --yes" in capsys.readouterr().err
    assert fake.changes == []


def test_apply_limits_an_environment_that_admits_every_branch_and_never_removes(tmp_path, at):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub()
    fake.environment("knowledge-librarian", policy=None, wait=5, reviewers=["second"])
    fake.environment("knowledge-sync", branches=["main", "release/*"])
    result = planned(fake)
    assert "Environment knowledge-sync also admits release/*, which no catalogue names, so a job on those refs can read its secrets" in texts(result, "person")
    assert ktl(fake, "apply", "--yes") == 0
    librarian = fake.environments["knowledge-librarian"]
    assert librarian["refs"] == [("branch", "main")]
    assert librarian["reviewers"] == [102] and librarian["wait"] == 5, "a reviewer and a wait timer a person set are kept"
    assert fake.environments["knowledge-sync"]["refs"] == [("branch", "main"), ("branch", "release/*")]
    assert not fake.mutations("DELETE")


def test_apply_switches_protected_branches_only_to_the_named_branch(tmp_path, at):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub()
    fake.environment("knowledge-sync", policy="protected")
    fake.environment("knowledge-librarian", branches=["main"])
    assert "protected branches only, which counts no ruleset" in " ".join(texts(planned(fake), "apply"))
    assert ktl(fake, "apply", "--yes") == 0
    assert fake.environments["knowledge-sync"]["policy"]["custom_branch_policies"] is True
    assert fake.environments["knowledge-sync"]["refs"] == [("branch", "main")]


def test_a_review_environment_a_variable_names_gets_a_reviewer_and_keeps_its_other_rules(tmp_path, at):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub()
    fake.variables["KNOWLEDGE_SYNC_REVIEW_ENVIRONMENT"] = "knowledge-sync-review"
    fake.environment("knowledge-sync-review", branches=["main"], wait=2)
    fake.environment("knowledge-sync", branches=["main"])
    fake.environment("knowledge-librarian", branches=["main"])
    assert ktl(fake, "check") == 1
    assert ktl(fake, "apply", "--yes", "--reviewer", "second") == 0
    review = fake.environments["knowledge-sync-review"]
    assert review["reviewers"] == [102] and review["wait"] == 2 and review["refs"] == [("branch", "main")]


def test_apply_makes_the_recommended_changes_only_when_asked(tmp_path, at):
    at(host(tmp_path))
    fake = FakeGitHub()
    fake.pvr = False
    fake.alerts = False
    fake.repo["security_and_analysis"]["dependabot_security_updates"]["status"] = "disabled"
    fake.rulesets = []
    assert ktl(fake, "apply", "--yes") == 0
    assert fake.changes == []
    assert ktl(fake, "apply", "--yes", "--recommended") == 0
    assert fake.pvr and fake.alerts
    assert fake.repo["security_and_analysis"]["dependabot_security_updates"]["status"] == "enabled", "alerts come before the updates that need them"
    rules = {r["name"]: {x["type"] for x in r["rules"]} for r in fake.rulesets}
    assert rules == {"default branch": {"deletion", "non_fast_forward"}, "release tags": {"update", "deletion"}}


def test_a_ruleset_that_covers_the_branch_counts_and_one_of_the_same_name_is_extended(tmp_path, at):
    at(host(tmp_path, files={".github/repository-settings.json": json.dumps({"format": 1, "settings": [
        {"kind": "ruleset", "name": "default branch", "target": "branch", "include": ["~DEFAULT_BRANCH"], "rules": ["required_linear_history"], "why": "w"}]})}))
    fake = FakeGitHub()
    assert ktl(fake, "apply", "--yes") == 0
    assert {x["type"] for x in fake.rulesets[0]["rules"]} == {"deletion", "non_fast_forward", "required_linear_history"}
    fake.rulesets[0]["enforcement"] = "disabled"
    result = planned(fake)
    assert any("is disabled, so it blocks nothing" in t for t in texts(result, "person"))


def test_requiring_pinned_actions_waits_until_every_action_is_pinned(tmp_path, at):
    loose = "on: push\njobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n"
    at(host(tmp_path, *BUNDLE, extra={"loose.yml": loose}))
    fake = FakeGitHub()
    fake.actions_permissions["sha_pinning_required"] = False
    result = planned(fake)
    assert any("would stop actions/checkout@v4 in loose.yml" in t for t in texts(result, "note"))
    assert not any("sha pinning" in t for t in texts(result, "apply"))
    (Path.cwd() / ".github" / "workflows" / "loose.yml").unlink()
    assert "Setting sha pinning required: set it to true" in texts(planned(fake), "apply")


def test_a_private_repository_on_github_free_keeps_its_secrets_on_the_repository(tmp_path, at):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub(visibility="private", plan="free")
    result = planned(fake)
    assert not [t for t in texts(result, "apply") if t.startswith("Environment")]
    assert any("a private repository on GitHub Free has none" in t for t in texts(result, "note"))
    assert "Secret KNOWLEDGE_SYNC_TOKEN in the repository: not set" in texts(result, "secrets")


def test_a_quoted_value_and_a_refused_name_are_reported(tmp_path, at):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub()
    fake.variables.update({"AGENT_CLI": '"npx -y tool"', "AGENT_API_KEY_ENV": "GITHUB_TOKEN"})
    people = texts(planned(fake), "person")
    assert any("Variable AGENT_CLI is" in t and "keeps the quotes" in t for t in people)
    assert "Variable AGENT_API_KEY_ENV is 'GITHUB_TOKEN', which its workflow refuses" in people


def test_a_renamed_repository_in_a_list_is_written_under_its_current_name(tmp_path, at):
    catalogue = {"format": 1, "settings": [{"kind": "variable", "name": "HOSTS", "workflows": ["hosts.yml"], "check": "repositories", "level": "optional", "why": "w"}]}
    workflow = "on: push\njobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo ${{ vars.HOSTS }}\n"
    at(host(tmp_path, extra={"hosts.yml": workflow}, files={".github/repository-settings.json": json.dumps(catalogue)}))
    fake = FakeGitHub()
    fake.variables["HOSTS"] = "acme/one old/two acme/gone"
    fake.elsewhere = {"acme/one": "acme/one", "old/two": "new/two"}
    result = planned(fake)
    assert "Variable HOSTS names old/two, which is now new/two" in texts(result, "note")
    assert "Variable HOSTS names acme/gone, which your gh login cannot find" in texts(result, "person")
    assert ktl(fake, "apply", "--yes", "--recommended") == 0
    assert fake.variables["HOSTS"] == "acme/one new/two acme/gone"


def test_apply_sets_an_agent_preset_and_a_domain_host_gets_the_members_script(tmp_path, at):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub()
    fake.variables["AGENT_PROMPT_FLAG"] = "arg"
    assert ktl(fake, "apply", "--yes", "--agent", "claude-code") == 0
    assert fake.variables["AGENT_CLI"].startswith("npx -y @anthropic-ai/claude-code@")
    assert fake.variables["AGENT_API_KEY_ENV"] == "ANTHROPIC_API_KEY"
    assert "AGENT_PROMPT_FLAG" not in fake.variables and "AGENT_USE_JOB_TOKEN" not in fake.variables

    root = tmp_path / "domain"
    root.mkdir()
    at(host(root, *BUNDLE, "knowledge-federation.yaml"))
    fake = FakeGitHub()
    result = planned(fake)
    assert "Variable AGENT_CLI: set it to uv run --project .lokf .lokf/scripts/knowledge-federate.py members" in texts(result, "apply")
    assert ktl(fake, "apply", "--yes", "--recommended") == 0
    assert fake.variables["AGENT_USE_JOB_TOKEN"] == "true"


# secrets


def test_secrets_reads_values_from_standard_input_and_sets_each_where_it_belongs(tmp_path, at, capsys):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub()
    fake.environment("knowledge-sync", branches=["main"])
    fake.environment("knowledge-librarian", branches=["main"])
    rc = ktl(fake, "secrets", stdin="KNOWLEDGE_SYNC_TOKEN=github_pat_x\nAGENT_API_KEY='sk-y'\nUNRELATED=z\n")
    assert rc == 0
    assert sorted(fake.secrets_set) == [("AGENT_API_KEY", "knowledge-librarian", "sk-y"), ("KNOWLEDGE_SYNC_TOKEN", "knowledge-sync", "github_pat_x")]
    out = capsys.readouterr().out
    assert "github_pat_x" not in out and "sk-y" not in out
    assert "skipped: KNOWLEDGE_SKILLS_TOKEN" in out


def test_secrets_waits_for_the_environment_and_refuses_a_name_no_workflow_reads(tmp_path, at, capsys):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub()
    assert ktl(fake, "secrets", "KNOWLEDGE_SYNC_TOKEN", stdin="KNOWLEDGE_SYNC_TOKEN=x\n") == 1
    assert "create the Environment knowledge-sync first" in capsys.readouterr().err
    assert ktl(fake, "secrets", "NOT_A_SECRET", stdin="") == 2
    assert fake.secrets_set == []


def test_a_job_token_means_no_agent_key_is_asked_for(tmp_path, at):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub()
    fake.variables["AGENT_USE_JOB_TOKEN"] = "true"
    fake.environment("knowledge-librarian", branches=["main"])
    fake.environment("knowledge-sync", branches=["main"])
    assert ktl(fake, "secrets", stdin="AGENT_API_KEY=k\n") == 0
    assert fake.secrets_set == []


def test_the_ingest_secrets_are_the_ones_its_manifest_names(tmp_path, at):
    manifest = "auth:\n  a:\n    user_env: KNOWLEDGE_INGEST_ATLASSIAN_USER   # KNOWLEDGE_INGEST_NOT_THIS\n    env: KNOWLEDGE_INGEST_ATLASSIAN_TOKEN\n"
    at(host(tmp_path, *BUNDLE, "knowledge-ingest.yaml", files={".lokf/ingest.yaml": manifest}))
    fake = FakeGitHub()
    fake.variables["KNOWLEDGE_INGEST_ENABLED"] = "true"
    result = planned(fake)
    assert any("each KNOWLEDGE_INGEST_ secret the manifest names" in t for t in texts(result, "secrets"))
    assert ktl(fake, "apply", "--yes") == 0
    assert ktl(fake, "secrets", stdin="KNOWLEDGE_INGEST_ATLASSIAN_USER=me\nKNOWLEDGE_INGEST_ATLASSIAN_TOKEN=t\n") == 0
    assert {(n, e) for n, e, _ in fake.secrets_set} == {("KNOWLEDGE_INGEST_ATLASSIAN_USER", "knowledge-ingest"), ("KNOWLEDGE_INGEST_ATLASSIAN_TOKEN", "knowledge-ingest")}


# prune


def test_prune_removes_a_retired_name_wherever_it_is(tmp_path, at, capsys):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub()
    fake.variables["KNOWLEDGE_LIBRARIAN_CMD"] = "bash .lokf/scripts/knowledge-librarian.sh"
    fake.environment("knowledge-librarian", branches=["main"], secrets=["KNOWLEDGE_LIBRARIAN_CMD"])
    result = planned(fake)
    assert "Variable KNOWLEDGE_LIBRARIAN_CMD in the repository: retired, replaced by KNOWLEDGE_LIBRARIAN_ENABLED (CHANGELOG 0.11.0)" in texts(result, "prune")
    assert ktl(fake, "apply", "--yes") == 0
    assert "KNOWLEDGE_LIBRARIAN_CMD" in fake.variables, "apply removes nothing"
    assert ktl(fake, "prune", "--yes") == 0
    assert "KNOWLEDGE_LIBRARIAN_CMD" not in fake.variables
    assert "KNOWLEDGE_LIBRARIAN_CMD" not in fake.environments["knowledge-librarian"]["secrets"]


def test_prune_keeps_a_retired_name_a_workflow_still_reads(tmp_path, at, capsys):
    old = "on: workflow_dispatch\njobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n      - run: ${{ vars.KNOWLEDGE_LIBRARIAN_CMD }}\n"
    at(host(tmp_path, *BUNDLE, extra={"old-librarian.yml": old}))
    fake = FakeGitHub()
    fake.variables["KNOWLEDGE_LIBRARIAN_CMD"] = "x"
    assert ktl(fake, "prune", "--yes") == 0
    assert "old-librarian.yml still reads it" in capsys.readouterr().out
    assert fake.variables["KNOWLEDGE_LIBRARIAN_CMD"] == "x"


def test_prune_removes_a_switch_from_an_environment_and_moves_a_value(tmp_path, at):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub()
    fake.environment("knowledge-librarian", branches=["main"], variables={"KNOWLEDGE_LIBRARIAN_ENABLED": "true", "KNOWLEDGE_RETRIEVAL": "true"})
    fake.environment("release", variables={"PYPI_RELEASE_ENABLED": "false"})
    fake.contents = {}
    pypi = "on: release\njobs:\n  up:\n    if: vars.PYPI_RELEASE_ENABLED == 'true'\n    runs-on: ubuntu-latest\n    steps:\n      - run: true\n"
    (Path.cwd() / ".github" / "workflows" / "pypi.yml").write_text(pypi)
    assert ktl(fake, "prune", "--yes") == 0
    assert fake.environments["knowledge-librarian"]["variables"] == {}
    assert fake.variables == {"KNOWLEDGE_RETRIEVAL": "true"}, "a value a step reads moves to the repository; a switch a job's if: reads is removed"
    assert fake.environments["release"]["variables"] == {}


def test_prune_removes_a_repository_copy_of_a_secret_only_once_its_environment_holds_it(tmp_path, at):
    at(host(tmp_path, *BUNDLE, "knowledge-federation.yaml"))
    fake = FakeGitHub()
    fake.secrets = {"AGENT_API_KEY", "KNOWLEDGE_SYNC_TOKEN", "KNOWLEDGE_FEDERATE_TOKEN"}
    fake.environment("knowledge-librarian", branches=["main"], secrets=["AGENT_API_KEY"])
    fake.environment("knowledge-sync", branches=["main"])
    fake.environment("knowledge-federation", branches=["main"], tags=["v*"], secrets=["KNOWLEDGE_FEDERATE_TOKEN"])
    result = planned(fake)
    assert any(t.startswith("Secret KNOWLEDGE_SYNC_TOKEN: set it in Environment knowledge-sync") for t in texts(result, "secrets"))
    assert ktl(fake, "prune", "--yes") == 0
    assert fake.secrets == {"KNOWLEDGE_SYNC_TOKEN", "KNOWLEDGE_FEDERATE_TOKEN"}, "the federation's check job reads a repository copy"


# enable


def test_enable_lists_the_switches_and_what_each_needs(tmp_path, at, capsys):
    at(host(tmp_path, *BUNDLE))
    assert ktl(FakeGitHub(), "enable") == 0
    out = capsys.readouterr().out
    assert re.search(r"^librarian\s+off\s+KNOWLEDGE_LIBRARIAN_ENABLED$", out, re.M)
    assert "enable also sets: Actions may create pull requests" in out


def test_enable_refuses_a_switch_whose_prerequisites_are_missing(tmp_path, at, capsys):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub()
    assert ktl(fake, "enable", "librarian", "--yes") == 1
    assert "AGENT_CLI, the agent's command" in capsys.readouterr().out
    assert fake.changes == []


def test_enable_turns_the_librarian_on_once_its_agent_is_set_and_starts_a_run(tmp_path, at, capsys):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub()
    assert ktl(fake, "apply", "--yes", "--agent", "copilot") == 0
    assert ktl(fake, "enable", "librarian", "--yes", "--run") == 0
    assert fake.workflow_permissions == {"default_workflow_permissions": "read", "can_approve_pull_request_reviews": True}
    assert fake.variables["KNOWLEDGE_LIBRARIAN_ENABLED"] == "true"
    assert ("POST", "repos/acme/host/actions/workflows/knowledge-librarian.yaml/dispatches", {"ref": "main"}) in fake.changes
    switch = next(n for n, c in enumerate(fake.changes) if (c[2] or {}).get("name") == "KNOWLEDGE_LIBRARIAN_ENABLED")
    permission = next(n for n, c in enumerate(fake.changes) if c[1].endswith("actions/permissions/workflow"))
    assert permission < switch, "Actions may open pull requests before the switch is on"
    assert ktl(fake, "check") == 0


def test_apply_never_turns_a_switch_on(tmp_path, at):
    at(host(tmp_path, *BUNDLE, "knowledge-website.yaml"))
    fake = FakeGitHub()
    assert ktl(fake, "apply", "--yes", "--recommended", "--agent", "copilot") == 0
    switches = {e["name"] for c in CATALOGUES.values() for e in load(c)["settings"] if e.get("switch")}
    assert not switches & set(fake.variables)
    assert fake.pages is None and fake.workflow_permissions["can_approve_pull_request_reviews"] is False


def test_enable_website_turns_pages_on_and_refuses_beside_another_publisher(tmp_path, at, capsys):
    at(host(tmp_path, *BUNDLE, "knowledge-website.yaml"))
    fake = FakeGitHub()
    assert ktl(fake, "enable", "website", "--yes") == 0
    assert fake.pages["build_type"] == "workflow" and fake.variables["KNOWLEDGE_WEBSITE_ENABLED"] == "true"

    root = tmp_path / "other"
    root.mkdir()
    at(host(root, *BUNDLE, "knowledge-website.yaml", extra={"docs.yml": "jobs:\n  a:\n    steps:\n      - run: mkdocs gh-deploy --force\n"}))
    fake = FakeGitHub()
    fake.pages = {"build_type": "legacy", "source": {"branch": "gh-pages", "path": "/"}}
    assert ktl(fake, "enable", "website", "--yes") == 1
    out = capsys.readouterr().out
    assert "Pages builds from gh-pages" in out and "docs.yml (gh-deploy)" in out
    assert fake.changes == []


def test_a_domain_host_leaves_the_website_switch_off(tmp_path, at, capsys):
    at(host(tmp_path, *BUNDLE, "knowledge-website.yaml", "knowledge-federation.yaml"))
    fake = FakeGitHub()
    assert ktl(fake, "enable", "website", "--yes") == 1
    assert "knowledge-federation.yaml deploys this repository's site" in capsys.readouterr().err
    fake.variables["KNOWLEDGE_WEBSITE_ENABLED"] = "true"
    assert any("should be off" in t for t in texts(planned(fake), "person"))


def test_enable_sync_review_gives_the_environment_a_reviewer_before_naming_it(tmp_path, at):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub()
    assert ktl(fake, "enable", "sync-review", "--yes") == 0
    review = fake.environments["knowledge-sync-review"]
    assert review["reviewers"] == [101] and review["refs"] == [("branch", "main")]
    assert fake.variables["KNOWLEDGE_SYNC_REVIEW_ENVIRONMENT"] == "knowledge-sync-review"
    paths = [c[1] for c in fake.changes]
    assert paths.index("repos/acme/host/environments/knowledge-sync-review") < paths.index("repos/acme/host/actions/variables")


def test_a_switch_compares_as_a_workflow_does_ignoring_case(tmp_path, at):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub()
    fake.variables["KNOWLEDGE_RELEASE_ENABLED"] = "True"
    assert {s["name"]: s["on"] for s in planned(fake)["switches"]}["release"] is True


def test_enable_asks_a_person_to_confirm_what_github_cannot_see(tmp_path, at, capsys):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub(visibility="private", plan="enterprise")
    assert ktl(fake, "enable", "attest-private") == 1
    assert "Enterprise Cloud" in capsys.readouterr().err
    assert ktl(fake, "enable", "attest-private", "--yes") == 0
    assert fake.variables["KNOWLEDGE_ATTEST_PRIVATE"] == "true"


# This repository


def test_this_repositorys_own_catalogue_describes_its_switches(tmp_path, at):
    """KTL's own repository: the PyPI and docent-eval switches, and the
    release Environment the threat model says waits for a person."""
    at(REPO)
    fake = FakeGitHub(slug="noelmcloughlin/knowledge-trust-ladder")
    fake.environment("release", branches=["main"])
    result = planned(fake)
    switches = {s["name"] for s in result["switches"]}
    assert {"pypi", "docent-eval", "librarian", "website", "release"} <= switches
    assert "Environment pypi: create it, limited to tags v*" in texts(result, "apply")
    reviewer = [f for f in result["findings"] if f["text"] == "Environment release: add noelmcloughlin as required reviewer"]
    assert [f["level"] for f in reviewer] == ["recommended"], "a reviewer on release waits until releases have downstream users"
    assert not [t for t in texts(result) if "OpenSSF Scorecard" in t], "scorecard.yml publishes the score the threat model says it does"


def test_check_strict_names_a_release_environment_without_a_reviewer(tmp_path, at, capsys):
    at(host(tmp_path, *BUNDLE))
    fake = FakeGitHub()
    fake.environment("knowledge-librarian", branches=["main"])
    fake.environment("knowledge-sync", branches=["main"])
    assert ktl(fake, "check") == 0
    fake.environment("release")
    assert ktl(fake, "check") == 0, "a release Environment is the repository's own, so a reviewer is recommended"
    assert ktl(fake, "check", "--strict") == 1
    assert "Environment release: add acme as required reviewer" in capsys.readouterr().out


@pytest.mark.skipif(shutil.which("uv") is None, reason="uv is not installed")
def test_the_command_plans_on_python_3_9(tmp_path):
    """The package claims Python 3.9, the python3 RHEL 9 includes."""
    script = """
import sys
from ktl import cli, gh

class Quiet:
    def call(self, method, path, body=None):
        if path == "repos/acme/host":
            return 200, {"full_name": "acme/host", "visibility": "public", "default_branch": "main", "owner": {"login": "acme", "type": "User"}}
        if path == "user":
            return 200, {"login": "acme", "id": 1}
        return 404, {"message": "Not Found"}

    def current_repo(self, cwd):
        return "acme/host"

args = cli.build_parser().parse_args(["gh", "plan", "--role", "domain"])
sys.exit(gh.main(args, github=Quiet()))
"""
    run = subprocess.run(
        [shutil.which("uv"), "run", "--no-project", "--python", "3.9", "python", "-c", script],
        cwd=tmp_path, env=dict(os.environ, PYTHONPATH=str(REPO / "src")), capture_output=True, text=True,
    )
    assert run.returncode == 0, run.stderr
    assert "Environment knowledge-federation: create it, limited to main and tags v*" in run.stdout
