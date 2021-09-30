from typing import Callable, Dict, Any
from time import sleep
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM

from loguru import logger

from .connection import Connection


class Server(Thread):
    def __init__(
            self,
            message_queue,
            new_connection_callback: Callable,
            listen_host: str,
            listen_port: int,
            max_inbound_connections: int,
            connections: Dict[Any, Connection]
    ):
        super().__init__(daemon=True)
        self._stop = False
        self._new_connection_callback = new_connection_callback
        self._message_queue = message_queue
        self._connections = connections

        self.max_inbound_connections = max_inbound_connections
        self.host = listen_host
        self.port = listen_port
        self.listen_socket = socket(AF_INET, SOCK_STREAM)
        self.listen_socket.bind((self.host, self.port))
        self.listen_socket.listen(5)

    @property
    def _inbound_connected_peers_count(self):
        return len(list(filter(lambda c: c.is_inbound, self._connections.values())))

    def run(self):
        logger.info(f"Started listening for connections on {self.host}:{self.port}")
        while not self._stop:
            sleep(1)
            if self._inbound_connected_peers_count < self.max_inbound_connections:
                new_socket, address = self.listen_socket.accept()
                new_connection = Connection(new_socket, address, self._message_queue, inbound=True)
                self._new_connection_callback(new_connection)
