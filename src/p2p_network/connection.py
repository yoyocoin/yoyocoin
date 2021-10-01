from typing import Dict
from time import sleep, time
from queue import Queue
from threading import Thread
from typing import Tuple
from socket import socket as Socket, AF_INET, SOCK_STREAM

from loguru import logger

from .exceptions import ConnectionClosed
from .protocols import VersionProtocol


__all__ = ["Connection"]

Address = Tuple[str, int]
CONNECT_TIMEOUT = 2  # Seconds
REQUEST_TIMEOUT = 5  # Seconds
MAX_BUFFER_SIZE = 1024 * 1024  # 1Mb


class Connection(Thread):
    def __init__(self, socket: Socket, address: Address, recv_queue: Queue, inbound: bool = False):
        super().__init__(daemon=True, name=f"Connection {address}")
        self.socket = socket
        self.address = address
        self.version = None
        self.is_inbound = inbound
        self._recv_queue = recv_queue
        self._run = True

        self._waiting = False
        self._response: bytes = b''
        self.internal_sent_messages_hash: Dict = dict()

        self.socket.settimeout(None)
        self.start()
        self.send(VersionProtocol.create_version_message().to_bytes())

    def is_alive(self) -> bool:
        return super().is_alive() and self._run

    @classmethod
    def connect(cls, address: Address, recv_queue: Queue):
        new_socket = Socket(AF_INET, SOCK_STREAM)
        new_socket.settimeout(CONNECT_TIMEOUT)
        new_socket.connect(address)
        logger.debug(f"Connected to {address}")
        return cls(new_socket, address, recv_queue)

    def _wait(self, timeout: int):
        """ Wait until self._waiting is False
        :param timeout: max seconds to wait
        :return:
        """
        wait_start = time()
        while self._waiting:
            if time() - wait_start > timeout:
                raise TimeoutError()
            sleep(0.1)

    def send(self, message: bytes):
        if not self.is_alive():
            raise ConnectionClosed()
        self.socket.send(message)
        # logger.debug(f"sent {message.decode()}")

    def get(self, request: bytes) -> bytes:
        self.socket.settimeout(REQUEST_TIMEOUT)
        try:
            self.send(request)
        finally:
            self.socket.settimeout(None)
        self._waiting = True
        self._wait(timeout=REQUEST_TIMEOUT)
        response, self._response = self._response, b''
        return response

    def run(self):
        while self._run:
            try:
                data = self.socket.recv(MAX_BUFFER_SIZE)
                # logger.debug(f"received {data}")
            except (ConnectionError, OSError):
                data = b''
            if not data:
                self.close()
                break
            if self._waiting:
                self._response = data
                self._waiting = False
                continue
            self._recv_queue.put((self.address, data))

    def close(self):
        if not self._run:  # All ready stop
            return
        logger.debug(f"Closing connection {self.address}")
        self._run = False
        self.socket.close()
