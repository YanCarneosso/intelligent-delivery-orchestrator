# ADR 0005: AWS SAM as the primary IaC

## Context

The stack is predominantly Lambda and Step Functions and should deploy with one reviewable template.

## Decision

Use AWS SAM with an external ASL definition and explicit IAM roles. `make deploy` performs build and
deployment; `make destroy` removes the named development stack.

## Alternatives

CDK offers higher-level composition but generates a larger review surface and requires Node tooling.
Terraform adds state management for a single-AWS portfolio stack. Raw CloudFormation is viable but
more verbose for Lambda packaging.

## Consequences

Low conceptual overhead and native SAM validation. Contributors need SAM CLI for cloud builds; local
domain tests require only Python.

## Status

Accepted — 2026-08-14.

