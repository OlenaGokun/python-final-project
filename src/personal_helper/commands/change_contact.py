from personal_helper.core.decorators import input_error
from personal_helper.models.book import AddressBook
from personal_helper.commands.base_command import AddressBookCommand
from personal_helper.core.data import parse_options


class ChangeContactCommand(AddressBookCommand):
    """Command to change phone number for a contact"""

    def get_command_name(self) -> str:
        return "change-phone"

    def get_description(self) -> str:
        return "change phone number for a contact"

    def get_usage(self) -> str:
        return "change-phone --name <name> --old-phone <phone-or-alias> --new-phone <phone>"

    @input_error
    def run_with_address_book(self, args: list, address_book: AddressBook) -> str:
        required = {"--name", "--old-phone", "--new-phone"}
        options = parse_options(args, required, required, self.get_usage(), {"--old-phone", "--new-phone"})
        name = " ".join(options["--name"])
        old_phone, new_phone = options["--old-phone"][0], options["--new-phone"][0]
        record = address_book[name]
        record.edit_phone(old_phone, new_phone)
        return f"✅ Contact '{record.name.value}' updated."
