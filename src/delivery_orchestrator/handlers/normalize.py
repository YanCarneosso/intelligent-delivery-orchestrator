"""Lambda handler for validating and normalizing untrusted Bedrock output."""

from __future__ import annotations

from typing import Any

from ..cognitive import extract_model_text, normalize_analysis
from ..safety import SafetySignal
from ..telemetry import metric_log


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    del context
    raw_safety = event["safety"]
    safety = SafetySignal(
        allergy_risk=bool(raw_safety["allergy_risk"]),
        restrictions=tuple(raw_safety["restrictions"]),
        matched_terms=tuple(raw_safety["matched_terms"]),
    )
    analysis = normalize_analysis(extract_model_text(event), safety)
    usage = event.get("bedrock", {}).get("usage", {})
    input_tokens = usage.get("inputTokens", 0)
    output_tokens = usage.get("outputTokens", 0)
    retry_count = event.get("bedrock", {}).get("retryCount", 0)
    if not all(isinstance(value, int) for value in (input_tokens, output_tokens, retry_count)):
        input_tokens = output_tokens = retry_count = 0
    metric_log(
        "cognitive_output_accepted",
        metrics={
            "BedrockCalls": 1,
            "AllergyRiskOrders": int(analysis["risco_alergia"]),
            "HighPriorityOrders": int(analysis["prioridade"] == "HIGH"),
            "BedrockInputTokens": input_tokens,
            "BedrockOutputTokens": output_tokens,
            "BedrockRetries": retry_count,
        },
        order_id=event["order"]["order_id"],
        correlation_id=event["order"]["correlation_id"],
        safety_override=analysis["safety_override_applied"],
    )
    return analysis
