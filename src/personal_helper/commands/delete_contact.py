from personal_helper.commands.base_command import AddressBookCommand
from personal_helper.core.data import parse_options
from personal_helper.core.decorators import input_error
from personal_helper.core.formatting import error_message
from personal_helper.models.book import AddressBook


class DeleteContactCommand(AddressBookCommand):
    def get_command_name(self) -> str:
        return "delete-contact"

    def get_description(self) -> str:
        return "delete a contact after confirmation"

    def get_usage(self) -> str:
        return "delete-contact --name <contact name>"

    @input_error
    def run_with_address_book(self, args: list, address_book: AddressBook) -> str:
        required = {"--name"}
        options = parse_options(args, required, required, self.get_usage())
        name = " ".join(options["--name"])
        contact = address_book[name]
        display_name = contact.name.value

        while True:
            try:
                answer = input(f"Delete contact '{display_name}'? (Y)es/(N)o: ")
            except (EOFError, KeyboardInterrupt):
                return "Contact deletion canceled."

            answer = answer.strip().casefold()
            if answer in ("y", "yes"):
                address_book.delete(name)
                return f"✅ Contact '{display_name}' deleted."
            if answer in ("n", "no"):
                return "Contact deletion canceled."
            print(error_message("Please enter yes or no."))
