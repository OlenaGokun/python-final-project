import pytest
from collections import UserDict

from personal_helper.core import InvalidNoteError, NoteAlreadyExistsError, NoteNotFoundError
from personal_helper.models.fields import Tag, Text, Title
from personal_helper.models.note import Note
from personal_helper.models.notes import Notebook


def test_note_string_representations_include_sorted_tags():
    note = Note("Shopping", "Buy milk", {"Home", "FOOD"})
    assert str(note) == "Note title: Shopping, text: Buy milk, tags: food, home"
    assert repr(note) == "Note('Shopping', 'Buy milk', tags={'food', 'home'})"
    assert str(Note("Plain", "Text")) == "Note title: Plain, text: Text, tags: "
    assert repr(Note("Plain", "Text")) == "Note('Plain', 'Text', tags=set())"


def test_notebook_string_representations():
    notebook = Notebook()
    assert str(notebook) == "Notebook is empty."
    assert repr(notebook) == "Notebook({})"

    notebook.add("Shopping", "Buy milk", {"food"})
    notebook.add("Plain", "Text")
    assert str(notebook) == (
        "Note title: Shopping, text: Buy milk, tags: food\n"
        "Note title: Plain, text: Text, tags: "
    )
    assert repr(notebook) == (
        "Notebook({'shopping': Note('Shopping', 'Buy milk', tags={'food'}), "
        "'plain': Note('Plain', 'Text', tags=set())})"
    )


def test_notebook_mapping_is_case_insensitive():
    notebook = Notebook()
    note = Note("Straße", "First")
    notebook["STRASSE"] = note
    assert isinstance(notebook, UserDict)
    assert len(notebook) == 1
    assert notebook["strasse"] is note
    assert notebook.get("STRASSE") is note
    assert "Straße" in notebook
    assert list(notebook) == ["strasse"]
    assert notebook.get("missing") is None
    del notebook["STRASSE"]
    assert "straße" not in notebook
    with pytest.raises(KeyError):
        _ = notebook["missing"]


def test_notebook_mapping_rejects_mismatched_title_or_value():
    notebook = Notebook()
    with pytest.raises(InvalidNoteError):
        notebook["other"] = Note("shopping", "text")
    with pytest.raises(TypeError):
        notebook["shopping"] = "not a note"
    assert not notebook


def test_notebook_retains_standard_mapping_update():
    notebook = Notebook({"Shopping": Note("shopping", "text")})
    notebook.update({"TRIP": Note("Trip", "Pack")})
    assert notebook["shopping"].text.value == "text"
    assert notebook["trip"].title.value == "Trip"


@pytest.mark.parametrize("title", ["", " ", None])
def test_invalid_titles_are_rejected(title):
    with pytest.raises(InvalidNoteError, match="Note title"):
        Notebook().add(title, "text")


@pytest.mark.parametrize("text", ["", "  ", None])
def test_invalid_text_is_rejected(text):
    notes = Notebook()
    with pytest.raises(InvalidNoteError):
        notes.add("name", text)


def test_casefolded_titles_are_unique():
    notes = Notebook()
    notes.add("Straße", "First")
    with pytest.raises(NoteAlreadyExistsError):
        notes.add("STRASSE", "Second")
    assert notes["strasse"].text.value == "First"


def test_multiword_titles_are_trimmed_and_case_insensitive():
    notes = Notebook()
    notes.add("  Grocery List  ", "Buy milk")
    assert notes["grocery list"].title.value == "Grocery List"
    with pytest.raises(NoteAlreadyExistsError):
        notes.add("GROCERY LIST", "Other")
    notes.update_note(" Grocery List ", "Buy bread")
    assert notes["GROCERY LIST"].text.value == "Buy bread"
    notes.delete("grocery list")
    assert len(notes) == 0

def test_title_is_immutable_and_lookup_uses_normalized_key():
    notes = Notebook()
    notes.add("Straße", "First", {"personal"})
    note = notes["strasse"]
    with pytest.raises(AttributeError):
        note.title = "Different"
    with pytest.raises(AttributeError):
        note.title.value = "Different"
    notes.update_note("STRASSE", "Updated")
    assert notes["strasse"].text.value == "Updated"
    notes.delete("strasse")
    assert "strasse" not in notes


def test_add_with_optional_tags_normalizes_and_deduplicates():
    notes = Notebook()
    notes.add("shopping", "Buy milk", {"FOOD", "Home", "food"})
    assert notes["shopping"].tags == {Tag("food"), Tag("home")}


def test_note_tags_are_read_only_and_independent():
    first = Note("first", "text")
    second = Note("second", "text")
    assert isinstance(first.title, Title)
    assert isinstance(first.text, Text)
    with pytest.raises(AttributeError):
        first.tags.add(Tag("tag"))
    first.add_tags({"tag"})
    assert first.tags == {Tag("tag")}
    assert second.tags == frozenset()


@pytest.mark.parametrize("tags", [None, set()])
def test_note_can_be_created_without_tags(tags):
    note = Note("shopping", "Buy milk", tags)
    assert note.tags == frozenset()


def test_note_initial_tags_are_validated_and_deduplicated():
    note = Note("shopping", "Buy milk", {"FOOD", "food", "home"})
    assert note.tags == {Tag("food"), Tag("home")}
    with pytest.raises(InvalidNoteError):
        Note("shopping", "Buy milk", {"food", "bad tag"})


def test_add_with_invalid_tag_does_not_create_note():
    notes = Notebook()
    with pytest.raises(InvalidNoteError):
        notes.add("shopping", "Buy milk", {"food", "bad tag"})
    assert "shopping" not in notes


def test_update_validates_before_replacing():
    notes = Notebook()
    notes.add("name", "Original")
    with pytest.raises(InvalidNoteError):
        notes.update_note("name", "  ")
    assert notes["name"].text.value == "Original"


def test_update_note_replaces_tags_or_text_and_can_clear_tags():
    notes = Notebook()
    notes.add("Grocery List", "Original", {"old", "home"})
    notes.update_note("grocery list", tags={"FOOD", "food", "new"})
    assert notes["grocery list"].text.value == "Original"
    assert notes["grocery list"].tags == {Tag("food"), Tag("new")}
    notes.update_note("grocery list", text="Changed")
    assert notes["grocery list"].tags == {Tag("food"), Tag("new")}
    notes.update_note("grocery list", text="Both", tags=set())
    assert notes["grocery list"].text.value == "Both"
    assert notes["grocery list"].tags == frozenset()


def test_update_note_is_atomic_for_invalid_text_or_tags():
    notes = Notebook()
    notes.add("name", "Original", {"old"})
    with pytest.raises(InvalidNoteError):
        notes.update_note("name", text="New", tags={"valid", "bad tag"})
    with pytest.raises(InvalidNoteError):
        notes.update_note("name", text=" ", tags={"new"})
    with pytest.raises(InvalidNoteError):
        notes.update_note("name")
    assert notes["name"].text.value == "Original"
    assert notes["name"].tags == {Tag("old")}


@pytest.mark.parametrize("method", ["update", "delete"])
def test_missing_note_raises(method):
    notes = Notebook()
    with pytest.raises(NoteNotFoundError):
        if method == "update":
            notes.update_note("missing", "text")
        else:
            notes.delete("missing")


def test_search_notes_combines_fields_and_matches_any_tag():
    notes = Notebook()
    notes.add("Straße", "Buy MILK and bread", {"food", "home"})
    notes.add("street", "Buy milk", {"travel"})
    notes.add("recipe", "Buy milk and bread", {"food"})
    notes.add("plain", "Other")

    assert notes.search() == ()
    assert [n.title.value for n in notes.search(title="STRASSE")] == ["Straße"]
    assert [n.title.value for n in notes.search(text="MILK AND")] == ["Straße", "recipe"]
    assert [n.title.value for n in notes.search(tags={"TRAVEL", "home"})] == ["Straße", "street"]
    assert [n.title.value for n in notes.search(
        title="STRASSE", text="milk", tags={"missing", "FOOD"}
    )] == ["Straße"]
    assert notes.search(title="street", text="milk", tags={"food"}) == ()


def test_search_query_matches_any_field_and_takes_precedence():
    notes = Notebook()
    notes.add("Shopping", "Buy milk", {"groceries"})
    notes.add("Plans", "Call grocery store", {"personal"})

    assert [note.title.value for note in notes.search("grocer")] == [
        "Shopping",
        "Plans",
    ]
    assert [note.title.value for note in notes.search(
        "grocer", title="missing"
    )] == ["Shopping", "Plans"]


@pytest.mark.parametrize(
    "filters",
    [{"title": ""}, {"text": "  "}, {"tags": set()}, {"tags": {"bad tag"}}],
)
def test_search_rejects_invalid_filters(filters):
    with pytest.raises(InvalidNoteError):
        Notebook().search(**filters)


def test_tags_match_any():
    notes = Notebook()
    notes.add("shopping", "Buy milk")
    notes.add("trip", "Pack bags")
    notes.add("plain", "No tags")
    notes.add_tags("Shopping", {"Personal", "GROCERIES", "personal"})
    notes.add_tags("trip", {"travel", "personal"})

    assert [note.title.value for note in notes.search(tags={"groceries", "TRAVEL"})] == [
        "shopping", "trip"
    ]
    assert [note.title.value for note in notes.search(tags={"personal", "travel"})] == [
        "shopping", "trip"
    ]
    assert notes.search(tags={"unknown"}) == ()


def test_tag_removal_is_atomic_and_text_update_keeps_tags():
    notes = Notebook()
    notes.add("shopping", "Buy milk")
    notes.add_tags("shopping", {"food", "home"})
    with pytest.raises(InvalidNoteError):
        notes.remove_tags("shopping", {"food", "missing"})
    assert notes["shopping"].tags == {Tag("food"), Tag("home")}
    notes.update_note("SHOPPING", "Buy bread")
    notes.remove_tags("shopping", {"FOOD"})
    assert notes.search(tags={"food"}) == ()
    assert notes.search(tags={"home"})[0].text.value == "Buy bread"


def test_note_text_is_validated_on_update():
    note = Note("shopping", "  Buy milk  ")
    assert note.text.value == "Buy milk"
    with pytest.raises(AttributeError):
        note.text = Text("Changed")
    with pytest.raises(InvalidNoteError):
        note.update_text("  ")
    assert note.text.value == "Buy milk"
    note.update_text("Buy bread")
    assert note.text.value == "Buy bread"


@pytest.mark.parametrize("tags", [set(), {""}, {"two words"}, {"good", "bad tag"}])
def test_invalid_tags_are_rejected_without_partial_mutation(tags):
    notes = Notebook()
    notes.add("shopping", "Buy milk")
    with pytest.raises(InvalidNoteError):
        notes.add_tags("shopping", tags)
    assert notes["shopping"].tags == frozenset()
