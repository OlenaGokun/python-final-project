from address_book.core.decorators import input_error
from address_book.models.book import AddressBook
from address_book.commands.base_command import BaseCommand
from address_book.core.exceptions import InvalidInputError


class ShowBirthdayCommand(BaseCommand):
    """Command to show birthday for a contact"""

    def get_command_name(self) -> str:
        return "show-birthday"

    def get_description(self) -> str:
        return "show birthday for a contact"

    def get_usage(self) -> str:
        return "show-birthday <name>"

    @input_error
    def run(self, args: list, book: AddressBook) -> str:
        if len(args) != 1:
            raise InvalidInputError(
                f"Invalid arguments.\n"
                f"Usage: {self.get_usage()}\n"
                f"Example: show-birthday John"
            )
        record = book[args[0]]
        if record.birthday is None:
            return f"ℹ️  {record.name.value} has no birthday set."
        return f"🎂 {record.name.value}'s birthday: {record.birthday}"
