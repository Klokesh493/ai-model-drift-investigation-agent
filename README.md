# AI Model Drift Investigation Agent

Compare feature distribution drift, mature label quality, and data freshness before opening an investigation.

[Skills and verification](docs/ENGINEERING_NOTES.md)

## What I built

A shifted feature population alone gives weaker evidence than a shift paired with measured quality loss. Stale data and late labels require an explicit review outcome.

The local language model selects one evidence probe per turn. The loop validates the returned action, executes the corresponding read-only function and sends the resulting observation back to the model. A deterministic domain policy consumes the validated evidence to produce the decision and source IDs. Missing required evidence yields review. The JSON report includes the trace and per-probe SHA-256 digests.

## Architecture

```mermaid
flowchart LR
    Input["Aligned feature histograms, mature labels and freshness metadata"] --> Session["Bounded agent loop"]
    Session --> Model["Ollama model selects one probe"]
    Model --> Allow["Validate probe against remaining allowlist"]
    Allow --> Probe["Calculate smoothed PSI, compare accuracy and validate input freshness"]
    Probe --> Evidence["Hash evidence, record trace, update observations"]
    Evidence -->|More evidence needed| Session
    Evidence --> Output["Investigate drift or quality, watch, observe, or review"]
    Session -->|Budget or model failure| Review["Review with missing keys"]
```

## Run the project

Use Python 3.9+ and Make from the repository root. Replay uses explicit scripted actions. Live mode requires a local Ollama server with the named model.

```sh
make verify
make demo
```

For model-backed execution, start `ollama serve` in a separate terminal. Then run:

```sh
ollama pull qwen2.5:0.5b
make live
```

The main fixture flags checkout_value and measured accuracy moving from 94% to 79%. The feature-shift-only case returns watch. Late labels or stale data returns review.

## Verification

Local Qwen2.5 0.5B through Ollama v0.40.16 selected `population → quality → freshness` and returned `investigate_drift`. The offline suite covers 6 cases. [Captured report](examples/live-report.json)

`make verify` runs the test suite and then compares each replay case’s decision, stop reason and citations against its expected outputs. For automated execution, use the [CI template](docs/github-actions/ci.yml).

The model also ran the `late-labels` fixture and returned `review`.

To verify the decision in a local pipeline, run:

```sh
python3 agent.py run examples/main.json --replay examples/actions.json --require-decision investigate_drift
```

A mismatched decision exits 1 and keeps the JSON report on stdout. Duplicate JSON keys exit 2 for fixtures and are rejected in the local model response.

## Operating limits

Bins must be aligned upstream. PSI uses a 0.25 threshold with additive smoothing. The demonstration uses aggregate, synthetic signals and does not automatically retrain or roll back a model.

The model receives bounded summaries through a loopback API. The fixture reader caps inputs at 128 KiB. The model can select only named probes and supplies no tool arguments. Keep local fixtures within the intended data boundary.

[Architecture](docs/ARCHITECTURE.md) · [Case study](docs/CASE_STUDY.md) · [Runbook](docs/RUNBOOK.md) · [Troubleshooting](docs/TROUBLESHOOTING.md)

[Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs)
