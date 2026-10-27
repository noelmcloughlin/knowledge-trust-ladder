# Recipes for Knowledge Trust Ladder's own checks. The sidecar's recipes are
# .lokf/justfile, which `just --justfile .lokf/justfile` runs and which this
# file leaves as it is. Run `just --list` to see these.

# List available recipes
default:
    @just --list

# Check tests/docent-holdout.yaml: each expected concept exists, and evals/ asks the same questions
docent-holdout:
    uv run --no-project --with-requirements tests/requirements.txt pytest tests/test_docent_holdout.py -q

# Run ktl-docent on the holdout through `claude plugin eval` (one run per question, no judge) under a cost ceiling in US dollars; pass when at most one case failed
docent-eval cost="5":
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p evals/results
    rm -f evals/results/docent-eval.json
    # Exit 0 is every case passed and 1 is a case below the threshold, which
    # the count below weighs; anything else stopped the run before every
    # case ran: 2 is the cost ceiling, or a credential the API refused.
    status=0
    claude plugin eval . --trust-plugin --scaffold --ablation none --threshold 1 --no-publish --max-cost-usd "{{ cost }}" --json evals/results/docent-eval.json || status=$?
    if [ "$status" -ne 0 ] && [ "$status" -ne 1 ]; then
      echo "docent-eval: claude plugin eval exited $status before every case ran" >&2
      exit "$status"
    fi
    if [ ! -s evals/results/docent-eval.json ]; then
      echo "docent-eval: claude plugin eval wrote no result (exit $status): a case failed to load, or no case was found" >&2
      exit 1
    fi
    passed="$(jq -r '.aggregates.casesPassed' evals/results/docent-eval.json)"
    total="$(jq -r '.aggregates.casesTotal' evals/results/docent-eval.json)"
    failed="$(jq -r '[.cases[] | select(.aggregates.score < 1) | .name] | join(", ")' evals/results/docent-eval.json)"
    if ! [[ "$passed" =~ ^[0-9]+$ && "$total" =~ ^[0-9]+$ ]] || [ "$total" -eq 0 ]; then
      echo "docent-eval: evals/results/docent-eval.json carries no case count" >&2
      exit 1
    fi
    echo "docent-eval: $passed of $total cases named the expected concept${failed:+ (failed: $failed)}"
    if [ "$(jq -r '.partial // false' evals/results/docent-eval.json)" = "true" ]; then
      echo "docent-eval: the run was partial ($(jq -r '.partialReason // "unknown"' evals/results/docent-eval.json)), so not every case ran" >&2
      exit 2
    fi
    # The bar is the plan's: the expected concept is named for all but one
    # question, nine of ten there and seven of eight here.
    if [ $((total - passed)) -gt 1 ]; then
      echo "docent-eval: more than one case failed" >&2
      exit 1
    fi
