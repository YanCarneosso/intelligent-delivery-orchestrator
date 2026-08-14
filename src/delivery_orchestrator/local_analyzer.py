"""Clearly identified deterministic replacement for Bedrock in local demonstrations."""

from __future__ import annotations

import json
from typing import Any

from .safety import detect_safety_signals, normalize_text


def analyze_locally(order: dict[str, Any]) -> str:
    """Produce schema-compatible cognitive output without AWS or an LLM."""
    notes = normalize_text(str(order["notes"]))
    safety = detect_safety_signals(notes)
    anxious_terms = ("ansioso", "ansiosa", "urgente", "atrasado", "preocupado", "rapido")
    negative_terms = ("péssimo", "pessimo", "ruim", "reclama", "nunca")
    positive_terms = ("obrigado", "por favor", "excelente", "adoro")

    if any(term in notes for term in anxious_terms):
        sentiment = "ANXIOUS"
    elif any(term in notes for term in negative_terms):
        sentiment = "NEGATIVE"
    elif any(term in notes for term in positive_terms):
        sentiment = "POSITIVE"
    else:
        sentiment = "NEUTRAL"

    output = {
        "intent": "ORDER",
        "analise_sentimento": sentiment,
        "prioridade": "HIGH" if safety.allergy_risk or sentiment == "ANXIOUS" else "NORMAL",
        "risco_alergia": safety.allergy_risk,
        "restricoes": list(safety.restrictions),
        "confidence": 1.0,
    }
    return json.dumps(output, ensure_ascii=False, separators=(",", ":"))
