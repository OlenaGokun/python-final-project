# Contributing Guide

## Project Overview

Personal Helper Bot is a command-line application that stores contacts with phone numbers and birthdays, as well as independent notes. Data is automatically saved to the user's system when they quit.

## Architecture Overview

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the application layers and command
discovery.

## Where to Add New Commands

Commands are located in `src/personal_helper/commands/`. Each command is a separate file.

For the complete project structure, see [`ARCHITECTURE.md`](ARCHITECTURE.md#project-structure).

## How Commands Work

Commands are organized as separate classes that inherit from `BaseCommand`. The **Registry pattern** automatically discovers commands at startup by scanning for classes that inherit from `BaseCommand`.

### 1. Create a new command file

Create `src/personal_helper/commands/my_command.py`:

```python
from personal_helper.models import PersonalHelper
from personal_helper.commands.base_command import BaseCommand
from personal_helper.core import input_error
from personal_helper.core.data import parse_options


class MyCommand(BaseCommand):
    """Return a greeting."""

    def get_command_name(self) -> str:
        return "my-command"
    
    def get_description(self) -> str:
        return "greet a person"

    def get_usage(self) -> str:
        return "my-command --name <name>"

    @input_error
    def run(self, args: list, data: PersonalHelper) -> str:
        options = parse_options(args, {"--name"}, {"--name"}, self.get_usage())
        return f"Hello, {' '.join(options['--name'])}!"
```

### 2. That's it!

The registry automatically:
- Finds your new file on startup
- Imports it
- Discovers `MyCommand` via class inheritance scanning
- Registers it and makes it available in the help menu

No manual registration or registration decorator is needed. The name must be
non-empty, unique, contain no whitespace, and remain unchanged by Python's
`casefold()` method. Command classes must be
concrete, defined in a module directly under `commands/`, and instantiable
without arguments.

Commands that need access to the complete command list can override
`set_registry(self, registry)`; the registry calls it after discovery finishes.
The built-in `help` command uses this hook rather than creating a second registry.

Commands that request application shutdown should return `ExitRequest`; the
application remains responsible for saving data and exiting.

For commands that need one collection, inherit from `AddressBookCommand` or
`NotebookCommand` instead. Implement `run_with_address_book(self, args,
address_book: AddressBook)` or `run_with_notebook(self, args, notebook:
Notebook)` respectively, rather than `run`. Their base classes select the
collection from `PersonalHelper` while keeping the main dispatch unchanged.
Their `run` methods are marked `@final`: implement the collection-specific
method instead of overriding `run`. Python type checkers enforce this, but
Python itself does not prevent overriding at runtime.
Use `BaseCommand` directly for commands such as `hello` that need neither
collection, or for commands requiring both. Apply `@input_error` to the method
you implement when formatted command errors are needed.

## Error Handling

Custom exceptions are defined in `src/personal_helper/core/exceptions.py`:

```python
from personal_helper.core import input_error, InvalidInputError

@input_error  # This decorator catches errors and formats them nicely
def run(self, args, data):
    if len(args) < 2:
        raise InvalidInputError("Need at least 2 arguments")
    # ... rest of command
```

The `@input_error` decorator returns formatted messages for `CommandError`
subclasses and unexpected exceptions. Include usage hints in the exception
message when appropriate. Decorators are optional; the main loop also reports
exceptions that escape a command.

## Testing

See [README.md](README.md#run-tests) for setup, test, and coverage commands.

### Write Tests for Your New Command

Create `tests/personal_helper/commands/test_my_command.py`:

```python
class TestMyCommand:
    """Tests for my-command"""
    
    def test_my_command_success(self, registry, data):
        cmd = registry.get_command("my-command")
        result = cmd.run(["--name", "arg1"], data)
        
        assert result == "Hello, arg1!"
    
    def test_my_command_error(self, registry, data):
        cmd = registry.get_command("my-command")
        result = cmd.run([], data)
        
        assert result.startswith("❌ Invalid arguments.")
```

**Note:** Use the shared `registry` and `data` fixtures from `tests/conftest.py` - no need to define them in every test file!

## Common Tasks

### Add a new command
See "How Commands Work" section above.

### Add a new error type
1. Add to `src/personal_helper/core/exceptions.py`:
   ```python
   class MyCustomError(CommandError):
       """Description of your error"""
   ```

2. Import and use in your command:
   ```python
   from personal_helper.core import input_error, MyCustomError
   
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

For the source directory structure, see [Project Structure in ARCHITECTURE.md](ARCHITECTURE.md#project-structure).

## Data Storage

See [README.md](README.md#data-storage) for data storage locations on Windows, macOS, and Linux.

## Testing Architecture

Tests are organized to mirror the source structure:

```
tests/
├── conftest.py          # Shared fixtures (book, registry, etc.)
├── personal_helper/
│   ├── models/          # Mirrors src/personal_helper/models/
│   ├── commands/        # Mirrors src/personal_helper/commands/
│   ├── core/            # Infrastructure tests, including persistence
│   └── test_*.py        # Registry and integration tests
└── test_main.py         # Application entry point tests
```

This mirrored structure makes it easy to find and write tests for new code.
