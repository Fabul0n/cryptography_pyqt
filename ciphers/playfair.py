from ciphers.base import BaseCipher
from utils.alphabets import playfair_alphabets as alphabets
import re

class Playfair(BaseCipher):
    def __init__(self, message, key):
        self.message: str = message
        self.set_key(key)

    def set_key(self, key: str):
        self._validate_key(key)
        used = set()
        new_key = ''
        for _ in key:
            if _ not in used:
                new_key += _
                used.add(_)
        
        for alphabet in alphabets.values():
            for char in alphabet:
                if char not in used:
                    new_key += char
                    used.add(char)

        self.key = list()
        for i in range(10):
            tmp_list = []
            for j in range(15):
                tmp_list.append(new_key[i*15+j])
            self.key.append(tmp_list)

    def set_message(self, message: str):
        self.message = message

    @staticmethod
    def _validate_key(key):
        unique_chars = set()
        for alph in alphabets.values():
            unique_chars.update(alph)

        pattern = f"^[{''.join(re.escape(c) for c in unique_chars)}]+$"
        if not re.fullmatch(pattern, key):
            raise ValueError 
        
    @staticmethod
    def _validate_message(message):
        unique_chars = set()
        for alph in alphabets.values():
            unique_chars.update(alph)

        pattern = f"^[{''.join(re.escape(c) for c in unique_chars)}]+$"
        if not re.fullmatch(pattern, message):
            raise SyntaxError 
        
    def _split_into_bigrams(self):
        self._validate_message(self.message)
        bigrams = list()
        prev = ''
        for i, char in enumerate(self.message):
            if prev == '':
                prev = char
            elif prev == char:
                bigrams.append(prev+'~')
                prev = char
            else:
                bigrams.append(prev+char)
                prev = ''
        if prev:
            bigrams.append(prev+'~')
        return bigrams


    def encode(self):
        bigrams = self._split_into_bigrams()
        result = ''
        for bigram in  bigrams:
            tmp_bigram = ''
            first_x, first_y = 0, 0
            second_x, second_y = 0, 0
            f0, f1 = 0, 0
            for i in range(10):
                for j in range(15):
                    if bigram[0] == self.key[i][j]:
                        first_x, first_y = i, j
                        f0 = 1
                    if bigram[1] == self.key[i][j]:
                        second_x, second_y = i, j
                        f1 = 1
                    if f0 and f1:
                        break
                if f0 and f1:
                    break
            if first_x == second_x:
                tmp_bigram += self.key[first_x][(first_y+1)%15]
                tmp_bigram += self.key[second_x][(second_y+1)%15]
            elif first_y == second_y:
                tmp_bigram += self.key[(first_x+1)%10][first_y]
                tmp_bigram += self.key[(second_x+1)%10][second_y]
            else:
                tmp_bigram += self.key[first_x][second_y]
                tmp_bigram += self.key[second_x][first_y]
            result += tmp_bigram
        return result
                    
            
    def decode(self):
        if len(self.message) % 2:
            raise SyntaxError("message is incorrect")

        bigrams = [self.message[i:i+2] for i in range(0, len(self.message), 2)]
        result = ''
        for bigram in  bigrams:
            tmp_bigram = ''
            first_x, first_y = 0, 0
            second_x, second_y = 0, 0
            f0, f1 = 0, 0
            for i in range(10):
                for j in range(15):
                    if bigram[0] == self.key[i][j]:
                        first_x, first_y = i, j
                        f0 = 1
                    if bigram[1] == self.key[i][j]:
                        second_x, second_y = i, j
                        f1 = 1
                    if f0 and f1:
                        break
                if f0 and f1:
                    break
            if first_x == second_x:
                tmp_bigram += self.key[first_x][(first_y-1)%15]
                tmp_bigram += self.key[second_x][(second_y-1)%15]
            elif first_y == second_y:
                tmp_bigram += self.key[(first_x-1)%10][first_y]
                tmp_bigram += self.key[(second_x-1)%10][second_y]
            else:
                tmp_bigram += self.key[first_x][second_y]
                tmp_bigram += self.key[second_x][first_y]
            result += tmp_bigram

        tmp_result = result
        result = ''

        for _ in tmp_result:
            if _ != '~':
                result += _
                
        return result
