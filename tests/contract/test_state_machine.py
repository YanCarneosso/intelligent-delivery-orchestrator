from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parents[2]
WORKFLOW_PATH = ROOT / "aws-step-functions" / "workflow.asl.json"


def _workflow() -> dict[str, Any]:
    with WORKFLOW_PATH.open(encoding="utf-8") as workflow_file:
        value = json.load(workflow_file)
    assert isinstance(value, dict)
    return value


def _assert_targets(states: dict[str, Any]) -> None:
    names = set(states)
    for state in states.values():
        if "Next" in state:
            assert state["Next"] in names
        if "Default" in state:
            assert state["Default"] in names
        for choice in state.get("Choices", []):
            assert choice["Next"] in names
        for catcher in state.get("Catch", []):
            assert catcher["Next"] in names
        for branch in state.get("Branches", []):
            assert branch["StartAt"] in branch["States"]
            _assert_targets(branch["States"])


def test_state_machine_is_connected() -> None:
    workflow = _workflow()
    assert workflow["StartAt"] in workflow["States"]
    _assert_targets(workflow["States"])


def test_architecture_uses_direct_bedrock_integration() -> None:
    state = _workflow()["States"]["InvokeNovaLite"]
    assert state["Resource"] == "arn:aws:states:::bedrock:invokeModel"
    assert state["Parameters"]["ModelId"] == "${BedrockModelId}"
    assert state["TimeoutSeconds"] == 20


def test_bedrock_retries_only_transient_errors() -> None:
    errors = _workflow()["States"]["InvokeNovaLite"]["Retry"][0]["ErrorEquals"]
    assert "States.ALL" not in errors
    assert "Bedrock.ThrottlingException" in errors
    assert "Bedrock.ServiceUnavailableException" in errors


def test_workflow_demonstrates_required_state_types() -> None:
    states = _workflow()["States"]
    types = {state["Type"] for state in states.values()}
    assert {"Task", "Choice", "Parallel", "Pass", "Fail", "Succeed"} <= types
    assert any("Retry" in state for state in states.values())
    assert any("Catch" in state for state in states.values())


def test_payment_precedes_fulfillment() -> None:
    states = _workflow()["States"]
    assert states["AuthorizePayment"]["Next"] == "PaymentApproved"
    assert states["PaymentApproved"]["Choices"][0]["Next"] == "FulfillInParallel"


def test_notification_failure_is_explicitly_degraded() -> None:
    parallel = _workflow()["States"]["FulfillInParallel"]
    notification_states = parallel["Branches"][1]["States"]
    assert notification_states["NotifyCustomer"]["Catch"][0]["Next"] == "NotificationDegraded"


def test_template_substitutes_every_external_resource() -> None:
    template = (ROOT / "template.yaml").read_text(encoding="utf-8")
    for token in (
        "ValidateFunctionArn",
        "NormalizeFunctionArn",
        "PaymentFunctionArn",
        "DispatchFunctionArn",
        "NotificationFunctionArn",
        "IdempotencyTable",
        "BedrockModelId",
    ):
        assert f"{token}:" in template


def test_lambda_deployment_assets_match_public_contracts() -> None:
    assets = ROOT / "src" / "delivery_orchestrator" / "assets"
    for name in ("order.schema.json", "cognitive-output.schema.json"):
        assert json.loads((assets / name).read_text(encoding="utf-8")) == json.loads(
            (ROOT / "schemas" / name).read_text(encoding="utf-8")
        )
    assert (assets / "system_prompt_delivery.txt").read_text(encoding="utf-8") == (
        ROOT / "amazon-bedrock" / "prompt_templates" / "system_prompt_delivery.txt"
    ).read_text(encoding="utf-8")


def test_lambda_code_uri_excludes_repository_and_virtual_environment() -> None:
    template = (ROOT / "template.yaml").read_text(encoding="utf-8")
    assert template.count("CodeUri: src/") == 5
