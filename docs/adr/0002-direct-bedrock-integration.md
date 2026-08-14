# ADR 0002: Direct Step Functions to Bedrock integration

## Context

AWS supports the optimized `arn:aws:states:::bedrock:invokeModel` resource with a 256 KiB inline body.
A proxy Lambda would add code, permissions, latency, and another failure mode.

## Decision

Invoke Nova directly from the state machine. Use Lambdas only before the call to build a minimized
request and after it to enforce the output schema and deterministic safety policy.

## Alternatives

A boto3 Lambda proxy was rejected. S3 input/output is unnecessary because bounded text payloads are
far below 256 KiB. Converse via SDK integration was not selected because the optimized InvokeModel
integration is directly supported.

## Consequences

The ASL exposes the real service boundary and has narrower code. The workflow must understand Nova's
model-specific request/response shape; contract tests protect it.

## Status

Accepted — 2026-08-14.

