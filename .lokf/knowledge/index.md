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

* [ktl-sidecar skill](playbooks/ktl-sidecar-skill.md) - Procedure that creates a .lokf/ sidecar - tooling, docs, a dummy skeleton, and the knowledge_bundle doorway link beside it - from bundled templates, or repairs a single missing sidecar file, then hands off to ktl-librarian.
* [Open the knowledge bundle in Obsidian](playbooks/open-bundle-in-obsidian.md) - two vaults: the workshop someone keeps, and the bundle opened as its own vault through the root `knowledge_bundle` link.
* [The docent in Microsoft 365 Copilot](playbooks/docent-in-m365-copilot.md) - the docent packed with a bundle snapshot as a Copilot custom skill: from a release zip or the sidecar's builder, into a declarative agent.
* [ktl-librarian skill](playbooks/ktl-librarian-skill.md) - Recurring procedure that scrapes the host repository, derives and maintains the .lokf/ concepts and their typed relations, audits the bundle, and hands off for human review.
* [ktl-curator skill](playbooks/ktl-curator-skill.md) - a human curator's assistant; verdicts, never facts.
* [ktl-docent skill](playbooks/ktl-docent-skill.md) - answers from the bundle and records what it lacked.
* [Knowledge sources](playbooks/knowledge-sources.md) - Map of the repository locations this bundle was derived from, and how to re-check each on a future refresh.
* [Contributing](playbooks/contributing.md) - local checks and the role boundary a change must respect.
* [Releasing](playbooks/releasing.md) - the maintainer-gated publish path.
* [Repository validation](playbooks/repository-validation.md) - what CI enforces on every pull request.
* [ktl-prose skill](playbooks/ktl-prose-skill.md) - The librarian's copy editor. It rewords the body of a concept an agent wrote, in plain English, before a person confirms it, changing the wording and never a fact or a frontmatter byte, and its script proves that only the wording changed.

# References

* [LOKF specification](references/lokf-specification.md)
* [OKF specification (v0.2)](references/okf-specification.md)
* [Agent Skills specification](references/agent-skills-specification.md)
* [LOKF toolkit (lokf on PyPI)](references/lokf-toolkit.md)
* [LinkML](references/linkml.md)
* [gh skill (GitHub CLI)](references/gh-skill-cli.md)
* [Open Skills CLI (npx skills)](references/open-skills-cli.md)

# Glossary

* [LOKF](glossary/lokf.md) - the semantic profile of OKF this bundle is written in.
* [OKF](glossary/okf.md) - Google's Markdown-and-frontmatter format that LOKF profiles.
* [Knowledge bundle](glossary/knowledge-bundle.md) - the `.lokf/knowledge` directory: documentation and a queryable graph at once.
* [Trust label](glossary/trust-label.md) - the plain words for how far a concept has been checked.

# Policies

* [AI covenant](policies/ai-covenant.md)
* [Security policy](policies/security.md)
* [Threat model](policies/threat-model.md) - The security design the three LOKF repositories share: repository hardening, the human:-attribution gate on a verified event, and the prompt-injection guard for each input path that reads content it did not author - carried once here so each SECURITY.md can link instead of restate.
* [Versioning policy](policies/versioning.md)
* [Code of conduct](policies/code-of-conduct.md)

# Explanation

* [Why four skill roles rather than one skill](explanation/why-four-roles.md)
* [Why a registrar role, and why it is not a fifth skill](explanation/why-a-registrar-role.md) - The job none of the four skills does - keeping bundle records well-formed and every confirmation tied to a person - and why it is done by tooling (the `lokf` toolkit, CI, and two optional Obsidian plugins) rather than by an agent.
* [Why the skills live in their own repository](explanation/why-a-distribution-repository.md)
* [Hosts and doorways - where the bundle's real folder lives](explanation/hosts-and-doorways.md) - one real folder, a doorway link beside it on every host, and why the visible layout was retired.
* [Three lines of defence - where each role sits, and what an auditor can check](explanation/three-lines-of-defence.md) - Placing the librarian, curator, registrar, sidecar and docent roles in The Institute of Internal Auditors' Three Lines Model, with a diagram - who owns a claim, what a machine checks, and what a person can examine afterwards - the four limits on what that evidence shows, a pointer to the critics page, and what remains to do and who does it. The critics page quotes the model's critics (preliminary research) and says which of their points a LOKF bundle answers and what kind of gap each remainder is. Written for whoever adopts a bundle, not about this repository's own arrangements.
* [When the built-in vocabulary stops fitting - domain schemas](explanation/domain-schemas.md) - the signs a domain schema is due, how it extends LOKF's classes, and reusing a domain's own vocabulary such as the AI Risk Ontology for AI governance.
* [What Knowledge Trust Ladder is for, and what it is not](explanation/intended-uses.md) - a draft placeholder carrying a reader's question no source yet settles.
* [What WikiSkill says about a knowledge bundle](explanation/wikiskill.md) - The WikiSkill paper (Tang et al., 2026) read against this design: what the two share, what the skills took from it, and what the paper can and cannot say about determinism.
