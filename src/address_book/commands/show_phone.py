from address_book.decorators import input_error
from address_book.book import AddressBook


@input_error
def show_phone(args, book: AddressBook):
    if len(args) != 1:
        raise ValueError("Usage: phone <name>")
    record = book[args[0]]
    if not record.phones:
        return f"No phone numbers found for {record.name.value}."
    return "; ".join(p.value for p in record.phones)
