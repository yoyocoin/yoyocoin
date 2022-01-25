from typing import Tuple
from threading import Thread
from socket import socket

from .processor import Processor

RECV_BATCH = 50000


class Client(Thread):
    def __init__(self, addr: Tuple[str, int], processor: Processor, server_port: int) -> None:
        self.server_port = server_port
        self.addr = addr
        self.sock = None
        self.__stop = False
        self.processor = processor

        super().__init__(name=f"client to {addr}", daemon=True)
    
    def connect(self):
        self.sock = socket()
        self.sock.connect(self.addr)

    def run(self) -> None:
        self.connect()
        self.sock.send(b'{"msg":"peer-info","ttl":5,"addr":["127.0.0.1",' + str(self.server_port).encode() + b']}')
        while True:
            msg = self.sock.recv(RECV_BATCH)
            if msg == b'' or self.__stop:
                break
            messages = msg.split(b"}")
            for msg in messages:
                if not msg:
                    continue
                self.processor.process(msg + b"}")
    

    def stop(self):
        self.__stop = True
        self.sock.settimeout(1)
    