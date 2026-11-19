# Personal Helper Bot

A command-line application for managing contacts with phone numbers and birthdays.

## Features

- Store and manage contacts
- Add, update, and delete phone numbers
- Track birthdays and get reminders
- Interactive help system
- Automatic data persistence
- Full test coverage

## Instructions

### Setup

```bash
# Enter the project directory
cd python-final-project

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Run the Application

```bash
# Activate virtual environment (if not already active)
source .venv/bin/activate

# Run the application
personal-helper-bot
```

The `personal-helper-bot` command is now available after installation.

**Alternative methods (if you skip the installation):**
```bash
# Run directly from src/
cd src
python3 main.py

# Or set PYTHONPATH and run from project root
PYTHONPATH=src python3 src/main.py
```

### Run Tests

```bash
# Run all tests
pytest tests/

# Run model tests (domain layer)
pytest tests/address_book/models/ -v

# Run command tests (application layer)
pytest tests/address_book/commands/ -v

# Run infrastructure tests
pytest tests/address_book/test_*.py -v

# Install coverage once (if not already installed)
python -m pip install coverage

# Run tests with branch coverage
python -m coverage run --branch --source=src -m pytest

# Show coverage summary and uncovered lines
python -m coverage report -m

# Optional: generate an HTML report in htmlcov/
python -m coverage html
```

### Available Commands

- `help` — Show all available commands
- `help <command>` — Show details for a specific command
- `hello` — Get a greeting from the bot
- `add <name> [phone]` — Add a new contact or add phone to existing (phone is optional)
- `change <name> <old_phone> <new_phone>` — Change phone number for a contact
- `phone <name>` — Show phone numbers for a contact
- `all` — Show all contacts in address book
- `add-birthday <name> <DD.MM.YYYY>` — Add a birthday for a contact
- `show-birthday <name>` — Show birthday for a contact
- `birthdays` — Show upcoming birthdays in the next 7 days
- `close` / `exit` — Quit the program

### Interactive Help

The application includes an interactive help system:

```bash
help              # List all available commands
help add          # Show details for the 'add' command
help add-birthday # Show details for the 'add-birthday' command
```

### Data storage

Contacts are saved in a pickle file when you quit the application:

| OS      | Location                                                      |
|---------|---------------------------------------------------------------|
| Windows | `%APPDATA%\personal-helper-bot\addressbook.pkl` |
| macOS   | `~/Library/Application Support/personal-helper-bot/addressbook.pkl` |
| Linux   | `$XDG_DATA_HOME/personal-helper-bot/addressbook.pkl` (default `~/.local/share/personal-helper-bot/addressbook.pkl`) |

Saving is atomic: the file is written to a temporary file first and then swapped in, so a crash can't corrupt existing data.

### Requirements

- Python 3.10+
- No external dependencies (testing requires pytest)

## Architecture & Design Patterns

This project uses a modular command-based architecture where each command is a separate class. Commands are automatically discovered and registered when the app starts.

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for how the app works and [`CONTRIBUTING.md`](CONTRIBUTING.md) for how to add new commands.
