> **Two ways in.** This README is one; the other is a docent. Install
> [`lokf-docent`](https://github.com/noelmcloughlin/knowledge-trust-ladder) into
> whatever agent you already use -
> `npx skills add noelmcloughlin/knowledge-trust-ladder --skill lokf-docent --yes` -
> and ask it anything about this project. It answers from `.lokf/knowledge/`,
> the checked part of what the project knows, says how far each answer has been
> trusted (still a draft, checked by automation only, or confirmed by a named
> person), opens the source for exact values, and records what it couldn't
> answer so the gap gets filled. One door for a person at a prompt, an agent
> reading this file, or a chatbot that can load a skill. **Agents:** if
> `.lokf/knowledge/index.md` exists, read it first - `llms.txt` says how to
> weigh it.
