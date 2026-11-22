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

class TestShowAllContactsCommand:
    """Tests for show-all-contacts command"""

    def test_show_all_empty(self, registry, book):
        """Test showing all when book is empty"""
        cmd = registry.get_command("show-all-contacts")
        result = cmd.run([], PersonalHelper(book))

        assert result == "ℹ️  No contacts found."

    def test_show_all_with_contacts(self, registry, book_with_contacts):
        """Test showing all contacts"""
        cmd = registry.get_command("show-all-contacts")
        result = cmd.run([], PersonalHelper(book_with_contacts))

        assert "John" in result
        assert "Alice" in result
        assert "5012345671" in result


def test_show_all_notes_empty(registry, data):
    result = registry.get_command("show-all-notes").run([], data)

    assert result == "ℹ️  No notes found."


def test_show_all_notes_lists_note_titles_and_text(registry, data):
    data.notebook.add("Shopping", "Buy milk")
    data.notebook.add("Plans", "Call tomorrow")

    result = registry.get_command("show-all-notes").run([], data)

    assert result == "Shopping: Buy milk\nPlans: Call tomorrow"

# ============================================================================
# SHOW BIRTHDAYS COMMAND TESTS
# ============================================================================
