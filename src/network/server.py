from typing import Callable
from time import sleep
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM

from loguru import logger

from .config import Config
from .connection import Connection


class Server(Thread):
    def __init__(self, message_queue, new_connection_callback: Callable):
        super().__init__(daemon=True)
        self._stop = False
        self._connected_peers = 0
        self._new_connection_callback = new_connection_callback
        self._message_queue = message_queue

        self.listen_socket = socket(AF_INET, SOCK_STREAM)
        self.listen_socket.bind((Config.node_listen_host, Config.node_listen_port))
        self.listen_socket.listen(5)

    def run(self):
        logger.info(f"Started listening for connections on {Config.node_listen_host}:{Config.node_listen_port}")
        while not self._stop:
            sleep(1)
            if self._connected_peers < Config.max_inbound_connections:
                new_socket, address = self.listen_socket.accept()
                new_connection = Connection(new_socket, address, self._message_queue)
                self._new_connection_callback(new_connection)
