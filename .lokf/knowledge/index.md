---
lokf_version: "0.2"
okf_version: "0.2"
base_iri: https://knowledge-trust-ladder.example/knowledge/
context: https://w3id.org/lokf/context.jsonld
title: Knowledge Trust Ladder Knowledge Bundle
description: Four Agent Skills that turn a repository's scattered knowledge into a maintained, trusted LOKF knowledge bundle.
license: https://creativecommons.org/licenses/by/4.0/
publisher:
  type: Person
  id: https://knowledge-trust-ladder.example/knowledge/person/noel-mcloughlin
  name: Noel McLoughlin
---

# Knowledge Trust Ladder Knowledge Bundle

A [LOKF](https://lokf.nolan-nichols.com) knowledge base for Knowledge Trust Ladder. Every Markdown file under `knowledge/` is one concept; together they form a queryable knowledge graph, derived from this repository's code and docs.

# Playbooks

* [ktl-sidecar skill](playbooks/ktl-sidecar-skill.md) - Procedure that creates a .lokf/ sidecar, tooling, docs, a dummy skeleton, and the knowledge_bundle doorway link beside it, from bundled templates, or repairs a missing or broken sidecar file, then hands off to ktl-librarian.
* [Open the knowledge bundle in Obsidian](playbooks/open-bundle-in-obsidian.md) - How a knowledge bundle meets an Obsidian vault - two vaults, the workshop someone already keeps and the bundle opened as its own vault through the root-level knowledge_bundle doorway - with what Obsidian does with a link on each host, verified against Obsidian 1.13.7's file reconciler, and why the bundle is never laid down as a real folder inside a vault.
* [The docent in Microsoft 365 Copilot](playbooks/docent-in-m365-copilot.md) - How a person gets ktl-docent-m365, the docent packed with a snapshot of the bundle as a Microsoft 365 Copilot custom skill, from a release or by building it with `.lokf/m365/knowledge-m365.sh`, adds it to a declarative agent, checks the first answer, and keeps it current; what to do when a step fails, and why only the read-only roles go there.
* [ktl-librarian skill](playbooks/ktl-librarian-skill.md) - Recurring procedure that scrapes the host repository, derives and maintains the .lokf/ concepts and their typed relations, audits the bundle, and hands off for human review.
* [ktl-curator skill](playbooks/ktl-curator-skill.md) - A human curator's assistant - reports what needs a person's attention, then records that person's confirm/correct/retire/send-back verdicts into the bundle's frontmatter.
* [ktl-docent skill](playbooks/ktl-docent-skill.md) - The reader's side - answers questions from the bundle first with each concept's trust label, falls back to the repository deliberately, and records misses and disagreements for the librarian.
* [Knowledge sources](playbooks/knowledge-sources.md) - Map of the repository locations this bundle was derived from, and how to re-check each on a future refresh.
* [Contributing](playbooks/contributing.md) - How to work on the skills - no build step, the local checks to run before opening a pull request, the role boundary a change must respect, and where the release and signing detail now lives.
* [Releasing](playbooks/releasing.md) - semantic-release.yml computes the version and promotes CHANGELOG.md on merge to main but never tags, folding into a still-unpublished section rather than doubling it; a workflow_dispatch run of publish.yml then validates that version against the promoted changelog, re-checks the contract and spec, lets gh skill publish create the tag and release, and dispatches knowledge-release.yaml to attach the bundle zip.
* [Repository validation](playbooks/repository-validation.md) - What CI checks on every pull request and weekly - the repository contract, the Agent Skills spec, shell and workflow linting, the install smoke test, and Markdown/link/spelling checks.
* [ktl-prose skill](playbooks/ktl-prose-skill.md) - The librarian's copy editor. It rewords the body of a concept an agent wrote, in plain English, before a person confirms it, changing the wording and never a fact or a frontmatter byte, and its script proves that only the wording changed.

# References

* [LOKF specification](references/lokf-specification.md)
* [OKF specification (v0.2)](references/okf-specification.md)
* [Agent Skills specification](references/agent-skills-specification.md)
* [LOKF toolkit (lokf on PyPI)](references/lokf-toolkit.md) - The Python package that validates, converts, and serves a LOKF bundle - the dependency the scaffolded .lokf/pyproject.toml declares.
* [LinkML](references/linkml.md) - The schema-modelling language LOKF is written in, and the generator suite that turns a schema into JSON Schema, Pydantic models, SHACL shapes, docs, and OWL.
* [gh skill (GitHub CLI)](references/gh-skill-cli.md) - The GitHub CLI command group that installs, pins, and publishes agent skills from GitHub repositories; the publish path this repository uses for releases.
* [Open Skills CLI (npx skills)](references/open-skills-cli.md)

# Glossary

* [LOKF](glossary/lokf.md) - The Linked Open Knowledge Format, the semantic profile of OKF this bundle is written in, which binds every field to a public vocabulary so the bundle projects to RDF.
* [OKF](glossary/okf.md) - Google's Markdown-and-frontmatter format that LOKF profiles.
* [Knowledge bundle](glossary/knowledge-bundle.md) - the `.lokf/knowledge` directory: documentation and a queryable graph at once.
* [Trust label](glossary/trust-label.md) - The plain words the skills use for how far a concept has been checked, derived from its frontmatter on every read and never stored.

# Policies

* [AI covenant](policies/ai-covenant.md)
* [Security policy](policies/security.md) - How to report a vulnerability privately, supported versions, and a surface table (what executes here, what holds it) that links to the shared threat model instead of restating it.
* [Threat model](policies/threat-model.md) - The security design the three LOKF repositories share: repository hardening, the human:-attribution gate on a verified event, and the prompt-injection guard for each input path that reads content it did not author - carried once here so each SECURITY.md can link instead of restate.
* [Versioning policy](policies/versioning.md) - One repository-level semantic version covering all five skills, released together under a single tag, with patch, minor and major decided by Conventional Commits.
* [Code of conduct](policies/code-of-conduct.md) - Contributor Covenant v2.1 - the behavioural standards for issues, pull requests, and discussions, and how to report unacceptable behaviour.

# Explanation

* [Why four skill roles rather than one skill](explanation/why-four-roles.md) - Why the work is split into four skills, sidecar, librarian, curator and docent, named for the library and museum professions and run first in order and then as a loop, beside a fifth role that is not a skill (the registrar) and a fifth skill that is not a role (ktl-prose).
* [Why a registrar role, and why it is not a fifth skill](explanation/why-a-registrar-role.md) - What the registrar does, keeping every bundle record in order and every confirmation tied to a person, and why no person has to do it: the `lokf` toolkit, CI's `knowledge-registrar.yaml`, the `knowledge-apply.sh` pen at the librarian's desk, and two optional Obsidian plugins for a desk with no CI.
* [Why the skills live in their own repository](explanation/why-a-distribution-repository.md) - Why the five skills are published from one installable repository: three install routes, one tag for all of them, one changelog, and a bundle of its own that the docent answers from.
* [Hosts and doorways - where the bundle's real folder lives](explanation/hosts-and-doorways.md) - The bundle is `.lokf/knowledge`, one real folder on every host, and `knowledge_bundle` beside it is a link - the doorway for people and folder pickers. Why there is one layout, what the visible layout of 2026-09-12 tried and why it was retired the next day, and what a shared folder that is not a vault may still do by hand.
* [Three lines of defence - where each role sits, and what an auditor can check](explanation/three-lines-of-defence.md) - Placing the librarian, curator, registrar, sidecar and docent roles in The Institute of Internal Auditors' Three Lines Model, with a diagram - who owns a claim, what a machine checks, and what a person can examine afterwards - the four limits on what that evidence shows, a pointer to the critics page, and what remains to do and who does it. The critics page quotes the model's critics (preliminary research) and says which of their points a LOKF bundle answers and what kind of gap each remainder is. Written for whoever adopts a bundle, not about this repository's own arrangements.
* [When the built-in vocabulary stops fitting - domain schemas](explanation/domain-schemas.md) - How a bundle in a specialised or regulated domain goes beyond LOKF's core classes - the signs a domain schema is due, a LinkML schema importing LOKF's and checked with `lokf validate --schema`, reusing a domain's existing vocabulary (the AI Risk Ontology for AI governance), the Microsoft 365 identity shape held in reserve for a Copilot curator, and who raises, decides and applies it.
* [What Knowledge Trust Ladder is for, and what it is not](explanation/intended-uses.md) - a draft placeholder carrying a reader's question no source yet settles.
* [WikiSkill's loop and the bundle's ladder](explanation/wikiskill.md) - The WikiSkill paper (Tang et al., 2026) set beside this design part by part, as `docs/wikiskill.md` does: the same loop with different parts, what the paper found and what a bundle does with each finding, where each design puts programs, models and people, and what the paper does not settle.
