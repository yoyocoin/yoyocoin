from os import path
from typing import List, Tuple, Callable, Dict, Iterable
from queue import Queue
from random import choice

from loguru import logger

from .exceptions import TimeoutException
from .config import Config
from .server import Server
from .connection import Connection
from .protocol_handler import InternalProtocolHandler
from .protocols import BootstrapProtocol
from .message import Message


Address = Tuple[str, int]
Callback = Callable[[Dict], None]


class Node:
    def __init__(self, on_message: Callback):
        self._on_network_broadcast_callback: Callback = on_message
        self._active_connections: List = []
        self._initialized: bool = False
        self._connections: Dict[Address, Connection] = {}
        self._message_queue: Queue = Queue(maxsize=200)
        self._protocol_handler = InternalProtocolHandler(
            protocols=[BootstrapProtocol(self)],
            messages_queue=self._message_queue,
            external_message_callback=on_message
        )
        self._server = Server(
            message_queue=self._message_queue,
            new_connection_callback=self._register_connection
        )

        self.peer_list: List[Address] = []

    @property
    def connected_peers(self) -> List[Address]:
        ded_connections_address = []
        for address, connection in self._connections.items():
            if not connection.is_alive():
                ded_connections_address.append(address)
        for address in ded_connections_address:
            del self._connections[address]
        return list(self._connections.keys())

    def get_connection(self, address: Address) -> Connection:
        connection = self._connections[address]
        if not connection.is_alive():
            raise KeyError(address)
        return connection

    def _load_bootstrap_nodes(self) -> List[Address]:
        """
        load bootstrap nodes from disk or hardcoded list:
        if bootstrap nodes file exists load it else return hardcoded list
        :return: bootstrap nodes address list
        """
        if path.exists(Config.bootstrap_list_file_path):
            with open(Config.bootstrap_list_file_path) as bootstrap_file:
                file_bootstrap_list = bootstrap_file.read()
            if file_bootstrap_list:
                return [
                    (node_address.split(":")[0], int(node_address.split(":")[1]))
                    for node_address in file_bootstrap_list.split("\n")
                ]
        return Config.bootstrap_nodes_address

    def _load_nodes_list_from_bootstrap_node(self, node_address: Address) -> Iterable[Address]:
        """
        Get nodes list from bootstrap node with http request
        :param node_address: the bootstrap node address
        :return: list of currently active nodes
        """
        if node_address == (Config.node_listen_host, Config.node_listen_port):
            return []
        try:
            bootstrap_node = Connection.connect(node_address, recv_queue=self._message_queue)
        except TimeoutException:
            return []
        try:
            response = bootstrap_node.get(
                BootstrapProtocol.create_active_nodes_list_message(limit=Config.bootstrap_list_request_max).to_bytes()
            )
        except TimeoutException:
            return []
        finally:
            bootstrap_node.close()
        message = Message.from_bytes(response)
        peer_list = message.dict_message.get("peers", [])
        peer_list = map(lambda x: tuple(x), peer_list)
        return peer_list

    def _get_peers_list(self, bootstrap_nodes_address: List[Address]) -> List[Address]:
        nodes_list: List[Address] = []
        for bootstrap_node_address in bootstrap_nodes_address:
            network_nodes_address = self._load_nodes_list_from_bootstrap_node(bootstrap_node_address)
            nodes_list.extend(network_nodes_address)
        return nodes_list

    def _connect_to_random_peers(self, peers_list: List[Address]) -> List[Address]:
        """
        Connect to random peers
        :param peers_list: list of peers address
        :return: updated list of active nodes
        """
        try_nodes: set = set()
        while len(self._connections) < Config.max_outbound_connections and len(try_nodes) < len(peers_list):
            random_node: Address = choice(peers_list)
            if random_node not in try_nodes:
                try:
                    connection = Connection.connect(random_node, self._message_queue)
                except TimeoutException:
                    peers_list.remove(random_node)
                else:
                    self._connections[connection.address] = connection
                try_nodes.add(random_node)
        return peers_list

    def _connect_to_network(self) -> List[Address]:
        """
        Connect to <max outbound> nodes
        1. load bootstrap nodes
        2. get list of nodes
        3. connect to random <max outbound> nodes
        :return: list of active connected nodes
        """
        bootstrap_nodes_address = self._load_bootstrap_nodes()
        logger.debug(f"loaded bootstrap nodes {bootstrap_nodes_address}")
        peers_list: List[Address] = self._get_peers_list(bootstrap_nodes_address)
        logger.debug(f"found {len(peers_list)} peers")

        if not peers_list:
            logger.info("Cant find any peers")
            return []
        peers_list = self._connect_to_random_peers(peers_list)
        return peers_list

    def _register_connection(self, connection: Connection) -> None:
        """
        Called by server when new connection created (socket connected)
        :param connection: socket connection object
        :return: None
        """
        logger.debug(f"New connection from {connection.address}")
        self._connections[connection.address] = connection

    def broadcast(self, data: bytes):
        """
        Broadcast the data to the network
        :param data:
        :return:
        """
        for connection in self._connections.values():
            connection.send(data)

    def start(self):
        """
        Start the node:
        connect to nodes and listen for network broadcast
        """
        self.peer_list = self._connect_to_network()
        self._server.start()  # Start server thread
        self._protocol_handler.start()  # Start handling input messages


if __name__ == "__main__":
    n = Node(on_message=lambda x: print("broadcast:", x))
    n.start()
