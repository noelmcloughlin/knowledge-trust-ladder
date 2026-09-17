# Security Policy

*This file is a policy, not a threat model. It says how to report, what executes here, and what holds each surface, a line or two each that links to where the reasoning lives - a workflow header, a skill's own guardrail, or the shared [threat model](docs/threat-model.md) - and `bash scripts/validate-repository.sh` holds it to a word budget so it stays that way.*

## Reporting a vulnerability

Use GitHub's [private vulnerability reporting](https://github.com/noelmcloughlin/lokf-agent-skills/security/advisories/new), not a public issue or a pull request. Say which file is affected and why it is exploitable, and, for a template that gets copied into other repositories, whether the issue is in the template itself or appears only after a consumer customizes it. One person maintains this repository: expect a first reply in days, not hours, and no bounty.

## Supported versions

Only the latest published tag receives fixes. A security fix ships as a patch release and is noted in [CHANGELOG.md](CHANGELOG.md).

## What executes here

This repository is mostly Markdown. Three things in it run, or are run by other systems, and are the attack surface.

| Surface | What holds it |
| --- | --- |
| `skills/lokf-sidecar/templates/` - four scripts and two workflows the sidecar **copies into other repositories**, which run there | The template's own design: two jobs so the agent never meets a write token, a `publish` job that confines the patch to the bundle and refuses a `human:` claim, and a preflight and a forge-free gate that only read git and gpg. [Prompt-injection guards](docs/threat-model.md#prompt-injection-guards). |
| `.github/workflows/` - `validate.yml` on every pull request; `knowledge-registrar.yaml` and `knowledge-librarian.yaml`, this repository's own copies of the templates; `semantic-release.yml` and `publish.yml`, which write to `main` behind the `release` Environment | Actions pinned to commit SHAs, `permissions: {}` at the top of every workflow, harden-runner in audit mode. Each workflow's header comment says why it is shaped as it is. [Repository hardening](docs/threat-model.md#repository-hardening). |
| The four skills' `SKILL.md` and `references/` prose - **executed by whichever LLM agent runs it**, here and in every consumer | Each skill's guardrail for its own input path: content the agent did not author is quoted, never followed, and only an authenticated person's verdict is recorded as one. [Prompt-injection guards](docs/threat-model.md#prompt-injection-guards) and [Human attribution](docs/threat-model.md#human-attribution-human-is-a-claim-not-a-credential). |

A skill's `Scope:` line is prose, not a permission. Run interactively, an agent has whatever access your harness grants it, and only the scheduled workflow enforces its scope, so review what the agent changed before you commit. [Interactive use](docs/threat-model.md#interactive-use-scope-is-advisory-not-enforced).

## Not covered

- A compromised runner, upstream action or agent harness: this is a baseline, not a sandbox. Report a finding in one anyway, with scope and reproduction.
- Whether a bundle is *true*. The gate proves who vouched, not what they read; [AI_COVENANT.md](AI_COVENANT.md) sets the human-accountability rules.
- A reader's own words to lokf-docent. That boundary belongs to the agent harness, not to a Markdown file.
