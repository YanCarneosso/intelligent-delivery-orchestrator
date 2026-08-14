# Five-minute reviewer guide

## What this project demonstrates

AWS serverless architecture, generative-AI boundary design, distributed-system idempotency, JSON
contracts, food-safety defense in depth, least-privilege IAM, resilience, observability,
infrastructure as code, automated testing, CI/CD governance, cost reasoning, and honest measurement.

## Review path

1. **See the architecture** — the README diagram and `docs/architecture.md` show only deployed
   components.
2. **Run `make demo`** — observe a real deterministic local execution explicitly labeled as a mock.
3. **See the tests** — focus on `tests/unit/test_safety.py` and the adversarial workflow case.
4. **Inspect the state machine** — `aws-step-functions/workflow.asl.json` directly invokes Bedrock and
   keeps payment/fulfillment deterministic.
5. **Read the ADRs** — Standard versus Express, direct Bedrock, model choice, schema, SAM,
   idempotency, and IAM logging exception.
6. **Review the threat model** — prompt injection, replay, PII, denial of wallet, and supply chain are
   paired with concrete or explicit future controls.
7. **Inspect CI** — `.github/workflows/ci.yml` runs format, lint, type, schema/workflow, test,
   dependency, secret, and SAM validation gates.

## Useful interview discussion

- Why Standard Workflow is justified despite transition cost.
- Why an LLM must never own payment or food-safety truth.
- What DynamoDB idempotency does and does not guarantee across external providers.
- Why notification is degradable while dispatch is critical.
- How to replace the three reference adapters safely.
- Why `<800 ms` is a target, not a result, and how to measure it.
- When cross-region inference would improve throughput but complicate residency and IAM.

