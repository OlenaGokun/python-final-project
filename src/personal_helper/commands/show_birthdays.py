from personal_helper.commands.base_command import AddressBookCommand
from personal_helper.core.data import parse_options
from personal_helper.core.decorators import input_error
from personal_helper.core.exceptions import InvalidInputError
from personal_helper.models.book import (
    AddressBook,
    DEFAULT_BIRTHDAY_WINDOW_DAYS,
)


class ShowBirthdaysCommand(AddressBookCommand):
    """Command to show upcoming birthdays within a configurable window."""

    def get_command_name(self) -> str:
        return "show-birthdays"

    def get_description(self) -> str:
        return "show upcoming birthdays in the next 1 to 365 days (default: 7)"

    def get_usage(self) -> str:
        return "show-birthdays [--days <days>]"

    @input_error
    def run_with_address_book(
        self, args: list, address_book: AddressBook
    ) -> str:
        options = parse_options(
            args, {"--days"}, set(), self.get_usage(), {"--days"}
        )
        days = DEFAULT_BIRTHDAY_WINDOW_DAYS
        if "--days" in options:
            error_message = (
                "Invalid arguments. --days must be an integer from 1 to 365.\n"
                f"Usage: {self.get_usage()}"
            )
            try:
                days = int(options["--days"][0])
            except ValueError:
                raise InvalidInputError(error_message) from None
            if not 1 <= days <= 365:
                raise InvalidInputError(error_message)

        upcoming = address_book.get_upcoming_birthdays(days)
        if not upcoming:
            if days == 1:
                return "ℹ️  No upcoming birthdays in the next day."
            return f"ℹ️  No upcoming birthdays in the next {days} days."
        result = []
        for contact in upcoming:
            result.append(
                f"🎂 {contact['name']}: {contact['congratulation_date']}"
            )
        return "\n".join(result)
