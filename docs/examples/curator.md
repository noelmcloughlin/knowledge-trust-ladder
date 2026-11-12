# Examples: `ktl-curator` in a review session

One session of `ktl-curator` against this repository's own `.lokf/knowledge/` bundle, following `skills/ktl-curator/SKILL.md` as the repository held it on 2026-11-12. The maintainer sat in the run and typed every verdict; an agent showed the evidence and wrote what the skill says to write. The output is captured, cut only where a line says so. The bundle has changed since, so take the concepts named as current, not the counts.

The session had a plan going in. The curation policy had just been added, and the explanation of domain vocabularies had moved to a new path, so the old concept was waiting to be retired. After those, the session worked down the report's *worth ten minutes today* list.

## Step 1: the report

The agent ran `knowledge-preflight.sh` and `knowledge-report.sh`, worked out the two items the script leaves to hand, and printed the report. Nothing was written in this step.

```text
Knowledge bundle - Knowledge Trust Ladder - 2026-11-12
Confirmed by a person: 4 of 65 · Checked by automation only: 42 · Nobody has checked: 2 · Drafts: 43 · Reopened: 14 · Past review date: 0 · Edited since confirmed: 17 · Retired: 0 · Not tied to a signed commit: 8

Worth ten minutes today
1. Knowledge bundle (GlossaryTerm) - edited since a person last confirmed it; 27 other concepts rely on this - skills/ktl-sidecar/templates/README.md
2. ktl-librarian skill (Playbook) - edited since a person last confirmed it; 13 other concepts rely on this - skills/ktl-librarian/SKILL.md
3. Trust label (GlossaryTerm) - edited since a person last confirmed it; 11 other concepts rely on this - skills/ktl-curator/references/trust-fields.md
4. ktl-curator skill (Playbook) - edited since a person last confirmed it; 10 other concepts rely on this - skills/ktl-curator/SKILL.md
5. Three lines of defence - where each role sits, and what an auditor can check (Explanation) - edited since a person last confirmed it; 9 other concepts rely on this - docs/three-lines.md

Open questions
- When the built-in vocabulary stops fitting: domain vocabularies (explanation/domain-schemas.md): rewrite as needed
[four more of the maintainer's notes and three of the librarian's cut]

Feedback from readers: 2 entries waiting in .lokf/feedback.md

Vocabulary fit: fine

Not tied to a signed commit: 8 - Why a registrar role, Knowledge bundle, Knowledge sources, AI covenant, Security policy, Versioning policy, Agent Skills specification, LOKF specification, OKF specification. Recorded as confirmed by a person, but no signed commit stands behind it.

Sample - seed "2026-11-12"
For a person to check what automation passed (3, picked by the same rule):
Asked for 3: the bundle holds none checked by automation only, drafts apart, so the list is empty.
Re-checked by a second person: 0 of 4 confirmed

Ready to record: human:noelmcloughlin via gh · signing on (key C20A88C76BE67068), HEAD signed, your key is on file · attended

56 more not yet checked. Run again anytime - every confirmation counts.
```

*The signed-commit line is one of the two items worked out by hand, and the hand slipped: it counts 8 and names 9. Nine is right. On each of the nine, the first confirmation came from one of two curation commits of 2026-09-09 and 2026-09-10, made before the maintainer signed commits; their later confirmations are signed. The agent said so beside the report, as a question about two early commits and not as a sign of forgery.*

*The sample is empty because the new policy asks for three concepts checked by automation only, and every such concept in this bundle was still a draft.*

## Step 2: the review session

Before the first write, the agent said whose name the answers would carry:

> I'll record your answers as `human:noelmcloughlin`. Is that ok? Want to go through these now?

The maintainer answered "yes". Each item below is one turn: the evidence, the claim, the question, and the verdict the maintainer typed.

### 1. Retire the old explanation

The evidence was a comparison of `explanation/domain-schemas.md` with `explanation/domain-vocabularies.md`. The two differed only in their `id`, the maintainer's 2026-10-13 confirmation and their "rewrite as needed" note, which only the old one carried. Apart from itself, only `index.md` and `log.md` still named the old path.

> **Maintainer:** Retire (replaced by domain-vocabularies)

```diff
-status: draft
+status: deprecated
```

### 2. Clear a note on the retired concept

> **Maintainer:** the open question goes

```diff
-## Open questions
-
-- 2026-10-29, human:noelmcloughlin: rewrite as needed
```

### 3. Confirm the new explanation

The agent quoted ten lines across the concept's four sources, among them `docs/architecture.md:34`: "A domain whose concepts stop fitting it [extends the vocabulary]…". It then named one gap: the concept's overview said the page says a domain "extends the schema".

> **Maintainer:** Correct now "extends the vocabulary" - stale after 2028-11-12

```diff
-It also says that a domain whose concepts stop fitting it extends the schema, so
+It also says that a domain whose concepts stop fitting it extends the vocabulary, so
```

```yaml
generated:
  by: human:noelmcloughlin
  at: "2026-11-12T20:37:20Z"
verified:
  - by: human:noelmcloughlin
    at: "2026-11-12T20:37:20Z"
    revision: "12d91cac03649375c1a0a547cfb4d5987f20c558"
stale_after: 2028-11-12
```

*Correct now replaces `generated`, so the librarian will not rewrite this text again unless the maintainer releases it.*

### 4. Confirm the curation policy

The agent set the policy beside the template in `references/review-session.md` it was made from, row by row. The policy kept two of the template's three cadence rows, since the bundle holds no services or datasets. It set `Automation re-check: 3`, `Evidence first: yes` and `Younger readers: 13-18`. The maintainer had written the policy that afternoon, but no `verified` event recorded a check, so the report said nobody had checked it.

> **Maintainer:** Confirm

```yaml
verified:
  - by: human:noelmcloughlin
    at: "2026-11-12T20:38:32Z"
    revision: "12d91cac03649375c1a0a547cfb4d5987f20c558"
stale_after: 2027-11-12
```

### 5. Knowledge bundle

The librarian had rewritten this concept in full since the maintainer last confirmed it. The agent quoted the sidecar's README (lines 3, 7, 17-18, 24-31 and 34), `docs/architecture.md:28` and `docs/obsidian.md:7`. It also named what the old text had and the new one lost: a note that *bundle* and *sidecar* are used loosely for each other.

> **Maintainer:** Confirm

The new event was appended after the five earlier ones, `status: draft` was removed, and `stale_after` moved from 2028-09-24 to 2028-11-12.

### 6. ktl-librarian skill

This concept runs to 3,400 words. The agent checked ten of its numbers and names against their sources, each of which matched, and said plainly that the rest of the body was not read line by line.

> **Maintainer:** Later

Nothing was written.

### 7. Trust label

One sentence had changed since the last confirmation:

```diff
-A `revision` on an event (proposed for lokf 0.9.0, not yet released) is shown beside …
+A `revision` on an event (lokf 0.9.0 and later) is shown beside …
```

The agent quoted `references/trust-fields.md:28`, "It arrived in lokf 0.9.0", and the preflight's "lokf 0.9.0 installed".

> **Maintainer:** Confirm

### 8. ktl-curator skill

The agent checked six of the concept's claims against `SKILL.md`, each of which matched. The maintainer then asked a question of their own:

> **Maintainer:** Is there any excerpt for the concept?

There was none. The concept's two footnotes name a section of their source in words, such as "skills/ktl-curator/SKILL.md, Step 1, items 7 and 8", but no `sources[].excerpt` quotes the passage verbatim. No concept in the bundle carried one. With an excerpt, `just lokf-check-refs` would fail once the source no longer held the passage.

> **Maintainer:** Wrong - send back - "add excerpt to the footnoted sources"

```markdown
## Open questions

- 2026-10-29, human:noelmcloughlin: rewrite as needed
- 2026-11-12, human:noelmcloughlin: add excerpt to the footnoted sources
```

Before the next item, the maintainer cleared the older note:

> **Maintainer:** Clear the "- 2026-10-29, human:noelmcloughlin: rewrite as needed" note from previous entry

### 9. Three lines of defence

The concept had followed six edits to `docs/three-lines.md`, and each edit matched the page. The agent found one stale line, though, and it was in the source, not the concept: the page still listed "LOKF releasing it in 0.9.0" as work that remains.

> **Maintainer:** Wrong - send back - "remove stale information from docs/three-lines.md"

```diff
 stale_after: 2027-10-19
+status: draft
```

```markdown
## Open questions

- 2026-11-12, human:noelmcloughlin: remove stale information from docs/three-lines.md
```

*The earlier confirmation stays, so the report counts the concept as reopened, not as a draft. The fix belongs in the page; the librarian follows it on its next run.*

## After the session

The agent prepended two lines to `log.md` under the day's heading. The report reads the successor of a retired concept from the second line.

```markdown
* **Curation**: human:noelmcloughlin confirmed 3 concepts, corrected 1, sent 2 back, retired 1 and left 1 for later. They cleared their "rewrite as needed" notes on Domain schemas and the ktl-curator skill.
* **Deprecation**: [When the built-in vocabulary stops fitting: domain vocabularies](../explanation/domain-schemas.md) retired - replaced by [When the built-in vocabulary stops fitting: domain vocabularies](../explanation/domain-vocabularies.md).
```

Then it ran the checks and committed the verdicts on their own, signed:

```text
$ cd .lokf
$ uv run -q --frozen just lokf-validate
OK — 65 concepts in knowledge validate against KnowledgeBundle.
$ uv run -q --frozen just lokf-check-refs
OK — 65 concepts in knowledge validate against KnowledgeBundle. All in-namespace relation targets resolve. No local excerpt to check.
$ bash scripts/knowledge-conventions.sh knowledge --since origin/main
OK - knowledge keeps the conventions lokf validate cannot check
$ cd ..
$ bash .lokf/scripts/knowledge-provenance.sh origin/main
OK - 1 confirmation(s), new, changed or removed, in origin/main..HEAD signed by the key on file for their curator
```

*The provenance script counts each person once per commit, so one signed commit by one curator reads as 1, however many events it adds.*

## Notes

- The session ran no Step 3. The curation policy it confirmed had been written by hand earlier the same day, from the template, rather than through the skill.
- [What a curation changes for a reader](docent-after-curation.md) captures nine docent answers asked after this session, under `Evidence first: yes`. Nobody has yet captured answers under `Evidence first: no`.
