from personal_helper.commands.base_command import NotebookCommand
from personal_helper.core.decorators import input_error
from personal_helper.core.data import parse_options
from personal_helper.models.notes import Notebook


class DeleteNoteTagsCommand(NotebookCommand):
    def get_command_name(self) -> str:
        return "delete-note-tags"

    def get_description(self) -> str:
        return "remove selected tags or all tags from a note"

    def get_usage(self) -> str:
        return "delete-note-tags --title <title> [--tags <tag> [tag ...]]"

    @input_error
    def run_with_notebook(self, args: list, notebook: Notebook) -> str:
        options = parse_options(
            args, {"--title", "--tags"}, {"--title"}, self.get_usage()
        )
        title = " ".join(options["--title"])
        if "--tags" in options:
            notebook.remove_tags(title, set(options["--tags"]))
        else:
            notebook.update_note(title, tags=set())
        return f"✅ Tags removed from note '{title}'."
