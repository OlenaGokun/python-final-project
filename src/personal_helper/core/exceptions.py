"""Custom exceptions for address book commands with user-friendly messages"""


class CommandError(Exception):
    """Base exception for command errors with user-friendly messages"""
    pass


class InvalidInputError(CommandError):
    """Raised when input format is invalid"""
    pass


class InvalidNameError(CommandError):
    """Raised when name is invalid (empty or non-string)"""
    pass


class InvalidPhoneFormatError(CommandError):
    """Raised when phone format is invalid"""
    pass


class InvalidBirthdayFormatError(CommandError):
    """Raised when birthday format is invalid"""
    pass


class ContactNotFoundError(CommandError):
    """Raised when a contact is not found"""
    pass


class DuplicateContactError(CommandError):
    """Raised when trying to add a contact that already exists"""
    pass


class PhoneNotFoundError(CommandError):
    """Raised when a phone is not found in a contact"""
    pass


class DuplicatePhoneError(CommandError):
    """Raised when trying to add a phone that already exists in a contact"""
    pass


class InvalidNoteError(CommandError):
    """Raised when a note is invalid"""
    pass


class NoteAlreadyExistsError(CommandError):
    """Raised when a note title is already in use"""
    pass


class NoteNotFoundError(CommandError):
    """Raised when trying to update or delete a missing note"""
    pass
