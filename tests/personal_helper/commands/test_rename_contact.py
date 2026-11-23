import pytest

from personal_helper.models import Record


def test_rename_contact_through_registry(registry, data):
    data.address_book.add_record(Record("Mary Jane"))
    command = registry.get_command("rename-contact")

    result = command.run("--name mary jane --new-name Mary Doe".split(), data)

    assert "renamed" in result
    assert data.address_book.find("Mary Jane") is None
    assert data.address_book["Mary Doe"].name.value == "Mary Doe"
    assert "unchanged" in command.run("--name Mary Doe --new-name Mary Doe".split(), data)
    assert command.get_usage() in registry.get_command("help").run(["--command", "rename-contact"], data)


@pytest.mark.parametrize(
    ("args", "message"),
    [
        ("--name Missing --new-name New Name", "not found"),
        ("--name Mary Jane --new-name MARY DOE", "already exists"),
        ("--name Mary Jane --new-name", "--new-name requires a value"),
    ],
)
def test_rename_contact_reports_errors(registry, data, args, message):
    original = data.address_book.add_record(Record("Mary Jane"))
    other = data.address_book.add_record(Record("Mary Doe"))

    result = registry.get_command("rename-contact").run(args.split(), data)

    assert message in result
    assert list(data.address_book.values()) == [original, other]
