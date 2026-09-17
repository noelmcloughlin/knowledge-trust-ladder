---
type: Playbook
id: https://lokf-agent-skills.example/knowledge/playbooks/repository-validation
title: Repository validation
description: What CI checks on every pull request and weekly - the repository contract, the Agent Skills spec, shell and workflow linting, the install smoke test, and Markdown/link/spelling checks.
genre: how-to
resource: .github/workflows/validate.yml
generated:
  by: process:lokf-librarian
  at: "2026-09-17T17:30:00Z"
status: draft
references:
  - https://lokf-agent-skills.example/knowledge/references/agent-skills-specification
  - https://lokf-agent-skills.example/knowledge/references/open-skills-cli
  - https://lokf-agent-skills.example/knowledge/playbooks/contributing
verified:
- by: process:lokf-librarian
  at: "2026-09-17T17:30:00Z"
---

# Overview

`validate.yml` runs five jobs on every pull request, every push to `main`,
weekly, and on demand. `validate-skills` runs `scripts/validate-repository.sh` -
thirteen numbered checks: exactly four skill directories with a case-correct
`SKILL.md` in each, frontmatter `name` matching its directory and (check 3b,
added 2026-09-17) a `compatibility` field of at most 500 characters naming
what the skill needs, no duplicate `SKILL.md`, every relative Markdown link
under `skills/` resolving (fenced examples excluded), ShellCheck-clean
scripts, every stated LOKF class count agreeing with
`lokf-librarian/SKILL.md` Rule 3 (and with
`lokf-curator/references/trust-fields.md`'s own enumeration), the sidecar
layout tests, the paths the two sibling plugin repositories deep-link into by
URL still existing - and, when those siblings are cloned beside this repo,
that the list of them is complete - `CONTRIBUTING.md` and `SECURITY.md` each
staying under their own word budget (1000 and 900, check 10, extended
2026-09-14 when `SECURITY.md`'s design moved to `docs/threat-model.md`),
(check 11, added 2026-09-14) this repository's copies of the registrar gate,
the five sidecar scripts and `.lokf/.gitattributes` staying byte-identical to
their templates, with `knowledge-conventions.sh` shown to pass on this
bundle, to fail on a synthetic bundle breaking each of its ten rules (a
vanished `resource`, a `revision` naming no commit, a duplicate `id`, an
upper-case path, a byte order mark, a missing frontmatter block, an event
spelt with a quoted key or a tag, and the first four - six of which (2, 3, 4,
7, 9, 10), since 2026-09-17, it delegates to `knowledge-conventions.py`
through `uv run`, a real YAML parse in place of grep and awk, proven on the
layouts that used to slip: a multi-line flow item with an unquoted `at`, a
number for an `at`, a block that does not parse, reported on one line, and a
list where a mapping should be, while a second librarian event in a body
code fence is not counted), to read a CRLF bundle as it reads LF, to read a
bundle reached through a link, and without `uv` to run its own rules and say
which it skipped; (check 12, added 2026-09-17) `knowledge-preflight.sh`
ending on its summary line here, on a bare directory, and warning on a CRLF
bundle, counting a linked bundle, reading `commit.gpgsign = yes` as signing
on, warning when the conventions script's Python half is missing beside it,
stopping on one line under `sh` (as the other two scripts do), and every
line it can print as missing or a warning having a row on
`lokf-sidecar/references/prerequisites.md`; and (check 13, same day)
`knowledge-provenance.sh` passing a confirmation signed by the curator on
file - with a GPG key, a GPG signing subkey, or an SSH key - and failing an
unsigned one, an unknown id, an id the gate cannot look up (which it used to
skip), a wrong key of either kind and an id's own key registered in the same
range as their confirmation, while another curator's key landing alongside
passes; and, since events are read whole from the frontmatter, against every
parent of a commit and keyed by the concept's `id` rather than found as
added `by:` lines, failing a re-dated confirmation nobody signed, an unsigned
flow-style event, a flow-style human `generated` record and an event a merge
adds that neither side held, while passing the same re-date signed by its
curator, a confirmed concept that merely moved, an example event in a body
code fence and a merge that brings in a signed confirmation - all with
throwaway keys. Then
`gh skill publish --dry-run` runs.

`lint-scripts` runs ShellCheck on every script; `lint-workflows` runs
`actionlint`, pointed by path at this repository's workflows and at the two
workflow templates that get copied into other repositories (it would
otherwise look only under `.github/workflows/`), and (added 2026-09-14) a check that every `uses:`
in this repository's workflows and those templates names a commit SHA or
image digest rather than a floating tag or branch; `smoke-test` installs all
four skills from the checkout into a throwaway consumer repo via
`scripts/smoke-test-install.sh`; `validate-markdown` runs markdownlint,
lychee, and codespell.

The weekly schedule exists because link rot, an upstream `gh skill` change, or
install-path drift would otherwise surface only on the next incidental pull
request.
