# Personal Helper Bot

A command-line application for managing contacts and independent text notes.

## Features

- Store and manage contacts
- Add phone numbers and change existing ones
- Add email addresses and search contacts by name, phone, email, or birthday
- Track birthdays and get reminders
- Add, update, delete, and search notes
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
- `help --command <command>` — Show details for a specific command
- `hello` — Get a greeting from the bot
- `add --name <name> [--phone <phone> ...] [--email <email>] [--birthday <DD.MM.YYYY>]` — Add a contact or update its details
- `change --name <name> --old-phone <phone> --new-phone <phone>` — Change a phone number
- `phone --name <name>` — Show phone numbers for a contact
- `show-all-contacts` — Show all contacts in the address book
- `add-birthday --name <name> --birthday <DD.MM.YYYY>` — Add a birthday
- `show-birthday --name <name>` — Show birthday for a contact
- `birthdays` — Show upcoming birthdays in the next 7 days
- `add-email --name <name> --email <email>` — Add or update a contact's email
- `search (--query <query> | [--name <name>] [--email <email>] [--phone <phone>] [--birthday <DD.MM.YYYY>])` — Search contacts by a query or field filters
- `add-note --title <title> --text <text> [--tags <tag> ...]` — Add a note with optional tags
- `update-note --title <title> [--text <text>] [--tags <tag> ...]` — Update text or replace tags
- `delete-note --title <title>` — Delete a note
- `find-notes (--query <query> | [--title <title>] [--text <text>] [--tags <tag> ...])` — Search notes
- `show-all-notes` — Show all notes
- `add-note-tags --title <title> --tags <tag> [tag ...]` — Add tags to a note
- `delete-note-tags --title <title> --tags <tag> [tag ...]` — Remove tags from a note
- `exit` — Quit the program

Names, titles, text, and search queries can contain spaces without quotes.
Options may appear in any order; each consumes words until the next option.
Words starting with `--` are reserved for option names and cannot be used as
values. Options cannot be repeated, and each requires a value. Command input
whitespace is normalized to single spaces. For example:

```text
add --name Mary Jane --phone 0501234567 0501234568 --email mary@example.com --birthday 01.01.2000
search --name Mary Jane --email example.com
search --query 0501234567
find-notes --title Grocery list --tags food home
find-notes --query shopping
show-all-contacts
show-all-notes
add-note --title Grocery list --text Buy milk --tags food home
add-note-tags --title Grocery list --tags shopping
```

Note titles must be unique, ignoring case. Search commands require either a
`--query` or at least one field filter; `--query` cannot be combined with
field-specific filters. Text searches are case-insensitive substring matches,
not exact matches. Contact `--query` searches names, emails, phone numbers, and
birthdays; individual contact field filters also match substrings. Note
`--query` searches titles, text, and tags by substring. For note field filters,
`--title` and `--text` match substrings, while `--tags` matches tags exactly,
ignoring case. Multiple field filters for either contacts or notes are combined
with AND; any one supplied note tag may match. For example,
`find-notes --title shop --text buy milk --tags food home` finds notes whose
title contains `shop`, text contains `buy milk`, and tags include `food` or
`home`. Tags are single words, stored in case-folded form. Use
`show-all-notes` or `show-all-contacts` to list all records without filters.
`update-note` requires `--text`, `--tags`, or both. Its `--tags` option
replaces all existing tags; use `delete-note-tags` to remove individual tags
or clear them all.

### Interactive Help

The application includes an interactive help system:

```text
Enter a command: help
Enter a command: help --command add
Enter a command: help --command add-birthday
```

### Data storage

Contacts and notes are saved in a pickle file when you quit the application:

| OS      | Location                                                      |
|---------|---------------------------------------------------------------|
| Windows | `%APPDATA%\personal-helper-bot\addressbook.pkl` |
| macOS   | `~/Library/Application Support/personal-helper-bot/addressbook.pkl` |
| Linux   | `$XDG_DATA_HOME/personal-helper-bot/addressbook.pkl` (default `~/.local/share/personal-helper-bot/addressbook.pkl`) |

On exit, the application writes to a temporary file and atomically replaces the
existing file. If saving fails, it asks whether to exit without saving. A
loadable standalone `AddressBook` object is wrapped in `PersonalHelper` when
loaded; the application saves data in the current format on exit.

The file uses Python's pickle format. Only load files from trusted sources;
unpickling untrusted data can execute arbitrary code.

### Requirements

- Python 3.10+
- Runtime dependency: `colorama` (installed automatically with the application)
- Tests require `pytest`; coverage reports additionally require `coverage`

## Architecture & Design Patterns

This project uses a modular command-based architecture where each command is a separate class. Commands are automatically discovered and registered when the app starts.

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for how the app works and [`CONTRIBUTING.md`](CONTRIBUTING.md) for how to add new commands.
