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
        assert "search-contacts" in run("help", ["--command", "search-contacts"])
        assert "Unknown command" in run("help", ["--command", "missing"])
        assert run("show-all-contacts") == "ℹ️  No contacts found."
        assert run("show-birthdays") == "ℹ️  No upcoming birthdays in the next 7 days."

        assert run("add-contact", ["--name", "No Birthday"]) == "✅ Contact 'No Birthday' added."
        assert run("show-birthday", ["--name", "No Birthday"]) == (
            "ℹ️  No Birthday has no birthday set."
        )
        assert run(
            "add-contact",
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
            "add-address",
            ["--name", "Alex Rivera", "--address", "Privit", "st.", "5"],
        ) == "✅ Address added for Alex Rivera."
        assert run(
            "add-birthday",
            ["--name", "Alex Rivera", "--birthday", "03.01.2000"],
        ) == "✅ Birthday added for Alex Rivera."
        assert run("show-birthday", ["--name", "Alex Rivera"]) == (
            "🎂 Alex Rivera's birthday: 03.01.2000"
        )

        assert run(
            "change-phone",
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
        assert "Privit st. 5" in contacts

        class FixedDate(date):
            @classmethod
            def today(cls):
                return cls(2026, 1, 1)

        monkeypatch.setattr("personal_helper.models.book.date", FixedDate)
        assert run("show-birthdays") == "🎂 Alex Rivera: 05.01.2026"
        assert isinstance(run("exit"), ExitRequest)

    def test_contact_search_query_fields_and_validation(self, registry, data):
        run = lambda args: self.run(registry, data, "search-contacts", args)
        self.run(
            registry,
            data,
            "add-contact",
            [
                "--name",
                "Alice Smith",
                "--phone",
                "5012345671",
                "--email",
                "alice@north.example",
                "--birthday",
                "10.02.1990",
                "--address",
                "12",
                "North",
                "Street",
            ],
        )
        self.run(
            registry,
            data,
            "add-contact",
            [
                "--name",
                "Bob Smith",
                "--phone",
                "5098765432",
                "--email",
                "bob@south.example",
                "--birthday",
                "20.03.1985",
                "--address",
                "South",
                "Road",
            ],
        )

        assert "Alice Smith" in run(["--query", "alice"])
        assert "Alice Smith" in run(["--query", "north.example"])
        assert "Alice Smith" in run(["--query", "2345"])
        assert "Alice Smith" in run(["--query", "10.02.1990"])
        assert "Alice Smith" in run(["--name", "Alice"])
        assert "Alice Smith" in run(["--email", "NORTH"])
        assert "Alice Smith" in run(["--address", "north street"])
        assert "Bob Smith" in run(["--phone", "9876"])
        assert "Bob Smith" in run(["--birthday", "20.03"])
        assert run(["--name", "Smith", "--email", "north.example"]) == (
            "Alice Smith\n"
            "    phones:\n"
            "              5012345671\n"
            "    email:    alice@north.example\n"
            "    address:  12 North Street\n"
            "    birthday: 10.02.1990"
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

        assert run("search-notes", ["--query", "grocery"]) == (
            "Grocery list\n    text: Buy milk and bread\n    tags: food, home"
        )
        assert run("search-notes", ["--query", "food"]) == (
            "Grocery list\n    text: Buy milk and bread\n    tags: food, home"
        )
        assert run("search-notes", ["--query", "train"]) == (
            "Travel plans\n    text: Book train\n    tags: travel"
        )
        assert run("search-notes", ["--title", "grocery"]) == (
            "Grocery list\n    text: Buy milk and bread\n    tags: food, home"
        )
        assert run("search-notes", ["--text", "BREAD"]) == (
            "Grocery list\n    text: Buy milk and bread\n    tags: food, home"
        )
        assert run("search-notes", ["--tags", "HOME"]) == (
            "Grocery list\n    text: Buy milk and bread\n    tags: food, home"
        )
        assert run(
            "search-notes",
            ["--title", "grocery", "--text", "milk", "--tags", "home"],
        ) == "Grocery list\n    text: Buy milk and bread\n    tags: food, home"
        assert run(
            "search-notes",
            ["--title", "grocery", "--text", "milk", "--tags", "travel"],
        ) == "ℹ️  No notes found."
        assert run("search-notes", ["--query", "missing"]) == "ℹ️  No notes found."
        assert run("search-notes").startswith("❌ Invalid arguments. Provide --query")
        assert run(
            "search-notes", ["--query", "milk", "--title", "Grocery"]
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
        assert run("search-notes", ["--query", "coffee"]) == (
            "Grocery list\n    text: Buy coffee\n    tags: drinks, home"
        )
        assert run(
            "delete-note-tags",
            ["--title", "Grocery list", "--tags", "home"],
        ) == "✅ Tags removed from note 'Grocery list'."
        assert run("show-all-notes") == (
            "Grocery list: Buy coffee [tags: drinks]\n"
            "Travel plans: Book train [tags: travel]"
        )
        assert run("delete-note", ["--title", "Grocery list"]) == (
            "✅ Note 'Grocery list' deleted."
        )
        assert run("show-all-notes") == "Travel plans: Book train [tags: travel]"
