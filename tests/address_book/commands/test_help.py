"""Unit tests for address book commands"""

import pytest
from address_book.models.book import AddressBook
from address_book.models.record import Record
from address_book.command_registry import CommandRegistry
from address_book.core.exceptions import InvalidInputError, CommandError

# ============================================================================
# ADD COMMAND TESTS
# ============================================================================

class TestHelpCommand:
    """Tests for help command"""

    def test_help_all_commands(self, registry, book):
        """Test help without arguments"""
        cmd = registry.get_command("help")
        result = cmd.run([], book)

        assert cmd._registry is registry
        assert "📚" in result
        assert "Available Commands" in result
        assert "add" in result
        assert "phone" in result

    def test_help_specific_command(self, registry, book):
        """Test help for specific command"""
        cmd = registry.get_command("help")
        result = cmd.run(["add"], book)

        assert "📖" in result
        assert "Description:" in result
        assert "Usage:" in result

    def test_help_nonexistent_command(self, registry, book):
        """Test help for non-existent command"""
        cmd = registry.get_command("help")
        result = cmd.run(["nonexistent"], book)

        assert "❌" in result
        assert "Unknown command" in result

    def test_help_static_command(self, registry, book):
        """Test help for a built-in registry command."""
        cmd = registry.get_command("help")
        result = cmd.run(["hello"], book)

        assert "📖" in result
        assert "How can I help you?" in registry.get_command("hello").run([], book)

    def test_help_exit_command(self, registry, book):
        result = registry.get_command("help").run(["exit"], book)

        assert "Help for 'exit' command" in result
        assert "Usage:       exit" in result

# ============================================================================
# FACTORY TESTS
# ============================================================================
