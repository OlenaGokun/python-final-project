from personal_helper.models.book import AddressBook
from personal_helper.commands.base_command import AddressBookCommand


class ShowBirthdaysCommand(AddressBookCommand):
    """Command to show upcoming birthdays in the next 7 days"""

    def get_command_name(self) -> str:
        return "birthdays"

    def get_description(self) -> str:
        return "show upcoming birthdays in the next 7 days"

    def get_usage(self) -> str:
        return "birthdays"

    def run_with_address_book(self, args: list, address_book: AddressBook) -> str:
        upcoming = address_book.get_upcoming_birthdays()
        if not upcoming:
            return "ℹ️  No upcoming birthdays in the next 7 days."
        result = []
        for contact in upcoming:
            result.append(f"🎂 {contact['name']}: {contact['congratulation_date']}")
        return "\n".join(result)
