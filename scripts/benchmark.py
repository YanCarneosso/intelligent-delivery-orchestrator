"""Measure the deterministic local simulator; this is not an AWS benchmark."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from copy import deepcopy
from pathlib import Path
from typing import Any

from delivery_orchestrator.workflow import LocalWorkflow

ROOT = Path(__file__).parents[1]


def percentile(values: list[float], quantile: float) -> float:
    index = max(0, min(len(values) - 1, round((len(values) - 1) * quantile)))
    return sorted(values)[index]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=500)
    args = parser.parse_args()
    if args.iterations < 1:
        parser.error("--iterations must be positive")
    with (ROOT / "tests/fixtures/allergy_order.json").open(encoding="utf-8") as fixture_file:
        fixture: dict[str, Any] = json.load(fixture_file)

    durations: list[float] = []
    for index in range(args.iterations):
        order = deepcopy(fixture)
        order["order_id"] = f"ORD-BENCH-{index:06d}"
        order["idempotency_key"] = f"idem-benchmark-{index:06d}"
        started = time.perf_counter()
        result = LocalWorkflow().run(order)
        durations.append((time.perf_counter() - started) * 1000)
        if result["workflow_status"] != "COMPLETED":
            raise RuntimeError(f"benchmark execution failed: {result['workflow_status']}")

    report = {
        "classification": "LOCAL_SIMULATOR_MEASUREMENT",
        "aws_calls": 0,
        "llm_calls": 0,
        "iterations": args.iterations,
        "mean_ms": round(statistics.mean(durations), 3),
        "p50_ms": round(percentile(durations, 0.50), 3),
        "p95_ms": round(percentile(durations, 0.95), 3),
        "max_ms": round(max(durations), 3),
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
