# SOEN 6011 – Standard Deviation

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

## Adding a new library

```bash
source venv/bin/activate
pip install <package-name>
pip freeze > requirements.txt   # save it for others
deactivate
```

## Requirements

- Python 3.12
- See `requirements.txt` for third-party dependencies.
