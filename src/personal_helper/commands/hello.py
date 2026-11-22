from personal_helper.commands.base_command import BaseCommand
from personal_helper.models.personal_helper import PersonalHelper


class HelloCommand(BaseCommand):
    """Command that greets the user."""

    def get_command_name(self) -> str:
        return "hello"

    def get_description(self) -> str:
        return "get a greeting from the bot"

    def get_usage(self) -> str:
        return "hello"

    def run(self, args: list, data: PersonalHelper) -> str:
        return "How can I help you?"
