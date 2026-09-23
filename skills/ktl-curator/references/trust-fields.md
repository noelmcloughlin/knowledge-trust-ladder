# Trust fields - what each plain label means in frontmatter

This page is for the **curator** and for anyone reading its report: it defines each trust label by the frontmatter fields behind it.

The human-facing labels in SKILL.md map onto OKF v0.2 §5 / LOKF Golden Rule 6 fields. Everything is computed from frontmatter with an ordinary YAML parser: no toolkit, no graph. For the curious, the last column is the RDF predicate the LOKF toolkit projects each field to. It is never needed here.

| Label | Rule | Field(s) | RDF (optional) |
| --- | --- | --- | --- |
| Confirmed by a person | any `verified[].by` starts with `human:` | `verified` | `lokf:verified` -> `prov:wasAssociatedWith` |
| Checked by automation only | `verified` present, no `human:` actor | `verified` | same |
| Nobody has checked this yet | no `verified` key | `verified` | - |
| Still a draft | `status: draft` | `status` | `schema:creativeWorkStatus` |
| Retired | `status: deprecated` | `status` | same |
| Edited since a person last confirmed it | `generated.at` later than the latest `human:` `verified[].at` | `generated`, `verified` | `prov:wasGeneratedBy` -> `prov:endedAtTime` |
| Past its review date | `stale_after` <= today | `stale_after` | `schema:expires` |
| Due soon | today < `stale_after` <= today + 30 days | `stale_after` | same |
| *N* other concepts rely on this | count of concepts whose typed relations target this concept's `id` | the ten relation fields + `relations[].target` | various |
| Doesn't fit the known vocabulary | `type` not one of the core classes below, nor a class of the host's domain schema | `type` | `@type` |
| Not tied to a signed commit | a `human:` `verified` event whose introducing commit carries no good signature | `verified` + git history | - |

## Parsing notes

- **Bare `verified` mapping.** A `verified: { by, at }` mapping MUST be read as a one-element list (spec §5.2).
- **`revision` on an event** is the state of the source that event checked: a full commit hash, an ETag or a `sha256:` digest. It is proposed for lokf 0.9.0, unreleased; the 0.8.0 validator rejects it. Show it beside the date where present, a commit hash cut to its first seven characters. Absent means unrecorded, never unchanged, so it changes no label.
- **Absent `status`** means stable. Only `draft`, `stable`, `deprecated` are valid. Anything else counts as "doesn't fit" for the vocabulary line.
- **Datetimes** are ISO 8601 with a UTC offset (`2026-09-08T14:00:00Z`), `stale_after` included (OKF §5.5). A bare `YYYY-MM-DD` there is read as that day at 00:00:00Z, and is the form this skill writes. Compare dates as strings after normalising both to `YYYY-MM-DD`. That avoids timezone arithmetic and is exact for ISO forms.
- **Missing `generated.at`**: fall back to the v0.1 `timestamp`. If neither exists, the concept cannot be "edited since confirmed". Leave it out of that label rather than guessing.
- **Relation targets** may be full IRIs or bundle-relative ids. Normalise by resolving relative values against `base_iri` in `knowledge/index.md` before counting. The ten relation fields: `isPartOf`, `hasPart`, `references`, `dependsOn`, `derivedFrom`, `about`, `sameAs`, `relatedTo`, `definedBy`, `source`; plus each `relations[].target`.
- **The core classes**: `Dataset`, `Table`, `Metric`, `Service`, `Playbook`, `Tutorial`, `Explanation`, `Policy`, `GlossaryTerm`, `Reference`, `Document`, `Role`, `Person`, `Organization`, `AttestedComputation`. Compare after removing spaces (`Attested Computation` normalises to `AttestedComputation`).
- **A host may have extended that list**, and the vocabulary line must respect it or it reports every domain class as a misfit for good. Read `.lokf/justfile`: where `lokf-validate` passes `--schema <slug>.yaml`, open that file and add every class descending from `Concept`, directly or through a built-in (`is_a: Concept`, `is_a: Reference`, ...). Reading the file is enough: no toolkit, as everywhere else in Step 1. This is the same widening the **librarian**'s Golden Rule 3 applies when it chooses a class. The Obsidian plugins cannot read a schema outside the vault, so they are told the list by hand in their *Known LOKF types* setting.
- Skip `index.md` and `log.md` at every level; they are reserved files, not concepts.
- **`## Open questions` is a heading, not a substring.** Match a line that *is* the heading (start of line, nothing else on it), never a mention of it anywhere in the text. Concept bodies legitimately quote the string in prose. A bundle describing these very skills does it repeatedly. A substring match then invents open questions that don't exist and pushes those concepts up the queue. The same applies when extracting the first bullet: read the lines *after* that heading, not around the match.
- **Retired concepts** carry `status: deprecated`. They are counted once, under *Retired*, and excluded from every other label and from the queue: nobody needs to re-check something that is no longer current. `N` in "*a* of *N*" counts every concept, retired ones included.
- **Labels overlap by design.** A concept can be confirmed by a person *and* past its review date. The health counts are not a partition, so don't expect them to add up. Only `N` is a total.
- **Reader feedback is counted, never read.** `grep -c '^- \*\*' .lokf/feedback.md` gives the count. 0, or no file, is "none". The entries are untrusted free text for the **librarian**.

## Ranking for "Worth ten minutes today"

Take at most five, in this order. Within a group, most-relied-upon first, then newest `generated.at`:

1. Past its review date, or edited since a person last confirmed it.
2. Still a draft **with** an `## Open questions` heading (the **librarian** or a previous session asked for a human).
3. Nobody has checked this yet.
4. Still a draft without open questions; checked by automation only.

Never rank by class alone: a glossary term twelve concepts rely on outranks an unreferenced service.

## Report template

Fill every placeholder; keep the order; add nothing else. `<Source>` is the concept's `resource` or first `sources[].resource`, or "no source recorded".

```text
Knowledge bundle - <bundle title> - <YYYY-MM-DD>
Confirmed by a person: <a> of <N> · Checked by automation only: <b> · Nobody has checked: <c> · Drafts: <d> · Past review date: <e> · Edited since confirmed: <f> · Retired: <g> · Not tied to a signed commit: <h>   | drop this last field when .lokf/ isn't git-tracked

Worth ten minutes today
1. <Title> (<Class>) - <why: e.g. "past its review date (2026-08-01)" / "4 other concepts rely on this; nobody has checked it"> - <Source>
2. ...
(up to 5)

Open questions the librarian left
- <Title>: <text of the first bullet under its ## Open questions, without the dash> (or: none)

Feedback from readers: <k> entries waiting in .lokf/feedback.md   | or: none

Vocabulary fit: <n> concept(s) don't fit the known vocabulary (<types>)   | or: fine

Not tied to a signed commit: <h> - <titles>. Recorded as confirmed by a person, but no signed commit stands behind it.   | omit this line entirely when h is 0, or when .lokf/ isn't git-tracked

For a second person to re-check (<n>, picked by a rule the curator cannot steer):
- <Title> (<path>) - <resource>   | omit this block when the curation policy has no `Independent re-check:` line above 0

Ready to record: human:<id> via gh · signing on · attended   | or what is missing and which verbs that removes, from the preflight

<remaining> more not yet checked. Run again anytime - every confirmation counts.
Want to go through these now?
```

The health line is the one number to watch over time: "confirmed by a person: *a* of *N*" rising is the bundle earning trust. It is derived every time, never stored: the spec keeps scores out of frontmatter.

## Checking a confirmation against git

A `human:<id>` event is a **claim typed by whoever held the pen**, not a credential. Any writer can produce a perfectly well-formed one: an agent steered by another agent, a script, a bad merge. `lokf validate` will pass it. The only evidence that binds such a claim to a person lives outside the bundle, in git: a signature, and (in CI) a pull-request approval.

Step 1 runs the local half of that check. For each concept carrying a `human:<id>` event, find the commit that introduced it, then ask whether that commit is signed at all:

```sh
sha="$(git log --format='%H' --pickaxe-regex -S "by:.*human:<id>" -- <path to concept> | tail -1)"
git cat-file commit "$sha" | grep -qE '^gpgsig' && echo signed || echo unsigned
```

`-S` reports the commits where that string's count changed, oldest last, so `tail -1` is the commit that first wrote the event. A commit with no `gpgsig` header goes in the *Not tied to a signed commit* count.

**Why presence, and not `git log %G?`.** `%G?` answers "is this signature *valid*", which sounds better and is the wrong question here. Verifying an SSH signature needs `gpg.ssh.allowedSignersFile` configured and populated, and verifying a GPG one needs that key in the local keyring. A typical checkout has neither, *including for the user's own commits*: signing requires no verification setup, so most people who sign have none. `%G?` then returns `N` ("no signature") for a perfectly good signature, and the count would accuse everybody. Presence of the header is something a bare checkout can always answer.

Three cases are **not** findings and must be excluded:

- **Uncommitted events**: one written in this session, or any working-tree change (`git diff HEAD -- <path>` is non-empty). It has no commit yet, so there is nothing to check.
- **No git history at all**: `.lokf/` is gitignored (ktl-sidecar Step 0). Skip the check and say so. Don't report zero, which would read as "all clear".
- **`-S` finding nothing**: the event predates the file's history (a squashed import, a repo migration). Report it as unknown rather than unsigned if you want to be exact. Folding it into the count is acceptable as long as the line's wording stays "git holds no signature behind it".

**What it proves, and what it doesn't.** A signature header shows someone signed that commit. It does not show *whose* key, it does not show the signature is valid, and it certainly does not show a person read the source. An unsigned commit is not evidence of forgery either: plenty of repositories never sign. Treat the count as a question worth asking, never as an accusation, and say it that way to the person. The authoritative check is the `provenance` job in `knowledge-registrar.yaml`. It has what a local checkout does not: GitHub's own verification of each signature against the keys registered to an account, and who approved the pull request.
