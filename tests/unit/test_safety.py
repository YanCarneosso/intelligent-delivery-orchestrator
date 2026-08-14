from __future__ import annotations

import pytest

from delivery_orchestrator.safety import detect_safety_signals


@pytest.mark.parametrize(
    "notes",
    [
        "Sou alérgico.",
        "Tenho alergia alimentar.",
        "Intolerância a certos ingredientes.",
        "Preciso de opção sem lactose.",
        "Não posso consumir glúten.",
        "Sem amendoim.",
        "Evitar castanhas.",
        "Alergia a frutos do mar.",
        "Sem cebola.",
        "Não usar leite.",
        "Não pode conter ovos.",
    ],
)
def test_required_food_safety_vocabulary_fails_closed(notes: str) -> None:
    assert detect_safety_signals(notes).allergy_risk is True


def test_multiple_restrictions_are_preserved() -> None:
    signal = detect_safety_signals("Alergia a ovos, amendoim, castanhas e frutos do mar")
    assert {"OVOS", "AMENDOIM", "CASTANHAS", "FRUTOS_DO_MAR"} <= set(signal.restrictions)


def test_plain_note_without_risk_is_not_flagged() -> None:
    assert detect_safety_signals("Entregar na portaria").allergy_risk is False
