# Review session - exact edits, identity, log, handoff

## Who is recording

One source, resolved once per session, and confirmed aloud before the first write ("I'll record your answers as `human:<id>` - ok?"):

```sh
gh api user --jq .login
```

A GitHub login: stable, matching `CODEOWNERS`, and - the reason it is now the only accepted source - the identity that `knowledge-registrar.yaml`'s `provenance` job can check an event against afterwards, by asking whether that account approved the pull request carrying it.

The two fallbacks this skill used to allow are gone, and it matters why:

- **`git config user.name`** is an ordinary writable config value. Anything with shell access to the checkout can set it to a maintainer's slug before the session starts.
- **Asking** takes the identity from the conversation - the one channel an attacker fully controls. A name typed at you is a claim, not an identity.

**With no authenticated login**, *Confirm* and *Correct now* are unavailable for the session. Say so, and offer the three verbs that assert nothing about who checked what: *Wrong - send back*, *Retire*, *Later*. Do not fall back, do not guess, and never write a `human:` event whose id you cannot name a source for.

**Non-GitHub forges**: use the identity behind signed commits (the key in `git config user.signingkey`, resolved to that forge's account) together with that forge's approval gate. The principle is the rule, not the tool - the id must be one that something outside the bundle can independently confirm.

Never use an email address - the bundle may be public. The actor string is `human:<id>` exactly (OKF §7); it is a literal, never turned into a link.  Timestamps are UTC, ISO 8601, quoted in YAML: `"2026-09-08T14:00:00Z"`.

## Before the first verb: will the gate accept this?

Only when `.lokf/` is git-tracked **and** `.github/workflows/knowledge-registrar.yaml` exists. Two cheap questions:

```sh
git config --get commit.gpgsign                      # is signing on at all?
git cat-file commit HEAD | grep -qE '^gpgsig' \
  && echo "HEAD is signed" || echo "HEAD is unsigned"
```

If signing is off and this person would be the one opening the curation PR, tell them before they spend twenty minutes confirming things. GitHub does not let anyone approve their own pull request, so the `provenance` job's only remaining evidence is their signature - and without it every confirmation from this session is rejected at the gate.

What to say, and what not to do:

- Show the three `git config` lines from lokf-sidecar's [`references/automation.md`](../../lokf-sidecar/references/automation.md), and the part that catches people out: the same key must also be added at `github.com/settings/keys` **as a signing key**, because the job reads GitHub's verdict, not the local one.
- **Never run them yourself.** This skill records what a person says; it does not reconfigure their machine. A `--global` change would alter how they commit in every unrelated repository, and a wrong `user.signingkey` breaks `git commit` everywhere until they find it.
- A committed `.gitconfig` is not an option, and it is worth saying so when someone suggests it: git reads only `.git/config`, `~/.gitconfig`, and system config - never a file in the working tree. Git refuses this deliberately, since a config file arriving with a clone could otherwise run commands. A tracked one sits there doing nothing.
- Then carry on regardless. It is their call, and *Wrong - send back*, *Retire* and *Later* record no `human:` actor, so they pass the gate untouched.

## The verbs

Every example starts from this librarian-written frontmatter:

```yaml
type: Service
id: https://acme.example/knowledge/services/orders-api
title: Orders API
description: REST API serving order data to the CLI and web UI.
resource: services/orders/openapi.yaml
generated:
  by: process:lokf-librarian
  at: "2026-09-01T05:00:00Z"
verified:
  - by: process:lokf-librarian
    at: "2026-09-07T05:00:00Z"
status: draft
```

### Confirm

Append the person's event (keep every existing event; if `verified` is a bare mapping, turn it into a one-element list first), remove `status: draft`
(absent means stable), and propose `stale_after` from the curation policy - write it only after they accept or edit the date:

```yaml
verified:
  - by: process:lokf-librarian
    at: "2026-09-07T05:00:00Z"
  - by: human:ada-lovelace
    at: "2026-09-08T14:00:00Z"
    revision: "3f9c2a1b7e0d4c6a8f5e2d1c9b8a7f6e5d4c3b2a"
stale_after: 2027-03-08
```

`revision` is the state of the `resource` you quoted from in the evidence-first step, so a later reader can tell whether the page they see is the one the confirmation rested on. For a committed path in the repository, the last commit that touched it: `git log -1 --format=%H -- <path>`, the full hash, since an abbreviation can become ambiguous as the repository grows and the registrar gate resolves the pin against the tree; if the file has uncommitted changes, say so and leave the key out. For a URL, the `ETag` header if the server sends one, else `sha256:` plus the digest of the body you quoted from (`curl -sL <url> | sha256sum`) - and prefer the ETag, since a digest of a page that changes on every fetch cannot later tell "the source moved" from "the page is dynamic". Always quoted, like `at`: an all-digit commit id is otherwise read as a number and fails `lokf validate`, and an ETag carries its own double quotes (`revision: 'W/"33a64df5"'`). Several `sources`: the `resource`'s revision only. Leave the key out rather than guess, and leave it out on a toolkit older than lokf 0.9.0, whose validator rejects it (`uv run lokf --version` in `.lokf/`).

If the body has an `## Open questions` section and the person says those are answered, delete the section. Otherwise leave it.

### Wrong - send back (default)

Content untouched. Set `status: draft` (add it if absent) and add the person's note in plain prose under `## Open questions` at the end of the body, attributed and dated:

```markdown
## Open questions

- 2026-09-08, human:ada-lovelace: the endpoint moved to `/v2/orders` in July; this still shows the old path. Please re-derive from `services/orders/openapi.yaml`.
```

The librarian's next run reads this, fixes the fact from the source, and the concept comes back to the queue as a draft for re-confirmation.

### Wrong - correct now

Only when the person states the correct fact themselves. Make the smallest edit that expresses it (the one field, or the one sentence), then mark the content as human-authored and confirmed, and remove `draft`:

```yaml
endpoint: https://api.acme.example/v2/orders
generated:
  by: human:ada-lovelace
  at: "2026-09-08T14:05:00Z"
verified:
  - by: process:lokf-librarian
    at: "2026-09-07T05:00:00Z"
  - by: human:ada-lovelace
    at: "2026-09-08T14:05:00Z"
```

This is the widest verb in the skill, and the only one that writes *content*: what it stamps as human-authored, lokf-librarian will not rewrite (section 1), so a wrong fact recorded here survives every later refresh and is caught only if the repository actively contradicts it. Use it only for a fact the person states themselves, keep the edit as small as that fact, and never reach for it when *Wrong - send back* would do.

`generated` is replaced, not appended - it records who produced the *current* content. From now on the librarian will not rewrite this concept; if the repository later disagrees, it raises an open question instead (lokf-librarian, section 1). Never propose the correction yourself; if you think you know it, say so and let them decide.

### Retire

```yaml
status: deprecated
```

Nothing else changes. Retired concepts stay for links and history; the librarian leaves them alone.

### Later

Keep or set `status: draft`. If they name a date, write `stale_after`. No other edits.

## Log lines

Prepend under today's `## YYYY-MM-DD` heading in `.lokf/knowledge/log.md` (newest first, ISO date, matching the librarian's convention). Today's heading is the bare date and there is exactly one of it: reuse it if the librarian or an earlier session already wrote it today, create it at the top only if absent, and never a suffixed variant such as `## 2026-09-08 (2)` - the LOKF Curator plugin finds the day by the bare date and would open a second section beside one it cannot see. One line for the session and one per retirement:

```markdown
## 2026-09-08

* **Curation**: human:ada-lovelace confirmed 4 concepts, sent 1 back, corrected 1, retired 1.
* **Deprecation**: [Legacy Orders Sync](../services/legacy-orders-sync.md) retired - replaced by the Orders API.
```

Write no log line for a session that changed nothing.

## The curation policy concept

Create `policies/knowledge-curation.md` on the first Step 3 request (or when the person asks "how often should we re-check things?"). It is a normal concept: the person reviews and confirms it like any other. Plain words; they edit the defaults:

```markdown
---
type: Policy
id: <BASE_IRI>policies/knowledge-curation
title: Knowledge curation policy
description: How often each kind of concept in this bundle is re-confirmed by a person, and who does it.
generated:
  by: human:<id>
  at: "<now>"
verified:
  - by: human:<id>
    at: "<now>"
---

# Who curates

<team or people, plain names - link to Person/Organization concepts if they exist>

# How often a person re-confirms

| Kind of concept | Re-confirm every |
| --- | --- |
| Services, datasets, tables, metrics, attested computations | 6 months |
| Policies, playbooks, tutorials, references, documents, people, organizations | 12 months |
| Glossary terms, explanations | 24 months |

The lokf-curator skill proposes `stale_after` from this table when a person confirms a concept. Change the table, not the skill.

# What "confirmed" means here

A named person opened the concept's source and agreed the concept still says what the source says. Automation re-checking that a file still exists is recorded separately and is not confirmation.

# Independent re-check

Independent re-check: 0

Set above zero and every lokf-curator report lists that many concepts confirmed by a person, picked by a rule the curator cannot steer, with their sources, for someone other than the person who confirmed them. Their verdict is recorded as a separate `verified` event. How often that second person acts on the list is for the team to set here in words.

# How the docent answers

Evidence first: no

Set to yes and lokf-docent quotes the source before any answer that rests on a concept not yet confirmed by a person. Slower to read, harder to over-trust.
```

Step 1's report reads the `Independent re-check:` line and lokf-docent reads `Evidence first:`; both are optional, and absent means off.

Derive `stale_after` as *confirmation date + the row's interval*, and always show the date before writing it. Read the table tolerantly: a row names its classes in prose, so match ignoring spaces and plural form - "Glossary terms" is `GlossaryTerm`, "attested computations" is `AttestedComputation`, "Policies" is `Policy`, "people" is `Person` - and a row naming a class you do not know binds nothing. A host that extends the vocabulary with a domain schema may set an interval for its own classes the same way.

## Recording something missing

When the person reports that the bundle lacks something ("there's no concept for the billing worker"), write a placeholder for the librarian - type, title, and one open question only. Never fill in facts you don't have:

```markdown
---
type: Service
id: <BASE_IRI>services/billing-worker
title: Billing worker
description: Placeholder - not yet derived from the repository.
status: draft
generated:
  by: human:<id>
  at: "<now>"
---

## Open questions

- <date>, human:<id>: reported missing. Librarian: derive from the repository (they mention `workers/billing/`).
```

Add a bullet to the nearest `index.md`? No - `index.md` is the librarian's; it will add the bullet when it fills the placeholder. Log the intake as part of the session's `**Curation**` line ("recorded 1 gap").

## Handing off

Git-tracked `.lokf/`: open a pull request scoped to `.lokf/` titled "Curation: <date>", body = the health line before and after, the verbs taken, and the `just lokf-validate` output (or "validation skipped - no `uv`"). The `knowledge-registrar.yaml` gate, if scaffolded, runs on it - including its `provenance` job, which re-checks every `human:` event the PR adds: each named person must have approved the pull request, or, when the PR is their own (GitHub won't let authors approve themselves), have signed its commits. Tell the person plainly that the PR needs their approval or signature before the confirmations they just gave will pass - and if they are the repository's only maintainer, that GitHub will not let them approve their own PR, so signing their commits is the path (lokf-sidecar's `references/automation.md` has the three-line setup). That is the gate working, not a snag in it: it is what makes their confirmation something a later reader can check rather than take on faith.

Gitignored `.lokf/`: there is no diff to show; hand the person the list of changed files and the health line instead.
