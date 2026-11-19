"""Personal Helper Bot's address book and command system."""

# Domain models
from address_book.models import AddressBook, Record, Field, Name, Phone, Birthday

# Commands
from address_book.command_registry import CommandRegistry

# Infrastructure
from address_book.core import (
    parse_input,
    input_error,
    InvalidInputError,
    InvalidNameError,
    InvalidPhoneFormatError,
    InvalidBirthdayFormatError,
    ContactNotFoundError,
    DuplicateContactError,
    PhoneNotFoundError,
    DuplicatePhoneError,
    CommandError,
)

__all__ = [
    # Models
    "AddressBook",
    "Record",
    "Field",
    "Name",
    "Phone",
    "Birthday",
    # Commands
    "CommandRegistry",
    # Infrastructure
    "parse_input",
    "input_error",
    "InvalidInputError",
    "InvalidNameError",
    "InvalidPhoneFormatError",
    "InvalidBirthdayFormatError",
    "ContactNotFoundError",
    "DuplicateContactError",
    "PhoneNotFoundError",
    "DuplicatePhoneError",
    "CommandError",
]
