from personal_helper.commands.base_command import NotebookCommand
from personal_helper.models.notes import Notebook


class ShowAllNotesCommand(NotebookCommand):
    """Command to show all notes in the notebook."""

    def get_command_name(self) -> str:
        return "show-all-notes"

    def get_description(self) -> str:
        return "show all notes in the notebook"

    def get_usage(self) -> str:
        return "show-all-notes"

    def run_with_notebook(self, args: list, notebook: Notebook) -> str:
        if not notebook.data:
            return "ℹ️  No notes found."
        return "\n".join(f"{note.title}: {note.text}" for note in notebook.data.values())
