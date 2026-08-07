"""Numeric input parser for the GUI layer.

The Text widget in the GUI returns a free-form string. This module
turns it into a clean ``list[float]`` while raising descriptive,
position-aware errors that the GUI can render to the user.
"""

import re

from standard_deviation.builtin_helpers import _is_finite
from standard_deviation.exceptions import EmptyInputError, InvalidNumberError


# Split on commas, tabs, newlines, and runs of whitespace. Parentheses
# capture each non-empty token so we can iterate over them in order.
_TOKEN_PATTERN = re.compile(r"[^,\s]+")


def parse_numbers(raw_text: str) -> list[float]:
    """Parse a free-form numeric string into a list of floats.

    Accepted delimiters: commas, tabs, newlines, and any amount of
    whitespace. Empty tokens are silently skipped. Each token is
    converted via :func:`float`; non-numeric tokens, ``NaN`` and
    ``infinity`` literals, and ``bool`` values are rejected with an
    :class:`InvalidNumberError` that carries the offending position.

    Parameters
    ----------
    raw_text : str
        The raw text from the GUI Text widget.

    Returns
    -------
    list[float]
        The parsed numbers, in the order they appeared.

    Raises
    ------
    EmptyInputError
        If the input contains no tokens at all (only whitespace,
        commas, or an empty string).
    InvalidNumberError
        If a token cannot be parsed as a finite number. The
        ``position`` attribute is the 1-based index of the token.
    """
    if raw_text is None:
        raise EmptyInputError(
            "No numbers detected. Enter at least one numeric value."
        )

    tokens = _TOKEN_PATTERN.findall(raw_text)

    if not tokens:
        raise EmptyInputError(
            "No numbers detected. Enter at least one numeric value."
        )

    values: list[float] = []
    for index, token in enumerate(tokens, start=1):
        # Reject boolean literals explicitly. ``float("True")`` would
        # raise ``ValueError`` anyway, but the user-facing message is
        # friendlier if we catch it ourselves.
        if token in ("True", "False", "true", "false"):
            raise InvalidNumberError(
                f"Invalid number '{token}' at position {index}: "
                f"boolean values are not accepted",
                position=index,
            )

        try:
            value = float(token)
        except ValueError:
            raise InvalidNumberError(
                f"Invalid number '{token}' at position {index}: "
                f"not a valid numeric literal",
                position=index,
            ) from None

        if not _is_finite(value):
            raise InvalidNumberError(
                f"Number must be finite at position {index}: got {token!r}",
                position=index,
            )

        values.append(value)

    return values
