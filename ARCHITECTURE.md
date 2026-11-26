# Personal Helper Bot Architecture

A command-line application that stores contacts, birthdays, and independent notes. The application uses a modular command system where each command is a separate file, making it easy to add new features.

## Architecture

The project follows a layered architecture with clear separation of concerns:

### **Domain Layer** (`models/`)
Core business entities: `AddressBook`, `Record`, `Field`, `Name`, `Phone`,
`Email`, `Address`, `Birthday`, `Title`, `Text`, `Tag`, `Note`, and `Notebook`.
`PersonalHelper` holds an independent address book and notebook.
Notes are indexed by case-folded title while retaining the original title for display.

### **Application Layer** (`commands/`)
Command implementations using the **Registry Pattern** for auto-discovery:
- Each command inherits from `BaseCommand`
- Contact and note commands inherit from `AddressBookCommand` and `NotebookCommand`;
  these pass only the required collection to the command implementation and
  provide compact and detailed formatting helpers for their respective records
- Automatically discovered at startup via class scanning
- A command module import failure stops startup and propagates the original error
- Startup also fails if no commands are discovered
- Command names are validated, and duplicate names are rejected
- Shutdown requests are handled by the application
- The initialized registry is injected into commands after discovery for shared lookups
- Commands depend on the read-only `CommandLookup` protocol rather than the
  concrete registry; help uses it to list and look up commands
- No registration decorator is needed; inheritance is the discovery signal

### **Infrastructure Layer** (`core/`)
Utilities and support code:
- `data.py` — Input parsing (`parse_input`)
- `decorators.py` — Error handling (`@input_error`)
- `exceptions.py` — Custom errors (`InvalidInputError`, `CommandError`)
- `pickle_manager.py` — Application data persistence and standalone address-book loading

## How It Works

1. At startup, **CommandRegistry** discovers commands and the application loads `PersonalHelper`.
   If the saved file is missing, the application starts with empty data.
   If saved data is invalid or unsupported, the application reports the error
   and starts with empty data.
2. The user enters a command, such as `add-contact --name Mary Jane --phone 0501234567`.
3. The application splits the input and looks up the command in the registry. Commands use the shared option parser to collect values between named options.
4. The command receives the shared data; specialized command bases pass the relevant collection to the implementation. The command returns a message or an exit request.
5. The application displays the message, or saves the application data before exiting.

## Command System

Each command is a separate class that inherits from `BaseCommand`. The registry automatically discovers and loads all commands at startup.

## Project Structure

```
src/
├── main.py             # Application entry point
└── personal_helper/
    ├── models/         # Domain entities and validation
    ├── commands/       # Command implementations
    ├── core/           # Parsing, error handling, and persistence
    └── command_registry.py
```

Tests live under `tests/personal_helper/` and mirror the package structure.

## Error Handling

Commands using `@input_error` return formatted messages for `CommandError`
exceptions and unexpected exceptions. The main loop also reports exceptions
that escape command execution. Discovery errors stop startup.

## Extending the Application

To add a new command, follow the step-by-step guide in [`CONTRIBUTING.md`](CONTRIBUTING.md#how-commands-work).

## Data Storage

Data is saved automatically to a user-specific folder. A saved standalone
`AddressBook` object is wrapped in `PersonalHelper` when loaded. See
[README.md](README.md#data-storage) for storage locations on each operating system.
