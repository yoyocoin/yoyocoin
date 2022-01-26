from typing import Tuple, Union
from threading import Thread
from socket import socket

from .processor import Processor
from .messages.message import Message

RECV_BATCH = 50000
MESSAGE_DELIMITER = b"%99"  # TODO: move to p2p network config


class Client(Thread):
    def __init__(
        self,
        addr: Tuple[str, int],
        initial_message: Message,
        processor: Processor,
        server_port: int,
    ) -> None:
        self.server_port = server_port
        self.addr = addr
        self.initial_msg = initial_message
        self.sock: Union[socket, None] = None
        self.__stop = False
        self.processor = processor

        super().__init__(name=f"client to {addr}", daemon=True)

    def connect(self):
        self.sock = socket()
        self.sock.connect(self.addr)

    def run(self) -> None:
        try:
            self.connect()
        except ConnectionError:
            print(f"ERROR when connecting to {self.addr}")
            return
        self.sock.send(self.initial_msg.to_bytes())  # type: ignore
        while True:
            msg_batch = self.sock.recv(RECV_BATCH)  # type: ignore
            if msg_batch == b"" or self.__stop:
                break
            messages = msg_batch.split(MESSAGE_DELIMITER)
            for msg in messages:
                if not msg:
                    continue
                self.processor.process(msg)
        print(f"closing connection with {self.addr}")

    def stop(self):
        self.__stop = True
        self.sock.settimeout(1)
