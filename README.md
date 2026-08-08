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
python -m flake8 gui.py standard_deviation
```

Flake8 combines PyFlakes error detection, PEP 8 checks through pycodestyle,
and McCabe complexity checks. It is installed with the other project
dependencies from `requirements.txt`. An empty result followed by exit code
`0` means that no violations were found.

## Static analysis with Pylint

Pylint 3.3.7 is pinned in `requirements.txt` for compatibility with Python
3.12. Run static analysis against all project Python sources with:

```bash
python -m pylint gui.py standard_deviation
```

The command reports diagnostics and a score. Exit code `0` and a score of
`10.00/10` indicate that the configured analysis passed without findings.
The following snapshot records an actual full-project Pylint run:

![Successful Pylint static analysis](docs/pylint-static-analysis.png)

## Debugging with pdb

The calculation can be inspected with Python's built-in debugger. Start a
population-standard-deviation calculation under `pdb` from the project root:

```bash
python -c 'import pdb; from standard_deviation.algorithm import calculate_std_dev_welford; result = pdb.Pdb().runcall(calculate_std_dev_welford, [2, 4, 4, 4, 5, 5, 7, 9], True); print(f"Result: {result}")'
```

At the `(Pdb)` prompt, these commands stop on the fourth loop iteration,
inspect Welford's intermediate state, and finish the calculation:

```text
break 88
ignore 1 3
continue
p data
p index, item
p count, mean, squared_deviation_sum
where
clear 1
continue
```

The following snapshot records an actual debugger session run against
`standard_deviation/algorithm.py`:

![pdb session inspecting Welford's algorithm](docs/pdb-debugger-snapshot.png)

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
- `F1` — Show usage help

## User interface design principles

The GUI applies all seven principles from the course's *User Interface Design
Principles* notes. The applicability decision, mind map, design rationale, and
implementation traceability are documented in
[docs/uidp-mind-map.md](docs/uidp-mind-map.md).

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
├── requirements.txt          # Project dependencies and quality tooling
├── setup.cfg                 # PEP 8 checker configuration
└── .gitignore
```
