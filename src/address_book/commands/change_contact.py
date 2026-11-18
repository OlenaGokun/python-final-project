from address_book.decorators import input_error
from address_book.book import AddressBook


@input_error
def change_contact(args, book: AddressBook):
    if len(args) != 3:
        raise ValueError("Usage: change <name> <old_phone> <new_phone>")
    name, old_phone, new_phone = args
    record = book[name]
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."
