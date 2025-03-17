from ciphers.base import BaseCipher
from utils.alphabets import alphabets
import re

class Vigenere(BaseCipher):
    def __init__(self, message, key):
        self.message: str = message
        self.key: str = key

    def set_key(self, key: str):
        self.key = key

    def set_message(self, message: str):
        self.message = message

    def _validate_key(self):
        unique_chars = set()
        for alph in alphabets.values():
            unique_chars.update(alph)

        pattern = f"^[{''.join(re.escape(c) for c in unique_chars)}]+$"
        if not re.fullmatch(pattern, self.key):
            raise ValueError 

    def encode(self):
        self._validate_key()
        result = ''
        i = 0
        for char in self.message:
            is_encoded = 0
            for char_alphabet in alphabets.values():
                if char in char_alphabet:
                    for key_alphabet in alphabets.values():
                        if self.key[i % len(self.key)] in key_alphabet:
                            result += char_alphabet[(char_alphabet.find(char) + key_alphabet.find(self.key[i%len(self.key)])) % len(char_alphabet)]
                            i += 1
                            is_encoded = 1
                            break
                    if is_encoded:
                        break
            if not is_encoded:
                result += char
        
        return result
            
    def decode(self):
        self._validate_key()
        result = ''
        i = 0
        for char in self.message:
            is_encoded = 0
            for char_alphabet in alphabets.values():
                if char in char_alphabet:
                    for key_alphabet in alphabets.values():
                        if self.key[i % len(self.key)] in key_alphabet:
                            result += char_alphabet[(char_alphabet.find(char) - key_alphabet.find(self.key[i%len(self.key)])) % len(char_alphabet)]
                            is_encoded = 1
                            i += 1
                            break
                    if is_encoded:
                        break
            if not is_encoded:
                result += char
        
        return result

