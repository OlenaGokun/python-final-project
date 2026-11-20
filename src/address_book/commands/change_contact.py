from address_book.core.decorators import input_error
from address_book.models.book import AddressBook
from address_book.commands.base_command import BaseCommand
from address_book.core.exceptions import InvalidInputError


class ChangeContactCommand(BaseCommand):
    """Command to change phone number for a contact"""

    def get_command_name(self) -> str:
        return "change"

    def get_description(self) -> str:
        return "change phone number for a contact"

    def get_usage(self) -> str:
        return "change <name> <old_phone> <new_phone>"

    @input_error
    def run(self, args: list, book: AddressBook) -> str:
        if len(args) != 3:
            raise InvalidInputError(
                f"Invalid arguments.\n"
                f"Usage: {self.get_usage()}\n"
                f"Example: change John 0501234567 0509876543"
            )
        name, old_phone, new_phone = args
        record = book[name]
        record.edit_phone(old_phone, new_phone)
        return "✅ Contact updated."
