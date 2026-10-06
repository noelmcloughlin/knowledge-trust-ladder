# Knowledge Trust Ladder in a skills repository

> [!NOTE]
> For anyone deciding whether to install Knowledge Trust Ladder (KTL) in a repository whose content is Agent Skills. It reads two papers on skills against this design: WikiSkill (Google Research), which [docs/wikiskill.md](wikiskill.md) reads in full, and SkillWiki (Huang et al.), which [docs/skillwiki.md](skillwiki.md) reads. The names are close, and the papers are different.

A skills repository holds Agent Skills: folders with a `SKILL.md`, and often `scripts/`, `references/` and `assets/`. It may be a collection, such as this repository or `anthropics/skills`. It may be a library that includes skills in its package, or a project that keeps a few skills beside its code. Below, *KTL* is this design, *the bundle* is the corpus it keeps in `.lokf/knowledge/`, and *LOKF* is the format.

## The answer

KTL helps with the knowledge around a repository's skills, and leaves the skills as they are.

- **What it adds.** The bundle says what each skill is for, how the skills relate, why each says what it says, and which of those claims a named person checked. The docent, a museum's name for a guide, answers "which skill do I run first?" from the bundle and says how far each concept it used has been checked. KTL keeps `SKILL.md` as the source and never edits or converts it.
- **What it leaves to evaluations.** Whether a skill works is a question for an evaluation: WikiSkill's validation score, or SkillWiki's verifiers in a harness. KTL's checks cover the form and the provenance of what the bundle says.
- **What it costs.** In a repository whose skills change every week, a person's confirmation is overtaken by the next derivation within days. The label then reads *edited since a person last confirmed it* until a person confirms again.

## WikiSkill's wiki, kept by KTL

WikiSkill keeps its skills as Agent Skills folders. Each holds a `SKILL.md` and a `PURPOSE.md`, "which maps the skill back to the motivating Wiki patterns that inspired its creation or modification". The wiki is kept apart from the skills, and the agent that uses the skills does not write it. In the paper's ablation, on one model across four benchmarks, the wiki is worth fifteen points on average to the agent that proposes skill changes.

KTL has the same parts. The librarian writes the bundle, the docent only reads it, and a named person's verdict stands where WikiSkill has a score. The difference is in what the corpus holds. The bundle holds claims derived from the repository, and WikiSkill's wiki holds patterns drawn from the agent's runs. Holding those patterns as well needs a record of skill runs, which is listed under what remains.

## What a skills repository needs, and where each design puts it

| Need | WikiSkill | SkillWiki | KTL |
| --- | --- | --- | --- |
| Choosing the skill | `name` and `description`; the study injects skills into the prompt "to isolate skill quality and avoid confounding effects from skill retrieval" | the retriever ranks skills by words and by lifecycle state | the docent answers from the bundle, with labels; the retrieval score tests the bundle's index, not skill descriptions |
| Relations between skills | not described in the paper | typed edges, among them `depends_on`, `composes_with`, `conflicts_with` and `replaces` | typed relations, checked by `--check-refs` and projected to RDF; a retired concept links its successor in `log.md` |
| Why a skill says what it says | `PURPOSE.md` points to wiki patterns | each skill's `provenance` names its sources | a skill's concept cites its files, and `derivedFrom` names the concepts it follows where a source says so |
| Evidence from use | traces become wiki patterns | success counts, reflection memory and failure signatures | readers' misses and disagreements |
| Governed change | a proposer, a validation gate, and `skill-impact.md` | snapshot, structured diff, review, release and rollback | the pen, the registrar's gate and the curator govern the bundle; `SKILL.md` changes go through the repository's own review |
| Who stands behind it | a score | a promotion the record attributes to the repository | a named person, tied to their forge account and, with LOKF 0.9.0's `revision`, to the commit they checked |
| Retirement and pruning | no pruning of the wiki, by the authors' account | eight stored states, ending in *Deprecated* and *Archived* | `status`, `stale_after` and the librarian's orphan sweep |

## Evidence from this repository

This repository is a skills repository that has kept a bundle since 9 September 2026.

- **One concept per skill.** Each of the five skills has a `Playbook` concept. It summarises the `SKILL.md` at a third to a half of its length, and adds typed relations to the other skills, which no `SKILL.md` field can hold. The Agent Skills frontmatter has six fields: `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`.
- **Churn.** Since 9 September, `skills/ktl-librarian/SKILL.md` has changed in 13 commits on `main`, and its concept in 13. A person confirmed that concept on 9 September, 26 September and 3 October, and each confirmation was overtaken by the next derivation, so it reads *edited since a person last confirmed it*. The other four skill concepts are drafts that automation alone has checked. The concept cites eleven sources: the skill's page and five of its references, a workflow, three scripts and `CHANGELOG.md`. So almost any commit to the skill, and every release, puts it back on the work list.
- **Use.** Five of the eight captured docent answers in [docs/examples/docent.md](examples/docent.md) are about the skills: which to run first, how two relate, how to change one, the CLI version they need, and what comes next.

Collections move at different speeds. In `anthropics/skills`, most `SKILL.md` files changed one to four times in the ten months to October 2026, and `claude-api` changed 24 times in seven. In a collection like that, most confirmations hold.

## A run on `anthropics/skills`

A fresh agent ran ktl-sidecar and ktl-librarian on a clone of `anthropics/skills` at commit `683bc88` (5 October 2026), following only the skills' own pages. The clone also held a stray installed skill under `.agents/skills/`, and the three KTL skills installed under `.claude/skills/`. A second fresh agent then answered ten questions as ktl-docent. The questions, and the skill each one expects, were written before either run.

### The librarian's run

- **Time.** The sidecar took four minutes, and the librarian's first run nineteen.
- **What the librarian derived.** It derived 27 concepts, all drafts: one `Playbook` for each of the 19 skills, and eight more. Those are the source map, how-tos for installing the skills and for creating one, the plugin marketplace and the Agent Skills specification as references, a glossary term, a licensing policy and an explanation of the repository.
- **What it left out.** It derived no concept for the stray skill, for the installed KTL skills, or for the skills inside the toolkit's own virtual environment. The source map lists each of them as left out on purpose.
- **What the checks said.** `lokf validate --check-refs` and the conventions script passed on the first apply, and the pen refused nothing.
- **What the skills share.** No skill names another, so no concept relates one skill to another. Six concepts rely on the licensing policy instead.
- **What it found in the host.** It asked which licence applies to `doc-coauthoring`, which carries neither a licence file nor a `license` field. Its hand-off noted that `skills/pdf/SKILL.md` names two companion files in capitals the files themselves do not use.
- **What it found in KTL.** It listed nineteen places where the skills' pages were unclear or did not fit a repository of skills. Three were in `references/agent-skills.md`: a skill template, needs stated outside the frontmatter, and project skills a host keeps under `.claude/skills/`. That page now covers all three. The rest concern the sidecar's first install.

### The docent's run

- **What the docent answered.** It answered the ten questions in five and a half minutes, and named the expected skill every time. For the brand question it named `theme-factory` beside `brand-guidelines`, because the bundle says `brand-guidelines` applies Anthropic's own brand. Every concept it used read *nobody has checked this yet, still a draft*. So it opened each skill's `SKILL.md` before it answered, as its rules say for an unchecked concept. It fell back to the repository for no question and recorded no gap.
- **What the bundle added.** Its index entries closely restate each skill's own `description`, which is the text a skill router already reads. The concept bodies added what the descriptions leave out: file names, Slack's size limits, and the scope of `brand-guidelines`. Until a person confirms concepts, the bundle chooses which file to open, and the docent still opens it.
- **What the docent found in KTL.** Its rules have no row for "which skill should I use?", the commonest question in such a repository. A skill's concept and a how-to also share the `Playbook` class, so the type cannot tell them apart.
- **What the run does not show.** No run answered the same questions from the skills' own descriptions alone. So it shows that the bundle routes correctly, not how much better than the descriptions it routes.

## How KTL handles a skills repository

- **The librarian's first run maps Agent Skills folders.** Its sweep gives each skill the host authors one `Playbook` concept. The concept holds what the skill is for, what it needs and how it relates to the other skills. ktl-librarian's `references/agent-skills.md` says what such a concept holds, and the procedure stays in `SKILL.md`. The concept cites `SKILL.md` and only the files a claim depends on.
- **It leaves other projects' skills out.** It derives no concept for an installed skill: one a `skills-lock.json` names, or a copy under `.agents/skills/` or `.claude/skills/` whose `SKILL.md` names another repository as its home. It asks a person about any other skill it finds there, since a host may keep project skills of its own in `.claude/skills/`. It derives none for a vendored skill in a dependency, under `.venv/`, `node_modules/` or `site-packages/`. A skill template gets no concept of its own.
- **A skill's own deprecation is a fact, not a verdict.** When the repository deprecates a skill, the concept says so, with its source. `status: deprecated` stays the curator's verdict that a concept no longer holds.
- **A weak description reaches a person.** When a reader's miss names a skill whose `description` does not mention what the reader asked, the librarian fixes the concept's description and names the skill in its hand-off to the reviewer. Only a person changes a `SKILL.md`.
- **The threat model names the case.** In a skills repository every source is a set of instructions for an agent. The librarian reads each as data and writes only through the pen, and only the person reviewing a pull request catches an instruction that shapes what a concept says ([threat model](threat-model.md)).

## What remains to do

These are designs, not features. Each would extend KTL's checks from what the bundle says to whether a host's skills still work. That is a condition check, the work a museum gives its conservator, who examines objects and writes condition reports without cataloguing or authenticating them. If KTL takes these on, they belong to a new role, not to the librarian.

- **A record of skill runs.** A feedback kind for a skill run, recorded by the agent that ran the skill, would give WikiSkill's raw layer KTL's guards. It would accept only a skill name the host holds and a short failure signature, keep the entry's text from every session but the librarian's, and leave the librarian its only consumer.
- **A trigger test.** The retrieval score could be run over the host's skill descriptions, which is what an agent chooses skills by. It needs task prompts paired with the skill each should start, where the ledger holds the questions readers asked.
- **An `AgentSkill` domain schema.** A LinkML class for the six Agent Skills fields would let `lokf validate` check a skill's concept against them, and let the docent tell a skill's concept from a how-to.
- **OKF's attested computation for a skill's scripts.** LOKF's `AttestedComputation` is a sanctioned recipe whose run returns a receipt that an attester compares with it. A skill's deterministic scripts could be described that way.
- **A place for a fault in the host's own text.** The docent found a guide that names a script without its file extension. Its feedback records gaps in the bundle, so it had nowhere to record a fault in a skill.
- **The excerpt check.** LOKF 0.9.0's `sources[].excerpt` lets a program check the passage a concept relies on, so the work list can tell an edit to that passage from an edit elsewhere in the skill's file.

## Sources

- Tang, L., Rashtchian, C., Ferng, C.-S., Tomkins, A., Juan, D.-C. and Vu, T. (2026). WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution. arXiv:2608.27454. <https://arxiv.org/abs/2608.27454>
- Huang, D. et al. (2026). SkillWiki: A Living Knowledge Infrastructure for Agent Skills. arXiv:2606.16523. <https://arxiv.org/abs/2606.16523>
- The Agent Skills specification. <https://agentskills.io/specification>
- `anthropics/skills` at commit `683bc88`, the clone the run used. <https://github.com/anthropics/skills/tree/683bc88e56f3e09ba94f7055977f3d3aa499f202>
