"""Tests for the application data model."""

from personal_helper.models import AddressBook, Notebook, PersonalHelper


def test_default_collections_are_independent():
    first = PersonalHelper()
    second = PersonalHelper()

    first.notebook.add("shopping", "Buy milk")
    assert len(second.notebook) == 0
    assert first.address_book is not second.address_book
    assert not hasattr(first.address_book, "notes")


def test_supplied_empty_collections_are_preserved():
    address_book = AddressBook()
    notebook = Notebook()

    data = PersonalHelper(address_book, notebook)

    assert data.address_book is address_book
    assert data.notebook is notebook
