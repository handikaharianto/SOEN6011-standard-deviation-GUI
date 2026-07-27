"""Tkinter GUI for the standard deviation calculator.

Run with:

    python gui.py

The application collects numeric input from a multi-line text widget,
parses it through :func:`standard_deviation.parser.parse_numbers`, and
computes either population or sample standard deviation via
:func:`standard_deviation.algorithm.calculate_std_dev_welford`. All
errors are caught at the GUI boundary and rendered in a dedicated
status label with descriptive, actionable text — no raw stack traces
are ever shown to the user.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from standard_deviation import (
    ConvergenceError,
    EmptyInputError,
    InsufficientDataError,
    InvalidModeError,
    InvalidNumberError,
    NegativeVarianceError,
    NumericOverflowError,
    StandardDeviationError,
    calculate_std_dev_welford,
    parse_numbers,
)


# ---------------------------------------------------------------------------
# Style constants
# ---------------------------------------------------------------------------

COLOR_TEXT = "#1f2933"
COLOR_MUTED = "#52606d"
COLOR_SUCCESS = "#1f7a3a"
COLOR_ERROR = "#b21f1f"
COLOR_NEUTRAL = "#334155"

FONT_HEADING = ("TkDefaultFont", 16, "bold")
FONT_BODY = ("TkDefaultFont", 11)
FONT_INPUT = ("TkFixedFont", 11)
FONT_RESULT = ("TkDefaultFont", 18, "bold")
FONT_STATUS = ("TkDefaultFont", 10)

RESULT_PLACEHOLDER = "—"
STATUS_READY = "Ready. Enter numbers above and click Calculate."

# Value used by the radio buttons. Strings, not bools, because
# tk.StringVar requires strings.
MODE_POPULATION = "population"
MODE_SAMPLE = "sample"


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

class StandardDeviationApp:
    """Top-level controller for the calculator window."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Standard Deviation Calculator")
        self.root.geometry("640x520")
        self.root.minsize(520, 420)
        self.root.configure(padx=16, pady=16)

        # Tk variables
        self.mode_var = tk.StringVar(value=MODE_POPULATION)
        self.result_var = tk.StringVar(value=RESULT_PLACEHOLDER)
        self.status_text = tk.StringVar(value=STATUS_READY)

        self._build_widgets()
        self._bind_shortcuts()

    # --- widget construction ------------------------------------------------

    def _build_widgets(self) -> None:
        outer = ttk.Frame(self.root)
        outer.pack(fill=tk.BOTH, expand=True)

        # Heading
        heading = ttk.Label(
            outer,
            text="Standard Deviation Calculator",
            font=FONT_HEADING,
            foreground=COLOR_TEXT,
        )
        heading.pack(anchor=tk.W)

        subheading = ttk.Label(
            outer,
            text="Compute σ from a numeric dataset. Population or sample.",
            font=FONT_BODY,
            foreground=COLOR_MUTED,
        )
        subheading.pack(anchor=tk.W, pady=(2, 12))

        # Input section
        input_label = ttk.Label(
            outer,
            text="Data (comma, space, or newline separated):",
            font=FONT_BODY,
        )
        input_label.pack(anchor=tk.W, pady=(0, 4))

        text_frame = ttk.Frame(outer)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.text_input = tk.Text(
            text_frame,
            height=7,
            font=FONT_INPUT,
            wrap=tk.NONE,
            undo=True,
            borderwidth=1,
            relief=tk.SOLID,
        )
        scrollbar = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=self.text_input.yview
        )
        self.text_input.configure(yscrollcommand=scrollbar.set)
        self.text_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        hint = ttk.Label(
            outer,
            text="Tip: separate values with commas, spaces, or new lines. "
            "Use '.' for decimals.",
            font=FONT_STATUS,
            foreground=COLOR_MUTED,
        )
        hint.pack(anchor=tk.W, pady=(4, 8))

        # Mode section
        mode_frame = ttk.Frame(outer)
        mode_frame.pack(anchor=tk.W, pady=(0, 8))

        mode_label = ttk.Label(mode_frame, text="Mode:", font=FONT_BODY)
        mode_label.pack(side=tk.LEFT, padx=(0, 8))

        population_radio = ttk.Radiobutton(
            mode_frame,
            text="Population  (σ = √( Σ(xᵢ − μ)² / n ))",
            value=MODE_POPULATION,
            variable=self.mode_var,
        )
        population_radio.pack(side=tk.LEFT, padx=(0, 16))

        sample_radio = ttk.Radiobutton(
            mode_frame,
            text="Sample  (s = √( Σ(xᵢ − x̄)² / (n − 1) ))",
            value=MODE_SAMPLE,
            variable=self.mode_var,
        )
        sample_radio.pack(side=tk.LEFT)

        # Buttons row
        button_frame = ttk.Frame(outer)
        button_frame.pack(fill=tk.X, pady=(0, 8))

        self.calculate_button = ttk.Button(
            button_frame,
            text="Calculate",
            command=self._on_calculate,
        )
        self.calculate_button.pack(side=tk.LEFT, padx=(0, 8))

        self.clear_button = ttk.Button(
            button_frame,
            text="Clear",
            command=self._on_clear,
        )
        self.clear_button.pack(side=tk.LEFT)

        # Result section
        result_label = ttk.Label(
            outer, text="Standard Deviation:", font=FONT_BODY
        )
        result_label.pack(anchor=tk.W, pady=(8, 2))

        self.result_display = ttk.Label(
            outer,
            textvariable=self.result_var,
            font=FONT_RESULT,
            foreground=COLOR_TEXT,
        )
        self.result_display.pack(anchor=tk.W, pady=(0, 8))

        # Status section
        status_separator = ttk.Separator(outer)
        status_separator.pack(fill=tk.X, pady=(4, 4))

        self.status_label = ttk.Label(
            outer,
            textvariable=self.status_text,
            font=FONT_STATUS,
            foreground=COLOR_NEUTRAL,
            wraplength=580,
            justify=tk.LEFT,
        )
        self.status_label.pack(anchor=tk.W, fill=tk.X)

    # --- keyboard shortcuts -------------------------------------------------

    def _bind_shortcuts(self) -> None:
        # Ctrl+Return / Cmd+Return triggers Calculate from anywhere.
        self.root.bind_all("<Control-Return>", lambda _e: self._on_calculate())
        self.root.bind_all("<Command-Return>", lambda _e: self._on_calculate())
        # Ctrl+L / Cmd+L clears
        self.root.bind_all("<Control-l>", lambda _e: self._on_clear())
        self.root.bind_all("<Command-l>", lambda _e: self._on_clear())

    # --- status helpers -----------------------------------------------------

    def _set_status(self, message: str, color: str = COLOR_NEUTRAL) -> None:
        self.status_text.set(message)
        self.status_label.configure(foreground=color)

    def _set_result(self, text: str) -> None:
        self.result_var.set(text)

    # --- event handlers -----------------------------------------------------

    def _on_calculate(self) -> None:
        # Wipe the previous result so an old value can never be confused
        # with a new one.
        self._set_result(RESULT_PLACEHOLDER)

        raw_text = self.text_input.get("1.0", tk.END)
        # Text widget adds a trailing newline; strip it so the parser
        # doesn't interpret an empty trailing token.
        if raw_text.endswith("\n"):
            raw_text = raw_text[:-1]

        mode = self.mode_var.get()
        if mode == MODE_POPULATION:
            is_population = True
        elif mode == MODE_SAMPLE:
            is_population = False
        else:
            # Defensive — should never happen because the radio buttons
            # only emit known values.
            self._set_status(
                f"Internal error: unknown mode '{mode}'. Please restart the application.",
                COLOR_ERROR,
            )
            return

        try:
            values = parse_numbers(raw_text)
            result = calculate_std_dev_welford(values, is_population=is_population)

        except EmptyInputError as exc:
            self._set_status(
                f"Please enter at least one numeric value before calculating. "
                f"({exc})",
                COLOR_ERROR,
            )
            return

        except InvalidNumberError as exc:
            if exc.position > 0:
                self._set_status(
                    f"Invalid number at position {exc.position}: {exc}. "
                    f"Please check the highlighted token.",
                    COLOR_ERROR,
                )
            else:
                self._set_status(
                    f"Invalid input: {exc}. Please check your data.",
                    COLOR_ERROR,
                )
            return

        except InsufficientDataError as exc:
            count = getattr(exc, "count", 0)
            self._set_status(
                f"{exc} (currently {count} value"
                f"{'s' if count != 1 else ''}). "
                f"{'Need at least 2 numbers for sample standard deviation, or 1 for population.' if mode == MODE_SAMPLE else 'Need at least 1 number.'}",
                COLOR_ERROR,
            )
            return

        except NumericOverflowError as exc:
            self._set_status(
                f"Numbers grew too large during computation. "
                f"Use smaller values. ({exc})",
                COLOR_ERROR,
            )
            return

        except NegativeVarianceError as exc:
            self._set_status(
                f"Internal error: negative variance computed. "
                f"Please verify your input. ({exc})",
                COLOR_ERROR,
            )
            return

        except ConvergenceError as exc:
            self._set_status(
                f"Square root did not converge. Please retry with simpler values. "
                f"({exc})",
                COLOR_ERROR,
            )
            return

        except InvalidModeError as exc:
            self._set_status(
                f"Internal error: invalid mode flag. ({exc})",
                COLOR_ERROR,
            )
            return

        except TypeError as exc:
            self._set_status(
                f"Unexpected type error: {type(exc).__name__}: {exc}. "
                f"Please verify that all values are numeric.",
                COLOR_ERROR,
            )
            return

        except ValueError as exc:
            self._set_status(
                f"Unexpected value error: {type(exc).__name__}: {exc}.",
                COLOR_ERROR,
            )
            return

        except ZeroDivisionError as exc:
            self._set_status(
                f"Cannot divide by zero while computing standard deviation. "
                f"Please verify your input. ({exc})",
                COLOR_ERROR,
            )
            return

        except OverflowError as exc:
            self._set_status(
                f"Numerical overflow while computing standard deviation. "
                f"Please use smaller values. ({exc})",
                COLOR_ERROR,
            )
            return

        except StandardDeviationError as exc:
            # Catch-all for any future domain error that may not have
            # a dedicated clause above.
            self._set_status(
                f"Unexpected standard-deviation error: {type(exc).__name__}: {exc}.",
                COLOR_ERROR,
            )
            return

        except Exception as exc:  # last resort
            # Show a modal for genuinely unexpected failures so the user
            # knows the program hit something the developer didn't
            # anticipate. The status label is also updated.
            messagebox.showerror(
                "Unexpected error",
                f"An unexpected error occurred:\n\n{type(exc).__name__}: {exc}",
            )
            self._set_status(
                f"Internal error: {type(exc).__name__}: {exc}.",
                COLOR_ERROR,
            )
            return

        # Success path
        self._set_result(str(result))
        mode_label = "Population" if is_population else "Sample"
        self._set_status(
            f"✓ {mode_label} standard deviation calculated from {len(values)} "
            f"value{'s' if len(values) != 1 else ''}: σ = {result}",
            COLOR_SUCCESS,
        )

    def _on_clear(self) -> None:
        self.text_input.delete("1.0", tk.END)
        self._set_result(RESULT_PLACEHOLDER)
        self._set_status(STATUS_READY, COLOR_NEUTRAL)
        self.text_input.focus_set()


def main() -> None:
    """Construct the Tk root window and start the event loop."""
    root = tk.Tk()
    StandardDeviationApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
