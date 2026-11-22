"""Tests for the contact search command."""

import pytest

from personal_helper.models import PersonalHelper, Record


@pytest.fixture
def book_with_search_contacts(book):
    john = Record("John")
    john.add_phone("1234567890")
    john.add_email("john.doe@example.com")
    john.add_birthday("15.03.1990")
    book.add_record(john)

    jane = Record("Jane Smith")
    jane.add_phone("0987654321")
    jane.add_email("jane@work.org")
    book.add_record(jane)

    return book


def test_search_command_returns_matching_contact(registry, book_with_search_contacts):
    result = registry.get_command("search-contacts").run(
        ["--query", "jane@work.org"], PersonalHelper(book_with_search_contacts)
    )

    assert "Jane Smith" in result
    assert "jane@work.org" in result


def test_search_command_joins_multiword_query(registry, book_with_search_contacts):
    result = registry.get_command("search-contacts").run(
        ["--query", "Jane", "Smith"], PersonalHelper(book_with_search_contacts)
    )

    assert "Jane Smith" in result


def test_search_command_reports_no_matches(registry, book_with_search_contacts):
    result = registry.get_command("search-contacts").run(
        ["--query", "unknown_xyz"], PersonalHelper(book_with_search_contacts)
    )

    assert result == "ℹ️  No contacts found."


def test_search_command_requires_query_or_field(registry, book_with_search_contacts):
    result = registry.get_command("search-contacts").run(
        [], PersonalHelper(book_with_search_contacts)
    )

    assert "Provide --query or at least one field" in result
    assert "Usage: search-contacts" in result


def test_search_command_rejects_query_with_field_filter(
    registry, book_with_search_contacts
):
    result = registry.get_command("search-contacts").run(
        ["--query", "john", "--name", "John"],
        PersonalHelper(book_with_search_contacts),
    )

    assert "--query cannot be combined with field filters" in result


@pytest.mark.parametrize(
    ("field", "value", "expected_name"),
    [
        ("--name", "JOH", "John"),
        ("--email", "DOE@", "John"),
        ("--phone", "7654", "Jane Smith"),
        ("--birthday", "15.03", "John"),
    ],
)
def test_search_command_matches_field_filters(
    registry, book_with_search_contacts, field, value, expected_name
):
    result = registry.get_command("search-contacts").run(
        [field, value], PersonalHelper(book_with_search_contacts)
    )

    assert expected_name in result


def test_search_command_combines_field_filters_with_and(
    registry, book_with_search_contacts
):
    result = registry.get_command("search-contacts").run(
        ["--name", "John", "--email", "work.org"],
        PersonalHelper(book_with_search_contacts),
    )

    assert result == "ℹ️  No contacts found."
