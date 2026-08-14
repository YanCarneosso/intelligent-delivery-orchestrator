# ADR 0006: DynamoDB idempotency claim

## Context

Duplicate events can otherwise repeat Bedrock cost and external effects. Standard Workflow execution
names alone are insufficient when callers choose different names or retries cross workflow boundaries.

## Decision

Require an idempotency key and conditionally `PutItem` before Bedrock. Store identifiers, status,
execution ARN, and failure category only. Update the claim at terminal outcomes.

## Alternatives

Execution-name deduplication was too API-specific. No persistence was unsafe. Adding a full order
database would exceed the requirement.

## Consequences

DynamoDB is justified as a correctness boundary and adds small cost/operations. Failed claims remain
for operator reconciliation. Real provider adapters must also propagate the key.

## Status

Accepted — 2026-08-14.

