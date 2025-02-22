from ciphers.base import BaseCipher
from utils.alphabets import alphabets

class Richelieu(BaseCipher):
    def __init__(self, message, key):
        self.message: str = message
        self.key: str = key

    def set_key(self, key: str):
        self.key = key

    def set_message(self, message: str):
        self.message = message

    def _parse_key(self):
        result = []
        for _ in self.key.split(')')[:-1]:
            result.append(list(map(int, _[1:].split(','))))
        return result

    @staticmethod
    def _validate_part(part: list):
        try:
            n = len(part)
            zeros = [0]*n
            for _ in part:
                if 0 < int(_) <= n:
                    zeros[int(_) - 1] = 1
                    continue
                raise ValueError
            if sum(zeros) != n:
                raise ValueError
        except ValueError:
            raise ValueError
        
    def _validate_key(self):
        ls = self.key.split(')')
        left_bracket_count = 0
        char_count1 = 0
        char_count2 = 0

        for _ in ls[:-1]:
            if len(_) == 0:
                continue 
            if _[0] == '(':
                left_bracket_count += 1
            lss = _[1:].split(',')
            self._validate_part(lss)
            char_count1 += len(lss)

        if left_bracket_count != len(ls)-1:
            raise ValueError
        
        for char in self.message:
            for alphabet in alphabets.values():
                if char in alphabet:
                    char_count2 += 1
                    break

        if char_count1 != char_count2:
            raise ValueError

    def encode(self):
        self._validate_key()
        result = ''
        subresult = ''
        indent = 0
        parts = self._parse_key()
        all_chars = ''
        for char in self.message:
            for alphabet in alphabets.values():
                if char in alphabet:
                    all_chars += char
        for part in parts:
            for _ in part:
                subresult += all_chars[indent + _ - 1]
            indent += len(part)
        i = 0
        for char in self.message:
            is_encoded = False
            for alphabet in alphabets.values():
                if char in alphabet:
                    result += subresult[i]
                    i += 1
                    is_encoded = True
                    break
            if not is_encoded:
                result += char
        return result
    
    def decode(self):
        self._validate_key()
        result = ''
        subresult = ''
        indent = 0
        parts: list[list] = self._parse_key()
        all_chars = ''
        for char in self.message:
            for alphabet in alphabets.values():
                if char in alphabet:
                    all_chars += char
        for part in parts:
            for i in range(len(part)):
                subresult += all_chars[indent + part.index(i+1)]
            indent += len(part)
        i = 0
        for char in self.message:
            is_encoded = False
            for alphabet in alphabets.values():
                if char in alphabet:
                    result += subresult[i]
                    i += 1
                    is_encoded = True
                    break
            if not is_encoded:
                result += char
        return result

