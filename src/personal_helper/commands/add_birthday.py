from personal_helper.core.decorators import input_error
from personal_helper.models.book import AddressBook
from personal_helper.commands.base_command import AddressBookCommand
from personal_helper.core.data import parse_options


class AddBirthdayCommand(AddressBookCommand):
    """Command to add birthday for a contact"""

    def get_command_name(self) -> str:
        return "add-birthday"

    def get_description(self) -> str:
        return "add a birthday for a contact"

    def get_usage(self) -> str:
        return "add-birthday --name <name> --birthday <DD.MM.YYYY>"

    @input_error
    def run_with_address_book(self, args: list, address_book: AddressBook) -> str:
        required = {"--name", "--birthday"}
        options = parse_options(args, required, required, self.get_usage(), {"--birthday"})
        name, birthday = " ".join(options["--name"]), options["--birthday"][0]
        record = address_book[name]
        record.add_birthday(birthday)
        return f"✅ Birthday added for {record.name.value}."
