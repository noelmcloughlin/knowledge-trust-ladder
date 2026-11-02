# Reader feedback for the librarian

Written by ktl-docent; consumed and cleared by ktl-librarian on its next run. Newest first. One line per entry.

## 2026-11-02

- **Miss** - Does a released domain schema's `version` identify the release? Not in the bundle: `version` can name the upstream edition, so it stays the same across releases with different content (lmodel/github-actions v0.3.0, v0.4.0 and v0.5.0 all say 2026-10-28); only the asset name and its .sha256 carry the release. Answer found in host READMEs ("Release tags number the schema's versions", github-actions/README.md) and by comparing the released assets. playbooks/releasing.md and policies/versioning.md looked relevant from index.md but did not answer. - docent, for human:noelmcloughlin
