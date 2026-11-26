"""Unit tests for address book commands"""

import pytest
from personal_helper.models import PersonalHelper
from personal_helper.models.book import AddressBook
from personal_helper.models.record import Record
from personal_helper.command_registry import CommandRegistry
from personal_helper.core.exceptions import InvalidInputError, CommandError

# ============================================================================
# ADD COMMAND TESTS
# ============================================================================

class TestAddCommand:
    """Tests for add command"""

    def test_add_new_contact(self, registry, book):
        """Test adding a new contact"""
        cmd = registry.get_command("add-contact")
        result = cmd.run(["--name", "John", "--phone", "5012345671"], PersonalHelper(book))

        assert result == "✅ Contact 'John' added."
        assert "john" in book.data  # Keys are stored lowercase

    def test_add_contact_without_phone(self, registry, book):
        """Test adding contact without phone"""
        cmd = registry.get_command("add-contact")
        result = cmd.run(["--name", "Alice"], PersonalHelper(book))

        assert result == "✅ Contact 'Alice' added."
        assert "alice" in book.data  # Keys are stored lowercase

    def test_add_new_contact_with_email_and_birthday(self, registry, book):
        cmd = registry.get_command("add-contact")
        result = cmd.run(
            [
                "--name",
                "Alice",
                "--email",
                "alice@example.com",
                "--birthday",
                "25.12.1990",
            ],
            PersonalHelper(book),
        )

        record = book.find("Alice")
        assert result == "✅ Contact 'Alice' added."
        assert record.email.value == "alice@example.com"
        assert str(record.birthday) == "25.12.1990"

    def test_add_new_contact_with_address(self, registry, book):
        result = registry.get_command("add-contact").run(
            ["--name", "Alice", "--address", "Main", "st.", "5"],
            PersonalHelper(book),
        )

        assert result == "✅ Contact 'Alice' added."
        assert book["Alice"].address.value == "Main st. 5"

    def test_add_new_contact_with_multiple_phones(self, registry, book):
        cmd = registry.get_command("add-contact")
        result = cmd.run(
            [
                "--name",
                "Alice",
                "--phone",
                "5012345671",
                "5012345672",
                "--email",
                "alice@example.com",
            ],
            PersonalHelper(book),
        )

        record = book.find("Alice")
        assert result == "✅ Contact 'Alice' added."
        assert [phone.value for phone in record.phones] == [
            "5012345671",
            "5012345672",
        ]

    def test_add_phone_to_existing_contact(self, registry, book_with_contacts):
        """Test adding phone to existing contact"""
        cmd = registry.get_command("add-contact")
        result = cmd.run(["--name", "John", "--phone", "0559999999"], PersonalHelper(book_with_contacts))

        assert result == "✅ Contact 'John' updated."

    def test_add_multiple_phones_to_existing_contact(self, registry, book_with_contacts):
        cmd = registry.get_command("add-contact")
        result = cmd.run(
            [
                "--name",
                "John",
                "--phone",
                "0559999998",
                "0559999999",
            ],
            PersonalHelper(book_with_contacts),
        )

        record = book_with_contacts.find("John")
        assert result == "✅ Contact 'John' updated."
        assert [phone.value for phone in record.phones] == [
            "5012345671",
            "0559999998",
            "0559999999",
        ]

    def test_duplicate_phones_in_new_contact_are_rejected_without_creation(
        self, registry, book
    ):
        cmd = registry.get_command("add-contact")
        result = cmd.run(
            ["--name", "Alice", "--phone", "5012345671", "5012345671"],
            PersonalHelper(book),
        )

        assert "Phone 5012345671 already exists for Alice." in result
        assert book.find("Alice") is None

    def test_duplicate_phone_does_not_partially_update_contact(
        self, registry, book_with_contacts
    ):
        cmd = registry.get_command("add-contact")
        record = book_with_contacts.find("John")
        original_phones = record.phones

        result = cmd.run(
            [
                "--name",
                "John",
                "--phone",
                "0559999998",
                "5012345671",
            ],
            PersonalHelper(book_with_contacts),
        )

        assert "already exists" in result
        assert record.phones == original_phones

    def test_add_email_and_birthday_to_existing_contact(
        self, registry, book_with_contacts
    ):
        cmd = registry.get_command("add-contact")
        result = cmd.run(
            [
                "--name",
                "John",
                "--email",
                "john@example.com",
                "--birthday",
                "25.12.1990",
            ],
            PersonalHelper(book_with_contacts),
        )

        record = book_with_contacts.find("John")
        assert result == "✅ Contact 'John' updated."
        assert record.email.value == "john@example.com"
        assert str(record.birthday) == "25.12.1990"

    def test_add_contact_updates_existing_address(self, registry, book_with_contacts):
        command = registry.get_command("add-contact")
        result = command.run(
            ["--name", "John", "--address", "Main", "st.", "5"],
            PersonalHelper(book_with_contacts),
        )

        assert result == "✅ Contact 'John' updated."
        assert book_with_contacts["John"].address.value == "Main st. 5"

    @pytest.mark.parametrize(
        ("options", "error"),
        [
            (["--email", "invalid-email"], "Invalid email format"),
            (["--birthday", "31.02.1990"], "Invalid date format"),
        ],
    )
    def test_invalid_optional_field_does_not_create_contact(
        self, registry, book, options, error
    ):
        cmd = registry.get_command("add-contact")
        result = cmd.run(["--name", "Alice", *options], PersonalHelper(book))

        assert error in result
        assert book.find("Alice") is None

    def test_invalid_birthday_does_not_partially_update_existing_contact(
        self, registry, book_with_contacts
    ):
        cmd = registry.get_command("add-contact")
        record = book_with_contacts.find("John")

        result = cmd.run(
            [
                "--name",
                "John",
                "--email",
                "john@example.com",
                "--birthday",
                "31.02.1990",
            ],
            PersonalHelper(book_with_contacts),
        )

        assert "Invalid date format" in result
        assert record.email is None
        assert record.birthday is not None
        assert str(record.birthday) == "25.12.1990"

    def test_existing_contact_without_phone_is_unchanged(
        self, registry, book_with_contacts
    ):
        """Adding an existing name without a phone should not alter its phones."""
        cmd = registry.get_command("add-contact")
        record = book_with_contacts.find("John")
        original_phones = record.phones

        result = cmd.run(["--name", "John"], PersonalHelper(book_with_contacts))

        assert result == "✅ Contact 'John' updated."
        assert record.phones == original_phones

    def test_add_with_no_arguments(self, registry, book):
        """Test add command with no arguments"""
        cmd = registry.get_command("add-contact")
        result = cmd.run([], PersonalHelper(book))

        assert "❌" in result
        assert "Invalid arguments" in result
        assert "Usage:" in result

    def test_add_with_invalid_phone(self, registry, book):
        """Invalid phone values are rejected."""
        cmd = registry.get_command("add-contact")
        result = cmd.run(["--name", "John", "--phone", "phone1", "phone2"], PersonalHelper(book))

        assert "❌" in result
        assert "Phone must be a valid phone number" in result

# ============================================================================
# ADD BIRTHDAY COMMAND TESTS
# ============================================================================
