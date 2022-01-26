from threading import Thread
from time import sleep
from pathlib import Path
from typing import List, Set, Tuple

from .server import Server, RequestHandler
from .processor import Processor
from .client import Client
from .messages import PeerInfo, BlocksRequest
from .messages.message import Message


HEARTBEAT_RATE = 1  # Seconds

ROOT = Path(__file__).parent.parent
BOOTSTRAP_LIST = str(ROOT / "config" / "bootstrap.list")


class Node(Thread):
    def __init__(self, blockchain, port: int = 9346) -> None:
        self.port = port
        self.blockchain = blockchain
        self.processor = Processor(blockchain, self)
        self.nodes: Set[Tuple[str, int]] = set()
        self.clients: List[Client] = []
        self.server = Server(
            ("0.0.0.0", self.port),
            RequestHandlerClass=RequestHandler,
            bind_and_activate=True,
            processor=self.processor,
        )

        self.__loaded_bootstrap_nodes = False
        self._to_relay: List[bytes] = []

        super().__init__(name="node", daemon=True)

    def broadcast(self, msg):
        """Broadcast message to peers"""
        self._to_relay.append(msg.to_bytes())

    def load_history(self, from_index: int):
        """Initial block download
        from_index: the index of the block to start downloading from
        """
        self._load_bootstarp_nodes()
        blocks_request_message = BlocksRequest(1, None)  # All the blocks after the genesis block
        self._connect(initial_message=blocks_request_message, max_connections=1)  # download_blocks

    def run(self):
        """Send updates to connected peers every heartbeat 1/s"""

        Thread(
            target=lambda: self.server.serve_forever(poll_interval=0.5), daemon=True
        ).start()  # Run the server

        self._load_bootstarp_nodes()

        heartbeat = 0
        while True:
            relay_messages = self._to_relay.copy()
            self._to_relay.clear()
            heartbeat += 1
            sleep(HEARTBEAT_RATE)
            if heartbeat % 10 == 0 and self._need_to_connect():
                self._connect(initial_message=PeerInfo(["127.0.0.1", self.port]))  # get updates
            if heartbeat % 20 == 0:
                relay_messages.append(PeerInfo(["127.0.0.1", self.port]).to_bytes())
            relay_messages.extend(self.processor.relay_messages)
            self.server.send(relay_messages)

    def _load_bootstarp_nodes(self):
        if self.__loaded_bootstrap_nodes:
            return
        bootstarp_nodes = [
            (line.split(":")[0], int(line.split(":")[1]))
            for line in open(BOOTSTRAP_LIST).read().split("\n")
        ]
        self.nodes |= set(bootstarp_nodes)
        self.__loaded_bootstrap_nodes = True
        print("loaded nodes", self.nodes)

    def _need_to_connect(self) -> bool:
        """Check if the node have less then 8 active connections and remove inactive clients"""
        c = 0
        for i in range(0, len(self.clients) - 1):
            client = self.clients[i]
            if client.is_alive():
                c += 1
            else:
                self.clients.pop(i)
        return c < 8

    def _connected_to(self, addr) -> bool:
        return any([client.addr == addr and client.is_alive() for client in self.clients])

    def _is_me(self, addr) -> bool:
        return addr[1] == self.port

    def _connect(self, initial_message: Message, max_connections: int = 8):
        """Connect to other peers on the network"""

        for _, node in zip(range(0, max_connections), self.nodes):
            if self._is_me(node) or self._connected_to(node):
                continue
            print("connecting to node", node)
            client = Client(
                addr=node,
                initial_message=initial_message,
                processor=self.processor,
                server_port=self.port,
            )
            client.start()
            self.clients.append(client)
