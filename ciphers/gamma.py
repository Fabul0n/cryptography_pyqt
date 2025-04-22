from ciphers.base import BaseCipher

class RandGen:
    def __init__(self, seed = 2281337, a = 1103515245, c = 12345, m = 2**64):
        self.seed = seed
        self.a = a
        self.c = c
        self.m = m
        
    def gen(self):
        self.seed = (self.seed * self.a + self.c) % self.m
        return (self.seed//65536)

class Gamma(BaseCipher):
    def __init__(self, message, seed = 2281337, a = 1103515245, c = 12345, m = 2**64):
        self.random = RandGen(seed, a, c, m)
        self.message: str = message

    def set_key(self):
        pass

    def set_message(self, message):
        self.message = message

    def encode(self):
        data = self.message.encode('utf-8')
        res = bytearray()
        for byte in data:
            gamma = self.random.gen() & 0xFF
            res.append(byte ^ gamma)
        return bytes(res).hex()

    def decode(self):
        data = bytes.fromhex(self.message)
        res = bytearray()
        for byte in data:
            gamma = self.random.gen() & 0xFF
            res.append(byte ^ gamma)
        return bytes(res)