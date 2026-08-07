"""Babylonian-method square root (Newton-Raphson).

Independent of the standard library ``math`` module by design — this
project's standard deviation algorithm calls into here instead of
``math.sqrt``.
"""

from standard_deviation.builtin_helpers import _abs
from standard_deviation.exceptions import (
    ConvergenceError,
    NegativeVarianceError,
)


# Safety iteration limit. The Babylonian method converges quadratically,
# so 100 iterations is more than enough for any realistic input. If we
# have not converged by then, something is wrong with the input and we
# refuse to loop forever.
MAX_ITERATIONS = 1000


def calculate_sqrt(value: float, tolerance: float = 1e-7) -> float:
    """Return the square root of ``value`` using the Babylonian method.

    Parameters
    ----------
    value : float
        A non-negative number whose square root is desired.
    tolerance : float, optional
        The iteration stops when successive approximations differ by
        less than this amount. Defaults to ``1e-7``.

    Returns
    -------
    float
        An approximation of ``sqrt(value)``. Returns ``0`` for zero.

    Raises
    ------
    NegativeVarianceError
        If ``value`` is negative.
    ConvergenceError
        If the iteration does not converge within :data:`MAX_ITERATIONS`
        iterations.
    """
    if value < 0:
        raise NegativeVarianceError(
            f"Invalid input: Negative variance ({value})"
        )
    if value == 0:
        return 0

    x = value
    last_x = 0
    iterations = 0
    while _abs(x - last_x) > tolerance:
        last_x = x
        x = 0.5 * (x + (value / x))
        iterations += 1
        if iterations > MAX_ITERATIONS:
            raise ConvergenceError(
                "Babylonian square root did not converge after "
                f"{MAX_ITERATIONS} "
                f"iterations for value={value}"
            )
    return x
