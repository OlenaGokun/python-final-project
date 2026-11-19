from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from address_book.models.book import AddressBook

if TYPE_CHECKING:
    from address_book.command_registry import CommandRegistry


@dataclass(frozen=True)
class ExitRequest:
    """Signal that the application should save and shut down."""


CommandResult = str | ExitRequest


class BaseCommand(ABC):
    """Base class for all commands.
    
    To create a new command, inherit from this class and implement the
    abstract methods. CommandRegistry will automatically discover and
    register any class that inherits from BaseCommand.
    """

    @abstractmethod
    def get_command_name(self) -> str:
        """Return the command name (e.g., 'add', 'phone')"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Return a short description of what the command does"""
        pass

    @abstractmethod
    def get_usage(self) -> str:
        """Return usage example (e.g., 'add <name> [phone]')"""
        pass

    def get_aliases(self) -> tuple[str, ...]:
        """Return alternate names accepted for this command."""
        return ()

    def set_registry(self, registry: CommandRegistry) -> None:
        """Receive the registry after all commands have been registered."""

    @abstractmethod
    def run(self, args: list, book: AddressBook) -> CommandResult:
        """Execute the command and return a message or application signal."""
        pass
