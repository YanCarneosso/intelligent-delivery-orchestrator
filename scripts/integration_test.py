"""Start and verify a real deployed Standard Workflow execution."""

from __future__ import annotations

import argparse
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

import boto3

ROOT = Path(__file__).parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--show-result", action="store_true")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    state_machine_arn = os.environ.get("STATE_MACHINE_ARN")
    if not state_machine_arn:
        parser.error("STATE_MACHINE_ARN must reference a deployed stack output")

    with (ROOT / "tests/fixtures/allergy_order.json").open(encoding="utf-8") as fixture_file:
        order: dict[str, Any] = json.load(fixture_file)
    run_id = uuid.uuid4().hex[:12]
    order["order_id"] = f"ORD-AWS-{run_id.upper()}"
    order["idempotency_key"] = f"aws-integration-{run_id}"
    order["correlation_id"] = f"corr-aws-{run_id}"

    client = boto3.client("stepfunctions")
    response = client.start_execution(
        stateMachineArn=state_machine_arn,
        name=f"integration-{run_id}",
        input=json.dumps(order),
    )
    execution_arn = response["executionArn"]
    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        execution = client.describe_execution(executionArn=execution_arn)
        if execution["status"] != "RUNNING":
            report = {
                "classification": "REAL_AWS_INTEGRATION_RESULT",
                "execution_arn": execution_arn,
                "status": execution["status"],
            }
            if args.show_result and execution.get("output"):
                report["output"] = json.loads(execution["output"])
            print(json.dumps(report, indent=2, default=str))
            return 0 if execution["status"] == "SUCCEEDED" else 1
        time.sleep(2)
    raise TimeoutError(f"execution did not finish within {args.timeout} seconds: {execution_arn}")


if __name__ == "__main__":
    raise SystemExit(main())
