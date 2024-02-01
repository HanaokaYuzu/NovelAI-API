import unittest
from novelai import Metadata


class TestCalculateCost(unittest.TestCase):

    def setUp(self):
        self.params = Metadata(prompt="")

    # Test when is_opus is True and action is generate
    def test_cost_calculation_opus_true(self):
        result = self.params.calculate_cost(is_opus=True)
        self.assertEqual(result, 0)

    # Test when is_opus is False and action is something else
    def test_cost_calculation_opus_false_action_something_else(self):
        result = self.params.calculate_cost(is_opus=False)
        self.assertEqual(result, 24)


if __name__ == "__main__":
    unittest.main()
