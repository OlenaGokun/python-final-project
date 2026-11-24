from collections.abc import Iterable

from .fields import Name, Phone, Birthday, Email
from personal_helper.core import CommandError, DuplicatePhoneError, PhoneNotFoundError


class Record:
    def __init__(self, name):
        self._name = Name(name)
        self._phones = []
        self._birthday = None
        self._email = None

    @property
    def name(self) -> Name:
        return self._name

    @property
    def phones(self) -> tuple[Phone, ...]:
        # A tuple, so callers can't bypass add_phone/remove_phone validation.
        return tuple(self._phones)

    @property
    def birthday(self) -> Birthday | None:
        return self._birthday

    @property
    def email(self) -> Email | None:
        return getattr(self, "_email", None)

    def copy_with_name(self, name: str) -> "Record":
        replacement = Record(name)
        replacement._phones = list(self.phones)
        replacement._birthday = self.birthday
        replacement._email = self.email
        return replacement

    def add_birthday(self, birthday):
        new_birthday = Birthday(birthday)
        self._birthday = new_birthday
        return new_birthday

    def remove_birthday(self) -> Birthday:
        birthday = self.birthday
        if birthday is None:
            raise CommandError(f"Birthday not set for {self.name}.")
        self._birthday = None
        return birthday

    def add_phone(self, phone, alias: str | None = None):
        new_phone = Phone(phone, alias)
        self._validate_phone(new_phone, self._phones)
        self._phones.append(new_phone)
        return new_phone

    def remove_phone(self, phone):
        found = self.find_phone(phone)
        if found is None:
            raise PhoneNotFoundError(f"Phone {phone} not found for {self.name}.")
        self._phones.remove(found)
        return found

    def edit_phone(self, old_phone, new_phone):
        found = self.find_phone(old_phone)
        if found is None:
            raise PhoneNotFoundError(f"Phone {old_phone} not found for {self.name}.")
        replacement = Phone(new_phone, found.alias)
        other_phones = (phone for phone in self._phones if phone is not found)
        self._validate_phone(replacement, other_phones)
        # replace in place so the phone order is preserved
        self._phones[self._phones.index(found)] = replacement
        return replacement

    def find_phone(self, phone):
        key = phone.casefold() if isinstance(phone, str) else phone
        return next(
            (
                p for p in self._phones
                if p.value == phone or (key is not None and p.alias_key == key)
            ),
            None,
        )

    def _validate_phone(self, candidate: Phone, existing: Iterable[Phone]) -> None:
        alias_key = candidate.alias_key
        for phone in existing:
            selectors = (phone.value, phone.alias_key)
            if alias_key is not None and alias_key in selectors:
                raise DuplicatePhoneError(
                    f"Phone alias '{candidate.alias}' already exists for {self.name}."
                )
            if candidate.value in selectors:
                raise DuplicatePhoneError(
                    f"Phone {candidate.value} already exists for {self.name}."
                )

    def add_email(self, email):
        new_email = Email(email)
        self._email = new_email
        return new_email

    def remove_email(self) -> Email:
        email = self.email
        if email is None:
            raise CommandError(f"Email not set for {self.name}.")
        self._email = None
        return email

    def update_details(
        self,
        phones: Iterable[str] = (),
        email: str | None = None,
        birthday: str | None = None,
    ) -> None:
        updated_phones = list(self._phones)
        for value in phones:
            phone = Phone(value)
            self._validate_phone(phone, updated_phones)
            updated_phones.append(phone)

        new_email = Email(email) if email is not None else None
        new_birthday = Birthday(birthday) if birthday is not None else None

        self._phones = updated_phones
        if new_email is not None:
            self._email = new_email
        if new_birthday is not None:
            self._birthday = new_birthday

    def __str__(self):
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        email_str = f", email: {self.email}" if self.email else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(map(str, self.phones))}{email_str}{birthday_str}"

    def __repr__(self):
        birthday_repr = f", birthday={self.birthday.value!r}" if self.birthday else ""
        email_repr = f", email={self.email.value!r}" if self.email else ""
        return f"Record({self.name.value!r}, phones={[p.value for p in self.phones]!r}{email_repr}{birthday_repr})"
