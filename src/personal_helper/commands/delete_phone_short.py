from personal_helper.commands.base_command import AddressBookCommand
from personal_helper.core import InvalidInputError, input_error
from personal_helper.models.book import AddressBook


class DeletePhoneShortCommand(AddressBookCommand):
    def get_command_name(self) -> str:
        return "delete"

    def get_description(self) -> str:
        return "remove a phone selected by number or alias"

    def get_usage(self) -> str:
        return "delete <name> <phone-or-alias>"

    @input_error
    def run_with_address_book(self, args: list, address_book: AddressBook) -> str:
        if len(args) != 2:
            raise InvalidInputError(f"Invalid arguments.\nUsage: {self.get_usage()}")
        name, selector = args
        record = address_book[name]
        record.remove_phone(selector)
        return f"✅ Phone removed for {record.name.value}."
