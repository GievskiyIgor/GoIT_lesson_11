from collections import UserDict
from datetime import datetime
import re

class Field ():
    def __init__(self, value) -> None:
        self.value = value
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return str(self)
 
class Name (Field):
    pass
    
class Phone (Field):
    def __init__(self, value=None):
        self.value = value
        
    @property
    def value(self):
        return self._value
        
    @value.setter
    def value(self, value):
        if value is None:
            self._value = value
        else:
            self._value = self.number_phone(value)
        
    def number_phone(self, phone:str):
        if not re.match(r"^\+[\d]{12}$", phone):
                raise ValueError
        return phone

class Birthday (Field):
    def __init__(self, value) -> None:
        # super().__init__(value)
        self.__value = None
        self.value = value

    @property
    def value (self):
        return self.__value.strftime('%d-%m-%Y')

    @value.setter
    def value(self, value):
        try:
            self.__value = datetime.strptime(value, '%d-%m-%Y')
        except ValueError:
            raise ValueError('"dd-mm-yyyy" - birthday format')    


class Record ():
    def __init__(self, name:Name, phone:Phone = None, birthday:Birthday = None):
        self.name = name
        self.phones = [phone] if phone else [] 
        self.birthday = birthday
    
    # Добавление телефона из адресной книги
    def add_phone(self, phone:Phone):
        self.phones.append(phone)

    # Удаление телефона из адресной книги
    def remove_record(self, phone:Phone):
        # self.phones.remove(phone)
        for i, p in enumerate(self.phones):
            if p.value == phone.value:
                self.phones.pop(i)
                return f"Phone {phone} deleted successfully"
        return f'Contact has no phone {phone}'  
    
    # Изменение телефона в адресной книги
    def change_phone(self, old_phone:Phone, new_phone:Phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone.value:
                self.phones[i] = new_phone
                return f'Phone {old_phone} change to {new_phone}'
        return f'Contact has no phone {old_phone}'   
    
    # день рождения
    def set_birthday(self, birthday):
        self.birthday = birthday

    def get_birthday (self):    
        return self.birthday.value if self.birthday else None
    
    def days_to_birthday(self):
        
        if self.birthday:
            dateB = self.birthday
            today = datetime.date.today()
            current_year_dateB = datetime.date(today.year, dateB.month, dateB.day)

            if current_year_dateB < today:
                current_year_dateB = datetime.date(today.year+1, dateB.month, dateB.day)

            delta =current_year_dateB - today    
            return delta.days
        
        return None
    
    def __str__(self):
        result = ''
        phones = ", ".join([str(phone) for phone in self.phones])
    
        if self.birthday:
            result += f"{self.name}: {phones}. Birthday: {self.birthday}\n"
        else:
            result += f"{self.name}: {phones}"
        return result
   
class AddressBook(UserDict):
    index = 0
    def add_record(self, record: Record):
        self.data[record.name.value] = record
    
    def __iter__(self):
        self.keys_list = sorted(self.data.keys())
        return self

    # def __next__(self):
    #     if self.index >=len(self.keys_list):
    #         raise StopIteration
    #     else:
    #         name =self.keys_list[self.index]
    #         self.index +=1
    #         return self[name]

    def iterator(self, n=2):
        self.keys_list = sorted(self.data.keys())
        if self.index < len(self.keys_list):
            yield from [self[name] for name in self.keys_list[self.index:self.index+n]]
            self.index +=n
        else:
            self.index = 0
            self.keys_list =[]
    
    # def __str__(self) -> str:
    #     return str(self.value)
    
    # def __repr__(self) -> str:
    #     return str(self)

user_contacts = AddressBook()

def user_help ():
   return """
          Phone book commands:
          1. hello
          2. add 'Name' 'phone number" 'birthday' - (Igor +380989709609 28-05-1982) 
          3. change 'Name' 'phone number1' 'phone number1'  - (Igor +380989709609 +380990509393)
          4. phone 'Name'
          5. remove 'Name' 'phone number'  - (Igor +380989709609') 
          6. show all
          7. good bye
          8. close
          9. exit
          """
 
# Decorator input errors
def input_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except KeyError:
            return f"This contact {' '.join(args)} doesn't exist in the phone book"
        except ValueError:
            return "The entered name and phone number do not match the given parameter. For help, type 'help'"
        except IndexError:
            return "Type all params for command. For help, type 'help'"

    return wrapper

# Greetings
@input_error
def user_hello(*args):
    return "How can I help you?"

# Add добавление номера в адресную книгу
@input_error
def user_add(*args):
    name = Name(args[0])
    phone = Phone(args[1])
    birthday = Birthday(args[2]) 
    
    rec:Record = user_contacts.get(name.value)
    
    if not rec:
        if not birthday:
            birthday = None

        rec = Record(name, phone, birthday)
        user_contacts.add_record(rec)
        return f"{name} : {phone}, {birthday} has been added to the phone book"    
    
    rec.add_phone(phone)
    return f"Phone {phone} add to contact {name}"
    #  ****

# Change  изменение номера в адресной книги
@input_error
def user_change(*args):
    name = Name(args[0])
    old_phone = Phone(args[1])
    new_phone = Phone(args[2])
    
    rec = user_contacts.get(name.value)
    
    if rec:
        return rec.change_phone(old_phone, new_phone)
    
    return f'Phone book has no contact {name}'

    
# Contact phone number
@input_error
def user_phone(*args):
    name = Name(args[0])
    record = user_contacts[name.value]
   
    return f"The phone number for {name} is {record.phones}"
    

# Show all  вся адресная книга
@input_error
def user_show_all(*args):
    
    all = ""
    
    if len(user_contacts) == 0:
        return "Phone book is empty"
    else:
        for name in user_contacts.data:
           record = user_contacts.data[name]
           rec = Record(record.name.value, birthday=record.birthday.value)
           days_birthday = rec.days_to_birthday(rec.birthday)
           print(f"{record.name.value}: {', '.join(str(phone) for phone in record.phones)}. Dirthday {record.birthday.value}. Days birthday - {days_birthday}")
        #  for name, phone in user_contacts.items():
        #     all += f"{name}: {phone}\n"
        # return all
# 
@input_error
def remove_phone(*args):
    
    name = Name(args[0])
    phone = Phone(args[1])
    
    rec:Record = user_contacts[name.value]
    return rec.remove_record(phone) 
 
@input_error
def birthday_to_days(*args):
    name =Name(args[0])

    rec:Record = user_contacts.get(name.value)

    if rec:
        birthday = rec.birthday.value
        today = datetime.date.today()
        current_year_birthday = datetime.date(today.year, birthday.month, birthday.day)

    if current_year_birthday < today:
        current_year_birthday = datetime.date(today.year + 1 , birthday.month, birthday.day)
        delta = current_year_birthday - today
        return delta.days
    else:    
         print('No record found for '+ name)   




# Exit
def user_exit(*args): 
    return "Good bye!\n"

COMMANDS = {
    'hello': user_hello, # приветствие
    'add': user_add, # Добавление
    'change': user_change, # Изменение
    'phone': user_phone, # Телефон
    'show all': user_show_all, # Список контактов
    "remove": remove_phone, # удаление из адресной книги
    'good bye': user_exit, # выход
    'close': user_exit,
    'exit': user_exit,
    'help': user_help, # помощь
}
 
# Command processing
def command_handler(user_input: str):
    for cmd in COMMANDS:
        if user_input.startswith(cmd):
            return COMMANDS[cmd], user_input.replace(cmd, '').strip().split()
    return None, []

# ********
def main():
    
    print(user_help())

    while True:
        user_input = input("Enter a command: ")
        command, data = command_handler(user_input)

        if command == user_exit:
            break

        if not command:
            print("Command is not supported. Try again.")
            continue
        
        print(command(*data))


if __name__ == "__main__":
    main()
