import pytest

from address_book.command_registry import CommandRegistry
from address_book.models import AddressBook
from main import main, print_commands


def test_main_dispatches_greeting_and_exit_through_registry(monkeypatch, capsys):
    inputs = iter(["hello", "exit"])
    saves = []
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("main.load_data", AddressBook)
    monkeypatch.setattr("main.save_data", lambda book: saves.append(book))

    main()

    output = capsys.readouterr().out
    assert "Welcome to Personal Helper Bot!" in output
    assert "How can I help you?" in output
    assert "Good bye!" in output
    assert len(saves) == 1


def test_print_commands_uses_registry_for_every_command(capsys):
    print_commands(CommandRegistry())

    output = capsys.readouterr().out
    assert "hello" in output
    assert "exit" in output
    assert "close" not in output
    assert "add <name> [phone]" in output


def test_main_handles_empty_unknown_and_failing_commands(monkeypatch, capsys):
    inputs = iter(["", "close", "boom", "exit"])
    saves = []

    class ExplodingCommand:
        def run(self, args, book):
            raise RuntimeError("command failed")

    original_get_command = CommandRegistry.get_command

    def get_command(registry, name):
        if name == "boom":
            return ExplodingCommand()
        return original_get_command(registry, name)

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("main.load_data", AddressBook)
    monkeypatch.setattr("main.save_data", lambda book: saves.append(book))
    monkeypatch.setattr(CommandRegistry, "get_command", get_command)

    main()

    output = capsys.readouterr().out
    assert "Please enter a command." in output
    assert "Invalid command." in output
    assert "Error: command failed" in output
    assert "Good bye!" in output
    assert len(saves) == 1


def test_main_retries_after_save_failure_and_invalid_confirmation(
    monkeypatch, capsys
):
    inputs = iter(["exit", "maybe", "no", "exit", "yes"])
    save_attempts = []

    def fail_to_save(book):
        save_attempts.append(book)
        raise OSError("disk unavailable")

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("main.load_data", AddressBook)
    monkeypatch.setattr("main.save_data", fail_to_save)

    main()

    output = capsys.readouterr().out
    assert "Failed to save address book: disk unavailable" in output
    assert "Please enter yes or no." in output
    assert "Good bye!" in output
    assert len(save_attempts) == 2


@pytest.mark.parametrize("interrupt", [EOFError, KeyboardInterrupt])
def test_main_treats_input_interrupt_as_exit(monkeypatch, capsys, interrupt):
    saves = []

    def interrupted_input(_):
        raise interrupt

    monkeypatch.setattr("builtins.input", interrupted_input)
    monkeypatch.setattr("main.load_data", AddressBook)
    monkeypatch.setattr("main.save_data", lambda book: saves.append(book))

    main()

    output = capsys.readouterr().out
    assert "Good bye!" in output
    assert len(saves) == 1


@pytest.mark.parametrize("interrupt", [EOFError, KeyboardInterrupt])
def test_main_exits_when_save_confirmation_is_interrupted(
    monkeypatch, capsys, interrupt
):
    inputs = iter(["exit"])
    saves = []

    def input_with_interrupted_confirmation(_):
        try:
            return next(inputs)
        except StopIteration:
            raise interrupt

    def fail_to_save(book):
        saves.append(book)
        raise OSError("disk unavailable")

    monkeypatch.setattr("builtins.input", input_with_interrupted_confirmation)
    monkeypatch.setattr("main.load_data", AddressBook)
    monkeypatch.setattr("main.save_data", fail_to_save)

    main()

    output = capsys.readouterr().out
    assert "Good bye!" in output
    assert len(saves) == 1
