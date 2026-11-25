"""Unit tests for CommandRegistry discovery, validation, and retrieval."""

from types import ModuleType
from pkgutil import ModuleInfo

import pytest
import personal_helper.command_registry as command_registry_module
from personal_helper.commands.base_command import BaseCommand
from personal_helper.command_registry import CommandRegistry


def _registry_for_commands(monkeypatch, *command_classes):
    module = ModuleType("personal_helper.commands.test_commands")
    for command_class in command_classes:
        command_class.__module__ = module.__name__
        setattr(module, command_class.__name__, command_class)

    monkeypatch.setattr(
        command_registry_module.pkgutil,
        "iter_modules",
        lambda _: [ModuleInfo(None, "test_commands", False)],
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
        "add-contact",
        "add-address",
        "add-birthday",
        "add-email",
        "show-all-contacts",
        "show-all-notes",
        "show-birthday",
        "show-birthdays",
        "delete-address",
        "change-phone",
        "exit",
        "help",
        "hello",
        "show-contact",
        "search-contacts",
    } <= set(registry.commands)
    assert isinstance(registry.get_command("add-contact"), BaseCommand)
    assert registry.get_command("not-a-command") is None
    assert len(registry.get_all_commands()) == len(registry.commands)
    assert registry.get_command("exit") is not None
    assert registry.get_command("close") is None
    assert registry.get_command("all") is None
    assert registry.get_command("phone") is None


def test_ignores_imported_and_abstract_command_classes(monkeypatch):
    module = ModuleType("personal_helper.commands.test_commands")
    imported = _command_class("ImportedCommand", "imported")
    abstract = type("AbstractCommand", (BaseCommand,), {"__module__": module.__name__})
    module.ImportedCommand = imported
    module.AbstractCommand = abstract

    monkeypatch.setattr(
        command_registry_module.pkgutil, "iter_modules",
        lambda _: [ModuleInfo(None, "test_commands", False)],
    )
    monkeypatch.setattr(
        command_registry_module.importlib, "import_module", lambda _: module
    )

    with pytest.raises(RuntimeError, match="No commands were discovered"):
        CommandRegistry()


def test_fails_when_no_command_modules_are_found(monkeypatch):
    monkeypatch.setattr(command_registry_module.pkgutil, "iter_modules", lambda _: [])

    with pytest.raises(RuntimeError, match="No commands were discovered"):
        CommandRegistry()


@pytest.mark.parametrize("error", [ImportError("broken module"), RuntimeError("broken module")])
def test_failed_module_import_stops_registry_initialization(monkeypatch, error):
    imported_modules = []
    def import_module(name):
        imported_modules.append(name)
        raise error

    monkeypatch.setattr(
        command_registry_module.pkgutil, "iter_modules",
        lambda _: [ModuleInfo(None, "bad", False), ModuleInfo(None, "good", False)],
    )
    monkeypatch.setattr(command_registry_module.importlib, "import_module", import_module)

    with pytest.raises(type(error), match="broken module") as exc_info:
        CommandRegistry()

    assert exc_info.value is error
    assert imported_modules == ["personal_helper.commands.bad"]


@pytest.mark.parametrize("command_name", ["", "   "])
def test_rejects_empty_command_name(monkeypatch, command_name):
    command_class = _command_class("InvalidCommand", command_name)

    with pytest.raises(ValueError, match="non-empty name"):
        _registry_for_commands(monkeypatch, command_class)


@pytest.mark.parametrize("command_name", [None, 42])
def test_rejects_non_string_command_name(monkeypatch, command_name):
    command_class = _command_class("InvalidCommand", command_name)

    with pytest.raises(ValueError, match="non-empty name"):
        _registry_for_commands(monkeypatch, command_class)


@pytest.mark.parametrize(
    "command_name",
    ["two words", "Uppercase", "leading ", "\ttab", "straße"],
)
def test_rejects_command_names_with_invalid_format(monkeypatch, command_name):
    command_class = _command_class("InvalidCommand", command_name)

    with pytest.raises(ValueError, match="lowercase and contain no whitespace"):
        _registry_for_commands(monkeypatch, command_class)


@pytest.mark.parametrize("command_name", ["simple", "add-birthday", "help2"])
def test_registers_valid_command_name(monkeypatch, command_name):
    command_class = _command_class("ValidCommand", command_name)

    registry = _registry_for_commands(monkeypatch, command_class)

    assert isinstance(registry.get_command(command_name), command_class)


def test_rejects_duplicate_command_names(monkeypatch):
    first = _command_class("FirstCommand", "duplicate")
    second = _command_class("SecondCommand", "duplicate")

    with pytest.raises(ValueError, match="Duplicate command name"):
        _registry_for_commands(monkeypatch, first, second)


def test_discovered_commands_have_help_text():
    registry = CommandRegistry()

    for command in registry.get_all_commands():
        description = command.get_description()
        usage = command.get_usage()
        assert isinstance(description, str) and description.strip()
        assert isinstance(usage, str) and usage.strip()
