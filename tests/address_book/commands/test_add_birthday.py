"""Unit tests for address book commands"""

import pytest
from address_book.models.book import AddressBook
from address_book.models.record import Record
from address_book.command_registry import CommandRegistry
from address_book.core.exceptions import InvalidInputError, CommandError

# ============================================================================
# ADD COMMAND TESTS
# ============================================================================

class TestAddBirthdayCommand:
    """Tests for add-birthday command"""

    def test_add_birthday(self, registry, book_with_contacts):
        """Test adding birthday"""
        cmd = registry.get_command("add-birthday")
        result = cmd.run(["Alice", "15.06.1992"], book_with_contacts)

        assert "✅ Birthday added." in result
        alice = book_with_contacts["Alice"]
        assert alice.birthday is not None

    def test_add_birthday_missing_name(self, registry, book):
        """Test add-birthday with missing name"""
        cmd = registry.get_command("add-birthday")
        result = cmd.run([], book)

        assert "❌" in result
        assert "Invalid arguments" in result

    def test_add_birthday_missing_date(self, registry, book_with_contacts):
        """Test add-birthday with missing date"""
        cmd = registry.get_command("add-birthday")
        result = cmd.run(["John"], book_with_contacts)

        assert "❌" in result
        assert "Invalid arguments" in result

    def test_add_birthday_nonexistent_contact(self, registry, book):
        """Test adding birthday to non-existent contact"""
        cmd = registry.get_command("add-birthday")
        result = cmd.run(["Nonexistent", "01.01.2000"], book)

        assert "❌" in result
        assert "not found" in result

# ============================================================================
# CHANGE COMMAND TESTS
# ============================================================================

