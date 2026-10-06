---
type: Policy
id: https://knowledge-trust-ladder.example/knowledge/policies/threat-model
title: Threat model
description: "The security design the three KTL repositories share, kept in one place so each SECURITY.md can link to it: repository hardening, the human:-attribution gate on a verified event, and the prompt-injection guard for each input path that reads content it did not author."
genre: reference
resource: docs/threat-model.md
generated:
  by: process:ktl-librarian
  at: "2026-10-06T11:10:52Z"
verified:
- by: process:ktl-librarian
  at: "2026-10-06T11:10:52Z"
references:
- https://knowledge-trust-ladder.example/knowledge/policies/security
- https://knowledge-trust-ladder.example/knowledge/policies/ai-covenant
sources:
- resource: docs/threat-model.md
- resource: CHANGELOG.md
- resource: scripts/validate-repository.sh
---
# Overview

The page was added on 2026-09-14, when the design moved out of `SECURITY.md` and into it across the three KTL repositories (`knowledge-trust-ladder`, KTL Registrar, KTL Curator). Each repository's `SECURITY.md` says how to report, what that repository owns, and what it inherits from here. `scripts/validate-repository.sh` check 9 records this path among the ones a sibling depends on.

**Interactive use is advisory, not enforced.** A skill's `Scope:` line is prose, not a checked permission. An agent run interactively has whatever access its harness grants, and only the scheduled `knowledge-librarian.yaml` enforces its scope, because nothing is watching it run.

The skills ktl-curator, ktl-librarian and ktl-sidecar also run the repository's scripts from `.lokf/scripts/`, which anyone who can commit to the repository can change, so a skill runs them as the repository's code. The preflight's `copies` line cannot check them, because the preflight is one of them. Since 2026-10-05, ktl-docent runs none of them. It runs its own copies of `knowledge-report.sh` and `knowledge-feedback.sh`, which a check in `knowledge-trust-ladder` holds byte-identical to their templates, so a question runs no code the repository supplies. That holds only where the skill comes from a source the reader trusts, since a repository that holds its own copy of a skill supplies the instructions and the scripts.

**Repository hardening**:

- Actions are pinned to commit SHAs everywhere, the copied templates included. Dependabot bumps the workflow pins, and the templates are bumped by hand, since Dependabot scans only `.github/workflows/`.
- `permissions: {}` is at the top of every workflow.
- The agent step runs the reviewed, in-repo wrapper, never a repository variable's content as a command. `AGENT_CLI` chooses the agent, `KNOWLEDGE_LIBRARIAN_ENABLED` turns it on, and the workflow triggers only on `schedule` and `workflow_dispatch`.
- harden-runner runs in audit mode on any job that installs packages or runs third-party code.
- The librarian is split into an `earlier` job whose token can read pull requests and nothing else, a read-only `refresh` job and an agent-free `publish` job, so the write token and the agent never meet. The agent's one credential is the `AGENT_API_KEY` secret or, with `AGENT_USE_JOB_TOKEN`, the job's own token, holding `contents: read` and `copilot-requests: write`. It is exported into the agent's environment only, under a credential-shaped name the wrapper checks (2026-09-24).
- The release workflow is split the same way (2026-09-24). A `pack` job installs the toolkit and validates under `contents: read`. An `attach` job runs no third-party packages, holds `contents: write`, and checks each zip, the bundle's and any Copilot skill's, against the checksum `pack` made before uploading it.
- Every write to `main` waits behind the `release` Environment's required reviewers, which are configured by hand, or the Environment exists in name only. Release tooling is installed with `npm install --ignore-scripts`.
- `main` blocks deletion, force-pushes and non-linear history, and nothing more, since a stricter ruleset would also reject the release job's own commit.
- Secret scanning and push protection still hold, as GitHub settings nothing in CI can assert.
- No tracked file holds a character a reader cannot see, which `knowledge-trust-ladder`'s contract checks (2026-10-04).
- CodeQL and dependency review are skipped where there is nothing for them to scan.
- The skill a scheduled run installs is pinned to a commit: the install step installs nothing unless the release tag still names the commit it named when the pin was set.
- Every workflow that installs the lokf toolkit does so with `uv sync --locked`, so each file is checked against the hash `.lokf/uv.lock` records, and a lock that is missing or out of date fails the job.
- The Python halves of the conventions script and the pen name one PyYAML release, and take no file uploaded after a set date.
- Where there is no Python, ktl-librarian and ktl-sidecar read LOKF's schema from GitHub by commit, never by tag, so the file cannot change under them (2026-10-05). The contract in `knowledge-trust-ladder` fails a tag or a branch in that URL, and two pages that pin different commits.

**The librarian's pen (added 2026-10-03)**: the librarian writes the bundle only through `knowledge-apply.sh`. ktl-librarian describes each change as an operation in `.lokf/patch.yaml`, and the script stamps `generated`. It refuses an operation that would name a person as its actor, and refuses to rewrite text a person wrote or to delete a concept a person confirmed or left a note on. It writes nothing unless every operation passes. The pen also compares each concept it is about to write with the file it read, and refuses the patch when a person's event or note would differ, however the operations spelt it. The scheduled wrapper applies the file after the agent has finished and refuses a run that changed anything else, so the agent never writes the bundle itself. `publish` checks the patched tree for the same refusals with `knowledge-provenance.sh --unattended`. `docs/threat-model.md` lists the pen under repository hardening.

**Human attribution**: a `verified` event whose actor starts with `human:`, or a `generated` record written that way, is a claim, not a credential. It is a string in Markdown that any writer can type. `knowledge-registrar.yaml`'s `provenance` job is the authority: it requires an approving review from the named account or their verified signature on the introducing commit, evidence GitHub holds rather than evidence the bundle asserts. That job reads the events themselves: whole, from the frontmatter, against every parent of a commit, and keyed by the concept's `id`. So a re-dated event counts, while a rename, a merge and an example in a body code fence do not. Conventions rule 10 keeps those fields to spellings a line reader and a parser agree on.

ktl-curator writes `human:` only for an authenticated identity: `gh api user`, `glab api user`, or a signing key the forge lists under the stated login. Without one, it refuses the two verbs that assert a person vouched for something, while the three that assert nothing about who checked what stay available. It refuses to run a review session unattended, and its report flags an unsigned `human:` commit rather than trusting it silently.

Where GitHub is not the forge, or as a second opinion where it is, `knowledge-provenance.sh` (2026-09-17) does the signature half. It checks against public keys the repository carries under `.lokf/curators/`, one GPG or SSH key per curator id, and refuses a change that adds an id's key and that id's confirmation together. The optional `attestation` job is off unless `KNOWLEDGE_CURATION_ENVIRONMENT` names an environment, and naming one whose required reviewers are empty makes it self-approve instantly. Where `.lokf/` is gitignored, no pull request ever carries the bundle, so the CI half never runs and the curator's in-session rules are the whole of it. A host with no git at all has only its platform's version history. None of this proves anyone read the source: it raises the cost of forgery, not the truth of a confirmation.

**Prompt-injection guards**, one per input path:

- ktl-librarian resolves a `.lokf/feedback.md` entry only from the source it names, never from the entry's own wording, and ktl-curator only counts the waiting entries, with `grep -c`.
- ktl-curator quotes a fetched source to a person rather than acting on it.
- ktl-docent treats fetched or repository content as text to quote, never instructions, and is read-only on the bundle besides. Since 2026-09-23 it adds a feedback entry through `knowledge-feedback.sh`, its own copy since 2026-10-05, rather than by opening `feedback.md`, so the librarian is the only skill that reads what a reader wrote. Its one write path asks once per session first.
- ktl-prose never opens `.lokf/feedback.md`, and rewords only in a live session, on a request addressed to it. Its check script refuses a rewording that touches a concept a person wrote or confirmed, or a byte of frontmatter, or that adds a character no reader sees.
- The registrar's `provenance` job, which reads pull-request metadata, runs no agent. Event fields enter through `env:`, API reads are narrowed to logins, SHAs and a verification flag, and the `human:<id>` is held to a login's characters. The token is read-only, and a path git still has to quote is refused (2026-09-19).
- The librarian's `earlier` job, which lists the pull requests the workflow opened, runs no agent either and reads no title, body or comment. It counts a pull request only when its branch is `knowledge-librarian/...` in this repository, and matches each value it takes against a pattern. Only the hashes of the feedback entries those pull requests handled leave the job, since the entries are readers' words.

If a guard fails, the only unattended write path is `knowledge-librarian.yaml`'s `publish` job. It re-derives the touched paths from the patch's own `git apply --numstat`, on a clean checkout the agent never shared. It confines them to `.lokf/knowledge`, `knowledge_bundle`, `.lokf/feedback.md` and `.lokf/questions.md`, the only pathspecs the patch is built from. It refuses a patch that touches a person's record: an event added, changed or removed in any YAML layout, a person's note added or removed, or text a person wrote changed. Inside `refresh`, the wrapper snapshots `.git/config` and `.git/hooks` before the agent call and restores them from an `EXIT` trap. It keeps its own checks in a `main()` called last, so neither a failed agent nor a cancelled job leaves a poisoned config behind.

**A person's record is never removed without that person.** `docs/threat-model.md` has the `provenance` job collect the actor of every `human:` event a pull request adds, changes or removes. A `verified` event struck out, or gone with its concept, needs the same approval or signature as one that is added, and a person's `generated` record may give way only to another person's.

**The ledger of readers' questions.** A handled feedback entry leaves `feedback.md` for `.lokf/questions.md`, which the pen writes and only programs read. The librarian keeps a reader's words out of `log.md`, out of every concept and out of its hand-off, since the curator opens the first two and a person reads the third. `knowledge-report.sh` builds from the ledger the one prompt of the retrieval test, which an agent answers from an empty directory and whose reply is read for concept paths only.

**The librarian's hand-off (2026-10-04).** The patch file may carry up to ten lines for the person reviewing the pull request, in the agent's own words. It is the one free text that passes from the job that ran the agent to the pull request. The pen holds each line to printable text with no backtick and writes none of it to the bundle. Once the agent returns, the wrapper removes whatever is at the paths the workflow reads, so a file or a link the agent left there is gone. The retrieval test calls the agent again, with readers' words in its prompt, after the pen has written the hand-off. So the wrapper writes the pen's lines there again once that call returns. `publish` cleans the lines again and shows them in a code block, where nothing renders, and the curator never opens a pull request body.

**A confirmation covers the text the person saw (2026-10-04).** The label *confirmed by a person* holds while `generated.at` is no later than the confirmation. The pen restamps every change it writes, and conventions rule 13 fails a pull request in which any other hand changes a confirmed concept's content and leaves `generated` behind.
