"""Address Book - A command-line contact management application

A professional contact management system with birthday tracking and
command-based interface using the Registry pattern for extensibility.
"""

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

__version__ = "1.0.0"

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


