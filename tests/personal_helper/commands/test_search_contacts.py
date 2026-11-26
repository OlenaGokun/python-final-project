"""Tests for the contact search command."""

import pytest

from colorama import Fore, Style

from personal_helper.commands.base_command import AddressBookCommand
from personal_helper.core import formatting
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
    jane.add_address("Main st. 5")
    book.add_record(jane)

    return book


def test_search_command_returns_matching_contact(
    registry, book_with_search_contacts
):
    result = registry.get_command("search-contacts").run(
        ["--query", "jane@work.org"], PersonalHelper(book_with_search_contacts)
    )

    assert "Jane Smith" in result
    assert "jane@work.org" in result
    assert "address:" in result
    assert "Main st. 5" in result
    assert "birthday:" in result


def test_search_command_joins_multiword_query(
    registry, book_with_search_contacts
):
    result = registry.get_command("search-contacts").run(
        ["--query", "Jane", "Smith"], PersonalHelper(book_with_search_contacts)
    )

    assert "Jane Smith" in result


def test_search_command_reports_no_matches(
    registry, book_with_search_contacts
):
    result = registry.get_command("search-contacts").run(
        ["--query", "unknown_xyz"], PersonalHelper(book_with_search_contacts)
    )

    assert result == "ℹ️  No contacts found."


def test_search_command_requires_query_or_field(
    registry, book_with_search_contacts
):
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
        ("--address", "main ST.", "Jane Smith"),
    ],
)
def test_search_command_matches_field_filters(
    registry, book_with_search_contacts, field, value, expected_name
):
    result = registry.get_command("search-contacts").run(
        [field, value], PersonalHelper(book_with_search_contacts)
    )

    assert expected_name in result


def test_search_command_renders_contact_fields_in_vertical_layout(
    registry, book_with_search_contacts
):
    result = registry.get_command("search-contacts").run(
        ["--name", "Jane"], PersonalHelper(book_with_search_contacts)
    )

    assert result == (
        "Jane Smith\n"
        "    phones:\n"
        "              0987654321\n"
        "    email:    jane@work.org\n"
        "    address:  Main st. 5\n"
        "    birthday: —"
    )


def test_contact_detail_colors_are_applied_in_terminal(monkeypatch):
    class Terminal:
        @staticmethod
        def isatty():
            return True

    monkeypatch.setattr(formatting.sys, "stdout", Terminal())
    record = Record("Jane")
    record.add_phone("0505055500", "main")

    result = AddressBookCommand.format_contact_details(record)

    assert f"{Fore.BLUE}{Style.BRIGHT}Jane{Style.RESET_ALL}" in result
    assert f"{Fore.BLUE}address:{Style.RESET_ALL}" in result
    assert f"{Fore.BLUE}main{Style.RESET_ALL} 0505055500" in result


def test_search_displays_multiple_phone_aliases_and_contacts(registry, data):
    jane = data.address_book.add_record(Record("Jane Doe"))
    jane.add_phone("0505055500", "main")
    jane.add_phone("0976787886", "work")
    jane.add_email("jane@example.com")
    jane.add_address("Main st. 5")
    jane.add_birthday("21.11.2006")
    data.address_book.add_record(Record("James Doe"))

    result = registry.get_command("search-contacts").run(
        ["--name", "Doe"], data
    )

    assert result == (
        "Jane Doe\n"
        "    phones:\n"
        "              main 0505055500\n"
        "              work 0976787886\n"
        "    email:    jane@example.com\n"
        "    address:  Main st. 5\n"
        "    birthday: 21.11.2006\n\n"
        "James Doe\n"
        "    phones:\n"
        "              —\n"
        "    email:    —\n"
        "    address:  —\n"
        "    birthday: —"
    )


def test_search_command_combines_field_filters_with_and(
    registry, book_with_search_contacts
):
    result = registry.get_command("search-contacts").run(
        ["--name", "John", "--email", "work.org"],
        PersonalHelper(book_with_search_contacts),
    )

    assert result == "ℹ️  No contacts found."
