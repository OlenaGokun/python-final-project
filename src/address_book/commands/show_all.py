from address_book.models.book import AddressBook
from address_book.commands.base_command import BaseCommand


class ShowAllCommand(BaseCommand):
    """Command to show all contacts in the address book"""

    def get_command_name(self) -> str:
        return "all"

    def get_description(self) -> str:
        return "show all contacts in address book"

    def get_usage(self) -> str:
        return "all"

    def run(self, args: list, book: AddressBook) -> str:
        if not book.data:
            return "ℹ️  No contacts found. Use 'add <name>' to add a new contact."
        return "\n".join(str(record) for record in book.data.values())
