from personal_helper.commands.base_command import NotebookCommand
from personal_helper.core.decorators import input_error
from personal_helper.models.notes import Notebook


class SortNotesByTagsCommand(NotebookCommand):
    """Command to sort notes by tags."""

    def get_command_name(self) -> str:
        return "sort-notes-by-tags"

    def get_description(self) -> str:
        return "sort notes by tags"

    def get_usage(self) -> str:
        return "sort-notes-by-tags"

    @input_error
    def run_with_notebook(self, args: list, notebook: Notebook) -> str:
        notes = notebook.sort_by_tags()
        if not notes:
            return "ℹ️  No notes found."
        return "\n".join(self.format_note_compact(note) for note in notes)