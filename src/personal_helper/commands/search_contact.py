from personal_helper.commands.base_command import AddressBookCommand
from personal_helper.core.data import parse_options
from personal_helper.core.decorators import input_error
from personal_helper.core.exceptions import InvalidInputError
from personal_helper.models.book import AddressBook


class SearchContactsCommand(AddressBookCommand):
    """Command to find contacts by their details."""

    def get_command_name(self) -> str:
        return "search-contacts"

    def get_description(self) -> str:
        return "search contacts by name, phone, email, address, or birthday"

    def get_usage(self) -> str:
        return (
            "search-contacts (--query <query> | [--name <name>] "
            "[--email <email>] [--phone <phone>] [--address <address>] "
            "[--birthday <DD.MM.YYYY>])"
        )

    @input_error
    def run_with_address_book(
        self, args: list, address_book: AddressBook
    ) -> str:
        allowed = {
            "--query",
            "--name",
            "--email",
            "--phone",
            "--address",
            "--birthday",
        }
        single = {"--email", "--phone", "--birthday"}
        options = parse_options(
            args, allowed, set(), self.get_usage(), single=single
        )
        if not options:
            raise InvalidInputError(
                f"Invalid arguments. Provide --query or at least one field.\n"
                f"Usage: {self.get_usage()}"
            )
        field_options = allowed - {"--query"}
        if "--query" in options and options.keys() & field_options:
            raise InvalidInputError(
                "Invalid arguments. --query cannot be combined with "
                "field filters.\n"
                f"Usage: {self.get_usage()}"
            )

        values = {key[2:]: " ".join(items) for key, items in options.items()}
        matches = address_book.search(**values)
        if not matches:
            return "ℹ️  No contacts found."

        return "\n\n".join(
            self.format_contact_details(record) for record in matches
        )
