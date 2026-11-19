from collections.abc import ValuesView
import importlib
import inspect
import pkgutil

import address_book.commands as commands_module
from address_book.commands.base_command import BaseCommand


class CommandRegistry:
    """Registry that discovers and registers commands by scanning for BaseCommand subclasses"""

    def __init__(self) -> None:
        self.commands: dict[str, BaseCommand] = {}
        self._aliases: dict[str, BaseCommand] = {}
        self._load_all_commands()
        for command in self.commands.values():
            command.set_registry(self)

    def _load_all_commands(self) -> None:
        """Find all command modules and extract BaseCommand subclasses.
        
        Scans each module in the commands package for classes that inherit from
        BaseCommand, instantiates them, and registers them by command name.
        """
        commands_path = commands_module.__path__

        # Step 1: Import all command modules
        for importer, name, is_pkg in pkgutil.iter_modules(commands_path):
            module_name = f'address_book.commands.{name}'
            try:
                module = importlib.import_module(module_name)
            except Exception as e:
                print(f"Warning: Failed to load command module '{module_name}': {e}")
                continue

            # Step 2: Scan this module for concrete BaseCommand subclasses.
            for _, item in inspect.getmembers(module, inspect.isclass):
                if (
                    item.__module__ != module.__name__
                    or not issubclass(item, BaseCommand)
                    or inspect.isabstract(item)
                ):
                    continue

                instance = item()
                command_name = instance.get_command_name()
                if not isinstance(command_name, str) or not command_name.strip():
                    raise ValueError(
                        f"Command {item.__qualname__} must have a non-empty name"
                    )
                if (
                    command_name != command_name.casefold()
                    or any(character.isspace() for character in command_name)
                ):
                    raise ValueError(
                        f"Command name {command_name!r} must be lowercase "
                        "and contain no whitespace"
                    )
                if command_name in self.commands or command_name in self._aliases:
                    raise ValueError(f"Duplicate command name: {command_name!r}")

                for metadata_name, metadata in (
                    ("description", instance.get_description()),
                    ("usage", instance.get_usage()),
                ):
                    if not isinstance(metadata, str) or not metadata.strip():
                        raise ValueError(
                            f"Command {command_name!r} must have a non-empty "
                            f"{metadata_name}"
                        )

                aliases = instance.get_aliases()
                if not isinstance(aliases, tuple):
                    raise ValueError(
                        f"Aliases for command {command_name!r} must be a tuple"
                    )
                aliases_seen: set[str] = set()
                for alias in aliases:
                    if not isinstance(alias, str) or not alias.strip():
                        raise ValueError(
                            f"Command {command_name!r} has an empty alias"
                        )
                    if (
                        alias != alias.casefold()
                        or any(character.isspace() for character in alias)
                    ):
                        raise ValueError(
                            f"Command alias {alias!r} must be lowercase "
                            "and contain no whitespace"
                        )
                    if (
                        alias == command_name
                        or alias in self.commands
                        or alias in self._aliases
                        or alias in aliases_seen
                    ):
                        raise ValueError(f"Duplicate command name or alias: {alias!r}")
                    aliases_seen.add(alias)

                self.commands[command_name] = instance
                self._aliases.update({alias: instance for alias in aliases})

    def get_command(self, name: str) -> BaseCommand | None:
        """Get a command by name, return None if not found"""
        return self.commands.get(name) or self._aliases.get(name)

    def get_all_commands(self) -> ValuesView[BaseCommand]:
        """Get all registered commands"""
        return self.commands.values()
