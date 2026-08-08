"""PyUnit tests for Welford's standard-deviation implementation."""

import math
import unittest
from unittest.mock import patch

from standard_deviation.algorithm import calculate_std_dev_welford
from standard_deviation.exceptions import (
    InsufficientDataError,
    InvalidModeError,
    InvalidNumberError,
    NumericOverflowError,
)


class CalculateStdDevWelfordTests(unittest.TestCase):
    """Test the public behavior of ``calculate_std_dev_welford``."""

    def test_calculates_population_standard_deviation(self):
        data = [2, 4, 4, 4, 5, 5, 7, 9]

        result = calculate_std_dev_welford(data, is_population=True)

        self.assertAlmostEqual(result, 2.0, places=7)

    def test_calculates_sample_standard_deviation(self):
        data = [2, 4, 4, 4, 5, 5, 7, 9]

        result = calculate_std_dev_welford(data, is_population=False)

        self.assertAlmostEqual(result, math.sqrt(32 / 7), places=7)

    def test_accepts_negative_and_floating_point_values(self):
        data = [-5.5, -2.5, 0.5, 3.5]

        result = calculate_std_dev_welford(data, is_population=True)

        self.assertAlmostEqual(result, math.sqrt(11.25), places=7)

    def test_returns_zero_for_identical_values(self):
        result = calculate_std_dev_welford(
            [7.25, 7.25, 7.25], is_population=True
        )

        self.assertEqual(result, 0)

    def test_single_value_population_has_zero_deviation(self):
        result = calculate_std_dev_welford([42], is_population=True)

        self.assertEqual(result, 0)

    def test_is_stable_for_large_closely_spaced_values(self):
        data = [1_000_000_000_004, 1_000_000_000_007,
                1_000_000_000_013, 1_000_000_000_016]

        result = calculate_std_dev_welford(data, is_population=True)

        self.assertAlmostEqual(result, math.sqrt(22.5), places=7)

    def test_population_mode_uses_count_as_variance_denominator(self):
        with patch(
            "standard_deviation.algorithm.calculate_sqrt",
            return_value=123.0,
        ) as sqrt_mock:
            result = calculate_std_dev_welford([1, 2, 3], True)

        self.assertEqual(result, 123.0)
        sqrt_mock.assert_called_once_with(2 / 3)

    def test_sample_mode_uses_count_minus_one_as_variance_denominator(self):
        with patch(
            "standard_deviation.algorithm.calculate_sqrt",
            return_value=123.0,
        ) as sqrt_mock:
            result = calculate_std_dev_welford([1, 2, 3], False)

        self.assertEqual(result, 123.0)
        sqrt_mock.assert_called_once_with(1.0)

    def test_empty_dataset_raises_insufficient_data_error(self):
        with self.assertRaisesRegex(
            InsufficientDataError, "0 values provided"
        ) as context:
            calculate_std_dev_welford([], is_population=True)

        self.assertEqual(context.exception.count, 0)

    def test_single_value_sample_raises_insufficient_data_error(self):
        with self.assertRaisesRegex(
            InsufficientDataError, "need at least 2 values"
        ) as context:
            calculate_std_dev_welford([42], is_population=False)

        self.assertEqual(context.exception.count, 1)

    def test_rejects_non_boolean_mode(self):
        invalid_modes = [1, 0, None, "population"]

        for mode in invalid_modes:
            with self.subTest(mode=mode):
                with self.assertRaises(InvalidModeError):
                    calculate_std_dev_welford([1, 2], mode)

    def test_rejects_non_numeric_values_and_reports_position(self):
        invalid_values = ["2", None, True]

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaises(InvalidNumberError) as context:
                    calculate_std_dev_welford(
                        [1, invalid_value, 3], is_population=True
                    )

                self.assertEqual(context.exception.position, 2)

    def test_rejects_non_finite_values_and_reports_position(self):
        non_finite_values = [float("nan"), float("inf"), float("-inf")]

        for value in non_finite_values:
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    InvalidNumberError, "must be finite"
                ) as context:
                    calculate_std_dev_welford(
                        [1.0, 2.0, value], is_population=True
                    )

                self.assertEqual(context.exception.position, 3)

    def test_raises_numeric_overflow_for_excessive_mean(self):
        with self.assertRaisesRegex(
            NumericOverflowError, "position 1"
        ):
            calculate_std_dev_welford([1.1e308], is_population=True)

    def test_raises_numeric_overflow_for_non_finite_intermediate_value(self):
        with self.assertRaisesRegex(
            NumericOverflowError, "position 2"
        ):
            calculate_std_dev_welford(
                [1e308, -1e308], is_population=True
            )


if __name__ == "__main__":
    unittest.main()
