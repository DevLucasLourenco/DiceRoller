import unittest

from app.validators import ValidationError, normalize_roll_name, parse_modifier, parse_sides, validate_roll_inputs


class ValidatorTests(unittest.TestCase):
    def test_parse_sides_accepts_number_or_d_notation(self) -> None:
        self.assertEqual(parse_sides("20"), 20)
        self.assertEqual(parse_sides("D12"), 12)
        self.assertEqual(parse_sides("d100"), 100)

    def test_parse_sides_rejects_invalid_values(self) -> None:
        for value in ("", "abc", "D1", "0"):
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    parse_sides(value)

    def test_parse_modifier_accepts_signed_values_and_blank(self) -> None:
        self.assertEqual(parse_modifier("+5"), 5)
        self.assertEqual(parse_modifier("-2"), -2)
        self.assertEqual(parse_modifier("0"), 0)
        self.assertEqual(parse_modifier(""), 0)

    def test_parse_modifier_rejects_invalid_values(self) -> None:
        for value in ("++2", "abc", "1.5"):
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    parse_modifier(value)

    def test_validate_roll_inputs_normalizes_all_fields(self) -> None:
        values = validate_roll_inputs("D20", "+3", " Ataque ")

        self.assertEqual(values, {"sides": 20, "modifier": 3, "name": "Ataque"})

    def test_roll_name_defaults(self) -> None:
        self.assertEqual(normalize_roll_name(""), "Rolagem")


if __name__ == "__main__":
    unittest.main()
