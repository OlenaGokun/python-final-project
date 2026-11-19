# Contributing Guide

## Project Overview

Personal Helper Bot is a command-line application that stores contacts with phone numbers and birthdays. Data is automatically saved to the user's system when they quit.

## Architecture Overview

The project follows a **3-layer architecture**:

```
Domain Layer (models/)      ← Business entities
     ↓
Application Layer (commands/)  ← Command implementations
     ↓
Infrastructure Layer (core/)   ← Utilities & error handling
```

For complete architecture details, see [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Where to Add New Commands

Commands are located in `src/address_book/commands/`. Each command is a separate file.

For the complete project structure, see [`ARCHITECTURE.md`](ARCHITECTURE.md#project-structure).

## How Commands Work

Commands are organized as separate classes that inherit from `BaseCommand`. The **Registry pattern** automatically discovers commands at startup by scanning for classes that inherit from `BaseCommand`.

### 1. Create a new command file

Create `src/address_book/commands/my_command.py`:

```python
from address_book.models import AddressBook
from address_book.commands.base_command import BaseCommand
from address_book.core import input_error, InvalidInputError


class MyCommand(BaseCommand):
    """Your command description"""
    
    def get_command_name(self) -> str:
        return "my-command"
    
    def get_description(self) -> str:
        return "What this command does"
    
    def get_usage(self) -> str:
        return "my-command [args]"
    
    @input_error
    def run(self, args: list, book: AddressBook) -> str:
        # Your logic here
        return "Success message"
```

### 2. That's it!

The registry automatically:
- Finds your new file on startup
- Imports it
- Discovers `MyCommand` via class inheritance scanning
- Registers it and makes it available in the help menu

**No need to edit any other files or use decorators!**

Commands that need access to the complete command list can override
`set_registry(self, registry)`; the registry calls it after discovery finishes.
The built-in `help` command uses this hook rather than creating a second registry.

Alternate command names can be returned from `get_aliases()`, which defaults to
an empty tuple. Commands that request application shutdown should return
`ExitRequest`; the application remains responsible for saving data and exiting.

## Error Handling

Custom exceptions are defined in `src/address_book/core/exceptions.py`:

```python
from address_book.core import input_error, InvalidInputError, CommandError

@input_error  # This decorator catches errors and formats them nicely
def run(self, args, book):
    if len(args) < 2:
        raise InvalidInputError("Need at least 2 arguments")
    # ... rest of command
```

The `@input_error` decorator will:
- Catch your exceptions
- Display a friendly message with emoji indicator (✅ or ❌)
- Include helpful hints about correct usage
- Let the app continue running

## Testing

### Run Tests

```bash
# All tests
pytest tests/

# Model tests (domain layer)
pytest tests/address_book/models/ -v

# Command tests (application layer)
pytest tests/address_book/commands/ -v

# Infrastructure tests
pytest tests/address_book/test_command_registry.py tests/address_book/test_error_messages.py -v

# Specific test file
pytest tests/address_book/commands/test_add_contact.py -v
```

### Write Tests for Your New Command

Create `tests/address_book/commands/test_my_command.py`:

```python
import pytest
from address_book.commands.my_command import MyCommand

class TestMyCommand:
    """Tests for my-command"""
    
    def test_my_command_success(self, registry, book):
        cmd = registry.get_command("my-command")
        result = cmd.run(["arg1", "arg2"], book)
        
        assert "expected text" in result
        assert "✅" in result
    
    def test_my_command_error(self, registry, book):
        cmd = registry.get_command("my-command")
        result = cmd.run([], book)
        
        assert "❌" in result
```

**Note:** Use the shared `registry` and `book` fixtures from `tests/conftest.py` - no need to define them in every test file!

## Common Tasks

### Add a new command
See "How Commands Work" section above.

### Add a new error type
1. Add to `src/address_book/core/exceptions.py`:
   ```python
   class MyCustomError(CommandError):
       """Description of your error"""
   ```

2. Import and use in your command:
   ```python
   from address_book.core import input_error, MyCustomError
   
   @input_error
   def run(self, args, book):
       raise MyCustomError("Error message")
   ```

### Change error messages
Edit the command's `run()` method and update the exception:
```python
raise InvalidInputError("Phone must be 10 digits")
```

### Update help text
Edit the methods in your command class:
```python
def get_description(self) -> str:
    return "Updated description"

def get_usage(self) -> str:
    return "updated-command [new-args]"
```

For the source and test directory structure, see [Project Structure in ARCHITECTURE.md](ARCHITECTURE.md#project-structure).

## Data Storage

See [README.md](README.md#data-storage) for data storage locations on Windows, macOS, and Linux.

## Testing Architecture

Tests are organized to mirror the source structure:

```
tests/
├── conftest.py          # Shared fixtures (book, registry, etc.)
├── address_book/
│   ├── models/          # Mirrors src/models/
│   ├── commands/        # Mirrors src/commands/
│   ├── core/            # Infrastructure tests, including persistence
│   └── test_*.py        # Registry and integration tests
└── test_main.py         # Application entry point tests
```

This mirrored structure makes it easy to find and write tests for new code.
