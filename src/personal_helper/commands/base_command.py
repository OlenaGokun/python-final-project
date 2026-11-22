from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from personal_helper.models.personal_helper import PersonalHelper

if TYPE_CHECKING:
    from personal_helper.command_registry import CommandRegistry
    from personal_helper.models.book import AddressBook
    from personal_helper.models.notes import Notebook


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
        """Return usage example (e.g., 'add --name <name> [--phone <phone>]')"""
        pass

    def set_registry(self, registry: CommandRegistry) -> None:
        """Receive the registry after all commands have been registered."""

    @abstractmethod
    def run(self, args: list, data: PersonalHelper) -> CommandResult:
        """Execute the command and return a message or application signal."""
        pass


class AddressBookCommand(BaseCommand):
    """Command that operates on contacts."""

    @final
    def run(self, args: list, data: PersonalHelper) -> CommandResult:
        return self.run_with_address_book(args, data.address_book)

    @abstractmethod
    def run_with_address_book(self, args: list, address_book: AddressBook) -> CommandResult:
        """Execute the command with the address book."""


class NotebookCommand(BaseCommand):
    """Command that operates on notes."""

    @final
    def run(self, args: list, data: PersonalHelper) -> CommandResult:
        return self.run_with_notebook(args, data.notebook)

    @abstractmethod
    def run_with_notebook(self, args: list, notebook: Notebook) -> CommandResult:
        """Execute the command with the notebook."""
