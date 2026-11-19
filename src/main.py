import pickle

from address_book import parse_input, AddressBook, CommandRegistry
from address_book.commands.base_command import ExitRequest
from pickle_manager import load_data, save_data


def print_commands(registry: CommandRegistry):
    """Print available commands from the registry."""
    print("\nAvailable commands:")

    commands = [
        (cmd.get_usage(), cmd.get_description())
        for cmd in registry.get_all_commands()
    ]

    # Calculate width for alignment
    width = max(len(usage) for usage, _ in commands)

    # Print nicely formatted
    for usage, description in commands:
        print(f"  {usage.ljust(width)}  - {description}")
    print()


def confirm_exit(book: AddressBook) -> bool:
    """Save the book; if that fails, ask whether to quit anyway."""
    try:
        save_data(book)
        return True
    except (OSError, pickle.PickleError) as e:
        print(f"Failed to save address book: {e}")

    while True:
        try:
            choice = input("Exit without saving? (yes/no): ").strip().casefold()
        except (EOFError, KeyboardInterrupt):
            print()
            return True

        if choice in ("yes", "y"):
            return True
        if choice in ("no", "n"):
            return False
        print("Please enter yes or no.")


def main():
    registry = CommandRegistry()
    book = load_data()
    print("Welcome to the assistant bot!")
    print_commands(registry)

    while True:
        try:
            user_input = input("Enter a command: ")
        except (EOFError, KeyboardInterrupt):
            # Ctrl+D / Ctrl+C: exit the same way as "exit", so data gets saved.
            print()
            user_input = "exit"

        command, *args = parse_input(user_input)

        if not command:
            print("Please enter a command.")
            continue

        cmd = registry.get_command(command)
        if cmd is None:
            print("Invalid command.")
            continue

        try:
            result = cmd.run(args, book)
        except Exception as e:
            print(f"Error: {e}")
            continue

        if isinstance(result, ExitRequest):
            if confirm_exit(book):
                print("Good bye!")
                break
        else:
            print(result)
