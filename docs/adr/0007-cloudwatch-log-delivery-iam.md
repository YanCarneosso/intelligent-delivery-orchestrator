# ADR 0007: CloudWatch log-delivery IAM exception

## Context

Step Functions CloudWatch Logs delivery requires control-plane actions such as
`logs:CreateLogDelivery`, `logs:PutResourcePolicy`, and `logs:DescribeLogGroups`. AWS documents that
these actions do not support resource-level permissions in this integration.

## Decision

Isolate the required `Resource: "*"` actions in one named statement on the Step Functions role.
Every Lambda, DynamoDB, and Bedrock permission remains resource-scoped. Log execution errors without
payload data.

## Alternatives

Disabling logs removes valuable failure evidence. A fake log-group ARN restriction would deploy a
policy that cannot authorize the required control-plane calls.

## Consequences

One documented wildcard remains. Its action list cannot read log events or write arbitrary events;
AWS Organizations SCPs and permission boundaries can constrain the deployment further.

## Status

Accepted exception — 2026-08-14.

