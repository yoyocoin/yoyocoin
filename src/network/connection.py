from time import sleep, time
from queue import Queue
from threading import Thread
from typing import Tuple
from socket import socket as Socket, AF_INET, SOCK_STREAM

from .config import Config
from .exception import TimeoutException


__all__ = ["Connection"]

Address = Tuple[str, int]


class Connection(Thread):
    def __init__(self, socket: Socket, address: Address, recv_queue: Queue):
        super().__init__(daemon=True, name=f"Connection {address}")
        self.socket = socket
        self.address = address
        self._recv_queue = recv_queue
        self._stop = False

        self._waiting = False
        self._response = None

    @classmethod
    def connect(cls, address: Address, recv_queue: Queue):
        new_socket = Socket(AF_INET, SOCK_STREAM)
        new_socket.settimeout(Config.socket_connect_timeout)
        new_socket.connect(address)
        print("connected to", address)
        connection = cls(new_socket, address, recv_queue)
        new_socket.settimeout(None)
        connection.start()
        return connection

    def _wait(self, timeout: int):
        """
        Wait until self._waiting is False
        :param timeout: max seconds to wait
        :return:
        """
        wait_start = time()
        while self._waiting:
            if time() - wait_start > timeout:
                raise TimeoutException()
            sleep(0.1)

    def send(self, message: bytes):
        print("send", message, self.address)
        self.socket.send(message)

    def get(self, request: bytes):
        self.send(request)
        self._waiting = True
        self._wait(timeout=20)
        response = self._response
        self._response = None
        return response

    def run(self):
        while not self._stop:
            try:
                data = self.socket.recv(Config.socket_max_buffer_size)
            except (ConnectionError, OSError) as EX:
                print(EX)
                data = b''
            if not data:
                self.close()
                break
            print("recv", data, self.address, self._waiting)
            if self._waiting:
                self._response = data
                self._waiting = False
                continue
            self._recv_queue.put((self.address, data))

    def close(self):
        if self._stop:  # All ready stop
            return
        print("Closing connection", self.address)
        self._stop = True
        self.socket.close()
