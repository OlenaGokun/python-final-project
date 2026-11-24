import unittest

from personal_helper.models.fields import Name, Phone
from personal_helper.models.record import Record
from personal_helper.core import (
    CommandError,
    DuplicatePhoneError,
    InvalidBirthdayFormatError,
    InvalidNameError,
    InvalidPhoneFormatError,
    PhoneNotFoundError,
)

class TestRecordCreation(unittest.TestCase):
    def test_name_is_stored_as_a_name_object(self):
        record = Record("John")
        self.assertIsInstance(record.name, Name)
        self.assertEqual(record.name.value, "John")

    def test_phones_start_empty(self):
        self.assertEqual(Record("John").phones, ())

    def test_phones_cannot_be_mutated_from_outside(self):
        record = Record("John")
        with self.assertRaises(AttributeError):
            record.phones.append(Phone("1234567890"))
        self.assertEqual(record.phones, ())

    def test_attributes_are_read_only(self):
        record = Record("John")
        for attr in ("name", "phones", "birthday"):
            with self.subTest(attr=attr), self.assertRaises(AttributeError):
                setattr(record, attr, None)

    def test_invalid_name_is_rejected(self):
        with self.assertRaises(InvalidNameError):
            Record("")

class TestAddPhone(unittest.TestCase):
    def setUp(self):
        self.record = Record("John")

    def test_stores_phone_objects(self):
        self.record.add_phone("1234567890")
        self.assertIsInstance(self.record.phones[0], Phone)
        self.assertEqual(self.record.phones[0].value, "1234567890")

    def test_keeps_insertion_order(self):
        self.record.add_phone("1234567890")
        self.record.add_phone("5555555555")
        self.assertEqual(
            [p.value for p in self.record.phones], ["1234567890", "5555555555"]
        )

    def test_invalid_phone_is_rejected(self):
        with self.assertRaises(InvalidPhoneFormatError):
            self.record.add_phone("123")
        self.assertEqual(self.record.phones, ())

    def test_duplicate_phone_is_rejected(self):
        self.record.add_phone("1234567890")
        with self.assertRaises(DuplicatePhoneError):
            self.record.add_phone("1234567890")
        self.assertEqual(len(self.record.phones), 1)

    def test_normalizes_phone_and_rejects_duplicate_in_another_format(self):
        self.record.add_phone("+38(050)123-45-67")
        self.assertEqual(self.record.phones[0].value, "0501234567")
        with self.assertRaises(DuplicatePhoneError):
            self.record.add_phone("0501234567")

class TestFindPhone(unittest.TestCase):
    def setUp(self):
        self.record = Record("John")
        self.record.add_phone("1234567890")
        self.record.add_phone("5555555555")

    def test_returns_the_matching_phone(self):
        found = self.record.find_phone("5555555555")
        self.assertIsInstance(found, Phone)
        self.assertEqual(found.value, "5555555555")

    def test_unknown_phone_returns_none(self):
        self.assertIsNone(self.record.find_phone("0000000000"))

    def test_invalid_selector_returns_none(self):
        for selector in (None, "not-a-phone"):
            with self.subTest(selector=selector):
                self.assertIsNone(self.record.find_phone(selector))

    def test_alias_matches_case_insensitively(self):
        phone = self.record.add_phone("1112223333", "Work")
        self.assertIs(self.record.find_phone("work"), phone)

class TestRemovePhone(unittest.TestCase):
    def setUp(self):
        self.record = Record("John")
        self.record.add_phone("1234567890")
        self.record.add_phone("5555555555")

    def test_removes_the_phone(self):
        self.record.remove_phone("1234567890")
        self.assertEqual([p.value for p in self.record.phones], ["5555555555"])

    def test_unknown_phone_raises(self):
        with self.assertRaises(PhoneNotFoundError):
            self.record.remove_phone("0000000000")
        self.assertEqual(len(self.record.phones), 2)

class TestEditPhone(unittest.TestCase):
    def setUp(self):
        self.record = Record("John")
        self.record.add_phone("1234567890")
        self.record.add_phone("5555555555")

    def test_replaces_the_phone(self):
        self.record.edit_phone("1234567890", "1112223333")
        self.assertIsNone(self.record.find_phone("1234567890"))
        self.assertIsNotNone(self.record.find_phone("1112223333"))

    def test_preserves_position(self):
        self.record.edit_phone("1234567890", "1112223333")
        self.assertEqual(
            [p.value for p in self.record.phones], ["1112223333", "5555555555"]
        )

    def test_unknown_phone_raises(self):
        with self.assertRaises(PhoneNotFoundError):
            self.record.edit_phone("0000000000", "1112223333")

    def test_invalid_replacement_is_rejected_without_changing_anything(self):
        with self.assertRaises(InvalidPhoneFormatError):
            self.record.edit_phone("1234567890", "123")
        self.assertEqual(
            [p.value for p in self.record.phones], ["1234567890", "5555555555"]
        )

class TestUpdateDetails(unittest.TestCase):
    def setUp(self):
        self.record = Record("John")

    def test_adds_multiple_phones_email_and_birthday(self):
        self.record.update_details(
            phones=["1234567890", "5555555555"],
            email="john@example.com",
            birthday="15.03.1990",
        )

        self.assertEqual(
            [phone.value for phone in self.record.phones],
            ["1234567890", "5555555555"],
        )
        self.assertEqual(self.record.email.value, "john@example.com")
        self.assertEqual(str(self.record.birthday), "15.03.1990")

    def test_invalid_optional_value_does_not_partially_update(self):
        with self.assertRaises(InvalidBirthdayFormatError):
            self.record.update_details(
                phones=["1234567890"],
                email="john@example.com",
                birthday="31.02.1990",
            )

        self.assertEqual(self.record.phones, ())
        self.assertIsNone(self.record.email)
        self.assertIsNone(self.record.birthday)

    def test_duplicate_phone_does_not_partially_update(self):
        self.record.add_phone("1234567890")

        with self.assertRaises(DuplicatePhoneError):
            self.record.update_details(
                phones=["5555555555", "1234567890"],
                email="john@example.com",
            )

        self.assertEqual(
            [phone.value for phone in self.record.phones], ["1234567890"]
        )
        self.assertIsNone(self.record.email)

class TestRemoveOptionalDetails(unittest.TestCase):
    def test_removing_unset_birthday_or_email_raises(self):
        record = Record("John")
        for method, message in (
            (record.remove_birthday, "Birthday not set for John."),
            (record.remove_email, "Email not set for John."),
        ):
            with self.subTest(method=method.__name__):
                with self.assertRaises(CommandError) as error:
                    method()
                self.assertEqual(str(error.exception), message)

class TestRecordStr(unittest.TestCase):
    def test_matches_the_expected_format(self):
        record = Record("John")
        record.add_phone("1112223333")
        record.add_phone("5555555555")
        self.assertEqual(
            str(record), "Contact name: John, phones: 1112223333; 5555555555"
        )

    def test_record_without_phones(self):
        self.assertEqual(str(Record("John")), "Contact name: John, phones: ")

if __name__ == "__main__":
    unittest.main()


def test_copy_with_name_preserves_legacy_details_and_owns_its_phone_list():
    original = Record("Mary Jane")
    original.add_phone("5012345671")
    original.add_phone("5099999999")
    original.add_birthday("01.01.2000")
    original.add_address("Main st. 5")
    del original._email

    replacement = original.copy_with_name("Mary Doe")

    assert replacement.name.value == "Mary Doe"
    assert original.name.value == "Mary Jane"
    assert replacement.phones == original.phones
    assert replacement.birthday == original.birthday
    assert replacement.address == original.address
    assert replacement.email is None
    replacement.remove_phone("5012345671")
    assert len(original.phones) == 2
