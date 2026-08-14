# ADR 0004: Closed JSON contracts and deterministic safety precedence

## Context

Model output is probabilistic and user notes can contain prompt injection. Downstream financial and
operational code cannot consume arbitrary text.

## Decision

Use Draft 2020-12 schemas with required fields, enums, bounds, and `additionalProperties: false`.
Accept bare JSON only. Union restrictions with deterministic findings and compute allergy risk as
`model risk OR deterministic risk`; risk forces `HIGH` priority.

## Alternatives

Prompt-only enforcement and permissive JSON parsing were rejected. Bedrock structured-output/tool
features can be evaluated later but do not remove the need for downstream validation.

## Consequences

Unsafe downgrades fail closed. False positives are possible and intentional. Invalid outputs become
observable model-contract failures rather than guessed values.

## Status

Accepted — 2026-08-14.

