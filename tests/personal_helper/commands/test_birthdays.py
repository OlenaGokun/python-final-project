"""Unit tests for the birthdays command."""

from datetime import date

import pytest

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

    @pytest.mark.parametrize(
        ("days", "expected"),
        [
            ("1", "🎂 Tomorrow: 30.12.2027"),
            ("10", "🎂 Tomorrow: 30.12.2027\n🎂 January: 06.01.2028"),
            ("365", "🎂 Tomorrow: 30.12.2027\n🎂 January: 06.01.2028\n🎂 Cutoff: 28.12.2028"),
        ],
    )
    def test_show_birthdays_with_custom_days(self, registry, monkeypatch, days, expected):
        class FrozenDate(date):
            @classmethod
            def today(cls):
                return cls(2027, 12, 29)

        monkeypatch.setattr("personal_helper.models.book.date", FrozenDate)
        book = AddressBook()
        for name, birthday in (
            ("Tomorrow", "30.12.1990"),
            ("January", "06.01.1990"),
            ("Cutoff", "28.12.1990"),
        ):
            record = Record(name)
            record.add_birthday(birthday)
            book.add_record(record)

        cmd = registry.get_command("show-birthdays")
        assert cmd.run(["--days", days], PersonalHelper(book)) == expected

    @pytest.mark.parametrize("days", ["-1", "0", "366", "1.5", "many"])
    def test_show_birthdays_rejects_invalid_days(self, registry, book, days):
        cmd = registry.get_command("show-birthdays")
        result = cmd.run(["--days", days], PersonalHelper(book))

        assert result.startswith("❌")
        assert "1 to 365" in result

    def test_show_birthdays_reports_custom_empty_window(self, registry, book):
        cmd = registry.get_command("show-birthdays")

        assert cmd.run(["--days", "30"], PersonalHelper(book)) == (
            "ℹ️  No upcoming birthdays in the next 30 days."
        )
