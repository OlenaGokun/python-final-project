"""Tests for searching contacts in the address book."""

import pytest

from personal_helper.models import Record


@pytest.fixture
def book_with_search_contacts(book):
    john = Record("John")
    john.add_phone("1234567890")
    john.add_email("john.doe@example.com")
    john.add_birthday("15.03.1990")
    john.add_address("First street")
    book.add_record(john)

    jane = Record("Jane Smith")
    jane.add_phone("0987654321")
    jane.add_email("jane@work.org")
    book.add_record(jane)

    return book


@pytest.mark.parametrize(
    ("query", "expected_name"),
    [
        ("john", "John"),
        ("7654", "Jane Smith"),
        ("JOHN.DOE@EXAMPLE.COM", "John"),
        ("15.03.1990", "John"),
        ("first street", "John"),
    ],
)
def test_search_matches_contact_fields(book_with_search_contacts, query, expected_name):
    matches = book_with_search_contacts.search(query)

    assert [record.name.value for record in matches] == [expected_name]


def test_search_returns_multiple_contacts(book_with_search_contacts):
    matches = book_with_search_contacts.search("j")

    assert [record.name.value for record in matches] == ["John", "Jane Smith"]


@pytest.mark.parametrize("query", ["", "   ", None])
def test_search_returns_no_matches_for_empty_query(book_with_search_contacts, query):
    assert book_with_search_contacts.search(query) == []


def test_search_supports_address_field_filter(book_with_search_contacts):
    assert [
        record.name.value
        for record in book_with_search_contacts.search(address="STREET")
    ] == ["John"]
