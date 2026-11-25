import unittest

from personal_helper.commands.sort_notes_by_tags import SortNotesByTagsCommand
from personal_helper.models.notes import Notebook


class TestSortNotesByTags(unittest.TestCase):
    def setUp(self) -> None:
        self.notebook = Notebook()
        self.command = SortNotesByTagsCommand()

    def test_empty_notebook_model_and_command(self) -> None:
        self.assertEqual(self.notebook.sort_by_tags(), ())
        result = self.command.run_with_notebook([], self.notebook)
        self.assertEqual(result, "ℹ️  No notes found.")

    def test_sorts_by_smallest_tag_and_puts_untagged_last(self) -> None:
        self.notebook.add("Note Z", "text", {"z-tag", "a-tag"})
        self.notebook.add("Note M", "text", {"m-tag"})
        self.notebook.add("Untagged D", "text", set())
        self.notebook.add("Untagged C", "text", set())

        sorted_notes = self.notebook.sort_by_tags()
        titles = [note.title.value for note in sorted_notes]
        self.assertEqual(titles, ["Note Z", "Note M", "Untagged C", "Untagged D"])

    def test_tie_breaker_by_title_when_primary_tag_matches(self) -> None:
        self.notebook.add("Second", "text", {"work"})
        self.notebook.add("First", "text", {"work", "zebra"})

        sorted_notes = self.notebook.sort_by_tags()
        titles = [note.title.value for note in sorted_notes]
        # У "First" найменший тег "work", у "Second" теж "work" -> порівнюємо за заголовком
        self.assertEqual(titles, ["First", "Second"])

    def test_command_output_contains_sorted_titles(self) -> None:
        self.notebook.add("Beta", "body", {"urgent"})
        self.notebook.add("Alpha", "body", {"alpha"})
        self.notebook.add("Plain", "body", set())

        output = self.command.run_with_notebook([], self.notebook)
        lines = output.splitlines()
        self.assertEqual(len(lines), 3)
        self.assertIn("Alpha", lines[0])
        self.assertIn("Beta", lines[1])
        self.assertIn("Plain", lines[2])


if __name__ == "__main__":
    unittest.main()