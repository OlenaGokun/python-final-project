from personal_helper.commands.base_command import AddressBookCommand
from personal_helper.core import InvalidInputError, input_error
from personal_helper.models.book import AddressBook
from personal_helper.models.record import Record


class AddPhoneCommand(AddressBookCommand):
    def get_command_name(self) -> str:
        return "add"

    def get_description(self) -> str:
        return "add a phone to a contact, using main if no alias is supplied"

    def get_usage(self) -> str:
        return "add <name> [<alias>] <phone>"

    @input_error
    def run_with_address_book(self, args: list, address_book: AddressBook) -> str:
        if len(args) not in (2, 3):
            raise InvalidInputError(f"Invalid arguments.\nUsage: {self.get_usage()}")
        name, *alias, phone = args
        existing = address_book.find(name)
        record = existing if existing is not None else Record(name)
        record.add_phone(phone, alias[0] if alias else "main")
        if existing is None:
            address_book.add_record(record)
            return f"✅ Contact '{record.name.value}' added."
        return f"✅ Contact '{record.name.value}' updated."
