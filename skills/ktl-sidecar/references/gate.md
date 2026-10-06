# The gate: what `knowledge-registrar.yaml` checks, and how a confirmation passes it

`knowledge-registrar.yaml` is the registrar. It keeps the bundle's records well-formed and provenanced, and never judges whether their content is true; that is the curator's job. It runs no agent code, and none of its jobs can write to the repository. Step 5 lays it down together with the two scripts it runs, `knowledge-conventions.sh` (with its Python half) and `knowledge-provenance.sh`. [automation.md](automation.md) covers the other Step 5 files. Everything here applies only to a **git-tracked** `.lokf/` on **GitHub**, except the forge-free gate at the end.

Its three jobs, in the order a pull request meets them:

| Job | Runs when | Checks |
| --- | --- | --- |
| `validate` | every pull request touching `.lokf/**`, weekly, on demand | the schema, every relation target, and the fourteen conventions below |
| `provenance` | pull requests only | that each `human:` confirmation added, changed or removed is backed by that person's approval or signature |
| `attestation` | only when `provenance` finds an unbacked confirmation, and only once enabled | that a listed reviewer clicked Approve |

## The `validate` job

It runs on every pull request touching `.lokf/**` (or the workflow itself), weekly on Mondays at 06:00 UTC, and on demand. It holds `contents: read` only, and a newer run on the same ref cancels the older one. Keep it green: the bar is that the projected graph describes the repository as it is today.

It runs two checks:

1. `uv run lokf validate --check-refs knowledge`: the schema check, and every typed relation must point at a concept in the bundle.
2. `bash scripts/knowledge-conventions.sh knowledge`: the fourteen conventions below, which the toolkit cannot see. On a pull request it adds `--since` and the pull request's base, which convention 14 reads.

It checks out the full history, because conventions 6, 11, 13 and 14 read each concept's commits. It installs the toolkit with `uv sync --locked`: what `.lokf/uv.lock` names, each file checked against its recorded hash. A lock that is missing or behind `.lokf/pyproject.toml` fails the job, so the gate never runs a toolkit nobody reviewed.

### The fourteen conventions

`lokf validate` reads a concept body as an opaque string and never opens `log.md`. `knowledge-conventions.sh` checks the bundle against fourteen conventions the toolkit never sees. ktl-librarian's audit runs the same script before handing off.

1. `log.md` has one bare `## YYYY-MM-DD` heading per day, newest first (OKF §9, and how the KTL Curator plugin finds today).
2. Every `at:` is quoted.
3. `verified` is a list, carrying at most one `process:ktl-librarian` event.
4. Each `## Open questions` bullet has the `- YYYY-MM-DD, <actor>: ...` shape the curator quotes.
5. Every `resource:` that is not a URL names a file or directory that still exists relative to the repository root, so a vanished source fails the gate rather than waiting for the librarian's next refresh. URLs are never fetched.
6. Every commit-shaped `revision` on an event (lokf 0.9.0+) names a commit that holds the concept's local `resource`. A shallow clone is reported, not passed.
7. One file per `id`. A sync client's conflict copy carries its original's `id`, validates, and silently merges into it in the graph.
8. Every path is lowercase. Two paths differing only by case collide on Windows, macOS and SharePoint, and a space, a parenthesis or an upper-case host name is how sync clients name a conflict copy.
9. Every concept has a closed frontmatter block, with no byte order mark in front of it.
10. The fields the provenance gates read line by line (`id`, and `by`, `at` and `revision` on an event) are spelt with no tag, anchor, alias, quoted key, block scalar or value spanning lines, and with no comment beside them. Each of those is valid YAML that `lokf validate` accepts and neither gate can see. A line reader takes a comment for part of the value, so the report script cannot read that time and the concept never reads as edited since.
11. No `at:` is later than the commit that first recorded it, or, before it is committed, than now. A time written ahead of the clock, such as local time labelled `Z` or a round placeholder, sorts after the edits and confirmations that really followed it. So a concept reads as edited since it was confirmed when it was not. A rename or a shallow clone can only make that commit look later, so the rule can miss a bad time but never flags a good one. Outside git it is skipped.
12. An index bullet that names a concept carries that concept's title and description. That holds in the folder's `index.md` and in the root's. ktl-docent chooses what to open from the bullets alone, so one left behind by an edit hides the concept it names. `knowledge-apply.sh` keeps the three equal for every concept it writes, and its `reindex` operation repairs one any other hand left behind. A concept no index lists is not a finding.
13. A concept labelled confirmed by a person still says what that person confirmed. The label holds while `generated.at` is no later than the confirmation, so an edit that leaves `generated` alone would keep it. After the commit that recorded the latest confirmation, a change to the body or to a frontmatter field must move `generated.at` past that confirmation, and the label then reads *edited since*.

    The open questions, KTL Registrar's `lokf:related` block, and the fields that record who checked what and when (`generated`, `verified`, `status`, `stale_after`, `timestamp` and `usage_window`) are not part of what a person confirms. `knowledge-apply.sh` restamps every change it writes. A change by any other hand moves `generated.at` itself, or the person confirms the concept again. Parsed values are compared, so a value written back with other quotes is no change. The newest commit that recorded the confirmation's time is the one compared with, so the rule can miss an edit but never flags a concept the person saw. Outside git it is skipped.
14. A commit that records a person's confirmation changes the verdict, not what the concept says. Rule 13 compares with the commit that recorded the confirmation, so an edit made in that same commit would read as confirmed. With `--since`, each commit after the base is read against every parent, as the `provenance` job reads one. A commit that adds a `human:` event no parent holds may change the concept's claims only when `generated.by` names the same person. That is how *Correct now* records an edit the person made. A merge that brings in a confirmation made elsewhere adds nothing new. The `validate` job passes the pull request's base. Without `--since` the rule is skipped, because a squash merge on the default branch folds an edit and a later confirmation into one commit.

Each of the first five, and the eleventh, has been broken by an agent that had it in prose, which is why it is a script. The twelfth was three copies kept equal by attention alone. The thirteenth relied on the pen alone to restamp, so an edit by any other hand left the trust label behind. The fourteenth holds the curator's hand to the verdict, which only prose held before. The rest are there so that a pin, a duplicate, a file the script could not read or an event the gate could not fails loudly instead of passing unread.

Rules 2, 3, 8 and 10 are house rules, stricter than OKF, which permits an unquoted datetime, a bare `verified` mapping, any file name and any YAML. The gate asks more so that a datetime reaches every consumer as one string, and an event is always appended to a list. It also asks that a name never collides on a case-insensitive host, and that an event reads the same to a line reader as to a parser. Every reader here still accepts a bare mapping, as OKF requires, so that half of rule 3 is style, not safety.

The script is two files. Rules 2, 3, 4, 7, 9, 10, 12 and 13 are questions about a document's YAML, which a real parser answers outright where grep and awk only approximate. `knowledge-conventions.sh` hands those to `knowledge-conventions.py` beside it, through `uv run`, which reads the script's own dependency header and needs nothing preinstalled. That header names one PyYAML release and takes no file uploaded after a set date. Rule 13 reads git too, from the Python half. Rules 1, 5, 6, 8 and 11 are git and filesystem facts and stay in the shell script, which runs with bash, grep and awk alone; without `uv` it still runs and says which rules it skipped. Both read every file with carriage returns and a leading byte order mark stripped, so a Windows checkout gives the verdict CI gives.

## The `provenance` job

It runs on pull requests only, and enforces the other half of the registrar's remit: that the paperwork is *provenanced*, not merely well-formed.

A `human:<id>` verification claims that a named person checked a concept against its source. Nothing in the format proves one. Any writer that can edit the file can type the string, and `lokf validate` sees a perfectly valid event.

So the job collects the actor of every `human:` event the pull request adds, changes or removes under `.lokf/knowledge/`. An event is a `verified` entry, or the `generated` record the curator's Correct writes. The job reads each one whole from the frontmatter and keys it by the concept's `id`, so:

- a re-dated event counts;
- a renamed concept does not;
- an id quoted in an `## Open questions` note or a body code fence is not an event at all.

A removal is a claim too, because a person's record is never removed without that person. A `verified` event that the base holds and the head does not needs its actor's backing, whether the event was struck out or its concept deleted. A person's `generated` record may give way to another person's, which is what the curator's Correct writes and which the second person backs as an addition. It may give way to nothing else without the first person.

For each actor it then requires evidence from the forge, one of:

- an **APPROVED** review from that account; or
- a signature of *theirs* on each commit that introduced or removed the event, when that person opened the pull request. GitHub will not let authors approve their own pull request, so the signature is the route for them.

Signature status comes from GitHub's API rather than `git log %G?`. A runner has neither a GPG keyring nor an allowed-signers file, so locally every signature reads as unverifiable however good it is. The API also names the account each commit is attributed to, which is what ties a signature to a person rather than merely proving one exists.

The job needs `pull-requests: read` and `contents: read`, and `fetch-depth: 0` because it diffs against the merge base. Where the repository carries curator keys under `.lokf/curators/`, it also runs the forge-free gate below as a second opinion.

This is what makes ktl-curator's confirmations mean anything to a later reader. Without it, "confirmed by a person" is only as good as whatever wrote the file. The cost is intended: a curation pull request now needs its curator's approval or signature before it can merge.

### When the confirming person opens the pull request: sign the commits

Set up signing once, reusing the SSH key you already push with:

```sh
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
```

Then add that same key again at `github.com/settings/keys`, this time as a **signing** key. GitHub keeps authentication and signing keys in separate lists, and the gate reads GitHub's verdict, so a key registered only for auth leaves every commit Unverified however correct the local setup is. Skipping this step is the usual reason the gate still fails after someone has started signing. The commit's email must also be a verified email on that account. Commits made through GitHub's web editor are signed by GitHub automatically. The skills' home repository covers GPG as the alternative, key renewal and what to do when signing fails: [signing your commits](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/docs/signing-commits.md).

A signature is the better route anyway. It is cryptographic and still checkable years later, where a review approval is a mutable record that a force-push can dismiss.

**The skills show these lines and never run them.** `--global` changes how you commit in every unrelated repository, and a wrong `user.signingkey` makes `git commit` fail everywhere until you find it. The half a skill could do is also the half that does not help: the step the gate reads is the key registered with GitHub. **A committed `.gitconfig` cannot do it either.** Git reads `/etc/gitconfig`, `~/.gitconfig` and `.git/config`, never a file in the working tree, since a config file arriving with a clone could otherwise run commands on checkout. A tracked `.gitconfig` is inert.

### If you cannot sign: the `attestation` job

The third job is an opt-in escape hatch for a repository that cannot sign and has nobody else to approve. Enabling it takes two steps, and the first is the one that does the work:

1. **Settings -> Environments -> New environment.** Name it (`knowledge-curation`, say; this is a GitHub setting, not a file, and unrelated to the curation policy concept of the same name), tick **Required reviewers**, add the people allowed to attest, and save.
2. **Settings -> Secrets and variables -> Actions -> Variables**: set `KNOWLEDGE_CURATION_ENVIRONMENT` to that environment's name.

Do not do the second without the first. An environment with no required reviewers approves itself the instant it is reached, so setting the variable while skipping the reviewers silently disables the gate. With the variable unset (the default), the `attestation` job never runs and `provenance` simply fails on an unbacked confirmation.

It is **not** a setting that turns the check off, and that shape is deliberate. A permanent "provenance: off" switch gets set for one urgent afternoon and never reset, and from then on the bundle asserts confirmations nothing supports while the health line still promises otherwise. Instead the job asks for a fresh human action on each pull request that needs one: the run pauses, GitHub emails the environment's reviewers, and a person clicks Approve in a browser. An environment reviewer **may** be the person who opened the pull request, since environments carry no self-approval ban; that is what makes it usable for a solo maintainer. Each click is recorded in the deployment log, so it stays auditable.

Say plainly to whoever clicks what the attestation means. It records that a person with repository access vouched for the confirmation out of band. It is not evidence that anyone opened the concept's source. That is why signing is the recommended path and this is the fallback.

### Marking the required checks

Mark `validate` and `provenance` as required in branch protection, and `attestation` too if you enable it. When a confirmation is backed, `attestation` is skipped rather than run. If your branch protection treats a skipped required check as blocking, that errs toward a stuck pull request rather than a silent bypass: annoying, but the safe direction.

Add one line to the repository's pull request template for whoever approves a curation pull request: *I opened the sources named by every confirmation I am approving.* An approval then records a task done, not only a click. The gate can prove who approved, never what they read.

One wrinkle follows. The librarian's own pull request never fires this workflow, because GitHub starts no `pull_request` workflow for a pull request opened with the default `GITHUB_TOKEN`. Its `publish` job runs its own checks before opening it, the unattended form of the forge-free gate below among them, so nothing unsafe merges. But a required `validate` or `provenance` sits at "Expected" until a human closes and reopens the pull request or pushes an empty commit. ktl-librarian's [scheduled-task.md](../../ktl-librarian/references/scheduled-task.md) has the detail.

## The forge-free gate: `knowledge-provenance.sh`

The `provenance` job needs GitHub. Where it cannot run (another forge, or none), and as a second opinion where it does, `knowledge-provenance.sh` does the signature half of its work with plain git, and gpg or ssh-keygen, on any CI or by hand. Step 5 lays it down at `.lokf/scripts/knowledge-provenance.sh`.

- **Who may confirm.** The repository carries one public key per curator id under `.lokf/curators/`: `<id>.asc` for GPG (`gpg --armor --export <key>`, subkeys included) or `<id>.pub` for SSH (the `ssh-keygen` public key file, one key per line). That directory is the machine-readable list of who may confirm: a key not there is not a curator, whatever the forge says. The id is the forge login the curator skill records, so the two gates name the same person.
- **What is checked.** For every commit in a range that adds, changes or removes a `human:<id>` event under the bundle (a `verified` entry or the `generated` record), the script verifies the commit's signature against that id's key. A removal is read as the GitHub job reads it: a `verified` event every parent held, or a person's `generated` record that no other person's replaces. Events are read whole from the frontmatter, against every parent of the commit, and keyed by the concept's `id`, exactly as the GitHub job reads them. So a re-dated `at`, a moved `revision` or a flow-style event counts, while a renamed concept, a merge that brings in another curator's confirmation, and an example in a body code fence do not.

  A GPG signature is checked with `git verify-commit` in a throwaway keyring, matched against every fingerprint the key file carries, since most keys sign with a subkey. An SSH signature is checked with `ssh-keygen -Y verify` (OpenSSH 8.2+) over the commit's own payload, with the id as the principal.
- **What fails.** An unsigned commit. One signed by another key, by an expired or revoked key, or by a key of the other kind. An id with no key on file. And a range that adds, alters or removes an id's own key file and records a confirmation *by that id* together. So nobody registers a key and vouches with it in one step; a key is added in its own reviewed change first. Another curator's key added beside a confirmation is fine. One finding per problem, and exit 1.
- **What it proves** is what the GitHub job's signature route proves: that the holder of that key made that commit. Not that anyone read the source, and it says so.

**The unattended form.** `knowledge-provenance.sh --unattended` needs no key and no forge. It compares the working tree with `HEAD` and reports every way a change nobody stands behind touches a person's record. That is a `human:` event added, changed or removed in any YAML layout, a person's note under `## Open questions` added or removed, and text a person wrote changed. `knowledge-apply.sh` refuses each of those before it writes. This is the same refusal, checked on the result, and the librarian workflow runs it twice: in the wrapper, and again in the `publish` job, on a checkout the agent never shared.

With no `.lokf/curators/` the signed form says so and passes: a host that has not opted in loses nothing. The GitHub job runs it as an extra step when a key file exists. On another forge or a plain CI, run it with the pull or merge request's `<base> <head>`. The preflight's `curators` line says how many keys are on file and whether the current machine's signing key is among them. So a curator learns before a session, not at the gate, that theirs is missing. The request to send is in [prerequisites.md](prerequisites.md). [Signing your commits](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/docs/signing-commits.md) says how to export a key for the directory.
