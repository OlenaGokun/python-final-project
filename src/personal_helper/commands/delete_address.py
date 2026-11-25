from personal_helper.commands.base_command import AddressBookCommand
from personal_helper.core.data import parse_options
from personal_helper.core.decorators import input_error
from personal_helper.models.book import AddressBook


class DeleteAddressCommand(AddressBookCommand):
    def get_command_name(self) -> str:
        return "delete-address"

    def get_description(self) -> str:
        return "remove a contact's address"

    def get_usage(self) -> str:
        return "delete-address --name <name>"

    @input_error
    def run_with_address_book(self, args: list, address_book: AddressBook) -> str:
        required = {"--name"}
        options = parse_options(args, required, required, self.get_usage())
        record = address_book[" ".join(options["--name"])]
        record.remove_address()
        return f"✅ Address removed for {record.name.value}."
