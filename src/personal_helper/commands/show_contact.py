from personal_helper.core.decorators import input_error
from personal_helper.models.book import AddressBook
from personal_helper.commands.base_command import AddressBookCommand
from personal_helper.core.data import parse_options


class ShowContactCommand(AddressBookCommand):
    """Command to show all details for a contact."""

    def get_command_name(self) -> str:
        return "show-contact"

    def get_description(self) -> str:
        return "show all details for a contact"

    def get_usage(self) -> str:
        return "show-contact --name <name>"

    @input_error
    def run_with_address_book(
        self, args: list, address_book: AddressBook
    ) -> str:
        options = parse_options(args, {"--name"}, {"--name"}, self.get_usage())
        record = address_book[" ".join(options["--name"])]
        return self.format_contact_details(record)
