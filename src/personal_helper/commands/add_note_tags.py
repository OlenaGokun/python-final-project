from personal_helper.commands.base_command import NotebookCommand
from personal_helper.core.decorators import input_error
from personal_helper.core.data import parse_options
from personal_helper.models.notes import Notebook


class AddNoteTagsCommand(NotebookCommand):
    def get_command_name(self) -> str:
        return "add-note-tags"

    def get_description(self) -> str:
        return "add tags to a note"

    def get_usage(self) -> str:
        return "add-note-tags --title <title> --tags <tag> [tag ...]"

    @input_error
    def run_with_notebook(self, args: list, notebook: Notebook) -> str:
        required = {"--title", "--tags"}
        options = parse_options(args, required, required, self.get_usage())
        title = " ".join(options["--title"])
        notebook.add_tags(title, set(options["--tags"]))
        return f"✅ Tags added to note '{title}'."
