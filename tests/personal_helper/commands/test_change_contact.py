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

class TestChangeCommand:
    """Tests for change command"""

    def test_change_phone(self, registry, book_with_contacts):
        """Test changing phone number"""
        cmd = registry.get_command("change")
        result = cmd.run(["--name", "John", "--old-phone", "5012345671", "--new-phone", "5099999999"], PersonalHelper(book_with_contacts))

        assert result == "✅ Contact 'John' updated."

    def test_change_phone_missing_arguments(self, registry, book_with_contacts):
        """Test change with missing arguments"""
        cmd = registry.get_command("change")
        result = cmd.run(["--name", "John"], PersonalHelper(book_with_contacts))

        assert "❌" in result
        assert "Invalid arguments" in result

    def test_change_phone_nonexistent_contact(self, registry, book):
        """Test changing phone for non-existent contact"""
        cmd = registry.get_command("change")
        result = cmd.run(["--name", "Nonexistent", "--old-phone", "123", "--new-phone", "456"], PersonalHelper(book))

        assert "❌" in result

# ============================================================================
# SHOW PHONE COMMAND TESTS
# ============================================================================
