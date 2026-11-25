from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, final

from colorama import Fore, Style

from personal_helper.core.formatting import colored
from personal_helper.models.personal_helper import PersonalHelper

if TYPE_CHECKING:
    from personal_helper.models import AddressBook, Note, Notebook, Phone, Record


@dataclass(frozen=True)
class ExitRequest:
    """Signal that the application should save and shut down."""


CommandResult = str | ExitRequest

TITLE_COLOR = Fore.BLUE + Style.BRIGHT


class CommandLookup(Protocol):
    """Read-only command lookup used by commands that need registry access."""

    def get_command(self, name: str) -> BaseCommand | None: ...

    def get_all_commands(self) -> Iterable[BaseCommand]: ...


class BaseCommand(ABC):
    """Base class for all commands.
    
    To create a new command, inherit from this class and implement the
    abstract methods. CommandRegistry will automatically discover and
    register any class that inherits from BaseCommand.
    """

    @abstractmethod
    def get_command_name(self) -> str:
        """Return the command name (e.g., 'add-contact', 'show-contact')"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Return a short description of what the command does"""
        pass

    @abstractmethod
    def get_usage(self) -> str:
        """Return usage example (e.g., 'add-contact --name <name> [--phone <phone>]')"""
        pass

    def set_registry(self, registry: CommandLookup) -> None:
        """Receive the registry after all commands have been registered."""

    @abstractmethod
    def run(self, args: list, data: PersonalHelper) -> CommandResult:
        """Execute the command and return a message or application signal."""
        pass


class AddressBookCommand(BaseCommand):
    """Command that operates on contacts."""

    @staticmethod
    def _format_phone(phone: Phone) -> str:
        if phone.alias is None:
            return phone.value
        return f"{colored(phone.alias, Fore.BLUE)} {phone.value}"

    @staticmethod
    def format_contact_details(record: Record) -> str:
        """Render a contact's fields in an indented layout."""
        lines = [
            colored(record.name.value, TITLE_COLOR),
            f"    {colored('phones:', Fore.BLUE)}",
        ]
        phones = [
            AddressBookCommand._format_phone(phone) for phone in record.phones
        ] or ["—"]
        lines.extend(f"              {phone}" for phone in phones)
        fields = (
            ("email:", str(record.email) if record.email else "—"),
            ("address:", str(record.address) if record.address else "—"),
            ("birthday:", str(record.birthday) if record.birthday else "—"),
        )
        for label, value in fields:
            lines.append(
                f"    {colored(label, Fore.BLUE)}{' ' * (10 - len(label))}{value}"
            )
        return "\n".join(lines)

    @staticmethod
    def format_contacts_compact(records: list[Record]) -> str:
        """Render each contact on one compact line."""
        lines = []
        for record in records:
            name = colored(f"{record.name.value}:", TITLE_COLOR)
            phones = ", ".join(
                AddressBookCommand._format_phone(phone) for phone in record.phones
            ) or "—"
            email = str(record.email) if record.email else "—"
            address = str(record.address) if record.address else "—"
            birthday = str(record.birthday) if record.birthday else "—"
            lines.append(f"{name} 📞 {phones}; ✉️ {email}; 🏠 {address}; 🎂 {birthday}")
        return "\n".join(lines)

    @final
    def run(self, args: list, data: PersonalHelper) -> CommandResult:
        return self.run_with_address_book(args, data.address_book)

    @abstractmethod
    def run_with_address_book(self, args: list, address_book: AddressBook) -> CommandResult:
        """Execute the command with the address book."""


class NotebookCommand(BaseCommand):
    """Command that operates on notes."""

    @staticmethod
    def format_note_compact(note: Note) -> str:
        title = colored(f"{note.title}:", TITLE_COLOR)
        tags = ", ".join(sorted(tag.value for tag in note.tags))
        return f"{title} {note.text}" + (f" [tags: {tags}]" if tags else "")

    @staticmethod
    def format_note_details(note: Note) -> str:
        title = colored(str(note.title), TITLE_COLOR)
        text_label = colored("text:", Fore.BLUE)
        tags_label = colored("tags:", Fore.BLUE)
        tags = ", ".join(sorted(tag.value for tag in note.tags)) or "—"
        return f"{title}\n    {text_label} {note.text}\n    {tags_label} {tags}"

    @final
    def run(self, args: list, data: PersonalHelper) -> CommandResult:
        return self.run_with_notebook(args, data.notebook)

    @abstractmethod
    def run_with_notebook(self, args: list, notebook: Notebook) -> CommandResult:
        """Execute the command with the notebook."""
