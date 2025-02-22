from abc import ABC, abstractmethod

class BaseCipher(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def set_key(self, key):
        pass

    @abstractmethod
    def set_message(self, message: str):
        pass

    @abstractmethod
    def encode(self):
        pass

    @abstractmethod
    def decode(self):
        pass
