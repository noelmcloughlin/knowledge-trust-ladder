# A host whose content is Agent Skills

This page is for the **librarian** in a repository that holds Agent Skills: folders with a `SKILL.md` whose frontmatter has a `name` and a `description`, as the [Agent Skills specification](https://agentskills.io/specification) defines them. Such a host may be a collection of skills, a library that includes skills in its package, or a project that keeps a few beside its code. [bootstrap.md](bootstrap.md) sends you here on the first run, and the *Miss* handling in SKILL.md sends you here on a later one.

## Which skills are the host's own

Derive a concept for each skill the host authors, and leave out two kinds:

- **Installed skills**: anything under `.agents/skills/` or `.claude/skills/`, and any skill a `skills-lock.json` names. Another project wrote them, and the host runs them.
- **Vendored skills**: a `SKILL.md` inside a dependency, under `.venv/`, `node_modules/` or a `site-packages/` folder.

A concept may say that one of the host's skills needs an installed skill. It never describes an installed or vendored skill as the host's own.

## What a skill's concept holds

Give each authored skill one `Playbook` concept, with `genre: how-to`. It holds the claims a reader asks about and the facts `SKILL.md` has no field for:

- what the skill is for and when to use it, from its `description`, carried as the source states it;
- what it needs, from `compatibility`, `allowed-tools` and its `scripts/`;
- how it relates to the host's other skills: `dependsOn` for one it needs first or calls, `references` for one it points a reader to;
- where a source says so, the concepts it follows, through `derivedFrom`: a policy, a glossary term, a recorded decision.

The procedure stays in `SKILL.md`. An agent loads it from there when the skill starts, and a copy in the bundle would only drift from it.

Cite `SKILL.md`, and only the other files a claim depends on. A skill's folder changes often, and each file a concept cites puts the concept on the work list whenever it changes.

## A skill the repository deprecates

When a skill's `SKILL.md`, or the host's changelog, says the skill is deprecated, write that in the concept as a fact, with that source under `sources`. A concept that describes a deprecated skill truthfully is still current, so `status` stays as it is. `status: deprecated` is the curator's verdict that a concept no longer holds, and only ktl-curator writes it.

## A miss the skill's own description should have prevented

A reader's *Miss* sometimes names one of the host's skills as where the answer was found. When that skill's `description` does not mention what the reader asked, an agent choosing among the host's skills would not have picked it either. Fix the concept's `description` as for any *Miss*.

Then name the skill and what readers asked in a `handoff` line for the reviewer. A skill's `description` is what agents choose skills by, and only a person changes it. Use the hand-off rather than a `question`: a question sets the concept to draft, though its claims still hold. In a live session, say it to the person instead.
