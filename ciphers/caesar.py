from ciphers.base import BaseCipher
from utils.alphabets import alphabets

class Caesar(BaseCipher):
    def __init__(self, message, key):
        self.message = message
        self.key = key

    def set_key(self, key):
        self.key = key

    def set_message(self, message):
        self.message = message

    def encode(self):
        """
        :return: возвращает сообщение закодированное методом Цезаря
        """
        result: str = ''
        for char in self.message:
            is_encoded: bool = False
            for alphabet in alphabets.values():
                if char in alphabet:
                    result += alphabet[(alphabet.find(char) + self.key) % len(alphabet)]
                    is_encoded = True
                    break
            if not is_encoded:
                result += char
        return result

    def decode(self):
        """
        :return: возвращает сообщение декодированное методом Цезаря
        """
        result: str = ''
        for char in self.message:
            is_decoded: bool = False
            for alphabet in alphabets.values():
                if char in alphabet:
                    result += alphabet[(alphabet.find(char) - self.key) % len(alphabet)]
                    is_decoded = True
                    break
            if not is_decoded:
                result += char
        return result