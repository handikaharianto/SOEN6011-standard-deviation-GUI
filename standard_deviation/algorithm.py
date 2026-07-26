"""Welford's online algorithm for standard deviation.

Computes population (denominator ``n``) or sample (denominator ``n - 1``)
standard deviation in a single pass. Numerically stable for large
datasets with closely-spaced values. Independent of the ``math`` module
and the ``sum`` / ``abs`` / ``pow`` built-ins.
"""

from standard_deviation.builtin_helpers import _abs, _is_finite
from standard_deviation.exceptions import (
    InsufficientDataError,
    InvalidNumberError,
    InvalidModeError,
    NumericOverflowError,
)
from standard_deviation.sqrt import calculate_sqrt


# Literal overflow threshold. Matches Python float max (~1.7976e308)
# with margin. Defined as a literal so we avoid importing ``sys``.
MAX_NUMERIC_LIMIT = 1e308


def calculate_std_dev_welford(data: list, is_population: bool) -> float:
    """Compute the standard deviation of ``data`` using Welford's recurrence.

    Parameters
    ----------
    data : list[float]
        Already-parsed numeric values. Non-numeric or missing entries
        must be removed by the caller (the GUI does this via
        :func:`standard_deviation.parser.parse_numbers`).
    is_population : bool
        ``True`` for population standard deviation (denominator ``n``);
        ``False`` for sample standard deviation (denominator ``n - 1``).

    Returns
    -------
    float
        The standard deviation.

    Raises
    ------
    InvalidModeError
        If ``is_population`` is not a ``bool``.
    InvalidNumberError
        If any element of ``data`` is not a finite ``int`` or ``float``.
        The ``position`` attribute is the 1-based index of the element.
    InsufficientDataError
        If there are zero valid data points, or if exactly one data
        point is supplied in sample mode.
    NumericOverflowError
        If ``mean`` or ``m2`` cross :data:`MAX_NUMERIC_LIMIT` mid-loop.
    """
    if not isinstance(is_population, bool):
        raise InvalidModeError(
            f"is_population must be a bool, got {type(is_population).__name__}: "
            f"{is_population!r}"
        )

    count = 0
    mean = 0.0
    m2 = 0.0  # sum of squared deviations from the current mean

    for index, item in enumerate(data, start=1):
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise InvalidNumberError(
                f"Invalid number at position {index}: {type(item).__name__} {item!r}",
                position=index,
            )
        if not _is_finite(item):
            raise InvalidNumberError(
                f"Number must be finite at position {index}: {item!r}",
                position=index,
            )

        count += 1
        delta = item - mean
        mean = mean + (delta / count)
        delta2 = item - mean
        m2 = m2 + (delta * delta2)

        # Guard against overflow on either side of zero. Variance is
        # always non-negative, so a negative ``m2`` means numerical
        # noise has crept in; we treat it as overflow as well.
        if not _is_finite(mean) or not _is_finite(m2):
            raise NumericOverflowError(
                f"Numerical overflow detected at position {index}: "
                f"mean={mean}, m2={m2}"
            )
        if _abs(m2) > MAX_NUMERIC_LIMIT or _abs(mean) > MAX_NUMERIC_LIMIT:
            raise NumericOverflowError(
                f"Numerical overflow detected at position {index}: "
                f"mean={mean}, m2={m2}"
            )

    # Validate dataset size
    if count == 0:
        raise InsufficientDataError(
            "Insufficient data points for calculation: 0 values provided",
            count=0,
        )
    if count == 1 and not is_population:
        raise InsufficientDataError(
            "Insufficient data points for sample standard deviation: "
            "need at least 2 values, got 1",
            count=count,
        )

    if is_population:
        variance = m2 / count
    else:
        variance = m2 / (count - 1)

    return calculate_sqrt(variance)
