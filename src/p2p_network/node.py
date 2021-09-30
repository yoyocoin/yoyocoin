from os import path
from typing import List, Tuple, Callable, Dict, Iterable, Set
from queue import Queue
from random import choice
from time import time

from loguru import logger

from .exceptions import TimeoutException
from .server import Server
from .connection import Connection
from .protocol_handler import InternalProtocolHandler
from .heartbeat_service import HeartbeatService
from .protocols import BootstrapProtocol, VersionProtocol, PingProtocol
from .message import Message


Address = Tuple[str, int]
Callback = Callable[[Dict], None]
RELAY_HASH_STOP = 60
MAX_RELAY_HASH_SAVE = 10000


class Node:
    BOOTSTRAP_LIST_FILE_PATH = "config/bootstrap.list"

    MAX_OUTBOUND_CONNECTIONS = 8
    MAX_INBOUND_CONNECTIONS = 16

    BOOTSTRAP_NODES_ADDRESS = [("127.0.0.2", 6001)]
    MAX_PEER_LIST_REQUEST = 200
    BOOTSTRAP_REQUEST_TIMEOUT = 2  # Seconds

    NODE_VERSION = "0.0.1"
    LISTEN_PORT = 6001
    LISTEN_HOST = "0.0.0.0"

    CONNECT_TIMEOUT = 2  # Seconds
    REQUEST_TIMEOUT = 5  # Seconds
    MAX_BUFFER_SIZE = 1024 * 1024  # 1Mb

    HEARTBEAT_INTERVAL = 1

    def __init__(self):

        self.my_address = (self.__class__.LISTEN_HOST, self.__class__.LISTEN_PORT)
        self.peer_list: Set[Address] = {self.my_address}
        self._protocols = [BootstrapProtocol(self), VersionProtocol(self), PingProtocol(self)]

        self._active_connections: List = []
        self._initialized: bool = False
        self._connections: Dict[Address, Connection] = {}
        self._message_queue: Queue = Queue(maxsize=200)
        self._protocol_handler = InternalProtocolHandler(
            protocols=self._protocols,
            messages_queue=self._message_queue,
            external_message_callback=self.on_message
        )
        self._server = Server(
            message_queue=self._message_queue,
            new_connection_callback=self._register_connection,
            listen_host=self.LISTEN_HOST,
            listen_port=self.LISTEN_PORT,
            max_inbound_connections=self.MAX_INBOUND_CONNECTIONS,
            connections=self._connections
        )
        self._heartbeat_service = HeartbeatService(
            node_heartbeat_callback=self._heartbeat,
            interval=self.HEARTBEAT_INTERVAL
        )

    @property
    def connected_peers(self) -> List[Address]:
        """
        :return: list of connected peers address
        """
        return list(map(
            lambda item: item[0],
            filter(lambda item: item[-1].is_alive(), self._connections.items())
        ))

    def get_connection(self, address: Address) -> Connection:
        """
        Connection from address
        :param address: tuple with host and port e.g: ('158.46.75.1', 856)
        :return: connection object
        :raise: Key error if connection does not exist or disconnected
        """
        connection = self._connections[address]
        if not connection.is_alive():
            del self._connections[address]
            raise KeyError(address)
        return connection

    def on_message(self, message):
        """
        Called on every message received message
        :param message: Message object
        :return: None
        """
        pass

    def on_new_connection(self, connection: Connection):
        """
        Called when new connection created, inbound and outbound.
        :param connection: Connection object
        :return: None
        """
        pass

    def on_connection_closed(self, connection: Connection):
        """
        Called when connection has closed, inbound and outbound.
        :param connection: Connection object (closed socket)
        :return: None
        """
        pass

    def broadcast(self, message: Message, exclude: List[Address] = None) -> int:
        """
        Broadcast message to the network.
        :param message: Message object to broadcast
        :param exclude: address list to avoid sending that message
        :return: number of nodes the message sent to
        """
        if exclude is None:
            exclude = []
        if not message.is_valid():
            return 0
        sent_nodes_count = 0
        for address in self.connected_peers:
            if address in exclude:
                continue
            connection = self.get_connection(address)
            if message.hash in connection.internal_sent_messages_hash:
                if not time() - connection.internal_sent_messages_hash[message.hash]['sent_at'] > RELAY_HASH_STOP:
                    continue
                connection.internal_sent_messages_hash.pop(message.hash)
            try:
                connection.send(message.to_bytes())
            except ConnectionError:
                pass
            else:
                sent_nodes_count += 1
                connection.internal_sent_messages_hash[message.hash] = {"sent_at": time()}
                if len(connection.internal_sent_messages_hash) > MAX_RELAY_HASH_SAVE:
                    connection.internal_sent_messages_hash.popitem()
        return sent_nodes_count

    def start(self):
        """
        Start the node:
        connect to nodes and listen for network broadcast
        """
        self._connect_to_network()
        self._server.start()  # Start server thread
        self._protocol_handler.start()  # Start handling input messages
        self._heartbeat_service.start()

    def _load_bootstrap_nodes(self) -> List[Address]:
        """
        load bootstrap nodes from disk or hardcoded list:
        if bootstrap nodes file exists load it else return hardcoded list
        :return: bootstrap nodes address list
        """
        if path.exists(self.BOOTSTRAP_LIST_FILE_PATH):
            with open(self.BOOTSTRAP_LIST_FILE_PATH) as bootstrap_file:
                file_bootstrap_list = bootstrap_file.read()
            if file_bootstrap_list:
                return [
                    (node_address.split(":")[0], int(node_address.split(":")[1]))
                    for node_address in file_bootstrap_list.split("\n")
                ]
        return self.BOOTSTRAP_NODES_ADDRESS

    def _load_nodes_list_from_bootstrap_node(self, node_address: Address) -> Iterable[Address]:
        """
        Get nodes list from bootstrap node with request
        :param node_address: the bootstrap node address
        :return: list of currently active nodes
        """
        if node_address == (self.LISTEN_HOST, self.LISTEN_PORT):
            return []
        try:
            bootstrap_node = Connection.connect(node_address, recv_queue=self._message_queue)
        except TimeoutException:
            return []
        try:
            response = bootstrap_node.get(
                BootstrapProtocol.create_active_nodes_list_message(limit=self.MAX_PEER_LIST_REQUEST).to_bytes()
            )
        except TimeoutException:
            return []
        finally:
            bootstrap_node.close()
        message = Message.from_bytes(response)
        peer_list = message.dict_message.get("peers", [])
        peer_list = map(lambda x: tuple(x), peer_list)
        return peer_list

    def _get_peers_list(self, bootstrap_nodes_address: List[Address]) -> Set[Address]:
        nodes_list: Set[Address] = set()
        for bootstrap_node_address in bootstrap_nodes_address:
            network_nodes_address = self._load_nodes_list_from_bootstrap_node(bootstrap_node_address)
            nodes_list.update(network_nodes_address)
        return nodes_list

    def _connect_to_random_peers(self):
        """
        Connect to random peers
        """
        while len(self._connections) < self.MAX_OUTBOUND_CONNECTIONS:
            connected_peers = {*self.connected_peers, self.my_address}
            non_connected_peers = self.peer_list - connected_peers
            if not non_connected_peers:
                break
            random_node: Address = choice(tuple(non_connected_peers))
            try:
                connection = Connection.connect(random_node, self._message_queue)
            except TimeoutException:
                self.peer_list.remove(random_node)
            else:
                self._connections[connection.address] = connection

    def _connect_to_network(self):
        """
        Connect to <max outbound> nodes
        1. load bootstrap nodes
        2. get list of nodes
        3. connect to random <max outbound> nodes
        :return: None
        """
        bootstrap_nodes_address = self._load_bootstrap_nodes()
        logger.debug(f"loaded bootstrap nodes {bootstrap_nodes_address}")
        self.peer_list.update(self._get_peers_list(bootstrap_nodes_address))
        logger.debug(f"found {len(self.peer_list)} peers")

        if not self.peer_list:
            logger.info("Cant find any peers")
            return
        self._connect_to_random_peers()

    def _register_connection(self, connection: Connection) -> None:
        """
        Called by server when new connection created (socket connected)
        :param connection: socket connection object
        :return: None
        """
        logger.debug(f"New connection {connection.address}")
        self._connections[connection.address] = connection
        self.on_new_connection(connection)

    def _heartbeat(self):
        """
        Called from heartbeat service
        1. connect to other peers
        2. call protocols heartbeat
        3. check connections status
        :return: None
        """
        if int(time()) % 60 == 0:
            self._connect_to_random_peers()

        for protocol in self._protocols:
            if protocol.require_heartbeat and time() - protocol.last_heartbeat > protocol.heartbeat_interval:
                old_last_heartbeat = protocol.last_heartbeat
                logger.debug(f"Calling '{protocol.name}' protocol heartbeat")
                protocol.heartbeat()
                assert protocol.last_heartbeat != old_last_heartbeat, \
                    f'Protocol "{protocol.name}" must update last heartbeat every heartbeat'

        for address, connection in self._connections.copy().items():
            if not connection.is_alive():
                self.on_connection_closed(connection)
                del self._connections[address]


if __name__ == "__main__":
    n = Node()
    n.start()
