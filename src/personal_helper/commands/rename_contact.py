from personal_helper.commands.base_command import AddressBookCommand
from personal_helper.core.data import parse_options
from personal_helper.core.decorators import input_error
from personal_helper.models.book import AddressBook


class RenameContactCommand(AddressBookCommand):
    def get_command_name(self) -> str:
        return "rename-contact"

    def get_description(self) -> str:
        return "rename a contact"

    def get_usage(self) -> str:
        return "rename-contact --name <current name> --new-name <new name>"

    @input_error
    def run_with_address_book(
        self, args: list, address_book: AddressBook
    ) -> str:
        required = {"--name", "--new-name"}
        options = parse_options(args, required, required, self.get_usage())
        name = " ".join(options["--name"])
        new_name = " ".join(options["--new-name"])
        original = address_book[name]
        replacement = address_book.rename(name, new_name)
        if replacement is original:
            return f"Contact '{original.name.value}' unchanged."
        return (
            f"✅ Contact '{original.name.value}' renamed to "
            f"'{replacement.name.value}'."
        )
