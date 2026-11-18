from address_book.decorators import input_error
from address_book.book import AddressBook


@input_error
def add_birthday(args, book: AddressBook):
    if len(args) != 2:
        raise ValueError("Usage: add-birthday <name> <DD.MM.YYYY>")
    name, birthday = args
    record = book[name]
    record.add_birthday(birthday)
    return "Birthday added."
