---
type: Playbook
id: https://lokf-agent-skills.example/knowledge/playbooks/lokf-librarian-skill
title: lokf-librarian skill
description: Recurring procedure that scrapes the host repository, derives and maintains the .lokf/ concepts and their typed relations, audits the bundle, and hands off for human review.
genre: how-to
resource: skills/lokf-librarian/SKILL.md
generated:
  by: process:lokf-librarian
  at: "2026-09-14T07:47:56Z"
status: draft
dependsOn:
- https://lokf-agent-skills.example/knowledge/playbooks/lokf-sidecar-skill
about:
  - https://lokf-agent-skills.example/knowledge/glossary/knowledge-bundle
definedBy:
- https://lokf-agent-skills.example/knowledge/references/agent-skills-specification
references:
  - https://lokf-agent-skills.example/knowledge/references/lokf-specification
  - https://lokf-agent-skills.example/knowledge/references/okf-specification
verified:
- by: process:lokf-librarian
  at: "2026-09-16T09:10:00Z"
- by: human:noelmcloughlin
  at: "2026-09-09T18:36:00Z"
stale_after: 2027-09-09
---

# Overview

Runs **often**, including on a schedule. It carries the seven LOKF Golden Rules
(OKF-first; the bundle-root semantic header and `base_iri` authority test; the
type vocabulary - fifteen classes - plus the Diátaxis `genre` facet; typed
relationships over bare links; core field-to-ontology mapping; trust,
provenance and lifecycle; permissiveness), then four sections: scrape and
build, audit, hand off for review, and the scheduled task.

It deals in **facts about the repository, never verdicts about truth**: it may
record that it re-checked a concept against its source (`verified` by
`process:lokf-librarian`), but only [lokf-curator](lokf-curator-skill.md)
writes a `human:` confirmation. Concepts it creates start as `status: draft`,
and a claim it cannot settle gets an `## Open questions` section instead of a
guess.

Two things it now leaves alone by rule (added 2026-09-12): the Obsidian
affordances LOKF Registrar may write into a bundle - a marker-delimited
`<!-- lokf:related -->` block in a concept body and a `diataxis.md` Map of
Content (`type: Document`, `generated.by: lokf-registrar/<version>`, or
`lokf-enforcer/<version>` from a build before the plugin's rename), which it
never edits, lists, audits as orphans, or counts - and the bundle's second
name: `.lokf/knowledge` is the real folder lokf-sidecar lays down, with a
`knowledge_bundle` link beside it, but a host rearranged by hand may have the
link the other way round, so it addresses the bundle by the tools' name and
names both paths when scoping a diff or a PR.

The tooling-version check (rule 6) now runs **only in interactive
sessions**: the scheduled workflow's wrapper permits edits solely under
`.lokf/knowledge/`, `knowledge_bundle/` and `.lokf/feedback.md`, so a
scheduled run that touched `.lokf/pyproject.toml` would fail the whole run
closed rather than land a partial change - added 2026-09-12 as part of a
security-hardening pass that also added a second, independent enforcement
of that same path boundary in `knowledge-librarian.yaml`'s privileged
`publish` job (re-derived from the proposed patch on a clean checkout,
never trusting the `refresh` job's own check alone), plus harden-runner and
`.git/config`/`.git/hooks/` snapshot-and-restore around the agent call in
the wrapper script. See `policies/security.md` for the detail.

**Extending the vocabulary (added 2026-09-14).** Rule 3's fifteen classes are
deliberately small and portable. A domain needing more of its own gets a
LinkML schema that imports LOKF's and validates with `lokf validate --schema
<file>`, which the toolkit has always accepted - no loosening of Rule 7.
`lokf-librarian/references/domain-schema.md` is the recipe: a pinned copy of
the core schema, the domain schema, frontmatter naming the class exactly, and
the flag wired into the justfile and both workflow templates. Rule 3 reads
that wiring back - where the justfile passes `--schema`, that schema's
`Concept` descendants are part of the vocabulary, and a record names the
subclass. The tooling-version step (rule 6) refreshes the pinned copy.
`lokf-curator/references/domain-schemas.md` covers when; this covers how.
