from address_book.core.decorators import input_error
from address_book.models.book import AddressBook
from address_book.models.record import Record
from address_book.commands.base_command import BaseCommand
from address_book.core.exceptions import InvalidInputError


class AddContact(BaseCommand):
    """Command to add contact or update an existing one"""

    def get_command_name(self) -> str:
        return "add"

    def get_description(self) -> str:
        return "add a contact or update an existing one"

    def get_usage(self) -> str:
        return "add <name> [phone]"

    @input_error
    def run(self, args: list, book: AddressBook) -> str:
        if len(args) not in (1, 2):
            raise InvalidInputError(
                f"Invalid arguments.\n"
                f"Usage: {self.get_usage()}\n"
                f"Examples:\n"
                f"  add John\n"
                f"  add John 0501234567"
            )
        name, *rest = args
        phone = rest[0] if rest else None

        record = book.find(name)
        if record is None:
            # Validate the phone before creating the contact, so a bad phone
            # doesn't leave a half-added contact behind.
            record = Record(name)
            if phone:
                record.add_phone(phone)
            book.add_record(record)
            return "✅ Contact added."
        if phone:
            record.add_phone(phone)
        return "✅ Contact updated."
