from ciphers.base import BaseCipher
from utils.alphabets import alphabets

class Atbash(BaseCipher):
    def __init__(self, message: str):
        self.message: str = message

    def set_key(self, key):
        """
        Does nothing in this cipher
        """
        pass

    def set_message(self, message: str):
        self.message: str = message

    def encode(self) -> str:
        """
        :return: возвращает сообщение закодированное методом Атбаш
        """
        result: str = ''
        for char in self.message:
            is_encoded: bool = False
            for alphabet in alphabets.values():
                if char in alphabet:
                    result += alphabet[::-1][alphabet.find(char)]
                    is_encoded = True
                    break
            if not is_encoded: 
                result += char
        return result
    
    def decode(self) -> str:
        """
        :return: возвращает сообщение декодированное методом Атбаш
        """
        result: str = ''
        for char in self.message:
            is_decoded: bool = False
            for alphabet in alphabets.values():
                if char in alphabet:
                    result += alphabet[::-1][alphabet.find(char)]
                    is_decoded = True
            if not is_decoded: 
                result += char
        return result
            
