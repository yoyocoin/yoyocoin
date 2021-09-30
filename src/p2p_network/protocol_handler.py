from typing import List, Callable
from threading import Thread
from queue import Queue

from loguru import logger

from .message import Message
from .protocol import Protocol


class InternalProtocolHandler(Thread):
    def __init__(self, messages_queue: Queue, protocols: List[Protocol], external_message_callback: Callable):
        super().__init__(daemon=True, name="Protocol Handler")
        self._messages_queue = messages_queue
        self._external_message_callback = external_message_callback
        self._stop = False
        self._protocols = protocols

    def _handle_message(self, sender, message) -> bool:
        """
        Find message protocol and call it handle method on the message
        :param sender: address the message sent from
        :param message: message object
        :return: did found message protocol
        """
        for protocol in self._protocols:
            if message in protocol:  # Check for compatible protocol
                protocol.handle(sender, message)
                return True
        return False

    def run(self):
        logger.debug("Protocol handler thread started")
        while not self._stop:
            connection_address, message_bytes = self._messages_queue.get()
            try:
                message = Message.from_bytes(message_bytes)
                processed = self._handle_message(connection_address, message)
                if not processed:
                    self._external_message_callback((connection_address, message_bytes))
            except Exception:
                logger.exception("Protocol handler exception")
