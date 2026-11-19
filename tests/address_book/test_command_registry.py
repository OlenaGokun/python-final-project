"""Unit tests for CommandRegistry discovery, validation, and retrieval."""

from types import ModuleType

import pytest
import address_book.command_registry as command_registry_module
from address_book.commands.base_command import BaseCommand
from address_book.command_registry import CommandRegistry


def _registry_for_commands(monkeypatch, *command_classes):
    module = ModuleType("address_book.commands.test_commands")
    for command_class in command_classes:
        command_class.__module__ = module.__name__
        setattr(module, command_class.__name__, command_class)

    monkeypatch.setattr(
        command_registry_module.pkgutil,
        "iter_modules",
        lambda _: [(None, "test_commands", False)],
    )
    monkeypatch.setattr(
        command_registry_module.importlib,
        "import_module",
        lambda _: module,
    )
    return CommandRegistry()


def _command_class(name, command_name, description="A test command", usage="test"):
    def get_command_name(self):
        return command_name

    def get_description(self):
        return description

    def get_usage(self):
        return usage

    def run(self, args, book):
        return "ok"

    return type(
        name,
        (BaseCommand,),
        {
            "get_command_name": get_command_name,
            "get_description": get_description,
            "get_usage": get_usage,
            "run": run,
        },
    )


def test_discovers_commands_and_returns_them_by_name():
    registry = CommandRegistry()

    assert {
        "add",
        "add-birthday",
        "all",
        "show-birthday",
        "birthdays",
        "change",
        "close",
        "help",
        "hello",
        "phone",
    } <= set(registry.commands)
    assert isinstance(registry.get_command("add"), BaseCommand)
    assert registry.get_command("not-a-command") is None
    assert len(registry.get_all_commands()) == len(registry.commands)
    assert registry.get_command("exit") is registry.get_command("close")


@pytest.mark.parametrize("command_name", ["", "   "])
def test_rejects_empty_command_name(monkeypatch, command_name):
    command_class = _command_class("InvalidCommand", command_name)

    with pytest.raises(ValueError, match="non-empty name"):
        _registry_for_commands(monkeypatch, command_class)


@pytest.mark.parametrize("command_name", ["two words", "Uppercase"])
def test_rejects_command_names_with_invalid_format(monkeypatch, command_name):
    command_class = _command_class("InvalidCommand", command_name)

    with pytest.raises(ValueError, match="lowercase and contain no whitespace"):
        _registry_for_commands(monkeypatch, command_class)


def test_rejects_duplicate_command_names(monkeypatch):
    first = _command_class("FirstCommand", "duplicate")
    second = _command_class("SecondCommand", "duplicate")

    with pytest.raises(ValueError, match="Duplicate command name"):
        _registry_for_commands(monkeypatch, first, second)


def test_rejects_duplicate_aliases(monkeypatch):
    first = _command_class("FirstCommand", "first")
    second = _command_class("SecondCommand", "second")
    first.get_aliases = lambda self: ("shared",)
    second.get_aliases = lambda self: ("shared",)

    with pytest.raises(ValueError, match="Duplicate command name or alias"):
        _registry_for_commands(monkeypatch, first, second)


@pytest.mark.parametrize(
    ("description", "usage", "invalid_metadata"),
    [
        ("", "test", "description"),
        ("A test command", " ", "usage"),
    ],
)
def test_rejects_empty_command_metadata(
    monkeypatch, description, usage, invalid_metadata
):
    command_class = _command_class(
        "InvalidCommand", "test", description=description, usage=usage
    )

    with pytest.raises(ValueError, match=f"non-empty {invalid_metadata}"):
        _registry_for_commands(monkeypatch, command_class)
