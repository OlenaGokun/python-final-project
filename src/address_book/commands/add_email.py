from address_book.book import AddressBook
from address_book.decorators import input_error


@input_error
def add_email(args: list[str], book: AddressBook) -> str:
    if len(args) < 2:
        raise ValueError("Invalid arguments. Usage: add-email <name> <email>")

    name, email = args[0], args[1]
    record = book.find(name)
    if record is None:
        return f"Contact '{name}' not found."

    record.add_email(email)
    return f"Email added for {record.name.value}."