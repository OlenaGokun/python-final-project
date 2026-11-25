from personal_helper.core.decorators import input_error
from personal_helper.models.book import AddressBook
from personal_helper.commands.base_command import AddressBookCommand
from personal_helper.commands.contact_field_retry import ContactFieldRetry
from personal_helper.core.data import parse_options


class ChangePhoneCommand(ContactFieldRetry, AddressBookCommand):
    """Command to change phone number for a contact"""

    def get_command_name(self) -> str:
        return "change-phone"

    def get_description(self) -> str:
        return "change phone number for a contact"

    def get_usage(self) -> str:
        return "change-phone --name <name> --old-phone <phone-or-alias> --new-phone <phone>"

    @input_error
    def run_with_address_book(self, args: list, address_book: AddressBook) -> str:
        single = {"--old-phone", "--new-phone"}
        required = {"--name", *single}
        options = parse_options(args, required, required, self.get_usage(), single)
        name = " ".join(options["--name"])
        old_phone = options["--old-phone"][0]
        new_phone = options["--new-phone"][0]
        record = address_book[name]
        if record.find_phone(old_phone) is not None:
            new_phone = self._validate_contact_field(new_phone, "phone")
        record.edit_phone(old_phone, new_phone)
        return f"✅ Contact '{record.name.value}' updated."
