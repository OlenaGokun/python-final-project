import unittest
from address_book.book import AddressBook
from address_book.record import Record
from address_book.commands.add_contact import add_contact
from address_book.commands.change_contact import change_contact
from address_book.commands.add_birthday import add_birthday
from address_book.commands.show_phone import show_phone
from address_book.commands.show_birthday import show_birthday
from address_book.commands.show_all import show_all
from address_book.commands.show_birthdays import show_birthdays


class TestAddContactCommand(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()

    def test_adds_new_contact_with_phone(self):
        result = add_contact(["John", "1234567890"], self.book)
        self.assertEqual(result, "Contact added.")
        self.assertIsNotNone(self.book.find("John"))

    def test_adds_phone_to_existing_contact(self):
        record = Record("John")
        self.book.add_record(record)
        result = add_contact(["John", "1234567890"], self.book)
        self.assertEqual(result, "Contact updated.")
        self.assertEqual(len(self.book.find("John").phones), 1)

    def test_different_case_updates_existing_contact(self):
        add_contact(["John", "1234567890"], self.book)
        result = add_contact(["john", "5555555555"], self.book)
        self.assertEqual(result, "Contact updated.")
        self.assertEqual(len(self.book), 1)
        self.assertEqual(len(self.book.find("JOHN").phones), 2)

    def test_adds_contact_without_phone(self):
        result = add_contact(["John"], self.book)
        self.assertEqual(result, "Contact added.")
        record = self.book.find("John")
        self.assertIsNotNone(record)
        self.assertEqual(len(record.phones), 0)

    def test_missing_name_raises_error(self):
        result = add_contact([], self.book)
        self.assertTrue(result.startswith("Usage:"), result)


    def test_invalid_phone_raises_error(self):
        result = add_contact(["John", "123"], self.book)
        # Invalid phone should raise error with helpful message
        self.assertIn("exactly 10 digits", result)

    def test_invalid_phone_does_not_create_contact(self):
        add_contact(["John", "123"], self.book)
        self.assertIsNone(self.book.find("John"))

    def test_too_many_args_shows_usage(self):
        result = add_contact(["John", "Smith", "1234567890"], self.book)
        self.assertEqual(result, "Usage: add <name> [phone]")
        self.assertEqual(len(self.book), 0)


class TestChangeContactCommand(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        self.record = Record("John")
        self.record.add_phone("1234567890")
        self.book.add_record(self.record)

    def test_changes_phone_number(self):
        result = change_contact(["John", "1234567890", "9876543210"], self.book)
        self.assertEqual(result, "Contact updated.")
        record = self.book.find("John")
        self.assertIn("9876543210", [p.value for p in record.phones])
        self.assertNotIn("1234567890", [p.value for p in record.phones])

    def test_contact_not_found(self):
        result = change_contact(["Nobody", "1234567890", "9876543210"], self.book)
        self.assertEqual(result, "Contact not found.")

    def test_missing_arguments(self):
        result = change_contact(["John", "1234567890"], self.book)
        self.assertTrue(result.startswith("Usage:"), result)

    def test_empty_args_raises_error(self):
        result = change_contact([], self.book)
        self.assertTrue(result.startswith("Usage:"), result)

    def test_old_phone_not_found(self):
        result = change_contact(["John", "9999999999", "1111111111"], self.book)
        self.assertIn("not found", result.lower())


class TestAddBirthdayCommand(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        self.record = Record("John")
        self.book.add_record(self.record)

    def test_adds_birthday_to_existing_contact(self):
        result = add_birthday(["John", "15.03.1990"], self.book)
        self.assertEqual(result, "Birthday added.")
        self.assertIsNotNone(self.book.find("John").birthday)

    def test_contact_not_found(self):
        result = add_birthday(["Nobody", "15.03.1990"], self.book)
        self.assertEqual(result, "Contact not found.")

    def test_missing_name_raises_error(self):
        result = add_birthday(["15.03.1990"], self.book)
        self.assertTrue(result.startswith("Usage:"), result)

    def test_missing_birthday_raises_error(self):
        result = add_birthday(["John"], self.book)
        self.assertTrue(result.startswith("Usage:"), result)

    def test_empty_args_raises_error(self):
        result = add_birthday([], self.book)
        self.assertTrue(result.startswith("Usage:"), result)

    def test_invalid_birthday_format_raises_error(self):
        result = add_birthday(["John", "1990-03-15"], self.book)
        # Invalid date format raises ValueError in Birthday class
        self.assertEqual(result, "Invalid date format. Use DD.MM.YYYY")


class TestShowPhoneCommand(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        self.record = Record("John")
        self.record.add_phone("1234567890")
        self.record.add_phone("5555555555")
        self.book.add_record(self.record)

    def test_shows_phone(self):
        result = show_phone(["John"], self.book)
        self.assertIn("1234567890", result)
        self.assertIn("5555555555", result)

    def test_contact_not_found(self):
        result = show_phone(["Nobody"], self.book)
        self.assertEqual(result, "Contact not found.")

    def test_contact_without_phones(self):
        self.book.add_record(Record("Jane"))
        self.assertEqual(show_phone(["jane"], self.book), "No phone numbers found for Jane.")

    def test_missing_name_raises_error(self):
        result = show_phone([], self.book)
        self.assertTrue(result.startswith("Usage:"), result)



class TestShowBirthdayCommand(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        self.record = Record("John")
        self.record.add_birthday("15.03.1990")
        self.book.add_record(self.record)

    def test_shows_birthday(self):
        result = show_birthday(["John"], self.book)
        self.assertIn("15.03.1990", result)

    def test_contact_without_birthday(self):
        record = Record("Jane")
        self.book.add_record(record)
        result = show_birthday(["Jane"], self.book)
        self.assertEqual(result, "Jane has no birthday set.")

    def test_lookup_is_case_insensitive_and_shows_stored_name(self):
        result = show_birthday(["john"], self.book)
        self.assertEqual(result, "John's birthday: 15.03.1990")

    def test_contact_not_found(self):
        result = show_birthday(["Nobody"], self.book)
        self.assertEqual(result, "Contact not found.")

    def test_missing_name_raises_error(self):
        result = show_birthday([], self.book)
        self.assertTrue(result.startswith("Usage:"), result)



class TestShowAllCommand(unittest.TestCase):
    def test_empty_book(self):
        book = AddressBook()
        result = show_all(book)
        self.assertEqual(result, "No contacts found.")

    def test_shows_all_contacts(self):
        book = AddressBook()
        john = Record("John")
        john.add_phone("1234567890")
        jane = Record("Jane")
        jane.add_phone("9876543210")
        book.add_record(john)
        book.add_record(jane)
        result = show_all(book)
        self.assertIn("John", result)
        self.assertIn("Jane", result)
        self.assertIn("1234567890", result)
        self.assertIn("9876543210", result)


class TestShowBirthdaysCommand(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()

    def test_no_upcoming_birthdays(self):
        record = Record("John")
        record.add_birthday("15.03.1990")  # Far in the past
        self.book.add_record(record)
        result = show_birthdays(self.book)
        self.assertEqual(result, "No upcoming birthdays in the next 7 days.")

    def test_empty_book(self):
        result = show_birthdays(self.book)
        self.assertEqual(result, "No upcoming birthdays in the next 7 days.")


if __name__ == "__main__":
    unittest.main()
