import pytest

from personal_helper.models import Address, Field, Record
from personal_helper.core import CommandError, InvalidInputError


def test_address_strips_surrounding_whitespace():
    assert Address("  Main st. 5  ").value == "Main st. 5"


def test_address_equality_and_hashability():
    assert Address("Main st. 5") == Address("Main st. 5")
    assert Address("Main st. 5") != Field("Main st. 5")
    assert len({Address("Main st. 5"), Address("Main st. 5")}) == 1


@pytest.mark.parametrize("value", ["", "   ", None, 123])
def test_address_rejects_empty_or_non_string_values(value):
    with pytest.raises(InvalidInputError, match="Address must be a non-empty string"):
        Address(value)


def test_record_add_and_remove_address():
    record = Record("Jane")

    address = record.add_address("Main st. 5")

    assert record.address == address
    assert "address: Main st. 5" in str(record)
    assert "address='Main st. 5'" in repr(record)
    assert record.remove_address() == address
    assert record.address is None


def test_record_rejects_removing_an_unset_address():
    with pytest.raises(CommandError, match="Address not set"):
        Record("Jane").remove_address()


def test_record_copy_with_name_preserves_address():
    record = Record("Jane")
    record.add_address("Main st. 5")

    renamed = record.copy_with_name("Jane Doe")

    assert renamed.address == record.address


def test_record_without_address_reads_legacy_state():
    record = Record("Jane")
    del record._address

    assert record.address is None
