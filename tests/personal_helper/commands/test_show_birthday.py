"""Unit tests for address book commands"""

from personal_helper.models import PersonalHelper

# ============================================================================
# ADD COMMAND TESTS
# ============================================================================


class TestShowBirthdayCommand:
    """Tests for show-birthday command"""

    def test_show_birthday(self, registry, book_with_contacts):
        """Test showing birthday"""
        cmd = registry.get_command("show-birthday")
        result = cmd.run(
            ["--name", "John"], PersonalHelper(book_with_contacts)
        )

        assert "🎂" in result
        assert "25.12.1990" in result

    def test_show_birthday_not_set(self, registry, book_with_contacts):
        """Test showing birthday when not set"""
        cmd = registry.get_command("show-birthday")
        result = cmd.run(
            ["--name", "Alice"], PersonalHelper(book_with_contacts)
        )

        assert "ℹ️" in result
        assert "has no birthday set" in result

    def test_show_birthday_missing_name(self, registry, book):
        """Test show-birthday without name"""
        cmd = registry.get_command("show-birthday")
        result = cmd.run([], PersonalHelper(book))

        assert "❌" in result
        assert "Invalid arguments" in result

    def test_show_birthday_nonexistent_contact(self, registry, book):
        """Test showing birthday for non-existent contact"""
        cmd = registry.get_command("show-birthday")
        result = cmd.run(["--name", "Nonexistent"], PersonalHelper(book))

        assert "❌" in result


# ============================================================================
# SHOW ALL COMMAND TESTS
# ============================================================================
