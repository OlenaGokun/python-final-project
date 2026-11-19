"""Unit tests for address book commands"""

import pytest
from address_book.models.book import AddressBook
from address_book.models.record import Record
from address_book.command_registry import CommandRegistry
from address_book.core.exceptions import InvalidInputError, CommandError

# ============================================================================
# ADD COMMAND TESTS
# ============================================================================

class TestAddCommand:
    """Tests for add command"""

    def test_add_new_contact(self, registry, book):
        """Test adding a new contact"""
        cmd = registry.get_command("add")
        result = cmd.run(["John", "5012345671"], book)

        assert "✅ Contact added." in result
        assert "john" in book.data  # Keys are stored lowercase

    def test_add_contact_without_phone(self, registry, book):
        """Test adding contact without phone"""
        cmd = registry.get_command("add")
        result = cmd.run(["Alice"], book)

        assert "✅ Contact added." in result
        assert "alice" in book.data  # Keys are stored lowercase

    def test_add_phone_to_existing_contact(self, registry, book_with_contacts):
        """Test adding phone to existing contact"""
        cmd = registry.get_command("add")
        result = cmd.run(["John", "0559999999"], book_with_contacts)

        assert "✅ Contact updated." in result

    def test_existing_contact_without_phone_is_unchanged(
        self, registry, book_with_contacts
    ):
        """Adding an existing name without a phone should not alter its phones."""
        cmd = registry.get_command("add")
        record = book_with_contacts.find("John")
        original_phones = record.phones

        result = cmd.run(["John"], book_with_contacts)

        assert result == "✅ Contact updated."
        assert record.phones == original_phones

    def test_add_with_no_arguments(self, registry, book):
        """Test add command with no arguments"""
        cmd = registry.get_command("add")
        result = cmd.run([], book)

        assert "❌" in result
        assert "Invalid arguments" in result
        assert "Usage:" in result

    def test_add_with_too_many_arguments(self, registry, book):
        """Test add command with too many arguments"""
        cmd = registry.get_command("add")
        result = cmd.run(["John", "phone1", "phone2"], book)

        assert "❌" in result
        assert "Invalid arguments" in result

# ============================================================================
# ADD BIRTHDAY COMMAND TESTS
# ============================================================================
