"""Fast offline guard for common committed-secret patterns and unsafe placeholders."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
IGNORED_PARTS = {".git", ".venv", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
TEXT_SUFFIXES = {".py", ".json", ".yaml", ".yml", ".md", ".txt", ".toml", ".example"}
PATTERNS = {
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b"),
    "unsafe account placeholder": re.compile(
        "YOUR_" + r"ACCOUNT_ID|\b" + "change" + r"me\b", re.IGNORECASE
    ),
}


def main() -> int:
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in IGNORED_PARTS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"Makefile"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{path.relative_to(ROOT)}: {label}")
    if findings:
        print("Potential secret or unsafe placeholder detected:")
        print("\n".join(f"- {finding}" for finding in findings))
        return 1
    print("Offline secret-pattern scan: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
