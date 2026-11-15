# Case study

## Problem

A shifted feature population alone gives weaker evidence than a shift paired with measured quality loss. Stale data and late labels require an explicit review outcome.

## Design

The local language model selects one evidence probe per turn. The loop validates the returned action, executes the corresponding read-only function and sends the resulting observation back to the model. A deterministic domain policy consumes the validated evidence to produce the decision and source IDs. Missing required evidence yields review. The JSON report includes the trace and per-probe SHA-256 digests.

## Outcome

The main fixture flags checkout_value and measured accuracy moving from 94% to 79%. The feature-shift-only case returns watch. Late labels or stale data returns review.

The captured local-model report records the selected probe order and all validated outputs. The offline evaluation checks alternate inputs and the behavior when the loop cannot collect enough evidence. [Captured report](../examples/live-report.json)
