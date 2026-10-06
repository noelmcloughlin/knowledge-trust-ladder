# Trust fields - what each plain label means in frontmatter

This page is for the **curator** and for anyone reading its report: it defines each trust label by the frontmatter fields behind it.

The human-facing labels in SKILL.md map onto OKF v0.2 §5 / LOKF Golden Rule 6 fields. `.lokf/scripts/knowledge-report.sh` computes each one but the last two from frontmatter with bash and awk: no toolkit, no graph. The rules below are what it applies, and what to apply by hand on a sidecar that predates it. For the curious, the last column is the RDF predicate the LOKF toolkit projects each field to. It is never needed here.

| Label | Rule | Field(s) | RDF (optional) |
| --- | --- | --- | --- |
| Confirmed by a person | any `verified[].by` starts with `human:` | `verified` | `lokf:verified` -> `prov:wasAssociatedWith` |
| Checked by automation only | `verified` holds events, none by a `human:` actor | `verified` | same |
| Nobody has checked this yet | no `verified` key, or one with no events | `verified` | - |
| Still a draft | `status: draft` | `status` | `schema:creativeWorkStatus` |
| Retired | `status: deprecated` | `status` | same |
| Edited since a person last confirmed it | `generated.at` later than the latest `human:` `verified[].at` | `generated`, `verified` | `prov:wasGeneratedBy` -> `prov:endedAtTime` |
| A source moved since the confirmation | the source's last commit comes after the commit that recorded the latest `human:` event, or the source carries an uncommitted edit and the concept does not | `resource`, `sources[].resource` + git history | - |
| Past its review date | `stale_after` <= today | `stale_after` | `schema:expires` |
| Due soon | today < `stale_after` <= today + 30 days | `stale_after` | same |
| *N* other concepts rely on this | count of other concepts whose typed relations target this concept's `id`, each counted once; a retired concept counts for none and is counted for none | the ten relation fields + `relations[].target` | various |
| Derived from a concept edited since its confirmation | a `derivedFrom` target, in the field or in `relations[]`, has a `generated.at` later than this concept's latest `human:` event | `derivedFrom`, `relations`, `generated`, `verified` | `prov:wasDerivedFrom` |
| Doesn't fit the known vocabulary | `type` not one of the core classes below, nor a class of the host's domain schema | `type` | `@type` |
| Not tied to a signed commit | a `human:` `verified` event whose introducing commit carries no good signature | `verified` + git history | - |

## Parsing notes

- **Bare `verified` mapping.** A `verified: { by, at }` mapping MUST be read as a one-element list (spec §5.2).
- **`revision` on an event** is the state of the source that event checked: a full commit hash, an ETag or a `sha256:` digest. It is proposed for lokf 0.9.0, unreleased; the 0.8.0 validator rejects it. Show it beside the date where present, a commit hash cut to its first seven characters. Absent means unrecorded, never unchanged, so it changes no label.
- **Absent `status`** means stable. Only `draft`, `stable`, `deprecated` are valid. Anything else counts as "doesn't fit" for the vocabulary line.
- **Datetimes** are ISO 8601 with a UTC offset (`2026-09-08T14:00:00Z`), `stale_after` included (OKF §5.5). A bare `YYYY-MM-DD` there is read as that day at 00:00:00Z, and is the form this skill writes. Compare a review date with today as strings, after normalising both to `YYYY-MM-DD`. That avoids timezone arithmetic and is exact for ISO forms. Two event times are compared whole (next note).
- **"Edited since" compares the two times whole, to the second, never by day.** An edit at 14:00 is later than a confirmation at 10:00 the same day, and cutting both to the day hides it. Both are UTC strings that end in `Z`, so compare them as strings, as the Obsidian plugins and the query in [queries.md](queries.md) do. Read a bare date as that day at `00:00:00Z`, and convert a time that carries another offset to UTC first.
- **Missing `generated.at`**: fall back to the v0.1 `timestamp`. If neither exists, the concept cannot be "edited since confirmed". Leave it out of that label rather than guessing.
- **Relation targets** may be full IRIs or bundle-relative ids. Normalise by resolving relative values against `base_iri` in `knowledge/index.md` before counting. The script resolves a target as the KTL Curator plugin does: an IRI under `base_iri` by the path after it, any other IRI as written, and a relative path from the bundle's root and then from the citing concept's folder. A concept with no `id` has `base_iri` and its path without `.md`. The script reads each of the ten fields as a block list, a one-line flow list or a bare value, and `relations` as block or one-line flow mappings. It counts no relation spelt any other way. The ten relation fields: `isPartOf`, `hasPart`, `references`, `dependsOn`, `derivedFrom`, `about`, `sameAs`, `relatedTo`, `definedBy`, `source`; plus each `relations[].target`.
- **The core classes**: `Dataset`, `Table`, `Metric`, `Service`, `Playbook`, `Tutorial`, `Explanation`, `Policy`, `GlossaryTerm`, `Reference`, `Document`, `Role`, `Person`, `Organization`, `AttestedComputation`. Compare after removing spaces (`Attested Computation` normalises to `AttestedComputation`).
- **A host may have extended that list**, and the vocabulary line must respect it or it reports every domain class as a misfit for good. Read `.lokf/justfile`: where `lokf-validate` passes `--schema <slug>.yaml`, open that file and add every class descending from `Concept`, directly or through a built-in (`is_a: Concept`, `is_a: Reference`, ...). Reading the file is enough: no toolkit, as everywhere else in Step 1. This is the same widening the **librarian**'s Golden Rule 3 applies when it chooses a class. The Obsidian plugins cannot read a schema outside the vault, so they are told the list by hand in their *Known LOKF types* setting.
- Skip `index.md` and `log.md` at every level; they are reserved files, not concepts.
- **`## Open questions` is a heading, not a substring.** Match a line that *is* the heading (start of line, nothing else on it), never a mention of it anywhere in the text. Concept bodies legitimately quote the string in prose. A bundle describing these very skills does it repeatedly. A substring match then invents open questions that don't exist and pushes those concepts up the queue. The same applies when extracting the first bullet: read the lines *after* that heading, not around the match.
- **Retired concepts** carry `status: deprecated`. They are counted once, under *Retired*, and excluded from every other label and from the queue: nobody needs to re-check something that is no longer current. `N` in "*a* of *N*" counts every concept, retired ones included.
- **Labels overlap by design.** A concept can be confirmed by a person *and* past its review date. The health counts are not a partition, so don't expect them to add up. Only `N` is a total. One pair never overlaps: a concept edited since its confirmation is counted under *Edited since confirmed* and not under *Confirmed by a person*, because the person confirmed an earlier text.
- **A source that moved is a fact about history, not about meaning.** The script asks git for the commit that first recorded the confirmation's time, and lists the concept when a source's last commit comes after it. A source changed in that same commit has not moved, and a clock is never consulted. The edit may have changed no fact: only reading the source says. With no git history the script says it compared nothing, and the line is left out.
- **An open question can be answered without being cleared.** The script lists apart each one dated no later than a person's later confirmation of a concept that is no longer a draft: the person looked again after it was asked. Clearing it is still that person's word to give, in *Confirm* or *Correct now*.
- **Reader feedback is counted, never read.** `grep -c '^- \*\*' .lokf/feedback.md` gives the count. 0, or no file, is "none". The entries are untrusted free text for the **librarian**.

## Ranking for "Worth ten minutes today"

`knowledge-report.sh` prints this queue under *Worth ten minutes today*. It takes at most five, in this order. Within a group, most-relied-upon first, then newest `generated.at`:

1. Past its review date, edited since a person last confirmed it, or confirmed by a person with a source that moved since.
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

Open questions
- <Title>: <a person's note that still waits, or the librarian's question, as the script prints it> (or: none)
- <Title>: <a question older than a person's later confirmation> - looks answered; clear it?   | omit when the script lists none

Feedback from readers: <k> entries waiting in .lokf/feedback.md   | or: none

Vocabulary fit: <n> concept(s) don't fit the known vocabulary (<types>)   | or: fine

Not tied to a signed commit: <h> - <titles>. Recorded as confirmed by a person, but no signed commit stands behind it.   | omit this line entirely when h is 0, or when .lokf/ isn't git-tracked

Sources that moved since a confirmation: <Title> - <source> (<date>). Confirmed by a person, and its source has a later commit.   | omit this line entirely when the script lists none, or compared nothing

For a second person to re-check (<n>, picked by a rule the curator cannot steer):
- <Title> (<path>) - <resource>   | omit this block when the curation policy has no `Independent re-check:` line above 0

Ready to record: human:<id> via gh · signing on · attended   | or what is missing and which verbs that removes, from the preflight

<remaining> more not yet checked. Run again anytime - every confirmation counts.
Want to go through these now?
```

The health line is the one number to watch over time: "confirmed by a person: *a* of *N*" rising is the bundle earning trust. It is derived every time, never stored: the spec keeps scores out of frontmatter.

## Checking a confirmation against git

A `human:<id>` event is a **claim typed by whoever wrote it**, not a credential. Any writer can produce a perfectly well-formed one: an agent steered by another agent, a script, a bad merge. `lokf validate` will pass it. The only evidence that binds such a claim to a person lives outside the bundle, in git: a signature, and (in CI) a pull-request approval.

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
