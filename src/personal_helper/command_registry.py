from collections.abc import ValuesView
import importlib
import inspect
import pkgutil

import personal_helper.commands as commands_module
from personal_helper.commands.base_command import BaseCommand


class CommandRegistry:
    """Registry that discovers and registers commands by scanning for BaseCommand subclasses"""

    def __init__(self) -> None:
        self.commands: dict[str, BaseCommand] = {}
        self._load_all_commands()
        for command in self.commands.values():
            command.set_registry(self)

    def _load_all_commands(self) -> None:
        """Discover and register concrete commands defined in the package."""
        for module_info in pkgutil.iter_modules(commands_module.__path__):
            module_name = f"{commands_module.__name__}.{module_info.name}"
            module = importlib.import_module(module_name)

            for _, cls in inspect.getmembers(module, inspect.isclass):
                if (
                    cls.__module__ == module.__name__
                    and issubclass(cls, BaseCommand)
                    and not inspect.isabstract(cls)
                ):
                    self._register_command(cls())

        if not self.commands:
            raise RuntimeError("No commands were discovered in personal_helper.commands")

    def _register_command(self, command: BaseCommand) -> None:
        name = command.get_command_name()
        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                f"Command {type(command).__qualname__} must have a non-empty name"
            )
        if name != name.casefold() or any(character.isspace() for character in name):
            raise ValueError(
                f"Command name {name!r} must be lowercase and contain no whitespace"
            )
        if name in self.commands:
            raise ValueError(f"Duplicate command name: {name!r}")

        self.commands[name] = command

    def get_command(self, name: str) -> BaseCommand | None:
        """Get a command by name, return None if not found"""
        return self.commands.get(name)

    def get_all_commands(self) -> ValuesView[BaseCommand]:
        """Get all registered commands"""
        return self.commands.values()
