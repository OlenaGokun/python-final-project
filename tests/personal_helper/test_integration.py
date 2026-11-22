"""Integration tests for complete command workflows."""

from datetime import date

from personal_helper.commands.base_command import ExitRequest


class TestIntegration:
    """Exercise commands together through the registry and shared app data."""

    @staticmethod
    def run(registry, data, command_name, args=()):
        command = registry.get_command(command_name)
        assert command is not None, f"Command {command_name!r} was not registered."
        return command.run(list(args), data)

    def test_contact_command_workflow(self, registry, data, monkeypatch):
        run = lambda command, args=(): self.run(registry, data, command, args)

        assert run("hello") == "How can I help you?"
        assert "Available Commands" in run("help")
        assert "search" in run("help", ["--command", "search"])
        assert "Unknown command" in run("help", ["--command", "missing"])
        assert run("show-all-contacts") == "ℹ️  No contacts found."
        assert run("birthdays") == "ℹ️  No upcoming birthdays in the next 7 days."

        assert run("add", ["--name", "No Birthday"]) == "✅ Contact 'No Birthday' added."
        assert run("show-birthday", ["--name", "No Birthday"]) == (
            "ℹ️  No Birthday has no birthday set."
        )
        assert run(
            "add",
            [
                "--name",
                "Alex Rivera",
                "--phone",
                "5012345671",
                "5012345672",
                "--email",
                "old@example.com",
                "--birthday",
                "03.01.2000",
            ],
        ) == "✅ Contact 'Alex Rivera' added."
        assert run(
            "add-email",
            ["--name", "Alex Rivera", "--email", "alex@example.com"],
        ) == "✅ Email added for Alex Rivera."
        assert run(
            "add-birthday",
            ["--name", "Alex Rivera", "--birthday", "03.01.2000"],
        ) == "✅ Birthday added for Alex Rivera."
        assert run("show-birthday", ["--name", "Alex Rivera"]) == (
            "🎂 Alex Rivera's birthday: 03.01.2000"
        )

        assert run(
            "change",
            [
                "--name",
                "Alex Rivera",
                "--old-phone",
                "5012345671",
                "--new-phone",
                "5099999999",
            ],
        ) == "✅ Contact 'Alex Rivera' updated."
        phones = run("phone", ["--name", "Alex Rivera"])
        assert phones == "5099999999; 5012345672"
        contacts = run("show-all-contacts")
        assert "Alex Rivera" in contacts
        assert "No Birthday" in contacts
        assert "alex@example.com" in contacts

        class FixedDate(date):
            @classmethod
            def today(cls):
                return cls(2026, 1, 1)

        monkeypatch.setattr("personal_helper.models.book.date", FixedDate)
        assert run("birthdays") == "🎂 Alex Rivera: 05.01.2026"
        assert isinstance(run("exit"), ExitRequest)

    def test_contact_search_query_fields_and_validation(self, registry, data):
        run = lambda args: self.run(registry, data, "search", args)
        self.run(
            registry,
            data,
            "add",
            [
                "--name",
                "Alice Smith",
                "--phone",
                "5012345671",
                "--email",
                "alice@north.example",
                "--birthday",
                "10.02.1990",
            ],
        )
        self.run(
            registry,
            data,
            "add",
            [
                "--name",
                "Bob Smith",
                "--phone",
                "5098765432",
                "--email",
                "bob@south.example",
                "--birthday",
                "20.03.1985",
            ],
        )

        assert "Alice Smith" in run(["--query", "alice"])
        assert "Alice Smith" in run(["--query", "north.example"])
        assert "Alice Smith" in run(["--query", "2345"])
        assert "Alice Smith" in run(["--query", "10.02.1990"])
        assert "Alice Smith" in run(["--name", "Alice"])
        assert "Alice Smith" in run(["--email", "NORTH"])
        assert "Bob Smith" in run(["--phone", "9876"])
        assert "Bob Smith" in run(["--birthday", "20.03"])
        assert run(["--name", "Smith", "--email", "north.example"]) == (
            "Contact name: Alice Smith, phones: 5012345671, "
            "email: alice@north.example, birthday: 10.02.1990"
        )
        assert run(["--name", "Alice", "--email", "south.example"]) == (
            "ℹ️  No contacts found."
        )
        assert run(["--query", "not-present"]) == "ℹ️  No contacts found."
        assert run([]).startswith("❌ Invalid arguments. Provide --query")
        assert run(["--query", "Alice", "--name", "Alice"]).startswith(
            "❌ Invalid arguments. --query cannot be combined"
        )

    def test_note_command_workflow_search_and_validation(self, registry, data):
        run = lambda command, args=(): self.run(registry, data, command, args)

        assert run("show-all-notes") == "ℹ️  No notes found."
        assert run(
            "add-note",
            [
                "--title",
                "Grocery list",
                "--text",
                "Buy",
                "milk",
                "and",
                "bread",
                "--tags",
                "food",
                "home",
            ],
        ) == "✅ Note 'Grocery list' added."
        assert run(
            "add-note",
            [
                "--title",
                "Travel plans",
                "--text",
                "Book train",
                "--tags",
                "travel",
            ],
        ) == "✅ Note 'Travel plans' added."

        assert run("find-notes", ["--query", "grocery"]) == (
            "Grocery list: Buy milk and bread"
        )
        assert run("find-notes", ["--query", "food"]) == (
            "Grocery list: Buy milk and bread"
        )
        assert run("find-notes", ["--query", "train"]) == "Travel plans: Book train"
        assert run("find-notes", ["--title", "grocery"]) == (
            "Grocery list: Buy milk and bread"
        )
        assert run("find-notes", ["--text", "BREAD"]) == (
            "Grocery list: Buy milk and bread"
        )
        assert run("find-notes", ["--tags", "HOME"]) == (
            "Grocery list: Buy milk and bread"
        )
        assert run(
            "find-notes",
            ["--title", "grocery", "--text", "milk", "--tags", "home"],
        ) == "Grocery list: Buy milk and bread"
        assert run(
            "find-notes",
            ["--title", "grocery", "--text", "milk", "--tags", "travel"],
        ) == "ℹ️  No notes found."
        assert run("find-notes", ["--query", "missing"]) == "ℹ️  No notes found."
        assert run("find-notes").startswith("❌ Invalid arguments. Provide --query")
        assert run(
            "find-notes", ["--query", "milk", "--title", "Grocery"]
        ).startswith("❌ Invalid arguments. --query cannot be combined")

        assert run(
            "add-note-tags",
            ["--title", "Grocery list", "--tags", "shopping"],
        ) == "✅ Tags added to note 'Grocery list'."
        assert run(
            "update-note",
            [
                "--title",
                "Grocery list",
                "--text",
                "Buy",
                "coffee",
                "--tags",
                "home",
                "drinks",
            ],
        ) == "✅ Note 'Grocery list' updated."
        assert run("find-notes", ["--query", "coffee"]) == (
            "Grocery list: Buy coffee"
        )
        assert run(
            "delete-note-tags",
            ["--title", "Grocery list", "--tags", "home"],
        ) == "✅ Tags removed from note 'Grocery list'."
        assert run("show-all-notes") == (
            "Grocery list: Buy coffee\nTravel plans: Book train"
        )
        assert run("delete-note", ["--title", "Grocery list"]) == (
            "✅ Note 'Grocery list' deleted."
        )
        assert run("show-all-notes") == "Travel plans: Book train"
