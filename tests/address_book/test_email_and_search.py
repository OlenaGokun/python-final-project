import unittest

from address_book.book import AddressBook
from address_book.commands.add_email import add_email
from address_book.commands.search import search_contacts
from address_book.fields import Email, Field
from address_book.record import Record


class TestEmailField(unittest.TestCase):
    def test_accepts_valid_email(self):
        email = Email("user@example.com")
        self.assertEqual(email.value, "user@example.com")
        self.assertEqual(str(email), "user@example.com")

    def test_strips_surrounding_whitespace(self):
        email = Email("  user@example.com  ")
        self.assertEqual(email.value, "user@example.com")

    def test_equality_and_hashability(self):
        self.assertEqual(Email("user@example.com"), Email("user@example.com"))
        self.assertNotEqual(Email("user@example.com"), Field("user@example.com"))
        self.assertEqual(len({Email("user@example.com"), Email("user@example.com")}), 1)

    def test_invalid_emails_raise_value_error(self):
        invalid_values = [
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
        ]
        for invalid in invalid_values:
            with self.subTest(value=invalid):
                with self.assertRaises(ValueError) as ctx:
                    Email(invalid)
                self.assertIn("Invalid email format", str(ctx.exception))


class TestRecordEmail(unittest.TestCase):
    def setUp(self):
        self.record = Record("John")
        self.record.add_phone("1234567890")

    def test_initial_email_is_none(self):
        self.assertIsNone(self.record.email)
        self.assertNotIn("email:", str(self.record))

    def test_add_email_sets_email_and_updates_str_and_repr(self):
        added = self.record.add_email("john@example.com")
        self.assertIsInstance(added, Email)
        self.assertEqual(self.record.email, Email("john@example.com"))
        self.assertIn("email: john@example.com", str(self.record))
        self.assertIn("email='john@example.com'", repr(self.record))

    def test_add_email_overwrites_existing_email(self):
        self.record.add_email("first@example.com")
        self.record.add_email("second@example.com")
        self.assertEqual(self.record.email.value, "second@example.com")
        self.assertIn("second@example.com", str(self.record))
        self.assertNotIn("first@example.com", str(self.record))

    def test_add_invalid_email_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.record.add_email("not-an-email")
        self.assertIsNone(self.record.email)


class TestAddEmailCommand(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()
        self.john = Record("John")
        self.john.add_phone("1234567890")
        self.book.add_record(self.john)

    def test_adds_email_to_existing_contact(self):
        result = add_email(["John", "john@example.com"], self.book)
        self.assertEqual(result, "Email added for John.")
        self.assertEqual(self.john.email.value, "john@example.com")

    def test_case_insensitive_lookup_uses_stored_name(self):
        result = add_email(["john", "john@example.com"], self.book)
        self.assertEqual(result, "Email added for John.")
        self.assertEqual(self.john.email.value, "john@example.com")

    def test_contact_not_found(self):
        result = add_email(["Nobody", "nobody@example.com"], self.book)
        self.assertEqual(result, "Contact 'Nobody' not found.")

    def test_missing_arguments_shows_usage(self):
        result = add_email(["John"], self.book)
        self.assertIn("Usage: add-email <name> <email>", result)

    def test_empty_arguments_shows_usage(self):
        result = add_email([], self.book)
        self.assertIn("Usage: add-email <name> <email>", result)

    def test_invalid_email_returns_error_message(self):
        result = add_email(["John", "invalid-email"], self.book)
        self.assertIn("Invalid email format", result)
        self.assertIsNone(self.john.email)


class TestAddressBookAndCommandSearch(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()

        self.john = Record("John")
        self.john.add_phone("1234567890")
        self.john.add_email("john.doe@example.com")
        self.john.add_birthday("15.03.1990")

        self.jane = Record("Jane Smith")
        self.jane.add_phone("0987654321")
        self.jane.add_email("jane@work.org")

        self.book.add_record(self.john)
        self.book.add_record(self.jane)

    def test_search_by_name_case_insensitive(self):
        matches = self.book.search("john")
        self.assertEqual(matches, [self.john])

    def test_search_by_phone_partial(self):
        matches = self.book.search("7654")
        self.assertEqual(matches, [self.jane])

    def test_search_by_email_case_insensitive(self):
        matches = self.book.search("JOHN.DOE@EXAMPLE.COM")
        self.assertEqual(matches, [self.john])

    def test_search_by_birthday(self):
        matches = self.book.search("15.03.1990")
        self.assertEqual(matches, [self.john])

    def test_search_multiple_matches(self):
        matches = self.book.search("example.com")
        self.assertEqual(matches, [self.john])

        all_j = self.book.search("j")
        self.assertEqual(len(all_j), 2)

    def test_search_empty_or_non_string_query_returns_empty_list(self):
        self.assertEqual(self.book.search(""), [])
        self.assertEqual(self.book.search("   "), [])
        self.assertEqual(self.book.search(None), [])

    def test_search_command_returns_matching_records(self):
        output = search_contacts(["jane@work.org"], self.book)
        self.assertIn("Jane Smith", output)
        self.assertIn("jane@work.org", output)

    def test_search_command_joins_multi_word_query(self):
        output = search_contacts(["Jane", "Smith"], self.book)
        self.assertIn("Jane Smith", output)

    def test_search_command_no_matches(self):
        output = search_contacts(["unknown_xyz"], self.book)
        self.assertEqual(output, "No contacts found matching 'unknown_xyz'.")

    def test_search_command_empty_args_shows_usage(self):
        output = search_contacts([], self.book)
        self.assertIn("Usage: search <query>", output)


if __name__ == "__main__":
    unittest.main()