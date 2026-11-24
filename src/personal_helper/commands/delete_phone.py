from personal_helper.commands.base_command import AddressBookCommand
from personal_helper.core.data import parse_options
from personal_helper.core.decorators import input_error
from personal_helper.models.book import AddressBook


class DeletePhoneCommand(AddressBookCommand):
    def get_command_name(self) -> str:
        return "delete-phone"

    def get_description(self) -> str:
        return "remove a contact's phone"

    def get_usage(self) -> str:
        return "delete-phone --name <name> --phone <phone-or-alias>"

    @input_error
    def run_with_address_book(self, args: list, address_book: AddressBook) -> str:
        required = {"--name", "--phone"}
        options = parse_options(args, required, required, self.get_usage(), single={"--phone"})
        record = address_book[" ".join(options["--name"])]
        record.remove_phone(options["--phone"][0])
        return f"✅ Phone removed for {record.name.value}."
