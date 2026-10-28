---
type: Explanation
id: https://w3id.org/ktl/knowledge/explanation/skills-repositories
title: Knowledge Trust Ladder in a skills repository
description: "Whether to install Knowledge Trust Ladder (KTL) in a repository whose content is Agent Skills, as `docs/skills-repositories.md` answers: what it adds (the knowledge around the skills), what it leaves to evaluations (whether a skill works), what it costs when skills change weekly, this repository's six skills and a run on anthropics/skills, how the librarian maps skills, and what remains to do."
genre: explanation
resource: docs/skills-repositories.md
sources:
  - resource: docs/skills-repositories.md
    id: docs-skills-repositories.md
  - resource: skills/ktl-librarian/references/agent-skills.md
about:
  - https://w3id.org/ktl/knowledge/glossary/knowledge-bundle
relatedTo:
  - https://w3id.org/ktl/knowledge/explanation/wikiskill
  - https://w3id.org/ktl/knowledge/explanation/skillwiki
  - https://w3id.org/ktl/knowledge/playbooks/ktl-librarian-skill
  - https://w3id.org/ktl/knowledge/references/agent-skills-specification
generated:
  by: process:ktl-librarian
  at: "2026-10-28T00:35:16Z"
verified:
  - by: human:noelmcloughlin
    at: "2026-10-13T01:02:36Z"
  - by: process:ktl-librarian
    at: "2026-10-26T20:05:58Z"
status: draft
---

# Overview

`docs/skills-repositories.md` is for anyone deciding whether to install KTL in a repository whose content is Agent Skills: folders with a `SKILL.md`, and often `scripts/`, `references/` and `assets/`. Such a repository may be a collection, such as this repository or `anthropics/skills`, a library that includes skills in its package, or a project that keeps a few skills beside its code. What KTL took from the two papers on skills is in [WikiSkill](wikiskill.md) and [SkillWiki](skillwiki.md).

# The answer

KTL helps with the knowledge around a repository's skills, and leaves the skills as they are.

- **What it adds.** The bundle says what each skill is for, how the skills relate, why each says what it says, and which of those claims a named person checked. The docent answers "which skill do I run first?" from the bundle and says how far each concept it used has been checked. KTL keeps `SKILL.md` as the source and never edits or converts it.

- **What it leaves to evaluations.** Whether a skill works is a question for an evaluation: WikiSkill's validation score, or SkillWiki's verifiers in a harness. KTL's checks cover the form and the provenance of what the bundle says.

- **What it costs.** In a repository whose skills change every week, the next derivation overtakes a person's confirmation within days. The label then reads *edited since a person last confirmed it* until a person confirms again.

# Evidence

The page reports two runs. This repository has kept a bundle since 9 September 2026. Each of its six skills has a `Playbook` concept that summarises the `SKILL.md` at a third to a half of its length and adds typed relations to the other skills. The ktl-librarian concept cites eighteen sources, so almost any commit to the skill puts it back on the work list, and each of its four confirmations was overtaken by the next derivation.[^docs-skills-repositories.md] Five of the eight captured docent answers in `docs/examples/docent.md` are about the skills. Collections move at different speeds: in `anthropics/skills`, most `SKILL.md` files changed one to four times in the ten months to October 2026, so there most confirmations would hold.

The second run used a clone of `anthropics/skills` at commit `683bc88` of 5 October 2026. The librarian derived 27 draft concepts: one `Playbook` for each of the 19 skills, and eight more. Every check passed on the first apply. The docent then named the expected skill for each of ten questions, in five and a half minutes. Every concept read *nobody has checked this yet, still a draft*, so the docent opened each skill's `SKILL.md` before it answered, as its rules say for an unchecked concept. A control agent given only the skills' `name` and `description` answered the same ten correctly in 28 seconds. So on that collection the bundle did not route better than the descriptions do, and what it added was the detail the descriptions leave out. On a collection whose descriptions were weaker, or a project whose concepts carry relations the frontmatter cannot hold, the bundle has more to add.

The run found gaps in KTL's own pages. ktl-librarian's `references/agent-skills.md` now covers a skill template, needs stated outside the frontmatter, and project skills under `.claude/skills/`. The docent's rules still have no row for "which skill should I use?", and a skill's concept and a how-to share the `Playbook` class, which the `AgentSkill` domain schema would settle.

# How KTL handles a skills repository

- The librarian's first run gives each skill the host authors one `Playbook` concept, as ktl-librarian's `references/agent-skills.md` says. The concept says what the skill is for, what it needs and how it relates to the other skills, which no `SKILL.md` field can hold. The procedure stays in `SKILL.md`, and the concept cites `SKILL.md` and only the files a claim depends on.

- It derives no concept for an installed skill: one a `skills-lock.json` names, or a copy under `.agents/skills/` or `.claude/skills/` whose `SKILL.md` names another repository as its home. It asks a person about any other skill it finds there, since a host may keep project skills of its own in `.claude/skills/`. In a scheduled run, ktl-librarian's `references/agent-skills.md` has it leave such a skill out and name it in the hand-off. It derives none for a vendored skill in a dependency, and a skill template gets no concept of its own.

- A skill's own deprecation is a fact the concept states with its source. `status: deprecated` stays the curator's verdict that a concept no longer holds.

- When a reader's miss names a skill whose `description` does not mention what the reader asked, the librarian fixes the concept's description and names the skill in its hand-off. Only a person changes a `SKILL.md`.

- In a skills repository every source is a set of instructions for an agent. The librarian reads each as data and writes only through the pen, and only the person reviewing a pull request catches an instruction that shapes what a concept says ([threat model](../policies/threat-model.md)).

# What remains to do

The page lists designs, not features. Each would extend KTL's checks from what the bundle says to whether a host's skills still work:

- a record of skill runs;

- a trigger test over skill descriptions;

- an `AgentSkill` domain schema;

- OKF's attested computation for a skill's scripts;

- a place for a fault in the host's own text;

- the excerpt check, once the `sources[].excerpt` field proposed for LOKF 0.9.0 is released.

That is a condition check, the work a museum gives its conservator rather than its librarian. If KTL takes these on, they belong to a new role.

[^docs-skills-repositories.md]: docs/skills-repositories.md, *What two runs showed*
