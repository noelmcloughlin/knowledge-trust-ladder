---
lokf_version: "0.2"
okf_version: "0.2"
base_iri: https://knowledge-trust-ladder.example/knowledge/
context: https://w3id.org/lokf/context.jsonld
title: Knowledge Trust Ladder Knowledge Bundle
description: Four Agent Skills that turn a repository's scattered knowledge into a maintained, trusted LOKF knowledge bundle, and a fifth that keeps its prose plain.
license: https://creativecommons.org/licenses/by/4.0/
publisher:
  type: Person
  id: https://knowledge-trust-ladder.example/knowledge/person/noel-mcloughlin
  name: Noel McLoughlin
---


# Playbooks

* [ktl-sidecar skill](playbooks/ktl-sidecar-skill.md) - The procedure that creates a .lokf/ sidecar from bundled templates, tooling, docs, a dummy skeleton and the knowledge_bundle doorway link, or repairs one missing file, then hands off to ktl-librarian.
* [ktl-librarian skill](playbooks/ktl-librarian-skill.md) - The recurring procedure that scrapes the host repository, derives and maintains the .lokf/ concepts and their typed relations, audits the bundle, writes in plain English, and hands off for a person's review. Facts, never verdicts.
* [ktl-prose skill](playbooks/ktl-prose-skill.md) - The librarian's copy editor. It rewords the body of a concept an agent wrote, in plain English, before a person confirms it, changing the wording and never a fact or a frontmatter byte, and its script proves that only the wording changed.
* [ktl-curator skill](playbooks/ktl-curator-skill.md) - A human curator's assistant. It reports what needs a person's attention, then records that person's confirm, correct, retire or send-back verdicts into the bundle's own frontmatter, only in a live session and only under an authenticated identity.
* [ktl-docent skill](playbooks/ktl-docent-skill.md) - The reader's side. It answers questions from the bundle first, with each concept's trust label, verifies exact values at the source, falls back to the repository only when the bundle has no answer, and records misses and disagreements for the librarian without ever opening the feedback file.
* [Open the knowledge bundle in Obsidian](playbooks/open-bundle-in-obsidian.md) - How a knowledge bundle meets an Obsidian vault: two vaults, the workshop someone already keeps and the bundle opened as its own vault through the root-level knowledge_bundle link, which plugins go in it, and what each host does with the link.
* [The docent in Microsoft 365 Copilot](playbooks/docent-in-m365-copilot.md) - How a person gets ktl-docent-m365, the docent packed with a snapshot of the bundle as a Microsoft 365 Copilot custom skill, from a release or by building it, adds it to a declarative agent, and keeps it current.
* [Knowledge sources](playbooks/knowledge-sources.md) - The map of the repository locations this bundle was derived from, the class each yields, and how to re-check each one on a future refresh.
* [Contributing](playbooks/contributing.md) - How to work on the skills: no build step, the local checks to run before opening a pull request, the role boundary a change must respect, the code of conduct and the AI covenant, and what maintainers do to release.
* [Releasing](playbooks/releasing.md) - How the three repositories release: semantic-release.yml computes the version and promotes CHANGELOG.md on a merge to main but never tags; a maintainer runs publish.yml by hand; the siblings sync their templates and pin from the new tag.
* [Repository validation](playbooks/repository-validation.md) - What continuous integration checks on every pull request and weekly: the repository contract, the Agent Skills specification, shell and workflow linting, the install smoke test, Markdown linting, link checking and spelling.

# Policies

* [AI covenant](policies/ai-covenant.md) - Community norms for AI use: contributors own what they submit regardless of tooling, AI must not post autonomously in discussions, AI co-authorship in commit messages is discouraged, and repository-owned agents land every change as a reviewed pull request.
* [Code of conduct](policies/code-of-conduct.md) - The Contributor Covenant, version 2.1: the behavioural standards for issues, pull requests and discussions, and how to report unacceptable behaviour.
* [Security policy](policies/security.md) - How to report a vulnerability privately, which versions receive fixes, the four things in this repository that execute and what holds each, and what the policy does not cover.
* [Threat model](policies/threat-model.md) - The security design the three LOKF repositories share: scope is advisory in interactive use, repository hardening, the human: attribution gate on a verified event, the prompt-injection guard for each skill's input path, and what it does not cover.
* [Versioning policy](policies/versioning.md) - One repository-level semantic version covers all five skills, released together under a single tag, with patch, minor and major computed from Conventional Commits rather than hand-picked.

# Glossary

* [Knowledge bundle](glossary/knowledge-bundle.md) - The `.lokf/knowledge` folder: one Markdown file per concept, with a semantic header on the root index.md, which people read as documentation and tools query as a graph.
* [LOKF](glossary/lokf.md) - The Linked Open Knowledge Format: a semantic profile of OKF that binds every field, type and relationship to a public vocabulary, so a bundle projects losslessly to JSON-LD and RDF.
* [OKF](glossary/okf.md) - The Open Knowledge Format, Google Cloud's specification for a folder of Markdown concept files with YAML frontmatter, which LOKF profiles.
* [Trust label](glossary/trust-label.md) - The plain words the skills use for how far a concept has been checked. Each label is computed from the concept's frontmatter on every read and never stored.

# References

* [Agent Skills specification](references/agent-skills-specification.md) - The specification that defines a skill directory: a required SKILL.md with name and description frontmatter, plus optional scripts/, references/ and assets/ folders.
* [gh skill (GitHub CLI)](references/gh-skill-cli.md) - The GitHub CLI command group that installs, pins and publishes agent skills from GitHub repositories. It is the publish path this repository's releases use.
* [LinkML](references/linkml.md) - The schema-modelling language LOKF is written in, and the generator suite that turns a schema into JSON Schema, Pydantic models, SHACL shapes, documentation and OWL.
* [LOKF specification](references/lokf-specification.md) - The canonical definition of the Linked Open Knowledge Format: a semantic profile of OKF that binds every field, type and relationship to schema.org, DCAT and PROV-O terms.
* [LOKF toolkit (lokf on PyPI)](references/lokf-toolkit.md) - The Python package that validates, converts and serves a LOKF bundle. It is the dependency the scaffolded .lokf/pyproject.toml declares.
* [OKF specification (v0.2)](references/okf-specification.md) - Google Cloud's Open Knowledge Format: a folder of Markdown concept files with YAML frontmatter that requires only `type`, plus the v0.2 provenance, trust and lifecycle fields LOKF makes queryable.
* [Open Skills CLI (npx skills)](references/open-skills-cli.md) - The vendor-neutral installer for agent skills, `npx skills add`, which takes a GitHub repository, a git URL or a local path and repeatable --skill selections.

# Explanation

* [When the built-in vocabulary stops fitting: domain schemas](explanation/domain-schemas.md) - How a bundle in a specialised or regulated domain goes beyond LOKF's core classes: the signs that a domain schema is due, a LinkML schema that imports LOKF's, what it costs, and how the curator, the team and the librarian divide the work.
* [Hosts and doorways: where the bundle's real folder lives](explanation/hosts-and-doorways.md) - The bundle is `.lokf/knowledge`, one real folder on every host, and `knowledge_bundle` beside it is a link, the doorway for people and folder pickers. Why there is one layout, and what each kind of host does with the link.
* [What Knowledge Trust Ladder is for, and what it is not](explanation/intended-uses.md) - What the README says the skills are for, a repository's knowledge kept as a catalogued and checked collection, and the reader's question the sources do not settle: which fields of use, such as DevSecOps or technology governance, it fits.
* [Three lines of defence: where each role sits, and what an auditor can check](explanation/three-lines-of-defence.md) - How the librarian, curator, registrar, sidecar, docent and ktl-prose fit the Institute of Internal Auditors' Three Lines Model: who is accountable for a claim, what a machine checks, what can be examined afterwards, and what the model's critics say.
* [Why the skills live in their own repository](explanation/why-a-distribution-repository.md) - Why the five skills are published from one installable repository with three install routes, one tag for all of them and one changelog, and why this repository also keeps a bundle of its own.
* [Why a registrar role, and why it is not a skill](explanation/why-a-registrar-role.md) - The job none of the skills does, keeping bundle records well-formed and every confirmation tied to a person, and why tooling does it: the lokf toolkit, the knowledge-registrar.yaml gate, and the KTL Registrar plugin in Obsidian.
* [Why four skill roles rather than one skill](explanation/why-four-roles.md) - Why the work is split into four skills named for library and museum professions, sidecar, librarian, curator and docent, which run first in order and then as a loop, and why the fifth skill, ktl-prose, is a helper and not a role.
