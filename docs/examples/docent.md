# Examples: `lokf-docent` answering real questions

Eight questions actually asked against this repository's own `.lokf/knowledge/` bundle, following `skills/lokf-docent/SKILL.md` exactly: read the bundle first, widen along typed relations before searching the repo, verify exact values at the source before stating them, state each concept's trust label, and fall back - deliberately, and out loud - only when the bundle has no answer. These are real captured output, not invented transcripts.

Trust labels here mean what `skills/lokf-curator/references/trust-fields.md` defines. At the time these were run, no concept in this bundle had been confirmed by a person yet (`lokf-curator` hadn't been run), so every answer below is at most "checked by automation only" or "nobody has checked this yet" - which is itself demonstrated in examples 2 and 6. The answers are what the docent said then; some of the pages it checked have been rewritten since (`CONTRIBUTING.md` is now a shorter checklist), so take the sources named as current, not the values quoted.

## 1. "What is LOKF?"

> LOKF (Linked Open Knowledge Format) is a semantic profile of OKF in which
> every field, type, and relationship is bound to a public vocabulary, so the
> same Markdown expands losslessly to JSON-LD and RDF (bundle:
> `glossary/lokf.md`, checked by automation only).

*One concept fully answers the question, so the answer skips the full footer per the skill's own rule for that case.*

## 2. "What does OKF require of a concept file?"

> OKF (Open Knowledge Format) requires only that a concept file's path serve
> as its ID and that its YAML frontmatter carry a `type` field - everything
> else is optional. A consumer must never reject a bundle for missing
> optional fields, unknown types, unknown keys, or broken cross-links.

```text
From the bundle:
- OKF (glossary/okf.md) - checked by automation only
- OKF specification (v0.2) (references/okf-specification.md) - nobody has checked this yet
```

*Two related concepts, two different labels - the glossary term was re-verified against its internal resource file this session; the Reference concept's resource is an external URL that wasn't re-fetched, so it carries no `verified` event yet. Real difference, not an inconsistency.*

## 3. "I have a repo with no `.lokf/` yet - which skill do I run first?"

> Run `lokf-sidecar` first. It's the one-shot bootstrap that creates the
> `.lokf/` sidecar - tooling, docs, and a dummy skeleton - from bundled
> templates, then hands off to `lokf-librarian` to fill it with real
> knowledge.

```text
From the bundle:
- lokf-sidecar skill (playbooks/lokf-sidecar-skill.md) - checked by automation only
```

## 4. "How do lokf-librarian and lokf-curator relate?"

> `lokf-curator` `dependsOn` `lokf-librarian`: the curator's job - recording a
> person's verdicts - only makes sense once the librarian has derived
> concepts to review. The relationship also marks the boundary between them:
> the librarian deals in facts about the repository and never vouches for
> them; the curator deals in judgments a person made and never derives facts
> itself.

```text
From the bundle:
- lokf-librarian skill (playbooks/lokf-librarian-skill.md) - checked by automation only
- lokf-curator skill (playbooks/lokf-curator-skill.md) - checked by automation only
  (dependsOn -> lokf-librarian-skill)
```

## 5. "How do I contribute a change to these skills?"

> There's no build step - the skills are Markdown, YAML, and one shell
> script. Clone the repo and run `bash scripts/validate-repository.sh`.
> Before opening a pull request, run five checks: the repository-contract
> script, `gh skill publish --dry-run` (if the GitHub CLI is installed),
> `shellcheck` on any changed script, `actionlint` on any changed workflow
> (including the templates under `skills/lokf-sidecar/templates/github/`),
> and a `CHANGELOG.md` entry under `[Unreleased]` if the change alters
> behavior.

```text
From the bundle:
- Contributing (playbooks/contributing.md) - checked by automation only
Checked at source: CONTRIBUTING.md's "Before opening a pull request" section -
  all five items match exactly what the bundle claims.
```

## 6. "What GitHub CLI version do I need for `gh skill`?"

> The bundle's Reference concept says `gh skill` was added in GitHub CLI
> v2.90.0, and `README.md` independently states the same figure. I opened the
> concept's actual source to confirm the number directly, but the manual page
> at `cli.github.com/manual/gh_skill_install` documents current behavior, not
> a changelog - it doesn't state a version number itself, so I can't
> independently confirm v2.90.0 from that specific page. Both places in this
> repository agree, but I'd check the GitHub CLI release notes before relying
> on the exact number.

```text
From the bundle:
- gh skill (GitHub CLI) (references/gh-skill-cli.md) - nobody has checked this yet
Checked at source: cli.github.com/manual/gh_skill_install - does not state a version number
Gap recorded: none - the bundle's claim isn't contradicted, just unconfirmable at this page
```

*This is the honest version of "verify exact values at the source": the source didn't have the value to confirm, and the answer says so instead of quietly repeating the bundle's number as fact.*

## 7. "What's the roadmap for a fifth skill after lokf-docent?"

> I don't see anything in the bundle about a planned fifth skill - the
> Explanation concept on why there are four roles explains the current
> design, not a roadmap, and I searched the rest of the repository too.
> There's no mention of a fifth skill anywhere. This looks like a genuine gap
> rather than something I missed.

```text
From the bundle: (none relevant)
Gap recorded: Miss - "What's the roadmap for a fifth skill after lokf-docent?" -
  no answer found anywhere in the bundle or repository.
```

Asked once this session whether to record gaps in `.lokf/feedback.md`; the answer was yes, so this one was written there for real - see
[`.lokf/feedback.md`](../../.lokf/feedback.md). `lokf-librarian`'s next run will either turn it into a real concept or note that no roadmap exists.

## 8. "Who do I contact to report a security issue, and is that policy confirmed by a person?"

> Use GitHub's private vulnerability reporting (linked from `SECURITY.md`)
> rather than a public issue or a direct email - that's the documented
> channel, not the maintainer's personal contact. The bundle records the
> maintainer as Noel McLoughlin (the bundle's `publisher`). As for whether the
> security policy itself has been confirmed by a person: no - it's still a
> draft, checked by automation only. Nobody has reviewed it by hand yet.

```text
From the bundle:
- Security policy (policies/security.md) - still a draft; checked by automation only
Checked at source: SECURITY.md's "Reporting a vulnerability" section - matches exactly
```

---

Try these yourself once `lokf-docent` is installed, or ask your own - that's the point of the skill.
