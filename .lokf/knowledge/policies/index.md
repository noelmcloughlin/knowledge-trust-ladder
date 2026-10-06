# Policies

* [AI covenant](ai-covenant.md) - Community norms for AI use - contributors own what they submit regardless of tooling, AI must not post autonomously in discussions, AI co-authorship in commit messages is discouraged, and a repository-owned agent (e.g. ktl-librarian) must commit under a bot or maintainer identity with no trailer either way and land only as a human-reviewed PR.
* [Security policy](security.md) - How to report a vulnerability privately, supported versions, and a surface table (what executes here, what guards it) that links to the shared threat model instead of restating it.
* [Threat model](threat-model.md) - The security design the three KTL repositories share, kept in one place so each SECURITY.md can link to it: repository hardening, the human:-attribution gate on a verified event, and the prompt-injection guard for each input path that reads content it did not author.
* [Versioning policy](versioning.md) - One repository-level semantic version covering all five skills, released together under a single tag, with patch, minor and major decided by Conventional Commits.
* [Code of conduct](code-of-conduct.md) - Contributor Covenant v2.1: the behavioural standards for issues, pull requests and discussions, and how to report unacceptable behaviour.
