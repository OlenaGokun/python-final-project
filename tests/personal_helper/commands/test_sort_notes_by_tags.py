import unittest

from personal_helper.commands.sort_notes_by_tags import SortNotesByTagsCommand
from personal_helper.core import InvalidNoteError
from personal_helper.models.notes import Notebook


class TestSortNotesByTags(unittest.TestCase):
    def setUp(self) -> None:
        self.notebook = Notebook()
        self.command = SortNotesByTagsCommand()

    def test_empty_notebook_model_and_command(self) -> None:
        self.assertEqual(self.notebook.sort_by_tags({"work"}), ())
        result = self.command.run_with_notebook(
            ["--tags", "work"], self.notebook
        )
        self.assertEqual(result, "ℹ️  No notes found.")

    def test_sort_by_tags_requires_at_least_one_tag_in_model(self) -> None:
        self.notebook.add("Note 1", "text", {"work"})
        with self.assertRaises(InvalidNoteError):
            self.notebook.sort_by_tags(set())

    def test_single_tag_puts_matching_notes_first_and_preserves_order(
        self,
    ) -> None:
        self.notebook.add("First Match", "text", {"work", "later"})
        self.notebook.add("Other Tag", "text", {"home"})
        self.notebook.add("Untagged", "text", set())
        self.notebook.add("Second Match", "text", {"work"})

        sorted_notes = self.notebook.sort_by_tags({"work"})
        titles = [note.title.value for note in sorted_notes]
        self.assertEqual(
            titles,
            ["First Match", "Second Match", "Other Tag", "Untagged"],
        )

    def test_multiple_tags_puts_any_matching_note_first(self) -> None:
        self.notebook.add("Plain", "text", set())
        self.notebook.add("Urgent Note", "text", {"urgent"})
        self.notebook.add("Personal", "text", {"personal"})
        self.notebook.add("Work Note", "text", {"work"})

        sorted_notes = self.notebook.sort_by_tags({"work", "urgent"})
        titles = [note.title.value for note in sorted_notes]
        self.assertEqual(
            titles,
            ["Urgent Note", "Work Note", "Plain", "Personal"],
        )

    def test_tag_matching_is_case_insensitive(self) -> None:
        self.notebook.add("Other", "text", {"other"})
        self.notebook.add("Uppercase Tag", "text", {"Work"})

        sorted_notes = self.notebook.sort_by_tags({"work"})
        titles = [note.title.value for note in sorted_notes]
        self.assertEqual(titles, ["Uppercase Tag", "Other"])

    def test_command_outputs_matching_notes_first(self) -> None:
        self.notebook.add("Plain", "body", set())
        self.notebook.add("Urgent Task", "body", {"urgent"})
        self.notebook.add("Work Task", "body", {"work"})

        output = self.command.run_with_notebook(
            ["--tags", "work", "urgent"], self.notebook
        )
        lines = output.splitlines()
        self.assertEqual(len(lines), 3)
        self.assertIn("Urgent Task", lines[0])
        self.assertIn("Work Task", lines[1])
        self.assertIn("Plain", lines[2])

    def test_command_without_tags_returns_error_message(self) -> None:
        self.notebook.add("Note", "body", {"work"})
        output = self.command.run_with_notebook([], self.notebook)
        self.assertIn("Provide at least one tag", output)


if __name__ == "__main__":
    unittest.main()