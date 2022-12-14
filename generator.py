import string
import secrets


class generator():

    def generate(length, symbols, uppercase):
        combination = string.ascii_lowercase + string.digits

        if symbols:
            combination += string.punctuation

        if uppercase:
            combination += string.ascii_uppercase

        combination_length = len(combination)

        new_password = ""

        for _ in range(length):
            new_password += combination[secrets.randbelow(combination_length)]

        return new_password
