from ciphers.base import BaseCipher
from utils.get_alphabets import alphabets

class Atbash(BaseCipher):
    def __init__(self, message: str):
        self.message: str = message

    def set_message(self, message: str):
        self.message: str = message

    def encode(self) -> str:
        """
        :return: возвращает сообщение закодированное методом Атбаш
        """
        result: str = ''
        is_encoded = False
        for char in self.message:
            for alphabet in alphabets.values():
                if char in alphabet:
                    result += alphabet[::-1][alphabet.find(char)]
                    is_encoded = True
            if not is_encoded: 
                result += char
        return result
    
    def decode(self) -> str:
        """
        :return: возвращает сообщение раскодированное методом Атбаш
        """
        result: str = ''
        is_encoded = False
        for char in self.message:
            for alphabet in alphabets.values():
                if char in alphabet:
                    result += alphabet[::-1][alphabet.find(char)]
                    is_encoded = True
            if not is_encoded: 
                result += char
        return result
            
