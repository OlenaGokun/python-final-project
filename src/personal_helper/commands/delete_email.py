from personal_helper.commands.base_command import AddressBookCommand
from personal_helper.core.data import parse_options
from personal_helper.core.decorators import input_error
from personal_helper.models.book import AddressBook


class DeleteEmailCommand(AddressBookCommand):
    def get_command_name(self) -> str:
        return "delete-email"

    def get_description(self) -> str:
        return "remove a contact's email"

    def get_usage(self) -> str:
        return "delete-email --name <name>"

    @input_error
    def run_with_address_book(self, args: list, address_book: AddressBook) -> str:
        required = {"--name"}
        options = parse_options(args, required, required, self.get_usage())
        record = address_book[" ".join(options["--name"])]
        record.remove_email()
        return f"✅ Email removed for {record.name.value}."
