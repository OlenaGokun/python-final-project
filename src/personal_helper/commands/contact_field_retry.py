from collections.abc import Callable
from typing import Literal

from personal_helper.core.exceptions import CommandError, InvalidPhoneFormatError
from personal_helper.models.fields import Email, Phone


FieldRetryHandler = Callable[[str, Exception], str | None]


class ContactFieldRetry:
    """Optionally request replacements for invalid contact fields."""

    _field_retry_handler: FieldRetryHandler | None = None

    def set_field_retry_handler(self, handler: FieldRetryHandler) -> None:
        self._field_retry_handler = handler

    def _validate_contact_field(self, value: str, field: Literal["phone", "email"]) -> str:
        retry = self._field_retry_handler
        if retry is None:
            return value

        validator = Phone if field == "phone" else Email
        error_type = InvalidPhoneFormatError if field == "phone" else ValueError
        while True:
            try:
                validator(value)
                return value
            except error_type as error:
                replacement = retry(field, error)
                if replacement is None:
                    raise CommandError("Command canceled.") from None
                value = replacement
