---
type: Explanation
id: https://knowledge-trust-ladder.example/knowledge/explanation/skills-repositories
title: Knowledge Trust Ladder in a skills repository
description: "Whether to install Knowledge Trust Ladder (KTL) in a repository whose content is Agent Skills, as `docs/skills-repositories.md` answers: what it adds (the knowledge around the skills), what it leaves to evaluations (whether a skill works), what it costs when skills change weekly, a run on anthropics/skills, how the librarian maps skills, and what remains to do."
genre: explanation
resource: docs/skills-repositories.md
sources:
- resource: docs/skills-repositories.md
- resource: skills/ktl-librarian/references/agent-skills.md
about:
- https://knowledge-trust-ladder.example/knowledge/glossary/knowledge-bundle
relatedTo:
- https://knowledge-trust-ladder.example/knowledge/explanation/wikiskill
- https://knowledge-trust-ladder.example/knowledge/explanation/skillwiki
- https://knowledge-trust-ladder.example/knowledge/playbooks/ktl-librarian-skill
- https://knowledge-trust-ladder.example/knowledge/references/agent-skills-specification
generated:
  by: process:ktl-librarian
  at: "2026-10-12T00:29:45Z"
status: draft
---

# Overview

`docs/skills-repositories.md` is for anyone deciding whether to install KTL in a repository whose content is Agent Skills: folders with a `SKILL.md`, and often `scripts/`, `references/` and `assets/`. Such a repository may be a collection, a library that includes skills in its package, or a project that keeps a few skills beside its code. The page reads two papers against KTL's design: WikiSkill, which [WikiSkill's loop](wikiskill.md) covers, and SkillWiki, which [SkillWiki's skill governance](skillwiki.md) covers.

# The answer

KTL helps with the knowledge around a repository's skills, and leaves the skills as they are.

- **What it adds.** The bundle says what each skill is for, how the skills relate, why each says what it says, and which of those claims a named person checked. KTL keeps `SKILL.md` as the source and never edits or converts it.
- **What it leaves to evaluations.** Whether a skill works is a question for an evaluation. KTL's checks cover the form and the provenance of what the bundle says.
- **What it costs.** In a repository whose skills change every week, the next derivation overtakes a person's confirmation within days. The label then reads *edited since a person last confirmed it* until a person confirms again.

# Evidence

The page draws on this repository, which has kept a bundle since 9 September 2026. Each of its five skills has a `Playbook` concept. Every confirmation of the ktl-librarian concept was overtaken by the next derivation.

It also reports a run on a clone of `anthropics/skills` at commit `683bc88`. The librarian derived 27 draft concepts, and `lokf validate --check-refs` and the conventions script passed on the first apply. The docent then named the expected skill for each of ten questions. A control agent given only the skills' `name` and `description` answered the same ten correctly in 28 seconds, where the docent took five and a half minutes. So on that collection the bundle did not route better than the descriptions do, and what it added was the detail the descriptions leave out.

# How KTL handles a skills repository

- The librarian's first run gives each skill the host authors one `Playbook` concept, as ktl-librarian's `references/agent-skills.md` says.
- It derives no concept for an installed skill from another project, or for a vendored skill in a dependency. A skill template gets no concept of its own.
- A skill's own deprecation is a fact the concept states with its source. `status: deprecated` stays the curator's verdict.
- When a reader's miss names a skill whose `description` does not mention what the reader asked, the librarian fixes the concept's description and names the skill in its hand-off. Only a person changes a `SKILL.md`.

# What remains to do

The page lists designs, not features. Each would extend KTL from what the bundle says to whether a host's skills still work:

- a record of skill runs;
- a trigger test over skill descriptions;
- an `AgentSkill` domain schema;
- OKF's attested computation for a skill's scripts;
- a place for a fault in the host's own text;
- the excerpt check, once LOKF 0.9.0 is released.

If KTL takes these on, they belong to a new role, not to the librarian.
