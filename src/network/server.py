from time import sleep
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM

from loguru import logger

from .config import Config
from .connection import Connection


class Server(Thread):
    def __init__(self, node):
        super().__init__(daemon=True)
        self.node = node
        self._stop = False
        self._connected_peers = 0

        self.listen_socket = socket(AF_INET, SOCK_STREAM)
        self.listen_socket.bind((Config.node_listen_host, Config.node_listen_port))
        self.listen_socket.listen(5)

    def run(self):
        logger.info(f"Started listening for connections on {Config.node_listen_host}:{Config.node_listen_port}")
        while not self._stop:
            sleep(1)
            if self._connected_peers < Config.max_inbound_connections:
                new_socket, address = self.listen_socket.accept()
                new_connection = Connection(new_socket, address, self.node.message_queue)
                self.node.add_connection(new_connection)
