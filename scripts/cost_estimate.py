"""Reproducible monthly variable-cost estimate from documented assumptions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Assumptions:
    input_tokens: int = 700
    output_tokens: int = 120
    state_transitions: int = 18
    lambda_invocations: int = 5
    lambda_duration_seconds: float = 0.1
    lambda_memory_gb: float = 0.25
    dynamodb_writes: int = 2
    log_gb: float = 0.000003


def per_order(assumptions: Assumptions) -> dict[str, float]:
    return {
        "bedrock_nova_lite": assumptions.input_tokens / 1000 * 0.00006
        + assumptions.output_tokens / 1000 * 0.00024,
        "step_functions_standard": assumptions.state_transitions * 0.000025,
        "lambda_requests": assumptions.lambda_invocations * 0.20 / 1_000_000,
        "lambda_compute": assumptions.lambda_invocations
        * assumptions.lambda_duration_seconds
        * assumptions.lambda_memory_gb
        * 0.0000166667,
        "dynamodb_writes": assumptions.dynamodb_writes * 0.625 / 1_000_000,
        "cloudwatch_log_ingestion": assumptions.log_gb * 0.50,
    }


def main() -> int:
    costs = per_order(Assumptions())
    print("Estimate in USD before free tiers, taxes, data transfer, and regional variation")
    print(f"Per order: ${sum(costs.values()):.8f}")
    for volume in (10_000, 100_000, 1_000_000):
        print(f"{volume:>9,} orders/month: ${sum(costs.values()) * volume:,.2f}")
    print("Components per order:")
    for name, cost in costs.items():
        print(f"  {name:.<32} ${cost:.8f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
