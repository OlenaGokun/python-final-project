import pickle

from personal_helper import parse_input, CommandRegistry
from personal_helper.models import PersonalHelper
from personal_helper.commands.base_command import ExitRequest
from personal_helper.core import InvalidInputError
from personal_helper.core.pickle_manager import load_data, save_data


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


def confirm_exit(data: PersonalHelper) -> bool:
    """Save application data; if that fails, ask whether to quit anyway."""
    try:
        save_data(data)
        return True
    except (OSError, pickle.PickleError) as e:
        print(f"Failed to save application data: {e}")

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
    try:
        data = load_data()
    except (
        OSError,
        pickle.PickleError,
        EOFError,
        AttributeError,
        ImportError,
        IndexError,
        TypeError,
        ValueError,
    ) as e:
        print(f"Failed to load application data: {e}")
        print("Starting with empty application data.")
        data = PersonalHelper()

    print("Welcome to Personal Helper Bot!")
    print_commands(registry)

    while True:
        try:
            user_input = input("Enter a command: ")
        except (EOFError, KeyboardInterrupt):
            # Ctrl+D / Ctrl+C: exit the same way as "exit", so data gets saved.
            print()
            user_input = "exit"

        try:
            command, *args = parse_input(user_input)
        except InvalidInputError as error:
            print(f"❌ {error}")
            continue

        if not command:
            print("Please enter a command.")
            continue

        cmd = registry.get_command(command)
        if cmd is None:
            print("Invalid command.")
            continue

        try:
            result = cmd.run(args, data)
        except Exception as e:
            print(f"Error: {e}")
            continue

        if isinstance(result, ExitRequest):
            if confirm_exit(data):
                print("Good bye!")
                break
        else:
            print(result)
