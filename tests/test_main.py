import pickle
import io

import pytest
from colorama import Fore, Style

from personal_helper.command_registry import CommandRegistry
from personal_helper.core.pickle_manager import load_data, save_data
from personal_helper.core import formatting
from personal_helper.models import AddressBook, PersonalHelper, Record
from main import main, print_commands


def test_main_dispatches_greeting_and_exit_through_registry(
    monkeypatch, capsys
):
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


def test_cli_displays_compact_and_detailed_contacts(monkeypatch, capsys):
    data = PersonalHelper()
    contact = data.address_book.add_record(Record("Jane Doe"))
    contact.add_phone("0505055500", "main")
    contact.add_email("jane@example.com")
    contact.add_address("Main st. 5")
    contact.add_birthday("21.11.2006")
    inputs = iter(["show-all-contacts", "search-contacts --name Jane", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("main.load_data", lambda: data)
    monkeypatch.setattr("main.save_data", lambda _: None)

    main()

    output = capsys.readouterr().out
    assert (
        "Jane Doe: 📞 main 0505055500; ✉️ jane@example.com; "
        "🏠 Main st. 5; 🎂 21.11.2006\n"
    ) in output
    assert (
        "Jane Doe\n"
        "    phones:\n"
        "              main 0505055500\n"
        "    email:    jane@example.com\n"
        "    address:  Main st. 5\n"
        "    birthday: 21.11.2006\n"
    ) in output
    assert "\x1b[" not in output


def test_notes_are_searchable_after_cli_save_and_reload(
    monkeypatch, capsys, tmp_path
):
    path = tmp_path / "book.pkl"
    monkeypatch.setattr("main.load_data", lambda: load_data(path))
    monkeypatch.setattr("main.save_data", lambda book: save_data(book, path))
    inputs = iter(
        [
            "add-note --title Shopping --text Buy milk and bread "
            "--tags food home",
            "exit",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    main()
    capsys.readouterr()

    inputs = iter(
        [
            "search-notes --tags other FOOD",
            "search-notes --text MILK AND",
            "search-notes --title shop --text milk and --tags home other",
            "update-note --title shopping --text Buy coffee",
            "exit",
        ]
    )
    main()
    output = capsys.readouterr().out

    assert (
        output.count(
            "Shopping\n    text: Buy milk and bread\n    tags: food, home"
        )
        == 3
    )
    assert "✅ Note 'shopping' updated." in output
    assert load_data(path).notebook["shopping"].text.value == "Buy coffee"
    assert (
        load_data(path).notebook.search(tags={"home"})[0].text.value
        == "Buy coffee"
    )


def test_cli_note_tag_commands(monkeypatch, capsys, tmp_path):
    path = tmp_path / "book.pkl"
    monkeypatch.setattr("main.load_data", lambda: load_data(path))
    monkeypatch.setattr("main.save_data", lambda data: save_data(data, path))
    inputs = iter(
        [
            "add-note --title Shopping --text Buy milk",
            "add-note-tags --title Shopping --tags food home",
            "search-notes --tags FOOD",
            "delete-note-tags --title Shopping --tags food",
            "search-notes --tags food",
            "exit",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main()

    output = capsys.readouterr().out
    assert "Shopping\n    text: Buy milk\n    tags: food, home" in output
    assert "✅ Tags added to note 'Shopping'." in output
    assert "✅ Tags removed from note 'Shopping'." in output
    assert "ℹ️  No notes found." in output
    assert {
        tag.value for tag in load_data(path).notebook["shopping"].tags
    } == {"home"}


def test_cli_multiword_names_and_titles_without_quotes(
    monkeypatch, capsys, tmp_path
):
    path = tmp_path / "book.pkl"
    monkeypatch.setattr("main.load_data", lambda: load_data(path))
    monkeypatch.setattr("main.save_data", lambda data: save_data(data, path))
    inputs = iter(
        [
            "add-contact --phone 5012345671 --name Mary Jane",
            "show-contact --name mary jane",
            "add-birthday --birthday 01.01.2000 --name Mary Jane",
            "show-birthday --name Mary Jane",
            "change-phone --new-phone 5099999999 --name Mary Jane "
            "--old-phone 5012345671",
            "add-note --tags food home --title Grocery list --text Buy milk",
            "add-note-tags --tags shopping --title Grocery list",
            "delete-note-tags --title grocery list --tags food",
            "update-note --text Buy bread --title GROCERY LIST "
            "--tags home new",
            "search-notes --title grocery list --tags new",
            "exit",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main()

    output = capsys.readouterr().out
    assert "5012345671" in output
    assert "Mary Jane's birthday: 01.01.2000" in output
    assert "Grocery list\n    text: Buy bread\n    tags: home, new" in output
    assert "❌" not in output
    data = load_data(path)
    assert data.address_book["MARY JANE"].phones[0].value == "5099999999"
    assert {tag.value for tag in data.notebook["grocery list"].tags} == {
        "home",
        "new",
    }

    inputs = iter(
        ["delete-note --title Grocery list", "show-all-notes", "exit"]
    )
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
        [
            "show-all-contacts",
            "add-note --title Plans --text Call tomorrow",
            "exit",
        ]
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
        "add-contact --name <name> [--phone <phone> ...] [--email <email>] "
        "[--address <address>] [--birthday <DD.MM.YYYY>]"
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


def test_cli_retries_invalid_contact_fields_without_losing_other_values(
    monkeypatch, capsys
):
    data = PersonalHelper()
    inputs = iter(
        [
            "add-contact --name Jane --phone 0501234567 bad 0501234569 "
            "--email bad-email --address Main st. 5 --birthday 01.01.1990",
            "still-bad",
            "0501234568",
            "jane@example.com",
            "exit",
        ]
    )
    prompts = []

    def read_input(prompt):
        prompts.append(prompt)
        return next(inputs)

    monkeypatch.setattr("builtins.input", read_input)
    monkeypatch.setattr("main.load_data", lambda: data)
    monkeypatch.setattr("main.save_data", lambda _: None)

    main()

    record = data.address_book["Jane"]
    assert [phone.value for phone in record.phones] == [
        "0501234567",
        "0501234568",
        "0501234569",
    ]
    assert record.email.value == "jane@example.com"
    assert record.address.value == "Main st. 5"
    assert str(record.birthday) == "01.01.1990"
    assert prompts.count("Enter a valid phone (or cancel): ") == 2
    assert prompts.count("Enter a valid email (or cancel): ") == 1
    output = capsys.readouterr().out
    assert "❌ Phone must be a valid phone number, got 'bad'." in output
    assert "❌ Phone must be a valid phone number, got 'still-bad'." in output
    assert "❌ Invalid email format" in output
    assert "✅ Contact 'Jane' added." in output


@pytest.mark.parametrize(
    ("command", "replacement", "field"),
    [
        (
            "add-phone --name Jane --phone bad --alias work",
            "0501234568",
            "phone",
        ),
        (
            "change-phone --name Jane --old-phone 0501234567 --new-phone bad",
            "0501234569",
            "phone",
        ),
        ("add-email --name Jane --email bad", "jane@example.com", "email"),
    ],
)
def test_cli_retries_other_contact_commands(
    monkeypatch, capsys, command, replacement, field
):
    data = PersonalHelper()
    record = data.address_book.add_record(Record("Jane"))
    record.add_phone("0501234567")
    inputs = iter([command, replacement, "exit"])
    prompts = []

    def read_input(prompt):
        prompts.append(prompt)
        return next(inputs)

    monkeypatch.setattr("builtins.input", read_input)
    monkeypatch.setattr("main.load_data", lambda: data)
    monkeypatch.setattr("main.save_data", lambda _: None)

    main()

    assert f"Enter a valid {field} (or cancel): " in prompts
    assert "❌" in capsys.readouterr().out
    if field == "email":
        assert record.email.value == replacement
    else:
        assert replacement in [phone.value for phone in record.phones]
        if command.startswith("change-phone"):
            assert record.find_phone("0501234567") is None
        else:
            assert record.find_phone(replacement).alias == "work"


@pytest.mark.parametrize(
    "cancel", ["cancel", "CANCEL", EOFError, KeyboardInterrupt]
)
def test_cli_cancel_retry_does_not_change_existing_contact(
    monkeypatch, capsys, cancel
):
    data = PersonalHelper()
    record = data.address_book.add_record(Record("Jane"))
    record.add_phone("0501234567")
    record.add_email("old@example.com")
    inputs = iter(
        [
            "add-contact --name Jane --phone 0501234568 --email invalid",
            cancel,
            "exit",
        ]
    )

    def read_input(_):
        value = next(inputs)
        if isinstance(value, type) and issubclass(value, BaseException):
            raise value
        return value

    monkeypatch.setattr("builtins.input", read_input)
    monkeypatch.setattr("main.load_data", lambda: data)
    monkeypatch.setattr("main.save_data", lambda _: None)

    main()

    assert [phone.value for phone in record.phones] == ["0501234567"]
    assert record.email.value == "old@example.com"
    assert "❌ Command canceled." in capsys.readouterr().out


def test_cli_cancel_retry_does_not_create_new_contact(monkeypatch, capsys):
    data = PersonalHelper()
    inputs = iter(
        ["add-contact --name Jane --phone invalid", "cancel", "exit"]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("main.load_data", lambda: data)
    monkeypatch.setattr("main.save_data", lambda _: None)

    main()

    assert data.address_book.find("Jane") is None
    assert "❌ Command canceled." in capsys.readouterr().out


@pytest.mark.parametrize(
    "command",
    [
        "add-phone --name Jane --phone invalid --alias work",
        "change-phone --name Jane --old-phone 0501234567 "
        "--new-phone invalid",
        "add-email --name Jane --email invalid",
    ],
)
def test_cli_cancel_retry_does_not_change_contact_for_other_commands(
    monkeypatch, capsys, command
):
    data = PersonalHelper()
    record = data.address_book.add_record(Record("Jane"))
    record.add_phone("0501234567")
    record.add_email("old@example.com")
    inputs = iter([command, "cancel", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("main.load_data", lambda: data)
    monkeypatch.setattr("main.save_data", lambda _: None)

    main()

    assert [phone.value for phone in record.phones] == ["0501234567"]
    assert record.email.value == "old@example.com"
    assert "❌ Command canceled." in capsys.readouterr().out


def test_cli_does_not_retry_new_phone_when_old_phone_is_missing(
    monkeypatch, capsys
):
    data = PersonalHelper()
    data.address_book.add_record(Record("Jane"))
    inputs = iter(
        [
            "change-phone --name Jane --old-phone 0501234567 "
            "--new-phone invalid",
            "exit",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("main.load_data", lambda: data)
    monkeypatch.setattr("main.save_data", lambda _: None)

    main()

    assert "Phone 0501234567 not found" in capsys.readouterr().out


def test_main_colors_errors_in_terminal(monkeypatch):
    class Terminal(io.StringIO):
        def isatty(self):
            return True

    terminal = Terminal()
    inputs = iter(["", "unknown", "search-notes", "exit"])
    monkeypatch.setattr(formatting.sys, "stdout", terminal)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("main.load_data", PersonalHelper)
    monkeypatch.setattr("main.save_data", lambda _: None)

    main()

    output = terminal.getvalue()
    assert f"{Fore.RED}Please enter a command.{Style.RESET_ALL}" in output
    assert f"{Fore.RED}Invalid command.{Style.RESET_ALL}" in output
    assert f"{Fore.RED}❌ Invalid arguments." in output
    assert "Usage: search-notes" in output
    assert "Good bye!" in output


def test_cli_colors_field_retry_error_in_terminal(monkeypatch):
    class Terminal(io.StringIO):
        def isatty(self):
            return True

    terminal = Terminal()
    inputs = iter(
        ["add-contact --name Jane --email invalid", "cancel", "exit"]
    )
    monkeypatch.setattr(formatting.sys, "stdout", terminal)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("main.load_data", PersonalHelper)
    monkeypatch.setattr("main.save_data", lambda _: None)

    main()

    output = terminal.getvalue()
    assert (
        f"{Fore.RED}❌ Invalid email format: 'invalid'.{Style.RESET_ALL}"
        in output
    )
    assert f"{Fore.RED}❌ Command canceled.{Style.RESET_ALL}" in output


def test_main_colors_load_and_save_errors_in_terminal(monkeypatch):
    class Terminal(io.StringIO):
        def isatty(self):
            return True

    def fail_load():
        raise OSError("load failed")

    def fail_save(_):
        raise OSError("save failed")

    terminal = Terminal()
    inputs = iter(["exit", "maybe", "yes"])
    monkeypatch.setattr(formatting.sys, "stdout", terminal)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("main.load_data", fail_load)
    monkeypatch.setattr("main.save_data", fail_save)

    main()

    output = terminal.getvalue()
    assert (
        f"{Fore.RED}Failed to load application data: load failed"
        f"{Style.RESET_ALL}"
        in output
    )
    assert (
        f"{Fore.RED}Failed to save application data: save failed"
        f"{Style.RESET_ALL}"
        in output
    )
    assert f"{Fore.RED}Please enter yes or no.{Style.RESET_ALL}" in output
    assert "Starting with empty application data." in output


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


@pytest.mark.parametrize(
    ("operation", "confirmation", "expected_name"),
    [
        (
            "rename-contact --name Mary Jane --new-name Mary Doe",
            [],
            "Mary Doe",
        ),
        (
            "rename-contact --name Mary Jane --new-name MARY JANE",
            [],
            "MARY JANE",
        ),
        ("delete-contact --name Mary Jane", ["yes"], None),
    ],
)
def test_cli_contact_changes_survive_restart(
    monkeypatch, capsys, tmp_path, operation, confirmation, expected_name
):
    path = tmp_path / "book.pkl"
    data = PersonalHelper()
    original = Record("Mary Jane")
    original.update_details(["5012345671"], "mary@example.test", "01.01.2000")
    original.add_address("Main st. 5")
    data.address_book.add_record(original)
    data.notebook.add("Mary Jane", "Independent note", {"personal"})
    save_data(data, path)
    monkeypatch.setattr("main.load_data", lambda: load_data(path))
    monkeypatch.setattr(
        "main.save_data", lambda updated: save_data(updated, path)
    )

    inputs = iter([operation, *confirmation, "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    main()
    operation_output = capsys.readouterr().out
    if expected_name:
        assert (
            f"Contact 'Mary Jane' renamed to '{expected_name}'."
            in operation_output
        )
    else:
        assert "Contact 'Mary Jane' deleted." in operation_output

    inputs = iter(["show-all-contacts", "show-all-notes", "exit"])
    main()
    output = capsys.readouterr().out
    assert "Mary Jane: Independent note" in output

    reloaded = load_data(path)
    if expected_name:
        assert len(reloaded.address_book) == 1
        if expected_name.casefold() != original.name.key:
            assert reloaded.address_book.find("Mary Jane") is None
        renamed = reloaded.address_book[expected_name]
        assert renamed.name.value == expected_name
        assert (renamed.phones, renamed.email, renamed.birthday) == (
            original.phones,
            original.email,
            original.birthday,
        )
        assert renamed.address == original.address
        assert expected_name in output
    else:
        assert reloaded.address_book.find("Mary Jane") is None
        assert len(reloaded.address_book) == 0
        assert "ℹ️  No contacts found." in output

    note = reloaded.notebook["Mary Jane"]
    assert note.title.value == "Mary Jane"
    assert note.text.value == "Independent note"
    assert {tag.value for tag in note.tags} == {"personal"}


@pytest.mark.parametrize("interrupt", [EOFError, KeyboardInterrupt])
def test_exact_commands_and_prompt_controls_skip_suggestions(
    monkeypatch, capsys, interrupt
):
    from types import SimpleNamespace

    inputs = iter(["show-all-notes", "show-contact", "go", " ", interrupt])
    turns = []
    saves = []
    short_command = SimpleNamespace(
        run=lambda args, data: "Short command ran."
    )
    original_lookup = CommandRegistry.get_command

    def lookup(registry, name):
        return (
            short_command if name == "go" else original_lookup(registry, name)
        )

    def read(prompt):
        assert prompt == "Enter a command: "
        turns.append(capsys.readouterr().out)
        submission = next(inputs)
        if submission is interrupt:
            raise interrupt
        return submission

    monkeypatch.setattr(CommandRegistry, "get_command", lookup)
    monkeypatch.setattr("builtins.input", read)
    monkeypatch.setattr("main.load_data", PersonalHelper)
    monkeypatch.setattr("main.save_data", saves.append)

    main()

    assert turns[1].splitlines() == ["ℹ️  No notes found."]
    assert turns[2].splitlines() == [
        "❌ Invalid arguments. Missing required options: --name.",
        "Usage: show-contact --name <name>",
    ]
    assert turns[3].splitlines() == ["Short command ran."]
    assert turns[4].splitlines() == ["Please enter a command."]
    assert capsys.readouterr().out.strip() == "Good bye!"
    assert len(saves) == 1


def test_lookup_miss_sends_only_normalized_name_and_live_names(
    monkeypatch, capsys, registry, data
):
    from unittest.mock import Mock

    matcher = Mock(side_effect=[["show-all-contacts"], []])
    monkeypatch.setattr("main.suggest_commands", matcher, raising=False)
    monkeypatch.setattr("main.CommandRegistry", lambda: registry)
    monkeypatch.setattr("main.load_data", lambda: data)
    monkeypatch.setattr("main.save_data", lambda data: None)
    names = [cmd.get_command_name() for cmd in registry.get_all_commands()]
    enumerate_commands = Mock(wraps=registry.get_all_commands)
    monkeypatch.setattr(registry, "get_all_commands", enumerate_commands)
    submissions = iter(
        ["SHOW-ALL-C --name Private Person", "s", "sh", "zzzzzzzz", "exit"]
    )
    turns = []

    def read(prompt):
        assert prompt == "Enter a command: "
        turns.append(capsys.readouterr().out.splitlines())
        return next(submissions)

    monkeypatch.setattr("builtins.input", read)

    main()

    assert turns[1] == ["Invalid command.", "Did you mean: show-all-contacts?"]
    assert turns[2:] == [["Invalid command."]] * 3
    assert [
        (token, list(candidates))
        for token, candidates in (call.args for call in matcher.call_args_list)
    ] == [
        ("show-all-c", names),
        ("zzzzzzzz", names),
    ]
    assert (
        enumerate_commands.call_count == 4
    )  # Setup, help, and two eligible misses.
