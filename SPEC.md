# Knowledge Trust Ladder (KTL) specification

**Version 0.2, a draft.** It is written for OKF 0.2 and LOKF 0.2, the versions a bundle declares in its root `index.md`.

This page states the rules that Knowledge Trust Ladder (KTL) adds to a [LOKF](https://lokf.nolan-nichols.com/specification/) knowledge bundle. It is for anyone who writes a program that reads or writes a bundle KTL keeps, and for anyone who must say what *confirmed by a person* means there.

## 1. Scope

KTL is an [OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md) runtime. OKF defines the format and prescribes no runtime, and LOKF gives each field of that format its meaning. This page defines no field, type or relation. A field KTL needs is asked of LOKF.

The page states what neither specification states, and what more than one program applies:

- the ladder a concept climbs (section 3);

- which program or person writes each record, and what no program may change (section 5);

- the eighteen conventions a bundle keeps beyond the format (section 6);

- what counts as a person's confirmation (section 7);

- how a trust label is computed from the records (section 8).

How each role does its work is in that role's skill, and is no part of this page. [The architecture](docs/architecture.md) names the roles, and [How it works](docs/how-it-works.md) tells how they fit together.

Sections 3 to 8 and section 10 are rules. A sentence there says what a conforming bundle or program does. The examples, section 9 and section 12 explain and add no rule.

This page is the source for those rules. Each skill is installed alone, so the scripts and the skills' reference pages carry copies, and [section 12](#12-where-each-rule-is-applied) names each copy and the check that holds it to this page.

## 2. Terms

The format's terms, such as *bundle*, *concept*, *frontmatter* and *actor*, mean what OKF section 2 says. KTL adds these:

- **Sidecar**: the `.lokf/` folder, which holds the bundle and its tools beside the repository's own files.

- **Event**: a mapping in a concept's frontmatter that names who acted and when, as `by` and `at`, and may name the source's state as `revision`. The `generated` record is one event, and each entry of `verified` is one.

- **A person's record**: every mapping in the frontmatter whose `by` starts with `human:`, under any key, and every note a person left under `## Open questions`. A note under `process:ktl-curator` counts as one, since that actor stands for a person.

- **Verdict**: what a person decides about a concept: confirm, send back, correct, retire or later.

- **The pen**: `knowledge-apply.sh`, the one program through which an agent writes the bundle.

- **The gate**: the checks that run on each change to the bundle before it is merged: `lokf validate`, the conventions script and the provenance check.

- **Trust label**: a plain statement of how far a concept has been checked, such as *confirmed by a person*.

- **Today**: the date in UTC.

## 3. The ladder

A concept that is not retired stands on one of three rungs. Its `verified` events say which, and OKF section 5.3 names the same three as trust tiers.

| Rung | The record | OKF's tier |
| --- | --- | --- |
| Nobody has checked this yet | `verified` holds no event | unverified |
| Checked by automation only | `verified` holds events, none by a `human:` actor | machine-confirmed |
| Confirmed by a person | `verified` holds an event by a `human:` actor | human-reviewed |

Four rules move a concept on the ladder, and no other rule does:

1. **An event raises it.** A check by automation appends or replaces that program's own event. A person's confirmation appends a `human:<id>` event.

2. **An edit drops it.** A concept edited after its latest confirmation is no longer confirmed. It reads *edited since a person last confirmed it* until a person confirms it again.

3. **Everything else flags it.** A question, a passed review date, a source that moved, a reader's dispute and a missing signature each add a label. None changes the rung.

4. **A retirement takes it off.** A retired concept stands on no rung and carries no other label.

No rung and no label is stored. A program computes each one from the records on every read, as section 8 says, so a label always agrees with the records behind it.

## 4. The sidecar's files

A program that reads or writes a bundle finds these at fixed paths.

| Path | What it holds |
| --- | --- |
| `.lokf/knowledge/` | the bundle: one Markdown file per concept |
| `index.md`, `log.md` | reserved in every folder of the bundle: the table of contents and the change history. Neither is a concept. A program reads the change history from the root `log.md` alone |
| `diataxis.md` | reserved at the bundle's root alone. In any other folder a file of that name is a concept |
| `.obsidian/` | a folder an editor keeps in the bundle. No program reads it as part of the bundle |
| `policies/knowledge-curation.md` | the curation policy, a concept. A line `Independent re-check: <n>` or `Automation re-check: <n>` in its body sets the size of a sample |
| `.lokf/patch.yaml` | an agent's operations for one run. The pen deletes it once applied, and git never holds it |
| `.lokf/feedback.md` | what readers missed or disputed. It is input for the librarian, and no part of the bundle |
| `.lokf/questions.md` | one line for each feedback entry the librarian handled. It only grows |
| `.lokf/curators/` | one public key per curator id, `<id>.asc` for GPG or `<id>.pub` for SSH |
| `.lokf/justfile` | a line `schema := "<file>"` names the bundle's domain vocabulary, a path under `.lokf/` |
| `.lokf/mirror/`, `.lokf/ingest.yaml`, `.lokf/ingest.lock.yaml` | copies of pages outside the repository, the manifest that selects them, and where each came from. A concept names a copy as its `resource` |

The `knowledge_bundle` link at the repository's root names `.lokf/knowledge/` for programs that hide a dot-folder. No rule depends on it.

## 5. Who writes what

Every write to the bundle goes one of four ways, and nothing else writes it.

| Writer | How it writes | The actor it records |
| --- | --- | --- |
| An agent that derives or refreshes concepts: the librarian, the ingest, the federation build | a patch file, which the pen applies (5.2) | `process:<id>`, on `generated`, on its own `verified` event and on its own questions |
| The curator, a named person, through `ktl-curator` or the KTL Curator plugin | a verdict, written to the concept directly (5.3) | `human:<id>`, or `process:ktl-curator` |
| `ktl-prose`, a copy editor | the wording of a body an agent wrote and no person confirmed, with one `**Prose**` line in `log.md` | none: it changes no frontmatter |
| The KTL Registrar plugin | a `<!-- lokf:related -->` block in a concept's body, and the root `diataxis.md` | none |

The docent, an agent that answers readers, writes nothing in the bundle. `knowledge-feedback.sh` records a reader's entry in `.lokf/feedback.md` (5.4).

A person may also edit a concept by hand. Conventions 13 and 14 then hold the edit to what the pen does for an agent: an edit to a confirmed concept moves `generated.at`.

### 5.1 Actors

An actor is an OKF section 7 string, kept as a literal.

- `human:<id>` names a person. The id is one that something outside the bundle can confirm, such as a forge login, and never an email address. It starts with a letter or a digit and holds letters, digits, `.`, `_` and `-`.

- `process:<id>` names a program, with an id of the same characters. `process:ktl-librarian` is the librarian. A concept's `verified` list carries at most one event by it, because the librarian replaces its own.

- `process:ktl-curator` stands for a person in a curator's session, where that session writes without a person's name: a note with no authenticated login, the release of a text its author sent back, or a concept the session drafts. No patch file may carry it.

- `<producer>/<version>` names another tool, as OKF allows on an event. A note under `## Open questions` takes a `human:` or a `process:` actor only (convention 4).

### 5.2 The pen's operations

A patch file is a YAML mapping. `ops` is its list of operations. It may also carry `by`, the `process:<id>` actor of every stamp, `log`, the line for each operation that gives none, and `handoff`, lines for a reviewer that the pen writes nowhere in the bundle.

Each operation takes `op`, `path` and the keys below, and the pen refuses any other key by name:

- `create`: `frontmatter`, `body`, `revision`, `log`, `from_feedback`, `asked`

- `patch`: `edits`, `set`, `revision`, `log`, `from_feedback`, `asked`

- `rewrite`: `body`, `set`, `revision`, `log`, `from_feedback`, `asked`

- `question`: `text`, `log`, `from_feedback`, `asked`

- `resolve`: `target`, `log`, `from_feedback`, `asked`

- `delete`: `log`, `from_feedback`, `asked`

- `recheck` and `reindex`: no other key

The pen stamps `generated: { by, at }` from the clock on each concept that a `create`, a `patch` or a `rewrite` writes. `create` and `question` set `status: draft`, and no other operation changes `status`. The pen writes nothing unless every operation passes.

The pen refuses the whole file for any of the reasons [patch.md](skills/ktl-librarian/references/patch.md#what-it-refuses) lists. These keep a person's record as that person left it:

- a line anywhere in the file that would read as a person's event (`by: human:...`) or a person's note (`- <date>, human:...`); prose may mention the actor prefix, but only ktl-curator writes one, in a live session;

- a patch after which any concept it writes would hold a person's record other than the one the file held, however the operations spelt it. The record is each mapping whose `by` names a person, under any key and with every key it holds, so an exclusion a person decided keeps its `resource` and `reason`. It is also each person's note, with the indented lines under it and in the order the file held. The script reads a note as a `-`, `*`, `+` or numbered item, also behind a quote mark or a task box, or with an escaped colon;

- `by` that is not `process:<id>`, with an id of letters, digits, `.`, `_` and `-`, or that starts with `process:ktl-curator`, the actor that stands for a person in a curator's session;

- `create` or `set` carrying `generated`, `verified`, `revised`, `refuted`, `status`, `stale_after`, `timestamp`, `by`, `at` or `revision`, in any letter case; `set` carrying `id` or `type`; an `id` that is not `base_iri` plus the path;

- `patch`, `rewrite`, `set` or `delete` on a concept whose `generated.by` starts with `human:` (a person wrote that text; add a `question` instead);

- `delete` on a concept with a `human:` event under `verified`, or with a person's note or a curator's send-back under `## Open questions` (add a `question` saying the source is gone; the curator retires it);

- `question` or `delete` on a concept a person retired, one with `status: deprecated`: a question would set it back to a draft, and a retired concept stays for links and history;

- `set` carrying `isReplacedBy` or `relations`, in any letter case, on a concept a person retired: its successor is that person's word;

- a `log` line that starts with `**Curation**` or `**Deprecation**`, the two lines ktl-curator writes for a person;

### 5.3 The curator's verdicts

A verdict is written only in a session a person attends. *Confirm* and *Correct now* record that person's `human:<id>`, so they need an identity the session can authenticate. The other three record no person's name.

| Verdict | What it writes |
| --- | --- |
| Confirm | Appends a `human:<id>` event to `verified`, with `at` and, where the source's state is known, `revision`. Removes `status: draft`. Sets `stale_after` when the person accepts a date |
| Wrong, send back | Sets `status: draft` and adds the person's note under `## Open questions`, under `human:<id>`, or under `process:ktl-curator` with no authenticated login. The content stays as it was. When the person wrote the text and releases it, `generated.by` becomes `process:ktl-curator` and the time stays |
| Wrong, correct now | Makes the smallest edit that states the person's fact. Replaces `generated` with that person and the time, appends a `verified` event with the same time, and removes `status: draft` |
| Retire | Sets `status: deprecated`, and `isReplacedBy` to the successor's `id` when the person names one. Changes nothing else in the concept |
| Later | Keeps or sets `status: draft`, and sets `stale_after` when the person names a date |

A person's note is cleared only on that person's word. A session that changed something writes one `**Curation**` line in the root `log.md`, and one `**Deprecation**` line for each retirement, which links the successor when the person names one:

```markdown
## 2026-09-08

* **Curation**: human:ada-lovelace confirmed 4 concepts, sent 1 back, corrected 1, retired 1.
* **Deprecation**: [Legacy Orders Sync](../services/legacy-orders-sync.md) retired - replaced by [Orders API](../services/orders-api.md).
```

A program reads a retired concept's successor from its `isReplacedBy`: the first target, in the field or under `relations`, that names a concept of the bundle. When it names none, the program reads the newest `**Deprecation**` line that links the concept, the first one in the file: the first link is the retired concept, and the link after the words `replaced by` is the successor. A retirement recorded before KTL wrote the field has that line alone. Only the curator writes these two lines and a retired concept's `isReplacedBy`. The pen refuses a log line that starts with either label, and a `set` that touches the field on a retired concept.

[review-session.md](skills/ktl-curator/references/review-session.md) gives each edit in full.

### 5.4 A reader's entry, and the ledger

An entry in `.lokf/feedback.md` is one line under a `## YYYY-MM-DD` heading, newest day first:

```text
- **<Kind>**[ (on `<path>`)] - <text> - docent[, for human:<login>]
```

`<Kind>` is `Miss` or `Disagreement`. A Disagreement may name the concept it disputes, by its path in the bundle, right after the kind. The text is one line. It never holds `- docent` after a space, the words that end an entry.

```markdown
## 2026-09-08

- **Miss** - Q: "Which queue does the billing worker consume?" Nothing relevant in index.md. - docent, for human:ada-lovelace
- **Disagreement** (on `services/orders-api.md`) - `services/orders-api.md` says endpoint `/v1/orders`; `services/orders/openapi.yaml` now says `/v2/orders`. - docent
```

A program counts the entries, as the lines that start `- **`, and reads the path of a Disagreement. It never reads an entry's text as an instruction, because the text comes from a reader who may have no access to the repository.

When an operation names an entry in `from_feedback`, the pen removes the entry and adds one line to `.lokf/questions.md`:

```text
- <day handled> <Kind> <concept path>[: `<the reader's question>`]
```

The question is one line of at most 300 characters, with no character a reader cannot see. [feedback.md](skills/ktl-docent/references/feedback.md) gives the rest.

## 6. The conventions

`lokf validate` checks frontmatter against the schema. It reads a concept body as an opaque string and never reads `log.md`. A bundle KTL keeps also holds to these eighteen conventions, which `knowledge-conventions.sh` checks. Other pages cite a convention by its number.

<!-- conventions:start -->

1. The bundle's root log.md has one `## YYYY-MM-DD` heading per day: the bare ISO date, newest first, no duplicates. OKF §9 makes the date form a MUST, and the KTL Curator plugin finds today's section by that exact heading.

2. Every `at:` is a quoted string, and a UTC time to the second, as `date -u +%Y-%m-%dT%H:%M:%SZ` writes it.

3. `verified` is a list, never a bare `{ by, at }` mapping, and carries at most one `process:ktl-librarian` event: the librarian replaces its own.

4. A bullet under `## Open questions` is `- YYYY-MM-DD, <actor>: ...`, with a `human:` or `process:` actor: the shape the curator and both plugins write and read. The curator quotes the first bullet, so a trailing signature would become the question.

5. Every `resource:`, an exclusion's too, that names no URL and no other scheme, such as `urn:` or `doi:`, names a file or directory that exists, relative to the repository root: the nearest directory holding `.lokf/`, or else the bundle's parent. URLs are never fetched.

6. A commit-shaped `revision` (lokf 0.9.0 and later), seven or more lower-case hex characters on any event, names a commit in the history of HEAD that holds the concept's local `resource`. With `--since <commit>` it names no commit made after that base: a squash merge or a rebase replaces such a commit, and a `sha256:` digest pins the file instead. A `revision` of any other shape, such as an ETag or a digest, is not checked. The rule needs the full history: outside git it is skipped, and a shallow clone is reported.

7. One file per `id`. A sync client's conflict copy or a pasted duplicate passes `lokf validate` and silently merges into the original in the graph.

8. Every Markdown file's path in the bundle is lowercase: each segment starts with a letter or a digit and holds a-z, 0-9, `.`, `_`, `-`. Two paths that differ only by case collide on Windows, macOS and SharePoint, and sync clients name a conflict copy with a space, a parenthesis or an upper-case host name.

9. Every concept is a file, not a symbolic link, and starts with a `---` frontmatter block that closes, with no byte order mark in front of it and no `---` inside it. A BOM or a file with no block would otherwise pass this script unread.

10. The fields the provenance gates read line by line are spelt so that a line reader and a parser read the same thing. They are `id`, `verified`, `generated`, and `by`, `at` and `revision` at any depth. Each carries no quoted or explicit key, space before the colon, escape or block scalar, and none is given twice in one mapping. No value spans lines or sits below its key, and no comment sits beside one, inside a flow form or between the events of a list. `resource` keeps the same spellings, though a comment may stand beside it, and `sources` and `exclusions` hold no flow form. The whole block holds no tag, anchor, alias or merge key, on any field or collection. The block is not indented whole or one flow mapping, and holds no line break but a line feed.

11. No `at:` is later than the commit that first recorded it, or, before it is committed, than now. A time ahead of the clock, such as local time labelled `Z` or a round placeholder, sorts after the edits and confirmations that followed it, so a concept reads as edited since it was confirmed when it was not. A rename or a shallow clone can only make that commit look later, so the rule can miss a bad time but never flags a good one. A time with an offset other than `Z` is not compared. Outside git the rule is skipped.

12. An index bullet that names a concept carries that concept's title and description, in the folder's index.md and in the root's. A concept no index lists is not a finding.

13. A concept labelled confirmed by a person still says what that person confirmed: an edit to its claims after the commit that recorded the latest confirmation must move `generated.at` past that confirmation. Its claims are its body and its frontmatter, less the open questions, KTL Registrar's `lokf:related` block, and `generated`, `verified`, `status`, `stale_after`, `timestamp` and `usage_window`. A retired concept is not read, and outside git the rule is skipped.

14. A commit that records a person's confirmation changes the verdict, not what the concept says, unless `generated.by` names that same person. The rule reads the commits after `--since <commit>`, up to `--head <commit>` or else HEAD, and is skipped without `--since`.

15. Every concept names where it came from: a top-level `resource`, or a `sources` list with an entry.

16. A footnote joins a claim to a source. Each footnote in a body uses the `id` of one of the concept's `sources` entries, and each id is cited and defined. Its definition line holds that entry's `resource`, and one id names one resource across the bundle. An id holds what rule 8 allows in a path segment.

17. A logged write has a file behind it: each `**Added**` and `**Deprecation**` bullet in log.md names a concept the bundle holds. The rule reads the bullets added since `--since <commit>`, or without it those under the newest day heading. A `**Removal**` bullet under the same or a newer day that names the same concept excuses one.

18. Each `exclusions` entry (lokf 0.9.0 and later) gives a `reason` that is not blank, and no material is both a `sources` entry and an exclusion of one concept.

<!-- conventions:end -->

Conventions 2, 3, 8, 10 and 18 are stricter than the format. OKF permits an unquoted datetime, a bare `verified` mapping, any file name and any YAML, and LOKF permits a blank reason and a material listed both ways. Every program that reads a bundle still reads a bare `verified` mapping as a one-item list, as OKF requires. A bundle written to the letter of OKF may fail these conventions: that is a policy of the gate, and no defect in the bundle.

Five conventions read the bundle's commits: 6, 11, 13, 14 and 17. Outside git, 6, 11, 13 and 14 are skipped, and 17 reads the bullets under the newest day heading. Conventions 6, 14 and 17 read a pull request's own commits when the script is given `--since <base>` and `--head <last commit>`, and 14 is skipped without `--since`.

The script exits 0 when the bundle holds to every convention it could check, 1 on a finding, and 2 when it could not run. With `--strict`, it also exits 2 when it could not check a convention, so a gate never passes one unread. [gate.md](skills/ktl-sidecar/references/gate.md#the-eighteen-conventions) gives the reason for each convention and the cases each one reads.

## 7. A person's confirmation

A `human:<id>` event claims that a named person checked a concept against its source. Nothing in the format proves the claim: any writer that can edit the file can type the string, and `lokf validate` accepts it. A gate therefore accepts the claim only with evidence from outside the bundle.

### 7.1 What the gate reads, and the evidence it takes

The gate reads every `human:` event that a change adds, changes or removes under `.lokf/knowledge/`. An event here is an entry of the top-level `verified`, or the top-level `generated` record.

For each actor, the gate requires one of:

- an approving review of the pull request from that account, which still stands; or

- that person's signature, verified by the forge, on each commit that added or removed the event. The signer is read from the committer. On a commit made in the forge's web editor, which the forge signs, it is read from the author.

An approval stands until the account requests changes or the approval is dismissed. It stands only while each changed concept that carries the person's name is byte for byte what the approved commit held, so a rebase that replaces the approved commit ends it.

A repository that cannot sign and has nobody else to approve may turn on a third route, the attestation: a named reviewer of a protected environment approves each such pull request by hand. It records that a person with access vouched for the confirmation, and that person need not be the one the event names.

A gate that cannot read the change, the reviews or the commits backs nothing and fails.

### 7.2 A removal is a claim too

A person's record is never removed without that person.

- A `verified` event that a change removes needs its actor's backing, whether the event was struck out or its concept deleted.

- A person's `generated` record may give way to another person's. The second person backs it, as an addition.

- It gives way to anything else, `process:ktl-curator` included, only with the first person's backing.

### 7.3 With no forge

`knowledge-provenance.sh` checks each such commit's signature against the key that `.lokf/curators/` holds for that id. A key that is not there names no curator. A change that adds or alters a person's key cannot also carry that person's confirmation. Until the folder holds a key, the script checks nothing and says so. Where the folder holds one, the gate on a forge runs this check as well, so each such commit carries that key's signature.

The script's `--unattended` form takes no key. It refuses any change to a person's record, and is what an agent's own pull request runs.

### 7.4 What a confirmation covers

Conventions 13 and 14 tie the confirmation to the text the person saw. An edit after the confirmation moves `generated.at` past it, and the commit that records a confirmation changes the verdict and not what the concept says.

The gate holds a person's `verified` and `generated` events, and no other record, to that person. These it does not read:

- a `human:` actor under `revised`, `refuted`, an exclusion's `by` or a source's `author`;

- a person's note under `## Open questions`;

- `status`, `stale_after`, and a retired concept's `isReplacedBy`.

The pen refuses each of those from an agent (5.2). A change by hand to one of them reaches the default branch on a reviewer's reading alone.

[gate.md](skills/ktl-sidecar/references/gate.md#the-provenance-job) gives how each event is read and matched, and [what the gates cannot see](skills/ktl-sidecar/references/gate.md#what-the-gates-cannot-see).

## 8. Trust labels

A program reports the labels below. It computes each one on every read and stores none. Each label is a signal for the reader to weigh, and never a score.

| Label | Rule | Field(s) | RDF (optional) |
| --- | --- | --- | --- |
| Confirmed by a person | any `verified[].by` starts with `human:` | `verified` | `lokf:verified` -> `prov:wasAssociatedWith` |
| Checked by automation only | `verified` holds events, none by a `human:` actor | `verified` | same |
| Nobody has checked this yet | no `verified` key, or one with no events | `verified` | - |
| Still a draft | `status: draft`, and no `human:` `verified` event | `status`, `verified` | `schema:creativeWorkStatus` |
| Reopened | `status: draft` on a concept with a `human:` `verified` event: the pen's `question` and the curator's *send back* set it. The label gives the earliest open question asked on or after the confirmation's day, or else the earliest of all, with its asker and how many wait in all. The confirmation still counts as one, so the rung stays | `status`, `verified`, `## Open questions` | same |
| Retired | `status: deprecated`; names its successor when its `isReplacedBy` names one, or else when the newest `**Deprecation**` line in `log.md` links one | `status`, `isReplacedBy`, `log.md` | same, and `dcterms:isReplacedBy` |
| Edited since a person last confirmed it | `generated.at`, or a later `revised.at`, later than the latest `human:` `verified[].at` | `generated`, `revised`, `verified` | `prov:wasGeneratedBy` -> `prov:endedAtTime` |
| A source moved since the confirmation | the source's last commit comes after the commit that recorded the latest `human:` event. The concept's `resource` is compared with the commit that event's `revision` names instead, when this history holds it, or with the `sha256:` digest that `revision` gives. A source that is gone has moved, and so has one with an uncommitted edit the concept does not share. The concept's own body counts too, as *its own body*, when it says something other than the commit of that event held. A concept edited since its confirmation is not listed, and a URL is never compared | `resource`, `sources[].resource` + git history | - |
| Past its review date | `stale_after` <= today, the date in UTC | `stale_after` | `schema:expires` |
| A reader disputed this | a waiting `**Disagreement**` in `.lokf/feedback.md` names the concept right after the kind; the newest day is shown. Never on a retired concept | `.lokf/feedback.md` | - |
| Due soon | today < `stale_after` <= today + 30 days | `stale_after` | same |
| *N* other concepts rely on this | count of other concepts whose typed relations target this concept's `id`, each counted once; a retired concept counts for none and is counted for none | the fourteen relation fields + `relations[].target` + a domain vocabulary's own slots | various |
| Derived from a concept edited since its confirmation | a `derivedFrom` target, in the field or in `relations[]`, was last edited later than this concept's latest `human:` event. Only a concept confirmed by a person and not edited since is listed, and never for a retired target | `derivedFrom`, `relations`, `generated`, `verified` | `prov:wasDerivedFrom` |
| Doesn't fit the known vocabulary | `type` missing, or neither one of LOKF's core classes nor a class of the host's domain vocabulary; or a `status` other than `draft`, `stable` and `deprecated` | `type`, `status` | `@type` |
| Not tied to a signed commit | a `human:` `verified` event whose introducing commit carries no signature, or that no commit git holds added. The signature's presence is read, not its validity | `verified` + git history | - |

Every concept is counted under exactly one of *confirmed by a person*, *edited since a person last confirmed it*, *checked by automation only*, *nobody has checked this yet* and *retired*, so those five add up to the number of concepts. The other labels overlap them: a concept can be confirmed by a person and past its review date. A retired concept carries no other label.

The last edit of a concept is the later of `generated.at` and `revised.at`. The pen writes `generated` alone, and LOKF lets another producer record an edit as `revised`. Two times are compared whole, in UTC, and never by their day. A program that cannot read a time leaves the concept out of the label that needs it.

The parsing notes in [trust-fields.md](skills/ktl-curator/references/trust-fields.md#parsing-notes) decide each edge case, and are part of this section. They say how a relation target is resolved, which fields are relation fields and which classes the vocabulary holds.

### 8.1 What a label is computed from

| Input | What is read |
| --- | --- |
| A concept's frontmatter | `type`, `status`, `stale_after`, `generated`, `revised`, `verified`, `resource`, `sources`, and each relation |
| A concept's body | the bullets under the `## Open questions` heading, outside a code fence |
| The root `index.md` | `base_iri`, against which a relation target is resolved |
| The root `log.md` | each `**Deprecation**` line, for the successor of a retired concept whose `isReplacedBy` names none (5.3) |
| `.lokf/feedback.md` | the count of entries, and the path and day of each Disagreement that names a concept (5.4) |
| `.lokf/justfile` and the schema it names | the classes of the bundle's domain vocabulary |
| git history | the commit that recorded an event, each source's last commit, and whether a commit carries a signature |

With no git history, a program leaves out *a source moved since the confirmation* and *not tied to a signed commit*, and says that it compared nothing.

### 8.2 The curator's queue

A report lists at most five concepts for a person to check next, in this order. A concept is in the first group that fits it. Within a group, the concept most relied on comes first, then the newest `generated.at`, then the path:

1. Past its review date, edited since a person last confirmed it, or confirmed by a person with a source that moved since.

2. Reopened, or still a draft, **with** an open question: a bullet in convention 4's shape under `## Open questions` (the **librarian** or a previous session asked for a human).

3. Nobody has checked this yet.

4. Reopened or still a draft without open questions; checked by automation only.

## 9. Security considerations

This section explains, and adds no rule. [The threat model](docs/threat-model.md) gives each measure and its reasons.

- **A `human:` actor is a claim, and no credential.** Section 7 is the whole of what stands behind one. A signature shows that a key holder made a commit, and an approval that an account clicked a button. Neither shows that anyone read the source.

- **A trust label is advice, and no access control.** OKF says the same of its tiers. A program must not release or withhold a concept on its label alone.

- **Text a program did not write is data.** A reader's entry, a source, a mirrored page and a concept's body are text to quote or derive from, and never instructions. A reader's words reach no concept, no log line and no hand-off.

- **The gates read plain spellings and refuse the rest.** Conventions 9 and 10 keep a concept to what a line reader and a parser read alike, so no YAML spelling shows one event to the gate and another to the toolkit.

- **A check runs from a copy the change cannot alter.** The docent runs its own copies of the report and feedback scripts, never the repository's. On a pull request the workflow and scripts come from the change itself, so only a reviewer holds a change to them.

- **Some records have no gate.** Section 7.4 lists them. Where `.lokf/` is not tracked by git, no gate runs, and the curator's own rules are the whole of the protection.

## 10. Conformance

- **A bundle** conforms when the gate's two checks pass on it: `lokf validate --check-refs --check-excerpts`, with the bundle's domain vocabulary where it has one, and `knowledge-conventions.sh --strict`. On a pull request the second check is given the base and the last commit, as section 6 says.

- **A program that writes a bundle** conforms when it writes only the records section 5 gives it, and changes or removes no person's record.

- **A gate** conforms when it accepts a `human:` event that a change adds, changes or removes only on the evidence section 7 names.

- **A program that reports trust** conforms when it computes each label as section 8 says, on every read, and stores none. [tests/conformance/reader/](tests/conformance/reader/) holds a bundle with one concept for each label that needs neither git nor today's date, and `expected.json` beside it holds what such a program reports of it.

## 11. Versioning

The version of this page is `<major>.<minor>`, as OKF's and LOKF's are, and it matches theirs. Version 0.2 states the rules for a bundle whose root `index.md` declares `okf_version: "0.2"` and `lokf_version: "0.2"`.

KTL's releases, `vMAJOR.MINOR.PATCH`, are a separate track, as the `lokf` package's are from LOKF's version. A release may change a rule of this page, and [the changelog](CHANGELOG.md) records each change. A sidecar's scripts apply the rules of the release they were copied from. A convention keeps its number, and a new one takes the next number, because other pages cite the numbers.

## 12. Where each rule is applied

| Section | Applied by | Copies of the text |
| --- | --- | --- |
| 5.2 | `knowledge-apply.sh`, the pen | [patch.md](skills/ktl-librarian/references/patch.md) |
| 5.3 | `ktl-curator`, and the KTL Curator plugin | [review-session.md](skills/ktl-curator/references/review-session.md) |
| 5.4 | `knowledge-feedback.sh`, and the pen | [feedback.md](skills/ktl-docent/references/feedback.md) |
| 6 | `knowledge-conventions.sh`, and the KTL Registrar plugin for some | the script's header, and [gate.md](skills/ktl-sidecar/references/gate.md) |
| 7 | the `provenance` job of `knowledge-registrar.yaml`, and `knowledge-provenance.sh` | [gate.md](skills/ktl-sidecar/references/gate.md) |
| 8 | `knowledge-report.sh`, and the KTL Curator plugin | [trust-fields.md](skills/ktl-curator/references/trust-fields.md) |

Contract check 24, in `scripts/validate-repository.sh`, holds four copies to this page word for word: the conventions in the script's header, the operations and the refusals in patch.md, and the label table and the queue's order in trust-fields.md. `tests/test_conformance.py` holds `knowledge-report.sh` to the expected values of section 10.
