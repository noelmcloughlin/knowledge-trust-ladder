# Examples: a first bundle

One run of the four roles on a repository that had no bundle, following each skill's `SKILL.md` as [Your first bundle](../first-bundle.md) describes. The output is captured, cut only where a line says so. An agent made the run on 2026-11-12 with the skills as this repository held them that day.

The host was a throwaway repository made for the run: a youth club's tool for lending books. It held a README, one Python script (`src/lend.py`), a policy page (`docs/lending-policy.md`) and a list of books (`data/books.csv`).

## 1. "Add a LOKF knowledge bundle to this repository."

The **sidecar** ran its preflight first:

```text
Preflight for /home/.../first-run-host
ok      host         Linux, bash 5.2.21; digest: sha256sum; python3: 3.12
missing bundle       no .lokf/knowledge under /home/.../first-run-host - run ktl-sidecar first
ok      git          bundle not yet committed; history full; core.autocrlf=unset; .lokf/.gitattributes absent
warn    forge        github; no knowledge-registrar.yaml - ktl-sidecar Step 5 lays it down
[one line cut: the login a confirmation would carry]
warn    signing      commit signing off - a curation pull request you open yourself fails the gate (docs/signing-commits.md in knowledge-trust-ladder)
info    curators     no .lokf/curators/ - the forge-free gate skips; only the forge's own gate, if any, checks a confirmation
info    toolkit      uv 0.12.11 (x86_64-unknown-linux-gnu) present; no .lokf/pyproject.toml yet
ok      just         just 1.47.0
[two lines cut: the skills installed on this machine]
info    session      attended (Claude Code): a person can answer item by item
info    network      pypi.org reachable
Preflight: 1 missing, 2 warning(s). Missing disables: every skill but ktl-sidecar.
```

It then copied its templates into `.lokf/`, filled in the project's name and description from the README, added `llms.txt`, one paragraph in the README and the `knowledge_bundle` link, and installed the scripts and the workflows. The repository named no web address of its own, so the bundle's base IRI is the fallback `https://club-library.example/knowledge/`, which the hand-off names as a guess for a person to settle.

```text
$ cd .lokf && just lokf-install && just lokf-validate
uv run lokf validate  knowledge
OK — 2 concepts in knowledge validate against KnowledgeBundle.

$ bash .lokf/scripts/knowledge-preflight.sh | tail -1
Preflight: 0 missing, 1 warning(s).

$ bash .lokf/scripts/knowledge-report.sh health
Confirmed by a person: 0 of 2 · Checked by automation only: 0 · Nobody has checked: 2 · Drafts: 0 · Reopened: 0 · Past review date: 0 · Edited since confirmed: 0 · Retired: 0
```

*The two concepts are the sidecar's dummies. The one warning left is commit signing, which matters only once a person confirms a concept.*

## 2. "Fill the knowledge bundle from this repository."

The **librarian** read the four files and wrote one patch, `.lokf/patch.yaml`: six concepts, one open question, and the removal of the two dummies. The pen refused the first attempt:

```text
$ bash .lokf/scripts/knowledge-apply.sh --dry-run
op 9: services/example-service-b.md: delete needs a log line saying why
refused: 1 finding(s); nothing was written
```

With that line added the pen applied the patch, and the conventions check then failed six log lines:

```text
$ cd .lokf && bash scripts/knowledge-conventions.sh
knowledge/log.md: Added bullet under 2026-11-12 names no concept the bundle holds: the term overdue, from the lending policy. - start it with the concept's title, or link the concept
[five more lines cut, one for each other new concept]
```

Nothing was committed yet, so the librarian put the bundle back as git held it, opened each log line with its concept's title, and applied the patch again:

```text
$ bash .lokf/scripts/knowledge-apply.sh
schema checked: lokf validate accepts every concept this patch writes
OK - 9 operation(s) by process:ktl-librarian at 2026-11-12T13:44:40Z; now run lokf validate --check-refs and knowledge-conventions.sh

$ cd .lokf && just lokf-check-refs
OK — 6 concepts in knowledge validate against KnowledgeBundle. All in-namespace relation targets resolve. No local excerpt to check.

$ bash scripts/knowledge-conventions.sh
OK - knowledge keeps the conventions lokf validate cannot check
```

*Both refusals are the registrar at work: the agent's mistakes were caught by programs before a person saw the bundle.*

## 3. "What in the bundle needs my confirmation?"

The **curator** skill's report starts from `knowledge-report.sh`:

```text
Knowledge bundle report - 2026-11-12 (computed by knowledge-report.sh; nothing here is stored)
Confirmed by a person: 0 of 6 · Checked by automation only: 0 · Nobody has checked: 6 · Drafts: 6 · Reopened: 0 · Past review date: 0 · Edited since confirmed: 0 · Retired: 0

Worth ten minutes today: 5 of 6 waiting
1. Club Library command-line tool (Service) - still a draft, with an open question; 1 other concept relies on this - src/lend.py
2. Books list (Dataset) - nobody has checked this yet, still a draft; 2 other concepts rely on this - data/books.csv
3. Lending policy (Policy) - nobody has checked this yet, still a draft; 2 other concepts rely on this - docs/lending-policy.md
4. Overdue (GlossaryTerm) - nobody has checked this yet, still a draft - docs/lending-policy.md
5. Knowledge sources (Playbook) - nobody has checked this yet, still a draft - README.md

[the list of all six concepts cut]

Open questions a person left, still waiting: none
Open questions the librarian left: 1
- services/lend-cli.md (2026-11-12, process:ktl-librarian): the lending policy allows one renewal of 14 days, and `src/lend.py` has no renew command; is a renewal recorded by hand?

[the lines that read "none" cut]

Relied on by other concepts: 3
- datasets/books.md (2)
- policies/lending-policy.md (2)
- services/lend-cli.md (1)
```

*The review session that follows is not captured here. It records a person's own answers, and no person sat in this run, so no concept was confirmed.*

## 4. "How long can a member keep a book?"

The **docent** read the bundle's `index.md`, picked the lending policy from its one-line description, took the concept's label from its own copy of the report script, and opened the source for the two numbers.

> A loan lasts 21 days. It may be renewed once, for 14 more days, unless another member is waiting for the book. I checked both numbers in `docs/lending-policy.md`.

```text
From the bundle:
- Lending policy (policies/lending-policy.md) - nobody has checked this yet, still a draft
Checked at source: docs/lending-policy.md (21 days, 14 more days)
```

*The answer is right, and the label still says that nobody has vouched for the concept it rests on. That is the difference a curator's confirmation makes.*
