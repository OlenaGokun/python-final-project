# Personal Helper Bot Architecture

A command-line address book that stores contact information and birthdays. The application uses a modular command system where each command is a separate file, making it easy to add new features.

## Architecture

The project follows a layered architecture with clear separation of concerns:

### **Domain Layer** (`models/`)
Core business entities: `AddressBook`, `Record`, `Field`, `Name`, `Phone`, `Birthday`

### **Application Layer** (`commands/`)
Command implementations using the **Registry Pattern** for auto-discovery:
- Each command inherits from `BaseCommand`
- Automatically discovered at startup via class scanning
- A command module import failure stops startup and propagates the original error
- Startup also fails if no commands are discovered
- Command names are validated, and duplicate names are rejected
- Shutdown requests are handled by the application
- The initialized registry is injected into commands after discovery for shared lookups
- No registration decorator is needed; inheritance is the discovery signal

### **Infrastructure Layer** (`core/`)
Utilities and support code:
- `data.py` — Input parsing (`parse_input`)
- `decorators.py` — Error handling (`@input_error`)
- `exceptions.py` — Custom errors (`InvalidInputError`, `CommandError`)
- `pickle_manager.py` — Address book persistence

## How It Works

1. At startup, **CommandRegistry** discovers commands and the application loads the address book.
2. The user enters a command, such as `add John 0501234567`.
3. The application parses the input and looks up the command in the registry.
4. The command processes the request and returns a message or an exit request.
5. The application displays the message, or saves the address book before exiting.

## Command System

Each command is a separate class that inherits from `BaseCommand`. The registry automatically discovers and loads all commands at startup.

## Project Structure

```
src/address_book/
├── models/           # Domain entities and validation
├── commands/         # Command implementations
├── core/             # Parsing, error handling, and persistence
└── command_registry.py
```

## Error Handling

Commands using `@input_error` return formatted messages for `CommandError`
exceptions and unexpected exceptions. The main loop also reports exceptions
that escape command execution. Discovery errors stop startup.

## Extending the Application

To add a new command, follow the step-by-step guide in [`CONTRIBUTING.md`](CONTRIBUTING.md#how-commands-work).

## Data Storage

Data is saved automatically to a user-specific folder. See [README.md](README.md#data-storage) for storage locations on each operating system.
