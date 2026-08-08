"""Tkinter GUI for the standard deviation calculator.

Run with::

    python gui.py

The interface follows the user-interface design principles documented in
``docs/uidp-mind-map.md``. It presents a familiar calculator workflow,
exposes the available actions, makes state changes visible, uses consistent
language, and gives users a one-step recovery path for replaced input.
"""

from __future__ import annotations

import re
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
# Style and interface constants
# ---------------------------------------------------------------------------

COLOR_TEXT = "#1f2933"
COLOR_MUTED = "#52606d"
COLOR_SUCCESS = "#176b35"
COLOR_ERROR = "#a61b1b"
COLOR_NEUTRAL = "#334155"
COLOR_ERROR_BACKGROUND = "#ffe2e2"

FONT_HEADING = ("TkDefaultFont", 18, "bold")
FONT_BODY = ("TkDefaultFont", 11)
FONT_INPUT = ("TkFixedFont", 11)
FONT_RESULT = ("TkDefaultFont", 22, "bold")
FONT_STATUS = ("TkDefaultFont", 10)

RESULT_PLACEHOLDER = "—"
RESULT_CAPTION_READY = "Your result will appear here."
STATUS_READY = (
    "Ready: enter numbers, choose a calculation, then select Calculate."
)
EXAMPLE_DATA = "2, 4, 4, 4, 5, 5, 7, 9"

MODE_POPULATION = "population"
MODE_SAMPLE = "sample"

TOKEN_PATTERN = re.compile(r"[^,\s]+")


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

# This Tkinter controller intentionally owns its widget and state attributes.
# pylint: disable-next=too-many-instance-attributes,too-few-public-methods
class StandardDeviationApp:
    """Top-level controller for the calculator window."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Standard Deviation Calculator")
        self.root.geometry("720x680")
        self.root.minsize(660, 640)

        self.mode_var = tk.StringVar(value=MODE_POPULATION)
        self.mode_help_var = tk.StringVar()
        self.result_var = tk.StringVar(value=RESULT_PLACEHOLDER)
        self.result_caption_var = tk.StringVar(
            value=RESULT_CAPTION_READY
        )
        self.input_summary_var = tk.StringVar(value="0 values detected")
        self.status_text = tk.StringVar(value=STATUS_READY)

        self.previous_input: str | None = None
        self._suspend_modified_event = False

        # These widgets are constructed by the section builders below.
        self.text_input: tk.Text
        self.clear_button: ttk.Button
        self.undo_button: ttk.Button
        self.mode_help_label: ttk.Label
        self.calculate_button: ttk.Button
        self.result_display: ttk.Label
        self.status_label: ttk.Label

        self._configure_styles()
        self._build_widgets()
        self._bind_shortcuts()
        self._update_mode_help()
        self.root.after_idle(self.text_input.focus_set)

    # --- widget construction ----------------------------------------------

    def _configure_styles(self) -> None:
        """Configure a small, consistent visual vocabulary."""
        style = ttk.Style(self.root)
        style.configure("Body.TLabel", font=FONT_BODY)
        style.configure(
            "Muted.TLabel",
            font=FONT_STATUS,
            foreground=COLOR_MUTED,
        )
        style.configure(
            "Result.TLabel",
            font=FONT_RESULT,
            foreground=COLOR_TEXT,
        )
        style.configure(
            "Neutral.Status.TLabel",
            font=FONT_STATUS,
            foreground=COLOR_NEUTRAL,
        )
        style.configure(
            "Success.Status.TLabel",
            font=FONT_STATUS,
            foreground=COLOR_SUCCESS,
        )
        style.configure(
            "Error.Status.TLabel",
            font=FONT_STATUS,
            foreground=COLOR_ERROR,
        )
        style.configure("Primary.TButton", font=("TkDefaultFont", 11, "bold"))

    def _build_widgets(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        outer = ttk.Frame(self.root, padding=16)
        outer.grid(row=0, column=0, sticky="nsew")
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(2, weight=1)

        heading = ttk.Label(
            outer,
            text="Standard Deviation Calculator",
            font=FONT_HEADING,
            foreground=COLOR_TEXT,
        )
        heading.grid(row=0, column=0, sticky=tk.W)

        subheading = ttk.Label(
            outer,
            text=(
                "Enter a numeric dataset and calculate its population or "
                "sample standard deviation."
            ),
            style="Body.TLabel",
            foreground=COLOR_MUTED,
        )
        subheading.grid(row=1, column=0, sticky=tk.W, pady=(2, 12))

        self._build_input_section(outer)
        self._build_mode_section(outer)
        self._build_calculate_row(outer)
        self._build_result_section(outer)

        self.root.bind("<Configure>", self._on_window_resize)

    def _build_input_section(self, parent: ttk.Frame) -> None:
        input_section = ttk.LabelFrame(
            parent,
            text="1. Enter your data",
            padding=10,
        )
        input_section.grid(
            row=2,
            column=0,
            sticky="nsew",
            pady=(0, 10),
        )
        input_section.columnconfigure(0, weight=1)
        input_section.rowconfigure(1, weight=1)

        input_header = ttk.Frame(input_section)
        input_header.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        input_header.columnconfigure(0, weight=1)

        input_label = ttk.Label(
            input_header,
            text="Numbers separated by commas, spaces, or new lines",
            style="Body.TLabel",
        )
        input_label.grid(row=0, column=0, sticky=tk.W)

        input_summary = ttk.Label(
            input_header,
            textvariable=self.input_summary_var,
            style="Muted.TLabel",
        )
        input_summary.grid(row=0, column=1, sticky=tk.E, padx=(12, 0))

        text_frame = ttk.Frame(input_section)
        text_frame.grid(row=1, column=0, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.text_input = tk.Text(
            text_frame,
            height=7,
            font=FONT_INPUT,
            wrap=tk.WORD,
            undo=True,
            borderwidth=1,
            relief=tk.SOLID,
            padx=7,
            pady=7,
        )
        self.text_input.grid(row=0, column=0, sticky="nsew")
        self.text_input.tag_configure(
            "invalid_value",
            background=COLOR_ERROR_BACKGROUND,
            foreground=COLOR_ERROR,
        )
        self.text_input.bind("<<Modified>>", self._on_input_modified)

        scrollbar = ttk.Scrollbar(
            text_frame,
            orient=tk.VERTICAL,
            command=self.text_input.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text_input.configure(yscrollcommand=scrollbar.set)

        hint = ttk.Label(
            input_section,
            text=(
                "Example decimal formats: 3.5, -2, 1e3. "
                "NaN and infinity are not accepted."
            ),
            style="Muted.TLabel",
        )
        hint.grid(row=2, column=0, sticky=tk.W, pady=(5, 7))

        input_actions = ttk.Frame(input_section)
        input_actions.grid(row=3, column=0, sticky="ew")

        ttk.Button(
            input_actions,
            text="Try example",
            command=self._on_try_example,
        ).pack(side=tk.LEFT, padx=(0, 7))

        self.clear_button = ttk.Button(
            input_actions,
            text="Clear data",
            command=self._on_clear,
        )
        self.clear_button.pack(side=tk.LEFT, padx=(0, 7))

        self.undo_button = ttk.Button(
            input_actions,
            text="Undo change",
            command=self._on_undo_change,
        )
        self.undo_button.pack(side=tk.LEFT, padx=(0, 7))
        self.undo_button.state(["disabled"])

        ttk.Button(
            input_actions,
            text="How to use",
            command=self._show_help,
        ).pack(side=tk.RIGHT)

    def _build_mode_section(self, parent: ttk.Frame) -> None:
        mode_section = ttk.LabelFrame(
            parent,
            text="2. Choose the calculation",
            padding=10,
        )
        mode_section.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(0, 10),
        )
        mode_section.columnconfigure(0, weight=1)

        ttk.Radiobutton(
            mode_section,
            text="Population - the data contains the whole group",
            value=MODE_POPULATION,
            variable=self.mode_var,
            command=self._on_mode_change,
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 3))

        ttk.Radiobutton(
            mode_section,
            text="Sample - the data represents part of a larger group",
            value=MODE_SAMPLE,
            variable=self.mode_var,
            command=self._on_mode_change,
        ).grid(row=1, column=0, sticky=tk.W, pady=(0, 5))

        self.mode_help_label = ttk.Label(
            mode_section,
            textvariable=self.mode_help_var,
            style="Muted.TLabel",
        )
        self.mode_help_label.grid(row=2, column=0, sticky="ew")

    def _build_calculate_row(self, parent: ttk.Frame) -> None:
        calculate_row = ttk.Frame(parent)
        calculate_row.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        calculate_row.columnconfigure(0, weight=1)

        self.calculate_button = ttk.Button(
            calculate_row,
            text="Calculate standard deviation",
            command=self._on_calculate,
            style="Primary.TButton",
        )
        self.calculate_button.grid(row=0, column=0, sticky="ew")

        shortcut = ttk.Label(
            calculate_row,
            text="Shortcut: Ctrl+Enter or Cmd+Enter",
            style="Muted.TLabel",
        )
        shortcut.grid(row=1, column=0, pady=(3, 0))

    def _build_result_section(self, parent: ttk.Frame) -> None:
        result_section = ttk.LabelFrame(
            parent,
            text="3. Review the result",
            padding=10,
        )
        result_section.grid(row=5, column=0, sticky="ew")
        result_section.columnconfigure(0, weight=1)

        self.result_display = ttk.Label(
            result_section,
            textvariable=self.result_var,
            style="Result.TLabel",
        )
        self.result_display.grid(row=0, column=0, sticky=tk.W)

        result_caption = ttk.Label(
            result_section,
            textvariable=self.result_caption_var,
            style="Muted.TLabel",
        )
        result_caption.grid(row=1, column=0, sticky=tk.W, pady=(0, 7))

        ttk.Separator(result_section).grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(0, 7),
        )

        self.status_label = ttk.Label(
            result_section,
            textvariable=self.status_text,
            style="Neutral.Status.TLabel",
            wraplength=640,
            justify=tk.LEFT,
        )
        self.status_label.grid(row=3, column=0, sticky="ew")

    # --- keyboard and responsive behavior ---------------------------------

    def _bind_shortcuts(self) -> None:
        self.root.bind_all(
            "<Control-Return>",
            lambda _event: self._on_calculate(),
        )
        self.root.bind_all(
            "<Command-Return>",
            lambda _event: self._on_calculate(),
        )
        self.root.bind_all("<Control-l>", lambda _event: self._on_clear())
        self.root.bind_all("<Command-l>", lambda _event: self._on_clear())
        self.root.bind_all("<F1>", lambda _event: self._show_help())

    def _on_window_resize(self, event: tk.Event) -> None:
        if event.widget is not self.root:
            return
        wrap_length = max(360, event.width - 80)
        self.status_label.configure(wraplength=wrap_length)
        self.mode_help_label.configure(wraplength=wrap_length)

    # --- visible state helpers --------------------------------------------

    def _set_status(self, message: str, kind: str = "neutral") -> None:
        self.status_text.set(message)
        style_names = {
            "neutral": "Neutral.Status.TLabel",
            "success": "Success.Status.TLabel",
            "error": "Error.Status.TLabel",
        }
        self.status_label.configure(
            style=style_names.get(kind, "Neutral.Status.TLabel")
        )

    def _reset_result(self) -> None:
        self.result_var.set(RESULT_PLACEHOLDER)
        self.result_caption_var.set(RESULT_CAPTION_READY)

    def _clear_error_highlight(self) -> None:
        self.text_input.tag_remove("invalid_value", "1.0", tk.END)

    def _highlight_token(self, position: int) -> None:
        raw_text = self.text_input.get("1.0", "end-1c")
        matches = list(TOKEN_PATTERN.finditer(raw_text))
        if position < 1 or position > len(matches):
            return

        match = matches[position - 1]
        start = f"1.0+{match.start()}c"
        end = f"1.0+{match.end()}c"
        self.text_input.tag_add("invalid_value", start, end)
        self.text_input.see(start)
        self.text_input.focus_set()

    def _refresh_input_summary(self) -> None:
        raw_text = self.text_input.get("1.0", "end-1c")
        count = len(TOKEN_PATTERN.findall(raw_text))
        noun = "value" if count == 1 else "values"
        self.input_summary_var.set(f"{count} {noun} detected")

    def _on_input_modified(self, _event: tk.Event | None = None) -> None:
        if not self.text_input.edit_modified():
            return
        self.text_input.edit_modified(False)
        if self._suspend_modified_event:
            return

        self._clear_error_highlight()
        self._refresh_input_summary()
        if self.result_var.get() != RESULT_PLACEHOLDER:
            self._reset_result()
            self._set_status(
                "Data changed: calculate again to update the result."
            )

    def _replace_input(self, text: str) -> None:
        self._suspend_modified_event = True
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert("1.0", text)
        self.text_input.edit_modified(False)
        self._suspend_modified_event = False
        self._clear_error_highlight()
        self._refresh_input_summary()

    def _remember_current_input(self) -> None:
        self.previous_input = self.text_input.get("1.0", "end-1c")
        self.undo_button.state(["!disabled"])

    def _update_mode_help(self) -> None:
        if self.mode_var.get() == MODE_SAMPLE:
            self.mode_help_var.set(
                "Sample standard deviation uses n - 1 in the denominator "
                "and needs at least two values."
            )
        else:
            self.mode_help_var.set(
                "Population standard deviation uses n in the denominator "
                "and needs at least one value."
            )

    # --- actions -----------------------------------------------------------

    def _on_mode_change(self) -> None:
        self._update_mode_help()
        if self.result_var.get() != RESULT_PLACEHOLDER:
            self._reset_result()
        mode_label = (
            "Sample"
            if self.mode_var.get() == MODE_SAMPLE
            else "Population"
        )
        self._set_status(
            f"{mode_label} selected: calculate to update the result."
        )

    def _on_try_example(self) -> None:
        current = self.text_input.get("1.0", "end-1c")
        if current == EXAMPLE_DATA and self.mode_var.get() == MODE_POPULATION:
            self._set_status(
                "The population example is already loaded."
            )
            self.text_input.focus_set()
            return
        if current.strip() and current.strip() != EXAMPLE_DATA:
            should_replace = messagebox.askyesno(
                "Replace current data?",
                "Loading the example will replace the current data. "
                "You can undo this change afterward. Continue?",
                parent=self.root,
            )
            if not should_replace:
                self._set_status("Example not loaded: current data kept.")
                return

        if current != EXAMPLE_DATA:
            self._remember_current_input()
        self._replace_input(EXAMPLE_DATA)
        self.mode_var.set(MODE_POPULATION)
        self._update_mode_help()
        self._reset_result()
        self._set_status(
            "Example loaded: select Calculate to see the population "
            "standard deviation."
        )
        self.text_input.focus_set()

    def _on_clear(self) -> None:
        current = self.text_input.get("1.0", "end-1c")
        if not current:
            self._set_status("Nothing to clear: the data field is empty.")
            self.text_input.focus_set()
            return

        self._remember_current_input()
        self._replace_input("")
        self._reset_result()
        self._set_status(
            "Data cleared: select Undo change to restore it."
        )
        self.text_input.focus_set()

    def _on_undo_change(self) -> None:
        if self.previous_input is None:
            self._set_status("Nothing to undo.")
            return

        text_to_restore = self.previous_input
        self.previous_input = None
        self.undo_button.state(["disabled"])
        self._replace_input(text_to_restore)
        self._reset_result()
        self._set_status(
            "Previous data restored: calculate to produce a new result."
        )
        self.text_input.focus_set()

    def _show_help(self) -> None:
        messagebox.showinfo(
            "How to use the calculator",
            "1. Enter finite numbers separated by commas, spaces, or "
            "new lines.\n\n"
            "2. Choose Population when the data is the whole group, or "
            "Sample when it is part of a larger group.\n\n"
            "3. Select Calculate standard deviation. Invalid values are "
            "highlighted so you can correct them.\n\n"
            "Keyboard shortcuts:\n"
            "Ctrl+Enter or Cmd+Enter - calculate\n"
            "Ctrl+L or Cmd+L - clear data\n"
            "F1 - show this help",
            parent=self.root,
        )

    # Mapping each error to a distinct message intentionally makes this
    # boundary handler branch-and-return heavy.
    # pylint: disable=too-many-return-statements
    # pylint: disable=too-many-branches,too-many-statements
    def _on_calculate(self) -> None:
        self._reset_result()
        self._clear_error_highlight()

        raw_text = self.text_input.get("1.0", "end-1c")
        mode = self.mode_var.get()
        if mode == MODE_POPULATION:
            is_population = True
        elif mode == MODE_SAMPLE:
            is_population = False
        else:
            self._set_status(
                "Internal error: the calculation type is unknown. "
                "Please restart the application.",
                "error",
            )
            return

        try:
            values = parse_numbers(raw_text)
            result = calculate_std_dev_welford(
                values,
                is_population=is_population,
            )

        except EmptyInputError:
            self._set_status(
                "Input error: enter at least one number before "
                "calculating.",
                "error",
            )
            self.text_input.focus_set()
            return

        except InvalidNumberError as exc:
            self._highlight_token(exc.position)
            self._set_status(
                f"Input error: {exc}. Correct the highlighted value and "
                "calculate again.",
                "error",
            )
            return

        except InsufficientDataError as exc:
            count = getattr(exc, "count", 0)
            self._set_status(
                "Input error: sample standard deviation needs at least "
                f"two values; {count} provided. Add another value or "
                "choose Population.",
                "error",
            )
            return

        except NumericOverflowError:
            self._set_status(
                "Calculation error: the values are too large to process. "
                "Use smaller finite numbers.",
                "error",
            )
            return

        except NegativeVarianceError:
            self._set_status(
                "Calculation error: numerical precision produced an "
                "invalid variance. Check the input values.",
                "error",
            )
            return

        except ConvergenceError:
            self._set_status(
                "Calculation error: the square-root calculation did not "
                "converge. Try values with a smaller range.",
                "error",
            )
            return

        except InvalidModeError:
            self._set_status(
                "Internal error: the calculation type is invalid. "
                "Please restart the application.",
                "error",
            )
            return

        except (TypeError, ValueError):
            self._set_status(
                "Input error: every item must be a finite number. "
                "Check the data and calculate again.",
                "error",
            )
            return

        except ZeroDivisionError:
            self._set_status(
                "Calculation error: there are too few values for the "
                "selected calculation type.",
                "error",
            )
            return

        except OverflowError:
            self._set_status(
                "Calculation error: the values exceeded the supported "
                "numeric range. Use smaller values.",
                "error",
            )
            return

        except StandardDeviationError as exc:
            self._set_status(
                "Calculation error: "
                f"{type(exc).__name__}. Check the input and try again.",
                "error",
            )
            return

        # This is the application's last-resort GUI boundary. Domain errors
        # are handled specifically above.
        # pylint: disable-next=broad-exception-caught
        except Exception as exc:
            messagebox.showerror(
                "Unexpected error",
                "An unexpected error occurred. Your data has not been "
                "changed.\n\n"
                f"{type(exc).__name__}: {exc}",
                parent=self.root,
            )
            self._set_status(
                "Internal error: the calculation could not be completed. "
                "Your data is unchanged.",
                "error",
            )
            return

        formatted_result = f"{result:.10g}"
        mode_label = "Population" if is_population else "Sample"
        noun = "value" if len(values) == 1 else "values"
        self.result_var.set(formatted_result)
        self.result_caption_var.set(
            f"{mode_label} standard deviation · {len(values)} {noun}"
        )
        self._set_status(
            f"Success: calculated the {mode_label.lower()} standard "
            "deviation.",
            "success",
        )


def main() -> None:
    """Construct the Tk root window and start the event loop."""
    root = tk.Tk()
    StandardDeviationApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
