# Address Book Application

A command-line address book that stores contact information and birthdays. The application uses a modular command system where each command is a separate file, making it easy to add new features.

## Architecture

The project follows a layered architecture with clear separation of concerns:

### **Domain Layer** (`models/`)
Core business entities: `AddressBook`, `Record`, `Field`, `Name`, `Phone`, `Birthday`

### **Application Layer** (`commands/`)
Command implementations using the **Registry Pattern** for auto-discovery:
- Each command inherits from `BaseCommand`
- Automatically discovered at startup via class scanning
- Command names and help metadata are validated, and duplicate names are rejected
- Aliases are registered with their command, and shutdown requests are handled by the application
- The initialized registry is injected into commands after discovery for shared lookups
- No decorators or magic needed - inheritance is the signal

### **Infrastructure Layer** (`core/`)
Utilities and support code:
- `data.py` — Input parsing (`parse_input`)
- `decorators.py` — Error handling (`@input_error`)
- `exceptions.py` — Custom errors (`InvalidInputError`, `CommandError`)

## How It Works

1. **User enters a command** (like `add John 555-1234`)
2. **CommandRegistry** discovers all commands by scanning inherited classes
3. **Application parses the command** and finds the matching handler
4. **Handler processes the request** (validates input, updates data)
5. **Result is displayed** to the user
6. **Data is saved** automatically on exit

## Command System

Each command is a separate class that inherits from `BaseCommand`. The registry automatically discovers and loads all commands at startup.

### Example Command

```python
from address_book.models import AddressBook
from address_book.commands.base_command import BaseCommand
from address_book.core import input_error, InvalidInputError


class AddContactCommand(BaseCommand):
    def get_command_name(self) -> str:
        return "add"
    
    def get_description(self) -> str:
        return "Add or update a contact"
    
    def get_usage(self) -> str:
        return "add <name> [phone]"
    
    @input_error
    def run(self, args: list, book: AddressBook) -> str:
        # Validate input
        if not args:
            raise InvalidInputError("Name is required")
        # Update book
        name = args[0]
        # ... rest of logic
        return f"Contact '{name}' added"
```

## Project Structure

```
src/address_book/
├── models/           # Domain entities and validation
├── commands/         # Command implementations
├── core/             # Parsing, error handling, and exceptions
└── command_registry.py
```

## Error Handling

The app catches errors from each command and displays helpful messages:

```python
from address_book.core import input_error, InvalidInputError

@input_error  # Catches errors and formats them nicely
def run(self, args, book):
    if len(args) < 1:
        raise InvalidInputError("Name required")
```

## Extending the Application

To add a new command, follow the step-by-step guide in [`CONTRIBUTING.md`](CONTRIBUTING.md#how-commands-work).

The process is simple:
1. Create a new Python file in `src/address_book/commands/`
2. Write a class that inherits from `BaseCommand`
3. Implement the required abstract methods

That's it! The command is automatically discovered via the Registry pattern.

## Data Storage

Data is saved automatically to a user-specific folder. See [README.md](README.md#data-storage) for storage locations on each operating system.

## Testing

The project includes comprehensive tests organized to mirror the source structure:

```bash
# All tests
pytest tests/

# Model tests
pytest tests/address_book/models/ -v

# Command tests
pytest tests/address_book/commands/ -v

# Infrastructure tests
pytest tests/address_book/test_*.py -v
```

Tests use shared fixtures from `tests/conftest.py` to eliminate duplication.
