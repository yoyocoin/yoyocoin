from typing import Tuple
from abc import ABC, abstractmethod
from time import time

from .message import Message

Address = Tuple[str, int]


class Protocol(ABC):
    name: str = 'protocol name'  # Protocol name (for finding related messages)

    def __init__(self, node, require_heartbeat: bool = False, heartbeat_interval: float = None):
        """ Create protocol
        extend node handling of incoming messages
        :param node: the network node
        :param require_heartbeat: need to call on heartbeat?
        :param heartbeat_interval: space between heartbeat calls
        """
        assert not require_heartbeat or heartbeat_interval is not None, "heartbeat interval is required!"

        self.node = node
        self.require_heartbeat = require_heartbeat
        self.last_heartbeat = time()
        self.heartbeat_interval = heartbeat_interval

    @abstractmethod
    def handle(self, sender: Address, message: Message):
        raise NotImplementedError

    def heartbeat(self):
        self.last_heartbeat = time()

    def __contains__(self, message: Message):
        return message.dict_message.get("protocol", None) == self.__class__.name
