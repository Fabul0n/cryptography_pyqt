from ciphers.base import BaseCipher
from utils.alphabets import alphabets

class Gronsfeld(BaseCipher):
    def __init__(self, message, key):
        self.message: str = message
        self.key: str = key

    def set_key(self, key: str):
        self.key = key

    def set_message(self, message: str):
        self.message = message

    def _validate_key(self):
        pass

    def encode(self):
        self._validate_key()
        result = ''
        i = 0
        for char in self.message:
            is_encoded = 0
            for alphabet in alphabets.values():
                if char in alphabet:
                    result += alphabet[(alphabet.find(char) + int(self.key[i % len(self.key)])) % len(alphabet)]
                    i += 1
                    is_encoded = 1
            if not is_encoded:
                result += char
        
        return result
            
    def decode(self):
        self._validate_key()
        result = ''
        i = 0
        for char in self.message:
            is_decoded = 0
            for alphabet in alphabets.values():
                if char in alphabet:
                    result += alphabet[(alphabet.find(char) - int(self.key[i % len(self.key)])) % len(alphabet)]
                    is_decoded = 1
                    i += 1
                    break
            if not is_decoded:
                result += char
        
        return result

