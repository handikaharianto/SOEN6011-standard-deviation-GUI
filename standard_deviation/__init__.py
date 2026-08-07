"""Standard deviation calculator — from-scratch implementation with a Tkinter GUI.

Public API
----------

- :func:`calculate_std_dev_welford` — Welford's online algorithm.
- :func:`calculate_sqrt` — Babylonian square root.
- :func:`parse_numbers` — string-to-list-of-floats for the GUI.
- The exception classes in :mod:`standard_deviation.exceptions` are
  re-exported so callers can catch them via
  ``from standard_deviation import StandardDeviationError``.
"""

from standard_deviation._version import __version__
from standard_deviation.algorithm import (
    MAX_NUMERIC_LIMIT,
    calculate_std_dev_welford,
)
from standard_deviation.exceptions import (
    ConvergenceError,
    EmptyInputError,
    InsufficientDataError,
    InvalidModeError,
    InvalidNumberError,
    NegativeVarianceError,
    NumericOverflowError,
    StandardDeviationError,
)
from standard_deviation.parser import parse_numbers
from standard_deviation.sqrt import MAX_ITERATIONS, calculate_sqrt


__all__ = [
    "__version__",
    "MAX_ITERATIONS",
    "MAX_NUMERIC_LIMIT",
    "calculate_sqrt",
    "calculate_std_dev_welford",
    "parse_numbers",
    # Exceptions
    "ConvergenceError",
    "EmptyInputError",
    "InsufficientDataError",
    "InvalidModeError",
    "InvalidNumberError",
    "NegativeVarianceError",
    "NumericOverflowError",
    "StandardDeviationError",
]
