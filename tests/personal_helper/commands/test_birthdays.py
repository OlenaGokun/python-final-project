"""Unit tests for the birthdays command."""

from datetime import date

from personal_helper.models import AddressBook, PersonalHelper, Record


class TestShowBirthdaysCommand:
    """Tests for the birthdays command."""

    def test_show_birthdays_empty(self, registry, book):
        """Return the empty-state message when no birthdays are upcoming."""
        cmd = registry.get_command("show-birthdays")
        result = cmd.run([], PersonalHelper(book))

        assert "ℹ️" in result
        assert "No upcoming birthdays" in result

    def test_show_birthdays_with_contacts(self, registry, monkeypatch):
        """Format upcoming birthdays deterministically, including weekend shifts."""

        class FrozenDate(date):
            @classmethod
            def today(cls):
                return cls(2025, 1, 1)

        monkeypatch.setattr("personal_helper.models.book.date", FrozenDate)
        book = AddressBook()
        for name, birthday in (
            ("Friday", "03.01.1990"),
            ("Saturday", "04.01.1990"),
            ("Outside window", "09.01.1990"),
        ):
            record = Record(name)
            record.add_birthday(birthday)
            book.add_record(record)

        cmd = registry.get_command("show-birthdays")
        result = cmd.run([], PersonalHelper(book))

        assert result == "🎂 Friday: 03.01.2025\n🎂 Saturday: 06.01.2025"
