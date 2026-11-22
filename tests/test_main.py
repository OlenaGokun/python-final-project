import pickle

import pytest

from personal_helper.command_registry import CommandRegistry
from personal_helper.core.pickle_manager import load_data, save_data
from personal_helper.models import AddressBook, PersonalHelper, Record
from main import main, print_commands


def test_main_dispatches_greeting_and_exit_through_registry(monkeypatch, capsys):
    inputs = iter(["hello", "exit"])
    saves = []
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("main.load_data", PersonalHelper)
    monkeypatch.setattr("main.save_data", lambda book: saves.append(book))

    main()

    output = capsys.readouterr().out
    assert "Welcome to Personal Helper Bot!" in output
    assert "How can I help you?" in output
    assert "Good bye!" in output
    assert len(saves) == 1


def test_notes_are_searchable_after_cli_save_and_reload(monkeypatch, capsys, tmp_path):
    path = tmp_path / "book.pkl"
    monkeypatch.setattr("main.load_data", lambda: load_data(path))
    monkeypatch.setattr("main.save_data", lambda book: save_data(book, path))
    inputs = iter(["add-note --title Shopping --text Buy milk and bread --tags food home", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    main()
    capsys.readouterr()

    inputs = iter(["find-notes --tags other FOOD", "find-notes --text MILK AND",
                   "find-notes --title shop --text milk and --tags home other",
                   "update-note --title shopping --text Buy coffee", "exit"])
    main()
    output = capsys.readouterr().out

    assert "Shopping: Buy milk and bread" in output
    assert output.count("Shopping: Buy milk and bread") == 3
    assert "✅ Note 'shopping' updated." in output
    assert load_data(path).notebook["shopping"].text.value == "Buy coffee"
    assert load_data(path).notebook.search(tags={"home"})[0].text.value == "Buy coffee"


def test_cli_note_tag_commands(monkeypatch, capsys, tmp_path):
    path = tmp_path / "book.pkl"
    monkeypatch.setattr("main.load_data", lambda: load_data(path))
    monkeypatch.setattr("main.save_data", lambda data: save_data(data, path))
    inputs = iter([
        "add-note --title Shopping --text Buy milk",
        "add-note-tags --title Shopping --tags food home",
        "find-notes --tags FOOD",
        "delete-note-tags --title Shopping --tags food",
        "find-notes --tags food",
        "exit",
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main()

    output = capsys.readouterr().out
    assert "Shopping: Buy milk" in output
    assert "✅ Tags added to note 'Shopping'." in output
    assert "✅ Tags removed from note 'Shopping'." in output
    assert "ℹ️  No notes found." in output
    assert {tag.value for tag in load_data(path).notebook["shopping"].tags} == {"home"}


def test_cli_multiword_names_and_titles_without_quotes(monkeypatch, capsys, tmp_path):
    path = tmp_path / "book.pkl"
    monkeypatch.setattr("main.load_data", lambda: load_data(path))
    monkeypatch.setattr("main.save_data", lambda data: save_data(data, path))
    inputs = iter([
        "add --phone 5012345671 --name Mary Jane",
        "phone --name mary jane",
        "add-birthday --birthday 01.01.2000 --name Mary Jane",
        "show-birthday --name Mary Jane",
        "change --new-phone 5099999999 --name Mary Jane --old-phone 5012345671",
        "add-note --tags food home --title Grocery list --text Buy milk",
        "add-note-tags --tags shopping --title Grocery list",
        "delete-note-tags --title grocery list --tags food",
        "update-note --text Buy bread --title GROCERY LIST --tags home new",
        "find-notes --title grocery list --tags new",
        "exit",
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main()

    output = capsys.readouterr().out
    assert "5012345671" in output
    assert "Mary Jane's birthday: 01.01.2000" in output
    assert "Grocery list: Buy bread" in output
    assert "❌" not in output
    data = load_data(path)
    assert data.address_book["MARY JANE"].phones[0].value == "5099999999"
    assert {tag.value for tag in data.notebook["grocery list"].tags} == {"home", "new"}

    inputs = iter(["delete-note --title Grocery list", "show-all-notes", "exit"])
    main()
    assert "ℹ️  No notes found." in capsys.readouterr().out
    assert len(load_data(path).notebook) == 0


def test_cli_migrates_existing_contacts(monkeypatch, capsys, tmp_path):
    path = tmp_path / "book.pkl"
    book = AddressBook()
    book.add_record(Record("John"))
    path.write_bytes(pickle.dumps(book))
    monkeypatch.setattr("main.load_data", lambda: load_data(path))
    monkeypatch.setattr("main.save_data", lambda data: save_data(data, path))
    inputs = iter(
        ["show-all-contacts", "add-note --title Plans --text Call tomorrow", "exit"]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main()

    output = capsys.readouterr().out
    assert "John" in output
    data = load_data(path)
    assert data.address_book.find("John") is not None
    assert data.notebook["plans"].text.value == "Call tomorrow"


def test_print_commands_uses_registry_for_every_command(capsys):
    print_commands(CommandRegistry())

    output = capsys.readouterr().out
    assert "hello" in output
    assert "exit" in output
    assert "close" not in output
    assert (
        "add --name <name> [--phone <phone> ...] [--email <email>] "
        "[--birthday <DD.MM.YYYY>]"
    ) in output


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
    monkeypatch.setattr("main.load_data", PersonalHelper)
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
    monkeypatch.setattr("main.load_data", PersonalHelper)
    monkeypatch.setattr("main.save_data", fail_to_save)

    main()

    output = capsys.readouterr().out
    assert "Failed to save application data: disk unavailable" in output
    assert "Please enter yes or no." in output
    assert "Good bye!" in output
    assert len(save_attempts) == 2


def test_main_starts_with_empty_data_when_saved_data_is_corrupted(
    monkeypatch, capsys, tmp_path
):
    path = tmp_path / "book.pkl"
    path.write_bytes(b"corrupted pickle data")
    saves = []

    monkeypatch.setattr("builtins.input", lambda _: "exit")
    monkeypatch.setattr("main.load_data", lambda: load_data(path))
    monkeypatch.setattr("main.save_data", lambda data: saves.append(data))

    main()

    output = capsys.readouterr().out
    assert "Failed to load application data:" in output
    assert "Starting with empty application data." in output
    assert "Good bye!" in output
    assert len(saves) == 1
    assert len(saves[0].address_book) == 0
    assert len(saves[0].notebook) == 0


@pytest.mark.parametrize("interrupt", [EOFError, KeyboardInterrupt])
def test_main_treats_input_interrupt_as_exit(monkeypatch, capsys, interrupt):
    saves = []

    def interrupted_input(_):
        raise interrupt

    monkeypatch.setattr("builtins.input", interrupted_input)
    monkeypatch.setattr("main.load_data", PersonalHelper)
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
    monkeypatch.setattr("main.load_data", PersonalHelper)
    monkeypatch.setattr("main.save_data", fail_to_save)

    main()

    output = capsys.readouterr().out
    assert "Good bye!" in output
    assert len(saves) == 1
