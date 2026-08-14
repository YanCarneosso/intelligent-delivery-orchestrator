# Architecture

## System boundary

An authenticated upstream producer starts a Standard Workflow with an order matching
`schemas/order.schema.json`. Ingress authentication, a real payment acquirer, courier network, and
message delivery provider are outside this reference stack. The three effect adapters are explicit
non-side-effecting seams, not simulated production integrations.

## Runtime flow

1. `ValidateOrder` calls a Lambda that applies JSON Schema before any model cost, adds a correlation
   ID when absent, detects food-risk vocabulary, and creates a PII-minimized Nova request.
2. `ClaimIdempotencyKey` performs a conditional DynamoDB `PutItem`. A duplicate stops before model
   invocation or side effects.
3. `InvokeNovaLite` directly calls the Step Functions optimized Bedrock integration with bounded
   transient retries and a 20-second task timeout.
4. `ValidateModelOutput` parses bare JSON, enforces the closed cognitive schema, unions restrictions,
   and prevents the model from clearing deterministic allergy evidence.
5. A `Choice` attaches the auditable kitchen safety policy. Payment remains deterministic.
6. Dispatch and notification execute in parallel. Dispatch failure is critical; notification failure
   becomes a visible degraded result after bounded retries.
7. DynamoDB records the terminal status. CloudWatch receives Step Functions native metrics and
   PII-safe Embedded Metric Format logs from the Lambdas.

## Trust boundaries

| Boundary | Untrusted input | Enforcement |
|---|---|---|
| Caller → workflow | Order JSON | Closed input schema, length/type/enum limits |
| Notes → Bedrock | Natural language and prompt injection | Data delimiters, system prompt, deterministic detector |
| Bedrock → business logic | Arbitrary model text | Bare-JSON parse, closed output schema, safety merge |
| Workflow → effects | Approved deterministic state | Choice states, idempotency claim, scoped adapters |
| Workload → AWS | API permissions | Separate Lambda and Step Functions IAM roles |

## Resilience policy

| Failure | Classification | Behavior |
|---|---|---|
| Invalid order/payment enum | Caller/permanent | Reject before DynamoDB and Bedrock; no retry |
| Duplicate key | Replay/permanent | Conditional write fails; no side effect |
| Bedrock throttling/unavailable/model-not-ready | Dependency/transient | 3 attempts, exponential backoff |
| Bedrock timeout | Dependency | Catch, persist `FAILED / MODEL`, stop |
| Invalid model JSON/schema | Model/permanent | No model retry, persist `FAILED / MODEL` |
| Lambda service/SDK error | Infrastructure/transient | 2–3 bounded attempts |
| Payment rejection/failure | Business/critical | Persist `REJECTED / PAYMENT`, stop |
| Dispatch failure | Business/critical | Fail parallel state; persist `FAILED / FULFILLMENT` |
| Notification failure | Business/noncritical | Finish fulfillment with degraded notification result |
| DynamoDB failure | Infrastructure/critical | Stop; operator investigates execution history |

Retries add Step Functions transitions and can repeat an adapter call. A production provider adapter
must pass `idempotency_key` through to the provider; DynamoDB protects the workflow boundary but does
not replace provider-side idempotency.

## Data and observability

Step Functions logs only `ERROR` events with `IncludeExecutionData: false`. Application logs contain
order/correlation identifiers and outcome counters, not notes or address. The dashboard covers
workflow success/failure/time, Bedrock calls, allergy-risk orders, and high-priority orders. Retry and
state failure diagnosis uses execution history and Step Functions service-integration metrics; for a
complete business ledger, export terminal records to an analytics store in a future iteration.

## Performance

`<800 ms` remains a target, not a result. Direct Bedrock integration removes one proxy hop, but Nova
inference, Lambda cold starts, and Standard Workflow transition latency can exceed it. Use
`scripts/integration_test.py` plus CloudWatch `ExecutionTime` for deployed measurements. The local
benchmark measures only Python control logic and is deliberately labeled as such.

## Sources validated on 2026-08-14

- [Step Functions optimized Bedrock integration](https://docs.aws.amazon.com/step-functions/latest/dg/connect-bedrock.html)
- [Standard versus Express Workflows](https://docs.aws.amazon.com/step-functions/latest/dg/choosing-workflow-type.html)
- [Nova Lite model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-lite.html)
- [Nova Invoke API](https://docs.aws.amazon.com/nova/latest/userguide/using-invoke-api.html)
- [Step Functions CloudWatch metrics](https://docs.aws.amazon.com/step-functions/latest/dg/procedure-cw-metrics.html)

