import personal_helper
from personal_helper.commands.base_command import AddressBookCommand
from personal_helper.core.data import parse_options
from personal_helper.core.decorators import input_error
from personal_helper.models.book import AddressBook


class AddEmailCommand(AddressBookCommand):
    """Command to add or update a contact's email address."""

    def get_command_name(self) -> str:
        return "add-email"

    def get_description(self) -> str:
        return "add or update an email address for a contact"

    def get_usage(self) -> str:
        return "add-email --name <name> --email <email>"

    @input_error
    def run_with_address_book(self, args: list, address_book: AddressBook) -> str:
        required = {"--name", "--email"}
        options = parse_options(
            args, required, required, self.get_usage(), single={"--email"}
        )
        name = " ".join(options["--name"])
        record = address_book[name]

        record.add_email(options["--email"][0])
        return f"✅ Email added for {record.name.value}."
