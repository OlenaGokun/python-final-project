import pytest

from personal_helper.core import formatting
from personal_helper.models import Record


def test_show_contact_displays_all_details(registry, data, monkeypatch):
    monkeypatch.setattr(formatting.sys.stdout, "isatty", lambda: False)
    record = data.address_book.add_record(Record("Jane Doe"))
    record.add_phone("0505055500", "main")
    record.add_phone("0976787886", "work")
    record.add_email("jane@example.com")
    record.add_address("Main st. 5")
    record.add_birthday("21.11.2006")

    result = registry.get_command("show-contact").run(
        ["--name", "jane", "doe"], data
    )

    assert result == (
        "Jane Doe\n"
        "    phones:\n"
        "              main 0505055500\n"
        "              work 0976787886\n"
        "    email:    jane@example.com\n"
        "    address:  Main st. 5\n"
        "    birthday: 21.11.2006"
    )
    assert result == registry.get_command("search-contacts").run(
        ["--name", "Jane Doe"], data
    )


def test_show_contact_displays_missing_fields(registry, data, monkeypatch):
    monkeypatch.setattr(formatting.sys.stdout, "isatty", lambda: False)
    data.address_book.add_record(Record("Bob"))

    result = registry.get_command("show-contact").run(["--name", "Bob"], data)

    assert result == (
        "Bob\n"
        "    phones:\n"
        "              —\n"
        "    email:    —\n"
        "    address:  —\n"
        "    birthday: —"
    )


@pytest.mark.parametrize("args", [[], ["--name"], ["--unknown", "Bob"]])
def test_show_contact_rejects_invalid_arguments(registry, data, args):
    result = registry.get_command("show-contact").run(args, data)

    assert result.startswith("❌ Invalid arguments.")
    assert "Usage: show-contact --name <name>" in result


def test_show_contact_requires_existing_contact(registry, data):
    result = registry.get_command("show-contact").run(
        ["--name", "Nobody"], data
    )

    assert result == "❌ Contact 'Nobody' not found."
