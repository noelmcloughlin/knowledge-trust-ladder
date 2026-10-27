# The docent holdout as an eval suite

This directory is what `claude plugin eval` runs: one case per question in [`tests/docent-holdout.yaml`](../tests/docent-holdout.yaml), the eight questions [`docs/examples/docent.md`](../docs/examples/docent.md) captured against this repository's own bundle, each with the concept its answer should rest on. [`tests/test_docent_holdout.py`](../tests/test_docent_holdout.py) keeps the two equal: a question or a concept changed in one place fails that test until the other follows, and so does an expected concept that leaves the bundle.

Each case directory holds:

- `prompt.md`, whose body asks ktl-docent to answer the question from the `.lokf/knowledge` bundle in the current directory;
- `case.yaml`, naming `scaffold.sh`, a one-line script that runs [`scaffold-bundle.sh`](scaffold-bundle.sh);
- `graders/`, with one `regex` grader per expected concept, whose pattern is the concept's path with `.md` optional, and one `tool_used` grader that requires the ktl-docent skill to have answered.

A question where either of two concepts suffices has one regex grader holding both. No grader asks a judge model, so a run costs the eight agent runs alone, and a pass means the docent named the expected concept, not that its answer was right.

A run starts in an empty directory with only this plugin loaded, and cannot see the repository: the scaffold copies `.lokf/knowledge/` and the `knowledge_bundle` link into it, and nothing else. The agent may read, search and invoke the skill, but not run a shell, so the docent works each trust label out from its table rather than its script. The graders never read the label.

## Running it

From the repository root, with Claude Code 2.1.269 or later installed and signed in:

```sh
just docent-eval          # the cost ceiling is 5 US dollars
just docent-eval cost=2   # a lower ceiling
```

The recipe runs `claude plugin eval . --trust-plugin --scaffold --ablation none --threshold 1` with that ceiling, writes `results/docent-eval.json` (the whole `results/` directory is gitignored), prints how many cases named their concept and which did not, and fails when more than one did not. Each case is a model call billed to your account. The ceiling is a list-price estimate that `claude plugin eval` checks before each case starts: once it is spent, no further case starts, and the recipe reports the run as partial. `just docent-holdout` runs the test alone, which costs nothing.

[`docent-eval.yml`](../.github/workflows/docent-eval.yml) runs the same recipe weekly and on demand once the repository variable `KNOWLEDGE_DOCENT_EVAL_ENABLED` is `true`, with the credential from the `docent-eval` Environment, writes the count to the run's summary and uploads `results/` as an artifact. It never runs on a pull request or a push.
