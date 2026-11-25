import io

from colorama import Fore, Style

from personal_helper.core import formatting
from personal_helper.core.decorators import input_error


class Terminal(io.StringIO):
    def isatty(self):
        return True


def test_command_errors_are_red_in_terminal(registry, data, monkeypatch):
    monkeypatch.setattr(formatting.sys, "stdout", Terminal())

    result = registry.get_command("search-notes").run([], data)

    assert result.startswith(f"{Fore.RED}❌ Invalid arguments.")
    assert "Usage: search-notes" in result
    assert result.endswith(Style.RESET_ALL)


def test_unexpected_error_is_red_in_terminal(monkeypatch):
    monkeypatch.setattr(formatting.sys, "stdout", Terminal())

    @input_error
    def fail():
        raise RuntimeError("broken")

    assert fail() == f"{Fore.RED}⚠️ Unexpected error: broken{Style.RESET_ALL}"


def test_unknown_help_command_is_red_in_terminal(registry, data, monkeypatch):
    monkeypatch.setattr(formatting.sys, "stdout", Terminal())

    result = registry.get_command("help").run(["--command", "missing"], data)

    assert result == (
        f"{Fore.RED}❌ Unknown command: 'missing'. "
        f"Use 'help' to see all commands.{Style.RESET_ALL}"
    )


def test_error_message_has_no_escape_codes_when_redirected(monkeypatch):
    monkeypatch.setattr(formatting.sys, "stdout", io.StringIO())

    assert formatting.error_message("❌ Invalid input") == "❌ Invalid input"
