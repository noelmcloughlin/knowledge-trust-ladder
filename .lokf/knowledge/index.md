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
* [Open the knowledge bundle in Obsidian](playbooks/open-bundle-in-obsidian.md) - How a knowledge bundle meets an Obsidian vault: two vaults, the workshop someone keeps and the bundle opened as its own through the `knowledge_bundle` doorway, what Obsidian does with the link on each host, and why the bundle is never a real folder inside a vault.
* [The docent in Microsoft 365 Copilot](playbooks/docent-in-m365-copilot.md) - How a person gets ktl-docent-m365, the docent packed with a snapshot of the bundle as a Microsoft 365 Copilot custom skill, from a release or by building it, adds it to a declarative agent, checks the first answer and keeps it current, what to do when a step fails, and why only the read-only roles go there.
* [ktl-librarian skill](playbooks/ktl-librarian-skill.md) - Recurring procedure that scrapes the host repository, derives and maintains the .lokf/ concepts and their typed relations, audits the bundle, and hands off for human review.
* [ktl-curator skill](playbooks/ktl-curator-skill.md) - A human curator's assistant: it reports what needs a person's attention, then records that person's confirm, correct, retire or send-back verdicts in the bundle's frontmatter.
* [ktl-docent skill](playbooks/ktl-docent-skill.md) - The reader's side: it answers questions from the bundle first, with each concept's trust label, falls back to the repository when the bundle cannot answer, and records misses and disagreements for the librarian.
* [Knowledge sources](playbooks/knowledge-sources.md) - Map of the repository locations this bundle was derived from, and how to re-check each on a future refresh.
* [Contributing](playbooks/contributing.md) - How to work on the skills: no build step, the local checks to run before opening a pull request, the role boundary a change must respect, and which pages now hold the release and signing detail.
* [Releasing](playbooks/releasing.md) - How a release happens: `semantic-release.yml` computes the version from Conventional Commits and promotes `CHANGELOG.md` on merge to `main` but never tags, and a maintainer's `publish.yml` run checks that version against the changelog, lets `gh skill publish` create the tag and release, and dispatches `knowledge-release.yaml` to attach the bundle and Copilot zips.
* [Repository validation](playbooks/repository-validation.md) - What CI checks on every pull request and weekly: the repository contract, the Agent Skills spec, shell and workflow linting, the install smoke test, and Markdown, link and spelling checks.
* [ktl-prose skill](playbooks/ktl-prose-skill.md) - The librarian's copy editor. It rewords the body of a concept an agent wrote, in plain English, before a person confirms it, changing the wording and never a fact or a frontmatter byte, and its script proves that only the wording changed.

# References

* [LOKF specification](references/lokf-specification.md) - The canonical definition of the Linked Open Knowledge Format - a semantic profile of OKF binding every field, type, and relationship to schema.org, DCAT, and PROV-O.
* [OKF specification (v0.2)](references/okf-specification.md) - Google's Open Knowledge Format - a folder of Markdown concept files with YAML frontmatter, requiring only `type`, plus the v0.2 provenance, trust, and lifecycle families.
* [Agent Skills specification](references/agent-skills-specification.md) - The specification defining a skill directory - a required SKILL.md with name/description frontmatter, plus optional scripts/, references/, and assets/.
* [LOKF toolkit (lokf on PyPI)](references/lokf-toolkit.md) - The lokf Python package, which validates, converts and serves a LOKF bundle and is the dependency the scaffolded .lokf/pyproject.toml declares.
* [LinkML](references/linkml.md) - The schema-modelling language LOKF is written in, and the generator suite that turns a schema into JSON Schema, Pydantic models, SHACL shapes, docs, and OWL.
* [gh skill (GitHub CLI)](references/gh-skill-cli.md) - The GitHub CLI command group that installs, pins, and publishes agent skills from GitHub repositories; the publish path this repository uses for releases.
* [Open Skills CLI (npx skills)](references/open-skills-cli.md) - The vendor-neutral installer for agent skills, supporting GitHub, git, and local sources with repeatable --skill and --agent selection.

# Glossary

* [LOKF](glossary/lokf.md) - The Linked Open Knowledge Format, the semantic profile of OKF this bundle is written in, which binds every field to a public vocabulary so the bundle projects to RDF.
* [OKF](glossary/okf.md) - The Open Knowledge Format, Google's specification for a folder of Markdown concept files with YAML frontmatter, which LOKF profiles.
* [Knowledge bundle](glossary/knowledge-bundle.md) - The `.lokf/knowledge` directory - containing one-concept-per-file Markdown, carrying a semantic header, that is simultaneously human-readable documentation and a queryable graph.
* [Trust label](glossary/trust-label.md) - The plain words the skills use for how far a concept has been checked, derived from its frontmatter on every read and never stored.
* [The pen](glossary/the-pen.md) - The name for `knowledge-apply.sh`, the only way ktl-librarian writes the bundle: it applies the operations in `.lokf/patch.yaml`, stamps `generated`, keeps the index in step, and refuses a `human:` actor.
* [Docent](glossary/docent.md) - A museum's name for a guide, and the role that answers a reader's questions from the bundle, says how far each answer has been checked, and writes nothing in the bundle.
* [Desk](glossary/desk.md) - The README's word, in its library terms, for the place where a role does its work with the bundle: the registrar is `knowledge-apply.sh` at the librarian's desk, and `knowledge-report.sh` at the reader's and the curator's.
* [Registrar](glossary/registrar.md) - The person in a museum who keeps the collection's records, and Knowledge Trust Ladder's fifth role, which programs play: the `lokf` toolkit, the gate `knowledge-registrar.yaml`, the pen and the report script.
* [Sidecar](glossary/sidecar.md) - `.lokf/`, the folder beside a project's code that holds the bundle and the tooling that checks it, kept out of the project's build; also the role, and the ktl-sidecar skill, that installs it.
* [Accession](glossary/accession.md) - A museum's word for an item added to its collection, which the README's registrar keeps documented with its provenance filed; in the bundle, each concept added is one.

# Policies

* [AI covenant](policies/ai-covenant.md) - Community norms for AI use - contributors own what they submit regardless of tooling, AI must not post autonomously in discussions, AI co-authorship in commit messages is discouraged, and a repository-owned agent (e.g. ktl-librarian) must commit under a bot or maintainer identity with no trailer either way and land only as a human-reviewed PR.
* [Security policy](policies/security.md) - How to report a vulnerability privately, supported versions, and a surface table (what executes here, what guards it) that links to the shared threat model instead of restating it.
* [Threat model](policies/threat-model.md) - The security design the three KTL repositories share, kept in one place so each SECURITY.md can link to it: repository hardening, the human:-attribution gate on a verified event, and the prompt-injection guard for each input path that reads content it did not author.
* [Versioning policy](policies/versioning.md) - One repository-level semantic version covering all five skills, released together under a single tag, with patch, minor and major decided by Conventional Commits.
* [Code of conduct](policies/code-of-conduct.md) - Contributor Covenant v2.1: the behavioural standards for issues, pull requests and discussions, and how to report unacceptable behaviour.

# Explanation

* [Why four skill roles rather than one skill](explanation/why-four-roles.md) - Why the work is split into four skills, sidecar, librarian, curator and docent, named for the library and museum professions and run first in order and then as a loop, beside a fifth role that is not a skill (the registrar) and a fifth skill that is not a role (ktl-prose).
* [Why a registrar role, and why it is not a skill](explanation/why-a-registrar-role.md) - What the registrar does, keeping every bundle record in order and every confirmation tied to a person, and why no person has to do it: the `lokf` toolkit, CI's `knowledge-registrar.yaml`, the `knowledge-apply.sh` pen at the librarian's desk, and two optional Obsidian plugins for a desk with no CI.
* [Why the skills live in their own repository](explanation/why-a-distribution-repository.md) - Why the five skills are published from one installable repository: three install routes, one tag for all of them, one changelog, and a bundle of its own that the docent answers from.
* [Hosts and doorways - where the bundle's real folder lives](explanation/hosts-and-doorways.md) - Why the bundle is `.lokf/knowledge`, one real folder on every host, with `knowledge_bundle` beside it as a link for people and folder pickers; what the visible layout tried and why it was retired; and what a shared folder that is not a vault may still do by hand.
* [Three lines of defence - where each role sits, and what an auditor can check](explanation/three-lines-of-defence.md) - The librarian, curator, registrar, sidecar and docent placed in the IIA's Three Lines Model, for whoever adopts KTL: who owns a claim, what a machine checks, what a person can examine afterwards, the four limits on that evidence, what the critics page answers, and what remains to do and who does it.
* [When the built-in vocabulary stops fitting - domain schemas](explanation/domain-schemas.md) - How a bundle in a specialised or regulated domain goes beyond LOKF's core classes: the signs a domain schema is due, a LinkML schema importing LOKF's and checked with `lokf validate --schema`, reusing a domain's own vocabulary such as the AI Risk Ontology, the Microsoft 365 identity shape held in reserve, and who raises, decides and applies it.
* [What Knowledge Trust Ladder is for, and what it is not](explanation/intended-uses.md) - A draft placeholder for a reader's question no source settles: which uses Knowledge Trust Ladder is meant for, such as DevSecOps or technology governance, and which it is not. The README states the purpose and names no use case or non-goal.
* [WikiSkill's loop and Knowledge Trust Ladder](explanation/wikiskill.md) - The WikiSkill paper (Tang et al., 2026) set beside Knowledge Trust Ladder (KTL) part by part, as `docs/wikiskill.md` does: the same loop with different parts, what the paper found and what KTL does with each finding, where each design puts programs, models and people, and what the paper does not settle.
