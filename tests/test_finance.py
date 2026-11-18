import unittest
from finance import SCENARIOS, calculate


class FinanceTests(unittest.TestCase):
    def test_base_probabilities(self):
        result = calculate(100, SCENARIOS["base"])
        self.assertAlmostEqual(result["success"], .96)
        self.assertAlmostEqual(result["attempts"], 1.2)
        self.assertAlmostEqual(result["refunds"], 586.08)

    def test_no_success_refunds_all(self):
        result = calculate(1, {**SCENARIOS["base"], "p": 0})
        self.assertEqual(result["net"], 0)
        self.assertIsNone(result["break_even"])

    def test_reject_invalid_probability(self):
        with self.assertRaises(ValueError):
            calculate(1, {**SCENARIOS["base"], "p": 1.1})


if __name__ == "__main__":
    unittest.main()
