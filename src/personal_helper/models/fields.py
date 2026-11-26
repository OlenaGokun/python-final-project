from datetime import date, datetime
import re
from personal_helper.core import (
    InvalidBirthdayFormatError,
    InvalidNameError,
    InvalidNoteError,
    InvalidPhoneFormatError,
    InvalidInputError,
)


class Field:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{type(self).__name__}({self.value!r})"

    def __eq__(self, other):
        if isinstance(other, Field):
            return type(self) is type(other) and self.value == other.value
        return NotImplemented

    def __hash__(self):
        return hash((type(self), self.value))


class Name(Field):
    def __init__(self, value):
        if not isinstance(value, str) or not value.strip():
            raise InvalidNameError(
                "Name is required and must be a non-empty string."
            )
        super().__init__(value.strip())

    @property
    def key(self) -> str:
        """Case-insensitive key used to store and look up records."""
        return self.value.casefold()


class Title(Field):
    def __init__(self, value):
        if not isinstance(value, str) or not value.strip():
            raise InvalidNoteError("Note title must be a non-empty string.")
        super().__init__(value.strip())

    @property
    def key(self) -> str:
        return self.value.casefold()


class Text(Field):
    def __init__(self, value):
        if not isinstance(value, str) or not value.strip():
            raise InvalidNoteError("Note text must be a non-empty string.")
        super().__init__(value.strip())


class Tag(Field):
    def __init__(self, value):
        if (
            not isinstance(value, str)
            or not value
            or any(character.isspace() for character in value)
        ):
            raise InvalidNoteError("Tags must be single non-empty words.")
        super().__init__(value.casefold())


PHONE_ALLOWED_CHARS = re.compile(r"^[0-9+\-\s()]+$")
PLUS_PREFIX_PATTERN = re.compile(r"^\+38")


def has_valid_plus_and_parens(cleaned: str) -> bool:
    if "+" in cleaned:
        if not PLUS_PREFIX_PATTERN.match(cleaned) or cleaned.count("+") > 1:
            return False

    depth = 0
    for ch in cleaned:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def normalize_phone(phone_number, length=10):
    if not isinstance(phone_number, str):
        raise InvalidPhoneFormatError(
            f"Phone must be a string, got {phone_number!r}."
        )

    cleaned = phone_number.strip()
    if not cleaned or not PHONE_ALLOWED_CHARS.fullmatch(cleaned):
        raise InvalidPhoneFormatError(
            f"Phone must be a valid phone number, got {phone_number!r}."
        )

    if not has_valid_plus_and_parens(cleaned):
        raise InvalidPhoneFormatError(
            "Invalid '+' placement or parentheses in phone number: "
            f"{phone_number!r}."
        )

    digits = "".join(ch for ch in cleaned if "0" <= ch <= "9")

    if len(digits) == length:
        normalized = digits
    elif len(digits) == length + 2 and digits.startswith("38"):
        normalized = digits[2:]
    elif len(digits) == length + 1 and digits.startswith("8"):
        normalized = digits[1:]
    else:
        raise InvalidPhoneFormatError(
            f"Phone must have {length} digits, got {phone_number!r}."
        )

    return normalized


class Phone(Field):
    LENGTH = 10

    def __init__(self, value, alias: str | None = None):
        normalized_value = normalize_phone(value, length=self.LENGTH)
        if alias is not None and (
            not isinstance(alias, str)
            or not alias
            or any(character.isspace() for character in alias)
        ):
            raise InvalidInputError(
                "Phone alias must be a single non-empty word."
            )
        super().__init__(normalized_value)
        self._alias = alias

    @property
    def alias(self) -> str | None:
        # Phone objects saved before aliases have no _alias attribute.
        return getattr(self, "_alias", None)

    @property
    def alias_key(self) -> str | None:
        alias = self.alias
        return alias.casefold() if alias is not None else None

    def __str__(self) -> str:
        return (
            f"{self.alias}: {self.value}"
            if self.alias is not None
            else self.value
        )


class Birthday(Field):
    def __init__(self, value):
        try:
            date_obj = datetime.strptime(value, "%d.%m.%Y").date()
        except (ValueError, TypeError):
            raise InvalidBirthdayFormatError(
                "Invalid date format. Use DD.MM.YYYY"
            )
        super().__init__(date_obj)

    @property
    def value(self) -> date:
        return self._value

    def __str__(self):
        # Same format the user types it in.
        return self.value.strftime("%d.%m.%Y")
<<<<<<< HEAD
    
=======


>>>>>>> decb029 (added linter, fixed issues)
class Email(Field):
    EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(self, value):
        if not isinstance(value, str):
            raise ValueError(f"Invalid email format: {value!r}.")
        cleaned = value.strip()
        if not cleaned or not self.EMAIL_PATTERN.match(cleaned):
            raise ValueError(f"Invalid email format: {value!r}.")
        super().__init__(cleaned)


class Address(Field):
    def __init__(self, value):
        if not isinstance(value, str) or not value.strip():
            raise InvalidInputError("Address must be a non-empty string.")
        super().__init__(value.strip())
