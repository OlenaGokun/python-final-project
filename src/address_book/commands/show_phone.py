from address_book.core.decorators import input_error
from address_book.models.book import AddressBook
from address_book.commands.base_command import BaseCommand
from address_book.core.exceptions import InvalidInputError


class ShowPhoneCommand(BaseCommand):
    """Command to show phone numbers for a contact"""

    def get_command_name(self) -> str:
        return "phone"

    def get_description(self) -> str:
        return "show phone numbers for a contact"

    def get_usage(self) -> str:
        return "phone <name>"

    @input_error
    def run(self, args: list, book: AddressBook) -> str:
        if len(args) != 1:
            raise InvalidInputError(
                f"Invalid arguments.\n"
                f"Usage: {self.get_usage()}\n"
                f"Example: phone John"
            )
        record = book[args[0]]
        if not record.phones:
            return f"ℹ️  No phone numbers found for {record.name.value}."
        return "; ".join(p.value for p in record.phones)
