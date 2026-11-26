from personal_helper.commands.base_command import AddressBookCommand
from personal_helper.commands.contact_field_retry import ContactFieldRetry
from personal_helper.core import input_error
from personal_helper.core.data import parse_options
from personal_helper.models.book import AddressBook
from personal_helper.models.record import Record


class AddPhoneCommand(ContactFieldRetry, AddressBookCommand):
    def get_command_name(self) -> str:
        return "add-phone"

    def get_description(self) -> str:
        return "add a phone to a contact, using main if no alias is supplied"

    def get_usage(self) -> str:
        return "add-phone --name <name> --phone <phone> [--alias <alias>]"

    @input_error
    def run_with_address_book(
        self, args: list, address_book: AddressBook
    ) -> str:
        required = {"--name", "--phone"}
        options = parse_options(
            args,
            required | {"--alias"},
            required,
            self.get_usage(),
            single={"--phone", "--alias"},
        )
        name = " ".join(options["--name"])
        phone = options["--phone"][0]
        alias = options.get("--alias", ["main"])[0]
        existing = address_book.find(name)
        record = existing if existing is not None else Record(name)
        phone = self._validate_contact_field(phone, "phone")
        record.add_phone(phone, alias)
        if existing is None:
            address_book.add_record(record)
            return f"✅ Contact '{record.name.value}' added."
        return f"✅ Contact '{record.name.value}' updated."
