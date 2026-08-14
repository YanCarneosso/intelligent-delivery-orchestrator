# Operations runbook

## Signals

- `AWS/States`: `ExecutionsStarted`, `ExecutionsSucceeded`, `ExecutionsFailed`,
  `ExecutionsTimedOut`, `ExecutionTime`, service-integration failures and retries.
- `IntelligentDeliveryOrchestrator`: `OrdersValidated`, `BedrockCalls`, `AllergyRiskOrders`,
  `HighPriorityOrders`, payment/dispatch/notification outcome counters.
- DynamoDB terminal `status` and `failure_category` provide per-idempotency-key audit state.

CloudWatch metrics are best effort and not a financial ledger. Use `Sum` for count metrics and
execution history/DynamoDB for incident investigation.

## Triage order

1. Open the `ido-<environment>` dashboard and identify failed/timed-out executions.
2. Inspect Step Functions execution history using `order_id` / `correlation_id`; execution data is
   available in history to authorized operators even though CloudWatch payload logging is disabled.
3. Classify `MODEL`, `PAYMENT`, `FULFILLMENT`, duplicate, or infrastructure failure.
4. Check Bedrock quotas and service health for throttling/unavailability.
5. Do not manually replay until the idempotency record and external provider receipt are understood.
6. For a false-negative food-risk report, stop affected fulfillment paths and treat it as a safety
   incident, not a routine model-quality defect.

## Redrive and replay

Standard Workflow redrive preserves execution history, but the DynamoDB claim remains. The reference
design intentionally fails closed rather than deleting the claim automatically. An operator must
decide whether to resume, create a new authorized idempotency key, or reconcile a provider side
effect. Never delete a claim solely to make a retry pass.

## Cost controls

Set an AWS Budget and Cost Anomaly Detection outside this stack at the account/organization boundary.
Alarm on Bedrock throttling and unexpected `BedrockCalls / OrdersValidated` ratios after a production
baseline exists. Keep output tokens bounded and producer rate limits upstream.

## Deployment and rollback

Run `make ci`, `sam validate --lint`, then deploy to a non-production stack. Exercise the integration
harness and inspect logs before promotion. CloudFormation rollback handles resource changes; model or
prompt rollback is a reviewed source revert and redeploy. DynamoDB data is not automatically migrated.

