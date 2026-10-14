# Knowledge Trust Ladder in a skills repository

> [!NOTE]
> For anyone deciding whether to install Knowledge Trust Ladder (KTL) in a repository whose content is Agent Skills. What KTL took from the two papers on skills is in [docs/wikiskill.md](wikiskill.md) and [docs/skillwiki.md](skillwiki.md).

A skills repository holds Agent Skills: folders with a `SKILL.md`, and often `scripts/`, `references/` and `assets/`. It may be a collection, such as this repository or `anthropics/skills`, a library that includes skills in its package, or a project that keeps a few skills beside its code. Below, *the bundle* is the corpus KTL keeps in `.lokf/knowledge/`.

## The answer

KTL helps with the knowledge around a repository's skills, and leaves the skills as they are.

- **What it adds.** The bundle says what each skill is for, how the skills relate, why each says what it says, and which of those claims a named person checked. The docent answers "which skill do I run first?" from the bundle and says how far each concept it used has been checked. KTL keeps `SKILL.md` as the source and never edits or converts it.
- **What it leaves to evaluations.** Whether a skill works is a question for an evaluation: WikiSkill's validation score, or SkillWiki's verifiers in a harness. KTL's checks cover the form and the provenance of what the bundle says.
- **What it costs.** In a repository whose skills change every week, a person's confirmation is overtaken by the next derivation within days. The label then reads *edited since a person last confirmed it* until a person confirms again.

## How KTL handles a skills repository

- **The librarian's first run maps Agent Skills folders.** Each skill the host authors gets one `Playbook` concept. It says what the skill is for, what it needs and how it relates to the other skills, which no `SKILL.md` field can hold. ktl-librarian's `references/agent-skills.md` says what such a concept holds, and the procedure stays in `SKILL.md`. The concept cites `SKILL.md` and only the files a claim depends on.
- **It leaves other projects' skills out.** It derives no concept for an installed skill: one a `skills-lock.json` names, or a copy under `.agents/skills/` or `.claude/skills/` whose `SKILL.md` names another repository as its home. It asks a person about any other skill it finds there, since a host may keep project skills of its own in `.claude/skills/`. It derives none for a vendored skill in a dependency, and a skill template gets no concept of its own.
- **A skill's own deprecation is a fact, not a verdict.** When the repository deprecates a skill, the concept says so, with its source. `status: deprecated` stays the curator's verdict that a concept no longer holds.
- **A weak description reaches a person.** When a reader's miss names a skill whose `description` does not mention what the reader asked, the librarian fixes the concept's description and names the skill in its hand-off to the reviewer. Only a person changes a `SKILL.md`.
- **The threat model names the case.** In a skills repository every source is a set of instructions for an agent. The librarian reads each as data and writes only through the pen, and only the person reviewing a pull request catches an instruction that shapes what a concept says ([threat model](threat-model.md)).

## What two runs showed

**This repository** has kept a bundle since 9 September 2026. Each of its six skills has a `Playbook` concept that summarises the `SKILL.md` at a third to a half of its length and adds typed relations to the other skills. The ktl-librarian concept cites eleven sources, so almost any commit to the skill puts it back on the work list, and each of its three confirmations was overtaken by the next derivation. Five of the eight captured docent answers in [docs/examples/docent.md](examples/docent.md) are about the skills. Collections move at different speeds: in `anthropics/skills`, most `SKILL.md` files changed one to four times in the ten months to October 2026, so there most confirmations would hold.

**`anthropics/skills`**, at commit `683bc88` of 5 October 2026. A fresh agent ran ktl-sidecar and ktl-librarian on a clone, following only the skills' own pages, and a second fresh agent answered ten questions as ktl-docent. The questions, and the skill each one expects, were written before either run.

- The sidecar took four minutes and the librarian's first run nineteen. It derived 27 draft concepts: one `Playbook` for each of the 19 skills, and eight more for the source map, two how-tos, two references, a glossary term, a licensing policy and an explanation. It left out the stray and installed skills on purpose, and every check passed on the first apply.
- No skill names another, so no concept relates one skill to another, and six rely on the licensing policy instead. The librarian asked which licence applies to `doc-coauthoring`, which carries none, and noted that `skills/pdf/SKILL.md` names two companion files in capitals the files do not use.
- The docent named the expected skill every time, in five and a half minutes. Every concept read *nobody has checked this yet, still a draft*, so it opened each skill's `SKILL.md` before it answered, as its rules say for an unchecked concept.
- A control agent given only the skills' `name` and `description` answered the same ten questions correctly in 28 seconds. On this collection the bundle did not route better than the descriptions already do. What it added was the detail the descriptions leave out: that `brand-guidelines` is Anthropic's alone, file and script names, and Slack's size limits. On a collection whose descriptions were weaker, or a project whose concepts carry relations the frontmatter cannot hold, the bundle has more to add.
- The run found gaps in KTL's own pages. ktl-librarian's `references/agent-skills.md` now covers a skill template, needs stated outside the frontmatter, and project skills under `.claude/skills/`. The docent's rules still have no row for "which skill should I use?", and a skill's concept and a how-to share the `Playbook` class, which the domain schema below would settle.

## What remains to do

These are designs, not features. Each would extend KTL's checks from what the bundle says to whether a host's skills still work. That is a condition check, the work a museum gives its conservator, who examines objects and writes condition reports without cataloguing or authenticating them. If KTL takes these on, they belong to a new role, not to the librarian.

- **A record of skill runs.** A feedback kind for a skill run, recorded by the agent that ran the skill, would give WikiSkill's raw layer KTL's guards. It would accept only a skill name the host holds and a short failure signature, keep the entry's text from every session but the librarian's, and leave the librarian its only consumer.
- **A trigger test.** The retrieval score could be run over the host's skill descriptions, which is what an agent chooses skills by. It needs task prompts paired with the skill each should start, where the ledger holds the questions readers asked.
- **An `AgentSkill` domain schema.** A LinkML class for the six Agent Skills frontmatter fields would let `lokf validate` check a skill's concept against them, and let the docent tell a skill's concept from a how-to.
- **OKF's attested computation for a skill's scripts.** LOKF's `AttestedComputation` is a sanctioned recipe whose run returns a receipt that an attester compares with it. A skill's deterministic scripts could be described that way.
- **A place for a fault in the host's own text.** The docent found a guide that names a script without its file extension. Its feedback records gaps in the bundle, so it had nowhere to record a fault in a skill.
- **The excerpt check.** The `sources[].excerpt` field proposed for LOKF 0.9.0 would let a program check the passage a concept relies on. Once it is released, the work list could tell an edit to that passage from an edit elsewhere in the skill's file.

## Sources

- Tang, L., Rashtchian, C., Ferng, C.-S., Tomkins, A., Juan, D.-C. and Vu, T. (2026). WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution. arXiv:2608.27454. <https://arxiv.org/abs/2608.27454>
- Huang, D. et al. (2026). SkillWiki: A Living Knowledge Infrastructure for Agent Skills. arXiv:2606.16523. <https://arxiv.org/abs/2606.16523>
- The Agent Skills specification. <https://agentskills.io/specification>
- `anthropics/skills` at commit `683bc88`, the clone the run used. <https://github.com/anthropics/skills/tree/683bc88e56f3e09ba94f7055977f3d3aa499f202>
