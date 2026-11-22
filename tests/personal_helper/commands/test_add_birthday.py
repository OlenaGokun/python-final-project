"""Unit tests for address book commands"""

import pytest
from personal_helper.models import PersonalHelper
from personal_helper.models.book import AddressBook
from personal_helper.models.record import Record
from personal_helper.command_registry import CommandRegistry
from personal_helper.core.exceptions import InvalidInputError, CommandError

# ============================================================================
# ADD COMMAND TESTS
# ============================================================================

class TestAddBirthdayCommand:
    """Tests for add-birthday command"""

    def test_add_birthday(self, registry, book_with_contacts):
        """Test adding birthday"""
        cmd = registry.get_command("add-birthday")
        result = cmd.run(["--name", "Alice", "--birthday", "15.06.1992"], PersonalHelper(book_with_contacts))

        assert result == "✅ Birthday added for Alice."
        alice = book_with_contacts["Alice"]
        assert alice.birthday is not None

    def test_add_birthday_missing_name(self, registry, book):
        """Test add-birthday with missing name"""
        cmd = registry.get_command("add-birthday")
        result = cmd.run([], PersonalHelper(book))

        assert "❌" in result
        assert "Invalid arguments" in result

    def test_add_birthday_missing_date(self, registry, book_with_contacts):
        """Test add-birthday with missing date"""
        cmd = registry.get_command("add-birthday")
        result = cmd.run(["--name", "John"], PersonalHelper(book_with_contacts))

        assert "❌" in result
        assert "Invalid arguments" in result

    def test_add_birthday_nonexistent_contact(self, registry, book):
        """Test adding birthday to non-existent contact"""
        cmd = registry.get_command("add-birthday")
        result = cmd.run(["--name", "Nonexistent", "--birthday", "01.01.2000"], PersonalHelper(book))

        assert "❌" in result
        assert "not found" in result

# ============================================================================
# CHANGE COMMAND TESTS
# ============================================================================
