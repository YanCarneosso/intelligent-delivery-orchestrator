# Privacy assessment

## Data classification

| Field | Classification | Bedrock | Application logs | DynamoDB |
|---|---|---:|---:|---:|
| `order_id`, correlation/idempotency IDs | Internal identifier | No | Yes | Yes |
| Product name/SKU/quantity | Business data | Yes | No | No |
| Free-text notes | Potential PII and health/dietary data | Yes | No | No |
| City/state/postal code/instructions | Location PII | No | No | No |
| Payment method enum | Financial metadata | No | No | No |

No card number, payment token, customer name, phone, email, or street address belongs in this
contract. A real payment provider should receive a token through a dedicated, PCI-reviewed boundary.

## Controls

- The validation Lambda constructs a new model payload; it does not forward the entire order.
- Bedrock receives only product data, notes, and deterministic safety signals.
- Step Functions logging is `ERROR` with execution data disabled.
- EMF logging has an allowlist of identifiers and counters; notes/address are never logged.
- CloudWatch log retention defaults to 30 days and is configurable to 7–90 days.
- DynamoDB uses AWS-owned encryption at rest and point-in-time recovery.
- Tests assert address, delivery instructions, and payment method are absent from the model request.

## Residual risks and deployment decisions

Dietary restrictions and allergy statements can be health-related sensitive data. Before production,
confirm lawful basis, Bedrock regional/data-processing requirements, retention, deletion workflows,
and access logging with privacy/legal stakeholders. `us-east-1` is the documented reference region;
Brazilian deployments must explicitly assess cross-border transfer and LGPD obligations. These are
deployment decisions, not claims made by this codebase.

Use a customer-controlled KMS key when organizational policy requires key rotation or separation of
duties. Add automated deletion for idempotency records only after the replay window and audit
requirements are defined; no arbitrary TTL is imposed here.

