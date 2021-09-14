from abc import ABC, abstractmethod


class Signed(ABC):
    @property
    @abstractmethod
    def verifying_key(self) -> str:
        pass

    @property
    @abstractmethod
    def hash(self) -> str:
        pass

    @property
    @abstractmethod
    def is_signed(self) -> bool:
        pass

    @abstractmethod
    def add_signature(self, signature):
        pass

    @abstractmethod
    def signature_verified(self) -> bool:
        pass
