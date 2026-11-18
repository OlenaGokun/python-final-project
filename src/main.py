import pickle

from address_book.data import parse_input
from pickle_manager import load_data, save_data
from address_book.commands.add_contact import add_contact
from address_book.commands.change_contact import change_contact
from address_book.commands.show_all import show_all
from address_book.commands.show_phone import show_phone
from address_book.commands.add_birthday import add_birthday
from address_book.commands.show_birthday import show_birthday
from address_book.commands.show_birthdays import show_birthdays

from address_book.book import AddressBook

COMMANDS = [
    ("hello", "get a greeting from the bot"),
    ("add <name> [phone]", "add a new contact or add phone to existing"),
    ("change <name> <old_phone> <new_phone>", "change phone number for a contact"),
    ("phone <name>", "show phone numbers for a contact"),
    ("all", "show all contacts in address book"),
    ("add-birthday <name> <DD.MM.YYYY>", "add a birthday for a contact"),
    ("show-birthday <name>", "show birthday for a contact"),
    ("birthdays", "show upcoming birthdays in the next 7 days"),
    ("close | exit", "quit the program"),
]


def print_commands():
    width = max(len(usage) for usage, _ in COMMANDS)
    print("\nAvailable commands:")
    for usage, description in COMMANDS:
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
    book = load_data()
    print("Welcome to the assistant bot!")
    print_commands()

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

        if command in ["close", "exit"]:
            if confirm_exit(book):
                print("Good bye!")
                break
            continue

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(show_birthdays(book))

        else:
            print("Invalid command.")
