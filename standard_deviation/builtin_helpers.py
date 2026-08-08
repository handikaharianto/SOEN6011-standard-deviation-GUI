"""From-scratch replacements for the forbidden mathematical built-ins.

This module deliberately avoids the ``math`` module and the
``sum``, ``abs``, ``pow`` built-ins. Every helper is implemented with
basic arithmetic operators (``+``, ``-``, ``*``, ``/``, ``%``) so the
rest of the package can satisfy the "from scratch" requirement of the
project specification.

The functions are intentionally written in a defensive style: each one
performs explicit type checks and raises informative errors for
non-numeric or out-of-domain inputs. The GUI (and any future caller)
can rely on these helpers to fail loudly rather than silently
propagating ``NaN`` or ``inf`` through a computation.
"""

from collections.abc import Iterable


# ---------------------------------------------------------------------------
# Absolute value
# ---------------------------------------------------------------------------

def _abs(value: float) -> float:
    """Return the absolute value of ``value`` without using ``abs``."""
    if value < 0:
        return -value
    return value


# ---------------------------------------------------------------------------
# Sum
# ---------------------------------------------------------------------------

def _sum(values: Iterable[float]) -> float:
    """Sum an iterable of numbers without using ``sum``.

    Parameters
    ----------
    values : Iterable[float]
        Any iterable of numeric values. Booleans are explicitly rejected
        because Python treats them as ``int`` and would otherwise slip
        through.

    Returns
    -------
    float
        The cumulative sum. Returns ``0`` for an empty iterable (matches
        the behaviour of the built-in ``sum``).

    Raises
    ------
    TypeError
        If an element is not an ``int`` or ``float`` (booleans included).
    """
    total = 0
    for item in values:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise TypeError(
                "_sum expected a numeric value, got "
                f"{type(item).__name__}: {item!r}"
            )
        total = total + item
    return total


# ---------------------------------------------------------------------------
# Power
# ---------------------------------------------------------------------------

def _power(base: float, exponent: int) -> float:
    """Return ``base ** exponent`` without using ``pow`` or ``**``.

    Uses exponentiation by squaring. Only non-negative integer
    exponents are supported; negative or non-integer exponents are
    rejected because the rest of the package only needs squares.

    Parameters
    ----------
    base : float
        The base. May be negative.
    exponent : int
        A non-negative integer exponent.

    Returns
    -------
    float
        ``base ** exponent``.

    Raises
    ------
    TypeError
        If ``exponent`` is not an ``int`` (booleans excluded).
    ValueError
        If ``exponent`` is negative.
    """
    if isinstance(exponent, bool) or not isinstance(exponent, int):
        raise TypeError(
            "_power exponent must be int, got "
            f"{type(exponent).__name__}: {exponent!r}"
        )
    if exponent < 0:
        raise ValueError(
            "_power does not support negative exponents, got "
            f"{exponent}"
        )

    result = 1
    current_base = base
    current_exp = exponent
    while current_exp > 0:
        if current_exp % 2 == 1:
            result = result * current_base
        current_base = current_base * current_base
        current_exp = current_exp // 2
    return result


# ---------------------------------------------------------------------------
# Finite check
# ---------------------------------------------------------------------------

def _is_finite(value: float) -> bool:
    """Return ``True`` if ``value`` is a finite number (not NaN, not inf).

    Implemented without importing ``math``:
        * NaN is the only float that is not equal to itself.
        * Infinity is the only finite-algebra operation that overflows
          into a non-finite value when its magnitude is added to itself.
    """
    # NaN is the only float where ``value == value`` is False.
    # pylint: disable-next=comparison-with-itself
    if value != value:
        return False
    # Both positive and negative infinity fail ``value - value == 0``
    # because the subtraction overflows back to infinity / NaN.
    if value - value != 0:
        return False
    return True
