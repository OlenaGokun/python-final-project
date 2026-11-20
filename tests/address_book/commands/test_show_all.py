"""Unit tests for address book commands"""

import pytest
from address_book.models.book import AddressBook
from address_book.models.record import Record
from address_book.command_registry import CommandRegistry
from address_book.core.exceptions import InvalidInputError, CommandError

# ============================================================================
# ADD COMMAND TESTS
# ============================================================================

class TestShowAllCommand:
    """Tests for all command"""

    def test_show_all_empty(self, registry, book):
        """Test showing all when book is empty"""
        cmd = registry.get_command("all")
        result = cmd.run([], book)

        assert "ℹ️" in result
        assert "No contacts found" in result

    def test_show_all_with_contacts(self, registry, book_with_contacts):
        """Test showing all contacts"""
        cmd = registry.get_command("all")
        result = cmd.run([], book_with_contacts)

        assert "John" in result
        assert "Alice" in result
        assert "5012345671" in result

# ============================================================================
# SHOW BIRTHDAYS COMMAND TESTS
# ============================================================================

