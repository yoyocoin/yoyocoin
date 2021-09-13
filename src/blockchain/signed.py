from abc import ABC, abstractmethod


class Signed(ABC):
    @property
    @abstractmethod
    def verifying_key(self) -> str:
        return NotImplemented

    @property
    @abstractmethod
    def hash(self) -> str:
        return NotImplemented

    @property
    @abstractmethod
    def is_signed(self) -> bool:
        return NotImplemented

    @abstractmethod
    def add_signature(self, signature):
        return NotImplemented

    @abstractmethod
    def signature_verified(self) -> bool:
        return NotImplemented
