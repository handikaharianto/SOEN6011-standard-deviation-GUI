# SOEN 6011 – Standard Deviation

A Python implementation of Standard Deviation (σ) with a Tkinter
Graphical User Interface. The computation uses Welford's online
algorithm with a Babylonian-method for square root approximation.

## First-time setup

```bash
# Create the virtual environment (already done)
python3.12 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# When you're done, deactivate
deactivate
```

## Code style

Python source code follows [PEP 8](https://peps.python.org/pep-0008/).
Check all source files from the project root with:

```bash
python -m pycodestyle gui.py standard_deviation
```

## Releases and versioning

Releases follow [Semantic Versioning](https://semver.org/) and are
created automatically from Conventional Commit messages when commits are
pushed to `main`:

- `fix: ...` creates a patch release.
- `feat: ...` creates a minor release.
- `feat!: ...` or a `BREAKING CHANGE:` footer creates a major release.
- `docs:`, `style:`, `test:`, and `chore:` commits do not create a release.

Python Semantic Release updates `standard_deviation/_version.py`, creates
an annotated Git tag, and publishes the corresponding GitHub Release. The
current version is available in Python as `standard_deviation.__version__`.

## Adding a new library

```bash
source venv/bin/activate
pip install <package-name>
pip freeze > requirements.txt   # save it for others
deactivate
```

## Requirements

- Python 3.12
- Tkinter

## Usage

Run the GUI from the project root:

```bash
source venv/bin/activate
python gui.py
```

The calculator window accepts a list of numeric values in any
combination of commas, spaces, tabs, and new lines. Choose between
**Population** (divide by `n`) and **Sample** (divide by `n - 1`)
standard deviation, then click **Calculate**.

Keyboard shortcuts:

- `Ctrl+Enter` / `Cmd+Enter` — Calculate
- `Ctrl+L` / `Cmd+L` — Clear

## Project structure

```
.
├── gui.py                    # Tkinter entry point (run this)
├── standard_deviation/       # Computational package
│   ├── __init__.py           # Public API re-exports
│   ├── exceptions.py         # Custom exception hierarchy
│   ├── builtin_helpers.py    # _abs, _sum, _power, _is_finite
│   ├── sqrt.py               # Babylonian calculate_sqrt
│   ├── algorithm.py          # Welford's calculate_std_dev_welford
│   └── parser.py             # parse_numbers (string → list[float])
├── README.md
├── requirements.txt          # Project dependencies and style tooling
├── setup.cfg                 # PEP 8 checker configuration
└── .gitignore
```
