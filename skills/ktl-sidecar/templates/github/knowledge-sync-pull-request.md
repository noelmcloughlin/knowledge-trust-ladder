<!-- A sidecar sync. The sync writes the lines above this template when it opens the pull request: the release, the files it changed, the pin, and how the sidecar's checks ended. Opening one by hand: .lokf/scripts/knowledge-sync.sh --pr <tag> writes them too. -->

## Reviewer checklist

- [ ] The diff touches only the sidecar's copies, the site's copies, the skills pin and `CHANGELOG.md`.
- [ ] `TRUST_LADDER_SKILLS_REF` names the release, and `TRUST_LADDER_SKILLS_SHA` the commit that tag names.
- [ ] The release notes of Knowledge Trust Ladder ask nothing of this repository that the diff leaves undone.
- [ ] `CHANGELOG.md` has the entry under `## [Unreleased]` and `### Security`, and the title carries `security(sidecar):`, so the merge releases.
