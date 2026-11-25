from personal_helper.core.decorators import input_error
from personal_helper.core.data import parse_options
from personal_helper.models.book import AddressBook
from personal_helper.models.record import Record
from personal_helper.commands.base_command import AddressBookCommand


class AddContact(AddressBookCommand):
    """Command to add contact or update an existing one"""

    def get_command_name(self) -> str:
        return "add-contact"

    def get_description(self) -> str:
        return "add a contact or update an existing one"

    def get_usage(self) -> str:
        return (
            "add-contact --name <name> [--phone <phone> ...] [--email <email>] "
            "[--address <address>] [--birthday <DD.MM.YYYY>]"
        )

    @input_error
    def run_with_address_book(self, args: list, address_book: AddressBook) -> str:
        single = {"--email", "--birthday"}
        options = parse_options(
            args,
            {"--name", "--phone", "--address", *single},
            {"--name"},
            self.get_usage(),
            single=single,
        )
        name = " ".join(options["--name"])
        phones = options.get("--phone", [])
        email = options["--email"][0] if "--email" in options else None
        birthday = options["--birthday"][0] if "--birthday" in options else None
        address = " ".join(options["--address"]) if "--address" in options else None

        record = address_book.find(name)
        is_new_contact = record is None
        if record is None:
            record = Record(name)
        record.update_details(
            phones=phones, email=email, birthday=birthday, address=address
        )
        if is_new_contact:
            address_book.add_record(record)
            return f"✅ Contact '{record.name.value}' added."
        return f"✅ Contact '{record.name.value}' updated."
