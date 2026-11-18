from address_book.decorators import input_error
from address_book.book import AddressBook


@input_error
def show_birthday(args, book: AddressBook):
    if len(args) != 1:
        raise ValueError("Usage: show-birthday <name>")
    record = book[args[0]]
    if record.birthday is None:
        return f"{record.name.value} has no birthday set."
    return f"{record.name.value}'s birthday: {record.birthday}"
