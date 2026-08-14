# Cost model

Classification: **estimate**, not a bill or measured production result. Prices and service behavior
were checked against AWS public pages on **2026-08-14** for US East (N. Virginia). Reconfirm before a
deployment because region, free tier, tiering, model profile, taxes, and AWS price changes matter.

## Assumptions

- 700 Nova Lite input tokens and 120 output tokens per successful order.
- 18 Standard Workflow state transitions per happy path, no retry.
- Five Lambda invocations, each 100 ms at 256 MB (conservative hypothesis, not measured on AWS).
- Two DynamoDB writes, each item under 1 KB.
- 3 KB of ingested logs per order.
- No data transfer, KMS customer key, backup storage, Logs Insights, alarms/metrics over free tiers,
  failed executions, real external provider, or ingress cost.
- Estimates below are before free tiers. Standard Workflow includes 4,000 transitions/month free.

## Pricing sources and unit rates

| Component | Rate used | Source |
|---|---:|---|
| Nova Lite input | $0.00006 / 1k tokens | [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/) |
| Nova Lite output | $0.00024 / 1k tokens | [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/) |
| Standard Workflow | $0.025 / 1k transitions | [Step Functions pricing](https://aws.amazon.com/step-functions/pricing/) |
| Lambda requests | $0.20 / 1M | [Lambda pricing](https://aws.amazon.com/lambda/pricing/) |
| Lambda compute | $0.0000166667 / GB-s | [Lambda pricing](https://aws.amazon.com/lambda/pricing/) |
| DynamoDB on-demand writes | $0.625 / 1M WRU | [DynamoDB pricing](https://aws.amazon.com/dynamodb/pricing/) |
| CloudWatch log ingestion | $0.50 / GB | [CloudWatch pricing](https://aws.amazon.com/cloudwatch/pricing/) |

## Calculation

Per successful order:

```text
Bedrock = 0.7 × $0.00006 + 0.12 × $0.00024       = $0.00007080
Step Functions = 18 × $0.000025                   = $0.00045000
Lambda requests = 5 × $0.20 / 1,000,000           = $0.00000100
Lambda compute = 5 × 0.1s × 0.25GB × $0.0000166667= $0.00000208
DynamoDB = 2 × $0.625 / 1,000,000                 = $0.00000125
CloudWatch logs = 0.000003GB × $0.50               = $0.00000150
Total                                                   $0.00052663
```

`python scripts/cost_estimate.py` is the executable source of this arithmetic.

## Monthly estimate

| Successful orders/month | Estimated variable cost before free tiers |
|---:|---:|
| 10,000 | $5.27 |
| 100,000 | $52.66 |
| 1,000,000 | $526.63 |

At these assumptions, Standard Workflow transitions dominate. That is a conscious auditability and
exactly-once trade-off, not a claim that Standard is always economically optimal.

## Sensitivity analysis

| Change at 100k orders | Approximate effect |
|---|---:|
| Input tokens double to 1,400 | +$4.20/month |
| Output tokens double to 240 | +$2.88/month |
| Three additional state transitions | +$7.50/month |
| One full retry of the Bedrock task and related transition | at least +$7.08 model cost plus transitions |
| Logs grow from 3 KB to 30 KB/order | +$0.14/month (before tiering/free tier) |

Static CloudWatch custom metric, dashboard, alarm, PITR backup storage, and real provider charges can
matter independently of order count. Use AWS Pricing Calculator with actual log volume, measured
tokens/duration, retention, and retry rate before approval.

