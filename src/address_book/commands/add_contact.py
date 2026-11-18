from address_book.decorators import input_error
from address_book.book import AddressBook
from address_book.record import Record


@input_error
def add_contact(args, book: AddressBook):
    if len(args) not in (1, 2):
        raise ValueError("Usage: add <name> [phone]")
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
        return "Contact added."
    if phone:
        record.add_phone(phone)
    return "Contact updated."
