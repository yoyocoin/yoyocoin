from typing import List
from threading import Thread
from queue import Queue

from .message import Message
from .protocol import Protocol


class ProtocolHandler(Thread):
    def __init__(self, messages_queue: Queue, protocols: List[Protocol]):
        super().__init__(daemon=True, name="Protocol Handler")
        self.messages_queue = messages_queue
        self._stop = False
        self.protocols = protocols

    def _handle_message(self, sender, message):
        for protocol in self.protocols:
            if message in protocol:  # Check for compatible protocol
                protocol.handle(sender, message)
                break
        else:
            # Handle no protocol message
            pass

    def run(self):
        while not self._stop:
            connection_address, message_bytes = self.messages_queue.get()
            try:
                message = Message.from_bytes(message_bytes)
                self._handle_message(connection_address, message)
            except Exception as EX:
                print("protocol handler error", EX)
