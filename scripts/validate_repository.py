"""Offline repository and Amazon States Language structural validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from delivery_orchestrator.contracts import validate_schema_files

ROOT = Path(__file__).parents[1]
WORKFLOW = ROOT / "aws-step-functions" / "workflow.asl.json"
REQUIRED_FILES = (
    "README.md",
    "template.yaml",
    "aws-step-functions/workflow.asl.json",
    "schemas/order.schema.json",
    "schemas/cognitive-output.schema.json",
    "docs/architecture.md",
    "docs/cost-model.md",
    "docs/privacy.md",
    "docs/threat-model.md",
    ".github/workflows/ci.yml",
)


def load_workflow() -> dict[str, Any]:
    with WORKFLOW.open(encoding="utf-8") as workflow_file:
        workflow = json.load(workflow_file)
    if not isinstance(workflow, dict):
        raise ValueError("workflow must be a JSON object")
    return workflow


def validate_state_block(states: dict[str, Any], start_at: str, scope: str) -> None:
    if start_at not in states:
        raise ValueError(f"{scope}: StartAt target {start_at!r} does not exist")
    targets: set[str] = {start_at}
    for name, state in states.items():
        terminal = state.get("Type") in {"Succeed", "Fail"} or state.get("End") is True
        if not terminal and "Next" not in state and state.get("Type") != "Choice":
            raise ValueError(f"{scope}.{name}: state has no terminal marker or Next")
        if "Next" in state:
            targets.add(state["Next"])
        if "Default" in state:
            targets.add(state["Default"])
        targets.update(choice["Next"] for choice in state.get("Choices", []))
        targets.update(catcher["Next"] for catcher in state.get("Catch", []))
        for retry in state.get("Retry", []):
            if "States.ALL" in retry["ErrorEquals"]:
                raise ValueError(f"{scope}.{name}: indiscriminate retry is forbidden")
        for index, branch in enumerate(state.get("Branches", [])):
            validate_state_block(branch["States"], branch["StartAt"], f"{scope}.{name}[{index}]")
    unknown = targets - set(states)
    if unknown:
        raise ValueError(f"{scope}: unknown transition target(s): {sorted(unknown)}")


def main() -> int:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        raise FileNotFoundError(f"required repository artifacts missing: {missing}")
    validate_schema_files()
    workflow = load_workflow()
    validate_state_block(workflow["States"], workflow["StartAt"], "workflow")
    if WORKFLOW.stat().st_size > 256 * 1024:
        raise ValueError("state machine definition exceeds the Step Functions 256 KiB limit")
    print("Repository contracts and workflow structure: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
