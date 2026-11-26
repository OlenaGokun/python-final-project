from personal_helper.commands.base_command import NotebookCommand
from personal_helper.core.decorators import input_error
from personal_helper.core.data import parse_options
from personal_helper.models.notes import Notebook


class AddNoteCommand(NotebookCommand):
    """Command to add a note."""

    def get_command_name(self) -> str:
        return "add-note"

    def get_description(self) -> str:
        return "add a note"

    def get_usage(self) -> str:
        return "add-note --title <title> --text <text> [--tags <tag> ...]"

    @input_error
    def run_with_notebook(self, args: list, notebook: Notebook) -> str:
        options = parse_options(
            args,
            {"--title", "--text", "--tags"},
            {"--title", "--text"},
            self.get_usage(),
        )
        title = " ".join(options["--title"])
        text = " ".join(options["--text"])
        tags = set(options.get("--tags", []))
        notebook.add(title, text, tags)
        return f"✅ Note '{title}' added."
