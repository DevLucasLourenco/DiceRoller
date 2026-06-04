import unittest

from app.dice_engine import build_history_line, format_modifier, roll_dice


class FixedRng:
    def __init__(self, value: int) -> None:
        self.value = value

    def randint(self, a: int, b: int) -> int:
        return self.value


class DiceEngineTests(unittest.TestCase):
    def test_roll_dice_returns_expected_shape(self) -> None:
        result = roll_dice(20, 3, rng=FixedRng(17))

        self.assertEqual(result["sides"], 20)
        self.assertEqual(result["natural_result"], 17)
        self.assertEqual(result["modifier"], 3)
        self.assertEqual(result["final_result"], 20)
        self.assertFalse(result["is_critical_success"])
        self.assertFalse(result["is_critical_failure"])

    def test_critical_success_and_failure(self) -> None:
        self.assertTrue(roll_dice(8, 0, rng=FixedRng(8))["is_critical_success"])
        self.assertTrue(roll_dice(8, 0, rng=FixedRng(1))["is_critical_failure"])

    def test_format_modifier(self) -> None:
        self.assertEqual(format_modifier(3), "+3")
        self.assertEqual(format_modifier(-2), "-2")
        self.assertEqual(format_modifier(0), "0")

    def test_history_line_includes_critical_marker(self) -> None:
        result = roll_dice(20, 5, rng=FixedRng(20))
        line = build_history_line("Ataque", result)

        self.assertIn("[ Ataque ] D20 +5", line)
        self.assertIn("ACERTO CRITICO", line)


if __name__ == "__main__":
    unittest.main()
