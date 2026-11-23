import unittest
from collections import UserDict


import pytest
from personal_helper.models.book import AddressBook
from personal_helper.models.record import Record
from personal_helper.core import ContactNotFoundError, DuplicateContactError, InvalidNameError

class AddressBookTestCase(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        self.john = Record("John")
        self.john.add_phone("1234567890")
        self.book.add_record(self.john)

class TestAddRecord(AddressBookTestCase):
    def test_is_a_userdict(self):
        self.assertIsInstance(self.book, UserDict)

    def test_stores_the_record_under_its_casefolded_name(self):
        self.assertIs(self.book.data["john"], self.john)

    def test_supports_len_and_membership(self):
        self.assertEqual(len(self.book), 1)
        self.assertIn("John", self.book)
        self.assertIn("JOHN", self.book)

    def test_duplicate_name_raises_error(self):
        replacement = Record("John")
        replacement.add_phone("9999999999")
        with self.assertRaises(DuplicateContactError) as context:
            self.book.add_record(replacement)
        self.assertIn("already exists", str(context.exception))

    def test_duplicate_name_in_other_case_raises_error(self):
        with self.assertRaises(DuplicateContactError):
            self.book.add_record(Record("JOHN"))
        self.assertIs(self.book.find("john"), self.john)

class TestFind(AddressBookTestCase):
    def test_returns_the_record(self):
        self.assertIs(self.book.find("John"), self.john)

    def test_unknown_name_returns_none(self):
        self.assertIsNone(self.book.find("Nobody"))

    def test_lookup_is_case_insensitive(self):
        self.assertIs(self.book.find("john"), self.john)
        self.assertIs(self.book.find("JOHN"), self.john)

    def test_item_access_is_case_insensitive(self):
        self.assertIs(self.book["jOhN"], self.john)

    def test_unknown_item_raises_contact_not_found_error(self):
        with self.assertRaises(ContactNotFoundError) as context:
            _ = self.book["Nobody"]
        self.assertIn("Nobody", str(context.exception))

    def test_item_assignment_is_case_insensitive(self):
        jane = Record("Jane")

        self.book["JANE"] = jane

        self.assertIs(self.book["jane"], jane)
        self.assertIn("Jane", self.book)

class TestDelete(AddressBookTestCase):
    def test_removes_the_record(self):
        self.book.delete("John")
        self.assertEqual(len(self.book), 0)
        self.assertIsNone(self.book.find("John"))

    def test_delete_is_case_insensitive(self):
        self.assertIs(self.book.delete("JOHN"), self.john)
        self.assertEqual(len(self.book), 0)

    def test_returns_the_removed_record(self):
        self.assertIs(self.book.delete("John"), self.john)

    def test_unknown_name_returns_none(self):
        self.assertIsNone(self.book.delete("Nobody"))
        self.assertEqual(len(self.book), 1)

    def test_item_deletion_is_case_insensitive(self):
        del self.book["jOhN"]

        self.assertNotIn("John", self.book)
        self.assertEqual(len(self.book), 0)

class TestAddressBookStr(unittest.TestCase):
    def test_empty_book(self):
        self.assertEqual(str(AddressBook()), "Address book is empty.")

    def test_lists_every_record(self):
        book = AddressBook()
        jane = Record("Jane")
        jane.add_phone("9876543210")
        book.add_record(jane)
        self.assertEqual(str(book), "Contact name: Jane, phones: 9876543210")

if __name__ == "__main__":
    unittest.main()


def test_rename_rekeys_contact_and_preserves_details(book):
    original = Record("Mary Jane")
    original.update_details(["5012345671"], "mary@example.test", "01.01.2000")
    book.add_record(original)

    renamed = book.rename(" MARY JANE ", "Mary Doe")

    assert renamed is book["mary doe"]
    assert renamed is not original
    assert book.find("Mary Jane") is None
    assert (renamed.phones, renamed.email, renamed.birthday) == (
        original.phones, original.email, original.birthday
    )
    assert book.rename("Mary Doe", " Mary Doe ") is renamed
    assert book.rename("Mary Doe", "MARY DOE").name.value == "MARY DOE"
    assert len(book) == 1


def test_rename_rejects_invalid_or_taken_names_without_mutation(book):
    original = book.add_record(Record("Mary Jane"))
    other = book.add_record(Record("Mary Doe"))

    with pytest.raises(DuplicateContactError):
        book.rename("Mary Jane", " MARY DOE ")
    with pytest.raises(InvalidNameError):
        book.rename("Mary Jane", " ")
    with pytest.raises(ContactNotFoundError):
        book.rename("Missing", "New name")
    assert list(book.values()) == [original, other]


@pytest.mark.parametrize("name", ["Mary Doe", "MARY JANE"])
def test_rename_restores_original_when_add_fails(book, monkeypatch, name):
    original = book.add_record(Record("Mary Jane"))
    other = book.add_record(Record("Other Contact"))
    add_record = book.add_record

    def fail_after_insert(record):
        add_record(record)
        raise RuntimeError("replacement could not be added")

    monkeypatch.setattr(book, "add_record", fail_after_insert)
    with pytest.raises(RuntimeError, match="could not be added"):
        book.rename("Mary Jane", name)
    assert book["Mary Jane"] is original
    assert book["Other Contact"] is other
    assert len(book) == 2
