"""Unit tests for address book commands"""

from colorama import Fore, Style

from personal_helper.core import formatting
from personal_helper.models import PersonalHelper
from personal_helper.models.record import Record

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
        assert len(result.splitlines()) == 2

    def test_show_all_contacts_uses_one_line_per_contact(self, registry, book):
        record = Record("James Webb")
        record.add_phone("0665556655", "main")
        record.add_phone("0976664466", "home")
        record.add_email("jane@example.com")
        record.add_address("Main st. 5")
        record.add_birthday("21.11.2006")
        book.add_record(record)
        book.add_record(Record("Jane Doe"))

        result = registry.get_command("show-all-contacts").run(
            [], PersonalHelper(book)
        )

        assert result == (
            "James Webb: 📞 main 0665556655, home 0976664466; "
            "✉️ jane@example.com; 🏠 Main st. 5; 🎂 21.11.2006\n"
            "Jane Doe: 📞 —; ✉️ —; 🏠 —; 🎂 —"
        )

    def test_compact_contact_colors_names_and_aliases_in_terminal(
        self, registry, book, monkeypatch
    ):
        class Terminal:
            @staticmethod
            def isatty():
                return True

        record = book.add_record(Record("Jane"))
        record.add_phone("0505055500", "main")
        monkeypatch.setattr(formatting.sys, "stdout", Terminal())

        result = registry.get_command("show-all-contacts").run(
            [], PersonalHelper(book)
        )

        assert f"{Fore.BLUE}{Style.BRIGHT}Jane:{Style.RESET_ALL}" in result
        assert f"{Fore.BLUE}main{Style.RESET_ALL} 0505055500" in result


def test_show_all_notes_empty(registry, data):
    result = registry.get_command("show-all-notes").run([], data)

    assert result == "ℹ️  No notes found."


def test_show_all_notes_lists_note_titles_and_text(registry, data):
    data.notebook.add("Shopping", "Buy milk", {"food", "home"})
    data.notebook.add("Plans", "Call tomorrow")

    result = registry.get_command("show-all-notes").run([], data)

    assert result == (
        "Shopping: Buy milk [tags: food, home]\nPlans: Call tomorrow"
    )


# ============================================================================
# SHOW BIRTHDAYS COMMAND TESTS
# ============================================================================
