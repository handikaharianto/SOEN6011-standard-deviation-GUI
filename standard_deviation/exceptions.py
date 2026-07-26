"""Custom exception hierarchy for the standard deviation calculator.

Every domain error raised by this package inherits from
:class:`StandardDeviationError`, so the GUI layer can catch the whole
hierarchy with a single ``except`` clause while still being able to
distinguish individual error types for descriptive messages.

The hierarchy is intentionally flat-ish: each subclass maps to a
single, well-defined error condition that the GUI translates into a
user-friendly message.
"""


class StandardDeviationError(Exception):
    """Base class for all domain errors raised by this package.

    Catching this class is sufficient for "anything that went wrong
    related to standard-deviation computation". Use a more specific
    subclass if you need to react differently to a particular failure.
    """


class InvalidNumberError(StandardDeviationError):
    """A token in the input could not be parsed as a finite number.

    Parameters
    ----------
    message : str
        Human-readable explanation of the failure.
    position : int, optional
        1-based index of the offending token in the input. ``0`` means
        the error is not localised to a single token (e.g. mixed
        types in ``data``).
    """

    def __init__(self, message: str, position: int = 0) -> None:
        super().__init__(message)
        self.position = position


class EmptyInputError(StandardDeviationError):
    """The input contained no numeric tokens at all."""


class InsufficientDataError(StandardDeviationError):
    """The dataset has too few points for the requested mode.

    Raised when the list is empty (zero points) or when operating in
    sample mode with exactly one data point (division by zero).
    """

    def __init__(self, message: str, count: int = 0) -> None:
        super().__init__(message)
        self.count = count


class NumericOverflowError(StandardDeviationError):
    """An intermediate value crossed the float overflow threshold."""


class NegativeVarianceError(StandardDeviationError):
    """``calculate_sqrt`` received a negative argument.

    For a correctly-formed dataset this should never happen, but the
    algorithm and the GUI both guard against it so the user is never
    shown a NaN.
    """


class ConvergenceError(StandardDeviationError):
    """An iterative routine (e.g. Babylonian square root) failed to
    converge within the safety iteration limit."""


class InvalidModeError(StandardDeviationError):
    """The ``is_population`` flag was not a boolean."""
