"""Unit tests for address book commands"""

from personal_helper.models import PersonalHelper
from personal_helper.commands.base_command import BaseCommand, CommandLookup
from personal_helper.commands.hello import HelloCommand
from personal_helper.commands.help import HelpCommand

# ============================================================================
# ADD COMMAND TESTS
# ============================================================================


class TestHelpCommand:
    """Tests for help command"""

    def test_help_before_registration_reports_unexpected_error(
        self, data, monkeypatch
    ):
        monkeypatch.setattr("sys.stdout.isatty", lambda: False)

        result = HelpCommand().run([], data)

        assert result == (
            "⚠️ Unexpected error: HelpCommand must be registered "
            "before it can run"
        )

    def test_help_all_commands(self, registry, book):
        """Test help without arguments"""
        cmd = registry.get_command("help")
        result = cmd.run([], PersonalHelper(book))

        assert cmd._registry is registry
        assert "📚" in result
        assert "Available Commands" in result
        assert "add-contact" in result
        assert "show-contact" in result

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
        assert "How can I help you?" in registry.get_command("hello").run(
            [], PersonalHelper(book)
        )

    def test_help_exit_command(self, registry, book):
        result = registry.get_command("help").run(
            ["--command", "exit"], PersonalHelper(book)
        )

        assert "Help for 'exit' command" in result
        assert "Usage:       exit" in result

    def test_help_rejects_positional_and_duplicate_options(
        self, registry, book
    ):
        cmd = registry.get_command("help")
        for args in (
            ["add-contact"],
            ["--command"],
            ["--command", "add-contact", "--command", "exit"],
        ):
            assert cmd.run(args, PersonalHelper(book)).startswith(
                "❌ Invalid arguments."
            )


def test_help_uses_an_alternative_command_lookup(data):
    class FakeLookup:
        def __init__(self) -> None:
            self.command = HelloCommand()

        def get_command(self, name: str) -> BaseCommand | None:
            return self.command if name == "hello" else None

        def get_all_commands(self) -> list[BaseCommand]:
            return [self.command]

    lookup: CommandLookup = FakeLookup()
    command = HelpCommand()
    command.set_registry(lookup)

    assert "hello" in command.run([], data)
    assert "Usage:       hello" in command.run(["--command", "hello"], data)
    assert "Unknown command" in command.run(["--command", "missing"], data)


# ============================================================================
# FACTORY TESTS
# ============================================================================
