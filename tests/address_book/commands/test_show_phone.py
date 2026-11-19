"""Unit tests for address book commands"""

import pytest
from address_book.models.book import AddressBook
from address_book.models.record import Record
from address_book.command_registry import CommandRegistry
from address_book.core.exceptions import InvalidInputError, CommandError

# ============================================================================
# ADD COMMAND TESTS
# ============================================================================

class TestShowPhoneCommand:
    """Tests for phone command"""

    def test_show_phone(self, registry, book_with_contacts):
        """Test showing phone number"""
        cmd = registry.get_command("phone")
        result = cmd.run(["John"], book_with_contacts)

        assert "5012345671" in result

    def test_show_phone_multiple(self, registry, book_with_contacts):
        """Test showing multiple phones"""
        cmd = registry.get_command("phone")
        john = book_with_contacts["John"]
        john.add_phone("5099999999")  # 10 digits as string

        result = cmd.run(["John"], book_with_contacts)

        assert "5012345671" in result
        assert "5099999999" in result

    def test_show_phone_no_phones(self, registry, book):
        """Test showing phone when contact has no phones"""
        record = Record("Bob")
        book.add_record(record)

        cmd = registry.get_command("phone")
        result = cmd.run(["Bob"], book)

        assert "ℹ️" in result
        assert "No phone numbers" in result

    def test_show_phone_missing_name(self, registry, book):
        """Test phone command without name"""
        cmd = registry.get_command("phone")
        result = cmd.run([], book)

        assert "❌" in result
        assert "Invalid arguments" in result

    def test_show_phone_nonexistent_contact(self, registry, book):
        """Test showing phone for non-existent contact"""
        cmd = registry.get_command("phone")
        result = cmd.run(["Nonexistent"], book)

        assert "❌" in result

# ============================================================================
# SHOW BIRTHDAY COMMAND TESTS
# ============================================================================

