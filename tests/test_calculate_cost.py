import unittest

from novelai import Metadata, Resolution


class TestCalculateCost(unittest.TestCase):
    def setUp(self):
        param_s = Metadata(
            prompt="",
            width=Resolution.SMALL_PORTRAIT.value[0],
            height=Resolution.SMALL_PORTRAIT.value[1],
        )
        param_m1 = Metadata(
            prompt="",
            width=Resolution.NORMAL_LANDSCAPE.value[0],
            height=Resolution.NORMAL_LANDSCAPE.value[1],
        )
        param_m2 = Metadata(
            prompt="",
            width=Resolution.NORMAL_SQUARE.value[0],
            height=Resolution.NORMAL_SQUARE.value[1],
            sm=False,
        )
        param_m3 = Metadata(
            prompt="",
            width=Resolution.NORMAL_PORTRAIT.value[0],
            height=Resolution.NORMAL_PORTRAIT.value[1],
            sm_dyn=True,
        )
        param_m4 = Metadata(
            prompt="",
            width=Resolution.NORMAL_SQUARE.value[0],
            height=Resolution.NORMAL_SQUARE.value[1],
            steps=29,
        )
        param_m5 = Metadata(
            prompt="",
            width=Resolution.NORMAL_LANDSCAPE.value[0],
            height=Resolution.NORMAL_LANDSCAPE.value[1],
            n_samples=4,
        )
        param_l1 = Metadata(
            prompt="",
            width=Resolution.LARGE_PORTRAIT.value[0],
            height=Resolution.LARGE_PORTRAIT.value[1],
        )
        param_l2 = Metadata(
            prompt="",
            width=Resolution.LARGE_SQUARE.value[0],
            height=Resolution.LARGE_SQUARE.value[1],
        )
        param_xl = Metadata(
            prompt="",
            width=Resolution.WALLPAPER_LANDSCAPE.value[0],
            height=Resolution.WALLPAPER_LANDSCAPE.value[1],
        )
        self.params = {
            "param_s": param_s,
            "param_m1": param_m1,
            "param_m2": param_m2,
            "param_m3": param_m3,
            "param_m4": param_m4,
            "param_m5": param_m5,
            "param_l1": param_l1,
            "param_l2": param_l2,
            "param_xl": param_xl,
        }
        self.cost_opus = [0, 0, 0, 0, 24, 72, 36, 51, 48]
        self.cost_non_opus = [10, 24, 20, 28, 24, 96, 36, 51, 48]

    def test_opus_true(self):
        for param, cost in zip(self.params, self.cost_opus):
            with self.subTest(f"{param}"):
                result = self.params[param].calculate_cost(is_opus=True)
                self.assertEqual(result, cost)

    def test_opus_false(self):
        for param, cost in zip(self.params, self.cost_non_opus):
            with self.subTest(f"{param}"):
                result = self.params[param].calculate_cost(is_opus=False)
                self.assertEqual(result, cost)


if __name__ == "__main__":
    unittest.main()
