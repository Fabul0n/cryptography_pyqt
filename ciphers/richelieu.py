from ciphers.base import BaseCipher

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
        for _ in self.key:
            if _ not in '()0123456789,':
                raise ValueError
        ls = self.key.split(')')
        left_bracket_count = 0
        char_count1 = 0

        if ls[-1] != '':
            raise ValueError

        for _ in ls[:-1]:
            if len(_) == 0:
                continue 
            if _[0] == '(':
                left_bracket_count += 1
            lss = _[1:].split(',')
            self._validate_part(lss)
            char_count1 += len(lss)

        if left_bracket_count != len(ls)-1 or left_bracket_count == 0:
            raise ValueError

        if char_count1 > len(self.message):
            raise ValueError

    def encode(self):
        self._validate_key()
        result = ''
        indent = 0
        parts = self._parse_key()
        for part in parts:
            for _ in part:
                result += self.message[indent + _ - 1]
            indent += len(part)
        return result
    
    def decode(self):
        self._validate_key()
        result = ''
        indent = 0
        parts: list[list] = self._parse_key()
        for part in parts:
            for i in range(len(part)):
                result += self.message[indent + part.index(i+1)]
            indent += len(part)
        return result

