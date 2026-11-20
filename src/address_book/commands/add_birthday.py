from address_book.core.decorators import input_error
from address_book.models.book import AddressBook
from address_book.commands.base_command import BaseCommand
from address_book.core.exceptions import InvalidInputError


class AddBirthdayCommand(BaseCommand):
    """Command to add birthday for a contact"""

    def get_command_name(self) -> str:
        return "add-birthday"

    def get_description(self) -> str:
        return "add a birthday for a contact"

    def get_usage(self) -> str:
        return "add-birthday <name> <DD.MM.YYYY>"

    @input_error
    def run(self, args: list, book: AddressBook) -> str:
        if len(args) != 2:
            raise InvalidInputError(
                f"Invalid arguments.\n"
                f"Usage: {self.get_usage()}\n"
                f"Example: add-birthday John 25.12.1990"
            )
        name, birthday = args
        record = book[name]
        record.add_birthday(birthday)
        return "✅ Birthday added."
