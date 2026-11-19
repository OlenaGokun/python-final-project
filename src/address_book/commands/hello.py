from address_book.commands.base_command import BaseCommand
from address_book.models.book import AddressBook


class HelloCommand(BaseCommand):
    """Command that greets the user."""

    def get_command_name(self) -> str:
        return "hello"

    def get_description(self) -> str:
        return "get a greeting from the bot"

    def get_usage(self) -> str:
        return "hello"

    def run(self, args: list, book: AddressBook) -> str:
        return "How can I help you?"
