from personal_helper.commands.base_command import NotebookCommand
from personal_helper.core.decorators import input_error
from personal_helper.core.data import parse_options
from personal_helper.models.notes import Notebook


class DeleteNoteCommand(NotebookCommand):
    """Command to delete a note."""

    def get_command_name(self) -> str:
        return "delete-note"

    def get_description(self) -> str:
        return "delete a note"

    def get_usage(self) -> str:
        return "delete-note --title <title>"

    @input_error
    def run_with_notebook(self, args: list, notebook: Notebook) -> str:
        options = parse_options(
            args, {"--title"}, {"--title"}, self.get_usage()
        )
        title = " ".join(options["--title"])
        notebook.delete(title)
        return f"✅ Note '{title}' deleted."
