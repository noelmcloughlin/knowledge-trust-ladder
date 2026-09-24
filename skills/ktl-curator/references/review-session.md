# Review session: exact edits, identity, log, handoff

## Who is recording

Resolve the id from one source, once per session, and confirm it aloud before the first write ("I'll record your answers as `human:<id>` - ok?"). The preflight (`.lokf/scripts/knowledge-preflight.sh`) has already named it. The routes are, in order of preference:

```sh
gh api user --jq .login        # GitHub
glab api user                  # GitLab: the "username" field
```

A forge login is stable and matches `CODEOWNERS`. It is the accepted source because it is the identity the `provenance` gate can check an event against afterwards: the gate asks whether that account approved the pull request carrying the event, or signed the commit. With neither CLI, the third route resolves the local signing key to a forge account through the forge's public key listing. With no forge at all, the id is the account the host platform's version history shows. Both are spelled out, host by host, in [portability.md](portability.md).

The two fallbacks this skill used to allow are gone, and it matters why:

- **`git config user.name`** is an ordinary writable config value. Anything with shell access to the checkout can set it to a maintainer's slug before the session starts.
- **Asking** takes the identity from the conversation, the one channel an attacker fully controls. A name typed at you is a claim, not an identity.

**With no authenticated login**, *Confirm* and *Correct now* are unavailable for the session. Say so, and offer the three verbs that assert nothing about who checked what: *Wrong - send back*, *Retire*, *Later*. Do not fall back, do not guess, and never write a `human:` event whose id you cannot name a source for.

**Other forges, and no forge** are covered in [portability.md](portability.md). The principle is the rule, not the tool: the id must be one that something outside the bundle can independently confirm.

Never use an email address, since the bundle may be public. The actor string is `human:<id>` exactly (OKF §7). It is a literal, never turned into a link. Timestamps are UTC, ISO 8601, and quoted in YAML: `"2026-09-08T14:00:00Z"`.

## Before the first verb: will the gate accept this?

Check this only when `.lokf/` is git-tracked **and** `.github/workflows/knowledge-registrar.yaml` exists. Ask two cheap questions:

```sh
git config --bool --get commit.gpgsign               # is signing on at all? (yes/on/1 read as true)
git cat-file commit HEAD | grep -qE '^gpgsig' \
  && echo "HEAD is signed" || echo "HEAD is unsigned"
```

If signing is off and this person would be the one opening the curation PR, tell them before they spend twenty minutes confirming things. GitHub does not let anyone approve their own pull request, so the `provenance` job's only remaining evidence is their signature. Without it, every confirmation from this session is rejected at the gate.

What to say, and what not to do:

- Show the three `git config` lines from ktl-sidecar's [`references/gate.md`](../../ktl-sidecar/references/gate.md), and the part that catches people out: the same key must also be added at `github.com/settings/keys` **as a signing key**, because the job reads GitHub's verdict, not the local one.
- **Never run them yourself.** This skill records what a person says; it does not reconfigure their machine. A `--global` change would alter how they commit in every unrelated repository, and a wrong `user.signingkey` breaks `git commit` everywhere until they find it.
- A committed `.gitconfig` is not an option, and it is worth saying so when someone suggests it: git reads only `.git/config`, `~/.gitconfig`, and system config, never a file in the working tree. Git refuses this deliberately, since a config file arriving with a clone could otherwise run commands. A tracked one sits there doing nothing.
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
  by: process:ktl-librarian
  at: "2026-09-01T05:00:00Z"
verified:
  - by: process:ktl-librarian
    at: "2026-09-07T05:00:00Z"
status: draft
```

### Confirm

Append the person's event, keeping every existing event; if `verified` is a bare mapping, turn it into a one-element list first. Remove `status: draft` (absent means stable). Propose `stale_after` from the curation policy, and write it only after they accept or edit the date:

```yaml
verified:
  - by: process:ktl-librarian
    at: "2026-09-07T05:00:00Z"
  - by: human:ada-lovelace
    at: "2026-09-08T14:00:00Z"
    revision: "3f9c2a1b7e0d4c6a8f5e2d1c9b8a7f6e5d4c3b2a"
stale_after: 2027-03-08
```

`revision` is the state of the `resource` you quoted from in the evidence-first step, so a later reader can tell whether the page they see is the one the confirmation rested on. Fill it like this:

- **A committed path in the repository**: the last commit that touched it, `git log -1 --format=%H -- <path>`, as the full hash. An abbreviation can become ambiguous as the repository grows, and the registrar gate resolves the pin against the tree. If the file has uncommitted changes, or the host has no version control, say so and leave the key out.
- **A URL**: the `ETag` header if the server sends one, else `sha256:` plus the digest of the body you quoted from (`curl -sL <url> | sha256sum`; `shasum -a 256` on macOS). Prefer the ETag: a digest of a page that changes on every fetch cannot later tell "the source moved" from "the page is dynamic".
- **Several `sources`**: the `resource`'s revision only.

Quote it always, like `at`. An all-digit commit id is otherwise read as a number and fails `lokf validate`, and an ETag carries its own double quotes (`revision: 'W/"33a64df5"'`). Leave the key out rather than guess, and leave it out where the toolkit rejects it. Every released version does, since the field is proposed for lokf 0.9.0 and not yet shipped (`uv run lokf --version` in `.lokf/`).

If the body has an `## Open questions` section and the person says those are answered, delete the section. Otherwise leave it.

### Wrong - send back (default)

Leave the content untouched. Set `status: draft` (add it if absent) and add the person's note in plain prose under `## Open questions` at the end of the body, attributed and dated:

```markdown
## Open questions

- 2026-09-08, human:ada-lovelace: the endpoint moved to `/v2/orders` in July; this still shows the old path. Please re-derive from `services/orders/openapi.yaml`.
```

With no authenticated login, the actor is the session: `- 2026-09-08, process:ktl-curator: ...`, with any note about the missing login after the colon. `human:<id>` and `process:<name>` are the only actor shapes conventions rule 4 accepts. A typed name or a description of the session there fails the gate.

The librarian's next run reads this, fixes the fact from the source, and the concept comes back to the queue as a draft for re-confirmation.

### Wrong - correct now

Use this only when the person states the correct fact themselves. Make the smallest edit that expresses it (the one field, or the one sentence), then mark the content as human-authored and confirmed, and remove `draft`:

```yaml
endpoint: https://api.acme.example/v2/orders
generated:
  by: human:ada-lovelace
  at: "2026-09-08T14:05:00Z"
verified:
  - by: process:ktl-librarian
    at: "2026-09-07T05:00:00Z"
  - by: human:ada-lovelace
    at: "2026-09-08T14:05:00Z"
```

This is the widest verb in the skill, and the only one that writes *content*. ktl-librarian will not rewrite what it stamps as human-authored (section 1), so a wrong fact recorded here survives every later refresh and is caught only if the repository actively contradicts it. Use it only for a fact the person states themselves, keep the edit as small as that fact, and never reach for it when *Wrong - send back* would do.

`generated` is replaced, not appended: it records who produced the *current* content. From now on the librarian will not rewrite this concept. If the repository later disagrees, it raises an open question instead (ktl-librarian, section 1). Never propose the correction yourself. If you think you know it, say so and let them decide.

### Retire

```yaml
status: deprecated
```

Nothing else changes. Retired concepts stay for links and history; the librarian leaves them alone.

### Later

Keep or set `status: draft`. If they name a date, write `stale_after`. No other edits.

## Log lines

Prepend under today's `## YYYY-MM-DD` heading in `.lokf/knowledge/log.md` (newest first, ISO date, matching the librarian's convention). Today's heading is the bare date, and there is exactly one of it. Reuse it if the librarian or an earlier session already wrote it today, and create it at the top only if absent. Never write a suffixed variant such as `## 2026-09-08 (2)`: the KTL Curator plugin finds the day by the bare date and would open a second section beside one it cannot see. Write one line for the session and one per retirement:

```markdown
## 2026-09-08

* **Curation**: human:ada-lovelace confirmed 4 concepts, sent 1 back, corrected 1, retired 1.
* **Deprecation**: [Legacy Orders Sync](../services/legacy-orders-sync.md) retired - replaced by the Orders API.
```

Write no log line for a session that changed nothing.

## The curation policy concept

Create `policies/knowledge-curation.md` on the first Step 3 request (or when the person asks "how often should we re-check things?"). It is a normal concept: the person reviews and confirms it like any other. Write it in plain words; they edit the defaults:

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

The ktl-curator skill proposes `stale_after` from this table when a person confirms a concept. Change the table, not the skill.

# What "confirmed" means here

A named person opened the concept's source and agreed the concept still says what the source says. Automation re-checking that a file still exists is recorded separately and is not confirmation.

# Independent re-check

Independent re-check: 0

Set above zero and every ktl-curator report lists that many concepts confirmed by a person, picked by a rule the curator cannot steer, with their sources, for someone other than the person who confirmed them. Their verdict is recorded as a separate `verified` event. How often that second person acts on the list is for the team to set here in words.

# How the docent answers

Evidence first: no

Set to yes and ktl-docent quotes the source before any answer that rests on a concept not yet confirmed by a person. Slower to read, harder to over-trust.
```

Step 1's report reads the `Independent re-check:` line, and ktl-docent reads `Evidence first:`. Both are optional, and absent means off.

Derive `stale_after` as *confirmation date + the row's interval*, and always show the date before writing it. Read the table tolerantly. A row names its classes in prose, so match ignoring spaces and plural form: "Glossary terms" is `GlossaryTerm`, "attested computations" is `AttestedComputation`, "Policies" is `Policy`, "people" is `Person`. A row naming a class you do not know binds nothing. A host that extends the vocabulary with a domain schema may set an interval for its own classes the same way.

## Recording something missing

When the person reports that the bundle lacks something ("there's no concept for the billing worker"), write a placeholder for the librarian: type, title, and one open question only. Never fill in facts you do not have:

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

Do not add a bullet to the nearest `index.md`. That file is the librarian's, and it will add the bullet when it fills the placeholder. Log the intake as part of the session's `**Curation**` line ("recorded 1 gap").

## Handing off

**Git-tracked `.lokf/`.** Open a pull request scoped to `.lokf/`, titled "Curation: <date>". Its body holds the health line before and after, the verbs taken, and the `just lokf-validate` output (or "validation skipped - no `uv`"). The `knowledge-registrar.yaml` gate, if scaffolded, runs on it, including its `provenance` job, which re-checks every `human:` event the pull request adds. Each named person must have approved the pull request or, when the pull request is their own, have signed its commits, since GitHub will not let authors approve themselves. Tell the person plainly that the pull request needs their approval or signature before the confirmations they just gave will pass. If they are the repository's only maintainer, tell them that GitHub will not let them approve their own pull request, so signing their commits is the path (ktl-sidecar's `references/gate.md` has the three-line setup). That is the gate working, not a snag in it. It is what makes their confirmation something a later reader can check rather than take on faith.

**Gitignored `.lokf/`.** There is no diff to show; hand the person the list of changed files and the health line instead.
