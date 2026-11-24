from personal_helper.core.decorators import input_error
from personal_helper.models.book import AddressBook
from personal_helper.commands.base_command import AddressBookCommand
from personal_helper.core.data import parse_options


class ShowPhoneCommand(AddressBookCommand):
    """Command to show phone numbers for a contact"""

    def get_command_name(self) -> str:
        return "phone"

    def get_description(self) -> str:
        return "show phone numbers for a contact"

    def get_usage(self) -> str:
        return "phone --name <name>"

    @input_error
    def run_with_address_book(self, args: list, address_book: AddressBook) -> str:
        options = parse_options(args, {"--name"}, {"--name"}, self.get_usage())
        record = address_book[" ".join(options["--name"])]
        if not record.phones:
            return f"ℹ️  No phone numbers found for {record.name.value}."
        return "; ".join(map(str, record.phones))
