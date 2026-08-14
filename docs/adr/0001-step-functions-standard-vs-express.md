# ADR 0001: Step Functions Standard versus Express

## Context

Payment and dispatch are non-idempotent business effects. The system needs durable, inspectable
history. Express is cheaper at very high volume and supports direct request-response Bedrock calls,
but uses at-least-once execution and has a five-minute maximum.

## Decision

Use a Standard Workflow. Keep explicit adapter idempotency even with Standard's exactly-once workflow
semantics because configured retries and provider uncertainty still exist.

## Alternatives

Synchronous Express was rejected for the main workflow; asynchronous Express or a Standard parent
with Express child can be revisited for high-volume, fully idempotent cognitive preprocessing.

## Consequences

Better audit history and failure redrive; higher transition cost and no synchronous
`StartSyncExecution`. The `<800 ms` goal remains unproven.

## Status

Accepted — 2026-08-14.

