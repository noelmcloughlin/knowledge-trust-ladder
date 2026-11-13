# What KTL is for

This page is for anyone deciding whether Knowledge Trust Ladder (KTL) fits a use they have in mind.

KTL keeps what is known about a repository as a catalogue of claims. Each claim names the source it came from, and carries a label that says how far it has been checked: by nobody, by automation, or by a named person. KTL keeps knowledge about systems. It does not scan, enforce or run them.

## What it does in every use

- **It derives claims and names their sources.** The librarian writes one concept per subject, with the file or page behind it.
- **It checks what a program can check.** The registrar validates every record, finds each quoted passage in its file, and ties each confirmation to the person who gave it.
- **It records a person's verdict.** The curator confirms, corrects, sends back or retires a concept, and sets the day to look again.
- **It notices when a source moves.** The librarian's next run starts from the concepts whose sources changed.

[The architecture](architecture.md) says how the roles fit together.

## Uses it was built for

| Use | What carries it |
| --- | --- |
| **Answers about a repository that say how far each was checked**, for a newcomer, a reviewer, or anyone who asks who owns a thing or what depends on it | The [docent](cast/docent.md) in any agent, and in [Microsoft 365 Copilot](m365.md) from a snapshot |
| **Context for a coding agent that outlasts one session.** The agent reads the bundle's index before it explores the repository again | `.lokf/knowledge/index.md`, which the host's `llms.txt` tells an agent how to weigh |
| **Documentation that knows when it went stale.** Each concept names its sources, and a review date says when a person must look again | The [librarian](cast/librarian.md)'s work list, and the curation policy |
| **A record of who vouched for what**, for a team that must show which claims a named person confirmed, when, and against which state of the source | The [curator](cast/curator.md), the evidence table attached to each release, and [three lines of defence](three-lines.md) |
| **A typed catalogue of a domain**: services, datasets, metrics, policies, playbooks and terms, joined by typed relations and queried as a graph | LOKF's classes, and a [domain vocabulary](how-it-works.md#when-the-vocabulary-stops-fitting) where they stop fitting |
| **Knowledge kept outside the repository**: a wiki page, a shared document, a file in another repository | [The ingest](ingest.md), which copies each one in with its origin |
| **One layer of context over many repositories.** Each repository keeps its own bundle, and one accountable owner joins them into a domain | [Federation](federation.md) |
| **A site and a release that anyone can read**: a page for each concept with its label, and a zip with a checksum and a signed provenance | The [website](cast/website.md) skill and the release workflow |
| **The same knowledge retold for a younger reader** | [Young readers](young-readers.md) |

## Where it runs today

The bundles that the README lists as exhibitions come from three kinds of repository:

- **A repository of Agent Skills**: this one. [Skills repositories](skills-repositories.md) says what KTL adds there, and what it leaves to an evaluation.
- **An application**: the two Obsidian plugins, and AI-LinkMO, a reference implementation of AI governance.
- **A domain of bundles**: KTL Federation, which joins the others into one workspace.

## Two uses readers ask about

### DevSecOps

KTL fits as the knowledge side of it. A bundle can hold what a team's pipelines are, which checks a branch requires, which policy asks for them, and who confirmed each of those claims and when. This repository's own bundle holds its security policy, its threat model, its release procedure and its repository checks as concepts, each with its sources and its label. A domain vocabulary adds the types that a security standard defines, such as those of SLSA or CWE, beside LOKF's own.

KTL is not the tooling side. It runs no scanner, stores no secret, writes no bill of materials and decides no deployment. Its gate checks the bundle and never the code: a red check means a record is malformed or a confirmation has nobody behind it, and says nothing about a vulnerability.

### Technology governance

KTL fits where governance needs to know who is accountable for a statement. Every confirmation names one person, the gate ties it to that person's signature or approval, and a policy is a concept that a person reviews on a date like any other. [Three lines of defence](three-lines.md) places each role in that model and lists what an auditor can check. Across repositories, a [domain](federation.md) is a set of bundles with one accountable owner.

KTL is not a governance, risk and compliance system. It keeps no risk register, tests no control and tracks no exception. It records that a named person agreed a concept says what its source says. Whether the source is right, and whether that person was the right one to ask, stay with the organisation.

## What it is not

- **Not the source of truth.** The source is. A concept is a claim about a source, and the label says how far to trust the claim.
- **Not a judge of truth.** No program in KTL decides that a claim is correct. A person does, by name.
- **Not a vector store.** Nothing is embedded. A reader, person or agent, starts from `index.md` and follows typed relations.
- **Not live.** A bundle is as fresh as its last refresh. Who is on call today, or what is deployed this minute, belongs in the system that knows it.
- **Not a place for secrets or personal data.** A bundle may be published.
- **Not a test of whether something works.** KTL checks the form and the provenance of what a bundle says. Whether a skill, a pipeline or a control works takes an evaluation of that thing.

## Judging a use that is not on this page

Good tools find uses their makers did not list. Three questions settle most of them:

1. **Is there a source to point at?** A claim with no file or page behind it cannot be checked again.
2. **Does it matter who vouched for it?** Where nobody asks how far to trust a statement, a README does the job.
3. **Does it change slowly enough for a person to confirm?** A fact that holds for weeks fits. One that changes by the minute does not.

A use that passes all three still has one cost: someone plays the curator, a little and regularly.
