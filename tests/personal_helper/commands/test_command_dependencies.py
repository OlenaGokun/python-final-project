import inspect
import sys

import pytest

from personal_helper.commands.base_command import (
    AddressBookCommand,
    BaseCommand,
    NotebookCommand,
)


class ContactProbe(AddressBookCommand):
    def get_command_name(self):
        return "contact-probe"

    def get_description(self):
        return "test"

    def get_usage(self):
        return "contact-probe"

    def run_with_address_book(self, args, address_book):
        self.received = (args, address_book)
        return "contact result"


class NoteProbe(NotebookCommand):
    def get_command_name(self):
        return "note-probe"

    def get_description(self):
        return "test"

    def get_usage(self):
        return "note-probe"

    def run_with_notebook(self, args, notebook):
        self.received = (args, notebook)
        return "note result"


def test_contact_command_receives_address_book(data):
    command = ContactProbe()
    args = ["John"]

    assert command.run(args, data) == "contact result"
    assert command.received[0] is args
    assert command.received[1] is data.address_book


def test_note_command_receives_notebook(data):
    command = NoteProbe()
    args = ["Shopping"]

    assert command.run(args, data) == "note result"
    assert command.received[0] is args
    assert command.received[1] is data.notebook


@pytest.mark.parametrize("base", [AddressBookCommand, NotebookCommand])
def test_specialized_base_classes_are_abstract(base):
    assert inspect.isabstract(base)
    with pytest.raises(TypeError):
        base()


@pytest.mark.skipif(sys.version_info < (3, 11), reason="final metadata requires Python 3.11")
@pytest.mark.parametrize("base", [AddressBookCommand, NotebookCommand])
def test_specialized_run_is_marked_final(base):
    assert base.run.__final__ is True


def test_registry_discovers_specialized_and_general_commands(registry):
    for name in (
        "add",
        "change",
        "phone",
        "show-all-contacts",
        "add-birthday",
        "show-birthday",
        "birthdays",
        "add-email",
        "search",
    ):
        assert isinstance(registry.get_command(name), AddressBookCommand)
    for name in (
        "add-note",
        "update-note",
        "delete-note",
        "find-notes",
        "show-all-notes",
        "add-note-tags",
        "delete-note-tags",
    ):
        assert isinstance(registry.get_command(name), NotebookCommand)
    for name in ("hello", "help", "exit"):
        command = registry.get_command(name)
        assert isinstance(command, BaseCommand)
        assert not isinstance(command, (AddressBookCommand, NotebookCommand))


def test_notes_by_tag_command_is_not_registered(registry):
    assert registry.get_command("notes-by-tag") is None
    assert all(command.get_command_name() != "notes-by-tag" for command in registry.get_all_commands())


def test_find_tags_command_is_not_registered(registry):
    assert registry.get_command("find-tags") is None
    assert all(command.get_command_name() != "find-tags" for command in registry.get_all_commands())


@pytest.mark.parametrize("name", ["add-tags", "remove-tags", "remove-note-tags"])
def test_old_tag_command_names_are_not_registered(registry, name):
    assert registry.get_command(name) is None
