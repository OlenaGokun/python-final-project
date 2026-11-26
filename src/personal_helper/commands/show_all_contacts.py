from personal_helper.models.book import AddressBook
from personal_helper.commands.base_command import AddressBookCommand


class ShowAllContactsCommand(AddressBookCommand):
    """Command to show all contacts in the address book"""

    def get_command_name(self) -> str:
        return "show-all-contacts"

    def get_description(self) -> str:
        return "show all contacts in address book"

    def get_usage(self) -> str:
        return "show-all-contacts"

    def run_with_address_book(
        self, args: list, address_book: AddressBook
    ) -> str:
        if not address_book.data:
            return "ℹ️  No contacts found."
        return self.format_contacts_compact(list(address_book.data.values()))
