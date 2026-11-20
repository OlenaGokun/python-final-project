# Personal Helper Bot

A command-line application for managing contacts with phone numbers and birthdays.

## Features

- Store and manage contacts
- Add phone numbers and change existing ones
- Track birthdays and get reminders
- Interactive help system
- Automatic data persistence

## Instructions

### Setup

```bash
# Enter the project directory
cd python-final-project

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the application
python -m pip install .
```

### Run the Application

```bash
# Activate virtual environment (if not already active)
source .venv/bin/activate

# Run the application
personal-helper-bot
```

The `personal-helper-bot` command is now available after installation.

**Run from the source tree without installing the application:**
```bash
# From the project root
python src
```

### Run Tests

For development, install the project with its test dependencies:

```bash
python -m pip install -e ".[dev]"
```

```bash
# Run all tests
python -m pytest
```

For coverage, install the separate `coverage` package and run:

```bash
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
- `exit` — Quit the program

### Interactive Help

The application includes an interactive help system:

```text
Enter a command: help
Enter a command: help add
Enter a command: help add-birthday
```

### Data storage

Contacts are saved in a pickle file when you quit the application:

| OS      | Location                                                      |
|---------|---------------------------------------------------------------|
| Windows | `%APPDATA%\personal-helper-bot\addressbook.pkl` |
| macOS   | `~/Library/Application Support/personal-helper-bot/addressbook.pkl` |
| Linux   | `$XDG_DATA_HOME/personal-helper-bot/addressbook.pkl` (default `~/.local/share/personal-helper-bot/addressbook.pkl`) |

On exit, the application writes to a temporary file and atomically replaces the
existing file. If saving fails, it asks whether to exit without saving.

The file uses Python's pickle format. Only load files from trusted sources;
unpickling untrusted data can execute arbitrary code.

### Requirements

- Python 3.10+
- Runtime dependency: `colorama` (installed automatically with the application)
- Tests require `pytest`; coverage reports additionally require `coverage`

## Architecture & Design Patterns

This project uses a modular command-based architecture where each command is a separate class. Commands are automatically discovered and registered when the app starts.

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for how the app works and [`CONTRIBUTING.md`](CONTRIBUTING.md) for how to add new commands.
