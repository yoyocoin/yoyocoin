from queue import Queue
from threading import Thread
from typing import Tuple
from socket import socket as Socket, AF_INET, SOCK_STREAM

from .config import Config

__all__ = ["Connection"]

Address = Tuple[str, int]


class Connection(Thread):
    def __init__(self, socket: Socket, address: Address, recv_queue: Queue):
        super().__init__(daemon=True, name=f"Connection {address}")
        self.socket = socket
        self.address = address
        self._recv_queue = recv_queue
        self._stop = False

    @classmethod
    def connect(cls, address: Address, recv_queue: Queue):
        new_socket = Socket(AF_INET, SOCK_STREAM)
        new_socket.settimeout(Config.socket_connect_timeout)
        new_socket.connect(address)
        return cls(new_socket, address, recv_queue)

    def send(self, message: bytes):
        self.socket.sendall(message)

    def get(self, request: bytes):
        self.socket.sendall(request)
        self.socket.settimeout(Config.socket_request_timeout)
        response = self.socket.recv(Config.socket_max_buffer_size)
        self.socket.settimeout(-1)
        return response

    def run(self):
        while not self._stop:
            data = self.socket.recv(Config.socket_max_buffer_size)
            self._recv_queue.put((self.address, data))
