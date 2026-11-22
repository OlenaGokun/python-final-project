"""Tests for independent note commands."""

import pytest
from personal_helper.models.fields import Tag


@pytest.mark.parametrize(
    ("command_name", "usage"),
    [
        ("add-note", "add-note --title <title> --text <text> [--tags <tag> ...]"),
        ("update-note", "update-note --title <title> [--text <text>] [--tags <tag> ...]"),
        ("delete-note", "delete-note --title <title>"),
        ("add-note-tags", "add-note-tags --title <title> --tags <tag> [tag ...]"),
        ("delete-note-tags", "delete-note-tags --title <title> --tags <tag> [tag ...]"),
    ],
)
def test_note_command_usage_uses_title(registry, command_name, usage):
    assert registry.get_command(command_name).get_usage() == usage


def test_note_workflow_without_contacts(registry, data):
    assert registry.get_command("add-note").run(
        ["--title", "Shopping", "--text", "Buy", "milk", "and", "bread"], data
    ) == "✅ Note 'Shopping' added."
    assert registry.get_command("find-notes").run(
        ["--text", "MILK", "AND"], data
    ) == "Shopping: Buy milk and bread"
    assert registry.get_command("update-note").run(
        ["--title", "shopping", "--text", "Buy", "coffee"], data
    ) == "✅ Note 'shopping' updated."
    assert registry.get_command("find-notes").run(
        ["--text", "coffee"], data
    ) == "Shopping: Buy coffee"
    assert registry.get_command("delete-note").run(
        ["--title", "SHOPPING"], data
    ) == "✅ Note 'SHOPPING' deleted."
    assert registry.get_command("find-notes").run(["--text", "coffee"], data) == "ℹ️  No notes found."
    assert len(data.address_book) == 0


def test_add_note_with_tags(registry, data):
    result = registry.get_command("add-note").run(
        ["--title", "Shopping", "--text", "Buy", "milk", "--tags", "FOOD", "home", "food"], data
    )

    assert result == "✅ Note 'Shopping' added."
    assert data.notebook["shopping"].text.value == "Buy milk"
    assert data.notebook["shopping"].tags == {Tag("food"), Tag("home")}


@pytest.mark.parametrize("args", [
    ["--title", "shopping", "--tags", "food"],
    ["--title", "shopping", "--text", "text", "--tags", ""],
])
def test_add_note_with_invalid_text_or_tag_does_not_create_note(registry, data, args):
    result = registry.get_command("add-note").run(args, data)

    assert result.startswith("❌")
    assert "shopping" not in data.notebook


@pytest.mark.parametrize(
    ("command_name", "args"),
    [
        ("add-note", ["--title", "shopping"]),
        ("update-note", ["--title", "shopping"]),
        ("delete-note", []),
        ("delete-note", ["shopping", "extra"]),
    ],
)
def test_note_commands_validate_arguments(registry, data, command_name, args):
    result = registry.get_command(command_name).run(args, data)
    assert result.startswith("❌ Invalid arguments.")


@pytest.mark.parametrize(
    ("name", "args"),
    [
        ("add-note", ["--title", "List", "--text", "Buy", "--unknown", "value"]),
        ("add-note", ["--title", "List", "--text", "Buy", "--title", "Other"]),
        ("update-note", ["--title", "List", "--text"]),
        ("delete-note", ["List"]),
        ("add-note-tags", ["--title", "List", "--tags"]),
        ("delete-note-tags", ["--tags", "food"]),
    ],
)
def test_note_commands_reject_bad_options_without_mutation(registry, data, name, args):
    data.notebook.add("List", "Original", {"food"})
    assert registry.get_command(name).run(args, data).startswith("❌ Invalid arguments.")
    assert data.notebook["list"].text.value == "Original"
    assert data.notebook["list"].tags == {Tag("food")}


def test_add_note_rejects_duplicate_title(registry, data):
    command = registry.get_command("add-note")
    command.run(["--title", "Shopping", "--text", "First", "note"], data)

    result = command.run(["--title", "shopping", "--text", "Second", "note"], data)

    assert result.startswith("❌")
    assert "already exists" in result
    assert data.notebook["shopping"].text.value == "First note"


@pytest.mark.parametrize(
    ("command_name", "args"),
    [("update-note", ["--title", "missing", "--text", "new", "text"]), ("delete-note", ["--title", "missing"])],
)
def test_update_and_delete_require_existing_note(registry, data, command_name, args):
    result = registry.get_command(command_name).run(args, data)
    assert result.startswith("❌")
    assert "not found" in result


def test_update_note_replaces_tags_and_optionally_updates_text(registry, data):
    data.notebook.add("Grocery List", "Buy milk", {"old", "home"})
    command = registry.get_command("update-note")
    assert command.run(["--tags", "FOOD", "food", "--title", "grocery", "list"], data) == "✅ Note 'grocery list' updated."
    assert data.notebook["GROCERY LIST"].text.value == "Buy milk"
    assert data.notebook["GROCERY LIST"].tags == {Tag("food")}
    assert command.run(
        ["--title", "Grocery", "List", "--text", "Buy", "bread", "--tags", "home"], data
    ) == "✅ Note 'Grocery List' updated."
    assert data.notebook["grocery list"].text.value == "Buy bread"
    assert data.notebook["grocery list"].tags == {Tag("home")}
    assert command.run(["--title", "Grocery", "List", "--text", "Tea"], data) == "✅ Note 'Grocery List' updated."
    assert data.notebook["grocery list"].tags == {Tag("home")}


def test_update_note_invalid_tag_does_not_change_text(registry, data):
    data.notebook.add("List", "Original", {"old"})
    result = registry.get_command("update-note").run(
        ["--title", "List", "--text", "Changed", "--tags", "good", "bad tag"], data
    )
    assert result.startswith("❌")
    assert data.notebook["list"].text.value == "Original"
    assert data.notebook["list"].tags == {Tag("old")}


def test_search_returns_all_matching_text(registry, data):
    data.notebook.add("shopping", "Buy milk")
    data.notebook.add("recipe", "Add milk and honey")
    data.notebook.add("other", "Buy bread")

    result = registry.get_command("find-notes").run(["--text", "MILK"], data)

    assert result == "shopping: Buy milk\nrecipe: Add milk and honey"


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (
            [],
            "❌ Invalid arguments. Provide --query or at least one field.\n"
            "Usage: find-notes (--query <query> | [--title <title>] "
            "[--text <text>] [--tags <tag> ...])",
        ),
        (["--title", "shop"], "Shopping: Buy milk and bread\nShopTrip: Buy milk"),
        (["--text", "MILK", "AND"], "Shopping: Buy milk and bread\nRecipe: Buy milk and bread"),
        (["--tags", "HOME", "travel"], "Shopping: Buy milk and bread\nShopTrip: Buy milk"),
        (["--title", "shop", "--text", "milk", "and"], "Shopping: Buy milk and bread"),
        (["--tags", "food", "--title", "shop"], "Shopping: Buy milk and bread"),
        (["--text", "milk", "and", "--tags", "home"], "Shopping: Buy milk and bread"),
        (["--text", "milk", "--tags", "missing", "food", "--title", "shopping"], "Shopping: Buy milk and bread"),
        (["--title", "shoptrip", "--tags", "food"], "ℹ️  No notes found."),
    ],
)
def test_find_notes_optional_filters(registry, data, args, expected):
    data.notebook.add("Shopping", "Buy milk and bread", {"food", "home"})
    data.notebook.add("ShopTrip", "Buy milk", {"travel"})
    data.notebook.add("Recipe", "Buy milk and bread", {"food"})
    data.notebook.add("Plain", "Other")

    assert registry.get_command("find-notes").run(args, data) == expected


@pytest.mark.parametrize(
    "args",
    [
        ["--title"], ["--text", "--tags", "food"], ["--tags"],
        ["--unknown", "value"], ["--title", "shop", "--title", "other"],
        ["milk", "--tags", "food"], ["milk"], ["--tags", ""], ["--text", " "],
    ],
)
def test_find_notes_rejects_malformed_filters(registry, data, args):
    assert registry.get_command("find-notes").run(args, data).startswith("❌")


def test_find_notes_without_filters_on_empty_notebook(registry, data):
    result = registry.get_command("find-notes").run([], data)
    assert result.startswith("❌ Invalid arguments.")


def test_find_notes_by_query(registry, data):
    data.notebook.add("Shopping", "Buy milk", {"groceries"})
    data.notebook.add("Plans", "Call the grocery store", {"personal"})

    result = registry.get_command("find-notes").run(
        ["--query", "GROCER"], data
    )

    assert result == "Shopping: Buy milk\nPlans: Call the grocery store"


def test_find_notes_query_matches_title_text_or_tags(registry, data):
    data.notebook.add("Shopping", "Buy milk", {"groceries"})
    data.notebook.add("Plans", "Call the store", {"grocery"})

    result = registry.get_command("find-notes").run(
        ["--query", "GROCER"], data
    )

    assert result == "Shopping: Buy milk\nPlans: Call the store"


def test_find_notes_requires_query_or_filters(registry, data):
    assert registry.get_command("find-notes").run([], data).startswith(
        "❌ Invalid arguments."
    )
    assert registry.get_command("find-notes").run(
        ["--query", "milk", "--title", "Shopping"], data
    ).startswith("❌ Invalid arguments.")


def test_find_notes_field_filters_use_and_semantics(registry, data):
    data.notebook.add("Shopping list", "Buy milk", {"home"})
    data.notebook.add("Shopping ideas", "Buy bread", {"home"})
    data.notebook.add("Work", "Buy milk", {"work"})

    result = registry.get_command("find-notes").run(
        ["--title", "shopping", "--text", "milk", "--tags", "home"], data
    )

    assert result == "Shopping list: Buy milk"


def test_find_notes_combines_fields_with_and(registry, data):
    data.notebook.add("Shopping list", "Buy milk", {"home"})
    data.notebook.add("Shopping ideas", "Buy bread", {"home"})
    data.notebook.add("Work", "Buy milk", {"work"})

    result = registry.get_command("find-notes").run(
        ["--title", "shopping", "--text", "milk", "--tags", "home"], data
    )

    assert result == "Shopping list: Buy milk"


def test_tag_commands(registry, data):
    data.notebook.add("shopping", "Buy milk")
    data.notebook.add("holiday", "Pack bags")
    data.notebook.add("untagged", "Other")
    assert registry.get_command("add-note-tags").run(
        ["--title", "shopping", "--tags", "food", "personal"], data
    ) == "✅ Tags added to note 'shopping'."
    assert registry.get_command("add-note-tags").run(
        ["--title", "holiday", "--tags", "travel", "personal"], data
    ) == "✅ Tags added to note 'holiday'."
    assert registry.get_command("find-notes").run(
        ["--tags", "FOOD", "travel"], data
    ) == (
        "shopping: Buy milk\n"
        "holiday: Pack bags"
    )
    assert registry.get_command("delete-note-tags").run(
        ["--title", "shopping", "--tags", "food"], data
    ) == "✅ Tags removed from note 'shopping'."
    assert registry.get_command("find-notes").run(["--tags", "food"], data) == "ℹ️  No notes found."
    assert registry.get_command("find-notes").run(["--title", "HOLI"], data) == "holiday: Pack bags"


@pytest.mark.parametrize(
    ("name", "args"),
    [("add-note-tags", ["--title", "shopping"]), ("delete-note-tags", ["--title", "shopping"])],
)
def test_tag_commands_validate_arguments(registry, data, name, args):
    assert registry.get_command(name).run(args, data).startswith("❌ Invalid arguments.")
