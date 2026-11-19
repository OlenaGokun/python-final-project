"""Integration tests with multiple commands working together"""

import pytest
from address_book.models.book import AddressBook
from address_book.models.record import Record
from address_book.command_registry import CommandRegistry

class TestIntegration:
    """Integration tests with multiple commands"""

    def test_add_then_show_contact(self, registry, book):
        """Test adding contact and showing it"""
        # Add contact
        add_cmd = registry.get_command("add")
        add_cmd.run(["TestUser", "1234567890"], book)  # 10 digits

        # Show phone
        phone_cmd = registry.get_command("phone")
        result = phone_cmd.run(["TestUser"], book)

        assert "1234567890" in result

    def test_add_birthday_then_show(self, registry, book):
        """Test adding and showing birthday"""
        # Add contact
        add_cmd = registry.get_command("add")
        add_cmd.run(["TestUser"], book)

        # Add birthday
        bday_cmd = registry.get_command("add-birthday")
        bday_cmd.run(["TestUser", "01.01.2000"], book)

        # Show birthday
        show_cmd = registry.get_command("show-birthday")
        result = show_cmd.run(["TestUser"], book)

        assert "01.01.2000" in result

    def test_complete_workflow(self, registry, book):
        """Test complete user workflow"""
        # Add contact
        add_cmd = registry.get_command("add")
        add_cmd.run(["John", "5012345671"], book)  # 10 digits

        # Show phone
        phone_cmd = registry.get_command("phone")
        phone_result = phone_cmd.run(["John"], book)
        assert "5012345671" in phone_result

        # Add birthday
        bday_cmd = registry.get_command("add-birthday")
        bday_cmd.run(["John", "25.12.1990"], book)

        # Show birthday
        show_cmd = registry.get_command("show-birthday")
        bday_result = show_cmd.run(["John"], book)
        assert "25.12.1990" in bday_result

        # Change phone
        change_cmd = registry.get_command("change")
        change_cmd.run(["John", "5012345671", "5099999999"], book)

        # Verify change
        phone_result = phone_cmd.run(["John"], book)
        assert "5099999999" in phone_result
