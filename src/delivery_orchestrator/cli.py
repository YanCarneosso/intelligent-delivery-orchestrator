"""Local demo and schema-validation commands."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .adapters import (
    ReferenceDispatchGateway,
    ReferenceNotificationGateway,
    ReferencePaymentGateway,
)
from .contracts import validate_schema_files
from .workflow import LocalWorkflow


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as json_file:
        value = json.load(json_file)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _render(result: dict[str, Any]) -> None:
    print("LOCAL DEMO — no AWS or LLM calls were made\n")
    print(f"Order: {result['order_id']}")
    for step in result["steps"]:
        print(f"{step['name']:.<30} {step['status']}")
    analysis = result.get("analysis") or {}
    if analysis:
        print(f"{'Allergy risk':.<30} {str(analysis['risco_alergia']).upper()}")
        print(f"{'Sentiment':.<30} {analysis['analise_sentimento']}")
        print(f"{'Operational priority':.<30} {analysis['prioridade']}")
    print(f"\nWorkflow result: {result['workflow_status']}")
    print(f"Measured local duration: {result['measured_duration_ms']} ms")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "fixture",
        nargs="?",
        type=Path,
        default=Path("tests/fixtures/allergy_order.json"),
        help="order fixture to execute",
    )
    parser.add_argument(
        "--fault",
        choices=("none", "payment", "dispatch", "notification"),
        default="none",
        help="inject a documented local adapter fault",
    )
    parser.add_argument("--json", action="store_true", help="print machine-readable output")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    validate_schema_files()
    workflow = LocalWorkflow(
        payment=ReferencePaymentGateway(should_decline=args.fault == "payment"),
        dispatch=ReferenceDispatchGateway(should_fail=args.fault == "dispatch"),
        notification=ReferenceNotificationGateway(should_fail=args.fault == "notification"),
    )
    result = workflow.run(load_json(args.fixture))
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        _render(result)
    return 0 if result["workflow_status"].startswith("COMPLETED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
