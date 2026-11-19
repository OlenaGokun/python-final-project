from address_book.commands.base_command import BaseCommand, ExitRequest
from address_book.models.book import AddressBook


class ExitCommand(BaseCommand):
    """Command that requests application shutdown."""

    def get_command_name(self) -> str:
        return "close"

    def get_aliases(self) -> tuple[str, ...]:
        return ("exit",)

    def get_description(self) -> str:
        return "quit the program and save data"

    def get_usage(self) -> str:
        return "close | exit"

    def run(self, args: list, book: AddressBook) -> ExitRequest:
        return ExitRequest()
