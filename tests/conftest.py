"""Shared pytest fixtures for all tests"""

import pytest
from address_book.models import AddressBook, Record
from address_book.command_registry import CommandRegistry


@pytest.fixture
def book():
    """Create a fresh address book for each test"""
    return AddressBook()


@pytest.fixture
def registry():
    """Create command registry"""
    return CommandRegistry()


@pytest.fixture
def book_with_contacts(book):
    """Create book with sample data"""
    record1 = Record("John")
    record1.add_phone("5012345671")  # 10 digits as string
    record1.add_birthday("25.12.1990")
    book.add_record(record1)

    record2 = Record("Alice")
    record2.add_phone("5098765432")  # 10 digits as string
    book.add_record(record2)

    return book
