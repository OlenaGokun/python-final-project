import pytest

from personal_helper.models import PersonalHelper, Record


def test_add_address_updates_existing_contact(registry, data):
    data.address_book.add_record(Record("Jane"))

    result = registry.get_command("add-address").run(
        ["--name", "Jane", "--address", "Main", "st.", "5"], data
    )

    assert result == "✅ Address added for Jane."
    assert data.address_book["Jane"].address.value == "Main st. 5"


def test_add_address_replaces_existing_address(registry, data):
    record = data.address_book.add_record(Record("Jane"))
    record.add_address("Old address")

    result = registry.get_command("add-address").run(
        ["--name", "Jane", "--address", "New", "address"], data
    )

    assert result == "✅ Address added for Jane."
    assert record.address.value == "New address"


def test_add_address_requires_contact(registry, data):
    result = registry.get_command("add-address").run(
        ["--name", "Nobody", "--address", "Main", "st."], data
    )

    assert result == "❌ Contact 'Nobody' not found."


@pytest.mark.parametrize("args", [[], ["--name", "Jane"]])
def test_add_address_requires_name_and_address(registry, data, args):
    result = registry.get_command("add-address").run(args, data)

    assert "Usage: add-address --name <name> --address <address>" in result


def test_add_address_rejects_empty_address(registry, data):
    data.address_book.add_record(Record("Jane"))

    result = registry.get_command("add-address").run(
        ["--name", "Jane", "--address", "   "], data
    )

    assert result.startswith("❌")
    assert data.address_book["Jane"].address is None


def test_delete_address_removes_existing_address(registry, data):
    record = data.address_book.add_record(Record("Jane"))
    record.add_address("Main st. 5")

    result = registry.get_command("delete-address").run(["--name", "Jane"], data)

    assert result == "✅ Address removed for Jane."
    assert record.address is None


def test_delete_address_requires_existing_address(registry, data):
    data.address_book.add_record(Record("Jane"))

    result = registry.get_command("delete-address").run(["--name", "Jane"], data)

    assert result == "❌ Address not set for Jane."
