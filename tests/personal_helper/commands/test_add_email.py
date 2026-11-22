"""Tests for the add-email command."""

import pytest

from personal_helper.models import PersonalHelper


def test_add_email_updates_existing_contact(registry, book_with_contacts):
    result = registry.get_command("add-email").run(
        ["--name", "John", "--email", "john@example.com"],
        PersonalHelper(book_with_contacts),
    )

    assert result == "✅ Email added for John."
    assert book_with_contacts["John"].email.value == "john@example.com"


def test_add_email_uses_case_insensitive_contact_lookup(registry, book_with_contacts):
    result = registry.get_command("add-email").run(
        ["--name", "john", "--email", "john@example.com"],
        PersonalHelper(book_with_contacts),
    )

    assert result == "✅ Email added for John."
    assert book_with_contacts["John"].email.value == "john@example.com"


def test_add_email_reports_missing_contact(registry, data):
    result = registry.get_command("add-email").run(
        ["--name", "Nobody", "--email", "nobody@example.com"], data
    )

    assert result == "❌ Contact 'Nobody' not found."


@pytest.mark.parametrize(
    "args",
    [
        ["--name", "John"],
        [],
    ],
)
def test_add_email_requires_name_and_email(registry, data, args):
    result = registry.get_command("add-email").run(args, data)

    assert "Usage: add-email --name <name> --email <email>" in result


def test_add_email_rejects_invalid_email(registry, book_with_contacts):
    result = registry.get_command("add-email").run(
        ["--name", "John", "--email", "invalid-email"],
        PersonalHelper(book_with_contacts),
    )

    assert "Invalid email format" in result
    assert book_with_contacts["John"].email is None
