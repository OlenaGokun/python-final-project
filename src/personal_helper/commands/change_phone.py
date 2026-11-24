from personal_helper.commands.base_command import AddressBookCommand
from personal_helper.core import InvalidInputError, input_error
from personal_helper.models.book import AddressBook


class ChangePhoneCommand(AddressBookCommand):
    def get_command_name(self) -> str:
        return "change"

    def get_description(self) -> str:
        return "replace a phone selected by number or alias"

    def get_usage(self) -> str:
        return "change <name> <phone-or-alias> <new-phone>"

    @input_error
    def run_with_address_book(self, args: list, address_book: AddressBook) -> str:
        if len(args) != 3:
            raise InvalidInputError(f"Invalid arguments.\nUsage: {self.get_usage()}")
        name, selector, new_phone = args
        record = address_book[name]
        record.edit_phone(selector, new_phone)
        return f"✅ Contact '{record.name.value}' updated."
