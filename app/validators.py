from __future__ import annotations

import re


class ValidationError(ValueError):
    """Raised when user input cannot be used for a roll."""


def parse_sides(raw_value: str | None) -> int:
    """Parse a side count such as '20' or 'D20'."""
    text = (raw_value or "").strip().upper()
    if not text:
        raise ValidationError("Informe a quantidade de lados do dado.")

    if text.startswith("D"):
        text = text[1:].strip()

    if not re.fullmatch(r"\d+", text):
        raise ValidationError("Use um numero inteiro para os lados, como 20 ou D20.")

    sides = int(text)
    if sides <= 1:
        raise ValidationError("O dado precisa ter mais de 1 lado.")

    return sides


def parse_modifier(raw_value: str | None) -> int:
    """Parse a modifier such as '+3', '-2', '0' or an empty value."""
    text = (raw_value or "").strip().replace(" ", "")
    if not text:
        return 0

    if not re.fullmatch(r"[+-]?\d+", text):
        raise ValidationError("Use um modificador como +3, -2 ou 0.")

    return int(text)


def normalize_roll_name(raw_value: str | None) -> str:
    """Normalize the optional roll name."""
    text = (raw_value or "").strip()
    if not text:
        return "Rolagem"
    return text[:80]


def validate_roll_inputs(sides_text: str | None, modifier_text: str | None, name_text: str | None) -> dict[str, int | str]:
    """Validate and normalize all inputs needed for one roll."""
    return {
        "sides": parse_sides(sides_text),
        "modifier": parse_modifier(modifier_text),
        "name": normalize_roll_name(name_text),
    }
