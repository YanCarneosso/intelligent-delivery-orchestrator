"""Deterministic food-safety backstop independent of the LLM."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

ALLERGEN_PATTERNS: dict[str, tuple[str, ...]] = {
    "ALLERGY_DECLARATION": ("alergic", "alergia", "intoler"),
    "AMENDOIM": ("amendoim",),
    "CASTANHAS": ("castanha", "nozes"),
    "FRUTOS_DO_MAR": ("frutos do mar", "camarao", "lagosta"),
    "GLUTEN": ("gluten", "trigo"),
    "LACTOSE": ("lactose",),
    "LEITE": ("leite",),
    "OVOS": ("ovo",),
    "CEBOLA": ("cebola",),
}


@dataclass(frozen=True)
class SafetySignal:
    """Evidence found without relying on probabilistic model behavior."""

    allergy_risk: bool
    restrictions: tuple[str, ...]
    matched_terms: tuple[str, ...]


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(
        character for character in normalized if not unicodedata.combining(character)
    ).lower()


def detect_safety_signals(notes: str) -> SafetySignal:
    """Fail closed on explicit food-risk vocabulary, including adversarial text."""
    normalized = normalize_text(notes)
    restrictions: set[str] = set()
    matched_terms: set[str] = set()

    for restriction, patterns in ALLERGEN_PATTERNS.items():
        for pattern in patterns:
            if re.search(rf"(?<!\w){re.escape(pattern)}\w*", normalized):
                matched_terms.add(pattern)
                if restriction != "ALLERGY_DECLARATION":
                    restrictions.add(restriction)

    return SafetySignal(
        allergy_risk=bool(matched_terms),
        restrictions=tuple(sorted(restrictions)),
        matched_terms=tuple(sorted(matched_terms)),
    )
