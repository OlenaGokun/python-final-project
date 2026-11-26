from personal_helper.commands.base_command import AddressBookCommand
from personal_helper.core.data import parse_options
from personal_helper.core.decorators import input_error
from personal_helper.models.book import AddressBook


class AddAddressCommand(AddressBookCommand):
    def get_command_name(self) -> str:
        return "add-address"

    def get_description(self) -> str:
        return "add or update an address for a contact"

    def get_usage(self) -> str:
        return "add-address --name <name> --address <address>"

    @input_error
    def run_with_address_book(
        self, args: list, address_book: AddressBook
    ) -> str:
        required = {"--name", "--address"}
        options = parse_options(args, required, required, self.get_usage())
        name = " ".join(options["--name"])
        address = " ".join(options["--address"])
        record = address_book[name]
        record.add_address(address)
        return f"✅ Address added for {record.name.value}."
