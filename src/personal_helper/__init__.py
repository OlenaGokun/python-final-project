"""Personal Helper Bot's address book and command system."""

# Domain models
from personal_helper.models import AddressBook, Record, Field, Name, Phone, Birthday, Email

# Commands
from personal_helper.command_registry import CommandRegistry

# Infrastructure
from personal_helper.core import (
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
    "Email",
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
