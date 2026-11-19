from __future__ import annotations

from typing import TYPE_CHECKING

from address_book.models.book import AddressBook
from address_book.commands.base_command import BaseCommand

if TYPE_CHECKING:
    from address_book.command_registry import CommandRegistry


class HelpCommand(BaseCommand):
    """Command to show help for all or specific command"""

    def __init__(self) -> None:
        self._registry: CommandRegistry | None = None

    def get_command_name(self) -> str:
        return "help"

    def get_description(self) -> str:
        return "show help for all or specific command"

    def get_usage(self) -> str:
        return "help [command]"

    def set_registry(self, registry: CommandRegistry) -> None:
        self._registry = registry

    def run(self, args: list, book: AddressBook) -> str:
        if self._registry is None:
            raise RuntimeError("HelpCommand must be registered before it can run")

        if not args:
            return self._show_all_help(self._registry)
        command_name = args[0]
        return self._show_command_help(self._registry, command_name)

    def _show_all_help(self, registry: CommandRegistry) -> str:
        """Show help for all commands"""
        result = ["📚 Available Commands:\n"]

        result.append("ℹ️  Commands:")
        for cmd in sorted(registry.get_all_commands(), key=lambda c: c.get_command_name()):
            usage = cmd.get_usage()
            desc = cmd.get_description()
            result.append(f"  {usage.ljust(35)} - {desc}")

        result.append("")
        result.append("💡 Tip: Use 'help <command>' for detailed help on a specific command")

        return "\n".join(result)

    def _show_command_help(
        self, registry: CommandRegistry, command_name: str
    ) -> str:
        """Show detailed help for a specific command"""
        cmd = registry.get_command(command_name)

        if not cmd:
            return f"❌ Unknown command: '{command_name}'. Use 'help' to see all commands."

        result = [f"📖 Help for '{cmd.get_command_name()}' command:\n"]
        result.append(f"Description: {cmd.get_description()}")
        result.append(f"Usage:       {cmd.get_usage()}")
        result.append("")

        return "\n".join(result)
