# Playbooks

* [ktl-sidecar skill](ktl-sidecar-skill.md) - Procedure that creates a .lokf/ sidecar - tooling, docs, a dummy skeleton, and the knowledge_bundle doorway link beside it - from bundled templates, or repairs a single missing sidecar file, then hands off to ktl-librarian.
* [Open the knowledge bundle in Obsidian](open-bundle-in-obsidian.md) - two vaults: the one you keep, and the bundle opened through the `knowledge_bundle` doorway.
* [The docent in Microsoft 365 Copilot](docent-in-m365-copilot.md) - the docent and a bundle snapshot as a Copilot custom skill.
* [ktl-librarian skill](ktl-librarian-skill.md) - Recurring procedure that scrapes the host repository, derives and maintains the .lokf/ concepts and their typed relations, audits the bundle, and hands off for human review.
* [ktl-curator skill](ktl-curator-skill.md) - a human curator's assistant; verdicts, never facts.
* [ktl-docent skill](ktl-docent-skill.md) - answers from the bundle and records what it lacked.
* [Knowledge sources](knowledge-sources.md) - Map of the repository locations this bundle was derived from, and how to re-check each on a future refresh.
* [Contributing](contributing.md) - local checks and the role boundary a change must respect.
* [Releasing](releasing.md) - the maintainer-gated publish path.
* [Repository validation](repository-validation.md) - what CI enforces on every pull request.
* [ktl-prose skill](ktl-prose-skill.md) - The librarian's copy editor. It rewords the body of a concept an agent wrote, in plain English, before a person confirms it, changing the wording and never a fact or a frontmatter byte, and its script proves that only the wording changed.
