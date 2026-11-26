from personal_helper.commands.base_command import NotebookCommand
from personal_helper.core.decorators import input_error
from personal_helper.core.data import parse_options
from personal_helper.core.exceptions import InvalidInputError
from personal_helper.models.notes import Notebook


class UpdateNoteCommand(NotebookCommand):
    """Command to update a note."""

    def get_command_name(self) -> str:
        return "update-note"

    def get_description(self) -> str:
        return "update note text or replace its tags"

    def get_usage(self) -> str:
        return "update-note --title <title> [--text <text>] [--tags <tag> ...]"

    @input_error
    def run_with_notebook(self, args: list, notebook: Notebook) -> str:
        options = parse_options(
            args,
            {"--title", "--text", "--tags"},
            {"--title"},
            self.get_usage(),
        )
        if "--text" not in options and "--tags" not in options:
            raise InvalidInputError(
                "Invalid arguments. Provide --text or --tags.\n"
                f"Usage: {self.get_usage()}"
            )
        title = " ".join(options["--title"])
        notebook.update_note(
            title,
            text=" ".join(options["--text"]) if "--text" in options else None,
            tags=set(options["--tags"]) if "--tags" in options else None,
        )
        return f"✅ Note '{title}' updated."
