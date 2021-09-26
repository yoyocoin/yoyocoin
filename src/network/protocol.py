from abc import ABC, abstractmethod
from .message import Message


class Protocol(ABC):
    name: str = 'protocol name'  # Protocol name (for finding related messages)

    def __init__(self, node):
        self.node = node

    @abstractmethod
    def handle(self, sender, message):
        raise NotImplementedError

    def __contains__(self, message: Message):
        return message.dict_message.get("protocol", None) == self.__class__.name
