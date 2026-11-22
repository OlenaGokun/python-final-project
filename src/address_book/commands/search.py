from address_book.book import AddressBook
from address_book.decorators import input_error


@input_error
def search_contacts(args: list[str], book: AddressBook) -> str:
    if not args:
        raise ValueError("Invalid arguments. Usage: search <query>")

    query = " ".join(args)
    matches = book.search(query)

    if not matches:
        return f"No contacts found matching '{query}'."

    return "\n".join(str(record) for record in matches)