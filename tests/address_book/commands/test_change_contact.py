"""Unit tests for address book commands"""

import pytest
from address_book.models.book import AddressBook
from address_book.models.record import Record
from address_book.command_registry import CommandRegistry
from address_book.core.exceptions import InvalidInputError, CommandError

# ============================================================================
# ADD COMMAND TESTS
# ============================================================================

class TestChangeCommand:
    """Tests for change command"""

    def test_change_phone(self, registry, book_with_contacts):
        """Test changing phone number"""
        cmd = registry.get_command("change")
        result = cmd.run(["John", "5012345671", "5099999999"], book_with_contacts)

        assert "✅ Contact updated." in result

    def test_change_phone_missing_arguments(self, registry, book_with_contacts):
        """Test change with missing arguments"""
        cmd = registry.get_command("change")
        result = cmd.run(["John"], book_with_contacts)

        assert "❌" in result
        assert "Invalid arguments" in result

    def test_change_phone_nonexistent_contact(self, registry, book):
        """Test changing phone for non-existent contact"""
        cmd = registry.get_command("change")
        result = cmd.run(["Nonexistent", "123", "456"], book)

        assert "❌" in result

# ============================================================================
# SHOW PHONE COMMAND TESTS
# ============================================================================

