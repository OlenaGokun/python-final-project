from collections import UserDict
from datetime import datetime, date, timedelta
import calendar
from address_book.core import ContactNotFoundError, DuplicateContactError

class AddressBook(UserDict):

    @staticmethod
    def _birthday_in_year(birthday, year):
        """Feb 29 birthdays fall back to Feb 28 in non-leap years."""
        if birthday.month == 2 and birthday.day == 29 and not calendar.isleap(year):
            return birthday.replace(year=year, day=28)
        return birthday.replace(year=year)

    
    @staticmethod
    def _next_birthday(birthday, today):
        occurrence = AddressBook._birthday_in_year(birthday, today.year)
        if occurrence < today:
            # Re-derive from birthday: bumping occurrence would carry a Feb 28 fallback
            # into a leap year, or crash on a Feb 29 occurrence.
            occurrence = AddressBook._birthday_in_year(birthday, today.year + 1)
        return occurrence


    def get_upcoming_birthdays(self):
        """Return list of dicts with contact info for birthdays in the next 7 days."""
        users_to_congratulate = []
        today = date.today()
        
        for record in self.data.values():
            if not hasattr(record, 'birthday') or record.birthday is None:
                continue
            
            birthday = record.birthday.value
            next_birthday = self._next_birthday(birthday, today)
            
            number_of_days_until_birthday = (next_birthday - today).days
            if number_of_days_until_birthday <= 7:
                congratulation_date = next_birthday
                if congratulation_date.weekday() >= 5:
                    congratulation_date += timedelta(days=7 - congratulation_date.weekday())
                
                users_to_congratulate.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation_date.strftime("%d.%m.%Y")
                })
        
        return users_to_congratulate


    @staticmethod
    def _key(name):
        """Normalize a user-supplied name the same way Name.key does."""
        return name.strip().casefold() if isinstance(name, str) else name

    # Route the dict interface (book[name], name in book, del book[name])
    # through the same case-insensitive key as find()/delete().
    def __getitem__(self, name):
        key = self._key(name)
        try:
            return super().__getitem__(key)
        except KeyError:
            raise ContactNotFoundError(f"Contact '{name}' not found.")

    def __setitem__(self, name, record):
        super().__setitem__(self._key(name), record)

    def __delitem__(self, name):
        super().__delitem__(self._key(name))

    def __contains__(self, name):
        return super().__contains__(self._key(name))

    def add_record(self, record):
        if record.name.key in self.data:
            existing = self.data[record.name.key]
            raise DuplicateContactError(f"Contact '{existing.name.value}' already exists.")
        self.data[record.name.key] = record
        return record

    def find(self, name):
        return self.data.get(self._key(name))

    def delete(self, name):
        return self.data.pop(self._key(name), None)

    def __str__(self):
        if not self.data:
            return "Address book is empty."
        return "\n".join(str(record) for record in self.data.values())

    
