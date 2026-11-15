# Operator runbook

1. Run `make verify` and `make demo` from the repository root.
2. Start local Ollama and run `make live MODEL=qwen2.5:0.5b`.
3. Read `decision`, `reason`, `stop`, and `missing`. Match `citations` to the corresponding evidence entries.
4. Compare any changed evidence or outcome with the [bundled report](../examples/live-report.json).

If labels are late, wait for the mature-label interval and replay. If drift and quality loss coincide, segment the example population and verify data lineage before attributing cause.

When the run returns review on a model or budget failure, inspect the last trace event and recover the missing evidence before acting.
