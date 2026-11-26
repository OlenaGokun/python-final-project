from .book import AddressBook
from .notes import Notebook


class PersonalHelper:
    """Application data for independent contacts and notes."""

    def __init__(
        self,
        address_book: AddressBook | None = None,
        notebook: Notebook | None = None,
    ):
        self.address_book = (
            address_book if address_book is not None else AddressBook()
        )
        self.notebook = notebook if notebook is not None else Notebook()
