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

class TestHelpCommand:
    """Tests for help command"""

    def test_help_all_commands(self, registry, book):
        """Test help without arguments"""
        cmd = registry.get_command("help")
        result = cmd.run([], PersonalHelper(book))

        assert cmd._registry is registry
        assert "📚" in result
        assert "Available Commands" in result
        assert "add-contact" in result
        assert "phone" in result

    def test_help_specific_command(self, registry, book):
        """Test help for specific command"""
        cmd = registry.get_command("help")
        result = cmd.run(["--command", "add-contact"], PersonalHelper(book))

        assert "📖" in result
        assert "Description:" in result
        assert "Usage:" in result

    def test_help_nonexistent_command(self, registry, book):
        """Test help for non-existent command"""
        cmd = registry.get_command("help")
        result = cmd.run(["--command", "nonexistent"], PersonalHelper(book))

        assert "❌" in result
        assert "Unknown command" in result

    def test_help_static_command(self, registry, book):
        """Test help for a built-in registry command."""
        cmd = registry.get_command("help")
        result = cmd.run(["--command", "hello"], PersonalHelper(book))

        assert "📖" in result
        assert "How can I help you?" in registry.get_command("hello").run([], PersonalHelper(book))

    def test_help_exit_command(self, registry, book):
        result = registry.get_command("help").run(["--command", "exit"], PersonalHelper(book))

        assert "Help for 'exit' command" in result
        assert "Usage:       exit" in result

    def test_help_rejects_positional_and_duplicate_options(self, registry, book):
        cmd = registry.get_command("help")
        for args in (["add-contact"], ["--command"], ["--command", "add-contact", "--command", "exit"]):
            assert cmd.run(args, PersonalHelper(book)).startswith("❌ Invalid arguments.")

# ============================================================================
# FACTORY TESTS
# ============================================================================
