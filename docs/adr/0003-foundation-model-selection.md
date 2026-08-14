# ADR 0003: Foundation model selection

## Context

The workload needs low-cost multilingual text classification and JSON extraction, not deep agentic
reasoning. AWS documentation lists Nova Lite v1 as active with in-region availability in `us-east-1`.

## Decision

Default to `amazon.nova-lite-v1:0` in `us-east-1`; allowlist that exact value in SAM and IAM. Evaluate
with real labeled orders before production.

## Alternatives

Nova Micro could be cheaper for text-only input but requires comparative safety/quality evaluation.
Nova Pro is likely unnecessary cost. Cross-region inference may improve throughput but expands data
residency and IAM considerations.

## Consequences

Low estimated token cost and a 300k context window, though this project deliberately limits input and
output. A version change requires a reviewed ADR, schema/prompt tests, and deployed evaluation.

## Status

Accepted — 2026-08-14.

