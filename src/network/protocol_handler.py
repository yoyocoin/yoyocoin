from typing import List, Callable
from threading import Thread
from queue import Queue

from loguru import logger

from .message import Message, PREFIX
from .protocol import Protocol


class InternalProtocolHandler(Thread):
    def __init__(self, messages_queue: Queue, protocols: List[Protocol], external_message_callback: Callable):
        super().__init__(daemon=True, name="Protocol Handler")
        self._messages_queue = messages_queue
        self._external_message_callback = external_message_callback
        self._stop = False
        self._protocols = protocols

    def _handle_message(self, sender, message):
        for protocol in self._protocols:
            if message in protocol:  # Check for compatible protocol
                protocol.handle(sender, message)
                break
        else:
            # Handle no protocol message
            pass

    def run(self):
        logger.debug("Protocol handler thread started")
        while not self._stop:
            connection_address, message_bytes = self._messages_queue.get()
            if not message_bytes.startswith(PREFIX):
                self._external_message_callback((connection_address, message_bytes))
                continue
            try:
                message = Message.from_bytes(message_bytes)
                self._handle_message(connection_address, message)
            except Exception:
                logger.exception("Protocol handler exception")
