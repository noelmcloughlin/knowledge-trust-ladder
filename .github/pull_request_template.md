## Summary

## Which skill(s) changed?

- [ ] lokf-librarian
- [ ] lokf-sidecar
- [ ] lokf-curator
- [ ] lokf-docent
- [ ] repository packaging only (CI, docs, templates unrelated to skill content)

## Checklist

- [ ] `bash scripts/validate-repository.sh` passes locally
- [ ] `gh skill publish --dry-run` passes locally (or CI's `validate-skills` job is green)
- [ ] If a file the sibling repositories deep-link moved (check 9 lists them), their links change too, with this side landing first
- [ ] `CHANGELOG.md` has a line or two under `[Unreleased]` if this changes skill behavior
- [ ] For a curation PR (confirmations under `.lokf/knowledge/`), the approver opened the sources named by every confirmation they approve

## AI Assistance

If you used AI tools while preparing this PR, you are still the author and responsible for understanding, verifying, and defending your submission. Please engage with reviewers personally rather than through your agent during feedback and revisions. Don't dump LLM output into this PR without curation. See our [AI Covenant](https://github.com/noelmcloughlin/lokf-agent-skills/blob/main/AI_COVENANT.md) for details.
