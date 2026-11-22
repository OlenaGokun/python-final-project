"""Tests for email fields and contact email behavior."""

import pytest

from personal_helper.models import Email, Field, Record


def test_email_field_accepts_valid_email():
    email = Email("user@example.com")

    assert email.value == "user@example.com"
    assert str(email) == "user@example.com"


def test_email_field_strips_surrounding_whitespace():
    assert Email("  user@example.com  ").value == "user@example.com"


def test_email_field_equality_and_hashability():
    assert Email("user@example.com") == Email("user@example.com")
    assert Email("user@example.com") != Field("user@example.com")
    assert len({Email("user@example.com"), Email("user@example.com")}) == 1


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        "plainaddress",
        "@missing-local.com",
        "missing-domain@",
        "user@domain",
        "user name@example.com",
        "user@@example.com",
        None,
        12345,
    ],
)
def test_email_field_rejects_invalid_values(value):
    with pytest.raises(ValueError, match="Invalid email format"):
        Email(value)


def test_record_email_starts_unset():
    record = Record("John")

    assert record.email is None
    assert "email:" not in str(record)


def test_record_add_email_updates_email_string_and_repr():
    record = Record("John")

    added = record.add_email("john@example.com")

    assert isinstance(added, Email)
    assert record.email == Email("john@example.com")
    assert "email: john@example.com" in str(record)
    assert "email='john@example.com'" in repr(record)


def test_record_add_email_replaces_existing_email():
    record = Record("John")
    record.add_email("first@example.com")

    record.add_email("second@example.com")

    assert record.email.value == "second@example.com"
    assert "second@example.com" in str(record)
    assert "first@example.com" not in str(record)


def test_record_rejects_invalid_email_without_setting_it():
    record = Record("John")

    with pytest.raises(ValueError, match="Invalid email format"):
        record.add_email("not-an-email")

    assert record.email is None
