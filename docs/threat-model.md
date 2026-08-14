# Threat model

Method: lightweight STRIDE analysis of the deployed reference boundary. Assets include food-safety
signals, workflow integrity, payment authorization state, identifiers, AWS budget, and audit history.

| Threat | STRIDE | Control implemented | Residual risk / next control |
|---|---|---|---|
| Prompt injection clears an allergy | Tampering | Notes are labeled untrusted; deterministic detection is OR-ed after schema validation | Expand/evaluate multilingual vocabulary; human safety escalation |
| Model emits invalid/extra JSON | Tampering | Bare JSON only; closed Draft 2020-12 schema; no retry | Model drift can increase rejection rate; alarm and evaluate versions |
| Caller uses `CHEQUE` or malformed payload | Tampering | Pre-inference closed schema and enums | Authenticated ingress is out of scope |
| Replay/duplicate execution | Spoofing/Tampering | Conditional DynamoDB idempotency claim | Real providers also need the same idempotency key |
| IAM privilege escalation | Elevation | Separate trust policies and action/resource allowlists | CloudFormation deployer permissions need organization-level guardrails |
| PII reaches model or logs | Information disclosure | Rebuilt minimized prompt; payload logging disabled; log allowlist | Notes necessarily reach Bedrock and may contain unexpected PII |
| Malicious oversized payload | Denial of service | String/item bounds, closed schema, Step Functions 256 KiB boundary | Add WAF/API quotas if HTTP ingress is introduced |
| Bedrock throttling/outage | Denial of service | Bounded transient retries, timeout, categorized failure | Consider queue/backpressure at ingress and quota alarms |
| Denial of wallet | Denial of service | Validation before Bedrock, max 512 output tokens, bounded retries, dashboard | Add AWS Budgets/anomaly detection and producer rate limits per tenant |
| Logs reveal sensitive data | Information disclosure | No notes/address, error-only execution logs without data, retention | Exception messages must remain sanitized in future adapters |
| Fake payment/dispatch claim | Repudiation | Adapter receipts identify `REFERENCE_NON_*`; docs disclose boundary | Production integrations require signed/auditable provider receipts |
| Dependency or action compromise | Tampering/Elevation | Version ranges, dependency audit CI, pinned major GitHub actions | Add lockfile/SBOM and artifact signing for production release |
| CloudFormation supply-chain mutation | Tampering | IaC reviewed in PR; branch protection guidance | Pin action commits and enforce deployment environment approval |
| Rogue model ID/change | Tampering | SAM parameter allowlists exactly Nova Lite v1; IAM exact model ARN | Upgrade only through reviewed ADR and evaluation suite |

## Abuse cases tested

- Explicit instruction to return `risco_alergia=false` after declaring peanut allergy.
- Markdown-wrapped, missing-field, extra-field, wrong-type, invalid-enum, and out-of-range outputs.
- Multiple allergies and accented Portuguese vocabulary.
- Duplicate idempotency key, invalid payment, dependency timeout/throttle, payment/dispatch/notification
  failures.

## Security assumptions

The upstream caller is authenticated and authorized to start executions; CloudTrail and AWS account
controls exist; Bedrock access is enabled only in the intended region; and real provider adapters are
not yet installed. Violating one of these assumptions requires updating this model before production.

