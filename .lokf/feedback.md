# Reader feedback for the librarian

Written by ktl-docent; consumed and cleared by ktl-librarian on its next run. Newest first. One line per entry.

## 2026-10-23

- **Disagreement** (on `playbooks/ktl-sidecar-skill.md`) - The concept, following skills/ktl-sidecar/references/automation.md line 120, says every librarian variable goes under Repository variables because a variable set on an Environment is never seen. That holds for variables read in a job if: such as KNOWLEDGE_LIBRARIAN_ENABLED, but .github/workflows/knowledge-librarian.yaml line 306 reads AGENT_API_KEY_ENV in a step of the refresh job, which runs in the knowledge-librarian Environment, so an Environment copy would be seen there. Repository variables stay the right advice; the stated reason is too broad. - docent
- **Miss** - What command creates the subscription token the scheduled librarian's AGENT_API_KEY secret holds for Claude Code? Answered at skills/ktl-sidecar/references/automation.md lines 159-163 (claude setup-token, with AGENT_API_KEY_ENV set to CLAUDE_CODE_OAUTH_TOKEN). playbooks/ktl-sidecar-skill.md and playbooks/ktl-librarian-skill.md looked relevant from index.md and cover the secret and its Environment, but neither names the command. - docent
