from __future__ import annotations

from random import SystemRandom
from typing import Any, Protocol


class SupportsRandInt(Protocol):
    def randint(self, a: int, b: int) -> int:
        """Return a random integer N such that a <= N <= b."""


_secure_random = SystemRandom()


def format_modifier(modifier: int) -> str:
    """Format a modifier for display."""
    if modifier > 0:
        return f"+{modifier}"
    return str(modifier)


def roll_dice(sides: int, modifier: int = 0, rng: SupportsRandInt | None = None) -> dict[str, Any]:
    """Roll a die and return a structured result."""
    if not isinstance(sides, int):
        raise TypeError("sides must be an integer")
    if sides <= 1:
        raise ValueError("sides must be greater than 1")
    if not isinstance(modifier, int):
        raise TypeError("modifier must be an integer")

    generator = rng or _secure_random
    natural_result = generator.randint(1, sides)
    final_result = natural_result + modifier

    return {
        "sides": sides,
        "natural_result": natural_result,
        "modifier": modifier,
        "final_result": final_result,
        "is_critical_success": natural_result == sides,
        "is_critical_failure": natural_result == 1,
    }


def build_history_line(roll_name: str, result: dict[str, Any]) -> str:
    """Build a compact, human-friendly history line."""
    critical = ""
    if result["is_critical_success"]:
        critical = "  |  ACERTO CRITICO"
    elif result["is_critical_failure"]:
        critical = "  |  FALHA CRITICA"

    modifier = format_modifier(result["modifier"])
    return (
        f"[ {roll_name} ] D{result['sides']} {modifier} "
        f"(natural {result['natural_result']}) = {result['final_result']}{critical}"
    )
