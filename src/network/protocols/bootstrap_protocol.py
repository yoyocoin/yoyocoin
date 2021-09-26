import random

from ..config import Config
from ..protocol import Protocol
from ..message import Message


class BootstrapProtocol(Protocol):
    name = "bootstrap"

    def __init__(self, node):
        super().__init__(node)
        self.active_nodes = set()
        self.active_nodes.add((Config.node_listen_host, Config.node_listen_port))

    def _add_active_node_address(self, address: tuple):
        self.active_nodes.add(address)
        if len(self.active_nodes) > 20000:
            self.active_nodes.pop()

    def _handle_active_nodes_request(self, sender, limit):
        connection = self.node.get_connection(sender)
        random_peers = random.sample(self.active_nodes, k=min(limit, len(self.active_nodes)))
        connection.send(Message({"peers": random_peers}).to_bytes())

    def handle(self, sender, message: Message):
        print("bootstrap protocol", sender, message.dict_message)
        action = message.dict_message.get("action", None)
        if action == "active_nodes_list":
            self._handle_active_nodes_request(sender, message.dict_message.get("limit"))
        elif action == "active_node_address":
            self._add_active_node_address(message.dict_message.get("address"))

    @classmethod
    def create_active_node_address_message(cls, address) -> Message:
        return Message({"protocol": cls.name, "action": "active_node_address", "address": address})

    @classmethod
    def create_active_nodes_list_message(cls, limit) -> Message:
        return Message({"protocol": cls.name, "action": "active_nodes_list", "limit": limit})
