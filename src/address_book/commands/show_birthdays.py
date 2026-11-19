from address_book.models.book import AddressBook
from address_book.commands.base_command import BaseCommand


class ShowBirthdaysCommand(BaseCommand):
    """Command to show upcoming birthdays in the next 7 days"""

    def get_command_name(self) -> str:
        return "birthdays"

    def get_description(self) -> str:
        return "show upcoming birthdays in the next 7 days"

    def get_usage(self) -> str:
        return "birthdays"

    def run(self, args: list, book: AddressBook) -> str:
        upcoming = book.get_upcoming_birthdays()
        if not upcoming:
            return "ℹ️  No upcoming birthdays in the next 7 days."
        result = []
        for contact in upcoming:
            result.append(f"🎂 {contact['name']}: {contact['congratulation_date']}")
        return "\n".join(result)
