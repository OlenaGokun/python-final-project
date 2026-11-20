from .fields import Name, Phone, Birthday
from address_book.core import ContactNotFoundError, PhoneNotFoundError, DuplicatePhoneError


class Record:
    def __init__(self, name):
        self._name = Name(name)
        self._phones = []
        self._birthday = None

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

    def add_birthday(self, birthday):
        new_birthday = Birthday(birthday)
        self._birthday = new_birthday
        return new_birthday

    def add_phone(self, phone):
        new_phone = Phone(phone)
        if self.find_phone(phone) is not None:
            raise DuplicatePhoneError(f"Phone {phone} already exists for {self.name}.")
        self._phones.append(new_phone)
        return new_phone

    def remove_phone(self, phone):
        found = self.find_phone(phone)
        if found is None:
            raise PhoneNotFoundError(f"Phone {phone} not found for {self.name}.")
        self._phones.remove(found)
        return found

    def edit_phone(self, old_phone, new_phone):
        replacement = Phone(new_phone)
        found = self.find_phone(old_phone)
        if found is None:
            raise PhoneNotFoundError(f"Phone {old_phone} not found for {self.name}.")
        # replace in place so the phone order is preserved
        self._phones[self._phones.index(found)] = replacement
        return replacement

    def find_phone(self, phone):
        return next((p for p in self._phones if p.value == phone), None)

    def __str__(self):
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"

    def __repr__(self):
        birthday_repr = f", birthday={self.birthday.value!r}" if self.birthday else ""
        return f"Record({self.name.value!r}, phones={[p.value for p in self.phones]!r}{birthday_repr})"

